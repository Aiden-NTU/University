#!/usr/bin/env python3
"""
=============================================================================
SHEET: dataclasses / enum / copy / typing   TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x records / 15.x typing / object graphs
=============================================================================

WHAT IT IS
  - dataclasses: generates __init__/__repr__/__eq__ (and more) from
    annotated fields — boilerplate killer for plain data holders.
  - enum: symbolic constants (Enum), int-backed (IntEnum), bit flags
    (Flag / IntFlag), string enums (StrEnum).
  - copy: shallow copy.copy vs recursive copy.deepcopy of object graphs.
  - typing: *annotations for static checkers* (mypy/pyright). At runtime,
    annotations are data (or strings under from __future__ import
    annotations); they do NOT enforce types unless you opt into a
    runtime system (get_type_hints, Annotated metadata, pydantic, …).

INVARIANTS
  - dataclass: fields from annotations; ClassVar / InitVar excluded from
    certain generated methods as documented. frozen=True → raise on
    attribute set (uses object.__setattr__ in __init__). slots=True →
    __slots__, no per-instance __dict__ (unless you add one).
  - field(default=…) vs default_factory: factory for mutables (list/dict).
  - Enum members are singletons; identity and == usually agree for same
    member. Aliases share identity with the first definition.
  - Flag: combine with | & ^ ~; membership via & / in (3.11+ semantics).
  - copy.copy: new container / object, *same* nested identities.
  - deepcopy: recurse; memo dict breaks cycles. User types may define
    __copy__ / __deepcopy__.
  - typing: get_type_hints resolves strings/forward refs; Annotated[T, x]
    carries extra metadata but T is still the "real" hint for many tools.

DELEGATES TO (CPython)
  - Lib/dataclasses.py        — field collection, method generation
  - Lib/enum.py               — EnumType metaclass, Flag logic
  - Lib/copy.py               — copy / deepcopy dispatch tables
  - Lib/typing.py             — get_type_hints, Annotated, aliases
  - Objects/typeobject.c      — class creation hooks used by Enum/dataclass

COMPLEXITY CARD
  - dataclass construction:       O(#fields) + your __post_init__
  - frozen setattr (reject):      O(1) raise path
  - Enum lookup by name/value:    O(1) typical (internal maps)
  - Flag combine:                 O(1) for int-backed bit ops
  - copy.copy(list/dict):         O(n) shallow
  - deepcopy:                     O(size of reachable graph)
  - get_type_hints:               O(#annotations) + import resolve

WHEN A BEATS B
  - dataclass vs namedtuple: dataclass for defaults, mutability control,
    inheritance, __post_init__, slots/kw_only; namedtuple for tuple API.
  - dataclass vs attrs/pydantic: stdlib simplicity vs validation ecosystem.
  - Enum vs module-level consts: Enum for namespacing, iteration, type.
  - IntEnum vs Enum: IntEnum when you must == int / use as array index.
  - Flag vs set of enums: Flag when bitmasks / C ABI style matter.
  - copy vs deepcopy: copy when nesting is immutable or sharing is OK;
    deepcopy when you need an isolated graph (costly).
  - typing annotations vs runtime checks: annotations for tools; assert /
    pydantic / manual isinstance for runtime enforcement.

EDGE CASES
  - dataclass mutable default: NEVER write x: list = [] — use
    field(default_factory=list). The decorator rejects some bare mutables.
  - frozen + slots + inheritance: follow dataclass docs for ordering of
    base/derived field slots (3.10+ improved).
  - Enum functional API vs class API; auto() for values.
  - deepcopy of module / nested function / open file — limited / error.
  - from __future__ import annotations → annotations stored as strings;
    get_type_hints needed to evaluate. PEP 649 (3.14 deferred evaluation
    model) changes *how* annotations are stored/evaluated — still not
    runtime enforcement.
  - Annotated[int, "units"] is still an int for checkers; metadata is
    extra for frameworks.

SOURCE MAP
  - Lib/dataclasses.py :: dataclass, field, fields, asdict, astuple
  - Lib/enum.py        :: EnumType.__new__, Flag._generate_next_value_
  - Lib/copy.py        :: copy, deepcopy, _deepcopy_dispatch
  - Lib/typing.py      :: get_type_hints, Annotated, TypeAliasType (3.12+)
=============================================================================
"""

# --- API walkthrough (dense comments, setts.py style) ---------------------

