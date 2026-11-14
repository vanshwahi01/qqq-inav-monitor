# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 13, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $679.83 | $679.89 | +0.9 bp | $688.22 (2026-11-12) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.45% | $356.27 | +0.39% | +3.3 bp |
| NVDA | 6.53% | $162.85 | -2.01% | -13.1 bp |
| MSFT | 6.33% | $523.88 | +0.17% | +1.1 bp |
| AMZN | 4.70% | $266.66 | -0.29% | -1.4 bp |
| AMD | 4.30% | $534.06 | -8.75% | -37.6 bp |
| MU | 4.06% | $778.31 | -2.52% | -10.2 bp |
| TSLA | 3.40% | $390.22 | -1.82% | -6.2 bp |
| META | 3.02% | $641.69 | +2.90% | +8.8 bp |
| GOOGL | 2.86% | $295.77 | -0.98% | -2.8 bp |
| AVGO | 2.82% | $347.01 | -4.76% | -13.4 bp |

</details>
<!-- latest:end -->

Dashboard with a zoomable chart: download [`output/index.html`](output/index.html) and open it in a browser.

## How it works

1. Download QQQ's holdings from Invesco: the number of shares it owns of each stock, plus cash.
2. Get each stock's closing price from Yahoo Finance.
3. **iNAV** = (Σ shares × close + cash) ÷ QQQ shares outstanding.
4. **Premium / discount** = QQQ close vs iNAV, in basis points.
5. Run a few data checks (missing prices, possible stock splits, a valuation that doesn't reconcile with Invesco's weights), save everything to SQLite, and rebuild the dashboard and this page.

## Run it

```bash
pip install -r requirements.txt
python inav.py backfill --days 60   # build some history
python inav.py daily                # today's run
open output/index.html
```

## Notes

- End of day only. Real iNAVs are published every 15 seconds from live prices.
- There's no free source for shares outstanding (Yahoo's was 40% off), so it's backed out from the official NAV on the holdings date.
- The shaded history is valued with today's holdings, so it drifts the further back it goes.
