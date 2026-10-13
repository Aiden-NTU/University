"""Chapter 16 - Matrices. A matrix is a shop spreadsheet. Adding is cell by cell, multiplying is
'row meets column' traced with two highlighters, sizes are dominoes whose inner numbers must match,
and the inverse is the undo button that solves simultaneous equations."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, go, section, step, title_block

ORDER = 16
NUM = 16
TITLE = "Matrices"
SHORT = "Matrices"
SLUG = "Matrices"
ACCENT = C.PINK
REQUIRES = ["multiplication", "addition", "negative-numbers", "fraction", "reciprocal", "simultaneous-equations",
            "independent-equations", "substitution-method", "inverse-operations", "variable", "transpose"]
INTRODUCES = ["matrix", "matrix-size", "matrix-entry", "subscript-notation", "matrix-addition",
              "scalar-multiplication", "matrix-multiplication", "identity-matrix", "diagonal-matrix",
              "determinant", "matrix-inverse", "matrix-equation"]

PAPER = "#fffbfd"
M = sp.Matrix


def icon(pg, x0, y0):
    for i in range(3):
        for j in range(3):
            pg.rect(x0 + 1 + j * 5.5, y0 + 1 + i * 5.5, 5, 5, C.PINK, 0.8,
                    fillcolor=C.LIGHT[C.PINK] if i == j else None)


def sec(f, t, **kw):
    section(f, t, C.PINK, icon, **kw)


def mat(pg, x0, y0, rows, cw=34, rh=26, size=15, hrow=None, hcol=None, hcell=None, color=C.INK,
        brackets=True):
    """Draw a matrix as a grid of entries with square brackets. Highlights: hrow (yellow),
    hcol (blue), hcell (green). Returns (w, h)."""
    m, n = len(rows), len(rows[0])
    w, h = n * cw, m * rh
    for i in range(m):
        for j in range(n):
            fc = None
            if hcell == (i, j):
                fc = C.HL["g"]
            elif hrow == i:
                fc = C.HL["y"]
            elif hcol == j:
                fc = C.HL["b"]
            if fc:
                pg.rect(x0 + j * cw + 1, y0 + i * rh + 1, cw - 2, rh - 2, fc, 0.1, fillcolor=fc, layer=C.UNDER)
            pg.eq(x0 + j * cw + cw / 2, y0 + i * rh + rh / 2, str(rows[i][j]), size, color,
                  align="center", valign="middle")
    if brackets:
        for side in (0, 1):
            xx = x0 - 3 if side == 0 else x0 + w + 3
            d = 5 if side == 0 else -5
            pg.poly([(xx + d, y0), (xx, y0), (xx, y0 + h), (xx + d, y0 + h)], color, 1.3)
    return w, h


def domino(pg, x0, y0, a, b, col):
    pg.rect(x0, y0, 64, 30, col, 1.4, fillcolor="#ffffff", r=6)
    pg.line(x0 + 32, y0 + 4, x0 + 32, y0 + 26, col, 1)
    pg.text(x0 + 16, y0 + 6, str(a), 14, col, F.BOLD, align="center")
    pg.text(x0 + 48, y0 + 6, str(b), 14, col, F.BOLD, align="center")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 16, "Matrices", "a spreadsheet you can do sums with", C.PINK, PAPER)
    x0, y0 = L + 90, 230
    heads = ["", "bread", "milk", "eggs"]
    for j, hd in enumerate(heads[1:]):
        pg.text(x0 + j * 60 + 30, y0 - 20, hd, 12, C.GREY, F.BOLD, align="center")
    for i, sh in enumerate(["North shop", "South shop"]):
        pg.text(x0 - 12, y0 + i * 32 + 8, sh, 12, C.GREY, F.BOLD, align="right")
    for i in range(2):
        for j in range(3):
            pg.rect(x0 + j * 60, y0 + i * 32, 60, 32, C.PINK, 0.8, fillcolor="#ffffff")
    mat(pg, x0, y0, [[12, 30, 6], [8, 25, 10]], cw=60, rh=32, size=17, brackets=False)
    pg.arrow(x0 + 190, y0 + 32, x0 + 236, y0 + 32, C.PINK, 1.4)
    pg.eq(x0 + 300, y0 + 32, r"\begin{bmatrix}12&30&6\\8&25&10\end{bmatrix}", 20, C.PINK,
          align="center", valign="middle")
    pg.note(x0 + 200, y0 + 70, "drop the labels, keep the grid", C.PINK, 16)
    f = ch.flow(top=350)
    f.p("A {B:matrix} is a table of numbers in rows and columns, like a spreadsheet with the labels "
        "rubbed out. The North shop sold 12 loaves, 30 milks and 6 boxes of eggs; the South shop "
        "sold 8, 25 and 10. Keeping the numbers in their grid positions lets you do arithmetic on "
        "the whole table at once.", 14, gap=10)
    f.p("Your module says matrix {B:methods} are not assessed, but {B:solving simultaneous "
        "equations} is, and Lecture 12 solves them with matrices. So this chapter builds up just "
        "enough to follow that: reading a matrix, adding, multiplying (the only odd one), and the "
        "inverse, which is an undo button.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 12} {y:(matrices and systems of equations).}", 12.5)


def reading(ch):
    f = flow(ch)
    sec(f, "Reading a matrix: rows, columns, and seat numbers")
    f.p("{B:Rows} run across (like rows of seats in a cinema). {B:Columns} run up and down (like the "
        "columns holding up a building). The {B:size} is always said {B:rows first, then columns}:",
        14, gap=10)
    y_ = f.reserve(110)
    pg = f.pg
    examples = [([[1, 2], [3, 4]], "2 × 2", "2 rows, 2 columns"),
                ([[12, 30, 6], [8, 25, 10]], "2 × 3", "2 rows, 3 columns"),
                ([["a", "b"], ["c", "d"], ["e", "f"]], "3 × 2", "3 rows, 2 columns")]
    for k, (rows, sz, desc) in enumerate(examples):
        xx = L + 20 + k * 165
        mat(pg, xx, y_, rows, cw=30, rh=24, size=14, hrow=0 if k == 1 else None)
        pg.text(xx, y_ + 80, sz, 14, C.PINK, F.BOLD)
        pg.text(xx, y_ + 97, desc, 11, C.GREY)
    pg.note(L + 185, y_ + 52, "row 1 highlighted", C.BROWN, 13, solid=False)
    ch.term("matrix", "a rectangular table of numbers in rows and columns (plural: matrices)")
    ch.term("size of a matrix", "(number of rows) × (number of columns), said \"2 by 3\"")
    f.p("{b:Seat numbers.} Each number in a matrix is an {B:entry} (or element). Its address is "
        "written with two small numbers below the letter, a {B:subscript}: $a_{ij}$ means the entry "
        "in {B:row $i$, column $j$}, like \"row C, seat 7\".", 14, gap=8)
    ch.term("entry (element)", "one number inside a matrix; a₂₃ is the one in row 2, column 3")
    ch.term("subscript", "a small number or letter written low after a symbol, used as a label: a₁, x₂, a₂₃")
    ch.symbol(r"a_{ij}", "a sub i j", "the entry in row i, column j of matrix A")
    y_ = f.reserve(90)
    pg = f.pg
    mat(pg, L + 40, y_ + 6, [[12, 30, 6], [8, 25, 10]], cw=44, rh=30, size=16, hcell=(1, 2))
    pg.note(L + 200, y_ + 4, "a₂₃ = 10: go down to row 2,\nthen across to column 3.", C.GREEN, 16)
    pg.note(L + 200, y_ + 50, "a₁₂ = 30 (row 1, column 2)", C.GREY, 15)
    f.p("{h:Memory hook:} \"RC\", like a remote-controlled car: Rows before Columns, for sizes "
        "and for addresses.", 13.5, C.BROWN)


def adding(ch):
    f = flow(ch)
    sec(f, "Adding, subtracting and scaling: cell by cell", room=440)
    f.p("Week 1 and week 2 sales from the two shops. Total sales? Add each cell to the {B:matching "
        "cell}:", 14, gap=8)
    y_ = f.reserve(70)
    pg = f.pg
    mat(pg, L + 20, y_, [[12, 30, 6], [8, 25, 10]], cw=32)
    pg.text(L + 130, y_ + 16, "+", 18, C.INK, F.BOLD)
    mat(pg, L + 155, y_, [[10, 28, 4], [9, 20, 7]], cw=32)
    pg.text(L + 265, y_ + 16, "=", 18, C.INK, F.BOLD)
    mat(pg, L + 290, y_, [[22, 58, 10], [17, 45, 17]], cw=32, color=C.GREEN)
    pg.note(L + 20, y_ + 56, "12 + 10 = 22,  30 + 28 = 58, ...", C.GREY, 14)
    ch.check(M([[12, 30, 6], [8, 25, 10]]) + M([[10, 28, 4], [9, 20, 7]]), M([[22, 58, 10], [17, 45, 17]]))
    f.p("Lecture 12's picture of this: $\\begin{bmatrix}a&b\\\\c&d\\end{bmatrix} + "
        "\\begin{bmatrix}\\text{pizza}&\\text{kebab}\\\\\\text{curry}&\\text{soup}\\end{bmatrix}$ "
        "puts $a$ + pizza top-left, and so on. Things only combine with the thing in the {B:same seat}. "
        "So both matrices must be the {B:same size}; a 2 × 3 plus a 2 × 2 has no answer.", 14, gap=8)
    step(f, r"\begin{bmatrix}2&3&-1\\7&0&4\end{bmatrix}-\begin{bmatrix}-3&4&2\\1&0&2\end{bmatrix}"
            r"=\begin{bmatrix}5&-1&-3\\6&0&2\end{bmatrix}", "the slide's subtraction:  2 − (−3) = 5", size=17)
    ch.check(M([[2, 3, -1], [7, 0, 4]]) - M([[-3, 4, 2], [1, 0, 2]]), M([[5, -1, -3], [6, 0, 2]]))
    f.p("{b:Scaling} (multiplying by one plain number, called a {B:scalar}): every cell gets "
        "multiplied. Four weeks at the same rate:", 14, gap=6)
    step(f, r"4\begin{bmatrix}1&2\\3&4\end{bmatrix}=\begin{bmatrix}4&8\\12&16\end{bmatrix}", "4 × every entry",
         size=18)
    ch.check(4 * M([[1, 2], [3, 4]]), M([[4, 8], [12, 16]]))
    ch.term("scalar", "an ordinary single number (as opposed to a matrix or vector)")


def row_col(ch):
    f = flow(ch)
    sec(f, "Multiplying: row meets column", room=500)
    f.p("Multiplying two matrices is {B:not} cell by cell. It comes from a shopping bill. You buy "
        "2 coffees and 3 cakes; a coffee costs £2.50 and a cake £2. Write the order as a {B:row} "
        "and the prices as a {B:column}:", 14, gap=8)
    y_ = f.reserve(94) + 18
    pg = f.pg
    mat(pg, L + 20, y_ + 12, [[2, 3]], cw=36, hrow=0)
    pg.text(L + 20, y_ - 4, "order", 11, C.GREY)
    mat(pg, L + 110, y_, [["2.5"], [2]], cw=40, hcol=0)
    pg.text(L + 110, y_ - 16, "prices", 11, C.GREY)
    pg.eq(L + 170, y_ + 26, r"=2\times2.5+3\times2=11", 18, C.GREEN, valign="middle")
    pg.note(L + 20, y_ + 58, "first with first, second with second, then add: the bill is £11", C.PURPLE, 15)
    ch.check(M([[2, 3]]) * M([[sp.Rational(5, 2)], [2]]), M([[11]]))
    f.p("{B:That's the whole rule: pair up, multiply, add.} For bigger matrices you just do it for "
        "every row of the first with every column of the second. Lecture 12's example, traced with "
        "two highlighters (yellow row, blue column):", 14, gap=12)
    A, B = [[1, 2], [3, 4]], [[5, 6], [7, 8]]
    res = [[19, 22], [43, 50]]
    sums = [["1×5 + 2×7", "1×6 + 2×8"], ["3×5 + 4×7", "3×6 + 4×8"]]
    for i in range(2):
        y_ = f.reserve(76)
        pg = f.pg
        for j in range(2):
            xx = L + j * 250
            mat(pg, xx + 6, y_, A, cw=24, rh=24, size=14, hrow=i)
            mat(pg, xx + 66, y_, B, cw=24, rh=24, size=14, hcol=j)
            pg.text(xx + 124, y_ + 16, "→", 14, C.GREY)
            done = [[res[a][b] if (a, b) <= (i, j) else "" for b in range(2)] for a in range(2)]
            mat(pg, xx + 146, y_, done, cw=30, rh=24, size=14, hcell=(i, j))
            pg.note(xx + 6, y_ + 52, f"row {i + 1} × column {j + 1}:  {sums[i][j]} = {res[i][j]}", C.PURPLE, 14)
    ch.check(M(A) * M(B), M(res))
    f.p("{R:Slide check:} Lecture 12 writes the bottom-left entry as $3 \\times 5 + 4 \\times 8 = 47$. "
        "Row 2 of A is (3, 4) and column 1 of B is (5, 7), so it's $3 \\times 5 + 4 \\times 7 = 15 + 28 "
        "= 43$. The full answer is $\\begin{bmatrix}19&22\\\\43&50\\end{bmatrix}$.", 13.5)
    ch.term("matrix multiplication", "entry (i, j) of AB = row i of A paired with column j of B: multiply the pairs and add")


def dominoes(ch):
    f = flow(ch)
    sec(f, "Which sizes can multiply? Dominoes", room=400)
    f.p("Row-meets-column only works if a row of the first is {B:as long as} a column of the "
        "second (every item needs a price). Write each size as a domino and put them side by side: "
        "the {B:touching numbers must match}, and the {B:outside numbers give the answer's size}.",
        14, gap=10)
    y_ = f.reserve(150)
    pg = f.pg
    rows = [((2, 2), (2, 1), True, "2 × 1"), ((1, 2), (2, 1), True, "1 × 1 (a single number, like the bill)"),
            ((2, 3), (2, 2), False, "3 ≠ 2: can't be done")]
    for k, (d1, d2, ok, out) in enumerate(rows):
        yy = y_ + k * 46
        col = C.GREEN if ok else C.RED
        domino(pg, L + 20, yy, d1[0], d1[1], C.PINK)
        domino(pg, L + 88, yy, d2[0], d2[1], C.PINK)
        pg.ellipse(L + 86, yy + 15, 16, 13, col, 1.4)
        pg.text(L + 175, yy + 6, "→", 14, C.GREY)
        pg.text(L + 200, yy + 7, out, 13, col, F.BOLD)
    f.p("Lecture 12's \"different size\" example: $\\begin{bmatrix}1&4\\\\6&3\\end{bmatrix}"
        "\\begin{bmatrix}2\\\\5\\end{bmatrix}$ is (2 × 2)(2 × 1), so the answer is 2 × 1:", 14, gap=6)
    step(f, r"\begin{bmatrix}1\times2+4\times5\\6\times2+3\times5\end{bmatrix}=\begin{bmatrix}22\\27\end{bmatrix}",
         "each row meets the one column", size=18)
    ch.check(M([[1, 4], [6, 3]]) * M([[2], [5]]), M([[22], [27]]))


def order(ch):
    f = flow(ch)
    sec(f, "Order matters: CD is not DC", room=380)
    f.p("With ordinary numbers $3 \\times 5 = 5 \\times 3$. With matrices, swapping the order usually "
        "changes the answer. Lecture 12's \"give it a try\":", 14, gap=6)
    step(f, r"C=\begin{bmatrix}7&8\\2&-1\end{bmatrix},\quad D=\begin{bmatrix}3&2\\-1&4\end{bmatrix}", "", size=18)
    step(f, r"CD=\begin{bmatrix}7(3)+8(-1)&7(2)+8(4)\\2(3)+(-1)(-1)&2(2)+(-1)(4)\end{bmatrix}"
            r"=\begin{bmatrix}13&46\\7&0\end{bmatrix}", "", size=16)
    step(f, r"DC=\begin{bmatrix}3(7)+2(2)&3(8)+2(-1)\\-1(7)+4(2)&-1(8)+4(-1)\end{bmatrix}"
            r"=\begin{bmatrix}25&22\\1&-12\end{bmatrix}", "", size=16)
    Cm, Dm = M([[7, 8], [2, -1]]), M([[3, 2], [-1, 4]])
    ch.check(Cm * Dm, M([[13, 46], [7, 0]]))
    ch.check(Dm * Cm, M([[25, 22], [1, -12]]))
    f.p("Completely different! Think of socks and shoes: socks-then-shoes is not the same as "
        "shoes-then-socks. (The slide's heading says \"calculate CD\" again, but it's working out DC.)",
        14, gap=6)
    ch.term("commutative", "an operation where order doesn't matter (a × b = b × a); matrix multiplication is not")


def special(ch):
    f = flow(ch)
    sec(f, "The matrix that acts like 1", room=330)
    f.p("A {B:diagonal} matrix has numbers only on the diagonal from top-left to bottom-right (zeros "
        "elsewhere). The {B:identity} matrix $I$ is the diagonal matrix with every diagonal entry 1:",
        14, gap=6)
    step(f, r"I=\begin{bmatrix}1&0\\0&1\end{bmatrix}\qquad\begin{bmatrix}1&2\\3&4\end{bmatrix}"
            r"\begin{bmatrix}1&0\\0&1\end{bmatrix}=\begin{bmatrix}1&2\\3&4\end{bmatrix}", "unchanged!", size=18)
    ch.check(M([[1, 2], [3, 4]]) * sp.eye(2), M([[1, 2], [3, 4]]))
    f.p("Multiplying by $I$ changes nothing, just like multiplying a number by 1. Check the top-left "
        "entry: row (1, 2) meets column (1, 0): $1 \\times 1 + 2 \\times 0 = 1$. The zeros make sure "
        "each entry only \"sees\" itself.", 14)
    ch.term("identity matrix", "the square matrix I with 1s down the diagonal and 0s elsewhere; AI = IA = A")
    ch.term("diagonal matrix", "a square matrix whose only non-zero entries are on the top-left to bottom-right diagonal")


def equations(ch):
    f = flow(ch)
    sec(f, "Simultaneous equations as one matrix sum", room=380)
    f.p("Here's why matrices are in a course about equations. Multiply a 2 × 2 by a column of "
        "letters (Lecture 12):", 14, gap=6)
    step(f, r"\begin{bmatrix}3&2\\5&3\end{bmatrix}\begin{bmatrix}x\\y\end{bmatrix}=\begin{bmatrix}3x+2y\\5x+3y\end{bmatrix}",
         "row meets column, with letters", size=18)
    xs, ys = sp.symbols("x y")
    ch.check(M([[3, 2], [5, 3]]) * M([[xs], [ys]]), M([[3 * xs + 2 * ys], [5 * xs + 3 * ys]]))
    f.p("Those are the left-hand sides of two equations! So the pair $x + 2y = 13$ and "
        "$2x - 5y = 8$ can be written as {B:one} matrix equation:", 14, gap=6)
    y_ = f.reserve(104)
    pg = f.pg
    pg.eq(L + 30, y_ + 6, r"\begin{bmatrix}1&2\\2&-5\end{bmatrix}\begin{bmatrix}x\\y\end{bmatrix}"
          r"=\begin{bmatrix}13\\8\end{bmatrix}", 20)
    pg.note(L + 20, y_ + 76, "A = numbers in front", C.PINK, 14)
    pg.note(L + 150, y_ + 76, "X = unknowns", C.BLUE, 14)
    pg.note(L + 240, y_ + 76, "B = right-hand sides", C.GREEN, 14)
    pg.eq(L + 330, y_ + 20, r"AX=B", 26, C.PINK)
    f.p("It looks just like $3x = 12$, one equation with one unknown. To solve $3x = 12$ you'd undo "
        "the \"× 3\". So we need an {B:undo button for a matrix}.", 14)
    f.p("{h:Honest note:} for two equations, the Chapter 15 methods are quicker by hand. The matrix "
        "way wins for computers and for big systems, like Lecture 12's joke equation with 12 unknowns "
        "(which needs 12 independent equations).", 13.5, C.BROWN)
    ch.term("matrix equation", "AX = B: a set of simultaneous equations written with one matrix of coefficients A")


def inverse(ch):
    f = flow(ch)
    sec(f, "The inverse: an undo button (2 × 2 recipe)", room=520)
    f.p("For numbers, the undo for \"× 3\" is \"× $\\frac13$\" because $\\frac13 \\times 3 = 1$. For a "
        "matrix $A$, the undo is written $A^{-1}$ (\"A inverse\") and it satisfies $A^{-1}A = I$. "
        "Lecture 12 gives the recipe for a 2 × 2:", 14, gap=8)
    ch.symbol(r"A^{-1}", "A inverse", "the matrix that undoes A: A⁻¹A = I")
    y_ = f.reserve(120)
    pg = f.pg
    pg.eq(L + 10, y_ + 30, r"A=\begin{bmatrix}\color{cblu}a&\color{cred}b\\\color{cred}c&\color{cblu}d\end{bmatrix}",
          20, valign="middle")
    pg.arrow(L + 130, y_ + 30, L + 170, y_ + 30, C.GREY, 1.3)
    pg.eq(L + 180, y_ + 30, r"A^{-1}=\frac{1}{\color{cpur}ad-bc}\begin{bmatrix}\color{cblu}d&\color{cred}-b\\"
          r"\color{cred}-c&\color{cblu}a\end{bmatrix}", 20, valign="middle")
    pg.rich(L + 10, y_ + 66, "{B:1.} {b:swap} the two diagonal entries (a and d)   {B:2.} {r:change the sign} "
            "of the other two   {B:3.} {p:divide} everything by $ad - bc$", W - 20, 13)
    ch.formula(r"\begin{bmatrix}a&b\\c&d\end{bmatrix}^{-1}=\frac{1}{ad-bc}\begin{bmatrix}d&-b\\-c&a\end{bmatrix}",
               "inverse of a 2 × 2 matrix")
    a, b, c, d = sp.symbols("a b c d")
    ch.check(sp.simplify(M([[a, b], [c, d]]).inv() - M([[d, -b], [-c, a]]) / (a * d - b * c)), sp.zeros(2))
    f.p("The number $ad - bc$ is called the {B:determinant}. If it's 0 you'd divide by zero, so "
        "there's {B:no inverse}. That happens exactly when the two equations aren't independent "
        "(Chapter 15: the same line, or parallel lines).", 14, gap=8)
    ch.term("determinant", "for a 2 × 2 matrix, ad − bc; if it is 0 the matrix has no inverse")
    ch.term("inverse matrix", "A⁻¹, the matrix with A⁻¹A = I; it undoes multiplying by A")
    f.p("{b:Solve} $AX = B$ with $A = \\begin{bmatrix}1&2\\\\2&-5\\end{bmatrix}$. Tiny steps:", 14, gap=6)
    step(f, r"ad-bc=(1)(-5)-(2)(2)=-9", "the determinant (not 0: good)", size=18)
    step(f, r"A^{-1}=\frac{1}{-9}\begin{bmatrix}-5&-2\\-2&1\end{bmatrix}", "swap 1 and −5; flip signs of the 2s",
         size=18)
    step(f, r"X=A^{-1}B", "undo A on both sides (A⁻¹A = I, and IX = X)", size=18)
    step(f, r"=\frac{1}{-9}\begin{bmatrix}(-5)(13)+(-2)(8)\\(-2)(13)+(1)(8)\end{bmatrix}=\frac{1}{-9}"
            r"\begin{bmatrix}-81\\-18\end{bmatrix}", "row meets column", size=17)
    step(f, r"=\begin{bmatrix}9\\2\end{bmatrix}\ \Rightarrow\ x=9,\ y=2", "÷ (−9)", size=18, color=C.GREEN)
    A_ = M([[1, 2], [2, -5]])
    ch.check(A_.inv() * M([[13], [8]]), M([[9], [2]]))
    ch.check(A_.det(), -9)
    f.p("{G:Check in the original equations:} $9 + 2(2) = 13$ ✓ and $2(9) - 5(2) = 8$ ✓.", 13.5, gap=6)


def det_area(ch):
    f = flow(ch)
    sec(f, "What the determinant measures: area", room=560)
    f.p("$ad - bc$ looks like a random recipe, but it has a shape. Multiply a matrix by the corner points of a "
        "1 by 1 square, $\\begin{bmatrix}1\\\\0\\end{bmatrix}$ and $\\begin{bmatrix}0\\\\1\\end{bmatrix}$, "
        "and they land on the matrix's two {B:columns}. For $M = \\begin{bmatrix}3&1\\\\1&2\\end{bmatrix}$ "
        "the square gets pushed over into a slanted shape (a parallelogram):", 14, gap=12)
    g = 28
    y_ = f.reserve(3 * g + 64)
    pg = f.pg

    def grid(ox, oy, nx, ny):
        for i in range(nx + 1):
            pg.line(ox + i * g, oy, ox + i * g, oy - ny * g, "#d9dde3", 0.6)
        for j in range(ny + 1):
            pg.line(ox, oy - j * g, ox + nx * g, oy - j * g, "#d9dde3", 0.6)

    ox1, oy1 = L + 20, y_ + 3 * g + 26
    grid(ox1, oy1, 3, 3)
    pg.fillpoly([(ox1, oy1), (ox1 + g, oy1), (ox1 + g, oy1 - g), (ox1, oy1 - g)], C.LIGHT[C.PINK],
                outline=C.PINK, width=1.4)
    pg.note(ox1 - 6, oy1 + 4, "area 1", C.PINK, 13)
    pg.arrow(ox1 + 3 * g + 12, oy1 - 1.5 * g, ox1 + 3 * g + 52, oy1 - 1.5 * g, C.GREY, 1.4, head=6)
    pg.eq(ox1 + 3 * g + 32, oy1 - 1.5 * g - 22, r"\times M", 13, C.GREY, align="center")
    ox, oy = L + 190, oy1
    grid(ox, oy, 4, 3)
    P = lambda i, j: (ox + i * g, oy - j * g)
    pieces = [([P(0, 0), P(3, 0), P(3, 1)], C.ORANGE, "1.5"), ([P(1, 2), P(1, 3), P(4, 3)], C.ORANGE, "1.5"),
              ([P(3, 1), P(4, 1), P(4, 3)], C.TEAL, "1"), ([P(0, 0), P(1, 2), P(0, 2)], C.TEAL, "1"),
              ([P(3, 0), P(4, 0), P(4, 1), P(3, 1)], C.GREY, "1"), ([P(0, 2), P(1, 2), P(1, 3), P(0, 3)], C.GREY, "1")]
    total = 0
    for pts, col, lab in pieces:
        pg.fillpoly(pts, C.LIGHT[col], outline=col, width=0.8)
        cx = sum(p_[0] for p_ in pts) / len(pts)
        cy = sum(p_[1] for p_ in pts) / len(pts)
        pg.text(cx - 8, cy - 6, lab, 9, col, F.BOLD, w=16, align="center")
        total += float(lab)
    pg.fillpoly([P(0, 0), P(3, 1), P(4, 3), P(1, 2)], C.LIGHT[C.PINK], outline=C.PINK, width=1.6)
    pg.eq(ox + 2 * g, oy - 1.5 * g, r"5", 16, C.PINK, align="center", valign="middle")
    pg.rect(ox, oy - 3 * g, 4 * g, 3 * g, C.INK, 1.0)
    pg.note(ox - 6, oy + 4, "the box around it: 4 × 3 = 12", C.INK, 12)
    ch.check((12 - total, 3 * 2 - 1 * 1), (5.0, 5))
    pg.note(L + 330, y_ + 4, "Its area? Take the 4 × 3 box (12) and cut off the corner pieces: "
            "1.5 + 1.5 + 1 + 1 + 1 + 1 = 7.\n\n12 − 7 = 5, and ad − bc = 3×2 − 1×1 = 5 too!",
            C.INK, 14, w=R - L - 330)
    f.p("That always happens. With letters the box is $(a + b)$ by $(c + d)$, the orange triangles make one "
        "$a \\times c$ rectangle, the teal ones one $b \\times d$, and there are two grey $b \\times c$ "
        "rectangles:", 14, gap=6)
    step(f, r"(a+b)(c+d)-\org{ac}-\tea{bd}-\gry{2bc}=ad-bc", "the box, minus the corners", size=19,
         color=C.PINK)
    a_, b_, c_, d_ = sp.symbols("a b c d")
    ch.check(sp.expand((a_ + b_) * (c_ + d_) - a_ * c_ - b_ * d_ - 2 * b_ * c_), a_ * d_ - b_ * c_)
    f.p("So the {B:determinant is how much the matrix stretches area}: every shape comes out 5 times "
        "bigger under $M$. A minus sign means the square also got {B:flipped over}, like a mirror image: the "
        "inverse example's determinant of $-9$ means \"9 times the area, and flipped\".", 14, gap=10)

    f.p("{b:And why 0 means no undo button.} Try $\\begin{bmatrix}2&4\\\\1&2\\end{bmatrix}$: "
        "$ad - bc = 4 - 4 = 0$. Its columns point the same way, so the square gets squashed completely flat:",
        14, gap=10)
    y_ = f.reserve(3 * g + 40)
    pg = f.pg
    ox, oy = L + 40, y_ + 3 * g + 16
    for i in range(7):
        pg.line(ox + i * g, oy, ox + i * g, oy - 3 * g, "#d9dde3", 0.6)
    for j in range(4):
        pg.line(ox, oy - j * g, ox + 6 * g, oy - j * g, "#d9dde3", 0.6)
    pg.line(ox, oy, ox + 6 * g, oy - 3 * g, C.PINK, 3.0)
    pg.dot(ox + 2 * g, oy - g, 3, C.PINK)
    pg.dot(ox + 4 * g, oy - 2 * g, 3, C.PINK)
    pg.note(ox + 2 * g + 6, oy - g + 2, "(2, 1)", C.PINK, 12)
    pg.note(ox + 4 * g + 6, oy - 2 * g + 2, "(4, 2)", C.PINK, 12)
    ch.check(2 * 2 - 4 * 1, 0)
    pg.note(L + 250, y_ + 4, "The whole square lands on one line: area 0. Many different points land on the "
            "same spot, so there's no way to tell where each came from. You can't un-squash a line back "
            "into a square, so there is no inverse. That's the \"divide by zero\" warning, as a picture.",
            C.INK, 14, w=R - L - 250)


def order_seen(ch):
    f = flow(ch)
    sec(f, "Order matters, seen: stretch then turn, or turn then stretch?", room=600)
    f.p("A matrix moves every point, so two matrices in a row are two moves in a row. Take "
        "$S = \\begin{bmatrix}2&0\\\\0&1\\end{bmatrix}$ ({B:stretch} sideways ×2) and "
        "$T = \\begin{bmatrix}0&-1\\\\1&0\\end{bmatrix}$ ({B:turn} a quarter turn anticlockwise). Follow the "
        "square and its {R:red corner}:", 14, gap=8)
    Sm, Tm = M([[2, 0], [0, 1]]), M([[0, -1], [1, 0]])
    g = 20
    sq = [(0, 0), (1, 0), (1, 1), (0, 1)]

    def mini(ox, oy, mat_, col, cap):
        for i in range(-2, 3):
            pg.line(ox + i * g, oy, ox + i * g, oy - 2 * g, "#d9dde3", 0.6)
        for j in range(0, 3):
            pg.line(ox - 2 * g, oy - j * g, ox + 2 * g, oy - j * g, "#d9dde3", 0.6)
        pg.line(ox, oy + 3, ox, oy - 2 * g - 3, C.GREY, 1.0)
        pg.line(ox - 2 * g - 3, oy, ox + 2 * g + 3, oy, C.GREY, 1.0)
        pts = [mat_ * M([p_[0], p_[1]]) for p_ in sq]
        pg.fillpoly([(ox + v[0] * g, oy - v[1] * g) for v in pts], C.LIGHT[col], outline=col, width=1.6)
        red = pts[2]
        pg.dot(ox + red[0] * g, oy - red[1] * g, 3.8, C.RED)
        pg.text(ox, oy + 6, cap, 10, col, F.BOLD, align="center")
        return red

    y_ = f.reserve(230)
    pg = f.pg
    rows = [("stretch first, then turn", [(M.eye(2), "start"), (Sm, "after S"), (Tm * Sm, "after T: TALL")],
             ["stretch", "turn"], C.BLUE),
            ("turn first, then stretch", [(M.eye(2), "start"), (Tm, "after T"), (Sm * Tm, "after S: WIDE")],
             ["turn", "stretch"], C.ORANGE)]
    ends = []
    for r_, (title, stages, verbs, col) in enumerate(rows):
        oy = y_ + 70 + r_ * 110
        pg.text(L, oy - 64, title, 12, col, F.BOLD)
        for k, (mat_, cap) in enumerate(stages):
            ox = L + 70 + k * 160
            red = mini(ox, oy, mat_, col, cap)
            if k < 2:
                pg.arrow(ox + 2 * g + 12, oy - g, ox + 160 - 2 * g - 12, oy - g, C.GREY, 1.3, head=5)
                pg.text(ox + 80, oy - g - 18, verbs[k], 10.5, C.GREY, F.BOLD, align="center")
        ends.append(tuple(red))
        pg.note(L + 70 + 2 * 160 + 2 * g + 8, oy - 2 * g, f"red corner\nends at\n({red[0]}, {red[1]})", C.RED, 13)
    ch.check(ends, [(-1, 2), (-2, 1)])
    ch.check((Tm * Sm, Sm * Tm), (M([[0, -1], [2, 0]]), M([[0, -2], [1, 0]])))
    f.p("Same two moves, different order, different result: one ends up tall, the other wide. {R:Watch the "
        "order of the letters:} \"S first, then T\" is written $TS$, because the matrix nearest the point "
        "acts first ($TS\\,\\mathbf{v} = T(S\\mathbf{v})$). That's exactly why $CD \\neq DC$.", 14, gap=8)
    go(f, "To UNDO \"stretch, then turn\" (get the tall shape back to the start square), which move do you "
          "undo first: the stretch or the turn?")
    f.p("{b:Answer:} undo the {B:last} move first. Turn back, then un-stretch, just as you take off your "
        "shoes before your socks. So the inverse reverses the order:", 14, gap=6)
    step(f, r"(TS)^{-1}=S^{-1}T^{-1}", "undo the turn first, then the stretch", size=20, color=C.GREEN)
    ch.check((Tm * Sm).inv(), Sm.inv() * Tm.inv())
    ch.check((Tm * Sm).inv() * (Tm * Sm), M.eye(2))


def your_turn(ch):
    f = flow(ch)
    sec(f, "Spreadsheets: your turn", fresh=True)
    f.p("Answers in grey. Trace every multiplication with two fingers: one along the row, one down "
        "the column.", 13.5, gap=10)
    groups = [
        ("Reading", ["Size of [1 2 3]?", "Size of a matrix with 4 rows and 2 columns?",
                     "In [[5, 1], [7, 9]], what is a₂₁?"], "1. 1 × 3   2. 4 × 2   3. 7"),
        ("Adding and scaling", ["[[1, 2], [3, 4]] + [[0, 5], [−1, 2]]", "3 × [[2, −1], [0, 4]]",
                                "[[6, 3], [2, 1]] − [[1, 1], [1, 1]]"],
         "4. [[1, 7], [2, 6]]   5. [[6, −3], [0, 12]]   6. [[5, 2], [1, 0]]"),
        ("Multiplying", ["[1 4] × [[2], [3]]", "[[2, 1], [0, 3]] × [[1], [4]]", "[[1, 2], [0, 1]] × [[3, 0], [1, 2]]",
                         "Can a 3 × 2 multiply a 3 × 2?"],
         "7. [14]   8. [[6], [12]]   9. [[5, 4], [1, 2]]   10. No: inner numbers 2 and 3 don't match"),
        ("Inverse and equations", ["Determinant of [[4, 3], [2, 1]]", "Inverse of [[2, 1], [5, 3]]",
                                   "Solve 2x + y = 5, 5x + 3y = 13 using your answer to 12"],
         "11. 4 − 6 = −2   12. [[3, −1], [−5, 2]] (determinant 1)   13. x = 2, y = 1"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.PINK, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{n}. {qq}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(M([[1, 2], [3, 4]]) + M([[0, 5], [-1, 2]]), M([[1, 7], [2, 6]]))
    ch.check(3 * M([[2, -1], [0, 4]]), M([[6, -3], [0, 12]]))
    ch.check(M([[1, 4]]) * M([[2], [3]]), M([[14]]))
    ch.check(M([[2, 1], [0, 3]]) * M([[1], [4]]), M([[6], [12]]))
    ch.check(M([[1, 2], [0, 1]]) * M([[3, 0], [1, 2]]), M([[5, 4], [1, 2]]))
    ch.check(M([[4, 3], [2, 1]]).det(), -2)
    ch.check(M([[2, 1], [5, 3]]).inv(), M([[3, -1], [-5, 2]]))
    ch.check(M([[3, -1], [-5, 2]]) * M([[5], [13]]), M([[2], [1]]))


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    reading(ch)
    adding(ch)
    row_col(ch)
    dominoes(ch)
    order(ch)
    special(ch)
    equations(ch)
    inverse(ch)
    det_area(ch)
    order_seen(ch)
    your_turn(ch)
