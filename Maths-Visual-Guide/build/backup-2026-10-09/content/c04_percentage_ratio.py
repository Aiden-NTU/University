"""Chapter 4 - Percentage and ratio. A 100-square, shop receipts, bar models, squash recipes,
beakers of solution and the 'one of them' table."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 4
NUM = 4
TITLE = "Percentage and ratio"
SHORT = "Percentage and ratio"
SLUG = "Percentage-Ratio"
ACCENT = C.ORANGE
REQUIRES = ["fraction", "decimal-to-fraction", "fraction-to-decimal", "multiply-fractions",
            "simplify-fraction", "hcf", "decimal-arithmetic", "rounding", "recurring-decimals"]
INTRODUCES = ["percentage", "percent-conversion", "percentage-of", "reverse-percentage", "multiplier",
              "percentage-change", "ratio", "simplify-ratio", "share-in-ratio", "unitary-method",
              "proportion", "concentration"]

SQUASH = "#e8590c"
WATER = "#a5d8ff"
PAPER = "#fffdf8"


def icon(pg, x, y):
    for i in range(3):
        for j in range(3):
            pg.rect(x + j * 6, y + i * 6, 5.4, 5.4, C.ORANGE, 0.4,
                    fillcolor=C.ORANGE if (i * 3 + j) < 4 else "#ffffff")


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def grid100(pg, x, y, s, n, col=C.ORANGE, light=None, label=None):
    """A 10 x 10 square, first n little squares shaded (row by row)."""
    for i in range(10):
        for j in range(10):
            k = i * 10 + j
            fc = col if k < n else (light or "#ffffff")
            pg.rect(x + j * s, y + i * s, s, s, "#9a9a9a", 0.35, fillcolor=fc, layer=C.UNDER)
    pg.rect(x, y, 10 * s, 10 * s, C.INK, 1.0)
    if label:
        pg.text(x + 5 * s, y + 10 * s + 4, label, 12, C.INK, F.BOLD, align="center")


def bar(pg, x, y, w, h, n, fills=None, labels=None, col=C.ORANGE, size=11):
    """A bar cut into n equal blocks; fills[i] colours block i, labels[i] writes inside it."""
    bw = w / n
    for i in range(n):
        fc = (fills or {}).get(i, "#ffffff")
        pg.rect(x + i * bw, y, bw, h, col, 1.0, fillcolor=fc)
        if labels and i in labels:
            pg.text(x + i * bw + bw / 2, y + h / 2 - size * 0.62, labels[i], size, C.INK, F.BOLD,
                    align="center", solid=False)
    return bw


def cup(pg, x, y, col, w=18, h=24):
    pg.poly([(x, y), (x + 3, y + h), (x + w - 3, y + h), (x + w, y)], C.INK, 1.0,
            fill=None)
    pg.fillpoly([(x + 1, y + 5), (x + 3.4, y + h - 0.5), (x + w - 3.4, y + h - 0.5), (x + w - 1, y + 5)], col)


def beaker(pg, x, y, w, h, fill_h, a_frac, label=None, a_col=C.PURPLE, water=WATER):
    """A beaker with liquid up to fill_h; bottom a_frac of the liquid is chemical A."""
    top = y + h - fill_h
    ah = fill_h * a_frac
    pg.rect(x, top, w, fill_h - ah, water, 0.1, fillcolor=water, layer=C.UNDER)
    pg.rect(x, y + h - ah, w, ah, a_col, 0.1, fillcolor="#b98ee0" if a_col == C.PURPLE else a_col,
            layer=C.UNDER)
    pg.poly([(x - 4, y), (x, y + 4), (x, y + h), (x + w, y + h), (x + w, y + 4), (x + w + 4, y)], C.INK, 1.4)
    if label:
        pg.text(x + w / 2, y + h + 6, label, 11, C.INK, F.BOLD, align="center")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 4, "Percentage and ratio", "comparing amounts: out of a hundred, "
                     "and parts of a recipe", C.ORANGE, PAPER)
    grid100(pg, L + 20, 200, 16, 37)
    pg.note(L + 20, 366, "37 out of 100 = 37%", C.ORANGE, 20)
    x0 = L + 250
    for i in range(1):
        cup(pg, x0, 230, SQUASH, 26, 34)
    for i in range(4):
        cup(pg, x0 + 50 + i * 34, 230, WATER, 26, 34)
    pg.text(x0 + 13, 272, "1", 16, SQUASH, F.BOLD, align="center")
    pg.text(x0 + 110, 272, "4", 16, C.BLUE, F.BOLD, align="center")
    pg.text(x0 + 36, 272, ":", 16, C.INK, F.BOLD, align="center")
    pg.note(x0, 300, "squash to water 1 : 4", SQUASH, 20)
    f = ch.flow(top=420)
    f.p("\"20% off\". \"Mix 1 part squash with 4 parts water\". \"The model is 1 : 72 scale\". Both "
        "{B:percentages} and {B:ratios} answer the same kind of question: {o:how big is one amount "
        "compared to another?} They're fractions (Chapter 2) dressed for everyday life.", 14, gap=10)
    f.p("This chapter goes through all of Lecture 3: percentages of amounts, going up and down by a "
        "percentage, working backwards, ratios, sharing in a ratio, scaling with the \"one of them\" "
        "table, and mixing solutions.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 3} {y:(ratios and proportions).}", 12.5)


def per_cent(ch):
    f = flow(ch)
    sec(f, "Per cent means \"out of a hundred\"")
    f.p("\"Cent\" means hundred (a century is 100 years). So {B:per cent} means {B:per hundred}: "
        "chop the whole thing, whatever it is, into 100 equal pieces, and count pieces. The symbol "
        "{B:%} is a tiny drawing of \"/100\" (a slash between two zeros).", 14, gap=10)
    ch.term("percentage (%)", "a number of pieces out of 100 equal pieces of the whole")
    ch.symbol(r"\%", "per cent", "out of 100, so 25% means 25/100")
    y = f.reserve(160)
    pg = f.pg
    items = [(25, "25% = 1/4"), (50, "50% = 1/2"), (5, "5% = 1/20"), (100, "100% = all of it")]
    for i, (n, lab) in enumerate(items):
        grid100(pg, L + 10 + i * 124, y, 10.4, n, label=lab)
    f.p("{b:More than 100%} just means more than one whole. {B:125%} is one full square and "
        "another quarter of a square:", 14, gap=6)
    y = f.reserve(130)
    pg = f.pg
    grid100(pg, L + 20, y, 10.4, 100)
    grid100(pg, L + 140, y, 10.4, 25)
    pg.text(L + 128, y + 44, "+", 18, C.INK, F.BOLD)
    pg.note(L + 270, y + 20, "125% = 125/100 = 1.25\n(one and a quarter wholes)", C.ORANGE, 17)
    ch.check(sp.Rational(125, 100), sp.Rational(5, 4))


def converting(ch):
    f = flow(ch)
    sec(f, "Three outfits for the same number", room=330)
    f.p("A quarter can wear three outfits: $\\frac14$, $0.25$ and $25\\%$. Moving between them is "
        "always one of these arrows:", 14, gap=8)
    y = f.reserve(170)
    pg = f.pg
    P = {"pct": (L + 250, y + 20), "dec": (L + 90, y + 140), "frac": (L + 410, y + 140)}
    for key, (cx, cy), lab, col in [("pct", P["pct"], "25%", C.ORANGE), ("dec", P["dec"], "0.25", C.BLUE),
                                    ("frac", P["frac"], None, C.GREEN)]:
        pg.circle(cx, cy, 26, col, 1.8, fillcolor=C.LIGHT[col])
        if lab:
            pg.text(cx, cy - 9, lab, 16, col, F.BOLD, align="center")
        else:
            pg.eq(cx, cy, r"\tfrac14", 18, col, align="center", valign="middle")
    pg.arrow(P["pct"][0] - 26, P["pct"][1] + 14, P["dec"][0] + 12, P["dec"][1] - 26, C.BLUE, 1.4, bend=0.12)
    pg.note(L + 40, y + 50, "÷ 100\n(digits slide 2\nplaces right)", C.BLUE, 15)
    pg.arrow(P["dec"][0] + 26, P["dec"][1] + 4, P["frac"][0] - 26, P["frac"][1] + 4, C.GREEN, 1.4)
    pg.note(L + 150, y + 150, "write over 100 and simplify (Chapter 3)", C.GREEN, 15)
    pg.arrow(P["frac"][0] - 12, P["frac"][1] - 26, P["pct"][0] + 26, P["pct"][1] + 14, C.ORANGE, 1.4, bend=0.12)
    pg.note(L + 360, y + 40, "× 100 %\n(1/4 × 100 = 25)", C.ORANGE, 15)
    f.p("{b:Your Lecture 3 examples, one arrow each:}", 14, gap=6)
    rows = [(r"5\%=\frac{5}{100}=0.05", "percent → divide by 100"),
            (r"125\%=\frac{125}{100}=1.25", "same arrow, bigger number"),
            (r"0.75=\frac{75}{100}=75\%", "decimal → multiply by 100"),
            (r"1.583=158.3\%", "decimal → multiply by 100")]
    for e, why in rows:
        step(f, e, why, size=19)
    ch.check(sp.Rational(5, 100), sp.Rational(5, 100))
    ch.check(sp.Rational(1583, 1000) * 100, sp.Rational(1583, 10))


def pct_of(ch):
    f = flow(ch)
    sec(f, "Finding 15% of 23: the 10% ladder", room=440)
    f.p("You don't need a formula to begin with. {B:10%} is easy: it's a tenth, so divide by 10 "
        "(digits slide one place, Chapter 3). Build everything else from 10% and 1%:", 14, gap=8)
    y = f.reserve(104) + 14
    pg = f.pg
    bw = bar(pg, L + 10, y + 10, 470, 34, 10, fills={0: C.LIGHT[C.ORANGE]},
             labels={i: "2.3" for i in range(10)})
    pg.brace(L + 10, y + 50, L + 480, y + 50, C.INK, 1.1, 7)
    pg.note(L + 200, y + 60, "the whole: 23 = 100%", C.INK, 16)
    pg.note(L + 10, y - 12, "10 equal blocks, each 10%", C.ORANGE, 15)
    ch.check(sp.Rational(23, 10), sp.Rational(23, 10))
    step(f, r"10\%\text{ of }23 = 2.3", "divide by 10", size=19)
    step(f, r"5\%\text{ of }23 = 1.15", "half of 10%", size=19)
    step(f, r"15\%\text{ of }23 = 2.3+1.15=3.45", "10% + 5%", size=19, color=C.GREEN)
    ch.check(sp.Rational(15, 100) * 23, sp.Rational(345, 100))
    f.p("{b:The one-line version} from the lecture: \"of\" means multiply, and $x\\%$ means "
        "$\\frac{x}{100}$:", 14, gap=6)
    y = f.reserve(78)
    pg = f.pg
    pg.eq(L + 30, y, r"x\%\text{ of }y=\frac{x}{100}\times y", 22)
    pg.eq(L + 30, y + 50, r"15\%\text{ of }23=0.15\times23=3.45", 18, C.BLUE)
    pg.note(L + 330, y + 4, "x is the percentage,\ny is the whole amount", C.RED, 15)
    ch.formula(r"x\%\text{ of }y=\frac{x}{100}\times y", "percentage of an amount")
    f.p("{b:And above 100%:} 125% of 20 is $1.25 \\times 20 = 25$. Bigger than 20, as it should be.",
        14)
    ch.check(sp.Rational(125, 100) * 20, 25)


def backwards(ch):
    f = flow(ch)
    sec(f, "Working backwards: 25% of A is 14 kg", room=300)
    f.p("You know a {B:part} and want the {B:whole}. Draw the whole as a bar. 25% is a quarter, so "
        "cut it into 4 blocks. One block is 14 kg:", 14, gap=8)
    y = f.reserve(104) + 14
    pg = f.pg
    bar(pg, L + 30, y + 10, 400, 38, 4, fills={0: C.LIGHT[C.ORANGE]},
        labels={0: "14 kg", 1: "14 kg", 2: "14 kg", 3: "14 kg"}, size=13)
    pg.note(L + 30, y - 12, "25% (given)", C.ORANGE, 15)
    pg.note(L + 130, y - 12, "the other blocks are the same size", C.GREY, 15)
    pg.brace(L + 30, y + 54, L + 430, y + 54, C.INK, 1.1, 7)
    pg.note(L + 170, y + 64, "whole = 4 × 14 = 56 kg", C.GREEN, 17)
    ch.check(4 * 14, 56)
    f.p("{b:The lecture's way} (go through 1%, it always works, even for ugly percentages):", 14, gap=6)
    step(f, r"25\%\ \to\ 14", "what we know", size=19)
    step(f, r"1\%\ \to\ \frac{14}{25}", "÷ 25 on both sides", size=19)
    step(f, r"100\%\ \to\ 100\times\frac{14}{25}=56", "× 100 on both sides", size=19, color=C.GREEN)
    f.p("{R:Common slip:} 25% of A is 14, so A is 14 + 25% of 14? No! The 25% is of the "
        "{B:unknown whole}, not of 14. Always ask \"percent of {B:what}?\"", 13.5)


def receipts(ch):
    f = flow(ch)
    sec(f, "Going up and down: the multiplier", room=420)
    f.p("Increase 56.0 ml by 10%. The old amount is 100%. Adding 10% makes it {B:110%} of the "
        "old amount, so multiply by $\\frac{110}{100} = 1.10$. That number is the {B:multiplier}.",
        14, gap=8)
    ch.term("multiplier", "the number you multiply by to apply a percentage change, e.g. ×1.1 for +10%")
    y = f.reserve(150)
    pg = f.pg
    boxes = [(L + 10, "56.0 ml", C.INK), (L + 185, "61.6 ml", C.GREEN), (L + 360, "55.44 ml", C.RED)]
    for x, s, col in boxes:
        pg.rect(x, y + 30, 120, 50, col, 1.6, fillcolor=C.LIGHT.get(col, "#ffffff"), r=8)
        pg.text(x + 60, y + 44, s, 17, col, F.BOLD, align="center")
    pg.arrow(L + 132, y + 55, L + 183, y + 55, C.GREEN, 1.8)
    pg.eq(L + 157, y + 6, r"\times1.10", 16, C.GREEN, align="center")
    pg.note(L + 132, y + 84, "+10%", C.GREEN, 15)
    pg.arrow(L + 307, y + 55, L + 358, y + 55, C.RED, 1.8)
    pg.eq(L + 332, y + 6, r"\times0.90", 16, C.RED, align="center")
    pg.note(L + 307, y + 84, "-10%", C.RED, 15)
    pg.note(L + 10, y + 108, "Up 10% then down 10% does NOT get you back to 56! The second 10% is "
            "10% of a bigger number (61.6), so it takes away more (6.16) than was added (5.6).",
            C.PURPLE, 15, w=W - 10)
    ch.check(sp.Rational(56) * sp.Rational(110, 100), sp.Rational(616, 10))
    ch.check(sp.Rational(616, 10) * sp.Rational(90, 100), sp.Rational(5544, 100))
    f.p("(The lecture rounds 55.44 to 55.4.) {b:Decreasing by 10%} leaves {B:90%}, so the "
        "multiplier is 0.90. The rule:", 14, gap=6)
    y = f.reserve(56)
    pg = f.pg
    pg.rect(L + 10, y, W - 20, 50, C.ORANGE, 1.2, fillcolor="#fff5ea", r=8)
    pg.rich(L + 24, y + 8, "{B:up by r%}: multiply by $\\frac{100+r}{100}$        "
            "{B:down by r%}: multiply by $\\frac{100-r}{100}$", W - 40, 14)
    ch.formula(r"\text{new}=\text{old}\times\frac{100\pm r}{100}", "percentage increase / decrease")
    f.p("{b:Where did the missing 1% go? Draw it.} Two multipliers in a row multiply, and multiplying is "
        "the area of a rectangle (Chapter 1). Let the starting amount be a 1 by 1 square:", 14, gap=12)
    U, P = 110, 11
    y = f.reserve(U + P + 70)
    pg = f.pg
    x1, y1 = L + 30, y + 30
    pg.rect(x1, y1, U, U, C.INK, 1.0, fillcolor=C.LIGHT[C.BLUE])
    pg.rect(x1 + U, y1, P, U, C.GREEN, 1.0, fillcolor=C.LIGHT[C.GREEN])
    pg.rect(x1, y1 - P, U, P, C.GREEN, 1.0, fillcolor=C.LIGHT[C.GREEN])
    pg.rect(x1 + U, y1 - P, P, P, C.GREEN, 1.0, fillcolor=C.GREEN)
    pg.text(x1 + U / 2 - 20, y1 + U / 2 - 8, "1 (start)", 12, C.BLUE, F.BOLD)
    pg.note(x1 + U + P + 4, y1 - 22, "0.01: 10% of the 10%", C.GREEN, 13)
    pg.note(x1 - 20, y1 + U + 6, "up 10%, then up 10% again:\n1 + 0.1 + 0.1 + 0.01 = 1.21", C.GREEN, 13)
    ch.check(sp.Rational(11, 10) ** 2, sp.Rational(121, 100))
    x2, y2 = L + 280, y + 30
    pg.rect(x2, y2, U, U, C.INK, 1.0, fillcolor=C.LIGHT[C.BLUE])
    pg.rect(x2 + U, y2, P, U, C.GREEN, 1.0, fillcolor=C.LIGHT[C.GREEN])
    pg.rect(x2, y2, U + P, P, C.RED, 1.2, fillcolor=C.LIGHT[C.RED], dash=(3, 2))
    pg.rect(x2 + U, y2, P, P, C.RED, 1.0, fillcolor=C.RED)
    pg.text(x2 + U / 2 - 20, y2 + U / 2 - 8, "1 (start)", 12, C.BLUE, F.BOLD)
    pg.note(x2 + U + P + 4, y2 + 30, "green: +0.1\n(the 10% rise)", C.GREEN, 13)
    pg.note(x2 + U + P + 4, y2 - 14, "red: −0.11, the whole\nnew width loses 10%", C.RED, 13)
    pg.note(x2 - 20, y2 + U + 6, "up 10%, then down 10%:\n1 + 0.1 − 0.1 − 0.01 = 0.99", C.RED, 13)
    ch.check(sp.Rational(11, 10) * sp.Rational(9, 10), sp.Rational(99, 100))
    f.p("On the right, the 10% cut is taken off the {B:new, wider} amount, so it also slices off the little "
        "dark corner: 10% of the 10% that was added. That corner, 0.01, is the lost 1%. $56 \\times 0.99 = "
        "55.44$ ✓. On the left the same corner is a bonus: that's {B:interest on interest}, which Chapter 21 "
        "turns into compound growth.", 14, gap=10)
    ch.check(sp.Rational(56) * sp.Rational(99, 100), sp.Rational(5544, 100))
    f.p("{b:A shop receipt:} a £40 jacket in a 30% sale. Multiplier $\\frac{70}{100} = 0.7$, so "
        "you pay $40 \\times 0.7 = $ {G:£28}.", 14)
    ch.check(40 * sp.Rational(7, 10), 28)


def change(ch):
    f = flow(ch)
    sec(f, "Percentage change: always compare to where you started", room=260)
    f.p("A price goes from £40 to £50. By what percentage did it rise? Take the {B:change} and "
        "compare it with the {B:original}:", 14, gap=8)
    y = f.reserve(60)
    pg = f.pg
    pg.eq(L + 30, y, r"\text{percentage change}=\frac{\text{change}}{\text{original}}\times100", 20)
    ch.formula(r"\frac{\text{new}-\text{old}}{\text{old}}\times100", "percentage change")
    step(f, r"\frac{50-40}{40}\times100=\frac{10}{40}\times100=25\%", "a rise of 25%", size=19)
    step(f, r"\frac{40-50}{50}\times100=\frac{-10}{50}\times100=-20\%", "back down: only 20% (and a minus sign means a fall)", size=19)
    ch.check(sp.Rational(10, 40) * 100, 25)
    ch.check(sp.Rational(-10, 50) * 100, -20)
    f.p("Same £10 gap, different percentages, because the \"original\" is different each time.", 13.5,
        C.PURPLE)


def mixture_pct(ch):
    f = flow(ch)
    sec(f, "What percentage of the mixture is B?", room=300)
    f.p("250 mg of A is mixed with some B to make 1.21 g of mixture. What percentage is B? "
        "{B:First, same units}: 1.21 g is 1210 mg (1 g = 1000 mg).", 14, gap=8)
    y = f.reserve(130)
    pg = f.pg
    pg.rect(L + 30, y, 400, 36, C.INK, 1.2)
    wA = 400 * 250 / 1210
    pg.rect(L + 30, y, wA, 36, C.PURPLE, 0.1, fillcolor=C.LIGHT[C.PURPLE], layer=C.UNDER)
    pg.rect(L + 30 + wA, y, 400 - wA, 36, C.TEAL, 0.1, fillcolor=C.LIGHT[C.TEAL], layer=C.UNDER)
    pg.text(L + 30 + wA / 2, y + 10, "A: 250", 12, C.PURPLE, F.BOLD, align="center")
    pg.text(L + 30 + wA + (400 - wA) / 2, y + 10, "B: 1210 - 250 = 960", 12, C.TEAL, F.BOLD, align="center")
    pg.brace(L + 30, y + 42, L + 430, y + 42, C.INK, 1.1, 7)
    pg.note(L + 170, y + 52, "whole mixture 1210 mg", C.INK, 15)
    pg.eq(L + 30, y + 80, r"\frac{960}{1210}\times100\approx79.3\%", 20, C.TEAL)
    ch.check_num(960 / 1210 * 100, 79.34, tol=0.01)
    f.p("{B:Part over whole, times 100} is the percentage every time.", 14)


def ratio_intro(ch):
    f = flow(ch)
    sec(f, "Ratio: a recipe", room=420)
    f.p("Squash bottles say {B:\"1 part squash to 4 parts water\"}. A \"part\" can be any size of "
        "cup: an egg-cup or a bucket. The ratio only tells you the {B:shape of the recipe}, not the "
        "amount. We write it {B:1 : 4}, read \"one {B:to} four\".", 14, gap=8)
    ch.term("ratio", "how many parts of one thing for every so many parts of another, written a : b")
    ch.symbol(r"a:b", "a to b", "a parts of one thing for every b parts of the other")
    y = f.reserve(120)
    pg = f.pg
    for k, (sz, lab) in enumerate([(14, "egg-cups: 1 + 4"), (20, "mugs: 1 + 4"), (28, "jugs: 1 + 4")]):
        x0 = L + 10 + k * 165
        cup(pg, x0, y + 40 - sz, SQUASH, sz * 0.8, sz)
        for i in range(4):
            cup(pg, x0 + (i + 1) * (sz * 0.8 + 5), y + 40 - sz, WATER, sz * 0.8, sz)
        pg.note(x0, y + 48, lab, C.INK, 15)
    pg.note(L + 10, y + 78, "Three very different amounts, all the same taste: every one is 1 : 4.",
            C.PURPLE, 16)
    f.p("{b:Double the parts, same ratio:} 2 : 8 tastes identical to 1 : 4. So ratios {B:simplify} "
        "exactly like fractions (Chapter 2): divide every number by the same thing.", 14, gap=8)
    y = f.reserve(50)
    pg = f.pg
    pg.eq(L + 30, y, r"2:8\ =\ 1:4", 20)
    pg.eq(L + 200, y, r"260:100:20\ =\ 13:5:1", 20)
    pg.note(L + 30, y + 26, "÷ 2", C.RED, 15)
    pg.note(L + 200, y + 26, "÷ 20 (the HCF): a ratio can have 3 parts!", C.RED, 15)
    ch.check(sp.gcd(sp.gcd(260, 100), 20), 20)
    f.p("{R:Order matters:} squash : water 1 : 4 is not water : squash 1 : 4. That second one would "
        "be very strong squash!", 13.5)


def scale(ch):
    f = flow(ch)
    sec(f, "Reading the lecture's notation:  a : b :: 1 : 72", room=320)
    f.p("A model aeroplane: 1 cm on the model stands for 72 cm on the real plane. The scale is "
        "{B:1 : 72}. If the model is $a$ cm long and the real plane is $b$ cm long:", 14, gap=8)
    y = f.reserve(70)
    pg = f.pg
    pg.eq(L + 30, y, r"a:b\ ::\ 1:72", 24)
    pg.note(L + 200, y - 4, "say: \"a is to b as 1 is to 72\"\nthe :: means \"is in the same ratio as\"",
            C.RED, 15)
    ch.symbol(r"::", "is in the same ratio as", "a:b :: c:d means a/b = c/d")
    f.p("Every ratio statement can be rewritten as a fraction statement. These all say the same "
        "thing (the lecture lists them):", 14, gap=6)
    y = f.reserve(56)
    pg = f.pg
    for i, e in enumerate([r"\frac{a}{b}=\frac{1}{72}", r"b=72a", r"a=\frac{b}{72}"]):
        pg.eq(L + 40 + i * 150, y, e, 20, C.BLUE)
    f.p("{h:Say it in words:} the real thing is 72 times longer than the model; the model is one "
        "72nd of the real thing. A 30 cm model means a $30 \\times 72 = 2160$ cm (21.6 m) plane.",
        13.5, C.BROWN)
    ch.check(30 * 72, 2160)


def sharing(ch):
    f = flow(ch)
    sec(f, "Sharing in a ratio: count the parts", room=460)
    f.p("{B:Lecture 3, Example 3.} 336 g of alloy is copper, lead and tin in the ratio 16 : 4 : 1. "
        "How much of each? The lecture's advice: {B:count the parts}.", 14, gap=8)
    y = f.reserve(100)
    pg = f.pg
    cols = {"Cu": ("#d9822b", 16), "Pb": ("#6c7a89", 4), "Sn": ("#c9ced6", 1)}
    x = L + 10
    bw = 470 / 21
    for name, (col, n) in cols.items():
        for i in range(n):
            pg.rect(x, y + 20, bw, 34, C.INK, 0.6, fillcolor=col)
            x += bw
    pg.note(L + 10, y - 2, "16 copper blocks", "#b0621a", 15)
    pg.note(L + 10 + 16 * bw, y - 2, "4 lead", C.GREY, 15)
    pg.note(L + 10 + 20 * bw - 8, y + 60, "1 tin", C.GREY, 15)
    pg.brace(L + 10, y + 58, L + 10 + 16 * bw, y + 58, C.INK, 1.0, 6)
    pg.note(L + 100, y + 66, "21 blocks altogether = 336 g", C.INK, 15)
    step(f, r"16+4+1=21\text{ parts}", "1. count the parts", size=19)
    step(f, r"336\div21=16\text{ g per part}", "2. how heavy is one part?", size=19)
    step(f, r"16\times16=256,\ \ 4\times16=64,\ \ 1\times16=16", "3. each metal", size=17)
    step(f, r"256+64+16=336\ \checkmark", "4. check they add back up", size=17, color=C.GREEN)
    ch.check(336 // 21, 16)
    ch.check(256 + 64 + 16, 336)
    f.p("{b:Then 4 g copper, 36 g lead and 4 g tin are added:} 260 g, 100 g and 20 g (380 g in "
        "all). The new ratio is 260 : 100 : 20, which simplifies (÷ 20) to {G:13 : 5 : 1}.", 14)
    ch.check(sp.Rational(260, 20), 13)


def unitary(ch):
    f = flow(ch)
    sec(f, "The \"one of them\" table (unitary method)", room=430)
    f.p("{B:Lecture 3, Example 2.} 2.504 g of copper oxide contains 2 g of copper. How much copper "
        "is in 0.939 g of copper oxide? Make a two-column table and always pass through {B:one}:",
        14, gap=8)
    ch.term("unitary method", "scale a known pair down to 1 unit, then up to the amount you want")
    y = f.reserve(150)
    pg = f.pg
    x0 = L + 30
    pg.rect(x0, y, 300, 30, C.ORANGE, 1, fillcolor=C.LIGHT[C.ORANGE])
    pg.text(x0 + 75, y + 8, "copper oxide", 12, C.INK, F.BOLD, align="center")
    pg.text(x0 + 225, y + 8, "copper", 12, "#b0621a", F.BOLD, align="center")
    rows = [(r"2.504\text{ g}", r"2\text{ g}"), (r"1\text{ g}", r"\frac{2}{2.504}\text{ g}"),
            (r"0.939\text{ g}", r"0.939\times\frac{2}{2.504}=0.75\text{ g}")]
    for i, (a, b) in enumerate(rows):
        yy = y + 30 + i * 38
        pg.rect(x0, yy, 150, 38, C.ORANGE, 0.8)
        pg.rect(x0 + 150, yy, 150, 38, C.ORANGE, 0.8)
        pg.eq(x0 + 75, yy + 19, a, 15, align="center", valign="middle")
        pg.eq(x0 + 225, yy + 19, b, 13 if i == 2 else 15, C.GREEN if i == 2 else C.INK,
              align="center", valign="middle")
    pg.arrow(x0 + 310, y + 50, x0 + 310, y + 84, C.RED, 1.4, bend=-0.5)
    pg.note(x0 + 330, y + 52, "÷ 2.504 on both sides", C.RED, 15)
    pg.arrow(x0 + 310, y + 90, x0 + 310, y + 122, C.BLUE, 1.4, bend=-0.5)
    pg.note(x0 + 330, y + 92, "× 0.939 on both sides", C.BLUE, 15)
    ch.check_num(0.939 * 2 / 2.504, 0.75)
    f.p("Whatever you do to one column, do to the other. That keeps the ratio the same, which is "
        "what {B:proportion} means: the two amounts grow and shrink together.", 14, gap=8)
    ch.term("proportion", "two amounts that always stay in the same ratio")
    f.p("{b:Example 1 with the same table:} speeds U and V are in the ratio 8 : 3, and U = 5 m/s. "
        "Find V.", 14, gap=6)
    step(f, r"8\text{ parts}\to5", "U is 8 parts", size=19)
    step(f, r"1\text{ part}\to\frac58", "÷ 8", size=19)
    step(f, r"3\text{ parts}\to3\times\frac58=\frac{15}{8}=1.875", "× 3: V = 1.875 m/s", size=19, color=C.GREEN)
    ch.check(3 * sp.Rational(5, 8), sp.Rational(15, 8))
    f.p("The slide does this by \"cross multiplying\" $\\frac{5}{V} = \\frac83$ to get $15 = 8V$. "
        "Same answer; you'll see why that move is allowed in Chapter 15.", 13, C.GREY)


def ugly(ch):
    f = flow(ch)
    sec(f, "Ugly ratios: the lecture's tidy-up trick", room=250)
    f.p("Measured ratios are rarely neat, e.g. 262 : 96.7 : 18.1. To make one easy to read:", 14, gap=6)
    step(f, r"262:96.7:18.1", "the raw ratio", size=19)
    step(f, r"2620:967:181", "1. × 10 to remove the decimals", size=19)
    step(f, r"14.48:5.34:1", "2. ÷ the smallest (181): now it's \"per 1 of the last\"", size=19)
    step(f, r"1448:534:100", "3. × 100 (optional, whole numbers)", size=19, color=C.GREEN)
    ch.check_num(2620 / 181, 14.475, tol=0.01)
    ch.check_num(967 / 181, 5.34, tol=0.01)
    f.p("Step 2 is the useful one: \"14.48 of the first for every 1 of the last\".", 13.5, C.PURPLE)


def beakers(ch):
    f = flow(ch)
    sec(f, "Mixing solutions: beakers", room=440)
    f.p("A \"20% solution of A\" means 20% of the liquid is chemical A and the rest is water. This "
        "percentage is called the {B:concentration} or {B:strength}.", 14, gap=8)
    ch.term("concentration", "how much of a substance is in each amount of mixture, e.g. 20% or 60 g per litre")
    f.p("{B:Lecture 3, Mixing 1:} 50 ml of 20% solution is added to 100 ml of 10% solution. How "
        "strong is the result? {B:Track the A, not the percentages}:", 14, gap=8)
    y = f.reserve(182)
    pg = f.pg
    beaker(pg, L + 30, y + 20, 60, 100, 40, 0.2, "50 ml, 20%")
    pg.text(L + 110, y + 60, "+", 22, C.INK, F.BOLD)
    beaker(pg, L + 150, y + 20, 60, 100, 80, 0.1, "100 ml, 10%")
    pg.text(L + 230, y + 60, "=", 22, C.INK, F.BOLD)
    beaker(pg, L + 270, y + 20, 70, 100, 100, 20 / 150, "150 ml, ?%")
    pg.note(L + 360, y + 10, "A in first: 20% of 50\n= 10 ml\nA in second: 10% of 100\n"
            "= 10 ml\nA in total: 20 ml", C.PURPLE, 15)
    pg.note(L + 30, y + 146, "purple = chemical A, blue = water. (Real chemistry check from the "
            "slides: 100 ml alcohol + 100 ml water gives only about 190 ml!)", C.GREY, 13, w=W - 30)
    step(f, r"\frac{20}{150}\times100=13.\dot3\%", "A over whole, × 100", size=20, color=C.GREEN)
    ch.check(sp.Rational(20, 150) * 100, sp.Rational(40, 3))
    f.p("{R:The tempting wrong answer} is to average: (20 + 10) ÷ 2 = 15%. That ignores that there "
        "is twice as much of the weaker one, so the answer is pulled towards 10%.", 13.5, gap=8)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Recipe cards: your turn", fresh=True)
    f.p("Answers under each group, small and grey. Draw a bar or a table for every one!", 13.5, gap=10)
    f.p("{b:Harder mixtures} (\"how much 15% solution must be added to...?\" and the two-solution "
        "\"compounds\" problems) need an equation with a letter in it. They're solved step by step "
        "in Chapter 15.", 13.5, C.GREY, gap=12)

    groups = [
        ("Percentages", ["Write 35% as a decimal and a fraction", "Write 0.07 as a percentage",
                         "Find 20% of 65", "Find 17.5% of 80", "30% of a number is 12. Find the number"],
         "1. 0.35 = 7/20   2. 7%   3. 13   4. 14   5. 40"),
        ("Up, down and change", ["Increase 250 by 12%", "Decrease 80 by 15%",
                                 "A price falls from £60 to £45. Percentage change?",
                                 "What single multiplier is +20% then -20%?"],
         "6. 280   7. 68   8. -25%   9. 1.2 × 0.8 = 0.96 (a 4% fall)"),
        ("Ratio", ["Simplify 45 : 60", "Share £84 in the ratio 3 : 4", "Squash 2 : 7. 450 ml of drink: how much squash?",
                   "Map scale 1 : 25,000. 4 cm on the map is how many km?"],
         "10. 3 : 4   11. £36 and £48   12. 100 ml   13. 1 km"),
        ("Mixtures", ["200 ml of 30% solution + 300 ml of 5% solution. Strength?"], "14. (60 + 15)/500 = 15%"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14)
    ch.check(sp.Rational(35, 100), sp.Rational(7, 20))
    ch.check(sp.Rational(20, 100) * 65, 13)
    ch.check(sp.Rational(175, 1000) * 80, 14)
    ch.check(12 / sp.Rational(30, 100), 40)
    ch.check(250 * sp.Rational(112, 100), 280)
    ch.check(80 * sp.Rational(85, 100), 68)
    ch.check(sp.Rational(45 - 60, 60) * 100, -25)
    ch.check(sp.Rational(12, 10) * sp.Rational(8, 10), sp.Rational(96, 100))
    ch.check(sp.Rational(84, 7) * 3, 36)
    ch.check(sp.Rational(450, 9) * 2, 100)
    ch.check(4 * 25000, 100000)
    ch.check(sp.Rational(60 + 15, 500) * 100, 15)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    per_cent(ch)
    converting(ch)
    pct_of(ch)
    backwards(ch)
    receipts(ch)
    change(ch)
    mixture_pct(ch)
    ratio_intro(ch)
    scale(ch)
    sharing(ch)
    unitary(ch)
    ugly(ch)
    beakers(ch)
    your_turn(ch)
