"""Chapter 13 - Algebraic fractions. Chapter 2's three formulas with letters in, then each rule boxed
before its examples. Twin columns put every move with
numbers beside the same move with letters. 'Glued' (×) versus 'loose' (+) decides what may be
cancelled; the lowest common denominator, fractions inside fractions, and equations with fractions."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import (L, R, W, flow, go, mistakes, rule_box, rules_page, rules_table, section, step,
                         title_block)

ORDER = 13
NUM = 13
TITLE = "Algebraic fractions"
SHORT = "Algebraic fractions"
SLUG = "Algebraic-fractions"
ACCENT = C.TEAL
REQUIRES = ["fraction", "numerator-denominator", "simplify-fraction", "add-fractions", "subtract-fractions",
            "multiply-fractions", "divide-fractions", "reciprocal", "lcm", "factorise-common-factor",
            "factorise-quadratic", "expand-brackets", "substitution", "variable", "roots"]
INTRODUCES = ["algebraic-fractions", "cancel-factors", "common-denominator", "undefined-denominator",
              "lowest-common-denominator", "complex-fractions"]

PAPER = "#fafefe"
x, y, a, b, c, d = sp.symbols("x y a b c d")
MID = L + W / 2


def icon(pg, x0, y0):
    pg.line(x0 + 2, y0 + 9, x0 + 16, y0 + 9, C.TEAL, 1.6)
    pg.dot(x0 + 9, y0 + 4, 2.2, C.TEAL)
    pg.dot(x0 + 9, y0 + 14, 2.2, C.TEAL)


def sec(f, t, **kw):
    section(f, t, C.TEAL, icon, **kw)


def twin_head(f, left="with numbers", right="with letters"):
    y_ = f.reserve(26)
    pg = f.pg
    pg.rect(L, y_, W / 2 - 4, 22, C.ORANGE, 1, fillcolor=C.LIGHT[C.ORANGE], r=5)
    pg.rect(MID + 4, y_, W / 2 - 4, 22, C.TEAL, 1, fillcolor=C.LIGHT[C.TEAL], r=5)
    pg.text(L + W / 4, y_ + 3, left, 12.5, C.ORANGE, F.BOLD, align="center")
    pg.text(MID + W / 4, y_ + 3, right, 12.5, C.TEAL, F.BOLD, align="center")


def twin(f, left, right, why=None, size=18, col=C.INK):
    """One row: the number version and the letter version side by side, same move."""
    pg = f.pg
    hl = pg.eq_size(left, size)[1]
    hr = pg.eq_size(right, size)[1]
    h = max(hl, hr)
    nh = F.line_h(F.HAND, 15) + 2 if why else 0
    y_ = f.reserve(h + nh + 10)
    pg = f.pg
    pg.line(MID, y_ - 4, MID, y_ + h + nh + 6, C.GREY, 0.6, dash=(2, 3))
    pg.eq(L + W / 4, y_ + (h - hl) / 2, left, size, col, align="center")
    pg.eq(MID + W / 4, y_ + (h - hr) / 2, right, size, col, align="center")
    if why:
        pg.note(MID, y_ + h + 1, why, C.RED, 15, w=W / 2, align="center", solid=False)


def chips(pg, x0, y0, items, crossed=(), size=16):
    """A row of 'atom' tiles. items: latex strings, with '*' meaning glued (×) and '+' loose."""
    xx = x0
    spots = []
    for i, it in enumerate(items):
        if it == "*":
            pg.rect(xx - 3, y0 + 11, 10, 6, C.TEAL, 0.8, fillcolor=C.TEAL)
            xx += 4
            continue
        if it == "+":
            pg.eq(xx + 8, y0 + 14, r"+", size, C.GREY, align="center", valign="middle")
            xx += 16
            continue
        w_, _, _ = pg.eq_size(it, size)
        bw = max(26, w_ + 12)
        pg.rect(xx, y0, bw, 28, C.TEAL, 1.1, fillcolor="#ffffff", r=5)
        pg.eq(xx + bw / 2, y0 + 14, it, size, C.INK, align="center", valign="middle")
        if i in crossed:
            pg.line(xx + 3, y0 + 25, xx + bw - 3, y0 + 3, C.RED, 1.6)
        spots.append((xx, bw))
        xx += bw
    return xx - x0


def chip_frac(pg, x0, y0, top, bot, ctop=(), cbot=(), size=16):
    """A fraction built from atom rows; returns the total width."""
    wt = _row_w(pg, top, size)
    wb = _row_w(pg, bot, size)
    wmax = max(wt, wb)
    chips(pg, x0 + (wmax - wt) / 2, y0, top, ctop, size)
    pg.line(x0 - 4, y0 + 36, x0 + wmax + 4, y0 + 36, C.INK, 1.6)
    chips(pg, x0 + (wmax - wb) / 2, y0 + 44, bot, cbot, size)
    return wmax


def _row_w(pg, items, size):
    t = 0
    for it in items:
        if it == "*":
            t += 4
        elif it == "+":
            t += 16
        else:
            t += max(26, pg.eq_size(it, size)[0] + 12)
    return t


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 13, "Algebraic fractions", "nothing new: the same fraction moves, "
                     "done twice side by side", C.TEAL, PAPER)
    y0 = 214
    pg.rect(L + 20, y0, 200, 110, C.ORANGE, 1.3, fillcolor="#fffaf2", r=8)
    pg.rect(L + 270, y0, 200, 110, C.TEAL, 1.3, fillcolor="#f2fbfb", r=8)
    pg.text(L + 120, y0 + 8, "numbers", 13, C.ORANGE, F.BOLD, align="center")
    pg.text(L + 370, y0 + 8, "letters", 13, C.TEAL, F.BOLD, align="center")
    pg.eq(L + 120, y0 + 66, r"\frac23+\frac45=\frac{2\cdot5+3\cdot4}{3\cdot5}", 16, align="center",
          valign="middle")
    pg.eq(L + 370, y0 + 66, r"\frac ab+\frac cd=\frac{ad+bc}{bd}", 18, align="center", valign="middle")
    pg.arrow(L + 226, y0 + 60, L + 264, y0 + 60, C.GREY, 1.3, head=5)
    pg.note(L + 150, y0 + 118, "identical moves, the letters just sit where the numbers were", C.TEAL, 17)
    f = ch.flow(top=380)
    f.p("An {B:algebraic fraction} is a fraction with letters in it, like $\\frac{3}{x}$ or "
        "$\\frac{x+1}{x-2}$. That's the only difference from Chapter 2, so the {B:rules are Chapter 2's "
        "rules}: the same three formulas for add/subtract, multiply and divide, and each section "
        "states its rule in a box before any example. Many moves are shown in {B:two columns}: numbers you "
        "already trust on the left, the same move with letters on the right.", 14, gap=10)
    f.p("One new idea does most of the work here: which parts of a fraction are {B:glued} together "
        "(multiplied) and which are only {B:loose} (added). You may cancel glued parts, and must never "
        "cancel loose ones.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 1} {y:(combining fractions) and} {B:Lecture 2} "
        "{y:(common mistakes, the 1/x = 2/y − 3/z example).}", 12.5)


def what(ch):
    f = flow(ch)
    sec(f, "Letters in a fraction, and the one number it hates")
    f.p("$\\frac{x+1}{x-2}$ means {B:(the whole top) ÷ (the whole bottom)}. The fraction bar acts like "
        "a pair of brackets around the top and another around the bottom:", 14, gap=6)
    step(f, r"\frac{x+1}{x-2}=(x+1)\div(x-2)", "the bar groups each part", size=19)
    f.p("To get a value, substitute (Chapter 8). With $x = 4$: $\\frac{4+1}{4-2} = \\frac52 = 2.5$.",
        14, gap=8)
    ch.check(sp.Rational(4 + 1, 4 - 2), sp.Rational(5, 2))
    f.p("{R:The one number it hates.} With $x = 2$ the bottom becomes $2 - 2 = 0$, and dividing by "
        "zero means nothing (Chapter 1: share 3 sweets among 0 people?). So this fraction only "
        "makes sense when $x \\neq 2$. Whenever a letter sits on the bottom, ask: {B:which value makes "
        "the bottom zero?} That value is banned.", 14, gap=8)
    ch.term("algebraic fraction", "a fraction with letters in the top, bottom or both, e.g. 3/x or (x + 1)/(x − 2)")
    ch.term("undefined", "has no value; a fraction is undefined when its bottom equals 0")
    y_ = f.reserve(70)
    pg = f.pg
    for i, (fr, ban) in enumerate([(r"\frac3x", r"x\ne0"), (r"\frac{5}{x+4}", r"x\ne-4"),
                                    (r"\frac{x}{(x-1)(x+3)}", r"x\ne1,\ x\ne-3")]):
        cx = L + 80 + i * 165
        pg.eq(cx, y_ + 2, fr, 18, align="center")
        pg.eq(cx, y_ + 50, ban, 14, C.RED, align="center")
    ch.check(sp.solve((x - 1) * (x + 3), x), [-3, 1])


def at_a_glance(ch):
    f = flow(ch)
    sec(f, "The three formulas, with letters", room=520)
    f.p("Exactly Chapter 2's formulas. Now $a$, $b$, $c$, $d$ can be expressions like $x+1$; put each one "
        "in {B:brackets} when you plug it in.", 13.5, gap=8)
    rules_table(f, ["Operation", "Formula", "Example with letters"], [
        ["{B:Add / subtract}", "$\\dfrac ab\\pm\\dfrac cd=\\dfrac{ad\\pm bc}{bd}$",
         "$\\tfrac3x-\\tfrac2y=\\tfrac{3y-2x}{xy}$"],
        ["{B:Multiply}", "$\\dfrac ab\\times\\dfrac cd=\\dfrac{ac}{bd}$",
         "$\\tfrac{x+1}{x}\\times\\tfrac{x^2}{x+1}=\\tfrac{(x+1)x^2}{x(x+1)}=x$"],
        ["{B:Divide}", "$\\dfrac ab\\div\\dfrac cd=\\dfrac{ad}{bc}$",
         "$\\tfrac x4\\div\\tfrac{x^2}6=\\tfrac{6x}{4x^2}=\\tfrac3{2x}$"],
    ], [92, 170, 233], C.TEAL)
    ch.check(sp.simplify(3 / x - 2 / y - (3 * y - 2 * x) / (x * y)), 0)
    ch.check(sp.cancel((x + 1) / x * x ** 2 / (x + 1)), x)
    ch.check(sp.cancel((x / 4) / (x ** 2 / 6)), 3 / (2 * x))
    rule_box(f, "what's new with letters", [
        "{B:Brackets:} in $ad-bc$, $b$ and $c$ may be whole expressions; the minus applies to all of $bc$.",
        "{B:Banned values:} any value that makes a bottom zero is not allowed.",
        "{B:Tidying the answer:} factorise top and bottom, then cancel common {B:factors} (never terms): "
        "$\\frac{x^2+3x}{x+3}=\\frac{x(x+3)}{x+3}=x$.",
    ], C.TEAL)
    ch.check(sp.cancel((x ** 2 + 3 * x) / (x + 3)), x)


def cancel(ch):
    f = flow(ch)
    sec(f, "Cancelling: only glued parts come off", room=500)
    rule_box(f, "simplifying (cancelling)", [
        "{B:Factorise the top and the bottom completely first.}",
        "Cancel a factor only if it {B:multiplies the whole top and the whole bottom}. Cancel factors, "
        "{R:never terms}: in $\\frac{x+3}{3}$ the 3s do not cancel.",
        "A banned value of the original fraction stays banned after cancelling.",
    ], C.TEAL)
    f.p("Simplifying a fraction means dividing top and bottom by the {B:same thing}. Break both into "
        "atoms (as in Chapter 12) and cross out matching pairs:", 14, gap=6)
    twin_head(f)
    twin(f, r"\frac{12}{18}=\frac{2\cdot\cancel{6}}{3\cdot\cancel{6}}=\frac23",
         r"\frac{6x}{9x^2}=\frac{2\cdot\cancel{3x}}{3x\cdot\cancel{3x}}=\frac{2}{3x}", "the same 6 (or 3x) on top and bottom")
    ch.check(sp.cancel(6 * x / (9 * x ** 2)), 2 / (3 * x))
    f.p("Here's the {B:glue} picture. The teal bars mean \"multiplied\", so those atoms are stuck to "
        "the whole top or the whole bottom. Dividing top and bottom by one of them is fine:", 14, gap=10)
    y_ = f.reserve(94)
    pg = f.pg
    chip_frac(pg, L + 20, y_, ["2", "*", "3", "*", "x"], ["3", "*", "3", "*", "x", "*", "x"],
              ctop=(2, 4), cbot=(0, 4))
    pg.note(L + 220, y_ + 8, "every atom is glued (×)\nso a matching pair can be\nlifted off: left with 2/(3x) ✓",
            C.GREEN, 15)
    f.p("Now a {B:loose} part. Can the 3s in $\\frac{x+3}{3}$ cancel?", 14, gap=10)
    y_ = f.reserve(94)
    pg = f.pg
    chip_frac(pg, L + 20, y_, ["x", "+", "3"], ["3"], ctop=(2,), cbot=(0,))
    pg.xmark(L + 120, y_ + 30, 18)
    pg.note(L + 150, y_ + 4, "NO. The top 3 is only added on (loose).\nIt isn't multiplying the whole "
            "top.\nTest x = 6:  (6 + 3)/3 = 3,  but \"x\" = 6  ✗", C.RED, 15)
    ch.check(sp.Rational(6 + 3, 3), 3)
    f.p("{B:Fix: factorise first, to turn loose parts into glued ones.}", 14, gap=6)
    twin_head(f)
    twin(f, r"\frac{6+9}{3}=\frac{3(2+3)}{3}=5", r"\frac{x^2+3x}{x+3}=\frac{x\cancel{(x+3)}}{\cancel{(x+3)}}=x",
         "factorise the top: now (x + 3) is glued on")
    ch.check(sp.cancel((x ** 2 + 3 * x) / (x + 3)), x)
    twin(f, r"\frac{15}{20}=\frac{3\cdot\cancel5}{4\cdot\cancel5}",
         r"\frac{x^2-9}{x^2+x-6}=\frac{(x-3)\cancel{(x+3)}}{(x-2)\cancel{(x+3)}}",
         "top: squares;  bottom: Δ = 25, pair 3, −2", size=16)
    twin(f, r"=\frac34", r"=\frac{x-3}{x-2}", col=C.GREEN)
    ch.check(sp.cancel((x ** 2 - 9) / (x ** 2 + x - 6)), (x - 3) / (x - 2))
    f.p("{h:Rule of thumb:} if there's a + or − showing on the top or bottom, factorise before "
        "you cancel anything.", 13.5, C.BROWN, gap=12)

    f.need(330)
    f.p("{R:Cancelling doesn't un-ban a number.} Take $\\frac{x^2-1}{x-1}$. The top is a difference of "
        "squares, so it cancels:", 14, gap=6)
    step(f, r"\frac{x^2-1}{x-1}=\frac{(x+1)\cancel{(x-1)}}{\cancel{(x-1)}}=x+1", "", size=19)
    ch.check(sp.cancel((x ** 2 - 1) / (x - 1)), x + 1)
    go(f, "The original fraction still has x − 1 on the bottom. Which x is banned? On the line "
          "y = x + 1, mark the one point the fraction can't give.")
    y_ = f.reserve(196)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 24, 220, 150, (-2.5, 3), (-1.5, 4.2))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 1)
    ax.curve(lambda t: t + 1, -2.4, 0.93, C.TEAL, 2.2)
    ax.curve(lambda t: t + 1, 1.07, 3, C.TEAL, 2.2)
    ax.hollow(1, 2, C.RED, 4.5)
    ax.label(1, 2, "{R:hole at (1, 2)}", 11, dx=8, dy=8)
    rows = [(0.9, "1.9"), (0.99, "1.99"), (1, "0 ÷ 0: no value"), (1.01, "2.01"), (1.1, "2.1")]
    pg.text(L + 290, y_ + 18, "x", 12, C.GREY, F.BOLD)
    pg.text(L + 340, y_ + 18, "(x² − 1) ÷ (x − 1)", 12, C.GREY, F.BOLD)
    for k, (xv, out) in enumerate(rows):
        yy = y_ + 40 + k * 22
        col = C.RED if xv == 1 else C.INK
        pg.text(L + 290, yy, str(xv), 12.5, col)
        pg.text(L + 340, yy, out, 12.5, col, F.BOLD if xv == 1 else F.SANS)
        if xv != 1:
            ch.check_num((xv ** 2 - 1) / (xv - 1), float(out), 1e-9)
    pg.note(L + 290, y_ + 152, "creeps up to 2 from both sides,\nbut never actually lands on it", C.TEAL, 13)
    f.p("So the honest answer is $\\frac{x^2-1}{x-1} = x + 1$ {B:for $x \\neq 1$}. The graph is the whole "
        "straight line with {B:one point punched out}, drawn as an open circle. Cancelling hides the "
        "$x - 1$, but the ban stays with the original fraction.", 14)
    ch.term("cancel", "divide the top and bottom of a fraction by the same factor (something multiplying the "
            "whole top and the whole bottom)")


def back_to_front(ch):
    f = flow(ch)
    sec(f, "Back-to-front brackets: a − b = −(b − a)", room=380)
    rule_box(f, "reversing a subtraction", [
        "$a-b=-(b-a)$. Swapping the order of a subtraction only changes the sign: $5-3=2$ and $3-5=-2$.",
        "So $\\frac{a-b}{b-a}=-1$ (as long as $a\\ne b$).",
        "When a top and bottom bracket are the same apart from order, take out $-1$ from one of them, then "
        "cancel.",
    ], C.TEAL)
    twin_head(f)
    twin(f, r"\frac{7-3}{3-7}=\frac{4}{-4}=-1", r"\frac{x-3}{3-x}=\frac{-(3-x)}{3-x}=-1", "the top is −1 × the bottom")
    ch.check(sp.cancel((x - 3) / (3 - x)), -1)
    f.p("{b:Example:} $\\frac{2-x}{x^2-4}$. The bottom factorises to $(x-2)(x+2)$, and $2 - x = -(x - 2)$:",
        14, gap=6)
    step(f, r"\frac{2-x}{x^2-4}=\frac{-(x-2)}{(x-2)(x+2)}", "take out −1 on top; factorise the bottom", size=18)
    step(f, r"=\frac{-1}{x+2}=-\frac{1}{x+2}", "cancel (x − 2); x ≠ 2, x ≠ −2", size=18, color=C.GREEN)
    ch.check(sp.cancel((2 - x) / (x ** 2 - 4)), -1 / (x + 2))
    f.p("{G:Test} $x = 0$: $\\frac{2}{-4} = -0.5$ and $-\\frac12 = -0.5$ ✓.", 13.5, gap=6)
    ch.check(sp.Rational(2, -4), -sp.Rational(1, 2))
    mistakes(f, [
        (r"\frac{x+3}{3}=x", r"\frac{x+3}{3}=\frac x3+1", "3 is not a factor of the whole top: no cancelling"),
        (r"\frac{x^2+x}{x}=x^2+1", r"\frac{x(x+1)}{x}=x+1", "factorise first: x is a factor of the WHOLE top"),
        (r"\frac{x-3}{3-x}=1", r"\frac{x-3}{3-x}=-1", "reversed brackets differ by a factor of −1"),
    ])
    ch.check(sp.expand((x + 3) / 3), x / 3 + 1)
    ch.check(sp.cancel((x ** 2 + x) / x), x + 1)


def times(ch):
    f = flow(ch)
    sec(f, "Multiplying and dividing: the easy pair", room=420)
    rule_box(f, "multiplying and dividing algebraic fractions", [
        "{B:Multiply:} factorise every top and bottom, cancel any factor that appears on a top and a bottom "
        "(even in different fractions), then multiply tops together and bottoms together.",
        "{B:Divide:} keep the first fraction, flip the second (its reciprocal), then multiply as above. "
        "{R:Flip before you cancel.}",
    ], C.TEAL)
    f.p("Multiply: tops times tops, bottoms times bottoms. Divide: flip the second fraction "
        "(its reciprocal) and multiply. Exactly Chapter 2:", 14, gap=6)
    twin_head(f)
    twin(f, r"\frac23\times\frac45=\frac{8}{15}", r"\frac ab\times\frac cd=\frac{ac}{bd}", "tops × tops, bottoms × bottoms")
    twin(f, r"\frac23\div\frac45=\frac23\times\frac54", r"\frac ab\div\frac cd=\frac ab\times\frac dc", "flip the second, then multiply")
    ch.check(sp.Rational(2, 3) / sp.Rational(4, 5), sp.Rational(10, 12))
    f.p("{b:A full example in tiny steps:} $\\frac{2x}{3} \\times \\frac{9}{4x^2}$", 14, gap=6)
    step(f, r"\frac{2x\cdot9}{3\cdot4x^2}", "tops together, bottoms together", size=19)
    step(f, r"=\frac{18x}{12x^2}", "2 × 9 = 18;  3 × 4x² = 12x²", size=19)
    step(f, r"=\frac{3\cdot\cancel{6x}}{2x\cdot\cancel{6x}}=\frac{3}{2x}", "cancel the glued 6x", size=19,
         color=C.GREEN)
    ch.check(sp.cancel(2 * x / 3 * 9 / (4 * x ** 2)), 3 / (2 * x))
    f.p("{b:Dividing:} $\\frac{x}{4} \\div \\frac{x^2}{6}$", 14, gap=6)
    step(f, r"=\frac x4\times\frac6{x^2}=\frac{6x}{4x^2}", "flip the second fraction and multiply", size=19)
    step(f, r"=\frac{3}{2x}", "cancel 2x from top and bottom", size=19, color=C.GREEN)
    ch.check(sp.cancel((x / 4) / (x ** 2 / 6)), 3 / (2 * x))
    f.p("Test with $x = 3$: $\\frac34 \\div \\frac96 = 0.75 \\div 1.5 = 0.5$, and $\\frac{3}{6} = 0.5$ ✓.",
        13.5, C.GREEN, gap=10)
    f.p("{b:Dividing when you must factorise first:} $\\frac{x^2-9}{x+2} \\div \\frac{x-3}{x^2+2x}$", 14, gap=6)
    step(f, r"=\frac{x^2-9}{x+2}\times\frac{x^2+2x}{x-3}", "flip the second, then ×", size=18)
    step(f, r"=\frac{(x-3)(x+3)}{x+2}\times\frac{x(x+2)}{x-3}", "factorise every top and bottom", size=18)
    step(f, r"=\frac{\cancel{(x-3)}(x+3)}{\cancel{x+2}}\times\frac{x\cancel{(x+2)}}{\cancel{x-3}}=x(x+3)",
         "cancel across the ×", size=18, color=C.GREEN)
    ch.check(sp.cancel(((x ** 2 - 9) / (x + 2)) / ((x - 3) / (x ** 2 + 2 * x))), sp.expand(x * (x + 3)))
    f.p("{G:Test} $x = 1$: $\\frac{-8}{3} \\div \\frac{-2}{3} = 4$ and $1 \\times 4 = 4$ ✓.", 13.5, gap=6)
    ch.check(sp.Rational(-8, 3) / sp.Rational(-2, 3), 4)


def adding(ch):
    f = flow(ch)
    sec(f, "Adding and subtracting", fresh=True)
    rule_box(f, "adding and subtracting", [
        "$\\dfrac ab\\pm\\dfrac cd=\\dfrac{ad\\pm bc}{bd}$, with each top and bottom in brackets. This always works.",
        "If the bottoms share a factor (like $x$ and $2x$), the answer will contain that factor to "
        "cancel at the end. The optional procedure below avoids that by using a smaller bottom.",
    ], C.TEAL)
    rule_box(f, "optional: the lowest common denominator (LCD)", [
        "{B:Factorise every bottom.}",
        "The {B:LCD} is made of every different factor, each taken the {B:most times it appears in any one "
        "bottom}. (If the bottoms share no factor, the LCD is just the bottoms multiplied.)",
        "Multiply the top and bottom of each fraction by whatever its bottom is {B:missing} from the LCD.",
        "Add or subtract the tops (second top in brackets when subtracting). Keep the LCD.",
        "Factorise the new top and cancel if you can.",
    ], C.TEAL, numbered=True, tag="PROCEDURE")
    ch.term("lowest common denominator (LCD)", "the simplest bottom that every fraction's bottom divides into: "
            "each different factor of the bottoms, taken the most times it appears in any one bottom")
    twin_head(f)
    twin(f, r"\frac13+\frac14=\frac{1\cdot4+3\cdot1}{3\cdot4}", r"\frac1x+\frac1y=\frac{1\cdot y+x\cdot1}{xy}",
         "ad + bc over bd")
    twin(f, r"=\frac{7}{12}", r"=\frac{y+x}{xy}", "", col=C.GREEN)
    ch.check(sp.together(1 / x + 1 / y), (x + y) / (x * y))
    ch.check(sp.Rational(1, 3) + sp.Rational(1, 4), sp.Rational(7, 12))
    ch.formula(r"\frac ab\pm\frac cd=\frac{ad\pm bc}{bd}", "adding / subtracting fractions")
    f.p("That's Lecture 1's formula. (Its subtraction slide prints a + where the − should be; the "
        "appendix lists it.) When the bottoms {B:share a factor} it gives a bigger bottom than needed and "
        "you cancel at the end; the LCD is the optional way to skip that.", 13.5, gap=10)
    f.p("{b:Shared factor:} $\\frac1x + \\frac1{2x}$. The bottoms are $x$ and $2 \\times x$. The factors are "
        "2 (at most once) and $x$ (at most once), so the LCD is $2x$, not $2x^2$:", 14, gap=6)
    step(f, r"\frac1x+\frac1{2x}=\frac{1\times\blu2}{x\times\blu2}+\frac1{2x}", "x is missing a 2", size=18)
    step(f, r"=\frac{2+1}{2x}=\frac3{2x}", "same bottoms: add the tops", size=18, color=C.GREEN)
    ch.check(sp.together(1 / x + 1 / (2 * x)), 3 / (2 * x))
    f.p("(Multiplying the bottoms gives $\\frac{2x+x}{2x^2} = \\frac{3x}{2x^2}$, which still has to be "
        "cancelled down to $\\frac{3}{2x}$.)", 13, C.GREY, gap=10)
    ch.check(sp.cancel(3 * x / (2 * x ** 2)), 3 / (2 * x))
    f.p("{b:Factorise first:} $\\frac{1}{x+1} + \\frac{2}{x^2-1}$. The second bottom is a difference of two "
        "squares, $(x-1)(x+1)$, and it already contains $x + 1$:", 14, gap=6)
    step(f, r"\text{LCD}=(x-1)(x+1)", "(x + 1) at most once, (x − 1) at most once", size=18)
    step(f, r"\frac{1\blu{(x-1)}}{(x+1)\blu{(x-1)}}+\frac{2}{(x-1)(x+1)}", "the first is missing (x − 1)", size=18)
    step(f, r"=\frac{x-1+2}{(x-1)(x+1)}=\frac{x+1}{(x-1)(x+1)}", "add the tops", size=18)
    step(f, r"=\frac{1}{x-1}", "cancel (x + 1);  x ≠ ±1", size=18, color=C.GREEN)
    ch.check(sp.simplify(1 / (x + 1) + 2 / (x ** 2 - 1) - 1 / (x - 1)), 0)
    f.p("{G:Test} $x = 2$: $\\frac13 + \\frac23 = 1$ and $\\frac{1}{1} = 1$ ✓.", 13.5, gap=10)
    ch.check(sp.Rational(1, 3) + sp.Rational(2, 3), 1)
    f.p("{b:Bottoms with brackets:} $\\frac{2}{x+1} + \\frac{3}{x-2}$. Treat each bottom as one glued "
        "lump.", 14, gap=6)
    step(f, r"\frac{2(x-2)}{(x+1)(x-2)}+\frac{3(x+1)}{(x+1)(x-2)}", "each × the other bottom", size=18)
    step(f, r"=\frac{2x-4+3x+3}{(x+1)(x-2)}", "add the tops; expand", size=18)
    step(f, r"=\frac{5x-1}{(x+1)(x-2)}", "collect like terms", size=18, color=C.GREEN)
    ch.check(sp.simplify(2 / (x + 1) + 3 / (x - 2) - (5 * x - 1) / ((x + 1) * (x - 2))), 0)
    f.p("Test $x = 0$: $\\frac21 + \\frac{3}{-2} = 0.5$ and $\\frac{-1}{(1)(-2)} = 0.5$ ✓.", 13.5, C.GREEN, gap=10)


def minus_trap(ch):
    f = flow(ch)
    sec(f, "The minus-sign trap", room=300)
    rule_box(f, "subtracting a fraction", [
        "The minus applies to the {B:whole top} of the fraction after it. Put that top in {B:brackets}, then "
        "multiply out: $-(x-1)=-x+1$.",
    ], C.TEAL)
    f.p("When you subtract a fraction, the minus applies to its {B:whole top}. Keep the top in a "
        "bracket until the minus has been multiplied in: $\\frac{x+3}{2} - \\frac{x-1}{3}$", 14, gap=6)
    step(f, r"=\frac{3(x+3)-2(x-1)}{6}", "common bottom 6; brackets kept!", size=19)
    step(f, r"=\frac{3x+9-2x+2}{6}", "−2 × −1 = +2 (the trap is writing −2)", size=19)
    step(f, r"=\frac{x+11}{6}", "", size=19, color=C.GREEN)
    ch.check(sp.simplify((x + 3) / 2 - (x - 1) / 3 - (x + 11) / 6), 0)
    f.p("Test $x = 1$: $\\frac42 - \\frac03 = 2$ and $\\frac{12}{6} = 2$ ✓. Writing $-2x - 2$ would give "
        "$\\frac{x+7}{6}$, which is $\\frac86$ at $x = 1$ ✗.", 13.5)


def whole_and_nested(ch):
    f = flow(ch)
    sec(f, "Whole numbers, and fractions inside fractions", room=460)
    rule_box(f, "a whole number (or expression) with a fraction", [
        "Write the whole number over the other fraction's bottom: $1=\\frac{x+1}{x+1}$, $2=\\frac{2x}{x}$. "
        "Then add or subtract as usual.",
    ], C.TEAL)
    twin_head(f)
    twin(f, r"1-\frac34=\frac44-\frac34=\frac14", r"1-\frac{3}{x+1}=\frac{x+1}{x+1}-\frac{3}{x+1}",
         "1 written with the same bottom")
    twin(f, r"\phantom{1}", r"=\frac{x+1-3}{x+1}=\frac{x-2}{x+1}", col=C.GREEN)
    ch.check(sp.simplify(1 - 3 / (x + 1) - (x - 2) / (x + 1)), 0)
    rule_box(f, "a fraction inside a fraction (a complex fraction)", [
        "Find the LCD of {B:all} the small fractions inside.",
        "Multiply the {B:top and the bottom of the big fraction} by it. Every small fraction clears.",
        "Simplify: factorise and cancel.",
    ], C.TEAL, numbered=True, tag="PROCEDURE")
    ch.term("complex fraction", "a fraction with fractions in its top or bottom, e.g. (1 + 1/x)/(1 − 1/x); "
            "clear it by multiplying top and bottom by the LCD of the small fractions")
    f.p("{b:Example:} $\\dfrac{1+\\frac1x}{1-\\frac1x}$. The only small bottom is $x$, so multiply top and "
        "bottom by $x$:", 14, gap=6)
    step(f, r"\frac{\left(1+\frac1x\right)\blu{\times x}}{\left(1-\frac1x\right)\blu{\times x}}"
         r"=\frac{x+1}{x-1}", "x × 1 = x and x × 1/x = 1", size=18, color=C.GREEN)
    ch.check(sp.cancel((1 + 1 / x) / (1 - 1 / x)), (x + 1) / (x - 1))
    f.p("{b:Example:} $\\dfrac{\\frac1x+\\frac1y}{\\frac1{xy}}$. The LCD of $x$, $y$ and $xy$ is $xy$:", 14, gap=6)
    step(f, r"\frac{\left(\frac1x+\frac1y\right)\blu{\times xy}}{\frac1{xy}\blu{\times xy}}=\frac{y+x}{1}=x+y",
         "each small bottom cancels", size=18, color=C.GREEN)
    ch.check(sp.simplify((1 / x + 1 / y) / (1 / (x * y)) - (x + y)), 0)
    f.p("{G:Test} $x = 2$, $y = 3$: $\\frac{1/2 + 1/3}{1/6} = \\frac{5/6}{1/6} = 5$ and $2 + 3 = 5$ ✓.", 13.5)
    ch.check((sp.Rational(1, 2) + sp.Rational(1, 3)) / sp.Rational(1, 6), 5)


def equations(ch):
    f = flow(ch)
    sec(f, "Equations with algebraic fractions", room=480)
    f.p("An {B:equation} has an = sign, so you may multiply {B:both sides} by the same thing (Part 0's "
        "balance: do the same to both sides). That clears every fraction in one go. Chapters 14 and 15 do "
        "rearranging and solving in full; this is the fraction part.", 13.5, gap=6)
    rule_box(f, "solving an equation with fractions", [
        "Write down the {B:banned values} (anything that makes a bottom zero).",
        "Multiply {B:every term on both sides} by the LCD of all the bottoms.",
        "Solve what's left (no fractions now).",
        "{R:Reject any answer that is a banned value}, then check the rest in the original equation.",
    ], C.TEAL, numbered=True, tag="PROCEDURE")
    f.p("{b:Example:} $\\frac3x + \\frac12 = 2$. Banned: $x = 0$. LCD: $2x$.", 14, gap=6)
    step(f, r"2x\cdot\frac3x+2x\cdot\frac12=2x\cdot2", "× 2x, every term", size=18)
    step(f, r"6+x=4x\ \Rightarrow\ 6=3x\ \Rightarrow\ x=2", "solve", size=18, color=C.GREEN)
    ch.check(sp.solve(sp.Eq(3 / x + sp.Rational(1, 2), 2), x), [2])
    f.p("{G:Check:} $\\frac32 + \\frac12 = 2$ ✓, and 2 is not banned.", 13.5, gap=8)
    f.p("{b:Example with a rejected answer:} $\\frac{x}{x-2} = \\frac{2}{x-2} + 3$. Banned: $x = 2$.", 14, gap=6)
    step(f, r"x=2+3(x-2)", "× (x − 2), every term", size=18)
    step(f, r"x=3x-4\ \Rightarrow\ x=2", "solve", size=18)
    step(f, r"x=2\text{ is banned: no solution}", "it makes the bottom 0", size=18, color=C.RED)
    ch.check(sp.solve(x - (2 + 3 * (x - 2)), x), [2])
    ch.check(sp.solve(sp.Eq(x / (x - 2), 2 / (x - 2) + 3), x), [])
    f.p("Multiplying by $x - 2$ is multiplying by 0 when $x = 2$, which can create a fake answer. That's "
        "why step 4 is not optional.", 13.5, gap=6)
    mistakes(f, [
        (r"\frac3x+\frac12=2\ \to\ 6+x=2", r"6+x=4x", "multiply EVERY term by the LCD, including the 2 on the right"),
    ])


def bottom_test(ch):
    f = flow(ch)
    sec(f, "Splitting a fraction: the top may split, the bottom may not", room=430)
    f.p("Lecture 2's \"common mistakes (2)\" slide warns: $\\frac{a}{b+c} \\neq \\frac ab + \\frac ac$. "
        "Think of sweets:", 14, gap=8)
    y_ = f.reserve(120)
    pg = f.pg
    for i in range(12):
        pg.circle(L + 20 + (i % 6) * 18, y_ + 12 + (i // 6) * 18, 7, C.PINK, 1, fillcolor=C.LIGHT[C.PINK])
    pg.note(L + 10, y_ + 44, "12 sweets", C.PINK, 15)
    for i in range(6):
        cx = L + 190 + i * 30
        col = C.BLUE if i < 2 else C.GREEN
        pg.circle(cx, y_ + 12, 7, col, 1.2)
        pg.line(cx, y_ + 19, cx, y_ + 36, col, 1.2)
        pg.line(cx - 8, y_ + 26, cx + 8, y_ + 26, col, 1.2)
    pg.note(L + 190, y_ + 44, "2 friends arrive, then 4 more", C.GREY, 15)
    pg.eq(L + 20, y_ + 76, r"\frac{12}{2+4}=\frac{12}{6}=2\text{ each}", 17, C.GREEN)
    pg.eq(L + 270, y_ + 76, r"\frac{12}{2}+\frac{12}{4}=6+3=9", 17, C.RED)
    pg.xmark(L + 470, y_ + 84, 10)
    ch.check(sp.Rational(12, 6), 2)
    f.p("Nine sweets each would need 54 sweets! Sharing among a {B:sum} of people is not the same as "
        "sharing among each group separately. But splitting the {B:top} is fine: 12 red + 6 blue "
        "sweets among 3 people is 4 red + 2 blue each.", 14, gap=6)
    twin_head(f, "allowed: split the top", "not allowed: split the bottom")
    twin(f, r"\frac{a+b}{c}=\frac ac+\frac bc", r"\frac{a}{b+c}\neq\frac ab+\frac ac")
    ch.check(sp.expand((a + b) / c), a / c + b / c)
    f.p("The same slide's other warning is the root version: $\\sqrt{a^2 + b^2} \\neq a + b$. Test "
        "$a = 3$, $b = 4$: $\\sqrt{25} = 5$, not 7.", 13.5, gap=6)
    ch.check(sp.sqrt(9 + 16), 5)


def lecture(ch):
    f = flow(ch)
    sec(f, "The lecture's letters-only example", room=330)
    f.p("Lecture 2 asks you to solve $\\frac1x = \\frac2y - \\frac3z$ for $z$. The heart of it is one "
        "subtraction of fractions, which is this chapter's skill. On the way, you meet "
        "$\\frac2y - \\frac1x$:", 14, gap=6)
    twin_head(f)
    twin(f, r"\frac25-\frac13=\frac{2\cdot3-5}{15}", r"\frac2y-\frac1x=\frac{2x-y}{xy}", "a/b − c/d = (ad − bc)/bd")
    ch.check(sp.together(2 / y - 1 / x) - (2 * x - y) / (x * y), 0)
    f.p("Chapter 14 finishes the job (flip both sides, multiply by 3) and gets "
        "$z = \\frac{3xy}{2x - y}$. With $x = 1$, $y = 1$: $z = 3$, and indeed "
        "$\\frac11 = \\frac21 - \\frac33$ ✓.", 13.5)
    ch.check(sp.Rational(2, 1) - sp.Rational(3, 3), 1)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Banned values", None, "a fraction is undefined where its bottom is 0; cancelling doesn't remove the ban"),
        ("Simplify", r"\frac{x^2+3x}{x+3}=\frac{x\cancel{(x+3)}}{\cancel{(x+3)}}=x",
         "factorise top and bottom first; cancel {B:factors}, never terms"),
        ("Back-to-front brackets", r"a-b=-(b-a),\qquad\frac{a-b}{b-a}=-1", None),
        ("Add / subtract", r"\frac ab\pm\frac cd=\frac{ad\pm bc}{bd}", "always works; optional LCD "
         "(factorise the bottoms, each factor the most times it appears) gives a smaller bottom"),
        ("Subtracting", r"\frac{x+3}{2}-\frac{x-1}{3}=\frac{3(x+3)-2(x-1)}{6}", "second top in brackets"),
        ("Multiply", r"\frac ab\times\frac cd=\frac{ac}{bd}", "multiply across; factorise and cancel first"),
        ("Divide", r"\frac ab\div\frac cd=\frac ab\times\frac dc=\frac{ad}{bc}", "flip the second only"),
        ("Splitting", r"\frac{a+b}{c}=\frac ac+\frac bc,\qquad \frac{a}{b+c}\ne\frac ab+\frac ac",
         "the top may split, the bottom may not"),
        ("Whole number with a fraction", r"1-\frac{3}{x+1}=\frac{x+1-3}{x+1}", None),
        ("Fraction inside a fraction", None, "multiply the big top and big bottom by the LCD of the small "
         "fractions"),
        ("Equations with fractions", None, "× every term by the LCD, solve, {R:reject banned values}, check"),
    ], C.TEAL, title="Algebraic fraction rules")


def your_turn(ch):
    f = flow(ch)
    sec(f, "Twin columns: your turn", fresh=True)
    f.p("Answers in grey. Check each by substituting a number such as x = 3.", 13.5, gap=10)
    groups = [
        ("When is it undefined?", ["7/(x − 5)", "x/(x² − 4)"], "1. x = 5   2. x = 2 or x = −2"),
        ("Cancel (factorise first!)", ["10x²/(15x)", "(4x + 8)/4", "(x² − 1)/(x + 1)", "(x² + 5x + 6)/(x + 2)",
                                       "(x + 5)/5"],
         "3. 2x/3   4. x + 2   5. x − 1   6. x + 3   7. can't cancel: it's x/5 + 1"),
        ("Multiply and divide", ["(3x/4) × (8/x²)", "(x/2) ÷ (x/10)", "((x + 1)/x) × (x²/(x + 1))"],
         "8. 6/x   9. 5   10. x"),
        ("Add and subtract", ["1/x + 2/x", "1/x + 1/(2x)", "3/x − 2/y", "1/(x + 1) + 1/(x − 1)", "(x + 1)/2 − (x − 3)/4"],
         "11. 3/x   12. 3/(2x) (LCD 2x)   13. (3y − 2x)/(xy)   14. 2x/((x + 1)(x − 1))   15. (x + 5)/4"),
        ("Signs, nested fractions, equations", ["(x − 5)/(5 − x)", "1 − 2/(x + 3)", "(1 + 2/x)/(1 − 4/x²)",
                                                "((x² − 4)/(x + 1)) ÷ ((x − 2)/(x² + x))",
                                                "Solve 4/x − 1/3 = 1"],
         "16. −1   17. (x + 1)/(x + 3)   18. x/(x − 2) (× x², then cancel x + 2)   19. x(x + 2)   "
         "20. x = 3 (× 3x: 12 − x = 3x)"),
        ("Find the unknown", ["3/(x − 1) + A/(x + 1) = (5x + 1)/(x² − 1). Find A.",
                              "(x² + kx + 6)/(x + 2) simplifies to x + 3. Find k.",
                              "1/x + 1/(kx) = 5/(4x). Find k.",
                              "(x + 2)/(x − 3): for which x is it undefined, and for which is it 0?",
                              "a/(x − 2) − 1/x = (x + 2)/(x(x − 2)). Find a."],
         "21. A = 2 (3(x + 1) + A(x − 1) = 5x + 1)   22. k = 5 ((x + 2)(x + 3) = x² + 5x + 6)   "
         "23. k = 4 (× x: 1 + 1/k = 5/4)   24. undefined at x = 3 (bottom 0), zero at x = −2 (top 0)   "
         "25. a = 2 (ax − (x − 2) = x + 2)"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 40)
        f.text(title, 14, C.TEAL, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{n}. {qq}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    S = sp.simplify
    for g, e in [(10 * x ** 2 / (15 * x), 2 * x / 3), ((4 * x + 8) / 4, x + 2), ((x ** 2 - 1) / (x + 1), x - 1),
                 ((x ** 2 + 5 * x + 6) / (x + 2), x + 3), (3 * x / 4 * 8 / x ** 2, 6 / x), ((x / 2) / (x / 10), 5),
                 ((x + 1) / x * x ** 2 / (x + 1), x), (1 / x + 1 / (2 * x), 3 / (2 * x)),
                 (3 / x - 2 / y, (3 * y - 2 * x) / (x * y)), (1 / (x + 1) + 1 / (x - 1), 2 * x / ((x + 1) * (x - 1))),
                 ((x + 1) / 2 - (x - 3) / 4, (x + 5) / 4), ((x - 5) / (5 - x), -1),
                 (1 - 2 / (x + 3), (x + 1) / (x + 3)), ((1 + 2 / x) / (1 - 4 / x ** 2), x / (x - 2)),
                 (((x ** 2 - 4) / (x + 1)) / ((x - 2) / (x ** 2 + x)), x * (x + 2))]:
        ch.check(S(g - e), 0)
    ch.check(sp.solve(sp.Eq(4 / x - sp.Rational(1, 3), 1), x), [3])
    A_, k_, a_ = sp.symbols("A k a")
    ch.check(sp.solve(sp.Poly(sp.expand(3 * (x + 1) + A_ * (x - 1) - (5 * x + 1)), x).coeffs(), A_), {A_: 2})
    ch.check(sp.solve(sp.Poly(sp.expand((x + 2) * (x + 3) - (x ** 2 + k_ * x + 6)), x).coeffs(), k_), {k_: 5})
    ch.check(sp.solve(sp.Eq(1 / x + 1 / (k_ * x), sp.Rational(5, 4) / x), k_), [4])
    ch.check([sp.solve(x - 3, x), sp.solve(x + 2, x)], [[3], [-2]])
    ch.check(sp.solve(sp.Poly(sp.expand(a_ * x - (x - 2) - (x + 2)), x).coeffs(), a_), {a_: 2})
    ch.check(S(2 / (x - 2) - 1 / x - (x + 2) / (x * (x - 2))), 0)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    what(ch)
    at_a_glance(ch)
    cancel(ch)
    back_to_front(ch)
    times(ch)
    adding(ch)
    minus_trap(ch)
    whole_and_nested(ch)
    bottom_test(ch)
    lecture(ch)
    equations(ch)
    summary(ch)
    your_turn(ch)
