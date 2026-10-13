"""Chapter 27 - Angles (Lecture 6, first part). An angle is an amount of turning: people turning on the
spot, clock hands (30 degrees an hour), the anticlockwise convention, then the radian as a piece of
string one radius long wrapped round the rim, degree <-> radian conversion as a unit-conversion chain,
the DEG/RAD calculator trap, and arc length / sector area as pizza crust and slice."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 27
NUM = 27
TITLE = "Angles: degrees and radians"
SHORT = "Angles"
SLUG = "Angles"
ACCENT = C.PURPLE
REQUIRES = ["circle-measures", "pi-word", "unit-conversion", "fraction", "multiply-fractions", "division",
            "rounding", "area", "units", "simplify-fraction", "negative-numbers"]
INTRODUCES = ["angle", "degrees", "right-angle", "angle-types", "anticlockwise-positive", "radian",
              "degree-radian-conversion", "arc-length", "sector-area"]

PAPER = "#fcfaff"


def icon(pg, x0, y0):
    pg.line(x0 + 2, y0 + 16, x0 + 17, y0 + 16, C.PURPLE, 1.6)
    pg.line(x0 + 2, y0 + 16, x0 + 13, y0 + 3, C.PURPLE, 1.6)
    pg.arc(x0 + 2, y0 + 16, 8, 0, 50, C.PURPLE, 1.2)


def sec(f, t_, **kw):
    section(f, t_, C.PURPLE, icon, **kw)


def P(cx, cy, r, deg):
    """Point at maths angle deg (anticlockwise from east) on a y-down page."""
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def clock(pg, cx, cy, r, hh, mm, col=C.PURPLE, label=True):
    pg.circle(cx, cy, r, C.INK, 1.4, fillcolor="#ffffff")
    for k in range(12):
        x1, y1 = P(cx, cy, r * 0.88, 90 - 30 * k)
        x2, y2 = P(cx, cy, r, 90 - 30 * k)
        pg.line(x1, y1, x2, y2, C.INK, 1.2)
        if label and r > 30:
            xt, yt = P(cx, cy, r * 0.72, 90 - 30 * k)
            pg.text(xt, yt - 5, str(k or 12), 8, C.GREY, align="center", solid=False)
    ha = 90 - 30 * (hh % 12) - 0.5 * mm
    ma = 90 - 6 * mm
    pg.line(cx, cy, *P(cx, cy, r * 0.5, ha), C.INK, 2.6)
    pg.line(cx, cy, *P(cx, cy, r * 0.8, ma), col, 1.8)
    pg.dot(cx, cy, 2.4, C.INK)
    return ha, ma


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 27, "Angles: degrees and radians", "how much have you turned?", C.PURPLE, PAPER)
    clock(pg, L + 80, 260, 55, 2, 0)
    pg.arc(L + 80, 260, 22, 30, 90, C.RED, 1.6)
    pg.note(L + 150, 220, "2 o'clock:\nthe hands are\n60° apart", C.RED, 16)
    cx, cy, r = L + 370, 260, 50
    pg.circle(cx, cy, r, C.GREY, 1)
    pg.line(cx, cy, cx + r, cy, C.PURPLE, 1.6)
    pg.line(cx, cy, *P(cx, cy, r, math.degrees(1)), C.PURPLE, 1.6)
    pts = [P(cx, cy, r, d) for d in [i * math.degrees(1) / 20 for i in range(21)]]
    pg.poly(pts, C.ORANGE, 3)
    pg.note(cx + 55, cy - 50, "string one radius\nlong, laid on the rim:\n1 radian", C.ORANGE, 15)
    f = ch.flow(top=350)
    f.p("An angle isn't a length or a shape: it's {B:an amount of turning}. Open a door, turn a key, "
        "spin round on the spot: each is an angle.", 14, gap=10)
    f.p("We measure turning two ways: {B:degrees} (360 for a full turn, the everyday way) and "
        "{B:radians} (about 6.28 for a full turn, the way calculus and your lecturer prefer). This "
        "chapter shows where both come from and how to swap between them.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 6} {y:(radians vs degrees, notation and conversion).}", 12.5)


def turning(ch):
    f = flow(ch)
    sec(f, "Turning on the spot")
    f.p("Stand facing north and turn. A {B:full turn} brings you back to where you started. We cut a "
        "full turn into {B:360 equal steps} called {B:degrees}, written with a little circle: 360°.",
        14, gap=10)
    y_ = f.reserve(120)
    pg = f.pg
    turns = [(90, "quarter turn", "90°"), (180, "half turn", "180°"), (270, "three quarters", "270°"),
             (360, "full turn", "360°")]
    for k, (deg, nm, lab) in enumerate(turns):
        cx, cy = L + 55 + k * 125, y_ + 45
        pg.circle(cx, cy, 30, C.LIGHT[C.PURPLE], 0.8)
        pg.arc(cx, cy, 30, 90, 90 - deg + (4 if deg == 360 else 0), C.PURPLE, 1.8, arrow=True)
        pg.circle(cx, cy, 7, C.INK, 1.2, fillcolor="#ffffff")
        pg.line(cx, cy, *P(cx, cy, 14, 90 - deg), C.RED, 2)
        pg.text(cx, y_ + 86, nm, 11, C.INK, F.BOLD, align="center")
        pg.text(cx, y_ + 100, lab, 12, C.PURPLE, F.BOLD, align="center")
    ch.term("angle", "an amount of turning between two directions")
    ch.term("degree", "1/360 of a full turn, written °")
    ch.symbol(r"^\circ", "degrees", "360° is one full turn")
    f.p("Why 360? Nobody really knows: the Babylonians liked it (a year has about 360 days, and 360 "
        "divides by 2, 3, 4, 5, 6, 8, 9, 10, 12...). Lecture 6 calls degrees {B:arbitrary}, and that's "
        "fair.", 14, gap=10)
    f.p("{b:Names for sizes of angle:}", 14, gap=8)
    y_ = f.reserve(136)
    pg = f.pg
    kinds = [(50, "acute", "less than 90°"), (90, "right angle", "exactly 90°"), (130, "obtuse", "90° to 180°"),
             (180, "straight", "exactly 180°"), (250, "reflex", "more than 180°")]
    for k, (deg, nm, why) in enumerate(kinds):
        cx, cy = L + 30 + k * 100, y_ + 60
        pg.line(cx, cy, cx + 40, cy, C.INK, 1.6)
        pg.line(cx, cy, *P(cx, cy, 40, deg), C.INK, 1.6)
        if deg == 90:
            pg.rect(cx, cy - 9, 9, 9, C.PURPLE, 1.2)
        else:
            pg.arc(cx, cy, 14, 0, deg, C.PURPLE, 1.5)
        pg.text(cx + 10, y_ + 104, nm, 11, C.PURPLE, F.BOLD, align="center")
        pg.text(cx + 10, y_ + 118, why, 9, C.GREY, align="center")
    ch.term("right angle", "a quarter turn, 90°, marked with a little square")
    ch.term("acute / obtuse / reflex", "less than 90° / between 90° and 180° / more than 180°")


def clocks(ch):
    f = flow(ch)
    sec(f, "Clock hands: angles you already read every day", room=460)
    f.p("A clock face is a full turn split into 12 hours, so {B:each hour mark is 360 ÷ 12 = 30°} apart. "
        "The minute hand does a full turn in 60 minutes: {B:6° per minute}.", 14, gap=12)
    ch.check(sp.Rational(360, 12), 30)
    ch.check(sp.Rational(360, 60), 6)
    y_ = f.reserve(130)
    pg = f.pg
    for k, (hh, mm, ans) in enumerate([(3, 0, "90°"), (2, 0, "60°"), (6, 0, "180°"), (2, 30, "105°")]):
        cx = L + 55 + k * 125
        ha, ma = clock(pg, cx, y_ + 50, 42, hh, mm)
        a0, a1 = sorted([ha, ma])
        if a1 - a0 > 180:
            a0, a1 = a1, a0 + 360
        pg.arc(cx, y_ + 50, 16, a0, a1, C.RED, 1.6)
        pg.text(cx, y_ + 98, f"{hh}:{mm:02d}", 11, C.INK, F.BOLD, align="center")
        pg.text(cx, y_ + 112, ans, 12, C.RED, F.BOLD, align="center")
    f.p("2 o'clock: the hour hand is 2 marks round, so $2 \\times 30^\\circ = 60^\\circ$ (Lecture 6's "
        "cosine-rule clock, Chapter 31). {b:The trap at 2:30:} the hour hand has moved {B:halfway} "
        "towards 3, so it's at 75° from 12, while the minute hand is at 180°. Gap: "
        "$180^\\circ - 75^\\circ = 105^\\circ$, not 90°.", 14)
    ch.check(180 - (2 * 30 + 15), 105)


def direction(ch):
    f = flow(ch)
    sec(f, "Which way is positive? Anticlockwise, from the east", room=400)
    f.p("Clocks go clockwise from 12. Mathematicians do the opposite: {B:start pointing east (along the "
        "positive x-axis) and turn anticlockwise}. Lecture 6 measures angles this way on the unit "
        "circle. Turning clockwise gives a {B:negative} angle.", 14, gap=12)
    y_ = f.reserve(170)
    pg = f.pg
    cx, cy, r = L + 120, y_ + 80, 65
    pg.arrow(cx - r - 20, cy, cx + r + 20, cy, C.GREY, 1, head=5)
    pg.arrow(cx, cy + r + 15, cx, cy - r - 15, C.GREY, 1, head=5)
    for deg, col, lab in [(60, C.PURPLE, "+60°"), (-45, C.RED, "−45°"), (200, C.GREEN, "+200°")]:
        pg.line(cx, cy, *P(cx, cy, r, deg), col, 1.8)
        pg.arc(cx, cy, 22 + abs(deg) / 12, 0, deg, col, 1.3, arrow=True)
        tx, ty = P(cx, cy, r + 14, deg)
        pg.text(tx, ty - 6, lab, 11, col, F.BOLD, align="center")
    pg.note(L + 260, y_ + 10, "+60°: a sixth of a turn anticlockwise\n−45°: an eighth of a turn clockwise\n"
            "+200°: past the half-turn\n\nMore than 360° just means more than\none full turn: 550° = 360° + 190°.\n"
            "(Lecture 6 uses 550° in an example.)", C.INK, 14)
    ch.term("anticlockwise positive", "maths angles start at the positive x-axis and turn anticlockwise; clockwise is negative")


def radian(ch):
    f = flow(ch)
    sec(f, "The radian: a string one radius long", room=560)
    f.p("Take a piece of string {B:exactly as long as the circle's radius} and lay it along the rim. "
        "The angle it covers at the centre is {B:one radian}. (Lecture 6: \"1 radian is the angle "
        "subtended by an arc of length $R$\"; {h:subtended} just means \"made at the centre by\".)",
        14, gap=10)
    y_ = f.reserve(220)
    pg = f.pg
    cx, cy, r = L + 120, y_ + 105, 90
    pg.circle(cx, cy, r, C.GREY, 0.8)
    one = math.degrees(1)
    cols = [C.ORANGE, C.BLUE]
    for k in range(7):
        a0 = k * one
        a1 = min((k + 1) * one, 360)
        pts = [P(cx, cy, r, a0 + (a1 - a0) * i / 24) for i in range(25)]
        pg.poly(pts, cols[k % 2] if k < 6 else C.RED, 3.4)
        pg.line(cx, cy, *P(cx, cy, r, a0), C.LIGHT[C.GREY] if k else C.INK, 0.8 if k else 1.4)
        if k < 6:
            tx, ty = P(cx, cy, r + 14, (a0 + a1) / 2)
            pg.text(tx, ty - 6, str(k + 1), 11, cols[k % 2], F.BOLD, align="center")
    pg.line(cx, cy, cx + r, cy, C.INK, 1.4)
    pg.text(cx + r / 2, cy + 4, "r", 12, C.INK, F.BOLD, align="center")
    pg.note(cx + r + 30, y_ + 10, "Lay radius-long strings round the rim:\n6 whole strings fit, plus a "
            "little\nred bit (0.28 of a string).\n\nThe circumference is 2πr (Chapter 5),\nso exactly 2π ≈ "
            "6.28 strings fit.", C.INK, 14)
    ch.check_num(2 * math.pi, 6.283, tol=0.001)
    f.p("So a full turn is $2\\pi$ radians:", 14, gap=6)
    step(f, r"360^\circ=2\pi\text{ rad}\approx6.28\text{ rad}", "", size=21, color=C.PURPLE)
    step(f, r"1\text{ rad}=\frac{360^\circ}{2\pi}\approx57.3^\circ", "a bit less than 60°", size=19)
    ch.check_num(360 / (2 * math.pi), 57.30, tol=0.01)
    ch.term("radian", "the angle made at the centre by an arc as long as the radius; 2π radians = 360°")
    ch.formula(r"360^\circ=2\pi\text{ rad}", "degrees and radians")
    f.p("{b:Why bother?} A radian is {B:arc length ÷ radius}, a length divided by a length, so it has "
        "{B:no units}: it's a pure number. That makes formulas simpler (next pages) and calculus "
        "(Chapter 34) only works cleanly in radians.", 14)


def convert(ch):
    f = flow(ch)
    sec(f, "Converting: the unit-conversion chain again", room=560)
    f.p("Chapter 5 converted units by multiplying by a fraction equal to 1 (like $\\frac{100\\text{ cm}}{1\\text{ "
        "m}}$). Here the \"1\" is $\\frac{\\pi\\text{ rad}}{180^\\circ}$, because $\\pi$ rad and 180° are "
        "the same half-turn:", 14, gap=10)
    y_ = f.reserve(100)
    pg = f.pg
    pg.rect(L, y_, W / 2 - 8, 90, C.PURPLE, 1.3, fillcolor=C.LIGHT[C.PURPLE], r=8)
    pg.text(L + 10, y_ + 6, "degrees → radians", 12, C.PURPLE, F.BOLD)
    pg.eq(L + 20, y_ + 26, r"\times\frac{\pi}{180}", 20)
    pg.rect(L + W / 2 + 8, y_, W / 2 - 8, 90, C.ORANGE, 1.3, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.text(L + W / 2 + 18, y_ + 6, "radians → degrees", 12, C.ORANGE, F.BOLD)
    pg.eq(L + W / 2 + 28, y_ + 26, r"\times\frac{180}{\pi}", 20)
    ch.formula(r"\text{rad}=\text{deg}\times\frac{\pi}{180}", "degrees to radians")
    ch.term("degree-radian conversion", "× π/180 turns degrees into radians; × 180/π turns radians into degrees")
    step(f, r"60^\circ\times\frac{\pi}{180}=\frac{60\pi}{180}=\frac{\pi}{3}", "cancel 60/180 = 1/3", size=19)
    step(f, r"\frac{3\pi}{4}\times\frac{180}{\pi}=\frac{3\times180}{4}=135^\circ", "the π's cancel", size=19)
    ch.check(sp.Rational(60, 180) * sp.pi, sp.pi / 3)
    ch.check(sp.Rational(3, 4) * 180, 135)
    f.p("{b:Pizza shortcut:} think in fractions of a turn. 90° is a quarter turn, and a quarter of "
        "$2\\pi$ is $\\frac{\\pi}{2}$. The ones to know by heart:", 14, gap=10)
    y_ = f.reserve(110)
    pg = f.pg
    angs = [(30, r"\tfrac{\pi}{6}"), (45, r"\tfrac{\pi}{4}"), (60, r"\tfrac{\pi}{3}"), (90, r"\tfrac{\pi}{2}"),
            (180, r"\pi"), (270, r"\tfrac{3\pi}{2}"), (360, r"2\pi")]
    exp = [sp.pi / 6, sp.pi / 4, sp.pi / 3, sp.pi / 2, sp.pi, 3 * sp.pi / 2, 2 * sp.pi]
    ch.check([sp.Rational(d, 180) * sp.pi for d, _ in angs], exp)
    for k, (d, lat) in enumerate(angs):
        cx, cy = L + 32 + k * 70, y_ + 32
        pg.circle(cx, cy, 24, C.GREY, 0.8)
        pg.sector(cx, cy, 24, 0, d, C.LIGHT[C.PURPLE], outline=C.PURPLE)
        pg.text(cx, y_ + 62, f"{d}°", 11, C.INK, F.BOLD, align="center")
        pg.eq(cx, y_ + 88, lat, 15, C.PURPLE, align="center", valign="middle")
    f.gap(4)
    f.p("{R:Notation warning (Lecture 6):} degrees always carry the ° sign. Radians are written \"rad\", a "
        "small c ($2^c$), or {B:nothing at all}. So an angle with no ° is probably radians, but many "
        "sources are lazy: always check which one you're in.", 14)


def calculator(ch):
    f = flow(ch)
    sec(f, "The calculator trap: DEG or RAD?", room=320)
    f.p("Your calculator has a mode: {B:DEG} or {B:RAD}. Type the same keys in the wrong mode and you get "
        "a confident, wrong answer:", 14, gap=12)
    y_ = f.reserve(90)
    pg = f.pg
    for k, (mode, val, ok) in enumerate([("DEG", math.sin(math.radians(30)), True), ("RAD", math.sin(30), False)]):
        x0 = L + 20 + k * 250
        pg.rect(x0, y_, 200, 70, C.INK, 1.6, fillcolor="#e9efe6", r=8)
        pg.text(x0 + 10, y_ + 6, mode, 10, C.INK, F.BOLD)
        pg.text(x0 + 10, y_ + 22, "sin(30)", 13, C.INK, F.MONO)
        pg.text(x0 + 190, y_ + 44, f"{val:.4f}", 15, C.INK, F.MONO, align="right")
        (pg.tick if ok else pg.xmark)(x0 + 215, y_ + 30, 12)
    ch.check_num(math.sin(30), -0.9880, tol=0.0001)
    f.gap(6)
    f.p("In RAD mode, \"30\" means 30 radians (almost 5 full turns), so sin gives $-0.988$ instead of "
        "$0.5$. If a trig answer looks mad, check the mode first.", 14)


def arcs(ch):
    f = flow(ch)
    sec(f, "Pizza maths: crust length and slice area", room=440)
    f.p("With the angle $\\theta$ in {B:radians}, the formulas for a slice of circle are beautifully "
        "simple (that's the payoff for radians):", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    cx, cy, r = L + 90, y_ + 120, 110
    pg.sector(cx, cy, r, 0, 45, C.LIGHT[C.ORANGE], outline=C.ORANGE)
    pts = [P(cx, cy, r, 45 * i / 20) for i in range(21)]
    pg.poly(pts, C.BROWN, 4)
    pg.arc(cx, cy, 26, 0, 45, C.PURPLE, 1.4)
    pg.text(cx + 32, cy - 20, "θ", 13, C.PURPLE, F.BOLD)
    pg.text(cx + r / 2, cy + 4, "r", 12, C.INK, F.BOLD, align="center")
    pg.note(cx + r + 6, cy - 80, "crust", C.BROWN, 15)
    pg.eq(L + 240, y_ + 10, r"s=r\theta", 22, C.BROWN)
    pg.note(L + 340, y_ + 14, "arc (crust) length", C.BROWN, 15)
    pg.eq(L + 240, y_ + 60, r"A=\tfrac12r^2\theta", 22, C.ORANGE)
    pg.note(L + 360, y_ + 64, "sector (slice) area", C.ORANGE, 15)
    ch.formula(r"s=r\theta", "arc length (θ in radians)")
    ch.formula(r"A=\tfrac12r^2\theta", "sector area (θ in radians)")
    ch.term("arc length", "the distance along the curved edge of a slice of circle: s = rθ (θ in radians)")
    ch.term("sector area", "the area of a slice of circle: A = ½r²θ (θ in radians)")
    f.p("{b:Why they work:} a full turn ($\\theta = 2\\pi$) gives $s = 2\\pi r$ (the whole "
        "circumference) and $A = \\frac12r^2\\cdot2\\pi = \\pi r^2$ (the whole area). A slice is just that "
        "fraction of the whole.", 14, gap=8)
    f.p("{b:Example:} a 30 cm pizza (radius 15 cm) cut into 8 slices. Each slice angle is $\\frac{2\\pi}{8} "
        "= \\frac{\\pi}{4}$:", 14, gap=6)
    step(f, r"s=15\times\frac{\pi}{4}\approx11.8\text{ cm}", "crust per slice", size=19)
    step(f, r"A=\tfrac12\times15^2\times\frac{\pi}{4}\approx88.4\text{ cm}^2", "cheese per slice", size=19)
    ch.check_num(15 * math.pi / 4, 11.78, tol=0.01)
    ch.check_num(0.5 * 225 * math.pi / 4, 88.36, tol=0.01)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Answers in grey.", 13.5, gap=10)
    groups = [
        ("Degrees", ["Angle between clock hands at 4:00", "... at 9:30", "Is 170° acute, obtuse or reflex?",
                     "Describe −90° as a turn"],
         "1. 120°   2. 105° (hour hand at 285°, minute at 180°)   3. obtuse   4. a quarter turn clockwise"),
        ("Converting", ["120° in radians", "π/6 in degrees", "2.5 rad in degrees (1 d.p.)", "225° in radians"],
         "5. 2π/3   6. 30°   7. 143.2°   8. 5π/4"),
        ("Arcs", ["Arc length: r = 10 cm, θ = 1.2 rad", "Sector area: r = 4 m, θ = π/2",
                  "A slice has a crust of 6 cm on a 12 cm-radius pizza. Its angle in radians?"],
         "9. 12 cm   10. 4π ≈ 12.6 m²   11. 6 ÷ 12 = 0.5 rad"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.PURPLE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(abs((9 * 30 + 15) - 180), 105)
    ch.check([sp.Rational(120, 180) * sp.pi, sp.Rational(225, 180) * sp.pi], [2 * sp.pi / 3, 5 * sp.pi / 4])
    ch.check_num(2.5 * 180 / math.pi, 143.2, tol=0.05)
    ch.check(sp.Rational(1, 2) * 16 * sp.pi / 2, 4 * sp.pi)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    turning(ch)
    clocks(ch)
    direction(ch)
    radian(ch)
    convert(ch)
    calculator(ch)
    arcs(ch)
    your_turn(ch)
