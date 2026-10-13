"""Chapter 9 - Text and regular expressions: format specs, Unicode normalisation and casefold, translate,
regex built up token by token with a visual match highlighter, groups, sub with functions, greedy vs lazy,
verbose patterns, a scanner, string.Template and textwrap."""
import re

from generator import canvas as C
from generator import fonts as F
from content.kit import (L, W, callout, code, flow, go, pipe, practice, repl, section, stamp, sub, table,
                         title_block, two_ways)

ORDER = 9
NUM = 9
TITLE = "Text and regular expressions"
SHORT = "Text and regex"
SLUG = "Text-and-regex"
ACCENT = C.TEAL

GROUP_COLS = [C.ORANGE, C.PURPLE, C.GREEN, C.RED, C.BLUE]


def matches(f, pattern, text, flags=0, size=11.5, label=None):
    """Draw `text` in mono with every regex match boxed, and groups underlined in colour."""
    rx = re.compile(pattern, flags)
    while size > 9.4 and len(text) * F.width("M", F.MONO, size) > W - 20:
        size -= 0.2
    cw = F.width("M", F.MONO, size)
    per_line = int((W - 20) / cw)
    lines = [text[i:i + per_line] for i in range(0, len(text), per_line)] or [""]
    found = list(rx.finditer(text))
    groups = rx.groups
    lh = size * 2.6
    h = 22 + len(lines) * lh + 8
    y = f.reserve(h + 12)
    pg = f.pg
    pg.rect(L, y, W, h, "#d5d9df", 0.8, fillcolor="#fbfbfc", r=5)
    pg.text(L + 8, y + 5, f"re.finditer(r'{pattern}', text)" if label is None else label, 9, C.GREY, F.MONO)
    pg.text(L + W - 8, y + 5, f"{len(found)} match{'es' if len(found) != 1 else ''}", 9, ACCENT, F.BOLD,
            align="right")
    for li, ln in enumerate(lines):
        ly = y + 24 + li * lh
        base = li * per_line
        for m in found:
            s, e = max(m.start(), base), min(m.end(), base + len(ln))
            if s < e:
                pg.rect(L + 10 + (s - base) * cw, ly - 2, (e - s) * cw, size + 6, C.TEAL, 1.0,
                        fillcolor=C.LIGHT[C.TEAL], r=3)
            for g in range(1, groups + 1):
                if m.start(g) < 0:
                    continue
                gs, ge = max(m.start(g), base), min(m.end(g), base + len(ln))
                if gs < ge:
                    col = GROUP_COLS[(g - 1) % len(GROUP_COLS)]
                    pg.line(L + 10 + (gs - base) * cw + 1, ly + size + 7, L + 10 + (ge - base) * cw - 1,
                            ly + size + 7, col, 2.2)
        pg.text(L + 10, ly, ln.replace(" ", "\u00a0"), size, C.INK, F.MONO)
    return found


def title_page(ch):
    title_block(ch, 9, TITLE, "describe the shape of the text; the engine finds it", ACCENT)
    f = ch.flow(top=190)
    f.p("String methods (`split`, `strip`, `replace`, `startswith`, `in`) handle fixed text. When what you're "
        "looking for has a {B:shape} rather than a fixed value (\"a date\", \"an email\", \"a word followed by "
        "a number\"), you describe the shape with a {B:regular expression} and the `re` module finds every "
        "piece of text that fits:", 14, gap=10)
    matches(f, r"\d{4}-\d{2}-\d{2}", "Loans: Dune due 2026-10-03, Emma due 2026-11-15 (renewed 2026-10-20).")
    f.p("Each box is one match. In this chapter every pattern is drawn like this, so you can {B:see} what it "
        "matches before trusting it. Capturing groups get coloured underlines:", 13.5, gap=8)
    matches(f, r"(\w+) due (\d{4})-(\d{2})", "Loans: Dune due 2026-10-03, Emma due 2026-11-15.")
    callout(f, "rule", "Always write patterns as raw strings: `r\"\\d+\"`. Without the `r`, Python processes "
            "backslashes first (`\"\\b\"` is a backspace character), and your pattern silently changes.")
    callout(f, "honest", "Regular expressions are powerful and hard to read. If `str` methods can do the job, use "
            "them. Never parse HTML, JSON or a programming language with a regex: use a real parser "
            "(`html.parser`, `json`, `ast`).")


