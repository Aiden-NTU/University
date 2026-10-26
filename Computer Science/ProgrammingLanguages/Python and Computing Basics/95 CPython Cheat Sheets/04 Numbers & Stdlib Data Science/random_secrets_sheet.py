#!/usr/bin/env python3
"""
=============================================================================
SHEET: random / secrets                 TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 04.x PRNG vs CSPRNG / tokens / simulations
=============================================================================

WHAT IT IS
  - random: *deterministic* pseudo-random number generator (Mersenne
    Twister by default) for simulations, shuffles, games, teaching.
    NOT cryptographically secure. Seedable → reproducible sequences.
  - secrets: CSPRNG wrappers for passwords, tokens, security-sensitive
    picks — uses os.urandom / SystemRandom under the hood.
  - random.SystemRandom: random.Random API backed by os.urandom (also
    suitable for crypto-ish picks, but secrets is the clearer intent).

INVARIANTS
  - random.seed(x) makes subsequent random.* calls reproducible for that
    generator state (same platform/version assumptions).
  - Module-level random.* uses a shared global Random instance — fine for
    scripts; use Random() instances for isolation / threads care.
  - secrets.token_bytes / token_hex / token_urlsafe: unpredictable tokens.
  - secrets.choice / randbelow: CSPRNG analogues of common needs.
  - NEVER use random.random / random.choice / uuid without crypto for
    session tokens, reset links, API keys, lottery of capabilities.

DELEGATES TO (CPython)
  - Lib/random.py — Random, MT19937, SystemRandom
  - Modules/_randommodule.c — Mersenne Twister core
  - Lib/secrets.py — token_* on top of SystemRandom / urandom
  - Modules/posixmodule.c :: os_urandom — kernel CSPRNG bytes

COMPLEXITY CARD
  - random.random():          O(1)
  - shuffle(list of n):       O(n)
  - sample(pop, k):           O(k) typical
  - secrets.token_bytes(n):   O(n) urandom
  - SystemRandom.random():    O(1) but syscall/CSPRNG cost ≫ MT

WHEN A BEATS B
  - random for Monte Carlo / shuffle playlists / generative art seeds.
  - secrets for anything an attacker must not predict.
  - SystemRandom when you want Random's API with urandom entropy.
  - secrets.token_urlsafe vs hand-rolled base64(random.getrandbits):
    use secrets — getrandbits is MT, not secret.

EDGE CASES
  - Re-seeding with time.time() is still predictable — not security.
  - Forking: child may inherit PRNG state — reseed after fork if needed.
  - random.randrange vs secrets.randbelow: latter for secret bounds.
  - "Obscure formula on random.random()" is still not crypto.
  - Documentation slogan: random = simulation; secrets = credentials.

SOURCE MAP
  - Lib/random.py              :: Random, SystemRandom
  - Modules/_randommodule.c    :: genrand / seed
  - Lib/secrets.py             :: token_bytes / token_urlsafe / choice
  - Modules/posixmodule.c      :: os_urandom
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import random
import secrets

# --- random PRNG (NOT crypto) --------------------------------------------
# random.random() → [0.0, 1.0)
# random.randrange(a, b), randint(a, b), choice, sample, shuffle, gauss…
# rng = random.Random(42); rng.random()  — isolated instance

# --- secrets token_* -----------------------------------------------------
# secrets.token_bytes(32)
# secrets.token_hex(16)       # 32 hex chars
# secrets.token_urlsafe(16)   # base64-url, ~22 chars for 16 bytes
# secrets.randbelow(n)        # 0 .. n-1, uniform, CSPRNG
# secrets.compare_digest(a,b) # constant-time str/bytes compare

# --- SystemRandom --------------------------------------------------------
# sr = random.SystemRandom(); sr.choice(seq) — urandom-backed


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    # Reproducible PRNG
    rng_a = random.Random(12345)
    rng_b = random.Random(12345)
    seq_a = [rng_a.random() for _ in range(5)]
    seq_b = [rng_b.random() for _ in range(5)]
    assert seq_a == seq_b

    # Different seed → different stream (extremely likely)
    rng_c = random.Random(99999)
    assert [rng_c.random() for _ in range(5)] != seq_a

    # API smoke
    assert 0 <= random.Random(0).random() < 1
    assert random.Random(0).randint(1, 1) == 1
    deck = [1, 2, 3, 4]
    random.Random(0).shuffle(deck)
    assert sorted(deck) == [1, 2, 3, 4]
    assert set(random.Random(0).sample(range(10), 3)) <= set(range(10))

    # secrets tokens: length contracts
    assert len(secrets.token_bytes(16)) == 16
    assert len(secrets.token_hex(16)) == 32
    tok = secrets.token_urlsafe(16)
    assert isinstance(tok, str) and len(tok) >= 16

    # randbelow
    assert 0 <= secrets.randbelow(10) < 10
    assert secrets.choice("abc") in "abc"

    # SystemRandom is not seedable for prediction the MT way
    sr = random.SystemRandom()
    try:
        sr.seed(1)  # may be ignored / no-op for reproducibility
    except NotImplementedError:
        pass
    # Still produces a float in range:
    assert 0.0 <= sr.random() < 1.0

    # compare_digest
    assert secrets.compare_digest("abc", "abc")
    assert not secrets.compare_digest("abc", "abd")

    # Pedagogical contrast: MT getrandbits is NOT for tokens
    # (we do not use it for a token here — only show it exists)
    assert isinstance(random.getrandbits(32), int)

    print("random_secrets_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
