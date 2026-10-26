#!/usr/bin/env python3
"""
=============================================================================
SHEET: itertools                       TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x iterators / recipes / C-accelerated pipelines
=============================================================================

WHAT IT IS
  - Stdlib module of *iterator building blocks* implemented mostly in C
    (Modules/itertoolsmodule.c): infinite counters, combinatorics, slicing,
    chaining, grouping, windowing.
  - Designed to compose into lazy pipelines so Python bytecode only runs
    at the edges — the inner next() loops stay in C.

INVARIANTS
  - All tools return iterators (lazy); nothing materialises until consumed
    by list/for/sum/… (except tee which buffers).
  - Infinite iterators (count, cycle, repeat forever) need a terminating
    consumer (islice, break, takewhile, …) or they hang / OOM.
  - groupby requires *consecutive* equal keys — sort first if you want
    global groups (same as Unix uniq).
  - tee(it, n) clones n iterators but must buffer items that one tee has
    consumed ahead of the others — memory ∝ lead distance.
  - Combinatoric iterators yield tuples; lengths follow math formulas
    (product/permutations can be huge — prefer islice when exploring).

DELEGATES TO (CPython)
  - Modules/itertoolsmodule.c — all core types (count, chain, groupby, …)
  - Lib/itertools.py — docs + pure-Python recipes (not imported by default)
  - Objects/iterobject.c / abstract.c — underlying iter protocol

COMPLEXITY CARD (output size k; input sizes n, …)
  - count/cycle/repeat:     O(1) per next
  - chain(*its):            O(1) per next; O(m) setup for m iterables
  - islice(it, …):          O(start) skip + O(k) yield
  - tee(it, n):             O(1) setup; buffer O(lead) memory
  - groupby:                O(n) total; one pass
  - product(p,q,…):         O(|p|*|q|*…) outputs
  - permutations(n, r):     O(P(n,r)) outputs
  - combinations(n, r):     O(C(n,r)) outputs
  - pairwise:               O(n) outputs for n-input (n-1 pairs)
  - batched(it, n):         O(n) per batch; O(len/n) batches

WHEN A BEATS B
  - product vs nested for: product for Cartesian product clarity + C loop;
    nested for when bodies are heavy (same asymptotics).
  - chain vs + on lists: chain lazy / heterogeneous; + builds a list.
  - islice vs list slice on lazy stream: islice works on any iterator;
    list slice needs a sequence (and copies).
  - groupby vs dict-of-lists: groupby one-pass consecutive; dict gathers
    all groups with random key order / full memory.
  - tee vs list(it)+multi-iter: list if you need full reuse anyway; tee
    when streams stay nearly in sync (small buffer).
  - batched vs manual chunks: batched is clear and C-backed (3.12+).

EDGE CASES
  - cycle(empty) / chain() empty → immediate StopIteration.
  - repeat(x, times=None) is infinite — always bound with islice or times=.
  - groupby: holding onto group iterators after advancing the groupby
    exhausts them — materialise `list(group)` if needed later.
  - tee: do not use the original iterator after tee'ing.
  - combinations equal to permutations when order matters? No — combos
    are sorted-index subsets; perms are orderings.
  - pairwise on 0–1 length → empty.
  - batched uneven tail: last tuple shorter unless strict=True (3.13+).

SOURCE MAP
  - Modules/itertoolsmodule.c :: itertools_count / cycle / repeat
  - Modules/itertoolsmodule.c :: itertools_chain / islice / tee
  - Modules/itertoolsmodule.c :: itertools_groupby / product
  - Modules/itertoolsmodule.c :: permutations / combinations / combinations_with_replacement
  - Modules/itertoolsmodule.c :: pairwise / batched
=============================================================================
"""

from __future__ import annotations

import itertools as it
import math
import sys

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- Infinite / unbounded producers --------------------------------------
# count(start=0, step=1): arithmetic sequence — C long / PyLong as needed.
c = it.count(10, 2)
assert next(c) == 10 and next(c) == 12 and next(c) == 14

# cycle(iterable): caches the iterable's items, then loops forever.
# First pass consumes and stores; later passes replay the cache.
cy = it.cycle("AB")
assert [next(cy) for _ in range(5)] == list("ABABA")

# repeat(object, times=None): yield the same object reference repeatedly.
assert list(it.repeat(7, 3)) == [7, 7, 7]
# Infinite form — always cut with islice:
assert list(it.islice(it.repeat(None), 4)) == [None, None, None, None]

# --- chain / islice ------------------------------------------------------
# chain stitches iterators end-to-end without building a combined list.
assert list(it.chain([1, 2], (3,), "ab")) == [1, 2, 3, "a", "b"]
# chain.from_iterable: chain over an iterable *of* iterables (flatten one level).
assert list(it.chain.from_iterable([[1, 2], [3, 4]])) == [1, 2, 3, 4]

# islice(iterable, stop) or (start, stop[, step]) — like slice but for
# iterators; does not support negative indices.
assert list(it.islice(it.count(), 5)) == [0, 1, 2, 3, 4]
assert list(it.islice(it.count(), 2, 8, 2)) == [2, 4, 6]

