"""Chapter 31 - Solution of triangles (Lecture 6, last part). Triangles without a right angle: names and
the angle sum (tear the corners off), the sine rule found by dropping a height, measuring a river you
can't cross, the cosine rule as 'Pythagoras plus a correction', the lecture's clock hands, a
'what do I know?' decision map, and the area formula."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, flow, go, mistakes, rule_box, rules_page, rules_table, section, step,
                         title_block)

ORDER = 31
NUM = 31
TITLE = "Solving any triangle"
SHORT = "Triangles"
SLUG = "Triangles"
ACCENT = C.GREEN
REQUIRES = ["sine", "cosine", "inverse-trig", "pythagoras", "angle", "degrees", "transpose", "right-angle",
            "hypotenuse", "opposite-adjacent", "cross-multiply", "angle-types", "perimeter", "area", "sohcahtoa",
            "trig-any-angle"]
INTRODUCES = ["triangle-types", "triangle-notation", "angle-sum", "sine-rule", "cosine-rule", "ambiguous-case",
              "triangle-area-sine"]

PAPER = "#f9fdf8"
D = math.radians


def icon(pg, x0, y0):
    pg.poly([(x0 + 1, y0 + 17), (x0 + 17, y0 + 17), (x0 + 6, y0 + 2)], C.GREEN, 1.6, closed=True)


def sec(f, t_, **kw):
    section(f, t_, C.GREEN, icon, **kw)


def triangle(pg, pts, labels_v=None, labels_s=None, fill=None, col=C.INK, size=12):
    """pts = [A, B, C]. labels_v: names at vertices; labels_s: labels of the side opposite each vertex."""
    if fill:
        pg.fillpoly(pts, fill)
    pg.poly(pts, col, 1.6, closed=True)
    cx = sum(p[0] for p in pts) / 3
    cy = sum(p[1] for p in pts) / 3
    if labels_v:
        for (x, y), s_ in zip(pts, labels_v):
            dx, dy = x - cx, y - cy
            n = math.hypot(dx, dy) or 1
            pg.text(x + dx / n * 14, y + dy / n * 14 - 7, s_, size, C.RED, F.BOLD, align="center", solid=False)
    if labels_s:
        for i, s_ in enumerate(labels_s):
            p, q = pts[(i + 1) % 3], pts[(i + 2) % 3]
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            dx, dy = mx - cx, my - cy
            n = math.hypot(dx, dy) or 1
            pg.text(mx + dx / n * 14, my + dy / n * 14 - 7, s_, size, C.BLUE, F.BOLD, align="center", solid=False)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 31, "Solving any triangle", "measure a river without getting wet", C.GREEN, PAPER)
    pg.fillpoly([(L, 250), (L + W, 235), (L + W, 290), (L, 305)], C.LIGHT[C.BLUE])
    for k in range(6):
        pg.poly([(L + 20 + k * 80 + i * 6, 272 - k * 2 + 3 * math.sin(i)) for i in range(8)], C.BLUE, 0.8)
    A_, B_, T_ = (L + 120, 330), (L + 300, 330), (L + 190, 215)
    pg.poly([A_, B_, T_], C.GREEN, 1.6, closed=True)
    for (x, y) in (A_, B_):
        pg.circle(x, y + 2, 5, C.INK, 1.2, fillcolor=C.ORANGE)
    pg.circle(T_[0], T_[1] - 10, 10, C.GREEN, 1.2, fillcolor=C.LIGHT[C.GREEN])
    pg.line(T_[0], T_[1], T_[0], T_[1] - 2, C.BROWN, 3)
    pg.note(L + 330, 310, "two friends 50 m apart, one tree across\nthe river. Two angles and a sine rule\n"
            "give the width.", C.GREEN, 14)
    f = ch.flow(top=380)
    f.p("SOHCAHTOA only works when there's a right angle. Real triangles (plots of land, roof trusses, "
        "navigation) usually don't have one. This chapter gives you two tools that work on {B:any} "
        "triangle: the {B:sine rule} and the {B:cosine rule}, plus a map for choosing between them.",
        14, gap=10)
    f.p("{y:Goes with} {B:Lecture 6} {y:(triangle types and notation, sine rule, cosine rule, the clock "
        "example, answering questions).}", 12.5)


def names(ch):
    f = flow(ch)
    sec(f, "Names, and the 180° rule")
    rule_box(f, "triangle notation and the angle sum", [
        "Angles are capital letters $A, B, C$; the side {B:opposite} each angle is the same letter in lower "
        "case: side $a$ faces angle $A$.",
        "The three angles add up to $180^\\circ$: $A+B+C=180^\\circ$. Two angles always give the third.",
        "The biggest angle faces the longest side; the smallest angle faces the shortest side.",
    ], C.GREEN)
    f.p("Lecture 6's labelling: {B:capital letters for the angles} (at the corners) and the {B:same "
        "letter in lower case for the side opposite}. Side $a$ faces angle $A$:", 14, gap=12)
    y_ = f.reserve(140)
    pg = f.pg
    pts = [(L + 30, y_ + 120), (L + 250, y_ + 120), (L + 90, y_ + 15)]
    triangle(pg, pts, ["A", "B", "C"], ["a", "b", "c"], fill=C.LIGHT[C.GREEN])
    pg.note(L + 290, y_ + 10, "a is opposite A,\nb is opposite B,\nc is opposite C.\n\nBigger angle ↔ "
            "longer side\nopposite it.", C.INK, 15)
    ch.term("triangle notation", "angles A, B, C at the corners; sides a, b, c opposite them")
    f.p("{b:Three kinds} (Lecture 6): {B:scalene} (all sides different, from Greek \"unequal\"), "
        "{B:isosceles} (two equal sides: \"equal legs\") and {B:equilateral} (all three equal, so all "
        "angles 60°).", 14, gap=10)
    y_ = f.reserve(90)
    pg = f.pg
    for k, (pts, nm) in enumerate([([(0, 70), (120, 70), (30, 0)], "scalene"),
                                   ([(0, 70), (90, 70), (45, 0)], "isosceles"),
                                   ([(0, 70), (80, 70), (40, 70 - 69.3)], "equilateral")]):
        x0 = L + 20 + k * 165
        P_ = [(x0 + a, y_ + b) for a, b in pts]
        pg.fillpoly(P_, C.LIGHT[C.GREEN])
        pg.poly(P_, C.INK, 1.4, closed=True)
        pg.text(x0 + 50, y_ + 74, nm, 11, C.GREEN, F.BOLD, align="center")
    ch.term("scalene / isosceles / equilateral", "no equal sides / two equal sides / all three sides equal")
    f.p("{b:Angles in a triangle add up to 180°.} Tear the three corners off a paper triangle and line "
        "them up: they always make a straight line. So two angles always give you the third.", 14)
    ch.term("angle sum of a triangle", "the three angles of any triangle add up to 180°")


def sine_rule(ch):
    f = flow(ch)
    sec(f, "The sine rule: drop a height", room=560)
    rule_box(f, "the sine rule", [
        "In {B:any} triangle: $\\dfrac{a}{\\sin A}=\\dfrac{b}{\\sin B}=\\dfrac{c}{\\sin C}$. Each side over the sine "
        "of the angle {B:opposite} it.",
        "To find an {B:angle}, flip it: $\\dfrac{\\sin A}{a}=\\dfrac{\\sin B}{b}$ (the unknown goes on top).",
        "Use it when you know a {B:matching pair} (a side and the angle opposite it) plus one more side or "
        "angle. Use only the two fractions you need.",
    ], C.GREEN)
    f.p("Where does it come from? Drop a line straight down from C to the base, height $h$. That splits "
        "the triangle into {B:two right-angled triangles}, where SOHCAHTOA works again:", 14, gap=12)
    y_ = f.reserve(150)
    pg = f.pg
    A_, B_, C_ = (L + 30, y_ + 130), (L + 280, y_ + 130), (L + 110, y_ + 20)
    triangle(pg, [A_, B_, C_], None, None, fill=C.LIGHT[C.GREEN])
    pg.line(C_[0], C_[1], C_[0], A_[1], C.PURPLE, 1.6, dash=(4, 3))
    pg.rect(C_[0], A_[1] - 8, 8, 8, C.PURPLE, 0.8)
    pg.text(C_[0] + 4, (C_[1] + A_[1]) / 2 - 6, "h", 12, C.PURPLE, F.BOLD)
    pg.text((A_[0] + C_[0]) / 2 - 16, (A_[1] + C_[1]) / 2 - 12, "b", 12, C.BLUE, F.BOLD)
    pg.text((B_[0] + C_[0]) / 2 + 6, (B_[1] + C_[1]) / 2 - 10, "a", 12, C.BLUE, F.BOLD)
    for (x, y), s_ in [(A_, "A"), (B_, "B"), (C_, "C")]:
        pg.text(x + (-12 if s_ == "A" else 8 if s_ == "B" else -4), y + (-4 if s_ != "C" else -18), s_, 12, C.RED,
                F.BOLD)
    pg.note(L + 310, y_ + 10, "left triangle: sin A = h / b\n   so h = b sin A\n\nright triangle: sin B = h / a\n"
            "   so h = a sin B", C.INK, 15)
    f.p("Both expressions are the same height, so", 14, gap=6)
    step(f, r"b\sin A=a\sin B", "", size=19)
    step(f, r"\frac{a}{\sin A}=\frac{b}{\sin B}", "÷ both sides by sin A sin B", size=19)
    f.p("Dropping the height from a different corner brings in $c$ the same way. The {B:sine rule}:", 14, gap=6)
    step(f, r"\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}", "each side ÷ the sine of its opposite angle",
         size=21, color=C.GREEN)
    ch.formula(r"\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}", "sine rule")
    ch.term("sine rule", "a/sin A = b/sin B = c/sin C: use it when you know a side and its opposite angle")
    a_, A_s, B_s = sp.symbols("a A B", positive=True)
    ch.check(sp.simplify((a_ * sp.sin(B_s) / sp.sin(A_s)) * sp.sin(A_s) - a_ * sp.sin(B_s)), 0)
    f.p("{b:When to use it:} you know a {B:matching pair} (a side and the angle opposite it) plus one more "
        "fact. Use only the two fractions you need.", 14)


def river(ch):
    f = flow(ch)
    sec(f, "Measuring the river", room=560)
    f.p("Ana (A) and Ben (B) stand 50 m apart on one bank. Each measures the angle between the bank and "
        "a tree T on the far side: 62° at A, 48° at B. How wide is the river?", 14, gap=12)
    y_ = f.reserve(186)
    pg = f.pg
    A_, B_ = (L + 100, y_ + 160), (L + 300, y_ + 160)
    tA, tB = D(62), D(48)
    AT = 200 * math.sin(tB) / math.sin(math.pi - tA - tB)
    T_ = (A_[0] + AT * math.cos(tA), A_[1] - AT * math.sin(tA))
    pg.fillpoly([(L, y_ + 22), (L + W, y_ + 22), (L + W, y_ + 150), (L, y_ + 150)], C.LIGHT[C.BLUE])
    triangle(pg, [A_, B_, T_], None, None)
    pg.line(T_[0], T_[1], T_[0], A_[1], C.PURPLE, 1.6, dash=(4, 3))
    pg.text(T_[0] + 4, (T_[1] + A_[1]) / 2, "width w", 11, C.PURPLE, F.BOLD)
    pg.arc(A_[0], A_[1], 24, 0, 62, C.RED, 1.3)
    pg.text(A_[0] + 28, A_[1] - 22, "62°", 10, C.RED, F.BOLD)
    pg.arc(B_[0], B_[1], 24, 132, 180, C.RED, 1.3)
    pg.text(B_[0] - 50, B_[1] - 22, "48°", 10, C.RED, F.BOLD)
    pg.text(T_[0] - 8, T_[1] + 22, "70°", 10, C.RED, F.BOLD)
    pg.text((A_[0] + B_[0]) / 2, A_[1] + 4, "50 m", 11, C.INK, F.BOLD, align="center")
    for (x, y), s_ in [(A_, "A"), (B_, "B"), (T_, "T")]:
        pg.text(x - 4, y + (4 if s_ != "T" else -20), s_, 12, C.INK, F.BOLD)
    labels = [(r"T=180^\circ-62^\circ-48^\circ=70^\circ", "angle sum: now 50 m faces a known angle"),
              (r"\frac{AT}{\sin48^\circ}=\frac{50}{\sin70^\circ}", "sine rule: AT faces B, 50 faces T"),
              (r"AT=\frac{50\sin48^\circ}{\sin70^\circ}=39.54\text{ m}", "× sin 48°"),
              (r"w=AT\sin62^\circ=34.9\text{ m}", "SOH in the right triangle at A")]
    for lat, why in labels:
        step(f, lat, why, size=17, color=C.GREEN if lat.startswith("w") else C.INK)
    AT_m = 50 * math.sin(tB) / math.sin(D(70))
    ch.check_num(AT_m, 39.54, tol=0.005)
    ch.check_num(AT_m * math.sin(tA), 34.91, tol=0.01)
    f.p("{b:Lecture 6's example:} $a = 17$, $b = 2$, $A = 24^\\circ$. Find $B$:", 14, gap=6)
    step(f, r"\frac{17}{\sin24^\circ}=\frac{2}{\sin B}\ \Rightarrow\ \sin B=\frac{2\sin24^\circ}{17}", "", size=16)
    step(f, r"B=\sin^{-1}\!\left(\frac{2\sin24^\circ}{17}\right)=2.743^\circ", "", size=16, color=C.GREEN)
    ch.check_num(math.degrees(math.asin(2 * math.sin(D(24)) / 17)), 2.743, tol=0.001)


def cosine_rule(ch):
    f = flow(ch)
    sec(f, "The cosine rule: Pythagoras plus a correction", room=560)
    rule_box(f, "the cosine rule (all three forms)", [
        "$a^2=b^2+c^2-2bc\\cos A$",
        "$b^2=a^2+c^2-2ac\\cos B$",
        "$c^2=a^2+b^2-2ab\\cos C$",
        "{B:Pattern}: the side on the left is {B:opposite the angle} in the cosine; the other two sides appear "
        "squared and in the $2\\times\\dots$ term.",
        "{B:Angle form} (rearranged): $\\cos A=\\dfrac{b^2+c^2-a^2}{2bc}$, $\\cos B=\\dfrac{a^2+c^2-b^2}{2ac}$, "
        "$\\cos C=\\dfrac{a^2+b^2-c^2}{2ab}$.",
        "Use it with {B:two sides and the angle between them} (find the third side) or {B:all three sides} "
        "(find an angle).",
    ], C.GREEN)
    ch.formula(r"\cos A=\frac{b^2+c^2-a^2}{2bc}", "cosine rule (angle form)")
    f.p("If you know {B:two sides and the angle between them}, there's no matching pair, so the sine "
        "rule is stuck. The {B:cosine rule} takes over:", 14, gap=6)
    step(f, r"a^2=b^2+c^2-2bc\cos A", "", size=22, color=C.GREEN)
    ch.formula(r"a^2=b^2+c^2-2bc\cos A", "cosine rule")
    bb, cc, AA = sp.symbols("b c A", positive=True)
    aa2 = bb ** 2 + cc ** 2 - 2 * bb * cc * sp.cos(AA)
    ch.check(sp.simplify((bb ** 2 + cc ** 2 - aa2) / (2 * bb * cc) - sp.cos(AA)), 0)
    ch.term("cosine rule", "a² = b² + c² − 2bc cos A: use it with two sides and the angle between, or with all three sides")
    f.p("Look closely: it's {B:Pythagoras} ($a^2 = b^2 + c^2$) with a correction term. The correction "
        "depends on how far A is from 90°:", 14, gap=10)
    y_ = f.reserve(120)
    pg = f.pg
    for k, (ang, nm, why) in enumerate([(60, "A < 90°", "cos A > 0: subtract,\na is shorter"),
                                        (90, "A = 90°", "cos A = 0: plain\nPythagoras"),
                                        (125, "A > 90°", "cos A < 0: add,\na is longer")]):
        x0, y0 = L + 30 + k * 165, y_ + 80
        b_, c_ = 70, 90
        Bp = (x0 + c_, y0)
        Cp = (x0 + b_ * math.cos(D(ang)), y0 - b_ * math.sin(D(ang)))
        pg.fillpoly([(x0, y0), Bp, Cp], C.LIGHT[C.GREEN])
        pg.poly([(x0, y0), Bp, Cp], C.INK, 1.3, closed=True)
        pg.line(Bp[0], Bp[1], Cp[0], Cp[1], C.RED, 2.4)
        pg.arc(x0, y0, 14, 0, ang, C.PURPLE, 1.2)
        pg.text(x0 + 30, y0 + 4, nm, 10, C.PURPLE, F.BOLD)
        pg.note(x0 - 10, y0 + 18, why, C.GREY, 12)
    f.gap(10)
    f.p("{b:Lecture 6's clock:} hands 10 cm and 7 cm long. How far apart are the tips at 2 o'clock?", 14,
        gap=6)
    step(f, r"A=\tfrac{2}{12}\times360^\circ=60^\circ", "the angle between the hands (Chapter 27)", size=18)
    step(f, r"a^2=10^2+7^2-2\times10\times7\cos60^\circ", "", size=18)
    step(f, r"a^2=100+49-140\times0.5=79", "", size=18)
    step(f, r"a=\sqrt{79}=8.89\text{ cm}", "", size=19, color=C.GREEN)
    ch.check_num(math.sqrt(100 + 49 - 140 * 0.5), 8.888, tol=0.001)
    f.p("{b:Same rule, other letters:} $a = 8$, $c = 5$, $B = 110^\\circ$. Find $b$ (it faces $B$, so use the "
        "$b^2$ form):", 14, gap=6)
    step(f, r"b^2=8^2+5^2-2\times8\times5\cos110^\circ=89+27.36=116.36", "cos 110° < 0: the term is added",
         size=16)
    step(f, r"b=\sqrt{116.36}=10.79", "", size=19, color=C.GREEN)
    ch.check_num(89 - 80 * math.cos(D(110)), 116.36, tol=0.005)
    ch.check_num(math.sqrt(89 - 80 * math.cos(D(110))), 10.79, tol=0.005)
    f.p("{b:Finding an angle} from three sides: rearrange the rule (Chapter 14) to", 14, gap=6)
    step(f, r"\cos A=\frac{b^2+c^2-a^2}{2bc}", "", size=19, color=C.GREEN)
    step(f, r"\text{sides }5,6,7:\ \cos C=\frac{25+36-49}{2\times5\times6}=0.2,\ C=78.46^\circ",
         "C faces the 7", size=15)
    ch.check_num(math.degrees(math.acos(0.2)), 78.46, tol=0.005)


def decide(ch):
    f = flow(ch)
    sec(f, "Which rule? Ask \"what do I know?\"", room=460)
    rule_box(f, "sine rule or cosine rule?", [
        "Right angle in the triangle → SOHCAHTOA and Pythagoras (Chapter 28).",
        "Know a side {B:and the angle opposite it} (a matching pair) → {B:sine rule}.",
        "Know two sides and the angle {B:between} them (SAS), or {B:all three sides} (SSS) → {B:cosine rule}.",
    ], C.GREEN)
    rules_table(f, ["You know", "Use", "Then"], [
        ["two angles + any side (AAS / ASA)", "sine rule", "third angle $=180^\\circ-$ the other two, first"],
        ["two sides + an angle opposite one of them (SSA)", "sine rule (for an angle)",
         "check the {R:ambiguous case} (below)"],
        ["two sides + the angle between them (SAS)", "cosine rule", "third side; then the sine rule for an angle"],
        ["three sides (SSS)", "cosine rule, angle form", "find the {B:largest} angle first"],
        ["three angles only", "can't be solved", "only the shape is fixed, not the size"],
    ], [200, 130, 165], C.GREEN, size=11.5)
    f.p("Lecture 6's advice: {B:first draw the triangle and fill in everything you know}. Then:", 14, gap=12)
    y_ = f.reserve(260)
    pg = f.pg

    def box(x, y, s, col, w_=150, h_=36):
        pg.rect(x - w_ / 2, y, w_, h_, col, 1.3, fillcolor=C.LIGHT[col], r=8)
        pg.text(x - w_ / 2 + 4, y + 5, s, 10.5, C.INK, F.BOLD, align="center", w=w_ - 8)

    cx = L + W / 2
    box(cx, y_, "Is there a right angle?", C.GREY, 190, 30)
    box(L + 70, y_ + 70, "yes: SOHCAHTOA and Pythagoras (Ch. 28)", C.TEAL, 140, 44)
    pg.arrow(cx - 60, y_ + 30, L + 90, y_ + 70, C.GREY, 1.1, head=5)
    box(L + 330, y_ + 60, "no: do I know a side AND its opposite angle?", C.GREY, 200, 44)
    pg.arrow(cx + 40, y_ + 30, L + 320, y_ + 60, C.GREY, 1.1, head=5)
    box(L + 230, y_ + 150, "yes: SINE RULE", C.GREEN, 150, 30)
    box(L + 420, y_ + 150, "no: COSINE RULE", C.ORANGE, 150, 30)
    pg.arrow(L + 300, y_ + 104, L + 240, y_ + 150, C.GREY, 1.1, head=5)
    pg.arrow(L + 360, y_ + 104, L + 410, y_ + 150, C.GREY, 1.1, head=5)
    pg.note(L + 160, y_ + 186, "e.g. two angles + any side\n(get the 3rd angle by 180°)", C.GREEN, 13)
    pg.note(L + 360, y_ + 186, "two sides + the angle between,\nor all three sides", C.ORANGE, 13)
    rule_box(f, "the ambiguous case (two possible triangles)", [
        "It can only happen with {B:two sides and a non-included angle} (SSA): you know $a$, $b$ and $A$.",
        "It happens only when the given angle $A$ is {B:acute} and the side opposite it is the {B:shorter} "
        "one ($a<b$), but still longer than the height $b\\sin A$.",
        "Then $\\sin B$ gives two angles: $B_1=\\sin^{-1}(\\dots)$ (acute) and $B_2=180^\\circ-B_1$ (obtuse). "
        "Keep $B_2$ only if $A+B_2<180^\\circ$.",
        "If $A$ is {B:obtuse} (or $90^\\circ$), or $a\\ge b$: only {B:one} triangle. If $a<b\\sin A$: no "
        "triangle at all (the calculator gives an error).",
    ], C.GREEN)
    ch.term("ambiguous case", "two sides and a non-included angle can give two different triangles, since sin B = sin(180° − B)")
    f.need(340)
    f.p("{b:See it with a hinge.} $A = 30^\\circ$, $b = 8$, $a = 5$. Draw the 30° angle at A and the 8-long "
        "side up to C. Side $a$ (5 long) hangs from C on a hinge, and must reach the bottom line to close the "
        "triangle.", 14, gap=8)
    go(f, "Swing the 5-long side from C down to the bottom line (a compass set to 5 does it). "
          "How many places can it land?")
    u = 29
    y_ = f.reserve(206)
    pg = f.pg
    Ax, Ay = L + 20, y_ + 150
    P = lambda X, Y: (Ax + X * u, Ay - Y * u)
    Cx_, Cy_ = 8 * math.cos(math.radians(30)), 8 * math.sin(math.radians(30))
    B1x, B2x = Cx_ - 3, Cx_ + 3
    pg.fillpoly([P(0, 0), P(B2x, 0), P(Cx_, Cy_)], C.LIGHT[C.BLUE])
    pg.fillpoly([P(0, 0), P(B1x, 0), P(Cx_, Cy_)], C.LIGHT[C.ORANGE])
    pg.line(*P(0, 0), *P(11.3, 0), C.INK, 1.4)
    pg.line(*P(0, 0), *P(Cx_, Cy_), C.INK, 2.0)
    pg.line(*P(Cx_, Cy_), *P(Cx_, 0), C.GREY, 1.0, dash=(3, 3))
    pg.text(P(Cx_, 2)[0] + 4, P(Cx_, 2)[1] - 6, "4", 10, C.GREY)
    pg.arc(*P(Cx_, Cy_), 5 * u, -150, -30, C.GREEN, 1.0)
    pg.line(*P(Cx_, Cy_), *P(B1x, 0), C.ORANGE, 2.2)
    pg.line(*P(Cx_, Cy_), *P(B2x, 0), C.BLUE, 2.2)
    for bx, col, lab in [(B1x, C.ORANGE, "B₁"), (B2x, C.BLUE, "B₂")]:
        pg.dot(*P(bx, 0), 3.5, col)
        pg.text(P(bx, 0)[0], P(bx, 0)[1] + 6, lab, 12, col, F.BOLD, align="center")
    pg.arc(*P(0, 0), 26, 0, 30, C.RED, 1.2)
    pg.text(P(0, 0)[0] + 30, P(0, 0)[1] - 16, "30°", 10, C.RED, F.BOLD)
    pg.text(P(0, 0)[0] - 12, P(0, 0)[1] - 6, "A", 12, C.RED, F.BOLD)
    pg.text(P(Cx_, Cy_)[0] - 4, P(Cx_, Cy_)[1] - 18, "C", 12, C.RED, F.BOLD)
    pg.text(P(Cx_ / 2, Cy_ / 2)[0] - 34, P(Cx_ / 2, Cy_ / 2)[1] - 24, "b = 8", 11, C.INK, F.BOLD)
    pg.text(P(Cx_ - 2.2, 2)[0] - 22, P(Cx_ - 2.2, 2)[1] - 6, "a = 5", 11, C.ORANGE, F.BOLD)
    pg.text(P(Cx_ + 1.9, 2)[0] + 2, P(Cx_ + 1.9, 2)[1] - 6, "a = 5", 11, C.BLUE, F.BOLD)
    pg.note(L + 378, y_ + 2, "Green arc: everywhere the hinged side can reach. It crosses the line "
            "TWICE.\n\nOrange triangle: A, B₁, C.\nBlue triangle: A, B₂, C (the orange one sits inside it).",
            C.INK, 13, w=R - L - 378)
    ch.check_num(8 * math.sin(math.radians(30)), 4, 1e-12)
    ch.check_num(math.hypot(Cx_ - B1x, Cy_), 5, 1e-12)
    ch.check_num(math.hypot(Cx_ - B2x, Cy_), 5, 1e-12)
    f.p("Two different triangles, both with $A = 30^\\circ$, $b = 8$, $a = 5$. The sine rule can't tell "
        "them apart:", 14, gap=6)
    step(f, r"\sin B=\frac{8\sin30^\circ}{5}=0.8", "sine rule, rearranged", size=18)
    step(f, r"B=\blu{53.13^\circ}\ \text{(calculator)}\quad\text{or}\quad B=\org{180^\circ-53.13^\circ=126.87^\circ}",
         "", size=16)
    Bs = math.degrees(math.asin(0.8))
    ch.check_num(Bs, 53.13, 0.005)
    ch.check_num(math.degrees(math.asin(math.sin(math.radians(180 - Bs)))), Bs, 1e-9)
    f.p("{R:$\\sin^{-1}$ only ever gives the acute one} (the blue triangle, at $B_2$). The obtuse partner "
        "(orange, at $B_1$) has exactly the same sine, and it fits too: $30^\\circ + 126.87^\\circ = "
        "156.87^\\circ$, under 180°. When the hinge is {B:shorter than b but longer than the height} "
        "($4 < a < 8$ here), expect two answers. Longer than b: only one. Shorter than the height: it can't "
        "reach, so no triangle.", 14)
    ch.check((180 - Bs) + 30 < 180, True)


def area(ch):
    f = flow(ch)
    sec(f, "Area of any triangle", room=300)
    rule_box(f, "area from two sides and the included angle", [
        "$\\text{Area}=\\tfrac12ab\\sin C=\\tfrac12bc\\sin A=\\tfrac12ac\\sin B$: half × two sides × the sine of "
        "the angle {B:between} them.",
        "Find an angle from the area: $\\sin C=\\dfrac{2\\times\\text{Area}}{ab}$. Two angles have that sine, "
        "$C$ and $180^\\circ-C$; both can be valid.",
        "Find a side from the area: $a=\\dfrac{2\\times\\text{Area}}{b\\sin C}$.",
    ], C.GREEN)
    f.p("\"Half base × height\" needs the height. But the height is $b\\sin A$ (from the sine-rule "
        "picture), so with two sides and the angle between them:", 14, gap=6)
    step(f, r"\text{Area}=\tfrac12\,bc\sin A", "", size=21, color=C.GREEN)
    ch.formula(r"\text{Area}=\tfrac12bc\sin A", "area of a triangle")
    ch.term("area of a triangle (trig)", "½ × two sides × sine of the angle between them")
    step(f, r"\text{clock triangle: }\tfrac12\times10\times7\times\sin60^\circ=30.3\text{ cm}^2", "", size=16)
    ch.check_num(0.5 * 70 * math.sin(D(60)), 30.31, tol=0.01)
    f.p("And the {B:perimeter} is just the three sides added: for the clock triangle $10 + 7 + 8.89 = "
        "25.89$ cm.", 14)


def unknowns(ch):
    f = flow(ch)
    sec(f, "Find the unknown: working backwards and chaining", room=520)
    rule_box(f, "partial-information triangle problems", [
        "Sketch the triangle and label {B:everything} you know, including the area if given.",
        "Write the equation that links what you know to what you want (sine rule, cosine rule, area formula, "
        "or $A+B+C=180^\\circ$).",
        "Solve for the unknown. For an angle from a sine, check whether $180^\\circ-$ it also fits.",
        "If the rule you need has a gap, fill it first with another rule (a chain: angle → side → area).",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    f.p("{b:Area → side:} a triangle has area 20 cm², $b=8$ cm and $C=30^\\circ$. Find $a$.", 14, gap=6)
    step(f, r"20=\tfrac12\times a\times8\times\sin30^\circ=2a\ \Rightarrow\ a=10\text{ cm}", "½ × 8 × 0.5 = 2",
         size=18, color=C.GREEN)
    av = sp.Symbol("a")
    ch.check(sp.solve(sp.Rational(1, 2) * av * 8 * sp.Rational(1, 2) - 20, av), [10])
    f.p("{b:Area → angle:} area 30 cm², sides 8 cm and 10 cm. Find the angle $C$ between them.", 14, gap=6)
    step(f, r"30=\tfrac12\times8\times10\sin C\ \Rightarrow\ \sin C=\frac{30}{40}=0.75", "", size=18)
    step(f, r"C=48.59^\circ\quad\text{or}\quad C=180^\circ-48.59^\circ=131.41^\circ", "both fit: two triangles",
         size=17, color=C.GREEN)
    ch.check_num(math.degrees(math.asin(0.75)), 48.59, tol=0.005)
    ch.check_num(0.5 * 80 * math.sin(D(131.41)), 30, tol=0.01)
    f.p("{b:Chain (angle → side → area):} $A=50^\\circ$, $B=60^\\circ$, $c=12$. Find the area.", 14, gap=6)
    step(f, r"C=180^\circ-50^\circ-60^\circ=70^\circ", "angle sum: now c = 12 has its matching angle", size=17)
    step(f, r"a=\frac{12\sin50^\circ}{\sin70^\circ}=9.78", "sine rule", size=17)
    step(f, r"\text{Area}=\tfrac12\,ac\sin B=\tfrac12\times9.78\times12\times\sin60^\circ=50.83", "B is between a and c",
         size=16, color=C.GREEN)
    av_ = 12 * math.sin(D(50)) / math.sin(D(70))
    ch.check_num(av_, 9.78, tol=0.005)
    ch.check_num(0.5 * av_ * 12 * math.sin(D(60)), 50.83, tol=0.01)
    f.need(150)
    mistakes(f, [
        (r"\text{Area}=\tfrac12ab\sin A", r"\text{Area}=\tfrac12ab\sin C",
         "the angle must be the one between the two sides you use"),
        (r"c^2=\ldots-2ab\cos A", r"c^2=\ldots-2ab\cos C", "the side on the left faces the angle in the cosine"),
    ])


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Notation", None, "side $a$ is opposite angle $A$, and so on"),
        ("Angle sum", r"A+B+C=180^\circ", None),
        ("Sine rule", r"\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}", "for an angle: $\\frac{\\sin A}{a}=\\frac{\\sin B}{b}$"),
        ("Cosine rule", r"a^2=b^2+c^2-2bc\cos A", "also $b^2=a^2+c^2-2ac\\cos B$, $c^2=a^2+b^2-2ab\\cos C$"),
        ("Cosine rule (angle)", r"\cos A=\frac{b^2+c^2-a^2}{2bc}", "SSS: find the largest angle first"),
        ("Which rule?", None, "matching side + angle → sine rule; SAS or SSS → cosine rule"),
        ("Ambiguous case", None, "SSA with the given angle acute and the side opposite it shorter: try "
         "$B$ and $180^\\circ-B$. Obtuse given angle: one triangle only"),
        ("Area", r"\text{Area}=\tfrac12ab\sin C", "two sides and the angle between them"),
        ("Area backwards", r"\sin C=\frac{2\times\text{Area}}{ab},\qquad a=\frac{2\times\text{Area}}{b\sin C}",
         "an angle from a sine may have two answers"),
    ], C.GREEN)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Draw each triangle first. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Sine rule", ["A = 40°, B = 75°, a = 8. Find b.", "a = 12, A = 110°, b = 9. Find B.",
                       "Two angles are 35° and 65°; the side between them is 20. Find the side opposite 65°."],
         "1. 8 sin 75°/sin 40° ≈ 12.02   2. sin⁻¹(9 sin 110°/12) ≈ 44.8°   3. third angle 80°; 20 sin 65°/sin 80° ≈ 18.41"),
        ("Cosine rule", ["b = 5, c = 8, A = 50°. Find a.", "Sides 4, 7, 9: find the largest angle.",
                         "Clock hands 10 cm and 7 cm at 4 o'clock: distance between the tips?"],
         "4. ≈ 6.13   5. cos⁻¹((16 + 49 − 81)/56) ≈ 106.6°   6. 120°: √(149 + 70) ≈ 14.80 cm"),
        ("Choose", ["You know all three angles. Can you find the sides?", "Area with sides 6, 9 and 30° between"],
         "7. no, only their ratios (the triangle could be any size)   8. 13.5"),
        ("Find the unknown", ["A triangle has area 24 cm² and sides 8 cm and 10 cm. Find the angle between them "
                              "(two answers).",
                              "Area 35 cm², C = 150°, a = 10 cm. Find b.",
                              "A = 40°, B = 70°, c = 15. Find a, then the area.",
                              "Sides 7 and 9 with 60° between them: find the third side, then the area.",
                              "A = 120°, a = 9, b = 5. How many triangles? Find B."],
         "9. sin C = 48/80 = 0.6, C = 36.87° or 143.13°   10. 35 = ½ × 10 × b × 0.5, so b = 14 cm   "
         "11. C = 70°; a = 15 sin 40°/sin 70° ≈ 10.26; area = ½ × 10.26 × 15 × sin 70° ≈ 72.31   "
         "12. c² = 49 + 81 − 63 = 67, c ≈ 8.19; area = ½ × 7 × 9 × sin 60° ≈ 27.28   "
         "13. A is obtuse, so one triangle: sin B = 5 sin 120°/9 ≈ 0.481, B ≈ 28.76°"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.GREEN, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check_num(8 * math.sin(D(75)) / math.sin(D(40)), 12.02, tol=0.005)
    ch.check_num(math.degrees(math.asin(9 * math.sin(D(110)) / 12)), 44.8, tol=0.05)
    ch.check_num(20 * math.sin(D(65)) / math.sin(D(80)), 18.41, tol=0.005)
    ch.check_num(math.sqrt(25 + 64 - 80 * math.cos(D(50))), 6.13, tol=0.005)
    ch.check_num(math.degrees(math.acos((16 + 49 - 81) / 56)), 106.6, tol=0.05)
    ch.check_num(math.sqrt(149 - 140 * math.cos(D(120))), 14.80, tol=0.005)
    ch.check_num(0.5 * 54 * 0.5, 13.5)
    ch.check_num(math.degrees(math.asin(48 / 80)), 36.87, tol=0.005)
    ch.check_num(0.5 * 80 * math.sin(D(143.13)), 24, tol=0.01)
    bv = sp.Symbol("b")
    ch.check(sp.solve(sp.Rational(1, 2) * 10 * bv * sp.Rational(1, 2) - 35, bv), [14])
    a11 = 15 * math.sin(D(40)) / math.sin(D(70))
    ch.check_num(a11, 10.26, tol=0.005)
    ch.check_num(0.5 * a11 * 15 * math.sin(D(70)), 72.31, tol=0.01)
    ch.check(49 + 81 - 2 * 7 * 9 * sp.cos(sp.pi / 3), 67)
    ch.check_num(math.sqrt(67), 8.19, tol=0.005)
    ch.check_num(0.5 * 63 * math.sin(D(60)), 27.28, tol=0.005)
    sB = 5 * math.sin(D(120)) / 9
    ch.check_num(sB, 0.481, tol=0.0005)
    ch.check_num(math.degrees(math.asin(sB)), 28.76, tol=0.005)
    ch.check_true(120 + (180 - math.degrees(math.asin(sB))) > 180)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    names(ch)
    sine_rule(ch)
    river(ch)
    cosine_rule(ch)
    decide(ch)
    area(ch)
    unknowns(ch)
    summary(ch)
    your_turn(ch)
