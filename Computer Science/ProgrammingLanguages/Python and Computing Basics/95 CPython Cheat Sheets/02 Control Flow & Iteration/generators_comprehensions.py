#!/usr/bin/env python3
"""
=============================================================================
SHEET: generators & comprehensions     TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 15.x frames / 11.x iterators / PEP 342 / PEP 380
=============================================================================

WHAT IT IS
  - A *generator function* (def with yield / yield from) returns a
    generator iterator when called — it does not run the body yet.
  - Each next() resumes the suspended frame until the next yield (or
    return / StopIteration). Local state lives in the frame between calls.
  - *Generator expressions* ((x for x in …)) are anonymous one-shot
    generators; *list/set/dict comprehensions* eagerly build containers.
  - yield from subgen delegates iteration (and send/throw/close) to
    another iterable/generator (PEP 380).

INVARIANTS
  - Calling gen_fn() only allocates the generator object; body starts on
    first next() / send(None) / for-loop.
  - yield expr pauses; the value of the yield expression inside the
    generator is whatever was sent via send(v), or None on next().
  - return x in a generator raises StopIteration(x); for-loops ignore x;
    yield from captures it as the value of the yield from expression.
  - PEP 479: a bare raise StopIteration inside a generator becomes
    RuntimeError — use return to end cleanly.
  - Generators are one-shot; exhaust once. No rewind without tee/re-call.
  - Comprehension loop variables are isolated in their own scope (3.x);
    they do not leak into the enclosing function.

DELEGATES TO (CPython)
  - Objects/genobject.c    — PyGenObject, gen_send_ex, gen_throw, gen_close
  - Python/compile.c       — MAKE_FUNCTION + generator flag; yield opcodes
  - Python/ceval.c         — YIELD_VALUE / YIELD_FROM / RETURN_VALUE
  - Objects/itertoolsmodule.c / bltin — consumers; listcomp uses LIST_APPEND
  - Include/cpython/genobject.h — frame pointer, gi_exhausted, etc.

COMPLEXITY CARD
  - gen_fn() call:                 O(1) allocate generator
  - next(gen) / yield round-trip:  O(1)+ body until next yield
  - yield from n items:            O(n) delegated next() calls
  - listcomp n items:              O(n) time + O(n) peak memory
  - genexp n items (consumed):     O(n) time + O(1) extra peak (pipeline)
  - genexp fully listed:           same memory as listcomp at the end
  - send/throw/close:              O(1)+ resume / unwind

WHEN A BEATS B
  - genexp vs listcomp: genexp when one pass / fused pipeline / large n;
    listcomp when reuse, len(), indexing, or multiple passes.
  - generator function vs genexp: function when multi-statement body,
    yield from, send(), or reusable logic; genexp for tiny expressions.
  - yield from vs manual for+yield: yield from is clearer and correctly
    forwards send/throw/close / return value.
  - generator vs list for intermediate filters: generator chains defer
    work and cap memory; materialise at the boundary that needs random
    access (list/dict/set).

EDGE CASES
  - Generators are not thread-safe; do not next() the same gen from two
    threads.
  - Throwing GeneratorExit (via close()) should not be swallowed silently
    unless you re-raise or return; yielding after close → RuntimeError.
  - Genexp has *late binding* for the outermost iterable only in a subtle
    way: the iterable in (x for x in coll) is evaluated immediately;
    filters/expressions run lazily. Nested for clauses are also lazy.
  - Listcomp inside a generator still builds a full list when that
    statement runs — nesting does not magically stay lazy.
  - gi_frame / cr_frame introspection: frames may be None when exhausted
    (implementation detail — prefer gi_suspended / inspection APIs).
  - async def + yield → asynchronous generator (different type); not
    interchangeable with sync generators.

SOURCE MAP
  - Objects/genobject.c :: gen_new_with_qualname / gen_send_ex
  - Objects/genobject.c :: gen_throw / gen_close / gen_iternext
  - Python/ceval.c :: YIELD_VALUE / YIELD_FROM
  - PEP 342 (send/throw/close) / PEP 380 (yield from) / PEP 479
=============================================================================
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- Generator function: call ≠ run --------------------------------------


def countdown(n: int) -> Iterator[int]:
    """Yield n .. 1. Frame suspended at each yield."""
    while n > 0:
        yield n  # pause; produce n to the caller
        n -= 1
    # implicit return None → StopIteration


g = countdown(3)
# Body has not run yet — only a PyGenObject exists.
assert next(g) == 3
assert next(g) == 2
assert next(g) == 1
try:
    next(g)
except StopIteration as e:
    assert e.value is None

# for-loops are the usual consumer:
assert list(countdown(3)) == [3, 2, 1]

# --- yield expression value + send ---------------------------------------
# Inside the generator, `x = yield out` does two jobs:
#   1) yield `out` to the caller
#   2) when resumed, the yield expr evaluates to the sent value (or None)


def accumulator() -> Iterator[int]:
    total = 0
    while True:
        # First next()/send(None) runs up to this yield, yields total,
        # then waits. Subsequent send(v) injects v as the yield's value.
        got = yield total
        if got is None:
            continue
        total += int(got)


acc = accumulator()
assert next(acc) == 0  # prime: must start with next()/send(None)
assert acc.send(5) == 5
assert acc.send(3) == 8
acc.close()  # raises GeneratorExit into the frame; ends generator

# --- throw / close -------------------------------------------------------


def guarded() -> Iterator[str]:
    try:
        yield "start"
        yield "middle"
    except ValueError as e:
        yield f"caught:{e}"
    finally:
        # finally runs on close(), throw that unwinds, or normal end
        pass


gt = guarded()
assert next(gt) == "start"
assert gt.throw(ValueError("boom")) == "caught:boom"  # 3.12+: single-arg form
# after handling, generator may continue or end depending on body

gc = guarded()
assert next(gc) == "start"
gc.close()
try:
    next(gc)
except StopIteration:
    pass

# --- yield from (PEP 380) ------------------------------------------------
# yield from iterable:
#   - yields every item from iterable
#   - if iterable is a generator, forwards send/throw/close
#   - result of `yield from` expression = StopIteration.value of subgen


def sub() -> Iterator[int]:
    yield 1
    yield 2
    return 99  # becomes StopIteration(99)


def parent() -> Iterator[int]:
    result = yield from sub()
    yield result  # 99


assert list(parent()) == [1, 2, 99]

# yield from on a plain iterable (list) just walks it — no return value
# other than None.


def flatten_once(xs: list[Any]) -> Iterator[Any]:
    for x in xs:
        if isinstance(x, list):
            yield from x
        else:
            yield x


assert list(flatten_once([1, [2, 3], 4])) == [1, 2, 3, 4]

# --- Generator expression vs listcomp vs set/dict comps ------------------
# Genexp: lazy, one-shot, parentheses (or as a sole function argument).
# Listcomp: eager list. Set/dict comps: eager hashed containers.

N = 6
squares_list = [x * x for x in range(N) if x % 2 == 0]
squares_gen = (x * x for x in range(N) if x % 2 == 0)
assert squares_list == [0, 4, 16]
assert list(squares_gen) == [0, 4, 16]
assert list(squares_gen) == []  # exhausted

# Scope isolation (3.x): comprehension loop vars do not leak.


def scope_demo() -> int:
    xs = [i for i in range(3)]
    assert xs == [0, 1, 2]
    try:
        i  # type: ignore[name-defined]  # noqa: F821
        raise AssertionError("comp loop var leaked")
    except NameError:
        pass
    return len(xs)


assert scope_demo() == 3

# Dict / set comps:
d = {c: ord(c) for c in "ab"}
s = {x % 3 for x in range(10)}
assert d == {"a": 97, "b": 98}
assert s == {0, 1, 2}

# --- Memory tradeoff sketch ----------------------------------------------
# Pipeline (lazy): no intermediate lists
sum_filtered = sum(x * x for x in range(1000) if x % 2 == 0)
# Equivalent eager (three materialisations if written naively):
#   sum([x*x for x in [x for x in range(1000) if x % 2 == 0]])
assert sum_filtered == sum(x * x for x in range(0, 1000, 2))

# When you need len / reuse / indexing — materialise once at the edge:
materialised = list(x * x for x in range(10))  # genexp → list boundary
assert materialised[3] == 9

# --- Frame suspension intuition ------------------------------------------
# Between yields the generator holds:
#   - instruction pointer (where to resume)
#   - locals / stack of the frame
#   - references that keep objects alive until the gen is GC'd / exhausted
# So a generator that yields from a huge local list keeps that list alive
# for the generator's lifetime — close() early if you must release.


def holds_big() -> Iterator[int]:
    big = list(range(10_000))
    yield len(big)
    yield big[0]


hb = holds_big()
assert next(hb) == 10_000
hb.close()  # drop frame promptly if you won't continue

# --- PEP 479 reminder ----------------------------------------------------


def bad_end() -> Iterator[int]:
    yield 1
    # raise StopIteration  # would become RuntimeError inside generator
    return  # correct way to end


assert list(bad_end()) == [1]


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""

    def gfn() -> Iterator[int]:
        yield from range(3)
        return 7

    def outer() -> Iterator[int]:
        v = yield from gfn()
        yield int(v)

    assert list(outer()) == [0, 1, 2, 7]

    # send protocol
    def echo() -> Iterator[Any]:
        x = yield "ready"
        while True:
            x = yield x

    e = echo()
    assert next(e) == "ready"
    assert e.send("hi") == "hi"
    assert e.send(3) == 3
    e.close()

    # comps
    assert [x for x in range(5)] == list(x for x in range(5))
    assert {x for x in "aab"} == {"a", "b"}
    assert {k: k * 2 for k in range(3)} == {0: 0, 1: 2, 2: 4}

    # throw
    def catcher() -> Iterator[str]:
        try:
            yield "a"
        except KeyError:
            yield "handled"

    c = catcher()
    assert next(c) == "a"
    assert c.throw(KeyError()) == "handled"

    # genexp outermost iterable evaluated immediately
    src = [1, 2, 3]
    ge = (x for x in src)
    src.append(4)
    assert list(ge) == [1, 2, 3, 4]  # same list object, late elements visible

    print("generators_comprehensions.py: all probes passed")


if __name__ == "__main__":
    _probes()
