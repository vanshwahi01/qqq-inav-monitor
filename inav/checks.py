"""Data-quality checks. Each returns zero or more exceptions for the daily report.

Severity: 'critical' means the iNAV should not be trusted, 'warning' means look
into it, 'info' is context.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from .holdings import Holdings


@dataclass
class Flag:
    check: str
    severity: str
    detail: str


def check_unclassified(holdings: Holdings) -> list[Flag]:
    other = holdings.positions[holdings.positions["asset_class"] == "other"]
    return [
        Flag("unclassified_position", "warning", f"{r.name} ({r.line_id}) not valued")
        for r in other.itertuples()
    ]


def check_weights_sum(holdings: Holdings, tolerance_pct: float) -> list[Flag]:
    valued = holdings.positions[holdings.positions["asset_class"].isin(["equity", "cash"])]
    total = valued["weight_pct"].sum()
    if abs(total - 100) > tolerance_pct:
        return [Flag("weights_sum", "warning", f"Equity + cash weights sum to {total:.2f}%")]
    return []


def check_missing_prices(holdings: Holdings, raw_closes: pd.Series, critical_weight_pct: float) -> list[Flag]:
    """Raw (un-forward-filled) closes on the valuation date."""
    out = []
    for r in holdings.equities.itertuples():
        if pd.isna(raw_closes.get(r.ticker, np.nan)):
            sev = "critical" if r.weight_pct >= critical_weight_pct else "warning"
            out.append(Flag("missing_price", sev, f"{r.ticker} ({r.weight_pct:.2f}% weight) has no close; last price carried forward"))
    return out


def check_large_moves(holdings: Holdings, anchor: pd.Series, current: pd.Series, threshold_pct: float) -> list[Flag]:
    """Big moves since the holdings date can mean a split or corporate action,
    which would make the holdings units wrong."""
    out = []
    for r in holdings.equities.itertuples():
        a, c = anchor.get(r.ticker), current.get(r.ticker)
        if pd.notna(a) and pd.notna(c) and a:
            move = 100 * (c / a - 1)
            if abs(move) >= threshold_pct:
                out.append(Flag("large_move", "warning", f"{r.ticker} moved {move:+.1f}% since holdings date; check for corporate actions"))
    return out


def check_holdings_age(holdings_date: date, valuation_date: date, max_days: int) -> list[Flag]:
    age = (valuation_date - holdings_date).days
    if age > max_days:
        return [Flag("stale_holdings", "warning", f"Holdings are {age} days older than valuation date")]
    return []


def check_tna_reconciles(our_tna: float, weights_tna: float, tolerance_bp: float) -> list[Flag]:
    diff_bp = (our_tna / weights_tna - 1) * 1e4
    if abs(diff_bp) > tolerance_bp:
        return [Flag("tna_reconciliation", "warning", f"Valued TNA differs from weight-implied TNA by {diff_bp:+.1f} bp")]
    return []


def check_threshold(name: str, value: float | None, limit: float, label: str) -> list[Flag]:
    if value is not None and abs(value) > limit:
        return [Flag(name, "warning", f"{label} of {value:+.1f} bp exceeds ±{limit:g} bp")]
    return []
