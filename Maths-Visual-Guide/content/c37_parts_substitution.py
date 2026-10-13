"""Chapter 37 - Integration by parts and by substitution (Lecture 17). Parts is Chapter 35's product rule
run backwards: the u-v rectangle split by a curve into two areas. A 2×2 workings grid (differentiate one,
integrate the other), the L-I-A-T-E ladder for picking u, the good road vs the bad road, the D/I table for
doing parts twice, the invisible 1 in ln x, and definite examples read off their graphs. Substitution
renames the messy chunk: two rulers moving at different speeds explain dx = dy/3, colour-matched
partners cancel, and the limits change units too. Finally a sorting flowchart."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, section, step, title_block

ORDER = 37
NUM = 37
TITLE = "Integration by parts and substitution"
SHORT = "Parts & substitution"
SLUG = "Parts-Substitution"
ACCENT = C.GREEN
REQUIRES = ["integration", "indefinite-integral", "definite-integral", "reverse-power-rule", "standard-integrals",
            "constant-of-integration", "integral-linearity", "limits-of-integration", "negative-area",
            "integral-of-1-over-x", "product-rule", "chain-rule", "derivative", "differentiation",
            "standard-derivatives", "natural-log", "e-number", "sine", "cosine", "inverse-trig", "radian",
            "exact-trig-values", "fractional-powers", "negative-powers", "substitution", "area",
            "inverse-operations"]
INTRODUCES = ["integration-by-parts", "parts-formula", "liate", "tabular-integration",
              "integration-by-substitution", "substitution-limits", "reverse-chain-rule", "linear-inside-shortcut"]

PAPER = "#f8fcf8"
x, t, y = sp.symbols("x t y")
DIFF = r"\frac{\dd u}{\dd x}"
DV = r"\frac{\dd v}{\dd x}"
PARTS = (r"\int\blu{u}\,\org{\frac{\dd v}{\dd x}}\,\dd x=\blu{u}\,\org{v}-\int\org{v}\,\blu{\frac{\dd u}{\dd x}}"
         r"\,\dd x")


def icon(pg, x0, y0):
    pg.poly([(x0 + 9, y0 + 3), (x0 + 1, y0 + 9), (x0 + 9, y0 + 15)], C.GREEN, 1.8, closed=True)
    pg.poly([(x0 + 17, y0 + 3), (x0 + 9, y0 + 9), (x0 + 17, y0 + 15)], C.GREEN, 1.8, closed=True)


def sec(f, t_, **kw):
    section(f, t_, C.GREEN, icon, **kw)


def grid4(f, u, dudx, dvdx, v, note="", size=16):
    """Lecture 17's workings box: u goes DOWN by differentiating, dv/dx goes DOWN by integrating."""
    y_ = f.reserve(128)
    pg = f.pg
    x0, cw, rh, gp = L + 20, 140, 44, 24
    for c in range(2):
        for r_ in range(2):
            col = C.BLUE if c == 0 else C.ORANGE
            pg.rect(x0 + c * (cw + 50), y_ + 6 + r_ * (rh + gp), cw, rh, col, 1.2, fillcolor=C.LIGHT[col], r=6)
    cells = [(0, 0, "u=" + u, C.BLUE), (0, 1, r"\frac{\dd u}{\dd x}=" + dudx, C.BLUE),
             (1, 0, r"\frac{\dd v}{\dd x}=" + dvdx, C.ORANGE), (1, 1, "v=" + v, C.ORANGE)]
    for c, r_, s, col in cells:
        w_, h_, _ = pg.eq_size(s, size)
        pg.eq(x0 + c * (cw + 50) + cw / 2, y_ + 6 + r_ * (rh + gp) + rh / 2 - h_ / 2, s, size, col, align="center")
    for c, lab_ in [(0, "differentiate"), (1, "integrate")]:
        cx_ = x0 + c * (cw + 50) + cw / 2
        pg.arrow(cx_, y_ + 6 + rh + 2, cx_, y_ + 6 + rh + gp - 2, C.GREEN, 1.4, head=5)
        pg.text(cx_ + 8, y_ + 6 + rh + 5, lab_, 9, C.GREEN, F.BOLD, solid=False)
    if note:
        pg.note(x0 + 2 * cw + 80, y_ + 4, note, C.INK, 14, w=R - (x0 + 2 * cw + 80))


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 37, "Integration by parts and substitution", "rewind the rules", C.GREEN, PAPER)
    y0 = 200
    pg.rect(L + 10, y0, 200, 58, C.PURPLE, 1.4, fillcolor=C.LIGHT[C.PURPLE], r=8)
    pg.eq(L + 110, y0 + 8, r"(uv)'=u'v+uv'", 20, C.PURPLE, align="center")
    pg.text(L + 10, y0 + 36, "product rule (Chapter 35)", 10, C.PURPLE, F.BOLD, w=200, align="center")
    pg.rect(L + 10, y0 + 86, 200, 66, C.PURPLE, 1.4, fillcolor=C.LIGHT[C.PURPLE], r=8)
    pg.eq(L + 110, y0 + 96, r"f(g(x))'=f'(g)\,g'", 20, C.PURPLE, align="center")
    pg.text(L + 10, y0 + 132, "chain rule (Chapter 35)", 10, C.PURPLE, F.BOLD, w=200, align="center")
    for k, (lab_, yy) in enumerate([("integration by parts", y0 + 29), ("integration by substitution", y0 + 119)]):
        pg.arrow(L + 225, yy, L + 300, yy, C.GREEN, 2.2, head=9)
        icon(pg, L + 250, yy - 30)
        pg.rect(L + 310, yy - 29, 180, 58, C.GREEN, 1.4, fillcolor=C.LIGHT[C.GREEN], r=8)
        pg.text(L + 310, yy - 8, lab_, 12, C.GREEN, F.BOLD, w=180, align="center")
    pg.note(L + 240, y0 + 160, "each technique is a differentiation rule played in reverse", C.GREEN, 15, w=250)
    f = ch.flow(top=410)
    f.p("Chapter 36 could integrate single pieces: $x^n$, $e^{kx}$, $\\sin kx$. It could also add pieces. "
        "But what about pieces {B:multiplied} together, like $x\\sin x$, or a function {B:inside} another, "
        "like $(3x+1)^4$?", 14, gap=10)
    f.p("There's no simple \"multiply the integrals\" rule. Instead there are two techniques, and each "
        "one is a differentiation rule from Chapter 35 run backwards, like pressing rewind.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 17} {y:(recap, products of functions, integration by parts and its "
        "derivation, repeated parts, ln x, choosing u, definite integrals by parts, integration by substitution, "
        "substitution with limits, the general solution).}", 12.5)


