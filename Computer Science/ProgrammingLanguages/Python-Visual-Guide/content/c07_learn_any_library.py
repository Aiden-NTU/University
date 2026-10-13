"""Chapter 7 - How to learn any library: the method that turns an unseen module into a library card.
dir/help/inspect, reading signatures and docs pages, reading the source, the 20-line spike."""
from generator import canvas as C
from content.kit import (L, W, callout, card, code, flow, go, pipe, practice, repl, section, shell, stamp,
                         sub, table, title_block, tree)

ORDER = 7
NUM = 7
TITLE = "How to learn any library"
SHORT = "Learn any library"
SLUG = "Learn-any-library"
ACCENT = C.TEAL


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def title_page(ch):
    title_block(ch, 7, TITLE, "the method that makes every other chapter optional reading", ACCENT)
    f = ch.flow(top=190)
    f.p("When `sqlite3` or `hmac` feels impossible, the problem is almost never syntax. You can call a "
        "function and write a `with` block. What's missing is the {B:shape} of the library: what you "
        "create first, what you call on it, what you must close, and what goes wrong.", 14, gap=10)
    f.p("This chapter is the method for finding that shape on your own, for any module, in any language. "
        "It has four tools and one output:", 14, gap=8)
    pipe(f, [("REPL\ndir · help", C.BLUE), ("inspect\nsignatures", C.PURPLE), ("docs page\n+ source", C.ORANGE),
             ("20-line\nspike", C.GREEN), ("library\ncard", C.TEAL)], h=46,
         under=["poke it", "what does it take?", "what does it promise?", "make it work, then break it",
                "six answers"])
    f.p("Every later chapter is this method already applied to one module. Once it's a habit, you won't need "
        "a chapter (or a tutorial) to start using an unfamiliar library.", 14, gap=10)
    callout(f, "idea", "You don't learn a library by reading all of it. You learn its {B:shape} (the six card "
            "questions), then look up details only when you need them.")


def shapes(ch):
    f = flow(ch)
    sec(f, "The four shapes a library comes in")
    f.p("Nearly every library is one of four shapes. Spotting which one tells you how to start:", 13.5, gap=8)
    table(f, ["shape", "how you use it", "examples"], [
        ["**Bag of functions**", "import, call functions, get values back. Nothing to close.",
         "`math`, `json`, `base64`, `statistics`, `difflib`"],
        ["**Object factory**", "a function makes an object; you call its methods; often you must close it.",
         "`sqlite3.connect`, `open`, `hmac.new`, `zipfile.ZipFile`"],
        ["**Class to subclass**", "you write a subclass and fill in methods; the library calls them.",
         "`unittest.TestCase`, `http.server`'s `BaseHTTPRequestHandler`"],
        ["**Framework / runtime**", "you hand over your functions; the library runs the loop.",
         "`asyncio.run`, `tkinter` mainloop, `argparse` (lighter)"],
    ], widths=[1.3, 2.6, 2.1])
    f.p("The {b:object factory} shape is where most people get stuck, because the important part is the "
        "{B:lifecycle}: the order of calls, and what must happen at the end.", 13.5, gap=8)
    pipe(f, [("import", C.GREY), ("make the object", C.BLUE), ("use its methods", C.GREEN),
             ("handle errors", C.RED), ("release it", C.ORANGE)],
         under=["", "connect(), open(), new()", "execute(), read(), update()", "which exceptions?",
                "close(), or a with block"])
    code(f, """
        import zipfile, io

        buf = io.BytesIO()                         # an in-memory 'file'
        with zipfile.ZipFile(buf, "w") as z:       # make the object
            z.writestr("hello.txt", "hi there")    # use its methods
        # leaving the with block released it (wrote the zip's index)

        with zipfile.ZipFile(buf) as z:
            print(z.namelist(), z.read("hello.txt"))
    """, hl=(4, 5, 6), expect="['hello.txt'] b'hi there'")
    callout(f, "trap", "Forgetting the release step causes the bugs that make no sense: a zip with no index, "
            "a database change that never saved, a file that's still empty. If a library hands you an object, "
            "your first question is {R:how do I close it?}")


