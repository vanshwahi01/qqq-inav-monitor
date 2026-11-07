# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 6, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $652.80 | $656.10 | +50.5 bp | $647.78 (2026-11-05) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.70% | $342.37 | -0.52% | -4.5 bp |
| NVDA | 7.58% | $186.64 | +2.78% | +21.0 bp |
| MSFT | 6.89% | $530.61 | -0.99% | -6.8 bp |
| AMZN | 4.86% | $259.30 | -0.35% | -1.7 bp |
| MU | 3.54% | $690.00 | +5.12% | +18.1 bp |
| AMD | 3.15% | $449.04 | +11.04% | +34.8 bp |
| TSLA | 3.13% | $358.22 | +4.23% | +13.2 bp |
| META | 3.11% | $605.08 | +0.00% | +0.0 bp |
| WMT | 2.97% | $125.52 | -1.72% | -5.1 bp |
| GOOGL | 2.87% | $284.78 | +0.78% | +2.2 bp |

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
