# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 19, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $647.46 | $645.04 | -37.4 bp | $659.72 (2026-11-18) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.75% | $349.21 | -0.92% | -8.0 bp |
| MSFT | 6.42% | $498.30 | -1.97% | -12.6 bp |
| NVDA | 6.19% | $145.98 | -3.30% | -20.4 bp |
| AMZN | 4.91% | $257.37 | -3.87% | -19.0 bp |
| AMD | 4.06% | $489.19 | -7.72% | -31.4 bp |
| MU | 3.74% | $690.44 | -2.10% | -7.9 bp |
| TSLA | 3.43% | $374.41 | -2.43% | -8.3 bp |
| META | 3.12% | $616.38 | +0.00% | +0.0 bp |
| WMT | 2.91% | $126.04 | -1.04% | -3.0 bp |
| SPCX | 2.89% | $143.50 | +0.00% | +0.0 bp |

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
