#!/usr/bin/env python3
"""
=============================================================================
SHEET: collections                      TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x containers / queues / specialised mappings
=============================================================================

WHAT IT IS
  - Stdlib toolkit of specialised containers on top of (or beside) dict/list:
    deque (double-ended queue), Counter (multiset of hashables), defaultdict
    (dict with missing-key factory), namedtuple (tuple subclass with fields),
    OrderedDict (legacy ordered mapping; plain dict already ordered), ChainMap
    (layered dict search), UserDict (easy-to-subclass mapping wrapper).

INVARIANTS
  - deque: O(1) append/pop at BOTH ends; maxlen drops from the *opposite*
    end on overflow. Random index access is O(n) (block-linked, not array).
  - Counter: subclass of dict; missing key → 0 (via __missing__), NOT KeyError.
    Counts may go negative; .elements() skips non-positive.
  - defaultdict: __getitem__ on miss calls default_factory() and *inserts*
    the result — side effect on read via []. .get() does NOT insert.
  - namedtuple: immutable tuple; _replace / _asdict / _fields; hashable iff
    all fields are. Field names must be valid identifiers (unless rename=True).
  - OrderedDict: still tracks order explicitly for reorder APIs (move_to_end,
    equality that considers order). Plain dict already preserves insertion
    order since 3.7 — prefer dict unless you need OD-only methods.
  - ChainMap: lookups walk maps left→right; writes hit maps[0] only.
  - UserDict: stores data in .data dict; subclass without fighting C dict.

DELEGATES TO (CPython)
  - Modules/_collectionsmodule.c  — deque C type (block pointers, maxlen)
  - Lib/collections/__init__.py   — Counter, defaultdict, namedtuple,
    OrderedDict, ChainMap, UserDict, UserList, UserString (Python)
  - Objects/dictobject.c          — underlying mapping machinery for
    Counter / defaultdict / OrderedDict / ChainMap layers
  - Objects/tupleobject.c         — namedtuple instances are real tuples

COMPLEXITY CARD (amortised unless noted)
  - deque.append / appendleft / pop / popleft:     O(1)
  - deque[i] / insert / delete middle:             O(n)
  - deque rotate(k):                               O(k)  (or O(n-|k|))
  - Counter update / most_common(k):               O(n) / O(n log k) heap
  - defaultdict[k] miss:                           O(1) + factory cost
  - namedtuple field access:                       O(1)  (itemgetter attrs)
  - OrderedDict move_to_end:                       O(1)
  - ChainMap[k] lookup:                            O(#maps) worst
  - UserDict ops:                                  same as underlying dict

WHEN A BEATS B
  - deque vs list as queue: deque — list.pop(0) is O(n).
  - deque(maxlen=N) vs manual trim: maxlen auto-discards opposite end.
  - Counter vs dict[int]: Counter for multiset algebra (+ − & |) and
    most_common; plain dict when you only store arbitrary values.
  - defaultdict vs dict.setdefault: defaultdict when every miss should
    create the same shape; setdefault when creation is rare / custom.
  - namedtuple vs dataclass: namedtuple when you want tuple unpacking,
    hashing, and low memory; dataclass when you need defaults, mutability
    control, __post_init__, or richer methods.
  - OrderedDict vs dict: only when move_to_end / order-sensitive == matter.
  - ChainMap vs merge copies: ChainMap for layered scopes without copying.
  - UserDict vs subclassing dict: UserDict — dict subclassing has sharp
    C-level edges (some methods bypass your overrides).

EDGE CASES
  - deque index / in: O(n); do not use as a random-access array.
  - Counter: c['x'] += 1 works for missing keys (returns 0 first); del or
    subtract to remove. most_common() with ties: order among equals is
    insertion order of first appearance (stable heap path).
  - defaultdict: d['k'] inserts; 'k' in d becomes True after a miss via [].
  - namedtuple defaults (since 3.7): defaults attach to *rightmost* fields.
  - OrderedDict == dict: equal if same key→value (order ignored vs dict);
    OrderedDict == OrderedDict considers order.
  - ChainMap.new_child() pushes a fresh map; parents stay shared.
  - UserDict: override methods on the wrapper; mutate .data carefully.

SOURCE MAP
  - Modules/_collectionsmodule.c :: deque_append, deque_pop, deque_appendleft
  - Modules/_collectionsmodule.c :: deque_rotate, deque_maxlen handling
  - Lib/collections/__init__.py  :: class Counter / defaultdict / OrderedDict
  - Lib/collections/__init__.py  :: namedtuple() factory, ChainMap, UserDict
  - Objects/dictobject.c         :: dict subclass / __missing__ hooks
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

from collections import (
    ChainMap,
    Counter,
    OrderedDict,
    UserDict,
    defaultdict,
    deque,
    namedtuple,
)

# =============================================================================
# deque — double-ended queue (C: block-linked list of fixed-size blocks)
# =============================================================================
# Mental model: not a contiguous array. Each block holds many pointers;
# left/right block pointers make end ops O(1). Indexing walks blocks → O(n).

dq: deque[int] = deque([1, 2, 3])
dq.append(4)        # right end O(1)
dq.appendleft(0)    # left end O(1)
assert list(dq) == [0, 1, 2, 3, 4]
assert dq.pop() == 4          # right
assert dq.popleft() == 0      # left
# list equivalent of popleft is list.pop(0) → O(n) memmove. Use deque.

# maxlen: bounded ring. Overflow drops from the *other* end.
ring: deque[int] = deque(maxlen=3)
for x in (1, 2, 3, 4, 5):
    ring.append(x)  # after 3, further appends discard left
assert list(ring) == [3, 4, 5]
ring.appendleft(9)  # overflow on left → discard right
assert list(ring) == [9, 3, 4]

# rotate: positive → right; negative → left. O(|n|) element moves at ends.
d2: deque[int] = deque([0, 1, 2, 3, 4])
d2.rotate(2)   # [3, 4, 0, 1, 2]
assert list(d2) == [3, 4, 0, 1, 2]
d2.rotate(-2)
assert list(d2) == [0, 1, 2, 3, 4]

# extend / extendleft — extendleft reverses the iterable as it prepends
d3: deque[str] = deque("ab")
d3.extend("cd")       # right: a b c d
d3.extendleft("xy")   # left inserts x then y → y x a b c d
assert "".join(d3) == "yxabcd"

# Thread note (folklore): individual deque ops are atomic under the GIL for
# the C methods, but compound "check then pop" is still a race — use a Lock
# or queue.Queue for multi-thread producer/consumer.

# =============================================================================
# Counter — multiset / bag of hashable elements (dict subclass)
# =============================================================================
# __missing__ returns 0 so c[k] never KeyErrors for absent keys. That also
# means c[k] += 1 works without setdefault. Values are ints by convention
# but not enforced — non-int values break arithmetic helpers.

c = Counter("abracadabra")
assert c["a"] == 5 and c["z"] == 0  # miss → 0, does NOT insert
assert "z" not in c                 # unlike defaultdict[]
c["z"] += 1                         # now inserted
assert c["z"] == 1 and "z" in c

# most_common: heapq.nlargest under the hood for k; full sort if k is None
assert c.most_common(2)[0][0] == "a"
# total() (3.10+): sum of counts
assert c.total() == sum(c.values())

# Multiset algebra — like sets but with multiplicities
a = Counter(a=3, b=1)
b = Counter(a=1, b=2, c=1)
assert a + b == Counter(a=4, b=3, c=1)   # add counts
assert a - b == Counter(a=2)            # keep only positive results
assert a & b == Counter(a=1, b=1)       # min counts (intersection)
assert a | b == Counter(a=3, b=2, c=1)  # max counts (union)
# unary +: drop non-positive; unary -: negate then drop non-positive from +
neg = Counter(a=2, b=-3)
assert +neg == Counter(a=2)
assert -neg == Counter(b=3)

# elements(): expand positive counts (order = first-seen keys)
assert list(Counter(a=2, b=1).elements()) == ["a", "a", "b"]
# update / subtract: in-place; subtract can go negative
c2 = Counter(a=2)
c2.subtract(a=5)
assert c2["a"] == -3

# =============================================================================
# defaultdict — dict that inserts default_factory() on [] miss
# =============================================================================
# Critical: mutation-on-read via []. Use .get() / `in` when probing without
# inserting. Factory is called with ZERO args (use partial/lambda for args).

dd: defaultdict[str, list[int]] = defaultdict(list)
dd["nums"].append(1)  # creates [] then appends
dd["nums"].append(2)
assert dd == {"nums": [1, 2]}
assert dd.get("missing") is None  # get does NOT call factory / insert
assert "missing" not in dd

# Grouping idiom:
pairs = [("a", 1), ("b", 2), ("a", 3)]
groups: defaultdict[str, list[int]] = defaultdict(list)
for k, v in pairs:
    groups[k].append(v)
assert dict(groups) == {"a": [1, 3], "b": [2]}

# Nested: lambda: defaultdict(int) — each miss gets a fresh inner map
tree: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
tree["user"]["hits"] += 1
assert tree["user"]["hits"] == 1

# default_factory = None → behaves like normal dict (KeyError on miss)
plain = defaultdict(None)  # type: ignore[arg-type]
try:
    _ = plain["x"]
except KeyError:
    pass

# =============================================================================
# namedtuple — lightweight immutable record (tuple subclass)
# =============================================================================
# Factory returns a new type. Instances are tuples: unpackable, hashable
# (if fields are), indexable. Attributes are itemgetter descriptors → fast.

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
assert p.x == 3 and p[1] == 4 and p == (3, 4)
assert p._fields == ("x", "y")
assert p._asdict() == {"x": 3, "y": 4}  # OrderedDict historically; dict now
p2 = p._replace(y=99)
assert p2 == Point(3, 99) and p == Point(3, 4)  # original untouched

# defaults: apply to the rightmost fields
Rect = namedtuple("Rect", "w h color", defaults=["black"])
assert Rect(1, 2) == Rect(1, 2, "black")
assert Rect(1, 2, "red").color == "red"

# rename=True: invalid field names become _N
Weird = namedtuple("Weird", ["def", "x"], rename=True)
assert Weird._fields[0] == "_0"

# vs dataclass: namedtuple wins for tuple protocol + tiny memory; loses on
# mutable fields, validators, inheritance flexibility, slots+kw_only, etc.

# =============================================================================
# OrderedDict — legacy explicit order + reorder API
# =============================================================================
# Since 3.7, builtin dict preserves insertion order. Prefer dict unless you
# need: move_to_end, popitem(last=False) FIFO, or order-sensitive equality
# between two OrderedDicts.

od: OrderedDict[str, int] = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
od.move_to_end("a")            # → b, c, a  (last=True default)
assert list(od) == ["b", "c", "a"]
od.move_to_end("c", last=False)  # → c, b, a
assert list(od) == ["c", "b", "a"]
# popitem(last=True) LIFO; last=False FIFO — dict.popitem is LIFO only
assert od.popitem(last=False) == ("c", 3)

# Equality: OD vs OD cares about order; OD vs dict does not
assert OrderedDict([("a", 1), ("b", 2)]) != OrderedDict([("b", 2), ("a", 1)])
assert OrderedDict([("a", 1), ("b", 2)]) == {"b": 2, "a": 1}

# =============================================================================
# ChainMap — search a sequence of mappings (scopes / configs)
# =============================================================================
# Lookups: maps[0], then maps[1], … Writes/deletes always hit maps[0].

defaults = {"host": "localhost", "port": 8080, "debug": False}
cli = {"port": 9000}
env = {"debug": True}
cfg = ChainMap(cli, env, defaults)
assert cfg["host"] == "localhost"  # from defaults
assert cfg["port"] == 9000         # cli shadows
assert cfg["debug"] is True        # env shadows defaults
cfg["port"] = 9001                 # writes into cli only
assert cli["port"] == 9001 and defaults["port"] == 8080

# new_child: push a fresh mutable layer (like entering a scope)
child = cfg.new_child({"port": 1})
assert child["port"] == 1 and child.parents["port"] == 9001
# maps attribute: the underlying list (mutable — advanced use)
assert child.maps[0] == {"port": 1}

# =============================================================================
# UserDict — subclass-friendly mapping wrapper
# =============================================================================
# Prefer UserDict over subclassing dict when you override __getitem__/
# __setitem__/update: many dict methods are C-accelerated and may not call
# your Python overrides. UserDict routes through .data.

class UpperKeys(UserDict):
    def __setitem__(self, key, value):  # type: ignore[override]
        super().__setitem__(str(key).upper(), value)

    def __getitem__(self, key):  # type: ignore[override]
        return super().__getitem__(str(key).upper())

uk = UpperKeys(a=1)
uk["b"] = 2
assert uk["A"] == 1 and uk["B"] == 2 and list(uk.data) == ["A", "B"]


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    # deque ends + maxlen
    q: deque[int] = deque(maxlen=2)
    q.append(1)
    q.append(2)
    q.append(3)
    assert list(q) == [2, 3]
    q.appendleft(0)
    assert list(q) == [0, 2]

    # Counter algebra + miss semantics
    c = Counter("mississippi")
    assert c["s"] == 4 and c["z"] == 0 and "z" not in c
    assert (Counter(a=2) & Counter(a=5, b=1)) == Counter(a=2)
    assert c.total() == len("mississippi")

    # defaultdict mutation-on-[]
    d: defaultdict[str, int] = defaultdict(int)
    d["x"] += 1
    assert d["x"] == 1 and d.get("y") is None and "y" not in d

    # namedtuple
    T = namedtuple("T", "a b", defaults=[0])
    assert T(1) == (1, 0) and T(1)._replace(b=2).b == 2

    # OrderedDict reorder
    od: OrderedDict[str, int] = OrderedDict(x=1, y=2)
    od.move_to_end("x", last=False)
    assert list(od) == ["x", "y"]

    # ChainMap write locality
    m0, m1 = {"a": 1}, {"a": 9, "b": 2}
    cm = ChainMap(m0, m1)
    assert cm["b"] == 2
    cm["a"] = 5
    assert m0["a"] == 5 and m1["a"] == 9

    # UserDict
    class D(UserDict):
        pass

    assert D(a=1)["a"] == 1

    print("collections_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