def recap(ch):
    f = flow(ch)
    sec(f, "Warm-up: top minus bottom", room=400)
    f.p("Lecture 17 opens with a reminder of Chapter 36. Put the top limit in, put the bottom limit in, "
        "subtract. A scoreboard helps keep the two apart:", 14, gap=6)
    step(f, r"\int_0^2 3x^3\,\dd x=\Big[\tfrac34x^4\Big]_0^2", "power up, ÷ new power", size=18)
    y_ = f.reserve(70)
    pg = f.pg
    for k, (lab_, s, col) in enumerate([("TOP  (x = 2)", r"\tfrac34\times2^4=12", C.BLUE),
                                        ("BOTTOM  (x = 0)", r"\tfrac34\times0^4=0", C.RED)]):
        xx = L + 20 + k * 175
        pg.rect(xx, y_ + 4, 160, 56, col, 1.3, fillcolor=C.LIGHT[col], r=6)
        pg.text(xx, y_ + 8, lab_, 10, col, F.BOLD, w=160, align="center")
        pg.eq(xx + 80, y_ + 26, s, 16, col, align="center")
    pg.eq(L + 380, y_ + 20, r"12-0=\grn{12}", 20)
    ch.check(sp.integrate(3 * x ** 3, (x, 0, 2)), 12)
    f.p("{b:Lecture 17's your turn:} $\\int_1^2\\big(2x^{1/2} - 18x\\big)\\,\\dd x$. The half power is just "
        "another power (Chapter 9): up by one to $\\frac32$, then divide by $\\frac32$, which is the same as "
        "multiplying by $\\frac23$.", 14, gap=6)
    step(f, r"=\Big[\tfrac43x^{3/2}-9x^2\Big]_1^2", "2 × ⅔ = 4/3,   18 ÷ 2 = 9", size=18)
    y_ = f.reserve(70)
    pg = f.pg
    for k, (lab_, s, col) in enumerate([("TOP  (x = 2)", r"\tfrac43(2)^{3/2}-36\approx-32.23", C.BLUE),
                                        ("BOTTOM  (x = 1)", r"\tfrac43-9\approx-7.67", C.RED)]):
        xx = L + 20 + k * 205
        pg.rect(xx, y_ + 4, 195, 56, col, 1.3, fillcolor=C.LIGHT[col], r=6)
        pg.text(xx, y_ + 8, lab_, 10, col, F.BOLD, w=195, align="center")
        pg.eq(xx + 97, y_ + 26, s, 14, col, align="center")
    step(f, r"-32.23-(-7.67)=-32.23+7.67=\grn{-24.56}", "minus a minus is a plus", size=18)
    ch.check_num(float(sp.integrate(2 * sp.sqrt(x) - 18 * x, (x, 1, 2))), -24.56, 0.005)
    ch.check_num(float(sp.Rational(4, 3) * 2 ** 1.5 - 36), -32.23, 0.005)


def products(ch):
    f = flow(ch)
    sec(f, "Multiplied pieces: the trap", room=300)
    f.p("Adding is easy: $\\int(f + g) = \\int f + \\int g$. So it's tempting to guess that multiplying works "
        "the same way. {R:It doesn't.} Test it on the simplest product there is, $x \\times x$:", 14, gap=6)
    step(f, r"\int x\cdot x\,\dd x=\int x^2\,\dd x=\frac{x^3}{3}", "the true answer", size=18, color=C.GREEN)
    step(f, r"\Big(\int x\,\dd x\Big)\Big(\int x\,\dd x\Big)=\frac{x^2}{2}\cdot\frac{x^2}{2}=\frac{x^4}{4}\ \ \red{\times}",
         "the guess: wrong power, wrong number", size=17)
    ch.check(sp.integrate(x * x, x), x ** 3 / 3)
    ch.check(sp.integrate(x, x) ** 2 == sp.integrate(x * x, x), False)
    f.p("Lecture 17's examples of products: $\\int(x^2 + 7)\\sin x\\,\\dd x$, $\\int x e^{2x}\\,\\dd x$, "
        "$\\int f(x)\\,g(x)\\,\\dd x$. For these we need {B:integration by parts}.", 14)


def derivation(ch):
    f = flow(ch)
    sec(f, "Where parts comes from: one rectangle, two pieces", room=560)
    rule_box(f, "integration by parts", [
        "$\\int u\\frac{\\dd v}{\\dd x}\\,\\dd x=uv-\\int v\\frac{\\dd u}{\\dd x}\\,\\dd x$. Use it for a "
        "{B:product of two different kinds of function} ($x\\sin x$, $xe^{2x}$, $x^2\\ln x$).",
        "One factor is $u$ (you will {B:differentiate} it); the other is $\\frac{\\dd v}{\\dd x}$ (you will "
        "{B:integrate} it to get $v$).",
        "{B:Choosing $u$: LIATE.} Whichever factor comes first in Logs, Inverse trig, Algebra (powers of $x$), "
        "Trig, Exponentials is $u$. A good choice makes the leftover integral $\\int v\\frac{\\dd u}{\\dd x}\\,"
        "\\dd x$ simpler than the original.",
    ], C.GREEN)
    f.p("{b:Where the formula comes from.} Chapter 35 pictured $u \\times v$ as the area of a rectangle. Now let $u$ and $v$ change together, "
        "so that as $u$ grows from 0 to its final size, $v$ grows along a curve. The curve cuts the rectangle "
        "into two pieces:", 14, gap=10)
    y_ = f.reserve(212)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 18, 200, 170, (0, 1.25), (0, 1.25))
    cur = lambda s: (s ** 0.55)
    pts = [ax.P(i / 60, cur(i / 60)) for i in range(61)]
    pg.fillpoly([ax.P(0, 0)] + pts + [ax.P(1, 0)], C.LIGHT[C.ORANGE])
    pg.fillpoly([ax.P(0, 0)] + pts + [ax.P(0, 1)], C.LIGHT[C.TEAL])
    ax.axes("u", "v", 0, 0, size=10)
    pg.poly(pts, C.INK, 2.2)
    pg.rect(ax.X(0), ax.Y(1), ax.X(1) - ax.X(0), ax.Y(0) - ax.Y(1), C.PURPLE, 1.4, dash=(5, 3))
    pg.eq(ax.X(0.68), ax.Y(0.3), r"\int v\,\dd u", 15, C.ORANGE, align="center")
    pg.eq(ax.X(0.27), ax.Y(0.88), r"\int u\,\dd v", 15, C.TEAL, align="center")
    pg.text(ax.X(1) + 4, ax.Y(1) - 16, "final (u, v)", 9, C.PURPLE, F.BOLD)
    pg.note(L + 260, y_ + 6, "orange: the area under the curve, strips standing on the u axis: ∫ v du\n\n"
            "teal: the area beside the curve, strips lying against the v axis: ∫ u dv\n\n"
            "together: the whole rectangle, uv", C.INK, 15, w=R - L - 260)
    step(f, r"\tea{\int u\,\dd v}+\org{\int v\,\dd u}=\pur{uv}", "the two pieces fill the rectangle", size=20)
    step(f, r"\tea{\int u\,\dd v}=\pur{uv}-\org{\int v\,\dd u}", "move the orange piece across", size=20)
    f.p("So if you want the teal piece but it's hard, you can get it from the rectangle minus the orange piece. "
        "That swap is the whole trick. Writing $\\dd v$ as $\\frac{\\dd v}{\\dd x}\\dd x$ gives Lecture 17's "
        "version:", 14, gap=6)
    step(f, PARTS, "", size=20)
    ch.formula(r"\int u\frac{dv}{dx}\,dx=uv-\int v\frac{du}{dx}\,dx", "integration by parts")
    ch.term("integration by parts", "∫u (dv/dx) dx = uv − ∫v (du/dx) dx: the product rule run backwards")
    ch.term("parts formula", "∫u dv = uv − ∫v du")
    f.need(210)
    f.p("{b:Lecture 17's algebra route} (the same thing without the picture): start from the product "
        "rule for $y = uv$.", 14, gap=6)
    step(f, r"\frac{\dd y}{\dd x}=v\frac{\dd u}{\dd x}+u\frac{\dd v}{\dd x}", "Chapter 35", size=17)
    step(f, r"u\frac{\dd v}{\dd x}=\frac{\dd y}{\dd x}-v\frac{\dd u}{\dd x}", "subtract to isolate one term", size=17)
    step(f, r"\int u\frac{\dd v}{\dd x}\,\dd x=\int\frac{\dd y}{\dd x}\,\dd x-\int v\frac{\dd u}{\dd x}\,\dd x",
         "integrate every term", size=17)
    step(f, r"\int\frac{\dd y}{\dd x}\,\dd x=y=uv", "integrating undoes differentiating", size=17)
    uu, vv = sp.Function("u")(x), sp.Function("v")(x)
    ch.check(sp.simplify(uu * sp.diff(vv, x) - (sp.diff(uu * vv, x) - vv * sp.diff(uu, x))), 0)


