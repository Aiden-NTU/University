#!/usr/bin/env python3
"""
=============================================================================
SHEET: set / frozenset                 TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 07.x hash tables / 11.x containers
=============================================================================

WHAT IT IS
  - set: mutable, unordered (insertion order is NOT an API guarantee for
    sets — unlike dict), deduplicating collection of *hashable* objects.
  - frozenset: immutable sibling; hashable when its elements are hashable,
    so it can itself be a dict key or a set element.
  - Backed by an open-addressed hash table of (hash, PyObject*) entries —
    not a separate chaining bucket list.

INVARIANTS
  - Every live entry satisfies: entry.hash == hash(entry.key) (cached).
  - Membership: locate by hash & mask, then probe; accept only when
    cached hash matches AND key == candidate (rich compare). Hash alone
    never decides equality.
  - Table size is a power of two; mask = used_slots_capacity - 1.
  - Deletion leaves a *dummy* (tombstone) so probe chains stay intact.
  - Resize / rebuild when fill (used + dummies) crosses load thresholds.
  - Elements MUST implement __hash__ and __eq__ consistently
    (a == b ⇒ hash(a) == hash(b)); mutables that define __hash__ = None
    (list, dict, set, …) are rejected at insert time.

DELEGATES TO (CPython)
  - Objects/setobject.c  — PySetObject, set_lookkey, set_add_key,
    set_discard_key, set_table_resize, set_merge, …
  - Include/setobject.h  — struct layout (fill, used, mask, table, …)
  - Objects/dictobject.c shares folklore (open addressing) but dicts use
    a *compact* keys+values design; sets keep the classic entry table.

COMPLEXITY CARD (average / amortised unless noted)
  - x in s / add / discard / remove:  O(1) expected; O(n) worst (pathological hashes)
  - pop / clear:                      O(1) / O(n)
  - copy / frozenset(s):              O(n)
  - union / | :                       O(len(a)+len(b))
  - intersection / & :                O(min(len(a),len(b))) typical
  - difference / - :                  O(len(a)) typical when b is set-like
  - symmetric_difference / ^ :        O(len(a)+len(b))
  - issubset / <= / issuperset / >=:  O(len(self)) typical
  - isdisjoint:                       O(min) early-exit

WHEN A BEATS B
  - set vs list for membership: set wins O(1) vs O(n); list wins if you need
    order + duplicates + indexing.
  - set vs dict: use set when you only need keys; dict when values matter.
  - frozenset vs tuple: frozenset for unordered unique membership as a key;
    tuple when order / position matter.
  - discard vs remove: discard when absence is normal; remove when absence
    is a bug (raises KeyError).

EDGE CASES
  - Unhashable insert → TypeError immediately (no silent skip).
  - Mutating an object already in a set (if you cheated __hash__) corrupts
    the table: lookup may miss the entry forever.
  - Dummy density: many deletes without rebuild → longer probes; CPython
    rebuilds/resizes when fill is high relative to used.
  - set.pop() is arbitrary (implementation-dependent slot walk), not LIFO.
  - Shallow copy: copy() / set(s) reuses element identities; nested mutables
    (if somehow present via a custom hashable wrapper) are shared.
  - NaN: float('nan') != float('nan') but hash equal → one NaN can live in
    a set; membership uses eq so a *different* NaN object may still "hit"
    via hash+eq quirks — treat NaN carefully.
  - Folklore fix: index is NOT forever "hash & (size-1)" only — after a
    collision CPython uses *perturb* probing (see walkthrough).

SOURCE MAP
  - Objects/setobject.c :: set_lookkey / set_add_entry / set_insert_key
  - Objects/setobject.c :: set_table_resize / set_clear_internal
  - Objects/setobject.c :: set_difference* / set_intersection* / set_union
  - Objects/setobject.c :: set_symmetric_difference* / set_isdisjoint
  - Objects/setobject.c :: frozenset_new / frozenset_hash
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

# Construction: set() empty; set(iterable) consumes any iterable, hashing
# each element once and inserting. Literal {1, 2, 3} is the common path
# (BUILD_SET opcode). Empty literal {} is a *dict*, not a set — use set().
s = {1, 2, 3, 3}  # duplicate 3 collapsed; no warning
# Under the hood (setobject.c): allocate table with power-of-two size,
# for each key compute hash = PyObject_Hash(key), then probe for a free
# or equal slot. used counts live keys; fill counts live + dummies.

# --- Hashing folklore (correct the "hash & (size-1)" one-liner) -----------
#
# Initial index:
#     i = hash & mask          # mask = table_size - 1  (size is 2**k)
#
# That alone would clump keys whose hashes share low bits. After a miss,
# CPython sets do NOT just walk i+1. They use *perturb* open addressing
# (same family as classic dict probing before compact dicts):
#
#     perturb = hash
#     while True:
#         i = (i * 5 + 1 + perturb) & mask
#         perturb >>= PERTURB_SHIFT   # PERTURB_SHIFT == 5
#         # inspect table[i] …
#
# Why: mixes high hash bits into later probes so collision chains spread.
# So: first probe is cheap (hash & mask); *subsequent* probes are perturb.
# Linear "i = (i + 1) & mask" is a teaching simplification, not CPython.

# Membership: hash then eq — never hash alone.
assert 2 in s  # lookkey: follow probes; compare cached hash, then ==
assert 9 not in s

# Unhashables fail at the boundary — list has __hash__ = None.
try:
    s.add([1, 2])  # type: ignore[arg-type]
except TypeError as exc:
    _ = exc  # "unhashable type: 'list'"

# Why: without a stable hash, the table cannot choose a slot that will
# still be valid if the object mutates. Consistency rule:
#     a == b  ⇒  hash(a) == hash(b)
# If you define __eq__ you almost always need __hash__, or set
# __hash__ = None to opt out (make instances unhashable).

# --- Mutation API --------------------------------------------------------
s.add(4)  # no-op if already present (hash+eq hit); else insert / maybe resize
s.discard(99)  # absent → silent; preferred when "maybe gone" is fine
s.remove(4)  # absent → KeyError; preferred when absence is a logic error
# remove/discard both: hash → probe → match → mark slot DUMMY (tombstone).
# Dummy keeps the probe chain searchable for keys inserted after the
# deleted one that collided through this slot. Skipping dummies on lookup
# is mandatory; treating dummy as empty would truncate the chain.

got = s.pop()  # remove and return *some* element; arbitrary, not stack order
_ = got
s.clear()  # drop all; may free / reset table
s.update([1, 2, 3, 4, 5])  # in-place union from iterable
s |= {5, 6}  # same idea; right-hand should be a set for |, iterable for |=
# 3.9+: s |= iterable works for update; s | other requires both sets.

# --- Algebra (new set) vs _update (in-place) ------------------------------
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
# difference: in a but not b
assert a.difference(b) == {1, 2} == a - b
# intersection
assert a.intersection(b) == {3, 4} == a & b
# union
assert a.union(b) == {1, 2, 3, 4, 5, 6} == a | b
# symmetric_difference: in exactly one of the two
assert a.symmetric_difference(b) == {1, 2, 5, 6} == a ^ b

# In-place variants mutate the left operand (and return None).
c = a.copy()  # shallow: new table, same element objects
c.difference_update(b)  # c -= b
assert c == {1, 2}
c = a.copy()
c.intersection_update(b)  # c &= b
assert c == {3, 4}
c = a.copy()
c.update(b)  # c |= b   (union_update naming is just update)
assert c == {1, 2, 3, 4, 5, 6}
c = a.copy()
c.symmetric_difference_update(b)  # c ^= b
assert c == {1, 2, 5, 6}

# Multiple iterables allowed on many methods:
assert {1, 2, 3}.difference([1], (2,)) == {3}

# --- Predicates ----------------------------------------------------------
assert {1, 2}.issubset({1, 2, 3})  # also: <=  (proper: <)
assert {1, 2, 3}.issuperset({1, 2})  # also: >= (proper: >)
assert {1, 2}.isdisjoint({3, 4})  # no common elements; early exit
# Optimisation folklore: issubset may compare lengths first when other is
# set-like; then probes each element of the smaller side.

# --- frozenset: immutable + hashable -------------------------------------
fs = frozenset({1, 2, 3})
assert hash(fs) == hash(frozenset([3, 2, 1]))  # order-independent content hash
# frozenset hash mixes element hashes (see frozenset_hash); usable as key:
nested = {fs: "ok"}
assert nested[frozenset({3, 1, 2})] == "ok"
# set itself is unhashable (mutable):
try:
    hash({1, 2})
except TypeError:
    pass

# Shallow copy: element identities are shared. For frozenset, CPython may
# return *self* from copy() / frozenset(fs) because the object is immutable
# (safe sharing). set.copy() always allocates a new set object.
fs2 = fs.copy()
assert fs2 == fs  # often `fs2 is fs` for frozenset — allowed
mutable = {1, 2}
twin = mutable.copy()
assert twin == mutable and twin is not mutable

# --- Collisions (teaching sketch) ----------------------------------------
# Two unequal objects can share hash() % something. Table stores BOTH the
# cached hash and the key pointer. Lookup:
#   1) empty slot → miss
#   2) dummy → keep probing
#   3) hash mismatch → keep probing (cheap reject)
#   4) hash match → PyObject_RichCompareBool(key, candidate, Py_EQ)
# Only step 4 can accept. That is why "membership is hash then eq".

# --- Resize intuition ----------------------------------------------------
# Growing: when fill approaches ~2/3 (implementation thresholds), allocate
# a larger power-of-two table and *reinsert* live keys (dummies dropped).
# Shrinking / rebuild: heavy delete load can trigger a resize that cleans
# dummies even if used count is moderate — restores short probe runs.


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    x: set[int] = set()
    for i in range(100):
        x.add(i)
    assert len(x) == 100
    assert all(i in x for i in range(100))
    x.difference_update(range(0, 100, 2))
    assert x == set(range(1, 100, 2))
    f = frozenset(x)
    assert {f: True}[frozenset(x)] is True
    # algebra identities
    u, v = {1, 2, 3}, {3, 4}
    assert u | v == u.union(v)
    assert u & v == u.intersection(v)
    assert u - v == u.difference(v)
    assert u ^ v == u.symmetric_difference(v)
    assert u.isdisjoint({9})
    # remove vs discard
    u2 = {1}
    u2.discard(9)
    try:
        u2.remove(9)
        raise AssertionError("remove must KeyError")
    except KeyError:
        pass
    # copy is shallow / independent table
    base = {1, 2}
    twin = base.copy()
    twin.add(3)
    assert 3 not in base
    print("set_frozenset.py: all probes passed")


if __name__ == "__main__":
    _probes()
