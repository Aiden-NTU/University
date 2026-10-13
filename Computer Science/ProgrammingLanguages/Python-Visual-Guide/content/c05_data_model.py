"""Chapter 5 - Classes and the data model: syntax is dunder calls, attribute lookup and the MRO, repr,
equality and hashing, container and iteration protocols, operators, properties, dataclasses, ABCs and
protocols, enums."""
from generator import canvas as C
from content.kit import (L, W, callout, code, flow, go, memory, pipe, practice, repl, section, stamp, sub,
                         table, title_block, tree, two_ways)

ORDER = 5
NUM = 5
TITLE = "Classes and the data model"
SHORT = "Data model"
SLUG = "Data-model"
ACCENT = C.PURPLE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def title_page(ch):
    title_block(ch, 5, TITLE, "every piece of syntax is a method call you can define", ACCENT)
    f = ch.flow(top=190)
    f.p("You've written classes with `__init__` and methods. The step up is the {B:data model}: Python turns "
        "almost every piece of syntax into a call to a specially named (\"dunder\") method. Define the "
        "method, and your objects work with the syntax, the built-ins and the whole standard library.",
        14, gap=10)
    pipe(f, ["len(shelf)", ("type(shelf).__len__(shelf)", C.PURPLE), "your method runs", "an int"], mono=True,
         size=10)
    table(f, ["you write", "Python calls", "you write", "Python calls"], [
        ["`a + b`", "`a.__add__(b)`", "`len(x)`", "`x.__len__()`"],
        ["`a == b`", "`a.__eq__(b)`", "`x[k]`", "`x.__getitem__(k)`"],
        ["`a < b`", "`a.__lt__(b)`", "`k in x`", "`x.__contains__(k)`"],
        ["`for v in x`", "`iter(x)` → `x.__iter__()`", "`bool(x)`, `if x:`", "`x.__bool__()` or `__len__`"],
        ["`repr(x)`", "`x.__repr__()`", "`f(...)` on an object", "`x.__call__(...)`"],
        ["`hash(x)`", "`x.__hash__()`", "`with x:`", "`__enter__`, `__exit__` (Ch 6)"],
    ], widths=[1, 1.5, 1.1, 1.6], size=10.5)
    callout(f, "idea", "This is why `len` is a function and not a method: `len(x)` works on any object whose "
            "class defines `__len__`. It's an interface, not inheritance. Ask \"which protocol does this "
            "syntax use?\" and you can make your own types feel built in.")


def lookup(ch):
    f = flow(ch)
    sec(f, "Where attributes live", room=450)
    f.p("An instance has its own dict of attributes. Methods live on the {B:class}. `obj.name` looks in the "
        "instance first, then the class, then its base classes in order:", 13.5, gap=8)
    code(f, """
        class Member:
            limit = 3                          # class attribute: shared by all members

            def __init__(self, name):
                self.name = name               # instance attribute
                self.loans = []

            def can_borrow(self):
                return len(self.loans) < self.limit

        ana = Member("ana")
        print(vars(ana), "limit" in vars(ana), ana.limit)
        print(ana.can_borrow(), Member.can_borrow(ana))     # the same call
    """)
    memory(f, [("names", ["ana", "Member"])],
           {"I": dict(t="Member instance __dict__", v="name='ana'  loans=[]", col=0, row=0, color=C.BLUE),
            "K": dict(t="class Member __dict__", v="limit=3  __init__  can_borrow", col=0, row=1.3,
                      color=C.PURPLE)},
           [("ana", "I"), ("Member", "K")], height=110, obj_x=(L + 175, L + 380))
    f.p("`ana.can_borrow()` finds the function on the class and passes `ana` as `self`. That's all a method "
        "is: a function stored on the class, with the instance filled in as its first argument.", 13.5, gap=8)
    code(f, """
        ana.limit = 10                  # creates an INSTANCE attribute that hides the class one
        ben = Member("ben")
        print(ana.limit, ben.limit, Member.limit)
    """, expect="10 3 3")
    callout(f, "trap", "A mutable {B:class} attribute (`loans = []` at class level) is shared by every instance, "
            "the same bug as the mutable default argument. Create per-object state in `__init__`.")


