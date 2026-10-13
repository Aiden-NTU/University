"""Chapter 2 - Fractions. Three formulas (add/subtract, multiply, divide), then examples of
plugging numbers into them."""
from fractions import Fraction as Fr

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import mistakes, rule_box, rules_page

ORDER = 2
NUM = 2
TITLE = "Fractions"
SHORT = "Fractions"
SLUG = "Fractions"
ACCENT = C.BROWN
REQUIRES = ["reading-maths", "equals-sign", "multiplication-notation", "factors", "hcf", "lcm",
            "order-of-operations", "division"]
INTRODUCES = ["fraction", "numerator-denominator", "equivalent-fractions", "simplify-fraction",
              "improper-fraction", "mixed-number", "add-fractions", "subtract-fractions",
              "multiply-fractions", "divide-fractions", "reciprocal", "compare-fractions",
              "negative-fractions", "fraction-of-amount"]

CHOC = "#7a4a26"
CHOC_L = "#c89a6e"
WRAP = "#f6eee4"
L, R, W = 50, 545, 495


# ----------------------------------------------------------------------------- drawing kit
def bar(pg, x, y, w, h, n, have=0, color=CHOC, light=None, empty=WRAP, lw=1.3):
    """A strip cut into n equal parts with the first `have` parts shaded."""
    light = light or color
    cw = w / n
    for c in range(n):
        pg.rect(x + c * cw + 1.2, y + 1.2, cw - 2.4, h - 2.4, color, 0,
                fillcolor=light if c < have else empty, r=2)
    pg.rect(x, y, w, h, CHOC, lw + 0.4, r=3)
    for c in range(1, n):
        pg.line(x + c * cw, y, x + c * cw, y + h, CHOC, lw)


def step(f, latex, why, size=22, color=C.INK, x=L + 20, note_x=None, col=C.RED):
    """A worked line with its reason written beside it."""
    w, h, _ = f.pg.eq_size(latex, size)
    nx = note_x or max(x + w + 36, 300)
    below = bool(why) and nx > R - 110
    if below:
        nh = F.line_h(F.HAND, 16) * len(F.wrap(why, F.HAND, 16, R - x - 20))
        y = f.reserve(h + nh + 12)
    else:
        nh = F.line_h(F.HAND, 16) * len(F.wrap(why, F.HAND, 16, R - nx)) if why else 0
        y = f.reserve(max(h, nh) + 12)
    pg = f.pg
    pg.eq(x, y, latex, size, color)
    if below:
        pg.note(x + 20, y + h + 1, why, col, 16, w=R - x - 20)
    elif why:
        pg.note(nx, y + max(0, h / 2 - 11), why, col, 16, w=R - nx)
        pg.arrow(nx - 6, y + h / 2, x + w + 8, y + h / 2, col, 1.0, head=4)
    return y, w, h


def flow(ch):
    """One continuous writing position for the whole chapter."""
    if getattr(ch, "_flow", None) is None:
        ch._flow = ch.flow()
        ch._flow.new_page()
    return ch._flow


def heading(f, s, sub=None, room=300):
    """Section title. Starts a new page unless there is plenty of room left."""
    if f.y > f.top + 5:
        f.need(room)
        if f.y > f.top + 5:
            f.gap(22)
    y = f.y
    pg = f.pg
    size = 20
    while pg.twidth(s, size, F.BOLD) > W - 10 and size > 13:
        size -= 1
    pg.rect(L - 8, y, 6, 28, CHOC, 0, fillcolor=CHOC)
    pg.text(L + 6, y + 1 + (20 - size) / 2, s, size, CHOC, F.BOLD)
    f.y += 34
    if sub:
        f.p(sub, 12.5, C.GREY, gap=8)


def example(f, s):
    f.need(90)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = ch.new_page(bg="#fbf5ee")
    pg.text(L, 70, "Chapter 2", 16, C.GREY, F.BOLD)
    pg.text(L, 92, "Fractions", 44, CHOC, F.BOLD)
    pg.note(L, 150, "the rules for each operation, and why they work", CHOC, 24)
    pg.eq(200, 230, r"\frac{\org{3}}{\blu{4}}", 60, align="center")
    pg.arrow(330, 248, 225, 252, C.ORANGE, 1.5)
    pg.note(338, 230, "numerator: how many parts", C.ORANGE, 18)
    pg.arrow(330, 318, 225, 312, C.BLUE, 1.5)
    pg.note(338, 300, "denominator: how many equal\nparts make one whole", C.BLUE, 18)
    f = ch.flow(top=400)
    f.p("Everything you do with two fractions comes from {B:three formulas}: one for adding and "
        "subtracting, one for multiplying, one for dividing. They are on the next pages. Put your numbers "
        "in for $a$, $b$, $c$, $d$ and work it out; the rest of the chapter is examples.", 14, gap=12)
    f.p("{y:Goes with} {B:Lecture 1} {y:(Combining fractions). Uses factors, HCF and LCM from Chapter 1.}",
        12.5)


