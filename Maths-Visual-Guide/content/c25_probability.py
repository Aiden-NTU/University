"""Chapter 25 - Probability and Bayes (Lecture 8). Everything happens on a 6x6 grid of dice outcomes:
probability = shaded squares / 36, 'not' = the unshaded rest, 'and' = the overlap of two stripes,
'or' = both stripes (don't count the corner twice), 'given' = zoom into one stripe and treat it as the
whole world. Then the lecture's urn and hair tables, and the mammogram puzzle as 1000 little people."""
from fractions import Fraction as Fr

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step, title_block

ORDER = 25
NUM = 25
TITLE = "Probability and Bayes"
SHORT = "Probability"
SLUG = "Probability"
ACCENT = C.GREEN
REQUIRES = ["set", "element", "subset", "intersection", "union", "complement", "venn-diagram", "empty-set",
            "fraction", "simplify-fraction", "multiply-fractions", "add-fractions", "percentage", "proportion",
            "frequency", "decimal-to-fraction"]
INTRODUCES = ["probability", "sample-space", "event", "complement-rule", "joint-probability", "mutually-exclusive",
              "addition-rule", "conditional-probability", "independence", "two-way-table", "marginal-probability",
              "bayes-theorem", "prior-posterior", "multiplication-rule", "tree-diagram",
              "law-of-total-probability"]

PAPER = "#fafdf9"


def icon(pg, x0, y0):
    pg.rect(x0 + 1, y0 + 1, 16, 16, C.GREEN, 1.4, r=3)
    for (a, b) in [(5, 5), (13, 13), (9, 9)]:
        pg.dot(x0 + a, y0 + b, 1.6, C.GREEN)


def sec(f, t_, **kw):
    section(f, t_, C.GREEN, icon, **kw)


def ex(f, s):
    f.need(90)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


def die(pg, x, y, s, n, col=C.INK, fill="#ffffff"):
    pg.rect(x, y, s, s, col, 1.2, fillcolor=fill, r=s * 0.18)
    spots = {1: [(.5, .5)], 2: [(.28, .28), (.72, .72)], 3: [(.25, .25), (.5, .5), (.75, .75)],
             4: [(.28, .28), (.72, .28), (.28, .72), (.72, .72)],
             5: [(.25, .25), (.75, .25), (.5, .5), (.25, .75), (.75, .75)],
             6: [(.28, .22), (.72, .22), (.28, .5), (.72, .5), (.28, .78), (.72, .78)]}
    for a, b in spots[n]:
        pg.dot(x + a * s, y + b * s, s * 0.08, col)


def grid(pg, x, y, c, shade, labels=True, text=None):
    """6x6 outcome grid: column = red die, row = blue die. shade(r, b) -> colour or None."""
    for rd in range(1, 7):
        for bd in range(1, 7):
            col = shade(rd, bd)
            cx, cy = x + (rd - 1) * c, y + (bd - 1) * c
            pg.rect(cx, cy, c, c, C.GREY, 0.4, fillcolor=col)
            if text:
                s_ = text(rd, bd)
                if s_:
                    pg.text(cx + c / 2, cy + c / 2 - 5, s_, 8, C.INK, align="center", solid=False)
    if labels:
        for k in range(1, 7):
            pg.text(x + (k - 0.5) * c, y - 13, str(k), 9, C.RED, F.BOLD, align="center", solid=False)
            pg.text(x - 9, y + (k - 0.5) * c - 6, str(k), 9, C.BLUE, F.BOLD, align="center", solid=False)
    pg.rect(x, y, 6 * c, 6 * c, C.INK, 1)


def count(pred):
    return sum(1 for a in range(1, 7) for b in range(1, 7) if pred(a, b))


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 25, "Probability and Bayes", "count the squares", C.GREEN, PAPER)
    die(pg, L + 20, 210, 44, 6, C.RED)
    die(pg, L + 76, 222, 44, 1, C.BLUE)
    pg.note(L + 10, 275, "two dice = 36 possible\nresults, all equally likely", C.GREEN, 15)
    grid(pg, L + 260, 205, 15, lambda a, b: C.LIGHT[C.GREEN] if a + b == 7 else None)
    pg.note(L + 360, 215, "the 6 ways to\nroll a total of 7:\n6 out of 36", C.GREEN, 15)
    f = ch.flow(top=350)
    f.p("Probability sounds like guesswork, but most of it is {B:counting}. List every possible result, "
        "shade the ones you care about, and the probability is {B:shaded ÷ total}.", 14, gap=10)
    f.p("This chapter uses one picture for almost everything: the {B:6 × 6 grid of two dice}. With it "
        "you can {B:see} what \"not\", \"and\", \"or\" and \"given that\" mean, and then the lecture's "
        "famous puzzle (only 15% of doctors got it right) becomes a matter of counting little people.",
        14, gap=10)
    f.p("{y:Goes with} {B:Lecture 8} {y:(sample space, complements, joint, exclusive and conditional "
        "probability, independence, the urn, Bayes' theorem, the mammogram).}", 12.5)


