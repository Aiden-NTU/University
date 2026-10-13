EXERCISES = [
    dict(
        id="7.1", kind="explore", title="Map a module's public surface",
        task="""
        Write `public_api(module)` that returns a dict with three **sorted** lists of names:

        - `"functions"`: public callables that are not classes (functions and built-in functions)
        - `"classes"`: public classes that are **not** exceptions
        - `"exceptions"`: public classes that are subclasses of `BaseException`

        "Public" means the name doesn't start with `_`. Ignore everything else (constants, submodules).

        Tools: `dir`, `getattr`, `callable`, `isinstance(x, type)`, `issubclass`, or the `inspect` module.
        Try it on `json`, `hmac` and `sqlite3` in the REPL before running the tests.
        """,
        stub='''
        def public_api(module):
            """Return {"functions": [...], "classes": [...], "exceptions": [...]}, each sorted."""
            ...
        ''',
        tests='''
        import json, sqlite3, types

        def fake():
            m = types.ModuleType("fake")
            class Thing: pass
            class Oops(ValueError): pass
            def go(): pass
            m.Thing, m.Oops, m.go, m.len = Thing, Oops, go, len
            m._hidden, m.VERSION, m.json = go, "1.0", json
            return m

        def test_exact_answer_on_a_small_module(m):
            equal(m.public_api(fake()), {"functions": ["go", "len"], "classes": ["Thing"],
                                         "exceptions": ["Oops"]}, "public_api(fake)")

        def test_json(m):
            api = m.public_api(json)
            for name in ["dump", "dumps", "load", "loads"]:
                check(name in api["functions"], f"json.{name} should be in functions")
            check("JSONDecoder" in api["classes"], "JSONDecoder is a class")
            check("JSONDecodeError" in api["exceptions"], "JSONDecodeError is an exception")
            check("JSONDecodeError" not in api["classes"], "exceptions go only in 'exceptions'")

        def test_sqlite3(m):
            api = m.public_api(sqlite3)
            check("connect" in api["functions"], "sqlite3.connect is a function (built-in)")
            check({"Connection", "Cursor", "Row"} <= set(api["classes"]), "Connection, Cursor, Row are classes")
            check({"Error", "IntegrityError", "OperationalError"} <= set(api["exceptions"]),
                  "the sqlite3 errors")

        def test_lists_are_sorted_and_public(m):
            for mod in (json, sqlite3):
                api = m.public_api(mod)
                for k, names in api.items():
                    equal(names, sorted(names), f"{k} for {mod.__name__} sorted")
                    check(not any(n.startswith("_") for n in names), f"no _private names in {k}")
        ''',
        alts={
            "plain loop": ('''
                def public_api(module):
                    out = {"functions": [], "classes": [], "exceptions": []}
                    for name in sorted(dir(module)):
                        if name.startswith("_"):
                            continue
                        obj = getattr(module, name)
                        if isinstance(obj, type):
                            key = "exceptions" if issubclass(obj, BaseException) else "classes"
                            out[key].append(name)
                        elif callable(obj):
                            out["functions"].append(name)
                    return out
            ''', "Sorting dir() once up front keeps every list sorted for free. callable() also catches "
                 "objects with __call__, which is usually what you want."),
            "inspect predicates": ('''
                import inspect

                def public_api(module):
                    members = [(n, o) for n, o in inspect.getmembers(module) if not n.startswith("_")]
                    return {
                        "functions": [n for n, o in members if inspect.isroutine(o)],
                        "classes": [n for n, o in members
                                    if inspect.isclass(o) and not issubclass(o, BaseException)],
                        "exceptions": [n for n, o in members
                                       if inspect.isclass(o) and issubclass(o, BaseException)],
                    }
            ''', "inspect.getmembers already returns (name, value) pairs sorted by name. isroutine covers "
                 "Python functions and C built-ins; more readable, three passes instead of one."),
        },
    ),
    dict(
        id="7.2", kind="explore", title="Read a signature with inspect",
        task="""
        Write `describe(func)` returning a dict:

        - `"required"`: names you **must** pass (no default), in order, excluding `*args` / `**kwargs`
        - `"keyword_only"`: names that can only be passed by keyword (after a bare `*` or after `*args`)
        - `"positional_only"`: names that can only be passed by position (before a `/`)

        Use `inspect.signature(func).parameters`. Each parameter has `.kind` and `.default`
        (`inspect.Parameter.empty` when there's no default).
        """,
        stub='''
        import inspect

        def describe(func):
            ...
        ''',
        tests='''
        def f1(a, b, c=1): pass
        def f2(a, /, b, *, c, d=2): pass
        def f3(*args, key, **kw): pass
        def f4(x, y=0, /, z=1, *rest, flag=False): pass

        def test_ordinary(m):
            equal(m.describe(f1), {"required": ["a", "b"], "keyword_only": [], "positional_only": []}, "f1")

        def test_markers(m):
            equal(m.describe(f2), {"required": ["a", "b", "c"], "keyword_only": ["c", "d"],
                                   "positional_only": ["a"]}, "f2(a, /, b, *, c, d=2)")

        def test_varargs_are_not_required(m):
            equal(m.describe(f3), {"required": ["key"], "keyword_only": ["key"], "positional_only": []},
                  "f3(*args, key, **kw)")

        def test_mixed(m):
            equal(m.describe(f4), {"required": ["x"], "keyword_only": ["flag"], "positional_only": ["x", "y"]},
                  "f4(x, y=0, /, z=1, *rest, flag=False)")

        def test_a_builtin(m):
            equal(m.describe(sorted)["positional_only"], ["iterable"], "sorted's positional-only")
            equal(m.describe(sorted)["keyword_only"], ["key", "reverse"], "sorted's keyword-only")
        ''',
        alts={
            "one pass": ('''
                import inspect
                P = inspect.Parameter

                def describe(func):
                    out = {"required": [], "keyword_only": [], "positional_only": []}
                    for p in inspect.signature(func).parameters.values():
                        if p.kind in (P.VAR_POSITIONAL, P.VAR_KEYWORD):
                            continue
                        if p.default is P.empty:
                            out["required"].append(p.name)
                        if p.kind is P.KEYWORD_ONLY:
                            out["keyword_only"].append(p.name)
                        if p.kind is P.POSITIONAL_ONLY:
                            out["positional_only"].append(p.name)
                    return out
            ''', "One loop, three buckets. The kinds are an enum, so compare with `is`."),
            "comprehensions": ('''
                import inspect
                P = inspect.Parameter

                def describe(func):
                    ps = list(inspect.signature(func).parameters.values())
                    varargs = (P.VAR_POSITIONAL, P.VAR_KEYWORD)
                    return {
                        "required": [p.name for p in ps if p.default is P.empty and p.kind not in varargs],
                        "keyword_only": [p.name for p in ps if p.kind is P.KEYWORD_ONLY],
                        "positional_only": [p.name for p in ps if p.kind is P.POSITIONAL_ONLY],
                    }
            ''', "Reads like the spec, one line per key; walks the list three times (irrelevant here)."),
        },
    ),
    dict(
        id="7.3", kind="explore", title="Did you mean...? (difflib)",
        task="""
        Write `suggest(word, choices)` that returns the single closest string in `choices`,
        or `None` if nothing is reasonably close (a random word shouldn't match anything).

        This is what a CLI does when you mistype a command. The module that does it is
        `difflib`; find the function with `dir(difflib)` and its docs. (Writing your own edit
        distance is also allowed, and good practice.)
        """,
        stub='''
        def suggest(word, choices):
            ...
        ''',
        tests='''
        CMDS = ["status", "commit", "checkout", "branch", "merge", "rebase", "push", "pull"]

        def test_typos(m):
            for typo, want in [("comit", "commit"), ("chekout", "checkout"), ("brnch", "branch"),
                               ("stauts", "status"), ("rebsae", "rebase"), ("psuh", "push")]:
                equal(m.suggest(typo, CMDS), want, f"suggest({typo!r})")

        def test_exact_match_wins(m):
            equal(m.suggest("pull", CMDS), "pull", "an exact match")

        def test_nothing_close(m):
            for junk in ["xyzzy", "qqqq", "zebra-crossing"]:
                equal(m.suggest(junk, CMDS), None, f"suggest({junk!r})")

        def test_empty_choices(m):
            equal(m.suggest("anything", []), None, "no choices at all")
        ''',
        alts={
            "difflib": ('''
                import difflib

                def suggest(word, choices):
                    best = difflib.get_close_matches(word, choices, n=1)
                    return best[0] if best else None
            ''', "Two lines, because difflib already has the job. Default cutoff 0.6 decides 'close enough'."),
            "own edit distance": ('''
                def distance(a, b):
                    prev = list(range(len(b) + 1))
                    for i, ca in enumerate(a, 1):
                        cur = [i]
                        for j, cb in enumerate(b, 1):
                            cost = 0 if ca == cb else 1
                            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
                        prev = cur
                    return prev[-1]

                def suggest(word, choices):
                    scored = sorted((distance(word, c), c) for c in choices)
                    if not scored:
                        return None
                    d, best = scored[0]
                    return best if d <= max(1, len(best) // 2) else None
            ''', "Levenshtein distance by dynamic programming (Ch 21): O(len(a)*len(b)). You choose the "
                 "threshold yourself, which is the hard, judgement part difflib hides."),
        },
    ),
    dict(
        id="7.4", kind="explore", title="Zip and unzip in memory (zipfile)",
        task="""
        Write two functions:

        - `zip_texts(files)` takes a dict `{name: text}` and returns the **bytes** of a zip archive
          containing one file per entry (text encoded as UTF-8).
        - `unzip_texts(data)` takes zip bytes and returns the dict back.

        Don't write to disk: `io.BytesIO` is a file-like object in memory. Remember the release
        step (the zip's index is written when the `ZipFile` is closed).
        """,
        stub='''
        import io
        import zipfile

        def zip_texts(files):
            ...

        def unzip_texts(data):
            ...
        ''',
        tests='''
        import io, zipfile, random

        def test_round_trip(m):
            rng = random.Random(3)
            for _ in range(30):
                files = {f"f{i}.txt": "".join(rng.choice("abc é\\n✓") for _ in range(rng.randint(0, 40)))
                         for i in range(rng.randint(0, 5))}
                equal(m.unzip_texts(m.zip_texts(files)), files, "round trip")

        def test_real_zip(m):
            data = m.zip_texts({"a.txt": "hello"})
            check(isinstance(data, bytes), "zip_texts should return bytes")
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                equal(z.namelist(), ["a.txt"], "names inside")
                equal(z.read("a.txt"), b"hello", "content")

        def test_reads_zip_made_elsewhere(m):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                z.writestr("x/y.txt", "nested ✓")
            equal(m.unzip_texts(buf.getvalue()), {"x/y.txt": "nested ✓"}, "unzip of a compressed zip")
        ''',
        alts={
            "with blocks": ('''
                import io
                import zipfile

                def zip_texts(files):
                    buf = io.BytesIO()
                    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                        for name, text in files.items():
                            z.writestr(name, text.encode("utf-8"))
                    return buf.getvalue()

                def unzip_texts(data):
                    with zipfile.ZipFile(io.BytesIO(data)) as z:
                        return {name: z.read(name).decode("utf-8") for name in z.namelist()}
            ''', "getvalue() is called after the with block, so the index has been written. ZIP_DEFLATED "
                 "compresses; the default ZIP_STORED doesn't."),
        },
    ),
    dict(
        id="7.5", kind="explore", title="Wrap text for a terminal (textwrap)",
        task="""
        Write `boxed(text, width)` that wraps `text` into lines of at most `width` characters
        **including** a `"| "` prefix on every line, and returns them joined with `"\\n"`.

        Words are never split (assume no single word is longer than `width - 2`), the words stay in
        order, and each line is as full as possible (a word only moves down if it doesn't fit).
        Empty or all-whitespace text gives `""`.

        `textwrap` has an argument for the prefix; find it with `help(textwrap.TextWrapper)`.
        """,
        stub='''
        def boxed(text, width):
            ...
        ''',
        tests='''
        def check_box(m, text, width):
            out = m.boxed(text, width)
            if not text.split():
                equal(out, "", "empty text")
                return
            lines = out.split("\\n")
            for ln in lines:
                check(ln.startswith("| "), f"every line starts with '| ': {ln!r}")
                check(len(ln) <= width, f"line longer than {width}: {ln!r}")
            equal(" ".join(ln[2:] for ln in lines).split(), text.split(), "the words, in order")
            for a, b in zip(lines, lines[1:]):
                nxt = b[2:].split()[0]
                check(len(a) + 1 + len(nxt) > width, f"{nxt!r} would have fitted on {a!r}")

        def test_random_paragraphs(m):
            words = rand_words(400)
            for width in (12, 20, 33, 60):
                for k in range(0, 400, 37):
                    check_box(m, " ".join(words[k:k + 25]), width)

        def test_empty(m):
            check_box(m, "", 20)
            check_box(m, "   ", 20)
        ''',
        alts={
            "textwrap": ('''
                import textwrap

                def boxed(text, width):
                    return "\\n".join(textwrap.wrap(text, width, initial_indent="| ", subsequent_indent="| "))
            ''', "The prefix counts towards the width, which is exactly the rule here."),
            "greedy by hand": ('''
                def boxed(text, width):
                    lines, cur = [], "| "
                    for word in text.split():
                        if cur == "| ":
                            cur += word
                        elif len(cur) + 1 + len(word) <= width:
                            cur += " " + word
                        else:
                            lines.append(cur)
                            cur = "| " + word
                    if cur != "| ":
                        lines.append(cur)
                    return "\\n".join(lines)
            ''', "Greedy line filling is optimal for the line count; typesetters (TeX) use a costlier "
                 "algorithm to balance line lengths."),
        },
    ),
    dict(
        id="7.6", kind="project", title="Library card generator",
        task="""
        Mini-project: automate the start of the method. Write `library_card(name)` that imports the
        module called `name` (use `importlib.import_module`) and returns a Markdown string with
        these six headings, in this order, each on its own line as `## Heading`:

        Job, Core objects, Lifecycle, Errors, Traps, Docs

        Fill in what a program can find out:

        - **Job**: the first non-empty line of the module's docstring
        - **Core objects**: the public classes (not exceptions), comma-separated
        - **Errors**: the public exception classes, comma-separated
        - **Docs**: `https://docs.python.org/3/library/<name>.html`
        - **Lifecycle** and **Traps**: the line `TODO: spike it` (a human has to fill these in)

        Then run it on five modules you don't know, and finish the TODOs by hand. Reuse your
        7.1 solution if you like.
        """,
        stub='''
        import importlib

        def library_card(name):
            ...
        ''',
        tests='''
        import re

        HEADS = ["Job", "Core objects", "Lifecycle", "Errors", "Traps", "Docs"]

        def section(card, head):
            parts = re.split(r"^## ", card, flags=re.M)
            for p in parts:
                if p.startswith(head + "\\n") or p.strip() == head:
                    return p[len(head):].strip()
            raise Fail(f"no '## {head}' section")

        def test_headings_in_order(m):
            card = m.library_card("json")
            found = re.findall(r"^## (.+)$", card, flags=re.M)
            equal([h.strip() for h in found], HEADS, "the headings")

        def test_job_line(m):
            equal(section(m.library_card("hmac"), "Job"),
                  "HMAC (Keyed-Hashing for Message Authentication) module.", "hmac's Job")
            equal(section(m.library_card("zipfile"), "Job"), "Read and write ZIP files.",
                  "zipfile (docstring starts with a blank line)")

        def test_objects_and_errors(m):
            card = m.library_card("sqlite3")
            objs = section(card, "Core objects")
            errs = section(card, "Errors")
            for c in ["Connection", "Cursor", "Row"]:
                check(c in objs, f"{c} under Core objects")
            for e in ["IntegrityError", "OperationalError"]:
                check(e in errs, f"{e} under Errors")
                check(e not in objs, f"{e} should not be under Core objects")

        def test_docs_and_todos(m):
            card = m.library_card("difflib")
            equal(section(card, "Docs"), "https://docs.python.org/3/library/difflib.html", "Docs link")
            equal(section(card, "Lifecycle"), "TODO: spike it", "Lifecycle")
            equal(section(card, "Traps"), "TODO: spike it", "Traps")
        ''',
        alts={
            "straightforward": ('''
                import importlib

                def library_card(name):
                    mod = importlib.import_module(name)
                    doc = (mod.__doc__ or "").strip()
                    job = doc.splitlines()[0].strip() if doc else "(no docstring)"
                    classes, errors = [], []
                    for n in sorted(dir(mod)):
                        obj = getattr(mod, n)
                        if n.startswith("_") or not isinstance(obj, type):
                            continue
                        (errors if issubclass(obj, BaseException) else classes).append(n)
                    rows = {
                        "Job": job,
                        "Core objects": ", ".join(classes) or "(functions only)",
                        "Lifecycle": "TODO: spike it",
                        "Errors": ", ".join(errors) or "(none of its own)",
                        "Traps": "TODO: spike it",
                        "Docs": f"https://docs.python.org/3/library/{name}.html",
                    }
                    return "\\n\\n".join(f"## {k}\\n{v}" for k, v in rows.items()) + "\\n"
            ''', "A dict keeps the headings in insertion order, so the output order is the dict order. "
                 "Strip the docstring first: some start with a newline."),
        },
    ),
]

