"""Chapter 2 - Fractions. Everything is done with chocolate bars that get cut and re-cut."""
from fractions import Fraction as Fr

from generator import canvas as C
from generator import fonts as F
from content.kit import go

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
              "multiply-fractions", "divide-fractions", "reciprocal", "compare-fractions"]

CHOC = "#7a4a26"
CHOC_L = "#c89a6e"
WRAP = "#f6eee4"
L, R, W = 50, 545, 495


# ----------------------------------------------------------------------------- drawing kit
def bar(pg, x, y, w, h, n, have=0, color=CHOC, light=None, empty=WRAP, lw=1.3, rows=1,
        have_cells=None, label=None):
    """A chocolate bar cut into n equal columns (and optionally rows). The first `have`
    pieces (column by column) are filled."""
    light = light or color
    cw, rh = w / n, h / rows
    idx = 0
    for c in range(n):
        for r in range(rows):
            filled = (idx < have) if have_cells is None else ((c, r) in have_cells)
            pg.rect(x + c * cw + 1.2, y + r * rh + 1.2, cw - 2.4, rh - 2.4, color, 0,
                    fillcolor=light if filled else empty, r=2)
            idx += 1
    pg.rect(x, y, w, h, CHOC, lw + 0.4, r=3)
    for c in range(1, n):
        pg.line(x + c * cw, y, x + c * cw, y + h, CHOC, lw)
    for r in range(1, rows):
        pg.line(x, y + r * rh, x + w, y + r * rh, CHOC, lw)
    if label:
        pg.eq(x + w + 14, y + h / 2, label, 20, valign="middle")


def grid(pg, x, y, w, h, cols, rows, fill_fn, lw=1.0, vcol=CHOC, hcol=CHOC):
    """Bar cut both ways; fill_fn(c, r) -> colour or None."""
    cw, rh = w / cols, h / rows
    for c in range(cols):
        for r in range(rows):
            col = fill_fn(c, r)
            if col:
                pg.rect(x + c * cw, y + r * rh, cw, rh, col, 0, fillcolor=col)
    for c in range(1, cols):
        pg.line(x + c * cw, y, x + c * cw, y + h, vcol, lw)
    for r in range(1, rows):
        pg.line(x, y + r * rh, x + w, y + r * rh, hcol, lw)
    pg.rect(x, y, w, h, CHOC, 1.8, r=2)


def step(f, latex, why, size=22, color=C.INK, x=L + 20, note_x=None, col=C.RED):
    """A worked line with its reason written beside it."""
    w, h, _ = f.pg.eq_size(latex, size)
    nx = note_x or max(x + w + 36, 300)
    nh = F.line_h(F.HAND, 16) * len(F.wrap(why, F.HAND, 16, R - nx)) if why else 0
    y = f.reserve(max(h, nh) + 12)
    pg = f.pg
    pg.eq(x, y, latex, size, color)
    if why:
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
    pg.rect(L - 8, y, 6, 28, CHOC, 0, fillcolor=CHOC)
    pg.text(L + 6, y + 1, s, 20, CHOC, F.BOLD)
    f.y += 34
    if sub:
        f.p(sub, 12.5, C.GREY, gap=8)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = ch.new_page(bg="#fbf5ee")
    pg.text(L, 70, "Chapter 2", 16, C.GREY, F.BOLD)
    pg.text(L, 92, "Fractions", 44, CHOC, F.BOLD)
    pg.note(L, 150, "or: how to share a chocolate bar without an argument", CHOC, 24)
    # big bar with 3 of 8 pieces broken off
    x, y, w, h = 95, 230, 330, 120
    cw = w / 8
    for i in range(8):
        dx, dy = (0, 0) if i < 5 else (40 + (i - 5) * 16, -30 + (i - 5) * 28)
        pg.rect(x + i * cw + dx, y + dy, cw - 3, h, CHOC, 1.6, fillcolor=CHOC_L, r=4)
        pg.rect(x + i * cw + dx + 7, y + dy + 8, cw - 17, h / 2 - 12, CHOC, 0.8, r=3)
        pg.rect(x + i * cw + dx + 7, y + dy + h / 2 + 4, cw - 17, h / 2 - 12, CHOC, 0.8, r=3)
    pg.note(445, 205, "3 pieces\nbroken off", C.RED, 20)
    pg.eq(300, 400, r"\frac{\red{3}}{\brn{8}}", 44, align="center")
    pg.note(345, 400, "3 pieces taken...", C.RED, 20)
    pg.note(345, 440, "...out of 8 equal pieces", CHOC, 20)
    f = ch.flow(top=510)
    f.p("A fraction is the maths way of saying {b:\"part of something\"}. Half a pizza, three "
        "quarters of an hour, two thirds of the class. That is all. Every rule in this chapter "
        "(adding, taking away, multiplying, dividing) will be worked out by {B:drawing a "
        "chocolate bar and cutting it up}. You will see each rule happen before you see it "
        "written in symbols.", 14, gap=12)
    f.p("{y:This chapter goes with your} {B:Lecture 1} {y:(Combining fractions). It uses times tables, "
        "factors and the lowest common multiple from Chapter 1. If \"factor\" or \"LCM\" sound "
        "unfamiliar, have a quick look back there first.}", 12.5)


def what_is(ch):
    f = flow(ch)
    heading(f, "What the two numbers mean")
    f.p("Take a bar of chocolate and snap it into {B:4 equal pieces}. You eat {B:3} of them.", 14,
        gap=10)
    y = f.reserve(70)
    pg = f.pg
    bar(pg, 110, y + 5, 280, 55, 4, have=3)
    for i in range(3):
        pg.note(110 + 35 + i * 70, y + 18, "eaten", "#ffffff", 16, align="center")
    f.p("You have eaten three pieces, out of four equal pieces. In maths shorthand:", 14, gap=6)
    y = f.reserve(f.pg.eq_size(r"\frac{\org{3}}{\blu{4}}", 60)[1] + 18)
    pg = f.pg
    pg.eq(250, y + 4, r"\frac{\org{3}}{\blu{4}}", 60, align="center")
    pg.arrow(360, y + 25, 285, y + 28, C.ORANGE, 1.5)
    pg.note(368, y + 8, "TOP: how many pieces\nyou have (or ate)", C.ORANGE, 18)
    pg.arrow(360, y + 92, 285, y + 88, C.BLUE, 1.5)
    pg.note(368, y + 75, "BOTTOM: how many equal\npieces the whole bar was cut into", C.BLUE, 18)
    pg.note(60, y + 45, "the line\nmeans \"out of\"", C.GREY, 17)
    pg.arrow(150, y + 60, 225, y + 58, C.GREY, 1.2)
    f.p("You say it: {h:\"three quarters\"}. The bottom number gives the pieces their name: cut "
        "into 4 gives {b:quarters}, cut into 3 gives {b:thirds}, cut into 8 gives {b:eighths}. The top "
        "number counts how many of those pieces you have.", 14, gap=12)
    f.p("The two numbers have official names. You don't need to love them, but your lecturer will "
        "use them:", 13, gap=4)
    f.bullet("{O:numerator} = the {o:top} number (it {o:counts} the pieces, like a \"numberer\").", 13)
    f.bullet("{B:denominator} = the {b:bottom} number (it gives the pieces their {b:name}, "
             "\"denomination\" means name).", 13)
    f.gap(4)
    f.p("{h:Memory trick:} {B:D}enominator is {B:D}own below.", 13, C.BROWN, gap=14)
    ch.term("fraction", "part of a whole, written as top number over bottom number")
    ch.term("numerator", "the top number of a fraction: how many pieces you have")
    ch.term("denominator", "the bottom number of a fraction: how many equal pieces the whole is cut into")
    f.p("{R:The pieces must be equal.}  If you snap a bar badly, the pieces are not quarters, even if "
        "there are four of them:", 13, gap=6)
    y = f.reserve(70)
    pg = f.pg
    xs = [110, 150, 250, 330, 390]
    for a, b in zip(xs, xs[1:]):
        pg.rect(a + 1, y + 6, b - a - 2, 50, CHOC, 1.3, fillcolor=CHOC_L, r=2)
    pg.xmark(410, y + 20, 22)
    pg.note(445, y + 12, "4 pieces, but NOT\n4 quarters", C.RED, 18)


