"""Chapter 5 - Measurement. A pounds-and-pence swap chain for units, walking the fence, counting
squares, a 100 x 100 grid, stacking cubes, a clock face and 'per' as a division."""
import math

import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, section, step, title_block

ORDER = 5
NUM = 5
TITLE = "Measurement"
SHORT = "Measurement"
SLUG = "Measurement"
ACCENT = C.ORANGE
REQUIRES = ["decimal-arithmetic", "multiplication", "division", "fraction", "square-and-root-words",
            "pi-word", "multiplier", "unitary-method", "rounding"]
INTRODUCES = ["units", "metric-prefixes", "unit-conversion", "perimeter", "area", "area-units",
              "volume", "volume-units", "circle-measures", "time-conversion", "compound-units",
              "speed-distance-time", "density"]

WOOD = "#e9d3a8"
PAPER = "#fbfbf6"


def icon(pg, x, y):
    pg.rect(x, y + 5, 18, 8, C.BROWN, 1, fillcolor=WOOD)
    for i in range(1, 6):
        pg.line(x + i * 3, y + 5, x + i * 3, y + (9 if i % 2 else 8), C.BROWN, 0.7)


def sec(f, t, **kw):
    section(f, t, C.ORANGE, icon, **kw)


def ruler(pg, x, y, w, n, label_every=1, unit="", h=26):
    pg.rect(x - 6, y, w + 12, h, C.BROWN, 1.2, fillcolor=WOOD)
    for i in range(n + 1):
        X = x + w * i / n
        big = i % label_every == 0
        pg.line(X, y, X, y + (12 if big else 6), C.BROWN, 0.9)
        if big:
            pg.text(X, y + 12, f"{i // label_every}", 8, C.BROWN, align="center", solid=False)
    if unit:
        pg.text(x + w + 12, y + 6, unit, 10, C.BROWN, F.BOLD)


def chain(pg, x, y, units, ops, col=C.ORANGE, bw=70, gap=62, back=None):
    """Boxes of units joined by arrows labelled with the fixed swap rate."""
    xs = []
    for i, u in enumerate(units):
        bx = x + i * (bw + gap)
        xs.append(bx)
        pg.rect(bx, y, bw, 34, col, 1.5, fillcolor=C.LIGHT[col], r=8)
        pg.text(bx + bw / 2, y + 9, u, 14, C.INK, F.BOLD, align="center")
    for i, op in enumerate(ops):
        x1 = xs[i] + bw + 4
        x2 = xs[i + 1] - 4
        pg.arrow(x1, y + 12, x2, y + 12, C.GREEN, 1.6, head=5)
        pg.text((x1 + x2) / 2, y - 6, op, 12, C.GREEN, F.BOLD, align="center")
        if back:
            pg.arrow(x2, y + 26, x1, y + 26, C.RED, 1.2, head=5)
            pg.text((x1 + x2) / 2, y + 36, back[i], 11, C.RED, F.BOLD, align="center")
    return xs


def cube(pg, x, y, s, fc="#ffd8a8", ec=C.BROWN):
    d = s * 0.45
    pg.fillpoly([(x, y), (x + s, y), (x + s, y + s), (x, y + s)], fc, outline=ec, width=0.7, layer=C.MAIN)
    pg.fillpoly([(x, y), (x + d, y - d), (x + s + d, y - d), (x + s, y)], "#ffe8cc", outline=ec, width=0.7,
                layer=C.MAIN)
    pg.fillpoly([(x + s, y), (x + s + d, y - d), (x + s + d, y + s - d), (x + s, y + s)], "#f0b878",
                outline=ec, width=0.7, layer=C.MAIN)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 5, "Measurement", "how long, how much space, how much stuff, how fast",
                     C.ORANGE, PAPER)
    ruler(pg, L + 20, 200, 440, 30, 2, "cm")
    for i in range(3):
        for j in range(4):
            cube(pg, L + 40 + j * 26, 320 - i * 26, 24)
    pg.note(L + 30, 350, "24 little cubes: a volume", C.BROWN, 17)
    for i in range(5):
        for j in range(3):
            pg.rect(L + 260 + i * 22, 262 + j * 22, 22, 22, C.ORANGE, 0.6, fillcolor=C.LIGHT[C.ORANGE])
    pg.note(L + 260, 336, "15 squares: an area", C.ORANGE, 17)
    f = ch.flow(top=410)
    f.p("Measuring is counting how many {B:units} fit. A length counts little rulers, an area counts "
        "little squares, a volume counts little cubes. Almost every mistake in this topic comes from "
        "mixing up units, so this chapter slows right down on {B:changing units}.", 14, gap=10)
    f.p("It also covers perimeter, area and volume of the everyday shapes, time (which is sneakily "
        "not decimal), and \"per\" units like metres per second, which appear all over your "
        "lectures (the slides write speeds as ms⁻¹).", 14, gap=10)
    f.p("{y:Used throughout the lectures (units in L03, L09, L10, L14-L16).}", 12.5)


