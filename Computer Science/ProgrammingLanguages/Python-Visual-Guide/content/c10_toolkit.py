"""Chapter 10 - The algorithm toolkit: collections (Counter, defaultdict, deque, OrderedDict, ChainMap),
heapq, bisect, itertools, functools/operator; with timings showing why the right structure matters."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, W, callout, code, flow, go, pipe, practice, repl, section, stamp, sub, table,
                         title_block, tree, two_ways)

ORDER = 10
NUM = 10
TITLE = "The algorithm toolkit"
SHORT = "Algorithm toolkit"
SLUG = "Algorithm-toolkit"
ACCENT = C.GREEN


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def cells(f, values, color=C.BLUE, highlight=(), marks=None, label=None, size=11, cell=34, arrows=None):
    """A row of array cells with indexes; marks = {index: 'note'} drawn under; arrows = [(x_index, 'text')]."""
    n = len(values)
    total = n * cell
    y = f.reserve(78 if marks else 52)
    pg = f.pg
    x0 = L + (W - total) / 2
    if label:
        pg.text(x0 - 8, y + 9, label, 10, C.GREY, F.BOLD, align="right")
    for i, v in enumerate(values):
        col = C.ORANGE if i in highlight else color
        pg.rect(x0 + i * cell, y, cell, 28, col, 1.1, fillcolor=C.LIGHT[col])
        pg.text(x0 + i * cell + cell / 2, y + 7, str(v), size, C.INK, F.MONO, align="center")
        pg.text(x0 + i * cell + cell / 2, y + 31, str(i), 8, C.GREY, F.MONO, align="center")
    for i, note in (marks or {}).items():
        xi = x0 + i * cell
        pg.arrow(xi, y + 64, xi, y + 30, C.RED, 1.3, head=5)
        if i < n / 2 and len(marks) > 1:
            pg.note(xi - 4, y + 52, note, C.RED, 13, align="right")
        else:
            pg.note(xi + 4, y + 52, note, C.RED, 13)


def title_page(ch):
    title_block(ch, 10, TITLE, "the right container turns a slow program into a fast one", ACCENT)
    f = ch.flow(top=190)
    f.p("Lists, dicts and sets solve most problems. A handful of standard-library modules cover almost "
        "everything else that algorithm courses and interviews ask for. Each one exists because a common "
        "operation is {B:slow} with the obvious structure:", 14, gap=10)
    table(f, ["you need to...", "obvious way", "cost", "use instead", "cost"], [
        ["count things", "dict + `if k in d`", "fiddly", "`collections.Counter`", "O(n)"],
        ["take from the front of a queue", "`list.pop(0)`", "{R:O(n)}", "`deque.popleft()`", "O(1)"],
        ["repeatedly get the smallest", "`min(xs)` then remove", "{R:O(n)}", "`heapq.heappop`", "O(log n)"],
        ["find a position in sorted data", "scan the list", "{R:O(n)}", "`bisect.bisect_left`", "O(log n)"],
        ["test membership many times", "`x in some_list`", "{R:O(n)}", "`x in some_set`", "O(1)"],
        ["every pair / combination", "nested loops", "fiddly", "`itertools.combinations`", "lazy"],
    ], widths=[2.1, 1.7, 0.8, 2.3, 0.9], size=10.5)
    f.p("The difference is not academic. The same job, 50,000 items, measured on this machine while building "
        "the book:", 13.5, gap=8)
    code(f, """
        import time
        from collections import deque

        def drain_list(n):
            q = list(range(n))
            while q:
                q.pop(0)               # shifts every remaining item left

        def drain_deque(n):
            q = deque(range(n))
            while q:
                q.popleft()            # just moves a pointer

        for fn in (drain_list, drain_deque):
            t = time.perf_counter(); fn(50_000); ms = (time.perf_counter() - t) * 1000
            print(f"{fn.__name__:12} {ms:8.1f} ms")
    """)


def collections_section(ch):
    f = flow(ch)
    callout(f, "idea", "Big-O (Ch 20) tells you how the cost grows. O(n) per operation inside a loop of n is "
            "O(n²) overall: 50,000 items means ~1.25 billion element moves. Choosing the structure is the "
            "optimisation; micro-tuning the loop rarely matters.")
    sec(f, "collections: Counter, defaultdict, deque", room=430)
    code(f, """
        from collections import Counter, defaultdict

        words = "the cat and the hat and the bat".split()
        c = Counter(words)
        print(c.most_common(2), c["the"], c["dog"])         # missing keys count as 0
        print(c + Counter(["cat", "dog"]))                    # counters add like multisets

        by_letter = defaultdict(list)                         # missing key -> list() made for you
        for w in words:
            by_letter[w[0]].append(w)
        print(dict(by_letter))
    """)
    two_ways(f, ("plain dict", """
        groups = {}
        for w in "ab ac bd".split():
            if w[0] not in groups:
                groups[w[0]] = []
            groups[w[0]].append(w)
        print(groups)
    """), ("defaultdict", """
        from collections import defaultdict
        groups = defaultdict(list)
        for w in "ab ac bd".split():
            groups[w[0]].append(w)

        print(dict(groups))
    """), verdict=[("lines", 3, 5), ("no magic", 5, 3)])
    sub(f, "deque: a queue with two fast ends", ACCENT)
    cells(f, ["", "a", "b", "c", "d", ""], highlight=(1, 4), marks={1: "popleft() / appendleft()",
                                                                     4: "pop() / append()"})
    code(f, """
        from collections import deque

        recent = deque(maxlen=3)              # keeps only the last 3: older items fall off the left
        for page in ["home", "dune", "emma", "ubik", "kim"]:
            recent.append(page)
        print(recent, recent[0])

        q = deque(["ana", "ben"])
        q.append("cy"); first = q.popleft(); q.rotate(1)
        print(first, q)
    """)
    table(f, ["also in collections", "for"], [
        ["`OrderedDict`", "`move_to_end()`, `popitem(last=False)`: an LRU cache in a few lines (practice 10.6)"],
        ["`ChainMap(a, b)`", "look up in `a`, then `b`: layered config (command line > env > defaults)"],
        ["`namedtuple(\"P\", \"x y\")`", "a tuple with field names (prefer `typing.NamedTuple` or a dataclass)"],
    ], widths=[1.7, 4])


def heap_section(ch):
    f = flow(ch)
    sec(f, "heapq: always know the smallest", room=450)
    f.p("A {B:heap} is a list kept in a special order: every parent is ≤ its children, so the smallest item is "
        "always at index 0. It's a binary tree stored flat in a list: the children of index `i` are at "
        "`2i+1` and `2i+2`. Push and pop are O(log n) because only one root-to-leaf path is fixed up:", 13.5,
        gap=8)
    import heapq
    h = [7, 3, 9, 1, 5, 8, 2]
    heapq.heapify(h)
    nodes = {}
    pos = {0: (0.5, 0), 1: (0.27, 1), 2: (0.73, 1), 3: (0.15, 2), 4: (0.39, 2), 5: (0.61, 2), 6: (0.85, 2)}
    for i, v in enumerate(h):
        nodes[str(i)] = (f"{v}  [{i}]", pos[i][0], pos[i][1])
    edges = [(str((i - 1) // 2), str(i)) for i in range(1, len(h))]
    tree(f, nodes, edges, h=120, size=10.5, col=ACCENT)
    cells(f, h, color=ACCENT, highlight=(0,), label="the list:")
    code(f, """
        import heapq

        h = [7, 3, 9, 1, 5, 8, 2]
        heapq.heapify(h)                          # O(n), in place
        print(h, h[0])
        heapq.heappush(h, 0)
        print([heapq.heappop(h) for _ in range(3)])

        tasks = []                                # (priority, order, item): ties broken by order
        for i, (pri, job) in enumerate([(2, "email"), (1, "backup"), (2, "report")]):
            heapq.heappush(tasks, (pri, i, job))
        print([heapq.heappop(tasks)[2] for _ in range(len(tasks))])

        scores = {"ana": 81, "ben": 67, "cy": 94, "di": 72}
        print(heapq.nlargest(2, scores, key=scores.get))     # top k without a full sort
    """)
    callout(f, "trap", "`heapq` is a {B:min}-heap only. For a max-heap push negated keys (`-score`). And a heap "
            "list is not sorted: only `h[0]` is guaranteed to be the minimum.")


def bisect_section(ch):
    f = flow(ch)
    sec(f, "bisect: binary search in sorted data", room=420)
    f.p("`bisect` finds where a value belongs in a sorted list by halving the search range each step: about "
        "17 steps for 100,000 items instead of up to 100,000:", 13.5, gap=8)
    cells(f, [10, 20, 20, 20, 35, 50], marks={1: "bisect_left(xs, 20) = 1", 4: "bisect_right(xs, 20) = 4"})
    code(f, """
        import bisect

        xs = [10, 20, 20, 20, 35, 50]
        print(bisect.bisect_left(xs, 20), bisect.bisect_right(xs, 20))
        print(bisect.bisect_right(xs, 20) - bisect.bisect_left(xs, 20), "copies of 20")

        bisect.insort(xs, 27)                       # insert keeping it sorted
        print(xs)

        def grade(score, cutoffs=(40, 50, 60, 70), letters="FDCBA"):
            return letters[bisect.bisect_right(cutoffs, score)]
        print([grade(s) for s in (12, 40, 55, 69, 70, 99)])
    """)
    callout(f, "why", "`bisect_left` gives the first position where the value could go (before equal items), "
            "`bisect_right` the last (after them). Their difference counts the equal items; `bisect_right` on "
            "cutoffs turns a chain of `if score >= 70 ... elif` into one line.")


def itertools_section(ch):
    f = flow(ch)
    sec(f, "itertools: loops you don't have to write", room=430)
    code(f, """
        from itertools import (accumulate, chain, combinations, count, groupby, islice,
                               pairwise, permutations, product, batched)

        print(list(combinations("ABC", 2)), len(list(permutations("ABC"))))
        print(list(product("xy", [0, 1])))                       # nested loops, flattened
        print(list(accumulate([3, 1, 4, 1, 5])))                 # running totals
        print(list(pairwise([1, 4, 9, 16])))                     # neighbours
        print(list(batched("ABCDEFG", 3)))                       # chunks (3.12+)
        print(list(islice(count(10, 5), 4)), list(chain("ab", [1, 2])))
    """)
    f.p("`groupby` groups {B:consecutive} equal keys, so it needs sorted input to group everything:", 13.5, gap=6)
    two_ways(f, ("unsorted: surprise", """
        from itertools import groupby
        ws = ["ant", "bee", "ape", "bat"]
        print([(k, len(list(g)))
               for k, g in groupby(ws, key=lambda w: w[0])])
    """), ("sorted first", """
        from itertools import groupby
        ws = sorted(["ant", "bee", "ape", "bat"])
        print([(k, len(list(g)))
               for k, g in groupby(ws, key=lambda w: w[0])])
    """), same_output=False)
    table(f, ["function", "gives", "count for n items"], [
        ["`product(xs, repeat=k)`", "every k-tuple, with repeats, order matters", "nᵏ"],
        ["`permutations(xs, k)`", "ordered arrangements, no repeats", "n! / (n−k)!"],
        ["`combinations(xs, k)`", "unordered selections, no repeats", "n! / (k!(n−k)!)"],
        ["`combinations_with_replacement`", "unordered, repeats allowed", "(n+k−1)! / (k!(n−1)!)"],
    ], widths=[2.7, 2.4, 1.4])
    callout(f, "trap", "These grow explosively: `permutations(range(12))` is 479 million tuples. They're lazy, so "
            "creating one is free, but `list()` on it will exhaust memory. Loop over them and stop early.")


def functools_section(ch):
    f = flow(ch)
    sec(f, "functools and operator", room=380)
    code(f, """
        from functools import reduce, cache, partial, cmp_to_key
        from operator import mul, itemgetter

        print(reduce(mul, range(1, 6)))                          # 1*2*3*4*5

        @cache
        def ways(n):                                             # staircase: 1 or 2 steps at a time
            return 1 if n <= 1 else ways(n - 1) + ways(n - 2)
        print(ways(80))

        def by_length_then_reverse_alpha(a, b):                  # old-style comparator: <0, 0, >0
            return (len(a) - len(b)) or ((a < b) - (a > b))
        print(sorted(["bb", "a", "ccc", "aa"], key=cmp_to_key(by_length_then_reverse_alpha)))

        rows = [("ana", 3), ("ben", 1), ("cy", 2)]
        print(sorted(rows, key=itemgetter(1)), max(rows, key=itemgetter(1))[0])
    """)
    table(f, ["structure", "add", "remove", "find min/max", "x in s", "notes"], [
        ["`list`", "O(1) end", "O(n) front", "O(n)", "O(n)", "indexing O(1)"],
        ["`deque`", "O(1) both ends", "O(1) both ends", "O(n)", "O(n)", "indexing middle O(n)"],
        ["`dict` / `set`", "O(1)", "O(1)", "O(n)", "{G:O(1)}", "hashable keys; order kept (dict)"],
        ["`heapq` list", "O(log n)", "O(log n) min", "{G:O(1)} min", "O(n)", "min-heap only"],
        ["sorted list + `bisect`", "O(n) insort", "O(n)", "O(1) ends", "O(log n)", "great when read-mostly"],
    ], widths=[1.6, 1.2, 1.3, 1.1, 1.1, 2.1], size=10)


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 10)
    stamp(f, [
        (5, "Beyond list/dict/set: `Counter`, `defaultdict`, `deque`, `OrderedDict`, `heapq` (min-heap on a "
            "list), `bisect` (binary search), lazy `itertools`, `functools.cache`/`reduce`."),
        (11, "Know each structure's costs; pick by the operation you do most."),
    ])
    callout(f, "other", "Every language ships the same toolkit under other names: Java `ArrayDeque`, "
            "`PriorityQueue`, `Collections.binarySearch`, `HashMap`; C++ `std::deque`, `std::priority_queue` "
            "(a max-heap!), `std::lower_bound`; Rust `VecDeque`, `BinaryHeap`, `slice::binary_search`.")
    callout(f, "deep", "Vault notes: {b:7.2} A minimal cost vocabulary · {b:7.10} Choosing among sequence "
            "representations · {b:7.11} Sorting and ordering contracts · {b:7.15} A structure-selection case "
            "study · {b:11.11} collections · {b:11.12} itertools · {b:11.13} functools.")


def build(ch):
    title_page(ch)
    collections_section(ch)
    heap_section(ch)
    bisect_section(ch)
    itertools_section(ch)
    functools_section(ch)
    finish(ch)