def fraction_is_division(ch):
    f = flow(ch)
    heading(f, "A fraction is also a sharing sum")
    f.p("Here is a second way to see  $\\frac{3}{4}$, and it will be useful all through the book. "
        "Imagine {B:3 bars} shared equally between {B:4 people}.", 14, gap=8)
    y = f.reserve(140)
    pg = f.pg
    cols = [C.LIGHT[C.BLUE], C.LIGHT[C.ORANGE], C.LIGHT[C.GREEN], C.LIGHT[C.PURPLE]]
    for b in range(3):
        bx, by = 70, y + 8 + b * 42
        for i in range(4):
            pg.rect(bx + i * 60 + 1, by, 58, 34, CHOC, 1.2, fillcolor=cols[i], r=2)
            pg.text(bx + i * 60 + 30, by + 9, "ABCD"[i], 12, C.INK, F.BOLD, align="center")
    pg.note(330, y + 12, "cut each bar into 4 quarters.\nPerson A takes one quarter of\nevery bar, and "
            "so does B, C and D.", C.INK, 17)
    pg.note(330, y + 90, "Each person ends up with\n3 quarters.", C.GREEN, 19)
    f.p("So 3 shared by 4 gives each person three quarters:", 14, gap=4)
    f.eq(r"3 \div 4 = \frac{3}{4}", 30, gap=8)
    f.p("The fraction line {B:is} a division sign. Whenever you see a fraction, you can read it as "
        "\"top shared by bottom\" or \"top divided by bottom\". That is why $\\frac{12}{3}$ is just "
        "a fancy way to write 4: twelve shared between three.", 14, gap=14)
    ch.check(Fr(12, 3), 4)
    f.p("Now a gallery of fractions, to get your eye used to them. Say each one out loud.", 14, gap=8)
    items = [(1, 2, "one half"), (1, 3, "one third"), (2, 3, "two thirds"), (1, 4, "one quarter"),
             (3, 5, "three fifths"), (5, 8, "five eighths"), (4, 4, "four quarters = one whole"),
             (0, 5, "zero fifths = nothing")]
    for i, (a, b, say) in enumerate(items):
        if i % 2 == 0:
            y = f.reserve(60)
        pg = f.pg
        x0 = L + (i % 2) * 250
        pg.eq(x0 + 14, y + 4, r"\frac{%d}{%d}" % (a, b), 22, align="center")
        bar(pg, x0 + 40, y + 8, 110, 26, b, have=a)
        pg.note(x0 + 40, y + 34, say, C.BROWN, 15)


def equivalent(ch):
    f = flow(ch)
    heading(f, "Same amount of chocolate, different names")
    f.p("Take a bar cut into 2 and keep 1 piece. Now take an identical bar, and this time cut "
        "{B:every piece in half again}. And again. Look at how much chocolate is shaded:", 14, gap=8)
    rows = [(2, 1, r"\frac{1}{2}", ""), (4, 2, r"\frac{2}{4}", "cut every piece in 2:\n2x as many pieces, 2x as many kept"),
            (8, 4, r"\frac{4}{8}", "cut every piece in 2 again")]
    for n, k, lab, why in rows:
        y = f.reserve(56)
        pg = f.pg
        bar(pg, 80, y + 6, 240, 42, n, have=k, light=C.LIGHT[C.GREEN], color=C.GREEN)
        pg.eq(345, y + 27, lab, 22, valign="middle")
        if why:
            pg.note(390, y + 6, why, C.RED, 15)
    f.p("The shaded amount never changes: it is always exactly half the bar. So", 14, gap=4)
    f.eq(r"\frac{1}{2}=\frac{2}{4}=\frac{4}{8}", 30, gap=8)
    ch.check(Fr(1, 2), Fr(2, 4))
    ch.check(Fr(2, 4), Fr(4, 8))
    f.p("Fractions that look different but are the same amount are called {B:equivalent "
        "fractions} (\"equal value\").", 14, gap=12)
    ch.term("equivalent fractions", "fractions that look different but are the same amount, like 1/2 and 2/4")
    f.p("{B:What happened to the numbers?} When every piece was cut into 2, there were twice as many "
        "pieces (the bottom doubled) and twice as many shaded ones (the top doubled). Doing the same "
        "thing to top and bottom keeps the amount the same:", 14, gap=8)
    y, w, h = step(f, r"\frac{1}{2}=\frac{1\org{\times 2}}{2\org{\times 2}}=\frac{2}{4}",
                   "times top AND bottom by 2: same amount")
    y, w, h = step(f, r"\frac{3}{4}=\frac{3\org{\times 5}}{4\org{\times 5}}=\frac{15}{20}",
                   "times top AND bottom by 5: same amount")
    ch.check(Fr(3, 4), Fr(15, 20))
    f.gap(6)
    f.p("{R:The one rule:} you can multiply (or divide) the top and bottom by the {R:same} number, and "
        "the fraction keeps its value. If you only change one of them, you change the amount.", 13.5,
        gap=8)
    f.p("{R:Adding does not work.}  Adding 1 to top and bottom of $\\frac{1}{2}$ gives $\\frac{2}{3}$, "
        "and two thirds is more than a half. Only {B:multiplying} or {B:dividing} both keeps the "
        "amount.", 13)
    ch.check_true(Fr(2, 3) != Fr(1, 2))


def simplify(ch):
    f = flow(ch)
    heading(f, "Simplifying: gluing pieces back together")
    f.p("Going the other way is just as useful. Here are 6 pieces kept out of 8. Glue the pieces "
        "together in {B:pairs}:", 14, gap=8)
    y = f.reserve(124)
    pg = f.pg
    bar(pg, 80, y + 4, 280, 44, 8, have=6, light=C.LIGHT[C.PURPLE], color=C.PURPLE)
    pg.eq(385, y + 26, r"\frac{6}{8}", 22, valign="middle")
    for i in range(4):
        pg.brace(80 + i * 70 + 4, y + 52, 80 + i * 70 + 66, y + 52, C.PURPLE, 1.1, 6)
    bar(pg, 80, y + 70, 280, 44, 4, have=3, light=C.LIGHT[C.PURPLE], color=C.PURPLE)
    pg.eq(385, y + 92, r"\frac{3}{4}", 22, valign="middle")
    pg.note(430, y + 50, "same chocolate,\nfewer, bigger pieces", C.RED, 16)
    f.p("Gluing pairs means: {B:divide the top by 2 and the bottom by 2}.", 14, gap=4)
    step(f, r"\frac{6}{8}=\frac{6\org{\div 2}}{8\org{\div 2}}=\frac{3}{4}",
         "divide top AND bottom by 2")
    ch.check(Fr(6, 8), Fr(3, 4))
    f.p("This is called {B:simplifying} (or {B:reducing}, or {B:cancelling}) a fraction. The answer is "
        "the same amount, written with the smallest possible numbers. When nothing (except 1) divides "
        "into both numbers any more, the fraction is in its {B:simplest form}.", 14, gap=12)
    ch.term("simplify a fraction", "divide top and bottom by the same number so the numbers are as small as possible")
    f.need(260)
    f.p("{b:A harder one, in tiny steps:} simplify  $\\frac{12}{18}$.", 14, gap=6)
    step(f, r"\frac{12}{18}", "Which numbers divide into BOTH 12 and 18?", note_x=240)
    y = f.reserve(64)
    pg = f.pg
    pg.rich(L + 20, y, "Factors of 12:  1, {g:2}, {g:3}, 4, {G:6}, 12", 380, 13)
    pg.rich(L + 20, y + 22, "Factors of 18:  1, {g:2}, {g:3}, {G:6}, 9, 18", 380, 13)
    pg.note(360, y + 6, "the biggest one in both\nlists is 6 (the HCF,\nfrom Chapter 1)", C.RED, 15)
    step(f, r"\frac{12}{18}=\frac{12\org{\div 6}}{18\org{\div 6}}", "divide top and bottom by 6")
    step(f, r"\frac{12\div 6}{18\div 6}=\grn{\frac{2}{3}}", "12 shared by 6 is 2;\n18 shared by 6 is 3")
    ch.check(Fr(12, 18), Fr(2, 3))
    f.p("{h:It's fine to do it in smaller jumps.} Dividing by 2 first gives $\\frac{6}{9}$, then "
        "dividing by 3 gives $\\frac{2}{3}$. Same answer. The HCF just gets there in one go.", 13,
        C.BROWN)


