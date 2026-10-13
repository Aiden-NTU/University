"""Chapter 21 - Graphs and dynamic programming: adjacency lists, BFS, DFS and topological order (graphlib),
Dijkstra with heapq, then dynamic programming from memoised recursion to tables, edit distance, and when
greedy is enough."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, callout, code, flow, practice, section, stamp, sub, table, title_block,
                         trace, two_ways)

ORDER = 21
NUM = 21
TITLE = "Graphs and dynamic programming"
SHORT = "Algorithms II"
SLUG = "Algorithms-II"
ACCENT = C.ORANGE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


# ----------------------------------------------------------------------------- pictures
POS = {"Central": (0.04, 0.45), "North": (0.33, 0.04), "East": (0.42, 0.52), "West": (0.28, 0.96),
       "Uni": (0.78, 0.12), "Docks": (0.80, 0.88)}
LAYER = [C.ORANGE, C.BLUE, C.GREEN, C.PURPLE]


def graph_picture(f, edges, h=150, w=300, node_col=None, hl=(), tags=None, notes=()):
    """The courier network: nodes at fixed spots, edge weights in the middle, highlighted edges thick."""
    y = f.reserve(h + 30)
    pg = f.pg
    x0 = L + (48 if tags else 30)

    def xy(n):
        px, py = POS[n]
        return x0 + px * w, y + 12 + py * h

    for a, b, minutes in edges:
        (x1, y1), (x2, y2) = xy(a), xy(b)
        on = (a, b) in hl or (b, a) in hl
        pg.line(x1, y1, x2, y2, ACCENT if on else C.GREY, 2.6 if on else 1.0, layer=C.UNDER)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        pg.rect(mx - 9, my - 8, 18, 15, "#ffffff", 0, fillcolor="#ffffff", r=3)
        pg.text(mx, my - 6, str(minutes), 8.5, ACCENT if on else C.GREY, F.MONO, align="center")
    for n in POS:
        x, yy = xy(n)
        col = (node_col or {}).get(n, C.BLUE)
        label = f"{n} · {tags[n]}" if tags and n in tags else n
        size = 8.8 if tags else 9.5
        wd = F.width(label, F.BOLD, size) + 16
        pg.rect(x - wd / 2, yy - 11, wd, 22, col, 1.3, fillcolor=C.LIGHT[col], r=11)
        pg.text(x, yy - 6, label, size, col, F.BOLD, align="center")
    for k, (text, col) in enumerate(notes):
        pg.note(L + 375, y + 10 + k * 36, text, col, 13, w=R - L - 375)


def terms_picture(f, terms, needs):
    """Modules in columns by term, arrows from each prerequisite to the module that needs it."""
    bw, bh, colw, rowh = 100, 20, 130, 30
    rows = max(len(t) for t in terms)
    y = f.reserve(rows * rowh + 26)
    pg = f.pg
    where = {}
    for t, mods in enumerate(terms):
        for r, m in enumerate(mods):
            where[m] = (L + t * colw, y + 18 + r * rowh + bh / 2)
    for m, pre in needs.items():
        for p in pre:
            (x1, y1), (x2, y2) = where[p], where[m]
            pg.line(x1 + bw, y1, x2, y2, C.GREY, 0.9, layer=C.UNDER)
            k = 7 / ((x2 - x1 - bw) ** 2 + (y2 - y1) ** 2) ** 0.5
            pg.arrow(x2 - (x2 - x1 - bw) * k, y2 - (y2 - y1) * k, x2 - 1, y2, C.GREY, 0.9, head=4)
    for t, mods in enumerate(terms):
        x = L + t * colw
        pg.text(x + bw / 2, y, f"term {t + 1}", 9.5, C.GREY, F.BOLD, align="center")
        for r, m in enumerate(mods):
            yy = y + 18 + r * rowh
            pg.rect(x, yy, bw, bh, LAYER[t], 1.2, fillcolor=C.LIGHT[LAYER[t]], r=5)
            pg.text(x + bw / 2, yy + 4, m, 8.6, C.INK, F.SANS, align="center")


def grid_picture(f, a, b, d):
    """The edit-distance table with the path of choices traced back from the bottom-right corner."""
    cw, chh = 30, 19
    y = f.reserve((len(a) + 2) * chh + 12)
    pg = f.pg
    x0 = L + 14
    path, i, j = set(), len(a), len(b)
    while i or j:
        path.add((i, j))
        if i and j and d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            i, j = i - 1, j - 1
        elif i and d[i][j] == d[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
    path.add((0, 0))
    for j, ch in enumerate(" " + b):
        pg.text(x0 + (j + 1.5) * cw, y, ch, 10, C.BLUE, F.MONO, align="center")
    for i, ch in enumerate(" " + a):
        pg.text(x0 + cw / 2, y + (i + 1) * chh + 2, ch, 10, C.RED, F.MONO, align="center")
        for j in range(len(b) + 1):
            on = (i, j) in path
            col = ACCENT if on else C.GREY
            pg.rect(x0 + (j + 1) * cw, y + (i + 1) * chh, cw, chh, col, 0.8 if not on else 1.2,
                    fillcolor=C.LIGHT[ACCENT] if on else "#ffffff")
            pg.text(x0 + (j + 1.5) * cw, y + (i + 1) * chh + 3, str(d[i][j]), 9.5, C.INK if on else C.GREY,
                    F.MONO, align="center")
    nx = x0 + (len(b) + 2) * cw + 24
    pg.note(nx, y + 6, "cell [i][j] = fewest edits to turn\nthe first i letters of a into the\nfirst j "
            "letters of b", ACCENT, 13, w=R - nx)
    pg.note(nx, y + 72, "↘ keep (free) or replace (+1)\n↓ delete from a (+1)\n→ insert from b (+1)", C.GREY, 13,
            w=R - nx)
    pg.note(nx, y + 128, f"answer: bottom-right = {d[-1][-1]}", C.RED, 14, w=R - nx)


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 21, TITLE, "most hard problems are a graph or a table in disguise", ACCENT)
    f = ch._flow = ch.flow(top=190)
    f.p("A {B:graph} is things (nodes) and connections (edges): branches and courier routes, web pages and "
        "links, modules and prerequisites, people and friendships. Once a problem is drawn as a graph, a "
        "handful of algorithms answer most questions about it. Our example: six library branches and the "
        "minutes a courier needs between them.", 14, gap=10)
    graph_picture(f, ROUTES_LIST, notes=[("undirected: routes\nwork both ways", C.GREY),
                                         ("weighted: minutes\non every edge", ACCENT), ("6 nodes, 9 edges", C.BLUE)])
    code(f, """
        from collections import defaultdict

        ROUTES = '''Central North 7   Central East 9   Central West 14
                    North East 10     North Uni 15     East West 2
                    East Uni 11       West Docks 9     Uni Docks 6'''
        words = ROUTES.split()
        routes = [(a, b, int(m)) for a, b, m in zip(words[::3], words[1::3], words[2::3])]

        graph = defaultdict(list)                 # adjacency list: node -> [(neighbour, minutes)]
        for a, b, minutes in routes:
            graph[a].append((b, minutes))
            graph[b].append((a, minutes))         # undirected: store both directions
        print(graph["East"])
    """, size=8.8)
    table(f, ["store it as", "space", "neighbours of u", "is u–v an edge?", "best for"], [
        ["adjacency list (dict of lists)", "V + E", "O(degree)", "O(degree)", "almost everything"],
        ["adjacency matrix (V×V grid)", "V²", "O(V)", "O(1)", "dense graphs, NumPy maths"],
        ["edge list", "E", "O(E)", "O(E)", "input files, sorting edges"],
    ], widths=[2.4, 0.8, 1.3, 1.3, 1.9], size=10)


ROUTES_LIST = [("Central", "North", 7), ("Central", "East", 9), ("Central", "West", 14), ("North", "East", 10),
               ("North", "Uni", 15), ("East", "West", 2), ("East", "Uni", 11), ("West", "Docks", 9),
               ("Uni", "Docks", 6)]


def bfs_section(f):
    sec(f, "Breadth-first search: fewest steps", room=420)
    f.p("BFS explores in rings: first every neighbour of the start, then their neighbours, and so on. A "
        "{B:queue} (first in, first out) keeps the rings in order, so the first time BFS reaches a node is by "
        "the {B:fewest edges}:", 13.5, gap=8)
    code(f, """
        from collections import deque

        def bfs(graph, start):
            dist, prev = {start: 0}, {}
            queue = deque([start])
            while queue:
                u = queue.popleft()
                for v, _ in graph[u]:
                    if v not in dist:              # first visit = fewest steps
                        dist[v], prev[v] = dist[u] + 1, u
                        queue.append(v)
            return dist, prev

        def path(prev, end):
            out = [end]
            while out[-1] in prev:                 # walk the 'came from' links back
                out.append(prev[out[-1]])
            return out[::-1]

        dist, prev = bfs(graph, "Central")
        print(dist)
        print(path(prev, "Docks"))
    """, size=8.8)
    ns = f.ch._ns
    assert ns["routes"] == ROUTES_LIST
    dist, prev = ns["dist"], ns["prev"]
    graph_picture(f, ns["routes"], node_col={n: LAYER[d] for n, d in dist.items()},
                  hl={(v, u) for v, u in prev.items()}, tags={n: f"{d} step{'s' * (d != 1)}" if d else "start" for n, d in dist.items()},
                  notes=[("thick: how BFS first\nreached each node", ACCENT), ("colour: steps from\nCentral", C.BLUE)])
    callout(f, "idea", "BFS ignores the weights: Central → West → Docks is 2 steps but 23 minutes, while the "
            "quickest route has 3 steps. Each node and edge is handled once: O(V + E). BFS is the right tool "
            "whenever every step costs the same: mazes, word ladders, degrees of separation, the level-order walk "
            "of Ch 20.")


def dfs_section(f):
    sec(f, "Depth-first search and a safe order of work", room=420)
    f.p("Swap the queue for a {B:stack} and the search goes as deep as it can before backing up. That's DFS: the "
        "tool for reachability, cycles and ordering. Module prerequisites are a {B:directed} graph (an edge "
        "means 'needs'), and a valid study plan is a {B:topological order}: every module after the ones it "
        "needs. The stdlib's `graphlib` does it, and can even hand out modules term by term:", 13.5, gap=8)
    code(f, """
        from graphlib import TopologicalSorter, CycleError

        needs = {                                       # module: the modules it needs first
            "Algorithms": ["Programming", "Discrete Maths"],
            "Databases": ["Programming"],
            "Operating Systems": ["Architecture", "Programming"],
            "Networks": ["Operating Systems"],
            "Security": ["Networks", "Databases", "Discrete Maths"],
            "Compilers": ["Algorithms", "Architecture"],
        }
        ts = TopologicalSorter(needs)
        ts.prepare()
        terms = []
        while ts.is_active():
            ready = sorted(ts.get_ready())              # everything whose needs are all done
            terms.append(ready)
            ts.done(*ready)
        for k, ready in enumerate(terms, 1):
            print(f"term {k}: {', '.join(ready)}")
    """, size=8.8, notes={12: "raises CycleError if there's a loop"})
    terms_picture(f, f.ch._ns["terms"], f.ch._ns["needs"])
    code(f, """
        def depends_on(graph, start):
            seen, stack = set(), [start]
            while stack:
                u = stack.pop()                         # a stack: go deep first
                for v in graph.get(u, []):
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            return seen

        print(sorted(depends_on(needs, "Networks")))
        needs["Programming"] = ["Security"]             # a circular requirement
        try:
            list(TopologicalSorter(needs).static_order())
        except CycleError as e:
            print("cycle:", " -> ".join(e.args[1]))
    """, size=8.8)
    callout(f, "why", "Topological order exists only when there is no cycle (a DAG: directed acyclic graph). "
            "The same idea orders build steps (make), package installs (pip's resolver, Ch 19), spreadsheet "
            "cells and database migrations. A DFS-based version is practice 21.2.")


def dijkstra_section(f):
    sec(f, "Dijkstra: cheapest paths with a heap", room=300)
    f.p("With weights, the fewest steps isn't the quickest route. Dijkstra's algorithm grows a set of "
        "{B:settled} nodes whose best time is final, always settling the unsettled node with the smallest "
        "known time next. A heap (Ch 10) finds that node in O(log n):", 13.5, gap=8)
    code(f, """
        import heapq

        def dijkstra(graph, start):
            dist, prev = {start: 0}, {}
            heap = [(0, start)]
            while heap:
                d, u = heapq.heappop(heap)
                if d > dist[u]:
                    continue                    # stale: u was already settled more cheaply
                for v, minutes in graph[u]:
                    new = d + minutes
                    if new < dist.get(v, float("inf")):
                        dist[v], prev[v] = new, u
                        heapq.heappush(heap, (new, v))
            return dist, prev

        best, came_from = dijkstra(graph, "Central")
        print(path(came_from, "Docks"), best["Docks"], "minutes")
    """, size=8.8, notes={12: "found a quicker way to v"})
    ns = f.ch._ns
    import heapq
    graph, dist, rows = ns["graph"], {"Central": 0}, []
    heap = [(0, "Central")]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            rows.append([f"({d}, {u})", "stale: skip it", f"({u} was settled at {dist[u]})"])
            continue
        pushed = []
        for v, w in graph[u]:
            if d + w < dist.get(v, float("inf")):
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
                pushed.append(f"{v} {d + w}")
        rows.append([f"({d}, {u})", f"settle {u} at {d}", ", ".join(pushed) or "nothing better"])
    trace(f, ["popped", "action", "improved (pushed)"], rows, widths=[1.5, 1.8, 3.6], size=10)
    best, came = ns["best"], ns["came_from"]
    graph_picture(f, ns["routes"], node_col={n: C.GREEN for n in best}, hl={(v, u) for v, u in came.items()},
                  tags={n: f"{d} min" for n, d in best.items()},
                  notes=[("thick: each node's\nbest 'came from'", ACCENT), ("West: 14 direct,\nbut 11 via East", C.GREEN)])
    callout(f, "trap", "Dijkstra is only correct with {B:non-negative} weights: it assumes a settled node can't "
            "get cheaper later. With negative edges use Bellman-Ford (O(V·E)). The `if d > dist[u]: continue` "
            "line is the price of not having a decrease-key operation on `heapq`: old entries are skipped when "
            "they surface. Cost: O((V + E) log V).")


def dp_section(f):
    sec(f, "Dynamic programming: from recursion to a table", room=430)
    f.p("Dynamic programming is Ch 20's memoisation, applied on purpose: describe the answer in terms of answers "
        "to {B:smaller versions} of the same question, and make sure each smaller answer is computed once. How "
        "many ways can you pay 100p with 1p, 2p and 5p coins?", 13.5, gap=8)
    two_ways(f, ("top-down: recursion + cache", """
        from functools import cache

        COINS = (1, 2, 5)

        @cache
        def count(amount, i=0):
            if amount == 0:
                return 1
            if amount < 0 or i == len(COINS):
                return 0
            use = count(amount - COINS[i], i)
            skip = count(amount, i + 1)
            return use + skip

        print(count(100))
    """), ("bottom-up: fill a table", """
        COINS = (1, 2, 5)

        ways = [1] + [0] * 100     # index = amount
        for c in COINS:
            for a in range(c, 101):
                ways[a] += ways[a - c]

        print(ways[100])
    """), verdict=[("easy to derive", 5, 3), ("no recursion limit", 2, 5), ("memory you control", 2, 5)])
    table(f, ["step", "question to answer", "coins example"], [
        ["1. state", "what does a subproblem need to know?", "amount left, which coins are still allowed"],
        ["2. recurrence", "how do smaller answers combine?", "use coin i again + skip coin i"],
        ["3. base cases", "which answers are known outright?", "amount 0: 1 way; no coins left: 0 ways"],
        ["4. order", "what must be computed before what?", "smaller amounts first (the table's loop order)"],
        ["5. answer", "which cell holds the result?", "`count(100)` / `ways[100]`"],
    ], widths=[1.3, 2.7, 3.4], size=10)


def edit_section(f):
    sec(f, "A DP table you can see: edit distance", room=430)
    f.p("How many single-letter edits turn one word into another? It's the typosquat alarm of Ch 19 and every "
        "spell checker. Each cell answers a smaller question, and the table fills row by row:", 13.5, gap=8)
    code(f, """
        def edit_table(a, b):
            d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
            for i in range(len(a) + 1):
                d[i][0] = i                             # delete all i letters
            for j in range(len(b) + 1):
                d[0][j] = j                             # insert all j letters
            for i in range(1, len(a) + 1):
                for j in range(1, len(b) + 1):
                    d[i][j] = min(d[i - 1][j] + 1,                           # delete a[i-1]
                                  d[i][j - 1] + 1,                           # insert b[j-1]
                                  d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))  # keep/replace
            return d

        d = edit_table("kitten", "sitting")
        print(d[-1][-1])
    """, size=8.8)
    ns = f.ch._ns
    grid_picture(f, "kitten", "sitting", ns["d"])
    f.p("Following the orange cells back from the corner recovers the edits themselves: replace k→s, keep "
        "i, t, t, replace e→i, keep n, insert g. The table costs O(len(a) × len(b)) time and memory; keeping "
        "only the previous row cuts the memory to O(len(b)).", 13.5, gap=8)
    sub(f, "When greedy is enough, and when it isn't", ACCENT, room=260)
    code(f, """
        COINS = [4, 3, 1]

        def greedy(amount):                       # always take the biggest coin that fits
            used = []
            for c in COINS:
                while amount >= c:
                    amount -= c
                    used.append(c)
            return used

        def fewest(amount):                       # DP: best[a] = fewest coins that make a
            best = [[]] + [None] * amount
            for a in range(1, amount + 1):
                best[a] = min((best[a - c] + [c] for c in COINS if c <= a), key=len)
            return best[amount]

        print(greedy(6), fewest(6))
    """, size=8.8)
    callout(f, "idea", "A {B:greedy} algorithm commits to the best-looking choice and never reconsiders. It's "
            "right only when you can prove the local choice is safe: Dijkstra is greedy (safe because weights are "
            "non-negative), and so is paying with UK coins. When choices interact, as with coins 4, 3, 1, DP "
            "tries every option for every subproblem, once each.")


def finish(f):
    sec(f, "Practise, then stamp", room=300)
    practice(f, 21)
    stamp(f, [
        (5, "Graphs as `dict` of neighbour lists (or `defaultdict(list)`); `deque` for BFS, a list as a stack "
            "for DFS, `heapq` for Dijkstra. DP tables are lists of lists, or `@cache` on a recursive function."),
        (11, "`graphlib.TopologicalSorter` (ordering, cycle detection), `heapq`, `collections.deque`, "
             "`functools.cache`. For serious graph work: `networkx` from pip (Ch 19)."),
    ])
    callout(f, "other", "Every language has the parts: C++ `std::priority_queue` and `std::queue`, Java "
            "`PriorityQueue` and `ArrayDeque`, Rust `BinaryHeap` (a max-heap: wrap keys in `Reverse`) and "
            "`VecDeque`. C has none built in, so a graph is arrays of indices. The algorithms are identical; "
            "only the containers' names change.")
    callout(f, "deep", "Vault notes: {b:13.13} Graphs · {b:13.14} Topological ordering · {b:13.15} Weighted "
            "shortest paths and Dijkstra's boundary · {b:13.17} Greedy algorithms · {b:13.18} Dynamic "
            "programming · {b:13.19} Algorithm selection as evidence.")


def build(ch):
    title_page(ch)
    f = flow(ch)
    bfs_section(f)
    dfs_section(f)
    dijkstra_section(f)
    dp_section(f)
    edit_section(f)
    finish(f)
