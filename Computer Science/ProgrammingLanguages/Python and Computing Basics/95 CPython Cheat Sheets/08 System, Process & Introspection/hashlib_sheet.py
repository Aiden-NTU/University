#!/usr/bin/env python3
"""
=============================================================================
SHEET: hashlib (+ secrets / KDF notes)       TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x stdlib crypto primitives
=============================================================================

WHAT IT IS
  - hashlib: cryptographic hash / BLAKE2 / SHA-2/3 constructors; .update
    streaming; .digest() / .hexdigest().
  - hmac.compare_digest / secrets.compare_digest: constant-time compare.
  - Passwords: use a KDF (hashlib.scrypt / pbkdf2_hmac) — never store raw
    SHA of a password. Tokens/API keys: secrets module.

INVARIANTS
  - Hash objects are incremental: update(b1); update(b2) == update(b1+b2).
  - Digests are deterministic for given algorithm + input.
  - compare_digest(a, b) resists timing attacks on equality of secrets.
  - hashlib is not encryption; SHA256(password) is not password hashing.

DELEGATES TO (CPython)
  - Modules/hashlib.c + _hashlib (OpenSSL) / HACL* builtins for some algs
  - Lib/secrets.py → SystemRandom / token_* 

COMPLEXITY CARD
  - SHA-256: O(n) in message length
  - scrypt / pbkdf2: intentionally expensive (tune n/r/p or iterations)

WHEN A BEATS B
  - blake2b → sha256 for speed on large local data (still crypto-grade).
  - scrypt/pbkdf2 → raw sha256 for password storage.
  - secrets.token_urlsafe → hash of time.time() for tokens (predictable).

EDGE CASES
  - usedforsecurity=False for non-crypto checksums of insecure algs (MD5).
  - update() accepts buffered protocol (memoryview, bytearray).
  - OpenSSL vs builtin availability varies — algorithms_guaranteed safe set.
  - Never log raw tokens; compare with compare_digest.

SOURCE MAP
  - Modules/hashlib.h / hashlibmodule
  - Lib/hashlib.py :: new, scrypt, pbkdf2_hmac
  - Lib/secrets.py :: token_bytes, token_hex, token_urlsafe
  - Lib/hmac.py :: compare_digest
=============================================================================
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

# --- API walkthrough ------------------------------------------------------
#
# h = hashlib.sha256(b"...")           # or hashlib.new("sha256")
# h.update(chunk); h.digest(); h.hexdigest(); h.copy()
# hashlib.blake2b(data, digest_size=32, key=b"", salt=b"", person=b"")
# hashlib.algorithms_guaranteed / algorithms_available
#
# hashlib.pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None)
# hashlib.scrypt(password, *, salt, n, r, p, maxmem=0, dklen=64)
#
# secrets.token_bytes(n); token_hex(n); token_urlsafe(n)
# secrets.compare_digest(a, b)  # also hmac.compare_digest
#
# Password storage recipe (conceptual):
#   salt = secrets.token_bytes(16)
#   dk = hashlib.scrypt(password, salt=salt, n=2**14, r=8, p=1, dklen=32)
#   store (salt, dk) — verify with compare_digest


def _probes() -> None:
    # --- sha256 / streaming ----------------------------------------------
    one = hashlib.sha256(b"hello world").hexdigest()
    h = hashlib.sha256()
    h.update(b"hello ")
    h.update(b"world")
    assert h.hexdigest() == one
    assert len(h.digest()) == 32

    # --- blake2 ----------------------------------------------------------
    b2 = hashlib.blake2b(b"hello world", digest_size=32)
    assert len(b2.digest()) == 32
    assert b2.hexdigest() != one  # different algorithm

    # --- compare_digest --------------------------------------------------
    a = hashlib.sha256(b"secret").digest()
    b = hashlib.sha256(b"secret").digest()
    c = hashlib.sha256(b"other").digest()
    assert hmac.compare_digest(a, b) is True
    assert secrets.compare_digest(a, c) is False

    # --- KDF for passwords (not raw hash) --------------------------------
    password = b"correct horse battery staple"
    salt = secrets.token_bytes(16)
    # Modest params for a fast probe — production: higher n / iterations
    dk1 = hashlib.scrypt(password, salt=salt, n=2**10, r=8, p=1, dklen=32)
    dk2 = hashlib.scrypt(password, salt=salt, n=2**10, r=8, p=1, dklen=32)
    assert secrets.compare_digest(dk1, dk2)
    wrong = hashlib.scrypt(b"nope", salt=salt, n=2**10, r=8, p=1, dklen=32)
    assert not secrets.compare_digest(dk1, wrong)

    pbk = hashlib.pbkdf2_hmac("sha256", password, salt, iterations=10_000, dklen=32)
    assert len(pbk) == 32
    # Lesson: sha256(password) alone is insufficient — use KDF above.

    # --- secrets for tokens ----------------------------------------------
    tok = secrets.token_urlsafe(16)
    assert isinstance(tok, str) and len(tok) >= 16
    assert len(secrets.token_bytes(16)) == 16
    assert len(secrets.token_hex(8)) == 16  # 8 bytes → 16 hex chars

    assert "sha256" in hashlib.algorithms_guaranteed

    print("hashlib_sheet: OK", f"sha256_prefix={one[:12]}")


if __name__ == "__main__":
    _probes()