def formatting(ch):
    f = flow(ch)
    sec = lambda t, **kw: section(f, t, ACCENT, **kw)  # noqa: E731
    sec("Formatting: the mini-language after the colon", room=430)
    f.p("Inside an f-string, everything after `:` is a {B:format spec}: `{value:fill align width , .precision "
        "type}`. It's the same mini-language used by `format()` and `str.format`:", 13.5, gap=8)
    code(f, """
        title, price, count, ratio = "Dune", 7.5, 1234567, 0.4567

        print(f"[{title:<10}] [{title:>10}] [{title:^10}] [{title:*^10}]")
        print(f"[{price:8.2f}] [{count:,}] [{count:_d}] [{ratio:.1%}] [{count:.2e}]")
        print(f"[{42:05d}] [{255:x}] [{255:#b}] [{-3:+d}] [{3:+d}]")
        print(f"{title=}, {price * 2 = }")                      # self-documenting, for debugging
        width = 12
        print(f"[{title:>{width}}]")                             # nested: width from a variable
    """)
    table(f, ["spec", "means", "example → result"], [
        ["`<` `>` `^`", "align left / right / centre in the width", "`f\"{'ab':>4}\"` → `'  ab'`"],
        ["`*^10`", "fill character before the alignment", "`f\"{'ab':*^6}\"` → `'**ab**'`"],
        ["`.2f`, `.3g`, `.1%`, `.2e`", "fixed decimals, significant figures, percent, exponent",
         "`f\"{0.5:.0%}\"` → `'50%'`"],
        ["`,` or `_`", "thousands separator", "`f\"{10**6:,}\"` → `'1,000,000'`"],
        ["`05d`, `x`, `b`, `#x`", "zero-pad, hex, binary, with prefix", "`f\"{10:#x}\"` → `'0xa'`"],
        ["`!r`", "use `repr()` instead of `str()`", "`f\"{'a'!r}\"` → `\"'a'\"`"],
    ], widths=[1.5, 2.4, 2.2])
    sub(f, "Unicode: when equal-looking strings aren't equal", ACCENT)
    f.p("\"é\" can be stored as one code point (U+00E9) or as \"e\" plus a combining accent (U+0065 U+0301). "
        "They look identical and compare unequal. {B:Normalise} text from outside before comparing, and use "
        "`casefold()` (not `lower()`) for case-insensitive matching:", 13.5, gap=8)
    repl(f, """
        >>> import unicodedata
        >>> a, b = "caf\\u00e9", "cafe\\u0301"
        >>> a == b, len(a), len(b)
        >>> unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)
        >>> "Straße".lower() == "STRASSE".lower(), "Straße".casefold() == "STRASSE".casefold()
        >>> "".join(c for c in unicodedata.normalize("NFKD", "Zoë Ångström") if not unicodedata.combining(c))
    """)


def regex_tokens(ch):
    f = flow(ch)
    section(f, "Regex building blocks", ACCENT, room=430)
    f.p("A pattern is built from a small set of pieces. Learn these and you can read most regexes:", 13.5, gap=6)
    table(f, ["piece", "matches", "piece", "matches"], [
        ["`abc`", "exactly \"abc\"", "`.`", "any character except newline"],
        ["`\\d` `\\w` `\\s`", "digit, word char (letter, digit, _), whitespace", "`\\D` `\\W` `\\S`",
         "the opposite of each"],
        ["`[aeiou]`", "one of these", "`[^0-9]`", "one character NOT in the set"],
        ["`x*` `x+` `x?`", "0 or more, 1 or more, 0 or 1", "`x{3}` `x{2,4}`", "exactly 3, between 2 and 4"],
        ["`^` `$`", "start / end of the string (or line)", "`\\b`", "word boundary (between \\w and \\W)"],
        ["`a|b`", "a or b", "`(...)`", "group: capture, and apply `*`, `|` to the whole"],
        ["`(?P<name>...)`", "named group", "`(?:...)`", "group without capturing"],
    ], widths=[1.3, 2.3, 1.2, 2.3], size=10.5)
    f.p("Build a pattern up one piece at a time, checking each step against real text:", 13.5, gap=6)
    text = "Call 07700 900123 or +44 7700 900456; fax 0161-555-0199. Ref 12345."
    matches(f, r"\d+", text)
    matches(f, r"\d{5} \d{6}", text)
    matches(f, r"(\+44 |0)7\d{3} \d{6}", text)
    matches(f, r"(\+44 |0)(7\d{3}) (\d{6})", text)
    callout(f, "why", "Step 1 matched every run of digits, including the fax and the reference. Step 2 required the "
            "exact shape but missed the +44 form. Step 3 made the prefix an alternative and fixed the leading "
            "7. Step 4 added groups to pull out the parts. That loop (match too much, tighten, check) is how "
            "regexes are written in practice.")