def improper(ch):
    f = flow(ch)
    heading(f, "More than one whole bar")
    f.p("What does  $\\frac{7}{4}$  mean? Seven pieces, where each piece is a quarter. But a bar only "
        "has 4 quarters... so you need {B:a second bar}:", 14, gap=8)
    y = f.reserve(80)
    pg = f.pg
    bar(pg, 70, y + 6, 200, 50, 4, have=4, light=C.LIGHT[C.ORANGE], color=C.ORANGE)
    bar(pg, 300, y + 6, 200, 50, 4, have=3, light=C.LIGHT[C.ORANGE], color=C.ORANGE)
    pg.note(170, y + 58, "one whole bar (4 quarters)", C.ORANGE, 16, align="center")
    pg.note(400, y + 58, "plus 3 quarters", C.ORANGE, 16, align="center")
    f.p("Seven quarters is one whole bar and three more quarters. Both ways of writing it are used:",
        14, gap=4)
    f.eq(r"\frac{7}{4}=1\tfrac{3}{4}", 32, gap=6)
    ch.check(Fr(7, 4), 1 + Fr(3, 4))
    f.p("{B:$\\frac{7}{4}$} is an {B:improper fraction} (top bigger than bottom: more than a whole). "
        "{B:$1\\tfrac{3}{4}$} is a {B:mixed number} (a whole number and a fraction mixed together, "
        "said \"one and three quarters\"). A fraction smaller than one whole, like $\\frac{3}{4}$, is "
        "called a {B:proper fraction}.", 13.5, gap=12)
    ch.term("improper fraction", "a fraction whose top is bigger than its bottom (more than one whole)")
    ch.term("mixed number", "a whole number and a fraction together, such as 1 3/4")
    ch.term("proper fraction", "a fraction less than one whole: top smaller than bottom")
    f.p("{b:Improper to mixed:} how many whole bars can you fill?  Take $\\frac{11}{4}$.", 14, gap=4)
    step(f, r"11 \div 4 = 2\ \text{remainder}\ 3", "4 goes into 11 twice (8), with 3 left over")
    step(f, r"\frac{11}{4}=\org{2}\tfrac{\org{3}}{4}", "2 whole bars, and 3 quarters left over")
    ch.check(Fr(11, 4), 2 + Fr(3, 4))
    f.gap(4)
    f.need(230)
    f.p("{b:Mixed to improper:} turn the whole bars back into pieces.  Take $2\\tfrac{1}{3}$.", 14,
        gap=4)
    y = f.reserve(60)
    pg = f.pg
    for i in range(2):
        bar(pg, 70 + i * 140, y + 4, 120, 36, 3, have=3, light=C.LIGHT[C.TEAL], color=C.TEAL)
    bar(pg, 350, y + 4, 120, 36, 3, have=1, light=C.LIGHT[C.TEAL], color=C.TEAL)
    pg.note(70, y + 40, "each whole bar = 3 thirds", C.TEAL, 15)
    step(f, r"2\tfrac{1}{3} = \org{2\times 3}\ \text{thirds} + 1\ \text{third}",
         "2 bars, each 3 thirds")
    step(f, r"= 6+1 = 7\ \text{thirds} = \grn{\frac{7}{3}}", "count all the thirds")
    ch.check(2 + Fr(1, 3), Fr(7, 3))
    f.p("{h:The shortcut people use:} whole number times bottom, add the top, keep the bottom. "
        "$2\\tfrac13 \\to (2\\times3+1)$ over 3. Now you know {B:why} it works.", 13, C.BROWN)


def add_same(ch):
    f = flow(ch)
    heading(f, "Adding: easy when the pieces match")
    f.p("You have  $\\frac{1}{5}$  of a bar. A friend gives you  $\\frac{2}{5}$  of an identical bar. "
        "How much do you have?", 14, gap=8)
    y = f.reserve(80)
    pg = f.pg
    bar(pg, 60, y + 6, 160, 36, 5, have=1, light=C.LIGHT[C.BLUE], color=C.BLUE)
    pg.text(232, y + 12, "+", 22, C.INK, F.BOLD)
    bar(pg, 255, y + 6, 160, 36, 5, have_cells={(1, 0), (2, 0)}, light=C.LIGHT[C.ORANGE])
    pg.text(430, y + 12, "=", 22, C.INK, F.BOLD)
    pg.note(60, y + 46, "1 fifth", C.BLUE, 16)
    pg.note(255, y + 46, "2 fifths", C.ORANGE, 16)
    y2 = f.reserve(56)
    bar(pg, 255, y2, 160, 36, 5, have_cells={(0, 0)}, light=C.LIGHT[C.BLUE])
    for c in (1, 2):
        pg.rect(255 + c * 32 + 1.2, y2 + 1.2, 29.6, 33.6, C.ORANGE, 0, fillcolor=C.LIGHT[C.ORANGE], r=2)
    pg.note(430, y2 + 4, "3 fifths", C.GREEN, 20)
    f.p("Count the pieces: 1 fifth and 2 fifths make 3 fifths. The pieces are still {B:fifths}, so "
        "the bottom number {B:does not change}.", 14, gap=6)
    step(f, r"\frac{\blu{1}}{5}+\frac{\org{2}}{5}=\frac{\blu{1}+\org{2}}{5}=\grn{\frac{3}{5}}",
         "add the tops (count the pieces);\nkeep the bottom (the piece size)")
    ch.check(Fr(1, 5) + Fr(2, 5), Fr(3, 5))
    f.gap(8)
    f.need(330)
    f.p("{R:The most common mistake in all of maths}", 16, C.RED, gap=4)
    f.p("It is very tempting to add the bottoms too:", 14, gap=4)
    y = f.reserve(f.pg.eq_size(r"\frac{1}{5}+\frac{2}{5}=\frac{3}{10}", 24)[1] + 12)
    pg = f.pg
    w, h = pg.eq(L + 30, y, r"\frac{1}{5}+\frac{2}{5}=\frac{3}{10}", 24)
    pg.strike(L + 22, y - 2, w + 16, h + 4)
    pg.note(L + w + 70, y + 4, "NO!", C.RED, 26)
    f.p("Check it with chocolate: $\\frac{3}{10}$ means 3 pieces of a bar cut into 10. Those are "
        "{B:tiny} pieces. Three of them is {R:less} than the $\\frac{2}{5}$ your friend gave you on "
        "its own! Adding chocolate can't leave you with less. The bottom number is a {B:name} "
        "(\"fifths\"), and names don't add: 1 apple + 2 apples = 3 apples, not 3 \"double-apples\".",
        13.5, gap=6)
    ch.check_true(Fr(3, 10) < Fr(2, 5))
    y = f.reserve(70)
    pg = f.pg
    bar(pg, 90, y + 4, 300, 26, 10, have=3, light=C.LIGHT[C.RED], color=C.RED)
    pg.note(400, y + 2, "3/10: tiny pieces", C.RED, 16)
    bar(pg, 90, y + 36, 300, 26, 5, have_cells={(1, 0), (2, 0)}, light=C.LIGHT[C.ORANGE])
    pg.note(400, y + 34, "2/5 alone is more!", C.ORANGE, 16)
    f.p("{B:Taking away} works the same way when the pieces match:  "
        "$\\frac{4}{7}-\\frac{1}{7}=\\frac{3}{7}$  (4 pieces, eat 1, 3 left; still sevenths).", 13.5)
    ch.check(Fr(4, 7) - Fr(1, 7), Fr(3, 7))


