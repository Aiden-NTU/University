"""Chapter 12 - Factorisation. Un-baking: reading the recipe back off the cake. Common factors as shared
'atoms', then ONE formula for every quadratic: the grid formula (x + n/a)(ax + m), with the pair
m, n = (b ± √Δ)/2 and Δ = b² − 4ac, shown on one card and one worked example. Short patterns for two
terms (difference of squares, cut and slide), four terms (grouping) and cubes (a 2-by-3 grid)."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, go, section, step, title_block

ORDER = 12
NUM = 12
TITLE = "Factorisation"
SHORT = "Factorisation"
SLUG = "Factorisation"
ACCENT = C.PURPLE
REQUIRES = ["factors", "hcf", "expand-brackets", "double-brackets", "like-terms", "multiply-terms",
            "powers", "negative-numbers", "area", "substitution", "perfect-squares",
            "difference-of-squares-expansion"]
INTRODUCES = ["factorise", "factorise-common-factor", "factorise-quadratic", "split-the-middle",
              "factorise-by-grouping", "difference-of-two-squares", "sum-difference-cubes"]

PAPER = "#fdfbff"
x, y, a, b, q, w_ = sp.symbols("x y a b q w")


def icon(pg, x0, y0):
    pg.rect(x0 + 1, y0 + 3, 11, 11, C.PURPLE, 1.1, fillcolor=C.LIGHT[C.PURPLE])
    pg.rect(x0 + 13, y0 + 3, 4, 11, C.BLUE, 1.0, fillcolor=C.LIGHT[C.BLUE])


def sec(f, t, **kw):
    section(f, t, C.PURPLE, icon, **kw)


def chip(pg, x0, y0, s, col, hl=False, size=16):
    """One 'atom' of a term: a number or a letter on a little tile."""
    w_, h_, _ = pg.eq_size(s, size)
    bw = max(26, w_ + 12)
    pg.rect(x0, y0, bw, 28, col, 1.1, fillcolor=C.HL["y"] if hl else "#ffffff", r=5)
    pg.eq(x0 + bw / 2, y0 + 14, s, size, col, align="center", valign="middle")
    return bw








def box(pg, x0, y0, w_, h_, s, col, size=12.5):
    pg.rect(x0, y0, w_, h_, col, 1.3, fillcolor=C.LIGHT[col], r=7)
    th = pg.rich_h(s, w_ - 14, size)
    pg.rich(x0 + 7, y0 + (h_ - th) / 2, s, w_ - 14, size, align="center")


NEWFILL = "#fff1a8"


def fgrid(pg, x0, y0, cells, left, top, cw=56, rh=32, hh=26, hw=38, size=13, new=(), good=(), bad=(),
          cols=None):
    """Factorising grid. cells[i][j], left[i], top[j] are LaTeX ('' = still empty). Keys for new / good /
    bad highlighting: 'A' 'B' 'C' 'D' (cells, reading order), 'S1' 'S2' (side edges), 'T1' 'T2' (top)."""
    def fill(k, base):
        return (C.LIGHT[C.RED] if k in bad else C.LIGHT[C.GREEN] if k in good else NEWFILL if k in new
                else base)
    pg.rect(x0, y0, hw, hh, C.GREY, 0.8, fillcolor="#f1f3f6")
    pg.eq(x0 + hw / 2, y0 + hh / 2, r"\times", 12, C.GREY, align="center", valign="middle")
    for j in range(2):
        xx = x0 + hw + j * cw
        pg.rect(xx, y0, cw, hh, C.ORANGE, 1, fillcolor=fill(f"T{j + 1}", C.LIGHT[C.ORANGE]))
        if top[j]:
            pg.eq(xx + cw / 2, y0 + hh / 2, top[j], size, C.ORANGE, align="center", valign="middle")
    for i in range(2):
        yy = y0 + hh + i * rh
        pg.rect(x0, yy, hw, rh, C.GREEN, 1, fillcolor=fill(f"S{i + 1}", C.LIGHT[C.GREEN]))
        if left[i]:
            pg.eq(x0 + hw / 2, yy + rh / 2, left[i], size, C.GREEN, align="center", valign="middle")
        for j in range(2):
            k = "ABCD"[2 * i + j]
            xx = x0 + hw + j * cw
            pg.rect(xx, yy, cw, rh, C.INK, 1, fillcolor=fill(k, "#ffffff"))
            if cells[i][j]:
                pg.eq(xx + cw / 2, yy + rh / 2, cells[i][j], size, (cols or {}).get(k, C.INK), align="center",
                      valign="middle")
    return hw + 2 * cw, hh + 2 * rh


def grid23(pg, x0, y0, cells, left, top, cols, cw=56, rh=34, hh=28, hw=42, size=14):
    """A 2-row by 3-column multiplying grid; cols maps (row, col) to a colour for that box."""
    pg.rect(x0, y0, hw, hh, C.GREY, 0.8, fillcolor="#f1f3f6")
    pg.eq(x0 + hw / 2, y0 + hh / 2, r"\times", 12, C.GREY, align="center", valign="middle")
    for j in range(3):
        xx = x0 + hw + j * cw
        pg.rect(xx, y0, cw, hh, C.ORANGE, 1, fillcolor=C.LIGHT[C.ORANGE])
        pg.eq(xx + cw / 2, y0 + hh / 2, top[j], size, C.ORANGE, align="center", valign="middle")
    for i in range(2):
        yy = y0 + hh + i * rh
        pg.rect(x0, yy, hw, rh, C.GREEN, 1, fillcolor=C.LIGHT[C.GREEN])
        pg.eq(x0 + hw / 2, yy + rh / 2, left[i], size, C.GREEN, align="center", valign="middle")
        for j in range(3):
            xx = x0 + hw + j * cw
            col = cols.get((i, j), C.INK)
            pg.rect(xx, yy, cw, rh, C.INK, 1, fillcolor="#ffffff" if col == C.INK else C.LIGHT[col])
            pg.eq(xx + cw / 2, yy + rh / 2, cells[i][j], size, col, align="center", valign="middle")
    return hw + 3 * cw, hh + 2 * rh




def pair_of(a_, b_, c_):
    """The pair from the formula, (b ± √Δ)/2, as exact numbers."""
    D = b_ * b_ - 4 * a_ * c_
    return sp.nsimplify((b_ + sp.sqrt(D)) / 2), sp.nsimplify((b_ - sp.sqrt(D)) / 2)




# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 12, "Factorisation", "un-baking: reading the recipe back off the cake",
                     C.PURPLE, PAPER)
    # cake
    cx, cy = L + 110, 250
    pg.rect(cx - 80, cy, 160, 34, C.BROWN, 1.3, fillcolor="#f3d6b0", r=4)
    pg.rect(cx - 64, cy - 30, 128, 30, C.BROWN, 1.3, fillcolor="#f8e3c8", r=4)
    pg.line(cx, cy - 30, cx, cy - 48, C.RED, 2)
    pg.ellipse(cx, cy - 53, 3, 5, C.ORANGE, 1, fillcolor=C.YELLOW)
    pg.eq(cx, cy + 17, r"3x^2+6x", 18, C.BROWN, align="center", valign="middle")
    # recipe card
    rx, ry = L + 320, 214
    pg.rect(rx, ry, 150, 80, C.PURPLE, 1.3, fillcolor="#ffffff", r=6)
    pg.text(rx + 10, ry + 6, "RECIPE", 11, C.PURPLE, F.BOLD)
    pg.eq(rx + 75, ry + 48, r"3x\,(x+2)", 20, C.PURPLE, align="center", valign="middle")
    pg.arrow(rx - 10, ry + 22, cx + 92, ry + 22, C.GREEN, 1.4, bend=-0.2)
    pg.note(cx + 110, ry - 14, "expand = bake", C.GREEN, 16)
    pg.arrow(cx + 92, ry + 64, rx - 10, ry + 64, C.PURPLE, 1.4, bend=-0.2)
    pg.note(cx + 104, ry + 76, "factorise = un-bake", C.PURPLE, 16)
    f = ch.flow(top=350)
    f.p("In Chapter 11 you {B:expanded}: brackets in, long expression out. {B:Factorising} is the same "
        "trip backwards. You're handed the long expression (the cake) and asked for the brackets "
        "that made it (the recipe).", 14, gap=10)
    f.p("It's harder in this direction, the way un-baking is harder than baking. But there is {B:one method "
        "for every three-term expression}: one number, $\\Delta$, tells you whether brackets exist, one "
        "formula gives the numbers that go in them, and a grid puts them together. The other shapes (two "
        "terms, four terms, cubes) get one short pattern each, and a map at the end says which to use. Every "
        "answer can be checked by baking it again: expand it and see if you get back where you started.",
        14, gap=10)
    f.p("{y:Goes with} {B:Lecture 2} {y:(factorising, difference of two squares, perfect squares, cubes).}",
        12.5)


def what_is(ch):
    f = flow(ch)
    sec(f, "What \"factor\" means (numbers first)")
    f.p("A {B:factor} is something you multiply by. $12 = 3 \\times 4$, so 3 and 4 are factors of 12 "
        "(Chapter 1). {B:Factorising} means rewriting something {B:as a multiplication}.", 14, gap=8)
    ch.term("factorise", "rewrite an expression as a product (things multiplied together); the reverse of expanding")
    f.p("Try it with a sum of numbers: $6 + 9$. Both numbers are in the 3 times table:", 14, gap=6)
    step(f, r"6+9=3\times2+3\times3", "split each into 3 × something", size=19)
    step(f, r"=3\times(2+3)", "the 3 is shared, so pull it out front", size=19)
    step(f, r"=3\times5=15", "same as 6 + 9 ✓", size=19, color=C.GREEN)
    ch.check(3 * (2 + 3), 6 + 9)
    f.p("That's all factorising is: spot what every term {B:shares}, write it once outside a bracket, "
        "and put what's {B:left over} inside. Your slides do the same with fractions:", 14, gap=6)
    step(f, r"\frac27+\frac29=2\left(\frac17+\frac19\right)", "each term is 2 × something", size=19)
    ch.check(sp.Rational(2, 7) + sp.Rational(2, 9), 2 * (sp.Rational(1, 7) + sp.Rational(1, 9)))


def atoms(ch):
    f = flow(ch)
    sec(f, "Common factors: break every term into atoms", room=420)
    f.p("Lecture 2 example: $3x^2 + 6x$. Break each term into the smallest things multiplied together "
        "(its \"atoms\"). Numbers split into primes, and $x^2$ splits into $x \\times x$:", 14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    rows = [(r"3x^2", [("3", 1), ("x", 1), ("x", 0)]), (r"6x", [("2", 0), ("3", 1), ("x", 1)])]
    for i, (term, parts) in enumerate(rows):
        yy = y_ + i * 44
        pg.eq(L + 60, yy + 14, term, 20, C.PURPLE, align="right", valign="middle")
        pg.text(L + 70, yy + 5, "=", 14)
        xx = L + 90
        for s, shared in parts:
            xx += chip(pg, xx, yy, s, C.BLUE if s == "x" else C.ORANGE, hl=bool(shared)) + 4
            if (s, shared) != parts[-1]:
                pg.text(xx - 1, yy + 6, "×", 12, C.GREY)
                xx += 12
    pg.note(L + 290, y_ + 4, "highlighted = in BOTH rows\n(3 and x)", C.BROWN, 16)
    pg.note(L + 20, y_ + 96, "shared atoms go outside:  3 × x = 3x.   left over: x (top row) and 2 "
            "(bottom row)", C.PURPLE, 16, w=W - 20)
    step(f, r"3x^2+6x=3x\,(x+2)", "outside: shared;  inside: leftovers", size=21, color=C.GREEN)
    ch.check(sp.expand(3 * x * (x + 2)), 3 * x ** 2 + 6 * x)
    f.p("{G:Bake it again to check:} $3x \\times x = 3x^2$ and $3x \\times 2 = 6x$ ✓. And with a number, "
        "$x = 2$: $12 + 12 = 24$ and $6 \\times 4 = 24$ ✓.", 13.5, gap=10)
    f.p("{b:Take out the biggest shared thing.} $3x^2 + 6x = 3(x^2 + 2x)$ is true, but the bracket "
        "still has a shared $x$ inside, so you're not finished. Keep going until the terms in the "
        "bracket share nothing.", 14, gap=8)
    f.p("{b:Three terms, same idea} (your slides): $3x + 4qx + 12wx$. Every term has an $x$ atom; the "
        "numbers 3, 4, 12 share nothing (4 isn't a multiple of 3). So only $x$ comes out:", 14, gap=6)
    step(f, r"3x+4qx+12wx=x\,(3+4q+12w)", "x × 3, x × 4q, x × 12w", size=19)
    ch.check(sp.expand(x * (3 + 4 * q + 12 * w_)), 3 * x + 4 * q * x + 12 * w_ * x)
    ch.term("common factor", "something that divides every term; taking it out means writing it once outside a bracket")
    f.p("{b:Why bother?} Lecture 2 asks you to make $x$ the subject of $3x + xy = z$. The $x$ is stuck in two "
        "places; taking it out glues the two copies into one, and then one division finishes the job:",
        14, gap=6)
    step(f, r"3x+xy=z\ \Rightarrow\ x\,(3+y)=z\ \Rightarrow\ x=\frac{z}{3+y}", "one x, then divide", size=19,
         color=C.GREEN)
    xs, ys, zs = sp.symbols("x y z")
    ch.check(sp.solve(sp.Eq(3 * xs + xs * ys, zs), xs), [zs / (ys + 3)])


CARD_COLS = {"A": C.PURPLE, "B": C.BLUE, "C": C.BLUE, "D": C.ORANGE}


def grid_formula(ch):
    f = flow(ch)
    sec(f, "Three terms: the grid formula", fresh=True)
    f.p("Chapter 11 filled a grid from its edges. Factorising $ax^2 + bx + c$ runs it {B:backwards}: the boxes "
        "are the question, the edges are the answer, and the edges have a formula:", 14, gap=8)
    y_ = f.reserve(188)
    pg = f.pg
    pg.rect(L, y_, W, 180, C.PURPLE, 1.6, fillcolor=C.LIGHT[C.PURPLE], r=8)
    pg.text(L + 12, y_ + 8, "THE GRID FORMULA  for  ax² + bx + c", 11.5, C.PURPLE, F.BOLD)
    gx, gy = L + 16, y_ + 36
    fgrid(pg, gx, gy, [[r"ax^2", r"m\,x"], [r"n\,x", r"c"]], [r"x", r"+\frac{n}{a}"], [r"ax", r"+m"],
          cw=80, rh=44, hh=34, hw=56, size=16, cols=CARD_COLS)
    pg.rich(gx, gy + 34 + 88 + 6, "box = side edge × top edge", 216, 11.5)
    tx = gx + 56 + 160 + 30
    pg.eq(tx, y_ + 34, r"\text{1.}\ \ \Delta=b^2-4ac", 16)
    pg.eq(tx, y_ + 70, r"\text{2.}\ \ m,\,n=\frac{b\pm\sqrt\Delta}{2}", 16, C.BLUE)
    pg.eq(tx, y_ + 128, r"\text{3.}\ \ \left(x+\frac na\right)(ax+m)", 16, C.GREEN)
    ch.formula(r"m,\,n=\frac{b\pm\sqrt{b^2-4ac}}{2}", "the pair for factorising ax² + bx + c")
    ch.formula(r"ax^2+bx+c=\left(x+\frac na\right)(ax+m)", "the grid formula (m, n the pair)")
    f.p("$\\Delta$ is the Greek D, \"delta\". The two numbers $m$ and $n$ are {B:the pair}. (Take out any "
        "common factor first.)", 13.5, gap=10)

    f.p("{b:Worked example:} $2x^2 + 7x + 3$. Read off the letters: $a = 2$, $b = 7$, $c = 3$.", 14, gap=6)
    step(f, r"\Delta=7^2-4\times2\times3=49-24=25", "1. 25 = 5²", size=18)
    step(f, r"m=\frac{7+5}{2}=6,\qquad n=\frac{7-5}{2}=1", "2. the pair", size=18, color=C.BLUE)
    ch.check(pair_of(2, 7, 3), (6, 1))
    f.p("{b:3. Put the numbers into the grid}, in the places the letters were:", 14, gap=6)
    y_ = f.reserve(132)
    pg = f.pg
    fgrid(pg, L + 16, y_, [[r"2x^2", r"+6x"], [r"+x", r"+3"]], [r"x", r"+\frac12"], [r"2x", r"+6"],
          cw=80, rh=44, hh=34, hw=56, size=16, cols=CARD_COLS)
    tx = L + 16 + 216 + 30
    yy = y_ + 2
    for txt in ["{O:Top edges:} $ax = 2x$ and $m = 6$.",
                "{G:Side edges:} $x$ and $\\frac na = \\frac12$.",
                "{b:Boxes:} $2x \\times x = 2x^2$, then $6x + x = 7x$, then $\\frac12 \\times 6 = 3$. "
                "That's the question ✓"]:
        yy += pg.rich(tx, yy, txt, R - tx, 13) + 6
    ch.check(sp.expand(x * 2 * x + 6 * x + x + sp.Rational(1, 2) * 6), 2 * x ** 2 + 7 * x + 3)
    step(f, r"2x^2+7x+3=\left(x+\tfrac12\right)(2x+6)", "read the edges", size=18)
    step(f, r"=(2x+1)(x+3)", "clear the fraction: × 2 and ÷ 2", size=18, color=C.GREEN)
    ch.check(sp.expand((x + sp.Rational(1, 2)) * (2 * x + 6)), 2 * x ** 2 + 7 * x + 3)
    ch.check(sp.expand((2 * x + 1) * (x + 3)), 2 * x ** 2 + 7 * x + 3)
    f.p("Doubling one bracket and halving the other changes nothing, like $3 \\times 4 = 6 \\times 2$. "
        "{G:Bake it to check:} $(2x + 1)(x + 3) = 2x^2 + 6x + x + 3 = 2x^2 + 7x + 3$ ✓.", 14, gap=8)
    f.p("{b:When $a = 1$} there's no fraction: the answer is just $(x + n)(x + m)$. For $x^2 + 7x + 12$, "
        "$\\Delta = 49 - 48 = 1$ and the pair is $\\frac{7 \\pm 1}{2} = 4, 3$, so it's $(x + 3)(x + 4)$.",
        14, gap=10)
    ch.check(pair_of(1, 7, 12), (4, 3))
    ch.check(sp.expand((x + 3) * (x + 4)), x ** 2 + 7 * x + 12)

    f.need(150)
    go(f, "3x² + 10x + 8. Work out Δ, then the pair, then put them into the grid formula and clear the "
       "fraction.")
    ch.check(pair_of(3, 10, 8), (6, 4))
    ch.check(sp.expand((x + sp.Rational(4, 3)) * (3 * x + 6)), 3 * x ** 2 + 10 * x + 8)
    ch.check(sp.expand((3 * x + 4) * (x + 2)), 3 * x ** 2 + 10 * x + 8)
    f.p("{b:Answer:} $\\Delta = 100 - 96 = 4$, pair $\\frac{10 \\pm 2}{2} = 6, 4$. Top edges $3x$ and $6$, side "
        "edges $x$ and $\\frac43$. So $\\left(x + \\frac43\\right)(3x + 6)$; × 3 and ÷ 3 gives "
        "$(3x + 4)(x + 2)$.", 14)
    ch.term("quadratic", "an expression whose highest power is x², like x² + 4x + 3")
    ch.term("discriminant", "Δ = b² − 4ac for ax² + bx + c. A perfect square: whole-number brackets. Not a "
            "square: square-root brackets. Negative: no brackets (and no solutions)")
    ch.term("grid method (factorising)", "work out Δ = b² − 4ac and the pair m, n = (b ± √Δ)/2; the grid's "
            "edges are then x, n/a on the side and ax, m on top")


def why_works(ch):
    f = flow(ch)
    sec(f, "Why the grid formula always works", room=330)
    f.p("Multiply the card's edges back out, box by box. Every box comes out as the question, whatever "
        "$a$, $b$ and $c$ are:", 14, gap=8)
    step(f, r"x\times ax=ax^2", "top-left ✓", size=18)
    step(f, r"mx+nx=(m+n)\,x=bx", "middle ✓: the √Δ parts cancel", size=18)
    step(f, r"\frac na\times m=\frac{mn}{a}=\frac{ac}{a}=c", "bottom-right ✓ (needs mn = ac)", size=18)
    f.p("And $mn = ac$ is where $\\Delta$ comes in. Multiply the pair; the top is a difference of two squares "
        "(Chapter 11):", 14, gap=6)
    step(f, r"mn=\frac{(b+\sqrt\Delta)(b-\sqrt\Delta)}{4}=\frac{b^2-\Delta}{4}=\frac{4ac}{4}=ac",
         "because Δ = b² − 4ac", size=17)
    A, Bb, Cc = sp.symbols("a b c", positive=True)
    Dl = Bb ** 2 - 4 * A * Cc
    M, N = (Bb + sp.sqrt(Dl)) / 2, (Bb - sp.sqrt(Dl)) / 2
    ch.check(sp.simplify(M + N - Bb), 0)
    ch.check(sp.simplify(sp.expand(M * N) - A * Cc), 0)
    ch.check(sp.simplify(sp.expand((x + N / A) * (A * x + M)) - (A * x ** 2 + Bb * x + Cc)), 0)
    f.p("That's the whole reason $\\Delta$ is $b^2 - 4ac$: it's the number that makes the corner come out as "
        "$c$. Chapter 15 sets each bracket to zero, $x = -\\frac na$ or $x = -\\frac ma$, and that turns into "
        "the quadratic formula.", 14)


def delta_tells(ch):
    f = flow(ch)
    sec(f, "What Δ tells you before you start", room=300)
    f.p("Step 1 sorts every quadratic before you touch the grid:", 14, gap=8)
    rows = [(r"2x^2+7x+3", r"49-24=25", r"5", r"6,\ 1", "a square: whole brackets", C.GREEN),
            (r"x^2+4x+4", r"16-16=0", r"0", r"2,\ 2", "zero: (x + 2) twice", C.GREEN),
            (r"x^2+4x+2", r"16-8=8", r"\sqrt8", r"2\pm\sqrt2", "not a square: square roots", C.ORANGE),
            (r"6x^2+4x+3", r"16-72=-56", r"\text{--}", r"\text{none}", "negative: no brackets", C.RED)]
    y_ = f.reserve(30 + 34 * len(rows))
    pg = f.pg
    cols_x = [L + 4, L + 104, L + 222, L + 280, L + 360]
    for xx, hd in zip(cols_x, ["quadratic", "Δ = b² − 4ac", "√Δ", "pair", ""]):
        pg.text(xx, y_, hd, 12, C.GREY, F.BOLD)
    for k, (q_, dl, sq, pr, verdict, col) in enumerate(rows):
        yy = y_ + 36 + k * 34
        pg.eq(cols_x[0], yy, q_, 14, valign="middle")
        pg.eq(cols_x[1], yy, dl, 14, col, valign="middle")
        pg.eq(cols_x[2], yy, sq, 14, col, valign="middle")
        pg.eq(cols_x[3], yy, pr, 14, col, valign="middle")
        pg.note(cols_x[4], yy - 10, verdict, col, 13, w=R - cols_x[4])
    ch.check([bb * bb - 4 * aa * cc for aa, bb, cc in [(2, 7, 3), (1, 4, 4), (1, 4, 2), (6, 4, 3)]],
             [25, 0, 8, -56])
    ch.check([pair_of(2, 7, 3), pair_of(1, 4, 4)], [(6, 1), (2, 2)])
    ch.check(sp.simplify(pair_of(1, 4, 2)[0] - (2 + sp.sqrt(2))), 0)
    f.p("{b:Not a square:} the grid formula still works; the edges just contain square roots. There are no "
        "whole-number brackets, so the quadratic is called {B:prime} or {B:irreducible}:", 14, gap=6)
    r2 = sp.sqrt(2)
    step(f, r"x^2+4x+2=(x+2-\sqrt2)(x+2+\sqrt2)", "pair 2 ± √2, a = 1", size=18, color=C.ORANGE)
    ch.check(sp.expand((x + 2 - r2) * (x + 2 + r2)), x ** 2 + 4 * x + 2)
    ch.term("prime quadratic", "a quadratic with no whole-number brackets, e.g. x² + 4x + 2 (also called "
            "irreducible); its Δ is not a perfect square")
    f.p("{b:Negative:} no number squared is negative, so $\\sqrt{\\Delta}$ doesn't exist: no pair, {B:no "
        "brackets at all}. You haven't made a mistake; there's nothing to find. Exam questions are picked so "
        "that $\\Delta$ is a perfect square. Chapter 15 shows the three cases as graphs that cross the x-axis "
        "twice, touch it once, or miss it.", 14)
    ch.check(sp.factor(6 * x ** 2 + 4 * x + 3), 6 * x ** 2 + 4 * x + 3)


def minus_signs(ch):
    f = flow(ch)
    sec(f, "Minus signs: keep each sign with its number", room=330)
    f.p("$6x^2 - x - 2$: $a = 6$, $b = -1$, $c = -2$. The same steps:", 14, gap=6)
    step(f, r"\Delta=(-1)^2-4\times6\times(-2)=1+48=49", "1. 49 = 7²", size=17)
    step(f, r"m=\frac{-1+7}{2}=3,\qquad n=\frac{-1-7}{2}=-4", "2. the pair", size=17, color=C.BLUE)
    ch.check(pair_of(6, -1, -2), (3, -4))
    y_ = f.reserve(132)
    pg = f.pg
    fgrid(pg, L + 16, y_, [[r"6x^2", r"+3x"], [r"-4x", r"-2"]], [r"x", r"-\frac23"], [r"6x", r"+3"],
          cw=80, rh=44, hh=34, hw=56, size=16, cols=CARD_COLS)
    tx = L + 16 + 216 + 30
    yy = y_ + 2
    for txt in ["{b:3.} {O:Top:} $6x$ and $+3$. {G:Side:} $x$ and $\\frac na = \\frac{-4}{6} = -\\frac23$.",
                "{b:Boxes:} $3x - 4x = -x$ and $-\\frac23 \\times 3 = -2$ ✓. You never chose a minus sign: "
                "the formula handed it to you."]:
        yy += pg.rich(tx, yy, txt, R - tx, 13) + 6
    step(f, r"6x^2-x-2=\left(x-\tfrac23\right)(6x+3)", "read the edges", size=18)
    step(f, r"=(3x-2)(2x+1)", "clear the fraction: × 3 and ÷ 3", size=18, color=C.GREEN)
    ch.check(sp.expand((x - sp.Rational(2, 3)) * (6 * x + 3)), 6 * x ** 2 - x - 2)
    ch.check(sp.expand((3 * x - 2) * (2 * x + 1)), 6 * x ** 2 - x - 2)
    f.p("{b:Same answer, different look.} $(3x - 2)(2x + 1)$ and $(2x + 1)(3x - 2)$ are the same, like "
        "$3 \\times 4 = 4 \\times 3$. Lecture 2 writes $2x^2 + 5x + 3 = 2(x + 1.5)(x + 1)$ and says it \"isn't "
        "the only solution\": moving the 2 into the first bracket gives $(2x + 3)(x + 1)$, the whole-number "
        "version an examiner expects.", 14, gap=8)
    ch.check(sp.expand(2 * (x + sp.Rational(3, 2)) * (x + 1)), sp.expand((2 * x + 3) * (x + 1)))
    f.p("Lecture 2 also writes the grid's two rows in a line, called {B:split the middle}:", 14, gap=6)
    step(f, r"2x^2+7x+3=(2x^2+6x)+(x+3)", "the grid's two rows", size=17)
    step(f, r"=2x(x+3)+1(x+3)=(2x+1)(x+3)", "each row's side edge, then the shared bracket", size=17)
    ch.check(sp.expand(2 * x * (x + 3) + 1 * (x + 3)), 2 * x ** 2 + 7 * x + 3)
    ch.term("split the middle", "for ax² + bx + c: split bx using the pair (b ± √Δ)/2, then factorise in pairs "
            "(the grid's two rows written in a line)")


def squares(ch):
    f = flow(ch)
    sec(f, "Difference of two squares: cut and slide", room=260)
    f.p("Take a square of paper, $a$ by $a$, and snip a small $b$ by $b$ square off one corner. "
        "What's left has area $a^2 - b^2$. Now watch:", 14, gap=12)
    y_ = f.reserve(190)
    pg = f.pg
    A, B = 100, 40
    # frame 1
    X0, Y0 = L + 10, y_ + 20
    pg.fillpoly([(X0, Y0), (X0 + A, Y0), (X0 + A, Y0 + A - B), (X0 + A - B, Y0 + A - B),
                 (X0 + A - B, Y0 + A), (X0, Y0 + A)], C.LIGHT[C.PURPLE], outline=C.PURPLE, width=1.3)
    pg.rect(X0 + A - B, Y0 + A - B, B, B, C.RED, 1, dash=(3, 3))
    pg.eq(X0 + A - B / 2, Y0 + A - B / 2, r"b^2", 13, C.RED, align="center", valign="middle")
    pg.eq(X0 + (A - B) / 2, Y0 + (A - B) / 2, r"a^2-b^2", 14, C.PURPLE, align="center", valign="middle")
    pg.note(X0, Y0 + A + 8, "1. corner snipped off", C.GREY, 14)
    # frame 2: cut
    X1 = L + 170
    pg.rect(X1, Y0, A, A - B, C.PURPLE, 1.3, fillcolor=C.LIGHT[C.PURPLE])
    pg.rect(X1, Y0 + A - B + 8, A - B, B, C.BLUE, 1.3, fillcolor=C.LIGHT[C.BLUE])
    pg.line(X1 - 8, Y0 + A - B + 4, X1 + A + 8, Y0 + A - B + 4, C.RED, 1, dash=(4, 3))
    pg.note(X1 + A - 4, Y0 + A - B + 12, "cut", C.RED, 14)
    pg.eq(X1 + A / 2, Y0 - 12, r"a", 13, C.GREY, align="center", valign="middle")
    pg.eq(X1 + A + 12, Y0 + (A - B) / 2, r"a-b", 12, C.GREY, valign="middle")
    pg.eq(X1 + (A - B) / 2, Y0 + A - B + 8 + B / 2, r"b", 13, C.BLUE, align="center", valign="middle")
    pg.note(X1, Y0 + A + 8, "2. cut the L in two", C.GREY, 14)
    # frame 3: slide
    X2 = L + 330
    pg.rect(X2, Y0 + 20, A, A - B, C.PURPLE, 1.3, fillcolor=C.LIGHT[C.PURPLE])
    pg.rect(X2 + A, Y0 + 20, B, A - B, C.BLUE, 1.3, fillcolor=C.LIGHT[C.BLUE])
    pg.brace(X2, Y0 + 14, X2 + A + B, Y0 + 14, C.GREEN, 1, 6)
    pg.eq(X2 + (A + B) / 2, Y0 - 14, r"a+b", 14, C.GREEN, align="center", valign="middle")
    pg.eq(X2 + A + B + 8, Y0 + 20 + (A - B) / 2, r"a-b", 14, C.GREEN, valign="middle")
    pg.arc(X2 + A, Y0 + 90, 24, 200, 330, C.BLUE, 1.0, arrow=True)
    pg.note(X2, Y0 + A + 8, "3. stand the strip up\n    and slide it across", C.GREY, 14)
    pg.arrow(X0 + A + 10, Y0 + 50, X1 - 12, Y0 + 50, C.GREY, 1, head=4)
    pg.arrow(X1 + A + 44, Y0 + 50, X2 - 8, Y0 + 50, C.GREY, 1, head=4)
    f.p("Same paper, now a rectangle $(a + b)$ wide and $(a - b)$ tall:", 14, gap=6)
    y_ = f.reserve(56)
    pg = f.pg
    bw = 300
    pg.rect(L + (W - bw) / 2, y_, bw, 46, C.PURPLE, 1.6, fillcolor=C.LIGHT[C.PURPLE], r=8)
    pg.eq(L + W / 2, y_ + 23, r"a^2-b^2=(a-b)(a+b)", 22, align="center", valign="middle")
    ch.check(sp.factor(a ** 2 - b ** 2), (a - b) * (a + b))
    ch.formula(r"a^2-b^2=(a-b)(a+b)", "difference of two squares (factorising)")
    ch.term("difference of two squares", "something squared minus something else squared; it always "
            "factorises as (a − b)(a + b)")
    f.p("{b:How to spot it:} exactly {B:two} terms, a {B:minus} between them, and each term is a "
        "square. Then ask \"a square of what?\"", 14, gap=6)
    step(f, r"x^2-9=x^2-3^2=(x-3)(x+3)", "9 is 3 squared", size=19)
    step(f, r"x^2-4y^2=x^2-(2y)^2=(x-2y)(x+2y)", "4y² is (2y) squared", size=19)
    ch.check(sp.expand((x - 3) * (x + 3)), x ** 2 - 9)
    ch.check(sp.expand((x - 2 * y) * (x + 2 * y)), x ** 2 - 4 * y ** 2)
    f.p("It's also just the method with $b = 0$: for $x^2 - 9$, $\\Delta = 0 + 36 = 36$ and the pair is "
        "$\\pm 3$. Spotting the two squares is simply faster. (The slide says \"Expand: $x^2 - 4y^2$\" but "
        "then factorises it; \"factorise\" is the right word.)", 13.5, gap=8)
    ch.check(pair_of(1, 0, -9), (3, -3))
    f.p("{h:Party trick:} $51 \\times 49 = (50 + 1)(50 - 1) = 50^2 - 1^2 = 2499$, no calculator needed. "
        "{R:Warning:} $a^2 + b^2$ (a {B:plus}) does not factorise this way.", 13.5, C.BROWN)
    ch.check(51 * 49, 2499)


def chunks(ch):
    f = flow(ch)
    sec(f, "More common factors: chunks and pairs", room=250)
    f.p("Lecture 2: $(x + y)^3 + 7(x + y)^2$. It looks frightening, but $(x + y)$ appears whole every "
        "time. Cover it with a box and call it $\\square$:", 14, gap=6)
    step(f, r"\color{cpur}\square\color{ink}^3+7\,\color{cpur}\square\color{ink}^2",
         "□ is just a name for (x + y)", size=21)
    step(f, r"=\color{cpur}\square\color{ink}^2(\color{cpur}\square\color{ink}+7)",
         "atoms: □³ = □ × □ × □;  shared: □²", size=21)
    step(f, r"=(x+y)^2(x+y+7)", "take the box off again", size=20, color=C.GREEN)
    ch.check(sp.expand((x + y) ** 2 * (x + y + 7)), sp.expand((x + y) ** 3 + 7 * (x + y) ** 2))
    f.p("{b:Four terms: group them in pairs.} The slide's example should read "
        "$x^2 + 2y + 2x^3 + 4xy$. Look at the last two terms: $2x^3 + 4xy$ share $2x$.", 14, gap=6)
    step(f, r"(x^2+2y)+(2x^3+4xy)", "two pairs", size=19)
    step(f, r"=(x^2+2y)+2x\,(x^2+2y)", "the second pair: 2x × (x² + 2y)", size=19)
    step(f, r"=(x^2+2y)(1+2x)", "(x² + 2y) is shared; the first pair is 1 × it", size=19, color=C.GREEN)
    ch.check(sp.expand((x ** 2 + 2 * y) * (1 + 2 * x)), x ** 2 + 2 * y + 2 * x ** 3 + 4 * x * y)
    ch.term("factorise by grouping", "split four terms into two pairs, factorise each pair, then take out the "
            "bracket they share")
    f.p("{R:Slide check.} The slide prints $2y^2$ instead of $2y$ and finishes with "
        "$(x^2 + 2y)(x^2 + 2y + 2x)$. Test with $x = y = 1$: the slide's start is $1 + 2 + 2 + 4 = 9$, "
        "but its answer is $3 \\times 5 = 15$ ✗. The version above gives $3 \\times 3 = 9$ ✓.", 13.5)
    ch.check((1 + 2) * (1 + 2 + 2), 15)
    ch.check(1 + 2 + 2 + 4, 9)


def cubes(ch):
    f = flow(ch)
    sec(f, "Cubes: a bigger grid", room=320)
    f.p("Lecture 2 lists two cube patterns. The same grid proves them, with three columns instead of two:",
        14, gap=10)
    y_ = f.reserve(142)
    pg = f.pg
    pairs = {(0, 1): C.BLUE, (1, 0): C.BLUE, (0, 2): C.RED, (1, 1): C.RED, (0, 0): C.GREEN, (1, 2): C.GREEN}
    pg.eq(L + 4, y_, r"(a-b)(a^2+ab+b^2)", 15)
    gw, gh = grid23(pg, L + 4, y_ + 28, [[r"a^3", r"+a^2b", r"+ab^2"], [r"-a^2b", r"-ab^2", r"-b^3"]],
                    [r"a", r"-b"], [r"a^2", r"+ab", r"+b^2"], pairs)
    tx = L + 4 + gw + 26
    pg.rich(tx, y_ + 30, "Same colour, opposite sign: the {B:blue} boxes cancel and the {R:red} boxes cancel. "
            "Only the two {G:green} corners are left: $a^3 - b^3$.", R - tx, 13.5)
    ch.check(sp.expand((a - b) * (a ** 2 + a * b + b ** 2)), a ** 3 - b ** 3)
    step(f, r"a^3-b^3=(a-b)(a^2+ab+b^2)", "a = 2, b = 1:  8 − 1 = 1 × 7", size=19)
    f.p("Swap $b$ for $-b$ everywhere and the same grid gives the plus version:", 14, gap=6)
    step(f, r"a^3+b^3=(a+b)(a^2-ab+b^2)", "a = 2, b = 1:  8 + 1 = 3 × 3", size=19)
    ch.check(sp.expand((a + b) * (a ** 2 - a * b + b ** 2)), a ** 3 + b ** 3)
    ch.check((2 ** 3 - 1, 1 * 7, 2 ** 3 + 1, 3 * 3), (7, 7, 9, 9))
    ch.formula(r"a^3-b^3=(a-b)(a^2+ab+b^2)", "difference of cubes")
    ch.formula(r"a^3+b^3=(a+b)(a^2-ab+b^2)", "sum of cubes")
    f.p("{h:Remembering the signs, \"SOAP\":} the first bracket has the {B:S}ame sign as the question, "
        "the middle of the second bracket is {B:O}pposite, and the last term is {B:A}lways {B:P}ositive.",
        13.5, C.BROWN, gap=8)
    f.p("{b:Using it:} spot two cubes, find $a$ and $b$, and fill in the pattern.", 14, gap=6)
    step(f, r"8x^3-27=(2x)^3-3^3", "8x³ is (2x) cubed, 27 is 3 cubed", size=18)
    step(f, r"=(2x-3)(4x^2+6x+9)", "a = 2x, b = 3 in the minus pattern", size=18, color=C.GREEN)
    ch.check(sp.expand((2 * x - 3) * (4 * x ** 2 + 6 * x + 9)), 8 * x ** 3 - 27)


def which_tool(ch):
    f = flow(ch)
    sec(f, "The map: which tool do I use?", room=470)
    f.p("Start at the top every time. Most questions need two stops: a common factor first, then "
        "one of the others.", 14, gap=12)
    y_ = f.reserve(330)
    pg = f.pg
    cx = L + 150
    box(pg, cx - 110, y_, 220, 44, "{B:1. Anything shared by every term?} Take it out first.", C.PURPLE)
    pg.arrow(cx, y_ + 46, cx, y_ + 68, C.GREY, 1.2, head=5)
    box(pg, cx - 110, y_ + 70, 220, 34, "{B:2. Now count the terms} (inside the bracket)", C.INK)
    ends = [(L + 10, "{B:2 terms}, minus: squares or cubes", "$(a-b)(a+b)$, or SOAP", C.BLUE),
            (L + 175, "{B:3 terms}, $ax^2 + bx + c$", "$\\Delta$, pair, grid", C.GREEN),
            (L + 340, "{B:4 terms}", "group into pairs", C.ORANGE)]
    for xx, s1, s2, col in ends:
        pg.arrow(cx, y_ + 106, xx + 70, y_ + 150, C.GREY, 1.1, head=5)
        box(pg, xx, y_ + 154, 140, 44, s1, col)
        pg.arrow(xx + 70, y_ + 200, xx + 70, y_ + 218, C.GREY, 1.1, head=4)
        box(pg, xx, y_ + 220, 140, 40, s2, col)
    box(pg, L + 60, y_ + 286, 380, 36, "{B:3. Bake it again:} expand your answer, or test with $x = 1$.",
        C.RED)
    pg.note(L + 330, y_ + 10, "same big bracket appearing\nagain and again?\nrename it □ first", C.PURPLE, 15)
    f.p("{R:Three terms?} $\\Delta$ first. A perfect square: the grid formula gives whole brackets. Not a "
        "square: the same formula gives square-root brackets. Negative: stop, there are no brackets. (Two cubes with a {B:plus} still factorise; "
        "two squares with a plus don't.)", 13.5)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Un-baking: your turn", fresh=True)
    f.p("Answers in grey. Bake each answer again (expand it) to check yourself.", 13.5, gap=10)
    groups = [
        ("Common factor", ["4x + 12", "6x² − 9x", "5ab + 10a", "2x³ + 4x² + 8x"],
         "1. 4(x + 3)   2. 3x(2x − 3)   3. 5a(b + 2)   4. 2x(x² + 2x + 4)"),
        ("The method: Δ, pair, grid (show all three)",
         ["x² + 7x + 12", "x² − x − 20", "3x² + 6x − 24", "2x² + 11x + 5", "6x² + 7x + 2", "4x² − 4x − 3",
          "5x² + 13x − 6"],
         "5. Δ = 1, pair 4, 3: (x + 3)(x + 4)   6. Δ = 81, pair 4, −5: (x − 5)(x + 4)   7. take out 3 first; "
         "Δ = 36, pair 4, −2: 3(x + 4)(x − 2)   8. Δ = 81, pair 10, 1: (2x + 1)(x + 5)   9. Δ = 1, pair 4, 3: "
         "(2x + 1)(3x + 2)   10. Δ = 64, pair 2, −6: (2x − 3)(2x + 1)   11. Δ = 289, pair 15, −2: "
         "(5x − 2)(x + 3)"),
        ("Whole, square roots, or nothing? (Δ first)", ["x² + 6x + 8", "x² + 6x + 7", "x² + 2x + 3"],
         "12. Δ = 4 = 2²: pair 4, 2, (x + 2)(x + 4)   13. Δ = 8: pair 3 ± √2, (x + 3 − √2)(x + 3 + √2)   "
         "14. Δ = −8: no brackets"),
        ("Difference of two squares", ["x² − 25", "4x² − 49", "2x² − 18", "97 × 103 (use the trick)"],
         "15. (x − 5)(x + 5)   16. (2x − 7)(2x + 7)   17. 2(x − 3)(x + 3)   18. 100² − 3² = 9991"),
        ("Grouping and chunks", ["ax + ay + bx + by", "(x − 1)² + 3(x − 1)", "Make x the subject: ax − b = cx"],
         "19. (a + b)(x + y)   20. (x − 1)(x + 2)   21. x = b/(a − c)"),
        ("Cubes", ["x³ − 8", "27x³ + 1"],
         "22. (x − 2)(x² + 2x + 4)   23. (3x + 1)(9x² − 3x + 1)"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(90)
        f.text(title, 14, C.PURPLE, F.BOLD, gap=6)
        line = "      ".join(f"{n + k}. {qq}".replace(" ", "\u00a0") for k, qq in enumerate(qs))
        n += len(qs)
        f.text(line, 13, gap=6, x=L + 14, w=W - 14)
        ans = "   ".join(part.strip().replace(" ", "\u00a0") for part in ans.split("   "))
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    E = sp.expand
    c_ = sp.Symbol("c")
    for g, e in [(E(2 * x * (x ** 2 + 2 * x + 4)), 2 * x ** 3 + 4 * x ** 2 + 8 * x),
                 (E(4 * (x + 3)), 4 * x + 12), (E(3 * x * (2 * x - 3)), 6 * x ** 2 - 9 * x),
                 (E(5 * a * (b + 2)), 5 * a * b + 10 * a),
                 (E((x + 3) * (x + 4)), x ** 2 + 7 * x + 12), (E((x - 5) * (x + 4)), x ** 2 - x - 20),
                 (E(3 * (x + 4) * (x - 2)), 3 * x ** 2 + 6 * x - 24), (E((2 * x + 1) * (x + 5)), 2 * x ** 2 + 11 * x + 5),
                 (E((2 * x + 1) * (3 * x + 2)), 6 * x ** 2 + 7 * x + 2), (E((2 * x - 3) * (2 * x + 1)), 4 * x ** 2 - 4 * x - 3),
                 (E((5 * x - 2) * (x + 3)), 5 * x ** 2 + 13 * x - 6),
                 (E((x - 5) * (x + 5)), x ** 2 - 25), (E((2 * x - 7) * (2 * x + 7)), 4 * x ** 2 - 49),
                 (E(2 * (x - 3) * (x + 3)), 2 * x ** 2 - 18), (97 * 103, 9991),
                 (E((a + b) * (x + y)), a * x + a * y + b * x + b * y), (E((x - 1) * (x + 2)), E((x - 1) ** 2 + 3 * (x - 1))),
                 (E((x - 2) * (x ** 2 + 2 * x + 4)), x ** 3 - 8), (E((3 * x + 1) * (9 * x ** 2 - 3 * x + 1)), 27 * x ** 3 + 1)]:
        ch.check(g, e)
    ch.check(sp.solve(sp.Eq(a * x - b, c_ * x), x), [b / (a - c_)])
    ch.check([pair_of(1, 7, 12), pair_of(1, -1, -20), pair_of(1, 2, -8), pair_of(2, 11, 5), pair_of(6, 7, 2),
              pair_of(4, -4, -3), pair_of(5, 13, -6)],
             [(4, 3), (4, -5), (4, -2), (10, 1), (4, 3), (2, -6), (15, -2)])
    ch.check([bb * bb - 4 * aa * cc for aa, bb, cc in [(1, 7, 12), (1, -1, -20), (1, 2, -8), (2, 11, 5), (6, 7, 2),
                                                        (4, -4, -3), (5, 13, -6), (1, 6, 8), (1, 6, 7), (1, 2, 3)]],
             [1, 81, 36, 81, 1, 64, 289, 4, 8, -8])
    r2 = sp.sqrt(2)
    ch.check([E((x + 2) * (x + 4)), E((x + 3 - r2) * (x + 3 + r2)), E((x + 1) ** 2 + 2)],
             [x ** 2 + 6 * x + 8, x ** 2 + 6 * x + 7, x ** 2 + 2 * x + 3])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    what_is(ch)
    atoms(ch)
    chunks(ch)
    grid_formula(ch)
    why_works(ch)
    delta_tells(ch)
    minus_signs(ch)
    squares(ch)
    cubes(ch)
    which_tool(ch)
    your_turn(ch)