def using_re(ch):
    f = flow(ch)
    section(f, "Using re: search, findall, groups, sub", ACCENT, room=430)
    code(f, """
        import re

        line = "2026-09-28 14:03:11 WARN loans: member=ana book=Dune days_over=3"
        m = re.search(r"(?P<date>\\S+) (?P<time>\\S+) (?P<level>[A-Z]+) (?P<area>\\w+):", line)
        print(m["level"], m.group("area"), m.span(), m.groupdict()["date"])

        pairs = dict(re.findall(r"(\\w+)=(\\w+)", line))           # with 2 groups: list of tuples
        print(pairs)

        print(re.fullmatch(r"[A-Z]{2}\\d{2} ?\\d[A-Z]{2}", "M13 9PL"))   # whole string must match
        print(re.split(r"[;,]\\s*", "Dune; Emma,Ubik ,  Kim"))
    """)
    table(f, ["function", "returns", "use when"], [
        ["`re.search(p, s)`", "first `Match` anywhere, or `None`", "\"is it in there, and where?\""],
        ["`re.match(p, s)`", "`Match` only at the start, or `None`", "rarely; prefer `fullmatch` or `^`"],
        ["`re.fullmatch(p, s)`", "`Match` if the {B:whole} string fits", "validating input"],
        ["`re.findall(p, s)`", "list of strings (or tuples of groups)", "extracting every occurrence"],
        ["`re.finditer(p, s)`", "iterator of `Match` objects", "you need positions, or big text"],
        ["`re.sub(p, repl, s)`", "new string with matches replaced", "cleaning, redacting, rewriting"],
    ], widths=[1.6, 2.4, 2.2])
    sub(f, "sub with a function", ACCENT)
    f.p("`repl` can be a function: it receives each `Match` and returns the replacement. That turns `sub` into "
        "a general text transformer:", 13.5, gap=8)
    code(f, """
        import re

        def mask(m):
            user, domain = m["user"], m["domain"]
            return f"{user[0]}{'*' * (len(user) - 1)}@{domain}"

        text = "Contact ana.reader@uni.ac.uk or ben@library.org for keys."
        print(re.sub(r"(?P<user>[\\w.+-]+)@(?P<domain>[\\w-]+(\\.[\\w-]+)+)", mask, text))
        print(re.sub(r"(\\d+) days", lambda m: f"{int(m[1]) * 7} days", "renew for 2 days, then 3 days"))
    """)


