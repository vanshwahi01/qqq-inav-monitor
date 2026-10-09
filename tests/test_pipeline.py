"""End-to-end valuation and report build with synthetic prices (no network)."""
import json
from datetime import date

import pandas as pd
import pytest

from inav.pipeline import _store, resolve_shares_outstanding, value_and_check
from inav.report import build_report


@pytest.fixture
def raw_prices():
    # holdings date is 2026-10-01; fund = 3,000 and ETF trades at 30 that day
    return pd.DataFrame(
        {"A": [10.0, 11.0, 11.0], "B": [20.0, 20.0, None], "ETF": [30.0, 31.03, 31.0]},
        index=[date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 5)],
    )


def test_daily_valuation(cfg, toy_holdings, raw_prices):
    results, flags = value_and_check(cfg, toy_holdings, raw_prices, info={}, method="daily")

    assert list(results["valuation_date"]) == ["2026-10-01", "2026-10-02", "2026-10-05"]
    assert results["shares_out_source"].iloc[0] == "implied"
    assert results["premium_bp"].iloc[0] == pytest.approx(0)  # anchor day, by construction
    # Oct 2: A +1 -> fund 3,100 -> iNAV 31.00; ETF at 31.03 -> +~9.7 bp
    assert results["inav"].iloc[1] == pytest.approx(31.0)
    assert results["premium_bp"].iloc[1] == pytest.approx((31.03 / 31 - 1) * 1e4)
    # Oct 5: B missing -> carried forward and flagged
    assert results["inav"].iloc[2] == pytest.approx(31.0)
    assert any(f.check == "missing_price" for f in flags)


def test_official_nav_compared_on_latest_date(cfg, toy_holdings, raw_prices):
    results, _ = value_and_check(cfg, toy_holdings, raw_prices, info={"nav": 31.0}, method="daily")
    assert results["official_nav"].iloc[:-1].isna().all()
    assert results["nav_error_bp"].iloc[-1] == pytest.approx(0)


def test_shares_out_prefers_yahoo_when_consistent(cfg):
    so, source, flags = resolve_shares_outstanding(cfg, implied=100.0, info={"shares_outstanding": 100.2})
    assert (so, source, flags) == (100.2, "yahoo", [])


def test_shares_out_rejects_inconsistent_yahoo(cfg):
    so, source, flags = resolve_shares_outstanding(cfg, implied=100.0, info={"shares_outstanding": 120})
    assert (so, source) == (100.0, "implied") and flags[0].severity == "warning"


def test_manual_override_wins(cfg):
    cfg["shares_outstanding"] = 99
    assert resolve_shares_outstanding(cfg, 100.0, {"shares_outstanding": 100})[:2] == (99.0, "manual")


def test_store_and_build_report(cfg, toy_holdings, raw_prices):
    results, flags = value_and_check(cfg, toy_holdings, raw_prices, info={}, method="daily")
    _store(cfg, toy_holdings, raw_prices, results, flags)
    _store(cfg, toy_holdings, raw_prices, results, flags)  # re-running must not duplicate rows

    html = build_report(cfg).read_text()
    data = json.loads(html.split("const DATA = ", 1)[1].split(";\n", 1)[0])  # must be strict JSON
    assert "ETF iNAV Monitor" in html
    assert data["latest"]["valuation_date"] == "2026-10-05"
    assert {f["check_name"] for f in data["flags"]} >= {"missing_price"}
    assert len(pd.read_csv(f"{cfg['data_dir']}/inav_results.csv")) == 3
