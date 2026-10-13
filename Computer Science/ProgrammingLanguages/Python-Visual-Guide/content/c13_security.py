"""Chapter 13 - Security primitives: bytes and base64, hashlib, hmac and timing, signed tokens, secrets,
password storage with scrypt, encryption (Fernet, outside the stdlib), TLS with ssl, uuid."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, W, callout, card, code, flow, pipe, practice, repl, section, seq, shell, stamp,
                         sub, table, timeline, title_block, two_ways)

ORDER = 13
NUM = 13
TITLE = "Security primitives"
SHORT = "Security"
SLUG = "Security"
ACCENT = C.RED

try:
    import cryptography  # noqa: F401
    HAVE_CRYPTO = True
except ImportError:
    HAVE_CRYPTO = False


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def title_page(ch):
    title_block(ch, 13, TITLE, "pick the right tool; never invent your own", ACCENT)
    f = ch.flow(top=190)
    f.p("Security code fails silently. A broken sort gives wrong output you'll notice; a broken password "
        "check works perfectly until someone steals the database. So this chapter is less about clever "
        "code and more about {B:choosing the right primitive} and using it exactly as intended.", 14, gap=10)
    f.p("Start every security task with one question: {B:what am I protecting against?}", 14, gap=8)
    table(f, ["I need to...", "use", "module"], [
        ["detect accidental change (a corrupted download)", "a hash", "`hashlib`"],
        ["prove a message came from me and wasn't edited", "a MAC (keyed hash)", "`hmac`"],
        ["store passwords so a stolen database doesn't leak them", "a slow, salted KDF", "`hashlib.scrypt`"],
        ["make an unguessable token, reset link or key", "a CSPRNG", "`secrets`"],
        ["keep data secret (only key holders can read it)", "authenticated encryption", "{R:not in stdlib}: "
         "`cryptography`"],
        ["talk to a server without eavesdroppers", "TLS", "`ssl` (via `urllib`, `http.client`)"],
        ["put bytes in text (JSON, URLs, email)", "an {B:encoding}, not security", "`base64`"],
        ["name things uniquely", "an id, {B:not a secret}", "`uuid`"],
    ], widths=[3.1, 1.8, 1.5])
    callout(f, "rule", "Never design your own crypto (\"I'll XOR it with the key\", \"I'll hash it twice\"). "
            "Even experts get it wrong. Combine well-known primitives in well-known ways, as this chapter "
            "does.")


def b64_picture(f):
    """3 bytes -> 24 bits -> 4 groups of 6 -> 4 characters."""
    data = b"Hi!"
    bits = "".join(f"{b:08b}" for b in data)
    import base64
    enc = base64.b64encode(data).decode()
    cell = 12.5
    y0 = f.reserve(112)
    pg = f.pg
    x0 = L + (W - 24 * cell) / 2
    for i, ch_ in enumerate(data.decode()):
        bx = x0 + i * 8 * cell
        pg.rect(bx, y0, 8 * cell, 18, C.BLUE, 1.0, fillcolor=C.LIGHT[C.BLUE], r=3)
        pg.text(bx + 4 * cell, y0 + 3, f"'{ch_}' = {data[i]}", 9.5, C.BLUE, F.BOLD, align="center")
    for k, b in enumerate(bits):
        bx = x0 + k * cell
        col = (C.GREEN, C.ORANGE, C.PURPLE, C.TEAL)[k // 6]
        pg.rect(bx, y0 + 24, cell, 18, col, 0.7, fillcolor="#ffffff")
        pg.text(bx + cell / 2, y0 + 27, b, 9, C.INK, F.MONO, align="center")
    for g in range(4):
        gx = x0 + g * 6 * cell
        col = (C.GREEN, C.ORANGE, C.PURPLE, C.TEAL)[g]
        val = int(bits[g * 6:(g + 1) * 6], 2)
        pg.rect(gx + 2, y0 + 50, 6 * cell - 4, 18, col, 1.0, fillcolor=C.LIGHT[col], r=3)
        pg.text(gx + 3 * cell, y0 + 53, f"{val}", 9.5, col, F.BOLD, align="center")
        pg.arrow(gx + 3 * cell, y0 + 70, gx + 3 * cell, y0 + 82, col, 1.0, head=4)
        pg.text(gx + 3 * cell, y0 + 85, enc[g], 13, col, F.MONOB, align="center")
    pg.note(x0 + 24 * cell + 10, y0 + 2, "3 bytes", C.GREY, 13)
    pg.note(x0 + 24 * cell + 10, y0 + 24, "24 bits", C.GREY, 13)
    pg.note(x0 + 24 * cell + 10, y0 + 50, "4 × 6 bits", C.GREY, 13)
    pg.note(x0 + 24 * cell + 10, y0 + 82, "4 characters", C.GREY, 13)


def bytes_first(ch):
    f = flow(ch)
    sec(f, "Everything here speaks bytes")
    f.p("Every primitive in this chapter takes and returns `bytes`, not `str`. Text becomes bytes with "
        "`.encode()` (UTF-8 by default); digests and keys come out as raw bytes, which you usually show as "
        "{B:hex} or {B:base64}:", 13.5, gap=8)
    repl(f, """
        >>> import hashlib, base64
        >>> raw = hashlib.sha256("hello".encode()).digest()
        >>> len(raw), raw[:6]
        >>> raw.hex()[:24]
        >>> base64.b64encode(raw)[:16]
    """)
    f.p("{b:Base64} turns any bytes into 64 safe characters (A–Z a–z 0–9 + /), so binary data can travel in "
        "JSON, URLs or email. Every 3 bytes become 4 characters:", 13.5, gap=8)
    b64_picture(f)
    repl(f, """
        >>> base64.b64encode(b"Hi!"), base64.b64encode(b"Hi")
        >>> base64.urlsafe_b64encode(b"\\xfb\\xff"), base64.b64encode(b"\\xfb\\xff")
        >>> base64.b64decode("SGkh")
    """)
    callout(f, "trap", "Base64 is {R:not encryption}. Anyone can decode it in one line, as above. If you "
            "see a \"secret\" stored as base64, it's stored in plain text. Use `urlsafe_b64encode` (- and _ "
            "instead of + and /) for anything that goes in a URL; `=` is padding to a multiple of 4.")


def hashing(ch):
    f = flow(ch)
    sec(f, "hashlib: a fingerprint for data", room=440)
    f.p("A cryptographic hash turns any amount of data into a fixed-size fingerprint. Four properties make "
        "it useful:", 13.5, gap=8)
    table(f, ["property", "means", "so you can"], [
        ["deterministic", "same input → same digest, always, everywhere", "compare files without sending them"],
        ["fixed size", "1 byte or 10 GB → 32 bytes (SHA-256)", "store or index fingerprints cheaply"],
        ["one-way", "can't get the input back from the digest", "publish a digest safely"],
        ["avalanche", "change 1 bit → about half the output bits flip", "spot any edit at all"],
    ], widths=[1.3, 2.7, 2.2])
    code(f, """
        import hashlib

        a = hashlib.sha256(b"transfer 100 to alice").hexdigest()
        b = hashlib.sha256(b"transfer 900 to alice").hexdigest()
        print(a[:32])
        print(b[:32])
        flipped = bin(int(a, 16) ^ int(b, 16)).count("1")
        print(f"{flipped} of 256 bits differ")
    """, notes={4: "one character changed", 7: "count differing bits"})
    f.p("For big files, feed the hash in chunks with `.update()`, so memory use stays tiny however large "
        "the file is:", 13.5, gap=8)
    code(f, """
        with open("big.bin", "wb") as out:
            out.write(b"x" * 5_000_000)

        def file_sha256(path, chunk=64 * 1024):
            h = hashlib.sha256()
            with open(path, "rb") as fh:
                while block := fh.read(chunk):
                    h.update(block)
            return h.hexdigest()

        print(file_sha256("big.bin")[:16], len(hashlib.sha256().digest()), "bytes")
    """, hl=(7, 8), notes={7: "64 KB at a time", 8: "same result as one big call"})
    table(f, ["algorithm", "status"], [
        ["`sha256`, `sha512`, `sha3_256`, `blake2b`", "good for integrity and fingerprints"],
        ["`md5`, `sha1`", "{R:broken} for security (collisions can be manufactured); still fine as a "
         "non-security checksum"],
        ["any of these for passwords", "{R:wrong tool}: they're designed to be fast (next pages)"],
    ], widths=[2.4, 3.6])


def mac(ch):
    f = flow(ch)
    sec(f, "hmac: a hash only the key holder can make", room=440)
    f.p("A plain hash proves nothing about {B:who} made it: an attacker who edits a message just recomputes "
        "the hash. An {B:HMAC} mixes a secret key into the hash, so only someone with the key can produce a "
        "valid tag.", 13.5, gap=8)
    pipe(f, [("message", C.BLUE), ("HMAC-SHA256\nwith secret key", C.PURPLE), ("tag (32 bytes)", C.GREEN)],
         h=42, under=["readable by anyone", "server only", "sent with the message"])
    code(f, """
        import hmac, hashlib

        KEY = b"k3y-from-an-env-variable"
        msg = b"user=42;role=student"
        tag = hmac.new(KEY, msg, hashlib.sha256).hexdigest()

        def valid(msg, tag):
            expected = hmac.new(KEY, msg, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected, tag)

        print(valid(msg, tag))
        print(valid(b"user=42;role=admin", tag))
        print(valid(msg, hashlib.sha256(msg).hexdigest()))
    """, notes={9: "never ==", 12: "edited: False", 13: "no key: can't forge"})
    sub(f, "Why compare_digest and not ==", C.RED)
    f.p("`==` on strings stops at the {B:first differing character}. An attacker who can time thousands of "
        "requests sees that a guess with the right first character takes slightly longer, then works out the "
        "tag one character at a time. `compare_digest` always takes the same time. Say the real tag starts "
        "`7f3`:", 13.5, gap=8)
    f.need(150)
    timeline(f, ["== 'x9..'", "== '7a..'", "== '7f3..'", "compare_digest"], [
        (0, 0, 1, "", C.RED), (1, 0, 2, "1 right", C.ORANGE), (2, 0, 3, "3 right", C.ORANGE),
        (3, 0, 8, "always checks every byte", C.GREEN),
    ], tmax=8, unit="bytes", ticks=[0, 4, 8])
    callout(f, "idea", "A MAC gives {B:integrity + authenticity}, not secrecy. The message is still readable; "
            "it just can't be changed without detection.")


def tokens(ch):
    f = flow(ch)
    sec(f, "Building a signed token", room=470)
    f.p("Put the last two pages together and you have the idea behind login cookies, password-reset links "
        "and JWTs: {B:data + expiry, base64url-encoded, with an HMAC tag}. The server gives it out, the client "
        "hands it back, and the server can trust it without a database lookup.", 13.5, gap=8)
    seq(f, ["browser", "server"], [
        ("browser", "server", "POST /login (password ok)"),
        ("server", "browser", "token = payload.tag", "reply"),
        ("browser", "server", "GET /grades  (sends token)"),
        ("server", "browser", "tag valid and not expired: 200 OK", "reply"),
    ], step=26)
    code(f, """
        import base64, hashlib, hmac, json, time

        KEY = b"server-secret"

        def b64(b: bytes) -> str:
            return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

        def unb64(s: str) -> bytes:
            return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

        def issue(user, ttl, now):
            payload = b64(json.dumps({"u": user, "exp": now + ttl}).encode())
            tag = b64(hmac.digest(KEY, payload.encode(), "sha256"))
            return f"{payload}.{tag}"

        def check(token, now):
            payload, _, tag = token.partition(".")
            good = b64(hmac.digest(KEY, payload.encode(), "sha256"))
            if not hmac.compare_digest(good, tag):
                raise ValueError("bad signature")
            data = json.loads(unb64(payload))
            if now >= data["exp"]:
                raise ValueError("expired")
            return data["u"]

        t = issue("ana", ttl=3600, now=1_000_000)
        print(t)
        print(check(t, now=1_000_100))
        forged = b64(b'{"u": "bob", "exp": 9999999}') + "." + t.split(".")[1]
        for bad, when in [(forged, 1_000_100), (t, 1_004_000)]:
            try:
                check(bad, when)
            except ValueError as e:
                print("refused:", e)
        print(unb64(t.split(".")[0]))
    """, hl=(13, 19, 28), out_max=8)
    callout(f, "trap", "The last line shows the payload is {R:readable by anyone}: signed is not encrypted. "
            "Never put secrets in a token's payload. And always check the signature {B:before} trusting "
            "anything inside, including the expiry.")


def randomness(ch):
    f = flow(ch)
    sec(f, "secrets: randomness an attacker can't predict", room=440)
    f.p("The `random` module is a Mersenne Twister: fast, great for simulations and games, and completely "
        "{B:predictable}. Anyone who sees 624 outputs can compute every future one. Even easier, a seed "
        "reproduces the whole stream:", 13.5, gap=8)
    two_ways(f, ("random: reproducible (bad for secrets)", """
        import random
        random.seed(2026)
        print(random.randint(0, 10**6))
        random.seed(2026)
        print(random.randint(0, 10**6))
    """), ("secrets: from the OS (os.urandom)", """
        import secrets
        a = secrets.randbelow(10**6)
        b = secrets.randbelow(10**6)
        print(a != b or "astronomically rare")
        print(len(secrets.token_bytes(16)))
    """), same_output=False)
    table(f, ["need", "call", "gives"], [
        ["a URL-safe token (reset link, session id)", "`secrets.token_urlsafe(32)`", "43 chars, 256 bits"],
        ["a hex token (API key)", "`secrets.token_hex(16)`", "32 hex chars, 128 bits"],
        ["raw key bytes", "`secrets.token_bytes(32)`", "32 bytes"],
        ["pick from a list (password chars)", "`secrets.choice(seq)`", "one item"],
        ["a number in [0, n)", "`secrets.randbelow(n)`", "an int"],
    ], widths=[2.6, 2.2, 1.5])
    code(f, """
        import secrets, string

        def make_password(n=16):
            alphabet = string.ascii_letters + string.digits + "!@#$%&*-_"
            while True:
                pw = "".join(secrets.choice(alphabet) for _ in range(n))
                if (any(c.islower() for c in pw) and any(c.isupper() for c in pw)
                        and any(c.isdigit() for c in pw)):
                    return pw

        print(len(make_password()), len(secrets.token_urlsafe(32)))
    """, notes={6: "secrets, not random", 7: "retry until every class appears"})
    callout(f, "rule", "{B:If a person or attacker must not guess it, use `secrets`.} Tokens, keys, salts, "
            "one-time codes, temporary passwords. `random` is for everything else.")


def passwords(ch):
    f = flow(ch)
    sec(f, "Storing passwords: salted and deliberately slow", room=470)
    f.p("Assume the database {B:will} be stolen one day. Then the question is how long it takes the "
        "attacker to recover passwords from what you stored. Each step below closes one attack:", 13.5,
        gap=8)
    table(f, ["you store", "attacker does", "verdict"], [
        ["the password", "reads it", "{R:never}"],
        ["`sha256(password)`", "looks it up in a precomputed table, or tries billions per second on a GPU",
         "{R:still broken}"],
        ["`sha256(salt + password)`", "can't use tables (each user has a random salt), but still billions "
         "of guesses per second", "{O:better, not enough}"],
        ["`scrypt(password, salt, n, r, p)`", "each guess costs ~40 ms and 16 MB of memory", "{G:right}"],
    ], widths=[2.1, 3.0, 1.2])
    pipe(f, [("password", C.BLUE), ("+ random salt\n(16 bytes)", C.ORANGE), ("scrypt\nslow + memory-hard",
                                                                                  C.PURPLE),
             ("store: params,\nsalt, hash", C.GREEN)], h=44)
    code(f, """
        import hashlib, hmac, secrets, time

        N, R_, P = 2**14, 8, 1

        def hash_password(pw: str) -> str:
            salt = secrets.token_bytes(16)
            h = hashlib.scrypt(pw.encode(), salt=salt, n=N, r=R_, p=P)
            return f"scrypt${N}${R_}${P}${salt.hex()}${h.hex()}"

        def verify_password(pw: str, stored: str) -> bool:
            _, n, r, p, salt, h = stored.split("$")
            got = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt),
                                 n=int(n), r=int(r), p=int(p))
            return hmac.compare_digest(got.hex(), h)

        t = time.perf_counter()
        s = hash_password("correct horse battery staple")
        ms = (time.perf_counter() - t) * 1000
        print(s[:44] + "...")
        print(verify_password("correct horse battery staple", s),
              verify_password("Tr0ub4dor&3", s))
        print(hash_password("same") != hash_password("same"), f"{ms:.0f} ms per hash")
    """, hl=(6, 7, 14), out_max=5)
    f.p("The parameters are stored {B:with} each hash, so you can raise the cost next year and old hashes "
        "still verify (re-hash them when the user next logs in). `hashlib.pbkdf2_hmac('sha256', pw, salt, "
        "600_000)` is the other stdlib option; `argon2` (a pip package) is the current favourite.", 13.5,
        gap=8)
    callout(f, "trap", "The slowness is the point. 40 ms is nothing for one login and ruinous for an "
            "attacker trying a billion guesses. Don't \"optimise\" it away, and do rate-limit login attempts "
            "too.")


def encryption(ch):
    f = flow(ch)
    sec(f, "Encryption: the one thing the stdlib doesn't do", room=420)
    f.p("To keep data {B:secret} (only key holders can read it) you need encryption, and Python's standard "
        "library deliberately ships none: no AES. The standard answer is the `cryptography` package and its "
        "{B:Fernet} recipe, which bundles AES encryption with an HMAC so tampering is detected too "
        "(\"authenticated encryption\"). It's the first pip package in this course; Chapter 19 covers "
        "choosing and installing packages safely.", 13.5, gap=8)
    shell(f, """
        $ python3 -m venv .venv && source .venv/bin/activate
        $ pip install cryptography
    """)
    code(f, """
        from cryptography.fernet import Fernet, InvalidToken

        key = Fernet.generate_key()          # 32 random bytes, base64: keep it SECRET
        box = Fernet(key)

        token = box.encrypt(b"exam room B12, 09:00")
        print(token[:28], b"...")
        print(box.decrypt(token))

        tampered = token[:-2] + (b"A" if token[-2:-1] != b"A" else b"B") + token[-1:]
        try:
            box.decrypt(tampered)
        except InvalidToken:
            print("tampered: refused")
        try:
            Fernet(Fernet.generate_key()).decrypt(token)
        except InvalidToken:
            print("wrong key: refused")
    """, run=HAVE_CRYPTO, output=None if HAVE_CRYPTO else "(install cryptography to run this)", out_max=5)
    table(f, ["key management question", "sensible default"], [
        ["where does the key live?", "an environment variable or secrets file, {R:never in the source or git}"],
        ["what if it leaks?", "generate a new one and re-encrypt (`MultiFernet` helps rotate)"],
        ["what if it's lost?", "the data is gone. Back keys up separately from the data."],
    ], widths=[2, 4])
    callout(f, "honest", "Most programs don't need encryption code at all. Data in transit is TLS's job "
            "(next page); data at rest is often better handled by disk encryption. Reach for Fernet when "
            "one specific field must stay secret even from someone holding the database file.")


def tls(ch):
    f = flow(ch)
    sec(f, "ssl: TLS, the lock icon", room=380)
    f.p("TLS (what `https://` uses) encrypts the connection {B:and} proves you're talking to the real server, "
        "by checking its certificate against trusted authorities. `ssl.create_default_context()` turns all "
        "the checks on; `urllib.request` and `http.client` use it automatically:", 13.5, gap=8)
    code(f, """
        import ssl
        ctx = ssl.create_default_context()
        print(ctx.verify_mode == ssl.CERT_REQUIRED, ctx.check_hostname)
        print(ctx.minimum_version.name, ssl.OPENSSL_VERSION)
    """)
    callout(f, "trap", "Tutorials \"fix\" certificate errors with `ssl._create_unverified_context()`, "
            "`CERT_NONE` or `verify=False`. That keeps the encryption but {R:drops the identity check}, so "
            "anyone in the middle (café Wi-Fi) can impersonate the server. Fix the real cause (wrong clock, "
            "missing CA bundle, wrong hostname) instead.")
    sub(f, "uuid: unique, but not secret", C.INK)
    repl(f, """
        >>> import uuid
        >>> uuid.uuid4().version, len(str(uuid.uuid4()))
        >>> a, b = uuid.uuid7(), uuid.uuid7()
        >>> a < b
    """)
    f.p("`uuid4` is random, `uuid7` (new in 3.14) starts with a timestamp, so ids sort by creation time, "
        "which databases like. Use them as {B:names}. For anything that grants access, use `secrets`.",
        13.5, gap=8)


def finish(ch):
    f = flow(ch)
    sec(f, "Checklist, card, practice", room=520)
    for t in ["Bytes in, bytes out: `.encode()` text going in; `.hex()` or base64 to display.",
              "Integrity only: `hashlib.sha256`. Integrity + who: `hmac` with a secret key.",
              "Compare secrets with `hmac.compare_digest`, never `==`.",
              "Tokens, salts, keys: `secrets`. Never `random`.",
              "Passwords: `hashlib.scrypt` with a per-user salt; store the parameters.",
              "Secrecy: `cryptography`'s Fernet; the key lives outside the code.",
              "Never disable certificate checks. Signed ≠ encrypted. Base64 ≠ encrypted."]:
        f.bullet(t, 12.5, gap=4)
    f.gap(6)
    card(f, "hashlib · hmac · secrets", {
        "Job": "Fingerprints (`hashlib`), keyed tags (`hmac`), unguessable randomness (`secrets`).",
        "Core objects": "`hashlib.sha256(b)` → hash object: `.update(b)`, `.digest()`, `.hexdigest()`. "
                        "`hmac.new(key, msg, 'sha256')`, `hmac.digest(...)`, `hmac.compare_digest(a, b)`. "
                        "`secrets.token_urlsafe(n)`, `choice`, `randbelow`.",
        "Lifecycle": "new → update... → digest. No closing. Keys come from outside the code.",
        "Errors": "`TypeError` for `str` instead of `bytes`; `ValueError` for unknown algorithms / bad scrypt "
                  "parameters.",
        "Traps": "== on tags (timing) · md5/sha1 · fast hashes for passwords · `random` for tokens · "
                 "thinking base64 or signing hides data.",
        "Docs": "docs.python.org/3/library/{hashlib,hmac,secrets}.html · OWASP Password Storage Cheat Sheet",
    })
    practice(f, 13)
    stamp(f, [
        (11, "Security primitives ship in the stdlib (`hashlib`, `hmac`, `secrets`, `ssl`) except symmetric "
             "encryption, which comes from the `cryptography` package."),
        (5, "`bytes` vs `str` is a hard boundary: crypto, sockets and files in binary mode all speak bytes."),
    ])
    callout(f, "deep", "Vault notes: {b:19.16} Cryptographic objectives and the rule against invention · "
            "{b:19.17} Hash functions · {b:19.18} Message authentication codes · {b:19.19} Symmetric "
            "authenticated encryption · {b:19.21} Password storage · {b:19.22} Cryptographic randomness · "
            "{b:19.23} Key management · {b:5.12} Bytes and the text boundary.")


def build(ch):
    title_page(ch)
    bytes_first(ch)
    hashing(ch)
    mac(ch)
    tokens(ch)
    randomness(ch)
    passwords(ch)
    encryption(ch)
    tls(ch)
    finish(ch)
