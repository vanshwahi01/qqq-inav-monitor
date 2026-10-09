"""Build the outputs from the database: the HTML dashboard, a chart image, and the README section.

The dashboard is one static file and the README shows the same numbers, so nothing needs hosting.
"""
from __future__ import annotations

import json
import logging
import sqlite3
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no screen on the CI runner
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "dashboard.html"
README = ROOT / "README.md"
START, END = "<!-- latest:start -->", "<!-- latest:end -->"

log = logging.getLogger("inav")


def build(conn: sqlite3.Connection, ticker: str, alert_bp: float, out: Path) -> None:
    # One row per day; where a day has both, the daily run wins over the backfill estimate
    series = pd.read_sql("SELECT * FROM results ORDER BY valuation_date, method = 'daily'", conn)
    series = series.drop_duplicates("valuation_date", keep="last").reset_index(drop=True)
    if series.empty:
        log.warning("No results yet; run a backfill first")
        return

    latest = series.iloc[-1]
    navs = series.dropna(subset=["official_nav"])
    data = {
        "ticker": ticker,
        "alert_bp": alert_bp,
        "last_run": series["run_ts"].max().replace("T", " ").replace("+00:00", " UTC"),
        "latest": {k: latest[k] for k in ["valuation_date", "holdings_date", "inav", "market_close", "premium_bp"]},
        "nav": None if navs.empty else {"date": navs["valuation_date"].iloc[-1], "value": navs["official_nav"].iloc[-1]},
        "series": {
            "date": series["valuation_date"].tolist(),
            "premium_bp": series["premium_bp"].round(2).tolist(),
            "backfill": (series["method"] == "backfill").tolist(),
        },
        "holdings": top_holdings(conn, latest["holdings_date"], latest["valuation_date"]),
    }

    # Escape "</" so no text can close the <script> tag early
    payload = json.dumps(data, default=float).replace("</", "<\\/")
    page = TEMPLATE.read_text().replace("__TICKER__", ticker).replace("__DATA__", payload)
    (out / "index.html").write_text(page)
    chart(series, ticker, alert_bp, out / "chart.png")
    update_readme(data)
    log.info("Dashboard, chart and README updated")


def top_holdings(conn: sqlite3.Connection, holdings_date: str, valuation_date: str, n: int = 10) -> list[dict]:
    """Biggest positions, their move since the holdings date, and contribution to the fund."""
    top = pd.read_sql(
        "SELECT ticker, name, weight_pct FROM holdings WHERE holdings_date = ? AND kind = 'equity' "
        "ORDER BY weight_pct DESC LIMIT ?", conn, params=(holdings_date, n))
    prices = pd.read_sql("SELECT * FROM prices WHERE date <= ?", conn, params=(valuation_date,))
    prices = prices.pivot(index="date", columns="ticker", values="close").ffill()
    then, now = prices[prices.index <= holdings_date].iloc[-1], prices.iloc[-1]

    top["close"] = top["ticker"].map(now)
    top["move_pct"] = 100 * (top["close"] / top["ticker"].map(then) - 1)
    top["contrib_bp"] = top["weight_pct"] * top["move_pct"]  # weight% x return% = bp of the fund
    return top.round(2).to_dict(orient="records")


def chart(series: pd.DataFrame, ticker: str, alert_bp: float, path: Path) -> None:
    """Premium/discount bars, the same view as the dashboard."""
    df = series.assign(date=pd.to_datetime(series["valuation_date"]))
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.bar(df["date"], df["premium_bp"], width=0.8,
           color=["#2a78d6" if v >= 0 else "#eb6834" for v in df["premium_bp"]])
    for y in (alert_bp, -alert_bp):
        ax.axhline(y, color="#7a7973", lw=1, ls="--")
    ax.axhline(0, color="#c9c8c0", lw=1)

    backfill = df[series["method"] == "backfill"]
    if not backfill.empty:
        ax.axvspan(backfill["date"].min(), backfill["date"].max(), color="#898781", alpha=0.10, lw=0)

    ax.set_title(f"{ticker} premium / discount to iNAV (bp)", loc="left", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#ecebe6")
    ax.set_axisbelow(True)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def update_readme(data: dict) -> None:
    """Rewrite the block between the latest:start / latest:end markers."""
    text = README.read_text()
    if START not in text or END not in text:
        return
    L, nav = data["latest"], data["nav"]
    holdings = "\n".join(
        f"| {h['ticker']} | {h['weight_pct']:.2f}% | ${h['close']:,.2f} | {h['move_pct']:+.2f}% | {h['contrib_bp']:+.1f} bp |"
        for h in data["holdings"])

    block = f"""{START}
**As of {date.fromisoformat(L["valuation_date"]):%B %-d, %Y}**

| iNAV | {data["ticker"]} close | Premium / discount | Official NAV |
|---|---|---|---|
| ${L["inav"]:,.2f} | ${L["market_close"]:,.2f} | {L["premium_bp"]:+.1f} bp | {f"${nav['value']:,.2f} ({nav['date']})" if nav else "n/a"} |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
{holdings}

</details>
{END}"""
    start, end = text.index(START), text.index(END) + len(END)
    README.write_text(text[:start] + block + text[end:])
