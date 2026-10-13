"""Chapter 19 - Graphs of functions. Coordinates as a game of Battleship, table -> dots -> curve,
reading a graph both ways, even functions fold and odd functions spin, family portraits of the
power functions, dominance when you zoom, and sliding graphs around."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step, title_block

ORDER = 19
NUM = 19
TITLE = "Graphs of functions"
SHORT = "Graphs"
SLUG = "Graphs"
ACCENT = C.TEAL
REQUIRES = ["function", "function-notation", "negative-numbers", "powers", "negative-powers", "fractional-powers",
            "roots", "substitution", "completing-the-square", "quadratic-equation", "domain", "solution"]
INTRODUCES = ["coordinates", "axes", "quadrants", "plotting", "graph-of-function", "intercepts", "even-function",
              "odd-function", "asymptote", "dominance", "graph-transformations", "vertex-form"]

PAPER = "#fafefe"
x = sp.Symbol("x")


def icon(pg, x0, y0):
    pg.line(x0 + 2, y0 + 16, x0 + 17, y0 + 16, C.TEAL, 1.1)
    pg.line(x0 + 2, y0 + 16, x0 + 2, y0 + 1, C.TEAL, 1.1)
    pg.poly([(x0 + 3 + i * 1.4, y0 + 15 - (i * 1.4) ** 2 / 14) for i in range(11)], C.TEAL, 1.3)


def sec(f, t, **kw):
    section(f, t, C.TEAL, icon, **kw)


def panel(pg, x0, y0, w, h, xr, yr, fns, title=None, ticks=0):
    ax = Axes(pg, x0, y0, w, h, xr, yr)
    ax.grid(1, 1, color="#e6eaee")
    ax.axes(None, None, ticks, ticks, size=8)
    for fn, col, lab in fns:
        ax.curve(fn, color=col, width=1.8)
    if title:
        pg.text(x0 + w / 2, y0 + h + 8, title, 11.5, C.TEAL, F.BOLD, align="center")
    return ax


def safe(fn):
    def g(t):
        try:
            return fn(t)
        except (ValueError, ZeroDivisionError):
            return None
    return g


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 19, "Graphs of functions", "a picture of every input and output at once",
                     C.TEAL, PAPER)
    x0, y0, s = L + 30, 200, 22
    for i in range(8):
        for j in range(8):
            pg.rect(x0 + i * s, y0 + j * s, s, s, "#b2dfdb", 0.6, fillcolor="#e0f2f1" if (i + j) % 2 else "#ffffff")
    for k in range(3):
        pg.rect(x0 + (3 + k) * s + 3, y0 + 5 * s + 3, s - 6, s - 6, C.GREY, 1, fillcolor="#b0bec5", r=3)
    pg.circle(x0 + 6.5 * s, y0 + 1.5 * s, 7, C.RED, 1.5)
    pg.line(x0 + 6.5 * s - 6, y0 + 1.5 * s - 6, x0 + 6.5 * s + 6, y0 + 1.5 * s + 6, C.RED, 1.5)
    pg.line(x0 + 6.5 * s - 6, y0 + 1.5 * s + 6, x0 + 6.5 * s + 6, y0 + 1.5 * s - 6, C.RED, 1.5)
    pg.note(L + 230, 210, "\"along 7, up 7: hit!\"\nEvery square has an address.\nA graph is a grid where every\n"
            "input gets a dot at\n(input, output).", C.TEAL, 17)
    f = ch.flow(top=400)
    f.p("A {B:graph} turns a function into a picture. Each input $x$ and its output $f(x)$ become one "
        "dot, and all the dots together draw a line or curve. You can then {B:see} things that "
        "are hard to spot in a formula: where it's biggest, where it crosses zero, whether it "
        "grows fast or slowly.", 14, gap=10)
    f.p("You'll start with the grid itself (Battleship), plot a curve by hand, learn to read a graph "
        "in both directions, and then meet the \"family portraits\" of the common functions from "
        "Lecture 7 so you recognise them on sight.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 7} {y:(graphing common functions, dominance),} {B:Lecture 13} "
        "{y:(graph of a function) and} {B:Lecture 14} {y:(intercepts and vertex).}", 12.5)


def battleship(ch):
    f = flow(ch)
    sec(f, "Coordinates: Battleship with negative numbers")
    rule_box(f, "coordinates", [
        "The point $(x, y)$ is $x$ {B:across} (right if positive, left if negative) and then $y$ {B:up} "
        "(down if negative), starting from the origin $(0, 0)$. Always $x$ first.",
    ], C.TEAL)
    f.p("Two number lines cross at right angles. The across one is the {B:x-axis}, the up one is the "
        "{B:y-axis}, and they meet at the {B:origin} (0, 0). A point's address is written "
        "{B:(x, y)}: {B:across first, then up}.", 14, gap=8)
    y_ = f.reserve(220)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 12, 240, 190, (-4, 4), (-4, 4))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 1)
    pts = [(3, 2, "A", C.BLUE), (-2, 1, "B", C.ORANGE), (-3, -2, "C", C.PURPLE), (2, -3, "D", C.GREEN)]
    for px, py, lab, col in pts:
        ax.dot(px, py, col, 4)
        code_ = {C.BLUE: "B", C.ORANGE: "O", C.PURPLE: "P", C.GREEN: "G"}[col]
        ax.label(px, py, f"{{{code_}:{lab}}}", 12, col, dx=5, dy=-18)
    ax.seg(0, 0, 3, 0, C.BLUE, 2.2)
    ax.seg(3, 0, 3, 2, C.BLUE, 2.2)
    pg.note(L + 300, y_ + 8, "A = (3, 2): along 3, up 2\n(blue path: corridor first,\nthen the stairs)",
            C.BLUE, 15)
    pg.note(L + 300, y_ + 80, "B = (−2, 1): back 2, up 1", C.ORANGE, 15)
    pg.note(L + 300, y_ + 104, "C = (−3, −2): back 3, down 2", C.PURPLE, 15)
    pg.note(L + 300, y_ + 128, "D = (2, −3): along 2, down 3", C.GREEN, 15)
    pg.note(L + 300, y_ + 160, "Memory hook: \"along the\ncorridor, then up the stairs\"", C.BROWN, 15)
    ch.term("coordinates", "the pair (x, y) giving a point's position: x across, then y up")
    ch.term("origin", "the point (0, 0) where the axes cross")
    ch.term("axes", "the two number lines of a graph: the x-axis across and the y-axis up (singular: axis)")
    f.p("The axes split the page into four {B:quadrants}. Negative x means left of the y-axis; "
        "negative y means below the x-axis.", 14)
    ch.term("quadrant", "one of the four regions the axes divide the plane into")


def plotting(ch):
    f = flow(ch)
    sec(f, "From table to dots to curve", room=480)
    rule_box(f, "plotting y = f(x)", [
        "Choose inputs $x$ (include negatives and 0) and work out each $y=f(x)$ in a table.",
        "Plot each pair $(x, y)$ as a dot.",
        "Join the dots with a {B:smooth} curve (a ruler only if the rule is a straight line).",
    ], C.TEAL, numbered=True, tag="PROCEDURE")
    f.p("To draw $y = x^2 - 2$: choose some inputs, work out each output (a table), plot each pair "
        "as a dot, then join the dots with a smooth curve.", 14, gap=8)
    xs = [-3, -2, -1, 0, 1, 2, 3]
    ys = [t * t - 2 for t in xs]
    y_ = f.reserve(60)
    pg = f.pg
    pg.text(L + 6, y_ + 4, "x", 13, C.ORANGE, F.BOLD)
    pg.text(L + 6, y_ + 28, "y = x² − 2", 12, C.GREEN, F.BOLD)
    for i, (a, b) in enumerate(zip(xs, ys)):
        xx = L + 110 + i * 52
        pg.rect(xx - 22, y_, 44, 48, C.TEAL, 0.7)
        pg.text(xx, y_ + 4, str(a).replace("-", "−"), 13, C.ORANGE, align="center")
        pg.text(xx, y_ + 28, str(b).replace("-", "−"), 13, C.GREEN, align="center")
        ch.check(a * a - 2, b)
    f.p("{R:Careful with negatives:} for $x = -3$, it's $(-3)^2 - 2 = 9 - 2 = 7$, not $-9 - 2$.", 13.5, gap=10)
    y_ = f.reserve(190)
    pg = f.pg
    for k in range(2):
        ax = Axes(pg, L + 30 + k * 250, y_ + 10, 200, 150, (-3.5, 3.5), (-3, 8))
        ax.grid(1, 1)
        ax.axes("x", "y", 1, 2, size=8)
        for a, b in zip(xs, ys):
            ax.dot(a, b, C.TEAL, 3.5)
        if k:
            ax.curve(lambda t: t * t - 2, color=C.TEAL, width=2)
            ax.dot(1.5, 0.25, C.RED, 3)
            ax.label(1.5, 0.25, "{r:(1.5, 0.25)}", 10, C.RED, dx=8, dy=-4)
        pg.text(L + 130 + k * 250, y_ + 170, ["1. plot the dots", "2. join with a smooth curve"][k], 12, C.TEAL,
                F.BOLD, align="center")
    ch.check(sp.Rational(3, 2) ** 2 - 2, sp.Rational(1, 4))
    f.p("Why smooth, not straight lines between dots? Because in-between inputs have outputs too: "
        "$x = 1.5$ gives $0.25$, which lands right on the curve (red dot). Lecture 13 puts it neatly: "
        "the graph of $f$ is {B:the set of all points $(x, f(x))$}.", 14)
    ch.term("graph of a function", "all the points (x, f(x)) drawn on axes")


def reading(ch):
    f = flow(ch)
    sec(f, "Reading a graph both ways", room=420)
    rule_box(f, "intercepts and reading a graph", [
        "{B:$y$-intercept:} put $x=0$; the graph crosses the $y$-axis at $(0, f(0))$.",
        "{B:$x$-intercepts} (roots): put $y=0$ and solve $f(x)=0$.",
        "To solve $f(x)=k$ from a graph: go across from $k$ on the $y$-axis to the curve, then down to read $x$.",
    ], C.TEAL)
    y_ = f.reserve(224)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 14, 240, 170, (-3.5, 3.5), (-3, 8))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 1, size=8)
    ax.curve(lambda t: t * t - 2, color=C.TEAL, width=2)
    ax.seg(2.5, 0, 2.5, 4.25, C.ORANGE, 1.4, dash=(3, 2))
    ax.arrow(2.5, 4.25, 0, 4.25, C.ORANGE, 1.4, head=5)
    ax.hline(2, C.PURPLE, 1.3, dash=(3, 2))
    ax.arrow(-2, 2, -2, 0, C.PURPLE, 1.3, head=5)
    ax.arrow(2, 2, 2, 0, C.PURPLE, 1.3, head=5)
    ax.dot(0, -2, C.RED, 4)
    ax.dot(math.sqrt(2), 0, C.GREEN, 4)
    ax.dot(-math.sqrt(2), 0, C.GREEN, 4)
    pg.note(L + 300, y_ + 4, "Input → output: from x = 2.5\ngo UP to the curve, then ACROSS:\ny ≈ 4.25",
            C.ORANGE, 15)
    pg.note(L + 300, y_ + 66, "Output → input: which x give y = 2?\ngo ACROSS from 2, then DOWN:\nx = −2 and x = 2",
            C.PURPLE, 15)
    pg.note(L + 300, y_ + 128, "y-intercept (red): where it crosses\nthe y-axis. Put x = 0: y = −2", C.RED, 15)
    pg.note(L + 300, y_ + 170, "x-intercepts (green): where y = 0,\nthe solutions of x² − 2 = 0: x = ±1.41",
            C.GREEN, 15)
    ch.check(sp.solve(x ** 2 - 2 - 2, x), [-2, 2])
    ch.check(sp.solve(x ** 2 - 2, x), [-sp.sqrt(2), sp.sqrt(2)])
    ch.term("intercept", "where a graph crosses an axis: the y-intercept at x = 0, x-intercepts where y = 0")
    f.p("That second direction is {B:solving an equation by picture}: the answers to $x^2 - 2 = 2$ "
        "are where the curve meets the horizontal line $y = 2$. (Chapter 15's crossing lines were "
        "the same idea.)", 14)


def even_odd(ch):
    f = flow(ch)
    sec(f, "Even functions fold, odd functions spin", room=330)
    rule_box(f, "even and odd functions", [
        "{B:Even:} $f(-x)=f(x)$ for every $x$. The graph is symmetric in the $y$-axis (e.g. $x^2$, $x^4$, $x^2+3$).",
        "{B:Odd:} $f(-x)=-f(x)$ for every $x$. The graph is unchanged by a half turn about the origin "
        "(e.g. $x$, $x^3$, $\\frac1x$).",
        "To test: work out $f(-x)$ and simplify. Same as $f(x)$: even. Exactly $-f(x)$: odd. Otherwise: neither.",
    ], C.TEAL)
    f.p("Lecture 7 sorts the power graphs into {B:even} and {B:odd}. You can test by picture or by "
        "numbers:", 14, gap=10)
    y_ = f.reserve(190)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 10, 200, 140, (-2.5, 2.5), (-4, 4))
    ax.grid(1, 1)
    ax.axes("x", "y", 0, 0)
    ax.curve(lambda t: t * t, color=C.BLUE, width=2)
    ax.dot(-1.5, 2.25, C.ORANGE, 3.5)
    ax.dot(1.5, 2.25, C.ORANGE, 3.5)
    pg.arc(ax.X(0), ax.Y(3.3), 14, 200, 340, C.ORANGE, 1.1, arrow=True)
    pg.text(L + 120, y_ + 160, "x²: fold along the y-axis", 12, C.BLUE, F.BOLD, align="center")
    ax2 = Axes(pg, L + 270, y_ + 10, 200, 140, (-2.5, 2.5), (-4, 4))
    ax2.grid(1, 1)
    ax2.axes("x", "y", 0, 0)
    ax2.curve(lambda t: t ** 3, color=C.PURPLE, width=2)
    ax2.dot(1.4, 1.4 ** 3, C.ORANGE, 3.5)
    ax2.dot(-1.4, -1.4 ** 3, C.ORANGE, 3.5)
    pg.arc(ax2.X(0), ax2.Y(0), 22, 20, 200, C.ORANGE, 1.1, arrow=True)
    pg.text(L + 370, y_ + 160, "x³: spin half a turn about (0, 0)", 12, C.PURPLE, F.BOLD, align="center")
    f.p("{b:Even:} fold the page along the y-axis and the two halves match. In numbers, putting in "
        "$-x$ gives the {B:same} output: $(-1.5)^2 = 1.5^2 = 2.25$. So $f(-x) = f(x)$.", 14, gap=6)
    f.p("{b:Odd:} spin the page half a turn around the origin and the curve lands on itself. In numbers, "
        "$-x$ gives the {B:negative} output: $(-2)^3 = -8$. So $f(-x) = -f(x)$.", 14, gap=6)
    ch.check((-2) ** 3, -(2 ** 3))
    ch.term("even function", "f(−x) = f(x): the graph is a mirror image across the y-axis (e.g. x², x⁴)")
    ch.term("odd function", "f(−x) = −f(x): the graph looks the same after a half turn about the origin (e.g. x, x³)")
    f.p("{h:The names come from the powers:} $x^2, x^4, x^6$ are even functions; $x, x^3, x^5$ are odd. "
        "Many functions (like $x^2 + x$) are neither.", 13.5, C.BROWN)


def families(ch):
    f = flow(ch)
    sec(f, "Family portraits: recognise them on sight", room=560)
    f.p("These are the shapes from Lecture 7. Learn them like faces; you'll meet them everywhere.",
        14, gap=10)
    fams = [
        ("even powers", [(lambda t: t ** 2, C.BLUE, "x²"), (lambda t: t ** 4, C.GREEN, "x⁴"),
                         (lambda t: t ** 6, C.ORANGE, "x⁶")], (-1.8, 1.8), (-0.5, 3.5),
         "all pass through (−1, 1), (0, 0), (1, 1).\nNever negative. Higher power: flatter\nnear 0, steeper beyond 1."),
        ("odd powers", [(lambda t: t, C.BLUE, "x"), (lambda t: t ** 3, C.GREEN, "x³"),
                        (lambda t: t ** 5, C.ORANGE, "x⁵")], (-1.8, 1.8), (-3, 3),
         "negative on the left, positive on the\nright; all pass through (−1, −1),\n(0, 0) and (1, 1)."),
        ("negative powers", [(safe(lambda t: 1 / t), C.BLUE, "1/x"), (safe(lambda t: 1 / t ** 2), C.ORANGE, "1/x²")],
         (-3, 3), (-4, 4),
         "blow up near x = 0 (can't divide by 0),\nand creep towards 0 far out, never\nquite touching the axes."),
        ("fractional powers", [(safe(lambda t: math.sqrt(t)), C.BLUE, "√x"),
                               (lambda t: math.copysign(abs(t) ** (1 / 3), t), C.ORANGE, "∛x")], (-3, 3), (-2, 2),
         "√x only exists for x ≥ 0 (half a\ncurve); ∛x works for negatives too.\nBoth grow slower and slower."),
    ]
    for k, (title, fns, xr, yr, desc) in enumerate(fams):
        y_ = f.reserve(116)
        pg = f.pg
        panel(pg, L + 20, y_ + 4, 150, 96, xr, yr, fns)
        pg.text(L + 190, y_ + 2, title, 13.5, C.TEAL, F.BOLD)
        xx = L + 190
        for fn, col, lab in fns:
            pg.text(xx, y_ + 22, lab, 12.5, col, F.BOLD)
            xx += pg.twidth(lab, 12.5, F.BOLD) + 14
        pg.note(L + 190, y_ + 42, desc, C.GREY, 14)
    ch.term("asymptote", "a line a graph gets closer and closer to but never reaches, e.g. the axes for y = 1/x")
    f.p("Those lines that $\\frac1x$ creeps towards but never reaches are called {B:asymptotes}.", 13.5)


def dominance(ch):
    f = flow(ch)
    sec(f, "Dominance: what you see depends on the zoom", room=330)
    rule_box(f, "dominance (Lecture 7)", [
        "For $y=ax^m+\\dots+bx^n+c$ (highest power $m$, lowest power $n$):",
        "{B:Large $x$} (far from 0, either way): the {B:highest power} term dominates, so it looks like $y=ax^m$.",
        "{B:Small $x$} (close to 0): the {B:lowest powers and the constant} dominate, so it looks like "
        "$y=bx^n+c$.",
    ], C.TEAL)
    f.p("Lecture 7's example $y = x^3 - 2x$. Zoom out and the $x^3$ term swamps everything (the "
        "{B:biggest power dominates} for large $x$). Zoom in near 0 and $x^3$ is tiny, so it looks "
        "like the line $y = -2x$:", 14, gap=10)
    y_ = f.reserve(170)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 6, 200, 130, (-10, 10), (-800, 800))
    ax.axes(None, None, 0, 0)
    ax.curve(lambda t: t ** 3 - 2 * t, color=C.TEAL, width=2)
    ax.curve(lambda t: t ** 3, color=C.ORANGE, width=1.2, dash=(4, 3))
    pg.text(L + 120, y_ + 146, "zoomed out: looks like x³ (dashed)", 11.5, C.TEAL, F.BOLD, align="center")
    ax2 = Axes(pg, L + 270, y_ + 6, 200, 130, (-0.4, 0.4), (-0.8, 0.8))
    ax2.axes(None, None, 0, 0)
    ax2.curve(lambda t: t ** 3 - 2 * t, color=C.TEAL, width=2)
    ax2.curve(lambda t: -2 * t, color=C.ORANGE, width=1.2, dash=(4, 3))
    pg.text(L + 370, y_ + 146, "zoomed in: looks like −2x (dashed)", 11.5, C.TEAL, F.BOLD, align="center")
    ch.check_num((10 ** 3 - 20) / 10 ** 3, 0.98, tol=0.001)
    f.p("At $x = 10$: $x^3 = 1000$ and $2x = 20$, so the $-2x$ changes the answer by only 2%. At "
        "$x = 0.1$: $x^3 = 0.001$ and $2x = 0.2$, so now $x^3$ hardly matters.", 13.5)
    ch.term("dominant term", "the term that decides a graph's shape in some range: the highest power for large x")
    f.p("{B:Example:} $y = x^4 - 3x + 2$. For large $x$ it looks like $y = x^4$ (a U shape). Near 0 the "
        "$x^4$ is tiny and it looks like the straight line $y = -3x + 2$: at $x = 0.1$, "
        "$x^4 = 0.0001$ while $-3x + 2 = 1.7$.", 13.5, gap=6)
    ch.check_num(0.1 ** 4 - 0.3 + 2, 1.7001, tol=1e-9)


def moving(ch):
    f = flow(ch)
    sec(f, "Sliding and flipping graphs", room=440)
    rule_box(f, "transformations of y = f(x)", [
        "A change {B:outside} the function (to the output, $y$) moves the graph {B:vertically} and does "
        "exactly what it says.",
        "A change {B:inside} the brackets (to the input, $x$) moves the graph {B:horizontally} and does the "
        "{R:opposite} of what it looks like: $+a$ moves left, $\\times a$ squashes.",
    ], C.TEAL)
    rules_table(f, ["new graph", "what happens to y = f(x)", "point (x, y) moves to"], [
        ["$y=f(x)+a$", "{B:up} $a$ (down if $a<0$)", "$(x,\\ y+a)$"],
        ["$y=f(x+a)$", "{R:left} $a$ (opposite to the sign!)", "$(x-a,\\ y)$"],
        ["$y=f(x-a)$", "{R:right} $a$", "$(x+a,\\ y)$"],
        ["$y=af(x)$", "vertical stretch, factor $a$ (from the $x$-axis)", "$(x,\\ ay)$"],
        ["$y=f(ax)$", "horizontal squash by factor $a$ (a stretch of factor $\\frac1a$, towards the $y$-axis)",
         "$(\\frac xa,\\ y)$"],
        ["$y=-f(x)$", "reflect in the {B:$x$-axis} (upside down)", "$(x,\\ -y)$"],
        ["$y=f(-x)$", "reflect in the {B:$y$-axis} (left-right)", "$(-x,\\ y)$"],
    ], [120, 245, 130], C.TEAL, size=12)
    f.p("Change the formula a little and the whole picture moves. Starting from $y = x^2$:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    cases = [(r"y=x^2+3", lambda t: t * t + 3, "up 3: add 3 to\nevery output"),
             (r"y=(x-2)^2", lambda t: (t - 2) ** 2, "RIGHT 2 (not left!):\nx must be 2 bigger to\nget the same output"),
             (r"y=-x^2", lambda t: -t * t, "flipped upside down:\nevery output\nchanges sign")]
    for k, (lat, fn, desc) in enumerate(cases):
        x0 = L + 10 + k * 165
        ax = Axes(pg, x0, y_ + 4, 130, 90, (-3, 5), (-5, 7))
        ax.grid(1, 1, color="#e6eaee")
        ax.axes(None, None, 0, 0)
        ax.curve(lambda t: t * t, color=C.GREY, width=1.1, dash=(3, 2))
        ax.curve(fn, color=C.TEAL, width=2)
        pg.eq(x0 + 65, y_ + 100, lat, 14, C.TEAL, align="center")
        pg.note(x0, y_ + 118, desc, C.GREY, 13, solid=False)
    f.gap(24)
    f.p("{b:The one that feels backwards:} $(x - 2)^2$ moves {B:right}. Check with numbers: the lowest "
        "point of $x^2$ is at $x = 0$; for $(x - 2)^2$ the bracket is 0 when $x = 2$. So the bottom "
        "has moved to $x = 2$, to the right.", 14, gap=8)
    ch.term("transformation", "a change to a formula that moves, stretches or flips its graph")
    f.p("{b:Chapter 15, explained:} $y = x^2 + 6x + 5 = (x + 3)^2 - 4$. That's $x^2$ moved {B:left 3} "
        "and {B:down 4}, so its lowest point (vertex) is at $(-3, -4)$, just as Lecture 14 said. The "
        "completed-square form is the {B:sat-nav} to the vertex.", 14, gap=10)
    ch.check(sp.expand((x + 3) ** 2 - 4), x ** 2 + 6 * x + 5)
    rule_box(f, "vertex form of a quadratic", [
        "$y=a(x-h)^2+k$ has its {B:vertex} (turning point) at $(h, k)$ and is symmetric about the line $x=h$.",
        "$a>0$: U-shaped, the vertex is the {B:lowest} point. $a<0$: upside down, the vertex is the {B:highest} point.",
        "{R:Watch the sign of $h$}: $(x+3)^2$ is $(x-(-3))^2$, so $h=-3$.",
    ], C.TEAL)
    ch.term("vertex", "the turning point of a parabola: (h, k) for y = a(x − h)² + k")
    rule_box(f, "moving a point", [
        "Find the {B:horizontal} change from inside the bracket (opposite sign) and apply it to $x$.",
        "Find the {B:vertical} change from outside and apply it to $y$ (stretch first, then shift).",
        "Check: put the new $x$ into the new formula; it should give the new $y$.",
    ], C.TEAL, numbered=True, tag="PROCEDURE")
    fp = lambda t: t ** 2 + 1
    f.p("{B:Example:} $(2, 5)$ lies on $y = f(x)$. Where does it go on $y = f(x - 3) + 1$?", 13.5, gap=4)
    step(f, r"x:\ 2\to2+3=5", "inside: −3 means RIGHT 3", size=19)
    step(f, r"y:\ 5\to5+1=6", "outside: +1 means up 1", size=19)
    step(f, r"(2,5)\ \to\ (5,6)", "", size=20, color=C.GREEN)
    g1 = lambda t: fp(t - 3) + 1
    ch.check([fp(2), g1(5)], [5, 6])
    f.p("{G:Check} with $f(x) = x^2 + 1$ (which does pass through (2, 5)): new formula at $x = 5$ is "
        "$f(2) + 1 = 6$ ✓.", 13.5, gap=8)
    f.p("{B:Example:} $(4, 6)$ lies on $y = f(x)$. Where does it go on $y = f(2x)$, on $y = 3f(x)$ and on "
        "$y = -f(x)$?", 13.5, gap=4)
    step(f, r"f(2x):\ (4,6)\to(2,6)", "inside ×2 squashes: x ÷ 2", size=19)
    step(f, r"3f(x):\ (4,6)\to(4,18)", "outside ×3 stretches: y × 3", size=19)
    step(f, r"-f(x):\ (4,6)\to(4,-6)", "flip in the x-axis", size=19, color=C.GREEN)
    fq = lambda t: t + 2
    ch.check([fq(4), fq(2 * 2), 3 * fq(4), -fq(4)], [6, 6, 18, -6])


def asymptotes(ch):
    f = flow(ch)
    sec(f, "Asymptotes: where a graph can't go", room=420)
    rule_box(f, "asymptotes of fractions", [
        "A {B:vertical asymptote} is where the denominator is 0: $y=\\dfrac{1}{x-a}$ has the asymptote $x=a$. "
        "The graph shoots up or down beside it and never touches it.",
        "A {B:horizontal asymptote} is the value $y$ approaches as $x$ gets very large: for $\\dfrac{1}{x-a}$ "
        "it is $y=0$, because 1 divided by a huge number is nearly 0.",
        "$y=\\dfrac{b}{x-h}+k$ is $\\frac1x$ moved: asymptotes $x=h$ and $y=k$.",
    ], C.TEAL)
    y_ = f.reserve(172)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 6, 210, 140, (-2, 6), (-5, 5))
    ax.grid(1, 1, color="#e6eaee")
    ax.axes("x", "y", 1, 1, size=8)
    ax.curve(safe(lambda t: 1 / (t - 2) if abs(t - 2) > 0.18 else None), color=C.TEAL, width=2)
    ax.seg(2, -5, 2, 5, C.RED, 1.2, dash=(4, 3))
    pg.note(L + 260, y_ + 8, "y = 1/(x − 2)\n\nred dashed: x = 2. Put x = 2 in and\nyou'd divide by 0, so the "
            "graph\ncan't be there.\n\nFar left and far right it creeps\ntowards the x-axis (y = 0).", C.INK, 15)
    ch.check(sp.solve(x - 2, x), [2])
    f.p("{B:Example:} $y = \\dfrac{3}{x+1} + 2$. Denominator 0 when $x = -1$: vertical asymptote $x = -1$. "
        "For large $x$ the fraction is nearly 0, so $y$ is nearly 2: horizontal asymptote $y = 2$.", 13.5)
    ch.check(sp.limit(3 / (x + 1) + 2, x, sp.oo), 2)
    ch.check(sp.solve(x + 1, x), [-1])


def ex(f, s):
    f.need(100)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown: reading a formula from facts", room=480)
    rule_box(f, "partial-information graph problems", [
        "A point $(p, q)$ on a graph means: put $x=p$ into the formula and you get $y=q$. That's an equation "
        "for the unknown.",
        "A vertex $(h, k)$ means: write $y=a(x-h)^2+k$ and fill in $h$ and $k$.",
        "An asymptote $x=a$ means: the denominator is 0 when $x=a$.",
        "A moved graph: use the transformation table, on the point or on the formula.",
    ], C.TEAL, numbered=True, tag="PROCEDURE")
    h, k, a_, b_ = sp.symbols("h k a b")
    ex(f, "$y = (x - h)^2 + k$ has vertex $(3, -2)$. Find $h$ and $k$, and write the formula.")
    step(f, r"h=3,\ k=-2:\quad y=(x-3)^2-2", "vertex (h, k) read straight off", size=19, color=C.GREEN)
    ch.check(sp.expand((x - 3) ** 2 - 2).subs(x, 3), -2)
    ex(f, "$y = a(x - 1)^2 + 2$ passes through $(3, 10)$. Find $a$.")
    step(f, r"10=a(3-1)^2+2=4a+2\ \Rightarrow\ a=2", "put x = 3, y = 10", size=19, color=C.GREEN)
    ch.check(sp.solve(a_ * (3 - 1) ** 2 + 2 - 10, a_), [2])
    ex(f, "the graph of $y = f(x)$ is moved to $y = f(x + 4)$. Where does the point $(6, 1)$ go?")
    step(f, r"(6,1)\ \to\ (6-4,\ 1)=(2,1)", "inside +4: LEFT 4", size=19, color=C.GREEN)
    ch.check((lambda t: t - 5)(6), (lambda t: (t + 4) - 5)(2))
    ex(f, "$y = x^2 + bx + 3$ is an even function. Find $b$.")
    step(f, r"f(-x)=x^2-bx+3=x^2+bx+3\ \Rightarrow\ -b=b\ \Rightarrow\ b=0", "even: f(−x) = f(x)",
         size=17, color=C.GREEN)
    ch.check(sp.solve(((-x) ** 2 + b_ * (-x) + 3) - (x ** 2 + b_ * x + 3), b_), [0])
    ex(f, "$y = \\dfrac{5}{x - k}$ has a vertical asymptote at $x = 4$. Find $k$.")
    step(f, r"4-k=0\ \Rightarrow\ k=4", "denominator 0 at the asymptote", size=19, color=C.GREEN)
    ch.check(sp.solve(4 - k, k), [4])


def common_mistakes(ch):
    f = flow(ch)
    sec(f, "Mistakes to avoid", room=360)
    mistakes(f, [
        (r"y=(x+2)^2:\ \text{right }2", r"y=(x+2)^2:\ \text{left }2", "inside the bracket: opposite way"),
        (r"y=f(2x):\ (4,6)\to(8,6)", r"(4,6)\to(2,6)", "inside ×2 squashes: divide x by 2"),
        (r"y=(x+3)^2-4:\ \text{vertex }(3,-4)", r"\text{vertex }(-3,-4)", "h is the number that makes the bracket 0"),
        (r"(-3)^2-2=-9-2", r"(-3)^2-2=9-2=7", "square the whole negative number"),
        (r"\text{point }(2,5):\ y=2,\ x=5", r"x=2,\ y=5", "x first, then y"),
    ])


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Coordinates", r"(x,\ y)", "across first, then up"),
        ("Intercepts", None, "$y$-intercept: put $x=0$. $x$-intercepts: solve $f(x)=0$"),
        ("Even function", r"f(-x)=f(x)", "symmetric in the $y$-axis"),
        ("Odd function", r"f(-x)=-f(x)", "half-turn symmetry about the origin"),
        ("Dominance", None, "large $x$: highest power wins. Near 0: lowest powers and the constant win"),
        ("Asymptotes", r"y=\frac{b}{x-h}+k:\quad x=h,\ y=k", "vertical asymptote where the denominator is 0"),
        ("Vertex form", r"y=a(x-h)^2+k\ \Rightarrow\ \text{vertex }(h,k)", "$a>0$ minimum, $a<0$ maximum"),
        ("Shift up / down", r"y=f(x)+a", "up $a$: $(x, y)\\to(x, y+a)$"),
        ("Shift left / right", r"y=f(x+a)", "{R:left} $a$: $(x, y)\\to(x-a, y)$"),
        ("Vertical stretch", r"y=af(x)", "$(x, y)\\to(x, ay)$"),
        ("Horizontal squash", r"y=f(ax)", "$(x, y)\\to(\\frac xa, y)$"),
        ("Reflections", r"y=-f(x),\quad y=f(-x)", "in the $x$-axis; in the $y$-axis"),
    ], C.TEAL)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Battleship: your turn", fresh=True)
    f.p("Answers in grey. Sketch every graph on squared paper.", 13.5, gap=10)
    groups = [
        ("Points and plotting", ["Which quadrant is (−4, 2) in? (top-right is the 1st, go anticlockwise)",
                                 "Make a table for y = 2x − 1 with x = −2 to 2, and plot it.",
                                 "For y = x² − 4x, find the y-intercept and the x-intercepts."],
         "1. 2nd (top-left)   2. y = −5, −3, −1, 1, 3 (a straight line)   3. y-int 0; x = 0 and x = 4"),
        ("Even, odd, neither", ["y = x⁴ + 1", "y = x³ − x", "y = x² + x", "y = 1/x"],
         "4. even   5. odd   6. neither (try x = 1 and x = −1: 2 and 0)   7. odd"),
        ("Recognise and move", ["Which family: y = x⁻²?", "Where is the vertex of y = (x − 1)² + 5?",
                                "Describe y = (x + 4)² compared with y = x².", "Which term dominates y = 5x² + x⁴ for large x?"],
         "8. negative powers (even: always positive)   9. (1, 5)   10. moved left 4   11. x⁴"),
        ("Find the unknown", ["y = (x − h)² + k has vertex (3, −2). Find h and k.",
                              "(6, 1) is on y = f(x). Where does it move to on y = f(x + 4)?",
                              "(2, 5) is on y = f(x). Where does it move to on y = f(x + 1) − 4?",
                              "(4, −3) is on y = f(x). Where does it move to on y = −2f(x)?",
                              "y = a(x + 2)² − 1 passes through (0, 7). Find a.",
                              "y = 3/(x − k) has a vertical asymptote at x = −2. Find k."],
         "12. h = 3, k = −2   13. (2, 1): inside +4 moves left 4   14. (1, 1): left 1, down 4   "
         "15. (4, 6): y × (−2)   16. a = 2 (7 = 4a − 1)   17. k = −2 (denominator −2 − k = 0)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.TEAL, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check([2 * t - 1 for t in range(-2, 3)], [-5, -3, -1, 1, 3])
    ch.check(sp.solve(x ** 2 - 4 * x, x), [0, 4])
    ch.check(sp.expand((-x) ** 3 - (-x) + (x ** 3 - x)), 0)
    a_, k_ = sp.symbols("a k")
    g0 = lambda t: t - 5
    ch.check(g0(6), g0(2 + 4))
    g2 = lambda t: t + 3
    ch.check([g2(2), g2(1 + 1) - 4], [5, 1])
    g3 = lambda t: t - 7
    ch.check([g3(4), -2 * g3(4)], [-3, 6])
    ch.check(sp.solve(a_ * (0 + 2) ** 2 - 1 - 7, a_), [2])
    ch.check(sp.solve(-2 - k_, k_), [-2])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    battleship(ch)
    plotting(ch)
    reading(ch)
    even_odd(ch)
    families(ch)
    dominance(ch)
    moving(ch)
    asymptotes(ch)
    find_unknown(ch)
    common_mistakes(ch)
    summary(ch)
    your_turn(ch)
