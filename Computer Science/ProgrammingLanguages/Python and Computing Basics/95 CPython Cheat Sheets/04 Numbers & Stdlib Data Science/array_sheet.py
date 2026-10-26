#!/usr/bin/env python3
"""
=============================================================================
SHEET: array.array                      TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 04.x packed buffers / vs list / memoryview / NumPy
=============================================================================

WHAT IT IS
  - array.array(typecode, initializer): mutable sequence of *homogeneous*
    C-machine values packed densely (unboxed), exporting the buffer
    protocol. Stdlib-only — not a NumPy ndarray.
  - Typecodes select C type width/signedness: 'b' int8, 'B' uint8,
    'h'/'H' int16, 'i'/'I' int32-ish (platform), 'l'/'L', 'q'/'Q',
    'f' float32, 'd' float64, …
  - Good for compact storage + C interop; indexing still boxes to Python
    int/float on access.

INVARIANTS
  - One typecode per array for life of the object.
  - Out-of-range assign → OverflowError (signed/width enforced).
  - Supports buffer protocol → memoryview(array) zero-copy window.
  - tobytes / frombytes / tofile / fromfile for octet interchange
    (native endian unless you manage endian yourself).
  - list stores PyObject*; array stores raw C values — memory ≪ list
    for large int/float tables, but element access pays boxing.

DELEGATES TO (CPython)
  - Modules/arraymodule.c — arrayobject, typecode descriptors, buffer
  - Include/pybuffer.h — buffer export consumed by memoryview
  - Objects/memoryobject.c — memoryview over array buffers
  - (Leave CPython) NumPy — dtype arrays, ufuncs, BLAS, N-D

COMPLEXITY CARD
  - index / assign:          O(1) (+ box/unbox to Python object)
  - append:                  O(1) amortised (overallocation)
  - extend n items:          O(n)
  - tobytes:                 O(n) copy
  - memoryview slice:        O(1) metadata typically

WHEN A BEATS B
  - array vs list[int]: array when millions of small ints/floats and you
    care about RAM / buffer export; list when heterogeneous or object
    identity matters.
  - array vs memoryview: array owns storage; memoryview views someone's
    buffer (including an array's).
  - array vs NumPy: stay on array for tiny stdlib tools / simple C FFI;
    leave for NumPy when you need N-D, broadcasting, vectorised math,
    dtype ecosystem, or serious numeric performance.
  - array('d') vs list of float: array wins memory; NumPy wins compute.

EDGE CASES
  - Platform sizes: 'i'/'l' width is platform-dependent — check
    array.array('i').itemsize; prefer 'q'/'d' when you need fixed width
    in portable formats, or use struct for wire layouts.
  - Endianness: tobytes() is native — swap explicitly for portable files.
  - 'u' wide unicode typecode was removed — use str or other codes.
  - Empty array still has a typecode and itemsize.
  - Multiplying / slicing returns new array objects (copy semantics for
    slice values — still packed).

SOURCE MAP
  - Modules/arraymodule.c      :: array_new / array_item / array_buffer
  - Objects/memoryobject.c     :: PyMemoryView_FromObject
  - (external) NumPy C-API     :: when you leave the stdlib
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import array
import sys

# --- typecodes -----------------------------------------------------------
# array.typecodes → 'bBhHiIlLqQfd' (exact set may include more historically)
# itemsize = width in bytes of one element on this platform

# --- buffer / memoryview -------------------------------------------------
# mv = memoryview(a); mv[0] = … if writable; mv.cast('B') for bytes view

# --- vs list of int ------------------------------------------------------
# list: pointer farm, GC traffic, flexible types
# array: contiguous C values, rigid typecode

# --- vs NumPy (leave CPython) --------------------------------------------
# NumPy: ndarray, dtype, ufuncs, broadcasting, advanced indexing, BLAS
# array.array: none of that — stop expecting np.sin(a) to vectorise.


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    a = array.array("i", [1, 2, 3, 4])
    assert a.typecode == "i" and a.itemsize >= 2
    assert a[0] == 1 and list(a) == [1, 2, 3, 4]
    a.append(5)
    assert a[-1] == 5
    a.extend([6, 7])
    assert len(a) == 7

    # Overflow on narrow signed codes
    tiny = array.array("b", [0])  # signed int8
    try:
        tiny[0] = 128
        raise AssertionError("expected OverflowError")
    except OverflowError:
        pass
    tiny[0] = 127
    assert tiny[0] == 127

    # bytes round-trip (native endian)
    raw = a.tobytes()
    b = array.array("i")
    b.frombytes(raw)
    assert b == a

    # buffer protocol ↔ memoryview
    mv = memoryview(a)
    assert mv.format and mv.nbytes == len(a) * a.itemsize
    assert mv[1] == 2
    mv[1] = 20
    assert a[1] == 20
    mv.release()

    # float64 packed
    d = array.array("d", [0.1, 0.2, 0.3])
    assert d.itemsize == 8
    assert abs(d[0] - 0.1) < 1e-15  # still binary float semantics!

    # Memory contrast sketch: array stores unboxed; list stores objects.
    # We only assert typecodes exist and 'q' is 8 bytes on this build.
    q = array.array("q", [10**12])
    assert q.itemsize == 8
    assert "i" in array.typecodes and "d" in array.typecodes

    # Slice copies into a new array
    sl = a[1:4]
    assert isinstance(sl, array.array) and sl.typecode == "i"
    sl[0] = 99
    assert a[1] == 20  # original unchanged by slice element assign

    # Heterogeneous list cannot be an array
    try:
        array.array("i", [1, "x"])  # type: ignore[list-item]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass

    # Pointer: leave for NumPy when N-D / ufuncs needed (stdlib has none)
    assert not hasattr(a, "reshape")
    _ = sys  # platform note available if teaching itemsize variance

    print("array_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