def repl_tools(ch):
    f = flow(ch)
    sec(f, "Tool 1: the REPL, with dir() and help()", room=420)
    f.p("Open `python3` and import the module. `dir()` lists every name on an object; filter out the "
        "underscore names and what's left is the {B:public surface}:", 13.5, gap=8)
    repl(f, """
        >>> import hmac
        >>> [n for n in dir(hmac) if not n.startswith("_")]
        >>> type(hmac.new), type(hmac.HMAC)
    """)
    f.p("Now you know: one function (`new`), one class (`HMAC`), one helper (`compare_digest`). The "
        "`trans_` names are internal tables a stricter author would have hidden. `help(name)` shows the "
        "docstring; `__doc__` gives the same text as a string, handy for the first lines:", 13.5, gap=8)
    repl(f, """
        >>> print(hmac.new.__doc__[:200])
    """)
    f.p("The factory makes an object. Make one, and `dir()` **that** too: the object's methods are the next "
        "layer of the shape.", 13.5, gap=8)
    repl(f, """
        >>> h = hmac.new(b"secret key", b"message", "sha256")
        >>> print(*[n for n in dir(h) if not n.startswith("_")])
        >>> h.hexdigest()[:16]
    """)
    table(f, ["in the REPL", "tells you"], [
        ["`dir(x)`", "every attribute name (filter the underscores)"],
        ["`help(x)` / `x.__doc__`", "the docstring: what it does and what it takes"],
        ["`type(x)`, `type(x).__mro__`", "what kind of object, and which classes it inherits from"],
        ["`x.__module__`, `module.__file__`", "where it lives, so you can read the source"],
        ["`callable(x)`, `isinstance(x, type)`", "function or class? (filtering `dir()` output)"],
    ], widths=[2.2, 3.8])


def inspect_tools(ch):
    f = flow(ch)
    sec(f, "Tool 2: inspect, signatures and the source", room=420)
    f.p("`inspect.signature` answers \"what does it take?\" exactly. Learn to read the two markers, because "
        "the docs use them too:", 13.5, gap=8)
    repl(f, """
        >>> import inspect, json
        >>> inspect.signature(sorted)
        >>> inspect.signature(hmac.new)
        >>> inspect.signature(json.dumps)
    """, w=W)
    table(f, ["in a signature", "means", "so you write"], [
        ["`a, b`", "ordinary: by position or by name", "`f(1, 2)` or `f(a=1, b=2)`"],
        ["`x, /`", "everything before `/` is **positional-only**", "`sorted(xs)`, never `sorted(iterable=xs)`"],
        ["`*, key=None`", "everything after `*` is **keyword-only**", "`sorted(xs, key=len)`, not `sorted(xs, len)`"],
        ["`msg=None`", "has a default, so optional", "leave it out, or pass it"],
        ["`*args`, `**kw`", "any extra positional / keyword arguments", "read the docs for what's accepted"],
        ["`[, x]` in docs", "older docs' notation for optional", "same as a default"],
    ], widths=[1.3, 2.6, 2.3])
    f.p("Then read the source. A surprising amount of the standard library is plain Python, and reading it "
        "is the fastest way to see what a function really does:", 13.5, gap=8)
    code(f, """
        import inspect, statistics
        src = inspect.getsource(statistics.median)
        body = src.split('\"\"\"')[2]          # skip the docstring
        print(body.strip())
    """, notes={2: "the real code", 3: "drop the docstring"})
    callout(f, "honest", "Some modules are written in C (`math`, `_sqlite3`, parts of `hashlib`). For those "
            "`inspect.getsource` raises `TypeError`, and `inspect.signature(sqlite3.connect)` even raises "
            "`ValueError` on 3.14. Then fall back to `help()` and the docs page. `module.__file__` tells you "
            "which it is: a `.py` path, or a `.so` (compiled C).")
    repl(f, """
        >>> import math, sqlite3
        >>> math.__file__.rsplit("/", 1)[-1]
        >>> statistics.__file__.rsplit("/", 1)[-1]
    """)


