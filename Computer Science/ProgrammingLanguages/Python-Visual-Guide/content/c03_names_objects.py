"""Chapter 3 - Names, objects and memory: assignment binds names to objects, mutability, aliasing,
argument passing, shallow vs deep copies, identity vs equality, lifetime (refcounts, gc), hashing."""
from generator import canvas as C
from content.kit import (L, W, callout, code, flow, go, memory, practice, repl, section, stamp, sub, table,
                         title_block, two_ways)

ORDER = 3
NUM = 3
TITLE = "Names, objects and memory"
SHORT = "Names and memory"
SLUG = "Names-and-memory"
ACCENT = C.GREEN


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def title_page(ch):
    title_block(ch, 3, TITLE, "names are labels on objects, not boxes holding values", ACCENT)
    f = ch.flow(top=190)
    f.p("Most \"weird\" Python behaviour comes from one wrong picture: thinking a variable is a box that "
        "{B:holds} a value. In Python a variable is a {B:name} that {B:refers to} an object living somewhere "
        "else in memory. Assignment never copies anything; it just points a name at an object.", 14, gap=10)
    code(f, """
        a = [1, 2, 3]
        b = a
        b.append(4)
        print(a, a is b, id(a) == id(b))
    """, expect="[1, 2, 3, 4] True True")
    memory(f, [("names (global frame)", ["a", "b"])],
           {"L": dict(t="list", slots=["0", "1", "2", "3"], x=L + 250, row=0, color=C.BLUE),
            **{str(k + 1): dict(t="int", v=str(k + 1), x=L + 215 + k * 56, row=1.4, anchor="top")
               for k in range(4)}},
           [("a", "L"), ("b", "L"), ("L.0", "1"), ("L.1", "2"), ("L.2", "3"), ("L.3", "4")])
    f.p("There's {B:one} list and two names for it. `b.append(4)` changed the list, and `a` sees the change "
        "because `a` is the same list. Every picture in this chapter has this shape: names on the left, "
        "objects on the right, arrows for references.", 14, gap=10)
    callout(f, "idea", "`x = <expression>` means: evaluate the right side to an object, then make the name `x` "
            "refer to it. The name never contains the object.")


def mutability(ch):
    f = flow(ch)
    sec(f, "Mutable vs immutable: the second half of the story")
    f.p("Some objects can change in place ({B:mutable}: list, dict, set, most class instances). Others can "
        "never change ({B:immutable}: int, float, str, tuple, frozenset, bytes). With an immutable object, "
        "\"changing\" a variable always means pointing the name at a {B:new} object:", 13.5, gap=8)
    code(f, """
        x = 10
        y = x
        x += 1          # makes a NEW int 11 and rebinds x
        print(x, y)

        xs = [10]
        ys = xs
        xs += [11]      # list += mutates the SAME list in place
        print(xs, ys)
    """, notes={3: "y still points at 10", 8: "ys sees it"})
    memory(f, [("after x += 1", ["x", "y"]), ("after xs += [11]", ["xs", "ys"])],
           {"a": dict(t="int", v="11", col=0, row=0, color=C.ORANGE), "b": dict(t="int", v="10", col=0, row=1),
            "L": dict(t="list", slots=["0", "1"], col=0, row=2, color=C.BLUE),
            "c": dict(t="int", v="10", x=L + 200, row=3.2, anchor="top"),
            "d": dict(t="int", v="11", x=L + 262, row=3.2, anchor="top")},
           [("x", "a"), ("y", "b"), ("xs", "L"), ("ys", "L"), ("L.0", "c"), ("L.1", "d")], height=200)
    table(f, ["immutable (safe to share)", "mutable (sharing = aliasing)"], [
        ["`int`, `float`, `complex`, `bool`", "`list`"],
        ["`str`, `bytes`", "`dict`, `set`, `bytearray`"],
        ["`tuple` (but its items might be mutable)", "instances of your classes (by default)"],
        ["`frozenset`, `None`", "`array.array`, NumPy arrays"],
    ], widths=[1, 1])
    callout(f, "trap", "`x += 1` and `xs += [1]` look the same but do different things: for a list, `+=` is "
            "`xs.extend(...)` in place; for an int it builds a new object. `xs = xs + [1]` would build a new "
            "list and leave `ys` alone.")


