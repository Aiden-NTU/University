EXERCISES = [
    dict(
        id="19.1", kind="build", title="Read a requirement line",
        task="""
        Write `parse_requirement(line)` for one line of a `requirements.txt` file. Return a dict:

        - `name`: normalised the PyPI way (PEP 503): lower case, and every run of `-`, `_` or `.` becomes one `-`
        - `extras`: the names inside `[...]`, normalised and sorted (an empty list if there are none)
        - `specs`: a list of `(operator, version)` tuples in the order written; operators are
          `===`, `~=`, `==`, `!=`, `<=`, `>=`, `<`, `>` (an empty list means "any version")
        - `marker`: the text after `;`, stripped, or `None`

        Spaces may appear around any part. A `#` starts a comment. A blank or comment-only line returns
        `None`. Anything else that doesn't fit (`requests=>2`, `requests==`, `requests 2.0`) raises `ValueError`.
        """,
        stub='''
        def parse_requirement(line):
            name, _, version = line.partition("==")
            specs = [("==", version.strip())] if version else []
            return {"name": name.strip(), "extras": [], "specs": specs, "marker": None}
        ''',
        tests='''
        def req(name, extras=(), specs=(), marker=None):
            return {"name": name, "extras": list(extras), "specs": list(specs), "marker": marker}

        def test_simple(m):
            equal(m.parse_requirement("requests==2.32.5"), req("requests", specs=[("==", "2.32.5")]))
            equal(m.parse_requirement("numpy"), req("numpy"), "no version means any version")

        def test_normalise_and_comments(m):
            equal(m.parse_requirement("Python_Dateutil >= 2.8.2, <3  # dates"),
                  req("python-dateutil", specs=[(">=", "2.8.2"), ("<", "3")]))
            equal(m.parse_requirement("zope.interface===5.0"), req("zope-interface", specs=[("===", "5.0")]))
            equal(m.parse_requirement("pkg>=1,!=1.5.*")["specs"], [(">=", "1"), ("!=", "1.5.*")])

        def test_extras_and_marker(m):
            got = m.parse_requirement("cryptography[ssh, Test]~=46.0 ; python_version >= '3.9'")
            equal(got, req("cryptography", ["ssh", "test"], [("~=", "46.0")], "python_version >= '3.9'"))

        def test_blank_lines(m):
            equal(m.parse_requirement(""), None, "blank line")
            equal(m.parse_requirement("   # just a comment"), None, "comment line")

        def test_errors(m):
            for bad in ["requests=>2", "requests==", "requests 2.0", "==1.0"]:
                raises(ValueError, m.parse_requirement, bad)
        ''',
        alts={
            "two regular expressions": ('''
                import re

                NAME = re.compile(r"\\s*([A-Za-z0-9][A-Za-z0-9._-]*)\\s*(?:\\[([^\\]]*)\\])?\\s*(.*)")
                CLAUSE = re.compile(r"(===|~=|==|!=|<=|>=|<|>)\\s*([^\\s,;]+)")

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def parse_requirement(line):
                    line = line.split("#", 1)[0].strip()
                    if not line:
                        return None
                    req, _, marker = line.partition(";")
                    m = NAME.fullmatch(req)
                    if not m:
                        raise ValueError(f"no package name in {line!r}")
                    name, extras, rest = m.groups()
                    specs = []
                    if rest.strip():
                        for clause in rest.split(","):
                            c = CLAUSE.fullmatch(clause.strip())
                            if not c:
                                raise ValueError(f"bad version clause {clause.strip()!r}")
                            specs.append(c.groups())
                    extras = sorted(norm(e.strip()) for e in (extras or "").split(",") if e.strip())
                    return {"name": norm(name), "extras": extras, "specs": specs, "marker": marker.strip() or None}
            ''', "One pattern for the name and extras, one for each comma-separated clause. The operator "
                 "alternatives are ordered longest first (=== before ==, <= before <), because a regex takes the "
                 "first alternative that matches."),
            "a hand-written scanner": ('''
                import re
                import string

                OPS = ("===", "~=", "==", "!=", "<=", ">=", "<", ">")
                NAME_CHARS = set(string.ascii_letters + string.digits + "._-")

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def parse_requirement(line):
                    line = line.split("#", 1)[0].strip()
                    if not line:
                        return None
                    req, _, marker = line.partition(";")
                    req = req.strip()
                    i = 0
                    while i < len(req) and req[i] in NAME_CHARS:
                        i += 1
                    name, rest = req[:i], req[i:].strip()
                    if not name:
                        raise ValueError(f"no package name in {line!r}")
                    extras = []
                    if rest.startswith("["):
                        inside, close, rest = rest[1:].partition("]")
                        if not close:
                            raise ValueError("unclosed [")
                        extras = sorted(norm(e.strip()) for e in inside.split(",") if e.strip())
                        rest = rest.strip()
                    specs = []
                    if rest:
                        for clause in rest.split(","):
                            clause = clause.strip()
                            op = next((o for o in OPS if clause.startswith(o)), None)
                            version = clause[len(op):].strip() if op else ""
                            if not version or " " in version:
                                raise ValueError(f"bad version clause {clause!r}")
                            specs.append((op, version))
                    return {"name": norm(name), "extras": extras, "specs": specs, "marker": marker.strip() or None}
            ''', "No regex: walk the name characters, then peel off the extras with partition. Longer, but every "
                 "error has an obvious place to be raised, which is how real parsers (and tokenizers in any "
                 "language) are written."),
        },
    ),
    dict(
        id="19.2", kind="fix", title="Does this version satisfy the specifier?",
        task="""
        `satisfies(version, spec)` should answer whether a version like `"2.32.5"` is allowed by a specifier like
        `">=2.31,<3"`. Versions are dot-separated whole numbers, compared **as numbers**, with missing parts
        counting as 0 (`2.0 == 2`). Clauses are joined by commas and all must hold; an empty spec allows anything.

        - `==`, `!=`, `<`, `<=`, `>`, `>=` compare numerically
        - `==X.Y.*` and `!=X.Y.*` match by prefix (`2.32.7` matches `==2.32.*`)
        - `~=X.Y` means `>=X.Y` and the same version with the last part dropped: `~=2.32` is `>=2.32, ==2.*`,
          and `~=2.32.0` is `>=2.32.0, ==2.32.*`. It needs at least two parts.
        - `===` compares the strings exactly

        Raise `ValueError` for an unknown operator, `~=` with one part, or `.*` after an ordering operator.
        The stub compares strings, so `"2.10" < "2.9"`. Find that and the other bugs.
        """,
        stub='''
        def satisfies(version, spec):
            for clause in spec.split(","):
                clause = clause.strip()
                for op in ("==", "!=", ">=", "<=", ">", "<", "~="):
                    if clause.startswith(op):
                        target = clause[len(op):]
                        break
                if op == "==" and version != target:
                    return False
                if op == "!=" and version == target:
                    return False
                if op == ">=" and version < target:
                    return False
                if op == "<=" and version > target:
                    return False
                if op == ">" and version <= target:
                    return False
                if op == "<" and version >= target:
                    return False
                if op == "~=" and not version.startswith(target):
                    return False
            return True
        ''',
        tests='''
        import random

        def ref(version, spec):
            def nums(s):
                return [int(p) for p in s.split(".")]

            def pad(a, n):
                return a + [0] * (n - len(a))

            v = nums(version)
            for clause in [c.strip() for c in spec.split(",") if c.strip()]:
                op = next(o for o in ("===", "~=", "==", "!=", "<=", ">=", "<", ">") if clause.startswith(o))
                t = clause[len(op):].strip()
                if op == "===":
                    ok = version == t
                elif t.endswith(".*"):
                    p = nums(t[:-2])
                    ok = pad(v, len(p))[:len(p)] == p
                    ok = ok if op == "==" else not ok
                else:
                    tt = nums(t)
                    n = max(len(v), len(tt))
                    a, b = pad(v, n), pad(tt, n)
                    if op == "~=":
                        ok = a >= b and pad(v, len(tt))[:len(tt) - 1] == tt[:-1]
                    else:
                        ok = {"==": a == b, "!=": a != b, "<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op]
                if not ok:
                    return False
            return True

        CASES = [
            ("2.10.0", ">2.9", True), ("10.0", "<9.9", False), ("2.0", "==2", True), ("1.0", "<=1.0.0", True),
            ("2.32.5", "", True), ("2.31.0", ">=2.31,<3", True), ("3.0.0", ">=2.31,<3", False),
            ("2.32.7", "==2.32.*", True), ("2.33", "==2.32.*", False), ("2", "==2.0.*", True),
            ("1.5.3", ">=1,!=1.5.*", False), ("1.6", ">=1,!=1.5.*", True),
            ("2.32.5", "~=2.32.0", True), ("2.33.0", "~=2.32.0", False), ("2.33", "~=2.32", True),
            ("3.0", "~=2.32", False), ("2.31", "~=2.32", False), ("1.0", "===1.0", True), ("1.0", "===1", False),
        ]

        def test_table(m):
            for version, spec, want in CASES:
                equal(m.satisfies(version, spec), want, f"satisfies({version!r}, {spec!r})")

        def test_random(m):
            rng = random.Random(19)
            def ver(k):
                return ".".join(str(rng.randint(0, 11)) for _ in range(k))
            for _ in range(400):
                version = ver(rng.randint(1, 3))
                op = rng.choice(["==", "!=", "<", "<=", ">", ">=", "~=", "==*", "!=*"])
                if op.endswith("*"):
                    clause = f"{op[:-1]}{ver(rng.randint(1, 2))}.*"
                else:
                    clause = f"{op} {ver(rng.randint(2, 3))}"
                spec = clause if rng.random() < 0.6 else f"{clause}, >={ver(1)}"
                equal(m.satisfies(version, spec), ref(version, spec), f"satisfies({version!r}, {spec!r})")

        def test_errors(m):
            for bad in ["~=2", "=>2", ">=2.*", "==abc"]:
                raises(ValueError, m.satisfies, "2.0", bad)
        ''',
        alts={
            "pad to equal length, then compare lists": ('''
                OPS = ("===", "~=", "==", "!=", "<=", ">=", "<", ">")

                def nums(s):
                    return [int(p) for p in s.split(".")]

                def pad(a, n):
                    return a + [0] * (n - len(a))

                def clause_ok(version, clause):
                    op = next((o for o in OPS if clause.startswith(o)), None)
                    if op is None:
                        raise ValueError(f"unknown operator in {clause!r}")
                    target = clause[len(op):].strip()
                    if op == "===":
                        return version == target
                    v = nums(version)
                    if target.endswith(".*"):
                        if op not in ("==", "!="):
                            raise ValueError(f".* only works with == and !=: {clause!r}")
                        prefix = nums(target[:-2])
                        return (pad(v, len(prefix))[:len(prefix)] == prefix) == (op == "==")
                    t = nums(target)
                    n = max(len(v), len(t))
                    a, b = pad(v, n), pad(t, n)
                    if op == "~=":
                        if len(t) < 2:
                            raise ValueError("~= needs at least two parts")
                        return a >= b and pad(v, len(t))[:len(t) - 1] == t[:-1]
                    return {"==": a == b, "!=": a != b, "<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b}[op]

                def satisfies(version, spec):
                    return all(clause_ok(version, c.strip()) for c in spec.split(",") if c.strip())
            ''', "Lists of ints compare element by element, exactly like version numbers, once both are padded "
                 "to the same length. int() raises ValueError on 'abc' for free. all() over a generator stops "
                 "at the first failing clause."),
            "a Version class with total_ordering": ('''
                import functools
                import operator

                @functools.total_ordering
                class Version:
                    def __init__(self, text):
                        self.parts = [int(p) for p in text.split(".")]

                    def _key(self, n):
                        return self.parts + [0] * (n - len(self.parts))

                    def __eq__(self, other):
                        n = max(len(self.parts), len(other.parts))
                        return self._key(n) == other._key(n)

                    def __lt__(self, other):
                        n = max(len(self.parts), len(other.parts))
                        return self._key(n) < other._key(n)

                    def startswith(self, prefix):
                        return self._key(len(prefix.parts))[:len(prefix.parts)] == prefix.parts

                COMPARE = {"==": operator.eq, "!=": operator.ne, "<=": operator.le,
                           ">=": operator.ge, "<": operator.lt, ">": operator.gt}

                def satisfies(version, spec):
                    v = Version(version)
                    for clause in filter(None, (c.strip() for c in spec.split(","))):
                        op = next((o for o in ("===", "~=", *COMPARE) if clause.startswith(o)), None)
                        if op is None:
                            raise ValueError(f"unknown operator in {clause!r}")
                        target = clause[len(op):].strip()
                        if op == "===":
                            ok = version == target
                        elif target.endswith(".*"):
                            if op not in ("==", "!="):
                                raise ValueError(".* only works with == and !=")
                            ok = v.startswith(Version(target[:-2])) == (op == "==")
                        elif op == "~=":
                            t = Version(target)
                            if len(t.parts) < 2:
                                raise ValueError("~= needs at least two parts")
                            ok = v >= t and v.startswith(Version(".".join(map(str, t.parts[:-1]))))
                        else:
                            ok = COMPARE[op](v, Version(target))
                        if not ok:
                            return False
                    return True
            ''', "Teach the type to compare itself (Ch 5's data model): define == and <, and total_ordering "
                 "fills in <=, >, >=. Then the operator module maps the text '>=' to the function ge. This is "
                 "roughly what packaging.version.Version does, with pre-releases on top."),
        },
    ),
    dict(
        id="19.3", kind="build", title="Check downloads against a hashed lock file",
        task=r"""
        Write `verify_lock(lock_text, files)`. `lock_text` is a pip-style lock file: one requirement per entry,
        written without spaces (`requests==2.32.5`), followed by `--hash=sha256:HEX` options. A line ending in
        `\` continues on the next line; `#` starts a comment. `files` maps `"name==version"` (name normalised
        as in 19.1) to the downloaded bytes. Return a **sorted** list of problems:

        - `"unpinned: NAME"`: the entry has no `==` pin
        - `"no hash: NAME"`: pinned, but no sha256 hash (other algorithms don't count)
        - `"missing file: NAME==VERSION"`: pinned and hashed, but not in `files`
        - `"mismatch: NAME==VERSION"`: the file's sha256 matches none of the listed hashes
        - `"not in lock: KEY"`: a key of `files` that no pinned entry mentions

        Names in problems are normalised. A clean lock returns `[]`.
        """,
        stub='''
        import hashlib

        def verify_lock(lock_text, files):
            problems = []
            # 1. join continued lines, 2. read each requirement and its --hash options,
            # 3. compare with files, 4. report files the lock never mentions
            return sorted(problems)
        ''',
        tests=r'''
        import hashlib

        def h(data):
            return hashlib.sha256(data).hexdigest()

        FILES = {"requests==2.32.5": b"requests 2.32.5 wheel", "urllib3==2.6.3": b"urllib3 2.6.3 wheel",
                 "charset-normalizer==3.4.0": b"charset-normalizer wheel"}

        def good_lock():
            return (
                "# generated by pip-compile\n"
                f"requests==2.32.5 \\\n    --hash=sha256:{h(FILES['requests==2.32.5'])}\n"
                f"urllib3==2.6.3 --hash=sha256:{'0' * 64} --hash=sha256:{h(FILES['urllib3==2.6.3'])}\n"
                f"Charset_Normalizer==3.4.0 \\\n    --hash=sha256:{h(FILES['charset-normalizer==3.4.0'])}  # via requests\n"
            )

        def test_clean(m):
            equal(m.verify_lock(good_lock(), dict(FILES)), [], "a clean lock")

        def test_tampered_file(m):
            files = dict(FILES, **{"requests==2.32.5": b"requests 2.32.5 wheel + a backdoor"})
            equal(m.verify_lock(good_lock(), files), ["mismatch: requests==2.32.5"])

        def test_unpinned_and_unhashed(m):
            lock = good_lock() + "Flask>=3\nidna==3.10\nsix==1.17.0 --hash=md5:0cc175b9c0f1b6a831c399e269772661\n"
            files = dict(FILES, **{"idna==3.10": b"idna", "six==1.17.0": b"six"})
            equal(m.verify_lock(lock, files), ["no hash: idna", "no hash: six", "unpinned: flask"])

        def test_missing_and_extra(m):
            files = dict(FILES, **{"evil==1.0": b"surprise"})
            del files["urllib3==2.6.3"]
            equal(m.verify_lock(good_lock(), files), ["missing file: urllib3==2.6.3", "not in lock: evil==1.0"])
        ''',
        alts={
            "join lines, then one entry per line": (r'''
                import hashlib
                import re

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def verify_lock(lock_text, files):
                    problems, mentioned = [], set()
                    for line in lock_text.replace("\\\n", " ").splitlines():
                        tokens = line.split("#", 1)[0].split()
                        if not tokens:
                            continue
                        req, opts = tokens[0], tokens[1:]
                        name = norm(re.match(r"[A-Za-z0-9._-]+", req).group())
                        if "==" not in req:
                            problems.append(f"unpinned: {name}")
                            continue
                        key = f"{name}=={req.split('==', 1)[1]}"
                        mentioned.add(key)
                        hashes = {o.removeprefix("--hash=sha256:") for o in opts if o.startswith("--hash=sha256:")}
                        if not hashes:
                            problems.append(f"no hash: {name}")
                        elif key not in files:
                            problems.append(f"missing file: {key}")
                        elif hashlib.sha256(files[key]).hexdigest() not in hashes:
                            problems.append(f"mismatch: {key}")
                    problems += [f"not in lock: {k}" for k in files if k not in mentioned]
                    return sorted(problems)
            ''', "Replacing backslash-newline with a space turns every entry into one line, so the rest is a "
                 "plain loop. Collecting the hashes in a set makes 'matches any of them' a single `in`."),
            "a token stream": (r'''
                import hashlib
                import re

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def entries(text):
                    """Yield [requirement, set of sha256 hashes]: a token not starting with - begins a new entry."""
                    current = None
                    for line in text.splitlines():
                        for tok in line.split("#", 1)[0].split():
                            if tok == "\\":
                                continue
                            if tok.startswith("--hash="):
                                algo, _, digest = tok[len("--hash="):].partition(":")
                                if algo == "sha256" and current:
                                    current[1].add(digest)
                            elif not tok.startswith("-"):
                                if current:
                                    yield current
                                current = [tok, set()]
                    if current:
                        yield current

                def verify_lock(lock_text, files):
                    problems, mentioned = [], set()
                    for req, hashes in entries(lock_text):
                        name, pinned, version = req.partition("==")
                        name = norm(re.match(r"[A-Za-z0-9._-]+", name).group())
                        if not pinned:
                            problems.append(f"unpinned: {name}")
                            continue
                        key = f"{name}=={version}"
                        mentioned.add(key)
                        if not hashes:
                            problems.append(f"no hash: {name}")
                        elif key not in files:
                            problems.append(f"missing file: {key}")
                        elif hashlib.sha256(files[key]).hexdigest() not in hashes:
                            problems.append(f"mismatch: {key}")
                    return sorted(problems + [f"not in lock: {k}" for k in files.keys() - mentioned])
            ''', "Ignore lines altogether: read tokens, and let each requirement token start a new entry that "
                 "later --hash tokens attach to. A generator keeps the parsing apart from the checking, and "
                 "files.keys() - mentioned is a set difference."),
        },
    ),
    dict(
        id="19.4", kind="explore", title="Explore importlib.metadata: what is installed, and what does it need?",
        task="""
        Explore `importlib.metadata` in the REPL first (`help`, `dir`, then try `version`, `requires`,
        `distributions`, and what happens for a package that isn't installed). Then write:

        - `installed_version(name)`: the installed version string, or `None` if the package isn't installed.
        - `dependency_tree(name, get_requires=None)`: a nested dict `{dependency: its own tree}`.
          `get_requires(name)` returns a list of requirement strings like `importlib.metadata.requires` does,
          or `None`; when it isn't given, use the real installed metadata (and treat a missing package as
          having no dependencies). Call it with **normalised** names (19.1). Skip requirements whose marker
          mentions `extra` (optional features); keep the rest. If a dependency is already on the path from the
          root (a cycle), give it an empty dict and don't go further.
        """,
        stub='''
        import importlib.metadata as md

        def installed_version(name):
            ...

        def dependency_tree(name, get_requires=None):
            ...
        ''',
        tests='''
        import importlib.metadata as md

        GRAPH = {
            "app": ["Flask>=3", "requests[socks]>=2 ; python_version >= '3.8'", "pytest ; extra == 'test'"],
            "flask": ["Werkzeug>=3", "click", "itsdangerous", "blinker"],
            "werkzeug": ["MarkupSafe>=2.1"],
            "requests": ["urllib3<3,>=1.21.1", "idna", "charset_normalizer"],
            "a": ["b"],
            "b": ["a", "c"],
        }

        def test_tree(m):
            calls = []
            def get(name):
                calls.append(name)
                return GRAPH.get(name)
            want = {
                "flask": {"werkzeug": {"markupsafe": {}}, "click": {}, "itsdangerous": {}, "blinker": {}},
                "requests": {"urllib3": {}, "idna": {}, "charset-normalizer": {}},
            }
            equal(m.dependency_tree("app", get), want, "tree for app")
            check(all(c == c.lower() and "_" not in c for c in calls), f"look names up normalised, not {calls}")

        def test_cycle(m):
            equal(m.dependency_tree("a", GRAPH.get), {"b": {"a": {}, "c": {}}},
                  "a cycle stops where a name repeats on the path")

        def test_root_name_normalised(m):
            equal(m.dependency_tree("Flask", GRAPH.get).get("werkzeug"), {"markupsafe": {}}, "tree for 'Flask'")

        def test_installed_version(m):
            equal(m.installed_version("no-such-package-zz9"), None, "a package that isn't installed")
            for d in md.distributions():
                name = d.metadata["Name"]
                equal(m.installed_version(name), md.version(name), name)
                break

        def test_real_metadata(m):
            equal(m.dependency_tree("no-such-package-zz9"), {}, "an uninstalled package has no known dependencies")
            leaf = next((d.metadata["Name"] for d in md.distributions() if not d.requires), None)
            if leaf:
                equal(m.dependency_tree(leaf), {}, f"{leaf} declares no dependencies")
        ''',
        alts={
            "recursion with the path as a set": ('''
                import importlib.metadata as md
                import re

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def installed_version(name):
                    try:
                        return md.version(name)
                    except md.PackageNotFoundError:
                        return None

                def real_requires(name):
                    try:
                        return md.requires(name)
                    except md.PackageNotFoundError:
                        return None

                def dependency_tree(name, get_requires=None):
                    get = get_requires or real_requires

                    def walk(pkg, path):
                        tree = {}
                        for line in get(pkg) or []:
                            req, _, marker = line.partition(";")
                            if "extra" in marker:
                                continue
                            dep = norm(re.match(r"\\s*([A-Za-z0-9._-]+)", req).group(1))
                            tree[dep] = {} if dep in path else walk(dep, path | {dep})
                        return tree

                    root = norm(name)
                    return walk(root, {root})
            ''', "PackageNotFoundError is how importlib.metadata says 'not installed' (it subclasses "
                 "ModuleNotFoundError). The path set only holds the ancestors of the current node, so a package "
                 "shared by two branches (a diamond) still appears under both; only a true cycle is cut."),
            "an explicit stack instead of recursion": ('''
                import importlib.metadata as md
                import re

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def installed_version(name):
                    try:
                        return md.distribution(name).version
                    except md.PackageNotFoundError:
                        return None

                def dependency_tree(name, get_requires=None):
                    def real(pkg):
                        try:
                            return md.distribution(pkg).requires
                        except md.PackageNotFoundError:
                            return None

                    get = get_requires or real
                    root, start = {}, norm(name)
                    stack = [(start, root, (start,))]
                    while stack:
                        pkg, node, path = stack.pop()
                        for line in get(pkg) or []:
                            req, _, marker = line.partition(";")
                            dep = norm(re.split(r"[\\s\\[<>=!~(]", req.strip(), maxsplit=1)[0])
                            if "extra" in marker or dep in node:
                                continue
                            node[dep] = {}
                            if dep not in path:
                                stack.append((dep, node[dep], path + (dep,)))
                    return root
            ''', "Each stack item carries the dict to fill and its own path, so no recursion limit applies to "
                 "deep trees. md.distribution(name) returns one object with .version, .requires, .files and "
                 ".metadata: one lookup, several answers."),
        },
    ),
    dict(
        id="19.5", kind="fix", title="A typosquat alarm that knows its names",
        task="""
        `suspicious(name, popular)` should return the popular package that `name` looks like a typo of, or
        `None`. The rules:

        - Compare **normalised** names (19.1): `Requests` and `python_dateutil` *are* the popular packages.
        - Use `distance(a, b)`, the optimal string alignment distance: insert, delete, replace, or swap two
          neighbouring letters, each costing 1, and no part edited twice (so `distance("ca", "abc") == 3`).
        - A name of up to 5 characters may be 1 edit away; longer names up to 2.
        - Return the **closest** popular name; on a tie, the one listed first.

        The stub has a distance that ignores swaps, skips normalisation, and returns the first match, not the
        closest.
        """,
        stub='''
        def distance(a, b):
            prev = list(range(len(b) + 1))
            for i, ca in enumerate(a, 1):
                cur = [i]
                for j, cb in enumerate(b, 1):
                    cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
                prev = cur
            return prev[-1]

        def suspicious(name, popular):
            limit = 1 if len(name) <= 5 else 2
            for p in popular:
                if name == p:
                    return None
                if distance(name, p) <= limit:
                    return p
            return None
        ''',
        tests='''
        POPULAR = ["requests", "numpy", "pandas", "cryptography", "urllib3", "python-dateutil", "flask"]

        def test_distance(m):
            for a, b, want in [("ab", "ba", 1), ("kitten", "sitting", 3), ("", "abc", 3), ("ca", "abc", 3),
                               ("numpy", "nupmy", 1), ("same", "same", 0)]:
                equal(m.distance(a, b), want, f"distance({a!r}, {b!r})")

        def test_real_names_are_fine(m):
            for name in ["requests", "Requests", "python_dateutil", "Python.Dateutil", "FLASK"]:
                equal(m.suspicious(name, POPULAR), None, name)

        def test_typos(m):
            for name, want in [("reqeusts", "requests"), ("urlib3", "urllib3"), ("crytpography", "cryptography"),
                               ("numpyy", "numpy"), ("Reqests", "requests"), ("nupmy", "numpy"), ("falsk", "flask")]:
                equal(m.suspicious(name, POPULAR), want, name)

        def test_closest_wins(m):
            equal(m.suspicious("pandoz", ["pandas", "pandoc"]), "pandoc", "pandoz: 2 edits from pandas, 1 from pandoc")
            equal(m.suspicious("numby", ["numpy", "numba"]), "numpy", "a tie goes to the first popular name")

        def test_unrelated(m):
            for name in ["leftpad", "django", "httpx", "attrs", "nump"]:
                want = "numpy" if name == "nump" else None
                equal(m.suspicious(name, POPULAR), want, name)
        ''',
        alts={
            "full table with a swap step": ('''
                import re

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def distance(a, b):
                    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
                    for i in range(len(a) + 1):
                        d[i][0] = i
                    for j in range(len(b) + 1):
                        d[0][j] = j
                    for i in range(1, len(a) + 1):
                        for j in range(1, len(b) + 1):
                            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
                            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
                    return d[-1][-1]

                def suspicious(name, popular):
                    n = norm(name)
                    if n in {norm(p) for p in popular}:
                        return None
                    limit = 1 if len(n) <= 5 else 2
                    best, best_d = None, limit + 1
                    for p in popular:
                        dist = distance(n, norm(p))
                        if dist < best_d:
                            best, best_d = p, dist
                    return best
            ''', "The table d[i][j] is the cost of turning a[:i] into b[:j]; the swap step looks two cells back "
                 "diagonally. Starting best_d at limit + 1 means 'too far' needs no special case, and a strict < "
                 "keeps the first of any tie (the same dynamic programming returns in Ch 21)."),
            "memoised recursion and min()": ('''
                import re
                from functools import lru_cache

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def distance(a, b):
                    @lru_cache(maxsize=None)
                    def d(i, j):
                        if i == 0 or j == 0:
                            return i + j
                        best = min(d(i - 1, j) + 1, d(i, j - 1) + 1, d(i - 1, j - 1) + (a[i - 1] != b[j - 1]))
                        if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                            best = min(best, d(i - 2, j - 2) + 1)
                        return best
                    return d(len(a), len(b))

                def suspicious(name, popular):
                    n = norm(name)
                    if any(norm(p) == n for p in popular):
                        return None
                    scored = [(distance(n, norm(p)), p) for p in popular]
                    best = min(scored, key=lambda s: s[0], default=None)
                    limit = 1 if len(n) <= 5 else 2
                    return best[1] if best and best[0] <= limit else None
            ''', "The same recurrence written top-down: lru_cache remembers each (i, j), so it does the same "
                 "work as the table. min() with a key returns the first smallest item, which is the tie rule."),
        },
    ),
    dict(
        id="19.6", kind="project", title="Mini pip-audit",
        task=r"""
        Build a small vulnerability checker in one module.

        - `audit(requirements_text, advisories)`: `requirements_text` is a requirements file (comments, blank
          lines, `\` continuations, `--hash` options, extras and `; markers` may appear; each requirement is
          written without spaces). `advisories` is a list of dicts
          `{"id", "package", "affected", "fixed"}` where `affected` is a specifier like `">=2.0,<2.2.2"` using
          `== != < <= > >=` and `fixed` may be `None`. Return findings as tuples
          `(name, version, advisory_id, fixed)`, names normalised, sorted by name then id. An unpinned
          requirement can't be audited: report it as `(name, None, "UNPINNED", None)`.
        - `main(argv)`:           `argv` is `[requirements_path, advisories_json_path]`. Print one line per finding (the
          name, and the advisory id if there is one), or `no known vulnerabilities`. Return 1 if there were
          findings, else 0, so it can fail a CI job.

        Reuse your ideas from 19.1 and 19.2: versions compare as numbers.
        """,
        stub='''
        import json

        def audit(requirements_text, advisories):
            ...

        def main(argv):
            ...
        ''',
        tests=r'''
        import json
        import os

        ADVISORIES = [
            {"id": "DEMO-0001", "package": "urllib3", "affected": ">=2.0,<2.2.2", "fixed": "2.2.2"},
            {"id": "DEMO-0002", "package": "Jinja2", "affected": "<3.1.3", "fixed": "3.1.3"},
            {"id": "DEMO-0003", "package": "requests", "affected": "<2.32.0", "fixed": "2.32.0"},
            {"id": "DEMO-0004", "package": "left_pad", "affected": ">=0", "fixed": None},
            {"id": "DEMO-0005", "package": "urllib3", "affected": "<2.2.2,!=2.2.1", "fixed": "2.2.2"},
        ]

        REQS = (
            "# pinned in 2024\n"
            "requests==2.31.0 \\\n    --hash=sha256:" + "a" * 64 + "\n"
            "urllib3==2.2.1 --hash=sha256:" + "b" * 64 + "\n"
            "jinja2==3.1.4\n"
            "Flask>=3\n"
            "idna==3.10  # fine\n"
        )

        WANT = [("flask", None, "UNPINNED", None), ("requests", "2.31.0", "DEMO-0003", "2.32.0"),
                ("urllib3", "2.2.1", "DEMO-0001", "2.2.2")]

        def test_audit(m):
            equal(m.audit(REQS, ADVISORIES), WANT)

        def test_numbers_not_strings(m):
            equal(m.audit("urllib3==2.10.0\n", [{"id": "X", "package": "urllib3", "affected": "<2.9", "fixed": "2.9"}]),
                  [], "2.10.0 is newer than 2.9")
            equal(m.audit("pkg==2\n", [{"id": "Y", "package": "pkg", "affected": "==2.0", "fixed": None}]),
                  [("pkg", "2", "Y", None)], "2 == 2.0")

        def test_names_extras_markers(m):
            text = "Left.Pad==1.0\nrequests[socks]==2.0.0 ; python_version >= '3.8'\nJINJA2==3.0\n"
            equal(m.audit(text, ADVISORIES), [("jinja2", "3.0", "DEMO-0002", "3.1.3"),
                                               ("left-pad", "1.0", "DEMO-0004", None),
                                               ("requests", "2.0.0", "DEMO-0003", "2.32.0")])

        def test_main(m):
            with tmpdir() as d:
                with open("requirements.txt", "w") as fh:
                    fh.write(REQS)
                with open("advisories.json", "w") as fh:
                    json.dump(ADVISORIES, fh)
                code, out = capture(m.main, ["requirements.txt", "advisories.json"])
                equal(code, 1, "exit code with findings")
                for name, version, adv, _ in WANT:
                    shown = name in out.lower() and (version is None or adv in out)
                    check(shown, f"{name} / {adv} missing from the output:\n{out}")
                with open("clean.txt", "w") as fh:
                    fh.write("idna==3.10\nrequests==2.32.5\n")
                code, out = capture(m.main, ["clean.txt", "advisories.json"])
                equal(code, 0, "exit code when clean")
                check("no known vulnerabilities" in out, f"clean output was:\n{out}")
        ''',
        alts={
            "small functions, padded lists": (r'''
                import json
                import re

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def nums(s):
                    return [int(p) for p in s.split(".")]

                def satisfies(version, spec):
                    v = nums(version)
                    for clause in filter(None, (c.strip() for c in spec.split(","))):
                        op, target = re.fullmatch(r"(==|!=|<=|>=|<|>)\s*(.+)", clause).groups()
                        t = nums(target)
                        n = max(len(v), len(t))
                        a, b = v + [0] * (n - len(v)), t + [0] * (n - len(t))
                        ok = {"==": a == b, "!=": a != b, "<=": a <= b, ">=": a >= b, "<": a < b, ">": a > b}[op]
                        if not ok:
                            return False
                    return True

                def pins(text):
                    """Yield (normalised name, pinned version or None) for each requirement."""
                    for line in text.replace("\\\n", " ").splitlines():
                        line = line.split("#", 1)[0].strip()
                        if not line or line.startswith("-"):
                            continue
                        req = line.split(";")[0].split()[0]
                        m = re.match(r"([A-Za-z0-9._-]+)(?:\[[^\]]*\])?", req)
                        rest = req[m.end():]
                        pinned = rest[2:] if rest.startswith("==") and "," not in rest else None
                        yield norm(m.group(1)), pinned

                def audit(requirements_text, advisories):
                    found = []
                    for name, version in pins(requirements_text):
                        if version is None:
                            found.append((name, None, "UNPINNED", None))
                            continue
                        for adv in advisories:
                            if norm(adv["package"]) == name and satisfies(version, adv["affected"]):
                                found.append((name, version, adv["id"], adv.get("fixed")))
                    return sorted(found, key=lambda f: (f[0], f[2]))

                def main(argv):
                    with open(argv[0]) as fh:
                        text = fh.read()
                    with open(argv[1]) as fh:
                        advisories = json.load(fh)
                    found = audit(text, advisories)
                    for name, version, adv_id, fixed in found:
                        if version is None:
                            print(f"{name}: not pinned, so it cannot be audited")
                        else:
                            print(f"{name} {version}  {adv_id}  fix: {fixed or 'none yet'}")
                    if found:
                        print(f"{len(found)} problem(s) in {len({f[0] for f in found})} package(s)")
                    else:
                        print("no known vulnerabilities")
                    return 1 if found else 0

                if __name__ == "__main__":
                    import sys
                    raise SystemExit(main(sys.argv[1:]))
            ''', "Three small pieces (parse pins, compare versions, match advisories) that each fit on a screen "
                 "and can be tested alone. The exit code is the interface CI cares about: 0 passes the job, "
                 "anything else fails it."),
            "index advisories by package first": (r'''
                import json
                import operator
                import re
                from collections import defaultdict
                from itertools import zip_longest

                OPS = {"==": operator.eq, "!=": operator.ne, "<=": operator.le,
                       ">=": operator.ge, "<": operator.lt, ">": operator.gt}

                def norm(name):
                    return re.sub(r"[-_.]+", "-", name).lower()

                def key(version, width):
                    return [int(p) for p in version.split(".")] + [0] * width

                def satisfies(version, spec):
                    for clause in (c.strip() for c in spec.split(",") if c.strip()):
                        op = max((o for o in OPS if clause.startswith(o)), key=len)
                        target = clause[len(op):].strip()
                        width = max(version.count("."), target.count(".")) + 1
                        if not OPS[op](key(version, width)[:width], key(target, width)[:width]):
                            return False
                    return True

                def audit(requirements_text, advisories):
                    by_package = defaultdict(list)
                    for adv in advisories:
                        by_package[norm(adv["package"])].append(adv)
                    found = []
                    text = re.sub(r"\\\n", " ", requirements_text)
                    for line in text.splitlines():
                        req = line.split("#", 1)[0].split(";", 1)[0].strip()
                        if not req or req.startswith("-"):
                            continue
                        req = req.split()[0]
                        m = re.fullmatch(r"([A-Za-z0-9._-]+)(\[[^\]]*\])?(?:==([0-9.]+))?(.*)", req)
                        name, version = norm(m.group(1)), m.group(3)
                        if version is None or m.group(4):
                            found.append((name, None, "UNPINNED", None))
                            continue
                        found += [(name, version, a["id"], a.get("fixed"))
                                  for a in by_package[name] if satisfies(version, a["affected"])]
                    return sorted(found, key=operator.itemgetter(0, 2))

                def main(argv):
                    req_path, adv_path = argv
                    with open(req_path) as r, open(adv_path) as a:
                        found = audit(r.read(), json.load(a))
                    for name, version, adv_id, fixed in found:
                        print(f"{name:20} {version or '(unpinned)':12} {adv_id:20} {fixed or '-'}")
                    print(f"{len(found)} finding(s)" if found else "no known vulnerabilities")
                    return int(bool(found))
            ''', "Grouping the advisories by package once turns 'check every advisory for every line' into a "
                 "dictionary lookup, which matters when the database has 100,000 entries. max(..., key=len) "
                 "picks '<=' over '<' when both prefixes match."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code='import re\nprint(re.sub(r"[-_.]+", "-", "Zope.Interface__Ext").lower())',
         why="PEP 503: every run of - _ . becomes one -, then lower case."),
    dict(kind="predict", code='print("2.10" < "2.9", (2, 10) < (2, 9))',
         why="Strings compare character by character ('1' < '9'); tuples of ints compare numerically."),
    dict(kind="predict", code="import hashlib\nprint(len(hashlib.sha256(b'').hexdigest()))",
         why="256 bits = 32 bytes = 64 hex digits, whatever the input size."),
    dict(kind="predict", code='import difflib\nprint(difflib.get_close_matches("nunpy", ["numpy", "pandas", "sympy"], n=2))'),
    dict(kind="predict", code="import importlib.metadata as md\nprint(md.PackageNotFoundError.__mro__[1].__name__)",
         why="A missing distribution is a kind of missing module."),
    dict(kind="predict", code='line = "requests[socks]>=2 ; python_version > \'3\'  # http"\nprint(line.split("#")[0].partition(";")[0].strip())'),
    dict(kind="predict", code="import sys\nprint(type(sys.stdlib_module_names).__name__, 'json' in sys.stdlib_module_names)"),
    dict(kind="recall", q="Which file inside a venv records the base interpreter and version?", a=["pyvenv.cfg"]),
    dict(kind="recall", q="Which pip option refuses to install anything whose hash isn't listed?", a=["--require-hashes", "require-hashes"]),
    dict(kind="recall", q="Does ~=2.32.0 allow version 2.33.0? (yes/no)", a=["no"]),
    dict(kind="recall", q="Which PEP lets Linux distributions mark the system Python as 'externally managed'?", a=["668", "pep 668", "pep668"]),
]
