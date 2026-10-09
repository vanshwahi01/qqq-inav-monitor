from __future__ import annotations

import argparse
import html
import logging
import sqlite3
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

import report

TICKER = "QQQ"
OUTPUT = Path(__file__).parent / "output"
HOLDINGS_URL = (
    "https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/"
    "{ticker}/holdings/fund?idType=ticker&productType=ETF"
)

PREMIUM_ALERT_BP = 25      # premium/discount worth flagging
NAV_MATCH_BP = 25          # Yahoo's NAV must be this close to a recent ETF close to be dated
LARGE_MOVE_PCT = 15        # a move this big since the holdings date may be a stock split
MAX_HOLDINGS_AGE_DAYS = 5
TNA_TOLERANCE_BP = 25      # our valuation vs the total implied by Invesco's own weights

# Invesco security type -> how the position is valued. Index futures (IFUT) and
# their synthetic-cash offset (SYN) cancel each other out, so both are skipped.
EQUITY_TYPES = {"COM", "ADR", "DRNY", "REIT"}  # priced at the market close
CASH_TYPES = {"CURR", "CURRCOL"}  # face value (units are USD)

log = logging.getLogger("inav")


def fetch_holdings(ticker: str) -> tuple[date, pd.DataFrame]:
    """Today's holdings file from Invesco: one row per stock, plus cash lines."""
    url = HOLDINGS_URL.format(ticker=ticker)
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, timeout=30, headers={"User-Agent": "inav-monitor"})
            resp.raise_for_status()
            break
        except requests.RequestException as exc:
            if attempt == 3:
                raise
            log.warning("Holdings download failed (%s), retrying", exc)
            time.sleep(2 * attempt)
    payload = resp.json()

    rows = []
    for h in payload["holdings"]:
        code = (h.get("securityTypeCode") or "").upper()
        kind = "equity" if code in EQUITY_TYPES else "cash" if code in CASH_TYPES else None
        if kind is None:
            if code not in {"IFUT", "SYN"}:
                log.warning("Skipping unrecognised position %s (%s)", h.get("issuerName"), code)
            continue
        rows.append({
            "ticker": h.get("ticker") or code,
            "name": html.unescape(h.get("issuerName") or ""),  # feed has "CASH &amp; EQUIVALENTS"
            "kind": kind,
            "units": float(h.get("units") or 0),
            "weight_pct": float(h.get("percentageOfTotalNetAssets") or 0),
        })

    as_of = date.fromisoformat(payload["effectiveBusinessDate"] or payload["effectiveDate"])
    log.info("Holdings as of %s: %d positions", as_of, len(rows))
    return as_of, pd.DataFrame(rows)


def fetch_closes(tickers: list[str], start: date, end: date) -> pd.DataFrame:
    """Daily closes (dates x tickers). Raw, not dividend-adjusted: NAV is struck on actual closes.

    Yahoo sometimes drops a ticker from a bulk request, so missing ones are retried on their own.
    """
    yahoo = {t: t.replace(".", "-") for t in tickers}  # BRK.B -> BRK-B

    def download(symbols: list[str]) -> pd.DataFrame:
        data = yf.download(symbols, start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(),
                           auto_adjust=False, progress=False)
        closes = data["Close"]
        return closes.to_frame(symbols[0]) if isinstance(closes, pd.Series) else closes

    closes = download(list(yahoo.values()))
    for attempt in (1, 2):
        missing = [s for s in yahoo.values() if s not in closes or closes[s].isna().all()]
        if not missing:
            break
        log.warning("No prices for %s, retrying", ", ".join(missing))
        time.sleep(2 * attempt)
        closes = closes.drop(columns=missing, errors="ignore").join(download(missing), how="outer")

    closes.index = pd.to_datetime(closes.index).date
    closes = closes.rename(columns={y: t for t, y in yahoo.items()}).reindex(columns=tickers)
    return closes.dropna(how="all")  # drop non-trading days


def fetch_nav(ticker: str) -> float | None:
    """The issuer's official NAV as reported by Yahoo (not dated, see date_nav)."""
    try:
        return yf.Ticker(ticker).info.get("navPrice")
    except Exception as exc:  # yfinance raises many different errors
        log.warning("Could not get NAV from Yahoo: %s", exc)
        return None