def units(ch):
    f = flow(ch)
    sec(f, "A number without a unit means nothing")
    f.p("\"The desk is 3 long.\" 3 what? Pencils? Hands? Metres? The {B:unit} is the thing you "
        "counted. {B:The number and the unit always travel together.}", 14, gap=8)
    ch.term("unit", "the fixed amount you count with: a metre, a gram, a second...")
    y = f.reserve(112) + 14
    pg = f.pg
    pg.rect(L + 20, y + 30, 300, 14, C.BROWN, 1.2, fillcolor=WOOD)
    pg.note(L + 330, y + 26, "the same desk...", C.BROWN, 16)
    for i in range(5):
        pg.rect(L + 20 + i * 60, y + 6, 58, 10, C.ORANGE, 0.8, fillcolor=C.LIGHT[C.ORANGE], r=4)
    pg.note(L + 20, y - 12, "5 pencils", C.ORANGE, 15)
    for i in range(3):
        pg.rect(L + 20 + i * 100, y + 52, 98, 10, C.BLUE, 0.8, fillcolor=C.LIGHT[C.BLUE], r=4)
    pg.note(L + 20, y + 62, "3 rulers", C.BLUE, 15)
    pg.note(L + 330, y + 50, "5 or 3? Both right,\nwith their units.", C.RED, 16)
    f.p("Scientists agreed on standard units so everyone gets the same number: the {B:metre} (m) "
        "for length, the {B:kilogram} (kg) for mass, the {B:second} (s) for time, the {B:litre} (l) "
        "for liquid volume.", 14)


def prefixes(ch):
    f = flow(ch)
    sec(f, "The prefix ladder: kilo, centi, milli...", room=420)
    f.p("Instead of inventing new names, the metric system sticks a {B:prefix} (a word-start) on "
        "the front. The prefix is a multiplier (Chapter 4). Each one means the same thing on "
        "{B:every} unit:", 14, gap=8)
    ch.term("prefix (metric)", "a word-start like kilo- or milli- that multiplies a unit by 1000, 1/1000 ...")
    rows = [("giga", "G", "1,000,000,000", "GB of storage", C.PURPLE),
            ("mega", "M", "1,000,000", "MB file, MW power", C.PURPLE),
            ("kilo", "k", "1000", "km, kg, kB", C.BLUE),
            ("(none)", "", "1", "m, g, l, s, B", C.INK),
            ("centi", "c", "1/100 = 0.01", "cm", C.GREEN),
            ("milli", "m", "1/1000 = 0.001", "mm, mg, ml, ms", C.GREEN),
            ("micro", "µ", "1/1,000,000", "µm, µs", C.TEAL)]
    y = f.reserve(len(rows) * 30 + 10)
    pg = f.pg
    for i, (name, sym, val, ex, col) in enumerate(rows):
        yy = y + i * 30
        ind = i * 18
        pg.rect(L + 10 + ind, yy, 250, 26, col, 1.1, fillcolor=C.LIGHT.get(col, "#ffffff"), r=4)
        pg.text(L + 20 + ind, yy + 6, name, 13, col, F.BOLD)
        pg.text(L + 90 + ind, yy + 6, sym, 13, C.INK, F.BOLD)
        pg.text(L + 120 + ind, yy + 6, "× " + val, 12, C.INK)
        pg.note(L + 290 + ind, yy + 2, ex, col, 15)
    pg.note(L + 440, y + 64, "bigger", C.PURPLE, 15)
    pg.arrow(L + 488, y + 60, L + 488, y + 4, C.PURPLE, 1.4)
    pg.arrow(L + 488, y + 150, L + 488, y + 206, C.TEAL, 1.4)
    pg.note(L + 440, y + 130, "smaller", C.TEAL, 15)
    f.p("So a {B:kilo}gram is 1000 grams, a {B:milli}litre is a thousandth of a litre, a "
        "{B:centi}metre is a hundredth of a metre. {R:Careful:} capital M (mega) and small m (milli) "
        "differ by a factor of a thousand million!", 14, gap=8)
    f.p("{h:Computer aside:} in computing, a kilobyte is sometimes 1024 bytes instead of 1000, for "
        "reasons you'll see in Chapter 10 (number bases).", 13, C.BROWN)


