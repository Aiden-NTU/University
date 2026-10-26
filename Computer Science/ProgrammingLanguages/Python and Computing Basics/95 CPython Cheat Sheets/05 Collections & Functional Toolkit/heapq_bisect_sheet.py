#!/usr/bin/env python3
"""
=============================================================================
SHEET: heapq + bisect                   TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x heaps / binary search / sorted arrays
=============================================================================

WHAT IT IS
  - heapq: binary *min*-heap algorithms over a plain list. The heap is the
    list itself (invariant on indices); there is no separate Heap type.
  - bisect: binary search + sorted insert into a sorted *list* (array).
    Keeps order with O(log n) search + O(n) memmove for insert.

INVARIANTS
  HEAP (0-based, min-heap):
    - For every i > 0:  heap[i] >= heap[(i-1)//2]   (parent ≤ children)
    - Children of i: 2*i+1 and 2*i+2
    - heap[0] is always the minimum (if non-empty)
    - Equal keys: no stable tie-break beyond comparison order — use
      (priority, tie_breaker, item) triples when you need FIFO among ties.
  BISECT (list must already be sorted ascending w.r.t. the key used):
    - bisect_left(a, x)  → leftmost insertion index to keep sorted order
      (all a[i] < x for i < lo; all a[j] >= x for j >= lo)  [key=None case]
    - bisect_right(a, x) → rightmost insertion index
      (all a[i] <= x left; all a[j] > x right)
    - insort_* = bisect_* then a.insert(i, x)  → O(n) due to list shift

DELEGATES TO (CPython)
  - Lib/heapq.py              — pure Python + optional C accel
  - Modules/_heapqmodule.c    — heappush/heappop/heapify C implementations
  - Lib/bisect.py             — pure Python + C accel
  - Modules/_bisectmodule.c   — bisect_left/right, insort_*
  - Objects/listobject.c      — list.insert memmove for insort cost

COMPLEXITY CARD
  - heappush / heappop:              O(log n)
  - heapify(list):                  O(n)   (Floyd bottom-up — not n log n)
  - heapreplace / heappushpop:      O(log n)
  - nlargest(k) / nsmallest(k):     O(n log k) typical (heap of size k)
  - merge(*sorted_iters):           O(N log k) for k streams, N total out
  - bisect_left / bisect_right:     O(log n) comparisons
  - insort_left / insort_right:     O(n)     (search log n + insert n)
  - list.sort then walk:            O(n log n) once, then O(1)/O(log n)

WHEN A BEATS B
  - heapq vs sorted list for repeated "take min": heap — O(log n) vs
    O(n) remove from front of sorted list (or O(n) re-sort).
  - heapq.nlargest(k) vs sorted(xs)[-k:]: nlargest wins for k ≪ n;
    full sort wins when k ~ n or you need the whole order.
  - list + bisect vs sortedcontainers / tree / blist: for small–medium n
    (thousands–low hundreds of thousands) and occasional inserts, a plain
    sorted list often beats a balanced tree in CPython because of cache
    locality + lower constants; trees win when n is huge AND inserts are
    frequent (O(log n) vs O(n) shift). Prefer measure for your n.
  - bisect vs linear scan for "where would x go": bisect for sorted data.
  - heapify vs n × heappush: heapify O(n) beats O(n log n) pushes.

EDGE CASES
  - Max-heap: negate numeric keys, or store (-priority, …).
  - heappop on empty → IndexError.
  - Mutating heap[i] in place without sifting breaks the invariant —
    use heapq helpers only (or re-heapify).
  - Tuple compare: (1, "b") < (1, "c"); mixed types may TypeError in 3.x.
  - bisect on unsorted list → wrong index, silent logic bug.
  - key= on bisect (3.10+): key is applied to *elements*, not to x —
    pass a precomputed x key or use a wrapper; read docs carefully.
  - insort does not unique-ify — duplicates allowed (left vs right picks
    which side of equal runs).

SOURCE MAP
  - Modules/_heapqmodule.c :: siftup / siftdown / heappush / heappop
  - Modules/_heapqmodule.c :: heapify / heapreplace / heappushpop
  - Lib/heapq.py           :: nlargest, nsmallest, merge, _siftdown_max
  - Modules/_bisectmodule.c :: bisect_left, bisect_right, insort_*
  - Lib/bisect.py          :: key= wrappers (3.10+)
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

import bisect
import heapq
from typing import Any

# =============================================================================
# heapq — min-heap over list
# =============================================================================
# The "heap" IS the list. After heapify / push / pop, index 0 is the min.
# Parent(i) = (i-1)//2; left = 2*i+1; right = 2*i+2.

h: list[int] = [5, 1, 9, 3, 7]
heapq.heapify(h)  # O(n) in-place; builds heap invariant bottom-up
assert h[0] == 1  # minimum at root; rest is heap-ordered, NOT fully sorted
# Teaching check: every parent ≤ children
for i in range(1, len(h)):
    assert h[(i - 1) // 2] <= h[i]

heapq.heappush(h, 0)   # sift up O(log n)
assert h[0] == 0
assert heapq.heappop(h) == 0  # sift down O(log n); returns old root
assert h[0] == 1

# heappushpop: push then pop — more efficient than push+pop when new item
# is larger than current min (often stays at root briefly then pops).
h2 = [1, 3, 5]
heapq.heapify(h2)
assert heapq.heappushpop(h2, 4) == 1  # pushed 4, popped 1
assert h2[0] == 3

# heapreplace: pop then push — always removes current min, then adds;
# empty heap → IndexError. Useful for "replace the best with a candidate".
h3 = [2, 4, 6]
heapq.heapify(h3)
assert heapq.heapreplace(h3, 1) == 2
assert h3[0] == 1

# --- Priority queue pattern: (priority, tie, payload) ---------------------
# Without a tie-breaker, equal priorities compare payloads — can TypeError
# if payloads are incomparable, or reorder "equal" tasks unfairly.
tasks: list[tuple[int, int, str]] = []
_seq = 0


def push_task(priority: int, name: str) -> None:
    global _seq
    # lower priority number = more urgent (min-heap)
    heapq.heappush(tasks, (priority, _seq, name))
    _seq += 1


push_task(2, "write")
push_task(1, "fix")
push_task(1, "email")  # same priority → FIFO via _seq
assert heapq.heappop(tasks)[2] == "fix"
assert heapq.heappop(tasks)[2] == "email"

# Max-heap via negation (numbers only):
nums = [3, 1, 4]
max_h = [-n for n in nums]
heapq.heapify(max_h)
assert -heapq.heappop(max_h) == 4

# --- nlargest / nsmallest / merge ----------------------------------------
data = [9, 1, 5, 3, 7, 2, 8]
assert heapq.nlargest(3, data) == [9, 8, 7]
assert heapq.nsmallest(3, data) == [1, 2, 3]
# key= supported (like sorted)
assert heapq.nlargest(2, ["aa", "b", "ccc"], key=len) == ["ccc", "aa"]

# merge: lazy merge of *pre-sorted* iterables (heap of heads)
merged = list(heapq.merge([1, 4, 7], [2, 5], [0, 3, 6, 8]))
assert merged == list(range(9))

# =============================================================================
# bisect — binary search on a sorted list
# =============================================================================
# Prerequisite: a is sorted ascending (or by the same key you will use).

a = [1, 3, 3, 3, 5, 7]
# bisect_left: first position where all left < x (for default key)
assert bisect.bisect_left(a, 3) == 1   # before the run of 3s
assert bisect.bisect_right(a, 3) == 4  # after the run of 3s  (== bisect())
assert bisect.bisect(a, 3) == 4        # alias of bisect_right

# Membership in sorted list without building a set:
def sorted_contains(seq: list[Any], x: Any) -> bool:
    i = bisect.bisect_left(seq, x)
    return i < len(seq) and seq[i] == x


assert sorted_contains(a, 5) and not sorted_contains(a, 4)

# Range count of equals: right - left
assert bisect.bisect_right(a, 3) - bisect.bisect_left(a, 3) == 3

# insort: maintain sorted order — O(n) insert
b = [1, 3, 5]
bisect.insort_left(b, 3)   # inserts at leftmost equal position
assert b == [1, 3, 3, 5]
bisect.insort_right(b, 3)  # rightmost
assert b == [1, 3, 3, 3, 5]

# --- key= (3.10+): applied to elements in a, NOT automatically to x ------
# Docs: "The key argument should be used carefully" — x is NOT passed
# through key; you must pass an x that already compares in key-space, OR
# use a pattern with a parallel key array. Example with precomputed lo/hi:

rows = [("ann", 30), ("bob", 20), ("zoe", 40)]
# Search by age using a keys list kept in sync:
ages = [r[1] for r in rows]
assert ages == [30, 20, 40]  # NOT sorted — fix:
rows.sort(key=lambda r: r[1])
ages = [r[1] for r in rows]
i = bisect.bisect_left(ages, 30)
assert rows[i][0] == "ann"

# Or bisect with key= on the records, searching with a suitable probe:
# bisect_left(rows, 30, key=lambda r: r[1]) — here x=30 compares with key(el).
rows2 = [("bob", 20), ("ann", 30), ("zoe", 40)]
assert bisect.bisect_left(rows2, 30, key=lambda r: r[1]) == 1

# --- When list+bisect beats tree libraries --------------------------------
# Sorted list: search O(log n), insert/delete O(n).
# Balanced tree (e.g. sortedcontainers.SortedList): all O(log n) but higher
# constants and pointer chasing.
# Rule of thumb in CPython education:
#   n ≲ 10^4–10^5 with moderate inserts → sorted list often faster / simpler
#   n large + heavy insert/delete mid-list → dedicated sorted structure
# Always profile; this sheet documents the tradeoff, not a universal winner.

# Grade-boundary example: find band for a score
boundaries = [0, 50, 60, 70, 80, 90]  # lower edges
labels = ["F", "D", "C", "B", "A", "A*"]


def grade(score: float) -> str:
    # bisect_right - 1 → last boundary <= score
    i = bisect.bisect_right(boundaries, score) - 1
    return labels[max(0, i)]


assert grade(49) == "F" and grade(50) == "D" and grade(95) == "A*"


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    h = [9, 1, 8, 2, 7]
    heapq.heapify(h)
    assert h[0] == min(h)
    out = [heapq.heappop(h) for _ in range(5)]
    assert out == sorted(out) == [1, 2, 7, 8, 9]

    # pushpop / replace
    h = [5, 10, 15]
    heapq.heapify(h)
    assert heapq.heappushpop(h, 3) == 3  # 3 is new min and immediately popped
    assert h[0] == 5
    assert heapq.heapreplace(h, 1) == 5
    assert h[0] == 1

    assert heapq.nlargest(2, [4, 1, 3, 2]) == [4, 3]
    assert list(heapq.merge([1, 3], [2, 4])) == [1, 2, 3, 4]

    s = [1, 2, 4, 4, 5]
    assert bisect.bisect_left(s, 4) == 2
    assert bisect.bisect_right(s, 4) == 4
    bisect.insort(s, 3)
    assert s == [1, 2, 3, 4, 4, 5]

    # unsorted bisect is garbage — document by contrast with sorted check
    bad = [3, 1, 2]
    # no assert on index meaning; only that call succeeds
    _ = bisect.bisect_left(bad, 2)

    # max-heap via negation
    mx = [-x for x in (1, 5, 3)]
    heapq.heapify(mx)
    assert [-heapq.heappop(mx) for _ in range(3)] == [5, 3, 1]

    print("heapq_bisect_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