def calls(ch):
    f = flow(ch)
    sec(f, "Passing arguments: the parameter is one more name", room=440)
    f.p("A function call doesn't copy arguments. The parameter becomes another name for the {B:same} object "
        "(\"pass by assignment\"). So a function can {B:mutate} what you pass in, but {B:rebinding} its "
        "parameter does nothing to the caller:", 13.5, gap=8)
    code(f, """
        def add_bonus(scores):
            scores.append(5)        # mutates the caller's list

        def reset(scores):
            scores = []             # rebinds the local name only

        marks = [60, 70]
        add_bonus(marks)
        reset(marks)
        print(marks)
    """, notes={2: "visible outside", 5: "invisible outside"}, expect="[60, 70, 5]")
    memory(f, [("caller frame", ["marks"]), ("reset() frame", ["scores"])],
           {"L": dict(t="list", v="[60, 70, 5]", col=0, row=0, color=C.BLUE),
            "E": dict(t="new list", v="[]", col=0, row=2, color=C.ORANGE)},
           [("marks", "L"), ("scores", "E")], height=150)
    f.p("Inside `reset`, `scores = []` pointed the local name at a new empty list. The caller's list is "
        "untouched, and when `reset` returns, its frame and the empty list disappear.", 13.5, gap=8)
    callout(f, "rule", "A function should either {B:return a new value} or {B:mutate its argument and return "
            "None}, and its name should make clear which (`sorted(xs)` vs `xs.sort()`). Doing both confuses "
            "every caller.")


def copies(ch):
    f = flow(ch)
    sec(f, "Copies: shallow and deep", room=470)
    f.p("When you do want an independent object, copy it explicitly. A {B:shallow} copy makes a new outer "
        "container but reuses the items inside. For nested data that matters:", 13.5, gap=8)
    code(f, """
        import copy

        grid = [[1, 2], [3, 4]]
        shallow = grid.copy()           # same as list(grid) or grid[:]
        deep = copy.deepcopy(grid)

        grid[0].append(99)
        print(shallow)                  # shares the inner lists
        print(deep)                     # fully independent
    """)
    memory(f, [("names", ["grid", "shallow", "deep"])],
           {"G": dict(t="list grid", slots=["0", "1"], col=0, row=0, color=C.BLUE),
            "S": dict(t="list shallow", slots=["0", "1"], col=0, row=1, color=C.BLUE),
            "D": dict(t="list deep", slots=["0", "1"], col=0, row=2, color=C.PURPLE),
            "a": dict(t="list", v="[1, 2, 99]", col=1, row=0, color=C.ORANGE),
            "b": dict(t="list", v="[3, 4]", col=1, row=1, color=C.ORANGE),
            "c": dict(t="list (copy)", v="[1, 2]", col=1, row=2, color=C.PURPLE),
            "d": dict(t="list (copy)", v="[3, 4]", col=1, row=3, color=C.PURPLE)},
           [("grid", "G"), ("shallow", "S"), ("deep", "D"), ("G.0", "a"), ("G.1", "b"), ("S.0", "a"), ("S.1", "b"),
            ("D.0", "c"), ("D.1", "d")], height=195)
    table(f, ["how", "copies", "inner objects"], [
        ["`b = a`", "nothing (alias)", "shared"],
        ["`a.copy()`, `list(a)`, `a[:]`, `dict(d)`, `copy.copy(a)`", "the outer container", "shared"],
        ["`copy.deepcopy(a)`", "everything, recursively", "new (sharing inside is preserved)"],
    ], widths=[3, 1.6, 2])
    go(f, "Predict, then check: m = [[0] * 3] * 3; m[1][1] = 5; print(m). Draw the boxes and arrows first.")


