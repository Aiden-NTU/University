#!/usr/bin/env python3
"""
=============================================================================
SHEET: os + sys (+ platform)                 TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x / 15.x
=============================================================================

WHAT IT IS
  - os: environment, path helpers, process identity, filesystem ops.
  - sys: interpreter state — argv, path, version_info, modules, stderr.
  - platform: normalised OS/CPU strings for diagnostics.
  - sys.getsizeof: interpreter object overhead — not deep size of graphs.

INVARIANTS
  - os.environ is a mapping proxy to the process environment; mutations
    affect the process (and children) but are not thread-documented as safe
    on all platforms for concurrent writes.
  - sys.path[0] is script dir (or '' for -c / REPL); import searches it.
  - sys.version_info is a named tuple (major, minor, micro, releaselevel, serial).
  - getsizeof(container) excludes referred objects — use recursive recipes
    or tracemalloc for allocation stories.

DELEGATES TO (CPython)
  - Modules/posixmodule.c (or nt), Lib/os.py, sysmodule.c
  - Lib/platform.py

COMPLEXITY CARD
  - environ lookup: O(1) typical
  - getsizeof: O(1) for the object header/sampled size
  - listdir/scandir: O(n) entries

WHEN A BEATS B
  - pathlib for path composition → os.path string soup (both fine; be consistent).
  - sys.version_info comparisons → parsing sys.version strings.
  - os.environ.get(k, default) → KeyError on missing with os.environ[k].

EDGE CASES
  - Empty string env values vs missing keys.
  - Windows vs POSIX path separators; os.fspath / PathLike.
  - sys.argv[0] can be '-c' or '' depending on launch.
  - getsizeof(True) may equal getsizeof(1) (interning / shared layouts).

SOURCE MAP
  - Lib/os.py :: environ, path, getpid
  - Python/sysmodule.c :: sys_getsizeof, version_info
  - Lib/platform.py :: platform, python_implementation
=============================================================================
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

# --- API walkthrough ------------------------------------------------------
#
# os.environ["KEY"] / .get / .setdefault; os.putenv is lower-level / avoid
# os.getenv(name, default=None)
# os.getcwd(); os.chdir(path); os.getpid(); os.getppid()
# os.path.join, exists, isfile, isdir, abspath, expanduser, splitext
# Prefer pathlib.Path for new code — os.path still everywhere.
#
# sys.argv: list[str]  # [0] = program
# sys.path: module search path (mutable)
# sys.version_info >= (3, 14)
# sys.platform: 'linux', 'darwin', 'win32', ...
# sys.modules, sys.stdin/out/err, sys.exit(code)
# sys.getsizeof(obj, default=...)  # bytes for *this* object only
#
# platform.platform(); platform.python_implementation() → 'CPython'
# platform.machine(); platform.system()


def _probes() -> None:
    # --- environ ---------------------------------------------------------
    key = "CPYTHON_CHEATSHEET_PROBE"
    assert key not in os.environ or True
    os.environ[key] = "1"
    assert os.getenv(key) == "1"
    assert os.environ.get(key) == "1"
    del os.environ[key]
    assert os.getenv(key) is None

    # --- path helpers ----------------------------------------------------
    cwd = os.getcwd()
    assert Path(cwd).is_dir()
    joined = os.path.join("a", "b", "c.txt")
    assert "c.txt" in joined
    assert os.path.splitext("x.py") == ("x", ".py")

    # --- sys.argv / path / version ---------------------------------------
    assert isinstance(sys.argv, list) and len(sys.argv) >= 1
    assert isinstance(sys.path, list) and all(isinstance(p, str) for p in sys.path)
    assert sys.version_info.major == 3
    assert sys.version_info >= (3, 10)  # sheet targets 3.14 but tolerate runners

    # --- platform --------------------------------------------------------
    impl = platform.python_implementation()
    assert impl == "CPython" or impl  # allow alternate if ever run elsewhere
    assert platform.system()  # non-empty
    _ = platform.platform()

    # --- getsizeof caveat ------------------------------------------------
    empty_list = []
    small = [1, 2, 3]
    # Container overhead grows, but getsizeof does NOT include the ints' sizes
    assert sys.getsizeof(small) >= sys.getsizeof(empty_list)
    # Deep size would need walking referents — see tracemalloc / pympler tips
    one = 1
    # Same small int may share representation; don't assert identity of sizes
    _ = sys.getsizeof(one)

    print(
        "os_sys_sheet: OK",
        f"version_info={tuple(sys.version_info)}",
        f"platform={sys.platform}",
        f"pid={os.getpid()}",
    )


if __name__ == "__main__":
    _probes()
