"""Appendix B - the language passport: Python's full passport, a map of which chapter stamped which question
(read from the chapters' stamp() calls), the same twelve questions for C, Java and Rust, and a ten-minute
probe for answering each question in any new language."""
import ast
import glob
import os
import sys

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, PASSPORT_Q, callout, flow, passport, section, table, title_block

ORDER = 23
NUM = "B"
TITLE = "The language passport"
SHORT = "Passport"
SLUG = "Passport"
ACCENT = C.TEAL


def stamps():
    """{chapter number: set of question indexes} from every chapter's stamp(f, [(qi, text), ...]) call."""
    here = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for path in sorted(glob.glob(os.path.join(here, "c[0-2][0-9]_*.py"))):
        num = int(os.path.basename(path)[1:3])
        if num >= 22:
            continue
        for node in ast.walk(ast.parse(open(path, encoding="utf-8").read())):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "stamp":
                out.setdefault(num, set()).update(e.elts[0].value for e in node.args[1].elts)
    return out


def coverage(f, got):
    chs = list(range(1, 22))
    lab_w, cw, rh = 150, (W - 150) / len(chs), 19
    y = f.reserve(24 + rh * 12 + 8)
    pg = f.pg
    for k, n in enumerate(chs):
        pg.text(L + lab_w + k * cw + cw / 2, y, str(n), 8.5, C.GREY, F.BOLD, align="center")
    for qi, q in enumerate(PASSPORT_Q):
        yy = y + 18 + qi * rh
        if qi % 2 == 0:
            pg.rect(L, yy - 2, W, rh, "#f2f8f8", 0, fillcolor="#f2f8f8")
        hits = [n for n in chs if qi in got.get(n, ())]
        pg.text(L + 4, yy + 2, f"{qi + 1}. {q}", 9.5, ACCENT if hits else C.RED, F.BOLD)
        for k, n in enumerate(chs):
            cx = L + lab_w + k * cw + cw / 2
            if n in hits:
                pg.circle(cx, yy + rh / 2 - 2, 5, ACCENT, 0.8, fillcolor=ACCENT)
            else:
                pg.circle(cx, yy + rh / 2 - 2, 1.2, "#c9d3d3", 0.6, fillcolor="#c9d3d3")
    return {qi: [n for n in chs if qi in got.get(n, ())] for qi in range(12)}


ANSWERS = [
    "CPython compiles each module to bytecode (cached in `__pycache__`) and a stack VM runs it. Syntax errors "
    "at compile time, the rest at run time. To the OS: a process with argv, environment, three streams and an "
    "exit code (Ch 2, 14).",
    "Every value is a heap object; names, list slots and attributes hold references, and assignment never "
    "copies. Reference counting plus a cycle collector free memory. NumPy: one typed buffer, views share it "
    "(Ch 3, 18, 20).",
    "Dynamic and strong: values have types, names don't; `'5' + 5` is a TypeError. Mutable vs immutable; only "
    "hashable objects are dict keys. Hints are checked by mypy or pyright, never by Python (Ch 3, 11, 17).",
    "Indentation makes blocks. `if`/`elif`, `for` over any iterable, `while`, `match`, loop `else`. Generators "
    "pause at `yield`; exceptions are non-local exits (Ch 1, 4, 6).",
    "First-class functions made when `def` runs; positional-only, keyword-only, `*args`, `**kwargs`; defaults "
    "evaluated once. LEGB scope, closures, decorators. No tail calls; recursion limit 1000 (Ch 4, 20).",
    "`list`, `tuple`, `dict` (ordered), `set`, `str`, `bytes` built in; `deque`, `Counter`, `heapq`, `bisect` "
    "in the stdlib. List end O(1), front O(n); dict and set O(1) on average (Ch 10, 20, 21).",
    "Classes with multiple inheritance (C3 MRO, `super()`); duck typing through dunder protocols; ABCs and "
    "`typing.Protocol` for explicit interfaces; dataclasses, properties, enums (Ch 5).",
    "Exceptions unwind to the first matching `except`; `else`, `finally`, `raise ... from`, `ExceptionGroup`. "
    "EAFP style; `with` guarantees clean-up; library errors form class trees (Ch 6, 12).",
    "A module runs once, on first import, and is cached in `sys.modules`; found via `sys.path`. Packages are "
    "folders. A `venv` per project; pip installs wheels; `pyproject.toml` plus a lock file (Ch 2, 17, 19).",
    "Files are bytes; text is decoded with an explicit encoding. `open` in a `with`, `pathlib`, many formats in "
    "the stdlib, `sqlite3` for structured data; sockets speak bytes (Ch 8, 12, 15).",
    "Threads share memory (locks, queues), but the GIL blocks CPU parallelism on the default build: processes "
    "for CPU work, `asyncio` for many waits in one thread. Free-threaded builds since 3.13 (Ch 16).",
    "Batteries included: {n} public modules (Appendix A). `unittest`, `doctest`, `pdb`, `timeit`, `cProfile` "
    "built in; pip, mypy and Git outside (Ch 7, 17, 19).",
]

