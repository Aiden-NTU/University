"""Chapter 4 - Functions in depth: functions as objects, parameter kinds, the default trap, scope (LEGB),
closures, higher-order functions, decorators, generators, type hints."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, W, callout, code, flow, go, memory, pipe, practice, repl, section, seq, stamp, sub,
                         table, title_block, two_ways)

ORDER = 4
NUM = 4
TITLE = "Functions, closures and generators"
SHORT = "Functions"
SLUG = "Functions"
ACCENT = C.BLUE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def signature_picture(f):
    parts = [("def show(", None, None, 0), ("a, b", C.BLUE, "positional-only", 0), (", /, ", None, None, 0),
             ("c, d=0", C.GREEN, "positional or keyword", 1), (", ", None, None, 0),
             ("*args", C.ORANGE, "extra positionals: a tuple", 2), (", ", None, None, 0),
             ("e, f=1", C.PURPLE, "keyword-only", 0), (", ", None, None, 0),
             ("**kw", C.RED, "extra keywords: a dict", 1), ("):", None, None, 0)]
    size = 14
    cw = F.width("x", F.MONO, size)
    total = sum(len(p[0]) for p in parts) * cw
    y = f.reserve(110)
    pg = f.pg
    x = L + (W - total) / 2
    for s, col, label, row in parts:
        wd = len(s) * cw
        if col:
            pg.rect(x - 2, y, wd + 4, 24, col, 1.0, fillcolor=C.LIGHT[col], r=4)
            ly = y + 34 + row * 22
            pg.line(x + wd / 2, y + 24, x + wd / 2, ly, col, 0.9)
            pg.note(x + wd / 2, ly, label, col, 13, align="center")
        pg.text(x, y + 4, s, size, C.INK, F.MONO)
        x += wd


def legb_picture(f):
    y = f.reserve(200)
    pg = f.pg
    layers = [("Built-in", "print, len, range, ValueError", C.GREY),
              ("Global (the module)", "RATE, helper", C.GREEN),
              ("Enclosing (outer function)", "count", C.ORANGE),
              ("Local (current function)", "x, parameters", C.BLUE)]
    for k, (name, eg, col) in enumerate(layers):
        inset = k * 26
        pg.rect(L + inset, y + inset * 0.8, W - 160 - 2 * inset, 190 - inset * 1.6, col, 1.3,
                fillcolor=C.LIGHT.get(col, "#f4f5f7"), r=8)
        pg.text(L + inset + 10, y + inset * 0.8 + 5, name, 11, col, F.BOLD)
        right = L + W - 160 - inset
        ex = L + inset + 10 + F.width(name, F.BOLD, 11) + 10
        if ex + F.width(eg, F.MONO, 9.5) < right - 8:
            pg.text(ex, y + inset * 0.8 + 6, eg, 9.5, C.INK, F.MONO)
        else:
            pg.text(L + inset + 10, y + inset * 0.8 + 24, eg, 9.5, C.INK, F.MONO)
    ax = L + W - 135
    pg.arrow(ax, y + 160, ax, y + 20, C.RED, 1.6, head=7)
    pg.note(ax + 12, y + 70, "look up a name:\ninside first,\nthen outwards;\nfirst match wins", C.RED, 14, w=120)


def title_page(ch):
    title_block(ch, 4, TITLE, "a function is an object you can pass, store, wrap and pause", ACCENT)
    f = ch.flow(top=190)
    f.p("You know how to define and call functions. This chapter is about what a function {B:is}: an object, "
        "created when `def` runs, bound to a name like any other value. Everything else follows: passing "
        "functions to functions, functions that remember things, functions that wrap other functions, "
        "and functions that pause halfway.", 14, gap=10)
    code(f, """
        def shout(text):
            return text.upper() + "!"

        say = shout                     # another name, same object
        actions = [str.lower, shout, len]
        print(say("hi"), [act("Hey") for act in actions])
        print(type(shout).__name__, shout.__name__, shout.__code__.co_varnames)
    """)
    memory(f, [("names", ["shout", "say", "actions"])],
           {"F": dict(t="function", v="shout(text)", col=0, row=0, color=C.BLUE),
            "A": dict(t="list", slots=["0", "1", "2"], col=0, row=1.6, color=C.ORANGE),
            "lo": dict(t="method", v="str.lower", x=L + 395, row=1, color=C.GREY),
            "ln": dict(t="builtin", v="len", x=L + 395, row=2.2, color=C.GREY)},
           [("shout", "F"), ("say", "F"), ("actions", "A"), ("A.0", "lo"), ("A.1", "F"), ("A.2", "ln")],
           height=135)
    callout(f, "idea", "`def` is an assignment statement: it builds a function object (code, defaults, name, "
            "docstring) and binds it to a name. Calling is a separate step, written with `()`.")


def parameters(ch):
    f = flow(ch)
    sec(f, "Parameter kinds: one signature, five zones")
    f.p("A signature can have up to five zones, always in this order. The `/` and `*` markers are walls: "
        "parameters before `/` can't be passed by name; parameters after `*` (or `*args`) must be:", 13.5, gap=8)
    signature_picture(f)
    code(f, """
        def show(a, b, /, c, d=0, *args, e, f=1, **kw):
            print(a, b, c, d, args, e, f, kw)

        show(1, 2, 3, e=5)
        show(1, 2, c=3, d=4, e=5, colour="red")
        show(1, 2, 3, 4, 98, 99, e=5, f=6)
    """)
    code(f, """
        show(1, b=2, c=3, e=5)
    """, raises=TypeError, numbers=False)
    table(f, ["you want...", "write", "why"], [
        ["a flag that must be named", "`def save(path, *, overwrite=False)`",
         "`save(p, True)` is unreadable; this forces `overwrite=True`"],
        ["any number of values", "`def total(*nums)`", "`nums` is a tuple"],
        ["to forward everything", "`def wrapper(*args, **kwargs)`", "decorators (later this chapter)"],
        ["to spread a list into a call", "`f(*items)`, `f(**options)`", "the call-side mirror of `*args`"],
        ["names you may rename later", "`def area(w, h, /)`", "callers can't depend on the names"],
    ], widths=[1.6, 2.4, 2.6])


def defaults(ch):
    f = flow(ch)
    sec(f, "The default-value trap", room=420)
    f.p("Defaults are evaluated {B:once}, when `def` runs, and stored on the function object. A mutable default "
        "is therefore shared by every call that doesn't pass that argument:", 13.5, gap=8)
    code(f, """
        def add_loan(title, loans=[]):
            loans.append(title)
            return loans

        print(add_loan("Dune"))
        print(add_loan("Emma"))           # surprise
        print(add_loan.__defaults__)      # the one shared list
    """, notes={6: "Dune is still there"})
    memory(f, [("names", ["add_loan"])],
           {"F": dict(t="function add_loan", slots=["defaults"], col=0, row=0, color=C.BLUE),
            "D": dict(t="list (created once, at def time)", v="['Dune', 'Emma']", col=1, row=0, color=C.RED)},
           [("add_loan", "F"), ("F.0", "D")], height=55, obj_x=(L + 170, L + 300))
    f.p("The fix is the `None` sentinel: make the default immutable, create the list inside the call.", 13.5, gap=6)
    code(f, """
        def add_loan(title, loans=None):
            if loans is None:
                loans = []                # a new list on every call
            loans.append(title)
            return loans

        print(add_loan("Dune"), add_loan("Emma"))
    """, expect="['Dune'] ['Emma']")
    callout(f, "why", "This isn't a bug in Python; it falls out of \"`def` runs once\". The same rule makes "
            "`def stamp(t=time.time())` record the time the module loaded, not the time of the call.")


def scope(ch):
    f = flow(ch)
    sec(f, "Scope: where Python looks a name up", room=420)
    f.p("When code uses a name, Python searches four scopes in order, {B:L}ocal, {B:E}nclosing, {B:G}lobal, "
        "{B:B}uilt-in, and takes the first match:", 13.5, gap=8)
    legb_picture(f)
    f.p("Which scope a name belongs to is decided at {B:compile} time: if a function assigns to a name "
        "anywhere in its body, that name is local everywhere in that body. That produces this classic error:", 13.5,
        gap=8)
    code(f, """
        count = 0

        def bump():
            count += 1        # assignment makes count local, so it's read before being set

        bump()
    """, raises=UnboundLocalError)
    code(f, """
        def make_counter():
            count = 0
            def bump():
                nonlocal count      # rebind the enclosing function's name
                count += 1
                return count
            return bump

        tick = make_counter()
        print(tick(), tick(), tick())
    """, notes={4: "global count would mean the module's count"})
    callout(f, "rule", "Read globals freely, but avoid `global` for writing; pass values in and return them "
            "out. Module-level constants (`RATE = 0.2`) are fine; module-level mutable state is a source of bugs.")


def closures(ch):
    f = flow(ch)
    sec(f, "Closures: functions that remember", room=430)
    f.p("`tick` above kept its own `count` after `make_counter` had returned. The inner function holds a "
        "reference to a {B:cell} that holds the variable. Each call of `make_counter` makes a new cell, so "
        "counters are independent:", 13.5, gap=8)
    code(f, """
        a, b = make_counter(), make_counter()
        a(); a()
        print(a(), b())
        print(a.__closure__[0].cell_contents, a.__code__.co_freevars)
    """)
    memory(f, [("names", ["a", "b"])],
           {"A": dict(t="function bump", slots=["closure"], col=0, row=0, color=C.BLUE),
            "B": dict(t="function bump", slots=["closure"], col=0, row=1, color=C.BLUE),
            "c1": dict(t="cell", v="count=3", col=1, row=0, color=C.ORANGE),
            "c2": dict(t="cell", v="count=1", col=1, row=1, color=C.ORANGE)},
           [("a", "A"), ("b", "B"), ("A.0", "c1"), ("B.0", "c2")], height=90)
    sub(f, "The late-binding trap", ACCENT)
    f.p("A closure captures the {B:variable}, not its value at the time. Functions made in a loop all see "
        "the loop variable's {B:final} value:", 13.5, gap=8)
    two_ways(f, ("captures the variable (bug)", """
        fs = [lambda: i for i in range(3)]
        print([g() for g in fs])
    """), ("binds the value now (fix)", """
        fs = [lambda i=i: i for i in range(3)]
        print([g() for g in fs])
    """), same_output=False)
    callout(f, "other", "JavaScript closures work the same way (and had the same loop bug with `var`, fixed by "
            "`let`). Java lambdas may only capture variables that never change, which rules the bug out.")


def higher_order(ch):
    f = flow(ch)
    sec(f, "Functions that take functions", room=420)
    f.p("Because functions are values, a lot of the standard library takes a function as an argument "
        "(\"higher-order\" functions). The most useful by far is `key=`: tell `sorted`/`min`/`max` "
        "{B:what to compare}, not how to sort:", 13.5, gap=8)
    code(f, """
        from operator import itemgetter, attrgetter
        from functools import partial

        books = [("Dune", 1965, 4.3), ("Emma", 1815, 4.0), ("Ubik", 1969, 4.1)]
        print(sorted(books, key=itemgetter(1))[0][0])          # oldest
        print(max(books, key=lambda b: b[2])[0])               # best rated
        print(sorted(books, key=lambda b: (-b[2], b[0]))[0])   # rating desc, then title

        to_int = partial(int, base=2)                          # fix some arguments
        print(to_int("1011"))
    """)
    two_ways(f, ("map and filter", """
        nums = range(10)
        out = list(map(lambda n: n * n,
                   filter(lambda n: n % 2, nums)))
        print(out)
    """), ("a comprehension", """
        nums = range(10)
        out = [n * n for n in nums if n % 2]

        print(out)
    """), verdict=[("readability", 2, 5), ("passing a named function", 5, 4)])
    callout(f, "rule", "Prefer a comprehension when you'd need a `lambda`; `map(str, xs)` with an existing "
            "function is fine. `itemgetter`/`attrgetter` beat `lambda x: x[1]` for speed and clarity.")


def decorators(ch):
    f = flow(ch)
    sec(f, "Decorators: wrapping a function", room=450)
    f.p("A decorator is a function that takes a function and returns a replacement, usually a wrapper that "
        "does something before and after calling the original. `@timed` above a `def` is just shorthand for "
        "`slow = timed(slow)`:", 13.5, gap=8)
    pipe(f, ["call slow(n)", ("wrapper: start clock", C.ORANGE), ("original slow(n)", C.GREEN),
             ("wrapper: stop clock, report", C.ORANGE), "result returned"], size=10)
    code(f, """
        import functools, time

        def timed(func):
            @functools.wraps(func)                # copy name, docstring etc. onto the wrapper
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                ms = (time.perf_counter() - start) * 1000
                print(f"{func.__name__} took {ms:.3f} ms")
                return result
            return wrapper

        @timed
        def slow(n):
            return sum(range(n))

        print(slow(10_000), slow.__name__)
    """, notes={5: "forwards any arguments", 4: "without it: __name__ == 'wrapper'"})
    f.need(330)
    f.p("A decorator that takes options is one more layer: a function that {B:returns} a decorator.", 13.5, gap=6)
    code(f, """
        def retry(times):
            def decorate(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    for attempt in range(1, times + 1):
                        try:
                            return func(*args, **kwargs)
                        except ConnectionError:
                            if attempt == times:
                                raise
                return wrapper
            return decorate

        calls = []
        @retry(times=3)
        def flaky():
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionError("try again")
            return "ok"

        print(flaky(), len(calls))
    """, expect="ok 3")
    sub(f, "The standard library's decorators", ACCENT)
    code(f, """
        import functools, time

        @functools.cache                  # remember every result (lru_cache(maxsize=None))
        def fib(n):
            return n if n < 2 else fib(n - 1) + fib(n - 2)

        t = time.perf_counter(); fib(300); ms = (time.perf_counter() - t) * 1000
        print(fib(300) % 1000, ms < 50, fib.cache_info().hits)
    """)
    table(f, ["decorator", "does"], [
        ["`@functools.cache`, `@functools.lru_cache(maxsize=128)`", "memoise results (arguments must be hashable)"],
        ["`@property`, `@staticmethod`, `@classmethod`", "change how a method is accessed (Ch 5)"],
        ["`@dataclasses.dataclass`", "write `__init__`, `__repr__`, `__eq__` for you (Ch 5)"],
        ["`@contextlib.contextmanager`", "turn a generator into a `with` block (Ch 6)"],
        ["`@functools.singledispatch`", "choose an implementation by argument type"],
    ], widths=[2.4, 2])


def generators(ch):
    f = flow(ch)
    sec(f, "Generators: functions that pause", room=450)
    f.p("A function containing `yield` doesn't run when called. It returns a {B:generator}; each `next()` "
        "runs the body up to the next `yield`, hands out that value, and freezes there, with all its local "
        "variables kept, until the next `next()`:", 13.5, gap=8)
    code(f, """
        def countdown(n):
            print("  (starting)")
            while n > 0:
                yield n
                n -= 1
            print("  (done)")

        g = countdown(2)
        print("made it:", type(g).__name__)
        print(next(g))
        print(next(g))
        print(list(g))           # runs to the end: StopIteration ends the list
    """)
    seq(f, ["caller", "countdown(2) generator"], [
        ("caller", "countdown(2) generator", "next(g)"),
        ("countdown(2) generator", "caller", "yield 2  (paused, n=2)", "reply"),
        ("caller", "countdown(2) generator", "next(g)"),
        ("countdown(2) generator", "caller", "yield 1  (paused, n=1)", "reply"),
        ("caller", "countdown(2) generator", "next(g)"),
        ("countdown(2) generator", "caller", "returns: StopIteration", "reply"),
    ], step=26)
    f.p("Generators are lazy: they compute one item at a time, so a pipeline of them works on data far "
        "bigger than memory. Each stage pulls from the one before:", 13.5, gap=8)
    code(f, """
        import sys

        def read_lines(n):                   # pretend this is a 10 GB log file
            for i in range(n):
                yield f"2026-09-{i % 30 + 1:02} GET /book/{i % 7}"

        lines = read_lines(1_000_000)
        hits = (ln for ln in lines if ln.endswith("/book/3"))     # generator expression
        days = (ln[:10] for ln in hits)
        print(next(days), sum(1 for _ in days) + 1)
        print(sys.getsizeof(days), "bytes, vs",
              sys.getsizeof([0] * 1_000_000), "for a list of a million")
    """)
    callout(f, "trap", "A generator can only be consumed {B:once}. A second `for` over the same generator "
            "gets nothing, silently. If you need two passes, make a list, or call the generator function again.")


def hints(ch):
    f = flow(ch)
    sec(f, "Type hints: documentation a tool can check", room=320)
    f.p("Annotations say what a function expects and returns. Python itself {B:ignores} them at run time; "
        "they're read by humans, editors and checkers like mypy (Ch 17):", 13.5, gap=8)
    code(f, """
        from collections.abc import Iterable

        def average(marks: Iterable[float], *, ndigits: int = 1) -> float | None:
            marks = list(marks)
            return round(sum(marks) / len(marks), ndigits) if marks else None

        print(average([60, 71.5]), average([]), average.__annotations__["return"])
        print(average("12"))     # the hint says numbers; Python only notices when sum() fails
    """, raises=TypeError)
    callout(f, "honest", "Type hints don't make Python statically typed. They catch a class of bugs early "
            "{B:if} you run a checker. For a passport answer: Python is dynamically typed, with optional, "
            "gradual static typing on top. TypeScript did the same for JavaScript.")


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 4)
    stamp(f, [
        (4, "Functions are first-class objects made at `def` time. Parameters: positional-only / normal / "
            "`*args` / keyword-only / `**kwargs`. Defaults evaluated once. LEGB scope fixed at compile time; "
            "closures capture variables (cells); decorators wrap."),
        (3, "Generators: `yield` pauses a function; iteration pulls values lazily until `StopIteration`."),
        (2, "Dynamic typing with optional annotations, checked only by external tools."),
    ])
    callout(f, "deep", "Vault notes: {b:8.2} Parameters and arguments · {b:8.5} Defaults are evaluated at "
            "definition time · {b:8.7} Namespaces and the LEGB rule · {b:8.8} First-class functions · {b:8.9} "
            "Closures · {b:8.13} Decorators derived from first-class functions · {b:8.14} Decorator factories "
            "and timing · {b:6.9} Generator functions and suspension · {b:6.10} Generator expressions · "
            "{b:11.13} functools · {b:12.18} Type hints.")


def build(ch):
    title_page(ch)
    parameters(ch)
    defaults(ch)
    scope(ch)
    closures(ch)
    higher_order(ch)
    decorators(ch)
    generators(ch)
    hints(ch)
    finish(ch)
