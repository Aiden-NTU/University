"""Chapter 39 - Exam pocket cards.

One card per exam-critical topic: the handful of facts that unlock every question
of that type (the "y = mx + c" method). Built from past Foundation / engineering
maths papers and the NTU lecture sequence. Read the matching chapter for the why;
drill these cards until rinse-and-repeat is automatic.
"""
from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, title_block
from content.toc import CHAPTERS

ORDER = 39
NUM = 39
TITLE = "Exam pocket cards: the facts that unlock each topic"
SHORT = "Pocket cards"
SLUG = "Pocket-Cards"
ACCENT = C.BROWN
REQUIRES = []
INTRODUCES = []

PAPER = "#fffaf0"
CREAM = "#fbf1e2"


# Each card: (title, chapter_num, tier, facts)
# facts: list of (label, latex_or_None, words)
# tier 1 = must for pass/70% on module-shaped papers; tier 2 = stretch / later lectures
CARDS = [
    ("Fractions", 2, 1, [
        ("Add / subtract", r"\frac{a}{b}\pm\frac{c}{d}=\frac{ad\pm bc}{bd}", "common denom is already in the formula"),
        ("Multiply", r"\frac{a}{b}\times\frac{c}{d}=\frac{ac}{bd}", None),
        ("Divide", r"\frac{a}{b}\div\frac{c}{d}=\frac{a}{b}\times\frac{d}{c}", "flip the second, then multiply"),
        ("Inputs", None, "whole = n/1; mixed → improper first; simplify only if asked"),
    ]),
    ("Decimals, rounding, standard form", 3, 1, [
        ("d.p.", None, "look at the next digit: ≥5 rounds up"),
        ("s.f.", None, "start counting from the first non-zero digit"),
        ("Standard form", r"a\times10^n,\ 1\le a<10", "scientific notation is the same idea"),
        ("Recurring → fraction", None, "x = 0.ȧḃ…; multiply by 10^k; subtract; solve for x"),
    ]),
    ("Percentage and ratio", 4, 1, [
        ("Percent of", r"\frac{x}{100}\times y", None),
        ("Multiplier", r"\text{new}=\text{old}\times\frac{100\pm r}{100}", "+ for increase, − for decrease"),
        ("Reverse %", r"\text{original}=\frac{\text{new}}{1\pm r/100}", "undo a completed % change"),
        ("Share in ratio a:b:c", None, "parts = a+b+c; one part = total ÷ parts; each = parts × one"),
    ]),
    ("Indices", 9, 1, [
        ("Laws", r"a^m a^n=a^{m+n},\ \frac{a^m}{a^n}=a^{m-n},\ (a^m)^n=a^{mn}", None),
        ("Zero / negative", r"a^0=1,\ a^{-n}=\frac{1}{a^n}", "a ≠ 0"),
        ("Fractional", r"a^{1/n}=\sqrt[n]{a},\ a^{m/n}=(\sqrt[n]{a})^m", None),
    ]),
    ("Number bases", 10, 1, [
        ("Binary → decimal", None, "add place values: … 16 8 4 2 1"),
        ("Decimal → binary", None, "repeated ÷2; remainders bottom→top"),
        ("Hex", None, "groups of 4 bits; A=10 … F=15"),
        ("Binary +/−", None, "same as decimal but place values are powers of 2; show working"),
    ]),
    ("Expand and factorise", 12, 1, [
        ("Expand", r"(a+b)(c+d)=ac+ad+bc+bd", "every left term hits every right term"),
        ("Common factor", r"ab+ac=a(b+c)", "pull out the HCF of the terms"),
        ("Quadratic", None, "find two numbers that multiply to ac and add to b; split middle"),
        ("Difference of squares", r"a^2-b^2=(a-b)(a+b)", None),
    ]),
    ("Transposing", 14, 1, [
        ("Balance", None, "do the same inverse op to both sides"),
        ("Undo order", None, "unwrap outside-in (opposite of BIDMAS)"),
        ("Goal", None, "get the wanted letter alone on one side"),
    ]),
    ("Solving equations", 15, 1, [
        ("Linear", None, "expand → collect like terms → divide"),
        ("Simultaneous", None, "elimination (align one letter) or substitution"),
        ("Quadratic factorise", r"(x-p)(x-q)=0\Rightarrow x=p\text{ or }x=q", "zero-product rule"),
        ("Quadratic formula", r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}", "when factorising fails"),
    ]),
    ("Sets and Venn", 6, 1, [
        ("Symbols", None, "∪ union (OR), ∩ intersection (AND), ′ complement, − difference"),
        ("Count union", r"n(A\cup B)=n(A)+n(B)-n(A\cap B)", "don't double-count the overlap"),
        ("Power set", r"|P(S)|=2^n", "all subsets of an n-element set"),
        ("Venn habit", None, "fill from the middle out; unknown region = x"),
    ]),
    ("Logic / truth tables", 7, 1, [
        ("Rows", r"2^n", "n letters → that many rows"),
        ("AND / OR / NOT", None, "∧ both T; ∨ either T; ¬ flips"),
        ("Implication", r"P\Rightarrow Q", "false only when P is T and Q is F"),
        ("Classify", None, "final column: all T = tautology; all F = contradiction; mixed = contingency"),
    ]),
    ("Sequences and series", 17, 1, [
        ("AP nth term", r"a_n=a+(n-1)d", "a = first term, d = common difference"),
        ("AP sum", r"S_n=\frac{n}{2}(2a+(n-1)d)=\frac{n}{2}(a+l)", "l = last term"),
        ("GP nth term", r"a_n=ar^{n-1}", "r = common ratio"),
        ("GP sum", r"S_n=\frac{a(1-r^n)}{1-r}\ (r\neq1)", r"|r|<1:\ S_\infty=\frac{a}{1-r}"),
    ]),
    ("Functions", 18, 1, [
        ("Evaluate", None, "replace every x with the given number; brackets help"),
        ("Compose", r"(f\circ g)(x)=f(g(x))", "inside first"),
        ("Inverse", None, "swap x and y (or set y = f(x)), then make x the subject; rename"),
    ]),
    ("Straight line", 20, 1, [
        ("Core", r"y=mx+c", "m = gradient, c = y-intercept"),
        ("Gradient", r"m=\frac{y_2-y_1}{x_2-x_1}", "rise over run"),
        ("Point-gradient", r"y-y_1=m(x-x_1)", "when you know a point and m"),
        ("Parallel / perp", r"m_1=m_2;\quad m_1 m_2=-1", "perp: negative reciprocal"),
    ]),
    ("Matrices (2×2)", 16, 1, [
        ("Multiply", None, "row of left · column of right; sizes must match"),
        ("Determinant", r"\det\begin{bmatrix}a&b\\c&d\end{bmatrix}=ad-bc", None),
        ("Inverse", r"\frac{1}{ad-bc}\begin{bmatrix}d&-b\\-c&a\end{bmatrix}", "swap diagonal, flip off-diagonal signs"),
        ("Solve Ax = b", None, "x = A⁻¹b when det ≠ 0"),
    ]),
    ("Probability", 25, 1, [
        ("Basic", r"p=\frac{\text{favourable}}{\text{total}}", "equally likely outcomes"),
        ("AND / OR", None, "independent: multiply; mutually exclusive: add"),
        ("Conditional", r"p(E|F)=\frac{p(E\cap F)}{p(F)}", None),
        ("Tree", None, "multiply along a path; add across paths; watch with/without replacement"),
    ]),
    ("Trigonometry (right-angled)", 28, 1, [
        ("SOH CAH TOA", r"\sin=\frac{o}{h},\ \cos=\frac{a}{h},\ \tan=\frac{o}{a}", None),
        ("Pythagoras", r"h^2=o^2+a^2", None),
        ("Exact values", None, "0°, 30°, 45°, 60°, 90°: memorise sin/cos/tan table"),
        ("CAST / graph", None, "find all solutions in the given range from the principal angle"),
    ]),
    ("Statistics (descriptive)", 24, 1, [
        ("Mean", r"\bar x=\frac{\sum x}{n}", "or Σfx / Σf from a frequency table"),
        ("Median / mode", None, "middle when ordered; most frequent"),
        ("IQR", None, "Q3 − Q1; resistant to outliers"),
        ("SD", r"s=\sqrt{\frac{\sum(x-\bar x)^2}{n}}\ \text{or}\ n-1", "spread around the mean"),
    ]),
    ("Vectors", 32, 1, [
        ("Add / scale", None, "component-wise; k⟨x,y⟩ = ⟨kx, ky⟩"),
        ("Magnitude", r"|\mathbf a|=\sqrt{x^2+y^2(+z^2)}", None),
        ("Dot product", r"\mathbf a\cdot\mathbf b=|\mathbf a||\mathbf b|\cos\theta=x_1x_2+y_1y_2", "perp ⇒ dot = 0"),
        ("Unit vector", r"\hat{\mathbf a}=\mathbf a/|\mathbf a|", None),
    ]),
    ("Differentiation (core)", 34, 1, [
        ("Power rule", r"\frac{d}{dx}x^n=nx^{n-1}", "constants differentiate to 0"),
        ("Sum / multiple", None, "term by term; constant factors stay"),
        ("Turning points", None, "dy/dx = 0; 2nd derivative (or sign check) for max/min"),
        ("Tangent", None, "m = dy/dx at the point; then y − y₁ = m(x − x₁)"),
    ]),
    ("Integration (core)", 36, 1, [
        ("Reverse power", r"\int x^n\,dx=\frac{x^{n+1}}{n+1}+C\ (n\neq-1)", None),
        ("Definite", r"\int_a^b f=F(b)-F(a)", "area under curve (watch sign below axis)"),
        ("1/x and e^x", r"\int\frac1x=\ln|x|+C,\ \int e^x=e^x+C", None),
    ]),
    # --- tier 2: later / stretch for 70%+ and full module ---
    ("Logs and exponentials", 22, 2, [
        ("Definition", r"y=\log_b x\ \Leftrightarrow\ b^y=x", None),
        ("Laws", r"\log(ab)=\log a+\log b,\ \log(a/b)=\log a-\log b,\ \log(a^k)=k\log a", None),
        ("Solve a^x = b", None, "take logs both sides, or rewrite as log"),
        ("e and ln", None, "ln = log base e; inverse of exp"),
    ]),
    ("Bayes and Normal", 26, 2, [
        ("Bayes", r"p(A|B)=\frac{p(B|A)\,p(A)}{p(B)}", "prior → posterior after evidence"),
        ("Total probability", None, "partition B via A and A′ (or a tree)"),
        ("z-score", r"z=\frac{x-\mu}{\sigma}", "then use the Normal table"),
    ]),
    ("Further differentiation", 35, 2, [
        ("Product", r"(uv)'=u'v+uv'", None),
        ("Quotient", r"(u/v)'=(u'v-uv')/v^2", None),
        ("Chain", r"\frac{dy}{dx}=\frac{dy}{du}\frac{du}{dx}", "function of a function"),
    ]),
    ("Trig identities / polar", 33, 2, [
        ("Pythagorean", r"\sin^2\theta+\cos^2\theta=1", None),
        ("Polar ↔ Cartesian", r"x=r\cos\theta,\ y=r\sin\theta,\ r=\sqrt{x^2+y^2}", "fix θ for quadrant"),
    ]),
]