FOUR = [
    ("bytecode on the CPython VM", "compiled ahead of time to machine code, then linked",
     "compiled to JVM bytecode, JIT-compiled while running", "compiled ahead of time to machine code by rustc"),
    ("all values are heap objects; refcount + cycle GC", "you manage it: stack values, `malloc`/`free`, pointers",
     "primitives by value, objects by reference; tracing GC", "ownership and borrowing, checked at compile time; no GC"),
    ("dynamic, strong; optional hints", "static, weak (implicit conversions, casts)",
     "static, strong, nominal; generics by erasure", "static, strong, inferred; traits; no implicit conversions"),
    ("indentation; `for` over iterables; `match`", "braces; counting `for` loops; `switch`; `goto`",
     "braces; enhanced `for`; `switch` expressions", "everything is an expression; exhaustive `match`"),
    ("first-class, closures, LEGB, `*args`", "function pointers, no closures; pass by value",
     "methods in classes; lambdas capture effectively-final", "functions and closures (`Fn`, `FnMut`, `FnOnce`); move or borrow"),
    ("`list`, `dict`, `set` built in; `deque`, `heapq`", "arrays and structs; build the rest yourself",
     "Collections: `ArrayList`, `HashMap`, `TreeMap`, `ArrayDeque`", "`Vec`, `HashMap`, `BTreeMap`, `VecDeque`, `BinaryHeap`"),
    ("classes, multiple inheritance, duck typing", "structs + function pointers; headers as interfaces",
     "classes, single inheritance, interfaces", "structs and enums + traits; no inheritance"),
    ("exceptions; `with` for clean-up", "return codes and `errno`",
     "exceptions (checked and unchecked); try-with-resources", "`Result<T, E>`, `Option`, the `?` operator; panic for bugs"),
    ("`import`, venv + pip, `pyproject.toml`", "`#include`, separate compilation, make/CMake",
     "packages and JARs; Maven or Gradle", "crates and modules; Cargo and crates.io"),
    ("`open()` file objects; text vs bytes", "`FILE*` from stdio, or POSIX `read`/`write`",
     "`java.io` streams; `Files` and `Path` (java.nio)", "`std::fs`, `Read`/`Write` traits returning `Result`"),
    ("threads (GIL), processes, `asyncio`", "pthreads, `fork`, C11 atomics",
     "threads, executors and concurrent collections, virtual threads", "threads with `Send`/`Sync` checked by the compiler; async runtimes"),
    ("huge stdlib; pip, unittest, pdb", "small libc; gdb, valgrind, sanitizers",
     "large JDK; jshell, JUnit, Flight Recorder", "lean std; cargo test, fmt, clippy, doc"),
]

