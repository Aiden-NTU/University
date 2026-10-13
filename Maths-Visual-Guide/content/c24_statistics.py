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
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step, title_block

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
              "bessel-correction", "frequency-table", "grouped-data"]

PAPER = "#fafcff"
DATA17 = [1, 2, 3, 5, 5, 6, 8, 18, 25, 34, 47, 56, 60, 69, 71, 88, 94]


def icon(pg, x0, y0):
    for k, h in enumerate([8, 14, 11, 5]):
        pg.rect(x0 + 1 + k * 4.4, y0 + 18 - h, 3.4, h, C.BLUE, 0.6, fillcolor=C.BLUE)


def sec(f, t_, **kw):
    section(f, t_, C.BLUE, icon, **kw)


def ex(f, s):
    f.need(90)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


def at_position(data, p, from_top=False):
    """Value at a (possibly fractional) position in ordered data, counting from 1."""
    xs = sorted(data, reverse=from_top)
    k = int(p)
    d = p - k
    return xs[k - 1] + d * (xs[k] - xs[k - 1]) if d else xs[k - 1]


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
    rule_box(f, "the mean", [
        "mean $=\\dfrac{\\text{sum of the values}}{\\text{number of values}}$, written "
        "$\\bar x=\\dfrac{\\sum x}{n}$.",
        "Turned round: {B:total = number of values × mean}. Every \"find the missing value\" question "
        "starts here.",
    ], C.BLUE)
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
    rule_box(f, "median and mode", [
        "{B:Median:} put the values {B:in order}; the median is the value in position $\\dfrac{n+1}{2}$.",
        "If $n$ is even the position ends in .5: the median is halfway between the two middle values "
        "(add them and halve).",
        "{B:Mode:} the value that occurs most often. There can be more than one mode, or none.",
    ], C.BLUE)
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


