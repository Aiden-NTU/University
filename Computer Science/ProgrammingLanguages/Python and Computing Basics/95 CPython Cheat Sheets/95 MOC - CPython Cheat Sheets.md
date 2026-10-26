# 95 MOC — CPython Cheat Sheets

Lookup-first, runnable deep-dives for CPython **3.14.x**. Long-form theory stays in chapters 05–15 and 11.*; open a sheet, read the comments, then `python3 path/to/sheet.py`.

## How to use

1. Pick a category below.
2. Open the `.py` sheet for the topic.
3. Read top-to-bottom (header → complexity → API → A-vs-B → edges).
4. Run the file to execute the probes at the bottom.
5. Follow the **Source map** into CPython when you want the next layer.

Claims labelled **CPython** are implementation facts, not language laws.

## Categories

| # | Category | Start here |
|---|----------|------------|
| 00 | [[00 Keywords & Builtins/00 MOC\|Keywords & Builtins]] | keywords, soft keywords, high-value builtins |
| 01 | [[01 Data Structures/01 MOC\|Data Structures]] | list, tuple, dict, set, str, bytes, range, memoryview |
| 02 | [[02 Control Flow & Iteration/02 MOC\|Control Flow & Iteration]] | for protocol, generators, match, itertools, contextlib |
| 03 | [[03 Text, Paths & I-O/03 MOC\|Text, Paths & I-O]] | pathlib, io, json, csv, re |
| 04 | [[04 Numbers & Stdlib Data Science/04 MOC\|Numbers & Stdlib Data Science]] | math, statistics, decimal, random, datetime, array |
| 05 | [[05 Collections & Functional Toolkit/05 MOC\|Collections & Functional Toolkit]] | collections, heapq, bisect, functools, dataclasses |
| 06 | [[06 Concurrency/06 MOC\|Concurrency]] | threading, futures, multiprocessing, asyncio |
| 07 | [[07 Network & IPC/07 MOC\|Network & IPC]] | socket, ssl, urllib, http, subprocess pipes |
| 08 | [[08 System, Process & Introspection/08 MOC\|System, Process & Introspection]] | os, sys, gc, dis, inspect, hashlib |

## Sheet template

Every sheet follows [[_TEMPLATE.py|_TEMPLATE.py]].

## Related chapters

- Built-in containers → chapter 07
- Stdlib contracts → chapter 11
- Internals / GC / frames → chapter 15
- Concurrency cost models → chapter 14
