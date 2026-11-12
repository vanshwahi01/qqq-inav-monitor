# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 11, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $690.22 | $690.38 | +2.4 bp | $674.83 (2026-11-10) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.45% | $355.63 | +2.04% | +17.3 bp |
| NVDA | 6.76% | $173.73 | +2.87% | +19.4 bp |
| MSFT | 6.58% | $521.13 | -2.26% | -14.8 bp |
| AMZN | 4.86% | $266.17 | -1.74% | -8.4 bp |
| AMD | 3.86% | $552.90 | +7.32% | +28.2 bp |
| MU | 3.76% | $811.30 | +11.89% | +44.7 bp |
| TSLA | 3.32% | $390.84 | +2.91% | +9.7 bp |
| META | 3.17% | $628.77 | -1.97% | -6.2 bp |
| SPCX | 2.82% | $139.75 | -2.33% | -6.6 bp |
| GOOGL | 2.80% | $293.45 | +2.11% | +5.9 bp |

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
