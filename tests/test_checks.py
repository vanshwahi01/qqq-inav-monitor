from datetime import date

import pandas as pd

from inav import checks


def test_missing_price_severity(toy_holdings):
    flags = checks.check_missing_prices(toy_holdings, pd.Series({"A": 10.0}), critical_weight_pct=0.5)
    assert [(f.check, f.severity) for f in flags] == [("missing_price", "critical")]


def test_large_move_flags_possible_split(toy_holdings):
    anchor = pd.Series({"A": 10.0, "B": 20.0})
    after_split = pd.Series({"A": 5.0, "B": 20.2})  # A halves: looks like a 2-for-1 split
    flags = checks.check_large_moves(toy_holdings, anchor, after_split, threshold_pct=15)
    assert len(flags) == 1 and "A moved -50.0%" in flags[0].detail


def test_weights_sum_ok(toy_holdings):
    assert checks.check_weights_sum(toy_holdings, tolerance_pct=0.5) == []


def test_weights_sum_flags_gap(real_holdings):
    # the trimmed fixture only has ~22% of the fund
    assert checks.check_weights_sum(real_holdings, tolerance_pct=0.5)[0].check == "weights_sum"


def test_stale_holdings():
    assert checks.check_holdings_age(date(2026, 10, 1), date(2026, 10, 9), max_days=5)
    assert not checks.check_holdings_age(date(2026, 10, 6), date(2026, 10, 8), max_days=5)


def test_tna_reconciliation():
    assert not checks.check_tna_reconciles(100.0, 100.1, tolerance_bp=25)  # 10 bp
    assert checks.check_tna_reconciles(100.0, 101.0, tolerance_bp=25)  # ~99 bp


def test_threshold_ignores_missing_values():
    assert checks.check_threshold("nav_error", None, 10, "x") == []
    assert checks.check_threshold("premium", -30.0, 25, "Premium")[0].severity == "warning"
