#!/usr/bin/env python3
"""
=============================================================================
SHEET: str / bytes / bytearray         TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 03.x unicode / 11.x buffers
=============================================================================

WHAT IT IS
  - str: immutable sequence of Unicode code points. CPython stores a
    *compact* representation: one of ASCII / Latin-1 / UCS-2 / UCS-4
    "kind" chosen by the maximum ordinal in the string (PEP 393).
  - bytes: immutable sequence of 0..255 ints (raw octets).
  - bytearray: mutable version of bytes.
  - memoryview: zero-copy window over buffer-exporting objects (brief).

INVARIANTS
  - str indexes yield length-1 str, not "char" ints; bytes index → int.
  - str and bytes never mix with silent coercion: b"a" + "a" → TypeError.
  - encode: str → bytes; decode: bytes/bytearray → str (codecs).
  - Interning: some strings (identifiers, explicit sys.intern) share
    identity; equal literals *may* be identical but == is the API contract.
  - Concatenation of many small pieces: prefer "".join / bytearray / io
    over repeated + in a loop (quadratic risk from immutability).

DELEGATES TO (CPython)
  - Objects/unicodeobject.c — PyUnicodeObject, kind, compact ascii structs,
    concatenation, intern, codecs entry points
  - Objects/bytesobject.c — PyBytesObject
  - Objects/bytearrayobject.c — mutable buffer
  - Objects/memoryobject.c — memoryview
  - Modules/_codecsmodule.c / Modules/cjkcodecs — codec registry

COMPLEXITY CARD
  - s[i] / len(s):                 O(1)  (fixed-width kind ⇒ pointer math)
  - s + t (two strings):           O(n+m) new object
  - "".join(parts):                O(total chars) typical (one allocate)
  - s.find / in / replace:         O(n·m) pattern-dependent
  - encode / decode:               O(n) plus codec tables
  - hash(str):                     O(n) first time, then cached on object

WHEN A BEATS B
  - str vs bytes: str for text; bytes for protocols / files / hashes.
  - bytearray vs repeated bytes+: bytearray for building binary buffers.
  - "".join(list) vs loop +: join wins for many pieces.
  - memoryview vs bytes slice: memoryview avoids copy on large buffers.
  - intern for many duplicate identifiers (dict keys of attribute names);
    do not intern huge unique payloads.

EDGE CASES
  - Surrogates / lone surrogates can exist in str (narrow pitfalls in codecs).
  - 'ascii' codec rejects >127; 'utf-8' is the usual default for text I/O.
  - bytes(3) → b'\\x00\\x00\\x00'; bytes([3]) → b'\\x03' — constructor overload.
  - str is not null-terminated C char*; embedded '\\0' is fine.
  - F-strings / format allocate new strings; build carefully in hot loops.
  - Changing PYTHONHASHSEED / salted hashes affect str hash values across
    processes — never persist hash() results.

SOURCE MAP
  - Objects/unicodeobject.c :: PyUnicode_New / _PyUnicode_Ready
  - Objects/unicodeobject.c :: unicode_decode_* / PyUnicode_AsEncodedString
  - Objects/unicodeobject.c :: PyUnicode_InternInPlace
  - Objects/bytesobject.c :: PyBytes_FromStringAndSize / bytes_concat
  - Objects/bytearrayobject.c :: bytearray_ass_subscript
  - Objects/memoryobject.c :: PyMemoryView_FromObject
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- str: compact Unicode (PEP 393) --------------------------------------
# CPython picks a *kind* from the max code point:
#   max <= 0x7F   → latin1/ascii compact (1 byte/code point; ascii flag)
#   max <= 0xFF   → 1-byte latin-1 kind
#   max <= 0xFFFF → 2-byte (UCS-2-ish) kind
#   else          → 4-byte (UCS-4) kind
# Indexing is O(1) because every code point uses the same width *within*
# one string object. Mixing BMP + non-BMP characters upgrades the whole
# string to a wider kind on creation — not a UTF-8 variable-width index.
ascii_s = "hello"
latin = "café"  # é = U+00E9 → still 1-byte kind
wide = "A" + "\U0001F600"  # grinning face → 4-byte kind for whole string
assert len(wide) == 2  # two code points, not UTF-8 bytes

# Indexing returns a length-1 str:
assert ascii_s[1] == "e" and isinstance(ascii_s[1], str)

# Immutability: methods return new strings.
assert ascii_s.upper() == "HELLO" and ascii_s == "hello"

# --- Intern --------------------------------------------------------------
# Identifiers used in the code object co_names etc. are typically interned.
# Explicit:
import sys

a = sys.intern("rarely_duplicated_token_xyz")
b = sys.intern("rarely_duplicated_token_xyz")
assert a is b  # same object — useful for dict-key identity speed paths
# Literal peephole / compile-time intern of short constants is common but
# NOT a language guarantee — use == for equality, `is` only for singletons
# you control (None, True, interned-by-you).

# --- bytes / bytearray ---------------------------------------------------
bs = b"abc\xff"  # immutable octets
assert bs[0] == 97 and list(bs[:2]) == [97, 98]  # index → int
ba = bytearray(b"abc")
ba[0] = 65  # mutable
assert bytes(ba) == b"Abc"

# Constructor traps:
assert bytes(3) == b"\x00\x00\x00"  # zero-filled length
assert bytes([3]) == b"\x03"  # iterable of ints
assert bytes("A", "utf-8") == b"A"  # encode form

# No implicit mix with str:
try:
    _ = b"a" + "b"  # type: ignore[operator]
except TypeError:
    pass

# --- encode / decode -----------------------------------------------------
text = "café"
raw = text.encode("utf-8")  # C3 A9 for é
assert raw == b"caf\xc3\xa9"
assert raw.decode("utf-8") == text
# errors= "strict" | "replace" | "ignore" | "backslashreplace" | …
assert b"\xff".decode("utf-8", errors="replace") == "\ufffd"

# --- join vs + in a loop -------------------------------------------------
# str and bytes are immutable → each + allocates a new object and copies.
parts = ["ab", "cd", "ef", "gh"]
# Good: compute total size (roughly), one allocate, memcpy pieces.
assert "".join(parts) == "abcdefgh"
# Binary builder:
buf = bytearray()
for chunk in (b"ab", b"cd", b"ef"):
    buf.extend(chunk)  # amortised growth, mutable buffer
assert bytes(buf) == b"abcdef"

# --- memoryview (brief) --------------------------------------------------
# Zero-copy slice over an object that exports the buffer protocol
# (bytes, bytearray, array.array, many C-extension types).
mv = memoryview(b"abcdef")
window = mv[2:5]  # no copy of underlying bytes
assert window.tobytes() == b"cde"
# For writable exporters (bytearray), memoryview can mutate in place.
wb = bytearray(b"xxxxxx")
memoryview(wb)[2:5] = b"ABC"
assert wb == bytearray(b"xxABCx")
mv.release()  # drop buffer export when done (esp. in long-lived code)

# --- Useful str APIs (dense reminders) -----------------------------------
s = "  Foo_Bar  "
assert s.strip() == "Foo_Bar"
assert s.strip().split("_") == ["Foo", "Bar"]
assert "foo" in s.lower()
assert "{}, {}".format("a", "b") == "a, b"
assert f"{3.14159:.2f}" == "3.14"
# Reminder: prefer pathlib / open(encoding=...) for files; always know
# your encoding at I/O boundaries — str is not "bytes with an accent".


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    s = "pythön"
    assert len(s) == 6
    enc = s.encode("utf-8")
    assert enc.decode("utf-8") == s
    assert "".join(["a", "b", "c"]) == "abc"
    ba = bytearray(b"hi")
    ba.extend(b"!")
    assert bytes(ba) == b"hi!"
    try:
        b"x" + "y"  # type: ignore[operator]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass
    assert bytes(2) == b"\x00\x00"
    assert bytes([2]) == b"\x02"
    mv = memoryview(bytearray(b"12345"))
    mv[1:3] = b"AB"
    assert bytes(mv) == b"1AB45"
    mv.release()
    x = sys.intern("probe_intern_token")
    y = sys.intern("probe_intern_token")
    assert x is y
    # kind upgrade intuition: ascii + non-BMP still len==code points
    emoji = "\U0001F4A9"
    assert len("a" + emoji) == 2
    print("str_bytes.py: all probes passed")


if __name__ == "__main__":
    _probes()