def basics(ch):
    f = flow(ch)
    sec(f, "Probability = shaded squares ÷ all squares")
    rule_box(f, "probability", [
        "For equally likely outcomes: $p(E)=\\dfrac{\\text{number of outcomes in }E}{\\text{total number of "
        "outcomes}}$.",
        "$0\\le p(E)\\le1$: 0 means impossible, 1 means certain. The probabilities of all the possible "
        "outcomes add up to 1.",
        "{B:Complement:} $p(\\text{not }E)=p(E')=1-p(E)$.",
    ], C.GREEN)
    f.p("Roll a red die and a blue die. Every square below is one possible result: column = red die, "
        "row = blue die. The whole grid is the {B:sample space} $S$ (every possible outcome). A set of "
        "outcomes you're interested in is an {B:event} $E$, a subset of $S$ (Chapter 6).", 14, gap=18)
    y_ = f.reserve(130)
    pg = f.pg
    grid(pg, L + 20, y_ + 4, 18, lambda a, b: C.LIGHT[C.GREEN] if a + b == 7 else None,
         text=lambda a, b: "7" if a + b == 7 else "")
    pg.note(L + 150, y_, "E = \"the total is 7\"", C.GREEN, 16)
    pg.eq(L + 150, y_ + 30, r"p(E)=\frac{\text{squares in }E}{\text{squares in }S}=\frac{6}{36}=\frac16", 18)
    pg.note(L + 150, y_ + 84, "read p(E) as \"the probability of E\"", C.GREY, 14)
    ch.check(Fr(count(lambda a, b: a + b == 7), 36), Fr(1, 6))
    ch.term("sample space", "the set S of every possible outcome")
    ch.term("event", "a set of outcomes you are interested in; a subset of the sample space")
    ch.term("probability", "how likely an event is, from 0 (impossible) to 1 (certain); shaded ÷ total when outcomes are equally likely")
    ch.symbol(r"p(E)", "p of E", "the probability that event E happens")
    f.p("Probabilities always sit between 0 and 1 (or 0% and 100%):", 14, gap=12)
    y_ = f.reserve(50)
    pg = f.pg
    pg.line(L + 20, y_ + 16, L + 470, y_ + 16, C.INK, 1.4)
    for v, s_ in [(0, "impossible\n(total 13)"), (1 / 6, "1/6\n(total 7)"), (0.5, "evens\n(red is odd)"),
                  (5 / 6, "5/6\n(not 7)"), (1, "certain\n(≤ 12)")]:
        xx = L + 20 + 450 * v
        pg.line(xx, y_ + 10, xx, y_ + 22, C.INK, 1.2)
        pg.text(xx, y_ + 24, s_, 9, C.GREEN, align="center", solid=False)
    pg.text(L + 20, y_ - 4, "0", 11, C.INK, F.BOLD, align="center")
    pg.text(L + 470, y_ - 4, "1", 11, C.INK, F.BOLD, align="center")
    f.gap(16)
    f.p("{b:Rule 1, complements:} the squares {B:not} in $E$ are everything else, so", 14, gap=6)
    step(f, r"p(\text{not }E)=1-p(E)", "not a total of 7: 1 − 1/6 = 5/6", size=19)
    ch.check(1 - Fr(1, 6), Fr(count(lambda a, b: a + b != 7), 36))
    ch.term("complement rule", "p(E doesn't happen) = 1 − p(E)")
    f.p("Handy when \"not\" is easier to count: $p(\\text{at least one six}) = 1 - p(\\text{no sixes}) = "
        "1 - \\frac{25}{36} = \\frac{11}{36}$.", 14)
    ch.check(1 - Fr(25, 36), Fr(count(lambda a, b: a == 6 or b == 6), 36))


def and_or(ch):
    f = flow(ch)
    sec(f, "AND is the overlap, OR is both stripes", room=520)
    rule_box(f, "AND and OR", [
        "$p(A\\cap B)$ = the probability that A {B:and} B both happen (the overlap).",
        "$p(A\\cup B)$ = the probability that A {B:or} B happens (either one, or both).",
        "{B:General addition rule}, always true: $p(A\\cup B)=p(A)+p(B)-p(A\\cap B)$.",
        "{B:Mutually exclusive} events can't both happen: $p(A\\cap B)=0$, so $p(A\\cup B)=p(A)+p(B)$.",
    ], C.GREEN)
    f.p("Let $E$ = \"red die shows 6\" (a column) and $F$ = \"blue die shows 6\" (a row):", 14, gap=18)
    y_ = f.reserve(130)
    pg = f.pg
    c = 17

    def sh_and(a, b):
        if a == 6 and b == 6:
            return C.LIGHT[C.PURPLE]
        if a == 6:
            return C.LIGHT[C.RED]
        if b == 6:
            return C.LIGHT[C.BLUE]
        return None
    grid(pg, L + 20, y_ + 4, c, sh_and)
    pg.ring(L + 20 + 5 * c - 3, y_ + 4 + 5 * c - 3, c + 6, c + 6, C.PURPLE)
    pg.note(L + 140, y_, "E (red column): 6 squares\nF (blue row): 6 squares\nboth (purple corner): 1 square",
            C.INK, 15)
    pg.eq(L + 140, y_ + 70, r"p(E\cap F)=\tfrac1{36}", 17, C.PURPLE)
    pg.eq(L + 300, y_ + 70, r"p(E\cup F)=\tfrac{6+6-1}{36}=\tfrac{11}{36}", 17, C.GREEN)
    ch.check(Fr(count(lambda a, b: a == 6 and b == 6), 36), Fr(1, 36))
    ch.check(Fr(count(lambda a, b: a == 6 or b == 6), 36), Fr(11, 36))
    f.p("{b:AND} (both happen, the {B:joint} probability) is the {B:overlap}: $\\cap$, the intersection "
        "from Chapter 6. {b:OR} (at least one happens) is {B:everything shaded}: $\\cup$, the union. "
        "Counting the column (6) and the row (6) counts the corner {B:twice}, so subtract it once:",
        14, gap=6)
    step(f, r"p(E\cup F)=p(E)+p(F)-p(E\cap F)", "Lecture 8's Rule 3", size=19, color=C.GREEN)
    ch.formula(r"p(E\cup F)=p(E)+p(F)-p(E\cap F)", "addition rule (OR)")
    ch.term("joint probability", "the probability that two events both happen, p(E ∩ F)")
    ch.term("addition rule", "p(E or F) = p(E) + p(F) − p(E and F)")
    f.p("{b:Mutually exclusive} events can't happen together: \"total is 2\" and \"total is 12\" have no "
        "squares in common, so $p(E\\cap F) = 0$ (Rule 2) and the OR rule becomes simply "
        "$p(E) + p(F) = \\frac1{36} + \\frac1{36}$.", 14)
    ch.term("mutually exclusive", "events that cannot both happen: p(E and F) = 0")


