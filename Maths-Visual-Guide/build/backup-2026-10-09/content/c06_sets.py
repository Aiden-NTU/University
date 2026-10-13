"""Chapter 6 - Sets. A sock drawer, two playlists, hula hoops on the floor, set-builder notation
decoded word by word, and nesting dolls for the families of numbers."""
import math

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 6
NUM = 6
TITLE = "Sets"
SHORT = "Sets"
SLUG = "Sets"
ACCENT = C.ORANGE
REQUIRES = ["reading-maths", "inequality-symbols", "fraction", "negative-numbers", "recurring-decimals",
            "decimal-point", "addition", "subtraction"]
INTRODUCES = ["set", "element", "set-notation", "union", "intersection", "complement", "set-difference",
              "venn-diagram", "subset", "empty-set", "set-builder", "interval-notation", "number-sets",
              "irrational-numbers"]

HOOP_A = C.PINK
HOOP_B = C.TEAL
FILL_A = "#f6c9dc"
FILL_B = "#bfe6ea"
FILL = "#ffd98a"
PAPER = "#fffefb"


def icon(pg, x, y):
    pg.circle(x + 6, y + 9, 6, HOOP_A, 1.6)
    pg.circle(x + 12, y + 9, 6, HOOP_B, 1.6)


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def region(pg, circles, pred, box, color, step=2.0, width=2.3):
    """Fill the part of `box` where pred(inside_1, inside_2, ...) is true, with scan lines."""
    x0, y0, x1, y1 = box
    y = y0 + step / 2
    while y < y1:
        bps = {x0, x1}
        for cx, cy, r in circles:
            dy = y - cy
            if abs(dy) < r:
                dx = math.sqrt(r * r - dy * dy)
                bps.update((cx - dx, cx + dx))
        bps = sorted(b for b in bps if x0 <= b <= x1)
        for a, b in zip(bps, bps[1:]):
            m = (a + b) / 2
            ins = [(m - cx) ** 2 + (y - cy) ** 2 < r * r for cx, cy, r in circles]
            if pred(*ins) and b - a > 0.3:
                pg.line(a, y, b, y, color, width, layer=C.UNDER)
        y += step


def venn(pg, x, y, w, h, pred=None, color=FILL, la="A", lb="B", u=True, r=None):
    """Universal box with two hoops. Returns the two circles."""
    r = r or min(h * 0.36, w * 0.24)
    ca = (x + w / 2 - r * 0.6, y + h / 2, r)
    cb = (x + w / 2 + r * 0.6, y + h / 2, r)
    if pred:
        region(pg, [ca, cb], pred, (x + 1, y + 1, x + w - 1, y + h - 1), color)
    if u:
        pg.rect(x, y, w, h, C.INK, 1.1)
        pg.text(x + 5, y + 3, "ξ", 11, C.GREY, F.BOLD, solid=False)
    pg.circle(*ca, HOOP_A, 2.2)
    pg.circle(*cb, HOOP_B, 2.2)
    pg.text(ca[0] - r * 0.75, y + h / 2 - r - 2, la, 12, HOOP_A, F.BOLD, solid=False)
    pg.text(cb[0] + r * 0.6, y + h / 2 - r - 2, lb, 12, HOOP_B, F.BOLD, solid=False)
    return ca, cb


def sock(pg, x, y, col, s=1.0):
    pts = [(x, y), (x + 10 * s, y), (x + 10 * s, y + 18 * s), (x + 20 * s, y + 24 * s), (x + 18 * s, y + 31 * s),
           (x + 2 * s, y + 26 * s), (x, y + 22 * s)]
    pg.fillpoly(pts, col, outline=C.INK, width=0.8, layer=C.MAIN)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 6, "Sets", "collections of things, drawn as hula hoops on the floor",
                     C.ORANGE, PAPER)
    ca, cb = venn(pg, L + 60, 200, 380, 190, lambda a, b: a and b, la="my playlist", lb="friend's playlist")
    pg.note(ca[0] - 70, ca[1] - 30, "Song 1\nSong 4", HOOP_A, 17)
    pg.note(cb[0] + 20, cb[1] - 30, "Song 7\nSong 9", HOOP_B, 17)
    pg.note((ca[0] + cb[0]) / 2 - 22, ca[1] - 18, "Song 2", C.BROWN, 17)
    pg.note(L + 70, 360, "Song 5 (on neither)", C.GREY, 15)
    f = ch.flow(top=420)
    f.p("A {B:set} is just a collection of things. That's all. Your sock drawer is a set of socks; "
        "a playlist is a set of songs. Sets give us a tidy way to talk about {o:groups}, {o:what's in "
        "both groups}, {o:what's in either} and {o:what's left out}.", 14, gap=10)
    f.p("Your Lecture 13 uses sets to describe the kinds of numbers (natural, integer, rational, "
        "real) and the inputs a function accepts (Chapter 18). This chapter decodes every symbol, "
        "including the scary-looking $\\{x \\mid 1 \\le x \\le 4\\}$.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 13} {y:(types of numbers, sets, domains).}", 12.5)