def identity(ch):
    f = flow(ch)
    sec(f, "Identity vs equality: is vs ==", room=430)
    f.p("`==` asks \"same value?\" by calling `__eq__`. `is` asks \"same object?\" by comparing identities "
        "(`id()`, in CPython the memory address). They differ more often than you'd think:", 13.5, gap=8)
    repl(f, """
        >>> a = [1, 2]; b = [1, 2]
        >>> a == b, a is b
        >>> x = 1000; y = int("1000")
        >>> x == y, x is y
        >>> s = None
        >>> s is None
    """)
    callout(f, "trap", "Small ints (−5 to 256) and some strings are cached, so `is` sometimes \"works\" on "
            "them by accident. That's a CPython detail that changes between versions. Use `is` only for "
            "`None` (and other singletons like `True`/`False` or sentinel objects), and `==` for values.")
    sub(f, "Why lists can't be dictionary keys", ACCENT)
    f.p("A dict finds keys by their {B:hash}, computed once when the key is inserted. If a key could change "
        "after insertion, its hash would no longer match and the entry would be lost. So only immutable "
        "(hashable) objects can be keys or set members:", 13.5, gap=8)
    code(f, """
        seen = {(1, 2): "tuple ok", "text": "str ok", frozenset({3}): "frozenset ok"}
        print(len(seen))
        seen[[1, 2]] = "list?"
    """, raises=TypeError)
    code(f, """
        seen[(1, [2])] = "tuple holding a list?"
    """, raises=TypeError, numbers=False)


def lifetime(ch):
    f = flow(ch)
    sec(f, "How long objects live", room=430)
    f.p("CPython keeps a {B:reference count} on every object: how many names, list slots, attributes etc. "
        "point at it. When the count drops to zero the object is freed immediately. `del x` removes a "
        "{B:name}; the object only dies if that was the last reference:", 13.5, gap=8)
    code(f, """
        import sys

        data = [0] * 1000
        alias = data
        print(sys.getrefcount(data) - 1)   # minus the temporary ref from the call itself
        del data
        print(len(alias))                  # still alive: alias refers to it
    """)
    f.p("Reference counting can't free {B:cycles} (two objects pointing at each other), so a separate "
        "garbage collector (`gc`) finds and frees unreachable cycles from time to time:", 13.5, gap=8)
    code(f, """
        import gc

        class Node:
            def __init__(self):
                self.other = None

        a, b = Node(), Node()
        a.other, b.other = b, a       # a cycle
        del a, b                      # unreachable, but refcounts are still 1
        print(gc.collect() >= 2)      # the cycle collector frees them
    """)
    table(f, ["size of...", "on 64-bit CPython", "why"], [
        ["`sys.getsizeof(0)`", "28 bytes", "every int is a full object (type pointer, refcount, digits)"],
        ["`sys.getsizeof([])`", "56 bytes", "header plus room to grow"],
        ["a list of 1,000 ints", "~8 KB of pointers + 28 KB of int objects", "the list holds references, not values"],
        ["an `array.array` of 1,000 ints", "~4 KB", "raw 4-byte values packed together; NumPy does the same (Ch 18)"],
    ], widths=[2, 2.2, 3])
    callout(f, "other", "C has no references by default: `int x = y;` really copies, and you manage memory "
            "yourself. Java works like Python for objects (references) but copies primitives (`int`). Rust "
            "makes ownership explicit: assignment {B:moves} a value unless you borrow it. The passport question "
            "\"what does assignment do?\" has a different answer in each.")


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 3)
    stamp(f, [
        (1, "Every value is an object on the heap; variables, list slots and attributes are references. "
            "Assignment and argument passing copy references, never objects. Freed by reference counting, "
            "plus a cycle collector."),
        (2, "Values have types; names don't. Mutable (list, dict, set, instances) vs immutable (int, str, tuple, "
            "frozenset); only hashable objects can be dict keys."),
    ])
    callout(f, "deep", "Vault notes: {b:5.3} Objects: identity, type, and value · {b:5.4} Names and bindings, "
            "not variable boxes · {b:5.6} References, reachability, and lifetime · {b:5.7} Mutability and "
            "shallow structure · {b:5.8} Equality, ordering, and hashing · {b:8.3} Python passes object "
            "references by assignment · {b:15.12} Reference counting · {b:15.13} Cyclic garbage collection.")


def build(ch):
    title_page(ch)
    mutability(ch)
    calls(ch)
    copies(ch)
    identity(ch)
    lifetime(ch)
    finish(ch)
