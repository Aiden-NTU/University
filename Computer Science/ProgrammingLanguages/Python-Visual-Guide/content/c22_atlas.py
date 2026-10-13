"""Appendix A - the standard library atlas: every module in sys.stdlib_module_names, grouped by job, with a
tier (1 use weekly, 2 know it exists, 3 map only) and the chapters that use it. The build fails if the
installed Python has a module the atlas doesn't cover."""
import ast
import glob
import os
import re
import sys

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, callout, code, flow, section, title_block

ORDER = 22
NUM = "A"
TITLE = "The standard library atlas"
SHORT = "Stdlib atlas"
SLUG = "Stdlib-Atlas"
ACCENT = C.TEAL

TIER_COL = {1: C.GREEN, 2: C.BLUE, 3: C.GREY}
TIER_FONT = {1: F.MONOB, 2: F.MONO, 3: F.MONO}

# (group, [(module, tier, what it is for)])
GROUPS = [
    ("Text", [
        ("string", 2, "constants (`ascii_letters`, `digits`), `Template` substitution"),
        ("re", 1, "regular expressions: search, match, split, substitute"),
        ("difflib", 2, "diffs between sequences; close-match suggestions"),
        ("textwrap", 1, "wrap, fill, indent and dedent paragraphs"),
        ("unicodedata", 2, "character names, categories, normalisation (NFC/NFKC)"),
        ("stringprep", 3, "internet string preparation tables (RFC 3454)"),
        ("readline", 3, "line editing and history for `input()` on Unix"),
        ("rlcompleter", 3, "tab completion of Python names for readline"),
    ]),
    ("Binary data", [
        ("struct", 2, "pack and unpack C structs and binary file headers"),
        ("codecs", 2, "the encoder/decoder registry behind `str.encode`"),
        ("encodings", 3, "the codec implementations (utf_8, latin_1, idna...)"),
    ]),
    ("Data types", [
        ("datetime", 1, "dates, times, durations; aware vs naive"),
        ("zoneinfo", 1, "IANA time zones for aware datetimes"),
        ("calendar", 2, "calendars, leap years, weekday arithmetic"),
        ("collections", 1, "`deque`, `Counter`, `defaultdict`, `namedtuple`, `ChainMap`"),
        ("heapq", 1, "a min-heap on a plain list; priority queues, top-k"),
        ("bisect", 1, "binary search and insertion into sorted lists"),
        ("array", 2, "compact typed arrays of numbers"),
        ("weakref", 2, "references that don't keep an object alive; caches"),
        ("types", 2, "names for built-in types, `SimpleNamespace`, `MappingProxyType`"),
        ("copy", 1, "shallow and deep copies"),
        ("pprint", 2, "pretty-print nested data structures"),
        ("reprlib", 3, "size-limited `repr()` for huge or recursive objects"),
        ("enum", 1, "named constants: `Enum`, `IntEnum`, `Flag`, `StrEnum`"),
        ("graphlib", 2, "`TopologicalSorter`: dependency order and cycle detection"),
    ]),
    ("Numbers and maths", [
        ("numbers", 3, "abstract number classes (`Integral`, `Real`...)"),
        ("math", 1, "floats and integers: `sqrt`, `isclose`, `comb`, `gcd`, `fsum`"),
        ("cmath", 2, "the same functions for complex numbers"),
        ("decimal", 2, "exact decimal arithmetic with chosen rounding (money)"),
        ("fractions", 2, "exact rational numbers"),
        ("random", 1, "pseudo-random numbers for simulations (never secrets)"),
        ("statistics", 1, "mean, median, stdev, quantiles, correlation"),
    ]),
    ("Functional tools", [
        ("itertools", 1, "lazy iterator building blocks: chain, groupby, product..."),
        ("functools", 1, "`cache`, `partial`, `reduce`, `wraps`, `total_ordering`"),
        ("operator", 1, "operators as functions: `itemgetter`, `attrgetter`"),
    ]),
    ("Files and directories", [
        ("pathlib", 1, "paths as objects: join, glob, read, write"),
        ("stat", 2, "decode `os.stat()` mode bits"),
        ("filecmp", 2, "compare files and directory trees"),
        ("tempfile", 1, "temporary files and directories, cleaned up for you"),
        ("glob", 2, "shell-style wildcard file matching"),
        ("fnmatch", 2, "match one name against a wildcard pattern"),
        ("linecache", 3, "random access to lines of source files (tracebacks)"),
        ("shutil", 1, "copy, move, delete trees; archives; `which`"),
        ("fileinput", 3, "loop over lines of many files or stdin"),
        ("genericpath", 3, "shared code behind `os.path` (internal)"),
        ("posixpath", 3, "`os.path` on Unix"),
        ("ntpath", 3, "`os.path` on Windows"),
    ]),
    ("Persistence", [
        ("pickle", 2, "serialise Python objects (never load untrusted data)"),
        ("copyreg", 3, "register how pickle and copy handle a type"),
        ("shelve", 2, "a persistent dict of pickled values"),
        ("marshal", 3, "the internal format of .pyc files"),
        ("dbm", 3, "simple key-value database files"),
        ("sqlite3", 1, "a full SQL database in one file"),
    ]),
    ("Compression and archives", [
        ("compression", 2, "new home of the codecs, including `compression.zstd` (3.14)"),
        ("zlib", 2, "deflate compression and CRC-32"),
        ("gzip", 2, "read and write .gz files"),
        ("bz2", 3, "bzip2 compression"),
        ("lzma", 3, "xz/LZMA compression"),
        ("zipfile", 2, "read and write ZIP archives"),
        ("tarfile", 2, "read and write tar archives (use extraction filters)"),
    ]),
    ("File formats", [
        ("csv", 1, "comma-separated files, including quoting rules"),
        ("configparser", 2, "INI-style configuration files"),
        ("tomllib", 2, "read TOML (pyproject.toml); read-only"),
        ("netrc", 3, "parse ~/.netrc login files"),
        ("plistlib", 3, "Apple property lists"),
    ]),
    ("Cryptographic services", [
        ("hashlib", 1, "SHA-2/SHA-3/BLAKE2 digests; `scrypt`, `pbkdf2_hmac`"),
        ("hmac", 1, "keyed message authentication; `compare_digest`"),
        ("secrets", 1, "unguessable tokens and choices for security"),
    ]),
    ("Operating system", [
        ("os", 1, "processes, environment, files, directories"),
        ("io", 1, "the stream classes behind `open()`; `StringIO`, `BytesIO`"),
        ("time", 1, "clocks (`perf_counter`, `monotonic`), sleep, timestamps"),
        ("logging", 1, "levelled, configurable logging for libraries and apps"),
        ("platform", 2, "which OS, machine and Python this is"),
        ("errno", 2, "symbolic names for OS error codes"),
        ("ctypes", 2, "call C functions in shared libraries"),
        ("argparse", 1, "command-line parsing with help and subcommands"),
        ("optparse", 3, "the older command-line parser"),
        ("getopt", 3, "C-style command-line parsing"),
        ("getpass", 2, "read a password without echoing it"),
        ("shlex", 2, "split and quote shell-style command lines safely"),
        ("curses", 3, "full-screen terminal interfaces"),
    ]),
    ("Concurrency", [
        ("threading", 1, "threads, locks, events, conditions"),
        ("multiprocessing", 2, "processes with queues, pipes, shared memory, pools"),
        ("concurrent", 1, "`concurrent.futures`: thread and process pools"),
        ("subprocess", 1, "run other programs; pipes and exit codes"),
        ("sched", 3, "a simple event scheduler"),
        ("queue", 1, "thread-safe FIFO, LIFO and priority queues"),
        ("contextvars", 2, "context-local state (per task in asyncio)"),
        ("asyncio", 1, "async/await: event loop, tasks, streams"),
    ]),
    ("Networking and signals", [
        ("socket", 1, "TCP and UDP sockets"),
        ("ssl", 2, "TLS for sockets: certificates, contexts"),
        ("select", 2, "wait for I/O on many file descriptors"),
        ("selectors", 2, "high-level I/O multiplexing (epoll/kqueue)"),
        ("signal", 2, "handle Unix signals (SIGINT, SIGTERM...)"),
        ("mmap", 3, "memory-mapped files"),
    ]),
    ("Internet data", [
        ("email", 2, "build and parse email messages (MIME)"),
        ("json", 1, "JSON encode and decode"),
        ("mailbox", 3, "mbox and Maildir mailboxes"),
        ("mimetypes", 2, "guess a MIME type from a file name"),
        ("base64", 1, "base64/base32/base85 encodings (not encryption)"),
        ("binascii", 3, "low-level binary-to-ASCII conversions"),
        ("quopri", 3, "quoted-printable encoding"),
    ]),
    ("Markup", [
        ("html", 2, "`escape`, `unescape`, and a simple HTML parser"),
        ("xml", 2, "ElementTree, DOM, SAX (use defusedxml for untrusted input)"),
        ("pyexpat", 3, "the Expat parser behind `xml`"),
    ]),
    ("Internet protocols", [
        ("webbrowser", 2, "open a URL in the user's browser"),
        ("wsgiref", 2, "reference WSGI server and utilities"),
        ("urllib", 1, "URLs: parse, quote, fetch (`urllib.request`)"),
        ("http", 1, "`http.client`, `http.server`, status codes, cookies"),
        ("ftplib", 3, "FTP client"),
        ("poplib", 3, "POP3 client"),
        ("imaplib", 3, "IMAP4 client"),
        ("smtplib", 2, "send mail over SMTP"),
        ("uuid", 2, "universally unique identifiers (uuid4, uuid7)"),
        ("socketserver", 2, "a framework for TCP/UDP servers"),
        ("xmlrpc", 3, "XML-RPC client and server"),
        ("ipaddress", 2, "IPv4/IPv6 addresses and networks"),
    ]),
    ("Multimedia", [
        ("wave", 3, "read and write WAV files"),
        ("colorsys", 3, "convert between RGB, HLS, HSV, YIQ"),
    ]),
    ("Internationalisation", [
        ("gettext", 3, "translations of messages"),
        ("locale", 2, "locale-aware formatting and sorting"),
    ]),
    ("Graphical interfaces", [
        ("tkinter", 2, "the Tk GUI toolkit"),
        ("turtle", 3, "turtle graphics for teaching"),
        ("turtledemo", 3, "demos for turtle"),
        ("idlelib", 3, "the IDLE editor's code"),
    ]),
    ("Development tools", [
        ("typing", 1, "type hints: generics, `Protocol`, `TypedDict`..."),
        ("annotationlib", 2, "inspect annotations, which are lazy since 3.14"),
        ("pydoc", 2, "documentation from docstrings (`help()`)"),
        ("pydoc_data", 3, "data files for pydoc"),
        ("doctest", 2, "run the examples in docstrings as tests"),
        ("unittest", 1, "the test framework; `unittest.mock`"),
        ("venv", 1, "virtual environments"),
        ("ensurepip", 3, "bootstrap pip into an environment"),
        ("zipapp", 3, "bundle a program into a runnable .pyz"),
    ]),
    ("Debugging and profiling", [
        ("bdb", 3, "the debugger framework under pdb"),
        ("faulthandler", 2, "dump tracebacks on crashes and hangs"),
        ("pdb", 1, "the interactive debugger (`breakpoint()`)"),
        ("timeit", 1, "time small snippets reliably"),
        ("trace", 3, "trace execution and line coverage"),
        ("tracemalloc", 2, "find where memory is allocated"),
        ("cProfile", 2, "deterministic profiler (C)"),
        ("profile", 3, "the same profiler in pure Python"),
        ("pstats", 2, "sort and print profiler results"),
    ]),
    ("Python runtime", [
        ("sys", 1, "interpreter state: argv, path, modules, exit, stdout"),
        ("sysconfig", 3, "install paths and build configuration"),
        ("builtins", 2, "the module holding `len`, `print`, `open`..."),
        ("__future__", 2, "opt in to future language behaviour"),
        ("warnings", 2, "issue and filter warnings (deprecations)"),
        ("dataclasses", 1, "classes from field declarations"),
        ("contextlib", 1, "`contextmanager`, `suppress`, `ExitStack`"),
        ("abc", 2, "abstract base classes"),
        ("atexit", 2, "run functions at interpreter exit"),
        ("traceback", 1, "format and print exceptions and stacks"),
        ("gc", 2, "the cycle collector: collect, inspect, disable"),
        ("inspect", 1, "look inside live objects: signatures, source, frames"),
        ("site", 3, "start-up path configuration (site-packages)"),
        ("this", 3, "the Zen of Python (`import this`)"),
        ("antigravity", 3, "an xkcd joke (opens a browser)"),
    ]),
    ("Interpreters and imports", [
        ("code", 3, "build your own interactive console"),
        ("codeop", 3, "compile possibly incomplete input (REPLs)"),
        ("cmd", 3, "line-oriented command interpreters"),
        ("zipimport", 3, "import modules from ZIP files"),
        ("pkgutil", 3, "iterate over and load package data"),
        ("modulefinder", 3, "find the modules a script uses"),
        ("runpy", 2, "run modules as scripts (`python -m`)"),
        ("importlib", 2, "the import system; `importlib.metadata`, `.resources`"),
    ]),
    ("Language services", [
        ("ast", 2, "parse source into a tree; analyse or rewrite code"),
        ("symtable", 3, "the compiler's symbol tables"),
        ("token", 3, "token type constants"),
        ("keyword", 3, "is this string a keyword?"),
        ("tokenize", 2, "split source into tokens (highlighters, linters)"),
        ("tabnanny", 3, "detect ambiguous indentation"),
        ("pyclbr", 3, "browse classes and functions without importing"),
        ("py_compile", 3, "compile one file to .pyc"),
        ("compileall", 3, "compile a whole tree to .pyc"),
        ("dis", 2, "disassemble bytecode"),
        ("pickletools", 3, "inspect and optimise pickles"),
        ("opcode", 3, "bytecode opcode tables"),
        ("sre_compile", 3, "deprecated alias of `re` internals"),
        ("sre_constants", 3, "deprecated alias of `re` internals"),
        ("sre_parse", 3, "deprecated alias of `re` internals"),
    ]),
    ("Unix only", [
        ("posix", 3, "the raw OS calls behind `os` on Unix"),
        ("pwd", 3, "the password database (users)"),
        ("grp", 3, "the group database"),
        ("termios", 3, "terminal control"),
        ("tty", 3, "raw and cbreak terminal modes"),
        ("pty", 3, "pseudo-terminals"),
        ("fcntl", 3, "file and I/O control, file locks"),
        ("resource", 3, "process resource limits and usage"),
        ("syslog", 3, "the Unix system log"),
    ]),
    ("Windows only", [
        ("msvcrt", 3, "Windows C runtime: console keys, file locking"),
        ("winreg", 3, "the Windows registry"),
        ("winsound", 3, "play sounds on Windows"),
        ("nt", 3, "the raw OS calls behind `os` on Windows"),
        ("nturl2path", 3, "file URL to path conversion (internal)"),
    ]),
]