def repr_eq(ch):
    f = flow(ch)
    sec(f, "repr, equality and hashing", room=430)
    f.p("A class you write gets the default `repr` (`<Book object at 0x7f...>`) and identity equality (two "
        "books with the same title are not `==`). For a {B:value} type you want both fixed:", 13.5, gap=8)
    code(f, """
        class Book:
            def __init__(self, title, year):
                self.title, self.year = title, year

            def __repr__(self):
                return f"Book({self.title!r}, {self.year})"     # looks like the code to rebuild it

            def __eq__(self, other):
                if not isinstance(other, Book):
                    return NotImplemented                       # let the other side try
                return (self.title, self.year) == (other.title, other.year)

            def __hash__(self):
                return hash((self.title, self.year))            # equal objects MUST hash equal

        a, b = Book("Dune", 1965), Book("Dune", 1965)
        print(a, a == b, a is b, len({a, b}))
    """)
    callout(f, "trap", "Defining `__eq__` without `__hash__` makes instances {B:unhashable} (Python sets "
            "`__hash__ = None` to protect you). And only hash fields that never change; mutate a key after "
            "putting it in a set and the set can't find it again.")
    sub(f, "dataclasses write all of that for you", ACCENT)
    two_ways(f, ("by hand", """
        class Point:
            def __init__(self, x, y):
                self.x, self.y = x, y
            def __repr__(self):
                x, y = self.x, self.y
                return f"Point({x=}, {y=})"
            def __eq__(self, o):
                return (self.x, self.y) == (o.x, o.y)
            def __hash__(self):
                return hash((self.x, self.y))
        print(Point(1, 2) == Point(1, 2), Point(1, 2))
    """), ("@dataclass(frozen=True)", """
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class Point:
            x: int
            y: int





        print(Point(1, 2) == Point(1, 2), Point(1, 2))
    """), verdict=[("lines to maintain", 1, 5), ("control", 5, 4)])
    table(f, ["dataclass option", "gives you"], [
        ["`@dataclass`", "`__init__`, `__repr__`, `__eq__` from the annotated fields"],
        ["`frozen=True`", "immutable fields (assignment raises), and `__hash__`"],
        ["`order=True`", "`<`, `<=`, `>`, `>=` comparing fields in order (so `sorted` works)"],
        ["`field(default_factory=list)`", "a fresh mutable default per instance (no shared-list bug)"],
        ["`slots=True`", "`__slots__`: smaller instances, no accidental new attributes"],
    ], widths=[1.9, 3])


def protocols(ch):
    f = flow(ch)
    sec(f, "Container and iteration protocols", room=430)
    f.p("Implement a few dunders and your object works with `len`, `in`, indexing, slicing, `for`, "
        "`sorted`, `list()`, unpacking, `sum`... none of which knows your class exists:", 13.5, gap=8)
    code(f, """
        class Shelf:
            def __init__(self, titles=()):
                self._titles = list(titles)

            def __len__(self):
                return len(self._titles)

            def __getitem__(self, i):                      # handles ints AND slices
                got = self._titles[i]
                return Shelf(got) if isinstance(i, slice) else got

            def __iter__(self):
                yield from self._titles

            def __contains__(self, title):
                return title.lower() in (t.lower() for t in self._titles)

            def __repr__(self):
                return f"Shelf({self._titles})"

        s = Shelf(["Dune", "Emma", "Ubik"])
        print(len(s), s[0], s[1:], "emma" in s, sorted(s, reverse=True))
        first, *rest = s
        print(first, rest, bool(Shelf()))
    """, notes={9: "a slice returns a Shelf", 15: "case-insensitive"})
    callout(f, "why", "`bool(Shelf())` is `False` without a `__bool__` method: Python falls back to `__len__`, "
            "and zero length means false. Protocols have sensible fallbacks: with only `__getitem__`, `for` "
            "and `in` still work by trying indexes 0, 1, 2... until `IndexError`.")


