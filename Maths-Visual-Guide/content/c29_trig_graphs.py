"""Chapter 29 - Trig functions and their graphs (Lecture 6). The unit circle turns sin and cos into
coordinates; a Ferris wheel comic strip unrolls the circle into a sine wave; cos is the same ride seen
side-on; tan explodes where cos is zero; bigger and faster wheels change amplitude and period (the
London Eye); and the lecture's power series shows how a calculator actually works out sin 1."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step, title_block

ORDER = 29
NUM = 29
TITLE = "Trig functions and their graphs"
SHORT = "Trig graphs"
SLUG = "Trig-graphs"
ACCENT = C.BLUE
REQUIRES = ["sine", "cosine", "tangent", "radian", "degrees", "coordinates", "graph-of-function", "even-function",
            "odd-function", "asymptote", "graph-transformations", "circle-equation", "anticlockwise-positive",
            "exact-trig-values", "series", "sigma-notation", "hypotenuse"]
INTRODUCES = ["unit-circle", "trig-any-angle", "sine-graph", "cosine-graph", "tangent-graph", "period",
              "amplitude", "trig-transformations", "factorial", "power-series", "cast-rule", "reference-angle"]

PAPER = "#f9fbff"
PI = math.pi


def icon(pg, x0, y0):
    pg.poly([(x0 + 1 + i * 0.85, y0 + 9 - 7 * math.sin(i * PI / 10)) for i in range(21)], C.BLUE, 1.6)


def sec(f, t_, **kw):
    section(f, t_, C.BLUE, icon, **kw)


def P(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def wheel(pg, cx, cy, r, deg, seat=True, spokes=8, col=C.BLUE):
    pg.circle(cx, cy, r, col, 1.2)
    for k in range(spokes):
        pg.line(cx, cy, *P(cx, cy, r, k * 360 / spokes), C.LIGHT[col] if col in C.LIGHT else C.GREY, 0.6)
    pg.line(cx - r * 0.5, cy + r * 1.25, cx, cy, C.GREY, 1)
    pg.line(cx + r * 0.5, cy + r * 1.25, cx, cy, C.GREY, 1)
    if seat:
        sx, sy = P(cx, cy, r, deg)
        pg.line(cx, cy, sx, sy, C.RED, 1.4)
        pg.rect(sx - 4, sy - 1, 8, 7, C.RED, 1, fillcolor=C.RED)
        return sx, sy


def trig_axes(pg, x, y, w_, h_, yr=(-1.3, 1.3), xmax=2 * PI, ticks=True):
    ax = Axes(pg, x, y, w_, h_, (0, xmax), yr)
    ax.grid(PI / 2, 0.5)
    ax.axes(None, None, 0, 0.5 if yr[1] < 3 else 1, size=8)
    if ticks:
        labs = ["π/2", "π", "3π/2", "2π", "5π/2", "3π", "7π/2", "4π"]
        for k in range(1, int(xmax / (PI / 2) + 0.01) + 1):
            X = ax.X(k * PI / 2)
            pg.line(X, ax.Y(0) - 3, X, ax.Y(0) + 3, C.INK, 1)
            pg.text(X, ax.Y(0) + 4, labs[k - 1], 8, C.GREY, align="center", solid=False)
    return ax


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 29, "Trig functions and their graphs", "ride the Ferris wheel", C.BLUE, PAPER)
    cx, cy, r = L + 70, 250, 50
    sx, sy = wheel(pg, cx, cy, r, 40)
    ax = trig_axes(pg, L + 170, 200, 300, 100, ticks=False)
    ax.curve(math.sin, 0, 2 * PI, C.RED, 2)
    pg.line(sx, sy, ax.X(math.radians(40)), sy, C.RED, 0.8, dash=(3, 2))
    ax.dot(math.radians(40), math.sin(math.radians(40)), C.RED, 3.5)
    pg.note(L + 180, 310, "your seat's height, turn by turn, draws a wave", C.RED, 15)
    f = ch.flow(top=360)
    f.p("In Chapter 28, sin, cos and tan lived inside right-angled triangles, so the angle had to be "
        "less than 90°. But angles can be anything: 200°, −45°, ten full turns. This chapter frees sin, "
        "cos and tan from the triangle by putting them on a {B:circle}, and then watches them move.",
        14, gap=10)
    f.p("The star of the show is a Ferris wheel. Ride it, record your height, and you've drawn the "
        "sine graph. Everything about the graphs (the repeats, the heights, the shifts) is something "
        "about the wheel.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 6} {y:(the unit circle, sin, cos and tan graphs, period, amplitude, "
        "power series, odd and even functions).}", 12.5)


def unit_circle(ch):
    f = flow(ch)
    sec(f, "The unit circle: sin and cos become coordinates")
    rule_box(f, "trig of any angle", [
        "On the unit circle (radius 1), the point at angle $\\theta$ is $(\\cos\\theta,\\ \\sin\\theta)$: "
        "{B:cos is the x-coordinate, sin is the y-coordinate}, and $\\tan\\theta=\\dfrac{\\sin\\theta}{\\cos\\theta}$.",
        "This defines sin, cos and tan for {B:every} angle, not just those under $90^\\circ$.",
    ], C.BLUE)
    f.p("Draw a circle of radius 1 (the {B:unit circle}, $x^2 + y^2 = 1$ from Chapter 28). Walk "
        "anticlockwise from the east by an angle $\\theta$ and drop a line down to the x-axis. You've made "
        "a right-angled triangle with hypotenuse 1:", 14, gap=12)
    y_ = f.reserve(200)
    pg = f.pg
    cx, cy, r = L + 110, y_ + 100, 85
    pg.arrow(cx - r - 20, cy, cx + r + 25, cy, C.GREY, 1, head=5)
    pg.arrow(cx, cy + r + 10, cx, cy - r - 15, C.GREY, 1, head=5)
    pg.circle(cx, cy, r, C.BLUE, 1.4)
    th = 35
    px, py = P(cx, cy, r, th)
    pg.fillpoly([(cx, cy), (px, cy), (px, py)], C.LIGHT[C.BLUE])
    pg.line(cx, cy, px, py, C.PURPLE, 2)
    pg.line(px, py, px, cy, C.ORANGE, 2.4)
    pg.line(cx, cy, px, cy, C.TEAL, 2.4)
    pg.arc(cx, cy, 20, 0, th, C.RED, 1.3)
    pg.text(cx + 24, cy - 16, "θ", 11, C.RED, F.BOLD)
    pg.dot(px, py, 3.5, C.INK)
    pg.text(px + 6, py - 18, "(cos θ, sin θ)", 11, C.INK, F.BOLD)
    pg.text(cx + (px - cx) / 2 - 8, cy - (cy - py) / 2 - 18, "1", 11, C.PURPLE, F.BOLD)
    pg.text(px + 5, (py + cy) / 2 - 6, "sin θ", 10, C.ORANGE, F.BOLD)
    pg.text((cx + px) / 2, cy + 4, "cos θ", 10, C.TEAL, F.BOLD, align="center")
    pg.note(L + 285, y_ + 30, "SOH with hyp = 1: opp = sin θ.\nCAH with hyp = 1: adj = cos θ.\n\nSo the point "
            "on the circle is\n(cos θ, sin θ) (Lecture 6).\n\nNow let θ keep growing: the point\nkeeps going round, "
            "and its x and y\ndefine cos and sin for ANY angle.", C.INK, 14)
    ch.term("unit circle", "the circle of radius 1 centred at the origin; the point at angle θ is (cos θ, sin θ)")
    ch.term("trig of any angle", "cos θ and sin θ are the x- and y-coordinates of the point at angle θ on the unit circle")
    f.p("{b:Signs come free:} in the second quarter (90° to 180°) the point is left of the y-axis, so "
        "cos is {B:negative} while sin is still positive. E.g. $\\cos120^\\circ = -0.5$, "
        "$\\sin120^\\circ = 0.866$. And since the point is on $x^2 + y^2 = 1$:", 14, gap=6)
    ch.check_num(math.cos(math.radians(120)), -0.5)
    step(f, r"\cos^2\theta+\sin^2\theta=1", "Pythagoras on the circle (Chapter 30 uses it)", size=19,
         color=C.BLUE)


def quadrants(ch):
    f = flow(ch)
    sec(f, "Any angle: quadrant signs and the reference angle", room=600)
    rule_box(f, "the quadrant sign rule (CAST)", [
        "The four quadrants are numbered anticlockwise from east: Q1 is $0^\\circ$–$90^\\circ$, Q2 "
        "$90^\\circ$–$180^\\circ$, Q3 $180^\\circ$–$270^\\circ$, Q4 $270^\\circ$–$360^\\circ$.",
        "Which ratios are {B:positive}: Q1 {B:All}; Q2 only {B:Sin}; Q3 only {B:Tan}; Q4 only {B:Cos}. "
        "Memory aid, going round from Q1: \"{h:All Students Take Calculus}\". The rest are negative.",
        "The {B:reference angle} $\\alpha$ is the acute angle between the radius and the {B:x-axis}. "
        "sin, cos and tan of $\\theta$ are those of $\\alpha$, with the sign from CAST.",
    ], C.BLUE)
    rules_table(f, ["Quadrant", "θ is between", "Positive", "Ref. angle α", "θ from α"], [
        ["{B:Q1}", "0° and 90°", "all", "$\\alpha=\\theta$", "$\\theta=\\alpha$"],
        ["{B:Q2}", "90° and 180°", "sin", "$\\alpha=180^\\circ-\\theta$", "$180^\\circ-\\alpha$  ($\\pi-\\alpha$)"],
        ["{B:Q3}", "180° and 270°", "tan", "$\\alpha=\\theta-180^\\circ$", "$180^\\circ+\\alpha$  ($\\pi+\\alpha$)"],
        ["{B:Q4}", "270° and 360°", "cos", "$\\alpha=360^\\circ-\\theta$", "$360^\\circ-\\alpha$  ($2\\pi-\\alpha$)"],
    ], [70, 100, 65, 125, 135], C.BLUE, size=11.5)
    ch.term("CAST rule", "which trig ratios are positive in each quadrant: All (Q1), Sin (Q2), Tan (Q3), Cos (Q4)")
    ch.term("reference angle", "the acute angle between the radius and the x-axis; trig of θ = ± trig of it")
    y_ = f.reserve(180)
    pg = f.pg
    cx, cy, r = L + 105, y_ + 88, 72
    pg.arrow(cx - r - 18, cy, cx + r + 22, cy, C.GREY, 1, head=5)
    pg.arrow(cx, cy + r + 10, cx, cy - r - 14, C.GREY, 1, head=5)
    pg.circle(cx, cy, r, C.BLUE, 1.2)
    for qx, qy, s_, col in [(1, -1, "A", C.GREEN), (-1, -1, "S", C.ORANGE), (-1, 1, "T", C.GREEN),
                            (1, 1, "C", C.TEAL)]:
        pg.text(cx + qx * 40 - 9, cy + qy * 40 - 12, s_, 22, col, F.BOLD)
    px, py = P(cx, cy, r, 210)
    pg.line(cx, cy, px, py, C.RED, 2)
    pg.line(px, py, px, cy, C.ORANGE, 2)
    pg.dot(px, py, 3.5, C.RED)
    pg.arc(cx, cy, 16, 0, 210, C.GREY, 1.0, arrow=True)
    pg.arc(cx, cy, 30, 180, 210, C.RED, 1.6)
    pg.text(cx - 80, cy - 16, "α = 30°", 10, C.RED, F.BOLD)
    pg.text(px - 6, py + 4, "210°", 10, C.RED, F.BOLD, align="right")
    pg.note(L + 225, y_ + 6, "S, A, T, C: the ratios that are positive\nin each quadrant.\n\n"
            "210° is in Q3: the point is below the\naxis (sin < 0) and left of it (cos < 0).\n"
            "Its reference angle is 210° − 180° = 30°,\nso sin 210° = −sin 30° = −0.5.", C.INK, 14, w=R - L - 225)
    rule_box(f, "sin, cos or tan of any angle", [
        "Reduce the angle to between $0^\\circ$ and $360^\\circ$ (add or subtract $360^\\circ$).",
        "Find its quadrant.",
        "Find the reference angle $\\alpha$ (table above).",
        "Work out sin, cos or tan of $\\alpha$ (exact value or calculator).",
        "Attach the sign from CAST: $+$ if the ratio is positive in that quadrant, $-$ if not.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    step(f, r"\sin210^\circ=-\sin30^\circ=-\tfrac12", "Q3, α = 30°; sin is −", size=19)
    step(f, r"\cos300^\circ=+\cos60^\circ=\tfrac12", "Q4, α = 60°; cos is +", size=19)
    step(f, r"\tan135^\circ=-\tan45^\circ=-1", "Q2, α = 45°; tan is −", size=19)
    step(f, r"\cos(-120^\circ)=\cos240^\circ=-\cos60^\circ=-\tfrac12", "+360°, then Q3, α = 60°", size=18)
    ch.check(sp.sin(sp.Rational(7, 6) * sp.pi), -sp.Rational(1, 2))
    ch.check(sp.cos(sp.Rational(5, 3) * sp.pi), sp.Rational(1, 2))
    ch.check(sp.tan(sp.Rational(3, 4) * sp.pi), -1)
    ch.check(sp.cos(-sp.Rational(2, 3) * sp.pi), -sp.Rational(1, 2))
    f.p("{G:Check} on a calculator in DEG mode: $\\sin210^\\circ=-0.5$, $\\cos300^\\circ=0.5$, "
        "$\\tan135^\\circ=-1$. The method matters for exact answers and, in Chapter 30, for running the "
        "rule backwards to find every angle with a given sine.", 13.5)


def ferris(ch):
    f = flow(ch)
    sec(f, "The comic strip: unrolling the wheel", room=430)
    f.p("A wheel of radius 1. Start level with the hub (on the right) and turn anticlockwise. In each "
        "frame, note how high the seat is {B:above the hub}:", 14, gap=12)
    y_ = f.reserve(90)
    pg = f.pg
    frames = [0, 45, 90, 135, 180, 225, 270, 315, 360]
    for k, d in enumerate(frames):
        cx = L + 26 + k * 55
        wheel(pg, cx, y_ + 30, 20, d, spokes=4)
        pg.line(cx - 22, y_ + 30, cx + 22, y_ + 30, C.GREY, 0.4, dash=(2, 2))
        pg.text(cx, y_ + 62, f"{d}°", 9, C.INK, F.BOLD, align="center")
        pg.text(cx, y_ + 74, f"{math.sin(math.radians(d)):+.2f}".replace("+0.00", "0").replace("-0.00", "0"),
                9, C.RED, align="center")
    f.p("Plot each height above its angle, then join the dots smoothly:", 14, gap=10)
    y_ = f.reserve(170)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 440, 130, (0, 360), (-1.3, 1.3))
    ax.grid(45, 0.5)
    ax.axes(None, None, 45, 0.5, size=8)
    ax.curve(lambda d: math.sin(math.radians(d)), 0, 360, C.RED, 2.2)
    for d in frames:
        ax.dot(d, math.sin(math.radians(d)), C.RED, 3.6)
    pg.text(L + 474, ax.Y(0) - 16, "angle", 9, C.GREY)
    ax.label(90, 1, "{R:top of the wheel}", 10, dx=-40, dy=-20)
    ax.label(270, -1, "{R:bottom}", 10, dx=-20, dy=6)
    ch.check([sp.sin(sp.pi / 2), sp.sin(sp.pi), sp.sin(3 * sp.pi / 2)], [1, 0, -1])
    ch.term("sine graph", "the wave y = sin x: starts at 0, peaks at 1 (90°), back to 0 (180°), down to −1 (270°), 0 at 360°")
    f.p("That wave is the {B:graph of $y = \\sin\\theta$}. Keep riding and it repeats every turn, forever "
        "(and backwards for negative angles).", 14)


def sin_cos(ch):
    f = flow(ch)
    sec(f, "Two numbers describe a wave: period and amplitude", room=520)
    rule_box(f, "the sine and cosine graphs", [
        "$y=\\sin x$ and $y=\\cos x$ both have {B:period} $360^\\circ$ ($2\\pi$) and {B:amplitude} 1: "
        "they stay between $-1$ and $1$.",
        "sin starts at 0 going up; cos starts at its peak 1. cos is sin shifted $90^\\circ$ left: "
        "$\\cos x=\\sin(x+90^\\circ)$.",
        "cos is even: $\\cos(-x)=\\cos x$.  sin is odd: $\\sin(-x)=-\\sin x$.",
    ], C.BLUE)
    y_ = f.reserve(150)
    pg = f.pg
    ax = trig_axes(pg, L + 30, y_ + 10, 440, 120, xmax=4 * PI)
    ax.curve(math.sin, 0, 4 * PI, C.RED, 2)
    ax.seg(PI / 2, 0, PI / 2, 1, C.GREEN, 1.8)
    pg.text(ax.X(PI / 2) + 5, ax.Y(0.6), "amplitude 1", 10, C.GREEN, F.BOLD, solid=False)
    yy = ax.Y(-1.2)
    pg.arrow(ax.X(0), yy, ax.X(2 * PI), yy, C.PURPLE, 1.2, head=4, both=True)
    pg.text(ax.X(PI), yy - 14, "period 2π (one turn)", 10, C.PURPLE, F.BOLD, align="center", solid=False)
    ch.term("period", "the length of one complete cycle before a graph repeats")
    ch.term("amplitude", "the height of a wave's peak above its middle line")
    f.p("The {B:period} is how long before it repeats: one full turn, $2\\pi$ (360°). The {B:amplitude} is "
        "how high it rises above the middle: the wheel's radius, 1. (Lecture 6: sin has period $2\\pi$ and "
        "amplitude 1.)", 14, gap=10)
    f.p("{b:Cosine is the same ride seen from the side.} The seat's {B:sideways} position (its "
        "x-coordinate) starts at 1 (far right), so cos is the sine wave {B:shifted a quarter turn left}:",
        14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    ax = trig_axes(pg, L + 30, y_ + 10, 440, 120, xmax=4 * PI)
    ax.curve(math.sin, 0, 4 * PI, C.RED, 1.2, dash=(4, 3))
    ax.curve(math.cos, 0, 4 * PI, C.TEAL, 2.2)
    ax.label(0.1, 1, "{T:cos starts at the top}", 10, dx=4, dy=-18)
    ax.label(2.2 * PI, -1.05, "{R:sin (dashed)}", 10, dx=0, dy=6)
    ch.check(sp.simplify(sp.cos(sp.Symbol("x")) - sp.sin(sp.Symbol("x") + sp.pi / 2)), 0)
    ch.term("cosine graph", "the wave y = cos x: the sine wave shifted π/2 left; starts at its peak, 1")
    f.p("Same period ($2\\pi$) and amplitude (1). {b:Even and odd} (Chapter 19): cos is {B:even}, a mirror "
        "image either side of the y-axis ($\\cos(-x) = \\cos x$); sin is {B:odd}, it spins onto itself "
        "($\\sin(-x) = -\\sin x$).", 14)


def tan_graph(ch):
    f = flow(ch)
    sec(f, "Tan: the wave that explodes", room=440)
    rule_box(f, "the tangent graph", [
        "$\\tan x=\\dfrac{\\sin x}{\\cos x}$. It has {B:period} $180^\\circ$ ($\\pi$) and no amplitude (no top or bottom).",
        "Vertical {B:asymptotes} wherever $\\cos x=0$: $x=90^\\circ, 270^\\circ, \\dots$ ($\\frac{\\pi}{2}+k\\pi$).",
        "$y=\\tan(Bx)$ has period $\\dfrac{180^\\circ}{B}$, i.e. $\\dfrac{\\pi}{B}$.",
    ], C.BLUE)
    f.p("$\\tan\\theta = \\frac{\\sin\\theta}{\\cos\\theta}$ (opp/adj = (opp/hyp) ÷ (adj/hyp)). Whenever cos "
        "hits 0, at 90° and 270°, we'd be dividing by zero: the graph shoots off to infinity at "
        "{B:vertical asymptotes} (Chapter 19):", 14, gap=10)
    y_ = f.reserve(170)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 440, 150, (-PI / 2 - 0.2, 2 * PI + 0.2), (-4, 4))
    ax.grid(PI / 2, 1)
    ax.axes(None, None, 0, 1, size=8)
    for a, b in [(-PI / 2, PI / 2), (PI / 2, 3 * PI / 2), (3 * PI / 2, 5 * PI / 2)]:
        ax.curve(math.tan, a + 0.02, min(b - 0.02, 2 * PI + 0.2), C.GREEN, 2)
    for k in (-1, 1, 3):
        ax.vline(k * PI / 2, C.RED, 1, (4, 3))
    for k, lab in [(1, "π/2"), (2, "π"), (3, "3π/2"), (4, "2π")]:
        pg.text(ax.X(k * PI / 2) + 3, ax.Y(0) + 4, lab, 8, C.GREY, solid=False)
    pg.note(ax.X(PI / 2) + 6, ax.Y(3.8), "asymptote:\ncos = 0 here", C.RED, 13, solid=False)
    ch.check(sp.tan(sp.pi / 4), 1)
    ch.term("tangent graph", "y = tan x: repeats every π, with vertical asymptotes where cos x = 0 (90°, 270°, ...)")
    f.p("Tan repeats every $\\pi$ (180°), not $2\\pi$: Lecture 6 says period $\\pi$ and, jokingly, "
        "\"amplitude of ∞\" (it has no top). Tan is odd, like sin.", 14, gap=12)

    f.need(330)
    f.p("{b:Why is it called tan? A picture.} Draw the line that just {B:touches} the circle at $(1, 0)$: the "
        "upright line $x = 1$. A line that touches a circle is a {B:tangent} (Latin {h:tangere}, to touch). Now "
        "extend the radius until it hits that line:", 14, gap=8)
    y_ = f.reserve(236)
    pg = f.pg
    cx, cy, r = L + 60, y_ + 170, 80
    th = 40
    c_, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
    t_ = s_ / c_
    px, py = cx + r * c_, cy - r * s_
    tx, ty = cx + r, cy - r * t_
    pg.line(cx - 20, cy, cx + r + 40, cy, C.GREY, 1.0)
    pg.line(cx, cy + 30, cx, y_ + 10, C.GREY, 1.0)
    pg.arc(cx, cy, r, -20, 110, C.BLUE, 1.2)
    pg.line(cx + r, cy + 40, cx + r, y_ + 6, C.INK, 1.6)
    pg.text(cx + r + 4, y_ + 4, "touching line x = 1", 10, C.INK, F.BOLD)
    pg.fillpoly([(cx, cy), (tx, cy), (tx, ty)], C.LIGHT[C.GREEN])
    pg.fillpoly([(cx, cy), (px, cy), (px, py)], C.LIGHT[C.BLUE])
    pg.line(cx, cy, tx, ty, C.PURPLE, 1.8)
    pg.line(px, py, px, cy, C.ORANGE, 2.4)
    pg.line(cx, cy, px, cy, C.TEAL, 2.4)
    pg.line(tx, cy, tx, ty, C.GREEN, 3.0)
    pg.arc(cx, cy, r, 0, th, C.RED, 2.6)
    pg.arc(cx, cy, 16, 0, th, C.INK, 1.0)
    pg.text(cx + 18, cy - 14, "θ", 10, C.INK, F.BOLD)
    pg.dot(px, py, 3, C.INK)
    pg.dot(tx, ty, 3.5, C.GREEN)
    pg.text(px - 4, (py + cy) / 2 - 4, "sin θ", 10, C.ORANGE, F.BOLD, align="right")
    pg.text((cx + px) / 2, cy + 4, "cos θ", 10, C.TEAL, F.BOLD, align="center")
    pg.text(tx + 5, (ty + cy) / 2 - 2, "tan θ", 11, C.GREEN, F.BOLD)
    pg.text(tx + 5, cy + 4, "1", 10, C.INK, F.BOLD)
    pg.text(px - 8, py - 24, "arc = θ", 10, C.RED, F.BOLD, align="right")
    ch.check_num(t_ / 1, s_ / c_, 1e-12)
    # second picture: steeper and steeper
    cx2, cy2, r2 = L + 330, y_ + 196, 38
    H = 4.6
    pg.line(cx2 - 10, cy2, cx2 + r2 + 30, cy2, C.GREY, 1.0)
    pg.arc(cx2, cy2, r2, -10, 100, C.BLUE, 1.0)
    pg.line(cx2 + r2, cy2 + 10, cx2 + r2, cy2 - H * r2 - 6, C.INK, 1.4)
    for d_, col in [(45, C.GREEN), (65, C.ORANGE), (80, C.RED)]:
        tv = math.tan(math.radians(d_))
        if tv <= H:
            ex, ey = cx2 + r2, cy2 - r2 * tv
            pg.line(cx2, cy2, ex, ey, col, 1.4)
            pg.dot(ex, ey, 3, col)
            pg.text(ex + 4, ey - 7, f"{d_}°: tan = {tv:.2f}", 10, col, F.BOLD)
        else:
            ex, ey = cx2 + r2 * H / tv, cy2 - r2 * H
            pg.arrow(cx2, cy2, ex, ey, col, 1.4, head=5)
            pg.text(ex + 8, ey - 4, f"{d_}°: tan = {tv:.1f},", 10, col, F.BOLD)
            pg.text(ex + 8, ey + 9, "off the top", 10, col, F.BOLD)
    pg.line(cx2, cy2, cx2, cy2 - H * r2, C.GREY, 1.2, dash=(4, 3))
    pg.note(cx2 - 100, cy2 - H * r2 + 10, "90°: the radius is\nparallel to the\ntouching line.\nThey never meet.",
            C.GREY, 13)
    pg.arrow(cx2 - 22, cy2 - H * r2 + 22, cx2 - 3, cy2 - H * r2 + 22, C.GREY, 1.0, head=4)
    ch.check([round(math.tan(math.radians(d_)), 2) for d_ in (45, 65)], [1.0, 2.14])
    f.p("The two shaded triangles are the same shape (same angle θ), one scaled up so its bottom is 1. So "
        "$\\frac{\\tan\\theta}{1} = \\frac{\\sin\\theta}{\\cos\\theta}$: {B:tan θ is the height where the radius "
        "line meets the touching line}, which is also the {B:slope} of the radius (rise ÷ run, Chapter 20). "
        "As the angle nears 90° the meeting point races up the line, and at 90° there is no meeting point: "
        "that's the asymptote. Past 90°, extend the radius backwards through the centre: it hits the "
        "touching line again, which is why tan repeats every half turn.", 14, gap=8)
    f.p("Notice three heights for the same angle: {O:sin θ} (shortest), the red {R:arc θ} (middle) and "
        "{G:tan θ} (tallest). Keep that order in mind; the recipes below will show it.", 14, gap=10)
    f.need(120)
    y_ = f.reserve(104)
    pg = f.pg
    machines = [("sin", C.ORANGE, "angle in (the distance walked round the unit circle)  →  the point's "
                 "HEIGHT out"),
                ("cos", C.TEAL, "angle in  →  the point's SIDEWAYS position out"),
                ("tan", C.GREEN, "angle in  →  where the radius line hits the touching line x = 1, i.e. the "
                 "radius's SLOPE (sin ÷ cos)")]
    bw = (W - 16) / 3
    for i, (nm, col, txt) in enumerate(machines):
        bx = L + i * (bw + 8)
        pg.rect(bx, y_, bw, 98, col, 1.3, fillcolor=C.LIGHT[col], r=8)
        pg.text(bx + 10, y_ + 6, nm, 15, col, F.BOLD)
        pg.text(bx + 10, y_ + 28, txt, 11, C.INK, w=bw - 20)


def wheels(ch):
    f = flow(ch)
    sec(f, "Bigger wheels, faster wheels", room=560)
    rule_box(f, "amplitude, period and shifts", [
        "For $y=A\\sin\\big(B(x-C)\\big)+D$ (the same for cos):",
        "{B:Amplitude} $=|A|$.  {B:Period} $=\\dfrac{360^\\circ}{B}=\\dfrac{2\\pi}{B}$.  {B:Shift} $C$ to the "
        "{B:right} (left if $C$ is negative).  {B:Midline} $y=D$.",
        "Maximum $=D+|A|$, minimum $=D-|A|$. A negative $A$ flips the wave upside down.",
        "For $y=\\tan(Bx)$ the period is $\\dfrac{180^\\circ}{B}=\\dfrac{\\pi}{B}$ (tan has no amplitude).",
    ], C.BLUE)
    ch.formula(r"y=A\sin(B(x-C))+D:\ \text{amplitude }|A|,\ \text{period }\frac{2\pi}{B},\ \text{shift }C,\ \text{midline }D",
               "general sine wave")
    f.p("Change the wheel, change the wave. For $y = A\\sin(Bx)$:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    ax = trig_axes(pg, L + 30, y_ + 10, 200, 120, yr=(-3.2, 3.2))
    ax.curve(math.sin, 0, 2 * PI, C.GREY, 1, dash=(3, 2))
    ax.curve(lambda v: 3 * math.sin(v), 0, 2 * PI, C.RED, 2)
    pg.text(L + 80, y_ + 138, "y = 3 sin x: radius 3, amplitude 3", 10, C.RED, F.BOLD, align="center")
    ax = trig_axes(pg, L + 270, y_ + 10, 200, 120, yr=(-1.4, 1.4))
    ax.curve(math.sin, 0, 2 * PI, C.GREY, 1, dash=(3, 2))
    ax.curve(lambda v: math.sin(2 * v), 0, 2 * PI, C.BLUE, 2)
    pg.text(L + 370, y_ + 138, "y = sin 2x: twice as fast, period π", 10, C.BLUE, F.BOLD, align="center")
    step(f, r"\text{amplitude}=A,\qquad\text{period}=\frac{2\pi}{B}", "", size=20, color=C.BLUE)
    ch.formula(r"y=A\sin(Bx):\ \text{amplitude }A,\ \text{period }\frac{2\pi}{B}", "stretching trig graphs")
    ch.term("trig transformations", "y = A sin(Bx) + D: A stretches the height, B squashes the period to 2π/B, D lifts it")
    f.p("Add a number $D$ on the end and the whole wave lifts up by $D$: the hub is higher off the "
        "ground.", 14, gap=10)
    f.p("{b:The London Eye:} radius 60 m, hub 70 m up, one turn every 30 minutes. You board at the "
        "{B:bottom}, so your height starts low: a flipped cosine.", 14, gap=6)
    step(f, r"h(t)=70-60\cos\!\left(\frac{2\pi t}{30}\right)", "t in minutes", size=19)
    step(f, r"h(10)=70-60\cos\!\left(\tfrac{2\pi}{3}\right)=70-60(-0.5)=100\text{ m}", "", size=18,
         color=C.GREEN)
    ch.check_num(70 - 60 * math.cos(2 * PI * 10 / 30), 100)
    y_ = f.reserve(110)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 5, 300, 90, (0, 60), (0, 140))
    ax.grid(5, 20)
    ax.axes(None, None, 10, 20, size=8)
    ax.curve(lambda t: 70 - 60 * math.cos(2 * PI * t / 30), 0, 60, C.BLUE, 2)
    ax.dot(10, 100, C.GREEN, 3.5)
    ax.hline(70, C.GREY, 0.8, (3, 3))
    pg.note(L + 350, y_ + 10, "minutes along the bottom,\nmetres up the side.\nHighest (130 m) at 15 min.",
            C.GREY, 14)
    ch.check(70 + 60, 130)
    f.gap(4)
    f.p("{b:Reading a formula:} $y=2\\sin\\big(3(x-20^\\circ)\\big)+1$.", 14, gap=6)
    step(f, r"\text{amplitude }2,\quad\text{period }\tfrac{360^\circ}{3}=120^\circ", "A = 2, B = 3", size=18)
    step(f, r"\text{shift }20^\circ\text{ right},\quad\text{midline }y=1", "C = 20°, D = 1", size=18)
    step(f, r"\max=1+2=3,\quad\min=1-2=-1", "D ± |A|", size=18, color=C.GREEN)
    xs = sp.Symbol("x")
    yv = [2 * math.sin(math.radians(3 * (d - 20))) + 1 for d in range(361)]
    ch.check_num(max(yv), 3, tol=1e-6)
    ch.check_num(min(yv), -1, tol=1e-6)
    ch.check(sp.periodicity(2 * sp.sin(3 * (xs - sp.pi / 9)) + 1, xs), sp.Rational(2, 3) * sp.pi)
    ch.check(sp.periodicity(sp.tan(3 * xs), xs), sp.pi / 3)
    f.p("And $y=\\tan3x$ repeats every $\\frac{180^\\circ}{3}=60^\\circ$ ($\\frac{\\pi}{3}$), with asymptotes "
        "$60^\\circ$ apart.", 14)


def read_graph(ch):
    f = flow(ch)
    sec(f, "Reading A, B and D off a graph", room=300)
    rule_box(f, "find A, B and D from a graph of y = A sin(Bx) + D", [
        "Read the {B:maximum} and {B:minimum} heights.",
        "Midline $D=\\dfrac{\\max+\\min}{2}$ (halfway). Amplitude $A=\\dfrac{\\max-\\min}{2}$ (half the height).",
        "Read the {B:period}: the distance from one peak to the next (or one full wave).",
        "$B=\\dfrac{360^\\circ}{\\text{period}}$ (or $\\dfrac{2\\pi}{\\text{period}}$ in radians).",
        "Check one point: at $x=0$, $y=A\\sin0+D=D$.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    y_ = f.reserve(170)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 300, 150, (0, 360), (-2, 6))
    ax.grid(45, 1)
    ax.axes(None, None, 90, 1, size=8)
    ax.curve(lambda d: 3 * math.sin(math.radians(2 * d)) + 2, 0, 360, C.BLUE, 2.2)
    ax.hline(5, C.GREEN, 0.9, (4, 3))
    ax.hline(-1, C.GREEN, 0.9, (4, 3))
    ax.hline(2, C.ORANGE, 0.9, (4, 3))
    ax.dot(45, 5, C.RED, 3.5)
    ax.dot(225, 5, C.RED, 3.5)
    yy = ax.Y(5.6)
    pg.arrow(ax.X(45), yy, ax.X(225), yy, C.PURPLE, 1.2, head=4, both=True)
    pg.text(ax.X(135), yy - 14, "one wave: 180°", 10, C.PURPLE, F.BOLD, align="center", solid=False)
    pg.note(L + 350, y_ + 12, "max 5, min −1\n(green lines)\n\norange line: halfway\n\npeaks at 45° and 225°",
            C.INK, 14, w=R - L - 350)
    step(f, r"D=\frac{5+(-1)}{2}=2,\qquad A=\frac{5-(-1)}{2}=3", "midline, then half the height", size=18)
    step(f, r"\text{period}=225^\circ-45^\circ=180^\circ\ \Rightarrow\ B=\frac{360^\circ}{180^\circ}=2", "", size=18)
    step(f, r"y=3\sin2x+2", "check x = 0: y = 2, on the midline ✓", size=20, color=C.GREEN)
    ch.check(sp.Rational(5 + (-1), 2), 2)
    ch.check(sp.Rational(5 - (-1), 2), 3)
    ch.check(sp.Rational(360, 225 - 45), 2)
    ch.check_num(3 * math.sin(math.radians(90)) + 2, 5)
    ch.check_num(3 * math.sin(math.radians(2 * 225)) + 2, 5)
    mistakes(f, [
        (r"\text{period of }\sin2x=720^\circ", r"\text{period}=\tfrac{360^\circ}{2}=180^\circ",
         "a bigger B squashes the wave: divide by B, don't multiply"),
        (r"A=\max=5", r"A=\tfrac{5-(-1)}{2}=3", "amplitude is measured from the midline, not from zero"),
    ])


def step_rule(ch):
    f = flow(ch)
    sec(f, "The engine inside sin and cos: one tiny step", room=620)
    f.p("A calculator can only add, subtract, multiply and divide. So how does it find sin 1? With a recipe "
        "made of powers (the {B:power series}, coming up). The recipe isn't magic: it grows out of one picture "
        "of the point walking round the unit circle. Two facts set it up.", 14, gap=8)
    f.p("{b:1. In radians, the angle IS the distance walked.} A radian is one radius of string laid on the rim "
        "(Chapter 27). On a circle of radius 1, turning by $\\theta$ radians moves the point exactly $\\theta$ "
        "along the rim. So a tiny extra turn $h$ moves it a distance $h$. (In degrees this fails, which is why "
        "the recipes need radians.)", 14, gap=8)
    f.p("{b:2. The point always moves at right angles to the radius}, along the line that touches the circle. "
        "Zoom in on one tiny step:", 14, gap=8)
    y_ = f.reserve(220)
    pg = f.pg
    cx, cy, r = L + 95, y_ + 125, 88
    th = 35
    c_, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
    px, py = cx + r * c_, cy - r * s_
    pg.line(cx - r - 12, cy, cx + r + 16, cy, C.GREY, 1.0)
    pg.line(cx, cy + r + 8, cx, cy - r - 12, C.GREY, 1.0)
    pg.circle(cx, cy, r, C.BLUE, 1.2)
    pg.line(cx, cy, px, py, C.PURPLE, 1.8)
    pg.arc(cx, cy, 18, 0, th, C.INK, 1.0)
    pg.text(cx + 21, cy - 14, "θ", 10, C.INK, F.BOLD)
    pg.text((cx + px) / 2 - 10, (cy + py) / 2 - 16, "1", 10, C.PURPLE, F.BOLD)
    L0 = 34
    ex, ey = px - L0 * s_, py - L0 * c_
    pg.line(px + 30 * s_, py + 30 * c_, px - 60 * s_, py - 60 * c_, C.GREY, 0.8, dash=(3, 3))
    pg.arrow(px, py, ex, ey, C.RED, 2.2, head=6)
    pg.dot(px, py, 3.2, C.INK)
    q = 7
    ux, uy = -c_, s_
    vx, vy = -s_, -c_
    pg.poly([(px + q * ux, py + q * uy), (px + q * ux + q * vx, py + q * uy + q * vy), (px + q * vx, py + q * vy)],
            C.INK, 0.8)
    pg.circle((px + ex) / 2, (py + ey) / 2, 26, C.RED, 0.8, dash=(3, 2))
    pg.text(ex - 6, ey - 16, "step h", 10, C.RED, F.BOLD, align="right")
    # magnified step triangle
    Sx, Sy, Hm = L + 330, y_ + 190, 150
    Ex, Ey = Sx - Hm * s_, Sy - Hm * c_
    Kx, Ky = Sx, Ey
    pg.fillpoly([(Sx, Sy), (Kx, Ky), (Ex, Ey)], C.LIGHT[C.RED])
    pg.line(Sx, Sy, Kx, Ky, C.ORANGE, 3.0)
    pg.line(Kx, Ky, Ex, Ey, C.TEAL, 3.0)
    pg.arrow(Sx, Sy, Ex, Ey, C.RED, 2.4, head=8)
    pg.rect(Kx - 9, Ky, 9, 9, C.GREY, 0.8)
    pg.arc(Sx, Sy, 26, 90, 90 + th, C.INK, 1.1)
    pg.text(Sx - 13, Sy - 44, "θ", 11, C.INK, F.BOLD)
    pg.text(Sx + 6, (Sy + Ky) / 2 - 18, "h cos θ\nUP: sin grows", 11, C.ORANGE, F.BOLD)
    pg.text((Kx + Ex) / 2, Ky - 34, "h sin θ\nLEFT: cos shrinks", 11, C.TEAL, F.BOLD, align="center")
    pg.text((Sx + Ex) / 2 - 16, (Sy + Ey) / 2 + 2, "h", 12, C.RED, F.BOLD, align="right")
    pg.text(Sx - 60, Sy + 6, "the step, magnified", 10, C.RED, F.BOLD)
    pg.arrow(cx + r + 20, y_ + 40, Sx - 110, y_ + 70, C.GREY, 1.0, bend=-0.2, head=5)
    f.p("The step is the radius turned a quarter turn, so it leans away from upright by the same $\\theta$ that "
        "the radius leans away from flat. Read the little triangle with SOHCAHTOA (hypotenuse $h$): the point "
        "rises by $h\\cos\\theta$ and slides left by $h\\sin\\theta$.", 14, gap=6)
    step(f, r"\org{\sin(\theta+h)}\approx\org{\sin\theta}+h\,\tea{\cos\theta}", "sin grows at the rate cos says",
         size=18)
    step(f, r"\tea{\cos(\theta+h)}\approx\tea{\cos\theta}-h\,\org{\sin\theta}", "cos shrinks at the rate sin says",
         size=18)
    tr, hh = math.radians(th), 1e-4
    ch.check_num((math.sin(tr + hh) - math.sin(tr)) / hh, math.cos(tr), 1e-4)
    ch.check_num((math.cos(tr + hh) - math.cos(tr)) / hh, -math.sin(tr), 1e-4)
    f.p("{B:That's the whole engine: sin grows at cos's rate, cos shrinks at sin's rate.} Each one drives the "
        "other. Everything else (the waves, the recipes, even Chapter 35's derivatives) comes out of this "
        "little triangle.", 14)


def leapfrog(ch):
    f = flow(ch)
    sec(f, "Building the recipe: leapfrog", room=620)
    f.p("Start at angle 0: the point is at $(1, 0)$, so $\\sin 0 = 0$ and $\\cos 0 = 1$. Now let the angle grow to "
        "$x$ and use the engine again and again, each round correcting the last. One tool: when something grows "
        "at a known {B:rate}, its total growth is the {B:area under the rate graph} (like a speed–time graph, "
        "where area = distance). The areas we'll need are all a fraction of a box:", 14, gap=8)
    rates = [(lambda t: 1.0, "rate 1", r"x", "box ÷ 1"),
             (lambda t: t, "rate t", r"\frac{x^2}{2}", "box ÷ 2"),
             (lambda t: t * t / 2, "rate t²/2", r"\frac{x^3}{2\cdot3}", "box ÷ 3"),
             (lambda t: t ** 3 / 6, "rate t³/(2·3)", r"\frac{x^4}{2\cdot3\cdot4}", "box ÷ 4")]
    y_ = f.reserve(170)
    pg = f.pg
    pw = (W - 12) / 4
    for i, (fn, lab, area, frac) in enumerate(rates):
        x0 = L + i * (pw + 4) + 8
        top = fn(1.0) * 1.35
        ax = Axes(pg, x0, y_ + 22, pw - 22, 80, (0, 1.25), (0, top))
        ax.fill_under(fn, 0, 1.0, C.ORANGE if i % 2 == 0 else C.TEAL)
        ax.axes(None, None, 0, 0, size=8)
        ax.curve(fn, 0, 1.2, C.INK, 1.8)
        pg.rect(ax.X(0), ax.Y(fn(1.0)), ax.X(1.0) - ax.X(0), ax.Y(0) - ax.Y(fn(1.0)), C.GREY, 1.0, dash=(3, 2))
        pg.text(ax.X(1.0), ax.Y(0) + 3, "x", 10, C.INK, F.BOLD, align="center")
        pg.text(x0 + (pw - 22) / 2, y_ + 2, lab, 11, C.INK, F.BOLD, align="center")
        pg.text(x0 + (pw - 22) / 2, y_ + 118, frac, 11, C.RED, F.BOLD, align="center")
        pg.eq(x0 + (pw - 22) / 2, y_ + 136, r"\text{area}=" + area, 12, C.INK, align="center")
        n = 4000
        num = sum(fn((k + 0.5) / n) for k in range(n)) / n
        ch.check_num(num, fn(1.0) / (i + 1), 1e-6)
    f.p("The triangle is obviously half its box. The next two (a third, a quarter) are Chapter 36's pyramid "
        "facts; for now, trust the pattern: {B:each new area is the box ÷ the next whole number}.", 13.5,
        C.BROWN, gap=10)
    f.p("{b:Now leapfrog.} sin feeds cos, cos feeds sin, and each round uses the latest guess:", 14, gap=8)
    y_ = f.reserve(312)
    pg = f.pg
    lx, rx, dy = L + 95, L + 285, 56
    pg.text(lx, y_, "cos", 14, C.TEAL, F.BOLD, align="center")
    pg.text(rx, y_, "sin", 14, C.ORANGE, F.BOLD, align="center")
    rows = [(lx, r"1", C.TEAL), (rx, r"x", C.ORANGE), (lx, r"1-\frac{x^2}{2}", C.TEAL),
            (rx, r"x-\frac{x^3}{2\cdot3}", C.ORANGE), (lx, r"1-\frac{x^2}{2}+\frac{x^4}{2\cdot3\cdot4}", C.TEAL)]
    why = ["sin grows by the area\nunder cos ≈ 1", "cos shrinks by the area\nunder sin ≈ x",
           "sin grows by the area\nunder 1 − x²/2", "cos shrinks by the area\nunder x − x³/6"]
    for k, (xx, lat, col) in enumerate(rows):
        yy = y_ + 26 + k * dy
        pg.eq(xx, yy + 14, lat, 15, col, align="center", valign="middle")
        if k < 4:
            nx = rows[k + 1][0]
            x1 = xx + (50 if xx == lx else -50)
            x2 = nx + (-60 if nx == rx else 70)
            pg.arrow(x1, yy + 22, x2, yy + dy + 8, C.GREY, 1.2, head=5)
            pg.note(L + 370 if xx == lx else L, yy + (26 if xx == lx else 0), why[k], nx == rx and C.ORANGE or C.TEAL, 12)
    xs = sp.Symbol("x")
    ch.check(sp.integrate(1 - xs ** 2 / 2, (xs, 0, xs)), xs - xs ** 3 / 6)
    ch.check(sp.integrate(xs - xs ** 3 / 6, (xs, 0, xs)), xs ** 2 / 2 - xs ** 4 / 24)
    f.p("Why the signs flip: cos {B:shrinks} by its area, so every correction to cos is subtracted, and that "
        "minus is carried into sin on the next round. Why only odd powers in sin and even ones in cos: each "
        "round raises the power by one and swaps sides.", 14, gap=8)
    f.p("{b:The bottoms are a pattern too:} 1, 2, 2×3, 2×3×4, ... Each round divides by the next whole number. "
        "That product has a name: $n!$ (\"$n$ factorial\") means multiply the whole numbers from $n$ down to 1, "
        "so $3! = 3\\times2\\times1 = 6$ and $5! = 120$. Carry on leapfrogging forever and you get:", 14, gap=6)
    ch.check([sp.factorial(3), sp.factorial(5), sp.factorial(7)], [6, 120, 5040])
    ch.term("factorial", "n! = n × (n − 1) × ... × 2 × 1; e.g. 4! = 24")
    ch.symbol(r"n!", "n factorial", "n × (n−1) × ... × 1")
    step(f, r"\sin x=x-\frac{x^3}{3!}+\frac{x^5}{5!}-\frac{x^7}{7!}+\dots", "x in radians!", size=20,
         color=C.ORANGE)
    step(f, r"\cos x=1-\frac{x^2}{2!}+\frac{x^4}{4!}-\frac{x^6}{6!}+\dots", "", size=20, color=C.TEAL)
    ch.check(sp.series(sp.sin(xs), xs, 0, 8).removeO(), xs - xs ** 3 / 6 + xs ** 5 / 120 - xs ** 7 / 5040)
    ch.check(sp.series(sp.cos(xs), xs, 0, 8).removeO(), 1 - xs ** 2 / 2 + xs ** 4 / 24 - xs ** 6 / 720)
    ch.formula(r"\sin x=x-\frac{x^3}{3!}+\frac{x^5}{5!}-\dots", "sine series")
    ch.formula(r"\cos x=1-\frac{x^2}{2!}+\frac{x^4}{4!}-\dots", "cosine series")
    ch.term("power series", "a function written as an endless sum of powers of x, like sin x = x − x³/3! + ...")
    f.p("And there's the order from the tan picture: $\\sin x = x - $ (something), so sin is a little {B:less} "
        "than the arc $x$.", 14)


def clipped(ax, fn, a, b, lim, color, width=2.0, dash=None):
    t, stepv, last = a, (b - a) / 400, a
    while t <= b and abs(fn(t)) <= lim:
        last = t
        t += stepv
    ax.curve(fn, a, last, color, width, dash=dash)
    return last


def series(ch):
    f = flow(ch)
    sec(f, "How does a calculator know sin 1?", room=500)
    f.p("It follows the recipe. Put $x = 1$ and watch the running total home in on the true value:", 14,
        gap=10)
    terms = [1, -1 / 6, 1 / 120, -1 / 5040]
    y_ = f.reserve(4 * 26 + 10)
    pg = f.pg
    tot = 0
    labs = ["1", "− 1/6", "+ 1/120", "− 1/5040"]
    for k, t_ in enumerate(terms):
        tot += t_
        yy = y_ + k * 26
        pg.text(L + 20, yy, f"add {labs[k]}", 13, C.INK)
        pg.text(L + 160, yy, f"{tot:.6f}", 13, C.BLUE, F.MONO)
        pg.rect(L + 260, yy + 2, 200 * tot / 1.05, 14, C.BLUE, 0.5, fillcolor=C.LIGHT[C.BLUE])
    pg.line(L + 260 + 200 * math.sin(1) / 1.05, y_ - 4, L + 260 + 200 * math.sin(1) / 1.05, y_ + 100, C.RED, 1,
            dash=(3, 2))
    pg.text(L + 262 + 200 * math.sin(1) / 1.05, y_ + 100, "sin 1 = 0.841471", 10, C.RED, F.BOLD)
    ch.check_num(sum(terms), math.sin(1), tol=0.00001)
    f.gap(8)
    f.p("Four terms already agree to 5 decimal places: Lecture 6's $\\sin(1) \\approx 0.841$. Only {B:odd} "
        "powers appear in sin (an odd function) and {B:even} ones in cos (an even function): that's where the "
        "names odd and even come from.", 14, gap=10)
    f.p("{b:Watch each term earn its place.} Here's the real sine wave (thick red) against the recipe cut off "
        "after 1, 2, 3 and 4 terms:", 14, gap=8)
    y_ = f.reserve(186)
    pg = f.pg
    ax = trig_axes(pg, L + 30, y_ + 10, 420, 150, yr=(-1.6, 1.6))
    ax.curve(math.sin, 0, 2 * PI, C.RED, 3.2)
    parts = [(lambda v: v, "x", C.GREY), (lambda v: v - v ** 3 / 6, "2 terms", C.ORANGE),
             (lambda v: v - v ** 3 / 6 + v ** 5 / 120, "3 terms", C.GREEN),
             (lambda v: v - v ** 3 / 6 + v ** 5 / 120 - v ** 7 / 5040, "4 terms", C.BLUE)]
    for fn, lab, col in parts:
        end_ = clipped(ax, fn, 0, 2 * PI, 1.55, col, 1.6)
        ax.label(end_, fn(end_), f"{{{'n' if col == C.GREY else {C.ORANGE: 'o', C.GREEN: 'g', C.BLUE: 'b'}[col]}:{lab}}}",
                 9, dx=4, dy=-6 if fn(end_) > 0 else -4)
    pg.note(L + 345, y_ + 12, "each extra term\nbends the curve back\nand hugs the wave\nfor longer", C.GREY, 13)
    ch.check_num(parts[3][0](2.0), math.sin(2.0), 0.01)
    f.p("$x$ alone rises forever. The $-\\frac{x^3}{3!}$ term pulls it back down; $+\\frac{x^5}{5!}$ stops it "
        "falling too far; and so on. Add enough terms and the recipe matches the wave as far along as you like: "
        "the factorials on the bottom grow so fast that they always win in the end.", 14)


def tan_series(ch):
    f = flow(ch)
    sec(f, "Tan: one recipe divided by another", room=560)
    f.p("$\\tan x = \\frac{\\sin x}{\\cos x}$, so divide the recipes. Dividing by $1 - (\\text{something small})$ "
        "is Chapter 17's sum to infinity read backwards: $\\frac{1}{1-r} = 1 + r + r^2 + \\dots$", 14, gap=6)
    step(f, r"\tan x=\frac{x-\frac{x^3}{6}+\dots}{1-\frac{x^2}{2}+\dots}", "sin recipe ÷ cos recipe", size=19)
    step(f, r"\frac{1}{1-\frac{x^2}{2}}\approx1+\frac{x^2}{2}", "Chapter 17 with r = x²/2", size=19)
    step(f, r"\tan x\approx\left(x-\frac{x^3}{6}\right)\left(1+\frac{x^2}{2}\right)=x+\frac{x^3}{2}-\frac{x^3}{6}+\dots",
         "expand; keep powers up to x³", size=17)
    step(f, r"\tan x=x+\frac{x^3}{3}+\frac{2x^5}{15}+\frac{17x^7}{315}+\dots", "the rest: by computer", size=19, color=C.GREEN)
    xs = sp.Symbol("x")
    ch.check(sp.expand((xs - xs ** 3 / 6) * (1 + xs ** 2 / 2)).coeff(xs, 3), sp.Rational(1, 3))
    ch.check(sp.series(sp.tan(xs), xs, 0, 8).removeO(),
             xs + xs ** 3 / 3 + 2 * xs ** 5 / 15 + 17 * xs ** 7 / 315)
    ch.formula(r"\tan x=x+\frac{x^3}{3}+\frac{2x^5}{15}+\dots\ \ (|x|<\tfrac{\pi}{2})", "tangent series")
    f.p("Compare the starts: $\\sin x = x - \\frac{x^3}{6}$ and $\\tan x = x + \\frac{x^3}{3}$. sin dips just "
        "{B:below} the arc $x$, tan climbs {B:above} it: exactly the order of the three heights in the "
        "touching-line picture.", 14, gap=10)
    y_ = f.reserve(186)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 300, 160, (0, 1.75), (0, 6))
    ax.grid(0.25, 1)
    ax.axes("x", None, 0.5, 1, size=8)
    ax.curve(math.tan, 0, math.atan(6), C.GREEN, 3.0)
    ax.vline(PI / 2, C.RED, 1.2, (4, 3))
    pg.text(ax.X(PI / 2) + 3, ax.Y(5.9), "π/2", 9, C.RED, F.BOLD)
    tparts = [(lambda v: v, "x", C.GREY), (lambda v: v + v ** 3 / 3, "2 terms", C.ORANGE),
              (lambda v: v + v ** 3 / 3 + 2 * v ** 5 / 15, "3 terms", C.BLUE),
              (lambda v: v + v ** 3 / 3 + 2 * v ** 5 / 15 + 17 * v ** 7 / 315, "4 terms", C.PURPLE)]
    for fn, lab, col in tparts:
        clipped(ax, fn, 0, 1.75, 6, col, 1.5)
    for k, (fn, lab, col) in enumerate(tparts):
        pg.line(L + 350, y_ + 20 + k * 20, L + 372, y_ + 20 + k * 20, col, 2)
        pg.text(L + 378, y_ + 13 + k * 20, lab, 10, col, F.BOLD)
    pg.line(L + 350, y_ + 100, L + 372, y_ + 100, C.GREEN, 3)
    pg.text(L + 378, y_ + 93, "real tan", 10, C.GREEN, F.BOLD)
    ch.check(all(tparts[3][0](v / 100) < math.tan(v / 100) for v in range(1, 157)), True)
    f.p("Every recipe is a smooth polynomial, and a polynomial can never shoot off to infinity at a fixed $x$. "
        "So the tan recipe can only work {B:between $-\\frac{\\pi}{2}$ and $\\frac{\\pi}{2}$}. That's Chapter "
        "17's warning in disguise: $\\frac{1}{1-r}$ needs $r$ below 1, and here $r = 1 - \\cos x$ reaches 1 "
        "exactly when $\\cos x = 0$, at the asymptote. The division breaks exactly where the picture's radius "
        "stops meeting the touching line.", 14)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Unit circle", r"(\cos\theta,\ \sin\theta),\qquad\tan\theta=\frac{\sin\theta}{\cos\theta}", "the point at angle $\\theta$"),
        ("Pythagorean identity", r"\cos^2\theta+\sin^2\theta=1", None),
        ("CAST", None, "positive: Q1 {B:All}, Q2 {B:Sin}, Q3 {B:Tan}, Q4 {B:Cos}"),
        ("Reference angle", None, "Q2: $180^\\circ-\\theta$;  Q3: $\\theta-180^\\circ$;  Q4: $360^\\circ-\\theta$"),
        ("Any angle", None, "reduce to $0$–$360^\\circ$, find the quadrant, use $\\alpha$, attach the CAST sign"),
        ("sin and cos graphs", None, "period $360^\\circ$ ($2\\pi$), amplitude 1; cos is even, sin is odd"),
        ("tan graph", None, "period $180^\\circ$ ($\\pi$); asymptotes where $\\cos x=0$"),
        ("General wave", r"y=A\sin(B(x-C))+D",
         "amplitude $|A|$, period $\\frac{360^\\circ}{B}$, shift $C$ right, midline $D$; max/min $D\\pm|A|$"),
        ("tan(Bx)", r"\text{period}=\frac{180^\circ}{B}=\frac{\pi}{B}", None),
        ("Read off a graph", r"D=\frac{\max+\min}{2},\quad A=\frac{\max-\min}{2},\quad B=\frac{360^\circ}{\text{period}}", None),
        ("Power series", r"\sin x=x-\frac{x^3}{3!}+\frac{x^5}{5!}-\dots,\quad\cos x=1-\frac{x^2}{2!}+\frac{x^4}{4!}-\dots",
         "$x$ in radians"),
    ], C.BLUE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Answers in grey.", 13.5, gap=10)
    groups = [
        ("Circle", ["Coordinates of the point at 90° on the unit circle", "Is cos 150° positive or negative?",
                    "sin 210° = ? (use the 30° triangle and the sign)"],
         "1. (0, 1)   2. negative (left half)   3. −0.5"),
        ("Graphs", ["Period and amplitude of y = 4 sin x", "Period of y = sin 3x", "Period of y = cos(x/2)",
                    "Where does y = tan x have asymptotes between 0 and 2π?"],
         "4. 2π, 4   5. 2π/3   6. 4π   7. x = π/2 and 3π/2"),
        ("Wheels", ["A wheel of radius 10 m, hub 12 m up, turning once a minute: write h(t) if you board "
                    "at the bottom.", "Use the sine series with 3 terms to estimate sin 0.5"],
         "8. h = 12 − 10 cos(2πt), t in minutes   9. 0.5 − 0.125/6 + 0.03125/120 ≈ 0.479427"),
        ("Recipes", ["Use the cosine series with 3 terms to estimate cos 0.5",
                     "Estimate tan 0.3 with the start of the tan recipe, x + x³/3",
                     "At 60° (x ≈ 1.047 radians) put sin x, the arc x and tan x in order, with values",
                     "In the one-tiny-step triangle, which side tells you how fast sin grows?"],
         "10. 1 − 0.25/2 + 0.0625/24 ≈ 0.877604 (true 0.877583)   11. 0.3 + 0.027/3 = 0.309 (true 0.3093)   "
         "12. sin 0.866 < arc 1.047 < tan 1.732   13. the upright side, h cos θ: sin grows at cos's rate"),
        ("Find the unknown", ["Exact values of cos 225° and tan 300°",
                              "θ is in quadrant 2 and sin θ = 0.6. Find θ, cos θ and tan θ.",
                              "y = A sin(Bx) + D has maximum 7, minimum 1 and repeats every 90°. Find A, B and D.",
                              "y = 5 sin(Bx) has period 72°. Find B.",
                              "y = tan(Bx) has asymptotes 45° apart. Find B."],
         "14. cos 225° = −cos 45° = −1/√2 (Q3);  tan 300° = −tan 60° = −√3 (Q4)   "
         "15. α = sin⁻¹ 0.6 = 36.87°, θ = 180° − 36.87° = 143.13°;  cos θ = −0.8, tan θ = −0.75   "
         "16. D = (7 + 1)/2 = 4, A = (7 − 1)/2 = 3, B = 360/90 = 4   17. B = 360/72 = 5   "
         "18. period 45° = 180°/B, so B = 4"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(sp.sin(sp.Rational(7, 6) * sp.pi), -sp.Rational(1, 2))
    ch.check_num(0.5 - 0.125 / 6 + 0.03125 / 120, 0.479427, tol=0.000002)
    ch.check_num(1 - 0.25 / 2 + 0.0625 / 24, 0.877604, tol=0.000001)
    ch.check_num(0.3 + 0.027 / 3, 0.309, tol=1e-12)
    ch.check_num(math.tan(0.3), 0.3093, tol=0.00005)
    ch.check([round(v, 3) for v in (math.sin(PI / 3), PI / 3, math.tan(PI / 3))], [0.866, 1.047, 1.732])
    ch.check([sp.cos(sp.Rational(5, 4) * sp.pi), sp.tan(sp.Rational(5, 3) * sp.pi)], [-1 / sp.sqrt(2), -sp.sqrt(3)])
    th = 180 - math.degrees(math.asin(0.6))
    ch.check_num(th, 143.13, tol=0.005)
    ch.check_num(math.cos(math.radians(th)), -0.8, tol=1e-9)
    ch.check_num(math.tan(math.radians(th)), -0.75, tol=1e-9)
    ch.check([sp.Rational(7 + 1, 2), sp.Rational(7 - 1, 2), sp.Rational(360, 90)], [4, 3, 4])
    xs = sp.Symbol("x")
    ch.check(sp.periodicity(5 * sp.sin(5 * xs), xs), sp.Rational(72, 180) * sp.pi)
    ch.check(sp.periodicity(sp.tan(4 * xs), xs), sp.Rational(45, 180) * sp.pi)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    unit_circle(ch)
    quadrants(ch)
    ferris(ch)
    sin_cos(ch)
    tan_graph(ch)
    wheels(ch)
    read_graph(ch)
    step_rule(ch)
    leapfrog(ch)
    series(ch)
    tan_series(ch)
    summary(ch)
    your_turn(ch)
