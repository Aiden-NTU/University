"""Chapter 28 - Introduction to trigonometry (Lecture 6). A ladder against a wall; naming the sides from
the angle's point of view (an eye at the corner); Pythagoras with real squares of unit tiles, in 3D and
as the circle equation; zoomed photos of one triangle to show why the ratios exist; SOHCAHTOA with
cover-up triangles; the lecture's three examples in tiny steps; inverse trig as the undo button; and
the two special triangles that give exact values."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 28
NUM = 28
TITLE = "Introduction to trigonometry"
SHORT = "Trigonometry"
SLUG = "Trig-intro"
ACCENT = C.TEAL
REQUIRES = ["angle", "degrees", "right-angle", "roots", "powers", "transpose", "inverse-operations", "fraction",
            "rounding", "area", "ratio", "coordinates", "square-and-root-words", "radian", "subject-of-formula"]
INTRODUCES = ["hypotenuse", "opposite-adjacent", "pythagoras", "pythagoras-3d", "circle-equation",
              "similar-triangles", "sine", "cosine", "tangent", "sohcahtoa", "inverse-trig", "exact-trig-values"]

PAPER = "#f8fcfc"


def icon(pg, x0, y0):
    pg.poly([(x0 + 1, y0 + 17), (x0 + 17, y0 + 17), (x0 + 17, y0 + 2)], C.TEAL, 1.6, closed=True)
    pg.rect(x0 + 13, y0 + 13, 4, 4, C.TEAL, 0.8)


def sec(f, t_, **kw):
    section(f, t_, C.TEAL, icon, **kw)


SIDE_COL = {"H": C.PURPLE, "O": C.ORANGE, "A": C.BLUE}


def badge(pg, x, y, letter, r=7.5):
    """A side's name tag: H (hypotenuse), O (opposite), A (adjacent), always in the same colour."""
    col = SIDE_COL[letter]
    pg.circle(x, y, r, col, 1.1, fillcolor=C.LIGHT[col])
    pg.text(x - r, y - r * 0.82, letter, r * 1.3, col, F.BOLD, w=2 * r, align="center", solid=False)


def tri(pg, x, y, a, o, labels=None, col=C.INK, theta_at="left", size=12, fill=None, tags="left"):
    """Right triangle with the right angle at bottom-right: (x,y) bottom-left, width a, height o.
    tags: which corner the angle θ is at ("left" or "top"), so every triangle wears H/O/A badges; None for none."""
    A_, B_, C_ = (x, y), (x + a, y), (x + a, y - o)
    if fill:
        pg.fillpoly([A_, B_, C_], fill)
    pg.poly([A_, B_, C_], col, 1.6, closed=True)
    pg.rect(x + a - 9, y - 9, 9, 9, col, 0.9)
    ang = math.degrees(math.atan2(o, a))
    if theta_at == "left":
        pg.arc(x, y, 22, 0, ang, C.RED, 1.4)
        pg.text(x + 26, y - 17, "θ", size, C.RED, F.BOLD)
    vert, base = ("O", "A") if tags == "left" else ("A", "O")
    if labels:
        h_, o_, a_ = labels
        hw = F.width(h_, F.BOLD, size)
        pg.text(x + a / 2 - 14, y - o / 2 - 22, h_, size, C.PURPLE, F.BOLD, align="right", solid=False)
        pg.text(x + a + 24, y - o / 2 - 7, o_, size, SIDE_COL[vert], F.BOLD, solid=False)
        pg.text(x + a / 2 + 10, y + 4, a_, size, SIDE_COL[base], F.BOLD, align="center", solid=False)
        if tags:
            badge(pg, x + a / 2 - 26 - hw, y - o / 2 - 14, "H")
            badge(pg, x + a + 13, y - o / 2, vert)
            badge(pg, x + a / 2 - F.width(a_, F.BOLD, size) / 2, y + 12, base)
    elif tags:
        n = math.hypot(a, o)
        nx, ny = o / n, a / n
        badge(pg, x + a / 2 + nx * 13, y - o / 2 + ny * 13, "H")
        badge(pg, x + a - 12, y - o * 0.42, vert)
        badge(pg, x + a * 0.62, y - 11, base)
    return A_, B_, C_


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 28, "Introduction to trigonometry", "triangles that measure what you can't reach",
                     C.TEAL, PAPER)
    gx, gy = L + 40, 330
    pg.rect(gx + 150, gy - 150, 18, 150, C.BROWN, 1, fillcolor=C.LIGHT[C.BROWN])
    pg.line(gx - 20, gy, gx + 200, gy, C.GREEN, 2)
    pg.line(gx + 40, gy, gx + 150, gy - 130, C.ORANGE, 4)
    for k in range(1, 8):
        t_ = k / 8
        x1, y1 = gx + 40 + 110 * t_, gy - 130 * t_
        pg.line(x1 - 5, y1 - 3, x1 + 5, y1 + 3, C.ORANGE, 1.4)
    pg.arc(gx + 40, gy, 24, 0, 50, C.RED, 1.5)
    pg.text(gx + 68, gy - 20, "70°", 11, C.RED, F.BOLD)
    pg.text(gx + 176, gy - 80, "?", 22, C.PURPLE, F.BOLD)
    pg.note(gx + 200, gy - 150, "A 5 m ladder leans at 70°.\nHow high up the wall\ndoes it reach?\n\n"
            "No tape measure needed:\ntrigonometry answers it\nfrom the angle alone.", C.TEAL, 16)
    f = ch.flow(top=370)
    f.p("{B:Trigonometry} means \"triangle measuring\". Surveyors use it to find the height of mountains, "
        "sat-navs to find where you are, engineers to find forces. It all rests on one fact about "
        "right-angled triangles: {B:the angle decides the shape}.", 14, gap=10)
    f.p("We'll name the sides properly, meet Pythagoras (with real squares), see {B:why} sin, cos and tan "
        "exist, and work Lecture 6's examples one tiny step at a time.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 6} {y:(right-angled triangles, Pythagoras in 2D and 3D, the circle, "
        "SOHCAHTOA, inverse functions, Examples 1-3).}", 12.5)


