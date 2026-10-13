EXERCISES = [
    dict(
        id="3.1", kind="fix", title="The function that changes your data",
        task="""
        `curve(scores, bonus)` should return a **new** dict where every student's list of marks has
        `bonus` added to each mark (capped at 100). It returns the right answer, but the caller's dict
        changes too, and later code breaks. Find the aliasing and fix it: the input must be untouched.
        """,
        stub='''
        def curve(scores, bonus):
            out = dict(scores)
            for name, marks in out.items():
                for i in range(len(marks)):
                    marks[i] = min(100, marks[i] + bonus)
            return out
        ''',
        tests='''
        import copy, random

        def test_result(m):
            equal(m.curve({"ana": [50, 98], "ben": []}, 5), {"ana": [55, 100], "ben": []}, "curve")

        def test_input_untouched_random(m):
            rng = random.Random(3)
            for _ in range(100):
                scores = {n: [rng.randint(0, 100) for _ in range(rng.randint(0, 5))] for n in rand_words(4, rng.randint(0, 99))}
                before = copy.deepcopy(scores)
                out = m.curve(scores, rng.randint(0, 20))
                equal(scores, before, "the input dict and its lists must not change")
                for k in out:
                    check(out[k] is not scores[k], "result lists must be new lists, not the caller's")
        ''',
        alts={
            "comprehension": ('''
                def curve(scores, bonus):
                    return {name: [min(100, m + bonus) for m in marks] for name, marks in scores.items()}
            ''', "Build new lists instead of editing: nothing to alias, and it reads like the spec."),
            "deepcopy then edit": ('''
                import copy

                def curve(scores, bonus):
                    out = copy.deepcopy(scores)
                    for marks in out.values():
                        for i, mark in enumerate(marks):
                            marks[i] = min(100, mark + bonus)
                    return out
            ''', "Works, but copies everything first; the comprehension builds the result directly."),
        },
    ),
    dict(
        id="3.2", kind="build", title="Write your own deep copy",
        task="""
        Write `deep_copy(obj)` (without the `copy` module) for data made of `list`, `dict`, `set`,
        `tuple` and immutable leaves (`int`, `float`, `str`, `bool`, `None`).

        The result must be equal to the original, and **no mutable object** (list, dict, set) may be
        shared between the two. Bonus (tested): if the same list appears twice in the input, the copy
        should contain one new list appearing twice too (use a `memo` dict keyed by `id()`).
        """,
        stub='''
        def deep_copy(obj, memo=None):
            ...
        ''',
        tests='''
        import random

        def mutables(o, acc):
            if isinstance(o, (list, dict, set)):
                acc.append(o)
            if isinstance(o, dict):
                for k, v in o.items():
                    mutables(v, acc)
            elif isinstance(o, (list, tuple, set)):
                for v in o:
                    mutables(v, acc)
            return acc

        def rand_obj(rng, d=0):
            r = rng.random()
            if d > 3 or r < 0.3:
                return rng.choice([1, 2.5, "s", None, True])
            if r < 0.5:
                return [rand_obj(rng, d + 1) for _ in range(rng.randint(0, 3))]
            if r < 0.7:
                return {rng.choice("abc"): rand_obj(rng, d + 1) for _ in range(rng.randint(0, 3))}
            if r < 0.85:
                return tuple(rand_obj(rng, d + 1) for _ in range(rng.randint(0, 3)))
            return {rng.randint(0, 5) for _ in range(3)}

        def test_random_structures(m):
            rng = random.Random(11)
            for _ in range(200):
                o = rand_obj(rng)
                c = m.deep_copy(o)
                equal(c, o, "copy equals original")
                ids = {id(x) for x in mutables(o, [])}
                check(not any(id(x) in ids for x in mutables(c, [])), "a mutable object is shared with the original")

        def test_shared_inside_stays_shared(m):
            inner = [1, 2]
            outer = [inner, inner, {"k": inner}]
            c = m.deep_copy(outer)
            check(c[0] is c[1] is c[2]["k"], "the same inner list should be copied once and reused")
            check(c[0] is not inner, "but it must be a new list")
        ''',
        alts={
            "recursive with memo": ('''
                def deep_copy(obj, memo=None):
                    if memo is None:
                        memo = {}
                    if id(obj) in memo:
                        return memo[id(obj)]
                    if isinstance(obj, list):
                        new = []
                        memo[id(obj)] = new
                        new.extend(deep_copy(x, memo) for x in obj)
                    elif isinstance(obj, dict):
                        new = {}
                        memo[id(obj)] = new
                        for k, v in obj.items():
                            new[k] = deep_copy(v, memo)
                    elif isinstance(obj, set):
                        new = {deep_copy(x, memo) for x in obj}
                    elif isinstance(obj, tuple):
                        new = tuple(deep_copy(x, memo) for x in obj)
                    else:
                        return obj
                    memo[id(obj)] = new
                    return new
            ''', "Registering a new list in memo *before* filling it also handles cycles (a list that contains "
                 "itself). That's exactly how copy.deepcopy works; read its source with inspect."),
        },
    ),
    dict(
        id="3.3", kind="explore", title="Spot the aliasing (id and is)",
        task="""
        Write `distinct_lists(obj)` that counts how many **distinct list objects** are reachable from
        `obj` (including `obj` itself if it's a list), following lists, tuples and dict values.
        A list reached twice counts once.

        `[[0] * 3] * 3` has 2 distinct lists (the outer one and the single shared row);
        `[[0] * 3 for _ in range(3)]` has 4. Identity is the key: `id(x)` or `is`.
        """,
        stub='''
        def distinct_lists(obj):
            ...
        ''',
        tests='''
        def test_grids(m):
            equal(m.distinct_lists([[0] * 3] * 3), 2, "[[0]*3]*3")
            equal(m.distinct_lists([[0] * 3 for _ in range(3)]), 4, "comprehension grid")
            equal(m.distinct_lists(5), 0, "not a list")

        def test_nested_and_cycles(m):
            a = [1]
            b = [a, (a, [a]), {"x": a, "y": [2]}]
            equal(m.distinct_lists(b), 4, "b, a, [a], [2]")
            c = []
            c.append(c)
            equal(m.distinct_lists(c), 1, "a list containing itself")
        ''',
        alts={
            "seen set of ids": ('''
                def distinct_lists(obj):
                    seen = set()
                    stack = [obj]
                    while stack:
                        o = stack.pop()
                        if isinstance(o, list):
                            if id(o) in seen:
                                continue
                            seen.add(id(o))
                            stack.extend(o)
                        elif isinstance(o, tuple):
                            stack.extend(o)
                        elif isinstance(o, dict):
                            stack.extend(o.values())
                    return len(seen)
            ''', "An explicit stack instead of recursion: no recursion limit, and the seen-set stops cycles. "
                 "The same pattern is a graph traversal (Ch 21)."),
        },
    ),
    dict(
        id="3.4", kind="build", title="Make it hashable",
        task="""
        Write `freeze(obj)` converting nested lists, dicts and sets into hashable equivalents, so the
        result can be a dict key or set member:

        - list → tuple (of frozen items), set → frozenset (of frozen items)
        - dict → frozenset of `(key, frozen value)` pairs
        - tuples are frozen item by item; immutable leaves are returned as they are

        Two inputs that are equal must freeze to equal (and equally hashed) results, so
        `freeze({"a": [1, 2]}) == freeze({"a": [1, 2]})`.
        """,
        stub='''
        def freeze(obj):
            ...
        ''',
        tests='''
        import random

        def test_hashable_and_equal(m):
            rng = random.Random(5)
            for _ in range(200):
                d = {rng.choice("abcd"): [rng.randint(0, 3) for _ in range(rng.randint(0, 3))] for _ in range(3)}
                same = {k: list(v) for k, v in reversed(list(d.items()))}
                f1, f2 = m.freeze(d), m.freeze(same)
                hash(f1)
                equal(f1, f2, "equal dicts (any insertion order) freeze equal")
                equal(hash(f1), hash(f2), "and hash equal")

        def test_kinds(m):
            f = m.freeze([1, {2, 3}, {"k": [4]}, (5, [6])])
            hash(f)
            check(isinstance(f, tuple), "a list becomes a tuple")
            check(m.freeze([1, 2]) != m.freeze([2, 1]), "order matters for lists")
            equal(m.freeze({1, 2}), m.freeze({2, 1}), "but not for sets")
            equal(m.freeze("text"), "text", "leaves unchanged")
        ''',
        alts={
            "recursive dispatch": ('''
                def freeze(obj):
                    if isinstance(obj, dict):
                        return frozenset((k, freeze(v)) for k, v in obj.items())
                    if isinstance(obj, (list, tuple)):
                        return tuple(freeze(x) for x in obj)
                    if isinstance(obj, (set, frozenset)):
                        return frozenset(freeze(x) for x in obj)
                    return obj
            ''', "A list and a tuple with the same items freeze to the same thing; usually what you want for "
                 "a cache key, but note it."),
            "functools.singledispatch": ('''
                from functools import singledispatch

                @singledispatch
                def freeze(obj):
                    return obj

                @freeze.register(list)
                @freeze.register(tuple)
                def _(obj):
                    return tuple(freeze(x) for x in obj)

                @freeze.register(set)
                @freeze.register(frozenset)
                def _(obj):
                    return frozenset(freeze(x) for x in obj)

                @freeze.register(dict)
                def _(obj):
                    return frozenset((k, freeze(v)) for k, v in obj.items())
            ''', "singledispatch picks the implementation by the argument's type, and other modules can "
                 "register new types without editing this one (Ch 4)."),
        },
    ),
    dict(
        id="3.5", kind="project", title="Mini-project: undo for a document",
        task="""
        Write a class `Document` holding a list of lines:

        - `Document(lines=None)`: starts with a **copy** of `lines` (or empty)
        - `lines` property: returns a copy, so callers can't change the document behind its back
        - `insert(i, text)`, `delete(i)`, `replace(i, text)`: edit, each one undoable
        - `undo()`: reverts the last edit (`IndexError` if there's nothing to undo); `redo()` re-applies it
        - a new edit after an undo clears the redo history (like every editor)

        The tests try hard to change your document through aliases. Then: compare storing full
        snapshots with storing small "inverse operations"; which uses less memory for a 10,000-line document?
        """,
        stub='''
        class Document:
            def __init__(self, lines=None):
                ...
        ''',
        tests='''
        import random

        def test_aliasing(m):
            start = ["a", "b"]
            d = m.Document(start)
            start.append("SNEAKY")
            equal(d.lines, ["a", "b"], "document must copy its input")
            got = d.lines
            got.append("SNEAKY")
            equal(d.lines, ["a", "b"], "lines must return a copy")

        def test_undo_redo(m):
            d = m.Document(["a"])
            d.insert(1, "b"); d.replace(0, "A"); d.delete(1)
            equal(d.lines, ["A"], "after edits")
            d.undo(); equal(d.lines, ["A", "b"], "undo delete")
            d.undo(); equal(d.lines, ["a", "b"], "undo replace")
            d.redo(); equal(d.lines, ["A", "b"], "redo replace")
            d.insert(0, "new")
            raises(IndexError, d.redo)
            d.undo(); d.undo(); d.undo()
            equal(d.lines, ["a"], "back to the start")
            raises(IndexError, d.undo)

        def test_random_against_snapshots(m):
            rng = random.Random(2)
            d = m.Document([])
            history = [[]]
            for _ in range(300):
                cur = history[-1]
                r = rng.random()
                if r < 0.25 and len(history) > 1:
                    d.undo(); history.pop()
                else:
                    new = list(cur)
                    if cur and r < 0.5:
                        i = rng.randrange(len(cur)); d.delete(i); del new[i]
                    elif cur and r < 0.7:
                        i = rng.randrange(len(cur)); w = rand_words(1, rng.randint(0, 999))[0]
                        d.replace(i, w); new[i] = w
                    else:
                        i = rng.randint(0, len(cur)); w = rand_words(1, rng.randint(0, 999))[0]
                        d.insert(i, w); new.insert(i, w)
                    history.append(new)
                equal(d.lines, history[-1], "document state")
        ''',
        alts={
            "inverse operations": ('''
                class Document:
                    def __init__(self, lines=None):
                        self._lines = list(lines or [])
                        self._undo, self._redo = [], []

                    @property
                    def lines(self):
                        return list(self._lines)

                    def _apply(self, op):
                        kind, i, text = op
                        if kind == "insert":
                            self._lines.insert(i, text)
                            return ("delete", i, None)
                        if kind == "delete":
                            old = self._lines.pop(i)
                            return ("insert", i, old)
                        old, self._lines[i] = self._lines[i], text
                        return ("replace", i, old)

                    def _edit(self, op):
                        self._undo.append(self._apply(op))
                        self._redo.clear()

                    def insert(self, i, text): self._edit(("insert", i, text))
                    def delete(self, i): self._edit(("delete", i, None))
                    def replace(self, i, text): self._edit(("replace", i, text))

                    def undo(self):
                        if not self._undo:
                            raise IndexError("nothing to undo")
                        self._redo.append(self._apply(self._undo.pop()))

                    def redo(self):
                        if not self._redo:
                            raise IndexError("nothing to redo")
                        self._undo.append(self._apply(self._redo.pop()))
            ''', "Each operation returns its own inverse, so undo and redo are the same code. Memory per edit "
                 "is O(1), versus O(n) for a full snapshot (the Command pattern)."),
            "snapshots": ('''
                class Document:
                    def __init__(self, lines=None):
                        self._lines = list(lines or [])
                        self._past, self._future = [], []

                    @property
                    def lines(self):
                        return list(self._lines)

                    def _edit(self, change):
                        self._past.append(list(self._lines))
                        self._future.clear()
                        change(self._lines)

                    def insert(self, i, text): self._edit(lambda ls: ls.insert(i, text))
                    def delete(self, i): self._edit(lambda ls: ls.pop(i))
                    def replace(self, i, text): self._edit(lambda ls: ls.__setitem__(i, text))

                    def undo(self):
                        if not self._past:
                            raise IndexError("nothing to undo")
                        self._future.append(self._lines)
                        self._lines = self._past.pop()

                    def redo(self):
                        if not self._future:
                            raise IndexError("nothing to redo")
                        self._past.append(self._lines)
                        self._lines = self._future.pop()
            ''', "Much simpler and obviously correct, but each edit copies the whole document: O(n) memory "
                 "per edit. Fine for small documents (and the strings themselves are shared, not copied)."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="a = [1, 2]\nb = a\na = a + [3]\nprint(b)", why="a + [3] builds a new list; b still refers to the old one."),
    dict(kind="predict", code="a = [1, 2]\nb = a\na += [3]\nprint(b)", why="list += mutates in place; b is the same list."),
    dict(kind="predict", code="def f(xs):\n    xs = xs + [0]\n    return len(xs)\nys = [1]\nprint(f(ys), ys)"),
    dict(kind="predict", code="import copy\na = [[1], [2]]\nb = copy.copy(a)\nb[0].append(9)\nb.append([3])\nprint(a)",
         why="Shallow copy: new outer list, shared inner lists."),
    dict(kind="predict", code="t = ([1], 2)\nt[0].append(3)\nprint(t)", why="The tuple can't change which objects it holds, but the list inside can change."),
    dict(kind="recall", q="Which comparison should you use to test for None?", a=["is", "is None", "x is None"]),
    dict(kind="recall", q="Which function copies nested structures fully?", a=["copy.deepcopy", "deepcopy"]),
]
