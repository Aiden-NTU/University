#!/usr/bin/env python3
"""
=============================================================================
SHEET: keywords (hard + soft)           TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 00 Keywords & Builtins / control-flow / binding
=============================================================================

WHAT IT IS
  - Hard keywords (`keyword.kwlist`) are reserved tokens: you cannot bind them
    as names. Soft keywords (`keyword.softkwlist`: match, case, type, _) are
    contextual — they are keywords only in specific grammatical positions and
    remain usable as ordinary identifiers elsewhere.
  - Keywords drive the grammar (Parser/ + Python/compile.c) and lower to
    bytecode executed by the eval loop (Python/ceval.c). Binding rules live
    in the symbol table (Python/symtable.c). Built-in constants True/False/None
    are wired through Python/bltinmodule.c / Objects/.

INVARIANTS
  - True, False, None are singletons: there is exactly one of each in a
    process; `is` and `==` both succeed for them, but `is` is the idiomatic
    check (and the one the compiler special-cases for None).
  - `and` / `or` return an operand, not a coerced bool — short-circuit is
    both control-flow and value-producing.
  - Loop `else` runs iff the loop did NOT exit via `break`.
  - `try`/`except`/`else`/`finally`: `else` runs only if no exception;
    `finally` always runs (even on return/break/continue out of the try).
  - Default argument values are evaluated once at `def` time, not per call.
  - `global` / `nonlocal` declare binding scope; they do not create names.
  - Soft keywords are NOT in `keyword.kwlist`; use `keyword.issoftkeyword`.

DELEGATES TO (CPython)
  - Grammar / AST: Parser/, Python/ast.c, Python/compile.c
  - Symbol table: Python/symtable.c (LOCAL / GLOBAL_EXPLICIT / FREE / CELL)
  - Eval loop: Python/ceval.c (opcodes: JUMP_IF_*, FOR_ITER, LOAD_*, STORE_*,
    RAISE_VARARGS, WITH_EXCEPT_START, GET_AWAITABLE, YIELD_VALUE, …)
  - Exceptions: Objects/exceptions.c; chaining on BaseException
  - Import: Python/import.c + importlib (Lib/importlib/)
  - Builtins module: Python/bltinmodule.c
  - Types: Objects/typeobject.c (type_call → tp_new/tp_init)

COMPLEXITY CARD (amortised unless noted)
  - Keyword dispatch itself: O(1) (compile-time); runtime cost is the
    construct (loop body, exception path, import I/O).
  - `in` on list/tuple: O(n); on set/dict/frozenset: avg O(1); on str: O(n·m)
  - `is`: O(1) pointer compare; `==`: may call __eq__ → arbitrary cost
  - `import`: first load dominated by filesystem + exec; then sys.modules hit
  - Exception raise/catch: expensive vs a branch — do not use for control flow
  - `match` subject + patterns: linear in patterns; capture/guards add cost

WHEN A BEATS B
  - `x is None` beats `x == None` (idiom + identity; None has no rich compare
    surprises with custom __eq__).
  - `and`/`or` for defaulting (`x or default`) beats ternary when falsy→default
    is intended; use `x if x is not None else d` when 0/"" must survive.
  - Loop `else` beats a flag variable for “completed without break”.
  - `with` beats manual try/finally for resource pairing (__enter__/__exit__).
  - `yield from` / `async for` beat hand-rolled delegation loops.
  - Soft `type` alias beats stringy forward refs when you want a real TypeAlias
    binding (PEP 695); hard `class` still wins for real types with methods.

EDGE CASES
  - Assignment expression `:=` (walrus) is an OPERATOR, not a keyword.
  - `else` on `for`/`while` is easy to misread — not “else if”.
  - Bare `except:` catches BaseException (incl. KeyboardInterrupt/SystemExit);
    prefer `except Exception:`.
  - `raise` without args only valid inside an except; re-raises current.
  - `del x` unbinds the name; `del a[i]` / `del a.b` call __delitem__/__delattr__.
  - Mutable default args are a classic trap (shared across calls).
  - `async def` returns a coroutine object; calling it does NOT run the body.
  - Soft `_` in match is a wildcard; elsewhere `_` is a normal name (often
    “discarded” by convention only).
  - `type` soft keyword (PEP 695) vs builtin `type` — context decides.

SOURCE MAP
  - Python/ceval.c          :: PyEval_EvalFrameDefault, opcode handlers
  - Python/compile.c        :: compiler_*, codegen for stmts/exprs
  - Python/symtable.c       :: symtable_visit_*, analyze_block
  - Python/bltinmodule.c    :: builtin constants / helpers
  - Objects/typeobject.c    :: type_call, type_new
  - Objects/exceptions.c    :: BaseException, __cause__/__context__
  - Python/import.c         :: PyImport_ImportModule*
  - Lib/keyword.py          :: kwlist, softkwlist
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import ast
import keyword
import sys
from contextlib import contextmanager
from typing import Any, Iterator

# ============================================================================
# HARD KEYWORDS — keyword.kwlist (CPython 3.14)
# ============================================================================
# False None True and as assert async await break class continue def del
# elif else except finally for from global if import in is lambda nonlocal
# not or pass raise return try while with yield
#
# Soft (keyword.softkwlist): _  case  match  type
# ============================================================================

## True / False / None — singletons (not “just” literals)
# The compiler emits LOAD_CONST for these. Identity is stable for the life of
# the process. Prefer `is` / `is not` for None (PEP 8); True/False usually use
# truthiness (`if flag:`) rather than `is True`, except when distinguishing
# True from other truthy values.
_TRUE, _FALSE, _NONE = True, False, None
assert _TRUE is True and _FALSE is False and _NONE is None
_one = 1
assert (True == _one) and (True is not _one)  # equality ≠ identity for bool vs int
# bool subclasses int; True == 1, but they are different objects.

## is vs ==
# `is`  → pointer identity (ceval: IS_OP). No __eq__ call.
# `==`  → rich comparison (__eq__), may fall back to identity.
# Rule: singletons / sentinels → `is`; values → `==`.


## and / or — short-circuit, return operand
# Semantics (left to right):
#   x and y  →  if x is falsy: return x; else return y
#   x or  y  →  if x is truthy: return x; else return y
# NOT boolean coercion at the keyword level — truth-value testing uses
# __bool__ / __len__ (Objects/abstract.c :: PyObject_IsTrue).
def _demo_and_or(x: Any, y: Any) -> tuple[Any, Any]:
    return (x and y, x or y)


## not — unary boolean invert of truth value
# `not x` always returns True or False (actual bool singleton).


## in / not in
# Containment: calls __contains__ if present, else iterates.
# For dict: tests KEYS. For str: substring search.
def _demo_in() -> bool:
    return "a" in {"a", "b"} and 1 not in (2, 3)


## if / elif / else
# Compiles to conditional jumps (POP_JUMP_IF_*, etc.). Only one branch body
# runs. `elif` is syntactic sugar for nested else-if.
def _classify(n: int) -> str:
    if n < 0:
        return "neg"
    elif n == 0:
        return "zero"
    else:
        return "pos"


## Walrus `:=` — NOT a keyword (assignment expression, PEP 572)
# Allowed in conditions / comprehensions to bind while testing:
#   if (m := re.search(...)): use m
# Forbidden as a bare statement replacement for `=` in most positions.
# Mentioned here only so learners do not hunt for it in kwlist.


## for / while / break / continue / else-on-loops
# for x in it:  → GET_ITER + FOR_ITER loop in ceval.c
# while cond:   → conditional jumps
# break         → jump out of innermost loop; suppresses loop-else
# continue      → jump to next iteration (still allows loop-else if finishes)
# for/while else: runs when loop terminates “naturally” (iterator exhausted
# or condition false) WITHOUT hitting break.
def _find_first_even(xs: list[int]) -> int | None:
    for x in xs:
        if x % 2 == 0:
            break
    else:
        return None  # no break → no even found
    return x


## def / lambda / return
# `def` creates a function object at runtime (MAKE_FUNCTION); body compiles
# to a code object. `lambda` is an expression form of a single-expression
# anonymous function (no statements).
# Default args evaluated ONCE at definition time — classic mutable trap.
def _accumulator(item: int, bucket: list[int] | None = None) -> list[int]:
    # Correct pattern: default None, create fresh list per call when needed.
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


def _bad_default(item: int, bucket: list[int] = []) -> list[int]:  # noqa: B006
    # Shared list across calls — educational footgun only.
    bucket.append(item)
    return bucket


_add = lambda a, b: a + b  # noqa: E731 — fine for teaching; prefer def in real code


## class — type call basics
# class C(Base, metaclass=M): ...
# Roughly: namespace = exec(body); C = metaclass(name, bases, namespace)
# Default metaclass is `type`. See Objects/typeobject.c :: type_call.
class _Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


## global / nonlocal — symbol table (symtable.c)
# Without declaration: assignment creates a LOCAL name in the current function.
# `global x`    → bind x in the module globals.
# `nonlocal x`  → bind x in the nearest enclosing function scope (closure cell).
# Reading alone may close over outer names (LOAD_DEREF) without nonlocal;
# ASSIGNMENT to an outer function name requires `nonlocal`.
_G = 0


def _bump_global() -> int:
    global _G
    _G += 1
    return _G


def _make_counter(start: int = 0):
    n = start

    def inc() -> int:
        nonlocal n
        n += 1
        return n

    return inc


## del — unbind vs container delete
# del name          → unbind from local/global (DELETE_FAST / DELETE_NAME / …)
# del obj[key]      → obj.__delitem__(key)
# del obj.attr      → type(obj).__delattr__(obj, "attr")
# Does NOT “call the destructor” by itself; __del__ runs when refcount→0
# (CPython), which is not guaranteed timing under cycles/GC.
def _demo_del() -> None:
    d = {"a": 1, "b": 2}
    del d["a"]  # __delitem__
    x = 1
    del x  # unbind local name


## try / except / else / finally / raise / assert
# try:
#   BODY
# except E1 as e: ...
# except* EG: ...   # ExceptionGroup (PEP 654) — related, not a separate keyword
# else:             # no exception in BODY
# finally:          # always; runs before leaving the try statement
#
# Exception chaining:
#   raise New from old     → __cause__ = old; __suppress_context__ = True
#   raise New              → inside except: __context__ = caught
# assert expr[, msg]  → if __debug__ (True unless -O): if not expr: raise AssertionError
def _div(a: int, b: int) -> float:
    try:
        return a / b
    except ZeroDivisionError as e:
        raise ValueError("b must be non-zero") from e
    else:
        pass  # unreachable here because return above; shown for structure
    finally:
        pass  # runs even when returning / raising


## import / from / as — importlib briefly
# import pkg.mod as m
# from pkg.mod import name as n
# Mechanism: sys.modules cache → loaders via importlib (Python/import.c hooks).
# Prefer `importlib.import_module("a.b")` for dynamic names; avoid bare
# `__import__` unless mirroring the statement semantics carefully.
import math as _math  # noqa: E402 — after teaching block by design
from math import sqrt as _sqrt  # noqa: E402


## with — context managers (__enter__ / __exit__)
# with CM as x: BODY
# ≈
#   mgr = CM
#   x = mgr.__enter__()
#   try: BODY
#   except: if not mgr.__exit__(*sys.exc_info()): raise
#   else: mgr.__exit__(None, None, None)
# Multiple items: with A() as a, B() as b: ...
# Async form: async with (uses __aenter__/__aexit__).
@contextmanager
def _temp_flag() -> Iterator[dict[str, bool]]:
    state = {"on": True}
    try:
        yield state
    finally:
        state["on"] = False


## async / await / yield / yield from — coroutine vs generator
# def f(): yield ...           → generator function; calling f() → generator
# async def g(): ...           → coroutine function; calling g() → coroutine
# await expr                   → wait on awaitable (coroutine / Task / …)
# yield from it                → delegate to a subgenerator (PEP 380)
# Generators implement the iterator protocol; coroutines are driven by an
# event loop (or await). Mixing: async generators use `async def` + `yield`.
def _gen() -> Iterator[int]:
    yield 1
    yield from range(2, 4)  # yields 2, 3


async def _coro_add(a: int, b: int) -> int:
    return a + b  # trivial awaitable demo; real code awaits I/O


## pass — no-op statement
# Fills a required suite when you need empty body (class stub, TODO branch).
class _Stub:
    pass


## Soft keywords: match / case / type / _
# Available via keyword.softkwlist. Contextual — these names remain legal
# identifiers outside the soft-keyword grammar positions.


def _demo_match(value: object) -> str:
    # Structural pattern matching (PEP 634+). Subject evaluated once.
    match value:
        case 0:
            return "zero"
        case int(n) if n > 0:
            return f"pos:{n}"
        case [x, y]:
            return f"pair:{x},{y}"
        case {"k": v}:
            return f"map:{v}"
        case _:
            # soft keyword `_` here = wildcard (binds nothing)
            return "other"


# PEP 695 type alias (soft keyword `type`) — 3.12+; fine on 3.14
type _IntOrStr = int | str


# Soft keywords as ordinary names (still legal):
match = "not soft here"  # noqa: A001 — teaching: identifier use
case = 1  # noqa: A001
type_name = type  # builtin type still reachable; `type` as soft kw only in alias form


# ============================================================================
# Sanity: kwlist completeness note for maintainers
# ============================================================================
_HARD = frozenset(keyword.kwlist)
_SOFT = frozenset(keyword.softkwlist)
assert "match" in _SOFT and "match" not in _HARD
assert "True" in _HARD and "_" in _SOFT


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 keywords.py — short educational output."""
    print("=== keywords.py probes (CPython", sys.version.split()[0], ") ===")
    print("hard count:", len(keyword.kwlist), "| soft:", keyword.softkwlist)

    # Singletons / is vs ==
    _i = 1
    print("None is None:", None is None, "| True == 1:", True == _i, "| True is 1:", True is _i)

    # Short-circuit returns operand
    print("'' or 'fallback' →", "" or "fallback")
    print("'hi' and 42 →", "hi" and 42)
    print("not [] →", not [])

    # in / is
    print("'x' in 'xyz':", "x" in "xyz", "| [] is []:", [] is [])  # False: new lists

    # if / walrus note
    print("classify(-2):", _classify(-2))
    if (n := 3) > 2:
        print("walrus n:=3 worked, n=", n)

    # loop else
    print("find even [1,3,5]:", _find_first_even([1, 3, 5]))
    print("find even [1,4,5]:", _find_first_even([1, 4, 5]))

    # defaults
    print("good defaults:", _accumulator(1), _accumulator(2))
    print("bad shared default:", _bad_default(1), _bad_default(2))
    print("lambda add:", _add(2, 3))

    # class / type
    p = _Point(1, 2)
    print("class instance:", p, "| type(p) is _Point:", type(p) is _Point)

    # global / nonlocal
    print("global bump:", _bump_global(), _bump_global())
    c = _make_counter(10)
    print("nonlocal counter:", c(), c())

    # del
    _demo_del()
    print("del demo: ok")

    # exceptions + chaining
    try:
        _div(1, 0)
    except ValueError as e:
        print("chained raise:", type(e).__name__, "| cause:", type(e.__cause__).__name__)

    # import
    print("math.pi via as:", round(_math.pi, 5), "| sqrt(9)=", _sqrt(9))

    # with
    with _temp_flag() as st:
        print("with enter on=", st["on"])
    print("with exit on=", st["on"])

    # yield / coroutine object
    print("gen list:", list(_gen()))
    co = _coro_add(2, 3)
    print("async def returns:", type(co).__name__)
    # Drive trivial coroutine without an event loop:
    try:
        co.send(None)
    except StopIteration as e:
        print("coro result via send:", e.value)

    # soft match / type alias
    print("match 0 →", _demo_match(0))
    print("match 5 →", _demo_match(5))
    print("match [1,2] →", _demo_match([1, 2]))
    print("match other →", _demo_match("z"))
    print("PEP695 alias _IntOrStr:", _IntOrStr)

    # pass / soft-as-name
    print("pass Stub:", _Stub())
    print("soft names rebound: match=", match, "case=", case)

    # quick AST note: assert compiles away under -O
    print("__debug__ (assert enabled):", __debug__)
    print("ast.parse walrus ok:", ast.parse("(x := 1)").body[0].__class__.__name__)

    print("=== probes done ===")


if __name__ == "__main__":
    _probes()
