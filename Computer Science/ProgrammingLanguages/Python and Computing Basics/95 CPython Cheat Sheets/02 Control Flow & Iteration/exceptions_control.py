#!/usr/bin/env python3
"""
=============================================================================
SHEET: exceptions as control flow      TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x errors / PEP 3134 / PEP 654 ExceptionGroup
=============================================================================

WHAT IT IS
  - Exceptions signal failure *and* non-local control transfer: raise jumps
    to the nearest matching except, running finally handlers on the way.
  - try / except / else / finally: structured handlers; else runs when no
    exception escaped the try body; finally always runs on the way out.
  - raise X from Y sets __cause__ (explicit chaining); implicit __context__
    is kept when an exception is raised during handling of another.
  - ExceptionGroup (PEP 654) bundles multiple unrelated exceptions — used
    heavily by TaskGroup / concurrent failure aggregation; `except*`
    unwraps matching subgroups.

INVARIANTS
  - except matches by isinstance(exc, listed_type) — order matters; put
    specific subclasses before bases.
  - bare `raise` inside except re-raises the active exception (keeps
    traceback). `raise New()` starts a new raise; use `from` to chain.
  - finally runs on return / break / continue / exception / fallthrough.
    If finally raises or returns, it can suppress the pending exception.
  - else is skipped if try raised (even if except handled it) — else means
    "try completed without exception", not "no error occurred ever".
  - EAFP ("easier to ask forgiveness"): try the operation, catch expected
    errors. LBYL ("look before you leap"): check preconditions first.
  - Exceptions are for *exceptional / rare / error* paths. Using them for
    ordinary tight-loop control is usually slower and harder to read than
    predicates / sentinels / iterators.

DELEGATES TO (CPython)
  - Python/ceval.c — RAISE_VARARGS, exception unwind, RERAISE
  - Objects/exceptions.c — BaseException hierarchy, ExceptionGroup
  - Python/traceback.c — traceback objects
  - Lib/traceback.py / Lib/exceptiongroup folklore (stdlib helpers)

COMPLEXITY CARD
  - Successful try path (no raise):     cheap setup (still > plain code)
  - raise + matching except:            expensive (allocate traceback,
                                        unwind frames) — µs–ms scale vs ns
  - LBYL `in` dict / getattr check:     O(1) expected, no traceback
  - EAFP KeyError on dict miss:         fine when misses are rare; costly
                                        when misses are the common case
  - ExceptionGroup build / except*:     O(n) in group size for splits

WHEN A BEATS B
  - EAFP vs LBYL for dict hit-heavy paths: EAFP often wins (one lookup).
  - LBYL vs EAFP when miss is common or check is cheap and clear:
    LBYL avoids traceback construction (e.g. os.path.exists before open
    is still racy — prefer EAFP for I/O races).
  - Iterator StopIteration vs return sentinel: protocol needs StopIteration;
    for app-level "not found" prefer None / Result / raise domain error
    once at an API boundary — not per-item in a hot loop.
  - raise from vs stuffing context in message: `from` preserves machine-
    readable causes for logging and __cause__ walks.
  - except* vs except ExceptionGroup: except* when you want to handle
    *matching subtypes* and leave the rest for outer handlers.

EDGE CASES
  - `except Exception` does not catch BaseException (KeyboardInterrupt,
    SystemExit, GeneratorExit) — usually what you want for cleanup layers.
  - `finally: return` swallows exceptions from try — footgun; 3.14+ warns.
  - Chaining: __cause__ is explicit (`from`); __context__ is implicit;
    `raise X from None` suppresses context display.
  - Multiple exceptions in 3.11+ ExceptionGroup — `except*` can run
    partial handlers; unhandled subgroups re-raise.
  - Catching too broadly then ignoring (`except Exception: pass`) hides bugs.
  - Evaluating `expensive()` in `except` headers is not a thing — patterns
    are types (or tuples of types), not callables (unless metaclass tricks).

SOURCE MAP
  - Objects/exceptions.c :: Exception / ExceptionGroup / BaseExceptionGroup
  - Python/ceval.c :: exception handling / RERAISE
  - PEP 3134 (chaining) / PEP 654 (ExceptionGroup) / PEP 678 (notes)
=============================================================================
"""

from __future__ import annotations

import sys

# --- API walkthrough (dense comments, setts.py style) ---------------------

# --- Hierarchy sketch ----------------------------------------------------
# BaseException
#   ├── SystemExit / KeyboardInterrupt / GeneratorExit
#   └── Exception
#         ├── ArithmeticError (ZeroDivisionError, OverflowError, …)
#         ├── LookupError (KeyError, IndexError)
#         ├── OSError (FileNotFoundError, PermissionError, …)
#         ├── ValueError / TypeError / RuntimeError / …
#         └── ExceptionGroup (PEP 654) — also BaseExceptionGroup sibling path
assert issubclass(KeyError, LookupError)
assert issubclass(FileNotFoundError, OSError)
assert not issubclass(KeyboardInterrupt, Exception)

# --- try / except / else / finally ---------------------------------------


def divide(a: float, b: float) -> str:
    try:
        q = a / b
    except ZeroDivisionError:
        return "nan-path"
    else:
        # runs only if try did *not* raise — good for post-success work
        # that should not be covered by the same except clauses
        return f"ok:{q}"
    finally:
        # always runs before the function actually returns
        # (cleanup: close files, release locks, …)
        pass


assert divide(6, 3) == "ok:2.0"
assert divide(1, 0) == "nan-path"

# Order: body → (except? → else?) → finally → leave.
# Concrete: success → else → finally → return else value.
#            fail    → except → finally → return except value.


