"""Chapter 12 - sqlite3 and SQL from zero: the lifecycle, queries as a pipeline, placeholders and
injection, transactions, normalisation and joins, indexes, errors, and how to organise database code."""
import sqlite3

from generator import canvas as C
from content.kit import (L, W, callout, card, code, er, flow, go, pipe, practice, section, seq, sql, stamp,
                         sub, table, title_block, tree, two_ways)

ORDER = 12
NUM = 12
TITLE = "sqlite3: a database in a file"
SHORT = "sqlite3"
SLUG = "sqlite3"
ACCENT = C.BLUE

DB = {}


def db():
    if "c" not in DB:
        DB["c"] = sqlite3.connect(":memory:")
    return DB["c"]


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def title_page(ch):
    title_block(ch, 12, TITLE, "a file you can ask questions, that survives crashes", ACCENT)
    f = ch.flow(top=190)
    f.p("Sooner or later a program needs to remember things between runs: users, bookings, scores, loans. "
        "A JSON file works until you need to change one record without rewriting the lot, find \"every loan "
        "overdue by a week\", or survive the power going off halfway through a save.", 14, gap=10)
    f.p("SQLite is a full SQL database that lives in {B:one ordinary file} and ships inside Python as "
        "`sqlite3`. No server, no install. It's in every phone and browser, and it's the right first "
        "database for almost any project.", 14, gap=10)
    table(f, ["need", "JSON file", "SQLite"], [
        ["change one record", "rewrite the whole file", "`UPDATE` touches one row"],
        ["\"which loans are overdue?\"", "load everything, loop in Python", "one `SELECT ... WHERE`"],
        ["crash halfway through a save", "file can be left half-written", "transaction: all or nothing"],
        ["two programs at once", "last writer wins, silently", "locking handles it"],
        ["rules (\"email is unique\")", "your code must remember to check", "the database refuses bad rows"],
    ], widths=[1.8, 2.1, 2.1])
    f.p("The lifecycle you'll use every time:", 13.5, gap=6)
    pipe(f, [("connect", C.BLUE), ("execute SQL", C.GREEN), ("fetch rows", C.TEAL), ("commit", C.ORANGE),
             ("close", C.GREY)],
         under=["opens / creates the file", "with ? placeholders", "tuples or Row objects",
                "makes changes permanent", "or a with block"])


def first_db(ch):
    f = flow(ch)
    sec(f, "Your first database, end to end")
    code(f, """
        import sqlite3

        conn = sqlite3.connect("library.db")
        conn.execute(\"\"\"CREATE TABLE IF NOT EXISTS books (
                            id     INTEGER PRIMARY KEY,
                            title  TEXT NOT NULL,
                            year   INTEGER)\"\"\")
        conn.execute("INSERT INTO books (title, year) VALUES (?, ?)",
                     ("Dune", 1965))
        conn.commit()
        conn.close()

        conn = sqlite3.connect("library.db")
        print(conn.execute("SELECT * FROM books").fetchall())
        conn.close()
    """, notes={3: "1. connect (creates the file)", 8: "2. execute SQL", 10: "3. commit: now on disk",
                11: "4. close", 13: "a later run: still there"})
    f.p("That's the whole library. Everything else in this chapter is SQL (the language you send through "
        "`execute`) and the habits that keep it safe. Here's what happens between your program and the "
        "file:", 13.5, gap=8)
    seq(f, ["your code", "sqlite3 module", "library.db"], [
        ("your code", "sqlite3 module", "connect('library.db')"),
        ("sqlite3 module", "library.db", "open / create file"),
        ("your code", "sqlite3 module", "execute('INSERT ...')"),
        ("sqlite3 module", "library.db", "BEGIN (implicit), write to journal"),
        ("your code", "sqlite3 module", "commit()"),
        ("sqlite3 module", "library.db", "COMMIT: change made permanent"),
        ("library.db", "your code", "SELECT results come back as tuples", "reply"),
    ], step=27)
    callout(f, "trap", "Close without `commit()` and your inserts are {R:silently thrown away}. sqlite3 "
            "opens a transaction automatically before the first `INSERT`/`UPDATE`/`DELETE`, and only "
            "`commit()` ends it. (The `with conn:` form in a few pages does this for you.)")


