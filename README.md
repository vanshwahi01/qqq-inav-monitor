# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 20, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $609.47 | $608.45 | -16.7 bp | $645.24 (2026-11-19) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.86% | $342.56 | -1.90% | -16.9 bp |
| MSFT | 6.44% | $484.52 | -2.77% | -17.8 bp |
| NVDA | 6.12% | $125.53 | -14.01% | -85.7 bp |
| AMZN | 4.83% | $246.82 | -4.10% | -19.8 bp |
| AMD | 3.83% | $424.39 | -13.25% | -50.8 bp |
| MU | 3.74% | $594.51 | -13.89% | -52.0 bp |
| TSLA | 3.42% | $345.82 | -7.64% | -26.1 bp |
| META | 3.08% | $560.84 | -5.93% | -18.3 bp |
| WMT | 2.94% | $127.95 | +1.52% | +4.5 bp |
| AVGO | 2.87% | $304.41 | -12.19% | -34.9 bp |

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
