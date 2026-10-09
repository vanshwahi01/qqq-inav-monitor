"""Build a static HTML dashboard (docs/index.html) from the database.

Static on purpose: GitHub Pages can host it for free and it needs no server.
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path

import pandas as pd

from . import db

log = logging.getLogger(__name__)
TEMPLATE = Path(__file__).parent / "dashboard.html"


def _clean(obj):
    """Recursively replace NaN with None so the output is valid JSON."""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


def _series(conn) -> pd.DataFrame:
    """One row per valuation date: prefer a daily run over backfill, and the newest holdings."""
    df = db.read_sql(conn, "SELECT * FROM inav_results")
    if df.empty:
        return df
    df["rank"] = (df["method"] != "daily").astype(int)
    df = df.sort_values(["valuation_date", "rank", "holdings_date"], ascending=[True, True, False])
    return df.drop_duplicates("valuation_date").drop(columns="rank").reset_index(drop=True)


def _top_holdings(conn, holdings_date: str, valuation_date: str, n: int = 10) -> list[dict]:
    h = db.read_sql(
        conn,
        "SELECT ticker, name, weight_pct FROM holdings WHERE holdings_date = ? AND asset_class = 'equity' "
        "ORDER BY weight_pct DESC LIMIT ?",
        (holdings_date, n),
    )
    px = db.read_sql(conn, "SELECT date, ticker, close FROM prices WHERE date <= ?", (valuation_date,))
    px = px.pivot(index="date", columns="ticker", values="close").sort_index().ffill()
    anchor = px[px.index <= holdings_date].iloc[-1]
    current = px.iloc[-1]
    h["price"] = h["ticker"].map(current)
    h["ret_pct"] = 100 * (h["ticker"].map(current) / h["ticker"].map(anchor) - 1)
    h["contrib_bp"] = h["weight_pct"] * h["ret_pct"]  # weight% x return% = bp of fund
    return h.round(4).to_dict(orient="records")


def build_report(cfg: dict) -> Path:
    out = Path(cfg["report_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    conn = db.connect(cfg["db_path"])
    series = _series(conn)

    if series.empty:
        payload = {"ticker": cfg["ticker"], "empty": True}
    else:
        last = series.iloc[-1]
        flags = db.read_sql(
            conn,
            "SELECT check_name, severity, detail FROM exceptions "
            "WHERE run_ts = (SELECT MAX(run_ts) FROM exceptions) "
            "ORDER BY CASE severity WHEN 'critical' THEN 0 WHEN 'warning' THEN 1 ELSE 2 END",
        )
        payload = {
            "ticker": cfg["ticker"],
            "empty": False,
            "thresholds": cfg["thresholds"],
            "series": series[["valuation_date", "method", "inav", "market_close", "premium_bp"]].round(6).to_dict(orient="list"),
            "latest": json.loads(last.to_json()),
            "last_run": db.read_sql(conn, "SELECT MAX(run_ts) AS t FROM inav_results")["t"].iloc[0],
            "flags": flags.to_dict(orient="records"),
            "holdings": _top_holdings(conn, last["holdings_date"], last["valuation_date"]),
        }
    conn.close()

    # Escape "</" so no text field can close the <script> tag early
    data = json.dumps(_clean(payload), default=str, allow_nan=False).replace("</", "<\\/")
    html = TEMPLATE.read_text().replace("__TICKER__", cfg["ticker"]).replace("__DATA__", data)
    out.write_text(html)
    log.info("Dashboard written to %s", out)
    return out