def queries(ch):
    f = flow(ch)
    sec(f, "SQL in one picture: a query is a pipeline", room=420)
    c = db()
    c.executescript("""
        CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL,
                            year INTEGER, copies INTEGER NOT NULL DEFAULT 1 CHECK (copies >= 0));
    """)
    c.executemany("INSERT INTO books (title, author, year, copies) VALUES (?, ?, ?, ?)", [
        ("Dune", "Herbert", 1965, 2), ("Neuromancer", "Gibson", 1984, 1), ("Emma", "Austen", 1815, 3),
        ("Persuasion", "Austen", 1817, 1), ("Count Zero", "Gibson", 1986, 0), ("Hyperion", "Simmons", 1989, 2),
        ("Children of Dune", "Herbert", 1976, 1), ("Sense and Sensibility", "Austen", 1811, 2),
    ])
    c.commit()
    f.p("You write a query in one order, but the database {B:runs} it in another. Read it in run order "
        "and SQL stops being mysterious:", 13.5, gap=8)
    pipe(f, [("FROM", C.BLUE), ("WHERE", C.RED), ("GROUP BY", C.PURPLE), ("HAVING", C.PURPLE),
             ("SELECT", C.GREEN), ("ORDER BY", C.ORANGE), ("LIMIT", C.GREY)], mono=True, h=34,
         under=["which table", "keep rows", "make groups", "keep groups", "pick columns", "sort", "cut"])
    f.p("Eight books are already in a table. Every grid below is the real result:", 13.5, gap=6)
    sql(f, c, "SELECT title, author, year FROM books WHERE year > 1900 ORDER BY year LIMIT 4")
    sql(f, c, """
        SELECT author, COUNT(*) AS n_books, SUM(copies) AS copies
        FROM books
        GROUP BY author
        HAVING COUNT(*) > 1
        ORDER BY n_books DESC, author
    """)
    go(f, "Before reading on, predict the rows: SELECT title FROM books WHERE copies = 0 OR author = 'Simmons'. "
          "Then: why can't WHERE use the alias n_books? (Look at the pipeline.)")
    sql(f, c, "SELECT title FROM books WHERE copies = 0 OR author = 'Simmons'")
    table(f, ["clause", "job", "tiny example"], [
        ["`SELECT`", "columns or expressions to return", "`SELECT title, year + 1 AS next`"],
        ["`WHERE`", "filter rows (before grouping)", "`WHERE year < 1990`"],
        ["`GROUP BY`", "one output row per group", "`GROUP BY author`"],
        ["`HAVING`", "filter groups (after grouping)", "`HAVING COUNT(*) > 1`"],
        ["`ORDER BY`", "sort; `DESC` reverses", "`ORDER BY year DESC, title`"],
        ["`LIMIT`", "first n rows (`OFFSET` skips)", "`LIMIT 10 OFFSET 20`  (page 3)"],
    ], widths=[1.1, 2.4, 2.6], mono=())


def changing(ch):
    f = flow(ch)
    sec(f, "Changing data: INSERT, UPDATE, DELETE", room=330)
    c = db()
    sql(f, c, "UPDATE books SET copies = copies + 1 WHERE title = 'Count Zero'")
    sql(f, c, "DELETE FROM books WHERE year < 1812")
    sql(f, c, "SELECT title, copies FROM books WHERE author = 'Austen' OR title = 'Count Zero'")
    callout(f, "trap", "An `UPDATE` or `DELETE` with no `WHERE` changes {R:every row}. Write the `WHERE` "
            "first, and try it as a `SELECT` before turning it into an `UPDATE`.")


