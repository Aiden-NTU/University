import textwrap

SCHEMA_TASK = """
- `members(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE)`
- `books(id INTEGER PRIMARY KEY, title TEXT NOT NULL, copies INTEGER NOT NULL DEFAULT 1, CHECK (copies >= 0))`
- `loans(id INTEGER PRIMARY KEY, member_id INTEGER NOT NULL REFERENCES members(id),
  book_id INTEGER NOT NULL REFERENCES books(id), due TEXT NOT NULL)`
"""
SCHEMA_TASK = textwrap.indent(SCHEMA_TASK, " " * 8)

SCHEMA_SRC = '''
SCHEMA = """
CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                                    email TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                                  copies INTEGER NOT NULL DEFAULT 1 CHECK (copies >= 0));
CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY,
                                  member_id INTEGER NOT NULL REFERENCES members(id),
                                  book_id INTEGER NOT NULL REFERENCES books(id),
                                  due TEXT NOT NULL);
"""
'''

# shared by the tests below: build a database in the reference shape
MAKE_DB = '''
import sqlite3, random
SCHEMA = """
CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE);
CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                    copies INTEGER NOT NULL DEFAULT 1 CHECK (copies >= 0));
CREATE TABLE loans (id INTEGER PRIMARY KEY, member_id INTEGER NOT NULL REFERENCES members(id),
                    book_id INTEGER NOT NULL REFERENCES books(id), due TEXT NOT NULL);
"""
def make_db(seed=0, members=12, books=8, loans=40):
    rng = random.Random(seed)
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    names = rng.sample(["Ana", "Ben", "Cat", "Dev", "Eli", "Fay", "Gus", "Hal", "Ivy", "Jo", "Kai",
                        "Lou", "Mo", "Ned", "O'Neil", "Pip"], members)
    conn.executemany("INSERT INTO members (name, email) VALUES (?, ?)",
                     [(n, f"{n.lower()}@x.org") for n in names])
    conn.executemany("INSERT INTO books (title, copies) VALUES (?, ?)",
                     [(f"Book {i}", rng.randint(0, 3)) for i in range(books)])
    conn.executemany("INSERT INTO loans (member_id, book_id, due) VALUES (?, ?, ?)",
                     [(rng.randint(1, members), rng.randint(1, books),
                       f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}") for _ in range(loans)])
    conn.commit()
    return conn
'''
MAKE_DB = textwrap.indent(MAKE_DB, " " * 8)   # same indent as the tests it's glued onto