def totals(ch):
    f = flow(ch)
    sec(f, "Missing values: work with the total", room=520)
    rule_box(f, "missing-value problems", [
        "Turn every mean you are given into a total: total = number of values × mean.",
        "Subtract the values you know from the total: what's left is the missing value (or their sum).",
        "If a value is added or removed, change the total {B:and} the count, then divide again: "
        "new mean = new total ÷ new count.",
        "Check: add the values up and divide.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    ex(f, "the mean of five numbers is 8. Four of them are 6, 7, 9 and 10. Find the fifth.")
    step(f, r"\text{total}=5\times8=40", "total = n × mean", size=19)
    step(f, r"40-(6+7+9+10)=40-32=8", "take away the four you know", size=19, color=C.GREEN)
    ch.check(5 * 8 - (6 + 7 + 9 + 10), 8)
    ch.check(st.mean([6, 7, 9, 10, 8]), 8)
    ex(f, "four values have mean 15. A fifth value, 25, is added. What is the new mean?")
    step(f, r"4\times15=60,\qquad \frac{60+25}{5}=\frac{85}{5}=17", "new total ÷ new count", size=19,
         color=C.GREEN)
    ch.check(sp.Rational(4 * 15 + 25, 5), 17)
    ex(f, "six values have mean 10. The value 20 is removed. What is the new mean?")
    step(f, r"6\times10=60,\qquad \frac{60-20}{5}=\frac{40}{5}=8", "one fewer value", size=19, color=C.GREEN)
    ch.check(sp.Rational(6 * 10 - 20, 5), 8)
    ex(f, "the mean of $x$, $2x$ and $3x$ is 12. Find $x$.")
    step(f, r"\frac{x+2x+3x}{3}=12\ \Rightarrow\ 6x=36\ \Rightarrow\ x=6", "total = 3 × 12 = 36", size=19,
         color=C.GREEN)
    xs = sp.symbols("x")
    ch.check(sp.solve(sp.Eq((xs + 2 * xs + 3 * xs) / 3, 12), xs), [6])
    ex(f, "four tests average 66. What must the fifth score be to bring the average up to 70?")
    step(f, r"5\times70-4\times66=350-264=86", "total needed − total so far", size=19, color=C.GREEN)
    ch.check(5 * 70 - 4 * 66, 86)
    mistakes(f, [
        (r"\frac{20+40}{2}=30", r"\frac{10\times20+30\times40}{40}=35",
         "group A: 10 people, mean 20; group B: 30 people, mean 40. Combine the totals, not the means"),
    ], title="Common mistake: averaging two means")
    ch.check(sp.Rational(10 * 20 + 30 * 40, 40), 35)


def freq_table(ch):
    f = flow(ch)
    sec(f, "Averages from a frequency table", room=560)
    rule_box(f, "frequency tables", [
        "$f$ = how many times the value $x$ occurs. The number of values is $n=\\sum f$ (not the number "
        "of rows).",
        "Mean $=\\dfrac{\\sum fx}{\\sum f}$: multiply each value by its frequency, add these up, divide by "
        "the total frequency.",
        "Median: position $\\frac{n+1}{2}$ with $n=\\sum f$. Keep a running total of $f$ to see which value "
        "sits in that position. Mode: the value with the biggest $f$.",
        "{B:Grouped data} (classes like 10-20): use each class's {B:midpoint} as $x$. The mean is then "
        "only an {B:estimate}, because the exact values are lost.",
    ], C.BLUE)
    ex(f, "the number of brothers and sisters of 20 students.")
    rows = [(0, 5), (1, 8), (2, 4), (3, 3)]
    run = 0
    cells = []
    for x_, f_ in rows:
        run += f_
        cells.append([str(x_), str(f_), f"{x_} × {f_} = {x_ * f_}", str(run)])
    cells.append(["{B:total}", "{B:Σf = 20}", "{B:Σfx = 25}", ""])
    rules_table(f, ["siblings x", "frequency f", "fx", "running total of f"], cells, [100, 110, 160, 125],
                C.BLUE)
    data = [x_ for x_, f_ in rows for _ in range(f_)]
    step(f, r"\bar x=\frac{\sum fx}{\sum f}=\frac{25}{20}=1.25", "", size=19, color=C.GREEN)
    ch.check(sp.Rational(sum(x_ * f_ for x_, f_ in rows), sum(f_ for _, f_ in rows)), sp.Rational(5, 4))
    ch.check_num(st.mean(data), 1.25)
    step(f, r"\text{median position}=\frac{20+1}{2}=10.5", "between the 10th and 11th values", size=18)
    f.p("The running total says values 1 to 5 are 0s and values 6 to 13 are 1s, so the 10th and 11th "
        "are both 1: {G:median = 1}. The mode is also 1 (frequency 8).", 13.5, gap=10)
    ch.check(st.median(data), 1)
    ch.check(st.mode(data), 1)
    ex(f, "grouped data: minutes spent on homework by 20 students.")
    grp = [(0, 10, 4), (10, 20, 10), (20, 40, 6)]
    cells = [[f"{a}-{b}", str(n_), f"{(a + b) / 2:g}", f"{(a + b) / 2:g} × {n_} = {(a + b) / 2 * n_:g}"]
             for a, b, n_ in grp]
    cells.append(["{B:total}", "{B:20}", "", "{B:350}"])
    rules_table(f, ["minutes", "frequency f", "midpoint x", "fx"], cells, [110, 110, 110, 165], C.BLUE)
    step(f, r"\bar x\approx\frac{350}{20}=17.5\text{ minutes}", "an estimate: midpoints stand in for the "
         "real values", size=19, color=C.GREEN)
    ch.check(sp.Rational(sum(sp.Rational(a + b, 2) * n_ for a, b, n_ in grp), 20), sp.Rational(35, 2))
    ch.term("frequency table", "a table listing each value (or class) with how many times it occurs")
    ch.term("midpoint (of a class)", "halfway between a class's boundaries; stands in for its values when "
            "estimating a mean")


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
    rule_box(f, "range, quartiles and IQR (Lecture 4's method)", [
        "Put the data in order. Median position $=\\dfrac{n+1}{2}$.",
        "Quartile position $=\\dfrac{\\text{median position}+1}{2}$. Count that far {B:up from the "
        "smallest} for the lower quartile (LQ) and {B:down from the largest} for the upper quartile (UQ).",
        "Range = largest − smallest.  IQR = UQ − LQ.  Semi-interquartile range = IQR ÷ 2.",
    ], C.BLUE)
    rule_box(f, "fractional positions", [
        "Position 3.5 means {B:halfway} between the 3rd and 4th values: add them and halve.",
        "In general, position $k+d$ (whole part $k$, decimal part $d$) means: start at the $k$th value "
        "and go the fraction $d$ of the gap to the next one: $x_k+d\\,(x_{k+1}-x_k)$.",
        "So position 1.75 is {B:¾ of the way} from the 1st value to the 2nd, and 2.25 is ¼ of the way "
        "from the 2nd to the 3rd. Counting down from the top for the UQ, move the fraction {B:down} "
        "towards the next value.",
        "Calculators and software use slightly different quartile rules, so their answers can differ a "
        "little. Say which method you used.",
    ], C.BLUE)
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
    pg.note(ax.X(27), top + 5, "the box: the middle half", C.ORANGE, 13, solid=False)
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
        "the top and bottom quarters, so it's robust, like the median.", 14, gap=10)
    ex(f, "quartiles with fractional positions: 2, 4, 6, 8, 10, 12, 14, 16 ($n = 8$).")
    d8 = [2, 4, 6, 8, 10, 12, 14, 16]
    step(f, r"\text{median position}=\tfrac{8+1}{2}=4.5,\ \ \text{median}=\tfrac{8+10}{2}=9", "halfway between the 4th "
         "and 5th", size=17)
    step(f, r"\text{quartile position}=\tfrac{4.5+1}{2}=2.75", "", size=17)
    step(f, r"\text{LQ}=4+0.75\times(6-4)=5.5", "¾ of the way from the 2nd value (4) to the 3rd (6)", size=17)
    step(f, r"\text{UQ}=14-0.75\times(14-12)=12.5", "2.75th from the top: ¾ of the way from 14 down "
         "to 12", size=17)
    step(f, r"\text{IQR}=12.5-5.5=7", "", size=19, color=C.GREEN)
    ch.check_num(at_position(d8, 4.5), 9)
    ch.check_num(at_position(d8, 2.75), 5.5)
    ch.check_num(at_position(d8, 2.75, from_top=True), 12.5)
    ch.check_num(at_position(d8, 2.75, from_top=True) - at_position(d8, 2.75), 7)


def deviation(ch):
    f = flow(ch)
    sec(f, "How spread out? A tug of war that always draws", room=440)
    rule_box(f, "deviation", [
        "The deviation of a value is its distance from the mean: $x-\\bar x$ (negative below the mean).",
        "The deviations of any data set {B:always add up to 0}, so their plain average is useless as a "
        "measure of spread.",
    ], C.BLUE)
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
    rule_box(f, "variance and standard deviation", [
        "Variance = the {B:mean of the squared deviations}. Standard deviation = $\\sqrt{\\text{variance}}$, "
        "back in the units of the data.",
        "Whole {B:population} ($N$ values, mean $\\mu$):  $\\sigma^2=\\dfrac{\\sum(x-\\mu)^2}{N}$,  "
        "$\\sigma=\\sqrt{\\sigma^2}$.",
        "{B:Sample} ($n$ values, mean $\\bar x$):  $s^2=\\dfrac{\\sum(x-\\bar x)^2}{n-1}$,  $s=\\sqrt{s^2}$ "
        "(why $n-1$: three sections on).",
    ], C.BLUE)
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
        "10. Bigger groups get bigger sums. {B:Fix: divide by the number of values.} That's the average "
        "square:", 14, gap=6)
    step(f, r"\frac54=1.25\qquad\frac{10}{8}=1.25", "same spread, same answer", size=19)
    ch.check_num(st.pvariance([1, 1, 2, 2, 3, 3, 4, 4]), 1.25)
    f.need(190)
    f.p("This average-square area is the {B:variance}, $\\sigma^2$. Its side length (the square root) "
        "is the {B:standard deviation} $\\sigma$, which is back in the same units as the data. Treating "
        "the values as a whole population, Lecture 4 writes the mean as $\\mu$ and the count as $N$:",
        14, gap=6)
    y_ = f.reserve(110)
    pg = f.pg
    pg.eq(L + 10, y_ + 4, r"\sigma^2=\frac{\sum(x_i-\mu)^2}{N}", 22, C.GREEN)
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


