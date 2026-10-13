"""Chapter 17 - Quality: unittest, doctest, unittest.mock, timeit and cProfile, type hints and mypy,
pyproject packaging, and a Git workflow."""
import os
import shlex
import subprocess
import tempfile

from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, callout, code, flow, pipe, practice, section, shell, stamp, sub, table,
                         title_block, tree)

ORDER = 17
NUM = 17
TITLE = "Quality: tests, speed, types, shipping"
SHORT = "Quality"
SLUG = "Quality"
ACCENT = C.GREEN


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


# ----------------------------------------------------------------------------- a real git session
FEES_V1 = "def late_fee(days):\n    return days * 0.25\n"
FEES_V2 = "def late_fee(days):\n    return min(days * 0.25, 5.0)\n"

GIT_STEPS = [
    ("# write fees.py", ("fees.py", FEES_V1)),
    ("git init -q -b main", None),
    ("git add fees.py", None),
    ('git commit -qm "Add late fee"', None),
    ("git switch -qc fine-cap", None),
    ("# edit fees.py: cap the fee at 5.00", ("fees.py", FEES_V2)),
    ('git commit -qam "Cap late fees at 5.00"', None),
    ("git switch -q main", None),
    ("# write README.md", ("README.md", "# loans\n")),
    ("git add README.md", None),
    ('git commit -qm "Add README"', None),
    ("git merge -q --no-edit fine-cap", None),
    ("git log --oneline --graph", None),
]


def git_session():
    """Run GIT_STEPS for real in a temp folder; fixed names and dates make the hashes reproducible."""
    lines = []
    with tempfile.TemporaryDirectory() as d:
        for k, (cmd, write) in enumerate(GIT_STEPS):
            stamp_ = f"2026-03-01T{10 + k}:00:00+00:00"
            env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                   "GIT_AUTHOR_NAME": "Ana", "GIT_AUTHOR_EMAIL": "ana@example.org",
                   "GIT_COMMITTER_NAME": "Ana", "GIT_COMMITTER_EMAIL": "ana@example.org",
                   "GIT_AUTHOR_DATE": stamp_, "GIT_COMMITTER_DATE": stamp_}
            if write:
                name, text = write
                with open(os.path.join(d, name), "w") as fh:
                    fh.write(text)
                lines.append(cmd)
                continue
            r = subprocess.run(shlex.split(cmd), cwd=d, env=env, capture_output=True, text=True, timeout=30)
            if r.returncode != 0:
                raise RuntimeError(f"{cmd}: {r.stderr}")
            lines.append("$ " + cmd)
            lines += [l.rstrip() for l in r.stdout.splitlines()]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- pictures
def pyramid_picture(f):
    """Many fast unit tests, fewer integration tests, a handful of end-to-end tests."""
    y = f.reserve(146)
    pg = f.pg
    cx = L + 130
    tiers = [("end-to-end", "a few: the whole program, real I/O", C.RED, 90),
             ("integration", "some: real sqlite, real files", C.ORANGE, 180),
             ("unit", "many: one function, milliseconds", ACCENT, 260)]
    for i, (name, what, col, wd) in enumerate(tiers):
        ty = y + 4 + i * 38
        pg.rect(cx - wd / 2, ty, wd, 32, col, 1.3, fillcolor=C.LIGHT[col], r=5)
        pg.text(cx, ty + 9, name, 11, col, F.BOLD, align="center")
        pg.text(L + 296, ty + 9, what, 10, C.INK)
        pg.line(cx + wd / 2 + 4, ty + 16, L + 290, ty + 16, C.GREY, 0.7, dash=(2, 3))
    pg.note(R, y + 122, "slower, costlier, flakier as you go up", C.PURPLE, 13, align="right")


