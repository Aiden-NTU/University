#!/usr/bin/env python3
"""
=============================================================================
SHEET: decimal / fractions              TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 04.x exact arithmetic / money / rationals
=============================================================================

WHAT IT IS
  - decimal.Decimal: decimal floating-point with user-selectable precision
    and rounding via Context — base-10, suitable for money/ledger maths
    when configured deliberately.
  - fractions.Fraction: exact rational (numerator/denominator ints in
    lowest terms). Closed under +, −, ×, ÷ (except ÷0).
  - Both exist because binary float lies about many decimal fractions.

INVARIANTS
  - Decimal("0.1") is exact tenth; float(0.1) is not.
  - Construct Decimal from *strings* (or ints), not from polluted floats,
    unless you intentionally want Decimal(repr of that binary value).
  - Context.prec / rounding / traps control Decimal ops globally
    (localcontext() for scoped changes).
  - quantize(Decimal("0.01")) rounds to cents under current context
    rounding mode — the money idiom.
  - Fraction(1, 3) stays 1/3 forever; float(1/3) is an approximation.
  - Fraction(Decimal) / Fraction(float) have defined conversions —
    float path still embeds binary error if you start from float.

DELEGATES TO (CPython)
  - Modules/_decimal/* (mpdecimal) — Decimal engine
  - Lib/decimal.py — Context, public API
  - Lib/fractions.py — Fraction arithmetic / limits
  - Objects/longobject.c — arbitrary-precision ints underneath Fraction

COMPLEXITY CARD
  - Decimal +/− at precision p:     roughly poly in p (mpdecimal)
  - Decimal ×/÷:                    higher cost in p
  - Fraction +/−:                   O(size of ints) gcd work
  - Fraction from float:            exact binary rational of that float

WHEN A BEATS B
  - Decimal vs float for currency: Decimal (+ quantize) — float for
    physics/signals/approx where binary is native.
  - Fraction vs Decimal: Fraction for exact ratios / rational proofs;
    Decimal for fixed-exponent decimal money and reports.
  - Decimal vs float when sum of tenths must equal one: Decimal.
  - float when speed + libm + NumPy matter and error is tolerable.

EDGE CASES — when float lies for money
  - 0.1 + 0.2 != 0.3 in float → ledger drift if you bank on ==.
  - Decimal(0.1) captures the *binary* value of float 0.1 — surprise!
    Use Decimal("0.1") or Decimal.from_float only when intentional.
  - Division: Context division traps / Inexact signals if traps enabled.
  - Mixing Decimal and float in expressions → TypeError (good).
  - Fraction limit_denominator for friendly approximations of floats.

SOURCE MAP
  - Modules/_decimal/…          :: mpdecimal bindings
  - Lib/decimal.py              :: Context, Decimal.quantize
  - Lib/fractions.py            :: Fraction._operator hooks
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

from decimal import ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction

# --- Decimal context -----------------------------------------------------
# getcontext().prec = 28  (default often 28)
# with localcontext() as ctx:
#     ctx.prec = 6
#     ctx.rounding = ROUND_HALF_UP
# Rounding modes: ROUND_HALF_EVEN (banker's, default), HALF_UP, etc.

# --- quantize ------------------------------------------------------------
# amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  → cents

# --- Fraction ------------------------------------------------------------
# Fraction(1, 3) + Fraction(1, 6) == Fraction(1, 2)
# Fraction("0.1") exact; Fraction(0.1) = exact value of that float


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    # Float lies; Decimal string truth
    assert 0.1 + 0.2 != 0.3
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")

    # The float constructor trap
    sneaky = Decimal(0.1)
    assert sneaky != Decimal("0.1")
    assert format(sneaky, ".20f").startswith("0.10000000000000000")

    # Money: quantize to cents
    price = Decimal("10.00")
    tax = (price * Decimal("0.075")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    assert tax == Decimal("0.75")
    total = price + tax
    assert total == Decimal("10.75")

    # Scoped precision
    with localcontext() as ctx:
        ctx.prec = 4
        assert +Decimal("1") / Decimal("3") == Decimal("0.3333")

    # Fraction exact rationals
    assert Fraction(1, 3) + Fraction(1, 6) == Fraction(1, 2)
    assert Fraction(1, 3) * 3 == Fraction(1, 1)
    assert float(Fraction(1, 3)) != Fraction(1, 3)  # float approx
    # Comparing Fraction to float is allowed but think carefully:
    assert Fraction(1, 2) == 0.5  # 0.5 is exact in binary

    # Fraction from float embeds binary error
    assert Fraction(0.1) != Fraction(1, 10)
    assert Fraction("0.1") == Fraction(1, 10)

    # Friendly approx of a float via continued fractions
    pi_approx = 3.141592653589793
    approx = Fraction(pi_approx).limit_denominator(1000)
    assert approx == Fraction(355, 113)
    assert abs(float(approx) - pi_approx) < 1e-6

    # No silent Decimal/float mix
    try:
        _ = Decimal("1") + 0.1  # type: ignore[operator]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass

    print("decimal_fractions_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
