# 02 — Control Flow & Iteration

## Sheets

| Sheet | Covers |
|-------|--------|
| [[iteration_protocol.py]] | `__iter__`/`__next__`, `for`, `zip`, `enumerate` |
| [[generators_comprehensions.py]] | Generators, comps, yield from; cost tradeoffs |
| [[pattern_matching.py]] | `match`/`case` structural patterns |
| [[exceptions_control.py]] | Exceptions as control; EAFP vs LBYL cost |
| [[itertools_sheet.py]] | itertools recipes and C-speed pipelines |
| [[contextlib_sheet.py]] | `with`, contextmanagers, ExitStack |

## A vs B

| Goal | Prefer | Why |
|------|--------|-----|
| Transform then consume once | generator / genexp | Lazy; lower peak memory |
| Need random access / reuse | list / listcomp | Materialised |
| Nested resource cleanup | `ExitStack` / multiple `with` | Deterministic unwind |
| Combinatorial loops | `itertools.product` etc. | C loops, less Python bytecode |
