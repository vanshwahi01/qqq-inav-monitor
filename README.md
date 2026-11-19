# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 18, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $659.71 | $659.51 | -3.1 bp | $656.93 (2026-11-17) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.77% | $352.45 | +0.15% | +1.4 bp |
| MSFT | 6.42% | $508.29 | +0.40% | +2.6 bp |
| NVDA | 6.40% | $150.96 | -2.89% | -18.5 bp |
| AMZN | 4.75% | $267.74 | +3.82% | +18.1 bp |
| AMD | 3.87% | $530.14 | +5.31% | +20.6 bp |
| MU | 3.79% | $705.27 | -1.00% | -3.8 bp |
| TSLA | 3.41% | $383.72 | +0.95% | +3.2 bp |
| META | 3.14% | $616.38 | -0.40% | -1.3 bp |
| WMT | 2.92% | $127.36 | -0.13% | -0.4 bp |
| SPCX | 2.87% | $143.50 | +1.27% | +3.6 bp |

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
