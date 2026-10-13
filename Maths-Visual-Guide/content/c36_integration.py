"""Chapter 36 - Integration and areas (Lecture 16). Filling a pool: flow rate × time is an area; the
trapezium rule built from one strip, shared walls counted twice, and 1/2/4/8 strips on x² from 1 to 4
(the error quarters each time); Σ stretching into ∫; integration as the undo button for
differentiation; +C as a family of lifted curves; 1/x and ln|x|; definite integrals (the pool's exact 21);
and area below the axis counting as negative."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import DEPTH, L, R, W, block, flow, go, mistakes, rule_box, rules_page, section, step, title_block

ORDER = 36
NUM = 36
TITLE = "Integration and areas"
SHORT = "Integration"
SLUG = "Integration"
ACCENT = C.BLUE
REQUIRES = ["derivative", "differentiation", "power-rule", "standard-derivatives", "area", "sigma-notation",
            "natural-log", "modulus", "e-number", "sine", "cosine", "normal-distribution", "speed-distance-time",
            "inverse-operations", "negative-numbers", "rate-of-change", "compound-units", "negative-powers",
            "fractional-powers", "expand-brackets", "factorise-quadratic", "solve-equation"]
INTRODUCES = ["integration", "area-under-curve", "trapezium-rule", "strip-width", "integral-sign", "integrand",
              "indefinite-integral", "constant-of-integration", "reverse-power-rule", "integral-of-1-over-x",
              "standard-integrals", "integral-linearity", "definite-integral", "limits-of-integration",
              "negative-area"]

PAPER = "#f7faff"
x = sp.symbols("x")


def icon(pg, x0, y0):
    pg.fillpoly([(x0 + 1, y0 + 17), (x0 + 1, y0 + 10), (x0 + 6, y0 + 7), (x0 + 11, y0 + 5), (x0 + 17, y0 + 2),
                 (x0 + 17, y0 + 17)], C.LIGHT[C.BLUE])
    pg.poly([(x0 + 1, y0 + 10), (x0 + 6, y0 + 7), (x0 + 11, y0 + 5), (x0 + 17, y0 + 2)], C.BLUE, 1.5)
    pg.line(x0 + 1, y0 + 17, x0 + 17, y0 + 17, C.INK, 1)


def sec(f, t_, **kw):
    section(f, t_, C.BLUE, icon, **kw)


def trap(n, a=1.0, b=4.0, fn=lambda v: v * v):
    h = (b - a) / n
    ys = [fn(a + i * h) for i in range(n + 1)]
    return h / 2 * (ys[0] + 2 * sum(ys[1:-1]) + ys[-1])


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 36, "Integration and areas", "add up the tiny pieces", C.BLUE, PAPER)
    ax = Axes(pg, L + 15, 195, 240, 130, (0, 10), (0, 30))
    rate = lambda t: 12 + 10 * math.sin(math.pi * t / 10) + 0.4 * t
    ax.fill_under(rate, 0, 10, C.LIGHT[C.BLUE])
    ax.axes("t", None, 0, 0, size=9)
    ax.curve(rate, 0, 10, C.BLUE, 2.4)
    pg.text(L + 15, 180, "flow rate (litres per minute)", 10, C.GREY, F.BOLD)
    pg.text(L + 70, 290, "area = water", 12, C.BLUE, F.BOLD)
    px, py, pw, ph = L + 320, 230, 160, 90
    pg.rect(px, py + 40, pw, ph - 40, C.BLUE, 0.1, fillcolor=C.LIGHT[C.BLUE])
    pg.poly([(px, py), (px, py + ph), (px + pw, py + ph), (px + pw, py)], C.INK, 1.8)
    pg.poly([(px + 20, py - 36), (px + 20, py - 20), (px + 44, py - 20), (px + 44, py - 8)], "#777777", 5)
    for k in range(3):
        pg.dot(px + 44, py + 4 + k * 12, 2.4, C.BLUE)
    pg.arrow(px - 45, 260, px - 8, 270, C.GREY, 1.2, head=6)
    pg.note(px - 10, py + ph + 6, "the pool holds exactly the\narea under the flow graph", C.BLUE, 14, w=190)
    f = ch.flow(top=375)
    f.p("If water pours in at 20 litres a minute for 5 minutes, the pool gains $20 \\times 5 = 100$ litres. "
        "On a graph of flow rate against time that's a rectangle's {B:area}. When the rate keeps changing, "
        "the water is still the {B:area under the curve}, and finding it is called {B:integration}.", 14, gap=10)
    f.p("It's the second half of calculus, and it turns out to be differentiation run backwards.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 16} {y:(area under a curve, the trapezium rule and its accuracy, the "
        "integral sign, the general formula, +c, 1/x, standard integrals, adding and multiples, definite "
        "integrals, negative areas).}", 12.5)


def pool(ch):
    f = flow(ch)
    sec(f, "Area under a graph = a total", room=420)
    f.p("Rate × time = amount. On a rate–time graph, rate is the height and time is the width, so the "
        "amount is an {B:area}:", 14, gap=10)
    y_ = f.reserve(180)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 10, 180, 130, (0, 6), (0, 25))
    ax.fill_under(lambda t: 20, 0, 5, C.LIGHT[C.BLUE])
    ax.axes("t", None, 1, 5, size=8)
    ax.curve(lambda t: 20, 0, 5, C.BLUE, 2.2)
    ax.vline(5, C.BLUE, 1.2, dash=None, y0=0, y1=20)
    ax.label(1.0, 10, "{B:20 × 5}\n{B:= 100 L}", 11, dx=0, dy=-10)
    pg.text(L, y_ + 152, "steady 20 L/min for 5 min", 11, C.INK, F.BOLD, w=220, align="center")
    ax2 = Axes(pg, L + 280, y_ + 10, 180, 130, (0, 6), (0, 25))
    ax2.fill_under(lambda t: 4 * t, 0, 5, C.LIGHT[C.GREEN])
    ax2.axes("t", None, 1, 5, size=8)
    ax2.curve(lambda t: 4 * t, 0, 5, C.GREEN, 2.2)
    ax2.label(3.1, 4, "{G:½ × 5 × 20}\n{G:= 50 L}", 11, dx=0, dy=-10)
    pg.text(L + 260, y_ + 152, "tap opened steadily: a triangle", 11, C.INK, F.BOLD, w=220, align="center")
    ch.check(sp.Rational(1, 2) * 5 * 20, 50)
    f.p("Rectangles and triangles are easy. A {B:curved} top isn't, which is what the rest of this chapter "
        "is for. Lecture 16's examples of \"area under a curve\" in real life:", 14, gap=6)
    f.p("• a {B:probability}: the area under the Normal curve (Chapter 26)\n• {B:displacement}: the area under "
        "a velocity–time graph\n• {B:drug absorption} (pharmacokinetics): the area under a concentration curve",
        14, x=L + 10, w=W - 10)
    ch.term("area under a curve", "the region between a graph and the x axis; it measures a total (amount, distance, probability)")


def trapezium(ch):
    f = flow(ch)
    sec(f, "Strips with sloping tops: the trapezium rule", room=560)
    f.p("Chop the area into vertical strips of width $h$ and give each strip a straight sloping top. Each "
        "strip is a {B:trapezium} (four sides, two of them parallel). Its area is the {B:average height × "
        "width}:", 14, gap=10)
    y_ = f.reserve(140)
    pg = f.pg
    x0, yb = L + 40, y_ + 120
    pg.fillpoly([(x0, yb), (x0, yb - 55), (x0 + 110, yb - 100), (x0 + 110, yb)], C.LIGHT[C.BLUE])
    pg.poly([(x0, yb), (x0, yb - 55), (x0 + 110, yb - 100), (x0 + 110, yb), (x0, yb)], C.BLUE, 1.6)
    pg.poly([(x0 - 10, yb - 50), (x0 + 30, yb - 62), (x0 + 70, yb - 80), (x0 + 120, yb - 108)], C.ORANGE, 1.6,
            dash=(4, 3))
    pg.text(x0 - 34, yb - 34, "y₀", 12, C.RED, F.BOLD)
    pg.text(x0 + 114, yb - 56, "y₁", 12, C.RED, F.BOLD)
    pg.text(x0 + 40, yb + 4, "h", 12, C.BLUE, F.BOLD)
    pg.text(x0 + 2, y_ - 2, "curve (orange) vs straight top", 9, C.ORANGE)
    pg.eq(L + 230, y_ + 30, r"\text{area}\approx\frac{y_0+y_1}{2}\times h=\frac h2(y_0+y_1)", 19, C.BLUE)
    pg.note(L + 240, y_ + 80, "the straight top misses the curve a little, so this over- or "
            "under-estimates (Lecture 16's \"imperfections\")", C.INK, 14, w=R - L - 240)
    f.p("{b:Lecture 16, one strip:} area under $y = x^2$ from $x = 1$ to $x = 4$, so $h = 3$:", 14, gap=6)
    step(f, r"\text{area}\approx\tfrac32\,(1^2+4^2)=\tfrac32\times17=25.5", "", size=18)
    ch.check_num(trap(1), 25.5)
    f.p("{b:More strips.} With several strips side by side, every {B:inside wall} belongs to two strips "
        "(the right side of one, the left side of the next), so it gets counted {B:twice}:", 14, gap=10)
    y_ = f.reserve(115)
    pg = f.pg
    x0, yb, hw = L + 40, y_ + 100, 70
    heights = [30, 48, 72, 100]
    for i in range(3):
        pts = [(x0 + i * hw, yb), (x0 + i * hw, yb - heights[i]), (x0 + (i + 1) * hw, yb - heights[i + 1]),
               (x0 + (i + 1) * hw, yb)]
        pg.fillpoly(pts, C.LIGHT[C.BLUE] if i % 2 == 0 else "#c7dbf7")
        pg.poly(pts + [pts[0]], C.BLUE, 1.2)
    for i in (1, 2):
        pg.line(x0 + i * hw, yb, x0 + i * hw, yb - heights[i], C.RED, 3)
    for i, lab_ in enumerate(["y₀", "y₁", "y₂", "y₃"]):
        pg.text(x0 + i * hw - 8, yb + 2, lab_, 11, C.RED if i in (1, 2) else C.INK, F.BOLD)
    pg.note(L + 290, y_ + 8, "red walls y₁ and y₂ are shared by two strips, so they appear twice. The two "
            "end walls y₀ and y₃ only once.", C.RED, 15, w=R - L - 290)
    step(f, r"\text{area}\approx\frac h2\big(y_0+2(y_1+y_2+\dots+y_{n-1})+y_n\big)", "", size=19, color=C.BLUE)
    step(f, r"h=\frac{b-a}{n}", "n strips between x = a and x = b", size=18)
    ch.formula(r"\int_a^b y\,dx\approx\frac h2\big(y_0+2(y_1+\dots+y_{n-1})+y_n\big),\ h=\frac{b-a}{n}", "trapezium rule")
    ch.term("trapezium rule", "estimate an area with n sloping-topped strips: h/2 × (first + 2 × middles + last)")
    ch.term("strip width h", "h = (b − a) ÷ n: the width of each strip")
    f.p("{R:Slide slip:} Lecture 16's general formula leaves out the 2 in front of the middle heights. Its own "
        "two-strip example (next page) does use the 2.", 13.5)


def strips(ch):
    f = flow(ch)
    sec(f, "1, 2, 4, 8 strips: watch the error shrink", room=560)
    f.p("Lecture 16's two-strip version: $h = 1.5$, middle height $2.5^2 = 6.25$:", 14, gap=6)
    step(f, r"\tfrac{1.5}{2}\,(1+2\times6.25+16)=0.75\times29.5=22.125", "", size=18)
    ch.check_num(trap(2), 22.125)
    f.p("The true area is 21 (you'll prove it later in this chapter). Keep doubling:", 14, gap=10)
    frames = []
    for n in (1, 2, 4, 8):
        frames.append((n, trap(n)))
    for row in range(2):
        y_ = f.reserve(172)
        pg = f.pg
        for col in range(2):
            n, est = frames[row * 2 + col]
            x0 = L + col * 255
            ax = Axes(pg, x0 + 10, y_ + 5, 220, 125, (0.4, 4.3), (0, 17.5))
            h = 3 / n
            for i in range(n):
                a_, b_ = 1 + i * h, 1 + (i + 1) * h
                pts = [ax.P(a_, 0), ax.P(a_, a_ * a_), ax.P(b_, b_ * b_), ax.P(b_, 0)]
                pg.fillpoly(pts, C.LIGHT[C.BLUE] if i % 2 == 0 else "#c7dbf7")
                pg.poly(pts, C.BLUE, 0.9, closed=True)
            ax.axes(None, None, 1, 0, size=8)
            ax.curve(lambda v: v * v, 0.4, 4.15, C.ORANGE, 2.0)
            err = est - 21
            pg.rich(x0 + 10, y_ + 142, f"{{B:n = {n}}}: {est:g}   {{R:error {err:g}}}", w=240, size=12)
    ch.check([trap(n) for n in (1, 2, 4, 8)], [25.5, 22.125, 21.28125, 21.0703125])
    ch.check([round((trap(n) - 21) / (trap(2 * n) - 21), 6) for n in (1, 2, 4)], [4.0, 4.0, 4.0])
    f.p("Look at the errors: 4.5, 1.125, 0.28, 0.07. For this curve, {B:halving the strip width cuts the "
        "error to exactly a quarter.} For other smooth curves it is only {B:roughly} a quarter, and only once "
        "the strips are fairly narrow; for some curves the pattern is different. What always holds: as the "
        "number of strips heads to infinity, the error heads to 0 (Lecture 16: as $n \\to \\infty$, "
        "$\\varepsilon \\to 0$).", 14)


def integral_sign(ch):
    f = flow(ch)
    sec(f, "Infinitely many strips: the integral sign", room=380)
    f.p("With a finite number of strips you'd write a sum with $\\Sigma$ (Chapter 17). With infinitely many, "
        "infinitely thin strips, the S gets stretched into a new symbol, $\\int$ (a tall S for \"sum\"):", 14,
        gap=12)
    y_ = f.reserve(185)
    pg = f.pg
    x0, y0 = L + 40, y_ + 40
    wi, hi, _ = pg.eq_size(r"\int", 44)
    pg.eq(x0, y0, r"\int", 44)
    pg.eq(x0 + wi - 4, y0 - 12, "b", 18, C.RED, solid=False)
    pg.eq(x0 - 2, y0 + hi - 4, "a", 18, C.RED, solid=False)
    wf, hf, _ = pg.eq_size("f(x)", 30)
    pg.eq(x0 + wi + 14, y0 + hi / 2 - hf / 2, "f(x)", 30, C.BLUE)
    pg.eq(x0 + wi + 22 + wf, y0 + hi / 2 - hf / 2, r"\dd x", 30, C.ORANGE)
    pg.note(L + 250, y_ + 0, "∫ \"the integral of\": add up infinitely many thin strips", C.INK, 15, w=R - L - 250)
    pg.note(L + 250, y_ + 44, "a and b: the limits (where the area starts and stops)", C.RED, 15, w=R - L - 250)
    pg.note(L + 250, y_ + 88, "f(x): the integrand, the height of each strip", C.BLUE, 15, w=R - L - 250)
    pg.note(L + 250, y_ + 126, "dx: the strip width, shrunk to nothing. It also says which letter you're "
            "integrating with.", C.ORANGE, 15, w=R - L - 250)
    ch.symbol(r"\int_a^b f(x)\,dx", "the integral from a to b of f of x, dee x", "the exact area under y = f(x) between x = a and x = b")
    ch.term("integral sign ∫", "a stretched S for 'sum': adds up infinitely many infinitely thin strips")
    ch.term("integrand", "the function being integrated (the strip height)")
    ch.term("limits of integration", "the start and end values of x for a definite integral")
    ch.term("integration", "finding the area under a curve; also the reverse of differentiation")


def undo(ch):
    f = flow(ch)
    sec(f, "Integration is the undo button for differentiation", room=520)
    rule_box(f, "the reverse power rule", [
        "$\\int ax^n\\,\\dd x=\\dfrac{a}{n+1}x^{n+1}+c$: add 1 to the power, then divide by the {B:new} power.",
        "It works for every $n$ {B:except} $n=-1$, which would divide by 0. That case is "
        "$\\int\\frac1x\\,\\dd x=\\ln|x|+c$ (later in this chapter).",
        "A constant: $\\int k\\,\\dd x=kx+c$ (it is $kx^0$, so the power goes up to 1). For example "
        "$\\int5\\,\\dd x=5x+c$.",
        "Every indefinite integral ends with $+c$. Check by differentiating your answer: you must get back "
        "what you started with.",
    ], C.BLUE)
    ch.check(sp.integrate(5, x), 5 * x)
    f.p("Chapter 14's {B:undo button}: every operation has an inverse that takes you back. Integration is "
        "the undo button for differentiation (Lecture 16): it asks {B:\"what did I differentiate to get "
        "this?\"}", 14, gap=6)
    step(f, r"y=5x^3+3\ \xrightarrow{\ \text{differentiate}\ }\ 15x^2\ \xrightarrow{\ \text{integrate}\ }\ 5x^3+\,?",
         "", size=17)
    f.p("The \"+3\" vanished when we differentiated, so undoing can't know what it was. More on that "
        "in a moment. First the rule. Differentiating made the power {B:dive down and drop by one}. "
        "Undo it in reverse order:", 14, gap=10)
    y_ = f.reserve(112)
    pg = f.pg
    pg.eq(L + 30, y_ + 18, r"x^{\red{3}}", 36)
    pg.arrow(L + 95, y_ + 45, L + 160, y_ + 45, C.GREY, 1.6, head=7)
    pg.eq(L + 175, y_ + 10, r"\frac{x^{\blu{4}}}{\blu{4}}", 36)
    pg.note(L + 270, y_ + 2, "1. the power goes UP by one: 3 → 4", C.BLUE, 16, w=R - L - 270)
    pg.note(L + 270, y_ + 44, "2. divide by the NEW power", C.BLUE, 16, w=R - L - 270)
    step(f, r"\int ax^n\,\dd x=\frac{a}{n+1}x^{n+1}+c\qquad(n\neq-1)", "", size=21, color=C.BLUE)
    ch.formula(r"\int ax^n\,dx=\frac{a}{n+1}x^{n+1}+c\ \ (n\ne-1)", "power rule for integration")
    ch.term("reverse power rule", "∫ a xⁿ dx = a xⁿ⁺¹ ÷ (n + 1) + c, for any n except −1")
    f.need(150)
    f.p("{b:Lecture 16:} $\\int 10x^4\\,\\dd x$.", 14, gap=6)
    step(f, r"\int10x^4\,\dd x=\frac{10}{4+1}x^{4+1}+c=2x^5+c", "", size=18)
    step(f, r"\text{check: }\frac{\dd}{\dd x}(2x^5+c)=10x^4\ \checkmark", "always check by differentiating back",
         size=17, color=C.GREEN)
    ch.check(sp.integrate(10 * x ** 4, x), 2 * x ** 5)
    ch.check(sp.diff(2 * x ** 5, x), 10 * x ** 4)


def moving_edge(ch):
    f = flow(ch)
    sec(f, "Why area undoes a gradient: slide the right edge", room=450)
    f.p("Why should {B:area} (adding strips) be the undo of {B:gradient} (Chapter 34)? Fix the left edge at 0 "
        "and let the right edge sit at $x$. Call the shaded area $A(x)$: a number that changes as you slide "
        "the edge. Take $f(t) = t^2$:", 14, gap=6)
    fn = lambda t: t * t
    xv, h = 2.0, 0.45
    go(f, "Slide the right edge a tiny distance h further. What shape is the extra sliver of area, "
          "roughly? How tall is it, and so what's its area?")
    y_ = f.reserve(222)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 16, 250, 150, (0, 3), (0, 7.5))
    ax.fill_under(fn, 0, xv, C.BLUE)
    ax.fill_under(fn, xv, xv + h, C.ORANGE)
    ax.axes("t", None, 0, 0)
    ax.curve(fn, 0, 2.7, C.INK, 2)
    pg.rect(ax.X(xv), ax.Y(fn(xv)), ax.X(xv + h) - ax.X(xv), ax.Y(0) - ax.Y(fn(xv)), C.RED, 1.2, dash=(3, 2))
    ax.label(1.25, 0.9, "{B:A(x)}", 13, dx=0, dy=0)
    pg.text(ax.X(xv), ax.Y(0) + 8, "x", 12, C.BLUE, F.BOLD, align="center")
    pg.brace(ax.X(xv + h), ax.Y(0) + 26, ax.X(xv), ax.Y(0) + 26, C.ORANGE, 1.0, 5)
    pg.text(ax.X(xv + h / 2), ax.Y(0) + 34, "h", 12, C.ORANGE, F.BOLD, align="center")
    pg.arrow(ax.X(xv) - 30, ax.Y(fn(xv)), ax.X(xv) - 3, ax.Y(fn(xv)), C.RED, 1.0, head=4)
    pg.text(ax.X(xv) - 34, ax.Y(fn(xv)) - 8, "f(x)", 12, C.RED, F.BOLD, align="right")
    pg.note(L + 300, y_ + 20, "The new orange sliver is almost a rectangle (red dashes): height f(x), "
            "width h.\n\nSo  extra area ≈ f(x) × h.\n\nThe thinner the sliver, the smaller the curved "
            "error on top.", C.INK, 14, w=R - L - 300)
    f.p("Turn that into a gradient. The {B:rise} of $A$ is the sliver, the {B:run} is $h$:", 14, gap=6)
    step(f, r"A(x+h)-A(x)\approx f(x)\times h", "extra area = the sliver", size=18)
    step(f, r"\frac{A(x+h)-A(x)}{h}\approx f(x)", "÷ h: rise over run", size=18)
    step(f, r"A'(x)=f(x)", "let h shrink to 0 (Chapter 34)", size=21, color=C.GREEN)
    f.p("{B:The rate the area grows is the height of the curve at the moving edge.} So $A$ is a function "
        "whose derivative is $f$: finding area {B:is} undoing differentiation. Check with $f(t) = t^2$: the "
        "reverse power rule says $A(x) = \\frac{x^3}{3}$, and at $x = 2$, with a sliver of width 0.01:",
        14, gap=6)
    A = lambda v: v ** 3 / 3
    step(f, r"\frac{A(2.01)-A(2)}{0.01}=4.02003\approx f(2)=4\ \checkmark", "", size=17)
    ch.check_num((A(2.01) - A(2)) / 0.01, 4.02003, 1e-5)
    ch.check(sp.diff(x ** 3 / 3, x), x ** 2)
    ch.term("area function", "A(x) = area under f from a fixed start up to x; its derivative is f(x)")


def family(ch):
    f = flow(ch)
    sec(f, "+ c: a whole family of answers", room=460)
    f.p("$3x^2$, $3x^2 + 1$ and $3x^2 - 4$ all differentiate to $6x$ (Lecture 16 calls this {B:degenerate}: "
        "many answers). They're the same curve lifted up or down, with exactly the same slope at every $x$:",
        14, gap=10)
    y_ = f.reserve(190)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 5, 210, 165, (-2, 2), (-5.5, 14))
    ax.grid(1, 2)
    ax.axes("x", "y", 1, 0, size=8)
    for c_, col in [(-4, C.GREEN), (-2, "#9e9e9e"), (0, C.BLUE), (1, C.ORANGE), (3, "#9e9e9e"), (5, "#9e9e9e")]:
        ax.curve(lambda v, c_=c_: 3 * v * v + c_, -2, 2, col, 1.8)
        ax.seg(0.7, 3 + c_ - 6 * 0.3, 1.3, 3 + c_ + 6 * 0.3, C.RED, 1.2)
    ax.label(-1.95, 13, "{O:c = 1}", 9, dx=18, dy=-4)
    pg.note(L + 250, y_ + 6, "every curve y = 3x² + c.\nRed: the tangents at x = 1 are parallel\n(all have slope 6).\n\n"
            "So every integral gets a \"+ c\": the constant of integration, meaning \"some number we "
            "don't know yet\".", C.INK, 15, w=R - L - 250)
    ch.check([sp.diff(3 * x ** 2 + c_, x) for c_ in (0, 1, -4)], [6 * x] * 3)
    ch.term("constant of integration (+c)", "the unknown constant added to every indefinite integral")
    ch.term("indefinite integral", "∫ f(x) dx with no limits: a family of functions, + c")
    rule_box(f, "finding c from a point on the curve", [
        "Integrate $\\frac{\\dd y}{\\dd x}$ to get $y=F(x)+c$.",
        "Substitute the given point: its $x$ into $F$, its $y$ on the left.",
        "Solve for $c$.",
        "Write the final equation with that number in place of $c$.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    f.p("{b:Lecture 16:} $\\frac{\\dd y}{\\dd x} = 12x^3$, and $y = 5$ when $x = 1$. The extra fact picks out "
        "one member of the family:", 14, gap=6)
    step(f, r"y=\int12x^3\,\dd x=3x^4+c", "step 1", size=18)
    step(f, r"5=3(1)^4+c\ \Rightarrow\ c=2", "steps 2–3: x = 1, y = 5", size=18)
    step(f, r"y=3x^4+2", "step 4: the specific solution", size=19, color=C.BLUE)
    ch.check(sp.solve(sp.Eq(5, 3 + sp.Symbol("c")), sp.Symbol("c")), [2])
    f.p("{b:Another:} a curve has gradient $3x^2-4$ and passes through $(2, 5)$.", 14, gap=6)
    step(f, r"y=x^3-4x+c", "integrate each term", size=18)
    step(f, r"5=2^3-4(2)+c=0+c\ \Rightarrow\ c=5", "x = 2, y = 5", size=18)
    step(f, r"y=x^3-4x+5", "", size=19, color=C.BLUE)
    cc = sp.Symbol("c")
    ch.check(sp.integrate(3 * x ** 2 - 4, x), x ** 3 - 4 * x)
    ch.check(sp.solve(x ** 3 - 4 * x + cc - 5, cc)[0].subs(x, 2), 5)


def one_over_x(ch):
    f = flow(ch)
    sec(f, "The one exception: 1/x", room=300)
    f.p("Try the rule on $\\int\\frac1x\\,\\dd x = \\int x^{-1}\\,\\dd x$: the power goes up to 0 and you'd divide "
        "by 0. {R:Impossible.} But Chapter 34 showed $\\ln x$ differentiates to $\\frac1x$, so:", 14, gap=6)
    step(f, r"\int\frac1x\,\dd x=\ln|x|+c", "|x|: the size of x, sign removed", size=21, color=C.BLUE)
    ch.check(sp.diff(sp.log(-x), x), 1 / x)
    ch.formula(r"\int\frac1x\,dx=\ln|x|+c", "integral of 1/x")
    ch.term("integral of 1/x", "ln|x| + c: the one power the reverse power rule can't do")
    f.p("{R:Slide slip:} Lecture 16 writes $\\ln x + c$. The modulus matters: $\\frac1x$ exists for negative "
        "$x$ too, but $\\ln$ only accepts positive numbers, so we feed it $|x|$ (Chapter 17's modulus).", 13.5)


def rewrite(ch):
    f = flow(ch)
    sec(f, "Negative and fractional powers: rewrite first", room=520)
    rule_box(f, "integrating anything built from powers of x", [
        "Rewrite every term as $ax^n$: $\\frac{3}{x^2}=3x^{-2}$, $\\sqrt{x}=x^{\\frac12}$, "
        "$\\frac{1}{\\sqrt{x}}=x^{-\\frac12}$, $\\frac{5}{x}=5x^{-1}$. {B:Expand} brackets; {B:split} a fraction "
        "with a single term on the bottom ($\\frac{x^2+1}{x}=x+\\frac1x$).",
        "Integrate term by term: for $n\\neq-1$, add 1 to the power and divide by the new power; a term "
        "$ax^{-1}$ gives $a\\ln|x|$; a constant $k$ gives $kx$.",
        "Add $+c$ and, if you like, turn the powers back into fractions and roots.",
        "Check by differentiating.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    step(f, r"\int\frac{3}{x^2}\,\dd x=\int3x^{-2}\,\dd x=\frac{3x^{-1}}{-1}+c=-\frac{3}{x}+c",
         "−2 + 1 = −1, ÷ (−1)", size=18)
    ch.check(sp.integrate(3 / x ** 2, x), -3 / x)
    step(f, r"\int\sqrt{x}\,\dd x=\int x^{\frac12}\,\dd x=\frac{x^{3/2}}{3/2}+c=\tfrac23x^{\frac32}+c",
         "÷ ³⁄₂ is × ⅔", size=18)
    ch.check(sp.integrate(sp.sqrt(x), x), sp.Rational(2, 3) * x ** sp.Rational(3, 2))
    step(f, r"\int\frac{1}{\sqrt{x}}\,\dd x=\int x^{-\frac12}\,\dd x=\frac{x^{1/2}}{1/2}+c=2\sqrt{x}+c",
         "−½ + 1 = ½", size=18)
    ch.check(sp.integrate(1 / sp.sqrt(x), x), 2 * sp.sqrt(x))
    step(f, r"\int(x+1)^2\,\dd x=\int(x^2+2x+1)\,\dd x=\frac{x^3}{3}+x^2+x+c", "expand first", size=18)
    ch.check(sp.integrate(sp.expand((x + 1) ** 2), x), x ** 3 / 3 + x ** 2 + x)
    step(f, r"\int\frac{x^2+1}{x}\,\dd x=\int\Big(x+\frac1x\Big)\dd x=\frac{x^2}{2}+\ln|x|+c", "split, then 1/x → ln",
         size=18)
    ch.check(sp.integrate(sp.expand((x ** 2 + 1) / x), x), x ** 2 / 2 + sp.log(x))
    mistakes(f, [
        (r"\int\frac{3}{x^2}\,\dd x=\frac{3}{x^3/3}", r"\int3x^{-2}\,\dd x=-3x^{-1}+c", "rewrite as a power; never integrate the bottom on its own"),
        (r"\int(2x+1)^2\,\dd x=\frac{(2x+1)^3}{3}", r"\int(4x^2+4x+1)\,\dd x", "expand first: the answer is ⁴⁄₃x³ + 2x² + x + c (Chapter 37 has a shortcut)"),
        (r"\int x^{-1}\,\dd x=\frac{x^0}{0}", r"\int x^{-1}\,\dd x=\ln|x|+c", "n = −1 is the one exception"),
    ])
    ch.check(sp.integrate(4 * x ** 2 + 4 * x + 1, x), sp.Rational(4, 3) * x ** 3 + 2 * x ** 2 + x)
    ch.check(sp.simplify(sp.diff((2 * x + 1) ** 3 / 6, x) - (2 * x + 1) ** 2), 0)


def standard_list(ch):
    f = flow(ch)
    sec(f, "Standard integrals and the easy rules", room=520)
    rule_box(f, "standard integrals", [
        "Each one is a derivative from Chapter 34 read backwards. Add $+c$ to every indefinite integral.",
        "{B:Sums and differences}: integrate term by term. {B:A number in front} waits outside: "
        "$\\int kf(x)\\,\\dd x=k\\int f(x)\\,\\dd x$.",
        "{R:Products and quotients have no such rule}: expand or split them first (previous section), or use "
        "Chapter 37's methods.",
    ], C.BLUE)
    f.p("Lecture 16's list (angles in radians):", 14, gap=10)
    rows = [("k", "kx"), ("x", r"\tfrac12x^2"), ("x^n", r"\tfrac{1}{n+1}x^{n+1}"), (r"\tfrac1x", r"\ln|x|"),
            ("e^x", "e^x"), ("e^{kx}", r"\tfrac1ke^{kx}"), (r"\sin x", r"-\cos x"), (r"\cos x", r"\sin x"),
            (r"\sin kx", r"-\tfrac1k\cos kx"), (r"\cos kx", r"\tfrac1k\sin kx"), (r"\tan x", r"\ln|\sec x|")]
    per = (len(rows) + 1) // 2
    y_ = f.reserve(22 + 28 * per)
    pg = f.pg
    for c in range(2):
        pg.text(L + 10 + c * 250, y_, "function", 11, C.BLUE, F.BOLD)
        pg.text(L + 110 + c * 250, y_, "integral", 11, C.BLUE, F.BOLD)
    pg.line(L, y_ + 17, R, y_ + 17, C.GREY, 0.8)
    for k, (a, b) in enumerate(rows):
        c, r_ = k // per, k % per
        yy = y_ + 22 + r_ * 28
        pg.eq(L + 10 + c * 250, yy, a, 15)
        pg.eq(L + 110 + c * 250, yy, b, 15, C.BLUE)
    kk = sp.symbols("k", positive=True)
    for fx, Fx in [(sp.exp(kk * x), sp.exp(kk * x) / kk), (sp.sin(kk * x), -sp.cos(kk * x) / kk),
                   (sp.cos(kk * x), sp.sin(kk * x) / kk)]:
        ch.check(sp.simplify(sp.diff(Fx, x) - fx), 0)
    ch.check(sp.simplify(sp.diff(sp.log(1 / sp.cos(x)), x) - sp.tan(x)), 0)
    f.p("{b:About $\\tan x$.} Lectures 16 and 17 list $\\int\\tan x\\,\\dd x=\\ln(\\sec x)+c$, where "
        "$\\sec x=\\frac{1}{\\cos x}$. As with $\\frac1x$, write $\\ln|\\sec x|$ so that it also works where "
        "$\\cos x$ is negative. (Check: by the chain rule, $\\ln(\\sec x)$ differentiates to "
        "$\\frac{\\sec x\\tan x}{\\sec x}=\\tan x$.)", 13.5, gap=10)
    ch.term("standard integrals", "the basic list: k, powers, 1/x, e^(kx), sin kx, cos kx, tan x")
    f.p("{b:The easy rules (Lecture 16).} Integrate a sum or difference term by term, and pull constant "
        "multiples out front. All the separate $c$'s merge into one:", 14, gap=6)
    step(f, r"\int(x^2+x^3)\,\dd x=\frac{x^3}{3}+\frac{x^4}{4}+c", "term by term", size=17)
    step(f, r"\int3x^4\,\dd x=3\int x^4\,\dd x=\frac{3x^5}{5}+c", "the 3 waits outside", size=17)
    ch.term("linearity of integration", "∫(f ± g) = ∫f ± ∫g and ∫k f = k ∫f")
    f.need(130)
    f.p("{b:Lecture 16's example:} $\\int(4x - 2x^2 + 8)\\,\\dd x$.", 14, gap=6)
    step(f, r"=\frac{4x^2}{2}-\frac{2x^3}{3}+8x+c=2x^2-\frac{2x^3}{3}+8x+c", "each term: power up, ÷ new power",
         size=17, color=C.BLUE)
    ch.check(sp.integrate(4 * x - 2 * x ** 2 + 8, x), 2 * x ** 2 - sp.Rational(2, 3) * x ** 3 + 8 * x)


def definite(ch):
    f = flow(ch)
    sec(f, "Definite integrals: top minus bottom", room=480)
    rule_box(f, "evaluating a definite integral", [
        "Integrate (rewrite first if needed) and write the result in square brackets with the limits: "
        "$\\big[F(x)\\big]_a^b$. Leave out the $+c$: it would cancel.",
        "Substitute the {B:top} limit $b$: $F(b)$.",
        "Substitute the {B:bottom} limit $a$: $F(a)$. Use brackets; negative limits cause most mistakes.",
        "Subtract: $F(b)-F(a)$. The answer is a number (a signed area), not a formula.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    f.p("The square brackets mean \"this, evaluated at the top minus at the bottom\":", 14, gap=6)
    step(f, r"\int_a^b f(x)\,\dd x=\Big[F(x)\Big]_a^b=F(b)-F(a)", "F is any integral of f", size=20,
         color=C.BLUE)
    ch.formula(r"\int_a^bf(x)\,dx=F(b)-F(a)", "definite integral")
    ch.term("definite integral", "∫ from a to b: a number, F(b) − F(a), the (signed) area between x = a and x = b")
    f.p("{b:The pool's exact answer:} the area under $x^2$ from 1 to 4, which the strips were chasing:", 14, gap=6)
    step(f, r"\int_1^4x^2\,\dd x=\Big[\frac{x^3}{3}\Big]_1^4=\frac{64}{3}-\frac13=\frac{63}{3}=21", "✓ the strips' target",
         size=18, color=C.BLUE)
    ch.check(sp.integrate(x ** 2, (x, 1, 4)), 21)
    f.p("{b:Lecture 16:} $\\int_1^3 2x^5\\,\\dd x$.", 14, gap=6)
    step(f, r"=2\Big[\frac{x^6}{6}\Big]_1^3=\Big[\frac{x^6}{3}\Big]_1^3=\frac{729}{3}-\frac13=243-\tfrac13=242.\dot6",
         "", size=17)
    ch.check(sp.integrate(2 * x ** 5, (x, 1, 3)), sp.Rational(728, 3))
    f.p("{b:Lecture 16's your turn:} $\\int_{-1}^{1}(3x^2 + 7)\\,\\dd x$.", 14, gap=6)
    step(f, r"=\Big[x^3+7x\Big]_{-1}^{1}=(1+7)-(-1-7)=8+8=16", "careful with the minus signs", size=17)
    ch.check(sp.integrate(3 * x ** 2 + 7, (x, -1, 1)), 16)
    f.p("{R:Slide slip:} Lecture 16's general limits formula ends with $\\frac{a}{n+1}(b^{n+1} - c^{n+1})$ "
        "for limits $b$ (bottom) to $c$ (top). It's the other way round: top minus bottom, "
        "$\\frac{a}{n+1}(c^{n+1} - b^{n+1})$, as its own line above it says.", 13.5)


def shapes(ch):
    f = flow(ch)
    sec(f, "Where the ÷2 and ÷3 come from: a triangle and a pyramid", room=520)
    f.p("The rule \"power up by one, divide by the new power\" can be checked with shapes you already know. "
        "{b:Area under $y = x$ from 0 to $a$:} the strips build a triangle, and a triangle is {B:half} of "
        "the $a$ by $a$ square:", 14, gap=10)
    S = 110
    y_ = f.reserve(S + 44)
    pg = f.pg
    x0, y0 = L + 50, y_ + 10
    pg.rect(x0, y0, S, S, C.GREY, 1.0, dash=(4, 3))
    pg.fillpoly([(x0, y0 + S), (x0 + S, y0 + S), (x0 + S, y0)], C.LIGHT[C.BLUE], outline=C.BLUE, width=1.3)
    for k in range(1, 8):
        xx = x0 + S * k / 8
        pg.line(xx, y0 + S, xx, y0 + S - S * k / 8, C.BLUE, 0.5)
    pg.line(x0, y0 + S, x0 + S + 12, y0 + S - S - 12, C.BLUE, 1.6)
    pg.text(x0 + S + 14, y0 - 20, "y = x", 12, C.BLUE, F.BOLD)
    pg.text(x0 + S / 2 - 4, y0 + S + 4, "a", 12, C.INK, F.BOLD)
    pg.text(x0 - 14, y0 + S / 2 - 8, "a", 12, C.INK, F.BOLD)
    pg.note(x0 + 6, y0 + 8, "the other half\nof the square", C.GREY, 12)
    pg.note(L + 250, y_ + 6, "triangle = half of a × a:", C.INK, 14, w=R - L - 250)
    pg.eq(L + 250, y_ + 34, r"\int_0^a x\,\dd x=\left[\frac{x^2}{\red 2}\right]_0^a=\frac{a^2}{\red 2}", 18)
    pg.note(L + 250, y_ + 90, "the ÷2 IS the half", C.RED, 15, w=R - L - 250)
    xs, aa = sp.symbols("x a", positive=True)
    ch.check(sp.integrate(xs, (xs, 0, aa)), aa ** 2 / 2)

    f.p("{b:Area under $y = x^2$ from 0 to $a$.} Each strip is $x^2$ tall and $\\dd x$ wide. Now turn "
        "every strip into a {B:square slab}: $x$ by $x$, and $\\dd x$ thick (same number, $x^2\\,\\dd x$). "
        "Stack the slabs, biggest at the bottom, and they build a {B:pyramid} with an $a$ by $a$ base and "
        "height $a$:", 14, gap=10)
    A_ = 120
    y_ = f.reserve(A_ + DEPTH * A_ + 52)
    pg = f.pg
    ox, oy = L + 40, y_ + A_ + DEPTH * A_ + 16
    block(pg, ox, oy, 0, 0, 0, A_, A_, A_, C.GREY, dashed=True)
    n = 8
    for k in range(n):
        side = A_ * (n - k) / n
        block(pg, ox, oy, 0, A_ * k / n, A_ - side, side, A_ * (k + 1) / n, A_, C.PURPLE)
    pg.note(ox, oy + 2, "dashed: the whole a × a × a cube", C.GREY, 12)
    tx = L + 260
    pg.note(tx, y_ + 4, "Three of these pyramids fit together to fill the whole cube (a famous fact, "
            "known to Euclid). So the pyramid is a THIRD of a³:", C.INK, 14, w=R - tx)
    pg.eq(tx, y_ + 80, r"\int_0^a x^2\,\dd x=\left[\frac{x^3}{\red 3}\right]_0^a=\frac{a^3}{\red 3}", 18)
    pg.note(tx, y_ + 136, "the ÷3 IS the third", C.RED, 15, w=R - tx)
    ch.check(sp.integrate(xs ** 2, (xs, 0, aa)), aa ** 3 / 3)
    fr = [sum(k * k for k in range(1, m + 1)) / m ** 3 for m in (8, 100, 10000)]
    ch.check([round(v, 3) for v in fr], [0.398, 0.338, 0.333])
    f.p("With 8 chunky slabs the staircase is a bit more than a third (0.398 of the cube); with 100 thin "
        "ones it's 0.338; with infinitely thin ones, exactly $\\frac13$. That's the integral doing its job. "
        "The pattern continues past what we can draw: $\\int x^3\\,\\dd x$ is a 4D pyramid, a quarter "
        "of a 4D cube, $\\frac{x^4}{4}$.", 14)


def negative(ch):
    f = flow(ch)
    sec(f, "Area below the axis counts as negative", room=480)
    rule_box(f, "areas that cross the axis", [
        "A definite integral counts area {B:above} the $x$-axis as positive and area {B:below} it as negative, "
        "so pieces on opposite sides cancel.",
        "To find the {B:total area} between a curve and the axis: solve $f(x)=0$ to find where the curve "
        "crosses the axis between the limits.",
        "Integrate over each piece separately (limit to crossing, crossing to crossing, crossing to limit).",
        "Add the {B:sizes} of the pieces (ignore their minus signs).",
    ], C.BLUE)
    f.p("Lecture 16: $\\int_{-2}^{2}x^3\\,\\dd x = \\Big[\\frac{x^4}{4}\\Big]_{-2}^{2} = \\frac{16}{4} - "
        "\\frac{16}{4} = 0$. Zero area? Look at the picture:", 14, gap=10)
    y_ = f.reserve(185)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 5, 250, 170, (-2.3, 2.3), (-9, 9))
    ax.fill_under(lambda v: v ** 3, 0, 2, C.LIGHT[C.BLUE])
    ax.fill_under(lambda v: v ** 3, -2, 0, C.LIGHT[C.RED])
    ax.grid(1, 2)
    ax.axes("x", "y", 1, 4, size=8)
    ax.curve(lambda v: v ** 3, -2.1, 2.1, C.INK, 2.2)
    ax.label(1.35, 2.2, "{B:+4}", 13, dx=0, dy=-8)
    ax.label(-1.75, -2.2, "{R:−4}", 13, dx=0, dy=-8)
    pg.note(L + 290, y_ + 10, "Area above the axis counts +, area below counts −. Here they cancel exactly.\n\n"
            "If you want the total shaded area, split at the crossing and add the sizes: 4 + 4 = 8.",
            C.INK, 15, w=R - L - 290)
    ch.check([sp.integrate(x ** 3, (x, 0, 2)), sp.integrate(x ** 3, (x, -2, 0)), sp.integrate(x ** 3, (x, -2, 2))],
             [4, -4, 0])
    ch.term("negative area", "area below the x axis comes out negative in a definite integral")
    f.p("{R:Take care interpreting them} (Lecture 16): a velocity graph dipping below the axis means going "
        "backwards, and the integral gives your net displacement (Chapter 32), not the distance run.", 14,
        gap=10)
    f.need(330)
    f.p("{b:Worked example: the crossing point isn't given.} Find the total area between $y=x^2-x-2$ and the "
        "$x$-axis from $x=0$ to $x=3$.", 14, gap=6)
    step(f, r"x^2-x-2=0\ \Rightarrow\ (x-2)(x+1)=0\ \Rightarrow\ x=2\ \text{or}\ x=-1", "solve f(x) = 0",
         size=17)
    f.p("Only $x=2$ lies between 0 and 3, so split there. Let $F(x)=\\frac{x^3}{3}-\\frac{x^2}{2}-2x$:", 13.5, gap=6)
    step(f, r"\int_0^2f(x)\,\dd x=F(2)-F(0)=\Big(\tfrac83-2-4\Big)-0=-\tfrac{10}{3}", "below the axis", size=17)
    step(f, r"\int_2^3f(x)\,\dd x=F(3)-F(2)", "above the axis", size=17)
    step(f, r"=\Big(9-\tfrac92-6\Big)-\Big(-\tfrac{10}{3}\Big)=-\tfrac32+\tfrac{10}{3}=\tfrac{11}{6}", "", size=17)
    step(f, r"\text{total area}=\tfrac{10}{3}+\tfrac{11}{6}=\tfrac{31}{6}\approx5.17", "add the sizes", size=18,
         color=C.BLUE)
    fx = x ** 2 - x - 2
    ch.check(sp.solve(fx, x), [-1, 2])
    ch.check([sp.integrate(fx, (x, 0, 2)), sp.integrate(fx, (x, 2, 3))], [-sp.Rational(10, 3), sp.Rational(11, 6)])
    ch.check(abs(sp.integrate(fx, (x, 0, 2))) + abs(sp.integrate(fx, (x, 2, 3))), sp.Rational(31, 6))
    f.p("Integrating straight from 0 to 3 would give $-\\frac{10}{3}+\\frac{11}{6}=-\\frac32$: not an area at "
        "all.", 13.5)
    ch.check(sp.integrate(fx, (x, 0, 3)), -sp.Rational(3, 2))


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown", room=380)
    rule_box(f, "an integral with a missing value", [
        "Do the integral with the unknown letter ($k$, $a$...) treated as a number, exactly as usual.",
        "Set the result equal to the value you are given. This gives an equation in the unknown.",
        "Solve it. If you get two answers, keep only the one that fits the question (e.g. $k>1$).",
        "Check by putting your answer back into the integral.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    k, a = sp.symbols("k a")
    f.p("{b:Unknown limit:} $\\int_1^k2x\\,\\dd x=8$ with $k>1$. Find $k$.", 14, gap=6)
    step(f, r"\Big[x^2\Big]_1^k=k^2-1", "integrate, top minus bottom", size=18)
    step(f, r"k^2-1=8\ \Rightarrow\ k^2=9\ \Rightarrow\ k=3", "k = −3 is ruled out by k > 1", size=18, color=C.BLUE)
    ch.check(sp.integrate(2 * x, (x, 1, k)), k ** 2 - 1)
    ch.check([s for s in sp.solve(k ** 2 - 1 - 8, k) if s > 1], [3])
    f.p("{b:Unknown constant:} $\\int_0^2(ax+1)\\,\\dd x=10$. Find $a$.", 14, gap=6)
    step(f, r"\Big[\tfrac{a}{2}x^2+x\Big]_0^2=2a+2", "a is just a number", size=18)
    step(f, r"2a+2=10\ \Rightarrow\ a=4", "", size=18, color=C.BLUE)
    ch.check(sp.integrate(a * x + 1, (x, 0, 2)), 2 * a + 2)
    ch.check(sp.solve(2 * a + 2 - 10, a), [4])
    f.p("{b:Unknown $c$ with a negative power:} $\\frac{\\dd y}{\\dd x}=4x-\\frac{3}{x^2}$, and the curve passes "
        "through $(1, 6)$.", 14, gap=6)
    step(f, r"y=\int\big(4x-3x^{-2}\big)\,\dd x=2x^2+3x^{-1}+c=2x^2+\frac3x+c", "rewrite first", size=18)
    step(f, r"6=2+3+c\ \Rightarrow\ c=1", "x = 1, y = 6", size=18)
    step(f, r"y=2x^2+\frac3x+1", "", size=19, color=C.BLUE)
    ch.check(sp.integrate(4 * x - 3 / x ** 2, x), 2 * x ** 2 + 3 / x)
    ch.check(sp.solve(2 + 3 + sp.Symbol("c") - 6, sp.Symbol("c")), [1])


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Reverse power rule", r"\int ax^n\,dx=\frac{a}{n+1}x^{n+1}+c\ \ (n\ne-1)", "power up by 1, ÷ new power"),
        ("Constant", r"\int k\,dx=kx+c", None),
        ("The exception", r"\int\frac1x\,dx=\ln|x|+c", None),
        ("Rewrite first", r"\frac{3}{x^2}=3x^{-2},\quad\sqrt x=x^{\frac12},\quad\frac{1}{\sqrt x}=x^{-\frac12}",
         "expand brackets; split fractions over a single term"),
        ("Sums and multiples", r"\int(f\pm g)\,dx=\int f\,dx\pm\int g\,dx,\qquad\int kf\,dx=k\int f\,dx",
         "no such rule for products or quotients"),
        ("e and trig", r"\int e^{kx}dx=\tfrac1ke^{kx},\ \int\sin kx\,dx=-\tfrac1k\cos kx,\ \int\cos kx\,dx=\tfrac1k\sin kx",
         None),
        ("tan", r"\int\tan x\,dx=\ln|\sec x|+c", "the slides write $\\ln(\\sec x)$"),
        ("Finding c", None, "integrate, substitute the known point, solve for $c$"),
        ("Definite integral", r"\int_a^bf(x)\,dx=F(b)-F(a)", "top minus bottom; no $+c$"),
        ("Total area", None, "solve $f(x)=0$, integrate each piece, add the sizes"),
        ("Find the unknown", None, "integrate with the letter as a number, set equal to the given value, solve"),
        ("Trapezium rule", r"\frac h2\big(y_0+2(y_1+\dots+y_{n-1})+y_n\big),\ \ h=\frac{b-a}{n}", None),
    ], C.BLUE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Check every indefinite answer by differentiating it. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Trapezium rule", ["Estimate the area under y = x² from 0 to 2 with 2 strips, then 4 strips. (True: 8/3.)"],
         "1. 3 and 2.75"),
        ("Indefinite integrals", ["∫ 6x² dx", "∫ (3x² − 4x + 5) dx", "∫ (2/x) dx", "∫ e^(3x) dx", "∫ 4 cos 2x dx"],
         "2. 2x³ + c   3. x³ − 2x² + 5x + c   4. 2 ln|x| + c   5. ⅓e^(3x) + c   6. 2 sin 2x + c"),
        ("Find the curve", ["dy/dx = 6x + 2 and the curve passes through (1, 10)."],
         "7. y = 3x² + 2x + 5"),
        ("Definite integrals", ["∫ from 0 to 3 of x² dx", "∫ from 1 to 2 of (4x³ − 1) dx",
                                "The shaded area between y = x³ and the x axis from −1 to 1"],
         "8. 9   9. 14   10. ½ (each side is ¼; the integral itself is 0)"),
        ("Rewrite first", ["∫ 4/x³ dx", "∫ 6√x dx", "∫ (x + 2)² dx", "∫ (x³ − 5)/x dx",
                           "Total area between y = x² − 1 and the x axis from x = 0 to x = 2"],
         "11. −2/x² + c (4x⁻³ → 4x⁻²/(−2))   12. 4x^(3/2) + c   13. x³/3 + 2x² + 4x + c   14. x³/3 − 5 ln|x| + c   "
         "15. 2 (crosses at x = 1: pieces −⅔ and 4/3)"),
        ("Find the unknown", ["dy/dx = 4x + 3 and the curve passes through (1, 2). Find y.",
                              "∫ from 1 to k of 2x dx = 15, with k > 1. Find k.", "∫ from 0 to 3 of (ax + 2) dx = 15. Find a.",
                              "∫ from 0 to k of 3x² dx = 64. Find k.", "f′(x) = 6x² − 2/x² and f(1) = 5. Find f(x)."],
         "16. y = 2x² + 3x − 3 (2 + 3 + c = 2)   17. k = 4 (k² − 1 = 15)   18. a = 2 (9a/2 + 6 = 15)   "
         "19. k = 4 (k³ = 64)   20. f(x) = 2x³ + 2/x + 1 (2 + 2 + c = 5)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check([trap(2, 0, 2), trap(4, 0, 2)], [3.0, 2.75])
    ch.check(sp.integrate(6 * x ** 2, x), 2 * x ** 3)
    ch.check(sp.integrate(3 * x ** 2 - 4 * x + 5, x), x ** 3 - 2 * x ** 2 + 5 * x)
    ch.check(sp.integrate(2 / x, x), 2 * sp.log(x))
    ch.check(sp.integrate(sp.exp(3 * x), x), sp.exp(3 * x) / 3)
    ch.check(sp.integrate(4 * sp.cos(2 * x), x), 2 * sp.sin(2 * x))
    c = sp.Symbol("c")
    ch.check(sp.solve(sp.Eq(3 + 2 + c, 10), c), [5])
    ch.check([sp.integrate(x ** 2, (x, 0, 3)), sp.integrate(4 * x ** 3 - 1, (x, 1, 2)),
              2 * sp.integrate(x ** 3, (x, 0, 1))], [9, 14, sp.Rational(1, 2)])
    ch.check(sp.integrate(4 / x ** 3, x), -2 / x ** 2)
    ch.check(sp.integrate(6 * sp.sqrt(x), x), 4 * x ** sp.Rational(3, 2))
    ch.check(sp.integrate(sp.expand((x + 2) ** 2), x), x ** 3 / 3 + 2 * x ** 2 + 4 * x)
    ch.check(sp.integrate(sp.expand((x ** 3 - 5) / x), x), x ** 3 / 3 - 5 * sp.log(x))
    ch.check([sp.integrate(x ** 2 - 1, (x, 0, 1)), sp.integrate(x ** 2 - 1, (x, 1, 2)),
              abs(sp.integrate(x ** 2 - 1, (x, 0, 1))) + abs(sp.integrate(x ** 2 - 1, (x, 1, 2)))],
             [-sp.Rational(2, 3), sp.Rational(4, 3), 2])
    ch.check(sp.solve(x ** 2 - 1, x), [-1, 1])
    k, a = sp.symbols("k a")
    ch.check(sp.solve(sp.integrate(4 * x + 3, x).subs(x, 1) + c - 2, c), [-3])
    ch.check([s for s in sp.solve(sp.integrate(2 * x, (x, 1, k)) - 15, k) if s > 1], [4])
    ch.check(sp.solve(sp.integrate(a * x + 2, (x, 0, 3)) - 15, a), [2])
    ch.check([s for s in sp.solve(sp.integrate(3 * x ** 2, (x, 0, k)) - 64, k) if s.is_real], [4])
    F20 = sp.integrate(6 * x ** 2 - 2 / x ** 2, x)
    ch.check(F20, 2 * x ** 3 + 2 / x)
    ch.check(sp.solve(F20.subs(x, 1) + c - 5, c), [1])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    pool(ch)
    trapezium(ch)
    strips(ch)
    integral_sign(ch)
    undo(ch)
    moving_edge(ch)
    family(ch)
    one_over_x(ch)
    rewrite(ch)
    standard_list(ch)
    definite(ch)
    shapes(ch)
    negative(ch)
    find_unknown(ch)
    summary(ch)
    your_turn(ch)