def operators(ch):
    f = flow(ch)
    sec(f, "Operators: a money type", room=440)
    f.p("Arithmetic operators are two-sided. For `a + b` Python tries `a.__add__(b)`; if that returns "
        "`NotImplemented`, it tries `b.__radd__(a)`. That's what makes `sum()` (which starts from `0`) work:",
        13.5, gap=8)
    code(f, """
        from dataclasses import dataclass
        from decimal import Decimal
        from functools import total_ordering

        @total_ordering
        @dataclass(frozen=True)
        class Money:
            pence: int

            def __add__(self, other):
                if isinstance(other, Money):
                    return Money(self.pence + other.pence)
                return NotImplemented

            def __radd__(self, other):          # 0 + Money, from sum()
                return self if other == 0 else NotImplemented

            def __mul__(self, k):
                if isinstance(k, (int, float, Decimal)):
                    return Money(round(self.pence * k))
                return NotImplemented
            __rmul__ = __mul__

            def __lt__(self, other):
                return self.pence < other.pence

            def __str__(self):
                return f"£{self.pence / 100:.2f}"

        fines = [Money(150), Money(275), Money(20)]
        print(sum(fines), 3 * Money(150), max(fines), Money(1) >= Money(1))
    """, notes={5: "fills in <=, >, >= from < and =="})
    code(f, """
        Money(100) + 5
    """, raises=TypeError, numbers=False)
    callout(f, "rule", "Return `NotImplemented` (don't raise) when you don't recognise the other operand. "
            "Python then tries the reflected method and only raises `TypeError` if both sides give up, with a "
            "clear message. Money is stored in integer pence: never in a `float` (Ch 11).")


def properties(ch):
    f = flow(ch)
    sec(f, "Properties: attributes with rules", room=420)
    f.p("A `@property` looks like an attribute to the caller but runs code. Use it to {B:protect an "
        "invariant} (a rule that must always hold) or compute a value, without changing how callers "
        "write `obj.days`:", 13.5, gap=8)
    code(f, """
        class Loan:
            MAX_DAYS = 28

            def __init__(self, title, days=14):
                self.title = title
                self.days = days                # goes through the setter below

            @property
            def days(self):
                return self._days

            @days.setter
            def days(self, value):
                if not 1 <= value <= self.MAX_DAYS:
                    raise ValueError(f"days must be 1..{self.MAX_DAYS}, got {value}")
                self._days = value

            @property
            def weeks(self):                    # computed, read-only
                return self.days / 7

        loan = Loan("Dune")
        loan.days = 21
        print(loan.days, loan.weeks)
        loan.days = 90
    """, raises=ValueError, notes={6: "validated even in __init__"})
    callout(f, "other", "Java and C# write `getDays()`/`setDays()` up front, in case validation is needed "
            "later. Python starts with a plain attribute and swaps in a property only when needed, and "
            "callers don't change. The leading underscore in `_days` means \"internal\" by convention only.")