def what_is(ch):
    f = flow(ch)
    sec(f, "A set is a sock drawer")
    f.p("Open the drawer: a red sock, a blue sock and a green sock. Write the set with {B:curly "
        "brackets} (called {B:braces}) and commas:", 14, gap=8)
    y = f.reserve(70)
    pg = f.pg
    pg.rect(L + 20, y, 150, 60, C.BROWN, 1.5, fillcolor="#f3e6d3", r=4)
    for i, col in enumerate(["#e57373", "#64b5f6", "#81c784"]):
        sock(pg, L + 34 + i * 44, y + 14, col)
    pg.eq(L + 200, y + 10, r"S=\{\text{red},\ \text{blue},\ \text{green}\}", 20)
    pg.note(L + 200, y + 40, "S is the set's name; each sock is an element", C.RED, 15)
    ch.symbol(r"\{\ \}", "the set of / braces", "curly brackets that hold the members of a set")
    ch.term("set", "a collection of distinct things, written inside curly brackets { }")
    ch.term("element (member)", "one of the things in a set")
    f.p("{b:Two rules make a set different from a list:}", 14, gap=6)
    y = f.reserve(90)
    pg = f.pg
    pg.eq(L + 30, y, r"\{\text{red},\text{blue},\text{green}\}=\{\text{green},\text{red},\text{blue}\}", 17)
    pg.note(L + 360, y - 2, "1. order doesn't matter\n(the drawer isn't sorted)", C.PURPLE, 15)
    pg.eq(L + 30, y + 48, r"\{\text{red},\text{red},\text{blue}\}=\{\text{red},\text{blue}\}", 17)
    pg.note(L + 360, y + 46, "2. repeats don't count\n(\"is red in there?\" yes)", C.PURPLE, 15)
    f.p("{b:Is it in the drawer?} The symbol $\\in$ (a curly E, for \"element\") means \"is in\"; "
        "with a slash, $\\notin$ means \"is not in\":", 14, gap=6)
    y = f.reserve(40)
    pg = f.pg
    pg.eq(L + 30, y, r"\text{blue}\in S", 20, C.GREEN)
    pg.note(L + 130, y, "\"blue is in S\" (true)", C.GREEN, 15)
    pg.eq(L + 280, y, r"\text{pink}\notin S", 20, C.RED)
    pg.note(L + 390, y, "\"pink is not in S\"", C.RED, 15)
    ch.symbol(r"\in", "is an element of / is in", "x ∈ A means x belongs to set A")
    ch.symbol(r"\notin", "is not an element of", "x ∉ A means x is not in A")
    f.p("Sets can hold numbers too: $A = \\{2, 4, 6, 8\\}$ is the set of even numbers from 2 to 8, "
        "and $3 \\notin A$. The number of elements is written $n(A)$; here $n(A) = 4$.", 14)
    ch.symbol(r"n(A)", "n of A / the size of A", "how many elements are in set A")


