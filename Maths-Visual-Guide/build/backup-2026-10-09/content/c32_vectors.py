"""Chapter 32 - Vectors (Lecture 10). A vector is a trip on a city map: blocks east and north (i, j),
floors up (k). Distance vs displacement with an out-and-back run, tip-to-tail adding (in any order),
Pythagoras for the length, the dot product as a sled rope's shadow, the cross product as a
screwdriver plus the parallelogram area, and the 3 x 3 determinant by covering rows and columns."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 32
NUM = 32
TITLE = "Vectors"
SHORT = "Vectors"
SLUG = "Vectors"
ACCENT = C.BLUE
REQUIRES = ["pythagoras", "pythagoras-3d", "cosine", "sine", "inverse-trig", "coordinates", "negative-numbers",
            "determinant", "matrix", "angle", "degrees", "right-angle", "area", "square-and-root-words"]
INTRODUCES = ["scalar", "vector", "vector-notation", "unit-vectors", "displacement", "vector-addition",
              "vector-subtraction", "scalar-times-vector", "vector-magnitude", "dot-product",
              "perpendicular-vectors", "cross-product", "right-hand-rule", "determinant-3x3"]

PAPER = "#f8fafe"


def icon(pg, x0, y0):
    pg.arrow(x0 + 2, y0 + 16, x0 + 16, y0 + 3, C.BLUE, 1.8, head=5)


def sec(f, t_, **kw):
    section(f, t_, C.BLUE, icon, **kw)


def city(pg, x0, y0, nx, ny, s, gx0=0, gy0=0):
    """nx x ny city blocks. Returns G(gx, gy): the street corner gx blocks east, gy blocks north,
    where (gx0, gy0) is the bottom-left corner."""
    ins = max(2.0, s * 0.14)
    for i in range(nx):
        for j in range(ny):
            pg.rect(x0 + i * s + ins, y0 + j * s + ins, s - 2 * ins, s - 2 * ins, "#dadada", 0.3,
                    fillcolor="#efefef", r=2)
    return lambda gx, gy: (x0 + (gx - gx0) * s, y0 + (ny - (gy - gy0)) * s)


def vec(pg, P, Q, col, w=2.2, dash=None, head=7):
    pg.arrow(P[0], P[1], Q[0], Q[1], col, w, head=head, dash=dash)


def lab(pg, x, y, latex, col, size=14):
    pg.eq(x, y - 8, latex, size, col, align="center", solid=False)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 32, "Vectors", "a vector is a trip: how far, and which way", C.BLUE, PAPER)
    G = city(pg, L + 20, 190, 8, 4, 40)
    start, turn, end = G(1, 1), G(6, 1), G(6, 4)
    vec(pg, start, turn, C.ORANGE, 2.0, dash=(5, 3))
    vec(pg, turn, end, C.TEAL, 2.0, dash=(5, 3))
    vec(pg, start, end, C.BLUE, 3.0, head=9)
    pg.dot(*start, 4, C.INK)
    pg.text(start[0] - 30, start[1] + 6, "you", 12, C.INK, F.BOLD, solid=False)
    pg.star(end[0], end[1] - 2, 10, C.ORANGE)
    lab(pg, (start[0] + turn[0]) / 2, turn[1] + 16, r"5\,\mathbf i", C.ORANGE)
    lab(pg, turn[0] + 20, (turn[1] + end[1]) / 2, r"3\,\mathbf j", C.TEAL)
    lab(pg, (start[0] + end[0]) / 2 - 16, (start[1] + end[1]) / 2 - 16, r"\mathbf a", C.BLUE, 16)
    pg.note(L + 355, 215, "5 blocks east, then 3 north.\nThe blue arrow is the whole\ntrip in one go: "
            "that's the\nvector a = 5i + 3j.", C.BLUE, 15, w=R - L - 355)
    f = ch.flow(top=380)
    f.p("Some things are just a size: 20 °C, 3 kg, 10 miles. Others only make sense with a {B:direction} "
        "too: a push, a wind, a trip across town. Those are {B:vectors}, and this chapter treats every "
        "one of them as a little trip on a map: how many blocks east, how many north, and (in 3D) how "
        "many floors up.", 14, gap=10)
    f.p("You'll add trips, stretch them, measure them, and multiply them in two very different ways "
        "(the dot product and the cross product), each with its own picture.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 10} {y:(scalars and vectors, notation, unit vectors, adding and "
        "subtracting, scalar multiples, dot product, cross product, determinants).}", 12.5)


def scalars(ch):
    f = flow(ch)
    sec(f, "Size only, or size and direction?", room=520)
    f.p("A {B:scalar} is one piece of information: its size. A {B:vector} needs two: its size {B:and} "
        "its direction. Same speed, two different stories:", 14, gap=10)
    y_ = f.reserve(160)
    pg = f.pg
    cx, cy, r_ = L + 90, y_ + 70, 52
    pg.arc(cx, cy, r_, -30, 210, C.INK, 1.6)
    for k in range(11):
        t = math.radians(210 - k * 24)
        pg.line(cx + (r_ - 7) * math.cos(t), cy - (r_ - 7) * math.sin(t), cx + r_ * math.cos(t),
                cy - r_ * math.sin(t), C.INK, 1.0)
    pg.text(cx - r_ + 4, cy + 20, "0", 9, C.GREY)
    pg.text(cx + r_ - 22, cy + 20, "100", 9, C.GREY)
    pg.line(cx, cy, cx, cy - 42, C.RED, 2.6)
    pg.dot(cx, cy, 4, C.INK)
    pg.text(cx - 40, cy + 8, "50 mph", 12, C.INK, F.BOLD, w=80, align="center")
    pg.rich(cx - 90, cy + 70, "{B:scalar}: speed = 50 mph", w=180, size=12, align="center")
    cx2 = L + 330
    pg.circle(cx2, cy, r_, C.GREY, 1.2)
    for s_, dx, dy in [("N", 0, -r_ - 14), ("E", r_ + 8, -7), ("S", 0, r_ + 1), ("W", -r_ - 14, -7)]:
        pg.text(cx2 + dx - (4 if s_ in "NS" else 0), cy + dy, s_, 11, C.GREY, F.BOLD)
    vec(pg, (cx2, cy), (cx2 + 40, cy - 40), C.BLUE, 2.8, head=8)
    pg.text(cx2 + 42, cy - 56, "50 mph", 11, C.BLUE, F.BOLD)
    pg.rich(cx2 - 140, cy + 70, "{B:vector}: velocity = 50 mph north-east", w=280, size=12, align="center")
    ch.term("scalar", "a quantity with size only (speed, distance, mass, temperature)")
    ch.term("vector", "a quantity with size AND direction (velocity, displacement, force)")
    f.gap(8)
    f.p("{b:Lecture 10's runner} jogs 5 miles away from home, then 5 miles back:", 14, gap=10)
    y_ = f.reserve(120)
    pg = f.pg
    yr = y_ + 55
    pg.line(L + 30, yr, L + 330, yr, "#bdbdbd", 4)
    house = [(L + 18, yr), (L + 18, yr - 17), (L + 30, yr - 27), (L + 42, yr - 17), (L + 42, yr)]
    pg.fillpoly(house, C.LIGHT[C.ORANGE])
    pg.poly(house, C.INK, 1.2, closed=True)
    pg.text(L + 14, yr + 6, "home", 10, C.INK)
    pg.line(L + 330, yr, L + 330, yr - 26, C.INK, 1.2)
    pg.fillpoly([(L + 330, yr - 26), (L + 348, yr - 21), (L + 330, yr - 16)], C.RED)
    pg.text(L + 312, yr + 6, "5 miles", 10, C.INK)
    vec(pg, (L + 50, y_ + 22), (L + 322, y_ + 22), C.GREEN, 2.0)
    pg.rich(L + 120, y_ + 4, "{G:+5 miles} (out)", w=140, size=11, align="center", solid=False)
    vec(pg, (L + 322, y_ + 88), (L + 50, y_ + 88), C.RED, 2.0)
    pg.rich(L + 120, y_ + 93, "{R:−5 miles} (back)", w=140, size=11, align="center", solid=False)
    pg.note(L + 362, y_ + 2, "distance (scalar):\n5 + 5 = 10 miles\n\ndisplacement (vector):\n"
            "+5 + (−5) = 0\nhe ends where he began", C.INK, 14, w=R - L - 362)
    ch.term("distance", "how far you travelled in total: a scalar")
    ch.term("displacement", "where you ended up compared with the start (how far and which way): a vector")
    f.p("Same with north then south, or any direction and its opposite: the two trips cancel.", 14)


def notation(ch):
    f = flow(ch)
    sec(f, "One arrow, four spellings", room=260)
    f.p("Lecture 10 admits the notation is \"quite confusing\". All four of these mean the same arrow, "
        "the trip from point A to point B, named $\\mathbf a$:", 14, gap=12)
    y_ = f.reserve(135)
    pg = f.pg
    A_, B_ = (L + 30, y_ + 110), (L + 170, y_ + 25)
    vec(pg, A_, B_, C.BLUE, 2.6, head=9)
    pg.dot(*A_, 3.5, C.INK)
    pg.text(A_[0] - 16, A_[1] - 4, "A", 12, C.INK, F.BOLD)
    pg.text(B_[0] + 6, B_[1] - 14, "B", 12, C.INK, F.BOLD)
    lab(pg, (A_[0] + B_[0]) / 2 - 14, (A_[1] + B_[1]) / 2 - 12, r"\mathbf a", C.BLUE, 16)
    rows = [(r"\vec{a}", "arrow over the letter"),
            (r"\overrightarrow{AB}", "the trip from A to B"),
            (r"\mathbf{a}", "bold: how books print it"),
            (r"\underline{a}", "underlined: how you write it by hand (you can't write bold with a pen)")]
    for k, (lat, why) in enumerate(rows):
        yy = y_ + 2 + k * 32
        pg.eq(L + 230, yy, lat, 16, C.BLUE)
        pg.note(L + 290, yy - 2, why, C.INK, 14, w=R - L - 290)
    ch.symbol(r"\vec a", "vector a", "a vector named a (also bold a, or a underlined)")
    ch.symbol(r"\overrightarrow{AB}", "vector A B", "the vector that takes you from point A to point B")
    ch.term("vector notation", "an arrow over the letter, bold type, or an underline all mark a vector")


def unit_vectors(ch):
    f = flow(ch)
    sec(f, "i, j and k: one block east, one north, one floor up", room=520)
    f.p("In a city you give directions in blocks: \"2 east, 3 north\". Vectors do exactly this using three "
        "standard mini-trips, each exactly {B:1 long} (a {B:unit vector}):", 14, gap=6)
    f.p("{O:$\\mathbf i$} = one step along $x$ (east),  {T:$\\mathbf j$} = one step along $y$ (north),  "
        "{P:$\\mathbf k$} = one step along $z$ (one floor up). Lecture 10 writes them with hats: "
        "$\\hat{\\imath},\\hat{\\jmath},\\hat{k}$.", 14, gap=12)
    y_ = f.reserve(190)
    pg = f.pg
    G = city(pg, L + 20, y_ + 8, 4, 4, 38)
    for k in range(2):
        vec(pg, G(k, 0), G(k + 1, 0), C.ORANGE, 2.2, head=6)
        lab(pg, (G(k, 0)[0] + G(k + 1, 0)[0]) / 2, G(0, 0)[1] + 14, r"\mathbf i", C.ORANGE)
    for k in range(3):
        vec(pg, G(2, k), G(2, k + 1), C.TEAL, 2.2, head=6)
        lab(pg, G(2, 0)[0] + 12, (G(2, k)[1] + G(2, k + 1)[1]) / 2, r"\mathbf j", C.TEAL)
    vec(pg, G(0, 0), G(2, 3), C.BLUE, 2.8, head=9)
    lab(pg, (G(0, 0)[0] + G(2, 3)[0]) / 2 - 16, (G(0, 0)[1] + G(2, 3)[1]) / 2 - 8, r"\mathbf a", C.BLUE, 16)
    pg.note(L + 185, y_ + 20, "a = 2i + 3j", C.BLUE, 16)
    O = (L + 300, y_ + 150)
    ex, ey, ez = (30, 0), (18, -13.5), (0, -30)

    def Pt(a, b, c):
        return (O[0] + a * ex[0] + b * ey[0] + c * ez[0], O[1] + a * ex[1] + b * ey[1] + c * ez[1])

    for end, nm in [(Pt(4.8, 0, 0), "x"), (Pt(0, 4.4, 0), "y"), (Pt(0, 0, 4), "z")]:
        pg.arrow(O[0], O[1], end[0], end[1], C.GREY, 1.0, head=5)
        pg.text(end[0] + 4, end[1] - 14, nm, 11, C.GREY, F.BOLD)
    pg.line(O[0], O[1], O[0], O[1] + 26, C.GREY, 0.8, dash=(3, 3))
    P1, P2, P3 = Pt(2, 0, 0), Pt(2, 3, 0), Pt(2, 3, -1)
    vec(pg, O, P1, C.ORANGE, 2.0, dash=(4, 3), head=6)
    vec(pg, P1, P2, C.TEAL, 2.0, dash=(4, 3), head=6)
    vec(pg, P2, P3, C.PURPLE, 2.0, dash=(4, 3), head=6)
    vec(pg, O, P3, C.BLUE, 2.6, head=8)
    lab(pg, (O[0] + P1[0]) / 2, O[1] + 16, r"2\mathbf i", C.ORANGE, 13)
    lab(pg, (P1[0] + P2[0]) / 2 - 16, (P1[1] + P2[1]) / 2 - 14, r"3\mathbf j", C.TEAL, 13)
    lab(pg, P2[0] + 16, P2[1] + 2, r"-\mathbf k", C.PURPLE, 13)
    pg.text(P3[0] - 6, O[1] + 3, "(2, 3, −1)", 10, C.BLUE, F.BOLD)
    pg.note(O[0] + 24, Pt(0, 0, 4)[1] - 10, "k = one floor up", C.PURPLE, 14)
    ch.term("unit vector", "a vector of length exactly 1; i, j, k point along the x, y, z axes")
    ch.symbol(r"\mathbf i,\ \mathbf j,\ \mathbf k", "i, j, k", "unit vectors along x, y and z (also written with hats)")
    f.p("On the right is Lecture 10's 3D example, $\\mathbf a = 2\\mathbf i+3\\mathbf j-\\mathbf k$: 2 east, "
        "3 north, then one floor {B:down} (that's the $-\\mathbf k$). So $x = 2$, $y = 3$, $z = -1$. These "
        "are {B:Cartesian} coordinates; Chapter 33 shows the other way (polar).", 14, gap=8)
    f.p("The same trip can be written as a column (or a row), the numbers in order $x, y, z$:", 14, gap=6)
    step(f, r"2\mathbf i+3\mathbf j-\mathbf k=\begin{pmatrix}2\\3\\-1\end{pmatrix}=(2,\,3,\,-1)",
         "three ways, one trip", size=18)


def adding(ch):
    f = flow(ch)
    sec(f, "Adding: one trip, then the next (tip to tail)", room=560)
    f.p("To add vectors, do the first trip, then start the second one {B:where the first one ended}. The "
        "answer is the single arrow from the very start to the very end. That's why \"1 up + 2 right\" "
        "isn't 3 of anything: it's one diagonal trip.", 14, gap=6)
    f.p("Lecture 10's example: $\\mathbf a = 7\\mathbf i+3\\mathbf j$,  $\\mathbf b = \\mathbf i-2\\mathbf j$,  "
        "$\\mathbf c = -3\\mathbf i+\\mathbf j$.", 14, gap=10)
    y_ = f.reserve(128)
    pg = f.pg
    s = 22
    pg.rich(L + 5, y_, "{B:a + b}", w=200, size=12, color=C.PURPLE)
    G1 = city(pg, L + 5, y_ + 18, 9, 4, s)
    O1, A1, B1 = G1(0, 0), G1(7, 3), G1(8, 1)
    vec(pg, O1, B1, C.PURPLE, 2.0, dash=(5, 3))
    vec(pg, O1, A1, C.BLUE, 2.2)
    vec(pg, A1, B1, C.ORANGE, 2.2)
    pg.dot(*O1, 3.5, C.INK)
    lab(pg, (O1[0] + A1[0]) / 2 - 12, (O1[1] + A1[1]) / 2 - 12, r"\mathbf a", C.BLUE)
    lab(pg, (A1[0] + B1[0]) / 2 + 14, (A1[1] + B1[1]) / 2 - 6, r"\mathbf b", C.ORANGE)
    lab(pg, (O1[0] + B1[0]) / 2 + 8, (O1[1] + B1[1]) / 2 + 12, r"\mathbf a+\mathbf b", C.PURPLE, 12)
    x2 = L + 5 + 9 * s + 30
    pg.rich(x2, y_, "{R:c + a + b}: a different order, same finish", w=260, size=12)
    G2 = city(pg, x2, y_ + 18, 11, 4, s, gx0=-3)
    O2, C2, A2, B2 = G2(0, 0), G2(-3, 1), G2(4, 4), G2(5, 2)
    vec(pg, O2, B2, C.RED, 2.4)
    vec(pg, O2, C2, C.GREEN, 2.2)
    vec(pg, C2, A2, C.BLUE, 2.2)
    vec(pg, A2, B2, C.ORANGE, 2.2)
    pg.dot(*O2, 3.5, C.INK)
    lab(pg, (O2[0] + C2[0]) / 2, (O2[1] + C2[1]) / 2 - 14, r"\mathbf c", C.GREEN)
    lab(pg, (C2[0] + A2[0]) / 2 - 12, (C2[1] + A2[1]) / 2 - 12, r"\mathbf a", C.BLUE)
    lab(pg, (A2[0] + B2[0]) / 2 + 14, (A2[1] + B2[1]) / 2 - 6, r"\mathbf b", C.ORANGE)
    lab(pg, (O2[0] + B2[0]) / 2 + 10, (O2[1] + B2[1]) / 2 + 14, r"\mathbf a+\mathbf b+\mathbf c", C.RED, 12)
    f.gap(4)
    f.p("With numbers it's even easier: keep {O:$\\mathbf i$}'s with $\\mathbf i$'s and {T:$\\mathbf j$}'s "
        "with $\\mathbf j$'s, like two separate tally columns:", 14, gap=8)
    y_ = f.reserve(120)
    pg = f.pg
    xi, xj = L + 210, L + 270
    pg.eq(xi, y_, r"\mathbf i", 15, C.ORANGE, align="center")
    pg.eq(xj, y_, r"\mathbf j", 15, C.TEAL, align="center")
    for k, (nm, a, b, col) in enumerate([("a", "7", "3", C.BLUE), ("b", "1", "-2", C.ORANGE),
                                         ("c", "-3", "1", C.GREEN)]):
        yy = y_ + 24 + k * 22
        pg.eq(L + 150, yy, r"\mathbf " + nm, 15, col, align="center")
        pg.eq(xi, yy, a, 15, align="center")
        pg.eq(xj, yy, b, 15, align="center")
    pg.line(L + 135, y_ + 92, L + 295, y_ + 92, C.INK, 1.2)
    pg.eq(xi, y_ + 98, "5", 16, C.RED, align="center")
    pg.eq(xj, y_ + 98, "2", 16, C.RED, align="center")
    pg.eq(L + 315, y_ + 96, r"\mathbf a+\mathbf b+\mathbf c=5\mathbf i+2\mathbf j", 16, C.RED)
    pg.note(L, y_ + 20, "add down the\ni column, then\ndown the j\ncolumn. Never\nmix them.", C.INK, 14, w=125)
    step(f, r"\mathbf a+\mathbf b=7\mathbf i+3\mathbf j+\mathbf i-2\mathbf j=8\mathbf i+\mathbf j",
         "i's: 7 + 1,  j's: 3 − 2", size=17)
    a_ = sp.Matrix([7, 3])
    b_ = sp.Matrix([1, -2])
    c_ = sp.Matrix([-3, 1])
    ch.check(a_ + b_, sp.Matrix([8, 1]))
    ch.check(a_ + b_ + c_, sp.Matrix([5, 2]))
    ch.check(c_ + a_ + b_, a_ + b_ + c_)
    ch.term("adding vectors (tip to tail)", "start each vector where the last one ended; the answer runs from the first start to the last end")
    f.p("{b:Subtracting} is adding the {B:reverse}. $-\\mathbf c$ is $\\mathbf c$ turned round: same length, "
        "opposite way, so every sign flips:", 14, gap=8)
    y_ = f.reserve(64)
    pg = f.pg
    vec(pg, (L + 110, y_ + 50), (L + 50, y_ + 30), C.GREEN, 2.2)
    lab(pg, L + 80, y_ + 26, r"\mathbf c", C.GREEN)
    vec(pg, (L + 170, y_ + 30), (L + 230, y_ + 50), C.PINK, 2.2)
    lab(pg, L + 200, y_ + 26, r"-\mathbf c", C.PINK)
    pg.eq(L + 270, y_ + 8, r"\mathbf c=-3\mathbf i+\mathbf j", 15, C.GREEN)
    pg.eq(L + 270, y_ + 34, r"-\mathbf c=3\mathbf i-\mathbf j", 15, C.PINK)
    step(f, r"\mathbf a-\mathbf c=\mathbf a+(-\mathbf c)=7\mathbf i+3\mathbf j+3\mathbf i-\mathbf j=10\mathbf i+2\mathbf j",
         "", size=17)
    ch.check(a_ - c_, sp.Matrix([10, 2]))
    ch.term("negative of a vector", "the same arrow pointing the opposite way: every component changes sign")


def stretch(ch):
    f = flow(ch)
    sec(f, "Stretching, and measuring the length", room=420)
    f.p("Multiply a vector by an ordinary number (a scalar) and you do the trip that many times: "
        "$2\\mathbf a$ is the same direction, {B:twice as long}. A negative number also turns it round.", 14,
        gap=6)
    f.p("{b:How long is the arrow?} The $\\mathbf i$ part and the $\\mathbf j$ part meet at a right angle, so "
        "it's {B:Pythagoras} (Chapter 28). The length is called the {B:magnitude}, written $|\\mathbf a|$.",
        14, gap=10)
    y_ = f.reserve(200)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 6, 4.6 * 28, 6.6 * 28, (0, 4.6), (0, 6.6))
    ax.grid(1, 1)
    ax.axes(None, None, 1, 1, size=9)
    ax.seg(0, 0, 4, 0, C.PURPLE, 1.0, dash=(3, 3))
    ax.seg(4, 0, 4, 6, C.PURPLE, 1.0, dash=(3, 3))
    ax.arrow(0, 0, 4, 6, C.PURPLE, 4.0, head=9)
    ax.seg(2, 0, 2, 3, C.BLUE, 1.2, dash=(3, 3))
    ax.arrow(0, 0, 2, 3, C.BLUE, 2.4, head=7)
    ax.label(0.2, 2.2, "$\\mathbf a$", 13, C.BLUE, dx=0, dy=-8)
    ax.label(2.6, 5.0, "$2\\mathbf a$", 13, C.PURPLE, dx=0, dy=-8)
    ax.label(2.0, 1.5, "{B:3}", 11, C.BLUE, dx=4, dy=-8)
    ax.label(1.0, 0, "{B:2}", 11, C.BLUE, dx=-4, dy=-16)
    xq = L + 185
    pg.eq(xq, y_ + 4, r"|\mathbf a|=\sqrt{2^2+3^2}=\sqrt{13}\approx3.61", 17, C.BLUE)
    pg.eq(xq, y_ + 52, r"|2\mathbf a|=\sqrt{4^2+6^2}=\sqrt{52}\approx7.21", 17, C.PURPLE)
    pg.note(xq + 10, y_ + 92, "= 2 × 3.61: twice the trip, twice the length", C.RED, 15, w=R - xq - 10)
    pg.eq(xq, y_ + 130, r"|\mathbf a|=\sqrt{x^2+y^2+z^2}", 17, C.INK)
    pg.note(xq + 10, y_ + 162, "in 3D add the k part too (Chapter 28's box)", C.GREY, 14, w=R - xq - 10)
    ch.check(sp.sqrt(4 + 9), sp.sqrt(13))
    ch.check(sp.sqrt(16 + 36), 2 * sp.sqrt(13))
    ch.check_num(math.sqrt(13), 3.61, tol=0.006)
    ch.formula(r"|\mathbf a|=\sqrt{x^2+y^2+z^2}", "magnitude (length) of a vector")
    ch.symbol(r"|\mathbf a|", "the magnitude of a", "the length of vector a")
    ch.term("magnitude", "the length of a vector, found by Pythagoras on its components")
    ch.term("scalar multiple", "k times a vector: k times as long, same direction (reversed if k is negative)")


def dot(ch):
    f = flow(ch)
    sec(f, "The dot product: the rope's shadow", room=600)
    f.p("Pull a sled with a rope at an angle. Only the part of your pull {B:along the ground} moves the "
        "sled; the upward part is wasted. The {B:dot product} measures exactly that: how much one vector "
        "pulls in the direction of another.", 14, gap=10)
    y_ = f.reserve(158)
    pg = f.pg
    yg = y_ + 132
    pg.line(L, yg, L + 300, yg, C.BROWN, 1.6)
    pg.rect(L + 50, y_ + 108, 80, 16, C.BROWN, 1.2, fillcolor=C.LIGHT[C.BROWN], r=3)
    pg.poly([(L + 42, yg - 6), (L + 46, yg - 1), (L + 136, yg - 1)], C.INK, 1.4)
    S = (L + 130, y_ + 116)
    th = math.radians(35)
    H = (S[0] + 140 * math.cos(th), S[1] - 140 * math.sin(th))
    vec(pg, S, H, C.RED, 2.6, head=8)
    pg.text((S[0] + H[0]) / 2 - 36, (S[1] + H[1]) / 2 - 18, "F (pull)", 11, C.RED, F.BOLD, solid=False)
    pg.circle(H[0], y_ + 12, 7, C.ORANGE, 1.2, fillcolor=C.YELLOW)
    for k in range(8):
        t = k * math.pi / 4
        pg.line(H[0] + 10 * math.cos(t), y_ + 12 + 10 * math.sin(t), H[0] + 14 * math.cos(t),
                y_ + 12 + 14 * math.sin(t), C.ORANGE, 1.0)
    pg.line(H[0], H[1] + 4, H[0], yg, C.GREY, 1.0, dash=(3, 3))
    vec(pg, (S[0], yg), (H[0], yg), C.GREEN, 3.0, head=7)
    pg.text(S[0], yg + 4, "shadow = |F| cos θ", 11, C.GREEN, F.BOLD, w=H[0] - S[0] + 30, align="center")
    pg.arc(S[0], S[1], 26, 0, 35, C.PURPLE, 1.2)
    pg.text(S[0] + 30, S[1] - 17, "θ", 11, C.PURPLE, F.BOLD)
    pg.note(L + 320, y_ + 8, "the sun is straight overhead.\nThe rope's shadow on the\nground is the "
            "useful part.\n\nwork done =\n|F| cos θ × distance", C.INK, 14, w=R - L - 320)
    f.p("Put the two vectors tail to tail with angle $\\theta$ between them. The dot product is the length "
        "of one times the length of the other's shadow on it:", 14, gap=6)
    step(f, r"\mathbf a\cdot\mathbf b=|\mathbf a|\,|\mathbf b|\cos\theta", "say \"a dot b\"", size=21,
         color=C.BLUE)
    ch.formula(r"\mathbf a\cdot\mathbf b=|\mathbf a||\mathbf b|\cos\theta", "dot product (angle form)")
    ch.symbol(r"\mathbf a\cdot\mathbf b", "a dot b", "the dot (scalar) product: a plain number")
    f.p("The sign tells you whether they help or fight:", 14, gap=10)
    y_ = f.reserve(112)
    pg = f.pg
    for k, (ang, col, txt) in enumerate([(40, C.GREEN, "positive: b helps a\n(angle under 90°)"),
                                         (90, C.GREY, "zero: at right angles,\nno shadow at all"),
                                         (140, C.RED, "negative: the shadow\npoints backwards")]):
        x0, y0 = L + 45 + k * 165, y_ + 60
        t = math.radians(ang)
        tip = (x0 + 55 * math.cos(t), y0 - 55 * math.sin(t))
        if ang != 90:
            pg.line(x0, y0 + 4, tip[0], y0 + 4, col, 4)
        pg.line(tip[0], tip[1], tip[0], y0, C.GREY, 0.8, dash=(3, 3))
        vec(pg, (x0, y0), (x0 + 80, y0), C.BLUE, 2.0, head=6)
        vec(pg, (x0, y0), tip, C.ORANGE, 2.0, head=6)
        lab(pg, x0 + 88, y0 - 4, r"\mathbf a", C.BLUE, 12)
        lab(pg, tip[0] + (8 if ang < 100 else -8), tip[1] - 8, r"\mathbf b", C.ORANGE, 12)
        pg.note(x0 - 30, y0 + 10, txt, col if col != C.GREY else C.INK, 13, w=160)
    ch.term("dot product", "a·b = |a||b| cos θ = axbx + ayby (+ azbz): a scalar measuring how much two vectors point the same way")


def dot_numbers(ch):
    f = flow(ch)
    sec(f, "Dot product with numbers", room=520)
    f.p("With components you don't need the angle at all: {B:pair up} the matching parts, {B:multiply} each "
        "pair, {B:add}. The answer is a single number (a scalar), not an arrow.", 14, gap=10)
    y_ = f.reserve(104)
    pg = f.pg
    cw, chh = 60, 24
    cols = [L + 70, L + 140]
    for r_, (nm, vals, col) in enumerate([("A", ["-6", "7"], C.BLUE), ("B", ["8", "14"], C.ORANGE)]):
        yy = y_ + r_ * 30
        pg.eq(L + 40, yy + 3, r"\mathbf " + nm, 15, col, align="center")
        for cx_, v in zip(cols, vals):
            pg.rect(cx_, yy, cw, chh, col, 1.0, fillcolor=C.LIGHT[col], r=4)
            pg.eq(cx_ + cw / 2, yy + 3, v, 15, align="center")
    for cx_, v in zip(cols, ["-48", "98"]):
        pg.arrow(cx_ + cw / 2, y_ + 56, cx_ + cw / 2, y_ + 70, C.GREY, 1.0, head=4)
        pg.text(cx_ + cw / 2 + 6, y_ + 55, "×", 11, C.GREY, F.BOLD)
        pg.rect(cx_, y_ + 72, cw, chh, C.GREEN, 1.0, fillcolor=C.LIGHT[C.GREEN], r=4)
        pg.eq(cx_ + cw / 2, y_ + 75, v, 15, align="center")
    pg.text(L + 131, y_ + 74, "+", 14, C.INK, F.BOLD, w=10, align="center")
    pg.arrow(L + 206, y_ + 84, L + 236, y_ + 84, C.GREEN, 1.4, head=5)
    pg.rect(L + 242, y_ + 70, 44, 28, C.GREEN, 1.6, r=5)
    pg.eq(L + 264, y_ + 75, "50", 16, C.GREEN, align="center")
    pg.note(L + 320, y_ + 2, "Lecture 10: A = (−6, 7),\nB = (8, 14)\n\npair up → multiply → add\n"
            "= one plain number", C.INK, 14, w=R - L - 320)
    step(f, r"\mathbf A\cdot\mathbf B=(-6)(8)+(7)(14)=-48+98=50", "", size=18, color=C.BLUE)
    ch.formula(r"\mathbf a\cdot\mathbf b=a_xb_x+a_yb_y+a_zb_z", "dot product (components)")
    A_, B_ = sp.Matrix([-6, 7]), sp.Matrix([8, 14])
    ch.check(A_.dot(B_), 50)
    f.p("{b:Now find the angle.} Put the 50 into the angle form and undo the cosine (Chapter 28's "
        "$\\cos^{-1}$):", 14, gap=6)
    step(f, r"|\mathbf A|=\sqrt{36+49}=9.22,\quad|\mathbf B|=\sqrt{64+196}=16.12", "", size=16)
    step(f, r"\cos\theta=\frac{50}{9.22\times16.12}=0.336", "a·b ÷ both lengths", size=17)
    step(f, r"\theta=\cos^{-1}(0.336)=70.3^\circ", "", size=18, color=C.GREEN)
    ch.check_num(math.degrees(math.acos(50 / (math.sqrt(85) * math.sqrt(260)))), 70.35, tol=0.01)
    f.p("{R:Slide slip:} Lecture 10 uses $\\theta = 60^\\circ$ here, but $9.22\\times16.12\\times\\cos60^\\circ "
        "= 74.3$, not 50. The true angle is 70.3°.", 13.5, gap=10)
    ch.check_num(math.sqrt(85) * math.sqrt(260) * 0.5, 74.33, tol=0.01)
    f.p("{b:Lecture 10's second example:} $\\mathbf A = (2, 3)$, $\\mathbf B = (-1, 5)$.", 14, gap=6)
    step(f, r"\mathbf A\cdot\mathbf B=2\times(-1)+3\times5=-2+15=13", "", size=17)
    step(f, r"\theta=\cos^{-1}\frac{13}{\sqrt{13}\,\sqrt{26}}=\cos^{-1}\frac{13}{3.6\times5.1}=\cos^{-1}(0.707)=45^\circ",
         "", size=16, color=C.GREEN)
    ch.check(sp.Matrix([2, 3]).dot(sp.Matrix([-1, 5])), 13)
    ch.check(sp.acos(13 / (sp.sqrt(13) * sp.sqrt(26))), sp.pi / 4)
    f.p("{b:The right-angle test.} At 90° the shadow vanishes ($\\cos 90^\\circ = 0$), so {B:perpendicular "
        "vectors have dot product 0}. Lecture 10: $\\mathbf a = 2\\mathbf i+0\\mathbf j$ (along $x$), "
        "$\\mathbf b = 0\\mathbf i+1\\mathbf j$ (along $y$): $2\\times0+0\\times1 = 0$.", 14, gap=8)
    ch.term("perpendicular vectors", "vectors at right angles; their dot product is 0")
    f.p("{b:Where it turns up:} work = force · displacement (the sled), power = force · velocity, and a "
        "solar panel's energy depends on the dot product of the sun's rays with the panel's direction.", 14)


def cross(ch):
    f = flow(ch)
    sec(f, "The cross product: a screwdriver", room=600)
    f.p("The {B:cross product} $\\mathbf a\\times\\mathbf b$ multiplies two vectors and gives a new "
        "{B:vector}, pointing at right angles to both of them. Think of a screwdriver: you turn the handle "
        "in a flat circle (that's where $\\mathbf a$ and $\\mathbf b$ live), and the screw moves straight "
        "in or out of the wood (that's the answer).", 14, gap=10)
    y_ = f.reserve(165)
    pg = f.pg
    pg.rect(L + 20, y_ + 120, 180, 26, C.BROWN, 1.2, fillcolor=C.LIGHT[C.BROWN])
    for k in range(3):
        pg.line(L + 30 + k * 50, y_ + 128 + k * 4, L + 70 + k * 50, y_ + 130 + k * 4, C.BROWN, 0.6)
    pg.line(L + 110, y_ + 60, L + 110, y_ + 134, C.GREY, 3)
    pg.rect(L + 96, y_ + 14, 28, 46, C.ORANGE, 1.2, fillcolor=C.LIGHT[C.ORANGE], r=6)
    pg.ellipse(L + 110, y_ + 38, 42, 10, C.PURPLE, 1.3)
    pg.arrow(L + 118, y_ + 48, L + 124, y_ + 47.5, C.PURPLE, 1.3, head=6)
    pg.note(L + 158, y_ + 6, "turn in the\nflat plane", C.PURPLE, 13)
    vec(pg, (L + 150, y_ + 70), (L + 150, y_ + 114), C.PURPLE, 2.4)
    pg.note(L + 158, y_ + 78, "screw goes in:\na × b", C.PURPLE, 13)
    O = (L + 330, y_ + 120)
    vec(pg, O, (O[0] + 115, O[1]), C.BLUE, 2.4)
    pg.text(O[0] + 30, O[1] + 5, "a: first finger", 11, C.BLUE, F.BOLD)
    vec(pg, O, (O[0] + 70, O[1] - 50), C.GREEN, 2.4)
    pg.text(O[0] + 74, O[1] - 66, "b: second finger", 11, C.GREEN, F.BOLD)
    vec(pg, O, (O[0], y_ + 18), C.PURPLE, 2.8, head=8)
    pg.text(O[0] + 8, y_ + 10, "a × b: thumb", 11, C.PURPLE, F.BOLD)
    pg.line(O[0], O[1], O[0], y_ + 160, C.PURPLE, 1.4, dash=(4, 3))
    pg.text(O[0] + 8, y_ + 144, "b × a points the other way", 10, C.PURPLE)
    pg.rect(O[0], O[1] - 9, 9, 9, C.GREY, 0.8)
    f.p("{b:Right-hand rule} (Lecture 10): point your right hand's first finger along $\\mathbf a$ and "
        "your second finger along $\\mathbf b$; your thumb points along $\\mathbf a\\times\\mathbf b$. Swap "
        "the order and the thumb flips: $\\mathbf b\\times\\mathbf a = -\\,\\mathbf a\\times\\mathbf b$. "
        "(Left-handers: use your right hand anyway!)", 14, gap=8)
    ch.term("cross product", "a×b: a vector at right angles to a and b, of length |a||b| sin θ")
    ch.term("right-hand rule", "first finger along a, second finger along b, thumb gives the direction of a×b")
    ch.symbol(r"\mathbf a\times\mathbf b", "a cross b", "the cross (vector) product")
    f.p("{b:How long is it?} $|\\mathbf a\\times\\mathbf b| = |\\mathbf a|\\,|\\mathbf b|\\sin\\theta$, "
        "which is exactly the {B:area of the parallelogram} the two arrows make. Lecture 10: "
        "$\\mathbf a = (2, 3)$, $\\mathbf b = (1, 4)$.", 14, gap=10)
    ch.formula(r"|\mathbf a\times\mathbf b|=|\mathbf a||\mathbf b|\sin\theta", "size of the cross product")
    y_ = f.reserve(182)
    pg = f.pg
    ax = Axes(pg, L + 22, y_ + 4, 3.4 * 22, 7.3 * 22, (0, 3.4), (0, 7.3))
    ax.grid(1, 1)
    ax.axes(None, None, 0, 0)
    pg.fillpoly([ax.P(0, 0), ax.P(2, 3), ax.P(3, 7), ax.P(1, 4)], C.LIGHT[C.ORANGE])
    ax.seg(2, 3, 3, 7, C.GREY, 1.0, dash=(3, 3))
    ax.seg(1, 4, 3, 7, C.GREY, 1.0, dash=(3, 3))
    ax.arrow(0, 0, 2, 3, C.BLUE, 2.2, head=6)
    ax.arrow(0, 0, 1, 4, C.GREEN, 2.2, head=6)
    ax.label(2.1, 2.4, "$\\mathbf a$", 12, C.BLUE, dx=0, dy=-4)
    ax.label(0.1, 3.4, "$\\mathbf b$", 12, C.GREEN, dx=-14, dy=-4)
    ax.label(1.4, 4.1, "{O:5}", 12, C.ORANGE, dx=0, dy=-8)
    xq = L + 130
    pg.eq(xq, y_ + 2, r"|\mathbf a|\,|\mathbf b|=\sqrt{13}\,\sqrt{17}=14.87", 15)
    pg.eq(xq, y_ + 40, r"\mathbf a\cdot\mathbf b=2\times1+3\times4=14", 15)
    pg.eq(xq, y_ + 72, r"\theta=\cos^{-1}\frac{14}{14.87}=19.65^\circ", 15)
    pg.eq(xq, y_ + 112, r"|\mathbf a\times\mathbf b|=14.87\sin19.65^\circ=5.00", 15, C.GREEN)
    pg.note(xq + 10, y_ + 140, "shortcut in 2D: 2×4 − 3×1 = 5 (Chapter 16's ad − bc)", C.RED, 14, w=R - xq - 10)
    ch.check_num(math.sqrt(13 * 17), 14.87, tol=0.006)
    ch.check_num(math.degrees(math.acos(14 / math.sqrt(221))), 19.65, tol=0.006)
    ch.check_num(math.sqrt(221) * math.sin(math.acos(14 / math.sqrt(221))), 5.0, tol=0.001)
    f.gap(6)
    f.p("{R:Slide slip:} Lecture 10's answer is 11.18, but $14.87\\sin19.7^\\circ = 5.0$. The parallelogram "
        "really has area 5.", 13.5, gap=10)
    f.p("{b:Where it turns up:} turning a screwdriver or spanner (turning force in the flat plane, "
        "movement along the axis), and the force on a wire carrying current in a magnetic field.", 14)


def det3(ch):
    f = flow(ch)
    sec(f, "The 3 × 3 determinant: cover up and work out", room=560)
    f.p("In 3D, the cross product has a recipe using a 3 × 3 {B:determinant} (Chapter 16 did the 2 × 2 "
        "kind: $ad - bc$). Put $\\mathbf i, \\mathbf j, \\mathbf k$ along the top, then the two vectors. "
        "Lecture 10: $\\mathbf a = 3\\mathbf i+4\\mathbf j+7\\mathbf k$, $\\mathbf b = 4\\mathbf i+9\\mathbf j+2\\mathbf k$.",
        14, gap=6)
    step(f, r"\mathbf a\times\mathbf b=\begin{vmatrix}\mathbf i&\mathbf j&\mathbf k\\3&4&7\\4&9&2\end{vmatrix}",
         "top row: letters\nrow 2: a\nrow 3: b", size=19)
    f.p("{b:The cover-up method.} For each letter on the top row, cover its row and its column with "
        "your fingers, and work out the little 2 × 2 that's left ({g:down-right diagonal} minus "
        "{r:up-right diagonal}). The signs go {B:+  −  +}.", 14, gap=10)
    y_ = f.reserve(168)
    pg = f.pg
    M = [[r"\mathbf i", r"\mathbf j", r"\mathbf k"], ["3", "4", "7"], ["4", "9", "2"]]
    calc = [(r"+\mathbf i\,(4\times2-7\times9)", r"=-55\,\mathbf i"),
            (r"-\mathbf j\,(3\times2-7\times4)", r"=-(-22)\,\mathbf j=+22\,\mathbf j"),
            (r"+\mathbf k\,(3\times9-4\times4)", r"=+11\,\mathbf k")]
    for k in range(3):
        x0 = L + k * 168
        cxs = [x0 + 38 + c * 38 for c in range(3)]
        cys = [y_ + 30 + r_ * 26 for r_ in range(3)]
        pg.circle(cxs[k], y_ + 10, 9, C.BLUE, 1.2)
        pg.text(cxs[k] - 6, y_ + 2, "+−+"[k], 12, C.BLUE, F.BOLD, w=12, align="center")
        pg.fillpoly([(x0 + 20, y_ + 26), (x0 + 132, y_ + 26), (x0 + 132, y_ + 50), (x0 + 20, y_ + 50)], C.GREY, 70)
        pg.fillpoly([(cxs[k] - 16, y_ + 50), (cxs[k] + 16, y_ + 50), (cxs[k] + 16, y_ + 102),
                     (cxs[k] - 16, y_ + 102)], C.GREY, 70)
        pg.line(x0 + 18, y_ + 26, x0 + 18, y_ + 102, C.INK, 1.2)
        pg.line(x0 + 134, y_ + 26, x0 + 134, y_ + 102, C.INK, 1.2)
        rest = [c for c in range(3) if c != k]
        c1, c2 = rest
        pg.line(cxs[c1] + 7, cys[1] + 14, cxs[c2] - 7, cys[2] + 6, C.GREEN, 1.0)
        pg.line(cxs[c1] + 7, cys[2] + 6, cxs[c2] - 7, cys[1] + 14, C.RED, 1.0)
        for r_ in range(3):
            for c in range(3):
                covered = r_ == 0 or c == k
                col = C.BLUE if (r_ == 0 and c == k) else (C.GREY if covered else C.INK)
                pg.eq(cxs[c], cys[r_], M[r_][c], 15, col, align="center")
        pg.eq(x0 + 8, y_ + 112, calc[k][0], 13, C.INK)
        pg.eq(x0 + 8, y_ + 140, calc[k][1], 13, C.GREEN)
    step(f, r"\mathbf a\times\mathbf b=-55\,\mathbf i+22\,\mathbf j+11\,\mathbf k", "", size=20, color=C.GREEN)
    a_, b_ = sp.Matrix([3, 4, 7]), sp.Matrix([4, 9, 2])
    ch.check(a_.cross(b_), sp.Matrix([-55, 22, 11]))
    f.p("{b:Check it!} The answer must be at right angles to {B:both} $\\mathbf a$ and $\\mathbf b$, so both "
        "dot products must be 0:", 14, gap=6)
    step(f, r"(-55)(3)+(22)(4)+(11)(7)=-165+88+77=0", "✓ perpendicular to a", size=16)
    step(f, r"(-55)(4)+(22)(9)+(11)(2)=-220+198+22=0", "✓ perpendicular to b", size=16)
    ch.check(a_.cross(b_).dot(a_), 0)
    ch.check(a_.cross(b_).dot(b_), 0)
    f.p("{R:Slide slip:} Lecture 10's final answer says $-11\\mathbf k$, but the $\\mathbf k$ part is "
        "$+(3\\times9-4\\times4) = +11$. The check catches it: with $-11\\mathbf k$ the first dot product "
        "comes out as $-154$, not 0.", 13.5, gap=10)
    ch.check(-165 + 88 - 77, -154)
    f.p("The general recipe, if you prefer letters:", 14, gap=6)
    step(f, r"\mathbf a\times\mathbf b=\mathbf i(a_yb_z-a_zb_y)-\mathbf j(a_xb_z-a_zb_x)+\mathbf k(a_xb_y-a_yb_x)",
         "", size=15)
    ch.formula(r"\mathbf a\times\mathbf b=\mathbf i(a_yb_z-a_zb_y)-\mathbf j(a_xb_z-a_zb_x)+\mathbf k(a_xb_y-a_yb_x)",
               "cross product (components)")
    ch.term("3 × 3 determinant", "cover each top-row entry's row and column, take the 2 × 2 determinant left over, and combine with signs + − +")


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Sketch every vector on squared paper first. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Trips, adding, lengths", ["p = 3i − 2j and q = −i + 5j. Find p + q and p − q.",
                                    "Find |p|, exactly and to 2 d.p.", "Find 3q and its length."],
         "1. 2i + 3j;  4i − 7j   2. √13 ≈ 3.61   3. −3i + 15j;  √234 ≈ 15.30"),
        ("Dot product", ["(4, 1) · (2, −3)", "The angle between (1, 2) and (3, 1)",
                         "Are 2i + 3j and 6i − 4j perpendicular?"],
         "4. 8 − 3 = 5   5. cos⁻¹(5 ÷ (√5 × √10)) = 45°   6. yes: 12 − 12 = 0"),
        ("Cross product", ["Area of the parallelogram made by (3, 1) and (1, 2)",
                           "(1, 2, 0) × (0, 1, 3) by the cover-up method",
                           "Check your answer to 8 with two dot products."],
         "7. 3×2 − 1×1 = 5   8. 6i − 3j + k   9. 6 − 6 + 0 = 0 and 0 − 3 + 3 = 0"),
        ("Distance or displacement?", ["A bus drives 3 km east then 4 km north. Distance travelled? "
                                       "Size of the displacement?"],
         "10. 7 km;  √(9 + 16) = 5 km"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    p, q = sp.Matrix([3, -2]), sp.Matrix([-1, 5])
    ch.check(p + q, sp.Matrix([2, 3]))
    ch.check(p - q, sp.Matrix([4, -7]))
    ch.check(p.norm(), sp.sqrt(13))
    ch.check((3 * q).norm(), sp.sqrt(234))
    ch.check_num(math.sqrt(234), 15.30, tol=0.006)
    ch.check(sp.Matrix([4, 1]).dot(sp.Matrix([2, -3])), 5)
    ch.check(sp.acos(5 / (sp.sqrt(5) * sp.sqrt(10))), sp.pi / 4)
    ch.check(sp.Matrix([2, 3]).dot(sp.Matrix([6, -4])), 0)
    ch.check(3 * 2 - 1 * 1, 5)
    u, v = sp.Matrix([1, 2, 0]), sp.Matrix([0, 1, 3])
    ch.check(u.cross(v), sp.Matrix([6, -3, 1]))
    ch.check([u.cross(v).dot(u), u.cross(v).dot(v)], [0, 0])
    ch.check(sp.sqrt(9 + 16), 5)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    scalars(ch)
    notation(ch)
    unit_vectors(ch)
    adding(ch)
    stretch(ch)
    dot(ch)
    dot_numbers(ch)
    cross(ch)
    det3(ch)
    your_turn(ch)
