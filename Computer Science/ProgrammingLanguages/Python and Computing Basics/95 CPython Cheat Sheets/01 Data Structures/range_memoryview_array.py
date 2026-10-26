#!/usr/bin/env python3
"""
=============================================================================
SHEET: range / memoryview / array.array   TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x sequences / 03.x buffer protocol / 04.x numbers
=============================================================================

WHAT IT IS
  - range: lazy arithmetic progression (start, stop, step) — O(1) space
    regardless of length (within index limits). Not a list of integers.
  - memoryview: zero-copy interpretation of an object's buffer export
    (PEP 3118). Slicing a memoryview usually views the same memory.
  - array.array: compact *homogeneous* C-typed sequence (typecodes like
    'i', 'd', 'b'). Packed values — still NOT NumPy (no broadcasting,
    no ufuncs, no N-D, no dtypes ecosystem).

INVARIANTS
  - range equality is value-based (same sequence of ints), not identity.
  - range supports O(1) len / indexing / membership for ints (clever
    arithmetic), slicing → new range (also lazy).
  - memoryview format/shape come from the exporter; casting requires
    compatible sizes; release() drops the buffer.
  - array.array typecode fixed at construction; append grows with
    overallocation similar in spirit to list but stores unboxed C values.
  - Buffer consumers must respect read-only vs writable exporters.

DELEGATES TO (CPython)
  - Objects/rangeobject.c — range_new, range_length, range_item, contains
  - Objects/memoryobject.c — PyMemoryView_FromObject, memory_cast, …
  - Modules/arraymodule.c — arrayobject, typecode table
  - Include/abstract.h buffer API — PyObject_GetBuffer / PyBuffer_Release

COMPLEXITY CARD
  - len(range) / range[i] / n in range:   O(1) arithmetic
  - list(range(n)):                       O(n) materialise
  - memoryview slice:                     O(1) metadata (typically)
  - memoryview.tobytes():                 O(n) copy
  - array append / index:                 O(1) amortised / O(1)
  - array vs list for PyObject workload:  array loses (must box on access)

WHEN A BEATS B
  - range vs list(range): keep range for loops / membership / len; list
    only when you need a mutable materialised sequence.
  - memoryview vs bytes[a:b]: memoryview when zero-copy matters (large
    buffers, protocol parsers); bytes slice when you need an owned bytes.
  - array.array vs list: array for dense C scalars + buffer export; list
    for heterogeneous Python objects.
  - array.array vs NumPy: NumPy for numeric computing; array for stdlib-
    only packed storage / C interop without the dependency.

EDGE CASES
  - range(10**18) is fine; list(range(10**18)) is not (memory).
  - True/False are ints subclass-wise: True in range(2) → True.
  - Empty ranges: range(0), range(5, 2), range(0, 10, -1) → empty.
  - memoryview of a released / mutated exporter: use carefully; release
    order matters with nested views.
  - array('u') was wide unicode and was removed — use str or other codes.
  - Endianness: array.tobytes() is native endian unless you manage it;
    for portable wire formats prefer struct / explicit endian.

SOURCE MAP
  - Objects/rangeobject.c :: range_new / range_contains / range_subscript
  - Objects/memoryobject.c :: memoryview_from* / memory_cast / memory_release
  - Modules/arraymodule.c :: array_new / array_from* / array_buffer
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- range: arithmetic sequence, not a container of ints -----------------
# Internally: store start, stop, step, length — NOT the expanded ints.
r = range(0, 10, 2)
assert list(r) == [0, 2, 4, 6, 8]
assert len(r) == 5  # O(1): length computed from the three parameters
assert r[3] == 6  # O(1): start + i*step (with bounds check)
assert 4 in r and 5 not in r  # O(1) membership via arithmetic, not scan
# Huge ranges stay tiny objects:
huge = range(10**18)
assert len(huge) == 10**18  # ok
assert huge[10**18 - 1] == 10**18 - 1
# Do NOT list(huge).

# Slicing a range returns another range (still lazy):
assert r[1:4] == range(2, 8, 2)
assert r[::-1] == range(8, -2, -2)

# Equality compares the generated sequence, not the parameters alone:
assert range(0, 5, 1) == range(0, 5)
assert range(0, 0) == range(5, 2)  # both empty
# Identity is irrelevant:
assert range(3) == range(0, 3) and range(3) is not range(0, 3)

# range is immutable; no append. It is *not* a list subclass.
try:
    r[0] = 1  # type: ignore[index]
except TypeError:
    pass

# --- memoryview: buffer protocol window ----------------------------------
# Any object supporting the buffer protocol can be viewed without copying
# the underlying memory (bytes, bytearray, array.array, mmap, many C types).
data = bytearray(b"0123456789")
mv = memoryview(data)
# Zero-copy slice: new memoryview, same exporter memory:
mid = mv[2:7]
assert mid.tobytes() == b"23456"
mid[0:2] = b"XX"  # writable because bytearray is writable
assert data == bytearray(b"01XX456789")

# Cast: reinterpret item size / format when byte lengths allow.
# Prefer struct for portable endian-aware layouts; cast('B') is always safe.
raw = bytearray(b"\x01\x00\x00\x00\x02\x00\x00\x00")
bv = memoryview(raw).cast("B")
assert list(bv[:4]) == [1, 0, 0, 0]
# Native unsigned-int view: same bytes, itemsize-wide units (endian = host).
iv = memoryview(raw).cast("I")
assert iv.nbytes == 8 and len(iv) == 8 // iv.itemsize
iv.release()
bv.release()

# Read-only exporter → read-only view:
ro = memoryview(b"abcd")
try:
    ro[0] = 65  # type: ignore[index]
except TypeError:
    pass
ro.release()
mv.release()
# Nested views: release children before relying on exporter teardown.

# --- array.array: packed C values (stdlib) — not NumPy -------------------
from array import array

# Typecodes (common): 'b' signed char, 'B' unsigned char, 'h'/'H' short,
# 'i'/'I' int, 'l'/'L' long, 'q'/'Q' long long, 'f' float, 'd' double.
ai = array("i", [1, 2, 3, 4])
assert ai[0] == 1 and ai.itemsize >= 2  # itemsize platform-dependent for 'i'
ai.append(5)
ai.extend([6, 7])
assert list(ai) == [1, 2, 3, 4, 5, 6, 7]
# Buffer export → memoryview / C extensions / socket.send without boxing
# every element as a PyLong:
view = memoryview(ai)
assert view.ndim == 1
view.release()

# bytes round-trip (native endian):
blob = ai.tobytes()
ai2 = array("i")
ai2.frombytes(blob)
assert ai2 == ai

# Contrast with list: list stores PyObject* (8 bytes pointer + object
# header each); array stores raw C values. Accessing ai[i] still *boxes*
# into a Python int temporarily — fine for I/O buffers, not a NumPy
# replacement for heavy numeric kernels.

# Wrong expectations:
#   - no ai + ai vector add → concatenates like sequences
assert array("i", [1, 2]) + array("i", [3]) == array("i", [1, 2, 3])
#   - no broadcasting, no dtype promotion rules, no N-dimensional strides
#     beyond what memoryview.cast can flat-reinterpret.

# range + array + memoryview combo: build packed samples without a giant
# temporary Python list when you can feed an iterable of ints:
samples = array("d", (i * 0.5 for i in range(5)))
assert samples[2] == 1.0


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    r = range(1, 20, 3)
    assert 1 in r and 2 not in r
    assert r[0] == 1 and r[-1] == 19
    assert len(range(10**12)) == 10**12
    assert range(5)[::2] == range(0, 5, 2)

    buf = bytearray(b"helloworld")
    mv = memoryview(buf)
    mv[0:5] = b"HELLO"
    assert bytes(buf) == b"HELLOworld"
    assert mv[5:].tobytes() == b"world"
    mv.release()

    ar = array("I", [10, 20, 30])
    assert ar.itemsize in (2, 4, 8)
    ar.append(40)
    assert sum(ar) == 100
    mv2 = memoryview(ar)
    assert mv2.tolist() == [10, 20, 30, 40]
    mv2.release()

    # range is not materialised
    assert range(3) == range(0, 3, 1)
    assert list(range(0)) == []

    # memoryview read-only
    try:
        memoryview(b"ab")[0] = 1  # type: ignore[index]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass

    print("range_memoryview_array.py: all probes passed")


if __name__ == "__main__":
    _probes()
