"""Chapter 7 - Elementary logic. Light switches wired in a row and side by side, the landing
light, colour-coded truth tables, a parent's promise, and Python's `if`."""
from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, go, section, step, title_block

ORDER = 7
NUM = 7
TITLE = "Elementary logic"
SHORT = "Logic"
SLUG = "Logic"
ACCENT = C.ORANGE
REQUIRES = ["set", "union", "intersection", "complement", "inequality-symbols", "venn-diagram"]
INTRODUCES = ["statement", "truth-value", "logical-not", "logical-and", "logical-or", "xor", "truth-table",
              "implication", "converse", "contrapositive", "iff", "de-morgan", "quantifiers"]

PAPER = "#f8fafc"
WIRE = "#37474f"
TRUE_BG = "#d7f0dc"
FALSE_BG = "#fadada"
GLOW = "#ffe066"


def icon(pg, x, y):
    pg.circle(x + 9, y + 8, 6, WIRE, 1.4, fillcolor=GLOW)
    pg.line(x + 6, y + 14, x + 12, y + 14, WIRE, 1.4)
    pg.line(x + 7, y + 17, x + 11, y + 17, WIRE, 1.4)


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def TF(v):
    return "T" if v else "F"


def table(pg, x, y, headers, rows, colw=60, rowh=22, hl=None, size=12, head_h=26):
    """Truth table. rows: list of tuples of bools. hl: set of column indexes to outline."""
    for j, h in enumerate(headers):
        pg.rect(x + j * colw, y, colw, head_h, C.INK, 1, fillcolor="#e8ecf2")
        pg.eq(x + j * colw + colw / 2, y + head_h / 2, h, size + 1, align="center", valign="middle")
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            yy = y + head_h + i * rowh
            pg.rect(x + j * colw, yy, colw, rowh, "#9aa3ad", 0.6, fillcolor=TRUE_BG if v else FALSE_BG)
            pg.text(x + j * colw + colw / 2, yy + rowh / 2 - size * 0.62, TF(v), size,
                    C.GREEN if v else C.RED, F.BOLD, align="center")
    for j in (hl or ()):
        pg.rect(x + j * colw, y, colw, head_h + rowh * len(rows), C.ORANGE, 2.2)
    return head_h + rowh * len(rows)


def battery(pg, x, y):
    pg.line(x, y - 10, x, y + 10, WIRE, 2)
    pg.line(x + 6, y - 5, x + 6, y + 5, WIRE, 3)


def lamp(pg, x, y, on):
    if on:
        for k in range(8):
            import math
            a = k * math.pi / 4
            pg.line(x + 14 * math.cos(a), y + 14 * math.sin(a), x + 20 * math.cos(a), y + 20 * math.sin(a),
                    C.ORANGE, 1.4)
    pg.circle(x, y, 10, WIRE, 1.6, fillcolor=GLOW if on else "#ffffff")
    pg.line(x - 7, y - 7, x + 7, y + 7, WIRE, 1)
    pg.line(x - 7, y + 7, x + 7, y - 7, WIRE, 1)


def switch(pg, x, y, closed, label=None, w=34):
    pg.dot(x, y, 2.6, WIRE)
    pg.dot(x + w, y, 2.6, WIRE)
    if closed:
        pg.line(x, y, x + w, y, C.GREEN, 2.2)
    else:
        pg.line(x, y, x + w - 4, y - 14, C.RED, 2.2)
    if label:
        pg.text(x + w / 2, y + 6, label, 11, C.INK, F.BOLD, align="center", solid=False)