def inheritance(ch):
    f = flow(ch)
    sec(f, "Inheritance, composition and the MRO", room=450)
    f.p("Inheritance says \"is a\"; composition says \"has a\". Prefer composition unless the subclass truly "
        "can be used everywhere the base class can. When you do inherit, `super()` calls the next class in "
        "the {B:method resolution order} (MRO), a single line Python computes from the class tree:", 13.5, gap=8)
    tree(f, {"o": ("object", 0.5, 0), "i": ("Item", 0.5, 1), "b": ("Borrowable", 0.25, 2),
             "s": ("Searchable", 0.75, 2), "k": ("Book", 0.5, 3)},
         [("o", "i"), ("i", "b"), ("i", "s"), ("b", "k"), ("s", "k")], h=170)
    code(f, """
        class Item:
            def describe(self):
                return ["item"]

        class Borrowable(Item):
            def describe(self):
                return ["borrowable"] + super().describe()

        class Searchable(Item):
            def describe(self):
                return ["searchable"] + super().describe()

        class Book(Borrowable, Searchable):
            pass

        print(" → ".join(c.__name__ for c in Book.__mro__))
        print(Book().describe())
    """, notes={7: "next in the MRO, not 'my parent'"})
    f.p("`super()` in `Borrowable` called `Searchable`, a class it has never heard of, because that's next "
        "in `Book`'s MRO. Every class runs exactly once, even in a diamond.", 13.5, gap=8)
    sub(f, "Interfaces: ABCs and duck typing", ACCENT, room=300)
    code(f, """
        from abc import ABC, abstractmethod
        from typing import Protocol

        class Notifier(ABC):                    # nominal: subclasses must implement send
            @abstractmethod
            def send(self, to, text): ...

        class CanSend(Protocol):                # structural: anything with a send() matches
            def send(self, to, text): ...

        class Email(Notifier):
            def send(self, to, text):
                return f"mail {to}: {text}"

        print(Email().send("ana", "due"))
        Notifier()
    """, raises=TypeError)


def enums(ch):
    f = flow(ch)
    sec(f, "Enums: a fixed set of named values", room=300)
    code(f, """
        from enum import Enum, auto

        class Status(Enum):
            ON_SHELF = auto()
            ON_LOAN = auto()
            LOST = auto()

        s = Status.ON_LOAN
        print(s, s.name, s.value, s is Status["ON_LOAN"], [m.name for m in Status])
        match s:
            case Status.ON_LOAN | Status.LOST:
                print("not available")
    """)
    callout(f, "rule", "Use an `Enum` instead of magic strings (`\"on_loan\"`) or numbers: typos become "
            "`AttributeError`s, editors autocomplete, and `match` reads clearly. `IntEnum`/`StrEnum` when the "
            "values must also behave like ints or strings (e.g. stored in SQLite).")
    table(f, ["need", "reach for"], [
        ["a bag of fields with behaviour", "a class; `@dataclass` if it's mostly data"],
        ["an immutable record", "`@dataclass(frozen=True)` or `typing.NamedTuple`"],
        ["a fixed set of choices", "`enum.Enum`"],
        ["\"anything with a `.send()`\"", "duck typing; `typing.Protocol` to document it"],
        ["shared behaviour with enforced methods", "`abc.ABC` with `@abstractmethod`"],
    ], widths=[1.6, 2.4])


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 5)
    stamp(f, [
        (6, "Classes with single and multiple inheritance (C3 MRO, cooperative `super()`); duck typing via "
            "protocols of dunder methods; ABCs and `typing.Protocol` for explicit interfaces; properties for "
            "invariants; dataclasses for records; enums for choices."),
        (5, "User types plug into built-in syntax by implementing protocols: `__len__`, `__getitem__`, "
            "`__iter__`, `__contains__`, `__eq__`/`__hash__`, arithmetic with `NotImplemented`."),
    ])
    callout(f, "deep", "Vault notes: {b:9.3} Instance attributes, class attributes, and lookup · {b:9.4} Methods "
            "are functions transformed by descriptor access · {b:9.7} Representation methods · {b:9.8} Equality, "
            "hashing, and immutable value objects · {b:9.10} Composition and delegation · {b:9.11} Polymorphism "
            "and protocols · {b:9.12} Special methods and operator protocols · {b:9.13} Cooperative binary "
            "operations and NotImplemented · {b:9.14} Multiple inheritance and MRO · {b:9.15} Descriptors · "
            "{b:9.17} Slots.")


def build(ch):
    title_page(ch)
    lookup(ch)
    repr_eq(ch)
    protocols(ch)
    operators(ch)
    properties(ch)
    inheritance(ch)
    enums(ch)
    finish(ch)