def add_different(ch):
    f = flow(ch)
    heading(f, "Adding when the pieces are different sizes")
    f.p("Now the hard one. What is  $\\frac{1}{2}+\\frac{1}{3}$ ?  You can't just count pieces, "
        "because a half and a third are {R:different sizes}. \"One half-piece plus one third-piece\" is "
        "like adding 1 euro to 1 pound: you need to convert to the same thing first.", 14, gap=10)
    y = f.reserve(80)
    pg = f.pg
    bar(pg, 70, y + 4, 180, 44, 2, have=1, light=C.LIGHT[C.BLUE], color=C.BLUE)
    pg.text(262, y + 14, "+", 22, C.INK, F.BOLD)
    bar(pg, 290, y + 4, 180, 44, 3, have=1, light=C.LIGHT[C.ORANGE], color=C.ORANGE)
    pg.note(70, y + 50, "a half", C.BLUE, 16)
    pg.note(290, y + 50, "a third: a different size!", C.ORANGE, 16)
    f.p("{b:The trick: re-cut both bars so that all the pieces are the same size.} Draw the "
        "\"thirds\" cuts onto the halves bar, and the \"halves\" cut onto the thirds bar:", 14, gap=8)
    y = f.reserve(110)
    pg = f.pg
    grid(pg, 70, y + 4, 180, 44, 6, 1, lambda c, r: C.LIGHT[C.BLUE] if c < 3 else None, lw=0.8,
         vcol="#b48a60")
    pg.line(160, y + 4, 160, y + 48, CHOC, 2)
    grid(pg, 290, y + 4, 180, 44, 6, 1, lambda c, r: C.LIGHT[C.ORANGE] if c < 2 else None, lw=0.8,
         vcol="#b48a60")
    pg.line(350, y + 4, 350, y + 48, CHOC, 2)
    pg.line(410, y + 4, 410, y + 48, CHOC, 2)
    pg.note(70, y + 52, "half = 3 sixths", C.BLUE, 17)
    pg.note(290, y + 52, "third = 2 sixths", C.ORANGE, 17)
    pg.note(185, y + 80, "Now both bars are cut into 6 equal pieces: SIXTHS.", C.RED, 17)
    f.p("Now the pieces match, so you can count them:  3 sixths + 2 sixths = {G:5 sixths}.", 14,
        gap=8)
    f.need(250)
    f.p("{b:The same thing, written as maths, one change per line:}", 14, gap=4)
    step(f, r"\frac{1}{2}+\frac{1}{3}", "different bottoms: can't add yet")
    step(f, r"=\frac{1\org{\times3}}{2\org{\times3}}+\frac{1\pur{\times2}}{3\pur{\times2}}",
         "make both bottoms 6, top AND bottom\nchanged together (equivalent fractions)")
    step(f, r"=\frac{3}{6}+\frac{2}{6}", "work out the multiplications")
    step(f, r"=\frac{3+2}{6}=\grn{\frac{5}{6}}", "same pieces now: add the tops")
    ch.check(Fr(1, 2) + Fr(1, 3), Fr(5, 6))
    f.p("{h:Where did 6 come from?} It is the smallest number that both 2 and 3 go into: the "
        "{B:lowest common multiple} (LCM) from Chapter 1. It's the smallest piece-count that both "
        "bars can be re-cut into.", 13, C.BROWN)


def lecture_add(ch):
    f = flow(ch)
    heading(f, "Your lecture example:  2/3 + 4/5")
    f.p("Lecture 1 works through  $\\frac{2}{3}+\\frac{4}{5}$. Thirds and fifths don't match, so we "
        "re-cut. A neat way to see it: cut one bar into 3 {B:columns} and the other into 5 {O:rows}. "
        "Then put {B:both} sets of cuts on {B:both} bars. Every bar is now a grid of 3 x 5 = 15 "
        "little squares: {B:fifteenths}.", 14, gap=10)
    y = f.reserve(170)
    pg = f.pg
    bw, bh = 150, 110
    grid(pg, 70, y + 10, bw, bh, 3, 5, lambda c, r: C.LIGHT[C.BLUE] if c < 2 else None, 0.8,
         vcol=CHOC, hcol="#c9a877")
    grid(pg, 330, y + 10, bw, bh, 3, 5, lambda c, r: C.LIGHT[C.ORANGE] if r < 4 else None, 0.8,
         vcol="#c9a877", hcol=CHOC)
    pg.text(262, y + 50, "+", 26, C.INK, F.BOLD)
    pg.note(70, y + 125, "2 of 3 columns = 10 squares", C.BLUE, 16)
    pg.note(330, y + 125, "4 of 5 rows = 12 squares", C.ORANGE, 16)
    pg.note(145, y - 6, "thirds", C.BLUE, 15, align="center")
    pg.note(405, y - 6, "fifths", C.ORANGE, 15, align="center")
    f.p("Count the squares: 10 + 12 = 22 squares, and each square is one fifteenth.", 14, gap=6)
    step(f, r"\frac{2}{3}+\frac{4}{5}", "thirds and fifths: different pieces")
    step(f, r"=\frac{2\org{\times5}}{3\org{\times5}}+\frac{4\pur{\times3}}{5\pur{\times3}}",
         "re-cut both into fifteenths (3x5=15)")
    step(f, r"=\frac{\blu{10}}{15}+\frac{\org{12}}{15}", "these are the squares counted above")
    step(f, r"=\frac{22}{15}", "same pieces: add the tops")
    step(f, r"=\grn{1\tfrac{7}{15}}", "15 of the 22 squares fill one\nwhole bar; 7 squares left over")
    ch.check(Fr(2, 3) + Fr(4, 5), Fr(22, 15))
    ch.check(Fr(22, 15), 1 + Fr(7, 15))
    f.gap(4)
    f.p("{G:Sense check} (your lecturer loves these): $\\frac23$ is a bit less than 1 and $\\frac45$ "
        "is a bit less than 1, so the total should be a bit less than 2, and more than 1. "
        "$1\\tfrac{7}{15}$ is. {h:Always ask \"is my answer a sensible size?\"}", 13.5)