def series(pg, x, y, a, b, w=200):
    """Battery - switch A - switch B - lamp in one loop."""
    top, bot = y, y + 50
    battery(pg, x, (top + bot) / 2)
    pg.line(x, top + 15, x, top, WIRE, 1.4)
    pg.line(x, top, x + 40, top, WIRE, 1.4)
    switch(pg, x + 40, top, a, "A")
    pg.line(x + 74, top, x + 100, top, WIRE, 1.4)
    switch(pg, x + 100, top, b, "B")
    pg.line(x + 134, top, x + w, top, WIRE, 1.4)
    pg.line(x + w, top, x + w, (top + bot) / 2 - 10, WIRE, 1.4)
    lamp(pg, x + w, (top + bot) / 2, a and b)
    pg.line(x + w, (top + bot) / 2 + 10, x + w, bot, WIRE, 1.4)
    pg.line(x + w, bot, x + 6, bot, WIRE, 1.4)
    pg.line(x + 6, bot, x + 6, (top + bot) / 2 + 5, WIRE, 1.4)
    pg.line(x, top + 15, x, (top + bot) / 2 - 10, WIRE, 1.4)


def parallel(pg, x, y, a, b, w=200):
    top, mid, bot = y, y + 34, y + 76
    battery(pg, x, (mid + bot) / 2 + 4)
    pg.line(x, (mid + bot) / 2 - 6, x, top, WIRE, 1.4)
    pg.line(x, top, x + 60, top, WIRE, 1.4)
    pg.line(x + 30, top, x + 30, mid, WIRE, 1.4)
    pg.line(x + 30, mid, x + 60, mid, WIRE, 1.4)
    switch(pg, x + 60, top, a, "A")
    switch(pg, x + 60, mid, b, "B")
    pg.line(x + 94, top, x + 130, top, WIRE, 1.4)
    pg.line(x + 94, mid, x + 130, mid, WIRE, 1.4)
    pg.line(x + 130, top, x + 130, mid, WIRE, 1.4)
    pg.line(x + 130, top, x + w, top, WIRE, 1.4)
    pg.line(x + w, top, x + w, (top + bot) / 2 - 10, WIRE, 1.4)
    lamp(pg, x + w, (top + bot) / 2, a or b)
    pg.line(x + w, (top + bot) / 2 + 10, x + w, bot, WIRE, 1.4)
    pg.line(x + w, bot, x + 6, bot, WIRE, 1.4)
    pg.line(x + 6, bot, x + 6, (mid + bot) / 2 + 9, WIRE, 1.4)


def code(pg, x, y, lines, w=300, size=11.5):
    lh = size * 1.5
    h = lh * len(lines) + 14
    pg.rect(x, y, w, h, "#263238", 1, fillcolor="#263238", r=6)
    for i, (s, col) in enumerate(lines):
        pg.text(x + 12, y + 7 + i * lh, s, size, col, F.MONO)
    return h


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 7, "Elementary logic", "true or false, wired up like light switches",
                     C.ORANGE, PAPER)
    series(pg, L + 30, 220, True, True, 190)
    pg.note(L + 30, 290, "both switches on: lamp on", C.GREEN, 17)
    parallel(pg, L + 270, 210, False, True, 190)
    pg.note(L + 270, 300, "either switch on: lamp on", C.GREEN, 17)
    f = ch.flow(top=400)
    f.p("Logic is the maths of {B:true} and {B:false}. It's how computers make decisions (every "
        "{o:if} in a program), how search engines combine words, and how you check whether an "
        "argument actually holds up.", 14, gap=10)
    f.p("There are only a handful of ideas: {B:not}, {B:and}, {B:or}, and {B:if... then}. We'll "
        "wire each one as a light switch circuit, then write it as a {B:truth table} (a list of "
        "every possible case), and finally as Python code.", 14, gap=10)
    f.p("{y:Not on a lecture slide, but underneath Chapter 6 (sets) and every program you'll write.}",
        12.5)


