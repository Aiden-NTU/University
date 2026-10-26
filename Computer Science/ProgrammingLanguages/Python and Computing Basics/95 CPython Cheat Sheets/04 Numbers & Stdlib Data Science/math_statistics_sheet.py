#!/usr/bin/env python3
"""
=============================================================================
SHEET: math / statistics                TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 04.x floats / descriptive stats / numeric helpers
=============================================================================

WHAT IT IS
  - math: C libm-backed real functions (sqrt, sin, log, comb, …) plus
    IEEE helpers (isfinite, isnan, frexp) and integer helpers (gcd, lcm,
    isqrt, perm, comb).
  - statistics: descriptive stats on Python iterables — mean, median,
    mode, pstdev/stdev, quantiles, … — stdlib only, not NumPy.
  - math.isclose: relative+absolute tolerance comparison for floats.

INVARIANTS
  - Python float is IEEE-754 binary64 (C double) on CPython platforms.
  - Many decimals (0.1, 0.2) are *not* exact in binary — sums drift.
  - isclose(a, b, *, rel_tol=1e-09, abs_tol=0.0): True if
      abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
  - statistics.mean uses a stable-ish accumulation; still float semantics.
  - stdev = sample (n-1); pstdev = population (n). Need ≥2 points for
    sample stdev.
  - quantiles: method-dependent cut points (see docs: inclusive/exclusive).

DELEGATES TO (CPython)
  - Modules/mathmodule.c — math.* wrapping libm + pure helpers
  - Modules/_statistics.c / Lib/statistics.py — stats algorithms
  - Objects/floatobject.c — PyFloat, binary64 ops
  - Python/pymath.h — platform math glue

COMPLEXITY CARD
  - math.sqrt / sin / …:     O(1) libm call (value-dependent internally)
  - math.comb(n, k):         O(k) style integer work (exact int result)
  - statistics.mean(xs):     O(n)
  - median:                  O(n) average with selection; may sort
  - stdev / variance:        O(n)
  - quantiles:               O(n log n) typical (sort)

WHEN A BEATS B
  - math.isclose vs == for floats: isclose for measured/computed reals;
    == for integers or exact bit patterns you truly need.
  - statistics vs hand-rolled sum/len: statistics for clarity + edge
    cases (empty, single element errors).
  - math.fsum vs sum for floats: fsum for long float sums (Shewchuk-
    style partials) — more accurate, still not Decimal money.
  - Leave for NumPy when you need vectorised arrays / BLAS, not a few
    Python floats.

EDGE CASES (float binary traps)
  - 0.1 + 0.2 != 0.3  (classic binary representation gap)
  - sum([0.1] * 10) may not equal 1.0
  - NaN: x != x; sort/stats behaviour with NaN is hostile — filter first
  - -0.0 vs 0.0: equal under == but distinct signs (copysign, atan2)
  - Overflow → inf; underflow → 0.0; check isfinite when needed
  - statistics on empty / one-element sample → StatisticsError

SOURCE MAP
  - Modules/mathmodule.c       :: math_isclose, math_fsum, libm wraps
  - Lib/statistics.py          :: mean, median, stdev, quantiles
  - Objects/floatobject.c      :: float_add / float_richcompare
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import math
import statistics

# --- math funcs ----------------------------------------------------------
# sqrt, exp, log, log10, log2, sin/cos/tan, degrees/radians
# hypot(*coords), dist(p, q)
# floor/ceil/trunc; fabs; frexp/ldexp; modf
# comb(n, k), perm(n, k), factorial, gcd, lcm, isqrt
# prod(iterable) — product of numbers

# --- isclose -------------------------------------------------------------
# Prefer isclose for "approximately equal" on binary floats.
# Tune abs_tol when comparing values near zero (rel_tol alone is weak).

# --- statistics ----------------------------------------------------------
# mean, fmean (float always), geometric_mean, harmonic_mean
# median, median_low, median_high, mode, multimode
# pstdev / pvariance (population); stdev / variance (sample)
# quantiles(data, *, n=4, method='exclusive') → n-1 cut points

# --- float binary traps --------------------------------------------------
# Decimal / Fraction when you need exact base-10 or exact rationals
# (see decimal_fractions_sheet.py). math/statistics stay in float-land.


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    assert math.sqrt(9.0) == 3.0
    assert math.comb(5, 2) == 10
    assert math.gcd(12, 18) == 6
    assert math.isqrt(10) == 3
    assert math.hypot(3, 4) == 5.0

    # Classic float trap
    assert 0.1 + 0.2 != 0.3
    assert math.isclose(0.1 + 0.2, 0.3)
    assert math.isclose(1e-12, 0.0, abs_tol=1e-9)
    assert not math.isclose(1e-12, 0.0)  # rel_tol alone fails near 0

    # fsum vs naive sum — fsum is the accurate accumulator for many floats
    xs = [0.1] * 10
    assert math.isclose(math.fsum(xs), 1.0)
    # Built-in sum may drift; do not rely on exact binary equality:
    assert isinstance(sum(xs), float)

    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert statistics.mean(data) == 3.0
    assert statistics.median(data) == 3.0
    assert math.isclose(
        statistics.stdev(data), math.sqrt(statistics.variance(data))
    )
    assert math.isclose(statistics.pstdev([1.0, 1.0, 1.0]), 0.0)

    qs = statistics.quantiles([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], n=4)
    assert len(qs) == 3 and qs[0] <= qs[1] <= qs[2]

    # Empty mean → StatisticsError
    try:
        statistics.mean([])
        raise AssertionError("expected StatisticsError")
    except statistics.StatisticsError:
        pass

    # NaN inequality
    nan = float("nan")
    assert nan != nan and math.isnan(nan)
    assert not math.isfinite(float("inf"))

    print("math_statistics_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
