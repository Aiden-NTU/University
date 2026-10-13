"""Chapter 22 - Logarithms. A log answers 'how many times do I multiply?'. The same fact in two
languages, logs as the undo button for powers, a ruler where every step is x10, each log law
next to the index law it comes from, and Lecture 7's questions (capacitor, resisted motion)."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from generator.plot import Axes
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 22
NUM = 22
TITLE = "Logarithms"
SHORT = "Logarithms"
SLUG = "Logarithms"
ACCENT = C.PURPLE
REQUIRES = ["powers", "index-laws", "exponential-function", "e-number", "inverse-operations", "transpose",
            "solve-equation", "standard-form", "graph-of-function", "domain", "zero-power", "negative-powers",
            "compound-interest", "exponential-decay", "time-constant", "factorise-common-factor", "algebraic-fractions"]
INTRODUCES = ["logarithm", "log-base", "common-log", "natural-log", "log-laws", "log-scale", "change-of-base",
              "solve-exponential-equation"]

PAPER = "#fdfbff"


def icon(pg, x0, y0):
    pg.poly([(x0 + 1 + i * 1.7, y0 + 16 - 14 * math.log(1 + i) / math.log(11)) for i in range(11)], C.PURPLE, 1.5)
    pg.line(x0 + 1, y0 + 17, x0 + 18, y0 + 17, C.PURPLE, 0.8)


def sec(f, t_, **kw):
    section(f, t_, C.PURPLE, icon, **kw)


def lg(v):
    return math.log10(v)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 22, "Logarithms", "counting the multiplications", C.PURPLE, PAPER)
    xx = L + 30
    for i in range(3):
        pg.circle(xx + 22 + i * 70, 250, 22, C.PURPLE, 1.4, fillcolor=C.LIGHT[C.PURPLE])
        pg.text(xx + 22 + i * 70, 240, "2", 18, C.PURPLE, F.BOLD, align="center")
        if i < 2:
            pg.text(xx + 57 + i * 70, 240, "×", 18, C.GREY, F.BOLD, align="center")
    pg.text(xx + 215, 240, "= 8", 20, C.INK, F.BOLD)
    pg.line(xx, 284, xx + 184, 284, C.ORANGE, 1.2)
    pg.note(xx + 30, 290, "three 2s were multiplied", C.ORANGE, 17)
    pg.eq(xx + 330, 250, r"\log_2 8=3", 30, C.PURPLE, valign="middle")
    f = ch.flow(top=370)
    f.p("Powers ask: {B:multiply 2 by itself 3 times, what do you get?} (8). Logarithms ask the "
        "question the other way round: {B:how many 2s must I multiply to get 8?} (3). That's all a "
        "log is: {B:a count of multiplications}, or equivalently, {B:the missing power}.", 14, gap=10)
    f.p("Logs are the undo button for exponentials (Chapter 21), so they're how you answer "
        "\"how long until...?\" questions. Each log rule is just an index rule (Chapter 9) wearing "
        "a disguise, and this chapter shows them side by side.", 14, gap=10)
    f.p("{y:Goes with} {B:Lecture 7} {y:(logarithms, laws of logs, natural log, Questions 1-3).}", 12.5)


def question(ch):
    f = flow(ch)
    sec(f, "The question a log asks")
    f.p("Read $\\log_b N$ as \"{B:log to the base $b$ of $N$}\", and hear it as the question: {B:what power "
        "of $b$ gives $N$?} The small number $b$ is the {B:base}: the thing being multiplied.", 14, gap=8)
    rows = [(r"\log_2 8", "how many 2s make 8?", r"2\times2\times2=8", "3"),
            (r"\log_{10}100", "how many 10s make 100?", r"10\times10=100", "2"),
            (r"\log_4 16", "how many 4s make 16?", r"4\times4=16", "2"),
            (r"\log_{10}1000000", "how many 10s make a million?", r"10^6", "6"),
            (r"\log_5 5", "how many 5s make 5?", r"5", "1"),
            (r"\log_7 1", "how many 7s make 1?", r"7^0=1", "0")]
    y_ = f.reserve(20 + 32 * len(rows))
    pg = f.pg
    for i, (lat, ask, work, ans) in enumerate(rows):
        yy = y_ + 14 + i * 32
        pg.eq(L + 10, yy, lat, 17, C.PURPLE, valign="middle")
        pg.note(L + 135, yy - 11, ask, C.GREY, 15)
        pg.eq(L + 330, yy, work, 15, valign="middle")
        pg.text(L + 460, yy - 9, ans, 16, C.GREEN, F.BOLD)
    for b, N, ans in [(2, 8, 3), (10, 100, 2), (4, 16, 2), (10, 10 ** 6, 6), (5, 5, 1), (7, 1, 0)]:
        ch.check(sp.log(N, b), ans)
    ch.term("logarithm", "log_b N is the power you must raise b to, to get N; it counts how many b's multiply to N")
    ch.term("base (of a log)", "the number being raised to a power, written small: the 2 in log₂ 8")
    ch.symbol(r"\log_b N", "log to the base b of N", "the power of b that gives N")
    f.p("{b:The same fact in two languages.} Every log statement is a power statement in disguise. "
        "Lecture 7's translation rule:", 14, gap=10)
    y_ = f.reserve(80)
    pg = f.pg
    pg.rect(L + 30, y_, 170, 60, C.ORANGE, 1.4, fillcolor=C.LIGHT[C.ORANGE], r=8)
    pg.eq(L + 115, y_ + 30, r"y=a^{x}", 24, align="center", valign="middle")
    pg.rect(L + 290, y_, 170, 60, C.PURPLE, 1.4, fillcolor=C.LIGHT[C.PURPLE], r=8)
    pg.eq(L + 375, y_ + 30, r"x=\log_a y", 24, align="center", valign="middle")
    pg.arrow(L + 206, y_ + 18, L + 284, y_ + 18, C.GREY, 1.3, head=5, bend=-0.15)
    pg.arrow(L + 284, y_ + 44, L + 206, y_ + 44, C.GREY, 1.3, head=5, bend=-0.15)
    pg.note(L + 214, y_ + 58, "same fact", C.GREY, 14)
    f.p("{h:A handy chant:} \"the base stays the base, and the log is the power\".", 13.5, C.BROWN)


def undo(ch):
    f = flow(ch)
    sec(f, "Logs are the undo button for powers", room=330)
    f.p("In Chapter 14 every operation had an undo button: + undoes −, × undoes ÷, squaring undoes "
        "square-rooting. {B:\"Raise 10 to the power\" and \"take $\\log_{10}$\" undo each other}:",
        14, gap=6)
    step(f, r"\log_{10}(10^{\,x})=x", "power first, then log: back to x", size=19)
    step(f, r"10^{\log_{10}x}=x", "log first, then power: back to x", size=19)
    f.p("Your calculator has two log buttons. {B:log} means base 10 (the {B:common log}); {B:ln} "
        "means base $e$ (the {B:natural log}, Lecture 7: we write ln rather than $\\log_e$).", 14, gap=8)
    ch.term("common log", "log to base 10, the log button: log 1000 = 3")
    ch.term("natural log", "log to base e (2.718...), written ln: ln e = 1")
    ch.symbol(r"\ln", "L-N, natural log", "log to base e")
    f.p("{b:Logs of in-between numbers} are decimals. 50 is between 10 and 100, so $\\log_{10}50$ is "
        "between 1 and 2:", 14, gap=10)
    y_ = f.reserve(70)
    pg = f.pg
    x0, w_ = L + 30, 420
    pg.line(x0, y_ + 20, x0 + w_, y_ + 20, C.INK, 1.2)
    for k, v in enumerate([1, 10, 100, 1000]):
        xx = x0 + k * w_ / 3
        pg.line(xx, y_ + 14, xx, y_ + 26, C.INK, 1.2)
        pg.text(xx, y_ - 4, f"{v:,}".replace(",", " "), 12, C.INK, F.BOLD, align="center")
        pg.text(xx, y_ + 30, f"log = {k}", 11, C.PURPLE, align="center")
    xx = x0 + lg(50) * w_ / 3
    pg.dot(xx, y_ + 20, 4, C.RED)
    pg.text(xx, y_ - 4, "50", 12, C.RED, F.BOLD, align="center")
    pg.text(xx, y_ + 30, "1.699", 11, C.RED, align="center")
    ch.check_num(lg(50), 1.699, tol=0.001)
    f.p("{R:What you can't log:} $\\log 1 = 0$ (since $10^0 = 1$), numbers between 0 and 1 have "
        "{B:negative} logs ($\\log 0.01 = -2$), and 0 or negative numbers have {B:no log at all}: no "
        "power of 10 is ever 0 or negative (the curve of $10^x$ never reaches the x-axis). So the "
        "domain of log is positive numbers only.", 14)
    ch.check(sp.log(sp.Rational(1, 100), 10), -2)


def scale(ch):
    f = flow(ch)
    sec(f, "Log scales: a ruler where every step is ×10", room=300)
    f.p("On an ordinary ruler every step {B:adds} the same amount. On a {B:log scale} every step "
        "{B:multiplies} by the same amount. That squashes enormous ranges onto one page:", 14, gap=12)
    y_ = f.reserve(78)
    pg = f.pg
    x0, w_ = L + 20, 450
    pg.line(x0, y_ + 20, x0 + w_, y_ + 20, C.INK, 1.4)
    for k in range(6):
        for mm in range(1, 10):
            xx = x0 + (k + lg(mm)) * w_ / 5
            if xx > x0 + w_ + 1:
                break
            big = mm == 1
            pg.line(xx, y_ + (10 if big else 15), xx, y_ + 20, C.INK, 1.2 if big else 0.6)
            if big:
                pg.text(xx, y_ - 6, f"{10 ** k:,}".replace(",", " "), 11, C.INK, F.BOLD, align="center")
            elif mm in (2, 5) and k < 2:
                pg.text(xx, y_ + 24, str(mm * 10 ** k), 9, C.GREY, align="center")
    pg.note(x0, y_ + 38, "equal gaps from 1 to 10, 10 to 100, 100 to 1000... and 2 sits 30% of the way "
            "to 10, because log 2 ≈ 0.301", C.PURPLE, 14, w=w_)
    ch.check_num(lg(2), 0.301, tol=0.001)
    f.p("You meet log scales in {B:decibels} (sound), {B:pH} (acidity) and the {B:Richter scale} "
        "(earthquakes): one step up means 10 times more intense. They also straighten out "
        "exponential curves: plot $10^x$ on a log axis and you get a straight line.", 14, gap=10)
    ch.term("log scale", "a scale where equal steps mean multiplying by the same amount (e.g. ×10)")
    y_ = f.reserve(150)
    pg = f.pg
    ax = Axes(pg, L + 30, y_ + 10, 200, 120, (-1, 4), (-1, 4))
    ax.grid(1, 1)
    ax.axes("x", "y", 1, 1, size=8)
    ax.curve(lambda v: 2 ** v, color=C.RED, width=2)
    ax.curve(lambda v: math.log2(v) if v > 0 else None, 0.02, 4, color=C.PURPLE, width=2)
    ax.curve(lambda v: v, color=C.GREY, width=1, dash=(3, 3))
    ax.label(0.3, 2.6, "{R:2ˣ}", 11, dy=0)
    ax.label(3.2, 1.5, "{P:log₂ x}", 11, dy=0)
    pg.note(L + 260, y_ + 10, "The graph of log is the graph of the\npower, reflected in the dashed line\n"
            "y = x (because they undo each other:\ninputs and outputs swap).\n\nIt rises ever more slowly and "
            "never\nexists for x ≤ 0.", C.GREY, 15)


def laws(ch):
    f = flow(ch)
    sec(f, "The log laws are the index laws in disguise", room=420)
    f.p("A log {B:is} a power, so the three index laws of Chapter 9 turn straight into three log laws. "
        "Read across each row: the index law on the left, the log law on the right, and a number test.",
        14, gap=10)
    rows = [
        (r"10^m\times10^n=10^{m+n}", r"\log(ab)=\log a+\log b", "multiply inside → add outside",
         r"\log(100\times1000)=\log10^5=5=2+3"),
        (r"\frac{10^m}{10^n}=10^{m-n}", r"\log\frac ab=\log a-\log b", "divide inside → subtract outside",
         r"\log\frac{1000}{10}=\log100=2=3-1"),
        (r"(10^m)^n=10^{mn}", r"\log a^n=n\log a", "power inside → multiply in front",
         r"\log1000^2=\log10^6=6=2\times3"),
    ]
    for il, ll, words, test in rows:
        y_ = f.reserve(92)
        pg = f.pg
        pg.rect(L, y_, W / 2 - 6, 50, C.ORANGE, 1, fillcolor=C.LIGHT[C.ORANGE], r=6)
        pg.rect(L + W / 2 + 6, y_, W / 2 - 6, 50, C.PURPLE, 1.3, fillcolor=C.LIGHT[C.PURPLE], r=6)
        pg.eq(L + W / 4, y_ + 25, il, 17, align="center", valign="middle")
        pg.eq(L + 3 * W / 4 + 3, y_ + 25, ll, 18, align="center", valign="middle")
        pg.arrow(L + W / 2 - 4, y_ + 25, L + W / 2 + 4, y_ + 25, C.GREY, 1.2, head=4)
        pg.note(L + W / 2 + 12, y_ + 52, words, C.PURPLE, 14)
        pg.eq(L + 10, y_ + 60, test, 13, C.GREEN)
    ch.check(sp.log(100 * 1000, 10), 5)
    ch.check(sp.log(sp.Integer(1000) ** 2, 10), 6)
    ch.formula(r"\log(ab)=\log a+\log b", "log law: product")
    ch.formula(r"\log\frac ab=\log a-\log b", "log law: quotient")
    ch.formula(r"\log a^n=n\log a", "log law: power")
    ch.term("laws of logs", "log(ab) = log a + log b, log(a/b) = log a − log b, log aⁿ = n log a (any base)")
    f.p("{R:Traps (test with numbers!):} $\\log(a + b)$ is {B:not} $\\log a + \\log b$ (try "
        "$\\log(10 + 10) = 1.30$, but $1 + 1 = 2$). And $\\frac{\\log a}{\\log b}$ is {B:not} "
        "$\\log\\frac ab$.", 13.5, gap=6)
    ch.check_num(lg(20), 1.301, tol=0.001)
    f.p("(Lecture 7's example for $\\log a^n = n\\log a$ is a copy of the first law's example. A real "
        "one: $\\log_{10}a^3 = 3\\log_{10}a$.)", 12.5, C.GREY)


def q1(ch):
    f = flow(ch)
    sec(f, "Lecture 7, Question 1: pulling a log apart", room=300)
    f.p("{B:Express $\\log_{10}\\frac{a^2b^3}{100c}$ as separate logs of $a$, $b$ and $c$.} One law per "
        "line; do the division first, because it's the \"outermost\" operation:", 14, gap=6)
    step(f, r"\log\frac{a^2b^3}{100c}=\log(a^2b^3)-\log(100c)", "divide → subtract", size=18)
    step(f, r"=\log a^2+\log b^3-\big(\log100+\log c\big)", "multiply → add (keep the bracket!)", size=18)
    step(f, r"=2\log a+3\log b-(2+\log c)", "powers come to the front; log 100 = 2", size=18)
    step(f, r"=2\log a+3\log b-2-\log c", "the minus reaches both terms", size=18, color=C.GREEN)
    a, b, c = 3.0, 5.0, 7.0
    ch.check_num(lg(a ** 2 * b ** 3 / (100 * c)), 2 * lg(a) + 3 * lg(b) - 2 - lg(c), tol=1e-9)
    f.p("{G:Test with numbers:} $a = 3$, $b = 5$, $c = 7$: both sides give $0.2061$ ✓.", 13.5)
    ch.check_num(lg(9 * 125 / 700), 0.2061, tol=0.0001)


def solving(ch):
    f = flow(ch)
    sec(f, "How many doublings? Solving with logs", room=400)
    f.p("When the unknown is {B:in the power}, no amount of adding or dividing will get it down. "
        "Lecture 7: {B:take logs of both sides} (allowed: do the same to both sides), then use the "
        "power law to bring it to the front:", 14, gap=6)
    step(f, r"2^{\,x}=8", "", size=19)
    step(f, r"\log2^{\,x}=\log8", "log both sides", size=19)
    step(f, r"x\log2=\log8", "the power law lifts x down", size=19)
    step(f, r"x=\frac{\log8}{\log2}=\frac{0.903}{0.301}=3", "÷ log 2  (the slide's 0.90309)", size=19, color=C.GREEN)
    ch.check_num(lg(8) / lg(2), 3)
    f.p("{b:Now one you couldn't guess:} how many years until £1000 at 5% doubles to £2000?", 14, gap=6)
    step(f, r"1000\times1.05^{\,t}=2000", "Chapter 21's formula", size=19)
    step(f, r"1.05^{\,t}=2", "÷ 1000", size=19)
    step(f, r"t=\frac{\log2}{\log1.05}\approx14.2", "log both sides; power law; ÷ log 1.05", size=19,
         color=C.GREEN)
    ch.check_num(lg(2) / lg(1.05), 14.21, tol=0.01)
    ch.term("solving exponential equations", "take logs of both sides and use log aⁿ = n log a to bring the unknown down")
    f.p("So 15 whole years (after 14 years it's only £1979.93). {b:Change of base} (Lecture 7) is the "
        "same trick: $\\log_5 15 = \\frac{\\log15}{\\log5} = \\frac{1.1761}{0.6990} = 1.6825$, which lets "
        "a base-10 calculator do any base.", 14)
    ch.check_num(lg(15) / lg(5), 1.6826, tol=0.0002)
    ch.formula(r"\log_aN=\frac{\log_bN}{\log_ba}", "change of base")


def q2(ch):
    f = flow(ch)
    sec(f, "Lecture 7, Question 2: how long for the current to fade?", room=380)
    f.p("{B:The current falls from $I$ to $i$ following $i = Ie^{-t/CR}$. Find an expression for the "
        "time $t$.} The unknown is in the power of $e$, so we'll need {B:ln}, the undo button for $e$. "
        "Unwrap one layer per line:", 14, gap=6)
    step(f, r"i=Ie^{-t/CR}", "", size=19)
    step(f, r"i=\frac{I}{e^{t/CR}}", "negative power = 1 over (Chapter 9)", size=19)
    step(f, r"e^{t/CR}=\frac Ii", "swap i and the e-part (× e^(t/CR), ÷ i)", size=19)
    step(f, r"\frac{t}{CR}=\ln\frac Ii", "ln undoes e: ln(e^▢) = ▢", size=19)
    step(f, r"t=CR\ln\frac Ii", "× CR", size=21, color=C.GREEN)
    I_, i_, C_, R_ = sp.symbols("I i C R", positive=True)
    tt = sp.Symbol("t", positive=True)
    ch.check(sp.simplify(I_ * sp.exp(-(C_ * R_ * sp.log(I_ / i_)) / (C_ * R_))), i_)
    f.p("{b:Put numbers in} (Chapter 21's question): with $CR = 2$ seconds, how long until the current "
        "is 10% of the start? Then $\\frac Ii = 10$:", 14, gap=6)
    step(f, r"t=2\ln10\approx2\times2.303=4.61\text{ s}", "", size=19, color=C.GREEN)
    ch.check_num(2 * math.log(10), 4.605, tol=0.001)
    f.p("{G:Check:} $e^{-4.61/2} = e^{-2.303} \\approx 0.10$ ✓.", 13.5)


def q3(ch):
    f = flow(ch)
    sec(f, "Lecture 7, Question 3: resisted motion", room=420)
    f.p("{B:$v = u(1 - e^{-kt})$ gives the velocity $v$ at time $t$ from the starting velocity $u$. Find "
        "$t$.} (The slides do it two ways; this is the shorter, version 3b.)", 14, gap=6)
    step(f, r"v=u-ue^{-kt}", "expand the bracket", size=19)
    step(f, r"v=u-\frac{u}{e^{kt}}", "negative power = 1 over", size=19)
    step(f, r"ve^{kt}=ue^{kt}-u", "× e^(kt) every term", size=19)
    step(f, r"u=(u-v)e^{kt}", "gather the e-terms: factorise (Chapter 12)", size=19)
    step(f, r"e^{kt}=\frac{u}{u-v}", "÷ (u − v)", size=19)
    step(f, r"kt=\ln\frac{u}{u-v}", "ln undoes e", size=19)
    step(f, r"t=\frac1k\ln\frac{u}{u-v}", "÷ k", size=21, color=C.GREEN)
    u_, v_, k_, tt = sp.symbols("u v k t", positive=True)
    ch.check(sp.simplify(u_ * (1 - sp.exp(-k_ * (sp.log(u_ / (u_ - v_)) / k_))) - v_), 0)
    f.p("{G:Test:} $u = 10$, $k = 0.5$, $v = 5$: $t = 2\\ln2 \\approx 1.386$. Back in the original: "
        "$10(1 - e^{-0.693}) = 10(1 - 0.5) = 5$ ✓.", 13.5)
    ch.check_num(10 * (1 - math.exp(-0.5 * 2 * math.log(2))), 5)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Counting multiplications: your turn", fresh=True)
    f.p("Answers in grey.", 13.5, gap=10)
    groups = [
        ("What is it?", ["log₃ 9", "log₂ 32", "log₁₀ 0.001", "log₆ 1", "Write 5³ = 125 as a log", "Write log₂ 64 = 6 as a power"],
         "1. 2   2. 5   3. −3   4. 0   5. log₅ 125 = 3   6. 2⁶ = 64"),
        ("Laws", ["Write as one log: log 4 + log 5", "Write as one log: 3 log 2 − log 4",
                  "Expand: log(x³y/z)"],
         "7. log 20   8. log 2 (since 8/4 = 2)   9. 3 log x + log y − log z"),
        ("Solve", ["3ˣ = 81", "5ˣ = 40 (2 d.p.)", "eˣ = 20 (2 d.p.)",
                   "How many years for money at 8% to double?", "Make t the subject: N = N₀e^(−λt)"],
         "10. 4   11. 2.29   12. ln 20 ≈ 3.00   13. log 2 / log 1.08 ≈ 9.0 years   14. t = (1/λ) ln(N₀/N)"),
    ]
    k = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.PURPLE, F.BOLD, gap=6)
        for qq in qs:
            f.text(f"{k}. {qq}", 13, gap=5, x=L + 14)
            k += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14, w=W - 14)
    ch.check([sp.log(9, 3), sp.log(32, 2), sp.log(sp.Rational(1, 1000), 10), sp.log(1, 6)], [2, 5, -3, 0])
    ch.check_num(lg(4) + lg(5), lg(20), tol=1e-12)
    ch.check_num(3 * lg(2) - lg(4), lg(2), tol=1e-12)
    ch.check_num(lg(40) / lg(5), 2.29, tol=0.005)
    ch.check_num(math.log(20), 3.00, tol=0.005)
    ch.check_num(lg(2) / lg(1.08), 9.0, tol=0.01)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    question(ch)
    undo(ch)
    scale(ch)
    laws(ch)
    q1(ch)
    solving(ch)
    q2(ch)
    q3(ch)
    your_turn(ch)
