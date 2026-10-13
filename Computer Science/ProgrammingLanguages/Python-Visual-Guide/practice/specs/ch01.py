EXERCISES = [
    dict(
        id="1.1", kind="build", title="Top words in a text",
        task="""
        Write `top_words(text, n)` returning the `n` most common words as `(word, count)` tuples,
        most common first, ties in alphabetical order.

        A word is a run of letters (`a-z`, any case) and apostrophes inside words ("don't" is one word);
        compare case-insensitively and return words in lowercase.
        """,
        stub='''
        def top_words(text, n):
            ...
        ''',
        tests='''
        import random, re

        def reference(text, n):
            counts = {}
            for w in re.findall(r"[a-z]+(?:'[a-z]+)*", text.lower()):
                counts[w] = counts.get(w, 0) + 1
            return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

        def test_small(m):
            equal(m.top_words("The cat and the hat. THE end!", 2), [("the", 3), ("and", 1)], "small text")
            equal(m.top_words("Don't stop; don't.", 5), [("don't", 2), ("stop", 1)], "apostrophes")
            equal(m.top_words("", 3), [], "empty text")

        def test_random_texts(m):
            rng = random.Random(7)
            vocab = rand_words(30)
            for _ in range(100):
                words = [rng.choice(vocab) for _ in range(rng.randint(0, 80))]
                seps = [rng.choice([" ", ", ", ". ", "\\n", " -- ", "! "]) for _ in words]
                text = "".join(w.upper() if rng.random() < .2 else w for pair in zip(words, seps) for w in pair)
                n = rng.randint(1, 10)
                equal([tuple(x) for x in m.top_words(text, n)], reference(text, n), f"text {text[:40]!r}...")
        ''',
        alts={
            "Counter + regex": ('''
                import re
                from collections import Counter

                def top_words(text, n):
                    words = re.findall(r"[a-z]+(?:'[a-z]+)*", text.lower())
                    return sorted(Counter(words).items(), key=lambda kv: (-kv[1], kv[0]))[:n]
            ''', "Counter.most_common(n) would break ties by first appearance, not alphabetically, so we "
                 "sort ourselves with a (-count, word) key."),
            "plain dict": ('''
                def top_words(text, n):
                    counts = {}
                    word = ""
                    for ch in text.lower() + " ":
                        if ch.isalpha() and ch.isascii() or (ch == "'" and word):
                            word += ch
                        else:
                            word = word.strip("'")
                            if word:
                                counts[word] = counts.get(word, 0) + 1
                            word = ""
                    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
            ''', "A hand-written tokenizer: more code and more edge cases (trailing apostrophes), which is "
                 "exactly what regular expressions (Ch 9) save you from."),
        },
    ),
    dict(
        id="1.2", kind="build", title="Run-length encoding",
        task="""
        Write `encode(s)` that turns runs of the same character into character + count:
        `"aaabccdddd"` → `"a3b1c2d4"`, and `decode(code)` that reverses it. Counts can be more
        than one digit (`"x" * 12` → `"x12"`). Input strings contain letters only.
        """,
        stub='''
        def encode(s):
            ...

        def decode(code):
            ...
        ''',
        tests='''
        import random

        def test_examples(m):
            equal(m.encode("aaabccdddd"), "a3b1c2d4", "encode")
            equal(m.encode("x" * 12), "x12", "long run")
            equal(m.encode(""), "", "empty")
            equal(m.decode("a3b1c2d4"), "aaabccdddd", "decode")

        def test_round_trip(m):
            rng = random.Random(2)
            for _ in range(300):
                s = "".join(rng.choice("abZ") * rng.randint(1, 15) for _ in range(rng.randint(0, 8)))
                equal(m.decode(m.encode(s)), s, f"decode(encode({s!r}))")
        ''',
        alts={
            "groupby": ('''
                import re
                from itertools import groupby

                def encode(s):
                    return "".join(f"{ch}{len(list(run))}" for ch, run in groupby(s))

                def decode(code):
                    return "".join(ch * int(n) for ch, n in re.findall(r"(\\D)(\\d+)", code))
            ''', "itertools.groupby groups consecutive equal items: exactly a 'run'. Ch 10 covers itertools."),
            "index loop": ('''
                def encode(s):
                    out, i = [], 0
                    while i < len(s):
                        j = i
                        while j < len(s) and s[j] == s[i]:
                            j += 1
                        out.append(f"{s[i]}{j - i}")
                        i = j
                    return "".join(out)

                def decode(code):
                    out, i = [], 0
                    while i < len(code):
                        ch, i = code[i], i + 1
                        j = i
                        while j < len(code) and code[j].isdigit():
                            j += 1
                        out.append(ch * int(code[i:j]))
                        i = j
                    return "".join(out)
            ''', "Two-pointer scanning: verbose but language-neutral; this is how you'd write it in C."),
        },
    ),
    dict(
        id="1.3", kind="build", title="Group anagrams",
        task="""
        Write `group_anagrams(words)` returning groups of words that are anagrams of each other.
        Each group is sorted alphabetically, and the list of groups is sorted by its first word.
        Words that have no anagram partner form a group of one.

        `group_anagrams(["tea", "eat", "bat", "ate", "tab", "cat"])`
        → `[["ate", "eat", "tea"], ["bat", "tab"], ["cat"]]`
        """,
        stub='''
        def group_anagrams(words):
            ...
        ''',
        tests='''
        import random

        def reference(words):
            groups = {}
            for w in words:
                groups.setdefault("".join(sorted(w)), []).append(w)
            return sorted(sorted(g) for g in groups.values())

        def test_example(m):
            equal(m.group_anagrams(["tea", "eat", "bat", "ate", "tab", "cat"]),
                  [["ate", "eat", "tea"], ["bat", "tab"], ["cat"]], "example")
            equal(m.group_anagrams([]), [], "no words")

        def test_random(m):
            rng = random.Random(3)
            for _ in range(100):
                base = rand_words(6, seed=rng.randint(0, 999))
                words = list({"".join(rng.sample(w, len(w))) for w in base for _ in range(3)})
                rng.shuffle(words)
                equal(m.group_anagrams(words), reference(words), "random words")
        ''',
        alts={
            "sorted-letters key": ('''
                from collections import defaultdict

                def group_anagrams(words):
                    groups = defaultdict(list)
                    for w in words:
                        groups["".join(sorted(w))].append(w)
                    return sorted(sorted(g) for g in groups.values())
            ''', "Anagrams share the same sorted letters, so that's the dict key. O(n·k log k)."),
            "letter-count key": ('''
                from collections import Counter

                def group_anagrams(words):
                    groups = {}
                    for w in words:
                        key = frozenset(Counter(w).items())
                        groups.setdefault(key, []).append(w)
                    return sorted(sorted(g) for g in groups.values())
            ''', "A frozenset of (letter, count) pairs is hashable, so it can be a key; avoids sorting each "
                 "word (O(n·k)), though with bigger constants."),
        },
    ),
    dict(
        id="1.4", kind="fix", title="The grid that changes itself",
        task="""
        `transpose(matrix)` should return a new matrix with rows and columns swapped:
        `[[1, 2, 3], [4, 5, 6]]` → `[[1, 4], [2, 5], [3, 6]]`. It returns nonsense. Find out why
        (draw the lists as boxes and arrows), then fix it. The input must not be changed.
        """,
        stub='''
        def transpose(matrix):
            if not matrix:
                return []
            rows, cols = len(matrix), len(matrix[0])
            out = [[None] * rows] * cols
            for r in range(rows):
                for c in range(cols):
                    out[c][r] = matrix[r][c]
            return out
        ''',
        tests='''
        import random, copy

        def test_examples(m):
            equal(m.transpose([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]], "2x3")
            equal(m.transpose([[7]]), [[7]], "1x1")
            equal(m.transpose([]), [], "empty")

        def test_random_and_independent(m):
            rng = random.Random(1)
            for _ in range(100):
                r, c = rng.randint(1, 6), rng.randint(1, 6)
                mat = [[rng.randint(0, 9) for _ in range(c)] for _ in range(r)]
                before = copy.deepcopy(mat)
                t = m.transpose(mat)
                equal(t, [list(col) for col in zip(*mat)], f"transpose of {mat}")
                equal(mat, before, "input unchanged")
                if len(t) > 1:
                    check(t[0] is not t[1], "rows of the result must be separate lists")
        ''',
        alts={
            "comprehension per row": ('''
                def transpose(matrix):
                    if not matrix:
                        return []
                    rows, cols = len(matrix), len(matrix[0])
                    out = [[None] * rows for _ in range(cols)]
                    for r in range(rows):
                        for c in range(cols):
                            out[c][r] = matrix[r][c]
                    return out
            ''', "The minimal fix: the comprehension creates a new inner list on every iteration, instead of "
                 "one list repeated cols times."),
            "zip(*matrix)": ('''
                def transpose(matrix):
                    return [list(col) for col in zip(*matrix)]
            ''', "zip(*rows) pairs up the first items, the second items, ...: that's a transpose."),
        },
    ),
    dict(
        id="1.5", kind="build", title="A command parser with match",
        task="""
        Write `parse(line)` for a text adventure, using `match` on `line.split()`. Return:

        - `"go north"` (or south/east/west) → `("go", "north")`; also the shortcuts `"n"`, `"s"`, `"e"`, `"w"`
        - `"take red key"` → `("take", "red key")` (everything after `take`; at least one word)
        - `"drop X"` → `("drop", "X")` likewise
        - `"inventory"` or `"i"` → `("inventory",)`
        - `"quit"` → `("quit",)`
        - anything else, including `""` and `"go up"` → `("unknown", line)`

        Matching is case-insensitive (lowercase the line first) and ignores extra spaces.
        """,
        stub='''
        def parse(line):
            ...
        ''',
        tests='''
        def test_moves(m):
            for d in ["north", "south", "east", "west"]:
                equal(m.parse(f"go {d}"), ("go", d), f"go {d}")
                equal(m.parse(d[0]), ("go", d), f"shortcut {d[0]}")
            equal(m.parse("  GO   North "), ("go", "north"), "case and spaces")

        def test_items(m):
            equal(m.parse("take red key"), ("take", "red key"), "take")
            equal(m.parse("drop lamp"), ("drop", "lamp"), "drop")
            equal(m.parse("take"), ("unknown", "take"), "take with nothing")

        def test_other(m):
            equal(m.parse("i"), ("inventory",), "i")
            equal(m.parse("Inventory"), ("inventory",), "inventory")
            equal(m.parse("quit"), ("quit",), "quit")
            for junk in ["", "go up", "dance", "go north now"]:
                equal(m.parse(junk), ("unknown", junk), f"{junk!r}")

        def test_uses_match(m):
            check(any(type(n).__name__ == "Match" for n in __import__("ast").walk(source_tree(m))),
                  "this one is practice for the match statement")
        ''',
        alts={
            "match with patterns": ('''
                DIRS = {"n": "north", "s": "south", "e": "east", "w": "west"}

                def parse(line):
                    match line.lower().split():
                        case ["go", ("north" | "south" | "east" | "west") as d]:
                            return ("go", d)
                        case [("n" | "s" | "e" | "w") as k]:
                            return ("go", DIRS[k])
                        case [("take" | "drop") as verb, *item] if item:
                            return (verb, " ".join(item))
                        case ["inventory" | "i"]:
                            return ("inventory",)
                        case ["quit"]:
                            return ("quit",)
                        case _:
                            return ("unknown", line)
            ''', "Or-patterns with `as`, a star pattern for the rest, and a guard (`if item`) for 'at least one'."),
        },
    ),
    dict(
        id="1.6", kind="project", title="Mini-project: bank accounts with rules",
        task="""
        Write a class `Account(owner, balance=0)`:

        - `deposit(amount)` and `withdraw(amount)`: amounts must be positive numbers, otherwise
          `ValueError`; withdrawing more than the balance raises `ValueError` and changes nothing.
        - `balance` is readable (`acct.balance`) but setting it directly raises `AttributeError`
          (use a `@property` with no setter).
        - `history` is a list of `("deposit", amount)` / `("withdraw", amount)` tuples, oldest first;
          a failed operation adds nothing.
        - `repr(acct)` → `Account('Ana', 120)`.
        - A function `transfer(src, dst, amount)` moves money; if it fails, **neither** account changes.
        """,
        stub='''
        class Account:
            def __init__(self, owner, balance=0):
                ...

        def transfer(src, dst, amount):
            ...
        ''',
        tests='''
        import random

        def test_basics(m):
            a = m.Account("Ana", 100)
            a.deposit(20)
            a.withdraw(50)
            equal(a.balance, 70, "balance")
            equal(a.history, [("deposit", 20), ("withdraw", 50)], "history")
            equal(repr(a), "Account('Ana', 70)", "repr")

        def test_rules(m):
            a = m.Account("Ben")
            for bad in [0, -5]:
                raises(ValueError, a.deposit, bad)
                raises(ValueError, a.withdraw, bad)
            raises(ValueError, a.withdraw, 1)
            equal((a.balance, a.history), (0, []), "nothing changed after failures")
            raises(AttributeError, setattr, a, "balance", 10**6)

        def test_transfer_random(m):
            rng = random.Random(4)
            accts = [m.Account(n, rng.randint(0, 100)) for n in "ABCD"]
            total = sum(a.balance for a in accts)
            for _ in range(300):
                s, d = rng.sample(accts, 2)
                amt = rng.randint(-10, 120)
                before = (s.balance, d.balance)
                try:
                    m.transfer(s, d, amt)
                    equal((s.balance, d.balance), (before[0] - amt, before[1] + amt), "after transfer")
                except ValueError:
                    equal((s.balance, d.balance), before, "failed transfer must change nothing")
                equal(sum(a.balance for a in accts), total, "money is never created or lost")
        ''',
        alts={
            "property + validate first": ('''
                class Account:
                    def __init__(self, owner, balance=0):
                        self.owner = owner
                        self._balance = balance
                        self.history = []

                    @property
                    def balance(self):
                        return self._balance

                    @staticmethod
                    def _check(amount):
                        if not isinstance(amount, (int, float)) or amount <= 0:
                            raise ValueError(f"amount must be positive, got {amount!r}")

                    def deposit(self, amount):
                        self._check(amount)
                        self._balance += amount
                        self.history.append(("deposit", amount))

                    def withdraw(self, amount):
                        self._check(amount)
                        if amount > self._balance:
                            raise ValueError("insufficient funds")
                        self._balance -= amount
                        self.history.append(("withdraw", amount))

                    def __repr__(self):
                        return f"Account({self.owner!r}, {self._balance})"

                def transfer(src, dst, amount):
                    src.withdraw(amount)
                    dst.deposit(amount)
            ''', "transfer is safe because withdraw validates everything that could make deposit fail. "
                 "If deposit could fail for other reasons, you'd need to undo the withdrawal (Ch 6, 12)."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="print(-7 // 2, -7 % 2)", why="// floors toward minus infinity; % takes the sign of the divisor."),
    dict(kind="predict", code="print(round(0.5), round(1.5), round(2.5))", why="Banker's rounding: ties go to even."),
    dict(kind="predict", code="t = (5)\nprint(type(t).__name__)", why="Brackets don't make a tuple; commas do."),
    dict(kind="predict", code="x = [[]] * 3\nx[0].append(1)\nprint(x)", why="Three references to one list."),
    dict(kind="predict", code="for i in range(3):\n    pass\nelse:\n    print('else', i)",
         why="No break happened, so else runs; i keeps its last value."),
    dict(kind="predict", code="print(sorted('Banana'))", why="Uppercase sorts before lowercase (code points)."),
    dict(kind="recall", q="Which method returns a dict value or a default instead of raising KeyError?",
         a=["get", ".get", "dict.get", "d.get"]),
    dict(kind="recall", q="What is the empty-set literal? (careful)", a=["set()"]),
]