def names(ch):
    f = flow(ch)
    sec(f, "Naming the sides: stand at the angle and look")
    f.p("A right-angled triangle has one 90° corner (the little square). Its three sides get names, "
        "and two of the names depend on {B:which angle you're standing at}, called $\\theta$ (\"theta\", "
        "a Greek letter used for angles).", 14, gap=14)
    y_ = f.reserve(170)
    pg = f.pg
    tri(pg, L + 20, y_ + 140, 190, 120, ("hypotenuse", "opposite", "adjacent"), fill=C.LIGHT[C.TEAL])
    pg.circle(L + 12, y_ + 148, 6, C.RED, 1.2)
    pg.dot(L + 14, y_ + 147, 2, C.RED)
    pg.arrow(L + 30, y_ + 132, L + 200, y_ + 80, C.RED, 1, head=5, bend=0.1)
    pg.note(L + 60, y_ + 160, "the eye at θ looks across to the opposite side", C.RED, 13)
    pg.note(L + 320, y_ + 10, "HYPOTENUSE: the longest side,\nopposite the right angle. It never\nchanges name.",
            C.PURPLE, 14)
    pg.note(L + 320, y_ + 70, "OPPOSITE: across from θ,\nthe side θ is \"looking at\".", C.ORANGE, 14)
    pg.note(L + 320, y_ + 115, "ADJACENT: next to θ (\"adjacent\"\nmeans next to), but not the\nhypotenuse.",
            C.BLUE, 14)
    ch.term("hypotenuse", "the longest side of a right-angled triangle, opposite the right angle")
    ch.term("opposite / adjacent", "the side across from the angle θ / the side next to θ that isn't the hypotenuse")
    ch.symbol(r"\theta", "theta", "a common letter for an unknown angle")
    f.gap(10)
    f.p("{b:Stand at the other corner} and opposite and adjacent {B:swap}; the hypotenuse stays put:",
        14, gap=14)
    y_ = f.reserve(140)
    pg = f.pg
    A_, B_, C_ = tri(pg, L + 20, y_ + 120, 190, 110, None, theta_at="none", fill=C.LIGHT[C.TEAL], tags="top")
    pg.arc(C_[0], C_[1], 22, 210, 270, C.RED, 1.4)
    pg.text(C_[0] - 18, C_[1] + 24, "θ", 12, C.RED, F.BOLD)
    pg.text(L + 100, y_ + 124, "opposite (now!)", 12, C.ORANGE, F.BOLD, align="center")
    pg.text(L + 216, y_ + 60, "adjacent", 12, C.BLUE, F.BOLD)
    pg.text(L + 70, y_ + 40, "hypotenuse", 12, C.PURPLE, F.BOLD)
    pg.note(L + 300, y_ + 20, "Always label from θ's point of\nview, one side at a time:\n1. hypotenuse "
            "(easy, longest)\n2. opposite (across from θ)\n3. adjacent (the one left over)", C.INK, 14)
    f.p("Lecture 6 writes them $h$, $o$ and $a$.", 13.5, C.GREY, gap=10)
    f.p("{b:The labelling habit.} From here on, every triangle in this book's trig chapters wears three "
        "badges: {P:H} (hypotenuse, purple), {O:O} (opposite, orange) and {B:A} (adjacent, blue), always in the "
        "same colours. Do the same on paper: {B:mark θ, then badge all three sides, before anything else}, even "
        "when a question only needs two of them. After a week it becomes automatic, and choosing SOH, CAH or "
        "TOA becomes a matter of reading your own badges.", 14)


