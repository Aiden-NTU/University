"""Chapter 38 - Partial differentiation (the ∂ notation from Lecture 14). A hill whose height depends on
two map readings: a coloured height table, a loaf cut into slices (each slice an ordinary curve), a hiker
walking only east or only north on a contour map, the frozen letter drawn inside an ice cube, the chain
rule with a frozen letter, contour spacing as steepness with the uphill arrow, mixed second partials,
and small changes on a can."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, go, mistakes, rule_box, rules_page, section, step, title_block

ORDER = 38
NUM = 38
TITLE = "Partial differentiation"
SHORT = "Partial differentiation"
SLUG = "Partial-Differentiation"
ACCENT = C.BROWN
REQUIRES = ["function", "coordinates", "derivative", "differentiation", "dy-dx-notation", "power-rule",
            "derivative-of-constant", "sum-rule-derivative", "standard-derivatives", "tangent-line", "gradient",
            "second-derivative", "chain-rule", "e-number", "natural-log", "sine", "cosine", "vector",
            "perpendicular-vectors", "area"]
INTRODUCES = ["multivariable-function", "partial-derivative", "partial-notation", "frozen-variable",
              "contour-map", "gradient-vector", "mixed-partials", "small-changes"]

PAPER = "#fcf9f4"
x, y, z, r, h = sp.symbols("x y z r h")
HILL = lambda a, b: 12 - a * a - 2 * b * b
ICE = r"\colorbox[HTML]{D4ECFB}{$\blu{%s}$}"


def icon(pg, x0, y0):
    pg.poly([(x0, y0 + 17), (x0 + 6, y0 + 6), (x0 + 10, y0 + 11), (x0 + 13, y0 + 3), (x0 + 18, y0 + 17)],
            C.BROWN, 1.6, closed=True)
    pg.line(x0 + 11, y0 + 5, x0 + 15, y0 + 5, "#ffffff", 1.2)


def sec(f, t_, **kw):
    section(f, t_, C.BROWN, icon, **kw)


def ice(pg, x0, y0, w, h_):
    pg.rect(x0, y0, w, h_, "#7fb8dc", 1.4, fillcolor="#d4ecfb", r=5)
    pg.line(x0 + 5, y0 + 5, x0 + 12, y0 + 5, "#ffffff", 2)
    pg.line(x0 + 5, y0 + 5, x0 + 5, y0 + 12, "#ffffff", 2)


def shade(v, lo=0, hi=12):
    t_ = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    c0, c1 = (0xfb, 0xf1, 0xe0), (0x9c, 0x5b, 0x2a)
    return "#%02x%02x%02x" % tuple(int(a + (b - a) * t_) for a, b in zip(c0, c1))


def exploded(pg, x0, yb, step_x, step_y, sx, sz, hl=None, labels=True):
    """The hill cut into slices y = -2..2 and pulled apart like a sliced loaf, so no slice hides another."""
    spots = {}
    for k, b in enumerate([-2, -1, 0, 1, 2]):
        ox, oy = x0 + k * step_x, yb - k * step_y
        pts = [(ox + (a_ + 2) * sx, oy - HILL(a_, b) * sz) for a_ in [-2 + 4 * i / 40 for i in range(41)]]
        on = hl is not None and b == hl
        pg.fillpoly(pts + [(ox + 4 * sx, oy), (ox, oy)], "#f4c9a8" if on else "#fbf1e0", 255)
        pg.poly(pts + [(ox + 4 * sx, oy), (ox, oy)], C.RED if on else C.BROWN, 2.2 if on else 1.2, closed=True)
        if labels:
            pg.text(ox, oy + 3, f"y = {b}", 9, C.RED if on else C.GREY, F.BOLD, w=4 * sx, align="center",
                    solid=False)
        spots[b] = (ox, oy)
    return spots


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 38, "Partial differentiation", "one direction at a time", C.BROWN, PAPER)
    sp_ = exploded(pg, L + 10, 350, 62, 26, 13, 9, hl=None, labels=False)
    ox, oy = sp_[-2]
    hx, hy = ox + 3 * 13, oy - HILL(1, -2) * 9
    pg.circle(hx, hy - 16, 4, C.INK, 1.4)
    pg.line(hx, hy - 12, hx, hy - 3, C.INK, 1.6)
    pg.line(hx, hy - 3, hx - 4, hy + 4, C.INK, 1.6)
    pg.line(hx, hy - 3, hx + 4, hy + 4, C.INK, 1.6)
    pg.arrow(hx + 8, hy - 6, hx + 30, hy + 8, C.RED, 1.8, head=7)
    pg.note(L + 340, 210, "a hill is a height that depends on two things: how far east and how far north you "
            "are", C.BROWN, 15, w=R - L - 340)
    f = ch.flow(top=390)
    f.p("Every function so far had one input: put in $x$, get out $y$. Plenty of real things depend on "
        "{B:two} inputs. The height of a hill depends on how far east and how far north you stand; the volume "
        "of a can depends on its radius and its height.", 14, gap=10)
    f.p("You can't ask \"what's the slope?\" of a hill: it depends which way you face. So we ask one "
        "direction at a time, keeping everything else still. That is {B:partial differentiation}.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 14} {y:(the notation slide: \"∂y/∂x is used when the function is made up of "
        "more than one variable\"). Not a lecture of its own, but it builds straight on Chapter 34.}", 12.5)


def two_inputs(ch):
    f = flow(ch)
    sec(f, "Two inputs, one output: a height table", room=520)
    f.p("Take the hill $h = 12 - x^2 - 2y^2$, where $x$ is metres east and $y$ metres north of the summit. "
        "Every pair $(x, y)$ gives one height, so a spreadsheet of heights describes the hill. Darker means "
        "higher:", 14, gap=10)
    y_ = f.reserve(215)
    pg = f.pg
    x0, cw = L + 60, 46
    for j, yy in enumerate([2, 1, 0, -1, -2]):
        pg.text(x0 - 40, y_ + 22 + j * 38, f"y = {yy}", 10, C.GREY, F.BOLD)
        for i, xx in enumerate([-2, -1, 0, 1, 2]):
            v = HILL(xx, yy)
            pg.rect(x0 + i * cw, y_ + 12 + j * 38, cw - 2, 36, C.BROWN, 0.6, fillcolor=shade(v))
            pg.text(x0 + i * cw, y_ + 22 + j * 38, str(v), 12, C.INK if v < 8 else "#ffffff", F.BOLD, w=cw - 2,
                    align="center")
    for i, xx in enumerate([-2, -1, 0, 1, 2]):
        pg.text(x0 + i * cw, y_ + 12 + 5 * 38 + 2, f"x = {xx}", 10, C.GREY, F.BOLD, w=cw, align="center")
    pg.rect(x0 + 3 * cw - 2, y_ + 12 + 38 - 2, cw + 2, 40, C.RED, 2.2)
    pg.note(L + 330, y_ + 10, "the red cell: 1 m east, 1 m north.\nh = 12 − 1 − 2 = 9\n\nwalk along a row "
            "(east): the heights go 9, 10, 9, 6 ... gently.\nwalk up a column (north): 3, 9, 11, 9, 3: steeper.",
            C.INK, 15, w=R - L - 330)
    ch.check([HILL(1, 1), HILL(0, 0), HILL(2, 2)], [9, 12, 0])
    ch.term("function of two variables", "one output from two inputs, like h(x, y): a height for each map position")
    f.p("We write $h(x, y)$: \"h of x and y\". The question for the rest of the chapter: {B:how steep is it} "
        "at the red cell? Answer: it depends which way you walk.", 14)


def loaf(ch):
    f = flow(ch)
    sec(f, "Slice the loaf", room=520)
    f.p("Draw the hill in 3D and it looks like a loaf of bread. Cut it into slices, each at a fixed $y$. "
        "{B:Every slice is an ordinary curve}, with only $x$ changing, and Chapter 34 already knows how to find "
        "the slope of those.", 14, gap=10)
    y_ = f.reserve(228)
    pg = f.pg
    sp_ = exploded(pg, L + 5, y_ + 190, 56, 14, 11, 8, hl=1)
    ox, oy = sp_[-2]
    pg.arrow(ox, oy + 16, ox + 44, oy + 16, C.INK, 1.2, head=5)
    pg.text(ox - 4, oy + 18, "x (east)", 9, C.INK, F.BOLD, solid=False)
    pg.arrow(ox + 50, oy + 18, ox + 50 + 4 * 56, oy + 18 - 4 * 14, C.GREY, 1.0, head=5, dash=(3, 3))
    pg.text(ox + 50 + 4 * 56 - 10, oy + 18 - 4 * 14 - 16, "y (north)", 9, C.GREY, F.BOLD, solid=False)
    hx, hy = sp_[1]
    pg.text(hx - 30, hy - HILL(0, 1) * 8 - 22, "the slice y = 1", 11, C.RED, F.BOLD)
    ax = Axes(pg, L + 320, y_ + 20, 170, 140, (-2.3, 2.3), (0, 12))
    ax.fill_under(lambda v: 10 - v * v, -2, 2, "#f4c9a8")
    ax.axes("x", "h", 1, 5, size=8)
    ax.curve(lambda v: 10 - v * v, -2.2, 2.2, C.RED, 2.2)
    ax.seg(0.2, 9 + 1.6, 1.8, 9 - 1.6, C.INK, 1.4)
    ax.dot(1, 9, C.INK, 3)
    pg.eq(L + 405, y_ + 168, r"h=10-x^2", 14, C.RED, align="center")
    ch.check(sp.expand(HILL(x, 1)), 10 - x ** 2)
    f.p("With $y$ stuck at 1 the formula becomes $h = 12 - x^2 - 2 = 10 - x^2$, a plain one-letter curve. "
        "Its slope is $-2x$, so at $x = 1$ it's $-2$: walking east there, you drop 2 m for every metre.", 14)
    ch.check(sp.diff(10 - x ** 2, x).subs(x, 1), -2)


def ice_cube(ch):
    f = flow(ch)
    sec(f, "Freeze the other letter", room=560)
    rule_box(f, "partial differentiation", [
        "$\\frac{\\partial f}{\\partial x}$: differentiate with respect to $x$ while {B:holding every other letter "
        "constant}. Treat $y$ exactly like a number such as 7.",
        "So a term with no $x$ in it (like $3y^2$) differentiates to {B:0}, and a frozen letter multiplying $x$ "
        "stays as a multiplier: $\\frac{\\partial}{\\partial x}(yx^2)=2xy$.",
        "All the Chapter 34–35 rules (power, chain, product, quotient) still apply, to the moving letter only.",
        "{B:Subscript notation}: $f_x$ means $\\frac{\\partial f}{\\partial x}$ and $f_y$ means "
        "$\\frac{\\partial f}{\\partial y}$.",
    ], C.BROWN)
    f.p("Slicing at $y = 1$ worked, but we'd like a formula for {B:any} slice. So don't put in a number: just "
        "{B:pretend} $y$ is a number. Picture it frozen in an ice cube. It can't move, so it behaves exactly "
        "like the 7 in $7x^2$:", 14, gap=10)
    y_ = f.reserve(120)
    pg = f.pg
    pairs = [(r"7x^2", r"14x", "a number in front stays in front"),
             (ICE % "y" + r"\,x^2", r"2x\," + ICE % "y", "so does a frozen y"),
             (r"7", r"0", "a number alone vanishes"),
             (ICE % "y" + r"^2", r"0", "so does a frozen y on its own")]
    for k, (a, b, why) in enumerate(pairs):
        xx = L + (k % 2) * 252
        yy = y_ + (k // 2) * 58
        pg.rect(xx, yy + 2, 240, 52, C.BROWN, 0.8, fillcolor="#ffffff", r=6)
        pg.eq(xx + 14, yy + 10, a, 17)
        pg.arrow(xx + 80, yy + 22, xx + 112, yy + 22, C.GREY, 1.2, head=5)
        pg.eq(xx + 120, yy + 10, b, 17, C.BROWN)
        pg.text(xx + 6, yy + 38, why, 9.5, C.GREY, F.BOLD, w=228, align="right")
    ice(pg, L + 252 + 214, y_ + 2 + 6, 20, 16)
    f.p("The new notation: a curly $\\partial$ (say \"partial\" or \"del\") instead of $\\dd$, so nobody "
        "forgets that another letter was frozen:", 14, gap=6)
    step(f, r"\frac{\partial h}{\partial x}", "\"partial h by partial x\": slope walking east, y frozen", size=22,
         color=C.BROWN)
    ch.symbol(r"\frac{\partial f}{\partial x}", "partial f by partial x (or del f by del x)",
              "the slope of f when only x changes; every other letter is frozen as a constant")
    ch.symbol(r"f_x,\ f_y", "f sub x, f sub y", "short for ∂f/∂x and ∂f/∂y")
    ch.term("partial derivative", "the derivative with respect to one letter, all the others treated as constants")
    ch.term("frozen variable", "in a partial derivative, every letter except the one you differentiate by acts like a number")
    f.need(200)
    f.p("{b:The hill, both ways.} $h = 12 - x^2 - 2y^2$.", 14, gap=6)
    step(f, r"\frac{\partial h}{\partial x}=0-2x-\underbrace{2" + ICE % "y" + r"^2}_{\text{frozen}\,\to\,0}=-2x",
         "12 → 0 as usual", size=18)
    step(f, r"\frac{\partial h}{\partial y}=0-\underbrace{" + ICE % "x" + r"^2}_{\text{frozen}\,\to\,0}-4y=-4y",
         "now freeze x instead", size=18)
    step(f, r"\text{at }(1,1):\ \ \frac{\partial h}{\partial x}=-2,\qquad\frac{\partial h}{\partial y}=-4",
         "north is twice as steep", size=18, color=C.BROWN)
    ch.check([sp.diff(HILL(x, y), x), sp.diff(HILL(x, y), y)], [-2 * x, -4 * y])
    ch.check([sp.diff(HILL(x, y), x).subs({x: 1, y: 1}), sp.diff(HILL(x, y), y).subs({x: 1, y: 1})], [-2, -4])
    f.p("That matches the height table: the column (north) changed faster than the row (east).", 14)


def examples(ch):
    f = flow(ch)
    sec(f, "Term by term, ice cube by ice cube", room=520)
    f.p("{b:Example.} $f = x^2y + 3y^2 + 5x$. Go through one term at a time, asking \"does this term contain "
        "the moving letter?\"", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    terms = [("x^2y", r"2x\," + ICE % "y", ICE % "x" + r"^2", "x^2 \\to x^2"), ("3y^2", "0", "6y", ""),
             ("5x", "5", "0", "")]
    cols = [L + 10, L + 130, L + 310]
    pg.text(cols[0], y_, "term", 11, C.GREY, F.BOLD)
    pg.text(cols[1], y_, "∂/∂x  (freeze y)", 11, C.BROWN, F.BOLD)
    pg.text(cols[2], y_, "∂/∂y  (freeze x)", 11, C.BROWN, F.BOLD)
    pg.line(L, y_ + 18, R, y_ + 18, C.GREY, 0.8)
    for k, (a, dx_, dy_, _) in enumerate(terms):
        yy = y_ + 26 + k * 38
        pg.eq(cols[0], yy, a, 17)
        pg.eq(cols[1], yy, dx_, 17, C.BROWN)
        pg.eq(cols[2], yy, dy_, 17, C.BROWN)
    step(f, r"\frac{\partial f}{\partial x}=2xy+5,\qquad\frac{\partial f}{\partial y}=x^2+6y", "add the columns",
         size=20, color=C.BROWN)
    F_ = x ** 2 * y + 3 * y ** 2 + 5 * x
    ch.check([sp.diff(F_, x), sp.diff(F_, y)], [2 * x * y + 5, x ** 2 + 6 * y])
    f.need(170)
    f.p("{b:Lecture 14's example,} printed as $y = 2x^2x + 3z$. Here $y$ is the output and the inputs are $x$ "
        "and $z$. As printed, $2x^2x = 2x^3$:", 14, gap=6)
    step(f, r"\frac{\partial y}{\partial x}=6x^2,\qquad\frac{\partial y}{\partial z}=3", "", size=18)
    f.p("If it was meant to be $2x^2z + 3z$ (a more typical example), freeze $z$ for the first and $x$ for "
        "the second:", 14, gap=6)
    step(f, r"\frac{\partial y}{\partial x}=4x\,z,\qquad\frac{\partial y}{\partial z}=2x^2+3", "", size=18)
    ch.check([sp.diff(2 * x ** 3 + 3 * z, x), sp.diff(2 * x ** 3 + 3 * z, z)], [6 * x ** 2, 3])
    ch.check([sp.diff(2 * x ** 2 * z + 3 * z, x), sp.diff(2 * x ** 2 * z + 3 * z, z)], [4 * x * z, 2 * x ** 2 + 3])
    f.need(200)
    f.p("{b:With Chapter 35's rules.} A frozen letter changes nothing about the chain rule. It's just a "
        "number riding along:", 14, gap=6)
    step(f, r"z=e^{2x}\sin y:\quad\frac{\partial z}{\partial x}=2e^{2x}\sin y,\quad\frac{\partial z}{\partial y}"
         r"=e^{2x}\cos y", "sin y or e²ˣ is a constant factor", size=16)
    step(f, r"z=\ln(x^2+y^2):\quad\frac{\partial z}{\partial x}=\frac{2x}{x^2+y^2}", "chain rule: inside's slope ÷ inside",
         size=16)
    Z1 = sp.exp(2 * x) * sp.sin(y)
    ch.check([sp.diff(Z1, x), sp.diff(Z1, y)], [2 * sp.exp(2 * x) * sp.sin(y), sp.exp(2 * x) * sp.cos(y)])
    ch.check(sp.simplify(sp.diff(sp.log(x ** 2 + y ** 2), x) - 2 * x / (x ** 2 + y ** 2)), 0)
    f.need(280)
    rule_box(f, "when the product rule is needed", [
        "Look at the factors of a product. If only {B:one} factor contains the moving letter, the other is a "
        "constant multiplier: no product rule.",
        "If {B:both} factors contain the moving letter, use the product rule $vu'+uv'$, with $'$ meaning "
        "$\\frac{\\partial}{\\partial x}$ (or $\\frac{\\partial}{\\partial y}$).",
    ], C.BROWN)
    f.p("{b:Example.} $z=xe^{xy}$. Both factors, $x$ and $e^{xy}$, contain $x$:", 14, gap=6)
    step(f, r"u=x,\ \ v=e^{xy},\ \ \frac{\partial u}{\partial x}=1,\ \ \frac{\partial v}{\partial x}=y\,e^{xy}",
         "chain: inside xy → y", size=16)
    step(f, r"\frac{\partial z}{\partial x}=e^{xy}\cdot1+x\cdot ye^{xy}=(1+xy)\,e^{xy}", "product rule", size=17,
         color=C.BROWN)
    f.p("Now with respect to $y$: the first factor $x$ is frozen, so it is just a multiplier:", 14, gap=6)
    step(f, r"\frac{\partial z}{\partial y}=x\cdot x\,e^{xy}=x^2e^{xy}", "no product rule; chain: xy → x", size=17,
         color=C.BROWN)
    Zp = x * sp.exp(x * y)
    ch.check(sp.simplify(sp.diff(Zp, x) - (1 + x * y) * sp.exp(x * y)), 0)
    ch.check(sp.diff(Zp, y), x ** 2 * sp.exp(x * y))


def contours(ch):
    f = flow(ch)
    sec(f, "The walker's map: contour lines", room=560)
    f.p("Hikers don't carry 3D models. They carry a {B:contour map}: lines joining points of equal height, "
        "seen from above. For our hill the contours are ovals. Stand at $(1, 1)$, height 9:", 14, gap=10)
    y_ = f.reserve(250)
    pg = f.pg
    ax = Axes(pg, L + 10, y_ + 10, 230, 230, (-3.6, 3.6), (-3.6, 3.6))
    for hv in (0, 3, 6, 9, 11):
        rx, ry = math.sqrt(12 - hv), math.sqrt((12 - hv) / 2)
        ax.param(lambda s, rx=rx: rx * math.cos(s), lambda s, ry=ry: ry * math.sin(s), 0, 2 * math.pi,
                 C.RED if hv == 9 else shade(hv + 3), 1.8 if hv == 9 else 1.6)
        ax.label(rx, 0, f"{{{'r' if hv == 9 else 'n'}:{hv}}}", 8, dx=2, dy=-13)
    ax.axes("x", "y", 0, 0, size=9)
    ax.dot(1, 1, C.INK, 3.5)
    ax.arrow(1, 1, 2.3, 1, C.ORANGE, 2.0, head=7)
    ax.arrow(1, 1, 1, 2.3, C.TEAL, 2.0, head=7)
    ax.arrow(1, 1, 0.55, 0.1, C.GREEN, 2.2, head=7)
    ax.label(2.0, 1, "{O:east}", 9, dx=0, dy=2)
    ax.label(1, 2.3, "{t:north}", 9, dx=4, dy=-6)
    pg.note(L + 260, y_ + 4, "orange: walk east. Slope ∂h/∂x = −2.\nteal: walk north. Slope ∂h/∂y = −4 "
            "(the contours are more tightly packed that way: closer lines = steeper).\n\nthe red oval is height 9, "
            "the one you're standing on (12 − 1² − 2 × 1² = 9). Walk along it and the height doesn't change at all.", C.INK, 15,
            w=R - L - 260)
    ch.term("contour map", "a map with lines joining points of equal height; lines close together = steep")
    f.p("{b:The uphill arrow.} Put the two partial slopes together as a vector (Chapter 32):", 14, gap=6)
    step(f, r"\nabla h=\begin{pmatrix}\partial h/\partial x\\ \partial h/\partial y\end{pmatrix}"
         r"=\begin{pmatrix}-2\\-4\end{pmatrix}\ \text{at }(1,1)", "say \"grad h\"", size=18, color=C.BROWN)
    f.p("This arrow (green, scaled down, on the map) points the {B:steepest way uphill} and cuts "
        "across the contour at a right angle. It points south-west, roughly at the summit, but not exactly: it "
        "leans {B:south} (its $y$-part, −4, is bigger than its $x$-part, −2), because the hill is steeper in "
        "the north–south direction. Its length, "
        "$\\sqrt{(-2)^2 + (-4)^2} = \\sqrt{20} \\approx 4.47$, is how steep that steepest way is.", 14)
    ch.symbol(r"\nabla f", "grad f (or del f)", "the vector of partial derivatives; points the steepest way uphill")
    ch.term("gradient vector", "∇f = (∂f/∂x, ∂f/∂y): points steepest uphill, at right angles to the contours")
    tx, ty = 2, -1
    ch.check((-2) * tx + (-4) * ty, 0)
    ch.check_num(math.hypot(-2, -4), 4.47, 0.005)
    f.need(300)
    f.p("{b:Walking any other way.} Most walks aren't due east or due north. Walk diagonally, and each metre "
        "you go splits into an {O:east part} and a {t:north part}:", 14, gap=8)
    go(f, "From (1, 1) you walk 1 m in a direction that takes you 0.6 m east and 0.8 m north. East drops you "
          "2 per metre, north drops you 4 per metre. Roughly how much height do you lose?")
    y_ = f.reserve(170)
    pg = f.pg
    u = 150
    ox, oy = L + 50, y_ + 136
    for i in range(0, 5):
        pg.line(ox + i * u * 0.2, oy, ox + i * u * 0.2, oy - u * 0.8, "#e3e6ea", 0.6)
        pg.line(ox, oy - i * u * 0.2, ox + u * 0.8, oy - i * u * 0.2, "#e3e6ea", 0.6)
    pg.line(ox, oy, ox + 0.6 * u, oy, C.ORANGE, 2.4)
    pg.line(ox + 0.6 * u, oy, ox + 0.6 * u, oy - 0.8 * u, C.TEAL, 2.4)
    pg.arrow(ox, oy, ox + 0.6 * u, oy - 0.8 * u, C.PURPLE, 2.6, head=8)
    pg.rect(ox + 0.6 * u - 8, oy - 8, 8, 8, C.GREY, 0.8)
    pg.dot(ox, oy, 3.5, C.INK)
    pg.text(ox - 8, oy + 4, "(1, 1)", 10, C.INK, align="right")
    pg.text(ox + 0.3 * u, oy + 6, "0.6 east", 11, C.ORANGE, F.BOLD, align="center")
    pg.text(ox + 0.6 * u + 8, oy - 0.4 * u - 6, "0.8 north", 11, C.TEAL, F.BOLD)
    pg.text(ox + 0.3 * u - 10, oy - 0.4 * u - 24, "1 m", 12, C.PURPLE, F.BOLD, align="right")
    pg.note(L + 230, y_ + 6, "east part:   0.6 × (−2) = −1.2\nnorth part:  0.8 × (−4) = −3.2\n\n"
            "total: about 4.4 lost per metre\nof diagonal walking.", C.INK, 15, w=R - L - 230)
    rate = 0.6 * (-2) + 0.8 * (-4)
    ch.check_num(rate, -4.4, 1e-12)
    hh = lambda X, Y: 12 - X * X - 2 * Y * Y
    ch.check_num((hh(1 + 0.6e-4, 1 + 0.8e-4) - hh(1, 1)) / 1e-4, -4.4, 1e-3)
    f.p("That's the {B:directional slope}: take each partial slope, weight it by how much of your step goes "
        "that way, and add. It's the dot product (Chapter 32) of the uphill arrow with your walking direction: "
        "$(-2)(0.6) + (-4)(0.8) = -4.4$. Walk straight along $\\nabla h$ and you get the steepest possible "
        "climb, 4.47; walk along the contour and you get 0.", 14)
    ch.term("directional derivative", "the slope in any direction: (∂f/∂x)(east part) + (∂f/∂y)(north part), a dot product with ∇f")


def second(ch):
    f = flow(ch)
    sec(f, "Second partials: the mixed ones agree", room=560)
    rule_box(f, "second partial derivatives and their notation", [
        "$\\frac{\\partial^2f}{\\partial x^2}=f_{xx}$: differentiate by $x$ twice.  "
        "$\\frac{\\partial^2f}{\\partial y^2}=f_{yy}$: by $y$ twice.",
        "$\\frac{\\partial^2f}{\\partial y\\,\\partial x}=\\frac{\\partial}{\\partial y}\\Big(\\frac{\\partial f}"
        "{\\partial x}\\Big)$: differentiate by $x$ {B:first}, then by $y$. Read the bottom {B:right to left}.",
        "In subscripts the order reads {B:left to right}: $f_{xy}=(f_x)_y$, $x$ first then $y$. So "
        "$f_{xy}=\\frac{\\partial^2f}{\\partial y\\,\\partial x}$.",
        "For the smooth functions in this course the two mixed partials are equal, so the order never changes "
        "the answer; it is still worth reading the notation correctly.",
    ], C.BROWN)
    f.p("You can differentiate again, in either letter. With $f = x^2y + 3y^2 + 5x$ from before:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    pg.eq(L + 200, y_ + 4, r"f", 20, align="center")
    pg.arrow(L + 190, y_ + 30, L + 110, y_ + 58, C.BROWN, 1.3, head=6)
    pg.arrow(L + 210, y_ + 30, L + 290, y_ + 58, C.BROWN, 1.3, head=6)
    pg.text(L + 100, y_ + 30, "∂/∂x", 10, C.BROWN, F.BOLD)
    pg.text(L + 262, y_ + 30, "∂/∂y", 10, C.BROWN, F.BOLD)
    pg.eq(L + 90, y_ + 62, r"2xy+5", 17, align="center")
    pg.eq(L + 310, y_ + 62, r"x^2+6y", 17, align="center")
    for (x1, x2, lab_, s_, col) in [(L + 70, L + 30, "∂/∂x", "2y", C.INK), (L + 110, L + 180, "∂/∂y", "2x", C.RED),
                                    (L + 290, L + 220, "∂/∂x", "2x", C.RED), (L + 330, L + 380, "∂/∂y", "6", C.INK)]:
        pg.arrow(x1, y_ + 88, x2, y_ + 112, C.BROWN, 1.1, head=5)
        pg.eq(x2, y_ + 116, s_, 17, col, align="center")
    pg.note(L + 400, y_ + 20, "the two middle routes (x then y, y then x) land on the same 2x. They always do "
            "for the smooth functions you'll meet.", C.RED, 14, w=R - L - 400)
    F_ = x ** 2 * y + 3 * y ** 2 + 5 * x
    ch.check([sp.diff(F_, x, 2), sp.diff(F_, x, y), sp.diff(F_, y, x), sp.diff(F_, y, 2)], [2 * y, 2 * x, 2 * x, 6])
    step(f, r"\frac{\partial^2 f}{\partial y\,\partial x}=\frac{\partial^2 f}{\partial x\,\partial y}",
         "mixed partials are equal", size=19, color=C.BROWN)
    ch.term("mixed partial derivatives", "∂²f/∂x∂y: differentiate by one letter then the other; the order doesn't matter")


def small_changes(ch):
    f = flow(ch)
    sec(f, "What partials are for: small changes", room=400)
    f.p("A can's volume is its circle's area times its height: $V = \\pi r^2 h$. A factory makes cans with "
        "$r = 2$ cm and $h = 5$ cm, but the machine drifts: $r$ grows by 0.1 and $h$ shrinks by 0.2. Roughly how "
        "much does the volume change?", 14, gap=10)
    y_ = f.reserve(110)
    pg = f.pg
    cx_, top_ = L + 60, y_ + 12
    pg.ellipse(cx_, top_ + 80, 40, 10, C.BROWN, 1.3, fillcolor="#f4e2cc")
    pg.rect(cx_ - 40, top_, 80, 80, C.BROWN, 0.1, fillcolor="#f4e2cc")
    pg.line(cx_ - 40, top_, cx_ - 40, top_ + 80, C.BROWN, 1.3)
    pg.line(cx_ + 40, top_, cx_ + 40, top_ + 80, C.BROWN, 1.3)
    pg.ellipse(cx_, top_, 40, 10, C.BROWN, 1.3, fillcolor="#fbf1e0")
    pg.line(cx_, top_, cx_ + 40, top_, C.RED, 1.4)
    pg.text(cx_ + 8, top_ - 18, "r", 12, C.RED, F.BOLD)
    pg.line(cx_ + 52, top_, cx_ + 52, top_ + 80, C.TEAL, 1.4)
    pg.text(cx_ + 57, top_ + 30, "h", 12, C.TEAL, F.BOLD)
    pg.note(L + 150, y_ + 6, "Each partial says how sensitive V is to one measurement while the other stays "
            "put. Multiply each by its own nudge and add (the δ's are Lecture 14's \"small increments\"):",
            C.INK, 15, w=R - L - 150)
    step(f, r"\delta V\approx\frac{\partial V}{\partial r}\,\delta r+\frac{\partial V}{\partial h}\,\delta h",
         "", size=20, color=C.BROWN)
    ch.formula(r"\delta z\approx\frac{\partial z}{\partial x}\delta x+\frac{\partial z}{\partial y}\delta y",
               "small changes (two variables)")
    step(f, r"\frac{\partial V}{\partial r}=2\pi rh=20\pi,\qquad\frac{\partial V}{\partial h}=\pi r^2=4\pi",
         "at r = 2, h = 5", size=17)
    step(f, r"\delta V\approx20\pi(0.1)+4\pi(-0.2)=2\pi-0.8\pi=1.2\pi\approx3.77\text{ cm}^3", "", size=17,
         color=C.BROWN)
    Vv = sp.pi * r ** 2 * h
    ch.check([sp.diff(Vv, r).subs({r: 2, h: 5}), sp.diff(Vv, h).subs({r: 2, h: 5})], [20 * sp.pi, 4 * sp.pi])
    ch.check_num(float(1.2 * math.pi), 3.77, 0.005)
    exact = float(Vv.subs({r: 2.1, h: 4.8}) - Vv.subs({r: 2, h: 5}))
    ch.check_num(exact, 3.67, 0.005)
    f.p("Check with the real volumes: $\\pi(2.1^2)(4.8) - \\pi(2^2)(5) \\approx 3.67$. Close, and the smaller "
        "the nudges, the closer it gets.", 14)
    ch.term("small changes formula", "δz ≈ (∂z/∂x)δx + (∂z/∂y)δy: add up each input's effect")


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown", room=420)
    rule_box(f, "a partial derivative with a missing value", [
        "Differentiate with respect to the stated letter, treating the unknown constant ($a$, $k$...) and the "
        "other letters as numbers.",
        "Substitute the given point $(x, y)$.",
        "Set the result equal to the given value and solve for the unknown. Check by substituting back.",
    ], C.BROWN, numbered=True, tag="PROCEDURE")
    k = sp.Symbol("k")
    f.p("{b:Example.} $f=kxy^2+x^3$ has $\\frac{\\partial f}{\\partial y}=8$ at $(1, 2)$. Find $k$.", 14, gap=6)
    step(f, r"\frac{\partial f}{\partial y}=2kxy", "x and k frozen; x³ → 0", size=18)
    step(f, r"2k(1)(2)=8\ \Rightarrow\ 4k=8\ \Rightarrow\ k=2", "at (1, 2)", size=18, color=C.BROWN)
    ch.check(sp.diff(k * x * y ** 2 + x ** 3, y), 2 * k * x * y)
    ch.check(sp.solve(sp.diff(k * x * y ** 2 + x ** 3, y).subs({x: 1, y: 2}) - 8, k), [2])
    f.p("{b:Example.} Where are both slopes of $z=x^2+y^2-4x+6y$ zero (the bottom of the bowl)?", 14, gap=6)
    step(f, r"\frac{\partial z}{\partial x}=2x-4=0\Rightarrow x=2,\qquad\frac{\partial z}{\partial y}=2y+6=0\Rightarrow y=-3",
         "", size=16)
    f.p("Both are zero at $(2, -3)$: the surface is flat in every direction there.", 14)
    Zb = x ** 2 + y ** 2 - 4 * x + 6 * y
    ch.check(sp.solve([sp.diff(Zb, x), sp.diff(Zb, y)], [x, y]), {x: 2, y: -3})
    mistakes(f, [
        (r"\frac{\partial}{\partial x}(3y^2)=6y", r"\frac{\partial}{\partial x}(3y^2)=0", "no x in the term: it is a constant"),
        (r"\frac{\partial}{\partial x}(x^2y)=2x+x^2", r"\frac{\partial}{\partial x}(x^2y)=2xy", "frozen y is a multiplier, not a product"),
    ])


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Partial derivative", r"\frac{\partial f}{\partial x}=f_x", "differentiate by $x$, holding every other "
                                                                       "letter constant"),
        ("Frozen letters", None, "a term with no moving letter → 0; a frozen factor stays as a multiplier"),
        ("Product rule", None, "only when both factors contain the moving letter"),
        ("Second partials", r"f_{xx}=\frac{\partial^2f}{\partial x^2},\qquad f_{xy}=\frac{\partial^2f}{\partial y\,\partial x}",
         "$f_{xy}$: $x$ first, then $y$"),
        ("Mixed partials", r"\frac{\partial^2f}{\partial y\,\partial x}=\frac{\partial^2f}{\partial x\,\partial y}",
         "for smooth functions"),
        ("Gradient vector", r"\nabla f=\begin{pmatrix}f_x\\ f_y\end{pmatrix}", "points steepest uphill"),
        ("Small changes", r"\delta z\approx\frac{\partial z}{\partial x}\delta x+\frac{\partial z}{\partial y}\delta y",
         None),
        ("Find the unknown", None, "differentiate, substitute the point, set equal to the given value, solve"),
    ], C.BROWN)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Freeze, then differentiate. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Freeze the other letter", ["f = x³ + 4xy + y²: find ∂f/∂x and ∂f/∂y", "f = 5x²y³: find ∂f/∂x and ∂f/∂y",
                                     "z = 7y − 3x (careful: very short answers)"],
         "1. 3x² + 4y,  4x + 2y   2. 10xy³,  15x²y²   3. ∂z/∂x = −3,  ∂z/∂y = 7"),
        ("With the chain rule", ["z = sin(3x + 2y)", "z = e^(xy)"],
         "4. 3cos(3x + 2y),  2cos(3x + 2y)   5. y e^(xy),  x e^(xy)"),
        ("The hill h = 12 − x² − 2y²", ["Find both slopes at (2, −1).", "Which way is steeper there, east or north?"],
         "6. ∂h/∂x = −4,  ∂h/∂y = 4   7. equally steep (both size 4); east goes down, north goes up"),
        ("Second partials", ["f = x²y³: check that the two mixed partials agree."],
         "8. both are 6xy²"),
        ("Small changes", ["A rectangle is 10 by 5. Each side grows by 0.1. Estimate the change in area A = xy."],
         "9. δA ≈ 5(0.1) + 10(0.1) = 1.5  (true: 1.51)"),
        ("Product rule and notation", ["z = x e^(xy): find ∂z/∂x and ∂z/∂y.", "z = x² sin(xy): find ∂z/∂x.",
                                       "f = x³y²: find f_x, f_y and f_xy."],
         "10. (1 + xy)e^(xy),  x²e^(xy)   11. 2x sin(xy) + x²y cos(xy)   12. 3x²y²,  2x³y,  6x²y"),
        ("Find the unknown", ["f = ax²y + 3y² and ∂f/∂x = 12 at (1, 2). Find a.",
                              "f = x³ + bxy and ∂f/∂x = 0 at (1, 3). Find b.",
                              "f = e^(kxy) and ∂f/∂x = 6 at (0, 3). Find k.",
                              "z = x² + y² − 6x + 2y: find the point where both partials are zero.",
                              "V = πr²h with r = 2. Find h so that ∂V/∂r = ∂V/∂h."],
         "13. a = 3 (2axy = 4a = 12)   14. b = −1 (3 + 3b = 0)   15. k = 2 (ky e⁰ = 3k = 6)   "
         "16. (3, −1) (2x − 6 = 0, 2y + 2 = 0)   17. h = 1 (2πrh = πr², so 4πh = 4π)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.BROWN, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check([sp.diff(x ** 3 + 4 * x * y + y ** 2, v) for v in (x, y)], [3 * x ** 2 + 4 * y, 4 * x + 2 * y])
    ch.check([sp.diff(5 * x ** 2 * y ** 3, v) for v in (x, y)], [10 * x * y ** 3, 15 * x ** 2 * y ** 2])
    ch.check([sp.diff(7 * y - 3 * x, v) for v in (x, y)], [-3, 7])
    ch.check([sp.diff(sp.sin(3 * x + 2 * y), v) for v in (x, y)], [3 * sp.cos(3 * x + 2 * y), 2 * sp.cos(3 * x + 2 * y)])
    ch.check([sp.diff(sp.exp(x * y), v) for v in (x, y)], [y * sp.exp(x * y), x * sp.exp(x * y)])
    ch.check([sp.diff(HILL(x, y), v).subs({x: 2, y: -1}) for v in (x, y)], [-4, 4])
    ch.check([sp.diff(x ** 2 * y ** 3, x, y), sp.diff(x ** 2 * y ** 3, y, x)], [6 * x * y ** 2, 6 * x * y ** 2])
    ch.check_num(10.1 * 5.1 - 50, 1.51, 1e-9)
    Zp = x * sp.exp(x * y)
    ch.check([sp.simplify(sp.diff(Zp, x) - (1 + x * y) * sp.exp(x * y)), sp.diff(Zp, y)], [0, x ** 2 * sp.exp(x * y)])
    ch.check(sp.diff(x ** 2 * sp.sin(x * y), x), 2 * x * sp.sin(x * y) + x ** 2 * y * sp.cos(x * y))
    F3 = x ** 3 * y ** 2
    ch.check([sp.diff(F3, x), sp.diff(F3, y), sp.diff(F3, x, y)], [3 * x ** 2 * y ** 2, 2 * x ** 3 * y, 6 * x ** 2 * y])
    a, b, k = sp.symbols("a b k")
    ch.check(sp.solve(sp.diff(a * x ** 2 * y + 3 * y ** 2, x).subs({x: 1, y: 2}) - 12, a), [3])
    ch.check(sp.solve(sp.diff(x ** 3 + b * x * y, x).subs({x: 1, y: 3}), b), [-1])
    ch.check(sp.solve(sp.diff(sp.exp(k * x * y), x).subs({x: 0, y: 3}) - 6, k), [2])
    Z16 = x ** 2 + y ** 2 - 6 * x + 2 * y
    ch.check(sp.solve([sp.diff(Z16, x), sp.diff(Z16, y)], [x, y]), {x: 3, y: -1})
    Vv = sp.pi * r ** 2 * h
    ch.check(sp.solve((sp.diff(Vv, r) - sp.diff(Vv, h)).subs(r, 2), h), [1])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    two_inputs(ch)
    loaf(ch)
    ice_cube(ch)
    examples(ch)
    contours(ch)
    second(ch)
    small_changes(ch)
    find_unknown(ch)
    summary(ch)
    your_turn(ch)