def formula_page(ch):
    f = flow(ch)
    heading(f, "Where the lecture's formula comes from")
    f.p("Your slides show this recipe for adding any two fractions. It looks scary, but it is "
        "{B:exactly} the grid you just drew, written with letters instead of numbers:", 14, gap=8)
    f.eq(r"\frac{\blu{a}}{\blu{b}}+\frac{\org{c}}{\org{d}}=\frac{\blu{a}\org{d}+\blu{b}\org{c}}{\blu{b}\org{d}}",
         36, gap=10)
    ch.formula(r"\frac{a}{b}+\frac{c}{d}=\frac{ad+bc}{bd}", "adding fractions")
    f.p("Match it up with $\\frac{2}{3}+\\frac{4}{5}$, where $a=2$, $b=3$, $c=4$, $d=5$:", 14, gap=6)
    rows = [
        (r"\blu{b}\org{d}", r"3\times5=15", "the bottom: every bar cut into b times d squares"),
        (r"\blu{a}\org{d}", r"2\times5=10", "the first fraction re-cut: a columns of d squares"),
        (r"\blu{b}\org{c}", r"3\times4=12", "the second fraction re-cut: c rows of b squares"),
    ]
    for a, b, why in rows:
        y = f.reserve(44)
        pg = f.pg
        pg.eq(L + 30, y, a, 22)
        pg.eq(L + 85, y, b, 22)
        pg.note(L + 210, y + 2, why, C.RED, 16, w=280)
    f.p("So the formula just says: {b:multiply to re-cut both bars into matching pieces, then add the "
        "tops}. The formula always works, but it doesn't always give the smallest numbers.", 14,
        gap=14)
    f.p("{R:Slide error alert.}  On the Lecture 1 slide for {B:taking away}, the formula is printed "
        "with a {R:+} sign where there should be a minus. The correct version is:", 13.5, gap=6)
    f.eq(r"\frac{a}{b}-\frac{c}{d}=\frac{ad\red{\,-\,}bc}{bd}", 30, gap=6)
    ch.formula(r"\frac{a}{b}-\frac{c}{d}=\frac{ad-bc}{bd}", "subtracting fractions")
    f.p("Everything else is the same: re-cut, then take the tops away.", 13.5, gap=12)
    f.p("{b:Taking away, in tiny steps:}  $\\frac{4}{5}-\\frac{2}{3}$", 14, gap=4)
    step(f, r"=\frac{4\org{\times3}}{5\org{\times3}}-\frac{2\pur{\times5}}{3\pur{\times5}}",
         "re-cut both into fifteenths")
    step(f, r"=\frac{12}{15}-\frac{10}{15}", "12 squares, take away 10 squares")
    step(f, r"=\grn{\frac{2}{15}}", "2 squares left")
    ch.check(Fr(4, 5) - Fr(2, 3), Fr(2, 15))


def lcm_shortcut(ch):
    f = flow(ch)
    heading(f, "A shortcut: re-cut as little as possible")
    f.p("Lecture 1 also adds  $\\frac{1}{2}+\\frac{3}{4}$. The formula works, but look: a half can "
        "already be cut into quarters. You don't need to cut into eighths.", 14, gap=10)
    y = f.reserve(40)
    pg = f.pg
    pg.text(L, y + 2, "Route 1: the formula (b x d = 8)", 14, C.GREY, F.BOLD)
    pg.text(L + 280, y + 2, "Route 2: use the LCM (4)", 14, C.GREEN, F.BOLD)
    left = [r"\frac{1\times4}{2\times4}+\frac{3\times2}{4\times2}", r"=\frac{4}{8}+\frac{6}{8}",
            r"=\frac{10}{8}", r"=\frac{5}{4}"]
    right = [r"\frac{1\org{\times2}}{2\org{\times2}}+\frac{3}{4}", r"=\frac{2}{4}+\frac{3}{4}",
             r"=\frac{5}{4}", ""]
    notes_r = ["only the half needs re-cutting", "quarters + quarters", "done: already simplest", ""]
    for a, b, n in zip(left, right, notes_r):
        y = f.reserve(48)
        pg = f.pg
        pg.eq(L + 10, y, a, 19, C.GREY)
        if b:
            pg.eq(L + 280, y, b, 19)
            pg.note(L + 400, y + 2, n, C.GREEN, 14, w=100)
    pg.note(L + 150, y + 4, "then simplify\n(divide by 2)", C.GREY, 14)
    ch.check(Fr(1, 2) + Fr(3, 4), Fr(5, 4))
    f.p("Same answer, $\\frac{5}{4}$ (which is $1\\tfrac14$), but route 2 used smaller numbers and "
        "didn't need simplifying at the end.", 14, gap=8)
    f.p("{b:How to find the smallest matching piece size:} list the multiples (times table) of each "
        "bottom number and find the first one they share. That is the LCM from Chapter 1.", 14, gap=6)
    y = f.reserve(60)
    pg = f.pg
    pg.rich(L + 20, y, "Multiples of 4:   4,  8,  {G:12},  16,  20, ...", 400, 13.5)
    pg.rich(L + 20, y + 24, "Multiples of 6:   6,  {G:12},  18,  24, ...", 400, 13.5)
    pg.note(360, y + 8, "12 is the first one\nin both lists", C.GREEN, 16)
    f.p("So to work out $\\frac{3}{4}+\\frac{1}{6}$, re-cut everything into twelfths:", 14, gap=4)
    step(f, r"\frac{3\org{\times3}}{4\org{\times3}}+\frac{1\pur{\times2}}{6\pur{\times2}}",
         "4 goes into 12 three times;\n6 goes into 12 two times")
    step(f, r"=\frac{9}{12}+\frac{2}{12}=\grn{\frac{11}{12}}", "add the tops")
    ch.check(Fr(3, 4) + Fr(1, 6), Fr(11, 12))
    f.p("{h:Either route is correct.} If finding the LCM feels like too much, just multiply the "
        "bottoms and simplify at the end. You will still get the right answer.", 13, C.BROWN)


def multiply(ch):
    f = flow(ch)
    heading(f, "Multiplying: a fraction OF a fraction")
    f.p("In fractions, {B:\"times\" means \"of\"}. Three times two means \"three lots of two\". So "
        "$\\frac{2}{3}\\times\\frac{4}{5}$ means {B:\"two thirds OF four fifths\"}. Let's draw it.", 14,
        gap=10)
    y = f.reserve(150)
    pg = f.pg
    labels = [("1. Start with 4/5 of a bar\n(4 of 5 rows).", lambda c, r: C.LIGHT[C.ORANGE] if r < 4 else None),
              ("2. Now take 2/3 OF that:\ncut into 3 columns, keep 2.",
               lambda c, r: (C.GREEN if c < 2 and r < 4 else C.LIGHT[C.ORANGE] if r < 4 else None))]
    for i, (lab, fn) in enumerate(labels):
        x0 = 70 + i * 250
        grid(pg, x0, y + 6, 140, 100, 3 if i else 1, 5, fn, 0.8, vcol=C.GREEN, hcol=CHOC)
        pg.note(x0, y + 110, lab, C.INK, 15)
    pg.arrow(225, y + 55, 305, y + 55, C.GREY, 1.4)
    f.p("The dark green squares are \"two thirds of four fifths\". Count them: {G:8} squares. The whole "
        "bar is 3 x 5 = {B:15} squares. So:", 14, gap=4)
    f.eq(r"\frac{2}{3}\times\frac{4}{5}=\frac{\grn{8}}{\blu{15}}", 32, gap=6)
    ch.check(Fr(2, 3) * Fr(4, 5), Fr(8, 15))
    f.p("Look where 8 and 15 came from: 8 = 2 x 4 (the tops), 15 = 3 x 5 (the bottoms). "
        "The rule for multiplying is the {B:easiest rule of all}:", 14, gap=4)
    f.eq(r"\frac{\blu{a}}{\blu{b}}\times\frac{\org{c}}{\org{d}}=\frac{\blu{a}\times\org{c}}{\blu{b}\times\org{d}}", 30, gap=4)
    ch.formula(r"\frac{a}{b}\times\frac{c}{d}=\frac{ac}{bd}", "multiplying fractions")
    f.p("{B:top times top, bottom times bottom.}  No re-cutting needed.", 14, C.BLUE, gap=10)
    f.p("{G:Sense check:} taking part {B:of} something gives you less of it. $\\frac{8}{15}$ is "
        "smaller than $\\frac{4}{5}$ (which is $\\frac{12}{15}$). ✓", 13.5, gap=10)
    f.p("{b:A whole number times a fraction.} Write the whole number as a fraction over 1 "
        "(3 is \"3 wholes\", $\\frac{3}{1}$):", 14, gap=4)
    step(f, r"3\times\frac{2}{5}=\frac{\org{3}}{\org{1}}\times\frac{2}{5}", "3 wholes = 3 over 1")
    step(f, r"=\frac{3\times2}{1\times5}=\frac{6}{5}=\grn{1\tfrac{1}{5}}", "top x top, bottom x bottom")
    ch.check(3 * Fr(2, 5), Fr(6, 5))


