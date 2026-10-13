"""Appendix C - glossary: one line per term, with the chapters that teach it. The build checks that every
term (or one of its aliases) really appears in each chapter it cites."""
import ast
import glob
import os

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, title_block

ORDER = 24
NUM = "C"
TITLE = "Glossary"
SHORT = "Glossary"
SLUG = "Glossary"
ACCENT = C.BROWN

# (term, chapters, definition, aliases searched for when checking the chapters)
TERMS = [
    ("abstract base class", [5], "a class that declares methods its subclasses must provide; it can't be instantiated itself", ("abc",)),
    ("adjacency list", [21], "a graph stored as a dict from each node to the list of its neighbours", ("neighbour lists",)),
    ("aliasing", [3], "two names referring to one object, so a change made through one is seen through the other", ("alias",)),
    ("amortised cost", [20], "the average cost per operation over a long run: `list.append` is O(1) amortised despite occasional resizes", ("amortised",)),
    ("argv", [14], "the list of command-line arguments; `sys.argv[0]` is the program itself", ()),
    ("aware datetime", [11], "a datetime that carries a time zone; a naive one doesn't, and the two can't be compared", ("aware",)),
    ("atomic write", [8], "write a temporary file, then `os.replace` it, so readers see the old file or the new one, never half", ("os.replace",)),
    ("base case", [20], "the input a recursive function answers directly, without recursing", ()),
    ("base64", [13], "an encoding of bytes as ASCII text; anyone can decode it, so it is not encryption", ()),
    ("big-O", [20], "how cost grows with input size, ignoring constant factors: O(1), O(log n), O(n), O(n log n), O(n²)", ("o(n)",)),
    ("binary search", [10, 20], "find a position in sorted data by halving the range each step: O(log n)", ("bisect",)),
    ("breadth-first search", [21], "explore a graph in rings of distance using a queue; finds the fewest edges", ("bfs",)),
    ("broadcasting", [18], "NumPy's rule for combining arrays of different shapes by stretching size-1 axes", ()),
    ("bytecode", [2], "the instructions CPython compiles source to and its virtual machine runs (cached in .pyc files)", ()),
    ("bytes", [8, 13], "an immutable sequence of integers 0-255: what files, sockets and hashes really hold", ()),
    ("call stack", [6, 20], "the stack of frames for the calls in progress; each call pushes a frame, each return pops it", ("frame",)),
    ("closure", [4], "a function that remembers variables from the scope where it was defined", ()),
    ("code point", [9], "the number Unicode assigns to a character; a `str` is a sequence of code points", ()),
    ("comprehension", [1], "an expression building a list, dict or set from a loop: `[x * x for x in xs if x]`", ()),
    ("context manager", [6], "an object used with `with` whose `__exit__` runs however the block ends", ()),
    ("coroutine", [16], "an `async def` function's object; it runs until an `await`, letting the event loop run others", ()),
    ("cursor", [12], "the object that executes SQL and walks through the result rows", ()),
    ("cycle collector", [3], "the part of the garbage collector that frees groups of objects referring only to each other", ("cycles",)),
    ("dataclass", [5], "a class whose `__init__`, `__repr__` and `__eq__` are generated from its field declarations", ()),
    ("decorator", [4], "a function that takes a function and returns a replacement, applied with `@name`", ()),
    ("deep copy", [3], "a copy of an object and, recursively, everything it refers to (`copy.deepcopy`)", ("deepcopy",)),
    ("depth-first search", [21], "explore a graph as far as possible along each branch before backing up, using a stack", ("dfs",)),
    ("dict", [1, 10], "a hash table from keys to values; O(1) lookup on average, remembers insertion order", ()),
    ("Dijkstra's algorithm", [21], "cheapest paths from one node when weights are non-negative, using a heap", ("dijkstra",)),
    ("duck typing", [5], "using an object for what it can do (its methods), not for what class it is", ()),
    ("dunder method", [5], "a `__double_underscore__` method Python calls for syntax: `__len__`, `__eq__`, `__iter__`", ("dunder",)),
    ("dynamic programming", [20, 21], "solve each overlapping subproblem once and reuse the answer: memoised recursion or a table", ()),
    ("EAFP", [6], "'easier to ask forgiveness than permission': try the operation and handle the exception", ()),
    ("edit distance", [21], "the fewest single-character inserts, deletes and replacements turning one string into another", ()),
    ("encoding", [8, 13], "the rule turning text into bytes and back; UTF-8 unless you have a reason", ()),
    ("environment variable", [14], "a name-value string a process inherits from its parent (`os.environ`)", ("os.environ",)),
    ("event loop", [16], "asyncio's scheduler: runs ready tasks, and switches at every `await` that has to wait", ()),
    ("exception", [6], "an object raised to signal an error; it unwinds the stack until an `except` matches", ()),
    ("exit code", [14], "the number a process returns to the OS: 0 for success, anything else for failure", ()),
    ("f-string", [9], "a string literal with `{expressions}` and format specs: `f\"{total:,.2f}\"`", ("format spec",)),
    ("foreign key", [12], "a column referring to another table's primary key, so rows link by id", ()),
    ("framing", [15], "marking where each message ends in a byte stream such as TCP (lines, length prefixes)", ()),
    ("free-threaded build", [16], "a CPython build without the GIL (3.13 onwards), so threads can run Python in parallel", ("free-threaded",)),
    ("generator", [4], "a function with `yield`; calling it returns an iterator that runs the body lazily", ()),
    ("GIL", [16], "the global interpreter lock: on the default build, one thread runs Python bytecode at a time", ()),
    ("graph", [21], "nodes joined by edges, directed or not, possibly weighted", ()),
    ("greedy algorithm", [21], "always take the best-looking choice now; correct only when that choice can be proved safe", ("greedy",)),
    ("hash function", [13], "a function from data to a fixed-size digest; cryptographic ones make collisions infeasible", ("hashlib",)),
    ("hashable", [3, 5], "has a hash that never changes, so it can be a dict key or set member", ()),
    ("heap", [10, 21], "a tree stored in a list where every parent is <= its children; `heapq` pops the smallest in O(log n)", ("heapq",)),
    ("HMAC", [13], "a tag made from a message and a secret key; proves the message is intact and from a key holder", ()),
    ("HTTP", [15], "the text request-response protocol of the web: method, path, headers, body, status code", ()),
    ("immutable", [3], "can't be changed after creation (int, str, tuple, frozenset); 'changes' make new objects", ()),
    ("index (database)", [12], "a sorted structure (a B-tree) that lets a query find rows without scanning the table", ("index",)),
    ("interpreter", [14, 16], "the program that runs Python code: `python3` is CPython's interpreter", ()),
    ("invariant", [20], "a statement that is true before and after every step of a loop or method", ()),
    ("iterator", [4], "an object with `__next__` that hands out values one at a time; iterables make iterators", ("iterable",)),
    ("join", [12], "an SQL query combining rows of two tables where a condition (usually key = foreign key) holds", ()),
    ("JSON", [8], "a text format for nested lists, dicts, strings, numbers, booleans and null", ()),
    ("LEGB", [4], "the order Python looks names up: Local, Enclosing, Global, Built-in", ()),
    ("library card", [7], "this book's six questions for learning any library", ()),
    ("linked list", [20], "nodes each holding a value and a reference to the next; O(1) insert at a known node, O(n) indexing", ()),
    ("lock", [16], "lets one thread at a time into a critical section (`threading.Lock`)", ()),
    ("lock file", [19], "exact versions and hashes of every dependency, so installs are reproducible", ()),
    ("memoisation", [20, 21], "caching a function's results by argument (`functools.cache`)", ("cache",)),
    ("merge sort", [20], "split in half, sort each half, merge: O(n log n), stable", ()),
    ("method resolution order", [5], "the order classes are searched for an attribute (C3 linearisation; `Class.__mro__`)", ("mro",)),
    ("mock", [17], "a stand-in object that records calls and returns canned answers in a test", ("test double",)),
    ("module", [2, 7], "a `.py` file (or compiled extension) loaded by `import`; a package is a folder of modules", ()),
    ("mutable", [3], "can be changed in place (list, dict, set, most instances)", ()),
    ("ndarray", [18], "NumPy's n-dimensional array: one typed buffer plus a header of dtype, shape and strides", ()),
    ("normalisation", [9, 12], "Unicode: one canonical form for equal-looking text (NFC). Databases: each fact stored once", ()),
    ("parameter binding", [12], "passing values to SQL through `?` placeholders, never by building strings: stops injection", ("placeholder",)),
    ("passport", [0], "this book's twelve questions for understanding any programming language", ()),
    ("pickle", [8], "Python's object serialiser; loading a pickle can run arbitrary code, so never load untrusted ones", ()),
    ("pip", [19], "the installer that resolves, downloads, verifies and unpacks packages into an environment", ()),
    ("process", [14, 16], "a running program with its own memory; processes don't share objects", ()),
    ("protocol", [5, 17], "a set of methods a type must have to be used somewhere (iteration, `typing.Protocol`)", ()),
    ("pseudo-random", [11], "numbers from a deterministic generator: reproducible with a seed, predictable, so not for secrets", ("pseudo",)),
    ("race condition", [16], "a bug where the result depends on how threads' steps interleave", ("race",)),
    ("recursion", [20], "a function solving a problem by calling itself on smaller inputs", ()),
    ("reference count", [3], "how many references point at an object; at zero CPython frees it at once", ()),
    ("regular expression", [9], "a pattern language for matching text (`re`)", ()),
    ("salt", [13], "random bytes stored with a password hash so equal passwords hash differently", ()),
    ("scope", [4], "the region of code where a name is visible", ()),
    ("secrets", [11, 13], "the module for unguessable random values (tokens, passwords); `random` is not safe for these", ()),
    ("shallow copy", [3], "a new container holding the same element objects (`list(xs)`, `xs.copy()`, `copy.copy`)", ("shallow",)),
    ("signal", [14], "an asynchronous notification from the OS to a process (SIGINT on Ctrl-C, SIGTERM)", ()),
    ("socket", [15], "an endpoint for network communication; TCP sockets carry a byte stream", ()),
    ("spike", [7], "a throwaway 20-line program written to answer one question about a library", ()),
    ("SQL injection", [12], "attacker text ending a string inside an SQL statement and adding its own commands", ("injection",)),
    ("stable sort", [20], "a sort that keeps equal items in their original order (Python's always is)", ("stable",)),
    ("stack", [21], "last in, first out; a Python list with `append` and `pop`", ()),
    ("stderr", [14], "the stream for messages and errors; stdout is for results, so pipes stay clean", ()),
    ("stride", [18], "how many bytes to step in memory to move one place along an array axis", ("strides",)),
    ("subprocess", [14], "running another program from Python and collecting its output and exit code", ()),
    ("supply-chain attack", [19], "attacking users through a dependency: typosquatted names, hijacked or malicious packages", ("supply-chain",)),
    ("TCP", [15], "the reliable, ordered byte-stream protocol under HTTP, SMTP and most of the internet", ()),
    ("thread", [16], "a line of execution inside a process; threads share memory", ()),
    ("timing attack", [13], "learning a secret from how long a comparison takes; prevented by `hmac.compare_digest`", ("compare_digest",)),
    ("Timsort", [20], "Python's sort: a merge sort that exploits runs already in order", ()),
    ("TLS", [15], "encryption and server authentication for a TCP connection (the S in HTTPS)", ()),
    ("topological order", [21], "an order of a directed graph's nodes where every edge points forward; exists only without cycles", ()),
    ("traceback", [6], "the printed stack of calls that led to an exception, oldest first", ()),
    ("transaction", [12], "a group of changes that commit together or not at all", ()),
    ("tree", [20], "nodes with children and no cycles; in a binary search tree, left < node < right", ()),
    ("type hint", [17], "an annotation like `def f(x: int) -> str`; checked by tools, ignored when running", ()),
    ("Unicode", [9], "the standard numbering every character in every script", ()),
    ("unit test", [17], "a test of one small piece of code in isolation", ("unit",)),
    ("UTC", [11], "Coordinated Universal Time; store and compute in UTC, convert to local time for display", ()),
    ("vectorisation", [18], "replacing Python loops with whole-array operations that run in compiled code", ("vectorise",)),
    ("view", [18], "an array sharing another array's buffer: changing one changes the other", ()),
    ("virtual environment", [2, 19], "a folder with its own site-packages so each project has its own dependencies", ("venv",)),
    ("wheel", [17, 19], "a built package file (.whl) that pip unpacks without running any setup code", ()),
]


