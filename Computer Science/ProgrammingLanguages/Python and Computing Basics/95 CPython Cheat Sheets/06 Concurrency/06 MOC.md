# 06 — Concurrency

## Sheets

| Sheet | Covers |
|-------|--------|
| [[threading_queue_sheet.py]] | Threads, GIL, Queue |
| [[futures_mp_sheet.py]] | concurrent.futures; multiprocessing |
| [[asyncio_sheet.py]] | Event loop, tasks, cancellation |

## A vs B

| Workload | Prefer | Why |
|----------|--------|-----|
| I/O-bound many waits | `asyncio` or threads | Overlap waits |
| CPU-bound pure Python | `multiprocessing` / process pool | Bypass GIL (default build) |
| Mix of blocking libs | `ThreadPoolExecutor` | Simple; GIL released in many C I/O calls |
| Structured async | `asyncio.TaskGroup` (3.11+) | Linked failure |

**CPython 3.14:** free-threaded builds exist; most distro builds still use the GIL. Sheets note both.