def commit_picture(f):
    """Commits point at their parents; a branch is just a name pointing at one commit."""
    y = f.reserve(150)
    pg = f.pg
    cw, chh = 112, 40
    pos = {"A": (L + 10, y + 52), "B": (L + 160, y + 4), "C": (L + 160, y + 100), "D": (L + 330, y + 52)}
    info = {"A": ("Add late fee", C.BLUE), "B": ("Add README", C.BLUE),
            "C": ("Cap late fees", C.PURPLE), "D": ("Merge fine-cap", C.BLUE)}
    for k, (x, yy) in pos.items():
        msg, col = info[k]
        pg.rect(x, yy, cw, chh, col, 1.3, fillcolor=C.LIGHT[col], r=6)
        pg.text(x + 8, yy + 5, f"commit {k}", 9, col, F.BOLD)
        pg.text(x + 8, yy + 20, msg, 9.5, C.INK)
    for child, parent in [("B", "A"), ("C", "A"), ("D", "B"), ("D", "C")]:
        cx_, cy_ = pos[child]
        px, py = pos[parent]
        pg.arrow(cx_ - 2, cy_ + chh / 2, px + cw + 2, py + chh / 2, C.GREY, 1.1, head=5)
    dx, dy = pos["D"]
    pg.rect(dx + cw + 18, dy + 8, 50, 22, C.GREEN, 1.2, fillcolor=C.LIGHT[C.GREEN], r=4)
    pg.text(dx + cw + 43, dy + 12, "main", 10, C.GREEN, F.BOLD, align="center")
    pg.arrow(dx + cw + 16, dy + 19, dx + cw + 3, dy + 19, C.GREEN, 1.1, head=5)
    cx_, cy_ = pos["C"]
    pg.rect(cx_ + cw + 18, cy_ + 8, 66, 22, C.PURPLE, 1.2, fillcolor=C.LIGHT[C.PURPLE], r=4)
    pg.text(cx_ + cw + 51, cy_ + 12, "fine-cap", 10, C.PURPLE, F.BOLD, align="center")
    pg.arrow(cx_ + cw + 16, cy_ + 19, cx_ + cw + 3, cy_ + 19, C.PURPLE, 1.1, head=5)
    pg.note(R, y + 112, "arrows point to the parent:\nhistory is read backwards", C.GREY, 13, align="right")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 17, TITLE, "how professionals know their code works, and keep it working", ACCENT)
    f = ch.flow(top=190)
    f.p("Writing code that works once is the easy half. Quality means being able to {B:show} it works, find "
        "out {B:why} it's slow, catch mistakes {B:before} running it, let other people {B:install} it, and "
        "{B:undo} any change. Each of those has a standard Python tool, and every other language has the "
        "same five:", 14, gap=10)
    pipe(f, ["edit", ("type-check\nmypy", C.PURPLE), ("test\nunittest", ACCENT), ("measure\ncProfile", C.ORANGE),
             ("commit\ngit", C.BLUE), ("ship\npyproject", C.BROWN)], color=C.GREY, h=44,
         under=[None, "before it runs", "does what I claim?", "only when too slow", "small, often", "pip install"])
    table(f, ["the question", "Python tool", "in the stdlib?"], [
        ["Does it do what I claim, and still after my change?", "`unittest`, `doctest`, `unittest.mock`", "yes"],
        ["Where does the time go?", "`timeit`, `cProfile` + `pstats`", "yes"],
        ["Do the types line up, before I run anything?", "type hints + `mypy` or `pyright`", "hints yes, checker no"],
        ["Can someone else install and run it?", "`pyproject.toml`, `venv`, `pip`, `build`", "venv yes, rest pip"],
        ["What changed, when, why, and can I undo it?", "Git", "separate program"],
    ], widths=[3.0, 2.6, 1.3], size=10.5)
    f.p("The habit matters more than the tool: a test written before the fix, a measurement taken before the "
        "optimisation, a commit made before the experiment. The practice repo you've been using is built "
        "exactly this way: every exercise is a unittest suite.", 13.5, gap=8)