def pythag(ch):
    f = flow(ch)
    sec(f, "Pythagoras: squares on the sides", room=560)
    f.p("Build a real square on each side of a 3-4-5 triangle out of 1 × 1 tiles and count them:",
        14, gap=12)
    y_ = f.reserve(250)
    pg = f.pg
    u = 20
    ox, oy = L + 120, y_ + 150
    A_, B_, C_ = (ox, oy), (ox + 4 * u, oy), (ox + 4 * u, oy - 3 * u)
    pg.fillpoly([A_, B_, C_], C.LIGHT[C.TEAL])
    pg.poly([A_, B_, C_], C.INK, 1.6, closed=True)
    for i in range(4):
        for j in range(4):
            pg.rect(ox + i * u, oy + j * u, u, u, C.BLUE, 0.6, fillcolor=C.LIGHT[C.BLUE])
    for i in range(3):
        for j in range(3):
            pg.rect(ox + 4 * u + i * u, oy - 3 * u + j * u, u, u, C.ORANGE, 0.6, fillcolor=C.LIGHT[C.ORANGE])
    dx, dy = 4 * u, -3 * u
    nx, ny = dy, -dx
    sq = [A_, C_, (C_[0] + nx, C_[1] + ny), (A_[0] + nx, A_[1] + ny)]
    for i in range(5):
        for j in range(5):
            p0 = (A_[0] + dx * i / 5 + nx * j / 5, A_[1] + dy * i / 5 + ny * j / 5)
            pts = [p0, (p0[0] + dx / 5, p0[1] + dy / 5), (p0[0] + dx / 5 + nx / 5, p0[1] + dy / 5 + ny / 5),
                   (p0[0] + nx / 5, p0[1] + ny / 5)]
            pg.fillpoly(pts, C.LIGHT[C.PURPLE], outline=C.PURPLE, width=0.6)
    pg.text(ox + 2 * u, oy + 4 * u + 4, "4 × 4 = 16 tiles", 11, C.BLUE, F.BOLD, align="center")
    pg.text(ox + 7 * u + 8, oy - 2 * u, "3 × 3 = 9", 11, C.ORANGE, F.BOLD)
    pg.text(ox - 110, oy - 110, "5 × 5 = 25 tiles", 11, C.PURPLE, F.BOLD)
    badge(pg, ox + 2 * u + 8, oy - 1.5 * u + 10, "H", 6.5)
    pg.note(L + 360, y_ + 10, "9 + 16 = 25.\nThe two small squares\nexactly fill the big one.\n\nTrue for "
            "every right-\nangled triangle.", C.INK, 15)
    ch.check(3 ** 2 + 4 ** 2, 5 ** 2)
    step(f, r"h^2=o^2+a^2", "Pythagoras: hypotenuse squared = the other two squared, added", size=22,
         color=C.TEAL)
    ch.formula(r"h^2=o^2+a^2", "Pythagoras")
    ch.term("Pythagoras' theorem", "in a right-angled triangle, hypotenuse² = (one short side)² + (other short side)²")
    f.p("{b:Finding a short side} means subtracting instead. Lecture 6, Example 3: $h = 5$, $o = 2.5$:", 14, gap=6)
    step(f, r"a^2=5^2-2.5^2=25-6.25=18.75", "", size=18)
    step(f, r"a=\sqrt{18.75}\approx4.33", "don't forget the square root!", size=18, color=C.GREEN)
    ch.check_num(math.sqrt(25 - 6.25), 4.330, tol=0.001)
    f.p("(The slide writes \"$5^2 - 2.5^2 = a = 4.33$\", dropping the square root: $5^2 - 2.5^2$ is "
        "18.75, not 4.33.)", 12.5, C.GREY)