def _fit(pg, latex, size, maxw, lo=9):
    while size > lo and pg.eq_size(latex, size)[0] > maxw:
        size -= 0.5
    return size


def cover(ch):
    pg = title_block(ch, 39, "Exam pocket cards",
                     "the handful of facts that unlock each topic — like y = mx + c for lines",
                     C.BROWN, PAPER)
    f = ch.flow(top=220)
    f.p("You said it yourself: once {B:y = mx + c}, the gradient formula, and \"parallel / "
        "perpendicular\" are in your head, every straight-line question is rinse and repeat. "
        "These cards do that for every exam-critical topic.", 14, gap=10)
    f.text("How to use them", 15, C.BROWN, F.BOLD, gap=6)
    for s in [
        "Read the matching chapter once for the {g:why} (pictures, derivations).",
        "Memorise the card until you can write it from blank paper.",
        "Drill past-paper questions of that type until the card fires automatically.",
        "{o:Tier 1} cards first (pass → 70%). {p:Tier 2} after those are automatic.",
    ]:
        f.bullet(s, 13)
    f.gap(8)
    f.p("{y:Past papers reviewed:} Goldsmiths Foundation Maths IS50002 (2010–2019), NCC "
        "FDM May 2016, Bolton EEE4011, plus your NTU lecture sequence L01–L17. "
        "{R:IS51002} (graph theory, relations, induction) is a {B:different} module — not the "
        "focus of this guide.", 12.5, C.GREY, gap=8)


