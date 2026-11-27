# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 25, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $633.91 | $633.93 | +0.3 bp | $633.91 (2026-11-25) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 9.18% | $355.58 | +0.00% | +0.0 bp |
| MSFT | 6.45% | $489.93 | +0.00% | +0.0 bp |
| NVDA | 6.37% | $149.30 | +0.00% | +0.0 bp |
| AMZN | 4.67% | $244.43 | +0.00% | +0.0 bp |
| TSLA | 3.53% | $380.14 | +0.00% | +0.0 bp |
| MU | 3.32% | $601.25 | +0.00% | +0.0 bp |
| AMD | 3.24% | $406.03 | +0.00% | +0.0 bp |
| META | 3.21% | $609.89 | +0.00% | +0.0 bp |
| WMT | 3.14% | $131.94 | +0.00% | +0.0 bp |
| GOOGL | 2.84% | $273.10 | +0.00% | +0.0 bp |

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