def multiply2(ch):
    f = flow(ch)
    heading(f, "Cancelling first (optional, but saves effort)")
    f.p("Sometimes multiplying gives big numbers that need simplifying. Take "
        "$\\frac{3}{4}\\times\\frac{2}{9}$.", 14, gap=6)
    y = f.reserve(30)
    pg = f.pg
    pg.text(L, y, "The long way", 14, C.GREY, F.BOLD)
    step(f, r"\frac{3}{4}\times\frac{2}{9}=\frac{3\times2}{4\times9}=\frac{6}{36}", "multiply straight away")
    step(f, r"\frac{6}{36}=\frac{6\div6}{36\div6}=\grn{\frac{1}{6}}", "then simplify (HCF of 6 and 36 is 6)")
    ch.check(Fr(3, 4) * Fr(2, 9), Fr(1, 6))
    y = f.reserve(30)
    pg = f.pg
    pg.text(L, y, "The short way: simplify before multiplying", 14, C.GREEN, F.BOLD)
    f.p("Because everything on top gets multiplied together and everything on the bottom gets "
        "multiplied together, you may divide {B:any top number} and {B:any bottom number} by the same "
        "thing, even if they're in different fractions:", 13.5, gap=6)
    step(f, r"\frac{\cancel{3}^{\,1}}{\cancel{4}_{\,2}}\times\frac{\cancel{2}^{\,1}}{\cancel{9}_{\,3}}",
         "3 (top) and 9 (bottom) both divide by 3;\n2 (top) and 4 (bottom) both divide by 2", size=26)
    step(f, r"=\frac{1\times1}{2\times3}=\grn{\frac{1}{6}}", "much smaller numbers, same answer")
    f.gap(6)
    f.p("{R:Only across a times sign!}  You can cancel like this when fractions are {B:multiplied}. "
        "You can {R:never} do it when they are added or taken away. (Chapter 13 shows why, with "
        "numbers you can test.)", 13.5)


