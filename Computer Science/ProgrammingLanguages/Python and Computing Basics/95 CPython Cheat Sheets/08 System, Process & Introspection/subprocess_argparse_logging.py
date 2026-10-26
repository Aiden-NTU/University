#!/usr/bin/env python3
"""
=============================================================================
SHEET: subprocess + argparse + logging       TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x stdlib
=============================================================================

WHAT IT IS
  - subprocess.run: spawn children with argv lists (shell=False default
    mindset); capture_output / check / timeout.
  - argparse: declarative CLI parsers → Namespace.
  - logging: basicConfig, loggers, handlers, formatters — library code
    should log; apps configure handlers.

INVARIANTS
  - Prefer argv sequences over shell=True (injection + quoting hell).
  - CompletedProcess: .returncode, .stdout, .stderr (bytes or str if text=True).
  - argparse: parse_args(argv=None) uses sys.argv[1:]; test with explicit lists.
  - logging hierarchy: child loggers propagate to parents unless disabled.
  - Probes spawn sys.executable only — offline, no network.

DELEGATES TO (CPython)
  - Lib/subprocess.py → _posixsubprocess / Windows CreateProcess
  - Lib/argparse.py
  - Lib/logging/__init__.py, handlers.py

COMPLEXITY CARD
  - process spawn: heavy vs function call
  - capture_output: buffers all output — bad for huge streams (use Popen pipes)

WHEN A BEATS B
  - subprocess.run → os.system / os.popen (safer, richer).
  - shell=False + list → shell=True + string.
  - logging → print for libraries (callers configure).
  - argparse → manual sys.argv slicing for non-trivial CLIs.

EDGE CASES
  - check=True raises CalledProcessError on non-zero.
  - timeout raises TimeoutExpired (may leave child — kill handling matters).
  - basicConfig is a no-op if root already has handlers.
  - FileHandler paths need care in concurrent processes.

SOURCE MAP
  - Lib/subprocess.py :: run, Popen, CompletedProcess
  - Lib/argparse.py :: ArgumentParser
  - Lib/logging/__init__.py :: basicConfig, getLogger
=============================================================================
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

# --- API walkthrough ------------------------------------------------------
#
# subprocess.run(
#     args, *, input=None, capture_output=False, timeout=None,
#     check=False, text=False / encoding=..., env=None, cwd=None, shell=False)
# → CompletedProcess
# Also: DEVNULL, PIPE, STDOUT; Popen for streaming.
#
# parser = argparse.ArgumentParser(prog=..., description=...)
# parser.add_argument("-v", "--verbose", action="store_true")
# parser.add_argument("path", type=Path)
# ns = parser.parse_args(["-v", "x"])  # ns.verbose, ns.path
#
# logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s",
#                     handlers=[logging.StreamHandler(sys.stderr)])
# log = logging.getLogger(__name__)
# log.info("..."); log.exception("with traceback")


def _probes() -> None:
    # --- subprocess.run shell=False --------------------------------------
    cp = subprocess.run(
        [sys.executable, "-c", "print('hi', end='')"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    assert cp.returncode == 0
    assert cp.stdout == "hi"
    assert cp.stderr == ""

    bad = subprocess.run(
        [sys.executable, "-c", "raise SystemExit(3)"],
        capture_output=True,
    )
    assert bad.returncode == 3

    try:
        subprocess.run(
            [sys.executable, "-c", "raise SystemExit(7)"],
            check=True,
            capture_output=True,
        )
        raise AssertionError("expected CalledProcessError")
    except subprocess.CalledProcessError as e:
        assert e.returncode == 7

    # --- argparse --------------------------------------------------------
    parser = argparse.ArgumentParser(prog="probe")
    parser.add_argument("-n", "--count", type=int, default=1)
    parser.add_argument("name")
    ns = parser.parse_args(["-n", "3", "widget"])
    assert ns.count == 3 and ns.name == "widget"

    # --- logging ---------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "probe.log"
        logger = logging.getLogger("cheatsheet.probe")
        logger.handlers.clear()
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(
            logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        )
        logger.addHandler(fh)
        logger.info("hello %s", "world")
        for h in list(logger.handlers):
            h.close()
            logger.removeHandler(h)
        text = log_path.read_text(encoding="utf-8")
        assert "INFO:cheatsheet.probe:hello world" in text

    # basicConfig demo (may no-op if root configured — still callable)
    logging.basicConfig(level=logging.WARNING)

    print("subprocess_argparse_logging: OK")


if __name__ == "__main__":
    _probes()
