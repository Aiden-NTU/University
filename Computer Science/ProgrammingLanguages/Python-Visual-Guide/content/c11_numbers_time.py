"""Chapter 11 - Numbers and time: int/float/Decimal/Fraction, float traps, rounding, math and statistics,
random versus secrets, the three clocks, datetime with zoneinfo and DST."""
import math
import statistics
from decimal import Decimal

from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, callout, code, flow, pipe, practice, section, stamp, sub, table,
                         title_block, two_ways)

ORDER = 11
NUM = 11
TITLE = "Numbers and time"
SHORT = "Numbers and time"
SLUG = "Numbers-and-time"
ACCENT = C.ORANGE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


# ----------------------------------------------------------------------------- pictures
def float_line(f):
    """The doubles either side of 0.1, and where the true 1/10 falls between them."""
    y = f.reserve(122)
    pg = f.pg
    ay = y + 52
    pg.line(L + 20, ay, R - 20, ay, C.GREY, 1.2)
    xs = [L + 100, L + W / 2, R - 100]
    vals = [math.nextafter(0.1, 0), 0.1, math.nextafter(0.1, 1)]
    names = ["previous double", "what 0.1 stores", "next double"]
    gap_px = xs[1] - xs[0]
    for x, v, nm in zip(xs, vals, names):
        col = ACCENT if v == 0.1 else C.BLUE
        pg.line(x, ay - 9, x, ay + 9, col, 1.8)
        pg.text(x, y + 22, str(Decimal(v))[:20] + "…", 8.2, col, F.MONO, align="center")
        pg.text(x, ay + 12, nm, 9.5, col, F.BOLD, align="center")
    frac = float((Decimal(0.1) - Decimal(1) / Decimal(10)) / Decimal(math.ulp(0.1)))
    xt = xs[1] - frac * gap_px
    pg.circle(xt, ay, 3.2, C.GREEN, 1, fillcolor=C.GREEN)
    pg.note(xt, ay + 30, "exact 1/10 lives here: no double can hold it", C.GREEN, 13, align="center")
    pg.arrow(xt + 5, ay - 5, xs[1] - 3, ay - 5, C.GREEN, 1.0, head=4)
    pg.text(L + W / 2, y + 2, f"neighbouring doubles near 0.1 are math.ulp(0.1) = {math.ulp(0.1):.3g} apart",
            9.5, C.GREY, align="center")


def floor_picture(f):
    """-7 // 2 and -7 % 2 drawn as hops on a number line."""
    y = f.reserve(112)
    pg = f.pg
    lo, hi = -9, 2

    def x_of(v):
        return L + 40 + (v - lo) * (W - 80) / (hi - lo)

    ay = y + 50
    pg.line(x_of(lo), ay, x_of(hi), ay, C.GREY, 1.1)
    for v in range(lo, hi + 1):
        pg.line(x_of(v), ay - 4, x_of(v), ay + 4, C.GREY, 1)
        pg.text(x_of(v), ay + 7, str(v), 9, C.RED if v == -7 else C.INK, F.MONO, align="center")
    for k in range(4):
        pg.arrow(x_of(-2 * k), ay - 5, x_of(-2 * (k + 1)) + 2, ay - 5, ACCENT, 1.4, bend=-0.45, head=5)
        pg.text(x_of(-2 * k - 1), ay - 30, f"{k + 1}", 9, ACCENT, F.BOLD, align="center")
    pg.note(x_of(1.3), y - 2, "-7 // 2 = -4: hop left in 2s from 0 until you reach or pass -7", ACCENT, 13,
            align="right")
    pg.arrow(x_of(-8), ay + 26, x_of(-7) - 1, ay + 26, C.RED, 1.4, head=5)
    pg.note(x_of(-6.7), ay + 18, "then -7 % 2 = 1: step back right. With a positive divisor, % is never negative",
            C.RED, 13)


