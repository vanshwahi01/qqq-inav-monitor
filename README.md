# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 9, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $751.06 | $751.27 | +2.8 bp | $757.96 (2026-10-07) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.33% | $229.28 | -0.52% | -4.3 bp |
| AAPL | 7.45% | $336.64 | -1.11% | -8.3 bp |
| MSFT | 5.82% | $535.07 | +2.38% | +13.9 bp |
| MU | 4.85% | $1,029.00 | -0.66% | -3.2 bp |
| AMD | 4.20% | $608.10 | -2.03% | -8.5 bp |
| AMZN | 4.11% | $262.43 | +3.29% | +13.6 bp |
| META | 3.22% | $718.67 | -0.31% | -1.0 bp |
| GOOGL | 3.07% | $351.66 | +0.97% | +3.0 bp |
| TSLA | 2.96% | $382.70 | +2.05% | +6.1 bp |
| GOOG | 2.86% | $347.86 | +0.87% | +2.5 bp |

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
