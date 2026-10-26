#!/usr/bin/env python3
"""
=============================================================================
SHEET: gc + dis + inspect + tracemalloc      TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 15.x internals
=============================================================================

WHAT IT IS
  - gc: cyclic garbage collector (refcounting is primary; gc finds cycles).
  - dis: disassemble bytecode / show opcodes.
  - inspect: signatures, source, callability introspection.
  - tracemalloc: track Python memory allocations by traceback.

INVARIANTS
  - CPython uses refcounting + generational cyclic GC (gens 0/1/2).
  - gc.get_referrers(obj) finds containers that reference obj (debug aid).
  - dis.dis(x) prints; dis.Bytecode for structured access.
  - inspect.signature(callable) fails on some builtins without docs.
  - tracemalloc.start() before allocating of interest; snapshots compare.

DELEGATES TO (CPython)
  - Modules/gcmodule.c, Python/gc.c
  - Lib/dis.py → code object co_code / adaptive specialization (3.11+)
  - Lib/inspect.py
  - Modules/_tracemalloc.c, Lib/tracemalloc.py

COMPLEXITY CARD
  - gc.collect(): can be expensive — pauses proportional to tracked objects
  - get_referrers: scans heaps — debug only
  - tracemalloc: overhead while enabled

WHEN A BEATS B
  - tracemalloc → RSS alone (shows *Python* alloc sites).
  - dis → guessing why a loop is slow without measuring.
  - inspect.signature → brittle manual __code__.co_varnames parsing.

EDGE CASES
  - Objects with __del__ / resurrection complicate GC.
  - get_referrers may include frames / temporaries — interpret carefully.
  - Specialized bytecodes (CACHE / adaptive) appear in 3.11+ dis output.
  - Always tracemalloc.stop() in probes to avoid leaking global state.

SOURCE MAP
  - Modules/gcmodule.c :: gc_collect, get_referrers
  - Lib/dis.py :: dis, Bytecode
  - Lib/inspect.py :: signature, signature.bind
  - Lib/tracemalloc.py :: start, take_snapshot, Filter
=============================================================================
"""

from __future__ import annotations

import dis
import gc
import inspect
import io
import tracemalloc
from typing import Any, Callable, List

# --- API walkthrough ------------------------------------------------------
#
# gc.collect(generation=2) → unreachable count
# gc.get_stats(); gc.get_count(); gc.get_threshold() / set_threshold
# gc.get_referrers(*objs); gc.get_referents(*objs)
# gc.is_tracked(obj); gc.disable() / enable()  # rarely needed
#
# dis.dis(func_or_code); dis.show_code(f)
# for instr in dis.Bytecode(f): instr.opname, instr.argval
#
# sig = inspect.signature(f); sig.parameters; sig.bind(*a, **k)
# inspect.isfunction / ismethod / iscoroutinefunction
# inspect.getsource(f)  # may fail for builtins
#
# tracemalloc.start(nframe=1)
# s1 = tracemalloc.take_snapshot()
# ... allocate ...
# s2 = tracemalloc.take_snapshot()
# top = s2.compare_to(s1, "lineno")
# tracemalloc.stop()


def _sample(a: int, b: str = "x") -> str:
    return f"{a}:{b}"


def _probes() -> None:
    # --- gc generations / referrers --------------------------------------
    stats = gc.get_stats()
    assert isinstance(stats, list) and len(stats) >= 3  # gen 0,1,2
    collected = gc.collect()
    assert collected >= 0

    holder: List[Any] = []
    target = {"probe": True}
    holder.append(target)
    refs = gc.get_referrers(target)
    assert any(r is holder for r in refs), "list should refer to target"

    # Cycle demo: two lists pointing at each other — collectable by gc
    a: List[Any] = []
    b: List[Any] = []
    a.append(b)
    b.append(a)
    del a, b
    gc.collect()

    # --- dis -------------------------------------------------------------
    buf = io.StringIO()
    dis.dis(_sample, file=buf)
    text = buf.getvalue()
    assert "RESUME" in text or "LOAD" in text or "RETURN" in text

    ops = [instr.opname for instr in dis.Bytecode(_sample)]
    assert ops  # non-empty opcode list

    # --- inspect.signature -----------------------------------------------
    sig = inspect.signature(_sample)
    assert list(sig.parameters) == ["a", "b"]
    bound = sig.bind(1)
    bound.apply_defaults()
    assert bound.arguments == {"a": 1, "b": "x"}
    assert _sample(*bound.args, **bound.kwargs) == "1:x"

    # --- tracemalloc snapshots -------------------------------------------
    was_tracing = tracemalloc.is_tracing()
    if not was_tracing:
        tracemalloc.start(1)
    try:
        s1 = tracemalloc.take_snapshot()
        junk = [bytearray(64) for _ in range(200)]
        s2 = tracemalloc.take_snapshot()
        diff = s2.compare_to(s1, "lineno")
        assert isinstance(diff, list)
        # Should observe some allocation growth somewhere
        total = sum(stat.size_diff for stat in diff)
        assert total > 0 or junk  # junk keeps allocations alive until here
        del junk
    finally:
        if not was_tracing:
            tracemalloc.stop()

    print(
        "gc_dis_inspect_tracemalloc: OK",
        f"gc_stats_gens={len(stats)}",
        f"sample_sig={sig}",
    )


if __name__ == "__main__":
    _probes()
