"""Chapter 3 - Decimal fractions. Sticks cut into slivers and crumbs, a magnifying glass on the
number line, digits sliding past a fixed dot, long division as a comic strip, rough and fine
rulers for rounding."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, flow, go, mistakes, rule_box, rules_page, rules_table, section, step,
                         title_block)

ORDER = 3
NUM = 3
TITLE = "Decimal fractions"
SHORT = "Decimals"
SLUG = "Decimals"
ACCENT = C.ORANGE
REQUIRES = ["place-value", "fraction", "division", "multiplication", "remainder",
            "equivalent-fractions", "simplify-fraction", "addition", "subtraction"]
INTRODUCES = ["decimal-point", "decimal-place-value", "compare-decimals", "decimal-to-fraction",
              "fraction-to-decimal", "decimal-arithmetic", "recurring-decimals", "rounding",
              "decimal-places", "truncation", "significant-figures", "estimation"]

STICK = "#b07a3a"
GLASS = "#5b8fd6"
PAPER = "#f6f9ff"


def icon(pg, x, y):
    pg.circle(x + 7, y + 7, 6, GLASS, 2, fillcolor="#e6f0ff")
    pg.line(x + 11.5, y + 11.5, x + 18, y + 18, C.BROWN, 3)


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def numline(pg, x, y, w, a, b, n, labels=None, color=C.INK, size=10, lab_every=1, fmt=None):
    """Horizontal ruler from value a to b with n equal gaps."""
    pg.line(x - 6, y, x + w + 6, y, color, 1.4)
    for i in range(n + 1):
        X = x + w * i / n
        big = (i % lab_every == 0)
        pg.line(X, y - (6 if big else 3), X, y + (6 if big else 3), color, 1.1 if big else 0.8)
        if big and labels is not False:
            v = a + (b - a) * i / n
            s = fmt(v) if fmt else (f"{v:.10f}".rstrip("0").rstrip("."))
            pg.text(X, y + 9, s, size, C.GREY, align="center", solid=False)
    return lambda v: x + w * (v - a) / (b - a)


def funnel(pg, x1, x2, y1, X1, X2, y2, color=GLASS):
    """The magnifying-glass cone: a small stretch of one line blown up to a longer line below."""
    pg.fillpoly([(x1, y1), (x2, y1), (X2, y2), (X1, y2)], "#e6f0ff")
    pg.line(x1, y1, X1, y2, color, 0.9, dash=(4, 3))
    pg.line(x2, y1, X2, y2, color, 0.9, dash=(4, 3))


def lens(pg, cx, cy, r):
    pg.circle(cx, cy, r, GLASS, 2.4)
    a = 0.72
    pg.line(cx + r * a, cy + r * a, cx + r * a + 22, cy + r * a + 22, C.BROWN, 5)


def slivers(pg, x, y, n, h=30, col=C.ORANGE):
    for i in range(n):
        pg.rect(x + i * 6, y, 3.4, h, col, 0.6, fillcolor=C.LIGHT[C.ORANGE] if col == C.ORANGE else col)


def crumbs(pg, x, y, n, col=C.RED):
    for i in range(n):
        pg.dot(x + (i % 5) * 6, y + (i // 5) * 6, 2.0, col)


def stick(pg, x, y, h=30):
    pg.rect(x, y, 7, h, C.BROWN, 0.8, fillcolor=STICK)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 3, "Decimal fractions", "numbers with a dot in them, seen through a "
                     "magnifying glass", C.ORANGE, PAPER)
    y = 250
    X = numline(pg, L + 20, y, 455, 0, 10, 10, size=11)
    pg.dot(X(3.47), y, 3.5, C.RED)
    funnel(pg, X(3), X(4), y + 26, L + 20, L + 475, y + 70)
    X2 = numline(pg, L + 20, y + 70, 455, 3, 4, 10, size=11)
    funnel(pg, X2(3.4), X2(3.5), y + 96, L + 20, L + 475, y + 140)
    X3 = numline(pg, L + 20, y + 140, 455, 3.4, 3.5, 10, size=11, fmt=lambda v: f"{v:.2f}")
    pg.dot(X3(3.47), y + 140, 5, C.RED)
    pg.text(X3(3.47), y + 108, "3.47", 20, C.RED, F.BOLD, align="center")
    lens(pg, X(3.5), y - 2, 20)
    pg.note(L + 300, y - 50, "zoom into the gap between 3 and 4...", GLASS, 17)
    f = ch.flow(top=430)
    f.p("A whole number counts whole things. But life is full of {o:bits}: £3.47, 1.8 metres, "
        "37.5 °C. The {B:dot} in these numbers lets you say \"and a bit\" precisely. This chapter "
        "shows that a decimal is nothing new: it's the same place-value idea from Chapter 1, "
        "carried on {B:to the right}, and it's another way to write a fraction (Chapter 2).",
        14, gap=10)
    f.p("You'll learn to read, compare, add, multiply and divide decimals, turn fractions into "
        "decimals with a comic-strip division, and round numbers sensibly (decimal places and "
        "significant figures, both on your Lecture 1 slides).", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 1} {y:(significant figures, decimal places, recurring decimals).}",
        12.5)


def cutting(ch):
    f = flow(ch)
    sec(f, "Cutting a stick into ten")
    f.p("In Chapter 1, ten sticks made a bundle. Now go the other way. Take {B:one stick} and cut "
        "it into {B:ten equal slivers}. Each sliver is a {o:tenth} of a stick. Cut one sliver into "
        "ten {r:crumbs}: each crumb is a {r:hundredth} of a stick.", 14, gap=10)
    y = f.reserve(96)
    pg = f.pg
    stick(pg, L + 20, y + 8, 60)
    pg.note(L + 4, y + 72, "1 stick", C.BROWN, 15)
    pg.arrow(L + 42, y + 38, L + 88, y + 38, C.GREY, 1.3)
    pg.note(L + 44, y + 12, "cut\nin 10", C.GREY, 14)
    slivers(pg, L + 100, y + 8, 10, 60)
    pg.note(L + 94, y + 72, "10 slivers (tenths)", C.ORANGE, 15)
    pg.arrow(L + 170, y + 38, L + 226, y + 38, C.GREY, 1.3)
    pg.note(L + 176, y + 12, "cut one\nin 10", C.GREY, 14)
    for i in range(10):
        pg.dot(L + 244 + (i % 5) * 9, y + 26 + (i // 5) * 12, 3, C.RED)
    pg.note(L + 226, y + 72, "10 crumbs (hundredths)", C.RED, 15)
    pg.rect(L + 360, y + 2, 130, 84, C.GREY, 0.8, r=6)
    pg.note(L + 370, y + 8, "1 stick = 10 slivers\n1 sliver = 10 crumbs\n1 stick = 100 crumbs",
            C.INK, 15)
    f.p("Now {B:3 sticks, 4 slivers and 7 crumbs} is written like this. The {B:dot} (called the "
        "{B:decimal point}) is a fence: whole sticks on the left, pieces on the right.", 14, gap=8)
    ch.term("decimal point", "the dot that separates whole units (left) from parts of a unit (right)")
    y = f.reserve(150)
    pg = f.pg
    cols = [("tens", "0", C.GREY), ("ones", "3", C.BROWN), ("", ".", C.INK),
            ("tenths", "4", C.ORANGE), ("hundredths", "7", C.RED), ("thousandths", "0", C.GREY)]
    x = L + 30
    for name, d, col in cols:
        wcol = 20 if name == "" else 78
        if name:
            pg.rect(x, y, wcol, 32, col, 1, fillcolor=C.LIGHT.get(col, "#ffffff"))
            pg.text(x + wcol / 2, y + 10, name, 9.5, col, F.BOLD, align="center")
            pg.rect(x, y + 32, wcol, 50, col, 1)
        pg.text(x + wcol / 2, y + 40, d, 30, col if name else C.INK, F.BOLD, align="center")
        x += wcol
    stick(pg, L + 30 + 78 + 20, y + 92, 34)
    stick(pg, L + 30 + 78 + 32, y + 92, 34)
    stick(pg, L + 30 + 78 + 44, y + 92, 34)
    slivers(pg, L + 30 + 176 + 20, y + 92, 4, 34)
    crumbs(pg, L + 30 + 254 + 22, y + 96, 7)
    pg.note(L + 30 + 336, y + 94, "the grey zeros change\nnothing: 03.470 = 3.47", C.GREY, 15)
    f.p("Read it as {B:\"three point four seven\"}. (Not \"three point forty-seven\": after the "
        "dot you read the digits one at a time.)", 14, gap=8)
    ch.check(3 + sp.Rational(4, 10) + sp.Rational(7, 100), sp.Rational(347, 100))
    f.p("Each column is {B:ten times smaller} than the column to its left, on {B:both} sides of "
        "the dot. That's the only rule. Hundreds, tens, ones, tenths, hundredths, thousandths... "
        "one long ladder, and the dot just marks where the whole ones stop.", 14, gap=8)
    ch.term("tenth", "one of ten equal pieces of 1; written 0.1 or 1/10")
    ch.term("hundredth", "one of a hundred equal pieces of 1; written 0.01 or 1/100")


def zooming(ch):
    f = flow(ch)
    sec(f, "The magnifying glass: where does 3.47 live?", room=380)
    f.p("A number line is a ruler that goes on forever. Decimals live {B:in the gaps} between "
        "whole numbers. To find 3.47, zoom in twice:", 14, gap=8)
    y = f.reserve(230)
    pg = f.pg
    X = numline(pg, L + 20, y + 20, 440, 0, 10, 10, size=11)
    pg.highlight(X(3), y + 12, X(4) - X(3), 16, "o")
    pg.note(L + 20, y - 6, "zoom 1: which whole numbers is it between? 3 and 4.", C.ORANGE, 15)
    funnel(pg, X(3), X(4), y + 36, L + 20, L + 460, y + 90)
    X2 = numline(pg, L + 20, y + 90, 440, 3, 4, 10, size=11, fmt=lambda v: f"{v:.1f}")
    pg.highlight(X2(3.4), y + 82, X2(3.5) - X2(3.4), 16, "r")
    pg.note(L + 20, y + 58, "zoom 2: which tenths? 3.4 and 3.5.", C.RED, 15)
    funnel(pg, X2(3.4), X2(3.5), y + 106, L + 20, L + 460, y + 160)
    X3 = numline(pg, L + 20, y + 160, 440, 3.4, 3.5, 10, size=11, fmt=lambda v: f"{v:.2f}")
    pg.dot(X3(3.47), y + 160, 5, C.RED)
    pg.arrow(X3(3.47), y + 200, X3(3.47), y + 170, C.RED, 1.4)
    pg.note(X3(3.47) + 8, y + 190, "3.47: seven small steps past 3.4", C.RED, 15)
    f.p("Every zoom shows one more digit. The first digit after the dot says which tenth, the "
        "next says which hundredth, and so on. You could keep zooming forever, which is why some "
        "numbers need endless digits (you'll meet them later in this chapter).", 14)


def comparing(ch):
    f = flow(ch)
    sec(f, "Which is bigger: 0.5 or 0.45?", room=330)
    f.p("Lots of people say 0.45, because 45 is bigger than 5. {R:That's the trap.} Compare "
        "column by column, from the left, like a race where the first difference wins:", 14, gap=8)
    y = f.reserve(120)
    pg = f.pg
    x0 = L + 40
    for k, (num, pieces) in enumerate([("0.50", (5, 0)), ("0.45", (4, 5))]):
        yy = y + k * 52
        for j, ch_ in enumerate(num):
            col = [C.BROWN, C.INK, C.ORANGE, C.RED][j]
            if num == "0.50" and j == 3:
                col = C.GREY
            pg.text(x0 + j * 22, yy, ch_, 26, col, F.BOLD)
        slivers(pg, x0 + 130, yy + 2, pieces[0], 28)
        crumbs(pg, x0 + 130 + pieces[0] * 6 + 8, yy + 8, pieces[1])
    pg.highlight(x0 + 42, y - 2, 20, 88, "y")
    pg.note(x0 + 240, y - 2, "tenths column: 5 against 4.\n5 wins, so 0.5 is bigger.\n"
            "Stop! The later digits don't matter.", C.RED, 15)
    pg.note(x0 + 240, y + 62, "padding with a zero (0.50) helps\nyour eye line them up.", C.GREY, 15)
    ch.check_true(sp.Rational(1, 2) > sp.Rational(45, 100), "0.5 > 0.45")
    f.p("With slivers you can see it: half a stick (5 slivers) is more than 4 slivers and a few "
        "crumbs. {B:Line the dots up, pad with zeros, compare from the left.}", 14)
    ch.term("compare decimals", "line up the dots, pad with zeros, compare digits from the left")


def as_fractions(ch):
    f = flow(ch)
    sec(f, "A decimal is a fraction wearing a disguise", room=440)
    rule_box(f, "decimal to fraction", [
        "Count the digits after the point: 1 digit means tenths, 2 hundredths, 3 thousandths.",
        "Write the digits after the point over 10, 100 or 1000 (one 0 per digit), then simplify.",
        "A whole-number part stays in front (mixed number): $2.6=2\\frac{6}{10}=2\\frac35$.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    f.p("The last column you use tells you the bottom number. Read the digits after the dot as a "
        "whole number, and put it over 10, 100 or 1000:", 14, gap=8)
    rows = [(r"0.7", r"\frac{7}{10}", None, "one digit after the dot: tenths"),
            (r"0.25", r"\frac{25}{100}", r"\frac{1}{4}", "two digits: hundredths, then simplify"),
            (r"0.125", r"\frac{125}{1000}", r"\frac{1}{8}", "three digits: thousandths"),
            (r"2.6", r"2\frac{6}{10}", r"2\frac{3}{5}", "the whole 2 just rides along")]
    for dec, fr, simp, why in rows:
        y = f.reserve(50)
        pg = f.pg
        pg.eq(L + 20, y + 22, dec, 22, C.ORANGE, valign="middle")
        pg.text(L + 88, y + 12, "=", 18, C.GREY)
        w, _ = pg.eq(L + 110, y + 22, fr, 20, valign="middle")
        if simp:
            pg.text(L + 120 + w, y + 12, "=", 18, C.GREY)
            pg.eq(L + 142 + w, y + 22, simp, 20, C.GREEN, valign="middle")
        pg.note(L + 250, y + 12, why, C.RED, 15)
    ch.check(sp.Rational(25, 100), sp.Rational(1, 4))
    ch.check(sp.Rational(125, 1000), sp.Rational(1, 8))
    ch.check(sp.Rational(26, 10), 2 + sp.Rational(3, 5))
    f.p("{b:Worth knowing by heart} (they come up constantly):", 14, gap=6)
    y = f.reserve(56)
    pg = f.pg
    pairs = [(r"\tfrac12", "0.5"), (r"\tfrac14", "0.25"), (r"\tfrac34", "0.75"), (r"\tfrac15", "0.2"),
             (r"\tfrac1{10}", "0.1"), (r"\tfrac18", "0.125"), (r"\tfrac13", r"0.\dot3")]
    for i, (a, b) in enumerate(pairs):
        cx = L + 36 + i * 70
        pg.rect(cx - 32, y, 64, 50, C.ORANGE, 0.9, fillcolor="#fff5ea", r=6)
        pg.eq(cx, y + 3, a, 17, align="center")
        pg.eq(cx, y + 27, b, 15, C.ORANGE, align="center")
    f.p("(The dot over the 3 in the last one is explained later in this chapter.)", 12, C.GREY)


def add_sub(ch):
    f = flow(ch)
    sec(f, "Adding and taking away: line up the dots", room=460)
    rule_box(f, "adding and subtracting decimals", [
        "Write the numbers in columns with the {B:decimal points in a vertical line}.",
        "Fill empty places with zeros so every number has the same number of decimal places "
        "($5=5.00$).",
        "Add or subtract column by column from the right, exactly as for whole numbers.",
        "The point in the answer goes directly under the other points.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    f.p("A shopping receipt already does this. Pence line up under pence, pounds under pounds, so "
        "the dots form a straight vertical line:", 14, gap=8)
    y = f.reserve(162)
    pg = f.pg
    pg.rect(L + 20, y, 170, 146, C.GREY, 0.8, fillcolor="#ffffff")
    for i in range(0, 170, 10):
        pg.line(L + 20 + i, y + 146, L + 25 + i, y + 150, C.GREY, 0.6)
    pg.text(L + 105, y + 6, "CORNER SHOP", 10, C.GREY, F.BOLD, align="center")
    items = [("milk", " 1.35"), ("bread", " 0.99"), ("cheese", "12.50")]
    for i, (it, pr) in enumerate(items):
        pg.text(L + 30, y + 28 + i * 22, it, 12, C.INK, F.MONO)
        pg.text(L + 120, y + 28 + i * 22, pr, 13, C.INK, F.MONO)
    pg.line(L + 115, y + 96, L + 180, y + 96, C.INK, 1)
    pg.text(L + 30, y + 104, "TOTAL", 12, C.INK, F.BOLD)
    pg.text(L + 120, y + 104, "14.84", 13, C.GREEN, F.MONO)
    dotx = L + 120 + pg.twidth("12", 13, F.MONO) + pg.twidth(".", 13, F.MONO) / 2
    pg.line(dotx, y + 22, dotx, y + 122, C.RED, 1, dash=(2, 2))
    pg.note(L + 210, y + 4, "the dots sit in one straight column.\n"
            "Then add exactly like Chapter 1:", C.RED, 15)
    pg.note(L + 210, y + 50, "hundredths: 5 + 9 + 0 = 14, write 4 carry 1\n"
            "tenths: 3 + 9 + 5 + 1 = 18, write 8 carry 1\n"
            "ones: 1 + 0 + 2 + 1 = 4\ntens: 1", C.INK, 15)
    pg.note(L + 210, y + 134, "the dot drops straight down into the answer", C.GREEN, 15)
    ch.check(sp.Rational(135, 100) + sp.Rational(99, 100) + sp.Rational(1250, 100), sp.Rational(1484, 100))
    f.p("{b:Taking away: fill the empty spaces with zeros first.} Work out $5 - 1.37$:", 14, gap=6)
    y = f.reserve(112)
    pg = f.pg
    X = L + 60
    for j, (d, col) in enumerate([("5", C.INK), (".", C.INK), ("0", C.ORANGE), ("0", C.ORANGE)]):
        pg.text(X + j * 18, y + 6, d, 24, col, F.BOLD)
    pg.text(X - 26, y + 40, "-", 24, C.INK, F.BOLD)
    for j, d in enumerate("1.37"):
        pg.text(X + j * 18, y + 40, d, 24, C.INK, F.BOLD)
    pg.line(X - 30, y + 74, X + 76, y + 74, C.INK, 1.6)
    for j, d in enumerate("3.63"):
        pg.text(X + j * 18, y + 78, d, 24, C.GREEN, F.BOLD)
    pg.note(X + 110, y + 4, "5 is the same as 5.00 (5 pounds = 5 pounds 0 pence).\n"
            "Write the zeros in so every column has a digit.", C.ORANGE, 15)
    pg.note(X + 110, y + 44, "then take away exactly as in Chapter 1, opening\n"
            "bundles when a column is too small.", C.INK, 15)
    pg.note(X + 110, y + 88, "check: 3.63 + 1.37 = 5.00 ✓", C.GREEN, 16)
    ch.check(5 - sp.Rational(137, 100), sp.Rational(363, 100))


def sliding(ch):
    f = flow(ch)
    sec(f, "Times 10: the dot stays still, the digits slide", room=430)
    rule_box(f, "multiplying and dividing by 10, 100, 1000", [
        "$\\times10$, $\\times100$, $\\times1000$: every digit moves {B:1, 2 or 3 places left} (the "
        "number gets bigger). $3.47\\times100=347$.",
        "$\\div10$, $\\div100$, $\\div1000$: every digit moves {B:1, 2 or 3 places right} (the number gets "
        "smaller). $3.47\\div10=0.347$.",
        "Fill any gap next to the point with 0: $0.6\\div100=0.006$.",
    ], C.ORANGE)
    ch.check(sp.Rational(6, 10) / 100, sp.Rational(6, 1000))
    f.p("Multiplying by 10 makes every stick into a bundle, every sliver into a stick, every crumb "
        "into a sliver. Each digit moves {B:one column to the left}. Picture the dot nailed to the "
        "page and the digits sliding past it:", 14, gap=8)
    y = f.reserve(170)
    pg = f.pg
    colx = [L + 40 + i * 44 for i in range(7)]
    dot_x = colx[3] + 22 + 22 - 22
    heads = ["hundreds", "tens", "ones", "tenths", "hundredths", "thousandths"]
    xs = [L + 60 + i * 58 for i in range(6)]
    for i, h in enumerate(heads):
        pg.text(xs[i] + 14, y, h, 9, C.GREY, align="center")
    dot_x = (xs[2] + xs[3]) / 2 + 14
    pg.rect(dot_x - 6, y + 14, 12, 150, C.RED, 0.6, fillcolor="#fff0f0")
    rows = [("3.47", "", 2, C.INK), ("34.7", r"\times 10", 1, C.BLUE), ("347", r"\times 100", 0, C.PURPLE),
            ("0.347", r"\div 10", 3, C.GREEN)]
    for k, (num, lab, start, col) in enumerate(rows):
        yy = y + 20 + k * 36
        digits = num.replace(".", "")
        first = {"3.47": 2, "34.7": 1, "347": 0, "0.347": 2}[num]
        if num == "0.347":
            digits = "0347"
        for j, d in enumerate(digits):
            pg.text(xs[first + j] + 14, yy, d, 22, col, F.BOLD, align="center")
        pg.dot(dot_x, yy + 20, 3, C.RED)
        if lab:
            pg.eq(L + 420, yy + 2, lab, 17, col)
        if num == "347":
            pg.text(xs[3] + 14, yy + 2, "", 22)
    pg.arrow(xs[3] + 14, y + 44, xs[2] + 14, y + 58, C.BLUE, 1.2, bend=0.3)
    pg.note(L + 380, y + 150, "the red dot never moves", C.RED, 14)
    ch.check(sp.Rational(347, 100) * 10, sp.Rational(347, 10))
    ch.check(sp.Rational(347, 100) / 10, sp.Rational(347, 1000))
    f.p("{B:× 10}: digits slide 1 place left.  {B:× 100}: 2 places.  {B:× 1000}: 3 places.  "
        "{B:÷ 10}: 1 place right, and so on. Gaps next to the dot get filled with zero "
        "(0.347 needs a 0 in the ones column so the dot isn't left floating).", 14, gap=8)
    f.p("{h:Shortcut people say:} \"move the decimal point\". It gives the same answer, but it's "
        "really the digits moving; the columns stay where they are.", 13.5, C.BROWN)


def multiplying(ch):
    f = flow(ch)
    sec(f, "Multiplying decimals: a square cut into 100", room=420)
    f.p("What is $0.3 \\times 0.4$? Think of \"of\": 0.3 {B:of} 0.4. Take a square that is 1 by 1, "
        "cut into a 10 × 10 grid. Shade 3 columns (0.3 of the width) and 4 rows (0.4 of the height):",
        14, gap=8)
    y = f.reserve(214) + 24
    pg = f.pg
    s = 16
    x0 = L + 30
    for i in range(10):
        for j in range(10):
            fc = None
            if i < 4 and j < 3:
                fc = "#f3b0a0"
            elif j < 3:
                fc = C.LIGHT[C.BLUE]
            elif i < 4:
                fc = C.LIGHT[C.ORANGE]
            pg.rect(x0 + j * s, y + i * s, s, s, "#b0b0b0", 0.4, fillcolor=fc, layer=C.UNDER)
    pg.rect(x0, y, 10 * s, 10 * s, C.INK, 1.2)
    pg.brace(x0, y - 4, x0 + 3 * s, y - 4, C.BLUE, 1.1, 5)
    pg.note(x0 + 6, y - 26, "0.3", C.BLUE, 16)
    pg.brace(x0 - 4, y + 4 * s, x0 - 4, y, C.ORANGE, 1.1, 5)
    pg.note(x0 - 30, y + 20, "0.4", C.ORANGE, 16)
    pg.note(L + 220, y + 4, "The overlap (red) is 3 × 4 = 12 little squares.", C.RED, 16)
    pg.note(L + 220, y + 34, "Each little square is 1/100 of the whole.", C.INK, 16)
    pg.eq(L + 230, y + 70, r"0.3\times0.4=\frac{12}{100}=0.12", 20)
    pg.note(L + 220, y + 128, "the answer is SMALLER than both. Multiplying by\n"
            "something less than 1 shrinks, like taking a\npart of a part.", C.PURPLE, 15)
    ch.check(sp.Rational(3, 10) * sp.Rational(4, 10), sp.Rational(12, 100))
    f.need(330)
    rule_box(f, "multiplying decimals", [
        "Ignore the decimal points and multiply the whole numbers.",
        "Count the digits after the point in {B:both} numbers together.",
        "Give the answer that many digits after the point (count from the right; add 0s at the "
        "front if needed: $0.03\\times0.2=0.006$).",
        "{B:Then} you may drop zeros at the end: $0.5\\times0.4$: $5\\times4=20$, 2 places, $0.20=0.2$.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    ch.check(sp.Rational(3, 100) * sp.Rational(2, 10), sp.Rational(6, 1000))
    ch.check(sp.Rational(5, 10) * sp.Rational(4, 10), sp.Rational(2, 10))
    step(f, r"2.5\times1.3", "1. ignore the dots for a moment")
    step(f, r"25\times13=325", "2. multiply whole numbers (Chapter 1 grid method)")
    step(f, r"2.5\ \to\ 1\text{ digit},\ \ 1.3\ \to\ 1\text{ digit}", "3. count digits after the dots: 1 + 1 = 2", size=17)
    step(f, r"3.25", "4. give the answer 2 digits after the dot", color=C.GREEN)
    ch.check(sp.Rational(25, 10) * sp.Rational(13, 10), sp.Rational(325, 100))
    step(f, r"0.5\times0.4=0.20=\grn{0.2}", "5 × 4 = 20; 2 places gives 0.20; the end 0 can go")
    f.p("{R:Place the point before you drop the zero.} Write 20, count 2 places from the right: "
        "$0.20$. Dropping the 0 first and then counting 2 places gives the wrong $0.02$.", 13.5, gap=6)
    f.p("{G:Sanity check:} 2.5 × 1.3 is roughly 2.5 × 1 = 2.5, a bit more. 3.25 is sensible; "
        "32.5 or 0.325 would be silly. Always ask \"is the answer the right size?\"", 13.5)


def dividing(ch):
    f = flow(ch)
    sec(f, "Dividing by a decimal: make it a whole number first", room=330)
    f.p("How many 15p coins fit into £4.50? That's $4.5 \\div 0.15$. Dividing by 0.15 feels "
        "impossible, but in {B:pence} the question is easy: how many 15s in 450?", 14, gap=8)
    y = f.reserve(152)
    pg = f.pg
    for i in range(10):
        pg.circle(L + 36 + i * 22, y + 20, 9, C.BROWN, 1, fillcolor="#e9c98f")
        pg.text(L + 36 + i * 22, y + 15, "15", 7, C.BROWN, align="center", solid=False)
    pg.note(L + 270, y + 8, "... 30 coins make 450p", C.BROWN, 16)
    pg.eq(L + 20, y + 50, r"\frac{4.5}{0.15}", 22)
    pg.text(L + 78, y + 58, "=", 18, C.GREY)
    pg.eq(L + 100, y + 50, r"\frac{4.5\times100}{0.15\times100}=\frac{450}{15}=30", 22)
    pg.note(L + 20, y + 106, "multiply top and bottom by the same number: that's an equivalent "
            "fraction (Chapter 2), so the answer can't change", C.RED, 15, w=W - 20)
    ch.check(sp.Rational(45, 10) / sp.Rational(15, 100), 30)
    rule_box(f, "dividing by a decimal", [
        "Multiply {B:both} numbers by the same power of 10 (10, 100, ...) so that the number you divide "
        "{B:by} becomes a whole number.",
        "Divide normally (short division). The answer is unchanged, because $\\frac{a}{b}=\\frac{10a}{10b}$.",
        "Check by multiplying back: answer × divisor = the number you started with.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    step(f, r"0.36\div0.4=\frac{3.6}{4}=\grn{0.9}", "× 10 top and bottom; check 0.9 × 0.4 = 0.36")
    ch.check(sp.Rational(36, 100) / sp.Rational(4, 10), sp.Rational(9, 10))
    f.p("Dividing by a number {B:less than 1} makes the answer {B:bigger} (lots of small coins "
        "fit). That's the mirror of multiplying on the previous page.", 13.5, C.PURPLE)


def comic_strip(ch):
    f = flow(ch)
    sec(f, "Fraction to decimal: division as a comic strip", room=560)
    rule_box(f, "fraction to decimal", [
        "$\\frac{a}{b}=a\\div b$: divide the top by the bottom.",
        "Write the top as $a.000\\ldots$ and keep dividing; each remainder carries to the next column.",
        "Stop when the remainder is 0 ({B:terminating} decimal) or a remainder repeats "
        "({B:recurring} decimal: the digits repeat from there on).",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    f.p("A fraction is a division (Chapter 2): $\\frac38$ means $3 \\div 8$. Eight people share "
        "3 pizzas. Follow the strip one panel at a time:", 14, gap=8)
    panels = [
        (r"3\div8", "8 into 3? Too small.\nNo whole pizzas each.", "0."),
        (r"30\div8=3\ \text{r}\,6", "cut the 3 pizzas into\ntenths: 30 slices.\n3 each, 6 left.", "0.3"),
        (r"60\div8=7\ \text{r}\,4", "cut the 6 leftover\ntenths into 60\nhundredths. 7 each,\n4 left.", "0.37"),
        (r"40\div8=5\ \text{r}\,0", "40 thousandths.\n5 each, nothing\nleft. STOP.", "0.375"),
    ]
    y = f.reserve(190)
    pg = f.pg
    pw = (W - 18) / 4
    for i, (eq_, cap, ans) in enumerate(panels):
        x = L + i * (pw + 6)
        pg.rect(x, y, pw, 184, C.INK, 1.4, fillcolor="#fffdf7", r=4)
        pg.circle(x + 12, y + 12, 9, C.ORANGE, 1, fillcolor=C.ORANGE)
        pg.text(x + 12, y + 5, str(i + 1), 10, "#ffffff", F.BOLD, align="center")
        pg.eq(x + pw / 2, y + 28, eq_, 14, align="center")
        pg.note(x + 8, y + 58, cap, C.INK, 14)
        pg.rect(x + 14, y + 146, pw - 28, 28, C.GREEN, 1, fillcolor=C.LIGHT[C.GREEN], r=10)
        pg.text(x + pw / 2, y + 151, ans, 15, C.GREEN, F.BOLD, align="center")
        if i < 3:
            pg.arrow(x + pw - 2, y + 160, x + pw + 8, y + 160, C.ORANGE, 1.6, head=4)
    ch.check(sp.Rational(3, 8), sp.Rational(375, 1000))
    f.p("Written the usual compact way (\"bus stop\" division), the same four panels look like "
        "this. The small red numbers are the leftovers carried to the next column:", 14, gap=8)
    y = f.reserve(78)
    pg = f.pg
    X = L + 60
    pg.text(X - 4, y + 34, "8", 22, C.INK, F.BOLD)
    pg.line(X + 18, y + 30, X + 18, y + 62, C.INK, 1.6)
    pg.line(X + 18, y + 30, X + 140, y + 30, C.INK, 1.6)
    xs = [X + 28, X + 46, X + 60, X + 88, X + 116]
    for xx, d, top in zip(xs, "3.000", "0.375"):
        pg.text(xx, y + 34, d, 22, C.INK, F.BOLD)
        pg.text(xx, y, top, 22, C.GREEN, F.BOLD)
    for xx, rem in zip(xs[2:], "364"):
        pg.text(xx - 9, y + 29, rem, 9, C.RED, F.BOLD, solid=False)
    pg.note(L + 220, y + 8, "the carried 3, 6 and 4 are the leftovers\nfrom panels 1, 2 and 3. "
            "Add as many 0s after\nthe dot as you need: 3 = 3.000", C.RED, 15)


def recurring(ch):
    f = flow(ch)
    sec(f, "When the strip never ends: recurring decimals", room=380)
    f.p("Try $\\frac13 = 1 \\div 3$. Panel after panel, the same leftover comes back:", 14, gap=8)
    y = f.reserve(150)
    pg = f.pg
    pw = 118
    for i in range(3):
        x = L + i * (pw + 14)
        pg.rect(x, y, pw, 100, C.INK, 1.3, fillcolor="#fffdf7", r=4)
        pg.eq(x + pw / 2, y + 12, r"10\div3=3\ \text{r}\,1" if i else r"1\div3", 14, align="center")
        pg.note(x + 8, y + 40, "leftover 1 again!" if i else "too small.\nWrite 0.", C.RED, 14)
        pg.text(x + pw / 2, y + 74, ["0.", "0.3", "0.33"][i], 15, C.GREEN, F.BOLD, align="center")
    pg.text(L + 3 * (pw + 14) - 10, y + 36, "...", 26, C.GREY, F.BOLD)
    pg.arrow(L + 2 * (pw + 14) + pw / 2, y + 104, L + (pw + 14) + pw / 2, y + 104, C.PURPLE, 1.6, bend=-0.35)
    pg.note(L + 150, y + 118, "same leftover = same next step, forever", C.PURPLE, 15)
    pg.note(L + 428, y + 10, "0.3333333...\nthe 3s never\nstop", C.GREEN, 15)
    f.p("A decimal that repeats forever is called {B:recurring}. We can't write infinitely many "
        "3s, so we put a {B:dot over the repeating digit}:", 14, gap=6)
    ch.term("recurring decimal", "a decimal whose digits repeat forever, e.g. 0.333...; shown with dots")
    y = f.reserve(90)
    pg = f.pg
    ex = [(r"\tfrac13=0.\dot3", "0.3333..."), (r"\tfrac16=0.1\dot6", "only the 6 repeats: 0.16666..."),
          (r"\tfrac{2}{11}=0.\dot1\dot8", "dots on first and last\nof the repeating block: 0.181818..."),
          (r"\tfrac17=0.\dot14285\dot7", "block 142857 repeats")]
    for i, (e, s) in enumerate(ex):
        x = L + 10 + (i % 2) * 250
        yy = y + (i // 2) * 46
        w, _ = pg.eq(x, yy, e, 18)
        pg.note(x + w + 10, yy, s, C.RED, 13)
    ch.symbol(r"0.\dot3", "nought point three recurring", "the 3 repeats forever")
    ch.check(sp.Rational(1, 6) - sp.Rational(1, 10), sp.Rational(1, 15))
    f.p("Your Lecture 1 slide writes $\\frac13 = 0.3\\dot3 \\approx 0.33$. The wavy equals sign "
        "$\\approx$ means {B:\"is roughly\"}: 0.33 is close to a third, but not exactly it.", 14, gap=8)
    ch.symbol(r"\approx", "is approximately equal to", "close to, but not exactly")
    f.p("{R:Why the lecture says keep fractions when you want exact answers:} "
        "$\\frac13 \\times 3 = 1$ exactly, but $0.33 \\times 3 = 0.99$. The rounding error "
        "sneaks in. Use fractions for algebra, decimals when an approximate answer is fine "
        "(statistics, measurements).", 13.5)
    ch.check(sp.Rational(33, 100) * 3, sp.Rational(99, 100))


def recurring_rules(ch):
    f = flow(ch)
    sec(f, "Which fractions stop, and recurring back to fractions", room=560)
    rule_box(f, "terminating or recurring?", [
        "Simplify the fraction first.",
        "If the denominator's prime factors are {B:only 2s and 5s}, the decimal {B:terminates} (stops). "
        "Reason: it can be scaled to a denominator of 10, 100, 1000, ... (and $10=2\\times5$).",
        "Any other prime factor (3, 7, 11, ...) in the denominator gives a {B:recurring} decimal.",
    ], C.ORANGE)
    rules_table(f, ["Fraction", "Denominator", "Primes", "Decimal"], [
        ["$\\frac{3}{8}$", "$8$", "$2^3$", "{G:terminates}: $0.375$"],
        ["$\\frac{7}{20}$", "$20$", "$2^2\\times5$", "{G:terminates}: $0.35$"],
        ["$\\frac{5}{12}$", "$12$", "$2^2\\times3$", "{R:recurs}: $0.41\\dot6$"],
        ["$\\frac{9}{15}$", "$15\\to5$ after simplifying to $\\frac35$", "$5$", "{G:terminates}: $0.6$"],
    ], widths=[80, 170, 105, 140], color=C.ORANGE, size=12)
    ch.check(sp.Rational(3, 8), sp.Rational(375, 1000))
    ch.check(sp.Rational(7, 20), sp.Rational(35, 100))
    ch.check(sp.Rational(5, 12) - sp.Rational(41, 100), sp.Rational(1, 150))
    ch.check(sp.Rational(9, 15), sp.Rational(6, 10))
    for q, term in ((8, True), (20, True), (12, False), (5, True)):
        ch.check_true((set(sp.primefactors(q)) <= {2, 5}) == term)
    rule_box(f, "recurring decimal to fraction", [
        "Call the decimal $x$. Write out several repeats: $x=0.272727\\ldots$",
        "Multiply by 10 if one digit repeats, 100 if two digits repeat, 1000 if three, ... so the "
        "repeating part lines up: $100x=27.2727\\ldots$",
        "Subtract: the endless tails cancel. $100x-x=27$, so $99x=27$.",
        "Divide and simplify: $x=\\frac{27}{99}=\\frac{3}{11}$.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    ch.check(sp.Rational(27, 99), sp.Rational(3, 11))
    f.p("{b:Example.}  Write $0.\\dot3$ as a fraction.", 14, gap=4)
    step(f, r"x=0.3333\ldots", "one digit repeats: use 10x")
    step(f, r"10x=3.3333\ldots", "× 10")
    step(f, r"10x-x=3\ \Rightarrow\ 9x=3", "the tails .3333... cancel")
    step(f, r"x=\frac39=\grn{\frac13}", "÷ 9, simplify")
    ch.check(sp.Rational(3, 9), sp.Rational(1, 3))
    f.p("{b:Example.}  $0.1\\dot6$ (only the 6 repeats): use $10x$ and $100x$, which both end in "
        "$.666\\ldots$", 14, gap=4)
    step(f, r"100x=16.666\ldots,\quad 10x=1.666\ldots", "both tails are .666...")
    step(f, r"90x=15\ \Rightarrow\ x=\frac{15}{90}=\grn{\frac16}", "subtract, then ÷ 90")
    ch.check(sp.Rational(15, 90), sp.Rational(1, 6))


def rounding(ch):
    f = flow(ch)
    sec(f, "Rounding: which mark on the ruler is nearer?", room=400)
    f.p("A price of £3.47 on a sign that only shows 10p steps: is it nearer £3.40 or £3.50? "
        "Zoom in with the magnifying glass:", 14, gap=8)
    y = f.reserve(104) + 14
    pg = f.pg
    X = numline(pg, L + 30, y + 30, 400, 3.4, 3.5, 10, size=11, fmt=lambda v: f"{v:.2f}")
    pg.line(X(3.45), y + 8, X(3.45), y + 36, C.PURPLE, 1.4, dash=(3, 3))
    pg.note(X(3.45) - 30, y - 12, "halfway: 3.45", C.PURPLE, 14)
    pg.dot(X(3.47), y + 30, 5, C.RED)
    pg.arrow(X(3.47) + 4, y + 22, X(3.5) - 3, y + 22, C.GREEN, 1.8, bend=-0.3)
    pg.note(X(3.5) + 18, y + 12, "nearer 3.5!", C.GREEN, 17)
    ch.check_true(abs(3.47 - 3.5) < abs(3.47 - 3.4))
    f.p("So 3.47 {B:rounded to 1 decimal place} is 3.5. \"Decimal places\" (d.p.) just means "
        "digits after the dot. You don't have to draw a ruler every time. The rule is:", 14, gap=6)
    ch.term("decimal places (d.p.)", "the number of digits after the decimal point")
    ch.term("rounding", "replacing a number with the nearest one on a coarser ruler")
    rule_box(f, "rounding to a number of decimal places", [
        "Find the last digit you are keeping (the {B:cut}).",
        "Look at the {R:next} digit only (the {B:decider}).",
        "Decider {B:5 or more}: increase the kept digit by 1. Decider {B:4 or less}: leave it.",
        "Remove every digit after the cut. Keep end zeros that are inside the required places "
        "(3.96 to 1 d.p. is 4.0, not 4).",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    f.p("{b:Round 2.71828 to 2 decimal places:}", 14, gap=6)
    y = f.reserve(64)
    pg = f.pg
    x = L + 40
    for j, d in enumerate("2.71828"):
        col = C.INK if j <= 3 else (C.RED if j == 4 else C.GREY)
        pg.text(x + j * 20, y + 6, d, 26, col, F.BOLD)
    pg.line(x + 4 * 20 - 2, y, x + 4 * 20 - 2, y + 44, C.ORANGE, 2)
    pg.note(x + 4 * 20 - 30, y + 40, "cut", C.ORANGE, 14)
    pg.note(x + 4 * 20 + 6, y + 40, "decider 8", C.RED, 14)
    pg.arrow(x + 200, y + 22, x + 250, y + 22, C.GREY, 1.4)
    pg.text(x + 262, y + 6, "2.72", 26, C.GREEN, F.BOLD)
    pg.note(x + 350, y + 4, "8 is 5 or more:\nthe 1 bumps up to 2", C.GREEN, 15)
    ch.check(round(2.71828, 2), 2.72)
    f.p("{b:Bumping can ripple:} 3.96 to 1 d.p. The decider 6 bumps the 9 up, 9 + 1 = 10, so it "
        "carries: 3.96 becomes {G:4.0}. Keep the 0: it shows you rounded to 1 d.p.", 13.5, gap=8)
    ch.check(round(3.96, 1), 4.0)
    f.need(300)
    f.p("{b:Going backwards: what could it have been?} A tape measure says a rug is {B:3.5 m} long, "
        "rounded to 1 d.p. The true length isn't exactly 3.5.", 14, gap=8)
    go(f, "On a ruler from 3.4 to 3.6, shade every true length that would round to 3.5. Where does the "
          "shading start, and where does it stop?")
    y = f.reserve(84) + 14
    pg = f.pg
    X = numline(pg, L + 30, y + 30, 400, 3.4, 3.6, 20, size=10, lab_every=5, fmt=lambda v: f"{v:.2f}")
    pg.rect(X(3.45), y + 22, X(3.55) - X(3.45), 16, C.GREEN, 0.8, fillcolor=C.LIGHT[C.GREEN])
    pg.dot(X(3.45), y + 30, 4.5, C.GREEN)
    pg.circle(X(3.55), y + 30, 4.5, C.GREEN, 1.6, fillcolor="#ffffff")
    pg.dot(X(3.5), y + 30, 3, C.INK)
    pg.note(X(3.45) - 70, y - 14, "3.45 rounds UP to 3.5:\nincluded (solid dot)", C.GREEN, 13)
    pg.note(X(3.55) - 20, y - 14, "3.55 rounds to 3.6:\nleft out (open dot)", C.RED, 13)
    ch.check((round(3.45 + 1e-9, 1), round(3.5499, 1), round(3.55 + 1e-9, 1)), (3.5, 3.5, 3.6))
    f.p("So \"3.5 to 1 d.p.\" really means {B:anywhere from 3.45 up to (but not including) 3.55}: half a "
        "step either side of the mark. Those two ends are the {B:lower and upper bounds}.", 14, gap=8)
    ch.term("bounds", "the smallest and largest values a rounded number could really have been")
    f.p("{b:Why it matters: the rug's area.} It's 3.5 m by 2.0 m, both to 1 d.p., so \"7 m²\". But "
        "the true rug is somewhere between the smallest and the biggest possible rectangles:", 14, gap=8)
    y = f.reserve(168)
    pg = f.pg
    s_ = 62
    x0, yb = L + 20, y + 148
    pg.rect(x0, yb - 2.05 * s_, 3.55 * s_, 2.05 * s_, C.RED, 1.2, fillcolor=C.LIGHT[C.RED], dash=(4, 3))
    pg.rect(x0, yb - 1.95 * s_, 3.45 * s_, 1.95 * s_, C.BLUE, 1.4, fillcolor=C.LIGHT[C.BLUE])
    pg.text(x0 + 3.45 * s_ / 2, yb - 1.95 * s_ / 2 - 8, "3.45 × 1.95", 12, C.BLUE, F.BOLD, align="center")
    pg.text(x0 + 3.45 * s_ / 2, yb - 1.95 * s_ / 2 + 8, "= 6.7275 m²", 12, C.BLUE, F.BOLD, align="center")
    pg.note(x0 + 3.55 * s_ + 14, yb - 2.05 * s_ - 2, "biggest: 3.55 × 2.05\n= 7.2775 m² (red edge)", C.RED, 14)
    pg.arrow(x0 + 3.55 * s_ + 40, yb - 2.05 * s_ + 60, x0 + 3.5 * s_, yb - 2.05 * s_ + 72, C.RED, 1.1, head=5)
    pg.note(x0 + 3.55 * s_ + 44, yb - 2.05 * s_ + 40, "the thin red band (0.05 m on\nthe outside, 0.05 m inside the\n"
            "3.5 × 2 mark) is the uncertainty:\nthe true area could be anywhere\nfrom about 6.73 to 7.28 m²", C.INK, 14)
    ch.check_num(3.45 * 1.95, 6.7275, 1e-9)
    ch.check_num(3.55 * 2.05, 7.2775, 1e-9)
    f.p("A thin half-step on each side becomes a whole band of area: about 0.28 m² either way. Multiplying "
        "rounded numbers multiplies their uncertainty too, so don't quote \"7.000 m²\" from measurements "
        "that were only good to 1 d.p.", 14, gap=8)


def bounds(ch):
    f = flow(ch)
    sec(f, "Upper and lower bounds: the rules", room=560)
    rule_box(f, "bounds of a rounded number", [
        "Find the step size of the rounding: 1 d.p. means steps of 0.1, 2 d.p. steps of 0.01, "
        "nearest 10 means steps of 10.",
        "{B:Half a step} either side: lower bound $=$ value $-\\ \\frac12$ step, upper bound $=$ value "
        "$+\\ \\frac12$ step.",
        "Write $\\text{lower}\\le x<\\text{upper}$: the lower bound is included, the upper bound is not "
        "(it would round up).",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    step(f, r"7.8\ (1\text{ d.p.}):\quad 7.75\le x<7.85", "step 0.1, half step 0.05", size=19)
    step(f, r"70\ (\text{nearest }10):\quad 65\le x<75", "step 10, half step 5", size=19)
    ch.check((sp.Rational(78, 10) - sp.Rational(5, 100), sp.Rational(78, 10) + sp.Rational(5, 100)),
             (sp.Rational(775, 100), sp.Rational(785, 100)))
    ch.check((70 - 5, 70 + 5), (65, 75))
    rule_box(f, "bounds of a calculation", [
        "{B:Add:} biggest $=$ upper $+$ upper; smallest $=$ lower $+$ lower. Same idea for $\\times$.",
        "{B:Subtract:} biggest $=$ upper $-$ {R:lower}; smallest $=$ lower $-$ {R:upper}.",
        "{B:Divide:} biggest $=$ upper $\\div$ {R:lower}; smallest $=$ lower $\\div$ {R:upper}. "
        "(A big top over a small bottom gives the biggest answer.)",
    ], C.ORANGE)
    f.p("{b:Example (division).}  A plank is 2.4 m long and is cut into pieces 0.3 m long, both "
        "measured to 1 d.p. Find the bounds for the number of pieces, $2.4\\div0.3$.", 14, gap=4)
    step(f, r"2.35\le\text{plank}<2.45,\qquad 0.25\le\text{piece}<0.35", "half a step (0.05) each side", size=17)
    step(f, r"\text{max}=\frac{2.45}{0.25}=9.8", "upper ÷ lower", size=19)
    step(f, r"\text{min}=\frac{2.35}{0.35}\approx6.71", "lower ÷ upper", size=19)
    ch.check(sp.Rational(245, 100) / sp.Rational(25, 100), sp.Rational(98, 10))
    ch.check_num(2.35 / 0.35, 6.714, tol=0.001)
    f.p("So \"8 pieces\" ($2.4\\div0.3$) could really be anything from about 6.7 to 9.8: rounding in a "
        "division can matter a lot.", 13.5, gap=6)
    ch.check(sp.Rational(24, 10) / sp.Rational(3, 10), 8)


def truncating(ch):
    f = flow(ch)
    sec(f, "Rounding versus chopping (truncating)", room=240)
    f.p("Your Lecture 1 slide says $0.123456789$ \"truncated\" to 2 d.p. is $0.12$. To "
        "{B:truncate} means to just {B:chop off} the extra digits without looking at the decider:",
        14, gap=8)
    ch.term("truncate", "chop off digits after a point without rounding")
    y = f.reserve(80)
    pg = f.pg
    for k, (lab, res, col, why) in enumerate([("round", "0.68", C.GREEN, "decider 8 → bump the 7 up"),
                                              ("truncate", "0.67", C.PURPLE, "just chop after 2 digits")]):
        yy = y + k * 38
        pg.text(L + 20, yy + 4, "0.678", 22, C.INK, F.BOLD)
        pg.note(L + 110, yy + 2, lab, col, 17)
        pg.arrow(L + 170, yy + 16, L + 210, yy + 16, col, 1.4)
        pg.text(L + 220, yy + 4, res, 22, col, F.BOLD)
        pg.note(L + 300, yy + 4, why, col, 15)
    f.p("For 0.123456789 both give 0.12 (the decider is 3, so nothing bumps). They only differ when "
        "the decider is 5 or more. Unless told to truncate, {B:round}.", 13.5)


def sig_figs(ch):
    f = flow(ch)
    sec(f, "Significant figures: a rough ruler and a fine ruler", room=560)
    rule_box(f, "which digits are significant?", [
        "{B:Non-zero digits always count.} 4.72 has 3 s.f.",
        "{B:Leading zeros never count}: zeros before the first non-zero digit only hold place. "
        "$0.0047$ has 2 s.f. (the 4 and the 7).",
        "{B:Zeros between non-zero digits always count}: $3.07$ has 3 s.f.; $2005$ has 4 s.f.",
        "{B:Trailing zeros after the decimal point count}: they were written on purpose to show "
        "precision. $0.030$ has 2 s.f. (the 3 and the final 0); $4.0$ has 2 s.f.",
        "{B:Trailing zeros in a whole number are ambiguous}: $48\\,000$ could be 2, 3, 4 or 5 s.f. Say "
        "which (\"48 000 to 2 s.f.\") when it matters.",
    ], C.ORANGE)
    f.p("A crowd of {B:48,372} people. A newspaper says \"about 50,000\"; a report says "
        "\"48,000\". Both are rounding, just with rulers of different fineness:", 14, gap=8)
    y = f.reserve(172)
    pg = f.pg
    pg.note(L + 30, y, "rough ruler (marks every 10,000): 1 significant figure", C.BLUE, 15)
    X = numline(pg, L + 30, y + 40, 420, 40000, 60000, 2, size=10, fmt=lambda v: f"{int(v):,}")
    pg.dot(X(48372), y + 40, 4.5, C.RED)
    pg.arrow(X(48372), y + 31, X(50000) - 2, y + 31, C.GREEN, 1.6, head=5)
    pg.note(X(50000) + 30, y + 22, "48,372 is nearer 50,000", C.GREEN, 15)
    pg.note(L + 30, y + 86, "fine ruler (marks every 1,000): 2 significant figures", C.ORANGE, 15)
    X2 = numline(pg, L + 30, y + 126, 420, 45000, 50000, 5, size=10, fmt=lambda v: f"{int(v):,}")
    pg.dot(X2(48372), y + 126, 4.5, C.RED)
    pg.arrow(X2(48372), y + 117, X2(48000) + 2, y + 117, C.GREEN, 1.6, head=5)
    pg.note(X2(48000) - 40, y + 146, "nearer 48,000", C.GREEN, 15)
    f.p("{B:Significant figures} (s.f.) count digits {B:from the first non-zero digit}. They say "
        "how fine your ruler is, whatever the size of the number. Zeros at the end of a big number "
        "stay, because they hold the size (48,000 must not shrink to 48).", 14, gap=8)
    ch.term("significant figures (s.f.)", "digits counted from the first non-zero digit; how precise a number is")
    f.p("{b:Small numbers:} the zeros at the front are only place-holders, so they don't count. "
        "Your Lecture 1 table, with the counting shown:", 14, gap=6)
    y = f.reserve(112)
    pg = f.pg
    x = L + 40
    for j, d in enumerate("0.123456789"):
        col = C.GREY if j < 2 else C.INK
        pg.text(x + j * 16, y, d, 20, col, F.BOLD)
        if j >= 2:
            pg.text(x + j * 16 + 5, y + 26, str(j - 1), 9, C.ORANGE, F.BOLD, solid=False)
    pg.note(x - 10, y + 36, "leading 0s: not counted", C.GREY, 13)
    rows = [("1 s.f.", "0.1"), ("2 s.f.", "0.12"), ("3 s.f.", "0.123"), ("4 s.f.", "0.1235")]
    for i, (a, b) in enumerate(rows):
        pg.text(L + 270, y + i * 24, a, 13, C.ORANGE, F.BOLD)
        pg.text(L + 330, y + i * 24, b, 13, C.GREEN, F.BOLD)
    pg.note(L + 400, y + 66, "4 s.f.: decider 5,\nso 4 bumps to 5!", C.RED, 14)
    ch.check(sp.Float(0.123456789, 20).round(4), sp.Float(0.1235, 20).round(4))
    f.p("{R:Heads-up:} the slide table shows 0.1234 for 4 s.f.; that is the {B:truncated} value. "
        "Rounded properly it's 0.1235, because the next digit is 5.", 13.5, gap=8)
    f.p("{b:One more:} 0.004 72 to 2 s.f. Skip the zeros, the first significant digit is 4. Keep "
        "4 and 7, decider 2: {G:0.0047}.", 13.5, gap=10)
    ch.check(sp.Float(0.00472).round(4), sp.Float(0.0047).round(4))
    f.need(300)
    rule_box(f, "rounding to n significant figures", [
        "Start counting at the {B:first non-zero digit}. Count $n$ digits (zeros in between count). "
        "That is the cut.",
        "Round at the cut using the decider, as for decimal places.",
        "{B:Whole-number part:} replace the dropped digits with zeros to keep the size "
        "($48\\,372\\to48\\,000$). {B:After the point:} just drop them.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    rules_table(f, ["Number", "s.f.", "Why"], [
        ["$3.07$", "3", "the 0 is between 3 and 7: counts"],
        ["$0.030$", "2", "leading zeros don't count; the final 0 after the point does"],
        ["$0.0405$", "3", "4, 0, 5 (the zero between counts)"],
        ["$12.50$", "4", "trailing zero after the point counts"],
        ["$5200$", "2, 3 or 4", "trailing zeros in a whole number: ambiguous"],
    ], widths=[95, 80, 320], color=C.ORANGE, size=12)
    step(f, r"3.0496\to\grn{3.05}\ (3\text{ s.f.})", "cut after 3, 0, 4; decider 9: 4 → 5", size=19)
    step(f, r"2045\to\grn{2000}\ (2\text{ s.f.})", "keep 2, 0; decider 4; refill with zeros", size=19)
    step(f, r"0.06996\to\grn{0.0700}\ (3\text{ s.f.})", "6, 9, 9; decider 6 ripples: keep both zeros", size=19)
    ch.check(sp.Float("3.0496").round(2), sp.Float("3.05").round(2))
    ch.check(round(2045, -2), 2000)
    ch.check(round(0.06996, 4), 0.07)


def estimating(ch):
    f = flow(ch)
    sec(f, "Estimating: round everything to 1 s.f. to check", room=240)
    f.p("Before trusting a calculator, round each number to 1 significant figure and do the easy "
        "sum in your head. If the real answer is nowhere near, you pressed a wrong button.", 14, gap=8)
    step(f, r"4.87\times21.3", "the real question")
    step(f, r"\approx 5\times20", "1 s.f. each: 4.87 → 5, 21.3 → 20")
    step(f, r"=100", "easy!", color=C.GREEN)
    f.p("The calculator says 103.731. Close to 100 ✓. If it said 1037.31 you'd know a dot went "
        "astray.", 13.5)
    ch.check_num(4.87 * 21.3, 103.731)


def missing(ch):
    f = flow(ch)
    sec(f, "Find the unknown", room=480)
    rule_box(f, "finding an unknown decimal", [
        "Undo the operation with its inverse ($\\times$ with $\\div$, $+$ with $-$), then use the decimal "
        "rules above.",
        "For \"it was rounded to ...\" questions, the unknown is a {B:range}: give the lower and upper "
        "bounds.",
        "Check by putting the answer back.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    f.p("{b:Example.}  $?\\times0.4=0.36$", 14, gap=4)
    step(f, r"?=0.36\div0.4=3.6\div4=\grn{0.9}", "undo × 0.4; × 10 top and bottom")
    step(f, r"0.9\times0.4=0.36\ \checkmark", "9 × 4 = 36, 2 places")
    ch.check(sp.Rational(36, 100) / sp.Rational(4, 10), sp.Rational(9, 10))
    f.p("{b:Example.}  $?+2.75=5.1$", 14, gap=4)
    step(f, r"?=5.10-2.75=\grn{2.35}", "undo + with −; pad 5.1 to 5.10")
    ch.check(sp.Rational(51, 10) - sp.Rational(275, 100), sp.Rational(235, 100))
    f.p("{b:Example.}  A length rounded to 1 d.p. is 2.7 cm. What could it really be?", 14, gap=4)
    step(f, r"2.7-0.05=2.65,\quad 2.7+0.05=2.75", "half of the 0.1 step each side")
    step(f, r"\grn{2.65\le x<2.75}", "2.75 itself would round to 2.8")
    ch.check((sp.Rational(27, 10) - sp.Rational(5, 100), sp.Rational(27, 10) + sp.Rational(5, 100)),
             (sp.Rational(265, 100), sp.Rational(275, 100)))


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Place value", None, "each column is $\\frac{1}{10}$ of the one to its left: tenths, hundredths, "
         "thousandths"),
        ("Compare", None, "line up the points, pad with zeros, compare from the left"),
        ("Decimal to fraction", r"0.abc=\frac{abc}{1000}", "one 0 per decimal place, then simplify"),
        ("Fraction to decimal", r"\frac{a}{b}=a\div b", None),
        ("+ and −", None, "line up the points; fill gaps with 0"),
        ("× and ÷ by 10, 100, 1000", None, "digits move 1, 2, 3 places (left for ×, right for ÷)"),
        ("Multiply", None, "multiply without points; answer has as many decimal places as both "
         "numbers together"),
        ("Divide", r"\frac{a}{b}=\frac{10a}{10b}", "scale both until the divisor is whole"),
        ("Terminating?", None, "simplified denominator has only the primes 2 and 5"),
        ("Recurring to fraction", r"x=0.\dot2\dot7:\ 100x-x=27\Rightarrow x=\frac{27}{99}",
         "multiply by 10, 100, ... (one 0 per repeating digit), subtract"),
        ("Rounding", None, "decider 5 or more: round up; 4 or less: leave"),
        ("Significant figures", None, "count from the first non-zero digit; zeros between count; "
         "trailing zeros after the point count; leading zeros never"),
        ("Bounds", r"\text{value}-\tfrac12\text{step}\le x<\text{value}+\tfrac12\text{step}", None),
        ("Bounds of a ÷", r"\max\frac{a}{b}=\frac{a_{\max}}{b_{\min}},\quad \min\frac{a}{b}=\frac{a_{\min}}{b_{\max}}",
         None),
        ("Estimate", None, "round every number to 1 s.f. first"),
    ], C.ORANGE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Magnifying glass: your turn", fresh=True)
    f.p("Answers are at the bottom of each group, small and grey. Cover them first!", 13.5, gap=10)
    groups = [
        ("Reading and comparing", ["What is the 6 worth in 2.068?", "Which is bigger: 0.7 or 0.69?",
                                   "Put in order: 0.3, 0.33, 0.303", "Write 0.35 as a fraction (simplest)"],
         "1. 6 hundredths   2. 0.7   3. 0.3, 0.303, 0.33   4. 7/20"),
        ("Working with them", ["2.4 + 13.75", "10 - 3.62", "0.6 × 0.7", "1.2 × 3.5", "7.2 ÷ 0.08"],
         "5. 16.15   6. 6.38   7. 0.42   8. 4.2   9. 90"),
        ("Fraction to decimal", ["5/8", "2/3", "7/20"], "10. 0.625   11. 0.6 recurring   12. 0.35"),
        ("Rounding", ["6.748 to 1 d.p.", "6.748 to 2 d.p.", "0.03049 to 2 s.f.", "72,650 to 2 s.f.",
                      "Estimate 9.8 × 51"],
         "13. 6.7   14. 6.75   15. 0.030   16. 73,000   17. 10 × 50 = 500"),
        ("Significant figures, recurring, bounds", ["How many s.f. in 3.07? In 0.030? In 0.0405?",
                                                    "Round 0.04096 to 3 s.f.", "Write 0.4 recurring (0.444...) as a fraction",
                                                    "Does 7/40 terminate? Does 5/6?",
                                                    "Bounds of 12.6 (rounded to 1 d.p.)",
                                                    "a = 8 and b = 2, both to the nearest whole number. Largest a ÷ b?"],
         "18. 3, 2, 3   19. 0.0410 (4, 0, 9; decider 6 bumps the 9)   20. 4/9 (10x − x = 4)   21. yes (40 = 2³ × 5); no (6 has a 3)   "
         "22. 12.55 ≤ x < 12.65   23. 8.5 ÷ 1.5 = 5.67 (upper ÷ lower)"),
        ("Find the unknown", ["? × 0.4 = 0.36", "? − 1.8 = 2.65", "? ÷ 0.2 = 15",
                              "A number rounded to 1 d.p. is 4.3. What are its bounds?",
                              "A number rounded to 2 s.f. is 0.56. What are its bounds?"],
         "24. 0.9 (0.36 ÷ 0.4 = 3.6 ÷ 4)   25. 4.45 (2.65 + 1.8)   26. 3 (15 × 0.2)   "
         "27. 4.25 ≤ x < 4.35 (± 0.05)   28. 0.555 ≤ x < 0.565 (± 0.005)"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 40)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14, w=W - 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(sp.Rational(35, 100), sp.Rational(7, 20))
    ch.check(sp.Rational(24, 10) + sp.Rational(1375, 100), sp.Rational(1615, 100))
    ch.check(10 - sp.Rational(362, 100), sp.Rational(638, 100))
    ch.check(sp.Rational(6, 10) * sp.Rational(7, 10), sp.Rational(42, 100))
    ch.check(sp.Rational(12, 10) * sp.Rational(35, 10), sp.Rational(42, 10))
    ch.check(sp.Rational(72, 10) / sp.Rational(8, 100), 90)
    ch.check(sp.Rational(5, 8), sp.Rational(625, 1000))
    ch.check(sp.Rational(7, 20), sp.Rational(35, 100))
    ch.check(round(6.748, 1), 6.7)
    ch.check(round(6.748, 2), 6.75)
    ch.check_true(abs(0.03049 - 0.030) < 0.0005)
    ch.check(round(72650, -3), 73000)
    ch.check_num(round(0.04096, 4), 0.0410, tol=1e-9)
    ch.check(10 * sp.Rational(4, 9) - sp.Rational(4, 9), 4)
    ch.check_true(set(sp.primefactors(40)) <= {2, 5} and not set(sp.primefactors(6)) <= {2, 5})
    ch.check((sp.Rational(1255, 100), sp.Rational(1265, 100)),
             (sp.Rational(126, 10) - sp.Rational(5, 100), sp.Rational(126, 10) + sp.Rational(5, 100)))
    ch.check_num(8.5 / 1.5, 5.67, tol=0.005)
    ch.check(sp.Rational(36, 100) / sp.Rational(4, 10), sp.Rational(9, 10))
    ch.check(sp.Rational(265, 100) + sp.Rational(18, 10), sp.Rational(445, 100))
    ch.check(15 * sp.Rational(2, 10), 3)
    ch.check((sp.Rational(43, 10) - sp.Rational(5, 100), sp.Rational(43, 10) + sp.Rational(5, 100)),
             (sp.Rational(425, 100), sp.Rational(435, 100)))
    ch.check((sp.Rational(56, 100) - sp.Rational(5, 1000), sp.Rational(56, 100) + sp.Rational(5, 1000)),
             (sp.Rational(555, 1000), sp.Rational(565, 1000)))


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    cutting(ch)
    zooming(ch)
    comparing(ch)
    as_fractions(ch)
    add_sub(ch)
    sliding(ch)
    multiplying(ch)
    dividing(ch)
    comic_strip(ch)
    recurring(ch)
    recurring_rules(ch)
    rounding(ch)
    bounds(ch)
    truncating(ch)
    sig_figs(ch)
    estimating(ch)
    missing(ch)
    summary(ch)
    your_turn(ch)
