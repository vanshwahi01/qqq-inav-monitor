# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 5, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $647.84 | $647.05 | -12.3 bp | $691.74 (2026-11-04) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.27% | $344.17 | -1.53% | -12.6 bp |
| NVDA | 7.82% | $181.60 | -9.26% | -72.4 bp |
| MSFT | 6.69% | $535.93 | -3.58% | -23.9 bp |
| AMZN | 4.65% | $260.21 | -2.19% | -10.2 bp |
| MU | 4.02% | $656.39 | -17.46% | -70.2 bp |
| AMD | 3.57% | $404.40 | -17.26% | -61.6 bp |
| TSLA | 3.28% | $343.69 | -10.77% | -35.3 bp |
| META | 3.04% | $605.08 | -3.96% | -12.0 bp |
| WMT | 2.81% | $127.72 | -1.12% | -3.2 bp |
| GOOGL | 2.75% | $282.57 | -2.20% | -6.0 bp |

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
