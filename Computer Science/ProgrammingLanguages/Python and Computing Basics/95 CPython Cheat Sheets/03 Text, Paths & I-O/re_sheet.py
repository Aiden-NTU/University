#!/usr/bin/env python3
"""
=============================================================================
SHEET: re (regex)                       TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 03.x text search / SRE engine / safety
=============================================================================

WHAT IT IS
  - Python's standard regular-expression module over the SRE engine
    (not PCRE, not Rust regex). Patterns compile to a bytecode-ish
    program executed by a backtracking matcher (with some optimisations).
  - Prefer re.compile for repeated use; module-level functions cache a
    limited number of recent patterns but explicit compile is clearer.

INVARIANTS
  - compile(pattern, flags) → Pattern; Pattern.match/search/finditer/…
  - match anchors at start (or at pos); search scans; fullmatch whole str.
  - Groups: numbered (1…) and (?P<name>...); group(0) is whole match.
  - finditer yields Match objects lazily — preferred over findall when you
    need spans/groups (findall flattens groupy results awkwardly).
  - Flags: re.I/M/S/X/A/…; inline (?i) etc. Affect compile semantics.
  - Possessive quantifiers (*+, ++, ?+, {m,n}+) and atomic groups (?>...)
    are supported in modern CPython (3.11+) — they refuse to give back
    matched chars (can prevent some backtracking blow-ups).
  - Catastrophic backtracking is still possible on crafted patterns +
    inputs — treat untrusted regex + untrusted text as a DoS risk.

DELEGATES TO (CPython)
  - Modules/_sre/ / Modules/_sre.c — SRE engine core
  - Lib/re/__init__.py / Lib/re/_compiler.py / _parser.py / _casefix.py
  - Include/sre.h — opcodes / limits

COMPLEXITY CARD
  - compile:              O(pattern length) parse + compile
  - match typical:        O(n) for many practical patterns
  - worst-case backtrack: exponential in n for some patterns (ReDoS)
  - finditer consume all: O(n · match work)

WHEN A BEATS B
  - re.compile once vs re.search in a hot loop with same pattern string:
    compile (or rely on cache, but compile documents intent).
  - finditer vs findall: finditer for Match details; findall for simple
    list of strings/tuples.
  - possessive/atomic vs greedy+backtrack: use when you know a prefix
    must be consumed irrevocably — can make failure fail fast.
  - str.find / in / startswith: beat regex for fixed literal needles.

EDGE CASES
  - Catastrophic example class: (a+)+b against 'a'*N + 'c' — huge
    backtracking. Prefer possessive (a++)+b or atomic (?>a+)+b, or
    rewrite without nested quantifiers on overlapping tokens.
  - Zero-width matches: finditer can advance one char to avoid loops —
    know your pattern.
  - bytes patterns require bytes subjects; str with str — no mix.
  - re.ASCII vs Unicode word/digit classes under ASCII flag.
  - Last group wins for repeated groups; use findall carefully.
  - Never feed untrusted patterns to compile on a hot server without
    timeouts/limits — pattern itself can be hostile.

SOURCE MAP
  - Lib/re/_parser.py / _compiler.py   :: parse + compile to SRE code
  - Modules/_sre/*.c                   :: sre_match / backtracking VM
  - Lib/re/__init__.py                 :: compile, flags, cache
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import re

# --- compile / flags -----------------------------------------------------
# pat = re.compile(r"\d+", re.ASCII)  # or re.A
# Inline: re.compile(r"(?i)hello")
# VERBOSE (re.X): whitespace/comments inside pattern for readability.

# --- groups --------------------------------------------------------------
# m.group(1), m.group("name"), m.groups(), m.groupdict()
# (?:...) non-capturing; (?P<name>...) named; (?P=name) backref.

# --- finditer ------------------------------------------------------------
# for m in pat.finditer(text): use m.span(), m.group(...)

# --- possessive / atomic (3.11+) ----------------------------------------
# a++   possessive plus — match as many as possible, never give back
# (?>...) atomic group — commit to the group's match
# These eliminate some backtracking paths; they are NOT a full ReDoS
# vaccine for every pattern shape.

# --- catastrophic backtracking warning -----------------------------------
# Nested quantifiers on the same character class are classic landmines.
# Demo kept tiny in probes (N small) — do not scale N up casually.


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    pat = re.compile(r"(?P<word>\w+)@(?P<domain>[\w.-]+)", re.ASCII)
    m = pat.search("mail user@example.com end")
    assert m is not None
    assert m.group("word") == "user" and m.group("domain") == "example.com"
    assert m.group(0) == "user@example.com"
    assert m.groups() == ("user", "example.com")

    # match vs search vs fullmatch
    assert re.match(r"\d+", "123abc").group(0) == "123"  # type: ignore[union-attr]
    assert re.match(r"\d+", "abc123") is None
    assert re.search(r"\d+", "abc123").group(0) == "123"  # type: ignore[union-attr]
    assert re.fullmatch(r"\d+", "123") and re.fullmatch(r"\d+", "123a") is None

    # finditer
    spans = [m.span() for m in re.finditer(r"[a-z]+", "one TWO three", re.I)]
    assert spans == [(0, 3), (4, 7), (8, 13)]

    # flags: IGNORECASE / MULTILINE / DOTALL
    assert re.search(r"^b", "a\nb", re.M)
    assert re.search(r"a.b", "a\nb", re.S)

    # possessive: a++b succeeds; classic greedy also would, but possessive
    # refuses to backtrack — a++c fails cleanly on 'aaab'
    assert re.fullmatch(r"a++b", "aaab")
    assert re.fullmatch(r"a++c", "aaab") is None

    # atomic group equivalent spirit
    assert re.fullmatch(r"(?>a+)b", "aaab")
    assert re.fullmatch(r"(?>a+)c", "aaab") is None

    # Tiny catastrophic-shape demo: keep N small — this is a WARNING probe,
    # not a load test. Nested quantifiers on 'a' before a failing 'b'.
    n = 20
    evil_pat = re.compile(r"(a+)+b")
    # Matching success is fine; failure against nearly-matching input is
    # where backtracking explodes. We only assert *correctness* here.
    assert evil_pat.fullmatch("a" * n + "b")
    assert evil_pat.fullmatch("a" * n + "c") is None
    # Prefer possessive rewrite for the same intent when applicable:
    safe = re.compile(r"(a++)+b")
    assert safe.fullmatch("a" * n + "b")
    assert safe.fullmatch("a" * n + "c") is None

    # bytes vs str
    assert re.search(rb"\d+", b"x12y").group(0) == b"12"  # type: ignore[union-attr]
    try:
        re.search(r"\d+", b"12")  # type: ignore[arg-type]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass

    print("re_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