def date_nav(nav: float | None, etf_closes: pd.Series) -> date | None:
    """Work out which day Yahoo's NAV belongs to.

    Yahoo doesn't date it, and different Yahoo servers have returned NAVs one or two
    days old. ETFs close within a few bp of NAV while daily moves are ~100 bp, so the
    NAV is matched to the recent close it is clearly nearest to.
    """
    if not nav:
        return None
    gaps = ((nav / etf_closes.dropna().iloc[-5:] - 1) * 1e4).abs().sort_values()
    if gaps.iloc[0] > NAV_MATCH_BP or (len(gaps) > 1 and gaps.iloc[1] < 3 * gaps.iloc[0]):
        log.warning("Yahoo NAV %.2f doesn't match a single recent close; not used", nav)
        return None
    return gaps.index[0]


def run(method: str, days: int | None = None) -> None:
    as_of, holdings = fetch_holdings(TICKER)
    equities = holdings[holdings["kind"] == "equity"].set_index("ticker")
    cash = holdings.loc[holdings["kind"] == "cash", "units"].sum()

    start = date.today() - timedelta(days=int((days or 5) * 1.6) + 10)
    closes = fetch_closes(list(equities.index) + [TICKER], min(start, as_of - timedelta(days=10)), date.today())
    filled = closes.ffill()  # a missing price carries the last one forward (flagged below)
    nav = fetch_nav(TICKER)

    # Value of the whole fund each day: sum of units x close, plus cash
    fund_value = (filled[equities.index] * equities["units"]).sum(axis=1) + cash

    # Shares outstanding has no free, reliable source (Yahoo's was 40% off), so back it out
    # on the holdings date: fund value / official NAV if we have that day's NAV, otherwise
    # assume the ETF closed at NAV that day.
    dates = list(filled.index)
    anchor = [d for d in dates if d <= as_of][-1]
    nav_date = date_nav(nav, filled[TICKER])
    if nav_date == anchor:
        shares, shares_source = fund_value[anchor] / nav, "nav"
    else:
        shares, shares_source = fund_value[anchor] / filled.loc[anchor, TICKER], "close"

    window = dates[-days:] if days else [d for d in dates if d >= anchor]
    results = pd.DataFrame({"inav": fund_value / shares, "market_close": filled[TICKER]}).loc[window]
    results["premium_bp"] = (results["market_close"] / results["inav"] - 1) * 1e4
    results["official_nav"] = [nav if d == nav_date else None for d in results.index]

    latest = window[-1]
    issues = check(as_of, holdings, equities, closes, filled, anchor, latest, fund_value, results)
    if nav_date in window and shares_source != "nav":  # an independent test of our number
        log.info("iNAV vs official NAV on %s: %+.1f bp", nav_date, (results.loc[nav_date, "inav"] / nav - 1) * 1e4)

    row = results.loc[latest]
    log.info("%s %s: iNAV %.2f, close %.2f, premium %+.1f bp, %d issue(s)",
             TICKER, latest, row["inav"], row["market_close"], row["premium_bp"], len(issues))
    for name, detail in issues:
        log.warning("%s: %s", name, detail)

    results = results.reset_index(names="valuation_date").assign(
        method=method, holdings_date=as_of.isoformat(), shares_out=shares, shares_source=shares_source)
    save(as_of, holdings, closes, results, issues)