def exchange(ch):
    f = flow(ch)
    sec(f, "Changing units is like swapping coins", room=560)
    f.p("A £1 coin is always worth exactly 100 pennies. Not roughly, not today's rate: {B:always}, by "
        "definition. Swap one pound for pennies and the {B:number gets bigger} (1 becomes 100), but you have "
        "exactly the same money, just counted in smaller pieces. Units work the same way: {B:1 m is always "
        "exactly 100 cm}.", 14, gap=10)
    y = f.reserve(96)
    pg = f.pg
    pg.circle(L + 45, y + 42, 30, "#b8860b", 2, fillcolor="#f5d77a")
    pg.text(L + 15, y + 32, "£1", 17, "#7a5a00", F.BOLD, w=60, align="center")
    pg.text(L + 88, y + 30, "=", 22, C.INK, F.BOLD)
    for st in range(10):
        for k in range(10):
            pg.ellipse(L + 130 + st * 17, y + 76 - k * 6, 7, 3, "#9a5b2f", 0.8, fillcolor="#d99a6c")
    pg.text(L + 125, y + 84, "100 pennies (10 stacks of 10)", 10, "#9a5b2f", F.BOLD)
    pg.note(L + 320, y + 6, "same amount of money,\nbigger number, because\neach piece is smaller.\n"
            "1 m → 100 cm works identically.", C.INK, 15, w=R - L - 320)
    f.p("(Currency exchange between countries is a bad model for this, because those rates change every day. "
        "Unit swaps never change: 1 km is 1000 m today, tomorrow and forever.)", 12.5, C.GREY, gap=10)
    y = f.reserve(120)
    pg = f.pg
    chain(pg, L + 10, y + 26, ["km", "m", "cm", "mm"], ["× 1000", "× 100", "× 10"],
          back=["÷ 1000", "÷ 100", "÷ 10"])
    pg.note(L + 10, y - 4, "going to smaller units: multiply (you need more of them)", C.GREEN, 15)
    pg.note(L + 10, y + 84, "going to bigger units: divide (you need fewer of them)", C.RED, 15)
    f.p("{b:Example: 2.5 km in centimetres.} Walk along the chain, one swap at a time:", 14, gap=6)
    step(f, r"2.5\text{ km}", "start", size=19)
    step(f, r"2.5\times1000=2500\text{ m}", "swap km → m: × 1000", size=19)
    step(f, r"2500\times100=250{,}000\text{ cm}", "swap m → cm: × 100", size=19, color=C.GREEN)
    ch.check(sp.Rational(25, 10) * 1000 * 100, 250000)
    f.p("{b:Backwards: 350 g in kg.} Grams are small, kilograms big, so divide: "
        "$350 \\div 1000 = 0.35$ kg.", 14, gap=8)
    ch.check(sp.Rational(350, 1000), sp.Rational(35, 100))
    f.p("{G:Sense check every time:} is the new number bigger or smaller? Metres to centimetres "
        "must get bigger (a small unit needs lots). If it shrank, you went the wrong way.", 13.5)