def priority(ch):
    f = flow(ch)
    f.new_page()
    f.text("Four-week priority map", 22, C.BROWN, F.BOLD, gap=10)
    f.p("Your NTU module end-goals (graphs, descriptive stats, rearrange equations, "
        "calculus on curves, geometry & probability, vectors) sit mostly in Tier 1. "
        "Goldsmiths-style foundation papers match Tier 1 almost question-for-question.", 13.5, gap=12)

    weeks = [
        ("Week 1 — number fluency", C.ORANGE,
         "Ch 1–5, 9–10: fractions, decimals, %, ratio, indices, bases. No calculator habits."),
        ("Week 2 — algebra engine", C.BLUE,
         "Ch 8, 11–15: expand, factorise, transpose, linear / simultaneous / quadratic."),
        ("Week 3 — structures + chance", C.PURPLE,
         "Ch 6–7, 16–18, 25: sets, logic, matrices, sequences, functions, probability trees."),
        ("Week 4 — graphs, geo, calc core", C.GREEN,
         "Ch 19–20, 24, 28, 32, 34, 36: lines, stats, trig, vectors, differentiate, integrate."),
    ]
    for title, col, body in weeks:
        y = f.reserve(72)
        pg = f.pg
        pg.rect(L, y, W, 64, col, 1.4, fillcolor=C.LIGHT[col], r=8)
        pg.text(L + 14, y + 10, title, 14, col, F.BOLD)
        pg.rich(L + 14, y + 32, body, W - 28, 12)
    f.gap(8)
    f.p("Daily drill: {B:one pocket card from memory}, then {B:two past-paper parts} of that type. "
        "Aim for speed with full working shown — foundation papers often ban calculators.", 13.5, gap=8)