def what_is(ch):
    f = flow(ch)
    heading(f, "What a fraction means")
    rule_box(f, "reading a fraction", [
        "$\\frac{a}{b}$ means: split one whole into {B:b equal parts} and take {O:a} of them.",
        "{O:a} is the {O:numerator} (top). {B:b} is the {B:denominator} (bottom). $b$ can never be 0.",
        "The fraction line {B:is} a division: $\\frac{a}{b}=a\\div b$. So $\\frac{12}{3}=4$ and "
        "$\\frac{3}{4}=0.75$.",
        "Any whole number can be written over 1: $5=\\frac{5}{1}$.",
    ], CHOC, tag="DEFINITION")
    ch.check(Fr(12, 3), 4)
    ch.check(Fr(3, 4), Fr(75, 100))
    y = f.reserve(58)
    pg = f.pg
    bar(pg, 110, y + 4, 260, 40, 4, have=3, light=C.LIGHT[C.ORANGE], color=C.ORANGE)
    pg.eq(400, y + 24, r"\frac{3}{4}", 22, valign="middle")
    pg.note(440, y + 8, "3 of 4\nequal parts", C.ORANGE, 15)
    f.p("The parts must be {B:equal}. The denominator gives the parts their name: halves, thirds, "
        "quarters, fifths... The numerator counts how many of those parts you have.", 13.5, gap=8)
    f.bullet("{B:Proper fraction}: top smaller than bottom, so less than 1 (e.g. $\\frac{3}{4}$).", 13)
    f.bullet("{B:Improper fraction}: top bigger than bottom, so more than 1 (e.g. $\\frac{7}{4}$).", 13)
    f.bullet("{B:Mixed number}: a whole number plus a proper fraction (e.g. $1\\tfrac{3}{4}$, "
             "\"one and three quarters\").", 13)
    ch.term("fraction", "part of a whole, written as top number over bottom number; also means top ÷ bottom")
    ch.term("numerator", "the top number of a fraction: how many parts you have")
    ch.term("denominator", "the bottom number of a fraction: how many equal parts make one whole")
    ch.term("improper fraction", "a fraction whose top is bigger than its bottom (more than one whole)")
    ch.term("mixed number", "a whole number and a fraction together, such as 1 3/4")
    ch.term("proper fraction", "a fraction less than one whole: top smaller than bottom")


def at_a_glance(ch):
    f = flow(ch)
    heading(f, "The three formulas", room=560)
    f.p("These are the whole lesson. Put your numbers in for $a$, $b$, $c$, $d$ and work it out.",
        13.5, gap=8)
    formulas = [
        ("Add / subtract", r"\frac{a}{b}\pm\frac{c}{d}=\frac{ad\pm bc}{bd}", "same for + and −"),
        ("Multiply", r"\frac{a}{b}\times\frac{c}{d}=\frac{ac}{bd}", "multiply across"),
        ("Divide", r"\frac{a}{b}\div\frac{c}{d}=\frac{a}{b}\times\frac{d}{c}=\frac{ad}{bc}",
         "flip the 2nd, then\nmultiply across"),
    ]
    rh = 74
    y = f.reserve(len(formulas) * rh + 44)
    pg = f.pg
    pg.rect(L, y, W, len(formulas) * rh + 34, CHOC, 1.6, fillcolor="#fbf1e2", r=8)
    pg.text(L + 14, y + 8, "THE RULES", 11, CHOC, F.BOLD)
    for i, (name, lat, say) in enumerate(formulas):
        yy = y + 26 + i * rh
        pg.text(L + 14, yy + 14, name, 14, CHOC, F.BOLD)
        h = pg.eq_size(lat, 24)[1]
        pg.eq(L + 150, yy + (rh - 10 - h) / 2, lat, 24)
        pg.note(L + 14, yy + 34, say, C.RED, 15)
    a, b, c, d = sp.symbols("a b c d", nonzero=True)
    ch.check(sp.simplify(a / b + c / d - (a * d + b * c) / (b * d)), 0)
    ch.check(sp.simplify(a / b - c / d - (a * d - b * c) / (b * d)), 0)
    ch.check(sp.simplify((a / b) / (c / d) - (a * d) / (b * c)), 0)
    f.gap(4)
    f.p("{B:With numbers} ($a=2$, $b=3$, $c=4$, $d=5$: Lecture 1's examples):", 13.5, gap=4)
    step(f, r"\frac23+\frac45=\frac{2\times5+3\times4}{3\times5}=\frac{22}{15}", "ad + bc over bd", size=20)
    step(f, r"\frac23-\frac45=\frac{2\times5-3\times4}{3\times5}=-\frac{2}{15}", "ad − bc over bd", size=20)
    step(f, r"\frac23\times\frac45=\frac{2\times4}{3\times5}=\frac{8}{15}", "ac over bd", size=20)
    step(f, r"\frac23\div\frac45=\frac{2\times5}{3\times4}=\frac{10}{12}", "ad over bc", size=20)
    ch.check(Fr(2, 3) + Fr(4, 5), Fr(22, 15))
    ch.check(Fr(2, 3) - Fr(4, 5), Fr(-2, 15))
    ch.check(Fr(2, 3) * Fr(4, 5), Fr(8, 15))
    ch.check(Fr(2, 3) / Fr(4, 5), Fr(10, 12))
    f.gap(4)
    rule_box(f, "getting the numbers into a/b form", [
        "A whole number goes over 1: $4=\\frac41$.",
        "A mixed number becomes an improper fraction first: $2\\tfrac13=\\frac{2\\times3+1}{3}=\\frac73$.",
        "Simplifying the answer is an optional tidy-up: $\\frac{10}{12}$ and $\\frac56$ are the same "
        "number. Do it when a question asks for the simplest form.",
    ], CHOC, tag="INPUTS")


