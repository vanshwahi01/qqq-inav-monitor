# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 12, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $745.92 | $746.04 | +1.6 bp | $751.23 (2026-10-09) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.25% | $226.32 | -1.29% | -10.7 bp |
| AAPL | 7.34% | $340.97 | +1.29% | +9.4 bp |
| MSFT | 5.93% | $541.15 | +1.14% | +6.7 bp |
| MU | 4.79% | $989.04 | -3.88% | -18.6 bp |
| AMZN | 4.23% | $259.53 | -1.11% | -4.7 bp |
| AMD | 4.09% | $594.24 | -2.28% | -9.3 bp |
| META | 3.19% | $742.96 | +3.38% | +10.8 bp |
| GOOGL | 3.08% | $352.72 | +0.30% | +0.9 bp |
| TSLA | 3.00% | $378.03 | -1.22% | -3.7 bp |
| SPCX | 2.87% | $163.42 | +0.52% | +1.5 bp |

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
