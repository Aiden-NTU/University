"""Chapter 9 - Indices (powers). Folding paper, counting the laws out longhand, a staircase down
to zero and negative powers, squares and cubes for roots, and standard form with KB and MB."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, rule_box, rules_page, rules_table, section, step, title_block
from content.kit import mistakes as wrong_right

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
uk = sp.symbols("uk")


def ex(f, s):
    f.need(100)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


def solve1(eq):
    """The single real solution of an equation in `uk` (written as expression = 0)."""
    (s,) = [r for r in sp.solve(eq, uk) if r.is_real]
    return s


def icon(pg, x0, y0):
    pg.rect(x0, y0 + 2, 18, 14, C.BROWN, 1, fillcolor=FOLD)
    pg.line(x0 + 9, y0 + 2, x0 + 9, y0 + 16, C.BROWN, 0.8, dash=(2, 2))
    pg.text(x0 + 13, y0 - 4, "n", 8, C.BLUE, F.BOLD, solid=False)


def sec(f, t, **kw):
    section(f, t, C.BLUE, icon, **kw)


def xbox(pg, x0, y0, col, letter="x", s=24):
    pg.rect(x0, y0, s, s, col, 1.3, fillcolor=C.LIGHT.get(col, "#ffffff"), r=4)
    pg.eq(x0 + s / 2, y0 + s / 2, letter, 15, col, align="center", valign="middle", solid=False)


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
    rule_box(f, "what a power means", [
        "$a^n=a\\times a\\times\\cdots\\times a$ with $n$ copies of $a$. $a$ is the {B:base}; $n$ is the "
        "{B:power} (also called the {B:index} or {B:exponent}).",
        "$a^1=a$, $a^2$ is \"$a$ squared\", $a^3$ is \"$a$ cubed\". $a^n$ is {B:not} $a\\times n$.",
    ], C.BLUE)
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
    sec(f, "Roots: running a power backwards", room=480)
    rule_box(f, "roots", [
        "$\\sqrt[n]{a}$ (the $n$-th root of $a$) is the number whose $n$-th power is $a$: "
        "$\\sqrt[3]{8}=2$ because $2^3=8$. $\\sqrt{a}$ means $\\sqrt[2]{a}$.",
        "The $\\sqrt{\\ }$ sign means the {B:positive} root: $\\sqrt{25}=5$. But $x^2=25$ has two "
        "solutions, $x=\\pm5$.",
    ], C.BLUE)
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


def negatives(ch):
    f = flow(ch)
    sec(f, "Negative bases, and roots of negative numbers", room=440)
    rule_box(f, "powers of a negative number", [
        "A negative base to an {B:even} power is {B:positive}: $(-2)^4=16$. "
        "Every pair of minus signs multiplies to $+$.",
        "A negative base to an {B:odd} power is {B:negative}: $(-2)^3=-8$. One minus sign is left over.",
        "Brackets matter: $(-3)^2=(-3)\\times(-3)=9$, but $-3^2=-(3\\times3)=-9$. "
        "Without brackets the power is done first and only touches the 3.",
    ], C.BLUE)
    rule_box(f, "roots of a negative number", [
        "{B:Even} roots ($\\sqrt{\\ }$, $\\sqrt[4]{\\ }$, ...) of a negative number {B:do not exist} as real "
        "numbers: no real number squared gives $-4$, so $\\sqrt{-4}$ is undefined (your calculator says Error).",
        "{B:Odd} roots of a negative number are negative: $\\sqrt[3]{-8}=-2$ because $(-2)^3=-8$.",
    ], C.BLUE)
    I = sp.Integer
    step(f, r"(-2)^4=(-2)(-2)(-2)(-2)=16", "two pairs of minuses: positive", size=19)
    step(f, r"(-2)^5=16\times(-2)=-32", "one more minus: negative", size=19)
    step(f, r"-2^4=-(2^4)=-16", "no brackets: the minus waits until the end", size=19)
    step(f, r"\sqrt[3]{-27}=-3", "check: (−3)³ = −27", size=19, color=C.GREEN)
    ch.check(I(-2) ** 4, 16)
    ch.check(I(-2) ** 5, -32)
    ch.check(-I(2) ** 4, -16)
    ch.check(I(-3) ** 3, -27)
    ch.check(sp.real_root(-27, 3), -3)
    ch.check_true(not sp.sqrt(I(-4)).is_real)


def laws(ch):
    f = flow(ch)
    sec(f, "The first law: multiplying powers", room=400)
    rule_box(f, "multiplying powers of the same base", [
        "$a^m\\times a^n=a^{m+n}$: keep the base, {B:add} the powers.",
        "Only for the {B:same base}: $x^2\\times y^3$ and $2^3\\times3^2$ cannot be combined this way.",
        "Only for {B:multiplying}: $x^2+x^3$ is not $x^5$; it can't be simplified.",
        "Numbers in front (coefficients) are multiplied as ordinary numbers: "
        "$3x^2\\times2x^3=6x^5$.",
    ], C.BLUE)
    f.p("Why? What is $x^2 \\times x^3$? {B:Write out every x and count them}:",
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
        "$2^5 = 32$ ✓.", 14, gap=6)
    ch.formula(r"a^m\times a^n=a^{m+n}", "multiplying powers of the same base")
    ch.check(2 ** 2 * 2 ** 3, 2 ** 5)
    ex(f, "$3x^2\\times2x^3$.")
    step(f, r"(3\times2)(x^2\times x^3)=6x^5", "numbers × numbers; add the powers", size=19, color=C.GREEN)
    ch.check(3 * x ** 2 * 2 * x ** 3, 6 * x ** 5)
    f.p("{R:Only for the same base.} $x^2 \\times y^3$ can't be squashed (different envelopes), and "
        "$x^2 + x^3$ is {B:not} $x^5$ (that's adding, not multiplying: test $x = 2$: $4 + 8 = 12$, "
        "but $2^5 = 32$).", 13.5)
    ch.check_true((2 ** 2 + 2 ** 3) != 2 ** 5)


def law2(ch):
    f = flow(ch)
    sec(f, "Dividing: cancel in pairs", room=300)
    rule_box(f, "dividing powers of the same base", [
        "$a^m\\div a^n=\\dfrac{a^m}{a^n}=a^{m-n}$: keep the base, {B:subtract} the powers (top minus bottom).",
        "Coefficients are divided as ordinary numbers: $6x^5\\div2x^2=3x^3$.",
    ], C.BLUE)
    f.p("Why? $\\frac{x^5}{x^2}$: write the x's out on top and bottom. Each x on the bottom cancels one on "
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
    ch.formula(r"\frac{a^m}{a^n}=a^{m-n}", "dividing powers of the same base")
    f.p("Test: $\\frac{2^5}{2^2} = \\frac{32}{4} = 8 = 2^3$ ✓.", 14, gap=8)
    ex(f, "$6x^5\\div2x^2$.")
    step(f, r"\frac{6x^5}{2x^2}=\frac62\times\frac{x^5}{x^2}=3x^3", "divide the numbers; subtract the powers",
         size=19, color=C.GREEN)
    ch.check(6 * x ** 5 / (2 * x ** 2), 3 * x ** 3)
    ex(f, "$\\dfrac{10a^4b^3}{5ab}$.")
    step(f, r"\frac{10}{5}\,a^{4-1}\,b^{3-1}=2a^3b^2", "each letter separately; a = a¹", size=19,
         color=C.GREEN)
    ch.check(10 * a ** 4 * b ** 3 / (5 * a * b), 2 * a ** 3 * b ** 2)


def law3(ch):
    f = flow(ch)
    sec(f, "A power of a power: groups of groups", room=300)
    rule_box(f, "powers of powers and of brackets", [
        "$(a^m)^n=a^{mn}$: {B:multiply} the powers.",
        "A power outside a bracket applies to {B:every factor inside}: $(ab)^n=a^nb^n$ and "
        "$\\left(\\dfrac ab\\right)^n=\\dfrac{a^n}{b^n}$.",
        "That includes the number in front: $(2x^3)^2=2^2x^6=4x^6$, {R:not} $2x^6$.",
    ], C.BLUE)
    f.p("Why? $(x^2)^3$ means three copies of $x^2$. Each copy is a pair of x's, so count the pairs:",
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
    ch.formula(r"(a^m)^n=a^{mn}", "power of a power")
    f.p("{b:Brackets with several things inside} (the last two laws on your slides). The power "
        "applies to {B:everything} in the bracket:", 14, gap=6)
    step(f, r"(xy)^3=xy\times xy\times xy=x^3y^3", "rearrange: all x's together, all y's together", size=19)
    step(f, r"\left(\frac{x}{y}\right)^3=\frac{x}{y}\times\frac{x}{y}\times\frac{x}{y}=\frac{x^3}{y^3}",
         "top × top, bottom × bottom", size=19)
    step(f, r"(2x)^3=8x^3", "the 2 gets cubed too! (2³ = 8)", size=19, color=C.GREEN)
    step(f, r"(2x^3)^2=2^2\times x^{3\times2}=4x^6", "square the 2; multiply the powers", size=19,
         color=C.GREEN)
    step(f, r"(-3a^2b)^3=(-3)^3a^6b^3=-27a^6b^3", "odd power of −3 stays negative", size=19,
         color=C.GREEN)
    ch.formula(r"(ab)^n=a^nb^n", "power of a product")
    ch.check(sp.expand((2 * x) ** 3), 8 * x ** 3)
    ch.check((2 * x ** 3) ** 2, 4 * x ** 6)
    ch.check((-3 * a ** 2 * b) ** 3, -27 * a ** 6 * b ** 3)


def staircase(ch):
    f = flow(ch)
    sec(f, "The staircase: zero and negative powers", room=480)
    rule_box(f, "zero and negative powers", [
        "$a^0=1$ for any $a\\neq0$.",
        "$a^{-n}=\\dfrac{1}{a^n}$: a negative power means {B:one over} (the reciprocal). It does "
        "{B:not} make the answer negative: $2^{-3}=\\frac18$.",
        "Turned the other way: $\\dfrac{1}{a^{-n}}=a^n$, so $\\dfrac{1}{x^{-2}}=x^2$. A power can move "
        "between top and bottom of a fraction by changing its sign.",
        "For a fraction, flip it and make the power positive: $\\left(\\dfrac ab\\right)^{-n}="
        "\\left(\\dfrac ba\\right)^n$.",
    ], C.BLUE)
    f.p("Why? What could $2^0$ or $2^{-1}$ possibly mean? \"Zero copies of 2 multiplied\"? Walk down a "
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
        "over 1, so $8 = \\frac81$ flips to $\\frac18$ (Chapter 2, \"Dividing\"). Read the "
        "staircase: $2^{-3}$ is $2^3 = 8$ flipped, which is $\\frac18$.", 14, gap=6)
    ch.formula(r"a^0=1", "zero power")
    ch.formula(r"a^{-n}=\frac1{a^n}", "negative power")
    step(f, r"\frac{1}{x^{-2}}=\frac{1}{\;\frac{1}{x^2}\;}=x^2", "one over a reciprocal flips it back",
         size=19, color=C.GREEN)
    step(f, r"\left(\frac23\right)^{-2}=\left(\frac32\right)^2=\frac94", "flip, then square", size=19,
         color=C.GREEN)
    step(f, r"5x^{-3}=\frac{5}{x^3}", "only the x has the power; the 5 stays on top", size=19,
         color=C.GREEN)
    ch.check(1 / x ** -2, x ** 2)
    ch.check(sp.Rational(2, 3) ** -2, sp.Rational(9, 4))
    ch.check(5 * x ** -3, 5 / x ** 3)
    f.p("{b:The dividing law agrees}, which is how we know the staircase isn't a trick: "
        "$\\frac{x^3}{x^3} = x^{3-3} = x^0$, but anything divided by itself is 1. And "
        "$\\frac{x^2}{x^3} = x^{-1}$, but cancelling leaves $\\frac{1}{x}$.", 14, gap=8)
    f.p("{R:A negative power does NOT make the number negative:} $2^{-3} = \\frac18$, a small "
        "positive number.", 13.5)


def fractional(ch):
    f = flow(ch)
    sec(f, "Fraction powers are roots", room=460)
    rule_box(f, "fraction powers", [
        "$a^{\\frac1n}=\\sqrt[n]{a}$: the {B:bottom} of the fraction is the {B:root}.",
        "$a^{\\frac mn}=\\left(\\sqrt[n]{a}\\right)^m=\\sqrt[n]{a^m}$: the {B:top} is an ordinary {B:power}.",
    ], C.BLUE)
    rule_box(f, "evaluating a (negative) fraction power", [
        "If the power is negative, write one over the same thing with a positive power.",
        "Take the root given by the bottom number $n$ (smaller numbers this way round).",
        "Raise to the power given by the top number $m$.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    f.p("Why? What would $9^{\\frac12}$ mean? Use the power-of-a-power law as a detective. Square it:", 14, gap=6)
    step(f, r"\left(9^{\frac12}\right)^2=9^{\frac12\times2}=9^1=9", "powers multiply: ½ × 2 = 1", size=19)
    step(f, r"\text{so }9^{\frac12}\text{ is the number whose square is 9}", "that's the definition of √", size=17)
    step(f, r"9^{\frac12}=\sqrt9=3", "", size=19, color=C.GREEN)
    ch.check(sp.Integer(9) ** sp.Rational(1, 2), 3)
    f.p("That is the rule in the box: the bottom of the fraction is the root, the top an ordinary power.",
        14, gap=6)
    ch.formula(r"a^{\frac mn}=\left(\sqrt[n]{a}\right)^m", "fractional power")
    step(f, r"8^{\frac23}=\left(\sqrt[3]8\right)^2=2^2=4", "root first (cube root of 8 is 2), then square", size=19)
    step(f, r"16^{-\frac12}=\frac{1}{\sqrt{16}}=\frac14", "minus: one over. Half: square root.", size=19)
    ch.check(sp.Integer(8) ** sp.Rational(2, 3), 4)
    step(f, r"27^{-\frac23}=\frac{1}{27^{\frac23}}=\frac{1}{\left(\sqrt[3]{27}\right)^2}=\frac{1}{3^2}=\frac19",
         "the procedure: flip, root, power", size=18)
    ch.check(sp.Integer(16) ** sp.Rational(-1, 2), sp.Rational(1, 4))
    ch.check(sp.Integer(27) ** sp.Rational(-2, 3), sp.Rational(1, 9))
    f.p("{h:Why roots first?} Smaller numbers: $(\\sqrt[3]{8})^2 = 2^2$ is easier than "
        "$\\sqrt[3]{64}$ (same answer, 4).", 13.5, C.BROWN)


def all_laws(ch):
    f = flow(ch)
    sec(f, "All the index laws in one table", room=560)
    f.p("Every law in this chapter, with one example each. Learn the table; the rest of the chapter "
        "explains where each line comes from.", 13.5, gap=8)
    rules_table(f, ["Law", "Rule", "Example"], [
        ["Multiplying", "$a^m\\times a^n=a^{m+n}$", "$x^2\\times x^3=x^5$"],
        ["Dividing", "$a^m\\div a^n=a^{m-n}$", "$x^7\\div x^3=x^4$"],
        ["Power of a power", "$(a^m)^n=a^{mn}$", "$(x^2)^3=x^6$"],
        ["Zero power", "$a^0=1\\quad(a\\neq0)$", "$5^0=1$"],
        ["Negative power", "$a^{-n}=\\dfrac{1}{a^n}$", "$2^{-3}=\\dfrac18$"],
        ["One over a negative power", "$\\dfrac{1}{a^{-n}}=a^n$", "$\\dfrac{1}{x^{-2}}=x^2$"],
        ["Root", "$a^{\\frac1n}=\\sqrt[n]{a}$", "$8^{\\frac13}=\\sqrt[3]{8}=2$"],
        ["Fraction power", "$a^{\\frac mn}=\\left(\\sqrt[n]{a}\\right)^m$", "$8^{\\frac23}=2^2=4$"],
        ["Power of a product", "$(ab)^n=a^nb^n$", "$(2x^3)^2=4x^6$"],
        ["Power of a fraction", "$\\left(\\dfrac ab\\right)^n=\\dfrac{a^n}{b^n}$",
         "$\\left(\\dfrac x3\\right)^2=\\dfrac{x^2}{9}$"],
        ["Negative power of a fraction", "$\\left(\\dfrac ab\\right)^{-n}=\\left(\\dfrac ba\\right)^n$",
         "$\\left(\\dfrac23\\right)^{-2}=\\dfrac94$"],
    ], widths=[150, 175, 170], color=C.BLUE)
    I = sp.Integer
    ch.check(x ** 7 / x ** 3, x ** 4)
    ch.check(I(5) ** 0, 1)
    ch.check(I(8) ** sp.Rational(1, 3), 2)
    ch.check((x / 3) ** 2, x ** 2 / 9)
    rule_box(f, "when the laws apply", [
        "The first three laws need the {B:same base}. $2^3\\times2^4=2^7$, but $2^3\\times3^4$ can only be "
        "worked out as numbers ($8\\times81$). Never multiply the bases: $2^3\\times2^4$ is not $4^7$.",
        "There are {B:no laws for adding}: $x^2+x^3$ and $2^3+2^4$ stay as they are (or are worked out as numbers).",
        "Coefficients are ordinary numbers: multiply or divide them separately, but a bracket's power "
        "applies to them too.",
    ], C.BLUE)
    ch.check(I(2) ** 3 * I(2) ** 4, I(2) ** 7)
    ch.check_true(I(2) ** 3 * I(2) ** 4 != I(4) ** 7)


def solve_powers(ch):
    f = flow(ch)
    sec(f, "Find the unknown: equations with a power", room=320)
    f.p("Exam questions often give you the answer and hide the power (or the base). Two rules handle "
        "almost all of them:", 13.5, gap=6)
    rule_box(f, "unknown power: make the bases match", [
        "Write both sides as powers of the {B:same base}: $\\frac19=3^{-2}$, $32=2^5$, $4=2^2$, $8=2^3$.",
        "If $a^p=a^q$ (same base, not 0, 1 or −1), then the powers are equal: $p=q$.",
        "Solve that ordinary equation, then check in the original.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    rule_box(f, "unknown base: undo the power", [
        "If $x^{\\frac mn}=c$, raise both sides to the {B:flipped} power $\\frac nm$: "
        "$x=c^{\\frac nm}$, because $\\left(x^{\\frac mn}\\right)^{\\frac nm}=x^1$.",
    ], C.BLUE)
    ex(f, "solve $3^n=\\frac19$.")
    step(f, r"\frac19=\frac{1}{3^2}=3^{-2}", "write 1/9 as a power of 3", size=19)
    step(f, r"3^n=3^{-2}\ \Rightarrow\ n=-2", "same base: powers equal", size=19, color=C.GREEN)
    ch.check(solve1(3 ** uk - sp.Rational(1, 9)), -2)
    ex(f, "solve $2^x=32$.")
    step(f, r"2^x=2^5\ \Rightarrow\ x=5", "2 × 2 × 2 × 2 × 2 = 32", size=19, color=C.GREEN)
    ch.check(solve1(2 ** uk - 32), 5)
    ex(f, "solve $4^x=8$. (4 and 8 are both powers of 2.)")
    step(f, r"(2^2)^x=2^3", "4 = 2², 8 = 2³", size=19)
    step(f, r"2^{2x}=2^3", "power of a power: multiply", size=19)
    step(f, r"2x=3\ \Rightarrow\ x=\tfrac32", "powers equal", size=19, color=C.GREEN)
    ch.check(solve1(4 ** uk - 8), sp.Rational(3, 2))
    f.p("Check: $4^{\\frac32}=(\\sqrt4)^3=2^3=8$ ✓.", 13.5, C.GREEN, gap=8)
    ex(f, "solve $x^{\\frac32}=8$.")
    step(f, r"x=8^{\frac23}", "raise both sides to the flipped power 2/3", size=19)
    step(f, r"x=\left(\sqrt[3]8\right)^2=2^2=4", "root first, then square", size=19, color=C.GREEN)
    ch.check(sp.Integer(8) ** sp.Rational(2, 3), 4)
    ch.check(sp.Integer(4) ** sp.Rational(3, 2), 8)
    ex(f, "find $k$ if $x^k\\times x^3=x^{10}$.")
    step(f, r"x^{k+3}=x^{10}\ \Rightarrow\ k+3=10\ \Rightarrow\ k=7", "first law, then match powers",
         size=19, color=C.GREEN)
    ch.check(solve1(uk + 3 - 10), 7)
    ex(f, "solve $5^{x+1}=125$.")
    step(f, r"5^{x+1}=5^3\ \Rightarrow\ x+1=3\ \Rightarrow\ x=2", "125 = 5³", size=19, color=C.GREEN)
    ch.check(solve1(5 ** (uk + 1) - 125), 2)


def mistakes(ch):
    f = flow(ch)
    sec(f, "Test before you trust: four famous mistakes", room=380)
    f.p("The square-root one is on Lecture 2's \"common mistakes\" slide; the other three are just as "
        "common. Each one is caught instantly by trying small numbers:", 14, gap=8)
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
    f.gap(6)
    wrong_right(f, [
        (r"2^3\times2^4=4^7", r"2^3\times2^4=2^7", "same base: keep the base, add the powers"),
        (r"(2x^3)^2=2x^6", r"(2x^3)^2=4x^6", "the bracket's power applies to the 2 as well"),
        (r"3^{-2}=-9", r"3^{-2}=\frac19", "a negative power means one over, not a negative answer"),
        (r"-3^2=9", r"-3^2=-9,\ \ (-3)^2=9", "without brackets the power touches only the 3"),
        (r"x^6\div x^2=x^3", r"x^6\div x^2=x^4", "dividing subtracts the powers; it doesn't divide them"),
        (r"x^0=0", r"x^0=1", "anything (except 0) to the power 0 is 1"),
    ])
    ch.check(sp.Integer(3) ** -2, sp.Rational(1, 9))
    ch.check(x ** 6 / x ** 2, x ** 4)


def standard_form(ch):
    f = flow(ch)
    sec(f, "Standard form: KB, MB, GB and tiny things", room=480)
    rule_box(f, "standard form", [
        "A number in standard form is $a\\times10^n$ with $1\\le a<10$ and $n$ a whole number "
        "(positive, negative or zero).",
        "Numbers $\\ge10$ have a positive power; numbers between 0 and 1 have a negative power; "
        "numbers from 1 to 9.99... have power 0.",
    ], C.BLUE)
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
        "the power. {B:Digits slid left} (the number was small, less than 1) → {B:negative} power. "
        "Digits slid right (the number was big) → positive power.", 14, gap=6)
    step(f, r"0.0024\ \to\ 2.4", "digits slide 3 places left, so the dot seems to move right", size=18)
    step(f, r"0.0024=2.4\times10^{-3}", "× 10⁻³ (÷ 1000) puts it back", size=19, color=C.GREEN)
    f.p("{R:Slide note:} Lecture 7 writes $1 \\le a \\le 10$; it should be $1 \\le a < 10$. The number "
        "10 itself is written $1 \\times 10^1$, never $10 \\times 10^0$.", 13.5, gap=8)
    f.p("{b:Multiplying in standard form} uses the first law on the powers of 10: "
        "$(3 \\times 10^4) \\times (2 \\times 10^5) = 6 \\times 10^{9}$. Calculators show "
        "$2.4 \\times 10^{-3}$ as 2.4E-3 (E for exponent).", 14)
    ch.check((3 * 10 ** 4) * (2 * 10 ** 5), 6 * 10 ** 9)


def standard_form_calc(ch):
    f = flow(ch)
    sec(f, "Calculating in standard form", room=520)
    rule_box(f, "multiplying and dividing", [
        "Multiply (or divide) the front numbers.",
        "Add the powers of 10 when multiplying; subtract them when dividing.",
        "{B:Re-normalise}: if the front number is 10 or more, divide it by 10 and add 1 to the power "
        "($20\\times10^5=2\\times10^6$); if it is less than 1, multiply it by 10 and take 1 off the "
        "power ($0.5\\times10^3=5\\times10^2$).",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    rule_box(f, "adding and subtracting", [
        "Rewrite the numbers with the {B:same power of 10} first (or write them out in full).",
        "Add or subtract the front numbers; keep the power.",
        "Re-normalise if needed.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    ex(f, "$(6\\times10^5)\\times(5\\times10^3)$.")
    step(f, r"(6\times5)\times10^{5+3}=30\times10^8", "multiply fronts, add powers", size=19)
    step(f, r"=3\times10^9", "30 is too big: 30 = 3 × 10¹, so add 1 to the power", size=19, color=C.GREEN)
    ch.check(6 * 10 ** 5 * 5 * 10 ** 3, 3 * 10 ** 9)
    ex(f, "$(8\\times10^7)\\div(2\\times10^3)$.")
    step(f, r"\frac82\times10^{7-3}=4\times10^4", "divide fronts, subtract powers", size=19, color=C.GREEN)
    ch.check(sp.Rational(8 * 10 ** 7, 2 * 10 ** 3), 4 * 10 ** 4)
    ex(f, "$(3\\times10^4)\\div(6\\times10^{-2})$.")
    step(f, r"\frac36\times10^{4-(-2)}=0.5\times10^6", "4 − (−2) = 6", size=19)
    step(f, r"=5\times10^5", "0.5 is less than 1: × 10 and take 1 off the power", size=19, color=C.GREEN)
    ch.check(sp.Rational(3 * 10 ** 4) / (6 * sp.Rational(1, 100)), 5 * 10 ** 5)
    ex(f, "$(3\\times10^4)+(5\\times10^3)$.")
    step(f, r"3\times10^4+0.5\times10^4", "5 × 10³ = 0.5 × 10⁴: same power now", size=19)
    step(f, r"=3.5\times10^4", "add the fronts, keep the power", size=19, color=C.GREEN)
    ch.check(3 * 10 ** 4 + 5 * 10 ** 3, sp.Rational(35, 10) * 10 ** 4)
    f.p("Check by writing them out: $30\\,000 + 5000 = 35\\,000$ ✓. {R:Never} add the powers when "
        "adding: $3\\times10^4+5\\times10^3$ is not $8\\times10^7$.", 13.5, gap=8)
    ex(f, "$(7.2\\times10^{-3})-(4\\times10^{-4})$.")
    step(f, r"7.2\times10^{-3}-0.4\times10^{-3}=6.8\times10^{-3}", "4 × 10⁻⁴ = 0.4 × 10⁻³", size=19,
         color=C.GREEN)
    ch.check(sp.Rational(72, 10) * sp.Rational(1, 1000) - 4 * sp.Rational(1, 10 ** 4),
             sp.Rational(68, 10) * sp.Rational(1, 1000))


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Power", r"a^n=a\times a\times\cdots\times a", "$n$ copies of $a$; $a^1=a$"),
        ("Multiplying", r"a^m\times a^n=a^{m+n}", "same base only; coefficients multiply"),
        ("Dividing", r"\frac{a^m}{a^n}=a^{m-n}", "same base only; coefficients divide"),
        ("Power of a power", r"(a^m)^n=a^{mn}", None),
        ("Brackets", r"(ab)^n=a^nb^n,\quad\left(\frac ab\right)^n=\frac{a^n}{b^n}", "the number in front is raised too: $(2x^3)^2=4x^6$"),
        ("Zero power", r"a^0=1\quad(a\neq0)", None),
        ("Negative power", r"a^{-n}=\frac{1}{a^n},\quad\frac{1}{a^{-n}}=a^n", "one over; never a negative answer"),
        ("Negative power of a fraction", r"\left(\frac ab\right)^{-n}=\left(\frac ba\right)^n", None),
        ("Fraction power", r"a^{\frac1n}=\sqrt[n]{a},\quad a^{\frac mn}=\left(\sqrt[n]{a}\right)^m", "bottom = root, top = power"),
        ("Negative base", r"(-2)^4=16,\ (-2)^3=-8,\ -3^2=-9", "even power positive, odd power negative"),
        ("Roots of negatives", r"\sqrt[3]{-8}=-2", "odd roots fine; even roots don't exist (real numbers)"),
        ("No adding law", None, "$x^2+x^3$ and $(a+b)^2$ don't follow the index laws"),
        ("Unknown power", r"a^p=a^q\Rightarrow p=q", "write both sides as powers of the same base"),
        ("Unknown base", r"x^{\frac mn}=c\Rightarrow x=c^{\frac nm}", None),
        ("Standard form", r"a\times10^n,\quad1\le a<10", "× / ÷: fronts, then powers, then re-normalise"),
        ("Adding in standard form", None, "make the powers of 10 equal first, then add the fronts"),
    ], C.BLUE)


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
        ("Coefficients and negatives", ["6x⁵ ÷ 2x²", "(2x³)²", "12a⁶b² ÷ 4a²b", "(−2)⁵", "−2⁴",
                                        "∛(−27)", "1/x⁻³", "(3/4)⁻²"],
         "19. 3x³   20. 4x⁶   21. 3a⁴b   22. −32   23. −16   24. −3   25. x³   26. 16/9"),
        ("Calculating in standard form", ["(6 × 10⁵) × (5 × 10³)", "(9 × 10⁸) ÷ (3 × 10⁻²)",
                                          "(4 × 10³) + (2 × 10²)", "Write 25 × 10⁴ in standard form"],
         "27. 3 × 10⁹   28. 3 × 10¹⁰   29. 4.2 × 10³   30. 2.5 × 10⁵"),
        ("Find the unknown", ["3ⁿ = 1/9", "2ˣ = 32", "4ˣ = 8", "x^(3/2) = 8", "xᵏ × x³ = x¹⁰", "5^(x+1) = 125"],
         "31. n = −2 (1/9 = 3⁻²)   32. x = 5 (32 = 2⁵)   33. x = 3/2 (2²ˣ = 2³)   34. x = 4 (x = 8^(2/3))   "
         "35. k = 7 (k + 3 = 10)   36. x = 2 (125 = 5³, x + 1 = 3)"),
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
    for g, e in [(6 * x ** 5 / (2 * x ** 2), 3 * x ** 3), ((2 * x ** 3) ** 2, 4 * x ** 6),
                 (12 * a ** 6 * b ** 2 / (4 * a ** 2 * b), 3 * a ** 4 * b), (I(-2) ** 5, -32), (-I(2) ** 4, -16),
                 (sp.real_root(-27, 3), -3), (1 / x ** -3, x ** 3), (sp.Rational(3, 4) ** -2, sp.Rational(16, 9))]:
        ch.check(g, e)
    ch.check(6 * 10 ** 5 * 5 * 10 ** 3, 3 * 10 ** 9)
    ch.check(sp.Integer(9 * 10 ** 8) / (3 * sp.Rational(1, 100)), 3 * 10 ** 10)
    ch.check(4 * 10 ** 3 + 2 * 10 ** 2, sp.Rational(42, 10) * 10 ** 3)
    ch.check(25 * 10 ** 4, sp.Rational(25, 10) * 10 ** 5)
    ch.check(solve1(3 ** uk - sp.Rational(1, 9)), -2)
    ch.check(solve1(2 ** uk - 32), 5)
    ch.check(solve1(4 ** uk - 8), sp.Rational(3, 2))
    ch.check(solve1(uk ** sp.Rational(3, 2) - 8), 4)
    ch.check(solve1(uk + 3 - 10), 7)
    ch.check(solve1(5 ** (uk + 1) - 125), 2)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    what(ch)
    roots(ch)
    negatives(ch)
    laws(ch)
    law2(ch)
    law3(ch)
    staircase(ch)
    fractional(ch)
    all_laws(ch)
    solve_powers(ch)
    mistakes(ch)
    standard_form(ch)
    standard_form_calc(ch)
    summary(ch)
    your_turn(ch)