def why_formula(ch):
    f = flow(ch)
    heading(f, "Where the add/subtract formula comes from")
    f.p("Multiplying a fraction's top and bottom by the same number doesn't change its value. So "
        "multiply the first fraction by $\\frac{d}{d}$ and the second by $\\frac{b}{b}$:", 13.5, gap=6)
    f.eq(r"\frac{a}{b}+\frac{c}{d}=\frac{a\org{d}}{b\org{d}}+\frac{\org{b}c}{\org{b}d}=\frac{ad+bc}{bd}", 24,
         gap=8)
    f.p("Both fractions are now over $bd$, so their tops add. That's the whole derivation. When a "
        "textbook says \"find a common denominator\", it means this step; the formula has already done "
        "it for you with $bd$.", 13.5, gap=8)
    f.p("Multiplying needs no such step: $\\frac{a}{b}\\times\\frac{c}{d}$ is just $a\\times c\\div(b\\times d)$. "
        "Dividing by $\\frac{c}{d}$ is multiplying by $\\frac{d}{c}$, because $\\frac{c}{d}\\times\\frac{d}{c}=1$.",
        13.5)


def equivalent(ch):
    f = flow(ch)
    heading(f, "Simplifying an answer (equivalent fractions)")
    f.p("The formulas often give answers like $\\frac{10}{12}$. That is already correct; simplifying just "
        "writes the same number with smaller numbers.", 13.5, gap=6)
    rule_box(f, "equivalent fractions", [
        "Multiplying or dividing the top {B:and} the bottom by the {B:same} non-zero number gives the same "
        "value: $\\frac{a}{b}=\\frac{a\\times k}{b\\times k}$.",
        "{R:Adding or subtracting the same number to top and bottom does NOT keep the value.}",
    ], CHOC)
    step(f, r"\frac{3}{4}=\frac{3\org{\times 5}}{4\org{\times 5}}=\frac{15}{20}",
         "top AND bottom × 5")
    step(f, r"\frac{1}{2}\ne\frac{1+1}{2+1}=\frac{2}{3}", "adding 1 to both changes the value", color=C.GREY)
    ch.check(Fr(3, 4), Fr(15, 20))
    ch.check_true(Fr(2, 3) != Fr(1, 2))
    ch.term("equivalent fractions", "fractions with the same value, like 1/2 and 2/4: top and bottom multiplied by the same number")
    f.gap(6)
    rule_box(f, "simplifying (cancelling)", [
        "Find the {B:highest common factor} (HCF) of the top and bottom (Chapter 1).",
        "Divide the top and the bottom by it.",
        "Check: if no number except 1 divides both, the fraction is in {B:simplest form}. "
        "(Smaller steps are fine: divide by any common factor, repeat until none is left.)",
    ], CHOC, numbered=True, tag="PROCEDURE")
    example(f, "simplify $\\frac{12}{18}$.")
    step(f, r"\text{HCF}(12,18)=6", "factors of 12: 1,2,3,4,6,12; of 18: 1,2,3,6,9,18")
    step(f, r"\frac{12\org{\div 6}}{18\org{\div 6}}=\grn{\frac{2}{3}}", "divide top and bottom by 6")
    ch.check(Fr(12, 18), Fr(2, 3))
    ch.term("simplify a fraction", "divide top and bottom by the same number (ideally the HCF) so the numbers are as small as possible")
    f.p("{R:Cancel factors, never terms.} In $\\frac{6}{8}$ you divide the {B:whole} top and the {B:whole} "
        "bottom. In $\\frac{2+4}{2+6}$ you may {R:not} cross out the 2s: work out the top and bottom first "
        "($\\frac{6}{8}$), then cancel.", 13.5)
    ch.check(Fr(2 + 4, 2 + 6), Fr(3, 4))


def improper(ch):
    f = flow(ch)
    heading(f, "Mixed numbers and improper fractions")
    rule_box(f, "converting", [
        "{B:Mixed to improper:} whole × bottom, add the top, keep the bottom: "
        "$p\\tfrac{a}{b}=\\frac{p\\times b+a}{b}$.",
        "{B:Improper to mixed:} divide top by bottom. The quotient is the whole number, the remainder "
        "is the new top, the bottom stays the same.",
    ], CHOC)
    step(f, r"2\tfrac{1}{3}=\frac{2\times3+1}{3}=\grn{\frac{7}{3}}", "2 wholes = 6 thirds, plus 1 third")
    ch.check(2 + Fr(1, 3), Fr(7, 3))
    step(f, r"\frac{11}{4}:\ 11\div4=2\ \text{r}\ 3", "4 goes into 11 twice, 3 left over")
    step(f, r"\frac{11}{4}=\grn{2\tfrac{3}{4}}", "2 wholes and 3 quarters")
    ch.check(Fr(11, 4), 2 + Fr(3, 4))
    f.p("{B:Negative mixed numbers:} $-1\\tfrac{3}{4}$ means $-(1+\\frac34)=-\\frac74$. The minus sign "
        "applies to the whole thing, {R:not} just the 1.", 13.5)
    ch.check(-(1 + Fr(3, 4)), Fr(-7, 4))


