"""Chapter 24 - Descriptive statistics (Lecture 4). Squash a pile of numbers into three or four you can
hold in your head: the mean as levelling towers, the median as the middle of a queue of stick figures,
a billionaire walking into a pub, the box plot drawn under the lecture's 17 values, deviations as a
tug of war that always cancels, variance as the area of literal squares, and why samples use n - 1."""
import math
import statistics as st

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 24
NUM = 24
TITLE = "Statistics: averages and spread"
SHORT = "Statistics"
SLUG = "Statistics"
ACCENT = C.BLUE
REQUIRES = ["sigma-notation", "subscript-notation", "powers", "roots", "greek-letters", "fraction", "division",
            "rounding", "dotplot", "histogram", "outlier", "frequency", "numerical-data", "area", "units",
            "standard-form"]
INTRODUCES = ["average", "mean", "median", "mode", "skew", "range", "quartiles", "interquartile-range",
              "box-plot", "deviation", "sum-of-squares", "variance", "standard-deviation", "population-sample",
              "bessel-correction"]

PAPER = "#fafcff"
DATA17 = [1, 2, 3, 5, 5, 6, 8, 18, 25, 34, 47, 56, 60, 69, 71, 88, 94]


def icon(pg, x0, y0):
    for k, h in enumerate([8, 14, 11, 5]):
        pg.rect(x0 + 1 + k * 4.4, y0 + 18 - h, 3.4, h, C.BLUE, 0.6, fillcolor=C.BLUE)


def sec(f, t_, **kw):
    section(f, t_, C.BLUE, icon, **kw)


