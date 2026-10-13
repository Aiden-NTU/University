"""Chapter 20 - The straight line. A taxi meter (fixed charge + price per mile) is y = mx + c;
gradient is a staircase and a road sign; the line through two points in tiny steps; cover-up
sketching; parallel and perpendicular lines by turning the staircase on its side."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 20
NUM = 20
TITLE = "The straight line"
SHORT = "Straight line"
SLUG = "Straight-line"
ACCENT = C.ORANGE
REQUIRES = ["coordinates", "axes", "graph-of-function", "intercepts", "function", "substitution", "transpose",
            "solve-equation", "negative-numbers", "fraction", "percentage", "simultaneous-equations", "reciprocal"]
INTRODUCES = ["gradient", "straight-line-equation", "gradient-formula", "parallel-gradients",
              "perpendicular-gradients", "linear-relationship"]

PAPER = "#fffcf8"
x, y, c, m = sp.symbols("x y c m")


def icon(pg, x0, y0):
    pg.line(x0 + 1, y0 + 16, x0 + 17, y0 + 2, C.ORANGE, 1.6)
    pg.poly([(x0 + 5, y0 + 13), (x0 + 11, y0 + 13), (x0 + 11, y0 + 8)], C.ORANGE, 0.9)


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def stair(ax, x1, y1, run, rise, col=C.GREEN, labels=True, size=12):
    """Draw a run-then-rise staircase between two points of a line, in data coordinates."""
    ax.seg(x1, y1, x1 + run, y1, col, 1.8)
    ax.seg(x1 + run, y1, x1 + run, y1 + rise, C.RED, 1.8)
    if labels:
        pg = ax.pg
        pg.text(ax.X(x1 + run / 2), ax.Y(y1) + 3, f"run {run:g}".replace("-", "−"), size, col, F.BOLD,
                align="center", solid=False)
        pg.text(ax.X(x1 + run) + 5, ax.Y(y1 + rise / 2) - 7, f"rise {rise:g}".replace("-", "−"), size, C.RED,
                F.BOLD, solid=False)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 20, "The straight line", "a taxi meter drawn as a picture", C.ORANGE, PAPER)
    pg.rect(L + 30, 220, 150, 90, C.INK, 1.4, fillcolor="#263238", r=10)
    pg.text(L + 105, 230, "TAXI", 12, C.YELLOW, F.BOLD, align="center")
    pg.rect(L + 45, 252, 120, 40, "#76ff03", 1, fillcolor="#1b5e20", r=4)
    pg.text(L + 105, 258, "£ 9.00", 20, "#b9f6ca", F.MONO, align="center")
    pg.note(L + 30, 318, "£3 to get in, then £2 per mile.\n3 miles: 3 + 2 × 3 = £9", C.BROWN, 16)
    ax = Axes(pg, L + 250, 200, 200, 130, (0, 5), (0, 14))
    ax.grid(1, 2)
    ax.axes("x", "y", 1, 2, size=8)
    ax.curve(lambda t: 2 * t + 3, color=C.ORANGE, width=2.2)
    ax.dot(3, 9, C.RED, 4)
    f = ch.flow(top=400)
    f.p("Some things grow by the {B:same amount for every step}: a taxi fare goes up £2 for every "
        "mile, a phone bill by 10p per minute, a spring stretches 1 cm for every 100 g. Graph any of "
        "these and you get a {B:straight line}, and every straight line has the same kind of formula:",
        14, gap=6)
    f.eq(r"y=mx+c", 26, C.ORANGE)
    f.p("This chapter decodes that formula: $c$ is where the line starts (the £3 to get in) and "
        "$m$ is how steep it is (the £2 per mile). Then you'll find the equation of a line from any "
        "two points on it, which is exactly what Lecture 14 asks.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 7} {y:(y = mx + c, slope and intercept) and} {B:Lecture 14} "
        "{y:(line through two points).}", 12.5)


def taxi(ch):
    f = flow(ch)
    sec(f, "The taxi meter: c is the start, m is the price per step")
    f.p("Fare in pounds $y$ for $x$ miles: $y = 2x + 3$. Make a table, like Lecture 7 does for "
        "$y = 2x + 1$:", 14, gap=8)
    y_ = f.reserve(86)
    pg = f.pg
    labs = [("miles x", C.INK), ("2x", C.BLUE), ("+ 3", C.PURPLE), ("fare y", C.ORANGE)]
    for r_, (lab, col) in enumerate(labs):
        pg.text(L + 6, y_ + r_ * 20, lab, 12, col, F.BOLD)
    for i in range(6):
        xx = L + 110 + i * 60
        pg.text(xx, y_, str(i), 13, C.INK, align="center")
        pg.text(xx, y_ + 20, str(2 * i), 13, C.BLUE, align="center")
        pg.text(xx, y_ + 40, "3", 13, C.PURPLE, align="center")
        pg.text(xx, y_ + 60, str(2 * i + 3), 13, C.ORANGE, F.BOLD, align="center")
        if i:
            pg.note(xx - 36, y_ + 68, "+2", C.GREEN, 13, solid=False)
    f.gap(6)
    f.p("The fares go up by {B:2 every time} the miles go up by 1: that's the $m$, the number in "
        "front of $x$. At 0 miles you still pay {B:3}: that's the $c$, the number on its own.",
        14, gap=10)
    y_ = f.reserve(190)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 250, 160, (0, 5.5), (0, 14))
    ax.grid(1, 2)
    ax.axes("x", "y", 1, 2, size=9)
    ax.curve(lambda t: 2 * t + 3, color=C.ORANGE, width=2.2)
    for i in range(6):
        ax.dot(i, 2 * i + 3, C.ORANGE, 3.5)
    stair(ax, 2, 7, 1, 2)
    ax.dot(0, 3, C.PURPLE, 5)
    pg.note(L + 310, y_ + 20, "c = 3: where the line\ncrosses the y-axis\n(purple dot)", C.PURPLE, 16)
    pg.note(L + 310, y_ + 90, "m = 2: every 1 step across,\nthe line climbs 2\n(the little staircase)",
            C.GREEN, 16)
    ch.check((2 * x + 3).subs(x, 3), 9)
    ch.term("gradient (slope)", "how steep a line is: how much y goes up for each 1 that x goes across; m in y = mx + c")
    ch.term("y-intercept", "c in y = mx + c: the value of y where the line crosses the y-axis (x = 0)")
    ch.formula(r"y=mx+c", "straight line (m = gradient, c = y-intercept)")


def gradient(ch):
    f = flow(ch)
    sec(f, "Gradient: rise over run", room=520)
    f.p("To measure steepness anywhere on a line, draw a staircase under it: go {B:across} (the run) "
        "then {B:up} (the rise). The gradient is how much you rise for each step across:", 14, gap=6)
    y_ = f.reserve(72)
    pg = f.pg
    bw = 260
    pg.rect(L + (W - bw) / 2, y_, bw, 64, C.ORANGE, 1.6, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.eq(L + W / 2, y_ + 32, r"m=\frac{\text{rise}}{\text{run}}", 22, align="center", valign="middle")
    f.p("{b:Road signs use this.} A \"10%\" hill sign means you rise 10 m for every 100 m across: "
        "gradient $\\frac{10}{100} = 0.1$. A \"1 in 4\" sign means rise 1 for every 4 across: 0.25, a "
        "steep hill!", 14, gap=10)
    ch.check(sp.Rational(10, 100), sp.Rational(1, 10))
    y_ = f.reserve(150)
    pg = f.pg
    cases = [(2, "m = 2: steep uphill", C.ORANGE), (0.5, "m = 0.5: gentle uphill", C.BLUE),
             (0, "m = 0: flat (y = c)", C.GREY), (-1, "m = −1: downhill", C.RED)]
    for k, (mv, lab, col) in enumerate(cases):
        x0 = L + 4 + k * 124
        ax = Axes(pg, x0, y_ + 4, 104, 104, (-2, 3), (-2, 4))
        ax.grid(1, 1, color="#eeeeee")
        ax.axes(None, None, 0, 0)
        ax.curve(lambda t, mv=mv: mv * t + 1, color=col, width=2)
        if mv:
            stair(ax, 0, 1, 1, mv, labels=False)
        pg.text(x0 + 52, y_ + 116, lab, 10.5, col, F.BOLD, align="center")
    f.p("Read lines {B:left to right}, like text. Going uphill = positive gradient; downhill = "
        "negative; flat = 0. Lecture 7: \"the greater $m$, the steeper the line\", and a negative "
        "$m$ tilts it the other way. (A vertical line has no gradient at all: the run is 0, and you "
        "can't divide by 0. Its equation is just $x = $ a number.)", 14, gap=8)
    f.p("{b:Changing $c$ only slides the line up or down.} Same $m$ means same steepness, so "
        "$y = 2x + 1$, $y = 2x$ and $y = 2x - 1$ are {B:parallel}: they never meet.", 14)
    ch.term("parallel lines", "lines with the same gradient; they never meet")


def two_points(ch):
    f = flow(ch)
    sec(f, "The line through two points (Lecture 14)", room=520)
    f.p("{B:Find the equation of the line through (4, 4) and (8, 12).} Two jobs: find $m$ from the "
        "staircase, then find $c$ by using one of the points.", 14, gap=10)
    y_ = f.reserve(200)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 14, 230, 170, (-1, 10), (-6, 14))
    ax.grid(1, 2)
    ax.axes("x", "y", 2, 2, size=9)
    ax.curve(lambda t: 2 * t - 4, color=C.ORANGE, width=2)
    stair(ax, 4, 4, 4, 8)
    ax.dot(4, 4, C.BLUE, 4)
    ax.dot(8, 12, C.BLUE, 4)
    ax.dot(0, -4, C.PURPLE, 4.5)
    ax.label(4, 4, "{B:(4, 4)}", 11, dx=-44, dy=-6)
    ax.label(8, 12, "{B:(8, 12)}", 11, dx=-52, dy=-10)
    ax.label(0, -4, "{P:c = −4}", 11, dx=6, dy=-4)
    pg.note(L + 290, y_ + 16, "From (4, 4) to (8, 12):\nacross 8 − 4 = 4\nup 12 − 4 = 8", C.GREEN, 16)
    pg.note(L + 290, y_ + 100, "The line crosses the\ny-axis at −4, below 0.", C.PURPLE, 16)
    step(f, r"m=\frac{\text{rise}}{\text{run}}=\frac{12-4}{8-4}=\frac84=2", "job 1: the staircase", size=19)
    step(f, r"y=2x+c", "we know m, not c yet", size=19)
    step(f, r"4=2\times4+c", "the line goes through (4, 4): put x = 4, y = 4", size=19)
    step(f, r"4=8+c\ \Rightarrow\ c=-4", "−8 on both sides", size=19)
    step(f, r"y=2x-4", "job 2 done", size=21, color=C.GREEN)
    ch.check(sp.solve([4 - (4 * m + c), 12 - (8 * m + c)], [m, c]), {m: 2, c: -4})
    f.p("{G:Check with the other point:} $2 \\times 8 - 4 = 12$ ✓. (Always check with the point you "
        "{B:didn't} use.)", 13.5, gap=8)
    f.p("The staircase as a formula, for points $(x_1, y_1)$ and $(x_2, y_2)$:", 14, gap=6)
    y_ = f.reserve(72)
    pg = f.pg
    bw = 240
    pg.rect(L + (W - bw) / 2, y_, bw, 64, C.ORANGE, 1.6, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.eq(L + W / 2, y_ + 32, r"m=\frac{y_2-y_1}{x_2-x_1}", 22, align="center", valign="middle")
    ch.formula(r"m=\frac{y_2-y_1}{x_2-x_1}", "gradient through two points")
    f.p("{R:Keep the order the same top and bottom} (second point minus first, both times).", 13.5)


def downhill(ch):
    f = flow(ch)
    sec(f, "A downhill example, in tiny steps", room=380)
    f.p("{B:Line through (−1, 5) and (3, −3).} The minus signs are where mistakes happen, so every "
        "subtraction gets its own bracket:", 14, gap=6)
    step(f, r"m=\frac{(-3)-(5)}{(3)-(-1)}", "second minus first, top and bottom", size=19)
    step(f, r"=\frac{-8}{4}=-2", "−3 − 5 = −8;  3 − (−1) = 3 + 1 = 4", size=19)
    step(f, r"5=-2\times(-1)+c", "use (−1, 5)", size=19)
    step(f, r"5=2+c\ \Rightarrow\ c=3", "−2 × −1 = +2", size=19)
    step(f, r"y=-2x+3", "", size=21, color=C.GREEN)
    ch.check(sp.solve([5 - (-m + c), -3 - (3 * m + c)], [m, c]), {m: -2, c: 3})
    f.p("{G:Check:} $-2(3) + 3 = -3$ ✓. {h:Sense check:} from the first point to the second, $x$ went "
        "up but $y$ went down, so the gradient must be negative. It is.", 13.5)


def other_forms(ch):
    f = flow(ch)
    sec(f, "Lines in disguise, and the cover-up sketch", room=420)
    f.p("Lines aren't always written as $y = mx + c$. {B:$2x + 3y = 12$} is a line too. To read off $m$ "
        "and $c$, rearrange so $y$ is on its own (Chapter 14):", 14, gap=6)
    step(f, r"3y=-2x+12", "−2x from both sides", size=19)
    step(f, r"y=-\tfrac23x+4", "÷ 3: so m = −2/3 and c = 4", size=19, color=C.GREEN)
    ch.check(sp.solve(2 * x + 3 * y - 12, y), [-sp.Rational(2, 3) * x + 4])
    f.p("{b:The cover-up sketch.} To draw it fast, find where it crosses each axis:", 14, gap=8)
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 200, 130, (-1, 7), (-1, 5))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 1, size=8)
    ax.curve(lambda t: -2 * t / 3 + 4, color=C.ORANGE, width=2)
    ax.dot(0, 4, C.PURPLE, 4)
    ax.dot(6, 0, C.BLUE, 4)
    pg.note(L + 260, y_ + 10, "Cover up the x-term (x = 0):\n3y = 12, so y = 4.  Point (0, 4)", C.PURPLE, 15)
    pg.note(L + 260, y_ + 62, "Cover up the y-term (y = 0):\n2x = 12, so x = 6.  Point (6, 0)", C.BLUE, 15)
    pg.note(L + 260, y_ + 114, "Join the two dots with a ruler.", C.ORANGE, 15)
    f.p("This is how the simultaneous-equation lines of Chapter 15 are drawn.", 13.5, C.GREY)


def perpendicular(ch):
    f = flow(ch)
    sec(f, "Perpendicular lines: turn the staircase on its side", room=400)
    f.p("Two lines are {B:perpendicular} when they cross at a right angle (a perfect corner). Take a "
        "staircase of run 2, rise 1 (gradient $\\frac12$) and turn it a quarter turn. The run and rise "
        "swap places, and one of them now points the negative way: run 1, rise −2, gradient $-2$.",
        14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 40, y_ + 6, 170, 130, (-2, 4), (-2, 3))
    ax.grid(1, 1)
    ax.axes(None, None, 0, 0)
    ax.curve(lambda t: 0.5 * t, color=C.ORANGE, width=2)
    ax.curve(lambda t: -2 * t + 2.5, color=C.BLUE, width=2)
    stair(ax, 0, 0, 2, 1, labels=False)
    ax.seg(1, 0.5, 2, 0.5, C.GREEN, 1.8)
    ax.seg(2, 0.5, 2, -1.5, C.RED, 1.8)
    pg.note(L + 240, y_ + 10, "orange: m = 1/2\nblue: m = −2\n\nMultiply them: (1/2) × (−2) = −1", C.PURPLE, 16)
    ch.check(sp.Rational(1, 2) * -2, -1)
    f.p("The rule: gradients of perpendicular lines {B:multiply to −1}. So to get the perpendicular "
        "gradient, {B:flip the fraction and change its sign}: 3 becomes $-\\frac13$, $-\\frac25$ becomes "
        "$\\frac52$.", 14)
    ch.formula(r"m_1m_2=-1", "perpendicular lines")
    ch.term("perpendicular", "meeting at a right angle (90°); for lines, gradients multiply to −1")


def science(ch):
    f = flow(ch)
    sec(f, "Straight lines in real life: temperature", room=300)
    f.p("Fahrenheit and Celsius are linked by a straight line: $F = 1.8C + 32$. Decode it: water "
        "freezes at 0 °C, which is $c = 32$ °F; every 1 °C warmer is 1.8 °F warmer.", 14, gap=6)
    step(f, r"F=1.8(100)+32=212", "boiling point: 100 °C = 212 °F ✓", size=19)
    step(f, r"C=\frac{F-32}{1.8}", "undo it for the reverse conversion (Chapter 14)", size=19)
    ch.check_num(1.8 * 100 + 32, 212)
    f.p("Any time a question says \"a fixed amount plus so much per...\", think $y = mx + c$.", 13.5,
        C.BROWN)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Taxi meters: your turn", fresh=True)
    f.p("Answers in grey. Draw the staircase for every gradient question.", 13.5, gap=10)
    groups = [
        ("Reading y = mx + c", ["Gradient and intercept of y = 5x − 2?", "Gradient and intercept of y = 7 − 3x?",
                                "Gradient and intercept of 4x + 2y = 10?", "A plumber charges £40 call-out plus £30 per hour. Write the cost y for x hours."],
         "1. m = 5, c = −2   2. m = −3, c = 7   3. y = −2x + 5: m = −2, c = 5   4. y = 30x + 40"),
        ("Two points", ["Gradient between (1, 2) and (4, 11)", "Equation through (1, 2) and (4, 11)",
                        "Equation through (−2, 7) and (2, −1)", "Equation through (0, 5) parallel to y = 3x − 1"],
         "5. 3   6. y = 3x − 1   7. y = −2x + 3   8. y = 3x + 5"),
        ("Sketch and perpendicular", ["Where does 3x + 5y = 15 cross the axes?", "Perpendicular gradient to m = 4?",
                                      "Perpendicular gradient to m = −2/3?"],
         "9. (0, 3) and (5, 0)   10. −1/4   11. 3/2"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(sp.solve(4 * x + 2 * y - 10, y), [5 - 2 * x])
    ch.check(sp.Rational(11 - 2, 4 - 1), 3)
    ch.check(sp.solve([2 - (m + c), 11 - (4 * m + c)], [m, c]), {m: 3, c: -1})
    ch.check(sp.solve([7 - (-2 * m + c), -1 - (2 * m + c)], [m, c]), {m: -2, c: 3})
    ch.check([sp.Rational(15, 5), sp.Rational(15, 3)], [3, 5])
    ch.check(-1 / sp.Rational(-2, 3), sp.Rational(3, 2))


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    taxi(ch)
    gradient(ch)
    two_points(ch)
    downhill(ch)
    other_forms(ch)
    perpendicular(ch)
    science(ch)
    your_turn(ch)
