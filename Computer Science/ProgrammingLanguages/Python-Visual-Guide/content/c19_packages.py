"""Chapter 19 - Choosing pip packages safely: what venv and pip do, reading installed metadata, the library
card applied to requests / pytest / cryptography, version specifiers, pins, hashes and lock files, and
supply-chain attacks with the checks that catch them."""
import os
import subprocess
import sys
import tempfile
from importlib.metadata import requires, version

from packaging.requirements import Requirement

from generator import canvas as C
from content.kit import (L, R, W, callout, card, code, flow, pipe, practice, section, shell, stamp, sub, table,
                         title_block, tree, two_ways)

ORDER = 19
NUM = 19
TITLE = "Choosing pip packages safely"
SHORT = "pip packages"
SLUG = "Packages"
ACCENT = C.BROWN


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


# ----------------------------------------------------------------------------- real data
def deps(dist):
    """Direct runtime dependencies of an installed distribution (extras dropped, markers evaluated)."""
    out = []
    for line in requires(dist) or []:
        r = Requirement(line)
        if r.marker and not r.marker.evaluate({"extra": ""}):
            continue
        if r.name not in out:
            out.append(r.name)
    return out


def dep_tree(f, roots):
    """Draw the real dependency tree of `roots` as installed on the machine building the book."""
    nodes, edges = {"app": ("your project", 0.5, 0)}, []
    row2 = []
    for r in roots:
        for d in deps(r):
            row2.append((r, d))
    xs = [0.08 + 0.84 * i / max(1, len(row2) - 1) for i in range(len(row2))]
    for (parent, d), x in zip(row2, xs):
        nodes[d] = (d, x, 2)
        edges.append((parent, d))
        for g in deps(d):
            nodes[g] = (g, x, 3)
            edges.append((d, g))
    for k, r in enumerate(roots):
        kids = [x for (p, _), x in zip(row2, xs) if p == r]
        nodes[r] = (f"{r} {version(r)}", sum(kids) / len(kids) if kids else 0.25 + 0.5 * k, 1)
        edges.append(("app", r))
    tree(f, nodes, edges, size=9, row_h=34, gap=8)


def venv_session():
    """Create a real venv (without pip, so it's fast and offline) and show what's inside."""
    with tempfile.TemporaryDirectory() as d:
        steps = [
            [sys.executable, "-m", "venv", "--without-pip", ".venv"],
            ["ls", ".venv"],
            ["ls", ".venv/bin"],
            ["cat", ".venv/pyvenv.cfg"],
            [".venv/bin/python", "-c", "import sys; print(sys.prefix != sys.base_prefix, sys.prefix)"],
        ]
        shown = ["python3 -m venv .venv", "ls .venv", "ls .venv/bin", "cat .venv/pyvenv.cfg",
                 '.venv/bin/python -c "import sys; print(sys.prefix != sys.base_prefix, sys.prefix)"']
        lines = []
        for cmd, label in zip(steps, shown):
            r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                raise RuntimeError(r.stderr)
            lines.append("$ " + label)
            out = r.stdout.replace(os.path.realpath(d), "~/loans").replace(d, "~/loans")
            out = out.replace("--without-pip ", "")
            lines += [l for l in out.splitlines() if not l.startswith("command =")]
    return "\n".join(lines)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 19, TITLE, "every pip install runs a stranger's code with your permissions", ACCENT)
    f = ch.flow(top=190)
    f.p("The standard library can't do everything: no friendly HTTP client, no symmetric encryption, no "
        "pytest. PyPI has over half a million packages for the rest. Each one you add brings its own "
        "dependencies, all written by people you've never met. Here is what two popular packages pull in, "
        "read from the metadata on the machine that built this page:", 14, gap=10)
    dep_tree(f, ["pandas", "cryptography"])
    code(f, """
        from importlib.metadata import requires
        from packaging.requirements import Requirement

        for line in requires("cryptography")[:4]:
            r = Requirement(line)
            keep = r.marker is None or r.marker.evaluate({"extra": ""})
            print(f"{r.name:18} {str(r.specifier):10} {'needed' if keep else 'skipped'}")
    """, size=8.4, notes={6: "markers: Python version, OS, extras"})
    f.p("This chapter gives you a routine for the four decisions every project makes: {B:whether} to add a "
        "package, {B:which} one, {B:how} to pin it, and how to notice when the supply chain is attacked.",
        13.5, gap=8)
    table(f, ["need", "stdlib first", "the usual package (and why)"], [
        ["HTTP client", "`urllib.request` (Ch 15)", "`requests` / `httpx`: sessions, retries"],
        ["encryption", "hashes + HMAC only (Ch 13)", "`cryptography`: AES-GCM, Fernet"],
        ["tests", "`unittest` (Ch 17)", "`pytest`: `assert`, fixtures, plugins"],
    ], widths=[1.3, 2.4, 3.6], size=10.5)


