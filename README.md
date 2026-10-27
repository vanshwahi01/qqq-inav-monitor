# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 26, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $712.07 | $712.20 | +1.8 bp | $704.38 (2026-10-22) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.10% | $216.00 | +2.39% | +19.3 bp |
| AAPL | 8.08% | $343.91 | -1.10% | -8.9 bp |
| MSFT | 6.20% | $532.60 | +1.54% | +9.6 bp |
| MU | 4.36% | $903.70 | +2.98% | +13.0 bp |
| AMZN | 4.26% | $249.09 | +0.44% | +1.9 bp |
| AMD | 3.71% | $531.28 | +2.80% | +10.4 bp |
| TSLA | 3.11% | $391.62 | +5.21% | +16.2 bp |
| META | 3.04% | $630.56 | -1.88% | -5.7 bp |
| GOOGL | 2.99% | $316.80 | -1.06% | -3.2 bp |
| GOOG | 2.79% | $314.19 | -0.97% | -2.7 bp |

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