def why_pythag(ch):
    f = flow(ch)
    sec(f, "Why it's always true: four triangles in a box", room=420)
    f.p("Counting tiles only checks one triangle. Here's why it works for {B:every} right-angled triangle. "
        "Take four copies of any one, with short sides $o$ and $a$ and hypotenuse $h$, and a square box with "
        "sides $o + a$. Pack the triangles in two different ways:", 14, gap=12)
    o_, a_ = 42, 88
    S = o_ + a_
    y_ = f.reserve(S + 78)
    pg = f.pg
    tfill = C.LIGHT[C.TEAL]

    def box_labels(x0, y0, side_o_first=True):
        pg.text(x0 + o_ / 2 - 4, y0 - 18, "o", 12, C.ORANGE, F.BOLD)
        pg.text(x0 + o_ + a_ / 2 - 4, y0 - 18, "a", 12, C.BLUE, F.BOLD)
        first, second = (("o", C.ORANGE, o_), ("a", C.BLUE, a_)) if side_o_first else (("a", C.BLUE, a_), ("o", C.ORANGE, o_))
        pg.text(x0 - 14, y0 + first[2] / 2 - 8, first[0], 12, first[1], F.BOLD)
        pg.text(x0 - 14, y0 + first[2] + second[2] / 2 - 8, second[0], 12, second[1], F.BOLD)
        pg.rect(x0, y0, S, S, C.INK, 1.6)

    x0, y0 = L + 40, y_ + 24
    P = [(x0 + o_, y0), (x0 + S, y0 + o_), (x0 + a_, y0 + S), (x0, y0 + a_)]
    corners = [(x0, y0), (x0 + S, y0), (x0 + S, y0 + S), (x0, y0 + S)]
    pg.fillpoly(P, C.LIGHT[C.PURPLE], outline=C.PURPLE, width=1.2)
    for k in range(4):
        pg.fillpoly([corners[k], P[k], P[k - 1]], tfill, outline=C.INK, width=1.0)
    pg.eq(x0 + S / 2, y0 + S / 2, r"h^2", 18, C.PURPLE, align="center", valign="middle")
    box_labels(x0, y0, side_o_first=False)
    pg.text((P[0][0] + P[1][0]) / 2 - 12, (P[0][1] + P[1][1]) / 2 + 2, "h", 12, C.PURPLE, F.BOLD)
    pg.note(x0 - 20, y0 + S + 8, "4 triangles, and the tilted\nsquare on the hypotenuse", C.INK, 13)

    pg.arrow(x0 + S + 20, y0 + S / 2, x0 + S + 58, y0 + S / 2, C.GREY, 1.4, head=6)
    pg.note(x0 + S + 12, y0 + S / 2 + 6, "slide the\ntriangles", C.GREY, 12)

    x1 = L + 290
    pg.fillpoly([(x1, y0), (x1 + o_, y0), (x1 + o_, y0 + o_), (x1, y0 + o_)], C.LIGHT[C.ORANGE],
                outline=C.ORANGE, width=1.2)
    pg.fillpoly([(x1 + o_, y0 + o_), (x1 + S, y0 + o_), (x1 + S, y0 + S), (x1 + o_, y0 + S)], C.LIGHT[C.BLUE],
                outline=C.BLUE, width=1.2)
    for tri_ in ([(x1 + o_, y0), (x1 + S, y0), (x1 + S, y0 + o_)], [(x1 + o_, y0), (x1 + o_, y0 + o_), (x1 + S, y0 + o_)],
                 [(x1, y0 + o_), (x1 + o_, y0 + o_), (x1 + o_, y0 + S)], [(x1, y0 + o_), (x1, y0 + S), (x1 + o_, y0 + S)]):
        pg.fillpoly(tri_, tfill, outline=C.INK, width=1.0)
    pg.eq(x1 + o_ / 2, y0 + o_ / 2, r"o^2", 14, C.ORANGE, align="center", valign="middle")
    pg.eq(x1 + o_ + a_ / 2, y0 + o_ + a_ / 2, r"a^2", 18, C.BLUE, align="center", valign="middle")
    box_labels(x1, y0)
    pg.note(x1 - 20, y0 + S + 8, "the same 4 triangles, paired into\n2 rectangles, and two squares", C.INK, 13)
    ch.check_num(S ** 2 - 4 * (o_ * a_ / 2), o_ ** 2 + a_ ** 2, 1e-9)
    f.p("Both boxes are the same size and hold the same four triangles. So the space the triangles leave "
        "must be the same too: on the left that's $h^2$, on the right it's $o^2 + a^2$. Nothing here "
        "depended on the lengths, so it's true for {B:every} right-angled triangle:", 14, gap=6)
    step(f, r"\pur{h^2}=\org{o^2}+\blu{a^2}", "the leftover space, counted two ways", size=22, color=C.TEAL)
    f.p("(Chapter 11's perfect square is hiding here: the whole box is $(o + a)^2 = o^2 + 2oa + a^2$, "
        "and the four triangles are the two $oa$ rectangles.)", 13, C.GREY)


def pythag3d(ch):
    f = flow(ch)
    sec(f, "Pythagoras in 3D, and the circle", room=440)
    f.p("{b:A box:} the longest stick that fits in a 3 × 4 × 12 box goes corner to opposite corner. Use "
        "Pythagoras twice: across the floor, then up:", 14, gap=10)
    y_ = f.reserve(130)
    pg = f.pg
    ox, oy, a, b, c, dx, dy = L + 30, y_ + 110, 120, 50, 90, 45, -30
    fr = [(ox, oy), (ox + a, oy), (ox + a, oy - c), (ox, oy - c)]
    bk = [(x + dx, y + dy) for x, y in fr]
    for i in range(4):
        pg.line(*fr[i], *fr[(i + 1) % 4], C.INK, 1.2)
        pg.line(*bk[i], *bk[(i + 1) % 4], C.GREY, 0.8, dash=(3, 2) if i in (0, 3) else None)
        pg.line(*fr[i], *bk[i], C.GREY, 0.8, dash=(3, 2) if i == 0 else None)
    pg.line(ox, oy, bk[1][0], bk[1][1], C.BLUE, 1.6, dash=(4, 2))
    pg.line(ox, oy, bk[2][0], bk[2][1], C.RED, 2.2)
    pg.text(ox + a / 2, oy + 4, "4", 11, C.INK, align="center")
    pg.text(ox + a + dx / 2 + 6, oy + dy / 2, "3", 11, C.INK)
    pg.text(ox - 16, oy - c / 2, "12", 11, C.INK)
    pg.eq(L + 230, y_ + 10, r"\text{floor: }\sqrt{4^2+3^2}=5", 16, C.BLUE)
    pg.eq(L + 230, y_ + 45, r"\text{stick: }\sqrt{5^2+12^2}=13", 16, C.RED)
    pg.eq(L + 230, y_ + 85, r"d^2=a^2+b^2+c^2", 18, C.TEAL)
    ch.check(sp.sqrt(4 ** 2 + 3 ** 2 + 12 ** 2), 13)
    ch.term("Pythagoras in 3D", "the diagonal of a box: d² = a² + b² + c²")
    f.p("{b:A circle} is every point at distance $r$ from the centre $(a, b)$. The distance from the centre "
        "to a point $(x, y)$ is the hypotenuse of a triangle with sides $x - a$ and $y - b$, so Pythagoras "
        "gives Lecture 6's circle equation:", 14, gap=6)
    step(f, r"(x-a)^2+(y-b)^2=r^2", "centred at the origin: x² + y² = r²", size=20, color=C.TEAL)
    ch.formula(r"(x-a)^2+(y-b)^2=r^2", "circle, centre (a, b), radius r")
    ch.term("equation of a circle", "(x − a)² + (y − b)² = r²: centre (a, b), radius r")


