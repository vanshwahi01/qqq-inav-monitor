"""Command line entry point.

    python -m inav run              # today's iNAV, checks, store
    python -m inav backfill --days 60
    python -m inav report           # rebuild docs/index.html from the database
    python -m inav daily            # run + report (what the scheduled job calls)
"""
import argparse
import logging

from .pipeline import load_config, run_backfill, run_daily
from .report import build_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="inav", description="ETF iNAV calculator and monitor")
    parser.add_argument("command", choices=["run", "backfill", "report", "daily"])
    parser.add_argument("--days", type=int, default=60, help="trading days to backfill")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = load_config(args.config)

    if args.command in ("run", "daily"):
        run_daily(cfg)
    if args.command == "backfill":
        run_backfill(cfg, args.days)
    if args.command in ("report", "daily", "backfill"):
        build_report(cfg)


if __name__ == "__main__":
    main()
