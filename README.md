# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 28, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $725.16 | $725.61 | +6.2 bp | $721.23 (2026-10-27) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.17% | $215.38 | -1.17% | -9.6 bp |
| AAPL | 7.88% | $343.83 | -0.94% | -7.4 bp |
| MSFT | 6.14% | $531.01 | -0.06% | -0.4 bp |
| MU | 4.50% | $983.23 | +5.86% | +26.4 bp |
| AMZN | 4.25% | $254.60 | +0.59% | +2.5 bp |
| AMD | 3.93% | $578.44 | +3.24% | +12.7 bp |
| TSLA | 3.33% | $404.22 | -0.80% | -2.6 bp |
| GOOGL | 2.93% | $324.89 | +1.34% | +3.9 bp |
| META | 2.87% | $612.49 | -1.24% | -3.6 bp |
| SPCX | 2.74% | $145.23 | -2.25% | -6.2 bp |

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