def unittest_section(f):
    sec(f, "unittest: claims the computer checks", room=440)
    f.p("A test is a {B:claim about behaviour} written as code: \"a book returned 4 days late costs 1.00\". Each "
        "test follows the same three steps:", 13.5, gap=8)
    pipe(f, [("arrange\nbuild inputs, fresh state", C.BLUE), ("act\ncall the one thing", C.PURPLE),
             ("assert\ncompare with the claim", ACCENT)], h=42)
    code(f, """
        import sys, unittest
        from datetime import date, timedelta

        def late_fee(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 0 else min(days * per_day, cap)

        class LateFeeTest(unittest.TestCase):
            due = date(2026, 3, 1)

            def test_on_time_is_free(self):
                self.assertEqual(late_fee(self.due, self.due), 0.0)

            def test_per_day(self):
                self.assertEqual(late_fee(self.due, date(2026, 3, 5)), 1.0)

            def test_capped(self):
                self.assertEqual(late_fee(self.due, date(2026, 6, 1)), 5.0)

            def test_rejects_text(self):
                with self.assertRaises(TypeError):
                    late_fee(self.due, "2026-03-05")

        def run(*cases, v=1):                    # what `python -m unittest` does for you
            load = unittest.defaultTestLoader.loadTestsFromTestCase
            suite = unittest.TestSuite(load(c) for c in cases)
            unittest.TextTestRunner(stream=sys.stdout, verbosity=v).run(suite)

        run(LateFeeTest, v=2)
    """, notes={8: "subclass TestCase", 11: "every test_* method is one test",
                21: "the error is the expected behaviour"})
    f.p("A failing test tells you which claim broke and shows both values. Here the claim is wrong, not the "
        "code: floats can't hold 0.1 exactly (Ch 11), so compare money with a tolerance or use `Decimal`:",
        13.5, gap=8)
    code(f, """
        class TenPence(unittest.TestCase):
            def test_three_days(self):
                self.assertEqual(late_fee(date(2026, 3, 1), date(2026, 3, 4), per_day=0.1), 0.3)

        run(TenPence)
    """, out_max=16)
    table(f, ["assert method", "checks", "use it for"], [
        ["`assertEqual(a, b)`", "`a == b`, with a diff on failure", "most things; lists and dicts get a diff"],
        ["`assertAlmostEqual(a, b)`", "equal to 7 decimal places", "floats"],
        ["`assertTrue(x)` / `assertIn(a, b)`", "truthiness / membership", "flags, containers"],
        ["`assertRaises(E)` as a `with`", "the block raises `E`", "error paths (they need tests too)"],
        ["`self.subTest(**info)`", "labels one case in a loop", "table-driven tests (next)"],
    ], widths=[2.4, 2.3, 2.6], size=10.5)


def choosing_section(f):
    sec(f, "Which cases? Partitions and boundaries", room=290)
    f.p("You can't test every input, so split the inputs into {B:partitions} that should behave the same, test "
        "one from each, and add the {B:boundaries} between them, where off-by-one bugs live:", 13.5, gap=8)
    table(f, ["partition", "days late", "expected fee", "why this case"], [
        ["returned early", "`-3`", "`0.0`", "negative days must not give a refund"],
        ["on the due date", "`0`", "`0.0`", "boundary: `<` vs `<=`"],
        ["first late day", "`1`", "`0.25`", "boundary: the first charge"],
        ["just under the cap", "`19`", "`4.75`", "boundary below the cap"],
        ["exactly at the cap", "`20`", "`5.0`", "boundary: `min` kicks in"],
        ["far over the cap", "`90`", "`5.0`", "the cap holds"],
    ], widths=[1.8, 1.1, 1.2, 3.0], size=10.5)
    code(f, """
        class Boundaries(unittest.TestCase):
            def test_table(self):
                due = date(2026, 3, 1)
                for days, fee in [(-3, 0.0), (0, 0.0), (1, 0.25), (19, 4.75), (20, 5.0), (90, 5.0)]:
                    with self.subTest(days=days):
                        self.assertEqual(late_fee(due, due + timedelta(days)), fee)

        run(Boundaries)
    """, notes={5: "a failure names the case and keeps going"})
    sub(f, "setUp and addCleanup: a fresh world for every test", ACCENT, room=330)
    code(f, """
        import sqlite3

        class LoanStore(unittest.TestCase):
            def setUp(self):                              # runs before every test
                self.db = sqlite3.connect(":memory:")
                self.addCleanup(self.db.close)            # runs after, even if the test fails
                self.db.execute("CREATE TABLE loans (title TEXT, due TEXT)")

            def test_insert(self):
                self.db.execute("INSERT INTO loans VALUES ('Dune', '2026-03-01')")
                self.assertEqual(self.db.execute("SELECT count(*) FROM loans").fetchone(), (1,))

            def test_starts_empty(self):                  # test_insert's row is gone
                self.assertEqual(self.db.execute("SELECT count(*) FROM loans").fetchone(), (0,))

        run(LoanStore, v=2)
    """)
    callout(f, "rule", "Tests must not depend on each other or on their order. Each one builds what it needs "
            "(in `setUp`, or a temporary folder from `tempfile`) and leaves nothing behind. If a test passes "
            "alone but fails in the suite, some state is leaking.")


