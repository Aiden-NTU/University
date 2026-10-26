# 00 — Keywords & Builtins

## Sheets

| Sheet | Covers |
|-------|--------|
| [[keywords.py]] | All hard + soft keywords; binding; exceptions; async/yield |
| [[builtins_core.py]] | High-value builtins: iteration, introspection, aggregates |

## Keyword → sheet map

| Keyword / builtin family | Sheet |
|--------------------------|-------|
| `if`/`elif`/`else`, `for`/`while`, `break`/`continue`, `pass` | keywords.py → also 02 |
| `def`/`lambda`/`return`/`yield`/`async`/`await` | keywords.py |
| `class`, `global`, `nonlocal`, `del` | keywords.py |
| `try`/`except`/`finally`/`raise`/`assert` | keywords.py |
| `import`/`from`/`as`, `with` | keywords.py |
| `match`/`case`/`type`/`_` (soft) | keywords.py |
| `and`/`or`/`not`/`in`/`is`, `True`/`False`/`None` | keywords.py |
| `len`, `iter`, `next`, `map`, `filter`, `zip`, `enumerate` | builtins_core.py |
| `open`, `type`, `isinstance`, `hash`, `id`, `sorted` | builtins_core.py |

## A vs B (quick)

| Goal | Prefer | Avoid / weaker |
|------|--------|----------------|
| Early exit over a stream | generator + `any`/`next` | building a full list first |
| Membership in large unique set | `set` / `dict` | `list` linear scan |
| Identity vs equality | `is` for singletons (`None`) | `is` for value equality |
| Call with keywords often | `functools.partial` / explicit kwargs | deep nested lambdas |
