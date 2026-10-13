"""Chapter 26 - The Normal distribution (Lecture 9). Where the bell comes from (add dice together and
the flat histogram grows a hump; a Galton board of bouncing balls), the anatomy of the bell, area as
probability, z-scores as rulers marked in sigmas, the lecture's IQ range and aeroplane-seat problems,
the real 100 measurements from the slides, and a reminder to stay critical."""
import math
import statistics as st

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 26
NUM = 26
TITLE = "The Normal distribution"
SHORT = "Normal distribution"
SLUG = "Normal"
ACCENT = C.ORANGE
REQUIRES = ["probability", "mean", "standard-deviation", "variance", "histogram", "frequency", "skew",
            "e-number", "exponential-function", "transpose", "percentage", "area", "median", "mode",
            "population-sample", "graph-of-function"]
INTRODUCES = ["distribution", "uniform-distribution", "normal-distribution", "bell-curve", "probability-density",
              "z-score", "standard-normal", "normal-table", "kurtosis"]

PAPER = "#fffcf7"
SEATS = [33.5, 37.0, 50.5, 39.4, 46.8, 49.8, 36.4, 45.8, 40.2, 45.1, 37.9, 31.6, 45.5, 44.8, 36.8, 35.8, 38.7,
         43.3, 49.2, 36.6, 44.2, 43.1, 40.2, 44.5, 35.0, 50.6, 46.2, 55.2, 52.1, 42.2, 41.9, 42.8, 52.6, 40.0,
         32.4, 38.1, 49.0, 36.8, 43.9, 51.5, 51.0, 37.1, 33.2, 44.5, 46.3, 36.0, 46.3, 46.5, 36.8, 40.3, 43.7,
         39.5, 48.1, 43.3, 35.9, 46.4, 40.2, 49.1, 37.0, 35.7, 45.5, 44.2, 42.0, 50.1, 41.8, 37.7, 43.4, 45.6,
         48.5, 41.6, 43.7, 39.5, 32.9, 41.6, 43.5, 46.2, 32.5, 34.7, 38.3, 36.0, 32.4, 37.4, 43.3, 40.2, 37.2,
         40.4, 46.4, 40.4, 50.2, 45.2, 48.8, 45.6, 38.5, 31.7, 35.0, 47.1, 42.1, 41.7, 43.4, 40.6]


def Phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def pdf(z):
    return math.exp(-z * z / 2) / math.sqrt(2 * math.pi)


def icon(pg, x0, y0):
    pg.poly([(x0 + 1 + i * 0.8, y0 + 17 - 15 * math.exp(-((i - 10) / 4.5) ** 2)) for i in range(21)], C.ORANGE, 1.6)


def sec(f, t_, **kw):
    section(f, t_, C.ORANGE, icon, **kw)


def dice_sum(n):
    dist = {0: 1}
    for _ in range(n):
        nd = {}
        for s, c in dist.items():
            for k in range(1, 7):
                nd[s + k] = nd.get(s + k, 0) + c
        dist = nd
    return dist


def hist(pg, x, y, w_, h_, dist, col, title):
    ks = sorted(dist)
    vmax = max(dist.values())
    bw = w_ / len(ks)
    for i, k in enumerate(ks):
        hh = h_ * dist[k] / vmax
        pg.rect(x + i * bw, y + h_ - hh, bw, hh, col, 0.4, fillcolor=C.LIGHT[col])
    pg.line(x, y + h_, x + w_, y + h_, C.INK, 1)
    pg.text(x + w_ / 2, y + h_ + 4, title, 10, C.INK, F.BOLD, align="center")


