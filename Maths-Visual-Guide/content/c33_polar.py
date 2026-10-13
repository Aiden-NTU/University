"""Chapter 33 - Polar coordinates (Lecture 11). Radar screen: 'turn, then walk'. The same point in both
languages, the right triangle hiding inside (x = r cos θ, y = r sin θ), the calculator's blind spot
for tan⁻¹ and the quadrant fix, a spinning pen drawing polar curves (circle, ray, spiral, r = 1.5 cos θ,
the cardioid), converting equations, and Lecture 11's extended trig list."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step, title_block

ORDER = 33
NUM = 33
TITLE = "Polar coordinates"
SHORT = "Polar"
SLUG = "Polar"
ACCENT = C.TEAL
REQUIRES = ["pythagoras", "sine", "cosine", "tangent", "inverse-trig", "sohcahtoa", "radian",
            "degree-radian-conversion", "quadrants", "coordinates", "unit-circle", "trig-any-angle",
            "pythagorean-identity", "compound-angle", "transpose", "subject-of-formula", "anticlockwise-positive",
            "negative-numbers"]
INTRODUCES = ["polar-coordinates", "polar-to-cartesian", "cartesian-to-polar", "quadrant-correction",
              "polar-curve", "cardioid", "polar-equation-conversion", "double-angle"]

PAPER = "#f7fcfc"
D = math.radians


def icon(pg, x0, y0):
    pg.circle(x0 + 9, y0 + 9, 8, C.TEAL, 1.2)
    pg.line(x0 + 9, y0 + 9, x0 + 15, y0 + 3, C.TEAL, 1.6)


def sec(f, t_, **kw):
    section(f, t_, C.TEAL, icon, **kw)


def pgrid(pg, cx, cy, s, rings, spokes=30, col="#c9d6d8", a0=0, a1=360):
    """Polar graph paper: circles at the given radii (in units, s px per unit) and spokes every
    `spokes` degrees between a0 and a1. Returns Pp(r, deg) -> page point."""
    rmax = max(rings)
    for r_ in rings:
        if a1 - a0 >= 360:
            pg.circle(cx, cy, r_ * s, col, 0.6)
        else:
            pg.arc(cx, cy, r_ * s, a0, a1, col, 0.6)
    d = a0
    while d < a1 + 0.01 and not (a1 - a0 >= 360 and d >= a1):
        t = D(d)
        pg.line(cx, cy, cx + rmax * s * math.cos(t), cy - rmax * s * math.sin(t), col, 0.6)
        d += spokes
    return lambda r_, deg: (cx + r_ * s * math.cos(D(deg)), cy - r_ * s * math.sin(D(deg)))


def pcurve(pg, Pp, rf, d0, d1, col, w=2.2, n=240, dash=None):
    pts = [Pp(rf(d0 + (d1 - d0) * i / n), d0 + (d1 - d0) * i / n) for i in range(n + 1)]
    pg.poly(pts, col, w, dash=dash)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 33, "Polar coordinates", "turn, then walk", C.TEAL, PAPER)
    cx, cy, Rr = L + 150, 280, 95
    pg.circle(cx, cy, Rr, "#2e7d4f", 2.0, fillcolor="#123b2a")
    for k in (1, 2, 3):
        pg.circle(cx, cy, Rr * k / 3, "#3fae6a", 0.7)
    for d in range(0, 360, 30):
        pg.line(cx, cy, cx + Rr * math.cos(D(d)), cy - Rr * math.sin(D(d)), "#2e7d4f", 0.5)
    pg.sector(cx, cy, Rr, 18, 40, "#4cd07d", 120)
    pg.line(cx, cy, cx + Rr * math.cos(D(40)), cy - Rr * math.sin(D(40)), "#8ff0b0", 1.6)
    bx, by = cx + Rr * 0.8 * math.cos(D(40)), cy - Rr * 0.8 * math.sin(D(40))
    pg.circle(bx, by, 5, "#b9ffd0", 1.0, fillcolor="#b9ffd0")
    pg.arc(cx, cy, 22, 0, 40, "#ffe14d", 1.4, arrow=True)
    pg.text(cx + 26, cy - 22, "40°", 10, "#ffe14d", F.BOLD, solid=False)
    pg.note(L + 270, 205, "The radar operator doesn't say\n\"3 km east, 2.5 km north\".\nShe says "
            "\"40° round from east, 4 km out\":\nturn to face the angle, then\nwalk the distance.\n"
            "(Maths angles go anticlockwise from\neast. A navigator's bearing goes\nclockwise from north.)", C.TEAL, 15,
            w=R - L - 270)
    f = ch.flow(top=395)
    f.p("You've always said where things are with $(x, y)$: so far across, so far up. {B:Polar "
        "coordinates} use a different pair: {B:how far from the centre} ($r$) and {B:which direction} "
        "($\\theta$). Anything that spins or radiates (wheels, radar, waves, sound from a speaker) is "
        "easier this way.", 14, gap=10)
    f.p("You'll translate between the two languages, dodge the calculator's blind spot, and draw some "
        "curves that would be horrible in $x$ and $y$.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 11} {y:(Cartesian vs polar, converting, degrees vs radians, finding θ "
        "in each quadrant, polar curves, converting equations, the extended trig list, the cardioid).}", 12.5)


def two_ways(ch):
    f = flow(ch)
    sec(f, "Two ways to say where", room=420)
    f.p("The same point A, described in both languages:", 14, gap=10)
    y_ = f.reserve(206)
    pg = f.pg
    for k in range(2):
        ax = Axes(pg, L + 30 + k * 260, y_ + 10, 150, 160, (-0.5, 2.5), (-0.5, 2.7))
        ax.grid(1, 1)
        ax.axes("x", "y", 1, 1, size=9)
        ax.dot(1, 2, C.INK, 3.5)
        if k == 0:
            ax.arrow(0, 0, 1, 0, C.ORANGE, 2.0, head=6)
            ax.arrow(1, 0, 1, 2, C.TEAL, 2.0, head=6)
            ax.label(1, 2, "{B:A (1, 2)}", 11, dx=6, dy=-16)
            pg.rich(L - 10, y_ + 184, "{B:Cartesian}: walk 1 east, then 2 north", w=250, size=12, align="center")
        else:
            ax.arrow(0, 0, 1, 2, C.RED, 2.4, head=7)
            ox, oy = ax.P(0, 0)
            pg.arc(ox, oy, 24, 0, 63.43, C.PURPLE, 1.4, arrow=True)
            ax.label(0.35, 0.05, "{P:θ = 63.4°}", 10, dx=4, dy=-16)
            ax.label(0.5, 1.0, "{R:r = 2.24}", 11, dx=-62, dy=-10)
            ax.label(1, 2, "{B:A}", 11, dx=6, dy=-16)
            pg.rich(L + 245, y_ + 184, "{B:Polar}: turn to 63.4°, then walk 2.24", w=250, size=12, align="center")
    f.p("Cartesian writes A as $(x, y) = (1, 2)$. Polar writes it as $(r, \\theta) = (2.24, 63.4^\\circ)$. "
        "$r$ is the {B:radius} (distance from the centre, the origin) and $\\theta$ is the angle turned "
        "{B:anticlockwise from the positive $x$ axis} (Chapter 27's convention).", 14, gap=8)
    f.p("Lecture 11: Cartesian is what graphs, slopes and vectors are built on; polar is how you describe "
        "circular motion and navigate on a round planet.", 14)
    ch.term("polar coordinates", "(r, θ): distance r from the origin and angle θ anticlockwise from the positive x axis")
    ch.symbol(r"(r,\theta)", "r, theta", "a point in polar coordinates: radius then angle")


def to_cartesian(ch):
    f = flow(ch)
    sec(f, "Polar to Cartesian: the triangle hiding inside", room=460)
    rule_box(f, "polar to Cartesian", [
        "$x=r\\cos\\theta$ and $y=r\\sin\\theta$.",
        "This works for {B:any} angle: the signs of $\\cos\\theta$ and $\\sin\\theta$ put the point in the "
        "right quadrant automatically. No fix needed in this direction.",
    ], C.TEAL)
    f.p("Drop a line from the point straight down to the $x$ axis. You get a right-angled triangle with "
        "hypotenuse $r$ and angle $\\theta$ at the origin, so SOHCAHTOA (Chapter 28) does the rest:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 8, 4.6 * 36, 2.8 * 36, (-0.3, 4.3), (-0.3, 2.5))
    ax.grid(1, 1)
    ax.axes(None, None, 0, 0)
    px_, py_ = 4 * math.cos(D(30)), 2.0
    ax.seg(0, 0, px_, 0, C.TEAL, 3.0)
    ax.seg(px_, 0, px_, py_, C.ORANGE, 3.0)
    ax.seg(0, 0, px_, py_, C.RED, 2.6)
    ax.dot(px_, py_, C.INK, 3.5)
    X0, Y0 = ax.P(px_, 0)
    pg.rect(X0 - 9, Y0 - 9, 9, 9, C.GREY, 0.8)
    ox, oy = ax.P(0, 0)
    pg.arc(ox, oy, 30, 0, 30, C.PURPLE, 1.3)
    pg.text(ox + 34, oy - 16, "θ", 11, C.PURPLE, F.BOLD, solid=False)
    ax.label(1.3, 0.75, "{R:r}", 13, dx=-10, dy=-22)
    ax.label(1.2, 0, "{T:x = r cos θ}", 11, dx=0, dy=6)
    ax.label(px_, 1.0, "{O:y = r sin θ}", 11, dx=8, dy=-8)
    xq = L + 290
    pg.eq(xq, y_ + 8, r"x=r\cos\theta", 20, C.TEAL)
    pg.note(xq + 12, y_ + 38, "CAH: adjacent = hyp × cos", C.INK, 15, w=R - xq - 12)
    pg.eq(xq, y_ + 72, r"y=r\sin\theta", 20, C.ORANGE)
    pg.note(xq + 12, y_ + 102, "SOH: opposite = hyp × sin", C.INK, 15, w=R - xq - 12)
    ch.formula(r"x=r\cos\theta,\quad y=r\sin\theta", "polar to Cartesian")
    ch.term("polar to Cartesian", "x = r cos θ, y = r sin θ")
    f.p("{b:Example:} a ship at $(r, \\theta) = (4, 30^\\circ)$.", 14, gap=6)
    step(f, r"x=4\cos30^\circ=4\times0.866=3.46", "", size=17)
    step(f, r"y=4\sin30^\circ=4\times0.5=2", "", size=17)
    step(f, r"(r,\theta)=(4,30^\circ)\ \longrightarrow\ (x,y)=(3.46,\ 2)", "", size=17, color=C.TEAL)
    ch.check_num(4 * math.cos(D(30)), 3.46, tol=0.006)
    ch.check_num(4 * math.sin(D(30)), 2.0)
    f.p("{R:Slide slip:} Lecture 11's summary slide writes $y = x\\sin\\theta$. It should be "
        "$y = r\\sin\\theta$ (the hypotenuse is $r$, not $x$).", 13.5)


def to_polar(ch):
    f = flow(ch)
    sec(f, "Cartesian to polar, and the calculator's blind spot", room=600)
    rule_box(f, "Cartesian to polar", [
        "$r=\\sqrt{x^2+y^2}$ (Pythagoras; $r$ is never negative here).",
        "$\\theta=\\tan^{-1}\\dfrac yx$ {B:plus a correction} that depends on the quadrant: the calculator "
        "only answers between $-90^\\circ$ and $90^\\circ$.",
        "Always sketch the point first so you know which quadrant the answer must be in.",
    ], C.TEAL)
    f.p("Going the other way, Pythagoras gives the distance and TOA gives the angle:", 14, gap=6)
    step(f, r"r=\sqrt{x^2+y^2},\qquad \theta=\tan^{-1}\frac{y}{x}", "", size=20, color=C.TEAL)
    ch.formula(r"r=\sqrt{x^2+y^2},\quad\theta=\tan^{-1}\frac yx\ (+\text{quadrant fix})", "Cartesian to polar")
    f.p("Lecture 11: $A = (1, 2)$ in quadrant 1. $r = \\sqrt{1+4} = \\sqrt5 = 2.24$, "
        "$\\theta = \\tan^{-1}\\frac21 = 63.43^\\circ$ (1.107 rad). Perfect.", 14, gap=6)
    ch.check_num(math.degrees(math.atan(2)), 63.43, tol=0.006)
    f.p("Now $B = (-1, 2)$, in quadrant 2. The calculator says $\\tan^{-1}\\frac{2}{-1} = \\tan^{-1}(-2) = "
        "-63.43^\\circ$. That points down into quadrant 4: {R:the wrong way!}", 14, gap=10)
    y_ = f.reserve(212)
    pg = f.pg
    cx, cy, Rr, s = L + 120, y_ + 105, 85, 38
    pg.sector(cx, cy, Rr, -90, 90, C.LIGHT[C.GREEN])
    pg.circle(cx, cy, Rr, C.GREY, 1.0)
    pg.line(cx - Rr - 6, cy, cx + Rr + 6, cy, C.GREY, 0.8)
    pg.line(cx, cy - Rr - 6, cx, cy + Rr + 6, C.GREY, 0.8)
    Bp = (cx - s, cy - 2 * s)
    vec_ = (cx + s, cy + 2 * s)
    pg.arrow(cx, cy, Bp[0], Bp[1], C.RED, 2.4, head=7)
    pg.dot(*Bp, 3.5, C.RED)
    pg.text(Bp[0] - 70, Bp[1] - 16, "B (−1, 2)", 11, C.RED, F.BOLD)
    pg.arrow(cx, cy, vec_[0], vec_[1], C.GREY, 1.4, head=6, dash=(4, 3))
    pg.text(vec_[0] + 4, vec_[1] - 8, "calculator: −63.4°", 10, C.GREY, F.BOLD)
    pg.arc(cx, cy, 30, -63.43, 116.57, C.PURPLE, 1.5, arrow=True)
    pg.text(cx + 26, cy - 50, "+180°", 11, C.PURPLE, F.BOLD)
    pg.note(cx - 80, cy + 10, "green = the\ncalculator's half:\nit only answers\n−90° to 90°", C.GREEN, 12)
    cx2, cy2, R2 = L + 395, cy, 70
    pg.sector(cx2, cy2, R2, 90, 270, C.LIGHT[C.ORANGE])
    pg.sector(cx2, cy2, R2, 270, 360, C.LIGHT[C.PURPLE])
    pg.circle(cx2, cy2, R2, C.GREY, 1.0)
    pg.line(cx2 - R2, cy2, cx2 + R2, cy2, C.GREY, 0.8)
    pg.line(cx2, cy2 - R2, cx2, cy2 + R2, C.GREY, 0.8)
    pg.text(cx2 - 60, cy2 - R2 - 22, "the fix", 12, C.TEAL, F.BOLD, w=120, align="center")
    for qx, qy, q, fix, col in [(1, -1, "Q1", "as it is", C.GREEN), (-1, -1, "Q2", "+180°", C.ORANGE),
                                (-1, 1, "Q3", "+180°", C.ORANGE), (1, 1, "Q4", "+360°", C.PURPLE)]:
        x_, y0 = cx2 + qx * 36 - 32, cy2 + qy * 32 - 14
        pg.text(x_, y0, q, 11, C.INK, F.BOLD, w=64, align="center")
        pg.text(x_, y0 + 14, fix, 11, col, F.BOLD, w=64, align="center")
    f.p("{b:Why +180°?} The calculator can't tell $\\frac{2}{-1}$ from $\\frac{-2}{1}$: both are $-2$. So "
        "it always answers in the right-hand half. If the point is really on the left (quadrants 2 or 3), "
        "its direction is exactly opposite: turn another half-turn.", 14, gap=6)
    step(f, r"\theta_B=-63.43^\circ+180^\circ=116.57^\circ\quad(-1.107+\pi=2.03\text{ rad})", "", size=17,
         color=C.TEAL)
    ch.check_num(math.degrees(math.atan2(2, -1)), 116.57, tol=0.006)
    ch.check_num(math.atan2(2, -1), 2.03, tol=0.006)
    f.need(150)
    f.p("{b:The quadrant fix in full.} Work out $\\tan^{-1}\\frac yx$ on the calculator, then:", 14, gap=6)
    rules_table(f, ["Point is in", "Signs", "Add (degrees)", "Add (radians)", "θ ends up in"], [
        ["Quadrant 1", "x > 0, y > 0", "nothing", "nothing", "0° to 90°  (0 to π/2)"],
        ["Quadrant 2", "x < 0, y > 0", "180°", "π", "90° to 180°  (π/2 to π)"],
        ["Quadrant 3", "x < 0, y < 0", "180°", "π", "180° to 270°  (π to 3π/2)"],
        ["Quadrant 4", "x > 0, y < 0", "360°", "2π", "270° to 360°  (3π/2 to 2π)"],
    ], widths=[80, 85, 75, 75, 180], color=C.TEAL)
    rule_box(f, "points on the axes", [
        "No calculator needed (and $\\tan^{-1}\\frac y0$ gives an error anyway). Read the angle off the sketch:",
        "positive $x$ axis $0$; positive $y$ axis $90^\\circ=\\frac\\pi2$; negative $x$ axis "
        "$180^\\circ=\\pi$; negative $y$ axis $270^\\circ=\\frac{3\\pi}2$. And $r$ is just the distance from O.",
    ], C.TEAL)
    step(f, r"(0,-3):\ \ r=3,\ \ \theta=270^\circ=\tfrac{3\pi}{2}", "straight down", size=17)
    step(f, r"(-4,0):\ \ r=4,\ \ \tan^{-1}\tfrac{0}{-4}=0^\circ\to0^\circ+180^\circ=180^\circ=\pi",
         "x < 0: the fix still works", size=16, color=C.TEAL)
    ch.check_num(math.degrees(math.atan2(-3, 0)) % 360, 270)
    ch.check_num(math.degrees(math.atan2(0, -4)) % 360, 180)
    f.need(160)
    f.p("Lecture 11's four test points. Watch the calculator column repeat itself:", 14, gap=8)
    y_ = f.reserve(118)
    pg = f.pg
    colx = [L + 5, L + 85, L + 150, L + 240, L + 350]
    heads = ["point", "y ÷ x", "calculator", "quadrant fix", "true angle"]
    for x_, h_ in zip(colx, heads):
        pg.text(x_, y_, h_, 11, C.TEAL, F.BOLD)
    pg.line(L, y_ + 17, R, y_ + 17, C.GREY, 0.8)
    rows = [("(1, 1)", "1", "45°", "Q1: as it is", "45° = π/4"),
            ("(−1, 1)", "−1", "−45°", "Q2: +180°", "135° = 3π/4"),
            ("(−1, −1)", "1", "45°", "Q3: +180°", "225° = 5π/4"),
            ("(1, −1)", "−1", "−45°", "Q4: +360°", "315° = 7π/4")]
    for k, row in enumerate(rows):
        for j, (x_, v) in enumerate(zip(colx, row)):
            col = C.GREY if j == 2 else (C.GREEN if j == 4 else C.INK)
            pg.text(x_, y_ + 24 + k * 21, v, 12, col, F.BOLD if j == 4 else F.SANS)
    ch.check([round(math.degrees(math.atan2(y, x)) % 360) for x, y in [(1, 1), (-1, 1), (-1, -1), (1, -1)]],
             [45, 135, 225, 315])
    ch.check(sp.Rational(225, 180) * sp.pi, sp.Rational(5, 4) * sp.pi)
    f.p("{R:Slide slip:} Lecture 11 labels 225° as $\\frac{4\\pi}{3}$; it's $\\frac{5\\pi}{4}$ "
        "($\\frac{225}{180} = \\frac54$). $\\frac{4\\pi}{3}$ would be 240°.", 13.5, gap=8)
    f.p("{b:Degrees or radians?} Lecture 11: {B:calculate in radians}, and present in degrees only when the "
        "context wants it (navigation). If a question names a format, use it; if not, either is fine. "
        "Check the calculator's DEG/RAD mode first (Chapter 27).", 14)
    ch.term("quadrant correction", "after θ = tan⁻¹(y/x): add 180° (π) in quadrants 2 and 3, add 360° (2π) in "
            "quadrant 4; points on the axes are read off the sketch")


def curves(ch):
    f = flow(ch)
    sec(f, "Drawing with a spinning pen", room=560)
    f.p("Picture a pen on a spinning arm, like the radar sweep. As the arm turns through $\\theta$, you slide "
        "the pen in or out to distance $r$. A {B:polar equation} is the rule that says how far out the pen "
        "is at each angle.", 14, gap=10)
    y_ = f.reserve(152)
    pg = f.pg
    caps = ["{B:r = 2}, any θ:\na circle", "{B:θ = 45°}, any r:\na ray from the centre",
            "{B:r grows with θ}\n(r = 0.2θ): a spiral"]
    for k in range(3):
        cx = L + 80 + k * 165
        Pp = pgrid(pg, cx, y_ + 62, 22, [1, 2], spokes=45)
        if k == 0:
            pcurve(pg, Pp, lambda d: 2, 0, 360, C.TEAL, 2.4)
            pg.line(cx, y_ + 62, *Pp(2, 60), C.GREY, 1.0, dash=(3, 3))
        elif k == 1:
            pg.line(cx, y_ + 62, *Pp(2.6, 45), C.TEAL, 2.4)
            pg.arc(cx, y_ + 62, 14, 0, 45, C.PURPLE, 1.2)
        else:
            pcurve(pg, Pp, lambda d: 0.2 * D(d), 0, 720, C.TEAL, 2.0, n=400)
        for i, line_ in enumerate(caps[k].split("\n")):
            pg.rich(cx - 80, y_ + 122 + i * 15, line_, w=160, size=11, align="center")
    ch.term("polar curve", "the path traced by r = f(θ) as θ turns: the pen is r from the centre at angle θ")
    f.gap(4)
    f.p("{b:Lecture 11's example: $r = 1.5\\cos\\theta$.} Make a table, then plot each point by "
        "turning to $\\theta$ and walking $r$:", 14, gap=10)
    y_ = f.reserve(232)
    pg = f.pg
    cx, cy, s = L + 50, y_ + 112, 70
    Pp = pgrid(pg, cx, cy, s, [0.5, 1, 1.5], spokes=30, a0=-90, a1=90)
    pg.line(cx, cy - 110, cx, cy + 110, "#c9d6d8", 0.6)
    pcurve(pg, Pp, lambda d: 1.5 * math.cos(D(d)), -90, 90, C.TEAL, 2.4)
    for d, col in [(0, C.BLUE), (30, C.BLUE), (60, C.BLUE), (120, C.ORANGE), (150, C.ORANGE)]:
        r_ = 1.5 * math.cos(D(d))
        X, Y = Pp(r_, d)
        pg.dot(X, Y, 3.5, col)
        pg.text(X + 6, Y - (16 if d < 90 else -2), f"{d}°", 10, col, F.BOLD)
    pg.line(cx, cy, cx + 60 * math.cos(D(120)) * -1, cy - 60 * math.sin(D(120)) * -1, C.ORANGE, 1.0, dash=(3, 3))
    pg.arrow(cx, cy, cx + 30 * math.cos(D(120)), cy - 30 * math.sin(D(120)), C.GREY, 1.0, head=4)
    pg.text(cx - 28, cy - 44, "face 120°…", 9, C.GREY)
    pg.dot(cx, cy, 3.5, C.BLUE)
    pg.text(cx - 34, cy + 4, "90°", 10, C.BLUE, F.BOLD)
    tx = [L + 250, L + 320, L + 400]
    for x_, h_ in zip(tx, ["θ", "cos θ", "r = 1.5 cos θ"]):
        pg.text(x_, y_ + 2, h_, 11, C.TEAL, F.BOLD)
    pg.line(L + 245, y_ + 19, R, y_ + 19, C.GREY, 0.8)
    for k, d in enumerate(range(0, 181, 30)):
        c_ = math.cos(D(d))
        col = C.ORANGE if c_ < -1e-9 else C.INK
        pg.text(tx[0], y_ + 24 + k * 19, f"{d}°", 12, col)
        pg.text(tx[1], y_ + 24 + k * 19, f"{c_:.2f}".replace("-", "−").replace("−0.00", "0.00"), 12, col)
        pg.text(tx[2], y_ + 24 + k * 19, f"{1.5 * c_:.2f}".replace("-", "−").replace("−0.00", "0.00"), 12, col,
                F.BOLD)
    pg.note(L + 250, y_ + 162, "Negative r: face θ, then walk BACKWARDS. So 120° lands where 300° would: "
            "the pen goes round the same circle again.", C.ORANGE, 14, w=R - L - 250)
    ch.check([round(1.5 * math.cos(D(d)), 2) for d in range(0, 181, 30)],
             [1.5, 1.3, 0.75, 0.0, -0.75, -1.3, -1.5])
    t = sp.symbols("t")
    xx, yy = 1.5 * sp.cos(t) * sp.cos(t), 1.5 * sp.cos(t) * sp.sin(t)
    ch.check(sp.simplify((xx - sp.Rational(3, 4)) ** 2 + yy ** 2 - sp.Rational(9, 16)), 0)
    f.p("Surprise: it's a {B:circle} of diameter 1.5 sitting on the origin. In $x$ and $y$ that's "
        "$(x - 0.75)^2 + y^2 = 0.75^2$, which is much uglier to plot.", 14)


def cardioid(ch):
    f = flow(ch)
    sec(f, "The cardioid: a heart from one line of maths", room=330)
    f.p("Change the rule to $r = 1 + \\cos\\theta$. The pen starts 2 out, comes in to 1 when facing up, and "
        "reaches 0 (the centre) facing left:", 14, gap=10)
    y_ = f.reserve(205)
    pg = f.pg
    cx, cy, s = L + 110, y_ + 100, 45
    Pp = pgrid(pg, cx, cy, s, [1, 2], spokes=30)
    pts = [Pp(1 + math.cos(D(d)), d) for d in range(0, 361, 2)]
    pg.fillpoly(pts, C.LIGHT[C.PINK])
    pg.poly(pts, C.PINK, 2.6)
    for d in (0, 60, 90, 120, 180, 270):
        r_ = 1 + math.cos(D(d))
        X, Y = Pp(r_, d)
        pg.dot(X, Y, 3.2, C.INK)
        off = {0: (6, -16), 60: (6, -16), 90: (6, -18), 120: (-34, -16), 180: (-30, -18), 270: (6, 2)}[d]
        pg.text(X + off[0], Y + off[1], f"{d}°", 9, C.INK, F.BOLD, solid=False)
    pg.note(L + 250, y_ + 6, "θ = 0°: r = 1 + 1 = 2 (far right)\nθ = 90°: r = 1 + 0 = 1 (straight up)\n"
            "θ = 120°: r = 1 − 0.5 = 0.5\nθ = 180°: r = 1 − 1 = 0 (the dent)\nθ = 270°: r = 1 (straight down)",
            C.INK, 14, w=R - L - 250)
    pg.note(L + 250, y_ + 118, "\"Cardioid\" means heart-shaped. Microphones that hear mostly from the front "
            "have this pick-up pattern, and it turns up in roller and cam design (Lecture 11).", C.PINK, 14,
            w=R - L - 250)
    ch.check([1 + sp.cos(sp.rad(d)) for d in (0, 90, 120, 180)], [2, 1, sp.Rational(1, 2), 0])
    ch.term("cardioid", "the heart-shaped polar curve r = a(1 + cos θ)")


def converting(ch):
    f = flow(ch)
    sec(f, "Converting equations: swap x and y out", room=300)
    rule_box(f, "converting equations, both ways", [
        "{B:Cartesian → polar:} replace $x$ by $r\\cos\\theta$ and $y$ by $r\\sin\\theta$ "
        "(and $x^2+y^2$ by $r^2$), then make $r$ the subject.",
        "{B:Polar → Cartesian:} look for $r\\cos\\theta$, $r\\sin\\theta$ and $r^2$ and swap them for $x$, $y$ and "
        "$x^2+y^2$. If there is a lone $\\cos\\theta$ or $\\sin\\theta$, {B:multiply both sides by $r$} first.",
        "A fixed angle $\\theta=\\alpha$ is the line through O: $\\dfrac yx=\\tan\\alpha$.",
    ], C.TEAL)
    ch.formula(r"x^2+y^2=r^2,\qquad \tan\theta=\frac yx", "polar and Cartesian links")
    f.p("To turn a Cartesian equation into a polar one: {B:replace every $x$ by $r\\cos\\theta$ and every "
        "$y$ by $r\\sin\\theta$}, collect the $r$ terms, then make $r$ the subject (Chapter 14).", 14, gap=8)
    f.p("{b:Lecture 11: the straight line $y = 2x + 2$.}", 14, gap=6)
    step(f, r"r\sin\theta=2r\cos\theta+2", "swap y and x", size=18)
    step(f, r"r\sin\theta-2r\cos\theta=2", "r terms together", size=18)
    step(f, r"r(\sin\theta-2\cos\theta)=2", "factor out r (Chapter 12)", size=18)
    step(f, r"r=\frac{2}{\sin\theta-2\cos\theta}", "÷ the bracket", size=19, color=C.TEAL)
    th = sp.symbols("theta")
    rr = 2 / (sp.sin(th) - 2 * sp.cos(th))
    ch.check(sp.simplify(rr * sp.sin(th) - (2 * rr * sp.cos(th) + 2)), 0)
    f.p("{b:Check one point:} at $\\theta = 90^\\circ$, $r = \\frac{2}{1 - 0} = 2$: straight up 2, the point "
        "$(0, 2)$. And $y = 2x + 2$ does cross the $y$ axis at 2. ✓", 14, gap=10)
    f.p("{b:Lecture 11: the oval $x^2 + 2y^2 = 9$.}", 14, gap=6)
    step(f, r"(r\cos\theta)^2+2(r\sin\theta)^2=9", "swap", size=17)
    step(f, r"r^2(\cos^2\theta+2\sin^2\theta)=9", "factor out r²", size=17)
    step(f, r"r^2(\underbrace{\cos^2\theta+\sin^2\theta}_{=\,1}+\sin^2\theta)=9",
         "split 2 sin² into sin² + sin², then Chapter 30's identity", size=17)
    step(f, r"r^2=\frac{9}{1+\sin^2\theta}\quad\Rightarrow\quad r=\frac{3}{\sqrt{1+\sin^2\theta}}", "", size=18,
         color=C.TEAL)
    r2 = 9 / (1 + sp.sin(th) ** 2)
    ch.check(sp.simplify(r2 * sp.cos(th) ** 2 + 2 * r2 * sp.sin(th) ** 2 - 9), 0)
    f.p("{b:Check:} $\\theta = 0$ gives $r = 3$, the point $(3, 0)$: $9 + 0 = 9$ ✓. $\\theta = 90^\\circ$ gives "
        "$r = \\frac{3}{\\sqrt2} = 2.12$, the point $(0, 2.12)$: $2\\times2.12^2 = 9$ ✓.", 14)
    ch.check_num(2 * (3 / math.sqrt(2)) ** 2, 9.0)
    f.need(190)
    y_ = f.reserve(170)
    pg = f.pg
    cx, cy, s = L + 100, y_ + 82, 24
    Pp = pgrid(pg, cx, cy, s, [1, 2, 3], spokes=30)
    pcurve(pg, Pp, lambda d: 3 / math.sqrt(1 + math.sin(D(d)) ** 2), 0, 360, C.TEAL, 2.4)
    for d in (0, 90, 180, 270):
        X, Y = Pp(3 / math.sqrt(1 + math.sin(D(d)) ** 2), d)
        pg.dot(X, Y, 3.2, C.INK)
    pg.note(L + 220, y_ + 10, "Lecture 11's \"Polar curves 3\" slide is this oval. As the pen turns, r changes "
            "smoothly: largest (r = 3) facing 0 and π, smallest (r = 2.12) facing π/2 and 3π/2. "
            "So the oval is wider than it is tall.", C.INK, 14, w=R - L - 220)
    ch.check_num(3 / math.sqrt(1 + math.sin(math.pi / 2) ** 2), 2.12, tol=0.005)
    ch.term("converting to polar", "replace x by r cos θ and y by r sin θ, then make r the subject")


def back_to_xy(ch):
    f = flow(ch)
    sec(f, "Converting back, and quick wins", room=420)
    f.p("{b:Circle centred on O:} $x^2+y^2=9$.", 14, gap=6)
    step(f, r"r^2=9\ \Rightarrow\ r=3", "x² + y² is r²", size=18, color=C.TEAL)
    th = sp.symbols("theta")
    ch.check(sp.simplify((3 * sp.cos(th)) ** 2 + (3 * sp.sin(th)) ** 2), 9)
    f.p("{b:Line through O:} $y=x$.", 14, gap=6)
    step(f, r"r\sin\theta=r\cos\theta\ \Rightarrow\ \tan\theta=1\ \Rightarrow\ \theta=\tfrac\pi4",
         "÷ r cos θ", size=17, color=C.TEAL)
    ch.check(sp.atan(1), sp.pi / 4)
    f.p("(With negative $r$ allowed, $\\theta=\\frac\\pi4$ covers the whole line, including the part in "
        "quadrant 3.)", 13.5, gap=10)
    f.p("{b:Polar → Cartesian:} $r=4\\cos\\theta$. There is a lone $\\cos\\theta$, so multiply by $r$:", 14, gap=6)
    step(f, r"r^2=4r\cos\theta", "× r", size=18)
    step(f, r"x^2+y^2=4x", "r² → x² + y², r cos θ → x", size=18)
    step(f, r"x^2-4x+y^2=0\ \Rightarrow\ (x-2)^2+y^2=4", "complete the square", size=18, color=C.TEAL)
    xs, ys = sp.symbols("x y")
    rt = 4 * sp.cos(th)
    ch.check(sp.simplify(((rt * sp.cos(th)) - 2) ** 2 + (rt * sp.sin(th)) ** 2 - 4), 0)
    ch.check(sp.expand((xs - 2) ** 2 + ys ** 2 - 4 - (xs ** 2 + ys ** 2 - 4 * xs)), 0)
    f.p("A circle of radius 2 centred at $(2, 0)$, passing through O, just like $r=1.5\\cos\\theta$ earlier.",
        14, gap=10)
    mistakes(f, [
        (r"r=4\cos\theta\ \to\ r=4x", r"r^2=4r\cos\theta=4x",
         "x is r cos θ, not cos θ: multiply by r first"),
        (r"x^2+y^2=9\ \to\ r=9", r"r^2=9,\ r=3", "x² + y² is r², not r"),
    ])
    ch.term("polar to Cartesian equation", "swap r cos θ → x, r sin θ → y, r² → x² + y²; multiply by r first if needed")


def trig_list(ch):
    f = flow(ch)
    sec(f, "Lecture 11's extended trig list", room=330)
    f.p("Converting equations often needs these. The first four are the compound angle rules (Chapter 30 "
        "met the first). Notice the sign {B:flips} in the cosine ones:", 14, gap=6)
    for lat in [r"\sin(A\pm B)=\sin A\cos B\pm\cos A\sin B", r"\cos(A\pm B)=\cos A\cos B\mp\sin A\sin B"]:
        step(f, lat, "", size=18)
    f.p("Now just {B:set $B = A$} in the \"+\" versions, and the {B:double angle} rules drop out:", 14, gap=6)
    step(f, r"\sin2A=2\sin A\cos A", "sin A cos A + cos A sin A", size=18, color=C.TEAL)
    step(f, r"\cos2A=\cos^2A-\sin^2A=2\cos^2A-1=1-2\sin^2A", "", size=17, color=C.TEAL)
    f.p("The last two come from swapping $\\sin^2 A = 1 - \\cos^2 A$ (or the other way round) into the first "
        "one. Quick test with $A = 30^\\circ$: $\\sin 60^\\circ = 0.866$ and $2\\times0.5\\times0.866 = 0.866$ ✓.",
        14)
    A_, B_ = sp.symbols("A B")
    for lhs, rhs in [(sp.sin(A_ + B_), sp.sin(A_) * sp.cos(B_) + sp.cos(A_) * sp.sin(B_)),
                     (sp.sin(A_ - B_), sp.sin(A_) * sp.cos(B_) - sp.cos(A_) * sp.sin(B_)),
                     (sp.cos(A_ + B_), sp.cos(A_) * sp.cos(B_) - sp.sin(A_) * sp.sin(B_)),
                     (sp.cos(A_ - B_), sp.cos(A_) * sp.cos(B_) + sp.sin(A_) * sp.sin(B_)),
                     (sp.cos(2 * A_), 1 - 2 * sp.sin(A_) ** 2)]:
        ch.check(sp.simplify(sp.expand_trig(lhs) - rhs), 0)
    ch.formula(r"\sin2A=2\sin A\cos A,\quad\cos2A=\cos^2A-\sin^2A", "double angle")
    ch.term("double angle formulas", "sin 2A = 2 sin A cos A; cos 2A = cos²A − sin²A = 2cos²A − 1 = 1 − 2sin²A")


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Sketch the point or curve first. For θ from tan⁻¹, always ask \"which quadrant?\". Answers in grey.",
        13.5, gap=10)
    groups = [
        ("Polar to Cartesian", ["(r, θ) = (6, 60°)", "(r, θ) = (2, 3π/4)"],
         "1. (3, 5.20)   2. (−1.41, 1.41)"),
        ("Cartesian to polar (mind the quadrant!)", ["(3, 4)", "(−3, 4)", "(−2, −2)", "(5, −5)"],
         "3. (5, 53.13°)   4. (5, 126.87°)   5. (2.83, 225°)   6. (7.07, 315°)"),
        ("Curves and equations", ["Sketch r = 3. What shape is it?",
                                  "Where is the pen for r = 1 + cos θ at θ = 90°? Give x and y.",
                                  "Write the line x = 4 in polar form.",
                                  "Write the circle x² + y² = 25 in polar form."],
         "7. a circle of radius 3   8. r = 1, the point (0, 1)   9. r cos θ = 4, so r = 4/cos θ   10. r² = 25, so r = 5"),
        ("Double angle", ["Use sin 2A = 2 sin A cos A to find sin 90° from A = 45°."],
         "11. 2 × 0.7071 × 0.7071 = 1"),
        ("Find the unknown", ["Write r = 6 sin θ in Cartesian form and describe the curve.",
                              "Write the line y = √3 x in polar form.",
                              "Write the point (0, −5) in polar form, in degrees and radians.",
                              "A point has r = 8, y = 4 and is left of the y axis. Find θ and x.",
                              "A point has x = −3 and θ = 135°. Find y and r."],
         "12. × r: r² = 6r sin θ, x² + y² = 6y, x² + (y − 3)² = 9: circle, centre (0, 3), radius 3   "
         "13. tan θ = √3, θ = π/3 (60°)   14. on the negative y axis: (5, 270°) = (5, 3π/2)   "
         "15. sin θ = 4/8 = 0.5 and x < 0, so θ = 150°; x = 8 cos 150° ≈ −6.93   "
         "16. y = x tan 135° = (−3)(−1) = 3; r = √(9 + 9) ≈ 4.24"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.TEAL, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check_num(6 * math.sin(D(60)), 5.20, tol=0.006)
    ch.check_num(2 * math.cos(3 * math.pi / 4), -1.41, tol=0.006)
    pol = [(math.hypot(x, y), math.degrees(math.atan2(y, x)) % 360) for x, y in [(3, 4), (-3, 4), (-2, -2), (5, -5)]]
    for (r_, t_), (er, et) in zip(pol, [(5, 53.13), (5, 126.87), (2.83, 225), (7.07, 315)]):
        ch.check_num(r_, er, tol=0.006)
        ch.check_num(t_, et, tol=0.006)
    ch.check([1 + sp.cos(sp.pi / 2), (1 + sp.cos(sp.pi / 2)) * sp.cos(sp.pi / 2), (1 + sp.cos(sp.pi / 2)) * sp.sin(sp.pi / 2)],
             [1, 0, 1])
    ch.check(sp.simplify(2 * sp.sin(sp.pi / 4) * sp.cos(sp.pi / 4)), 1)
    th = sp.symbols("theta")
    r6 = 6 * sp.sin(th)
    ch.check(sp.simplify((r6 * sp.cos(th)) ** 2 + (r6 * sp.sin(th) - 3) ** 2), 9)
    ch.check(sp.atan(sp.sqrt(3)), sp.pi / 3)
    ch.check_num(math.degrees(math.atan2(-5, 0)) % 360, 270)
    ch.check_num(math.degrees(math.atan2(4, -math.sqrt(64 - 16))), 150, tol=0.001)
    ch.check_num(8 * math.cos(D(150)), -6.93, tol=0.005)
    ch.check_num(-3 * math.tan(D(135)), 3)
    ch.check_num(math.hypot(-3, 3), 4.24, tol=0.005)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Polar → Cartesian", r"x=r\cos\theta,\qquad y=r\sin\theta", "works for any angle; no fix needed"),
        ("Distance", r"r=\sqrt{x^2+y^2}", None),
        ("Angle", r"\theta=\tan^{-1}\frac yx", "then the quadrant fix"),
        ("Quadrant fix", None, "Q1: nothing; Q2 and Q3: + 180° (+ π); Q4: + 360° (+ 2π)"),
        ("Points on the axes", None, "read off the sketch: 0, 90° (π/2), 180° (π), 270° (3π/2)"),
        ("Links", r"x^2+y^2=r^2,\qquad \tan\theta=\frac yx", None),
        ("Cartesian → polar equation", None, "swap $x\\to r\\cos\\theta$, $y\\to r\\sin\\theta$, make $r$ the subject"),
        ("Polar → Cartesian equation", None, "multiply by $r$ if needed, then swap $r\\cos\\theta\\to x$, "
         "$r\\sin\\theta\\to y$, $r^2\\to x^2+y^2$"),
        ("Simple curves", None, "$r=a$: circle radius $a$; $\\theta=\\alpha$: line through O; "
         "$r=a\\cos\\theta$: circle through O"),
        ("Double angle", r"\sin2A=2\sin A\cos A,\quad \cos2A=\cos^2A-\sin^2A", None),
    ], C.TEAL)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    two_ways(ch)
    to_cartesian(ch)
    to_polar(ch)
    curves(ch)
    cardioid(ch)
    converting(ch)
    back_to_xy(ch)
    trig_list(ch)
    summary(ch)
    your_turn(ch)