def dotplot(f, xs, lo, hi):
    """Marks as stacked dots, with mean, median and one standard deviation either side."""
    y = f.reserve(122)
    pg = f.pg

    def x_of(v):
        return L + 30 + (v - lo) * (W - 60) / (hi - lo)

    ay = y + 74
    pg.line(x_of(lo), ay, x_of(hi), ay, C.GREY, 1.1)
    for v in range(lo, hi + 1, 5):
        pg.line(x_of(v), ay - 3, x_of(v), ay + 3, C.GREY, 1)
        pg.text(x_of(v), ay + 5, str(v), 8.5, C.GREY, align="center")
    seen = {}
    for v in xs:
        k = seen.get(v, 0)
        pg.circle(x_of(v), ay - 7 - k * 11, 4, C.BLUE, 1, fillcolor=C.LIGHT[C.BLUE])
        seen[v] = k + 1
    mean, med, sd = statistics.mean(xs), statistics.median(xs), statistics.stdev(xs)
    pg.line(x_of(mean), y + 16, x_of(mean), ay, C.PURPLE, 1.4, dash=(4, 3))
    pg.line(x_of(med), y + 16, x_of(med), ay, C.GREEN, 1.4, dash=(4, 3))
    pg.text(x_of(mean) - 4, y + 4, f"mean {mean:g}", 9.5, C.PURPLE, F.BOLD, align="right")
    pg.text(x_of(med) + 4, y + 4, f"median {med:g}", 9.5, C.GREEN, F.BOLD)
    by = ay + 24
    pg.line(x_of(mean - sd), by, x_of(mean + sd), by, C.PURPLE, 1.3)
    for v in (mean - sd, mean + sd):
        pg.line(x_of(v), by - 4, x_of(v), by + 4, C.PURPLE, 1.3)
    pg.note(x_of(mean + sd) + 6, by - 9, f"mean ± 1 stdev ({sd:.1f}): the usual spread", C.PURPLE, 13)


def clocks_picture(f):
    """Clock reading against real time: the wall clock can jump, monotonic never goes back."""
    y = f.reserve(160)
    pg = f.pg
    x0, y0, w, hh = L + 70, y + 12, 230, 120
    sx, sy = w / 10, hh / 10

    def P(t, v):
        return x0 + t * sx, y0 + hh - v * sy

    pg.arrow(*P(0, 0), *P(10.7, 0), C.GREY, 1, head=5)
    pg.arrow(*P(0, 0), *P(0, 10.8), C.GREY, 1, head=5)
    pg.text(x0 + w / 2, y0 + hh + 5, "real time passing  →", 9.5, C.GREY, align="center")
    pg.text(x0 - 8, y0 + hh / 2 - 12, "what the\nclock says", 9.5, C.GREY, align="right")
    pg.line(*P(0, 0), *P(10, 9), C.GREEN, 2)
    pg.line(*P(0, 2), *P(6, 8), C.RED, 2)
    pg.line(*P(6, 8), *P(6, 4.5), C.RED, 1.4, dash=(3, 3))
    pg.line(*P(6, 4.5), *P(10, 8.5), C.RED, 2)
    pg.note(P(6, 4.5)[0] + 4, P(6, 4.5)[1] + 2, "NTP sets it back", C.RED, 13)
    nx = x0 + w + 30
    pg.rich(nx, y0 + 8, "{R:time.time()}: the wall clock. Seconds since 1970 UTC. Can jump either way "
            "(NTP sync, a user changing it, a VM resuming).", R - nx, 10.5)
    pg.rich(nx, y0 + 72, "{G:time.monotonic()}, {G:time.perf_counter()}: never go backwards. Their zero "
            "means nothing; only differences do.", R - nx, 10.5)


