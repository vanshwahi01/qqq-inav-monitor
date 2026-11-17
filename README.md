# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 16, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $661.71 | $661.75 | +0.5 bp | $679.85 (2026-11-13) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.58% | $352.78 | -0.98% | -8.4 bp |
| NVDA | 6.47% | $156.14 | -4.12% | -26.7 bp |
| MSFT | 6.42% | $517.99 | -1.12% | -7.2 bp |
| AMZN | 4.74% | $257.75 | -3.34% | -15.8 bp |
| MU | 4.00% | $719.02 | -7.62% | -30.5 bp |
| AMD | 3.97% | $504.28 | -5.58% | -22.1 bp |
| TSLA | 3.38% | $379.74 | -2.69% | -9.1 bp |
| META | 3.15% | $626.41 | -2.38% | -7.5 bp |
| GOOGL | 2.86% | $283.72 | -4.07% | -11.7 bp |
| WMT | 2.84% | $128.41 | +0.25% | +0.7 bp |

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
