EXERCISES = [
    dict(
        id="20.1", kind="time", title="Members on both lists, fast",
        task="""
        `common_members(a, b)` returns the items of `a` that also appear in `b`, in `a`'s order, each item
        once. It is correct but O(n·m): every `in` on a list is a hidden loop. Make it O(n + m) so two lists
        of 8,000 member ids take well under 0.05 s. Items are hashable.
        """,
        stub='''
        def common_members(a, b):
            out = []
            for x in a:
                if x in b and x not in out:
                    out.append(x)
            return out
        ''',
        tests='''
        import random
        import time

        def ref(a, b):
            out = []
            for x in a:
                if x in b and x not in out:
                    out.append(x)
            return out

        def test_small(m):
            equal(m.common_members([3, 1, 3, 2, 5], [5, 3, 9, 3]), [3, 5])
            equal(m.common_members([], [1]), [], "empty a")
            equal(m.common_members(["ana", "ben"], []), [], "empty b")
            equal(m.common_members(list("banana"), list("nab")), ["b", "a", "n"], "strings")

        def test_random(m):
            rng = random.Random(20)
            for _ in range(50):
                a = [rng.randint(0, 30) for _ in range(rng.randint(0, 40))]
                b = [rng.randint(0, 30) for _ in range(rng.randint(0, 40))]
                equal(m.common_members(a, b), ref(a, b), f"common_members({a}, {b})")

        def test_fast(m):
            rng = random.Random(1)
            a = [rng.randrange(40_000) for _ in range(8_000)]
            b = [rng.randrange(40_000) for _ in range(8_000)]
            t0 = time.perf_counter()
            got = m.common_members(a, b)
            took = time.perf_counter() - t0
            in_b = set(b)
            equal(got, [x for x in dict.fromkeys(a) if x in in_b], "common members of the big lists")
            check(took < 0.05, f"took {took:.3f} s; budget 0.05 s")
        ''',
        alts={
            "a set for b, a set for seen": ('''
                def common_members(a, b):
                    in_b, seen, out = set(b), set(), []
                    for x in a:
                        if x in in_b and x not in seen:
                            seen.add(x)
                            out.append(x)
                    return out
            ''', "Two sets turn both hidden loops into O(1) average lookups. The list keeps the order; the sets only "
                 "answer 'have I got this?'."),
            "dict.fromkeys keeps first occurrences": ('''
                def common_members(a, b):
                    in_b = set(b)                                  # built once, not once per item
                    return [x for x in dict.fromkeys(a) if x in in_b]
            ''', "dict.fromkeys(a) drops duplicates and keeps first-seen order, because dicts remember insertion "
                 "order. The trap: writing `if x in set(b)` inside the comprehension rebuilds the set every time, "
                 "which is O(n·m) again."),
        },
    ),
    dict(
        id="20.2", kind="build", title="Flatten anything, however deep",
        task="""
        Write `flatten(nested)`: return a new flat list of the non-list items of `nested`, in left-to-right
        order. Only `list` counts as a container (tuples and strings are items). It must not change `nested`,
        and it must work for a list nested 10,000 deep, deeper than Python's recursion limit, so use an
        explicit stack (or a queue) instead of recursion.
        """,
        stub='''
        def flatten(nested):
            out = []
            for item in nested:
                if isinstance(item, list):
                    out.extend(flatten(item))
                else:
                    out.append(item)
            return out
        ''',
        tests='''
        import copy

        def test_basic(m):
            equal(m.flatten([1, [2, [3, [4]], 5], [], [[6]]]), [1, 2, 3, 4, 5, 6])
            equal(m.flatten([]), [], "empty")
            equal(m.flatten(["ab", (1, 2), ["cd", [(3,)]]]), ["ab", (1, 2), "cd", (3,)], "tuples and str are items")

        def test_not_modified(m):
            data = [1, [2, [3]], [[4, 5]]]
            before = copy.deepcopy(data)
            m.flatten(data)
            equal(data, before, "the input after flatten")

        def test_deep(m):
            deep = ["end"]
            for k in range(10_000):
                deep = [k, deep]
            got = m.flatten(deep)
            equal(len(got), 10_001, "items in a 10,000-deep list")
            equal(got[:3] + got[-2:], [9999, 9998, 9997, 0, "end"], "order")
        ''',
        alts={
            "push in reverse, pop from the end": ('''
                def flatten(nested):
                    out, stack = [], list(reversed(nested))
                    while stack:
                        item = stack.pop()
                        if isinstance(item, list):
                            stack.extend(reversed(item))     # so the first child is popped first
                        else:
                            out.append(item)
                    return out
            ''', "A list used as a stack pops from the end, so each box's contents are pushed reversed to come "
                 "out in their original order. The input lists are only read, never changed."),
            "a stack of iterators": ('''
                def flatten(nested):
                    out, stack = [], [iter(nested)]
                    while stack:
                        for item in stack[-1]:
                            if isinstance(item, list):
                                stack.append(iter(item))     # pause this list, start the inner one
                                break
                            out.append(item)
                        else:
                            stack.pop()                      # this list is finished
                    return out
            ''', "Each stack entry remembers where it had got to in its list: exactly what a recursive call's "
                 "frame would remember. for/else runs the else only when the loop wasn't broken, i.e. the list "
                 "is exhausted."),
        },
    ),
    dict(
        id="20.3", kind="fix", title="Binary search, by the invariant",
        task="""
        `first_at_least(xs, target)` should return the index of the first item of the sorted list `xs` that is
        `>= target`, or `len(xs)` if there is none. The stub has two bugs. Fix them by writing down the
        invariant first. Then write `count_between(xs, lo, hi)`: how many items satisfy `lo <= x <= hi`, in
        O(log n), using your own binary search (no `bisect` import, no scanning).
        """,
        stub='''
        def first_at_least(xs, target):
            lo, hi = 0, len(xs) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if xs[mid] <= target:
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        def count_between(xs, lo, hi):
            return sum(1 for x in xs if lo <= x <= hi)
        ''',
        tests='''
        import bisect
        import random
        import time

        def test_examples(m):
            ids = [3, 8, 15, 21, 27, 34, 40, 52, 66, 71]
            for t, want in [(40, 6), (41, 7), (99, 10), (1, 0), (3, 0), (71, 9)]:
                equal(m.first_at_least(ids, t), want, f"first_at_least(ids, {t})")
            equal(m.first_at_least([], 5), 0, "empty list")

        def test_random(m):
            rng = random.Random(3)
            for _ in range(300):
                xs = sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 15)))
                t = rng.randint(-2, 22)
                equal(m.first_at_least(xs, t), bisect.bisect_left(xs, t), f"first_at_least({xs}, {t})")
                a, b = sorted((rng.randint(-2, 22), rng.randint(-2, 22)))
                equal(m.count_between(xs, a, b), sum(a <= x <= b for x in xs), f"count_between({xs}, {a}, {b})")

        def test_fast_and_own(m):
            check("bisect" not in imports(m), "write the binary search yourself (no bisect)")
            xs = list(range(0, 400_000, 2))
            rng = random.Random(4)
            queries = [sorted((rng.randrange(400_000), rng.randrange(400_000))) for _ in range(200)]
            t0 = time.perf_counter()
            got = [m.count_between(xs, a, b) for a, b in queries]
            took = time.perf_counter() - t0
            equal(got, [bisect.bisect_right(xs, b) - bisect.bisect_left(xs, a) for a, b in queries], "counts")
            check(took < 0.05, f"200 queries took {took:.2f} s; budget 0.05 s (that's a scan, not a search)")
        ''',
        alts={
            "half-open range, two searches": ('''
                def first_at_least(xs, target):
                    lo, hi = 0, len(xs)              # the answer is in range(lo, hi + 1)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if xs[mid] < target:
                            lo = mid + 1             # mid and everything left of it are too small
                        else:
                            hi = mid                 # mid could be the answer
                    return lo

                def first_above(xs, target):
                    lo, hi = 0, len(xs)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if xs[mid] <= target:
                            lo = mid + 1
                        else:
                            hi = mid
                    return lo

                def count_between(xs, lo, hi):
                    return max(0, first_above(xs, hi) - first_at_least(xs, lo))
            ''', "Two bugs, both in the invariant: hi must start at len(xs) because 'past the end' is a valid "
                 "answer, and the test must be < (not <=) to find the first item >= target. first_above is the "
                 "same search with <=: bisect_right. Their difference counts the range."),
            "one search with a key function": ('''
                def first_true(n, pred):
                    """Smallest i in range(n + 1) with pred(i) true, for a pred that goes False...False True...True."""
                    lo, hi = 0, n
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if pred(mid):
                            hi = mid
                        else:
                            lo = mid + 1
                    return lo

                def first_at_least(xs, target):
                    return first_true(len(xs), lambda i: xs[i] >= target)

                def count_between(xs, lo, hi):
                    if lo > hi:
                        return 0
                    return first_true(len(xs), lambda i: xs[i] > hi) - first_at_least(xs, lo)
            ''', "Binary search really finds the boundary of a predicate that flips once from False to True. "
                 "Written that way, one function answers every 'first position where...' question, including "
                 "ones that have nothing to do with lists (the smallest capacity that fits, the earliest day...)."),
        },
    ),
    dict(
        id="20.4", kind="build", title="A linked list with a tail",
        task="""
        Write a class `LinkedList` built from your own nodes (no `list`, `deque` or `dict` holding the items):

        - `push_front(v)`, `push_back(v)`: both O(1), so keep a reference to the last node too
        - `pop_front()`: remove and return the first value; `IndexError` if empty
        - `remove(v)`: remove the first node holding `v`; `ValueError` if there is none
        - `reverse()`: reverse in place by relinking nodes (no new nodes)
        - `len(ll)`, `iter(ll)` (values front to back), and `v in ll`

        Watch the tail: after `pop_front`, `remove` or `reverse`, `push_back` must still add at the real end.
        """,
        stub='''
        class Node:
            def __init__(self, value, next=None):
                self.value, self.next = value, next

        class LinkedList:
            def __init__(self):
                self.head = None

            def push_front(self, v):
                self.head = Node(v, self.head)

            def __iter__(self):
                node = self.head
                while node:
                    yield node.value
                    node = node.next
        ''',
        tests='''
        import time
        from collections import deque

        def test_push_pop(m):
            ll = m.LinkedList()
            equal(list(ll), [], "a new list")
            equal(len(ll), 0, "len of a new list")
            ll.push_back(2); ll.push_front(1); ll.push_back(3)
            equal(list(ll), [1, 2, 3])
            equal((len(ll), 2 in ll, 9 in ll), (3, True, False), "len and in")
            equal(ll.pop_front(), 1, "pop_front")
            equal(ll.pop_front(), 2, "pop_front")
            equal(ll.pop_front(), 3, "pop_front")
            raises(IndexError, ll.pop_front)
            ll.push_back("x")
            equal(list(ll), ["x"], "push_back after emptying (the tail must be reset)")

        def test_remove(m):
            ll = m.LinkedList()
            for v in [1, 2, 3, 2]:
                ll.push_back(v)
            ll.remove(2)
            equal(list(ll), [1, 3, 2], "remove the first 2")
            ll.remove(2)
            ll.push_back(4)
            equal(list(ll), [1, 3, 4], "remove the last node, then push_back")
            ll.remove(1)
            equal(list(ll), [3, 4], "remove the head")
            raises(ValueError, ll.remove, 99)
            equal(len(ll), 2, "len after removes")

        def test_reverse(m):
            ll = m.LinkedList()
            for v in "abcd":
                ll.push_back(v)
            ll.reverse()
            equal(list(ll), list("dcba"), "reversed")
            ll.push_back("z")
            equal(list(ll), list("dcbaz"), "push_back after reverse")
            empty = m.LinkedList()
            empty.reverse()
            equal(list(empty), [], "reverse an empty list")

        def test_own_nodes_and_fast(m):
            ll = m.LinkedList()
            t0 = time.perf_counter()
            for i in range(200_000):
                ll.push_back(i)
            took = time.perf_counter() - t0
            check(took < 0.6, f"200,000 push_back took {took:.2f} s: is push_back walking the whole list?")
            state = getattr(ll, "__dict__", {}) or {s: getattr(ll, s, None) for s in getattr(type(ll), "__slots__", ())}
            for name, value in state.items():
                check(not isinstance(value, (list, deque, dict, tuple)), f"attribute {name!r} stores the items in a {type(value).__name__}")
            equal(len(ll), 200_000, "len")
        ''',
        alts={
            "singly linked, head and tail": ('''
                class Node:
                    __slots__ = ("value", "next")
                    def __init__(self, value, next=None):
                        self.value, self.next = value, next

                class LinkedList:
                    def __init__(self):
                        self.head = self.tail = None
                        self.size = 0

                    def push_front(self, v):
                        self.head = Node(v, self.head)
                        if self.tail is None:
                            self.tail = self.head
                        self.size += 1

                    def push_back(self, v):
                        node = Node(v)
                        if self.tail is None:
                            self.head = self.tail = node
                        else:
                            self.tail.next = self.tail = node
                        self.size += 1

                    def pop_front(self):
                        if self.head is None:
                            raise IndexError("pop from an empty list")
                        node, self.head = self.head, self.head.next
                        if self.head is None:
                            self.tail = None
                        self.size -= 1
                        return node.value

                    def remove(self, v):
                        prev, node = None, self.head
                        while node is not None and node.value != v:
                            prev, node = node, node.next
                        if node is None:
                            raise ValueError(f"{v!r} not in list")
                        if prev is None:
                            self.head = node.next
                        else:
                            prev.next = node.next
                        if node is self.tail:
                            self.tail = prev
                        self.size -= 1

                    def reverse(self):
                        prev, node = None, self.head
                        self.tail = node
                        while node is not None:
                            node.next, prev, node = prev, node, node.next
                        self.head = prev

                    def __len__(self):
                        return self.size

                    def __iter__(self):
                        node = self.head
                        while node is not None:
                            yield node.value
                            node = node.next

                    def __contains__(self, v):
                        return any(x == v for x in self)
            ''', "Every method that can change the ends must fix head and tail together; most linked-list bugs "
                 "are a stale tail. `self.tail.next = self.tail = node` assigns left to right: first the old "
                 "tail's next, then the tail. The tuple swap in reverse evaluates the right side first."),
            "doubly linked with a sentinel": ('''
                class Node:
                    __slots__ = ("value", "prev", "next")
                    def __init__(self, value=None):
                        self.value, self.prev, self.next = value, self, self

                class LinkedList:
                    def __init__(self):
                        self.end = Node()            # sentinel: end.next is the first node, end.prev the last
                        self.size = 0

                    def _insert_after(self, where, v):
                        node = Node(v)
                        node.prev, node.next = where, where.next
                        where.next.prev = node
                        where.next = node
                        self.size += 1

                    def _unlink(self, node):
                        node.prev.next, node.next.prev = node.next, node.prev
                        self.size -= 1
                        return node.value

                    def push_front(self, v):
                        self._insert_after(self.end, v)

                    def push_back(self, v):
                        self._insert_after(self.end.prev, v)

                    def pop_front(self):
                        if self.size == 0:
                            raise IndexError("pop from an empty list")
                        return self._unlink(self.end.next)

                    def _nodes(self):
                        node = self.end.next
                        while node is not self.end:
                            yield node
                            node = node.next

                    def remove(self, v):
                        for node in self._nodes():
                            if node.value == v:
                                self._unlink(node)
                                return
                        raise ValueError(f"{v!r} not in list")

                    def reverse(self):
                        node = self.end
                        while True:
                            node.prev, node.next = node.next, node.prev
                            node = node.prev             # the old next
                            if node is self.end:
                                break

                    def __len__(self):
                        return self.size

                    def __iter__(self):
                        return (node.value for node in self._nodes())

                    def __contains__(self, v):
                        return any(x == v for x in self)
            ''', "A sentinel node joins the two ends into a ring, so there is no 'empty' or 'last node' special "
                 "case anywhere: every insert is 'after some node', every removal is 'unlink this node'. "
                 "Reversing is swapping prev and next on every node, sentinel included. This is the layout "
                 "CPython's deque and the LRU cache in 20.7 use."),
        },
    ),
    dict(
        id="20.5", kind="build", title="A binary search tree that survives sorted input",
        task="""
        Write a class `BST` of unique keys:

        - `add(key)` (adding an existing key does nothing), `key in tree`, `len(tree)`
        - `iter(tree)`: keys in sorted order
        - `min()`, `max()`: `ValueError` on an empty tree
        - `height()`: the number of nodes on the longest root-to-leaf path (0 when empty)
        - `between(lo, hi)`: a sorted list of keys with `lo <= key <= hi`, skipping subtrees that can't match

        Adding 2,000 keys in sorted order makes a 2,000-deep tree, deeper than the recursion limit: every
        method must use loops (an explicit stack or queue), not recursion. Don't sort anything: the tree is the
        order.
        """,
        stub='''
        class Node:
            def __init__(self, key):
                self.key, self.left, self.right = key, None, None

        class BST:
            def __init__(self):
                self.root = None

            def add(self, key, node="start"):
                if node == "start":
                    node = self.root
                if node is None:
                    self.root = Node(key)
                elif key < node.key:
                    if node.left is None:
                        node.left = Node(key)
                    else:
                        self.add(key, node.left)
                elif key > node.key:
                    if node.right is None:
                        node.right = Node(key)
                    else:
                        self.add(key, node.right)
        ''',
        tests='''
        import random

        def build(m, keys):
            t = m.BST()
            for k in keys:
                t.add(k)
            return t

        def test_basics(m):
            t = build(m, [50, 30, 70, 20, 40, 60, 80, 35, 30])
            equal(list(t), [20, 30, 35, 40, 50, 60, 70, 80], "in-order")
            equal(len(t), 8, "len (30 was added twice)")
            equal((35 in t, 36 in t), (True, False), "in")
            equal((t.min(), t.max(), t.height()), (20, 80, 4), "min, max, height")
            equal(t.between(33, 60), [35, 40, 50, 60], "between(33, 60)")
            equal(t.between(81, 90), [], "between with no keys")

        def test_empty(m):
            t = m.BST()
            equal((list(t), len(t), t.height(), 5 in t, t.between(0, 9)), ([], 0, 0, False, []), "an empty tree")
            raises(ValueError, t.min)
            raises(ValueError, t.max)

        def test_random(m):
            rng = random.Random(5)
            keys = [rng.randrange(10_000) for _ in range(3_000)]
            t = build(m, keys)
            want = sorted(set(keys))
            equal(list(t), want, "3,000 random keys in order")
            equal(len(t), len(want), "len")
            for _ in range(50):
                a, b = sorted((rng.randrange(10_000), rng.randrange(10_000)))
                equal(t.between(a, b), [k for k in want if a <= k <= b], f"between({a}, {b})")
            check(t.height() < 40, f"height {t.height()} for random keys looks wrong")

        def test_sorted_input(m):
            t = build(m, range(2_000))
            equal(t.height(), 2_000, "height after sorted inserts")
            equal(list(t)[-3:], [1997, 1998, 1999], "in-order on a 2,000-deep tree")
            equal((1999 in t, t.max(), t.between(1995, 5000)), (True, 1999, [1995, 1996, 1997, 1998, 1999]), "deep searches")

        def test_no_sorting(m):
            check(not uses_name(m, "sorted") and not uses_name(m, "sort"), "don't sort: walk the tree in order")
            check("bisect" not in imports(m), "don't use bisect: the tree is the search structure")
        ''',
        alts={
            "loops with an explicit stack": ('''
                class Node:
                    __slots__ = ("key", "left", "right")
                    def __init__(self, key):
                        self.key, self.left, self.right = key, None, None

                class BST:
                    def __init__(self):
                        self.root, self.size = None, 0

                    def add(self, key):
                        if self.root is None:
                            self.root = Node(key)
                            self.size = 1
                            return
                        node = self.root
                        while key != node.key:
                            side = "left" if key < node.key else "right"
                            child = getattr(node, side)
                            if child is None:
                                setattr(node, side, Node(key))
                                self.size += 1
                                return
                            node = child

                    def __contains__(self, key):
                        node = self.root
                        while node is not None and node.key != key:
                            node = node.left if key < node.key else node.right
                        return node is not None

                    def __len__(self):
                        return self.size

                    def __iter__(self):
                        stack, node = [], self.root
                        while stack or node is not None:
                            while node is not None:          # go as far left as possible
                                stack.append(node)
                                node = node.left
                            node = stack.pop()
                            yield node.key
                            node = node.right

                    def _end(self, side):
                        if self.root is None:
                            raise ValueError("empty tree")
                        node = self.root
                        while getattr(node, side) is not None:
                            node = getattr(node, side)
                        return node.key

                    def min(self):
                        return self._end("left")

                    def max(self):
                        return self._end("right")

                    def height(self):
                        best, stack = 0, [(self.root, 1)] if self.root else []
                        while stack:
                            node, depth = stack.pop()
                            best = max(best, depth)
                            stack.extend((c, depth + 1) for c in (node.left, node.right) if c is not None)
                        return best

                    def between(self, lo, hi):
                        out, stack, node = [], [], self.root
                        while stack or node is not None:
                            while node is not None:
                                stack.append(node)
                                node = node.left if node.key > lo else None    # nothing useful further left
                            node = stack.pop()
                            if node.key > hi:
                                break                                          # in-order: all the rest are bigger
                            if node.key >= lo:
                                out.append(node.key)
                            node = node.right
                        return out
            ''', "The in-order iterator is the recursive walk with its frames made explicit: push the left spine, "
                 "pop, yield, then do the same from the right child. between() is the same walk with two cuts: "
                 "don't go left of lo, and stop at the first key above hi."),
            "parent pointers, no stack at all": ('''
                class Node:
                    __slots__ = ("key", "left", "right", "up")
                    def __init__(self, key, up=None):
                        self.key, self.left, self.right, self.up = key, None, None, up

                class BST:
                    def __init__(self):
                        self.root, self.size = None, 0

                    def _find(self, key):
                        """The node holding key, or the node it would hang from (None for an empty tree)."""
                        node, last = self.root, None
                        while node is not None and node.key != key:
                            last, node = node, (node.left if key < node.key else node.right)
                        return node if node is not None else last

                    def add(self, key):
                        spot = self._find(key)
                        if spot is not None and spot.key == key:
                            return
                        node = Node(key, spot)
                        if spot is None:
                            self.root = node
                        elif key < spot.key:
                            spot.left = node
                        else:
                            spot.right = node
                        self.size += 1

                    def __contains__(self, key):
                        spot = self._find(key)
                        return spot is not None and spot.key == key

                    def __len__(self):
                        return self.size

                    @staticmethod
                    def _leftmost(node):
                        while node.left is not None:
                            node = node.left
                        return node

                    @staticmethod
                    def _successor(node):
                        if node.right is not None:
                            return BST._leftmost(node.right)
                        while node.up is not None and node is node.up.right:
                            node = node.up
                        return node.up

                    def _from(self, node):
                        while node is not None:
                            yield node.key
                            node = self._successor(node)

                    def __iter__(self):
                        return self._from(self._leftmost(self.root) if self.root else None)

                    def min(self):
                        if self.root is None:
                            raise ValueError("empty tree")
                        return self._leftmost(self.root).key

                    def max(self):
                        if self.root is None:
                            raise ValueError("empty tree")
                        node = self.root
                        while node.right is not None:
                            node = node.right
                        return node.key

                    def height(self):
                        level, best = [self.root] if self.root else [], 0
                        while level:
                            best += 1
                            level = [c for n in level for c in (n.left, n.right) if c is not None]
                        return best

                    def between(self, lo, hi):
                        node, start = self.root, None
                        while node is not None:                  # the first node with key >= lo
                            if node.key >= lo:
                                start, node = node, node.left
                            else:
                                node = node.right
                        out = []
                        for key in self._from(start):
                            if key > hi:
                                break
                            out.append(key)
                        return out
            ''', "With a pointer to its parent, each node can find its in-order successor: the leftmost node of "
                 "its right subtree, or else the first ancestor it is a left descendant of. No stack, and "
                 "between() is 'find the first key >= lo, then step to successors'. Height goes level by level, "
                 "like the level-order walk."),
        },
    ),
    dict(
        id="20.6", kind="refactor", title="Count inversions in O(n log n)",
        task="""
        An **inversion** is a pair of positions `i < j` with `xs[i] > xs[j]`: it measures how far a list is from
        sorted (0 when sorted, n(n-1)/2 when reversed). It is how ranking systems compare two orderings.
        `count_inversions(xs)` is correct but checks every pair. Rewrite it in O(n log n): 3,000 numbers must
        take under 0.05 s (the pair check needs about ten times that, and 100 times more for 30,000).
        Don't change `xs`.
        """,
        stub='''
        def count_inversions(xs):
            count = 0
            for i in range(len(xs)):
                for j in range(i + 1, len(xs)):
                    if xs[i] > xs[j]:
                        count += 1
            return count
        ''',
        tests='''
        import random
        import time

        def ref(xs):
            return sum(xs[i] > xs[j] for i in range(len(xs)) for j in range(i + 1, len(xs)))

        def test_small(m):
            for xs, want in [([], 0), ([1], 0), ([1, 2, 3], 0), ([3, 2, 1], 3), ([2, 4, 1, 3, 5], 3),
                             ([1, 1, 1], 0), ([2, 1, 2, 1], 3)]:
                equal(m.count_inversions(xs), want, f"count_inversions({xs})")

        def test_random(m):
            rng = random.Random(6)
            for _ in range(60):
                xs = [rng.randint(0, 9) for _ in range(rng.randint(0, 30))]
                before = list(xs)
                equal(m.count_inversions(xs), ref(xs), f"count_inversions({xs})")
                equal(xs, before, "the input list was changed")

        def test_fast(m):
            rng = random.Random(7)
            xs = [rng.randrange(1_000_000) for _ in range(3_000)]
            t0 = time.perf_counter()
            got = m.count_inversions(xs)
            took = time.perf_counter() - t0
            check(abs(got - 3_000 * 2_999 / 4) < 100_000, f"{got} inversions for random data looks wrong")
            check(took < 0.05, f"took {took:.3f} s; budget 0.05 s")
        ''',
        alts={
            "merge sort that counts": ('''
                def count_inversions(xs):
                    def sort(a):
                        if len(a) <= 1:
                            return a, 0
                        mid = len(a) // 2
                        left, x = sort(a[:mid])
                        right, y = sort(a[mid:])
                        out, i, j, count = [], 0, 0, x + y
                        while i < len(left) and j < len(right):
                            if left[i] <= right[j]:
                                out.append(left[i]); i += 1
                            else:
                                out.append(right[j]); j += 1
                                count += len(left) - i       # right[j] jumps over every remaining left item
                        out += left[i:] + right[j:]
                        return out, count

                    return sort(list(xs))[1]
            ''', "When the merge takes an item from the right half, every item still waiting in the left half is "
                 "bigger and was before it: that many inversions at once. Same O(n log n) as merge sort, and the "
                 "recursion depth is only log₂ n."),
            "a Fenwick tree over ranks": ('''
                def count_inversions(xs):
                    rank = {v: r for r, v in enumerate(sorted(set(xs)), 1)}
                    tree = [0] * (len(rank) + 1)
                    count = 0
                    for seen, v in enumerate(xs):
                        r, smaller_or_equal = rank[v], 0
                        i = r
                        while i > 0:                          # how many seen values are <= v
                            smaller_or_equal += tree[i]
                            i -= i & -i
                        count += seen - smaller_or_equal       # the rest of those seen are bigger
                        i = r
                        while i < len(tree):                  # record v
                            tree[i] += 1
                            i += i & -i
                    return count
            ''', "A Fenwick (binary indexed) tree keeps running counts in a flat list, and `i & -i` (the lowest "
                 "set bit) jumps between the slots that cover a prefix: O(log n) per update and query. A tree "
                 "doesn't need nodes and pointers: like the heap in Ch 10, it can live in index arithmetic."),
        },
    ),
    dict(
        id="20.7", kind="project", title="An O(1) LRU cache",
        task="""
        Build `LRUCache(capacity, on_evict=None)`, a cache that forgets the **least recently used** entry when
        it is full:

        - `get(key, default=None)`: the value (this counts as a use), or `default`
        - `put(key, value)`: insert or update (a use); if that makes it exceed `capacity`, evict the least
          recently used entry and call `on_evict(key, value)` if given
        - `len(cache)`, `key in cache` (not a use), and `keys()`: a list from least to most recently used

        Every operation must be O(1): a dict for lookup plus a doubly linked list for the order (or another
        O(1) design). Not allowed: `functools.lru_cache` and `collections.OrderedDict`.
        """,
        stub='''
        class LRUCache:
            def __init__(self, capacity, on_evict=None):
                self.capacity = capacity
                self.on_evict = on_evict
                self.items = []                    # (key, value), least recent first

            def get(self, key, default=None):
                for i, (k, v) in enumerate(self.items):
                    if k == key:
                        self.items.append(self.items.pop(i))
                        return v
                return default

            def put(self, key, value):
                self.items.append((key, value))
                if len(self.items) > self.capacity:
                    self.items.pop(0)
        ''',
        tests='''
        import random
        import time
        from collections import OrderedDict

        class Model:
            def __init__(self, capacity):
                self.capacity, self.d, self.evicted = capacity, OrderedDict(), []

            def get(self, key, default=None):
                if key not in self.d:
                    return default
                self.d.move_to_end(key)
                return self.d[key]

            def put(self, key, value):
                self.d[key] = value
                self.d.move_to_end(key)
                if len(self.d) > self.capacity:
                    self.evicted.append(self.d.popitem(last=False))

        def test_basics(m):
            gone = []
            c = m.LRUCache(2, on_evict=lambda k, v: gone.append((k, v)))
            c.put("a", 1); c.put("b", 2)
            equal(c.get("a"), 1, "get a")
            c.put("c", 3)                                   # b is now least recently used
            equal((gone, "b" in c, len(c)), ([("b", 2)], False, 2), "evict b")
            equal(c.keys(), ["a", "c"], "keys, least recent first")
            c.put("a", 10)                                  # update counts as a use
            equal((c.keys(), c.get("a"), c.get("zz", "none")), (["c", "a"], 10, "none"), "update")
            "c" in c                                        # not a use
            c.put("d", 4)
            equal((gone[-1], c.keys()), (("c", 3), ["a", "d"]), "membership tests are not uses")

        def test_against_model(m):
            rng = random.Random(8)
            for capacity in (1, 3, 7):
                gone = []
                c, ref = m.LRUCache(capacity, on_evict=lambda k, v: gone.append((k, v))), Model(capacity)
                for step in range(2_000):
                    k = rng.randrange(12)
                    if rng.random() < 0.5:
                        equal(c.get(k, -1), ref.get(k, -1), f"get({k}) at step {step}, capacity {capacity}")
                    else:
                        c.put(k, step); ref.put(k, step)
                equal(c.keys(), list(ref.d), f"final keys, capacity {capacity}")
                equal(gone, ref.evicted, f"evictions, capacity {capacity}")

        def test_fast_and_allowed(m):
            check("functools" not in imports(m) and not uses_name(m, "OrderedDict"),
                  "build it yourself: no lru_cache or OrderedDict")
            c = m.LRUCache(50_000)
            t0 = time.perf_counter()
            for i in range(200_000):
                c.put(i % 70_000, i)
                c.get((i * 7) % 70_000)
                if i % 1000 == 0:
                    took = time.perf_counter() - t0
                    check(took < 1.0, f"{2 * i:,} operations took {took:.2f} s: something is O(n)")
            equal(len(c), 50_000, "len when full")
        ''',
        alts={
            "dict + doubly linked list with a sentinel": ('''
                class Node:
                    __slots__ = ("key", "value", "prev", "next")
                    def __init__(self, key=None, value=None):
                        self.key, self.value = key, value
                        self.prev = self.next = self

                class LRUCache:
                    def __init__(self, capacity, on_evict=None):
                        self.capacity, self.on_evict = capacity, on_evict
                        self.map = {}
                        self.end = Node()                 # end.next = least recent, end.prev = most recent

                    def _unlink(self, node):
                        node.prev.next, node.next.prev = node.next, node.prev

                    def _append(self, node):              # as most recent
                        node.prev, node.next = self.end.prev, self.end
                        self.end.prev.next = node
                        self.end.prev = node

                    def get(self, key, default=None):
                        node = self.map.get(key)
                        if node is None:
                            return default
                        self._unlink(node)
                        self._append(node)
                        return node.value

                    def put(self, key, value):
                        node = self.map.get(key)
                        if node is not None:
                            node.value = value
                            self._unlink(node)
                        else:
                            node = self.map[key] = Node(key, value)
                        self._append(node)
                        if len(self.map) > self.capacity:
                            old = self.end.next
                            self._unlink(old)
                            del self.map[old.key]
                            if self.on_evict:
                                self.on_evict(old.key, old.value)

                    def __len__(self):
                        return len(self.map)

                    def __contains__(self, key):
                        return key in self.map

                    def keys(self):
                        out, node = [], self.end.next
                        while node is not self.end:
                            out.append(node.key)
                            node = node.next
                        return out
            ''', "The dict finds the node in O(1); the linked list moves it to the most-recent end in O(1), "
                 "because unlinking a node you already hold needs no search. The node stores its key so that "
                 "evicting from the list can also delete from the dict. This is how OrderedDict is built. "
                 "Tempting shortcut: a plain dict keeps insertion order, so pop-and-reinsert plus next(iter(d)) "
                 "looks O(1), but every deleted slot at the front must be skipped by iter(), and this test catches "
                 "it slowing down."),
            "links stored in dicts, no node objects": ('''
                END = object()                            # sentinel key, can't clash with a real key

                class LRUCache:
                    def __init__(self, capacity, on_evict=None):
                        self.capacity, self.on_evict = capacity, on_evict
                        self.value = {}
                        self.prev, self.next = {END: END}, {END: END}

                    def _unlink(self, key):
                        p, n = self.prev.pop(key), self.next.pop(key)
                        self.next[p], self.prev[n] = n, p

                    def _append(self, key):               # just before END = most recent
                        last = self.prev[END]
                        self.next[last], self.prev[key] = key, last
                        self.next[key], self.prev[END] = END, key

                    def get(self, key, default=None):
                        if key not in self.value:
                            return default
                        self._unlink(key)
                        self._append(key)
                        return self.value[key]

                    def put(self, key, value):
                        if key in self.value:
                            self._unlink(key)
                        self.value[key] = value
                        self._append(key)
                        if len(self.value) > self.capacity:
                            old = self.next[END]
                            self._unlink(old)
                            old_value = self.value.pop(old)
                            if self.on_evict:
                                self.on_evict(old, old_value)

                    def __len__(self):
                        return len(self.value)

                    def __contains__(self, key):
                        return key in self.value

                    def keys(self):
                        out, k = [], self.next[END]
                        while k is not END:
                            out.append(k)
                            k = self.next[k]
                        return out
            ''', "A 'pointer' only has to name the next item: here the keys themselves are the names, and two "
                 "dicts hold the prev and next links. Same O(1) relinking, no Node class. Graphs in Ch 21 are "
                 "stored the same way: a dict from each node to its neighbours."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="import sys\nprint(sys.getrecursionlimit())",
         why="The default limit; sys.setrecursionlimit can raise it, but the C stack can still overflow."),
    dict(kind="predict", code="calls = 0\ndef fib(n):\n    global calls\n    calls += 1\n    return n if n < 2 else fib(n - 1) + fib(n - 2)\nfib(6)\nprint(calls)",
         why="calls(n) = calls(n-1) + calls(n-2) + 1: it grows like fib itself."),
    dict(kind="predict", code="from functools import cache\n@cache\ndef f(n):\n    return n if n < 2 else f(n - 1) + f(n - 2)\nf(30)\nprint(f.cache_info().misses)",
         why="Each n from 0 to 30 is computed once: 31 misses."),
    dict(kind="predict", code='print(sorted([("b", 1), ("a", 1), ("c", 0)], key=lambda p: p[1]))',
         why="Sorting is stable: b and a keep their order."),
    dict(kind="predict", code="import bisect\nxs = [1, 3, 3, 3, 5]\nprint(bisect.bisect_left(xs, 3), bisect.bisect_right(xs, 3))"),
    dict(kind="predict", code="xs = []\nfor i in range(3):\n    xs.insert(0, i)\nprint(xs)"),
    dict(kind="recall", q="What is the Big-O cost of `x in some_list`?", a=["O(n)", "n", "linear"]),
    dict(kind="recall", q="Which BST traversal visits the keys in sorted order?", a=["in-order", "inorder", "in order"]),
    dict(kind="recall", q="Insert 1, 2, ..., 100 into an empty BST in that order. What is its height (nodes on the longest path)?", a=["100"]),
    dict(kind="recall", q="Merge sort's worst-case cost?", a=["O(n log n)", "n log n", "nlogn", "O(nlogn)"]),
]