def perimeter(ch):
    f = flow(ch)
    sec(f, "Perimeter: walk round the fence", room=240)
    f.p("The {B:perimeter} is the distance all the way round the edge. Imagine walking along a "
        "garden fence and adding up every stretch until you're back at the start:", 14, gap=8)
    ch.term("perimeter", "the total length of the boundary of a shape")
    y = f.reserve(148) + 16
    pg = f.pg
    pg.rect(L + 30, y + 10, 175, 100, C.GREEN, 2.2, fillcolor=C.LIGHT[C.GREEN])
    pg.note(L + 100, y - 12, "7 m", C.INK, 16)
    pg.note(L + 100, y + 112, "7 m", C.INK, 16)
    pg.note(L + 2, y + 50, "4 m", C.INK, 16)
    pg.note(L + 212, y + 50, "4 m", C.INK, 16)
    pg.circle(L + 30, y + 10, 5, C.RED, 1, fillcolor=C.RED)
    pg.note(L + 36, y + 12, "start", C.RED, 14)
    pg.arrow(L + 60, y + 22, L + 170, y + 22, C.RED, 1.2, head=5)
    pg.arrow(L + 192, y + 30, L + 192, y + 90, C.RED, 1.2, head=5)
    pg.eq(L + 260, y + 20, r"7+4+7+4=22\text{ m}", 20, C.GREEN)
    pg.note(L + 260, y + 56, "every side counted once;\nthe answer is a length (m)", C.RED, 15)
    ch.check(7 + 4 + 7 + 4, 22)
    f.p("{b:Circles:} the perimeter of a circle is called the {B:circumference}. Wrap a string round "
        "any circle and it's always about 3.14 diameters long; that number is π (Part 0):", 14, gap=6)
    ch.term("circumference", "the perimeter of a circle")
    y = f.reserve(60)
    pg = f.pg
    pg.circle(L + 50, y + 26, 24, C.BLUE, 1.6)
    pg.line(L + 26, y + 26, L + 74, y + 26, C.RED, 1.2)
    pg.note(L + 32, y + 28, "d", C.RED, 14)
    pg.eq(L + 100, y + 6, r"C=\pi d=2\pi r", 20)
    pg.note(L + 250, y + 4, "d = diameter (across), r = radius\n(centre to edge, half of d)", C.RED, 15)
    ch.formula(r"C=\pi d=2\pi r", "circumference of a circle")
    ch.term("radius", "distance from the centre of a circle to its edge")
    ch.term("diameter", "distance straight across a circle through the centre; twice the radius")