def docs_page(ch):
    f = flow(ch)
    sec(f, "Tool 3: reading a docs page (without reading all of it)", room=430)
    f.p("A page on docs.python.org is a reference, not a story. You don't read it top to bottom. You read it "
        "in this order, and stop as soon as you can write your spike:", 13.5, gap=8)
    tree(f, {
        "p": ("docs.python.org/3/library/<module>.html", 0.5, 0),
        "a": ("1. top paragraph: the Job", 0.17, 1),
        "b": ("2. last section: Examples", 0.5, 1),
        "c": ("3. the main class / factory", 0.83, 1),
        "d": ("4. its methods you need", 0.3, 2),
        "e": ("5. Exceptions section", 0.7, 2),
        "f": ("'Changed in version 3.x'", 0.3, 3),
        "g": ("'Note' / 'Warning' boxes", 0.7, 3),
    }, [("p", "a"), ("p", "b"), ("p", "c"), ("c", "d"), ("c", "e"), ("d", "f"), ("e", "g")], mono=False,
        size=9.5)
    f.p("{b:Skip ahead to the examples.} Most module pages end with a worked example; it shows the "
        "lifecycle in ten lines. {b:Warning boxes} are where the traps live (for `hmac`: compare with "
        "`compare_digest`, not `==`). {b:\"Changed in version\"} lines tell you whether a blog post from 2016 "
        "still applies.", 13.5, gap=8)
    f.p("You can read the same docstrings offline in a terminal, which helps when you're on a train:", 13.5,
        gap=6)
    shell(f, """
        $ python3 -m pydoc hmac            # the module's docs, in a pager
        $ python3 -m pydoc hmac.new        # one function
        $ python3 -m pydoc -k zip          # search every module's summary line
    """)
    callout(f, "rule", "Search in this order: the official docs page, then the source, then the PEP that "
            "introduced the feature (linked from the docs). Only then blogs and Q&A sites, and check the "
            "{B:date}: Python 2 answers still rank highly. AI answers are a fourth opinion: run what they "
            "give you in a spike before you trust it.")


def spike(ch):
    f = flow(ch)
    sec(f, "Tool 4: the 20-line spike", room=430)
    f.p("A {B:spike} is the smallest throwaway program that uses the library end to end. You write it in "
        "a scratch file before touching your real project. Then you {B:break it on purpose}, because seeing "
        "the errors now means you'll recognise them later.", 13.5, gap=8)
    f.p("Here's a spike for `difflib`, a module this book never teaches. Ten minutes with `dir()` and the "
        "docs page found `get_close_matches`:", 13.5, gap=8)
    code(f, """
        import difflib

        commands = ["status", "commit", "checkout", "branch", "merge"]
        for typo in ["comit", "chekout", "brnch", "xyz"]:
            print(typo, "->", difflib.get_close_matches(typo, commands, n=1))

        # break it: what does the cutoff do?
        print(difflib.get_close_matches("xyz", commands, cutoff=0.0))
    """, notes={5: "make it work", 8: "now poke it"})
    f.p("And break it with wrong input, to learn the error before it surprises you:", 13.5, gap=6)
    code(f, """
        difflib.get_close_matches("x", commands, n=0)
    """, raises=ValueError, numbers=False)
    pipe(f, [("1. happy path", C.GREEN), ("2. edge inputs\n(empty, huge, unicode)", C.ORANGE),
             ("3. wrong types /\nbad values", C.RED), ("4. write the card", C.TEAL)], h=44)
    go(f, "Spike the textwrap module: find (with dir and help, no searching) how to wrap a long sentence to "
          "30 characters and how to indent every line by two spaces. Then pass it an empty string.")


