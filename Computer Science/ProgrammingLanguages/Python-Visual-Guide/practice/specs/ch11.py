EXERCISES = [
    dict(
        id="11.1", kind="build", title="Split a bill to the penny",
        task="""
        Write `split_bill(total, people)` where `total` is a string like `"10.00"`. Return a list of
        `people` `Decimal` amounts, each with exactly two decimal places, that **add up exactly** to the
        total and differ from each other by at most `0.01`. Larger shares come first. Raise `ValueError`
        if `people < 1`.
        """,
        stub='''
        def split_bill(total, people):
            share = round(float(total) / people, 2)
            return [share] * people
        ''',
        tests='''
        import random
        from decimal import Decimal

        def test_example(m):
            equal(m.split_bill("10.00", 3), [Decimal("3.34"), Decimal("3.33"), Decimal("3.33")], "10.00 / 3")
            equal(m.split_bill("0.05", 4), [Decimal("0.02"), Decimal("0.01"), Decimal("0.01"), Decimal("0.01")], "0.05 / 4")
            raises(ValueError, m.split_bill, "5.00", 0)

        def test_random(m):
            rng = random.Random(11)
            for _ in range(300):
                total = Decimal(rng.randint(0, 100_000)) / 100
                n = rng.randint(1, 13)
                parts = m.split_bill(f"{total:.2f}", n)
                equal(len(parts), n, "number of shares")
                check(all(isinstance(p, Decimal) for p in parts), "every share must be a Decimal")
                check(all(p.as_tuple().exponent == -2 for p in parts), f"two decimal places each: {parts}")
                equal(sum(parts), total, f"shares of {total} must add up")
                check(max(parts) - min(parts) <= Decimal("0.01"), f"shares differ by more than 0.01: {parts}")
                equal(parts, sorted(parts, reverse=True), "larger shares first")
        ''',
        alts={
            "whole pence with divmod": ('''
                from decimal import Decimal

                def split_bill(total, people):
                    if people < 1:
                        raise ValueError("need at least one person")
                    pence = int(Decimal(total) * 100)
                    q, r = divmod(pence, people)
                    return [(Decimal(q + (i < r)) / 100).quantize(Decimal("0.01")) for i in range(people)]
            ''', "Convert to whole pence, divide with remainder, and give the r leftover pennies to the first r "
                 "people. Integers can't drift, so the sum is right by construction."),
            "Decimal rounding down": ('''
                from decimal import Decimal, ROUND_DOWN

                def split_bill(total, people):
                    if people < 1:
                        raise ValueError("need at least one person")
                    total = Decimal(total)
                    cent = Decimal("0.01")
                    base = (total / people).quantize(cent, rounding=ROUND_DOWN)
                    extra = int((total - base * people) / cent)
                    return [base + cent if i < extra else base for i in range(people)]
            ''', "Round every share down, then hand out the leftover cents. Same idea in Decimal; the pence "
                 "version is what payment systems usually store."),
        },
    ),
    dict(
        id="11.2", kind="fix", title="A float range that doesn't drift",
        task="""
        `frange(start, stop, step)` should yield `start, start + step, start + 2*step, ...` for every value
        **below** `stop`, like `range` for floats. The stub keeps adding `step`, so errors pile up:
        `list(frange(0, 1, 0.1))` gives 11 values, the last `0.9999999999999999`. Fix it so the count is
        right and the i-th value is (within 1e-9) `start + i * step`. A value within `1e-9 * step` of `stop`
        counts as equal to `stop` and is excluded. Raise `ValueError` if `step <= 0`.
        """,
        stub='''
        def frange(start, stop, step):
            x = start
            while x < stop:
                yield x
                x += step
        ''',
        tests='''
        import math, random

        def close_all(got, want, what):
            equal(len(got), len(want), f"{what}: number of values")
            for i, (g, w) in enumerate(zip(got, want)):
                check(math.isclose(g, w, rel_tol=0, abs_tol=1e-9), f"{what}: value {i} is {g!r}, want {w!r}")

        def test_examples(m):
            close_all(list(m.frange(0, 1, 0.1)), [i / 10 for i in range(10)], "frange(0, 1, 0.1)")
            close_all(list(m.frange(0, 0.3, 0.1)), [0, 0.1, 0.2], "frange(0, 0.3, 0.1)")
            close_all(list(m.frange(1, 2, 0.25)), [1, 1.25, 1.5, 1.75], "frange(1, 2, 0.25)")
            close_all(list(m.frange(0, 0.25, 0.1)), [0, 0.1, 0.2], "frange(0, 0.25, 0.1)")
            equal(list(m.frange(3, 1, 0.5)), [], "stop below start")
            raises(ValueError, lambda: list(m.frange(0, 1, 0)))

        def test_long(m):
            got = list(m.frange(0, 1000, 0.1))
            close_all(got, [i * 0.1 for i in range(10_000)], "frange(0, 1000, 0.1)")

        def test_random(m):
            rng = random.Random(12)
            for _ in range(300):
                start, n = rng.randint(-5, 5), rng.randint(0, 60)
                step = rng.choice([0.1, 0.2, 0.25, 0.3, 0.7, 1.1])
                stop = start + n * step
                close_all(list(m.frange(start, stop, step)), [start + i * step for i in range(n)],
                          f"frange({start}, {stop}, {step})")
        ''',
        alts={
            "count first, then multiply": ('''
                import math

                def frange(start, stop, step):
                    if step <= 0:
                        raise ValueError("step must be positive")
                    n = max(0, math.ceil((stop - start) / step - 1e-9))
                    for i in range(n):
                        yield start + i * step
            ''', "Each value is computed fresh from i, so there's one rounding per value instead of i of them. "
                 "This is how numpy.linspace works; numpy.arange has the stub's counting trap."),
            "exact counting with Fraction": ('''
                from fractions import Fraction

                def frange(start, stop, step):
                    if step <= 0:
                        raise ValueError("step must be positive")
                    a, b, s = (Fraction(str(v)) for v in (start, stop, step))
                    i = 0
                    while a + i * s < b - s / 10**9:
                        yield float(a + i * s)
                        i += 1
            ''', "Fraction(str(0.1)) is exactly 1/10, so the loop condition is exact. Slower, but it treats the "
                 "inputs as the decimals the caller meant."),
        },
    ),
    dict(
        id="11.3", kind="fix", title="Running mean and variance that stay accurate",
        task="""
        `RunningStats` takes numbers one at a time with `add(x)` and reports `count`, `mean`, `variance`
        (sample, n − 1; `0.0` with fewer than two values) and `stdev`, using O(1) memory: don't keep
        the values. The stub uses the textbook formula `(Σx² − (Σx)²/n) / (n − 1)`, which is correct on
        paper but cancels catastrophically in floats: for `1e9 + [4, 7, 13, 16]` it's wildly off (the answer is
        30). Fix it, without the `statistics` module. Look up **Welford's algorithm**, or think about subtracting
        a shift first.
        """,
        stub='''
        import math

        class RunningStats:
            def __init__(self):
                self.count = 0
                self._sum = 0.0
                self._sumsq = 0.0

            def add(self, x):
                self.count += 1
                self._sum += x
                self._sumsq += x * x

            @property
            def mean(self):
                return self._sum / self.count if self.count else 0.0

            @property
            def variance(self):
                n = self.count
                if n < 2:
                    return 0.0
                return (self._sumsq - self._sum ** 2 / n) / (n - 1)

            @property
            def stdev(self):
                return math.sqrt(self.variance)
        ''',
        tests='''
        import math, random, statistics

        def feed(m, xs):
            r = m.RunningStats()
            for x in xs:
                r.add(x)
            return r

        def test_small(m):
            r = feed(m, [])
            equal((r.count, r.variance), (0, 0.0), "empty")
            r = feed(m, [5.0])
            equal((r.count, r.mean, r.variance), (1, 5.0, 0.0), "one value")
            r = feed(m, [2, 4, 4, 4, 5, 5, 7, 9])
            check(math.isclose(r.mean, 5.0) and math.isclose(r.variance, 32 / 7), "mean 5, variance 32/7")
            check(math.isclose(r.stdev, math.sqrt(32 / 7)), "stdev is sqrt(variance)")

        def test_offset(m):
            r = feed(m, [1e9 + v for v in (4, 7, 13, 16)])
            check(abs(r.variance - 30) < 1e-6, f"1e9 + [4, 7, 13, 16]: variance should be 30, got {r.variance}")
            xs = [1e8 + v / 10 for v in range(100)]
            r = feed(m, xs)
            want = statistics.variance(xs)
            check(math.isclose(r.variance, want, rel_tol=1e-6), f"large offset: want {want}, got {r.variance}")

        def test_random(m):
            rng = random.Random(13)
            for _ in range(100):
                xs = [rng.uniform(-1000, 1000) for _ in range(rng.randint(2, 200))]
                r = feed(m, xs)
                check(math.isclose(r.mean, statistics.fmean(xs), rel_tol=1e-9, abs_tol=1e-9), "mean")
                check(math.isclose(r.variance, statistics.variance(xs), rel_tol=1e-9), "variance")

        def test_no_statistics(m):
            check("statistics" not in imports(m), "compute it yourself: don't import statistics")
        ''',
        alts={
            "Welford": ('''
                import math

                class RunningStats:
                    def __init__(self):
                        self.count, self.mean, self._m2 = 0, 0.0, 0.0

                    def add(self, x):
                        self.count += 1
                        delta = x - self.mean
                        self.mean += delta / self.count
                        self._m2 += delta * (x - self.mean)

                    @property
                    def variance(self):
                        return self._m2 / (self.count - 1) if self.count > 1 else 0.0

                    @property
                    def stdev(self):
                        return math.sqrt(self.variance)
            ''', "Welford keeps the running mean and the sum of squared distances from it. Every quantity stays "
                 "the size of the spread, never the size of x², so nothing cancels."),
            "shifted sums": ('''
                import math

                class RunningStats:
                    def __init__(self):
                        self.count, self._k, self._s, self._ss = 0, None, 0.0, 0.0

                    def add(self, x):
                        if self._k is None:
                            self._k = x                     # shift by the first value seen
                        d = x - self._k
                        self.count += 1
                        self._s += d
                        self._ss += d * d

                    @property
                    def mean(self):
                        return self._k + self._s / self.count if self.count else 0.0

                    @property
                    def variance(self):
                        n = self.count
                        return (self._ss - self._s ** 2 / n) / (n - 1) if n > 1 else 0.0

                    @property
                    def stdev(self):
                        return math.sqrt(self.variance)
            ''', "Variance doesn't change if you subtract a constant from every value. Shifting by any typical "
                 "value (the first) keeps the sums small. Simple, and good unless the data drifts far from it."),
        },
    ),
    dict(
        id="11.4", kind="fix", title="A weekly meeting across clock changes",
        task="""
        `meeting_times(first_local, tz_name, weeks)` gets the first meeting as a **naive** local datetime
        in zone `tz_name` (for example `"Europe/London"`). Return `weeks` aware UTC datetimes, one a week,
        always at the **same local wall-clock time**. The stub adds 7 days in UTC, so after the clocks change
        the meeting starts an hour early or late. Fix it. You may assume no meeting falls in a DST gap.
        """,
        stub='''
        from datetime import timedelta, timezone
        from zoneinfo import ZoneInfo

        def meeting_times(first_local, tz_name, weeks):
            first = first_local.replace(tzinfo=ZoneInfo(tz_name)).astimezone(timezone.utc)
            return [first + timedelta(weeks=i) for i in range(weeks)]
        ''',
        tests='''
        import random
        from datetime import datetime, timedelta, timezone
        from zoneinfo import ZoneInfo

        def test_london_autumn(m):
            got = m.meeting_times(datetime(2026, 10, 19, 9, 0), "Europe/London", 3)
            want = [datetime(2026, 10, 19, 8, 0, tzinfo=timezone.utc), datetime(2026, 10, 26, 9, 0, tzinfo=timezone.utc),
                    datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)]
            equal(got, want, "London, across the October change")
            check(all(t.utcoffset() == timedelta(0) for t in got), "results must be aware UTC datetimes")

        def test_random(m):
            rng = random.Random(14)
            zones = ["Europe/London", "America/New_York", "Australia/Sydney", "Asia/Kolkata", "Europe/Berlin"]
            for _ in range(60):
                tz = rng.choice(zones)
                first = datetime(2026, rng.randint(1, 12), rng.randint(1, 28), rng.choice([8, 12, 17]), rng.choice([0, 30]))
                n = rng.randint(1, 30)
                got = m.meeting_times(first, tz, n)
                equal(len(got), n, "number of meetings")
                for i, t in enumerate(got):
                    check(t.utcoffset() == timedelta(0), "each result must be in UTC")
                    local = t.astimezone(ZoneInfo(tz)).replace(tzinfo=None)
                    equal(local, first + timedelta(weeks=i), f"{tz} meeting {i} in local time")
        ''',
        alts={
            "add in local time, then convert": ('''
                from datetime import timedelta, timezone
                from zoneinfo import ZoneInfo

                def meeting_times(first_local, tz_name, weeks):
                    tz = ZoneInfo(tz_name)
                    return [(first_local + timedelta(weeks=i)).replace(tzinfo=tz).astimezone(timezone.utc)
                            for i in range(weeks)]
            ''', "Do the 'same time next week' arithmetic on the wall clock, attach the zone, and only then "
                 "convert. Each week gets the offset that applies on that date."),
            "aware arithmetic in the zone": ('''
                from datetime import timedelta, timezone
                from zoneinfo import ZoneInfo

                def meeting_times(first_local, tz_name, weeks):
                    first = first_local.replace(tzinfo=ZoneInfo(tz_name))
                    return [(first + timedelta(weeks=i)).astimezone(timezone.utc) for i in range(weeks)]
            ''', "Adding a timedelta to an aware datetime keeps the same tzinfo and does wall-clock arithmetic "
                 "(Ch 11's 'says 1 day, only 23 hours passed'). Here that's exactly what you want."),
        },
    ),
    dict(
        id="11.5", kind="explore", title="Calendar questions with an unseen module",
        task="""
        Use the `calendar` module (Ch 7 method: `help(calendar)`, `dir`, try things) to write
        `last_weekday(year, month, weekday)`, the `date` of the last given weekday in that month
        (`0` = Monday ... `6` = Sunday), and `working_days(year, month)`, the number of Monday-to-Friday days
        in the month. Useful: `calendar.monthrange`, `calendar.monthcalendar`, `calendar.Calendar`.
        """,
        stub='''
        import calendar
        from datetime import date

        def last_weekday(year, month, weekday):
            ...

        def working_days(year, month):
            ...
        ''',
        tests='''
        from datetime import date, timedelta

        def brute_days(year, month):
            d = date(year, month, 1)
            while d.month == month:
                yield d
                d += timedelta(days=1)

        def test_examples(m):
            equal(m.last_weekday(2026, 5, 0), date(2026, 5, 25), "last Monday of May 2026 (a bank holiday)")
            equal(m.last_weekday(2026, 2, 6), date(2026, 2, 22), "last Sunday of Feb 2026")
            equal(m.working_days(2026, 9), 22, "working days in Sept 2026")

        def test_all_months(m):
            for year in (2023, 2024, 2026, 2100):
                for month in range(1, 13):
                    days = list(brute_days(year, month))
                    equal(m.working_days(year, month), sum(d.weekday() < 5 for d in days), f"{year}-{month} working days")
                    for wd in range(7):
                        want = max(d for d in days if d.weekday() == wd)
                        equal(m.last_weekday(year, month, wd), want, f"{year}-{month} last weekday {wd}")
        ''',
        alts={
            "monthcalendar grid": ('''
                import calendar
                from datetime import date

                def last_weekday(year, month, weekday):
                    weeks = calendar.monthcalendar(year, month)       # rows Mon..Sun, 0 = not this month
                    day = max(week[weekday] for week in weeks)
                    return date(year, month, day)

                def working_days(year, month):
                    return sum(1 for week in calendar.monthcalendar(year, month) for d in week[:5] if d)
            ''', "monthcalendar returns the month as printed on a wall calendar. Once you've seen its shape in "
                 "the REPL, both questions are one line."),
            "monthrange arithmetic": ('''
                import calendar
                from datetime import date

                def last_weekday(year, month, weekday):
                    _, ndays = calendar.monthrange(year, month)
                    last = date(year, month, ndays)
                    return date(year, month, ndays - (last.weekday() - weekday) % 7)

                def working_days(year, month):
                    first, ndays = calendar.monthrange(year, month)
                    return sum((first + i) % 7 < 5 for i in range(ndays))
            ''', "monthrange gives (weekday of the 1st, number of days). From there it's modular arithmetic. "
                 "Note % 7 on a possibly negative number: Python's floor-mod keeps it in 0..6."),
        },
    ),
    dict(
        id="11.6", kind="project", title="A seeded dice roller",
        task="""
        Mini-project. Write `roll(expr, rng)` for dice expressions like `"3d6"`, `"d20"`, `"2d8+3"`,
        `"4d6-1"`: N dice (default 1, max 100) with S sides (2 to 1000), plus or minus a whole number.
        Use `rng.randint(1, S)` once per die, in order. Return `(total, rolls)`. Surrounding spaces are fine;
        anything else malformed raises `ValueError`.

        Then `estimate(expr, trials, seed)` returns the mean total over `trials` rolls using
        `random.Random(seed)`, so the same seed always gives the same answer.
        """,
        stub='''
        def roll(expr, rng):
            n, s = expr.split("d")
            rolls = [rng.randint(1, int(s)) for _ in range(int(n))]
            return sum(rolls), rolls
        ''',
        tests='''
        import random

        class Highest:
            def randint(self, a, b):
                return b

        class Counting:
            def __init__(self):
                self.n = 0
            def randint(self, a, b):
                self.n += 1
                return a

        def test_parse(m):
            equal(m.roll("3d6+2", Highest()), (20, [6, 6, 6]), "3d6+2 with every die at maximum")
            equal(m.roll(" d20 ", Highest()), (20, [20]), "d20 means 1d20")
            equal(m.roll("4d6-1", Counting()), (3, [1, 1, 1, 1]), "4d6-1 with every die at 1")
            c = Counting()
            m.roll("100d1000", c)
            equal(c.n, 100, "one randint call per die")
            for bad in ["", "d", "3d", "0d6", "101d6", "3d1", "3d1001", "3x6", "3d6+", "3d6+2+1", "-3d6", "3d6.5"]:
                raises(ValueError, m.roll, bad, Highest())

        def test_ranges(m):
            rng = random.Random(15)
            for _ in range(500):
                n, s, k = rng.randint(1, 10), rng.randint(2, 30), rng.randint(-5, 5)
                expr = f"{n}d{s}{k:+d}" if k else f"{n}d{s}"
                total, rolls = m.roll(expr, rng)
                equal(len(rolls), n, f"{expr}: number of rolls")
                check(all(1 <= r <= s for r in rolls), f"{expr}: each roll in 1..{s}")
                equal(total, sum(rolls) + k, f"{expr}: total")

        def test_estimate(m):
            a = m.estimate("3d6", 20_000, 1)
            equal(a, m.estimate("3d6", 20_000, 1), "same seed, same estimate")
            check(abs(a - 10.5) < 0.1, f"3d6 averages 10.5, got {a}")
            check(abs(m.estimate("2d8+3", 20_000, 2) - 12.0) < 0.12, "2d8+3 averages 12")
        ''',
        alts={
            "regex + statistics": ('''
                import random, re, statistics

                DICE = re.compile(r"(\\d*)d(\\d+)([+-]\\d+)?")

                def roll(expr, rng):
                    mt = DICE.fullmatch(expr.strip())
                    if not mt:
                        raise ValueError(f"not a dice expression: {expr!r}")
                    n = int(mt[1] or 1)
                    sides = int(mt[2])
                    if not (1 <= n <= 100 and 2 <= sides <= 1000):
                        raise ValueError(f"out of range: {expr!r}")
                    rolls = [rng.randint(1, sides) for _ in range(n)]
                    return sum(rolls) + int(mt[3] or 0), rolls

                def estimate(expr, trials, seed):
                    rng = random.Random(seed)
                    return statistics.fmean(roll(expr, rng)[0] for _ in range(trials))
            ''', "fullmatch (Ch 9) rejects trailing junk for free; the rng is passed in, so tests can hand you a "
                 "fake that always rolls high. That's dependency injection, and it's why the spec insisted."),
            "hand parser with partition": ('''
                import random

                def roll(expr, rng):
                    s = expr.strip()
                    sign = 1
                    body, mod = s, "0"
                    for op in "+-":
                        if op in s[1:]:
                            body, _, mod = s.partition(op)
                            sign = 1 if op == "+" else -1
                            break
                    n, d, sides = body.partition("d")
                    if not d or not sides.isdigit() or not (n == "" or n.isdigit()) or not mod.isdigit():
                        raise ValueError(f"not a dice expression: {expr!r}")
                    n, sides = int(n or 1), int(sides)
                    if not (1 <= n <= 100 and 2 <= sides <= 1000):
                        raise ValueError(f"out of range: {expr!r}")
                    rolls = [rng.randint(1, sides) for _ in range(n)]
                    return sum(rolls) + sign * int(mod), rolls

                def estimate(expr, trials, seed):
                    rng = random.Random(seed)
                    return sum(roll(expr, rng)[0] for _ in range(trials)) / trials
            ''', "No regex: str.partition and isdigit. Longer and easier to get subtly wrong (count the edge "
                 "cases the tests had to list), which is the case for the regex."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="print(0.1 + 0.2 == 0.3, round(2.5), round(3.5))", why="round() ties go to the even neighbour."),
    dict(kind="predict", code="print(-7 // 2, -7 % 2, int(-3.5))", why="// floors towards minus infinity; int() truncates towards zero."),
    dict(kind="predict", code="from decimal import Decimal\nprint(Decimal('0.1') * 3, Decimal(0.5) == Decimal('0.5'))", why="0.5 is a power of two, so the float is exact."),
    dict(kind="predict", code="from fractions import Fraction\nprint(Fraction(3, 6), Fraction(1, 3) * 3)"),
    dict(kind="predict", code="import statistics as st\nprint(st.median([1, 3, 2, 10]), st.mode([1, 2, 2, 3]))"),
    dict(kind="predict", code="from datetime import date\nprint((date(2026, 3, 1) - date(2026, 2, 1)).days)"),
    dict(kind="predict", code="import random\na = random.Random(7).random()\nb = random.Random(7).random()\nprint(a == b)"),
    dict(kind="recall", q="Which time function should you use to measure how long code takes?", a=["time.perf_counter", "perf_counter", "time.perf_counter()", "perf_counter()"]),
    dict(kind="recall", q="Which module should generate a password-reset token: random or secrets?", a=["secrets"]),
]
