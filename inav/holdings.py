"""Fetch and parse ETF holdings from Invesco's public holdings feed.

The feed returns one row per position: stocks, cash, futures, and a "synthetic
cash" line that offsets the futures notional. Each row is classified into an
asset class so the valuation step knows how to treat it.
"""
from __future__ import annotations

import html
import logging
import time
from dataclasses import dataclass
from datetime import date

import pandas as pd
import requests

log = logging.getLogger(__name__)

INVESCO_URL = (
    "https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/"
    "{ticker}/holdings/fund?idType=ticker&productType=ETF"
)

# Invesco securityTypeCode -> how we value the position
EQUITY_CODES = {"COM", "ADR", "DRNY", "REIT"}  # priced at market close
CASH_CODES = {"CURR", "CURRCOL"}  # valued at face (units = USD amount)
FUTURE_CODES = {"IFUT"}  # notional is not fund value; excluded
SYNTHETIC_CODES = {"SYN"}  # offsets futures notional; excluded


def classify(security_type_code: str | None) -> str:
    code = (security_type_code or "").upper()
    if code in EQUITY_CODES:
        return "equity"
    if code in CASH_CODES:
        return "cash"
    if code in FUTURE_CODES:
        return "future"
    if code in SYNTHETIC_CODES:
        return "synthetic"
    return "other"


@dataclass
class Holdings:
    as_of: date
    positions: pd.DataFrame  # line_id, ticker, name, asset_class, units, weight_pct

    @property
    def equities(self) -> pd.DataFrame:
        return self.positions[self.positions["asset_class"] == "equity"]

    @property
    def cash(self) -> float:
        is_cash = self.positions["asset_class"] == "cash"
        return float(self.positions.loc[is_cash, "units"].sum())


def parse_holdings(payload: dict) -> Holdings:
    """Turn the raw Invesco JSON into a tidy DataFrame."""
    rows = []
    for h in payload["holdings"]:
        code = h.get("securityTypeCode")
        ticker = h.get("ticker")
        asset_class = classify(code)
        if asset_class == "other":
            log.warning("Unclassified position %s (type %s)", h.get("issuerName"), code)
        rows.append(
            {
                # futures and their offset share a CUSIP, so prefix with the type code
                "line_id": f"{code}:{ticker or h.get('cusip') or h.get('issuerName')}",
                "ticker": ticker,
                "name": html.unescape(h.get("issuerName") or ""),
                "asset_class": asset_class,
                "units": float(h.get("units") or 0.0),
                "weight_pct": float(h.get("percentageOfTotalNetAssets") or 0.0),
            }
        )

    as_of = date.fromisoformat(payload["effectiveBusinessDate"] or payload["effectiveDate"])
    positions = pd.DataFrame(rows)
    log.info("Parsed %d positions as of %s", len(positions), as_of)
    return Holdings(as_of=as_of, positions=positions)


def fetch_holdings_json(ticker: str, retries: int = 3, timeout: int = 30) -> dict:
    url = INVESCO_URL.format(ticker=ticker)
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": "inav-monitor"})
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            log.warning("Holdings fetch attempt %d/%d failed: %s", attempt, retries, exc)
            if attempt == retries:
                raise
            time.sleep(2 * attempt)
    raise RuntimeError("unreachable")