def galton(pg, x, y, rows, sp_, balls=True):
    for r_ in range(rows):
        for k in range(r_ + 1):
            pg.dot(x + (k - r_ / 2) * sp_, y + r_ * sp_ * 0.9, 2, C.GREY)
    base = y + rows * sp_ * 0.9 + 4
    for k in range(rows + 2):
        xx = x + (k - (rows + 1) / 2) * sp_
        pg.line(xx, base, xx, base + 70, C.GREY, 0.8)
    if balls:
        for k in range(rows + 1):
            n = math.comb(rows, k)
            hh = 66 * n / math.comb(rows, rows // 2)
            xx = x + (k - rows / 2) * sp_
            nb = max(1, int(hh / 5.5))
            for j in range(nb):
                pg.circle(xx, base + 70 - 3 - j * 5.5, 2.5, C.ORANGE, 0.6, fillcolor=C.LIGHT[C.ORANGE])
    pg.line(x - (rows + 1) / 2 * sp_, base + 70, x + (rows + 1) / 2 * sp_, base + 70, C.INK, 1)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 26, "The Normal distribution", "why so many things pile up into a bell", C.ORANGE,
                     PAPER)
    galton(pg, L + 110, 205, 9, 13)
    pg.circle(L + 110, 192, 3, C.ORANGE, 0.8, fillcolor=C.ORANGE)
    ax = Axes(pg, L + 270, 205, 210, 110, (-3.5, 3.5), (0, 0.42))
    ax.fill_under(pdf, -3.5, 3.5, C.LIGHT[C.ORANGE])
    ax.curve(pdf, -3.5, 3.5, C.ORANGE, 2)
    pg.line(ax.X(-3.5), ax.Y(0), ax.X(3.5), ax.Y(0), C.INK, 1)
    pg.note(L + 290, 325, "the shape the balls are aiming for", C.ORANGE, 14)
    f = ch.flow(top=400)
    f.p("Drop balls into a board of pegs. At each peg a ball bounces left or right at random, yet the "
        "pile at the bottom always makes the same shape: a {B:bell}, high in the middle and fading "
        "at the edges. Heights, test scores and measurement errors make the same bell.", 14, gap=10)
    f.p("This chapter shows {B:why} the bell appears, how to read it (it's all about {B:area}), and "
        "how the {B:standard deviation} of Chapter 24 becomes a ruler for answering \"what fraction of "
        "people...?\" questions. You will never need to integrate the scary formula by hand.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 9} {y:(uniform vs Normal, sums of distributions, the bell curve equation, "
        "IQ, skewness and kurtosis, probability density, the seat-width problem).}", 12.5)


