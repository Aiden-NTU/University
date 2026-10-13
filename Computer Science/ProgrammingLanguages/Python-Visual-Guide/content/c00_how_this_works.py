"""Chapter 0 - How this course works: the learning loop, how to read the pages, the practice repo,
the library card and the language passport."""
from generator import canvas as C
from content.kit import (L, W, callout, card, code, flow, go, passport, pipe, practice, repl, section,
                         shell, table, title_block, two_ways)

ORDER = 0
NUM = 0
TITLE = "How this course works"
SHORT = "How this works"
SLUG = "How-this-works"
ACCENT = C.TEAL


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def title_page(ch):
    pg = title_block(ch, 0, TITLE, "practice teaches; the book shows you what to practise", ACCENT)
    f = ch.flow(top=190)
    f.p("You can already write Python: loops, functions, classes, a few sorting algorithms. The wall you hit "
        "is the next layer: a module you've never seen (`sqlite3`, `hmac`, `asyncio`), documentation that "
        "assumes you already know it, and programs big enough to need structure. This course is about that "
        "layer.", 14, gap=10)
    f.p("Text alone doesn't teach programming, any more than reading about press-ups builds muscle. So every "
        "page here is a {B:map of what to practise}, and the practice lives in a companion folder of "
        "exercises that check themselves. The book is short on purpose. The hours go into the exercises "
        "and into your own projects.", 14, gap=10)
    f.p("Three ideas run through everything:", 14, gap=6)
    for t in ["{B:The loop.} See it, predict it, build it, compare solutions, drill it.",
              "{B:The library card.} Six questions that crack open any library, in any language.",
              "{B:The language passport.} Twelve questions every language answers. Python fills them in "
              "now; C, Java and Rust fill in the same page later, so each new language is a diff, not a "
              "restart."]:
        f.bullet(t, 14, gap=6)
    f.gap(6)
    f.p("{y:The first half of your Computing module (types, strings, lists, control flow, dictionaries, "
        "functions, classes) is squeezed into Chapter 1 as a fast recall sprint. NumPy gets a full chapter "
        "(18), because that's where the module gets interesting.}", 12.5)


def loop(ch):
    f = flow(ch)
    sec(f, "The loop: five steps, every topic")
    pipe(f, [("See", C.BLUE), ("Predict", C.ORANGE), ("Build", C.GREEN), ("Compare", C.PURPLE),
             ("Drill", C.RED)], labels=["", "", "", ""],
         under=["a picture of what happens in memory", "commit to an answer before running",
                "write it; tests check behaviour", "2-3 valid solutions, trade-offs", "spaced repetition, 10 min a day"])
    f.p("{b:See.} Every idea gets a picture: names pointing at objects, a resource opened and closed, bytes "
        "flowing through a pipeline, two threads on a timeline. The same pictures come back in every chapter, "
        "and later in every language.", 13.5, gap=8)
    f.p("{b:Predict.} Before running a snippet, write down what you think it prints. Being wrong is the "
        "useful part: it shows exactly where your mental model is off.", 13.5, gap=8)
    f.p("{b:Build.} The practice folder gives a task, an empty `solution.py` and a set of tests. The tests "
        "check what your code {B:does} (its contract), never how it looks, so any correct solution passes.",
        13.5, gap=8)
    f.p("{b:Compare.} After you pass, you're shown two or three other solutions that also pass, with notes on "
        "speed, memory and readability. There's rarely one best answer; there's a best answer {B:for a "
        "situation}.", 13.5, gap=8)
    f.p("{b:Drill.} Ten minutes of quick questions a day (\"what does this print?\", \"which module does X?\"). "
        "Questions you get right come back less often; questions you miss come back tomorrow.", 13.5, gap=8)


def reading(ch):
    f = flow(ch)
    sec(f, "How to read a page", room=420)
    f.p("{b:Code boxes.} Grey boxes are code, with line numbers. Red handwriting points at the lines that "
        "matter. The dark box underneath is the {B:real output}: the book is built by running every snippet, "
        "so if a snippet printed something different, the book wouldn't build.", 13.5, gap=8)
    code(f, """
        prices = {"tea": 1.20, "cake": 2.50}
        order = ["tea", "cake", "tea"]
        total = sum(prices[item] for item in order)
        print(f"{len(order)} items, £{total:.2f}")
    """, notes={3: "look each item up, add them", 4: ":.2f means 2 decimal places"},
         expect="3 items, £4.90")
    f.p("{b:REPL boxes} show an interactive session. Type the part after `>>>` yourself; Python echoes "
        "the value back. The REPL is your main tool for learning a library: poke it and see.", 13.5, gap=8)
    repl(f, """
        >>> word = "practice"
        >>> word.upper()
        >>> len(word), word[::-1]
    """)
    f.p("{b:Terminal boxes} are commands typed in a shell (not run by the book):", 13.5, gap=6)
    shell(f, """
        $ cd Python-Visual-Guide
        $ python -m practice next
    """)
    callout(f, "idea", "Callout boxes like this one hold the one sentence to remember from a page. Red "
            "{R:TRAP} boxes mark the mistakes almost everyone makes once.")
    go(f, "Before reading on: what does `print(sorted('banana'))` print? Write it down, then try it.")


