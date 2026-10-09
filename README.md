# QQQ iNAV Monitor

Rebuilds the **indicative net asset value (iNAV)** of the Invesco QQQ ETF from its published holdings, compares it with the market price, and runs data-quality checks on every step. A GitHub Actions job runs it each weekday and publishes a dashboard to GitHub Pages.

**Live dashboard:** `https://<your-username>.github.io/<repo-name>/`

<!-- Add a screenshot after the first run: docs/screenshot.png -->

## Why

An ETF trades all day, but its NAV is only struck once, after the close. The iNAV (also called IOPV) fills that gap: it values the fund's holdings at current prices so market makers and investors can see whether the ETF is trading at a premium or discount to what it holds. This project builds a simplified, end-of-day version of that calculation from public data.

## How it works

```
Invesco holdings feed ──┐
                        ├─► value basket ─► iNAV ─► checks ─► SQLite ─► static dashboard
Yahoo Finance closes ───┘
```

1. **Holdings.** Pulls QQQ's daily holdings from Invesco's public JSON feed (units of each stock, cash, index futures) and saves the raw file to `data/raw/` as an audit trail.
2. **Classification.** Each line is tagged by security type:
   - stocks and ADRs are priced at market;
   - cash and futures collateral are taken at face value;
   - futures notional and its "synthetic cash" offset cancel out, so both are excluded.
3. **Prices.** Pulls raw (not dividend-adjusted) daily closes for every holding and for QQQ itself.
4. **Shares outstanding.** Resolved in priority order, with the source recorded:
   1. a manual override in `config.yaml`;
   2. Yahoo's figure, only if it is within 0.5% of the implied value;
   3. implied from the holdings-date close.
5. **iNAV.** `(Σ units × close + cash) / shares outstanding`, for every trading day from the holdings date onward.
6. **Checks.** Flags anything that would make the number untrustworthy (see below).
7. **Storage and report.**
   - Everything goes into `data/inav.db` (SQLite), with a CSV copy so changes show in git diffs.
   - `docs/index.html` is rebuilt for GitHub Pages.

## Data-quality checks

| Check | What it catches |
|---|---|
| `missing_price` | A holding with no close today (critical if weight ≥ 0.5%) |
| `large_move` | A stock moving ≥ 15% since the holdings date, which may be a split or corporate action that invalidates the units |
| `weights_sum` | Equity + cash weights not summing to ~100% |
| `tna_reconciliation` | Our valuation disagreeing with the total assets implied by the issuer's own weights |
| `stale_holdings` | Holdings file more than 5 days old |
| `shares_out_source` | Yahoo's shares outstanding inconsistent with the holdings, so it is rejected |
| `premium` / `nav_error` | Premium/discount or gap to official NAV beyond the threshold |

Thresholds live in `config.yaml`.

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q                          # unit tests, no network needed
python -m inav backfill --days 60  # seed history, then build the dashboard
python -m inav daily               # today's run + dashboard
open docs/index.html
```

## Deploy (free)

1. Push this repo to GitHub.
2. Under **Settings → Pages**, choose "Deploy from a branch", branch `main`, folder `/docs`.
3. Under **Settings → Actions → General**, give workflows "Read and write permissions".
4. Under **Actions**, run "Daily iNAV update" once by hand. After that it runs every weekday at 22:30 UTC.

Run `python -m inav backfill --days 60` locally once and commit `data/` and `docs/` so the chart has history from day one.

## Project layout

```
inav/
  holdings.py   fetch + parse the issuer's holdings feed
  prices.py     Yahoo Finance closes and fund info
  calc.py       iNAV maths (pure functions, unit tested)
  checks.py     data-quality checks
  pipeline.py   orchestration: fetch -> value -> check -> store
  db.py         SQLite schema and upserts
  report.py     builds the static dashboard
tests/          pytest suite with a real holdings snapshot as fixture
config.yaml     ticker, paths, thresholds
.github/workflows/daily.yml
```

## Limitations and next steps

- **End-of-day only.** A production iNAV is published every 15 seconds from real-time prices. The valuation step is already separate, so an intraday price source could be plugged in.
- **Holdings lag.** The feed is one to two business days behind, so creations, redemptions and rebalances in between are missed.
- **Dividends and fees.** Accrued dividends and the management fee are not modelled. Ex-dividend dates show up as small jumps in the premium.
- **Single currency.** QQQ is all USD. Extending to a fund with foreign holdings means adding FX conversion per position.
- **Futures.** Futures P&L since the holdings date is ignored. It is about 0.14% of assets, so under 0.2 bp per 1% market move.