def venv_section(f):
    sec(f, "What venv and pip actually do", room=430)
    f.p("A {B:virtual environment} is just a folder with its own `site-packages` and a `python` that uses it, so "
        "each project gets its own package versions. Nothing is hidden; look inside one:", 13.5, gap=8)
    shell(f, venv_session(), title="a real venv, created while building this page", size=8.6)
    f.p("(The `πthon` link is real: a joke alias for version 3.14.) `pip install requests` inside it then does "
        "five things, and each one is a place where trust is needed:", 13.5, gap=8)
    pipe(f, [("resolve\nversions", C.GREY), ("download\nfrom PyPI", C.BLUE), ("check\nhash", C.GREEN),
             ("unpack wheel\ninto site-packages", ACCENT), ("record\n.dist-info", C.PURPLE)], h=42,
         under=["picks versions that fit everyone's ranges", "HTTPS", "matches the index (or your lock file)",
                "a wheel is a zip; an sdist may run code to build", "metadata: version, requires, files"])
    code(f, """
        import sys, sysconfig

        print(sys.prefix == sys.base_prefix)            # True: this book runs outside any venv
        print(sysconfig.get_paths()["purelib"])        # where pip would put packages
    """, notes={3: "inside a venv this is False"})
    callout(f, "rule", "One venv per project, never `sudo pip install`, and never install into the system "
            "Python (many Linux distributions now refuse: PEP 668, \"externally managed environment\"). "
            "Commit `pyproject.toml` and the lock file, never the `.venv` folder itself (Ch 17's `.gitignore`).")


def requests_section(f):
    sec(f, "Using a package well: requests", room=430)
    f.p("Apply the Ch 7 method to a third-party package exactly as to a stdlib module. A tiny local API to "
        "talk to (Ch 15's `http.server`), so this page needs no internet:", 13.5, gap=8)
    code(f, """
        import json, threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        class Api(BaseHTTPRequestHandler):
            def do_GET(self):
                found = self.path == "/books/1"
                body = {"title": "Dune"} if found else {"error": "no such book"}
                self.send_response(200 if found else 404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(body).encode())
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Api)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
    """, size=8.4)
    two_ways(f, ("stdlib: urllib (Ch 15)", """
        import json, urllib.request as ur
        from urllib.error import HTTPError
        try:
            r = ur.urlopen(f"{base}/books/9", timeout=5)
            print(json.load(r))
        except HTTPError as e:                # 404 raises
            print(e.code, json.load(e))
    """), ("requests", """
        import requests

        r = requests.get(f"{base}/books/9", timeout=5)
        print(r.status_code, r.json())
    """), ns=f.ch._ns, verdict=[("no install needed", 5, 0), ("reads easily", 2, 5)])
    code(f, """
        import requests
        with requests.Session() as s:                   # keeps connections open between calls
            s.headers["User-Agent"] = "loans/0.3"
            r = s.get(f"{base}/books/1", timeout=5)
            r.raise_for_status()                        # 4xx / 5xx -> requests.HTTPError
            print(r.json(), r.headers["Content-Type"])
            try:
                s.get(f"{base}/books/9", timeout=5).raise_for_status()
            except requests.HTTPError as e:
                print("HTTPError", e.response.status_code)
        server.shutdown()
    """, notes={3: "always pass a timeout: the default is to wait forever"})
    card(f, "requests", {
        "Job": "HTTP client: send requests, get `Response` objects. Sync only (`httpx` adds async).",
        "Core objects": "`requests.get/post(url, params=, json=, headers=, timeout=)` → `Response`: "
                        "`.status_code`, `.json()`, `.text`, `.content`, `.headers`, `.raise_for_status()`. "
                        "`Session()` for many calls to one host.",
        "Lifecycle": "request → response; a `Session` is a context manager (`with`) that pools connections.",
        "Errors": "`requests.RequestException` ← `ConnectionError`, `Timeout`, `HTTPError` (only if you call "
                  "`raise_for_status()`).",
        "Traps": "no default timeout · a 404 is not an exception · `verify=False` disables TLS checks · "
                 "`.json()` on a non-JSON body raises.",
        "Docs": "requests.readthedocs.io · source: github.com/psf/requests",
    }, color=ACCENT)