def add_subtract(ch):
    f = flow(ch)
    heading(f, "Adding and subtracting", room=420)
    f.eq(r"\frac{a}{b}\pm\frac{c}{d}=\frac{ad\pm bc}{bd}", 26, gap=8)
    example(f, "$\\frac{3}{4}+\\frac{1}{6}$.")
    step(f, r"=\frac{3\times6+4\times1}{4\times6}=\frac{18+4}{24}=\frac{22}{24}", "a = 3, b = 4, c = 1, d = 6")
    step(f, r"=\grn{\frac{11}{12}}", "optional: simplify, ÷ 2")
    ch.check(Fr(3, 4) + Fr(1, 6), Fr(22, 24))
    ch.check(Fr(22, 24), Fr(11, 12))
    example(f, "$\\frac{5}{6}-\\frac{1}{4}$.")
    step(f, r"=\frac{5\times4-6\times1}{6\times4}=\frac{20-6}{24}=\frac{14}{24}=\grn{\frac{7}{12}}",
         "ad − bc over bd")
    ch.check(Fr(5, 6) - Fr(1, 4), Fr(7, 12))
    example(f, "the bottoms are already the same, $\\frac{1}{5}+\\frac{2}{5}$.")
    step(f, r"=\frac{1\times5+5\times2}{5\times5}=\frac{15}{25}=\grn{\frac35}", "the formula still works")
    ch.check(Fr(1, 5) + Fr(2, 5), Fr(15, 25))
    f.p("Shortcut when $b=d$: the formula's answer always simplifies to \"add the tops, keep the "
        "bottom\", $\\frac{1+2}{5}=\\frac35$. Use it or ignore it; the answer is the same.", 13.5, gap=8)
    f.p("{y:Optional, for smaller numbers:} instead of $bd$ you may use any number both bottoms divide "
        "into, such as the lowest common multiple. For $\\frac34+\\frac16$ that is 12: "
        "$\\frac{9}{12}+\\frac{2}{12}=\\frac{11}{12}$, the same answer as above without the simplifying "
        "at the end.", 13, C.GREY, gap=10)
    ch.check(Fr(9, 12) + Fr(2, 12), Fr(11, 12))
    f.p("{R:Slide error alert.} On the Lecture 1 slide for {B:subtraction}, the left-hand side is printed "
        "with a {R:+} sign. The correct formula has a minus on both sides.", 13.5, gap=6)
    f.p("{G:Sense check} (your lecturer's habit): $\\frac23$ and $\\frac45$ are each a bit under 1, so "
        "$\\frac23+\\frac45=\\frac{22}{15}=1\\tfrac{7}{15}$, a bit under 2, is sensible. ✓", 13.5)
    ch.check(Fr(22, 15), 1 + Fr(7, 15))


def negatives(ch):
    f = flow(ch)
    heading(f, "Negative fractions")
    f.p("The lecture's subtraction example is $\\frac23-\\frac45$, which comes out {B:negative}: you take "
        "away more than you started with.", 13.5, gap=6)
    rule_box(f, "negative fractions", [
        "The minus sign can sit in front, on top, or on the bottom: "
        "$-\\frac{a}{b}=\\frac{-a}{b}=\\frac{a}{-b}$. Put it on {B:top} while you work.",
        "The three formulas work unchanged; the tops follow the rules for negative numbers (Chapter 1).",
        "Multiplying and dividing: same sign gives {B:+}, different signs give {B:−}.",
        "Two minus signs cancel: $\\frac{-a}{-b}=\\frac{a}{b}$.",
    ], CHOC)
    step(f, r"\frac{2}{3}-\frac{4}{5}=\frac{2\times5-3\times4}{3\times5}", "ad − bc over bd")
    step(f, r"=\frac{10-12}{15}=\grn{-\frac{2}{15}}", "10 − 12 = −2")
    ch.check(Fr(2, 3) - Fr(4, 5), Fr(-2, 15))
    f.p("{G:Sense check:} you took away $\\frac45=0.8$ from $\\frac23\\approx0.67$, so the answer must be "
        "a little below zero. $-\\frac{2}{15}\\approx-0.13$ ✓", 13.5, gap=8)
    step(f, r"\frac{-1}{4}+\frac{2}{3}=\frac{-1\times3+4\times2}{4\times3}=\grn{\frac{5}{12}}", "−3 + 8 = 5")
    step(f, r"\left(-\frac{2}{3}\right)\times\frac{9}{4}=-\frac{18}{12}=\grn{-\frac{3}{2}}", "different signs: negative")
    step(f, r"\left(-\frac{1}{2}\right)\div\left(-\frac{1}{4}\right)=\frac{1}{2}\times\frac{4}{1}=\grn{2}",
         "same signs: positive")
    ch.check(Fr(-1, 4) + Fr(2, 3), Fr(5, 12))
    ch.check(Fr(-2, 3) * Fr(9, 4), Fr(-3, 2))
    ch.check(Fr(-1, 2) / Fr(-1, 4), 2)
    ch.term("negative fraction", "a fraction below zero; -a/b = (-a)/b = a/(-b)")


def mixed_add(ch):
    f = flow(ch)
    heading(f, "Mixed numbers")
    f.p("Change each mixed number to an improper fraction, then use the formula as normal.", 13.5, gap=6)
    example(f, "$1\\tfrac12+2\\tfrac34$.")
    step(f, r"=\frac{3}{2}+\frac{11}{4}=\frac{3\times4+2\times11}{2\times4}=\frac{34}{8}", "improper, then the formula")
    step(f, r"=\frac{17}{4}=\grn{4\tfrac14}", "simplify; 17 ÷ 4 = 4 r 1")
    ch.check(1 + Fr(1, 2) + 2 + Fr(3, 4), Fr(34, 8))
    example(f, "$3\\tfrac14-1\\tfrac23$.")
    step(f, r"=\frac{13}{4}-\frac{5}{3}=\frac{13\times3-4\times5}{4\times3}=\frac{19}{12}=\grn{1\tfrac{7}{12}}",
         "improper, then the formula")
    ch.check(3 + Fr(1, 4) - (1 + Fr(2, 3)), Fr(19, 12))
    ch.check(Fr(19, 12), 1 + Fr(7, 12))


