"""Chapter 1 - Recall sprint: the first-half module (types, strings, numbers, collections, control flow,
functions, classes) as three predict-then-check quizzes with real answers, plus a one-page cheat sheet."""
import textwrap

from generator import canvas as C
from generator import fonts as F
from content.kit import (CODE_BG, CODE_EDGE, L, W, _draw_line, _spans, callout, flow, practice, run_src,
                         section, stamp, table, title_block)

ORDER = 1
NUM = 1
TITLE = "Recall sprint"
SHORT = "Recall sprint"
SLUG = "Recall-sprint"
ACCENT = C.ORANGE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def answer_of(ch, src):
    try:
        out, err = run_src(ch, src, ns={"__name__": "__main__"}, raises=Exception)
    except Exception:  # noqa: BLE001  (run_src insists on an error when raises= is given)
        out, err = run_src(ch, src, ns={"__name__": "__main__"})
    ch.checks += 1
    if err:
        return (out.strip() + "\n" if out.strip() else "") + err.split(":")[0] + "!"
    return out.strip()


def quiz(ch, title, items, size=8.6):
    """Numbered snippets, outputs hidden. Returns the answers for the answer page."""
    f = flow(ch)
    sec(f, title, fresh=True)
    f.p("Write down what each prints (an error counts: write its name). No running anything. Answers on "
        "the next page.", 12.5, gap=8)
    half = (W - 12) / 2
    min_size = 7.6

    def fits(src, width, s):
        return max(len(l) for l in src.split("\n")) * F.width("M", F.MONO, s) + 32 <= width

    srcs = [textwrap.dedent(s).strip() for s, _ in items]
    rows, k = [], 0                       # pair up items that fit in half a page; wide ones get a full row
    while k < len(srcs):
        if k + 1 < len(srcs) and fits(srcs[k], half, min_size) and fits(srcs[k + 1], half, min_size):
            rows.append([k, k + 1])
            k += 2
        else:
            rows.append([k])
            k += 1
    answers = []
    for row in rows:
        colw = half if len(row) == 2 else W
        s = size
        while not all(fits(srcs[j], colw, s) for j in row) and s > min_size:
            s = round(s - 0.2, 2)
        cw = F.width("M", F.MONO, s)
        lh = F.line_h(F.MONO, s) * 1.04
        hs = [len(srcs[j].split("\n")) * lh + 14 for j in row]
        y = f.reserve(max(hs) + 8)
        pg = f.pg
        for pos, j in enumerate(row):
            src = srcs[j]
            x0 = L + pos * (colw + 12)
            pg.rect(x0, y, colw, max(hs), CODE_EDGE, 0.8, fillcolor=CODE_BG, r=5)
            pg.rect(x0, y, 20, max(hs), ACCENT, 0, fillcolor=C.LIGHT[ACCENT], r=5)
            pg.text(x0 + 10, y + 5, str(j + 1), 10, ACCENT, F.BOLD, align="center")
            sp = _spans(src)
            for jj, line in enumerate(src.split("\n")):
                _draw_line(pg, x0 + 27, y + 7 + jj * lh, line, sp[jj], cw, s)
            answers.append((j + 1, answer_of(ch, src), items[j][1]))
    return answers


def answers_page(ch, title, answers, where):
    f = flow(ch)
    sec(f, title, fresh=True)
    rows = [[str(n), "`" + a.replace("\n", "`  `") + "`" if a else "(nothing)", why] for n, a, why in answers]
    table(f, ["#", "prints", "why"], rows, widths=[0.35, 2.3, 3.6], size=10, head_col=ACCENT)
    callout(f, "rule", where, size=11.5)


