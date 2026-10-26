#!/usr/bin/env python3
"""
=============================================================================
SHEET: structural pattern matching     TARGET: CPython 3.14.x
CHAPTER CROSSWALK: PEP 634 / 635 / 636 — match/case (3.10+)
=============================================================================

WHAT IT IS
  - match subject: / case pattern: — structural pattern matching.
  - Patterns deconstruct subjects (sequences, mappings, objects) and bind
    names; optional `if` guards refine matches.
  - Soft keywords: match, case, _ are keywords *only* in match statements;
    elsewhere they remain ordinary identifiers (PEP 634).

INVARIANTS
  - Cases are tried top-to-bottom; first full match wins; no fall-through.
  - Irrefutable patterns always match (bare name capture, _, and some
    combinations). An irrefutable case must be last — SyntaxError otherwise.
  - Capture names bind only on a successful full match of that case.
  - `_` is a wildcard: matches anything, binds nothing (not a variable).
  - Guards (`case pat if expr`) run only after the pattern structure
    matches; if the guard is false, matching continues to the next case.
  - `as` binds the whole successfully matched subject (or sub-pattern).
  - Class patterns use `__match_args__` (or keyword attrs) — not arbitrary
    ctor introspection.
  - Literal patterns use equality (and identity for None/True/False).

DELEGATES TO (CPython)
  - Python/compile.c — match bytecode (MATCH_*, jumps)
  - Python/ceval.c   — MATCH_SEQUENCE / MATCH_MAPPING / MATCH_CLASS / …
  - Lib/typing.py / dataclasses — __match_args__ conventions
  - PEP 634 (spec), 635 (motivation), 636 (tutorial)

COMPLEXITY CARD
  - match dispatch:    O(cases tried) structural checks until hit
  - sequence pattern:  O(k) for k fixed positions (+ rest)
  - mapping pattern:   O(k) key lookups for k pattern keys
  - class pattern:     O(k) attribute loads for k fields
  - guard:             cost of the Python expression when reached
  Not a hashtable jump table for arbitrary subjects — order matters.

WHEN A BEATS B
  - match vs isinstance ladders: match when shape/destructuring dominates;
    plain if/elif when Boolean logic / ranges dominate.
  - match vs dict dispatch: dict of callables when key→handler is flat and
    hashable; match when nested structure / guards / OR patterns matter.
  - sequence pattern vs manual unpack: pattern when branches differ by
    length/shape; unpack when one shape is guaranteed.
  - guard vs nested if in case body: guard when failure should try next
    case; body if when failure is local handling.

EDGE CASES
  - Soft keywords: `match = 1` still legal outside match statements.
  - `case _:` matches everything remaining — often a default.
  - OR patterns (`|`) share one binding set — each branch must bind the
    same names.
  - Mapping patterns ignore extra keys by default; use `**rest` to capture.
  - Sequence patterns: fixed length unless `*rest` used; strings are
    sequences of 1-chars — often match with care.
  - Value patterns (dotted names) vs capture: `case Color.RED:` compares
    to that value; `case red:` captures into name red. Use dotted names
    or `|` literals when you mean constants.
  - Class pattern positional args require `__match_args__`.
  - walrus / side effects in guards: possible but hard to read — avoid.

SOURCE MAP
  - Python/compile.c :: compiler match machinery
  - Python/ceval.c :: MATCH_* opcodes
  - PEP 634 § Patterns / soft keywords
=============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- Soft keywords -------------------------------------------------------
# These names are ordinary identifiers here:
match = "not a keyword here"
case = 42
_ = "underscore name is fine as a variable outside match"
assert match == "not a keyword here" and case == 42
del match, case, _

# --- Literal / capture / wildcard ----------------------------------------


def classify_status(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "ok"
        case 404:
            return "missing"
        case 500 | 502 | 503:
            return "upstream"
        case n if 400 <= n < 500:
            return f"client:{n}"
        case _:
            return "other"


assert classify_status(201) == "ok"
assert classify_status(404) == "missing"
assert classify_status(422) == "client:422"
assert classify_status(302) == "other"

# Capture `n` binds the subject when the case matches.
# Guard `if …` is evaluated after the structural match (here: bare capture).
# `_` matches anything, binds nothing — irrefutable default.

# --- Sequence patterns ---------------------------------------------------


def parse_cmd(argv: list[str]) -> str:
    match argv:
        case ["help"]:
            return "help"
        case ["run", name]:
            return f"run:{name}"
        case ["run", name, *flags]:
            return f"run:{name}:{flags}"
        case [cmd, *rest] if cmd.startswith("-"):
            return f"flag-cmd:{cmd}:{rest}"
        case []:
            return "empty"
        case _:
            return "unknown"


assert parse_cmd(["help"]) == "help"
assert parse_cmd(["run", "build"]) == "run:build"
assert parse_cmd(["run", "build", "-v", "-q"]) == "run:build:['-v', '-q']"
assert parse_cmd([]) == "empty"

# Nested sequences:
pair = [1, [2, 3]]
match pair:
    case [a, [b, c]]:
        assert (a, b, c) == (1, 2, 3)
    case _:
        raise AssertionError("expected nested sequence match")

# --- Mapping patterns ----------------------------------------------------


def greet(payload: dict) -> str:
    match payload:
        case {"name": str(name), "age": int(age)} if age >= 18:
            return f"adult:{name}"
        case {"name": str(name)}:
            return f"hi:{name}"
        case {"error": err}:
            return f"err:{err}"
        case _:
            return "nope"


assert greet({"name": "Ada", "age": 36}) == "adult:Ada"
assert greet({"name": "Bob"}) == "hi:Bob"
assert greet({"error": 7, "extra": True}) == "err:7"  # extra keys OK

# Capture remaining keys with **rest:
msg = {"type": "ping", "n": 1, "tag": "x"}
match msg:
    case {"type": "ping", **rest}:
        assert rest == {"n": 1, "tag": "x"}
    case _:
        raise AssertionError("mapping rest")

# --- Class patterns + __match_args__ -------------------------------------


@dataclass
class Point:
    x: float
    y: float
    # dataclass provides __match_args__ = ("x", "y") automatically


@dataclass
class Circle:
    center: Point
    r: float


def describe(shape: object) -> str:
    match shape:
        case Point(0, 0):
            return "origin"
        case Point(x, y) if x == y:
            return f"diag:{x}"
        case Point(x=x, y=0):
            return f"x-axis:{x}"
        case Circle(Point(0, 0), r):
            return f"unit-at-origin:{r}"
        case Circle(center=Point(x, y), r=r):
            return f"circle@{x},{y}:r={r}"
        case _:
            return "unknown"


assert describe(Point(0, 0)) == "origin"
assert describe(Point(2, 2)) == "diag:2"
assert describe(Point(3, 0)) == "x-axis:3"
assert describe(Circle(Point(0, 0), 1.5)) == "unit-at-origin:1.5"

# Manual __match_args__ for non-dataclass types:


class Pair:
    __match_args__ = ("left", "right")

    def __init__(self, left: int, right: int) -> None:
        self.left = left
        self.right = right


match Pair(1, 2):
    case Pair(1, r):
        assert r == 2
    case _:
        raise AssertionError("class pattern")

# --- as / OR patterns ----------------------------------------------------


def norm_color(c: object) -> str:
    match c:
        case ("rgb", r, g, b) as full if min(r, g, b) >= 0:
            return f"rgb-tuple:{full}"
        case "red" | "RED" | "Red":
            return "red"
        case ("hex", hexcode):
            return f"hex:{hexcode}"
        case _:
            return "unknown"


assert norm_color("RED") == "red"
assert norm_color(("rgb", 1, 2, 3)) == "rgb-tuple:('rgb', 1, 2, 3)"

# OR branches must bind the same names:
match 1:
    case 0 | 1 as n:
        assert n == 1
    case _:
        raise AssertionError("or-bind")

# --- Value patterns (dotted constants) -----------------------------------


class Color:
    RED = "red"
    BLUE = "blue"


def is_warm(c: object) -> bool:
    match c:
        case Color.RED:
            return True
        case Color.BLUE:
            return False
        case _:
            return False


assert is_warm(Color.RED) is True
assert is_warm("red") is True  # equality to Color.RED's value
# Bare `case RED:` would *capture* into name RED, not compare — a classic
# footgun. Use dotted names, literals, or enum.Enum members.


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    assert classify_status(503) == "upstream"
    assert parse_cmd(["run", "t", "-x"]) == "run:t:['-x']"
    assert greet({"name": "Z", "age": 10}) == "hi:Z"

    # irrefutable last
    def always(x: object) -> str:
        match x:
            case 1:
                return "one"
            case _:
                return "default"

    assert always(1) == "one" and always(9) == "default"

    # sequence with rest
    match [1, 2, 3, 4]:
        case [a, b, *mid, z]:
            assert (a, b, mid, z) == (1, 2, [3], 4)
        case _:
            raise AssertionError("star mid")

    # guard failure falls through
    def g(n: int) -> str:
        match n:
            case x if x > 10:
                return "big"
            case x if x > 5:
                return "mid"
            case _:
                return "small"

    assert g(12) == "big" and g(7) == "mid" and g(2) == "small"

    # mapping + class combo
    assert describe(Circle(Point(1, 2), 3)) == "circle@1,2:r=3"

    # soft keyword reuse still works as identifiers
    match_ = 1
    case_ = 2
    assert match_ + case_ == 3

    print("pattern_matching.py: all probes passed")


if __name__ == "__main__":
    _probes()