def flat_to_bell(ch):
    f = flow(ch)
    sec(f, "From flat to bell: add things together")
    f.p("Roll one die many times and every face turns up about equally: a {B:flat} histogram. Lecture 9 "
        "calls this {B:uniformly random} (coins, dice, roulette and lottery balls are all flat). A "
        "{B:distribution} is just the pattern of how often each value turns up.", 14, gap=10)
    ch.term("distribution", "the pattern of how often each possible value occurs")
    ch.term("uniform distribution", "every value equally likely: a flat histogram")
    y_ = f.reserve(120)
    pg = f.pg
    for k, n in enumerate([1, 2, 3, 5]):
        hist(pg, L + k * 124, y_ + 4, 108, 80, dice_sum(n), C.ORANGE, f"total of {n} di{'e' if n == 1 else 'ce'}")
    d2 = dice_sum(2)
    ch.check(d2[7], 6)
    ch.check(sum(dice_sum(3).values()), 216)
    f.p("Now add two dice. A total of 7 can happen 6 ways but 2 only one way (the diagonals of "
        "Chapter 25's grid), so the histogram becomes a {B:triangle}. Three dice: a hump. Five: already a "
        "bell. Lecture 9 does the same with coins: one coin is flat; the number of heads in 100 coins is "
        "a beautiful bell (mean 50, standard deviation 5).", 14, gap=8)
    ch.check_num(math.sqrt(100 * 0.25), 5)
    f.p("{B:That's the secret:} whenever a quantity is the {B:sum (or average) of many small random "
        "bits}, it comes out bell-shaped, whatever the bits looked like. Lecture 9: {h:\"Any sum (or "
        "average) of multiple identically distributed distributions\"} is Normal. Your height is the "
        "sum of thousands of small genetic and dietary nudges; that's why it's (roughly) Normal.", 14, gap=10)
    f.need(190)
    f.p("{R:But not just any sum.} The bits must be {B:separate} (independent, or only weakly linked). "
        "Both pictures below add up five dice numbers, but only one makes a bell:", 14, gap=8)
    y_ = f.reserve(128)
    pg = f.pg
    copied = {t: (1 if t % 5 == 0 else 0) for t in range(5, 31)}
    ch.check(sorted(dice_sum(5)), sorted(copied))
    hist(pg, L + 10, y_ + 4, 210, 84, dice_sum(5), C.GREEN, "5 separate rolls, added")
    hist(pg, L + 270, y_ + 4, 210, 84, copied, C.RED, "1 roll, copied 5 times, added")
    pg.text(L + 115, y_ + 108, "bell ✓", 12, C.GREEN, F.BOLD, align="center")
    pg.text(L + 375, y_ + 108, "still flat: only 5, 10, ..., 30", 12, C.RED, F.BOLD, align="center")
    f.p("Copying one roll adds no new randomness, so the shape is just the single die, stretched. "
        "The honest rule: a sum of {B:many} contributions is close to Normal when they're {B:independent "
        "or only weakly linked}, each has a {B:finite spread}, and {B:no single one dominates} the total. "
        "(If one huge nudge outweighs all the rest, the total just looks like that one nudge.)", 14)
    ch.term("normal distribution", "the symmetric bell-shaped distribution you get when many small random effects add up")


def galton_page(ch):
    f = flow(ch)
    sec(f, "The Galton board: coin flips you can watch", room=420)
    y_ = f.reserve(250)
    pg = f.pg
    galton(pg, L + 120, y_ + 14, 8, 20)
    pg.circle(L + 120, y_ + 2, 3, C.ORANGE, 0.8, fillcolor=C.ORANGE)
    pts = [(0, 0), (-0.5, 1), (0, 2), (0.5, 3), (0, 4), (0.5, 5), (1, 6), (0.5, 7), (1, 8)]
    pg.poly([(L + 120 + a * 20, y_ + 6 + b * 18) for a, b in pts], C.RED, 1.2, dash=(3, 2))
    pg.note(L + 250, y_ + 6, "Each peg is a coin flip: left or right.\n8 rows = 8 flips. The bin a ball "
            "lands in\n= the number of rights.\n\nThe red path went L R R L R R L R:\n5 rights, so bin 5.\n\n"
            "Ending in the middle needs a mix of lefts\nand rights, and there are {B:many} such paths.\nThe "
            "edges need all-left or all-right:\nonly {B:one} path each.".replace("{B:", "").replace("}", ""),
            C.INK, 14)
    ch.check(math.comb(8, 4), 70)
    ch.check(math.comb(8, 0), 1)
    f.p("With 8 rows there are $2^8 = 256$ possible paths: 70 of them end in the middle bin but only 1 "
        "reaches each edge. Count paths, and the bell appears. (The counts 1, 8, 28, 56, 70, 56, 28, 8, "
        "1 are the same numbers as expanding $(a+b)^8$.)", 14)