def multiply(ch):
    f = flow(ch)
    heading(f, "Multiplying", room=520)
    f.eq(r"\frac{a}{b}\times\frac{c}{d}=\frac{ac}{bd}", 26, gap=8)
    f.p("Multiply across. Whole numbers go over 1; mixed numbers become improper fractions first. "
        "\"$\\times$\" with fractions means \"of\": $\\frac23\\times\\frac45$ is two thirds of four fifths.",
        13.5, gap=6)
    example(f, "Lecture 1, $\\frac23\\times\\frac45$.")
    step(f, r"\frac{2}{3}\times\frac{4}{5}=\frac{2\times4}{3\times5}=\grn{\frac{8}{15}}", "ac over bd")
    ch.check(Fr(2, 3) * Fr(4, 5), Fr(8, 15))
    f.p("{y:Optional shortcut (cross-cancelling):} before multiplying you may divide any top and any "
        "bottom by a common factor, to keep the numbers small. Only across $\\times$, never $+$ or $-$.",
        13, C.GREY, gap=6)
    example(f, "cross-cancelling, $\\frac34\\times\\frac29$.")
    step(f, r"\frac{\cancel{3}^{\,1}}{\cancel{4}_{\,2}}\times\frac{\cancel{2}^{\,1}}{\cancel{9}_{\,3}}"
            r"=\frac{1\times1}{2\times3}=\grn{\frac16}", "3 with 9 (÷3); 2 with 4 (÷2)", size=24)
    ch.check(Fr(3, 4) * Fr(2, 9), Fr(1, 6))
    example(f, "a whole number, $3\\times\\frac25$.")
    step(f, r"\frac{3}{1}\times\frac{2}{5}=\frac{6}{5}=\grn{1\tfrac15}", "3 = 3/1")
    ch.check(3 * Fr(2, 5), Fr(6, 5))
    example(f, "mixed numbers, $1\\tfrac12\\times2\\tfrac12$.")
    step(f, r"=\frac{3}{2}\times\frac{5}{2}=\frac{15}{4}=\grn{3\tfrac34}", "change to improper first")
    ch.check((1 + Fr(1, 2)) * (2 + Fr(1, 2)), Fr(15, 4))
    f.p("{R:Not} $1\\times2+\\frac12\\times\\frac12=2\\tfrac14$. Multiplying the wholes and the parts "
        "separately misses the cross terms (like expanding brackets, Chapter 11).", 13.5, gap=10)
    rule_box(f, "a fraction of an amount", [
        "\"$\\frac{a}{b}$ of $N$\" means $\\frac{a}{b}\\times N$: divide $N$ by the bottom, then multiply by "
        "the top.",
    ], CHOC)
    step(f, r"\frac35\text{ of }40=\frac{40}{5}\times3=8\times3=\grn{24}", "÷ bottom, × top")
    ch.check(Fr(3, 5) * 40, 24)
    ch.term("fraction of an amount", "a/b of N = (N ÷ b) × a")


def divide(ch):
    f = flow(ch)
    heading(f, "Dividing", room=520)
    f.eq(r"\frac{a}{b}\div\frac{c}{d}=\frac{a}{b}\times\frac{d}{c}=\frac{ad}{bc}", 26, gap=8)
    f.p("Change ÷ to ×, flip the {B:second} fraction only, then multiply across. Whole numbers go over 1 "
        "($4=\\frac41$, flipped $\\frac14$); mixed numbers become improper fractions first.", 13.5, gap=6)
    f.p("The {B:reciprocal} of a fraction is the fraction flipped upside down: $\\frac23\\to\\frac32$, "
        "$4\\to\\frac14$. A number times its reciprocal is always 1.", 13.5, gap=6)
    ch.check(Fr(2, 3) * Fr(3, 2), 1)
    ch.term("reciprocal", "a fraction flipped upside down: the reciprocal of 4/5 is 5/4, of 4 (= 4/1) is 1/4")
    example(f, "Lecture 1, $\\frac23\\div\\frac45$.")
    step(f, r"\frac{2}{3}\div\frac{4}{5}=\frac{2}{3}\times\frac{5}{4}", "keep, change, flip")
    step(f, r"=\frac{10}{12}=\grn{\frac{5}{6}}", "multiply, then simplify ÷ 2")
    ch.check(Fr(2, 3) / Fr(4, 5), Fr(5, 6))
    example(f, "dividing by a whole number, $\\frac23\\div4$.")
    step(f, r"\frac{2}{3}\div\frac{4}{1}=\frac{2}{3}\times\frac{1}{4}=\frac{2}{12}=\grn{\frac16}", "4 = 4/1, flipped 1/4")
    ch.check(Fr(2, 3) / 4, Fr(1, 6))
    example(f, "mixed numbers, $2\\tfrac12\\div1\\tfrac14$.")
    step(f, r"=\frac{5}{2}\div\frac{5}{4}=\frac{5}{2}\times\frac{4}{5}=\frac{20}{10}=\grn{2}", "improper first")
    ch.check((2 + Fr(1, 2)) / (1 + Fr(1, 4)), 2)
    f.p("{B:Why flipping works:} $\\frac{c}{d}\\times\\frac{d}{c}=1$, so multiplying by $\\frac{d}{c}$ undoes "
        "multiplying by $\\frac{c}{d}$, which is exactly what dividing by $\\frac{c}{d}$ does. "
        "E.g. $3\\div\\frac14=3\\times4=12$: twelve quarters in 3.", 13.5, gap=8)
    ch.check(3 / Fr(1, 4), 12)
    f.p("{G:Sense check:} dividing by a number less than 1 makes the answer bigger; dividing by a "
        "number more than 1 makes it smaller.", 13.5)


