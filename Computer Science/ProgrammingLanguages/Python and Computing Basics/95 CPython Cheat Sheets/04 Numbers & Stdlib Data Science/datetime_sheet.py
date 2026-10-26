#!/usr/bin/env python3
"""
=============================================================================
SHEET: datetime                         TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 04.x civil time / aware vs naive / UTC
=============================================================================

WHAT IT IS
  - datetime.date — calendar date (y, m, d)
  - datetime.time — wall-clock time of day (optional tzinfo)
  - datetime.datetime — date + time (optional tzinfo)
  - datetime.timedelta — duration (days, seconds, microseconds…)
  - datetime.timezone / datetime.UTC — fixed-offset tzinfo; UTC singleton
  - isoformat / fromisoformat — round-trip friendly string forms

INVARIANTS
  - Naive objects have tzinfo is None — they are *not* UTC by default;
    they are "unspecified zone" civil times.
  - Aware objects have tzinfo set; comparisons between aware & naive
    raise TypeError.
  - UTC: prefer datetime.now(UTC) / datetime.now(timezone.utc) over
    deprecated utcnow() (naive UTC trap).
  - timedelta arithmetic on aware datetimes preserves/normalises via
    tzinfo; converting zones uses astimezone().
  - date/datetime are immutable value objects; replace() returns new.

DELEGATES TO (CPython)
  - Lib/datetime.py — pure Python + C accelerator
  - Modules/_datetimemodule.c — C implementation of types
  - time module / OS — clock sources for now()/today()

COMPLEXITY CARD
  - construct / replace / isoformat:   O(1)
  - timedelta add/sub:                 O(1)
  - astimezone:                        O(1) + tz rules (fixed offset cheap)
  - parsing fromisoformat:             O(length of string)

WHEN A BEATS B
  - aware UTC storage vs naive local: store/transmit UTC aware; convert
    to local only at the edges (UI).
  - date vs datetime: date when time-of-day is meaningless.
  - timedelta vs raw second ints: timedelta for readable durations.
  - isoformat vs strftime: isoformat for interchange; strftime for
    locale/display layouts.

EDGE CASES
  - Naive now() is local time — folding DST ambiguities need care.
  - utcnow() returns *naive* — easy to mis-label as UTC; avoided in
    modern code (3.12+ deprecation path toward removal).
  - fromisoformat is strict about formats it accepts (broader than
    early 3.7, still not every RFC3339 oddity).
  - Mixing zones: a.astimezone(b.tzinfo); don't subtract distant naives
    pretending they share a zone.
  - timedelta modulo / division quirks — read docs for total_seconds.

SOURCE MAP
  - Modules/_datetimemodule.c   :: datetime_now, astimezone, …
  - Lib/datetime.py             :: timezone, UTC, isoformat helpers
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

from datetime import (
    UTC,
    date,
    datetime,
    time,
    timedelta,
    timezone,
)

# --- date / time / datetime / timedelta ----------------------------------
# date(2026, 10, 23); date.today()
# time(14, 30, 0); time(14, 30, tzinfo=UTC)
# datetime(2026, 10, 23, 14, 30, tzinfo=UTC)
# timedelta(days=1, hours=2, minutes=3)

# --- aware vs naive ------------------------------------------------------
# naive:  datetime(2026, 1, 1, 12, 0)           # tzinfo is None
# aware:  datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
# Prefer: datetime.now(UTC)  over  datetime.utcnow()

# --- timezone UTC --------------------------------------------------------
# UTC is timezone.utc (alias datetime.UTC since 3.11)
# Fixed offsets: timezone(timedelta(hours=1), name="CET-ish")

# --- isoformat -----------------------------------------------------------
# dt.isoformat() → '2026-10-23T14:30:00+00:00'
# datetime.fromisoformat(s)


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    d = date(2026, 10, 23)
    assert d.isoformat() == "2026-10-23"
    assert date.fromisoformat("2026-10-23") == d

    t = time(14, 30, 0)
    assert t.hour == 14 and t.tzinfo is None

    naive = datetime(2026, 10, 23, 14, 30, 0)
    aware = datetime(2026, 10, 23, 14, 30, 0, tzinfo=UTC)
    assert naive.tzinfo is None and aware.tzinfo is UTC
    assert UTC is timezone.utc

    # Equality across naive/aware is False; ordering raises TypeError.
    assert (naive == aware) is False
    try:
        _ = naive < aware
        raise AssertionError("expected TypeError")
    except TypeError:
        pass

    delta = timedelta(hours=2, minutes=15)
    assert aware + delta == datetime(2026, 10, 23, 16, 45, 0, tzinfo=UTC)
    assert delta.total_seconds() == 2 * 3600 + 15 * 60

    # now(UTC) is aware
    now_utc = datetime.now(UTC)
    assert now_utc.tzinfo is not None

    # isoformat round-trip
    iso = aware.isoformat()
    assert iso.endswith("+00:00") or iso.endswith("Z") or "+00:00" in iso
    assert datetime.fromisoformat(iso) == aware

    # Fixed offset zone
    cet = timezone(timedelta(hours=1))
    localish = aware.astimezone(cet)
    assert localish.hour == 15 and localish.tzinfo == cet
    # Back to UTC
    assert localish.astimezone(UTC) == aware

    # replace returns new object
    assert d.replace(day=24) == date(2026, 10, 24) and d.day == 23

    print("datetime_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
