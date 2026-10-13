"""Chapter 1 - Arithmetic of whole numbers. Sticks and bundles, a lift, getting dressed,
rectangles of dots and blinking traffic lights."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step,
                         title_block)

ORDER = 1
NUM = 1
TITLE = "Arithmetic of whole numbers"
SHORT = "Whole numbers"
SLUG = "Whole-Numbers"
ACCENT = C.ORANGE
REQUIRES = ["reading-maths", "equals-sign", "multiplication-notation", "brackets-first"]
INTRODUCES = ["place-value", "addition", "subtraction", "multiplication", "division", "remainder",
              "negative-numbers", "order-of-operations", "factors", "multiples", "primes",
              "prime-factorisation", "hcf", "lcm"]

STICK = "#b07a3a"


def icon(pg, x, y):
    for i in range(4):
        pg.line(x + 3 + i * 4, y + 1, x + 3 + i * 4, y + 17, STICK, 2)
    pg.line(x, y + 9, x + 18, y + 9, C.RED, 1.6)


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def sticks(pg, x, y, n, h=34, gap=6, col=STICK):
    for i in range(n):
        pg.line(x + i * gap, y, x + i * gap, y + h, col, 2.4)


def bundle(pg, x, y, h=34, col=STICK):
    for i in range(10):
        pg.line(x + i * 2.4, y, x + i * 2.4, y + h, col, 1.6)
    pg.line(x - 2, y + h / 2, x + 24, y + h / 2, C.RED, 2)


def crate(pg, x, y, s=34):
    pg.rect(x, y, s, s, C.BROWN, 1.6, fillcolor="#e8cfa8", r=3)
    for i in range(1, 4):
        pg.line(x + i * s / 4, y + 3, x + i * s / 4, y + s - 3, "#b58f5c", 0.8)
    pg.text(x + s / 2, y + s / 2 - 7, "100", 9, C.BROWN, F.BOLD, align="center")


def dots(pg, x, y, rows, cols, gap=12, col=C.ORANGE, r=3.4):
    for i in range(rows):
        for j in range(cols):
            pg.dot(x + j * gap, y + i * gap, r, col)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 1, "Arithmetic of whole numbers", "the four things you can do to numbers, "
                     "done with sticks, lifts and dots", C.ORANGE, "#fff8f0")
    y = 220
    for i in range(3):
        crate(pg, 90 + i * 44, y, 40)
    for i in range(4):
        bundle(pg, 250 + i * 32, y + 3, 36)
    sticks(pg, 390, y + 3, 7, 36, 7)
    pg.note(110, y + 50, "3 hundreds", C.BROWN, 18)
    pg.note(255, y + 50, "4 tens", C.RED, 18)
    pg.note(390, y + 50, "7 ones", STICK, 18)
    pg.text(297, y + 90, "347", 54, C.INK, F.BOLD, align="center")
    f = ch.flow(top=420)
    f.p("Everything in maths is built on four actions: {o:adding}, {o:taking away}, {o:multiplying} and "
        "{o:dividing}. You already do these every day with money. This chapter slows them right "
        "down so you can {B:see} what is happening inside them, because every later chapter, "
        "from fractions to calculus, is these four actions in disguise.", 14, gap=10)
    f.p("It also covers negative numbers, the order you do things in (the famous BODMAS), and the "
        "{b:factor} and {b:multiple} ideas that fractions (Chapter 2) depend on.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 1} {y:(mathematical writing and BODMAS).}", 12.5)


def place_value(ch):
    f = flow(ch)
    sec(f, "Numbers are bundles of ten")
    f.p("Why does 347 mean three hundred and forty-seven? Imagine counting sticks. Every time you "
        "reach {B:ten sticks}, you tie them into a {B:bundle}. Every time you have {B:ten bundles}, "
        "you pack them in a {B:crate} (a crate holds 100 sticks).", 14, gap=10)
    y = f.reserve(90)
    pg = f.pg
    cols = [("crates (hundreds)", C.BROWN), ("bundles (tens)", C.RED), ("loose sticks (ones)", STICK)]
    for i, (lab, col) in enumerate(cols):
        x0 = L + 20 + i * 165
        pg.rect(x0, y, 150, 80, col, 1.3, r=8)
        pg.note(x0 + 75, y + 56, lab, col, 15, align="center")
    for i in range(3):
        crate(pg, L + 30 + i * 44, y + 10, 36)
    for i in range(4):
        bundle(pg, L + 200 + i * 32, y + 12, 34)
    sticks(pg, L + 360, y + 12, 7, 34, 8)
    f.p("A written number is just a report of what is in each box, in order: {w:3} crates, "
        "{r:4} bundles, {o:7} loose sticks is written {w:3}{r:4}{o:7}. The {B:position} of a digit "
        "tells you its size. That is called {B:place value}.", 14, gap=10)
    ch.term("place value", "the position of a digit tells you its size: ones, tens, hundreds...")
    ch.term("digit", "one of the ten symbols 0 1 2 3 4 5 6 7 8 9")
    f.p("{b:Zero is a place-holder.} 307 means 3 crates, {B:no} bundles, 7 sticks. Without the 0 "
        "you'd write 37, which is a completely different number. Zero says \"this box is empty\".",
        14, gap=10)
    f.p("{b:A car mileage counter} works the same way. When the ones wheel goes past 9, it rolls "
        "back to 0 and pushes the tens wheel on by one:", 14, gap=8)
    y = f.reserve(60)
    pg = f.pg
    for k, num in enumerate(["0 1 9", "0 2 0"]):
        x0 = L + 40 + k * 250
        for j, d in enumerate(num.split()):
            pg.rect(x0 + j * 40, y, 36, 46, C.INK, 1.6, fillcolor="#222222", r=4)
            pg.text(x0 + j * 40 + 18, y + 10, d, 22, "#ffffff", F.BOLD, align="center")
    pg.arrow(L + 180, y + 23, L + 280, y + 23, C.ORANGE, 1.6)
    pg.note(L + 190, y - 4, "+1 mile", C.ORANGE, 16)
    f.p("19 plus 1: the ones wheel rolls from 9 to 0 and the tens wheel clicks from 1 to 2. That "
        "\"roll over and push the next one\" is exactly what {B:carrying} means in adding.", 13.5)


def adding(ch):
    f = flow(ch)
    sec(f, "Adding: put the piles together, re-bundle")
    f.p("Work out $47+38$. Put 47 sticks and 38 sticks side by side, each in its columns:", 14, gap=8)
    y = f.reserve(120)
    pg = f.pg
    pg.text(L, y + 12, "47", 18, C.INK, F.BOLD)
    pg.text(L, y + 62, "38", 18, C.INK, F.BOLD)
    for i in range(4):
        bundle(pg, L + 50 + i * 30, y + 5, 32)
    sticks(pg, L + 220, y + 5, 7, 32, 8)
    for i in range(3):
        bundle(pg, L + 50 + i * 30, y + 55, 32)
    sticks(pg, L + 220, y + 55, 8, 32, 8)
    pg.note(L + 340, y + 5, "ones: 7 + 8 = 15 loose sticks.\nThat's more than ten, so tie\n"
            "ten of them into a new bundle:\n15 = 1 bundle and 5 sticks", C.RED, 15)
    f.p("{b:Step by step, column by column, starting with the ones:}", 14, gap=6)
    y = f.reserve(150)
    pg = f.pg
    X = L + 60
    pg.text(X + 20, y + 0, "1", 13, C.RED, F.BOLD)
    pg.text(X, y + 14, "4 7", 26, C.INK, F.BOLD)
    pg.text(X - 26, y + 48, "+", 26, C.INK, F.BOLD)
    pg.text(X, y + 48, "3 8", 26, C.INK, F.BOLD)
    pg.line(X - 30, y + 84, X + 60, y + 84, C.INK, 1.8)
    pg.text(X, y + 90, "8 5", 26, C.GREEN, F.BOLD)
    pg.note(X + 110, y + 10, "1. ones column: 7 + 8 = 15. Write the 5, and carry\n"
            "    the new bundle (1 ten) over to the tens column.", C.RED, 15)
    pg.note(X + 110, y + 60, "2. tens column: 4 + 3 = 7 bundles, plus the 1\n"
            "    carried bundle = 8 bundles. Write 8.", C.RED, 15)
    pg.note(X + 110, y + 105, "3. So 47 + 38 = 85 (8 bundles and 5 sticks).", C.GREEN, 16)
    ch.check(47 + 38, 85)
    f.p("{h:Carrying is just re-bundling:} ten ones become one ten, ten tens become one hundred. "
        "Adding also doesn't care about order: $47+38 = 38+47$.", 13.5, C.BROWN)


def subtracting(ch):
    f = flow(ch)
    sec(f, "Taking away: sometimes you must open a bundle")
    f.p("Work out $52-17$. Start with 52: five bundles and 2 loose sticks. You need to take away "
        "7 loose sticks... but you only have 2!", 14, gap=8)
    y = f.reserve(140)
    pg = f.pg
    for i in range(5):
        bundle(pg, L + 20 + i * 30, y + 5, 32, col=STICK if i < 4 else C.ORANGE)
    sticks(pg, L + 180, y + 5, 2, 32, 8)
    pg.arrow(L + 230, y + 22, L + 280, y + 22, C.GREY, 1.4)
    for i in range(4):
        bundle(pg, L + 290 + i * 30, y + 5, 32)
    sticks(pg, L + 420, y + 5, 12, 32, 6, col=C.ORANGE)
    pg.note(L + 290, y + 42, "open one bundle: now 4 bundles\nand 2 + 10 = 12 loose sticks", C.ORANGE, 15)
    pg.note(L + 20, y + 42, "52 = 5 bundles, 2 sticks", C.GREY, 15)
    y2 = y + 90
    X = L + 60
    pg.text(X - 4, y2 - 12, "4", 13, C.ORANGE, F.BOLD)
    pg.text(X + 18, y2 - 12, "12", 13, C.ORANGE, F.BOLD)
    pg.text(X, y2 + 2, "5 2", 24, C.INK, F.BOLD)
    pg.line(X - 2, y2 + 4, X + 14, y2 + 24, C.ORANGE, 1.3)
    f.gap(0)
    y = f.reserve(80)
    pg.text(X - 26, y - 14, "-", 24, C.INK, F.BOLD)
    pg.text(X, y - 14, "1 7", 24, C.INK, F.BOLD)
    pg.line(X - 30, y + 18, X + 60, y + 18, C.INK, 1.8)
    pg.text(X, y + 24, "3 5", 24, C.GREEN, F.BOLD)
    pg.note(X + 110, y - 50, "1. ones: 2 - 7? Not enough. Open a bundle:\n"
            "    the 5 tens become 4, the 2 ones become 12.", C.ORANGE, 15)
    pg.note(X + 110, y - 4, "2. ones: 12 - 7 = 5.   tens: 4 - 1 = 3.", C.RED, 15)
    pg.note(X + 110, y + 24, "3. So 52 - 17 = 35.", C.GREEN, 16)
    ch.check(52 - 17, 35)
    f.p("{G:Check by adding back:} $35 + 17 = 52$. ✓  Taking away is the undo button for adding.",
        13.5, gap=8)
    f.p("{R:Order matters here!}  $52-17$ is not the same as $17-52$. (The second one goes below "
        "zero, which is the next idea.)", 13.5)


def negatives(ch):
    f = flow(ch)
    sec(f, "Below zero: the lift in a building", room=520)
    f.p("A lift has floors above the ground (1, 2, 3...) and basement floors below it. Call the "
        "ground floor 0 and the basement floors {B:negative}: $-1$, $-2$, $-3$ (said \"minus one\" or "
        "\"negative one\").", 14, gap=8)
    y = f.reserve(300)
    pg = f.pg
    bx = L + 40
    for k, fl in enumerate(range(5, -5, -1)):
        yy = y + k * 28
        col = C.BLUE if fl > 0 else (C.GREEN if fl == 0 else C.RED)
        pg.rect(bx, yy, 70, 26, col, 1.2, fillcolor=C.LIGHT[col])
        pg.text(bx + 35, yy + 5, str(fl) if fl <= 0 else f"{fl}", 13, col, F.BOLD, align="center")
    pg.note(bx + 80, y + 145, "ground floor = 0", C.GREEN, 15)
    pg.line(bx - 20, y + 140, bx + 180, y + 140, C.GREEN, 1.2, dash=(4, 3))
    ex = [("start at 2, go DOWN 5 floors", r"2-5=-3", 2, -3),
          ("start at -3, go UP 4 floors", r"-3+4=1", -3, 1),
          ("start at -1, go DOWN 2 floors", r"-1-2=-3", -1, -3)]
    for i, (say, lat, a, b) in enumerate(ex):
        yy = y + 10 + i * 90
        pg.eq(L + 280, yy, lat, 22)
        pg.note(L + 280, yy + 30, say, C.INK, 15)
        ya = y + (5 - a) * 28 + 13
        yb = y + (5 - b) * 28 + 13
        xoff = bx + 76 + i * 16
        pg.arrow(xoff, ya, xoff, yb, [C.ORANGE, C.PURPLE, C.TEAL][i], 1.6, bend=0.25 if a > b else -0.25)
    ch.check(2 - 5, -3)
    ch.check(-3 + 4, 1)
    ch.check(-1 - 2, -3)
    f.p("{B:Adding} a positive number moves you {B:up}; {B:taking away} a positive number moves you "
        "{B:down}. The rules below cover every other case. The {B:size} of a number is how far it is "
        "from 0, ignoring the sign: the size of $-7$ is 7.", 14, gap=10)
    ch.term("integer", "a whole number that may be positive, negative or zero: ..., -2, -1, 0, 1, 2, ...")
    rule_box(f, "adding and subtracting with negative numbers", [
        "{B:Adding a negative is the same as subtracting:} $a+(-b)=a-b$.  E.g. $7+(-3)=7-3=4$.",
        "{B:Subtracting a negative is the same as adding:} $a-(-b)=a+b$.  E.g. $5-(-2)=5+2=7$.",
        "{B:Two signs, different:} subtract the smaller size from the bigger size, and give the answer "
        "the {B:sign of the number with the bigger size}.  E.g. $-9+4=-5$ (9 is bigger, it was "
        "negative); $-3+8=5$ (8 is bigger, it was positive).",
        "{B:Both negative:} add the sizes, the answer is negative.  E.g. $-4-6=-10$, "
        "$-4+(-6)=-10$.",
    ], C.ORANGE)
    step(f, r"7+(-3)=7-3=\grn{4}", "+ (−) becomes −")
    step(f, r"-9+4=\grn{-5}", "sizes 9 and 4: 9 − 4 = 5; the 9 was negative")
    step(f, r"-2-(-5)=-2+5=\grn{3}", "− (−) becomes +, then sizes 5 − 2 = 3, sign of the 5")
    step(f, r"-4+(-6)=-4-6=\grn{-10}", "both negative: add sizes, keep −")
    ch.check(7 + (-3), 4)
    ch.check(-9 + 4, -5)
    ch.check(-3 + 8, 5)
    ch.check(-2 - (-5), 3)
    ch.check(-4 + (-6), -10)
    f.p("{b:Why subtracting a negative adds.}  Think of money: $-2$ is a debt of £2. If someone "
        "{B:takes away} a debt you owe, you are {B:better off} by £2, so $5-(-2)=7$. Two minus signs "
        "{B:next to each other} make a plus.", 14, C.INK)


def neg_multiply(ch):
    f = flow(ch)
    sec(f, "Multiplying and dividing negatives", room=520)
    rule_box(f, "signs when multiplying and dividing", [
        "Work out the sizes as usual, then fix the sign.",
        "{G:Same signs give a positive answer:} $(+)\\times(+)=+$ and $(-)\\times(-)=+$.",
        "{R:Different signs give a negative answer:} $(+)\\times(-)=-$ and $(-)\\times(+)=-$.",
        "Division follows exactly the same sign rules as multiplication.",
        "Several numbers: count the minus signs. {B:Even} count gives $+$, {B:odd} count gives $-$. "
        "E.g. $(-2)\\times(-3)\\times(-1)=-6$ (three minus signs).",
    ], C.ORANGE)
    ch.check((-2) * (-3) * (-1), -6)
    rules_table(f, ["Signs", "×", "÷", "Answer"], [
        ["$+$ and $+$", "$3\\times4=12$", "$12\\div3=4$", "{G:positive}"],
        ["$+$ and $-$", "$3\\times(-4)=-12$", "$12\\div(-3)=-4$", "{R:negative}"],
        ["$-$ and $+$", "$(-3)\\times4=-12$", "$-12\\div3=-4$", "{R:negative}"],
        ["$-$ and $-$", "$(-3)\\times(-4)=12$", "$-12\\div(-3)=4$", "{G:positive}"],
    ], widths=[100, 150, 145, 100], color=C.ORANGE, size=12)
    for a, b in ((3, -4), (-3, 4), (-3, -4)):
        ch.check(a * b, 12 if (a < 0) == (b < 0) else -12)
    for a, b in ((12, -3), (-12, 3), (-12, -3)):
        ch.check(sp.Rational(a, b), 4 if (a < 0) == (b < 0) else -4)
    f.p("{b:Why is negative times negative positive?} Watch a pattern. Each line below multiplies "
        "by one less than the line above, so the answer changes by 3 each time:", 14, gap=8)
    rows = [(3, 2), (3, 1), (3, 0), (3, -1), (3, -2)]
    rows2 = [(-3, 2), (-3, 1), (-3, 0), (-3, -1), (-3, -2)]
    y = f.reserve(170)
    pg = f.pg
    for k, ((a, b), (c, d)) in enumerate(zip(rows, rows2)):
        yy = y + k * 32
        pg.eq(L + 30, yy, r"%d\times %s=%s" % (a, f"({b})" if b < 0 else b, a * b), 19,
              C.RED if a * b < 0 else C.INK)
        pg.eq(L + 290, yy, r"%d\times %s=%s" % (c, f"({d})" if d < 0 else d, c * d), 19,
              C.GREEN if (c < 0 and d < 0) else (C.RED if c * d < 0 else C.INK))
    pg.note(L + 160, y + 10, "down 3\neach time", C.GREY, 14)
    pg.note(L + 420, y + 10, "UP 3\neach time", C.GREY, 14)
    pg.arrow(L + 200, y + 50, L + 200, y + 150, C.GREY, 1.2)
    pg.arrow(L + 460, y + 50, L + 460, y + 150, C.GREY, 1.2)
    f.p("On the left the answers go 6, 3, 0, then keep going down: $-3$, $-6$. On the right they go "
        "$-6$, $-3$, 0, then keep going {B:up}: 3, 6. The pattern forces it: a negative times a "
        "negative is {G:positive}.", 14, gap=8)
    f.p("{R:Careful:} the \"two minuses make a plus\" rule for × and ÷ is about {B:two numbers}. "
        "For adding it is different: $-3+(-4)=-7$, not $+7$.", 13.5)
    ch.check(-3 + (-4), -7)


def multiplying(ch):
    f = flow(ch)
    sec(f, "Multiplying: rows of dots", room=420)
    f.p("$4\\times6$ means \"4 lots of 6\". Draw it as 4 rows of 6 dots: a rectangle.", 14, gap=6)
    y = f.reserve(70)
    pg = f.pg
    dots(pg, L + 40, y + 6, 4, 6, 12)
    pg.note(L + 120, y + 4, "4 rows of 6 = 24 dots.\nTurn the page sideways and it's\n6 rows of 4: "
            "still 24. Order doesn't matter.", C.ORANGE, 15)
    ch.check(4 * 6, 24)
    f.p("{b:Bigger numbers: split the rectangle.}  $23\\times14$ is a rectangle 23 wide and 14 tall. "
        "Split 23 into 20 + 3 and 14 into 10 + 4. Now it's four easy rectangles (the {B:grid method}):",
        14, gap=8)
    y = f.reserve(170)
    pg = f.pg
    x0, y0, sc = L + 60, y + 20, 5.2
    wA, wB, hA, hB = 20 * sc, 3 * sc * 2.2, 10 * sc * 1.6, 4 * sc * 1.6
    cells = [(x0, y0, wA, hA, "20 x 10\n= 200", C.BLUE), (x0 + wA, y0, wB, hA, "3x10\n=30", C.ORANGE),
             (x0, y0 + hA, wA, hB, "20 x 4 = 80", C.GREEN), (x0 + wA, y0 + hA, wB, hB, "12", C.PURPLE)]
    for (cx, cy, cw, chh, lab, col) in cells:
        pg.rect(cx, cy, cw, chh, col, 1.4, fillcolor=C.LIGHT[col])
        pg.text(cx + cw / 2, cy + chh / 2 - 8 * lab.count("\n") - 7, lab, 11, col, F.BOLD, align="center")
    pg.text(x0 + wA / 2, y0 - 16, "20", 12, C.INK, F.BOLD, align="center")
    pg.text(x0 + wA + wB / 2, y0 - 16, "3", 12, C.INK, F.BOLD, align="center")
    pg.text(x0 - 22, y0 + hA / 2 - 7, "10", 12, C.INK, F.BOLD)
    pg.text(x0 - 16, y0 + hA + hB / 2 - 7, "4", 12, C.INK, F.BOLD)
    pg.note(L + 290, y + 20, "Add the four pieces:\n200 + 30 + 80 + 12 = 322", C.RED, 18)
    ch.check(23 * 14, 322)
    pg.eq(L + 290, y + 80, r"23\times14=\grn{322}", 24)
    rule_box(f, "laws of multiplication (and which operations can be swapped)", [
        "{B:Commutative:} order does not matter for $\\times$ and $+$: $a\\times b=b\\times a$, "
        "$a+b=b+a$. {R:It does matter for $-$ and $\\div$:} $7-3\\ne3-7$, $20\\div4\\ne4\\div20$.",
        "{B:Distributive law:} $a(b+c)=ab+ac$. Multiplying a sum means multiplying {B:each part} and "
        "adding. The grid method above is this law: $23\\times14=23\\times10+23\\times4=230+92=322$.",
        "Also works with minus: $a(b-c)=ab-ac$. E.g. $6\\times19=6\\times20-6\\times1=114$.",
    ], C.ORANGE)
    ch.check(23 * 10 + 23 * 4, 322)
    ch.check(6 * 20 - 6 * 1, 6 * 19)
    ch.check_true(7 - 3 != 3 - 7 and sp.Rational(20, 4) != sp.Rational(4, 20))
    ch.term("distributive law", "a(b + c) = ab + ac: multiply each part of the bracket")
    ch.term("commutative", "order doesn't matter: a + b = b + a and a × b = b × a (not true for − or ÷)")
    f.p("{h:This \"split into easy rectangles\" picture comes back in Chapter 11}, where it's used to "
        "multiply out brackets like $(x+3)(x+2)$.", 13.5, C.BROWN, gap=8)
    f.p("{b:Times tables.} Quick recall of the times tables up to 10 x 10 makes everything later "
        "much less tiring. If they are shaky, the grid on the next page is worth pinning up.", 13.5)


def times_grid(ch):
    f = flow(ch)
    sec(f, "The times-table square", room=440)
    f.p("Find a row and a column; where they meet is the answer. The {o:diagonal} holds the "
        "{B:square numbers} ($1\\times1$, $2\\times2$, ...), which come up constantly later.", 13.5,
        gap=8)
    y = f.reserve(360)
    pg = f.pg
    s = 32
    x0 = L + 70
    for i in range(11):
        for j in range(11):
            x, yy = x0 + j * s, y + i * s
            if i == 0 and j == 0:
                pg.text(x + s / 2, yy + 9, "x", 12, C.GREY, F.BOLD, align="center")
                continue
            if i == 0 or j == 0:
                pg.rect(x, yy, s, s, C.ORANGE, 0.6, fillcolor=C.LIGHT[C.ORANGE])
                pg.text(x + s / 2, yy + 9, str(i or j), 12, C.ORANGE, F.BOLD, align="center")
                continue
            col = C.LIGHT[C.GREEN] if i == j else "#ffffff"
            pg.rect(x, yy, s, s, "#cccccc", 0.5, fillcolor=col)
            pg.text(x + s / 2, yy + 9, str(i * j), 11, C.INK, align="center")
    pg.note(x0 + 11 * s + 8, y + 5 * s, "square\nnumbers\non the\ndiagonal", C.GREEN, 15)


def dividing(ch):
    f = flow(ch)
    sec(f, "Dividing: sharing out, and what's left over", room=420)
    f.p("$20\\div4$ asks: {B:share 20 sweets between 4 people. How many each?} Deal them out one at "
        "a time, like cards:", 14, gap=6)
    y = f.reserve(70)
    pg = f.pg
    for p_ in range(4):
        pg.circle(L + 60 + p_ * 110, y + 12, 10, C.INK, 1.3)
        dots(pg, L + 40 + p_ * 110, y + 32, 1, 5, 10, C.PURPLE)
    pg.note(L + 450, y + 20, "5 each", C.GREEN, 18)
    ch.check(20 // 4, 5)
    f.p("Division is the undo button for multiplying: $4\\times5 = 20$, so $20\\div4 = 5$. The same "
        "sum can be asked the other way round: \"how many groups of 4 can I make from 20?\" (also 5).",
        14, gap=8)
    rule_box(f, "division", [
        "{B:Division undoes multiplication:} if $a\\times b=c$ then $c\\div b=a$ and $c\\div a=b$. "
        "Use this to check every division.",
        "{R:Order matters:} $20\\div4=5$ but $4\\div20=\\frac{4}{20}=\\frac15$. Division is not "
        "commutative.",
        "{B:With a remainder:} number $=$ quotient $\\times$ divisor $+$ remainder, and the remainder is "
        "always smaller than the divisor. E.g. $23=5\\times4+3$.",
        "{R:You can never divide by 0.}",
    ], C.ORANGE)
    ch.check(sp.Rational(4, 20), sp.Rational(1, 5))
    ch.check(5 * 4 + 3, 23)
    f.p("{b:Remainders.} Share 23 sweets between 4: each gets 5 (that uses 20), and {R:3 are left "
        "over}. We write $23\\div4 = 5$ remainder 3, or \"5 r 3\".", 14, gap=6)
    ch.term("remainder", "what is left over when a number doesn't share out exactly")
    ch.check(23 // 4, 5)
    ch.check(23 % 4, 3)
    f.p("{b:Bigger division, sharing crate by crate (\"short division\"):}  $156\\div6$.", 14, gap=6)
    y = f.reserve(110)
    pg = f.pg
    X = L + 50
    for dx, d in ((30, "1"), (52, "5"), (74, "6")):
        pg.text(X + dx, y + 32, d, 22, C.INK, F.BOLD)
    for dx, d in ((52, "2"), (74, "6")):
        pg.text(X + dx, y, d, 22, C.GREEN, F.BOLD)
    pg.text(X - 4, y + 32, "6", 22, C.INK, F.BOLD)
    pg.line(X + 18, y + 28, X + 18, y + 60, C.INK, 1.6)
    pg.line(X + 18, y + 28, X + 100, y + 28, C.INK, 1.6)
    pg.text(X + 67, y + 29, "3", 10, C.RED, F.BOLD, solid=False)
    pg.note(X + 130, y - 4, "1. 6 into 1 (hundred)? Can't. Look at 15 (tens) instead.", C.RED, 15)
    pg.note(X + 130, y + 22, "2. 6 into 15 = 2, remainder 3. Write 2 on top.\n"
            "    The 3 tens left over become 30 ones: write a small 3.", C.RED, 15)
    pg.note(X + 130, y + 68, "3. 6 into 36 = 6. Write 6. So 156 ÷ 6 = 26.", C.GREEN, 16)
    ch.check(156 // 6, 26)
    f.p("{G:Check by multiplying back:} $26\\times6 = 120 + 36 = 156$. ✓", 13.5, gap=8)
    f.p("{R:Dividing by zero is not allowed.} \"Share 5 sweets between 0 people\" has no sensible "
        "answer. Calculators give an error, and so does maths.", 13.5)


def bodmas(ch):
    f = flow(ch)
    sec(f, "The order of operations (BODMAS)", room=520)
    rule_box(f, "order of operations", [
        "{B:Brackets} first. With brackets inside brackets, work from the {B:innermost} outwards.",
        "{B:Orders}: powers and roots ($5^2$, $\\sqrt9$).",
        "{B:Division and Multiplication}: {R:equal priority}. Work {B:left to right}, doing whichever "
        "comes first.",
        "{B:Addition and Subtraction}: {R:equal priority}. Work {B:left to right}.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    rule_box(f, "hidden brackets", [
        "A {B:fraction bar} acts as brackets round the whole top and the whole bottom: "
        "$\\frac{4+8}{5-2}=(4+8)\\div(5-2)$.",
        "A power applies only to what it touches: $-3^2=-(3^2)=-9$, but $(-3)^2=(-3)\\times(-3)=9$.",
    ], C.ORANGE)
    f.p("Like getting dressed (socks before shoes), doing the steps in a different order gives a "
        "different result. The order is often remembered as {B:BODMAS}:", 14, gap=8)
    items = [("B", "Brackets", "( ) first, always", C.RED),
             ("O", "Orders", "powers and roots, like 5² or √9", C.ORANGE),
             ("DM", "Division and Multiplication", "equal rank: work left to right", C.BLUE),
             ("AS", "Addition and Subtraction", "equal rank: work left to right", C.GREEN)]
    for i, (a, b, c, col) in enumerate(items):
        y = f.reserve(44)
        pg = f.pg
        pg.rect(L + 10 + i * 18, y, 50, 34, col, 1.6, fillcolor=C.LIGHT[col], r=8)
        pg.text(L + 35 + i * 18, y + 7, a, 15, col, F.BOLD, align="center")
        pg.text(L + 72 + i * 18, y + 1, b, 14, C.INK, F.BOLD)
        pg.note(L + 72 + i * 18, y + 17, c, C.GREY, 15)
    f.p("(Some people learned {B:BIDMAS} or {B:PEMDAS}: same rules, different words.) Note that "
        "D and M are {B:equal}: do whichever comes first reading left to right. Same for A and S.",
        13.5, gap=10)
    ch.term("BODMAS", "the order to do operations: Brackets, Orders (powers), Division/Multiplication, Addition/Subtraction")
    f.p("{b:Example, one step per line:}  $3+4\\times2^2-(6-1)$", 14, gap=4)
    step(f, r"3+4\times2^2-\org{(6-1)}", "B: brackets first: 6 - 1 = 5")
    step(f, r"3+4\times\org{2^2}-5", "O: powers: 2 squared = 4")
    step(f, r"3+\org{4\times4}-5", "M: multiply: 4 x 4 = 16")
    step(f, r"\org{3+16}-5", "A/S left to right: 3 + 16 = 19")
    step(f, r"19-5=\grn{14}", "then 19 - 5")
    ch.check(3 + 4 * 2 ** 2 - (6 - 1), 14)
    f.need(330)
    f.p("{b:Equal priority means left to right:}", 14, gap=4)
    step(f, r"12\div3\times2=\org{12\div3}\times2=4\times2=\grn{8}", "÷ comes first reading left to right")
    step(f, r"10-4+3=\org{10-4}+3=6+3=\grn{9}", "− comes first reading left to right")
    ch.check(sp.Rational(12, 3) * 2, 8)
    ch.check(10 - 4 + 3, 9)
    f.p("{b:Nested brackets, innermost first:}  $2\\times[3+(8-2)^2]$", 14, gap=4)
    step(f, r"2\times[3+\org{(8-2)}^2]=2\times[3+6^2]", "inner bracket: 8 − 2 = 6")
    step(f, r"=2\times[3+\org{36}]=2\times39=\grn{78}", "power, then the outer bracket")
    ch.check(2 * (3 + (8 - 2) ** 2), 78)
    f.p("{b:Fraction bar and powers of negatives:}", 14, gap=4)
    step(f, r"\frac{4+8}{5-2}=\frac{12}{3}=\grn{4}", "top and bottom first, then divide")
    step(f, r"(-3)^2=9,\qquad -3^2=-9", "the square touches −3 in the first, only 3 in the second")
    ch.check(sp.Rational(4 + 8, 5 - 2), 4)
    ch.check((-3) ** 2, 9)
    ch.check(-3 ** 2, -9)
    mistakes(f, [
        (r"12\div3\times2=12\div6=2", r"12\div3\times2=4\times2=8",
         "× is not done before ÷: they are equal, so go left to right"),
        (r"10-4+3=10-7=3", r"10-4+3=6+3=9", "same for + and −: left to right"),
        (r"-3^2=9", r"-3^2=-(3^2)=-9", "without brackets the power does not include the minus sign"),
    ])


def viral(ch):
    f = flow(ch)
    sec(f, "The internet argument:  8 ÷ 2(2+2)", room=340)
    f.p("Your Lecture 1 slides show this famous puzzle. People get {B:16} or {B:1}, and argue for "
        "days. Here are the two readings side by side:", 14, gap=8)
    y = f.reserve(200)
    pg = f.pg
    for k, (title, lines, col, why) in enumerate([
        ("Reading A: strict left to right", [r"8\div2(2+2)", r"8\div2\times4", r"4\times4", r"16"], C.BLUE,
         "brackets first, then\n÷ and x left to right"),
        ("Reading B: \"2(2+2)\" is one lump", [r"8\div2(2+2)", r"8\div(2\times4)", r"8\div8", r"1"], C.PURPLE,
         "treat 2(4) as a single\nnumber, because it's glued"),
    ]):
        x0 = L + 10 + k * 250
        pg.text(x0, y, title, 13, col, F.BOLD)
        for i, lat in enumerate(lines):
            pg.eq(x0 + 20, y + 24 + i * 36, lat, 19, col if i == 3 else C.INK)
        pg.note(x0 + 120, y + 140, why, col, 15)
    ch.check(sp.Rational(8, 2) * (2 + 2), 16)
    ch.check(sp.Rational(8, 2 * (2 + 2)), 1)
    f.p("The honest answer: the expression is {R:badly written}. The rules above give 16, but plenty "
        "of calculators and scientists treat \"$2(2+2)$\" as glued together and give 1. The lesson "
        "from your lecture is: {B:when you write maths, remove the doubt.} Use extra brackets, and "
        "use a fraction line instead of ÷:", 14, gap=8)
    y = f.reserve(60)
    pg = f.pg
    pg.eq(L + 60, y, r"\frac{8}{2}(2+2)=16", 22, C.BLUE)
    pg.eq(L + 300, y, r"\frac{8}{2(2+2)}=1", 22, C.PURPLE)
    f.p("Nobody can argue with either of those. That's why, from now on, this book (and your "
        "lecturer) almost never uses the ÷ sign once letters appear.", 13.5)


def factors(ch):
    f = flow(ch)
    sec(f, "Factors: every way to make a rectangle", room=300)
    f.p("A {B:factor} of 12 is a number that divides into 12 exactly, with no remainder. Here's a "
        "picture of it: take 12 dots and find {B:every rectangle} you can make with them.", 14, gap=8)
    y = f.reserve(110)
    pg = f.pg
    shapes = [(1, 12), (2, 6), (3, 4)]
    x = L + 10
    for r, c in shapes:
        dots(pg, x, y + 10, r, c, 11)
        pg.note(x, y + 10 + r * 11 + 2, f"{r} x {c}", C.ORANGE, 16)
        x += c * 11 + 30
    pg.note(L + 360, y + 50, "(4 x 3, 6 x 2 and 12 x 1\nare the same rectangles\nturned sideways)", C.GREY, 14)
    f.p("The side lengths are the factors: {O:1, 2, 3, 4, 6, 12}. Factors come in pairs that "
        "multiply to 12: 1 & 12, 2 & 6, 3 & 4.", 14, gap=10)
    ch.term("factor", "a number that divides exactly into another: the factors of 12 are 1, 2, 3, 4, 6, 12")
    ch.check(sp.divisors(12), [1, 2, 3, 4, 6, 12])
    f.p("{B:Primes} are the numbers bigger than 1 that {B:only} make a single line of dots:", 14, gap=6)
    y = f.reserve(56)
    pg = f.pg
    dots(pg, L + 20, y + 8, 1, 7, 11, C.GREEN)
    pg.note(L + 110, y, "7 dots: only 1 x 7 works.\nNo other rectangle. 7 is prime.", C.GREEN, 15)
    dots(pg, L + 300, y + 4, 2, 4, 11, C.RED)
    pg.note(L + 350, y, "8 dots makes 2 x 4:\n8 is NOT prime", C.RED, 15)
    f.p("The first primes are {G:2, 3, 5, 7, 11, 13, 17, 19, 23, 29}. (1 is not counted as prime.) "
        "A whole number bigger than 1 that isn't prime is called {B:composite} (it has a factor other "
        "than 1 and itself). 0 and 1 are neither prime nor composite.", 14, gap=10)
    ch.term("prime number", "a number bigger than 1 whose only factors are 1 and itself")
    ch.check(list(sp.primerange(2, 30)), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
    f.p("{B:Multiples} are the times table of a number: the multiples of 4 are 4, 8, 12, 16, 20... "
        "\"12 is a multiple of 4\" and \"4 is a factor of 12\" say the same thing from opposite ends.",
        14)
    ch.term("multiple", "a number in another number's times table: 12 is a multiple of 4")


def prime_tree(ch):
    f = flow(ch)
    sec(f, "Breaking a number into primes: a factor tree", room=220)
    f.p("Every whole number bigger than 1 can be built by multiplying primes together, and in "
        "only one way. To find the primes, keep splitting into any factor pair until only primes "
        "are left. Take 60:", 14, gap=8)
    y = f.reserve(170)
    pg = f.pg
    nodes = {"60": (L + 120, y + 10), "6": (L + 70, y + 60), "10": (L + 170, y + 60),
             "2a": (L + 45, y + 110), "3": (L + 95, y + 110), "2b": (L + 145, y + 110), "5": (L + 195, y + 110)}
    edges = [("60", "6"), ("60", "10"), ("6", "2a"), ("6", "3"), ("10", "2b"), ("10", "5")]
    for a, b in edges:
        (xa, ya), (xb, yb) = nodes[a], nodes[b]
        pg.line(xa, ya + 18, xb, yb, C.GREY, 1.2)
    for k, (x, yy) in nodes.items():
        lab = k.rstrip("ab")
        prime = lab in ("2", "3", "5")
        if prime:
            pg.circle(x, yy + 9, 14, C.GREEN, 1.6, fillcolor=C.LIGHT[C.GREEN])
        pg.text(x, yy, lab, 16, C.GREEN if prime else C.INK, F.BOLD, align="center")
    pg.note(L + 250, y + 10, "60 = 6 x 10", C.INK, 17)
    pg.note(L + 250, y + 40, "6 = 2 x 3,  10 = 2 x 5", C.INK, 17)
    pg.note(L + 250, y + 70, "circled numbers are prime: stop", C.GREEN, 17)
    pg.eq(L + 250, y + 105, r"60=2\times2\times3\times5", 19)
    pg.eq(L + 250, y + 135, r"\phantom{60}=2^2\times3\times5", 19)
    ch.check(2 * 2 * 3 * 5, 60)
    f.p("You could start with $60 = 4\\times15$ instead; you'd still end with the same primes. This "
        "list of primes is the number's {B:prime factorisation}.", 13.5)
    ch.term("prime factorisation", "a number written as primes multiplied together: 60 = 2 x 2 x 3 x 5")


def hcf_lcm(ch):
    f = flow(ch)
    sec(f, "LCM: when do two blinking lights blink together?", room=250)
    f.p("One traffic light blinks every {o:4 seconds}; another blinks every {b:6 seconds}. They both "
        "blink at the start. When do they next blink {B:at the same time}?", 14, gap=8)
    y = f.reserve(110)
    pg = f.pg
    x0, sc = L + 30, 17
    pg.line(x0, y + 80, x0 + 25 * sc, y + 80, C.INK, 1.2)
    for t in range(0, 25):
        pg.line(x0 + t * sc, y + 77, x0 + t * sc, y + 83, C.GREY, 0.8)
        if t % 2 == 0:
            pg.text(x0 + t * sc, y + 86, str(t), 9, C.GREY, align="center")
    for t in range(0, 25, 4):
        pg.circle(x0 + t * sc, y + 22, 7, C.ORANGE, 1.4, fillcolor=C.LIGHT[C.ORANGE])
    for t in range(0, 25, 6):
        pg.circle(x0 + t * sc, y + 50, 7, C.BLUE, 1.4, fillcolor=C.LIGHT[C.BLUE])
    for t in (12, 24):
        pg.rect(x0 + t * sc - 11, y + 10, 22, 54, C.GREEN, 1.6, r=8)
    pg.note(x0 + 25 * sc + 6, y + 14, "every 4 s", C.ORANGE, 14)
    pg.note(x0 + 25 * sc + 6, y + 42, "every 6 s", C.BLUE, 14)
    pg.note(x0 + 25 * sc + 6, y + 70, "seconds", C.GREY, 13)
    f.p("Together at {G:12 seconds} (and again at 24, 36...). 12 is the smallest number in {B:both} "
        "times tables: the {B:Lowest Common Multiple}, or {B:LCM}, of 4 and 6.", 14, gap=6)
    ch.check(sp.ilcm(4, 6), 12)
    ch.term("LCM (lowest common multiple)", "the smallest number that is in both times tables")
    f.p("Chapter 2 uses the LCM to find the smallest piece-size two fractions can be cut into.", 13,
        C.GREY, gap=12)
    sec(f, "HCF: the biggest number that fits into both", room=240)
    f.p("The {B:Highest Common Factor} (HCF) of 12 and 18 is the {B:biggest} number that divides "
        "into both. List the factors and find the biggest one they share:", 14, gap=6)
    y = f.reserve(56)
    pg = f.pg
    pg.rich(L + 20, y, "Factors of 12:  1, 2, 3, 4, {G:6}, 12", 380, 14)
    pg.rich(L + 20, y + 26, "Factors of 18:  1, 2, 3, {G:6}, 9, 18", 380, 14)
    pg.note(L + 330, y + 8, "HCF = 6", C.GREEN, 20)
    ch.check(sp.igcd(12, 18), 6)
    ch.term("HCF (highest common factor)", "the biggest number that divides exactly into both numbers")
    f.p("Chapter 2 uses the HCF to simplify fractions in one step: $\\frac{12}{18}$ becomes "
        "$\\frac{2}{3}$ by dividing top and bottom by 6.", 13.5, gap=8)
    f.p("{h:Don't mix them up:} {B:M}ultiples get bigger (LC{B:M} is at least as big as both numbers). "
        "{B:F}actors get smaller (HC{B:F} is no bigger than either number).", 13.5, C.BROWN)


def hcf_lcm_primes(ch):
    f = flow(ch)
    sec(f, "HCF and LCM from prime factorisations", room=520)
    f.p("Listing factors or multiples is slow for big numbers. Prime factorisations give both in "
        "one go.", 14, gap=8)
    rule_box(f, "HCF and LCM using primes", [
        "Write each number as a product of primes, using powers: $24=2^3\\times3$, $36=2^2\\times3^2$.",
        "{B:HCF}: take only the primes that appear in {B:every} number, each with its {B:lowest} power.",
        "{B:LCM}: take {B:every} prime that appears in any of the numbers, each with its {B:highest} "
        "power.",
        "Multiply out. Check: for two numbers, $\\text{HCF}\\times\\text{LCM}=$ the two numbers "
        "multiplied together.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    f.p("{b:Example: HCF and LCM of 24 and 36.}", 14, gap=4)
    step(f, r"24=2^3\times3,\qquad 36=2^2\times3^2", "factor trees")
    step(f, r"\text{HCF}=2^{\org{2}}\times3^{\org{1}}=\grn{12}", "shared primes 2 and 3, lowest powers")
    step(f, r"\text{LCM}=2^{\org{3}}\times3^{\org{2}}=8\times9=\grn{72}", "all primes, highest powers")
    step(f, r"12\times72=864=24\times36\ \checkmark", "the check")
    ch.check(2 ** 3 * 3, 24)
    ch.check(2 ** 2 * 3 ** 2, 36)
    ch.check(sp.igcd(24, 36), 2 ** 2 * 3)
    ch.check(sp.ilcm(24, 36), 2 ** 3 * 3 ** 2)
    ch.check(12 * 72, 24 * 36)
    f.p("{b:Word problems: which one do I need?}  \"Biggest thing that fits into both\" (cutting, "
        "sharing into equal groups) is the {B:HCF}. \"When do they next happen together\" (timetables, "
        "repeating patterns) is the {B:LCM}.", 14, gap=8)
    f.p("{b:Example.} A floor is 84 cm by 60 cm. It is covered exactly with identical square tiles, as "
        "large as possible. What size are the tiles?", 14, gap=4)
    step(f, r"84=2^2\times3\times7,\qquad 60=2^2\times3\times5", "tile side must divide both: HCF")
    step(f, r"\text{HCF}=2^2\times3=\grn{12\text{ cm}}", "84 ÷ 12 = 7 tiles by 60 ÷ 12 = 5 tiles")
    ch.check(2 ** 2 * 3 * 7, 84)
    ch.check(2 ** 2 * 3 * 5, 60)
    ch.check(sp.igcd(84, 60), 12)
    f.p("{b:Example.} Buses leave every 12 minutes and trams every 18 minutes. Both leave at 9:00. When "
        "do they next leave together?", 14, gap=4)
    step(f, r"12=2^2\times3,\ \ 18=2\times3^2\ \Rightarrow\ \text{LCM}=2^2\times3^2=36",
         "\"together again\": LCM", size=19)
    step(f, r"9{:}00+36\text{ min}=\grn{9{:}36}", "")
    ch.check(sp.ilcm(12, 18), 36)


def missing(ch):
    f = flow(ch)
    sec(f, "Find the missing number", room=520)
    rule_box(f, "finding an unknown", [
        "Write the unknown as $?$ (later in the book: a letter such as $x$).",
        "{B:Undo} what was done to it, using the {B:inverse} operation: $+$ is undone by $-$, $-$ by "
        "$+$, $\\times$ by $\\div$, $\\div$ by $\\times$.",
        "Apply the sign rules for negatives as you go.",
        "{B:Check} by putting your answer back into the original line.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    f.p("{b:Example.}  $?-7=-3$", 14, gap=4)
    step(f, r"?=-3+7=\grn{4}", "undo − 7 by adding 7")
    step(f, r"4-7=-3\ \checkmark", "check")
    ch.check(-3 + 7, 4)
    ch.check(4 - 7, -3)
    f.p("{b:Example.}  $-4\\times\\,?=28$", 14, gap=4)
    step(f, r"?=28\div(-4)=\grn{-7}", "undo × (−4) by dividing; different signs: negative")
    step(f, r"-4\times(-7)=28\ \checkmark", "same signs: positive")
    ch.check(sp.Rational(28, -4), -7)
    ch.check(-4 * -7, 28)
    f.p("{b:Example.}  $?\\div3=-6$", 14, gap=4)
    step(f, r"?=-6\times3=\grn{-18}", "undo ÷ 3 by multiplying by 3")
    ch.check(sp.Rational(-18, 3), -6)
    f.p("{b:Example.}  The HCF of 12 and $n$ is 4, and $n$ is from 20 to 30. What could $n$ be?",
        14, gap=4)
    step(f, r"4\mid n:\ \ n\in\{20,24,28\}", "4 must divide n: multiples of 4 in range", size=19)
    step(f, r"\text{HCF}(12,24)=12\ne4", "24 shares the factor 3 with 12 as well: rule it out", size=19)
    step(f, r"\text{HCF}(12,20)=4,\ \ \text{HCF}(12,28)=4\Rightarrow n=\grn{20\text{ or }28}", "", size=19)
    ch.check([n for n in range(20, 31) if n % 4 == 0], [20, 24, 28])
    ch.check([n for n in range(20, 31) if sp.igcd(12, n) == 4], [20, 28])
    f.p("(The \"$\\mid$\" sign means \"divides exactly\": $4\\mid20$ reads \"4 divides 20\".)", 12.5, C.GREY)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Place value", None, "each column is worth 10 times the column to its right; 0 holds an empty place"),
        ("Adding a negative", r"a+(-b)=a-b", "e.g. $7+(-3)=4$"),
        ("Subtracting a negative", r"a-(-b)=a+b", "e.g. $5-(-2)=7$"),
        ("Different signs (+, −)", None, "subtract the sizes; the answer takes the sign of the number "
         "with the bigger size: $-9+4=-5$"),
        ("× and ÷ signs", r"(-a)\times(-b)=ab,\quad (-a)\times b=-ab",
         "same signs give $+$, different signs give $-$; the same for $\\div$"),
        ("Order of operations", None, "brackets (innermost first), powers, × and ÷ left to right, "
         "+ and − left to right"),
        ("Fraction bar", r"\frac{a+b}{c+d}=(a+b)\div(c+d)", "the bar acts as brackets"),
        ("Powers of negatives", r"(-3)^2=9,\qquad -3^2=-9", None),
        ("Commutative", r"a+b=b+a,\quad a\times b=b\times a", "{R:not} for $-$ or $\\div$"),
        ("Distributive law", r"a(b+c)=ab+ac", None),
        ("Division", r"a\times b=c\iff c\div b=a", "never divide by 0"),
        ("Remainder", None, "number = quotient × divisor + remainder (remainder < divisor)"),
        ("Prime factorisation", None, "every whole number above 1 is one product of primes, e.g. "
         "$60=2^2\\times3\\times5$"),
        ("HCF", None, "primes common to all the numbers, lowest powers"),
        ("LCM", None, "every prime that appears, highest powers"),
        ("HCF and LCM", r"\text{HCF}(a,b)\times\text{LCM}(a,b)=a\times b", None),
        ("Find an unknown", None, "undo the operation with its inverse, then check"),
    ], C.ORANGE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Number detective: your turn", fresh=True)
    f.p("Try each one on paper or straight onto this page. Answers are underneath each group, "
        "written small and upside-down... well, small and grey. Cover them with your hand!", 13.5,
        gap=10)
    groups = [
        ("Bundles", ["1.  What does the 6 in 3602 stand for?", "2.  68 + 57", "3.  81 - 36"],
         "1. 6 hundreds (600)   2. 125 (ones: 8+7 = 15, carry 1)   3. 45 (open a bundle: 11 - 6, 7 - 3)"),
        ("The lift", ["4.  -4 + 9", "5.  3 - 8", "6.  -2 - (-5)", "7.  (-4) x (-5)"],
         "4. 5   5. -5   6. 3 (taking away a debt)   7. 20 (same signs: positive)"),
        ("Getting dressed", ["8.  10 - 2 x 3", "9.  (10 - 2) x 3", "10.  2 + 3²"],
         "8. 4 (multiply first)   9. 24 (brackets first)   10. 11 (power first: 9, then + 2)"),
        ("Dots and lights", ["11.  All factors of 18", "12.  Is 21 prime?", "13.  LCM of 6 and 8",
                             "14.  HCF of 24 and 36"],
         "11. 1, 2, 3, 6, 9, 18   12. No: 21 = 3 x 7   13. 24   14. 12"),
        ("Signs, order and primes", ["15.  -6 + (-9)", "16.  -12 ÷ 3 × 2", "17.  (-5)² and -5²",
                                     "18.  2 × [10 - (1 + 2)²]", "19.  (18 - 3) / (2 + 3)",
                                     "20.  HCF and LCM of 18 and 24, using prime factors"],
         "15. -15 (both negative: add sizes)   16. -8 (left to right: -4 × 2)   17. 25 and -25   "
         "18. 2 (inner bracket 3, then 10 - 9 = 1)   19. 3 (15 ÷ 5)   "
         "20. 18 = 2 × 3², 24 = 2³ × 3: HCF = 2 × 3 = 6, LCM = 2³ × 3² = 72"),
        ("Find the unknown", ["21.  ? - 7 = -3", "22.  -4 × ? = 28", "23.  ? ÷ (-6) = 5", "24.  15 + ? = 9",
                              "25.  The HCF of 12 and n is 4, and n is from 20 to 30. Find n.",
                              "26.  The LCM of 6 and n is 30, and n is less than 10. Find n."],
         "21. 4 (? = -3 + 7)   22. -7 (? = 28 ÷ (-4))   23. -30 (? = 5 × (-6))   24. -6 (? = 9 - 15)   "
         "25. 20 or 28 (multiples of 4; 24 is out because HCF(12, 24) = 12)   "
         "26. 5 (30 = 2 × 3 × 5 and 6 = 2 × 3, so n must supply the 5; 10 is too big)"),
    ]
    ch.check(-6 + (-9), -15)
    ch.check(sp.Rational(-12, 3) * 2, -8)
    ch.check(((-5) ** 2, -5 ** 2), (25, -25))
    ch.check(2 * (10 - (1 + 2) ** 2), 2)
    ch.check(sp.Rational(18 - 3, 2 + 3), 3)
    ch.check((sp.igcd(18, 24), sp.ilcm(18, 24)), (6, 72))
    ch.check(-3 + 7 - 7, -3)
    ch.check(-4 * sp.Rational(28, -4), 28)
    ch.check(sp.Rational(5 * -6, -6), 5)
    ch.check(15 + (9 - 15), 9)
    ch.check([n for n in range(20, 31) if sp.igcd(12, n) == 4], [20, 28])
    ch.check([n for n in range(1, 10) if sp.ilcm(6, n) == 30], [5])
    ch.check(68 + 57, 125)
    ch.check(81 - 36, 45)
    ch.check(-4 + 9, 5)
    ch.check(3 - 8, -5)
    ch.check(-2 - (-5), 3)
    ch.check((-4) * (-5), 20)
    ch.check(10 - 2 * 3, 4)
    ch.check((10 - 2) * 3, 24)
    ch.check(2 + 3 ** 2, 11)
    ch.check(sp.divisors(18), [1, 2, 3, 6, 9, 18])
    ch.check(sp.ilcm(6, 8), 24)
    ch.check(sp.igcd(24, 36), 12)
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 40)
        y = f.reserve(30)
        f.pg.text(L, y, title, 15, C.ORANGE, F.BOLD)
        for q in qs:
            f.p(q, 13.5, x=L + 16, gap=4)
        f.gap(4)
        f.p(ans, 10.5, C.GREY, x=L + 16, gap=14)


def build(ch):
    title_page(ch)
    place_value(ch)
    adding(ch)
    subtracting(ch)
    negatives(ch)
    neg_multiply(ch)
    multiplying(ch)
    times_grid(ch)
    dividing(ch)
    bodmas(ch)
    viral(ch)
    factors(ch)
    prime_tree(ch)
    hcf_lcm(ch)
    hcf_lcm_primes(ch)
    missing(ch)
    summary(ch)
    your_turn(ch)
