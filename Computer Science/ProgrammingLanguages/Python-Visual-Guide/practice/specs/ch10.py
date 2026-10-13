EXERCISES = [
    dict(
        id="10.1", kind="build", title="The k most frequent words",
        task="""
        Write `top_words(text, k)` returning the `k` most frequent words as `(word, count)` pairs,
        most frequent first, **ties broken alphabetically**. Words are runs of letters (and apostrophes),
        compared case-insensitively and returned lowercase.
        """,
        stub='''
        def top_words(text, k):
            words = text.lower().split()
            return [(w, words.count(w)) for w in words][:k]
        ''',
        tests='''
        import random, re
        from collections import Counter

        def test_example(m):
            equal(m.top_words("The cat; the CAT. A dog, the end!", 2), [("the", 3), ("cat", 2)], "top 2")
            equal(m.top_words("b a c b a", 3), [("a", 2), ("b", 2), ("c", 1)], "ties alphabetical")
            equal(m.top_words("", 3), [], "empty")

        def test_random(m):
            rng = random.Random(10)
            vocab = rand_words(30, 4)
            for _ in range(50):
                text = " ".join(rng.choice(vocab) for _ in range(rng.randint(0, 300)))
                c = Counter(re.findall(r"[a-z']+", text.lower()))
                want = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
                equal(m.top_words(text, 5), want, "top 5")
        ''',
        alts={
            "Counter + sorted": ('''
                import re
                from collections import Counter

                def top_words(text, k):
                    counts = Counter(re.findall(r"[a-z']+", text.lower()))
                    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
            ''', "most_common(k) breaks ties by first appearance, not alphabetically, so sort with a tuple key."),
            "heapq.nsmallest": ('''
                import heapq, re
                from collections import Counter

                def top_words(text, k):
                    counts = Counter(re.findall(r"[a-z']+", text.lower()))
                    return heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))
            ''', "O(n log k) instead of O(n log n): it matters when there are millions of distinct words and k is 10."),
        },
    ),
    dict(
        id="10.2", kind="build", title="Merge sorted streams lazily",
        task="""
        Write a generator `merge(*iterables)` that merges any number of **already sorted** iterables
        into one sorted stream. It must be lazy: the tests pass infinite iterators, so you can't
        read everything first. Equal items may come out in any order.
        """,
        stub='''
        def merge(*iterables):
            return iter(sorted(x for it in iterables for x in it))
        ''',
        tests='''
        import itertools, random

        def test_random(m):
            rng = random.Random(2)
            for _ in range(100):
                lists = [sorted(rng.randint(0, 50) for _ in range(rng.randint(0, 10))) for _ in range(rng.randint(0, 5))]
                equal(list(m.merge(*lists)), sorted(x for l in lists for x in l), "merged")

        def endless(start, step):
            for n, x in enumerate(itertools.count(start, step)):
                if n > 1000:
                    raise AssertionError("merge read far ahead: it must be lazy (inputs are infinite)")
                yield x

        def test_lazy(m):
            evens, odds = endless(0, 2), endless(1, 2)
            equal(list(itertools.islice(m.merge(evens, odds, [5, 5]), 9)), [0, 1, 2, 3, 4, 5, 5, 5, 6], "infinite inputs")
        ''',
        alts={
            "heap of iterators": ('''
                import heapq

                def merge(*iterables):
                    heap = []
                    for i, it in enumerate(map(iter, iterables)):
                        for first in it:
                            heap.append((first, i, it))
                            break
                    heapq.heapify(heap)
                    while heap:
                        value, i, it = heap[0]
                        yield value
                        for nxt in it:
                            heapq.heapreplace(heap, (nxt, i, it))
                            break
                        else:
                            heapq.heappop(heap)
            ''', "The index i breaks ties so Python never compares two iterators. heapreplace pops and pushes "
                 "in one O(log k) step. This is the merge step of external sort, for files bigger than RAM."),
            "heapq.merge": ('''
                import heapq

                def merge(*iterables):
                    yield from heapq.merge(*iterables)
            ''', "The stdlib already has it (and accepts key= and reverse=). Writing it once is how you "
                 "learn when to reach for it."),
        },
    ),
    dict(
        id="10.3", kind="time", title="Pairs that sum to a target, fast",
        task="""
        Write `pair_count(nums, target)`: the number of index pairs `i < j` with
        `nums[i] + nums[j] == target`. The stub is correct but O(n²); the tests use 100,000 numbers
        and a time limit, so you need an O(n) approach. Hint: walking left to right, how many earlier
        numbers would complete the current one?
        """,
        stub='''
        def pair_count(nums, target):
            n = 0
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    if nums[i] + nums[j] == target:
                        n += 1
            return n
        ''',
        tests='''
        import random, time

        def slow(nums, target):
            return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] + nums[j] == target)

        def test_small_random(m):
            rng = random.Random(1)
            for _ in range(200):
                nums = [rng.randint(-5, 5) for _ in range(rng.randint(0, 25))]
                t = rng.randint(-6, 6)
                equal(m.pair_count(nums, t), slow(nums, t), f"pair_count({nums}, {t})")

        def test_fast(m):
            rng = random.Random(7)
            n = 1000
            while n <= 128_000:
                nums = [rng.randint(-1000, 1000) for _ in range(n)]
                start = time.perf_counter()
                m.pair_count(nums, 17)
                took = time.perf_counter() - start
                check(took < 0.5, f"took {took:.2f}s on {n:,} numbers: needs O(n)")
                n *= 2
        ''',
        alts={
            "Counter of seen values": ('''
                from collections import Counter

                def pair_count(nums, target):
                    seen, pairs = Counter(), 0
                    for x in nums:
                        pairs += seen[target - x]
                        seen[x] += 1
                    return pairs
            ''', "One pass: each number pairs with every earlier number equal to target - x. Trading O(n) "
                 "memory for O(n) time is the most common optimisation there is."),
            "sort + two pointers": ('''
                def pair_count(nums, target):
                    xs = sorted(nums)
                    i, j, pairs = 0, len(xs) - 1, 0
                    while i < j:
                        s = xs[i] + xs[j]
                        if s < target:
                            i += 1
                        elif s > target:
                            j -= 1
                        elif xs[i] == xs[j]:
                            k = j - i + 1
                            pairs += k * (k - 1) // 2
                            break
                        else:
                            a, b = xs[i], xs[j]
                            ca = cb = 0
                            while xs[i] == a:
                                ca += 1; i += 1
                            while xs[j] == b:
                                cb += 1; j -= 1
                            pairs += ca * cb
                    return pairs
            ''', "O(n log n) and O(1) extra memory, but the duplicate handling is fiddly. The Counter version "
                 "is shorter, faster and easier to trust."),
        },
    ),
    dict(
        id="10.4", kind="build", title="Running median with two heaps",
        task="""
        Write a class `RunningMedian` with `add(x)` and `median()`. After each `add`, `median()` returns
        the median of all numbers so far (for an even count, the mean of the two middle values; `median()`
        on an empty object raises `ValueError`). Both operations must be fast: `add` O(log n), `median` O(1).

        Hint: keep the smaller half in a max-heap (store negatives) and the larger half in a min-heap,
        with sizes differing by at most one.
        """,
        stub='''
        class RunningMedian:
            def __init__(self):
                self.xs = []

            def add(self, x):
                self.xs.append(x)

            def median(self):
                xs = sorted(self.xs)
                return xs[len(xs) // 2]
        ''',
        tests='''
        import random, statistics, time

        def test_random(m):
            rng = random.Random(4)
            for _ in range(30):
                rm, seen = m.RunningMedian(), []
                for _ in range(rng.randint(1, 60)):
                    x = rng.randint(-100, 100)
                    rm.add(x); seen.append(x)
                    equal(rm.median(), statistics.median(seen), f"median of {seen}")

        def test_empty_and_speed(m):
            raises(ValueError, m.RunningMedian().median)
            rm = m.RunningMedian()
            rng = random.Random(1)
            start = time.perf_counter()
            for i in range(50_000):
                rm.add(rng.random())
                rm.median()
                if i % 1000 == 0:
                    check(time.perf_counter() - start < 2.0, "50,000 add+median calls should take well under 2 s")
        ''',
        alts={
            "two heaps": ('''
                import heapq

                class RunningMedian:
                    def __init__(self):
                        self.low = []    # max-heap via negatives: the smaller half
                        self.high = []   # min-heap: the larger half

                    def add(self, x):
                        heapq.heappush(self.low, -x)
                        heapq.heappush(self.high, -heapq.heappop(self.low))
                        if len(self.high) > len(self.low):
                            heapq.heappush(self.low, -heapq.heappop(self.high))

                    def median(self):
                        if not self.low:
                            raise ValueError("no numbers yet")
                        if len(self.low) > len(self.high):
                            return -self.low[0]
                        return (-self.low[0] + self.high[0]) / 2
            ''', "Pushing through both heaps keeps every low item <= every high item without any comparisons "
                 "of your own; then rebalance sizes."),
            "bisect.insort": ('''
                import bisect

                class RunningMedian:
                    def __init__(self):
                        self.xs = []

                    def add(self, x):
                        bisect.insort(self.xs, x)

                    def median(self):
                        n = len(self.xs)
                        if not n:
                            raise ValueError("no numbers yet")
                        mid = n // 2
                        return self.xs[mid] if n % 2 else (self.xs[mid - 1] + self.xs[mid]) / 2
            ''', "insort is O(n) per add (shifting), but the shift is a fast C memmove, so for 50,000 items it "
                 "still passes. Big-O predicts growth, not small-n speed: measure."),
        },
    ),
    dict(
        id="10.5", kind="build", title="Binary search questions",
        task="""
        Using `bisect` (or your own binary search) on a **sorted** list `xs`, write:

        - `count_between(xs, lo, hi)`: how many values `v` satisfy `lo <= v <= hi`, in O(log n)
        - `nearest(xs, x)`: the value in `xs` closest to `x` (the smaller one on a tie); `ValueError` if `xs` is empty
        - `first_at_least(xs, x)`: the index of the first value `>= x`, or `len(xs)` if none
        """,
        stub='''
        def count_between(xs, lo, hi):
            return sum(1 for v in xs if lo <= v <= hi)

        def nearest(xs, x):
            return min(xs, key=lambda v: abs(v - x))

        def first_at_least(xs, x):
            for i, v in enumerate(xs):
                if v >= x:
                    return i
            return len(xs)
        ''',
        tests='''
        import random, time

        def test_random(m):
            rng = random.Random(5)
            for _ in range(300):
                xs = sorted(rng.randint(0, 30) for _ in range(rng.randint(1, 20)))
                lo, hi, x = sorted([rng.randint(-2, 32), rng.randint(-2, 32)]) + [rng.randint(-5, 35)]
                equal(m.count_between(xs, lo, hi), sum(lo <= v <= hi for v in xs), "count_between")
                best = min(xs, key=lambda v: (abs(v - x), v))
                equal(m.nearest(xs, x), best, f"nearest({xs}, {x})")
                equal(m.first_at_least(xs, x), next((i for i, v in enumerate(xs) if v >= x), len(xs)), "first_at_least")
            raises(ValueError, m.nearest, [], 3)

        def test_log_time(m):
            xs = list(range(0, 4_000_000, 2))
            start = time.perf_counter()
            for q in range(2000):
                m.count_between(xs, q * 7, q * 7 + 1000)
                m.first_at_least(xs, 3_999_000 - q)
                check(time.perf_counter() - start < 0.5, "2,000 queries on 2 million items must use binary search")
        ''',
        alts={
            "bisect": ('''
                from bisect import bisect_left, bisect_right

                def count_between(xs, lo, hi):
                    return bisect_right(xs, hi) - bisect_left(xs, lo)

                def first_at_least(xs, x):
                    return bisect_left(xs, x)

                def nearest(xs, x):
                    if not xs:
                        raise ValueError("empty list")
                    i = bisect_left(xs, x)
                    candidates = xs[max(0, i - 1):i + 1]
                    return min(candidates, key=lambda v: (abs(v - x), v))
            ''', "The answer to 'nearest' is always one of the two neighbours of the insertion point."),
            "hand-written binary search": ('''
                def first_at_least(xs, x):
                    lo, hi = 0, len(xs)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if xs[mid] < x:
                            lo = mid + 1
                        else:
                            hi = mid
                    return lo

                def count_between(xs, lo, hi):
                    return first_at_least(xs, hi + 1) - first_at_least(xs, lo) if isinstance(hi, int) else \\
                        sum(lo <= v <= hi for v in xs)

                def nearest(xs, x):
                    if not xs:
                        raise ValueError("empty list")
                    i = first_at_least(xs, x)
                    return min(xs[max(0, i - 1):i + 1], key=lambda v: (abs(v - x), v))
            ''', "The half-open [lo, hi) loop with `hi = mid` is the version that never goes off by one. "
                 "(The hi + 1 trick only works for integers; bisect_right handles any type.)"),
        },
    ),
    dict(
        id="10.6", kind="project", title="Mini-project: an LRU cache",
        task="""
        Write a class `LRUCache(capacity)`:

        - `get(key, default=None)`: the value, and marks the key as **most recently used**
        - `put(key, value)`: insert or update (also marks it most recent); if this makes the cache
          exceed `capacity`, evict the **least recently used** key
        - `len(cache)`, `key in cache` (checking does **not** count as a use)
        - attributes `hits` and `misses` counting `get` calls that found / didn't find the key

        All operations O(1). Then compare with `functools.lru_cache`: what can your class do that the
        decorator can't?
        """,
        stub='''
        class LRUCache:
            def __init__(self, capacity):
                self.capacity = capacity
                self.data = {}
        ''',
        tests='''
        import random

        def test_basic(m):
            c = m.LRUCache(2)
            c.put("a", 1); c.put("b", 2)
            equal(c.get("a"), 1, "get a")
            c.put("c", 3)
            check("b" not in c and "a" in c and "c" in c, "b was least recently used")
            equal(c.get("b", "gone"), "gone", "default")
            equal((c.hits, c.misses), (1, 1), "hits and misses")
            c.put("a", 10)
            c.put("d", 4)
            check("c" not in c and c.get("a") == 10, "updating a refreshed it")
            equal(len(c), 2, "len")

        def test_against_model(m):
            rng = random.Random(6)
            for cap in (1, 3, 5):
                c, model = m.LRUCache(cap), []
                for _ in range(500):
                    k = rng.randint(0, 8)
                    if rng.random() < 0.5:
                        c.put(k, k * 10)
                        if k in model:
                            model.remove(k)
                        model.append(k)
                        if len(model) > cap:
                            model.pop(0)
                    else:
                        got = c.get(k)
                        if k in model:
                            model.remove(k); model.append(k)
                            equal(got, k * 10, "value")
                        else:
                            equal(got, None, "missing")
                    equal(sorted(k for k in range(9) if k in c), sorted(model), "contents")
        ''',
        alts={
            "OrderedDict": ('''
                from collections import OrderedDict

                class LRUCache:
                    def __init__(self, capacity):
                        self.capacity = capacity
                        self._data = OrderedDict()
                        self.hits = self.misses = 0

                    def get(self, key, default=None):
                        if key not in self._data:
                            self.misses += 1
                            return default
                        self.hits += 1
                        self._data.move_to_end(key)
                        return self._data[key]

                    def put(self, key, value):
                        self._data[key] = value
                        self._data.move_to_end(key)
                        if len(self._data) > self.capacity:
                            self._data.popitem(last=False)

                    def __len__(self):
                        return len(self._data)

                    def __contains__(self, key):
                        return key in self._data
            ''', "OrderedDict is a dict plus a doubly linked list: move_to_end and popitem(last=False) are O(1). "
                 "Unlike @lru_cache, this cache can be inspected, invalidated per key, and shared."),
            "plain dict (insertion order)": ('''
                class LRUCache:
                    def __init__(self, capacity):
                        self.capacity = capacity
                        self._d = {}
                        self.hits = self.misses = 0

                    def get(self, key, default=None):
                        try:
                            value = self._d.pop(key)
                        except KeyError:
                            self.misses += 1
                            return default
                        self.hits += 1
                        self._d[key] = value
                        return value

                    def put(self, key, value):
                        self._d.pop(key, None)
                        self._d[key] = value
                        if len(self._d) > self.capacity:
                            del self._d[next(iter(self._d))]

                    def __len__(self):
                        return len(self._d)

                    def __contains__(self, key):
                        return key in self._d
            ''', "Since 3.7 dicts keep insertion order, so pop-and-reinsert moves a key to the end and the "
                 "first key is the oldest. Neat, but relies on a subtler guarantee than OrderedDict's API."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="from collections import Counter\nprint(Counter('banana').most_common(2))"),
    dict(kind="predict", code="import heapq\nh = [5, 1, 4]\nheapq.heapify(h)\nheapq.heappush(h, 0)\nprint(h[0], heapq.heappop(h), heapq.heappop(h))"),
    dict(kind="predict", code="import bisect\nxs = [1, 3, 3, 7]\nprint(bisect.bisect_left(xs, 3), bisect.bisect_right(xs, 3), bisect.bisect_left(xs, 4))"),
    dict(kind="predict", code="from itertools import combinations, permutations\nprint(len(list(combinations(range(5), 2))), len(list(permutations(range(5), 2))))"),
    dict(kind="predict", code="from collections import deque\nd = deque([1, 2, 3], maxlen=3)\nd.append(4)\nd.appendleft(0)\nprint(list(d))"),
    dict(kind="predict", code="from collections import defaultdict\nd = defaultdict(int)\nfor ch in 'abca':\n    d[ch] += 1\nprint(d['a'], d['z'], len(d))", why="Reading d['z'] creates the key with int() == 0."),
    dict(kind="recall", q="Which collections type gives O(1) appends and pops at both ends?", a=["deque", "collections.deque"]),
    dict(kind="recall", q="Is heapq a min-heap or a max-heap?", a=["min-heap", "min heap", "min"]),
]