# --- tee -----------------------------------------------------------------
# Split one iterator into n independent ones. Internally a shared buffer
# of already-emitted values. If a pulls far ahead of b, memory grows.
a, b = it.tee(range(5), 2)
assert next(a) == 0 and next(a) == 1
assert next(b) == 0  # b still starts at the beginning (buffered)
assert list(a) == [2, 3, 4]
assert list(b) == [1, 2, 3, 4]

# --- groupby (consecutive!) ----------------------------------------------
# Groups *runs* of equal key(item). Sort first for global aggregation.
rows = [("a", 1), ("a", 2), ("b", 3), ("a", 4)]
# Without sort: three groups (a | b | a).
keys = [k for k, _g in it.groupby(rows, key=lambda r: r[0])]
assert keys == ["a", "b", "a"]
# With sort: two groups.
rows_sorted = sorted(rows, key=lambda r: r[0])
grouped = {
    k: list(g) for k, g in it.groupby(rows_sorted, key=lambda r: r[0])
}
assert list(grouped) == ["a", "b"]
assert grouped["a"] == [("a", 1), ("a", 2), ("a", 4)]
# Caveat: the group iterator is lazy and tied to the groupby advance —
# list(g) immediately if you store groups.

# --- Combinatorics -------------------------------------------------------
assert list(it.product("AB", repeat=2)) == [
    ("A", "A"),
    ("A", "B"),
    ("B", "A"),
    ("B", "B"),
]
assert list(it.product([1, 2], ["x", "y"])) == [
    (1, "x"),
    (1, "y"),
    (2, "x"),
    (2, "y"),
]

assert list(it.permutations("ABC", 2)) == [
    ("A", "B"),
    ("A", "C"),
    ("B", "A"),
    ("B", "C"),
    ("C", "A"),
    ("C", "B"),
]
assert list(it.combinations("ABC", 2)) == [
    ("A", "B"),
    ("A", "C"),
    ("B", "C"),
]
assert list(it.combinations_with_replacement("AB", 2)) == [
    ("A", "A"),
    ("A", "B"),
    ("B", "B"),
]

# Sanity vs math:
n, r = 5, 3
assert sum(1 for _ in it.permutations(range(n), r)) == math.perm(n, r)
assert sum(1 for _ in it.combinations(range(n), r)) == math.comb(n, r)

# --- pairwise / batched --------------------------------------------------
# pairwise(it): (s0,s1), (s1,s2), …  (3.10+)
assert list(it.pairwise("ABCD")) == [("A", "B"), ("B", "C"), ("C", "D")]
assert list(it.pairwise([])) == []

# batched(iterable, n): tuples of length n (last may be short). 3.12+
assert list(it.batched("ABCDEFG", 3)) == [
    ("A", "B", "C"),
    ("D", "E", "F"),
    ("G",),
]
# 3.13+: strict=True → ValueError if last batch is short
if sys.version_info >= (3, 13):
    try:
        list(it.batched("ABCD", 3, strict=True))
        raise AssertionError("strict batched must ValueError")
    except ValueError:
        pass
    assert list(it.batched("ABCD", 2, strict=True)) == [
        ("A", "B"),
        ("C", "D"),
    ]

# --- C-speed pipeline folklore -------------------------------------------
# Compose itertools so the per-element loop stays in C; pull with a single
# Python-level consumer:
pipeline = (
    x
    for x in it.islice(it.count(1), 0, 1000)
    if x % 2 == 0  # filter still Python — bottleneck if huge
)
# Better for numeric filters: push work into C where possible, or use
# a dedicated library. For combinatorics + take, prefer:
sample = list(it.islice(it.permutations(range(10), 3), 5))
assert len(sample) == 5 and sample[0] == (0, 1, 2)

# compress / filterfalse / takewhile / dropwhile — also C, useful gates:
assert list(it.compress("ABCD", [1, 0, 1, 0])) == ["A", "C"]
assert list(it.takewhile(lambda x: x < 3, [0, 1, 2, 3, 1])) == [0, 1, 2]
assert list(it.dropwhile(lambda x: x < 3, [0, 1, 2, 3, 1])) == [3, 1]
assert list(it.filterfalse(lambda x: x % 2, range(6))) == [0, 2, 4]

# starmap: like map but argument tuples are unpacked — great with product:
assert list(it.starmap(pow, [(2, 5), (3, 2)])) == [32, 9]

# accumulate: running totals (C)
assert list(it.accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    assert list(it.islice(it.count(0, 3), 4)) == [0, 3, 6, 9]
    assert list(it.chain.from_iterable(["ab", "cd"])) == list("abcd")

    xs, ys = it.tee(iter([10, 20, 30]))
    assert list(xs) == [10, 20, 30]
    assert list(ys) == [10, 20, 30]

    data = [1, 1, 2, 2, 2, 1]
    assert [k for k, g in it.groupby(data)] == [1, 2, 1]
    assert [list(g) for _, g in it.groupby(data)] == [[1, 1], [2, 2, 2], [1]]

    assert len(list(it.product([0, 1], repeat=3))) == 8
    assert list(it.pairwise([1])) == []
    assert list(it.batched(range(5), 2)) == [(0, 1), (2, 3), (4,)]

    # pipeline: first 5 odd squares via count + islice style
    odd_squares = it.islice((n * n for n in it.count() if n % 2), 5)
    assert list(odd_squares) == [1, 9, 25, 49, 81]

    assert hasattr(it, "batched")
    assert hasattr(it, "pairwise")
    print("itertools_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
