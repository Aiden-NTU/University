#!/usr/bin/env python3
"""
=============================================================================
SHEET: io (streams)                     TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 03.x text/binary I-O / buffering / in-memory streams
=============================================================================

WHAT IT IS
  - The layered stream stack behind open() and in-memory buffers:
      raw OS file  →  BufferedReader/Writer/Random  →  TextIOWrapper
  - BytesIO / StringIO: in-memory binary / text streams (no filesystem).
  - Text mode decodes/encodes Unicode; binary mode deals in bytes.
  - buffering, flush, seek/tell control when data hits the next layer.

INVARIANTS
  - Text streams: .read() → str; binary: .read() → bytes. Never mix.
  - TextIOWrapper wraps a *buffered binary* stream + encoding/errors/
    newline translation. Writing str encodes; reading decodes.
  - BufferedReader/Writer sit on RawIOBase; they coalesce small reads/
    writes into block-sized syscalls.
  - flush() pushes buffer → underlying raw/OS; close() flushes then
    releases. `with` guarantees close.
  - seek/tell: binary offsets are byte offsets. Text seek is restricted
    (usually 0, or offsets previously returned by tell() from the same
    text stream) because variable-width encodings + newline translation
    make arbitrary byte offsets unsafe.
  - BytesIO/StringIO support seek; they are fully in-memory.

DELEGATES TO (CPython)
  - Modules/_io/*.c (FileIO, Buffered*, TextIOWrapper) — C accelerator
  - Lib/_pyio.py — pure-Python reference / fallback of the same API
  - Lib/io.py — re-exports ABC + open helpers
  - Python/fileutils.c / posix — OS read/write underneath FileIO

COMPLEXITY CARD
  - small write without flush:     O(1) into buffer (syscall deferred)
  - flush / close:                 O(buffered size) + syscall
  - read(n) buffered:              amortised O(n); may pull a block
  - BytesIO/StringIO getvalue:     O(n) view/copy of buffer contents
  - seek in BytesIO:               O(1) pointer move

WHEN A BEATS B
  - binary open + decode once vs text open: binary when you own framing
    or need exact octets; text when line-oriented Unicode is the product.
  - BufferedWriter vs unbuffered raw: buffering wins for many small
    writes (fewer syscalls).
  - BytesIO vs bytearray+manual: BytesIO when you need a file-like API
    (libraries that call .read/.write/.seek).
  - StringIO vs "".join list: StringIO when incremental file-like text
    API is required; join often simpler for pure string build.

EDGE CASES
  - Text after binary without buffering/encoding → wrong layering.
  - Mixing .read() and iteration (for line in f) can surprise on buffers.
  - flush does not fsync; durability needs os.fsync(f.fileno()) on real
    files (and still has OS/disk caveats).
  - seek(0) after write on BytesIO before getvalue is optional —
    getvalue returns the whole buffer regardless of position; but
    read() depends on position — seek(0) before re-read.
  - newline='' in text csv reading disables universal newline
    translation (csv module recommends it).
  - closed stream ops → ValueError.

SOURCE MAP
  - Modules/_io/textio.c       :: TextIOWrapper
  - Modules/_io/bufferedio.c   :: BufferedReader / BufferedWriter
  - Modules/_io/fileio.c       :: FileIO (raw)
  - Modules/_io/stringio.c / bytesio.c :: in-memory
  - Lib/io.py / Lib/_pyio.py   :: public API + ABCs
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import io
import tempfile

# --- Layer cake (open) ---------------------------------------------------
# open(path, "rb", buffering=0)  → raw FileIO-ish
# open(path, "rb")               → BufferedReader over FileIO
# open(path, "r", encoding=...)  → TextIOWrapper over BufferedReader
# Default buffering: policy based on mode/device (block size heuristic).

# --- Text vs binary ------------------------------------------------------
# "rt" / "r"  → str;  "rb" → bytes
# encoding=, errors= only valid in text mode.
# Universal newlines: by default text mode translates \r\n → \n on read
# (platform-dependent write translation unless newline= set).

# --- BufferedReader / BufferedWriter -------------------------------------
# .read1 / .readinto / .peek (reader) — buffer-aware primitives.
# .write / .flush (writer). Random access → BufferedRandom.

# --- BytesIO / StringIO --------------------------------------------------
# bio = io.BytesIO(b"abc"); bio.read(); bio.seek(0); bio.getvalue()
# sio = io.StringIO("hi");  same idea for str.
# Useful as drop-in file-like for tests and parsers — no network/disk.

# --- flush / seek --------------------------------------------------------
# Always flush (or close) before another process/reader needs to see data
# on a real file. In-memory streams: flush is mostly a no-op beyond API
# compatibility, but seek still matters for subsequent read().


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    # BytesIO: binary file-like
    bio = io.BytesIO()
    n = bio.write(b"hello")
    assert n == 5
    assert bio.tell() == 5
    bio.seek(0)
    assert bio.read(2) == b"he"
    assert bio.read() == b"llo"
    bio.seek(0)
    assert bio.getvalue() == b"hello"

    # StringIO: text file-like
    sio = io.StringIO()
    sio.write("café")
    sio.seek(0)
    assert sio.read() == "café"
    assert sio.getvalue() == "café"

    # TextIOWrapper over BytesIO (encoding layer)
    raw = io.BytesIO()
    # write_through / buffering: wrap binary buffer as text
    text = io.TextIOWrapper(raw, encoding="utf-8", write_through=True)
    text.write("ü")
    text.flush()
    assert raw.getvalue() == "ü".encode("utf-8")
    text.seek(0)
    assert text.read() == "ü"
    text.close()  # also closes underlying by default

    # BufferedWriter behaviour via real temp file
    with tempfile.TemporaryFile(mode="w+b") as tf:
        # TemporaryFile is already buffered binary typically
        assert isinstance(tf, io.BufferedIOBase) or hasattr(tf, "write")
        tf.write(b"abc")
        tf.flush()
        tf.seek(0)
        assert tf.read() == b"abc"
        # overwrite via seek
        tf.seek(0)
        tf.write(b"Z")
        tf.flush()
        tf.seek(0)
        assert tf.read() == b"Zbc"

    # Text vs binary mismatch
    buf = io.BytesIO(b"x")
    try:
        buf.write("nope")  # type: ignore[arg-type]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass

    # Text seek restriction: use tell() cookie
    bio2 = io.BytesIO()
    tw = io.TextIOWrapper(bio2, encoding="utf-8", newline="\n")
    tw.write("a\nb\n")
    tw.flush()
    tw.seek(0)
    line1 = tw.readline()
    pos = tw.tell()
    _ = tw.readline()
    tw.seek(pos)
    assert tw.readline() == "b\n"
    tw.close()

    print("io_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
