EXERCISES = [
    dict(
        id="13.1", kind="build", title="Fingerprint a file in chunks",
        task="""
        Write `file_digest(path, algorithm="sha256")` returning the hex digest of the file's bytes,
        reading it in chunks (say 64 KB) so a 10 GB file wouldn't need 10 GB of memory.

        `algorithm` is any name `hashlib.new()` accepts ("sha256", "sha512", "blake2b", ...).
        Open the file with the built-in `open(path, "rb")` (the tests watch how you read it).
        Then: `hashlib.file_digest` exists since 3.11. Try it afterwards and compare.
        """,
        stub='''
        import hashlib

        def file_digest(path, algorithm="sha256"):
            ...
        ''',
        tests='''
        import hashlib, os, random

        def test_random_files(m):
            rng = random.Random(1)
            for size in [0, 1, 100, 65535, 65536, 65537, 1_000_003]:
                data = rng.randbytes(size)
                with open("f.bin", "wb") as fh:
                    fh.write(data)
                for alg in ("sha256", "sha512", "blake2b", "md5"):
                    equal(m.file_digest("f.bin", alg), hashlib.new(alg, data).hexdigest(), f"{alg}, {size} bytes")

        def test_default_is_sha256(m):
            with open("x", "wb") as fh:
                fh.write(b"hello")
            equal(m.file_digest("x"), hashlib.sha256(b"hello").hexdigest(), "default algorithm")

        def test_reads_in_chunks(m):
            import builtins
            real_open = builtins.open
            reads = []
            class Spy:
                def __init__(self, f):
                    self.f = f
                def read(self, n=-1):
                    reads.append(n)
                    return self.f.read(n)
                def readinto(self, buf):
                    reads.append(len(buf))
                    return self.f.readinto(buf)
                def __enter__(self):
                    return self
                def __exit__(self, *exc):
                    self.f.close()
                def __getattr__(self, name):
                    return getattr(self.f, name)
            with real_open("big", "wb") as fh:
                fh.write(b"z" * 300_000)
            def spy_open(p, mode="r", *a, **k):
                f = real_open(p, mode, *a, **k)
                return Spy(f) if "b" in mode and "r" in mode and str(p) == "big" else f
            builtins.open = spy_open
            try:
                m.file_digest("big")
            finally:
                builtins.open = real_open
            check(reads and all(n is not None and 0 < n <= 1_000_000 for n in reads),
                  f"read the file in chunks with fh.read(size), not all at once (calls: {reads[:5]})")
        ''',
        alts={
            "walrus loop": ('''
                import hashlib

                def file_digest(path, algorithm="sha256"):
                    h = hashlib.new(algorithm)
                    with open(path, "rb") as fh:
                        while chunk := fh.read(64 * 1024):
                            h.update(chunk)
                    return h.hexdigest()
            ''', "The walrus (:=) reads and tests in one line; the loop ends on b'' (end of file)."),
            "iter with sentinel": ('''
                import hashlib
                from functools import partial

                def file_digest(path, algorithm="sha256"):
                    h = hashlib.new(algorithm)
                    with open(path, "rb") as fh:
                        for chunk in iter(partial(fh.read, 1 << 16), b""):
                            h.update(chunk)
                    return h.hexdigest()
            ''', "iter(callable, sentinel) calls fh.read(65536) until it returns b''. A classic idiom."),
        },
    ),
    dict(
        id="13.2", kind="build", title="Sign and verify messages with HMAC",
        task="""
        Write `sign(message: bytes, key: bytes) -> str` that returns a token `"<base64url message>.<hex tag>"`
        where the tag is HMAC-SHA256 of the message, and `verify(token: str, key: bytes) -> bytes`
        that returns the original message, or raises `ValueError` if the token was altered in any way,
        was made with another key, or is malformed.

        Compare tags with `hmac.compare_digest` (the tests check you do).
        """,
        stub='''
        import base64
        import hmac

        def sign(message, key):
            ...

        def verify(token, key):
            ...
        ''',
        tests='''
        import random, string

        def test_round_trip(m):
            rng = random.Random(4)
            for _ in range(100):
                msg = rng.randbytes(rng.randint(0, 60))
                key = rng.randbytes(16)
                equal(m.verify(m.sign(msg, key), key), msg, "verify(sign(msg))")

        def test_any_edit_is_caught(m):
            key = b"k" * 16
            tok = m.sign(b"user=42;role=student", key)
            for i in range(len(tok)):
                for c in "A0f.-_x":
                    if tok[i] == c:
                        continue
                    bad = tok[:i] + c + tok[i + 1:]
                    try:
                        got = m.verify(bad, key)
                    except ValueError:
                        continue
                    check(got == b"user=42;role=student", f"edited token {bad!r} was accepted")

        def test_wrong_key_and_junk(m):
            tok = m.sign(b"hello", b"key one")
            raises(ValueError, m.verify, tok, b"key two")
            for junk in ["", ".", "abc", "no-dot-here", "a.b.c", "!!!.zz"]:
                raises(ValueError, m.verify, junk, b"key one")

        def test_uses_compare_digest(m):
            check(uses_name(m, "compare_digest"), "compare tags with hmac.compare_digest, not ==")
        ''',
        alts={
            "partition": ('''
                import base64
                import binascii
                import hmac

                def _tag(message, key):
                    return hmac.new(key, message, "sha256").hexdigest()

                def sign(message, key):
                    return base64.urlsafe_b64encode(message).decode() + "." + _tag(message, key)

                def verify(token, key):
                    body, dot, tag = token.partition(".")
                    if not dot:
                        raise ValueError("malformed token")
                    try:
                        message = base64.urlsafe_b64decode(body.encode())
                    except (binascii.Error, ValueError) as e:
                        raise ValueError("malformed token") from e
                    if not hmac.compare_digest(_tag(message, key), tag):
                        raise ValueError("bad signature")
                    return message
            ''', "Decoding first is safe here because nothing is trusted until compare_digest passes. Note "
                 "two different base64 strings can decode to the same bytes; signing the encoded body "
                 "(next alternative) avoids even thinking about it."),
            "sign the encoded text": ('''
                import base64
                import hmac

                def sign(message, key):
                    body = base64.urlsafe_b64encode(message).decode()
                    return body + "." + hmac.new(key, body.encode(), "sha256").hexdigest()

                def verify(token, key):
                    if token.count(".") != 1:
                        raise ValueError("malformed token")
                    body, tag = token.split(".")
                    good = hmac.new(key, body.encode(), "sha256").hexdigest()
                    if not hmac.compare_digest(good, tag):
                        raise ValueError("bad signature")
                    return base64.urlsafe_b64decode(body)
            ''', "Verify the exact bytes that travelled, before decoding anything: the pattern JWT uses."),
        },
    ),
    dict(
        id="13.3", kind="build", title="Store passwords properly",
        task="""
        Write `hash_password(password: str) -> str` and `verify_password(password: str, stored: str) -> bool`.

        - Use a slow, salted KDF from the stdlib: `hashlib.scrypt` (n=2**14, r=8, p=1) or
          `hashlib.pbkdf2_hmac("sha256", ..., iterations >= 600_000)`.
        - A fresh random salt (from `secrets`) for every call, stored inside the returned string
          together with the parameters, so hashing the same password twice gives different strings.
        - The stored string must not contain the password.
        - Compare with `hmac.compare_digest`.
        """,
        stub='''
        import hashlib
        import hmac
        import secrets

        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()

        def verify_password(password, stored):
            return hash_password(password) == stored
        ''',
        tests='''
        import time

        def test_verifies(m):
            for pw in ["correct horse", "", "pässwörd ✓", "x" * 200]:
                s = m.hash_password(pw)
                check(m.verify_password(pw, s), f"the right password {pw!r} should verify")
                check(not m.verify_password(pw + "!", s), "a wrong password must not verify")

        def test_salted(m):
            a, b = m.hash_password("same"), m.hash_password("same")
            check(a != b, "two hashes of the same password must differ (random salt)")
            check("same" not in a, "the stored string must not contain the password")

        def test_deliberately_slow(m):
            t = time.perf_counter()
            m.hash_password("timing")
            check(time.perf_counter() - t > 0.01, "hashing should take at least ~10 ms (use scrypt or "
                                                   "pbkdf2 with many iterations)")

        def test_safe_compare_and_randomness(m):
            check(uses_name(m, "compare_digest"), "use hmac.compare_digest")
            check("random" not in imports(m), "salts come from secrets (or os.urandom), not random")
        ''',
        alts={
            "scrypt": ('''
                import hashlib
                import hmac
                import secrets

                def hash_password(password):
                    salt = secrets.token_bytes(16)
                    h = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
                    return f"scrypt$16384$8$1${salt.hex()}${h.hex()}"

                def verify_password(password, stored):
                    algo, n, r, p, salt, h = stored.split("$")
                    got = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p))
                    return hmac.compare_digest(got.hex(), h)
            ''', "Memory-hard: each guess needs ~16 MB, which hurts GPU attackers far more than CPU time alone."),
            "pbkdf2": ('''
                import hashlib
                import hmac
                import secrets

                ITER = 600_000

                def hash_password(password):
                    salt = secrets.token_bytes(16)
                    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITER)
                    return f"pbkdf2_sha256${ITER}${salt.hex()}${h.hex()}"

                def verify_password(password, stored):
                    _, it, salt, h = stored.split("$")
                    got = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(it))
                    return hmac.compare_digest(got.hex(), h)
            ''', "The format Django uses. Only CPU-hard, so raise ITER over the years (OWASP's 2023 figure: "
                 "600,000)."),
        },
    ),
    dict(
        id="13.4", kind="build", title="A password generator you'd trust",
        task="""
        Write `generate(length=16, symbols=True)` returning a random password of exactly `length`
        characters that contains at least one lowercase letter, one uppercase letter, one digit and
        (if `symbols`) one character from `"!@#$%&*-_"`. Without symbols, it contains only letters and
        digits. `length` below 4 raises `ValueError`.

        Randomness must come from `secrets` (the tests check you don't import `random`).
        """,
        stub='''
        import secrets
        import string

        def generate(length=16, symbols=True):
            ...
        ''',
        tests='''
        import string
        SYM = "!@#$%&*-_"

        def test_rules(m):
            for n in [4, 5, 8, 16, 40]:
                for sym in (True, False):
                    for _ in range(60):
                        pw = m.generate(n, sym)
                        equal(len(pw), n, "length")
                        check(any(c.islower() for c in pw) and any(c.isupper() for c in pw)
                              and any(c.isdigit() for c in pw), f"missing a character class: {pw!r}")
                        if sym:
                            check(any(c in SYM for c in pw), f"no symbol in {pw!r}")
                            check(all(c.isalnum() or c in SYM for c in pw), f"unexpected character in {pw!r}")
                        else:
                            check(pw.isalnum() and pw.isascii(), f"symbols=False but got {pw!r}")

        def test_varied(m):
            seen = {m.generate() for _ in range(200)}
            equal(len(seen), 200, "200 passwords, all different")
            firsts = {m.generate(8)[0] for _ in range(300)}
            check(len(firsts) > 20, "the first character should vary too (not always a fixed class)")

        def test_too_short(m):
            raises(ValueError, m.generate, 3)

        def test_uses_secrets(m):
            check("random" not in imports(m), "use secrets, not random")
        ''',
        alts={
            "retry until valid": ('''
                import secrets
                import string

                def generate(length=16, symbols=True):
                    if length < 4:
                        raise ValueError("length must be at least 4")
                    classes = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
                    if symbols:
                        classes.append("!@#$%&*-_")
                    alphabet = "".join(classes)
                    while True:
                        pw = "".join(secrets.choice(alphabet) for _ in range(length))
                        if all(any(c in cls for c in pw) for cls in classes):
                            return pw
            ''', "Rejection sampling keeps every valid password equally likely. For short lengths it may "
                 "retry a few times; that's fine."),
            "one from each, then shuffle": ('''
                import secrets
                import string

                def generate(length=16, symbols=True):
                    if length < 4:
                        raise ValueError("length must be at least 4")
                    classes = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
                    if symbols:
                        classes.append("!@#$%&*-_")
                    alphabet = "".join(classes)
                    chars = [secrets.choice(c) for c in classes]
                    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
                    secrets.SystemRandom().shuffle(chars)
                    return "".join(chars)
            ''', "Never loops, but the distribution is slightly skewed towards the small classes. "
                 "SystemRandom gives random's API on top of the OS's secure source."),
        },
    ),
    dict(
        id="13.5", kind="explore", title="URL-safe base64 without padding",
        task="""
        Tokens in URLs usually use base64url **without** the `=` padding. Write:

        - `encode(data: bytes) -> str`: URL-safe alphabet (`-` and `_`), no `=` at the end
        - `decode(text: str) -> bytes`: the inverse (put the padding back before decoding)

        Explore `base64` with `dir()`/`help()` first. How many `=` does a length-n input need?
        """,
        stub='''
        import base64

        def encode(data):
            ...

        def decode(text):
            ...
        ''',
        tests='''
        import random, base64

        def test_round_trip_and_alphabet(m):
            rng = random.Random(9)
            for n in list(range(0, 20)) + [255, 1000]:
                for _ in range(10):
                    data = rng.randbytes(n)
                    s = m.encode(data)
                    check(isinstance(s, str), "encode returns str")
                    check("=" not in s and "+" not in s and "/" not in s, f"not url-safe/unpadded: {s!r}")
                    equal(m.decode(s), data, f"decode(encode(...)) for {n} bytes")

        def test_known_values(m):
            equal(m.encode(b"\\xfb\\xff"), "-_8", "encode(b'\\\\xfb\\\\xff')")
            equal(m.decode("SGk"), b"Hi", "decode('SGk')")
        ''',
        alts={
            "strip and restore": ('''
                import base64

                def encode(data):
                    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

                def decode(text):
                    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
            ''', "-len % 4 is the number of characters needed to reach a multiple of 4 (0, 1 or 2 here)."),
        },
    ),
    dict(
        id="13.6", kind="project", title="Mini-project: expiring signed tokens",
        task="""
        Build the token scheme from the chapter as a small module you could drop into a web app.

        - `issue(claims: dict, key: bytes, ttl: int, now: int) -> str`: a token `payload.tag`, where
          payload is base64url (no padding) of the JSON of `claims` plus `"exp": now + ttl`, and tag is
          base64url HMAC-SHA256 of the payload text.
        - `check(token: str, key: bytes, now: int) -> dict`: returns the claims (without `exp`) if the
          tag is valid and `now < exp`. Raise `ValueError("bad signature")` for a bad/foreign/malformed
          token and `ValueError("expired")` if it has expired. Check the signature **first**.

        `now` is passed in (instead of calling `time.time()`) so the tests control the clock: a design
        trick worth stealing. Then use it: issue a token in one script, verify it in another, with the
        key in an environment variable.
        """,
        stub='''
        import base64
        import hashlib
        import hmac
        import json

        def issue(claims, key, ttl, now):
            ...

        def check(token, key, now):
            ...
        ''',
        tests='''
        import base64, json

        K = b"0123456789abcdef"

        def test_round_trip(m):
            for claims in [{"u": "ana"}, {"u": 42, "role": "admin"}, {}]:
                t = m.issue(claims, K, ttl=60, now=1000)
                equal(m.check(t, K, now=1059), claims, f"claims {claims}")

        def test_expiry(m):
            t = m.issue({"u": "ana"}, K, ttl=60, now=1000)
            e = raises(ValueError, m.check, t, K, 1060)
            check("expired" in str(e), f"message should say expired, got {e}")

        def test_forgery_and_tampering(m):
            t = m.issue({"u": "ana", "role": "student"}, K, ttl=60, now=1000)
            payload, tag = t.split(".")
            forged_body = base64.urlsafe_b64encode(json.dumps({"u": "ana", "role": "admin",
                                                               "exp": 99999}).encode()).rstrip(b"=").decode()
            for bad in [forged_body + "." + tag, payload + "." + tag[::-1], payload, "x.y", ""]:
                e = raises(ValueError, m.check, bad, K, 1001)
                check("signature" in str(e), f"{bad[:20]!r}...: should be a bad signature, got {e}")
            raises(ValueError, m.check, t, b"another key 1234", 1001)

        def test_signature_checked_before_expiry(m):
            t = m.issue({"u": "ana"}, K, ttl=60, now=1000)
            e = raises(ValueError, m.check, t, b"wrong", 5000)
            check("signature" in str(e), "a token with a bad signature must say 'bad signature' even if old")

        def test_format(m):
            t = m.issue({"u": "ana"}, K, ttl=60, now=1000)
            check(t.count(".") == 1 and "=" not in t, f"token should be payload.tag without padding: {t}")
            body = t.split(".")[0]
            data = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
            equal(data, {"u": "ana", "exp": 1060}, "decoded payload")
        ''',
        alts={
            "reference": ('''
                import base64
                import binascii
                import hashlib
                import hmac
                import json

                def _b64(b):
                    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

                def _unb64(s):
                    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

                def _tag(payload, key):
                    return _b64(hmac.new(key, payload.encode(), hashlib.sha256).digest())

                def issue(claims, key, ttl, now):
                    payload = _b64(json.dumps({**claims, "exp": now + ttl}).encode())
                    return f"{payload}.{_tag(payload, key)}"

                def check(token, key, now):
                    payload, dot, tag = token.partition(".")
                    if not dot or not hmac.compare_digest(_tag(payload, key), tag):
                        raise ValueError("bad signature")
                    data = json.loads(_unb64(payload))
                    if now >= data.pop("exp"):
                        raise ValueError("expired")
                    return data
            ''', "{**claims, 'exp': ...} builds a new dict, so the caller's claims aren't modified. Once the "
                 "signature is valid we created the payload, so json.loads can't be fed attacker junk."),
        },
    ),
]