def area(ch):
    f = flow(ch)
    sec(f, "Area: count the squares", room=380)
    f.p("{B:Area} is how much flat surface a shape covers. We measure it by counting unit squares. A "
        "rectangle 5 cm by 3 cm holds 3 rows of 5 squares:", 14, gap=8)
    ch.term("area", "the amount of flat surface inside a shape, counted in unit squares")
    y = f.reserve(90)
    pg = f.pg
    for i in range(3):
        for j in range(5):
            pg.rect(L + 30 + j * 24, y + i * 24, 24, 24, C.ORANGE, 0.7, fillcolor=C.LIGHT[C.ORANGE])
    pg.eq(L + 200, y + 10, r"5\times3=15\text{ cm}^2", 20)
    pg.note(L + 200, y + 44, "cm² (\"square centimetres\"): each little\nsquare is 1 cm by 1 cm", C.RED, 15)
    ch.symbol(r"\text{cm}^2", "square centimetres", "a count of 1 cm x 1 cm squares")
    ch.check(5 * 3, 15)
    f.p("Other shapes are rectangles in disguise. {B:Cut and move pieces}; the area can't change:",
        14, gap=8)
    y = f.reserve(150)
    pg = f.pg
    # triangle: half a rectangle
    x0 = L + 10
    pg.rect(x0, y + 20, 120, 70, C.GREY, 0.8, dash=(3, 3))
    pg.fillpoly([(x0, y + 90), (x0 + 120, y + 90), (x0 + 120, y + 20)], C.LIGHT[C.BLUE], outline=C.BLUE)
    pg.note(x0, y - 4, "triangle = half a rectangle", C.BLUE, 14)
    pg.eq(x0, y + 100, r"A=\tfrac12\times b\times h", 16)
    # parallelogram: slide a triangle
    x1 = L + 175
    pg.fillpoly([(x1 + 30, y + 20), (x1 + 140, y + 20), (x1 + 110, y + 90), (x1, y + 90)], C.LIGHT[C.GREEN],
                outline=C.GREEN)
    pg.line(x1 + 30, y + 20, x1 + 30, y + 90, C.RED, 1, dash=(3, 2))
    pg.arrow(x1 + 10, y + 70, x1 + 115, y + 70, C.RED, 1.1, bend=-0.2, head=5)
    pg.note(x1, y - 4, "slide the corner across", C.GREEN, 14)
    pg.eq(x1 + 10, y + 100, r"A=b\times h", 16)
    # circle: pizza slices
    x2 = L + 350
    pg.circle(x2 + 50, y + 55, 34, C.PURPLE, 1.4, fillcolor=C.LIGHT[C.PURPLE])
    for k in range(8):
        a = k * math.pi / 4
        pg.line(x2 + 50, y + 55, x2 + 50 + 34 * math.cos(a), y + 55 + 34 * math.sin(a), C.PURPLE, 0.7)
    pg.note(x2, y - 4, "circle", C.PURPLE, 14)
    pg.eq(x2 + 10, y + 100, r"A=\pi r^2", 16)
    pg.note(L + 10, y + 124, "b = base, h = height measured straight up (at right angles to the base), "
            "not along the slope", C.RED, 14, w=W - 10)
    ch.formula(r"A=\tfrac12 bh", "area of a triangle")
    ch.formula(r"A=\pi r^2", "area of a circle")
    f.p("{b:Why πr² for a circle?} Cut it into many thin pizza slices and lay them alternately "
        "point-up, point-down. They form an almost-rectangle: its height is the radius r and its "
        "length is half the circumference, πr. Area ≈ πr × r = πr².", 14, gap=8)
    y = f.reserve(60)
    pg = f.pg
    b = 44
    for k in range(6):
        x = L + 40 + k * b
        pg.fillpoly([(x, y + 50), (x + b, y + 50), (x + b / 2, y + 6)], C.LIGHT[C.PURPLE], outline=C.PURPLE,
                    width=0.7)
        pg.fillpoly([(x + b / 2, y + 6), (x + 3 * b / 2, y + 6), (x + b, y + 50)], "#e2d0f5", outline=C.PURPLE,
                    width=0.7)
    pg.note(L + 370, y + 10, "height r,\nlength πr", C.PURPLE, 15)
    ch.check(sp.pi * 3 ** 2, 9 * sp.pi)


