"""Chapter 6 - Errors and context managers: exceptions unwinding the stack, reading tracebacks, the
hierarchy, try/except/else/finally, EAFP, custom exceptions and chaining, with-statements (class and
contextmanager), ExitStack, exception groups, logging, assert."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, W, callout, code, flow, go, pipe, practice, repl, section, seq, stamp, sub, table,
                         title_block, tree, two_ways)

ORDER = 6
NUM = 6
TITLE = "Errors and context managers"
SHORT = "Errors"
SLUG = "Errors"
ACCENT = C.RED


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def stack_picture(f):
    frames = [("main()", "try: ... except LibraryError: report it", C.GREEN),
              ("load_members(path)", "no try: the exception passes straight through", C.GREY),
              ("parse_line(line)", "int('abc') raises ValueError here", C.RED)]
    y = f.reserve(170)
    pg = f.pg
    bw = 300
    for k, (name, what, col) in enumerate(frames):
        by = y + k * 52
        pg.rect(L + 20, by, bw, 42, col, 1.3, fillcolor=C.LIGHT[col], r=6)
        pg.text(L + 30, by + 5, name, 11, col, F.MONO)
        pg.text(L + 30, by + 22, what, 9.5, C.INK)
    pg.text(L + 20, y + 158, "the call stack: each call adds a frame below its caller", 9.5, C.GREY)
    ax = L + bw + 45
    pg.arrow(ax, y + 125, ax, y + 22, C.RED, 2.0, head=8)
    pg.note(ax + 12, y + 30, "the exception climbs up,\nending each frame,\nuntil an except\nmatches it", C.RED, 14,
            w=150)


def title_page(ch):
    title_block(ch, 6, TITLE, "errors climb the call stack until someone catches them", ACCENT)
    f = ch.flow(top=190)
    f.p("When something goes wrong, Python {B:raises} an exception: an object describing the problem. The "
        "current function stops at once, and the exception travels {B:up} the call stack, ending each "
        "function it passes through, until it reaches a `try` block with a matching `except`. If none "
        "matches, the program stops and prints a traceback.", 14, gap=10)
    stack_picture(f)
    code(f, """
        import traceback

        def parse_line(line):
            name, age = line.split(",")
            return name, int(age)

        def load_members(lines):
            return [parse_line(ln) for ln in lines]

        try:
            load_members(["ana,20", "ben,abc"])
        except ValueError:
            print(traceback.format_exc(limit=-2))
    """, size=8.8)
    callout(f, "rule", "Read a traceback from the {B:bottom}: the last line says what happened "
            "(`ValueError: invalid literal...`), the frame just above it says where. Then walk upwards to find "
            "the first line that's {B:your} code doing something wrong.")


def hierarchy(ch):
    f = flow(ch)
    sec(f, "The exception family tree", room=420)
    f.p("Exceptions are classes, arranged in a hierarchy. `except X` catches `X` {B:and all its subclasses}, "
        "so where you catch in the tree decides how much you catch:", 13.5, gap=8)
    nodes = {"B": ("BaseException", 0.5, 0), "K": ("KeyboardInterrupt", 0.13, 1), "S": ("SystemExit", 0.36, 1),
             "E": ("Exception", 0.68, 1),
             "A": ("ArithmeticError", 0.08, 2), "Lk": ("LookupError", 0.32, 2), "O": ("OSError", 0.58, 2),
             "V": ("ValueError", 0.8, 2), "T": ("TypeError", 0.96, 2),
             "Z": ("ZeroDivisionError", 0.08, 3), "Ke": ("KeyError", 0.25, 3), "I": ("IndexError", 0.39, 3),
             "Fn": ("FileNotFoundError", 0.58, 3), "U": ("UnicodeDecodeError", 0.83, 3),
             "P": ("PermissionError", 0.58, 4)}
    edges = [("B", "K"), ("B", "S"), ("B", "E"), ("E", "A"), ("E", "Lk"), ("E", "O"), ("E", "V"), ("E", "T"),
             ("A", "Z"), ("Lk", "Ke"), ("Lk", "I"), ("O", "Fn"), ("O", "P"), ("V", "U")]
    tree(f, nodes, edges, size=8.6, h=225)
    code(f, """
        def lookup(data, key):
            try:
                return data[key]
            except LookupError as e:                # catches KeyError AND IndexError
                return f"missing: {type(e).__name__}"

        print(lookup({"a": 1}, "b"), lookup([10], 5), lookup([10], 0))
    """)
    callout(f, "trap", "Never write a bare `except:` or `except BaseException:`. They also catch "
            "`KeyboardInterrupt` (Ctrl+C) and `SystemExit`, so your program can't be stopped. Even "
            "`except Exception:` hides bugs like typos (`NameError`). Catch the most specific class you can "
            "actually handle.")
    callout(f, "trap", "Order matters: Python checks `except` clauses top to bottom and runs the first match. "
            "`except Exception` above `except ValueError` means the `ValueError` branch can never run.")


def try_flow(ch):
    f = flow(ch)
    sec(f, "try, except, else, finally", room=430)
    f.p("A `try` statement has up to four parts. Watch which ones run when the body succeeds and when it fails:",
        13.5, gap=8)
    code(f, """
        def attempt(text):
            try:
                print("  try:", end=" ")
                n = int(text)
            except ValueError as e:
                print("except:", type(e).__name__, end=" | ")
            else:
                print("else: got", n, end=" | ")      # only if no exception
            finally:
                print("finally")                      # always, even on return or a new error

        attempt("42")
        attempt("4x2")
    """)
    table(f, ["part", "runs when", "use it for"], [
        ["`try:`", "always (until something raises)", "only the lines that can fail"],
        ["`except E as e:`", "an `E` (or subclass) was raised in the `try`", "recovering, or translating the error"],
        ["`else:`", "the `try` finished without an exception", "the next steps, kept out of the `try`"],
        ["`finally:`", "always, whatever happened", "cleanup: close, release, delete temp files"],
    ], widths=[1.1, 2.2, 2.2])
    sub(f, "Ask forgiveness, or look before you leap?", ACCENT)
    two_ways(f, ("LBYL: check first", """
        import os

        path = "members.csv"
        if os.path.exists(path):
            with open(path) as fh:
                print(fh.read())
        else:
            print("no file")
    """), ("EAFP: try it", """
        path = "members.csv"
        try:
            with open(path) as fh:
                print(fh.read())
        except FileNotFoundError:
            print("no file")


    """), verdict=[("no race between check and use", 2, 5), ("clear when failure is common", 4, 3)])
    callout(f, "why", "The LBYL version has a race: the file can be deleted between `exists()` and `open()`. "
            "Python style generally prefers EAFP for things outside your control (files, network, dict keys "
            "from input), and plain `if` checks for your own program's logic.")


def custom(ch):
    f = flow(ch)
    sec(f, "Your own exceptions, and chaining", room=430)
    f.p("A library or app should raise exceptions that mean something in {B:its} terms. Make one base class, "
        "then specific subclasses; callers can catch broadly or narrowly:", 13.5, gap=8)
    code(f, """
        class LibraryError(Exception):
            \"\"\"Base class for everything this app raises on purpose.\"\"\"

        class LimitReached(LibraryError):
            def __init__(self, member, limit):
                super().__init__(f"{member} already has {limit} loans")
                self.member, self.limit = member, limit

        class UnknownBook(LibraryError, KeyError):     # also a KeyError, for code that expects one
            pass

        try:
            raise LimitReached("ana", 3)
        except LibraryError as e:
            print(type(e).__name__, "-", e, "-", e.limit)
    """)
    f.p("When you catch a low-level error and raise your own, use `raise ... from err`. The original is kept "
        "as `__cause__` and printed too, so nobody loses the real reason:", 13.5, gap=8)
    code(f, """
        import traceback

        BOOKS = {"111": "Dune"}

        def find(isbn):
            try:
                return BOOKS[isbn]
            except KeyError as err:
                raise UnknownBook(isbn) from err

        try:
            find("999")
        except LibraryError as e:
            print(repr(e), "caused by", repr(e.__cause__))
            print(traceback.format_exc().count("direct cause"), "'direct cause' line in the traceback")
    """)
    callout(f, "idea", "Since 3.11 you can attach context without changing the exception: "
            "`e.add_note(\"while importing row 17\")` adds a line to the traceback. Use it in loops over input "
            "data, where the row number is what you actually need to know.")


def context_managers(ch):
    f = flow(ch)
    sec(f, "with: cleanup that can't be forgotten", room=450)
    f.p("A `with` block guarantees that setup is paired with cleanup, even when the body raises. It calls "
        "`__enter__` at the start and `__exit__` at the end, {B:whatever happens}:", 13.5, gap=8)
    seq(f, ["your code", "with-statement", "context manager"], [
        ("your code", "with-statement", "with Timer() as t:"),
        ("with-statement", "context manager", "__enter__()"),
        ("context manager", "your code", "returns the object bound to t", "reply"),
        ("your code", "with-statement", "block ends (normally or by raising)"),
        ("with-statement", "context manager", "__exit__(exc_type, exc, tb)"),
        ("context manager", "with-statement", "True = swallow the error; else re-raise", "reply"),
    ], step=25)
    code(f, """
        import time

        class Timer:
            def __enter__(self):
                self.start = time.perf_counter()
                return self                           # this is what 'as t' receives

            def __exit__(self, exc_type, exc, tb):
                self.ms = (time.perf_counter() - self.start) * 1000
                print(f"block took {self.ms:.2f} ms, error: {exc_type.__name__ if exc_type else None}")
                return False                          # don't swallow exceptions

        with Timer() as t:
            sum(range(100_000))
        try:
            with Timer():
                1 / 0
        except ZeroDivisionError:
            print("the error still reached us")
    """)
    sub(f, "The quick way: a generator with @contextmanager", ACCENT)
    code(f, """
        import contextlib, os, tempfile

        @contextlib.contextmanager
        def working_dir(path):
            old = os.getcwd()
            os.chdir(path)                 # setup: everything before yield
            try:
                yield path                 # the with-block runs here
            finally:
                os.chdir(old)              # cleanup: runs even if the block raised

        with tempfile.TemporaryDirectory() as d, working_dir(d):
            print(os.getcwd() == os.path.realpath(d))
        print(os.getcwd() == os.path.realpath(d))
    """, notes={8: "without try/finally, an error skips cleanup"})
    table(f, ["stdlib context manager", "guarantees"], [
        ["`open(...)`", "the file is closed (and flushed)"],
        ["`sqlite3` connection", "commit on success, rollback on error (Ch 12; doesn't close!)"],
        ["`threading.Lock()`", "the lock is released (Ch 16)"],
        ["`tempfile.TemporaryDirectory()`", "the directory and its contents are deleted"],
        ["`contextlib.suppress(E)`", "errors of type `E` are ignored, nothing else"],
        ["`contextlib.ExitStack()`", "a variable number of resources, all cleaned up in reverse order"],
    ], widths=[2.3, 3])


def groups_logging(ch):
    f = flow(ch)
    sec(f, "Several errors at once, and logging instead of print", room=430)
    f.p("When many independent tasks fail together (validating every row, running tasks concurrently), you "
        "want {B:all} the errors, not just the first. Python 3.11 added `ExceptionGroup` and `except*`:",
        13.5, gap=8)
    code(f, """
        def validate(rows):
            errors = []
            for i, (name, age) in enumerate(rows, 1):
                if not name:
                    errors.append(ValueError(f"row {i}: empty name"))
                if not 0 < age < 130:
                    errors.append(ValueError(f"row {i}: bad age {age}"))
            if errors:
                raise ExceptionGroup("invalid rows", errors)

        try:
            validate([("ana", 20), ("", 200), ("cy", 30)])
        except* ValueError as group:
            for e in group.exceptions:
                print(e)
    """)
    f.p("`print` is for output the user asked for. Diagnostics belong in `logging`: it has levels, timestamps, "
        "one place to configure where messages go, and it can be turned down without editing code:", 13.5, gap=8)
    code(f, """
        import logging, sys

        logging.basicConfig(stream=sys.stdout, level=logging.INFO, force=True,
                            format="%(levelname)-7s %(name)s: %(message)s")
        log = logging.getLogger("library.loans")

        log.debug("not shown: below INFO")
        log.info("lent %s to %s", "Dune", "ana")    # args, not an f-string: formatted only if shown
        try:
            {}["999"]
        except KeyError:
            log.exception("lookup failed")                  # ERROR level + the traceback
    """, out_max=10)
    table(f, ["level", "for"], [
        ["`DEBUG`", "details only useful while diagnosing"],
        ["`INFO`", "normal events worth a record (started, lent a book)"],
        ["`WARNING`", "unexpected but handled (retrying, using a default); the default threshold"],
        ["`ERROR` / `CRITICAL`", "something failed / the program can't continue"],
    ], widths=[1.3, 4])
    callout(f, "trap", "`assert` is for {B:your own} assumptions while developing (\"this list can't be empty "
            "here\"), never for checking user input: `python -O` removes every assert. Validate input with "
            "`if ...: raise ValueError(...)`.")


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 6)
    stamp(f, [
        (7, "Exceptions are class instances that unwind the stack until a matching `except` (subclasses "
            "match). `try/except/else/finally`; `raise X from err` chains; `ExceptionGroup` + `except*` for "
            "many at once. Style: EAFP. Cleanup via `with` (`__enter__`/`__exit__`), never by hoping."),
        (11, "`logging` for diagnostics; `contextlib` (contextmanager, suppress, ExitStack) for resources."),
    ])
    callout(f, "other", "Java has checked exceptions (the compiler forces you to handle them) and "
            "try-with-resources for cleanup. Go has no exceptions: functions return an `error` value you must "
            "check. Rust returns `Result<T, E>` and uses `?` to pass errors up. C++ uses destructors (RAII) "
            "where Python uses `with`.")
    callout(f, "deep", "Vault notes: {b:6.12} Exceptions as non-local control flow · {b:6.13} Exception "
            "propagation and stack unwinding · {b:6.14} Exceptions versus result values · {b:6.15} Iteration, "
            "exceptions, and generator cleanup · {b:11.1} Boundaries turn assumptions into failure modes · "
            "{b:11.4} Context managers and deterministic release · {b:12.11} Debugging as hypothesis testing · "
            "{b:12.12} Logging and diagnostics · {b:15.9} Exception machinery.")


def build(ch):
    title_page(ch)
    hierarchy(ch)
    try_flow(ch)
    custom(ch)
    context_managers(ch)
    groups_logging(ch)
    finish(ch)