def anatomy(ch):
    f = flow(ch)
    sec(f, "Anatomy of the bell", room=520)
    y_ = f.reserve(236)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 20, 300, 150, (-3.5, 3.5), (0, 0.45))
    ax.fill_under(pdf, -3.5, 3.5, C.LIGHT[C.ORANGE])
    ax.curve(pdf, -3.5, 3.5, C.ORANGE, 2.2)
    pg.line(ax.X(-3.5), ax.Y(0), ax.X(3.5), ax.Y(0), C.INK, 1)
    ax.vline(0, C.RED, 1.3, (4, 3), 0, 0.43)
    pg.text(ax.X(0), ax.Y(0.45) - 6, "mean = median = mode", 10, C.RED, F.BOLD, align="center", solid=False)
    ax.dot(1, pdf(1), C.PURPLE, 3.5)
    ax.dot(-1, pdf(-1), C.PURPLE, 3.5)
    ax.seg(0, 0.03, 1, 0.03, C.PURPLE, 1.4)
    pg.text(ax.X(0.5), ax.Y(0.03) - 14, "σ", 12, C.PURPLE, F.BOLD, align="center", solid=False)
    pg.note(ax.X(1.2), ax.Y(0.3), "bends from ∩\nto ∪ here, one\nσ from the middle", C.PURPLE, 13, solid=False)
    pg.note(ax.X(2.2), ax.Y(0.1), "tails fade but\nnever touch 0", C.GREY, 13, solid=False)
    for k in range(-3, 4):
        pg.text(ax.X(k), ax.Y(0) + 4, ["μ−3σ", "μ−2σ", "μ−σ", "μ", "μ+σ", "μ+2σ", "μ+3σ"][k + 3], 9,
                C.GREY, align="center", solid=False)
    pg.note(L + 360, y_ + 20, "Symmetric: the left\nhalf mirrors the right.\n\nOne peak in the\nmiddle.\n\n"
            "Two numbers pin\nit down completely:\nthe mean μ (where)\nand the standard\ndeviation σ (how wide).",
            C.INK, 14)
    ch.term("bell curve", "the Normal distribution's graph: symmetric, one central peak, tails fading to zero")
    f.p("Lecture 9's equation of the curve looks terrifying, but read it piece by piece:", 14, gap=6)
    y_ = f.reserve(150)
    pg = f.pg
    pg.eq(L + 20, y_ + 4, r"f(x)=\frac{1}{\sigma\sqrt{2\pi}}\;e^{-\frac12\left(\frac{x-\mu}{\sigma}\right)^2}", 24,
          C.ORANGE)
    pg.note(L + 20, y_ + 76, "(x − μ)/σ: how many σ's from the middle (the z-score, two pages on)", C.RED, 14)
    pg.note(L + 20, y_ + 98, "e to minus a square: 1 in the middle, shrinking fast either side (Chapter 21)",
            C.RED, 14)
    pg.note(L + 20, y_ + 120, "the front fraction just makes the total area exactly 1", C.GREY, 14)
    ch.formula(r"f(x)=\frac{1}{\sigma\sqrt{2\pi}}e^{-\frac12\left(\frac{x-\mu}{\sigma}\right)^2}", "Normal curve")
    f.gap(8)
    f.p("With $\\mu = 0$ and $\\sigma = 1$ it's the {B:standard Normal}: $f(x) = \\frac{1}{\\sqrt{2\\pi}}"
        "e^{-x^2/2}$. Every Normal curve is this one, slid along and stretched.", 14)
    ch.term("standard Normal distribution", "the Normal distribution with mean 0 and standard deviation 1")