def area_units(ch):
    f = flow(ch)
    sec(f, "The big trap: 1 m² is NOT 100 cm²", room=600)
    f.p("It feels as if it should be. 1 m = 100 cm, so surely 1 m² = 100 cm²? Test it on a square small "
        "enough to see every piece: {B:one square centimetre}, blown up, with millimetres marked. "
        "1 cm = 10 mm.", 14, gap=10)
    y = f.reserve(178)
    pg = f.pg
    s_ = 14
    X0, Y0 = L + 40, y + 22
    for i in range(10):
        for j in range(10):
            pg.rect(X0 + j * s_, Y0 + i * s_, s_, s_, "#c0c0c0", 0.5, fillcolor=C.LIGHT[C.ORANGE] if i == 0 else None)
    pg.rect(X0, Y0, 10 * s_, s_, C.ORANGE, 1.6)
    pg.rect(X0, Y0, 10 * s_, 10 * s_, C.INK, 1.6)
    pg.text(X0, y + 4, "1 cm = 10 mm", 11, C.INK, F.BOLD, w=10 * s_, align="center")
    pg.text(X0 + 10 * s_ + 6, Y0 + 58, "1 cm\n= 10 mm", 11, C.INK, F.BOLD)
    pg.note(L + 270, y + 10, "orange: ONE row of 10 little squares. That's only 10 mm².", C.ORANGE, 15,
            w=R - L - 270)
    pg.note(L + 270, y + 62, "the whole square needs 10 rows of 10 = 100 little squares.", C.INK, 15,
            w=R - L - 270)
    pg.eq(L + 270, y + 108, r"1\text{ cm}^2=100\text{ mm}^2", 18, C.GREEN)
    pg.note(L + 270, y + 136, "not 10 mm²: the 10 happens twice, once across and once down", C.PURPLE, 15,
            w=R - L - 270)
    ch.check(10 * 10, 100)
    f.p("{b:Now the square metre.} Same idea, bigger numbers. 100 cm² is {B:one ribbon} 100 cm long and "
        "1 cm tall, running along the top edge. The square metre is 100 cm tall, so it needs "
        "{B:100 of those ribbons} stacked up:", 14, gap=10)
    y = f.reserve(184)
    pg = f.pg
    S = 140
    X0, Y0 = L + 40, y + 20
    pg.rect(X0, Y0, S, S, C.INK, 1.6, fillcolor="#fafafa")
    for k in range(6):
        pg.rect(X0, Y0 + k * 7, S, 7, C.ORANGE if k == 0 else "#d9a066", 1.6 if k == 0 else 0.6,
                fillcolor="#f6b26b" if k == 0 else "#fbe9d6")
    pg.text(X0 + S / 2 - 6, Y0 + 48, "⋮", 22, "#d9a066", F.BOLD)
    pg.rect(X0, Y0 + S - 7, S, 7, "#d9a066", 0.6, fillcolor="#fbe9d6")
    pg.text(X0, y + 2, "1 m = 100 cm", 11, C.INK, F.BOLD, w=S, align="center")
    pg.text(X0 + S + 6, Y0 + 58, "1 m\n= 100 cm\n(100 ribbons)", 11, C.INK, F.BOLD)
    pg.note(X0, Y0 + S + 4, "ribbons drawn thicker than real, so you can see them", C.GREY, 12)
    pg.note(L + 315, y + 14, "top ribbon = 100 cm²\n(100 little 1 cm squares in a row)\n\n100 ribbons × 100 cm² "
            "each:", C.ORANGE, 15, w=R - L - 315)
    pg.eq(L + 315, y + 110, r"1\text{ m}^2=10{,}000\text{ cm}^2", 18, C.GREEN)
    ch.check(100 * 100, 10000)
    f.p("{b:Why the little ² catches everyone.} \"m²\" is short for m × m. So swap {B:each} m for 100 cm:", 14,
        gap=6)
    step(f, r"1\text{ m}^2=1\text{ m}\times1\text{ m}=100\text{ cm}\times100\text{ cm}=10{,}000\text{ cm}^2",
         "", size=17)
    f.need(96)
    f.p("The trap is mixing up two different things that look alike:", 14, gap=6)
    step(f, r"100\text{ cm}^2", "a hundred little 1 cm squares (one ribbon)", size=18, color=C.ORANGE)
    step(f, r"(100\text{ cm})^2", "a square whose SIDE is 100 cm: 10,000 little squares", size=18, color=C.GREEN)
    f.p("1 m² is the second one. The ² squares everything inside the bracket: the 100 {B:and} the cm.", 14,
        gap=10)
    f.p("{B:Rule:} for area, square the length swap rate. For volume (next page), cube it. "
        "The chain for areas:", 14, gap=8)
    y = f.reserve(70)
    pg = f.pg
    chain(pg, L + 10, y + 20, ["km²", "m²", "cm²", "mm²"], ["× 1,000,000", "× 10,000", "× 100"],
          bw=64, gap=76)
    f.p("{b:Example:} a room of 12 m² in cm²: $12 \\times 10\\,000 = 120\\,000$ cm².", 14)
    ch.check(12 * 10000, 120000)


