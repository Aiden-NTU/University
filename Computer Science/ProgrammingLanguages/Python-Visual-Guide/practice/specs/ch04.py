EXERCISES = [
    dict(
        id="4.1", kind="fix", title="Two bugs that every Python programmer writes once",
        task="""
        `make_reminders(names)` returns a dict mapping each name to a function that returns
        `"Hi <name>, your book is due"`. `log_due(name, log=[])` appends the name to a log and returns it.

        Both have a classic bug (one is a closure bug, one is a default-value bug). Fix them so that
        every reminder uses its own name, and each `log_due` call without a `log` gets a fresh list.
        """,
        stub='''
        def make_reminders(names):
            out = {}
            for name in names:
                out[name] = lambda: f"Hi {name}, your book is due"
            return out

        def log_due(name, log=[]):
            log.append(name)
            return log
        ''',
        tests='''
        def test_reminders(m):
            r = m.make_reminders(["ana", "ben", "cy"])
            equal(r["ana"](), "Hi ana, your book is due", "ana's reminder")
            equal(r["ben"](), "Hi ben, your book is due", "ben's reminder")

        def test_log(m):
            equal(m.log_due("ana"), ["ana"], "first call")
            equal(m.log_due("ben"), ["ben"], "second call gets its own list")
            mine = ["x"]
            check(m.log_due("cy", mine) is mine and mine == ["x", "cy"], "a passed-in list is appended to")
        ''',
        alts={
            "default arg + None sentinel": ('''
                def make_reminders(names):
                    return {name: (lambda name=name: f"Hi {name}, your book is due") for name in names}

                def log_due(name, log=None):
                    if log is None:
                        log = []
                    log.append(name)
                    return log
            ''', "name=name freezes the current value as a default (evaluated once, which is the very "
                 "behaviour that causes the second bug)."),
            "functools.partial": ('''
                from functools import partial

                def _remind(name):
                    return f"Hi {name}, your book is due"

                def make_reminders(names):
                    return {name: partial(_remind, name) for name in names}

                def log_due(name, log=None):
                    log = [] if log is None else log
                    log.append(name)
                    return log
            ''', "partial stores the argument value right away; no lambda, no trap."),
        },
    ),
    dict(
        id="4.2", kind="build", title="Your own memoising decorator",
        task="""
        Write a decorator `memoize` (without `functools.cache`/`lru_cache`) that:

        - remembers results by the positional arguments (assume they're hashable),
        - exposes the cache as a dict attribute `.cache` on the decorated function,
        - keeps the original `__name__` and `__doc__` (`functools.wraps` is allowed).

        Then decorate a recursive `fib(n)` with it in your file, so `fib(200)` returns instantly.
        """,
        stub='''
        def memoize(func):
            ...

        @memoize
        def fib(n):
            """Fibonacci number n."""
            return n if n < 2 else fib(n - 1) + fib(n - 2)
        ''',
        tests='''
        def test_fib_fast_and_named(m):
            equal(m.fib(200), 280571172992510140037611932413038677189525, "fib(200)")
            equal(m.fib.__name__, "fib", "__name__ preserved")
            equal(m.fib.__doc__, "Fibonacci number n.", "__doc__ preserved")
            check(len(m.fib.cache) >= 200, ".cache holds the results")

        def test_counts_calls(m):
            calls = []
            @m.memoize
            def sq(x):
                calls.append(x)
                return x * x
            equal([sq(3), sq(3), sq(4), sq(3)], [9, 9, 16, 9], "results")
            equal(calls, [3, 4], "the body runs once per distinct argument")
            import ast
            for node in ast.walk(source_tree(m)):
                if isinstance(node, ast.ImportFrom) and node.module == "functools":
                    check(not {a.name for a in node.names} & {"cache", "lru_cache"}, "write the cache yourself")
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "functools":
                    check(node.attr not in ("cache", "lru_cache"), "write the cache yourself")
        ''',
        alts={
            "closure dict": ('''
                import functools

                def memoize(func):
                    cache = {}

                    @functools.wraps(func)
                    def wrapper(*args):
                        if args not in cache:
                            cache[args] = func(*args)
                        return cache[args]

                    wrapper.cache = cache
                    return wrapper

                @memoize
                def fib(n):
                    """Fibonacci number n."""
                    return n if n < 2 else fib(n - 1) + fib(n - 2)
            ''', "The recursion calls the *name* fib, which now refers to the wrapper, so inner calls are "
                 "cached too."),
            "class-based decorator": ('''
                import functools

                class memoize:
                    def __init__(self, func):
                        functools.update_wrapper(self, func)
                        self.func = func
                        self.cache = {}

                    def __call__(self, *args):
                        try:
                            return self.cache[args]
                        except KeyError:
                            result = self.cache[args] = self.func(*args)
                            return result

                @memoize
                def fib(n):
                    """Fibonacci number n."""
                    return n if n < 2 else fib(n - 1) + fib(n - 2)
            ''', "Any callable object can be a decorator. Note: a class decorator like this doesn't bind as a "
                 "method on classes without a __get__; the function version does."),
        },
    ),
    dict(
        id="4.3", kind="build", title="Check types at run time from the hints",
        task="""
        Write a decorator `checked` that reads the decorated function's annotations and raises
        `TypeError` when an argument isn't an instance of its annotated type. Unannotated parameters
        are not checked; defaults must still work; keyword arguments must be checked too. Only
        plain classes are used as annotations (`int`, `str`, `float`...).

        Hint: `inspect.signature(func).bind(*args, **kwargs)` maps arguments to parameter names.
        """,
        stub='''
        def checked(func):
            ...
        ''',
        tests='''
        def test_checks(m):
            @m.checked
            def lend(title: str, days: int = 14, note=None):
                return f"{title}:{days}:{note}"
            equal(lend("Dune"), "Dune:14:None", "defaults")
            equal(lend("Dune", days=7, note=5), "Dune:7:5", "keywords, unannotated note")
            raises(TypeError, lend, 3)
            raises(TypeError, lend, "Dune", days="7")
            raises(TypeError, lend, "Dune", "7")
            equal(lend.__name__, "lend", "keep the name")
        ''',
        alts={
            "signature.bind": ('''
                import functools, inspect

                def checked(func):
                    sig = inspect.signature(func)

                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        bound = sig.bind(*args, **kwargs)
                        for name, value in bound.arguments.items():
                            kind = sig.parameters[name].annotation
                            if kind is not inspect.Parameter.empty and not isinstance(value, kind):
                                raise TypeError(f"{name} should be {kind.__name__}, got {type(value).__name__}")
                        return func(*args, **kwargs)

                    return wrapper
            ''', "The signature is computed once, at decoration time, not on every call. Libraries like "
                 "pydantic and typeguard do this properly for generic types too."),
        },
    ),
    dict(
        id="4.4", kind="build", title="Lazy chunks and windows",
        task="""
        Write two **generator** functions:

        - `chunks(iterable, n)`: yields lists of `n` items; the last may be shorter.
        - `windows(iterable, n)`: yields every run of `n` consecutive items as a tuple
          (`windows("abcd", 2)` → `('a','b'), ('b','c'), ('c','d')`).

        Both must be lazy: they're tested on an infinite iterator (`itertools.count()`), so building
        a full list first will hang.
        """,
        stub='''
        def chunks(iterable, n):
            ...

        def windows(iterable, n):
            ...
        ''',
        tests='''
        import itertools, random

        def test_chunks(m):
            equal(list(m.chunks(range(7), 3)), [[0, 1, 2], [3, 4, 5], [6]], "chunks of 3")
            equal(list(m.chunks([], 3)), [], "empty")
            equal(list(itertools.islice(m.chunks(itertools.count(), 2), 3)), [[0, 1], [2, 3], [4, 5]], "infinite")

        def test_windows(m):
            equal(list(m.windows("abcd", 2)), [("a", "b"), ("b", "c"), ("c", "d")], "pairs")
            equal(list(m.windows("ab", 3)), [], "too short")
            equal(list(itertools.islice(m.windows(itertools.count(), 3), 2)), [(0, 1, 2), (1, 2, 3)], "infinite")

        def test_random(m):
            for xs in rand_lists(150, seed=4):
                n = random.Random(len(xs)).randint(1, 4)
                equal([x for c in m.chunks(xs, n) for x in c], xs, "chunks rejoin to the input")
                equal(list(m.windows(xs, n)), [tuple(xs[i:i + n]) for i in range(len(xs) - n + 1)], "windows")
        ''',
        alts={
            "islice and deque": ('''
                from collections import deque
                from itertools import islice

                def chunks(iterable, n):
                    it = iter(iterable)
                    while batch := list(islice(it, n)):
                        yield batch

                def windows(iterable, n):
                    it = iter(iterable)
                    win = deque(islice(it, n), maxlen=n)
                    if len(win) == n:
                        yield tuple(win)
                    for x in it:
                        win.append(x)
                        yield tuple(win)
            ''', "deque(maxlen=n) drops the oldest item automatically. Python 3.12 ships itertools.batched "
                 "(chunks as tuples) and 3.10 ships itertools.pairwise (n=2 windows)."),
            "plain loops": ('''
                def chunks(iterable, n):
                    batch = []
                    for x in iterable:
                        batch.append(x)
                        if len(batch) == n:
                            yield batch
                            batch = []
                    if batch:
                        yield batch

                def windows(iterable, n):
                    win = []
                    for x in iterable:
                        win.append(x)
                        if len(win) > n:
                            win.pop(0)
                        if len(win) == n:
                            yield tuple(win)
            ''', "Clear, but win.pop(0) is O(n) per step; deque.popleft is O(1)."),
        },
    ),
    dict(
        id="4.5", kind="refactor", title="Name your flags",
        task="""
        `export(rows, path, True, False, ";")` is unreadable at the call site. Refactor `export` so
        that `rows` and `path` are positional, and `header`, `quote` and `sep` are **keyword-only**
        with defaults `header=True`, `quote=False`, `sep=","`. Behaviour must stay the same: it returns
        the text it would write (it doesn't really write a file).
        """,
        stub='''
        def export(rows, path, header, quote, sep):
            lines = []
            if header:
                lines.append(sep.join(rows[0].keys()))
            for r in rows:
                vals = [str(v) for v in r.values()]
                if quote:
                    vals = [f'"{v}"' for v in vals]
                lines.append(sep.join(vals))
            return "\\n".join(lines)
        ''',
        tests='''
        import inspect

        ROWS = [{"t": "Dune", "y": 1965}, {"t": "Emma", "y": 1815}]

        def test_behaviour(m):
            equal(m.export(ROWS, "x.csv"), "t,y\\nDune,1965\\nEmma,1815", "defaults")
            equal(m.export(ROWS, "x.csv", header=False, quote=True, sep=";"), '"Dune";"1965"\\n"Emma";"1815"', "options")

        def test_keyword_only(m):
            raises(TypeError, m.export, ROWS, "x.csv", True)
            kinds = {n: p.kind.name for n, p in inspect.signature(m.export).parameters.items()}
            equal({kinds[k] for k in ("header", "quote", "sep")}, {"KEYWORD_ONLY"}, "flag parameter kinds")
        ''',
        alts={
            "bare star": ('''
                def export(rows, path, *, header=True, quote=False, sep=","):
                    lines = [sep.join(rows[0].keys())] if header else []
                    for r in rows:
                        vals = [f'"{v}"' if quote else str(v) for v in r.values()]
                        lines.append(sep.join(vals))
                    return "\\n".join(lines)
            ''', "One `*` does it. The csv module (Ch 8) is what you'd really use to write this."),
        },
    ),
    dict(
        id="4.6", kind="project", title="Mini-project: an event bus with decorators",
        task="""
        Write a class `EventBus`:

        - `@bus.on("loaned")` registers the decorated function as a handler for that event name and
          returns the function **unchanged** (so it can still be called directly)
        - `bus.on("loaned", once=True)` registers a handler that runs only the first time
        - `bus.emit("loaned", **data)` calls the event's handlers in registration order with the
          keyword data and returns a list of their return values (`[]` if none)
        - `bus.off("loaned", func)` removes a handler (`ValueError` if it isn't registered)

        A handler that raises must not stop later handlers: collect the exception object in the
        result list in its place.
        """,
        stub='''
        class EventBus:
            ...
        ''',
        tests='''
        def test_basic(m):
            bus = m.EventBus()
            @bus.on("loaned")
            def note(title, who):
                return f"{who} has {title}"
            @bus.on("loaned")
            def count(**data):
                return len(data)
            equal(bus.emit("loaned", title="Dune", who="ana"), ["ana has Dune", 2], "results in order")
            equal(note("Emma", "ben"), "ben has Emma", "decorated function still callable")
            equal(bus.emit("returned"), [], "no handlers")

        def test_once_off_errors(m):
            bus = m.EventBus()
            @bus.on("x", once=True)
            def first():
                return 1
            @bus.on("x")
            def boom():
                raise RuntimeError("bad")
            @bus.on("x")
            def last():
                return 3
            out = bus.emit("x")
            equal([out[0], out[2]], [1, 3], "first and last ran")
            check(isinstance(out[1], RuntimeError), "the exception is collected in place")
            equal(len(bus.emit("x")), 2, "once handler is gone")
            bus.off("x", boom)
            equal(bus.emit("x"), [3], "after off")
            raises(ValueError, bus.off, "x", boom)
        ''',
        alts={
            "dict of lists": ('''
                from collections import defaultdict

                class EventBus:
                    def __init__(self):
                        self._handlers = defaultdict(list)

                    def on(self, event, once=False):
                        def register(func):
                            self._handlers[event].append((func, once))
                            return func
                        return register

                    def off(self, event, func):
                        for i, (h, _) in enumerate(self._handlers[event]):
                            if h is func:
                                del self._handlers[event][i]
                                return
                        raise ValueError(f"{func!r} is not handling {event!r}")

                    def emit(self, event, **data):
                        results = []
                        for func, once in list(self._handlers[event]):
                            if once:
                                self.off(event, func)
                            try:
                                results.append(func(**data))
                            except Exception as exc:
                                results.append(exc)
                        return results
            ''', "Iterating over a copy (list(...)) lets handlers remove themselves mid-emit safely. This is "
                 "the observer pattern; Flask's @app.route is the same decorator-registers-function idea."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="def f(x, items=[]):\n    items.append(x)\n    return len(items)\nf(1)\nprint(f(2))"),
    dict(kind="predict", code="x = 1\ndef f():\n    return x\nx = 2\nprint(f())", why="Names are looked up when the function runs, not when it's defined."),
    dict(kind="predict", code="def g():\n    yield 1\n    yield 2\nit = g()\nprint(list(it), list(it))", why="A generator is consumed once."),
    dict(kind="predict", code="fs = [lambda: i * 10 for i in range(3)]\nprint(fs[0]())"),
    dict(kind="predict", code="def deco(f):\n    return lambda *a: f(*a) + 1\n@deco\ndef h(n):\n    return n * 2\nprint(h(5))"),
    dict(kind="recall", q="Which keyword lets an inner function rebind a variable of its enclosing function?", a="nonlocal"),
    dict(kind="recall", q="Which functools decorator copies __name__ and __doc__ onto a wrapper?", a=["wraps", "functools.wraps"]),
    dict(kind="recall", q="In the signature def f(a, /, b, *, c), how must c be passed?", a=["by keyword", "keyword", "as a keyword", "by name"]),
]