def zoom(ch):
    f = flow(ch)
    sec(f, "Why sin, cos and tan exist: zoomed photos", room=500)
    f.p("Draw a right-angled triangle with a 30° angle. Now photograph it and zoom in: the triangle "
        "gets bigger but its {B:shape} can't change, because the angles are the same. Measure the sides "
        "of each copy:", 14, gap=12)
    y_ = f.reserve(148)
    pg = f.pg
    xx = L + 10
    for k, s_ in enumerate([1, 1.6, 2.3]):
        h_ = 60 * s_
        o_, a_ = h_ / 2, h_ * math.sqrt(3) / 2
        tri(pg, xx, y_ + 110, a_, o_, None, fill=C.LIGHT[C.TEAL], tags=None)
        badge(pg, xx + a_ + 10, y_ + 110 - o_ / 2, "O", 6)
        pg.text(xx + a_ + 18, y_ + 110 - o_ / 2 - 6, f"{2 * s_:g}", 10, C.ORANGE, F.BOLD)
        badge(pg, xx + a_ / 2 - 22, y_ + 110 - o_ / 2 - 13, "H", 6)
        pg.text(xx + a_ / 2 - 14, y_ + 110 - o_ / 2 - 20, f"{4 * s_:g}", 10, C.PURPLE, F.BOLD)
        badge(pg, xx + a_ / 2 - 12, y_ + 120, "A", 6)
        pg.text(xx + a_ / 2 - 4, y_ + 114, f"{4 * s_ * math.sqrt(3) / 2:.2f}", 10, C.BLUE, F.BOLD)
        pg.text(xx + a_ / 2, y_ + 132, f"O ÷ H: {2 * s_:g} ÷ {4 * s_:g} = 0.5", 9, C.INK, align="center")
        xx += a_ + 50
    ch.check_num(math.sin(math.radians(30)), 0.5)
    f.gap(4)
    f.p("{B:Every} 30° triangle has opposite ÷ hypotenuse = 0.5, however big. The ratio depends {B:only "
        "on the angle}. So we give each ratio a name and let the calculator remember them:", 14, gap=10)
    ch.term("similar triangles", "triangles with the same angles: one is a zoomed copy of the other, so side ratios match")
    y_ = f.reserve(110)
    pg = f.pg
    trio = [(r"\sin\theta=\frac{\text{opp}}{\text{hyp}}", "S O H", C.ORANGE, "sine"),
            (r"\cos\theta=\frac{\text{adj}}{\text{hyp}}", "C A H", C.BLUE, "cosine"),
            (r"\tan\theta=\frac{\text{opp}}{\text{adj}}", "T O A", C.GREEN, "tangent")]
    for k, (lat, code, col, nm) in enumerate(trio):
        x0 = L + k * 168
        pg.rect(x0, y_, 156, 100, col, 1.4, fillcolor=C.LIGHT[col], r=8)
        pg.text(x0 + 78, y_ + 6, code, 16, col, F.BOLD, align="center")
        pg.eq(x0 + 78, y_ + 60, lat, 17, align="center", valign="middle")
        pg.text(x0 + 78, y_ + 84, f"({nm})", 10, C.GREY, align="center")
    for lat, nm in [(r"\sin\theta=\frac{o}{h}", "sine"), (r"\cos\theta=\frac{a}{h}", "cosine"),
                    (r"\tan\theta=\frac{o}{a}", "tangent")]:
        ch.formula(lat, nm)
    ch.term("sine, cosine, tangent", "the ratios opp/hyp, adj/hyp and opp/adj of a right-angled triangle, fixed by the angle")
    ch.term("SOHCAHTOA", "memory aid: Sin = Opp/Hyp, Cos = Adj/Hyp, Tan = Opp/Adj")
    ch.symbol(r"\sin\theta", "sine theta (say 'sign')", "opp ÷ hyp for the angle θ")
    f.gap(8)
    f.p("{B:SOHCAHTOA} glues the codes together. Lecture 6 admits it's a nightmare to pronounce and "
        "suggests your own sentence, e.g. {h:\"Some Old Horses Can Always Hear Their Owners "
        "Approach\"}. Degrees or radians doesn't matter here: like measuring in feet or inches.", 14)


