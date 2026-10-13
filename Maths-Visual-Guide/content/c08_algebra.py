"""Chapter 8 - Algebra: letters as sealed envelopes, an x-ray of 3x^2 + 5x - 7, opening the
envelopes (substitution), turning words into algebra, and the Greek-letter phrasebook."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, section, step, title_block

ORDER = 8
NUM = 8
TITLE = "Algebra: letters for numbers"
SHORT = "Algebra"
SLUG = "Algebra"
ACCENT = C.BLUE
REQUIRES = ["letters-stand-for-numbers", "multiplication-notation", "order-of-operations", "negative-numbers",
            "square-and-root-words", "brackets-first", "equals-sign"]
INTRODUCES = ["variable", "algebraic-notation", "term", "coefficient", "constant", "expression",
              "equation-vs-expression", "substitution", "forming-expressions", "greek-letters", "identity"]

ENV = "#f3e2b3"
ENV_EDGE = "#a0782c"
PAPER = "#fbfcff"
x = sp.symbols("x")
uk = sp.symbols("uk")


def ex(f, s):
    f.need(100)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


def solve1(eq):
    """The single solution of a linear equation in `uk` (written as expression = 0)."""
    (s,) = sp.solve(eq, uk)
    return s


def icon(pg, x0, y0):
    envelope(pg, x0, y0 + 3, 18, 13, None)


def sec(f, t, **kw):
    section(f, t, C.BLUE, icon, **kw)


def envelope(pg, x0, y0, w=46, h=32, letter="x", col=C.BLUE, size=16):
    pg.rect(x0, y0, w, h, ENV_EDGE, 1.1, fillcolor=ENV)
    pg.poly([(x0, y0), (x0 + w / 2, y0 + h * 0.55), (x0 + w, y0)], ENV_EDGE, 1.0)
    if letter:
        pg.eq(x0 + w / 2, y0 + h * 0.66, letter, size, col, align="center", valign="middle", solid=False)


def sweets(pg, x0, y0, n, col=C.PINK, gap=11):
    for i in range(n):
        pg.circle(x0 + i * gap, y0, 4, col, 1, fillcolor="#f8bbd0")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 8, "Algebra: letters for numbers", "a letter is a sealed envelope with a "
                     "number inside", C.BLUE, PAPER)
    envelope(pg, L + 40, 220, 90, 62, "x", size=30)
    pg.text(L + 150, 236, "+", 30, C.INK, F.BOLD)
    sweets(pg, L + 190, 252, 3, gap=18)
    pg.note(L + 40, 292, "a sealed envelope of sweets, and 3 loose ones", ENV_EDGE, 17)
    pg.eq(L + 330, 236, r"x+3", 36, C.BLUE)
    f = ch.flow(top=400)
    f.p("Algebra scares people because suddenly there are letters in the sums. But a letter is "
        "just a {B:number you can't see yet}, like sweets in a sealed envelope. Everything you know "
        "about numbers still works; you just can't do the final bit of arithmetic until someone "
        "opens the envelope.", 14, gap=10)
    f.p("This chapter teaches the {B:grammar} of algebra: how things are written, what each part "
        "of an expression is called, how to put numbers in (substitution), and how to turn "
        "sentences into algebra. Chapters 11 to 15 then teach you to move algebra around.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 2} {y:(algebra, letters as numbers, Greek letters).}", 12.5)


def envelopes(ch):
    f = flow(ch)
    sec(f, "A letter is a sealed envelope")
    f.p("I hand you an envelope with some sweets in it, and 3 loose sweets. How many do you have? "
        "You can't say a number, but you {B:can} describe it exactly: \"whatever is in the "
        "envelope, plus 3\". Name the envelope $x$, and that's $x + 3$.", 14, gap=8)
    ch.term("variable", "a letter standing for a number that can change or is not yet known")
    rows = [
        (lambda pg, y: (envelope(pg, L + 20, y), pg.text(L + 76, y + 6, "+", 18, C.INK, F.BOLD),
                        sweets(pg, L + 100, y + 16, 3)), r"x+3", "an envelope and 3 more sweets"),
        (lambda pg, y: (envelope(pg, L + 20, y), envelope(pg, L + 72, y)), r"2x",
         "TWO envelopes with the same letter. Same letter = same number inside, always."),
        (lambda pg, y: (envelope(pg, L + 20, y), envelope(pg, L + 72, y, letter="y", col=C.GREEN)), r"x+y",
         "different letters: might be different numbers (might be the same, by luck)"),
        (lambda pg, y: (envelope(pg, L + 20, y), envelope(pg, L + 72, y), envelope(pg, L + 124, y),
                        pg.text(L + 176, y + 6, "-", 18, C.INK, F.BOLD), sweets(pg, L + 196, y + 16, 1)),
         r"3x-1", "three envelopes, then eat one sweet"),
    ]
    for draw, lat, say in rows:
        y = f.reserve(58)
        pg = f.pg
        draw(pg, y + 4)
        pg.eq(L + 236, y + 6, lat, 21, C.BLUE)
        pg.note(L + 320, y + 6, say, C.RED, 15, w=R - L - 320)
    f.p("{b:Opening the envelopes.} If it turns out $x = 5$, then $x + 3 = 8$, $2x = 10$ and "
        "$3x - 1 = 14$. Until then, the algebra is a {B:recipe} waiting for its ingredient.", 14)
    ch.check((x + 3).subs(x, 5), 8)
    ch.check((3 * x - 1).subs(x, 5), 14)


def grammar(ch):
    f = flow(ch)
    sec(f, "The grammar: what's hidden, what's shortened", room=440)
    rule_box(f, "algebraic notation", [
        "A number next to a letter, or two letters side by side, are {B:multiplied}: $3x=3\\times x$, "
        "$xy=x\\times y$. A letter on its own has coefficient 1: $x=1x$.",
        "Division is written as a fraction: $\\frac{x}{2}=x\\div2$.",
        "A power applies only to the thing it touches: $x^2=x\\times x$ (not $2x$), "
        "$3x^2=3\\times x\\times x$, but $(3x)^2=3x\\times3x=9x^2$.",
        "Write the number first, then the letters in alphabetical order: $3ab$, not $a3b$.",
    ], C.BLUE)
    f.p("Algebra is written in a shorthand. Each rule below is tested with $x = 5$, so you can "
        "{B:see} it's true rather than take it on trust:", 14, gap=8)
    rows = [(r"3x", r"3\times x", r"3\times5=15", "the × between a number and a letter is invisible"),
            (r"xy", r"x\times y", r"", "letters side by side are multiplied too"),
            (r"x", r"1x", r"1\times5=5", "a lonely x means one x; we never write the 1"),
            (r"\frac{x}{2}", r"x\div2", r"5\div2=2.5", "division is written as a fraction"),
            (r"x^2", r"x\times x", r"5\times5=25", "x squared: NOT 2 × x (that's 10)"),
            (r"3x^2", r"3\times x\times x", r"3\times25=75", "the power sits on x only, not on the 3"),
            (r"(3x)^2", r"3x\times3x", r"15\times15=225", "brackets put the power on everything inside")]
    for a, b, test, why in rows:
        y = f.reserve(40)
        pg = f.pg
        pg.eq(L + 10, y + 16, a, 20, C.BLUE, valign="middle")
        pg.text(L + 70, y + 6, "means", 11, C.GREY)
        pg.eq(L + 116, y + 16, b, 17, valign="middle")
        if test:
            pg.eq(L + 216, y + 16, test, 14, C.GREEN, valign="middle")
        pg.note(L + 330, y + 2, why, C.RED, 14, w=R - L - 330)
    ch.check((3 * x ** 2).subs(x, 5), 75)
    ch.check(((3 * x) ** 2).subs(x, 5), 225)
    f.p("{b:Order:} write the number first, then letters (usually alphabetical): $3ab$, not $a3b$ "
        "or $ba3$. They mean the same (multiplying in any order gives the same answer) but "
        "$3ab$ is the tidy way.", 14)


def xray(ch):
    f = flow(ch)
    sec(f, "An x-ray of  3x² + 5x − 7", room=560)
    rule_box(f, "the parts of an expression", [
        "{B:Terms} are the pieces separated by $+$ and $-$ signs. Each sign belongs to the term after it.",
        "The {B:coefficient} of a term is the number multiplying its letters, {B:sign included}: in "
        "$x^2-x$ the coefficients are $1$ and $-1$.",
        "A {B:constant} is a term with no letter.",
    ], C.BLUE)
    f.p("Your lectures will use words like {B:term}, {B:coefficient} and {B:constant} without "
        "stopping. Here's every part labelled on one example:", 14, gap=8)
    y = f.reserve(230)
    pg = f.pg
    X0 = L + 110
    # draw the expression piece by piece so parts can be pointed at
    parts = [(r"3", C.ORANGE), (r"x^{2}", C.BLUE), (r"+", C.GREY), (r"5", C.ORANGE), (r"x", C.BLUE),
             (r"-", C.GREY), (r"7", C.PURPLE)]
    xs = []
    xx = X0
    for lat, col in parts:
        w, h = pg.eq(xx, y + 90, lat, 40, col)
        xs.append((xx, w))
        xx += w + 12
    # term brackets underneath
    def under(i0, i1, lab, col, dy):
        a = xs[i0][0]
        b = xs[i1][0] + xs[i1][1]
        pg.brace(b, y + 146, a, y + 146, col, 1.2, 7)
        pg.note((a + b) / 2 - 30, y + 158 + dy, lab, col, 15)
    under(0, 1, "term 1", C.INK, 0)
    under(2, 4, "term 2: +5x", C.INK, 0)
    under(5, 6, "term 3: −7", C.INK, 0)
    # labels above
    def above(i, text, col, tx, ty):
        cx = xs[i][0] + xs[i][1] / 2
        pg.arrow(tx + 20, ty + 22, cx, y + 86, col, 1.1, head=5)
        pg.note(tx, ty, text, col, 15)
    above(0, "coefficient: the number\nmultiplying the letter", C.ORANGE, L, y)
    above(1, "variable (x) with a\npower (index) of 2", C.BLUE, L + 170, y - 4)
    above(6, "constant: a plain number,\nno letter, never changes", C.PURPLE, L + 330, y)
    pg.note(xs[2][0] - 10, y + 190, "the + and − signs split the expression into terms,\n"
            "and each sign belongs to the term after it", C.GREY, 14)
    ch.term("term", "one piece of an expression, separated from the others by + or − signs")
    ch.term("coefficient", "the number multiplying a letter, e.g. 5 in 5x")
    ch.term("constant", "a term with no letter: a fixed number")
    ch.term("power (index, exponent)", "the small raised number: how many times to multiply by itself")
    f.p("{b:Lonely letters have invisible coefficients.} In $x^2 - x$, the coefficient of $x^2$ is 1 "
        "and the coefficient of $x$ is {B:−1} (the minus sign is part of it).", 14, gap=8)
    f.p("{b:The whole thing} $3x^2 + 5x - 7$ is called an {B:expression}: a mathematical phrase. "
        "It has no equals sign, so it doesn't claim anything; it's just a quantity.", 14)
    ch.term("expression", "a combination of numbers, letters and operations with no equals sign")


def words(ch):
    f = flow(ch)
    sec(f, "Expression, equation, formula, identity", room=420)
    rule_box(f, "four kinds of algebraic statement", [
        "{B:Expression}: no equals sign. It can be simplified or evaluated, but not solved.",
        "{B:Equation}: two expressions joined by $=$, true only for particular values. Solving it "
        "means finding those values.",
        "{B:Formula}: an equation linking real quantities; substitute the known ones to find the other.",
        "{B:Identity}: true for {B:every} value of the letters, written with $\\equiv$.",
    ], C.BLUE)
    f.p("These four words sound alike but do different jobs. Think of them as types of sentence:",
        14, gap=8)
    rows = [("expression", r"2x+3", "a phrase: no equals sign, no claim. Like \"two coffees and a cake\".", C.BLUE),
            ("equation", r"2x+3=11", "a claim that's true only for some values. Here only x = 4. Solving "
             "means finding them (Chapter 15).", C.ORANGE),
            ("formula", r"A=lw", "a rule linking real quantities (area = length × width). Plug numbers in "
             "to get the answer.", C.GREEN),
            ("identity", r"2(x+3)\equiv2x+6", "true for EVERY value of x. The ≡ (three lines) says "
             "\"identical\": two ways of writing the same thing.", C.PURPLE)]
    for name, lat, say, col in rows:
        y = f.reserve(62)
        pg = f.pg
        pg.text(L + 10, y + 4, name, 13, col, F.BOLD)
        pg.eq(L + 96, y + 2, lat, 17, col)
        pg.note(L + 270, y, say, C.INK, 14, w=R - L - 270)
    ch.term("equation", "a statement that two expressions are equal; true only for particular values")
    ch.term("formula", "an equation linking real quantities, used by substituting values")
    ch.term("identity", "an equation true for every value of the letters, written with ≡")
    ch.symbol(r"\equiv", "is identically equal to", "true for all values")
    ch.check_true(sp.expand(2 * (x + 3)) == 2 * x + 6)


def substitution(ch):
    f = flow(ch)
    sec(f, "Substitution: open the envelopes", room=500)
    rule_box(f, "substitution", [
        "Replace every letter by its value, written {B:in brackets}: $x=-3$ turns $2x^2$ into $2(-3)^2$.",
        "Work out the result in the order of operations (BODMAS, Chapter 1): {B:B}rackets, then "
        "{B:O}rders (powers and roots), then {B:D}ivision and {B:M}ultiplication left to right, then "
        "{B:A}ddition and {B:S}ubtraction left to right.",
        "A fraction line groups like brackets: work out the {B:whole top} and the {B:whole bottom} first, "
        "then divide.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    rule_box(f, "signs when multiplying and powering", [
        "$(+)\\times(+)=+$,   $(-)\\times(-)=+$,   $(+)\\times(-)=-$,   $(-)\\times(+)=-$.",
        "So a negative number to an {B:even} power is positive: $(-3)^2=9$. To an {B:odd} power it stays "
        "negative: $(-2)^3=-8$.",
        "$-3^2$ means $-(3^2)=-9$: without brackets the power is done first and the minus after. "
        "That is why you always bracket a substituted number.",
    ], C.BLUE)
    ch.check((-3) ** 2, 9)
    ch.check((-2) ** 3, -8)
    ch.check(-3 ** 2, -9)
    f.p("{B:Substitution} means replacing each letter with its number. Find "
        "$3x^2 + 5x - 7$ when $x = 2$:", 14, gap=8)
    ch.term("substitution", "replacing letters by given numbers, then working out the value")
    step(f, r"3x^2+5x-7", "the expression")
    step(f, r"3(2)^2+5(2)-7", "rub out each x, write (2)", col=C.BLUE)
    step(f, r"3\times4+10-7", "powers first: (2)² = 4; and 5 × 2 = 10")
    step(f, r"12+10-7=15", "multiply, then add and take away left to right", color=C.GREEN)
    ch.check((3 * x ** 2 + 5 * x - 7).subs(x, 2), 15)
    f.p("{R:Now the one everyone gets wrong:} $x = -1$. The brackets save you:", 14, gap=6)
    step(f, r"3(-1)^2+5(-1)-7", "brackets around the −1", col=C.BLUE)
    step(f, r"3\times1-5-7", "(−1)² = (−1) × (−1) = +1 (negative × negative, Ch. 1)")
    step(f, r"3-5-7=-9", "", color=C.GREEN)
    ch.check((3 * x ** 2 + 5 * x - 7).subs(x, -1), -9)
    msg = ("{R:Without brackets} you'd type $-1^2$ into a calculator and get $-1$, "
            "because the calculator squares the 1 first and then applies the minus. With brackets, "
            "$(-1)^2 = 1$. Always bracket negative numbers when substituting.")
    bh = f.pg.rich_h(msg, W - 48, 13) + 18
    y = f.reserve(bh + 8)
    pg = f.pg
    pg.rect(L + 10, y, W - 20, bh, C.RED, 1.2, fillcolor="#fff3f3", r=8)
    pg.rich(L + 24, y + 9, msg, W - 48, 13)
    ex(f, "$2x^2$ when $x=-3$.")
    step(f, r"2(-3)^2=2\times9=18", "power first: (−3)² = +9, then × 2", size=19, color=C.GREEN)
    step(f, r"\red{\text{not }}2\times(-9)=-18", "that squares 3 and forgets the minus", size=17,
         color=C.GREY)
    ch.check((2 * x ** 2).subs(x, -3), 18)
    ex(f, "$\\dfrac{x+y}{x-y}$ when $x=5$ and $y=-3$.")
    step(f, r"\frac{(5)+(-3)}{(5)-(-3)}", "brackets round both values", size=19, col=C.BLUE)
    step(f, r"=\frac{5-3}{5+3}=\frac{2}{8}", "top: + (−3) = − 3;  bottom: − (−3) = + 3", size=19)
    step(f, r"=\frac14", "simplify the fraction (Chapter 2)", size=19, color=C.GREEN)
    X_, Y_ = sp.Integer(5), sp.Integer(-3)
    ch.check((X_ + Y_) / (X_ - Y_), sp.Rational(1, 4))
    f.p("{R:Not} $\\frac{5+3}{5-3}$: the minus sign of $y$ must come in with it. And never cancel the "
        "5s: the top and bottom are sums, so each must be finished before dividing.", 13.5, gap=8)
    f.p("{b:Formulas work the same way.} Physics: $v = u + at$ with $u = 3$, $a = 2$, $t = 5$ "
        "(the letters are starting speed, acceleration and time):", 14, gap=6)
    step(f, r"v=(3)+(2)(5)=3+10=13", "at means a × t", size=19, color=C.GREEN)
    ch.check(3 + 2 * 5, 13)


def forming(ch):
    f = flow(ch)
    sec(f, "Turning words into algebra", room=400)
    rule_box(f, "forming an expression from words", [
        "Choose a letter for each unknown quantity and say what it stands for (\"let $n$ be the number\").",
        "Translate one phrase at a time, in the order the sentence gives them.",
        "If an operation applies to {B:everything so far}, put everything so far in brackets: "
        "\"add 3, then multiply by 5\" is $5(n+3)$, not $5n+3$.",
        "Test with a number: pick $n=2$, follow the words, and check the expression gives the same.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    f.p("Read the sentence slowly and translate one phrase at a time, like a phrasebook:", 14, gap=8)
    rows = [("\"think of a number\"", r"n", "choose a letter for the unknown"),
            ("\"double it\"", r"2n", "× 2"),
            ("\"add 3\"", r"2n+3", "+ 3 to everything so far"),
            ("\"then multiply by 5\"", r"5(2n+3)", "brackets: the WHOLE thing gets × 5")]
    for words_, lat, why in rows:
        y = f.reserve(36)
        pg = f.pg
        pg.text(L + 10, y + 4, words_, 13.5, C.INK)
        pg.arrow(L + 170, y + 12, L + 200, y + 12, C.GREY, 1.1, head=4)
        pg.eq(L + 210, y + 2, lat, 20, C.BLUE)
        pg.note(L + 330, y + 2, why, C.RED, 15)
    f.p("{b:More translations}, with the tricky words highlighted:", 14, gap=6)
    rows2 = [("2 coffees at c pounds and 3 cakes at k pounds", r"2c+3k"),
             ("a rectangle l long and w wide: perimeter", r"2l+2w"),
             ("5 {R:less than} a number", r"n-5\ \ (\text{not }5-n)"),
             ("a number {R:shared equally} between 4", r"\frac{n}{4}"),
             ("the {R:square} of a number, plus the number", r"n^2+n")]
    for s, lat in rows2:
        y = f.reserve(40)
        pg = f.pg
        pg.rich(L + 10, y + 4, s, 300, 13.5)
        pg.eq(L + 330, y + 2, lat, 18, C.BLUE)
    f.p("{h:\"less than\" reverses the order:} \"5 less than 12\" is 12 − 5 = 7. Test with a number "
        "whenever you're unsure.", 13.5, C.BROWN)


def forming_equations(ch):
    f = flow(ch)
    sec(f, "From words to an equation, and solving it", room=520)
    f.p("When the words also tell you the {B:result}, the expression becomes an {B:equation}, and "
        "the unknown can be found. Chapter 15 covers solving in full; simple ones need only one idea:",
        14, gap=8)
    rule_box(f, "keeping an equation balanced", [
        "An equation stays true if you do {B:the same thing to both sides}: add, subtract, multiply or "
        "divide (but not divide by 0).",
        "To get the unknown alone, undo what was done to it in {B:reverse order}: the last operation "
        "applied is the first one you undo. $+$ is undone by $-$, $\\times$ by $\\div$.",
    ], C.BLUE)
    rule_box(f, "word problem to answer", [
        "Let a letter stand for the unknown.",
        "Write an expression for the quantity the words describe.",
        "Set it equal to the value given: that is the equation.",
        "Solve by undoing operations in reverse order, the same on both sides.",
        "Check the answer in the {B:words} of the question, not just the equation.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    ex(f, "I think of a number, double it and add 3. The answer is 17. What was the number?")
    step(f, r"2n+3=17", "let n be the number; double, then + 3", size=19)
    step(f, r"2n=14", "undo the last step first: − 3 from both sides", size=19)
    step(f, r"n=7", "undo × 2: ÷ 2 both sides", size=19, color=C.GREEN)
    ch.check(solve1(2 * uk + 3 - 17), 7)
    f.p("Check in words: double 7 is 14, add 3 is 17 ✓.", 13.5, C.GREEN, gap=8)
    ex(f, "4 concert tickets plus a £3 booking fee cost £35. How much is one ticket?")
    step(f, r"4t+3=35", "let t be the price of one ticket in £", size=19)
    step(f, r"4t=32", "− 3 from both sides", size=19)
    step(f, r"t=8", "÷ 4 both sides: £8 a ticket", size=19, color=C.GREEN)
    ch.check(solve1(4 * uk + 3 - 35), 8)
    ex(f, "think of a number, add 5, then multiply by 3. The answer is 27.")
    step(f, r"3(n+5)=27", "brackets: the whole n + 5 is tripled", size=19)
    step(f, r"n+5=9", "the last step was × 3, so ÷ 3 first", size=19)
    step(f, r"n=4", "then − 5", size=19, color=C.GREEN)
    ch.check(solve1(3 * (uk + 5) - 27), 4)
    f.p("Check: 4 + 5 = 9, and 9 × 3 = 27 ✓.", 13.5, C.GREEN)


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown: formulas with one letter missing", room=520)
    f.p("A very common question type gives you {B:every value but one} and asks for the missing one. "
        "It is substitution followed by a small equation:", 13.5, gap=6)
    rule_box(f, "finding a missing value", [
        "Write down the formula or equation.",
        "Substitute every value you know, in brackets.",
        "Tidy each side (do the arithmetic you can).",
        "Undo the operations round the unknown, in reverse order, doing the same to both sides.",
        "Check by substituting {B:all} the values back into the original.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    ex(f, "$v=u+at$. Given $v=20$, $u=5$ and $t=3$, find $a$.")
    step(f, r"20=(5)+a(3)", "substitute what you know", size=19, col=C.BLUE)
    step(f, r"20=5+3a", "tidy: a × 3 is written 3a", size=19)
    step(f, r"15=3a", "− 5 from both sides", size=19)
    step(f, r"a=5", "÷ 3 both sides", size=19, color=C.GREEN)
    ch.check(solve1(5 + uk * 3 - 20), 5)
    f.p("Check: $5 + 5 \\times 3 = 20$ ✓.", 13.5, C.GREEN, gap=8)
    ex(f, "$3p-4=11$. Find $p$.")
    step(f, r"3p=15", "+ 4 both sides (undo the − 4)", size=19)
    step(f, r"p=5", "÷ 3 both sides", size=19, color=C.GREEN)
    ch.check(solve1(3 * uk - 4 - 11), 5)
    ex(f, "the area of a triangle is $A=\\frac12bh$. $A=24$ and $b=8$: find $h$.")
    step(f, r"24=\tfrac12(8)h=4h", "half of 8 is 4", size=19)
    step(f, r"h=6", "÷ 4 both sides", size=19, color=C.GREEN)
    ch.check(solve1(sp.Rational(1, 2) * 8 * uk - 24), 6)
    ex(f, "when $x=2$, the expression $3x+k$ equals 10. Find $k$.")
    step(f, r"3(2)+k=10\ \Rightarrow\ 6+k=10", "substitute x = 2", size=19)
    step(f, r"k=4", "− 6 both sides", size=19, color=C.GREEN)
    ch.check(solve1(3 * 2 + uk - 10), 4)
    f.p("{h:The unknown can be any letter,} even one that looks like a \"given\" in the formula. "
        "Whichever letter has no value is the one you solve for.", 13.5, C.BROWN)


def common_mistakes(ch):
    f = flow(ch)
    sec(f, "Mistakes to avoid", room=360)
    mistakes(f, [
        (r"x=-3:\ 2x^2=-18", r"2(-3)^2=18", "bracket the substituted value; the square makes it positive"),
        (r"-3^2=9", r"-3^2=-9,\ (-3)^2=9", "without brackets only the 3 is squared"),
        (r"x=2:\ 3x^2=36", r"3(2)^2=12", "the power is on x only; (3x)² would be 36"),
        (r"x^2=2x", r"x^2=x\times x", "squared means times itself, not times 2"),
        (r"5\text{ less than }n=5-n", r"n-5", "\"less than\" reverses the order"),
        (r"x=-3:\ \frac{x+5}{x}=\frac{5}{1}", r"\frac{(-3)+5}{(-3)}=-\frac23", "finish the top and the bottom before dividing; never cancel part of a sum"),
    ])
    ch.check((2 * x ** 2).subs(x, -3), 18)
    ch.check((3 * x ** 2).subs(x, 2), 12)
    ch.check(((x + 5) / x).subs(x, -3), sp.Rational(-2, 3))


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Hidden ×", r"3x=3\times x,\quad xy=x\times y", "a letter alone has coefficient 1"),
        ("Division", r"\frac{x}{2}=x\div2", None),
        ("Powers", r"3x^2=3\times x\times x,\quad(3x)^2=9x^2", "a power applies only to what it touches"),
        ("Terms", None, "pieces separated by $+$ and $-$; each sign belongs to the term after it"),
        ("Coefficient", None, "the number multiplying the letters, sign included ($-1$ in $-x$)"),
        ("Constant", None, "a term with no letter"),
        ("Expression / equation", None, "an expression has no $=$; an equation is true only for some values"),
        ("Formula / identity", r"2(x+3)\equiv2x+6", "a formula links quantities; an identity ($\\equiv$) is true for all values"),
        ("Substitution", None, "replace each letter by its value {B:in brackets}, then BODMAS"),
        ("Sign rules", r"(-)\times(-)=+,\quad(+)\times(-)=-", None),
        ("Powers of negative numbers", r"(-3)^2=9,\quad-3^2=-9,\quad(-2)^3=-8", "even power: positive; odd power: negative"),
        ("Fractions", None, "finish the whole top and the whole bottom, then divide"),
        ("Forming", None, "letter for the unknown; translate phrase by phrase; bracket \"everything so far\""),
        ("Balancing", None, "do the same to both sides; undo operations in reverse order"),
        ("Find the unknown", None, "substitute the known values, tidy, undo, check"),
    ], C.BLUE)


def greek(ch):
    f = flow(ch)
    sec(f, "The Greek-letter phrasebook", room=520)
    f.p("When mathematicians run out of English letters (or want a letter with a traditional job), "
        "they use Greek ones. Your Lecture 2 lists the common ones. Here they are with how to say "
        "them and where you'll meet them:", 14, gap=8)
    rows = [(r"\alpha", "alpha", "AL-fa", "angles; radiation (α particles)"),
            (r"\beta", "beta", "BEE-ta", "angles; radiation"),
            (r"\gamma", "gamma", "GAM-a", "angles; gamma rays"),
            (r"\delta,\ \Delta", "delta", "DEL-ta", "a small change (Δx: change in x) (Ch. 20, 34)"),
            (r"\varepsilon", "epsilon", "EP-si-lon", "a tiny amount; errors"),
            (r"\theta", "theta", "THEE-ta", "the most common angle letter (Ch. 27-31)"),
            (r"\phi", "phi", "FYE (or fee)", "another angle"),
            (r"\lambda", "lambda", "LAM-da", "wavelength; eigenvalues"),
            (r"\mu", "mu", "MEW", "the mean in statistics (Ch. 24, 26)"),
            (r"\sigma,\ \Sigma", "sigma", "SIG-ma", "σ: spread (Ch. 24); Σ: add up (Ch. 17)"),
            (r"\pi", "pi", "PIE", "3.14159..., the circle number"),
            (r"\omega", "omega", "oh-MEE-ga", "angular speed; spinning"),
            (r"\chi", "chi", "KYE", "the chi-squared test in statistics")]
    y = f.reserve(len(rows) * 26 + 30)
    pg = f.pg
    hdr = [("letter", L + 10), ("name", L + 80), ("say it", L + 150), ("you'll meet it in...", L + 250)]
    for s, xx in hdr:
        pg.text(xx, y, s, 11, C.GREY, F.BOLD)
    for i, (lat, name, say, use) in enumerate(rows):
        yy = y + 20 + i * 26
        if i % 2 == 0:
            pg.rect(L + 4, yy - 2, W - 8, 26, "#eef3fb", 0.1, fillcolor="#eef3fb", layer=C.UNDER)
        pg.eq(L + 14, yy + 11, lat, 18, C.BLUE, valign="middle")
        pg.text(L + 80, yy + 4, name, 12.5, C.INK, F.BOLD)
        pg.note(L + 150, yy + 1, say, C.RED, 15)
        pg.text(L + 250, yy + 4, use, 11.5, C.INK)
        ch.symbol(lat, f"{name} ({say})", use)
    f.p("{h:Don't panic when you see one:} a Greek letter is just another envelope with a number in "
        "it. θ = 30° is no different from x = 30.", 13.5, C.BROWN)
    ch.term("Greek letters", "letters like θ, π, σ used as variables or constants with traditional meanings")


def your_turn(ch):
    f = flow(ch)
    sec(f, "Envelopes: your turn", fresh=True)
    f.p("Answers in grey. For every one, test your answer by putting a number in!", 13.5, gap=10)
    groups = [
        ("Reading algebra", ["What does 4ab mean in full?", "Is x² the same as 2x? Test with x = 3",
                             "In 7y³ − y + 2, name the coefficient of y³, the coefficient of y, and the constant"],
         "1. 4 × a × b   2. no: 9 vs 6   3. 7, −1, 2"),
        ("Substitution (x = 3, y = −2)", ["2x + 5", "x² − y", "3y²", "xy − 4", "(x + y)²", "y³",
                                          "(x + y)/(x − y)", "(x − y)/(2y)"],
         "4. 11   5. 11   6. 12   7. −10   8. 1   9. −8   10. 1/5   11. 5/(−4) = −5/4"),
        ("Words to algebra", ["A number, times 4, minus 7", "£p shared equally between 3 people",
                              "The cost of 5 pens at q pence each and a pad at 90p", "7 more than twice a number"],
         "12. 4n − 7   13. p/3   14. 5q + 90   15. 2n + 7"),
        ("Types", ["Expression, equation, formula or identity?  (a) 3x − 1   (b) 3x − 1 = 8   (c) E = mc²   "
                   "(d) x + x ≡ 2x"], "16. (a) expression (b) equation (c) formula (d) identity"),
        ("Find the unknown", ["v = u + at with v = 20, u = 5, t = 3. Find a.", "3p − 4 = 11. Find p.",
                              "P = 2l + 2w with P = 30, l = 9. Find w.", "A = ½bh with A = 24, h = 6. Find b.",
                              "I think of a number, multiply it by 4 and subtract 7. The answer is 21. Find the number.",
                              "When x = 3, 2x + k = 15. Find k."],
         "17. a = 5 (20 = 5 + 3a)   18. p = 5 (3p = 15)   19. w = 6 (30 = 18 + 2w)   20. b = 8 (24 = 3b)   "
         "21. 7 (4n − 7 = 21, 4n = 28)   22. k = 9 (6 + k = 15)"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14, w=W - 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    X, Y = sp.Integer(3), sp.Integer(-2)
    ch.check(2 * X + 5, 11)
    ch.check(X ** 2 - Y, 11)
    ch.check(3 * Y ** 2, 12)
    ch.check(X * Y - 4, -10)
    ch.check((X + Y) ** 2, 1)
    ch.check(Y ** 3, -8)
    ch.check((X + Y) / (X - Y), sp.Rational(1, 5))
    ch.check((X - Y) / (2 * Y), sp.Rational(-5, 4))
    ch.check(solve1(5 + uk * 3 - 20), 5)
    ch.check(solve1(3 * uk - 4 - 11), 5)
    ch.check(solve1(2 * 9 + 2 * uk - 30), 6)
    ch.check(solve1(sp.Rational(1, 2) * uk * 6 - 24), 8)
    ch.check(solve1(4 * uk - 7 - 21), 7)
    ch.check(solve1(2 * 3 + uk - 15), 9)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    envelopes(ch)
    grammar(ch)
    xray(ch)
    words(ch)
    substitution(ch)
    forming(ch)
    forming_equations(ch)
    find_unknown(ch)
    common_mistakes(ch)
    greek(ch)
    summary(ch)
    your_turn(ch)