def doctest_mock_section(f):
    sec(f, "doctest: examples that can't go stale", room=440)
    f.p("A `>>>` example in a docstring documents the function {B:and} is a test: `doctest` runs it and compares "
        "the printed result. Good for small pure functions; use unittest for anything with setup.", 13.5, gap=8)
    code(f, """
        import doctest

        def fine(days_late, per_day=0.25, cap=5.0):
            '''Late fee for a book, capped.

            >>> fine(0)
            0.0
            >>> fine(4)
            1.0
            >>> fine(100)
            5.0
            '''
            return min(max(days_late, 0) * per_day, cap)

        runner = doctest.DocTestRunner()
        for test in doctest.DocTestFinder().find(fine, globs={"fine": fine}):
            runner.run(test)
        print(runner.summarize(verbose=False))
    """, notes={6: "the REPL session, pasted in", 16: "python -m doctest file.py does this"})
    sub(f, "How big should a test be?", ACCENT, room=260)
    f.p("A {B:unit} test checks one function on its own; an {B:integration} test checks pieces working "
        "together, with a real database or real files; an {B:end-to-end} test runs the whole program the way "
        "a user would. Aim for this shape:", 13.5, gap=8)
    pyramid_picture(f)
    sec(f, "unittest.mock: replacing the outside world", room=420)
    f.p("Some code talks to things a test can't use: a mail server, the network, the clock. A {B:test double} "
        "stands in for them. The cleanest seam is a parameter, so the test can pass a `Mock`, which accepts "
        "any call and records it:", 13.5, gap=8)
    code(f, """
        from unittest.mock import Mock

        def send_reminders(loans, today, mailer):
            for who, title, due in loans:
                if due < today:
                    mailer.send(who, f"'{title}' was due {due:%d %b}")

        mailer = Mock()
        loans = [("ana@x.org", "Dune", date(2026, 3, 1)), ("ben@x.org", "Emma", date(2026, 4, 1))]
        send_reminders(loans, date(2026, 3, 10), mailer)
        mailer.send.assert_called_once_with("ana@x.org", "'Dune' was due 01 Mar")
        print(mailer.send.call_count, mailer.send.call_args)
    """, notes={3: "the dependency comes in as an argument", 8: "no SMTP server needed",
                11: "raises AssertionError if not"})
    table(f, ["double", "what it does", "in Python"], [
        ["dummy", "fills a parameter, never used", "`None`, `object()`"],
        ["stub", "returns canned answers", "`Mock(return_value=...)`"],
        ["fake", "a real, simpler implementation", "sqlite `:memory:`, a dict, `io.StringIO`"],
        ["spy / mock", "records calls so you can check them", "`Mock()` + `assert_called_with`"],
    ], widths=[1.2, 2.8, 3.2], size=10.5)


def patch_section(f):
    sub(f, "patch: when you can't pass the dependency in", ACCENT, room=420)
    f.p("`patch` swaps a name for a `MagicMock` during a `with` block and puts the original back afterwards. "
        "`return_value` decides what the fake returns; `side_effect` makes it raise, so you can test the "
        "error path without unplugging the network:", 13.5, gap=8)
    code(f, """
        import io, json, urllib.request
        from unittest.mock import patch

        def book_title(isbn):
            url = f"https://openlibrary.org/isbn/{isbn}.json"
            with urllib.request.urlopen(url, timeout=5) as r:
                return json.load(r)["title"]

        with patch("urllib.request.urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value = io.BytesIO(b'{"title": "Dune"}')
            print(book_title("9780441013593"), "|", urlopen.call_args.args[0])

        with patch("urllib.request.urlopen", side_effect=TimeoutError("too slow")):
            try:
                book_title("9780441013593")
            except TimeoutError as e:
                print("error path tested:", e)
    """, notes={10: "what `with ... as r` will give", 13: "the fake raises instead"})
    callout(f, "trap", "Patch the name {B:where it is looked up}, not where it was defined. If `loans.py` did "
            "`from urllib.request import urlopen`, it holds its own reference, so you must patch "
            "`\"loans.urlopen\"`. Patching `urllib.request.urlopen` would leave that copy untouched.")
    callout(f, "why", "Mock too much and your tests check {B:how} the code works (which calls it makes) instead "
            "of {B:what} it achieves, so every refactor breaks them. Prefer fakes (an in-memory database, a "
            "temporary folder) and keep mocks for the edges of your program: network, mail, clock, randomness.")


