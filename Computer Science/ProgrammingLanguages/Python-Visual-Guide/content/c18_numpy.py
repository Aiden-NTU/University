"""Chapter 18 - NumPy done properly: why arrays, dtype/shape/strides, views and copies, broadcasting,
vectorisation and masks, axes and reductions, random generators and linear algebra, then Matplotlib
and pandas briefly."""
import matplotlib

matplotlib.use("Agg")

from generator import canvas as C  # noqa: E402
from generator import fonts as F  # noqa: E402
from content.kit import (L, R, W, callout, code, flow, practice, section, stamp, sub, table,  # noqa: E402
                         title_block, two_ways)

ORDER = 18
NUM = 18
TITLE = "NumPy done properly"
SHORT = "NumPy"
SLUG = "NumPy"
ACCENT = C.BLUE
ROWS = [C.BLUE, C.PURPLE, C.ORANGE]


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def cell(pg, x, y, w, h, s, col, size=9.5, dash=None, edge=None):
    pg.rect(x, y, w, h, edge or col, 1.0, fillcolor=None if dash else C.LIGHT[col], r=2, dash=dash)
    pg.text(x + w / 2, y + (h - 12) / 2, s, size, C.INK if not dash else C.GREY, F.MONO, align="center")


# ----------------------------------------------------------------------------- pictures
def list_vs_array(f):
    """A list is a row of pointers to separate objects; an ndarray is one typed block of raw numbers."""
    y = f.reserve(170)
    pg = f.pg
    vals = ["3", "1", "4", "1"]
    pg.text(L, y, "Python list [3, 1, 4, 1]", 10.5, C.INK, F.BOLD)
    xs = [L + 10 + i * 30 for i in range(4)]
    for x in xs:
        pg.rect(x, y + 22, 28, 22, C.GREY, 1.0, fillcolor="#f4f5f7", r=2)
        pg.dot(x + 14, y + 33, 2.4, C.ORANGE)
    objs = [(L + 0, y + 92), (L + 62, y + 118), (L + 118, y + 86), (L + 170, y + 120)]
    for (ox, oy), v, x in zip(objs, vals, xs):
        pg.rect(ox, oy, 46, 30, C.GREY, 1.0, fillcolor="#ffffff", r=4)
        pg.text(ox + 4, oy + 2, "int", 7.5, C.GREY, F.BOLD)
        pg.text(ox + 23, oy + 13, v, 10, C.INK, F.MONO, align="center")
        pg.arrow(x + 14, y + 35, ox + 23, oy - 1, C.ORANGE, 0.9, head=4)
    pg.note(L, y + 152, "4 pointers + 4 full objects, anywhere", C.GREY, 13)
    rx = L + 270
    pg.text(rx, y, "np.array([3, 1, 4, 1])", 10.5, C.INK, F.BOLD)
    pg.rect(rx, y + 22, 150, 40, ACCENT, 1.2, fillcolor=C.LIGHT[ACCENT], r=5)
    pg.text(rx + 8, y + 26, "dtype int64, shape (4,)", 9, ACCENT, F.BOLD)
    pg.text(rx + 8, y + 42, "strides (8,), data →", 9, ACCENT)
    for i, v in enumerate(vals):
        cell(pg, rx + i * 44, y + 96, 44, 26, v, ACCENT, 10.5)
    pg.arrow(rx + 120, y + 64, rx + 4, y + 94, ACCENT, 1.0, head=5)
    for i in range(5):
        pg.text(rx + i * 44, y + 124, f"{i * 8}", 7.5, C.GREY, align="center")
    pg.note(rx, y + 152, "one block: 4 × 8 bytes, no pointers", C.GREY, 13)


