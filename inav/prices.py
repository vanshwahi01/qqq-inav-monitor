"""Market data from Yahoo Finance (via yfinance).

Raw closes (not dividend-adjusted) are used on purpose: an ETF's NAV is
struck on the actual closing prices of its holdings.
"""
from __future__ import annotations

import logging
import time
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)


def to_yahoo(ticker: str) -> str:
    """Map an issuer ticker to Yahoo's format (e.g. BRK.B -> BRK-B)."""
    return ticker.replace(".", "-").replace("/", "-")


def _download(yahoo_tickers: list[str], start: date, end: date) -> pd.DataFrame:
    data = yf.download(
        yahoo_tickers,
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),  # yfinance's end is exclusive
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    closes = data["Close"]
    if isinstance(closes, pd.Series):
        closes = closes.to_frame(name=yahoo_tickers[0])
    closes.index = pd.to_datetime(closes.index).date
    return closes


def fetch_closes(tickers: list[str], start: date, end: date, retries: int = 2) -> pd.DataFrame:
    """Daily raw closes, indexed by date, one column per (original) ticker.

    Yahoo sometimes drops a ticker from a bulk request (seen on CI runners),
    so tickers with no data at all are retried on their own.
    """
    yahoo_map = {to_yahoo(t): t for t in tickers}
    closes = _download(list(yahoo_map), start, end)

    for attempt in range(1, retries + 1):
        missing = [y for y in yahoo_map if y not in closes or closes[y].isna().all()]
        if not missing:
            break
        log.warning("Retrying %d ticker(s) with no prices (attempt %d/%d): %s",
                    len(missing), attempt, retries, ", ".join(missing))
        time.sleep(2 * attempt)
        retry = _download(missing, start, end)
        closes = closes.drop(columns=[c for c in missing if c in closes]).join(retry, how="outer")

    closes = closes.rename(columns=yahoo_map)
    closes.index.name = "date"
    missing = sorted(set(tickers) - set(closes.columns[closes.notna().any()]))
    if missing:
        log.warning("No prices returned for: %s", ", ".join(missing))
    return closes.reindex(columns=tickers)


def fetch_fund_info(ticker: str) -> dict:
    """Issuer-reported NAV and shares outstanding, where Yahoo provides them.

    These fields are not guaranteed to exist, so callers must handle None.
    """
    try:
        info = yf.Ticker(to_yahoo(ticker)).info
    except Exception as exc:  # yfinance raises a variety of errors
        log.warning("Could not fetch fund info for %s: %s", ticker, exc)
        return {"nav": None, "shares_outstanding": None}
    return {
        "nav": info.get("navPrice"),
        "shares_outstanding": info.get("sharesOutstanding"),
    }