QUIZ_A = [
    ("print(7 / 2, 7 // 2, -7 // 2, 7 % 3)", "`/` is true division (always float); `//` floors towards minus "
     "infinity, so `-7 // 2` is -4."),
    ("print(0.1 + 0.2 == 0.3)\nprint(round(0.1 + 0.2, 10) == 0.3)", "floats are binary fractions; 0.1 can't be "
     "stored exactly. Compare with a tolerance or `math.isclose`."),
    ("print(round(2.5), round(3.5), round(-0.5))", "`round` uses banker's rounding: ties go to the even "
     "neighbour."),
    ("s = \"python\"\nprint(s[1:4], s[-2:], s[::-1][:3])", "slices are [start:stop) and never fail; negative "
     "indexes count from the end."),
    ("print(\"ab\" * 3, \"-\".join(\"abc\"), \"a,b,,c\".split(\",\"))", "`join` is a string method taking an "
     "iterable; `split` with a separator keeps empty fields."),
    ("print(True + True, int(\"08\"), bool(\"False\"))", "bool is a subclass of int; any non-empty string is "
     "truthy, even \"False\"."),
    ("x = 1_000_000\nprint(f\"{x:,} {x:.2e} {3.14159:.2f} {'hi':>5}|\")", "format spec mini-language: `,` "
     "thousands, `e` scientific, `.2f`, `>5` right-align."),
    ("print(1 < 2 < 3, 3 > 2 > 2, \"a\" < \"B\")", "comparisons chain (`a < b and b < c`); strings compare by "
     "code point, and uppercase letters come first."),
    ("a = [1, 2]\nb = [1, 2]\nprint(a == b, a is b)", "`==` compares values, `is` compares identity "
     "(same object). Use `is` only for `None`."),
    ("print(\"5\" + str(5), int(\"5\") + 5)\nprint(\"5\" + 5)", "Python is strongly typed: no silent "
     "conversion between str and int."),
    ("print(type(3/1).__name__, 2**100 > 10**30, 10**20 + 1.0 == 10**20)", "ints are arbitrary precision; "
     "floats have 53 bits, so adding 1.0 to 1e20 is lost."),
    ("s = \"  Hi There  \"\nprint(s.strip().lower().replace(\" \", \"_\"), len(s))", "string methods return "
     "new strings (str is immutable); they chain."),
]

QUIZ_B = [
    ("a = [3, 1, 2]\nb = a\nb.append(0)\nprint(a)", "`b = a` copies the reference, not the list "
     "(Chapter 3 draws it)."),
    ("a = [3, 1, 2]\nprint(a.sort(), sorted(a, reverse=True))", "`list.sort()` sorts in place and returns "
     "None; `sorted()` returns a new list."),
    ("t = (1)\nu = (1,)\nprint(type(t).__name__, type(u).__name__, len(u))", "the comma makes the tuple, not "
     "the brackets."),
    ("d = {\"b\": 1, \"a\": 2}\nd[\"c\"] = 3\nprint(list(d), d.get(\"z\", 0))", "dicts keep insertion order "
     "(3.7+); `.get` gives a default instead of KeyError."),
    ("d = {\"x\": 1}\nprint(d[\"y\"])", "missing key with `[]` raises KeyError. Use `.get`, `in`, or "
     "`collections.defaultdict`."),
    ("a, b = {1, 2, 3}, {3, 4}\nprint(a | b, a & b, a - b)", "set union, intersection, difference: the maths "
     "notation, as operators."),
    ("print([x * x for x in range(6) if x % 2])", "comprehension: expression, loop, optional filter."),
    ("first, *rest = \"hello\"\nprint(first, rest)", "star-unpacking collects the leftovers into a list."),
    ("for i, c in enumerate(\"ab\", start=1):\n    print(i, c, end=\"; \")", "enumerate gives (index, item) "
     "pairs; `end=` replaces the newline."),
    ("print(list(zip([1, 2, 3], \"ab\")))", "zip stops at the shortest input (`strict=True` makes it raise)."),
    ("nums = [0, 1, 2, 3, 4, 5]\ndel nums[1::2]\nprint(nums, nums[10:])", "slices can be deleted or assigned; "
     "slicing past the end gives an empty list, not an error."),
    ("grid = [[0] * 2] * 2\ngrid[0][0] = 9\nprint(grid)", "`* 2` repeats the {R:same} inner list twice. Use "
     "`[[0] * 2 for _ in range(2)]`."),
]

