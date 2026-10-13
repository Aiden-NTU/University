EXERCISES = [
    dict(
        id="14.1", kind="build", title="An argparse CLI from a spec",
        task="""
        Write `make_parser()` returning an `argparse.ArgumentParser` for this interface:

            loans [-v ...] [--db PATH] add TITLE [--days N]
            loans [-v ...] [--db PATH] list [--overdue] [--sort {title,due}]
            loans [-v ...] [--db PATH] return LOAN_ID

        `-v`/`--verbose` counts (default 0); `--db` defaults to `loans.db`; `--days` is an int from 1 to 60
        (default 14); `--sort` defaults to `due`; `LOAN_ID` is an int. The parsed attributes must be named
        `verbose, db, cmd, title, days, overdue, sort, loan_id`. Any misuse must exit with code 2, and that is
        argparse's default behaviour.
        """,
        stub='''
        import argparse

        def make_parser():
            p = argparse.ArgumentParser(prog="loans")
            sub = p.add_subparsers(dest="cmd")
            add = sub.add_parser("add")
            add.add_argument("title")
            add.add_argument("--days", default=14)
            return p
        ''',
        tests='''
        import contextlib, io

        def parse(m, argv):
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                return m.make_parser().parse_args(argv)

        def rejects(m, argv):
            try:
                parse(m, argv)
            except SystemExit as e:
                equal(e.code, 2, f"{argv}: usage errors exit with code 2")
            else:
                check(False, f"{argv} should be rejected")

        def test_add(m):
            a = parse(m, ["add", "Dune"])
            equal((a.cmd, a.title, a.days, a.verbose, a.db), ("add", "Dune", 14, 0, "loans.db"), "loans add Dune")
            a = parse(m, ["-vv", "--db", "x.db", "add", "Emma", "--days", "7"])
            equal((a.cmd, a.title, a.days, a.verbose, a.db), ("add", "Emma", 7, 2, "x.db"), "-vv --db x.db add Emma --days 7")

        def test_list_and_return(m):
            a = parse(m, ["list"])
            equal((a.cmd, a.overdue, a.sort), ("list", False, "due"), "loans list")
            a = parse(m, ["list", "--overdue", "--sort", "title"])
            equal((a.overdue, a.sort), (True, "title"), "list --overdue --sort title")
            a = parse(m, ["return", "12"])
            equal((a.cmd, a.loan_id), ("return", 12), "return 12")

        def test_rejects(m):
            for argv in ([], ["add"], ["add", "X", "--days", "0"], ["add", "X", "--days", "61"],
                         ["add", "X", "--days", "two"], ["list", "--sort", "author"], ["return", "abc"], ["fly"]):
                rejects(m, argv)

        def test_help(m):
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out):
                    m.make_parser().parse_args(["--help"])
            except SystemExit as e:
                equal(e.code, 0, "--help exits 0")
            for word in ("add", "list", "return"):
                check(word in out.getvalue(), f"--help should mention {word!r}")
        ''',
        alts={
            "a type function": ('''
                import argparse

                def loan_days(text):
                    n = int(text)                    # ValueError -> argparse reports "invalid loan_days value"
                    if not 1 <= n <= 60:
                        raise argparse.ArgumentTypeError("must be between 1 and 60")
                    return n

                def make_parser():
                    p = argparse.ArgumentParser(prog="loans", description="Track library loans.")
                    p.add_argument("-v", "--verbose", action="count", default=0)
                    p.add_argument("--db", default="loans.db", metavar="PATH")
                    sub = p.add_subparsers(dest="cmd", required=True)
                    add = sub.add_parser("add", help="lend a book")
                    add.add_argument("title")
                    add.add_argument("--days", type=loan_days, default=14, metavar="N")
                    ls = sub.add_parser("list", help="show loans")
                    ls.add_argument("--overdue", action="store_true")
                    ls.add_argument("--sort", choices=["title", "due"], default="due")
                    ret = sub.add_parser("return", help="a book came back")
                    ret.add_argument("loan_id", type=int)
                    return p
            ''', "type= can be any function from str to value. Raising ArgumentTypeError gives the user your "
                 "message; required=True on the subparsers makes plain `loans` an error."),
            "choices=range": ('''
                import argparse

                def make_parser():
                    p = argparse.ArgumentParser(prog="loans")
                    p.add_argument("-v", "--verbose", action="count", default=0)
                    p.add_argument("--db", default="loans.db")
                    sub = p.add_subparsers(dest="cmd", required=True)
                    add = sub.add_parser("add")
                    add.add_argument("title")
                    add.add_argument("--days", type=int, choices=range(1, 61), default=14, metavar="1..60")
                    ls = sub.add_parser("list")
                    ls.add_argument("--overdue", action="store_true")
                    ls.add_argument("--sort", choices=["title", "due"], default="due")
                    sub.add_parser("return").add_argument("loan_id", type=int)
                    return p
            ''', "choices accepts any container, and a range checks membership in O(1). Without metavar, the "
                 "help would print all 60 numbers."),
        },
    ),
    dict(
        id="14.2", kind="fix", title="Close the shell-injection hole",
        task="""
        `count_lines(path)` runs `wc -l` on a file and returns the count as an int. The stub builds a shell
        command from the filename, so names with spaces, quotes, `$` or a leading `-` break it, and a name
        like `x; touch HACKED; y.txt` runs a command. Fix it so every legal filename works, still using
        `wc` through `subprocess`. Raise `FileNotFoundError` if `wc` reports a failure.
        """,
        stub='''
        import subprocess

        def count_lines(path):
            out = subprocess.run(f"wc -l {path}", shell=True, capture_output=True, text=True).stdout
            return int(out.split()[0])
        ''',
        tests='''
        import os

        NAMES = ["plain.txt", "with space.txt", "quote's.txt", "$HOME.txt", "x; touch HACKED; y.txt", "-n.txt", "back`tick`.txt"]

        def test_names(m):
            with tmpdir():
                for i, name in enumerate(NAMES):
                    with open(name, "w") as fh:
                        fh.write("line\\n" * (i + 2))
                for i, name in enumerate(NAMES):
                    equal(m.count_lines(name), i + 2, f"lines in {name!r}")
                check(not os.path.exists("HACKED"), "the filename ran a command: injection still possible")

        def test_missing(m):
            with tmpdir():
                raises(FileNotFoundError, m.count_lines, "nope.txt")

        def test_uses_subprocess(m):
            check("subprocess" in imports(m), "keep using wc via subprocess (the point is to call it safely)")
        ''',
        alts={
            "list of arguments": ('''
                import subprocess

                def count_lines(path):
                    r = subprocess.run(["wc", "-l", "--", path], capture_output=True, text=True)
                    if r.returncode != 0:
                        raise FileNotFoundError(r.stderr.strip())
                    return int(r.stdout.split()[0])
            ''', "No shell, so nothing parses the name: it arrives as one argv entry. The '--' stops wc from "
                 "reading '-n.txt' as an option. This is the fix to reach for first."),
            "shlex.quote, if you truly need a shell": ('''
                import shlex, subprocess

                def count_lines(path):
                    cmd = f"wc -l -- {shlex.quote(path)}"
                    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if r.returncode != 0:
                        raise FileNotFoundError(r.stderr.strip())
                    return int(r.stdout.split()[0])
            ''', "shlex.quote wraps the value in single quotes the shell can't break out of. Only worth it when "
                 "you need shell features (pipes, globs); one forgotten quote() reopens the hole."),
        },
    ),
    dict(
        id="14.3", kind="build", title="A grep-like filter with proper exit codes",
        task="""
        Write `main(argv, stdin, stdout, stderr)` for a tool used as `grepish [-i] [-c] PATTERN [FILE ...]`.
        It prints lines matching the regex `PATTERN` (`re.search`). With no files, or a file named `-`, it reads
        `stdin`. With more than one source, prefix each output line with `NAME:` (stdin's name is
        `(standard input)`). `-i` ignores case; `-c` prints only the count of matching lines (per source,
        prefixed the same way). Return grep's exit code: `0` if any line matched, `1` if none, `2` if any
        error happened. Errors are a bad regex, or a file that can't be opened: write a message naming it to
        `stderr` and carry on with the other files.
        """,
        stub='''
        def main(argv, stdin, stdout, stderr):
            pattern = argv[0]
            for line in stdin:
                if pattern in line:
                    stdout.write(line)
            return 0
        ''',
        tests='''
        import contextlib, io, random, re

        def run(m, argv, text=""):
            out, err = io.StringIO(), io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    code = m.main(argv, io.StringIO(text), out, err)
            except SystemExit as e:
                code = e.code
            return code, out.getvalue(), err.getvalue()

        def write(name, text):
            with open(name, "w") as fh:
                fh.write(text)

        def test_stdin(m):
            text = "ok\\nerror 1\\nERROR 2\\n"
            equal(run(m, ["err"], text)[:2], (0, "error 1\\n"), "match from stdin")
            equal(run(m, ["-i", "err"], text)[:2], (0, "error 1\\nERROR 2\\n"), "-i")
            equal(run(m, ["-c", "-i", "err"], text)[:2], (0, "2\\n"), "-c -i")
            equal(run(m, ["^E.*\\\\d$"], text)[:2], (0, "ERROR 2\\n"), "it's a regex")
            equal(run(m, ["zzz"], text)[:2], (1, ""), "no match: exit 1")
            equal(run(m, ["-c", "zzz"], text)[:2], (1, "0\\n"), "-c with no match prints 0, exit 1")

        def test_files(m):
            with tmpdir():
                write("a.txt", "x1\\ny\\n")
                write("b.txt", "x2\\n")
                equal(run(m, ["x", "a.txt"])[:2], (0, "x1\\n"), "one file: no prefix")
                equal(run(m, ["x", "a.txt", "b.txt"])[:2], (0, "a.txt:x1\\nb.txt:x2\\n"), "two files: prefixed")
                equal(run(m, ["-c", "x", "a.txt", "b.txt"])[:2], (0, "a.txt:1\\nb.txt:1\\n"), "-c per file")
                equal(run(m, ["x", "a.txt", "-"], "x3\\n")[:2], (0, "a.txt:x1\\n(standard input):x3\\n"), "'-' is stdin")

        def test_errors(m):
            with tmpdir():
                write("a.txt", "x1\\n")
                code, out, err = run(m, ["x", "a.txt", "nope.txt"])
                equal((code, out), (2, "a.txt:x1\\n"), "missing file: still prints the rest, exit 2")
                check("nope.txt" in err, "the error message should name the missing file")
                code, out, err = run(m, ["(", "a.txt"])
                check(code == 2 and err.strip(), "a bad regex is an error: message on stderr, exit 2")
                code, _, _ = run(m, [])
                equal(code, 2, "no pattern: usage error")

        def test_random(m):
            rng = random.Random(16)
            words = rand_words(12, 7)
            for _ in range(80):
                lines = [" ".join(rng.choice(words) for _ in range(rng.randint(0, 4))) for _ in range(rng.randint(0, 15))]
                text = "".join(l + "\\n" for l in lines)
                pat = rng.choice(words)[:2]
                want = [l for l in lines if re.search(pat, l)]
                equal(run(m, [pat], text)[:2], (0 if want else 1, "".join(l + "\\n" for l in want)), f"pattern {pat!r}")
        ''',
        alts={
            "argparse + one function per source": ('''
                import argparse, re

                def main(argv, stdin, stdout, stderr):
                    p = argparse.ArgumentParser(prog="grepish")
                    p.add_argument("-i", action="store_true")
                    p.add_argument("-c", action="store_true")
                    p.add_argument("pattern")
                    p.add_argument("files", nargs="*")
                    args = p.parse_args(argv)
                    try:
                        rx = re.compile(args.pattern, re.IGNORECASE if args.i else 0)
                    except re.error as e:
                        print(f"grepish: bad pattern: {e}", file=stderr)
                        return 2
                    sources = args.files or ["-"]
                    prefix = len(sources) > 1
                    matched = error = False

                    def scan(name, lines):
                        nonlocal matched
                        hits = [l.rstrip("\\n") for l in lines if rx.search(l)]
                        matched |= bool(hits)
                        tag = f"{name}:" if prefix else ""
                        if args.c:
                            print(f"{tag}{len(hits)}", file=stdout)
                        else:
                            for h in hits:
                                print(f"{tag}{h}", file=stdout)

                    for src in sources:
                        if src == "-":
                            scan("(standard input)", stdin)
                            continue
                        try:
                            with open(src) as fh:
                                scan(src, fh)
                        except OSError as e:
                            print(f"grepish: {src}: {e.strerror}", file=stderr)
                            error = True
                    return 2 if error else 0 if matched else 1
            ''', "argparse already exits 2 on usage errors, matching grep. Passing the streams in is what makes "
                 "it testable without touching the real terminal (Ch 14's main(argv) pattern, extended)."),
            "generators and an exit-code table": ('''
                import re, sys

                def sources(names, stdin, stderr, failed):
                    for name in names or ["-"]:
                        if name == "-":
                            yield "(standard input)", stdin
                            continue
                        try:
                            with open(name) as fh:
                                yield name, fh
                        except OSError as e:
                            print(f"grepish: {name}: {e.strerror}", file=stderr)
                            failed.append(name)

                def main(argv, stdin, stdout, stderr):
                    flags = {a for a in argv if a in ("-i", "-c")}
                    rest = [a for a in argv if a not in ("-i", "-c")]
                    if not rest:
                        print("usage: grepish [-i] [-c] PATTERN [FILE ...]", file=stderr)
                        return 2
                    try:
                        rx = re.compile(rest[0], re.I if "-i" in flags else 0)
                    except re.error as e:
                        print(f"grepish: {e}", file=stderr)
                        return 2
                    names, failed, total = rest[1:], [], 0
                    for name, lines in sources(names, stdin, stderr, failed):
                        tag = f"{name}:" if len(names) > 1 else ""
                        hits = [l.rstrip("\\n") for l in lines if rx.search(l)]
                        total += len(hits)
                        out = [f"{tag}{len(hits)}"] if "-c" in flags else [tag + h for h in hits]
                        stdout.writelines(o + "\\n" for o in out)
                    return 2 if failed else (0 if total else 1)
            ''', "Hand-rolled option parsing is fine for two flags, but it would treat a pattern of '-c' as a "
                 "flag: real tools need '--' handling, which argparse gives you for free."),
        },
    ),
    dict(
        id="14.4", kind="build", title="Config from flags, environment and defaults",
        task="""
        Write `load_config(argv, environ, defaults)` returning a new dict. `defaults` maps names to default
        values (str, int, float or bool). An environment variable `LOANS_<NAME>` (upper case) overrides a
        default; a command-line flag overrides both. Flags look like `--name value` or `--name=value`; a bool is
        set by `--name` (True) or `--no-name` (False), with no value. Convert every value to the **type of
        its default**. Env bools accept `1/0, true/false, yes/no, on/off` (any case). Raise `ValueError` for
        an unknown flag, a missing or unconvertible value, or a bad bool. Ignore unknown `LOANS_` variables,
        and don't change `defaults`.
        """,
        stub='''
        def load_config(argv, environ, defaults):
            config = defaults
            for i, arg in enumerate(argv):
                if arg.startswith("--"):
                    config[arg[2:]] = argv[i + 1]
            return config
        ''',
        tests='''
        import random

        D = {"db": "loans.db", "days": 14, "fine": 0.25, "verbose": False}

        def test_precedence(m):
            d = dict(D)
            equal(m.load_config([], {}, d), D, "defaults only")
            equal(d, D, "defaults must not be modified")
            equal(m.load_config([], {"LOANS_DAYS": "21", "HOME": "/x"}, d)["days"], 21, "env overrides (and is converted to int)")
            equal(m.load_config(["--days", "7"], {"LOANS_DAYS": "21"}, d)["days"], 7, "flag beats env")
            equal(m.load_config(["--days=30"], {}, d)["days"], 30, "--name=value form")
            equal(m.load_config(["--fine", "0.5"], {}, d)["fine"], 0.5, "float")
            equal(m.load_config(["--db", "x.db"], {"LOANS_DB": "y.db"}, d)["db"], "x.db", "str")

        def test_bools(m):
            equal(m.load_config(["--verbose"], {}, D)["verbose"], True, "--verbose")
            equal(m.load_config(["--no-verbose"], {"LOANS_VERBOSE": "yes"}, D)["verbose"], False, "--no-verbose beats env")
            for s, want in [("1", True), ("TRUE", True), ("on", True), ("No", False), ("off", False), ("0", False)]:
                equal(m.load_config([], {"LOANS_VERBOSE": s}, D)["verbose"], want, f"LOANS_VERBOSE={s}")

        def test_errors(m):
            for argv, env in [(["--colour", "red"], {}), (["--days"], {}), (["--days", "many"], {}),
                              ([], {"LOANS_DAYS": "x"}), ([], {"LOANS_VERBOSE": "maybe"}), (["days", "3"], {}),
                              (["--fine=cheap"], {})]:
                raises(ValueError, m.load_config, argv, env, dict(D))
            equal(m.load_config([], {"LOANS_UNKNOWN": "1"}, D), D, "unknown LOANS_ variables are ignored")

        def test_random(m):
            rng = random.Random(17)
            for _ in range(200):
                want, argv, env = dict(D), [], {}
                if rng.random() < 0.5:
                    env["LOANS_DAYS"] = str(rng.randint(1, 60)); want["days"] = int(env["LOANS_DAYS"])
                if rng.random() < 0.5:
                    v = rng.randint(1, 60); want["days"] = v
                    argv += rng.choice([["--days", str(v)], [f"--days={v}"]])
                if rng.random() < 0.5:
                    v = rng.random() < 0.5; want["verbose"] = v
                    argv.append("--verbose" if v else "--no-verbose")
                equal(m.load_config(argv, env, D), want, f"argv={argv} env={env}")
        ''',
        alts={
            "ChainMap of layers": ('''
                from collections import ChainMap

                TRUE, FALSE = {"1", "true", "yes", "on"}, {"0", "false", "no", "off"}

                def convert(name, text, default):
                    if isinstance(default, bool):
                        low = text.lower()
                        if low in TRUE | FALSE:
                            return low in TRUE
                        raise ValueError(f"{name}: not a yes/no value: {text!r}")
                    try:
                        return type(default)(text)
                    except ValueError:
                        raise ValueError(f"{name}: expected {type(default).__name__}, got {text!r}") from None

                def load_config(argv, environ, defaults):
                    env = {k: convert(k, environ[f"LOANS_{k.upper()}"], v)
                           for k, v in defaults.items() if f"LOANS_{k.upper()}" in environ}
                    cli, args = {}, list(argv)
                    while args:
                        arg = args.pop(0)
                        if not arg.startswith("--"):
                            raise ValueError(f"unexpected argument {arg!r}")
                        name, eq, value = arg[2:].partition("=")
                        if name.startswith("no-") and isinstance(defaults.get(name[3:]), bool) and not eq:
                            cli[name[3:]] = False
                        elif name not in defaults:
                            raise ValueError(f"unknown option --{name}")
                        elif isinstance(defaults[name], bool):
                            if eq:
                                raise ValueError(f"--{name} takes no value")
                            cli[name] = True
                        else:
                            if not eq:
                                if not args:
                                    raise ValueError(f"--{name} needs a value")
                                value = args.pop(0)
                            cli[name] = convert(name, value, defaults[name])
                    return dict(ChainMap(cli, env, defaults))
            ''', "ChainMap(cli, env, defaults) is the precedence rule written as data: lookups try each layer in "
                 "order. dict() flattens it so callers get a plain, independent dict."),
            "argparse generated from the defaults": ('''
                import argparse

                TRUE, FALSE = {"1", "true", "yes", "on"}, {"0", "false", "no", "off"}

                def env_value(name, text, default):
                    if isinstance(default, bool):
                        if text.lower() not in TRUE | FALSE:
                            raise ValueError(f"LOANS_{name.upper()}: not a yes/no value")
                        return text.lower() in TRUE
                    return type(default)(text)

                def load_config(argv, environ, defaults):
                    start = dict(defaults)
                    for name, default in defaults.items():
                        key = f"LOANS_{name.upper()}"
                        if key in environ:
                            start[name] = env_value(name, environ[key], default)
                    p = argparse.ArgumentParser(exit_on_error=False, add_help=False, allow_abbrev=False)
                    for name, default in defaults.items():
                        if isinstance(default, bool):
                            p.add_argument(f"--{name}", action=argparse.BooleanOptionalAction)
                        else:
                            p.add_argument(f"--{name}", type=type(default))
                    p.set_defaults(**start)
                    try:
                        ns, extra = p.parse_known_args(argv)
                    except argparse.ArgumentError as e:
                        raise ValueError(str(e)) from None
                    if extra:
                        raise ValueError(f"unrecognised arguments: {extra}")
                    return vars(ns)
            ''', "Let argparse do the flag syntax (including --no-x via BooleanOptionalAction) and feed the env "
                 "layer in as defaults. exit_on_error=False turns its errors into exceptions you can convert."),
        },
    ),
    dict(
        id="14.5", kind="explore", title="Read a .env file with shlex",
        task="""
        Use the `shlex` module (Ch 7 method) to write `parse_env_file(text)` for `.env` files: each non-blank
        line is `KEY=value`, optionally preceded by `export `. `#` starts a comment (outside quotes). Values
        may be single- or double-quoted to hold spaces or `#`; `KEY=` means an empty string. Later lines override
        earlier ones. Keys must match `[A-Za-z_][A-Za-z0-9_]*`. Raise `ValueError` whose message contains the
        **line number** (1-based) for a bad key, a missing `=`, extra words, or an unclosed quote.
        """,
        stub='''
        def parse_env_file(text):
            out = {}
            for line in text.splitlines():
                if "=" in line:
                    key, value = line.split("=")
                    out[key] = value
            return out
        ''',
        tests='''
        GOOD = """
        # settings for local runs
        DB=loans.db
        export DAYS=21
        GREETING="hello world"   # trailing comment
        NOTE='a # inside quotes'
        EMPTY=
        DB=other.db
        """

        def test_good(m):
            equal(m.parse_env_file(GOOD), {"DB": "other.db", "DAYS": "21", "GREETING": "hello world",
                                           "NOTE": "a # inside quotes", "EMPTY": ""}, "parsed .env")
            equal(m.parse_env_file(""), {}, "empty file")

        def test_bad(m):
            for text, line in [("A=1\\n1BAD=x", 2), ("A=1\\n\\nNOEQUALS", 3), ("X=a b", 1), ('A=1\\nB="open', 2),
                               ("A-B=1", 1)]:
                try:
                    m.parse_env_file(text)
                except ValueError as e:
                    check(str(line) in str(e), f"error for {text!r} should mention line {line}: got {e}")
                else:
                    check(False, f"{text!r} should raise ValueError")
        ''',
        alts={
            "shlex.split per line": ('''
                import re, shlex

                KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

                def parse_env_file(text):
                    out = {}
                    for n, line in enumerate(text.splitlines(), 1):
                        try:
                            words = shlex.split(line, comments=True)
                        except ValueError as e:
                            raise ValueError(f"line {n}: {e}") from None
                        if words[:1] == ["export"]:
                            words = words[1:]
                        if not words:
                            continue
                        key, eq, value = words[0].partition("=")
                        if len(words) > 1 or not eq or not KEY.fullmatch(key):
                            raise ValueError(f"line {n}: expected KEY=value, got {line.strip()!r}")
                        out[key] = value
                    return out
            ''', "shlex already implements shell quoting and comments, so quotes, # and spaces are handled. "
                 "You only add the KEY=value check and the line numbers."),
            "one regex per line": ('''
                import re

                LINE = re.compile(r"""\\s*(?:export\\s+)?([A-Za-z_][A-Za-z0-9_]*)=(?:"([^"]*)"|'([^']*)'|([^\\s#'"]*))\\s*(?:\\#.*)?""")

                def parse_env_file(text):
                    out = {}
                    for n, line in enumerate(text.splitlines(), 1):
                        if not line.strip() or line.strip().startswith("#"):
                            continue
                        mt = LINE.fullmatch(line)
                        if not mt:
                            raise ValueError(f"line {n}: can't parse {line.strip()!r}")
                        key, dq, sq, bare = mt.groups()
                        out[key] = next(v for v in (dq, sq, bare) if v is not None)
                    return out
            ''', "A regex works and has no hidden behaviour, but it doesn't do backslash escapes inside double "
                 "quotes, which shlex does. Knowing what the library already solves is the Ch 7 lesson."),
        },
    ),
    dict(
        id="14.6", kind="project", title="A tiny task runner",
        task="""
        Mini-project. Write `run_all(commands, timeout=10, keep_going=False)`. `commands` is a list of argv
        lists. Run them in order and return a list of results, each with attributes `cmd`, `returncode`,
        `stdout`, `stderr` (text), `seconds` (float) and `timed_out` (bool).
        - A command that runs too long is killed: `timed_out=True`, `returncode=None`.
        - A program that doesn't exist gives `returncode=127`, with its name in `stderr`.
        - Stop after the first failure (non-zero, timeout or not found) unless `keep_going`.
        Never use a shell.
        """,
        stub='''
        import subprocess

        def run_all(commands, timeout=10, keep_going=False):
            return [subprocess.run(" ".join(c), shell=True, capture_output=True, text=True) for c in commands]
        ''',
        tests='''
        import sys

        PY = sys.executable

        def test_success_and_capture(m):
            rs = m.run_all([[PY, "-c", "print('hi')"], [PY, "-c", "import sys; print('oops', file=sys.stderr)"]])
            equal(len(rs), 2, "both ran")
            equal((rs[0].returncode, rs[0].stdout, rs[0].timed_out), (0, "hi\\n", False), "first result")
            equal(rs[1].stderr, "oops\\n", "stderr captured separately")
            check(all(isinstance(r.seconds, float) and r.seconds >= 0 for r in rs), "seconds is a float")
            equal(rs[0].cmd, [PY, "-c", "print('hi')"], "cmd recorded")

        def test_stop_on_failure(m):
            cmds = [[PY, "-c", "raise SystemExit(3)"], [PY, "-c", "print('never')"]]
            rs = m.run_all(cmds)
            equal([r.returncode for r in rs], [3], "stops after the first failure")
            rs = m.run_all(cmds, keep_going=True)
            equal([r.returncode for r in rs], [3, 0], "keep_going runs everything")

        def test_timeout(m):
            rs = m.run_all([[PY, "-c", "import time; time.sleep(5)"], [PY, "-c", "pass"]], timeout=0.3)
            equal(len(rs), 1, "a timeout counts as a failure")
            equal((rs[0].timed_out, rs[0].returncode), (True, None), "timed out")
            check(rs[0].seconds < 3, "the slow command must be killed at the timeout")

        def test_not_found(m):
            rs = m.run_all([["no-such-program-xyz", "arg"]])
            equal(rs[0].returncode, 127, "missing program")
            check("no-such-program-xyz" in rs[0].stderr, "stderr names the missing program")
            equal(m.run_all([["no-such-program-xyz"], [PY, "-c", "pass"]], keep_going=True)[1].returncode, 0, "keep_going")

        def test_no_shell(m):
            for node in __import__("ast").walk(source_tree(m)):
                if type(node).__name__ == "keyword" and node.arg == "shell":
                    check(False, "don't pass shell= at all")
        ''',
        alts={
            "subprocess.run + a dataclass": ('''
                import subprocess, time
                from dataclasses import dataclass

                @dataclass
                class Result:
                    cmd: list
                    returncode: int | None
                    stdout: str
                    stderr: str
                    seconds: float
                    timed_out: bool = False

                    @property
                    def ok(self):
                        return self.returncode == 0

                def run_one(cmd, timeout):
                    t0 = time.perf_counter()
                    try:
                        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                        return Result(cmd, p.returncode, p.stdout, p.stderr, time.perf_counter() - t0)
                    except subprocess.TimeoutExpired as e:
                        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
                        return Result(cmd, None, out, "", time.perf_counter() - t0, timed_out=True)
                    except FileNotFoundError as e:
                        return Result(cmd, 127, "", f"{cmd[0]}: {e.strerror}", time.perf_counter() - t0)

                def run_all(commands, timeout=10, keep_going=False):
                    results = []
                    for cmd in commands:
                        results.append(r := run_one(cmd, timeout))
                        if not r.ok and not keep_going:
                            break
                    return results
            ''', "run() kills the child when the timeout expires. The three outcomes (finished, timed out, "
                 "never started) map to three branches, and perf_counter (Ch 11) does the timing."),
            "Popen + communicate": ('''
                import subprocess, time
                from types import SimpleNamespace

                def run_all(commands, timeout=10, keep_going=False):
                    results = []
                    for cmd in commands:
                        t0 = time.perf_counter()
                        r = SimpleNamespace(cmd=cmd, returncode=None, stdout="", stderr="", timed_out=False)
                        try:
                            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as p:
                                try:
                                    r.stdout, r.stderr = p.communicate(timeout=timeout)
                                    r.returncode = p.returncode
                                except subprocess.TimeoutExpired:
                                    p.kill()
                                    r.stdout, r.stderr = p.communicate()
                                    r.timed_out = True
                        except FileNotFoundError:
                            r.returncode, r.stderr = 127, f"{cmd[0]}: command not found"
                        r.seconds = time.perf_counter() - t0
                        results.append(r)
                        if r.returncode != 0 and not keep_going:
                            break
                    return results
            ''', "Popen is the lower layer run() is built on. You need it to stream output live or talk to a "
                 "child interactively; here it shows what run(timeout=) does for you: kill, then collect."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="import subprocess, sys\nr = subprocess.run([sys.executable, '-c', 'import sys; sys.exit(4)'])\nprint(r.returncode)"),
    dict(kind="predict", code="import shlex\nprint(shlex.split('cp \"my file.txt\" backup/'))"),
    dict(kind="predict", code="import shlex\nprint(shlex.quote(\"it's\"))", why="Close the quote, add a double-quoted ', reopen: 'it'\"'\"'s'."),
    dict(kind="predict", code="import argparse\np = argparse.ArgumentParser()\np.add_argument('-v', action='count', default=0)\nprint(p.parse_args(['-vvv']).v)"),
    dict(kind="predict", code="import os\nos.environ['X_DEMO'] = '1'\nprint(type(os.environ['X_DEMO']).__name__, os.getenv('NOPE_DEMO', 'default'))"),
    dict(kind="recall", q="What exit code means success?", a=["0", "zero"]),
    dict(kind="recall", q="Which signal can never be caught or ignored?", a=["SIGKILL", "kill", "9", "sigkill"]),
    dict(kind="recall", q="Which subprocess.run argument makes a non-zero exit raise an exception?", a=["check", "check=True"]),
    dict(kind="recall", q="Which exit code does argparse use for usage errors?", a=["2"]),
]