def volume(ch):
    f = flow(ch)
    sec(f, "Volume: stack the cubes", room=340)
    f.p("{B:Volume} is how much 3-D space something fills, counted in unit cubes. A box 4 cm long, "
        "3 cm wide and 2 cm tall: one layer on the floor holds 4 × 3 = 12 cubes, and there are 2 "
        "layers.", 14, gap=8)
    ch.term("volume", "the amount of 3-D space inside a solid, counted in unit cubes")
    y = f.reserve(120)
    pg = f.pg
    s = 26
    for layer in range(2):
        for r in range(3)[::-1]:
            for c in range(4):
                cube(pg, L + 40 + c * s + r * s * 0.45, y + 80 - layer * s - r * s * 0.45, s)
    pg.eq(L + 270, y + 20, r"4\times3\times2=24\text{ cm}^3", 20)
    pg.note(L + 270, y + 56, "cm³ (\"cubic centimetres\"):\ncount of 1 cm cubes", C.RED, 15)
    ch.symbol(r"\text{cm}^3", "cubic centimetres", "a count of 1 cm cubes")
    ch.check(4 * 3 * 2, 24)
    f.p("{b:The layer idea works for any \"straight-up\" shape:} volume = area of the floor × "
        "height. A cylinder (a tin can) is a stack of circles, like a pile of coins:", 14, gap=6)
    y = f.reserve(60)
    pg = f.pg
    pg.eq(L + 30, y + 6, r"V=\pi r^2\times h", 22)
    pg.note(L + 220, y, "floor area (a circle) × height.\nr = 3 cm, h = 10 cm: V = π × 9 × 10 ≈ 282.7 cm³",
            C.RED, 15)
    ch.formula(r"V=\pi r^2 h", "volume of a cylinder")
    ch.check_num(float(sp.pi * 9 * 10), 282.74, tol=0.01)
    f.p("{b:Volume units, and litres.} A 1 m cube holds 100 × 100 × 100 = 1,000,000 cm³ (the "
        "swap rate is cubed). Liquids use litres:", 14, gap=6)
    y = f.reserve(90)
    pg = f.pg
    cube(pg, L + 40, y + 30, 50, "#cfe8ff", C.BLUE)
    pg.note(L + 30, y + 6, "10 cm", C.BLUE, 14)
    pg.note(L + 130, y + 10, "a 10 cm × 10 cm × 10 cm cube = 1000 cm³ = 1 litre", C.BLUE, 16)
    pg.note(L + 130, y + 40, "so 1 cm³ = 1 ml (a millilitre, a thousandth of a litre)", C.GREEN, 16)
    ch.check(10 ** 3, 1000)


def time(ch):
    f = flow(ch)
    sec(f, "Time is not decimal!", room=260)
    f.p("An hour has {B:60} minutes, not 100. So 1.5 hours is {R:not} 1 hour 50 minutes. The \".5\" "
        "means half an hour, which is 30 minutes. Look at the clock:", 14, gap=8)
    y = f.reserve(120)
    pg = f.pg
    cx, cy, r = L + 70, y + 56, 50
    pg.sector(cx, cy, r, 90, -90, C.LIGHT[C.BLUE])
    pg.circle(cx, cy, r, C.INK, 1.8)
    for k in range(12):
        a = math.radians(90 - k * 30)
        pg.line(cx + 0.85 * r * math.cos(a), cy - 0.85 * r * math.sin(a), cx + r * math.cos(a),
                cy - r * math.sin(a), C.INK, 1)
    pg.line(cx, cy, cx, cy - 40, C.INK, 2)
    pg.line(cx, cy, cx, cy + 40, C.RED, 2)
    pg.note(L + 150, y + 2, "0.5 hour = half the clock = 30 min", C.BLUE, 16)
    rows = [("0.5 h", "0.5 × 60 = 30 min"), ("0.25 h", "0.25 × 60 = 15 min"), ("0.1 h", "0.1 × 60 = 6 min"),
            ("2.75 h", "2 h and 0.75 × 60 = 45 min")]
    for i, (a, b) in enumerate(rows):
        pg.text(L + 150, y + 30 + i * 22, a, 13, C.INK, F.BOLD)
        pg.text(L + 210, y + 30 + i * 22, b, 13, C.INK)
    ch.check(sp.Rational(75, 100) * 60, 45)
    f.p("{B:Hours → minutes: multiply the decimal part by 60.} Minutes → hours: divide by 60, so "
        "40 minutes is $\\frac{40}{60} = \\frac23 \\approx 0.67$ hours.", 14)