def area(ch):
    f = flow(ch)
    sec(f, "Probability is area", room=520)
    f.p("Imagine a histogram of 100,000 people's heights with ever thinner bars: the tops of the bars "
        "melt into the smooth curve. The height of the curve is called {B:probability density}. On its "
        "own a single height means little; {B:areas} are what count:", 14, gap=10)
    ch.term("probability density", "the height of a smooth distribution curve; areas under it are probabilities")
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 250, 120, (-3.5, 3.5), (0, 0.42))
    ax.fill_under(pdf, -1, 1, C.LIGHT[C.ORANGE])
    ax.curve(pdf, -3.5, 3.5, C.ORANGE, 2)
    pg.line(ax.X(-3.5), ax.Y(0), ax.X(3.5), ax.Y(0), C.INK, 1)
    for k in (-1, 1):
        ax.vline(k, C.ORANGE, 1, (3, 2), 0, pdf(k))
    pg.text(ax.X(0), ax.Y(0.15), "0.68", 12, C.INK, F.BOLD, align="center")
    pg.note(L + 300, y_ + 10, "the whole area under the curve\n= 1 (everybody, 100%)\n\nthe shaded slice = "
            "the fraction\nof people between those values\n= the probability a random\nperson lands there",
            C.INK, 14)
    ch.check_num(Phi(1) - Phi(-1), 0.6827, tol=0.0001)
    f.p("{b:The 68-95-99.7 rule.} For {B:every} Normal distribution:", 14, gap=10)
    y_ = f.reserve(116)
    pg = f.pg
    ax = Axes(pg, L + 10, y_, 380, 70, (-3.5, 3.5), (0, 0.42))
    cols = [C.LIGHT[C.RED], C.LIGHT[C.ORANGE], C.LIGHT[C.YELLOW]]
    for k, col in zip((3, 2, 1), reversed(cols)):
        ax.fill_under(pdf, -k, k, col)
    ax.curve(pdf, -3.5, 3.5, C.ORANGE, 1.6)
    pg.line(ax.X(-3.5), ax.Y(0), ax.X(3.5), ax.Y(0), C.INK, 1)
    for k, pct in [(1, "68%"), (2, "95%"), (3, "99.7%")]:
        yy = ax.Y(0) + 6 + (k - 1) * 12
        pg.arrow(ax.X(-k), yy + 5, ax.X(k), yy + 5, C.INK, 0.8, head=3, both=True)
        pg.text(ax.X(3) + 10, yy, f"within {k}σ: {pct}", 9, C.INK, F.BOLD, solid=False)
    for k in (1, 2, 3):
        ch.check_num(Phi(k) - Phi(-k), [0.6827, 0.9545, 0.9973][k - 1], tol=0.0001)
    f.gap(8)
    f.p("So about 2 in 3 people are within one standard deviation of the mean, 19 in 20 within two, "
        "and almost everyone within three.", 14)


def zscore(ch):
    f = flow(ch)
    sec(f, "z-scores: a ruler marked in sigmas", room=520)
    f.p("IQ scores are Normal with mean 100 and standard deviation 15 (Lecture 9). Lay a {B:second "
        "ruler} under the IQ ruler, marked in steps of one σ. The reading on that ruler is the "
        "{B:z-score}: {B:how many standard deviations above (+) or below (−) the mean}.", 14, gap=12)
    y_ = f.reserve(140)
    pg = f.pg
    x0, w_ = L + 20, 450
    for row, (lab, fmt, col) in enumerate([("IQ", lambda k: str(100 + 15 * k), C.INK),
                                            ("seat cm", lambda k: str(42 + 6 * k), C.BROWN),
                                            ("z", lambda k: f"{k:+d}" if k else "0", C.ORANGE)]):
        yy = y_ + 10 + row * 36
        pg.text(x0 - 4, yy - 2, lab, 10, col, F.BOLD, align="right")
        pg.line(x0 + 10, yy + 6, x0 + w_, yy + 6, col, 1.4)
        for k in range(-3, 4):
            xx = x0 + 10 + (k + 3) * (w_ - 10) / 6
            pg.line(xx, yy, xx, yy + 12, col, 1.2)
            pg.text(xx, yy + 14, fmt(k), 10, col, F.BOLD if row == 2 else F.SANS, align="center")
    xx = x0 + 10 + (2 + 3) * (w_ - 10) / 6
    pg.line(xx, y_ + 4, xx, y_ + 118, C.RED, 1.2, dash=(3, 3))
    pg.note(xx - 200, y_ + 112, "IQ 130 = seat 54 cm = z of 2", C.RED, 14)
    step(f, r"z=\frac{x-\mu}{\sigma}", "distance from the mean ÷ the size of one step", size=22, color=C.ORANGE)
    ch.formula(r"z=\frac{x-\mu}{\sigma}", "z-score")
    ch.term("z-score", "how many standard deviations a value is above (+) or below (−) the mean: z = (x − μ)/σ")
    step(f, r"\text{IQ }75:\ z=\frac{75-100}{15}=\frac{-25}{15}\approx-1.67", "1.67 σ's below", size=18)
    ch.check_num((75 - 100) / 15, -1.667, tol=0.001)
    f.p("Once everything is in z-units, {B:one} table (or calculator button) works for every Normal "
        "distribution in the world. That table gives $\\Phi(z)$ (\"phi of z\"): the area to the {B:left} "
        "of $z$, i.e. the fraction of people {B:below} that point.", 14, gap=10)
    ch.symbol(r"\Phi(z)", "fie of z (capital phi)", "area under the standard Normal curve to the left of z")
    y_ = f.reserve(50)
    pg = f.pg
    zs = [-2, -1.67, -1, 0, 1, 1.28, 1.645, 2]
    cw = W / len(zs)
    for i, z in enumerate(zs):
        pg.rect(L + i * cw, y_, cw, 20, C.ORANGE, 0.6, fillcolor=C.LIGHT[C.ORANGE])
        pg.text(L + i * cw + cw / 2, y_ + 4, f"z = {z:g}", 10, C.INK, F.BOLD, align="center")
        pg.rect(L + i * cw, y_ + 20, cw, 20, C.ORANGE, 0.6)
        pg.text(L + i * cw + cw / 2, y_ + 24, f"{Phi(z):.4f}", 10, C.INK, align="center")
    ch.term("Normal table", "a table of Φ(z), the area to the left of z under the standard Normal curve")
    ch.check_num(Phi(1.28), 0.8997, tol=0.0001)


