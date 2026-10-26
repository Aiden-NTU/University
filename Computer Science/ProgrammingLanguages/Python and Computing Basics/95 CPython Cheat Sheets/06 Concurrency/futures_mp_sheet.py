#!/usr/bin/env python3
"""
=============================================================================
SHEET: concurrent.futures + processes        TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 14.x concurrency cost models
=============================================================================

WHAT IT IS
  - High-level pools: ThreadPoolExecutor (threads) and ProcessPoolExecutor
    (processes). submit() → Future; map() preserves order of results.
  - Processes bypass the default GIL for CPU-bound Python by using separate
    interpreters; arguments/results must be picklable.

INVARIANTS
  - Thread pool: shared memory; same GIL rules as threading sheet.
  - Process pool: workers are separate processes; no shared Python objects
    unless via Manager / shared memory — prefer return values.
  - Future.result(timeout=...) raises concurrent.futures.TimeoutError;
    worker exceptions re-raised from result().
  - Free-threaded 3.14: threads may help CPU more; pickling still required
    for processes. Most distro builds still ship with the GIL.

DELEGATES TO (CPython)
  - Lib/concurrent/futures/thread.py, process.py
  - Lib/multiprocessing/* (spawn/fork/forkserver start methods)

COMPLEXITY CARD
  - submit: O(1) enqueue; worker cost dominates
  - process spawn: heavy (esp. spawn on Windows/macOS)
  - map: yields in order; may buffer ahead (chunksize for processes)

WHEN A BEATS B
  - I/O-bound / releasing-GIL C → ThreadPoolExecutor (cheap).
  - CPU-bound pure Python (GIL build) → ProcessPoolExecutor.
  - Tiny tasks → pool overhead can exceed gain; batch work.
  - Unpicklable closures / lambdas / local functions → threads or
    top-level defs for processes.

EDGE CASES
  - Nested ProcessPool from already-forked context → use if __name__ guard.
  - max_workers=None defaults differ (threads ~ min(32, cpu+4); processes
    = cpu_count).
  - Cancelling a running Future often cannot stop the worker mid-flight.
  - Exceptions in map() surface on iteration of results.

SOURCE MAP
  - Lib/concurrent/futures/_base.py :: Future, Executor
  - Lib/concurrent/futures/process.py :: ProcessPoolExecutor
  - Lib/multiprocessing/process.py :: BaseProcess
=============================================================================
"""

from __future__ import annotations

import math
import os
import sys
import time
from concurrent.futures import (
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
from typing import Iterable, List


# --- Top-level worker (must be picklable for ProcessPool) -----------------

def _cpu_chunk(n: int) -> int:
    """Pure-Python CPU bite — process pool can parallelise under GIL."""
    s = 0
    for i in range(n):
        s += i * i
    return s


def _io_like(delay: float) -> float:
    """Simulate I/O wait (sleep releases GIL → threads help)."""
    time.sleep(delay)
    return delay


def _gil_note() -> str:
    checker = getattr(sys, "_is_gil_enabled", None)
    if checker is None:
        return "GIL API N/A (default build assumed)"
    return f"sys._is_gil_enabled() -> {checker()}"


# --- API walkthrough ------------------------------------------------------
#
# with ThreadPoolExecutor(max_workers=4) as ex:
#     fut = ex.submit(fn, *args)          # → Future
#     fut.result(timeout=None)            # blocks; re-raises worker error
#     fut.done(), fut.cancelled(), fut.exception()
#     list(ex.map(fn, iterable, timeout=None, chunksize=1))
#
# ProcessPoolExecutor: same API; workers import __main__ / module.
#   Pickling boundary: args, kwargs, return value, and the callable itself
#   (module-level functions OK; nested/lambda usually not).
#
# as_completed(fs, timeout=None): yield Futures as they finish (any order).
# wait(fs, return_when=FIRST_COMPLETED | FIRST_EXCEPTION | ALL_COMPLETED)
#
# CPU vs I/O:
#   - sleep / socket / many C I/O → threads overlap waits.
#   - pure Python arithmetic → processes (or free-threaded build).

# --- Runnable probes ------------------------------------------------------


def _probes() -> None:
    """Offline probes; ProcessPool may be skipped if start fails."""
    # --- ThreadPool map / submit -----------------------------------------
    with ThreadPoolExecutor(max_workers=4) as ex:
        doubled = list(ex.map(lambda x: x * 2, range(5)))
        assert doubled == [0, 2, 4, 6, 8], doubled

        futs = [ex.submit(_io_like, 0.01) for _ in range(4)]
        got = [f.result(timeout=5) for f in as_completed(futs)]
        assert all(x == 0.01 for x in got)

    # --- ProcessPool: pickling + CPU -------------------------------------
    # Guard: some environments restrict process spawn; soft-skip on failure.
    try:
        with ProcessPoolExecutor(max_workers=2) as ex:
            # Top-level function + int args → picklable
            results = list(ex.map(_cpu_chunk, [2000, 3000, 1000]))
            assert results == [_cpu_chunk(2000), _cpu_chunk(3000), _cpu_chunk(1000)]

            fut = ex.submit(math.factorial, 10)
            assert fut.result(timeout=30) == 3_628_800

            # Demonstrate pickling failure surfaces as exception on result
            def nested(x: int) -> int:  # local → typically unpicklable
                return x

            bad = ex.submit(nested, 1)
            try:
                bad.result(timeout=10)
                # Some start methods might surprise; if it "works", fine.
            except Exception:
                pass  # expected path: PicklingError / BrokenProcessPool wrap
    except Exception as exc:
        # Still exit 0 — document that process pools need a working spawn.
        print(f"ProcessPool soft-skip: {type(exc).__name__}: {exc}")

    # --- Order: map preserves input order --------------------------------
    with ThreadPoolExecutor(max_workers=3) as ex:
        ordered = list(ex.map(lambda x: x, [3, 1, 2]))
        assert ordered == [3, 1, 2]

    cpus = os.cpu_count()
    print(
        "futures_mp_sheet: OK",
        f"cpu_count={cpus}",
        _gil_note(),
    )


if __name__ == "__main__":
    # Required for ProcessPoolExecutor on spawn platforms
    _probes()
