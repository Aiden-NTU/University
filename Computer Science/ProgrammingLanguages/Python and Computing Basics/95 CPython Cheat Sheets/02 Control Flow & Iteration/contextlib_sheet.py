#!/usr/bin/env python3
"""
=============================================================================
SHEET: contextlib & with protocol      TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x resources / PEP 343 with-statement
=============================================================================

WHAT IT IS
  - The *context management protocol*: __enter__ / __exit__ (or C slots)
    enabling `with obj as name:` for deterministic setup/teardown.
  - contextlib: stdlib helpers — @contextmanager, closing, suppress,
    ExitStack, nullcontext, redirect_stdout/stderr, … — so you rarely
    hand-write classes for simple cases.

INVARIANTS
  - with cm as x:  →  x = cm.__enter__(); try: body; finally:
    exc = …; cm.__exit__(exc_type, exc, tb); optionally suppress.
  - __exit__ returns a true value ⇒ exception is *suppressed* (like
    except that handled it). False / None ⇒ re-raise.
  - Multiple context managers in one with are like nested withs —
    enter L→R, exit R→L (same as ExitStack order discipline).
  - @contextmanager: yield once; code before yield = enter, after = exit.
    Exceptions in the with body are re-raised at the yield point.
  - ExitStack.enter_context / callbacks unwind in reverse registration
    order even when enter fails halfway (already-entered are cleaned).

DELEGATES TO (CPython)
  - Python/ceval.c — SETUP_WITH / WITH_EXCEPT_START / before+after 3.11
    exception table forms for with
  - Objects/typeobject.c — tp_as_context slots
  - Lib/contextlib.py — ContextDecorator, ExitStack, generators→CM
  - Objects/clinic / abstract — PyObject_Enter / Leave helpers where used

COMPLEXITY CARD
  - with enter/exit:           O(1)+ user callbacks
  - ExitStack with n cms:      O(n) enter; O(n) exit (LIFO)
  - @contextmanager:           generator allocate + one yield round-trip
  - suppress(*types):          O(1) + isinstance checks on exit
  - nullcontext:               O(1) no-op enter/exit
  - redirect_stdout:           O(1) swap sys.stdout (not thread-safe)

WHEN A BEATS B
  - @contextmanager vs class CM: decorator for simple split setup/teardown;
    class when you need reuse, inheritance, or rich state/API on the CM.
  - ExitStack vs nested with: ExitStack when N is dynamic / conditional /
    open-in-a-loop; nested with when fixed and small.
  - nullcontext vs optional if: nullcontext keeps a single with shape when
    a CM is optional (typing/branches).
  - suppress(FileNotFoundError) vs exists check: suppress for EAFP delete;
    don't use suppress to hide unexpected bugs.
  - closing(obj) vs native CM: for objects with .close() but no __enter__
    (legacy APIs). Prefer native context managers when available.

EDGE CASES
  - Yielding twice / not yielding in @contextmanager → RuntimeError.
  - If __enter__ raises, __exit__ is NOT called for that CM.
  - redirect_stdout is process-global (sys.stdout) — unsafe across threads
    without locks; prefer passing an explicit file-like to APIs.
  - ExitStack.pop_all() transfers ownership — useful when cleanup should
    move to another scope.
  - ContextDecorator lets the same object be used as decorator + with.
  - async with / AsyncExitStack are the asyncio cousins (different sheet).

SOURCE MAP
  - Lib/contextlib.py :: contextmanager / ExitStack / suppress / closing
  - Lib/contextlib.py :: nullcontext / redirect_stdout / ContextDecorator
  - Python/ceval.c :: with-statement opcodes / exception handling
  - PEP 343
=============================================================================
"""

from __future__ import annotations

import io
import sys
from contextlib import (
    ExitStack,
    closing,
    contextmanager,
    nullcontext,
    redirect_stdout,
    suppress,
)
from typing import Any, Iterator

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- Protocol: __enter__ / __exit__ --------------------------------------


class Gate:
    """Minimal CM: records lifecycle; suppresses ValueError if asked."""

    def __init__(self, name: str, *, swallow_value: bool = False) -> None:
        self.name = name
        self.swallow_value = swallow_value
        self.events: list[str] = []

    def __enter__(self) -> "Gate":
        self.events.append(f"enter:{self.name}")
        return self  # bound to `as` target

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: Any) -> bool:
        self.events.append(f"exit:{self.name}:{exc_type and exc_type.__name__}")
        # Return True → suppress the exception (don't propagate).
        return bool(self.swallow_value and exc_type is ValueError)


g = Gate("g")
with g as cm:
    assert cm is g
assert g.events == ["enter:g", "exit:g:None"]

g2 = Gate("g2", swallow_value=True)
with g2:
    raise ValueError("hidden")
assert g2.events[-1] == "exit:g2:ValueError"  # suppressed

# Nested / multi-item with: enter A then B; exit B then A.
log: list[str] = []


class LogCM:
    def __init__(self, label: str) -> None:
        self.label = label

    def __enter__(self) -> str:
        log.append(f"+{self.label}")
        return self.label

    def __exit__(self, *args: object) -> None:
        log.append(f"-{self.label}")


