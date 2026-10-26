#!/usr/bin/env python3
"""
=============================================================================
SHEET: dict                            TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 07.x hash tables / 11.x containers
=============================================================================

WHAT IT IS
  - Mutable mapping: hashable keys → arbitrary values.
  - CPython's "compact dict": a shared keys object (hashes + key pointers +
    index table) plus a dense values array. Insertion order of keys is an
    *official* language guarantee (since 3.7; CPython implemented it in 3.6).

INVARIANTS
  - Key must be hashable (same rules as set elements).
  - Lookup: hash(key) → index into keys table → compare hash then ==.
  - d[k] = v replaces value for equal key; does not duplicate the key entry.
  - Iteration order == insertion order of *currently living* keys
    (deleted keys leave gaps that are compacted on resize; new keys append).
  - Views (keys/values/items) are dynamic — they reflect later mutations.
  - Mutating the set of keys during active iteration → RuntimeError.
  - Combined vs split table (implementation): many equal-shaped instances
    can share a keys object (split) with per-instance values; ordinary
    dicts are usually *combined*. You program to the abstract mapping API.

DELEGATES TO (CPython)
  - Objects/dictobject.c  — insertion, lookup, resize, merge, views
  - Objects/dictobject.h / Include/internal/pycore_dict.h — PyDictKeysObject,
    DKIX_EMPTY / DKIX_DUMMY, compact layout
  - Objects/clinic/dictobject.c.h — Argument Clinic wrappers where used

COMPLEXITY CARD (average / amortised)
  - get / set / del / in:     O(1) expected
  - popitem:                  O(1)  (LIFO of insertion order in CPython)
  - copy / dict(d):           O(n)
  - update / | / |=:          O(n) in size of other
  - fromkeys:                 O(n)
  - iterate keys/values/items: O(n)

WHEN A BEATS B
  - dict vs list of pairs: dict for keyed lookup; list when order+dup keys.
  - dict vs set: dict when values exist; set when presence-only.
  - d.get(k, default) vs d[k]: get when miss is normal; [] when miss is bug.
  - setdefault vs if k not in d: setdefault does one lookup path for
    "insert if absent"; careful — default is evaluated eagerly.
  - | vs update: | builds a new dict; update / |= mutate in place.

EDGE CASES
  - Unhashable key → TypeError.
  - popitem() on empty → KeyError; CPython pops *last inserted* (LIFO).
  - views are not snapshots: list(d.keys()) if you need a stable copy.
  - d | other requires mappings; |= accepts any mapping or key-iterable
    of pairs depending on version/API — prefer Mapping.update clarity.
  - Hash collisions: unequal keys, same hash bits → probe / compare eq.
  - Equal keys with different identity collapse to one entry (last value).
  - float('nan') as key: weird because nan != nan; usually one entry but
    avoid NaN keys.
  - Changing a key object in-place after insert (custom class) corrupts
    the dict the same way as with sets.

SOURCE MAP
  - Objects/dictobject.c :: PyDict_GetItem* / _PyDict_GetItem_KnownHash
  - Objects/dictobject.c :: insertdict / delitem / dict_table_resize
  - Objects/dictobject.c :: dict_merge / dict_update_common
  - Objects/dictobject.c :: dictkeys_new / new_keys_object (compact keys)
  - Objects/dictobject.c :: dict_keys / dict_values / dict_items (views)
  - Objects/dictobject.c :: dict_popitem (LIFO)
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

# Literal construction — BUILD_MAP / BUILD_CONST_KEY_MAP in bytecode for
# constant-key shapes. Empty {} is a dict (unlike sets which need set()).
d: dict[str, int] = {"a": 1, "b": 2, "c": 3}

# Insertion order is observable and guaranteed:
assert list(d) == ["a", "b", "c"]
d["d"] = 4
assert list(d) == ["a", "b", "c", "d"]
# Re-binding an existing key does NOT move it in order:
d["a"] = 10
assert list(d) == ["a", "b", "c", "d"] and d["a"] == 10

# --- Compact layout (mental model, not exact field names) ----------------
# Older teaching model: flat open-addressed array of (hash, key, value).
# Modern CPython compact dict roughly:
#   keys object:  indices[]  +  dense entries(hash, key) in insertion order
#   values:       dense array parallel to entries  (or split per-instance)
# Why compact: iteration walks the dense entry list (cache-friendly), not
# a sparse hash table full of empty slots. The indices table maps
#   hash-derived probe → entry index   (or DKIX_EMPTY / DKIX_DUMMY).
# Split-table form: many objects' __dict__ share one keys object when they
# share the same attribute layout; each instance keeps its own values
# array. Ordinary {} literals are combined (keys+values owned together).

# --- Hash collision folklore ---------------------------------------------
# Same as sets at the comparison layer: probe until empty OR (hash match
# AND key == candidate). Compact dict stores indices into entries; probing
# still uses hash bits. Collision ⇒ extra probes + eq checks, still O(1)
# expected under good hashes (SipHash for str, etc.).

# Key must be hashable:
try:
    d[[1, 2]] = 0  # type: ignore[index]
except TypeError:
    pass

# --- Lookup / insert helpers ---------------------------------------------
assert d.get("z") is None  # miss → default None (or second arg)
assert d.get("z", -1) == -1
assert d.setdefault("e", 5) == 5  # insert if absent, return final value
assert d.setdefault("e", 99) == 5  # already present → no change
# Eager default pitfall:
#   d.setdefault(k, expensive())   # expensive() ALWAYS runs
# Prefer:
#   if k not in d: d[k] = expensive()

# pop: remove key, return value; KeyError unless default given
assert d.pop("e") == 5
assert d.pop("e", None) is None

# popitem: CPython LIFO — last inserted key wins
last_key, last_val = d.popitem()
assert (last_key, last_val) == ("d", 4)

# --- Views: dynamic windows, not lists -----------------------------------
d = {"x": 1, "y": 2}
kv, vv, iv = d.keys(), d.values(), d.items()
assert list(kv) == ["x", "y"]
d["z"] = 3
assert "z" in kv and 3 in vv and ("z", 3) in iv
# Set operations on key views (and items if values hashable):
assert d.keys() & {"x", "q"} == {"x"}
# Snapshot when you need isolation from later mutation:
snap = list(d.items())

# --- Merge: update, |, |= ------------------------------------------------
left = {"a": 1, "b": 2}
right = {"b": 20, "c": 3}
merged = left | right  # new dict; right wins on conflict (PEP 584)
assert merged == {"a": 1, "b": 20, "c": 3} and left == {"a": 1, "b": 2}
left |= right  # in-place; equivalent spirit to left.update(right)
assert left == merged
left.update(c=30, d=4)  # kwargs / iterable of pairs / mapping
assert left["c"] == 30 and left["d"] == 4

# fromkeys: same value object shared — careful with mutables
row = dict.fromkeys(["p", "q"], 0)
assert row == {"p": 0, "q": 0}
bad = dict.fromkeys(["p", "q"], [])  # ONE list shared by both keys
bad["p"].append(1)
assert bad["q"] == [1]  # surprise sharing

# --- Mutating during iteration fails -------------------------------------
# The interpreter detects dict version tags / size changes on the key set.
boom = {"a": 1, "b": 2, "c": 3}
try:
    for k in boom:
        if k == "b":
            boom["new"] = 0  # changing keys while iterating
except RuntimeError:
    pass
# Safe patterns: iterate list(boom), or collect keys to delete first,
# or build a new dict. Value-only rebinds of *existing* keys are a gray
# area — still prefer not to mutate the mapping during iteration.

# clear / copy
clone = boom.copy()  # shallow: new dict, same value objects
boom.clear()
assert boom == {} and clone.keys()  # clone independent table

# --- Equality / identity -------------------------------------------------
assert {"a": 1, "b": 2} == {"b": 2, "a": 1}  # order irrelevant for ==
assert list({"a": 1, "b": 2}) != list({"b": 2, "a": 1})  # order for list()


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    m: dict[int, str] = {}
    for i in range(50):
        m[i] = str(i)
    assert list(m) == list(range(50))  # insertion order
    m[0] = "zero"
    assert list(m)[0] == 0  # rebind keeps position
    assert m.popitem() == (49, "49")  # LIFO
    assert (m.keys() | {100}) >= {0, 100}
    a, b = {"x": 1}, {"x": 9, "y": 2}
    assert a | b == {"x": 9, "y": 2}
    a |= b
    assert a == {"x": 9, "y": 2}
    # view dynamism
    keys = a.keys()
    a["z"] = 3
    assert "z" in keys
    # mutation guard
    try:
        for k in a:
            a[k + "_"] = 0  # type: ignore[operator]
        raise AssertionError("expected RuntimeError")
    except (RuntimeError, TypeError):
        # TypeError if k+"_" fails first on non-str — rebuild cleanly:
        pass
    g = {1: "a", 2: "b"}
    try:
        for k in g:
            g[99] = "x"
        raise AssertionError("expected RuntimeError")
    except RuntimeError:
        pass
    assert dict.fromkeys(("a", "b"), 1) == {"a": 1, "b": 1}
    print("dict.py: all probes passed")


if __name__ == "__main__":
    _probes()