# names that are ordinary words in prose: only an import statement counts as a reference
AMBIGUOUS = {"code", "this", "string", "token", "site", "copy", "time", "trace", "stat", "cmd", "keyword",
             "resource", "types", "select", "numbers", "queue", "array", "wave", "profile", "platform",
             "calendar", "struct", "random", "operator", "glob", "abc", "html", "signal", "email", "test"}


def public(name):
    return not name.startswith("_") or name == "__future__"


def chapter_refs():
    """{module: [chapter numbers]} from the import statements and backticked names in every chapter's text."""
    here = os.path.dirname(os.path.abspath(__file__))
    known = {m for _, rows in GROUPS for m, _, _ in rows}
    refs = {}
    for path in sorted(glob.glob(os.path.join(here, "c[0-2][0-9]_*.py"))):
        num = int(os.path.basename(path)[1:3])
        if num >= ORDER:
            continue
        tree = ast.parse(open(path, encoding="utf-8").read())
        text = "\n".join(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str))
        found = set()
        for line in re.findall(r"(?m)^\s*import ([\w., ]+)", text):
            found |= {p.strip().split(".")[0] for p in line.split(",")}
        found |= {m.split(".")[0] for m in re.findall(r"(?m)^\s*from ([\w.]+) import", text)}
        for name, nxt in re.findall(r"`([A-Za-z_]\w*)([.`])", text):
            if nxt == "." or name not in AMBIGUOUS:
                found.add(name)
        for m in found & known:
            refs.setdefault(m, []).append(num)
    return refs