def dst_picture(f):
    """Europe/London on 29 March 2026: UTC runs smoothly, the local clock skips 01:00-01:59."""
    y = f.reserve(128)
    pg = f.pg
    x0 = L + 70
    k = (W - 100) / 4
    uy, ly = y + 26, y + 88
    pg.text(L, uy - 7, "UTC", 11, C.BLUE, F.BOLD)
    pg.text(L, ly - 7, "London", 11, ACCENT, F.BOLD)
    pg.line(x0, uy, x0 + 3 * k, uy, C.BLUE, 1.3)
    pg.line(x0, ly, x0 + 4 * k, ly, ACCENT, 1.3)
    pg.rect(x0 + k, ly - 5, k, 10, C.RED, 0.8, fillcolor=C.LIGHT[C.RED])
    for i in range(7):
        t = i * 0.5
        lt = t if t < 1 else t + 1
        xu, xl = x0 + t * k, x0 + lt * k
        pg.line(xu, uy, xl, ly, C.GREY, 0.8, dash=(2, 2))
        pg.dot(xu, uy, 2.4, C.BLUE)
        pg.dot(xl, ly, 2.4, ACCENT)
        pg.text(xu, uy - 15, f"{int(t):02d}:{int(t % 1 * 60):02d}", 8.5, C.BLUE, F.MONO, align="center")
        pg.text(xl, ly + 6, f"{int(lt):02d}:{int(lt % 1 * 60):02d}", 8.5, ACCENT, F.MONO, align="center")
    pg.note(x0 + 1.5 * k, ly + 20, "01:00-01:59 never happens in London", C.RED, 13, align="center")
    pg.note(R, ly + 20, "clocks jump at 01:00 UTC", C.GREY, 13, align="right")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 11, TITLE, "count exactly, measure approximately, keep time carefully", ACCENT)
    f = ch.flow(top=190)
    f.p("Python has five kinds of number. Picking the wrong one gives answers that are {B:almost} right, "
        "which is worse than an error because nothing tells you:", 14, gap=10)
    table(f, ["type", "exact?", "size", "use it for"], [
        ["`int`", "{G:yes}", "unlimited: grows as needed", "counting, indexes, ids, money stored as pence"],
        ["`float`", "{R:no}: nearest binary fraction", "64 bits, about 15-17 significant digits",
         "measurements, science, graphics"],
        ["`Decimal`", "{G:yes} for base-10 digits", "you choose the precision",
         "money, anything a person types in decimal"],
        ["`Fraction`", "{G:yes}", "unlimited", "exact ratios, probability, maths"],
        ["`complex`", "as two floats", "two 64-bit floats", "signals, geometry, `(-1) ** 0.5`"],
    ], widths=[1.1, 1.8, 2.0, 2.7], size=10.5)
    code(f, """
        from decimal import Decimal
        from fractions import Fraction

        print(2 ** 100)                                # ints never overflow
        print(0.1 + 0.2, 0.1 + 0.2 == 0.3)             # floats are approximations
        print(Decimal("0.1") + Decimal("0.2"), Fraction(1, 3) + Fraction(1, 6))
        print(7 / 2, 7 // 2, type(2 ** 0.5).__name__, (-1) ** 0.5)
    """, notes={5: "the famous one: next page explains it"})
    f.p("Time is worse. Clocks get corrected, countries move their clocks twice a year, and \"3 pm\" means "
        "nothing without a place. The second half of the chapter gives you the three rules that avoid "
        "nearly every time bug.", 13.5, gap=8)