def per(ch):
    f = flow(ch)
    sec(f, "\"Per\" means divide: speed, density and friends", room=300)
    f.p("A sprinter runs 100 m in 12.5 s. {B:Speed} is how many metres she covers {B:per} second: "
        "share the 100 m out equally among the 12.5 seconds.", 14, gap=8)
    ch.term("speed", "distance travelled per unit of time: distance ÷ time")
    y = f.reserve(80)
    pg = f.pg
    pg.eq(L + 30, y, r"\text{speed}=\frac{\text{distance}}{\text{time}}=\frac{100\text{ m}}{12.5\text{ s}}=8\text{ m/s}", 20)
    pg.note(L + 30, y + 54, "read m/s as \"metres per second\": the units divide too!", C.RED, 15)
    ch.formula(r"\text{speed}=\frac{\text{distance}}{\text{time}}", "speed")
    ch.check(sp.Rational(100) / sp.Rational(125, 10), 8)
    f.p("{b:Three ways to write the same unit.} Your lecture slides write speeds as "
        "\"ms⁻¹\". It means exactly the same as m/s:", 14, gap=6)
    y = f.reserve(52)
    pg = f.pg
    for i, e in enumerate([r"\text{m/s}", r"\frac{\text{m}}{\text{s}}", r"\text{m\,s}^{-1}"]):
        pg.eq(L + 40 + i * 110, y, e, 20, C.BLUE)
    pg.note(L + 360, y, "the little ⁻¹ means \"per\";\nChapter 9 explains why", C.RED, 14)
    ch.symbol(r"\text{m\,s}^{-1}", "metres per second", "same as m/s")
    f.p("{b:Changing \"per\" units: one swap at a time.} 8 m/s in km/h (kilometres per hour):",
        14, gap=6)
    step(f, r"8\text{ m per second}", "start", size=18)
    step(f, r"8\times3600=28{,}800\text{ m per hour}", "1 hour = 3600 seconds: 3600 times as far", size=18)
    step(f, r"28{,}800\div1000=28.8\text{ km per hour}", "metres → km: ÷ 1000", size=18, color=C.GREEN)
    ch.check(sp.Rational(8 * 3600, 1000), sp.Rational(288, 10))
    f.p("{b:Density} is mass per volume. A 50 cm³ block weighing 135 g has density "
        "$\\frac{135}{50} = 2.7$ g/cm³ (that's aluminium). Rearranging these formulas "
        "(e.g. time = distance ÷ speed) is the job of Chapter 14.", 14)
    ch.term("density", "mass per unit volume: mass ÷ volume")
    ch.check(sp.Rational(135, 50), sp.Rational(27, 10))


def your_turn(ch):
    f = flow(ch)
    sec(f, "Tape measure: your turn", fresh=True)
    f.p("Answers under each group in grey. Draw the chain or the picture first!", 13.5, gap=10)
    groups = [
        ("Changing units", ["3.2 km in m", "450 mm in m", "2.5 kg in g", "750 ml in litres",
                            "0.004 s in ms"],
         "1. 3200 m   2. 0.45 m   3. 2500 g   4. 0.75 l   5. 4 ms"),
        ("Shapes", ["Perimeter and area of a 9 cm by 6 cm rectangle", "Area of a triangle, base 10 cm, height 7 cm",
                    "Circumference and area of a circle, radius 5 cm (1 d.p.)"],
         "6. 30 cm, 54 cm²   7. 35 cm²   8. 31.4 cm, 78.5 cm²"),
        ("Area and volume units", ["3 m² in cm²", "Volume of a 5 × 4 × 3 cm box", "2 litres in cm³",
                                   "0.5 m³ in cm³"],
         "9. 30,000 cm²   10. 60 cm³   11. 2000 cm³   12. 500,000 cm³"),
        ("Time and per", ["2.4 hours in hours and minutes", "150 km in 2.5 h: speed?", "20 m/s in km/h"],
         "13. 2 h 24 min   14. 60 km/h   15. 72 km/h"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.ORANGE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14)
    ch.check(sp.Rational(32, 10) * 1000, 3200)
    ch.check(sp.Rational(450, 1000), sp.Rational(45, 100))
    ch.check(sp.Rational(4, 1000) * 1000, 4)
    ch.check(2 * (9 + 6), 30)
    ch.check(sp.Rational(1, 2) * 10 * 7, 35)
    ch.check_num(float(2 * sp.pi * 5), 31.4, tol=0.05)
    ch.check_num(float(sp.pi * 25), 78.5, tol=0.05)
    ch.check(sp.Rational(4, 10) * 60, 24)
    ch.check(sp.Rational(150) / sp.Rational(25, 10), 60)
    ch.check(sp.Rational(20 * 3600, 1000), 72)
    ch.check(sp.Rational(1, 2) * 100 ** 3, 500000)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    units(ch)
    prefixes(ch)
    exchange(ch)
    perimeter(ch)
    area(ch)
    area_units(ch)
    volume(ch)
    time(ch)
    per(ch)
    your_turn(ch)
