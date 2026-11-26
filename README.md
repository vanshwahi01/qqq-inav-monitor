# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 25, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $634.05 | $633.93 | -1.8 bp | $637.95 (2026-11-24) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 9.09% | $355.58 | +0.43% | +3.9 bp |
| NVDA | 6.59% | $149.30 | -3.91% | -25.8 bp |
| MSFT | 6.49% | $489.93 | -1.25% | -8.1 bp |
| AMZN | 4.79% | $244.43 | -3.12% | -14.9 bp |
| TSLA | 3.55% | $380.14 | -1.18% | -4.2 bp |
| MU | 3.45% | $601.25 | -4.53% | -15.7 bp |
| AMD | 3.28% | $406.03 | -1.75% | -5.7 bp |
| WMT | 3.12% | $131.94 | -0.28% | -0.9 bp |
| META | 3.08% | $609.89 | +3.40% | +10.5 bp |
| GOOGL | 2.88% | $273.10 | -2.13% | -6.1 bp |

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