def float_section(ch):
    f = flow(ch)
    sec(f, "Why 0.1 + 0.2 isn't 0.3", room=420)
    f.p("A float stores `sign × 1.fraction × 2^exponent` with 52 bits of fraction. Only numbers that are "
        "sums of powers of two fit exactly. One tenth in binary is `0.000110011001100…` forever, just "
        "as 1/3 is `0.333…` in decimal, so Python stores the {B:nearest} double instead:", 13.5, gap=8)
    float_line(f)
    code(f, """
        import math
        from decimal import Decimal

        print(Decimal(0.1))                       # the exact value actually stored
        print((0.1).as_integer_ratio())           # = that value as a fraction over 2**55
        print(0.1 + 0.2)                          # two rounding errors, then a third
        print(math.isclose(0.1 + 0.2, 0.3), abs((0.1 + 0.2) - 0.3) < 1e-9)
        print(sum([0.1] * 10), math.fsum([0.1] * 10))
        print(math.ulp(1.0), math.ulp(1e16), 1e16 + 1 == 1e16)
    """, notes={7: "compare with a tolerance", 8: "fsum tracks the lost bits", 9: "big floats have big gaps"})
    table(f, ["trap", "what happens", "do this instead"], [
        ["`a == b` on results", "tiny differences make equal values unequal", "`math.isclose(a, b)`"],
        ["adding many floats", "errors pile up", "`math.fsum`, or Decimal / int pence"],
        ["huge + tiny", "the tiny one vanishes (`1e16 + 1`)", "rescale, or sort small-first"],
        ["`float(\"nan\")`", "`nan != nan`, and it spreads through maths", "`math.isnan(x)`"],
        ["money in floats", "`0.1 + 0.2` pence errors in totals", "`Decimal(\"0.10\")` or int pence"],
    ], widths=[1.5, 2.6, 2.2], size=10.5)
    callout(f, "other", "This is IEEE 754, built into the CPU. C `double`, Java `double`, JavaScript `Number` "
            "(its {B:only} number type), Rust `f64` all print `0.30000000000000004`. It is not a Python bug.")


def int_section(ch):
    f = flow(ch)
    sec(f, "Integers, division and rounding", room=420)
    f.p("Python ints grow as large as memory allows, so there is no overflow. `/` always gives a float; `//` "
        "gives the {B:floor} (rounds towards minus infinity), and `%` is whatever is left over:", 13.5, gap=10)
    floor_picture(f)
    code(f, """
        import math

        print(2 ** 200 % 1000, (2 ** 200).bit_length())
        print(7 // 2, -7 // 2, 7 % 3, -7 % 3, divmod(-7, 2))
        print(int(-3.7), math.floor(-3.7), math.trunc(-3.7), math.ceil(-3.7))
        print(round(2.5), round(3.5), round(0.125, 2), round(2.675, 2))
        print(pow(3, 200, 1000), math.gcd(12, 18), math.lcm(4, 6), math.isqrt(99))
        print(math.comb(5, 2), math.perm(5, 2), math.factorial(20))
    """, notes={4: "floor: -3.5 becomes -4", 6: "half to even; 2.675 is really 2.67499…",
                7: "modular power: fast, no huge number"})
    callout(f, "why", "Flooring keeps `a == (a // b) * b + a % b` true {B:and} keeps `%` the same sign as the "
            "divisor, so `(i - 1) % n` wraps round a list cleanly. C, Java and JavaScript truncate towards "
            "zero instead: `-7 / 2` is `-3` and `-7 % 2` is `-1` there. Port maths code carefully.")
    table(f, ["you want", "use", "2.5 →", "-2.5 →"], [
        ["round to nearest, ties to even (less bias)", "`round(x)`", "2", "-2"],
        ["round half up (school rounding)", "`Decimal.quantize(..., ROUND_HALF_UP)`", "3", "-3"],
        ["always down / always up", "`math.floor` / `math.ceil`", "2 / 3", "-3 / -2"],
        ["chop the fraction off", "`int(x)` or `math.trunc(x)`", "2", "-2"],
    ], widths=[2.6, 2.9, 0.8, 0.9], size=10.5)


