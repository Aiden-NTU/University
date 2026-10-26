#!/usr/bin/env python3
"""
=============================================================================
SHEET: iteration protocol              TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x iterators / 15.x bytecode (FOR_ITER)
=============================================================================

WHAT IT IS
  - The *iterator protocol*: objects that produce a stream of values one at
    a time via __iter__ / __next__ (or the C slots tp_iter / tp_iternext).
  - for-loops, comprehensions, unpacking, and many builtins (list, sum,
    zip, …) are thin consumers of that protocol — not special-cased per type.
  - An *iterable* returns an iterator from iter(x); an *iterator* returns
    itself from iter(it) and advances with next(it).

INVARIANTS
  - iter(x) calls type(x).__iter__ (or falls back to the old sequence
    protocol: __getitem__ with 0,1,2,… until IndexError — rare today).
  - next(it) returns the next item OR raises StopIteration to signal end.
    Exhaustion is *sticky* for most iterators: further next() keep raising.
  - for x in coll:  ≡  it = iter(coll); while True: try: x = next(it)
    except StopIteration: break  — plus FOR_ITER opcode fast path.
  - StopIteration.args[0] can carry a "return value" for generators; plain
    for-loops discard it. Do not raise StopIteration to mean "business
    logic miss" inside ordinary functions — it can leak into callers oddly
    (PEP 479: in generators it becomes RuntimeError).
  - Iterators are generally *one-shot* and *lazy*; iterables may be
    re-iterable (list) or not (file, generator).

DELEGATES TO (CPython)
  - Objects/abstract.c     — PyObject_GetIter, PyIter_Next
  - Python/bltinmodule.c   — builtin_iter, builtin_next, builtin_zip, …
  - Python/ceval.c         — FOR_ITER / GET_ITER bytecode handling
  - Objects/iterobject.c   — seqiter, calliter, …
  - Objects/enumobject.c   — enumerate
  - Objects/listobject.c   — list_iter / listiter_next (dense C loop)
  - Objects/rangeobject.c  — range_iterator (arithmetic, no materialisation)

COMPLEXITY CARD (amortised unless noted)
  - iter(list/tuple/dict/set):     O(1)  (allocate tiny iterator object)
  - next(it) on list/tuple/range:  O(1)
  - for x in n-seq:                O(n)  total; per-step cheap in C
  - list(iterable):                O(n)  materialise
  - enumerate(it):                 O(1) wrap; O(1) per next
  - zip(*its):                     O(1) wrap; O(k) per next for k streams
  - reversed(seq):                 O(1) if seq has __reversed__ or is
                                   sized+indexable; else TypeError
  - custom Python __next__:        O(1)+ interpreter overhead per item
                                   (much slower than listiter in C)

WHEN A BEATS B
  - for + C iterator (list, range) vs manual index loop: for wins clarity
    and usually speed (FOR_ITER specialised).
  - enumerate vs range(len): enumerate when you need (i, item); avoid
    range(len) when the object is not a sequence.
  - zip vs index lockstep: zip is clearer; zip(strict=True) catches length
    bugs (3.10+).
  - reversed(list) vs list[::-1]: reversed is O(1) wrapper + O(n) walk;
    slice copy is O(n) memory up front.
  - generator / custom iterator vs materialised list: generator when one
    pass + memory; list when reuse / random access.

EDGE CASES
  - Exhausted iterator stays exhausted — tee / list / itertools if reuse.
  - Mutating a list while iterating it: CPython may not crash but is
    undefined for "safe semantics"; can skip/repeat. Prefer iterate a copy
    or build a new list.
  - zip stops at *shortest* by default (silent truncation); use strict=.
  - iter(callable, sentinel) — second form: calls callable until sentinel.
  - Raising StopIteration inside a generator body is a RuntimeError
    (PEP 479); return ends the generator cleanly.
  - __iter__ that returns self without __next__ → TypeError on for-loop.
  - Asynchronous cousins (aiter/anext) are a different protocol.

SOURCE MAP
  - Objects/abstract.c :: PyObject_GetIter / PyIter_Next
  - Python/ceval.c :: FOR_ITER handling
  - Objects/iterobject.c :: seqiter_new / calliter_new
  - Objects/enumobject.c :: enum_new / enum_next
  - Objects/listobject.c :: list_iter / listiter_next
  - Python/bltinmodule.c :: builtin_zip / zip_next
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- Core: iter / next ---------------------------------------------------
# iter(obj) → iterator. For containers this usually allocates a lightweight
# C struct holding (container ref, index). The container is NOT copied.
L = [10, 20, 30]
it = iter(L)
assert it is not L
assert iter(it) is it  # iterators are iterable and return themselves

assert next(it) == 10
assert next(it) == 20
assert next(it) == 30
try:
    next(it)  # exhausted → StopIteration
except StopIteration as stop:
    assert stop.value is None  # .value is args[0] or None

# next(it, default) swallows StopIteration and returns default — useful in
# manual loops without try/except.
it2 = iter([1])
assert next(it2, "done") == 1
assert next(it2, "done") == "done"

# --- for-loop desugaring -------------------------------------------------
#   for x in L:
#       body
# is conceptually:
#   _it = iter(L)
#   while True:
#       try:
#           x = next(_it)
#       except StopIteration:
#           break
#       body
# CPython emits GET_ITER + FOR_ITER; FOR_ITER jumps to the break target
# when the iterator signals end (C-level, not a Python except each time).
seen: list[int] = []
for x in L:
    seen.append(x)
assert seen == [10, 20, 30]

# --- Custom iterable / iterator ------------------------------------------
class Countdown:
    """Iterable that yields n, n-1, …, 1. Fresh iterator each iter()."""

    def __init__(self, n: int) -> None:
        self.n = n

    def __iter__(self) -> "CountdownIterator":
        return CountdownIterator(self.n)


class CountdownIterator:
    def __init__(self, n: int) -> None:
        self._cur = n

    def __iter__(self) -> "CountdownIterator":
        return self

    def __next__(self) -> int:
        if self._cur <= 0:
            raise StopIteration
        v = self._cur
        self._cur -= 1
        return v


assert list(Countdown(3)) == [3, 2, 1]
assert list(Countdown(3)) == [3, 2, 1]  # re-iterable: new iterator each time

# One-shot anti-pattern: returning self from __iter__ on the same object
# that holds mutable cursor state makes the *iterable* one-shot (like a
# generator or file). Fine when intentional; surprising for containers.


class Oneshot:
    def __init__(self, data: list[int]) -> None:
        self._data = data
        self._i = 0

    def __iter__(self) -> "Oneshot":
        return self

    def __next__(self) -> int:
        if self._i >= len(self._data):
            raise StopIteration
        v = self._data[self._i]
        self._i += 1
        return v


once = Oneshot([1, 2])
assert list(once) == [1, 2]
assert list(once) == []  # already exhausted

# --- enumerate -----------------------------------------------------------
# enumerate(iterable, start=0) wraps an iterator; each next() does
#   return (count, next(inner)); count += 1
# Cost: tiny Python/C object + integer bump per step — negligible vs body.
pairs = list(enumerate(["a", "b"], start=1))
assert pairs == [(1, "a"), (2, "b")]

# Prefer enumerate over range(len(...)) when you need the element; range(len)
# fails on non-sized iterables and is less clear.

# --- zip -----------------------------------------------------------------
# zip(a, b, …) holds one iterator per argument. Each next():
#   build tuple(next(it) for it in iterators)  — stops when ANY raises
#   StopIteration (shortest-stream semantics).
assert list(zip([1, 2, 3], "ab")) == [(1, "a"), (2, "b")]  # 3 dropped

# zip(..., strict=True) raises ValueError if lengths differ — use when
# unequal length is a bug, not a feature (3.10+).
try:
    list(zip([1, 2], [1], strict=True))
except ValueError:
    pass

# Cost: per-step allocates a result tuple (unless elided by specialised
# consumers). Still usually cheaper/clearer than hand-rolled index loops.
# zip is lazy — zip(range(10**9), range(10**9)) does not allocate 1e9 pairs.

# --- reversed ------------------------------------------------------------
# Fast path: obj.__reversed__() if present (list, range, …).
# Else: if sized and implement __getitem__, build a reverse index iterator.
# Otherwise TypeError (plain generators / most iterators have no length).
assert list(reversed([1, 2, 3])) == [3, 2, 1]
assert list(reversed(range(3))) == [2, 1, 0]
try:
    reversed(iter([1, 2]))  # naked iterator: not reversible
except TypeError:
    pass
# list[::-1] copies; reversed(list) does not copy the list.

# --- iter(callable, sentinel) --------------------------------------------
# Second form: repeatedly call callable() until it returns sentinel.
# Classic file-read loop:
#   for block in iter(lambda: f.read(4096), b""): …
from functools import partial

nums = iter([1, 2, 3, -1, 99])
# toy: pull until -1
pulled: list[int] = []
for v in iter(lambda: next(nums), -1):
    pulled.append(v)
assert pulled == [1, 2, 3]

# --- Sequence protocol fallback ------------------------------------------
# Objects without __iter__ but with __getitem__ can still be iterated:
# CPython walks index 0,1,2,… until IndexError. Prefer real __iter__.


class OldStyleSeq:
    def __init__(self, data: list[int]) -> None:
        self._data = data

    def __getitem__(self, i: int) -> int:
        return self._data[i]  # raises IndexError when i out of range


assert list(OldStyleSeq([7, 8])) == [7, 8]

# --- Mutation during iteration (footgun) ---------------------------------
# listiter holds an index into the live list. Insert/delete shifts elements
# under the cursor — skipped or repeated items are easy. Safe patterns:
# iterate list(L), or build results in a new list, or iterate reversed
# when deleting by index carefully.
scary = [1, 2, 3, 4]
for x in scary:
    if x % 2 == 0:
        scary.remove(x)  # mutates under iterator — do not rely on result
# Prefer:
scary = [1, 2, 3, 4]
scary = [x for x in scary if x % 2]  # [1, 3]

# --- Unpacking is iteration ----------------------------------------------
a, b, c = [1, 2, 3]  # drives iterator to exhaustion; length must match
a, *rest = range(4)
assert a == 0 and rest == [1, 2, 3]


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    data = [10, 20, 30, 40]
    it = iter(data)
    assert next(it) == 10
    assert list(it) == [20, 30, 40]
    assert list(it) == []  # sticky exhaustion

    assert list(enumerate("ab", 5)) == [(5, "a"), (6, "b")]
    assert list(zip("abc", [1, 2], strict=False)) == [("a", 1), ("b", 2)]
    try:
        list(zip("ab", "a", strict=True))
        raise AssertionError("strict zip must ValueError")
    except ValueError:
        pass

    assert list(reversed(range(3))) == [2, 1, 0]
    assert list(Countdown(4)) == [4, 3, 2, 1]

    # for-loop and list() agree
    acc: list[int] = []
    for v in Countdown(3):
        acc.append(v)
    assert acc == list(Countdown(3))

    # iter(callable, sentinel)
    from itertools import count

    c = count(0)
    assert list(iter(lambda: next(c), 3)) == [0, 1, 2]

    # custom vs builtin cost is not asserted — correctness only
    assert sum(x for x in range(100)) == 4950
    print("iteration_protocol.py: all probes passed")


if __name__ == "__main__":
    _probes()