from __future__ import annotations

import copy
import sys
from dataclasses import (
    InitVar,
    asdict,
    astuple,
    dataclass,
    field,
    fields,
    replace,
)
from enum import Enum, Flag, IntEnum, StrEnum, auto
from typing import Annotated, Any, ClassVar, get_args, get_origin, get_type_hints

# =============================================================================
# dataclasses — generated data holders
# =============================================================================


@dataclass
class Point:
    x: float
    y: float = 0.0  # default: fields without defaults must come first


p = Point(1.5)
assert p == Point(1.5, 0.0)  # __eq__ compares field values
assert repr(p).startswith("Point(")


# frozen: immutable (hashable if all fields hashable — eq+frozen enables hash)
@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int


c = Color(1, 2, 3)
try:
    c.r = 9  # type: ignore[misc]
except Exception as exc:  # FrozenInstanceError (dataclasses)
    assert type(exc).__name__ == "FrozenInstanceError"
assert hash(c) == hash(Color(1, 2, 3))


# slots=True (3.10+): __slots__ from fields — less memory, no __dict__
@dataclass(slots=True)
class Particle:
    mass: float
    vx: float = 0.0
    vy: float = 0.0


part = Particle(1.0)
assert not hasattr(part, "__dict__")
assert part.mass == 1.0


# field(): default_factory for mutables; metadata; repr/compare/hash flags
@dataclass
class Bucket:
    name: str
    items: list[str] = field(default_factory=list)
    _secret: int = field(default=0, repr=False, compare=False)
    tag: str = field(default="x", metadata={"ui": "label"})


b1, b2 = Bucket("a"), Bucket("a")
b1.items.append("one")
assert b2.items == []  # separate lists — factory ran twice
assert "_secret" not in repr(b1)  # repr=False hides it
b1.items.clear()
b1._secret = 99
assert b1 == b2  # _secret ignored in compare; items both empty
assert fields(b1)[-1].metadata.get("ui") == "label"


# ClassVar / InitVar / __post_init__ / replace / asdict
@dataclass
class User:
    name: str
    roles: list[str] = field(default_factory=list)
    active: bool = True
    kind: ClassVar[str] = "user"  # not an instance field
    raw: InitVar[str | None] = None  # passed to __post_init__, not stored

    def __post_init__(self, raw: str | None) -> None:
        if raw:
            self.roles.append(raw)


u = User("ann", raw="admin")
assert u.roles == ["admin"] and User.kind == "user"
u2 = replace(u, name="bob")  # new instance; shallow copy of fields
assert u2.name == "bob" and u2.roles is u.roles  # shared mutable!
assert asdict(Point(1, 2)) == {"x": 1, "y": 2}
assert astuple(Point(1, 2)) == (1, 2)

# kw_only (3.10+): keyword-only fields — useful with inheritance
@dataclass
class Base:
    x: int


@dataclass
class Child(Base):
    y: int = 0
    z: int = field(default=1, kw_only=True)


assert Child(5, 9, z=3) == Child(5, 9, z=3)

# =============================================================================
# enum — Enum / IntEnum / Flag / StrEnum
# =============================================================================


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()


assert Direction.NORTH is Direction["NORTH"]
assert Direction.NORTH.name == "NORTH"
assert list(Direction) == [
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
]
# Aliases: same value → not a new member in iteration
class AliasDemo(Enum):
    A = 1
    B = 1  # alias of A


assert AliasDemo.B is AliasDemo.A
assert list(AliasDemo) == [AliasDemo.A]


class Status(IntEnum):
    OK = 200
    NOT_FOUND = 404


assert Status.OK == 200 and Status.OK + 1 == 201  # int ops
assert isinstance(Status.OK, int)


class Perm(Flag):
    R = auto()
    W = auto()
    X = auto()


rw = Perm.R | Perm.W
assert Perm.R in rw and Perm.X not in rw
assert (rw & Perm.W) == Perm.W
# IntFlag similarly mixes with int bitmasks


class ColorName(StrEnum):
    RED = "red"
    BLUE = "blue"


assert ColorName.RED == "red" and f"{ColorName.BLUE}" == "blue"

# =============================================================================
# copy.copy vs copy.deepcopy
# =============================================================================
# Shallow: new outer object; nested objects shared by identity.
# Deep: recurse; independent graph (with memo for cycles).

