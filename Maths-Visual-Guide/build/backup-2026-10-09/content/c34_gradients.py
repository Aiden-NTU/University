"""Chapter 34 - Gradients of curves (Lecture 14). Zoom in until a curve looks straight; the speedometer
('right now') versus the trip average (chords sliding into a tangent); the lecture's shrinking-h table
for 2x³ − 3x²; the notation phrasebook; the power rule discovered from a table of measured gradients
(the power 'dives' to the front); standard derivatives with the sin → cos wheel; stationary points
with gradient-sign arrows drawn on the curve; the second derivative as a smile or a frown."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import DEPTH, L, R, W, block, blocks, flow, section, step, title_block

ORDER = 34
NUM = 34
TITLE = "Gradients of curves"
SHORT = "Gradients"
SLUG = "Gradients"
ACCENT = C.ORANGE
REQUIRES = ["gradient", "straight-line-equation", "gradient-formula", "function-notation", "index-laws",
            "negative-powers", "fractional-powers", "roots", "quadratic-formula", "graph-of-function",
            "coordinates", "substitution", "e-number", "natural-log", "exponential-function", "sine", "cosine",
            "radian", "greek-letters", "speed-distance-time", "subject-of-formula"]
INTRODUCES = ["tangent-line", "chord", "numerical-gradient", "derivative", "differentiation", "dy-dx-notation",
              "power-rule", "derivative-of-constant", "sum-rule-derivative", "standard-derivatives",
              "rate-of-change", "stationary-point", "turning-point", "maximum-minimum", "point-of-inflection",
              "second-derivative"]

PAPER = "#fffbf5"


def icon(pg, x0, y0):
    pg.poly([(x0 + 1 + i, y0 + 17 - 15 * (i / 17) ** 2) for i in range(18)], C.ORANGE, 1.5)
    pg.line(x0 + 5, y0 + 13, x0 + 17, y0 + 5, C.RED, 1.2)


def sec(f, t_, **kw):
    section(f, t_, C.ORANGE, icon, **kw)


def tseg(ax, fn, dfn, a, half, col, w=1.8, dash=None):
    ax.seg(a - half, fn(a) - dfn(a) * half, a + half, fn(a) + dfn(a) * half, col, w, dash=dash)


def speedo(pg, cx, cy, r_, frac, col=C.RED):
    pg.arc(cx, cy, r_, -30, 210, C.INK, 1.5)
    for k in range(11):
        t = math.radians(210 - k * 24)
        pg.line(cx + (r_ - 6) * math.cos(t), cy - (r_ - 6) * math.sin(t), cx + r_ * math.cos(t),
                cy - r_ * math.sin(t), C.INK, 0.9)
    t = math.radians(210 - frac * 240)
    pg.line(cx, cy, cx + (r_ - 9) * math.cos(t), cy - (r_ - 9) * math.sin(t), col, 2.4)
    pg.dot(cx, cy, 3.5, C.INK)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 34, "Gradients of curves", "zoom in until it's straight", C.ORANGE, PAPER)

    def cy_(t):
        return 335 - 110 * t * t

    pts = [(L + 10 + 290 * i / 100, cy_(i / 100)) for i in range(101)]
    pg.poly(pts, C.ORANGE, 2.6)
    t0 = 0.6
    px, py = L + 10 + 290 * t0, cy_(t0)
    slope = -110 * 2 * t0 / 290
    pg.circle(px, py, 18, C.INK, 1.4)
    pg.line(px + 13, py + 13, px + 30, py + 30, C.INK, 3)
    lx, ly, lr = L + 400, 250, 62
    pg.line(px + 4, py - 18, lx - 20, ly - lr + 3, C.GREY, 0.8, dash=(3, 3))
    pg.line(px + 4, py + 18, lx - 20, ly + lr - 3, C.GREY, 0.8, dash=(3, 3))
    pg.circle(lx, ly, lr, C.INK, 1.6, fillcolor="#ffffff")
    pg.line(lx - 54, ly - 54 * slope, lx + 54, ly + 54 * slope, C.ORANGE, 2.6)
    pg.dot(lx, ly, 3.5, C.RED)
    pg.note(lx - 70, ly + lr + 6, "up close, it's a straight line\n(gradient = its steepness here)",
            C.ORANGE, 14, w=170)
    f = ch.flow(top=380)
    f.p("A straight line has the same steepness everywhere (Chapter 20). A curve doesn't: a road over a "
        "hill gets steeper, levels off at the top, then tips downwards. This chapter answers {B:\"how steep "
        "is it right here?\"}", 14, gap=10)
    f.p("The trick is in the picture: zoom in on any smooth curve and it looks straight, so it has a "
        "gradient at that spot. {B:Differentiation} is the method that finds that gradient for every "
        "point at once. It's the first half of calculus.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 14} {y:(straight-line recap, tangents, approximating the gradient, "
        "differentiation and notation, standard derivatives, stationary points, the second derivative).}", 12.5)


def one_or_many(ch):
    f = flow(ch)
    sec(f, "A line has one gradient; a curve has many", room=460)
    f.p("{b:Recap (Lecture 14):} the line through $(4, 4)$ and $(8, 12)$ goes up 8 while it goes across 4, "
        "so $m = \\frac84 = 2$. Then $4 = 2\\times4 + c$ gives $c = -4$: the line is $y = 2x - 4$.", 14, gap=10)
    ch.check(sp.Rational(12 - 4, 8 - 4), 2)
    ch.check(4 - 2 * 4, -4)
    y_ = f.reserve(206)
    pg = f.pg
    ax = Axes(pg, L + 25, y_ + 8, 185, 150, (0, 9.5), (-1, 14))
    ax.grid(1, 2)
    ax.axes("x", "y", 2, 4, size=8)
    ax.curve(lambda x: 2 * x - 4, 2, 9, C.BLUE, 2.2)
    ax.seg(4, 4, 8, 4, C.ORANGE, 2.0)
    ax.seg(8, 4, 8, 12, C.TEAL, 2.0)
    ax.dot(4, 4, C.INK)
    ax.dot(8, 12, C.INK)
    ax.label(5, 4, "{O:across 4}", 9, dx=0, dy=2)
    ax.label(8, 7, "{T:up 8}", 9, dx=4, dy=-6)
    ax2 = Axes(pg, L + 280, y_ + 8, 185, 150, (0, 3.1), (0, 9.5))
    ax2.grid(1, 1)
    ax2.axes("x", "y", 1, 2, size=8)
    ax2.curve(lambda x: x * x, 0, 3.05, C.ORANGE, 2.4)
    for a in (0.5, 1.5, 2.5):
        tseg(ax2, lambda x: x * x, lambda x: 2 * x, a, 0.45, C.RED)
        ax2.dot(a, a * a, C.RED)
        ax2.label(a, a * a, f"{{R:slope {int(2 * a)}}}", 9, dx=-44, dy=-6)
    pg.rich(L - 5, y_ + 170, "a line: {B:one} gradient everywhere", w=250, size=11.5, align="center")
    pg.rich(L + 250, y_ + 170, "the curve $y = x^2$: a {B:different} gradient at every point", w=250, size=11.5,
            align="center")
    f.p("The gradient of a curve at a point is the gradient of its {B:tangent} there: the straight line "
        "that just touches the curve at that point, heading the same way (the red lines).", 14)
    ch.term("tangent (to a curve)", "the straight line that just touches a curve at one point, going the same way as the curve there")


def zoom(ch):
    f = flow(ch)
    sec(f, "Zoom in until it's straight", room=300)
    f.p("Lecture 14 zooms in on $y = x^2$. Here's the same idea around the point $(1, 1)$:", 14, gap=10)
    y_ = f.reserve(165)
    pg = f.pg
    wins = [((-0.2, 2.2), (-0.3, 4.4), 0.2, 0.4, "×1: clearly curved"),
            ((0.8, 1.2), (0.6, 1.4), 0.02, 0.04, "×10: less curved"),
            ((0.98, 1.02), (0.96, 1.04), None, None, "×100: a straight line, gradient 2")]
    for k, (xr, yr, bx, by, cap) in enumerate(wins):
        x0 = L + k * 177
        pg.rect(x0, y_ + 5, 140, 120, "#cccccc", 0.8)
        ax = Axes(pg, x0, y_ + 5, 140, 120, xr, yr)
        ax.curve(lambda x: x * x, xr[0], xr[1], C.ORANGE, 2.4)
        ax.dot(1, 1, C.RED, 3.2)
        if bx:
            X0, Y0 = ax.P(1 - bx, 1 + by)
            X1, Y1 = ax.P(1 + bx, 1 - by)
            pg.rect(X0, Y0, X1 - X0, Y1 - Y0, C.BLUE, 1.2)
            pg.arrow(X1 + 2, (Y0 + Y1) / 2, x0 + 177 - 4, y_ + 65, C.BLUE, 1.0, head=5, dash=(3, 3))
        pg.text(x0 - 10, y_ + 130, cap, 10.5, C.INK, F.BOLD, w=160, align="center")
    f.p("Lecture 14: \"The slope that we see is 'roughly' correct, but only for that location!\" Zoom in "
        "somewhere else and you'd see a line with a different slope.", 14)


def speedometer(ch):
    f = flow(ch)
    sec(f, "Average speed vs the speedometer", room=480)
    f.p("A trip computer says you averaged 40 mph (60 miles in 1.5 hours). The speedometer says what "
        "you're doing {B:right now}. On a distance–time graph:", 14, gap=6)
    f.p("• the {B:average} is the gradient of a {B:chord}: a straight line joining two points of the curve;\n"
        "• {B:right now} is the gradient of the {B:tangent}.\nTo turn one into the other, slide the second "
        "point closer and closer to the first:", 14, gap=10)
    y_ = f.reserve(200)
    pg = f.pg
    speedo(pg, L + 55, y_ + 80, 45, 0.52)
    pg.text(L + 5, y_ + 130, "right now:\n52 mph", 11, C.RED, F.BOLD, w=100, align="center")
    ax = Axes(pg, L + 150, y_ + 5, 300, 170, (0, 3.3), (0, 10))
    ax.grid(0.5, 1)
    ax.axes("t", "d", 1, 2, size=8)
    ax.curve(lambda t: t * t, 0, 3.15, C.ORANGE, 2.6)
    cols = ["#bdbdbd", "#9e9e9e", "#757575", C.BLUE]
    for b, col in zip((3, 2, 1.5, 1.15), cols):
        m = (b * b - 1) / (b - 1)
        ax.seg(1, 1, b, b * b, col, 1.6)
        ax.dot(b, b * b, col, 3.0)
        ax.label(b, b * b, f"slope {m:g}", 9, col, dx=6, dy=-12)
    ax.curve(lambda t: 2 * t - 1, 0.55, 3.2, C.RED, 1.6, dash=(5, 3))
    ax.dot(1, 1, C.INK, 3.5)
    ax.label(1, 1, "{B:A}", 11, dx=-16, dy=-6)
    ax.label(3.0, 5.0, "{R:tangent: slope 2}", 10, dx=-10, dy=6)
    for b in (3, 2, 1.5, 1.15):
        ch.check_num((b * b - 1) / (b - 1), b + 1)
    f.p("The chord slopes 4, 3, 2.5, 2.15 close in on 2: the speed right now at A.", 14)
    ch.term("chord", "a straight line joining two points on a curve; its gradient is an average rate")


def shrinking_h(ch):
    f = flow(ch)
    sec(f, "Lecture 14's shrinking step", room=300)
    f.p("With numbers: take a small step $h$ along the $x$ axis. The chord from $x = a$ to $x = a + h$ has "
        "gradient rise ÷ run:", 14, gap=6)
    step(f, r"f'(a)\approx\frac{f(a+h)-f(a)}{h}", "rise ÷ run, and the run is h", size=21)
    ch.symbol("h", "h", "a small step along the x axis")
    ch.term("numerical gradient", "(f(a + h) − f(a)) ÷ h for a small h: an estimate of the gradient at x = a")
    f.need(220)
    f.p("{b:Lecture 14:} the gradient of $f(x) = 2x^3 - 3x^2$ at the point $(2, 4)$. (Check the point: "
        "$f(2) = 16 - 12 = 4$ ✓.) Shrink $h$ and watch the last column:", 14, gap=10)
    fx = lambda x: 2 * x ** 3 - 3 * x ** 2
    ch.check(fx(2), 4)
    y_ = f.reserve(150)
    pg = f.pg
    cx_ = [L + 10, L + 100, L + 230, L + 370]
    for x_, h_ in zip(cx_, ["step h", "f(2 + h)", "rise = f(2 + h) − 4", "rise ÷ h"]):
        pg.text(x_, y_, h_, 11, C.ORANGE, F.BOLD)
    pg.line(L, y_ + 17, R, y_ + 17, C.GREY, 0.8)
    rows = []
    for k, h in enumerate([1, 0.1, 0.01, 0.001, 0.00001]):
        v = fx(2 + h)
        rise = v - 4
        g = rise / h
        rows.append(g)
        yy = y_ + 23 + k * 22
        pg.text(cx_[0], yy, f"{h:.5f}".rstrip("0").rstrip("."), 12)
        pg.text(cx_[1], yy, f"{v:.9g}", 12)
        pg.text(cx_[2], yy, f"{rise:.6g}", 12)
        pg.text(cx_[3], yy, f"{g:.6g}", 12, C.RED, F.BOLD)
    pg.arrow(R - 30, y_ + 26, R - 30, y_ + 125, C.RED, 1.6, head=6)
    pg.note(R - 40, y_ + 126, "→ 12", C.RED, 16)
    ch.check_num(rows[0], 23, tol=1e-9)
    ch.check_num(rows[1], 12.92, tol=1e-6)
    ch.check_num(rows[-1], 12.0001, tol=0.0001)
    xs = sp.symbols("x")
    ch.check(sp.diff(2 * xs ** 3 - 3 * xs ** 2, xs).subs(xs, 2), 12)
    f.p("The answers home in on {B:12}. Now imagine $h$ shrinking {B:all the way} to nothing. That's "
        "{B:differentiation}, and Lecture 14 lists its two advantages over the table:", 14, gap=6)
    f.p("1. it gives the gradient at {B:any} point, not just at $x = 2$;\n2. it's {B:exact} (12, not "
        "12.0001).", 14, gap=6, x=L + 14, w=W - 14)
    ch.term("differentiation", "the process of finding the gradient function (derivative) of a function")
    ch.term("derivative", "the gradient function dy/dx: the exact gradient of the curve at every x")


def notation(ch):
    f = flow(ch)
    sec(f, "The phrasebook: how to read the symbols", room=330)
    rows = [(r"\frac{\dd y}{\dd x}", "\"dee y by dee x\": the gradient of y as x changes (the derivative)"),
            (r"f'(x)", "\"f dash of x\" (or \"f prime of x\"): the same thing for a function f"),
            (r"\delta x,\ \delta y", "\"delta x\": a small step in x (δ is small Greek delta). δy is the matching small step in y"),
            (r"\frac{\dd^2y}{\dd x^2}", "\"dee two y by dee x squared\": differentiate twice (later in this chapter)"),
            (r"\frac{\partial y}{\partial x}", "\"partial y by partial x\": when y depends on more than one letter (Chapter 38)")]
    for lat, why in rows:
        w_, h_, _ = f.pg.eq_size(lat, 19)
        y_ = f.reserve(max(h_, 34) + 10)
        pg = f.pg
        pg.eq(L + 10, y_, lat, 19, C.ORANGE)
        pg.note(L + 110, y_ + max(0, h_ / 2 - 12), why, C.INK, 15, w=R - L - 110)
    ch.symbol(r"\frac{dy}{dx}", "dee y by dee x", "the derivative: gradient of y with respect to x")
    ch.symbol(r"f'(x)", "f dash of x", "the derivative of the function f")
    ch.symbol(r"\delta x", "delta x", "a small change in x")
    ch.term("dy/dx notation", "dy/dx is one symbol meaning 'the gradient of y as x changes'; the d's never cancel")
    f.p("{R:Careful:} $\\frac{\\dd y}{\\dd x}$ is {B:one symbol}, not a fraction of $d \\times y$ over "
        "$d \\times x$. You can't cancel the d's.", 14)


def power_rule(ch):
    f = flow(ch)
    sec(f, "Discover the power rule", room=560)
    f.p("Doing the shrinking-step table every time would be exhausting. So let's measure some gradients "
        "(with a tiny $h$, exactly as above) and hunt for a pattern:", 14, gap=10)
    y_ = f.reserve(112)
    pg = f.pg
    cx_ = [L + 10, L + 110, L + 190, L + 270, L + 370]
    for x_, h_ in zip(cx_, ["curve", "at x = 1", "at x = 2", "at x = 3", "pattern?"]):
        pg.text(x_, y_, h_, 11, C.ORANGE, F.BOLD)
    pg.line(L, y_ + 17, R, y_ + 17, C.GREY, 0.8)
    pats = [r"2x", r"3x^2", r"4x^3"]
    for k, n in enumerate((2, 3, 4)):
        yy = y_ + 24 + k * 28
        pg.eq(cx_[0], yy, f"y=x^{n}", 15)
        meas = []
        for j, a in enumerate((1, 2, 3)):
            h = 1e-6
            g = ((a + h) ** n - a ** n) / h
            meas.append(round(g))
            pg.text(cx_[1 + j], yy + 2, f"{round(g)}", 13)
        ch.check(meas, [n * a ** (n - 1) for a in (1, 2, 3)])
        pg.eq(cx_[4], yy, pats[k], 15, C.RED)
    f.p("Look at $x^3$: the gradients 3, 12, 27 are $3\\times1^2$, $3\\times2^2$, $3\\times3^2$. The "
        "power {B:dives to the front}, and what's left has power {B:one smaller}:", 14, gap=10)
    y_ = f.reserve(100)
    pg = f.pg
    pg.eq(L + 40, y_ + 20, r"x^{\red{3}}", 40)
    pg.arrow(L + 110, y_ + 55, L + 180, y_ + 55, C.GREY, 1.6, head=7)
    pg.eq(L + 200, y_ + 20, r"\red{3}\,x^{\blu{2}}", 40)
    pg.arrow(L + 70, y_ + 18, L + 204, y_ + 26, C.RED, 1.4, bend=0.35, head=6)
    pg.note(L + 305, y_ + 8, "the power jumps down in front…", C.RED, 16, w=R - L - 305)
    pg.note(L + 305, y_ + 50, "…and the power goes down by one: 3 − 1 = 2", C.BLUE, 16, w=R - L - 305)
    f.p("If a number is already in front, the diving power multiplies it: $5x^4 \\to 5\\times4\\,x^3 = "
        "20x^3$. In general:", 14, gap=6)
    step(f, r"y=ax^n\quad\Rightarrow\quad\frac{\dd y}{\dd x}=a\,n\,x^{n-1}", "a and n are constants", size=22,
         color=C.ORANGE)
    ch.formula(r"\frac{d}{dx}\left(ax^n\right)=anx^{n-1}", "power rule")
    ch.term("power rule", "the derivative of a xⁿ is a n xⁿ⁻¹: the power comes down in front and drops by one")
    xs = sp.symbols("x")
    ch.check(sp.diff(5 * xs ** 4, xs), 20 * xs ** 3)
    f.p("{b:A constant has gradient 0:} $y = 2$ is a flat line. The rule agrees: $y = 2x^0$ gives "
        "$0\\times2x^{-1} = 0$ (Lecture 14).", 14, gap=6)
    ch.term("derivative of a constant", "zero: a flat line has no slope")
    f.p("{b:Several terms?} Differentiate each one separately and keep the + and − signs.", 14, gap=6)
    ch.term("sum rule (differentiation)", "differentiate a sum or difference term by term")
    for lat, why in [(r"y=x\ \Rightarrow\ \frac{\dd y}{\dd x}=1x^0=1", "x is x¹"),
                     (r"y=2x+3\ \Rightarrow\ \frac{\dd y}{\dd x}=2+0=2", "the +3 just lifts the line"),
                     (r"f(x)=x^3+3x\ \Rightarrow\ f'(x)=3x^2+3", ""),
                     (r"f(z)=3z^3-2z^2+z\ \Rightarrow\ f'(z)=9z^2-4z+1", "any letter works")]:
        step(f, lat, why, size=17)
    z = sp.symbols("z")
    ch.check(sp.diff(xs ** 3 + 3 * xs, xs), 3 * xs ** 2 + 3)
    ch.check(sp.diff(3 * z ** 3 - 2 * z ** 2 + z, z), 9 * z ** 2 - 4 * z + 1)
    f.p("{b:Roots and fractions:} rewrite them as powers first (Chapter 9), then use the rule.", 14, gap=6)
    step(f, r"y=\sqrt[4]{x}=x^{\frac14}", "fourth root = power ¼", size=18)
    step(f, r"\frac{\dd y}{\dd x}=\tfrac14\,x^{\frac14-1}=\tfrac14\,x^{-\frac34}=\frac{1}{4x^{3/4}}",
         "¼ − 1 = −¾", size=18)
    ch.check(sp.diff(xs ** sp.Rational(1, 4), xs), sp.Rational(1, 4) * xs ** sp.Rational(-3, 4))
    step(f, r"y=\frac{1}{x^2}=x^{-2}\ \Rightarrow\ \frac{\dd y}{\dd x}=-2x^{-3}=-\frac{2}{x^3}", "", size=18)
    ch.check(sp.diff(xs ** -2, xs), -2 * xs ** -3)
    f.p("{b:Lecture 14's sneaky one:} $x = \\frac13(y + 2)$. Make $y$ the subject first (Chapter 14): "
        "$y = 3x - 2$, so $\\frac{\\dd y}{\\dd x} = 3$.", 14)


def grow(ch):
    f = flow(ch)
    sec(f, "Why the power rule works: grow a square, grow a cube", room=520)
    f.p("The table found the pattern; a picture shows {B:why}. Think of $y = x^2$ as the {B:area of a square} "
        "with side $x$. Nudge the side up by a tiny amount $h$. How much new area appears?", 14, gap=12)
    X_, H_ = 96, 18
    y_ = f.reserve(X_ + H_ + 62)
    pg = f.pg
    X0, Y0 = L + 50, y_ + 30
    pg.rect(X0, Y0, X_, X_, C.PURPLE, 1.2, fillcolor=C.LIGHT[C.PURPLE])
    pg.eq(X0 + X_ / 2, Y0 + X_ / 2, r"x^2", 17, C.PURPLE, align="center", valign="middle")
    pg.rect(X0 + X_, Y0, H_, X_, C.BLUE, 1.1, fillcolor=C.LIGHT[C.BLUE])
    pg.rect(X0, Y0 + X_, X_, H_, C.BLUE, 1.1, fillcolor=C.LIGHT[C.BLUE])
    pg.rect(X0 + X_, Y0 + X_, H_, H_, C.RED, 1.1, fillcolor=C.LIGHT[C.RED])
    pg.eq(X0 + X_ + H_ / 2, Y0 + X_ / 2, r"xh", 10, C.BLUE, align="center", valign="middle")
    pg.eq(X0 + X_ / 2, Y0 + X_ + H_ / 2, r"xh", 10, C.BLUE, align="center", valign="middle")
    pg.brace(X0, Y0 - 4, X0 + X_, Y0 - 4, C.PURPLE, 1, 5)
    pg.brace(X0 + X_, Y0 - 4, X0 + X_ + H_, Y0 - 4, C.BLUE, 1, 5)
    pg.eq(X0 + X_ / 2, Y0 - 12, "x", 13, C.PURPLE, align="center", valign="baseline")
    pg.eq(X0 + X_ + H_ / 2, Y0 - 12, "h", 13, C.BLUE, align="center", valign="baseline")
    pg.note(X0 + X_ + H_ + 8, Y0 + X_ + 2, "h²: a speck", C.RED, 13)
    pg.note(X0 - 20, Y0 + X_ + H_ + 6, "(h drawn far bigger than it really is)", C.GREY, 12)
    pg.note(L + 250, y_ + 8, "New area = two thin strips (x by h each) plus a tiny corner (h by h).\n\n"
            "Gradient = new area ÷ nudge:", C.INK, 14, w=R - L - 250)
    pg.eq(L + 250, y_ + 88, r"\frac{\blu{2xh}+\red{h^2}}{h}=\blu{2x}+\red{h}", 18)
    pg.note(L + 250, y_ + 140, "shrink h to nothing and only 2x is left", C.GREEN, 14, w=R - L - 250)
    xs, hs = sp.symbols("x h")
    ch.check(sp.expand((xs + hs) ** 2 - xs ** 2), 2 * xs * hs + hs ** 2)
    ch.check(sp.limit(((xs + hs) ** 2 - xs ** 2) / hs, hs, 0), 2 * xs)
    f.p("So the {B:2 in $2x$ is the two strips}: the square grows along two edges. (It's Chapter 11's "
        "$(x+1)^2$ picture with the 1 shrunk down to a tiny $h$.)", 14, gap=12)

    f.p("{b:Now $y = x^3$: the volume of a cube.} Nudge every edge by $h$. The cube grows "
        "the same way in 3D: three thin {B:slabs} ($x$ by $x$ by $h$, one on the top, one on the right, one hidden on "
        "the back), three thin {B:rods} along the edges where slabs meet, and a speck of a cube in the corner:",
        14, gap=10)
    X3, H3 = 70, 14
    y_ = f.reserve(X3 + H3 + 100)
    pg = f.pg
    seg = [(0, X3), (X3, X3 + H3)]
    col_of = {3: C.TEAL, 2: C.PURPLE, 1: C.BLUE, 0: C.RED}
    items = []
    for ix in range(2):
        for iy in range(2):
            for iz in range(2):
                nx = (ix == 0) + (iy == 0) + (iz == 0)
                items.append((seg[ix][0], seg[iy][0], seg[iz][0], seg[ix][1], seg[iy][1], seg[iz][1],
                              col_of[nx], "x^3" if nx == 3 else None, 15))
    ox, oy = L + 40, y_ + X3 + H3 + 50
    blocks(pg, ox, oy, items)
    pg.text(ox + X3 / 2 - 4, oy + 4, "x", 12, C.TEAL, F.BOLD)
    pg.text(ox + X3 + H3 / 2 - 4, oy + 4, "h", 12, C.BLUE, F.BOLD)
    tx = L + 210
    for k, (txt, col) in enumerate([("3 slabs: 3 × x²h", C.PURPLE), ("3 rods: 3 × xh²", C.BLUE),
                                    ("1 speck: h³", C.RED)]):
        pg.text(tx, y_ + 8 + k * 24, txt, 13, col, F.BOLD)
    pg.eq(tx, y_ + 80, r"\frac{\pur{3x^2h}+\blu{3xh^2}+\red{h^3}}{h}=\pur{3x^2}+\blu{3xh}+\red{h^2}", 15)
    pg.note(tx, y_ + 130, "shrink h: the rods and the speck vanish, the slabs stay. Gradient 3x²", C.GREEN, 14,
            w=R - tx)
    ch.check(sp.expand((xs + hs) ** 3 - xs ** 3), 3 * xs ** 2 * hs + 3 * xs * hs ** 2 + hs ** 3)
    ch.check(sp.limit(((xs + hs) ** 3 - xs ** 3) / hs, hs, 0), 3 * xs ** 2)
    f.p("The {B:3 in $3x^2$ is the three slabs}: a cube grows on three faces, and each slab has area $x^2$. "
        "You can't draw $x^4$, but the pattern carries on: $n$ \"slabs\" of size $x^{n-1}$, which is exactly "
        "the power diving down to the front and dropping by one.", 14)


def standard(ch):
    f = flow(ch)
    sec(f, "The standard derivatives", room=470)
    f.p("Lecture 14's list. Learn these like vocabulary: every harder derivative is built from them. "
        "(Angles in radians, Chapter 27.)", 14, gap=10)
    rows = [("c", "0", "flat line"), ("ax^n", "anx^{n-1}", "the power rule"),
            (r"\ln x", r"\tfrac1x", "natural log (Chapter 22)"),
            (r"ae^{kx}", r"ake^{kx}", "e is its own gradient, times k"),
            (r"a\sin(bx)", r"ab\cos(bx)", "see the wheel below"),
            (r"a\cos(bx)", r"-ab\sin(bx)", "note the minus"),
            (r"\tan x", r"\sec^2x", "sec x = 1/cos x")]
    y_ = f.reserve(24 + 34 * len(rows))
    pg = f.pg
    pg.text(L + 20, y_, "function y", 11, C.ORANGE, F.BOLD)
    pg.text(L + 160, y_, "derivative dy/dx", 11, C.ORANGE, F.BOLD)
    pg.line(L, y_ + 17, L + 470, y_ + 17, C.GREY, 0.8)
    for k, (a, b, why) in enumerate(rows):
        yy = y_ + 22 + k * 34
        pg.eq(L + 20, yy, a, 16)
        pg.eq(L + 160, yy, b, 16, C.ORANGE)
        pg.note(L + 300, yy, why, C.GREY, 14, w=R - L - 300)
    xs, a, b, k_, n = sp.symbols("x a b k n")
    ch.check(sp.diff(sp.log(xs), xs), 1 / xs)
    ch.check(sp.diff(a * sp.exp(k_ * xs), xs), a * k_ * sp.exp(k_ * xs))
    ch.check(sp.diff(a * sp.sin(b * xs), xs), a * b * sp.cos(b * xs))
    ch.check(sp.diff(a * sp.cos(b * xs), xs), -a * b * sp.sin(b * xs))
    ch.check(sp.simplify(sp.diff(sp.tan(xs), xs) - 1 / sp.cos(xs) ** 2), 0)
    ch.symbol(r"\sec x", "seck x (secant)", "1 ÷ cos x")
    ch.term("standard derivatives", "the basic list: constants, powers, ln x, e^(kx), sin, cos, tan")
    f.p("{b:The sin–cos wheel.} Differentiating sine and cosine goes round in a circle. Each step "
        "clockwise is one differentiation:", 14, gap=10)
    y_ = f.reserve(170)
    pg = f.pg
    cx, cy, rr = L + 140, y_ + 80, 62
    pg.circle(cx, cy, rr, "#e0c9a6", 1.0, dash=(3, 3))
    spots = [(90, r"\sin x"), (0, r"\cos x"), (270, r"-\sin x"), (180, r"-\cos x")]
    for d, lat in spots:
        X, Y = cx + rr * math.cos(math.radians(d)), cy - rr * math.sin(math.radians(d))
        pg.circle(X, Y, 25, C.ORANGE, 1.2, fillcolor=C.LIGHT[C.ORANGE])
        pg.eq(X, Y - 9, lat, 14, align="center")
    for d0 in (90, 0, -90, -180):
        pg.arc(cx, cy, rr + 4, d0 - 25, d0 - 65, C.RED, 1.4, arrow=True)
    pg.note(L + 260, y_ + 10, "sin → cos → −sin → −cos → back to sin.\n\nFour differentiations bring you "
            "home. (Some functions, like x³, vanish instead: 6x, 6, 0.)", C.INK, 15, w=R - L - 260)
    ch.check(sp.diff(sp.sin(xs), xs, 4), sp.sin(xs))


def rates(ch):
    f = flow(ch)
    sec(f, "Gradients are rates of change", room=260)
    f.p("A gradient is \"how fast one thing changes as another changes\". With time $t$ instead of $x$ you "
        "write $\\frac{\\dd}{\\dd t}$. Lecture 14: velocity $v = 3t^2 + 2$.", 14, gap=6)
    step(f, r"\frac{\dd v}{\dd t}=6t", "power rule; the +2 vanishes", size=19)
    step(f, r"t=3:\quad\frac{\dd v}{\dd t}=6\times3=18", "", size=19, color=C.ORANGE)
    t = sp.symbols("t")
    ch.check(sp.diff(3 * t ** 2 + 2, t).subs(t, 3), 18)
    f.p("How fast velocity changes is {B:acceleration}, so at $t = 3$ the acceleration is 18 (m/s² if "
        "$v$ is in m/s). Likewise, the gradient of distance against time is velocity: the speedometer.", 14)
    ch.term("rate of change", "how fast one quantity changes as another does: the derivative")


def stationary(ch):
    f = flow(ch)
    sec(f, "Stationary points: hilltops, valleys and ledges", room=380)
    f.p("Where the gradient is {B:exactly 0} the tangent is flat: the curve has stopped rising or "
        "falling, for a moment. That's a {B:stationary point}. Lecture 14's gallery:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    gal = [(lambda x: 3 - x * x, (-2, 2), (-1.2, 4), "local maximum (0, 3):\nstationary and turning", True),
           (lambda x: x * x - 3, (-2, 2), (-3.6, 1.6), "local minimum (0, −3):\nstationary and turning", True),
           (lambda x: x ** 3 + 2, (-1.5, 1.5), (-1.6, 5.6), "inflection (0, 2):\nstationary, NOT turning", True),
           (lambda x: abs(x) + 1, (-2, 2), (-0.5, 3.5), "sharp corner (0, 1):\nturning, NOT stationary", False)]
    for k, (fn, xr, yr, cap, flat) in enumerate(gal):
        x0 = L + k * 126
        ax = Axes(pg, x0 + 8, y_ + 5, 100, 90, xr, yr)
        ax.axes(None, None, 0, 0, arrows=False)
        ax.curve(fn, xr[0], xr[1], C.ORANGE, 2.2)
        if flat:
            ax.seg(-0.8, fn(0), 0.8, fn(0), C.RED, 1.6, dash=(4, 3))
        ax.dot(0, fn(0), C.RED, 3.2)
        for i, line_ in enumerate(cap.split("\n")):
            pg.text(x0 - 6, y_ + 104 + i * 14, line_, 9.5, C.INK, F.BOLD if i == 0 else F.SANS, w=130,
                    align="center")
    ch.term("stationary point", "a point where the gradient is zero (the tangent is flat)")
    ch.term("turning point", "where a curve changes from going up to going down, or down to up")
    ch.term("local maximum / minimum", "a hilltop / valley bottom: higher / lower than the points just around it")
    ch.term("point of inflection (stationary)", "a flat 'ledge' where the curve keeps going the same way")
    f.p("{b:Finding them:} differentiate, set the derivative equal to 0, solve. Lecture 14: $y = -x^2 + 3$ "
        "gives $\\frac{\\dd y}{\\dd x} = -2x$, and $-2x = 0$ only when $x = 0$. The stationary point is "
        "$(0, 3)$.", 14, gap=6)
    f.p("{R:Careful with words:} the slide says differentiating finds the curve's \"zeros\". It finds where "
        "the {B:gradient} is zero (stationary points), not where the curve crosses the $x$ axis.", 13.5, gap=10)
    f.p("{b:Lecture 14's big example:} $y = x^3 + 2x^2 + x - 1$. The arrows show the gradient's sign as "
        "you walk left to right:", 14, gap=10)
    fn = lambda x: x ** 3 + 2 * x ** 2 + x - 1
    dfn = lambda x: 3 * x * x + 4 * x + 1
    y_ = f.reserve(200)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 5, 300, 180, (-2.2, 0.8), (-3.2, 1.7))
    ax.grid(0.5, 1)
    ax.axes("x", "y", 1, 1, size=8)
    ax.curve(fn, -2.2, 0.8, C.ORANGE, 2.6)
    for a in (-1.8, -1.4, -1.0, -0.7, -1 / 3, 0.2, 0.55):
        g = dfn(a)
        col = C.GREEN if g > 1e-9 else (C.RED if g < -1e-9 else C.BLUE)
        P1 = ax.P(a, fn(a))
        P2 = ax.P(a + 0.01, fn(a) + g * 0.01)
        dx_, dy_ = P2[0] - P1[0], P2[1] - P1[1]
        nrm = math.hypot(dx_, dy_)
        ux, uy = dx_ / nrm, dy_ / nrm
        ox, oy = uy * 12, -ux * 12
        if oy > 0:
            ox, oy = -ox, -oy
        cx_, cy_ = P1[0] + ox, P1[1] + oy
        pg.arrow(cx_ - ux * 11, cy_ - uy * 11, cx_ + ux * 11, cy_ + uy * 11, col, 1.8, head=5)
        sym = "+" if g > 1e-9 else ("−" if g < -1e-9 else "0")
        pg.text(cx_ + ox * 0.9 - 4, cy_ + oy * 0.9 - 8, sym, 11, col, F.BOLD, solid=False)
    ax.label(-1, -1, "{B:max (−1, −1)}", 10, dx=-60, dy=-64)
    Xm, Ym = ax.P(-1, -1)
    pg.line(Xm - 20, Ym - 48, Xm - 2, Ym - 4, C.BLUE, 0.6)
    ax.label(-1 / 3, fn(-1 / 3), "{B:min (−⅓, −1.15)}", 10, dx=-30, dy=10)
    pg.note(L + 350, y_ + 10, "green +: uphill\nblue 0: flat\nred −: downhill\n\n+ then 0 then −:\na hilltop\n\n"
            "− then 0 then +:\na valley", C.INK, 15, w=R - L - 350)
    step(f, r"\frac{\dd y}{\dd x}=3x^2+4x+1=0", "set the gradient to zero", size=18)
    step(f, r"x=\frac{-4\pm\sqrt{16-12}}{6}=\frac{-4\pm2}{6}", "quadratic formula, a = 3, b = 4, c = 1 (Chapter 15)",
         size=18)
    step(f, r"x=-\tfrac13\quad\text{or}\quad x=-1", "", size=18, color=C.ORANGE)
    xs = sp.symbols("x")
    ch.check(sorted(sp.solve(3 * xs ** 2 + 4 * xs + 1, xs), key=float), [-1, sp.Rational(-1, 3)])
    f.p("{b:Which kind is $x = -1$?} Test the gradient just either side (Lecture 14):", 14, gap=6)
    step(f, r"x=-1.1:\ 3(-1.1)^2+4(-1.1)+1=3.63-4.4+1=0.23", "+  uphill", size=16)
    step(f, r"x=-0.9:\ 3(-0.9)^2+4(-0.9)+1=2.43-3.6+1=-0.17", "−  downhill", size=16)
    ch.check_num(dfn(-1.1), 0.23, tol=1e-9)
    ch.check_num(dfn(-0.9), -0.17, tol=1e-9)
    ch.check(sp.Rational(-1) ** 3 + 2 - 1 - 1, -1)
    ch.check_num(fn(-1 / 3), -1.148, tol=0.001)
    f.p("Uphill, flat, downhill: $x = -1$ is a {B:maximum}, at $y = -1 + 2 - 1 - 1 = -1$.", 14)


def second(ch):
    f = flow(ch)
    sec(f, "The second derivative: smile or frown?", room=440)
    f.p("Differentiate the derivative and you get the {B:second derivative} $\\frac{\\dd^2y}{\\dd x^2}$: how "
        "fast the {B:gradient itself} is changing (Lecture 14).", 14, gap=10)
    y_ = f.reserve(135)
    pg = f.pg
    for k, (sgn, cap, col) in enumerate([(1, "positive: gradient growing\n(−, 0, +) → a valley: minimum", C.GREEN),
                                         (-1, "negative: gradient shrinking\n(+, 0, −) → a hilltop: maximum", C.RED)]):
        cx = L + 90 + k * 250
        cy = y_ + 50
        pg.circle(cx, cy, 44, col, 1.6, fillcolor=C.LIGHT[col])
        pg.dot(cx - 15, cy - 14, 3.5, C.INK)
        pg.dot(cx + 15, cy - 14, 3.5, C.INK)
        mouth = [(cx + t, cy + 16 + sgn * (5 - (t / 22) ** 2 * 10)) for t in range(-22, 23, 2)]
        pg.poly(mouth, C.INK, 2.0)
        for i, line_ in enumerate(cap.split("\n")):
            pg.text(cx - 110, y_ + 100 + i * 15, line_, 11, col if i == 0 else C.INK, F.BOLD, w=220,
                    align="center")
    ch.term("second derivative", "d²y/dx²: the derivative of the derivative; positive at a minimum, negative at a maximum")
    ch.symbol(r"\frac{d^2y}{dx^2}", "dee two y by dee x squared", "the second derivative")
    f.p("Lecture 14 finishes the big example:", 14, gap=6)
    step(f, r"\frac{\dd y}{\dd x}=3x^2+4x+1\quad\Rightarrow\quad\frac{\dd^2y}{\dd x^2}=6x+4", "differentiate again",
         size=17)
    step(f, r"x=-1:\ 6(-1)+4=-2<0", "frown: maximum ✓", size=18)
    step(f, r"x=-\tfrac13:\ 6(-\tfrac13)+4=2>0", "smile: minimum", size=18)
    xs = sp.symbols("x")
    d2 = sp.diff(xs ** 3 + 2 * xs ** 2 + xs - 1, xs, 2)
    ch.check([d2.subs(xs, -1), d2.subs(xs, sp.Rational(-1, 3))], [-2, 2])
    f.p("If the second derivative is {B:zero}, it can't decide (it might be a ledge): go back to the "
        "either-side test.", 14)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Answers in grey. For stationary points, sketch the curve afterwards: does your answer match the picture?",
        13.5, gap=10)
    groups = [
        ("Gradient from scratch", ["Estimate the gradient of y = x² at x = 3 using h = 0.01."],
         "1. (9.0601 − 9) ÷ 0.01 = 6.01 (the exact answer is 6)"),
        ("Power rule", ["y = 5x⁴", "y = 3x² − 7x + 2", "y = √x", "y = 4/x³"],
         "2. 20x³   3. 6x − 7   4. ½x^(−½) = 1/(2√x)   5. −12x⁻⁴ = −12/x⁴"),
        ("Standard derivatives", ["y = 3e^(2x)", "y = 2 sin 5x", "the gradient of y = ln x at x = 4"],
         "6. 6e^(2x)   7. 10 cos 5x   8. 1/4 = 0.25"),
        ("Stationary points", ["y = x² − 6x + 1: find the stationary point and say what kind it is.",
                               "y = x³ − 3x: find both stationary points and classify them with the second derivative."],
         "9. x = 3, y = −8: minimum (second derivative 2 > 0)   10. (1, −2) minimum (6 > 0); (−1, 2) maximum (−6 < 0)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    xs = sp.symbols("x")
    ch.check_num((3.01 ** 2 - 9) / 0.01, 6.01, tol=1e-6)
    ch.check(sp.diff(5 * xs ** 4, xs), 20 * xs ** 3)
    ch.check(sp.diff(3 * xs ** 2 - 7 * xs + 2, xs), 6 * xs - 7)
    ch.check(sp.diff(sp.sqrt(xs), xs), 1 / (2 * sp.sqrt(xs)))
    ch.check(sp.diff(4 / xs ** 3, xs), -12 / xs ** 4)
    ch.check(sp.diff(3 * sp.exp(2 * xs), xs), 6 * sp.exp(2 * xs))
    ch.check(sp.diff(2 * sp.sin(5 * xs), xs), 10 * sp.cos(5 * xs))
    ch.check(sp.diff(sp.log(xs), xs).subs(xs, 4), sp.Rational(1, 4))
    ch.check([sp.solve(2 * xs - 6, xs), (xs ** 2 - 6 * xs + 1).subs(xs, 3)], [[3], -8])
    y3 = xs ** 3 - 3 * xs
    ch.check(sorted(sp.solve(sp.diff(y3, xs), xs), key=float), [-1, 1])
    ch.check([y3.subs(xs, 1), sp.diff(y3, xs, 2).subs(xs, 1), y3.subs(xs, -1), sp.diff(y3, xs, 2).subs(xs, -1)],
             [-2, 6, 2, -6])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    one_or_many(ch)
    zoom(ch)
    speedometer(ch)
    shrinking_h(ch)
    notation(ch)
    power_rule(ch)
    grow(ch)
    standard(ch)
    rates(ch)
    stationary(ch)
    second(ch)
    your_turn(ch)
