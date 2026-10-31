# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 30, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $690.46 | $690.49 | +0.4 bp | $715.18 (2026-10-29) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.08% | $204.64 | -4.22% | -34.1 bp |
| AAPL | 7.99% | $344.63 | -1.23% | -9.8 bp |
| MSFT | 6.17% | $521.91 | -1.55% | -9.6 bp |
| MU | 4.57% | $884.74 | -5.30% | -24.2 bp |
| AMZN | 4.12% | $240.35 | -1.41% | -5.8 bp |
| AMD | 4.00% | $504.80 | -10.88% | -43.5 bp |
| TSLA | 3.32% | $399.81 | -0.87% | -2.9 bp |
| META | 2.91% | $614.99 | -1.53% | -4.4 bp |
| SPCX | 2.67% | $134.72 | -6.37% | -17.0 bp |
| GOOGL | 2.61% | $279.84 | -1.40% | -3.7 bp |

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