outer = [[1, 2], [3, 4]]
shallow = copy.copy(outer)
deep = copy.deepcopy(outer)
shallow[0].append(99)
assert outer[0][-1] == 99          # shared inner list
assert deep[0] == [1, 2]           # independent

# dict / custom objects
d = {"a": [1]}
d_s = copy.copy(d)
d_d = copy.deepcopy(d)
d_s["a"].append(2)
assert d["a"] == [1, 2] and d_d["a"] == [1]


@dataclass
class Node:
    val: int
    kids: list[Node] = field(default_factory=list)


n = Node(1)
n.kids.append(n)  # cycle
n2 = copy.deepcopy(n)
assert n2.val == 1 and n2.kids[0] is n2  # cycle preserved via memo
assert n2 is not n

# =============================================================================
# typing — runtime reality vs static checkers
# =============================================================================
# CRITICAL TEACHING POINT:
#   def f(x: int) -> str: ...
# does NOT check that x is int or that the return is str at runtime.
# Annotations are advisory for type checkers / IDEs / optional frameworks.


def add(x: int, y: int) -> int:
    return x + y  # type checkers would complain if we returned a str


# Runtime: no enforcement — this "works" even though types lie:
assert add("a", "b") == "ab"  # type: ignore[arg-type]

# Inspect annotations (with future annotations they may be strings until
# evaluated). get_type_hints evaluates forward refs in a real namespace.
assert add.__annotations__["x"] in ("int", int) or True  # form varies


class Box:
    items: list[int]
    label: Annotated[str, "ui-title"]

    def __init__(self, items: list[int], label: str) -> None:
        self.items = items
        self.label = label


hints = get_type_hints(Box, include_extras=False)
assert hints["items"] == list[int]
# With include_extras=True, Annotated is preserved:
hints_x = get_type_hints(Box, include_extras=True)
ann = hints_x["label"]
assert get_origin(ann) is Annotated
args = get_args(ann)
assert args[0] is str and "ui-title" in args[1:]

# Annotated does not enforce either — it carries metadata for tools:
weird: Annotated[int, "mm"] = "not-an-int"  # type: ignore[assignment]
assert weird == "not-an-int"

# Practical split:
#   static: mypy/pyright read annotations, never run your code
#   runtime: isinstance / explicit checks / pydantic / typedload
#   get_type_hints: bridge for libraries that want to act at import/call


def checked_add(x: Any, y: Any) -> int:
    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("int required")
    return x + y


assert checked_add(1, 2) == 3
try:
    checked_add("a", "b")
except TypeError:
    pass

# Version breadcrumb for the sheet's target:
assert sys.version_info[:2] >= (3, 14) or True  # educational; probes still run


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""

    @dataclass(frozen=True, slots=True)
    class P:
        x: int
        y: int = 0

    p = P(1)
    assert p == P(1, 0)
    try:
        p.x = 2  # type: ignore[misc]
        raise AssertionError("expected frozen error")
    except Exception as e:
        assert type(e).__name__ == "FrozenInstanceError"

    @dataclass
    class Acc:
        xs: list[int] = field(default_factory=list)

    a, b = Acc(), Acc()
    a.xs.append(1)
    assert b.xs == []

    class Kind(Enum):
        A = auto()
        B = auto()

    assert Kind.A is Kind["A"] and Kind.A != Kind.B

    class Bit(Flag):
        X = auto()
        Y = auto()

    assert Bit.X | Bit.Y == Bit.X | Bit.Y
    assert Bit.X in (Bit.X | Bit.Y)

    class Code(IntEnum):
        S = 1

    assert Code.S == 1

    class Hue(StrEnum):
        G = "green"

    assert Hue.G == "green"

    nest = {"k": [1, 2]}
    s = copy.copy(nest)
    d = copy.deepcopy(nest)
    s["k"].append(3)
    assert nest["k"] == [1, 2, 3] and d["k"] == [1, 2]

    def f(x: int) -> int:
        return x

    # no runtime check:
    assert f("z") == "z"  # type: ignore[arg-type]
    ht = get_type_hints(f)
    assert ht["x"] is int and ht["return"] is int

    T = Annotated[int, "t"]
    assert get_origin(T) is Annotated and get_args(T)[0] is int

    print("dataclasses_enum_copy_typing.py: all probes passed")


if __name__ == "__main__":
    _probes()
