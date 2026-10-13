EXERCISES = [
    dict(
        id="17.1", kind="build", title="Tests that catch bugs (the checker plants them)",
        task="""
        This time **you write the tests**. Add test methods to `LateFeeTests` for `late_fee`: no fee on or
        before the due date, `per_day` per day late, never more than `cap`, and both keyword arguments
        respected.
        The checker runs your tests against the real `late_fee` (they must all pass), then against six broken
        versions it swaps in (each must make at least one of your tests fail). Call `late_fee` by its
        module-level name inside your tests, so the swap reaches them. This is **mutation testing**, the honest
        way to ask whether your tests are any good.
        """,
        stub='''
        import unittest
        from datetime import date, timedelta

        def late_fee(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 0 else min(days * per_day, cap)

        class LateFeeTests(unittest.TestCase):
            def test_one_day_late(self):
                self.assertEqual(late_fee(date(2026, 3, 1), date(2026, 3, 2)), 0.25)
        ''',
        tests='''
        import io, unittest

        def real(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 0 else min(days * per_day, cap)

        def early_refund(due, returned, per_day=0.25, cap=5.0):
            return min((returned - due).days * per_day, cap)

        def off_by_one(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 0 else min((days + 1) * per_day, cap)

        def no_cap(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 0 else days * per_day

        def fixed_rate(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 0 else min(days * 0.25, cap)

        def fixed_cap(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 0 else min(days * per_day, 5.0)

        def grace_day(due, returned, per_day=0.25, cap=5.0):
            days = (returned - due).days
            return 0.0 if days <= 1 else min(days * per_day, cap)

        def suite_passes(m, impl):
            old = m.late_fee
            m.late_fee = impl
            try:
                cases = [v for v in vars(m).values()
                         if isinstance(v, type) and issubclass(v, unittest.TestCase) and v is not unittest.TestCase]
                suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in cases)
                r = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
                return r.testsRun, r.wasSuccessful()
            finally:
                m.late_fee = old

        def caught(m, impl, what):
            n, ok = suite_passes(m, impl)
            check(not ok, f"a late_fee that {what} still passes all your tests")

        def test_real_passes(m):
            n, ok = suite_passes(m, real)
            check(n >= 3, f"write at least 3 tests (found {n})")
            check(ok, "your tests must all pass on the correct late_fee")

        def test_early_refund(m):
            caught(m, early_refund, "gives a refund when a book comes back early")

        def test_off_by_one(m):
            caught(m, off_by_one, "charges one day too many")

        def test_no_cap(m):
            caught(m, no_cap, "ignores the cap")

        def test_fixed_rate(m):
            caught(m, fixed_rate, "ignores per_day")

        def test_fixed_cap(m):
            caught(m, fixed_cap, "ignores the cap argument")

        def test_grace_day(m):
            caught(m, grace_day, "lets the first late day go free")
        ''',
        alts={
            "one test per partition and boundary": ('''
                import unittest
                from datetime import date, timedelta

                def late_fee(due, returned, per_day=0.25, cap=5.0):
                    days = (returned - due).days
                    return 0.0 if days <= 0 else min(days * per_day, cap)

                DUE = date(2026, 3, 1)

                def back(days):
                    return DUE + timedelta(days)

                class LateFeeTests(unittest.TestCase):
                    def test_early_is_free(self):
                        self.assertEqual(late_fee(DUE, back(-3)), 0.0)

                    def test_on_the_day_is_free(self):
                        self.assertEqual(late_fee(DUE, back(0)), 0.0)

                    def test_first_late_day(self):
                        self.assertEqual(late_fee(DUE, back(1)), 0.25)

                    def test_just_under_cap(self):
                        self.assertEqual(late_fee(DUE, back(19)), 4.75)

                    def test_capped(self):
                        self.assertEqual(late_fee(DUE, back(90)), 5.0)

                    def test_custom_rate(self):
                        self.assertEqual(late_fee(DUE, back(4), per_day=0.5), 2.0)

                    def test_custom_cap(self):
                        self.assertEqual(late_fee(DUE, back(90), cap=2.0), 2.0)
            ''', "Each test names the claim it checks, so a failure reads like a sentence. The partitions and "
                 "boundaries from the chapter's table pick the cases; the keyword tests cover the parameters."),
            "table-driven with subTest": ('''
                import unittest
                from datetime import date, timedelta

                def late_fee(due, returned, per_day=0.25, cap=5.0):
                    days = (returned - due).days
                    return 0.0 if days <= 0 else min(days * per_day, cap)

                CASES = [  # (days late, kwargs, expected)
                    (-3, {}, 0.0), (0, {}, 0.0), (1, {}, 0.25), (19, {}, 4.75), (20, {}, 5.0), (90, {}, 5.0),
                    (4, {"per_day": 0.5}, 2.0), (90, {"cap": 2.0}, 2.0), (3, {"per_day": 1.0, "cap": 2.5}, 2.5),
                ]

                class LateFeeTests(unittest.TestCase):
                    def test_table(self):
                        due = date(2026, 3, 1)
                        for days, kw, want in CASES:
                            with self.subTest(days=days, **kw):
                                self.assertAlmostEqual(late_fee(due, due + timedelta(days), **kw), want)

                    def test_type_error_for_text(self):
                        with self.assertRaises(TypeError):
                            late_fee(date(2026, 3, 1), "2026-03-02")

                    def test_never_negative(self):
                        due = date(2026, 3, 1)
                        for d in range(-30, 30):
                            self.assertGreaterEqual(late_fee(due, due + timedelta(d)), 0.0)
            ''', "Adding a case is one line in the table. The last test states a property (never negative) "
                 "over many inputs: a small taste of property-based testing (vault 12.9)."),
        },
    ),
    dict(
        id="17.2", kind="fix", title="Tests that pass alone but fail together",
        task="""
        `Library` is correct. Its **tests** are broken: they share one `Library` object, so each test depends on
        what the others did before it. Fix the tests, not the class:
        - each test must pass when run alone, in the normal order and in reverse order;
        - keep at least 4 tests, covering lending, lending a book that's already out (`ValueError`), giving a
          book back, and `out()` being sorted;
        - the checker swaps in broken `Library` classes, and your tests must catch each one. Create the library
          inside each test or in `setUp`, by its module-level name `Library`.
        """,
        stub='''
        import unittest

        class Library:
            def __init__(self):
                self.loans = {}

            def lend(self, title, who):
                if title in self.loans:
                    raise ValueError(f"{title} is already out")
                self.loans[title] = who

            def give_back(self, title):
                del self.loans[title]

            def out(self):
                return sorted(self.loans)

        class LibraryTests(unittest.TestCase):
            lib = Library()                        # one object shared by every test

            def test_lend(self):
                self.lib.lend("Dune", "ana")
                self.assertEqual(self.lib.out(), ["Dune"])

            def test_double_lend(self):
                with self.assertRaises(ValueError):
                    self.lib.lend("Dune", "ben")

            def test_give_back(self):
                self.lib.give_back("Dune")
                self.assertEqual(self.lib.out(), [])
        ''',
        tests='''
        import io, unittest

        class Real:
            def __init__(self):
                self.loans = {}
            def lend(self, title, who):
                if title in self.loans:
                    raise ValueError(f"{title} is already out")
                self.loans[title] = who
            def give_back(self, title):
                del self.loans[title]
            def out(self):
                return sorted(self.loans)

        class NoDuplicateCheck(Real):
            def lend(self, title, who):
                self.loans[title] = who

        class ForgetfulReturn(Real):
            def give_back(self, title):
                pass

        class Unsorted(Real):
            def out(self):
                return list(self.loans)[::-1]

        def all_tests(m):
            cases = [v for v in vars(m).values()
                     if isinstance(v, type) and issubclass(v, unittest.TestCase) and v is not unittest.TestCase]
            return [c(n) for c in cases for n in unittest.defaultTestLoader.getTestCaseNames(c)]

        def passes(m, lib, tests):
            old = m.Library
            m.Library = lib
            try:
                r = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(unittest.TestSuite(tests))
                return r.wasSuccessful()
            finally:
                m.Library = old

        def test_count(m):
            check(len(all_tests(m)) >= 4, "keep at least 4 tests")

        def test_any_order(m):
            check(passes(m, Real, all_tests(m)), "the tests fail in the normal order")
            check(passes(m, Real, all_tests(m)[::-1]), "the tests fail in reverse order")
            for t in all_tests(m):
                check(passes(m, Real, [t]), f"{t.id()} fails when run on its own")

        def test_catches_duplicate_lending(m):
            check(not passes(m, NoDuplicateCheck, all_tests(m)), "a Library that lends the same book twice passes")

        def test_catches_forgetful_return(m):
            check(not passes(m, ForgetfulReturn, all_tests(m)), "a Library whose give_back does nothing passes")

        def test_catches_unsorted(m):
            check(not passes(m, Unsorted, all_tests(m)), "a Library whose out() isn't sorted passes")
        ''',
        alts={
            "setUp builds a fresh Library": ('''
                import unittest

                class Library:
                    def __init__(self):
                        self.loans = {}

                    def lend(self, title, who):
                        if title in self.loans:
                            raise ValueError(f"{title} is already out")
                        self.loans[title] = who

                    def give_back(self, title):
                        del self.loans[title]

                    def out(self):
                        return sorted(self.loans)

                class LibraryTests(unittest.TestCase):
                    def setUp(self):
                        self.lib = Library()               # a new one before every test

                    def test_lend(self):
                        self.lib.lend("Dune", "ana")
                        self.assertEqual(self.lib.out(), ["Dune"])

                    def test_double_lend(self):
                        self.lib.lend("Dune", "ana")       # arrange its own precondition
                        with self.assertRaises(ValueError):
                            self.lib.lend("Dune", "ben")

                    def test_give_back(self):
                        self.lib.lend("Dune", "ana")
                        self.lib.give_back("Dune")
                        self.assertEqual(self.lib.out(), [])

                    def test_out_sorted(self):
                        for t in ["Emma", "Dune", "Ulysses"]:
                            self.lib.lend(t, "ana")
                        self.assertEqual(self.lib.out(), ["Dune", "Emma", "Ulysses"])
            ''', "Two fixes: setUp gives each test its own object, and each test arranges its own starting "
                 "state instead of hoping an earlier test did. The sorted test lends out of order on purpose."),
            "a helper that returns a ready library": ('''
                import unittest

                class Library:
                    def __init__(self):
                        self.loans = {}

                    def lend(self, title, who):
                        if title in self.loans:
                            raise ValueError(f"{title} is already out")
                        self.loans[title] = who

                    def give_back(self, title):
                        del self.loans[title]

                    def out(self):
                        return sorted(self.loans)

                def library_with(*titles):
                    lib = Library()
                    for t in titles:
                        lib.lend(t, "ana")
                    return lib

                class LibraryTests(unittest.TestCase):
                    def test_lend(self):
                        self.assertEqual(library_with("Dune").out(), ["Dune"])

                    def test_double_lend(self):
                        lib = library_with("Dune")
                        self.assertRaises(ValueError, lib.lend, "Dune", "ben")

                    def test_give_back(self):
                        lib = library_with("Dune", "Emma")
                        lib.give_back("Dune")
                        self.assertEqual(lib.out(), ["Emma"])

                    def test_out_sorted(self):
                        lib = library_with("Emma", "Dune", "Ulysses")       # reversed or insertion order both fail
                        self.assertEqual(lib.out(), ["Dune", "Emma", "Ulysses"])
            ''', "A factory function (a 'test data builder') makes each test's starting state visible in one "
                 "line. No shared state at all, so order can't matter."),
        },
    ),
    dict(
        id="17.3", kind="refactor", title="Make the reminder job testable",
        task="""
        `remind_overdue()` reads the clock and connects to a mail server itself, so it can't be tested. Rewrite it
        as `remind_overdue(loans, today, mailer)`, where `loans` is a list of `(email, title, due)` tuples and
        `mailer.send(to, subject, body)` sends one email. Also:
        - a loan is overdue if `due < today`; skip loans with an empty email;
        - send **one** email per person, in alphabetical order of address;
        - the subject is `"1 overdue book"` or `"N overdue books"`;
        - the body has one line per book, `Title (due YYYY-MM-DD)`, oldest due date first;
        - return the number of emails sent.
        The tests pass a `Mock` as the mailer and make sure no real SMTP connection is opened.
        """,
        stub='''
        import smtplib
        from datetime import date
        from email.message import EmailMessage

        LOANS = [("ana@x.org", "Dune", date(2026, 3, 1)), ("ben@x.org", "Emma", date(2026, 4, 1))]

        def remind_overdue():
            today = date.today()
            with smtplib.SMTP("localhost") as smtp:
                for who, title, due in LOANS:
                    if due < today:
                        msg = EmailMessage()
                        msg["To"], msg["Subject"] = who, "Overdue book"
                        msg.set_content(f"'{title}' was due on {due}.")
                        smtp.send_message(msg)
        ''',
        tests='''
        import inspect
        from datetime import date
        from unittest.mock import Mock, patch

        LOANS = [
            ("ben@x.org", "Emma", date(2026, 3, 5)),
            ("ana@x.org", "Dune", date(2026, 3, 1)),
            ("ana@x.org", "Ulysses", date(2026, 2, 20)),
            ("", "Beloved", date(2026, 1, 1)),
            ("cy@x.org", "Middlemarch", date(2026, 4, 1)),
            ("ana@x.org", "Kindred", date(2026, 5, 1)),
        ]

        def sent(m, today, loans=LOANS):
            mailer = Mock()
            with patch("smtplib.SMTP", side_effect=AssertionError("tests must not open a real SMTP connection")):
                n = m.remind_overdue(list(loans), today, mailer)
            calls = []
            for c in mailer.send.call_args_list:
                calls.append(tuple(c.args) + tuple(c.kwargs[k] for k in ("to", "subject", "body") if k in c.kwargs))
            return n, calls

        def test_signature(m):
            equal(len(inspect.signature(m.remind_overdue).parameters), 3, "remind_overdue(loans, today, mailer)")

        def test_grouped(m):
            n, calls = sent(m, date(2026, 3, 10))
            equal(calls, [("ana@x.org", "2 overdue books", "Ulysses (due 2026-02-20)\\nDune (due 2026-03-01)"),
                          ("ben@x.org", "1 overdue book", "Emma (due 2026-03-05)")], "emails sent")
            equal(n, 2, "return value")

        def test_today_is_used(m):
            equal(sent(m, date(2026, 1, 1)), (0, []), "nothing overdue yet (the blank email is skipped)")
            n, calls = sent(m, date(2026, 3, 5))
            equal([c[0] for c in calls], ["ana@x.org"], "due today is not overdue")
            n, calls = sent(m, date(2027, 1, 1))
            equal(n, 3, "a year later everyone with an email is overdue")
            equal(calls[0][1:], ("3 overdue books", "Ulysses (due 2026-02-20)\\nDune (due 2026-03-01)\\n"
                                 "Kindred (due 2026-05-01)"), "three books in one email, oldest first")

        def test_empty(m):
            equal(sent(m, date(2026, 3, 10), []), (0, []), "no loans")
        ''',
        alts={
            "group with a dict of lists": ('''
                from collections import defaultdict

                def remind_overdue(loans, today, mailer):
                    by_person = defaultdict(list)
                    for who, title, due in loans:
                        if who and due < today:
                            by_person[who].append((due, title))
                    for who in sorted(by_person):
                        books = sorted(by_person[who])
                        n = len(books)
                        subject = f"{n} overdue book" + ("" if n == 1 else "s")
                        body = "\\n".join(f"{title} (due {due:%Y-%m-%d})" for due, title in books)
                        mailer.send(who, subject, body)
                    return len(by_person)
            ''', "The function now only decides what to send; the mailer does the sending. Real code passes an "
                 "SMTP-backed mailer, tests pass a Mock, and both satisfy the same small interface (a Protocol)."),
            "sort then itertools.groupby, plus the real mailer": ('''
                import smtplib
                from email.message import EmailMessage
                from itertools import groupby
                from operator import itemgetter

                class SmtpMailer:                          # the production adapter: thin, and not unit-tested
                    def __init__(self, host="localhost"):
                        self.host = host

                    def send(self, to, subject, body):
                        msg = EmailMessage()
                        msg["To"], msg["Subject"] = to, subject
                        msg.set_content(body)
                        with smtplib.SMTP(self.host) as smtp:
                            smtp.send_message(msg)

                def remind_overdue(loans, today, mailer):
                    late = sorted((who, due, title) for who, title, due in loans if who and due < today)
                    count = 0
                    for who, rows in groupby(late, key=itemgetter(0)):
                        rows = list(rows)
                        subject = f"{len(rows)} overdue book{'s' if len(rows) != 1 else ''}"
                        mailer.send(who, subject, "\\n".join(f"{t} (due {d.isoformat()})" for _, d, t in rows))
                        count += 1
                    return count
            ''', "groupby needs its input sorted by the key, which also gives alphabetical addresses and oldest-"
                 "first books in one sort. The SmtpMailer adapter stays so small it barely needs a test."),
        },
    ),
    dict(
        id="17.4", kind="time", title="Profile it, then make it fast",
        task="""
        `busiest_borrowers(loans, k)` is correct but far too slow for a real library. `loans` is a list of
        `(member_id, title)` pairs (repeats allowed). It returns the `k` members with the most **distinct**
        titles as `(member_id, count)` pairs, most first, ties broken by smaller `member_id`.
        Run `cProfile` on it first to see where the time goes, then make it fast enough for 25,000 loans in
        under 0.2 s without changing the results.
        """,
        stub='''
        def busiest_borrowers(loans, k=3):
            members = []
            for mid, _ in loans:
                if mid not in members:
                    members.append(mid)
            result = []
            for mid in members:
                titles = []
                for other, title in loans:
                    if other == mid and title not in titles:
                        titles.append(title)
                result.append((mid, len(titles)))
            result.sort(key=lambda p: (-p[1], p[0]))
            return result[:k]
        ''',
        tests='''
        import random, time

        def reference(loans, k=3):
            seen = {}
            for mid, t in loans:
                seen.setdefault(mid, set()).add(t)
            return sorted(((mid, len(ts)) for mid, ts in seen.items()), key=lambda p: (-p[1], p[0]))[:k]

        def make(n, members, titles, seed):
            rng = random.Random(seed)
            return [(rng.randrange(members), f"t{rng.randrange(titles)}") for _ in range(n)]

        def test_small(m):
            equal(m.busiest_borrowers([(1, "a"), (2, "a"), (2, "b"), (2, "b"), (3, "c"), (3, "d")], 2),
                  [(2, 2), (3, 2)], "distinct titles; tie broken by smaller id")
            equal(m.busiest_borrowers([], 3), [], "no loans")
            equal(m.busiest_borrowers([(5, "x")], 3), [(5, 1)], "fewer members than k")

        def test_random(m):
            for seed in range(6):
                loans = make(300, 25, 40, seed)
                equal(m.busiest_borrowers(loans, 5), reference(loans, 5), f"random case {seed}")

        def test_fast(m):
            loans = make(25_000, 2_500, 5_000, 99)
            t0 = time.perf_counter()
            got = m.busiest_borrowers(loans, 10)
            took = time.perf_counter() - t0
            equal(got, reference(loans, 10), "same answer on the big input")
            check(took < 0.2, f"took {took:.2f} s on 25,000 loans; budget 0.2 s")
        ''',
        alts={
            "a dict of sets, then sort": ('''
                def busiest_borrowers(loans, k=3):
                    titles = {}
                    for mid, title in loans:
                        titles.setdefault(mid, set()).add(title)      # O(1) membership instead of a list scan
                    ranked = sorted(titles.items(), key=lambda kv: (-len(kv[1]), kv[0]))
                    return [(mid, len(ts)) for mid, ts in ranked[:k]]
            ''', "The profile shows two hot spots, both `in` on a list inside a loop over every loan: O(n x members). "
                 "One pass with sets makes it O(n); the sort is O(members log members)."),
            "dedupe pairs with a set, count with Counter, heapq for top k": ('''
                import heapq
                from collections import Counter

                def busiest_borrowers(loans, k=3):
                    counts = Counter(mid for mid, _ in set(loans))    # each (member, title) once
                    return heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))
            ''', "set(loans) removes repeat borrowings in one step, Counter counts, and nsmallest finds the top k "
                 "without sorting everyone: O(members log k). Three stdlib tools, one line each."),
        },
    ),
    dict(
        id="17.5", kind="explore", title="Documentation that tests itself",
        task="""
        Write `parse_duration(text)`, turning loan periods like `"2w3d"` into days (`w` = 7, `d` = 1). Upper
        and lower case are fine, spaces are allowed around the parts, each unit appears at most once, in either
        order. Anything else (empty text, unknown units, a bare number, a repeated unit) raises `ValueError`.
        The docstring must hold **at least 5** `>>>` examples that `doctest` passes, including one that shows
        the `ValueError` (look up how doctest writes an expected traceback: `help(doctest)`, or the docs).
        """,
        stub='''
        def parse_duration(text):
            """Turn a loan period like '2w3d' into a number of days.

            >>> parse_duration("2w3d")
            17
            """
            raise NotImplementedError
        ''',
        tests='''
        import doctest

        def test_doctests(m):
            finder = doctest.DocTestFinder()
            found = finder.find(m.parse_duration, globs={"parse_duration": m.parse_duration})
            examples = [ex for t in found for ex in t.examples]
            check(len(examples) >= 5, f"the docstring needs at least 5 examples (found {len(examples)})")
            check(any(ex.exc_msg for ex in examples), "one example must show the ValueError traceback")
            runner, out = doctest.DocTestRunner(verbose=False), []
            failed = sum(runner.run(t, out=out.append).failed for t in found)
            check(failed == 0, "doctest failures:\\n" + "".join(out))

        def test_values(m):
            for text, days in [("2w3d", 17), ("10d", 10), ("1w", 7), ("2W 3D", 17), (" 3d ", 3),
                               ("3d2w", 17), ("0d", 0), ("12w", 84)]:
                equal(m.parse_duration(text), days, repr(text))

        def test_errors(m):
            for bad in ["", "   ", "3x", "w", "3", "d3", "3d3d", "2w 1w", "3.5d", "-1d"]:
                raises(ValueError, m.parse_duration, bad)
        ''',
        alts={
            "re.fullmatch for the shape, findall for the parts": ('''
                import re

                PART = re.compile(r"\\s*(\\d+)\\s*([wd])\\s*", re.IGNORECASE)

                def parse_duration(text):
                    """Turn a loan period like '2w3d' into a number of days.

                    >>> parse_duration("2w3d")
                    17
                    >>> parse_duration("10d")
                    10
                    >>> parse_duration("3D 1W")
                    10
                    >>> parse_duration("0d")
                    0
                    >>> parse_duration("3x")
                    Traceback (most recent call last):
                        ...
                    ValueError: bad duration: '3x'
                    """
                    if not re.fullmatch(f"(?:{PART.pattern})+", text, re.IGNORECASE):
                        raise ValueError(f"bad duration: {text!r}")
                    parts = [(int(n), unit.lower()) for n, unit in PART.findall(text)]
                    units = [u for _, u in parts]
                    if len(units) != len(set(units)):
                        raise ValueError(f"bad duration: {text!r}")
                    return sum(n * {"w": 7, "d": 1}[u] for n, u in parts)
            ''', "doctest only compares the traceback's first and last lines, so `...` stands for the middle. "
                 "fullmatch checks the whole string has the right shape; findall then pulls out the parts."),
            "a hand-written scanner": ('''
                def parse_duration(text):
                    """Days in a loan period: w = 7 days, d = 1 day.

                    >>> parse_duration("1w")
                    7
                    >>> parse_duration(" 2w 3d ")
                    17
                    >>> parse_duration("3d2w")
                    17
                    >>> [parse_duration(s) for s in ("1d", "2W")]
                    [1, 14]
                    >>> parse_duration("3d3d")
                    Traceback (most recent call last):
                    ValueError: 'd' appears twice in '3d3d'
                    """
                    total, seen, digits = 0, set(), ""
                    for ch in text.lower() + " ":
                        if ch.isdigit() and ch.isascii():
                            digits += ch
                        elif ch in "wd":
                            if not digits or ch in seen:
                                raise ValueError(f"{ch!r} appears twice in {text!r}" if ch in seen
                                                 else f"no number before {ch!r} in {text!r}")
                            total += int(digits) * (7 if ch == "w" else 1)
                            seen.add(ch)
                            digits = ""
                        elif ch.isspace():
                            if digits:
                                raise ValueError(f"number without a unit in {text!r}")
                        else:
                            raise ValueError(f"unexpected {ch!r} in {text!r}")
                    if not seen:
                        raise ValueError(f"empty duration: {text!r}")
                    return total
            ''', "No regex: one pass, one character at a time, with a specific message for each mistake. The "
                 "traceback example may skip the middle lines entirely; doctest only needs the header and the error."),
        },
    ),
    dict(
        id="17.6", kind="explore", title="Read type hints at run time",
        task="""
        Python ignores type hints, but a program can read them. Explore `typing.get_type_hints`,
        `typing.get_origin` and `typing.get_args`, then write a decorator `checked` that raises `TypeError` when
        an argument or the return value doesn't match its hint. The message must name the parameter (or say
        `return`). Support plain classes, `float` (which also accepts `int`, as type checkers do), `list[X]`,
        `dict[K, V]`, `tuple[X, Y]`, `tuple[X, ...]`, `X | Y` (including `X | None`) and `typing.Any`. Skip
        parameters without hints, and keep the function's name (`functools.wraps`).
        """,
        stub='''
        import functools, typing

        def checked(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)
            return wrapper
        ''',
        tests='''
        from typing import Any

        def expect_error(fn, word, *args, **kwargs):
            try:
                fn(*args, **kwargs)
            except TypeError as e:
                check(word in str(e), f"the TypeError should mention {word!r}: got {e}")
            else:
                check(False, f"{fn.__name__}{args} should raise TypeError")

        def test_simple(m):
            @m.checked
            def lend(title: str, days: int = 14, note=None) -> str:
                return f"{title}:{days}"
            equal(lend("Dune"), "Dune:14", "valid call")
            equal(lend(title="Emma", days=3, note=object()), "Emma:3", "keywords; unhinted note is not checked")
            expect_error(lend, "days", "Dune", "14")
            expect_error(lend, "title", 42)
            expect_error(lambda: lend(days="x", title="Dune"), "days")
            equal(lend.__name__, "lend", "functools.wraps keeps the name")

        def test_containers(m):
            @m.checked
            def total(prices: list[float]) -> float:
                return sum(prices)
            equal(total([1, 2.5]), 3.5, "int is fine where float is expected")
            expect_error(total, "prices", [1, "2"])
            expect_error(total, "prices", (1, 2))

            @m.checked
            def find(index: dict[str, int], key: str) -> int | None:
                return index.get(key)
            equal(find({"a": 1}, "b"), None, "None allowed by int | None")
            expect_error(find, "index", {"a": "1"}, "a")

            @m.checked
            def span(p: tuple[int, int], tags: tuple[str, ...] = ()) -> int:
                return p[1] - p[0]
            equal(span((1, 4), ("a", "b")), 3, "fixed and variable tuples")
            expect_error(span, "p", (1, 2, 3))
            expect_error(span, "tags", (1, 2), ("a", 1))

        def test_return_and_any(m):
            @m.checked
            def bad() -> int:
                return "x"
            expect_error(bad, "return")

            @m.checked
            def anything(x: Any) -> Any:
                return x
            equal(anything([object()]) is not None, True, "Any accepts everything")

            class Loan:
                pass

            @m.checked
            def title_of(loan: Loan) -> str:
                return "Dune"
            equal(title_of(Loan()), "Dune", "own classes")
            expect_error(title_of, "loan", "Dune")
        ''',
        alts={
            "recursive matcher on get_origin/get_args": ('''
                import functools, inspect, types, typing

                def matches(value, hint):
                    if hint is typing.Any:
                        return True
                    if hint is float:
                        return isinstance(value, (int, float))
                    origin, args = typing.get_origin(hint), typing.get_args(hint)
                    if origin in (typing.Union, types.UnionType):
                        return any(matches(value, a) for a in args)
                    if origin is list:
                        return isinstance(value, list) and all(matches(v, args[0]) for v in value)
                    if origin is dict:
                        return isinstance(value, dict) and all(
                            matches(k, args[0]) and matches(v, args[1]) for k, v in value.items())
                    if origin is tuple:
                        if not isinstance(value, tuple):
                            return False
                        if len(args) == 2 and args[1] is Ellipsis:
                            return all(matches(v, args[0]) for v in value)
                        return len(value) == len(args) and all(map(matches, value, args))
                    return isinstance(value, origin or hint)

                def checked(fn):
                    hints = typing.get_type_hints(fn)
                    sig = inspect.signature(fn)

                    @functools.wraps(fn)
                    def wrapper(*args, **kwargs):
                        bound = sig.bind(*args, **kwargs)
                        bound.apply_defaults()
                        for name, value in bound.arguments.items():
                            if name in hints and not matches(value, hints[name]):
                                raise TypeError(f"{name}={value!r} is not {hints[name]}")
                        result = fn(*args, **kwargs)
                        if "return" in hints and not matches(result, hints["return"]):
                            raise TypeError(f"return value {result!r} is not {hints['return']}")
                        return result
                    return wrapper
            ''', "get_origin(list[int]) is list and get_args gives (int,), so one recursive function walks any "
                 "nesting. signature.bind lines positional and keyword arguments up with parameter names."),
            "a table of handlers by origin": ('''
                import functools, inspect, types, typing

                def _union(v, args):
                    return any(ok(v, a) for a in args)

                def _list(v, args):
                    return isinstance(v, list) and all(ok(x, args[0]) for x in v)

                def _dict(v, args):
                    return isinstance(v, dict) and all(ok(a, args[0]) and ok(b, args[1]) for a, b in v.items())

                def _tuple(v, args):
                    if not isinstance(v, tuple):
                        return False
                    if args[-1:] == (Ellipsis,):
                        return all(ok(x, args[0]) for x in v)
                    return len(v) == len(args) and all(ok(x, a) for x, a in zip(v, args))

                HANDLERS = {typing.Union: _union, types.UnionType: _union, list: _list, dict: _dict, tuple: _tuple}

                def ok(v, hint):
                    if hint is typing.Any:
                        return True
                    if hint is float:
                        hint = (int, float)
                    handler = HANDLERS.get(typing.get_origin(hint))
                    return handler(v, typing.get_args(hint)) if handler else isinstance(v, hint)

                def checked(fn):
                    hints, sig = typing.get_type_hints(fn), inspect.signature(fn)

                    @functools.wraps(fn)
                    def wrapper(*args, **kwargs):
                        for name, v in sig.bind(*args, **kwargs).arguments.items():
                            if name in hints and not ok(v, hints[name]):
                                raise TypeError(f"argument {name!r} got {type(v).__name__}, wants {hints[name]}")
                        out = fn(*args, **kwargs)
                        if "return" in hints and not ok(out, hints["return"]):
                            raise TypeError(f"return got {type(out).__name__}, wants {hints['return']}")
                        return out
                    return wrapper
            ''', "Dispatch through a dict instead of an if-chain: supporting set[X] is one new handler and one "
                 "entry. Libraries like pydantic and typeguard are this idea, industrial-strength."),
        },
    ),
    dict(
        id="17.7", kind="project", title="Scaffold an installable project",
        task="""
        Mini-project. Write `scaffold(root, name, version="0.1.0")` that creates a complete src-layout project
        in the folder `root` (raise `ValueError` if `name` isn't a valid identifier):
        - `pyproject.toml`: valid TOML with `[build-system]`, `[project]` (`name`, `version`,
          `requires-python`) and `[project.scripts]` mapping `name` to `"<name>.cli:main"`;
        - `src/<name>/__init__.py` defining `__version__`; `src/<name>/__main__.py` so `python -m <name>` works;
        - `src/<name>/cli.py` with `main(argv=None)`: `--version` prints `<name> <version>`, and
          `hello WHO` prints `hello, WHO` and returns 0;
        - `tests/test_cli.py`: at least 2 tests that pass under `python -m unittest discover -s tests` (run with
          `PYTHONPATH=src`), and that fail if the greeting breaks;
        - `.gitignore` listing at least `.venv/`, `__pycache__/` and `dist/`.
        """,
        stub='''
        from pathlib import Path

        def scaffold(root, name, version="0.1.0"):
            root = Path(root)
            (root / "src" / name).mkdir(parents=True)
            (root / "pyproject.toml").write_text("")
            return root
        ''',
        tests='''
        import os, subprocess, sys, tomllib
        from pathlib import Path

        def run(root, *args):
            env = {**os.environ, "PYTHONPATH": "src"}
            return subprocess.run([sys.executable, *args], cwd=root, env=env, capture_output=True, text=True,
                                  timeout=30)

        def test_bad_names(m):
            with tmpdir() as d:
                for bad in ["my-app", "1abc", ""]:
                    raises(ValueError, m.scaffold, Path(d) / "x", bad)

        def test_pyproject(m):
            with tmpdir() as d:
                m.scaffold(d, "shelfie", "0.4.2")
                cfg = tomllib.loads((Path(d) / "pyproject.toml").read_text())
                equal((cfg["project"]["name"], cfg["project"]["version"]), ("shelfie", "0.4.2"), "[project]")
                check("requires-python" in cfg["project"], "requires-python is set")
                equal(cfg["project"]["scripts"], {"shelfie": "shelfie.cli:main"}, "[project.scripts]")
                check("build-backend" in cfg.get("build-system", {}), "[build-system] names a build backend")
                ignore = (Path(d) / ".gitignore").read_text().split()
                check({".venv/", "__pycache__/", "dist/"} <= set(ignore), ".gitignore entries")

        def test_runs(m):
            with tmpdir() as d:
                m.scaffold(d, "shelfie", "0.4.2")
                r = run(d, "-m", "shelfie", "--version")
                equal(r.stdout.strip(), "shelfie 0.4.2", f"python -m shelfie --version (stderr: {r.stderr[-300:]})")
                r = run(d, "-m", "shelfie", "hello", "Ana")
                equal((r.returncode, r.stdout.strip()), (0, "hello, Ana"), "python -m shelfie hello Ana")

        def test_own_tests(m):
            with tmpdir() as d:
                m.scaffold(d, "shelfie")
                r = run(d, "-m", "unittest", "discover", "-s", "tests")
                check(r.returncode == 0, f"the generated tests fail:\\n{r.stderr[-600:]}")
                ran = [l for l in r.stderr.splitlines() if l.startswith("Ran ")]
                check(ran and int(ran[0].split()[1]) >= 2, "at least 2 generated tests")
                cli = Path(d) / "src" / "shelfie" / "cli.py"
                text = cli.read_text()
                check("hello, " in text, "cli.py should contain the greeting 'hello, '")
                cli.write_text(text.replace("hello, ", "helo, "))
                r = run(d, "-m", "unittest", "discover", "-s", "tests")
                check(r.returncode != 0, "the generated tests still pass after the greeting was broken")
        ''',
        alts={
            "a dict of path -> content": ('''
                from pathlib import Path

                def scaffold(root, name, version="0.1.0"):
                    if not name.isidentifier():
                        raise ValueError(f"{name!r} is not a valid package name")
                    root = Path(root)
                    files = {
                        "pyproject.toml": [
                            "[build-system]",
                            'requires = ["setuptools>=77"]',
                            'build-backend = "setuptools.build_meta"',
                            "",
                            "[project]",
                            f'name = "{name}"',
                            f'version = "{version}"',
                            'requires-python = ">=3.12"',
                            "",
                            "[project.scripts]",
                            f'{name} = "{name}.cli:main"',
                        ],
                        f"src/{name}/__init__.py": [f'__version__ = "{version}"'],
                        f"src/{name}/__main__.py": ["import sys", "from .cli import main", "", "sys.exit(main())"],
                        f"src/{name}/cli.py": [
                            "import argparse",
                            f"from {name} import __version__",
                            "",
                            "def main(argv=None):",
                            f'    p = argparse.ArgumentParser(prog="{name}")',
                            f'    p.add_argument("--version", action="version", version="{name} " + __version__)',
                            '    sub = p.add_subparsers(dest="cmd", required=True)',
                            '    sub.add_parser("hello").add_argument("who")',
                            "    args = p.parse_args(argv)",
                            '    print(f"hello, {args.who}")',
                            "    return 0",
                        ],
                        "tests/test_cli.py": [
                            "import contextlib, io, unittest",
                            f"from {name}.cli import main",
                            "",
                            "def run(*argv):",
                            "    out = io.StringIO()",
                            "    with contextlib.redirect_stdout(out):",
                            "        code = main(list(argv))",
                            "    return code, out.getvalue()",
                            "",
                            "class CliTests(unittest.TestCase):",
                            "    def test_hello(self):",
                            '        self.assertEqual(run("hello", "Ana"), (0, "hello, Ana\\\\n"))',
                            "",
                            "    def test_version(self):",
                            "        out = io.StringIO()",
                            "        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):",
                            '            main(["--version"])',
                            f'        self.assertEqual(out.getvalue().strip(), "{name} {version}")',
                        ],
                        ".gitignore": [".venv/", "__pycache__/", "dist/", "*.egg-info/"],
                    }
                    for rel, lines in files.items():
                        path = root / rel
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("\\n".join(lines) + "\\n")
                    return root
            ''', "All the knowledge is data: one dict says what goes where, and a four-line loop writes it. "
                 "This is what `uv init`, cookiecutter and `cargo new` do, with more templates."),
            "string.Template files": ('''
                from pathlib import Path
                from string import Template
                import textwrap

                TEMPLATES = {
                    "pyproject.toml": """
                        [build-system]
                        requires = ["setuptools>=77"]
                        build-backend = "setuptools.build_meta"

                        [project]
                        name = "$name"
                        version = "$version"
                        requires-python = ">=3.12"

                        [project.scripts]
                        $name = "$name.cli:main"
                    """,
                    "src/$name/__init__.py": """
                        __version__ = "$version"
                    """,
                    "src/$name/__main__.py": """
                        import sys
                        from .cli import main

                        sys.exit(main())
                    """,
                    "src/$name/cli.py": """
                        import argparse
                        from $name import __version__

                        def main(argv=None):
                            p = argparse.ArgumentParser(prog="$name")
                            p.add_argument("--version", action="version", version="$name " + __version__)
                            sub = p.add_subparsers(dest="cmd", required=True)
                            sub.add_parser("hello").add_argument("who")
                            args = p.parse_args(argv)
                            print("hello, " + args.who)
                            return 0
                    """,
                    "tests/test_cli.py": """
                        import contextlib, io, unittest
                        from $name.cli import main

                        class CliTests(unittest.TestCase):
                            def test_hello(self):
                                out = io.StringIO()
                                with contextlib.redirect_stdout(out):
                                    self.assertEqual(main(["hello", "Ana"]), 0)
                                self.assertEqual(out.getvalue(), "hello, Ana\\\\n")

                            def test_version(self):
                                out = io.StringIO()
                                with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as cm:
                                    main(["--version"])
                                self.assertEqual(cm.exception.code, 0)
                                self.assertIn("$version", out.getvalue())
                    """,
                    ".gitignore": """
                        .venv/
                        __pycache__/
                        dist/
                    """,
                }

                def scaffold(root, name, version="0.1.0"):
                    if not name.isidentifier():
                        raise ValueError(f"bad package name: {name!r}")
                    values = {"name": name, "version": version}
                    for rel, body in TEMPLATES.items():
                        path = Path(root) / Template(rel).substitute(values)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(Template(textwrap.dedent(body).lstrip()).substitute(values))
                    return Path(root)
            ''', "string.Template uses $name, so the templates read like the real files, with no clash with the "
                 "{} braces of f-strings inside the generated code. Even the paths are templates."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n    def helper(self): pass\n    def test_b(self): pass\nprint(unittest.defaultTestLoader.getTestCaseNames(T))", why="Only methods starting with 'test' are tests, run in alphabetical order."),
    dict(kind="predict", code="from unittest.mock import Mock\nm = Mock()\nm.send('a', 1)\nm.send('b', 2)\nprint(m.send.call_count, m.send.call_args)"),
    dict(kind="predict", code="from unittest.mock import Mock\nm = Mock(return_value=42)\nprint(m(), m.anything.you.like.__class__.__name__)", why="A Mock invents attributes on demand; each is another Mock."),
    dict(kind="predict", code="from unittest.mock import Mock\nm = Mock(side_effect=[1, 2, ValueError('done')])\nprint(m(), m())\ntry:\n    m()\nexcept ValueError as e:\n    print('raised', e)"),
    dict(kind="predict", code="def f(n: int) -> int:\n    return n * 2\nprint(f('ab'))", why="Python doesn't enforce hints; only a static checker would complain."),
    dict(kind="predict", code="import typing\nprint(typing.get_origin(list[int]), typing.get_args(dict[str, float]))"),
    dict(kind="predict", code="import tomllib\nprint(tomllib.loads('[project]\\nname = \"loans\"\\nversion = \"1.0\"'))"),
    dict(kind="recall", q="Which unittest method runs before every test method?", a=["setUp", "setUp()"]),
    dict(kind="recall", q="Which module finds where a program spends its time, function by function?", a=["cProfile", "profile", "cProfile and pstats"]),
    dict(kind="recall", q="Which file declares a Python project's name, version, dependencies and commands?", a=["pyproject.toml", "pyproject"]),
]