def stick(pg, x, yfoot, h, col=C.INK, w=1.4):
    head = h * 0.13
    pg.circle(x, yfoot - h + head, head, col, w)
    neck, hip = yfoot - h + 2 * head, yfoot - h * 0.42
    pg.line(x, neck, x, hip, col, w)
    pg.line(x, hip, x - h * 0.13, yfoot, col, w)
    pg.line(x, hip, x + h * 0.13, yfoot, col, w)
    pg.line(x - h * 0.16, neck + h * 0.12, x + h * 0.16, neck + h * 0.12, col, w)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 24, "Statistics: averages and spread", "three numbers that tell the whole story",
                     C.BLUE, PAPER)
    hs = [52, 60, 44, 70, 56, 48, 64]
    for i, h in enumerate(sorted(hs)):
        stick(pg, L + 30 + i * 34, 290, h, C.RED if i == 3 else C.BLUE)
    pg.note(L + 10, 300, "line them up by height:\nthe one in the middle is the median", C.RED, 15)
    for k, (s_, col) in enumerate([("TYPICAL?", C.RED), ("HOW FAR?", C.ORANGE), ("HOW SPREAD?", C.GREEN)]):
        pg.rect(L + 300, 205 + k * 36, 170, 28, col, 1.3, fillcolor=C.LIGHT[col], r=6)
        pg.text(L + 385, 211 + k * 36, s_, 13, col, F.BOLD, align="center")
    f = ch.flow(top=370)
    f.p("Lecture 4 starts from a fact about brains: {B:we can only work with about four things at "
        "once}. A data set of hundreds of values is useless until we squash it into three or four "
        "summary numbers:", 14, gap=8)
    f.p("{R:the average} (what number is typical?), {o:the range} (what are the outer limits?) and "
        "{g:the variance} (how spread out are the values?).", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 4} {y:(mean, median, mode, quartiles, box plot, variance, standard "
        "deviation, sample vs population).}", 12.5)


def mean(ch):
    f = flow(ch)
    sec(f, "The mean: level the towers")
    f.p("Five friends have 2, 5, 3, 6 and 4 sweets. The {B:mean} is what each would get if they "
        "{B:shared them out equally}. Picture towers of blocks and move blocks from tall towers to "
        "short ones until they're level:", 14, gap=10)
    vals = [2, 5, 3, 6, 4]
    y_ = f.reserve(150)
    pg = f.pg
    bs = 18
    for side, xoff in [(0, L + 10), (1, L + 280)]:
        for i, v in enumerate(vals):
            hgt = 4 if side else v
            for b in range(hgt):
                moved = side and b >= v
                pg.rect(xoff + i * 34, y_ + 120 - (b + 1) * bs, bs * 1.4, bs - 2, C.ORANGE if moved else C.BLUE,
                        0.8, fillcolor=C.LIGHT[C.ORANGE if moved else C.BLUE])
        pg.line(xoff - 6, y_ + 120, xoff + 5 * 34, y_ + 120, C.INK, 1.2)
    pg.line(L + 4, y_ + 120 - 4 * bs - 1, L + 10 + 5 * 34, y_ + 120 - 4 * bs - 1, C.RED, 1.2, dash=(4, 3))
    pg.note(L + 10, y_ + 124, "before: 2, 5, 3, 6, 4", C.GREY, 14)
    pg.note(L + 280, y_ + 124, "after: every tower is 4 (orange = moved)", C.GREY, 14)
    pg.arrow(L + 200, y_ + 60, L + 266, y_ + 60, C.GREY, 1.4, head=6)
    ch.check(sp.Rational(sum(vals), len(vals)), 4)
    f.p("Sharing out equally is the same as: {B:add them all up, divide by how many there are.}", 14, gap=6)
    step(f, r"\bar x=\frac{2+5+3+6+4}{5}=\frac{20}{5}=4", "", size=19)
    f.p("Lecture 4 writes it with the sigma (adding-up) sign of Chapter 17:", 14, gap=6)
    y_ = f.reserve(118)
    pg = f.pg
    pg.eq(L + 30, y_ + 4, r"\bar x=\frac{\displaystyle\sum_{i=1}^{n}x_i}{n}", 24, C.BLUE)
    pg.note(L + 200, y_ + 2, "x̄  (\"x bar\") = the mean", C.RED, 15)
    pg.note(L + 200, y_ + 22, "Σ xᵢ = add up every value x₁, x₂, ... xₙ", C.RED, 15)
    pg.note(L + 200, y_ + 42, "n = how many values there are", C.RED, 15)
    ch.term("mean", "add all the values and divide by how many there are (the fair-share average)")
    ch.symbol(r"\bar x", "x bar", "the mean of a sample of x-values")
    ch.formula(r"\bar x=\frac{\sum x_i}{n}", "mean")
    ch.term("average", "a single typical value for a data set: mean, median or mode")
    f.p("{b:The lecture's giant example:} UK GDP is about 2.5 trillion dollars and there are about 65 "
        "million people, so the mean income is $2.5\\times10^{12}\\div(6.5\\times10^{7}) \\approx 38\\,500$ "
        "dollars, about £24,000.", 14)
    ch.check_num(2.5e12 / 6.5e7, 38462, tol=1)


def median_mode(ch):
    f = flow(ch)
    sec(f, "The median: the middle of the queue")
    f.p("Line everyone up in order of size. The {B:median} is the person standing in the middle.", 14, gap=12)
    y_ = f.reserve(150)
    pg = f.pg
    hs = [44, 50, 55, 61, 70]
    for i, h in enumerate(hs):
        stick(pg, L + 30 + i * 40, y_ + 90, h, C.RED if i == 2 else C.BLUE)
        pg.text(L + 30 + i * 40, y_ + 94, str(i + 1), 10, C.GREY, align="center")
    pg.note(L + 18, y_ + 106, "5 people: position 3 is the middle", C.RED, 14)
    hs = [44, 50, 55, 61]
    for i, h in enumerate(hs):
        stick(pg, L + 290 + i * 40, y_ + 90, h, C.PURPLE if i in (1, 2) else C.BLUE)
        pg.text(L + 290 + i * 40, y_ + 94, str(i + 1), 10, C.GREY, align="center")
    pg.line(L + 350, y_ + 20, L + 350, y_ + 92, C.RED, 1.2, dash=(3, 3))
    pg.note(L + 278, y_ + 106, "4 people: nobody is in the middle,\nso go halfway between 2 and 3", C.PURPLE, 14)
    f.gap(14)
    f.p("The position of the middle is $\\frac{n+1}{2}$ (Lecture 4 writes $M = x_{(n+1)/2}$). For "
        "$[1, 2, 3, 4, 5]$ that's position 3, so $M = 3$. For $[1, 2, 3, 4]$ it's position 2.5, so halfway "
        "between the 2nd and 3rd values: $M = \\frac{2+3}{2} = 2.5$.", 14, gap=8)
    ch.check(st.median([1, 2, 3, 4, 5]), 3)
    ch.check_num(st.median([1, 2, 3, 4]), 2.5)
    ch.term("median", "the middle value when the data are in order; position (n+1)/2")
    f.p("{b:The mode} is the {B:most common} value: the tallest stack in a dotplot. In 3, 5, 5, 6, 8, 5, 2 "
        "the mode is 5. No formula, just counting. For measurements like wages, where nobody earns "
        "exactly the same, you first group them into brackets (Chapter 23), then the mode is the "
        "busiest bracket.", 14)
    ch.check(st.mode([3, 5, 5, 6, 8, 5, 2]), 5)
    ch.term("mode", "the most common value (or busiest group)")


def pub(ch):
    f = flow(ch)
    sec(f, "A billionaire walks into a pub", room=480)
    f.p("Five people in a pub earn £20k, £22k, £25k, £28k and £30k. Mean £25k, median £25k. Then a "
        "billionaire earning £1,000 000k walks in:", 14, gap=10)
    before = [20, 22, 25, 28, 30]
    after = before + [1_000_000]
    y_ = f.reserve(110)
    pg = f.pg
    for i in range(5):
        stick(pg, L + 30 + i * 32, y_ + 80, 50, C.BLUE)
    stick(pg, L + 30 + 5 * 32 + 20, y_ + 80, 64, C.ORANGE, 2)
    pg.rect(L + 30 + 5 * 32 + 8, y_ + 8, 24, 8, C.ORANGE, 1, fillcolor=C.ORANGE)
    pg.text(L + 280, y_ + 10, "mean", 13, C.INK, F.BOLD)
    pg.text(L + 350, y_ + 10, "£25k  →  £166 687k", 13, C.RED, F.BOLD)
    pg.text(L + 280, y_ + 40, "median", 13, C.INK, F.BOLD)
    pg.text(L + 350, y_ + 40, "£25k  →  £26.5k", 13, C.GREEN, F.BOLD)
    pg.note(L + 280, y_ + 66, "the mean now describes nobody in the room", C.RED, 14)
    ch.check_num(st.mean(after), 166687.5, tol=1)
    ch.check_num(st.median(after), 26.5)
    f.p("One extreme value (an outlier) drags the mean but barely moves the median. Data with a long "
        "tail on one side are called {B:skewed}, and UK wages are exactly like that. Lecture 4's three "
        "answers to \"what is the average UK wage?\":", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 10, 300, 110, (0, 60), (0, 1.1))
    pg.line(ax.X(0), ax.Y(0), ax.X(60), ax.Y(0), C.INK, 1)
    ax.fill_under(lambda v: (v / 15) ** 2 * math.exp(2 - 2 * v / 15) if v > 0 else 0, 0.01, 60,
                  C.LIGHT[C.BLUE])
    ax.curve(lambda v: (v / 15) ** 2 * math.exp(2 - 2 * v / 15) if v > 0 else 0, 0.01, 60, C.BLUE, 1.6)
    for v, col, nm in [(15, C.PURPLE, "mode 15k"), (16.4, C.GREEN, "median 16.4k"), (24, C.RED, "mean 24k")]:
        ax.vline(v, col, 1.3, (4, 3), 0, 1.05)
    pg.text(ax.X(15) - 50, ax.Y(1.08), "mode 15k", 9, C.PURPLE, solid=False)
    pg.text(ax.X(16.4) + 3, ax.Y(1.08) + 12, "median 16.4k", 9, C.GREEN, solid=False)
    pg.text(ax.X(24) + 4, ax.Y(0.8), "mean 24k", 9, C.RED, solid=False)
    pg.text(ax.X(42), ax.Y(0.5), "long tail of\nhigh earners", 9, C.GREY, solid=False)
    pg.note(L + 340, y_ + 10, "The mega-rich few in the\ntail pull the mean right.\n\nMedian: usually the "
            "most\nhonest for skewed data.\nMean: best for symmetric\n(Normal) data. Mode: rarely\nused.",
            C.GREY, 14)
    ch.term("skewed data", "data with a long tail on one side; the mean is dragged towards the tail")
    f.p("Lecture 4 also lists what's wrong with the wage data itself (part-time work not "
        "pro-rata, self-reporting, tax avoidance...), and hides a puzzle on each slide: a wrong title, "
        "a bad choice of graph (Chapter 23's case 1) and overlapping brackets like \"£6000 to £7000\" "
        "then \"£7000 to £8000\": which bracket does exactly £7000 go in?", 13.5)


def boxplot(ch):
    f = flow(ch)
    sec(f, "Range, quartiles and the box plot", room=520)
    f.p("Lecture 4's 17 values, in order. We'll find five landmarks and hang a box on them.", 14, gap=10)
    y_ = f.reserve(64)
    pg = f.pg
    cw = W / 17
    marks = {0: ("min", C.GREY), 4: ("LQ", C.ORANGE), 8: ("median", C.RED), 12: ("UQ", C.ORANGE),
             16: ("max", C.GREY)}
    for i, v in enumerate(DATA17):
        col = marks[i][1] if i in marks else C.INK
        if i in marks:
            pg.rect(L + i * cw + 1, y_ + 14, cw - 2, 22, col, 1.2, fillcolor=C.LIGHT[col] if col != C.GREY else None)
            pg.text(L + i * cw + cw / 2, y_ + 40, marks[i][0], 8, col, F.BOLD, align="center")
        pg.text(L + i * cw + cw / 2, y_ + 18, str(v), 11, col, F.BOLD if i in marks else F.SANS, align="center")
        pg.text(L + i * cw + cw / 2, y_, str(i + 1), 8, C.GREY, align="center")
    f.p("{b:Median:} position $\\frac{17+1}{2} = 9$, so the 9th value: {R:25}.", 14, gap=4)
    f.p("{b:Quartiles} cut the data into quarters. Lecture 4: the quartile position is $\\frac{\\text{median "
        "position} + 1}{2} = \\frac{9+1}{2} = 5$. Count 5 from the bottom for the {o:lower quartile} "
        "(LQ = 5) and 5 from the top for the {o:upper quartile} (UQ = 60).", 14, gap=10)
    ch.check(DATA17[8], 25)
    ch.check([DATA17[4], DATA17[12]], [5, 60])
    y_ = f.reserve(100)
    pg = f.pg
    ax = Axes(pg, L + 20, y_, 440, 70, (0, 100), (0, 1))
    for v in DATA17:
        ax.dot(v, 0.85, C.BLUE, 2.6)
    top, bot = ax.Y(0.65), ax.Y(0.25)
    pg.rect(ax.X(5), top, ax.X(60) - ax.X(5), bot - top, C.ORANGE, 1.6, fillcolor=C.LIGHT[C.ORANGE])
    pg.line(ax.X(25), top, ax.X(25), bot, C.RED, 2.2)
    for a_, b_ in [(1, 5), (60, 94)]:
        pg.line(ax.X(a_), (top + bot) / 2, ax.X(b_), (top + bot) / 2, C.INK, 1.3)
    for v in (1, 94):
        pg.line(ax.X(v), top + 6, ax.X(v), bot - 6, C.INK, 1.3)
    pg.line(ax.X(0), ax.Y(0), ax.X(100), ax.Y(0), C.INK, 1)
    for v in range(0, 101, 10):
        pg.line(ax.X(v), ax.Y(0) - 3, ax.X(v), ax.Y(0) + 3, C.INK, 1)
        pg.text(ax.X(v), ax.Y(0) + 5, str(v), 9, C.GREY, align="center", solid=False)
    pg.note(ax.X(64), top - 22, "the box holds the middle half", C.ORANGE, 14, solid=False)
    rows = [("range", "largest − smallest", "94 − 1 = 93"),
            ("interquartile range (IQR)", "UQ − LQ: the width of the box", "60 − 5 = 55"),
            ("semi-interquartile range", "half the IQR", "55 ÷ 2 = 27.5")]
    y_ = f.reserve(24 * 3 + 6)
    pg = f.pg
    for k, (a_, b_, c_) in enumerate(rows):
        pg.text(L, y_ + k * 24, a_, 12.5, C.BLUE, F.BOLD)
        pg.text(L + 200, y_ + k * 24, b_, 12.5, C.INK)
        pg.text(L + 400, y_ + k * 24, c_, 12.5, C.GREEN, F.BOLD)
    ch.check(DATA17[-1] - DATA17[0], 93)
    ch.check_num((60 - 5) / 2, 27.5)
    for t_, m_ in [("range", "largest value minus smallest value"),
                   ("quartiles", "the values a quarter (LQ) and three quarters (UQ) of the way through the ordered data"),
                   ("interquartile range", "UQ − LQ: the spread of the middle half of the data"),
                   ("box plot", "a box from LQ to UQ with a line at the median and whiskers out to the min and max")]:
        ch.term(t_, m_)
    f.p("The range uses only the two most extreme values, so one outlier wrecks it. The IQR ignores "
        "the top and bottom quarters, so it's robust, like the median.", 14)


def deviation(ch):
    f = flow(ch)
    sec(f, "How spread out? A tug of war that always draws", room=440)
    f.p("Take $[1, 2, 3, 4]$: mean $2.5$. But so does $[-1000, 608, 400, 2]$! The mean can't tell them "
        "apart; we need to measure how far values sit from the mean. That distance is the "
        "{B:deviation}: $x - \\bar x$.", 14, gap=10)
    ch.check_num(st.mean([-1000, 608, 400, 2]), 2.5)
    y_ = f.reserve(124)
    pg = f.pg
    ax = Axes(pg, L + 40, y_ + 10, 400, 60, (0.5, 4.5), (0, 1))
    pg.line(ax.X(0.5), ax.Y(0), ax.X(4.5), ax.Y(0), C.INK, 1)
    ax.vline(2.5, C.RED, 1.5, (4, 3), -0.2, 1.1)
    pg.text(ax.X(2.5), ax.Y(1.1) - 14, "mean 2.5", 11, C.RED, F.BOLD, align="center")
    for k, v in enumerate([1, 2, 3, 4]):
        yy = 0.25 + 0.22 * (k % 2)
        ax.dot(v, 0, C.BLUE, 4)
        pg.text(ax.X(v), ax.Y(0) + 6, str(v), 11, C.BLUE, align="center")
        ax.arrow(2.5, yy + 0.1 * k, v, yy + 0.1 * k, C.ORANGE if v < 2.5 else C.GREEN, 1.5, head=5)
        pg.text((ax.X(v) + ax.X(2.5)) / 2, ax.Y(yy + 0.1 * k) - 14, f"{v - 2.5:+g}", 10,
                C.ORANGE if v < 2.5 else C.GREEN, F.BOLD, align="center", solid=False)
    pg.note(L + 10, y_ + 96, "left pulls: −1.5, −0.5.   Right pulls: +0.5, +1.5.   Total: 0. Always!",
            C.GREY, 15)
    ch.check(sum(v - sp.Rational(5, 2) for v in [1, 2, 3, 4]), 0)
    ch.term("deviation", "how far a value is from the mean: x − x̄ (negative if below)")
    f.p("Averaging the deviations is useless: the mean is the balance point, so the pulls to the left "
        "and right {B:always cancel to zero}. We need to get rid of the minus signs. Lecture 4's trick: "
        "{B:square them}.", 14)


def squares(ch):
    f = flow(ch)
    sec(f, "Variance: the area of the average square", room=330)
    f.p("Squaring a deviation means drawing a {B:real square} whose side is the deviation. Minus signs "
        "vanish (area is never negative), and far-away values get {B:much} bigger squares:", 14, gap=12)
    devs = [-1.5, -0.5, 0.5, 1.5]
    y_ = f.reserve(120)
    pg = f.pg
    u = 40
    xx = L + 20
    for d in devs:
        s_ = abs(d) * u
        pg.rect(xx, y_ + 70 - s_, s_, s_, C.GREEN, 1.3, fillcolor=C.LIGHT[C.GREEN])
        pg.text(xx, y_ + 76, f"({d:+g})² = {d * d:g}", 11, C.INK)
        xx += max(s_, 80) + 26
    pg.note(L + 20, y_ + 94, "sum of squares = 2.25 + 0.25 + 0.25 + 2.25 = 5", C.GREEN, 16)
    ch.check_num(sum(d * d for d in devs), 5)
    ch.term("sum of squares", "add up the squared deviations Σ(x − x̄)²")
    f.p("{b:Problem:} $[1, 1, 2, 2, 3, 3, 4, 4]$ is just as spread out, but has 8 squares, so its sum is "
        "10. Bigger groups get bigger sums. {B:Fix: divide by $n$.} That's the average square:", 14, gap=6)
    step(f, r"\frac54=1.25\qquad\frac{10}{8}=1.25", "same spread, same answer", size=19)
    ch.check_num(st.pvariance([1, 1, 2, 2, 3, 3, 4, 4]), 1.25)
    f.need(190)
    f.p("This average-square area is the {B:variance}, $\\sigma^2$. Its side length (the square root) "
        "is the {B:standard deviation} $\\sigma$, which is back in the same units as the data:", 14, gap=6)
    y_ = f.reserve(110)
    pg = f.pg
    pg.eq(L + 10, y_ + 4, r"\sigma^2=\frac{\sum(x_i-\bar x)^2}{n}", 22, C.GREEN)
    pg.eq(L + 10, y_ + 66, r"\sigma=\sqrt{1.25}\approx1.118", 20, C.GREEN)
    s_ = math.sqrt(1.25) * u
    pg.rect(L + 340, y_ + 80 - s_, s_, s_, C.GREEN, 1.6, fillcolor=C.LIGHT[C.GREEN])
    pg.note(L + 340 + s_ + 8, y_ + 20, "area 1.25 = variance\nside 1.118 = standard\ndeviation", C.GREEN, 14)
    ch.check_num(math.sqrt(1.25), 1.118, tol=0.001)
    ch.term("variance", "the mean of the squared deviations; σ² for a population")
    ch.term("standard deviation", "the square root of the variance; a typical distance from the mean, in the data's units")
    ch.symbol(r"\sigma", "sigma (lower case)", "standard deviation of a population")
    ch.formula(r"\sigma^2=\frac{\sum(x_i-\mu)^2}{N}", "population variance")
    f.p("{b:Units check (Lecture 4):} $[10, 20, 30, 40]$ has variance 125, a hundred times bigger than "
        "1.25, because squares of 10× longer sides have 100× the area. The standard deviation, $\\sqrt{125} "
        "= 11.18$, is exactly 10× bigger: sensible. That's why we usually quote $\\sigma$.", 14)
    ch.check_num(st.pvariance([10, 20, 30, 40]), 125)


def range_fallacy(ch):
    f = flow(ch)
    sec(f, "Wider range means more spread? Not always", room=260)
    f.p("Lecture 4's \"range fallacy\": $[1,1,1,1,1,1,1,1,1,1,1,1,1,5]$ has range 4, wider than "
        "$[1,2,3,4]$ (range 3). Yet its variance is $1.06$, {B:slightly less} than 1.25: thirteen values "
        "sit almost on top of the mean, and only one lonely square is big. {B:Range looks at two values; "
        "variance looks at all of them.}", 14)
    ch.check_num(st.pvariance([1] * 13 + [5]), 1.061, tol=0.001)


def sample(ch):
    f = flow(ch)
    sec(f, "Sample or population, and the mysterious n − 1", room=560)
    f.p("A {B:population} is everyone you care about (all NTU students). A {B:sample} is the handful "
        "you actually measured (this class). Lecture 4 uses different letters so you always know "
        "which you mean:", 14, gap=10)
    y_ = f.reserve(24 * 4 + 8)
    pg = f.pg
    hdr = [("", "population (Greek)", "sample (English)")]
    rows = hdr + [("mean", "μ  (\"mew\")", "x̄  (\"x bar\")"), ("standard deviation", "σ  (\"sigma\")", "s"),
                  ("how many", "N", "n")]
    for k, (a_, b_, c_) in enumerate(rows):
        fnt = F.BOLD if k == 0 else F.SANS
        pg.text(L + 10, y_ + k * 24, a_, 12.5, C.INK, F.BOLD)
        pg.text(L + 180, y_ + k * 24, b_, 12.5, C.PURPLE, fnt)
        pg.text(L + 350, y_ + k * 24, c_, 12.5, C.BLUE, fnt)
    ch.symbol(r"\mu", "mew", "the mean of a whole population")
    ch.term("population", "every member of the group you want to know about")
    ch.term("sample", "the members you actually measured, used to estimate the population")
    y_ = f.reserve(80)
    pg = f.pg
    pg.eq(L + 20, y_ + 4, r"\sigma=\sqrt{\frac{\sum(x_i-\mu)^2}{N}}", 20, C.PURPLE)
    pg.eq(L + 270, y_ + 4, r"s=\sqrt{\frac{\sum(x_i-\bar x)^2}{\blu{n-1}}}", 20, C.BLUE)
    ch.formula(r"s=\sqrt{\frac{\sum(x_i-\bar x)^2}{n-1}}", "sample standard deviation")
    f.p("{b:Why $n - 1$ (Bessel's correction)?} A sample huddles closer to {B:its own} mean than to the "
        "true population mean, because its mean was calculated from those very values. So its squares "
        "come out {B:too small}. Dividing by a slightly smaller number ($n - 1$) nudges the answer back "
        "up:", 14, gap=10)
    y_ = f.reserve(90)
    pg = f.pg
    ax = Axes(pg, L + 20, y_, 440, 60, (0, 20), (0, 1))
    pg.line(ax.X(0), ax.Y(0.2), ax.X(20), ax.Y(0.2), C.INK, 1)
    pop = [2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18]
    for v in pop:
        ax.dot(v, 0.2, C.LIGHT[C.GREY], 4)
    smp = [11, 12, 14]
    for v in smp:
        ax.dot(v, 0.2, C.BLUE, 4.5)
    ax.vline(10.07, C.PURPLE, 1.4, (4, 3), 0, 0.9)
    ax.vline(12.33, C.BLUE, 1.4, (4, 3), 0, 0.9)
    pg.text(ax.X(10.07) - 4, ax.Y(0.95), "true mean μ", 10, C.PURPLE, align="right", solid=False)
    pg.text(ax.X(12.33) + 4, ax.Y(0.95), "sample mean x̄", 10, C.BLUE, solid=False)
    pg.note(L + 20, y_ + 64, "the 3 blue values are closer to x̄ than to μ, so their spread looks smaller than "
            "it really is", C.GREY, 14, w=W - 20)
    ch.check_num(st.mean(pop), 10.07, tol=0.01)
    ch.term("Bessel's correction", "dividing by n − 1 instead of n for a sample, to undo the underestimate of spread")
    f.p("The fix matters most for small samples: dividing by 2 instead of 3 is a big change; by 999 "
        "instead of 1000 is tiny.", 14)


def recipe(ch):
    f = flow(ch)
    sec(f, "The recipe, one step per line", room=500)
    f.p("Lecture 4's \"break it down\" for the sample standard deviation of $[1, 2, 3, 4]$:", 14, gap=10)
    y_ = f.reserve(4 * 26 + 30)
    pg = f.pg
    hd = ["x", "x − x̄", "(x − x̄)²"]
    for j, h_ in enumerate(hd):
        pg.text(L + 40 + j * 110, y_, h_, 13, C.BLUE, F.BOLD, align="center")
    for i, v in enumerate([1, 2, 3, 4]):
        d = v - 2.5
        for j, s_ in enumerate([str(v), f"{d:+g}", f"{d * d:g}"]):
            pg.text(L + 40 + j * 110, y_ + 24 + i * 24, s_, 13, C.INK, F.MONO, align="center")
    pg.line(L + 180, y_ + 120, L + 260, y_ + 120, C.INK, 1)
    pg.text(L + 260, y_ + 124, "total 5", 13, C.GREEN, F.BOLD, align="center")
    labels = ["1  find the mean: 10 ÷ 4 = 2.5", "2  subtract the mean from each x",
              "3  square each one", "4  add the squares: 5", "5  divide by n − 1 = 3: 1.667",
              "6  square root: s ≈ 1.291"]
    for k, s_ in enumerate(labels):
        pg.note(L + 330, y_ + k * 22, s_, C.RED, 14)
    ch.check_num(st.stdev([1, 2, 3, 4]), 1.291, tol=0.001)
    f.gap(6)
    f.p("Compare: dividing by $n = 4$ gave $\\sigma = 1.118$ (treating the four values as the whole "
        "population). Calculators have both buttons: $\\sigma_n$ (or $\\sigma x$) and $\\sigma_{n-1}$ (or "
        "$sx$).", 14)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Data A: 3, 7, 7, 8, 10, 12, 15.   Answers in grey.", 13.5, gap=10)
    groups = [
        ("Averages", ["Mean of A", "Median of A", "Mode of A",
                      "Add 100 to data A. Which average changes most?"],
         "1. 62 ÷ 7 ≈ 8.86   2. 8   3. 7   4. the mean (it becomes 20.25; median 9)"),
        ("Spread", ["Range of A", "Median position for 11 values? Quartile position?",
                    "Population variance and σ of 2, 4, 6", "Sample s of 2, 4, 6"],
         "5. 12   6. 6th; 3rd from each end   7. 8/3 ≈ 2.67, σ ≈ 1.63   8. √(8/2) = 2"),
        ("Think", ["Why is median house price reported, not the mean?",
                   "Two classes both average 60%. What else would you want to know?"],
         "9. a few mansions skew the mean upward   10. the spread (standard deviation / IQR)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    A = [3, 7, 7, 8, 10, 12, 15]
    ch.check_num(st.mean(A), 8.857, tol=0.001)
    ch.check([st.median(A), st.mode(A)], [8, 7])
    ch.check_num(st.mean(A + [100]), 20.25)
    ch.check_num(st.median(A + [100]), 9)
    ch.check_num(st.pvariance([2, 4, 6]), 8 / 3)
    ch.check_num(st.stdev([2, 4, 6]), 2)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    mean(ch)
    median_mode(ch)
    pub(ch)
    boxplot(ch)
    deviation(ch)
    squares(ch)
    range_fallacy(ch)
    sample(ch)
    recipe(ch)
    your_turn(ch)
