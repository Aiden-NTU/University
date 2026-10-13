"""Chapter 18 - Functions. A function is a vending machine: one input in, exactly one output out.
f(x) as 'put x in the slot', Python def, the domain as the coins a machine accepts, piecewise
functions as parking charges, machines in a chain, and running a machine backwards."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, rules_table, section, step, title_block

ORDER = 18
NUM = 18
TITLE = "Functions"
SHORT = "Functions"
SLUG = "Functions"
ACCENT = C.BLUE
REQUIRES = ["letters-stand-for-numbers", "substitution", "expand-brackets", "set", "interval-notation",
            "number-sets", "roots", "reciprocal", "inverse-operations", "transpose", "powers", "undefined-denominator",
            "completing-the-square", "quadratic-equation", "simultaneous-equations", "solve-equation"]
INTRODUCES = ["function", "function-notation", "maps-to", "domain", "range-image", "many-to-one",
              "piecewise-function", "composite-function", "inverse-function", "one-to-one", "solve-f-equals-k"]

PAPER = "#fbfcff"
x, a = sp.symbols("x a")


def icon(pg, x0, y0):
    pg.rect(x0 + 3, y0 + 4, 12, 10, C.BLUE, 1.1, fillcolor=C.LIGHT[C.BLUE], r=2)
    pg.poly([(x0 + 5, y0 + 4), (x0 + 3, y0), (x0 + 15, y0), (x0 + 13, y0 + 4)], C.BLUE, 1.0)
    pg.line(x0 + 15, y0 + 11, x0 + 18, y0 + 16, C.BLUE, 1.0)


def sec(f, t, **kw):
    section(f, t, C.BLUE, icon, **kw)


def machine(pg, x0, y0, label, inp=None, out=None, w=120, h=64, col=C.BLUE, size=17, reject=None):
    """A function machine: hopper on top, rule on the front, chute bottom-right."""
    pg.poly([(x0 + w * 0.3, y0), (x0 + w * 0.22, y0 - 16), (x0 + w * 0.58, y0 - 16), (x0 + w * 0.5, y0)],
            col, 1.2)
    pg.rect(x0, y0, w, h, col, 1.5, fillcolor=C.LIGHT[col], r=8)
    pg.eq(x0 + w / 2, y0 + h / 2, label, size, col, align="center", valign="middle")
    pg.poly([(x0 + w, y0 + h - 18), (x0 + w + 18, y0 + h + 4), (x0 + w + 8, y0 + h + 8), (x0 + w - 4, y0 + h - 4)],
            col, 1.2)
    if inp is not None:
        pg.eq(x0 + w * 0.4, y0 - 30, inp, 16, C.ORANGE, align="center", valign="baseline")
        pg.arrow(x0 + w * 0.4, y0 - 26, x0 + w * 0.4, y0 - 4, C.ORANGE, 1.1, head=4)
    if out is not None:
        pg.eq(x0 + w + 26, y0 + h + 12, out, 16, C.GREEN, valign="middle")
    if reject is not None:
        pg.eq(x0 - 40, y0 - 22, reject, 15, C.RED, align="center", valign="middle")
        pg.arrow(x0 - 30, y0 - 18, x0 + w * 0.18, y0 - 12, C.RED, 1, head=4, dash=(3, 2))
        pg.xmark(x0 + w * 0.22, y0 - 10, 7)


def code(pg, x0, y0, lines, w=300, size=11.5):
    lh = size * 1.5
    h = lh * len(lines) + 14
    pg.rect(x0, y0, w, h, "#263238", 1, fillcolor="#263238", r=6)
    for i, (s, col) in enumerate(lines):
        pg.text(x0 + 12, y0 + 7 + i * lh, s, size, col, F.MONO)
    return h


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 18, "Functions", "a vending machine for numbers", C.BLUE, PAPER)
    machine(pg, L + 60, 250, r"\times2", r"3", r"6", w=140, h=80, size=24)
    machine(pg, L + 300, 250, r"x^2+1", r"4", r"17", w=140, h=80, size=22, col=C.PURPLE)
    pg.note(L + 60, 356, "put 3 in, 6 comes out. Every time.", C.BLUE, 17)
    pg.note(L + 300, 356, "put 4 in: 4² + 1 = 17", C.PURPLE, 17)
    f = ch.flow(top=410)
    f.p("A {B:function} is a rule that turns each input number into exactly {B:one} output number, "
        "like a vending machine: press B3 and you get crisps, every single time. You already know "
        "lots: \"double it\", \"square it\", \"add VAT\", and the sin button on your calculator.",
        14, gap=10)
    f.p("This chapter is mostly about {B:reading the notation}, $f(x)$, which trips everyone up, and "
        "about which inputs a machine will accept. Then you'll chain machines together and run them "
        "backwards, which is Chapter 14's undo idea again.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 13} {y:(functions, domains, images, piecewise functions).}", 12.5)


def notation(ch):
    f = flow(ch)
    sec(f, "Three ways to write the same machine")
    rule_box(f, "function and function notation", [
        "A {B:function} is a rule that gives {B:exactly one output} for each allowed input.",
        "$f(x)$ means \"the output of $f$ when the input is $x$\". $f(3)$ means: replace {B:every} $x$ in "
        "the rule by $3$ and work it out.",
        "$f(x)$ is {R:not} $f\\times x$. $f$ is the name of the rule; the brackets hold the input.",
    ], C.BLUE)
    f.p("Lecture 13 writes the doubling machine three ways. They all mean \"input a number, output "
        "twice it\":", 14, gap=8)
    y_ = f.reserve(70)
    pg = f.pg
    forms = [(r"x\mapsto2x", "\"x maps to 2x\""), (r"y=2x", "\"output y is 2 times x\""),
             (r"f(x)=2x", "\"f of x is 2x\"")]
    for i, (lat, say) in enumerate(forms):
        cx = L + 80 + i * 165
        pg.eq(cx, y_ + 4, lat, 22, C.BLUE, align="center")
        pg.note(cx - 70, y_ + 40, say, C.GREY, 15, w=150, align="center")
    ch.symbol(r"\mapsto", "maps to", "the input on the left is turned into the output on the right")
    ch.symbol(r"f(x)", "f of x", "the output of function f when the input is x")
    ch.term("function", "a rule that gives exactly one output for each allowed input")
    f.p("The third one, {B:function notation}, is the one to master. The letter $f$ is the {B:name of "
        "the machine} (you could call it $g$, $h$ or anything). The brackets hold {B:what you put "
        "in}. So:", 14, gap=8)
    y_ = f.reserve(104) + 14
    pg = f.pg
    pg.eq(L + 40, y_ + 10, r"f\,(\,3\,)=6", 30)
    pg.arrow(L + 50, y_ + 62, L + 48, y_ + 44, C.BLUE, 1.1, head=4)
    pg.note(L + 20, y_ + 64, "machine's name", C.BLUE, 14)
    pg.arrow(L + 90, y_ - 2, L + 82, y_ + 10, C.ORANGE, 1.1, head=4)
    pg.note(L + 92, y_ - 12, "the input", C.ORANGE, 14)
    pg.arrow(L + 160, y_ + 62, L + 158, y_ + 44, C.GREEN, 1.1, head=4)
    pg.note(L + 140, y_ + 64, "the output", C.GREEN, 14)
    pg.note(L + 250, y_ + 10, "Said: \"f of 3 is 6\".\nMeaning: put 3 into machine f,\nand 6 comes out.",
            C.GREY, 16)
    f.p("{R:The big trap: $f(x)$ is NOT \"f times x\".} There is no multiplication here. $f$ isn't a "
        "number at all, it's a name. Writing $f(3) = 3f$ is like saying \"vending-machine(B3)\" "
        "equals \"3 vending machines\".", 14)


def slot(ch):
    f = flow(ch)
    sec(f, "The x is a slot: whatever goes in fills every slot", room=440)
    rule_box(f, "substituting into a function", [
        "Replace {B:every} $x$ by the input, {B:in brackets}: $f(-2)$ for $f(x)=x^2+1$ is $(-2)^2+1$.",
        "An expression can be the input: $f(a+1)$ means replace each $x$ by $(a+1)$, then simplify.",
        "$f(x+1)$ changes the {B:input}; $f(x)+1$ changes the {B:output}. They are different.",
    ], C.BLUE)
    f.p("Take $f(x) = x^2 + 1$. Think of every $x$ in the rule as an empty slot, $\\square^2 + 1$. "
        "The input fills {B:every} slot, and it goes in {B:with brackets} round it:", 14, gap=8)
    step(f, r"f(\square)=\square^2+1", "the rule with its slots showing", size=20)
    step(f, r"f(3)=(3)^2+1=10", "3 in the slot", size=20)
    step(f, r"f(-2)=(-2)^2+1=5", "the brackets matter: (−2)² = +4", size=20)
    step(f, r"f(a+1)=(a+1)^2+1=a^2+2a+2", "a whole expression can go in the slot", size=20)
    fx = lambda t: t ** 2 + 1
    ch.check(fx(3), 10)
    ch.check(fx(-2), 5)
    ch.check(sp.expand(fx(a + 1)), a ** 2 + 2 * a + 2)
    f.p("{R:Watch out:} $f(x + 1)$ and $f(x) + 1$ are different. The first puts $x + 1$ {B:into} the "
        "machine; the second adds 1 to what comes {B:out}. With $x = 3$: $f(4) = 17$, but "
        "$f(3) + 1 = 11$.", 14, gap=10)
    ch.check(fx(4), 17)
    f.p("{b:If you code:} a function in maths is exactly a Python function. The letter in the "
        "brackets is the parameter; calling it with a number fills the slot.", 14, gap=8)
    y_ = f.reserve(90)
    pg = f.pg
    code(pg, L + 20, y_, [("def f(x):", "#80cbc4"), ("    return x**2 + 1", "#ffcc80"), ("", "#eceff1"),
                          ("print(f(3))    # 10", "#b0bec5"), ("print(f(-2))   # 5", "#b0bec5")], w=230)
    pg.note(L + 280, y_ + 10, "def = define the machine\nf(3) = use it with input 3", C.GREY, 16)


def domain(ch):
    f = flow(ch)
    sec(f, "The domain: which coins the machine accepts", room=520)
    rule_box(f, "domain and range", [
        "{B:Domain} = the set of inputs allowed. {B:Range} (or image) = the set of outputs that actually come out.",
        "If no domain is given, take every real number {B:except} those that break the rule: a denominator "
        "can't be 0, and you can't square-root a negative number.",
        "A function can be given a {B:restricted domain} on purpose, e.g. $f(x)=x^2,\\ x\\geq0$. The "
        "domain is part of the function: change it and you change the range.",
    ], C.BLUE)
    f.p("A vending machine rejects foreign coins. Some functions reject some inputs, because the rule "
        "would break:", 14, gap=24)
    y_ = f.reserve(134)
    pg = f.pg
    machine(pg, L + 70, y_ + 24, r"\frac1x", r"2", r"\tfrac12", w=100, h=56, reject=r"0")
    pg.note(L + 30, y_ + 90, "0 rejected: can't divide by 0", C.RED, 14)
    machine(pg, L + 320, y_ + 24, r"\sqrt{x}", r"9", r"3", w=100, h=56, col=C.PURPLE, reject=r"-4")
    pg.note(L + 270, y_ + 90, "−4 rejected: no real number squares\nto give −4 (Chapter 9)", C.RED, 14)
    f.p("The set of inputs a function accepts is its {B:domain}. The set of outputs that can come out "
        "is its {B:image} (also called its {B:range}). Lecture 13's examples, in the set notation "
        "of Chapter 6:", 14, gap=8)
    ch.term("domain", "the set of inputs a function accepts")
    ch.term("image (range)", "the set of all outputs a function can produce")
    rows = [(r"f(x)=2x", r"\mathbb{R}", r"\mathbb{R}", "anything in, anything out"),
            (r"f(x)=x^2", r"\mathbb{R}", r"[0,\infty)", "squares are never negative"),
            (r"f(x)=\sin x", r"\mathbb{R}", r"[-1,1]", "the sin button never gives more than 1"),
            (r"f(x)=\frac1x", r"x\neq0", r"y\neq0", "no input makes 1/x equal 0")]
    y_ = f.reserve(26 + 36 * len(rows))
    pg = f.pg
    xs = [L + 6, L + 130, L + 210, L + 300]
    for j, hd in enumerate(["function", "domain", "image", "why"]):
        pg.text(xs[j], y_, hd, 12, C.GREY, F.BOLD)
    for i, (fn, dom, img, why) in enumerate(rows):
        yy = y_ + 38 + i * 36
        pg.eq(xs[0], yy, fn, 16, valign="middle")
        pg.eq(xs[1], yy, dom, 16, C.ORANGE, valign="middle")
        pg.eq(xs[2], yy, img, 16, C.GREEN, valign="middle")
        pg.note(xs[3], yy - 11, why, C.GREY, 14, w=R - xs[3])
    f.p("(Lecture 13 writes the squaring function's image as $\\mathbb{Q}^+$, but that's the positive "
        "{B:fractions}; the outputs are all the non-negative {B:real} numbers, $[0, \\infty)$, "
        "including 0 and numbers like $(\\sqrt[3]{2})^2$.)", 12.5, C.GREY, gap=8)
    f.p("When no domain is given, assume it's {B:every number that doesn't break the rule}: usually "
        "just avoid dividing by zero and square-rooting negatives.", 14, gap=10)
    rule_box(f, "finding the domain and the range", [
        "{B:Domain:} set any denominator $\\neq0$ and anything under a square root $\\geq0$; solve for $x$.",
        "{B:Range of a straight line on an interval:} work out the outputs at the two ends of the domain. "
        "The range runs between them.",
        "{B:Range of a square:} $(\\text{anything})^2\\geq0$, so $a(x-h)^2+k\\geq k$ when $a>0$ "
        "(Chapter 15's completed square). The smallest output is $k$.",
        "Check with one or two inputs that the outputs really land in your range.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    x_ = x
    step(f, r"g(x)=\sqrt{x-3}:\quad x-3\geq0\ \Rightarrow\ x\geq3", "domain: no negatives under the root", size=18)
    ch.check_true(sp.solve_univariate_inequality(x_ - 3 >= 0, x_, relational=False) == sp.Interval(3, sp.oo))
    step(f, r"h(x)=\frac{5}{2x-6}:\quad 2x-6\neq0\ \Rightarrow\ x\neq3", "domain: denominator not 0", size=18)
    ch.check(sp.solve(2 * x_ - 6, x_), [3])
    step(f, r"f(x)=2x+1,\ 0\leq x\leq3:\quad f(0)=1,\ f(3)=7", "range: work out the two ends", size=17)
    step(f, r"\Rightarrow\ 1\leq f(x)\leq7", "the outputs run between them", size=17)
    ch.check([2 * 0 + 1, 2 * 3 + 1], [1, 7])
    step(f, r"q(x)=x^2-6x+11=(x-3)^2+2\geq2", "range: f(x) ≥ 2 (complete the square)", size=18)
    ch.check(sp.expand((x_ - 3) ** 2 + 2), x_ ** 2 - 6 * x_ + 11)
    ch.term("restricted domain", "a domain deliberately limited, e.g. x ≥ 0, often to make a function one-to-one")


def is_function(ch):
    f = flow(ch)
    sec(f, "Is it a function? One button, one snack", room=380)
    rule_box(f, "function tests", [
        "A rule is a function only if every input in the domain gives {B:exactly one} output.",
        "{B:Vertical line test} (on a graph, Chapter 19): every vertical line meets the graph {B:at most "
        "once}. Crossing twice means one input has two outputs: not a function.",
        "{B:One-to-one}: different inputs always give different outputs (every horizontal line meets the "
        "graph at most once). {B:Many-to-one}: some output comes from two or more inputs, like $x^2$.",
    ], C.BLUE)
    f.p("A machine that gave crisps {B:or} chocolate when you pressed B3 would be broken. A function "
        "must give {B:exactly one output per input}. Draw arrows from inputs to outputs:", 14, gap=10)
    y_ = f.reserve(130)
    pg = f.pg
    panels = [("f(x) = x²", [(-2, 4), (2, 4), (3, 9)], True, "two inputs share an output:\nfine (\"many-to-one\")"),
              ("\"± root\"", [(4, -2), (4, 2), (9, 3)], False, "one input, two outputs:\nNOT a function")]
    for k, (title, pairs, ok, verdict) in enumerate(panels):
        x0 = L + 10 + k * 250
        ins = sorted(set(p[0] for p in pairs))
        outs = sorted(set(p[1] for p in pairs))
        pg.text(x0 + 70, y_, title, 13, C.BLUE, F.BOLD, align="center")
        pg.ellipse(x0 + 20, y_ + 60, 18, 40, C.ORANGE, 1.1, fillcolor=C.LIGHT[C.ORANGE])
        pg.ellipse(x0 + 120, y_ + 60, 18, 40, C.GREEN, 1.1, fillcolor=C.LIGHT[C.GREEN])
        iy = {v: y_ + 36 + i * 24 for i, v in enumerate(ins)}
        oy = {v: y_ + 36 + i * 24 for i, v in enumerate(outs)}
        for v, yy in iy.items():
            pg.text(x0 + 20, yy - 7, str(v).replace("-", "−"), 12, C.INK, F.BOLD, align="center")
        for v, yy in oy.items():
            pg.text(x0 + 120, yy - 7, str(v).replace("-", "−"), 12, C.INK, F.BOLD, align="center")
        for p_, q_ in pairs:
            pg.arrow(x0 + 32, iy[p_], x0 + 106, oy[q_], C.GREEN if ok else C.RED, 1.1, head=4)
        pg.note(x0 + 146, y_ + 90, verdict, C.GREEN if ok else C.RED, 14)
    ch.term("many-to-one", "a function where different inputs can give the same output, like x² (2 and −2 both give 4)")
    ch.term("one-to-one", "a function where different inputs always give different outputs, like 2x + 3")
    ch.term("vertical line test", "a graph is a function if no vertical line crosses it more than once")
    f.p("That's why $\\sqrt{\\ }$ on its own always means the {B:positive} root (Chapter 9): it keeps "
        "the square-root button a proper function.", 14)


def piecewise(ch):
    f = flow(ch)
    sec(f, "Piecewise functions: parking charges", room=460)
    f.p("Some rules change depending on the input. A car park charges £2 for up to 1 hour, £5 for up to "
        "3 hours, and £10 for longer. One machine, three rules:", 14, gap=6)
    step(f, r"c(t)=\begin{cases}2&0<t\le1\\5&1<t\le3\\10&t>3\end{cases}", "t = hours parked, c = cost in £",
         size=18)
    y_ = f.reserve(146)
    pg = f.pg
    ax = Axes(pg, L + 40, y_ + 14, 240, 110, (0, 5), (0, 12))
    ax.grid(1, 2)
    ax.axes("t", "c", 1, 2)
    for x1, x2, v in [(0, 1, 2), (1, 3, 5), (3, 5, 10)]:
        ax.seg(x1, v, x2, v, C.BLUE, 2.2)
        ax.hollow(x1, v, C.BLUE)
        if x2 < 5:
            ax.dot(x2, v, C.BLUE)
    pg.note(L + 310, y_ + 16, "filled dot = included\nhollow dot = not included\n\nexactly 1 hour costs £2\n"
            "(filled dot on the lower step);\n1 hour 1 minute costs £5", C.GREY, 15)
    ch.term("piecewise function", "a function defined by different formulas on different parts of its domain")
    f.p("To use it, {B:first find which piece your input belongs to}, then use that piece's rule: "
        "$c(0.5) = 2$, $c(3) = 5$, $c(4.5) = 10$.", 14, gap=8)
    f.p("{b:Lecture 13's example} is the {B:sign function}: 1 for positive inputs, −1 for negative "
        "inputs, 0 for 0. It can't be written as one formula, so it's written in pieces:", 14, gap=6)
    step(f, r"\operatorname{sgn}(x)=\begin{cases}1&x>0\\0&x=0\\-1&x<0\end{cases}", "sgn(7) = 1,  sgn(−0.2) = −1",
         size=18)
    ch.check(sp.sign(7), 1)
    ch.check(sp.sign(sp.Rational(-1, 5)), -1)


def chains(ch):
    f = flow(ch)
    sec(f, "Machines in a chain: composite functions", room=520)
    rule_box(f, "composite functions", [
        "$fg(x)$ means $f(g(x))$: {B:do $g$ first}, then put its output into $f$. It is also written "
        "$(f\\circ g)(x)$, read \"f after g\".",
        "Work from the {B:inside out}: the function written nearest to $x$ acts first.",
        "In general $fg(x)\\neq gf(x)$: the order matters.",
        "To find $fg(x)$ as a formula: take the rule for $f$ and replace every $x$ by the whole of $g(x)$, "
        "in brackets.",
    ], C.BLUE)
    f.p("The output of one machine can be fed straight into another. With $f(x) = 2x$ and "
        "$g(x) = x + 3$:", 14, gap=28)
    y_ = f.reserve(90)
    pg = f.pg
    machine(pg, L + 40, y_ + 10, r"g:\ +3", r"4", None, w=100, h=50)
    pg.arrow(L + 160, y_ + 64, L + 210, y_ + 34, C.GREEN, 1.2, head=4)
    pg.eq(L + 180, y_ + 70, r"7", 15, C.GREEN, align="center")
    machine(pg, L + 220, y_ + 10, r"f:\ \times2", None, r"14", w=100, h=50, col=C.PURPLE)
    pg.note(L + 380, y_ + 4, "g first, then f.\nWritten f(g(4)):\nread from the inside out", C.GREY, 15)
    step(f, r"fg(x)=f(g(x))=2(x+3)=2x+6", "g's output fills f's slot", size=19)
    step(f, r"gf(x)=g(f(x))=2x+3", "other order: different machine!", size=19)
    ch.check(sp.expand(2 * (x + 3)), 2 * x + 6)
    ch.symbol(r"f\circ g", "f after g (f compose g)", "the composite function f(g(x)): g first, then f")
    ch.term("composite function", "one function applied to the output of another, written f(g(x)), fg(x) or (f∘g)(x)")
    f.p("Order matters, like socks and shoes (Chapter 14). $f(g(4)) = 14$ but $g(f(4)) = 11$.", 14, gap=8)
    f.p("{b:With squares:} $f(x) = x^2 + 1$ and $g(x) = 3x - 2$.", 14, gap=6)
    step(f, r"fg(x)=(3x-2)^2+1=9x^2-12x+5", "replace x in f by (3x − 2)", size=18)
    step(f, r"gf(x)=3(x^2+1)-2=3x^2+1", "replace x in g by (x² + 1)", size=18)
    ch.check(sp.expand((3 * x - 2) ** 2 + 1), 9 * x ** 2 - 12 * x + 5)
    ch.check(sp.expand(3 * (x ** 2 + 1) - 2), 3 * x ** 2 + 1)
    f.p("{G:Check with a number:} $x = 1$: $g(1) = 1$, $f(1) = 2$; formula: $9 - 12 + 5 = 2$ ✓.", 13.5)


def inverse_fn(ch):
    f = flow(ch)
    sec(f, "Running a machine backwards: inverse functions", room=560)
    rule_box(f, "inverse functions", [
        "$f^{-1}$ undoes $f$: if $f(a)=b$ then $f^{-1}(b)=a$. So $f(f^{-1}(x))=x$ and $f^{-1}(f(x))=x$.",
        "Only a {B:one-to-one} function has an inverse. A many-to-one function (like $x^2$ on all numbers) "
        "needs its domain restricted first (e.g. $x\\geq0$).",
        "{B:Domain of $f^{-1}$ = range of $f$}, and range of $f^{-1}$ = domain of $f$: inputs and outputs swap.",
        "The graph of $y=f^{-1}(x)$ is the graph of $y=f(x)$ {B:reflected in the line $y=x$}.",
        "$f^{-1}(x)$ is {R:not} $\\dfrac{1}{f(x)}$: the $-1$ is a label meaning \"reverse\".",
    ], C.BLUE)
    rule_box(f, "finding f⁻¹(x)", [
        "Write $y=f(x)$.",
        "Rearrange to make $x$ the subject (undo each step in reverse order, Chapter 14).",
        "Swap the letters: write the answer with $x$ as the input, $f^{-1}(x)=\\dots$",
        "State the domain of $f^{-1}$ (the range of $f$) and check: $f^{-1}(f(a))=a$ for some number $a$.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    f.p("{B:Example:}  $f(x) = 2x + 3$ (× 2, then + 3).", 13.5, gap=4)
    step(f, r"y=2x+3", "step 1", size=19)
    step(f, r"x=\frac{y-3}{2}", "step 2: undo +3, then undo ×2", size=19)
    step(f, r"f^{-1}(x)=\frac{x-3}{2}", "step 3: rename the input x", size=19, color=C.GREEN)
    yv = sp.Symbol("y")
    ch.check(sp.solve(sp.Eq(yv, 2 * x + 3), x), [(yv - 3) / 2])
    ch.symbol(r"f^{-1}", "f inverse", "the function that undoes f")
    ch.term("inverse function", "f⁻¹, the function that reverses f: if f(3) = 9 then f⁻¹(9) = 3")
    f.p("{G:Step 4, check:} $f(5) = 13$ and $f^{-1}(13) = \\frac{10}{2} = 5$ ✓. Domain of $f^{-1}$: every "
        "number, since $f$'s range is every number.", 13.5, gap=8)
    ch.check(((2 * x + 3) - 3) / 2, x)
    y_ = f.reserve(186)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 6, 190, 160, (-4, 6), (-4, 6))
    ax.grid(1, 1)
    ax.axes("x", "y", 2, 2, size=8)
    ax.curve(lambda t: t, color=C.GREY, width=1.1, dash=(4, 3))
    ax.curve(lambda t: 2 * t + 3, color=C.BLUE, width=2)
    ax.curve(lambda t: (t - 3) / 2, color=C.PURPLE, width=2)
    ax.dot(1, 5, C.BLUE, 3.5)
    ax.dot(5, 1, C.PURPLE, 3.5)
    ax.seg(1, 5, 5, 1, C.ORANGE, 1, dash=(2, 2))
    pg.note(L + 240, y_ + 8, "blue: y = 2x + 3\npurple: y = (x − 3)/2\ngrey dashed: y = x (the mirror)\n\n"
            "(1, 5) on f becomes (5, 1) on the\ninverse: the coordinates swap, which is a\nreflection in y = x.",
            C.INK, 15)
    ch.check([2 * 1 + 3, sp.Rational(5 - 3, 2)], [5, 1])
    f.p("{B:Example:}  $f(x) = \\dfrac{x+4}{3}$ with domain $x \\geq 2$.", 13.5, gap=4)
    step(f, r"y=\frac{x+4}{3}\ \Rightarrow\ 3y=x+4\ \Rightarrow\ x=3y-4", "× 3, then − 4", size=18)
    step(f, r"f^{-1}(x)=3x-4,\quad x\geq2", "domain of the inverse = range of f", size=18, color=C.GREEN)
    ch.check(sp.solve(sp.Eq(yv, (x + 4) / 3), x), [3 * yv - 4])
    f.p("The range of $f$: the smallest input is 2, giving $f(2) = \\frac{6}{3} = 2$, and $f$ goes up, so "
        "$f(x) \\geq 2$. That becomes the domain of $f^{-1}$.", 13.5, gap=8)
    ch.check(sp.Rational(2 + 4, 3), 2)
    f.p("{B:Example:}  $f(x) = x^2$ has no inverse on all numbers: $f(3) = f(-3) = 9$, so $f^{-1}(9)$ "
        "couldn't decide. Restrict to $x \\geq 0$ and it is one-to-one, with $f^{-1}(x) = \\sqrt{x}$, "
        "$x \\geq 0$.", 13.5)
    ch.check(sp.sqrt(x ** 2).subs(x, 3), 3)


def ex(f, s):
    f.need(100)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown: working backwards from outputs", room=520)
    rule_box(f, "partial-information function problems", [
        "\"Solve $f(x)=k$\": write the rule $= k$ and solve the equation for $x$ (Chapter 15). A square may "
        "give two answers; check each is in the domain.",
        "\"$f(1)=5$\" is an equation: put $x=1$ into the rule and set it equal to 5. Two unknown letters "
        "need two facts: solve them simultaneously.",
        "\"Solve $fg(x)=k$\": first write $fg(x)$ as one formula, then set it equal to $k$.",
        "\"Find $f^{-1}(b)$\": either find the formula for $f^{-1}$, or solve $f(x)=b$; it's the same answer.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    ex(f, "$f(x) = 3x - 5$. Solve $f(x) = 10$.")
    step(f, r"3x-5=10\ \Rightarrow\ 3x=15\ \Rightarrow\ x=5", "check: f(5) = 15 − 5 = 10", size=19,
         color=C.GREEN)
    ch.check(sp.solve(3 * x - 5 - 10, x), [5])
    ex(f, "$f(x) = x^2 - 2x$. Solve $f(x) = 3$.")
    step(f, r"x^2-2x-3=0\ \Rightarrow\ (x-3)(x+1)=0", "rearrange to = 0, factorise", size=19)
    step(f, r"x=3\ \text{ or }\ x=-1", "two inputs give 3: f is many-to-one", size=19, color=C.GREEN)
    ch.check(sp.solve(x ** 2 - 2 * x - 3, x), [-1, 3])
    a_, b_ = sp.symbols("a b")
    ex(f, "$f(x) = ax + b$, with $f(1) = 5$ and $f(3) = 11$. Find $a$ and $b$.")
    step(f, r"a+b=5,\qquad 3a+b=11", "x = 1 and x = 3 into the rule", size=19)
    step(f, r"2a=6\ \Rightarrow\ a=3,\quad b=2", "subtract: b cancels", size=19, color=C.GREEN)
    ch.check(sp.solve([a_ + b_ - 5, 3 * a_ + b_ - 11], [a_, b_]), {a_: 3, b_: 2})
    f.p("{G:Check:} $f(x) = 3x + 2$: $f(1) = 5$ ✓, $f(3) = 11$ ✓.", 13.5, gap=8)
    ex(f, "$f(x) = 2x + 1$ and $g(x) = x^2$. Solve $fg(x) = 19$.")
    step(f, r"fg(x)=f(x^2)=2x^2+1", "g first, then f", size=19)
    step(f, r"2x^2+1=19\ \Rightarrow\ x^2=9\ \Rightarrow\ x=\pm3", "", size=19, color=C.GREEN)
    ch.check(sp.solve(2 * x ** 2 + 1 - 19, x), [-3, 3])
    ex(f, "$f(x) = kx^2 - 3$ and $f(2) = 9$. Find $k$.")
    step(f, r"4k-3=9\ \Rightarrow\ k=3", "x = 2 into the rule", size=19, color=C.GREEN)
    kk = sp.Symbol("k")
    ch.check(sp.solve(kk * 4 - 3 - 9, kk), [3])
    ex(f, "$f(x) = 4x - 7$. Find $f^{-1}(5)$ without finding the formula.")
    step(f, r"4x-7=5\ \Rightarrow\ x=3,\ \text{so } f^{-1}(5)=3", "the input that gives 5", size=18,
         color=C.GREEN)
    ch.check(sp.solve(4 * x - 7 - 5, x), [3])
    ch.check(sp.Rational(5 + 7, 4), 3)


def common_mistakes(ch):
    f = flow(ch)
    sec(f, "Mistakes to avoid", room=360)
    mistakes(f, [
        (r"f(3)=3f", r"f(3)=\text{rule with }x=3", "f is a name, not a number"),
        (r"f(-2)=-2^2+1=-3", r"f(-2)=(-2)^2+1=5", "brackets round the input"),
        (r"fg(x):\ \text{do } f \text{ first}", r"fg(x)=f(g(x)):\ g\text{ first}", "inside out"),
        (r"f^{-1}(x)=\frac{1}{f(x)}", r"f^{-1}\text{ undoes }f", "−1 means inverse, not a power"),
        (r"f(x+1)=f(x)+1", r"f(x+1)\neq f(x)+1", "input changed vs output changed"),
    ])


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Function", None, "exactly one output for each input in the domain"),
        ("Notation", r"f(a)=\text{the rule with every }x\text{ replaced by }(a)", None),
        ("Domain", None, "allowed inputs: denominator $\\neq0$, nothing negative under a square root"),
        ("Range", None, "all outputs; for a line on an interval use the end values; $a(x-h)^2+k\\geq k$ ($a>0$)"),
        ("Vertical line test", None, "a graph is a function if every vertical line meets it at most once"),
        ("One-to-one", None, "different inputs give different outputs; needed for an inverse"),
        ("Composite", r"fg(x)=(f\circ g)(x)=f(g(x))", "$g$ first; in general $fg\\neq gf$"),
        ("Inverse", r"f(f^{-1}(x))=f^{-1}(f(x))=x", "write $y=f(x)$, make $x$ the subject, rename"),
        ("Inverse domain", None, "domain of $f^{-1}$ = range of $f$ (and range of $f^{-1}$ = domain of $f$)"),
        ("Inverse graph", None, "reflect the graph of $f$ in the line $y=x$"),
        ("Solve f(x) = k", None, "set the rule equal to $k$ and solve; $f(a)=b$ gives an equation"),
    ], C.BLUE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Vending machines: your turn", fresh=True)
    f.p("Answers in grey.", 13.5, gap=10)
    groups = [
        ("Using the notation", ["f(x) = 3x − 1. Find f(2), f(0) and f(−4).", "g(x) = x² − x. Find g(3) and g(−3).",
                                "h(x) = 10/x. Find h(5) and h(0.5).", "f(x) = 3x − 1. Find f(a + 2) and simplify."],
         "1. 5, −1, −13   2. 6, 12   3. 2, 20   4. 3a + 5"),
        ("Domain and image", ["What input does 1/(x − 4) reject?", "What inputs does √(x − 1) accept?",
                              "What is the image of f(x) = x² + 5?"],
         "5. x = 4   6. x ≥ 1   7. [5, ∞): outputs of 5 or more"),
        ("Pieces, chains and inverses", ["With the car park c(t), find c(2) and c(3.5).",
                                         "f(x) = x + 4, g(x) = 3x. Find f(g(2)) and g(f(2)).",
                                         "Find the inverse of f(x) = 5x − 2.", "Find the inverse of f(x) = (x + 1)/4."],
         "8. £5, £10   9. 10, 18   10. f⁻¹(x) = (x + 2)/5   11. f⁻¹(x) = 4x − 1"),
        ("Find the unknown", ["f(x) = 5x + 2. Solve f(x) = 27.", "g(x) = x² + 4x. Solve g(x) = 12.",
                              "f(x) = ax + b, with f(2) = 7 and f(5) = 16. Find a and b.",
                              "f(x) = 3x − 1 and g(x) = x + 2. Solve fg(x) = 20.",
                              "h(x) = kx³ + 1 and h(2) = 25. Find k.",
                              "f(x) = (x + 4)/2. Find the value of a for which f⁻¹(a) = 6."],
         "12. x = 5 (5x = 25)   13. x = 2 or x = −6 ((x + 6)(x − 2) = 0)   14. a = 3, b = 1 (3a = 9)   "
         "15. x = 5 (fg(x) = 3(x + 2) − 1 = 3x + 5)   16. k = 3 (8k + 1 = 25)   17. a = 5 (f⁻¹(a) = 6 means a = f(6))"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    F1 = lambda t: 3 * t - 1
    ch.check([F1(2), F1(0), F1(-4)], [5, -1, -13])
    ch.check([3 ** 2 - 3, 9 + 3], [6, 12])
    ch.check(sp.expand(F1(a + 2)), 3 * a + 5)
    ch.check([2 * 3 + 4, 3 * (2 + 4)], [10, 18])
    yv = sp.Symbol("y")
    ch.check(sp.solve(sp.Eq(yv, 5 * x - 2), x), [(yv + 2) / 5])
    ch.check(sp.solve(sp.Eq(yv, (x + 1) / 4), x), [4 * yv - 1])
    a_, b_, k_ = sp.symbols("a b k")
    ch.check(sp.solve(5 * x + 2 - 27, x), [5])
    ch.check(sp.solve(x ** 2 + 4 * x - 12, x), [-6, 2])
    ch.check(sp.solve([2 * a_ + b_ - 7, 5 * a_ + b_ - 16], [a_, b_]), {a_: 3, b_: 1})
    ch.check(sp.solve(3 * (x + 2) - 1 - 20, x), [5])
    ch.check(sp.solve(k_ * 8 + 1 - 25, k_), [3])
    ch.check(sp.Rational(6 + 4, 2), 5)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    notation(ch)
    slot(ch)
    domain(ch)
    is_function(ch)
    piecewise(ch)
    chains(ch)
    inverse_fn(ch)
    find_unknown(ch)
    common_mistakes(ch)
    summary(ch)
    your_turn(ch)
