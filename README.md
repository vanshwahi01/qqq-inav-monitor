# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 9, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $678.84 | $679.35 | +7.6 bp | $656.55 (2026-11-06) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.53% | $350.69 | +2.43% | +20.7 bp |
| NVDA | 7.68% | $178.67 | -4.27% | -32.8 bp |
| MSFT | 6.73% | $545.18 | +2.75% | +18.5 bp |
| AMZN | 4.78% | $266.93 | +2.94% | +14.1 bp |
| MU | 3.67% | $733.15 | +6.25% | +23.0 bp |
| AMD | 3.46% | $508.58 | +13.26% | +45.8 bp |
| TSLA | 3.21% | $378.05 | +5.54% | +17.8 bp |
| META | 3.10% | $641.37 | +5.12% | +15.9 bp |
| WMT | 2.88% | $125.66 | +0.11% | +0.3 bp |
| GOOGL | 2.85% | $288.15 | +1.18% | +3.4 bp |

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
