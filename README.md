# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 14, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $733.79 | $728.95 | -66.0 bp | $743.59 (2026-10-13) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.31% | $221.30 | -3.16% | -26.2 bp |
| AAPL | 7.51% | $342.96 | +0.50% | +3.7 bp |
| MSFT | 6.09% | $533.69 | -1.80% | -10.9 bp |
| MU | 4.48% | $914.13 | -4.10% | -18.4 bp |
| AMZN | 4.21% | $254.08 | -1.74% | -7.3 bp |
| AMD | 4.12% | $570.82 | -5.73% | -23.6 bp |
| META | 3.42% | $762.50 | +0.00% | +0.0 bp |
| GOOGL | 3.13% | $347.64 | -1.74% | -5.4 bp |
| TSLA | 2.97% | $367.16 | -2.15% | -6.4 bp |
| GOOG | 2.91% | $349.52 | +0.00% | +0.0 bp |

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