def worked(ch):
    f = flow(ch)
    sec(f, "Worked example: cracking hmac from zero", room=440)
    f.p("Pretend you've never seen `hmac`. The project needs to check that a QR code's contents weren't "
        "edited. Five minutes of the method:", 13.5, gap=8)
    table(f, ["step", "what you did", "what you learned"], [
        ["Job", "first line of `hmac.__doc__`, the top paragraph of the docs", "makes a keyed hash: a tag "
         "only someone with the key could produce"],
        ["Shape", "`dir(hmac)`: `new`, `HMAC`, `compare_digest`, `digest`", "object factory, plus a one-shot "
         "function `digest`"],
        ["Signature", "`inspect.signature(hmac.new)`", "`(key, msg=None, digestmod='')`: key and message are "
         "bytes; you must choose a hash"],
        ["Docs warning", "the Warning box on the page", "compare tags with `compare_digest`, never `==`"],
        ["Spike", "the 12 lines below", "it works; wrong key gives a different tag; `str` key is a "
         "`TypeError`"],
    ], widths=[1.0, 2.6, 2.6])
    code(f, """
        import hmac

        KEY = b"server-only secret"
        def tag(msg: bytes) -> str:
            return hmac.new(KEY, msg, "sha256").hexdigest()

        t = tag(b"student=42;room=B12")
        print(t[:20], len(t))
        print(hmac.compare_digest(t, tag(b"student=42;room=B12")))
        print(hmac.compare_digest(t, tag(b"student=43;room=B12")))
        print(hmac.digest(KEY, b"student=42;room=B12", "sha256").hex() == t)
    """, notes={5: "factory + method in one line", 9: "unchanged: True", 10: "edited: False",
                11: "the one-shot form agrees"})
    code(f, """hmac.new("not bytes", b"m", "sha256")""", raises=TypeError, numbers=False)
    f.p("The output of the method is the card. Writing it down is what makes it stick, and it's what you'll "
        "look at in six months instead of the docs:", 13.5, gap=8)
    card(f, "hmac", {
        "Job": "A keyed hash (a {B:tag}): proves a message came from someone with the key and wasn't changed.",
        "Core objects": "`hmac.new(key, msg, digestmod)` → `HMAC` object with `.update(b)`, `.digest()`, "
                        "`.hexdigest()`. One-shot: `hmac.digest(key, msg, 'sha256')`.",
        "Lifecycle": "new → update (any number of times) → digest. Nothing to close.",
        "Errors": "`TypeError` if key/msg are `str` (encode them); unknown digest name → `ValueError`.",
        "Traps": "Compare with `hmac.compare_digest` ({R:== leaks timing}). Not encryption: the message is "
                 "still readable. Keep the key out of the source (Ch 13).",
        "Docs": "docs.python.org/3/library/hmac.html · RFC 2104",
    })


def strategy(ch):
    f = flow(ch)
    sec(f, "When you're stuck: a checklist", room=360)
    for t in ["{B:Which shape is it?} Bag of functions, factory, subclass, or framework. That decides what "
              "to look for first.",
              "{B:What's the core object?} Find the one or two classes everything else hangs off "
              "(`Connection` and `Cursor`, `ZipFile`, `Request` and `Response`).",
              "{B:Bytes or text?} Half of all stdlib confusion. Crypto, sockets and compression want "
              "`bytes`; you `.encode()` on the way in and `.decode()` on the way out (Ch 9).",
              "{B:Who closes it?} Look for `close()`, `__enter__` in `dir()` (it works with `with`), or a "
              "`commit()`.",
              "{B:What does it raise?} Look for names ending in `Error` in `dir(module)`; that's the "
              "Errors row of the card.",
              "{B:Is there a one-shot helper?} Many modules have a simple function for the common case "
              "(`hmac.digest`, `json.loads`, `subprocess.run`, `urllib.request.urlopen`). Start there."]:
        f.bullet(t, 13, gap=6)
    repl(f, """
        >>> print(*[n for n in dir(sqlite3) if n.endswith("Error")])
        >>> "__enter__" in dir(sqlite3.Connection)
    """, w=W)
    callout(f, "other", "The method is language-neutral. In Java the REPL is `jshell` and the docs are "
            "Javadoc; in Rust, `cargo doc --open` and the docs.rs Examples section; in C, `man 3 qsort`. "
            "The questions (shape, core object, lifecycle, errors, traps) don't change.")


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 7)
    stamp(f, [
        (8, "A module is a `.py` file (or compiled C `.so`) found on `sys.path`; `module.__file__` says "
            "which. Packages are folders of modules."),
        (11, "Built-in introspection: `dir`, `help`, `type`, `inspect.signature`, `inspect.getsource`, "
             "`python -m pydoc`. Most of the stdlib is readable Python source."),
    ])
    callout(f, "deep", "Vault notes: {b:11.10} Standard-library method: inspect by contract · {b:10.2} Import "
            "is execution with caching · {b:10.7} Public APIs and `__all__` · {b:8.15} Function attributes "
            "and introspection · {b:15.20} Reading CPython source responsibly.")


def build(ch):
    title_page(ch)
    shapes(ch)
    repl_tools(ch)
    inspect_tools(ch)
    docs_page(ch)
    spike(ch)
    worked(ch)
    strategy(ch)
    finish(ch)