def compare(ch):
    f = flow(ch)
    heading(f, "Comparing fractions")
    f.eq(r"\frac{a}{b}>\frac{c}{d}\iff ad>bc\qquad(\text{positive }b,\ d)", 24, gap=8)
    f.p("Cross-multiply and compare $ad$ with $bc$. It's the top of the subtraction formula: "
        "$\\frac{a}{b}-\\frac{c}{d}=\\frac{ad-bc}{bd}$ is positive exactly when $ad>bc$. Or turn both into "
        "decimals (top ÷ bottom).", 13.5, gap=6)
    example(f, "Lecture 1, $\\frac{9}{17}$ or $\\frac{49}{97}$?")
    step(f, r"9\times97=873\qquad 49\times17=833", "each top × the OTHER bottom")
    step(f, r"873>833\ \Rightarrow\ \grn{\frac{9}{17}>\frac{49}{97}}", "")
    ch.check(9 * 97, 873)
    ch.check(49 * 17, 833)
    ch.check_true(Fr(9, 17) > Fr(49, 97))
    f.p("The lecture does it with decimals: $0.529>0.505$.", 13.5)


def order_ops(ch):
    f = flow(ch)
    heading(f, "Order of operations and whole numbers")
    rule_box(f, "order of operations with fractions", [
        "The usual order applies (Chapter 1): {B:brackets, powers, × and ÷ (left to right), + and − "
        "(left to right)}.",
        "A fraction bar groups like brackets: in $\\frac{1+2}{3+4}$, work out the top and the bottom "
        "first.",
        "\"Of\" means ×.",
    ], CHOC)
    step(f, r"\frac12+\frac13\times\frac34=\frac12+\frac14=\grn{\frac34}", "× first, then +")
    step(f, r"\left(\frac12+\frac13\right)\times\frac34=\frac56\times\frac34=\frac{15}{24}=\grn{\frac58}",
         "brackets first")
    ch.check(Fr(1, 2) + Fr(1, 3) * Fr(3, 4), Fr(3, 4))
    ch.check((Fr(1, 2) + Fr(1, 3)) * Fr(3, 4), Fr(5, 8))
    f.gap(4)
    f.p("{B:Whole numbers with fractions.} Write the whole number over 1, then use the formula:",
        13.5, gap=6)
    step(f, r"3+\frac25=\frac31+\frac25=\frac{3\times5+1\times2}{1\times5}=\grn{\frac{17}{5}}", "3 = 3/1")
    step(f, r"2-\frac34=\frac21-\frac34=\frac{2\times4-1\times3}{1\times4}=\grn{\frac54}", "2 = 2/1")
    ch.check(3 + Fr(2, 5), Fr(17, 5))
    ch.check(2 - Fr(3, 4), Fr(5, 4))
    f.p("{B:Fractions or decimals?} $\\frac13=0.333...$ never ends, so any decimal you write is slightly "
        "wrong. For exact work (algebra), {B:keep fractions}. For measured data (statistics), decimals "
        "are fine (Lecture 1).", 13.5)


def missing(ch):
    f = flow(ch)
    heading(f, "Find the missing number", room=500)
    rule_box(f, "finding an unknown fraction", [
        "Write the unknown as $?$ (or $x$).",
        "{B:Undo} the operation that was done to it, using the opposite operation on the known values: "
        "+ is undone by −, × is undone by ÷ (and the other way round).",
        "Then use the three formulas to work out the answer.",
        "Check by putting your answer back into the original question.",
    ], CHOC, numbered=True, tag="PROCEDURE")
    example(f, "$\\frac34=\\frac{?}{20}$.")
    step(f, r"4\times5=20\Rightarrow ?=3\times5=\grn{15}", "the bottom was × 5, so the top is × 5")
    ch.check(Fr(3, 4), Fr(15, 20))
    example(f, "$\\frac25+?=\\frac{9}{10}$.")
    step(f, r"?=\frac{9}{10}-\frac25=\frac{9\times5-10\times2}{10\times5}=\frac{25}{50}=\grn{\frac12}",
         "undo + with −")
    ch.check(Fr(9, 10) - Fr(2, 5), Fr(1, 2))
    example(f, "$?\\times\\frac34=\\frac12$.")
    step(f, r"?=\frac12\div\frac34=\frac12\times\frac43=\frac46=\grn{\frac23}", "undo × with ÷")
    ch.check(Fr(1, 2) / Fr(3, 4), Fr(2, 3))
    example(f, "$\\frac56\\div\\,?=\\frac53$.")
    step(f, r"?=\frac56\div\frac53=\frac56\times\frac35=\frac{15}{30}=\grn{\frac12}",
         "the unknown is the divisor: ? = 5/6 ÷ 5/3")
    ch.check(Fr(5, 6) / Fr(1, 2), Fr(5, 3))
    example(f, "$\\frac38$ of a number is 15. What is the number?")
    step(f, r"\frac38\times ?=15\ \Rightarrow\ ?=15\div\frac38=15\times\frac83=\grn{40}", "undo × with ÷")
    ch.check(15 / Fr(3, 8), 40)