def given(ch):
    f = flow(ch)
    sec(f, "\"Given that\": zoom in, and the stripe becomes the world", room=520)
    rule_box(f, "conditional probability", [
        "$p(A\\,|\\,B)$ = the probability of A {B:given that} B has happened. B becomes the whole sample "
        "space.",
        "$p(A\\,|\\,B)=\\dfrac{p(A\\cap B)}{p(B)}$  (as long as $p(B)\\neq0$).",
        "{B:Multiplication rule} (the same rule turned round): $p(A\\cap B)=p(B)\\times p(A\\,|\\,B)"
        "=p(A)\\times p(B\\,|\\,A)$.",
    ], C.GREEN)
    f.p("Your friend rolls, peeks, and says \"the red die is a 6\". What's the chance the total is 10 or "
        "more {B:now}? The bar $|$ is read \"{B:given}\": $p(E\\,|\\,F)$ = probability of E given that F "
        "has happened.", 14, gap=18)
    y_ = f.reserve(150)
    pg = f.pg
    c = 17

    def sh(a, b):
        if a + b >= 10:
            return C.LIGHT[C.GREEN] if a == 6 else C.LIGHT[C.GREY]
        return None
    grid(pg, L + 20, y_ + 4, c, sh, text=lambda a, b: str(a + b) if a + b >= 10 else "")
    pg.rect(L + 20 + 5 * c, y_ + 4, c, 6 * c, C.RED, 2)
    pg.arrow(L + 20 + 6 * c + 6, y_ + 50, L + 200, y_ + 50, C.RED, 1.4, head=6)
    zx = L + 210
    for bd in range(1, 7):
        yy = y_ + 4 + (bd - 1) * 20
        ok = 6 + bd >= 10
        pg.rect(zx, yy, 60, 20, C.RED, 0.8, fillcolor=C.LIGHT[C.GREEN] if ok else "#ffffff")
        pg.text(zx + 30, yy + 4, f"6 + {bd} = {6 + bd}", 9, C.INK, align="center")
    pg.note(zx + 72, y_ + 10, "F = \"red is 6\" is the\nnew sample space:\n6 squares, not 36.\n3 of them "
            "reach 10+.", C.RED, 15)
    ch.check(Fr(count(lambda a, b: a == 6 and a + b >= 10), count(lambda a, b: a == 6)), Fr(1, 2))
    ch.check(Fr(count(lambda a, b: a + b >= 10), 36), Fr(1, 6))
    f.p("Without the peek, $p(\\text{10+}) = \\frac{6}{36} = \\frac16$. With it, $p(\\text{10+}\\,|\\,\\text{red "
        "6}) = \\frac36 = \\frac12$. New information {B:changes} the probability. Lecture 8: "
        "{B:\"F is the new S!\"} As a formula, count the overlap inside F, as a fraction of F:", 14, gap=6)
    step(f, r"p(E\,|\,F)=\frac{p(E\cap F)}{p(F)}=\frac{3/36}{6/36}=\frac12", "Rule 4", size=19, color=C.GREEN)
    ch.formula(r"p(E\,|\,F)=\frac{p(E\cap F)}{p(F)}", "conditional probability")
    ch.term("conditional probability", "p(E | F): the probability of E once you know F happened; F becomes the new sample space")
    ch.symbol(r"p(E\,|\,F)", "p of E given F", "probability of E, knowing that F has happened")
    f.p("Rearranged: $p(E\\cap F) = p(F)\\times p(E\\,|\\,F)$: the chance of both = the chance of the "
        "first × the chance of the second {B:once the first has happened}.", 14)


def independence(ch):
    f = flow(ch)
    sec(f, "Independent: when the peek tells you nothing", room=520)
    rule_box(f, "independent events", [
        "A and B are {B:independent} when knowing that one happened doesn't change the probability of "
        "the other: $p(A\\,|\\,B)=p(A)$.",
        "Then, and only then: $p(A\\cap B)=p(A)\\times p(B)$.",
        "{B:Test:} work out $p(A)\\times p(B)$ and compare it with $p(A\\cap B)$. Equal: independent. "
        "Not equal: dependent.",
    ], C.GREEN)
    f.p("Two events are {B:independent} if knowing one doesn't change the other: $p(E\\,|\\,F) = p(E)$. "
        "Then the multiplication rule becomes simply $p(E\\cap F) = p(E)\\times p(F)$. Lecture 8's "
        "cards: {B:draw two cards; what's the chance both are hearts?}", 14, gap=12)
    for title, second, tot, ans, col in [("put the first card back and shuffle", 13, 52, Fr(1, 16), C.GREEN),
                                         ("keep the first card out", 12, 51, Fr(3, 51), C.ORANGE)]:
        y_ = f.reserve(84)
        pg = f.pg
        pg.text(L, y_, title, 13, col, F.BOLD)
        for k, (h_, t_) in enumerate([(13, 52), (second, tot)]):
            yy = y_ + 22 + k * 26
            bw = 300 / 52
            for i in range(t_):
                pg.rect(L + 60 + i * bw, yy, bw - 0.6, 18, C.RED if i < h_ else C.GREY, 0.3,
                        fillcolor=C.LIGHT[C.RED] if i < h_ else "#ffffff")
            pg.text(L, yy + 3, ["card 1", "card 2"][k], 10, C.GREY)
            pg.text(L + 370, yy + 3, f"{h_}/{t_} hearts", 11, C.RED)
        pg.eq(L + 450, y_ + 40, r"=\tfrac{%d}{%d}" % (ans.numerator, ans.denominator), 16, col, valign="middle")
    ch.check(Fr(13, 52) * Fr(13, 52), Fr(1, 16))
    ch.check(Fr(13, 52) * Fr(12, 51), Fr(3, 51))
    f.p("With replacement the deck is identical for card 2: {B:independent}, $\\frac14\\times\\frac14 = "
        "\\frac1{16} = 0.0625$. Without replacement one heart has gone: {B:dependent}, "
        "$\\frac14\\times\\frac{12}{51} = \\frac{3}{51} = \\frac1{17} \\approx 0.0588$.", 14, gap=8)
    ch.check_num(3 / 51, 0.0588, tol=0.0001)
    ch.term("independent events", "knowing one happened doesn't change the other's probability; then p(E and F) = p(E) × p(F)")
    f.p("{b:Sun and red cars} (independent): $p(\\text{sun}) = 0.4$, $p(\\text{red car}) = 0.2$, so "
        "$p(\\text{both}) = 0.08$. {b:Sun and umbrellas} (dependent): the weather obviously changes "
        "your chance of seeing an umbrella, so you {B:can't} just multiply.", 14)
    ch.check_num(0.4 * 0.2, 0.08)