QUIZ_C = [
    ("for n in [3, 5, 7]:\n    if n % 2 == 0:\n        break\nelse:\n    print(\"no evens\")", "a loop's `else` "
     "runs only if the loop finished without `break`."),
    ("i = 0\nwhile True:\n    i += 3\n    if i > 10:\n        break\nprint(i)", "the loop runs until the first "
     "value over 10: 3, 6, 9, 12."),
    ("def f(cmd):\n    match cmd.split():\n        case [\"go\", d]: return f\"go {d}\"\n"
     "        case [\"quit\"]: return \"bye\"\n        case _: return \"?\"\nprint(f(\"go north\"), f(\"jump\"))",
     "structural pattern matching matches shapes and binds names (3.10+)."),
    ("def add(x, items=[]):\n    items.append(x)\n    return items\nadd(1)\nprint(add(2))", "defaults are "
     "evaluated {R:once}, when `def` runs; the same list is reused. Use `items=None`."),
    ("def f(a, b=2, *args, c, **kw):\n    return a, b, args, c, kw\nprint(f(1, 5, 6, c=7, d=8))", "positional, "
     "default, extra positionals, keyword-only, extra keywords."),
    ("x = 10\ndef f():\n    print(x)\n    x = 5\nf()", "assigning `x` anywhere in a function makes it local "
     "everywhere in that function: UnboundLocalError (Chapter 4)."),
    ("def f():\n    pass\nprint(f(), (lambda: 1)())", "a function without `return` returns None."),
    ("words = [\"bb\", \"a\", \"ccc\"]\nprint(sorted(words, key=len), max(words, key=len))", "`key=` is called "
     "on each item; the items themselves are returned."),
    ("class Dog:\n    tricks = []\n    def __init__(self, n): self.n = n\na, b = Dog(1), Dog(2)\n"
     "a.tricks.append(\"sit\")\nprint(b.tricks)", "a class attribute is shared by every instance. Put "
     "per-object lists in `__init__`."),
    ("class P:\n    def __init__(self, x): self.x = x\n    def __repr__(self): return f\"P({self.x})\"\n"
     "print([P(1), P(2)])", "containers show items with `repr`; define `__repr__` for debugging output."),
    ("class A:\n    def hi(self): return \"A\"\nclass B(A):\n    def hi(self): return \"B+\" + super().hi()\n"
     "print(B().hi(), isinstance(B(), A))", "`super()` calls the parent's version; a B is an A."),
    ("try:\n    print(int(\"x\"))\nexcept ValueError as e:\n    print(\"bad:\", e)\nfinally:\n    print(\"done\")",
     "`finally` always runs, error or not (Chapter 6)."),
]


def title_page(ch):
    title_block(ch, 1, TITLE, "find your gaps in an hour, not a semester", ACCENT)
    f = ch.flow(top=190)
    f.p("This chapter is the first half of your Computing module (types, strings, numbers, collections, "
        "control flow, functions, classes) squeezed into three quizzes. You know most of it. The point is "
        "to find the {B:few things you only think you know}, because those are what make later chapters "
        "confusing.", 14, gap=10)
    f.p("How to use it:", 14, gap=6)
    for t in ["Do a quiz page with a pencil, no REPL. Writing the answer down matters: \"I'd have got that\" "
              "doesn't count.",
              "Turn the page, mark yourself, and read the {b:why} only for the ones you missed.",
              "Every miss points to the chapter that explains it properly. Note those chapters; they're your "
              "personal reading list.",
              "Then do the practice exercises: small programs that use all of it together."]:
        f.bullet(t, 13.5, gap=6)
    f.gap(4)
    table(f, ["quiz", "covers", "lecture"], [
        ["A", "numbers, strings, booleans, comparison, formatting", "1, 2"],
        ["B", "lists, tuples, dicts, sets, comprehensions, unpacking", "3, 5"],
        ["C", "loops, match, functions, scope, classes, exceptions", "4, 6, 7"],
    ], widths=[0.6, 4, 1])
    callout(f, "idea", "Every answer on the answer pages was produced by running the snippet while building "
            "the book, so the answers are exactly what Python 3.14 prints.")