def tests_idea(ch):
    f = flow(ch)
    sec(f, "Many right answers: tests check behaviour", room=420)
    f.p("Maths questions have one answer. Code usually has many: two sorting functions can look nothing alike "
        "and both be correct. So the practice tests never compare your code to mine. They check the "
        "{B:contract}: for a sort, \"the output has the same items as the input, in order\". They check it "
        "on hundreds of random inputs, including the awkward ones (empty, one item, all the same).", 13.5,
        gap=8)
    code(f, """
        import random

        def is_sorted_version(out, original):
            same_items = sorted(out) == sorted(original)
            in_order = all(a <= b for a, b in zip(out, out[1:]))
            return same_items and in_order

        def my_sort(xs):              # any correct sort would do
            xs = list(xs)
            for i in range(1, len(xs)):
                j = i
                while j and xs[j - 1] > xs[j]:
                    xs[j - 1], xs[j] = xs[j], xs[j - 1]
                    j -= 1
            return xs

        rng = random.Random(0)
        cases = [[], [7], [3, 3, 3]]
        for _ in range(500):
            n = rng.randint(0, 12)
            cases.append([rng.randint(-9, 9) for _ in range(n)])
        ok = all(is_sorted_version(my_sort(c), c) for c in cases)
        print(ok, len(cases), "cases")
    """, hl=(3, 4), notes={3: "same items...", 4: "...and in order", 18: "the awkward cases first"},
         expect="True 503 cases")
    f.p("After you pass, the {b:compare} step shows other solutions side by side. Both of these pass the same "
        "tests; the bars are the trade-offs, not a ranking:", 13.5, gap=8)
    two_ways(f, ("Insertion sort, by hand", """
        def sort_copy(xs):
            xs = list(xs)
            for i in range(1, len(xs)):
                j = i
                while j and xs[j-1] > xs[j]:
                    xs[j-1], xs[j] = xs[j], xs[j-1]
                    j -= 1
            return xs

        print(sort_copy([5, 2, 9, 1]))
    """), ("Use the built-in", """
        def sort_copy(xs):
            return sorted(xs)



        print(sort_copy([5, 2, 9, 1]))
    """), verdict=[("speed on big lists", 1, 5), ("teaches how sorting works", 5, 1),
                   ("short and obviously right", 2, 5)])
    callout(f, "rule", "Write it by hand to {B:learn} it; use the library to {B:ship} it. The exercises "
            "will often ask for both.")


def card_idea(ch):
    f = flow(ch)
    sec(f, "The library card: how to crack open any library", room=480)
    f.p("Getting stuck on `sqlite3` or `hmac` is rarely about syntax. It's about not knowing the {B:shape} of "
        "the library: which objects you create, which methods you call, what you must close, and what goes "
        "wrong. Every library, in every language, answers the same six questions. Chapter 7 teaches how to "
        "find the answers yourself; every later chapter fills in cards like this one:", 13.5, gap=10)
    card(f, "json", {
        "Job": "Turn Python dicts/lists/str/numbers into JSON text and back.",
        "Core objects": "No objects to create: four functions. `dumps`/`loads` work on strings, `dump`/`load` "
                        "on open files.",
        "Lifecycle": "data → `json.dumps(data)` → text → `json.loads(text)` → data.",
        "Errors": "`json.JSONDecodeError` for bad text; `TypeError` for things JSON can't hold (sets, dates).",
        "Traps": "Tuples come back as lists; dict keys always come back as strings.",
        "Docs": "docs.python.org/3/library/json.html, or `help(json)` in the REPL.",
    })
    code(f, """
        import json
        data = {"id": 7, "tags": ("new", "hot"), 3: "three"}
        text = json.dumps(data)
        print(text)
        print(json.loads(text))
    """, notes={2: "a tuple and an int key", 5: "the traps, live"})


