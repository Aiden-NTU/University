"""Chapter 15 - Solving equations. Rule first: each method is boxed (linear procedure, elimination,
substitution, quadratic procedure, completing the square, inequalities) before its worked examples.
Balance scales for one unknown, cafe receipts for two, the zero trick and the quadratic formula
(derived from Chapter 12's pair), find-the-unknown problems with Δ and given roots, word problems,
x on the bottom, and inequalities. Includes the Lecture 3 mixing and compounds problems."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, go, mistakes, rule_box, rules_page, section, step, title_block

ORDER = 15
NUM = 15
TITLE = "Solving equations"
SHORT = "Solving equations"
SLUG = "Solving-equations"
ACCENT = C.GREEN
REQUIRES = ["equals-sign", "substitution", "inverse-operations", "transpose", "expand-brackets", "like-terms",
            "algebraic-fractions", "factorise-quadratic", "roots", "perfect-squares", "concentration",
            "percentage-of", "negative-numbers", "lcm", "proportion", "inequality-symbols"]
INTRODUCES = ["solve-equation", "solution", "linear-equation", "cross-multiply", "simultaneous-equations",
              "elimination", "substitution-method", "independent-equations", "quadratic-equation",
              "zero-product", "completing-the-square", "quadratic-formula", "discriminant", "inequality"]

PAPER = "#fbfefb"
ENV, ENV_EDGE = "#fff3d6", "#b8860b"
x, y, V = sp.symbols("x y V")


def icon(pg, x0, y0):
    pg.line(x0 + 1, y0 + 6, x0 + 17, y0 + 6, C.GREEN, 1.5)
    pg.poly([(x0 + 9, y0 + 6), (x0 + 5, y0 + 16), (x0 + 13, y0 + 16)], C.GREEN, 1.2, closed=True)
    pg.rect(x0 + 1, y0 + 1, 5, 5, C.GREEN, 1)
    pg.rect(x0 + 12, y0 + 1, 5, 5, C.GREEN, 1)


def sec(f, t, **kw):
    section(f, t, C.GREEN, icon, **kw)


def envelope(pg, x0, y0, w=24, h=18, letter="x"):
    pg.rect(x0, y0, w, h, ENV_EDGE, 1.0, fillcolor=ENV)
    pg.poly([(x0, y0), (x0 + w / 2, y0 + h * 0.55), (x0 + w, y0)], ENV_EDGE, 0.9)
    pg.eq(x0 + w / 2, y0 + h * 0.68, letter, 11, C.BLUE, align="center", valign="middle", solid=False)


def weight(pg, x0, y0, n):
    s = str(n)
    w = 16 + 7 * len(s)
    pg.poly([(x0 + 3, y0), (x0 + w - 3, y0), (x0 + w, y0 + 18), (x0, y0 + 18)], C.GREY, 1.1,
            fill=None, closed=True)
    pg.fillpoly([(x0 + 3, y0), (x0 + w - 3, y0), (x0 + w, y0 + 18), (x0, y0 + 18)], "#d6d9de")
    pg.text(x0 + w / 2, y0 + 2, s, 10.5, C.INK, F.BOLD, align="center", solid=False)
    return w


def scale(pg, cx, y0, left, right, w=210, caption=None):
    """A balance. left/right: lists of tokens, 'x' = envelope, int = weight; ('x', 1) = crossed out."""
    by = y0 + 50
    pg.line(cx - w / 2, by, cx + w / 2, by, C.BROWN, 2.2)
    pg.fillpoly([(cx, by), (cx - 12, by + 26), (cx + 12, by + 26)], C.LIGHT[C.BROWN], outline=C.BROWN)
    for side, items in ((-1, left), (1, right)):
        px = cx + side * w / 4
        pw = w / 2 - 16
        pg.poly([(px - pw / 2, by - 4), (px - pw / 2 + 6, by), (px + pw / 2 - 6, by), (px + pw / 2, by - 4)],
                C.BROWN, 1.3)
        widths = []
        for it in items:
            tok = it[0] if isinstance(it, tuple) else it
            widths.append(24 if tok == "x" else 16 + 7 * len(str(tok)))
        total = sum(widths) + 3 * (len(items) - 1)
        rows = [list(range(len(items)))]
        if total > pw:
            half = (len(items) + 1) // 2
            rows = [list(range(half)), list(range(half, len(items)))]
        for r_, idx in enumerate(rows):
            rw = sum(widths[i] for i in idx) + 3 * (len(idx) - 1)
            xx = px - rw / 2
            yy = by - 24 - r_ * 22
            for i in idx:
                it = items[i]
                tok, crossed = (it if isinstance(it, tuple) else (it, 0))
                if tok == "x":
                    envelope(pg, xx, yy + 2)
                else:
                    weight(pg, xx, yy + 2, tok)
                if crossed:
                    pg.line(xx - 2, yy + 22, xx + widths[i] + 2, yy, C.RED, 1.6)
                xx += widths[i] + 3
    if caption:
        pg.note(cx, by + 30, caption, C.GREEN, 15, align="center", solid=False)


def receipt(pg, x0, y0, lines, total, title="CAFÉ", w=140, col=C.INK):
    h = 40 + 18 * len(lines) + 24
    pg.poly([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h)] + [(x0 + w - i * 10 - 5, y0 + h - (4 if i % 2 == 0 else 0))
                                                          for i in range(int(w / 10))] + [(x0, y0 + h)],
            C.GREY, 1.0, closed=True)
    pg.text(x0 + w / 2, y0 + 6, title, 11, C.GREY, F.BOLD, align="center")
    yy = y0 + 28
    for s in lines:
        pg.text(x0 + 10, yy, s, 12, col)
        yy += 18
    pg.line(x0 + 8, yy + 2, x0 + w - 8, yy + 2, C.GREY, 0.8, dash=(3, 2))
    pg.text(x0 + 10, yy + 6, "TOTAL", 11.5, C.INK, F.BOLD)
    pg.text(x0 + w - 10, yy + 6, total, 11.5, C.INK, F.BOLD, align="right")
    return h


# ----------------------------------------------------------------------------- pages
def beaker(pg, x0, y0, w, h, fill, frac_a, col, top_lab, dashed=False):
    """A glass with the liquid drawn 'unmixed': the chemical (coloured) settled under the water (pale blue)."""
    lh = h * fill
    ah = lh * frac_a
    if dashed:
        pg.rect(x0 + 1, y0 + h - lh, w - 2, lh, C.BLUE, 1.0, dash=(3, 3), fillcolor="#eef5fc")
    else:
        pg.rect(x0 + 1, y0 + h - lh, w - 2, lh - ah, "#d8ebfa", 0.1, fillcolor="#d8ebfa")
        pg.rect(x0 + 1, y0 + h - ah, w - 2, ah, col, 0.1, fillcolor=col)
    pg.poly([(x0 - 4, y0), (x0, y0 + 4), (x0, y0 + h), (x0 + w, y0 + h), (x0 + w, y0 + 4), (x0 + w + 4, y0)],
            C.INK, 1.6)
    pg.text(x0 - 20, y0 - 18, top_lab, 10.5, C.INK, F.BOLD, w=w + 40, align="center")


def brackets_fractions(ch):
    f = flow(ch)
    sec(f, "Brackets and fractions: tidy first, then balance", room=460)
    f.p("{b:Brackets:} expand them (Chapter 11), then it's an ordinary balance. $3(x - 2) = 2(x + 1)$:",
        14, gap=6)
    step(f, r"3x-6=2x+2", "expand both sides", size=19)
    step(f, r"x-6=2", "−2x", size=19)
    step(f, r"x=8", "+6", size=19, color=C.GREEN)
    ch.check(sp.solve(3 * (x - 2) - 2 * (x + 1), x), [8])
    f.p("{G:Check:} $3(6) = 18$ and $2(9) = 18$ ✓.", 13.5, gap=10)
    f.p("{b:Fractions:} multiply {B:both sides} by something that clears every bottom. For "
        "$\\frac{x+1}{3} = \\frac{x-1}{2}$, use 6 (both 3 and 2 go into it):", 14, gap=6)
    step(f, r"6\times\frac{x+1}{3}=6\times\frac{x-1}{2}", "× 6 on both sides", size=19)
    step(f, r"2(x+1)=3(x-1)", "6 ÷ 3 = 2;  6 ÷ 2 = 3", size=19)
    step(f, r"2x+2=3x-3\ \Rightarrow\ x=5", "−2x and +3 on both sides", size=19, color=C.GREEN)
    ch.check(sp.solve((x + 1) / 3 - (x - 1) / 2, x), [5])
    f.p("Look at step 2: each top ended up multiplied by the {B:other} side's bottom. That shortcut "
        "has a name.", 14, gap=6)
    y_ = f.reserve(80)
    pg = f.pg
    pg.eq(L + 60, y_ + 4, r"\frac{a}{b}=\frac{c}{d}", 26)
    pg.arrow(L + 70, y_ + 16, L + 132, y_ + 48, C.RED, 1.3, head=5)
    pg.arrow(L + 70, y_ + 48, L + 132, y_ + 16, C.BLUE, 1.3, head=5)
    pg.eq(L + 170, y_ + 18, r"\Rightarrow\ ad=cb", 22, C.GREEN)
    pg.note(L + 350, y_ + 2, "\"cross multiplying\" is just\n× b and × d on both sides,\ndone in one go",
            C.PURPLE, 15)
    ch.term("cross-multiply", "from a/b = c/d go straight to ad = cb; it's multiplying both sides by b and by d")
    f.p("{b:The Chapter 4 promise:} Lecture 3 turns $\\frac5V = \\frac83$ into $15 = 8V$. That's "
        "cross multiplying: $5 \\times 3 = 8 \\times V$, so $V = \\frac{15}{8} = 1.875$ m/s.", 14)
    ch.check(sp.solve(sp.Rational(5) / V - sp.Rational(8, 3), V), [sp.Rational(15, 8)])


def receipts(ch):
    f = flow(ch)
    sec(f, "Two unknowns: café receipts", room=500)
    f.p("You find two receipts. You don't know the price of a coffee ($c$) or a cake ($k$):", 14, gap=10)
    y_ = f.reserve(130)
    pg = f.pg
    receipt(pg, L + 10, y_, ["coffee", "coffee", "cake"], "£7.00")
    receipt(pg, L + 170, y_, ["coffee", "cake"], "£4.50")
    pg.note(L + 330, y_ + 4, "Put them side by side.\nThe first has exactly ONE\nmore coffee than the second,\n"
            "and costs £2.50 more.\nSo a coffee is £2.50!", C.GREEN, 16)
    f.p("That's the whole idea of {B:simultaneous equations}: two facts about the same two unknowns, "
        "used together. Written in algebra:", 14, gap=6)
    step(f, r"2c+k=7\qquad(1)", "", size=19)
    step(f, r"c+k=4.5\qquad(2)", "", size=19)
    step(f, r"c=2.5", "(1) − (2): the cakes cancel", size=19, color=C.BLUE)
    step(f, r"2.5+k=4.5\ \Rightarrow\ k=2", "put c into (2)", size=19, color=C.GREEN)
    ch.check(sp.solve([2 * x + y - 7, x + y - sp.Rational(9, 2)], [x, y]), {x: sp.Rational(5, 2), y: 2})
    ch.term("simultaneous equations", "two (or more) equations about the same unknowns, which must all be true at once")
    ch.term("elimination", "adding or subtracting whole equations so one unknown cancels out")
    f.p("{G:Check in the other one:} $2(2.50) + 2 = 7$ ✓. Subtracting whole equations like this is "
        "called {B:elimination}. Here is the rule in full:", 14, gap=6)
    rule_box(f, "elimination", [
        "Label the equations (1) and (2), lined up: $x$ under $x$, $y$ under $y$, numbers on the right.",
        "Multiply one equation, {B:or both}, by numbers that make the coefficients of one letter the "
        "{B:same size}.",
        "{B:Same signs: subtract} the equations. {B:Opposite signs: add} them. That letter cancels.",
        "Solve for the letter that's left.",
        "Put it back into either original equation to find the other letter. Check in the other one.",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    f.p("{b:Scale one equation} (three copies of a receipt cost three times as much):", 14, gap=6)
    step(f, r"\begin{aligned}3x+2y&=16\\x+y&=6\end{aligned}", "", size=18)
    step(f, r"2x+2y=12", "× 2 the second equation", size=18)
    step(f, r"x=4", "+2y in both (same sign): subtract", size=18, color=C.BLUE)
    step(f, r"4+y=6\ \Rightarrow\ y=2", "put x = 4 into x + y = 6", size=18, color=C.GREEN)
    ch.check(sp.solve([3 * x + 2 * y - 16, x + y - 6], [x, y]), {x: 4, y: 2})
    f.p("{b:Scale both equations:} $3x + 2y = 12$ (1) and $4x - 3y = -1$ (2). No single multiplier makes "
        "anything match, so aim for $6y$ in both:", 14, gap=6)
    step(f, r"9x+6y=36\qquad(1)\times3", "", size=18)
    step(f, r"8x-6y=-2\qquad(2)\times2", "", size=18)
    step(f, r"17x=34\ \Rightarrow\ x=2", "+6y and −6y (opposite signs): add", size=18, color=C.BLUE)
    step(f, r"6+2y=12\ \Rightarrow\ y=3", "x = 2 into (1)", size=18, color=C.GREEN)
    ch.check(sp.solve([3 * x + 2 * y - 12, 4 * x - 3 * y + 1], [x, y]), {x: 2, y: 3})
    f.p("{G:Check in (2):} $4(2) - 3(3) = 8 - 9 = -1$ ✓.", 13.5)
    ch.check(4 * 2 - 3 * 3, -1)


def substitution(ch):
    f = flow(ch)
    sec(f, "The substitution method", room=460)
    rule_box(f, "substitution", [
        "{B:Rearrange} one equation to get one letter on its own (pick a letter with no number in front).",
        "{B:Substitute} that expression into the {B:other} equation, in brackets.",
        "Solve the one-letter equation you now have.",
        "{B:Back-substitute}: put the answer into the rearranged equation to find the other letter.",
        "Check both answers in {B:both} original equations.",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    ch.term("substitution method", "rearrange one equation for one letter and put it into the other equation")
    f.p("{b:Example:} $2x - y = 1$ (1) and $3x + 2y = 12$ (2).", 14, gap=6)
    step(f, r"y=2x-1", "1. rearrange (1): y has no number in front", size=18)
    step(f, r"3x+2\blu{(2x-1)}=12", "2. substitute into (2)", size=18)
    step(f, r"3x+4x-2=12\ \Rightarrow\ 7x=14\ \Rightarrow\ x=2", "3. solve", size=18, color=C.BLUE)
    step(f, r"y=2(2)-1=3", "4. back-substitute", size=18, color=C.GREEN)
    ch.check(sp.solve([2 * x - y - 1, 3 * x + 2 * y - 12], [x, y]), {x: 2, y: 3})
    f.p("{G:5. Check:} (1) $4 - 3 = 1$ ✓, (2) $6 + 6 = 12$ ✓.", 13.5, gap=8)
    ch.check((2 * 2 - 3, 3 * 2 + 2 * 3), (1, 12))
    f.p("{b:Which method?} Substitution is quickest when a letter is already on its own (like $y = 2x - 1$ or "
        "$x = 1000 - y$). Elimination is quickest when the equations are lined up with whole numbers. Both "
        "always give the same answer, and Lecture 12 (matrices) solves the same systems a third way.", 14)


def title_page(ch):
    pg = title_block(ch, 15, "Solving equations", "finding the number hiding in the envelope",
                     C.GREEN, PAPER)
    scale(pg, L + 130, 210, ["x", "x", "x", 5], [20], w=240)
    pg.note(L + 290, 214, "three sealed envelopes and a 5 g weight\nbalance a 20 g weight.\n"
            "How heavy is one envelope?", C.BROWN, 17)
    pg.eq(L + 290, 290, r"3x+5=20", 24, C.GREEN)
    f = ch.flow(top=360)
    f.p("An {B:equation} says two things are equal: the scales balance. {B:Solving} it means finding "
        "the number (or numbers) that the letter must be for the balance to hold. That number is "
        "called the {B:solution}.", 14, gap=10)
    f.p("Every move in this chapter is one of the \"undo buttons\" from Chapter 14, done to {B:both "
        "sides at once} so the scales stay level. After one letter, you'll meet two letters at once "
        "(café receipts) and squared letters, where Chapter 12's pair turns straight into the quadratic "
        "formula. Every answer gets put back into the question as a check.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 2} {y:(rearranging),} {B:Lecture 3} {y:(mixing solutions, compounds, "
        "simultaneous equations) and} {B:Lecture 14} {y:(solving quadratics).}", 12.5)


def balance(ch):
    f = flow(ch)
    sec(f, "Balance scales: do the same to both pans")
    rule_box(f, "solving a linear equation", [
        "Clear {B:brackets} (expand) and {B:fractions} (multiply every term by the LCD).",
        "Collect the letter terms on one side (the side with more of them) and the numbers on the other, "
        "doing the same to both sides.",
        "Divide both sides by the number in front of the letter.",
        "{B:Check:} put the answer back into the original equation.",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    f.p("You could solve $3x + 5 = 20$ by trying numbers until both sides match, but that fails for answers "
        "like $x = 1.875$. The no-guessing way: each move keeps the scales level, so whatever you take from "
        "one pan, you take from the other:", 14, gap=8)
    y_ = f.reserve(110)
    pg = f.pg
    scale(pg, L + 90, y_, ["x", "x", "x", (5, 1)], [(20, 0)], w=170, caption="take 5 from both")
    pg.text(L + 190, y_ + 44, "→", 18, C.GREY)
    scale(pg, L + 290, y_, ["x", "x", "x"], [15], w=150, caption="3 envelopes = 15")
    pg.text(L + 375, y_ + 44, "→", 18, C.GREY)
    scale(pg, L + 440, y_, ["x"], [5], w=100, caption="one = 5")
    step(f, r"3x+5=20", "", size=19)
    step(f, r"3x=15", "−5 on both sides", size=19)
    step(f, r"x=5", "÷3 on both sides (share into 3 equal groups)", size=19, color=C.GREEN)
    ch.check(sp.solve(3 * x + 5 - 20, x), [5])
    ch.term("solve", "find the value(s) of the letter that make an equation true")
    ch.term("solution", "a value of the letter that makes the equation true (also called a root)")
    f.p("{G:Always check:} put the answer back. $3(5) + 5 = 20$ ✓.", 13.5, gap=10)
    f.p("{b:Letters on both sides:} $5x + 2 = 2x + 14$. Take the {B:same number of envelopes} off each "
        "pan, just as you'd take weights off:", 14, gap=8)
    y_ = f.reserve(116)
    pg = f.pg
    scale(pg, L + 110, y_, [("x", 1), ("x", 1), "x", "x", "x", 2], [("x", 1), ("x", 1), 14], w=220,
          caption="take 2 envelopes from each pan")
    pg.note(L + 250, y_ + 10, "2 envelopes crossed out on EACH pan:\nwhat's left still balances", C.GREY, 14)
    step(f, r"5x+2=2x+14", "", size=19)
    step(f, r"3x+2=14", "−2x on both sides (2 envelopes off each pan)", size=19)
    step(f, r"3x=12\ \Rightarrow\ x=4", "−2, then ÷3", size=19, color=C.GREEN)
    ch.check(sp.solve(5 * x + 2 - (2 * x + 14), x), [4])
    f.p("{G:Check:} left $5(4) + 2 = 22$, right $2(4) + 14 = 22$ ✓. {h:Tip:} move the letters to "
        "whichever side has {B:more} of them, so you never end up with a negative number of envelopes.",
        13.5)
    ch.term("linear equation", "an equation where the letter appears only to the power 1 (no x², no 1/x)")


def mixing(ch):
    f = flow(ch)
    sec(f, "Lecture 3, Mixing 2 and 3: an equation from beakers", room=520)
    f.p("{B:How much 15% solution must be added to 60 ml of 25% solution to make a 17.5% solution?} "
        "Before any maths, let's decode what that sentence is asking.", 14, gap=10)
    f.p("{b:What \"a 25% solution\" means.} A solution is a chemical (call it A) dissolved in water. "
        "\"25%\" says a quarter of the liquid is A and the rest is water. In the pictures below, imagine the A "
        "could be poured out separately: the dark part is A, the pale part is water.", 14, gap=12)
    y_ = f.reserve(172)
    pg = f.pg
    beaker(pg, L + 20, y_ + 22, 70, 100, 0.6, 0.25, C.PURPLE, "60 ml at 25%")
    pg.note(L + 16, y_ + 126, "15 ml of A\n45 ml water", C.PURPLE, 13)
    pg.text(L + 104, y_ + 70, "+", 22, C.INK, F.BOLD)
    beaker(pg, L + 135, y_ + 22, 70, 100, 0.8, 0.15, C.BLUE, "V ml at 15%", dashed=True)
    pg.text(L + 135, y_ + 60, "?", 30, C.BLUE, F.BOLD, w=70, align="center")
    pg.note(L + 128, y_ + 126, "how much? (V)", C.BLUE, 13)
    pg.arrow(L + 218, y_ + 75, L + 258, y_ + 75, C.GREY, 1.6, head=7)
    beaker(pg, L + 270, y_ + 22, 90, 100, 0.95, 0.175, C.GREEN, "the mix: 17.5%")
    pg.note(L + 266, y_ + 126, "must come out 17.5% A", C.GREEN, 13)
    f.p("{b:In plain English:} you have a strong mix. You pour in a weaker one, which dilutes it. Pour a little "
        "and it's still strong; pour loads and it's nearly down to 15%. Somewhere in between it is exactly 17.5%. "
        "{B:How much do you pour to stop right there?} That amount is $V$.", 14, gap=10)
    f.p("To find it, {B:follow the chemical A}, not the percentages. Count how much A is in each beaker:",
        14, gap=10)
    y_ = f.reserve(122)
    pg = f.pg
    boxes = [("60 ml at 25%", r"0.25\times60=15", C.PURPLE), ("V ml at 15%", r"0.15V", C.BLUE),
             ("60 + V ml together", r"15+0.15V", C.GREEN)]
    for i, (lab, a_, col) in enumerate(boxes):
        bx = L + 10 + i * 170
        pg.rect(bx, y_, 140, 90, col, 1.3, fillcolor=C.LIGHT[col], r=8)
        pg.text(bx + 70, y_ + 8, lab, 12, col, F.BOLD, align="center")
        pg.text(bx + 70, y_ + 30, "amount of A:", 11, C.GREY, align="center")
        pg.eq(bx + 70, y_ + 64, a_, 16, align="center", valign="middle")
        if i < 2:
            pg.text(bx + 150, y_ + 34, "+" if i == 0 else "=", 18, C.INK, F.BOLD)
    pg.note(L + 10, y_ + 96, "percentage of the mix = (amount of A) ÷ (total volume) × 100, and it must be 17.5",
            C.GREEN, 15, w=W)
    step(f, r"\frac{15+0.15V}{60+V}\times100=17.5", "the equation (the slide's)", size=19)
    step(f, r"(15+0.15V)\times100=17.5(60+V)", "× (60 + V) on both sides", size=19)
    step(f, r"1500+15V=1050+17.5V", "expand both sides", size=19)
    step(f, r"450=2.5V", "−1050 and −15V on both sides", size=19)
    step(f, r"V=\frac{450}{2.5}=180", "÷ 2.5", size=19, color=C.GREEN)
    ch.check(sp.solve((15 + sp.Rational(15, 100) * V) / (60 + V) * 100 - sp.Rational(35, 2), V), [180])
    f.p("{G:Check with the beakers:} A = $15 + 0.15 \\times 180 = 15 + 27 = 42$ ml in $60 + 180 = 240$ ml. "
        "$\\frac{42}{240} \\times 100 = 17.5\\%$ ✓. So add {B:180 ml} of the 15% solution.", 13.5)
    ch.check(sp.Rational(42, 240) * 100, sp.Rational(35, 2))


def lines(ch):
    f = flow(ch)
    sec(f, "The picture: where two lines cross", room=420)
    f.p("Each equation on its own has endless answers. $c + k = 4.5$ could be (1, 3.5), (2, 2.5), "
        "(3, 1.5)... Plot them all and you get a straight line (Chapter 20). The other receipt gives another "
        "line, and the answer is the one point on {B:both}: where they cross, at (2.5, 2).", 14, gap=8)
    f.p("Two lines can meet in three ways, and that decides how many answers there are:", 14, gap=8)
    y_ = f.reserve(122)
    pg = f.pg
    for i, (title, lns, col) in enumerate([("cross once: one answer", [(-0.5, 3), (1, 0.5)], C.GREEN),
                                           ("same line: endless answers", [(-0.5, 3), (-0.5, 3)], C.ORANGE),
                                           ("parallel: no answer", [(-0.5, 3), (-0.5, 1.6)], C.RED)]):
        ax = Axes(pg, L + 30 + i * 165, y_ + 6, 110, 76, (0, 4), (0, 4))
        ax.axes(None, None, 0, 0)
        for j, (m, c0) in enumerate(lns):
            ax.curve(lambda t, m=m, c0=c0: m * t + c0, color=C.BLUE if j == 0 else col,
                     width=2.6 if j == 0 else 1.6, dash=(4, 3) if (i == 1 and j == 1) else None)
        pg.text(L + 85 + i * 165, y_ + 100, title, 10.5, col, F.BOLD, align="center")
    f.p("Lecture 3 ends with the middle case: $x + 2y = 10$ and $3x + 6y = 30$. The second is just the first "
        "multiplied by 3 (the same order bought three times), so it tells you nothing new. Try to solve and "
        "everything cancels to $30 = 30$: true, but no letter left to find. These equations are {B:not "
        "independent}. Two equations that contradict each other, like $x + 2y = 10$ and $x + 2y = 12$, are "
        "the parallel case: no answer at all.", 14)
    ch.check(sp.expand(3 * (x + 2 * y)), 3 * x + 6 * y)
    ch.check(sp.solve([2 * x + y - 7, x + y - sp.Rational(9, 2)], [x, y]), {x: sp.Rational(5, 2), y: 2})
    ch.term("independent equations", "equations that each give genuinely new information; you need as many as "
            "there are unknowns")


def compounds(ch):
    f = flow(ch)
    sec(f, "Lecture 3 compounds: two receipts in disguise", room=520)
    f.p("{B:Solution 1 has 80 g of C per litre, solution 2 has 25 g per litre. How much of each makes "
        "1 litre with 60 g per litre?}", 14, gap=8)
    f.p("{b:Decoding it.} Think of two bottles of squash, with C as the sugar. \"80 g per litre\" means every "
        "litre of bottle 1 has 80 g of sugar dissolved in it: strong. Bottle 2 has only 25 g per litre: weak. "
        "You need to fill a {B:1-litre jug} that contains exactly {B:60 g} of sugar. {B:How many ml do you pour "
        "from each bottle?} That's two unknowns.", 14, gap=12)
    y_ = f.reserve(160)
    pg = f.pg
    for k, (lab_, col, amt) in enumerate([("bottle 1: 80 g per litre", C.RED, "x ml"),
                                          ("bottle 2: 25 g per litre", C.ORANGE, "y ml")]):
        bx = L + 10 + k * 130
        pg.rect(bx + 20, y_ + 40, 60, 90, col, 1.5, fillcolor=C.LIGHT[col], r=8)
        pg.rect(bx + 38, y_ + 26, 24, 14, col, 1.5, fillcolor=C.LIGHT[col], r=2)
        pg.text(bx - 20, y_ + 8, lab_, 9.5, col, F.BOLD, w=140, align="center")
        pg.text(bx + 20, y_ + 78, amt, 13, col, F.BOLD, w=60, align="center")
    pg.arrow(L + 95, y_ + 136, L + 300, y_ + 110, C.RED, 1.4, head=6, bend=0.15)
    pg.arrow(L + 225, y_ + 136, L + 300, y_ + 118, C.ORANGE, 1.4, head=6, bend=0.1)
    pg.poly([(L + 305, y_ + 40), (L + 310, y_ + 140), (L + 390, y_ + 140), (L + 395, y_ + 40)], C.INK, 1.6)
    pg.rect(L + 309, y_ + 60, 83, 79, "#d8c7f0", 0.1, fillcolor="#efe7fb")
    pg.text(L + 305, y_ + 20, "the jug: 1 litre", 10.5, C.INK, F.BOLD, w=90, align="center")
    pg.text(L + 305, y_ + 88, "60 g of C", 12, C.PURPLE, F.BOLD, w=90, align="center")
    pg.note(L + 405, y_ + 30, "x + y must make 1000 ml\n\nthe sugar from both must add to 60 g", C.INK, 14,
            w=R - L - 405)
    f.p("Every ml of bottle 1 carries $80 \\div 1000 = 0.08$ g; every ml of bottle 2 carries $0.025$ g. So the "
        "two facts are two receipts:", 14, gap=6)
    step(f, r"x+y=1000\qquad(1)", "the volumes add to 1 litre", size=19)
    step(f, r"0.08x+0.025y=60\qquad(2)", "the grams of C add to 60", size=19)
    f.p("Elimination, exactly as with the café: make the $x$ parts match, then subtract.", 14, gap=6)
    step(f, r"0.08x+0.08y=80", "(1) × 0.08", size=19)
    step(f, r"0.055y=20\ \Rightarrow\ y=\frac{20}{0.055}\approx364", "this − (2): the x's cancel", size=19)
    step(f, r"x=1000-364=636", "back into (1)", size=19, color=C.GREEN)
    sol = sp.solve([x + y - 1000, sp.Rational(8, 100) * x + sp.Rational(25, 1000) * y - 60], [x, y])
    ch.check_num(sol[y], 363.64, tol=0.01)
    ch.check_num(sol[x], 636.36, tol=0.01)
    f.p("{G:Check:} $0.08 \\times 636 + 0.025 \\times 364 = 50.9 + 9.1 = 60$ g ✓. The slide uses {B:substitution} "
        "instead (rearrange (1) to $x = 1000 - y$ and put that into (2): "
        "$0.08(1000 - y) + 0.025y = 60$, so $80 - 0.055y = 60$); it gives the same answer. The slide "
        "prints $\\frac{20}{0.55}$; it should be $\\frac{20}{0.055}$, as the answer 364 shows.", 13.5)
    ch.check(sp.expand(sp.Rational(8, 100) * (1000 - y) + sp.Rational(25, 1000) * y), 80 - sp.Rational(55, 1000) * y)


def zero_trick(ch):
    f = flow(ch)
    sec(f, "Squared letters: two answers, and the zero trick", fresh=True)
    rule_box(f, "the zero product rule", [
        "If $A\\times B=0$, then $A=0$ or $B=0$. This works {R:only for 0}.",
        "So {B:rearrange so one side is 0 BEFORE you factorise}. $(x-1)(x-2)=6$ does {R:not} give $x-1=6$: "
        "two numbers can multiply to 6 in endless ways.",
    ], C.GREEN)
    rule_box(f, "solving a quadratic equation", [
        "{B:Rearrange to} $ax^2+bx+c=0$: expand any brackets, move every term to one side.",
        "{B:Factorise} (Chapter 12). If it won't factorise, use the {B:quadratic formula} (next section).",
        "Set {B:each bracket equal to 0} and solve each one.",
        "{B:Check} each answer in the original equation, and reject any that don't fit the question.",
    ], C.GREEN, numbered=True, tag="PROCEDURE")
    f.p("$x^2 = 25$ has {B:two} solutions: $5 \\times 5 = 25$ and also $(-5) \\times (-5) = 25$ (Chapter 9 "
        "warned you). We write $x = \\pm5$, said \"plus or minus five\".", 14, gap=8)
    ch.symbol(r"\pm", "plus or minus", "both the + version and the − version are answers")
    ch.check(sp.solve(x ** 2 - 25, x), [-5, 5])
    f.p("An equation with an $x^2$ is a {B:quadratic equation}. Lecture 14's example: "
        "$x^2 + 6x + 5 = 0$. The key fact is the {B:zero trick}: if two numbers multiply to give 0, "
        "one of them must be 0 (there's no other way to make 0 by multiplying).", 14, gap=6)
    ch.term("quadratic equation", "an equation with x² as the highest power, e.g. x² + 6x + 5 = 0")
    step(f, r"x^2+6x+5=0", "", size=19)
    step(f, r"(x+5)(x+1)=0", "factorise (Chapter 12: Δ = 16, pair 5 and 1)", size=19)
    step(f, r"x+5=0\quad\text{or}\quad x+1=0", "one bracket must be zero", size=19)
    step(f, r"x=-5\quad\text{or}\quad x=-1", "", size=19, color=C.GREEN)
    ch.check(sp.solve(x ** 2 + 6 * x + 5, x), [-5, -1])
    ch.check(6 ** 2 - 4 * 5, 16)
    ch.term("zero product rule", "if A × B = 0 then A = 0 or B = 0")
    y_ = f.reserve(184)
    pg = f.pg
    ax = Axes(pg, L + 40, y_ + 24, 230, 140, (-6, 1), (-5, 6))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 2)
    ax.curve(lambda t: t * t + 6 * t + 5, color=C.GREEN)
    ax.dot(-5, 0, C.RED, 4)
    ax.dot(-1, 0, C.RED, 4)
    ax.dot(-3, -4, C.PURPLE, 3)
    pg.note(L + 300, y_ + 20, "The graph of y = x² + 6x + 5 is a\nU-shaped curve. The solutions are where\n"
            "it crosses the x-axis (where y = 0):\nx = −5 and x = −1.\n\nThe bottom of the U, (−3, −4),\n"
            "is the vertex (two sections on).", C.GREY, 15)
    f.p("{b:Not zero yet:} $(x - 1)(x - 2) = 6$. Expand and rearrange first:", 14, gap=6)
    step(f, r"x^2-3x+2=6", "expand", size=18)
    step(f, r"x^2-3x-4=0", "−6 on both sides: now one side is 0", size=18)
    step(f, r"(x-4)(x+1)=0\ \Rightarrow\ x=4\ \text{or}\ x=-1", "factorise; each bracket = 0", size=18,
         color=C.GREEN)
    ch.check(sp.solve((x - 1) * (x - 2) - 6, x), [-1, 4])
    f.p("{G:Check:} $(3)(2) = 6$ ✓ and $(-2)(-3) = 6$ ✓.", 13.5, gap=6)
    mistakes(f, [
        (r"(x-1)(x-2)=6\Rightarrow x-1=6", r"x^2-3x-4=0\Rightarrow x=4,\,-1",
         "the zero trick only works when the other side is 0"),
        (r"x^2=3x\Rightarrow x=3", r"x(x-3)=0\Rightarrow x=0,\,3", "dividing by x loses x = 0: factorise instead"),
        (r"x^2=25\Rightarrow x=5", r"x=\pm5", "a square root gives two answers"),
    ])
    ch.check(sp.solve(x ** 2 - 3 * x, x), [0, 3])


def formula(ch):
    f = flow(ch)
    sec(f, "The quadratic formula: straight from Chapter 12", room=520)
    f.p("Chapter 12 factorises {B:any} quadratic with its pair $m, n = \\frac{b \\pm \\sqrt{\\Delta}}{2}$, where "
        "$\\Delta = b^2 - 4ac$. Chapter 12's grid formula gives the brackets. Now use the zero trick on them:",
        14, gap=6)
    step(f, r"ax^2+bx+c=\left(x+\frac na\right)(ax+m)=0", "Chapter 12's brackets", size=19)
    step(f, r"x=-\frac na\quad\text{or}\quad x=-\frac ma", "one bracket must be zero", size=19)
    step(f, r"x=\frac{-b\pm\sqrt{\Delta}}{2a}", "put in m, n = (b ± √Δ)/2", size=21, color=C.GREEN)
    A, Bb, Cc = sp.symbols("a b c", positive=True)
    Dl = Bb ** 2 - 4 * A * Cc
    for sgn in (1, -1):
        root = (-Bb + sgn * sp.sqrt(Dl)) / (2 * A)
        ch.check(sp.simplify(sp.expand(A * root ** 2 + Bb * root + Cc)), 0)
    ch.check(sp.simplify(-((Bb - sp.sqrt(Dl)) / 2) / A - (-Bb + sp.sqrt(Dl)) / (2 * A)), 0)
    f.p("That's the famous {B:quadratic formula}. It is Chapter 12's pair with the signs flipped and divided "
        "by $a$: nothing new to learn. Treat it like a recipe card:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    pg.rect(L + 20, y_, W - 40, 140, C.GREEN, 1.6, fillcolor="#ffffff", r=10)
    pg.rect(L + 20, y_, W - 40, 26, C.GREEN, 0.1, fillcolor=C.LIGHT[C.GREEN], r=10)
    pg.text(L + 34, y_ + 5, "RECIPE: solving  ax² + bx + c = 0", 13, C.GREEN, F.BOLD)
    pg.text(L + 34, y_ + 38, "Ingredients:", 12, C.INK, F.BOLD)
    pg.rich(L + 34, y_ + 56, "{b:a} = number in front of $x^2$\n{o:b} = number in front of $x$\n"
            "{p:c} = the plain number", 170, 12)
    pg.text(L + 230, y_ + 38, "Method:", 12, C.INK, F.BOLD)
    pg.eq(L + 345, y_ + 88, r"x=\frac{-\color{corg}b\color{ink}\pm\sqrt{\color{corg}b\color{ink}^2-4\color{cblu}a"
          r"\color{cpur}c}}{2\color{cblu}a}", 21, align="center", valign="middle")
    ch.formula(r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}", "quadratic formula (for ax² + bx + c = 0)")
    ch.term("quadratic formula", "x = (−b ± √(b² − 4ac)) / 2a, the solutions of ax² + bx + c = 0; the roots "
            "are Chapter 12's pair with the sign flipped, divided by a")
    f.p("{b:Lecture 14's example:} $x^2 + 3x + 2 = 0$. Ingredients: $a = 1$, $b = 3$, $c = 2$. Work out "
        "$\\Delta$ first, as in Chapter 12:", 14, gap=6)
    step(f, r"\Delta=3^2-4\times1\times2=1", "a perfect square: it would factorise too", size=18)
    step(f, r"x=\frac{-3\pm1}{2}=-1\quad\text{or}\quad-2", "+ version, then − version", size=18, color=C.GREEN)
    ch.check(sp.solve(x ** 2 + 3 * x + 2, x), [-2, -1])
    f.p("{b:Where it earns its keep:} $2x^2 - 4x - 3 = 0$. $a = 2$, $b = -4$, $c = -3$. {R:Careful:} "
        "$-b$ is $-(-4) = +4$.", 14, gap=6)
    step(f, r"\Delta=(-4)^2-4\times2\times(-3)=16+24=40", "not a square: no neat brackets", size=18)
    step(f, r"x=\frac{4\pm\sqrt{40}}{4}\approx2.58\quad\text{or}\quad-0.58", "√40 ≈ 6.32", size=18,
         color=C.GREEN)
    r1, r2 = (4 + math.sqrt(40)) / 4, (4 - math.sqrt(40)) / 4
    ch.check_num(2 * r1 ** 2 - 4 * r1 - 3, 0, tol=1e-9)
    ch.check_num(r1, 2.58, tol=0.01)
    ch.check_num(r2, -0.58, tol=0.01)
    f.p("So: $\\Delta$ a perfect square, factorising and the formula both work. Not a square, the formula "
        "is the quick route.", 14)


def vertex(ch):
    f = flow(ch)
    sec(f, "Completing the square: where the U bottoms out", room=480)
    rule_box(f, "completing the square", [
        "$x^2+bx+c=\\left(x+\\frac b2\\right)^2-\\left(\\frac b2\\right)^2+c$.",
        "In words: {B:halve the number in front of x}, put it in a squared bracket, then {B:subtract that "
        "half squared} (the bracket adds it on, so take it off again) and keep $c$.",
        "If $a\\ne1$: take $a$ out of the $x^2$ and $x$ terms first, complete the square inside, then "
        "multiply the $a$ back in.",
        "The result $a(x+p)^2+q$ is {B:vertex form}: the vertex (turning point) is at $(-p,\\ q)$.",
    ], C.GREEN)
    bb, cc = sp.symbols("b c")
    ch.check(sp.expand((x + bb / 2) ** 2 - (bb / 2) ** 2 + cc), x ** 2 + bb * x + cc)
    ch.formula(r"x^2+bx+c=\left(x+\frac b2\right)^2-\left(\frac b2\right)^2+c", "completing the square")
    f.p("It's worth knowing because it shows the bottom of the U. Lecture 14's example:", 14, gap=6)
    step(f, r"x^2+6x+5=(x+3)^2-9+5=(x+3)^2-4", "half of 6 is 3;  3² = 9", size=18)
    ch.check(sp.expand((x + 3) ** 2 - 4), x ** 2 + 6 * x + 5)
    ch.term("completing the square", "rewriting x² + bx + c as (x + b/2)² − (b/2)² + c; for a ≠ 1 take a out "
            "of the x terms first. Gives vertex form a(x + p)² + q")
    ch.term("vertex form", "a quadratic written a(x + p)² + q; its vertex (turning point) is (−p, q)")
    f.p("{b:When a is not 1:} $2x^2 + 12x + 7$ (Lecture 14 uses this vertex form).", 14, gap=6)
    step(f, r"=2(x^2+6x)+7", "take 2 out of the x terms only", size=18)
    step(f, r"=2\left[(x+3)^2-9\right]+7", "complete the square inside", size=18)
    step(f, r"=2(x+3)^2-18+7=2(x+3)^2-11", "multiply the 2 back in", size=18, color=C.GREEN)
    ch.check(sp.expand(2 * (x + 3) ** 2 - 11), 2 * x ** 2 + 12 * x + 7)
    f.p("Vertex $(-3, -11)$. {G:Check} $x = 0$: $7$ and $2(9) - 11 = 7$ ✓.", 13.5, gap=8)
    f.p("{b:Solving by completing the square:} $x^2 + 4x - 1 = 0$ won't factorise, but:", 14, gap=6)
    step(f, r"(x+2)^2-4-1=0\ \Rightarrow\ (x+2)^2=5", "half of 4 is 2", size=18)
    step(f, r"x+2=\pm\sqrt5\ \Rightarrow\ x=-2\pm\sqrt5", "square root: ±", size=18, color=C.GREEN)
    ch.check_true(set(sp.solve(x ** 2 + 4 * x - 1, x)) == {-2 + sp.sqrt(5), -2 - sp.sqrt(5)})
    f.p("A square is never negative, so $(x + 3)^2 - 4$ is smallest when the bracket is 0: at $x = -3$, "
        "where it's $-4$. That point, $(-3, -4)$, is the {B:vertex}. It also solves the equation by pure "
        "undoing: $(x + 3)^2 = 4$, so $x + 3 = \\pm 2$ and $x = -1$ or $-5$, the same answers as before.",
        14)
    ch.check(sp.solve((x + 3) ** 2 - 4, x), [-5, -1])


def discriminant(ch):
    f = flow(ch)
    sec(f, "How many answers? Look at Δ", room=520)
    f.p("The part under the root, $\\Delta = b^2 - 4ac$, is Chapter 12's test number (the {B:discriminant}). "
        "It decides the brackets there, and the number of answers here. Take three neighbours that differ only "
        "in the last number:", 14, gap=8)
    trio = [(3, C.GREEN), (4, C.ORANGE), (5, C.RED)]
    go(f, "y = x² + 4x + 3, y = x² + 4x + 4 and y = x² + 4x + 5 are three U-shaped graphs. Work out Δ for each, "
          "then predict how many times each U crosses the x-axis (where y = 0) before you look below.")
    y_ = f.reserve(150)
    pg = f.pg
    for i, (u, col) in enumerate(trio):
        ax = Axes(pg, L + 20 + i * 165, y_ + 4, 130, 90, (-4.5, 0.5), (-1.5, 4))
        ax.axes(None, None, 0, 0)
        hw = math.sqrt(7.3 - u)
        ax.curve(lambda t, u=u: t * t + 4 * t + u, -2 - hw, -2 + hw, col, 2)
        roots = sorted(float(r) for r in sp.solve(x ** 2 + 4 * x + u, x) if r.is_real)
        for r_ in roots:
            ax.dot(r_, 0, col, 3.5)
        d = 16 - 4 * u
        ch.check(len(roots), {3: 2, 4: 1, 5: 0}[u])
        pg.eq(L + 85 + i * 165, y_ + 104, rf"x^2+4x+{u}:\ \Delta={d}", 12, col, align="center")
        pg.text(L + 85 + i * 165, y_ + 126, ["two crossings", "one touch", "no crossings"][i], 11, col, F.BOLD,
                align="center")
    ch.check([16 - 4 * u for u, _ in trio], [4, 0, -4])
    f.p("Positive: the formula's $\\pm$ gives two different answers, and the U crosses twice. Zero: $+0$ and "
        "$-0$ are the same, so one answer, and the U just touches. Negative: there is no real square root "
        "(Chapter 9), so no {B:real} answers, and the U floats above (or below) the axis. Chapter 12's table of cases is the same fact.",
        14, gap=8)
    y_ = f.reserve(40)
    pg = f.pg
    for i, (lat, lab, col) in enumerate([(r"\Delta>0", "two answers", C.GREEN),
                                         (r"\Delta=0", "one answer", C.ORANGE),
                                         (r"\Delta<0", "no real answers", C.RED)]):
        pg.eq(L + 85 + i * 165, y_ + 4, lat, 13, col, align="center")
        pg.text(L + 85 + i * 165, y_ + 24, lab, 11, col, F.BOLD, align="center")


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown: partial information about a quadratic", room=520)
    f.p("Exam questions often hide a letter (usually $k$) in the equation and give you {B:one fact} about the "
        "answers. Each fact turns into an equation for $k$:", 14, gap=6)
    rule_box(f, "what each fact means", [
        "\"{B:Equal roots}\" (or \"one repeated root\", \"touches the x-axis\"): $\\Delta=b^2-4ac=0$.",
        "\"{B:Two different real roots}\": $\\Delta>0$.  \"{B:No real roots}\": $\\Delta<0$.",
        "\"{B:x = r is a root}\": put $x=r$ into the equation; it must come out true. Solve for $k$.",
        "Then answer the rest (e.g. the other root) by solving the now-complete equation.",
    ], C.GREEN)
    f.p("{b:Example 1:} find $k$ so that $x^2 + kx + 9 = 0$ has equal roots.", 14, gap=6)
    step(f, r"\Delta=k^2-4\times1\times9=k^2-36", "a = 1, b = k, c = 9", size=18)
    step(f, r"k^2-36=0\ \Rightarrow\ k^2=36\ \Rightarrow\ k=\pm6", "equal roots: Δ = 0", size=18, color=C.GREEN)
    k = sp.symbols("k")
    ch.check(sp.solve(sp.discriminant(x ** 2 + k * x + 9, x), k), [-6, 6])
    f.p("{G:Check} $k = 6$: $x^2 + 6x + 9 = (x + 3)^2$, one repeated root $x = -3$ ✓. ($k = -6$ gives "
        "$(x - 3)^2$.)", 13.5, gap=10)
    ch.check(sp.factor(x ** 2 + 6 * x + 9), (x + 3) ** 2)
    f.p("{b:Example 2:} one root of $x^2 + kx - 10 = 0$ is $x = 2$. Find $k$ and the other root.", 14, gap=6)
    step(f, r"2^2+2k-10=0", "x = 2 makes it true", size=18)
    step(f, r"2k-6=0\ \Rightarrow\ k=3", "solve for k", size=18, color=C.BLUE)
    step(f, r"x^2+3x-10=(x-2)(x+5)=0", "now factorise the full equation", size=18)
    step(f, r"\text{other root: }x=-5", "", size=18, color=C.GREEN)
    ch.check(sp.solve(2 ** 2 + 2 * k - 10, k), [3])
    ch.check(sp.solve(x ** 2 + 3 * x - 10, x), [-5, 2])
    f.p("{G:Check:} $(-5)^2 + 3(-5) - 10 = 25 - 15 - 10 = 0$ ✓. (The $(x - 2)$ bracket had to be there, "
        "because $x = 2$ is a root.)", 13.5)


def word_problems(ch):
    f = flow(ch)
    sec(f, "Quadratics from words, and x on the bottom", room=520)
    rule_box(f, "rejecting answers", [
        "After solving, test every answer against the {B:question}: a length, time, mass or count can't be "
        "negative, so reject a negative answer there (say why).",
        "Reject any answer that makes a {B:denominator 0} in the original equation.",
    ], C.GREEN)
    f.p("{b:Word problem:} a rectangle is 3 cm longer than it is wide, and its area is 40 cm². Find its size.",
        14, gap=6)
    step(f, r"x(x+3)=40", "width x, length x + 3; area = width × length", size=18)
    step(f, r"x^2+3x-40=0", "expand, then rearrange to 0", size=18)
    step(f, r"(x+8)(x-5)=0\ \Rightarrow\ x=-8\ \text{or}\ x=5", "pair 8, −5", size=18)
    step(f, r"x=5:\ 5\text{ cm by }8\text{ cm}", "reject −8: a width can't be negative", size=18, color=C.GREEN)
    ch.check(sp.solve(x * (x + 3) - 40, x), [-8, 5])
    f.p("{G:Check:} $5 \\times 8 = 40$ ✓, and 8 is 3 more than 5 ✓.", 13.5, gap=10)
    f.p("{b:x on the bottom:} $x + \\frac6x = 5$. Banned: $x = 0$. Multiply every term by $x$ (Chapter 13):",
        14, gap=6)
    step(f, r"x^2+6=5x\ \Rightarrow\ x^2-5x+6=0", "× x, then rearrange to 0", size=18)
    step(f, r"(x-2)(x-3)=0\ \Rightarrow\ x=2\ \text{or}\ 3", "neither is banned", size=18, color=C.GREEN)
    ch.check(sp.solve(sp.Eq(x + 6 / x, 5), x), [2, 3])
    f.p("{G:Check:} $2 + 3 = 5$ ✓ and $3 + 2 = 5$ ✓.", 13.5, gap=10)
    f.p("{b:A banned answer:} $\\frac{x^2}{x-1} = \\frac{1}{x-1}$. Banned: $x = 1$.", 14, gap=6)
    step(f, r"x^2=1\ \Rightarrow\ x=\pm1", "× (x − 1)", size=18)
    step(f, r"x=-1\ \text{only}", "x = 1 makes the bottom 0: reject it", size=18, color=C.GREEN)
    ch.check(sp.solve(sp.Eq(x ** 2 / (x - 1), 1 / (x - 1)), x), [-1])
    f.p("{G:Check:} $\\frac{1}{-2} = \\frac{1}{-2}$ ✓.", 13.5)


def numline(pg, x0, y0, w, lo, hi, at, closed, right, col=C.GREEN):
    """A number line from lo to hi; a circle at `at` (filled if closed) and a thick ray to the right or left."""
    sx = w / (hi - lo)
    X = lambda v: x0 + (v - lo) * sx
    pg.arrow(x0 - 8, y0, x0 + w + 10, y0, C.GREY, 1.0, head=4)
    for v in range(lo, hi + 1):
        pg.line(X(v), y0 - 4, X(v), y0 + 4, C.GREY, 0.8)
        pg.text(X(v), y0 + 7, str(v).replace("-", "−"), 9.5, C.GREY, align="center")
    end = x0 + w + 6 if right else x0 - 6
    pg.arrow(X(at), y0 - 12, end, y0 - 12, col, 2.6, head=6)
    pg.line(X(at), y0 - 12, X(at), y0, col, 0.8, dash=(2, 2))
    pg.circle(X(at), y0 - 12, 5, col, 1.6, fillcolor=col if closed else "#ffffff")


def inequalities(ch):
    f = flow(ch)
    sec(f, "Inequalities: solve like an equation, with one twist", room=520)
    rule_box(f, "solving an inequality", [
        "Use the same moves as for an equation: add or subtract anything on both sides; multiply or divide "
        "both sides by a {B:positive} number. The sign stays the same.",
        "{R:Multiplying or dividing both sides by a NEGATIVE number flips the sign}: $<$ becomes $>$, "
        "$\\le$ becomes $\\ge$ (and the other way round).",
        "The answer is a {B:range} of values. Show it on a number line: {B:open circle} for $<$ or $>$ (the "
        "end is not included), {B:filled circle} for $\\le$ or $\\ge$ (it is).",
        "Check with one number from inside the range and one from outside.",
    ], C.GREEN)
    ch.term("inequality", "a statement that one side is less than (<), greater than (>), at most (≤) or at "
            "least (≥) the other; its solution is a range of values")
    f.p("{b:Why the flip?} $2 < 5$ is true. Multiply both sides by $-1$: $-2$ and $-5$. Now $-2$ is the "
        "{B:bigger} one, so $-2 > -5$. Multiplying by a negative reverses the order of numbers.", 14, gap=8)
    ch.check_true(-2 > -5)
    f.p("{b:Example 1:} $3x + 2 < 14$.", 14, gap=6)
    step(f, r"3x<12\ \Rightarrow\ x<4", "−2, then ÷3 (positive: no flip)", size=18, color=C.GREEN)
    ch.check_true(sp.solve_univariate_inequality(3 * x + 2 < 14, x, relational=False) == sp.Interval.open(-sp.oo, 4))
    y_ = f.reserve(52)
    numline(f.pg, L + 40, y_ + 18, 260, -2, 6, 4, False, False)
    f.pg.note(L + 330, y_ + 2, "open circle: 4 itself is not included", C.GREY, 14)
    f.p("{b:Example 2:} $5 - 2x \\ge 11$.", 14, gap=6)
    step(f, r"-2x\ge6", "−5 on both sides", size=18)
    step(f, r"x\le-3", "÷ (−2): FLIP ≥ to ≤", size=18, color=C.GREEN)
    ch.check_true(sp.solve_univariate_inequality(5 - 2 * x >= 11, x, relational=False) == sp.Interval(-sp.oo, -3))
    y_ = f.reserve(52)
    numline(f.pg, L + 40, y_ + 18, 260, -6, 2, -3, True, False)
    f.pg.note(L + 330, y_ + 2, "filled circle: −3 is included", C.GREY, 14)
    f.p("{G:Check:} $x = -4$ (inside): $5 + 8 = 13 \\ge 11$ ✓. $x = 0$ (outside): $5 \\ge 11$ is false ✓.",
        13.5, gap=8)
    ch.check_true(5 - 2 * (-4) >= 11 and not (5 - 2 * 0 >= 11))
    f.p("{b:Example 3 (two-sided):} $-1 < 2x + 3 \\le 9$. Do each move to {B:all three} parts:", 14, gap=6)
    step(f, r"-4<2x\le6\ \Rightarrow\ -2<x\le3", "−3, then ÷2", size=18, color=C.GREEN)
    ch.check_true(sp.solve_univariate_inequality(2 * x + 3 > -1, x, relational=False).intersect(
        sp.solve_univariate_inequality(2 * x + 3 <= 9, x, relational=False)) == sp.Interval.Lopen(-2, 3))


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Balance", None, "do the same to both sides; check the answer in the original"),
        ("Linear equations", None, "clear brackets and fractions, letters to one side, divide, check"),
        ("Cross-multiplying", r"\frac ab=\frac cd\ \Rightarrow\ ad=bc", None),
        ("Elimination", None, "scale one or both equations to match a letter; {B:same signs subtract, "
         "opposite signs add}"),
        ("Substitution", None, "rearrange one equation for a letter, substitute into the other, solve, "
         "back-substitute, check both"),
        ("Zero product", r"AB=0\ \Rightarrow\ A=0\ \text{or}\ B=0", "{R:rearrange to = 0 before factorising}"),
        ("Quadratic formula", r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}", "for $ax^2+bx+c=0$"),
        ("Discriminant", r"\Delta=b^2-4ac", "$>0$ two roots, $=0$ equal roots, $<0$ no real roots"),
        ("Given a root", None, "substitute it; it must make the equation true"),
        ("Completing the square", r"x^2+bx+c=\left(x+\frac b2\right)^2-\left(\frac b2\right)^2+c",
         "$a\\ne1$: take $a$ out of the $x$ terms first; vertex at $(-p, q)$"),
        ("Rejecting answers", None, "negative lengths/times; values making a denominator 0"),
        ("Inequalities", None, "as equations, but {R:× or ÷ by a negative flips the sign}; open circle "
         "$<$, filled $\\le$"),
    ], C.GREEN, title="Solving rules")


def your_turn(ch):
    f = flow(ch)
    sec(f, "Balance scales: your turn", fresh=True)
    f.p("Answers in grey. Put every answer back into the question to check it.", 13.5, gap=10)
    groups = [
        ("One unknown", ["4x − 7 = 13", "6x + 1 = 2x + 17", "5(x − 3) = 2x + 3", "(x + 4)/3 = (x − 2)/2",
                         "How much 10% solution must be added to 40 ml of 30% solution to make 20%?"],
         "1. x = 5   2. x = 4   3. x = 6   4. x = 14   5. 40 ml"),
        ("Two unknowns", ["x + y = 10,  x − y = 4", "2x + 3y = 13,  x + y = 5",
                          "3 pens and 2 pads cost £7; 1 pen and 2 pads cost £5. Find each price.",
                          "Is x + y = 3, 2x + 2y = 6 one answer, none, or endless?",
                          "Compounds 3: how much of the 80 g/L and 25 g/L solutions make 70 ml at 45 g/L?"],
         "6. x = 7, y = 3   7. x = 2, y = 3   8. pen £1, pad £2   9. endless (same line)   "
         "10. about 25.5 ml and 44.5 ml"),
        ("Quadratics (Δ first)", ["x² = 49", "x² − 5x + 6 = 0", "x² + 2x − 8 = 0", "x² = 7x",
                                  "Complete the square: x² + 8x + 10", "x² + 4x + 1 = 0 (2 d.p.)"],
         "11. ±7   12. Δ = 1: x = 2 or 3   13. Δ = 36: x = 2 or −4   14. x = 0 or 7   15. (x + 4)² − 6   "
         "16. Δ = 12: −0.27 or −3.73"),
        ("Methods, words and inequalities", ["Use substitution: y = 3x − 1 and 2x + y = 9",
                                             "Use elimination (scale both): 2x + 3y = 8, 3x + 2y = 7",
                                             "Solve (x + 2)(x − 3) = 6",
                                             "Complete the square: 3x² − 12x + 5",
                                             "Solve 7 − 3x > 1 and show it on a number line",
                                             "A rectangle is 2 m longer than it is wide, with area 48 m². Width?",
                                             "Solve 2/x + x = 3"],
         "17. x = 2, y = 5   18. x = 1, y = 2   19. x² − x − 12 = 0: x = 4 or −3   20. 3(x − 2)² − 7   "
         "21. x < 2 (open circle)   22. 6 m (reject −8)   23. x = 1 or 2"),
        ("Find the unknown", ["Find k so that x² + kx + 16 = 0 has equal roots.",
                              "One root of x² + kx − 12 = 0 is 3. Find k and the other root.",
                              "For which k does x² + 6x + k = 0 have no real roots?",
                              "x = −2 is a root of 2x² + 5x + k = 0. Find k and the other root.",
                              "ax + 2y = 11 and x − y = 2 have the solution x = 3. Find y and a.",
                              "kx² + 4x + 1 = 0 has equal roots. Find k."],
         "24. k = ±8 (k² − 64 = 0)   25. k = 1, other root −4 (9 + 3k − 12 = 0)   26. k > 9 (36 − 4k < 0)   "
         "27. k = 2, other root −1/2 (8 − 10 + k = 0)   28. y = 1, a = 3 (3a + 2 = 11)   29. k = 4 (16 − 4k = 0)"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 40)
        f.text(title, 14, C.GREEN, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{n}. {qq}", 13, gap=5, x=L + 14)
            n += 1
        ans = "   ".join(a.replace(" ", "\u00a0") for a in ans.split("   "))
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    S = sp.solve
    ch.check(S(4 * x - 7 - 13, x), [5])
    ch.check(S(6 * x + 1 - (2 * x + 17), x), [4])
    ch.check(S(5 * (x - 3) - (2 * x + 3), x), [6])
    ch.check(S((x + 4) / 3 - (x - 2) / 2, x), [14])
    ch.check(S((12 + sp.Rational(1, 10) * V) / (40 + V) - sp.Rational(1, 5), V), [40])
    ch.check(S([x + y - 10, x - y - 4], [x, y]), {x: 7, y: 3})
    ch.check(S([2 * x + 3 * y - 13, x + y - 5], [x, y]), {x: 2, y: 3})
    ch.check(S([3 * x + 2 * y - 7, x + 2 * y - 5], [x, y]), {x: 1, y: 2})
    sol = S([x + y - 70, sp.Rational(8, 100) * x + sp.Rational(25, 1000) * y - sp.Rational(315, 100)], [x, y])
    ch.check_num(sol[y], 44.545, tol=0.01)
    ch.check_num(sol[x], 25.45, tol=0.01)
    ch.check(S(x ** 2 - 5 * x + 6, x), [2, 3])
    ch.check(S(x ** 2 + 2 * x - 8, x), [-4, 2])
    ch.check(S(x ** 2 - 7 * x, x), [0, 7])
    ch.check([25 - 24, 4 + 32, 16 - 4], [1, 36, 12])
    ch.check(sp.expand((x + 4) ** 2 - 6), x ** 2 + 8 * x + 10)
    ch.check_num(-2 + math.sqrt(3), -0.27, tol=0.005)
    ch.check_num(-2 - math.sqrt(3), -3.73, tol=0.005)
    k, a = sp.symbols("k a")
    ch.check(S([y - (3 * x - 1), 2 * x + y - 9], [x, y]), {x: 2, y: 5})
    ch.check(S([2 * x + 3 * y - 8, 3 * x + 2 * y - 7], [x, y]), {x: 1, y: 2})
    ch.check(S((x + 2) * (x - 3) - 6, x), [-3, 4])
    ch.check(sp.expand(3 * (x - 2) ** 2 - 7), 3 * x ** 2 - 12 * x + 5)
    ch.check_true(sp.solve_univariate_inequality(7 - 3 * x > 1, x, relational=False) == sp.Interval.open(-sp.oo, 2))
    ch.check(S(x * (x + 2) - 48, x), [-8, 6])
    ch.check(S(sp.Eq(2 / x + x, 3), x), [1, 2])
    ch.check(S(sp.discriminant(x ** 2 + k * x + 16, x), k), [-8, 8])
    ch.check(S(9 + 3 * k - 12, k), [1])
    ch.check(S(x ** 2 + x - 12, x), [-4, 3])
    ch.check_true(sp.solve_univariate_inequality(sp.discriminant(x ** 2 + 6 * x + k, x) < 0, k, relational=False)
                  == sp.Interval.open(9, sp.oo))
    ch.check(S(2 * 4 - 10 + k, k), [2])
    ch.check(S(2 * x ** 2 + 5 * x + 2, x), [-2, -sp.Rational(1, 2)])
    ch.check(S([a * x + 2 * y - 11, x - y - 2, x - 3], [x, y, a], dict=True), [{x: 3, y: 1, a: 3}])
    ch.check(S(sp.discriminant(k * x ** 2 + 4 * x + 1, x), k), [4])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    balance(ch)
    brackets_fractions(ch)
    mixing(ch)
    receipts(ch)
    substitution(ch)
    lines(ch)
    compounds(ch)
    zero_trick(ch)
    formula(ch)
    vertex(ch)
    discriminant(ch)
    find_unknown(ch)
    word_problems(ch)
    inequalities(ch)
    summary(ch)
    your_turn(ch)