def check(as_of, holdings, equities, closes, filled, anchor, latest, fund_value, results) -> list[tuple[str, str]]:
    """Data-quality checks. Anything returned means the latest number needs a look."""
    issues = []

    weights = holdings["weight_pct"].sum()
    if abs(weights - 100) > 0.5:
        issues.append(("weights_sum", f"stock + cash weights add up to {weights:.2f}%"))

    age = (latest - as_of).days
    if age > MAX_HOLDINGS_AGE_DAYS:
        issues.append(("stale_holdings", f"holdings are {age} days old"))

    for ticker, weight in equities["weight_pct"].items():
        if pd.isna(closes.loc[latest, ticker]):
            issues.append(("missing_price", f"{ticker} ({weight:.2f}% of fund) has no close; last price used"))

    moves = (filled.loc[latest, equities.index] / filled.loc[anchor, equities.index] - 1) * 100
    for ticker, move in moves[moves.abs() >= LARGE_MOVE_PCT].items():
        issues.append(("large_move", f"{ticker} moved {move:+.1f}% since the holdings date; possible split"))

    # Independent cross-check: each stock's value / its published weight should give the
    # same fund total. A bad or missing price shows up as a gap.
    big = equities[equities["weight_pct"] >= 0.1]
    implied_total = (big["units"] * filled.loc[anchor, big.index] / (big["weight_pct"] / 100)).median()
    gap_bp = (fund_value[anchor] / implied_total - 1) * 1e4
    if abs(gap_bp) > TNA_TOLERANCE_BP:
        issues.append(("valuation_gap", f"our fund value is {gap_bp:+.0f} bp off the total implied by Invesco's weights"))

    premium = results.loc[latest, "premium_bp"]
    if abs(premium) > PREMIUM_ALERT_BP:
        issues.append(("premium", f"premium/discount of {premium:+.1f} bp is beyond ±{PREMIUM_ALERT_BP} bp"))
    return issues


SCHEMA = """
CREATE TABLE IF NOT EXISTS holdings (
    holdings_date TEXT, ticker TEXT, name TEXT, kind TEXT, units REAL, weight_pct REAL
);
CREATE TABLE IF NOT EXISTS prices (
    date TEXT, ticker TEXT, close REAL, PRIMARY KEY (date, ticker)
);
CREATE TABLE IF NOT EXISTS results (
    valuation_date TEXT, method TEXT, holdings_date TEXT, inav REAL, market_close REAL,
    premium_bp REAL, official_nav REAL, shares_out REAL, shares_source TEXT, run_ts TEXT,
    PRIMARY KEY (valuation_date, method)
);
CREATE TABLE IF NOT EXISTS issues (run_ts TEXT, check_name TEXT, detail TEXT);
"""


def connect() -> sqlite3.Connection:
    OUTPUT.mkdir(exist_ok=True)
    conn = sqlite3.connect(OUTPUT / "inav.db")
    conn.executescript(SCHEMA)
    return conn


def upsert(conn: sqlite3.Connection, table: str, df: pd.DataFrame) -> None:
    """Insert rows, replacing any with the same key, so re-running a day is safe."""
    rows = df.astype(object).where(df.notna(), None).itertuples(index=False)
    marks = ", ".join("?" for _ in df.columns)
    conn.executemany(f"INSERT OR REPLACE INTO {table} ({', '.join(df.columns)}) VALUES ({marks})", rows)


def save(as_of, holdings, closes, results, issues) -> None:
    run_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute("DELETE FROM holdings WHERE holdings_date = ?", (as_of.isoformat(),))
        upsert(conn, "holdings", holdings.assign(holdings_date=as_of.isoformat()))

        prices = closes.stack().rename("close").reset_index()
        prices.columns = ["date", "ticker", "close"]
        upsert(conn, "prices", prices.assign(date=prices["date"].astype(str)))

        upsert(conn, "results", results.assign(valuation_date=results["valuation_date"].astype(str), run_ts=run_ts))
        upsert(conn, "issues", pd.DataFrame(issues, columns=["check_name", "detail"]).assign(run_ts=run_ts))

        # Plain-text copy so each day's change is visible in the git history
        pd.read_sql("SELECT * FROM results ORDER BY valuation_date, method", conn).to_csv(
            OUTPUT / "results.csv", index=False)
    conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{TICKER} iNAV calculator")
    parser.add_argument("command", choices=["daily", "backfill", "report"])
    parser.add_argument("--days", type=int, default=60, help="trading days to backfill")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)

    if args.command == "daily":
        run("daily")
    elif args.command == "backfill":
        run("backfill", args.days)
    with connect() as conn:
        report.build(conn, TICKER, PREMIUM_ALERT_BP, OUTPUT)
    conn.close()


if __name__ == "__main__":
    main()