def transform(ch):
    f = flow(ch)
    sec(f, "Shifting and stretching the data", room=480)
    rule_box(f, "adding or multiplying every value", [
        "{B:Add} a constant $c$ to every value: the mean, median, mode and quartiles all go up by $c$. "
        "The spread does {B:not} change: range, IQR, variance and standard deviation stay the same.",
        "{B:Multiply} every value by $k$: the mean, median, mode and quartiles are multiplied by $k$; the "
        "range, IQR and standard deviation by $|k|$; the variance by $k^2$.",
        "Both at once ($y=kx+c$): new mean $=k\\bar x+c$, new standard deviation $=|k|\\times$ old.",
    ], C.BLUE)
    f.p("Sliding every value along by 10 moves the whole data set, but the gaps between the values (and "
        "so the spread) are untouched. Tripling every value triples every gap.", 13.5, gap=8)
    base = [2, 4, 6]
    ex(f, "2, 4, 6 has mean 4 and $\\sigma\\approx1.633$.")
    step(f, r"\text{add 10: }12,14,16\ \Rightarrow\ \text{mean }14,\ \sigma\approx1.633", "mean + 10, "
         "spread unchanged", size=17)
    step(f, r"\text{times 3: }6,12,18\ \Rightarrow\ \text{mean }12,\ \sigma\approx4.899", "both × 3", size=17)
    ch.check_num(st.mean([v + 10 for v in base]), 14)
    ch.check_num(st.pstdev([v + 10 for v in base]), st.pstdev(base), tol=1e-9)
    ch.check_num(st.pstdev(base), 1.633, tol=0.001)
    ch.check_num(st.mean([3 * v for v in base]), 12)
    ch.check_num(st.pstdev([3 * v for v in base]), 3 * st.pstdev(base), tol=1e-9)
    ch.check_num(3 * st.pstdev(base), 4.899, tol=0.001)
    ex(f, "temperatures have mean 20 °C and standard deviation 5 °C. In Fahrenheit, $F=1.8C+32$.")
    step(f, r"\text{mean}=1.8\times20+32=68\,^\circ\text{F}", "multiply and add", size=18)
    step(f, r"\text{SD}=1.8\times5=9\,^\circ\text{F}", "multiply only: the +32 doesn't spread anything",
         size=18, color=C.GREEN)
    temps = [14, 17, 20, 23, 26]
    ch.check_num(st.mean([1.8 * t + 32 for t in temps]), 1.8 * st.mean(temps) + 32, tol=1e-9)
    ch.check_num(st.pstdev([1.8 * t + 32 for t in temps]), 1.8 * st.pstdev(temps), tol=1e-9)
    ch.check_num(1.8 * 20 + 32, 68)
    ch.check_num(1.8 * 5, 9)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Mean", r"\bar x=\frac{\sum x}{n}", "add them up, divide by how many"),
        ("Total from a mean", r"\text{total}=n\times\bar x", "the first step of every missing-value problem"),
        ("Mean of a frequency table", r"\bar x=\frac{\sum fx}{\sum f}", "grouped data: $x$ = class midpoint "
         "(an estimate)"),
        ("Median position", r"\frac{n+1}{2}", "data in order; a .5 position means halfway between two values"),
        ("Quartile position", r"\frac{\text{median position}+1}{2}", "count up from the bottom for LQ, down "
         "from the top for UQ"),
        ("Fractional position", r"k+d\ \to\ x_k+d\,(x_{k+1}-x_k)", "e.g. 1.75 = ¾ of the way from the "
         "1st value to the 2nd"),
        ("Mode", None, "the most common value (or busiest class)"),
        ("Range", r"\text{largest}-\text{smallest}", None),
        ("Interquartile range", r"\text{IQR}=\text{UQ}-\text{LQ}", "semi-interquartile range = IQR ÷ 2"),
        ("Population variance and SD", r"\sigma^2=\frac{\sum(x-\mu)^2}{N},\qquad\sigma=\sqrt{\sigma^2}",
         "the whole population: mean $\\mu$, $N$ values"),
        ("Sample SD", r"s=\sqrt{\frac{\sum(x-\bar x)^2}{n-1}}", "a sample: mean $\\bar x$, divide by "
         "$n-1$ (Bessel)"),
        ("Add c to every value", None, "averages + c; range, IQR, SD, variance unchanged"),
        ("Multiply every value by k", None, "averages × k; range, IQR, SD × |k|; variance × k²"),
        ("Which average?", None, "skewed data or outliers: median. Symmetric data: mean"),
    ], C.BLUE)


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
         "5. 12   6. 6th; (6 + 1)/2 = 3.5th from each end (halfway between the 3rd and 4th)   "
         "7. 8/3 ≈ 2.67, σ ≈ 1.63   8. √(8/2) = 2"),
        ("Think", ["Why is median house price reported, not the mean?",
                   "Two classes both average 60%. What else would you want to know?"],
         "9. a few mansions skew the mean upward   10. the spread (standard deviation / IQR)"),
        ("Find the unknown", ["The mean of 5 numbers is 8. Four of them are 6, 7, 9, 10. Find the fifth.",
                              "The mean of x, 2x and 3x is 12. Find x.",
                              "4 values have mean 15. The value 25 is added. New mean?",
                              "6 values have mean 10. The value 20 is removed. New mean?",
                              "Ten values have mean 7 and σ = 2. New mean and σ if every value is "
                              "(a) increased by 5, (b) tripled?",
                              "x = 1, 2, 3 have frequencies 4, k, 2 and the mean is 1.8. Find k."],
         "11. 8 (total 5 × 8 = 40; 40 − 32 = 8)   12. x = 6 (6x = 3 × 12 = 36)   13. 17 (60 + 25 = 85; "
         "85 ÷ 5)   14. 8 (60 − 20 = 40; 40 ÷ 5)   15. (a) mean 12, σ = 2 (b) mean 21, σ = 6   "
         "16. k = 4 (Σfx = 10 + 2k = 1.8 × (6 + k))"),
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
    ch.check(st.mean([6, 7, 9, 10, 8]), 8)
    kx = sp.symbols("k")
    ch.check(sp.solve(sp.Eq(6 * kx / 3, 12), kx), [6])
    ch.check(sp.Rational(4 * 15 + 25, 5), 17)
    ch.check(sp.Rational(6 * 10 - 20, 5), 8)
    ch.check([7 + 5, 2, 3 * 7, 3 * 2], [12, 2, 21, 6])
    ch.check(sp.solve(sp.Eq((1 * 4 + 2 * kx + 3 * 2) / (4 + kx + 2), sp.Rational(9, 5)), kx), [4])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    mean(ch)
    median_mode(ch)
    totals(ch)
    freq_table(ch)
    pub(ch)
    boxplot(ch)
    deviation(ch)
    squares(ch)
    range_fallacy(ch)
    sample(ch)
    recipe(ch)
    transform(ch)
    summary(ch)
    your_turn(ch)