def speed_section(f):
    sec(f, "Measure, then optimise", room=460)
    f.p("Programmers are famously bad at guessing where time goes. The professional loop never skips a step:",
        13.5, gap=8)
    pipe(f, [("is it too slow?\nhave a target", C.GREY), ("profile\nfind the hot spot", C.ORANGE),
             ("fix that one\nusually: data structure", C.PURPLE), ("measure again\nkeep the tests green", ACCENT)],
         h=42)
    code(f, """
        import cProfile, pstats

        def is_member(members, mid):
            return mid in members

        def report(n):
            members = [f"m{i:05}" for i in range(n)]
            loans = [f"m{i * 7 % (2 * n):05}" for i in range(n)]
            return sum(is_member(members, m) for m in loans)

        with cProfile.Profile() as prof:
            report(4000)
        funcs = pstats.Stats(prof).get_stats_profile().func_profiles
        for name, p in sorted(funcs.items(), key=lambda kv: -kv[1].tottime)[:3]:
            print(f"{name[:12]:12} calls={p.ncalls:>5}  own time={p.tottime:.3f} s")
    """, notes={4: "`in` on a list: a linear scan", 11: "record every call",
                14: "sort by time spent inside each function"})
    f.p("`is_member` takes nearly all the time, and it's called 4000 times, each scanning up to 4000 names. "
        "Change one line, membership in a `set` (Ch 10), then check it's faster {B:and} still gives the same "
        "answer:", 13.5, gap=8)
    code(f, """
        import timeit

        def report_fast(n):
            members = {f"m{i:05}" for i in range(n)}      # a set: the only change
            loans = [f"m{i * 7 % (2 * n):05}" for i in range(n)]
            return sum(is_member(members, m) for m in loans)

        assert report(4000) == report_fast(4000)
        for fn in (report, report_fast):
            t = min(timeit.repeat(lambda: fn(4000), number=3, repeat=3)) / 3
            print(f"{fn.__name__:12} {t * 1000:7.1f} ms")
    """, notes={8: "same result first", 10: "min of repeats: least noise"})
    callout(f, "honest", "Timings on this page were measured while building the book, so yours will differ. "
            "From the shell: `python3 -m timeit -s \"xs = list(range(1000))\" \"999 in xs\"` for one-liners, and "
            "`python3 -m cProfile -s tottime script.py` for a whole program. Profilers slow code down, so trust "
            "their proportions more than their seconds.")


