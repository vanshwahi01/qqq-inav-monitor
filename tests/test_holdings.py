from datetime import date

from inav.holdings import classify


def test_as_of_date(real_holdings):
    assert real_holdings.as_of == date(2026, 10, 6)


def test_asset_classes(real_holdings):
    counts = real_holdings.positions["asset_class"].value_counts().to_dict()
    assert counts == {"equity": 4, "cash": 3, "future": 1, "synthetic": 1}


def test_adr_counts_as_equity(real_holdings):
    assert "ASML" in set(real_holdings.equities["ticker"])


def test_cash_includes_collateral(real_holdings):
    assert real_holdings.cash == 1233394765.55 + 17148445.48 + 0


def test_line_ids_unique_even_when_cusips_collide(real_holdings):
    # the future and its synthetic offset share CUSIP "NQZ6"
    assert real_holdings.positions["line_id"].is_unique


def test_html_entities_unescaped(real_holdings):
    assert "CASH & EQUIVALENTS" in set(real_holdings.positions["name"])


def test_unknown_type_is_other():
    assert classify("SWAP") == "other"
    assert classify(None) == "other"
