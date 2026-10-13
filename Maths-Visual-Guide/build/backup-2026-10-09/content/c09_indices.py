"""Chapter 9 - Indices (powers). Folding paper, counting the laws out longhand, a staircase down
to zero and negative powers, squares and cubes for roots, and standard form with KB and MB."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 9
NUM = 9
TITLE = "Indices (powers and roots)"
SHORT = "Indices"
SLUG = "Indices"
ACCENT = C.BLUE
REQUIRES = ["multiplication", "fraction", "reciprocal", "decimal-place-value", "algebraic-notation", "term",
            "variable", "area", "volume", "negative-numbers", "divide-fractions", "substitution"]
INTRODUCES = ["powers", "base-exponent", "roots", "index-laws", "zero-power", "negative-powers",
              "fractional-powers", "standard-form"]

PAPER = "#fcfbff"
FOLD = "#fff3c4"
x, a, b = sp.symbols("x a b", positive=True)


def icon(pg, x0, y0):
    pg.rect(x0, y0 + 2, 18, 14, C.BROWN, 1, fillcolor=FOLD)
    pg.line(x0 + 9, y0 + 2, x0 + 9, y0 + 16, C.BROWN, 0.8, dash=(2, 2))
    pg.text(x0 + 13, y0 - 4, "n", 8, C.BLUE, F.BOLD, solid=False)


def sec(f, t, **kw):
    section(f, t, C.BLUE, icon, **kw)


def xbox(pg, x0, y0, col, letter="x", s=24):
    pg.rect(x0, y0, s, s, col, 1.3, fillcolor=C.LIGHT.get(col, "#ffffff"), r=4)
    pg.eq(x0 + s / 2, y0 + s / 2, letter, 15, col, align="center", valign="middle", solid=False)


def lawbox(f, latex, size=22):
    pg = f.pg
    w, h, _ = pg.eq_size(latex, size)
    bw, bh = max(290, w + 50), h + 20
    y = f.reserve(bh + 8)
    pg = f.pg
    pg.rect(L + (W - bw) / 2, y, bw, bh, C.BLUE, 1.6, fillcolor=C.LIGHT[C.BLUE], r=8)
    pg.eq(L + W / 2, y + bh / 2, latex, size, align="center", valign="middle")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 9, "Indices (powers and roots)", "multiplying a number by itself, "
                     "again and again", C.BLUE, PAPER)
    y = 210
    for k in range(5):
        n = 2 ** k
        xx = L + 20 + k * 96
        for i in range(min(n, 16)):
            pg.rect(xx + i * 1.6, y + 60 - i * 1.6 - 40 / (k + 1), 60 / (1 + k * 0.3), 40 / (k + 1) + 20,
                    C.BROWN, 0.5, fillcolor=FOLD)
        pg.eq(xx + 30, y + 100, rf"2^{k}={n}", 16, C.BLUE, align="center")
        pg.note(xx + 4, y + 124, f"{k} fold{'s' if k != 1 else ''}", C.BROWN, 15)
    f = ch.flow(top=400)
    f.p("Fold a sheet of paper in half: 2 layers. Again: 4. Again: 8. Each fold {B:doubles} the "
        "layers. After 5 folds you have $2 \\times 2 \\times 2 \\times 2 \\times 2 = 32$ layers. "
        "Writing all those 2s is tiring, so maths has a shorthand: $2^5$. That little raised number "
        "is a {B:power} (also called an {B:index} or {B:exponent}).", 14, gap=10)
    f.p("Powers are everywhere: areas (cm²), volumes (cm³), computer memory (2¹⁰ bytes), tiny and "
        "huge numbers (standard form), and later exponential growth and logarithms (Chapters 21-22). "
        "This chapter builds every rule by {B:counting}, so you never have to memorise blindly.",
        14, gap=10)
    f.p("{y:Goes with} {B:Lecture 7} {y:(power terminology, combining powers, standard form).}", 12.5)


def what(ch):
    f = flow(ch)
    sec(f, "A power is repeated multiplication")
    f.p("Your lecture puts it neatly. {B:Repeated adding} has a shortcut called multiplying; "
        "{B:repeated multiplying} has a shortcut called a power:", 14, gap=8)
    y = f.reserve(70)
    pg = f.pg
    pg.eq(L + 20, y, r"3+3+3+3=4\times3=12", 20)
    pg.note(L + 290, y, "four 3s added", C.GREY, 15)
    pg.eq(L + 20, y + 36, r"3\times3\times3\times3=3^4=81", 20, C.BLUE)
    pg.note(L + 290, y + 36, "four 3s multiplied", C.BLUE, 15)
    ch.check(3 ** 4, 81)
    y = f.reserve(142)
    pg = f.pg
    pg.eq(L + 60, y + 20, r"3", 60, C.ORANGE)
    pg.eq(L + 92, y + 6, r"4", 30, C.BLUE, solid=False)
    pg.arrow(L + 40, y + 96, L + 70, y + 76, C.ORANGE, 1.2)
    pg.note(L - 4, y + 96, "the base: the number\nbeing multiplied", C.ORANGE, 15)
    pg.arrow(L + 150, y + 10, L + 118, y + 18, C.BLUE, 1.2)
    pg.note(L + 156, y - 2, "the power (index, exponent):\nhow many copies of the base", C.BLUE, 15)
    pg.note(L + 300, y + 56, "say: \"three to the power four\"\nor \"three to the four\"", C.RED, 15)
    ch.term("base", "in a^n, the number a that gets multiplied by itself")
    ch.term("exponent", "another name for the power or index")
    ch.symbol(r"a^n", "a to the power n", "n copies of a multiplied together")
    f.p("{b:Special names:} power 2 is \"squared\" ($5^2 = 25$), power 3 is \"cubed\" "
        "($2^3 = 8$). Power 1 is just the number itself: $7^1 = 7$ (one copy).", 14, gap=8)
    f.p("{R:The trap:} $3^4$ is {B:not} $3 \\times 4$. $3^4 = 81$ but $3 \\times 4 = 12$. The power "
        "counts copies; it doesn't multiply by itself.", 14, gap=8)
    f.p("{h:Typing powers:} calculators have an x^y or ^ key; computers write 3^4, and Python "
        "writes 3**4. Your slides mention \"x^2\" for when you can't type a raised number.", 13.5, C.BROWN)
    y = f.reserve(40)
    pg = f.pg
    for i, (lat, v) in enumerate([(r"10^1", "10"), (r"10^2", "100"), (r"10^3", "1000"), (r"10^6", "1,000,000")]):
        pg.eq(L + 20 + i * 120, y, lat + "=" + r"\text{" + v + "}", 16, C.BLUE)
    f.p("Powers of 10 are easy: the power counts the zeros.", 13.5, C.GREY)


def roots(ch):
    f = flow(ch)
    sec(f, "Roots: running a power backwards", room=380)
    f.p("A square with side 5 has area $5^2 = 25$. Going backwards, \"which side gives area 25?\", "
        "is the {B:square root}: $\\sqrt{25} = 5$. The √ sign started life as a letter r, for radix "
        "(root).", 14, gap=8)
    ch.term("square root", "the number that, multiplied by itself, gives the original: √25 = 5")
    ch.symbol(r"\sqrt{x}", "the square root of x", "the positive number whose square is x")
    y = f.reserve(120)
    pg = f.pg
    s = 18
    for i in range(5):
        for j in range(5):
            pg.rect(L + 20 + j * s, y + 10 + i * s, s, s, C.BLUE, 0.5, fillcolor=C.LIGHT[C.BLUE])
    pg.note(L + 20, y - 10, "side 5", C.BLUE, 14)
    pg.note(L + 116, y + 36, "area 25", C.BLUE, 14)
    pg.arrow(L + 180, y + 30, L + 240, y + 30, C.GREEN, 1.4)
    pg.note(L + 176, y + 6, "square it", C.GREEN, 14)
    pg.arrow(L + 240, y + 60, L + 180, y + 60, C.RED, 1.4)
    pg.note(L + 176, y + 64, "square root", C.RED, 14)
    pg.eq(L + 260, y + 20, r"5^2=25", 20, C.GREEN)
    pg.eq(L + 260, y + 54, r"\sqrt{25}=5", 20, C.RED)
    pg.note(L + 370, y + 20, "each one is the\nundo button of\nthe other", C.PURPLE, 15)
    f.p("{b:Cube roots} undo cubing: a cube of volume 8 has side 2, so $\\sqrt[3]{8} = 2$. In "
        "general $\\sqrt[n]{x}$ (the {B:n-th root}) undoes the power n: $\\sqrt[4]{81} = 3$ because "
        "$3^4 = 81$.", 14, gap=8)
    ch.symbol(r"\sqrt[n]{x}", "the n-th root of x", "the number whose n-th power is x")
    ch.check(sp.root(81, 4), 3)
    f.p("{R:Two answers hiding:} $(-5)^2$ is also 25 (negative × negative is positive). The √ sign "
        "always means the {B:positive} one, but when solving $x^2 = 25$ (Chapter 15) remember "
        "$x = 5$ or $x = -5$, written $x = \\pm 5$.", 13.5)
    ch.symbol(r"\pm", "plus or minus", "both the + and − versions")


def laws(ch):
    f = flow(ch)
    sec(f, "The first law: count the letters", room=400)
    f.p("What is $x^2 \\times x^3$? Don't reach for a rule. {B:Write out every x and count them}:",
        14, gap=8)
    y = f.reserve(70)
    pg = f.pg
    pg.eq(L + 10, y + 12, r"x^2\times x^3=", 20)
    X0 = L + 130
    for i in range(2):
        xbox(pg, X0 + i * 28, y + 6, C.ORANGE)
    pg.text(X0 + 60, y + 8, "×", 18, C.INK)
    for i in range(3):
        xbox(pg, X0 + 80 + i * 28, y + 6, C.GREEN)
    pg.text(X0 + 172, y + 8, "=", 18, C.INK)
    pg.eq(X0 + 196, y + 10, r"x^5", 24, C.BLUE)
    pg.note(X0, y + 36, "2 x's", C.ORANGE, 15)
    pg.note(X0 + 80, y + 36, "3 x's", C.GREEN, 15)
    pg.note(X0 + 196, y + 36, "5 x's altogether", C.BLUE, 15)
    ch.check(x ** 2 * x ** 3, x ** 5)
    f.p("The powers just {B:add}. Test with numbers: $2^2 \\times 2^3 = 4 \\times 8 = 32$ and "
        "$2^5 = 32$ ✓. Written as a law (from your slides):", 14, gap=6)
    lawbox(f, r"a^m\times a^n=a^{m+n}", 22)
    ch.formula(r"a^m\times a^n=a^{m+n}", "multiplying powers of the same base")
    ch.check(2 ** 2 * 2 ** 3, 2 ** 5)
    f.p("{R:Only for the same base.} $x^2 \\times y^3$ can't be squashed (different envelopes), and "
        "$x^2 + x^3$ is {B:not} $x^5$ (that's adding, not multiplying: test $x = 2$: $4 + 8 = 12$, "
        "but $2^5 = 32$).", 13.5)
    ch.check_true((2 ** 2 + 2 ** 3) != 2 ** 5)


def law2(ch):
    f = flow(ch)
    sec(f, "Dividing: cancel in pairs", room=330)
    f.p("$\\frac{x^5}{x^2}$: write the x's out on top and bottom. Each x on the bottom cancels one on "
        "top (like simplifying a fraction, Chapter 2):", 14, gap=8)
    y = f.reserve(90)
    pg = f.pg
    X0 = L + 40
    for i in range(5):
        xbox(pg, X0 + i * 28, y + 4, C.GREEN)
    pg.line(X0 - 4, y + 38, X0 + 144, y + 38, C.INK, 1.4)
    for i in range(2):
        xbox(pg, X0 + i * 28, y + 44, C.ORANGE)
    for i in range(2):
        pg.line(X0 + i * 28 - 2, y + 30, X0 + i * 28 + 26, y + 2, C.RED, 1.6)
        pg.line(X0 + i * 28 - 2, y + 70, X0 + i * 28 + 26, y + 42, C.RED, 1.6)
    pg.text(X0 + 160, y + 26, "=", 20, C.INK)
    pg.eq(X0 + 190, y + 26, r"x^3", 24, C.BLUE)
    pg.note(X0 + 250, y + 10, "two pairs cancel;\n5 − 2 = 3 x's are left", C.RED, 15)
    ch.check(x ** 5 / x ** 2, x ** 3)
    lawbox(f, r"\frac{a^m}{a^n}=a^{m-n}", 22)
    ch.formula(r"\frac{a^m}{a^n}=a^{m-n}", "dividing powers of the same base")
    f.p("Test: $\\frac{2^5}{2^2} = \\frac{32}{4} = 8 = 2^3$ ✓.", 14)


def law3(ch):
    f = flow(ch)
    sec(f, "A power of a power: groups of groups", room=360)
    f.p("$(x^2)^3$ means three copies of $x^2$. Each copy is a pair of x's, so count the pairs:",
        14, gap=8)
    y = f.reserve(60)
    pg = f.pg
    pg.eq(L + 10, y + 12, r"(x^2)^3=", 20)
    X0 = L + 110
    for g in range(3):
        gx = X0 + g * 80
        pg.rect(gx - 4, y + 2, 64, 36, C.PURPLE, 1.1, r=8, dash=(3, 2))
        for i in range(2):
            xbox(pg, gx + i * 28, y + 8, C.ORANGE)
    pg.text(X0 + 246, y + 8, "=", 20, C.INK)
    pg.eq(X0 + 270, y + 10, r"x^6", 24, C.BLUE)
    pg.note(X0, y + 42, "3 groups of 2 = 6 x's: the powers multiply", C.PURPLE, 15)
    ch.check((x ** 2) ** 3, x ** 6)
    lawbox(f, r"(a^m)^n=a^{mn}", 22)
    ch.formula(r"(a^m)^n=a^{mn}", "power of a power")
    f.p("{b:Brackets with several things inside} (the last two laws on your slides). The power "
        "applies to {B:everything} in the bracket:", 14, gap=6)
    step(f, r"(xy)^3=xy\times xy\times xy=x^3y^3", "rearrange: all x's together, all y's together", size=19)
    step(f, r"\left(\frac{x}{y}\right)^3=\frac{x}{y}\times\frac{x}{y}\times\frac{x}{y}=\frac{x^3}{y^3}",
         "top × top, bottom × bottom", size=19)
    step(f, r"(2x)^3=8x^3", "the 2 gets cubed too! (2³ = 8)", size=19, color=C.GREEN)
    ch.formula(r"(ab)^n=a^nb^n", "power of a product")
    ch.check(sp.expand((2 * x) ** 3), 8 * x ** 3)


def staircase(ch):
    f = flow(ch)
    sec(f, "The staircase: zero and negative powers", room=480)
    f.p("What could $2^0$ or $2^{-1}$ possibly mean? \"Zero copies of 2 multiplied\"? Walk down a "
        "staircase instead. Every step down {B:divides by 2} (the opposite of one more fold):", 14, gap=8)
    y = f.reserve(262)
    pg = f.pg
    steps_ = [("2^3", "8"), ("2^2", "4"), ("2^1", "2"), ("2^0", "1"), ("2^{-1}", r"\tfrac12"),
              ("2^{-2}", r"\tfrac14"), ("2^{-3}", r"\tfrac18")]
    sw, sh = 62, 28
    for i, (p, v) in enumerate(steps_):
        xx = L + 10 + i * sw
        yy = y + i * sh
        col = C.BLUE if i < 3 else (C.GREEN if i == 3 else C.PURPLE)
        pg.rect(xx, yy + 20, sw, 250 - 20 - i * sh, col, 0.8, fillcolor=C.LIGHT[col])
        pg.eq(xx + sw / 2, yy + 34, p, 16, col, align="center", valign="middle")
        pg.eq(xx + sw / 2, yy + 58, "=" + v, 15, C.INK, align="center", valign="middle")
        if i < len(steps_) - 1:
            pg.arrow(xx + sw - 8, yy + 12, xx + sw + 16, yy + sh + 12, C.RED, 1.1, bend=-0.4, head=4)
    pg.note(L + 250, y - 6, "÷ 2 on every step down", C.RED, 15)
    pg.note(L + 270, y + 40, "power 0 lands on 1", C.GREEN, 15)
    pg.note(L + 340, y + 90, "below zero: fractions", C.PURPLE, 15)
    ch.check(sp.Integer(2) ** 0, 1)
    ch.check(sp.Integer(2) ** -3, sp.Rational(1, 8))
    f.p("So {B:anything to the power 0 is 1}, and a {B:negative power means \"one over\"} the positive "
        "power. \"One over\" is the {B:reciprocal}: flip the number upside down. A whole number is secretly "
        "over 1, so $8 = \\frac81$ flips to $\\frac18$ (Chapter 2, \"Dividing: how many fit?\"). Read the "
        "staircase: $2^{-3}$ is $2^3 = 8$ flipped, which is $\\frac18$.", 14, gap=6)
    lawbox(f, r"a^0=1\qquad\qquad a^{-n}=\frac{1}{a^n}", 22)
    ch.formula(r"a^0=1", "zero power")
    ch.formula(r"a^{-n}=\frac1{a^n}", "negative power")
    f.p("{b:The dividing law agrees}, which is how we know the staircase isn't a trick: "
        "$\\frac{x^3}{x^3} = x^{3-3} = x^0$, but anything divided by itself is 1. And "
        "$\\frac{x^2}{x^3} = x^{-1}$, but cancelling leaves $\\frac{1}{x}$.", 14, gap=8)
    f.p("{R:A negative power does NOT make the number negative:} $2^{-3} = \\frac18$, a small "
        "positive number.", 13.5)


def fractional(ch):
    f = flow(ch)
    sec(f, "Fraction powers are roots", room=360)
    f.p("What would $9^{\\frac12}$ mean? Use the power-of-a-power law as a detective. Square it:", 14, gap=6)
    step(f, r"\left(9^{\frac12}\right)^2=9^{\frac12\times2}=9^1=9", "powers multiply: ½ × 2 = 1", size=19)
    step(f, r"\text{so }9^{\frac12}\text{ is the number whose square is 9}", "that's the definition of √", size=17)
    step(f, r"9^{\frac12}=\sqrt9=3", "", size=19, color=C.GREEN)
    ch.check(sp.Integer(9) ** sp.Rational(1, 2), 3)
    f.p("In general, the bottom of the fraction is the root and the top is an ordinary power:", 14, gap=6)
    lawbox(f, r"a^{\frac1n}=\sqrt[n]{a}\qquad\quad a^{\frac mn}=\left(\sqrt[n]{a}\right)^m", 20)
    ch.formula(r"a^{\frac mn}=\left(\sqrt[n]{a}\right)^m", "fractional power")
    step(f, r"8^{\frac23}=\left(\sqrt[3]8\right)^2=2^2=4", "root first (cube root of 8 is 2), then square", size=19)
    step(f, r"16^{-\frac12}=\frac{1}{\sqrt{16}}=\frac14", "minus: one over. Half: square root.", size=19)
    ch.check(sp.Integer(8) ** sp.Rational(2, 3), 4)
    ch.check(sp.Integer(16) ** sp.Rational(-1, 2), sp.Rational(1, 4))
    f.p("{h:Why roots first?} Smaller numbers: $(\\sqrt[3]{8})^2 = 2^2$ is easier than "
        "$\\sqrt[3]{64}$ (same answer, 4).", 13.5, C.BROWN)


def mistakes(ch):
    f = flow(ch)
    sec(f, "Test before you trust: four famous mistakes", room=380)
    f.p("Your Lecture 2 lists these. Each one is caught instantly by trying small numbers:", 14, gap=8)
    rows = [(r"(a+b)^2\ne a^2+b^2", "a = 3, b = 4:  (7)² = 49,  but 9 + 16 = 25",
             "the square is on the whole bracket; Chapter 11 shows (a+b)² = a² + 2ab + b²"),
            (r"\sqrt{a^2+b^2}\ne a+b", "a = 3, b = 4:  √25 = 5,  but 3 + 4 = 7", "roots don't split over +"),
            (r"2x^3\ne(2x)^3", "x = 1:  2 × 1 = 2,  but 2³ = 8", "the power only sits on what it touches"),
            (r"x^2+x^3\ne x^5", "x = 2:  4 + 8 = 12,  but 32", "laws are for ×, not +")]
    for lat, test, why in rows:
        y = f.reserve(56)
        pg = f.pg
        pg.eq(L + 10, y + 4, lat, 19, C.RED)
        pg.text(L + 190, y + 2, test, 12, C.INK)
        pg.note(L + 190, y + 20, why, C.GREEN, 14, w=R - L - 190)
    ch.check_true((3 + 4) ** 2 != 3 ** 2 + 4 ** 2)


def standard_form(ch):
    f = flow(ch)
    sec(f, "Standard form: KB, MB, GB and tiny things", room=480)
    f.p("A 1 GB file holds about 1,000,000,000 bytes. A bacterium is 0.000002 m long. Counting "
        "zeros is error-prone, so we write a {B:small number × a power of 10}:", 14, gap=8)
    ch.term("standard form", "a number written as a × 10^n with 1 ≤ a < 10")
    y = f.reserve(170)
    pg = f.pg
    rows = [("1 kB", "1000 bytes", r"1\times10^3"), ("1 MB", "1,000,000 bytes", r"1\times10^6"),
            ("1 GB", "1,000,000,000 bytes", r"1\times10^9"), ("57", "", r"5.7\times10^1"),
            ("0.0024", "", r"2.4\times10^{-3}"), ("0.000001", "", r"1\times10^{-6}")]
    for i, (a_, b_, c_) in enumerate(rows):
        yy = y + i * 27
        col = C.BLUE if i < 3 else (C.INK if i == 3 else C.PURPLE)
        pg.text(L + 20, yy + 4, a_, 14, col, F.BOLD)
        pg.text(L + 110, yy + 4, b_, 12, C.GREY)
        pg.eq(L + 280, yy + 2, c_, 18, col)
    pg.note(L + 390, y + 20, "big numbers:\npositive power", C.BLUE, 15)
    pg.note(L + 390, y + 110, "small numbers:\nnegative power", C.PURPLE, 15)
    ch.check(sp.Rational(24, 10) * sp.Integer(10) ** -3, sp.Rational(24, 10000))
    f.p("{b:The recipe.} Write the digits with the dot after the first non-zero digit (that's a, "
        "between 1 and 10). Then count how many places the digits had to slide (Chapter 3): that's "
        "the power. Slid right (the number was small) → negative power.", 14, gap=6)
    step(f, r"0.0024\ \to\ 2.4", "digits slide 3 places left, so the dot seems to move right", size=18)
    step(f, r"0.0024=2.4\times10^{-3}", "× 10⁻³ (÷ 1000) puts it back", size=19, color=C.GREEN)
    f.p("{R:Slide note:} Lecture 7 writes $1 \\le a \\le 10$; it should be $1 \\le a < 10$. The number "
        "10 itself is written $1 \\times 10^1$, never $10 \\times 10^0$.", 13.5, gap=8)
    f.p("{b:Multiplying in standard form} uses the first law on the powers of 10: "
        "$(3 \\times 10^4) \\times (2 \\times 10^5) = 6 \\times 10^{9}$. Calculators show "
        "$2.4 \\times 10^{-3}$ as 2.4E-3 (E for exponent).", 14)
    ch.check((3 * 10 ** 4) * (2 * 10 ** 5), 6 * 10 ** 9)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Folding paper: your turn", fresh=True)
    f.p("Answers in grey. Write out the letters longhand if you're not sure!", 13.5, gap=10)
    groups = [
        ("Values", ["2⁶", "5³", "10⁰", "4⁻¹", "3⁻²", "25^(1/2)", "27^(2/3)", "√(49)"],
         "1. 64   2. 125   3. 1   4. 1/4   5. 1/9   6. 5   7. 9   8. 7"),
        ("Simplify", ["x⁴ × x⁵", "y⁹ ÷ y³", "(a³)⁴", "(3x)²", "x⁻² × x⁵", "(x²y³)²"],
         "9. x⁹   10. y⁶   11. a¹²   12. 9x²   13. x³   14. x⁴y⁶"),
        ("Standard form", ["Write 45,000 in standard form", "Write 0.00061 in standard form",
                           "(4 × 10³) × (2 × 10⁻⁵)"],
         "15. 4.5 × 10⁴   16. 6.1 × 10⁻⁴   17. 8 × 10⁻²"),
        ("Spot the error", ["Tom says 3⁻² = −9. Why is he wrong?"], "18. negative power means one over: 1/9"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    I = sp.Integer
    for g, e in [(I(2) ** 6, 64), (I(4) ** -1, sp.Rational(1, 4)), (I(3) ** -2, sp.Rational(1, 9)),
                 (I(27) ** sp.Rational(2, 3), 9), (x ** -2 * x ** 5, x ** 3), ((a ** 3) ** 4, a ** 12)]:
        ch.check(g, e)
    ch.check(sp.Rational(4 * 10 ** 3 * 2, 10 ** 5), sp.Rational(8, 100))


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    what(ch)
    roots(ch)
    laws(ch)
    law2(ch)
    law3(ch)
    staircase(ch)
    fractional(ch)
    mistakes(ch)
    standard_form(ch)
    your_turn(ch)