def pytest_section(f):
    sec(f, "pytest and cryptography: two more cards", room=430)
    f.p("`pytest` runs the same `unittest` suites you already have, and also lets tests be plain functions "
        "using plain `assert`. Fixtures replace `setUp`; `parametrize` replaces `subTest` loops:", 13.5, gap=8)
    code(f, """
        import sqlite3
        import pytest
        from fees import late_fee, DUE, back

        @pytest.mark.parametrize("days, fee", [(-3, 0.0), (0, 0.0), (1, 0.25), (20, 5.0), (90, 5.0)])
        def test_fee(days, fee):
            assert late_fee(DUE, back(days)) == fee        # failures show both values

        @pytest.fixture
        def db():
            conn = sqlite3.connect(":memory:")
            yield conn                                      # the test runs here
            conn.close()                                    # cleanup, even after a failure

        def test_starts_empty(db):                          # asks for the fixture by name
            assert db.execute("SELECT 1").fetchone() == (1,)
    """, run=False, title="test_fees.py")
    shell(f, """
        $ python3 -m pip install pytest
        $ python3 -m pytest -q
        ......                                                                   [100%]
        6 passed in 0.04s
    """, size=8.4)
    card(f, "pytest", {
        "Job": "Find and run tests (`test_*.py`, `test_*` functions, `unittest` classes too); report clearly.",
        "Core objects": "plain `assert` (rewritten to show values) · `@pytest.fixture` · "
                        "`@pytest.mark.parametrize` · `pytest.raises(E)` · built-ins: `tmp_path`, `monkeypatch`, "
                        "`capsys`.",
        "Lifecycle": "collect → set up fixtures → run → tear down (code after `yield`) → report.",
        "Errors": "a failed `assert` = test failure; an exception anywhere else = error; `-x` stops at the first.",
        "Traps": "a file not named `test_*.py` is silently skipped · module-scoped fixtures share state · "
                 "too many plugins make runs mysterious.",
        "Docs": "docs.pytest.org · `pytest --fixtures` lists every fixture available",
    }, color=ACCENT)
    card(f, "cryptography", {
        "Job": "Vetted cryptography: Fernet and AES-GCM encryption, signatures, key exchange, X.509 certificates.",
        "Core objects": "`fernet.Fernet(key)`: `.encrypt`, `.decrypt` (Ch 13). Lower level: "
                        "`hazmat.primitives.ciphers.aead.AESGCM`, `hazmat.primitives.asymmetric.ed25519`.",
        "Lifecycle": "generate or load a key → make the object → encrypt/sign. Keys live outside the code.",
        "Errors": "`InvalidToken` (Fernet), `InvalidTag` (AES-GCM), `InvalidSignature`: tampering or wrong key.",
        "Traps": "`hazmat` means hazardous: wrong nonce reuse breaks AES-GCM completely · never invent your "
                 "own scheme · ships compiled Rust code, so install wheels, not source builds.",
        "Docs": "cryptography.io · the 'recipes' layer first, `hazmat` only when a protocol demands it",
    }, color=ACCENT)


