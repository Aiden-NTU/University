#!/usr/bin/env python3
"""
=============================================================================
SHEET: list                            TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x sequences / 08.x allocation
=============================================================================

WHAT IT IS
  - Mutable dynamic array of PyObject* pointers (not an unboxed value array).
  - Contiguous C array: ob_item[0 .. ob_size-1] are live refs; allocated
    capacity (allocated) may be larger — *overallocation* amortises append.

INVARIANTS
  - len(L) == ob_size; indices [0, len) valid; negative index i → i+len.
  - Elements are borrowed/owned refs; store INCREFs, clear DECREFs.
  - list.sort is in-place, stable (Timsort); key= is decorated decorate-
    sort-undecorate style internally.
  - Slicing L[a:b] allocates a *new* list and copies pointers (shallow).
  - "+" between lists allocates a new list; extend / += mutate in place.

DELEGATES TO (CPython)
  - Objects/listobject.c — list_resize, list_append, ins1, list_ass_slice,
    list_sort_impl (Timsort), list_extend, …
  - Include/listobject.h — PyListObject { ob_item, allocated }

COMPLEXITY CARD (amortised where noted)
  - L[i] / L[i] = x:           O(1)
  - append / pop():            O(1) amortised
  - pop(0) / insert(0, x):     O(n)  (memmove all pointers)
  - insert(i, x) / del L[i]:   O(n - i)
  - extend(iterable):          O(k) plus possible resize
  - L + M:                     O(len(L)+len(M)) new list
  - L[a:b]:                    O(b-a) copy
  - sort:                      O(n log n) typical; highly optimised Timsort
  - x in L:                    O(n) equality scan (no hashing)

WHEN A BEATS B
  - list vs deque for stack (append/pop end): both fine; list is leaner.
  - deque vs list for queue (left pop): deque O(1); list pop(0) O(n).
  - list vs array.array: list for PyObjects; array for packed C scalars.
  - append loop vs repeated L = L + [x]: append/extend win; + rebuilds.
  - listcomp vs map+list: listcomp usually clearer; similar speed ballpark.
  - bisect on sorted list vs set: set for pure membership; list+bisect when
    you need order statistics on a sorted sequence.

EDGE CASES
  - Overallocation formula is heuristic (grows ~pattern like 0,4,8,16,…
    historically; exact curve can change — do not hardcode sizes).
  - Multiplying [[]] * n aliases the SAME inner list n times.
  - sort(key=...) must not mutate the list; cmp removed since Python 3.
  - Concurrent mutation from another thread without locks is undefined
    (free-threaded 3.14 builds still need discipline around shared lists).
  - Slice assignment L[a:b] = iterable can grow/shrink; length need not match.

SOURCE MAP
  - Objects/listobject.c :: list_resize / list_grow_shared
  - Objects/listobject.c :: PyList_Append / ins1 / list_ass_slice
  - Objects/listobject.c :: list_sort_impl / Objects/listsort.doc
  - Objects/listobject.c :: list_extend / list_inplace_concat
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

# Construction: list() empty; list(iterable) walks and appends; literal [].
L = [10, 20, 30]
# Memory picture: a C array of pointers → PyLongObjects for 10,20,30.
# Capacity may be > 3 already so the next few appends avoid realloc.

# Indexing is pointer arithmetic — O(1); no hashing.
assert L[0] == 10 and L[-1] == 30

# --- Overallocation / amortised append -----------------------------------
# list_resize: when ob_size+1 > allocated, allocate a larger array, copy
# pointers, free old buffer. Growth is *geometric-ish*, so the cost of
# copying is amortised to O(1) per append across a long append sequence.
# Shrinks may happen when much capacity is wasted (implementation detail).
for i in range(100):
    L.append(i)  # hot path: often just STORE + INCREF + size++

# pop() from the end: O(1) — decrement size, DECREF, no memmove.
end = L.pop()
assert end == 99

# pop(0) / insert(0, x): must slide every pointer — O(n). Classic footgun
# when people use list as a queue. Prefer collections.deque for both ends.
head = [1, 2, 3, 4]
head.pop(0)  # memmove left; O(n)
head.insert(0, 0)  # memmove right; O(n)

# --- extend vs + ---------------------------------------------------------
a = [1, 2]
b = [3, 4]
c = a + b  # NEW list; a and b unchanged
assert c == [1, 2, 3, 4] and a == [1, 2]
a.extend(b)  # mutate a; may resize once for len(b)
assert a == [1, 2, 3, 4]
a += [5]  # in-place for lists (like extend), NOT realloc-identity guaranteed
# but typically same object:
a_id = id(a)
a += [6]
assert id(a) == a_id

# Anti-pattern: building with + in a loop → quadratic (new list each time).
# Use append/extend or a listcomp / join for strings.

# --- Slicing copies (shallow) --------------------------------------------
base = [[1], [2], [3]]
sl = base[0:2]  # new list object; SAME inner list identities
assert sl[0] is base[0]
sl[0].append(99)
assert base[0] == [1, 99]
# Slice assignment:
nums = [0, 1, 2, 3, 4]
nums[1:3] = [8, 9, 10]  # can change length
assert nums == [0, 8, 9, 10, 3, 4]
nums[1:4] = []  # delete slice
assert nums == [0, 3, 4]

# --- sort: Timsort (stable) ----------------------------------------------
# Adaptive mergesort: finds natural runs, merges with galloping, etc.
# Stability: equal keys keep original relative order.
pairs = [("b", 2), ("a", 1), ("b", 1)]
pairs.sort(key=lambda p: p[0])  # in-place
assert pairs == [("a", 1), ("b", 2), ("b", 1)]  # both "b" keep order
# sorted(iterable) returns a NEW list; original untouched.
assert sorted([3, 1, 2], reverse=True) == [3, 2, 1]

# --- list comprehensions -------------------------------------------------
# Syntactic sugar for building a list in a tight C-ish loop (LIST_APPEND).
squares = [x * x for x in range(5) if x % 2 == 0]
assert squares == [0, 4, 16]
# Nested / dependent comps are just nested loops — still produce one list.

# --- Aliasing traps ------------------------------------------------------
row = [[0] * 3] * 3  # three references to ONE inner list
row[0][0] = 1
assert row[1][0] == 1  # shared
# Correct grid:
grid = [[0] * 3 for _ in range(3)]
grid[0][0] = 1
assert grid[1][0] == 0

# Membership: linear equality scan — fine for tiny lists; use a set for
# repeated membership tests on large collections.
assert 3 in [1, 2, 3]


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    xs: list[int] = []
    for i in range(1000):
        xs.append(i)
    assert len(xs) == 1000 and xs[-1] == 999
    assert xs.pop() == 999 and len(xs) == 999
    chunk = xs[10:20]
    assert chunk == list(range(10, 20)) and chunk is not xs
    xs.extend(range(3))
    assert xs[-3:] == [0, 1, 2]
    ys = [3, 1, 2, 1]
    ys.sort()
    assert ys == [1, 1, 2, 3]
    assert [x for x in range(4)] == [0, 1, 2, 3]
    # + vs extend identity
    p = [1]
    q = p + [2]
    assert p == [1] and q == [1, 2]
    p.extend([2])
    assert p == [1, 2]
    # slice length change
    z = [0, 1, 2, 3]
    z[1:3] = [9]
    assert z == [0, 9, 3]
    print("list.py: all probes passed")


if __name__ == "__main__":
    _probes()
