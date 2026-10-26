#!/usr/bin/env python3
"""
=============================================================================
SHEET: pathlib                          TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 03.x paths / 08.x filesystem / vs os.path
=============================================================================

WHAT IT IS
  - Object-oriented filesystem paths. PurePath subclasses do pure string
    path algebra (no I/O). Path / concrete subclasses (PosixPath,
    WindowsPath) add os.stat, open, glob, read_text, etc.
  - The `/` operator joins path segments (like os.path.join, but typed).
  - Preferred modern API over stringly-typed os.path for most new code.

INVARIANTS
  - PurePath never touches the disk; Path methods that need the FS do.
  - Path.cwd() / Path.home() are concrete; PurePath('a')/'b' stays pure.
  - resolve() makes absolute + normalises symlinks (may fail if missing
    on some platforms/options); absolute() only prepends cwd — no symlink
    resolution and does not require the path to exist.
  - Equality compares the path *representation* under the flavour rules
    (case-folding on Windows flavours), not inode identity.
  - glob / rglob yield Path objects; patterns are not full regex.
  - read_text / write_text are convenience wrappers around open(); they
    open, read/write, close — fine for whole-file loads, not streams.

DELEGATES TO (CPython)
  - Lib/pathlib/__init__.py / Lib/pathlib/_local.py — Path public API
  - Lib/pathlib/_abc.py — PurePath / Path abstract flavour logic
  - Modules/posixmodule.c / nt — underlying os.stat, listdir, open
  - Lib/os.py :: os.path (ntpath / posixpath) — still used under the hood
    for some joins/norms; pathlib is the OO façade

COMPLEXITY CARD (amortised unless noted)
  - Path / PurePath construction:     O(segments) string work
  - p / "child":                      O(1) new Path object
  - resolve / absolute:               O(depth) + syscalls for resolve
  - iterdir:                          O(n) directory entries
  - glob / rglob:                     O(tree size matched); rglob walks
  - read_text / write_bytes:          O(file size) + I/O
  - exists / is_file / is_dir:        one stat (or equivalent) each

WHEN A BEATS B
  - pathlib.Path vs os.path.join strings: Path for readability, `/` join,
    methods as verbs; os.path when you already have string APIs or need
    the absolute thinnest glue in a tiny script.
  - resolve() vs absolute(): resolve when you need canonical real path
    (symlinks flattened); absolute when you only need "not relative"
    without requiring existence / following links.
  - read_text vs open().read: read_text for whole small files; open for
    streaming, custom buffering, or binary+text mix control.
  - glob vs os.walk + fnmatch: glob for simple patterns; walk when you
    need full control of prune/order/error handling.

EDGE CASES
  - Missing target: resolve(strict=True) → OSError; strict=False may still
    resolve parents and append the missing tail (3.6+ behaviour).
  - Trailing slash / dot segments: PurePath normalises for == in flavour-
    specific ways — inspect .parts when surprised.
  - Windows vs Posix: PureWindowsPath vs PurePosixPath differ on drive,
    UNC, case; on Linux you usually get PosixPath.
  - Path.open inherits open() encoding rules (text vs binary).
  - write_text(newline=...) / encoding= matter for cross-platform text.
  - Relative glob patterns are relative to the Path you call .glob on,
    not necessarily cwd.

SOURCE MAP
  - Lib/pathlib/_local.py          :: Path, cwd, home, open helpers
  - Lib/pathlib/_abc.py            :: PurePath.__truediv__, with_segments
  - Lib/pathlib/_abc.py            :: resolve / absolute / glob patterns
  - Modules/posixmodule.c          :: os_stat / os_listdir_impl
  - Lib/os.py / Lib/posixpath.py   :: join, normpath (legacy twin API)
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import os
import tempfile
from pathlib import Path, PurePath, PurePosixPath

# --- PurePath vs Path ----------------------------------------------------
# PurePath: algebra only (join, parts, suffix, with_name, …). No .exists().
# Path: concrete — binds to the local OS flavour and can touch the FS.
pure = PurePosixPath("/var") / "log" / "app.log"
assert pure.parts == ("/", "var", "log", "app.log")
assert pure.suffix == ".log" and pure.stem == "app"
assert pure.with_suffix(".txt").name == "app.txt"
# PurePosixPath is pure algebra — not a concrete FS path class.
assert type(pure) is PurePosixPath
assert not isinstance(pure, Path)

# `/` join: right operand may be str or another pure path segment sequence.
# Absolute right-hand side *replaces* (like os.path.join):
assert PurePosixPath("rel") / "/abs" == PurePosixPath("/abs")

# --- Path: concrete FS ops -----------------------------------------------
# Prefer Path for scripts; keep PurePath for cross-platform path *data*
# that you serialise without a real disk (e.g. zip member names as Posix).

# --- resolve vs absolute -------------------------------------------------
# absolute(): make absolute using cwd; do NOT require existence; do NOT
#   fully resolve symlinks the way resolve does.
# resolve(strict=...): walk symlinks toward a canonical path.

# --- glob / rglob --------------------------------------------------------
# Patterns: *, ?, [..] — NOT regex. ** is recursive in glob("**/x") /
# rglob("*.py"). Yields Paths lazily.

# --- read_text / write_bytes / write_text --------------------------------
# Convenience: open → read/write → close. Encoding defaults for text follow
# open()'s rules (locale/UTF-8 depending on version & platform; prefer
# encoding="utf-8" explicitly for portable text).

# --- vs os.path ----------------------------------------------------------
# os.path.join("a", "b")  ≈  Path("a") / "b"   (then str(path) if needed)
# os.path.exists(p)       ≈  Path(p).exists()
# os.path.abspath(p)      ≈  Path(p).absolute()   (not the same as resolve)
# Many APIs still accept path-like (os.PathLike) — Path implements __fspath__.


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    # Pure join + parts
    p = PurePosixPath("docs") / "ch03" / "notes.md"
    assert str(p) == "docs/ch03/notes.md"
    assert p.name == "notes.md" and p.parent.as_posix() == "docs/ch03"

    # Absolute RHS replaces
    assert PurePosixPath("a") / PurePosixPath("/b/c") == PurePosixPath("/b/c")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        sub = root / "data"
        sub.mkdir()
        f = sub / "hello.txt"
        f.write_text("café\n", encoding="utf-8")
        assert f.read_text(encoding="utf-8") == "café\n"
        f.write_bytes(b"\x00\x01\xff")
        assert f.read_bytes() == b"\x00\x01\xff"
        f.write_text("x", encoding="utf-8")

        # absolute vs resolve (temp path exists)
        abs_p = f.absolute()
        assert abs_p.is_absolute()
        res = f.resolve(strict=True)
        assert res.exists() and res.is_file()

        # glob
        (sub / "a.py").write_text("# a\n", encoding="utf-8")
        (sub / "b.txt").write_text("b\n", encoding="utf-8")
        names = sorted(p.name for p in sub.glob("*.py"))
        assert names == ["a.py"]
        deep = sub / "nested"
        deep.mkdir()
        (deep / "c.py").write_text("# c\n", encoding="utf-8")
        rnames = sorted(p.name for p in sub.rglob("*.py"))
        assert rnames == ["a.py", "c.py"]

        # PathLike for os APIs
        assert os.path.isfile(f)
        assert os.fspath(f) == str(f)

        # missing + resolve(strict=True)
        missing = root / "nope"
        try:
            missing.resolve(strict=True)
            raise AssertionError("expected OSError")
        except OSError:
            pass
        # absolute does not require existence
        assert missing.absolute().is_absolute()

    # Flavour-independent PurePath factory still yields a pure class
    assert isinstance(PurePath("x"), PurePath)
    print("pathlib_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
