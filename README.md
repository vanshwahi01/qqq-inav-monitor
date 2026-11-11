# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 10, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $675.99 | $674.76 | -18.1 bp | $678.86 (2026-11-09) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.45% | $348.51 | -0.62% | -5.3 bp |
| NVDA | 7.11% | $168.89 | -5.47% | -38.9 bp |
| MSFT | 6.69% | $533.16 | -2.20% | -14.7 bp |
| AMZN | 4.76% | $270.87 | +1.48% | +7.0 bp |
| AMD | 3.79% | $515.21 | +1.30% | +4.9 bp |
| MU | 3.78% | $725.11 | -1.10% | -4.1 bp |
| TSLA | 3.28% | $379.78 | +0.46% | +1.5 bp |
| META | 3.15% | $641.37 | +0.00% | +0.0 bp |
| GOOGL | 2.79% | $287.38 | -0.27% | -0.8 bp |
| WMT | 2.79% | $125.55 | -0.09% | -0.2 bp |

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
