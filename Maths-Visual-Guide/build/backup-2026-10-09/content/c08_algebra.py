"""Chapter 8 - Algebra: letters as sealed envelopes, an x-ray of 3x^2 + 5x - 7, opening the
envelopes (substitution), turning words into algebra, and the Greek-letter phrasebook."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

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
    sec(f, "An x-ray of  3x² + 5x − 7", room=440)
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
    sec(f, "Expression, equation, formula, identity", room=330)
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
    f.p("{B:Substitution} means replacing each letter with its number. The safe way: {B:rub out the "
        "letter and write the number in brackets}, then use BODMAS (Chapter 1). Find "
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
    f.p("{b:Formulas work the same way.} Physics: $v = u + at$ with $u = 3$, $a = 2$, $t = 5$ "
        "(the letters are starting speed, acceleration and time):", 14, gap=6)
    step(f, r"v=(3)+(2)(5)=3+10=13", "at means a × t", size=19, color=C.GREEN)
    ch.check(3 + 2 * 5, 13)


def forming(ch):
    f = flow(ch)
    sec(f, "Turning words into algebra", room=400)
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
        ("Substitution (x = 3, y = −2)", ["2x + 5", "x² − y", "3y²", "xy − 4", "(x + y)²"],
         "4. 11   5. 11   6. 12   7. −10   8. 1"),
        ("Words to algebra", ["A number, times 4, minus 7", "£p shared equally between 3 people",
                              "The cost of 5 pens at q pence each and a pad at 90p", "7 more than twice a number"],
         "9. 4n − 7   10. p/3   11. 5q + 90   12. 2n + 7"),
        ("Types", ["Expression, equation, formula or identity?  (a) 3x − 1   (b) 3x − 1 = 8   (c) E = mc²   "
                   "(d) x + x ≡ 2x"], "13. (a) expression (b) equation (c) formula (d) identity"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14, w=W - 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    X, Y = 3, -2
    ch.check(2 * X + 5, 11)
    ch.check(X ** 2 - Y, 11)
    ch.check(3 * Y ** 2, 12)
    ch.check(X * Y - 4, -10)
    ch.check((X + Y) ** 2, 1)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    envelopes(ch)
    grammar(ch)
    xray(ch)
    words(ch)
    substitution(ch)
    forming(ch)
    greek(ch)
    your_turn(ch)
