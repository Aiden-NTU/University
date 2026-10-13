EXERCISES = [
    dict(
        id="6.1", kind="fix", title="The except that hides everything",
        task="""
        `parse_ages(lines)` takes lines like `"ana,20"` and returns `(ages, bad)`: a dict of
        name → age for good lines, and a list of the **1-based line numbers** that couldn't be parsed
        (wrong number of fields, or an age that isn't an integer).

        The bare `except:` makes it "work", but it also hides real bugs: passing something that
        isn't a list of strings (e.g. `[None]` or `[42]`) is silently treated as a bad line. Make it
        catch only the errors that mean "bad line", so programming errors raise.
        """,
        stub='''
        def parse_ages(lines):
            ages, bad = {}, []
            for i, line in enumerate(lines, 1):
                try:
                    name, age = line.split(",")
                    ages[name.strip()] = int(age)
                except:
                    bad.append(i)
            return ages, bad
        ''',
        tests='''
        def test_parsing(m):
            ages, bad = m.parse_ages(["ana,20", "ben,x", "cy", "di, 31 ", "a,b,c"])
            equal(ages, {"ana": 20, "di": 31}, "good lines")
            equal(bad, [2, 3, 5], "bad line numbers")

        def test_bugs_raise(m):
            raises(AttributeError, m.parse_ages, [None])
            raises(AttributeError, m.parse_ages, [42])
        ''',
        alts={
            "except ValueError": ('''
                def parse_ages(lines):
                    ages, bad = {}, []
                    for i, line in enumerate(lines, 1):
                        try:
                            name, age = line.split(",")
                            ages[name.strip()] = int(age)
                        except ValueError:
                            bad.append(i)
                    return ages, bad
            ''', "Both 'wrong number of fields' (unpacking) and int('x') raise ValueError, so one specific "
                 "clause covers exactly the expected failures."),
            "check, don't catch": ('''
                def parse_ages(lines):
                    ages, bad = {}, []
                    for i, line in enumerate(lines, 1):
                        parts = line.split(",")
                        age = parts[-1].strip()
                        if len(parts) != 2 or not age.lstrip("-").isdigit():
                            bad.append(i)
                            continue
                        ages[parts[0].strip()] = int(age)
                    return ages, bad
            ''', "LBYL works here, but the validity test now duplicates int()'s rules (and gets them slightly "
                 "wrong: '+5' and '٣' are valid for int). EAFP lets int() be the judge."),
        },
    ),
    dict(
        id="6.2", kind="build", title="All or nothing: a transaction context manager",
        task="""
        Write a context manager **class** `Transaction(store)` for a dict `store`:

        - inside `with Transaction(store) as s:` the code edits `s` (which is `store` itself)
        - if the block finishes normally, the changes stay
        - if the block raises, `store` is restored **exactly** to how it was before the block
          (including nested lists inside it), and the exception still propagates
        """,
        stub='''
        class Transaction:
            def __init__(self, store):
                self.store = store
        ''',
        tests='''
        def test_commit(m):
            store = {"ana": ["Dune"]}
            with m.Transaction(store) as s:
                check(s is store, "as-target is the store itself")
                s["ben"] = []
                s["ana"].append("Emma")
            equal(store, {"ana": ["Dune", "Emma"], "ben": []}, "changes kept")

        def test_rollback(m):
            store = {"ana": ["Dune"], "cy": []}
            try:
                with m.Transaction(store) as s:
                    s["ana"].append("Emma")
                    del s["cy"]
                    s["new"] = 1
                    raise RuntimeError("boom")
            except RuntimeError:
                pass
            else:
                raise AssertionError("the exception must propagate")
            equal(store, {"ana": ["Dune"], "cy": []}, "store restored, nested list too")
        ''',
        alts={
            "deepcopy snapshot": ('''
                import copy

                class Transaction:
                    def __init__(self, store):
                        self.store = store

                    def __enter__(self):
                        self._snapshot = copy.deepcopy(self.store)
                        return self.store

                    def __exit__(self, exc_type, exc, tb):
                        if exc_type is not None:
                            self.store.clear()
                            self.store.update(self._snapshot)
                        return False
            ''', "Restore *in place* (clear + update): other code holding a reference to the same dict "
                 "sees the rollback. Rebinding self.store would only change our own name (Ch 3)."),
            "contextmanager function": ('''
                import contextlib, copy

                @contextlib.contextmanager
                def Transaction(store):
                    snapshot = copy.deepcopy(store)
                    try:
                        yield store
                    except BaseException:
                        store.clear()
                        store.update(snapshot)
                        raise
            ''', "Same behaviour in a generator. A bare raise re-raises the active exception unchanged."),
        },
    ),
    dict(
        id="6.3", kind="build", title="Temporarily change environment variables",
        task="""
        Write a `@contextlib.contextmanager` function `temp_env(**changes)`:

        - on entry, sets each `os.environ[name] = value`; a value of `None` means **remove** the variable
        - on exit, puts everything back exactly: restores old values, and removes variables that
          didn't exist before, **even if the block raised**
        """,
        stub='''
        import contextlib, os

        @contextlib.contextmanager
        def temp_env(**changes):
            yield
        ''',
        tests='''
        import os

        def test_set_and_restore(m):
            os.environ["PRACTICE_A"] = "old"
            os.environ.pop("PRACTICE_B", None)
            os.environ["PRACTICE_C"] = "keep?"
            with m.temp_env(PRACTICE_A="new", PRACTICE_B="b", PRACTICE_C=None):
                equal(os.environ["PRACTICE_A"], "new", "changed")
                equal(os.environ["PRACTICE_B"], "b", "added")
                check("PRACTICE_C" not in os.environ, "None removes")
            equal(os.environ["PRACTICE_A"], "old", "restored")
            check("PRACTICE_B" not in os.environ, "added variable removed again")
            equal(os.environ["PRACTICE_C"], "keep?", "removed variable restored")

        def test_restore_on_error(m):
            os.environ["PRACTICE_A"] = "old"
            try:
                with m.temp_env(PRACTICE_A="new"):
                    raise KeyError("x")
            except KeyError:
                pass
            equal(os.environ["PRACTICE_A"], "old", "restored after an error")
        ''',
        alts={
            "try/finally": ('''
                import contextlib, os

                @contextlib.contextmanager
                def temp_env(**changes):
                    old = {k: os.environ.get(k) for k in changes}
                    try:
                        for k, v in changes.items():
                            if v is None:
                                os.environ.pop(k, None)
                            else:
                                os.environ[k] = v
                        yield
                    finally:
                        for k, v in old.items():
                            if v is None:
                                os.environ.pop(k, None)
                            else:
                                os.environ[k] = v
            ''', "Saving the old values *before* changing anything, and putting the changes inside the try, "
                 "means even a half-applied change is undone. unittest.mock.patch.dict(os.environ) does this "
                 "for tests."),
        },
    ),
    dict(
        id="6.4", kind="build", title="Exceptions that mean something",
        task="""
        Write an exception hierarchy and a function that uses it:

        - `LoanError(Exception)`: the base class
        - `LimitReached(LoanError)`: has attributes `member` and `limit`; `str(e)` mentions both
        - `NotAvailable(LoanError, LookupError)`: the title isn't on the shelf (so `except LookupError` catches it too)
        - `lend(member, title, loans, shelf, limit=3)`: `loans` maps member → list of titles, `shelf` is a set
          of titles. Raise `NotAvailable` if `title not in shelf`, `LimitReached` if the member already has
          `limit` loans; otherwise move the title from the shelf to the member's loans.

        Check availability first: if both problems apply, `NotAvailable` wins.
        """,
        stub='''
        class LoanError(Exception):
            pass
        ''',
        tests='''
        def test_hierarchy(m):
            check(issubclass(m.LimitReached, m.LoanError) and issubclass(m.NotAvailable, m.LoanError), "subclasses")
            check(issubclass(m.NotAvailable, LookupError), "NotAvailable is a LookupError")

        def test_lend(m):
            loans, shelf = {}, {"Dune", "Emma", "Ubik", "Kim"}
            for t in ["Dune", "Emma", "Ubik"]:
                m.lend("ana", t, loans, shelf)
            equal(loans, {"ana": ["Dune", "Emma", "Ubik"]}, "loans recorded")
            equal(shelf, {"Kim"}, "shelf updated")
            try:
                m.lend("ana", "Kim", loans, shelf)
            except m.LimitReached as e:
                equal((e.member, e.limit), ("ana", 3), "attributes")
                check("ana" in str(e) and "3" in str(e), "message mentions member and limit")
            else:
                raise AssertionError("LimitReached expected")
            raises(m.NotAvailable, m.lend, "ana", "Dune", loans, shelf)
            raises(LookupError, m.lend, "ben", "Nope", loans, shelf)
            equal(shelf, {"Kim"}, "failed loans change nothing")
        ''',
        alts={
            "classes + guard clauses": ('''
                class LoanError(Exception):
                    """Anything that stops a loan."""

                class LimitReached(LoanError):
                    def __init__(self, member, limit):
                        super().__init__(f"{member} already has {limit} loans")
                        self.member = member
                        self.limit = limit

                class NotAvailable(LoanError, LookupError):
                    pass

                def lend(member, title, loans, shelf, limit=3):
                    if title not in shelf:
                        raise NotAvailable(title)
                    mine = loans.setdefault(member, [])
                    if len(mine) >= limit:
                        raise LimitReached(member, limit)
                    shelf.remove(title)
                    mine.append(title)
            ''', "Guard clauses: check and raise first, then do the work, so a failed call changes nothing. "
                 "(setdefault does create an empty list for a new member; harmless here.)"),
        },
    ),
    dict(
        id="6.5", kind="build", title="Retry, and keep the real cause",
        task="""
        Write `retry_call(func, attempts, exceptions=(Exception,))`:

        - calls `func()` up to `attempts` times, returning the first successful result
        - only exceptions that are instances of `exceptions` are retried; others propagate at once
        - if every attempt fails, raise `RetryError` (define it) **chained** from the last exception
          (`raise ... from last`), with an attribute `attempts`
        """,
        stub='''
        def retry_call(func, attempts, exceptions=(Exception,)):
            return func()
        ''',
        tests='''
        def flaky(fail_times, exc=ConnectionError):
            calls = []
            def f():
                calls.append(1)
                if len(calls) <= fail_times:
                    raise exc(f"fail {len(calls)}")
                return len(calls)
            return f, calls

        def test_success_after_failures(m):
            f, calls = flaky(2)
            equal(m.retry_call(f, 3), 3, "third call succeeds")

        def test_gives_up_with_cause(m):
            f, calls = flaky(5)
            try:
                m.retry_call(f, 3, (ConnectionError,))
            except m.RetryError as e:
                equal(e.attempts, 3, "attempts attribute")
                check(isinstance(e.__cause__, ConnectionError) and "fail 3" in str(e.__cause__), "chained from the last error")
            else:
                raise AssertionError("RetryError expected")
            equal(len(calls), 3, "exactly 3 calls")

        def test_other_errors_not_retried(m):
            f, calls = flaky(5, exc=KeyError)
            raises(KeyError, m.retry_call, f, 3, (ConnectionError,))
            equal(len(calls), 1, "a non-matching error stops at once")
        ''',
        alts={
            "loop with for-else": ('''
                class RetryError(Exception):
                    def __init__(self, attempts):
                        super().__init__(f"gave up after {attempts} attempts")
                        self.attempts = attempts

                def retry_call(func, attempts, exceptions=(Exception,)):
                    last = None
                    for _ in range(attempts):
                        try:
                            return func()
                        except exceptions as exc:
                            last = exc
                    raise RetryError(attempts) from last
            ''', "`except exceptions` accepts a tuple of classes. Note `last = exc`: the name `exc` itself "
                 "is deleted at the end of the except block, so you must copy it out."),
        },
    ),
    dict(
        id="6.6", kind="project", title="Mini-project: report every bad row at once",
        task="""
        Write `import_members(rows)`, where each row is a dict that should have `name`, `age`, `email`:

        - a valid row has a non-empty `name` (after stripping), an `age` that `int()` accepts with
          0 < age < 130, and an `email` containing exactly one `@`
        - return a list of cleaned dicts `{"name": str, "age": int, "email": lowercased str}`
          if **all** rows are valid
        - otherwise raise `ExceptionGroup("invalid rows", errors)` holding **one exception per problem**:
          `KeyError` for a missing field, `ValueError` for a bad value. Every exception must carry a note
          (`add_note`) of the form `"row N"` (1-based)
        """,
        stub='''
        def import_members(rows):
            return [dict(r) for r in rows]
        ''',
        tests='''
        GOOD = [{"name": " Ana ", "age": "20", "email": "Ana@Uni.ac.uk"}, {"name": "Ben", "age": 31, "email": "b@x.io"}]

        def test_all_good(m):
            equal(m.import_members(GOOD), [{"name": "Ana", "age": 20, "email": "ana@uni.ac.uk"},
                                           {"name": "Ben", "age": 31, "email": "b@x.io"}], "cleaned rows")

        def test_errors_grouped(m):
            rows = GOOD + [{"name": "", "age": "x", "email": "nope"}, {"name": "Cy", "email": "c@d.e"}]
            try:
                m.import_members(rows)
            except ExceptionGroup as eg:
                kinds = sorted(type(e).__name__ for e in eg.exceptions)
                equal(kinds, ["KeyError", "ValueError", "ValueError", "ValueError"], "one exception per problem")
                notes = sorted(n for e in eg.exceptions for n in getattr(e, "__notes__", []))
                equal(notes, ["row 3", "row 3", "row 3", "row 4"], "row notes")
            else:
                raise AssertionError("ExceptionGroup expected")

        def test_except_star(m):
            caught = []
            try:
                m.import_members([{"name": "A", "age": 200, "email": "a@b@c"}])
            except* ValueError as g:
                caught.append(len(g.exceptions))
            equal(caught, [2], "two ValueErrors caught with except*")
        ''',
        alts={
            "collect per field": ('''
                def _check(row):
                    for field in ("name", "age", "email"):
                        if field not in row:
                            yield KeyError(field)
                    if "name" in row and not str(row["name"]).strip():
                        yield ValueError("empty name")
                    if "age" in row:
                        try:
                            if not 0 < int(row["age"]) < 130:
                                yield ValueError(f"age out of range: {row['age']}")
                        except ValueError:
                            yield ValueError(f"age is not a number: {row['age']!r}")
                    if "email" in row and str(row["email"]).count("@") != 1:
                        yield ValueError(f"bad email: {row['email']!r}")

                def import_members(rows):
                    errors, out = [], []
                    for n, row in enumerate(rows, 1):
                        problems = list(_check(row))
                        for e in problems:
                            e.add_note(f"row {n}")
                        errors += problems
                        if not problems:
                            out.append({"name": row["name"].strip(), "age": int(row["age"]),
                                        "email": row["email"].lower()})
                    if errors:
                        raise ExceptionGroup("invalid rows", errors)
                    return out
            ''', "A generator of problems keeps each rule independent: adding a rule is one more `if`. "
                 "Exceptions are just objects here; they're only raised once, as a group."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="def f():\n    try:\n        return 'try'\n    finally:\n        print('finally', end=' ')\nprint(f())"),
    dict(kind="predict", code="try:\n    {}['k']\nexcept LookupError as e:\n    print(type(e).__name__)"),
    dict(kind="predict", code="try:\n    int('x')\nexcept ValueError:\n    print('A', end=' ')\nelse:\n    print('B', end=' ')\nfinally:\n    print('C')"),
    dict(kind="predict", code="try:\n    try:\n        1 / 0\n    except ZeroDivisionError as e:\n        raise ValueError('bad') from e\nexcept ValueError as v:\n    print(type(v.__cause__).__name__)"),
    dict(kind="predict", code="import contextlib\nwith contextlib.suppress(KeyError):\n    {}['x']\n    print('inside')\nprint('after')", why="The rest of the with-block is skipped once the error is raised; suppress only stops it propagating."),
    dict(kind="recall", q="Which two methods does a class need to work in a with statement?", a=["__enter__ and __exit__", "__enter__, __exit__", "enter and exit"]),
    dict(kind="recall", q="What syntax catches exceptions inside an ExceptionGroup?", a=["except*", "except star"]),
    dict(kind="recall", q="Which exception class should custom app exceptions usually inherit from?", a=["Exception"]),
]