def chapter_text():
    here = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for path in sorted(glob.glob(os.path.join(here, "c[0-2][0-9]_*.py"))):
        num = int(os.path.basename(path)[1:3])
        if num >= 22:
            continue
        tree = ast.parse(open(path, encoding="utf-8").read())
        out[num] = "\n".join(n.value for n in ast.walk(tree)
                             if isinstance(n, ast.Constant) and isinstance(n.value, str)).lower()
    return out


def check_refs():
    text = chapter_text()
    bad = []
    for term, chs, _, aliases in TERMS:
        words = [term.lower(), *aliases]
        for n in chs:
            if not any(w in text[n] for w in words):
                where = [k for k, t in text.items() if any(w in t for w in words)]
                bad.append(f"{term!r} not in ch {n} (found in {where})")
    assert not bad, "glossary references:\n" + "\n".join(bad)


def entries(f, terms, size=9.6):
    term_w = 128
    def_w = W - term_w - 48
    letter = None
    for term, chs, meaning, _ in sorted(terms, key=lambda t: t[0].lower()):
        term_h = F.line_h(F.BOLD, 9.8) * len(F.wrap(term, F.BOLD, 9.8, term_w - 8))
        h = max(f.pg.rich_h(meaning, def_w, size), term_h, 12) + 5
        first = term[0].upper()
        if first != letter:
            f.need(22 + h)
            y = f.reserve(20)
            pg = f.pg
            pg.text(L, y, first, 13, ACCENT, F.BOLD)
            pg.line(L + 16, y + 9, R, y + 9, C.LIGHT[ACCENT], 1.2)
            letter = first
        y = f.reserve(h)
        pg = f.pg
        pg.text(L + 4, y + 0.5, term, 9.8, C.INK, F.BOLD, w=term_w - 8)
        pg.rich(L + term_w, y, meaning, def_w, size)
        pg.text(R, y + 1.5, " · ".join(map(str, chs)), 8.5, C.GREY, align="right")


def build(ch):
    check_refs()
    title_block(ch, NUM, TITLE, "the words, in one line each, and where to read more", ACCENT)
    f = ch._flow = ch.flow(top=190)
    f.p(f"{len(TERMS)} terms, each with the chapters that teach it (grey numbers on the right). One line is a "
        "reminder, not an explanation: if a definition doesn't click, read the chapter, then the vault notes "
        "listed in its deep-dive box.", 12.5, gap=12)
    entries(f, TERMS)