def check_complete():
    listed = [m for _, rows in GROUPS for m, _, _ in rows]
    dupes = {m for m in listed if listed.count(m) > 1}
    assert not dupes, f"listed twice: {dupes}"
    names = set(sys.stdlib_module_names)
    missing = sorted(n for n in names if public(n) and n not in listed)
    extra = sorted(set(listed) - names)
    assert not missing, f"atlas is missing {missing}"
    assert not extra, f"atlas lists modules this Python doesn't have: {extra}"
    return sorted(n for n in names if not public(n))


# ----------------------------------------------------------------------------- pictures
def tile_layout(groups, colw, size=7.4):
    """Each group as a tile of module names; returns [(group, height, [(name, tier, dx, dy)])]."""
    out = []
    lh = size + 3.2
    for title, rows in groups:
        x, y, items = 0.0, 17.0, []
        for m, tier, _ in rows:
            w = F.width(m, TIER_FONT[tier], size)
            if x and x + w > colw - 12:
                x, y = 0.0, y + lh
            items.append((m, tier, x, y))
            x += w + 7
        out.append((title, y + lh + 6, items))
    return out


def atlas_map(f, groups, cols=3, size=7.4):
    colw = (W - 8 * (cols - 1)) / cols
    tiles = tile_layout(groups, colw, size)
    heights, place = [0.0] * cols, []
    for title, h, items in tiles:
        k = heights.index(min(heights))
        place.append((k, heights[k], title, h, items))
        heights[k] += h + 7
    y0 = f.reserve(max(heights))
    pg = f.pg
    for k, yy, title, h, items in place:
        x = L + k * (colw + 8)
        pg.rect(x, y0 + yy, colw, h, ACCENT, 0.8, fillcolor="#f7fbfb", r=5)
        pg.text(x + 6, y0 + yy + 4, title, 8.4, ACCENT, F.BOLD)
        for m, tier, dx, dy in items:
            pg.text(x + 6 + dx, y0 + yy + dy, m, size, TIER_COL[tier], TIER_FONT[tier])


