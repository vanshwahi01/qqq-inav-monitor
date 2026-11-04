# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 3, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $685.50 | $685.28 | -3.1 bp | $680.87 (2026-11-02) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.13% | $331.90 | -1.90% | -15.4 bp |
| NVDA | 8.02% | $206.69 | +2.29% | +18.4 bp |
| MSFT | 6.20% | $520.99 | +2.74% | +17.0 bp |
| AMZN | 4.36% | $250.69 | +2.06% | +9.0 bp |
| MU | 4.28% | $855.10 | +2.58% | +11.1 bp |
| TSLA | 3.49% | $398.50 | -1.32% | -4.6 bp |
| AMD | 3.47% | $483.90 | +3.65% | +12.7 bp |
| META | 2.97% | $621.03 | +2.36% | +7.0 bp |
| WMT | 2.82% | $124.86 | -2.22% | -6.3 bp |
| GOOGL | 2.70% | $280.03 | +0.37% | +1.0 bp |

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