def exam_map(ch):
    f = flow(ch)
    f.new_page()
    f.text("What the papers actually ask", 22, C.BROWN, F.BOLD, gap=8)
    f.p("Goldsmiths IS50002 Foundation Maths is remarkably stable across years. Ten questions, "
        "~10 marks each, no calculator. Typical map → guide chapters:", 13.5, gap=10)

    rows = [
        ("Q-type (every year-ish)", "Guide chapters"),
        ("Fractions, %, order of ops, d.p./s.f., standard form", "2, 3, 4, 9"),
        ("Algebra: expand, substitute, indices, factors", "8, 9, 11, 12"),
        ("Number bases (bin/hex) ± matrices sometimes", "10, 16"),
        ("Sets, Venn, truth tables (tautology / contingency / contradiction)", "6, 7"),
        ("Linear, simultaneous, quadratic", "15"),
        ("Sequences and series (AP/GP, Σ)", "17"),
        ("Functions: evaluate, compose, inverse", "18"),
        ("Graphs / straight lines / intersection", "19, 20"),
        ("Trig: Pythagoras, sin/cos/tan, sketch sin", "27, 28, 29"),
        ("Matrices 2×2: +, ×, I, inverse", "16"),
        ("Probability: dice/coins, trees, with/without replacement", "25"),
    ]
    # header + rows as a simple list
    y = f.reserve(22)
    pg = f.pg
    pg.rect(L, y, W, 20, C.BROWN, 0.1, fillcolor=C.BROWN, r=3)
    pg.text(L + 8, y + 3, rows[0][0], 11, "#ffffff", F.BOLD)
    pg.text(L + 360, y + 3, rows[0][1], 11, "#ffffff", F.BOLD)
    for a, b in rows[1:]:
        y = f.reserve(28)
        pg = f.pg
        pg.text(L + 8, y + 4, a, 11, C.INK, w=340)
        pg.text(L + 360, y + 4, b, 12, C.BROWN, F.BOLD)
        pg.line(L, y + 26, R, y + 26, "#eadfc8", 0.7)

    f.gap(10)
    f.p("{B:NTU lectures add} descriptive stats (L04), charts (L05), Bayes/Normal (L08–09), "
        "vectors (L10), polar (L11), and calculus (L14–17). Those are Tier 1 for your course "
        "even when Goldsmiths papers stop before them.", 13, C.GREY, gap=8)
    f.p("{R:Skip for now (unless your paper is IS51002-shaped):} graph theory, relations / "
        "orders, proof by induction, homogeneous coordinates, complex numbers, ODEs.", 13, gap=8)


