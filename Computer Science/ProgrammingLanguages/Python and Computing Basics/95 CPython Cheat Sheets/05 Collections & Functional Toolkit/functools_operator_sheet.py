#!/usr/bin/env python3
"""
=============================================================================
SHEET: functools + operator             TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 15.x higher-order / caching / dispatch / callables
=============================================================================

WHAT IT IS
  - functools: tools for working with callables — memoisation (lru_cache /
    cache), partial application, reduce, decorator bookkeeping (wraps),
    rich ordering from a subset (total_ordering), single-dispatch generics.
  - operator: function equivalents of operators / lookups — itemgetter,
    attrgetter, methodcaller — for key= and map without ad-hoc lambdas.

INVARIANTS
  - lru_cache / cache: arguments must be hashable; cache key is based on
    the call args/kwargs. Pure functions only — side effects won't re-run
    on cache hit. maxsize=None (cache) is unbounded; watch memory.
  - wraps(f): copies __name__, __doc__, __module__, __qualname__,
    __annotations__, and updates __wrapped__ so introspection sees f.
  - total_ordering: define __eq__ + ONE of __lt__/__le__/__gt__/__ge__;
    the decorator fills the rest. Equality must be consistent with order.
  - singledispatch: dispatches on the type of the *first* positional arg.
    register(type) adds overloads; Unknown types fall back to the generic.
  - partial: freezes some args/keywords; still a callable (Partial object).
  - reduce(f, xs): f must be binary; empty xs without initializer → TypeError.
  - itemgetter/attrgetter return callables; they capture indices/names at
    creation time.

DELEGATES TO (CPython)
  - Lib/functools.py           — wraps, partial, reduce, total_ordering,
    singledispatch, cache wrappers (Python)
  - Modules/_functoolsmodule.c — C accelerate partial, reduce, lru_cache
  - Lib/operator.py            — Python wrappers
  - Modules/_operator.c        — itemgetter, attrgetter, methodcaller, …

COMPLEXITY CARD
  - lru_cache hit:                 O(1) expected (dict lookup + link update)
  - lru_cache miss:                cost of f + O(1) insert; eviction O(1)
  - cache (unbounded):             like lru with maxsize=None
  - partial call:                  O(1) + f
  - reduce(f, n items):            O(n) applications of f
  - wraps:                         O(1) metadata copy
  - total_ordering methods:        each derived compare → your root compare
  - singledispatch:                O(1)–MRO walk to find registered impl
  - itemgetter(i)(row):            O(1) index; multi-index → tuple

WHEN A BEATS B
  - cache / lru_cache vs manual dict: decorator handles hashing, hits,
    stats (lru), and eviction — prefer for pure recursive / hot functions.
  - lru_cache(maxsize=N) vs cache(): bounded when memory matters; cache()
    when the domain is finite and small (e.g. enum-like keys).
  - partial vs lambda: partial preserves a real callable object and is
    picklable in more cases; lambda is lighter for one-off key=.
  - reduce vs for-loop: loop wins for readability; reduce when folding
    with an associative op (especially with operator.xxx).
  - wraps vs bare decorator: always wraps — else help()/__name__ break.
  - total_ordering vs writing all six: less boilerplate; tiny overhead.
  - singledispatch vs if/elif isinstance: scales better across modules
    (others can register); isinstance chain wins for 2–3 local types.
  - itemgetter vs lambda r: r[0]: itemgetter faster in tight sorts (C).

EDGE CASES
  - lru_cache on methods: caches per (self, args) — self is part of key;
    can pin instances alive. Prefer @cache on static/module functions, or
    use cached_property for per-instance.
  - Unhashable args (list/dict) → TypeError at call time.
  - typed=True: 3 and 3.0 are different cache keys.
  - singledispatchmethod (3.8+): for methods; dispatch still on first arg
    after self/cls — see docs for register patterns.
  - reduce without initializer on empty → TypeError; with initializer OK.
  - total_ordering: if __eq__ is NotImplemented for foreign types, derived
    ops may misbehave — keep comparisons tight.
  - operator.attrgetter("a.b"): nested dotted lookup.

SOURCE MAP
  - Modules/_functoolsmodule.c :: lru_cache_wrapper, partial_new, reduce
  - Lib/functools.py           :: wraps, update_wrapper, total_ordering
  - Lib/functools.py           :: singledispatch, singledispatchmethod
  - Modules/_operator.c        :: itemgetter, attrgetter, methodcaller
  - Lib/operator.py            :: re-exports + pure helpers
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

from __future__ import annotations

import functools
import operator
from functools import (
    cache,
    lru_cache,
    partial,
    reduce,
    singledispatch,
    total_ordering,
    wraps,
)
from operator import attrgetter, itemgetter, methodcaller

# =============================================================================
# lru_cache / cache — memoisation
# =============================================================================
# lru_cache(maxsize=128): bounded LRU. maxsize=None → unbounded (same as
# functools.cache since 3.9). typed=True separates int/float equal values.


@lru_cache(maxsize=32)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


assert fib(20) == 6765
info = fib.cache_info()  # CacheInfo(hits, misses, maxsize, currsize)
assert info.hits + info.misses >= 1
fib.cache_clear()
assert fib.cache_info().currsize == 0


@cache
def square(x: int) -> int:
    return x * x


assert square(7) == 49 and square(7) == 49  # second call is a hit


@lru_cache(maxsize=4, typed=True)
def ident(x):  # type: ignore[no-untyped-def]
    return x


ident(3)
ident(3.0)  # different key when typed=True
assert ident.cache_info().currsize == 2

# Unhashable → TypeError
try:

    @cache
    def bad(xs: list[int]) -> int:
        return sum(xs)

    bad([1, 2])  # type: ignore[arg-type]
except TypeError:
    pass

# =============================================================================
# partial — freeze arguments
# =============================================================================
def power(base: float, exp: float) -> float:
    return base**exp


square_p = partial(power, exp=2)
cube = partial(power, exp=3)
assert square_p(5) == 25 and cube(2) == 8
# partial object exposes .func / .args / .keywords
assert square_p.func is power and square_p.keywords == {"exp": 2}

# Useful with map / APIs that need a one-arg callable:
assert list(map(partial(operator.mul, 10), [1, 2, 3])) == [10, 20, 30]

# =============================================================================
# reduce — fold a binary function over an iterable
# =============================================================================
assert reduce(operator.add, [1, 2, 3, 4]) == 10
assert reduce(operator.mul, [1, 2, 3, 4], 1) == 24
# empty without initializer fails:
try:
    reduce(operator.add, [])
except TypeError:
    pass
assert reduce(operator.add, [], 0) == 0

# =============================================================================
# wraps — preserve metadata through decorators
# =============================================================================
def trace(fn):  # type: ignore[no-untyped-def]
    @wraps(fn)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        return fn(*args, **kwargs)

    return wrapper


@trace
def greet(name: str) -> str:
    """Say hi."""
    return f"hi {name}"


assert greet.__name__ == "greet"
assert greet.__doc__ == "Say hi."
assert greet.__wrapped__ is greet.__wrapped__  # update_wrapper link
# Without wraps, __name__ would be "wrapper" and help() would lie.

# =============================================================================
# total_ordering — derive rich comparisons
# =============================================================================
@total_ordering
class Version:
    def __init__(self, major: int, minor: int) -> None:
        self.major = major
        self.minor = minor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) < (other.major, other.minor)


assert Version(1, 2) < Version(1, 10)
assert Version(2, 0) >= Version(1, 9)
assert Version(1, 0) == Version(1, 0)

# =============================================================================
# singledispatch — overload on first argument type
# =============================================================================
@singledispatch
def dump(obj: object) -> str:
    return f"repr:{obj!r}"


@dump.register
def _(obj: int) -> str:
    return f"int:{obj}"


@dump.register(list)
def _(obj: list) -> str:  # type: ignore[type-arg]
    return "list:" + ",".join(dump(x) for x in obj)


assert dump(3) == "int:3"
assert dump("x") == "repr:'x'"
assert dump([1, 2]) == "list:int:1,int:2"
# Extensibility: other modules can dump.register(TheirType)(fn)

# =============================================================================
# operator — itemgetter / attrgetter / methodcaller
# =============================================================================
rows = [("c", 3), ("a", 1), ("b", 2)]
# Sort by column 1 — itemgetter is a C callable; faster than lambda in hot paths
assert sorted(rows, key=itemgetter(1)) == [("a", 1), ("b", 2), ("c", 3)]
# Multi-index → tuple key
assert itemgetter(1, 0)(("c", 3)) == (3, "c")


class Person:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def greet(self, bang: str = "!") -> str:
        return self.name + bang


people = [Person("zoe", 40), Person("ann", 30)]
assert sorted(people, key=attrgetter("age"))[0].name == "ann"
# Nested: attrgetter("addr.city") if obj.addr.city exists

assert methodcaller("greet")(people[0]) == "zoe!"
assert methodcaller("greet", "!!!")(people[0]) == "zoe!!!"
# methodcaller("encode", "utf-8")("ab") → b'ab' — same idea for str methods

# Other high-traffic operator callables (for reduce / map):
assert list(map(operator.neg, [1, 2])) == [-1, -2]
assert operator.add(2, 3) == 5
assert operator.itemgetter(0)([10, 20]) == 10  # same as itemgetter import


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""

    @lru_cache(maxsize=8)
    def fact(n: int) -> int:
        return 1 if n < 2 else n * fact(n - 1)

    assert fact(10) == 3_628_800
    assert fact(10) == 3_628_800  # second top-level call → cache hit
    assert fact.cache_info().hits >= 1
    fact.cache_clear()

    @cache
    def twice(x: int) -> int:
        return x * 2

    assert twice(4) == 8

    p = partial(operator.sub, 10)  # 10 - x
    assert p(3) == 7
    assert reduce(operator.mul, range(1, 6)) == 120

    def deco(f):  # type: ignore[no-untyped-def]
        @wraps(f)
        def w(*a, **k):  # type: ignore[no-untyped-def]
            return f(*a, **k)

        return w

    @deco
    def f():
        """doc"""
        return 1

    assert f.__name__ == "f" and f.__doc__ == "doc" and f() == 1

    @total_ordering
    class N:
        def __init__(self, v: int) -> None:
            self.v = v

        def __eq__(self, o: object) -> bool:
            return isinstance(o, N) and self.v == o.v

        def __lt__(self, o: object) -> bool:
            return isinstance(o, N) and self.v < o.v

    assert N(1) <= N(2) and N(3) > N(2)

    @singledispatch
    def tag(x: object) -> str:
        return "other"

    @tag.register(str)
    def _(x: str) -> str:
        return "str"

    assert tag(1) == "other" and tag("a") == "str"

    data = [{"k": 2}, {"k": 1}]
    assert sorted(data, key=itemgetter("k"))[0]["k"] == 1
    assert attrgetter("v")(N(9)) == 9
    assert methodcaller("strip")("  z  ") == "z"

    print("functools_operator_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
