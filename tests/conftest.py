import json
from pathlib import Path

import pandas as pd
import pytest

from inav.holdings import Holdings, parse_holdings

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def real_payload() -> dict:
    """A trimmed copy of the real Invesco QQQ feed (2026-10-06)."""
    return json.loads((FIXTURES / "qqq_holdings_sample.json").read_text())


@pytest.fixture
def real_holdings(real_payload) -> Holdings:
    return parse_holdings(real_payload)


@pytest.fixture
def toy_holdings() -> Holdings:
    """Two stocks + cash with round numbers, so expected values are easy to check by hand.

    At A=10, B=20: A is worth 1,000, B 1,000, cash 1,000 -> fund 3,000.
    """
    from datetime import date

    positions = pd.DataFrame([
        {"line_id": "COM:A", "ticker": "A", "name": "Stock A", "asset_class": "equity", "units": 100.0, "weight_pct": 100 / 3},
        {"line_id": "COM:B", "ticker": "B", "name": "Stock B", "asset_class": "equity", "units": 50.0, "weight_pct": 100 / 3},
        {"line_id": "CURR:USD", "ticker": "USD", "name": "Cash", "asset_class": "cash", "units": 1000.0, "weight_pct": 100 / 3},
        {"line_id": "IFUT:F", "ticker": "F", "name": "Future", "asset_class": "future", "units": 5.0, "weight_pct": 1.0},
        {"line_id": "SYN:F", "ticker": None, "name": "Contra", "asset_class": "synthetic", "units": -5.0, "weight_pct": -1.0},
    ])
    return Holdings(as_of=date(2026, 10, 1), positions=positions)


@pytest.fixture
def cfg(tmp_path) -> dict:
    return {
        "ticker": "ETF",
        "data_dir": str(tmp_path / "data"),
        "db_path": str(tmp_path / "data" / "inav.db"),
        "report_path": str(tmp_path / "docs" / "index.html"),
        "shares_outstanding": None,
        "thresholds": {
            "premium_warn_bp": 25,
            "nav_error_warn_bp": 10,
            "missing_weight_critical_pct": 0.5,
            "large_move_pct": 15,
            "holdings_max_age_days": 5,
            "weights_tolerance_pct": 0.5,
            "tna_tolerance_bp": 25,
            "shares_out_agreement_pct": 0.5,
        },
    }