def legend(f, counts):
    y = f.reserve(24)
    pg = f.pg
    x = L
    for tier, label in [(1, "tier 1: use it weekly"), (2, "tier 2: know it exists"), (3, "tier 3: map only")]:
        pg.rect(x, y + 3, 12, 12, TIER_COL[tier], 0, fillcolor=C.LIGHT[TIER_COL[tier]], r=3)
        s = f"{label} ({counts[tier]})"
        pg.text(x + 18, y + 2, s, 10.5, TIER_COL[tier], F.BOLD)
        x += 18 + F.width(s, F.BOLD, 10.5) + 22


def group_list(f, title, rows, refs, size=9.3):
    name_w, ch_w = 104, 54
    desc_w = W - name_w - ch_w - 12
    hs = [max(f.pg.rich_h(d, desc_w, size), 12) + 2.5 for _, _, d in rows]
    f.need(22 + sum(hs[:3]))
    y = f.reserve(20)
    pg = f.pg
    pg.rect(L, y, W, 17, ACCENT, 0, fillcolor=C.LIGHT[ACCENT], r=3)
    pg.text(L + 7, y + 2, title, 10, ACCENT, F.BOLD)
    pg.text(R - 7, y + 3, "chapters", 8, C.GREY, align="right")
    for (m, tier, desc), h in zip(rows, hs):
        y = f.reserve(h)
        pg = f.pg
        pg.circle(L + 6, y + 6.5, 2.6, TIER_COL[tier], 0.8, fillcolor=TIER_COL[tier])
        pg.text(L + 14, y + 1, m, 9, TIER_COL[tier] if tier < 3 else C.INK, TIER_FONT[tier])
        pg.rich(L + name_w, y, desc, desc_w, size)
        chs = refs.get(m, [])
        s = " · ".join(map(str, chs[:3])) + (" …" if len(chs) > 3 else "")
        if s:
            pg.text(R - 4, y + 1.5, s, 8.3, C.GREY, align="right")
        pg.line(L + 12, y + h - 1, R, y + h - 1, "#e8ecef", 0.5)
    f.gap(8)