def choosing_section(f):
    sec(f, "Is this package worth trusting?", room=360)
    f.p("Before `pip install`, spend five minutes on the project page and repository. None of these checks is "
        "proof; together they separate a well-run project from a risky one:", 13.5, gap=8)
    table(f, ["check", "good sign", "warning sign"], [
        ["Does the stdlib already do it?", "no, or only painfully", "yes: one dependency less to trust"],
        ["Maintenance", "releases this year, issues answered", "last release years ago, piles of open PRs"],
        ["People", "several maintainers, an organisation", "one anonymous account"],
        ["Users", "widely used, depended on by big projects", "brand new, few downloads, name like a famous one"],
        ["Dependencies", "few, well-known", "dozens for a small job"],
        ["Security", "advisories handled quickly, a SECURITY.md", "no way to report problems"],
        ["Licence", "MIT, BSD, Apache-2.0 (permissive)", "none at all (you may not use it), or GPL in closed code"],
        ["Install", "wheels for your platform", "only an sdist that runs a build script"],
    ], widths=[2.0, 2.6, 2.7], size=10)


def pinning_section(f):
    sec(f, "Version ranges, pins, hashes, lock files", room=430)
    f.p("A dependency line says {B:which versions} you accept. Wide ranges get bug fixes automatically but "
        "can change under you; exact pins are repeatable but go stale. The `packaging` library (what pip "
        "itself uses) shows what each specifier accepts:", 13.5, gap=8)
    code(f, """
        from packaging.specifiers import SpecifierSet
        from packaging.version import Version

        releases = ["2.28.2", "2.31.0", "2.32.3", "2.32.5", "3.0.0"]
        for spec in ["", ">=2.31", "~=2.32.0", ">=2.31,<3", "==2.32.5"]:
            ok = [v for v in releases if Version(v) in SpecifierSet(spec)]
            print(f"{spec or '(any)':10} accepts {ok}")
    """, notes={5: "~=2.32.0 means >=2.32.0 and ==2.32.*"})
    callout(f, "rule", "{B:Libraries} declare ranges in `pyproject.toml` (`requests>=2.31,<3`) so they combine with "
            "other libraries. {B:Applications} also commit a {B:lock file}: every package, direct and indirect, "
            "pinned to an exact version {B:and hash}, so every install is byte-for-byte the same.")
    f.p("A hash pins the exact file, not just the version number: if anyone replaces the file on the server, "
        "the install refuses. The idea in five lines of `hashlib` (Ch 13):", 13.5, gap=8)
    code(f, """
        import hashlib

        wheel = b"PK\\x03\\x04 ... the real wheel's bytes ..."
        pinned = hashlib.sha256(wheel).hexdigest()           # recorded in the lock file
        for blob in (wheel, wheel.replace(b"real", b"evil")):
            print("install" if hashlib.sha256(blob).hexdigest() == pinned else "REFUSE: hash mismatch")
    """)
    shell(f, """
        $ cat requirements.txt
        requests==2.32.5 \\
            --hash=sha256:2462f94637a34fd532264295e186976db0f5d453d1cdd31473c85a6a161affb6
        urllib3==2.6.3 \\
            --hash=sha256:bf272323e553dfb2e87d9bfd225ca7b0f467b919d7bbd355436d3fd37cb0acd4
        $ python3 -m pip install --require-hashes -r requirements.txt
    """, title="what a hashed lock file looks like (hashes illustrative)", size=8.0)
    table(f, ["tool", "writes", "notes"], [
        ["`pip-tools` (`pip-compile`)", "`requirements.txt` with pins and hashes", "small, classic, plain pip underneath"],
        ["`uv`", "`uv.lock`", "very fast; manages venvs and Python versions too"],
        ["Poetry / PDM / Hatch", "their own lock files", "whole project managers"],
        ["the standard: PEP 751", "`pylock.toml`", "one lock format tools are converging on"],
    ], widths=[2.2, 2.6, 2.5], size=10)