def decimal_section(ch):
    f = flow(ch)
    sec(f, "decimal and fractions: exact arithmetic", room=420)
    f.p("`Decimal` does arithmetic in base 10, the way you do it on paper, so `0.10` stays exactly `0.10`. "
        "It's slower than float, and that never matters for money:", 13.5, gap=8)
    two_ways(f, ("float", """
        prices = [0.10] * 3
        total = sum(prices)
        print(total, total == 0.30)
        print(f"{total:.2f}")
    """), ("Decimal", """
        from decimal import Decimal
        prices = [Decimal("0.10")] * 3
        total = sum(prices)
        print(total, total == Decimal("0.30"))
    """), same_output=False, verdict=[("exact", 1, 5), ("speed", 5, 2)])
    code(f, """
        from decimal import Decimal, ROUND_HALF_UP, localcontext

        print(Decimal(0.1) == Decimal("0.1"))         # made from a float: inherits its error
        price = Decimal("19.99")
        vat = (price * Decimal("0.20")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        print(vat, price + vat)
        print(Decimal("2.675").quantize(Decimal("0.01")), Decimal(1) / Decimal(7))
        with localcontext() as ctx:
            ctx.prec = 50                             # digits of precision, for this block only
            print(Decimal(1) / Decimal(7))
    """, notes={3: "always build from strings", 5: "quantize = round to these places"})
    sub(f, "Fraction: exact ratios", ACCENT, room=200)
    code(f, """
        import math
        from fractions import Fraction

        x = Fraction(1, 3) + Fraction(1, 6)
        print(x, x.numerator, x.denominator, float(x))
        print(Fraction("0.75"), Fraction(0.1) == Fraction(1, 10))
        print(Fraction(math.pi).limit_denominator(1000))
        print(sum(Fraction(1, n) for n in range(1, 11)))
    """, notes={7: "best fraction with a small denominator", 8: "1 + 1/2 + ... + 1/10, exactly"})
    callout(f, "rule", "Money: `Decimal` built from strings, or whole pence in an `int`. Measurements: `float` "
            "and compare with `math.isclose`. Exact ratios: `Fraction`. Never `Decimal(some_float)`: the "
            "error is already inside the float.")


def stats_section(ch):
    f = flow(ch)
    sec(f, "math and statistics", room=420)
    marks = [62, 71, 71, 58, 90, 45, 71, 66]
    f.p("`statistics` covers what a first statistics module teaches, with careful numerics. Here are eight "
        "exam marks drawn as dots:", 13.5, gap=6)
    dotplot(f, marks, 40, 95)
    code(f, """
        import statistics as st

        marks = [62, 71, 71, 58, 90, 45, 71, 66]
        print(st.mean(marks), st.median(marks), st.mode(marks))
        print(round(st.stdev(marks), 2), round(st.pstdev(marks), 2))
        print(st.quantiles(marks, n=4))                   # the three quartile cut points

        hours, score = [2, 4, 5, 7, 9], [50, 62, 65, 74, 88]
        fit = st.linear_regression(hours, score)
        print(round(st.correlation(hours, score), 3), round(fit.slope, 2), round(fit.intercept, 2))
    """, notes={5: "sample (n-1) vs population (n)"})
    callout(f, "why", "`stdev` divides by n − 1 because your data is a {B:sample}: its own mean sits closer to "
            "its points than the true mean would, so dividing by n underestimates the spread. Use `pstdev` "
            "only when you have the whole population (every student, not some).")
    table(f, ["math has...", "for"], [
        ["`sqrt`, `isqrt`, `cbrt`, `exp`, `log`, `log2`, `log10`", "roots and logs (`log(x, base)` too)"],
        ["`sin`, `cos`, `atan2`, `radians`, `degrees`", "trigonometry, in radians"],
        ["`hypot`, `dist`, `prod`, `sumprod`", "lengths, distances, products"],
        ["`pi`, `tau`, `e`, `inf`, `nan`", "constants"],
        ["`isclose`, `isfinite`, `isnan`, `nextafter`, `ulp`", "float housekeeping"],
    ], widths=[3.4, 2.6], size=10.5)


