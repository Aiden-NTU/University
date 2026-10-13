"""Chapter 21 - The exponential function. Folding paper to the Moon, a race between x^2 and 2^x,
growth and decay as mirror images, compound interest turning into the number e, and cooling tea
and a draining capacitor as real exponential decay."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 21
NUM = 21
TITLE = "The exponential function"
SHORT = "Exponentials"
SLUG = "Exponential"
ACCENT = C.RED
REQUIRES = ["powers", "index-laws", "zero-power", "negative-powers", "multiplier", "percentage-change",
            "graph-of-function", "asymptote", "function", "standard-form", "substitution", "geometric-progression",
            "units", "rounding"]
INTRODUCES = ["exponential-function", "exponential-growth", "exponential-decay", "compound-interest",
              "e-number", "exp-notation", "time-constant"]

PAPER = "#fffafa"
t = sp.Symbol("t")


def icon(pg, x0, y0):
    pg.poly([(x0 + 1 + i * 1.6, y0 + 16 - 15 * (2 ** (i / 2.5) - 1) / (2 ** 4 - 1)) for i in range(11)], C.RED, 1.5)
    pg.line(x0 + 1, y0 + 17, x0 + 18, y0 + 17, C.RED, 0.8)


def sec(f, t_, **kw):
    section(f, t_, C.RED, icon, **kw)


def box(f, latex, size=22, col=C.RED, h=None):
    pg = f.pg
    w, hh, _ = pg.eq_size(latex, size)
    bw, bh = max(260, w + 50), (h or hh + 22)
    y_ = f.reserve(bh + 8)
    pg = f.pg
    pg.rect(L + (W - bw) / 2, y_, bw, bh, col, 1.6, fillcolor=C.LIGHT[col], r=8)
    pg.eq(L + W / 2, y_ + bh / 2, latex, size, align="center", valign="middle")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 21, "The exponential function", "fold a sheet of paper 42 times and reach "
                     "the Moon", C.RED, PAPER)
    base = 340
    for k in range(6):
        n = 2 ** k
        hh = min(n * 3, 100)
        xx = L + 30 + k * 44
        for i in range(min(n, 34)):
            pg.line(xx, base - i * hh / min(n, 34), xx + 30, base - i * hh / min(n, 34), C.GREY, 0.6)
        pg.rect(xx, base - hh, 30, hh, C.RED, 1.0)
        pg.text(xx + 15, base + 4, f"{k} folds", 9.5, C.GREY, align="center")
        pg.text(xx + 15, base - hh - 16, f"{n}", 11, C.RED, F.BOLD, align="center")
    pg.circle(L + 420, 230, 26, C.GREY, 1.2, fillcolor="#eceff1")
    pg.circle(L + 410, 222, 5, C.GREY, 0.8, fillcolor="#cfd8dc")
    pg.circle(L + 428, 240, 4, C.GREY, 0.8, fillcolor="#cfd8dc")
    pg.note(L + 300, 270, "each fold doubles\nthe layers: 1, 2, 4, 8...", C.RED, 16)
    f = ch.flow(top=390)
    f.p("Most growth you know is {B:adding}: a taxi fare goes up £2 per mile. {B:Exponential} growth "
        "is {B:multiplying}: the amount doubles (or grows by 5%, or halves) at every step. It starts "
        "slowly and then explodes, which is why it surprises everyone.", 14, gap=10)
    f.p("You'll see it race against $x^2$, meet its mirror image (decay), and watch the famous number "
        "$e = 2.718...$ appear out of a bank account. Then two real decays from your lectures: "
        "cooling and the current in a circuit.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 7} {y:(power vs exponential, growth vs decay, the number e).}", 12.5)


def folding(ch):
    f = flow(ch)
    sec(f, "Folding paper: multiply, multiply, multiply")
    f.p("A sheet of paper is about 0.1 mm thick. Each fold {B:doubles} the thickness. After $n$ folds "
        "there are $2^n$ layers:", 14, gap=8)
    rows = [(0, "0.1 mm", "a sheet"), (10, "102 mm", "a paperback book"), (20, "105 m", "a 30-storey tower"),
            (30, "107 km", "into space"), (42, "440,000 km", "past the Moon (384,000 km)")]
    y_ = f.reserve(24 + 24 * len(rows))
    pg = f.pg
    for j, hd in enumerate(["folds n", "layers 2ⁿ", "thickness", "about as tall as"]):
        pg.text([L + 6, L + 80, L + 210, L + 320][j], y_, hd, 12, C.GREY, F.BOLD)
    for i, (k, th, like) in enumerate(rows):
        yy = y_ + 22 + i * 24
        pg.text(L + 6, yy, str(k), 13, C.INK, F.BOLD)
        pg.text(L + 80, yy, f"{2 ** k:,}".replace(",", " "), 13, C.RED)
        pg.text(L + 210, yy, th, 13)
        pg.text(L + 320, yy, like, 13, C.GREY)
    ch.check_num(0.1 * 2 ** 42 / 1e6, 439804.65, tol=0.1)
    ch.check_num(0.1 * 2 ** 20 / 1000, 104.86, tol=0.01)
    f.p("(Nobody can actually fold paper 42 times; about 7 is the limit. But the {B:maths} is the "
        "point.) The thickness is $0.1 \\times 2^n$ mm. Notice where the letter is: {B:up in the "
        "power}. That's what makes a function exponential.", 14, gap=8)
    ch.term("exponential function", "a function with the variable in the power, like 2ˣ or eˣ")
    f.p("{h:Chapter 17 link:} the layers 1, 2, 4, 8, ... are a geometric progression with $r = 2$. "
        "An exponential function is a G.P. that's allowed to take in-between inputs too.", 13.5, C.BROWN)


def race(ch):
    f = flow(ch)
    sec(f, "The race: x² against 2ˣ", room=500)
    f.p("They look similar, but in $x^2$ the letter is the {B:base} (a power function, Chapter 19) and "
        "in $2^x$ the letter is the {B:power} (exponential). Lecture 7 races them:", 14, gap=8)
    xs = [0, 1, 2, 3, 4, 5, 6, 8, 10, 20]
    y_ = f.reserve(64)
    pg = f.pg
    pg.text(L + 6, y_, "x", 12, C.INK, F.BOLD)
    pg.text(L + 6, y_ + 20, "x²", 12, C.BLUE, F.BOLD)
    pg.text(L + 6, y_ + 40, "2ˣ", 12, C.RED, F.BOLD)
    for i, v in enumerate(xs):
        xx = L + 60 + i * 44
        pg.text(xx, y_, str(v), 12, C.INK, align="center")
        pg.text(xx, y_ + 20, f"{v * v}", 11, C.BLUE, F.BOLD if v * v > 2 ** v else F.SANS, align="center")
        s = f"{2 ** v}" if v < 20 else "1.05M"
        pg.text(xx, y_ + 40, s, 11, C.RED, F.BOLD if 2 ** v > v * v else F.SANS, align="center")
    f.p("From $x = 2$ to 4 they swap leads and tie at 16. After that, $2^x$ runs away: at $x = 20$ it's "
        "over a million while $x^2$ is only 400. (Bold = the leader.)", 14, gap=8)
    ch.check(2 ** 4, 4 ** 2)
    ch.check(2 ** 20, 1048576)
    y_ = f.reserve(170)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 220, 140, (-3, 6), (0, 40))
    ax.grid(1, 5)
    ax.axes("x", "y", 1, 10, size=8)
    ax.curve(lambda v: v * v, color=C.BLUE, width=2)
    ax.curve(lambda v: 2 ** v, color=C.RED, width=2)
    ax.label(5.1, 25, "{B:x²}", 11, dx=-30, dy=-4)
    ax.label(5.1, 34, "{R:2ˣ}", 11, dx=4, dy=-16)
    pg.note(L + 280, y_ + 10, "Every step right, x² adds a bit more\n(+5, then +7, then +9...).\n\n2ˣ DOUBLES "
            "every step. Doubling\nalways wins in the end.\n\nOn the left, 2ˣ never goes negative\n"
            "or reaches 0: 2⁻³ = 1/8.", C.GREY, 15)
    f.p("{h:The \"where's the x?\" test:} letter in the base → power function. Letter in the power → "
        "exponential.", 13.5, C.BROWN)


def shape(ch):
    f = flow(ch)
    sec(f, "The shape: growth and its mirror, decay", room=440)
    y_ = f.reserve(180)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 230, 150, (-3, 3), (0, 8))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 1, size=8)
    for base_, col in [(2, C.RED), (3, C.ORANGE), (0.5, C.BLUE)]:
        ax.curve(lambda v, b=base_: b ** v, color=col, width=2)
    ax.dot(0, 1, C.INK, 4)
    ax.label(1.9, 7.4, "{O:3ˣ}", 11, dx=-6, dy=-4)
    ax.label(2.6, 6.2, "{R:2ˣ}", 11, dx=-6, dy=-4)
    ax.label(-2.9, 7.2, "{B:(1/2)ˣ = 2⁻ˣ}", 11, dx=2, dy=-4)
    pg.note(L + 290, y_ + 10, "Every one passes through (0, 1),\nbecause anything to the power 0\nis 1 "
            "(Chapter 9).", C.INK, 15)
    pg.note(L + 290, y_ + 70, "Base bigger than 1: GROWTH.\nBigger base: steeper.", C.RED, 15)
    pg.note(L + 290, y_ + 112, "Base between 0 and 1: DECAY.\n2⁻ˣ is 2ˣ reflected in the y-axis.", C.BLUE, 15)
    ch.check(sp.Rational(1, 2) ** 3, 2 ** -3)
    f.p("All of them hug the x-axis on one side without ever touching it: the x-axis is an "
        "{B:asymptote} (Chapter 19). Lecture 7: growth models savings (and student debt!); decay "
        "models radioactivity and electric currents dying away.", 14, gap=8)
    ch.term("exponential growth", "increase by the same multiplier (bigger than 1) each step")
    ch.term("exponential decay", "decrease by the same multiplier (between 0 and 1) each step")


def money(ch):
    f = flow(ch)
    sec(f, "Start amount × multiplier to the power of steps", room=340)
    f.p("Real exponentials are written $y = A \\times b^x$: $A$ is the {B:starting amount}, $b$ is the "
        "{B:multiplier per step} (Chapter 4's multipliers), and $x$ counts the steps.", 14, gap=6)
    box(f, r"y=A\times b^{\,x}")
    f.p("{b:Savings:} £1000 at 5% interest a year. Each year the money is multiplied by 1.05:", 14, gap=6)
    step(f, r"1000\times1.05\times1.05\times\dots=1000\times1.05^{\,t}", "t years of × 1.05", size=18)
    step(f, r"1000\times1.05^{10}\approx1628.89", "after 10 years: £1628.89", size=18, color=C.GREEN)
    ch.check_num(1000 * 1.05 ** 10, 1628.89, tol=0.01)
    ch.term("compound interest", "interest added each period and then earning interest itself: amount = A × (1 + rate)ᵗ")
    f.p("Compare simple interest (£50 added every year, a straight line): £1500 after 10 years. The "
        "extra £128.89 is interest earning interest.", 14)


def find_e(ch):
    f = flow(ch)
    sec(f, "The number e falls out of a bank account", room=500)
    f.p("A generous bank offers {B:100% interest} per year on £1. Paid once at the end: £2. But what if "
        "they pay {B:half} of it (50%) every six months, so the first half starts earning too? Or "
        "a quarter every three months? Paying $n$ times a year multiplies by $(1 + \\frac1n)$, $n$ times:",
        14, gap=8)
    rows = [(1, "once a year"), (2, "every 6 months"), (4, "every 3 months"), (12, "monthly"),
            (365, "daily"), (8760, "hourly"), (1000000, "a million times")]
    y_ = f.reserve(22 + 22 * len(rows))
    pg = f.pg
    pg.text(L + 6, y_, "paid n times", 12, C.GREY, F.BOLD)
    pg.text(L + 190, y_, "(1 + 1/n)ⁿ", 12, C.GREY, F.BOLD)
    for i, (nn, lab) in enumerate(rows):
        yy = y_ + 22 + i * 22
        v = (1 + 1 / nn) ** nn
        pg.text(L + 6, yy, f"{nn:,}  ({lab})".replace(",", " "), 12.5)
        pg.text(L + 190, yy, f"£{v:.5f}", 12.5, C.RED, F.MONO)
        pg.rect(L + 300, yy + 2, (v - 1.9) / 0.9 * 180, 11, C.RED, 0.6, fillcolor=C.LIGHT[C.RED])
    pg.line(L + 300 + (math.e - 1.9) / 0.9 * 180, y_ + 16, L + 300 + (math.e - 1.9) / 0.9 * 180, y_ + 22 + 22 * 7,
            C.RED, 1.2, dash=(3, 2))
    pg.note(L + 300 + (math.e - 1.9) / 0.9 * 180 - 30, y_ - 6, "a wall at 2.718...", C.RED, 13, solid=False)
    ch.check_num((1 + 1 / 12) ** 12, 2.61304, tol=1e-4)
    ch.check_num((1 + 1 / 1e6) ** 1e6, math.e, tol=1e-5)
    f.p("More often helps less and less. It never passes a ceiling of about {B:2.71828}. That number "
        "is called $e$ (Lecture 7: $e = (1 + \\frac1n)^n$ as $n \\to \\infty$). Like $\\pi$, nobody "
        "invented it and its decimals never end or repeat.", 14, gap=8)
    ch.symbol(r"e", "e (Euler's number)", "2.71828..., the base of natural growth")
    ch.symbol(r"\to\infty", "tends to infinity", "gets bigger and bigger without end")
    ch.term("e", "the number 2.71828..., the limit of (1 + 1/n)ⁿ; the natural base for growth and decay")
    f.p("The function $e^x$ is {B:the} exponential function; you'll also see it written $\\exp(x)$. "
        "Your calculator has an $e^x$ button (usually shift + ln). It behaves just like $2^x$ or $3^x$, "
        "sitting between them, and it's the one nature and calculus prefer (Chapter 34 shows why).",
        14)
    ch.symbol(r"\exp(x)", "exp of x", "another way to write eˣ")


def decay(ch):
    f = flow(ch)
    sec(f, "Real decay: cooling tea and a draining capacitor", room=500)
    f.p("A mug of tea at 90 °C cools in a 20 °C room. The {B:difference} from room temperature (70 °C "
        "to start) decays exponentially:", 14, gap=6)
    step(f, r"T=20+70e^{-0.1t}", "t in minutes", size=20)
    rows = [0, 10, 20, 30, 60]
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 220, 120, (0, 60), (0, 100))
    ax.grid(10, 20)
    ax.axes("t", "T", 10, 20, size=8)
    ax.curve(lambda v: 20 + 70 * math.exp(-0.1 * v), color=C.RED, width=2)
    ax.hline(20, C.BLUE, 1.2)
    for v in rows:
        ax.dot(v, 20 + 70 * math.exp(-0.1 * v), C.RED, 3)
    pg.note(L + 280, y_ + 6, "t = 0:   20 + 70 × 1 = 90 °C\nt = 10:  20 + 70e⁻¹ ≈ 45.8 °C\nt = 20:  ≈ 29.5 °C\n"
            "t = 30:  ≈ 23.5 °C\n\nIt creeps towards 20 °C (blue\nasymptote) but never gets there.", C.GREY, 15)
    ch.check_num(20 + 70 * math.exp(-1), 45.75, tol=0.01)
    ch.check_num(20 + 70 * math.exp(-2), 29.47, tol=0.01)
    f.p("{b:The capacitor} (Lecture 7, Question 2). A current starts at $I$ and dies away:", 14, gap=6)
    step(f, r"i=Ie^{-t/CR}", "C and R are the circuit's capacitance and resistance", size=20)
    f.p("When $t = CR$ the power is $-1$, so $i = Ie^{-1} \\approx 0.37I$: the current has dropped to "
        "37%. $CR$ is called the {B:time constant}. After another $CR$ it's 37% of that, and so on: "
        "the same fraction lost in every equal stretch of time. That's the fingerprint of every "
        "exponential decay.", 14, gap=8)
    ch.check_num(math.exp(-1), 0.3679, tol=1e-4)
    ch.term("time constant", "for e^(−t/τ), the time τ in which the quantity drops to 1/e ≈ 37% of its value")
    f.p("Chapter 22 answers the reverse question, \"how {B:long} until the current is 10%?\", which "
        "needs logarithms.", 13.5, C.BROWN)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Folding paper: your turn", fresh=True)
    f.p("Answers in grey. Use a calculator for the e questions.", 13.5, gap=10)
    groups = [
        ("Power or exponential?", ["y = x⁵", "y = 5ˣ", "y = 3 × 0.8ˣ", "y = 1/x²"],
         "1. power   2. exponential growth   3. exponential decay   4. power"),
        ("Using y = A × bˣ", ["A colony of 200 bacteria doubles every hour. How many after 6 hours?",
                              "A £15,000 car loses 20% of its value each year. Value after 3 years?",
                              "£500 at 3% compound interest for 4 years?"],
         "5. 200 × 2⁶ = 12,800   6. 15,000 × 0.8³ = £7680   7. 500 × 1.03⁴ ≈ £562.75"),
        ("e", ["Work out e² and e⁻² (2 d.p.)", "Using T = 20 + 70e^(−0.1t), find T when t = 5.",
               "A current i = 4e^(−t/2) amps. Find i at t = 0 and t = 2."],
         "8. 7.39 and 0.14   9. about 62.5 °C   10. 4 A and 4e⁻¹ ≈ 1.47 A"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.RED, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(200 * 2 ** 6, 12800)
    ch.check_num(15000 * 0.8 ** 3, 7680)
    ch.check_num(500 * 1.03 ** 4, 562.75, tol=0.01)
    ch.check_num(math.exp(2), 7.39, tol=0.005)
    ch.check_num(20 + 70 * math.exp(-0.5), 62.46, tol=0.01)
    ch.check_num(4 * math.exp(-1), 1.47, tol=0.005)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    folding(ch)
    race(ch)
    shape(ch)
    money(ch)
    find_e(ch)
    decay(ch)
    your_turn(ch)