def layout_picture(f):
    """The 3x4 grid you think in, and the single row of bytes it really is."""
    y = f.reserve(204)
    pg = f.pg
    cw, chh = 32, 22
    for r in range(3):
        for c in range(4):
            cell(pg, L + 10 + c * cw, y + 18 + r * chh, cw, chh, str(r * 4 + c), ROWS[r])
    pg.text(L + 10, y, "what you see: a.shape == (3, 4)", 9.5, C.GREY, F.BOLD)
    pg.text(L + 190, y + 20, "a.dtype    int64  (8 bytes each)", 10, C.INK, F.MONO)
    pg.text(L + 190, y + 38, "a.shape    (3, 4)", 10, C.INK, F.MONO)
    pg.text(L + 190, y + 56, "a.strides  (32, 8)", 10, C.INK, F.MONO)
    pg.note(L + 190, y + 72, "bytes to jump for the next row, next column", C.PURPLE, 13)
    by = y + 128
    bw = 36
    pg.text(R, by - 18, "what is stored: 12 × 8 = 96 bytes in a row", 9.5, C.GREY, F.BOLD, align="right")
    for i in range(12):
        cell(pg, L + 10 + i * bw, by, bw, 24, str(i), ROWS[i // 4])
        pg.text(L + 10 + i * bw, by + 26, str(i * 8), 7.5, C.GREY, align="center")
    pg.arrow(L + 28, by - 1, L + 28 + bw, by - 1, C.RED, 1.1, bend=-0.6, head=4)
    pg.note(L + 52, by - 34, "+8: next column", C.RED, 13)
    pg.arrow(L + 28, by + 36, L + 28 + 4 * bw, by + 36, C.GREEN, 1.1, bend=0.25, head=4)
    pg.note(L + 80, by + 50, "+32: next row", C.GREEN, 13)
    pg.note(R, by + 50, "a[r, c] lives at  r*32 + c*8", C.INK, 13, align="right")


def view_picture(f):
    """Two headers, one buffer: the slice a[:, 1] is a different window on the same bytes."""
    y = f.reserve(158)
    pg = f.pg
    bw = 36
    by = y + 62
    for i in range(12):
        hit = i % 4 == 1
        cell(pg, L + 10 + i * bw, by, bw, 24, str(i), ROWS[i // 4], edge=C.RED if hit else None)
        if hit:
            pg.rect(L + 11 + i * bw, by + 1, bw - 2, 22, C.RED, 1.8, r=2)
    pg.rect(L + 10, y, 210, 36, ACCENT, 1.1, fillcolor=C.LIGHT[ACCENT], r=5)
    pg.text(L + 18, y + 4, "a", 10, ACCENT, F.BOLD)
    pg.text(L + 18, y + 18, "offset 0, shape (3, 4), strides (32, 8)", 8.5, C.INK, F.MONO)
    pg.arrow(L + 30, y + 37, L + 22, by - 2, ACCENT, 1.0, head=4)
    hx = L + 250
    pg.rect(hx, by + 52, 230, 36, C.RED, 1.1, fillcolor=C.LIGHT[C.RED], r=5)
    pg.text(hx + 8, by + 56, "col = a[:, 1]", 10, C.RED, F.BOLD)
    pg.text(hx + 8, by + 70, "offset 8, shape (3,), strides (32,)", 8.5, C.INK, F.MONO)
    for i in (1, 5, 9):
        pg.arrow(hx + 20 + i * 4, by + 51, L + 10 + i * bw + bw / 2, by + 26, C.RED, 0.9, head=4)
    pg.note(L + 10, by + 46, "no bytes copied: writing\nthrough col changes a", C.RED, 13)


def broadcast_picture(f):
    """(3, 1) + (5,) -> (3, 5): size-1 axes are stretched, without copying, to match."""
    y = f.reserve(132)
    pg = f.pg
    cw, chh = 24, 22
    col = [0, 10, 20]
    row = [0, 1, 2, 3, 4]
    x0 = L + 4
    for r in range(3):
        for c in range(5):
            cell(pg, x0 + c * cw, y + 16 + r * chh, cw, chh, str(col[r]), C.PURPLE, 9, dash=None if c == 0 else (2, 2))
    pg.text(x0, y, "col: (3, 1)", 9.5, C.PURPLE, F.BOLD)
    pg.text(x0 + 5 * cw + 10, y + 40, "+", 16, C.INK, F.BOLD)
    x1 = x0 + 5 * cw + 30
    for r in range(3):
        for c in range(5):
            cell(pg, x1 + c * cw, y + 16 + r * chh, cw, chh, str(row[c]), C.ORANGE, 9, dash=None if r == 0 else (2, 2))
    pg.text(x1, y, "row: (5,) → (1, 5)", 9.5, C.ORANGE, F.BOLD)
    pg.text(x1 + 5 * cw + 10, y + 40, "=", 16, C.INK, F.BOLD)
    x2 = x1 + 5 * cw + 30
    for r in range(3):
        for c in range(5):
            cell(pg, x2 + c * cw, y + 16 + r * chh, cw, chh, str(col[r] + row[c]), ACCENT, 9)
    pg.text(x2, y, "result: (3, 5)", 9.5, ACCENT, F.BOLD)
    pg.note(L, y + 92, "dashed cells are never stored: NumPy re-reads the same value (a stride of 0)", C.GREY, 13)


def axis_picture(f, m):
    """sum(axis=0) collapses the rows (down the page); sum(axis=1) collapses the columns (across)."""
    y = f.reserve(150)
    pg = f.pg
    cw, chh = 34, 24
    x0 = L + 60
    for r in range(3):
        for c in range(4):
            cell(pg, x0 + c * cw, y + 8 + r * chh, cw, chh, str(m[r][c]), ROWS[r], 10)
    for c in range(4):
        cell(pg, x0 + c * cw, y + 8 + 3 * chh + 30, cw, chh, str(sum(m[r][c] for r in range(3))), C.GREEN, 10)
    pg.arrow(x0 + 2 * cw, y + 8 + 3 * chh + 3, x0 + 2 * cw, y + 8 + 3 * chh + 27, C.GREEN, 1.3, head=5)
    pg.note(x0 - 52, y + 8 + 3 * chh + 32, "axis=0", C.GREEN, 13)
    xr = x0 + 4 * cw + 34
    for r in range(3):
        cell(pg, xr, y + 8 + r * chh, cw, chh, str(sum(m[r])), C.RED, 10)
    pg.arrow(x0 + 4 * cw + 3, y + 8 + 1.5 * chh, xr - 3, y + 8 + 1.5 * chh, C.RED, 1.3, head=5)
    pg.note(xr + cw + 8, y + 8 + chh, "axis=1: across each row\n→ one total per branch", C.RED, 13)
    pg.note(x0 + 4 * cw + 30, y + 8 + 3 * chh + 30, "axis=0: down each column\n→ one total per month", C.GREEN, 13)


def plot(f, fig, w=W * 0.86):
    fw, fh = fig.get_size_inches()
    h = w * fh / fw
    y = f.reserve(h + 12)
    f.pg.mpl(fig, L + (W - w) / 2, y, w)


# ----------------------------------------------------------------------------- pages
LOANS = [[5, 3, 8, 2], [1, 7, 4, 6], [9, 2, 3, 5]]


def title_page(ch):
    title_block(ch, 18, TITLE, "the array is a block of memory with a shape painted on it", ACCENT)
    f = ch.flow(top=190)
    f.p("The Computing module showed you NumPy's {B:what}. This chapter is the {B:why}: once you can picture an "
        "array in memory, views, broadcasting and the speed all stop being magic. Start with the difference "
        "that causes everything else:", 14, gap=10)
    list_vs_array(f)
    code(f, """
        import timeit
        import numpy as np

        days = list(range(1_000_000))
        arr = np.arange(1_000_000)

        def with_list():
            return [min(d * 0.25, 5.0) for d in days]      # a million boxed objects, one at a time

        def with_numpy():
            return np.minimum(arr * 0.25, 5.0)              # C loops over raw doubles

        assert with_list() == with_numpy().tolist()
        t_list, t_np = (min(timeit.repeat(fn, number=1, repeat=3)) for fn in (with_list, with_numpy))
        print(f"list {t_list * 1000:.0f} ms, numpy {t_np * 1000:.1f} ms: {t_list / t_np:.0f}x faster")
    """, notes={13: "same answer first", 14: "best of 3 runs each"})
    f.p("Python's loop handles a {B:boxed object} on every step: look up its type, dispatch the operation, "
        "allocate a new object for the result. NumPy checks the type once for the whole block, then runs a "
        "tight loop in C over raw machine numbers, often using SIMD instructions to do several at a time.",
        13.5, gap=8)


def layout_section(f):
    sec(f, "dtype, shape, strides: the three facts", room=430)
    f.p("Every array is a {B:header} plus a {B:buffer}. The header says how to read the bytes: what each item "
        "is (`dtype`), the grid it forms (`shape`), and how many bytes to jump along each axis (`strides`):",
        13.5, gap=8)
    code(f, """
        a = np.arange(12).reshape(3, 4)
        print(a)
        print(a.dtype, a.shape, a.strides, a.itemsize, a.nbytes)
        print(a[1, 2], a[1], a[:, 2])
    """, notes={4: "row 1, column 2 / a row / a column"})
    layout_picture(f)
    f.p("The dtype is a contract: every item has the same type and size, which is what makes the C loop "
        "possible. The price is that NumPy numbers behave like C numbers, not Python ones:", 13.5, gap=8)
    code(f, """
        small = np.array([120, 127], dtype=np.int8)
        print(small + 10)                               # wraps around, no error
        print(np.array([1, 2]) / 2, np.array([1, 2]) // 2)
        print(np.array([1, 2.5, True]).dtype, np.array(["a", 1]).dtype)
        print(np.array([2**62]) * 4, 2**62 * 4)
    """, notes={2: "int8 holds -128..127", 4: "everything upcast to one type", 5: "int64 overflow vs Python's big int"})
    table(f, ["dtype", "bytes", "holds", "typical use"], [
        ["`int64` / `int32`", "8 / 4", "whole numbers, fixed range", "counts, indexes (default int)"],
        ["`uint8`", "1", "0..255", "image pixels"],
        ["`float64` / `float32`", "8 / 4", "IEEE floats (Ch 11)", "default float / GPUs, big data"],
        ["`bool`", "1", "True / False", "masks (later this chapter)"],
        ["`<U10`", "40", "fixed-width text", "labels (pandas usually better)"],
        ["`object`", "8", "pointers to Python objects", "{R:avoid}: back to slow boxes"],
    ], widths=[1.9, 0.8, 2.1, 2.5], size=10.5)


def views_section(f):
    sec(f, "Views and copies: who owns the bytes?", room=430)
    f.p("Because the header and buffer are separate, NumPy can make a {B:new header over the same buffer}. "
        "Slicing does exactly that, so it's instant even on a gigabyte array, and writing through the slice "
        "writes into the original:", 13.5, gap=8)
    code(f, """
        a = np.arange(12).reshape(3, 4)
        col = a[:, 1]                           # a view: new header, same bytes
        col[:] = -1
        print(a)
        print(np.shares_memory(a, col), col.strides)

        picked = a[[0, 2]]                      # fancy indexing: always a copy
        picked[:] = 99
        print(a[0], np.shares_memory(a, picked))

        t = a.T                                 # transpose: just swap the strides
        print(t.shape, t.strides, np.shares_memory(a, t))
    """, notes={3: "writes into a", 11: "no data moved at all"})
    table(f, ["operation", "result", "why"], [
        ["`a[1:3]`, `a[:, 1]`, `a[::2]`", "view", "a regular step: offset + strides describe it"],
        ["`a.reshape(...)`, `a.T`, `a.ravel()`", "view (usually)", "same bytes, new shape or strides"],
        ["`a[[0, 2]]`, `a[a > 3]`", "copy", "irregular picks can't be described by strides"],
        ["`a * 2`, `np.sqrt(a)`, `a.copy()`", "new array", "its own memory, independent of `a`"],
    ], widths=[2.6, 1.3, 3.2], size=10.5)
    f.need(200)
    f.p("Here is the first view in memory: two headers reading the same twelve numbers.", 13.5, gap=6)
    view_picture(f)
    callout(f, "trap", "A function that receives a slice and modifies it in place is modifying the caller's "
            "array. If a function shouldn't have side effects, `.copy()` its input or build a new result. "
            "Strides also explain speed: walking along the last axis reads neighbouring bytes (cache-friendly); "
            "walking down a column of a big array jumps through memory.")


def broadcasting_section(f):
    sec(f, "Broadcasting: shapes that stretch", room=260)
    f.p("Arithmetic between arrays of different shapes works if NumPy can stretch them to a common shape. "
        "The rule is short enough to memorise:", 13.5, gap=8)
    callout(f, "rule", "Line the shapes up {B:from the right}. Each pair of sizes must be {B:equal}, or one of them "
            "must be {B:1} (a missing axis counts as 1). Axes of size 1 are stretched to match.")
    broadcast_picture(f)
    code(f, """
        days = np.arange(0, 25, 6)                      # 0, 6, 12, 18, 24 days late: shape (5,)
        rates = np.array([[0.10], [0.25], [0.50]])      # one rate per row: shape (3, 1)
        print(np.minimum(days * rates, 5.0))            # (3, 1) with (5,) -> a (3, 5) fee table

        due = np.array([3, 10, 4])
        print(due[:, None] - due[None, :])              # every pair: (3, 1) - (1, 3) -> (3, 3)
    """, notes={3: "no loops, no copies of days or rates", 6: "None adds an axis of size 1"})
    code(f, """
        np.ones(3) + np.ones(4)
    """, raises=ValueError)
    table(f, ["shapes", "line up from the right", "result"], [
        ["`(3, 4)` and `(4,)`", "4 = 4; 3 vs missing (1)", "`(3, 4)`: the row is added to every row"],
        ["`(3, 4)` and `(3,)`", "4 vs 3: neither is 1", "{R:error}: use `(3, 1)` for one value per row"],
        ["`(3, 1)` and `(1, 5)`", "1 vs 5, 3 vs 1", "`(3, 5)`: an outer table"],
        ["`(2, 3, 4)` and `(3, 1)`", "4 vs 1, 3 = 3, 2 vs missing", "`(2, 3, 4)`"],
    ], widths=[2.0, 2.4, 2.9], size=10.5)


def vectorise_section(f):
    sec(f, "Vectorise: masks instead of if, whole arrays instead of for", room=430)
    f.p("A comparison on an array gives a {B:boolean array} of the same shape: a mask. Masks replace the `if` "
        "inside a loop; `np.where` is the vectorised `x if cond else y`:", 13.5, gap=8)
    code(f, """
        rng = np.random.default_rng(7)
        days_late = rng.integers(-10, 30, size=12)
        print(days_late)

        late = days_late > 0                            # bool array, same shape
        print(late.sum(), days_late[late])              # True counts as 1; a mask selects
        fees = np.where(late, np.minimum(days_late * 0.25, 5.0), 0.0)
        print(fees.sum(), fees.max(), fees.argmax())
    """, notes={5: "a mask", 7: "where(cond, if_true, if_false)", 8: "argmax: the index of the max"})
    two_ways(f, ("a Python loop", """
        total = 0.0
        for d in days_late:
            if d > 0:
                total += min(d * 0.25, 5.0)
        print(total)
    """), ("vectorised", """
        paid = np.clip(days_late, 0, None) * 0.25
        total = np.minimum(paid, 5.0).sum()
        print(total)
    """), verdict=[("reads like the formula", 2, 5), ("speed on big arrays", 1, 5)], ns=f.ch._ns)
    f.p("Same answer. The vectorised version states {B:what} to compute over the whole array and leaves the "
        "looping to C, which is where the speed on the chapter's first page came from.", 13.5, gap=8)
    callout(f, "trap", "`if days_late > 0:` raises `ValueError: The truth value of an array ... is ambiguous`: "
            "an array of booleans isn't one boolean. Say which you mean with `.any()` or `.all()`. Likewise "
            "combine masks with `&`, `|`, `~` and parentheses, `(a > 0) & (a < 10)`, never `and` / `or`.")


def axes_section(f):
    sec(f, "Axes and reductions", room=420)
    f.p("A {B:reduction} (`sum`, `mean`, `max`, `argmax`, `std`...) collapses an axis. `axis=0` runs down "
        "the rows and leaves one value per column; `axis=1` runs across and leaves one value per row. Here: "
        "loans at 3 branches (rows) over 4 months (columns):", 13.5, gap=8)
    axis_picture(f, LOANS)
    code(f, """
        loans = np.array([[5, 3, 8, 2],
                          [1, 7, 4, 6],
                          [9, 2, 3, 5]])
        print(loans.sum(axis=0), loans.sum(axis=1), loans.sum())
        print(loans.argmax(axis=1))                         # busiest month per branch
        share = loans / loans.sum(axis=1, keepdims=True)    # (3, 4) / (3, 1)
        print(share.round(2))
    """, notes={6: "keepdims leaves (3, 1), ready to broadcast"})
    callout(f, "honest", "Floating-point sums lose precision as they grow (Ch 11). `np.sum` uses pairwise "
            "summation, which is far more accurate than a naive loop, and `float64` is the safe default; "
            "`float32` accumulates error quickly. For an exact sum of Python floats there's `math.fsum`.")


def random_linalg_section(f):
    sec(f, "Random numbers, linear algebra, a plot", room=430)
    f.p("Make randomness {B:reproducible} with a seeded `Generator` (not the old `np.random.seed` global). "
        "Then let linear algebra fit a straight line through noisy data by least squares:", 13.5, gap=8)
    code(f, """
        rng = np.random.default_rng(seed=2026)
        copies = rng.integers(1, 6, size=40)                 # copies of each title on the shelf
        loans = 3 * copies + rng.normal(0, 2, size=40)       # the hidden rule, plus noise

        A = np.column_stack([copies, np.ones(40)])           # rows: [copies, 1]
        (slope, intercept), *_ = np.linalg.lstsq(A, loans)
        print(f"loans ≈ {slope:.2f} × copies + {intercept:.2f}")

        M, v = np.array([[2, 1], [1, 3]]), np.array([5, 10])
        x = np.linalg.solve(M, v)                            # solve M @ x == v exactly
        print(x, M @ x)
    """, notes={1: "same seed, same numbers, every run", 6: "best slope and intercept",
                10: "@ is matrix multiplication"})
    code(f, """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 2.4))
        ax.scatter(copies, loans, s=14, alpha=0.6, label="titles")
        xs = np.array([1, 5])
        ax.plot(xs, slope * xs + intercept, color="C3", label="least-squares fit")
        ax.set(xlabel="copies on the shelf", ylabel="loans per year")
        ax.legend()
        fig.tight_layout()                       # then plt.show() or fig.savefig("fit.png")
    """)
    plot(f, f.ch._ns["fig"])


def pandas_section(f):
    sec(f, "pandas, briefly: labelled columns on top of NumPy", room=360)
    f.p("`pandas` adds names: a `DataFrame` is a table whose columns are NumPy arrays with labels, missing-value "
        "handling and SQL-like operations (Ch 12's `GROUP BY` in one line):", 13.5, gap=8)
    code(f, """
        import pandas as pd

        df = pd.DataFrame({"branch": ["north", "south", "north", "east", "south", "north"],
                           "title": ["Dune", "Emma", "Emma", "Dune", "Dune", "Ulysses"],
                           "days": [14, 21, 7, 14, 28, 14]})
        print(df.groupby("branch")["days"].agg(["count", "mean"]))
        print(type(df["days"].to_numpy()).__name__, df["days"].to_numpy().dtype)
    """, notes={6: "GROUP BY branch", 7: "underneath: an ndarray"})
    table(f, ["reach for", "when"], [
        ["plain Python + `csv`/`sqlite3`", "small data, mixed types, or logic per record"],
        ["NumPy", "numbers in a grid, the same operation on every element"],
        ["pandas", "tables with named, differently-typed columns: filter, group, join"],
        ["Matplotlib", "any plot; pandas' `.plot()` calls it for you"],
    ], widths=[2.4, 4.4], size=10.5)


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 18)
    stamp(f, [
        (1, "An `ndarray` is one contiguous typed buffer plus a header (dtype, shape, strides). Slices are views "
            "that share the buffer; fancy and boolean indexing copy."),
        (5, "`ndarray` (n-dimensional, one dtype), pandas `Series`/`DataFrame` (labelled columns)."),
        (11, "Not stdlib: `numpy`, `matplotlib`, `pandas` from pip (Ch 19). The stdlib's `array` module and "
             "`statistics` cover small cases."),
    ])
    callout(f, "other", "C: an array {B:is} this buffer, and a 2-D array is row-major exactly like NumPy's "
            "default. Fortran, MATLAB and Julia store columns first. R and MATLAB are vectorised by design. "
            "Java has primitive arrays but no broadcasting. Rust: the `ndarray` crate. GPUs (PyTorch, JAX) "
            "use the same shape-and-strides model.")
    callout(f, "deep", "Vault notes: {b:16.5} Why an array abstraction exists · {b:16.6} Dtypes are "
            "representation contracts · {b:16.7} Shape, strides, and physical layout · {b:16.8} Views, copies, "
            "and aliasing · {b:16.9} Broadcasting as shape algebra · {b:16.10} Vectorisation and native kernels "
            "· {b:16.11} Reductions, axes, and numerical stability · {b:16.12} Randomness, generators, and "
            "reproducibility · {b:16.13} Linear algebra as array structure · {b:16.18} Grouping, aggregation, "
            "and transformation · {b:16.25} Visualisation is an encoded argument.")


def build(ch):
    title_page(ch)
    f = flow(ch)
    layout_section(f)
    views_section(f)
    broadcasting_section(f)
    vectorise_section(f)
    axes_section(f)
    random_linalg_section(f)
    pandas_section(f)
    finish(ch)
