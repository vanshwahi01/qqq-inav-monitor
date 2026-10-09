"""SQLite storage. One file, committed to the repo, so history survives between runs."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

SCHEMA = """
CREATE TABLE IF NOT EXISTS holdings (
    holdings_date TEXT NOT NULL,
    line_id       TEXT NOT NULL,
    ticker        TEXT,
    name          TEXT,
    asset_class   TEXT,
    units         REAL,
    weight_pct    REAL,
    PRIMARY KEY (holdings_date, line_id)
);

CREATE TABLE IF NOT EXISTS prices (
    date   TEXT NOT NULL,
    ticker TEXT NOT NULL,
    close  REAL,
    PRIMARY KEY (date, ticker)
);

CREATE TABLE IF NOT EXISTS inav_results (
    valuation_date    TEXT NOT NULL,
    holdings_date     TEXT NOT NULL,
    method            TEXT NOT NULL,   -- 'daily' or 'backfill'
    inav              REAL,
    market_close      REAL,
    premium_bp        REAL,
    official_nav      REAL,
    nav_error_bp      REAL,
    shares_out        REAL,
    shares_out_source TEXT,
    coverage_pct      REAL,
    run_ts            TEXT,
    PRIMARY KEY (valuation_date, holdings_date, method)
);

CREATE TABLE IF NOT EXISTS exceptions (
    run_ts         TEXT NOT NULL,
    valuation_date TEXT,
    check_name     TEXT NOT NULL,
    severity       TEXT,
    detail         TEXT NOT NULL,
    PRIMARY KEY (run_ts, check_name, detail)
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def upsert(conn: sqlite3.Connection, table: str, df: pd.DataFrame) -> None:
    """Insert rows, replacing any with the same primary key (re-runs are safe)."""
    if df.empty:
        return
    cols = ", ".join(df.columns)
    marks = ", ".join("?" for _ in df.columns)
    rows = [tuple(None if pd.isna(v) else v for v in row) for row in df.itertuples(index=False)]
    conn.executemany(f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({marks})", rows)
    conn.commit()


def save_prices(conn: sqlite3.Connection, closes: pd.DataFrame) -> None:
    long = closes.stack().rename("close").reset_index()
    long.columns = ["date", "ticker", "close"]
    long["date"] = long["date"].astype(str)
    upsert(conn, "prices", long)


def read_sql(conn: sqlite3.Connection, query: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(query, conn, params=params)
