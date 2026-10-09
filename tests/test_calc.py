import pandas as pd
import pytest

from inav.calc import compute_inav, fund_value, implied_shares_outstanding, implied_tna_from_weights, premium_bp
from inav.prices import to_yahoo

PRICES = pd.Series({"A": 10.0, "B": 20.0})


def test_fund_value_excludes_futures(toy_holdings):
    total, _ = fund_value(toy_holdings, PRICES)
    assert total == pytest.approx(3000)


def test_inav_per_share(toy_holdings):
    result = compute_inav(toy_holdings, PRICES, shares_out=100)
    assert result.inav == pytest.approx(30)
    assert result.coverage_pct == pytest.approx(100)
    assert result.unpriced == []


def test_missing_price_reduces_coverage(toy_holdings):
    result = compute_inav(toy_holdings, pd.Series({"A": 10.0}), shares_out=100)
    assert result.unpriced == ["B"]
    assert result.coverage_pct == pytest.approx(50)
    assert result.inav == pytest.approx(20)  # B's value is missing


def test_implied_shares_outstanding():
    assert implied_shares_outstanding(3000, 30) == pytest.approx(100)


def test_tna_from_weights_matches_valuation(toy_holdings):
    assert implied_tna_from_weights(toy_holdings, PRICES) == pytest.approx(3000)


def test_premium_sign():
    assert premium_bp(30.03, 30) == pytest.approx(10)
    assert premium_bp(29.97, 30) == pytest.approx(-10)


def test_real_feed_weights_reconcile(real_holdings):
    # Back out each stock's price from the issuer weight, then check every
    # position implies the same total net assets.
    tna = 1233394765.55 / (0.242304 / 100)  # from the cash line
    eq = real_holdings.equities
    prices = pd.Series((eq["weight_pct"] / 100 * tna / eq["units"]).values, index=eq["ticker"])
    assert implied_tna_from_weights(real_holdings, prices) == pytest.approx(tna, rel=1e-9)


def test_yahoo_ticker_mapping():
    assert to_yahoo("BRK.B") == "BRK-B"
    assert to_yahoo("NVDA") == "NVDA"