def injection(ch):
    f = flow(ch)
    sec(f, "Placeholders, and the attack they stop", room=480)
    f.p("The single most important habit in this chapter. Never build SQL by pasting values into the string. "
        "Here's a login check written the wrong way, and what an attacker types as the username:", 13.5,
        gap=8)
    code(f, """
        import sqlite3
        users = sqlite3.connect(":memory:")
        users.execute("CREATE TABLE users (name TEXT, pw TEXT)")
        users.executemany("INSERT INTO users VALUES (?, ?)",
                          [("alice", "x1"), ("bob", "x2")])

        def find_user_BAD(name):
            q = f"SELECT name FROM users WHERE name = '{name}'"
            print("   runs:", q)
            return users.execute(q).fetchall()

        print(find_user_BAD("alice"))
        print(find_user_BAD("nobody' OR '1'='1"))
    """, hl=(8,), notes={8: "value pasted into SQL", 13: "attacker's 'name'"}, w=355, out_max=6)
    f.p("The quote in the input {B:closed the string early}, and the rest became SQL: `OR '1'='1'` is true "
        "for every row, so the \"login\" matched everyone. With a placeholder, the value travels separately "
        "from the SQL and can never become code:", 13.5, gap=8)
    code(f, """
        def find_user(name):
            q = "SELECT name FROM users WHERE name = ?"
            return users.execute(q, (name,)).fetchall()

        print(find_user("alice"))
        print(find_user("nobody' OR '1'='1"))
        print(find_user("O'Brien"))
    """, hl=(2, 3), notes={3: "(name,) is a 1-tuple", 7: "quotes just work, too"}, w=355)
    table(f, ["placeholder style", "looks like", "params"], [
        ["qmark", "`name = ? AND year = ?`", "a tuple, in order: `(name, year)`"],
        ["named", "`name = :n AND year = :y`", "a dict: `{\"n\": name, \"y\": 1965}`"],
    ], widths=[1.1, 2.6, 2.6])
    callout(f, "trap", "Placeholders are for {R:values only}. A table or column name can't be a `?`. If one "
            "has to vary, check it against a fixed list (`if col not in {\"title\", \"year\"}: raise "
            "ValueError`) before putting it in the string. And `(name)` is not a tuple; `(name,)` is.")


def fetching(ch):
    f = flow(ch)
    sec(f, "Getting rows out", room=420)
    c = db()
    f.p("`execute` returns a {B:cursor}: a pointer into the result that you read from. Four ways to read it:",
        13.5, gap=8)
    DB["ns"] = {"conn": c, "__name__": "__main__"}
    code(f, """
        cur = conn.execute("SELECT title, year FROM books ORDER BY year")
        print(cur.fetchone())            # the next row, or None at the end
        print(cur.fetchmany(2))          # the next 2 rows
        print(len(cur.fetchall()))       # everything left

        for title, year in conn.execute("SELECT title, year FROM books LIMIT 2"):
            print(title, year)           # iterate: one row at a time, low memory
    """, ns=DB["ns"])
    f.p("Tuples are fine for two columns, but `row[3]` is unreadable. Set `row_factory = sqlite3.Row` and "
        "rows work by name as well as position:", 13.5, gap=8)
    code(f, """
        import sqlite3
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM books WHERE title = ?", ("Dune",)).fetchone()
        print(row["title"], row["year"], row.keys())
        print(dict(row))
        conn.row_factory = None
    """, ns=DB["ns"])
    f.p("Insert many rows at once with `executemany`, and get the id SQLite gave a new row with "
        "`lastrowid`:", 13.5, gap=8)
    code(f, """
        new = [("Ubik", "Dick", 1969, 1), ("Solaris", "Lem", 1961, 2)]
        conn.executemany("INSERT INTO books (title, author, year, copies) "
                         "VALUES (?, ?, ?, ?)", new)
        cur = conn.execute("INSERT INTO books (title, author) VALUES (?, ?)",
                           ("Kindred", "Butler"))
        print("new id:", cur.lastrowid)
        conn.commit()
    """, ns=DB["ns"])