def types_section(ch):
    f = flow(ch)
    sec(f, "Type hints, and a checker that reads them", room=230)
    f.p("Python checks types only at run time, and only when an operation fails. {B:Type hints} write your "
        "intent down; Python itself ignores them:", 13.5, gap=8)
    code(f, """
        def double(n: int) -> int:
            return n * 2

        print(double(21), double("ha"), double.__annotations__)
    """, notes={4: "runs fine: hints aren't enforced"})
    f.p("A separate {B:static checker}, `mypy` or `pyright` (both pip installs; editors run them as you type), "
        "reads the hints and finds the mismatch without running anything:", 13.5, gap=8)
    code(f, """
        from dataclasses import dataclass

        @dataclass
        class Loan:
            title: str
            days: int

        def double(n: int) -> int:
            return n * 2
        double("ha")

        def find(loans: list[Loan], title: str) -> Loan | None:
            return next((x for x in loans if x.title == title), None)
        print(find([], "Dune").title)
    """, run=False, title="loans.py")
    shell(f, """
        $ mypy loans.py
        loans.py:10: error: Argument 1 to "double" has incompatible type "str"; expected "int"  [arg-type]
        loans.py:14: error: Item "None" of "Loan | None" has no attribute "title"  [union-attr]
        Found 2 errors in 1 file (checked 1 source file)
    """, size=8.0)
    f.p("The second error is the valuable kind: `find` can return `None`, and the caller forgot. That bug would "
        "pass every test that happens to find the book, then crash in production.", 13.5, gap=8)
    table(f, ["write", "means"], [
        ["`list[str]`, `dict[str, int]`, `tuple[int, ...]`", "containers and what they hold"],
        ["`Loan | None`", "maybe missing: the checker makes you handle `None`"],
        ["`Callable[[int], str]`  (from `collections.abc`)", "a function taking an int, returning a str"],
        ["`Literal[\"due\", \"title\"]`", "only these exact values"],
        ["`def first[T](xs: list[T]) -> T:`  (3.12+)", "generic: the output type follows the input"],
        ["`class Mailer(Protocol): def send(...)`", "anything with a matching `send` method fits"],
    ], widths=[3.4, 3.3], size=10.5)
    code(f, """
        from typing import Protocol

        class Mailer(Protocol):
            def send(self, to: str, text: str) -> None: ...

        class PrintMailer:                             # never mentions Mailer
            def send(self, to: str, text: str) -> None:
                print(f"to {to}: {text}")

        def remind(m: Mailer) -> None:
            m.send("ana@x.org", "Dune is due")

        def first[T](items: list[T], default: T) -> T:
            return items[0] if items else default

        remind(PrintMailer())
        print(first([3, 1], 0), first([], "none"))
    """, notes={3: "structural: any class with this send fits", 11: "T: the checker knows first(...) is an int"})
    callout(f, "honest", "Hints are {B:gradual}: unannotated code is simply not checked, so you can add them one "
            "module at a time. They don't make Python faster. Since 3.14 annotations are evaluated lazily "
            "(PEP 649), so a hint can name a class defined further down the file.")


def packaging_section(ch):
    f = flow(ch)
    sec(f, "pyproject.toml: making it installable", room=280)
    f.p("A project others can install has a standard shape. The {B:src layout} keeps your package out of the "
        "current folder, so tests run against the {B:installed} code, exactly as users will (Ch 2's sys.path):",
        13.5, gap=8)
    tree(f, {
        "root": ("loans-project/", 0.5, 0),
        "py": ("pyproject.toml", 0.12, 1), "src": ("src/loans/", 0.45, 1), "tests": ("tests/", 0.82, 1),
        "init": ("__init__.py", 0.22, 2), "cli": ("cli.py", 0.43, 2), "fees": ("fees.py", 0.6, 2),
        "tf": ("test_fees.py", 0.84, 2),
    }, [("root", "py"), ("root", "src"), ("root", "tests"), ("src", "init"), ("src", "cli"), ("src", "fees"),
        ("tests", "tf")])
    code(f, '''
        import tomllib

        PYPROJECT = """
        [build-system]
        requires = ["setuptools>=77"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "loans"
        version = "0.3.0"
        requires-python = ">=3.12"
        dependencies = []

        [project.optional-dependencies]
        dev = ["mypy"]

        [project.scripts]
        loans = "loans.cli:main"
        """
        cfg = tomllib.loads(PYPROJECT)                 # the stdlib reads TOML (it can't write it)
        print(cfg["project"]["name"], cfg["project"]["version"], cfg["project"]["scripts"])
    ''', notes={5: "the tool that builds the package", 12: "runtime needs (Ch 19)",
                15: "extras: pip install -e '.[dev]'", 18: "a command → your main(argv=None)"})
    shell(f, """
        $ python3 -m venv .venv && source .venv/bin/activate
        (.venv) $ pip install -e ".[dev]"          # editable: edits in src/ apply at once
        (.venv) $ loans --help                     # the [project.scripts] entry point
        usage: loans [-h] [-v] {add,list} ...
        (.venv) $ python -m unittest discover -s tests
        ....
        ----------------------------------------------------------------------
        Ran 4 tests in 0.002s

        OK
        (.venv) $ python -m build                  # pip install build; output goes to dist/
        Successfully built loans-0.3.0.tar.gz and loans-0.3.0-py3-none-any.whl
    """, title="from a fresh clone to a running command and a wheel", size=8.4)
    callout(f, "why", "A {B:wheel} (`.whl`) is a zip of your package plus metadata; `pip install` just unpacks it "
            "into `site-packages`. `pyproject.toml` replaced `setup.py` so that any build tool (setuptools, "
            "hatchling, flit, uv) can read the same file. Which dependencies to trust is Ch 19.")