def statements(ch):
    f = flow(ch)
    sec(f, "Statements: sentences that are true or false")
    f.p("A {B:statement} is a sentence that is definitely {G:true} or definitely {R:false}, even if "
        "you don't know which yet. Which of these are statements?", 14, gap=8)
    ch.term("statement", "a sentence that is either true or false")
    rows = [("\"Paris is in France.\"", True, "statement: true"),
            ("\"7 is an even number.\"", True, "statement: false (still a statement!)"),
            ("\"Shut the door.\"", False, "an order: can't be true or false"),
            ("\"Is it raining?\"", False, "a question: not a statement"),
            ("\"x > 3\"", None, "depends on x: a statement once x\nhas a value")]
    for s, ok, why in rows:
        y = f.reserve(30 if "\n" not in why else 46)
        pg = f.pg
        pg.text(L + 20, y + 3, s, 14, C.INK)
        if ok is True:
            pg.tick(L + 230, y + 4, 12)
        elif ok is False:
            pg.xmark(L + 230, y + 4, 12)
        else:
            pg.text(L + 228, y + 1, "?", 16, C.ORANGE, F.BOLD)
        pg.note(L + 260, y + 2, why, C.GREEN if ok else (C.RED if ok is False else C.ORANGE), 15)
    f.p("Being true or false is called the statement's {B:truth value}, written {G:T} or {R:F}. "
        "Computers write 1 and 0, or True and False. We'll use letters like $P$ and $Q$ as "
        "names for statements, just as $x$ names a number.", 14)
    ch.term("truth value", "whether a statement is true (T, 1) or false (F, 0)")


def logic_not(ch):
    f = flow(ch)
    sec(f, "NOT: flip it", room=250)
    f.p("{B:NOT} turns true into false and false into true, like flicking a switch. If $P$ is "
        "\"it is raining\", then $\\neg P$ (\"not P\") is \"it is not raining\".", 14, gap=8)
    ch.symbol(r"\neg P", "not P", "true exactly when P is false")
    y = f.reserve(80)
    pg = f.pg
    table(pg, L + 30, y, [r"P", r"\neg P"], [(True, False), (False, True)], colw=70)
    pg.note(L + 200, y + 4, "Only 2 rows: P can only be T or F.\nNOT just swaps them.", C.RED, 15)
    pg.note(L + 200, y + 46, "Set version (Chapter 6): the complement A'", C.PURPLE, 15)
    f.p("{h:Other ways books write it:} ~P,  P̄,  !P (in C and Java), not P (Python).", 13.5, C.BROWN)