def random_section(ch):
    f = flow(ch)
    sec(f, "random versus secrets", room=420)
    f.p("`random` is a {B:pseudo}-random generator: a deterministic formula (the Mersenne Twister) that "
        "turns a seed into a long sequence that only looks random. Same seed, same sequence:", 13.5, gap=8)
    pipe(f, ["seed\n42", "state\n624 numbers", "0.639…, 0.025…, 0.275…"], color=ACCENT,
         labels=["sets", "each call steps it"], under=["", "", "replays identically from the same seed"])
    code(f, """
        import random

        rng = random.Random(42)                       # your own generator, reproducible
        print(rng.randint(1, 6), rng.choice("ABC"), round(rng.random(), 3))
        again = random.Random(42)
        print(again.randint(1, 6), again.choice("ABC"), round(again.random(), 3))
        deck = list(range(10))
        rng.shuffle(deck)
        print(deck)
        print(rng.sample(range(100), 3), rng.choices("HT", weights=[9, 1], k=8))
        print(round(rng.gauss(0, 1), 3), round(rng.uniform(1.5, 2.5), 3))
    """, notes={6: "identical: same seed", 10: "sample: no repeats; choices: repeats, weighted"})
    callout(f, "trap", "Watch 624 outputs of `random` and you can rebuild its state and predict every later "
            "number. Fine for games, simulations and tests; useless against an attacker. Tokens, passwords, "
            "keys and anything with money riding on it use `secrets` (Ch 13), which reads the OS's "
            "cryptographic generator.")
    table(f, ["you need", "use"], [
        ["a simulation, test data or game you can replay", "`random.Random(seed)` (pass the rng in)"],
        ["shuffle quiz questions", "`random.shuffle`"],
        ["a password-reset token or session id", "`secrets.token_urlsafe(32)`"],
        ["pick the winner of a paid draw", "`secrets.choice(entries)`"],
        ["millions of random numbers for NumPy", "`np.random.default_rng(seed)` (Ch 18)"],
    ], widths=[3.2, 2.8], size=10.5)
    callout(f, "rule", "Pass a `random.Random` object into code that needs randomness instead of calling the "
            "global `random.randint`. Tests can then give it a fixed seed, or a fake, and get the same result "
            "every run. Practice 11.6 makes you do exactly this.")


def clocks_section(ch):
    f = flow(ch)
    sec(f, "Three clocks, three jobs", room=280)
    f.p("A computer has more than one clock. Using the wrong one is how a 30-second timeout fires instantly, "
        "or a benchmark reports negative time:", 13.5, gap=8)
    clocks_picture(f)
    table(f, ["call", "use it for", "can jump?"], [
        ["`time.time()`", "timestamps you store: when did this happen?", "{R:yes}"],
        ["`time.monotonic()`", "timeouts, deadlines, retry back-off", "{G:never back}"],
        ["`time.perf_counter()`", "measuring how long code takes (finest resolution)", "{G:never back}"],
        ["`time.process_time()`", "CPU time used by this process (ignores sleeping)", "{G:never back}"],
        ["`time.sleep(s)`", "pause the thread for at least s seconds", ""],
    ], widths=[1.9, 3.5, 1.1], size=10.5)
    code(f, """
        import time

        print(time.get_clock_info("time").adjustable, time.get_clock_info("monotonic").adjustable)

        deadline = time.monotonic() + 0.05            # 50 ms from now, immune to clock changes
        polls = 0
        while time.monotonic() < deadline:
            polls += 1
            time.sleep(0.01)
        print(polls >= 3)
    """, notes={3: "True: can be set; False: can't", 5: "the deadline pattern"})


