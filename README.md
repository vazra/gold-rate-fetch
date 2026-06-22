# Kerala Gold Holdings Calculator (24K)

Single self-contained `index.html` web app. Pick a date (+ intraday update) and an amount in ₹;
it computes the gold weight (`grams = amount ÷ 24K per-gram rate`), lists purchases, and totals
holdings in grams and pavan. Purchases persist in the browser (`localStorage`). No backend.

**Live:** https://vazra.github.io/gold-rate-fetch/

## Data
- `kerala_gold_24k_daily_2yr.csv` — daily All-Kerala 24K rates, 2024-06-01 to 2026-06-22 (830 rows incl. intraday updates). Source: keralagoldrates.com.
- `build_index.py` — regenerates `index.html` (embeds the CSV). Run `python3 build_index.py` after updating the data.