def ladder(ch):
    f = flow(ch)
    sec(f, "The ladder, in five tiny steps", room=560)
    f.p("{B:A 5 m ladder makes 70° with the ground. How high up the wall does it reach?}", 14, gap=12)
    y_ = f.reserve(222)
    pg = f.pg
    tri(pg, L + 50, y_ + 150, 50, 137, ("hyp = 5", "opp = ?", "adj"), fill=C.LIGHT[C.TEAL], theta_at="none")
    pg.arc(L + 50, y_ + 150, 20, 0, 70, C.RED, 1.4)
    pg.text(L + 72, y_ + 118, "70°", 10, C.RED, F.BOLD)
    labels = ["1  Label the sides from θ = 70°: the ladder is the hypotenuse, the wall height is opposite.",
              "2  What do I know, what do I want? Know hyp, want opp: O and H, so SOH, sine.",
              "3  Write it: sin 70° = opp ÷ 5.",
              "4  Transpose (Chapter 14): opp = 5 × sin 70°.",
              "5  Calculate: 5 × 0.9397 = 4.70 m."]
    for k, s_ in enumerate(labels):
        pg.note(L + 225, y_ + k * 44, s_, C.INK if k < 4 else C.GREEN, 14, w=W - 225)
    ch.check_num(5 * math.sin(math.radians(70)), 4.698, tol=0.001)
    f.gap(6)
    f.p("{b:How far is its foot from the wall?} Now we want the adjacent side: A and H, so CAH, cosine:", 14, gap=6)
    step(f, r"\cos70^\circ=\frac{\text{adj}}{5}", "", size=19)
    step(f, r"\text{adj}=5\cos70^\circ=5\times0.342=1.71\text{ m}", "", size=19, color=C.GREEN)
    ch.check_num(5 * math.cos(math.radians(70)), 1.710, tol=0.001)
    f.p("{G:Check with Pythagoras:} $4.70^2 + 1.71^2 = 22.09 + 2.92 = 25.0 = 5^2$ ✓.", 13.5, gap=10)
    f.p("{b:Cover-up triangles} save the transposing. Put the top letter over the other two; cover what "
        "you want:", 14, gap=10)
    y_ = f.reserve(100)
    pg = f.pg
    for k, (top, l_, r_, col) in enumerate([("O", "S", "H", C.ORANGE), ("A", "C", "H", C.BLUE),
                                            ("O", "T", "A", C.GREEN)]):
        cx = L + 70 + k * 160
        pts = [(cx, y_), (cx + 55, y_ + 85), (cx - 55, y_ + 85)]
        pg.fillpoly(pts, C.LIGHT[col], outline=col, width=1.4)
        pg.line(cx - 34, y_ + 52, cx + 34, y_ + 52, col, 1.2)
        pg.line(cx, y_ + 52, cx, y_ + 85, col, 1.2)
        pg.text(cx, y_ + 26, top, 16, col, F.BOLD, align="center")
        pg.text(cx - 18, y_ + 60, l_, 15, col, F.BOLD, align="center")
        pg.text(cx + 18, y_ + 60, r_, 15, col, F.BOLD, align="center")
    f.p("Cover O in the first: O = S × H. Cover H: H = O ÷ S. (Same idea as the speed-distance-time "
        "triangle.)", 13.5)


def mini(f, labels, angle, why):
    """A small badged triangle for one example, with the SOH/CAH/TOA choice read off the badges."""
    y_ = f.reserve(108)
    pg = f.pg
    tri(pg, L + 50, y_ + 82, 130, 64, labels, fill=C.LIGHT[C.TEAL], theta_at="none")
    pg.arc(L + 50, y_ + 82, 24, 0, math.degrees(math.atan2(64, 130)), C.RED, 1.4)
    pg.text(L + 78, y_ + 66, angle, 10, C.RED, F.BOLD)
    pg.note(L + 300, y_ + 30, why, C.INK, 14, w=R - L - 300)