def git_section(ch):
    f = flow(ch)
    sec(f, "Git: every change, recorded and undoable", room=420)
    f.p("Git stores {B:snapshots} of your whole project, called commits. Each commit records its parent(s), "
        "its author and a message. A change travels from your folder into the repository, then out to a "
        "shared copy:", 13.5, gap=8)
    pipe(f, [("working folder\nfiles you edit", C.GREY), ("staging area\nthe next commit", C.ORANGE),
             ("repository\nall commits", C.BLUE), ("remote\nGitHub, a server", C.PURPLE)],
         labels=["git add", "git commit", "git push"], h=42)
    f.p("A {B:branch} is only a movable name pointing at one commit, so branching is instant. Do an experiment "
        "on a branch, then merge it: the merge commit has two parents.", 13.5, gap=8)
    commit_picture(f)
    shell(f, git_session(), title="a real session, run while building this page", size=8.6)
    table(f, ["everyday command", "does"], [
        ["`git status`, `git diff`", "what changed since the last commit (check before every commit)"],
        ["`git add -p`", "stage piece by piece: one commit = one logical change"],
        ["`git switch -c name` / `git merge name`", "start an experiment / bring it back"],
        ["`git restore file`", "throw away uncommitted edits to a file"],
        ["`git revert <commit>`", "a new commit that undoes an old one (safe on shared history)"],
    ], widths=[3.0, 3.8], size=10.5)
    callout(f, "trap", "A secret committed once stays in the history even after you delete the file, and anyone "
            "who clones gets it. Add `.env`, keys and `*.db` to `.gitignore` {B:before} the first commit. If a "
            "secret was ever pushed, {B:rotate it}: rewriting history doesn't remove copies people already have.")


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 17)
    stamp(f, [
        (2, "Dynamic and strong at run time. Optional hints (`list[str]`, `X | None`, `Protocol`, generics) are "
            "ignored by Python and checked statically by `mypy` or `pyright`."),
        (8, "`pyproject.toml` declares the package, dependencies and commands; `venv` + `pip install -e .` for "
            "development; wheels for distribution; src layout."),
        (11, "`unittest` (+ `subTest`, `setUp`, `addCleanup`), `doctest`, `unittest.mock`, `timeit`, "
             "`cProfile` + `pstats`, `tomllib`, `typing`. Outside: Git, mypy, build."),
    ])
    callout(f, "other", "Java: JUnit + Mockito, Maven/Gradle (`pom.xml`), static types checked by the compiler. "
            "Rust: `#[test]` and `cargo test`, `cargo bench`, `Cargo.toml`. C: no standard test framework, "
            "`make`/CMake, `perf`/`gprof`. TypeScript's types work exactly like Python's hints: checked by `tsc`, "
            "erased at run time. Git is the same in every language.")
    callout(f, "deep", "Vault notes: {b:12.3} Testing is executable claim checking · {b:12.4} Test selection by "
            "partitions and boundaries · {b:12.7} Test doubles and mocking · {b:12.9} Property-based and "
            "metamorphic testing · {b:12.10} Coverage and mutation testing · {b:12.18} Type hints · {b:12.19} "
            "Static analysis with mypy · {b:14.15} Microbenchmarking · {b:14.16} Profiling · {b:12.13} Git's "
            "object model · {b:12.14} Branching, merging, and conflicts · {b:12.21} Continuous integration.")


def build(ch):
    title_page(ch)
    f = flow(ch)
    unittest_section(f)
    choosing_section(f)
    doctest_mock_section(f)
    patch_section(f)
    speed_section(f)
    types_section(ch)
    packaging_section(ch)
    git_section(ch)
    finish(ch)