def iq(ch):
    f = flow(ch)
    sec(f, "Lecture 9's IQ range: what fraction scores 75 to 100?", room=420)
    y_ = f.reserve(140)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 260, 110, (40, 160), (0, 0.028))
    g = lambda v: pdf((v - 100) / 15) / 15
    ax.fill_under(g, 75, 100, C.LIGHT[C.ORANGE])
    ax.curve(g, 40, 160, C.ORANGE, 2)
    pg.line(ax.X(40), ax.Y(0), ax.X(160), ax.Y(0), C.INK, 1)
    for v in (55, 75, 100, 130, 145):
        pg.text(ax.X(v), ax.Y(0) + 4, str(v), 9, C.GREY, align="center", solid=False)
    pg.text(ax.X(88), ax.Y(0.008), "?", 16, C.RED, F.BOLD, align="center")
    pg.note(L + 310, y_ + 10, "Area between 75 and 100\n= (area left of 100)\n   − (area left of 75)", C.INK, 15)
    step(f, r"z_{100}=0,\quad z_{75}=-1.667", "convert both ends to z", size=18)
    step(f, r"\Phi(0)-\Phi(-1.667)=0.5000-0.0478", "look both up; half the area is left of the middle", size=18)
    step(f, r"=0.4522\approx45\%", "exactly the lecture's figure", size=20, color=C.GREEN)
    ch.check_num(Phi(0) - Phi(-5 / 3), 0.4522, tol=0.0001)
    f.p("(Lecture 9 uses this to show how a far-right group targeted its propaganda at people with "
        "IQ 75-100. The maths is neutral; what people do with it isn't.)", 13, C.GREY)


