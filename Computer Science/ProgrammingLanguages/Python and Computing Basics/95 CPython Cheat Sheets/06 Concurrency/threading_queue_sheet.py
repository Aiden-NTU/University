#!/usr/bin/env python3
"""
=============================================================================
SHEET: threading + queue                     TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 14.x concurrency cost models
=============================================================================

WHAT IT IS
  - OS threads + sync primitives (Lock, RLock, Event) and Queue for
    producer/consumer. Threads share the process heap; the GIL serialises
    bytecode in the *default* CPython build.

INVARIANTS
  - Only one thread holds the GIL at a time (default build) → pure-Python
    CPU work does not speed up with more threads.
  - Many C extensions / I/O release the GIL → threads *do* overlap waits.
  - Lock is non-reentrant; RLock is reentrant for the same thread.
  - Queue is thread-safe; put/get block by default (or timeout / nowait).
  - Free-threaded 3.14 builds (PEP 703) omit the GIL — races become real;
    still need locks for shared mutable state.

DELEGATES TO (CPython)
  - Modules/_threadmodule.c, Lib/threading.py, Lib/queue.py
  - Objects/obmalloc.c / ceval (GIL acquisition around bytecode)

COMPLEXITY CARD (amortised unless noted)
  - Thread start: O(OS)   notes: expensive vs coroutines
  - Lock acquire (uncontended): ~O(1) atomic
  - Queue put/get: O(1) + possible wait
  - Context switch: OS scheduler; not free

WHEN A BEATS B
  - I/O-bound waits → threads (or asyncio) beat single-threaded blocking.
  - CPU-bound pure Python → ProcessPool / multiprocessing beats threads
    under the GIL; free-threaded build may change that.
  - Queue vs shared list+Lock → Queue encodes blocking/backpressure.

EDGE CASES
  - Daemon threads die with main — unfinished work is lost.
  - join() without timeout can hang forever.
  - Calling lock.acquire() twice on Lock → deadlock (use RLock).
  - Race demos below use intentional windows; production needs locks.

SOURCE MAP
  - Lib/threading.py :: Thread, Lock, RLock, Event, Condition
  - Lib/queue.py :: Queue
  - Python/ceval_gil.c :: take_gil / drop_gil (default build)
=============================================================================
"""

from __future__ import annotations

import queue
import sys
import threading
import time
from typing import List

# --- API walkthrough (dense comments) -------------------------------------

# Thread(target=f, args=(), kwargs={}, daemon=False, name=None)
#   .start()  → OS thread; .join(timeout=None); .is_alive()
#   current_thread(), main_thread(), active_count()
#
# Lock(): acquire(blocking=True, timeout=-1) / release()
#   Prefer:  with lock: ...
# RLock(): same thread may re-acquire; release once per acquire.
#
# Event(): set() / clear() / wait(timeout=None) / is_set()
#   One-shot broadcast “go”; not a barrier (use Barrier for N threads).
#
# queue.Queue(maxsize=0):  # 0 = unbounded
#   put(item, block=True, timeout=None)
#   get(block=True, timeout=None) → item; task_done(); join() waits for
#   as many task_done() as put() for unfinished tasks.
#   Also: LifoQueue, PriorityQueue, SimpleQueue (3.7+, fewer features).
#
# GIL (default build): only one thread executes Python bytecode at a time.
#   Helps: network/file waits that release GIL; some C libs (numpy parts).
#   Does not help: tight pure-Python loops (use processes or free-threaded).
# Free-threaded 3.14: check sys._is_gil_enabled() if available — races need
#   explicit synchronisation even more carefully.

# --- Runnable probes (quiet on import) ------------------------------------


def _gil_note() -> str:
    checker = getattr(sys, "_is_gil_enabled", None)
    if checker is None:
        return "GIL status API unavailable (assume default GIL build)"
    return f"sys._is_gil_enabled() -> {checker()}"


def _probes() -> None:
    """Run with: python3 this_file.py  — offline, no network."""
    assert _gil_note()  # just ensure callable path

    # --- Lock protects a shared counter ----------------------------------
    counter = 0
    lock = threading.Lock()
    N = 2000

    def bump_safe() -> None:
        nonlocal counter
        for _ in range(N):
            with lock:
                counter += 1

    threads = [threading.Thread(target=bump_safe) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert counter == 4 * N, counter

    # --- Intentional race (may or may not lose updates under GIL) --------
    # Under the GIL, += may still tear if bytecode splits around the load/
    # store; free-threaded builds make loss likelier. We only assert that
    # the *locked* version above is correct; race result is observational.
    raced = 0

    def bump_racy() -> None:
        nonlocal raced
        for _ in range(500):
            tmp = raced
            # tiny yield window to encourage interleaving
            time.sleep(0)
            raced = tmp + 1

    racy_threads = [threading.Thread(target=bump_racy) for _ in range(4)]
    for t in racy_threads:
        t.start()
    for t in racy_threads:
        t.join()
    # Do not assert equality — race is the lesson; value is in [1, 2000].
    assert 1 <= raced <= 2000, raced

    # --- RLock reentrancy ------------------------------------------------
    rl = threading.RLock()
    with rl:
        with rl:  # would deadlock with Lock
            pass

    # --- Event gate ------------------------------------------------------
    ready = threading.Event()
    seen: List[str] = []

    def waiter() -> None:
        ready.wait(timeout=2.0)
        seen.append("go")

    tw = threading.Thread(target=waiter)
    tw.start()
    assert not ready.is_set()
    ready.set()
    tw.join(timeout=2.0)
    assert seen == ["go"]

    # --- Queue producer / consumer ---------------------------------------
    q: queue.Queue[int] = queue.Queue(maxsize=8)
    out: List[int] = []

    def producer() -> None:
        for i in range(20):
            q.put(i)
        q.put(None)  # sentinel

    def consumer() -> None:
        while True:
            item = q.get()
            try:
                if item is None:
                    break
                out.append(item)
            finally:
                q.task_done()

    tp = threading.Thread(target=producer)
    tc = threading.Thread(target=consumer)
    tp.start()
    tc.start()
    tp.join()
    tc.join()
    q.join()
    assert out == list(range(20)), out

    print("threading_queue_sheet: OK", _gil_note())


if __name__ == "__main__":
    _probes()