def first(ch):
    f = flow(ch)
    sec(f, "The workings box: x sin x", room=520)
    rule_box(f, "integration by parts, step by step", [
        "Choose $u$ by LIATE; the other factor is $\\frac{\\dd v}{\\dd x}$.",
        "Differentiate $u$ to get $\\frac{\\dd u}{\\dd x}$. Integrate $\\frac{\\dd v}{\\dd x}$ to get $v$ "
        "(no $+C$ yet).",
        "Substitute into $uv-\\int v\\frac{\\dd u}{\\dd x}\\,\\dd x$.",
        "Do the leftover integral. If it is still a product, use parts again.",
        "Add a single $+C$ at the end, and check by differentiating.",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    f.p("The formula has four ingredients. Lecture 17 lays them out in a box. You {B:choose} the top row; "
        "the bottom row follows. $u$ gets {B:differentiated} and $\\frac{\\dd v}{\\dd x}$ gets {B:integrated}:",
        14, gap=10)
    grid4(f, "x", "1", r"\sin x", r"-\cos x", "u = x because it turns into a plain 1 when differentiated.")
    f.p("Now feed the four boxes into the formula, colour for colour:", 14, gap=6)
    step(f, PARTS, "", size=17)
    step(f, r"\int x\sin x\,\dd x=\blu{x}\,\org{(-\cos x)}-\int\org{(-\cos x)}\,\blu{(1)}\,\dd x", "", size=17)
    step(f, r"=-x\cos x+\int\cos x\,\dd x", "minus times minus", size=17)
    step(f, r"=\sin x-x\cos x+C", "∫cos x = sin x (Chapter 36)", size=19, color=C.GREEN)
    ch.check(sp.integrate(x * sp.sin(x), x), sp.sin(x) - x * sp.cos(x))
    step(f, r"\text{check: }\frac{\dd}{\dd x}(\sin x-x\cos x)=\cos x-(\cos x-x\sin x)=x\sin x\ \checkmark",
         "product rule on x cos x", size=15, color=C.GREEN)
    ch.check(sp.simplify(sp.diff(sp.sin(x) - x * sp.cos(x), x) - x * sp.sin(x)), 0)
    f.p("{b:About the +c.} Lecture 17 carries a $+c$ on $v$ and it cancels out ($+cx$ then $-cx$). So leave "
        "$v$ without one and add a single $+C$ at the very end. (The slide ends with \"$-d$\": any constant, "
        "plus or minus, means the same thing.)", 13.5)


def choosing(ch):
    f = flow(ch)
    sec(f, "Which one is u? The ladder", room=560)
    f.p("Lecture 17: you must be able to {B:differentiate u easily} and {B:integrate dv/dx easily}, and the "
        "leftover integral must be no harder than the one you started with. A handy ordering: climb the "
        "ladder, and whichever piece sits {B:higher} becomes $u$.", 14, gap=10)
    y_ = f.reserve(210)
    pg = f.pg
    lx, top_, rw, gapr = L + 50, y_ + 10, 250, 38
    pg.line(lx, top_ - 4, lx, top_ + 4 * gapr + 22, C.BROWN, 3)
    pg.line(lx + rw, top_ - 4, lx + rw, top_ + 4 * gapr + 22, C.BROWN, 3)
    rungs = [("L", "logs: ln x", C.RED), ("I", "inverse trig: sin⁻¹x", C.ORANGE),
             ("A", "algebra: x, x², 7x", C.GREEN), ("T", "trig: sin x, cos 3x", C.BLUE),
             ("E", "exponentials: eˣ, e⁻ˣ", C.PURPLE)]
    for k, (letter, lab_, col) in enumerate(rungs):
        yy = top_ + k * gapr
        pg.line(lx, yy + 12, lx + rw, yy + 12, C.BROWN, 2)
        pg.circle(lx + 24, yy + 12, 12, col, 1.2, fillcolor="#ffffff")
        pg.text(lx + 12, yy + 3, letter, 13, col, F.BOLD, w=24, align="center")
        pg.text(lx + 46, yy - 4, lab_, 12, col, F.BOLD)
    pg.arrow(lx - 22, top_ + 4 * gapr + 12, lx - 22, top_ + 4, C.GREEN, 1.8, head=7)
    pg.note(lx + rw + 20, top_ - 4, "higher rung = make it u\n\nsingle powers of x are great u's (Lecture 17): "
            "differentiate them and they shrink to a number", C.INK, 15, w=R - lx - rw - 20)
    ch.term("LIATE", "order for choosing u in parts: Logs, Inverse trig, Algebra, Trig, Exponentials")
    f.p("{b:What happens if you pick the wrong one?} Try $x\\sin x$ both ways:", 14, gap=10)
    y_ = f.reserve(162)
    pg = f.pg
    for k, (title_, lines, col, mark) in enumerate([
            ("u = x (A beats T)", [r"\frac{\dd u}{\dd x}=1,\ \ v=-\cos x", r"\text{left over: }\int-\cos x\,\dd x",
                                   r"\text{power of }x\text{ fell: }x\to1"], C.GREEN, "✓ easier"),
            ("u = sin x (wrong way)", [r"\frac{\dd u}{\dd x}=\cos x,\ \ v=\tfrac{x^2}{2}",
                                       r"\text{left over: }\int\tfrac{x^2}{2}\cos x\,\dd x",
                                       r"\text{power of }x\text{ rose: }x\to x^2"], C.RED, "✗ harder")]):
        xx = L + k * 252
        pg.rect(xx, y_ + 4, 240, 150, col, 1.4, fillcolor=C.LIGHT[col], r=8)
        pg.text(xx, y_ + 10, title_, 12, col, F.BOLD, w=240, align="center")
        for j, s in enumerate(lines):
            pg.eq(xx + 120, y_ + 30 + j * 36, s, 12, align="center")
        pg.text(xx, y_ + 134, mark, 12, col, F.BOLD, w=240, align="center")
    ch.check(sp.expand(sp.integrate(x ** 2 / 2 * sp.cos(x), x) - x ** 2 / 2 * sp.sin(x)).has(x ** 2), False)


def twice(ch):
    f = flow(ch)
    sec(f, "Parts twice: x² cos x", room=520)
    f.p("{b:Lecture 17's harder example:} $\\int x^2\\cos x\\,\\dd x$. By the ladder, $u = x^2$ (A beats T).",
        14, gap=10)
    grid4(f, "x^2", "2x", r"\cos x", r"\sin x")
    step(f, r"\int x^2\cos x\,\dd x=x^2\sin x-\int\sin x\cdot2x\,\dd x", "", size=17)
    f.p("The leftover $\\int 2x\\sin x\\,\\dd x$ is {B:still a product}. But it's $2 \\times$ the example we just "
        "did, so reuse it:", 14, gap=6)
    step(f, r"=x^2\sin x-2(\sin x-x\cos x)+C", "Lecture 17's answer", size=18, color=C.GREEN)
    step(f, r"=x^2\sin x+2x\cos x-2\sin x+C", "brackets opened", size=18, color=C.GREEN)
    ans = x ** 2 * sp.sin(x) + 2 * x * sp.cos(x) - 2 * sp.sin(x)
    ch.check(sp.simplify(sp.integrate(x ** 2 * sp.cos(x), x) - ans), 0)
    f.p("{b:A shortcut table.} When $u$ is a power of $x$, parts keeps going until $u$ is differentiated down "
        "to 0. Make two columns: {B:D} (keep differentiating $u$) and {B:I} (keep integrating). Join each D "
        "to the {B:next row's} I, with signs $+, -, +, \\dots$ taking turns:", 14, gap=10)
    y_ = f.reserve(190)
    pg = f.pg
    x0, rowh = L + 60, 38
    Dcol = ["x^2", "2x", "2", "0"]
    Icol = [r"\cos x", r"\sin x", r"-\cos x", r"-\sin x"]
    pg.text(x0 - 10, y_, "D", 15, C.BLUE, F.BOLD, w=60, align="center")
    pg.text(x0 + 150, y_, "I", 15, C.ORANGE, F.BOLD, w=60, align="center")
    for k in range(4):
        yy = y_ + 26 + k * rowh
        pg.eq(x0 + 20, yy, Dcol[k], 16, C.BLUE if k < 3 else C.GREY, align="center")
        pg.eq(x0 + 180, yy, Icol[k], 16, C.ORANGE, align="center")
    signs = ["+", "−", "+"]
    for k in range(3):
        y1, y2 = y_ + 36 + k * rowh, y_ + 36 + (k + 1) * rowh
        pg.arrow(x0 + 45, y1, x0 + 145, y2, C.GREEN, 1.4, head=6)
        pg.text(x0 + 82, (y1 + y2) / 2 - 20, signs[k], 14, C.RED, F.BOLD, solid=False)
    pg.text(x0 - 10, y_ + 26 + 3 * rowh + 20, "stop when D hits 0", 10, C.GREY, F.BOLD)
    pg.note(L + 300, y_ + 20, "multiply along each arrow, with its sign:\n\n+ x² sin x\n− 2x (−cos x)\n+ 2 (−sin x)",
            C.INK, 15, w=R - L - 300)
    step(f, r"=x^2\sin x+2x\cos x-2\sin x+C", "✓ the same", size=18, color=C.GREEN)
    ch.term("tabular integration", "D/I table for repeated parts: differentiate u down to 0, integrate the other, alternate signs")


def log_case(ch):
    f = flow(ch)
    sec(f, "The invisible 1: integrating ln x", room=360)
    f.p("$\\ln x$ isn't in Chapter 36's table, and it isn't a product... unless you spot the {B:invisible 1} "
        "that's always there:", 14, gap=10)
    y_ = f.reserve(80)
    pg = f.pg
    pg.eq(L + 60, y_ + 8, r"\int\ln x\,\dd x", 24)
    pg.arrow(L + 180, y_ + 24, L + 230, y_ + 24, C.GREY, 1.4, head=6)
    pg.eq(L + 245, y_ + 8, r"\int\gry{1\times}\ln x\,\dd x", 24)
    pg.note(L + 420, y_, "ln is top of the ladder, so u = ln x and the 1 is dv/dx", C.RED, 13, w=R - L - 420)
    grid4(f, r"\ln x", r"\frac1x", "1", "x")
    step(f, r"\int\ln x\,\dd x=x\ln x-\int x\cdot\frac1x\,\dd x", "", size=18)
    step(f, r"=x\ln x-\int1\,\dd x=x\ln x-x+C", "x × 1/x = 1", size=18, color=C.GREEN)
    ch.check(sp.integrate(sp.log(x), x), x * sp.log(x) - x)


def definite(ch):
    f = flow(ch)
    sec(f, "Parts with limits", room=520)
    rule_box(f, "definite integration by parts (Lecture 17)", [
        "$\\displaystyle\\int_a^b u\\frac{\\dd v}{\\dd x}\\,\\dd x=\\Big[uv\\Big]_a^b-\\int_a^b v\\frac{\\dd u}"
        "{\\dd x}\\,\\dd x$",
        "The $uv$ part gets square brackets and its own top-minus-bottom; the leftover integral keeps the "
        "{B:same limits}. No $+C$ anywhere.",
        "Tidy approach: find the whole indefinite answer first, then put it in one set of square brackets and "
        "do top minus bottom once.",
    ], C.GREEN)
    ch.formula(r"\int_a^bu\frac{dv}{dx}\,dx=\Big[uv\Big]_a^b-\int_a^bv\frac{du}{dx}\,dx", "definite integration by parts")
    f.need(330)
    f.p("{b:Lecture 17:} $\\int_0^2 x e^{-x}\\,\\dd x$. By the ladder, $u = x$ (A beats E).", 14, gap=10)
    grid4(f, "x", "1", "e^{-x}", "-e^{-x}", "∫e^(−x) = −e^(−x): the k = −1 case of ∫e^(kx) = (1/k)e^(kx)")
    step(f, r"=\Big[-xe^{-x}\Big]_0^2+\int_0^2e^{-x}\,\dd x=\Big[-xe^{-x}-e^{-x}\Big]_0^2", "", size=17)
    step(f, r"=(-2e^{-2}-e^{-2})-(0-1)=1-3e^{-2}\approx0.594", "top minus bottom", size=17, color=C.GREEN)
    ch.check(sp.integrate(x * sp.exp(-x), (x, 0, 2)), 1 - 3 * sp.exp(-2))
    y_ = f.reserve(120)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 5, 200, 100, (0, 2.4), (0, 0.45))
    ax.fill_under(lambda v: v * math.exp(-v), 0, 2, C.LIGHT[C.GREEN])
    ax.axes("x", None, 1, 0, size=8)
    ax.curve(lambda v: v * math.exp(-v), 0, 2.35, C.GREEN, 2.0)
    ax.label(0.9, 0.12, "{G:≈ 0.594}", 11, dx=0, dy=-8)
    pg.note(L + 250, y_ + 10, "sanity check: the shape is under 0.37 tall and 2 wide, so an area a bit over "
            "half makes sense", C.INK, 14, w=R - L - 250)
    ch.check_num(0.37 * 2 * 0.8, 0.594, 0.01)
    f.p("{R:Slide slip:} Lecture 17's working writes $-xe^{x}$ where it should be $-xe^{-x}$, and $e^2$ where "
        "it should be $e^{-2}$. Its final answer $1 - 3e^{-2}$ is right.", 13.5)


def definite_trig(ch):
    f = flow(ch)
    sec(f, "A trig one with limits in radians", room=520)
    f.p("{b:Lecture 17:} $\\int_{\\pi/4}^{\\pi/2} 7x\\sin 3x\\,\\dd x$. The limits are in radians (Chapter 27).",
        14, gap=10)
    grid4(f, "7x", "7", r"\sin3x", r"-\tfrac13\cos3x", "∫sin kx = −(1/k)cos kx with k = 3")
    step(f, r"=\Big[-\tfrac{7x}{3}\cos3x\Big]+\int\tfrac73\cos3x\,\dd x=\Big[-\tfrac{7x}{3}\cos3x+\tfrac79\sin3x"
         r"\Big]_{\pi/4}^{\pi/2}", "", size=16)
    y_ = f.reserve(100)
    pg = f.pg
    boxes = [("TOP  x = π/2", [r"\cos\tfrac{3\pi}{2}=0,\ \sin\tfrac{3\pi}{2}=-1", r"0+\tfrac79(-1)=-\tfrac79"],
              C.BLUE),
             ("BOTTOM  x = π/4", [r"\cos\tfrac{3\pi}{4}=-\tfrac1{\sqrt2},\ \sin\tfrac{3\pi}{4}=\tfrac1{\sqrt2}",
                                  r"\tfrac{7\pi}{12\sqrt2}+\tfrac{7}{9\sqrt2}\approx1.846"], C.RED)]
    for k, (lab_, lines, col) in enumerate(boxes):
        xx = L + k * 252
        pg.rect(xx, y_ + 2, 240, 92, col, 1.3, fillcolor=C.LIGHT[col], r=6)
        pg.text(xx, y_ + 6, lab_, 10, col, F.BOLD, w=240, align="center")
        for j, s in enumerate(lines):
            pg.eq(xx + 120, y_ + 26 + j * 32, s, 13, align="center")
    step(f, r"-\tfrac79-1.846\approx-0.778-1.846\approx\grn{-2.62}", "top minus bottom", size=18)
    val = sp.integrate(7 * x * sp.sin(3 * x), (x, sp.pi / 4, sp.pi / 2))
    ch.check_num(float(val), -2.62, 0.005)
    ch.check_num(float(7 * sp.pi / (12 * sp.sqrt(2)) + 7 / (9 * sp.sqrt(2))), 1.846, 0.001)
    f.p("A negative answer? Chapter 36: area below the axis counts negative. The graph shows why:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    g = lambda v: 7 * v * math.sin(3 * v)
    ax = Axes(pg, L + 20, y_ + 5, 240, 135, (0.6, 1.75), (-12, 5))
    ax.fill_under(g, math.pi / 4, math.pi / 3, C.LIGHT[C.BLUE])
    ax.fill_under(g, math.pi / 3, math.pi / 2, C.LIGHT[C.RED])
    ax.axes("x", None, 0, 4, size=8)
    ax.curve(g, 0.65, 1.7, C.INK, 2.0)
    ax.vline(math.pi / 4, C.GREY, 0.8, dash=(3, 3), y0=-12, y1=5)
    ax.vline(math.pi / 2, C.GREY, 0.8, dash=(3, 3), y0=-12, y1=5)
    ax.label(math.pi / 4, -11, "π/4", 9, dx=-8, dy=4)
    ax.label(math.pi / 2, 4.5, "π/2", 9, dx=4, dy=0)
    pg.note(L + 285, y_ + 10, "a small blue piece above the axis (π/4 to π/3), a much bigger red piece below "
            "(π/3 to π/2). Net: negative.", C.INK, 15, w=R - L - 285)
    ch.check_num(float(sp.integrate(7 * x * sp.sin(3 * x), (x, sp.pi / 4, sp.pi / 3))), 0.598, 0.001)


def rename(ch):
    f = flow(ch)
    sec(f, "Substitution: rename the messy chunk", room=560)
    rule_box(f, "integration by substitution", [
        "{B:Choose the new letter}: let $y=$ the inside of a bracket, power or function, ideally one whose "
        "derivative (give or take a number) also appears in the integral.",
        "Differentiate: find $\\frac{\\dd y}{\\dd x}$, then rearrange to $\\dd x=\\dfrac{\\dd y}{\\dd y/\\dd x}$.",
        "Substitute both, so that {B:every} $x$ disappears (matching $x$ factors cancel). If an $x$ is left "
        "over, this choice of $y$ doesn't work.",
        "Integrate with respect to $y$.",
        "Indefinite: substitute back, $y=$ (the chunk), and add $+C$.  Definite: instead {B:change the "
        "limits} into $y$-values and never go back to $x$.",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    f.p("Lecture 17 calls the new letter $y$, because $u$ is already busy in the parts formula. Many books "
        "call it $u$; the letter doesn't matter as long as it's not $x$.", 13.5, gap=10)
    f.p("{b:Lecture 17:} $\\int(3x+1)^4\\,\\dd x$. You could multiply out the fourth power, but that's a "
        "pain. Instead, wrap the messy chunk in a parcel and give it a one-letter name:", 14, gap=10)
    y_ = f.reserve(100)
    pg = f.pg
    pg.eq(L + 20, y_ + 22, r"\int(\blu{3x+1})^4\,\dd x", 22)
    bx = L + 200
    pg.rect(bx, y_ + 10, 110, 70, C.BLUE, 1.6, fillcolor=C.LIGHT[C.BLUE], r=4)
    pg.line(bx, y_ + 28, bx + 110, y_ + 28, C.RED, 2.4)
    pg.line(bx + 55, y_ + 10, bx + 55, y_ + 28, C.RED, 2.4)
    pg.ellipse(bx + 46, y_ + 8, 9, 5, C.RED, 1.6)
    pg.ellipse(bx + 64, y_ + 8, 9, 5, C.RED, 1.6)
    pg.eq(bx + 55, y_ + 42, r"\blu{3x+1}", 16, align="center", solid=False)
    pg.text(bx, y_ - 12, "call it y", 12, C.BLUE, F.BOLD, w=110, align="center")
    pg.arrow(bx + 120, y_ + 45, bx + 165, y_ + 45, C.GREY, 1.4, head=6)
    pg.eq(bx + 180, y_ + 22, r"\int\blu{y}^4\,\dd x\ \ ?", 22)
    ch.term("integration by substitution", "rename an inner chunk as a new letter, swap dx for the new letter's d, integrate, swap back")
    f.p("$y^4$ is easy, but there's a problem: the $\\dd x$ still says \"x\". The strips are measured in the "
        "wrong units. How do x-steps convert into y-steps? Put two rulers side by side:", 14, gap=10)
    y_ = f.reserve(110)
    pg = f.pg
    x0, sp_ = L + 40, 120
    pg.line(x0 - 10, y_ + 20, x0 + 2 * sp_ + 30, y_ + 20, C.INK, 1.4)
    pg.line(x0 - 10, y_ + 80, x0 + 2 * sp_ + 30, y_ + 80, C.INK, 1.4)
    pg.text(x0 - 40, y_ + 12, "x", 14, C.INK, F.BOLD)
    pg.text(x0 - 40, y_ + 72, "y", 14, C.BLUE, F.BOLD)
    for k in range(3):
        xx = x0 + k * sp_
        pg.line(xx, y_ + 14, xx, y_ + 26, C.INK, 1.4)
        pg.text(xx - 10, y_ - 6, str(k), 12, C.INK, F.BOLD, w=20, align="center")
        pg.arrow(xx, y_ + 28, xx, y_ + 72, C.GREY, 1.0, head=5, dash=(3, 3))
        pg.text(xx - 10, y_ + 88, str(3 * k + 1), 12, C.BLUE, F.BOLD, w=20, align="center")
    for j in range(7):
        xx = x0 + j * sp_ / 3
        pg.line(xx, y_ + 75, xx, y_ + 85, C.BLUE, 1.4)
    pg.note(x0 + 2 * sp_ + 50, y_ + 0, "one step along x is three steps along y. So dy = 3 dx, which "
            "means dx = dy ÷ 3", C.INK, 15, w=R - (x0 + 2 * sp_ + 50))
    step(f, r"\frac{\dd y}{\dd x}=3\ \Rightarrow\ \dd x=\frac{\dd y}{3}", "Lecture 17", size=18)
    step(f, r"\int(3x+1)^4\,\dd x=\int y^4\,\frac{\dd y}{3}=\frac13\cdot\frac{y^5}{5}+C", "now everything is y",
         size=18)
    step(f, r"=\frac{(3x+1)^5}{15}+C", "unwrap the parcel: y = 3x + 1", size=19, color=C.GREEN)
    ch.check(sp.simplify(sp.integrate((3 * x + 1) ** 4, x) - (3 * x + 1) ** 5 / 15).is_constant(), True)
    step(f, r"\text{check: }\frac{\dd}{\dd x}\frac{(3x+1)^5}{15}=\frac{5(3x+1)^4\times3}{15}=(3x+1)^4\ \checkmark",
         "chain rule", size=15, color=C.GREEN)
    ch.check(sp.simplify(sp.diff((3 * x + 1) ** 5 / 15, x) - (3 * x + 1) ** 4), 0)


def partners(ch):
    f = flow(ch)
    sec(f, "The partner outside the bracket", room=520)
    f.p("{b:First, why a partner is needed at all.} With $y = 3x + 1$ the rulers matched evenly: every x-step "
        "was 3 y-steps. Try $y = x^2$. Mark equal x-steps of 0.5 and see where they land on a y-ruler:", 14,
        gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    x0, wx = L + 40, 300
    X = lambda v: x0 + v / 2 * wx
    Y = lambda v: x0 + v / 4 * wx
    ty, by = y_ + 26, y_ + 104
    strip_cols = [C.ORANGE, C.GREEN, C.PURPLE, C.PINK]
    for k in range(4):
        a_, b_ = k / 2, (k + 1) / 2
        col = strip_cols[k]
        pg.rect(X(a_), ty - 7, X(b_) - X(a_), 14, col, 0.6, fillcolor=C.LIGHT[col])
        pg.rect(Y(a_ ** 2), by - 7, Y(b_ ** 2) - Y(a_ ** 2), 14, col, 0.6, fillcolor=C.LIGHT[col])
        wy = b_ ** 2 - a_ ** 2
        pg.text((Y(a_ ** 2) + Y(b_ ** 2)) / 2, by + 10, f"{wy:g}", 10, col, F.BOLD, align="center")
        ch.check_num(wy, 2 * ((a_ + b_) / 2) * 0.5, 1e-12)
    pg.line(X(0), ty, X(2) + 16, ty, C.INK, 1.4)
    pg.line(Y(0), by, Y(4) + 16, by, C.INK, 1.4)
    pg.text(x0 - 30, ty - 8, "x", 14, C.INK, F.BOLD)
    pg.text(x0 - 30, by - 8, "y", 14, C.BLUE, F.BOLD)
    for k in range(5):
        v = k / 2
        pg.line(X(v), ty - 7, X(v), ty + 7, C.INK, 1.2)
        pg.text(X(v), ty - 24, f"{v:g}", 10, C.INK, align="center")
        pg.arrow(X(v), ty + 9, Y(v * v), by - 10, C.GREY, 0.9, head=4, dash=(3, 3))
    for v in range(5):
        pg.line(Y(v), by - 7, Y(v), by + 7, C.BLUE, 1.2)
        pg.text(Y(v), by + 24, str(v), 10, C.BLUE, align="center")
    pg.note(x0 + wx + 30, y_ + 10, "equal x-steps,\nUNEQUAL y-steps:\nthey grow as x grows", C.RED, 14,
            w=R - (x0 + wx + 30))
    f.p("Each y-step is $2x \\times 0.5$, where $x$ is the middle of that strip: $2(0.25)(0.5) = 0.25$, "
        "$2(0.75)(0.5) = 0.75$, and so on. So $\\dd y = 2x\\,\\dd x$: the exchange rate between the rulers "
        "{B:changes as you go}, and it's $\\frac{\\dd y}{\\dd x}$. When you swap $\\dd x$ for $\\dd y$ you must "
        "bring that rate along, and it only disappears if a matching $x$ is sitting outside to cancel it. "
        "That's the partner.", 14, gap=12)
    f.p("{b:Lecture 17:} $\\int x\\sin(2x^2)\\,\\dd x$. The messy chunk is $2x^2$, so let $y = 2x^2$. Its "
        "derivative is $4x$... and look: an $x$ is already sitting outside, waiting. Colour them:", 14, gap=6)
    step(f, r"\int\org{x}\,\sin(\blu{2x^2})\,\dd x,\qquad\frac{\dd y}{\dd x}=4\org{x}\ \Rightarrow\ \dd x=\frac{\dd y}{4\org{x}}",
         "", size=18)
    step(f, r"=\int\cancel{\org{x}}\,\sin y\,\frac{\dd y}{4\cancel{\org{x}}}=\frac14\int\sin y\,\dd y",
         "the partners cancel: only y is left", size=18)
    step(f, r"=-\frac14\cos y+C=-\frac{\cos(2x^2)}{4}+C", "∫sin = −cos", size=19, color=C.GREEN)
    ch.check(sp.simplify(sp.integrate(x * sp.sin(2 * x ** 2), x) + sp.cos(2 * x ** 2) / 4).is_constant(), True)
    f.p("{R:Slide slip:} Lecture 17 writes $+\\frac{\\cos(2x^2)}{4}$. Differentiate it and you get "
        "$-x\\sin(2x^2)$, the wrong sign, because $\\int\\sin y\\,\\dd y = -\\cos y$.", 13.5, gap=14)
    f.need(260)
    f.p("{b:Lecture 17's your turn:} $\\int t\\sqrt{t^2+1}\\,\\dd t$. Chunk $t^2 + 1$, derivative $2t$, partner "
        "$t$ outside:", 14, gap=6)
    step(f, r"y=\blu{t^2+1},\ \ \frac{\dd y}{\dd t}=2\org{t},\ \ \dd t=\frac{\dd y}{2\org{t}}", "", size=17)
    step(f, r"\int\cancel{\org{t}}\sqrt{y}\,\frac{\dd y}{2\cancel{\org{t}}}=\frac12\int y^{1/2}\,\dd y", "√ is the power ½",
         size=17)
    step(f, r"=\frac12\cdot\frac23y^{3/2}+C=\frac13(t^2+1)^{3/2}+C", "", size=18, color=C.GREEN)
    ch.check(sp.simplify(sp.diff((t ** 2 + 1) ** sp.Rational(3, 2) / 3, t) - t * sp.sqrt(t ** 2 + 1)), 0)
    f.p("{B:The spotting test.} Substitution works when the derivative of the chunk (give or take a number) is "
        "sitting outside as a partner. No partner, no cancelling: $\\int\\sin(2x^2)\\,\\dd x$ can't be done "
        "this way, because $\\frac{\\dd x}{4x}$ would leave an $x$ stranded among the $y$'s.", 14)


def limits(ch):
    f = flow(ch)
    sec(f, "Substitution with limits: change the limits too", room=520)
    f.p("{b:Lecture 17:} $\\int_1^2\\frac{3}{(2t+1)^2}\\,\\dd t$. Let $y = 2t + 1$, so $\\frac{\\dd y}{\\dd t} = 2$ "
        "and $\\dd t = \\frac{\\dd y}{2}$.", 14, gap=6)
    f.p("The limits 1 and 2 are values of $t$. Once everything is in $y$, the limits must be $y$ values too. "
        "Convert them with the same rule, like converting pounds into pence:", 14, gap=10)
    y_ = f.reserve(116)
    pg = f.pg
    x0, sc = L + 60, 60
    pg.line(x0 - 20, y_ + 20, x0 + 5 * sc + 20, y_ + 20, C.INK, 1.4)
    pg.line(x0 - 20, y_ + 80, x0 + 5 * sc + 20, y_ + 80, C.INK, 1.4)
    pg.text(x0 - 50, y_ + 12, "t", 14, C.INK, F.BOLD)
    pg.text(x0 - 50, y_ + 72, "y", 14, C.BLUE, F.BOLD)
    for k in range(6):
        pg.line(x0 + k * sc, y_ + 75, x0 + k * sc, y_ + 85, C.BLUE, 1.2)
        pg.text(x0 + k * sc - 10, y_ + 88, str(k), 10, C.BLUE, w=20, align="center")
    for tv in (1, 2):
        xt = x0 + tv * sc * 1.5
        pg.dot(xt, y_ + 20, 4, C.RED)
        pg.text(xt - 20, y_ - 2, f"t = {tv}", 11, C.RED, F.BOLD, w=40, align="center")
        yv = 2 * tv + 1
        pg.arrow(xt, y_ + 24, x0 + yv * sc, y_ + 76, C.RED, 1.3, head=6)
        pg.dot(x0 + yv * sc, y_ + 80, 4, C.RED)
    pg.note(x0 + 5 * sc + 40, y_ + 6, "t = 1 → y = 3\nt = 2 → y = 5", C.RED, 16, w=R - (x0 + 5 * sc + 40))
    step(f, r"\int_1^2\frac{3}{(2t+1)^2}\,\dd t=\int_{\red3}^{\red5}\frac{3}{y^2}\cdot\frac{\dd y}{2}=\frac32\int_3^5y^{-2}\,\dd y",
         "new limits, new letter", size=17)
    step(f, r"=\frac32\Big[-\frac1y\Big]_3^5=\frac32\Big(-\frac15+\frac13\Big)=\frac32\cdot\frac2{15}=\grn{0.2}",
         "no need to swap back to t", size=17)
    ch.check(sp.integrate(3 / (2 * t + 1) ** 2, (t, 1, 2)), sp.Rational(1, 5))
    ch.term("substitution limits", "when substituting in a definite integral, convert the limits into the new letter")
    f.need(200)
    f.p("{b:The general pattern (Lecture 17).} Every substitution example had a chunk $g(x)$ {B:and its derivative} "
        "$g'(x)$ multiplied together:", 14, gap=6)
    step(f, r"\int_a^b f\big(\blu{g(x)}\big)\,\org{g'(x)}\,\dd x=\int_{g(a)}^{g(b)}f(y)\,\dd y", "y = g(x)", size=19,
         color=C.GREEN)
    ch.formula(r"\int_a^bf(g(x))\,g'(x)\,dx=\int_{g(a)}^{g(b)}f(y)\,dy", "integration by substitution (y = g(x))")
    f.p("That's the {B:chain rule backwards}: Chapter 35's chain rule makes exactly this shape (outer "
        "derivative × inner derivative). In $x\\sin(2x^2)$, $x$ is a quarter of the derivative of $2x^2$; "
        "in $t\\sqrt{t^2+1}$, $t$ is half the derivative of $t^2$.", 14)
    ch.term("reverse chain rule", "∫f(g(x)) g′(x) dx = F(g(x)) + C: substitution undoes the chain rule")


def linear(ch):
    f = flow(ch)
    sec(f, "Shortcut: a linear inside, ax + b", room=520)
    rule_box(f, "integrating f(ax + b)", [
        "If $\\int f(x)\\,\\dd x=F(x)+C$, then $\\int f(ax+b)\\,\\dd x=\\dfrac1a\\,F(ax+b)+C$.",
        "In words: integrate as if the bracket were plain $x$, then {B:divide by $a$}, the number in front of $x$.",
        "{R:Only when the inside is linear} ($ax+b$). For an inside like $x^2+1$ you can't divide by its "
        "derivative $2x$: use substitution with a partner, or expand.",
    ], C.GREEN)
    ch.formula(r"\int f(ax+b)\,dx=\frac1aF(ax+b)+C", "linear inside shortcut")
    f.p("It is substitution done in your head: $y=ax+b$ gives $\\dd x=\\frac{\\dd y}{a}$, and that $\\frac1a$ "
        "comes straight out front. Lecture 17's first example agrees: $\\int(3x+1)^4\\,\\dd x=\\frac13\\cdot"
        "\\frac{(3x+1)^5}{5}=\\frac{(3x+1)^5}{15}$.", 14, gap=8)
    rows = [(r"\int(3x+1)^5\,\dd x=\frac13\cdot\frac{(3x+1)^6}{6}=\frac{(3x+1)^6}{18}+C", "a = 3",
             (3 * x + 1) ** 5, (3 * x + 1) ** 6 / 18),
            (r"\int\cos(2x)\,\dd x=\tfrac12\sin(2x)+C", "a = 2", sp.cos(2 * x), sp.sin(2 * x) / 2),
            (r"\int e^{4x}\,\dd x=\tfrac14e^{4x}+C", "a = 4", sp.exp(4 * x), sp.exp(4 * x) / 4),
            (r"\int\frac{1}{2x+3}\,\dd x=\tfrac12\ln|2x+3|+C", "1/x → ln|x|, a = 2", 1 / (2 * x + 3),
             sp.log(2 * x + 3) / 2),
            (r"\int\sqrt{4x-1}\,\dd x=\frac14\cdot\frac{(4x-1)^{3/2}}{3/2}=\frac{(4x-1)^{3/2}}{6}+C", "a = 4",
             sp.sqrt(4 * x - 1), (4 * x - 1) ** sp.Rational(3, 2) / 6)]
    for lat, why, fx, Fx in rows:
        step(f, lat, why, size=17)
        ch.check(sp.simplify(sp.diff(Fx, x) - fx), 0)
    mistakes(f, [
        (r"\int(3x+1)^5\dd x=\tfrac{(3x+1)^6}{6}", r"\tfrac{(3x+1)^6}{18}+C", "divide by the 3 in front of x as well"),
        (r"\int e^{4x}\,\dd x=4e^{4x}", r"\int e^{4x}\,\dd x=\tfrac14e^{4x}+C", "integrating divides by a; differentiating multiplies"),
        (r"\int(x^2+1)^5\,\dd x=\frac{(x^2+1)^6}{6\cdot2x}", r"\text{expand first}", "the shortcut needs a linear inside"),
    ])


def which(ch):
    f = flow(ch)
    sec(f, "Parts, substitution, or neither? A sorting machine", room=560)
    f.p("Ask the questions in this order. Stop at the first yes.", 14, gap=10)
    y_ = f.reserve(250)
    pg = f.pg
    qs = [("Is it in Chapter 36's table (maybe with a number in front)?", "just use the table", C.GREY),
          ("Is there a chunk whose derivative is sitting outside as a partner?", "substitution", C.BLUE),
          ("Is it a product of two different kinds (x × trig, x × e, ln x)?", "parts: u by the ladder", C.ORANGE)]
    for k, (q, a, col) in enumerate(qs):
        yy = y_ + k * 78
        pg.poly([(L + 10, yy + 28), (L + 30, yy + 4), (L + 290, yy + 4), (L + 310, yy + 28), (L + 290, yy + 52),
                 (L + 30, yy + 52)], C.INK, 1.3, closed=True)
        pg.text(L + 34, yy + 12, q, 11.5, C.INK, w=252, align="center")
        pg.arrow(L + 312, yy + 28, L + 360, yy + 28, C.GREEN, 1.6, head=6)
        pg.text(L + 318, yy + 12, "yes", 9, C.GREEN, F.BOLD)
        pg.rect(L + 362, yy + 10, 138, 36, col, 1.4, fillcolor=C.LIGHT[col], r=6)
        pg.text(L + 362, yy + 19, a, 11, col, F.BOLD, w=138, align="center")
        if k < 2:
            pg.arrow(L + 160, yy + 54, L + 160, yy + 78, C.RED, 1.4, head=6)
            pg.text(L + 166, yy + 56, "no", 9, C.RED, F.BOLD)
    pg.text(L + 34, y_ + 3 * 78 - 8, "no to all three: try rewriting it first (expand, split, use an identity)",
            10.5, C.GREY, F.BOLD, w=440)
    f.p("{b:Sort these} (answers checked by differentiating):", 14, gap=6)
    rows = [(r"\int x\,e^{x^2}\,\dd x", "substitution: y = x², partner x", r"\tfrac12e^{x^2}+C", C.BLUE),
            (r"\int x\,e^{x}\,\dd x", "parts: u = x", r"xe^x-e^x+C", C.ORANGE),
            (r"\int e^{3x}\,\dd x", "table", r"\tfrac13e^{3x}+C", C.GREY),
            (r"\int\cos x\,\sin^4x\,\dd x", "substitution: y = sin x, partner cos x", r"\tfrac15\sin^5x+C", C.BLUE),
            (r"\int x\ln x\,\dd x", "parts: u = ln x (L beats A)", r"\tfrac{x^2}{2}\ln x-\tfrac{x^2}{4}+C", C.ORANGE)]
    y_ = f.reserve(42 * len(rows) + 4)
    pg = f.pg
    for k, (a, how, ans, col) in enumerate(rows):
        yy = y_ + k * 42
        pg.eq(L + 10, yy + 2, a, 14)
        pg.text(L + 150, yy + 8, how, 11.5, col, F.BOLD, w=200)
        pg.eq(L + 370, yy + 4, ans, 14, C.GREEN)
    Fs = [sp.exp(x ** 2) / 2, x * sp.exp(x) - sp.exp(x), sp.exp(3 * x) / 3, sp.sin(x) ** 5 / 5,
          x ** 2 / 2 * sp.log(x) - x ** 2 / 4]
    fs = [x * sp.exp(x ** 2), x * sp.exp(x), sp.exp(3 * x), sp.cos(x) * sp.sin(x) ** 4, x * sp.log(x)]
    ch.check([sp.simplify(sp.diff(F_, x) - f_) for F_, f_ in zip(Fs, fs)], [0] * 5)
    f.p("And the big picture: {B:integration by parts undoes the product rule; substitution undoes the "
        "chain rule.} Both are the undo button (Chapter 36) for a Chapter 35 rule.", 14)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Integration by parts", r"\int u\frac{dv}{dx}\,dx=uv-\int v\frac{du}{dx}\,dx",
         "for a product of two different kinds of function"),
        ("Choosing u", None, "LIATE: Logs, Inverse trig, Algebra, Trig, Exponentials; the earlier one is $u$"),
        ("Parts with limits", r"\int_a^bu\frac{dv}{dx}\,dx=\Big[uv\Big]_a^b-\int_a^bv\frac{du}{dx}\,dx",
         "same limits on both parts"),
        ("Parts twice", None, "if the leftover is still a product, use parts again (or the D/I table)"),
        ("ln x", r"\int\ln x\,dx=x\ln x-x+C", "parts with $u=\\ln x$, $\\frac{dv}{dx}=1$"),
        ("Substitution", None, "let $y$ = inside chunk; $dx=\\frac{dy}{dy/dx}$; every $x$ must disappear; "
                               "integrate; substitute back"),
        ("Substitution with limits", r"\int_a^bf(g(x))\,g'(x)\,dx=\int_{g(a)}^{g(b)}f(y)\,dy",
         "change the limits; don't go back to $x$"),
        ("Linear inside", r"\int f(ax+b)\,dx=\frac1aF(ax+b)+C", "only for $ax+b$"),
        ("Which method?", None, "in the table: use it. Chunk with its derivative outside: substitution. "
                                "Product of different kinds: parts. Otherwise rewrite first"),
    ], C.GREEN)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Check every answer by differentiating it. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Integration by parts", ["∫ x cos x dx", "∫ x e^(2x) dx", "∫ x² e^x dx  (use the D/I table)",
                                  "∫ from 1 to e of ln x dx"],
         "1. x sin x + cos x + C   2. ½x e^(2x) − ¼e^(2x) + C   3. e^x(x² − 2x + 2) + C   4. 1"),
        ("Integration by substitution", ["∫ (2x − 5)⁶ dx", "∫ 6x (x² + 4)⁵ dx", "∫ cos x · e^(sin x) dx",
                                         "∫ from 0 to 1 of 2x (x² + 1)³ dx  (change the limits)"],
         "5. (2x − 5)⁷/14 + C   6. (x² + 4)⁶/2 + C   7. e^(sin x) + C   8. 15/4 (limits become 1 and 2)"),
        ("Which technique?", ["∫ x sin(x²) dx", "∫ x sin x dx", "∫ sin 5x dx"],
         "9. substitution: −½cos(x²) + C   10. parts: sin x − x cos x + C   11. table: −⅕cos 5x + C"),
        ("Linear inside shortcut", ["∫ (5x − 2)³ dx", "∫ sin(3x + 1) dx", "∫ e^(−2x) dx", "∫ 1/(4x + 1) dx"],
         "12. (5x − 2)⁴/20 + C   13. −⅓cos(3x + 1) + C   14. −½e^(−2x) + C   15. ¼ ln|4x + 1| + C"),
        ("Find the unknown", ["∫ from 0 to k of x eˣ dx = 1, with k > 0. Find k.",
                              "∫ (ax + 1)⁴ dx = (ax + 1)⁵/10 + C. Find a.",
                              "∫ from 0 to k of 2x(x² + 1)³ dx = 255/4, with k > 0. Find k.",
                              "dy/dx = x eˣ and y = 3 when x = 0. Find y.",
                              "Find the smallest k > 0 with ∫ from 0 to k of cos 2x dx = ½."],
         "16. k = 1 ([x eˣ − eˣ] gives (k − 1)eᵏ + 1 = 1)   17. a = 2 (1/(5a) = 1/10)   "
         "18. k = √3 (((k² + 1)⁴ − 1)/4 = 255/4, so k² + 1 = 4)   19. y = (x − 1)eˣ + 4 (−1 + C = 3)   "
         "20. k = π/4 (½ sin 2k = ½, so 2k = π/2)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.GREEN, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    pairs = [(x * sp.cos(x), x * sp.sin(x) + sp.cos(x)),
             (x * sp.exp(2 * x), x * sp.exp(2 * x) / 2 - sp.exp(2 * x) / 4),
             (x ** 2 * sp.exp(x), sp.exp(x) * (x ** 2 - 2 * x + 2)),
             ((2 * x - 5) ** 6, (2 * x - 5) ** 7 / 14),
             (6 * x * (x ** 2 + 4) ** 5, (x ** 2 + 4) ** 6 / 2),
             (sp.cos(x) * sp.exp(sp.sin(x)), sp.exp(sp.sin(x))),
             (x * sp.sin(x ** 2), -sp.cos(x ** 2) / 2),
             (sp.sin(5 * x), -sp.cos(5 * x) / 5)]
    ch.check([sp.simplify(sp.diff(F_, x) - f_) for f_, F_ in pairs], [0] * len(pairs))
    ch.check([sp.integrate(sp.log(x), (x, 1, sp.E)), sp.integrate(2 * x * (x ** 2 + 1) ** 3, (x, 0, 1))],
             [1, sp.Rational(15, 4)])
    pairs2 = [((5 * x - 2) ** 3, (5 * x - 2) ** 4 / 20), (sp.sin(3 * x + 1), -sp.cos(3 * x + 1) / 3),
              (sp.exp(-2 * x), -sp.exp(-2 * x) / 2), (1 / (4 * x + 1), sp.log(4 * x + 1) / 4)]
    ch.check([sp.simplify(sp.diff(F_, x) - f_) for f_, F_ in pairs2], [0] * len(pairs2))
    k = sp.Symbol("k", positive=True)
    a, C_ = sp.symbols("a C")
    I16 = sp.integrate(x * sp.exp(x), (x, 0, k))
    ch.check(sp.simplify(I16 - ((k - 1) * sp.exp(k) + 1)), 0)
    ch.check(sp.solve(I16 - 1, k), [1])
    ch.check(sp.solve(sp.diff((a * x + 1) ** 5 / 10, x).subs(x, 0) - 1, a), [2])
    ch.check(sp.solve(sp.integrate(2 * x * (x ** 2 + 1) ** 3, (x, 0, k)) - sp.Rational(255, 4), k), [sp.sqrt(3)])
    F19 = sp.integrate(x * sp.exp(x), x)
    c19 = sp.solve(F19.subs(x, 0) + C_ - 3, C_)[0]
    ch.check(sp.simplify(F19 + c19 - ((x - 1) * sp.exp(x) + 4)), 0)
    ch.check(sp.integrate(sp.cos(2 * x), (x, 0, sp.pi / 4)), sp.Rational(1, 2))
    ch.check(sp.solve(sp.sin(2 * k) / 2 - sp.Rational(1, 2), k)[0], sp.pi / 4)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    recap(ch)
    products(ch)
    derivation(ch)
    first(ch)
    choosing(ch)
    twice(ch)
    log_case(ch)
    definite(ch)
    definite_trig(ch)
    rename(ch)
    partners(ch)
    limits(ch)
    linear(ch)
    which(ch)
    summary(ch)
    your_turn(ch)
