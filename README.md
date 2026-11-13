# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 12, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $688.16 | $688.17 | +0.1 bp | $690.23 (2026-11-11) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.43% | $354.88 | -0.21% | -1.8 bp |
| NVDA | 6.80% | $166.19 | -4.34% | -29.5 bp |
| MSFT | 6.29% | $523.00 | +0.36% | +2.3 bp |
| AMZN | 4.66% | $267.44 | +0.48% | +2.2 bp |
| MU | 4.11% | $798.44 | -1.59% | -6.5 bp |
| AMD | 4.05% | $585.30 | +5.86% | +23.7 bp |
| TSLA | 3.34% | $397.45 | +1.69% | +5.6 bp |
| META | 3.04% | $623.61 | -0.82% | -2.5 bp |
| GOOGL | 2.80% | $298.70 | +1.79% | +5.0 bp |
| WMT | 2.74% | $126.19 | +0.41% | +1.1 bp |

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