def lecture(ch):
    f = flow(ch)
    sec(f, "Lecture 6's examples, and the undo button", room=560)
    f.need(150)
    f.p("{b:Example 1:} opposite = 3, adjacent = 4. Find $\\theta$.", 14, gap=6)
    mini(f, ("h", "o = 3", "a = 4"), "θ = ?", "badges: O and A are known, so TOA (tan)")
    step(f, r"\tan\theta=\frac34=0.75", "", size=19)
    f.p("Now $\\theta$ is {B:stuck inside} the tan. We need an {B:undo button} for tan, just as in "
        "Chapter 14 (÷ undoes ×) and Chapter 22 (log undoes power). It's called {B:inverse tan}, "
        "written $\\tan^{-1}$ (or arctan):", 14, gap=6)
    step(f, r"\theta=\tan^{-1}(0.75)=36.87^\circ", "SHIFT then tan on the calculator", size=19, color=C.GREEN)
    ch.check_num(math.degrees(math.atan(0.75)), 36.87, tol=0.005)
    y_ = f.reserve(60)
    pg = f.pg
    pg.rect(L + 20, y_ + 10, 90, 34, C.TEAL, 1.3, fillcolor=C.LIGHT[C.TEAL], r=6)
    pg.text(L + 65, y_ + 19, "36.87°", 13, C.INK, F.BOLD, align="center")
    pg.rect(L + 330, y_ + 10, 90, 34, C.TEAL, 1.3, fillcolor=C.LIGHT[C.TEAL], r=6)
    pg.text(L + 375, y_ + 19, "0.75", 13, C.INK, F.BOLD, align="center")
    pg.arrow(L + 115, y_ + 18, L + 325, y_ + 18, C.ORANGE, 1.5, head=6, bend=-0.08)
    pg.arrow(L + 325, y_ + 38, L + 115, y_ + 38, C.GREEN, 1.5, head=6, bend=-0.08)
    pg.text(L + 220, y_ - 2, "tan", 12, C.ORANGE, F.BOLD, align="center")
    pg.text(L + 220, y_ + 44, "tan⁻¹ (undo)", 12, C.GREEN, F.BOLD, align="center")
    ch.term("inverse trig functions", "sin⁻¹, cos⁻¹, tan⁻¹ (arcsin, arccos, arctan): given the ratio, they give back the angle")
    ch.symbol(r"\sin^{-1}", "inverse sine, or arcsine", "the angle whose sine is ...")
    f.p("{R:Warning:} the $-1$ here means \"undo\", {B:not} \"1 over\" (Chapter 9's negative powers). "
        "$\\sin^{-1}x$ is not $\\frac{1}{\\sin x}$. Sorry, mathematicians reused the symbol.", 13.5, gap=10)
    f.need(150)
    f.p("{b:Example 2:} $h = 5$, $\\theta = 36.87^\\circ$. Find $a$.", 14, gap=6)
    mini(f, ("h = 5", "o", "a = ?"), "36.87°", "badges: know H, want A, so CAH (cos)")
    step(f, r"a=5\times\cos36.87^\circ=4", "", size=19, color=C.GREEN)
    ch.check_num(5 * math.cos(math.radians(36.87)), 4.0, tol=0.001)
    f.p("(Lecture 6 asks \"what do we think about the notation here?\": it writes 36.870° with a "
        "superscript o. Use a proper ° sign.)", 12.5, C.GREY, gap=8)
    f.need(150)
    f.p("{b:Example 3:} $h = 5$, $\\theta = 30^\\circ$. Find all the sides.", 14, gap=6)
    mini(f, ("h = 5", "o = ?", "a = ?"), "30°", "badges: know H, want O first, so SOH (sin); "
         "then Pythagoras for A")
    step(f, r"o=5\sin30^\circ=2.5,\qquad a=\sqrt{5^2-2.5^2}=4.33", "", size=18, color=C.GREEN)