def divide(ch):
    f = flow(ch)
    heading(f, "Dividing: how many fit?")
    f.p("Division asks {B:\"how many of these fit into that?\"}  $12\\div3$ asks \"how many 3s fit "
        "into 12?\" (answer: 4). So $3\\div\\frac{1}{4}$ asks: {B:how many quarter-pieces fit into 3 "
        "bars?}", 14, gap=8)
    y = f.reserve(70)
    pg = f.pg
    for b in range(3):
        bar(pg, 60 + b * 160, y + 6, 140, 40, 4, have=4, light=C.LIGHT[C.TEAL], color=C.TEAL)
        for i in range(4):
            pg.text(60 + b * 160 + 17.5 + i * 35, y + 17, str(b * 4 + i + 1), 12, C.TEAL, F.BOLD,
                    align="center")
    f.p("Count the pieces: {G:12}. So  $3\\div\\frac{1}{4}=12$. Dividing by a quarter gave a "
        "{B:bigger} answer! That makes sense: quarters are small, so lots of them fit.", 14, gap=6)
    ch.check(3 / Fr(1, 4), 12)
    f.p("Notice: each bar holds 4 quarters, so 3 bars hold 3 x 4. {B:Dividing by $\\frac{1}{4}$ "
        "gave the same answer as multiplying by 4.} The fraction got flipped upside down: "
        "$\\frac{1}{4}$ became $\\frac{4}{1}$ (which is 4).", 14, gap=10)
    f.p("That upside-down version has a name: the {B:reciprocal}. To find a reciprocal, "
        "{B:flip the fraction over}: top goes to the bottom, bottom goes to the top.", 14, gap=6)
    y = f.reserve(96)
    pg = f.pg
    pairs = [(r"\frac{\blu{2}}{\org{3}}", r"\frac{\org{3}}{\blu{2}}", ""),
             (r"\frac{\blu{4}}{\org{5}}", r"\frac{\org{5}}{\blu{4}}", ""),
             (r"4=\frac{\blu{4}}{\org{1}}", r"\frac{\org{1}}{\blu{4}}", "a whole number is secretly over 1")]
    for i, (a_, b_, n_) in enumerate(pairs):
        x0 = L + 10 + i * 165
        pg.rect(x0, y + 4, 150, 64, C.TEAL, 1.2, fillcolor=C.LIGHT[C.TEAL], r=10)
        pg.eq(x0 + (38 if i < 2 else 44), y + 36, a_, 20, align="center", valign="middle")
        pg.eq(x0 + 122, y + 36, b_, 20, align="center", valign="middle")
        pg.arrow(x0 + (60 if i < 2 else 84), y + 22, x0 + 104, y + 22, C.RED, 1.2, bend=-0.5, head=4)
        pg.text(x0 + (60 if i < 2 else 80), y + 50, "flip", 10, C.RED, F.BOLD, w=(44 if i < 2 else 26), align="center")
        if n_:
            pg.note(x0 + 4, y + 70, n_, C.GREY, 13, w=150)
    f.p("{G:Check:} a number times its reciprocal is always 1, because everything cancels: "
        "$\\frac23 \\times \\frac32 = \\frac66 = 1$ and $4 \\times \\frac14 = 1$. "
        "(Chapter 9 uses this: $2^{-3}$ means the reciprocal of $2^3$.)", 13.5, gap=10)
    ch.check(Fr(2, 3) * Fr(3, 2), 1)
    ch.term("reciprocal", "a fraction flipped upside down: the reciprocal of 4/5 is 5/4, of 4 (= 4/1) is 1/4")
    f.need(330)
    f.p("{b:But what if the piece isn't one quarter?} Try $2\\div\\frac34$: {B:how many three-quarter "
        "pieces fit into 2 bars?} Cut both bars into quarters first:", 14, gap=8)

    def two_bars(y0):
        for b in range(2):
            bar(pg, 60 + b * 160, y0, 140, 40, 4, have=4, light=C.LIGHT[C.TEAL], color=C.TEAL)
            for i in range(4):
                pg.text(60 + b * 160 + 17.5 + i * 35, y0 + 11, str(b * 4 + i + 1), 12, C.TEAL, F.BOLD,
                        align="center")

    def px(k):
        return 60 + (k // 4) * 160 + (k % 4) * 35

    y = f.reserve(58)
    pg = f.pg
    two_bars(y + 6)
    pg.note(390, y + 12, "8 quarters", C.TEAL, 16)
    go(f, "Ring groups of 3 quarters (each group is one 3/4-piece). How many whole groups? "
          "Then: what fraction of a group is left over?")
    y = f.reserve(108)
    pg = f.pg
    two_bars(y + 10)
    for g, (k0, k1, col, lab) in enumerate([(0, 2, C.GREEN, "group 1"), (3, 5, C.PURPLE, "group 2")]):
        pg.rect(px(k0) + 3, y + 4, px(k1) + 35 - px(k0) - 6, 52, col, 2.0, r=10)
        pg.text((px(k0) + px(k1) + 35) / 2, y + 60, lab, 11, col, F.BOLD, align="center")
    pg.rect(px(6) + 3, y + 4, 35 * 3 - 6, 52, C.ORANGE, 2.0, r=10, dash=(5, 3))
    pg.rect(px(6) + 70 + 1.2, y + 11.2, 35 - 2.4, 40 - 2.4, C.ORANGE, 1.0, r=2, dash=(3, 2))
    pg.text(px(6) + 87, y + 22, "?", 13, C.ORANGE, F.BOLD, align="center")
    pg.note(px(6) - 20, y + 60, "only 2 of the 3 needed:\n2/3 of a group", C.ORANGE, 14)
    ch.check(8 // 3, 2)
    ch.check(Fr(8 % 3, 3), Fr(2, 3))
    f.p("Two whole groups, plus $\\frac23$ of a group: $2\\div\\frac34 = 2\\frac23 = \\frac83$.", 14, gap=6)
    ch.check(2 / Fr(3, 4), Fr(8, 3))
    f.p("{b:Why that's the flip.} Look at what you did. Cutting into quarters {B:multiplied by 4} "
        "(2 bars became 8 pieces). Ringing threes {B:divided by 3} (8 pieces made $\\frac83$ groups). "
        "So dividing by $\\frac34$ is the same as $\\times 4$ then $\\div 3$, which is $\\times\\frac43$: the "
        "reciprocal.", 14, gap=6)
    step(f, r"2\div\frac34=2\times\frac43=\frac83", "cut into 4s, then group in 3s")
    ch.check(2 * Fr(4, 3), Fr(8, 3))
    f.p("{B:The division rule:} to divide by a fraction, {B:multiply by its reciprocal} "
        "(\"flip the second one and multiply\").", 15, C.BLUE, gap=6)
    f.eq(r"\frac{a}{b}\div\frac{\org{c}}{\org{d}}=\frac{a}{b}\times\frac{\org{d}}{\org{c}}", 30, gap=10)
    ch.formula(r"\frac{a}{b}\div\frac{c}{d}=\frac{a}{b}\times\frac{d}{c}=\frac{ad}{bc}", "dividing fractions")
    f.need(120)
    f.p("{b:The lecture example:}  $\\frac{2}{3}\\div\\frac{4}{5}$", 14, gap=4)
    step(f, r"\frac{2}{3}\div\frac{4}{5}", "how many 4/5-pieces fit into 2/3?")
    step(f, r"=\frac{2}{3}\org{\times}\frac{\org{5}}{\org{4}}", "flip the SECOND fraction,\nchange ÷ into ×")
    step(f, r"=\frac{2\times5}{3\times4}=\frac{10}{12}", "top x top, bottom x bottom")
    step(f, r"=\grn{\frac{5}{6}}", "simplify: divide top and bottom by 2")
    ch.check(Fr(2, 3) / Fr(4, 5), Fr(5, 6))
    f.p("{G:Sense check:} $\\frac45$ is bigger than $\\frac23$, so a whole $\\frac45$ can't fit "
        "into $\\frac23$. The answer should be {B:less than 1}. It is: $\\frac56$ of a piece fits. ✓",
        13.5, gap=6)
    f.p("{R:Flip only the second fraction}, the one you are dividing {B:by}. Flipping the first one "
        "gives a wrong answer.", 13.5)


def compare(ch):
    f = flow(ch)
    heading(f, "Which is bigger?  9/17  or  49/97")
    f.p("Lecture 1 asks this. The numbers are awkward, so let's think instead of calculating.", 14,
        gap=8)
    f.p("{b:Idea 1: compare each one with a half.} Half of 17 is 8.5. So 9 out of 17 is {B:just over} a "
        "half: 0.5 of a piece over. Half of 97 is 48.5, so 49 out of 97 is {B:also} 0.5 of a piece over "
        "half.", 14, gap=6)
    y = f.reserve(110)
    pg = f.pg
    bar(pg, 70, y + 6, 408, 34, 17, have=9, light=C.LIGHT[C.BLUE], color=C.BLUE, lw=0.8)
    pg.line(70 + 204, y, 70 + 204, y + 46, C.RED, 1.8)
    pg.note(485, y + 8, "9/17", C.BLUE, 17)
    xs = 70
    pg.rect(xs, y + 60, 408, 34, CHOC, 1.4, r=2)
    pg.rect(xs + 1, y + 61, 408 * 49 / 97 - 1, 32, C.ORANGE, 0, fillcolor=C.LIGHT[C.ORANGE])
    for k in range(1, 97):
        pg.line(xs + 408 * k / 97, y + 60, xs + 408 * k / 97, y + 94, "#c9a877", 0.3)
    pg.line(70 + 204, y + 54, 70 + 204, y + 100, C.RED, 1.8)
    pg.note(485, y + 62, "49/97", C.ORANGE, 17)
    pg.note(280, y + 36, "halfway", C.RED, 14)
    f.p("Both are half a piece over halfway, but a piece of a 17-piece bar is {B:much bigger} than a "
        "piece of a 97-piece bar. So $\\frac{9}{17}$ is further over halfway: {G:$\\frac{9}{17}$ is "
        "bigger}.", 14, gap=12)
    ch.check_true(Fr(9, 17) > Fr(49, 97))
    f.p("{b:Idea 2: cross-multiply} (a reliable method that always works).", 14, gap=4)
    step(f, r"\frac{\blu{9}}{\org{17}}\quad ?\quad \frac{\pur{49}}{\grn{97}}", "which side is bigger?")
    step(f, r"\blu{9}\times\grn{97}=873\qquad \pur{49}\times\org{17}=833", "multiply each top by the\nOTHER bottom")
    step(f, r"873>833\ \text{so}\ \frac{9}{17}>\frac{49}{97}", "bigger number = bigger fraction")
    ch.check(9 * 97, 873)
    ch.check(49 * 17, 833)
    f.p("{h:Why this works:} it is secretly re-cutting both bars into $17\\times97 = 1649$ pieces, "
        "just like adding. $\\frac{9}{17}$ becomes 873 of those pieces and $\\frac{49}{97}$ becomes 833. "
        "Then you only compare the tops.", 13, C.BROWN)
    ch.check(Fr(9, 17), Fr(873, 1649))


def mixed_ops(ch):
    f = flow(ch)
    heading(f, "Adding mixed numbers:  1½ + 2¾")
    f.p("Mixed numbers are easiest if you turn them into improper fractions first, then use the "
        "rules you already know. One change per line:", 14, gap=8)
    step(f, r"1\tfrac{1}{2}+2\tfrac{3}{4}", "mixed numbers: change them first")
    step(f, r"=\frac{\org{3}}{2}+\frac{\org{11}}{4}", "1 bar = 2 halves, +1 = 3 halves;\n2 bars = 8 quarters, +3 = 11 quarters")
    step(f, r"=\frac{3\pur{\times2}}{2\pur{\times2}}+\frac{11}{4}", "re-cut the halves into quarters")
    step(f, r"=\frac{6}{4}+\frac{11}{4}", "")
    step(f, r"=\frac{17}{4}", "add the tops")
    step(f, r"=\grn{4\tfrac{1}{4}}", "17 ÷ 4 = 4 remainder 1")
    ch.check(1 + Fr(1, 2) + 2 + Fr(3, 4), Fr(17, 4))
    f.p("{G:Sense check:} a bit more than 1, plus a bit less than 3, is roughly 4. ✓", 13.5, gap=14)
    f.p("{h:Another route:} add the whole bars (1 + 2 = 3) and the pieces separately "
        "($\\frac12+\\frac34 = \\frac54 = 1\\tfrac14$), then put them together: $3 + 1\\tfrac14 = "
        "4\\tfrac14$. Also fine!", 13, C.BROWN, gap=14)
    heading(f, "Fractions or decimals?")
    f.p("Your Lecture 1 slides make a point worth remembering. $\\frac{1}{3}$ as a decimal is "
        "0.33333... going on forever, so any decimal you write down is slightly wrong. In "
        "algebra and exact working, {B:keep fractions}. When you're dealing with measured data "
        "(statistics, lab results), decimals are fine. Chapter 3 is all about decimals.", 13.5)


def your_turn(ch):
    f = flow(ch)
    f.new_page()
    heading(f, "Your turn: shade the bars")
    f.p("Each puzzle has empty bars. Use Xournal's {b:highlighter} or pen to shade the pieces, then "
        "write the answer in the space. Answers, fully worked, are on the next page. {h:Don't peek "
        "until you've tried!}", 13.5, gap=10)
    puzzles = [
        ("1.  Shade 2/5. Then shade 2/5 on the second bar, re-cut into tenths. What is 2/5 in tenths?",
         [(5, 1), (10, 1)]),
        ("2.  Simplify 10/15. (Hint: which number divides 10 and 15?)", [(15, 1)]),
        ("3.  Write 9/4 as a mixed number.", [(4, 1), (4, 1), (4, 1)]),
        ("4.  Work out 1/4 + 1/3. Re-cut both bars into twelfths.", [(12, 1), (12, 1)]),
        ("5.  Work out 1/2 of 3/4 (that is, 1/2 x 3/4).", [(4, 2)]),
        ("6.  How many sixths fit into 2 bars? (That is, 2 ÷ 1/6.)", [(6, 1), (6, 1)]),
    ]
    for q, bars in puzzles:
        qh = f.pg.rich_h(q, W, 13.5)
        need = qh + 8 + 42 * (1 if len(bars) > 1 and bars[0][1] == 1 else len(bars)) + 26
        y = f.reserve(need + 34)
        pg = f.pg
        pg.rich(L, y, q, W, 13.5)
        by = y + qh + 8
        bx = L + 20
        for n, rows in bars:
            bw = 130 if len(bars) > 1 else 220
            bar(pg, bx, by, bw, 34 * rows if rows > 1 else 34, n, rows=rows)
            bx += bw + 20
        pg.note(L + 20, by + (34 * bars[0][1]) + 6, "answer:", C.GREY, 16)
        pg.line(L + 80, by + (34 * bars[0][1]) + 26, L + 260, by + (34 * bars[0][1]) + 26, "#bbbbbb", 0.8)


def answers(ch):
    f = flow(ch)
    f.new_page()
    heading(f, "Answers, worked")
    ans = [
        ("1.", r"\frac{2}{5}=\frac{2\times2}{5\times2}=\grn{\frac{4}{10}}",
         "cut every fifth in half: twice as many pieces AND twice as many shaded"),
        ("2.", r"\frac{10}{15}=\frac{10\div5}{15\div5}=\grn{\frac{2}{3}}",
         "5 divides both (the HCF of 10 and 15)"),
        ("3.", r"9\div4=2\ \text{r}\ 1,\ \text{so}\ \frac{9}{4}=\grn{2\tfrac{1}{4}}",
         "two full bars of 4 quarters, one quarter left"),
        ("4.", r"\frac{1\times3}{4\times3}+\frac{1\times4}{3\times4}=\frac{3}{12}+\frac{4}{12}=\grn{\frac{7}{12}}",
         "12 is the LCM of 4 and 3"),
        ("5.", r"\frac{1}{2}\times\frac{3}{4}=\frac{1\times3}{2\times4}=\grn{\frac{3}{8}}",
         "half of 3 quarters: cut each quarter in half, keep 3 of the 8 small pieces"),
        ("6.", r"2\div\frac{1}{6}=2\times\frac{6}{1}=\grn{12}", "each bar holds 6 sixths, 2 bars hold 12"),
    ]
    ch.check(Fr(2, 5), Fr(4, 10))
    ch.check(Fr(10, 15), Fr(2, 3))
    ch.check(Fr(9, 4), 2 + Fr(1, 4))
    ch.check(Fr(1, 4) + Fr(1, 3), Fr(7, 12))
    ch.check(Fr(1, 2) * Fr(3, 4), Fr(3, 8))
    ch.check(2 / Fr(1, 6), 12)
    for n, lat, why in ans:
        w, h, _ = f.pg.eq_size(lat, 20)
        y = f.reserve(h + 32)
        pg = f.pg
        pg.text(L, y + h / 2 - 9, n, 15, CHOC, F.BOLD)
        pg.eq(L + 28, y, lat, 20)
        pg.note(L + 28, y + h + 2, why, C.RED, 15)
    f.gap(10)
    f.p("{b:Got one wrong?} Find the page with the matching picture (equivalent fractions, "
        "simplifying, improper fractions, adding, multiplying, dividing) and redraw the bars for your "
        "puzzle. The picture will show you where the step went wrong.", 13.5)


def wrapper(ch):
    """Closing page: the chocolate wrapper, with the four rules printed on it."""
    pg = ch.new_page(bg="#fbf5ee")
    pg.rect(40, 40, 515, 730, CHOC, 3, fillcolor="#6b3f1f", r=18)
    pg.rect(58, 58, 479, 694, "#e6c9a3", 1.5, r=12, dash=(6, 4))
    pg.text(297, 78, "THE FRACTION BAR", 26, "#f6e3c6", F.BOLD, align="center")
    pg.note(297, 112, "ingredients: everything in this chapter", "#e6c9a3", 19, align="center")
    rules = [
        ("SAME AMOUNT", r"\frac{1}{2}=\frac{1\times3}{2\times3}=\frac{3}{6}",
         "times (or divide) top AND bottom by the same number"),
        ("ADD / TAKE AWAY", r"\frac{1}{2}+\frac{1}{3}=\frac{3}{6}+\frac{2}{6}=\frac{5}{6}",
         "re-cut into matching pieces first, then add the tops"),
        ("MULTIPLY", r"\frac{2}{3}\times\frac{4}{5}=\frac{8}{15}",
         "top x top, bottom x bottom (\"of\")"),
        ("DIVIDE", r"\frac{2}{3}\div\frac{4}{5}=\frac{2}{3}\times\frac{5}{4}=\frac{5}{6}",
         "flip the second fraction, then multiply"),
    ]
    y = 160
    for head, lat, say in rules:
        pg.rect(80, y, 435, 132, "#f6e3c6", 1.2, fillcolor="#fbf1e2", r=10)
        pg.text(100, y + 12, head, 14, CHOC, F.BOLD)
        pg.eq(297, y + 36, lat, 24, align="center")
        pg.note(297, y + 96, say, C.RED, 18, align="center")
        y += 145
    pg.note(297, 745 - 12, "never add the bottoms!", "#ffd9a0", 20, align="center")


def build(ch):
    title_page(ch)
    what_is(ch)
    fraction_is_division(ch)
    equivalent(ch)
    simplify(ch)
    improper(ch)
    add_same(ch)
    add_different(ch)
    lecture_add(ch)
    formula_page(ch)
    lcm_shortcut(ch)
    multiply(ch)
    multiply2(ch)
    divide(ch)
    compare(ch)
    mixed_ops(ch)
    your_turn(ch)
    answers(ch)
    wrapper(ch)
