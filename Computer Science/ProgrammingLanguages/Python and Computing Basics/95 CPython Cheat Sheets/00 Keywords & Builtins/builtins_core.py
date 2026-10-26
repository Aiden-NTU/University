#!/usr/bin/env python3
"""
=============================================================================
SHEET: builtins_core                    TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 00 Keywords & Builtins / iteration / introspection / I-O
=============================================================================

WHAT IT IS
  - The names always available without import (the builtins module, exposed as
    `__builtins__` / `builtins`). Implemented mostly in Python/bltinmodule.c
    with helpers in Objects/*.c. This sheet covers the high-traffic core:
    sizing/iteration adapters, aggregates, open, typing probes, identity/hash,
    string/repr, descriptors (property/staticmethod/classmethod), super/vars/dir,
    numeric helpers, and the eval/exec/compile danger zone.

INVARIANTS
  - Builtins can be shadowed by assignment in a module/local scope; the real
    object remains at `builtins.len` etc.
  - `hash(x)` for str/bytes is process-salted by default (PYTHONHASHSEED) —
    equal strings hash equal *within* one process; across processes, order of
    set/dict iteration is not stable unless seed is fixed.
  - `id(obj)` is the object’s identity (CPython: typically `(uintptr_t)obj`).
    After an object dies, that address MAY be reused — never stash ids as
    durable keys across lifetimes.
  - `zip` stops at the shortest iterable (unless zip(..., strict=True) → error).
  - `sorted` returns a NEW list; timsort is stable.
  - `open` text mode returns str; binary returns bytes — never mix encodings.

DELEGATES TO (CPython)
  - Python/bltinmodule.c     :: builtin_len, builtin_iter, builtin_next, …
  - Objects/iterobject.c / calliter / map / filter / zip / enum / reversed
  - Objects/listobject.c     :: list_sort (timsort)
  - Objects/rangeobject.c    :: range
  - Objects/sliceobject.c    :: slice
  - Objects/typeobject.c     :: type_call, isinstance/issubclass helpers
  - Objects/object.c         :: PyObject_Hash, PyObject_Repr, id via pointer
  - Objects/descrobject.c    :: property, classmethod, staticmethod
  - Objects/methodobject.c / funcobject.c :: descriptors + super
  - Python/ceval.c           :: CALL, FOR_ITER driving iterators
  - Lib/_pyio.py / Modules/_io :: open implementation stack

COMPLEXITY CARD (amortised unless noted)
  - len(seq)           O(1) for list/tuple/dict/set/str/bytes/range/…
  - iter(x)            O(1) to build iterator; then per-step cost of type
  - next(it)           O(1) amortised for most iterators (+ body work)
  - map/filter         O(1) lazy wrapper; full consume O(n · f)
  - zip(*its)          O(1) wrapper; consume O(min lengths)
  - enumerate          O(1) wrapper
  - reversed(seq)      O(1) if __reversed__ or random-access + len
  - sorted(it)         O(n log n) time, O(n) extra space (timsort)
  - any/all            O(k) early-exit where k ≤ n
  - sum                O(n); floats use compensated ideas in some paths
  - min/max            O(n)
  - open               dominated by syscall / buffering, not Python loops
  - isinstance         typically O(1)–O(MRO depth) style checks
  - hash               O(size) for str/bytes; O(1) for interned small ints
  - id / hash(int)     O(1)
  - eval/exec/compile  parse + compile cost; then exec like running code

WHEN A BEATS B
  - `map(f, xs)` / generator beats `[f(x) for x in xs]` when you only need
    to stream results (no random access, no multiple passes) — saves memory.
  - listcomp beats map when you need a list anyway AND a complex expression
    (readability); map wins for a named function + lazy pipeline.
  - `any(cond for x in xs)` beats building a filtered list then checking.
  - `zip` parallel walk beats index loops when lengths should track.
  - `sorted(xs)` beats repeated list.sort copies when you must keep original.
  - `isinstance(x, (A, B))` beats chained type(x) is … (and respects ABC).
  - `with open(...)` beats bare open without close.

EDGE CASES
  - zip exhaustion: longer iterables silently truncated (use strict=True).
  - map/filter are single-pass iterators — list(map(...)) to reify.
  - sorted key= is computed once per element (decorate-sort-undecorate).
  - open text: locale/UTF-8 encoding; binary: no encoding= allowed.
  - hash randomization → DoS resistance; set/dict order not cross-process stable.
  - id reuse after death: `id(object()) == id(object())` often True!
  - getattr(obj, "x", default) vs obj.x — default suppresses AttributeError.
  - eval/exec: arbitrary code execution — never on untrusted input.
  - round uses banker’s rounding (half to even) for ties in binary floats.
  - pow(base, exp, mod) is efficient modular exponentiation.

SOURCE MAP
  - Python/bltinmodule.c           :: builtin_* entries
  - Objects/listsort.txt + listobject.c :: timsort
  - Objects/dictobject.c / setobject.c  :: hash tables
  - Objects/unicodeobject.c        :: hash siphash, unicode ops
  - Modules/_io/*.c / Lib/io.py    :: open
  - Objects/typeobject.c           :: PyObject_IsInstance, IsSubclass
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import builtins
import io
import os
import sys
import tempfile
from collections.abc import Iterable
from typing import Any

## len(obj) — size protocol
# Prefer obj.__len__(); must return >= 0. O(1) for built-in containers.
# Missing __len__ → TypeError. (Also used by truth-value testing.)


## iter(obj) / iter(callable, sentinel)
# Protocol: __iter__ → iterator; else if __getitem__ sequence protocol.
# Two-arg form: call callable until it returns sentinel (file-readline idiom).
# Returns an iterator; iterators themselves return self from __iter__.


## next(iterator, default=missing)
# Calls __next__; StopIteration if exhausted — default suppresses that.


## map(func, *iterables) — lazy
# Stops when the SHORTEST iterable ends (like zip). Prefer map when `func`
# is a named/callable and you stream; listcomp when you need a list + expr.
def _map_demo(xs: Iterable[int]) -> list[int]:
    return list(map(lambda x: x * x, xs))


## filter(func | None, iterable) — lazy
# If func is None, keeps truthy elements. Else keeps where func(x) true.


## zip(*iterables, strict=False)
# Tuples until shortest ends. strict=True → ValueError if lengths differ.
# Tip: unzip with zip(*rows) (consumes); empty rows → empty.


## enumerate(iterable, start=0)
# Yields (index, item). O(1) wrapper — no materialization.


## reversed(seq)
# Needs __reversed__ OR (__len__ + __getitem__). Not for general iterators
# (no going backwards without storage — use reversed(list(it)) if you must).


## sorted(iterable, *, key=None, reverse=False) → list
# Timsort (Objects/listobject.c): stable, O(n log n) worst, exploits runs.
# key= computed once per element. For huge streams prefer heapq / DB sort.


## any(iterable) / all(iterable)
# Short-circuit: any on first truthy; all on first falsy. Empty: any→False,
# all→True (vacuous truth). Ideal over materializing filters.


## sum(iterable, start=0)
# Adds start + items. For strings use ''.join (sum refuses str start in 3.x
# spirit — actually sum of str raises TypeError). Use math.fsum for precise
# float sums when needed.


## min / max (*args | iterable, *, key=None, default=...)
# default= only with single iterable form (3.4+); avoids ValueError on empty.


## open(file, mode='r', buffering=-1, encoding=None, errors=None,
##      newline=None, closefd=True, opener=None)
# Text ('t', default): str in/out, encoding required on some platforms —
# pass encoding="utf-8" explicitly. Binary ('b'): bytes; encoding must be None.
# Always prefer `with open(...) as f:` so __exit__ closes the FD.
# buffering: -1 default; 0 only binary; 1 line-buffer text; >=2 byte buffer.


## type(obj) → type; type(name, bases, dict) → new type
# Same object as `object.__class__` machinery; metaclass path for 3-arg form.
# Prefer isinstance for checks that should honor subclasses/ABCs.


## isinstance(obj, class_or_tuple) / issubclass(cls, class_or_tuple)
# Walks MRO / ABC registry. Tuple means OR. issubclass requires a type
# (or virtual subclass registrant), not an instance.


## hasattr / getattr / setattr / callable
# hasattr(obj, name) ≈ try getattr except AttributeError → False
# getattr(obj, name[, default])
# setattr(obj, name, value) → obj.name = value (may hit data descriptors)
# callable(x) → True if __call__ in type(x)'s slots/MRO sense


## hash(obj) / id(obj)
# hash: __hash__; mutable containers are unhashable by default.
# Randomized for str/bytes (siphash with per-process seed).
# id: identity; CPython address — REUSED after deallocation.


## repr / str / ascii
# repr: ideally unambiguous / eval-able for many builtins.
# str: human-readable; falls back to repr.
# ascii: like repr but escapes non-ASCII to \x/\u/\U.


## slice(start=None, stop=None, step=None)
# slice objects are what `a[1:10:2]` builds. Use slice in __getitem__.
# indices(length) → concrete (start, stop, step) normalized to len.


## range — brief pointer
# Immutable sequence of ints; O(1) len/contains for ordinary ranges.
# Deep sheet belongs with sequences; here: range(n) is NOT a list.


## object — ultimate base
# New-style root; provides default __eq__ (identity), __hash__, __str__/__repr__.
# Instances of bare object() are attribute-slotless unless subclassed with
# __dict__/__slots__.


## property / staticmethod / classmethod — descriptors
# property: managed attribute via fget/fset/fdel (Objects/descrobject.c).
# staticmethod: strips descriptor binding — f(x) with no implicit self/cls.
# classmethod: binds first arg to the class (or subclass that looked it up).
class _Temp:
    _c = 0

    def __init__(self, c: float) -> None:
        self._c = c

    @property
    def f(self) -> float:
        return self._c * 9 / 5 + 32

    @staticmethod
    def zero() -> "_Temp":
        return _Temp(0.0)

    @classmethod
    def from_f(cls, f: float) -> "_Temp":
        return cls((f - 32) * 5 / 9)


## super() — cooperative multiple inheritance
# Zero-arg super() in a method uses the defining class + self/cls from
# the cell created by the compiler. Lookups continue along the MRO.


## vars(obj=None) / dir(obj=None) / help (brief)
# vars(): locals() if no arg; else obj.__dict__ (TypeError if none).
# dir(): names for interactive use — not a precise API contract.
# help(): pager over docstrings / pydoc — interactive, skip in batch probes.


## abs / round / divmod / pow
# abs(x) → __abs__
# round(x[, ndigits]) — banker’s rounding on .5 ties for floats
# divmod(a, b) → (a // b, a % b) coordinated
# pow(x, y[, mod]) → x**y or modular pow


## bin / hex / oct / chr / ord / format
# bin/hex/oct: int → '0b…' / '0x…' / '0o…' strings
# chr(i) ↔ ord(c) for Unicode code points
# format(value, format_spec) → type(value).__format__


## input / print
# input([prompt]) reads a line from sys.stdin (str, no trailing \\n).
# print(*args, sep=' ', end='\\n', file=sys.stdout, flush=False)
# Teaching probes avoid interactive input().


## eval / exec / compile — DANGER
# eval(expr)  → evaluate expression → value  (restricted to expressions)
# exec(code)  → execute statements → None
# compile(source, filename, mode) → code object; mode 'eval'|'exec'|'single'
# Security: equivalent to running attacker code in your process. Never feed
# untrusted strings. Prefer ast.literal_eval for data literals only.
# Also: can mutate globals/locals you pass — footprint is large.


## __import__(name, globals=None, locals=None, fromlist=(), level=0)
# Low-level hook the `import` statement uses. Prefer importlib.import_module
# for dynamic imports; __import__ return value semantics depend on fromlist.


# --- small helpers used by probes -----------------------------------------

def _consume(it: Iterable[Any], n: int) -> list[Any]:
    out: list[Any] = []
    for i, x in enumerate(it):
        if i >= n:
            break
        out.append(x)
    return out


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 builtins_core.py — short educational output."""
    print("=== builtins_core.py probes (CPython", sys.version.split()[0], ") ===")
    print("builtins is module:", type(builtins).__name__, "| len is", builtins.len)

    # len / iter / next
    xs = [10, 20, 30]
    print("len:", len(xs))
    it = iter(xs)
    print("next:", next(it), next(it), next(it, "EOF"), next(it, "EOF"))

    # map vs listcomp (lazy)
    m = map(str, range(5))
    print("map type:", type(m).__name__, "| first two:", _consume(m, 2))
    print("map exhausted remainder:", list(m))  # already partially consumed

    # filter / zip / enumerate / reversed
    print("filter evens:", list(filter(lambda n: n % 2 == 0, range(6))))
    print("zip short:", list(zip([1, 2, 3], "ab")))
    try:
        list(zip([1, 2], [1], strict=True))
    except ValueError as e:
        print("zip strict:", type(e).__name__)
    print("enumerate:", list(enumerate("ab", start=1)))
    print("reversed:", list(reversed(xs)))

    # sorted timsort + stability
    rows = [("b", 2), ("a", 2), ("a", 1)]
    print("sorted by key1 stable:", sorted(rows, key=lambda r: r[1]))

    # any / all / sum / min / max
    print("any>2:", any(x > 2 for x in xs), "| all>0:", all(x > 0 for x in xs))
    print("sum:", sum(xs), "| min/max:", min(xs), max(xs))
    print("min empty default:", min([], default=-1))

    # open text vs binary
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "t.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("π\n")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        with open(path, "rb") as f:
            raw = f.read()
        print("open text:", repr(text), "| binary:", raw)

    # type / isinstance / issubclass
    print("type(0):", type(0).__name__, "| isinstance True:", isinstance(True, int))
    print("issubclass(bool, int):", issubclass(bool, int))

    # hasattr / getattr / setattr / callable
    class Box:
        pass

    b = Box()
    print("hasattr x:", hasattr(b, "x"))
    setattr(b, "x", 7)
    print("getattr x:", getattr(b, "x"), "| missing:", getattr(b, "y", None))
    print("callable(len):", callable(len), "| callable(3):", callable(3))

    # hash / id reuse
    s = "hash-seed-demo"
    print("hash(str) stable in-process:", hash(s) == hash("hash-seed-demo"))
    print("id reuse often True:", id(object()) == id(object()))

    # repr / str / ascii
    print("repr/str/ascii:", repr("café"), str("café"), ascii("café"))

    # slice / range pointer
    sl = slice(1, None, 2)
    print("slice on range:", list(range(8)[sl]), "| range len:", len(range(10**9)))

    # object / property / static / class / super
    t = _Temp.from_f(32.0)
    print("property F from C≈0:", round(t.f, 2), "| static zero:", _Temp.zero()._c)

    class A:
        def who(self) -> str:
            return "A"

    class B(A):
        def who(self) -> str:
            return "B+" + super().who()

    print("super MRO:", B().who(), B.__mro__)

    # vars / dir (brief)
    print("vars(t) keys:", sorted(vars(t).keys()))
    print("dir(_Temp) has from_f:", "from_f" in dir(_Temp))
    # help(_Temp)  # interactive — skipped

    # numeric / format / bases
    print("abs/round/divmod/pow:", abs(-3), round(2.5), divmod(7, 3), pow(2, 10, 1000))
    print("bin/hex/oct:", bin(6), hex(255), oct(8))
    print("chr/ord:", chr(65), ord("A"))
    print("format:", format(3.14159, ".2f"))

    # print (and StringIO stand-in for input-less demo)
    buf = io.StringIO()
    print("hello", "world", sep="-", file=buf)
    print("print capture:", buf.getvalue().rstrip())

    # eval / exec / compile (safe literals only here)
    code = compile("1 + 2", "<probe>", "eval")
    print("compile+eval:", eval(code))
    ns: dict[str, Any] = {}
    exec("a = 40\nb = 2", ns)
    print("exec ns:", ns.get("a") + ns.get("b"))
    print("DANGER note: never eval/exec untrusted input")

    # __import__
    m = __import__("math")
    print("__import__('math').sqrt(9):", m.sqrt(9))

    print("=== probes done ===")


if __name__ == "__main__":
    _probes()
