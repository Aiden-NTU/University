"""Chapter 17 - Sequences and series. A piggy bank that gets a fixed amount more each week
(arithmetic), Gauss's pairing trick drawn as two staircases making a rectangle, sigma as a Python
for-loop, a bouncing ball (geometric), and walking halfway to the wall (sum to infinity)."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step, title_block

ORDER = 17
NUM = 17
TITLE = "Sequences and series"
SHORT = "Sequences & series"
SLUG = "Sequences-series"
ACCENT = C.ORANGE
REQUIRES = ["addition", "multiplication", "powers", "negative-numbers", "fraction", "substitution",
            "transpose", "solve-equation", "subscript-notation", "algebraic-fractions", "factorise-common-factor",
            "simultaneous-equations", "quadratic-equation"]
INTRODUCES = ["sequence", "series", "term-of-sequence", "arithmetic-progression", "common-difference",
              "nth-term", "arithmetic-sum", "sigma-notation", "geometric-progression", "common-ratio",
              "geometric-sum", "sum-to-infinity", "modulus", "converge"]

PAPER = "#fffcf7"
COIN, COIN_EDGE = "#ffd54f", "#b8860b"
n = sp.Symbol("n")


def icon(pg, x0, y0):
    for i in range(4):
        pg.rect(x0 + 1 + i * 4.5, y0 + 17 - (i + 1) * 4, 4, (i + 1) * 4, C.ORANGE, 0.8,
                fillcolor=C.LIGHT[C.ORANGE])


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def coins(pg, x0, base, k, w=22, h=5):
    for i in range(k):
        pg.ellipse(x0 + w / 2, base - i * h - h / 2, w / 2, h / 2 + 0.5, COIN_EDGE, 0.8, fillcolor=COIN)


def code(pg, x0, y0, lines, w=300, size=11.5):
    lh = size * 1.5
    h = lh * len(lines) + 14
    pg.rect(x0, y0, w, h, "#263238", 1, fillcolor="#263238", r=6)
    for i, (s, col) in enumerate(lines):
        pg.text(x0 + 12, y0 + 7 + i * lh, s, size, col, F.MONO)
    return h


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 17, "Sequences and series", "patterns that march on, and adding them all up",
                     C.ORANGE, PAPER)
    base = 330
    for i, k in enumerate([2, 6, 10, 14, 18]):
        coins(pg, L + 30 + i * 50, base, k)
        pg.text(L + 41 + i * 50, base + 6, f"£{k}", 11, C.BROWN, F.BOLD, align="center")
        pg.text(L + 41 + i * 50, base + 22, f"wk {i + 1}", 10, C.GREY, align="center")
    pg.note(L + 290, 230, "Each week you save £4 more\nthan the week before.\nHow much after a year?",
            C.BROWN, 17)
    pg.eq(L + 290, 300, r"2+6+10+\dots=\ ?", 20, C.ORANGE)
    f = ch.flow(top=390)
    f.p("A {B:sequence} is a list of numbers that follows a rule, like the savings above: 2, 6, 10, "
        "14, ... A {B:series} is what you get when you {B:add} the list up. This chapter has two kinds: "
        "lists that go up by the {B:same amount} each time (arithmetic) and lists that get "
        "{B:multiplied} by the same amount each time (geometric).", 14, gap=10)
    f.p("For each kind you'll learn to find any term without writing out the whole list, and to add "
        "up hundreds of terms in one line. Along the way, a trick a ten-year-old found, a Python "
        "loop, a bouncing ball, and an endless sum that adds up to exactly 1.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 13} {y:(arithmetic and geometric progressions, summation notation).}", 12.5)


def words(ch):
    f = flow(ch)
    sec(f, "Terms live in numbered lockers")
    f.p("Each number in a sequence is a {B:term}. Terms have positions: 1st, 2nd, 3rd... Picture a "
        "row of lockers, each with a number on the door (the position $n$) and a value inside:", 14, gap=10)
    y_ = f.reserve(80)
    pg = f.pg
    vals = [2, 6, 10, 14, 18, 22]
    for i, v in enumerate(vals):
        xx = L + 20 + i * 62
        pg.rect(xx, y_, 52, 54, C.ORANGE, 1.3, fillcolor=C.LIGHT[C.ORANGE], r=4)
        pg.circle(xx + 44, y_ + 27, 2, C.ORANGE, 1)
        pg.text(xx + 26, y_ + 4, f"n = {i + 1}", 10, C.GREY, align="center")
        pg.text(xx + 26, y_ + 22, str(v), 17, C.INK, F.BOLD, align="center")
    pg.text(L + 20 + 6 * 62, y_ + 20, "...", 17, C.GREY, F.BOLD)
    f.p("The value in locker $n$ is often written $u_n$ (\"u sub n\"). Here $u_1 = 2$, $u_4 = 14$. "
        "{B:Sequence} = the lockers. {B:Series} = the total of what's inside them: $2 + 6 + 10 + \\dots$",
        14, gap=8)
    ch.term("sequence", "an ordered list of numbers following a rule, e.g. 2, 6, 10, 14, ...")
    ch.term("series", "the sum of the terms of a sequence, e.g. 2 + 6 + 10 + 14")
    ch.term("term", "one number in a sequence; the nth term is the one in position n")
    ch.symbol(r"u_n", "u sub n", "the nth term of a sequence")
    f.p("{h:Lecture 13 says \"series are lists\".} Strictly, a list is a sequence and a sum is a "
        "series; the slides use the words loosely, so don't let that throw you.", 13.5, C.BROWN)


def arithmetic(ch):
    f = flow(ch)
    sec(f, "Arithmetic progressions: a staircase of equal steps", room=320)
    rule_box(f, "arithmetic progression (A.P.)", [
        "Each term = the previous term {B:+ d}. The common difference is $d=u_2-u_1$ (any term minus "
        "the one before). $a$ is the first term.",
        "$n$th term:  $u_n=a+(n-1)d$  (to reach term $n$ you make $n-1$ jumps of $d$).",
        "Any one of $u_n$, $a$, $n$, $d$ can be found from the other three by rearranging.",
    ], C.ORANGE)
    f.p("When each term is the last one {B:plus a fixed amount}, the sequence is an {B:arithmetic "
        "progression} (A.P.). The fixed amount is the {B:common difference} $d$. The savings: "
        "$a = 2$ (first term), $d = 4$.", 14, gap=10)
    ch.term("arithmetic progression (A.P.)", "a sequence where you add the same number d each time")
    ch.term("common difference", "d, the fixed amount added each time in an arithmetic progression")
    y_ = f.reserve(150)
    pg = f.pg
    sw, sh = 56, 18
    for i in range(5):
        xx = L + 30 + i * sw
        hgt = (1 + i * 1) * sh * 1.2
        pg.rect(xx, y_ + 130 - hgt, sw - 10, hgt, C.ORANGE, 1.2, fillcolor=C.LIGHT[C.ORANGE])
        pg.text(xx + (sw - 10) / 2, y_ + 132, f"n={i + 1}", 10, C.GREY, align="center")
        if i:
            pg.arrow(xx - 16, y_ + 130 - hgt + sh * 1.2 - 4, xx + 4, y_ + 130 - hgt - 2, C.GREEN, 1.1, bend=-0.4, head=4)
            pg.note(xx - 24, y_ + 108 - hgt, "+d", C.GREEN, 13, solid=False)
    pg.note(L + 330, y_ + 10, "To reach step 5 you make\nonly 4 jumps of d.\n"
            "(Like fence posts: 5 posts,\n4 gaps between them.)", C.GREEN, 16)
    f.p("So the $n$th term is the first term plus $(n - 1)$ jumps:", 14, gap=6)
    y_ = f.reserve(56)
    pg = f.pg
    bw = 250
    pg.rect(L + (W - bw) / 2, y_, bw, 46, C.ORANGE, 1.6, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.eq(L + W / 2, y_ + 23, r"u_n=a+(n-1)d", 22, align="center", valign="middle")
    ch.formula(r"u_n=a+(n-1)d", "nth term of an arithmetic progression")
    step(f, r"u_8=2+(8-1)\times4=2+28=30", "8th week's saving: 7 jumps of 4", size=19)
    ch.check((2 + (n - 1) * 4).subs(n, 8), 30)
    f.p("{b:Working backwards.} The same formula rearranges (Chapter 14) to answer the other "
        "questions Lecture 13 asks:", 14, gap=6)
    step(f, r"n=\frac{l-a}{d}+1", "how many terms, if the last term is l", size=19)
    step(f, r"d=\frac{l-a}{n-1}", "the difference, if you know n", size=19)
    f.p("{b:How many terms in} 2, 6, ..., 50? The gap from 2 to 50 is 48, that's $48 \\div 4 = 12$ "
        "jumps, so {B:13} terms (one more post than gaps). {b:And the slide's check:} 2, ..., 30 with "
        "8 terms has $d = \\frac{30-2}{8-1} = \\frac{28}{7} = 4$ ✓.", 14)
    ch.check(sp.Rational(50 - 2, 4) + 1, 13)
    ch.check(sp.Rational(30 - 2, 8 - 1), 4)


def gauss(ch):
    f = flow(ch)
    sec(f, "Adding them up: Gauss's pairing trick", room=520)
    rule_box(f, "sum of an arithmetic progression", [
        "First $n$ terms, when you know the last term $l$:  $S_n=\\dfrac n2(a+l)$.",
        "When you know $d$ instead:  $S_n=\\dfrac n2\\big(2a+(n-1)d\\big)$.",
        "Both say: (average of the first and last term) × (number of terms). The reason is below.",
    ], C.ORANGE)
    f.p("A famous story: a teacher told a class to add 1 + 2 + ... + 100, hoping for a quiet hour. "
        "Young Carl Gauss answered in seconds. He wrote the list forwards and backwards and added "
        "the columns:", 14, gap=8)
    y_ = f.reserve(78)
    pg = f.pg
    top = ["1", "2", "3", "…", "99", "100"]
    bot = ["100", "99", "98", "…", "2", "1"]
    for i in range(6):
        xx = L + 40 + i * 58
        pg.text(xx, y_, top[i], 14, C.BLUE, F.BOLD, align="center")
        pg.text(xx, y_ + 22, bot[i], 14, C.ORANGE, F.BOLD, align="center")
        pg.line(xx - 20, y_ + 42, xx + 20, y_ + 42, C.GREY, 0.8)
        pg.text(xx, y_ + 46, "101" if i != 3 else "…", 14, C.GREEN, F.BOLD, align="center")
    pg.note(L + 390, y_ + 2, "every column\nmakes 101!", C.GREEN, 17)
    f.p("100 columns of 101 is 10,100. But that's the list added {B:twice} (once each way), so "
        "the answer is half: {B:5050}.", 14, gap=8)
    ch.check(sum(range(1, 101)), 5050)
    f.p("The picture: a staircase of blocks, plus the same staircase upside down, makes a rectangle:",
        14, gap=10)
    y_ = f.reserve(120)
    pg = f.pg
    u = 16
    vals = [1, 2, 3, 4, 5]
    for i, v in enumerate(vals):
        for k in range(6):
            col = C.BLUE if k < v else C.ORANGE
            pg.rect(L + 30 + i * u, y_ + 96 - (k + 1) * u, u, u, col, 0.8, fillcolor=C.LIGHT[col])
    pg.note(L + 30, y_ + 100, "5 columns, each 6 tall", C.GREY, 14)
    pg.note(L + 160, y_ + 4, "blue: 1 + 2 + 3 + 4 + 5 (the staircase)\norange: the same staircase, flipped\n"
            "together: a 5 × 6 rectangle = 30 blocks\nso the staircase alone is 30 ÷ 2 = 15", C.PURPLE, 15)
    ch.check(sum(vals), 15)
    f.p("In general: {B:(first + last) is the same for every pair, there are $n$ terms, and we halve}. "
        "Or in words: the {B:average term} (halfway between first and last) {B:times how many terms}:",
        14, gap=6)
    y_ = f.reserve(64)
    pg = f.pg
    bw = 290
    pg.rect(L + (W - bw) / 2, y_, bw, 56, C.ORANGE, 1.6, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.eq(L + W / 2, y_ + 28, r"S_n=\frac{a+l}{2}\times n", 22, align="center", valign="middle")
    ch.formula(r"S_n=\frac{(a+l)}{2}\,n", "sum of an arithmetic progression (first a, last l, n terms)")
    ch.symbol(r"S_n", "S sub n", "the sum of the first n terms")
    step(f, r"2+6+10+14=\frac{2+14}{2}\times4=32", "Lecture 13, example 1", size=19)
    step(f, r"2+6+\dots+50=\frac{2+50}{2}\times13=338", "example 2 (13 terms, from the last page)", size=19)
    ch.check(sum(range(2, 51, 4)), 338)
    f.p("{b:If you know $n$ but not the last term,} swap $l$ for $a + (n-1)d$: "
        "$S_n = \\frac n2\\big(2a + (n-1)d\\big)$. Slide example: 2 + 6 + 10 + ..., 8 terms: "
        "$\\frac82(4 + 7 \\times 4) = 4 \\times 32 = 128$.", 14, gap=8)
    ch.formula(r"S_n=\frac n2\big(2a+(n-1)d\big)", "sum of an arithmetic progression (n terms, difference d)")
    ch.check(sum(2 + 4 * i for i in range(8)), 128)
    f.p("{h:The piggy bank, answered:} 52 weeks of 2, 6, 10, ... is $\\frac{52}{2}(4 + 51 \\times 4) = "
        "26 \\times 208 = 5408$, so £5408.", 13.5, C.BROWN)
    ch.check(sum(2 + 4 * i for i in range(52)), 5408)
    f.p("{b:A special staircase: the odd numbers.} Add $1 + 3 + 5 + 7 + 9$. Each odd number is an "
        "L-shaped layer that wraps around the previous square and makes the next one:", 14, gap=10)
    u = 17
    y_ = f.reserve(5 * u + 50)
    pg = f.pg
    cols = [C.ORANGE, C.BLUE, C.GREEN, C.PURPLE, C.PINK]
    x0, y0 = L + 40, y_ + 8
    for k in range(5):
        for i in range(k + 1):
            for j in range(k + 1):
                if i == k or j == k:
                    pg.rect(x0 + i * u, y0 + j * u, u, u, cols[k], 0.8, fillcolor=C.LIGHT[cols[k]])
    for k in range(5):
        pg.text(x0 + k * u, y0 + k * u + 3, f"{2 * k + 1}", 10, cols[k], F.BOLD, w=u, align="center")
    pg.note(x0 + 5 * u + 10, y0 + 10, "each colour is one\nlayer; its number sits\nin its corner", C.GREY, 12)
    pg.note(x0 - 10, y0 + 5 * u + 6, "1 + 3 + 5 + 7 + 9 = 5 × 5", C.INK, 13)
    ch.check(sum(range(1, 10, 2)), 25)
    pg.note(L + 250, y_ + 6, "Each new layer adds one row and one column to the square, plus the shared "
            "corner: k + k + 1 = the next odd number.\n\nSo the first n odd numbers always add up to n².",
            C.INK, 14, w=R - L - 250)
    step(f, r"S_n=\frac n2\big(2\times1+(n-1)\times2\big)=\frac n2\times2n=n^2", "the A.P. formula agrees (a = 1, d = 2)",
         size=17, color=C.GREEN)
    nn = sp.symbols("n")
    ch.check(sp.expand(nn / 2 * (2 + (nn - 1) * 2)), nn ** 2)


def sigma(ch):
    f = flow(ch)
    sec(f, "Σ is a for-loop", room=420)
    f.p("Writing $3 + 6 + 9 + \\dots + 36$ in full is tedious, so Lecture 13 uses the Greek capital "
        "{B:sigma}, Σ, meaning \"add up\". If you've written any code, it's a loop:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    pg.eq(L + 70, y_ + 60, r"\sum_{i=1}^{12}3i", 34, align="center", valign="middle")
    pg.arrow(L + 136, y_ + 10, L + 90, y_ + 22, C.RED, 1.1, head=4)
    pg.note(L + 140, y_ + 0, "stop when i = 12", C.RED, 14)
    pg.arrow(L + 136, y_ + 116, L + 90, y_ + 104, C.BLUE, 1.1, head=4)
    pg.note(L + 140, y_ + 108, "start with i = 1", C.BLUE, 14)
    pg.arrow(L + 150, y_ + 64, L + 120, y_ + 62, C.GREEN, 1.1, head=4)
    pg.note(L + 154, y_ + 54, "add 3i each time", C.GREEN, 14)
    code(pg, L + 270, y_ + 16, [("total = 0", "#eceff1"), ("for i in range(1, 13):", "#80cbc4"),
                                ("    total += 3 * i", "#ffcc80"), ("print(total)   # 234", "#b0bec5")], w=220)
    ch.check(sum(3 * i for i in range(1, 13)), 234)
    ch.symbol(r"\sum", "sigma (sum)", "add up the expression for each value of the counter from the bottom number to the top")
    ch.term("sigma notation", "Σ with a start value below and a stop value above: add up the expression for every counter value")
    f.p("Read it as: \"for $i$ from 1 to 12, add $3i$\": $3(1) + 3(2) + \\dots + 3(12)$. The letter $i$ "
        "is just a counter; it disappears from the answer. Python's range stops {B:before} its second "
        "number, which is why the code says 13.", 14, gap=8)
    f.p("Lecture 13 writes the same list a second way, counting from 0: "
        "$\\sum_{i=0}^{11}(3 + 3i) = 3 + 6 + \\dots + 36$. Different counter, same terms, same total. "
        "(It's an A.P., so $\\frac{3+36}{2} \\times 12 = 234$ ✓.)", 14)
    ch.check(sum(3 + 3 * i for i in range(12)), 234)


def geometric(ch):
    f = flow(ch)
    sec(f, "Geometric progressions: a bouncing ball", room=460)
    rule_box(f, "geometric progression (G.P.)", [
        "Each term = the previous term {B:× r}. The common ratio is $r=\\dfrac{u_2}{u_1}$ (any term divided "
        "by the one before). $a$ is the first term.",
        "$n$th term:  $u_n=ar^{\\,n-1}$  ($n-1$ multiplications by $r$).",
        "$r$ can be a fraction (the terms shrink) or negative (the signs alternate).",
    ], C.ORANGE)
    f.p("Drop a ball from 10 m. Each bounce reaches 60% of the height before. The heights are 10, 6, "
        "3.6, 2.16, ... Each term is the last one {B:multiplied} by the same number, 0.6:", 14, gap=10)
    y_ = f.reserve(130)
    pg = f.pg
    h, xx = 100, L + 30
    pg.line(L + 10, y_ + 112, L + 470, y_ + 112, C.GREY, 1.2)
    heights = [10, 6, 3.6, 2.16, 1.3]
    for i, hv in enumerate(heights):
        ph = hv * 10
        span = 30 + hv * 9
        pts = [(xx + span * t / 20, y_ + 112 - ph * (1 - (2 * t / 20 - 1) ** 2)) for t in range(21)]
        if i == 0:
            pts = pts[10:]
        pg.poly(pts, C.ORANGE, 1.4, dash=(3, 2))
        pg.text(pts[0][0] + (span / 2 if i else 0) - 8, y_ + 100 - ph - 6, f"{hv:g}", 11, C.ORANGE, F.BOLD,
                solid=False)
        xx = pts[-1][0]
    pg.circle(L + 30, y_ + 6, 6, C.RED, 1, fillcolor="#ff8a80")
    pg.note(L + 330, y_ + 4, "× 0.6 every bounce", C.PURPLE, 17)
    f.p("That's a {B:geometric progression} (G.P.). The multiplier is the {B:common ratio} $r$. Find "
        "it by dividing any term by the one before: $6 \\div 10 = 0.6$.", 14, gap=6)
    ch.term("geometric progression (G.P.)", "a sequence where you multiply by the same number r each time")
    ch.term("common ratio", "r, the fixed multiplier in a geometric progression (any term ÷ the one before)")
    f.p("Term $n$ has been multiplied by $r$ exactly $(n - 1)$ times (fence posts again):", 14, gap=6)
    y_ = f.reserve(56)
    pg = f.pg
    bw = 230
    pg.rect(L + (W - bw) / 2, y_, bw, 46, C.ORANGE, 1.6, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.eq(L + W / 2, y_ + 23, r"u_n=ar^{\,n-1}", 22, align="center", valign="middle")
    ch.formula(r"u_n=ar^{n-1}", "nth term of a geometric progression")
    f.p("{b:Lecture 13's example:} 3, 6, 12, ..., 3072. Here $a = 3$, $r = 2$. Which term is 3072?",
        14, gap=6)
    step(f, r"3\times2^{\,n-1}=3072", "", size=19)
    step(f, r"2^{\,n-1}=1024=2^{10}", "÷3; then keep doubling 1 until 1024: 10 doublings", size=19)
    step(f, r"n-1=10\ \Rightarrow\ n=11", "so 3072 is the 11th term", size=19, color=C.GREEN)
    ch.check(3 * 2 ** 10, 3072)
    f.p("(The slide's footnote says 3072 is $3 \\times 2^{11}$; that's 6144. It's $3 \\times 2^{10}$, and "
        "the slide itself then correctly uses $n = 11$.)", 12.5, C.GREY)


def geo_sum(ch):
    f = flow(ch)
    sec(f, "Adding a G.P.: shift and subtract", room=460)
    rule_box(f, "sum of a geometric progression", [
        "First $n$ terms:  $S_n=\\dfrac{a(1-r^n)}{1-r}$, or the same thing as $\\dfrac{a(r^n-1)}{r-1}$ "
        "(tidier when $r>1$).",
        "{R:Only for $r\\neq1$} (otherwise you divide by 0). If $r=1$ every term is $a$, so $S_n=na$.",
    ], C.ORANGE)
    f.p("Pairing doesn't work here (the pairs aren't equal). Instead, use this trick: write the sum, "
        "then write it again {B:multiplied by $r$}. Almost everything lines up:", 14, gap=8)
    y_ = f.reserve(96)
    pg = f.pg
    cw = 52
    row1 = [r"S", r"=", r"a", r"+ar", r"+ar^2", r"+\dots", r"+ar^{n-1}", ""]
    row2 = [r"rS", r"=", "", r"ar", r"+ar^2", r"+\dots", r"+ar^{n-1}", r"+ar^n"]
    for i in range(8):
        xx = L + 20 + i * cw + (18 if i > 1 else 0)
        if row1[i]:
            pg.eq(xx, y_ + 12, row1[i], 16, C.BLUE if i >= 3 and i <= 6 else C.INK, align="center", valign="middle")
        if row2[i]:
            pg.eq(xx, y_ + 46, row2[i], 16, C.BLUE if i >= 3 and i <= 6 else C.INK, align="center", valign="middle")
    pg.rect(L + 20 + 3 * cw - 6, y_ - 4, 4 * cw + 8, 66, C.BLUE, 1, dash=(4, 3), r=6)
    pg.note(L + 20 + 3 * cw, y_ + 66, "the blue parts match: subtracting wipes them out", C.BLUE, 14)
    step(f, r"S-rS=a-ar^n", "top line minus bottom line", size=19)
    step(f, r"S(1-r)=a(1-r^n)", "factorise both sides (Chapter 12)", size=19)
    step(f, r"S_n=\frac{a(1-r^n)}{1-r}", "÷ (1 − r)", size=21, color=C.GREEN)
    a, r = sp.symbols("a r")
    ch.check(sp.simplify(sum(a * r ** i for i in range(6)) - a * (1 - r ** 6) / (1 - r)), 0)
    ch.formula(r"S_n=\frac{a(1-r^n)}{1-r}", "sum of the first n terms of a geometric progression")
    f.p("{b:Lecture 13:} $3 + 6 + 12 + \\dots + 3072$, with $a = 3$, $r = 2$, $n = 11$:", 14, gap=6)
    step(f, r"S_{11}=\frac{3(1-2^{11})}{1-2}=\frac{3(1-2048)}{-1}=6141", "", size=19, color=C.GREEN)
    ch.check(sum(3 * 2 ** i for i in range(11)), 6141)
    f.p("(The slide puts a $\\sum$ in front of this formula. It doesn't need one: the formula already "
        "{B:is} the total.)", 12.5, C.GREY, gap=8)
    f.p("{b:When $r = 1$} the formula gives $\\frac{a \\times 0}{0}$, which means nothing. But then the "
        "list is just $a, a, a, \\dots$, so add it directly: $4 + 4 + 4 + \\dots$ (10 terms) $= 10 \\times 4 = 40$.",
        14, gap=6)
    ch.check(sum(4 for _ in range(10)), 40)
    f.p("{b:Negative ratio:} $2 - 6 + 18 - 54 + 162$ has $a = 2$, $r = -3$, $n = 5$:", 14, gap=6)
    step(f, r"S_5=\frac{2(1-(-3)^5)}{1-(-3)}=\frac{2(1+243)}{4}=122", "(−3)⁵ = −243: keep the brackets", size=19,
         color=C.GREEN)
    ch.check(sum(2 * (-3) ** i for i in range(5)), 122)


def infinity(ch):
    f = flow(ch)
    sec(f, "Walking halfway to the wall, forever", room=460)
    rule_box(f, "sum to infinity of a G.P.", [
        "$S_\\infty=\\dfrac{a}{1-r}$, {B:only when} $-1<r<1$ (written $|r|<1$). Then $r^n\\to0$ and the "
        "sums settle on this value: the series {B:converges}.",
        "{R:No sum to infinity} when $r\\geq1$ or $r\\leq-1$: the terms don't shrink, so the total grows "
        "without limit or swings about forever.",
    ], C.ORANGE)
    f.p("Stand 1 m from a wall. Walk half the distance, then half what's left, then half again... "
        "You walk $\\frac12 + \\frac14 + \\frac18 + \\dots$ and never stop, yet you never pass the wall:",
        14, gap=10)
    y_ = f.reserve(64)
    pg = f.pg
    x0, bw = L + 20, 420
    pg.rect(x0 + bw, y_ - 4, 8, 44, C.BROWN, 1, fillcolor=C.LIGHT[C.BROWN])
    pos = 0
    cols = [C.ORANGE, C.BLUE, C.GREEN, C.PURPLE, C.PINK, C.TEAL, C.ORANGE]
    for k in range(7):
        seg = bw / 2 ** (k + 1)
        pg.rect(x0 + pos, y_ + 8, seg, 20, cols[k], 0.8, fillcolor=C.LIGHT[cols[k]])
        if k < 4:
            pg.eq(x0 + pos + seg / 2, y_ + 18, rf"\tfrac1{{{2 ** (k + 1)}}}", 11, cols[k], align="center",
                  valign="middle")
        pos += seg
    pg.note(x0, y_ + 34, "the pieces fill the gap closer and closer: the total heads to exactly 1 m", C.GREY, 14)
    f.p("{b:The same sum, folded into a square.} Let a square have area 1. Shade half of it, then half of "
        "what's left, then half of that...", 14, gap=8)
    y_ = f.reserve(160)
    pg = f.pg
    S0 = 150
    rx, ry, rw, rh = L + 30, y_ + 4, S0, S0
    shaded = 0
    for k in range(10):
        if k % 2 == 0:
            piece, rem = (rx, ry, rw / 2, rh), (rx + rw / 2, ry, rw / 2, rh)
        else:
            piece, rem = (rx, ry, rw, rh / 2), (rx, ry + rh / 2, rw, rh / 2)
        pg.rect(*piece, cols[k % len(cols)], 0.8, fillcolor=C.LIGHT[cols[k % len(cols)]])
        if k < 5:
            pg.eq(piece[0] + piece[2] / 2, piece[1] + piece[3] / 2, rf"\tfrac1{{{2 ** (k + 1)}}}",
                  [15, 13, 11, 9, 8][k], cols[k], align="center", valign="middle")
        shaded += sp.Rational(1, 2 ** (k + 1))
        rx, ry, rw, rh = rem
    pg.rect(L + 30, y_ + 4, S0, S0, C.INK, 1.4)
    ch.check(1 - shaded, sp.Rational(1, 1024))
    pg.note(L + 210, y_ + 6, "After 1/2 + 1/4 + 1/8 the white part is 1/8.\nAfter 10 pieces it's 1/1024: a speck.\n\n"
            "The pieces never spill outside the square, and the white gap halves every time. So the total "
            "can't be more than 1, and it gets as close to 1 as you like: it IS 1.", C.INK, 14, w=R - L - 210)
    f.p("When the terms shrink (the ratio is between −1 and 1), $r^n$ gets closer and closer to 0 as "
        "$n$ grows ($0.5^{10} \\approx 0.001$). So in the G.P. sum formula the $r^n$ fades away:", 14, gap=6)
    step(f, r"S_\infty=\frac{a(1-0)}{1-r}=\frac{a}{1-r}", "valid only if −1 < r < 1", size=21, color=C.GREEN)
    ch.formula(r"S_\infty=\frac{a}{1-r}\quad(|r|<1)", "sum to infinity of a geometric progression")
    ch.symbol(r"S_\infty", "S infinity", "the sum of all the terms of a never-ending series")
    ch.symbol(r"|r|", "mod r (the modulus of r)", "the size of r ignoring its sign: |−3| = 3")
    ch.term("modulus (absolute value)", "the size of a number ignoring its sign, written |x|; |−0.5| = 0.5")
    ch.term("converge", "a never-ending sum converges if its total settles towards a fixed number")
    f.p("The slides write the condition as $|r| < 1$: the bars mean \"size, ignoring the sign\" "
        "(the {B:modulus}). Wall walk: $a = \\frac12$, $r = \\frac12$: $\\frac{1/2}{1 - 1/2} = 1$ ✓.",
        14, gap=8)
    ch.check(sp.Rational(1, 2) / (1 - sp.Rational(1, 2)), 1)
    f.p("{R:Slide check:} Lecture 13 writes $S_\\infty = \\frac{a}{r - 1}$. For the wall walk that "
        "gives $\\frac{1/2}{-1/2} = -1$: adding up positive distances can't give a negative total! "
        "The bottom must be $1 - r$.", 13.5, gap=8)
    f.p("{b:The ball, answered:} it falls 10 m, then goes up and down each bounce height: "
        "$10 + 2(6 + 3.6 + 2.16 + \\dots) = 10 + 2 \\times \\frac{6}{1 - 0.6} = 10 + 30 = 40$ m in total.",
        14, gap=6)
    ch.check_num(10 + 2 * 6 / (1 - 0.6), 40)
    f.p("{b:When there is no sum to infinity.} If $r \\geq 1$ (e.g. 3, 6, 12, ...) the total just keeps "
        "growing. If $r \\leq -1$ the terms never shrink either: with $r = -1$, $1 - 1 + 1 - 1 + \\dots$ "
        "flips between 1 and 0 forever; with $r = -2$, $1 - 2 + 4 - 8 + \\dots$ swings wider and wider. "
        "Either way it never settles, so there is no $S_\\infty$. {R:Always check $-1 < r < 1$ before using "
        "$\\frac{a}{1-r}$}: blindly using it for $r = 2$ gives $\\frac{1}{1-2} = -1$ for $1 + 2 + 4 + \\dots$, "
        "which is nonsense.", 13.5)
    ch.check([sum((-1) ** i for i in range(m)) for m in (1, 2, 3, 4)], [1, 0, 1, 0])


def which(ch):
    f = flow(ch)
    sec(f, "Which kind is it? The gaps test and the ratio test", room=300)
    f.p("Given a list, check the {B:gaps} (subtract neighbours) and the {B:ratios} (divide "
        "neighbours). Whichever stays constant tells you the type:", 14, gap=10)
    rows = [("5, 8, 11, 14", "3, 3, 3", "1.6, 1.375, ...", "A.P., d = 3", C.GREEN),
            ("2, 10, 50, 250", "8, 40, 200", "5, 5, 5", "G.P., r = 5", C.BLUE),
            ("80, 40, 20, 10", "−40, −20, −10", "0.5, 0.5, 0.5", "G.P., r = 0.5", C.BLUE),
            ("1, 4, 9, 16", "3, 5, 7", "4, 2.25, ...", "neither (squares)", C.GREY)]
    y_ = f.reserve(24 + 26 * len(rows))
    pg = f.pg
    xs = [L + 6, L + 140, L + 250, L + 370]
    for j, hd in enumerate(["list", "gaps", "ratios", "verdict"]):
        pg.text(xs[j], y_, hd, 12, C.GREY, F.BOLD)
    for i, (lst, gaps, rat, verdict, col) in enumerate(rows):
        yy = y_ + 22 + i * 26
        pg.text(xs[0], yy, lst, 12.5)
        pg.text(xs[1], yy, gaps, 12.5, C.GREEN if "A.P." in verdict else C.INK)
        pg.text(xs[2], yy, rat, 12.5, C.BLUE if "G.P." in verdict else C.INK)
        pg.text(xs[3], yy, verdict, 12.5, col, F.BOLD)


def side_by_side(ch):
    f = flow(ch)
    sec(f, "A.P. and G.P. rules side by side", room=360)
    f.p("Every formula in this chapter, in one table. The left column adds the same amount each time; "
        "the right column multiplies by the same amount.", 13.5, gap=8)
    rules_table(f, ["", "arithmetic (A.P.)", "geometric (G.P.)"], [
        ["{B:each step}", "add $d$", "multiply by $r$"],
        ["{B:find the step}", "$d=u_2-u_1$", "$r=\\dfrac{u_2}{u_1}$"],
        ["{B:$n$th term}", "$u_n=a+(n-1)d$", "$u_n=ar^{\\,n-1}$"],
        ["{B:sum of $n$ terms}", "$S_n=\\dfrac n2\\big(2a+(n-1)d\\big)$ or $S_n=\\dfrac n2(a+l)$",
         "$S_n=\\dfrac{a(1-r^n)}{1-r}$  ($r\\neq1$;  $r=1$: $S_n=na$)"],
        ["{B:sum to infinity}", "none: the terms don't shrink to 0, so the sum has no limit",
         "$S_\\infty=\\dfrac{a}{1-r}$ {R:only if} $-1<r<1$"],
        ["{B:three terms in a row} $x, y, z$", "$y-x=z-y$", "$\\dfrac yx=\\dfrac zy$"],
    ], [115, 175, 205], C.ORANGE, size=12)


def ex(f, s):
    f.need(100)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown: working backwards", room=330)
    rule_box(f, "given some facts, find the rest", [
        "Write each fact as an equation using the formulas: \"the 3rd term is 11\" means $a+2d=11$; "
        "\"the sum is 210\" means $S_n=210$.",
        "Two unknowns ($a$ and $d$, or $a$ and $r$) need two equations. For an A.P. subtract them; "
        "for a G.P. {B:divide} them, so $a$ cancels.",
        "Solve, then check by writing out the first few terms. Reject answers that make no sense "
        "(a negative or fractional number of terms).",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    a, d, r, nn = sp.symbols("a d r n")
    ex(f, "an A.P. has 3rd term 11 and 8th term 31. Find $a$ and $d$.")
    step(f, r"a+2d=11,\qquad a+7d=31", "u₃ and u₈ as equations", size=19)
    step(f, r"5d=20\ \Rightarrow\ d=4", "subtract: a cancels", size=19)
    step(f, r"a+2(4)=11\ \Rightarrow\ a=3", "back into the first", size=19, color=C.GREEN)
    ch.check(sp.solve([a + 2 * d - 11, a + 7 * d - 31], [a, d]), {a: 3, d: 4})
    f.p("{G:Check:} 3, 7, {B:11}, 15, 19, 23, 27, {B:31} ✓", 13.5, gap=8)
    ex(f, "how many terms of $3 + 7 + 11 + \\dots$ add up to 210?")
    step(f, r"\frac n2\big(2(3)+(n-1)4\big)=210", "A.P. sum with a = 3, d = 4", size=19)
    step(f, r"\frac n2(4n+2)=n(2n+1)=210\ \Rightarrow\ 2n^2+n-210=0", "a quadratic in n", size=18)
    step(f, r"(2n+21)(n-10)=0\ \Rightarrow\ n=10", "n = −10.5 is rejected: n counts terms", size=18,
         color=C.GREEN)
    ch.check(sp.solve(nn / 2 * (6 + (nn - 1) * 4) - 210, nn), [-sp.Rational(21, 2), 10])
    ch.check(sum(3 + 4 * i for i in range(10)), 210)
    ex(f, "a G.P. has 2nd term 6 and 5th term 162. Find $a$ and $r$.")
    step(f, r"ar=6,\qquad ar^4=162", "u₂ and u₅ as equations", size=19)
    step(f, r"\frac{ar^4}{ar}=r^3=27\ \Rightarrow\ r=3", "divide: a cancels", size=19)
    step(f, r"a=\frac63=2", "", size=19, color=C.GREEN)
    ch.check(sp.solve(r ** 3 - 27, r)[0], 3)
    ch.check([2 * 3, 2 * 3 ** 4], [6, 162])
    f.p("{G:Check:} 2, {B:6}, 18, 54, {B:162} ✓", 13.5, gap=8)
    ex(f, "a G.P. has first term 5 and sum to infinity 20. Find $r$.")
    step(f, r"\frac{5}{1-r}=20\ \Rightarrow\ 1-r=\tfrac14\ \Rightarrow\ r=\tfrac34", "S∞ = a/(1 − r)", size=19,
         color=C.GREEN)
    ch.check(sp.solve(5 / (1 - r) - 20, r), [sp.Rational(3, 4)])
    f.p("$r = \\frac34$ is between −1 and 1, so a sum to infinity really exists ✓.", 13.5, gap=8)
    ex(f, "what is the smallest number of terms of $1 + 2 + 4 + 8 + \\dots$ that add to more than 1000?")
    step(f, r"S_n=\frac{1(2^n-1)}{2-1}=2^n-1>1000\ \Rightarrow\ 2^n>1001", "a = 1, r = 2", size=18)
    step(f, r"2^9=512,\quad 2^{10}=1024\ \Rightarrow\ n=10", "try powers of 2", size=18, color=C.GREEN)
    ch.check_true(2 ** 9 - 1 <= 1000 < 2 ** 10 - 1)
    f.p("Trial works because the powers are easy. Chapter 22 solves $2^n > 1001$ directly with logs.",
        13.5, C.BROWN, gap=8)
    ex(f, "$k$, $2k + 1$ and $4k - 2$ are consecutive terms of an A.P. Find $k$.")
    step(f, r"(2k+1)-k=(4k-2)-(2k+1)", "equal gaps", size=19)
    step(f, r"k+1=2k-3\ \Rightarrow\ k=4", "terms 4, 9, 14 ✓", size=19, color=C.GREEN)
    kk = sp.Symbol("k")
    ch.check(sp.solve((2 * kk + 1) - kk - ((4 * kk - 2) - (2 * kk + 1)), kk), [4])


def common_mistakes(ch):
    f = flow(ch)
    sec(f, "Mistakes to avoid", room=360)
    mistakes(f, [
        (r"u_n=a+nd", r"u_n=a+(n-1)d", "n − 1 jumps to reach term n"),
        (r"u_n=ar^n", r"u_n=ar^{n-1}", "the first term has had no multiplications"),
        (r"r=2:\ S_\infty=\frac{a}{1-2}", r"r=2:\ \text{no }S_\infty", "only when −1 < r < 1"),
        (r"S_\infty=\frac{a}{r-1}", r"S_\infty=\frac{a}{1-r}", "1 minus r on the bottom"),
        (r"-3^5=243", r"(-3)^5=-243", "brackets round a negative ratio"),
    ])


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("A.P. term", r"u_n=a+(n-1)d", "$d$ = any term minus the one before"),
        ("A.P. sum", r"S_n=\frac n2\big(2a+(n-1)d\big)", None),
        ("A.P. sum (last term l)", r"S_n=\frac{(a+l)}{2}\,n", None),
        ("Number of terms", r"n=\frac{l-a}{d}+1", "one more term than gaps"),
        ("G.P. term", r"u_n=ar^{n-1}", "$r$ = any term divided by the one before"),
        ("G.P. sum", r"S_n=\frac{a(1-r^n)}{1-r}", "$r\\neq1$; if $r=1$, $S_n=na$"),
        ("Sum to infinity", r"S_\infty=\frac{a}{1-r}\quad(|r|<1)", "none if $r\\geq1$ or $r\\leq-1$"),
        ("Sigma", r"\sum_{i=1}^{n}f(i)=f(1)+f(2)+\dots+f(n)", "a for-loop: add for each counter value"),
        ("Odd numbers", r"1+3+5+\dots+(2n-1)=n^2", None),
        ("Two terms given", None, "two equations; subtract (A.P.) or divide (G.P.)"),
        ("Sum given, find n", None, "set $S_n$ equal to the total and solve for $n$ (often a quadratic); "
         "$n$ must be a positive whole number"),
    ], C.ORANGE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Piggy banks and bouncing balls: your turn", fresh=True)
    f.p("Answers in grey. For sums, try the first few terms by hand to check your formula.", 13.5, gap=10)
    groups = [
        ("Arithmetic", ["Find the 20th term of 7, 10, 13, ...", "How many terms in 5, 9, 13, ..., 81?",
                        "Add 1 + 2 + ... + 50", "Add 7 + 10 + 13 + ... (20 terms)",
                        "An A.P. starts at 4 and its 10th term is 31. Find d."],
         "1. 64   2. 20   3. 1275   4. 710   5. 3"),
        ("Sigma", ["Write out and add: Σ from i = 1 to 5 of (2i + 1)", "Write 4 + 8 + 12 + ... + 40 using Σ"],
         "6. 3 + 5 + 7 + 9 + 11 = 35   7. Σ from i = 1 to 10 of 4i  (total 220)"),
        ("Geometric", ["Find the 8th term of 2, 6, 18, ...", "Add 5 + 10 + 20 + ... (8 terms)",
                       "Sum to infinity: 12 + 6 + 3 + ...", "Sum to infinity: 1 − 1/3 + 1/9 − ...",
                       "Which is 1, 1.5, 2.25, 3.375: A.P. or G.P.? Does it have a sum to infinity?"],
         "8. 4374   9. 1275   10. 24   11. 3/4   12. G.P. with r = 1.5; no (r > 1)"),
        ("Find the unknown", ["An A.P. has 4th term 17 and 10th term 41. Find a and d.",
                              "How many terms of 4 + 7 + 10 + ... add up to 246?",
                              "A G.P. has 3rd term 12 and 6th term 96. Find a and r.",
                              "A G.P. has first term 8 and sum to infinity 12. Find r.",
                              "Smallest n for which 3 + 6 + 12 + ... (n terms) is more than 1000?",
                              "x, x + 3 and x + 9 are consecutive terms of a G.P. Find x."],
         "13. d = 4, a = 5 (6d = 24)   14. n = 12 (3n² + 5n − 492 = 0; reject the negative root)   "
         "15. r = 2, a = 3 (r³ = 96/12 = 8)   16. r = 1/3 (8/(1 − r) = 12)   "
         "17. n = 9 (S₈ = 3(2⁸ − 1) = 765, S₉ = 1533)   18. x = 3 ((x + 3)² = x(x + 9), so 3x = 9; terms 3, 6, 12)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(7 + 19 * 3, 64)
    ch.check(sp.Rational(81 - 5, 4) + 1, 20)
    ch.check(sum(range(1, 51)), 1275)
    ch.check(sum(7 + 3 * i for i in range(20)), 710)
    ch.check(sp.Rational(31 - 4, 9), 3)
    ch.check(sum(2 * i + 1 for i in range(1, 6)), 35)
    ch.check(sum(4 * i for i in range(1, 11)), 220)
    ch.check(2 * 3 ** 7, 4374)
    ch.check(sum(5 * 2 ** i for i in range(8)), 1275)
    ch.check(12 / (1 - sp.Rational(1, 2)), 24)
    ch.check(1 / (1 + sp.Rational(1, 3)), sp.Rational(3, 4))
    a, d, r, nn, xx = sp.symbols("a d r n x")
    ch.check(sp.solve([a + 3 * d - 17, a + 9 * d - 41], [a, d]), {a: 5, d: 4})
    ch.check(sp.solve(nn / 2 * (8 + (nn - 1) * 3) - 246, nn), [-sp.Rational(41, 3), 12])
    ch.check(sp.expand(2 * (nn / 2 * (8 + (nn - 1) * 3) - 246)), 3 * nn ** 2 + 5 * nn - 492)
    ch.check([3 * 2 ** 2, 3 * 2 ** 5], [12, 96])
    ch.check(sp.solve(8 / (1 - r) - 12, r), [sp.Rational(1, 3)])
    ch.check([3 * (2 ** 8 - 1), 3 * (2 ** 9 - 1)], [765, 1533])
    ch.check(sp.solve((xx + 3) ** 2 - xx * (xx + 9), xx), [3])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    words(ch)
    arithmetic(ch)
    gauss(ch)
    sigma(ch)
    geometric(ch)
    geo_sum(ch)
    infinity(ch)
    which(ch)
    side_by_side(ch)
    find_unknown(ch)
    common_mistakes(ch)
    summary(ch)
    your_turn(ch)