DRILLS = [
    dict(kind="recall", q="Which module makes unguessable tokens?", a=["secrets"]),
    dict(kind="recall", q="Which function compares two MAC tags safely?",
         a=["hmac.compare_digest", "compare_digest", "secrets.compare_digest"]),
    dict(kind="recall", q="Name a stdlib function suitable for hashing passwords.",
         a=["hashlib.scrypt", "scrypt", "hashlib.pbkdf2_hmac", "pbkdf2_hmac", "pbkdf2"]),
    dict(kind="recall", q="Is base64 encryption? (yes/no)", a=["no"]),
    dict(kind="recall", q="Which pip package provides Fernet?", a=["cryptography"]),
    dict(kind="predict", code="import hashlib\nprint(len(hashlib.sha256(b'').hexdigest()), len(hashlib.sha256(b'x' * 10**6).digest()))",
         why="SHA-256 is always 32 bytes = 64 hex characters, whatever the input size."),
    dict(kind="predict", code="import base64\nprint(base64.b64encode(b'abc'), base64.b64encode(b'abcd'))",
         why="3 bytes -> 4 chars exactly; 4 bytes -> 8 chars with == padding."),
    dict(kind="predict", code="import random\nrandom.seed(1); a = random.random()\nrandom.seed(1); b = random.random()\nprint(a == b)",
         why="Same seed, same stream: why random must never make secrets."),
]