def playlists(ch):
    f = flow(ch)
    sec(f, "Two playlists: in both, in either, only in one", room=440)
    f.p("You and a friend each have a playlist. Songs are numbered 1 to 9 in the whole music library. "
        "The whole library is called the {B:universal set} ξ (\"ksee\", a Greek letter) or U: "
        "everything we're allowed to talk about.", 14, gap=8)
    ch.term("universal set", "the set of everything under discussion, written ξ or U")
    ch.symbol(r"\xi", "ksee (or 'the universal set')", "everything being talked about")
    y = f.reserve(56)
    pg = f.pg
    pg.eq(L + 30, y, r"A=\{1,2,3,4\}", 20, HOOP_A)
    pg.eq(L + 200, y, r"B=\{2,3,7,9\}", 20, HOOP_B)
    pg.eq(L + 370, y, r"\xi=\{1,2,\dots,9\}", 18, C.GREY)
    pg.note(L + 30, y + 28, "my playlist", HOOP_A, 15)
    pg.note(L + 200, y + 28, "friend's playlist", HOOP_B, 15)
    rows = [
        (r"A\cap B=\{2,3\}", "intersection, \"A and B\"", "songs on BOTH playlists. ∩ looks like a bridge "
         "(or an upside-down cup) sitting on both.", C.ORANGE),
        (r"A\cup B=\{1,2,3,4,7,9\}", "union, \"A or B\"", "merge the playlists, no duplicates. ∪ looks like "
         "a cup that holds everything.", C.GREEN),
        (r"A-B=\{1,4\}", "difference, \"A minus B\"", "songs only on mine: take away anything your "
         "friend also has.", HOOP_A),
        (r"A'=\{5,6,7,8,9\}", "complement, \"not A\"", "everything in the library that's NOT on my "
         "playlist. (Some books write A with a bar over it.)", C.PURPLE),
    ]
    for e, name, expl, col in rows:
        y = f.reserve(58)
        pg = f.pg
        pg.eq(L + 10, y + 2, e, 17, col)
        pg.text(L + 245, y, name, 13, col, F.BOLD)
        pg.note(L + 245, y + 18, expl, C.INK, 14, w=R - L - 245)
    ch.symbol(r"\cap", "intersection / and", "elements in both sets")
    ch.symbol(r"\cup", "union / or", "elements in either set (or both)")
    ch.symbol(r"A'", "A complement / not A", "everything in ξ that is not in A")
    ch.term("intersection", "the elements that are in both sets")
    ch.term("union", "all elements in either set (or both), listed once")
    ch.term("complement", "everything in the universal set that is not in the given set")
    s_a, s_b = {1, 2, 3, 4}, {2, 3, 7, 9}
    ch.check(sorted(s_a & s_b), [2, 3])
    ch.check(sorted(s_a | s_b), [1, 2, 3, 4, 7, 9])
    ch.check(sorted(s_a - s_b), [1, 4])
    ch.check(sorted(set(range(1, 10)) - s_a), [5, 6, 7, 8, 9])
    f.p("{h:Memory hook:} ∪ is a {B:U} for {B:U}nion; ∩ is the other one. \"Or\" in maths always "
        "includes \"both\" (song 2 is in A or B, it's in both, so it counts).", 13.5, C.BROWN)