PROBES = [
    "Write hello world and run it. Which files appear? Add a type error: is it reported before running or "
    "only when that line runs?",
    "Make two names for one list, change it through one, print the other. Then pass it to a function that "
    "changes it.",
    "Try `\"5\" + 5`, `5 / 2` and storing text in a number variable. Which fail, and when?",
    "Loop over a list, a map and a string. Is there a `match`/`switch`, and must it cover every case?",
    "Return a function that counts its calls (a closure). Can it change the captured variable?",
    "Find the growable array, hash map, set, deque and heap. Look up the cost of inserting at the front.",
    "Define a Shape with `area()` and two implementations; call `area()` on a list holding both.",
    "Open a missing file. Exception, error value, or crash? How is clean-up guaranteed?",
    "Split a program into two files, import one from the other, and add one third-party package.",
    "Copy a UTF-8 file line by line and read stdin. What is the default encoding?",
    "Add 1 to a shared counter from 4 threads, 100,000 times each. Is the total right?",
    "Write and run one unit test, step through it in the debugger, and time a loop.",
]


def build(ch):
    n_public = sum(1 for n in sys.stdlib_module_names if not n.startswith("_") or n == "__future__")
    title_block(ch, NUM, TITLE, "the same twelve questions, for every language you learn", ACCENT)
    f = ch._flow = ch.flow(top=190)
    f.p("Each chapter ended with a stamp: Python's answer to the passport questions it covered. Here they are "
        "collected, first as a map of {B:where each answer was built}, then as one page. The last pages ask the "
        "same questions of C, Java and Rust, and give a ten-minute experiment for answering each one in any "
        "language.", 12.5, gap=10)
    got = coverage(f, stamps())
    thin = [PASSPORT_Q[qi] for qi, chs in got.items() if len(chs) < 2]
    assert len(got) == 12 and all(got.values()), "every passport question must be stamped by some chapter"
    f.p(f"Each dot is a chapter whose stamp answered that question. Data structures (question 6) and the "
        f"stdlib (12) are stamped most because almost every chapter adds to them; "
        f"{' and '.join(t.lower() for t in thin)} {'are' if len(thin) > 1 else 'is'} answered in one "
        f"place, so {'they are' if len(thin) > 1 else 'it is'} worth rereading before an exam." if thin else
        "Each dot is a chapter whose stamp answered that question.", 11.5, C.GREY, gap=10)
    callout(f, "idea", "The passport is a reading guide, not a summary. When a new language's tutorial says "
            "something, ask which of the twelve questions it answers. The parts it skips are where your "
            "Python habits will mislead you.", size=12)

    f = flow(ch)
    section(f, "Python's passport", ACCENT, room=700, fresh=True)
    passport(f, [a.replace("{n}", str(n_public)) for a in ANSWERS], size=9.4)

    section(f, "Four passports side by side", ACCENT, room=700, fresh=True)
    f.p("The same questions for the languages a CS degree usually meets next. One line each is a simplification; "
        "it tells you where to look, not everything you'll find.", 11.5, gap=8)
    table(f, ["", "Python", "C", "Java", "Rust"],
          [[f"**{i + 1}. {PASSPORT_Q[i]}**", *row] for i, row in enumerate(FOUR)],
          widths=[1.25, 1.5, 1.5, 1.5, 1.6], size=8.4, head_col=ACCENT)

    section(f, "Ten-minute probes", ACCENT, room=420)
    f.p("Run these in any new language, in order. Each one forces an answer to one passport question, and the "
        "surprises are what to write in that language's passport.", 11.5, gap=8)
    table(f, ["question", "the experiment"],
          [[f"**{i + 1}. {PASSPORT_Q[i]}**", p] for i, p in enumerate(PROBES)],
          widths=[1.3, 4.2], size=9.2, head_col=ACCENT)
    callout(f, "rule", "Pair the passport with the library card (Ch 7) for every library and the spike for every "
            "unknown: twelve questions for the language, six for each library, twenty lines of code for "
            "anything you're unsure of.", size=11.5)