def transactions(ch):
    f = flow(ch)
    sec(f, "Transactions: all or nothing", room=470)
    f.p("Lending a book is two changes: take a copy off the shelf {B:and} record the loan. If the program "
        "crashes between them, the copy has vanished and nobody has it. A {B:transaction} groups changes so "
        "they all happen or none do.", 13.5, gap=8)
    pipe(f, [("BEGIN", C.GREY), ("UPDATE copies - 1", C.BLUE), ("INSERT loan", C.BLUE),
             ("COMMIT", C.GREEN)], mono=True, h=34, under=["", "", "", "both changes saved"])
    pipe(f, [("BEGIN", C.GREY), ("UPDATE copies - 1", C.BLUE), ("error!", C.RED), ("ROLLBACK", C.ORANGE)],
         mono=True, h=34, under=["", "", "constraint, crash, bug", "as if nothing happened"])
    f.p("`with conn:` is the tidy way: it commits if the block finishes and rolls back if an exception "
        "escapes. Here the `CHECK (copies >= 0)` rule fires on the second loan of a one-copy book:", 13.5,
        gap=8)
    code(f, """
        conn.execute("CREATE TABLE IF NOT EXISTS loans (book_id INTEGER, who TEXT)")
        conn.commit()

        def lend(book_id, who):
            with conn:                                   # one transaction
                conn.execute("INSERT INTO loans VALUES (?, ?)", (book_id, who))
                conn.execute("UPDATE books SET copies = copies - 1 WHERE id = ?", (book_id,))

        nid = conn.execute("SELECT id FROM books WHERE title='Neuromancer'").fetchone()[0]
        lend(nid, "ana")
        try:
            lend(nid, "ben")                             # no copies left
        except sqlite3.IntegrityError as e:
            print("refused:", e)
        print(conn.execute("SELECT who FROM loans").fetchall())
        print(conn.execute("SELECT copies FROM books WHERE id=?", (nid,)).fetchone())
    """, ns=DB["ns"], hl=(5,), notes={})
    f.p("Ben's loan row was inserted first, then the `UPDATE` failed, and the rollback removed his loan too. "
        "The database never shows half a loan.", 13.5, gap=8)
    callout(f, "trap", "`with conn:` commits or rolls back, but it does {R:not close} the connection (unlike "
            "`with open(...)`). Close it yourself, or use `contextlib.closing(sqlite3.connect(...))`.")
    callout(f, "honest", "Python 3.12 added `sqlite3.connect(..., autocommit=False)`, which gives PEP 249 "
            "behaviour (always in a transaction; you commit). The default you've seen here is the older "
            "\"legacy\" mode, and it's what most existing code and tutorials assume.")


