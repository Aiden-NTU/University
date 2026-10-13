"""Chapter 20 - Cost, recursion, linked structures and trees: counting steps, Big-O and Python's real costs,
amortised append, the call stack, memoisation, merge sort, binary search with an invariant, linked lists
and binary search trees."""
import math
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from generator import canvas as C  # noqa: E402
from generator import fonts as F  # noqa: E402
from content.kit import (L, R, W, callout, code, flow, practice, section, stamp, sub, table,  # noqa: E402
                         title_block, trace, tree)

ORDER = 20
NUM = 20
TITLE = "Cost, recursion, links and trees"
SHORT = "Algorithms I"
SLUG = "Algorithms-I"
ACCENT = C.PURPLE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def plot(f, fig, w=W * 0.86):
    fw, fh = fig.get_size_inches()
    h = w * fh / fw
    y = f.reserve(h + 12)
    f.pg.mpl(fig, L + (W - w) / 2, y, w)


# ----------------------------------------------------------------------------- pictures
def growth_plot(f):
    """Real step counts from the three duplicate checkers, for growing n."""
    ns = f.ch._ns
    import random
    rng = random.Random(2)
    sizes = list(range(200, 2001, 200))
    rows = {"every pair": [], "sort first": [], "set": []}
    for n in sizes:
        xs = rng.sample(range(10 * n), n)
        rows["every pair"].append(ns["by_pairs"](xs))
        rows["sort first"].append(ns["by_sorting"](xs))
        rows["set"].append(ns["by_set"](xs))
    fig, ax = plt.subplots(figsize=(6, 1.75))
    for (name, ys), col in zip(rows.items(), ["#c0392b", "#8e44ad", "#16a085"]):
        ax.plot(sizes, ys, lw=2, color=col, marker="o", ms=3)
        ax.annotate(f"{name}: {ys[-1]:,} steps", (sizes[-1], ys[-1]), xytext=(8, -3), textcoords="offset points",
                    fontsize=8, color=col)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(180, 5200)
    ax.set_xticks([200, 500, 1000, 2000], ["200", "500", "1000", "2000"])
    ax.set_xlabel("n (log scale)", fontsize=8)
    ax.set_ylabel("steps (log scale)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.minorticks_off()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    plot(f, fig, w=W * 0.9)


def growth_table(f):
    def fmt(lg):
        return f"{10 ** lg:,.0f}" if lg < 7 else f"≈ 10^{lg:,.0f}"

    lg2 = math.log10(2)
    classes = [("O(1)", "dict lookup", lambda n: 0), ("O(log n)", "binary search", lambda n: math.log10(math.log2(n))),
               ("O(n)", "one loop", lambda n: math.log10(n)),
               ("O(n log n)", "sorting", lambda n: math.log10(n * math.log2(n))),
               ("O(n²)", "every pair", lambda n: 2 * math.log10(n)),
               ("O(2ⁿ)", "every subset", lambda n: n * lg2)]
    rows = [[name, ex] + [fmt(fn(n)) for n in (10, 1000, 1_000_000)] for name, ex, fn in classes]
    table(f, ["class", "example", "n = 10", "n = 1,000", "n = 1,000,000"], rows,
          widths=[1.3, 1.7, 1.1, 1.5, 1.7], size=10.5, mono=(0, 2, 3, 4))


def capacity_plot(f):
    """Allocated slots vs items, read from sys.getsizeof on the list as it grows."""
    empty = sys.getsizeof([])
    xs, lens, caps = [], [], []
    for i in range(1, 301):
        xs.append(i)
        lens.append(i)
        caps.append((sys.getsizeof(xs) - empty) // 8)
    fig, ax = plt.subplots(figsize=(6, 1.9))
    ax.step(lens, caps, where="post", color="#8e44ad", lw=2, label="room allocated")
    ax.plot(lens, lens, color="#999999", lw=1, ls="--", label="items stored")
    ax.set_xlabel("len(xs)", fontsize=8)
    ax.set_ylabel("slots", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    plot(f, fig, w=W * 0.78)


def stack_picture(f):
    """The call stack at its deepest moment while counting books on a nested shelf."""
    frames = [("count_books(['Dune', ['Emma', ['Ubik']]])", "total = 1  (Dune done)"),
              ("count_books(['Emma', ['Ubik']])", "total = 1  (Emma done)"),
              ("count_books(['Ubik'])", "total = 0"),
              ("count_books('Ubik')", "base case: return 1")]
    returns = [None, "2", "1", "1"]
    y = f.reserve(len(frames) * 34 + 30)
    pg = f.pg
    pg.text(L, y, "the call stack at its deepest (each call has its own frame and its own total)", 9.5, C.GREY,
            F.BOLD)
    for k, (call, local) in enumerate(frames):
        x, fy = L + k * 22, y + 18 + k * 34
        col = C.ORANGE if k == len(frames) - 1 else ACCENT
        w = 330
        pg.rect(x, fy, w, 28, col, 1.2, fillcolor=C.LIGHT[col], r=5)
        pg.text(x + 8, fy + 3, call, 8.6, C.INK, F.MONO)
        pg.text(x + 8, fy + 15, local, 8.2, col, F.MONO)
        if returns[k]:
            pg.arrow(x + w + 4, fy + 10, x + w - 18, fy - 16, C.GREEN, 1.1, bend=-0.4, head=5)
            pg.note(x + w + 10, fy - 6, f"later returns {returns[k]}" if k < 3 else "returns 1", C.GREEN, 12)


def fib_tree(f):
    """fib(5)'s call tree: every repeated subproblem drawn in orange."""
    nodes, edges, order, seen = {}, [], [], set()

    def walk(n, parent, depth):
        nid = f"n{len(nodes)}"
        repeat = n in seen
        seen.add(n)
        nodes[nid] = None
        if n >= 2:
            walk(n - 1, nid, depth + 1)
        order.append(nid)
        nodes[nid] = (n, repeat, depth)
        if n >= 2:
            walk(n - 2, nid, depth + 1)
        if parent:
            edges.append((parent, nid))

    walk(5, None, 0)
    out = {}
    for rank, nid in enumerate(order):
        n, repeat, depth = nodes[nid]
        out[nid] = ((f"f({n})", C.ORANGE) if repeat else f"f({n})", 0.04 + 0.92 * rank / (len(order) - 1), depth)
    tree(f, out, edges, size=9, row_h=32, col=ACCENT, gap=8)
    return sum(1 for n, rep, _ in nodes.values() if rep)


def merge_picture(f):
    """Split down to single items, then merge back up: log2(n) levels, n work per level."""
    data = [5, 2, 8, 1, 9, 3, 7, 4]
    split = [[data], [data[:4], data[4:]], [data[i:i + 2] for i in range(0, 8, 2)], [[v] for v in data]]
    merge = [[sorted(g) for g in split[2]], [sorted(g) for g in split[1]], [sorted(data)]]
    rows = [(r, ACCENT) for r in split] + [(r, C.GREEN) for r in merge]
    cell, gap, rh = 20, 12, 25
    y = f.reserve(len(rows) * rh + 8)
    pg = f.pg
    cx = L + 150
    for k, (groups, col) in enumerate(rows):
        total = 8 * cell + (len(groups) - 1) * gap
        x = cx - total / 2
        for g in groups:
            for v in g:
                pg.rect(x, y + k * rh, cell, 19, col, 1.0, fillcolor=C.LIGHT[col], r=2)
                pg.text(x + cell / 2, y + k * rh + 3, str(v), 9.5, C.INK, F.MONO, align="center")
                x += cell
            x += gap
    pg.line(L + 290, y + 2, L + 290, y + 4 * rh - 8, ACCENT, 1.2)
    pg.note(L + 300, y + 22, "split: halve until each piece\nhas one item (log₂ 8 = 3 levels)", ACCENT, 13)
    pg.line(L + 290, y + 4 * rh, L + 290, y + 7 * rh - 6, C.GREEN, 1.2)
    pg.note(L + 300, y + 4 * rh + 8, "merge: each level walks all\n8 items once, so n × log n", C.GREEN, 13)


def linked_picture(f, rows):
    """rows: [(label, [values])]: head -> [value | next] -> ... -> None."""
    rh = 40
    y = f.reserve(len(rows) * rh + 4)
    pg = f.pg
    for k, (label, values) in enumerate(rows):
        yy = y + k * rh
        pg.text(L, yy + 6, label, 9.5, C.GREY, F.BOLD)
        x = L + 110
        pg.text(x, yy + 6, "head", 9.5, C.INK, F.MONO)
        x += 36
        pg.arrow(x, yy + 13, x + 18, yy + 13, C.ORANGE, 1.2, head=5)
        x += 20
        for v in values:
            pg.rect(x, yy + 2, 50, 22, ACCENT, 1.2, fillcolor=C.LIGHT[ACCENT], r=3)
            pg.text(x + 25, yy + 6, v, 9.5, C.INK, F.MONO, align="center")
            pg.rect(x + 50, yy + 2, 20, 22, ACCENT, 1.2, fillcolor="#ffffff", r=3)
            pg.dot(x + 60, yy + 13, 2.4, C.ORANGE)
            pg.arrow(x + 61, yy + 13, x + 86, yy + 13, C.ORANGE, 1.1, head=5)
            x += 88
        pg.text(x, yy + 6, "None", 9.5, C.GREY, F.MONO)


def bst_picture(f, root, mark=()):
    nodes, edges, order = {}, [], []

    def walk(n, depth, parent):
        if n is None:
            return
        walk(n.left, depth + 1, n.key)
        order.append((n.key, depth))
        if parent is not None:
            edges.append((str(parent), str(n.key)))
        walk(n.right, depth + 1, n.key)

    walk(root, 0, None)
    for rank, (key, depth) in enumerate(order):
        lab = (str(key), C.ORANGE) if key in mark else str(key)
        nodes[str(key)] = (lab, 0.1 + 0.8 * rank / (len(order) - 1), depth)
    tree(f, nodes, edges, size=10, row_h=36, col=ACCENT, gap=8)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 20, TITLE, "count the steps, and the seconds take care of themselves", ACCENT)
    f = ch._flow = ch.flow(top=190)
    f.p("A faster computer buys you a constant factor. A better algorithm changes the {B:shape} of the cost. "
        "Here is one question, \"does this list contain a duplicate?\", answered three ways, with the steps "
        "each one takes counted rather than timed:", 14, gap=10)
    code(f, """
        import random
        from functools import cmp_to_key

        def by_pairs(xs):                  # compare every pair
            steps = 0
            for i, a in enumerate(xs):
                for b in xs[i + 1:]:
                    steps += 1
                    if a == b:
                        return steps
            return steps

        def by_sorting(xs):                # sort, then compare neighbours
            steps = 0
            def cmp(a, b):
                nonlocal steps
                steps += 1
                return (a > b) - (a < b)
            sorted(xs, key=cmp_to_key(cmp))
            return steps + len(xs) - 1

        def by_set(xs):                    # one hash lookup per item
            return len(xs)

        rng = random.Random(1)
        for n in (250, 500, 1000, 2000):
            xs = rng.sample(range(10 * n), n)          # no duplicates: the worst case
            print(f"{n:>5} {by_pairs(xs):>10,} {by_sorting(xs):>7,} {by_set(xs):>6,}")
    """, size=8.6, notes={17: "counts each comparison Timsort makes"})
    growth_plot(f)
    f.p("Double n and the pair-checker does {B:four times} the work, sorting a bit more than twice, the set "
        "exactly twice. On log scales that shows up as the {B:slope}: 2 for n², 1 for n. That ratio, not the "
        "seconds on one machine, is what Big-O describes.", 13.5, gap=8)


def bigo_section(f):
    sec(f, "Big-O: keep the term that wins", room=300)
    f.p("Big-O names how the steps grow as n grows, ignoring constant factors and smaller terms. "
        "`3n² + 50n + 7` is O(n²) because for large n the n² term is all that matters:", 13.5, gap=8)
    growth_table(f)
    callout(f, "rule", "Steps in sequence {B:add} (keep the biggest). Loops {B:multiply}: a loop of n around an "
            "O(n) body is O(n²). A {B:call counts with its own cost}: `x in some_list` inside a loop is a hidden "
            "inner loop. Halving the problem each step gives a log n.")
    sub(f, "What Python's own operations cost", ACCENT)
    table(f, ["structure", "O(1)", "O(n) or worse"], [
        ["`list`", "`xs[i]`, `xs[i] = v`, `append`, `pop()`, `len`",
         "`insert(0, v)`, `pop(0)`, `x in xs`, `remove`, `xs[a:b]` copies, `sort` O(n log n)"],
        ["`dict` / `set`", "`d[k]`, `k in d`, `d[k] = v`, `del d[k]` (on average)",
         "iterating; a worst case of O(n) when many keys collide"],
        ["`deque`", "`append`, `appendleft`, `pop`, `popleft`", "`dq[i]` near the middle"],
        ["`str`", "`s[i]`, `len(s)`", "`s + t` copies both; `+=` in a loop can be O(n²): use `\"\".join`"],
    ], widths=[1.1, 2.6, 3.6], size=10)
    f.p("Measure to check a claim: double n and look at the ratio of the times. About 2 means linear, about 4 "
        "means quadratic:", 13.5, gap=8)
    code(f, """
        import timeit

        for fn in (by_pairs, by_set):
            times = []
            for n in (500, 1000, 2000):
                xs = list(range(n))
                times.append(min(timeit.repeat(lambda: fn(xs), number=1, repeat=3)))
            ratios = [f"x{b / a:.1f}" for a, b in zip(times, times[1:])]
            print(f"{fn.__name__:9} each doubling: {' '.join(ratios)}")
    """, notes={7: "best of 3 runs"})
    callout(f, "honest", "Big-O hides constants, and constants matter at small n: `sorted()` on 20 items beats "
            "any clever structure. It also hides the machine: memory locality (Ch 18) and C-level loops can make "
            "an O(n) built-in faster than an O(log n) pure-Python one for every n you'll actually meet. Use Big-O "
            "to rule out designs, then measure (Ch 17).")


def amortised_section(f):
    sec(f, "Amortised: why append is O(1) on average", room=380)
    f.p("A list is an array of pointers with spare room at the end. When the room runs out, CPython allocates a "
        "bigger block and copies everything across: an O(n) step. It doesn't happen often, because each new "
        "block is about 1/8 larger than needed plus a little:", 13.5, gap=8)
    code(f, """
        import sys

        xs, last = [], sys.getsizeof([])
        for i in range(40):
            xs.append(i)
            size = sys.getsizeof(xs)
            if size != last:                     # a new, bigger block was allocated
                room = (size - sys.getsizeof([])) // 8
                print(f"len {len(xs):>2}: room for {room} items")
                last = size
    """, notes={8: "8 bytes per pointer"})
    capacity_plot(f)
    callout(f, "idea", "{B:Amortised} cost spreads the rare expensive step over the many cheap ones. Because the "
            "block grows by a fixed {B:fraction}, the copying adds up to a constant number of moves per append, "
            "however long the list gets. Growing by a fixed {B:amount} instead (say +10 each time) would make "
            "append O(n) on average.")


def recursion_section(f):
    sec(f, "Recursion: a function that trusts itself", room=420)
    f.p("A recursive function solves a problem by solving {B:smaller} copies of the same problem, and stops at "
        "a {B:base case} small enough to answer directly. Nested data is the natural fit: a shelf holds books "
        "and boxes, and a box is a smaller shelf.", 13.5, gap=8)
    code(f, """
        def count_books(shelf):
            if isinstance(shelf, str):          # base case: a single book
                return 1
            total = 0
            for item in shelf:                  # each item is a smaller shelf
                total += count_books(item)
            return total

        print(count_books(["Dune", ["Emma", ["Ubik"]]]))
    """)
    stack_picture(f)
    callout(f, "rule", "Write recursion in three checks: (1) the base case returns without recursing, (2) every "
            "recursive call gets a {B:strictly smaller} input, (3) assuming the smaller calls are right, this call "
            "combines them correctly. That last step is proof by induction ({b:13.5} Correctness through "
            "invariants and induction).")
    f.p("Each call is a new {B:frame} on the call stack (Ch 2), holding its own local variables, so the four "
        "`total`s never interfere. Python limits the stack's depth, and has no tail-call optimisation, so deep "
        "data needs a loop with an explicit stack instead:", 13.5, gap=8)
    code(f, """
        import sys

        def count_books_loop(shelf):
            stack, total = [shelf], 0
            while stack:
                item = stack.pop()
                if isinstance(item, str):
                    total += 1
                else:
                    stack.extend(item)          # look inside this box later
            return total

        deep = "Dune"
        for _ in range(5000):
            deep = [deep]                       # a book inside 5000 boxes
        print(sys.getrecursionlimit(), count_books_loop(deep))
        try:
            count_books(deep)
        except RecursionError as e:
            print("RecursionError:", e)
    """, notes={4: "the stack is now a list we own"})


def memo_section(f):
    sec(f, "Memoisation: never solve the same problem twice", room=300)
    f.p("The textbook Fibonacci definition calls itself twice, and the two calls overlap. Drawn out, `fib(5)` "
        "recomputes the same values again and again (orange):", 13.5, gap=8)
    repeats = fib_tree(f)
    code(f, """
        from functools import cache

        calls = 0
        def fib(n):
            global calls
            calls += 1
            return n if n < 2 else fib(n - 1) + fib(n - 2)

        print(fib(20), calls)                    # exponential: about 1.6^n calls

        @cache                                   # remember every answer by its argument
        def fast(n):
            return n if n < 2 else fast(n - 1) + fast(n - 2)

        print(fast(20), fast.cache_info())
        print(len(str(fast(500))), "digits, instantly")
    """, notes={7: f"{repeats} of fib(5)'s 15 calls are repeats"})
    callout(f, "idea", "`@cache` (or `@lru_cache(maxsize=N)` to bound memory) stores results in a dict keyed by the "
            "arguments, so the arguments must be hashable. Overlapping subproblems plus caching is the core of "
            "{B:dynamic programming}, Ch 21.")


def merge_section(f):
    sec(f, "Divide and conquer: merge sort", room=440)
    f.p("Split the list in half, sort each half (recursively), then {B:merge} two sorted lists by repeatedly "
        "taking the smaller front item. Splitting takes log₂ n levels, and every level merges all n items:",
        13.5, gap=8)
    merge_picture(f)
    code(f, """
        def merge_sort(xs):
            if len(xs) <= 1:
                return xs
            mid = len(xs) // 2
            left, right = merge_sort(xs[:mid]), merge_sort(xs[mid:])
            out, i, j = [], 0, 0
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    out.append(left[i]); i += 1
                else:
                    out.append(right[j]); j += 1
            return out + left[i:] + right[j:]

        print(merge_sort([5, 2, 8, 1, 9, 3, 7, 4]))
        loans = [("ana", 3), ("ben", 1), ("cy", 3), ("di", 1)]
        print(sorted(loans, key=lambda p: p[1]))       # stable: ana stays before cy
    """, notes={8: "<= keeps equal items in order", 12: "one side may have leftovers"})
    callout(f, "why", "Python's `sorted` is {B:Timsort}: merge sort that first finds runs already in order, so "
            "nearly-sorted data sorts in close to O(n). Like this merge sort it is {B:stable}: equal keys keep "
            "their order, which lets you sort by one key and then another. No comparison sort can beat "
            "O(n log n) in the worst case ({b:13.8} Comparison sorting).")


def invariant_section(f):
    sec(f, "Invariants: binary search you can trust", room=430)
    f.p("Binary search is famously easy to get almost right. The cure is to write down the {B:invariant}, a fact "
        "that is true before every loop step, and check that each line keeps it true:", 13.5, gap=8)
    code(f, """
        def first_at_least(xs, target):
            lo, hi = 0, len(xs)          # invariant: the answer is in range(lo, hi + 1)
            while lo < hi:
                mid = (lo + hi) // 2
                if xs[mid] < target:
                    lo = mid + 1         # xs[mid] and everything left of it are too small
                else:
                    hi = mid             # xs[mid] might be the answer: keep it
            return lo                    # lo == hi: the range has one candidate left

        ids = [3, 8, 15, 21, 27, 34, 40, 52, 66, 71]
        print(first_at_least(ids, 40), first_at_least(ids, 41), first_at_least(ids, 99))
    """, notes={2: "hi = len(xs): 'past the end' is a valid answer", 4: "the range shrinks every step"})
    ns = f.ch._ns
    ids, target, rows = ns["ids"], 40, []
    lo, hi = 0, len(ids)
    while lo < hi:
        mid = (lo + hi) // 2
        go_right = ids[mid] < target
        rows.append([str(lo), str(hi), str(mid), str(ids[mid]),
                     f"{ids[mid]} < 40: lo = {mid + 1}" if go_right else f"{ids[mid]} ≥ 40: hi = {mid}"])
        lo, hi = (mid + 1, hi) if go_right else (lo, mid)
    rows.append([str(lo), str(hi), "", "", f"stop: answer {lo}"])
    trace(f, ["lo", "hi", "mid", "xs[mid]", "step"], rows, widths=[0.7, 0.7, 0.7, 1, 3.4], size=10)
    callout(f, "trap", "Mixing conventions breaks it: `hi = len(xs) - 1` with `while lo < hi` misses the last "
            "item; `hi = mid - 1` throws away a possible answer; `lo = mid` (without + 1) loops forever when "
            "`hi == lo + 1`. Pick one invariant and derive every line from it. Or just use `bisect_left`, "
            "which is exactly this function (Ch 10).")


def linked_section(f):
    sec(f, "Linked lists from scratch", room=430)
    f.p("A linked list stores each item in its own small object, a {B:node}, that holds the value and a "
        "reference to the next node. There's no block to grow and nothing to shift: adding at the front is "
        "always O(1). Finding the 500th item means following 500 references.", 13.5, gap=8)
    code(f, """
        class Node:
            __slots__ = ("value", "next")            # no per-node __dict__: smaller nodes
            def __init__(self, value, next=None):
                self.value, self.next = value, next

        def from_items(items):
            head = None
            for v in reversed(items):
                head = Node(v, head)                 # O(1) push at the front
            return head

        def items(node):
            while node is not None:
                yield node.value
                node = node.next

        def reverse(node):
            prev = None
            while node is not None:
                nxt = node.next                      # remember the rest
                node.next = prev                     # turn this arrow around
                prev, node = node, nxt
            return prev

        head = from_items(["Dune", "Emma", "Ubik"])
        print(list(items(head)))
        head = reverse(head)
        print(list(items(head)))
    """, size=8.8)
    linked_picture(f, [("before", ["Dune", "Emma", "Ubik"]), ("after reverse()", ["Ubik", "Emma", "Dune"])])
    table(f, ["operation", "Python list (array)", "linked list"], [
        ["get item i", "O(1): address arithmetic", "{R:O(n)}: follow i references"],
        ["add/remove at the front", "{R:O(n)}: shift everything", "O(1): one new node"],
        ["insert after a node you hold", "{R:O(n)}", "O(1): relink two references"],
        ["memory per item", "8 bytes (one pointer)",
         f"a whole node object ({sys.getsizeof(f.ch._ns['Node']('x'))} bytes, `sys.getsizeof`)"],
    ], widths=[2.2, 2.4, 2.9], size=10.5)
    callout(f, "honest", "In Python you'll rarely write one: `list` and `deque` (which is itself a doubly linked "
            "list of 64-item blocks) are faster in practice. Linked structures matter because {B:trees and "
            "graphs are made of the same nodes and references}, and because in C and Rust you build them by "
            "hand. An LRU cache (practice 20.7) is the classic case where they win.")


def bst_section(f):
    sec(f, "Binary search trees", room=440)
    f.p("Give each node {B:two} references and keep one rule: everything in the left subtree is smaller, "
        "everything in the right subtree is larger. Then searching is binary search on a structure you can "
        "insert into, and an in-order walk visits the keys sorted:", 13.5, gap=8)
    code(f, """
        from dataclasses import dataclass

        @dataclass(slots=True)
        class TreeNode:
            key: int
            left: "TreeNode | None" = None
            right: "TreeNode | None" = None

        def insert(node, key):
            if node is None:
                return TreeNode(key)
            if key < node.key:
                node.left = insert(node.left, key)
            elif key > node.key:
                node.right = insert(node.right, key)
            return node                              # duplicates are ignored

        def contains(node, key):
            while node is not None:                  # searching needs no recursion
                if key == node.key:
                    return True
                node = node.left if key < node.key else node.right
            return False

        def inorder(node):
            if node is not None:
                yield from inorder(node.left)
                yield node.key
                yield from inorder(node.right)

        root = None
        for k in [50, 30, 70, 20, 40, 60, 80, 35]:
            root = insert(root, k)
        print(list(inorder(root)), contains(root, 35), contains(root, 36))
    """, size=8.8)
    bst_picture(f, f.ch._ns["root"], mark=(50, 30, 40, 35))
    f.p("Searching for 35 visits only the orange path: 50, 30, 40, 35. Each step discards a whole subtree, so a "
        "{B:balanced} tree of n keys needs about log₂ n steps. The four classic walks visit the same nodes in "
        "different orders:", 13.5, gap=8)
    code(f, """
        from collections import deque

        def preorder(n):
            if n:
                yield n.key; yield from preorder(n.left); yield from preorder(n.right)

        def postorder(n):
            if n:
                yield from postorder(n.left); yield from postorder(n.right); yield n.key

        def level_order(root):
            queue = deque([root])
            while queue:
                n = queue.popleft()
                if n:
                    yield n.key
                    queue.extend((n.left, n.right))

        print(list(preorder(root)), list(postorder(root)), list(level_order(root)), sep="\\n")
    """, size=8.8)
    table(f, ["walk", "order", "typical use"], [
        ["in-order", "left, node, right", "keys in sorted order"],
        ["pre-order", "node, then children", "copy or print a tree (parents before children)"],
        ["post-order", "children, then node", "delete or free a tree; sizes and heights from the bottom up"],
        ["level order", "row by row (a queue)", "shortest path in steps: BFS, Ch 21"],
    ], widths=[1.4, 2.0, 4.0], size=10.5)
    sub(f, "The catch: insertion order decides the shape", ACCENT, room=240)
    code(f, """
        import random

        def height(node):
            return 0 if node is None else 1 + max(height(node.left), height(node.right))

        keys = list(range(500))
        shuffled = random.Random(20).sample(keys, len(keys))
        for name, order in [("random order", shuffled), ("sorted order", keys)]:
            root = None
            for k in order:
                root = insert(root, k)
            print(f"{name}: height {height(root)} for {len(keys)} keys")
    """, notes={8: "same keys, two insertion orders"})
    callout(f, "honest", "Sorted input turns the tree into a linked list: O(n) per search. Real libraries use "
            "{B:self-balancing} trees (red-black, AVL) or {B:B-trees}, which is what SQLite indexes are (Ch 12). "
            "Python's standard library has none: use a `dict`/`set` for lookups, `bisect` on a sorted list for "
            "ranges, `heapq` for priorities, or the `sortedcontainers` package (Ch 19).")


def finish(f):
    sec(f, "Practise, then stamp", room=300)
    practice(f, 20)
    stamp(f, [
        (1, "Linked structures are objects holding references to other objects; `__slots__` shrinks each node. "
            "A list is a growable array of pointers with spare room (amortised O(1) append)."),
        (4, "Recursion uses one stack frame per call; the default limit is 1000 and there is no tail-call "
            "optimisation, so deep data needs an explicit stack. `functools.cache` memoises."),
        (5, "Know the costs: list O(1) at the end, O(n) at the front; dict/set O(1) on average; deque O(1) at both "
            "ends; heap O(log n); no balanced tree in the stdlib."),
    ])
    callout(f, "other", "C: a node is a `struct` with a pointer field, and you `malloc`/`free` every node "
            "yourself. Java: references like Python, and `TreeMap` is a red-black tree in the standard library. "
            "C++: `std::map` is a balanced tree, `std::list` a linked list. Rust: `Option<Box<Node>>`, and "
            "ownership makes doubly linked lists famously hard; use `BTreeMap`. Scheme guarantees tail calls; "
            "Python and Java never eliminate them, and C compilers only sometimes do.")
    callout(f, "deep", "Vault notes: {b:13.1} A cost claim begins with a model · {b:13.2} Asymptotic notation · "
            "{b:13.3} Common growth classes · {b:13.4} Amortised analysis · {b:13.5} Correctness through "
            "invariants and induction · {b:13.7} Binary search · {b:13.8} Comparison sorting · {b:13.9} Python "
            "sorting and Timsort · {b:13.10} Linked lists built from scratch · {b:13.12} Binary search trees.")


def build(ch):
    title_page(ch)
    f = flow(ch)
    bigo_section(f)
    amortised_section(f)
    recursion_section(f)
    memo_section(f)
    merge_section(f)
    invariant_section(f)
    linked_section(f)
    bst_section(f)
    finish(f)
