#!/usr/bin/env python3
"""
=============================================================================
SHEET: asyncio                               TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 14.x concurrency cost models
=============================================================================

WHAT IT IS
  - Cooperative concurrency on one thread (typical): coroutines scheduled
    by an event loop. await yields control so other Tasks can run during
    I/O waits. Does not remove the GIL for CPU; free-threaded 3.14 is a
    separate axis (threads vs async still different models).

INVARIANTS
  - Only one Task runs at a time per loop thread until it awaits.
  - Blocking the loop (time.sleep, heavy CPU, sync I/O) stalls *all* tasks.
  - Cancellation: CancelledError injected at await points; clean up in
    try/finally or with TaskGroup structured shutdown.
  - TaskGroup (3.11+): if one task fails, siblings are cancelled; group
    raises ExceptionGroup (unless cancelled).

DELEGATES TO (CPython)
  - Lib/asyncio/events.py, tasks.py, taskgroups.py, runners.py
  - Selector / IOCP event loop backends (platform-dependent)

COMPLEXITY CARD
  - create_task: O(1) schedule
  - gather N: completes when all (or first error depending on flags)
  - Context switch: coroutine yield — cheaper than OS threads

WHEN A BEATS B
  - Many concurrent sockets / timers → asyncio beats one-thread-per-conn.
  - Blocking library with no async API → ThreadPoolExecutor.run_in_executor
    or threads; don't call it on the loop thread.
  - CPU-bound → processes / free-threaded + threads; not more await.
  - Simple scripts → asyncio.run(main()); avoid nested run().

EDGE CASES
  - Forgotten create_task without strong ref → task may be GC'd (3.12+
    emits warning); keep references or use TaskGroup.
  - shield() protects from outer cancellation but not forever.
  - gather(..., return_exceptions=True) never raises — check results.
  - asyncio.sleep(0) yields once; useful to let others run.

SOURCE MAP
  - Lib/asyncio/runners.py :: run
  - Lib/asyncio/tasks.py :: create_task, gather, sleep, wait_for
  - Lib/asyncio/taskgroups.py :: TaskGroup
=============================================================================
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any, List


# --- API walkthrough ------------------------------------------------------
#
# async def coro() -> T: ...
#   await awaitable   # Task, Future, another coro, or Protocol
#
# asyncio.run(coro())                 # owns the loop (usual entry)
# asyncio.create_task(coro())         # schedule on running loop → Task
# asyncio.TaskGroup() as tg:          # 3.11+ structured concurrency
#     tg.create_task(coro())
#
# await asyncio.gather(*aws, return_exceptions=False)
# await asyncio.sleep(delay, result=None)
# await asyncio.wait_for(aw, timeout)
# task.cancel(); await task  → CancelledError (or result if finished first)
#
# Event loop: get_running_loop() inside async; don't block it.
# Free-threaded 3.14: async still cooperative; GIL note is about threads/
#   processes for CPU, not a substitute for await points.

def _gil_note() -> str:
    checker = getattr(sys, "_is_gil_enabled", None)
    if checker is None:
        return "GIL API N/A"
    return f"sys._is_gil_enabled() -> {checker()}"


async def _tick(name: str, delay: float, sink: List[str]) -> str:
    await asyncio.sleep(delay)
    sink.append(name)
    return name


async def _boom() -> None:
    await asyncio.sleep(0.01)
    raise ValueError("boom")


async def _cancellable(flag: dict[str, bool]) -> None:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        flag["cancelled"] = True
        raise


async def _async_main() -> None:
    order: List[str] = []

    # --- gather: concurrent sleeps ---------------------------------------
    results = await asyncio.gather(
        _tick("a", 0.02, order),
        _tick("b", 0.01, order),
        _tick("c", 0.005, order),
    )
    assert set(results) == {"a", "b", "c"}
    # Faster finishes first into `order`
    assert order[0] == "c", order

    # --- Task + cancellation ---------------------------------------------
    flag = {"cancelled": False}
    task = asyncio.create_task(_cancellable(flag))
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert flag["cancelled"] is True

    # --- TaskGroup: linked failure ---------------------------------------
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(_tick("ok", 0.01, []))
            tg.create_task(_boom())
    except* ValueError as eg:
        assert any(isinstance(e, ValueError) for e in eg.exceptions)
    else:
        raise AssertionError("TaskGroup should have raised ExceptionGroup")

    # --- sleep(0) yield --------------------------------------------------
    hopped: List[int] = []

    async def a() -> None:
        hopped.append(1)
        await asyncio.sleep(0)
        hopped.append(3)

    async def b() -> None:
        hopped.append(2)

    await asyncio.gather(a(), b())
    assert hopped == [1, 2, 3], hopped

    # Document: never call blocking time.sleep on the loop thread.
    # Use await asyncio.sleep or run_in_executor for sync blockers.


def _probes() -> None:
    """Run with: python3 this_file.py"""
    asyncio.run(_async_main())
    print("asyncio_sheet: OK", _gil_note())


if __name__ == "__main__":
    _probes()