def seats(ch):
    f = flow(ch)
    sec(f, "The aeroplane seat problem", room=560)
    f.p("Lecture 9: design seats wide enough for {B:90% of people}; the widest 10% buy two tickets. "
        "First, measure a sample. The slides list 100 seat widths (cm); here they are as histograms, "
        "binned two ways:", 14, gap=10)
    m, s_ = st.mean(SEATS), st.stdev(SEATS)
    ch.check_num(m, 42.0, tol=0.01)
    ch.check_num(s_, 5.46, tol=0.01)
    y_ = f.reserve(140)
    pg = f.pg
    for k, bw in enumerate([2, 5]):
        x0 = L + 10 + k * 250
        ax = Axes(pg, x0, y_ + 5, 210, 100, (30, 58), (0, 0.09))
        edges = [30 + bw * i for i in range(int(28 / bw) + 1)]
        for a in edges:
            n = sum(1 for v in SEATS if a <= v < a + bw)
            d = n / (len(SEATS) * bw)
            if n:
                pg.rect(ax.X(a), ax.Y(d), ax.X(a + bw) - ax.X(a), ax.Y(0) - ax.Y(d), C.BROWN, 0.5,
                        fillcolor=C.LIGHT[C.BROWN])
        ax.curve(lambda v: pdf((v - m) / s_) / s_, 30, 58, C.ORANGE, 1.8)
        pg.line(ax.X(30), ax.Y(0), ax.X(58), ax.Y(0), C.INK, 1)
        for v in (30, 40, 50):
            pg.text(ax.X(v), ax.Y(0) + 4, str(v), 9, C.GREY, align="center", solid=False)
        pg.text(x0 + 105, y_ + 124, f"{bw} cm bins", 10, C.INK, F.BOLD, align="center")
    f.p("Same data, different binning, different look (the lecture's point). Either way, the orange "
        "Normal curve fits well. The data give mean {B:42.0 cm} and standard deviation {B:5.46 cm}; the "
        "slides round this to {B:6 cm}, so we'll use 6.", 14, gap=8)
    f.p("{b:Now work backwards.} Before, we had $x$ and wanted the area. Now we have the area (90% to "
        "the left) and want $x$:", 14, gap=6)
    y_ = f.reserve(110)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 5, 240, 90, (-3.5, 3.5), (0, 0.42))
    ax.fill_under(pdf, -3.5, 1.2816, C.LIGHT[C.ORANGE])
    ax.fill_under(pdf, 1.2816, 3.5, C.LIGHT[C.RED])
    ax.curve(pdf, -3.5, 3.5, C.ORANGE, 1.8)
    pg.line(ax.X(-3.5), ax.Y(0), ax.X(3.5), ax.Y(0), C.INK, 1)
    pg.text(ax.X(-0.3), ax.Y(0.12), "90%", 12, C.INK, F.BOLD, align="center")
    pg.text(ax.X(2.3), ax.Y(0.12), "10%", 10, C.RED, F.BOLD, align="center")
    pg.text(ax.X(1.28), ax.Y(0) + 4, "z = ?", 10, C.RED, F.BOLD, align="center")
    pg.note(L + 300, y_ + 10, "Find the z with Φ(z) = 0.90.\nThe table (previous page):\nΦ(1.28) ≈ 0.90, so "
            "z ≈ 1.28.\nTwo tickets beyond here.", C.INK, 14)
    step(f, r"z=\frac{x-\mu}{\sigma}\ \Rightarrow\ x=\mu+z\sigma", "transpose (Chapter 14)", size=18)
    step(f, r"x=42+1.28\times6=49.7\text{ cm}", "", size=20, color=C.GREEN)
    ch.check_num(42 + 1.2816 * 6, 49.69, tol=0.01)
    f.p("Seats 49.7 cm wide fit 90% of passengers. (With the unrounded 5.46 cm you'd get 49.0 cm; "
        "rounding σ costs airlines 7 mm per seat.)", 14)
    ch.check_num(42.0 + 1.2816 * s_, 49.0, tol=0.05)


