"""iNAV maths. Pure functions only (no I/O), so everything here is unit-tested.

    iNAV per share = (sum(units_i * price_i) + cash) / shares outstanding

Futures notional and its synthetic-cash offset cancel out, so both are left out.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .holdings import Holdings


@dataclass
class InavResult:
    inav: float
    equity_value: float
    cash: float
    coverage_pct: float  # % of equity weight that had a price
    unpriced: list[str]


def equity_values(holdings: Holdings, closes: pd.Series) -> pd.DataFrame:
    """Per-position market value. Positions without a price get NaN value."""
    eq = holdings.equities[["ticker", "units", "weight_pct"]].copy()
    eq["price"] = eq["ticker"].map(closes)
    eq["value"] = eq["units"] * eq["price"]
    return eq


def fund_value(holdings: Holdings, closes: pd.Series) -> tuple[float, pd.DataFrame]:
    eq = equity_values(holdings, closes)
    return float(eq["value"].sum()) + holdings.cash, eq


def implied_tna_from_weights(holdings: Holdings, closes: pd.Series, min_weight: float = 0.1) -> float:
    """Total net assets implied by the issuer's own weights: value_i / weight_i.

    Taking the median over positions gives an independent cross-check of our
    valuation that is robust to a few bad prices.
    """
    eq = equity_values(holdings, closes)
    eq = eq[(eq["weight_pct"] >= min_weight) & eq["value"].notna()]
    return float((eq["value"] / (eq["weight_pct"] / 100)).median())


def implied_shares_outstanding(fund_mv: float, etf_close: float) -> float:
    """Shares outstanding if the ETF traded exactly at NAV on the anchor date."""
    return fund_mv / etf_close


def compute_inav(holdings: Holdings, closes: pd.Series, shares_out: float) -> InavResult:
    total, eq = fund_value(holdings, closes)
    priced = eq["value"].notna()
    total_weight = eq["weight_pct"].sum()
    coverage = 100 * eq.loc[priced, "weight_pct"].sum() / total_weight if total_weight else 0.0
    return InavResult(
        inav=total / shares_out,
        equity_value=float(eq["value"].sum()),
        cash=holdings.cash,
        coverage_pct=float(coverage),
        unpriced=eq.loc[~priced, "ticker"].tolist(),
    )


def premium_bp(price: float, nav: float) -> float:
    """Premium (+) or discount (-) of price to NAV, in basis points."""
    return (price / nav - 1) * 1e4
