# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 4, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $691.74 | $691.95 | +3.0 bp | $685.50 (2026-11-03) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.15% | $200.13 | -3.17% | -25.9 bp |
| AAPL | 7.92% | $349.51 | +5.31% | +42.0 bp |
| MSFT | 6.33% | $555.80 | +6.68% | +42.3 bp |
| AMZN | 4.42% | $266.03 | +6.12% | +27.1 bp |
| MU | 4.36% | $795.23 | -7.00% | -30.5 bp |
| AMD | 3.57% | $488.78 | +1.01% | +3.6 bp |
| TSLA | 3.42% | $385.19 | -3.34% | -11.4 bp |
| META | 3.02% | $630.00 | +1.44% | +4.4 bp |
| WMT | 2.74% | $129.17 | +3.45% | +9.5 bp |
| SPCX | 2.74% | $135.92 | -3.81% | -10.4 bp |

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