def greedy(ch):
    f = flow(ch)
    section(f, "Greedy, lazy, and readable patterns", ACCENT, room=430)
    f.p("`*` and `+` are {B:greedy}: they grab as much as possible and only give back what they must. Adding `?` "
        "makes them {B:lazy} (as little as possible). The classic surprise:", 13.5, gap=8)
    html = '<b>Dune</b> and <i>Emma</i>'
    matches(f, r"<.*>", html)
    matches(f, r"<.*?>", html)
    matches(f, r"<[^>]*>", html)
    f.p("Greedy `.*` ran to the {B:last} `>`, swallowing the whole line. The lazy version stops at the first `>`. "
        "A negated class `[^>]*` (\"anything but >\") says exactly what you mean and is usually fastest.",
        13.5, gap=8)
    f.need(300)
    f.p("Long patterns become readable with `re.VERBOSE`: whitespace is ignored and `#` starts a comment:", 13.5,
        gap=6)
    code(f, """
        import re

        POSTCODE = re.compile(r\"\"\"
            ^ (?P<area> [A-Z]{1,2} )      # 1-2 letters: M, SW
              (?P<district> \\d[A-Z\\d]? ) # digit, optional digit/letter: 13, 1A
            \\s?                           # optional space
              (?P<sector> \\d )            # one digit
              (?P<unit> [A-Z]{2} ) $      # two letters
        \"\"\", re.VERBOSE | re.IGNORECASE)

        for pc in ["M13 9PL", "sw1a 1aa", "M13-9PL"]:
            m = POSTCODE.match(pc)
            print(pc, "->", m and m.group("area", "sector"))
    """)
    callout(f, "trap", "Some patterns take exponential time on certain inputs (catastrophic backtracking), e.g. "
            "`(a+)+$` against `\"aaaaaaaaaaaaaaaaaaaaaaaa!\"`. If a regex runs on text from users, keep it "
            "simple, avoid nested quantifiers, and limit the input length. This has taken down real websites.")


def scanner(ch):
    f = flow(ch)
    section(f, "A scanner: turning text into tokens", ACCENT, room=430)
    f.p("Compilers, calculators and config parsers all start by splitting text into {B:tokens} (Ch 2). One regex "
        "with a named alternative per token type, scanned left to right, does it in a few lines:", 13.5, gap=8)
    matches(f, r"(?P<NUMBER>\d+(?:\.\d+)?)|(?P<NAME>[A-Za-z_]\w*)|(?P<OP>[-+*/=()])",
            "total = price * (1 + rate_2) - 3.5", label="NUMBER (orange) · NAME (purple) · OP (green)")
    code(f, """
        import re

        TOKEN = re.compile(r\"\"\"
            (?P<NUMBER> \\d+(?:\\.\\d+)? ) | (?P<NAME> [A-Za-z_]\\w* ) |
            (?P<OP> [-+*/=()] )         | (?P<SKIP> \\s+ )           | (?P<BAD> . )
        \"\"\", re.VERBOSE)

        def tokens(text):
            for m in TOKEN.finditer(text):
                kind = m.lastgroup                     # the name of the group that matched
                if kind == "SKIP":
                    continue
                if kind == "BAD":
                    raise SyntaxError(f"unexpected {m.group()!r} at column {m.start()}")
                yield kind, m.group()

        print(" ".join(f"{kind}:{text}" for kind, text in tokens("total = price * (1 + rate_2)")))
        print(list(tokens("2 $ 3")))
    """, raises=SyntaxError)
    sub(f, "Other text tools in the standard library", ACCENT)
    code(f, """
        import string, textwrap

        t = string.Template("Dear $name, '$title' is due on ${day}.")
        print(t.substitute(name="Ana", title="Dune", day="Friday"))
        print(textwrap.fill("Regular expressions are a small language for describing text.", width=28))
        print(textwrap.shorten("A very long book title that will not fit", width=24, placeholder="..."))
    """)


def finish(ch):
    f = flow(ch)
    section(f, "Practise, then stamp", ACCENT, room=300)
    practice(f, 9)
    stamp(f, [
        (5, "`str` is immutable Unicode text (code points); normalise with `unicodedata`, compare with "
            "`casefold`. Format specs: `{x:>10,.2f}`. Regex via `re` (Perl-style syntax, raw strings, named "
            "groups, `sub` with functions, `VERBOSE`)."),
        (11, "`re`, `string`, `textwrap`, `unicodedata`, `difflib` cover most text work."),
    ])
    callout(f, "other", "Regex syntax is nearly the same everywhere (Perl-compatible): JavaScript `/\\d+/g`, "
            "Java `Pattern.compile`, `grep -E`, your editor's search box. What changes is the API around it and "
            "a few features (named group syntax, lookbehind support).")
    callout(f, "deep", "Vault notes: {b:5.11} Strings, Unicode, and textual value · {b:5.12} Bytes and the text "
            "boundary · {b:7.9} Strings as immutable sequences with textual semantics.")


def build(ch):
    title_page(ch)
    formatting(ch)
    regex_tokens(ch)
    using_re(ch)
    greedy(ch)
    scanner(ch)
    finish(ch)