def order_trace(fail: bool) -> list[str]:
    log: list[str] = []
    try:
        log.append("try")
        if fail:
            raise RuntimeError("x")
    except RuntimeError:
        log.append("except")
    else:
        log.append("else")
    finally:
        log.append("finally")
    return log


assert order_trace(False) == ["try", "else", "finally"]
assert order_trace(True) == ["try", "except", "finally"]

# --- raise / re-raise / raise from ---------------------------------------


def parse_int(s: str) -> int:
    try:
        return int(s)
    except ValueError as e:
        # Explicit chaining: caller sees __cause__ == original ValueError
        raise ValueError(f"not an int: {s!r}") from e


try:
    parse_int("x")
except ValueError as e:
    assert e.__cause__ is not None
    assert isinstance(e.__cause__, ValueError)

# Suppress context when wrapping would be misleading:
try:
    try:
        raise OSError("disk")
    except OSError:
        raise RuntimeError("wrap") from None
except RuntimeError as e:
    assert e.__cause__ is None
    # __context__ may still be set internally but display is suppressed

# bare raise: re-raise current exception


def reraise_demo() -> None:
    try:
        raise KeyError("k")
    except KeyError:
        raise  # same object / traceback continuation


try:
    reraise_demo()
except KeyError as e:
    assert e.args == ("k",)

# --- EAFP vs LBYL cost intuition -----------------------------------------
# Dict hit path — EAFP (one lookup):
d = {"a": 1}


def eafp(key: str) -> int | None:
    try:
        return d[key]
    except KeyError:
        return None


# LBYL (two lookups on hit unless you bind):
def lbyl(key: str) -> int | None:
    if key in d:
        return d[key]
    return None


assert eafp("a") == lbyl("a") == 1
assert eafp("z") is lbyl("z") is None
# Prefer d.get(key) for this specific case — clear and C-fast.
assert d.get("z") is None

# When misses dominate *and* you catch a broad exception with a traceback,
# LBYL / get / explicit checks win. When hits dominate, EAFP / direct [] wins.
# I/O: LBYL exists()+open races; EAFP open+FileNotFoundError is correct.

# --- When exceptions are the wrong control mechanism ---------------------
# Anti-pattern: use exceptions for expected end-of-stream in app code
# (iterators already have StopIteration at the protocol layer — don't
# reinvent it for ordinary business logic).


def find_first_even_bad(xs: list[int]) -> int:
    # Bad style for expected "not found":
    try:
        for x in xs:
            if x % 2 == 0:
                return x
        raise RuntimeError("not found")  # control, not crisis
    except RuntimeError:
        return -1


def find_first_even_good(xs: list[int]) -> int:
    for x in xs:
        if x % 2 == 0:
            return x
    return -1  # sentinel / or raise *at API boundary* once


assert find_first_even_bad([1, 3, 4]) == find_first_even_good([1, 3, 4]) == 4
assert find_first_even_bad([1, 3]) == find_first_even_good([1, 3]) == -1

# Hot loops: prefer `if key in d` / `.get` / predicates over per-iteration
# try/except when the "except" path is common.

# --- ExceptionGroup & except* (brief) ------------------------------------
# Bundling multiple failures (task groups, validation aggregates):
eg = ExceptionGroup(
    "multi",
    [ValueError("a"), TypeError("b"), ValueError("c")],
)

# except* matches *subgroups* by type; may leave residual group.
values: list[str] = []
others: list[BaseException] = []
try:
    raise eg
except* ValueError as vg:
    # vg is an ExceptionGroup of the ValueError parts
    values.extend(str(e) for e in vg.exceptions)
except* TypeError as tg:
    others.extend(tg.exceptions)

assert values == ["a", "c"]
assert len(others) == 1 and isinstance(others[0], TypeError)

# Nested groups can be split; unhandled parts propagate as ExceptionGroup.
# Prefer except* when handlers are type-specific; plain
#   except ExceptionGroup as e
# when you want the whole bundle.

# --- notes (3.11+) -------------------------------------------------------
err = ValueError("boom")
err.add_note("while parsing config")  # appears in traceback display
assert "while parsing config" in err.__notes__


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    assert divide(8, 2) == "ok:4.0"
    assert order_trace(True)[-1] == "finally"

    # chaining
    try:
        parse_int("nope")
    except ValueError as e:
        assert isinstance(e.__cause__, ValueError)

    # matching order: specific before general
    def order(exc: BaseException) -> str:
        try:
            raise exc
        except KeyError:
            return "key"
        except LookupError:
            return "lookup"
        except Exception:
            return "exc"

    assert order(KeyError()) == "key"
    assert order(IndexError()) == "lookup"

    # Footgun (do not copy): `return` / `break` / new `raise` inside
    # `finally` can suppress a pending exception from `try`. CPython 3.14
    # warns on `return` in `finally` — keep cleanup side-effect-only.

    # ExceptionGroup split
    try:
        raise ExceptionGroup("g", [KeyError("k"), ValueError("v")])
    except* KeyError as kg:
        assert all(isinstance(e, KeyError) for e in kg.exceptions)
    except* ValueError as vg:
        assert all(isinstance(e, ValueError) for e in vg.exceptions)

    # EAFP file-style without touching disk: getattr
    class Obj:
        x = 1

    o = Obj()
    try:
        v = o.x
    except AttributeError:
        v = None
    assert v == 1
    assert getattr(o, "y", None) is None

    assert sys.version_info >= (3, 14)
    print("exceptions_control.py: all probes passed")


if __name__ == "__main__":
    _probes()
