"""Chapter 35 - Chain, product and quotient rules (Lecture 15). Differentiating again and again (a
staircase down to zero); a function inside a function as nesting dolls; the chain rule as gears whose
rates multiply; the product rule as a rectangle growing on two sides; the quotient rule as a product in
disguise, with three roads to the same answer; implicit differentiation as luggage tags on every y;
and a sorting table for choosing the rule."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 35
NUM = 35
TITLE = "Chain, product and quotient rules"
SHORT = "Rules"
SLUG = "Rules"
ACCENT = C.PURPLE
REQUIRES = ["derivative", "dy-dx-notation", "power-rule", "standard-derivatives", "sum-rule-derivative",
            "second-derivative", "expand-brackets", "negative-powers", "index-laws", "function-notation",
            "composite-function", "natural-log", "e-number", "sine", "cosine", "factorise-common-factor",
            "rate-of-change", "perpendicular-gradients", "circle-equation", "subject-of-formula"]
INTRODUCES = ["higher-derivatives", "chain-rule", "product-rule", "quotient-rule", "implicit-differentiation",
              "explicit-implicit"]

PAPER = "#fcf9fe"
x, t = sp.symbols("x t")


def icon(pg, x0, y0):
    gear(pg, x0 + 7, y0 + 10, 5, 6, C.PURPLE, 1.0, tooth=2.5)
    gear(pg, x0 + 15, y0 + 5, 3, 5, C.PURPLE, 1.0, tooth=2)


def sec(f, t_, **kw):
    section(f, t_, C.PURPLE, icon, **kw)


def gear(pg, cx, cy, r_, teeth, col, w=1.4, tooth=6, fill=None):
    pts = []
    n = teeth * 4
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        rr = r_ + (tooth if (i % 4) in (1, 2) else 0)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    if fill:
        pg.fillpoly(pts, fill)
    pg.poly(pts, col, w)
    pg.circle(cx, cy, max(2.0, r_ * 0.18), col, w)


def doll(pg, cx, cy, s, col, fill):
    pg.ellipse(cx, cy + 22 * s, 42 * s, 46 * s, col, 1.4, fillcolor=fill)
    pg.circle(cx, cy - 36 * s, 24 * s, col, 1.4, fillcolor=fill)
    pg.dot(cx - 8 * s, cy - 40 * s, 1.8, C.INK)
    pg.dot(cx + 8 * s, cy - 40 * s, 1.8, C.INK)
    pg.arc(cx, cy - 34 * s, 9 * s, 200, 340, C.INK, 1.0)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 35, "Chain, product and quotient rules", "rates multiply, one layer at a time", C.PURPLE,
                     PAPER)
    cy = 265
    specs = [(L + 70, 34, 9, C.ORANGE, "t"), (L + 160, 48, 13, C.BLUE, "z = 4t + 5"),
             (L + 247, 28, 8, C.PURPLE, "s = z³")]
    for cx, r_, n, col, nm in specs:
        gear(pg, cx, cy, r_, n, col, 1.6, fill=C.LIGHT[col])
        pg.text(cx - 50, cy + r_ + 12, nm, 12, col, F.BOLD, w=100, align="center")
    pg.arc(L + 70, cy, 20, 30, 150, C.INK, 1.2, arrow=True)
    pg.arc(L + 160, cy, 30, 150, 30, C.INK, 1.2, arrow=True)
    pg.arc(L + 247, cy, 16, 30, 150, C.INK, 1.2, arrow=True)
    pg.text(L + 100, cy - 78, "×4", 13, C.RED, F.BOLD)
    pg.text(L + 196, cy - 70, "×3z²", 13, C.RED, F.BOLD)
    pg.note(L + 300, 205, "Turn the first gear once: the\nmiddle one turns 4 times as fast,\nthe last one "
            "3z² times as fast\nas the middle. Altogether\n4 × 3z². Rates multiply.", C.PURPLE, 15, w=R - L - 300)
    f = ch.flow(top=365)
    f.p("Chapter 34's rules handle one simple term at a time. Real formulas are built from pieces: one "
        "thing {B:inside} another, two things {B:multiplied}, one thing {B:divided} by another. Each way of "
        "building gets its own rule and its own picture:", 14, gap=8)
    f.p("• {B:chain rule}: gears turning gears (and nesting dolls)\n• {B:product rule}: a rectangle growing "
        "on two sides\n• {B:quotient rule}: a product wearing a disguise\n• {B:implicit differentiation}: every "
        "y wears a luggage tag", 14, gap=10, x=L + 10, w=W - 10)
    f.p("{y:Goes with} {B:Lecture 15} {y:(higher-order derivatives, functions of functions, chain rule, "
        "product rule, quotient rule, options, implicit differentiation).}", 12.5)


def higher(ch):
    f = flow(ch)
    sec(f, "Differentiate again, and again", room=460)
    f.p("You can differentiate a derivative. Lecture 15: velocity differentiated is acceleration; "
        "acceleration differentiated says how the acceleration changes. For $y = 2x^3$ each "
        "differentiation walks one step down the stairs:", 14, gap=10)
    y_ = f.reserve(152)
    pg = f.pg
    items = [("y", "2x^3"), (r"\frac{\dd y}{\dd x}", "6x^2"), (r"\frac{\dd^2y}{\dd x^2}", "12x"),
             (r"\frac{\dd^3y}{\dd x^3}", "12"), (r"\frac{\dd^4y}{\dd x^4}", "0")]
    for k, (nm, val) in enumerate(items):
        x0, y0 = L + 5 + k * 97, y_ + 14 + k * 20
        top = y0 + 26
        pg.rect(x0, top, 92, y_ + 150 - top, C.PURPLE, 0.8, fillcolor=C.LIGHT[C.PURPLE])
        pg.eq(x0 + 46, y0 - 12, nm, 12, C.GREY, align="center")
        pg.eq(x0 + 46, top + 3, val, 17, C.PURPLE if k < 4 else C.RED, align="center")
        if k < 4:
            pg.arrow(x0 + 74, top - 4, x0 + 100, top + 16, C.GREY, 1.0, head=4)
    ch.check([sp.diff(2 * x ** 3, x, k) for k in range(5)], [2 * x ** 3, 6 * x ** 2, 12 * x, 12, 0])
    ch.term("higher derivatives", "differentiate repeatedly: d²y/dx², d³y/dx³, …, dⁿy/dxⁿ")
    f.p("Powers of $x$ eventually vanish; sine and cosine cycle for ever (Chapter 34's wheel). "
        "Lecture 15's examples:", 14, gap=6)
    step(f, r"y=4x^3-2x^2+\frac1x+2", "1/x is x⁻¹", size=17)
    step(f, r"\frac{\dd y}{\dd x}=12x^2-4x-\frac{1}{x^2}", "x⁻¹ → −1x⁻²", size=17)
    step(f, r"\frac{\dd^2y}{\dd x^2}=24x-4+\frac{2}{x^3}", "−x⁻² → +2x⁻³", size=17, color=C.PURPLE)
    yy = 4 * x ** 3 - 2 * x ** 2 + 1 / x + 2
    ch.check(sp.diff(yy, x, 2), 24 * x - 4 + 2 / x ** 3)
    f.p("{R:Slide slip:} Lecture 15 writes $+\\frac{1}{x^3}$ in the second derivative. The power rule on "
        "$-x^{-2}$ gives $(-1)(-2)x^{-3} = +2x^{-3}$, so it's $\\frac{2}{x^3}$.", 13.5, gap=8)
    step(f, r"y=\sin x+2x^3\ \Rightarrow\ \frac{\dd y}{\dd x}=\cos x+6x^2\ \Rightarrow\ \frac{\dd^2y}{\dd x^2}=-\sin x+12x",
         "", size=15)
    ch.check(sp.diff(sp.sin(x) + 2 * x ** 3, x, 2), -sp.sin(x) + 12 * x)


def dolls(ch):
    f = flow(ch)
    sec(f, "A function inside a function", room=520)
    f.p("Lecture 15: $s = (4t + 5)^3$. It's one function ({B:cube it}) wrapped around another "
        "($4t + 5$), like nesting dolls:", 14, gap=10)
    y_ = f.reserve(165)
    pg = f.pg
    doll(pg, L + 70, y_ + 70, 1.2, C.BLUE, C.LIGHT[C.BLUE])
    pg.eq(L + 70, y_ + 82, r"(\quad)^3", 16, C.BLUE, align="center")
    doll(pg, L + 190, y_ + 84, 0.75, C.ORANGE, C.LIGHT[C.ORANGE])
    pg.eq(L + 190, y_ + 94, r"4t+5", 12, C.ORANGE, align="center")
    pg.arrow(L + 125, y_ + 90, L + 150, y_ + 96, C.GREY, 1.2, head=5)
    pg.note(L + 250, y_ + 10, "outside doll: \"cube whatever is inside\"\ninside doll: 4t + 5\n\n"
            "(Chapter 18 called this a composite function.)", C.INK, 15, w=R - L - 250)
    f.p("{b:So what are we trying to find?} {B:Nothing here needs solving.} $s = (4t + 5)^3$ is a finished "
        "recipe: pick a time $t$ and it tells you the distance $s$. Think of $t$ as seconds and $s$ as metres "
        "travelled. Lecture 15's question is a different one: {B:how fast is $s$ changing?} That speed is "
        "$\\frac{\\dd s}{\\dd t}$, Chapter 34's gradient (how steep the graph is).", 14, gap=8)
    y_ = f.reserve(184)
    pg = f.pg
    pg.text(L + 8, y_ + 4, "t (s)", 12, C.ORANGE, F.BOLD)
    pg.text(L + 62, y_ + 4, "s (m)", 12, C.BLUE, F.BOLD)
    pg.text(L + 122, y_ + 4, "jump", 12, C.GREEN, F.BOLD)
    pg.line(L + 4, y_ + 22, L + 170, y_ + 22, C.GREY, 0.8)
    ts = [0, 0.5, 1, 1.5]
    ss = [(4 * v + 5) ** 3 for v in ts]
    for k, (tv, sv) in enumerate(zip(ts, ss)):
        yy = y_ + 30 + k * 28
        pg.text(L + 8, yy, f"{tv:g}", 13, C.INK)
        pg.text(L + 62, yy, f"{sv:,.0f}", 13, C.INK)
        if k:
            pg.text(L + 122, yy - 14, f"+{ss[k] - ss[k - 1]:,.0f}", 12, C.GREEN, F.BOLD)
    ch.check(ss, [125, 343, 729, 1331])
    pg.note(L + 4, y_ + 140, "the jumps keep growing: s speeds up,\nso the speed depends on t", C.GREEN, 13,
            w=230)
    ax = Axes(pg, L + 290, y_ + 12, 170, 130, (0, 1.5), (0, 1400))
    ax.grid(0.5, 200)
    ax.axes("t", "s", 0.5, 400)
    ax.curve(lambda v: (4 * v + 5) ** 3, 0, 1.5, C.BLUE, 2.2)
    ax.curve(lambda v: 343 + 588 * (v - 0.5), 0.22, 0.8, C.RED, 1.6)
    ax.dot(0.5, 343, C.RED, 3.2)
    pg.note(ax.X(0.04), ax.Y(1360), "steepness at t = 0.5:\n588 m per second", C.RED, 13, w=150)
    pg.arrow(ax.X(0.3), ax.Y(1000), ax.X(0.47), ax.Y(420), C.RED, 1.0, head=5)
    ch.check(sp.diff((4 * t + 5) ** 3, t).subs(t, sp.Rational(1, 2)), 588)
    f.p("So the goal is a {B:new formula}, $\\frac{\\dd s}{\\dd t}$: a speedometer. Feed in any $t$ and "
        "it gives the speed at that moment. We'll get $\\frac{\\dd s}{\\dd t} = 12(4t+5)^2$, so at "
        "$t = 0.5$ the speed is $12 \\times 7^2 = 588$, the slope of the red line.", 14, gap=10)
    f.p("{b:The long way} (what Lecture 15 does first): multiply it all out, then differentiate.", 14, gap=6)
    step(f, r"(4t+5)^3=(4t+5)(16t^2+40t+25)", "square first", size=16)
    step(f, r"=64t^3+240t^2+300t+125", "", size=16)
    step(f, r"\frac{\dd s}{\dd t}=192t^2+480t+300=12(16t^2+40t+25)=12(4t+5)^2", "take out 12, spot the square",
         size=15)
    ch.check(sp.expand((4 * t + 5) ** 3), 64 * t ** 3 + 240 * t ** 2 + 300 * t + 125)
    ch.check(sp.factor(192 * t ** 2 + 480 * t + 300), 12 * (4 * t + 5) ** 2)
    f.p("Six lines, and imagine a power of 10! Look at the answer though: $12(4t+5)^2 = 3(4t+5)^2 \\times 4$. "
        "That's the outside doll differentiated ($3(\\ )^2$) times the inside doll differentiated (4). "
        "That's the shortcut.", 14)


def chain(ch):
    f = flow(ch)
    sec(f, "The chain rule: gears", room=380)
    f.p("Name the inside $z$. Then $t$ drives $z$, and $z$ drives $s$, like the gears on the title page. "
        "How fast $s$ changes with $t$ is the two rates {B:multiplied}:", 14, gap=6)
    step(f, r"\frac{\dd s}{\dd t}=\frac{\dd s}{\dd z}\times\frac{\dd z}{\dd t}", "outside rate × inside rate",
         size=22, color=C.PURPLE)
    ch.formula(r"\frac{dy}{dx}=\frac{dy}{dz}\times\frac{dz}{dx}", "chain rule")
    ch.term("chain rule", "for a function inside a function: dy/dx = dy/dz × dz/dx (outside rate × inside rate)")
    f.p("(It looks as if the $\\dd z$'s cancel. They don't really, since these aren't fractions, but it's a "
        "handy way to remember it.)", 13, gap=10)
    f.p("{b:Five small steps} for $s = (4t + 5)^3$:", 14, gap=6)
    for lat, why, col in [(r"z=\org{4t+5}", "1. name the inside doll", C.INK),
                          (r"s=\blu{z^3}", "2. the outside doll", C.INK),
                          (r"\frac{\dd s}{\dd z}=\blu{3z^2},\qquad\frac{\dd z}{\dd t}=\org{4}", "3. differentiate each doll",
                           C.INK),
                          (r"\frac{\dd s}{\dd t}=\blu{3z^2}\times\org{4}=12z^2", "4. multiply the rates", C.INK),
                          (r"\frac{\dd s}{\dd t}=12(4t+5)^2", "5. put the inside back", C.PURPLE)]:
        step(f, lat, why, size=18, color=col)
    ch.check(sp.diff((4 * t + 5) ** 3, t), 12 * (4 * t + 5) ** 2)
    f.p("Same answer as the six-line slog. {b:Lecture 15's second example:} $z = 2(3t^3 + 2t^2)^4$.", 14, gap=6)
    u = sp.symbols("u")
    for lat, why, col in [(r"u=\org{3t^3+2t^2},\qquad z=\blu{2u^4}", "name the inside", C.INK),
                          (r"\frac{\dd z}{\dd u}=\blu{8u^3},\qquad\frac{\dd u}{\dd t}=\org{9t^2+4t}", "each doll", C.INK),
                          (r"\frac{\dd z}{\dd t}=8(9t^2+4t)(3t^3+2t^2)^3", "multiply, put u back", C.PURPLE)]:
        step(f, lat, why, size=17, color=col)
    ch.check(sp.simplify(sp.diff(2 * (3 * t ** 3 + 2 * t ** 2) ** 4, t)
                         - 8 * (9 * t ** 2 + 4 * t) * (3 * t ** 3 + 2 * t ** 2) ** 3), 0)
    f.p("{b:Lecture 15's quick version for brackets:} bring the power down, knock one off the power, then "
        "multiply by the derivative of what's in the bracket. And the table in Chapter 34 was secretly "
        "using the chain rule all along: the $k$ in $e^{kx} \\to ke^{kx}$ is the inside's rate.", 14, gap=6)
    step(f, r"\frac{\dd}{\dd x}\sin(x^2)=\cos(x^2)\times2x", "outside: sin → cos; inside: x² → 2x", size=17)
    ch.check(sp.diff(sp.sin(x ** 2), x), 2 * x * sp.cos(x ** 2))


def product(ch):
    f = flow(ch)
    sec(f, "The product rule: a rectangle growing on two sides", room=560)
    f.p("$y = u \\times v$, where $u$ and $v$ both depend on $x$. Picture $y$ as the {B:area} of a "
        "rectangle with sides $u$ and $v$. Nudge $x$ a little: both sides grow.", 14, gap=10)
    y_ = f.reserve(185)
    pg = f.pg
    X0, Yb = L + 40, y_ + 150
    uw, vh, du, dv = 190, 105, 32, 24
    pg.rect(X0, Yb - vh, uw, vh, C.GREY, 1.0, fillcolor=C.LIGHT[C.GREY])
    pg.rect(X0 + uw, Yb - vh, du, vh, C.ORANGE, 1.0, fillcolor=C.LIGHT[C.ORANGE])
    pg.rect(X0, Yb - vh - dv, uw, dv, C.TEAL, 1.0, fillcolor=C.LIGHT[C.TEAL])
    pg.rect(X0 + uw, Yb - vh - dv, du, dv, C.RED, 1.0, fillcolor=C.LIGHT[C.RED])
    pg.eq(X0 + uw / 2, Yb - vh / 2 - 10, r"u\,v", 18, align="center")
    pg.eq(X0 + uw + du / 2, Yb - vh / 2 - 10, r"v\,\delta u", 12, C.ORANGE, align="center")
    pg.eq(X0 + uw / 2, Yb - vh - dv + 3, r"u\,\delta v", 13, C.TEAL, align="center")
    pg.text(X0 + uw - 20, Yb - vh - dv - 17, "tiny × tiny", 9, C.RED, F.BOLD)
    pg.brace(X0, Yb + 4, X0 + uw, Yb + 4, C.INK, 1.0, depth=-7)
    pg.eq(X0 + uw / 2, Yb + 12, "u", 14, align="center")
    pg.eq(X0 + uw + du / 2, Yb + 12, r"\delta u", 12, C.ORANGE, align="center")
    pg.eq(X0 - 18, Yb - vh / 2 - 8, "v", 14, align="center")
    pg.eq(X0 - 20, Yb - vh - dv / 2 - 8, r"\delta v", 12, C.TEAL, align="center")
    pg.note(L + 290, y_ + 4, "extra area =\nv δu (orange) + u δv (teal)\n+ δu δv (red corner)\n\nShrink the nudge: "
            "the red corner is tiny × tiny, so it vanishes. What's left:", C.INK, 15, w=R - L - 290)
    step(f, r"\frac{\dd y}{\dd x}=v\frac{\dd u}{\dd x}+u\frac{\dd v}{\dd x}",
         "each side's growth × the other side", size=22, color=C.PURPLE)
    ch.formula(r"\frac{d(uv)}{dx}=v\frac{du}{dx}+u\frac{dv}{dx}", "product rule")
    ch.term("product rule", "d(uv)/dx = v du/dx + u dv/dx")
    uu, vv = sp.Function("u")(x), sp.Function("v")(x)
    ch.check(sp.simplify(sp.diff(uu * vv, x) - (vv * sp.diff(uu, x) + uu * sp.diff(vv, x))), 0)
    f.p("{b:Test it where you can check (Lecture 15):} $y = (3x+1)(5x-2)$.", 14, gap=6)
    step(f, r"\text{expand first: }y=15x^2-x-2,\ \ \frac{\dd y}{\dd x}=30x-1", "the old way", size=16)
    step(f, r"u=3x+1,\ v=5x-2,\ \frac{\dd u}{\dd x}=3,\ \frac{\dd v}{\dd x}=5", "", size=16)
    step(f, r"\frac{\dd y}{\dd x}=(5x-2)\times3+(3x+1)\times5=15x-6+15x+5=30x-1", "✓ the same", size=16,
         color=C.PURPLE)
    ch.check(sp.expand(sp.diff((3 * x + 1) * (5 * x - 2), x)), 30 * x - 1)
    f.p("{b:Where you have no choice:} $y = x^3\\ln x$ can't be expanded.", 14, gap=6)
    step(f, r"u=x^3,\ \ v=\ln x,\ \ \frac{\dd u}{\dd x}=3x^2,\ \ \frac{\dd v}{\dd x}=\frac1x", "", size=16)
    step(f, r"\frac{\dd y}{\dd x}=\ln x\times3x^2+x^3\times\frac1x=3x^2\ln x+x^2=x^2(1+3\ln x)", "", size=16,
         color=C.PURPLE)
    ch.check(sp.simplify(sp.diff(x ** 3 * sp.log(x), x) - x ** 2 * (1 + 3 * sp.log(x))), 0)


def product_more(ch):
    f = flow(ch)
    sec(f, "Product rule: Lecture 15's harder ones", room=420)
    f.p("{b:Your turn slide:} $y = x^{-2}(4 + 3x^{-3})$.", 14, gap=6)
    step(f, r"u=x^{-2},\ v=4+3x^{-3},\ \frac{\dd u}{\dd x}=-2x^{-3},\ \frac{\dd v}{\dd x}=-9x^{-4}", "", size=15)
    step(f, r"\frac{\dd y}{\dd x}=(4+3x^{-3})(-2x^{-3})+x^{-2}(-9x^{-4})", "v u′ + u v′", size=16)
    step(f, r"=-8x^{-3}-6x^{-6}-9x^{-6}=-8x^{-3}-15x^{-6}=-\frac{8x^3+15}{x^6}", "add powers (Chapter 9)", size=16,
         color=C.PURPLE)
    ch.check(sp.simplify(sp.diff(x ** -2 * (4 + 3 * x ** -3), x) + (8 * x ** 3 + 15) / x ** 6), 0)
    f.p("{b:Combined example:} $y = (x+3)^2(4x+1)^3$. Each factor is itself a nesting doll, so the chain "
        "rule works {B:inside} the product rule:", 14, gap=6)
    step(f, r"u=(x+3)^2\Rightarrow\frac{\dd u}{\dd x}=2(x+3)\times1", "chain", size=16)
    step(f, r"v=(4x+1)^3\Rightarrow\frac{\dd v}{\dd x}=3(4x+1)^2\times4=12(4x+1)^2", "chain", size=16)
    step(f, r"\frac{\dd y}{\dd x}=(4x+1)^3\cdot2(x+3)+(x+3)^2\cdot12(4x+1)^2", "product rule", size=16,
         color=C.PURPLE)
    step(f, r"=320x^4+1728x^3+2628x^2+1010x+114", "multiplied out", size=16)
    yy = (x + 3) ** 2 * (4 * x + 1) ** 3
    ch.check(sp.expand(sp.diff(yy, x)), 320 * x ** 4 + 1728 * x ** 3 + 2628 * x ** 2 + 1010 * x + 114)
    ch.check(sp.factor(sp.diff(yy, x)), 2 * (x + 3) * (4 * x + 1) ** 2 * (10 * x + 19))
    f.p("{R:Slide slip:} Lecture 15's multiplied-out answer starts $340x^4$; it's $320x^4$ ($2\\times64 + "
        "12\\times16 = 128 + 192 = 320$).", 13.5, gap=8)
    ch.check(2 * 64 + 12 * 16, 320)
    f.p("Tidier: take out the common factors $2(x+3)(4x+1)^2$, leaving $\\frac{dy}{dx} = "
        "2(x+3)(4x+1)^2(10x+19)$.", 14)


def quotient(ch):
    f = flow(ch)
    sec(f, "The quotient rule: a product in disguise", room=560)
    f.p("A fraction $\\frac{u}{v}$ is really $u \\times v^{-1}$. So you don't need anything new: use the product "
        "rule, with the chain rule for $v^{-1}$:", 14, gap=6)
    step(f, r"y=u\,v^{-1}", "dividing = multiplying by the reciprocal", size=18)
    step(f, r"\frac{\dd y}{\dd x}=v^{-1}\frac{\dd u}{\dd x}+u\cdot(-1)v^{-2}\frac{\dd v}{\dd x}",
         "product rule; chain on v⁻¹", size=17)
    step(f, r"=\frac{v\frac{\dd u}{\dd x}-u\frac{\dd v}{\dd x}}{v^2}", "over a common denominator v²", size=19)
    uu, vv = sp.Function("u")(x), sp.Function("v")(x)
    ch.check(sp.simplify(sp.diff(uu / vv, x) - (vv * sp.diff(uu, x) - uu * sp.diff(vv, x)) / vv ** 2), 0)
    ch.formula(r"\frac{d}{dx}\left(\frac uv\right)=\frac{v\frac{du}{dx}-u\frac{dv}{dx}}{v^2}", "quotient rule")
    ch.term("quotient rule", "d(u/v)/dx = (v du/dx − u dv/dx) ÷ v²")
    f.p("Memory rhyme: {B:\"low d-high minus high d-low, over the square of what's below\"}. The order "
        "matters because of the minus.", 14, gap=8)
    f.p("{b:Lecture 15:} $y = \\frac{x-1}{x+2}$, so $u = x - 1$, $v = x + 2$, and both derivatives are 1.", 14,
        gap=6)
    step(f, r"\frac{\dd y}{\dd x}=\frac{(x+2)(1)-(x-1)(1)}{(x+2)^2}=\frac{3}{(x+2)^2}", "", size=18, color=C.PURPLE)
    ch.check(sp.simplify(sp.diff((x - 1) / (x + 2), x) - 3 / (x + 2) ** 2), 0)
    f.p("{b:Harder:} $y = \\frac{e^{-3t}}{t^2+1}$, with $u = e^{-3t}$, $u' = -3e^{-3t}$, $v = t^2 + 1$, $v' = 2t$.",
        14, gap=6)
    step(f, r"\frac{\dd y}{\dd t}=\frac{(t^2+1)(-3e^{-3t})-e^{-3t}(2t)}{(t^2+1)^2}=\frac{-(3t^2+2t+3)\,e^{-3t}}{(t^2+1)^2}",
         "", size=16, color=C.PURPLE)
    ch.check(sp.simplify(sp.diff(sp.exp(-3 * t) / (t ** 2 + 1), t)
                         + (3 * t ** 2 + 2 * t + 3) * sp.exp(-3 * t) / (t ** 2 + 1) ** 2), 0)


def three_roads(ch):
    f = flow(ch)
    sec(f, "Three roads to the same answer", room=420)
    f.p("Lecture 15's \"options\": $f(x) = \\frac{1-x^2}{5x^2}$. The quotient rule works, the product rule "
        "works, and a third road (simplify first) is the shortest:", 14, gap=10)
    y_ = f.reserve(240)
    pg = f.pg
    roads = [(C.BLUE, "quotient rule", [r"\frac{-2x\cdot5x^2-10x(1-x^2)}{25x^4}", r"=\frac{-10x^3-10x+10x^3}{25x^4}",
                                         r"=\frac{-10x}{25x^4}"]),
             (C.ORANGE, "product rule", [r"\tfrac15x^{-2}(-2x)", r"+(1-x^2)(-\tfrac25x^{-3})", r"=-\tfrac25x^{-1}-\tfrac25x^{-3}+\tfrac25x^{-1}"]),
             (C.GREEN, "simplify first", [r"f=\tfrac15x^{-2}-\tfrac15", r"f'=-\tfrac25x^{-3}"])]
    for k, (col, nm, lines) in enumerate(roads):
        x0 = L + k * 168
        pg.rect(x0, y_, 158, 132, col, 1.2, fillcolor=C.LIGHT[col], r=8)
        pg.text(x0 + 4, y_ + 6, nm, 11.5, col, F.BOLD, w=150, align="center")
        for i, lat in enumerate(lines):
            pg.eq(x0 + 79, y_ + 26 + i * 34, lat, 10.5 if k < 2 else 14, align="center")
        pg.arrow(x0 + 79, y_ + 134, L + W / 2 + (k - 1) * 30, y_ + 176, col, 1.4, head=6)
    pg.rect(L + W / 2 - 80, y_ + 178, 160, 54, C.PURPLE, 1.6, r=8)
    pg.eq(L + W / 2, y_ + 183, r"f'(x)=-\frac{2}{5x^3}", 17, C.PURPLE, align="center")
    fx = (1 - x ** 2) / (5 * x ** 2)
    ch.check(sp.simplify(sp.diff(fx, x) + sp.Rational(2, 5) / x ** 3), 0)
    ch.check(sp.expand(fx), x ** -2 / 5 - sp.Rational(1, 5))
    f.p("Moral: {B:tidy up before you differentiate}. Splitting the fraction ($\\frac{1}{5x^2} - \\frac{x^2}{5x^2}$) "
        "turned a quotient into two plain powers.", 14)


def implicit(ch):
    f = flow(ch)
    sec(f, "Implicit differentiation: every y wears a tag", room=560)
    f.p("{B:Explicit}: $y = $ (something with $x$). {B:Implicit}: $x$ and $y$ are tangled together, like "
        "$x^3 + 3y^2 - 4x + y = 11$, and you can't easily get $y$ on its own.", 14, gap=6)
    ch.term("explicit / implicit function", "explicit: y = f(x); implicit: x and y mixed in one equation")
    f.p("The trick: $y$ is secretly a function of $x$ (an inside doll!). So when you differentiate a $y$ "
        "term with respect to $x$, the chain rule sticks a {B:tag} on it: differentiate as if $y$ were $x$, "
        "then multiply by $\\frac{\\dd y}{\\dd x}$.", 14, gap=10)
    y_ = f.reserve(80)
    pg = f.pg
    terms = [(r"x^3", r"3x^2", False), (r"+3y^2", r"+6y", True), (r"-4x", r"-4", False), (r"+y", r"+1", True),
             (r"=11", r"=0", False)]
    for k, (a, b, tag) in enumerate(terms):
        x0 = L + 20 + k * 95
        pg.eq(x0 + 30, y_, a, 18, align="center")
        pg.arrow(x0 + 30, y_ + 24, x0 + 30, y_ + 38, C.GREY, 1.0, head=4)
        pg.eq(x0 + 30, y_ + 42, b, 18, C.PURPLE if tag else C.INK, align="center")
        if tag:
            tx, ty = x0 + 56, y_ + 38
            pg.poly([(tx, ty + 10), (tx + 8, ty), (tx + 38, ty), (tx + 38, ty + 24), (tx + 8, ty + 24), (tx, ty + 10)],
                    C.RED, 1.1)
            pg.circle(tx + 7, ty + 12, 1.8, C.RED, 0.8)
            pg.eq(tx + 23, ty + 1, r"\tfrac{\dd y}{\dd x}", 11, C.RED, align="center")
    step(f, r"3x^2+6y\frac{\dd y}{\dd x}-4+\frac{\dd y}{\dd x}=0", "the tagged terms hold dy/dx", size=18)
    step(f, r"\frac{\dd y}{\dd x}(6y+1)=4-3x^2", "tagged terms on one side; factor (Chapter 12)", size=18)
    step(f, r"\frac{\dd y}{\dd x}=\frac{4-3x^2}{6y+1}", "÷ (6y + 1)", size=20, color=C.PURPLE)
    Y = sp.Function("Y")(x)
    d = sp.diff(x ** 3 + 3 * Y ** 2 - 4 * x + Y - 11, x)
    sol = sp.solve(d, sp.diff(Y, x))[0]
    ch.check(sp.simplify(sol - (4 - 3 * x ** 2) / (6 * Y + 1)), 0)
    ch.term("implicit differentiation", "differentiate every term; each y term gets an extra × dy/dx (chain rule); then solve for dy/dx")
    f.p("Notice the answer has $y$ in it: the gradient depends on {B:where} you are on the curve, which "
        "needs both coordinates.", 14, gap=10)
    f.p("{b:A picture you can check:} the circle $x^2 + y^2 = 25$ (Chapter 28).", 14, gap=8)
    y_ = f.reserve(182)
    pg = f.pg
    ax = Axes(pg, L + 20, y_ + 4, 168, 168, (-6, 6), (-6, 6))
    ax.grid(1, 1)
    ax.axes(None, None, 0, 0)
    ax.param(lambda a: 5 * math.cos(a), lambda a: 5 * math.sin(a), 0, 2 * math.pi, C.PURPLE, 2.2)
    ax.seg(0, 0, 3, 4, C.GREY, 1.2, dash=(3, 3))
    ax.curve(lambda X: 4 - 0.75 * (X - 3), 0.2, 5.9, C.RED, 1.8)
    ax.dot(3, 4, C.INK, 3.5)
    ax.label(3, 4, "{B:(3, 4)}", 10, dx=6, dy=-22)
    xq = L + 215
    pg.eq(xq, y_ + 4, r"2x+2y\frac{\dd y}{\dd x}=0", 16)
    pg.eq(xq, y_ + 46, r"\frac{\dd y}{\dd x}=-\frac{x}{y}", 17, C.PURPLE)
    pg.eq(xq, y_ + 94, r"\text{at }(3,4):\ -\tfrac34", 16, C.RED)
    pg.note(xq, y_ + 124, "The radius has gradient 4/3, the tangent −3/4: perpendicular, as Chapter 20 "
            "promised (they multiply to −1).", C.INK, 14, w=R - xq)
    ch.check(sp.Rational(-3, 4) * sp.Rational(4, 3), -1)
    ch.check(sp.simplify(sp.solve(sp.diff(x ** 2 + Y ** 2 - 25, x), sp.diff(Y, x))[0] + x / Y), 0)


def sorting(ch):
    f = flow(ch)
    sec(f, "Which rule? Sort by how it's built", room=300)
    f.p("Ask: what is the {B:last} thing you'd do if you worked it out on a calculator? That's the outer "
        "structure, and it picks the rule.", 14, gap=10)
    y_ = f.reserve(185)
    pg = f.pg
    bins = [(C.BLUE, "something inside\nsomething: CHAIN", [r"(2x+1)^5", r"e^{3x^2}", r"\sin(x^2)", r"\sqrt{1+x^3}"]),
            (C.ORANGE, "two x-things\nmultiplied: PRODUCT", [r"x^2\sin x", r"xe^x", r"(x+1)^3(x-2)", r"x\ln x"]),
            (C.GREEN, "one divided by\nanother: QUOTIENT", [r"\frac{x+1}{x-1}", r"\frac{\sin x}{x}", r"\frac{e^x}{x^2+1}"]),
            (C.PINK, "x and y tangled:\nIMPLICIT", [r"x^2+y^2=25", r"x^3+3y^2=11", r"y^3+x=y"])]
    for k, (col, head, items) in enumerate(bins):
        x0 = L + k * 125
        pg.rect(x0, y_, 118, 180, col, 1.2, r=8)
        pg.fillpoly([(x0, y_ + 36), (x0, y_ + 8), (x0 + 8, y_), (x0 + 110, y_), (x0 + 118, y_ + 8), (x0 + 118, y_ + 36)],
                    C.LIGHT[col])
        for i, line_ in enumerate(head.split("\n")):
            pg.text(x0 + 2, y_ + 4 + i * 14, line_, 9.5, col, F.BOLD, w=114, align="center")
        for i, lat in enumerate(items):
            pg.eq(x0 + 59, y_ + 44 + i * 34, lat, 13, align="center")
    f.p("Sums and differences are never a problem: split them up and do each term with its own rule.", 14)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Your turn", fresh=True)
    f.p("Name the rule before you start. Answers in grey.", 13.5, gap=10)
    groups = [
        ("Higher derivatives", ["Find d²y/dx² for y = x⁴ − 3x² + 5.", "Find d³y/dx³ for y = cos x."],
         "1. 12x² − 6   2. sin x"),
        ("Chain rule", ["y = (2x + 1)⁵", "y = e^(3x²)", "y = √(1 + x³)"],
         "3. 10(2x + 1)⁴   4. 6x e^(3x²)   5. 3x² ÷ (2√(1 + x³))"),
        ("Product rule", ["y = x² sin x", "y = x eˣ"],
         "6. 2x sin x + x² cos x   7. eˣ + x eˣ = (1 + x)eˣ"),
        ("Quotient rule (or rewrite!)", ["y = (x + 1)/(x − 1)", "y = (x² + 1)/x"],
         "8. −2/(x − 1)²   9. 1 − 1/x² (easiest: x + x⁻¹ first)"),
        ("Implicit", ["Find dy/dx for x² + y² = 100, and its value at (6, 8).", "Find dy/dx for y³ + x = y."],
         "10. −x/y; −3/4   11. 1/(1 − 3y²)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 22 * len(qs) + 30)
        f.text(title, 14, C.PURPLE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14, w=W - 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check(sp.diff(x ** 4 - 3 * x ** 2 + 5, x, 2), 12 * x ** 2 - 6)
    ch.check(sp.diff(sp.cos(x), x, 3), sp.sin(x))
    ch.check(sp.diff((2 * x + 1) ** 5, x), 10 * (2 * x + 1) ** 4)
    ch.check(sp.diff(sp.exp(3 * x ** 2), x), 6 * x * sp.exp(3 * x ** 2))
    ch.check(sp.simplify(sp.diff(sp.sqrt(1 + x ** 3), x) - 3 * x ** 2 / (2 * sp.sqrt(1 + x ** 3))), 0)
    ch.check(sp.diff(x ** 2 * sp.sin(x), x), 2 * x * sp.sin(x) + x ** 2 * sp.cos(x))
    ch.check(sp.simplify(sp.diff(x * sp.exp(x), x) - (1 + x) * sp.exp(x)), 0)
    ch.check(sp.simplify(sp.diff((x + 1) / (x - 1), x) + 2 / (x - 1) ** 2), 0)
    ch.check(sp.simplify(sp.diff((x ** 2 + 1) / x, x) - (1 - 1 / x ** 2)), 0)
    Y = sp.Function("Y")(x)
    s1 = sp.solve(sp.diff(x ** 2 + Y ** 2 - 100, x), sp.diff(Y, x))[0]
    ch.check(sp.simplify(s1 + x / Y), 0)
    ch.check(sp.Rational(-6, 8), sp.Rational(-3, 4))
    s2 = sp.solve(sp.diff(Y ** 3 + x - Y, x), sp.diff(Y, x))[0]
    ch.check(sp.simplify(s2 - 1 / (1 - 3 * Y ** 2)), 0)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    higher(ch)
    dolls(ch)
    chain(ch)
    product(ch)
    product_more(ch)
    quotient(ch)
    three_roads(ch)
    implicit(ch)
    sorting(ch)
    your_turn(ch)
