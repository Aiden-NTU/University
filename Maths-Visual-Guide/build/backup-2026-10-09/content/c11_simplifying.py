"""Chapter 11 - Simplifying algebraic expressions. Shopping bags for like terms, the minus sign as
a luggage tag, the grid (area) method for brackets, and catching slide errors with numbers."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 11
NUM = 11
TITLE = "Simplifying algebraic expressions"
SHORT = "Simplifying"
SLUG = "Simplifying"
ACCENT = C.BLUE
REQUIRES = ["term", "coefficient", "variable", "negative-numbers", "powers", "index-laws", "substitution",
            "multiplication", "area"]
INTRODUCES = ["like-terms", "collect-like-terms", "multiply-terms", "expand-brackets", "double-brackets",
              "perfect-squares", "difference-of-squares-expansion"]

PAPER = "#fbfdff"
TAG = "#fff1b8"
x, y, a, b = sp.symbols("x y a b")
TERMCOL = {"x2": C.PURPLE, "x": C.BLUE, "y": C.GREEN, "n": C.ORANGE}


def icon(pg, x0, y0):
    bag(pg, x0 + 1, y0 + 4, 16, 13, C.BLUE)


def sec(f, t, **kw):
    section(f, t, C.BLUE, icon, **kw)


def bag(pg, x0, y0, w, h, col):
    pg.rect(x0, y0, w, h, col, 1.3, fillcolor=C.LIGHT[col], r=3)
    pg.arc(x0 + w / 2, y0, w * 0.28, 0, 180, col, 1.2)


def card(pg, x0, y0, sign, body, col, w=None, size=18):
    """A term card with its sign on a luggage tag."""
    bw, bh, _ = pg.eq_size(body, size)
    w = w or bw + 20
    pg.rect(x0, y0, w, 34, col, 1.4, fillcolor=C.LIGHT[col], r=6)
    pg.eq(x0 + w / 2, y0 + 17, body, size, col, align="center", valign="middle")
    # tag on a string
    pg.line(x0 + 4, y0 + 4, x0 - 6, y0 - 8, C.GREY, 0.8)
    pg.rect(x0 - 20, y0 - 22, 20, 16, C.BROWN, 0.9, fillcolor=TAG, r=3)
    pg.text(x0 - 10, y0 - 22, sign, 12, C.RED if sign == "−" else C.GREEN, F.BOLD, align="center", solid=False)
    return w


def grid(pg, x0, y0, left, top, cells, cw=86, ch_=46, size=17, colors=None):
    """Grid method: `left` terms down the side, `top` terms across, cells[i][j] products."""
    pg.rect(x0, y0, 44, 30, C.GREY, 0.8, fillcolor="#f1f3f6")
    pg.eq(x0 + 22, y0 + 15, r"\times", 14, C.GREY, align="center", valign="middle")
    for j, t in enumerate(top):
        pg.rect(x0 + 44 + j * cw, y0, cw, 30, C.ORANGE, 1, fillcolor=C.LIGHT[C.ORANGE])
        pg.eq(x0 + 44 + j * cw + cw / 2, y0 + 15, t, size, C.ORANGE, align="center", valign="middle")
    for i, t in enumerate(left):
        pg.rect(x0, y0 + 30 + i * ch_, 44, ch_, C.GREEN, 1, fillcolor=C.LIGHT[C.GREEN])
        pg.eq(x0 + 22, y0 + 30 + i * ch_ + ch_ / 2, t, size, C.GREEN, align="center", valign="middle")
        for j in range(len(top)):
            col = (colors or {}).get((i, j), C.INK)
            fc = C.LIGHT.get(col, "#ffffff") if col != C.INK else "#ffffff"
            pg.rect(x0 + 44 + j * cw, y0 + 30 + i * ch_, cw, ch_, C.INK, 1, fillcolor=fc)
            pg.eq(x0 + 44 + j * cw + cw / 2, y0 + 30 + i * ch_ + ch_ / 2, cells[i][j], size, col,
                  align="center", valign="middle")
    return 30 + ch_ * len(left), 44 + cw * len(top)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 11, "Simplifying algebraic expressions", "sorting the shopping, and "
                     "multiplying out brackets with a grid", C.BLUE, PAPER)
    bag(pg, L + 40, 220, 120, 90, C.BLUE)
    bag(pg, L + 200, 220, 120, 90, C.GREEN)
    for i in range(7):
        pg.circle(L + 60 + (i % 4) * 26, 250 + (i // 4) * 28, 10, C.RED, 1, fillcolor="#ff8a80")
    for i in range(3):
        pg.ellipse(L + 225 + i * 32, 262, 8, 18, C.BROWN, 1, fillcolor="#ffe082")
    pg.eq(L + 100, 320, r"7a", 24, C.BLUE, align="center")
    pg.eq(L + 260, 320, r"3b", 24, C.GREEN, align="center")
    pg.note(L + 350, 250, "apples in one bag,\nbananas in the other.\nNever \"10ab\"!", C.RED, 18)
    f = ch.flow(top=390)
    f.p("Simplifying means rewriting an expression so it's {B:shorter but equal}: the same value "
        "for every number you could put in. Two skills do almost all of the work: {B:collecting like "
        "terms} (sorting the shopping into bags) and {B:expanding brackets} (multiplying everything "
        "inside by what's outside).", 14, gap=10)
    f.p("Every rule is tested with numbers, so you'll never have to wonder \"is this allowed?\". "
        "That same habit catches two mistakes on the Lecture 2 slides, near the end of the chapter.",
        14, gap=10)
    f.p("{y:Goes with} {B:Lecture 2} {y:(expanding brackets, common mistakes).}", 12.5)


def like_terms(ch):
    f = flow(ch)
    sec(f, "Like terms: same fruit, same bag")
    f.p("Your shopping: {B:3 apples, 2 bananas, 4 apples, 1 banana}. Written with $a$ for an apple "
        "and $b$ for a banana: $3a + 2b + 4a + b$. Sort into bags:", 14, gap=8)
    y_ = f.reserve(90)
    pg = f.pg
    bag(pg, L + 30, y_ + 10, 130, 60, C.BLUE)
    pg.eq(L + 95, y_ + 40, r"3a+4a=7a", 18, C.BLUE, align="center", valign="middle")
    bag(pg, L + 200, y_ + 10, 130, 60, C.GREEN)
    pg.eq(L + 265, y_ + 40, r"2b+b=3b", 18, C.GREEN, align="center", valign="middle")
    pg.eq(L + 360, y_ + 30, r"=7a+3b", 22)
    ch.check(3 * a + 2 * b + 4 * a + b, 7 * a + 3 * b)
    f.p("Terms with {B:exactly the same letters and powers} are {B:like terms}: they can be added "
        "by adding their coefficients. Different letters stay separate: $7a + 3b$ can't be squashed "
        "into $10ab$ (10 apple-bananas?).", 14, gap=8)
    ch.term("like terms", "terms with exactly the same letters raised to the same powers, e.g. 3x² and −5x²")
    f.p("{R:Powers count as a different fruit.} $x$ and $x^2$ are {B:not} like terms. Test with "
        "$x = 3$: $x + x^2 = 3 + 9 = 12$, but \"$2x^2$\" would be 18 and \"$2x$\" would be 6. So "
        "$x + x^2$ stays as it is.", 14, gap=8)
    f.p("{b:A bigger example, colour-coded by kind:}", 14, gap=6)
    y_ = f.reserve(110)
    pg = f.pg
    parts = [(r"5x^2", C.PURPLE), (r"+3x", C.BLUE), (r"-2x^2", C.PURPLE), (r"+7", C.ORANGE), (r"-x", C.BLUE),
             (r"+1", C.ORANGE)]
    xx = L + 20
    for lat, col in parts:
        w, h = pg.eq(xx, y_, lat, 22, col)
        xx += w + 6
    pg.note(L + 20, y_ + 34, "purple = x² bag, blue = x bag, orange = plain numbers", C.GREY, 14)
    pg.eq(L + 20, y_ + 62, r"=\color{cpur}(5-2)x^2\color{ink}+\color{cblu}(3-1)x\color{ink}+\color{corg}(7+1)", 19)
    pg.eq(L + 330, y_ + 62, r"=3x^2+2x+8", 20, C.GREEN)
    ch.check(5 * x ** 2 + 3 * x - 2 * x ** 2 + 7 - x + 1, 3 * x ** 2 + 2 * x + 8)
    f.p("Test with $x = 1$: the original gives $5 + 3 - 2 + 7 - 1 + 1 = 13$; the answer gives "
        "$3 + 2 + 8 = 13$ ✓.", 13.5, C.GREEN)


def tags(ch):
    f = flow(ch)
    sec(f, "The minus sign is a luggage tag", room=360)
    f.p("When you sort terms, each one carries the sign {B:in front of it}, like a luggage tag tied "
        "to a suitcase. Move the suitcase and the tag comes too. Simplify $4x - 3y - x + 5y$:", 14, gap=8)
    y_ = f.reserve(168)
    pg = f.pg
    row1 = [("+", "4x", C.BLUE), ("−", "3y", C.GREEN), ("−", "x", C.BLUE), ("+", "5y", C.GREEN)]
    for i, (sg, body, col) in enumerate(row1):
        card(pg, L + 40 + i * 110, y_ + 26, sg, body, col, w=70)
    pg.note(L + 40, y_ - 4, "the first term has an invisible + tag", C.GREY, 14)
    order = [0, 2, 1, 3]
    for k, i in enumerate(order):
        sg, body, col = row1[i]
        card(pg, L + 40 + k * 110, y_ + 106, sg, body, col, w=70)
        pg.arrow(L + 75 + i * 110, y_ + 62, L + 75 + k * 110, y_ + 84, C.GREY, 0.9, head=4)
    pg.note(L + 40, y_ + 142, "x's together, y's together; tags travel with their terms", C.PURPLE, 14)
    step(f, r"4x-x-3y+5y", "rearranged, tags attached", size=19)
    step(f, r"=3x+2y", "4 − 1 = 3 x's;  −3 + 5 = +2 y's", size=19, color=C.GREEN)
    ch.check(4 * x - 3 * y - x + 5 * y, 3 * x + 2 * y)
    f.p("{R:Classic slip:} reading $-3y + 5y$ as $-8y$ by \"adding the 3 and 5\". Use the lift from "
        "Chapter 1: start 3 floors down, go up 5 → floor 2.", 13.5)


def multiplying(ch):
    f = flow(ch)
    sec(f, "Multiplying terms is different from adding them", room=420)
    f.p("To {B:multiply} terms you don't need like terms at all. Multiply the numbers, then the "
        "letters (using the power law $x \\times x = x^2$ from Chapter 9):", 14, gap=8)
    step(f, r"3x\times2x=(3\times2)(x\times x)=6x^2", "numbers × numbers, letters × letters", size=19)
    step(f, r"2a\times5b=10ab", "different letters just sit side by side", size=19)
    step(f, r"-4x\times3x^2=-12x^3", "negative × positive = negative; x¹ × x² = x³", size=19)
    ch.check(3 * x * 2 * x, 6 * x ** 2)
    ch.check(-4 * x * 3 * x ** 2, -12 * x ** 3)
    f.p("{b:Your Lecture 2 \"common mistakes\" slide}, each caught by testing $x = 3$, $y = 2$:",
        14, gap=6)
    rows = [(r"2x+x\ne2x^2", "6 + 3 = 9, but 2 × 9 = 18", r"2x+x=3x"),
            (r"2x\times x\ne3x", "6 × 3 = 18, but 3 × 3 = 9", r"2x\times x=2x^2"),
            (r"2x+2y\ne2xy", "6 + 4 = 10, but 2 × 6 = 12", r"\text{stays }2x+2y"),
            (r"2x+2x^2\ne4x^2", "6 + 18 = 24, but 36", r"\text{stays }2x+2x^2")]
    for wrong, test, right in rows:
        y_ = f.reserve(34)
        pg = f.pg
        pg.eq(L + 10, y_ + 2, wrong, 17, C.RED)
        pg.text(L + 160, y_ + 4, test, 12, C.INK)
        pg.eq(L + 360, y_ + 2, right, 17, C.GREEN)
    f.p("{h:The pattern:} adding needs like terms and keeps the power; multiplying works on anything "
        "and adds the powers.", 13.5, C.BROWN)


def single(ch):
    f = flow(ch)
    sec(f, "Expanding one bracket: everything inside gets multiplied", room=440)
    f.p("$3(x + 4)$ means three bags, each holding $x$ and 4. Tip them all out: three x's and three "
        "4s. So $3(x + 4) = 3x + 12$.", 14, gap=8)
    y_ = f.reserve(70)
    pg = f.pg
    for i in range(3):
        bag(pg, L + 20 + i * 80, y_ + 10, 66, 44, C.BLUE)
        pg.eq(L + 53 + i * 80, y_ + 32, r"x\ \ 4", 16, C.BLUE, align="center", valign="middle")
    pg.eq(L + 270, y_ + 20, r"=3x+12", 22, C.GREEN)
    ch.check(sp.expand(3 * (x + 4)), 3 * x + 12)
    f.p("The {B:grid method} does the same thing and works for everything that follows. The "
        "outside goes down the side, the inside across the top; fill each box by multiplying:",
        14, gap=8)
    y_ = f.reserve(106)
    pg = f.pg
    grid(pg, L + 20, y_, [r"3"], [r"x", r"+4"], [[r"3x", r"+12"]])
    grid(pg, L + 270, y_, [r"-2"], [r"x", r"-5"], [[r"-2x", r"+10"]], colors={(0, 1): C.RED})
    pg.note(L + 20, y_ + 80, "3(x + 4) = 3x + 12", C.GREEN, 15)
    pg.note(L + 270, y_ + 80, "−2 × −5 = +10  (tags multiply!)", C.RED, 15)
    ch.check(sp.expand(-2 * (x - 5)), -2 * x + 10)
    f.p("Letters outside work the same: $x(x + 3) = x^2 + 3x$.", 14, gap=8)
    f.p("{b:Expand then collect.} $3(x + 2) - 2(x - 1)$. The $-2$ (with its minus tag) multiplies "
        "{B:both} things in its bracket:", 14, gap=6)
    step(f, r"3(x+2)-2(x-1)", "", size=19)
    step(f, r"=3x+6-2x+2", "−2 × x = −2x;  −2 × −1 = +2", size=19)
    step(f, r"=x+8", "collect: 3x − 2x = x;  6 + 2 = 8", size=19, color=C.GREEN)
    ch.check(sp.expand(3 * (x + 2) - 2 * (x - 1)), x + 8)


def double(ch):
    f = flow(ch)
    sec(f, "Two brackets: the grid is a rectangle's area", room=480)
    f.p("Your slides start with numbers: $(2 + 3)(4 + 5) = 5 \\times 9 = 45$. The long way, "
        "multiplying {B:everything in the first bracket by everything in the second}:", 14, gap=6)
    step(f, r"2\times4+2\times5+3\times4+3\times5=8+10+12+15=45", "same answer ✓", size=18)
    ch.check(8 + 10 + 12 + 15, 45)
    f.p("Why does that work? Draw a rectangle $2 + 3$ tall and $4 + 5$ wide and cut it into four "
        "pieces. Now do the same with letters: $(x + 3)(x + 2)$:", 14, gap=8)
    y_ = f.reserve(170)
    pg = f.pg
    X0, Y0, u = L + 30, y_ + 20, 24
    wx, w2, hx, h3 = 4 * u, 2 * u, 4 * u, 1.5 * u
    pieces = [(X0, Y0, wx, hx, C.PURPLE, r"x^2"), (X0 + wx, Y0, w2, hx, C.BLUE, r"2x"),
              (X0, Y0 + hx, wx, h3, C.BLUE, r"3x"), (X0 + wx, Y0 + hx, w2, h3, C.ORANGE, r"6")]
    for px, py, pw, ph, col, lab in pieces:
        pg.rect(px, py, pw, ph, col, 1.2, fillcolor=C.LIGHT[col])
        pg.eq(px + pw / 2, py + ph / 2, lab, 17, col, align="center", valign="middle")
    pg.text(X0 + wx / 2, Y0 - 16, "x", 13, C.ORANGE, F.ITALIC, align="center")
    pg.text(X0 + wx + w2 / 2, Y0 - 16, "2", 13, C.ORANGE, F.BOLD, align="center")
    pg.text(X0 - 14, Y0 + hx / 2 - 7, "x", 13, C.GREEN, F.ITALIC)
    pg.text(X0 - 14, Y0 + hx + h3 / 2 - 7, "3", 13, C.GREEN, F.BOLD)
    grid(pg, L + 230, y_ + 20, [r"x", r"+3"], [r"x", r"+2"], [[r"x^2", r"+2x"], [r"+3x", r"+6"]],
         colors={(0, 0): C.PURPLE, (0, 1): C.BLUE, (1, 0): C.BLUE, (1, 1): C.ORANGE})
    pg.note(L + 230, y_ + 144, "the grid is the rectangle, tidied", C.GREY, 14)
    step(f, r"(x+3)(x+2)=x^2+2x+3x+6=x^2+5x+6", "collect the two blue x-terms", size=18, color=C.GREEN)
    ch.check(sp.expand((x + 3) * (x + 2)), x ** 2 + 5 * x + 6)
    f.p("{G:Test} $x = 1$: $(4)(3) = 12$ and $1 + 5 + 6 = 12$ ✓.  {b:With a minus:} "
        "$(x + 4)(x - 3)$: the grid gives $x^2 - 3x + 4x - 12 = x^2 + x - 12$ (the $-3$ tag makes "
        "its row of boxes negative).", 14)
    ch.check(sp.expand((x + 4) * (x - 3)), x ** 2 + x - 12)


def squares(ch):
    f = flow(ch)
    sec(f, "Perfect squares: the two missing rectangles", room=460)
    f.p("A very common mistake is $(a + b)^2 = a^2 + b^2$. The picture shows why it's wrong. A "
        "square of side $a + b$ has {B:four} pieces, not two:", 14, gap=8)
    y_ = f.reserve(150)
    pg = f.pg
    X0, Y0, A, B = L + 40, y_ + 10, 90, 40
    for px, py, pw, ph, col, lab in [(X0, Y0, A, A, C.PURPLE, r"a^2"), (X0 + A, Y0, B, A, C.BLUE, r"ab"),
                                     (X0, Y0 + A, A, B, C.BLUE, r"ab"), (X0 + A, Y0 + A, B, B, C.ORANGE, r"b^2")]:
        pg.rect(px, py, pw, ph, col, 1.3, fillcolor=C.LIGHT[col])
        pg.eq(px + pw / 2, py + ph / 2, lab, 16, col, align="center", valign="middle")
    pg.note(L + 200, y_ + 10, "a² + b² only counts the purple and orange\nsquares. The two blue "
            "rectangles are\nforgotten, and together they're 2ab.", C.RED, 15)
    pg.eq(L + 200, y_ + 80, r"(a+b)^2=a^2+2ab+b^2", 21, C.GREEN)
    pg.eq(L + 200, y_ + 116, r"(a-b)^2=a^2-2ab+b^2", 21, C.GREEN)
    ch.check(sp.expand((a + b) ** 2), a ** 2 + 2 * a * b + b ** 2)
    ch.check(sp.expand((a - b) ** 2), a ** 2 - 2 * a * b + b ** 2)
    ch.formula(r"(a+b)^2=a^2+2ab+b^2", "perfect square")
    ch.formula(r"(a-b)^2=a^2-2ab+b^2", "perfect square (minus)")
    f.p("{b:Using it (Lecture 2 example):} expand $(2x - 3y)^2$. Replace $a$ by $2x$ and $b$ by "
        "$3y$, in brackets, exactly like substitution:", 14, gap=6)
    step(f, r"(2x)^2-2(2x)(3y)+(3y)^2", "a → 2x,  b → 3y", size=19)
    step(f, r"=4x^2-12xy+9y^2", "(2x)² = 4x²,  2 × 2 × 3 = 12,  (3y)² = 9y²", size=19, color=C.GREEN)
    ch.check(sp.expand((2 * x - 3 * y) ** 2), 4 * x ** 2 - 12 * x * y + 9 * y ** 2)
    f.p("{b:Difference of two squares.} $(a - b)(a + b)$: the grid gives $a^2 + ab - ab - b^2$. The "
        "middle terms {B:cancel each other}, leaving $a^2 - b^2$. Chapter 12 runs this backwards.", 14)
    ch.check(sp.expand((a - b) * (a + b)), a ** 2 - b ** 2)
    ch.formula(r"(a-b)(a+b)=a^2-b^2", "difference of two squares")


def three(ch):
    f = flow(ch)
    sec(f, "Three brackets, and catching a slide mistake", room=460)
    f.p("$(x + 1)^3 = (x + 1)(x + 1)(x + 1)$. Do it in two stages: first two brackets, then multiply "
        "the result by the last one with a bigger grid:", 14, gap=6)
    step(f, r"(x+1)(x+1)=x^2+2x+1", "stage 1: a perfect square", size=19)
    y_ = f.reserve(110)
    pg = f.pg
    grid(pg, L + 20, y_, [r"x", r"+1"], [r"x^2", r"+2x", r"+1"],
         [[r"x^3", r"+2x^2", r"+x"], [r"+x^2", r"+2x", r"+1"]], cw=70, ch_=36,
         colors={(0, 0): C.PURPLE, (0, 1): C.BLUE, (1, 0): C.BLUE, (0, 2): C.GREEN, (1, 1): C.GREEN, (1, 2): C.ORANGE})
    pg.note(L + 280, y_ + 6, "stage 2: (x + 1) × (x² + 2x + 1)\nsame colours = like terms", C.GREY, 15)
    step(f, r"(x+1)^3=x^3+3x^2+3x+1", "collect: 2x² + x² = 3x²,  x + 2x = 3x", size=19, color=C.GREEN)
    ch.check(sp.expand((x + 1) ** 3), x ** 3 + 3 * x ** 2 + 3 * x + 1)
    f.p("{R:Slide check.} Lecture 2 writes $(x+1)^3 = x^3 + 4x^2 + 3x + 1$. Test with $x = 1$: the "
        "left side is $2^3 = 8$. The slide's version gives $1 + 4 + 3 + 1 = 9$ ✗, ours gives "
        "$1 + 3 + 3 + 1 = 8$ ✓. (The slide's own working has $2x^2 + x^2 + x^2$, one $x^2$ too many.)",
        13.5, gap=8)
    f.p("{R:The \"MASSIVE example\"} $(x + 4)(x + 3)(x + 2)(x + 1)$: the slide ends with $44x^2$. With "
        "$x = 1$ the left side is $5 \\times 4 \\times 3 \\times 2 = 120$, but $1 + 10 + 44 + 50 + 24 = "
        "129$ ✗. The correct answer is $x^4 + 10x^3 + 35x^2 + 50x + 24$ (it sums to 120 ✓). On the "
        "slide, one \"$12x^2$\" was copied as \"$21x^2$\".", 13.5, gap=8)
    ch.check(sp.expand((x + 4) * (x + 3) * (x + 2) * (x + 1)), x ** 4 + 10 * x ** 3 + 35 * x ** 2 + 50 * x + 24)
    f.p("{h:The lesson:} putting $x = 1$ in both sides takes ten seconds and catches almost every "
        "expanding mistake, including your lecturer's.", 13.5, C.BROWN)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Shopping bags: your turn", fresh=True)
    f.p("Answers in grey. Test each answer with x = 1 or x = 2!", 13.5, gap=10)
    groups = [
        ("Collect like terms", ["5a + 3b − 2a + b", "4x² − x + 3x² + 5x − 2", "7p − 3q − 9p + q"],
         "1. 3a + 4b   2. 7x² + 4x − 2   3. −2p − 2q"),
        ("Multiply", ["4x × 3y", "−2a × 5a", "3x² × 2x³"], "4. 12xy   5. −10a²   6. 6x⁵"),
        ("One bracket", ["5(2x − 3)", "−3(x − 4)", "x(2x + 7)", "2(x + 5) − 3(x − 1)"],
         "7. 10x − 15   8. −3x + 12   9. 2x² + 7x   10. −x + 13"),
        ("Two brackets", ["(x + 5)(x + 2)", "(x − 3)(x + 7)", "(2x + 1)(x − 4)", "(x − 6)²", "(3x + 2)(3x − 2)"],
         "11. x² + 7x + 10   12. x² + 4x − 21   13. 2x² − 7x − 4   14. x² − 12x + 36   15. 9x² − 4"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    p, q = sp.symbols("p q")
    E = sp.expand
    for g, e in [(5 * a + 3 * b - 2 * a + b, 3 * a + 4 * b), (4 * x ** 2 - x + 3 * x ** 2 + 5 * x - 2, 7 * x ** 2 + 4 * x - 2),
                 (7 * p - 3 * q - 9 * p + q, -2 * p - 2 * q), (E(2 * (x + 5) - 3 * (x - 1)), -x + 13),
                 (E((x - 3) * (x + 7)), x ** 2 + 4 * x - 21), (E((2 * x + 1) * (x - 4)), 2 * x ** 2 - 7 * x - 4),
                 (E((x - 6) ** 2), x ** 2 - 12 * x + 36), (E((3 * x + 2) * (3 * x - 2)), 9 * x ** 2 - 4)]:
        ch.check(g, e)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    like_terms(ch)
    tags(ch)
    multiplying(ch)
    single(ch)
    double(ch)
    squares(ch)
    three(ch)
    your_turn(ch)
