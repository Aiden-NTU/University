# 01 — Data Structures

## Sheets

| Sheet | Covers |
|-------|--------|
| [[set_frozenset.py]] | Open-addressed hash sets; probe; dummy; set algebra |
| [[dict.py]] | Compact dict; insertion order; views; key lifecycle |
| [[list.py]] | Overallocated array of pointers; amortised append |
| [[tuple.py]] | Immutable sequence; freelist; hashability rules |
| [[str_bytes.py]] | Compact unicode; bytes vs str; join vs `+` |
| [[range_memoryview_array.py]] | Lazy ranges; buffer protocol; `array.array` |

## A vs B

| Goal | Prefer | Why |
|------|--------|-----|
| Unique membership tests | `set` / `frozenset` | Average O(1) hash lookup |
| Keyed records + order | `dict` | Compact table + insertion order |
| Stack / growable sequence | `list` | Amortised O(1) append/pop end |
| Queue (both ends) | `collections.deque` | O(1) ends; list `pop(0)` is O(n) |
| Immutable record / dict key | `tuple` (hashable elems) | Fixed structure, hashable if elems are |
| Binary blob | `bytes` / `bytearray` / `memoryview` | No text decode cost |
| Dense numeric C types | `array.array` | Packed; still not NumPy |