def supply_section(f):
    sec(f, "Supply-chain attacks, and the checks that catch them", room=430)
    f.p("Attackers aim at the path between the author and your program. Every stage of an install has a "
        "known attack:", 13.5, gap=8)
    pipe(f, [("you type\nthe name", C.GREY), ("PyPI\nthe index", C.BLUE), ("download", C.GREEN),
             ("install\n(build)", ACCENT), ("import\nand run", C.PURPLE)], h=42, color=C.RED,
         under=["typosquats: reqeusts, python-dateutils", "stolen maintainer account, malicious release",
                "tampered file (HTTPS and hashes stop it)", "an sdist's setup.py runs as you",
                "code runs with all your permissions"])
    code(f, """
        import difflib

        popular = ["requests", "numpy", "pandas", "cryptography", "urllib3", "flask", "pytest"]
        for name in ["reqeusts", "nunpy", "cryptograpy", "requests", "leftpad"]:
            near = difflib.get_close_matches(name, popular, n=1, cutoff=0.8)
            if name in popular:
                verdict = "ok"
            elif near:
                verdict = f"did you mean {near[0]}?"
            else:
                verdict = "unknown: check it"
            print(f"{name:12} {verdict}")
    """, notes={5: "a cheap typosquat alarm (practice 19.5)"})
    shell(f, """
        $ python3 -m pip install pip-audit
        $ pip-audit -r old-requirements.txt
        Found 1 known vulnerability in 1 package
        Name    Version ID                  Fix Versions
        ------- ------- ------------------- ------------
        urllib3 2.2.1   GHSA-34jh-p97f-mpxf 1.26.19,2.2.2
    """, title="a 2024 lock file checked against the PyPI advisory database (OSV)", size=8.4)
    table(f, ["defence", "stops"], [
        ["copy names from the official docs; check the PyPI page", "typosquats, look-alike names"],
        ["lock file with hashes; `--require-hashes`", "swapped files, surprise new versions"],
        ["`pip install --only-binary :all:` where possible", "build scripts running at install time"],
        ["`pip-audit` in CI, then update", "known vulnerabilities (only the known ones)"],
        ["few dependencies; review new ones in code review", "everything above, by shrinking the surface"],
        ["prefer releases with trusted publishing / attestations", "uploads from a stolen password"],
    ], widths=[3.9, 3.0], size=10)
    callout(f, "honest", "No tool proves a package is safe. Audits only know about {B:reported} problems, and a "
            "clean-looking package can turn malicious in its next release. The strongest defence is the boring "
            "one: depend on fewer things, and know why each one is there.")


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 19)
    stamp(f, [
        (8, "`venv` per project; `pip` resolves, downloads, checks hashes and unpacks wheels into "
            "`site-packages`; ranges in `pyproject.toml`, exact pins and hashes in a lock file."),
        (11, "Stdlib: `venv`, `importlib.metadata`, `hashlib`, `difflib`. Third-party staples: `requests`, "
             "`pytest`, `cryptography`, `packaging`, `pip-audit`."),
    ])
    callout(f, "other", "Every ecosystem has the same parts. JavaScript: npm, `package.json` + "
            "`package-lock.json`, and the most famous typosquats. Rust: crates.io, `Cargo.toml` + `Cargo.lock`, "
            "`cargo audit`. Java: Maven Central, `pom.xml`. Go: `go.mod` + `go.sum` (hashes built in). C/C++ "
            "often vendor code by hand, which is a supply chain too.")
    callout(f, "deep", "Vault notes: {b:19.14} Dependency and supply-chain risk · {b:19.28} Vulnerability "
            "management · {b:19.17} Cryptographic hash functions · {b:19.4} Trust and least privilege · "
            "{b:16.28} Reproducible computational environments · {b:12.5} pytest fundamentals · {b:12.6} "
            "Fixtures and lifetime scopes · {b:12.21} Continuous integration.")


def build(ch):
    title_page(ch)
    f = flow(ch)
    venv_section(f)
    requests_section(f)
    pytest_section(f)
    choosing_section(f)
    pinning_section(f)
    supply_section(f)
    finish(ch)