def exact(ch):
    f = flow(ch)
    sec(f, "Two special triangles give exact values", room=520)
    f.p("A few angles have sin, cos and tan you can write exactly, with no calculator. They come from "
        "two triangles:", 14, gap=12)
    y_ = f.reserve(176)
    pg = f.pg
    tri(pg, L + 20, y_ + 130, 110, 110, None, theta_at="none", fill=C.LIGHT[C.TEAL])
    pg.text(L + 70, y_ + 134, "1", 12, C.BLUE, F.BOLD)
    pg.text(L + 136, y_ + 70, "1", 12, C.ORANGE, F.BOLD)
    pg.eq(L + 40, y_ + 40, r"\sqrt2", 14, C.PURPLE)
    pg.text(L + 40, y_ + 110, "45°", 10, C.RED, F.BOLD)
    pg.note(L + 10, y_ + 150, "half a square", C.GREY, 13)
    bx = L + 230
    pg.fillpoly([(bx, y_ + 130), (bx + 64, y_ + 130), (bx + 64, y_ + 20)], C.LIGHT[C.TEAL])
    pg.poly([(bx, y_ + 130), (bx + 128, y_ + 130), (bx + 64, y_ + 20)], C.INK, 1.2, closed=True, dash=None)
    pg.line(bx + 64, y_ + 20, bx + 64, y_ + 130, C.INK, 1.6)
    pg.rect(bx + 55, y_ + 121, 9, 9, C.INK, 0.8)
    pg.text(bx + 30, y_ + 134, "1", 12, C.BLUE, F.BOLD)
    pg.text(bx + 16, y_ + 64, "2", 12, C.PURPLE, F.BOLD)
    pg.eq(bx + 70, y_ + 64, r"\sqrt3", 14, C.ORANGE)
    pg.text(bx + 18, y_ + 110, "60°", 10, C.RED, F.BOLD)
    pg.text(bx + 56, y_ + 38, "30°", 10, C.RED, F.BOLD, align="right")
    badge(pg, bx + 20, y_ + 141, "A", 6.5)
    badge(pg, bx + 76, y_ + 98, "O", 6.5)
    badge(pg, bx + 22, y_ + 50, "H", 6.5)
    pg.note(bx + 90, y_ + 150, "half an equilateral triangle (all sides 2)", C.GREY, 13)
    pg.note(bx + 150, y_ + 30, "badges from the 60° corner.\nFrom the 30° corner, O and A swap:\n"
            "opp = 1, adj = √3", C.GREY, 13, w=R - bx - 150)
    ch.check(sp.sqrt(1 + 1), sp.sqrt(2))
    ch.check(sp.sqrt(2 ** 2 - 1), sp.sqrt(3))
    f.p("Pythagoras gives the missing sides ($\\sqrt{1^2 + 1^2} = \\sqrt2$ and $\\sqrt{2^2 - 1^2} = "
        "\\sqrt3$). Now read off SOHCAHTOA:", 14, gap=10)
    y_ = f.reserve(26 * 4 + 6)
    pg = f.pg
    cols = ["", "30°", "45°", "60°"]
    vals = [(r"\sin", [r"\tfrac12", r"\tfrac{1}{\sqrt2}", r"\tfrac{\sqrt3}{2}"]),
            (r"\cos", [r"\tfrac{\sqrt3}{2}", r"\tfrac{1}{\sqrt2}", r"\tfrac12"]),
            (r"\tan", [r"\tfrac{1}{\sqrt3}", r"1", r"\sqrt3"])]
    for j, c_ in enumerate(cols):
        pg.text(L + 60 + j * 100, y_, c_, 12, C.RED, F.BOLD, align="center")
    for i, (fn, vs) in enumerate(vals):
        yy = y_ + 34 + i * 28
        pg.eq(L + 60, yy, fn, 15, C.TEAL, align="center", valign="middle")
        for j, v in enumerate(vs):
            pg.eq(L + 160 + j * 100, yy, v, 15, align="center", valign="middle")
    ch.check([sp.sin(sp.pi / 6), sp.cos(sp.pi / 4), sp.tan(sp.pi / 3)], [sp.Rational(1, 2), 1 / sp.sqrt(2), sp.sqrt(3)])
    ch.term("exact trig values", "sin, cos, tan of 30°, 45°, 60° written with roots, from the two special triangles")
    f.gap(8)
    f.p("Lecture 6 uses the 45° one: $(\\cos45^\\circ, \\sin45^\\circ) = (\\frac{1}{\\sqrt2}, \\frac{1}{\\sqrt2})$.",
        14)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Draw and label the triangle first (Lecture 6's advice). Answers in grey.", 13.5, gap=10)
    groups = [
        ("Pythagoras", ["Short sides 5 and 12: hypotenuse?", "Hypotenuse 10, one side 6: the other side?",
                        "Diagonal of a 2 × 3 × 6 box"],
         "1. 13   2. 8   3. √(4 + 9 + 36) = 7"),
        ("Sides", ["hyp 8, θ = 40°: opposite?", "adj 6, θ = 25°: opposite?", "opp 4, θ = 55°: hypotenuse?"],
         "4. 8 sin 40° ≈ 5.14   5. 6 tan 25° ≈ 2.80   6. 4 ÷ sin 55° ≈ 4.88"),
        ("Angles", ["opp 5, hyp 13: θ?", "adj 7, hyp 10: θ?", "A ramp rises 1 m over 12 m of ground. Its angle?"],
         "7. sin⁻¹(5/13) ≈ 22.6°   8. cos⁻¹(0.7) ≈ 45.6°   9. tan⁻¹(1/12) ≈ 4.8°"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.TEAL, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    d = math.radians
    ch.check([sp.sqrt(25 + 144), sp.sqrt(100 - 36), sp.sqrt(4 + 9 + 36)], [13, 8, 7])
    ch.check_num(8 * math.sin(d(40)), 5.14, tol=0.005)
    ch.check_num(6 * math.tan(d(25)), 2.80, tol=0.005)
    ch.check_num(4 / math.sin(d(55)), 4.88, tol=0.005)
    ch.check_num(math.degrees(math.asin(5 / 13)), 22.6, tol=0.05)
    ch.check_num(math.degrees(math.acos(0.7)), 45.6, tol=0.05)
    ch.check_num(math.degrees(math.atan(1 / 12)), 4.8, tol=0.05)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    names(ch)
    pythag(ch)
    why_pythag(ch)
    pythag3d(ch)
    zoom(ch)
    ladder(ch)
    lecture(ch)
    exact(ch)
    your_turn(ch)
