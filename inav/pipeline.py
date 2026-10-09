"""Orchestration: fetch -> value -> check -> store."""
from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yaml

from . import checks, db
from .calc import compute_inav, fund_value, implied_shares_outstanding, implied_tna_from_weights, premium_bp
from .holdings import Holdings, fetch_holdings_json, parse_holdings
from .prices import fetch_closes, fetch_fund_info

log = logging.getLogger(__name__)


def load_config(path: str | Path = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def resolve_shares_outstanding(cfg: dict, implied: float, info: dict) -> tuple[float, str, list[checks.Flag]]:
    """Pick a shares-outstanding figure and record where it came from.

    Priority: manual override > Yahoo (only if it agrees with our implied
    figure) > implied from the anchor-day close.
    """
    if cfg.get("shares_outstanding"):
        return float(cfg["shares_outstanding"]), "manual", []

    flags = []
    yahoo = info.get("shares_outstanding")
    if yahoo:
        diff_pct = abs(yahoo / implied - 1) * 100
        if diff_pct <= cfg["thresholds"]["shares_out_agreement_pct"]:
            return float(yahoo), "yahoo", []
        flags.append(checks.Flag(
            "shares_out_source", "warning",
            f"Yahoo shares outstanding ({yahoo:,.0f}) is {diff_pct:.2f}% away from implied ({implied:,.0f}); using implied",
        ))
    return implied, "implied", flags


def value_and_check(
    cfg: dict, holdings: Holdings, raw: pd.DataFrame, info: dict, method: str, n_days: int | None = None
) -> tuple[pd.DataFrame, list[checks.Flag]]:
    """Compute iNAV for each date and run checks on the latest one.

    raw: daily closes (dates x tickers), not forward-filled.
    n_days: for backfill, value the last n trading days; otherwise value every
            date from the holdings date onward.
    """
    etf, th = cfg["ticker"], cfg["thresholds"]
    filled = raw.ffill()  # carry last price forward for gaps (flagged below)
    dates = list(filled.index)

    on_or_before = [d for d in dates if d <= holdings.as_of]
    if not on_or_before:
        raise ValueError(f"No prices on or before holdings date {holdings.as_of}")
    anchor_date = on_or_before[-1]
    anchor = filled.loc[anchor_date]

    # Anchor: value the fund on the holdings date to pin down shares outstanding
    fund_mv, _ = fund_value(holdings, anchor)
    implied = implied_shares_outstanding(fund_mv, anchor[etf])
    shares_out, so_source, flags = resolve_shares_outstanding(cfg, implied, info)

    window = dates[-n_days:] if n_days else [d for d in dates if d >= anchor_date]
    rows = []
    for d in window:
        r = compute_inav(holdings, filled.loc[d], shares_out)
        market = float(filled.loc[d, etf])
        rows.append({
            "valuation_date": d.isoformat(),
            "holdings_date": holdings.as_of.isoformat(),
            "method": method,
            "inav": r.inav,
            "market_close": market,
            "premium_bp": premium_bp(market, r.inav),
            "official_nav": None,
            "nav_error_bp": None,
            "shares_out": shares_out,
            "shares_out_source": so_source,
            "coverage_pct": r.coverage_pct,
        })
    results = pd.DataFrame(rows)

    # Yahoo's NAV is "latest", so it's only compared on the most recent date
    latest = window[-1]
    if method == "daily" and info.get("nav"):
        nav = float(info["nav"])
        results.loc[results.index[-1], "official_nav"] = nav
        results.loc[results.index[-1], "nav_error_bp"] = premium_bp(results["inav"].iloc[-1], nav)

    last = results.iloc[-1]
    flags += checks.check_unclassified(holdings)
    flags += checks.check_weights_sum(holdings, th["weights_tolerance_pct"])
    flags += checks.check_missing_prices(holdings, raw.loc[latest], th["missing_weight_critical_pct"])
    flags += checks.check_large_moves(holdings, anchor, filled.loc[latest], th["large_move_pct"])
    flags += checks.check_holdings_age(holdings.as_of, latest, th["holdings_max_age_days"])
    flags += checks.check_tna_reconciles(fund_mv, implied_tna_from_weights(holdings, anchor), th["tna_tolerance_bp"])
    flags += checks.check_threshold("premium", last["premium_bp"], th["premium_warn_bp"], "Premium/discount")
    nav_err = last["nav_error_bp"]
    flags += checks.check_threshold("nav_error", None if pd.isna(nav_err) else nav_err, th["nav_error_warn_bp"], "iNAV vs official NAV")
    if so_source == "implied" and latest == anchor_date:
        flags.append(checks.Flag("anchor_day", "info", "Valuation date equals holdings date, so premium is ~0 by construction"))

    log.info("%s %s: iNAV %.4f, close %.2f, premium %+.1f bp, %d flags",
             etf, latest, last["inav"], last["market_close"], last["premium_bp"], len(flags))
    return results, flags


def _store(cfg: dict, holdings: Holdings, raw: pd.DataFrame, results: pd.DataFrame, flags: list[checks.Flag]) -> None:
    run_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn = db.connect(cfg["db_path"])
    h = holdings.positions.copy()
    h.insert(0, "holdings_date", holdings.as_of.isoformat())
    db.upsert(conn, "holdings", h)
    db.save_prices(conn, raw)
    db.upsert(conn, "inav_results", results.assign(run_ts=run_ts))
    db.upsert(conn, "exceptions", pd.DataFrame(
        [{"run_ts": run_ts, "valuation_date": results["valuation_date"].iloc[-1],
          "check_name": f.check, "severity": f.severity, "detail": f.detail} for f in flags],
        columns=["run_ts", "valuation_date", "check_name", "severity", "detail"],
    ))
    # Plain-text copy of results so changes are visible in git diffs
    db.read_sql(conn, "SELECT * FROM inav_results ORDER BY valuation_date, method").to_csv(
        Path(cfg["data_dir"]) / "inav_results.csv", index=False)
    conn.close()


def _fetch(cfg: dict, start: date) -> tuple[Holdings, pd.DataFrame]:
    payload = fetch_holdings_json(cfg["ticker"])
    holdings = parse_holdings(payload)

    # Keep the raw file: an audit trail of exactly what the issuer published
    raw_dir = Path(cfg["data_dir"]) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{cfg['ticker']}_{holdings.as_of}.json").write_text(json.dumps(payload))

    tickers = sorted(holdings.equities["ticker"].dropna().unique()) + [cfg["ticker"]]
    raw = fetch_closes(tickers, min(start, holdings.as_of - timedelta(days=10)), date.today())
    raw = raw.dropna(how="all")  # drop non-trading days
    return holdings, raw


def run_daily(cfg: dict) -> None:
    holdings, raw = _fetch(cfg, start=date.today() - timedelta(days=10))
    info = fetch_fund_info(cfg["ticker"])
    results, flags = value_and_check(cfg, holdings, raw, info, method="daily")
    _store(cfg, holdings, raw, results, flags)


def run_backfill(cfg: dict, days: int) -> None:
    """Value the last `days` trading days with today's holdings (constant basket).

    An approximation, since real holdings change, but it gives the chart
    history on day one. Daily runs replace it going forward.
    """
    holdings, raw = _fetch(cfg, start=date.today() - timedelta(days=int(days * 1.6) + 10))
    info = fetch_fund_info(cfg["ticker"])
    results, flags = value_and_check(cfg, holdings, raw, info, method="backfill", n_days=days)
    _store(cfg, holdings, raw, results, flags)
