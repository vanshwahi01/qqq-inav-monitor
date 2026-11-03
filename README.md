# QQQ iNAV

Rebuilds the value of the Invesco QQQ ETF from its daily holdings and compares it with the price QQQ actually closed at. The gap is the ETF's premium or discount. 
It runs for free on GitHub Actions every weekday after the US close and updates this page.

<!-- latest:start -->
**As of November 2, 2026**

| iNAV | QQQ close | Premium / discount | Official NAV |
|---|---|---|---|
| $680.90 | $681.09 | +2.9 bp | $690.49 (2026-10-30) |

![Premium / discount chart](output/chart.png)

<details><summary>Top 10 holdings</summary>

| Ticker | Weight | Close | Move | Contrib. |
|---|---|---|---|---|
| AAPL | 8.17% | $338.32 | -1.83% | -15.0 bp |
| NVDA | 8.01% | $202.06 | -1.26% | -10.1 bp |
| MSFT | 6.29% | $507.12 | -2.83% | -17.8 bp |
| MU | 4.48% | $833.59 | -5.78% | -25.9 bp |
| AMZN | 4.21% | $245.63 | +2.20% | +9.2 bp |
| AMD | 3.69% | $466.84 | -7.52% | -27.8 bp |
| TSLA | 3.41% | $403.82 | +1.00% | +3.4 bp |
| META | 2.97% | $606.73 | -1.34% | -4.0 bp |
| WMT | 2.69% | $127.69 | +3.38% | +9.1 bp |
| GOOGL | 2.67% | $278.99 | -0.30% | -0.8 bp |

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