def common_mistakes(ch):
    f = flow(ch)
    heading(f, "The mistakes to avoid", room=420)
    mistakes(f, [
        (r"\frac12+\frac13=\frac25", r"\frac12+\frac13=\frac{1\times3+2\times1}{2\times3}=\frac56",
         "adding tops and adding bottoms isn't the formula: use (ad + bc)/bd"),
        (r"\frac{\cancel{3}}{4}+\frac{1}{\cancel{3}}", r"\frac34+\frac13=\frac{9+4}{12}=\frac{13}{12}",
         "cross-cancelling only works across ×"),
        (r"\frac23\div\frac45=\frac32\times\frac45", r"\frac23\div\frac45=\frac23\times\frac54",
         "flip the SECOND fraction only"),
        (r"1\tfrac12\times2\tfrac12=2\tfrac14", r"\frac32\times\frac52=\frac{15}{4}=3\tfrac34",
         "change mixed numbers to improper fractions before × or ÷"),
        (r"\frac{2+4}{2+6}=\frac{4}{6}", r"\frac{2+4}{2+6}=\frac{6}{8}=\frac34",
         "cancel factors of the whole top and bottom, not single terms"),
    ])
    ch.check(Fr(3, 4) + Fr(1, 3), Fr(13, 12))


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Fraction = division", r"\frac{a}{b}=a\div b,\quad n=\frac{n}{1}", None),
        ("Equivalent fractions", r"\frac{a}{b}=\frac{a\times k}{b\times k}=\frac{a\div k}{b\div k}",
         "same non-zero $k$ on top and bottom; never + or −"),
        ("Simplify", None, "divide top and bottom by their HCF"),
        ("Mixed to improper", r"p\tfrac{a}{b}=\frac{pb+a}{b}", None),
        ("Add / subtract", r"\frac{a}{b}\pm\frac{c}{d}=\frac{ad\pm bc}{bd}", "plug in; simplify at the end if asked"),
        ("Multiply", r"\frac{a}{b}\times\frac{c}{d}=\frac{ac}{bd}", "multiply across"),
        ("Divide", r"\frac{a}{b}\div\frac{c}{d}=\frac{a}{b}\times\frac{d}{c}=\frac{ad}{bc}",
         "flip the second fraction only, then multiply across"),
        ("Reciprocal", r"\frac{a}{b}\to\frac{b}{a},\qquad \frac{a}{b}\times\frac{b}{a}=1", None),
        ("Compare", r"\frac{a}{b}>\frac{c}{d}\iff ad>bc", "for positive bottoms"),
        ("Negative fractions", r"-\frac{a}{b}=\frac{-a}{b}=\frac{a}{-b}", None),
        ("Fraction of an amount", r"\frac{a}{b}\text{ of }N=\frac{N}{b}\times a", None),
        ("Whole and mixed numbers", None, "whole number over 1; mixed number to improper; then the formula"),
    ], CHOC, title="Fraction rules")