def contrast(ch):
    f = flow(ch)
    sec(f, "Exclusive or independent? The rules side by side", room=520)
    f.p("These two words sound alike and get mixed up constantly. They mean very different things:",
        13.5, gap=8)
    rules_table(f, ["", "Mutually exclusive", "Independent"], [
        ["{B:meaning}", "A and B can't both happen", "one happening doesn't change the chance of the other"],
        ["{B:AND}", "$p(A\\cap B)=0$", "$p(A\\cap B)=p(A)\\,p(B)$"],
        ["{B:OR}", "$p(A\\cup B)=p(A)+p(B)$", "$p(A\\cup B)=p(A)+p(B)-p(A)\\,p(B)$"],
        ["{B:GIVEN}", "$p(A\\,|\\,B)=0$", "$p(A\\,|\\,B)=p(A)$"],
        ["{B:dice example}", "total is 2 / total is 12", "red shows 6 / blue shows 6"],
    ], [100, 165, 230], C.GREEN)
    rule_box(f, "always true, for any two events", [
        "General addition rule: $p(A\\cup B)=p(A)+p(B)-p(A\\cap B)$.",
        "Conditional probability: $p(A\\,|\\,B)=\\dfrac{p(A\\cap B)}{p(B)}$, so $p(A\\cap B)=p(B)\\,p(A\\,|\\,B)$.",
        "The two special cases in the table are these general rules with $p(A\\cap B)$ replaced by 0 "
        "or by $p(A)\\,p(B)$.",
    ], C.GREEN)
    rule_box(f, "exclusive events are never independent", [
        "If A and B are mutually exclusive and both have non-zero probability, they {R:cannot} be "
        "independent: $p(A\\cap B)=0$ but $p(A)\\,p(B)>0$.",
        "Knowing A happened tells you B definitely {B:didn't}: the biggest change of all.",
    ], C.GREEN)
    f.p("{b:Check on the dice:} \"red shows 1\" and \"red shows 2\" are exclusive. $p(\\text{both}) = 0$, "
        "but $\\frac16\\times\\frac16=\\frac1{36}$. Not equal, so they are dependent.", 13.5, gap=8)
    ch.check(Fr(count(lambda a, b: a == 1 and a == 2), 36), 0)
    ch.check(Fr(count(lambda a, b: a == 1), 36) * Fr(count(lambda a, b: a == 2), 36), Fr(1, 36))
    ch.check(Fr(count(lambda a, b: a == 6 and b == 6), 36),
             Fr(count(lambda a, b: a == 6), 36) * Fr(count(lambda a, b: b == 6), 36))
    mistakes(f, [
        (r"p(A\cup B)=p(A)+p(B)", r"p(A\cup B)=p(A)+p(B)-p(A\cap B)",
         "only drop the overlap when A and B are mutually exclusive"),
        (r"p(A\cap B)=p(A)\,p(B)", r"p(A\cap B)=p(B)\,p(A\,|\,B)",
         "multiply the plain probabilities only when A and B are independent"),
        (r"p(A\,|\,B)=p(B\,|\,A)", r"p(A\,|\,B)=\frac{p(B\,|\,A)\,p(A)}{p(B)}",
         "a conditional can't simply be turned round (Bayes, later in the chapter)"),
    ])


