"""Chapter 23 - Tables and charts (Lecture 5). The graph detective: every page is a case file. A wall of
numbers turned into a picture, the chart line-up, the HMRC histogram case, stem-and-leaf built leaf
by leaf, the lecturer-in-the-room outlier, ice cream and drownings, crooked graphs next to their
honest twins, the three-pass reading method, and a which-chart flowchart."""
import math

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, title_block

ORDER = 23
NUM = 23
TITLE = "Tables and charts"
SHORT = "Charts"
SLUG = "Charts"
ACCENT = C.TEAL
REQUIRES = ["coordinates", "axes", "plotting", "percentage", "fraction", "units", "rounding", "division",
            "area", "set"]
INTRODUCES = ["data", "categorical-data", "numerical-data", "bar-chart", "histogram", "pie-chart", "dotplot",
              "stem-and-leaf", "scatter-plot", "correlation", "causation", "outlier", "frequency",
              "misleading-graphs", "graph-reading"]

PAPER = "#f7fcfc"


def icon(pg, x0, y0):
    pg.circle(x0 + 7, y0 + 7, 6, C.TEAL, 1.6)
    pg.line(x0 + 11.5, y0 + 11.5, x0 + 17, y0 + 17, C.TEAL, 2.2)


def sec(f, t_, **kw):
    section(f, t_, C.TEAL, icon, **kw)


def stamp(pg, x, y, s, col=C.RED):
    w_ = pg.twidth(s, 11, F.BOLD) + 14
    pg.rect(x, y, w_, 20, col, 1.6, r=3)
    pg.text(x + 7, y + 3, s, 11, col, F.BOLD)
    return w_


