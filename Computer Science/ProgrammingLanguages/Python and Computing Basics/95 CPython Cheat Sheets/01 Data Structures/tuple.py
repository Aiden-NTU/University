#!/usr/bin/env python3
"""
=============================================================================
SHEET: tuple                           TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x sequences / 07.x hashing
=============================================================================

WHAT IT IS
  - Immutable ordered sequence of PyObject* pointers.
  - Fixed length after creation; elements cannot be reassigned (but if an
    element is mutable, *that* object can still mutate in place).
  - Hashable IFF every element is hashable → usable as dict key / set item.

INVARIANTS
  - t[i] = x  is illegal (TypeError); no resize, no append.
  - Identity: small-tuple freelist may recycle empty / small tuple *structs*
    (implementation optimisation) — do not rely on id() stability for () .
  - Singleton: (x,) needs the comma; (x) is just x in parentheses.
  - Packing / unpacking matches length exactly (or uses *rest).
  - Concatenation t + u allocates a new tuple; looping with += can go
    quadratic (new tuple each time) — prefer list then tuple(...).

DELEGATES TO (CPython)
  - Objects/tupleobject.c — tuple_new, tupleresize (rare), tuplehash,
    tupleconcat, free_list for small sizes
  - Include/tupleobject.h — PyTupleObject

COMPLEXITY CARD
  - t[i] / len(t):             O(1)
  - x in t:                    O(n)
  - t + u / t * k:             O(n) allocate+copy pointers
  - hash(t):                   O(n) once (result cached on the tuple object
    when hashable; unhashable → TypeError and may leave it unhashable)
  - tuple(iterable):           O(n)

WHEN A BEATS B
  - tuple vs list: tuple for fixed records, dict keys, safer sharing;
    list when you need growth / sort in place.
  - tuple vs frozenset: tuple preserves order / duplicates / positions;
    frozenset is unordered unique membership.
  - tuple vs namedtuple/dataclass: tuple for tiny anonymous records;
    named fields when readability matters.
  - Building: use list appends then tuple(xs) instead of repeated += on
    tuples inside a hot loop.

EDGE CASES
  - ([1],) is a valid tuple but unhashable because the list is unhashable.
  - t += (x,) rebinds the name t to a *new* tuple if t was a local/variable;
    for a closure/cell or __dict__ slot the statement still allocates new.
  - Single-element literal without comma is NOT a tuple: (42) is int 42.
  - Empty tuple () is a singleton in practice (one immortal empty tuple).
  - tuple.sort does not exist — use sorted(t) → list.

SOURCE MAP
  - Objects/tupleobject.c :: PyTuple_New / tuple_new
  - Objects/tupleobject.c :: tuplehash / tuplecontains
  - Objects/tupleobject.c :: tupleconcat / tuplerepeat
  - Objects/tupleobject.c :: free_list / PyTuple_ClearFreeList (debug/lifecycle)
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

# Literals and constructors
empty = ()  # empty tuple — typically one shared object
pair = (1, 2)
also = 1, 2  # packing: comma makes the tuple; parens often optional
assert pair == also

# THE singleton comma — most common beginner footgun:
singleton = (42,)
not_tuple = (42)
assert isinstance(singleton, tuple) and isinstance(not_tuple, int)

# Immutability of the *container*:
t = (1, 2, 3)
try:
    t[0] = 99  # type: ignore[index]
except TypeError:
    pass

# But mutable *elements* can still change — tuple only freezes the binding:
nested = ([1], [2])
nested[0].append(99)
assert nested == ([1, 99], [2])
# Hence hash(nested) fails:
try:
    hash(nested)
except TypeError:
    pass

# Hashable tuples are fine as keys:
key = (1, "a", frozenset({9}))
table = {key: "ok"}
assert table[(1, "a", frozenset({9}))] == "ok"
# tuplehash mixes item hashes with a length-dependent process; result is
# cached on the tuple when successful so re-hashing is O(1).

# --- Freelist folklore (CPython) -----------------------------------------
# Small tuples (historically lengths 1..20-ish) may come from a free_list
# of recycled PyTupleObjects to avoid allocator chatter. Empty tuple is
# often a true singleton. This is an optimisation — write code as if every
# PyTuple_New allocated fresh, but know why id(()) stays stable.

# --- Packing / unpacking -------------------------------------------------
a, b, c = (10, 20, 30)  # exact length
assert (a, b, c) == (10, 20, 30)
head, *mid, tail = (1, 2, 3, 4, 5)
assert head == 1 and mid == [2, 3, 4] and tail == 5  # *rest → list
# Swap idiom (bytecode uses ROT / unpack):
x, y = 1, 2
x, y = y, x
assert (x, y) == (2, 1)
# Mismatch length → ValueError:
try:
    p, q = (1, 2, 3)
except ValueError:
    pass

# --- Concatenation and the quadratic trap --------------------------------
# t + u allocates len(t)+len(u) and copies both pointer arrays.
u = (1, 2) + (3, 4)
assert u == (1, 2, 3, 4)
# Anti-pattern:
#   t = ()
#   for x in data:
#       t += (x,)     # each step copies growing prefix → O(n²)
# Fix: build a list (amortised append), then tuple(list) once.
data = range(100)
t_fast = tuple(data)  # single allocation path from iterable
assert len(t_fast) == 100

# Repetition:
assert (0,) * 3 == (0, 0, 0)
# Caution: ([]) * 3 aliases one list three times — same as list gotcha.
aliased = ([],) * 3
aliased[0].append(1)
assert aliased[1] == [1]

# Methods: count / index only (no append/sort/reverse mutators).
seq = (1, 2, 2, 3)
assert seq.count(2) == 2 and seq.index(3) == 3

# Slicing returns a new tuple (still shallow regarding elements):
assert seq[1:3] == (2, 2)


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    empty_a = ()
    empty_b = ()
    assert empty_a is empty_b  # empty tuple is a shared singleton in CPython
    s = (7,)
    assert isinstance(s, tuple) and s[0] == 7
    assert not isinstance((7), tuple)
    h = (1, 2, 3)
    assert hash(h) == hash((1, 2, 3))
    d = {h: True}
    assert d[(1, 2, 3)] is True
    try:
        hash(([1],))
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
    xs = (1, 2, 3)
    try:
        xs[0] = 0  # type: ignore[index]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
    a, *rest = (9, 8, 7, 6)
    assert a == 9 and rest == [8, 7, 6]
    # quadratic-avoidance sanity: tuple from list
    buf: list[int] = []
    for i in range(200):
        buf.append(i)
    assert tuple(buf) == tuple(range(200))
    assert (1, 2) + (3,) == (1, 2, 3)
    print("tuple.py: all probes passed")


if __name__ == "__main__":
    _probes()