def cheat_sheet(ch):
    f = flow(ch)
    sec(f, "The first half of the module, on one page", fresh=True)
    table(f, ["type", "make one", "most-used operations", "cost to know"], [
        ["`str`", "`'hi'`, `f'{x}'`, `str(x)`", "`s[i]`, `s[a:b]`, `split`, `join`, `strip`, `replace`, "
         "`find`, `startswith`, `upper`", "immutable; `+=` in a loop is O(n²), use `join`"],
        ["`list`", "`[1, 2]`, `list(it)`, `[x for x in it]`", "`append`, `extend`, `pop()`, `insert`, "
         "`remove`, `sort`, `index`, slicing", "`append`/`pop()` O(1); `insert(0)`/`pop(0)`/`in` O(n)"],
        ["`tuple`", "`(1, 2)`, `1,`, `tuple(it)`", "indexing, unpacking `a, b = t`", "immutable, hashable "
         "(dict key) if its items are"],
        ["`dict`", "`{'k': v}`, `dict(zip(ks, vs))`, `{k: v for ...}`", "`d[k]`, `get`, `items`, `keys`, "
         "`values`, `setdefault`, `pop`, `|`", "lookup/insert O(1) average; keys must be hashable"],
        ["`set`", "`{1, 2}`, `set()`, `{x for ...}`", "`add`, `discard`, `|`, `&`, `-`, `^`, `in`",
         "`in` is O(1); `{}` is an empty {R:dict}"],
    ], widths=[0.7, 1.9, 2.6, 2.0], size=9.5, head_col=ACCENT)
    table(f, ["control flow", "shape"], [
        ["`if` / `elif` / `else`", "conditional expression: `a if cond else b`"],
        ["`for x in iterable:`", "`range(a, b, step)`, `enumerate`, `zip`, `reversed`, `sorted`; `break`, "
         "`continue`, loop `else`"],
        ["`while cond:`", "for loops with no fixed count; watch the exit condition"],
        ["`match value:`", "`case 0:`, `case [x, y]:`, `case {\"k\": v}:`, `case Point(x=0):`, `case _:`"],
        ["`try` / `except E as e` / `else` / `finally`", "catch the narrowest error; `finally` for clean-up"],
    ], widths=[2.2, 4], size=9.5, head_col=ACCENT)
    table(f, ["functions and classes", "remember"], [
        ["`def f(a, b=1, *args, c, **kw)`", "defaults evaluated once; `*` makes keyword-only; return None by "
         "default"],
        ["`lambda x: x + 1`", "one expression; mostly for `key=` arguments"],
        ["`class C(Base):`  `def __init__(self, ...)`", "`self.x` per object; class attributes shared; "
         "`super().__init__(...)`"],
        ["`__repr__`, `__str__`, `__eq__`, `__len__`", "dunder methods hook into built-ins (Chapter 5)"],
        ["`import m`, `from m import f`, `import m as x`", "`if __name__ == \"__main__\":` for script code"],
    ], widths=[2.4, 3.8], size=9.5, head_col=ACCENT)


def finish(ch):
    f = flow(ch)
    sec(f, "Scoring, and what to read next", room=380)
    table(f, ["missed", "you're probably fuzzy on", "read"], [
        ["A1–A3, A11", "how numbers are stored", "Ch 11 (floats, Decimal, Fraction)"],
        ["A9, B1, B12", "names vs objects (aliasing)", "Ch 3: the most important chapter after this"],
        ["B4, B5", "dict behaviour", "Ch 5, Ch 10 (`collections`)"],
        ["C4, C6, C9", "when things are evaluated and where names live", "Ch 4 (functions, scope)"],
        ["C10, C11", "the data model (dunder methods)", "Ch 5"],
        ["C12", "exceptions", "Ch 6"],
    ], widths=[1.2, 2.6, 2.4], head_col=ACCENT)
    f.p("30 or more out of 36: skim Part I and spend your time from Chapter 7 onwards. Under 25: read "
        "Chapters 2–6 properly; they're the foundation everything else stands on.", 13.5, gap=10)
    practice(f, 1)
    stamp(f, [
        (3, "`if`/`elif`/`else`, `for` over any iterable, `while`, `match` (3.10+), loop `else`, "
            "`break`/`continue`. Blocks are defined by indentation."),
        (5, "Built in: `list`, `tuple`, `dict` (ordered), `set`, `str`, `bytes`; comprehensions for all of "
            "them."),
        (2, "Dynamic, strong typing: `\"5\" + 5` is a TypeError; bool is a subclass of int."),
    ])
    callout(f, "deep", "Vault notes: {b:5.9} Numeric objects · {b:5.11} Strings, Unicode, and textual value · "
            "{b:5.14} Truth values · {b:7.3} Lists as mutable sequences · {b:7.6} Dictionaries as mappings · "
            "{b:8.5} Defaults are evaluated at definition time · {b:91} Practice Questions.")


def build(ch):
    title_page(ch)
    a = quiz(ch, "Quiz A: values, strings, numbers", QUIZ_A)
    answers_page(ch, "Answers A", a, "Missed 2, 3 or 11? Chapter 11 on numbers. Missed 9? Chapter 3. "
                 "Everything else: re-read the why, then make up a variation and test it in the REPL.")
    b = quiz(ch, "Quiz B: collections", QUIZ_B)
    answers_page(ch, "Answers B", b, "Missed 1 or 12? Chapter 3 is for you: both are the same idea (two "
                 "names, one object). Missed 4 or 5? Chapter 10's `collections` makes dicts easier.")
    c = quiz(ch, "Quiz C: control flow, functions, classes", QUIZ_C)
    answers_page(ch, "Answers C", c, "Missed 4 or 6? Chapter 4 explains both with one picture. Missed 9, "
                 "10 or 11? Chapter 5 (the data model).")
    cheat_sheet(ch)
    finish(ch)