def bars(pg, x, y, w_, h_, vals, col, gap=0.25, labels=None, vmax=None, size=9):
    vmax = vmax or max(vals)
    n = len(vals)
    bw = w_ / n
    pg.line(x, y + h_, x + w_, y + h_, C.INK, 1)
    pg.line(x, y, x, y + h_, C.INK, 1)
    for i, v in enumerate(vals):
        hh = h_ * v / vmax
        pg.rect(x + i * bw + bw * gap / 2, y + h_ - hh, bw * (1 - gap), hh, col, 0.8, fillcolor=C.LIGHT[col])
        if labels:
            pg.text(x + i * bw + bw / 2, y + h_ + 3, labels[i], size, C.GREY, align="center", solid=False)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 23, "Tables and charts", "be a graph detective", C.TEAL, PAPER)
    vals = [math.tan(0.1 * k) for k in range(1, 61)]
    for i, v in enumerate(vals[:30]):
        pg.text(L + (i % 6) * 38, 205 + (i // 6) * 15, f"{v:.2f}", 9, C.GREY, F.MONO, solid=False)
    pg.arrow(L + 232, 240, L + 268, 240, C.TEAL, 1.6, head=6)
    ax = Axes(pg, L + 280, 200, 200, 80, (0, 61), (-15, 15))
    ax.hline(0, C.GREY, 0.6, None)
    for k, v in enumerate(vals, 1):
        if abs(v) < 15:
            ax.dot(k, v, C.TEAL, 2)
    pg.note(L + 280, 290, "the same 60 numbers as dots: a repeating pattern of spikes", C.TEAL, 14, w=210)
    f = ch.flow(top=350)
    f.p("A list of four numbers you can hold in your head. Lecture 5 points out that research says "
        "we can only juggle about {B:four to seven things} at once, so a list of sixty numbers is just "
        "noise. Turn the same numbers into dots (above) and your eyes spot the pattern instantly.",
        14, gap=10)
    f.p("This chapter is about {B:drawing data honestly} and {B:reading other people's graphs "
        "suspiciously}. Each page is a {B:case file}: a question, the evidence, and the verdict.",
        14, gap=10)
    f.p("{y:Goes with} {B:Lecture 5} {y:(graphical analysis: basic charts, outliers, bad and good graphs, "
        "form / message / criticism).}", 12.5)


def kinds(ch):
    f = flow(ch)
    sec(f, "Two kinds of data")
    f.p("{B:Data} just means the facts you've recorded. Before drawing anything, ask one question: "
        "{B:is each fact a word or a number?}", 14, gap=10)
    y_ = f.reserve(120)
    pg = f.pg
    pg.rect(L, y_, W / 2 - 8, 110, C.ORANGE, 1.3, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.text(L + 12, y_ + 8, "Categorical (words / labels)", 13, C.ORANGE, F.BOLD)
    pg.note(L + 12, y_ + 30, "favourite drink: tea, coffee, juice\nbus route: 7, 36, 58 (numbers used "
            "as names!)\neye colour, course, month", C.INK, 15, w=W / 2 - 30)
    pg.rect(L + W / 2 + 8, y_, W / 2 - 8, 110, C.BLUE, 1.3, fillcolor=C.LIGHT[C.BLUE], r=8)
    pg.text(L + W / 2 + 20, y_ + 8, "Numerical (measured / counted)", 13, C.BLUE, F.BOLD)
    pg.note(L + W / 2 + 20, y_ + 30, "height 1.74 m, age 19, wage £16,400\nyou can sensibly add or "
            "average them\n(the average bus route is nonsense)", C.INK, 15, w=W / 2 - 30)
    ch.term("data", "recorded facts: measurements, counts or labels")
    ch.term("categorical data", "data that are labels or groups (tea / coffee), not quantities")
    ch.term("numerical data", "data that are measured or counted quantities (heights, ages)")
    ch.term("frequency", "how many times a value (or group of values) occurs")
    f.p("A {B:frequency} is a count: \"how many times did this happen?\". Most charts draw frequencies. "
        "Lecture 5 asks the difference between a {B:chart} and a {B:graph}: loosely, a {B:graph} plots "
        "numbers against numbers on two axes, while {B:chart} is the wider word (bar charts, pie "
        "charts, tables...). People use the words loosely, so don't lose sleep over it.", 14)


def lineup(ch):
    f = flow(ch)
    sec(f, "The line-up: six basic charts", room=560)
    f.p("The same small data set drawn six ways (the lecture's Minitab examples). Each chart is "
        "good at {B:one} job.", 14, gap=10)
    cats = ["tea", "coffee", "juice", "water"]
    cnt = [4, 7, 2, 5]
    ages = [18, 18, 19, 19, 19, 20, 20, 21, 22, 23, 25, 31]
    cells = [
        ("Bar chart", "categories; gaps between bars because tea and coffee are separate things"),
        ("Pie chart", "parts of one whole; slice angle = share of 360°"),
        ("Histogram", "numbers in ranges; bars touch because the ranges join up"),
        ("Dotplot", "one dot per value; small data sets, see clusters"),
        ("Stem and leaf", "like a dotplot made of the digits themselves"),
        ("Scatter plot", "two measurements per person: does one go with the other?"),
    ]
    cw, chh = W / 2, 150
    for r_ in range(3):
        y_ = f.reserve(chh)
        pg = f.pg
        for c_ in range(2):
            idx = r_ * 2 + c_
            x0 = L + c_ * cw
            name, use = cells[idx]
            pg.text(x0, y_, name, 13, C.TEAL, F.BOLD)
            pg.note(x0 + 110, y_ + 8, use, C.GREY, 13, w=cw - 118)
            gx, gy, gw, gh = x0 + 6, y_ + 30, 100, 90
            if idx == 0:
                bars(pg, gx, gy, gw, gh, cnt, C.TEAL, labels=cats, vmax=8, size=7)
            elif idx == 1:
                tot, a0 = sum(cnt), 90
                cols = [C.TEAL, C.ORANGE, C.PURPLE, C.BLUE]
                for v, col, nm in zip(cnt, cols, cats):
                    a1 = a0 + 360 * v / tot
                    pg.sector(gx + 45, gy + 45, 42, a0, a1, C.LIGHT[col], outline=col)
                    mid = math.radians((a0 + a1) / 2)
                    pg.text(gx + 45 + 26 * math.cos(mid), gy + 40 - 26 * math.sin(mid), nm, 7, C.INK,
                            align="center", solid=False)
                    a0 = a1
            elif idx == 2:
                hist = [5, 4, 1, 1, 0, 1]
                bars(pg, gx, gy, gw, gh, hist, C.TEAL, gap=0, vmax=6)
                for i, lab in enumerate(["18", "20", "22", "24", "26", "28", "30+"][:7]):
                    pg.text(gx + i * gw / 6, gy + gh + 3, lab, 7, C.GREY, align="center", solid=False)
            elif idx == 3:
                pg.line(gx, gy + gh - 10, gx + gw, gy + gh - 10, C.INK, 1)
                seen = {}
                for a in ages:
                    seen[a] = seen.get(a, 0) + 1
                    pg.dot(gx + (a - 17) * gw / 15, gy + gh - 16 - (seen[a] - 1) * 8, 3, C.TEAL)
                for a in (18, 22, 26, 30):
                    pg.text(gx + (a - 17) * gw / 15, gy + gh - 6, str(a), 7, C.GREY, align="center", solid=False)
            elif idx == 4:
                rows = [("1", "8 8 9 9 9"), ("2", "0 0 1 2 3 5"), ("3", "1")]
                for k, (s, lf) in enumerate(rows):
                    pg.text(gx + 8, gy + 8 + k * 20, s, 12, C.INK, F.MONO)
                    pg.line(gx + 24, gy + 6 + k * 20, gx + 24, gy + 24 + k * 20, C.INK, 1)
                    pg.text(gx + 30, gy + 8 + k * 20, lf, 12, C.TEAL, F.MONO)
                pg.text(gx + 8, gy + 72, "key: 2 | 5 means 25", 8, C.GREY)
            else:
                ax = Axes(pg, gx + 8, gy, gw - 8, gh - 10, (150, 195), (40, 95))
                ax.axes(None, None, 0, 0)
                for h_, w_ in [(155, 50), (160, 55), (163, 60), (168, 62), (170, 66), (172, 70), (175, 68),
                               (178, 75), (181, 80), (185, 83), (188, 86), (166, 58)]:
                    ax.dot(h_, w_, C.TEAL, 2.4)
                pg.text(gx + gw - 30, gy + gh - 8, "height", 7, C.GREY, solid=False)
                pg.text(gx - 4, gy - 10, "weight", 7, C.GREY, solid=False)
    ch.term("bar chart", "separate bars (with gaps) whose heights show the frequency of each category")
    ch.term("pie chart", "a circle cut into slices; each slice's angle is its share of 360°")
    ch.term("histogram", "touching bars for numerical data grouped into ranges; area shows frequency")
    ch.term("dotplot", "a number line with one dot stacked up for every data value")
    ch.term("scatter plot", "one dot per item, placed by two measurements (x, y), to see whether they are related")
    ch.check(sum(cnt), 18)
    ch.check_num(360 * 7 / 18, 140)
    f.p("{b:Pie angle:} coffee is 7 of 18 drinks, so its slice is $\\frac{7}{18}\\times360^\\circ = "
        "140^\\circ$.", 13.5)


def hmrc(ch):
    f = flow(ch)
    sec(f, "Case 1: the HMRC wage brackets", room=560)
    f.p("Lecture 4 shows how many UK taxpayers earn in each wage bracket and asks: {R:\"Something is "
        "wrong with my choice of graph here. What is it?\"} Here are the middle brackets:", 14, gap=10)
    br = [("15-20k", 5, 4.95), ("20-30k", 10, 6.00), ("30-50k", 20, 4.09), ("50-70k", 20, 0.859)]
    y_ = f.reserve(170)
    pg = f.pg
    stamp(pg, L, y_, "SUSPECT: equal-width bars")
    x0, gy, gh = L + 10, y_ + 36, 110
    bars(pg, x0, gy, 180, gh, [b[2] for b in br], C.RED, gap=0.15, labels=[b[0] for b in br], vmax=6.5)
    pg.note(x0 + 190, gy + 10, "20-30k looks like\nthe winner (6.00 m\npeople)", C.RED, 14)
    stamp(pg, L + 265, y_, "HONEST: width = bracket size", C.GREEN)
    x1, scale = L + 275, 3.3
    pg.line(x1, gy + gh, x1 + 55 * scale, gy + gh, C.INK, 1)
    pg.line(x1, gy, x1, gy + gh, C.INK, 1)
    xx = x1
    dens = []
    for lab, wid, cnt in br:
        d = cnt / wid
        dens.append(d)
        hh = gh * d / 1.0
        pg.rect(xx, gy + gh - hh, wid * scale, hh, C.GREEN, 0.8, fillcolor=C.LIGHT[C.GREEN])
        pg.text(xx + wid * scale / 2, gy + gh + 3, lab, 7, C.GREY, align="center", solid=False)
        xx += wid * scale
    ch.check_num(dens[0], 0.99)
    ch.check_num(dens[1], 0.60)
    f.p("The brackets are {B:different widths}: £15k to £20k is only £5000 wide, but £30k to £50k is "
        "£20,000 wide. A wide bracket collects more people just by being wide. The fix (a proper "
        "{B:histogram}) makes the bar {B:width} the bracket width and the {B:area} the number of "
        "people, so the height becomes {B:people per £1000}:", 14, gap=6)
    y_ = f.reserve(110)
    pg = f.pg
    pg.eq(L + 20, y_ + 4, r"\frac{4.95\text{ million}}{5}=0.99", 18)
    pg.note(L + 220, y_ + 16, "million per £1000, for £15-20k: the real crowd", C.GREEN, 15)
    pg.eq(L + 20, y_ + 56, r"\frac{6.00\text{ million}}{10}=0.60", 18)
    pg.note(L + 220, y_ + 68, "million per £1000, for £20-30k: thinner!", C.GREEN, 15)
    f.p("{G:Verdict:} the busiest {B:£1000-slice} is around £15k-£20k, not £20k-£30k. This is why "
        "the lecture's mode lands at about £15,000 and the median at £16,400 (Chapter 24).", 14)


def stemleaf(ch):
    f = flow(ch)
    sec(f, "Stem and leaf, one leaf at a time", room=520)
    f.p("Lecture 4's data set, 17 values already in order:", 14, gap=6)
    data = [1, 2, 3, 5, 5, 6, 8, 18, 25, 34, 47, 56, 60, 69, 71, 88, 94]
    f.text("  ".join(str(d) for d in data), 13, C.INK, F.MONO, gap=10)
    f.p("{B:Split every number into a stem (the tens digit) and a leaf (the units digit).} "
        "34 splits into stem 3, leaf 4. Single figures like 5 have stem 0.", 14, gap=10)
    y_ = f.reserve(40)
    pg = f.pg
    for i, (n_, s_, l_) in enumerate([(34, "3", "4"), (5, "0", "5"), (94, "9", "4")]):
        xx = L + 20 + i * 160
        pg.text(xx, y_ + 4, str(n_), 18, C.INK, F.MONO)
        pg.arrow(xx + 34, y_ + 14, xx + 60, y_ + 14, C.GREY, 1.1, head=4)
        pg.text(xx + 66, y_ + 4, s_, 18, C.TEAL, F.MONO)
        pg.line(xx + 84, y_ + 2, xx + 84, y_ + 26, C.INK, 1.2)
        pg.text(xx + 90, y_ + 4, l_, 18, C.ORANGE, F.MONO)
    rows = {}
    for d in data:
        rows.setdefault(d // 10, []).append(d % 10)
    y_ = f.reserve(10 * 20 + 20)
    pg = f.pg
    for s_ in range(10):
        yy = y_ + s_ * 20
        pg.text(L + 40, yy, str(s_), 14, C.TEAL, F.MONO)
        pg.line(L + 58, yy - 2, L + 58, yy + 18, C.INK, 1.2)
        leaves = rows.get(s_, [])
        pg.text(L + 66, yy, " ".join(str(v) for v in leaves), 14, C.ORANGE, F.MONO)
        for j in range(len(leaves)):
            pg.rect(L + 260 + j * 16, yy + 2, 14, 14, C.TEAL, 0.6, fillcolor=C.LIGHT[C.TEAL])
    pg.text(L + 40, y_ + 204, "key: 2 | 5 means 25", 11, C.GREY)
    pg.note(L + 380, y_ + 10, "tip it on its side\nand it's a bar chart\nof the tens:", C.TEAL, 15)
    pg.arrow(L + 376, y_ + 30, L + 376 - 240 + 130, y_ + 10, C.TEAL, 1.1, head=5, bend=0.2)
    pg.note(L + 380, y_ + 90, "7 values under 10,\nthen a long thin\ntail up to 94", C.GREY, 15)
    ch.check(len(rows[0]), 7)
    ch.term("stem and leaf diagram", "each value split into stem (leading digit) and leaf (last digit); leaves listed beside their stem")
    f.p("You keep {B:every original number} (unlike a bar chart) and see the {B:shape} at a glance. "
        "Always give a {B:key}, or nobody knows if 2 | 5 is 25 or 2.5.", 14)


def outliers(ch):
    f = flow(ch)
    sec(f, "Case 2: the lecturer in the room", room=420)
    f.p("Lecture 5: \"Consider the distribution of ages in this room.\" Twelve students and one "
        "lecturer:", 14, gap=10)
    ages = [18, 18, 19, 19, 19, 19, 20, 20, 20, 21, 22, 23, 52]
    y_ = f.reserve(90)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 5, 440, 60, (15, 55), (0, 5))
    pg.line(ax.X(15), ax.Y(0), ax.X(55), ax.Y(0), C.INK, 1)
    seen = {}
    for a in ages:
        seen[a] = seen.get(a, 0) + 1
        ax.dot(a, seen[a] - 0.4, C.RED if a == 52 else C.TEAL, 4)
    for a in range(15, 56, 5):
        pg.text(ax.X(a), ax.Y(0) + 4, str(a), 9, C.GREY, align="center", solid=False)
    pg.ring(ax.X(52) - 10, ax.Y(0.6) - 10, 20, 20, C.RED)
    pg.note(ax.X(40), ax.Y(3.5), "the outlier", C.RED, 16)
    mean_all = sum(ages) / len(ages)
    mean_st = sum(ages[:-1]) / 12
    ch.check_num(mean_all, 22.31, tol=0.01)
    ch.check_num(mean_st, 19.83, tol=0.01)
    ch.term("outlier", "a value far away from the rest of the data")
    f.p("An {B:outlier} is a value far from the rest. It drags the average: the mean age is "
        "{B:22.3} with the lecturer and {B:19.8} without. But the lecturer is {B:real}: they really are "
        "in the room!", 14, gap=8)
    f.p("{R:The rule (Lecture 5):} remove a point only if you think something is {B:wrong} with it (a "
        "typo like age 190, a broken sensor), and {B:always say that you removed it and why}. "
        "\"Unusual\" is not the same as \"wrong\".", 14)


def causation(ch):
    f = flow(ch)
    sec(f, "Case 3: does ice cream cause drowning?", room=440)
    f.p("A town records ice cream sales and swimming accidents each month. The scatter plot shows a "
        "clear pattern: more ice cream, more accidents. Lock up the ice cream van?", 14, gap=10)
    y_ = f.reserve(160)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 200, 120, (0, 12), (0, 10))
    ax.axes(None, None, 0, 0)
    pts = [(1, 1.2), (2, 1.8), (3, 2.5), (4, 3.1), (5, 4.5), (6, 4.2), (7, 5.8), (8, 6.5), (9, 7.2), (10, 8.4),
           (11, 8.9), (3.5, 2.0)]
    for x, yv in pts:
        ax.dot(x, yv, C.TEAL, 3)
    ax.seg(0.5, 0.6, 11.5, 9.3, C.GREY, 1, dash=(4, 3))
    pg.text(L + 150, y_ + 138, "ice cream sales", 10, C.GREY)
    pg.text(L + 34, y_ - 6, "accidents", 10, C.GREY)
    cx = L + 350
    pg.circle(cx, y_ + 30, 18, C.ORANGE, 1.6, fillcolor=C.LIGHT[C.ORANGE])
    for k in range(8):
        a = k * math.pi / 4
        pg.line(cx + 22 * math.cos(a), y_ + 30 + 22 * math.sin(a), cx + 28 * math.cos(a),
                y_ + 30 + 28 * math.sin(a), C.ORANGE, 1.4)
    pg.text(cx, y_ + 62, "hot weather", 12, C.ORANGE, F.BOLD, align="center")
    pg.text(cx - 80, y_ + 118, "ice cream", 12, C.INK, F.BOLD, align="center")
    pg.text(cx + 80, y_ + 118, "swimming", 12, C.INK, F.BOLD, align="center")
    pg.arrow(cx - 14, y_ + 78, cx - 70, y_ + 110, C.ORANGE, 1.5, head=6)
    pg.arrow(cx + 14, y_ + 78, cx + 70, y_ + 110, C.ORANGE, 1.5, head=6)
    pg.line(cx - 40, y_ + 126, cx + 40, y_ + 126, C.RED, 1.2, dash=(3, 3))
    pg.xmark(cx, y_ + 126, 9)
    pg.note(cx - 40, y_ + 134, "no arrow here", C.RED, 14)
    ch.term("correlation", "two measurements tend to rise (or fall) together; seen as a sloping cloud on a scatter plot")
    ch.term("causation", "one thing actually makes the other happen")
    f.p("The two {B:go together} ({B:correlation}), but neither {B:makes} the other happen "
        "({B:causation}). A hidden third thing, hot weather, pushes both up. Lecture 5: "
        "{R:correlation does not equal causation!}", 14, gap=8)
    f.p("{b:Direction trap:} even when there is a real cause, which way does it go? Towns with more "
        "police have more crime. Do police cause crime, or does crime bring police?", 14, gap=8)
    f.p("{b:Joining the dots:} only connect the points with a line when there's a reason, like "
        "measurements taken one after another in {B:time}. Here, a line through the months in "
        "sales order would be meaningless; a dashed {B:trend line} is fine.", 14)


def crooked(ch):
    f = flow(ch)
    sec(f, "Case 4: crooked graphs and their honest twins", room=600)
    f.p("Lecture 5: bad graphs hide or twist information: missing titles or labels, poor use of "
        "colour, and a {B:poor choice of scale}. Each crime on the left, the fix on the right.", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    stamp(pg, L, y_, "CRIME: axis starts at 49")
    ax = Axes(pg, L + 20, y_ + 34, 170, 90, (0, 2), (49, 52.5))
    pg.line(ax.X(0), ax.Y(49), ax.X(2), ax.Y(49), C.INK, 1)
    pg.line(ax.X(0), ax.Y(49), ax.X(0), ax.Y(52.5), C.INK, 1)
    for i, v, col in [(0, 50, C.BLUE), (1, 52, C.RED)]:
        pg.rect(ax.X(i + 0.2), ax.Y(v), ax.X(0.6) - ax.X(0), ax.Y(49) - ax.Y(v), col, 0.8,
                fillcolor=C.LIGHT[col])
    for v in (49, 50, 51, 52):
        pg.text(ax.X(0) - 16, ax.Y(v) - 6, str(v), 8, C.GREY, solid=False)
    pg.note(L + 190, y_ + 50, "B looks\n3× bigger", C.RED, 15)
    stamp(pg, L + 265, y_, "HONEST: axis from 0", C.GREEN)
    ax = Axes(pg, L + 285, y_ + 34, 170, 90, (0, 2), (0, 55))
    pg.line(ax.X(0), ax.Y(0), ax.X(2), ax.Y(0), C.INK, 1)
    pg.line(ax.X(0), ax.Y(0), ax.X(0), ax.Y(55), C.INK, 1)
    for i, v, col in [(0, 50, C.BLUE), (1, 52, C.RED)]:
        pg.rect(ax.X(i + 0.2), ax.Y(v), ax.X(0.6) - ax.X(0), ax.Y(0) - ax.Y(v), col, 0.8,
                fillcolor=C.LIGHT[col])
    pg.note(L + 460, y_ + 50, "4%\nmore", C.GREEN, 15)
    ch.check_num((52 - 50) / 50 * 100, 4)
    y_ = f.reserve(150)
    pg = f.pg
    stamp(pg, L, y_, "CRIME: picture grows both ways")
    for k, s_ in [(0, 30), (1, 60)]:
        xx = L + 20 + k * 60
        pg.rect(xx, y_ + 120 - s_, s_ * 0.8, s_, C.ORANGE, 1.2, fillcolor=C.LIGHT[C.ORANGE], r=3)
        pg.text(xx + 2, y_ + 124, ["2020", "2025"][k], 9, C.GREY, solid=False)
    pg.note(L + 150, y_ + 40, "sales doubled, so\nthe bag is twice as tall\n... and twice as wide:\n4× the "
            "ink!", C.RED, 14)
    stamp(pg, L + 265, y_, "HONEST: plain bars", C.GREEN)
    bars(pg, L + 285, y_ + 34, 120, 86, [1, 2], C.GREEN, gap=0.4, labels=["2020", "2025"], vmax=2.2)
    pg.note(L + 415, y_ + 50, "twice as\ntall only", C.GREEN, 15)
    ch.term("misleading graph", "a graph whose scale, shape or missing labels give a false impression")
    f.p("{b:The checklist of crimes:} no title, no axis labels or units, no source, a y-axis that "
        "doesn't start at 0 (for bars), uneven scales, 3D effects, pictures that grow in area, and "
        "\"infographics\" (Lecture 5: {h:very modern, very useful, very easy to lie with!}).", 14)


def reading(ch):
    f = flow(ch)
    sec(f, "Reading any graph in three passes", room=520)
    f.p("Lecture 5's method: {B:start with how it's built, move on to what it says, finish by being "
        "critical.} Try it on this graph:", 14, gap=10)
    y_ = f.reserve(230)
    pg = f.pg
    ax = Axes(pg, L + 40, y_ + 20, 240, 120, (0, 24), (60, 90))
    ax.grid(4, 10)
    ax.axes(None, None, 4, 10, size=8)
    hum = [86, 85, 82, 76, 73, 70, 70, 72, 76, 78, 80, 81, 81, 82, 83, 83, 84, 84, 84, 84, 86]
    ax.polyline([(i * 1.2, h_) for i, h_ in enumerate(hum)], C.TEAL, 2)
    pg.text(L + 40, y_, "Humidity (%) through the day", 11, C.INK, F.BOLD)
    pg.text(L + 190, y_ + 160, "hours after 9 am", 9, C.GREY)
    tags = [("1  FORM", C.BLUE, "Title? Yes. Axes? % and hours, but\nwhere is the source? Why start at 60?"),
            ("2  MESSAGE", C.GREEN, "Driest around 3-4 pm (70%), damp\nagain overnight. Implication: sun\n"
             "warms the air and dries it."),
            ("3  CRITICISM", C.RED, "One day only, one place. Missing\nsource. Axis from 60 exaggerates the\ndip.")]
    for k, (t_, col, s_) in enumerate(tags):
        yy = y_ + k * 76
        pg.text(L + 300, yy, t_, 12, col, F.BOLD)
        pg.note(L + 300, yy + 16, s_, C.INK, 13, w=200)
    ch.check(min(hum), 70)
    ch.term("form / message / criticism", "Lecture 5's three passes for reading a graph: how it's built, what it says, what's wrong or missing")
    f.p("{B:Form:} title and footnotes, axis labels and scale, data source, colours and symbols. "
        "{B:Message:} meaning and implications. {B:Criticism:} missing data and ease of "
        "understanding. (The data are the weather table from the lecture slides.)", 14)


def which(ch):
    f = flow(ch)
    sec(f, "Which chart? A flowchart", room=380)
    y_ = f.reserve(300)
    pg = f.pg

    def box(x, y, s, col, w_=150, sub=None, h_=34):
        pg.rect(x - w_ / 2, y, w_, h_, col, 1.3, fillcolor=C.LIGHT[col], r=8)
        pg.text(x - w_ / 2 + 4, y + (5 if sub else 9), s, 11, C.INK, F.BOLD, align="center", w=w_ - 8)
        if sub:
            pg.text(x - w_ / 2 + 4, y + 21, sub, 9, C.GREY, align="center", w=w_ - 8)

    cx = L + W / 2
    box(cx, y_, "What is each fact?", C.TEAL, 170)
    box(L + 110, y_ + 70, "a word / label", C.ORANGE)
    box(L + 380, y_ + 70, "a number", C.BLUE)
    pg.arrow(cx - 40, y_ + 34, L + 130, y_ + 70, C.GREY, 1.2, head=5)
    pg.arrow(cx + 40, y_ + 34, L + 360, y_ + 70, C.GREY, 1.2, head=5)
    box(L + 50, y_ + 150, "pie chart", C.ORANGE, 95)
    box(L + 165, y_ + 150, "bar chart", C.ORANGE, 95)
    pg.arrow(L + 95, y_ + 104, L + 55, y_ + 150, C.GREY, 1.1, head=5)
    pg.arrow(L + 125, y_ + 104, L + 160, y_ + 150, C.GREY, 1.1, head=5)
    pg.note(L + 2, y_ + 188, "parts of one\nwhole (≤ 6 slices)", C.GREY, 13)
    pg.note(L + 125, y_ + 188, "comparing\ngroups", C.GREY, 13)
    sx = L + 318
    opts = [("dotplot / stem and leaf", "one measurement, small data"),
            ("histogram", "one measurement, lots of data"),
            ("scatter plot", "two measurements per item"),
            ("line graph", "one measurement over time")]
    pg.line(sx, y_ + 104, sx, y_ + 128 + 3 * 46 + 20, C.GREY, 1.1)
    for k, (s_, why) in enumerate(opts):
        yy = y_ + 128 + k * 46
        pg.arrow(sx, yy + 20, sx + 20, yy + 20, C.GREY, 1.1, head=4)
        box(sx + 20 + 80, yy, s_, C.BLUE, 160, sub=why, h_=40)
    f.gap(10)
    f.p("{b:And when is a table better than any chart?} When the reader needs {B:exact values} to look "
        "up, not a shape. Lecture 5's weather forecast is a table because you want to know the "
        "temperature at 3 pm, not admire a curve:", 14, gap=10)
    cols = ["time", "9:00", "12:00", "15:00", "18:00", "21:00", "0:00", "3:00"]
    rows = [("temp °C", ["10", "12", "12", "11", "10", "10", "9"]),
            ("wind", ["N", "NNE", "NNE", "NNE", "NNE", "N", "N"]),
            ("humidity", ["86%", "76%", "70%", "78%", "81%", "83%", "84%"])]
    y_ = f.reserve(24 * 4 + 10)
    pg = f.pg
    cw = W / len(cols)
    for j, c_ in enumerate(cols):
        pg.rect(L + j * cw, y_, cw, 22, C.TEAL, 0.6, fillcolor=C.LIGHT[C.TEAL])
        pg.text(L + j * cw + 4, y_ + 5, c_, 10, C.INK, F.BOLD, align="center", w=cw - 8)
    for i, (nm, vals) in enumerate(rows):
        yy = y_ + 24 * (i + 1)
        pg.text(L + 4, yy + 5, nm, 10, C.TEAL, F.BOLD)
        for j, v in enumerate(vals):
            pg.text(L + (j + 1) * cw + 4, yy + 5, v, 10, C.INK, align="center", w=cw - 8)
        pg.line(L, yy + 22, L + W, yy + 22, C.GREY, 0.4)
    f.p("{h:Rule of thumb:} tables for {B:looking up}, charts for {B:seeing patterns}. A table needs the "
        "same honesty as a graph: a title, units in the headings, and a source.", 14, C.INK)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Case files for you", fresh=True)
    f.p("Answers in grey.", 13.5, gap=10)
    groups = [
        ("Which chart?", ["Share of the budget spent on rent, food, travel, fun",
                          "Reaction times of 200 people",
                          "Hours of revision vs exam mark for 30 students",
                          "Temperature at noon every day in March"],
         "1. pie   2. histogram   3. scatter plot   4. line graph"),
        ("Build it", ["Draw a stem and leaf for 12, 15, 21, 22, 22, 27, 30, 34, 41 (with a key)",
                      "A pie chart shows 90 people. How many degrees for 25 of them?"],
         "5. 1 | 2 5;  2 | 1 2 2 7;  3 | 0 4;  4 | 1;  key 2 | 1 means 21   6. 25/90 × 360 = 100°"),
        ("Detective", ["\"Students who sit at the front get better marks, so sitting at the front "
                       "makes you clever.\" What's wrong?",
                       "A bar chart's y-axis runs from 95 to 100. Two bars read 96 and 99. "
                       "What false impression, and the fix?",
                       "Data: 4, 5, 5, 6, 7, 480. Should you delete 480?"],
         "7. correlation ≠ causation (keen students choose the front)   8. 99 looks 4× bigger than 96; "
         "start at 0   9. only if it's an error; check it, and say so if you remove it"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.TEAL, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check_num(25 / 90 * 360, 100)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    kinds(ch)
    lineup(ch)
    hmrc(ch)
    stemleaf(ch)
    outliers(ch)
    causation(ch)
    crooked(ch)
    reading(ch)
    which(ch)
    your_turn(ch)
