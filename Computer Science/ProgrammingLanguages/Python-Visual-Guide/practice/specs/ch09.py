EXERCISES = [
    dict(
        id="9.1", kind="build", title="URL slugs from any title",
        task="""
        Write `slugify(title)` that turns a title into a URL-safe slug:

        - accents removed (`"Zoë"` → `"zoe"`), lowercase
        - every run of characters that aren't ASCII letters or digits becomes a single `-`
        - no leading or trailing `-`

        `slugify("  Ångström & Zoë's 2nd Book!  ")` → `"angstrom-zoe-s-2nd-book"`.
        """,
        stub='''
        def slugify(title):
            return title.lower().replace(" ", "-")
        ''',
        tests='''
        def test_examples(m):
            equal(m.slugify("  Ångström & Zoë's 2nd Book!  "), "angstrom-zoe-s-2nd-book", "example")
            equal(m.slugify("Dune"), "dune", "simple")
            equal(m.slugify("--Hello,   World--"), "hello-world", "collapse and trim")
            equal(m.slugify("!!!"), "", "nothing left")
            equal(m.slugify("Crème Brûlée 101"), "creme-brulee-101", "accents")

        def test_properties(m):
            import re
            for w in rand_words(200, 9):
                s = m.slugify(w + " " + w.upper() + "!?")
                check(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*|", s) is not None, f"bad slug {s!r}")
        ''',
        alts={
            "normalize + re.sub": ('''
                import re, unicodedata

                def slugify(title):
                    ascii_text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
                    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
            ''', "NFKD splits é into e + combining accent; encoding to ASCII with 'ignore' drops the accent "
                 "(and any other non-ASCII character, like 李, entirely)."),
            "no regex": ('''
                import unicodedata

                def slugify(title):
                    out, dash = [], False
                    for c in unicodedata.normalize("NFKD", title.lower()):
                        if c.isascii() and c.isalnum():
                            if dash and out:
                                out.append("-")
                            out.append(c)
                            dash = False
                        elif not unicodedata.combining(c):
                            dash = True
                    return "".join(out)
            ''', "A small state machine: remember 'a separator is pending' and only emit it before the next "
                 "letter, so leading/trailing dashes never appear."),
        },
    ),
    dict(
        id="9.2", kind="build", title="Parse a log line with named groups",
        task="""
        Lines look like `2026-09-28 14:03:11 WARN loans: member=ana book=Dune days_over=3`
        (date, time, level in capitals, an area name followed by `:`, then zero or more `key=value`
        pairs with no spaces inside keys or values).

        Write `parse(line)` returning `{"date": ..., "time": ..., "level": ..., "area": ..., "fields": {...}}`,
        or `None` if the line doesn't have that shape. Values stay strings.
        """,
        stub='''
        def parse(line):
            parts = line.split()
            return {"date": parts[0], "time": parts[1], "level": parts[2], "area": parts[3], "fields": {}}
        ''',
        tests='''
        def test_good(m):
            got = m.parse("2026-09-28 14:03:11 WARN loans: member=ana book=Dune days_over=3")
            equal(got, {"date": "2026-09-28", "time": "14:03:11", "level": "WARN", "area": "loans",
                        "fields": {"member": "ana", "book": "Dune", "days_over": "3"}}, "parsed")
            equal(m.parse("2026-01-01 00:00:00 INFO boot:")["fields"], {}, "no fields")

        def test_bad(m):
            for bad in ["", "hello world", "2026-09-28 14:03 WARN loans: a=b", "2026-09-28 14:03:11 warn loans: a=b",
                        "2026-09-28 14:03:11 WARN loans a=b", "2026-09-28 14:03:11 WARN loans: a=b junk"]:
                equal(m.parse(bad), None, f"parse({bad!r})")
        ''',
        alts={
            "fullmatch + findall": ('''
                import re

                LINE = re.compile(r"(?P<date>\\d{4}-\\d{2}-\\d{2}) (?P<time>\\d{2}:\\d{2}:\\d{2}) "
                                  r"(?P<level>[A-Z]+) (?P<area>\\w+):(?P<rest>(?: \\S+=\\S+)*)")

                def parse(line):
                    m = LINE.fullmatch(line)
                    if not m:
                        return None
                    out = m.groupdict()
                    out["fields"] = dict(re.findall(r"(\\S+?)=(\\S+)", out.pop("rest")))
                    return out
            ''', "fullmatch rejects trailing junk; the repeated non-capturing group validates every pair, then "
                 "findall extracts them (a repeated group only remembers its last repetition)."),
        },
    ),
    dict(
        id="9.3", kind="fix", title="The greedy tag stripper",
        task="""
        `strip_tags(html)` should remove every HTML tag (`<...>`) and keep the text between them, then
        collapse runs of whitespace into one space and strip the ends. It currently deletes almost
        everything. Fix the pattern.
        """,
        stub='''
        import re

        def strip_tags(html):
            text = re.sub(r"<.*>", "", html)
            return re.sub(r"\\s+", " ", text).strip()
        ''',
        tests='''
        def test_strip(m):
            equal(m.strip_tags("<b>Dune</b> and <i>Emma</i>"), "Dune and Emma", "inline tags")
            equal(m.strip_tags('<p class="x">One</p>\\n\\n<p>Two <br/> three</p>'), "One Two three", "blocks")
            equal(m.strip_tags("no tags  here "), "no tags here", "plain text")
            equal(m.strip_tags("a < b and c > d"), "a d", "naive: '< b and c >' looks like a tag (that's why real code uses html.parser)")
        ''',
        alts={
            "negated class": ('''
                import re

                def strip_tags(html):
                    text = re.sub(r"<[^>]*>", " ", html)
                    return re.sub(r"\\s+", " ", text).strip()
            ''', "Replacing tags with a space (not '') stops 'Two<br/>three' becoming 'Twothree'."),
            "lazy quantifier": ('''
                import re

                def strip_tags(html):
                    return " ".join(re.sub(r"<.*?>", " ", html, flags=re.S).split())
            ''', "re.S lets . match newlines, for tags split across lines. ' '.join(s.split()) collapses "
                 "whitespace without a second regex."),
        },
    ),
    dict(
        id="9.4", kind="build", title="A text table with format specs",
        task="""
        Write `render(headers, rows)` returning a text table as a single string:

        - each column is as wide as its widest cell (header included)
        - text columns are left-aligned; columns where **every** row value is an `int` or `float` are
          right-aligned, with floats shown to 2 decimal places
        - columns separated by `" | "`, a line of `-` under the header the full table width (`"-+-"` at
          the separators), no trailing spaces on any line
        """,
        stub='''
        def render(headers, rows):
            lines = [" | ".join(headers)]
            for r in rows:
                lines.append(" | ".join(str(v) for v in r))
            return "\\n".join(lines)
        ''',
        tests='''
        def test_example(m):
            got = m.render(["title", "year", "rating"], [["Dune", 1965, 4.25], ["Emma", 1815, 4.0], ["Ubik", 1969, 4.1]])
            want = "\\n".join([
                "title | year | rating",
                "------+------+-------",
                "Dune  | 1965 |   4.25",
                "Emma  | 1815 |   4.00",
                "Ubik  | 1969 |   4.10",
            ])
            equal(got, want, "table")

        def test_widths_and_trailing(m):
            got = m.render(["a", "long header"], [["much longer cell", 1], ["x", 22]])
            lines = got.split("\\n")
            check(all(l == l.rstrip() for l in lines), "no trailing spaces")
            equal(lines[0], "a                | long header", "header padded to the widest cell")
            equal(lines[2], "much longer cell |           1", "numbers right-aligned")
            equal(len(set(len(l) for l in lines[:3])), 1, "header, rule and full rows have equal width")
        ''',
        alts={
            "format specs with nested widths": ('''
                def render(headers, rows):
                    cols = list(zip(*rows)) if rows else [[] for _ in headers]
                    numeric = [bool(c) and all(isinstance(v, (int, float)) for v in c) for c in cols]

                    def cell(v):
                        return f"{v:.2f}" if isinstance(v, float) else str(v)

                    widths = [max([len(h)] + [len(cell(v)) for v in c]) for h, c in zip(headers, cols)]

                    def line(values, is_header=False):
                        parts = []
                        for v, w, num in zip(values, widths, numeric):
                            text = v if is_header else cell(v)
                            parts.append(f"{text:>{w}}" if num and not is_header else f"{text:<{w}}")
                        return " | ".join(parts).rstrip()

                    out = [line(headers, True), "-+-".join("-" * w for w in widths)]
                    out += [line(r) for r in rows]
                    return "\\n".join(out)
            ''', "zip(*rows) transposes rows into columns. {text:>{w}} takes the width from a variable."),
        },
    ),
    dict(
        id="9.5", kind="build", title="Redact personal data",
        task="""
        Write `redact(text)` that hides personal data using `re.sub` with a **function**:

        - emails `user@domain.tld` become the first letter of the user, `***`, then `@domain.tld`
          (`ana.reader@uni.ac.uk` → `a***@uni.ac.uk`)
        - UK mobile numbers, written `07xxx xxxxxx` or `+44 7xxx xxxxxx` (space optional), become
          `07*** ***` followed by the **last 3 digits** (`07700 900123` → `07*** ***123`)

        Everything else is unchanged.
        """,
        stub='''
        def redact(text):
            return text
        ''',
        tests='''
        def test_redact(m):
            src = "Mail ana.reader@uni.ac.uk or b@x.io; call 07700 900123 or +447700900456 (ref 12345678901)."
            want = "Mail a***@uni.ac.uk or b***@x.io; call 07*** ***123 or 07*** ***456 (ref 12345678901)."
            equal(m.redact(src), want, "redacted")
            equal(m.redact("nothing personal"), "nothing personal", "unchanged")
        ''',
        alts={
            "two compiled patterns": ('''
                import re

                EMAIL = re.compile(r"\\b([\\w.+-])[\\w.+-]*@([\\w-]+(?:\\.[\\w-]+)+)")
                PHONE = re.compile(r"(?<!\\d)(?:\\+44 ?|0)7\\d{3} ?\\d{3}(\\d{3})(?!\\d)")

                def redact(text):
                    text = EMAIL.sub(lambda m: f"{m[1]}***@{m[2]}", text)
                    return PHONE.sub(lambda m: f"07*** ***{m[1]}", text)
            ''', "(?<!\\\\d) and (?!\\\\d) are lookarounds: 'not preceded/followed by a digit', so a long "
                 "reference number containing 07... isn't mistaken for a phone number."),
        },
    ),
    dict(
        id="9.6", kind="project", title="Mini-project: a calculator from scratch",
        task="""
        Write `evaluate(text)` for arithmetic with `+ - * /`, parentheses, unary minus, and numbers
        like `3` or `2.5`. Follow normal precedence (`*` `/` before `+` `-`, left to right).

        Do it in two stages, like a real interpreter:

        1. `tokens(text)`: a regex scanner yielding `(kind, value)` pairs, raising `SyntaxError` on an
           unexpected character
        2. a **recursive-descent parser**: one function per precedence level (`expr` handles + and -,
           `term` handles * and /, `factor` handles numbers, unary minus and parentheses)

        `eval()` and `ast` are not allowed. Malformed input like `"2 +"` or `"(1"` raises `SyntaxError`.
        """,
        stub='''
        def evaluate(text):
            raise SyntaxError("not written yet")
        ''',
        tests='''
        import random

        def test_examples(m):
            for src, want in [("1 + 2 * 3", 7), ("(1 + 2) * 3", 9), ("10 / 4", 2.5), ("2 - 3 - 4", -5),
                              ("-3 * -(2 + 1)", 9), ("2.5 * 4", 10), ("8 / 2 / 2", 2)]:
                equal(m.evaluate(src), want, src)

        def test_errors(m):
            for bad in ["2 +", "(1", "1 2", "3 $ 4", ")", ""]:
                raises(SyntaxError, m.evaluate, bad)

        def test_random_against_python(m):
            rng = random.Random(9)
            def gen(d=0):
                if d > 3 or rng.random() < 0.3:
                    return str(rng.randint(1, 9))
                op = rng.choice("+-*")
                return f"({gen(d + 1)} {op} {gen(d + 1)})" if rng.random() < 0.5 else f"{gen(d + 1)} {op} {gen(d + 1)}"
            for _ in range(200):
                e = gen()
                equal(m.evaluate(e), eval(e), e)

        def test_no_eval(m):
            check(not uses_name(m, "eval") and "ast" not in imports(m), "write the parser yourself")
        ''',
        alts={
            "recursive descent": ('''
                import re

                TOKEN = re.compile(r"\\s*(?:(?P<NUM>\\d+(?:\\.\\d+)?)|(?P<OP>[-+*/()])|(?P<BAD>\\S))")

                def tokens(text):
                    for m in TOKEN.finditer(text):
                        if m.lastgroup == "BAD":
                            raise SyntaxError(f"unexpected {m['BAD']!r} at {m.start('BAD')}")
                        if m.lastgroup:
                            yield m.lastgroup, m[m.lastgroup]

                class Parser:
                    def __init__(self, text):
                        self.toks = list(tokens(text)) + [("END", None)]
                        self.i = 0

                    def peek(self):
                        return self.toks[self.i]

                    def take(self, value=None):
                        tok = self.toks[self.i]
                        if value is not None and tok[1] != value:
                            raise SyntaxError(f"expected {value!r}, got {tok[1]!r}")
                        self.i += 1
                        return tok

                    def expr(self):
                        v = self.term()
                        while self.peek()[1] in ("+", "-"):
                            op = self.take()[1]
                            v = v + self.term() if op == "+" else v - self.term()
                        return v

                    def term(self):
                        v = self.factor()
                        while self.peek()[1] in ("*", "/"):
                            op = self.take()[1]
                            v = v * self.factor() if op == "*" else v / self.factor()
                        return v

                    def factor(self):
                        kind, val = self.peek()
                        if val == "-":
                            self.take()
                            return -self.factor()
                        if val == "(":
                            self.take()
                            v = self.expr()
                            self.take(")")
                            return v
                        if kind == "NUM":
                            self.take()
                            return float(val) if "." in val else int(val)
                        raise SyntaxError(f"unexpected {val!r}")

                def evaluate(text):
                    p = Parser(text)
                    v = p.expr()
                    if p.peek()[0] != "END":
                        raise SyntaxError(f"unexpected {p.peek()[1]!r}")
                    return v
            ''', "Each grammar rule becomes one method, and precedence falls out of which method calls which. "
                 "This is how CPython's own parser is structured (a PEG parser, generated from a grammar)."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="import re\nprint(re.findall(r'\\d+', 'a1b22c333'))"),
    dict(kind="predict", code="import re\nprint(re.findall(r'(\\w)(\\d)', 'a1 b2 cc'))"),
    dict(kind="predict", code="import re\nprint(re.sub(r'a+', '-', 'caaandy aa'))"),
    dict(kind="predict", code="import re\nprint(bool(re.match(r'\\d+', 'x123')), bool(re.search(r'\\d+', 'x123')))"),
    dict(kind="predict", code="print(f'[{3.14159:7.2f}] [{\"ab\":>4}] [{1234567:,}]')"),
    dict(kind="predict", code="import re\nprint(re.findall(r'<.+?>', '<a><b>'), re.findall(r'<.+>', '<a><b>'))"),
    dict(kind="recall", q="Which string method should you use for case-insensitive comparison of Unicode text?", a=["casefold", "str.casefold", "casefold()"]),
    dict(kind="recall", q="Which re function requires the entire string to match the pattern?", a=["fullmatch", "re.fullmatch"]),
]