EXERCISES = [
    dict(
        id="12.1", kind="build", title="A schema that refuses bad data",
        task=f"""
        Write `create_schema(conn)` that turns on foreign keys for `conn` and creates these three
        tables (exact names and columns; types and constraints as shown):
        {SCHEMA_TASK}
        Calling it twice on the same connection must not fail (`IF NOT EXISTS`).

        The tests then try to insert bad rows and expect `sqlite3.IntegrityError` every time:
        the database itself should refuse them, not your Python code.
        """,
        stub='''
        import sqlite3

        def create_schema(conn):
            ...
        ''',
        tests='''
        import sqlite3

        def fresh(m):
            conn = sqlite3.connect(":memory:")
            m.create_schema(conn)
            return conn

        def test_good_rows_go_in(m):
            c = fresh(m)
            c.execute("INSERT INTO members (name, email) VALUES ('Ana', 'ana@x.org')")
            c.execute("INSERT INTO books (title) VALUES ('Dune')")
            c.execute("INSERT INTO loans (member_id, book_id, due) VALUES (1, 1, '2026-10-01')")
            equal(c.execute("SELECT copies FROM books").fetchone(), (1,), "default copies")

        def test_twice_is_fine(m):
            c = fresh(m)
            m.create_schema(c)

        def test_refuses_bad_rows(m):
            c = fresh(m)
            c.execute("INSERT INTO members (name, email) VALUES ('Ana', 'ana@x.org')")
            c.execute("INSERT INTO books (title, copies) VALUES ('Dune', 2)")
            for bad in ["INSERT INTO members (name, email) VALUES ('Ann', 'ana@x.org')",
                        "INSERT INTO members (name, email) VALUES (NULL, 'x@x.org')",
                        "INSERT INTO members (name) VALUES ('NoEmail')",
                        "INSERT INTO books (title, copies) VALUES ('Neg', -1)",
                        "INSERT INTO books (copies) VALUES (1)",
                        "INSERT INTO loans (member_id, book_id, due) VALUES (99, 1, '2026-01-01')",
                        "INSERT INTO loans (member_id, book_id, due) VALUES (1, 99, '2026-01-01')",
                        "INSERT INTO loans (member_id, book_id) VALUES (1, 1)",
                        "UPDATE books SET copies = copies - 5"]:
                raises(sqlite3.IntegrityError, c.execute, bad)

        def test_foreign_keys_on(m):
            c = fresh(m)
            equal(c.execute("PRAGMA foreign_keys").fetchone(), (1,), "PRAGMA foreign_keys")
        ''',
        alts={
            "executescript": ("import sqlite3\n" + SCHEMA_SRC + '''
def create_schema(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
''', "The PRAGMA must come first: executescript() commits any open transaction, but a PRAGMA "
     "foreign_keys inside a transaction is silently ignored."),
            "one execute per table": ('''
                import sqlite3

                TABLES = [
                    "CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
                    "email TEXT NOT NULL UNIQUE)",
                    "CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
                    "copies INTEGER NOT NULL DEFAULT 1, CHECK (copies >= 0))",
                    "CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY, "
                    "member_id INTEGER NOT NULL REFERENCES members(id), "
                    "book_id INTEGER NOT NULL REFERENCES books(id), due TEXT NOT NULL)",
                ]

                def create_schema(conn):
                    conn.execute("PRAGMA foreign_keys = ON")
                    for stmt in TABLES:
                        conn.execute(stmt)
                    conn.commit()
            ''', "A list of statements is easy to extend into a migration list later (version 1, 2, 3...). "
                 "A table-level CHECK works the same as a column-level one."),
        },
    ),
    dict(
        id="12.2", kind="fix", title="Close the injection hole",
        task="""
        `find_member(conn, name)` returns the matching members as a list of `(id, name, email)` tuples.
        It works for "Ana", but crashes for "O'Neil", and an attacker can make it return every member.

        Fix it without changing what it returns. (The tests use names with quotes, percent signs and
        the classic `' OR '1'='1`.)
        """,
        stub='''
        def find_member(conn, name):
            q = f"SELECT id, name, email FROM members WHERE name = '{name}' ORDER BY id"
            return conn.execute(q).fetchall()
        ''',
        tests=MAKE_DB + '''
        def test_plain_names(m):
            c = make_db()
            for (mid, name, email) in c.execute("SELECT id, name, email FROM members"):
                equal(m.find_member(c, name), [(mid, name, email)], f"find_member({name!r})")

        def test_quotes_in_names(m):
            c = make_db()
            c.execute("INSERT INTO members (name, email) VALUES (?, ?)", ("D'Arcy", "d@x.org"))
            got = m.find_member(c, "D'Arcy")
            equal([r[1] for r in got], ["D'Arcy"], "a name with an apostrophe")

        def test_attacks_find_nothing(m):
            c = make_db()
            for evil in ["x' OR '1'='1", "' OR 1=1 --", "%", "Ana' --", "'; DROP TABLE members; --"]:
                equal(m.find_member(c, evil), [], f"find_member({evil!r})")
            equal(c.execute("SELECT COUNT(*) FROM members").fetchone()[0] > 0, True, "members table still there")
        ''',
        alts={
            "qmark placeholder": ('''
                def find_member(conn, name):
                    q = "SELECT id, name, email FROM members WHERE name = ? ORDER BY id"
                    return conn.execute(q, (name,)).fetchall()
            ''', "The value travels separately from the SQL text; quotes in it are just characters."),
            "named placeholder": ('''
                def find_member(conn, name):
                    return conn.execute(
                        "SELECT id, name, email FROM members WHERE name = :name ORDER BY id",
                        {"name": name}).fetchall()
            ''', "Named style reads better once there are three or more parameters."),
        },
    ),
    dict(
        id="12.3", kind="build", title="Top borrowers (JOIN + GROUP BY)",
        task="""
        Write `top_borrowers(conn, n)` returning the `n` members with the most loans, as a list of
        `(name, number_of_loans)` tuples: most loans first, ties in alphabetical order of name.
        Members with **no** loans count as 0 and can appear if `n` is large enough.

        Tables are as in 12.1. Try it in pure SQL (`LEFT JOIN`, `COUNT`, `GROUP BY`, `ORDER BY`,
        `LIMIT`); then compare with the alternatives.
        """,
        stub='''
        def top_borrowers(conn, n):
            ...
        ''',
        tests=MAKE_DB + '''
        def expected(c, n):
            counts = {name: 0 for (name,) in c.execute("SELECT name FROM members")}
            names = dict(c.execute("SELECT id, name FROM members"))
            for (mid,) in c.execute("SELECT member_id FROM loans"):
                counts[names[mid]] += 1
            return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

        def test_random_libraries(m):
            for seed in range(25):
                c = make_db(seed, loans=seed * 3)
                for n in (1, 3, 12, 20):
                    equal([tuple(r) for r in m.top_borrowers(c, n)], expected(c, n), f"seed {seed}, n={n}")
        ''',
        alts={
            "all in SQL": ('''
                def top_borrowers(conn, n):
                    return conn.execute("""
                        SELECT m.name, COUNT(l.id) AS n_loans
                        FROM members AS m
                        LEFT JOIN loans AS l ON l.member_id = m.id
                        GROUP BY m.id
                        ORDER BY n_loans DESC, m.name
                        LIMIT ?""", (n,)).fetchall()
            ''', "One query, one round trip, and the database only sends n rows back."),
            "Counter in Python": ('''
                from collections import Counter

                def top_borrowers(conn, n):
                    names = dict(conn.execute("SELECT id, name FROM members"))
                    counts = Counter({name: 0 for name in names.values()})
                    for (mid,) in conn.execute("SELECT member_id FROM loans"):
                        counts[names[mid]] += 1
                    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
            ''', "Fine for small data and easy to step through, but it moves every loan row into Python."),
        },
    ),
    dict(
        id="12.4", kind="build", title="Lend and return, atomically",
        task="""
        Write two functions (tables as in 12.1, foreign keys on):

        - `lend(conn, member_id, book_id, due)`: records a loan and takes one copy off the shelf,
          returning the new loan's id. Raise `LookupError` if the member or book doesn't exist, and
          `ValueError` if the book has no copies left.
        - `give_back(conn, loan_id)`: deletes the loan and puts the copy back. `LookupError` if there's
          no such loan.

        **After any failure the database must be exactly as it was** (use a transaction), and after
        success the change must be committed (a second connection must see it).
        """,
        stub='''
        def lend(conn, member_id, book_id, due):
            ...

        def give_back(conn, loan_id):
            ...
        ''',
        tests=MAKE_DB + '''
        import os

        def snapshot(c):
            return (c.execute("SELECT * FROM loans ORDER BY id").fetchall(),
                    c.execute("SELECT * FROM books ORDER BY id").fetchall())

        def test_random_sequence_against_a_model(m):
            rng = random.Random(5)
            c = make_db(1, loans=0)
            copies = dict(c.execute("SELECT id, copies FROM books"))
            out = {}
            for step in range(300):
                if out and rng.random() < 0.4:
                    lid = rng.choice(list(out))
                    m.give_back(c, lid)
                    copies[out.pop(lid)] += 1
                else:
                    mid, bid = rng.randint(1, 12), rng.randint(1, 8)
                    before = snapshot(c)
                    if copies[bid] == 0:
                        raises(ValueError, m.lend, c, mid, bid, "2026-10-01")
                        equal(snapshot(c), before, "database unchanged after a refused loan")
                    else:
                        lid = m.lend(c, mid, bid, "2026-10-01")
                        out[lid] = bid
                        copies[bid] -= 1
                equal(dict(c.execute("SELECT id, copies FROM books")), copies, f"copies after step {step}")
                equal(c.execute("SELECT COUNT(*) FROM loans").fetchone()[0], len(out), "number of loans")

        def test_missing_things(m):
            c = make_db(2, loans=0)
            c.execute("UPDATE books SET copies = 1")
            c.commit()
            before = snapshot(c)
            raises(LookupError, m.lend, c, 999, 1, "2026-10-01")
            raises(LookupError, m.lend, c, 1, 999, "2026-10-01")
            raises(LookupError, m.give_back, c, 12345)
            equal(snapshot(c), before, "database unchanged")

        def test_committed(m):
            c = sqlite3.connect("lib.db")
            c.executescript(SCHEMA)
            c.execute("INSERT INTO members (name, email) VALUES ('A', 'a@x')")
            c.execute("INSERT INTO books (title, copies) VALUES ('B', 1)")
            c.commit()
            m.lend(c, 1, 1, "2026-10-01")
            other = sqlite3.connect("lib.db")
            equal(other.execute("SELECT copies FROM books").fetchone(), (0,), "seen by a second connection")
            other.close(); c.close()
        ''',
        alts={
            "with conn": ('''
                def lend(conn, member_id, book_id, due):
                    with conn:
                        if not conn.execute("SELECT 1 FROM members WHERE id = ?", (member_id,)).fetchone():
                            raise LookupError(f"no member {member_id}")
                        row = conn.execute("SELECT copies FROM books WHERE id = ?", (book_id,)).fetchone()
                        if row is None:
                            raise LookupError(f"no book {book_id}")
                        if row[0] == 0:
                            raise ValueError("no copies left")
                        conn.execute("UPDATE books SET copies = copies - 1 WHERE id = ?", (book_id,))
                        return conn.execute("INSERT INTO loans (member_id, book_id, due) VALUES (?, ?, ?)",
                                            (member_id, book_id, due)).lastrowid

                def give_back(conn, loan_id):
                    with conn:
                        row = conn.execute("SELECT book_id FROM loans WHERE id = ?", (loan_id,)).fetchone()
                        if row is None:
                            raise LookupError(f"no loan {loan_id}")
                        conn.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
                        conn.execute("UPDATE books SET copies = copies + 1 WHERE id = ?", row)
            ''', "Check first, then change: the with block commits on success and rolls back if anything "
                 "raises, including our own LookupError/ValueError."),
            "let the constraints decide": ('''
                import sqlite3

                def lend(conn, member_id, book_id, due):
                    try:
                        with conn:
                            cur = conn.execute("UPDATE books SET copies = copies - 1 WHERE id = ?", (book_id,))
                            if cur.rowcount == 0:
                                raise LookupError(f"no book {book_id}")
                            return conn.execute(
                                "INSERT INTO loans (member_id, book_id, due) VALUES (?, ?, ?)",
                                (member_id, book_id, due)).lastrowid
                    except sqlite3.IntegrityError as e:
                        if "CHECK" in str(e):
                            raise ValueError("no copies left") from e
                        raise LookupError(f"no member {member_id}") from e

                def give_back(conn, loan_id):
                    with conn:
                        cur = conn.execute("UPDATE books SET copies = copies + 1 WHERE id = "
                                           "(SELECT book_id FROM loans WHERE id = ?)", (loan_id,))
                        if cur.rowcount == 0:
                            raise LookupError(f"no loan {loan_id}")
                        conn.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
            ''', "No check-then-act gap: the CHECK and FOREIGN KEY constraints refuse bad changes, even if "
                 "another program changes the data between our statements. Translating error messages "
                 "by text is the fragile part."),
        },
    ),
    dict(
        id="12.5", kind="time", title="Make the slow queries use an index",
        task="""
        A library app runs these two queries constantly:

            SELECT * FROM loans WHERE member_id = ?
            SELECT id FROM loans WHERE due < ? ORDER BY due

        Write `add_indexes(conn)` that creates whatever indexes make `EXPLAIN QUERY PLAN` show
        `SEARCH ... USING INDEX` (or `COVERING INDEX`) for both instead of `SCAN loans`.

        Then measure: time each query 1000 times on a 100,000-loan table before and after
        (`time.perf_counter`), and write the numbers in a comment in your solution.
        """,
        stub='''
        def add_indexes(conn):
            pass
        ''',
        tests=MAKE_DB + '''
        def plan(c, q, arg):
            return " | ".join(r[-1] for r in c.execute("EXPLAIN QUERY PLAN " + q, (arg,)))

        def test_both_queries_search(m):
            c = make_db(3, loans=2000)
            m.add_indexes(c)
            p1 = plan(c, "SELECT * FROM loans WHERE member_id = ?", 3)
            p2 = plan(c, "SELECT id FROM loans WHERE due < ? ORDER BY due", "2026-06-01")
            check("USING" in p1 and "INDEX" in p1, f"member_id query still scans: {p1}")
            check("USING" in p2 and "INDEX" in p2, f"due query still scans: {p2}")
            check("TEMP B-TREE" not in p2, f"the ORDER BY still needs a separate sort: {p2}")

        def test_answers_unchanged(m):
            c = make_db(4, loans=500)
            q = "SELECT id FROM loans WHERE due < ? ORDER BY due, id"
            before = c.execute(q, ("2026-06-01",)).fetchall()
            m.add_indexes(c)
            equal(c.execute(q, ("2026-06-01",)).fetchall(), before, "same rows after indexing")
        ''',
        alts={
            "two indexes": ('''
                def add_indexes(conn):
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_loans_due ON loans(due)")
                    conn.commit()
            ''', "An index on due serves both the WHERE (a range) and the ORDER BY (already sorted). "
                 "Each index costs disk space and a little time on every INSERT."),
        },
    ),
    dict(
        id="12.6", kind="project", title="Mini-project: a library loans module",
        task=f"""
        Build a small, reusable data layer. Write a class `Library`:

        - `Library(path)` opens (or creates) the database at `path` with the 12.1 schema and foreign keys on.
          `with Library(path) as lib:` works and **closes** the connection at the end.
        - `add_member(name, email) -> int` (id). Duplicate email → `ValueError` (not IntegrityError:
          callers shouldn't need to know it's SQLite).
        - `add_book(title, copies=1) -> int`
        - `lend(member_id, book_id, due) -> int` (loan id); `ValueError` if no copies left.
        - `give_back(loan_id)`
        - `overdue(today) -> list[tuple[str, str, str]]`: `(member name, book title, due)` for loans with
          `due < today` (ISO date strings compare correctly), sorted by due date, then name.
        - `close()`

        Everything must persist: open the same path again later and the data is there.
        Then use it from a 30-line command-line script of your own (`argparse`, Ch 14) for real.
        """,
        stub='''
        import sqlite3

        class Library:
            def __init__(self, path):
                ...
        ''',
        tests='''
        import sqlite3

        def test_persists(m):
            with m.Library("lib.db") as lib:
                a = lib.add_member("Ana", "ana@x.org")
                b = lib.add_book("Dune", copies=2)
                lib.lend(a, b, "2026-10-01")
            with m.Library("lib.db") as lib:
                equal(lib.overdue("2026-12-31"), [("Ana", "Dune", "2026-10-01")], "after reopening")

        def test_duplicate_email(m):
            with m.Library("lib.db") as lib:
                lib.add_member("Ana", "ana@x.org")
                raises(ValueError, lib.add_member, "Ann", "ana@x.org")

        def test_no_copies(m):
            with m.Library("lib.db") as lib:
                a = lib.add_member("Ana", "ana@x.org")
                b = lib.add_book("Rare", copies=1)
                lib.lend(a, b, "2026-10-01")
                raises(ValueError, lib.lend, a, b, "2026-10-02")
                equal(len(lib.overdue("2027-01-01")), 1, "still exactly one loan")

        def test_overdue_and_return(m):
            with m.Library("lib.db") as lib:
                ids = {n: lib.add_member(n, f"{n}@x.org") for n in ["Cat", "Ana", "Ben"]}
                bk = lib.add_book("Emma", copies=5)
                l1 = lib.lend(ids["Cat"], bk, "2026-09-01")
                lib.lend(ids["Ana"], bk, "2026-09-01")
                lib.lend(ids["Ben"], bk, "2026-08-15")
                lib.lend(ids["Ben"], bk, "2026-11-30")
                equal(lib.overdue("2026-10-01"), [("Ben", "Emma", "2026-08-15"), ("Ana", "Emma", "2026-09-01"),
                                                  ("Cat", "Emma", "2026-09-01")], "overdue on 2026-10-01")
                lib.give_back(l1)
                equal([r[0] for r in lib.overdue("2026-10-01")], ["Ben", "Ana"], "after Cat returns hers")

        def test_closed_after_with(m):
            with m.Library("lib.db") as lib:
                pass
            raises(sqlite3.ProgrammingError, lib.add_book, "Too late")
        ''',
        alts={
            "class over a connection": ("import sqlite3\n" + SCHEMA_SRC + '''

class Library:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.conn.close()

    def add_member(self, name, email):
        try:
            with self.conn:
                return self.conn.execute("INSERT INTO members (name, email) VALUES (?, ?)",
                                         (name, email)).lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"email {email!r} already registered") from e

    def add_book(self, title, copies=1):
        with self.conn:
            return self.conn.execute("INSERT INTO books (title, copies) VALUES (?, ?)",
                                     (title, copies)).lastrowid

    def lend(self, member_id, book_id, due):
        with self.conn:
            row = self.conn.execute("SELECT copies FROM books WHERE id = ?", (book_id,)).fetchone()
            if row is None:
                raise LookupError(f"no book {book_id}")
            if row[0] == 0:
                raise ValueError("no copies left")
            self.conn.execute("UPDATE books SET copies = copies - 1 WHERE id = ?", (book_id,))
            return self.conn.execute("INSERT INTO loans (member_id, book_id, due) VALUES (?, ?, ?)",
                                     (member_id, book_id, due)).lastrowid

    def give_back(self, loan_id):
        with self.conn:
            row = self.conn.execute("SELECT book_id FROM loans WHERE id = ?", (loan_id,)).fetchone()
            if row is None:
                raise LookupError(f"no loan {loan_id}")
            self.conn.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
            self.conn.execute("UPDATE books SET copies = copies + 1 WHERE id = ?", row)

    def overdue(self, today):
        return self.conn.execute("""
            SELECT m.name, b.title, l.due
            FROM loans l JOIN members m ON m.id = l.member_id JOIN books b ON b.id = l.book_id
            WHERE l.due < ?
            ORDER BY l.due, m.name""", (today,)).fetchall()
''', "__enter__/__exit__ make the class a context manager (Ch 6). Converting IntegrityError to "
     "ValueError at the boundary keeps SQLite an implementation detail you could swap out."),
        },
    ),
]

