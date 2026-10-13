EXERCISES = [
    dict(
        id="5.1", kind="build", title="A 2D vector that feels built in",
        task="""
        Write a class `Vec(x, y)` so that:

        - `Vec(1, 2) + Vec(3, 4) == Vec(4, 6)`, and `-` works the same way
        - `Vec(1, 2) * 3 == 3 * Vec(1, 2) == Vec(3, 6)`
        - `abs(Vec(3, 4)) == 5.0`, `bool(Vec(0, 0))` is `False`
        - `repr(Vec(1, 2)) == "Vec(1, 2)"`, `x, y = Vec(1, 2)` unpacks
        - vectors can be set members and dict keys (immutable: assigning `v.x = 5` raises an error)
        - `Vec(1, 2) + 5` raises `TypeError` (return `NotImplemented` for unknown operands)
        """,
        stub='''
        class Vec:
            def __init__(self, x, y):
                self.x, self.y = x, y
        ''',
        tests='''
        import random

        def test_ops_random(m):
            rng = random.Random(8)
            for _ in range(200):
                a, b, c, d, k = (rng.randint(-50, 50) for _ in range(5))
                equal(m.Vec(a, b) + m.Vec(c, d), m.Vec(a + c, b + d), "addition")
                equal(m.Vec(a, b) - m.Vec(c, d), m.Vec(a - c, b - d), "subtraction")
                equal(m.Vec(a, b) * k, m.Vec(a * k, b * k), "v * k")
                equal(k * m.Vec(a, b), m.Vec(a * k, b * k), "k * v")

        def test_protocols(m):
            V = m.Vec
            equal(abs(V(3, 4)), 5.0, "abs")
            check(not V(0, 0) and V(0, 1), "bool")
            equal(repr(V(1, 2)), "Vec(1, 2)", "repr")
            x, y = V(1, 2)
            equal((x, y), (1, 2), "unpacking")
            equal(len({V(1, 2), V(1, 2), V(2, 1)}), 2, "hashable, equal vectors collapse in a set")
            check(V(1, 2) != (1, 2), "a Vec is not equal to a tuple")
            raises(TypeError, lambda: V(1, 2) + 5)
            v = V(1, 2)
            try:
                v.x = 5
            except (AttributeError, TypeError):
                pass
            else:
                raise AssertionError("v.x = 5 should raise: vectors are immutable")
        ''',
        alts={
            "frozen dataclass": ('''
                from dataclasses import dataclass
                import math

                @dataclass(frozen=True)
                class Vec:
                    x: float
                    y: float

                    def __add__(self, o):
                        return Vec(self.x + o.x, self.y + o.y) if isinstance(o, Vec) else NotImplemented

                    def __sub__(self, o):
                        return Vec(self.x - o.x, self.y - o.y) if isinstance(o, Vec) else NotImplemented

                    def __mul__(self, k):
                        return Vec(self.x * k, self.y * k) if isinstance(k, (int, float)) else NotImplemented
                    __rmul__ = __mul__

                    def __abs__(self):
                        return math.hypot(self.x, self.y)

                    def __bool__(self):
                        return bool(self.x or self.y)

                    def __iter__(self):
                        yield self.x
                        yield self.y

                    def __repr__(self):
                        return f"Vec({self.x}, {self.y})"
            ''', "frozen=True gives immutability, __eq__ and __hash__; you add only the maths."),
            "NamedTuple": ('''
                import math
                from typing import NamedTuple

                class Vec(NamedTuple):
                    x: float
                    y: float

                    def __add__(self, o):
                        return Vec(self.x + o.x, self.y + o.y) if isinstance(o, Vec) else NotImplemented

                    def __sub__(self, o):
                        return Vec(self.x - o.x, self.y - o.y) if isinstance(o, Vec) else NotImplemented

                    def __mul__(self, k):
                        return Vec(self.x * k, self.y * k) if isinstance(k, (int, float)) else NotImplemented
                    __rmul__ = __mul__

                    def __abs__(self):
                        return math.hypot(*self)

                    def __bool__(self):
                        return bool(self.x or self.y)

                    def __eq__(self, o):
                        return isinstance(o, Vec) and tuple(self) == tuple(o)

                    def __ne__(self, o):
                        return not self == o

                    __hash__ = tuple.__hash__

                    def __repr__(self):
                        return f"Vec({self.x}, {self.y})"
            ''', "A NamedTuple is immutable and iterable for free, but it IS a tuple, so you must override "
                 "== and != (tuple defines its own __ne__) and restore __hash__ to stop Vec(1, 2) == (1, 2). "
                 "Inheritance brings baggage."),
        },
    ),
    dict(
        id="5.2", kind="fix", title="Shared state and a vanishing set member",
        task="""
        Two bugs in `Member`:

        1. Every member seems to share the same list of loans.
        2. After defining `__eq__`, members can no longer go in a set (`TypeError: unhashable`).
           Members are equal when their `member_id` is equal; `member_id` never changes.

        Fix both without changing how the class is used.
        """,
        stub='''
        class Member:
            loans = []

            def __init__(self, member_id, name):
                self.member_id = member_id
                self.name = name

            def borrow(self, title):
                self.loans.append(title)

            def __eq__(self, other):
                return isinstance(other, Member) and self.member_id == other.member_id
        ''',
        tests='''
        def test_separate_loans(m):
            a, b = m.Member(1, "ana"), m.Member(2, "ben")
            a.borrow("Dune")
            equal(b.loans, [], "ben's loans")
            equal(a.loans, ["Dune"], "ana's loans")

        def test_hashable(m):
            a, a2, b = m.Member(1, "ana"), m.Member(1, "Ana R."), m.Member(2, "ben")
            equal(len({a, a2, b}), 2, "set of members by id")
            check(a == a2 and a != b, "equality by id")
        ''',
        alts={
            "init + hash on the id": ('''
                class Member:
                    def __init__(self, member_id, name):
                        self.member_id = member_id
                        self.name = name
                        self.loans = []

                    def borrow(self, title):
                        self.loans.append(title)

                    def __eq__(self, other):
                        return isinstance(other, Member) and self.member_id == other.member_id

                    def __hash__(self):
                        return hash(self.member_id)
            ''', "Hash exactly what __eq__ compares (and only fields that never change)."),
            "dataclass with eq on id only": ('''
                from dataclasses import dataclass, field

                @dataclass(unsafe_hash=True)
                class Member:
                    member_id: int
                    name: str = field(compare=False)
                    loans: list = field(default_factory=list, compare=False)

                    def borrow(self, title):
                        self.loans.append(title)
            ''', "compare=False excludes fields from __eq__ and __hash__; default_factory gives each member "
                 "its own list. unsafe_hash is 'unsafe' only if you then mutate member_id."),
        },
    ),
    dict(
        id="5.3", kind="build", title="A container with slicing",
        task="""
        Write a class `Playlist` holding song titles in order:

        - `Playlist(songs=())`, `len(p)`, `p[i]` (negative indexes too), `p[1:3]` returns a **Playlist**
        - `"x" in p`, iteration in order, `p + q` gives a new Playlist (neither input changes)
        - `p == q` when they have the same songs in the same order; `repr(p) == "Playlist(['a', 'b'])"`
        - `p.shuffled(seed)` returns a new shuffled Playlist using `random.Random(seed)`; `p` is unchanged
        """,
        stub='''
        class Playlist:
            ...
        ''',
        tests='''
        import random

        def test_random(m):
            for xs in rand_lists(100, seed=6):
                songs = [f"s{x}" for x in xs]
                p = m.Playlist(songs)
                equal(len(p), len(songs), "len")
                equal(list(p), songs, "iteration")
                if songs:
                    equal(p[-1], songs[-1], "negative index")
                    i = len(songs) // 2
                    check(isinstance(p[i:], m.Playlist), "a slice is a Playlist")
                    equal(list(p[1:i]), songs[1:i], "slice contents")
                    check(songs[0] in p, "in")

        def test_add_eq_repr_shuffle(m):
            a, b = m.Playlist(["a", "b"]), m.Playlist(["c"])
            c = a + b
            equal(list(c), ["a", "b", "c"], "concatenation")
            equal(list(a), ["a", "b"], "inputs unchanged")
            equal(repr(a), "Playlist(['a', 'b'])", "repr")
            check(a == m.Playlist(["a", "b"]) and a != m.Playlist(["b", "a"]), "equality is ordered")
            big = m.Playlist([str(i) for i in range(20)])
            s = big.shuffled(1)
            check(sorted(s, key=int) == list(big) and list(s) != list(big), "shuffled is a permutation")
            equal(list(big.shuffled(1)), list(s), "same seed, same order")
            equal(list(big), [str(i) for i in range(20)], "original unchanged")
            raises(IndexError, lambda: m.Playlist([])[0])
        ''',
        alts={
            "wrap a list": ('''
                import random

                class Playlist:
                    def __init__(self, songs=()):
                        self._songs = list(songs)

                    def __len__(self):
                        return len(self._songs)

                    def __getitem__(self, i):
                        if isinstance(i, slice):
                            return Playlist(self._songs[i])
                        return self._songs[i]

                    def __iter__(self):
                        return iter(self._songs)

                    def __contains__(self, song):
                        return song in self._songs

                    def __add__(self, other):
                        if not isinstance(other, Playlist):
                            return NotImplemented
                        return Playlist(self._songs + other._songs)

                    def __eq__(self, other):
                        return isinstance(other, Playlist) and self._songs == other._songs

                    def __repr__(self):
                        return f"Playlist({self._songs!r})"

                    def shuffled(self, seed):
                        songs = list(self._songs)
                        random.Random(seed).shuffle(songs)
                        return Playlist(songs)
            ''', "Composition: a Playlist *has* a list. Only the operations you choose are exposed."),
            "subclass collections.abc.Sequence": ('''
                import random
                from collections.abc import Sequence

                class Playlist(Sequence):
                    def __init__(self, songs=()):
                        self._songs = list(songs)

                    def __len__(self):
                        return len(self._songs)

                    def __getitem__(self, i):
                        return Playlist(self._songs[i]) if isinstance(i, slice) else self._songs[i]

                    def __add__(self, other):
                        return Playlist([*self, *other]) if isinstance(other, Playlist) else NotImplemented

                    def __eq__(self, other):
                        return isinstance(other, Playlist) and list(self) == list(other)

                    def __repr__(self):
                        return f"Playlist({self._songs!r})"

                    def shuffled(self, seed):
                        songs = list(self)
                        random.Random(seed).shuffle(songs)
                        return Playlist(songs)
            ''', "The Sequence ABC provides __iter__, __contains__, index(), count() and reversed() from "
                 "just __len__ and __getitem__ (mixin methods)."),
        },
    ),
    dict(
        id="5.4", kind="build", title="Temperatures with rules",
        task="""
        Write a class `Temp` storing a temperature:

        - `Temp(celsius)`; properties `celsius` and `fahrenheit` (F = C × 9/5 + 32), **both settable**
        - setting either below absolute zero (−273.15 °C) raises `ValueError`, including in `__init__`
        - temperatures compare with `==`, `<`, `<=`, `>`, `>=` by value (`functools.total_ordering` is allowed)
        - `str(Temp(21.5)) == "21.5°C"`
        """,
        stub='''
        class Temp:
            def __init__(self, celsius):
                self.celsius = celsius
        ''',
        tests='''
        import random

        def test_props(m):
            t = m.Temp(100)
            equal(round(t.fahrenheit, 6), 212.0, "boiling point in F")
            t.fahrenheit = 32
            equal(round(t.celsius, 6), 0.0, "setting F updates C")
            equal(str(m.Temp(21.5)), "21.5°C", "str")
            raises(ValueError, m.Temp, -300)
            raises(ValueError, setattr, t, "fahrenheit", -500)
            raises(ValueError, setattr, t, "celsius", -273.16)

        def test_ordering_random(m):
            rng = random.Random(4)
            vals = [rng.uniform(-273, 500) for _ in range(60)]
            temps = [m.Temp(v) for v in vals]
            equal([t.celsius for t in sorted(temps)], sorted(vals), "sorted by value")
            a, b = m.Temp(1), m.Temp(2)
            check(a < b and a <= b and b > a and b >= a and a != b and a == m.Temp(1), "comparisons")
        ''',
        alts={
            "properties + total_ordering": ('''
                from functools import total_ordering

                ABS_ZERO = -273.15

                @total_ordering
                class Temp:
                    def __init__(self, celsius):
                        self.celsius = celsius

                    @property
                    def celsius(self):
                        return self._c

                    @celsius.setter
                    def celsius(self, value):
                        if value < ABS_ZERO:
                            raise ValueError(f"{value} °C is below absolute zero")
                        self._c = value

                    @property
                    def fahrenheit(self):
                        return self._c * 9 / 5 + 32

                    @fahrenheit.setter
                    def fahrenheit(self, value):
                        self.celsius = (value - 32) * 5 / 9

                    def __eq__(self, other):
                        return isinstance(other, Temp) and self._c == other._c

                    def __lt__(self, other):
                        return self._c < other._c if isinstance(other, Temp) else NotImplemented

                    def __hash__(self):
                        return hash(self._c)

                    def __str__(self):
                        return f"{self._c}°C"
            ''', "One stored value (Celsius); Fahrenheit is derived, and its setter reuses the Celsius "
                 "validation, so the rule lives in exactly one place."),
        },
    ),
    dict(
        id="5.5", kind="explore", title="Who defines this method?",
        task="""
        Using only introspection (`__mro__`, `vars()`/`__dict__`), write:

        - `mro_names(cls)`: the class names in method resolution order, e.g. for `bool`:
          `["bool", "int", "object"]`
        - `defined_by(cls, attr)`: the **name** of the first class in the MRO whose own namespace
          contains `attr`, or `None`. `defined_by(bool, "__add__")` is `"int"`.

        Then try it on `collections.OrderedDict`, `io.StringIO`, and your own classes from this chapter.
        """,
        stub='''
        def mro_names(cls):
            ...

        def defined_by(cls, attr):
            ...
        ''',
        tests='''
        import collections, io

        def test_builtins(m):
            equal(m.mro_names(bool), ["bool", "int", "object"], "bool's MRO")
            equal(m.defined_by(bool, "__add__"), "int", "bool + comes from int")
            equal(m.defined_by(bool, "__repr__"), "bool", "bool has its own repr")
            equal(m.defined_by(int, "nope"), None, "missing attribute")
            equal(m.defined_by(collections.OrderedDict, "get"), "dict", "OrderedDict.get")

        def test_diamond(m):
            class A:
                def hi(self): ...
            class B(A): ...
            class C(A):
                def hi(self): ...
            class D(B, C): ...
            equal(m.mro_names(D), ["D", "B", "C", "A", "object"], "diamond MRO")
            equal(m.defined_by(D, "hi"), "C", "C comes before A")
        ''',
        alts={
            "walk __mro__": ('''
                def mro_names(cls):
                    return [c.__name__ for c in cls.__mro__]

                def defined_by(cls, attr):
                    for c in cls.__mro__:
                        if attr in vars(c):
                            return c.__name__
                    return None
            ''', "This is exactly what attribute lookup does for a class attribute: walk the MRO and stop "
                 "at the first namespace containing the name."),
            "next() with a default": ('''
                def mro_names(cls):
                    return [c.__name__ for c in cls.mro()]

                def defined_by(cls, attr):
                    return next((c.__name__ for c in cls.mro() if attr in c.__dict__), None)
            ''', "cls.mro() returns the same order as a list; next(generator, default) is a compact search."),
        },
    ),
    dict(
        id="5.6", kind="project", title="Mini-project: a library catalogue",
        task="""
        Model a catalogue with the tools from this chapter:

        - `Status`: an `Enum` with `ON_SHELF`, `ON_LOAN`, `LOST`
        - `Book`: an **ordered** dataclass with fields `author`, `title`, `isbn`, `status`
          (default `Status.ON_SHELF`); sorting books orders them by author, then title
        - `Catalogue`: `add(book)` (`ValueError` for a duplicate isbn), `cat[isbn]` (`KeyError` if
          missing), `len(cat)`, `isbn in cat`, iteration yields books **sorted**,
          `cat.available()` returns the sorted list of books on the shelf,
          `cat.search(text)` returns sorted books whose title or author contains `text`, case-insensitively
        """,
        stub='''
        from enum import Enum
        from dataclasses import dataclass
        ''',
        tests='''
        def make(m):
            cat = m.Catalogue()
            cat.add(m.Book("Herbert", "Dune", "111"))
            cat.add(m.Book("Austen", "Emma", "222", m.Status.ON_LOAN))
            cat.add(m.Book("Austen", "Persuasion", "333"))
            cat.add(m.Book("Dick", "Ubik", "444", m.Status.LOST))
            return cat

        def test_catalogue(m):
            cat = make(m)
            equal(len(cat), 4, "len")
            equal([b.title for b in cat], ["Emma", "Persuasion", "Ubik", "Dune"], "iteration is sorted")
            equal(cat["111"].title, "Dune", "lookup by isbn")
            check("222" in cat and "999" not in cat, "in")
            raises(KeyError, lambda: cat["999"])
            raises(ValueError, cat.add, m.Book("X", "Y", "111"))
            equal([b.title for b in cat.available()], ["Persuasion", "Dune"], "available")
            equal([b.title for b in cat.search("AUST")], ["Emma", "Persuasion"], "search by author")
            equal([b.title for b in cat.search("ub")], ["Ubik"], "search by title")

        def test_types(m):
            check(issubclass(m.Status, __import__("enum").Enum), "Status is an Enum")
            check(m.Book("A", "B", "1") < m.Book("A", "C", "0"), "books order by author then title")
            equal(m.Book("A", "B", "1").status, m.Status.ON_SHELF, "default status")
        ''',
        alts={
            "dataclass(order) + dict": ('''
                from dataclasses import dataclass, field
                from enum import Enum, auto

                class Status(Enum):
                    ON_SHELF = auto()
                    ON_LOAN = auto()
                    LOST = auto()

                @dataclass(order=True)
                class Book:
                    author: str
                    title: str
                    isbn: str = field(compare=False)
                    status: Status = field(default=Status.ON_SHELF, compare=False)

                class Catalogue:
                    def __init__(self):
                        self._books = {}

                    def add(self, book):
                        if book.isbn in self._books:
                            raise ValueError(f"duplicate isbn {book.isbn}")
                        self._books[book.isbn] = book

                    def __getitem__(self, isbn):
                        return self._books[isbn]

                    def __len__(self):
                        return len(self._books)

                    def __contains__(self, isbn):
                        return isbn in self._books

                    def __iter__(self):
                        return iter(sorted(self._books.values()))

                    def available(self):
                        return [b for b in self if b.status is Status.ON_SHELF]

                    def search(self, text):
                        t = text.casefold()
                        return [b for b in self if t in b.title.casefold() or t in b.author.casefold()]
            ''', "compare=False keeps isbn and status out of the ordering (and out of ==, which may or may "
                 "not be what you want: two copies of Dune with different isbns now compare equal)."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="class A:\n    xs = []\na, b = A(), A()\na.xs.append(1)\nprint(b.xs)", why="xs is a class attribute shared by every instance."),
    dict(kind="predict", code="class P:\n    def __eq__(self, o):\n        return True\nprint(P() == 1, end=' ')\ntry:\n    {P()}\nexcept TypeError:\n    print('unhashable')"),
    dict(kind="predict", code="class S:\n    def __len__(self):\n        return 0\nprint(bool(S()), 'yes' if S() else 'no')"),
    dict(kind="predict", code="class A:\n    def f(self): return 'A'\nclass B(A):\n    def f(self): return 'B' + super().f()\nclass C(B): pass\nprint(C().f())"),
    dict(kind="predict", code="from dataclasses import dataclass\n@dataclass\nclass P:\n    x: int\n    y: int = 0\nprint(P(1), P(1) == P(1, 0))"),
    dict(kind="recall", q="What should __add__ return when it doesn't support the other operand's type?", a=["NotImplemented", "return NotImplemented"]),
    dict(kind="recall", q="Which dunder method does `for x in obj` call first?", a=["__iter__", "iter"]),
    dict(kind="recall", q="Which functools decorator fills in <=, > and >= from __eq__ and __lt__?", a=["total_ordering", "functools.total_ordering"]),
]
