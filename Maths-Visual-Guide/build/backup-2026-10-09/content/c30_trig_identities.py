"""Chapter 30 - Trig identities and equations (Lecture 6). 'Always true' vs 'true only sometimes'.
sin^2 + cos^2 = 1 is Pythagoras on the unit circle. Solving means drawing a horizontal line across the
wave and catching every crossing (the Ferris wheel seat is at each height twice per turn). Then two
waves added together make one shifted wave: a sin + b cos = r sin(theta + alpha), finishing the
lecture's advanced question, including the second answer it asks you to find."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 30
NUM = 30
TITLE = "Trig identities and equations"
SHORT = "Identities & equations"
SLUG = "Trig-identities"
ACCENT = C.PINK
REQUIRES = ["identity", "equation-vs-expression", "sine", "cosine", "tangent", "unit-circle", "sine-graph",
            "cosine-graph", "tangent-graph", "inverse-trig", "pythagoras", "trig-any-angle", "period",
            "amplitude", "solve-equation", "radian", "exact-trig-values", "roots"]
INTRODUCES = ["trig-identity", "pythagorean-identity", "trig-equation", "all-solutions", "compound-angle",
              "r-sin-form"]

PAPER = "#fffafc"
D = math.radians


def icon(pg, x0, y0):
    pg.poly([(x0 + 1 + i * 0.85, y0 + 9 - 7 * math.sin(i * math.pi / 10)) for i in range(21)], C.PINK, 1.5)
    pg.line(x0 + 1, y0 + 5, x0 + 18, y0 + 5, C.PINK, 1)


def sec(f, t_, **kw):
    section(f, t_, C.PINK, icon, **kw)


def deg_axes(pg, x, y, w_, h_, yr=(-1.3, 1.3), x0=0, x1=360, step_=90, ys=0.5):
    ax = Axes(pg, x, y, w_, h_, (x0, x1), yr)
    ax.grid(step_ / 2, ys)
    ax.axes(None, None, step_, ys, size=8)
    return ax


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 30, "Trig identities and equations", "always true, or only sometimes?", C.PINK, PAPER)
    for k, (s_, lat, col, why) in enumerate([
            ("ALWAYS TRUE", r"\sin^2\theta+\cos^2\theta=1", C.GREEN, "try any angle you like"),
            ("SOMETIMES TRUE", r"\sin\theta=0.5", C.ORANGE, "only at 30°, 150°, 390°...")]):
        x0 = L + k * 250
        pg.rect(x0, 200, 230, 110, col, 1.6, fillcolor=C.LIGHT[col], r=10)
        pg.text(x0 + 115, 210, s_, 14, col, F.BOLD, align="center")
        pg.eq(x0 + 115, 255, lat, 20, align="center", valign="middle")
        pg.note(x0 + 20, 280, why, col, 15)
    f = ch.flow(top=350)
    f.p("Some trig statements hold for {B:every} angle: these are {B:identities}, tools you can swap in "
        "whenever convenient. Others hold only for {B:particular} angles: these are {B:equations}, "
        "puzzles to solve.", 14, gap=10)
    f.p("The big idea for equations: trig waves repeat, so an equation usually has {B:many} answers, "
        "and your calculator only tells you one of them. We'll catch them all with a picture.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 6} {y:(cos² + sin² = 1, multiple values, r sin(θ + α), the advanced "
        "question).}", 12.5)


def identity(ch):
    f = flow(ch)
    sec(f, "sin² + cos² = 1 is Pythagoras on the circle")
    f.p("On the unit circle (Chapter 29) the point at angle $\\theta$ is $(\\cos\\theta, \\sin\\theta)$, "
        "and every point on it obeys $x^2 + y^2 = 1$. Swap in $x = \\cos\\theta$, $y = \\sin\\theta$:",
        14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    cx, cy, r = L + 90, y_ + 75, 65
    pg.circle(cx, cy, r, C.GREY, 1)
    px, py = cx + r * math.cos(D(40)), cy - r * math.sin(D(40))
    pg.fillpoly([(cx, cy), (px, cy), (px, py)], C.LIGHT[C.PINK])
    pg.poly([(cx, cy), (px, cy), (px, py)], C.INK, 1.4, closed=True)
    pg.text(px + 4, (py + cy) / 2 - 6, "sin θ", 10, C.ORANGE, F.BOLD)
    pg.text((cx + px) / 2, cy + 3, "cos θ", 10, C.TEAL, F.BOLD, align="center")
    pg.text((cx + px) / 2 - 12, (cy + py) / 2 - 16, "1", 11, C.PURPLE, F.BOLD)
    pg.eq(L + 200, y_ + 30, r"(\cos\theta)^2+(\sin\theta)^2=1^2", 20)
    pg.eq(L + 200, y_ + 80, r"\cos^2\theta+\sin^2\theta=1", 22, C.PINK)
    pg.note(L + 200, y_ + 116, "short sides squared, added = hypotenuse squared", C.GREY, 14)
    ch.check(sp.simplify(sp.sin(sp.Symbol("t")) ** 2 + sp.cos(sp.Symbol("t")) ** 2), 1)
    ch.formula(r"\sin^2\theta+\cos^2\theta=1", "Pythagorean identity")
    ch.term("trig identity", "a trig statement that is true for every angle, e.g. sin²θ + cos²θ = 1")
    ch.term("Pythagorean identity", "sin²θ + cos²θ = 1: Pythagoras on the unit circle")
    ch.symbol(r"\sin^2\theta", "sine squared theta", "(sin θ)², the sine worked out first, then squared")
    f.p("{b:Notation:} $\\sin^2\\theta$ means $(\\sin\\theta)^2$: work out the sine, then square it. It does "
        "{B:not} mean $\\sin(\\theta^2)$. (Lecture 6 writes \"cos 25² + sin 25² = 1\", which you should "
        "read as $\\cos^2 25^\\circ + \\sin^2 25^\\circ$.)", 14, gap=8)
    y_ = f.reserve(60)
    pg = f.pg
    for k, a in enumerate([25, 550, -73]):
        x0 = L + k * 165
        c, s_ = math.cos(D(a)), math.sin(D(a))
        pg.text(x0, y_, f"θ = {a}°", 12, C.PINK, F.BOLD)
        pg.text(x0, y_ + 18, f"({c:.4f})² + ({s_:.4f})²", 9, C.INK, F.MONO)
        pg.text(x0, y_ + 34, f"{c * c:.4f} + {s_ * s_:.4f} = 1 ✓", 9, C.GREEN, F.MONO)
        ch.check_num(c * c + s_ * s_, 1)
    f.p("{b:Using it:} if $\\sin\\theta = \\frac35$ (and $\\theta$ is acute), then $\\cos^2\\theta = 1 - "
        "\\frac{9}{25} = \\frac{16}{25}$, so $\\cos\\theta = \\frac45$. No angle needed. (It's the 3-4-5 "
        "triangle in disguise.) Dividing the identity by $\\cos^2\\theta$ also shows $\\tan\\theta = "
        "\\frac{\\sin\\theta}{\\cos\\theta}$ fits in: $\\tan^2\\theta + 1 = \\frac{1}{\\cos^2\\theta}$.", 14)
    ch.check(sp.sqrt(1 - sp.Rational(9, 25)), sp.Rational(4, 5))


def solving(ch):
    f = flow(ch)
    sec(f, "Solving: catch every crossing", room=560)
    f.p("{B:Solve $\\sin\\theta = 0.5$ for $0^\\circ \\le \\theta \\le 360^\\circ$.} The calculator's "
        "$\\sin^{-1}(0.5)$ says 30°. But the Ferris-wheel seat is at height 0.5 {B:twice} per turn: once "
        "going up, once coming down. Draw the line $y = 0.5$ across the wave:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    ax = deg_axes(pg, L + 30, y_ + 10, 440, 120)
    ax.curve(lambda d: math.sin(D(d)), 0, 360, C.RED, 2)
    ax.hline(0.5, C.PINK, 1.4, None)
    for d in (30, 150):
        ax.dot(d, 0.5, C.PINK, 4)
        ax.vline(d, C.PINK, 0.8, (3, 2), 0, 0.5)
        pg.text(ax.X(d), ax.Y(0) + 14, f"{d}°", 11, C.PINK, F.BOLD, align="center", solid=False)
    pg.note(ax.X(200), ax.Y(0.95), "same height, mirror\nimage: 180° − 30°", C.PINK, 14, solid=False)
    ch.check(sorted(sp.solveset(sp.Eq(sp.sin(sp.Symbol("x")), sp.Rational(1, 2)), sp.Symbol("x"),
                                sp.Interval(0, 2 * sp.pi)), key=float), [sp.pi / 6, 5 * sp.pi / 6])
    ch.term("trig equation", "a statement like sin θ = 0.5 that is true only for particular angles")
    f.p("The second answer comes from the wave's symmetry. Each function has its own partner rule "
        "(within one turn):", 14, gap=10)
    y_ = f.reserve(80)
    pg = f.pg
    rules = [("sin", "θ and 180° − θ", "the wave is symmetric about 90°", C.RED),
             ("cos", "θ and 360° − θ", "the wave is symmetric about 180°", C.TEAL),
             ("tan", "θ and θ + 180°", "tan repeats every 180°", C.GREEN)]
    for k, (fn, rule, why, col) in enumerate(rules):
        yy = y_ + k * 24
        pg.text(L + 10, yy, fn, 13, col, F.BOLD)
        pg.text(L + 60, yy, rule, 13, C.INK, F.BOLD)
        pg.note(L + 220, yy - 2, why, C.GREY, 14)
    ch.term("all solutions", "trig equations have many answers: find the calculator's one, its partner, then add or subtract whole turns")
    f.p("Then add or subtract {B:whole turns} (360°) to reach any other range. So $\\sin\\theta = 0.5$ "
        "also has $390^\\circ, 510^\\circ, -210^\\circ, \\dots$", 14, gap=10)
    f.p("{b:Lecture 6's example:} $\\cos^{-1}(-1)$. The calculator says 180° ($\\pi$). But cos touches "
        "$-1$ at the bottom of {B:every} dip: $\\theta = \\pi, 3\\pi, -\\pi, -3\\pi, \\dots$, i.e. $180^\\circ, "
        "540^\\circ, -180^\\circ, -540^\\circ$.", 14)


def harder(ch):
    f = flow(ch)
    sec(f, "A harder one, step by step", room=440)
    f.p("{B:Solve $5\\cos\\theta + 2 = 0$ for $0^\\circ \\le \\theta \\le 360^\\circ$.}", 14, gap=6)
    step(f, r"5\cos\theta=-2", "− 2 both sides", size=19)
    step(f, r"\cos\theta=-0.4", "÷ 5: get the cos on its own first", size=19)
    step(f, r"\theta=\cos^{-1}(-0.4)=113.58^\circ", "calculator (one answer)", size=19)
    step(f, r"\theta=360^\circ-113.58^\circ=246.42^\circ", "cos partner rule", size=19, color=C.GREEN)
    ch.check_num(math.degrees(math.acos(-0.4)), 113.58, tol=0.005)
    y_ = f.reserve(130)
    pg = f.pg
    ax = deg_axes(pg, L + 30, y_ + 10, 300, 100)
    ax.curve(lambda d: math.cos(D(d)), 0, 360, C.TEAL, 2)
    ax.hline(-0.4, C.PINK, 1.3, None)
    for d in (113.58, 246.42):
        ax.dot(d, -0.4, C.PINK, 4)
    pg.note(L + 350, y_ + 20, "two crossings,\nmirror images\nabout 180°", C.PINK, 15)
    ch.check_num(math.cos(D(246.42)), -0.4, tol=0.0002)
    f.p("{G:Check:} $5\\cos246.42^\\circ + 2 = 5(-0.4) + 2 = 0$ ✓.", 13.5)


def combine(ch):
    f = flow(ch)
    sec(f, "Two waves make one: r sin(θ + α)", room=560)
    f.p("Add a sine wave and a cosine wave, $2\\sin\\theta + 3\\cos\\theta$, and something lovely happens: "
        "the result is {B:a single sine wave}, just taller and shifted:", 14, gap=10)
    y_ = f.reserve(170)
    pg = f.pg
    ax = deg_axes(pg, L + 30, y_ + 10, 440, 150, yr=(-4, 4), ys=1)
    ax.curve(lambda d: 2 * math.sin(D(d)), 0, 360, C.RED, 1.2, dash=(4, 3))
    ax.curve(lambda d: 3 * math.cos(D(d)), 0, 360, C.TEAL, 1.2, dash=(4, 3))
    ax.curve(lambda d: 2 * math.sin(D(d)) + 3 * math.cos(D(d)), 0, 360, C.PINK, 2.4)
    ax.label(250, -2.0, "{R:2 sin θ}", 10, dx=6, dy=4)
    ax.label(0, 3, "{T:3 cos θ}", 10, dx=6, dy=2)
    ax.label(33.7, 3.6, "{P:the sum: height √13 ≈ 3.61}", 10, dx=8, dy=-14)
    ch.check_num(max(2 * math.sin(D(d / 10)) + 3 * math.cos(D(d / 10)) for d in range(3600)), math.sqrt(13),
                 tol=0.001)
    f.p("Lecture 6 writes $a\\sin\\theta + b\\cos\\theta = r\\sin(\\theta + \\alpha)$, with", 14, gap=6)
    y_ = f.reserve(130)
    pg = f.pg
    pg.eq(L + 20, y_ + 10, r"r=\sqrt{a^2+b^2}", 20, C.PINK)
    pg.eq(L + 20, y_ + 56, r"\alpha=\tan^{-1}\frac ba", 20, C.PINK)
    ox, oy = L + 290, y_ + 95
    pg.fillpoly([(ox, oy), (ox + 120, oy), (ox + 120, oy - 80)], C.LIGHT[C.PINK])
    pg.poly([(ox, oy), (ox + 120, oy), (ox + 120, oy - 80)], C.INK, 1.4, closed=True)
    pg.text(ox + 60, oy + 3, "a", 12, C.RED, F.BOLD, align="center")
    pg.text(ox + 125, oy - 46, "b", 12, C.TEAL, F.BOLD)
    pg.text(ox + 44, oy - 62, "r", 12, C.PINK, F.BOLD)
    pg.arc(ox, oy, 22, 0, math.degrees(math.atan2(80, 120)), C.PURPLE, 1.3)
    pg.text(ox + 26, oy - 18, "α", 11, C.PURPLE, F.BOLD)
    pg.note(ox - 30, oy + 16, "a and b as the sides of a right triangle", C.GREY, 13)
    ch.formula(r"a\sin\theta+b\cos\theta=r\sin(\theta+\alpha),\ r=\sqrt{a^2+b^2},\ \alpha=\tan^{-1}\frac ba", "r sin form")
    ch.term("r sin(θ + α) form", "a sin θ + b cos θ rewritten as one wave r sin(θ + α), r = √(a² + b²), tan α = b/a")
    f.p("{b:Why?} There's a standard identity for the sine of a sum (the {B:compound angle formula}):", 14,
        gap=6)
    step(f, r"\sin(\theta+\alpha)=\sin\theta\cos\alpha+\cos\theta\sin\alpha", "", size=18)
    x, a_ = sp.symbols("x a")
    ch.check(sp.simplify(sp.expand_trig(sp.sin(x + a_)) - (sp.sin(x) * sp.cos(a_) + sp.cos(x) * sp.sin(a_))), 0)
    ch.term("compound angle formula", "sin(A + B) = sin A cos B + cos A sin B")
    f.p("Multiply by $r$ and match with $a\\sin\\theta + b\\cos\\theta$: we need $r\\cos\\alpha = a$ and "
        "$r\\sin\\alpha = b$. Those are exactly the sides of the triangle above (CAH and SOH with "
        "hypotenuse $r$), and Pythagoras gives $r$. Lecture 6 notes this is the same move as going from "
        "$(x, y)$ to polar coordinates (Chapter 33).", 14, gap=10)
    f.need(250)
    f.p("{R:Watch the signs.} $r\\cos\\alpha = a$ and $r\\sin\\alpha = b$ say that $\\alpha$ is the "
        "angle of the {B:point $(a, b)$}. When $a$ and $b$ are both positive that point is in quadrant 1 "
        "and $\\tan^{-1}\\frac ba$ is right. When $a$ is {B:negative}, the calculator still answers in "
        "the right-hand half, so it points the wrong way:", 14, gap=6)
    y_ = f.reserve(162)
    pg = f.pg
    cx, cy, u = L + 130, y_ + 80, 20
    pg.line(cx - 90, cy, cx + 90, cy, C.GREY, 1)
    pg.line(cx, cy - 75, cx, cy + 70, C.GREY, 1)
    for (px, py, col, lab, dash) in [(2, 3, C.PINK, "(2, 3)", None), (-2, 3, C.RED, "(−2, 3)", None),
                                      (2, -3, C.GREY, "calculator's (2, −3)", (4, 3))]:
        pg.line(cx, cy, cx + px * u, cy - py * u, col, 1.8, dash=dash)
        pg.dot(cx + px * u, cy - py * u, 3.5, col)
        pg.text(cx + px * u + (6 if px > 0 else -8), cy - py * u - 8, lab, 11, col, F.BOLD,
                align="left" if px > 0 else "right")
    pg.arc(cx, cy, 16, 0, 56.31, C.PINK, 1.3)
    pg.arc(cx, cy, 26, 0, 123.69, C.RED, 1.3)
    pg.note(L + 260, y_ + 6, "a = −2, b = 3:\ntan⁻¹(3 ÷ −2) = −56.31°\npoints to (2, −3). Wrong!\n"
            "(−2, 3) is in quadrant 2,\nso add 180°:  α = 123.69°", C.RED, 14)
    for a0, b0, al in [(2, 3, 56.31), (-2, 3, 123.69)]:
        ch.check_num(math.sqrt(13) * math.cos(D(al)), a0, tol=0.001)
        ch.check_num(math.sqrt(13) * math.sin(D(al)), b0, tol=0.001)
    ch.check_num(math.degrees(math.atan(3 / -2)) + 180, 123.69, tol=0.005)
    f.p("So: {B:sketch the point $(a, b)$ first}. If $a < 0$ (quadrants 2 and 3), add $180^\\circ$ to the "
        "calculator's answer. Chapter 33 builds this {B:quadrant fix} properly for polar coordinates; "
        "it's exactly the same job.", 14)


def advanced(ch):
    f = flow(ch)
    sec(f, "Lecture 6's advanced question, both answers", room=560)
    f.p("{B:Solve $2\\sin\\theta + 3\\cos\\theta = 2$ for $0^\\circ \\le \\theta \\le 360^\\circ$.}", 14, gap=6)
    step(f, r"r=\sqrt{2^2+3^2}=\sqrt{13},\quad\alpha=\tan^{-1}\tfrac32=56.31^\circ", "a = 2, b = 3", size=17)
    step(f, r"\sqrt{13}\,\sin(\theta+56.31^\circ)=2", "one wave now", size=18)
    step(f, r"\sin(\theta+56.31^\circ)=\frac{2}{\sqrt{13}}=0.5547", "÷ √13", size=18)
    ch.check_num(math.degrees(math.atan(1.5)), 56.31, tol=0.005)
    f.p("Treat the whole bracket as one angle, call it $\\phi$ (\"fie\"). The calculator gives "
        "$\\phi = 33.69^\\circ$; the sin partner is $180^\\circ - 33.69^\\circ = 146.31^\\circ$:", 14, gap=6)
    step(f, r"\theta+56.31=33.69\ \Rightarrow\ \theta=-22.62^\circ\to337.38^\circ", "+ 360° to get into range",
         size=17)
    step(f, r"\theta+56.31=146.31\ \Rightarrow\ \theta=90^\circ", "the one the slide asks you to find", size=17,
         color=C.GREEN)
    ch.check_num(math.degrees(math.asin(2 / math.sqrt(13))), 33.69, tol=0.005)
    for th in (90, 337.38):
        ch.check_num(2 * math.sin(D(th)) + 3 * math.cos(D(th)), 2, tol=0.001)
    y_ = f.reserve(130)
    pg = f.pg
    ax = deg_axes(pg, L + 30, y_ + 10, 330, 110, yr=(-4, 4), ys=1)
    ax.curve(lambda d: 2 * math.sin(D(d)) + 3 * math.cos(D(d)), 0, 360, C.PINK, 2)
    ax.hline(2, C.ORANGE, 1.3, None)
    for d in (90, 337.38):
        ax.dot(d, 2, C.ORANGE, 4)
    pg.note(L + 380, y_ + 20, "the line y = 2\ncrosses the wave\nat 90° and 337.38°", C.ORANGE, 14)
    f.p("{G:Check} 90°: $2\\sin90^\\circ + 3\\cos90^\\circ = 2(1) + 3(0) = 2$ ✓. Easy to miss, which is exactly "
        "why the lecture asks.", 13.5)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Range 0° to 360° unless stated. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Identities", ["If cos θ = 5/13 (θ acute), find sin θ", "Simplify 3 sin²x + 3 cos²x",
                        "Is sin(2θ) = 2 sin θ an identity? Test θ = 90°."],
         "1. 12/13   2. 3   3. no: sin 180° = 0 but 2 sin 90° = 2"),
        ("Equations", ["sin θ = 0.8", "cos θ = 0.5", "tan θ = 1", "2 sin θ + 1 = 0"],
         "4. 53.13°, 126.87°   5. 60°, 300°   6. 45°, 225°   7. 210°, 330°"),
        ("r sin form", ["Write 3 sin θ + 4 cos θ as r sin(θ + α)", "Hence the largest value of 3 sin θ + 4 cos θ",
                        "Solve 3 sin θ + 4 cos θ = 5"],
         "8. 5 sin(θ + 53.13°)   9. 5   10. θ + 53.13 = 90, so θ = 36.87°"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.PINK, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(sp.sqrt(1 - sp.Rational(25, 169)), sp.Rational(12, 13))
    ch.check_num(math.degrees(math.asin(0.8)), 53.13, tol=0.005)
    ch.check_num(math.sin(D(210)), -0.5)
    ch.check_num(3 * math.sin(D(36.87)) + 4 * math.cos(D(36.87)), 5, tol=0.0001)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    identity(ch)
    solving(ch)
    harder(ch)
    combine(ch)
    advanced(ch)
    your_turn(ch)