def hoops(ch):
    f = flow(ch)
    sec(f, "Hula hoops on the floor: Venn diagrams", room=460)
    f.p("Lay two hula hoops on the floor so they overlap, inside a rectangle (the whole library). "
        "Put each song where it belongs. Songs on both playlists stand in the overlap. This picture "
        "is a {B:Venn diagram}:", 14, gap=8)
    ch.term("Venn diagram", "overlapping circles inside a rectangle, showing how sets share elements")
    y = f.reserve(170)
    pg = f.pg
    ca, cb = venn(pg, L + 60, y, 370, 165)
    pg.note(ca[0] - 50, ca[1] - 22, "1   4", HOOP_A, 22)
    pg.note((ca[0] + cb[0]) / 2 - 16, ca[1] - 22, "2  3", C.BROWN, 22)
    pg.note(cb[0] + 18, cb[1] - 22, "7   9", HOOP_B, 22)
    pg.note(L + 80, y + 128, "5  6  8", C.GREY, 20)
    pg.note(L + 150, y + 136, "outside both hoops, but still in the library", C.GREY, 14)
    f.p("Each operation from the last page is a {B:region} of the floor. Shade it and read it off:",
        14, gap=8)
    y = f.reserve(260)
    pg = f.pg
    panels = [(lambda a, b: a and b, r"A\cap B", "the overlap only"),
              (lambda a, b: a or b, r"A\cup B", "anything inside a hoop"),
              (lambda a, b: a and not b, r"A-B", "A's hoop, minus the overlap"),
              (lambda a, b: not a, r"A'", "everything outside A")]
    pw, ph = 230, 100
    for i, (pred, lab, cap) in enumerate(panels):
        x = L + 10 + (i % 2) * 250
        yy = y + (i // 2) * 130
        venn(pg, x, yy, pw, ph, pred)
        pg.eq(x, yy + ph + 6, lab, 16, C.ORANGE)
        pg.note(x + 70, yy + ph + 4, cap, C.INK, 14)


def counting(ch):
    f = flow(ch)
    sec(f, "Counting with a Venn diagram: fill it from the middle", room=500)
    f.p("A survey of {B:30} students: {B:18} drink tea, {B:15} drink coffee, {B:7} drink both. How "
        "many drink neither? The trick: {R:always start with the overlap}, then work outwards.",
        14, gap=8)
    y = f.reserve(190)
    pg = f.pg
    steps_ = [("7", None, None, None, "1. both: 7 goes\nin the middle"),
              ("7", "11", None, None, "2. tea only:\n18 - 7 = 11"),
              ("7", "11", "8", None, "3. coffee only:\n15 - 7 = 8"),
              ("7", "11", "8", "4", "4. neither:\n30 - 11 - 7 - 8 = 4")]
    pw = 116
    for i, (mid, ta, co, ne, cap) in enumerate(steps_):
        x = L + i * (pw + 10)
        ca, cb = venn(pg, x, y, pw, 90, la="T", lb="C", r=28)
        pg.text((ca[0] + cb[0]) / 2, ca[1] - 8, mid, 14, C.BROWN, F.BOLD, align="center")
        if ta:
            pg.text(ca[0] - 14, ca[1] - 8, ta, 14, HOOP_A, F.BOLD, align="center")
        if co:
            pg.text(cb[0] + 14, cb[1] - 8, co, 14, HOOP_B, F.BOLD, align="center")
        if ne:
            pg.text(x + pw - 14, y + 72, ne, 14, C.GREY, F.BOLD, align="center")
        pg.note(x + 2, y + 100, cap, C.RED, 14)
    pg.note(L, y + 150, "Check: 11 + 7 + 8 + 4 = 30 students ✓      (T = tea, C = coffee)", C.GREEN, 16)
    ch.check(30 - 11 - 7 - 8, 4)
    f.p("{R:The classic mistake:} 18 + 15 = 33 is more than 30 students! That's because the 7 "
        "who drink both got counted twice, once with tea and once with coffee. The fix, as a rule:",
        14, gap=6)
    y = f.reserve(62)
    pg = f.pg
    pg.eq(L + 30, y, r"n(A\cup B)=n(A)+n(B)-n(A\cap B)", 20)
    pg.note(L + 30, y + 32, "here: 18 + 15 - 7 = 26 drink at least one", C.RED, 15)
    ch.formula(r"n(A\cup B)=n(A)+n(B)-n(A\cap B)", "counting a union (don't count the overlap twice)")
    ch.check(18 + 15 - 7, 26)


def subsets(ch):
    f = flow(ch)
    sec(f, "Subsets and the empty set", room=300)
    f.p("Every cat is an animal, so the set of cats sits {B:entirely inside} the set of animals. We "
        "say cats are a {B:subset} of animals, and draw one hoop inside another:", 14, gap=8)
    ch.term("subset", "a set whose elements are all inside another set")
    y = f.reserve(100)
    pg = f.pg
    pg.ellipse(L + 120, y + 48, 100, 46, C.GREEN, 2, fillcolor=C.LIGHT[C.GREEN])
    pg.ellipse(L + 150, y + 52, 44, 24, C.ORANGE, 2, fillcolor=C.LIGHT[C.ORANGE])
    pg.text(L + 150, y + 45, "cats", 12, C.ORANGE, F.BOLD, align="center")
    pg.text(L + 70, y + 10, "animals", 12, C.GREEN, F.BOLD)
    pg.eq(L + 260, y + 20, r"\text{Cats}\subset\text{Animals}", 20)
    pg.note(L + 260, y + 50, "⊂ reads \"is a subset of\". It looks like\na C for \"contained in\".",
            C.RED, 15)
    ch.symbol(r"\subset", "is a subset of", "every element of the left set is in the right set")
    f.p("{b:The empty set} has nothing in it at all, written $\\{\\}$ or $\\varnothing$. Your "
        "lecture's example: the set of fish that drive BMWs. It counts as a subset of {B:every} "
        "set, because it has no element that could fail to be inside.", 14)
    ch.term("empty set", "the set with no elements, written {} or ∅")
    ch.symbol(r"\varnothing", "the empty set", "a set with nothing in it")


def set_builder(ch):
    f = flow(ch)
    sec(f, "Decoding set-builder notation", room=430)
    f.p("Listing works for small sets. For big ones, maths describes the {B:rule for getting in}, "
        "like a club's entry rules. This is from your Lecture 13 slides:", 14, gap=8)
    y = f.reserve(186)
    pg = f.pg
    parts = [(r"\{", "the set\nof all", C.GREY), (r"x", "numbers x", C.BLUE), (r"\mid", "such that", C.RED),
             (r"1\le x\le4", "x is between 1 and 4,\n1 and 4 allowed", C.GREEN),
             (r",\ x\in\mathbb{Z}", "and x is a\nwhole number", C.PURPLE), (r"\}", "", C.GREY)]
    x = L + 40
    for i, (lat, say, col) in enumerate(parts):
        w, h = pg.eq(x, y + 10, lat, 28, col)
        if say:
            lv = 68 if i % 2 else 104
            pg.line(x + w / 2, y + 52, x + w / 2, y + lv - 2, col, 1)
            pg.note(x + w / 2 - 12, y + lv, say, col, 14)
        x += w + 10
    pg.note(L + 330, y + 150, "= {1, 2, 3, 4}", C.ORANGE, 20)
    ch.symbol(r"\mid", "such that", "separates the variable from the rule it must obey")
    ch.term("set-builder notation", "{x | rule}: the set of all x that obey the rule")
    f.p("{R:Why the \"x ∈ ℤ\" part matters} (it's missing on the slide): without it, the rule "
        "$1 \\le x \\le 4$ also lets in 2.5, 3.14 and every other number in between, which is an "
        "endless set, not {1, 2, 3, 4}.", 13.5, gap=10)
    f.p("{b:Intervals.} When you do want every number between two ends, there's a shorter way. The "
        "square bracket means the end is {B:included}; the round bracket means it's {B:not}:", 14, gap=8)
    ch.term("interval", "all the numbers between two end points")
    y = f.reserve(120)
    pg = f.pg
    rows = [(r"[-1,1]=\{x\mid-1\le x\le1\}", True, True), (r"(0,3)=\{x\mid 0<x<3\}", False, False),
            (r"[0,3)", True, False)]
    for i, (lat, lc, rc) in enumerate(rows):
        yy = y + i * 40
        pg.eq(L + 10, yy, lat, 17)
        x1, x2 = L + 300, L + 440
        pg.line(x1 - 20, yy + 12, x2 + 20, yy + 12, C.GREY, 1)
        pg.line(x1, yy + 12, x2, yy + 12, C.BLUE, 3)
        for xx, closed in ((x1, lc), (x2, rc)):
            if closed:
                pg.circle(xx, yy + 12, 4.5, C.BLUE, 1.4, fillcolor=C.BLUE)
            else:
                pg.circle(xx, yy + 12, 4.5, C.BLUE, 1.4, fillcolor="#ffffff")
    pg.note(L + 290, y + 114, "filled dot = end included, hollow dot = end left out", C.RED, 14)
    ch.symbol(r"[a,b]", "the closed interval from a to b", "all numbers from a to b, ends included")
    ch.symbol(r"(a,b)", "the open interval from a to b", "all numbers between a and b, ends excluded")


def dolls(ch):
    f = flow(ch)
    sec(f, "Nesting dolls: the families of numbers", room=520)
    f.p("Numbers come in families, and each family fits inside a bigger one, like Russian nesting "
        "dolls. Each has a fancy double-struck letter (from your Lecture 13):", 14, gap=8)
    y = f.reserve(292)
    pg = f.pg
    pg.rect(L, y, W, 290, C.RED, 1.6, fillcolor="#fff7f7", r=26, dash=(5, 4))
    pg.eq(L + 12, y + 8, r"\mathbb{C}", 18, C.RED)
    pg.text(L + 36, y + 11, "Complex (not in this course)", 12, C.RED, F.BOLD)
    pg.note(L + 290, y + 6, "3 + 2i, where i = √−1", C.RED, 15)
    layers = [(r"\mathbb{R}", "Real", C.PURPLE, 470, 240), (r"\mathbb{Q}", "Rational", C.BLUE, 350, 196),
              (r"\mathbb{Z}", "Integers", C.GREEN, 232, 150), (r"\mathbb{N}", "Natural", C.ORANGE, 124, 100)]
    cx, bot = L + 10, y + 282
    for lat, name, col, w, h in layers:
        x0 = cx
        pg.rect(x0, bot - h, w, h, col, 2, fillcolor=C.LIGHT[col], r=22)
        pg.eq(x0 + 12, bot - h + 8, lat, 18, col)
        pg.text(x0 + 36, bot - h + 11, name, 12, col, F.BOLD)
    pg.note(L + 30, y + 228, "1, 2, 3, ...", C.ORANGE, 16)
    pg.note(L + 150, y + 198, "0, -1, -2, -3", C.GREEN, 16)
    pg.note(L + 250, y + 148, "½, -¾, 0.25, 0.3̇", C.BLUE, 16)
    pg.note(L + 380, y + 108, "π, √2, e", C.PURPLE, 16)
    pg.note(L + 370, y + 138, "(irrational: in ℝ\nbut not in ℚ)", C.PURPLE, 14)
    ch.symbol(r"\mathbb{N}", "N, the natural numbers", "counting numbers 1, 2, 3, ...")
    ch.symbol(r"\mathbb{Z}", "Z, the integers", "whole numbers including negatives and 0")
    ch.symbol(r"\mathbb{Q}", "Q, the rational numbers", "anything that can be written as a fraction")
    ch.symbol(r"\mathbb{R}", "R, the real numbers", "every point on the number line")
    rows = [("ℕ natural", "the counting numbers 1, 2, 3, ... (some books include 0)."),
            ("ℤ integers", "whole numbers, negatives and zero too: ..., -2, -1, 0, 1, 2, ... (Z is from the "
             "German \"Zahlen\", numbers.)"),
            ("ℚ rational", "any fraction of two integers (\"ratio-nal\"; Q for quotient): ½, 6/1, 3/7, -0.25. Their decimals "
             "either stop or repeat (Chapter 3)."),
            ("ℝ real", "every point on the number line, including numbers whose decimals never stop "
             "and never repeat: π = 3.14159..., √2 = 1.41421...; these are called irrational."),
            ("ℂ complex", "the dashed outer doll. No real number squares to give a negative (2² and (−2)² are "
             "both +4), so mathematicians invented a new number {B:i} with i² = −1. Numbers like 3 + 2i are "
             "not on the number line at all, which is why your Lecture 13 defines the reals as \"any number that "
             "could be used as a distance on a line (so excludes complex numbers)\". You won't need them in "
             "this course; they turn up later in electronics and waves.")]
    for a, b in rows:
        f.p("{B:" + a + ":} " + b, 13.5, gap=6)
    ch.term("natural numbers", "the counting numbers 1, 2, 3, ... (ℕ)")
    ch.term("integers", "whole numbers including 0 and negatives (ℤ)")
    ch.term("rational number", "a number that can be written as a fraction of two integers (ℚ)")
    ch.term("real numbers", "all numbers on the number line (ℝ)")
    ch.term("irrational number", "a real number that is not a fraction; its decimals never end or repeat")
    f.p("So $\\mathbb{N} \\subset \\mathbb{Z} \\subset \\mathbb{Q} \\subset \\mathbb{R}$: each doll "
        "fits in the next. The slides write the irrationals as $\\mathbb{R} - \\mathbb{Q}$ "
        "(real minus rational), which is set difference from earlier in this chapter.", 13.5)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Hula hoops: your turn", fresh=True)
    f.p("ξ = {1, 2, ..., 10},  A = {1, 2, 3, 4, 5},  B = {2, 4, 6, 8, 10}. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Reading sets", ["Is 6 ∈ A?", "List A ∩ B", "List A ∪ B", "List A - B", "List B'", "Find n(A ∪ B)"],
         "1. no   2. {2, 4}   3. {1, 2, 3, 4, 5, 6, 8, 10}   4. {1, 3, 5}   5. {1, 3, 5, 7, 9}   6. 8"),
        ("Venn counting", ["40 people: 25 have a cat, 20 a dog, 12 both. How many have neither?",
                           "How many have a cat but no dog?"], "7. 40 - (13 + 12 + 8) = 7   8. 13"),
        ("Decoding", ["Write {x | x ∈ ℤ, -2 ≤ x < 3} as a list", "Which family is the smallest that contains -5?",
                      "Is 0.75 rational? Is √2?", "Draw [2, 5) on a number line"],
         "9. {-2, -1, 0, 1, 2}   10. ℤ   11. yes (3/4); no   12. filled dot at 2, hollow at 5"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14)
    A, B = {1, 2, 3, 4, 5}, {2, 4, 6, 8, 10}
    ch.check(sorted(A & B), [2, 4])
    ch.check(len(A | B), 8)
    ch.check(sorted(A - B), [1, 3, 5])
    ch.check(sorted(set(range(1, 11)) - B), [1, 3, 5, 7, 9])
    ch.check(40 - (13 + 12 + 8), 7)
    ch.check([x for x in range(-2, 3)], [-2, -1, 0, 1, 2])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    what_is(ch)
    playlists(ch)
    hoops(ch)
    counting(ch)
    subsets(ch)
    set_builder(ch)
    dolls(ch)
    your_turn(ch)