def datetime_section(ch):
    f = flow(ch)
    sec(f, "datetime: naive, aware, and the time zone", room=420)
    f.p("A `datetime` with no `tzinfo` is {B:naive}: \"14:30 on 28 Sept\", but where? One with a zone from "
        "`zoneinfo` is {B:aware}: a single instant everyone agrees on. Only aware times can be converted "
        "or compared across places:", 13.5, gap=8)
    code(f, """
        from datetime import date, datetime, timedelta, timezone
        from zoneinfo import ZoneInfo

        naive = datetime(2026, 9, 28, 14, 30)
        aware = datetime(2026, 9, 28, 14, 30, tzinfo=ZoneInfo("Europe/London"))
        print(naive.tzinfo, aware.utcoffset(), aware.tzname())
        print(aware.astimezone(timezone.utc))
        print(aware.astimezone(ZoneInfo("Asia/Tokyo")).isoformat())
        print(date(2026, 12, 25) - date(2026, 9, 28), date(2026, 9, 28).strftime("%A %d %B"))
        print(datetime.fromisoformat("2026-09-28T14:30:00+01:00") == aware)
    """, notes={7: "same instant, other zone", 10: "ISO 8601: the format to store and send"})
    code(f, """
        print(naive < aware)
    """, raises=TypeError)
    sub(f, "Clock changes: the gap and the fold", ACCENT, room=170)
    dst_picture(f)
    code(f, """
        london = ZoneInfo("Europe/London")
        before = datetime(2026, 3, 28, 12, 0, tzinfo=london)
        after = before + timedelta(days=1)            # wall-clock arithmetic within one zone
        print(after, after - before)
        print(after.astimezone(timezone.utc) - before.astimezone(timezone.utc))
        gap = datetime(2026, 3, 29, 1, 30, tzinfo=london)     # never happened
        print(gap.astimezone(timezone.utc).astimezone(london))
        twice = datetime(2026, 10, 25, 1, 30, tzinfo=london)  # happened twice
        print(twice.utcoffset(), twice.replace(fold=1).utcoffset())
    """, notes={4: "says 1 day...", 5: "...but only 23 hours passed", 7: "shifted out of the gap",
                9: "fold picks which 01:30"})
    callout(f, "rule", "1. Store and compute in {B:UTC}, as aware datetimes: `datetime.now(timezone.utc)` "
            "(never `utcnow()`, which is deprecated and naive). 2. Convert to local time only to show a "
            "person. 3. Send and store times as ISO 8601 strings with the offset. Repeating events (\"every "
            "Monday at 9 local\") are the one case where you compute in local time, then convert (practice 11.4).")


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 11)
    stamp(f, [
        (2, "Numbers: `int` is unlimited; `float` is an IEEE 754 double (inexact); `Decimal` and `Fraction` "
            "are exact library types. `/` gives float, `//` floors. Booleans are ints (`True + True == 2`)."),
        (11, "`math`, `statistics`, `random` (reproducible, not secure), `secrets`, `decimal`, `fractions`, "
             "`time` (three clocks), `datetime` + `zoneinfo`."),
    ])
    callout(f, "other", "C and Java ints have fixed sizes and overflow (silently in C, wrapping in Java); Rust "
            "panics on overflow in debug builds. Java has `BigDecimal`, C# `decimal`, JavaScript `BigInt`. Every "
            "language has the same naive/aware time split: Java `LocalDateTime` vs `ZonedDateTime`, JS "
            "`Temporal.PlainDateTime` vs `Temporal.ZonedDateTime`.")
    callout(f, "deep", "Vault notes: {b:5.9} Numeric objects · {b:16.3} Descriptive location and dispersion · "
            "{b:16.11} Reductions, axes, and numerical stability · {b:16.12} Randomness, generators, and "
            "reproducibility · {b:16.21} Time data, ordering, and time zones · {b:19.22} Cryptographic "
            "randomness.")


def build(ch):
    title_page(ch)
    float_section(ch)
    int_section(ch)
    decimal_section(ch)
    stats_section(ch)
    random_section(ch)
    clocks_section(ch)
    datetime_section(ch)
    finish(ch)