def logic_and(ch):
    f = flow(ch)
    sec(f, "AND: two switches in a row", room=420)
    f.p("Wire two switches one after the other (\"in series\"). Electricity must get through "
        "{B:both}, so the lamp lights only when A {B:and} B are both on. Here are all four ways "
        "the switches can be set:", 14, gap=8)
    y = f.reserve(170)
    pg = f.pg
    combos = [(True, True), (True, False), (False, True), (False, False)]
    for i, (a, b) in enumerate(combos):
        x = L + 10 + (i % 2) * 250
        yy = y + (i // 2) * 84
        series(pg, x, yy + 6, a, b, 170)
        pg.note(x + 190, yy + 14, "ON" if a and b else "off", C.GREEN if a and b else C.GREY, 16)
    f.p("Replace \"on\" by T and \"off\" by F, and you have the {B:truth table} for AND. We "
        "write \"A and B\" as $A \\wedge B$:", 14, gap=8)
    ch.symbol(r"A\wedge B", "A and B", "true only when both A and B are true")
    ch.term("truth table", "a table listing every combination of T/F inputs and the result")
    y = f.reserve(130)
    pg = f.pg
    table(pg, L + 30, y, [r"A", r"B", r"A\wedge B"], [(a, b, a and b) for a, b in combos], colw=64, hl={2})
    pg.note(L + 250, y + 4, "just one T in the answer column:\nthe row where both are T", C.RED, 15)
    pg.note(L + 250, y + 56, "∧ looks like the ∩ of sets:\nA ∩ B = in A AND in B", C.PURPLE, 15)
    ch.check([a and b for a, b in combos], [True, False, False, False])


def logic_or(ch):
    f = flow(ch)
    sec(f, "OR: two switches side by side", room=430)
    f.p("Now wire the switches side by side (\"in parallel\"). Electricity can take {B:either} "
        "path, so the lamp lights if A is on, or B is on, {B:or both}.", 14, gap=8)
    y = f.reserve(200)
    pg = f.pg
    combos = [(True, True), (True, False), (False, True), (False, False)]
    for i, (a, b) in enumerate(combos):
        x = L + 10 + (i % 2) * 250
        yy = y + (i // 2) * 100
        parallel(pg, x, yy + 10, a, b, 170)
        pg.note(x + 190, yy + 24, "ON" if a or b else "off", C.GREEN if a or b else C.GREY, 16)
    y = f.reserve(130)
    pg = f.pg
    table(pg, L + 30, y, [r"A", r"B", r"A\vee B"], [(a, b, a or b) for a, b in combos], colw=64, hl={2})
    pg.note(L + 250, y + 4, "just one F: the row where\nboth are off", C.RED, 15)
    pg.note(L + 250, y + 56, "∨ is like the ∪ of sets:\nA ∪ B = in A OR in B (or both)", C.PURPLE, 15)
    ch.symbol(r"A\vee B", "A or B", "true when at least one of A, B is true")
    ch.check([a or b for a, b in combos], [True, True, True, False])
    f.p("{R:Maths \"or\" includes both.} In everyday speech \"or\" often means one but not the "
        "other. Maths has a separate name for that, on the next page.", 13.5)


def logic_xor(ch):
    f = flow(ch)
    sec(f, "Exclusive or: the landing light", room=330)
    f.p("A menu says \"tea {B:or} coffee included\". You can't have both! That's {B:exclusive or} "
        "(XOR, written $\\oplus$): true when exactly one is true.", 14, gap=8)
    ch.symbol(r"A\oplus B", "A x-or B (exclusive or)", "true when exactly one of A, B is true")
    ch.term("exclusive or (XOR)", "true when exactly one input is true, not both")
    y = f.reserve(130)
    pg = f.pg
    combos = [(True, True), (True, False), (False, True), (False, False)]
    table(pg, L + 30, y, [r"A", r"B", r"A\oplus B"], [(a, b, a != b) for a, b in combos], colw=64, hl={2})
    pg.note(L + 250, y, "The light on a staircase has a switch at the\nbottom and one at the top. "
            "Flip either one\nand the light changes. Light on = the two\nswitches are in different "
            "positions:\nthat's XOR.", C.INK, 15)
    ch.check([a != b for a, b in combos], [False, True, True, False])
    f.p("XOR is everywhere in computing: it's how a computer adds two binary digits (Chapter 10) "
        "without the carry, and a basic tool in encryption.", 13.5, C.GREY)


def de_morgan(ch):
    f = flow(ch)
    sec(f, "Building bigger tables, column by column", room=430)
    f.p("Is \"not (A and B)\" the same as \"(not A) or (not B)\"? Don't guess: build a table. "
        "Add one column for each small piece, then combine:", 14, gap=8)
    y = f.reserve(140)
    pg = f.pg
    combos = [(True, True), (True, False), (False, True), (False, False)]
    rows = [(a, b, a and b, not (a and b), not a, not b, (not a) or (not b)) for a, b in combos]
    hdr = [r"A", r"B", r"A\wedge B", r"\neg(A\wedge B)", r"\neg A", r"\neg B", r"\neg A\vee\neg B"]
    table(pg, L, y, hdr, rows, colw=70, hl={3, 6}, size=11)
    ch.check([r[3] for r in rows], [r[6] for r in rows])
    f.p("The two outlined columns match in every row, so the statements always agree. This is "
        "{B:De Morgan's law}. In words: \"it's not true that both happened\" means \"at least one "
        "of them didn't happen\".", 14, gap=8)
    ch.term("De Morgan's laws", "not(A and B) = (not A) or (not B);  not(A or B) = (not A) and (not B)")
    y = f.reserve(60)
    pg = f.pg
    pg.eq(L + 30, y, r"\neg(A\wedge B)=\neg A\vee\neg B", 19, C.BLUE)
    pg.eq(L + 270, y, r"\neg(A\vee B)=\neg A\wedge\neg B", 19, C.BLUE)
    pg.note(L + 30, y + 30, "NOT flips AND into OR...", C.RED, 15)
    pg.note(L + 270, y + 30, "...and OR into AND", C.RED, 15)
    ch.formula(r"\neg(A\wedge B)=\neg A\vee\neg B", "De Morgan's law")
    f.p("{h:Programming use:} \"not (logged_in and paid)\" is the same test as \"not logged_in or not "
        "paid\". Handy when tidying up conditions.", 13.5, C.BROWN)


def promise(ch):
    f = flow(ch)
    sec(f, "IF... THEN: a parent's promise", room=520)
    f.p("A parent says: {B:\"If you tidy your room, then you get ice cream.\"} When has the parent "
        "{R:broken} the promise? Look at the four things that can happen:", 14, gap=8)
    y = f.reserve(200)
    pg = f.pg
    panels = [(True, True, "Tidied, got ice cream.", "promise kept", True),
              (True, False, "Tidied, NO ice cream!", "promise BROKEN", False),
              (False, True, "Didn't tidy, got ice\ncream anyway.", "not broken: the parent\n"
               "just being generous", True),
              (False, False, "Didn't tidy, no ice\ncream.", "promise kept", True)]
    pw = (W - 18) / 4
    for i, (t, ic, what, verdict, ok) in enumerate(panels):
        x = L + i * (pw + 6)
        pg.rect(x, y, pw, 194, C.INK, 1.3, fillcolor="#ffffff" if ok else "#fff0f0", r=4)
        # room: tidy or messy
        pg.rect(x + 10, y + 12, 44, 30, C.BROWN, 1, fillcolor="#f5ecd9")
        if t:
            pg.line(x + 16, y + 34, x + 48, y + 34, C.BROWN, 2)
        else:
            for k in range(5):
                pg.line(x + 14 + k * 7, y + 36 - (k % 2) * 8, x + 20 + k * 7, y + 24 + (k % 3) * 4, C.RED, 1.4)
        # ice cream
        cx = x + pw - 30
        pg.poly([(cx - 9, y + 26), (cx + 9, y + 26), (cx, y + 50)], C.BROWN, 1.2, fill=None, closed=True)
        if ic:
            pg.circle(cx, y + 20, 9, C.PINK, 1.2, fillcolor="#f8bbd0")
        else:
            pg.xmark(cx - 6, y + 18, 12)
        pg.note(x + 6, y + 58, what, C.INK, 14)
        pg.note(x + 6, y + 110, verdict, C.GREEN if ok else C.RED, 15)
        pg.text(x + pw / 2, y + 166, "T" if ok else "F", 18, C.GREEN if ok else C.RED, F.BOLD, align="center")
    f.p("Only panel 2 breaks the promise. So \"if P then Q\", written $P \\Rightarrow Q$, is "
        "{R:false only when P is true and Q is false}. Everything else counts as true:", 14, gap=8)
    ch.symbol(r"P\Rightarrow Q", "P implies Q / if P then Q", "false only when P is true and Q is false")
    ch.term("implication (if... then)", "P ⇒ Q: false only when P is true but Q is false")
    y = f.reserve(130)
    pg = f.pg
    combos = [(True, True), (True, False), (False, True), (False, False)]
    table(pg, L + 30, y, [r"P", r"Q", r"P\Rightarrow Q"], [(p, q, (not p) or q) for p, q in combos], colw=64,
          hl={2})
    pg.note(L + 250, y + 4, "P = \"you tidy\", Q = \"you get ice cream\"", C.INK, 15)
    pg.note(L + 250, y + 34, "rows 3 and 4 feel odd, but the promise\nsaid nothing about what happens if\n"
            "you DON'T tidy, so it can't be broken there", C.RED, 15)
    ch.check([(not p) or q for p, q in combos], [True, False, True, True])


def converse(ch):
    f = flow(ch)
    sec(f, "Turning an \"if\" around", room=380)
    f.p("Start with a true statement: {B:\"If it's a cat, then it's an animal.\"} Now shuffle it "
        "in three ways. Which versions are still true?", 14, gap=8)
    rows = [("original", "If it's a cat, then it's an animal.", True, "true"),
            ("converse (swap)", "If it's an animal, then it's a cat.", False, "FALSE: a dog is an animal"),
            ("contrapositive", "If it's not an animal, then it's not a cat.", True,
             "true: swap AND put NOT on both; always matches the original"),
            ("inverse", "If it's not a cat, then it's not an animal.", False, "FALSE: a dog again (NOT on both, no swap)")]
    for name, s, ok, why in rows:
        y = f.reserve(44)
        pg = f.pg
        pg.text(L + 10, y + 2, name, 12, C.ORANGE, F.BOLD)
        pg.text(L + 140, y + 2, s, 12.5, C.INK)
        pg.note(L + 140, y + 18, why, C.GREEN if ok else C.RED, 14)
    ch.term("converse", "the 'if' statement with its two halves swapped: Q ⇒ P")
    ch.term("contrapositive", "not Q ⇒ not P; always has the same truth as P ⇒ Q")
    f.need(330)
    f.p("{b:The picture that settles it.} Draw everything that makes P true as a region, and the same for Q. "
        "\"If P then Q\" says {B:the P region sits entirely inside the Q region}.", 14, gap=8)
    go(f, "Picture a small blob \"cats\" inside a big blob \"animals\". Where would a dot have to be to "
          "break \"if it's a cat, then it's an animal\"? Is there any room for it?")
    y = f.reserve(214)
    pg = f.pg
    pw = (W - 18) / 4
    panels = [("if cat, then animal", "true: every cat is\nan animal", "in", None, None, True, "cats", "animals"),
              ("if pet, then mammal", "FALSE: a goldfish is\na pet, not a mammal", "poke", "goldfish", "P", False,
               "pets", "mammals"),
              ("converse: if animal,\nthen cat", "FALSE: a dog is an\nanimal, not a cat", "in", "dog", "Q", False,
               "cats", "animals"),
              ("contrapositive: if not\nanimal, then not cat", "true: nothing outside\nQ is inside P", "in", None,
               "out", True, "cats", "animals")]
    for i, (title, cap, shape, dot_lab, where, ok, pn, qn) in enumerate(panels):
        x = L + i * (pw + 6)
        fy = y + 34
        pg.text(x + pw / 2, y, title, 10.5, C.GREEN if ok else C.RED, F.BOLD, align="center")
        pg.rect(x, fy, pw, 110, C.GREY, 1.0, fillcolor=C.LIGHT[C.GREEN] if where == "out" else "#ffffff", r=4)
        qx, qy = x + pw / 2 - (12 if shape == "poke" else 0), fy + 55
        pg.ellipse(qx, qy, 46, 40, C.PURPLE, 1.4, fillcolor=C.LIGHT[C.PURPLE] if where != "out" else "#ffffff")
        px_ = qx + (40 if shape == "poke" else 4)
        pg.ellipse(px_, qy + 6, 22, 15, C.ORANGE, 1.4, fillcolor=C.LIGHT[C.ORANGE])
        if shape != "poke":
            pg.ellipse(qx, qy, 46, 40, C.PURPLE, 1.4)
        pg.text(qx + (4 if shape == "poke" else 0), qy - 32, f"Q: {qn}", 9.5, C.PURPLE, F.BOLD, align="center")
        if shape == "poke":
            pg.text(px_ + 12, qy + 23, f"P: {pn}", 9, C.ORANGE, F.BOLD, align="center")
        else:
            pg.text(px_, qy + 1, f"P: {pn}", 9, C.ORANGE, F.BOLD, align="center")
        if dot_lab:
            dx, dy = (px_ + 15, qy + 12) if where == "P" else (qx - 24, qy + 22)
            pg.dot(dx, dy, 3.5, C.RED)
            if where == "P":
                pg.text(x + pw - 3, fy + 94, dot_lab, 9.5, C.RED, F.BOLD, align="right")
            else:
                pg.text(dx, dy + 4, dot_lab, 9.5, C.RED, F.BOLD, align="center")
        pg.note(x + 2, fy + 116, cap, C.GREEN if ok else C.RED, 13, w=pw)
    world = {"tom the cat", "rex the dog", "a rock"}
    cats, animals = {"tom the cat"}, {"tom the cat", "rex the dog"}
    ch.check((cats <= animals, animals <= cats, (world - animals) <= (world - cats)), (True, False, True))
    f.p("A {B:counterexample} to \"if P then Q\" is a dot {B:inside P but outside Q}. When P sits wholly "
        "inside Q there's nowhere to put one, so the statement is true. The {B:converse} asks the opposite "
        "(is Q inside P?), which is a different question. The {B:contrapositive} looks at the outside: "
        "everything outside Q is automatically outside P, the same picture read from the other side.",
        14, gap=10)
    f.p("When a statement and its converse are {B:both} true, we say \"P {B:if and only if} Q\", "
        "written $P \\Leftrightarrow Q$. Example: \"a number is even if and only if it divides by 2\". "
        "The two sides always stand or fall together.", 14, gap=8)
    ch.symbol(r"P\Leftrightarrow Q", "P if and only if Q (iff)", "P and Q are both true or both false")
    ch.term("if and only if (iff)", "P ⇔ Q: P and Q are always both true or both false")
    f.p("{R:A very common reasoning error} is assuming the converse: \"all cats are animals, Tom is "
        "an animal, so Tom is a cat\". The last step uses the converse, which isn't true.", 13.5)


def python_if(ch):
    f = flow(ch)
    sec(f, "The same logic in Python", room=420)
    f.p("Programs are full of truth tables in disguise. Python spells the symbols out as words:",
        14, gap=8)
    y = f.reserve(176)
    pg = f.pg
    h = code(pg, L + 10, y, [("age = 20", "#ffffff"), ("has_ticket = False", "#ffffff"), ("", "#ffffff"),
                              ("if age >= 18 and has_ticket:", "#80cbc4"), ("    print('Come in')", "#ffcc80"),
                              ("elif age >= 18 or has_ticket:", "#80cbc4"), ("    print('Nearly!')", "#ffcc80"),
                              ("if not has_ticket:", "#80cbc4"), ("    print('Buy a ticket')", "#ffcc80")], w=270)
    pg.note(L + 300, y, "age >= 18 is True (20 ≥ 18)\nhas_ticket is False", C.INK, 15)
    pg.note(L + 300, y + 44, "True and False → False:\nskip 'Come in'", C.RED, 15)
    pg.note(L + 300, y + 88, "True or False → True:\nprints 'Nearly!'", C.GREEN, 15)
    pg.note(L + 300, y + 132, "not False → True:\nprints 'Buy a ticket'", C.GREEN, 15)
    ch.check((20 >= 18) and False, False)
    ch.check((20 >= 18) or False, True)
    f.gap(10)
    y = f.reserve(90)
    pg = f.pg
    rows = [("maths", r"\neg", r"\wedge", r"\vee", r"\oplus"), ("Python", "not", "and", "or", "^  or  !=")]
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            x = L + 10 + j * 96
            pg.rect(x, y + i * 34, 96, 34, C.GREY, 0.8, fillcolor="#eef1f5" if i == 0 else "#ffffff")
            if i == 0 and j > 0:
                pg.eq(x + 48, y + 17, cell, 16, align="center", valign="middle")
            else:
                pg.text(x + 48, y + i * 34 + 10, cell, 11 if len(cell) > 8 else 13, C.INK,
                        F.BOLD if j == 0 else F.MONO, align="center")
    f.p("{h:Python bonus:} \"and\" stops early if the left side is False (the answer must be False "
        "anyway). That's why \"if x != 0 and 10 / x > 2:\" never divides by zero.", 13.5, C.BROWN)


def quantifiers(ch):
    f = flow(ch)
    sec(f, "\"For all\" and \"there exists\"", room=300)
    f.p("Two more symbols appear in proofs and in later maths courses:", 14, gap=8)
    y = f.reserve(80)
    pg = f.pg
    pg.eq(L + 20, y, r"\forall", 26, C.BLUE)
    pg.note(L + 60, y + 2, "\"for all\" (an upside-down A, for All)", C.BLUE, 16)
    pg.eq(L + 20, y + 40, r"\exists", 26, C.PURPLE)
    pg.note(L + 60, y + 42, "\"there exists\" (a backwards E, for Exists)", C.PURPLE, 16)
    ch.symbol(r"\forall", "for all", "the statement holds for every value")
    ch.symbol(r"\exists", "there exists", "at least one value makes the statement true")
    ch.term("quantifier", "'for all' (∀) or 'there exists' (∃): says how many things a statement covers")
    f.p("$\\forall x \\in \\mathbb{R},\\ x^2 \\ge 0$ reads \"for every real number x, x squared is "
        "at least 0\" (true). $\\exists x \\in \\mathbb{Z},\\ x + 5 = 2$ reads \"there is an integer "
        "x with x + 5 = 2\" (true: x = -3).", 14, gap=8)
    f.p("{B:To prove a \"for all\" statement false, one counterexample is enough.} \"Every prime is "
        "odd\"? 2 is prime and even. Done: false.", 14)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Switchboard: your turn", fresh=True)
    f.p("Answers in grey. Draw the circuit or build the table for each one.", 13.5, gap=10)
    groups = [
        ("Statements", ["Is \"x + 1 = 4\" a statement? When?", "Give the truth value of \"3 > 5 or 2 < 4\"",
                        "Give the truth value of \"3 > 5 and 2 < 4\""],
         "1. only once x has a value (true if x = 3)   2. T   3. F"),
        ("Tables", ["Build the truth table for ¬A ∧ B", "Build the table for A ∨ ¬A. What do you notice?",
                    "Use a table to check ¬(A ∨ B) = ¬A ∧ ¬B"],
         "4. T only in the row A = F, B = T   5. always T (called a tautology)   6. the columns match"),
        ("If... then", ["\"If it rains, the match is off.\" It didn't rain and the match was off. Promise broken?",
                        "Write the converse and contrapositive of \"if n is divisible by 4, n is even\". Which are true?"],
         "7. no (row 4)   8. converse: if even then divisible by 4 (false: 6); contrapositive: if odd then not "
         "divisible by 4 (true)"),
        ("Python", ["x = 5. Is (x > 3 and x < 10) True?", "x = 5. Is not (x == 5 or x == 7) True?"],
         "9. True   10. False"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14, w=W - 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check((3 > 5) or (2 < 4), True)
    ch.check((3 > 5) and (2 < 4), False)
    ch.check((5 > 3 and 5 < 10), True)
    ch.check(not (5 == 5 or 5 == 7), False)
    combos = [(True, True), (True, False), (False, True), (False, False)]
    ch.check([not (a or b) for a, b in combos], [(not a) and (not b) for a, b in combos])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    statements(ch)
    logic_not(ch)
    logic_and(ch)
    logic_or(ch)
    logic_xor(ch)
    de_morgan(ch)
    promise(ch)
    converse(ch)
    python_if(ch)
    quantifiers(ch)
    your_turn(ch)
