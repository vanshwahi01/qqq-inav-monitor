# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 23, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $650.49 | $651.03 | +8.3 bp | $609.11 (2026-11-20) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 9.21% | $349.08 | +1.90% | +17.5 bp |
| MSFT | 6.64% | $492.50 | +1.65% | +10.9 bp |
| NVDA | 5.57% | $165.05 | +31.48% | +175.4 bp |
| AMZN | 4.90% | $255.39 | +3.47% | +17.0 bp |
| AMD | 3.52% | $453.46 | +6.85% | +24.1 bp |
| MU | 3.41% | $707.70 | +19.04% | +65.0 bp |
| TSLA | 3.35% | $385.46 | +11.46% | +38.3 bp |
| WMT | 3.16% | $129.58 | +1.27% | +4.0 bp |
| META | 3.07% | $597.60 | +6.55% | +20.1 bp |
| GOOGL | 2.87% | $282.10 | +6.34% | +18.2 bp |

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