def normal_or_not(ch):
    f = flow(ch)
    sec(f, "Is it Normal? And stay critical", room=420)
    f.p("{b:Probably Normal} (Lecture 9): averaged qualities like IQ, test scores, rainfall, molecular "
        "speeds, football crowds, women's heights. {R:Definitely not:} anything {B:lopsided} or with a "
        "{B:hard limit on one side}, like wages (skewed, Chapter 24). Two numbers measure the damage:",
        14, gap=10)
    y_ = f.reserve(100)
    pg = f.pg
    shapes = [("skewness ≠ 0", "lopsided", lambda v: (v + 2) * math.exp(-(v + 2)) * 2.6 if v > -2 else 0),
              ("kurtosis < 0", "too flat (e.g. uniform)", lambda v: 0.28 if abs(v) < 1.7 else 0),
              ("kurtosis > 0", "too peaky, heavy tails", lambda v: 0.45 / (1 + 2.5 * v * v))]
    for k, (nm, why, fn) in enumerate(shapes):
        ax = Axes(pg, L + 10 + k * 165, y_, 140, 60, (-3, 3), (0, 0.5))
        ax.curve(pdf, -3, 3, C.GREY, 1, dash=(3, 2))
        ax.curve(fn, -3, 3, C.ORANGE, 1.8, n=300)
        pg.line(ax.X(-3), ax.Y(0), ax.X(3), ax.Y(0), C.INK, 1)
        pg.text(L + 10 + k * 165, y_ + 66, nm, 11, C.ORANGE, F.BOLD)
        pg.text(L + 10 + k * 165, y_ + 82, why, 9, C.GREY)
    ch.term("kurtosis", "how peaky or flat a distribution is compared with the Normal (0 for Normal)")
    f.p("A Normal distribution has skewness 0 and kurtosis 0. Lecture 9's table: one uniform variable "
        "has kurtosis −1.18 (flat), the sum of four has −0.32: {B:adding makes it more Normal}, the "
        "lesson of page 2.", 14, gap=10)
    f.p("{R:Be critical.} Lecture 9 tells the story of {h:The Bell Curve} (1994) and a world IQ map built "
        "from biased samples: one country's \"national IQ\" came from a group of children in a Spanish "
        "care home; inconvenient high-scoring samples were dropped. Chapter 23's detective questions "
        "(who was sampled? what's missing?) matter more than the maths. The lecture's last word: "
        "{B:scientists can be lazy, prejudiced and wrong but still get published, so develop your own "
        "analytical skills}.", 14)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Use the Φ table on the z-score page. Answers in grey.", 13.5, gap=10)
    groups = [
        ("z-scores", ["IQ 115: z = ?", "IQ 70: z = ?", "A seat width of 36 cm (μ = 42, σ = 6): z = ?",
                      "What IQ has z = 1.645?"],
         "1. 1   2. −2   3. −1   4. 100 + 1.645 × 15 ≈ 124.7"),
        ("Areas", ["Fraction of people with IQ below 130", "Fraction with IQ above 115",
                   "Fraction between IQ 85 and 115", "Fraction with IQ between 100 and 124.7"],
         "5. Φ(2) = 0.977   6. 1 − Φ(1) = 0.159   7. 0.683 (the 68% rule)   8. 0.95 − 0.5 = 0.45"),
        ("Backwards", ["An exam is Normal, μ = 60, σ = 10. The top 10% get a distinction. What mark is "
                       "needed?",
                       "Which is more Normal: one die, or the average of 20 dice? Why?"],
         "9. 60 + 1.28 × 10 ≈ 72.8   10. the average of 20: sums of many independent bits become bell-shaped"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 24 * len(qs) + 30)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check_num(100 + 1.645 * 15, 124.7, tol=0.1)
    ch.check_num(Phi(2), 0.977, tol=0.001)
    ch.check_num(1 - Phi(1), 0.159, tol=0.001)
    ch.check_num(Phi(1.645) - 0.5, 0.45, tol=0.001)
    ch.check_num(60 + 1.2816 * 10, 72.8, tol=0.05)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    flat_to_bell(ch)
    galton_page(ch)
    anatomy(ch)
    area(ch)
    zscore(ch)
    iq(ch)
    seats(ch)
    normal_or_not(ch)
    your_turn(ch)
