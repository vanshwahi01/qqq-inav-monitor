# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of October 27, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $721.22 | $721.25 | +0.4 bp | $712.04 (2026-10-26) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| NVDA | 8.20% | $217.94 | +0.90% | +7.4 bp |
| AAPL | 7.91% | $347.10 | +0.93% | +7.3 bp |
| MSFT | 6.23% | $531.33 | -0.24% | -1.5 bp |
| MU | 4.44% | $928.76 | +2.77% | +12.3 bp |
| AMZN | 4.23% | $253.10 | +1.61% | +6.8 bp |
| AMD | 3.77% | $560.26 | +5.45% | +20.6 bp |
| TSLA | 3.24% | $407.46 | +4.04% | +13.1 bp |
| META | 2.95% | $620.19 | -1.64% | -4.9 bp |
| GOOGL | 2.93% | $320.58 | +1.19% | +3.5 bp |
| SPCX | 2.74% | $148.58 | +1.14% | +3.1 bp |

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
