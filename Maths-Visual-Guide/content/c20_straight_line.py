"""Chapter 20 - The straight line. Rule first: y = mx + c, the gradient formula, point-gradient form,
parallel and perpendicular gradients, midpoint and distance, intersections, and a catalogue of
"given part of the information, find the rest" problems."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import (L, R, W, flow, go, mistakes, rule_box, rules_page, rules_table, section, step,
                         title_block)

ORDER = 20
NUM = 20
TITLE = "The straight line"
SHORT = "Straight line"
SLUG = "Straight-line"
ACCENT = C.ORANGE
REQUIRES = ["coordinates", "axes", "graph-of-function", "intercepts", "function", "substitution", "transpose",
            "solve-equation", "negative-numbers", "fraction", "percentage", "simultaneous-equations", "reciprocal"]
INTRODUCES = ["gradient", "straight-line-equation", "gradient-formula", "parallel-gradients",
              "perpendicular-gradients", "linear-relationship", "point-gradient-form", "midpoint",
              "distance-between-points", "line-intersection", "perpendicular-bisector", "collinear"]

PAPER = "#fffcf8"
x, y, c, m, k = sp.symbols("x y c m k")


def icon(pg, x0, y0):
    pg.line(x0 + 1, y0 + 16, x0 + 17, y0 + 2, C.ORANGE, 1.6)
    pg.poly([(x0 + 5, y0 + 13), (x0 + 11, y0 + 13), (x0 + 11, y0 + 8)], C.ORANGE, 0.9)


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def ex(f, s):
    f.need(100)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


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


def grad(p, q):
    return sp.Rational(q[1] - p[1], q[0] - p[0])


def corner(ax, px, py, d1, d2, s=9, col=C.INK):
    """Right-angle square at data point (px, py) between data directions d1 and d2."""
    X, Y = ax.X(px), ax.Y(py)

    def u(d):
        vx, vy = ax.X(px + d[0]) - X, ax.Y(py + d[1]) - Y
        n = math.hypot(vx, vy)
        return vx / n * s, vy / n * s

    (ax_, ay_), (bx, by) = u(d1), u(d2)
    ax.pg.poly([(X + ax_, Y + ay_), (X + ax_ + bx, Y + ay_ + by), (X + bx, Y + by)], col, 1.2)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 20, "The straight line", "y = mx + c, and everything you can be asked about it",
                     C.ORANGE, PAPER)
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
    f.p("Anything that grows by the {B:same amount for every step} (a taxi fare, a phone bill, a "
        "spring) graphs as a {B:straight line}, and every straight line (except vertical ones) has the "
        "formula", 14, gap=6)
    f.eq(r"y=mx+c", 26, C.ORANGE)
    f.p("This chapter states every rule you need about straight lines and then practises each type of "
        "question: reading $m$ and $c$, finding the line through two points, {B:proving lines are parallel "
        "or perpendicular}, midpoints and distances, where lines cross, and {B:filling in a missing value} "
        "when you're only given part of the information.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 7} {y:(y = mx + c, slope and intercept) and} {B:Lecture 14} "
        "{y:(line through two points). Chapter 34 reuses this chapter for tangents and normals.}", 12.5)


def taxi(ch):
    f = flow(ch)
    sec(f, "y = mx + c: gradient and intercept")
    rule_box(f, "the equation of a straight line", [
        "$y=mx+c$, where {B:m} is the {B:gradient} (how much $y$ changes when $x$ goes up by 1) and "
        "{B:c} is the {B:y-intercept} (the value of $y$ where the line crosses the $y$-axis, i.e. at $x=0$).",
        "To read $m$ and $c$, the equation must start \"$y=$\" with $y$ on its own. If it doesn't, "
        "rearrange first.",
        "A point $(a, b)$ lies on the line exactly when putting $x=a$ into the equation gives $y=b$.",
    ], C.ORANGE)
    f.p("Fare in pounds $y$ for $x$ miles: $y = 2x + 3$. The table (like Lecture 7's for $y = 2x + 1$):",
        14, gap=8)
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
    f.p("The fares go up by {B:2 every time} the miles go up by 1: that's $m$. At 0 miles you still pay "
        "{B:3}: that's $c$.", 14, gap=10)
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


def gradient(ch):
    f = flow(ch)
    sec(f, "Gradient: rise over run", room=520)
    rule_box(f, "gradient", [
        "$m=\\dfrac{\\text{rise}}{\\text{run}}=\\dfrac{\\text{change in }y}{\\text{change in }x}$, read "
        "{B:left to right}.",
        "$m>0$: uphill.  $m<0$: downhill.  $m=0$: flat (horizontal).",
        "Steepness depends on the {B:size} of $m$ ignoring its sign, $|m|$: $y=-5x$ is steeper than $y=2x$.",
    ], C.ORANGE)
    f.p("{b:Road signs use this.} \"10%\" means rise 10 m for every 100 m across: gradient "
        "$\\frac{10}{100} = 0.1$. \"1 in 4\" means rise 1 for every 4 across: 0.25, a steep hill.", 14, gap=10)
    ch.check(sp.Rational(10, 100), sp.Rational(1, 10))
    y_ = f.reserve(150)
    pg = f.pg
    cases = [(2, "m = 2: steep uphill", C.ORANGE), (0.5, "m = 0.5: gentle uphill", C.BLUE),
             (0, "m = 0: flat (y = c)", C.GREY), (-1, "m = −1: downhill", C.RED)]
    for kk, (mv, lab, col) in enumerate(cases):
        x0 = L + 4 + kk * 124
        ax = Axes(pg, x0, y_ + 4, 104, 104, (-2, 3), (-2, 4))
        ax.grid(1, 1, color="#eeeeee")
        ax.axes(None, None, 0, 0)
        ax.curve(lambda t, mv=mv: mv * t + 1, color=col, width=2)
        if mv:
            stair(ax, 0, 1, 1, mv, labels=False)
        pg.text(x0 + 52, y_ + 116, lab, 10.5, col, F.BOLD, align="center")
    f.p("Lecture 7 says \"the greater $m$, the steeper the line\": strictly, it is the greater "
        "{B:size} of $m$. A negative $m$ tilts the line the other way.", 13.5, gap=10)
    rule_box(f, "horizontal and vertical lines", [
        "{B:Horizontal} line through $(a, b)$: $y=b$. Gradient 0.",
        "{B:Vertical} line through $(a, b)$: $x=a$. The run is 0 and you can't divide by 0, so the gradient "
        "is {B:undefined}. A vertical line can't be written as $y=mx+c$.",
        "The $x$-axis is the line $y=0$; the $y$-axis is the line $x=0$.",
    ], C.ORANGE)
    ch.term("parallel lines", "lines with the same gradient; they never meet")


def two_points(ch):
    f = flow(ch)
    sec(f, "The line through two points (Lecture 14)", room=560)
    rule_box(f, "gradient through two points", [
        "For points $(x_1, y_1)$ and $(x_2, y_2)$:  $m=\\dfrac{y_2-y_1}{x_2-x_1}$.",
        "{R:Same order top and bottom}: second minus first in both, or first minus second in both.",
    ], C.ORANGE)
    ch.formula(r"m=\frac{y_2-y_1}{x_2-x_1}", "gradient through two points")
    rule_box(f, "equation of the line through two points", [
        "Find $m$ with the gradient formula.",
        "Put $m$ into $y=mx+c$.",
        "Substitute {B:either} point for $x$ and $y$, and solve for $c$.",
        "Write the final equation, and check it with the {B:other} point.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    ex(f, "the line through (4, 4) and (8, 12).")
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
    step(f, r"m=\frac{12-4}{8-4}=\frac84=2", "step 1: gradient formula", size=19)
    step(f, r"y=2x+c", "step 2", size=19)
    step(f, r"4=2\times4+c\ \Rightarrow\ c=-4", "step 3: use (4, 4)", size=19)
    step(f, r"y=2x-4", "step 4. Check (8, 12): 2 × 8 − 4 = 12 ✓", size=21, color=C.GREEN)
    ch.check(sp.solve([4 - (4 * m + c), 12 - (8 * m + c)], [m, c]), {m: 2, c: -4})


def point_gradient(ch):
    f = flow(ch)
    sec(f, "Point-gradient form: the fastest route", room=420)
    rule_box(f, "point-gradient form", [
        "The line with gradient $m$ through the point $(x_1, y_1)$ is  $y-y_1=m(x-x_1)$.",
        "Use it whenever you know {B:one point and the gradient}. Expand the bracket and add $y_1$ to "
        "both sides to get $y=mx+c$.",
        "{R:Watch negative coordinates}: through $(-3, -2)$ it is $y-(-2)=m(x-(-3))$, i.e. $y+2=m(x+3)$.",
    ], C.ORANGE)
    ch.formula(r"y-y_1=m(x-x_1)", "line with gradient m through (x₁, y₁)")
    f.p("It is the gradient formula rearranged: for any point $(x, y)$ on the line, "
        "$\\frac{y-y_1}{x-x_1}=m$. Multiply both sides by $(x-x_1)$.", 13.5, gap=6)
    ex(f, "the same line through (4, 4) with gradient 2.")
    step(f, r"y-4=2(x-4)", "point (4, 4), m = 2", size=19)
    step(f, r"y-4=2x-8", "expand", size=19)
    step(f, r"y=2x-4", "+4 both sides: same answer as before", size=21, color=C.GREEN)
    ch.check(sp.expand(2 * (x - 4) + 4), 2 * x - 4)
    ex(f, "gradient $-\\frac12$ through $(-2, 3)$.")
    step(f, r"y-3=-\tfrac12(x-(-2))=-\tfrac12(x+2)", "", size=19)
    step(f, r"y=-\tfrac12x-1+3=-\tfrac12x+2", "", size=21, color=C.GREEN)
    ch.check(sp.expand(-sp.Rational(1, 2) * (x + 2) + 3), -sp.Rational(1, 2) * x + 2)


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
    rule_box(f, "other forms of a line", [
        "A line may be written $ax+by=d$ or $ax+by+c=0$. To find its gradient and intercept, "
        "{B:rearrange to} $y=mx+c$ (Chapter 14). Shortcut: for $ax+by=d$, $m=-\\frac{a}{b}$.",
        "To write $y=mx+c$ as $ax+by+c=0$ with whole numbers: multiply by the denominators, then move "
        "every term to one side.",
        "{B:Axis crossings:} the line crosses the $y$-axis where $x=0$ and the $x$-axis where $y=0$.",
    ], C.ORANGE)
    step(f, r"2x+3y=12\ \Rightarrow\ 3y=-2x+12", "−2x from both sides", size=19)
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
    ex(f, "write $y=\\frac34x-2$ in the form $ax+by+c=0$.")
    step(f, r"4y=3x-8", "× 4 to clear the fraction", size=19)
    step(f, r"3x-4y-8=0", "move everything to one side", size=19, color=C.GREEN)
    ch.check(sp.solve(3 * x - 4 * y - 8, y), [sp.Rational(3, 4) * x - 2])


def two_lines(ch):
    f = flow(ch)
    sec(f, "Two lines at once: only three things can happen", room=640)
    f.p("Until now every question had {B:one} line. When a second line turns up there is only one new "
        "question: {B:how do the two lines sit next to each other?}", 14, gap=6)
    f.p("Remember what the two numbers do. $m$ is the line's {B:tilt}. $c$ only {B:slides} the line up "
        "or down without turning it. So to compare how two lines tilt, {B:ignore the c's and compare the "
        "m's}. There are only three possible results:", 14, gap=10)
    y_ = f.reserve(246)
    pg = f.pg
    panels = [
        ("PARALLEL", C.BLUE, [(0.5, 1), (0.5, -1.5)],
         "same m, different c\nsame tilt: they never meet\n(train tracks)"),
        ("PERPENDICULAR", C.GREEN, [(2, -1), (-0.5, 1.5)],
         "m's multiply to −1\nmeet at a square corner\n(a + sign, a crossroads)"),
        ("NEITHER", C.RED, [(2, -1), (-2, 3)],
         "any other pair of m's\ncross at a slant\n(a squashed X)"),
    ]
    for k, (name, col, lines, words) in enumerate(panels):
        x0 = L + 14 + k * 166
        ax = Axes(pg, x0, y_ + 6, 140, 140, (-3, 3), (-3, 3))
        ax.grid(1, 1, color="#eeeeee")
        ax.axes(None, None, 0, 0, color=C.GREY)
        for (mv, cv), lc in zip(lines, (C.ORANGE, C.BLUE)):
            ax.curve(lambda t, mv=mv, cv=cv: mv * t + cv, color=lc, width=2.2)
        if k == 0:
            stair(ax, -2, 0, 2, 1, labels=False)
            stair(ax, 0, -1.5, 2, 1, labels=False)
        else:
            ax.dot(1, 1, C.INK, 3.5)
        if k == 1:
            corner(ax, 1, 1, (1, 2), (-2, 1))
        pg.text(x0, y_ + 158, name, 13, col, F.BOLD, w=140, align="center")
        pg.note(x0 - 12, y_ + 178, words, C.INK, 14, w=164, align="center")
    ch.check_true(sp.solve(2 * x - 1 - (-x / 2 + sp.Rational(3, 2)), x) == [1], "perpendicular panel meets at x=1")
    ch.check(2 * -sp.Rational(1, 2), -1)

    f.text("The words, decoded", 14, C.ORANGE, F.BOLD, gap=6)
    rules_table(f, ["Word", "Picture it as", "What it means for the m's"], [
        ["{B:Parallel}",
         "Train tracks, lanes on a motorway, the lines on lined paper. Look at the word itself: "
         "para{B:ll}el has two parallel l's in the middle.",
         "Same tilt: $m_1=m_2$. The c's are different (same $m$ {B:and} same $c$ is just one line "
         "drawn twice). They never meet."],
        ["{B:Perpendicular}\n(symbol ⊥)",
         "The corner of a page, a + sign, a crossroads, a wall standing on the floor. The symbol ⊥ is "
         "exactly that: a wall on a floor. The word comes from the Latin for a builder's {B:plumb "
         "line}, a weight on a string that hangs straight down and so meets level ground at a "
         "perfect square corner.",
         "They meet at a square corner (90°). Flip one gradient and change its sign to get the "
         "other: $m_2=-\\frac{1}{m_1}$."],
        ["{B:Neither}", "Two roads that cross at a slant.",
         "Any other pair of $m$'s. They meet once, but not at a square corner."],
    ], widths=[100, 215, 180], color=C.ORANGE)
    f.p("{B:Same meaning, different costume:} \"at right angles to\", \"normal to\" (Chapter 34) and "
        "\"orthogonal\" all mean {B:perpendicular}.", 13.5, gap=6)
    f.p("{B:Name tags.} With two lines around, the working needs to say which is which. $L_1$ and $L_2$ "
        "just mean \"line 1\" and \"line 2\"; $m_1$ is \"the gradient of line 1\"; $m_{AB}$ is \"the "
        "gradient of the line from A to B\". The small numbers and letters are labels, not something "
        "to calculate.", 13.5, gap=10)
    go(f, "y = 3x + 1 and y = 3x − 4. Before any algebra: will these two lines ever meet? Explain using "
          "only the numbers in the equations.")
    f.text("Answer: no. Both have m = 3, so they tilt exactly the same way; c = 1 and c = −4 only put "
           "one 5 units above the other. They are parallel.", 10.5, C.GREY, gap=12)


def parallel_perp(ch):
    f = flow(ch)
    sec(f, "Parallel and perpendicular: the gradient rules", room=300)
    rule_box(f, "parallel and perpendicular gradients", [
        "{B:Parallel} lines have {B:equal gradients}: $m_1=m_2$. (Same $m$ and same $c$ means it is the same "
        "line.)",
        "{B:Perpendicular} lines (meeting at 90°) have gradients that {B:multiply to −1}: $m_1\\times m_2=-1$.",
        "So the perpendicular gradient is the {B:negative reciprocal}: $m_2=-\\dfrac{1}{m_1}$. "
        "Flip the fraction {B:and} change the sign: $3\\to-\\frac13$, $-\\frac25\\to\\frac52$.",
        "Exception: a horizontal line ($m=0$) and a vertical line (no gradient) are perpendicular, "
        "but the product rule can't be used for them.",
    ], C.ORANGE)
    ch.formula(r"m_1=m_2", "parallel lines")
    ch.formula(r"m_1m_2=-1\quad\Leftrightarrow\quad m_2=-\frac{1}{m_1}", "perpendicular lines")
    ch.term("perpendicular", "meeting at a right angle (90°); for lines, gradients multiply to −1")
    f.need(330)
    f.p("{B:Why \"flip and change the sign\"? Give the staircase a quarter turn.}", 14, gap=4)
    f.p("The orange line's staircase goes across 1, up 2, so $m=2$. Now turn the whole staircase a "
        "quarter turn clockwise, like turning a page on its side, and watch its two sides:", 13.5, gap=6)
    y_ = f.reserve(232)
    pg = f.pg
    ax = Axes(pg, L + 16, y_ + 6, 215, 215, (-2.5, 4), (-2.5, 4))
    ax.grid(1, 1)
    ax.curve(lambda t: 2 * t, color=C.ORANGE, width=2.2)
    ax.curve(lambda t: -t / 2, color=C.BLUE, width=2.2)
    ax.seg(0, 0, 1, 0, C.GREEN, 2.4)
    ax.seg(1, 0, 1, 2, C.RED, 2.4)
    ax.seg(0, 0, 0, -1, C.GREEN, 2.4)
    ax.seg(0, -1, 2, -1, C.RED, 2.4)
    ax.label(0.5, 0, "{G:1}", 12, dx=-4, dy=2)
    ax.label(1, 1, "{R:2}", 12, dx=5, dy=-8)
    ax.label(0, -0.5, "{G:1}", 12, dx=-12, dy=-8)
    ax.label(1, -1, "{R:2}", 12, dx=-4, dy=2)
    corner(ax, 0, 0, (-1, -2), (-2, 1), s=10)
    ax.dot(0, 0, C.INK, 3)
    r_ = ax.X(3) - ax.X(0)
    pg.arc(ax.X(0), ax.Y(0), r_, 58, -20, C.PURPLE, 1.5, arrow=True)
    pg.note(ax.X(0) + r_ * 1.0, ax.Y(0) - r_ * 0.78, "quarter\nturn", C.PURPLE, 14, solid=False)
    nx = L + 262
    pg.note(nx, y_ + 4, "Before: across 1, up 2.\nOrange m = 2/1 = 2", C.ORANGE, 16, w=R - nx)
    pg.note(nx, y_ + 58, "After: across 2, down 1.\nBlue m = −1/2", C.BLUE, 16, w=R - nx)
    pg.note(nx, y_ + 112, "The 1 and the 2 swapped\nplaces: that's the FLIP.", C.GREEN, 16, w=R - nx)
    pg.note(nx, y_ + 166, "Uphill turned into downhill:\nthat's the MINUS sign.", C.RED, 16, w=R - nx)
    ch.check(2 * -sp.Rational(1, 2), -1)
    f.p("So a perpendicular gradient is always the old one {B:flipped} (rise and run swap places) {B:with "
        "its sign changed} (uphill becomes downhill). Multiply the pair and the numbers cancel, leaving "
        "only the minus: $2\\times(-\\frac12)=-1$. That is all \"$m_1m_2=-1$\" is saying.", 13.5, gap=10)
    rule_box(f, "does my perpendicular gradient look right?", [
        "A perpendicular pair always has {B:one uphill and one downhill} line (opposite signs), and "
        "{B:if one is steep the other is gentle} (one gradient bigger than 1 in size, the other smaller).",
        "$2$ and $-\\frac12$: pass.  $2$ and $-2$: fail (both steep).  $2$ and $\\frac12$: fail (both "
        "uphill). The only pair that is the same size is $1$ and $-1$.",
    ], C.GREEN, tag="SENSE CHECK")
    go(f, "Hold two pens crossed in a + shape and tilt the whole + slowly. One pen always points uphill "
          "while the other points downhill, and as one gets steeper the other gets flatter. That is the "
          "minus sign and the flip, in your hands.")
    rule_box(f, "parallel, perpendicular or neither?", [
        "Get each gradient: rearrange each equation to $y=mx+c$, or use the gradient formula on two points.",
        "If $m_1=m_2$: {B:parallel}.  If $m_1\\times m_2=-1$: {B:perpendicular}.  Otherwise: {B:neither}.",
        "Write the conclusion as a sentence that quotes the numbers (this is the \"proof\" an examiner "
        "wants).",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")


def two_line_questions(ch):
    f = flow(ch)
    sec(f, "Two-line questions are one-line questions in disguise", room=300)
    f.p("A question with two lines looks like twice the work. It isn't. Every one is one of {B:three "
        "kinds}, and each kind turns straight back into things you can already do with one line:",
        14, gap=8)
    rules_table(f, ["Kind", "It sounds like", "What you actually do"], [
        ["{B:1. Compare}",
         "\"Show that these lines are parallel.\" \"Parallel, perpendicular or neither?\" \"Show the "
         "triangle has a right angle.\"",
         "Find each line's $m$ on its own (a one-line job, done twice). Then ask: are they equal? Do "
         "they multiply to −1?"],
        ["{B:2. Build}",
         "\"Find the line through $P$ parallel (or perpendicular) to $L$.\" \"Find the perpendicular "
         "bisector.\"",
         "Take $m$ from the given line. Keep it (parallel), or flip it and change its sign "
         "(perpendicular). Now you have {B:one point and one gradient}: $y-y_1=m(x-x_1)$."],
        ["{B:3. Meet}", "\"Where do the lines meet / cross / intersect?\"",
         "At the crossing point both equations are true, so set them equal and solve."],
    ], widths=[82, 198, 215], color=C.ORANGE)
    f.p("{B:The big idea for Build questions:} the line you are given is only a {B:gradient donor}. "
        "Take its $m$ and ignore the rest of it, especially its $c$: your new line goes through a "
        "different point, so it gets its own $c$.", 13.5, gap=10)
    f.text("Decoder: what the scary words tell you to do", 14, C.ORANGE, F.BOLD, gap=6)
    rules_table(f, ["When the question says...", "...it means"], [
        ["\"parallel to\"", "use the {B:same} $m$"],
        ["\"perpendicular to\", \"at right angles to\", \"normal to\", ⊥",
         "flip $m$ and change its sign: $-\\frac{1}{m}$"],
        ["\"passes through $(a, b)$\", \"$(a, b)$ lies on\"", "put $x=a$ and $y=b$ into the equation"],
        ["\"meet\", \"cross\", \"intersect\", \"point of intersection\"", "set the two equations equal"],
        ["\"bisect\", \"bisector\"", "cut exactly in half: you need the {B:midpoint}"],
        ["\"show that\", \"prove\"", "do the working, then finish with one sentence that quotes the numbers"],
    ], widths=[250, 245], color=C.ORANGE)
    ex(f, "$L_1$ has equation $4x+2y=5$. $L_2$ passes through $(1, 4)$ and is perpendicular to $L_1$. "
          "Find the equation of $L_2$.")
    f.p("{R:Translate it into words first.} It's a {B:Build}. $L_1$ is only the gradient donor. "
        "\"Perpendicular\" means flip and change the sign. \"Passes through (1, 4)\" is my point.",
        13.5, gap=6)
    step(f, r"2y=-4x+5\ \Rightarrow\ y=-2x+2.5", "donor: m₁ = −2 (its c is not needed)", size=18)
    step(f, r"m_2=+\tfrac12", "flip 2 to ½, and − becomes +", size=18)
    step(f, r"y-4=\tfrac12(x-1)\ \Rightarrow\ y=\tfrac12x+3.5", "point (1, 4), gradient ½", size=18,
         color=C.GREEN)
    ch.check(sp.solve(4 * x + 2 * y - 5, y), [sp.Rational(5, 2) - 2 * x])
    ch.check(sp.expand(sp.Rational(1, 2) * (x - 1) + 4), x / 2 + sp.Rational(7, 2))
    f.p("{G:Sense check:} $-2\\times\\frac12=-1$ ✓. One line downhill, one uphill; one steep, one gentle ✓. "
        "Does (1, 4) fit? $\\frac12+3.5=4$ ✓", 13.5)


def proofs(ch):
    f = flow(ch)
    sec(f, "Proving lines are parallel or perpendicular", room=420)
    ex(f, "show that $y=3x-2$ and $6x-2y=7$ are parallel.")
    step(f, r"6x-2y=7\ \Rightarrow\ 2y=6x-7\ \Rightarrow\ y=3x-3.5", "rearrange the second line", size=18)
    step(f, r"m_1=3,\quad m_2=3", "read the gradients", size=18)
    f.p("{G:Conclusion:} both lines have gradient 3 (and different intercepts), so they are parallel.",
        13.5, gap=10)
    ch.check(sp.solve(6 * x - 2 * y - 7, y), [3 * x - sp.Rational(7, 2)])
    ex(f, "are $2x+3y=6$ and $3x-2y=4$ parallel, perpendicular or neither?")
    step(f, r"3y=-2x+6\ \Rightarrow\ y=-\tfrac23x+2", "m₁ = −2/3", size=18)
    step(f, r"-2y=-3x+4\ \Rightarrow\ y=\tfrac32x-2", "m₂ = 3/2 (÷ −2 flips every sign)", size=18)
    step(f, r"m_1m_2=-\tfrac23\times\tfrac32=-1", "", size=18)
    f.p("{G:Conclusion:} the product of the gradients is −1, so the lines are perpendicular.", 13.5, gap=10)
    ch.check(sp.Rational(-2, 3) * sp.Rational(3, 2), -1)
    ex(f, "$y=2x+1$ and $y=-2x+5$.")
    f.p("$m_1=2$, $m_2=-2$. Not equal, and $2\\times(-2)=-4\\neq-1$. {G:Neither}: they cross, but not at "
        "a right angle. ({R:Changing only the sign is not enough} for perpendicular; you must also flip.)",
        13.5, gap=10)
    ex(f, "A(1, 2), B(4, 8), C(0, 5), D(6, 2). Show AB is perpendicular to CD.")
    step(f, r"m_{AB}=\frac{8-2}{4-1}=\frac63=2", "", size=18)
    step(f, r"m_{CD}=\frac{2-5}{6-0}=\frac{-3}{6}=-\tfrac12", "", size=18)
    step(f, r"m_{AB}\times m_{CD}=2\times(-\tfrac12)=-1", "so AB ⟂ CD", size=18, color=C.GREEN)
    ch.check(grad((1, 2), (4, 8)) * grad((0, 5), (6, 2)), -1)
    ex(f, "show the triangle A(1, 1), B(3, 5), C(7, 3) has a right angle at B.")
    step(f, r"m_{AB}=\frac{5-1}{3-1}=2,\qquad m_{BC}=\frac{3-5}{7-3}=-\tfrac12", "", size=18)
    f.p("{G:Conclusion:} $2\\times(-\\frac12)=-1$, so AB is perpendicular to BC: the angle at B is 90°.",
        13.5)
    ch.check(grad((1, 1), (3, 5)) * grad((3, 5), (7, 3)), -1)


def through_point(ch):
    f = flow(ch)
    sec(f, "Parallel or perpendicular lines through a point", room=420)
    rule_box(f, "line parallel / perpendicular to a given line, through a given point", [
        "Find the gradient of the given line (rearrange to $y=mx+c$ if needed).",
        "Parallel: use the {B:same} gradient. Perpendicular: use $-\\frac{1}{m}$.",
        "Use $y-y_1=m(x-x_1)$ with the given point, then tidy into $y=mx+c$.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    ex(f, "the line parallel to $y=3x-1$ through (2, 9).")
    step(f, r"m=3:\ y-9=3(x-2)\ \Rightarrow\ y=3x+3", "same gradient", size=19, color=C.GREEN)
    ch.check(sp.expand(3 * (x - 2) + 9), 3 * x + 3)
    ex(f, "the line perpendicular to $2x+3y=6$ through (4, 1).")
    step(f, r"y=-\tfrac23x+2\ \Rightarrow\ m=-\tfrac23", "rearrange the given line", size=19)
    step(f, r"m_\perp=-\frac{1}{-\frac23}=\tfrac32", "negative reciprocal", size=19)
    step(f, r"y-1=\tfrac32(x-4)\ \Rightarrow\ y=\tfrac32x-5", "", size=19, color=C.GREEN)
    ch.check(sp.expand(sp.Rational(3, 2) * (x - 4) + 1), sp.Rational(3, 2) * x - 5)
    f.need(300)
    f.p("What those two answers look like (grey dashed = the given line, red dot = the given point):",
        13.5, gap=6)
    y_ = f.reserve(250)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 6, 170, 170, (-1, 4), (-2, 11))
    ax.grid(1, 2, color="#eeeeee")
    ax.axes(None, None, 0, 0, color=C.GREY)
    ax.curve(lambda t: 3 * t - 1, color=C.GREY, width=1.8, dash=(5, 3))
    ax.curve(lambda t: 3 * t + 3, color=C.ORANGE, width=2.2)
    ax.arrow(0.6, 0.8, 0.6, 4.8, C.PURPLE, 1.6, head=6)
    ax.dot(2, 9, C.RED, 4)
    pg.note(L + 10, y_ + 190, "Parallel: same tilt. Slide it\nup until it hits (2, 9).", C.ORANGE, 15,
            w=220, align="center")
    gx = -sp.Rational(2, 3) * x + 2
    meet = sp.solve(gx - (sp.Rational(3, 2) * x - 5), x)[0]
    ax = Axes(pg, L + 290, y_ + 6, 170, 170, (-1, 6), (-3, 4))
    ax.grid(1, 1, color="#eeeeee")
    ax.axes(None, None, 0, 0, color=C.GREY)
    ax.curve(lambda t: -2 * t / 3 + 2, color=C.GREY, width=1.8, dash=(5, 3))
    ax.curve(lambda t: 1.5 * t - 5, color=C.BLUE, width=2.2)
    corner(ax, float(meet), float(gx.subs(x, meet)), (2, 3), (3, -2))
    ax.dot(4, 1, C.RED, 4)
    pg.note(L + 265, y_ + 190, "Perpendicular: turn it a quarter\nturn, then slide it through (4, 1).",
            C.BLUE, 15, w=230, align="center")
    rule_box(f, "perpendicular bisector of AB", [
        "The line that cuts AB in half at a right angle. It passes through the {B:midpoint} of AB with "
        "gradient $-\\frac{1}{m_{AB}}$.",
    ], C.ORANGE)
    ex(f, "the perpendicular bisector of A(2, 1) and B(6, 5).")
    step(f, r"M=\left(\tfrac{2+6}{2},\tfrac{1+5}{2}\right)=(4,3)", "midpoint (next section)", size=19)
    step(f, r"m_{AB}=\frac{5-1}{6-2}=1\ \Rightarrow\ m_\perp=-1", "", size=19)
    step(f, r"y-3=-(x-4)\ \Rightarrow\ y=-x+7", "", size=19, color=C.GREEN)
    ch.check(sp.expand(-(x - 4) + 3), -x + 7)
    ch.term("perpendicular bisector", "the line through the midpoint of AB at right angles to AB")


def midpoint_distance(ch):
    f = flow(ch)
    sec(f, "Midpoint and distance", room=480)
    rule_box(f, "midpoint and distance between two points", [
        "{B:Midpoint} of $(x_1, y_1)$ and $(x_2, y_2)$: average the $x$s and average the $y$s: "
        "$M=\\left(\\dfrac{x_1+x_2}{2},\\ \\dfrac{y_1+y_2}{2}\\right)$.",
        "{B:Distance}: the run and rise are the two short sides of a right-angled triangle, so by "
        "Pythagoras ($a^2+b^2=c^2$, Chapter 28): $d=\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$.",
        "Missing endpoint: if M is the midpoint of A and B, then $B=(2x_M-x_A,\\ 2y_M-y_A)$.",
    ], C.ORANGE)
    ch.formula(r"M=\left(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2}\right)", "midpoint")
    ch.formula(r"d=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}", "distance between two points")
    ch.term("midpoint", "the point halfway between two points: average the x-coordinates and the y-coordinates")
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 6, 200, 135, (0, 8), (0, 11))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 2, size=8)
    ax.seg(1, 2, 7, 10, C.ORANGE, 2)
    stair(ax, 1, 2, 6, 8)
    ax.dot(1, 2, C.BLUE, 4)
    ax.dot(7, 10, C.BLUE, 4)
    ax.dot(4, 6, C.PURPLE, 4)
    ax.label(1, 2, "{B:(1, 2)}", 10, dx=-10, dy=-22)
    ax.label(7, 10, "{B:(7, 10)}", 10, dx=-54, dy=-6)
    ax.label(4, 6, "{P:M (4, 6)}", 10, dx=-60, dy=-6)
    pg.note(L + 260, y_ + 10, "midpoint: ((1 + 7)/2, (2 + 10)/2)\n= (4, 6)", C.PURPLE, 15)
    pg.note(L + 260, y_ + 62, "distance: run 6, rise 8\n√(6² + 8²) = √100 = 10", C.ORANGE, 15)
    ch.check(sp.sqrt(6 ** 2 + 8 ** 2), 10)
    ex(f, "M(3, −1) is the midpoint of A(1, 4) and B. Find B.")
    step(f, r"\tfrac{1+x_B}{2}=3\Rightarrow x_B=5;\quad \tfrac{4+y_B}{2}=-1\Rightarrow y_B=-6", "", size=18)
    f.p("So $B=(5,-6)$. Check: the midpoint of (1, 4) and (5, −6) is (3, −1) ✓", 13.5)
    ch.check(sp.Rational(1 + 5, 2), 3)
    ch.check(sp.Rational(4 - 6, 2), -1)
    ch.term("distance between two points", "√((x₂ − x₁)² + (y₂ − y₁)²): Pythagoras on the run and rise")


def intersection(ch):
    f = flow(ch)
    sec(f, "Where two lines cross", room=400)
    rule_box(f, "intersection of two lines", [
        "At the crossing point both equations are true at once, so solve them as {B:simultaneous "
        "equations} (Chapter 15).",
        "If both start $y=$, set the right-hand sides equal and solve for $x$. Otherwise substitute one "
        "into the other.",
        "Put $x$ back into either equation to get $y$. The answer is a {B:point} $(x, y)$.",
        "Parallel lines (same $m$, different $c$) never cross: the equation has no solution.",
    ], C.ORANGE)
    ex(f, "where do $y=2x-4$ and $y=-x+5$ meet?")
    step(f, r"2x-4=-x+5", "both equal y, so equal each other", size=19)
    step(f, r"3x=9\ \Rightarrow\ x=3", "+x and +4 both sides", size=19)
    step(f, r"y=2(3)-4=2", "back into the first line", size=19)
    f.p("They meet at {G:(3, 2)}. Check in the second line: $-3+5=2$ ✓", 13.5, gap=8)
    ch.check(sp.solve([y - (2 * x - 4), y - (-x + 5)], [x, y]), {x: 3, y: 2})
    ex(f, "$2x+3y=12$ and $y=x-1$.")
    step(f, r"2x+3(x-1)=12\ \Rightarrow\ 5x=15\ \Rightarrow\ x=3,\ y=2", "substitute y = x − 1", size=18)
    ch.check(sp.solve([2 * x + 3 * y - 12, y - (x - 1)], [x, y]), {x: 3, y: 2})
    ch.term("intersection", "the point where two lines (or curves) cross: solve their equations simultaneously")


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown: partial-information problems", room=520)
    f.p("Exam questions often give you {B:part} of the information about a line and a letter (often "
        "$k$, $a$ or $p$) for something missing. They are all solved the same way:", 13.5, gap=6)
    rule_box(f, "partial-information problems", [
        "Write down what each piece of information means as an equation: a point on the line means its "
        "coordinates satisfy the equation; a given gradient means the gradient formula equals that "
        "number; parallel or perpendicular gives you $m$.",
        "Solve the equation for the unknown.",
        "Check by substituting back.",
    ], C.ORANGE, numbered=True, tag="PROCEDURE")
    ex(f, "the point $(k, 7)$ lies on $y=2x-3$. Find $k$.")
    step(f, r"7=2k-3\ \Rightarrow\ 2k=10\ \Rightarrow\ k=5", "put x = k, y = 7", size=19)
    ch.check(sp.solve(7 - (2 * k - 3), k), [5])
    ex(f, "does (3, 5) lie on $y=2x-1$? Does (4, 6)?")
    f.p("$2(3)-1=5$ ✓ so (3, 5) is on the line. $2(4)-1=7\\neq6$, so (4, 6) is not.", 13.5, gap=8)
    ex(f, "the gradient from $(2, k)$ to $(5, 11)$ is 3. Find $k$.")
    step(f, r"\frac{11-k}{5-2}=3\ \Rightarrow\ 11-k=9\ \Rightarrow\ k=2", "gradient formula = 3", size=19)
    ch.check(sp.solve((11 - k) / 3 - 3, k), [2])
    ex(f, "$y=kx+4$ is parallel to $6x-2y=1$. Find $k$. What if it were perpendicular?")
    step(f, r"y=3x-\tfrac12\Rightarrow m=3", "rearrange the given line", size=19)
    f.p("Parallel: $k=3$. Perpendicular: $k=-\\frac13$.", 13.5, gap=8)
    ex(f, "a line passes through (1, 3) and has $y$-intercept 5. Find its gradient.")
    step(f, r"3=m(1)+5\ \Rightarrow\ m=-2", "c = 5; use (1, 3)", size=19)
    ch.check(sp.solve(3 - (m + 5), m), [-2])
    ex(f, "the line $ax+2y=8$ passes through (2, 1). Find $a$.")
    step(f, r"a(2)+2(1)=8\ \Rightarrow\ a=3", "", size=19)
    ch.check(sp.solve(2 * k + 2 - 8, k), [3])
    rule_box(f, "collinear points", [
        "Three points A, B, C are {B:collinear} (on one straight line) when $m_{AB}=m_{BC}$: the same "
        "gradient, and they share the point B.",
    ], C.ORANGE)
    ex(f, "are A(1, 1), B(3, 5), C(6, 11) collinear?")
    step(f, r"m_{AB}=\tfrac{4}{2}=2,\quad m_{BC}=\tfrac{6}{3}=2", "equal, so yes: collinear", size=19)
    ch.check(grad((1, 1), (3, 5)), grad((3, 5), (6, 11)))
    ex(f, "find $k$ so that (1, 1), (3, 5) and (5, k) are collinear.")
    step(f, r"\frac{k-5}{5-3}=2\ \Rightarrow\ k=9", "gradient must also be 2", size=19)
    ch.check(sp.solve((k - 5) / 2 - 2, k), [9])
    ch.term("collinear", "lying on the same straight line")


def common_mistakes(ch):
    f = flow(ch)
    sec(f, "Mistakes to avoid", room=420)
    mistakes(f, [
        (r"m=\frac{x_2-x_1}{y_2-y_1}", r"m=\frac{y_2-y_1}{x_2-x_1}", "rise over run: the y's go on top"),
        (r"m=\frac{12-4}{4-8}", r"m=\frac{12-4}{8-4}", "same order top and bottom"),
        (r"2x+3y=6:\ m=2", r"y=-\tfrac23x+2:\ m=-\tfrac23", "rearrange to y = mx + c before reading m"),
        (r"m=3\Rightarrow m_\perp=-3", r"m=3\Rightarrow m_\perp=-\tfrac13", "flip AND change sign"),
        (r"(-3,-2):\ y-2=m(x-3)", r"(-3,-2):\ y+2=m(x+3)", "subtracting a negative gives +"),
    ])


def science(ch):
    f = flow(ch)
    sec(f, "Straight lines in real life: temperature", room=300)
    f.p("Fahrenheit and Celsius are linked by a straight line: $F = 1.8C + 32$. Water freezes at 0 °C, "
        "which is $c = 32$ °F; every 1 °C warmer is 1.8 °F warmer.", 14, gap=6)
    step(f, r"F=1.8(100)+32=212", "boiling point: 100 °C = 212 °F ✓", size=19)
    step(f, r"C=\frac{F-32}{1.8}", "undo it for the reverse conversion (Chapter 14)", size=19)
    ch.check_num(1.8 * 100 + 32, 212)
    f.p("Any time a question says \"a fixed amount plus so much per...\", think $y = mx + c$.", 13.5,
        C.BROWN)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Straight line", r"y=mx+c", "$m$ = gradient, $c$ = $y$-intercept; rearrange to this form first"),
        ("Gradient", r"m=\frac{y_2-y_1}{x_2-x_1}", "same order top and bottom"),
        ("Point-gradient form", r"y-y_1=m(x-x_1)", "one point and the gradient"),
        ("Horizontal / vertical", r"y=b\ \ (m=0),\qquad x=a\ \ (m\text{ undefined})", None),
        ("Parallel", r"m_1=m_2", None),
        ("Perpendicular", r"m_1m_2=-1,\qquad m_2=-\frac{1}{m_1}", "except horizontal with vertical"),
        ("Perpendicular sense check", None, "one uphill and one downhill; one steep and one gentle"),
        ("Two-line questions", None, "Compare (find both $m$'s), Build (borrow $m$, add a point), "
         "Meet (set equal)"),
        ("Midpoint", r"\left(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2}\right)", None),
        ("Distance", r"\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}", None),
        ("Axis crossings", None, "put $x=0$ for the $y$-intercept; put $y=0$ for the $x$-intercept"),
        ("Intersection", None, "solve the two equations simultaneously"),
        ("Point on a line", None, "its coordinates make the equation true"),
        ("Collinear", r"m_{AB}=m_{BC}", None),
        ("Perpendicular bisector", None, "through the midpoint, gradient $-1/m_{AB}$"),
    ], C.ORANGE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Answers in grey; worked solutions for 12 onwards on the next page.", 13.5, gap=10)
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
        ("Parallel, perpendicular or neither?", ["y = 4x + 1 and y = 4x − 7", "y = 2x + 3 and x + 2y = 6",
                                                 "3x + y = 2 and y = 3x + 1", "A(0, 1), B(2, 7), C(1, 5), D(4, 4): AB and CD"],
         "12. parallel   13. perpendicular   14. neither   15. perpendicular"),
        ("Lines through a point", ["Parallel to y = 2x + 7 through (3, 1)", "Perpendicular to y = 2x + 7 through (4, 0)",
                                   "Perpendicular bisector of (0, 0) and (4, 8)"],
         "16. y = 2x − 5   17. y = −x/2 + 2   18. y = −x/2 + 5"),
        ("Midpoint, distance, intersection", ["Midpoint of (−2, 3) and (6, 9)", "Distance from (1, 1) to (4, 5)",
                                              "M(2, 5) is the midpoint of A(−1, 3) and B. Find B.",
                                              "Where do y = 3x − 2 and y = x + 4 meet?"],
         "19. (2, 6)   20. 5   21. (5, 7)   22. (3, 7)"),
        ("Find the unknown", ["(k, 11) lies on y = 3x − 4. Find k.", "The gradient from (1, k) to (4, 10) is 2. Find k.",
                              "y = kx − 3 is perpendicular to y = 4x + 1. Find k.", "ax + 3y = 12 passes through (3, 2). Find a.",
                              "Are (0, 2), (2, 8), (5, 17) collinear?",
                              "Gradient −2, through (3, 1): equation, and where it crosses the x-axis?"],
         "23. k = 5   24. k = 4   25. k = −1/4   26. a = 2   27. yes   28. y = −2x + 7; (3.5, 0)"),
    ]
    kq = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{kq}. {qq}", 13, gap=5, x=L + 14)
            kq += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(sp.solve(4 * x + 2 * y - 10, y), [5 - 2 * x])
    ch.check(sp.Rational(11 - 2, 4 - 1), 3)
    ch.check(sp.solve([2 - (m + c), 11 - (4 * m + c)], [m, c]), {m: 3, c: -1})
    ch.check(sp.solve([7 - (-2 * m + c), -1 - (2 * m + c)], [m, c]), {m: -2, c: 3})
    ch.check([sp.Rational(15, 5), sp.Rational(15, 3)], [3, 5])
    ch.check(-1 / sp.Rational(-2, 3), sp.Rational(3, 2))


def worked(ch):
    f = flow(ch)
    sec(f, "Worked solutions, 12 to 28", fresh=True)
    rows = [
        ("12", r"m_1=4=m_2", "parallel"),
        ("13", r"x+2y=6\Rightarrow y=-\tfrac12x+3;\ \ 2\times(-\tfrac12)=-1", "perpendicular"),
        ("14", r"y=-3x+2;\ \ -3\times3=-9", "neither: not equal, product not −1"),
        ("15", r"m_{AB}=\tfrac{6}{2}=3,\ m_{CD}=\tfrac{-1}{3};\ \ 3\times(-\tfrac13)=-1", "perpendicular"),
        ("16", r"y-1=2(x-3)\Rightarrow y=2x-5", ""),
        ("17", r"m_\perp=-\tfrac12;\ y-0=-\tfrac12(x-4)\Rightarrow y=-\tfrac12x+2", ""),
        ("18", r"M=(2,4),\ m=2,\ m_\perp=-\tfrac12;\ y-4=-\tfrac12(x-2)\Rightarrow y=-\tfrac12x+5", ""),
        ("19", r"\left(\tfrac{-2+6}{2},\tfrac{3+9}{2}\right)=(2,6)", ""),
        ("20", r"\sqrt{3^2+4^2}=\sqrt{25}=5", ""),
        ("21", r"B=(2\times2-(-1),\ 2\times5-3)=(5,7)", ""),
        ("22", r"3x-2=x+4\Rightarrow x=3,\ y=7", ""),
        ("23", r"11=3k-4\Rightarrow k=5", ""),
        ("24", r"\tfrac{10-k}{3}=2\Rightarrow k=4", ""),
        ("25", r"4k=-1\Rightarrow k=-\tfrac14", "perpendicular: product −1"),
        ("26", r"3a+6=12\Rightarrow a=2", ""),
        ("27", r"\tfrac{8-2}{2}=3,\ \tfrac{17-8}{3}=3", "equal gradients: collinear"),
        ("28", r"1=-6+c\Rightarrow y=-2x+7;\ \ 0=-2x+7\Rightarrow x=3.5", ""),
    ]
    for n, lat, why in rows:
        pg = f.pg
        s = 16
        while s > 11 and pg.eq_size(lat, s)[0] > W - 160:
            s -= 0.5
        w_, h_, _ = pg.eq_size(lat, s)
        yy = f.reserve(h_ + 10)
        pg = f.pg
        pg.text(L, yy + h_ / 2 - 8, n + ".", 13, C.ORANGE, F.BOLD)
        pg.eq(L + 32, yy, lat, s)
        if why:
            pg.note(L + 44 + w_, yy + h_ / 2 - 10, why, C.RED, 15, w=R - (L + 44 + w_))
    ch.check(sp.solve(x + 2 * y - 6, y), [3 - x / 2])
    ch.check(grad((0, 1), (2, 7)) * grad((1, 5), (4, 4)), -1)
    ch.check(sp.expand(2 * (x - 3) + 1), 2 * x - 5)
    ch.check(sp.expand(-sp.Rational(1, 2) * (x - 4)), -x / 2 + 2)
    ch.check(sp.expand(-sp.Rational(1, 2) * (x - 2) + 4), -x / 2 + 5)
    ch.check(sp.sqrt(3 ** 2 + 4 ** 2), 5)
    ch.check(sp.solve([y - (3 * x - 2), y - (x + 4)], [x, y]), {x: 3, y: 7})
    ch.check(sp.solve(11 - (3 * k - 4), k), [5])
    ch.check(sp.solve((10 - k) / 3 - 2, k), [4])
    ch.check(sp.solve(4 * k + 1, k), [-sp.Rational(1, 4)])
    ch.check(sp.solve(3 * k + 6 - 12, k), [2])
    ch.check(grad((0, 2), (2, 8)), grad((2, 8), (5, 17)))
    ch.check(sp.solve(-2 * x + 7, x), [sp.Rational(7, 2)])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    taxi(ch)
    gradient(ch)
    two_points(ch)
    point_gradient(ch)
    downhill(ch)
    other_forms(ch)
    two_lines(ch)
    parallel_perp(ch)
    two_line_questions(ch)
    proofs(ch)
    through_point(ch)
    midpoint_distance(ch)
    intersection(ch)
    find_unknown(ch)
    common_mistakes(ch)
    science(ch)
    summary(ch)
    your_turn(ch)
    worked(ch)