DRILLS = [
    dict(kind="recall", q="Which built-in lists every attribute name of an object?", a=["dir", "dir()", "dir(x)"]),
    dict(kind="recall", q="In a signature, everything before a bare / is ...?",
         a=["positional-only", "positional only"]),
    dict(kind="recall", q="In a signature, everything after a bare * is ...?", a=["keyword-only", "keyword only"]),
    dict(kind="recall", q="Which inspect function shows a function's Python source?",
         a=["inspect.getsource", "getsource"]),
    dict(kind="recall", q="Terminal command to read the docs of module hmac offline?",
         a=["python -m pydoc hmac", "python3 -m pydoc hmac", "pydoc hmac"]),
    dict(kind="recall", q="The four library shapes: bag of functions, object factory, class to subclass, and ...?",
         a=["framework", "runtime", "framework / runtime"]),
    dict(kind="predict", code="import hmac\nprint([n for n in dir(hmac) if not n.startswith('_')][:3])"),
    dict(kind="predict", code="def f(a, /, b, *, c): return a + b + c\nprint(f(1, b=2, c=3))"),
    dict(kind="predict", code="def f(a, /, b, *, c): return a + b + c\nprint(f(1, 2, 3))",
         why="c is keyword-only: f(1, 2, c=3). The error is a TypeError."),
]
