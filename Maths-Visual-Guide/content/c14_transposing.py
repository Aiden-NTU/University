"""Chapter 14 - Transposing formulae. A letter is a present wrapped in layers; we unwrap it. Rule first:
the balance rule, the undo buttons and the unwrapping procedure are boxed before the examples; then
minus signs, letters on the bottom, cube roots, safety rules, and rearranging to find a value."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import rule_box, rules_page

ORDER = 14
NUM = 14
TITLE = "Transposing formulae"
SHORT = "Transposing formulae"
SLUG = "Transposing-Formulae"
ACCENT = C.PINK
REQUIRES = ["equals-sign", "substitution", "powers", "roots", "like-terms", "expand-brackets",
            "factorise-common-factor", "algebraic-fractions", "reciprocal"]
INTRODUCES = ["inverse-operations", "transpose", "subject-of-formula"]

L, R, W = 50, 545, 495
PAPER = ["#f8bbd0", "#bbdefb", "#c8e6c9", "#ffe0b2", "#e1bee7"]
PAPER_EDGE = [C.PINK, C.BLUE, C.GREEN, C.ORANGE, C.PURPLE]


# ----------------------------------------------------------------------------- drawing kit
def op_box(pg, cx, cy, latex, col, w=None, size=17):
    ew, eh, _ = pg.eq_size(latex, size)
    bw = w or max(52, ew + 22)
    pg.rect(cx - bw / 2, cy - 17, bw, 34, col, 1.6, fillcolor=C.LIGHT.get(col, "#ffffff"), r=9)
    pg.eq(cx, cy, latex, size, col, align="center", valign="middle")
    return bw


def letter_blob(pg, cx, cy, latex, col=C.INK, size=22):
    pg.circle(cx, cy, 20, col, 1.8, fillcolor="#ffffff")
    pg.eq(cx, cy, latex, size, col, align="center", valign="middle")


def chain(f, start, ops, end, title=None, colors=None, reverse=False, size=17, gap=None):
    """Draw a flowchart: start -> op -> op -> ... -> end. Returns the y used."""
    n = len(ops)
    colors = colors or PAPER_EDGE
    h = 70 if title else 52
    y = f.reserve(h)
    pg = f.pg
    if title:
        pg.note(L, y, title, C.INK if not reverse else C.GREEN, 17)
        y += 22
    cy = y + 22
    span = R - L - 100
    gap = gap or span / (n + 1)
    xs = [L + 30 + gap * (i + 1) for i in range(n)]
    letter_blob(pg, L + 22, cy, start, C.INK if not reverse else C.BLUE)
    prev = L + 44
    for i, (x, lat) in enumerate(zip(xs, ops)):
        col = colors[i % len(colors)]
        bw = op_box(pg, x, cy, lat, col, size=size)
        pg.arrow(prev + 2, cy, x - bw / 2 - 3, cy, C.GREY, 1.3, head=5)
        prev = x + bw / 2
    ex = R - 28
    pg.arrow(prev + 2, cy, ex - 22, cy, C.GREY, 1.3, head=5)
    letter_blob(pg, ex, cy, end, C.BLUE if not reverse else C.INK)
    return y


def mini_chain(pg, x, cy, start, ops, end, colors, size=15, dashed=False, box_w=None):
    """Compact chain drawn directly at (x, cy). Empty op strings give blank boxes."""
    def blob(cx, lat, col):
        pg.circle(cx, cy, 15, col, 1.4 if lat else 1.1, fillcolor="#ffffff",
                  dash=None if lat else (3, 3))
        if lat:
            pg.eq(cx, cy, lat, size + 2, align="center", valign="middle")
    blob(x + 15, start, C.INK)
    px = x + 30
    for i, lat in enumerate(ops):
        col = colors[i % len(colors)]
        ew = pg.eq_size(lat, size)[0] if lat else 0
        bw = box_w or max(50, ew + 18)
        bx = px + 20
        pg.arrow(px + 1, cy, bx - 2, cy, C.GREY, 1.1, head=4)
        pg.rect(bx, cy - 14, bw, 28, col, 1.3, fillcolor=None if dashed else C.LIGHT.get(col), r=8,
                dash=(3, 3) if dashed else None)
        if lat:
            pg.eq(bx + bw / 2, cy, lat, size, col, align="center", valign="middle")
        px = bx + bw
    pg.arrow(px + 1, cy, px + 18, cy, C.GREY, 1.1, head=4)
    blob(px + 34, end, C.INK)
    return px + 50


def present(pg, cx, cy, layers, inner, scale=1.0):
    """Nested wrapped boxes; layers listed outermost first."""
    n = len(layers)
    for i, (lab, col) in enumerate(layers):
        w = (90 + 70 * (n - i)) * scale
        h = (56 + 50 * (n - i)) * scale
        pg.rect(cx - w / 2, cy - h / 2, w, h, col, 1.6, fillcolor=C.LIGHT.get(col), r=10)
        pg.note(cx - w / 2 + 8, cy - h / 2 + 1, lab, col, 15, solid=False)
    pg.circle(cx, cy + 4, 20 * scale, C.INK, 1.8, fillcolor="#ffffff")
    pg.eq(cx, cy + 4, inner, 22, align="center", valign="middle")


def onion(pg, cx, cy, layers, cols, inner):
    """A small present: layers listed outermost first, each labelled with its wrapping."""
    n = len(layers)
    for i, (lab, col) in enumerate(zip(layers, cols)):
        k = n - i
        x0, y0 = cx - 20 - 12 * k, cy - 18 - 16 * k
        pg.rect(x0, y0, 40 + 24 * k, 36 + 22 * k, col, 1.4, fillcolor=C.LIGHT.get(col), r=8)
        pg.eq(x0 + 5, y0 + 3, lab, 10, col)
    pg.circle(cx, cy, 14, C.INK, 1.6, fillcolor="#ffffff")
    pg.eq(cx, cy, inner, 16, align="center", valign="middle")


def peel(f, layers, cols, inner, undos, others, lead=None):
    """The present losing one layer per step. undos[j] takes off layers[j]; others[j] is what the
    other side of the = has become by then."""
    n = len(layers)
    if lead:
        f.p(lead, 13.5, gap=4)
    widths = [40 + 24 * (n - j) if j < n else 28 for j in range(n + 1)]
    gapw = min(96, (W - 20 - sum(widths)) / n)
    x = L + (W - sum(widths) - gapw * n) / 2
    h = 86 + 22 * n
    y = f.reserve(h)
    pg = f.pg
    cy = y + 22 + 16 * n
    base = cy + 18 + 6 * n + 16
    for j in range(n + 1):
        cx = x + widths[j] / 2
        onion(pg, cx, cy, layers[j:], cols[j:], inner)
        pg.eq(cx, base, others[j], 14, C.GREEN if j == n else C.INK, align="center", valign="middle")
        if j < n:
            ax0, ax1 = x + widths[j] + 6, x + widths[j] + gapw - 6
            pg.arrow(ax0, cy, ax1, cy, cols[j], 1.4, head=5)
            pg.eq((ax0 + ax1) / 2, cy - 14, undos[j], 13, cols[j], align="center", valign="middle")
        x += widths[j] + gapw
    pg.note(L, base + 10, "underneath: the other side of the =", C.GREY, 12)


def step(f, latex, why, size=22, x=L + 16, note_x=None, col=C.RED, color=C.INK):
    w, h, _ = f.pg.eq_size(latex, size)
    nx = note_x or max(x + w + 34, 290)
    nh = F.line_h(F.HAND, 16) * len(F.wrap(why, F.HAND, 16, R - nx)) if why else 0
    y = f.reserve(max(h, nh) + 12)
    pg = f.pg
    pg.eq(x, y, latex, size, color)
    if why:
        pg.note(nx, y + max(0, h / 2 - 11), why, col, 16, w=R - nx)
        pg.arrow(nx - 6, y + h / 2, x + w + 8, y + h / 2, col, 1.0, head=4)
    return y


def heading(f, s, room=300):
    if f.y > f.top + 5:
        f.need(room)
        if f.y > f.top + 5:
            f.gap(20)
    y = f.y
    pg = f.pg
    pg.rect(L - 4, y + 2, 16, 16, C.PINK, 1.6, fillcolor=C.LIGHT[C.PINK], r=3)
    pg.line(L + 4, y + 2, L + 4, y + 18, C.PINK, 1.2)
    pg.line(L - 4, y + 10, L + 12, y + 10, C.PINK, 1.2)
    size = 20
    while pg.twidth(s, size, F.BOLD) > R - L - 24 and size > 13:
        size -= 1
    pg.text(L + 22, y - 1 + (20 - size) / 2, s, size, C.PINK, F.BOLD)
    f.y += 34


def flow(ch):
    if getattr(ch, "_flow", None) is None:
        ch._flow = ch.flow()
        ch._flow.new_page()
    return ch._flow


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = ch.new_page(bg="#fff5f8")
    pg.text(L, 60, "Chapter 14", 16, C.GREY, F.BOLD)
    pg.text(L, 82, "Transposing formulae", 38, C.PINK, F.BOLD)
    pg.note(L, 132, "or: unwrapping a present to get at the letter inside", C.PINK, 23)
    present(pg, 250, 320, [("outer layer: + 3", C.PINK), ("inner layer: x 2", C.BLUE)], r"x", 1.45)
    pg.note(430, 200, "the letter you want\nis wrapped up inside", C.INK, 19)
    pg.arrow(450, 250, 275, 322, C.INK, 1.4, bend=-0.2)
    f = ch.flow(top=470)
    f.p("A formula is usually written to work out {B:one} particular thing. $F = \\frac{9}{5}C + 32$ "
        "turns a temperature in Celsius into Fahrenheit. But what if you know the Fahrenheit and "
        "want the Celsius? You need to {B:rearrange} the formula so that $C$ is on its own.", 14,
        gap=10)
    f.p("Rearranging a formula is called {B:transposing} it. The trick in this chapter is to see "
        "every formula as a {b:present}: the letter you want is in the middle, and the formula has "
        "wrapped it in layers (\"times 2\", \"add 3\", \"square root\"...). To get the letter out, "
        "you take the layers off, {B:outside layer first}.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 2} {y:(Algebraic manipulation) and parts of Lectures 7 and 12. Uses: "
        "letters and substituting (Chapter 8), squares and roots (Chapter 9), brackets (Chapter 11), "
        "factorising (Chapter 12) and algebraic fractions (Chapter 13).}", 12.5)
    ch.term("transpose", "rearrange a formula so that a different letter is on its own")


def subject(ch):
    f = flow(ch)
    heading(f, "What \"make x the subject\" means")
    f.p("The {B:subject} of a formula is the letter that is {B:on its own} on one side of the = "
        "sign. In", 14, gap=4)
    f.eq(r"\blu{y} = 2x+3", 28, gap=4)
    f.p("the subject is {b:$y$}. The formula is a machine for working out $y$: give it an $x$ and it "
        "tells you $y$. {B:\"Make $x$ the subject\"} means: rearrange it so it looks like", 14, gap=4)
    f.eq(r"\blu{x} = \text{(something with } y \text{ in it)}", 24, gap=6)
    f.p("so that it becomes a machine for working out $x$ instead. The words {B:transpose}, "
        "{B:rearrange}, {B:change the subject}, {B:make $x$ the subject} and {B:solve for $x$} all "
        "mean the same thing.", 14, gap=12)
    ch.term("subject of a formula", "the letter on its own on one side of the = sign")
    heading(f, "The undo buttons", room=420)
    rule_box(f, "inverse operations (undo buttons)", [
        "$+$ is undone by $-$, and $-$ by $+$.",
        "$\\times$ is undone by $\\div$, and $\\div$ by $\\times$ ({R:never divide by something that could be 0}).",
        "Squaring is undone by square-rooting (giving $\\pm$), and $\\sqrt{\\ }$ by squaring.",
        "Cubing is undone by the cube root $\\sqrt[3]{\\ }$ (one answer, no $\\pm$), and $\\sqrt[3]{\\ }$ by cubing.",
        "Flipping a fraction (taking the reciprocal) is undone by flipping it back.",
    ], C.PINK)
    f.p("Every operation has an {B:undo button}: another operation that exactly cancels it. "
        "The proper name is an {B:inverse operation}. Test each pair with a number: do it, then undo "
        "it, and you are back where you started.", 14, gap=10)
    ch.term("inverse operation", "the operation that undoes another one: minus undoes plus, divide undoes times")
    pairs = [("+3", "-3", r"7\xrightarrow{+3}10\xrightarrow{-3}7"),
             (r"\times2", r"\div2", r"7\xrightarrow{\times2}14\xrightarrow{\div2}7"),
             (r"\text{square}", r"\sqrt{\ }", r"7\xrightarrow{\text{sq}}49\xrightarrow{\sqrt{}}7"),
             (r"\text{flip}", r"\text{flip}", r"\tfrac{2}{7}\xrightarrow{\text{flip}}\tfrac{7}{2}\xrightarrow{\text{flip}}\tfrac27")]
    names = ["plus is undone by minus (and minus by plus)", "times is undone by divide (and divide by times)",
             "squaring is undone by square-rooting", "flipping a fraction is undone by flipping it back"]
    for (do, undo, test), nm in zip(pairs, names):
        y = f.reserve(62)
        pg = f.pg
        pg.rect(L + 10, y + 6, 70, 34, C.BLUE, 1.6, fillcolor=C.LIGHT[C.BLUE], r=17)
        pg.eq(L + 45, y + 23, do, 17, C.BLUE, align="center", valign="middle")
        pg.arrow(L + 86, y + 23, L + 118, y + 23, C.GREY, 1.2, both=True, head=5)
        pg.rect(L + 124, y + 6, 70, 34, C.GREEN, 1.6, fillcolor=C.LIGHT[C.GREEN], r=17)
        pg.eq(L + 159, y + 23, undo, 17, C.GREEN, align="center", valign="middle")
        pg.eq(L + 215, y + 2, test, 16)
        pg.note(L + 215, y + 36, nm, C.GREY, 14)
    ch.check(7 + 3 - 3, 7)
    ch.check(sp.sqrt(7 ** 2), 7)


def balance(ch):
    f = flow(ch)
    heading(f, "The only rule: keep the see-saw balanced", room=330)
    f.p("Part 0 said = is a balanced see-saw. If you take 3 off the left pan, it tips... unless you "
        "take 3 off the right pan as well. So the one and only rule of rearranging is:", 14, gap=8)
    rule_box(f, "the balance rule", [
        "{B:Whatever you do to one side, do exactly the same to the whole of the other side.}",
        "\"The whole side\": dividing $2x+3$ by 2 gives $\\frac{2x+3}{2}$, which is $x+\\frac32$, not $x+3$.",
    ], C.PINK)
    y = f.reserve(165)
    pg = f.pg
    for i, (lft, rgt, lab) in enumerate([(r"y", r"2x+3", "balanced"),
                                         (r"y\org{-3}", r"2x+3\org{-3}", "take 3 from BOTH pans: still balanced")]):
        cx = 170 + i * 250
        pg.poly([(cx - 14, y + 120), (cx, y + 60), (cx + 14, y + 120)], C.BROWN, 2)
        pg.line(cx - 95, y + 60, cx + 95, y + 60, C.BROWN, 2.5)
        for px, lat in ((cx - 80, lft), (cx + 80, rgt)):
            pg.line(px - 34, y + 58, px + 34, y + 58, C.BROWN, 2.5)
            pg.eq(px, y + 52, lat, 17, align="center", valign="baseline")
        pg.line(cx - 40, y + 121, cx + 40, y + 121, C.BROWN, 2.5)
        pg.note(cx, y + 130, lab, C.GREEN if i else C.GREY, 15, align="center", w=None)
    f.p("{R:\"The whole of the other side\" matters.} If the other side is $2x+3$ and you divide by 2, "
        "you must divide {B:all} of $2x+3$, not just the $2x$. More on this mistake later.", 13.5)


def first_unwrap(ch):
    f = flow(ch)
    heading(f, "Your first unwrapping:  y = 2x + 3", room=520)
    rule_box(f, "making a letter the subject", [
        "Write down what happens to the letter, {B:in order}, to build the formula (its layers).",
        "Undo the layers in {B:reverse order} (last on, first off), using the undo buttons.",
        "Do every move to the {B:whole} of both sides, one move per line.",
        "Swap sides so the letter is on the left. Test with numbers.",
    ], C.PINK, numbered=True, tag="PROCEDURE")
    f.p("{b:Step 1: work out how the present was wrapped.} Start with $x$ and ask: what happens to it, "
        "in order, to make $y$?  $x$ is first {p:multiplied by 2} (that makes $2x$), and then "
        "{o:3 is added} (that makes $2x+3$).", 14, gap=4)
    chain(f, "x", [r"\times 2", r"+3"], "y", "wrapping (building the formula):", [C.PURPLE, C.ORANGE])
    f.gap(4)
    f.p("{b:Step 2: unwrap in the reverse order, using the undo buttons.} The last layer on was "
        "{o:+3}, so it comes off first, using {o:$-3$}. Then {p:$\\times2$} comes off, using "
        "{p:$\\div2$}.", 14, gap=4)
    chain(f, "y", [r"-3", r"\div 2"], "x", "unwrapping (reverse order, undo buttons):",
          [C.ORANGE, C.PURPLE], reverse=True)
    peel(f, [r"+3", r"\times2"], [C.ORANGE, C.PURPLE], "x", [r"-3", r"\div2"],
         [r"y", r"y-3", r"\frac{y-3}{2}"], "{b:Picture it:} peel the present one layer per step. Whatever "
         "each peel does to the $x$ side, it does to the $y$ side too:")
    f.gap(6)
    f.p("{b:Step 3: do it on the formula, one layer per line, to both sides.}", 14, gap=6)
    step(f, r"y = 2x+3", "start")
    step(f, r"y\org{-3} = 2x+3\org{-3}", "take the outer layer off:\nsubtract 3 from BOTH sides")
    step(f, r"y-3 = 2x", "+3 and -3 cancel out on the right")
    step(f, r"\frac{y-3}{\pur{2}} = \frac{2x}{\pur{2}}", "next layer: divide BOTH\nsides by 2")
    step(f, r"\frac{y-3}{2} = x", "2x divided by 2 is just x")
    step(f, r"\grn{x = \frac{y-3}{2}}", "swap sides so x is on the left\n(allowed: = is a balance)")
    x, y = sp.symbols("x y")
    ch.check(sp.solve(sp.Eq(y, 2 * x + 3), x)[0], (y - 3) / 2)
    f.gap(4)
    f.p("{G:Test it with a number.} Put $x = 4$ into the original: $y = 2\\times4+3 = 11$. Now put "
        "$y = 11$ into the new formula: $x = \\frac{11-3}{2} = \\frac{8}{2} = 4$. We got the 4 back. "
        "The unwrapping worked. ✓", 13.5, gap=10)
    f.p("{h:Last on, first off.} Think of socks and shoes. You put socks on first and shoes second. "
        "To undress, the shoes come off first. Formulas are the same.", 14, C.PINK)


def wrong_order(ch):
    f = flow(ch)
    heading(f, "Why the order matters", room=300)
    f.p("What if you took the layers off in the wrong order, dividing by 2 first? Try it with numbers, "
        "where we know the answer should be $x = 4$ when $y = 11$:", 14, gap=8)
    y = f.reserve(90)
    pg = f.pg
    pg.text(L, y, "Right order", 14, C.GREEN, F.BOLD)
    pg.eq(L, y + 26, r"11\xrightarrow{-3}8\xrightarrow{\div 2}\grn{4}", 20)
    pg.tick(L + 170, y + 28, 14)
    pg.text(L + 260, y, "Wrong order", 14, C.RED, F.BOLD)
    pg.eq(L + 260, y + 26, r"11\xrightarrow{\div 2}5.5\xrightarrow{-3}\red{2.5}", 20)
    pg.xmark(L + 450, y + 30, 13)
    ch.check((11 - 3) / 2, 4)
    ch.check(sp.Rational(11, 2) - 3, sp.Rational(5, 2))
    f.p("The wrong order gives 2.5, which is wrong. Undoing has to happen in the {B:reverse} order "
        "of doing. That is why Step 1 (working out how the formula was built) matters so much.", 14,
        gap=12)
    heading(f, "The lecture example:  y = mx + c", room=330)
    f.p("Lecture 2 rearranges the straight-line formula (you will meet it properly in Chapter 20). "
        "It is exactly the same present, with letters where the numbers were: {p:$\\times m$} "
        "instead of $\\times2$, and {o:$+c$} instead of $+3$.", 14, gap=4)
    chain(f, "x", [r"\times m", r"+c"], "y", "wrapping:", [C.PURPLE, C.ORANGE])
    chain(f, "y", [r"-c", r"\div m"], "x", "unwrapping:", [C.ORANGE, C.PURPLE], reverse=True)
    peel(f, [r"+c", r"\times m"], [C.ORANGE, C.PURPLE], "x", [r"-c", r"\div m"],
         [r"y", r"y-c", r"\frac{y-c}{m}"])
    step(f, r"y-\org{c}=mx", "subtract c from both sides")
    step(f, r"\frac{y-c}{\pur{m}}=x", "divide both sides by m")
    step(f, r"\grn{x=\frac{y-c}{m}}", "swap sides")
    x, y, m, c = sp.symbols("x y m c")
    ch.check(sp.solve(sp.Eq(y, m * x + c), x)[0], (y - c) / m)


def minus_and_bottom(ch):
    f = flow(ch)
    heading(f, "When the letter has a minus in front", room=420)
    rule_box(f, "subject with a minus sign", [
        "If the letter's term is being {B:subtracted}, {B:add it to both sides} first. That moves it to the "
        "other side as a positive term.",
        "Then unwrap as usual. (Or multiply both sides by $-1$, which flips every sign.)",
    ], C.PINK)
    f.p("{b:Example:} make $x$ the subject of $y = 5 - 2x$.", 14, gap=6)
    step(f, r"y\org{+2x}=5", "add 2x to both sides:\nnow 2x is positive")
    step(f, r"2x=5\org{-y}", "subtract y from both sides")
    step(f, r"\grn{x=\frac{5-y}{2}}", "divide both sides by 2")
    x, y = sp.symbols("x y")
    ch.check(sp.solve(sp.Eq(y, 5 - 2 * x), x)[0], (5 - y) / 2)
    f.p("{G:Test:} $x = 1$ gives $y = 5 - 2 = 3$. New formula: $x = \\frac{5-3}{2} = 1$ ✓.", 13.5, gap=12)
    ch.check(sp.Rational(5 - 3, 2), 1)
    heading(f, "When the letter is on the bottom", room=280)
    rule_box(f, "subject in the denominator", [
        "{B:Multiply both sides by the denominator first}, so the letter comes up onto a top line.",
        "Then unwrap as usual: the letter is now in an ordinary layer.",
        "(If each side is a single fraction you may instead flip both sides; see the lecture example later.)",
    ], C.PINK)
    f.p("{b:Example:} make $R$ the subject of $P = \\frac{V}{R}$.", 14, gap=6)
    step(f, r"P\org{R}=V", "multiply both sides by R")
    step(f, r"\grn{R=\frac{V}{P}}", "divide both sides by P")
    P, V, R_ = sp.symbols("P V R", positive=True)
    ch.check(sp.solve(sp.Eq(P, V / R_), R_)[0], V / P)
    f.p("{G:Test:} $V = 12$, $R = 4$ gives $P = 3$, and $\\frac{12}{3} = 4$ ✓.", 13.5, gap=8)
    f.p("{b:Example:} make $v$ the subject of $t = \\frac{d}{v+2}$. The bottom is a whole bracket:", 14, gap=6)
    step(f, r"t\org{(v+2)}=d", "multiply both sides by (v + 2)")
    step(f, r"v+2=\frac{d}{\pur{t}}", "divide both sides by t")
    step(f, r"\grn{v=\frac{d}{t}-2}", "subtract 2 from both sides")
    t, d, v = sp.symbols("t d v", positive=True)
    ch.check(sp.solve(sp.Eq(t, d / (v + 2)), v)[0], d / t - 2)
    f.p("{G:Test:} $v = 3$, $d = 10$ gives $t = 2$; then $\\frac{10}{2} - 2 = 3$ ✓.", 13.5)
    ch.check(sp.Rational(10, 2) - 2, 3)


def temperature(ch):
    f = flow(ch)
    heading(f, "Three layers: Fahrenheit to Celsius", room=420)
    f.p("$F = \\frac{9}{5}C + 32$ is the same as $F = \\frac{9C}{5} + 32$. Make $C$ the subject.", 14,
        gap=4)
    f.p("{b:How it was wrapped:}  $C$ is multiplied by 9, then divided by 5, then 32 is added.", 14,
        gap=0)
    chain(f, "C", [r"\times 9", r"\div 5", r"+32"], "F", None, [C.PURPLE, C.BLUE, C.ORANGE])
    f.p("{b:Unwrap, last on first off:}  subtract 32, then {B:multiply} by 5 (undoes $\\div5$), then "
        "divide by 9.", 14, gap=0)
    chain(f, "F", [r"-32", r"\times 5", r"\div 9"], "C", None, [C.ORANGE, C.BLUE, C.PURPLE], reverse=True)
    peel(f, [r"+32", r"\div5", r"\times9"], [C.ORANGE, C.BLUE, C.PURPLE], "C", [r"-32", r"\times5", r"\div9"],
         [r"F", r"F-32", r"5(F-32)", r"\frac{5(F-32)}{9}"], "{b:Three layers, three peels:}")
    step(f, r"F = \frac{9C}{5}+32", "start")
    step(f, r"F\org{-32} = \frac{9C}{5}", "outer layer: subtract 32 from both sides")
    step(f, r"\blu{5}(F-32) = 9C", "next layer: multiply both sides by 5.\nBrackets: ALL of F - 32 gets x5")
    step(f, r"\frac{5(F-32)}{\pur{9}} = C", "last layer: divide both sides by 9")
    step(f, r"\grn{C = \frac{5(F-32)}{9}}", "swap sides")
    Fs, Cs = sp.symbols("F C")
    ch.check(sp.solve(sp.Eq(Fs, 9 * Cs / 5 + 32), Cs)[0], 5 * (Fs - 32) / 9)
    f.p("{G:Test:} water boils at 212 °F. $C = \\frac{5(212-32)}{9} = \\frac{5\\times180}{9} = "
        "\\frac{900}{9} = 100$ °C. ✓ Correct!", 13.5, gap=8)
    ch.check(sp.Rational(5 * (212 - 32), 9), 100)
    f.p("{R:Why the bracket?}  Without it, $5F - 32$ would mean \"multiply only F by 5, then take 32\". "
        "But the whole left side, $F - 32$, has to be multiplied by 5. The bracket keeps it together.",
        13.5)


def squares(ch):
    f = flow(ch)
    heading(f, "Layers with squares and roots", room=420)
    f.p("The area of a circle is $A = \\pi r^2$. Given the area, find the radius $r$.", 14, gap=4)
    f.p("{b:How it was wrapped:}  $r$ is {o:squared} first (that's $r^2$), then {p:multiplied by "
        "$\\pi$}. (Squaring happens before multiplying: powers come before times in the order of "
        "operations.)", 14, gap=0)
    chain(f, "r", [r"\text{square}", r"\times\pi"], "A", None, [C.ORANGE, C.PURPLE])
    chain(f, "A", [r"\div\pi", r"\sqrt{\ \ }"], "r", None, [C.PURPLE, C.ORANGE], reverse=True)
    peel(f, [r"\times\pi", r"(\ )^2"], [C.PURPLE, C.ORANGE], "r", [r"\div\pi", r"\sqrt{\ \ }"],
         [r"A", r"\frac{A}{\pi}", r"\sqrt{\frac{A}{\pi}}"])
    step(f, r"A=\pi r^2", "start")
    step(f, r"\frac{A}{\pur{\pi}}=r^2", "divide both sides by pi")
    step(f, r"\org{\sqrt{\frac{A}{\pi}}}=r", "square root both sides\n(undoes the squaring)")
    step(f, r"\grn{r=\sqrt{\frac{A}{\pi}}}", "swap sides")
    A, r = sp.symbols("A r", positive=True)
    ch.check(sp.solve(sp.Eq(A, sp.pi * r ** 2), r)[0], sp.sqrt(A / sp.pi))
    f.p("{G:Test:} a circle of radius 3 has $A = \\pi\\times9 \\approx 28.27$. Then "
        "$\\sqrt{28.27/\\pi} = \\sqrt{9} = 3$. ✓", 13.5, gap=8)
    ch.check_num(math.sqrt(math.pi * 9 / math.pi), 3)
    f.p("{h:A small print note:} $(-3)^2$ is also 9, so strictly $r$ could be $+3$ or $-3$ "
        "(written $\\pm3$). A radius can't be negative, so here we keep the positive one. When a "
        "question isn't about a length, remember the $\\pm$.", 13, C.BROWN, gap=12)
    rule_box(f, "cubes and cube roots", [
        "A cube is undone by a {B:cube root}: if $r^3=k$ then $r=\\sqrt[3]{k}$.",
        "There is only {B:one} cube root, and negatives are fine: $\\sqrt[3]{-8}=-2$ because $(-2)^3=-8$. "
        "So no $\\pm$ here.",
    ], C.PINK)
    f.p("{b:Example:} the volume of a sphere is $V = \\frac43\\pi r^3$. Make $r$ the subject. Wrapping: cube, "
        "then $\\times\\frac43\\pi$ (that is $\\times4$, $\\div3$, $\\times\\pi$). Unwrap in reverse:", 14, gap=6)
    step(f, r"3V=4\pi r^3", "multiply both sides by 3")
    step(f, r"\frac{3V}{\pur{4\pi}}=r^3", "divide both sides by 4 pi")
    step(f, r"\grn{r=\sqrt[3]{\frac{3V}{4\pi}}}", "cube root both sides, swap")
    Vs, rs = sp.symbols("V r", positive=True)
    ch.check(sp.solve(sp.Eq(Vs, sp.Rational(4, 3) * sp.pi * rs ** 3), rs)[0], sp.cbrt(3 * Vs / (4 * sp.pi)))
    ch.check_num((3 * (4 / 3 * math.pi * 8) / (4 * math.pi)) ** (1 / 3), 2)
    f.p("{G:Test:} $r = 2$ gives $V = \\frac43\\pi\\times8 \\approx 33.51$; then "
        "$\\sqrt[3]{3\\times33.51/(4\\pi)} = \\sqrt[3]{8} = 2$ ✓.", 13.5)


def pendulum(ch):
    f = flow(ch)
    f.new_page()
    heading(f, "The pendulum, one layer at a time")
    f.p("This is the big example from Lecture 2 (and the one from Part 0, where you learned to "
        "read it). Make $l$ (the string length) the subject:", 14, gap=4)
    f.eq(r"T=2\pi\sqrt{\frac{l}{g}}", 30, gap=4)
    f.p("{b:How it was wrapped}, reading from the inside out: $l$ is {b:divided by $g$}, then "
        "{o:square-rooted}, then {p:multiplied by $2\\pi$}.", 14, gap=0)
    chain(f, "l", [r"\div g", r"\sqrt{\ \ }", r"\times 2\pi"], "T", None, [C.BLUE, C.ORANGE, C.PURPLE])
    f.p("{b:Unwrapping} (reverse order, undo buttons): divide by $2\\pi$, then {o:square}, then "
        "multiply by $g$.", 14, gap=0)
    chain(f, "T", [r"\div 2\pi", r"\text{square}", r"\times g"], "l", None, [C.PURPLE, C.ORANGE, C.BLUE],
          reverse=True)
    peel(f, [r"\times2\pi", r"\sqrt{\ \ }", r"\div g"], [C.PURPLE, C.ORANGE, C.BLUE], "l",
         [r"\div2\pi", r"(\ )^2", r"\times g"],
         [r"T", r"\frac{T}{2\pi}", r"\frac{T^2}{4\pi^2}", r"\frac{gT^2}{4\pi^2}"],
         "{b:The present, peeled from the outside in:}")
    step(f, r"T=2\pi\sqrt{\frac{l}{g}}", "start")
    step(f, r"\frac{T}{\pur{2\pi}}=\sqrt{\frac{l}{g}}", "outer layer: divide both sides by 2 pi")
    step(f, r"\org{\left(\frac{T}{2\pi}\right)^2}=\frac{l}{g}", "middle layer: square both sides\n"
         "(squaring undoes the root)")
    step(f, r"\frac{T^2}{4\pi^2}=\frac{l}{g}", "tidy up: square the top (T x T) and\n"
         "the bottom (2 pi x 2 pi = 4 pi squared)")
    step(f, r"\blu{g}\times\frac{T^2}{4\pi^2}=l", "inner layer: multiply both sides by g")
    step(f, r"\grn{l=\frac{gT^2}{4\pi^2}}", "swap sides and tidy up.\nThis matches your lecture slide!")
    T, l, g = sp.symbols("T l g", positive=True)
    ch.check(sp.solve(sp.Eq(T, 2 * sp.pi * sp.sqrt(l / g)), l)[0], g * T ** 2 / (4 * sp.pi ** 2))
    Tv = 2 * math.pi * math.sqrt(1 / 9.81)
    ch.check_num(9.81 * Tv ** 2 / (4 * math.pi ** 2), 1.0)
    f.p("{G:Test:} with $g = 9.81$ and a 1 metre string, $T = 2\\pi\\sqrt{1/9.81} \\approx 2.006$ "
        "seconds. Put $T = 2.006$ into the new formula: $l = 9.81\\times2.006^2/(4\\pi^2) \\approx "
        "1.00$ metre. ✓", 13.5)


def fraction_letter(ch):
    f = flow(ch)
    heading(f, "When the letter is on the bottom of a fraction", room=420)
    f.p("Lecture 2's hardest example: make $z$ the subject of", 14, gap=4)
    f.eq(r"\frac{1}{x}=\frac{2}{y}-\frac{3}{z}", 28, gap=6)
    rule_box(f, "flipping both sides", [
        "If {B:each side is one single fraction}, you may flip both sides: $\\frac ab=\\frac cd$ gives "
        "$\\frac ba=\\frac dc$.",
        "{R:Never flip term by term.} Combine each side into one fraction first (Chapter 13).",
    ], C.PINK)
    f.p("This isn't a simple chain of layers, because there are several fractions. Plan: {b:(1) get "
        "the $z$ fraction alone on one side, (2) combine the other side into one fraction, (3) flip "
        "both sides.}", 14, gap=8)
    step(f, r"\frac{1}{x}\org{+\frac{3}{z}}=\frac{2}{y}", "add 3/z to both sides\n(it was being taken away)")
    step(f, r"\org{\frac{3}{z}}=\frac{2}{y}\org{-\frac{1}{x}}", "subtract 1/x from both sides:\nnow the z fraction is alone")
    step(f, r"\frac{3}{z}=\frac{2\blu{x}}{y\blu{x}}-\frac{1\blu{y}}{x\blu{y}}", "re-cut to a common\nbottom, xy (Chapter 13)")
    step(f, r"\frac{3}{z}=\frac{2x-y}{xy}", "same bottoms: combine the tops")
    step(f, r"\frac{z}{3}=\frac{xy}{2x-y}", "flip BOTH sides upside down.\nAllowed: if two things are equal,\ntheir reciprocals are equal too")
    step(f, r"\grn{z=\frac{3xy}{2x-y}}", "multiply both sides by 3")
    x, y, z = sp.symbols("x y z")
    ch.check(sp.solve(sp.Eq(1 / x, 2 / y - 3 / z), z)[0], 3 * x * y / (2 * x - y))
    f.p("{G:Test:} pick $x = 1$, $y = 1$. The new formula gives $z = \\frac{3}{2-1} = 3$. Check in the "
        "original: $\\frac11 = \\frac21 - \\frac33$ means $1 = 2 - 1$. ✓", 13.5, gap=8)
    f.p("{R:Only flip when each side is ONE single fraction.}  Flipping $\\frac{2}{y} - \\frac{1}{x}$ "
        "term by term (into $\\frac{y}{2} - \\frac{x}{1}$) is wrong. Test with $x=1, y=1$: "
        "$\\frac21-\\frac11 = 1$, flipped is 1; but $\\frac12 - 1 = -\\frac12$. Not the same!", 13.5)


def twice(ch):
    f = flow(ch)
    heading(f, "When the letter appears twice", room=520)
    rule_box(f, "subject appearing more than once", [
        "Clear fractions (multiply both sides by the bottom).",
        "Expand brackets, then collect every term containing the letter on {B:one} side, everything else "
        "on the other.",
        "{B:Factorise}: take the letter out as a common factor, so it appears once.",
        "Divide both sides by the bracket ({R:that bracket must not be 0}).",
    ], C.PINK, numbered=True, tag="PROCEDURE")
    f.p("Sometimes the letter you want is in two places, so it isn't wrapped in one neat present. "
        "Make $x$ the subject of", 14, gap=4)
    f.eq(r"y=\frac{x+1}{x-1}", 28, gap=6)
    f.p("{b:Plan: (1) get rid of the fraction, (2) collect every $x$ on one side, (3) take $x$ out as a "
        "common factor, (4) divide.}", 14, gap=8)
    step(f, r"y\org{(x-1)}=x+1", "multiply both sides by (x - 1):\nthe fraction disappears")
    step(f, r"\org{yx-y}=x+1", "open the bracket (Chapter 11)")
    step(f, r"yx\blu{-x}=1+y", "move the x terms left, the rest right:\nsubtract x, add y, on both sides")
    step(f, r"\blu{x}(y-1)=1+y", "take x out as a common factor\n(Chapter 12): now x appears ONCE")
    step(f, r"\grn{x=\frac{1+y}{y-1}}", "divide both sides by (y - 1)")
    x, y = sp.symbols("x y")
    ch.check(sp.solve(sp.Eq(y, (x + 1) / (x - 1)), x)[0], (1 + y) / (y - 1))
    f.p("{G:Test:} $x = 3$ gives $y = \\frac{4}{2} = 2$. New formula with $y = 2$: "
        "$x = \\frac{3}{1} = 3$. ✓", 13.5, gap=8)
    f.p("{h:The factorising step is the key idea.} Once all the $x$'s are on one side, factorising "
        "turns \"$x$ in two places\" into \"$x$ in one place\", and then it's an ordinary one-layer "
        "unwrap.", 13.5, C.PINK)


def safety(ch):
    f = flow(ch)
    heading(f, "Two safety rules", room=440)
    rule_box(f, "don't divide by something that could be zero", [
        "Dividing both sides by an expression is only allowed when that expression is {B:not 0}. In the last "
        "example, dividing by $(y-1)$ needs $y\\ne1$; write that condition down.",
        "If you divide by a letter in an {B:equation}, you can lose an answer. Move everything to one side "
        "and factorise instead.",
    ], C.PINK)
    f.p("{b:Example:} $x^2 = 3x$. Dividing by $x$ gives $x = 3$ and {R:loses} $x = 0$. Safe way:", 14, gap=6)
    step(f, r"x^2-3x=0\ \Rightarrow\ x(x-3)=0", "everything to one side, factorise")
    step(f, r"\grn{x=0\ \text{ or }\ x=3}", "either factor can be 0")
    x = sp.symbols("x")
    ch.check(sp.solve(x ** 2 - 3 * x, x), [0, 3])
    rule_box(f, "squaring both sides can add false answers", [
        "Squaring both sides is allowed, but it can create answers that {B:don't fit the original}, because "
        "$3^2$ and $(-3)^2$ are both 9.",
        "So after squaring, {B:check every answer in the original} and throw out any that fail.",
    ], C.PINK)
    f.p("{b:Example:} $\\sqrt{x} = -3$. Squaring gives $x = 9$, but $\\sqrt9 = 3$, not $-3$. So there is "
        "{B:no solution}: a square root (the $\\sqrt{\\ }$ sign) is never negative.", 14, gap=6)
    ch.check(sp.solve(sp.sqrt(x) + 3, x), [])
    f.p("{b:Example:} $\\sqrt{x+3} = x - 3$. Square: $x + 3 = x^2 - 6x + 9$, so $x^2 - 7x + 6 = 0$, "
        "$(x-1)(x-6) = 0$. Check $x = 6$: $\\sqrt9 = 3 = 6 - 3$ ✓. Check $x = 1$: $\\sqrt4 = 2$ but "
        "$1 - 3 = -2$ ✗. Only $x = 6$ is an answer.", 14)
    ch.check(sp.solve(x ** 2 - 7 * x + 6, x), [1, 6])
    ch.check(sp.solve(sp.sqrt(x + 3) - (x - 3), x), [6])


def find_value(ch):
    f = flow(ch)
    heading(f, "Using a rearranged formula: find the missing value", room=520)
    f.p("Exams rarely stop at the rearranged formula. Usually you're given {B:some} of the values and asked "
        "for the one that's missing:", 14, gap=6)
    rule_box(f, "finding an unknown from a formula", [
        "Circle the letter you need to find. That's the subject you want.",
        "{B:Rearrange} the formula to make it the subject (letters only, no numbers yet).",
        "{B:Substitute} the values you know. Put negative numbers in brackets.",
        "Calculate, with units. {B:Check} by putting every value back into the original formula.",
    ], C.PINK, numbered=True, tag="PROCEDURE")
    f.p("(Substituting first and then solving also works. Rearranging first gives a formula you can reuse, "
        "and the steps are easier to check.)", 12.5, C.GREY, gap=8)
    f.p("{b:Example 1 (motion):} $v^2 = u^2 + 2as$. Find $s$ when $v = 10$, $u = 4$, $a = 3$.", 14, gap=6)
    step(f, r"v^2\org{-u^2}=2as", "rearrange: subtract u²")
    step(f, r"s=\frac{v^2-u^2}{2a}", "divide by 2a, swap")
    step(f, r"s=\frac{10^2-4^2}{2\times3}=\frac{100-16}{6}=\frac{84}{6}", "substitute")
    step(f, r"\grn{s=14}", "calculate")
    v, u, a, s = sp.symbols("v u a s")
    ch.check(sp.solve(sp.Eq(v ** 2, u ** 2 + 2 * a * s), s)[0], (v ** 2 - u ** 2) / (2 * a))
    ch.check(sp.Rational(10 ** 2 - 4 ** 2, 2 * 3), 14)
    f.p("{G:Check:} $u^2 + 2as = 16 + 2\\times3\\times14 = 16 + 84 = 100 = 10^2$ ✓.", 13.5, gap=10)
    ch.check(16 + 2 * 3 * 14, 100)
    f.p("{b:Example 2 (pendulum):} $T = 2\\pi\\sqrt{\\frac lg}$. How long must the string be for $T = 2$ "
        "seconds, with $g = 9.81$?", 14, gap=6)
    step(f, r"l=\frac{gT^2}{4\pi^2}", "rearranged earlier in this chapter")
    step(f, r"l=\frac{9.81\times2^2}{4\pi^2}=\frac{39.24}{39.48}", "substitute")
    step(f, r"\grn{l\approx0.994\ \text{m}}", "about 99 cm")
    ch.check_num(9.81 * 4 / (4 * math.pi ** 2), 0.994, tol=0.001)
    f.p("{G:Check:} $2\\pi\\sqrt{0.994/9.81} = 2\\pi\\times0.3183 \\approx 2.00$ s ✓.", 13.5, gap=10)
    ch.check_num(2 * math.pi * math.sqrt(0.994 / 9.81), 2.0, tol=0.005)
    f.p("{b:Example 3 (energy):} $E = \\frac12mv^2$. Find $v$ when $E = 100$ J and $m = 8$ kg.", 14, gap=6)
    step(f, r"v=\sqrt{\frac{2E}{m}}=\sqrt{\frac{200}{8}}=\sqrt{25}", "rearrange (×2, ÷m, √), substitute")
    step(f, r"\grn{v=5\ \text{m/s}}", "a speed: keep the + root")
    ch.check(sp.sqrt(sp.Rational(2 * 100, 8)), 5)
    f.p("{G:Check:} $\\frac12\\times8\\times5^2 = 4\\times25 = 100$ ✓.", 13.5)
    ch.check(sp.Rational(1, 2) * 8 * 25, 100)


def mistakes(ch):
    f = flow(ch)
    heading(f, "Three classic slip-ups (tested with numbers)", room=440)
    f.p("Each one starts from the same kind of formula, shows the slip, then the correct move.", 14, gap=8)
    items = [
        ("Dividing only part of a side.", r"y=2x+3", "Move: divide both sides by 2.",
         r"\frac{y}{2}=x+3", "only the 2x was divided; the 3 was forgotten",
         r"\frac{y}{2}=\frac{2x+3}{2}=x+\frac{3}{2}", "the WHOLE side goes over 2, so the 3 is halved too",
         "Test with x = 4, y = 11: the wrong version says 5.5 = 7. The right version says 5.5 = 4 + 1.5. ✓ "
         "Divide EVERY term."),
        ("Undoing in the wrong order.", r"y=2x+3", "Move: make x the subject.",
         r"x=\frac{y}{2}-3", "took off ×2 first, but it's the INNER layer",
         r"x=\frac{y-3}{2}", "−3 first (outer layer), then ÷2",
         "With y = 11 the wrong one gives 2.5, the right one gives 4. ✓ Last on, first off."),
        ("Square-rooting term by term.", r"c^2=a^2+b^2", "Move: square-root both sides to get c.",
         r"c=a+b", "rooted a² and b² separately",
         r"c=\sqrt{a^2+b^2}", "the root goes over the WHOLE side",
         "Test with a = 3, b = 4: the right answer is the square root of 25, which is 5. The wrong one gives 7. "
         "(This is also a warning on your Lecture 2 slides.)"),
    ]
    for head, start_, move, wrong, wnote, right, rnote, why in items:
        wh = f.pg.rich_h(why, W - 20, 12.5)
        h0 = f.pg.eq_size(start_, 19)[1]
        h1 = f.pg.eq_size(wrong, 19)[1]
        h2 = f.pg.eq_size(right, 19)[1]
        y = f.reserve(34 + h0 + 12 + h1 + 12 + h2 + wh + 22)
        pg = f.pg
        pg.text(L, y, head, 15, C.RED, F.BOLD)
        yy = y + 26
        pg.note(L + 10, yy + 2, "start:", C.INK, 15)
        w0, _ = pg.eq(L + 70, yy, start_, 19)
        pg.note(L + 90 + w0, yy + 2, move, C.GREY, 15)
        yy += h0 + 12
        pg.note(L + 10, yy + 2, "wrong:", C.RED, 15)
        w1, _ = pg.eq(L + 70, yy, wrong, 19)
        pg.cross(L + 64, yy - 4, w1 + 12, h1 + 8)
        pg.note(L + 100 + w1, yy + 2, wnote, C.RED, 14, w=R - (L + 100 + w1))
        yy += h1 + 12
        pg.note(L + 10, yy + 2, "right:", C.GREEN, 15)
        w2, _ = pg.eq(L + 70, yy, right, 19, C.GREEN)
        pg.tick(L + 80 + w2, yy + 4, 13)
        pg.note(L + 104 + w2, yy + 2, rnote, C.GREEN, 14, w=R - (L + 104 + w2))
        pg.rich(L + 10, yy + h2 + 8, why, W - 20, 12.5, C.GREY)
    ch.check(sp.Rational(11, 2), 4 + sp.Rational(3, 2))
    ch.check_true(sp.sqrt(3 ** 2 + 4 ** 2) == 5)


def routine(ch):
    f = flow(ch)
    heading(f, "The unwrapping routine", room=400)
    steps = [("Circle the letter you want.", C.BLUE),
             ("Work out how it was wrapped: what happens to it, in order? Draw the chain.", C.PURPLE),
             ("Messy? Clear fractions first (multiply both sides), collect the letter on one side, and "
              "factorise so it appears once.", C.ORANGE),
             ("Unwrap: last layer first, using the undo buttons, doing the same to the whole of both sides.", C.PINK),
             ("Test with numbers.", C.GREEN)]
    for i, (s, col) in enumerate(steps):
        h = f.pg.rich_h(s, 400, 13.5)
        y = f.reserve(h + 26)
        pg = f.pg
        pg.circle(L + 18, y + 12, 14, col, 2, fillcolor=C.LIGHT[col])
        pg.text(L + 18, y + 3, str(i + 1), 13, col, F.BOLD, align="center")
        pg.rich(L + 45, y + 3, s, 400, 13.5)
        if i < len(steps) - 1:
            pg.arrow(L + 18, y + 28, L + 18, y + h + 24, "#cccccc", 1.2, head=4)
    f.gap(6)
    f.p("{h:Coming later:} Chapter 15 uses exactly the same moves to find the value of a mystery "
        "number, and Chapter 22 adds one more undo button (the logarithm), which undoes powers like "
        "$e^x$. That's how Lecture 7's capacitor formula gets rearranged.", 13, C.GREY)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Balance rule", None, "whatever you do to one side, do to the {B:whole} of the other side"),
        ("Undo buttons", r"+\leftrightarrow-,\quad\times\leftrightarrow\div,\quad x^2\leftrightarrow\pm\sqrt{x},"
         r"\quad x^3\leftrightarrow\sqrt[3]{x}", "flip undoes flip"),
        ("Order", None, "build the chain of layers, then undo them in {B:reverse} order: last on, first off"),
        ("Minus in front", r"y=5-2x\ \Rightarrow\ 2x=5-y", "add the subtracted term to both sides first"),
        ("Letter on the bottom", r"P=\frac VR\ \Rightarrow\ PR=V\ \Rightarrow\ R=\frac VP",
         "multiply both sides by the bottom first"),
        ("Flipping", r"\frac ab=\frac cd\ \Rightarrow\ \frac ba=\frac dc", "only when each side is ONE fraction"),
        ("Letter twice", r"yx-x=1+y\ \Rightarrow\ x(y-1)=1+y", "collect, factorise, divide"),
        ("Roots", r"r^2=k\Rightarrow r=\pm\sqrt k,\qquad r^3=k\Rightarrow r=\sqrt[3]{k}",
         "keep $+$ only for lengths, speeds and other sizes"),
        ("Safety", None, "{R:never divide by something that could be 0}; after squaring both sides, check "
         "every answer in the original"),
        ("Find a value", None, "rearrange first, then substitute, then check in the original formula"),
    ], C.PINK, title="Rearranging rules")


def your_turn(ch):
    f = flow(ch)
    f.new_page()
    heading(f, "Your turn: fill in the chains")
    groups = [
        ("Fill in the chains", ["y = 5x − 4 (x)", "P = V/R (V)", "v = u + at (a)", "E = ½mv² (v)", "s = √(A/6) (A)"],
         "1. x = (y + 4)/5   2. V = PR   3. a = (v − u)/t   4. v = √(2E/m)   5. A = 6s²"),
        ("Minus signs, bottoms and cubes", ["y = 7 − 3x: make x the subject", "I = V/R: make R the subject",
                                            "f = 1/(x + 3): make x the subject", "V = x³/3: make x the subject",
                                            "y = (2x + 1)/(x − 3): make x the subject"],
         "6. x = (7 − y)/3   7. R = V/I   8. x = 1/f − 3   9. x = ∛(3V)   10. x = (3y + 1)/(y − 2)"),
        ("Find the unknown", ["v² = u² + 2as. Find s when v = 20, u = 10, a = 5.",
                              "v = u + at. Find t when v = 25, u = 5, a = 4.",
                              "A = πr². Find r when A = 154, using π ≈ 22/7.",
                              "F = 9C/5 + 32. Find C when F = 50.",
                              "y = (x + 1)/(x − 1). Find x when y = 3.",
                              "E = ½mv². Find m when E = 90 and v = 6."],
         "11. s = 30 (s = (v² − u²)/(2a) = 300/10)   12. t = 5 (t = (v − u)/a)   13. r = 7 (r² = A/π = 49)   "
         "14. C = 10 (C = 5(F − 32)/9)   15. x = 2 (x = (y + 1)/(y − 1))   16. m = 5 (m = 2E/v² = 180/36)"),
    ]
    f.p("For each formula, fill in the {p:wrapping} boxes (what happens to the letter, in order), then "
        "the {g:unwrapping} boxes (reverse order, undo buttons), then write the rearranged formula "
        "on the line. Answers to 1 to 5 are on the last page; the later groups have theirs in grey.", 13.5,
        gap=10)
    qs = [(r"y=5x-4", "x", "y", 2), (r"P=\frac{V}{R}", "V", "P", 1), (r"v=u+at", "a", "v", 2),
          (r"E=\tfrac12 mv^2", "v", "E", 3), (r"s=\sqrt{\frac{A}{6}}", "A", "s", 2)]
    for i, (lat, want, subj, n) in enumerate(qs):
        eh = f.pg.eq_size(lat, 20)[1]
        y = f.reserve(eh + 92)
        pg = f.pg
        pg.text(L, y + eh / 2 - 9, f"{i + 1}.", 15, C.PINK, F.BOLD)
        pg.eq(L + 24, y, lat, 20)
        pg.note(L + 200, y + eh / 2 - 11, f"make {want} the subject", C.GREY, 16)
        cy = y + eh + 26
        pg.note(L + 10, cy - 11, "wrap:", C.PURPLE, 15)
        mini_chain(pg, L + 75, cy, want, [""] * n, subj, [C.PURPLE], dashed=True, box_w=70)
        cy += 40
        pg.note(L + 10, cy - 11, "unwrap:", C.GREEN, 15)
        end = mini_chain(pg, L + 75, cy, subj, [""] * n, want, [C.GREEN], dashed=True, box_w=70)
        pg.note(end + 8, cy - 11, f"so  {want} =", C.GREY, 16)
        pg.line(end + 60, cy + 10, R, cy + 10, "#bbbbbb", 0.8)
    n = len(qs) + 1
    f.gap(10)
    for title, gqs, ans in groups[1:]:
        f.need(40 + 21 * len(gqs) + 50)
        f.text(title, 14, C.PINK, F.BOLD, gap=6)
        for qq in gqs:
            f.text(f"{n}. {qq}", 13, gap=5, x=L + 14)
            n += 1
        ans = "   ".join(part.replace(" ", "\u00a0") for part in ans.split("   "))
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    x, y, V, I, R_, fs = sp.symbols("x y V I R f", positive=True)
    ch.check(sp.solve(sp.Eq(y, 7 - 3 * x), x)[0], (7 - y) / 3)
    ch.check(sp.solve(sp.Eq(I, V / R_), R_)[0], V / I)
    ch.check(sp.solve(sp.Eq(fs, 1 / (x + 3)), x)[0], 1 / fs - 3)
    ch.check(sp.solve(sp.Eq(V, x ** 3 / 3), x)[0], sp.cbrt(3 * V))
    xs, ys = sp.symbols("x y")
    ch.check(sp.solve(sp.Eq(ys, (2 * xs + 1) / (xs - 3)), xs)[0], (3 * ys + 1) / (ys - 2))
    ch.check(sp.Rational(20 ** 2 - 10 ** 2, 2 * 5), 30)
    ch.check(sp.Rational(25 - 5, 4), 5)
    ch.check(sp.sqrt(154 / sp.Rational(22, 7)), 7)
    ch.check(sp.Rational(5 * (50 - 32), 9), 10)
    ch.check(sp.Rational(3 + 1, 3 - 1), 2)
    ch.check(sp.Rational(2 * 90, 6 ** 2), 5)
    ch.check([sp.Rational(9 * 10, 5) + 32, sp.Rational(2 + 1, 2 - 1), sp.Rational(1, 2) * 5 * 36], [50, 3, 90])


def answers(ch):
    f = flow(ch)
    f.new_page()
    heading(f, "Answers")
    x, y, V, P, R_, v, u, a, t, E, m, s, A = sp.symbols("x y V P R v u a t E m s A", positive=True)
    ans = [
        ("x", [r"\times5", r"-4"], "y", "y", [r"+4", r"\div5"], "x", r"x=\frac{y+4}{5}"),
        ("V", [r"\div R"], "P", "P", [r"\times R"], "V", r"V=PR"),
        ("a", [r"\times t", r"+u"], "v", "v", [r"-u", r"\div t"], "a", r"a=\frac{v-u}{t}"),
        ("v", [r"\text{sq}", r"\times m", r"\div 2"], "E", "E", [r"\times2", r"\div m", r"\sqrt{\ }"], "v",
         r"v=\sqrt{\frac{2E}{m}}"),
        ("A", [r"\div6", r"\sqrt{\ }"], "s", "s", [r"\text{sq}", r"\times6"], "A", r"A=6s^2"),
    ]
    ch.check(sp.solve(sp.Eq(y, 5 * x - 4), x)[0], (y + 4) / 5)
    ch.check(sp.solve(sp.Eq(P, V / R_), V)[0], P * R_)
    ch.check(sp.solve(sp.Eq(v, u + a * t), a)[0], (v - u) / t)
    ch.check(sp.solve(sp.Eq(E, m * v ** 2 / 2), v)[0], sp.sqrt(2 * E / m))
    ch.check(sp.solve(sp.Eq(s, sp.sqrt(A / 6)), A)[0], 6 * s ** 2)
    for i, (s0, ops, e0, s1, ops2, e1, res) in enumerate(ans):
        y0 = f.reserve(100)
        pg = f.pg
        pg.text(L, y0 + 8, f"{i + 1}.", 15, C.PINK, F.BOLD)
        mini_chain(pg, L + 30, y0 + 16, s0, ops, e0, [C.PURPLE], size=14)
        mini_chain(pg, L + 30, y0 + 56, s1, ops2, e1, [C.GREEN], size=14)
        pg.eq(R - 10, y0 + 36, res, 22, C.GREEN, align="right", valign="middle")
    f.p("{h:In question 4,} $\\tfrac12 mv^2$ means: square $v$, times by $m$, then halve (divide by 2). "
        "So unwrapping is: double, divide by $m$, square root.", 13, C.PINK)


def build(ch):
    title_page(ch)
    subject(ch)
    balance(ch)
    first_unwrap(ch)
    wrong_order(ch)
    minus_and_bottom(ch)
    temperature(ch)
    squares(ch)
    pendulum(ch)
    fraction_letter(ch)
    twice(ch)
    safety(ch)
    find_value(ch)
    mistakes(ch)
    routine(ch)
    summary(ch)
    your_turn(ch)
    answers(ch)
