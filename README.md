# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 24, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $637.92 | $638.10 | +2.9 bp | $650.89 (2026-11-23) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.78% | $354.07 | +1.43% | +12.6 bp |
| NVDA | 6.86% | $155.38 | -5.86% | -40.2 bp |
| MSFT | 6.32% | $496.13 | +0.74% | +4.7 bp |
| AMZN | 4.75% | $252.29 | -1.21% | -5.8 bp |
| MU | 3.80% | $629.79 | -11.01% | -41.9 bp |
| AMD | 3.52% | $413.27 | -8.86% | -31.2 bp |
| TSLA | 3.49% | $384.68 | -0.20% | -0.7 bp |
| META | 3.06% | $589.82 | -1.30% | -4.0 bp |
| WMT | 3.00% | $132.31 | +2.11% | +6.3 bp |
| GOOGL | 2.85% | $279.05 | -1.08% | -3.1 bp |

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
