"""Market data from Yahoo Finance (via yfinance).

Raw closes (not dividend-adjusted) are used on purpose: an ETF's NAV is
struck on the actual closing prices of its holdings.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

log = logging.getLogger(__name__)


def to_yahoo(ticker: str) -> str:
    """Map an issuer ticker to Yahoo's format (e.g. BRK.B -> BRK-B)."""
    return ticker.replace(".", "-").replace("/", "-")


def fetch_closes(tickers: list[str], start: date, end: date) -> pd.DataFrame:
    """Daily raw closes, indexed by date, one column per (original) ticker."""
    yahoo_map = {to_yahoo(t): t for t in tickers}
    data = yf.download(
        list(yahoo_map),
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),  # yfinance's end is exclusive
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    closes = data["Close"]
    if isinstance(closes, pd.Series):
        closes = closes.to_frame(name=list(yahoo_map)[0])
    closes = closes.rename(columns=yahoo_map)
    closes.index = pd.to_datetime(closes.index).date
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