def private_box(f, names, size=7.6):
    colw = W - 16
    lines, x, line = [], 0.0, []
    for n in names:
        w = F.width(n, F.MONO, size)
        if x and x + w > colw:
            lines.append(line)
            line, x = [], 0.0
        line.append((n, x))
        x += w + 7
    lines.append(line)
    lh = size + 3.2
    h = 24 + lh * len(lines) + 6
    y = f.reserve(h + 10)
    pg = f.pg
    pg.rect(L, y, W, h, C.GREY, 0.8, fillcolor="#f6f6f6", r=6)
    pg.text(L + 8, y + 5, f"Underscore modules: private internals and C accelerators ({len(names)})", 9.5,
            C.GREY, F.BOLD)
    for k, line in enumerate(lines):
        for n, dx in line:
            pg.text(L + 8 + dx, y + 22 + k * lh, n, size, C.GREY, F.MONO)


# ----------------------------------------------------------------------------- pages
def build(ch):
    private = check_complete()
    refs = chapter_refs()
    counts = {t: sum(1 for _, rows in GROUPS for _, tier, _ in rows if tier == t) for t in (1, 2, 3)}
    title_block(ch, NUM, TITLE, "know the whole map, learn the roads you use", ACCENT)
    f = ch._flow = ch.flow(top=190)
    f.p(f"Python ships {sum(counts.values())} public modules. Nobody knows them all, and nobody should: the "
        "skill is knowing {B:which one exists for a job} and learning it on demand (Ch 7). This map is "
        "generated from `sys.stdlib_module_names`, so it is complete for the Python that built this book; the "
        "build fails if a module is missing.", 12.5, gap=8)
    legend(f, counts)
    atlas_map(f, GROUPS)

    f = flow(ch)
    section(f, "How to read the lists", ACCENT, room=200)
    f.p("Each job group lists its modules with a tier dot and the chapters of this book that use them (found "
        "automatically from the snippets). Tier 1 is the working set of a Python programmer: learn its API "
        "until you stop looking it up. Tier 2: know what it's for, so you reach for it instead of writing it "
        "yourself. Tier 3: recognise the name.", 12, gap=8)
    code(f, """
        import sys

        names = sorted(sys.stdlib_module_names)
        public = [n for n in names if not n.startswith("_") or n == "__future__"]
        print(sys.version.split()[0], len(names), "names,", len(public), "public")
        print([n for n in public if n.startswith("con")])
    """, size=8.8)
    assert len([n for n in sys.stdlib_module_names if public(n)]) == sum(counts.values())
    callout(f, "rule", "A leading underscore means private. `_json` is the C speed-up that `json` uses when it can, "
            "`_pydecimal` the pure-Python fallback for `decimal`, `_thread` the layer under `threading`. "
            "Import the public module; its internals can change in any release. The grey box lists them only "
            "so the map is complete.", size=11.5)
    private_box(f, private)
    callout(f, "other", "Every language has an atlas like this: the C standard library (small: `stdio.h`, "
            "`stdlib.h`, `string.h`...), Java's `java.base` packages, Rust's `std` modules. Python's is "
            "unusually large (\"batteries included\"), which is why Ch 19's question 'do I need a package at "
            "all?' so often ends with no.", size=11.5)
    for title, rows in GROUPS:
        group_list(f, title, rows, refs)
