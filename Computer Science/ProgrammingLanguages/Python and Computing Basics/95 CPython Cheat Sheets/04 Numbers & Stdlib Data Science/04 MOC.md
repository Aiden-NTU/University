# 04 — Numbers & Stdlib Data Science

Stdlib only. NumPy/pandas remain in chapter 16.

## Sheets

| Sheet | Covers |
|-------|--------|
| [[math_statistics_sheet.py]] | math, statistics; float pitfalls |
| [[decimal_fractions_sheet.py]] | Exact decimal / rational when float lies |
| [[random_secrets_sheet.py]] | PRNG vs CSPRNG |
| [[datetime_sheet.py]] | aware vs naive; timedelta |
| [[array_sheet.py]] | `array.array` packed buffers |

## When stdlib is enough vs leave CPython

| Need | Stay in stdlib | Leave for |
|------|----------------|-----------|
| Mean/median/stdev of Python floats | `statistics` | — |
| Exact money / decimal quantize | `decimal` | — |
| Large numeric arrays / BLAS | — | NumPy |
| DataFrames / groupby | — | pandas / polars |
| Crypto-quality tokens | `secrets` | — |
| Simulations / shuffle | `random` | — |