with LogCM("A") as a, LogCM("B") as b:
    assert (a, b) == ("A", "B")
assert log == ["+A", "+B", "-B", "-A"]

# --- @contextmanager -----------------------------------------------------
# Generator-based CM: setup → yield resource → teardown in finally.


@contextmanager
def temp_binding(box: dict[str, Any], key: str, value: Any) -> Iterator[Any]:
    old = box.get(key, _MISSING := object())
    box[key] = value
    try:
        yield value  # __enter__ returns this; body runs here
    finally:
        if old is _MISSING:
            box.pop(key, None)
        else:
            box[key] = old


ns: dict[str, Any] = {"x": 1}
with temp_binding(ns, "x", 99) as v:
    assert v == 99 and ns["x"] == 99
assert ns["x"] == 1

# Exceptions in the body propagate to the yield line — you can catch or
# let finally run and re-raise (default).


@contextmanager
def mark(events: list[str], name: str) -> Iterator[None]:
    events.append(f"in:{name}")
    try:
        yield
    except RuntimeError:
        events.append(f"caught:{name}")
        # no re-raise → suppresses like __exit__ returning True
    finally:
        events.append(f"out:{name}")


ev: list[str] = []
with mark(ev, "m"):
    raise RuntimeError("x")
assert ev == ["in:m", "caught:m", "out:m"]

# --- closing -------------------------------------------------------------
# For objects that have .close() but are not context managers.


class Legacy:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def read(self) -> str:
        return "data"


with closing(Legacy()) as leg:
    assert leg.read() == "data"
assert leg.closed is True

# --- suppress ------------------------------------------------------------
# Swallow specific exception types from the with body (EAFP shorthand).
path_missing = []
with suppress(FileNotFoundError, KeyError):
    path_missing.append(open("/nonexistent/cpython-cheat-sheet-probe"))  # noqa
assert path_missing == []

d = {"a": 1}
with suppress(KeyError):
    del d["missing"]
assert d == {"a": 1}

# --- nullcontext ---------------------------------------------------------
# Optional CM: keep one code path whether or not a real CM is provided.


def write_line(line: str, sink: Any | None = None) -> str:
    buffer = io.StringIO()
    cm = sink if sink is not None else nullcontext(buffer)
    with cm as f:
        f.write(line)
        return f.getvalue() if sink is None else line


assert write_line("hi") == "hi"

# --- ExitStack -----------------------------------------------------------
# Dynamic / variable number of contexts; LIFO cleanup; safe if enter fails.


def open_many(texts: list[str]) -> list[str]:
    out: list[str] = []
    with ExitStack() as stack:
        files = [
            stack.enter_context(closing(_FakeFile(t))) for t in texts
        ]
        for f in files:
            out.append(f.read())
        # all .close() called when leaving the with — reverse order
    return out


class _FakeFile:
    def __init__(self, text: str) -> None:
        self.text = text
        self.closed = False

    def read(self) -> str:
        return self.text

    def close(self) -> None:
        self.closed = True


assert open_many(["a", "b", "c"]) == ["a", "b", "c"]

# Callbacks without full CMs:
order: list[str] = []
with ExitStack() as stack:
    stack.callback(order.append, "first-registered")
    stack.callback(order.append, "second-registered")
assert order == ["second-registered", "first-registered"]  # LIFO

# enter_context failure: previously entered CMs still exit.
partial: list[str] = []


class OkCM:
    def __enter__(self) -> None:
        partial.append("ok-enter")

    def __exit__(self, *a: object) -> None:
        partial.append("ok-exit")


class BoomCM:
    def __enter__(self) -> None:
        raise RuntimeError("enter-fail")

    def __exit__(self, *a: object) -> None:
        partial.append("boom-exit")  # not called — enter never succeeded


try:
    with ExitStack() as stack:
        stack.enter_context(OkCM())
        stack.enter_context(BoomCM())
except RuntimeError:
    pass
assert partial == ["ok-enter", "ok-exit"]

# --- redirect_stdout -----------------------------------------------------
# Temporarily swap sys.stdout (thread-hostile — demo only).
buf = io.StringIO()
with redirect_stdout(buf):
    print("hello", end="")
assert buf.getvalue() == "hello"
# sys.stdout restored after the with


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    # protocol suppress
    box = Gate("p", swallow_value=True)
    with box:
        raise ValueError("n")
    assert "ValueError" in box.events[-1]

    # contextmanager restore
    state = {"k": 0}
    with temp_binding(state, "k", 5):
        assert state["k"] == 5
    assert state["k"] == 0

    # suppress
    with suppress(ZeroDivisionError):
        _ = 1 / 0

    # nullcontext identity
    sentinel = object()
    with nullcontext(sentinel) as s:
        assert s is sentinel

    # ExitStack LIFO callbacks
    seq: list[int] = []
    with ExitStack() as stack:
        for i in range(3):
            stack.callback(seq.append, i)
    assert seq == [2, 1, 0]

    # redirect round-trip
    old = sys.stdout
    b = io.StringIO()
    with redirect_stdout(b):
        print("x", end="")
    assert sys.stdout is old and b.getvalue() == "x"

    # closing
    lg = Legacy()
    with closing(lg):
        pass
    assert lg.closed

    print("contextlib_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
