"""Build the outputs from the database.

- docs/index.html: interactive dashboard, a single static file (no server)
- docs/chart.png and a "Latest run" table in README.md, so the GitHub repo
  page itself shows the results without any hosting
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display needed (CI runner)
import matplotlib.pyplot as plt
import pandas as pd

from . import db

log = logging.getLogger(__name__)
TEMPLATE = Path(__file__).parent / "dashboard.html"
README_START, README_END = "<!-- latest:start -->", "<!-- latest:end -->"


def _clean(obj):
    """Recursively replace NaN with None so the output is valid JSON."""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


def _series(conn) -> pd.DataFrame:
    """One row per valuation date: prefer a daily run over backfill, and the newest holdings."""
    df = db.read_sql(conn, "SELECT * FROM inav_results")
    if df.empty:
        return df
    df["rank"] = (df["method"] != "daily").astype(int)
    df = df.sort_values(["valuation_date", "rank", "holdings_date"], ascending=[True, True, False])
    return df.drop_duplicates("valuation_date").drop(columns="rank").reset_index(drop=True)


def _top_holdings(conn, holdings_date: str, valuation_date: str, n: int = 10) -> list[dict]:
    h = db.read_sql(
        conn,
        "SELECT ticker, name, weight_pct FROM holdings WHERE holdings_date = ? AND asset_class = 'equity' "
        "ORDER BY weight_pct DESC LIMIT ?",
        (holdings_date, n),
    )
    px = db.read_sql(conn, "SELECT date, ticker, close FROM prices WHERE date <= ?", (valuation_date,))
    px = px.pivot(index="date", columns="ticker", values="close").sort_index().ffill()
    anchor = px[px.index <= holdings_date].iloc[-1]
    current = px.iloc[-1]
    h["price"] = h["ticker"].map(current)
    h["ret_pct"] = 100 * (h["ticker"].map(current) / h["ticker"].map(anchor) - 1)
    h["contrib_bp"] = h["weight_pct"] * h["ret_pct"]  # weight% x return% = bp of fund
    return h.round(4).to_dict(orient="records")


def build_report(cfg: dict) -> Path:
    out = Path(cfg["report_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    conn = db.connect(cfg["db_path"])
    series = _series(conn)

    if series.empty:
        payload = {"ticker": cfg["ticker"], "empty": True}
    else:
        last = series.iloc[-1]
        flags = db.read_sql(
            conn,
            "SELECT check_name, severity, detail FROM exceptions "
            "WHERE run_ts = (SELECT MAX(run_ts) FROM exceptions) "
            "ORDER BY CASE severity WHEN 'critical' THEN 0 WHEN 'warning' THEN 1 ELSE 2 END",
        )
        payload = {
            "ticker": cfg["ticker"],
            "empty": False,
            "thresholds": cfg["thresholds"],
            "series": series[["valuation_date", "method", "inav", "market_close", "premium_bp", "official_nav", "nav_error_bp"]]
            .round(6).to_dict(orient="list"),
            "latest": json.loads(last.to_json()),
            "last_run": db.read_sql(conn, "SELECT MAX(run_ts) AS t FROM inav_results")["t"].iloc[0],
            "flags": flags.to_dict(orient="records"),
            "holdings": _top_holdings(conn, last["holdings_date"], last["valuation_date"]),
        }
    conn.close()

    if not series.empty:
        build_chart(cfg, series, out.parent / "chart.png")
        if cfg.get("readme_path"):
            update_readme(cfg, payload, cfg["readme_path"])

    # Escape "</" so no text field can close the <script> tag early
    data = json.dumps(_clean(payload), default=str, allow_nan=False).replace("</", "<\\/")
    html = TEMPLATE.read_text().replace("__TICKER__", cfg["ticker"]).replace("__DATA__", data)
    out.write_text(html)
    log.info("Dashboard written to %s", out)
    return out


def build_chart(cfg: dict, series: pd.DataFrame, path: Path) -> None:
    """Two-panel PNG for the README: iNAV vs close, and premium/discount."""
    df = series.assign(date=pd.to_datetime(series["valuation_date"]))
    limit = cfg["thresholds"]["premium_warn_bp"]
    backfill = df[df["method"] == "backfill"]

    fig, (top, bottom) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    top.plot(df["date"], df["inav"], color="#2a78d6", lw=2, label="Computed iNAV")
    top.plot(df["date"], df["market_close"], color="#eb6834", lw=1.5, ls=":", label=f"{cfg['ticker']} close")
    top.set_ylabel("USD per share")
    top.legend(loc="upper left", frameon=False)
    top.set_title(f"{cfg['ticker']} iNAV vs market close", loc="left", fontsize=12)

    bottom.bar(df["date"], df["premium_bp"], color="#2a78d6", width=0.8)
    for y in (limit, -limit):
        bottom.axhline(y, color="#6f6e69", lw=1, ls="--")
    bottom.axhline(0, color="#c3c2b7", lw=1)
    bottom.set_ylabel("Premium (bp)")

    if not backfill.empty:
        for ax in (top, bottom):
            ax.axvspan(backfill["date"].min(), backfill["date"].max(), color="#898781", alpha=0.10, lw=0)
        top.text(backfill["date"].min(), top.get_ylim()[0], " constant-basket backfill (approximate)", va="bottom", fontsize=8, color="#6f6e69")

    for ax in (top, bottom):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e1e0d9", lw=0.8)
        ax.set_axisbelow(True)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    log.info("Chart written to %s", path)


def _fmt(v, spec: str, prefix: str = "", suffix: str = "") -> str:
    return "n/a" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{prefix}{v:{spec}}{suffix}"


def update_readme(cfg: dict, payload: dict, readme_path: str | Path) -> None:
    """Rewrite the block between the latest:start / latest:end markers in the README."""
    path = Path(readme_path)
    if not path.exists():
        return
    text = path.read_text()
    if README_START not in text or README_END not in text:
        return

    L = payload["latest"]
    s = payload["series"]
    navs = [(d, n, e) for d, n, e in zip(s["valuation_date"], s["official_nav"], s["nav_error_bp"])
            if n is not None and not (isinstance(n, float) and math.isnan(n))]
    if navs:
        d, n, e = navs[-1]
        nav_row = f"| Official NAV ({d}) | {_fmt(n, ',.2f', '$')} |"
        if L["shares_out_source"] == "nav":
            nav_row += "\n| iNAV vs official NAV | n/a (NAV used to set shares outstanding) |"
        else:
            nav_row += f"\n| iNAV vs official NAV | {_fmt(e, '+.1f', suffix=' bp')} |"
    else:
        nav_row = "| Official NAV | not available |"

    sev = {"critical": "🔴", "warning": "🟡", "info": "ℹ️"}
    flags = "\n".join(f"- {sev.get(f['severity'], '')} `{f['check_name']}`: {f['detail']}" for f in payload["flags"]) \
        or "- ✅ All checks passed"

    block = f"""{README_START}
_Updated automatically by the daily job. Last run: {payload["last_run"].replace("T", " ").replace("+00:00", " UTC")}_

![{cfg["ticker"]} iNAV vs market close](docs/chart.png)

| Valuation date {L["valuation_date"]} | |
|---|---|
| Computed iNAV | {_fmt(L["inav"], ',.2f', '$')} |
| {cfg["ticker"]} close | {_fmt(L["market_close"], ',.2f', '$')} |
| Premium / discount | {_fmt(L["premium_bp"], '+.1f', suffix=' bp')} |
{nav_row}
| Holdings as of | {L["holdings_date"]} |
| Shares outstanding | {_fmt(L["shares_out"], ',.0f')} (source: {L["shares_out_source"]}) |
| Price coverage | {_fmt(L["coverage_pct"], '.1f', suffix='%')} |

**Data-quality checks**

{flags}
{README_END}"""
    start, end = text.index(README_START), text.index(README_END) + len(README_END)
    path.write_text(text[:start] + block + text[end:])
    log.info("README updated")