def design(ch):
    f = flow(ch)
    sec(f, "Designing tables: one fact in one place", room=470)
    c = db()
    c.executescript("""
        CREATE TABLE loans_flat (member TEXT, email TEXT, book TEXT, due TEXT);
        INSERT INTO loans_flat VALUES
          ('Ana Silva', 'ana@x.org', 'Dune', '2026-10-01'),
          ('Ana Silva', 'ana@x.org', 'Emma', '2026-10-03'),
          ('Ben Okafor', 'ben@x.org', 'Dune', '2026-10-02'),
          ('Ana Silva', 'ana@old.org', 'Ubik', '2026-10-09');
    """)
    f.p("The first design everyone writes is one wide table. It works until a fact needs to change:", 13.5,
        gap=6)
    sql(f, c, "SELECT * FROM loans_flat")
    f.p("Ana's email is stored three times, and one copy is already out of date. Which is right? This is an "
        "{B:update anomaly}. The fix is {B:normalisation}: each fact is stored once, in the table it belongs "
        "to, and other tables {B:refer to it by id}.", 13.5, gap=8)
    er(f, [
        ("members", [("id", "PK"), ("name", ""), ("email", "")]),
        ("loans", [("id", "PK"), ("member_id", "FK"), ("book_id", "FK"), ("due", "")]),
        ("books", [("id", "PK"), ("title", ""), ("author", ""), ("copies", "")]),
    ], [("loans.member_id", "members.id"), ("loans.book_id", "books.id")])
    c.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL);
        CREATE TABLE loans2 (id INTEGER PRIMARY KEY,
                             member_id INTEGER NOT NULL REFERENCES members(id),
                             book_id INTEGER NOT NULL REFERENCES books(id),
                             due TEXT NOT NULL);
        INSERT INTO members (name, email) VALUES ('Ana Silva', 'ana@x.org'), ('Ben Okafor', 'ben@x.org'),
                                                 ('Cat Moreau', 'cat@x.org');
        INSERT INTO loans2 (member_id, book_id, due) VALUES (1, 1, '2026-10-01'), (1, 3, '2026-10-03'),
                                                            (2, 1, '2026-10-02');
    """)
    table(f, ["constraint", "the database refuses...", "error"], [
        ["`PRIMARY KEY`", "a duplicate or missing id (`INTEGER PRIMARY KEY` auto-numbers)", "IntegrityError"],
        ["`NOT NULL`", "a missing value", "IntegrityError"],
        ["`UNIQUE`", "a second row with the same value (two members, one email)", "IntegrityError"],
        ["`CHECK (expr)`", "a row where expr is false (`copies >= 0`)", "IntegrityError"],
        ["`REFERENCES t(id)`", "an id that doesn't exist in `t`, {R:only if} `PRAGMA foreign_keys = ON`",
         "IntegrityError"],
    ], widths=[1.5, 3.4, 1.2])
    sql(f, c, "INSERT INTO loans2 (member_id, book_id, due) VALUES (99, 1, '2026-11-01')",
        raises=sqlite3.IntegrityError)
    callout(f, "trap", "SQLite ignores `REFERENCES` unless you run `PRAGMA foreign_keys = ON` on {R:every new "
            "connection}, straight after connecting (it does nothing inside an open transaction). Put it in "
            "your `connect()` helper and forget about it.")


def joins(ch):
    f = flow(ch)
    sec(f, "JOIN: putting the facts back together", room=470)
    c = db()
    f.p("Normalised tables are split apart; a {B:join} glues them back for one query. `JOIN ... ON` pairs "
        "every row of one table with the rows of the other where the condition holds:", 13.5, gap=8)
    sql(f, c, """
        SELECT m.name, b.title, l.due
        FROM loans2 AS l
        JOIN members AS m ON m.id = l.member_id
        JOIN books   AS b ON b.id = l.book_id
        ORDER BY l.due
    """)
    f.p("Cat has no loans, so she isn't in that result: a plain (inner) join keeps only rows that "
        "match. To keep everyone from the left table, use `LEFT JOIN`; the missing side comes back as "
        "`NULL`, which `COUNT(column)` doesn't count:", 13.5, gap=8)
    sql(f, c, """
        SELECT m.name, COUNT(l.id) AS loans
        FROM members AS m
        LEFT JOIN loans2 AS l ON l.member_id = m.id
        GROUP BY m.id
        ORDER BY loans DESC
    """)
    two_ways(f, ("Let SQL do it", """
        rows = conn.execute(\"\"\"
            SELECT m.name, COUNT(l.id)
            FROM members m
            LEFT JOIN loans2 l
              ON l.member_id = m.id
            GROUP BY m.id
            ORDER BY m.name\"\"\").fetchall()
        print(rows)
    """), ("Fetch everything, loop in Python", """
        counts = {}
        for (mid, name) in conn.execute(
                "SELECT id, name FROM members"):
            counts[mid] = [name, 0]
        for (mid,) in conn.execute(
                "SELECT member_id FROM loans2"):
            counts[mid][1] += 1
        print(sorted(map(tuple, counts.values())))
    """), verdict=[("fast on big tables", 5, 2), ("one round trip", 5, 1), ("easy to debug step by step", 2, 4)],
        ns={"conn": c, "__name__": "__main__"})
    callout(f, "rule", "Filter, join, count and sort {B:in SQL}, then fetch only what you need. Moving "
            "100,000 rows into Python to count them is the classic beginner slowdown.")


def indexes(ch):
    f = flow(ch)
    sec(f, "Indexes: why some queries are instant", room=470)
    f.p("To find rows matching a `WHERE`, SQLite either reads {B:every row} (a scan, O(n)) or jumps straight "
        "to them through an {B:index}, a sorted B-tree kept beside the table (O(log n)). `EXPLAIN QUERY "
        "PLAN` tells you which it chose:", 13.5, gap=8)
    code(f, """
        import sqlite3, time
        big = sqlite3.connect(":memory:")
        big.execute("CREATE TABLE visits (id INTEGER PRIMARY KEY, card TEXT, day TEXT)")
        rows = ((f"C{i % 20000:05d}", f"2026-{i % 12 + 1:02d}-01")
                for i in range(200_000))
        big.executemany("INSERT INTO visits (card, day) VALUES (?, ?)", rows)

        def plan(q):
            return big.execute("EXPLAIN QUERY PLAN " + q, ("?",)).fetchone()[-1]

        def timed(q, runs=200):
            t = time.perf_counter()
            for _ in range(runs):
                big.execute(q, ("C01234",)).fetchall()
            return (time.perf_counter() - t) / runs * 1000

        Q = "SELECT day FROM visits WHERE card = ?"
        print(plan(Q), f"{timed(Q, 20):.2f} ms")
        big.execute("CREATE INDEX idx_visits_card ON visits(card)")
        print(plan(Q), f"{timed(Q):.3f} ms")
    """, hl=(17, 19), out_max=4)
    f.p("Same query, same answer; the index turned a 200,000-row scan into a lookup that's hundreds to "
        "thousands of times faster. Primary keys and `UNIQUE` columns get an index automatically.", 13.5, gap=8)
    table(f, ["index a column when...", "don't bother when..."], [
        ["you search or join on it often (`WHERE card = ?`, foreign keys)", "the table is small (hundreds of rows)"],
        ["you sort by it a lot (`ORDER BY due`)", "the column has a handful of values (yes/no)"],
        ["the table will grow large", "the table is written far more than read (each index slows writes)"],
    ], widths=[1, 1])


def errors(ch):
    f = flow(ch)
    sec(f, "When it goes wrong: the error family", room=430)
    tree(f, {
        "e": ("Exception", 0.5, 0),
        "s": ("sqlite3.Error", 0.5, 1),
        "i": ("InterfaceError", 0.2, 2),
        "d": ("DatabaseError", 0.65, 2),
        "ig": ("IntegrityError", 0.14, 3),
        "op": ("OperationalError", 0.4, 3),
        "pr": ("ProgrammingError", 0.67, 3),
        "da": ("DataError …", 0.9, 3),
    }, [("e", "s"), ("s", "i"), ("s", "d"), ("d", "ig"), ("d", "op"), ("d", "pr"), ("d", "da")])
    table(f, ["error", "usually means", "fix"], [
        ["IntegrityError", "a constraint said no (UNIQUE, NOT NULL, CHECK, foreign key)", "expected: catch it "
         "and tell the user"],
        ["OperationalError", "bad SQL, missing table, \"database is locked\", can't open file",
         "a bug or an environment problem"],
        ["ProgrammingError", "wrong number of `?` values, using a closed connection", "a bug in your code"],
    ], widths=[1.4, 2.8, 1.8])
    c = db()
    sql(f, c, "INSERT INTO members (name, email) VALUES ('Ana Two', 'ana@x.org')", raises=sqlite3.IntegrityError)
    sql(f, c, "SELEC title FROM books", raises=sqlite3.OperationalError)
    sql(f, c, "SELECT * FROM books WHERE id = ? AND year = ?", params=(1,), raises=sqlite3.ProgrammingError)
    callout(f, "rule", "Catch `IntegrityError` where you can say something useful (\"that email is already "
            "registered\"). Let `OperationalError` and `ProgrammingError` crash loudly during development: "
            "they're bugs, and hiding them makes them worse.")


def organise(ch):
    f = flow(ch)
    sec(f, "Organising database code", room=470)
    f.p("Scattering `conn.execute` through a program makes it hard to change. Keep all the SQL in one "
        "module with small functions that take a connection, and the rest of the program never sees SQL:",
        13.5, gap=8)
    code(f, """
        import sqlite3
        from dataclasses import dataclass

        SCHEMA = \"\"\"
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL);
        \"\"\"

        @dataclass
        class Member:
            id: int
            name: str
            email: str

        def connect(path=":memory:"):
            conn = sqlite3.connect(path)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.executescript(SCHEMA)
            return conn

        def add_member(conn, name, email) -> int:
            with conn:
                return conn.execute("INSERT INTO members (name, email) VALUES (?, ?)",
                                    (name, email)).lastrowid

        def get_member(conn, member_id) -> Member | None:
            row = conn.execute("SELECT id, name, email FROM members WHERE id = ?",
                               (member_id,)).fetchone()
            return Member(*row) if row else None

        conn = connect()
        mid = add_member(conn, "Ana", "ana@x.org")
        print(get_member(conn, mid), get_member(conn, 99))
    """, ns={"__name__": "__main__"}, hl=(17, 22, 28))
    table(f, ["habit", "why"], [
        ["one `connect()` helper", "every connection gets the same PRAGMAs and schema"],
        ["functions take `conn` as a parameter", "tests pass `\":memory:\"`; no global state"],
        ["return dataclasses, not raw tuples", "`m.email` beats `row[2]`; the rest of the code doesn't know it's SQL"],
        ["schema version in `PRAGMA user_version`", "a tiny migration system: `if version < 2: ALTER TABLE ...`"],
        ["dates as ISO text `'2026-09-28'`", "they sort correctly as strings; the old automatic date "
         "converters are deprecated since 3.12"],
    ], widths=[2, 3])


def finish(ch):
    f = flow(ch)
    sec(f, "The card, practice and stamp", room=520)
    card(f, "sqlite3", {
        "Job": "A full SQL database in one file (or `\":memory:\"`), built into Python.",
        "Core objects": "`Connection` (from `sqlite3.connect`): `execute`, `executemany`, `commit`, "
                        "`rollback`, `close`. `Cursor`: `fetchone`, `fetchall`, iterate, `lastrowid`. "
                        "`sqlite3.Row` for rows by name.",
        "Lifecycle": "connect → `PRAGMA foreign_keys = ON` → execute with `?` → fetch → commit (or `with "
                     "conn:`) → close.",
        "Errors": "`IntegrityError` (constraints), `OperationalError` (bad SQL, locked), `ProgrammingError` "
                  "(wrong params, closed). All subclass `sqlite3.Error`.",
        "Traps": "{R:f-strings in SQL} (injection) · forgetting `commit` · `with conn` doesn't close · "
                 "foreign keys off by default · `(x)` isn't a tuple.",
        "Docs": "docs.python.org/3/library/sqlite3.html · sqlite.org/lang.html (the SQL itself)",
    })
    practice(f, 12)
    stamp(f, [
        (9, "Persistent structured data: `sqlite3` built in (one file, SQL, transactions). Other databases "
            "(PostgreSQL, MySQL) use the same DB-API shape: connect, cursor, execute, commit."),
        (7, "Errors from a library form a class tree (`sqlite3.Error` → `IntegrityError`...); catch the "
            "most specific one you can handle."),
    ])
    callout(f, "other", "Every language has this exact shape. Java: JDBC `Connection`, `PreparedStatement` "
            "(the `?` placeholders), `commit()`. Go: `database/sql` with `db.Query(q, args...)`. The SQL "
            "and the injection rule are identical everywhere.")
    callout(f, "deep", "Vault notes: {b:11.1} Boundaries turn assumptions into failure modes · {b:19.12} "
            "Injection as a general grammar failure · {b:11.4} Context managers and deterministic release · "
            "{b:11.6} Buffers, flushing, and durability · {b:16.19} Relational joins and cardinality.")


def build(ch):
    DB.clear()
    title_page(ch)
    first_db(ch)
    queries(ch)
    changing(ch)
    injection(ch)
    fetching(ch)
    transactions(ch)
    design(ch)
    joins(ch)
    indexes(ch)
    errors(ch)
    organise(ch)
    finish(ch)
