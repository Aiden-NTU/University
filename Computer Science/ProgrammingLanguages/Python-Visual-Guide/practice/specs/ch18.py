NO_LOOPS = ("For", "While", "ListComp", "SetComp", "DictComp", "GeneratorExp")

EXERCISES = [
    dict(
        id="18.1", kind="build", title="A fee table by broadcasting", needs=["numpy"],
        task="""
        Write `fee_table(days, rates, cap)`. `days` is a 1-D array of days late (negative means early) and
        `rates` a 1-D array of fees per day. Return a 2-D float array with one **row per rate** and one
        **column per day**: `min(max(day, 0) * rate, cap)`. Lists should work too (`np.asarray`).
        No Python loops or comprehensions: let broadcasting build the table.
        """,
        stub='''
        import numpy as np

        def fee_table(days, rates, cap):
            table = []
            for r in rates:
                table.append([min(max(d, 0) * r, cap) for d in days])
            return np.array(table)
        ''',
        tests=f'''
        import numpy as np

        def ref(days, rates, cap):
            return [[min(max(d, 0) * r, cap) for d in days] for r in rates]

        def test_values(m):
            days, rates = np.array([-3, 0, 1, 10, 30]), np.array([0.1, 0.25, 0.5])
            got = m.fee_table(days, rates, 5.0)
            check(isinstance(got, np.ndarray), "return a NumPy array")
            equal(got.shape, (3, 5), "shape: one row per rate, one column per day")
            check(np.allclose(got, ref(days, rates, 5.0)), f"values:\\n{{got}}")

        def test_lists_and_random(m):
            equal(m.fee_table([2], [1.5], 9).tolist(), [[3.0]], "plain lists")
            rng = np.random.default_rng(3)
            for _ in range(5):
                days, rates = rng.integers(-20, 60, 17), rng.random(6)
                check(np.allclose(m.fee_table(days, rates, 4.0), ref(days, rates, 4.0)), "random tables")

        def test_no_loops(m):
            forbid(m, *{NO_LOOPS!r}, msg="use broadcasting instead of a Python loop or comprehension")
        ''',
        alts={
            "None adds the axis": ('''
                import numpy as np

                def fee_table(days, rates, cap):
                    days = np.clip(np.asarray(days), 0, None)
                    rates = np.asarray(rates, dtype=float)
                    return np.minimum(rates[:, None] * days[None, :], cap)
            ''', "rates[:, None] has shape (r, 1) and days[None, :] has shape (1, d), so the product is (r, d). "
                 "clip(…, 0, None) is the vectorised max(day, 0)."),
            "np.outer": ('''
                import numpy as np

                def fee_table(days, rates, cap):
                    late = np.maximum(np.asarray(days), 0)
                    return np.minimum(np.outer(rates, late), cap).astype(float)
            ''', "np.outer(a, b) is exactly a[:, None] * b[None, :]: a named function for the most common "
                 "broadcast. Reading the docs for a function you half-remember is the Ch 7 method again."),
        },
    ),
    dict(
        id="18.2", kind="fix", title="normalise_rows must not touch its input", needs=["numpy"],
        task="""
        `normalise_rows(m)` should return a **new float array** where each row of `m` is divided by that
        row's sum (a row of zeros stays zeros, with no warnings). The stub has three bugs: it changes the
        caller's array, it truncates to integers when `m` holds ints, and it divides by zero. It must also work
        when `m` is a view into a bigger array.
        """,
        stub='''
        import numpy as np

        def normalise_rows(m):
            out = m
            for i in range(len(out)):
                out[i] = out[i] / out[i].sum()
            return out
        ''',
        tests='''
        import numpy as np

        def test_new_float_array(m):
            a = np.array([[1, 3], [2, 2], [0, 0]])
            before = a.copy()
            with np.errstate(all="raise"):
                got = m.normalise_rows(a)
            check(np.array_equal(a, before), "the input array was modified")
            check(got.dtype.kind == "f", f"the result should hold floats, not {got.dtype}")
            check(np.allclose(got, [[0.25, 0.75], [0.5, 0.5], [0, 0]]), f"values:\\n{got}")

        def test_float_input_untouched(m):
            a = np.array([[2.0, 6.0]])
            got = m.normalise_rows(a)
            check(np.array_equal(a, [[2.0, 6.0]]), "a float input was modified")
            check(not np.shares_memory(a, got), "the result shares memory with the input")

        def test_view_input(m):
            big = np.arange(1, 13).reshape(3, 4)
            got = m.normalise_rows(big[:, ::2])
            check(np.allclose(got.sum(axis=1), 1), "each row sums to 1")
            check(np.array_equal(big, np.arange(1, 13).reshape(3, 4)), "the array behind the view was modified")
        ''',
        alts={
            "np.divide with where=": ('''
                import numpy as np

                def normalise_rows(m):
                    m = np.asarray(m, dtype=float)
                    sums = m.sum(axis=1, keepdims=True)
                    return np.divide(m, sums, out=np.zeros_like(m), where=sums != 0)
            ''', "out= is a fresh array of zeros, and where= only divides where the sum isn't 0, so zero rows "
                 "keep their zeros and no warning is raised. asarray may return the input itself, but out= "
                 "means we never write into it."),
            "copy, then a safe divisor": ('''
                import numpy as np

                def normalise_rows(m):
                    m = np.array(m, dtype=float)        # np.array always copies
                    sums = m.sum(axis=1)
                    safe = np.where(sums == 0, 1.0, sums)
                    return m / safe[:, None]
            ''', "Replace zero sums by 1 before dividing: 0 / 1 = 0, the answer we want. np.array copies by "
                 "default; np.asarray doesn't. Knowing which one you called is the views-and-copies lesson."),
        },
    ),
    dict(
        id="18.3", kind="build", title="A moving average without loops", needs=["numpy"],
        task="""
        Write `moving_average(x, k)`: the mean of every window of `k` neighbouring values in the 1-D array `x`,
        so the result has `len(x) - k + 1` items. Raise `ValueError` unless `1 <= k <= len(x)`. No Python
        loops or comprehensions, and it must handle a million values in well under a tenth of a second.
        """,
        stub='''
        import numpy as np

        def moving_average(x, k):
            return np.array([x[i:i + k].mean() for i in range(len(x) - k + 1)])
        ''',
        tests=f'''
        import numpy as np, time

        def test_values(m):
            equal(m.moving_average(np.array([1, 2, 3, 4, 5]), 2).tolist(), [1.5, 2.5, 3.5, 4.5], "k=2")
            equal(m.moving_average(np.array([4.0, 8.0]), 2).tolist(), [6.0], "one window")
            equal(m.moving_average(np.array([1, 2, 3]), 1).tolist(), [1.0, 2.0, 3.0], "k=1 is the data")

        def test_errors(m):
            raises(ValueError, m.moving_average, np.arange(3), 0)
            raises(ValueError, m.moving_average, np.arange(3), 4)

        def test_fast(m):
            x = np.random.default_rng(5).random(1_000_000)
            t0 = time.perf_counter()
            got = m.moving_average(x, 20)
            took = time.perf_counter() - t0
            want = np.convolve(x, np.ones(20) / 20, mode="valid")
            check(got.shape == want.shape and np.allclose(got, want), "wrong values on the big input")
            check(took < 0.1, f"took {{took:.2f}} s for a million values")

        def test_no_loops(m):
            forbid(m, *{NO_LOOPS!r}, msg="no Python loops or comprehensions here")
        ''',
        alts={
            "cumulative sum: each window is a difference": ('''
                import numpy as np

                def moving_average(x, k):
                    x = np.asarray(x, dtype=float)
                    if not 1 <= k <= len(x):
                        raise ValueError(f"window {k} doesn't fit {len(x)} values")
                    c = np.concatenate(([0.0], np.cumsum(x)))
                    return (c[k:] - c[:-k]) / k
            ''', "c[i] is the sum of the first i values, so a window's sum is c[i + k] - c[i]: one pass, O(n) "
                 "whatever k is. Over very long arrays the running sum can lose a little precision."),
            "sliding_window_view: windows as a 2-D view": ('''
                import numpy as np
                from numpy.lib.stride_tricks import sliding_window_view

                def moving_average(x, k):
                    x = np.asarray(x, dtype=float)
                    if not 1 <= k <= len(x):
                        raise ValueError(f"window {k} doesn't fit {len(x)} values")
                    return sliding_window_view(x, k).mean(axis=1)
            ''', "sliding_window_view builds an (n-k+1, k) view with strides (8, 8): every row starts one item "
                 "later, and no data is copied. Clearer, but O(n·k) work."),
        },
    ),
    dict(
        id="18.4", kind="explore", title="Group without a loop: unique and bincount", needs=["numpy"],
        task="""
        Two parallel arrays describe loans: `ids` (member ids, ints) and `days` (loan lengths). Write
        `per_member(ids, days)` returning three arrays: the distinct ids in increasing order, how many loans
        each had, and each one's mean loan length. Inputs are non-empty. No Python loops or comprehensions.
        Explore `np.unique` (look at its `return_*` options) and `np.bincount` (look at `weights`).
        """,
        stub='''
        import numpy as np

        def per_member(ids, days):
            out = {}
            for i, d in zip(ids, days):
                out.setdefault(i, []).append(d)
            keys = sorted(out)
            return np.array(keys), np.array([len(out[k]) for k in keys]), np.array([np.mean(out[k]) for k in keys])
        ''',
        tests=f'''
        import numpy as np
        from collections import defaultdict

        def ref(ids, days):
            g = defaultdict(list)
            for i, d in zip(ids.tolist(), days.tolist()):
                g[i].append(d)
            keys = sorted(g)
            return keys, [len(g[k]) for k in keys], [sum(g[k]) / len(g[k]) for k in keys]

        def test_small(m):
            u, c, mean = m.per_member(np.array([7, 3, 7, 7, 10]), np.array([14, 21, 7, 9, 28]))
            equal((u.tolist(), c.tolist()), ([3, 7, 10], [1, 3, 1]), "ids and counts")
            check(np.allclose(mean, [21, 10, 28]), f"means: {{mean}}")

        def test_random(m):
            rng = np.random.default_rng(8)
            for _ in range(5):
                ids, days = rng.integers(0, 50, 300) * 3 + 1000, rng.integers(1, 40, 300)
                u, c, mean = m.per_member(ids, days)
                keys, counts, means = ref(ids, days)
                equal((u.tolist(), c.tolist()), (keys, counts), "ids and counts")
                check(np.allclose(mean, means), "means")

        def test_no_loops(m):
            forbid(m, *{NO_LOOPS!r}, msg="find the NumPy functions that do the grouping for you")
        ''',
        alts={
            "unique(return_inverse, return_counts) + bincount(weights)": ('''
                import numpy as np

                def per_member(ids, days):
                    u, inverse, counts = np.unique(ids, return_inverse=True, return_counts=True)
                    totals = np.bincount(inverse, weights=days)
                    return u, counts, totals / counts
            ''', "inverse maps every loan to its member's position in u (0..len(u)-1), exactly the small-int "
                 "labels bincount wants; weights= sums days instead of counting. This is GROUP BY in NumPy."),
            "sort, find the run starts, reduceat": ('''
                import numpy as np

                def per_member(ids, days):
                    order = np.argsort(ids, kind="stable")
                    s_ids, s_days = ids[order], days[order]
                    starts = np.flatnonzero(np.r_[True, s_ids[1:] != s_ids[:-1]])
                    counts = np.diff(np.r_[starts, len(s_ids)])
                    return s_ids[starts], counts, np.add.reduceat(s_days, starts) / counts
            ''', "After sorting, each member is one run. A run starts wherever the id changes; reduceat sums "
                 "each run. More steps, but it's how unique works inside, and it extends to any ufunc."),
        },
    ),
    dict(
        id="18.5", kind="time", title="Nearest branch for 20,000 readers", needs=["numpy"],
        task="""
        `homes` is an `(n, 2)` array of reader locations and `branches` an `(m, 2)` array of library branches.
        `nearest_branch(homes, branches)` returns, for every home, the index of the closest branch (straight-
        line distance). The stub is correct but slow; make it handle 20,000 homes and 50 branches in under
        0.15 s, with the same answers. Hint: what shape is `homes[:, None, :] - branches[None, :, :]`?
        """,
        stub='''
        import math
        import numpy as np

        def nearest_branch(homes, branches):
            out = []
            for hx, hy in homes:
                dists = [math.hypot(hx - bx, hy - by) for bx, by in branches]
                out.append(dists.index(min(dists)))
            return np.array(out)
        ''',
        tests='''
        import math, time
        import numpy as np

        def ref(homes, branches):
            return [min(range(len(branches)), key=lambda j: math.dist(h, branches[j])) for h in homes.tolist()]

        def test_small(m):
            homes = np.array([[0.0, 0.0], [9.0, 9.0], [5.0, 1.0]])
            branches = np.array([[1.0, 1.0], [8.0, 8.0], [6.0, 0.0]])
            equal(list(np.asarray(m.nearest_branch(homes, branches))), [0, 1, 2], "three obvious cases")

        def test_random(m):
            rng = np.random.default_rng(12)
            homes, branches = rng.random((300, 2)) * 100, rng.random((15, 2)) * 100
            equal(np.asarray(m.nearest_branch(homes, branches)).tolist(), ref(homes, branches), "random points")

        def test_fast(m):
            rng = np.random.default_rng(13)
            homes, branches = rng.random((20_000, 2)) * 100, rng.random((50, 2)) * 100
            t0 = time.perf_counter()
            got = np.asarray(m.nearest_branch(homes, branches))
            took = time.perf_counter() - t0
            d = ((homes[:, None, :] - branches[None, :, :]) ** 2).sum(axis=2)
            check(np.array_equal(got, d.argmin(axis=1)), "different answers on the big input")
            check(took < 0.15, f"took {took:.2f} s; budget 0.15 s")
        ''',
        alts={
            "broadcast to (n, m, 2), argmin": ('''
                import numpy as np

                def nearest_branch(homes, branches):
                    diff = homes[:, None, :] - branches[None, :, :]     # (n, m, 2)
                    return (diff ** 2).sum(axis=2).argmin(axis=1)       # no sqrt: it doesn't change the order
            ''', "Broadcasting builds all n x m differences at once. Skipping the square root is safe because "
                 "sqrt is increasing, so the nearest by squared distance is the nearest. Memory: n·m·2 floats."),
            "a loop over the few branches, vectorised over the many homes": ('''
                import numpy as np

                def nearest_branch(homes, branches):
                    best = np.full(len(homes), np.inf)
                    idx = np.zeros(len(homes), dtype=np.intp)
                    for j, (bx, by) in enumerate(branches):          # 50 iterations, each over 20,000 homes
                        d = (homes[:, 0] - bx) ** 2 + (homes[:, 1] - by) ** 2
                        closer = d < best
                        best[closer], idx[closer] = d[closer], j
                    return idx
            ''', "Loop over the short axis, vectorise the long one: only n floats of extra memory instead of "
                 "n·m·2. With a million homes this version still fits in memory; the full broadcast may not."),
        },
    ),
    dict(
        id="18.6", kind="project", title="Game of Life on a torus", needs=["numpy"],
        task="""
        Mini-project. Write `life_step(board)` for Conway's Game of Life. `board` is a 2-D bool array whose
        edges wrap around (a torus). A live cell with 2 or 3 live neighbours survives; a dead cell with exactly
        3 comes alive; everything else is dead. Return a **new** bool array (don't modify `board`). Also write
        `run(board, steps)`. It must be quick: 10 steps on a 200 x 200 board in under 0.2 s.
        """,
        stub='''
        import numpy as np

        def life_step(board):
            rows, cols = board.shape
            new = np.zeros_like(board)
            for r in range(rows):
                for c in range(cols):
                    n = sum(board[(r + dr) % rows, (c + dc) % cols]
                            for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0))
                    new[r, c] = n == 3 or (board[r, c] and n == 2)
            return new

        def run(board, steps):
            for _ in range(steps):
                board = life_step(board)
            return board
        ''',
        tests='''
        import time
        import numpy as np

        def grid(rows, cols, cells):
            b = np.zeros((rows, cols), dtype=bool)
            for r, c in cells:
                b[r, c] = True
            return b

        def test_still_and_blinker(m):
            block = grid(6, 6, [(2, 2), (2, 3), (3, 2), (3, 3)])
            check(np.array_equal(m.life_step(block), block), "a 2x2 block never changes")
            blink = grid(5, 5, [(2, 1), (2, 2), (2, 3)])
            step = m.life_step(blink)
            check(np.array_equal(step, grid(5, 5, [(1, 2), (2, 2), (3, 2)])), "a blinker turns vertical")
            check(np.array_equal(m.run(blink, 2), blink), "and back after 2 steps")
            check(step.dtype == bool, "return a bool array")
            check(np.array_equal(blink, grid(5, 5, [(2, 1), (2, 2), (2, 3)])), "the input board was modified")

        def test_glider_wraps(m):
            g = grid(8, 8, [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)])
            check(np.array_equal(m.run(g, 4), np.roll(g, (1, 1), axis=(0, 1))), "a glider moves 1 down, 1 right")
            check(np.array_equal(m.run(g, 32), g), "after 32 steps on an 8x8 torus it is home again")

        def test_fast(m):
            b = np.random.default_rng(4).random((200, 200)) < 0.3
            t0 = time.perf_counter()
            m.run(b, 10)
            took = time.perf_counter() - t0
            check(took < 0.2, f"10 steps on 200x200 took {took:.2f} s; budget 0.2 s")
        ''',
        alts={
            "np.roll the board 8 ways": ('''
                import numpy as np

                SHIFTS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]

                def life_step(board):
                    n = sum(np.roll(board, s, axis=(0, 1)).astype(np.uint8) for s in SHIFTS)
                    return (n == 3) | (board & (n == 2))

                def run(board, steps):
                    for _ in range(steps):
                        board = life_step(board)
                    return board
            ''', "Each roll shifts the whole board one step, wrapping at the edges, so adding the 8 rolled copies "
                 "gives every cell's neighbour count at once. The rule is then two masks combined with | and &."),
            "pad with wrap, then add 8 slices": ('''
                import numpy as np

                def life_step(board):
                    p = np.pad(board.astype(np.uint8), 1, mode="wrap")     # copy the opposite edges around
                    rows, cols = board.shape
                    n = (p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
                         p[1:-1, :-2] +                p[1:-1, 2:] +
                         p[2:, :-2] + p[2:, 1:-1] + p[2:, 2:])
                    return (n == 3) | (board & (n == 2))

                def run(board, steps):
                    for _ in range(steps):
                        board = life_step(board)
                    return board
            ''', "Padding adds a one-cell border copied from the far side; then the 8 neighbour grids are just "
                 "views (slices) of the padded board, laid out exactly like the 3x3 neighbourhood."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", needs=["numpy"], code="import numpy as np\na = np.arange(6).reshape(2, 3)\nprint(a.shape, a.strides, a.T.strides)"),
    dict(kind="predict", needs=["numpy"], code="import numpy as np\na = np.arange(5)\nb = a[1:4]\nb[0] = 99\nprint(a)", why="A basic slice is a view: writing to it writes to a."),
    dict(kind="predict", needs=["numpy"], code="import numpy as np\na = np.arange(5)\nb = a[[1, 2, 3]]\nb[0] = 99\nprint(a)", why="Fancy indexing (a list of indexes) makes a copy."),
    dict(kind="predict", needs=["numpy"], code="import numpy as np\nprint((np.ones((3, 1)) + np.arange(4)).shape)"),
    dict(kind="predict", needs=["numpy"], code="import numpy as np\nprint(np.array([200], dtype=np.uint8) + np.array([100], dtype=np.uint8))", why="uint8 arithmetic wraps modulo 256."),
    dict(kind="predict", needs=["numpy"], code="import numpy as np\nm = np.array([[1, 2], [3, 4]])\nprint(m.sum(axis=0), m.sum(axis=1))"),
    dict(kind="predict", needs=["numpy"], code="import numpy as np\na = np.array([3, -1, 4, -1, 5])\nprint(a[a > 0], (a > 0).sum())"),
    dict(kind="recall", q="Which NumPy attribute gives the number of bytes to step along each axis?", a=["strides", "a.strides", ".strides"]),
    dict(kind="recall", q="Shapes (4, 3) and (4,): do they broadcast? (yes/no)", a=["no"]),
    dict(kind="recall", q="Which function makes a seeded, reproducible random Generator in NumPy?", a=["np.random.default_rng", "default_rng", "numpy.random.default_rng"]),
]
