# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 17, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $656.94 | $656.95 | +0.1 bp | $661.69 (2026-11-16) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.73% | $351.91 | -0.25% | -2.1 bp |
| MSFT | 6.52% | $506.24 | -2.27% | -14.8 bp |
| NVDA | 6.38% | $155.46 | -0.44% | -2.8 bp |
| AMZN | 4.71% | $257.89 | +0.05% | +0.3 bp |
| AMD | 3.85% | $503.41 | -0.17% | -0.7 bp |
| MU | 3.80% | $712.42 | -0.92% | -3.5 bp |
| TSLA | 3.38% | $380.11 | +0.10% | +0.3 bp |
| META | 3.16% | $618.87 | -1.20% | -3.8 bp |
| WMT | 2.92% | $127.52 | -0.69% | -2.0 bp |
| GOOGL | 2.82% | $280.20 | -1.24% | -3.5 bp |

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
