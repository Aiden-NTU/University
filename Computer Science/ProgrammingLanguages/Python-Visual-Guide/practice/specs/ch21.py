EXERCISES = [
    dict(
        id="21.1", kind="build", title="Fewest steps through a maze",
        task="""
        A maze is a list of equal-length strings: `S` start, `E` exit, `#` wall, `.` open floor. You may step
        up, down, left or right. `shortest_steps(maze)` returns `(steps, path)`: the fewest steps from S to E
        and one shortest path as a list of `(row, col)` from S to E inclusive, or `(-1, [])` when E can't be
        reached. The stub walks depth-first: it finds *a* path, not the shortest, and a big maze blows the
        recursion limit. Rewrite it as a breadth-first search.
        """,
        stub='''
        def shortest_steps(maze):
            rows, cols = len(maze), len(maze[0])
            start = next((r, c) for r in range(rows) for c in range(cols) if maze[r][c] == "S")
            seen = set()

            def walk(r, c):
                if not (0 <= r < rows and 0 <= c < cols) or maze[r][c] == "#" or (r, c) in seen:
                    return None
                seen.add((r, c))
                if maze[r][c] == "E":
                    return [(r, c)]
                for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    rest = walk(r + dr, c + dc)
                    if rest:
                        return [(r, c)] + rest
                return None

            path = walk(*start)
            return (len(path) - 1, path) if path else (-1, [])
        ''',
        tests='''
        import random
        import time
        from collections import deque

        def ref(maze):
            rows, cols = len(maze), len(maze[0])
            start = next((r, c) for r in range(rows) for c in range(cols) if maze[r][c] == "S")
            dist, q = {start: 0}, deque([start])
            while q:
                r, c = q.popleft()
                if maze[r][c] == "E":
                    return dist[(r, c)]
                for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "#" and (nr, nc) not in dist:
                        dist[(nr, nc)] = dist[(r, c)] + 1
                        q.append((nr, nc))
            return -1

        def valid(maze, steps, path):
            if steps == -1:
                return path == []
            if len(path) != steps + 1 or maze[path[0][0]][path[0][1]] != "S" or maze[path[-1][0]][path[-1][1]] != "E":
                return False
            for (r1, c1), (r2, c2) in zip(path, path[1:]):
                if abs(r1 - r2) + abs(c1 - c2) != 1 or maze[r2][c2] == "#":
                    return False
            return True

        def test_small(m):
            equal(m.shortest_steps(["S.E"]), (2, [(0, 0), (0, 1), (0, 2)]))
            equal(m.shortest_steps(["S#E"]), (-1, []), "a wall in the way")
            equal(m.shortest_steps(["SE"]), (1, [(0, 0), (0, 1)]), "next door")
            maze = ["S..", "...", "E.."]
            steps, path = m.shortest_steps(maze)
            equal(steps, 2, "fewest steps in an open room (depth-first wanders)")
            check(valid(maze, steps, path), f"not a valid shortest path: {path}")

        def test_random(m):
            rng = random.Random(21)
            for _ in range(150):
                rows, cols = rng.randint(1, 8), rng.randint(2, 8)
                cells = [["#" if rng.random() < 0.3 else "." for _ in range(cols)] for _ in range(rows)]
                spots = rng.sample([(r, c) for r in range(rows) for c in range(cols)], 2)
                (sr, sc), (er, ec) = spots
                cells[sr][sc], cells[er][ec] = "S", "E"
                maze = ["".join(row) for row in cells]
                steps, path = m.shortest_steps(maze)
                equal(steps, ref(maze), f"steps for {maze}")
                check(valid(maze, steps, path), f"bad path {path} for {maze}")

        def test_big(m):
            rng = random.Random(1)
            cells = [["#" if rng.random() < 0.25 else "." for _ in range(200)] for _ in range(200)]
            cells[0][0], cells[199][199] = "S", "E"
            cells[0][1] = cells[1][0] = cells[199][198] = cells[198][199] = "."
            maze = ["".join(row) for row in cells]
            t0 = time.perf_counter()
            steps, path = m.shortest_steps(maze)
            took = time.perf_counter() - t0
            equal(steps, ref(maze), "steps in a 200 x 200 maze")
            check(valid(maze, steps, path), "the path in the big maze is not valid")
            check(took < 1.0, f"took {took:.2f} s; budget 1 s")
        ''',
        alts={
            "a queue and a came-from dict": ('''
                from collections import deque

                def shortest_steps(maze):
                    rows, cols = len(maze), len(maze[0])
                    start = next((r, c) for r in range(rows) for c in range(cols) if maze[r][c] == "S")
                    prev, q = {start: None}, deque([start])
                    while q:
                        r, c = cell = q.popleft()
                        if maze[r][c] == "E":
                            path = []
                            while cell is not None:
                                path.append(cell)
                                cell = prev[cell]
                            return len(path) - 1, path[::-1]
                        for nxt in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                            nr, nc = nxt
                            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "#" and nxt not in prev:
                                prev[nxt] = cell
                                q.append(nxt)
                    return -1, []
            ''', "The queue hands out cells in order of distance, so the first time E comes off the queue it was "
                 "reached in the fewest steps. `prev` does double duty: it is the 'seen' set and the trail back "
                 "to S. Mark a cell when you queue it, not when you pop it, or the same cell is queued many times."),
            "frontier by frontier, no queue": ('''
                def shortest_steps(maze):
                    rows, cols = len(maze), len(maze[0])
                    start = next((r, c) for r in range(rows) for c in range(cols) if maze[r][c] == "S")
                    prev, frontier, steps = {start: None}, [start], 0
                    while frontier:
                        for cell in frontier:
                            if maze[cell[0]][cell[1]] == "E":
                                path = [cell]
                                while prev[path[-1]] is not None:
                                    path.append(prev[path[-1]])
                                return steps, path[::-1]
                        nxt = []
                        for r, c in frontier:
                            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                                if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] != "#" and (nr, nc) not in prev:
                                    prev[(nr, nc)] = (r, c)
                                    nxt.append((nr, nc))
                        frontier, steps = nxt, steps + 1
                    return -1, []
            ''', "BFS as rings: everything in `frontier` is exactly `steps` away, and the next ring is every "
                 "unseen neighbour of this one. It is the picture from the chapter turned into code, and the "
                 "step count needs no per-cell bookkeeping."),
        },
    ),
    dict(
        id="21.2", kind="build", title="Your own topological sort",
        task="""
        `topo_order(needs)` takes a dict mapping each module to a list of its prerequisites (the same shape as
        `graphlib.TopologicalSorter`) and returns every module, including ones that only appear as
        prerequisites, in an order where each prerequisite comes before the modules that need it. When
        several modules are ready at once, take the alphabetically smallest first, so the answer is unique.
        Raise `ValueError` if there is a cycle. No `graphlib`. A 20,000-module chain must take under 0.5 s.
        """,
        stub='''
        def topo_order(needs):
            names = set(needs) | {p for ps in needs.values() for p in ps}
            return sorted(names, key=lambda n: len(needs.get(n, [])))
        ''',
        tests='''
        import heapq
        import random
        import time

        def ref(needs):
            names = set(needs) | {p for ps in needs.values() for p in ps}
            waiting = {n: len(set(needs.get(n, []))) for n in names}
            users = {n: [] for n in names}
            for n, ps in needs.items():
                for p in set(ps):
                    users[p].append(n)
            ready = [n for n in names if waiting[n] == 0]
            heapq.heapify(ready)
            out = []
            while ready:
                n = heapq.heappop(ready)
                out.append(n)
                for u in users[n]:
                    waiting[u] -= 1
                    if waiting[u] == 0:
                        heapq.heappush(ready, u)
            return out if len(out) == len(names) else None

        NEEDS = {"Networks": ["Programming", "Discrete Maths"], "Databases": ["Programming"],
                 "Security": ["Networks", "Databases"], "Operating Systems": ["Architecture", "Programming"]}

        def test_example(m):
            equal(m.topo_order(NEEDS), ["Architecture", "Discrete Maths", "Programming", "Databases", "Networks",
                                        "Operating Systems", "Security"])
            equal(m.topo_order({}), [], "no modules")
            equal(m.topo_order({"b": [], "a": []}), ["a", "b"], "no prerequisites: alphabetical")

        def test_cycles(m):
            raises(ValueError, m.topo_order, {"a": ["b"], "b": ["c"], "c": ["a"]})
            raises(ValueError, m.topo_order, {"a": ["a"]})
            raises(ValueError, m.topo_order, {**NEEDS, "Programming": ["Security"]})

        def test_random(m):
            rng = random.Random(2)
            for _ in range(100):
                names = [f"m{i}" for i in range(rng.randint(1, 12))]
                rng.shuffle(names)
                needs = {}
                for i, n in enumerate(names):
                    if rng.random() < 0.8:
                        needs[n] = rng.sample(names[:i], rng.randint(0, min(i, 3)))
                if rng.random() < 0.2 and len(names) > 1:
                    needs.setdefault(names[0], []).append(names[-1])
                want = ref(needs)
                if want is None:
                    raises(ValueError, m.topo_order, needs)
                else:
                    equal(m.topo_order(needs), want, f"topo_order({needs})")

        def test_fast_and_own(m):
            check("graphlib" not in imports(m), "write it yourself: no graphlib")
            chain = {f"m{i:05d}": [f"m{i - 1:05d}"] for i in range(1, 20_000)}
            t0 = time.perf_counter()
            got = m.topo_order(chain)
            took = time.perf_counter() - t0
            equal(got[:2] + got[-1:], ["m00000", "m00001", "m19999"], "order of a long chain")
            check(took < 0.5, f"took {took:.2f} s; budget 0.5 s (are you rescanning everything each step?)")
        ''',
        alts={
            "Kahn's algorithm with a heap": ('''
                import heapq

                def topo_order(needs):
                    names = set(needs) | {p for ps in needs.values() for p in ps}
                    waiting = {n: 0 for n in names}            # prerequisites not yet placed
                    users = {n: [] for n in names}             # who is waiting on n
                    for n, ps in needs.items():
                        for p in set(ps):
                            waiting[n] += 1
                            users[p].append(n)
                    ready = [n for n in names if waiting[n] == 0]
                    heapq.heapify(ready)
                    order = []
                    while ready:
                        n = heapq.heappop(ready)               # smallest ready name
                        order.append(n)
                        for u in users[n]:
                            waiting[u] -= 1
                            if waiting[u] == 0:
                                heapq.heappush(ready, u)
                    if len(order) < len(names):
                        stuck = sorted(n for n in names if waiting[n])
                        raise ValueError(f"cycle among {stuck}")
                    return order
            ''', "Count each module's unmet prerequisites; whatever reaches zero is ready. A heap of ready names "
                 "gives the alphabetical tie-break in O(log n). Anything never reaching zero sits on (or behind) a "
                 "cycle, which is both the cycle check and a useful error message. O((V + E) log V)."),
            "Kahn with a sorted ready list": ('''
                import bisect

                def topo_order(needs):
                    names = set(needs) | {p for ps in needs.values() for p in ps}
                    users = {n: set() for n in names}
                    waiting = {n: set(needs.get(n, ())) for n in names}
                    for n, ps in waiting.items():
                        for p in ps:
                            users[p].add(n)
                    ready = sorted(n for n in names if not waiting[n])
                    order = []
                    while ready:
                        n = ready.pop(0)
                        order.append(n)
                        for u in users[n]:
                            waiting[u].discard(n)
                            if not waiting[u]:
                                bisect.insort(ready, u)
                    if len(order) < len(names):
                        raise ValueError("the prerequisites contain a cycle")
                    return order
            ''', "Same algorithm, keeping the ready list sorted with bisect.insort. pop(0) and insort are O(n) "
                 "each, but the ready list is usually short, so this is fast in practice. A DFS-based sort (emit "
                 "a module after all its prerequisites) is just as correct, but makes the alphabetical "
                 "tie-break much harder."),
        },
    ),
    dict(
        id="21.3", kind="fix", title="Dijkstra that settles too early",
        task="""
        `dijkstra(graph, start)` should return a dict of the cheapest cost from `start` to every reachable node.
        `graph` maps a node to a list of `(neighbour, cost)` pairs (directed, costs >= 0; a node may appear
        only as a neighbour). The stub has two bugs. Then write `cheapest_path(graph, start, end)` returning
        `(cost, [start, ..., end])`, or `(None, [])` if `end` can't be reached.
        """,
        stub='''
        import heapq

        def dijkstra(graph, start):
            dist = {start: 0}
            heap = [(start, 0)]
            done = {start}
            while heap:
                u, d = heapq.heappop(heap)
                for v, cost in graph.get(u, []):
                    if v not in done:
                        done.add(v)
                        dist[v] = d + cost
                        heapq.heappush(heap, (v, d + cost))
            return dist

        def cheapest_path(graph, start, end):
            return dijkstra(graph, start).get(end), [start, end]
        ''',
        tests='''
        import random
        import time

        ROUTES = [("Central", "North", 7), ("Central", "East", 9), ("Central", "West", 14), ("North", "East", 10),
                  ("North", "Uni", 15), ("East", "West", 2), ("East", "Uni", 11), ("West", "Docks", 9),
                  ("Uni", "Docks", 6)]
        GRAPH = {}
        for a, b, w in ROUTES:
            GRAPH.setdefault(a, []).append((b, w))
            GRAPH.setdefault(b, []).append((a, w))

        def bellman_ford(graph, start):
            dist = {start: 0}
            for _ in range(len(graph) + 1):
                for u, edges in graph.items():
                    if u in dist:
                        for v, w in edges:
                            if dist[u] + w < dist.get(v, float("inf")):
                                dist[v] = dist[u] + w
            return dist

        def path_cost(graph, path):
            return sum(min(w for v, w in graph[a] if v == b) for a, b in zip(path, path[1:]))

        def test_routes(m):
            equal(m.dijkstra(GRAPH, "Central"), {"Central": 0, "North": 7, "East": 9, "West": 11, "Uni": 20, "Docks": 20})
            equal(m.cheapest_path(GRAPH, "Central", "Docks"), (20, ["Central", "East", "West", "Docks"]))
            equal(m.cheapest_path(GRAPH, "Uni", "Uni"), (0, ["Uni"]), "start == end")
            equal(m.cheapest_path({"a": [("b", 1)]}, "b", "a"), (None, []), "edges are one-way")

        def test_random(m):
            rng = random.Random(3)
            for _ in range(120):
                n = rng.randint(1, 9)
                graph = {}
                for _ in range(rng.randint(0, 20)):
                    a, b = rng.randrange(n), rng.randrange(n)
                    graph.setdefault(a, []).append((b, rng.randint(0, 20)))
                want = bellman_ford(graph, 0)
                equal(m.dijkstra(graph, 0), want, f"dijkstra({graph}, 0)")
                end = rng.randrange(n)
                cost, path = m.cheapest_path(graph, 0, end)
                if end not in want:
                    equal((cost, path), (None, []), f"cheapest_path to unreachable {end}")
                else:
                    equal(cost, want[end], f"cost to {end} in {graph}")
                    check(path[0] == 0 and path[-1] == end and path_cost(graph, path) == cost,
                          f"path {path} doesn't cost {cost} in {graph}")

        def test_fast(m):
            rng = random.Random(4)
            n = 20_000
            graph = {u: [(rng.randrange(n), rng.randint(1, 100)) for _ in range(5)] for u in range(n)}
            t0 = time.perf_counter()
            dist = m.dijkstra(graph, 0)
            took = time.perf_counter() - t0
            check(len(dist) > n * 0.9, "most nodes should be reachable")
            check(took < 1.0, f"took {took:.2f} s; budget 1 s")
        ''',
        alts={
            "settle when popped, lazy deletion": ('''
                import heapq

                def _search(graph, start):
                    dist, prev, heap = {start: 0}, {}, [(0, start)]
                    while heap:
                        d, u = heapq.heappop(heap)          # (cost, node): the heap orders by cost
                        if d > dist[u]:
                            continue                        # a stale entry: u was settled more cheaply
                        for v, cost in graph.get(u, []):
                            if d + cost < dist.get(v, float("inf")):
                                dist[v], prev[v] = d + cost, u
                                heapq.heappush(heap, (d + cost, v))
                    return dist, prev

                def dijkstra(graph, start):
                    return _search(graph, start)[0]

                def cheapest_path(graph, start, end):
                    dist, prev = _search(graph, start)
                    if end not in dist:
                        return None, []
                    path = [end]
                    while path[-1] != start:
                        path.append(prev[path[-1]])
                    return dist[end], path[::-1]
            ''', "Bug 1: the heap held (node, cost), so it popped nodes in name order, not cost order. Bug 2: a "
                 "node was final as soon as it was first seen, but a later, cheaper route can still reach it "
                 "(Central to West: 14 direct, 11 via East). A node is only settled when it comes off the heap."),
            "an explicit settled set": ('''
                import heapq

                def dijkstra(graph, start):
                    return {node: cost for node, (cost, _) in _tree(graph, start).items()}

                def _tree(graph, start):
                    settled, heap = {}, [(0, start, None)]
                    while heap:
                        d, u, came_from = heapq.heappop(heap)
                        if u in settled:
                            continue
                        settled[u] = (d, came_from)
                        for v, cost in graph.get(u, []):
                            if v not in settled:
                                heapq.heappush(heap, (d + cost, v, u))
                    return settled

                def cheapest_path(graph, start, end):
                    tree = _tree(graph, start)
                    if end not in tree:
                        return None, []
                    path = [end]
                    while tree[path[-1]][1] is not None:
                        path.append(tree[path[-1]][1])
                    return tree[end][0], path[::-1]
            ''', "Push every offer, settle a node the first time it is popped, and ignore later pops. Each heap "
                 "entry carries where it came from, so the settled dict is the shortest-path tree. Mixed node "
                 "types would break the tuple comparison on ties; adding a counter as the second item fixes that."),
        },
    ),
    dict(
        id="21.4", kind="explore", title="Islands in a random network",
        task="""
        Write `components(nodes, edges)`: the connected components of an undirected graph as a list of sorted
        lists, ordered by their smallest node. It must cope with a 20,000-node chain, so no recursion.

        Then explore: `giant_fraction(n, c, seed=0)` builds a random graph of nodes `0..n-1` and
        `round(c * n / 2)` edges, each joining `rng.randrange(n)` to `rng.randrange(n)` with
        `rng = random.Random(seed)`, and returns the size of the largest component divided by `n`. Print it for
        `n = 2000` and `c` from 0.2 to 3.0. Somewhere a giant component suddenly appears: where, and why
        there? (Each node has `c` neighbours on average.)
        """,
        stub='''
        def components(nodes, edges):
            adj = {n: [] for n in nodes}
            for a, b in edges:
                adj[a].append(b)
                adj[b].append(a)
            seen, out = set(), []

            def visit(n, comp):
                seen.add(n)
                comp.append(n)
                for v in adj[n]:
                    if v not in seen:
                        visit(v, comp)

            for n in adj:
                if n not in seen:
                    comp = []
                    visit(n, comp)
                    out.append(sorted(comp))
            return sorted(out)
        ''',
        tests='''
        import random
        import time

        def ref(nodes, edges):
            parent = {n: n for n in nodes}
            def find(x):
                while parent[x] != x:
                    x = parent[x]
                return x
            for a, b in edges:
                parent[find(a)] = find(b)
            groups = {}
            for n in nodes:
                groups.setdefault(find(n), []).append(n)
            return sorted(sorted(g) for g in groups.values())

        def test_small(m):
            equal(m.components(range(7), [(0, 1), (1, 2), (3, 4), (6, 6)]), [[0, 1, 2], [3, 4], [5], [6]])
            equal(m.components([], []), [], "no nodes")
            equal(m.components(["d", "a", "c", "b"], [("d", "a"), ("c", "b")]), [["a", "d"], ["b", "c"]], "strings")

        def test_random(m):
            rng = random.Random(5)
            for _ in range(100):
                n = rng.randint(1, 15)
                edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 15))]
                equal(m.components(range(n), edges), ref(range(n), edges), f"components of {edges}")

        def test_chain(m):
            n = 20_000
            t0 = time.perf_counter()
            got = m.components(range(n), [(i, i + 1) for i in range(n - 1)])
            took = time.perf_counter() - t0
            equal((len(got), len(got[0])), (1, n), "a 20,000-node chain is one component")
            check(took < 0.5, f"took {took:.2f} s; budget 0.5 s")

        def test_giant(m):
            small, big = m.giant_fraction(2000, 0.5), m.giant_fraction(2000, 3.0)
            check(0 < small < 0.05, f"c = 0.5 gave {small}: below c = 1 every component should be tiny")
            check(big > 0.85, f"c = 3 gave {big}: well above c = 1 most nodes should be in one component")
            equal(m.giant_fraction(500, 1.5, seed=7), m.giant_fraction(500, 1.5, seed=7), "same seed, same answer")
        ''',
        alts={
            "iterative DFS with a stack": ('''
                import random

                def components(nodes, edges):
                    adj = {n: [] for n in nodes}
                    for a, b in edges:
                        adj[a].append(b)
                        adj[b].append(a)
                    seen, out = set(), []
                    for start in adj:
                        if start in seen:
                            continue
                        seen.add(start)
                        stack, comp = [start], []
                        while stack:
                            n = stack.pop()
                            comp.append(n)
                            for v in adj[n]:
                                if v not in seen:
                                    seen.add(v)
                                    stack.append(v)
                        out.append(sorted(comp))
                    return sorted(out)

                def giant_fraction(n, c, seed=0):
                    rng = random.Random(seed)
                    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(round(c * n / 2))]
                    return max(map(len, components(range(n), edges))) / n

                if __name__ == "__main__":
                    for c in [0.2, 0.5, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0, 3.0]:
                        print(f"c = {c:3}: {giant_fraction(2000, c):.3f}")
            ''', "Every node is visited once and every edge looked at twice: O(V + E). The table jumps around "
                 "c = 1: below it, each node reaches on average fewer than one new node per step, so every "
                 "exploration dies out; above it, explorations keep growing and merge into one giant. It is the "
                 "same threshold as an epidemic's R number."),
            "union-find (disjoint sets)": ('''
                import random

                def components(nodes, edges):
                    parent = {n: n for n in nodes}

                    def find(x):
                        while parent[x] != x:
                            parent[x] = parent[parent[x]]    # path halving keeps the trees flat
                            x = parent[x]
                        return x

                    for a, b in edges:
                        ra, rb = find(a), find(b)
                        if ra != rb:
                            parent[ra] = rb
                    groups = {}
                    for n in parent:
                        groups.setdefault(find(n), []).append(n)
                    return sorted(sorted(g) for g in groups.values())

                def giant_fraction(n, c, seed=0):
                    rng = random.Random(seed)
                    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(round(c * n / 2))]
                    return max(map(len, components(range(n), edges))) / n
            ''', "No adjacency lists at all: each node points towards a representative, and joining two groups "
                 "is one assignment. Union-find shines when edges arrive one at a time ('are these two connected "
                 "yet?'), which is also how Kruskal's minimum spanning tree works."),
        },
    ),
    dict(
        id="21.5", kind="build", title="Longest common subsequence",
        task="""
        A **subsequence** keeps some characters in their original order (gaps allowed): "ace" is one of
        "abcde". `lcs(a, b)` returns one longest string that is a subsequence of both, which is the heart of
        `diff`. Use a DP table: two 600-character strings must take under 2 s. The stub is greedy: it is fast,
        but it isn't always longest.
        """,
        stub='''
        def lcs(a, b):
            out, j = [], 0
            for ch in a:
                k = b.find(ch, j)
                if k != -1:
                    out.append(ch)
                    j = k + 1
            return "".join(out)
        ''',
        tests='''
        import random
        import time

        def length(a, b):
            prev = [0] * (len(b) + 1)
            for x in a:
                cur = [0]
                for j, y in enumerate(b):
                    cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
                prev = cur
            return prev[-1]

        def is_subseq(s, t):
            it = iter(t)
            return all(ch in it for ch in s)

        def ok(m, a, b):
            got = m.lcs(a, b)
            check(isinstance(got, str), f"lcs should return a str, got {type(got).__name__}")
            check(is_subseq(got, a) and is_subseq(got, b), f"{got!r} is not a subsequence of {a!r} and {b!r}")
            equal(len(got), length(a, b), f"length of lcs({a!r}, {b!r}) = {got!r}")

        def test_examples(m):
            for a, b in [("ABCBDAB", "BDCABA"), ("abcde", "ace"), ("", "abc"), ("abc", ""), ("abc", "abc"),
                         ("abc", "xyz"), ("kitten", "sitting"), ("XMJYAUZ", "MZJAWXU")]:
                ok(m, a, b)

        def test_random(m):
            rng = random.Random(6)
            for _ in range(200):
                a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
                b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
                ok(m, a, b)

        def test_big(m):
            rng = random.Random(7)
            a = "".join(rng.choice("ACGT") for _ in range(600))
            b = "".join(rng.choice("ACGT") for _ in range(600))
            t0 = time.perf_counter()
            got = m.lcs(a, b)
            took = time.perf_counter() - t0
            check(is_subseq(got, a) and is_subseq(got, b), "the big answer is not a common subsequence")
            equal(len(got), length(a, b), "length for two 600-character strings")
            check(took < 2.0, f"took {took:.2f} s; budget 2 s")
        ''',
        alts={
            "table of lengths, then walk back": ('''
                def lcs(a, b):
                    n, m = len(a), len(b)
                    t = [[0] * (m + 1) for _ in range(n + 1)]    # t[i][j] = LCS length of a[:i], b[:j]
                    for i in range(1, n + 1):
                        for j in range(1, m + 1):
                            if a[i - 1] == b[j - 1]:
                                t[i][j] = t[i - 1][j - 1] + 1
                            else:
                                t[i][j] = max(t[i - 1][j], t[i][j - 1])
                    out, i, j = [], n, m
                    while i and j:
                        if a[i - 1] == b[j - 1]:
                            out.append(a[i - 1])
                            i, j = i - 1, j - 1
                        elif t[i - 1][j] >= t[i][j - 1]:
                            i -= 1
                        else:
                            j -= 1
                    return "".join(reversed(out))
            ''', "Fill the table of answers to the smaller questions (prefixes), then walk back from the corner "
                 "choosing whichever neighbour the value came from, exactly like the edit-distance grid. "
                 "O(n·m) time and space. Note `[[0] * (m + 1) for _ in ...]`: `[[0] * (m + 1)] * (n + 1)` "
                 "would be n + 1 references to one row."),
            "suffix table, walk forward": ('''
                def lcs(a, b):
                    n, m = len(a), len(b)
                    t = [[0] * (m + 1) for _ in range(n + 1)]    # t[i][j] = LCS length of a[i:], b[j:]
                    for i in range(n - 1, -1, -1):
                        row, below = t[i], t[i + 1]
                        for j in range(m - 1, -1, -1):
                            row[j] = below[j + 1] + 1 if a[i] == b[j] else max(below[j], row[j + 1])
                    out, i, j = [], 0, 0
                    while i < n and j < m:
                        if a[i] == b[j]:
                            out.append(a[i])
                            i, j = i + 1, j + 1
                        elif t[i + 1][j] >= t[i][j + 1]:
                            i += 1
                        else:
                            j += 1
                    return "".join(out)
            ''', "Define the subproblem on suffixes instead of prefixes and the walk goes forwards, building the "
                 "answer in order. Caching `row` and `below` as locals avoids repeated indexing in the hot loop, "
                 "a cheap and common Python speed-up."),
        },
    ),
    dict(
        id="21.6", kind="refactor", title="Packing the book bag: knapsack by DP",
        task="""
        `max_value(items, capacity)` picks books to carry: `items` is a list of `(name, weight, value)` with
        whole-number weights, and the total weight must be at most `capacity`. It returns
        `(best_value, names)`, the names of one best choice in their original order. The stub tries every
        subset: O(2ⁿ). Rewrite it as a DP over (items so far, weight used) so 18 items take under 0.05 s.
        Don't change `items`.
        """,
        stub='''
        from itertools import combinations

        def max_value(items, capacity):
            best, choice = 0, []
            for k in range(len(items) + 1):
                for combo in combinations(items, k):
                    if sum(w for _, w, _ in combo) <= capacity:
                        value = sum(v for _, _, v in combo)
                        if value > best:
                            best, choice = value, [name for name, _, _ in combo]
            return best, choice
        ''',
        tests='''
        import random
        import time
        from itertools import combinations

        def brute(items, capacity):
            return max((sum(v for _, _, v in c) for k in range(len(items) + 1) for c in combinations(items, k)
                        if sum(w for _, w, _ in c) <= capacity), default=0)

        def ok(m, items, capacity, want, what):
            before = list(items)
            value, names = m.max_value(items, capacity)
            equal(items, before, "the items list was changed")
            equal(value, want, f"best value for {what}")
            chosen = [it for it in items if it[0] in names]
            check(len(chosen) == len(names) == len(set(names)), f"names {names} must be distinct item names")
            check([it[0] for it in chosen] == list(names), f"names {names} should keep the items' order")
            check(sum(w for _, w, _ in chosen) <= capacity, f"{names} weigh more than {capacity}")
            equal(sum(v for _, _, v in chosen), value, f"value of {names}")

        def test_example(m):
            items = [("atlas", 5, 10), ("bible", 4, 40), ("comic", 6, 30), ("dict", 3, 50)]
            equal(m.max_value(items, 10), (90, ["bible", "dict"]))
            equal(m.max_value(items, 0), (0, []), "no capacity")
            equal(m.max_value([], 10), (0, []), "no items")

        def test_random(m):
            rng = random.Random(8)
            for _ in range(80):
                items = [(f"b{i}", rng.randint(1, 10), rng.randint(0, 30)) for i in range(rng.randint(0, 8))]
                cap = rng.randint(0, 25)
                ok(m, items, cap, brute(items, cap), f"{items}, capacity {cap}")

        def test_fast(m):
            rng = random.Random(9)
            items = [(f"b{i}", rng.randint(1, 60), rng.randint(1, 100)) for i in range(18)]
            t0 = time.perf_counter()
            value, names = m.max_value(items, 300)
            took = time.perf_counter() - t0
            check(took < 0.05, f"took {took:.3f} s; budget 0.05 s (that's still trying every subset)")
            chosen = [it for it in items if it[0] in names]
            check(sum(w for _, w, _ in chosen) <= 300 and sum(v for _, _, v in chosen) == value, "a valid choice")
        ''',
        alts={
            "a table, then trace the choices back": ('''
                def max_value(items, capacity):
                    n = len(items)
                    best = [[0] * (capacity + 1) for _ in range(n + 1)]   # best[i][c]: first i items, weight <= c
                    for i, (_, w, v) in enumerate(items, 1):
                        for c in range(capacity + 1):
                            best[i][c] = best[i - 1][c]
                            if w <= c and best[i - 1][c - w] + v > best[i][c]:
                                best[i][c] = best[i - 1][c - w] + v
                    names, c = [], capacity
                    for i in range(n, 0, -1):
                        if best[i][c] != best[i - 1][c]:                 # item i was taken
                            name, w, _ = items[i - 1]
                            names.append(name)
                            c -= w
                    return best[n][capacity], names[::-1]
            ''', "Each cell asks one question: is item i worth its weight here? Skip it (the cell above) or take it "
                 "(the cell above, w to the left, plus v). O(n·capacity): pseudo-polynomial, because it depends "
                 "on the size of the capacity number, not just the item count. Walking back finds which rows "
                 "changed the value."),
            "a dict of reachable weights": ('''
                def max_value(items, capacity):
                    best = {0: (0, ())}                       # weight used -> (value, names)
                    for name, w, v in items:
                        for used, (value, names) in list(best.items()):
                            new = used + w
                            if new <= capacity and (new not in best or best[new][0] < value + v):
                                best[new] = (value + v, names + (name,))
                    value, names = max(best.values())
                    return value, list(names)
            ''', "Only weights you can actually reach are stored, so a huge capacity with a few heavy items stays "
                 "cheap. Iterating over a snapshot (list(best.items())) stops an item being used twice in the "
                 "same round; without it this would be the unbounded knapsack."),
        },
    ),
    dict(
        id="21.7", kind="project", title="A courier route planner",
        task="""
        A routes file has one route per line, `A B minutes` (undirected, whole minutes >= 0); `#` starts a
        comment and blank lines are ignored. Build:

        - `plan(text, start, end, avoid=())` returns `(minutes, [start, ..., end])` for the quickest route that
          doesn't pass through any branch in `avoid`, or `None` if there is none. Raise `ValueError` with the
          line number for a bad line, for an unknown branch (start, end or avoided), and if asked to avoid the
          start or end.
        - `main(argv)`: `route FILE START END [--avoid BRANCH]...` prints `Central -> East -> West -> Docks: 20 min`
          and returns 0; prints `no route from X to Y` and returns 1; prints an error and returns 2 for an
          unreadable file or a `ValueError`.
        """,
        stub='''
        def read_routes(text):
            graph = {}
            for line in text.splitlines():
                if line.strip():
                    a, b, minutes = line.split()
                    graph.setdefault(a, []).append((b, int(minutes)))
            return graph

        def plan(text, start, end, avoid=()):
            raise NotImplementedError

        def main(argv):
            raise NotImplementedError
        ''',
        tests=r'''
        import contextlib
        import io
        import random

        ROUTES = """
        # the courier network: branch branch minutes
        Central North 7
        Central East 9
        Central West 14
        North East 10
        North Uni 15
        East West 2
        East Uni 11    # the bridge
        West Docks 9

        Uni Docks 6
        Island Pier 3
        """

        def run(m, argv):
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code, out = capture(m.main, argv)
            return code, out + err.getvalue()

        def test_plan(m):
            equal(m.plan(ROUTES, "Central", "Docks"), (20, ["Central", "East", "West", "Docks"]))
            equal(m.plan(ROUTES, "Docks", "Central"), (20, ["Docks", "West", "East", "Central"]), "both ways")
            equal(m.plan(ROUTES, "Central", "Docks", avoid=["East"]), (23, ["Central", "West", "Docks"]), "avoid East")
            equal(m.plan(ROUTES, "Central", "Docks", avoid=("East", "West")), (28, ["Central", "North", "Uni", "Docks"]),
                  "avoid East and West")
            equal(m.plan(ROUTES, "Uni", "Uni"), (0, ["Uni"]), "start == end")
            equal(m.plan(ROUTES, "Central", "Pier"), None, "unreachable")
            equal(m.plan(ROUTES, "Central", "Uni", avoid=["North", "East"]), (29, ["Central", "West", "Docks", "Uni"]),
                  "around both")

        def test_errors(m):
            e = raises(ValueError, m.plan, "Central North 7\nCentral East nine\n", "Central", "East")
            check("2" in str(e), f"the error should name line 2: {e}")
            raises(ValueError, m.plan, "Central North\n", "Central", "North")
            raises(ValueError, m.plan, "Central North -3\n", "Central", "North")
            e = raises(ValueError, m.plan, ROUTES, "Central", "Moon")
            check("Moon" in str(e), f"the error should name the unknown branch: {e}")
            raises(ValueError, m.plan, ROUTES, "Central", "Docks", avoid=["Atlantis"])
            raises(ValueError, m.plan, ROUTES, "Central", "Docks", avoid=["Docks"])

        def test_random(m):
            rng = random.Random(10)
            for _ in range(60):
                n = rng.randint(2, 8)
                names = [f"b{i}" for i in range(n)]
                pairs = rng.sample([(a, b) for i, a in enumerate(names) for b in names[i + 1:]], rng.randint(0, n * (n - 1) // 2))
                w = {frozenset(p): rng.randint(0, 20) for p in pairs}
                lines = [f"{a} {b} {w[frozenset((a, b))]}" for a, b in pairs] + [f"{x} {x} 0" for x in names]
                rng.shuffle(lines)
                text = "\n".join(lines)
                d = {(a, b): (0 if a == b else w.get(frozenset((a, b)), float("inf"))) for a in names for b in names}
                for k in names:
                    for a in names:
                        for b in names:
                            d[a, b] = min(d[a, b], d[a, k] + d[k, b])
                start, end = rng.sample(names, 2)
                got = m.plan(text, start, end)
                if d[start, end] == float("inf"):
                    equal(got, None, f"plan to unreachable {end}")
                    continue
                cost, path = got
                equal(cost, d[start, end], f"cost {start} -> {end} in:\n{text}")
                check(path[0] == start and path[-1] == end and
                      sum(w[frozenset(p)] for p in zip(path, path[1:])) == cost, f"path {path} doesn't cost {cost}")

        def test_main(m):
            with tmpdir():
                with open("routes.txt", "w") as fh:
                    fh.write(ROUTES)
                code, out = run(m, ["routes.txt", "Central", "Docks"])
                equal(code, 0, "exit code")
                check("Central -> East -> West -> Docks: 20 min" in out, f"output was:\n{out}")
                code, out = run(m, ["routes.txt", "Central", "Docks", "--avoid", "East", "--avoid", "West"])
                equal(code, 0, "exit code with --avoid")
                check("Central -> North -> Uni -> Docks: 28 min" in out, f"output was:\n{out}")
                code, out = run(m, ["routes.txt", "Central", "Pier"])
                check(code == 1 and "no route from Central to Pier" in out, f"unreachable: code {code}, output:\n{out}")
                code, out = run(m, ["routes.txt", "Central", "Moon"])
                check(code == 2 and "Moon" in out, f"unknown branch: code {code}, output:\n{out}")
                code, out = run(m, ["missing.txt", "Central", "Docks"])
                equal(code, 2, "exit code for a missing file")
        ''',
        alts={
            "argparse + Dijkstra with a came-from dict": ('''
                import argparse
                import heapq
                import sys

                def read_routes(text):
                    graph = {}
                    for n, line in enumerate(text.splitlines(), 1):
                        line = line.split("#", 1)[0].strip()
                        if not line:
                            continue
                        parts = line.split()
                        if len(parts) != 3 or not parts[2].isdigit():
                            raise ValueError(f"line {n}: expected 'A B minutes', got {line!r}")
                        a, b, minutes = parts[0], parts[1], int(parts[2])
                        graph.setdefault(a, []).append((b, minutes))
                        graph.setdefault(b, []).append((a, minutes))
                    return graph

                def plan(text, start, end, avoid=()):
                    graph = read_routes(text)
                    for name in (start, end, *avoid):
                        if name not in graph:
                            raise ValueError(f"unknown branch {name!r}")
                    if start in avoid or end in avoid:
                        raise ValueError("can't avoid the start or the end")
                    blocked = set(avoid)
                    dist, prev, heap = {start: 0}, {}, [(0, start)]
                    while heap:
                        d, u = heapq.heappop(heap)
                        if u == end:
                            break
                        if d > dist[u]:
                            continue
                        for v, minutes in graph[u]:
                            if v not in blocked and d + minutes < dist.get(v, float("inf")):
                                dist[v], prev[v] = d + minutes, u
                                heapq.heappush(heap, (d + minutes, v))
                    if end not in dist:
                        return None
                    path = [end]
                    while path[-1] != start:
                        path.append(prev[path[-1]])
                    return dist[end], path[::-1]

                def main(argv):
                    parser = argparse.ArgumentParser(prog="route", description="quickest courier route")
                    parser.add_argument("routes")
                    parser.add_argument("start")
                    parser.add_argument("end")
                    parser.add_argument("--avoid", action="append", default=[], metavar="BRANCH")
                    args = parser.parse_args(argv)
                    try:
                        with open(args.routes, encoding="utf-8") as fh:
                            result = plan(fh.read(), args.start, args.end, args.avoid)
                    except (OSError, ValueError) as e:
                        print(f"route: {e}", file=sys.stderr)
                        return 2
                    if result is None:
                        print(f"no route from {args.start} to {args.end}")
                        return 1
                    minutes, path = result
                    print(f"{' -> '.join(path)}: {minutes} min")
                    return 0

                if __name__ == "__main__":
                    sys.exit(main(sys.argv[1:]))
            ''', "Parsing, planning and the command line are three layers: plan() takes text, so it is tested "
                 "without files, and main() only translates between argv, files, printing and exit codes. "
                 "`isdigit()` rejects negative minutes for free, and avoided branches are simply never relaxed. "
                 "Stopping when `end` is popped is safe: it is settled."),
            "heap of whole paths": ('''
                import argparse
                import heapq
                import re
                import sys

                LINE = re.compile(r"(\\S+)\\s+(\\S+)\\s+(\\d+)")

                def plan(text, start, end, avoid=()):
                    graph = {}
                    for n, raw in enumerate(text.splitlines(), 1):
                        line = raw.partition("#")[0].strip()
                        if not line:
                            continue
                        m = LINE.fullmatch(line)
                        if not m:
                            raise ValueError(f"line {n}: can't read {line!r}")
                        a, b, w = m[1], m[2], int(m[3])
                        graph.setdefault(a, []).append((b, w))
                        graph.setdefault(b, []).append((a, w))
                    unknown = [x for x in (start, end, *avoid) if x not in graph]
                    if unknown:
                        raise ValueError(f"unknown branch: {', '.join(unknown)}")
                    if {start, end} & set(avoid):
                        raise ValueError("can't avoid the start or the end")
                    done, heap = set(avoid), [(0, [start])]
                    while heap:
                        cost, path = heapq.heappop(heap)
                        u = path[-1]
                        if u == end:
                            return cost, path
                        if u in done:
                            continue
                        done.add(u)
                        for v, w in graph[u]:
                            if v not in done:
                                heapq.heappush(heap, (cost + w, path + [v]))
                    return None

                def main(argv):
                    parser = argparse.ArgumentParser(prog="route")
                    parser.add_argument("routes")
                    parser.add_argument("start")
                    parser.add_argument("end")
                    parser.add_argument("--avoid", action="append", default=[])
                    args = parser.parse_args(argv)
                    try:
                        with open(args.routes, encoding="utf-8") as fh:
                            text = fh.read()
                        result = plan(text, args.start, args.end, args.avoid)
                    except (OSError, ValueError) as e:
                        print(f"error: {e}", file=sys.stderr)
                        return 2
                    if result is None:
                        print(f"no route from {args.start} to {args.end}")
                        return 1
                    print(f"{' -> '.join(result[1])}: {result[0]} min")
                    return 0
            ''', "Each heap entry carries its whole path, so there is no came-from dict to rebuild, and the first "
                 "time `end` is popped its path is the answer. Copying paths costs O(length) per push, fine for "
                 "a city map but not for a road network. Avoided branches go straight into `done`."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="from collections import deque\nq = deque([1, 2])\nq.appendleft(0)\nq.append(3)\nprint(q.popleft(), q.pop())"),
    dict(kind="predict", code="import heapq\nh = []\nfor x in [5, 1, 4]:\n    heapq.heappush(h, (x, str(x)))\nprint(heapq.heappop(h), len(h))",
         why="heapq is a min-heap ordered by the whole tuple, so the cost goes first."),
    dict(kind="predict", code='from graphlib import TopologicalSorter\nprint(list(TopologicalSorter({"c": ["b"], "b": ["a"]}).static_order()))'),
    dict(kind="predict", code='from collections import defaultdict\ng = defaultdict(list)\ng["a"].append("b")\nprint(dict(g), "b" in g)',
         why="Only looked-up keys are created: b is a neighbour, not a key, until someone asks for g['b']."),
    dict(kind="predict", code="grid = [[0] * 3] * 2\ngrid[0][0] = 1\nprint(grid)",
         why="Both rows are the same list object. Build DP tables with a comprehension."),
    dict(kind="recall", q="Which data structure turns BFS into Dijkstra's algorithm?",
         a=["heap", "a heap", "priority queue", "a priority queue", "heapq", "min-heap"]),
    dict(kind="recall", q="Dijkstra's algorithm is only correct when the edge weights are...?",
         a=["non-negative", "nonnegative", "not negative", ">= 0", "positive or zero"]),
    dict(kind="recall", q="What is the edit distance between 'kitten' and 'sitting'?", a=["3"]),
    dict(kind="recall", q="Big-O cost of BFS on a graph with V nodes and E edges (adjacency lists)?",
         a=["O(V + E)", "O(V+E)", "V + E", "V+E"]),
]
