# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 29, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $715.20 | $715.34 | +2.0 bp | $725.17 (2026-10-28) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.03% | $213.66 | -0.80% | -6.4 bp |
| AAPL | 7.76% | $348.91 | +1.48% | +11.5 bp |
| MSFT | 6.10% | $530.14 | -0.16% | -1.0 bp |
| MU | 4.74% | $934.27 | -4.98% | -23.6 bp |
| AMZN | 4.25% | $243.79 | -4.25% | -18.0 bp |
| AMD | 4.03% | $566.42 | -2.08% | -8.4 bp |
| TSLA | 3.28% | $403.30 | -0.23% | -0.8 bp |
| GOOGL | 2.95% | $283.82 | -12.64% | -37.3 bp |
| META | 2.82% | $624.52 | +1.96% | +5.5 bp |
| GOOG | 2.75% | $282.32 | -12.29% | -33.8 bp |

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