def your_turn(ch):
    f = flow(ch)
    f.new_page()
    heading(f, "Your turn")
    f.p("Answers are in grey under each group; full working is on the next page.", 13, C.GREY, gap=10)
    groups = [
        ("Simplify and convert", ["Simplify 18/24", "Write 23/5 as a mixed number",
                                  "Write 3 2/7 as an improper fraction", "Which is bigger, 5/8 or 7/11?"],
         "1. 3/4   2. 4 3/5   3. 23/7   4. 7/11 (5×11 = 55 < 56 = 7×8)"),
        ("Add and subtract", ["2/9 + 5/9", "3/4 − 2/5", "5/6 + 3/8", "1/3 − 3/4", "4 1/5 − 2 2/3"],
         "5. 7/9   6. 7/20   7. 29/24 = 1 5/24   8. −5/12   9. 23/15 = 1 8/15"),
        ("Multiply and divide", ["4/9 × 3/8", "2 1/3 × 1 1/2", "5/6 ÷ 10/9", "3/4 ÷ 6", "1 1/4 ÷ 2 1/2"],
         "10. 1/6   11. 7/2 = 3 1/2   12. 3/4   13. 1/8   14. 1/2"),
        ("Mixed operations", ["1/2 + 2/3 × 3/4", "(1/2 + 2/3) × 3/4", "3/5 of 45", "−2/3 × 3/8"],
         "15. 1   16. 7/8   17. 27   18. −1/4"),
        ("Find the unknown", ["5/6 = ?/30", "? + 1/4 = 7/8", "? × 2/3 = 4/9", "3/4 of a number is 18. Find it.",
                              "2/5 ÷ ? = 4/5"],
         "19. 25   20. 5/8   21. 2/3   22. 24   23. 1/2"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 30)
        f.text(title, 14, CHOC, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)


def answers(ch):
    f = flow(ch)
    f.new_page()
    heading(f, "Answers, worked")
    ans = [
        ("1.", r"\frac{18\div6}{24\div6}=\frac34", Fr(18, 24), Fr(3, 4)),
        ("2.", r"23\div5=4\text{ r }3\Rightarrow4\tfrac35", Fr(23, 5), 4 + Fr(3, 5)),
        ("3.", r"\frac{3\times7+2}{7}=\frac{23}{7}", 3 + Fr(2, 7), Fr(23, 7)),
        ("4.", r"5\times11=55<56=7\times8\Rightarrow\frac{7}{11}\text{ is bigger}", None, None),
        ("5.", r"\frac{2+5}{9}=\frac79", Fr(2, 9) + Fr(5, 9), Fr(7, 9)),
        ("6.", r"\frac{3\times5-4\times2}{4\times5}=\frac{7}{20}", Fr(3, 4) - Fr(2, 5), Fr(7, 20)),
        ("7.", r"\frac{5\times8+6\times3}{6\times8}=\frac{58}{48}=\frac{29}{24}=1\tfrac{5}{24}",
         Fr(5, 6) + Fr(3, 8), Fr(29, 24)),
        ("8.", r"\frac{1\times4-3\times3}{3\times4}=-\frac{5}{12}", Fr(1, 3) - Fr(3, 4), Fr(-5, 12)),
        ("9.", r"\frac{21}{5}-\frac{8}{3}=\frac{63-40}{15}=\frac{23}{15}=1\tfrac{8}{15}",
         4 + Fr(1, 5) - (2 + Fr(2, 3)), Fr(23, 15)),
        ("10.", r"\frac{4\times3}{9\times8}=\frac{12}{72}=\frac16", Fr(4, 9) * Fr(3, 8), Fr(1, 6)),
        ("11.", r"\frac73\times\frac32=\frac{21}{6}=\frac72=3\tfrac12", (2 + Fr(1, 3)) * (1 + Fr(1, 2)), Fr(7, 2)),
        ("12.", r"\frac56\times\frac{9}{10}=\frac{45}{60}=\frac34", Fr(5, 6) / Fr(10, 9), Fr(3, 4)),
        ("13.", r"\frac34\times\frac16=\frac{3}{24}=\frac18", Fr(3, 4) / 6, Fr(1, 8)),
        ("14.", r"\frac54\div\frac52=\frac54\times\frac25=\frac{10}{20}=\frac12", (1 + Fr(1, 4)) / (2 + Fr(1, 2)), Fr(1, 2)),
        ("15.", r"\frac12+\frac{6}{12}=\frac12+\frac12=1", Fr(1, 2) + Fr(2, 3) * Fr(3, 4), 1),
        ("16.", r"\frac76\times\frac34=\frac{21}{24}=\frac78", (Fr(1, 2) + Fr(2, 3)) * Fr(3, 4), Fr(7, 8)),
        ("17.", r"\frac{45}{5}\times3=9\times3=27", Fr(3, 5) * 45, 27),
        ("18.", r"-\frac{6}{24}=-\frac14", Fr(-2, 3) * Fr(3, 8), Fr(-1, 4)),
        ("19.", r"6\times5=30\Rightarrow ?=5\times5=25", Fr(5, 6), Fr(25, 30)),
        ("20.", r"?=\frac78-\frac14=\frac{28-8}{32}=\frac{20}{32}=\frac58", Fr(7, 8) - Fr(1, 4), Fr(5, 8)),
        ("21.", r"?=\frac49\div\frac23=\frac49\times\frac32=\frac{12}{18}=\frac23", Fr(4, 9) / Fr(2, 3), Fr(2, 3)),
        ("22.", r"?=18\div\frac34=18\times\frac43=24", 18 / Fr(3, 4), 24),
        ("23.", r"?=\frac25\div\frac45=\frac25\times\frac54=\frac{10}{20}=\frac12", Fr(2, 5) / Fr(4, 5), Fr(1, 2)),
    ]
    ch.check_true(Fr(7, 11) > Fr(5, 8))
    for n, lat, got, exp in ans:
        if got is not None:
            ch.check(got, exp)
        w, h, _ = f.pg.eq_size(lat, 17)
        y = f.reserve(h + 10)
        pg = f.pg
        pg.text(L, y + h / 2 - 8, n, 13, CHOC, F.BOLD)
        pg.eq(L + 34, y, lat, 17)


def rules_card(ch):
    """Closing page: the four operations on one card."""
    pg = ch.new_page(bg="#fbf5ee")
    pg.rect(40, 40, 515, 730, CHOC, 3, fillcolor="#6b3f1f", r=18)
    pg.rect(58, 58, 479, 694, "#e6c9a3", 1.5, r=12, dash=(6, 4))
    pg.text(297, 78, "FRACTION RULES CARD", 26, "#f6e3c6", F.BOLD, align="center")
    pg.note(297, 112, "cut it out, keep it next to you", "#e6c9a3", 19, align="center")
    rules = [
        ("ADD / SUBTRACT", r"\frac{a}{b}\pm\frac{c}{d}=\frac{ad\pm bc}{bd}",
         r"\frac{1}{2}+\frac{1}{3}=\frac{1\times3+2\times1}{2\times3}=\frac{5}{6}"),
        ("MULTIPLY", r"\frac{a}{b}\times\frac{c}{d}=\frac{ac}{bd}", r"\frac{2}{3}\times\frac{4}{5}=\frac{8}{15}"),
        ("DIVIDE", r"\frac{a}{b}\div\frac{c}{d}=\frac{a}{b}\times\frac{d}{c}=\frac{ad}{bc}",
         r"\frac{2}{3}\div\frac{4}{5}=\frac{2}{3}\times\frac{5}{4}=\frac{10}{12}"),
        ("SIMPLIFY (OPTIONAL)", r"\frac{a\times k}{b\times k}=\frac{a}{b}",
         r"\frac{10}{12}=\frac{10\div2}{12\div2}=\frac{5}{6}"),
    ]
    y = 160
    for head, gen, lat in rules:
        pg.rect(80, y, 435, 128, "#f6e3c6", 1.2, fillcolor="#fbf1e2", r=10)
        pg.text(100, y + 12, head, 14, CHOC, F.BOLD)
        pg.eq(297, y + 28, gen, 20, align="center")
        pg.eq(297, y + 90, lat, 14, CHOC, align="center")
        y += 138
    pg.note(297, y + 2, "whole numbers over 1, mixed numbers improper, then plug in", "#ffd9a0", 20,
            align="center")


def build(ch):
    title_page(ch)
    what_is(ch)
    at_a_glance(ch)
    why_formula(ch)
    add_subtract(ch)
    negatives(ch)
    multiply(ch)
    divide(ch)
    equivalent(ch)
    improper(ch)
    mixed_add(ch)
    compare(ch)
    order_ops(ch)
    missing(ch)
    common_mistakes(ch)
    summary(ch)
    your_turn(ch)
    answers(ch)
    rules_card(ch)