def partial(ch):
    f = flow(ch)
    sec(f, "Find the missing probability", room=520)
    rule_box(f, "partial-information problems", [
        "Write down every probability you are given, in symbols: $p(A)=0.5$, $p(A\\cup B)=0.7$, ...",
        "Pick the rule that links them: the addition rule (OR), the conditional / multiplication rule "
        "(GIVEN), or $p(A\\cap B)=p(A)\\,p(B)$ if you're told they're independent.",
        "Substitute and solve for the unknown. A Venn diagram or a two-way table helps you see it.",
        "Sense-check: every probability must be between 0 and 1.",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    ex(f, "$p(A)=0.5$, $p(B)=0.4$, $p(A\\cup B)=0.7$. Find $p(A\\cap B)$. Are A and B independent?")
    step(f, r"0.7=0.5+0.4-p(A\cap B)\ \Rightarrow\ p(A\cap B)=0.2", "addition rule", size=18)
    step(f, r"p(A)\,p(B)=0.5\times0.4=0.2=p(A\cap B)", "equal, so independent ✓", size=18, color=C.GREEN)
    pab = Fr("0.5") + Fr("0.4") - Fr("0.7")
    ch.check(pab, Fr("0.2"))
    ch.check(Fr("0.5") * Fr("0.4"), pab)
    ex(f, "$p(A\\,|\\,B)=0.3$ and $p(B)=0.6$. Find $p(A\\cap B)$.")
    step(f, r"p(A\cap B)=p(B)\,p(A\,|\,B)=0.6\times0.3=0.18", "multiplication rule", size=18, color=C.GREEN)
    ch.check(Fr("0.6") * Fr("0.3"), Fr("0.18"))
    ex(f, "A and B are independent, $p(A)=0.3$ and $p(A\\cup B)=0.65$. Find $p(B)$.")
    step(f, r"0.65=0.3+p-0.3p", "addition rule with p(A ∩ B) = 0.3p", size=18)
    step(f, r"0.35=0.7p\ \Rightarrow\ p(B)=0.5", "", size=18, color=C.GREEN)
    pb = sp.symbols("p")
    ch.check(sp.solve(sp.Rational(3, 10) + pb - sp.Rational(3, 10) * pb - sp.Rational(13, 20), pb),
             [sp.Rational(1, 2)])
    ex(f, "200 people: 40% wear glasses, 15% are left-handed, and 30% of the glasses-wearers are "
          "left-handed. Complete the table. Are glasses and left-handedness independent?")
    f.p("Turn each percentage into a count, {B:of the right group}: glasses $0.4\\times200=80$; left-handed "
        "$0.15\\times200=30$; left-handed glasses-wearers $0.3\\times80=24$ (30% {B:of the 80}). Every "
        "other cell is a subtraction from a total:", 13.5, gap=8)
    rules_table(f, ["", "left-handed", "right-handed", "total"], [
        ["{B:glasses}", "{B:24}", "80 − 24 = 56", "{B:80}"],
        ["{B:no glasses}", "30 − 24 = 6", "120 − 6 = 114", "200 − 80 = 120"],
        ["{B:total}", "{B:30}", "200 − 30 = 170", "{B:200}"],
    ], [110, 125, 135, 125], C.GREEN)
    ch.check([80 - 24, 30 - 24, 200 - 80, 120 - 6, 200 - 30], [56, 6, 120, 114, 170])
    ch.check(56 + 114, 170)
    step(f, r"p(G\cap L)=\frac{24}{200}=0.12,\qquad p(G)\,p(L)=0.4\times0.15=0.06", "", size=17)
    f.p("$0.12\\neq0.06$, so they are {G:dependent} (in this made-up group, glasses-wearers are more "
        "likely to be left-handed). Zoom in, as before: $p(G\\,|\\,L)=\\frac{24}{30}=0.8$, much more than "
        "$p(G)=0.4$.", 13.5)
    ch.check(Fr(24, 200), Fr("0.12"))
    ch.check(Fr("0.4") * Fr("0.15"), Fr("0.06"))
    ch.check(Fr(24, 30), Fr("0.8"))


def urn(ch):
    f = flow(ch)
    sec(f, "The urn: a table does the counting", room=520)
    rule_box(f, "reading a two-way table", [
        "{B:Joint} $p(A\\cap B)$: one cell ÷ the grand total.",
        "{B:Marginal} $p(A)$: a row or column total ÷ the grand total.",
        "{B:Conditional} $p(A\\,|\\,B)$: the cell ÷ the total of the row or column for B (zoom into B).",
        "Any missing cell = its row (or column) total minus the other cells in that row (or column).",
    ], C.GREEN)
    f.p("Lecture 8's urn holds 100 balls, each Red, Green or Blue and Large or Small. A {B:two-way "
        "table} counts every combination; the totals in the {B:margins} give the {B:marginal} "
        "probabilities:", 14, gap=10)
    tab = {("L", "R"): 5, ("L", "G"): 30, ("L", "B"): 15, ("S", "R"): 15, ("S", "G"): 20, ("S", "B"): 15}
    y_ = f.reserve(26 * 4 + 10)
    pg = f.pg
    cw = 80
    heads = ["", "Red", "Green", "Blue", "total"]
    for j, h_ in enumerate(heads):
        pg.text(L + 20 + j * cw + cw / 2, y_, h_, 12, [C.INK, C.RED, C.GREEN, C.BLUE, C.GREY][j], F.BOLD,
                align="center")
    for i, sz in enumerate(["L", "S"]):
        yy = y_ + 26 + i * 26
        pg.text(L + 20 + cw / 2, yy, "Large" if sz == "L" else "Small", 12, C.INK, F.BOLD, align="center")
        for j, co in enumerate("RGB"):
            hl = co == "R"
            if hl:
                pg.rect(L + 20 + (j + 1) * cw + 10, yy - 4, cw - 20, 22, C.RED, 0.8, fillcolor=C.LIGHT[C.RED])
            pg.text(L + 20 + (j + 1) * cw + cw / 2, yy, str(tab[(sz, co)]), 13, C.INK, align="center")
        pg.text(L + 20 + 4 * cw + cw / 2, yy, "50", 13, C.GREY, F.BOLD, align="center")
    yy = y_ + 78
    pg.line(L + 20, yy - 4, L + 20 + 5 * cw, yy - 4, C.GREY, 0.6)
    for j, v in enumerate([20, 50, 30, 100]):
        pg.text(L + 20 + (j + 1) * cw + cw / 2, yy, str(v), 13, C.GREY, F.BOLD, align="center")
    ch.check(sum(tab.values()), 100)
    ch.check(tab[("L", "R")] + tab[("S", "R")], 20)
    f.p("Joint: $p(R\\cap L) = \\frac{5}{100} = 0.05$ (one cell). Marginal: $p(R) = \\frac{20}{100} = "
        "0.20$ (a margin total). Conditional: told the ball is red, {B:zoom into the red column} "
        "(20 balls) and it's the new world:", 14, gap=6)
    step(f, r"p(L\,|\,R)=\frac{5}{20}=0.25\qquad p(S\,|\,R)=\frac{15}{20}=0.75", "", size=18)
    step(f, r"p(L\,|\,G)=\frac{30}{50}=0.60", "a different answer for green", size=18)
    ch.check([Fr(5, 20), Fr(15, 20), Fr(30, 50)], [Fr(1, 4), Fr(3, 4), Fr(3, 5)])
    ch.term("two-way table", "a table counting every combination of two characteristics, with totals in the margins")
    ch.term("marginal probability", "the overall probability of one characteristic, from a margin total")
    f.p("Before the peek, large was 50-50. Knowing the colour changes the odds for size, so colour and "
        "size are {B:dependent}.", 14)


def bayes(ch):
    f = flow(ch)
    sec(f, "Bayes: turning a conditional round", room=560)
    rule_box(f, "Bayes' theorem", [
        "$p(A\\,|\\,B)$ and $p(B\\,|\\,A)$ are {B:different} numbers: same overlap on top, different crowd "
        "underneath.",
        "To turn one into the other: $p(A\\,|\\,B)=\\dfrac{p(B\\,|\\,A)\\,p(A)}{p(B)}$.",
        "If $p(B)$ isn't given, build it from the law of total probability (two sections on).",
    ], C.GREEN)
    f.p("Lecture 8's school: 100 children. Two questions that {B:sound} the same but aren't:", 14, gap=10)
    y_ = f.reserve(26 * 4)
    pg = f.pg
    cw = 80
    rows = [("", "boy", "girl", "total"), ("dark hair", "30", "36", "66"), ("light hair", "25", "9", "34"),
            ("total", "55", "45", "100")]
    for i, rw in enumerate(rows):
        for j, s_ in enumerate(rw):
            bold = i == 0 or j == 0
            col = C.INK
            if (i, j) == (2, 2):
                pg.rect(L + 20 + j * cw + 18, y_ + i * 24 - 4, cw - 36, 22, C.PURPLE, 1.2,
                        fillcolor=C.LIGHT[C.PURPLE])
            pg.text(L + 20 + j * cw + cw / 2, y_ + i * 24, s_, 12, col, F.BOLD if bold else F.SANS, align="center")
    pg.note(L + 360, y_ + 4, "light hair: zoom into\nthe row of 34", C.ORANGE, 14)
    pg.note(L + 360, y_ + 50, "girl: zoom into the\ncolumn of 45", C.BLUE, 14)
    f.p("{o:If you see a light-haired child, how likely is it a girl?} Zoom into the light row: "
        "$p(\\text{girl}\\,|\\,\\text{light}) = \\frac{9}{34} = 0.26$.", 14, gap=4)
    f.p("{b:If you see a girl, how likely is light hair?} Zoom into the girl column: "
        "$p(\\text{light}\\,|\\,\\text{girl}) = \\frac{9}{45} = 0.20$.", 14, gap=10)
    ch.check_num(9 / 34, 0.2647, tol=0.0001)
    ch.check_num(9 / 45, 0.20)
    f.p("Same 9 children on top, {B:different crowd underneath}. {B:Bayes' theorem} converts one into the "
        "other using the marginal probabilities, when you don't have the whole table:", 14, gap=6)
    y_ = f.reserve(76)
    pg = f.pg
    pg.eq(L + 30, y_ + 4, r"p(a\,|\,b)=\frac{p(b\,|\,a)\,p(a)}{p(b)}", 24, C.GREEN)
    pg.note(L + 300, y_ + 4, "swap what's known and what's\nasked, then correct by the\nratio of the "
            "crowd sizes", C.GREEN, 15)
    ch.formula(r"p(a\,|\,b)=\frac{p(b\,|\,a)\,p(a)}{p(b)}", "Bayes' theorem")
    ch.term("Bayes' theorem", "p(a|b) = p(b|a) p(a) / p(b): turns one conditional probability round")
    step(f, r"p(\ell\,|\,g)=\frac{p(g\,|\,\ell)\,p(\ell)}{p(g)}=\frac{0.26\times0.34}{0.45}=0.20",
         "ℓ = light, g = girl ✓", size=18, color=C.GREEN)
    ch.check_num(0.26 * 0.34 / 0.45, 0.196, tol=0.001)


def tree(ch):
    f = flow(ch)
    sec(f, "Tree diagrams and the law of total probability", room=560)
    rule_box(f, "tree diagrams", [
        "Split first by one event (A or A′), then split each branch by the second event (B or B′). The "
        "second-level branches carry {B:conditional} probabilities such as $p(B\\,|\\,A)$.",
        "{B:Multiply along} a path to get the probability of that whole path: $p(A\\cap B)=p(A)\\,p(B\\,|\\,A)$.",
        "{B:Add between} the paths that end in the outcome you want. The branches leaving any point add "
        "up to 1.",
    ], C.GREEN)
    rule_box(f, "law of total probability", [
        "$p(B)=p(B\\,|\\,A)\\,p(A)+p(B\\,|\\,A')\\,p(A')$: every way B can happen, added up.",
        "Bayes' theorem uses it for the bottom line: $p(A\\,|\\,B)=\\dfrac{p(B\\,|\\,A)\\,p(A)}"
        "{p(B\\,|\\,A)\\,p(A)+p(B\\,|\\,A')\\,p(A')}$.",
    ], C.GREEN)
    ch.formula(r"p(B)=p(B\,|\,A)\,p(A)+p(B\,|\,A')\,p(A')", "law of total probability")
    ch.term("tree diagram", "branches for each outcome of each stage; multiply along a path, add between paths")
    ch.term("law of total probability", "p(B) = p(B|A)p(A) + p(B|A′)p(A′): add up every way B can happen")
    ex(f, "machine A makes 60% of a factory's bolts and machine B the other 40%. 5% of A's bolts are "
          "faulty and 10% of B's. What fraction of all bolts is faulty? A bolt is faulty: what's the chance "
          "machine A made it?")
    y_ = f.reserve(178)
    pg = f.pg
    x0, x1, x2 = L + 20, L + 150, L + 290
    ym = y_ + 84
    ends = []
    for k, (mach, pm, pf) in enumerate([("A", "0.6", "0.05"), ("B", "0.4", "0.10")]):
        yb = ym + (-42 if k == 0 else 42)
        pg.line(x0, ym, x1, yb, C.GREEN, 1.4)
        pg.text((x0 + x1) / 2 - 6, (ym + yb) / 2 + (-20 if k == 0 else 4), pm, 12, C.GREEN, F.BOLD)
        pg.text(x1 + 6, yb - 8, f"machine {mach}", 12, C.INK, F.BOLD)
        for j, (lab, pq) in enumerate([("faulty", pf), ("OK", f"{1 - float(pf):.2f}")]):
            yy = yb + (-20 if j == 0 else 20)
            pg.line(x1 + 82, yb, x2, yy, C.GREEN, 1.2)
            pg.text((x1 + 82 + x2) / 2 - 8, (yb + yy) / 2 + (-16 if j == 0 else 2), pq, 11, C.GREEN)
            prod = float(pm) * float(pq)
            ends.append(prod)
            col = C.RED if lab == "faulty" else C.GREY
            pg.text(x2 + 6, yy - 8, f"{lab}:  {pm} × {pq} = {prod:.2f}", 12, col,
                    F.BOLD if lab == "faulty" else F.SANS)
    pg.dot(x0, ym, 3, C.GREEN)
    ch.check_num(sum(ends), 1, tol=1e-9)
    step(f, r"p(F)=0.05\times0.6+0.10\times0.4=0.03+0.04=0.07", "add the two red paths", size=18,
         color=C.GREEN)
    ch.check(Fr("0.05") * Fr("0.6") + Fr("0.10") * Fr("0.4"), Fr("0.07"))
    step(f, r"p(A\,|\,F)=\frac{p(F\,|\,A)\,p(A)}{p(F)}=\frac{0.03}{0.07}=\frac37\approx0.43", "Bayes: the A path "
         "as a share of all faulty paths", size=18, color=C.GREEN)
    ch.check((Fr("0.05") * Fr("0.6")) / Fr("0.07"), Fr(3, 7))
    f.p("Machine A makes most of the bolts, yet a faulty bolt is more likely to have come from B "
        "($\\frac47$): B's higher fault rate wins. The mammogram puzzle next is the same calculation.", 13.5)


def mammogram(ch):
    f = flow(ch)
    sec(f, "The mammogram puzzle, as 1000 people", fresh=True)
    f.p("{B:1% of women aged 40 who are screened have breast cancer. 80% of those get a positive "
        "mammogram. 9.6% of women {I}without{/I} cancer also get a positive. A woman tests positive. "
        "What's the chance she has cancer?}".replace("{I}", "").replace("{/I}", ""), 14, gap=6)
    f.p("{h:Guess first!} Almost certain? Fairly likely? About half? (Lecture 8: only 15% of doctors got "
        "it right.) Now picture {B:1000 women}, one square each:", 14, gap=10)
    cols, rows_, s_ = 40, 25, 11.6
    y_ = f.reserve(rows_ * s_ + 30)
    pg = f.pg
    sick_pos, sick_neg, well_pos = 8, 2, 95
    k = 0
    for r_ in range(rows_):
        for c_ in range(cols):
            if k < sick_pos:
                col, fill = C.RED, C.RED
            elif k < sick_pos + sick_neg:
                col, fill = C.RED, "#ffffff"
            elif k < sick_pos + sick_neg + well_pos:
                col, fill = C.BLUE, C.LIGHT[C.BLUE]
            else:
                col, fill = "#c9ced6", None
            pg.rect(L + 10 + c_ * s_, y_ + r_ * s_, s_ - 2.4, s_ - 2.4, col, 0.6, fillcolor=fill)
            k += 1
    ch.check(round(1000 * 0.01), 10)
    ch.check(round(10 * 0.8), 8)
    ch.check(round(990 * 0.096), 95)
    lx = L + 10
    ly = y_ + rows_ * s_ + 6
    for fill, col, s2 in [(C.RED, C.RED, "cancer, positive (8)"), ("#ffffff", C.RED, "cancer, negative (2)"),
                          (C.LIGHT[C.BLUE], C.BLUE, "no cancer, positive (95)"),
                          (None, "#c9ced6", "no cancer, negative (895)")]:
        pg.rect(lx, ly + 2, 9, 9, col, 0.8, fillcolor=fill)
        pg.text(lx + 12, ly, s2, 9, C.INK)
        lx += pg.twidth(s2, 9) + 20
    f.p("Step by step: 1% of 1000 = {R:10 have cancer}; 80% of them = {R:8 test positive}. The other 990 "
        "are healthy, but 9.6% of 990 = {b:95 test positive anyway}. So {B:103 positives, only 8 of "
        "whom are ill}:", 14, gap=6)
    step(f, r"p(\text{cancer}\,|\,+)=\frac{8}{103}\approx0.078=7.8\%", "fairly unlikely!", size=20,
         color=C.GREEN)
    ch.check_num(8 / 103, 0.078, tol=0.001)
    f.p("The healthy group's chance of a false alarm is small, but {B:there are so many more of them} "
        "that their false alarms swamp the real cases. Bayes' theorem gives the same answer, with "
        "$p(+)$ built from both groups by the law of total probability (Lecture 8's alternative formula):", 14, gap=6)
    step(f, r"p(c\,|\,m)=\frac{p(m\,|\,c)\,p(c)}{p(m\,|\,c)p(c)+p(m\,|\,c')p(c')}=\frac{0.8\times0.01}{0.8\times0.01+0.096\times0.99}",
         "", size=15)
    step(f, r"=\frac{0.008}{0.10304}\approx0.078", "", size=17, color=C.GREEN)
    ch.check_num(0.008 / (0.008 + 0.096 * 0.99), 0.0776, tol=0.0002)
    f.p("{b:Vocabulary:} $p(\\text{cancer}) = 1\\%$ is the {B:prior} (belief before the evidence); "
        "$p(\\text{cancer}\\,|\\,+) = 7.8\\%$ is the {B:posterior} (belief after). The positive test raised "
        "the risk almost eightfold, but it's still far from certain. That's the scientific method in "
        "miniature: update your beliefs as evidence arrives.", 14, gap=10)
    f.p("{b:Lecture 8's extension question} asks whether $p(a_1\\,|\\,b) = \\frac{p(a_1\\cap b)}{p(a_1\\cap b)"
        "+p(a_2\\cap b)}$ when $a_1$ and $a_2$ can't both happen but one of them must. {G:Yes:} the bottom "
        "is just every way $b$ can happen, split into the $a_1$ part and the $a_2$ part. It's exactly "
        "the counting we did: $\\frac{8}{8+95}$, with $a_1$ = cancer, $a_2$ = no cancer, $b$ = positive.", 14)
    ch.term("prior probability", "the probability before new evidence, e.g. p(cancer) = 1%")
    ch.term("posterior probability", "the updated probability after the evidence, e.g. p(cancer | positive) = 7.8%")


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Use the dice grid where it helps. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Two dice", ["p(a double)", "p(total is 5)", "p(not a double)", "p(red is even OR blue is 1)",
                      "p(total is 8 | red is 3)"],
         "1. 6/36 = 1/6   2. 4/36 = 1/9   3. 5/6   4. (18 + 6 − 3)/36 = 21/36 = 7/12   5. 1/6 (only blue 5)"),
        ("Cards and tables", ["Two cards without replacement: p(both aces)?",
                              "Urn table: p(Small | Blue)?",
                              "Are 'coin shows heads' and 'die shows 6' independent? p(both)?"],
         "6. 4/52 × 3/51 = 1/221   7. 15/30 = 0.5   8. yes; 1/2 × 1/6 = 1/12"),
        ("Bayes", ["A disease affects 2% of people. A test catches 90% of cases but also gives 5% false "
                   "positives. Using 1000 people, find p(disease | positive)."],
         "9. 20 ill, 18 positive; 980 well, 49 positive; 18/67 ≈ 0.27"),
        ("Find the unknown", ["p(A) = 0.6, p(B) = 0.5, p(A ∪ B) = 0.8. Find p(A ∩ B). Are A and B independent?",
                              "p(A | B) = 0.25 and p(B) = 0.4. Find p(A ∩ B).",
                              "p(A ∩ B) = 0.12 and p(A) = 0.3. Find p(B | A).",
                              "A and B are mutually exclusive, p(A) = 0.35, p(A ∪ B) = 0.8. Find p(B).",
                              "A and B are independent, p(A) = 0.4, p(A ∪ B) = 0.7. Find p(B).",
                              "300 students: 40% come by bus; 25% of bus users are late, and 10% of the "
                              "others. How many are late? p(bus | late)?"],
         "10. 0.6 + 0.5 − 0.8 = 0.3; 0.6 × 0.5 = 0.3, so independent   11. 0.4 × 0.25 = 0.1   "
         "12. 0.12 ÷ 0.3 = 0.4   13. 0.8 − 0.35 = 0.45 (no overlap)   14. 0.7 = 0.4 + p − 0.4p, so "
         "p = 0.5   15. bus 120, late 30; others 180, late 18; 48 late; 30/48 = 0.625"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 24 * len(qs) + 30)
        f.text(title, 14, C.GREEN, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(Fr(count(lambda a, b: a == b), 36), Fr(1, 6))
    ch.check(Fr(count(lambda a, b: a + b == 5), 36), Fr(1, 9))
    ch.check(Fr(count(lambda a, b: a % 2 == 0 or b == 1), 36), Fr(7, 12))
    ch.check(Fr(count(lambda a, b: a == 3 and a + b == 8), 6), Fr(1, 6))
    ch.check(Fr(4, 52) * Fr(3, 51), Fr(1, 221))
    ch.check_num(18 / 67, 0.27, tol=0.005)
    ch.check(Fr("0.6") + Fr("0.5") - Fr("0.8"), Fr("0.6") * Fr("0.5"))
    ch.check(Fr("0.4") * Fr("0.25"), Fr("0.1"))
    ch.check(Fr("0.12") / Fr("0.3"), Fr("0.4"))
    ch.check(Fr("0.8") - Fr("0.35"), Fr("0.45"))
    pb = sp.symbols("p")
    ch.check(sp.solve(sp.Rational(2, 5) + pb - sp.Rational(2, 5) * pb - sp.Rational(7, 10), pb), [sp.Rational(1, 2)])
    late = Fr("0.25") * 120 + Fr("0.1") * 180
    ch.check(late, 48)
    ch.check(Fr("0.25") * 120 / late, Fr("0.625"))


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Probability", r"p(E)=\frac{\text{outcomes in }E}{\text{all outcomes}}", "equally likely outcomes; "
         "always between 0 and 1"),
        ("Complement", r"p(E')=1-p(E)", None),
        ("Addition rule (OR)", r"p(A\cup B)=p(A)+p(B)-p(A\cap B)", "always true"),
        ("Mutually exclusive", r"p(A\cap B)=0,\qquad p(A\cup B)=p(A)+p(B)", "can't both happen"),
        ("Conditional", r"p(A\,|\,B)=\frac{p(A\cap B)}{p(B)}", "B becomes the new sample space"),
        ("Multiplication rule (AND)", r"p(A\cap B)=p(B)\,p(A\,|\,B)=p(A)\,p(B\,|\,A)", "always true"),
        ("Independent", r"p(A\cap B)=p(A)\,p(B),\qquad p(A\,|\,B)=p(A)", "test: compare $p(A)p(B)$ with "
         "$p(A\\cap B)$"),
        ("Exclusive vs independent", None, "exclusive events with non-zero probabilities are never independent"),
        ("Tree diagram", None, "multiply along the branches, add between the paths; branches from a point "
         "add to 1"),
        ("Total probability", r"p(B)=p(B\,|\,A)\,p(A)+p(B\,|\,A')\,p(A')", None),
        ("Bayes' theorem", r"p(A\,|\,B)=\frac{p(B\,|\,A)\,p(A)}{p(B)}", "bottom line from the law of total "
         "probability"),
        ("Two-way table", None, "joint = one cell ÷ grand total; marginal = a total ÷ grand total; "
         "conditional = one cell ÷ its row or column total"),
    ], C.GREEN)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    basics(ch)
    and_or(ch)
    given(ch)
    independence(ch)
    contrast(ch)
    urn(ch)
    partial(ch)
    bayes(ch)
    tree(ch)
    mammogram(ch)
    summary(ch)
    your_turn(ch)