def card_page(ch, title, chnum, tier, facts):
    """One A4 pocket card."""
    col = C.ORANGE if tier == 1 else C.PURPLE
    bg = PAPER if tier == 1 else "#faf6ff"
    pg = ch.new_page(bg=bg)
    # outer frame
    pg.rect(36, 36, 523, 770, col, 2.8, fillcolor=C.LIGHT[col], r=16)
    pg.rect(52, 52, 491, 738, col, 1.2, r=12, dash=(5, 3))

    tier_lab = "TIER 1 · exam core" if tier == 1 else "TIER 2 · stretch / later lectures"
    pg.text(297, 68, tier_lab, 11, col, F.BOLD, align="center")
    pg.text(297, 92, title.upper(), 22, C.INK, F.BOLD, align="center")
    ref = CHAPTERS.get(chnum, "")
    pg.note(297, 122, f"full explanation → Chapter {chnum}: {ref}", col, 16, align="center")

    y = 155
    for label, latex, words in facts:
        box_h = 118 if latex else 88
        if y + box_h > 760:
            break
        pg.rect(70, y, 455, box_h - 8, "#ffffff", 1.1, fillcolor="#ffffff", r=8)
        pg.rect(70, y, 8, box_h - 8, col, 0.1, fillcolor=col, r=0)
        pg.text(90, y + 10, label, 13, col, F.BOLD)
        yy = y + 32
        if latex:
            s = _fit(pg, latex, 18, 420)
            h = pg.eq_size(latex, s)[1]
            pg.eq(297, yy, latex, s, align="center")
            yy += h + 8
        if words:
            pg.rich(90, yy, words, 420, 12, C.INK)
        y += box_h

    pg.note(297, 780, "cover the card · write from memory · check · then do 2 paper parts",
            C.GREY, 15, align="center")


def index_page(ch):
    f = flow(ch)
    f.new_page()
    f.text("Card index", 22, C.BROWN, F.BOLD, gap=8)
    f.p("Tier 1 first. Tick each card when you can reproduce it blank.", 13, C.GREY, gap=10)
    for title, chnum, tier, _ in CARDS:
        col = C.ORANGE if tier == 1 else C.PURPLE
        y = f.reserve(26)
        pg = f.pg
        pg.circle(L + 10, y + 8, 7, col, 1.2)  # tick target
        pg.text(L + 28, y + 2, f"Ch {chnum:02d}", 11, col, F.BOLD, w=50)
        pg.text(L + 80, y + 2, title, 12, C.INK, F.BOLD, w=300)
        pg.text(R - 80, y + 2, f"T{tier}", 11, col, F.BOLD, w=40, align="right")


def build(ch):
    cover(ch)
    priority(ch)
    exam_map(ch)
    index_page(ch)
    for title, chnum, tier, facts in CARDS:
        card_page(ch, title, chnum, tier, facts)