def passport_idea(ch):
    f = flow(ch)
    sec(f, "The language passport", room=520)
    f.p("When you learn C, Java or Rust later, you won't start again. You'll answer the same twelve "
        "questions. Here is Python's passport in one page; each chapter ends with a small {B:stamp} filling "
        "in the questions it covered, and Appendix B collects them.", 13.5, gap=10)
    passport(f, [
        "Source is compiled to bytecode, then run by the CPython virtual machine (Ch 2).",
        "Names point at objects on a heap; nothing is copied unless you ask (Ch 3).",
        "Dynamic and strong: values have types, names don't; `'1' + 1` is an error. Optional hints (Ch 5, 17).",
        "`if`/`elif`, `for` over iterables, `while`, `match`; exceptions as non-local exits (Ch 1, 6).",
        "First-class functions, closures, LEGB scope, decorators, generators (Ch 4).",
        "list, tuple, dict, set built in; heapq, deque, bisect in the stdlib; know the costs (Ch 10, 20).",
        "Classes with duck typing and protocols (dunder methods); dataclasses, ABCs (Ch 5).",
        "Exceptions with `try`/`except`/`finally`; context managers for clean-up (Ch 6).",
        "Modules and packages, `import`, venv + pip, `pyproject.toml` (Ch 2, 17, 19).",
        "File objects, `pathlib`, text vs bytes with explicit encodings (Ch 8).",
        "threads (GIL), processes, `asyncio`; free-threaded builds from 3.13 (Ch 16).",
        "Huge stdlib (\"batteries included\"); `unittest`, `pdb`, `cProfile` built in (Appendix A).",
    ], highlight=())


def routine(ch):
    f = flow(ch)
    sec(f, "Using the practice folder", room=420)
    f.p("The practice folder needs nothing but Python itself: no pip installs. From the course folder:", 13.5,
        gap=6)
    shell(f, """
        $ python -m practice list          # every exercise, and which you've passed
        $ python -m practice next          # set up the next one and show the task
        $ python -m practice check 12.3    # run the tests on your solution.py
        $ python -m practice alt 12.3      # after a pass: other solutions + trade-offs
        $ python -m practice drill         # today's spaced-repetition questions
    """)
    f.p("Each exercise has a kind, so you know what's being asked:", 13.5, gap=6)
    table(f, ["kind", "what you do"], [
        ["build from a spec", "write it from nothing; the task says what it must do"],
        ["fill the stub", "the outline is there; fill in the missing parts"],
        ["fix the bug", "the code runs but is wrong; find and fix it"],
        ["refactor", "make it cleaner or faster without breaking the tests (sometimes with a rule, like \"no loops\")"],
        ["learn an unseen module", "use a module the book hasn't taught, with the library card method"],
        ["measure and explain", "time two versions with `timeit` and explain the difference"],
        ["mini-project", "a small real program that uses the whole chapter"],
    ], widths=[1.3, 3.7])
    f.p("{b:A realistic day:} 10 minutes of drill, 45 minutes of exercises, then the rest on your own project "
        "(your mini-uni infrastructure is perfect for this). The exercises give you the moves; the project is "
        "where they become habits.", 13.5, gap=10)
    practice(f, 0)


def course_map(ch):
    f = flow(ch)
    sec(f, "The map", room=500)
    table(f, ["part", "chapters", "what it unlocks"], [
        ["0  Recall", "1 the module in one sprint", "find your gaps fast"],
        ["I  Mental model", "2 how Python runs · 3 names and memory · 4 functions · 5 the data model · 6 errors",
         "stop being surprised by Python"],
        ["II  The unlock", "7 how to learn any library", "never stuck on a new module again"],
        ["III  Stdlib by job", "8 files · 9 text · 10 algorithm toolkit · 11 numbers and time · 12 sqlite3 · "
         "13 security · 14 OS and CLI · 15 networking · 16 concurrency · 17 quality",
         "write most programs with no pip at all"],
        ["IV  Beyond", "18 NumPy · 19 choosing pip packages", "the outside world, safely"],
        ["V  Core CS", "20 complexity and linked structures · 21 graphs and dynamic programming",
         "the BSc algorithms module"],
        ["Appendices", "A stdlib atlas · B passport · C glossary", "look things up"],
    ], widths=[1.2, 3.2, 1.6])
    callout(f, "deep", "Your existing notes (the \"Python and Computing Basics\" vault) go far deeper on every "
            "topic. Each chapter points to the matching vault notes; read them when a page leaves you "
            "wanting the full story.")


def build(ch):
    title_page(ch)
    loop(ch)
    reading(ch)
    tests_idea(ch)
    card_idea(ch)
    passport_idea(ch)
    routine(ch)
    course_map(ch)
