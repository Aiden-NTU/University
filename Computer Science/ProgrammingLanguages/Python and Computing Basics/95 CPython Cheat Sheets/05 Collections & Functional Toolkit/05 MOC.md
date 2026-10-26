# 05 — Collections & Functional Toolkit

## Sheets

| Sheet | Covers |
|-------|--------|
| [[collections_sheet.py]] | deque, Counter, defaultdict, namedtuple, ChainMap |
| [[heapq_bisect_sheet.py]] | Binary heap; bisect invariants |
| [[functools_operator_sheet.py]] | lru_cache, partial, reduce, operator |
| [[dataclasses_enum_copy_typing.py]] | dataclasses, enum, copy, typing runtime |

## A vs B

| Goal | Prefer | Why |
|------|--------|-----|
| Queue both ends | `deque` | O(1) ends |
| Counts of hashables | `Counter` | specialised dict |
| Missing-key factory | `defaultdict` | mutates on `[]` — intentional |
| Top-k / priority | `heapq` | O(log n) push/pop |
| Sorted insert position | `bisect` | Keep list sorted cheaply |
| Memoised pure function | `lru_cache` | hashable args only |