DRILLS = [
    dict(kind="recall", q="Which method makes sqlite3 changes permanent?", a=["commit", "commit()", "conn.commit()"]),
    dict(kind="recall", q="Which PRAGMA must you run on every connection to enforce REFERENCES?",
         a=["PRAGMA foreign_keys = ON", "foreign_keys", "pragma foreign_keys=on", "PRAGMA foreign_keys=ON"]),
    dict(kind="recall", q="Order the clauses as SQL runs them: SELECT, WHERE, FROM, ORDER BY, GROUP BY",
         a=["FROM WHERE GROUP BY SELECT ORDER BY", "from, where, group by, select, order by",
            "FROM, WHERE, GROUP BY, SELECT, ORDER BY"]),
    dict(kind="recall", q="Which exception does a UNIQUE or CHECK violation raise?",
         a=["IntegrityError", "sqlite3.IntegrityError"]),
    dict(kind="recall", q="Which JOIN keeps rows from the left table that have no match?", a=["LEFT JOIN", "left"]),
    dict(kind="predict", code=(
        "import sqlite3\nc = sqlite3.connect(':memory:')\nc.execute('CREATE TABLE t (x INTEGER)')\n"
        "c.executemany('INSERT INTO t VALUES (?)', [(1,), (2,), (2,), (None,)])\n"
        "print(c.execute('SELECT COUNT(*), COUNT(x), COUNT(DISTINCT x) FROM t').fetchone())"),
        why="COUNT(*) counts rows; COUNT(x) skips NULLs; DISTINCT removes the duplicate 2."),
    dict(kind="predict", code=(
        "import sqlite3\nc = sqlite3.connect(':memory:')\nc.execute('CREATE TABLE t (x)')\n"
        "with c:\n    c.execute('INSERT INTO t VALUES (1)')\n"
        "try:\n    with c:\n        c.execute('INSERT INTO t VALUES (2)')\n        raise ValueError\n"
        "except ValueError:\n    pass\nprint(c.execute('SELECT x FROM t').fetchall())"),
        why="The second with block rolled back when ValueError escaped it."),
    dict(kind="predict", code="name = 'bob'\nprint(type((name)).__name__, type((name,)).__name__)",
         why="Brackets alone don't make a tuple; the comma does. execute(q, (name,))."),
]
