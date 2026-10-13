"""Shared helpers for the Python book: page flow, code that really runs, and the diagram language
(memory pictures, pipes, sequence diagrams, timelines, library cards, two-ways pages, passports)."""
import builtins
import contextlib
import io
import keyword
import os
import tempfile
import textwrap
import tokenize
import traceback

from generator import canvas as C
from generator import fonts as F
from generator.book import CheckFailed

L, R, W = 50, 545, 495

CODE_BG, CODE_EDGE, CODE_HL = "#f6f7f9", "#d5d9df", "#fff1a8"
OUT_BG, OUT_INK, OUT_ERR = "#22262e", "#e9edf2", "#ff8a80"
KW, BUILTIN, STR, NUM, COMMENT, DEFNAME, DECO, PROMPT = (
    "#7b3fb5", "#00838f", "#1e8a3c", "#c25e00", "#8a8a8a", "#1f5fbf", "#c2185b", "#8a8a8a")
BUILTINS = set(dir(builtins))
SOFT = {"match", "case", "type", "_"}


# ----------------------------------------------------------------------------- flow
def flow(ch):
    """One continuous writing position for the whole chapter (after its title page)."""
    if getattr(ch, "_flow", None) is None:
        ch._flow = ch.flow()
        ch._flow.new_page()
    return ch._flow


def section(f, title, color, room=300, size=19, fresh=False):
    if fresh and f.y > f.top + 5:
        f.new_page()
    elif f.y > f.top + 5:
        f.need(room)
        if f.y > f.top + 5:
            f.gap(18)
    pg = f.pg
    s = size
    while pg.twidth(title, s, F.BOLD) > W - 24 and s > 12:
        s -= 1
    y = f.y
    pg.rect(L - 2, y + 3, 12, 12, color, 1.2, fillcolor=C.LIGHT.get(color, "#eeeeee"), r=3)
    pg.text(L + 18, y - 1 + (size - s) / 2, title, s, color, F.BOLD)
    f.y += size + 14


def sub(f, title, color=C.INK, size=13.5, room=80):
    f.need(room)
    f.text(title, size, color, F.BOLD, gap=5)


def title_block(ch, number, title, tagline, color, bg="#ffffff"):
    pg = ch.new_page(bg=bg)
    pg.text(L, 60, f"{'Appendix' if isinstance(number, str) else 'Chapter'} {number}", 16, C.GREY, F.BOLD)
    s = 38
    while pg.twidth(title, s, F.BOLD) > W and s > 22:
        s -= 1
    pg.text(L, 82, title, s, color, F.BOLD)
    pg.note(L, 88 + s * 1.25, tagline, color, 22, w=W)
    return pg


# ----------------------------------------------------------------------------- callouts
KINDS = {
    "idea": ("KEY IDEA", C.BLUE),
    "trap": ("TRAP", C.RED),
    "why": ("WHY", C.PURPLE),
    "other": ("IN OTHER LANGUAGES", C.TEAL),
    "deep": ("DEEP DIVE (your vault)", C.BROWN),
    "honest": ("HONEST NOTE", C.ORANGE),
    "rule": ("RULE OF THUMB", C.GREEN),
}


def callout(f, kind, markup, size=12.5, gap=10):
    label, col = KINDS[kind]
    w = W - 22
    h = f.pg.rich_h(markup, w, size) + 24
    y = f.reserve(h + gap)
    pg = f.pg
    pg.rect(L, y, W, h, col, 0, fillcolor=C.LIGHT[col], r=5)
    pg.rect(L, y, 4, h, col, 0, fillcolor=col)
    pg.text(L + 14, y + 5, label, 9.5, col, F.BOLD)
    pg.rich(L + 14, y + 19, markup, w, size)
    return y


GO_FILL = "#fff7dc"


def go(f, s, gap=10, size=14, label="✎ YOUR GO (pencil, or the REPL, first)"):
    s = s.replace("`", "")
    h = 30 + F.line_h(F.HAND, size) * len(F.wrap(s, F.HAND, size, W - 24)) + 8
    y = f.reserve(h + gap)
    pg = f.pg
    pg.rect(L, y, W, h, C.ORANGE, 1.2, fillcolor=GO_FILL, r=8)
    pg.text(L + 12, y + 7, label, 11, C.ORANGE, F.BOLD)
    pg.note(L + 12, y + 26, s, C.INK, size, w=W - 24)


# ----------------------------------------------------------------------------- syntax colouring
def _spans(src):
    """Per line: list of (col0, col1, colour, font). Falls back to plain text if tokenize fails."""
    lines = src.split("\n")
    spans = [[] for _ in lines]
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src + "\n").readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return [[(0, len(l), C.INK, F.MONO)] if l else [] for l in lines]
    prev = None
    for t in toks:
        (r0, c0), (r1, c1) = t.start, t.end
        col, font = C.INK, F.MONO
        if t.type == tokenize.NAME:
            if keyword.iskeyword(t.string) or (t.string in SOFT and t.string != "_" and c0 == 0):
                col, font = KW, F.MONOB
            elif prev is not None and prev.type == tokenize.NAME and prev.string in ("def", "class"):
                col, font = DEFNAME, F.MONOB
            elif t.string in BUILTINS:
                col = BUILTIN
        elif t.type == tokenize.STRING or t.type in getattr(tokenize, "FSTRING_TYPES", ()):
            col = STR
        elif t.type in (getattr(tokenize, "FSTRING_START", -1), getattr(tokenize, "FSTRING_MIDDLE", -1),
                        getattr(tokenize, "FSTRING_END", -1), getattr(tokenize, "TSTRING_START", -2),
                        getattr(tokenize, "TSTRING_MIDDLE", -2), getattr(tokenize, "TSTRING_END", -2)):
            col = STR
        elif t.type == tokenize.NUMBER:
            col = NUM
        elif t.type == tokenize.COMMENT:
            col = COMMENT
        elif t.type == tokenize.OP and t.string == "@" and c0 == len(lines[r0 - 1]) - len(lines[r0 - 1].lstrip()):
            col = DECO
        if t.type in (tokenize.NEWLINE, tokenize.NL, tokenize.INDENT, tokenize.DEDENT,
                      tokenize.ENDMARKER):
            continue
        prev = t
        for r in range(r0, r1 + 1):
            if r - 1 >= len(lines):
                break
            a = c0 if r == r0 else 0
            b = c1 if r == r1 else len(lines[r - 1])
            if b > a:
                spans[r - 1].append((a, b, col, font))
    for i, l in enumerate(lines):          # anything tokenize skipped (e.g. after errors) stays visible
        covered = sorted(spans[i])
        out, pos = [], 0
        for a, b, col, font in covered:
            if a > pos and l[pos:a].strip():
                out.append((pos, a, C.INK, F.MONO))
            if b > pos:
                out.append((max(a, pos), b, col, font))
                pos = b
        if pos < len(l) and l[pos:].strip():
            out.append((pos, len(l), C.INK, F.MONO))
        spans[i] = out
    return spans


def _draw_line(pg, x, y, line, spans, cw, size):
    for a, b, col, font in spans:
        seg = line[a:b]
        lead = len(seg) - len(seg.lstrip(" "))
        seg = seg.strip(" ")
        if seg:
            # draw each run on its own so columns line up exactly
            pg.text(x + (a + lead) * cw, y, seg, size, col, font)


# ----------------------------------------------------------------------------- running snippets
class _Cwd:
    def __init__(self, ch):
        if getattr(ch, "_tmp", None) is None:
            ch._tmp = tempfile.mkdtemp(prefix=f"pvg-ch{ch.num}-")
        self.dir = ch._tmp

    def __enter__(self):
        self.old = os.getcwd()
        os.chdir(self.dir)

    def __exit__(self, *a):
        os.chdir(self.old)


def run_src(ch, src, ns=None, mode="exec", raises=None):
    """Run code the way the reader would; return what they'd see printed."""
    if ns is None:
        if getattr(ch, "_ns", None) is None:
            ch._ns = {"__name__": "__main__"}
        ns = ch._ns
    buf = io.StringIO()
    err = None
    with _Cwd(ch), contextlib.redirect_stdout(buf):
        try:
            exec(compile(src, f"<chapter {ch.num}>", mode), ns)
        except Exception as e:  # noqa: BLE001
            if raises is None or not isinstance(e, raises):
                raise CheckFailed(f"ch{ch.num} snippet raised {e!r}:\n{src}") from e
            err = "".join(traceback.format_exception_only(type(e), e)).strip()
    if raises is not None and err is None:
        raise CheckFailed(f"ch{ch.num} snippet should have raised {raises}:\n{src}")
    return buf.getvalue(), err


def code(f, src, notes=None, hl=(), run=True, expect=None, ns=None, size=9.2, show_out=True,
         raises=None, out_max=14, numbers=True, w=None, gap=12, title=None, x=None, output=None):
    """A code box. If run, the code is executed now and its real output shown underneath.
    notes = {line_number: 'hand-written note'} drawn in the right margin."""
    ch = f.ch
    src = textwrap.dedent(src).strip("\n").expandtabs(4)
    lines = src.split("\n")
    out, err = ("", None)
    if run:
        out, err = run_src(ch, src, ns, raises=raises)
        if expect is not None and out.strip() != textwrap.dedent(expect).strip():
            raise CheckFailed(f"ch{ch.num} output mismatch:\n--- got\n{out}\n--- expected\n{expect}\n{src}")
        ch.checks += 1
    if output is not None:
        out = textwrap.dedent(output).strip("\n") + "\n"
    cw = F.width("M", F.MONO, size)
    lh = F.line_h(F.MONO, size) * 1.04
    gut = (len(str(len(lines))) + 1.2) * cw if numbers else 0
    pad = 7
    need_w = gut + max(len(l) for l in lines) * cw + 2 * pad
    x0 = L if x is None else x
    if w is None and notes and W - 130 < need_w <= (W - 130) * 9.2 / 8.2:
        w = W - 130                       # shrink a little so the notes keep their margin
    if w is None:
        w = W if not notes else max(220, need_w)
        if w > W - 130:
            w = W
    while need_w > w + 0.5 and size > 8.0:
        size = round(size - 0.2, 2)
        cw = F.width("M", F.MONO, size)
        lh = F.line_h(F.MONO, size) * 1.04
        gut = (len(str(len(lines))) + 1.2) * cw if numbers else 0
        need_w = gut + max(len(l) for l in lines) * cw + 2 * pad
    if need_w > w + 0.5:
        raise CheckFailed(f"ch{ch.num} code too wide ({need_w:.0f} > {w:.0f}): {max(lines, key=len)!r}")
    title_h = 15 if title else 0
    code_h = len(lines) * lh + 2 * pad
    olines = []
    if show_out and (out or err):
        olines = out.rstrip("\n").split("\n") if out.strip() else []
        if len(olines) > out_max:
            olines = olines[:out_max - 1] + ["..."]
        if err:
            olines.append(err)
    out_h = (len(olines) * lh + 2 * pad + 2) if olines else 0
    below = []
    if notes and R - (x0 + w + 22) < 105:       # no room in the margin: list the notes underneath
        below = [f"line {ln}: {notes[ln]}" for ln in sorted(notes)]
        notes = None
    below_h = sum(F.line_h(F.HAND, 14) * len(F.wrap(b, F.HAND, 14, W - 10)) for b in below) + (4 if below else 0)
    total = title_h + code_h + out_h + below_h
    y = f.reserve(total + gap)
    pg = f.pg
    if title:
        pg.text(x0 + 2, y, title, 9.5, C.GREY, F.BOLD)
        y += title_h
    pg.rect(x0, y, w, code_h, CODE_EDGE, 0.8, fillcolor=CODE_BG, r=5)
    spans = _spans(src)
    for i, line in enumerate(lines):
        ly = y + pad + i * lh
        if (i + 1) in hl:
            pg.rect(x0 + 1, ly - 1, w - 2, lh + 1, CODE_HL, 0, fillcolor=CODE_HL)
        if numbers:
            pg.text(x0 + pad + gut - cw * 1.2, ly, str(i + 1), size * 0.85, "#a0a6ad", F.MONO, align="right")
        _draw_line(pg, x0 + pad + gut, ly, line, spans[i], cw, size)
    if notes:
        nx = x0 + w + 22
        last = -1e9
        for ln in sorted(notes):
            txt = notes[ln]
            ty = y + pad + (ln - 1) * lh + lh / 2
            nh = F.line_h(F.HAND, 14) * len(F.wrap(txt, F.HAND, 14, R - nx))
            top = max(ty - 9, last + 2)
            pg.note(nx, top, txt, C.RED, 14, w=R - nx)
            pg.arrow(nx - 4, top + 9, x0 + w + 3, ty, C.RED, 0.9, head=4)
            last = top + nh
        if last > y + code_h + out_h + gap:
            f.y = max(f.y, last + gap)
    if olines:
        oy = y + code_h + 2
        pg.rect(x0, oy, w, out_h - 2, OUT_BG, 0, fillcolor=OUT_BG, r=5)
        for i, ol in enumerate(olines):
            col = OUT_ERR if (err and i == len(olines) - 1) else OUT_INK
            if F.width(ol, F.MONO, size) > w - 2 * pad:
                while ol and F.width(ol + "…", F.MONO, size) > w - 2 * pad:
                    ol = ol[:-1]
                ol += "…"
            if ol.strip():
                lead = len(ol) - len(ol.lstrip(" "))
                pg.text(x0 + pad + lead * cw, oy + pad + i * lh, ol.strip(" "), size, col, F.MONO)
    by = y + code_h + out_h + 3
    for b in below:
        by += pg.note(x0 + 6, by, b, C.RED, 14, w=W - 10)
    return out


def repl(f, src, ns=None, size=9.2, gap=12, expect=None, w=None, notes=None, raises_ok=False):
    """An interactive session: lines starting '>>> ' (and '... ') are run like the real REPL,
    and the echoed values appear underneath each prompt."""
    ch = f.ch
    if ns is None:
        if getattr(ch, "_ns", None) is None:
            ch._ns = {"__name__": "__main__"}
        ns = ch._ns
    chunks, cur = [], []
    for line in textwrap.dedent(src).strip("\n").split("\n"):
        if line.startswith(">>> "):
            if cur:
                chunks.append(cur)
            cur = [line[4:]]
        elif line.startswith("... ") or line == "...":
            cur.append(line[4:])
        elif line.strip():
            raise CheckFailed(f"repl lines must start with '>>> ' or '... ': {line!r}")
    if cur:
        chunks.append(cur)
    shown = []  # (text, colour, font)
    for ck in chunks:
        shown.append((">>> " + ck[0], None))
        for c in ck[1:]:
            shown.append(("... " + c, None))
        body = "\n".join(ck) + ("\n" if len(ck) > 1 else "")
        buf = io.StringIO()
        with _Cwd(ch), contextlib.redirect_stdout(buf):
            try:
                exec(compile(body, "<stdin>", "single"), ns)
            except Exception as e:  # noqa: BLE001
                if not raises_ok:
                    raise CheckFailed(f"ch{ch.num} repl raised {e!r}: {body}") from e
                buf.write("".join(traceback.format_exception_only(type(e), e)))
                shown.append(("\0ERR", None))
        for ol in buf.getvalue().rstrip("\n").split("\n") if buf.getvalue() else []:
            shown.append((ol, "out"))
        ch.checks += 1
    if expect is not None:
        got = "\n".join(t for t, k in shown if k == "out")
        if got.strip() != textwrap.dedent(expect).strip():
            raise CheckFailed(f"ch{ch.num} repl mismatch:\n{got}\n--- expected\n{expect}")
    rows = [(t, k) for t, k in shown if t != "\0ERR"]
    cw = F.width("M", F.MONO, size)
    lh = F.line_h(F.MONO, size) * 1.04
    pad = 7
    w = w or (W if not notes else 300)
    h = len(rows) * lh + 2 * pad
    y = f.reserve(h + gap)
    pg = f.pg
    pg.rect(L, y, w, h, CODE_EDGE, 0.8, fillcolor=CODE_BG, r=5)
    for i, (t, k) in enumerate(rows):
        ly = y + pad + i * lh
        maxc = int((w - 2 * pad) / cw)
        if len(t) > maxc:
            t = t[:maxc - 1] + "…"
        if k == "out":
            col = C.RED if t.split(":")[0].endswith(("Error", "Exception")) else "#3b4250"
            if t.strip():
                pg.text(L + pad + (len(t) - len(t.lstrip(" "))) * cw, ly, t.strip(" "), size, col, F.MONO)
        else:
            pg.text(L + pad, ly, t[:4], size, PROMPT, F.MONO)
            body = t[4:]
            sp = _spans(body)[0] if body.strip() else []
            _draw_line(pg, L + pad + 4 * cw, ly, body, sp, cw, size)
    if notes:
        nx = L + w + 22
        for ln, txt in notes.items():
            ty = y + pad + (ln - 1) * lh + lh / 2
            pg.note(nx, ty - 9, txt, C.RED, 14, w=R - nx)
            pg.arrow(nx - 4, ty, L + w + 3, ty, C.RED, 0.9, head=4)
    return y


def shell(f, text, size=9.2, gap=12, title=None):
    """A terminal transcript (not executed). Lines starting '$ ' are commands."""
    lines = textwrap.dedent(text).strip("\n").split("\n")
    lh = F.line_h(F.MONO, size) * 1.04
    pad = 7
    th = 14 if title else 0
    h = len(lines) * lh + 2 * pad
    y = f.reserve(h + th + gap)
    pg = f.pg
    if title:
        pg.text(L + 2, y, title, 9.5, C.GREY, F.BOLD)
        y += th
    pg.rect(L, y, W, h, OUT_BG, 0, fillcolor=OUT_BG, r=5)
    cw = F.width("M", F.MONO, size)
    for i, l in enumerate(lines):
        ly = y + pad + i * lh
        if l.startswith("$ "):
            pg.text(L + pad, ly, "$", size, "#7ee787", F.MONOB)
            pg.text(L + pad + 2 * cw, ly, l[2:], size, "#ffffff", F.MONOB)
        elif l.strip():
            pg.text(L + pad + (len(l) - len(l.lstrip())) * cw, ly, l.strip(), size, OUT_INK, F.MONO)


# ----------------------------------------------------------------------------- SQL that really runs
SQL_KW = set("""SELECT FROM WHERE JOIN LEFT INNER OUTER CROSS ON USING GROUP BY ORDER LIMIT OFFSET INSERT INTO VALUES
CREATE TABLE IF EXISTS NOT NULL PRIMARY KEY UNIQUE REFERENCES FOREIGN AS AND OR IN IS HAVING INDEX UPDATE SET
DELETE DROP DEFAULT CHECK DESC ASC DISTINCT EXPLAIN QUERY PLAN BEGIN COMMIT ROLLBACK CASCADE LIKE BETWEEN
CASE WHEN THEN ELSE END UNION ALL ALTER ADD COLUMN RETURNING CONFLICT REPLACE IGNORE WITH RECURSIVE
INTEGER TEXT REAL BLOB NUMERIC STRICT PRAGMA AUTOINCREMENT TRANSACTION""".split())
SQL_FN = {"COUNT", "SUM", "AVG", "MIN", "MAX", "LENGTH", "UPPER", "LOWER", "COALESCE", "ROUND", "DATE",
          "GROUP_CONCAT", "TOTAL", "ABS", "SUBSTR", "IFNULL", "TIME", "DATETIME", "STRFTIME"}
_SQL_TOK = __import__("re").compile(r"(--[^\n]*|'(?:[^']|'')*'|\b\d+(?:\.\d+)?\b|\?|:\w+|\b\w+\b)")


def _sql_spans(line):
    out = []
    for m in _SQL_TOK.finditer(line):
        t = m.group(0)
        if t.startswith("--"):
            out.append((m.start(), m.end(), COMMENT, F.MONO))
        elif t.startswith("'"):
            out.append((m.start(), m.end(), STR, F.MONO))
        elif t[0].isdigit() or t == "?" or t.startswith(":"):
            out.append((m.start(), m.end(), NUM, F.MONO))
        elif t.upper() in SQL_KW and t.isupper():
            out.append((m.start(), m.end(), KW, F.MONOB))
        elif t.upper() in SQL_FN:
            out.append((m.start(), m.end(), BUILTIN, F.MONO))
        else:
            out.append((m.start(), m.end(), C.INK, F.MONO))
    filled, pos = [], 0
    for a, b, col, font in out:
        if a > pos and line[pos:a].strip():
            filled.append((pos, a, C.INK, F.MONO))
        filled.append((a, b, col, font))
        pos = b
    if line[pos:].strip():
        filled.append((pos, len(line), C.INK, F.MONO))
    return filled


def sql(f, conn, query, params=(), max_rows=8, size=9.2, gap=12, raises=None, script=False, show_rows=True,
        expect_rows=None, title=None, note=None):
    """A SQL box run for real against `conn`, with the result drawn as a grid underneath."""
    ch = f.ch
    q = textwrap.dedent(query).strip("\n")
    lines = q.split("\n")
    rows, cols, err, changed = [], [], None, None
    try:
        if script:
            conn.executescript(q)
        else:
            cur = conn.execute(q, params)
            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
            elif cur.rowcount >= 0:
                changed = cur.rowcount
    except Exception as e:  # noqa: BLE001
        if raises is None or not isinstance(e, raises):
            raise CheckFailed(f"ch{ch.num} sql raised {e!r}:\n{q}") from e
        mod = type(e).__module__
        err = f"{'' if mod == 'builtins' else mod + '.'}{type(e).__name__}: {e}"
    if raises is not None and err is None:
        raise CheckFailed(f"ch{ch.num} sql should have raised {raises}:\n{q}")
    if expect_rows is not None and [tuple(r) for r in rows] != [tuple(r) for r in expect_rows]:
        raise CheckFailed(f"ch{ch.num} sql rows mismatch: {rows!r} != {expect_rows!r}\n{q}")
    ch.checks += 1
    cw = F.width("M", F.MONO, size)
    lh = F.line_h(F.MONO, size) * 1.04
    pad = 7
    if max(len(l) for l in lines) * cw + 2 * pad > W:
        raise CheckFailed(f"ch{ch.num} sql too wide: {max(lines, key=len)!r}")
    code_h = len(lines) * lh + 2 * pad
    shown = [tuple("NULL" if v is None else (repr(v) if isinstance(v, bytes) else str(v)) for v in r)
             for r in rows[:max_rows]]
    more = len(rows) - len(shown)
    gsize = size
    rh = F.line_h(F.MONO, gsize) + 6
    grid_h = 0
    widths = []
    if show_rows and cols:
        widths = [max([F.width(c, F.MONOB, gsize)] + [F.width(r[j], F.MONO, gsize) for r in shown]) + 14
                  for j, c in enumerate(cols)]
        if sum(widths) > W:
            k = W / sum(widths)
            widths = [w_ * k for w_ in widths]
        grid_h = rh * (1 + len(shown)) + (rh if more else 0) + (rh if not shown else 0) + 4
    msg = None
    if err:
        msg = err
    elif changed is not None and not cols:
        msg = f"ok: {changed} row{'s' if changed != 1 else ''} changed"
    elif script:
        msg = "ok"
    msg_h = (lh + 2 * pad) if msg else 0
    th = 15 if title else 0
    y = f.reserve(th + code_h + grid_h + msg_h + gap + 2)
    pg = f.pg
    if title:
        pg.text(L + 2, y, title, 9.5, C.GREY, F.BOLD)
        y += th
    pg.rect(L, y, W, code_h, CODE_EDGE, 0.8, fillcolor="#f3f6fb", r=5)
    pg.text(R - 8, y + 3, "SQL", 7.5, "#9aa5b5", F.BOLD, align="right")
    for i, line in enumerate(lines):
        _draw_line(pg, L + pad, y + pad + i * lh, line, _sql_spans(line), cw, size)
    if note:
        pg.note(R + 6, y + 2, note, C.RED, 13, w=40)
    y += code_h + 4
    if grid_h:
        tw = sum(widths)
        x = L
        pg.rect(L, y, tw, rh, C.TEAL, 0, fillcolor=C.LIGHT[C.TEAL])
        for c, wd in zip(cols, widths):
            pg.text(x + 7, y + 3, c, gsize, C.TEAL, F.MONOB)
            x += wd
        for i, r in enumerate(shown):
            ry = y + rh * (i + 1)
            if i % 2:
                pg.rect(L, ry, tw, rh, "#f4f5f7", 0, fillcolor="#f4f5f7")
            x = L
            for v, wd in zip(r, widths):
                col = C.GREY if v == "NULL" else C.INK
                while v and F.width(v, F.MONO, gsize) > wd - 10:
                    v = v[:-2] + "…" if len(v) > 2 else ""
                pg.text(x + 7, ry + 3, v, gsize, col, F.MONO)
                x += wd
        last = y + rh * (1 + len(shown))
        if not shown:
            pg.text(L + 7, last + 3, "(no rows)", gsize, C.GREY, F.MONO)
            last += rh
        if more:
            pg.text(L + 7, last + 3, f"… {more} more row{'s' if more > 1 else ''}", gsize, C.GREY, F.MONO)
            last += rh
        pg.rect(L, y, tw, last - y, C.TEAL, 0.8)
        y = last + 4
    if msg:
        colr = OUT_ERR if err else "#7ee787"
        pg.rect(L, y, W, msg_h - 2, OUT_BG, 0, fillcolor=OUT_BG, r=5)
        m = msg
        while F.width(m, F.MONO, size) > W - 2 * pad:
            m = m[:-2] + "…"
        pg.text(L + pad, y + pad, m, size, colr, F.MONO)
    return rows


def er(f, tables, links, gap=14, size=9.5, col_w=None):
    """Entity-relationship picture. tables: [(name, [(column, 'PK'|'FK'|''), ...]), ...] drawn left to right.
    links: [(table.column, table.column)] arrows from a foreign key to the key it points at."""
    n = len(tables)
    gapx = 46
    bw = col_w or (W - gapx * (n - 1)) / n
    rh = 17
    h = max(len(cols) for _, cols in tables) * rh + 26
    y0 = f.reserve(h + gap)
    pg = f.pg
    pos = {}
    for i, (name, cols) in enumerate(tables):
        x = L + i * (bw + gapx)
        th = len(cols) * rh + 24
        pg.rect(x, y0, bw, th, C.INK, 1.1, fillcolor="#ffffff", r=5)
        pg.rect(x, y0, bw, 20, C.BLUE, 0, fillcolor=C.LIGHT[C.BLUE], r=5)
        pg.text(x + bw / 2, y0 + 3, name, size + 1, C.BLUE, F.BOLD, align="center")
        for k, (c, tag) in enumerate(cols):
            cy = y0 + 23 + k * rh
            colr = {"PK": C.ORANGE, "FK": C.PURPLE}.get(tag, C.INK)
            if tag:
                pg.text(x + 6, cy + 1, tag, 7.5, colr, F.BOLD)
            pg.text(x + 26, cy, c, size, colr, F.MONOB if tag == "PK" else F.MONO)
            pos[f"{name}.{c}"] = (x, x + bw, cy + rh / 2 - 2)
    for a, b in links:
        ax0, ax1, ay = pos[a]
        bx0, bx1, by = pos[b]
        if ax0 > bx0:
            pg.arrow(ax0 - 2, ay, bx1 + 2, by, C.PURPLE, 1.1, head=5)
        else:
            pg.arrow(ax1 + 2, ay, bx0 - 2, by, C.PURPLE, 1.1, head=5)
    return y0


# ----------------------------------------------------------------------------- tables
def table(f, header, rows, widths=None, size=11, head_col=C.BLUE, gap=12, zebra=True, mono=()):
    """Rows of rich-markup cells. `mono` = column indexes drawn in code font."""
    n = len(header)
    widths = widths or [W / n] * n
    scale = W / sum(widths)
    widths = [w_ * scale for w_ in widths]
    pg = f.pg

    def cell(s, j):
        return f"`{s}`" if (j in mono and s and not s.startswith("`")) else s

    hh = max(pg.rich_h(f"**{h_}**", wd - 10, size) for h_, wd in zip(header, widths)) + 8
    heights = [max(pg.rich_h(cell(c, j), wd - 10, size) for j, (c, wd) in enumerate(zip(r, widths))) + 8
               for r in rows]
    y = f.reserve(hh + min(sum(heights[:3]), sum(heights)))
    pg = f.pg
    x = L
    pg.rect(L, y, W, hh, head_col, 0, fillcolor=C.LIGHT[head_col])
    for h_, wd in zip(header, widths):
        pg.rich(x + 5, y + 4, f"**{h_}**", wd - 10, size, head_col)
        x += wd
    f.y = y + hh
    for k, (r, rh) in enumerate(zip(rows, heights)):
        if f.need(rh):
            pass
        pg = f.pg
        y = f.y
        if zebra and k % 2:
            pg.rect(L, y, W, rh, "#f4f5f7", 0, fillcolor="#f4f5f7")
        x = L
        for j, (c, wd) in enumerate(zip(r, widths)):
            pg.rich(x + 5, y + 4, cell(c, j), wd - 10, size)
            x += wd
        pg.line(L, y + rh, R, y + rh, "#dfe3e8", 0.6)
        f.y = y + rh
    f.gap(gap)


def trace(f, header, rows, **kw):
    """A trace table: one row per step, showing how the variables change."""
    table(f, header, rows, head_col=kw.pop("head_col", C.PURPLE), mono=kw.pop("mono", tuple(range(len(header)))),
          **kw)


# ----------------------------------------------------------------------------- diagrams
def _box(pg, x, y, w, h, s, col, size=11, font=F.SANS, fill=None, r=6, mono=False):
    pg.rect(x, y, w, h, col, 1.2, fillcolor=fill or C.LIGHT.get(col, "#ffffff"), r=r)
    if mono:
        font = F.MONO
    lines = s.split("\n")
    lh = F.line_h(font, size)
    ty = y + (h - lh * len(lines)) / 2
    for i, l in enumerate(lines):
        pg.text(x + w / 2, ty + i * lh, l, size, col if col != C.INK else C.INK, font, align="center")


def pipe(f, stages, color=C.BLUE, labels=None, size=10.5, h=40, gap=14, mono=False, under=None):
    """Boxes joined left to right by arrows: a lifecycle or a data-flow pipeline.
    stages: list of str or (str, colour). labels: text on the arrows. under: notes under boxes."""
    st = [(s, color) if isinstance(s, str) else s for s in stages]
    font = F.MONO if mono else F.SANS
    widths = [max(F.width(l, font, size) for l in s.split("\n")) + 18 for s, _ in st]
    arrow_w = 30 if not labels else max(34, max(F.width(l or "", F.HAND, 13) for l in labels) + 10)
    total = sum(widths) + arrow_w * (len(st) - 1)
    if total > W:
        k = W / total
        size *= k
        widths = [w_ * k for w_ in widths]
        arrow_w *= k
        total = W
    uh = 0
    if under:
        uh = max(F.line_h(F.HAND, 13) * len(F.wrap(u or "", F.HAND, 13, wd + arrow_w - 6))
                 for u, wd in zip(under, widths)) + 4
    lab_h = 14 if labels else 0
    y = f.reserve(lab_h + h + uh + gap)
    pg = f.pg
    x = L + (W - total) / 2
    y += lab_h
    for i, ((s, col), wd) in enumerate(zip(st, widths)):
        _box(pg, x, y, wd, h, s, col, size, font)
        if under and under[i]:
            pg.note(x, y + h + 3, under[i], C.GREY, 13, w=wd + arrow_w - 6)
        if i < len(st) - 1:
            pg.arrow(x + wd + 3, y + h / 2, x + wd + arrow_w - 3, y + h / 2, C.GREY, 1.2, head=5)
            if labels and labels[i]:
                pg.note(x + wd + arrow_w / 2, y - lab_h - 3, labels[i], C.PURPLE, 13, align="center")
        x += wd + arrow_w


def memory(f, frames, objects, links, height=None, gap=14, obj_x=(L + 230, L + 390), size=10.5):
    """Names on the left (grouped in frames), objects on the right, arrows between them.
    frames:  [(label, [name, ...]), ...]
    objects: {id: dict(t='int', v='42', col=0|1 (or x=absolute), row=k, slots=['0','1'] optional)}
    links:   [(src, dst)] where src is a name, or 'obj_id.slot'."""
    row_h, name_w, cell_h = 26, 120, 22
    rows = sum(len(n) + 1 for _, n in frames)
    oh = max([o.get("row", 0) for o in objects.values()] + [0]) + 1
    h = height or max(rows * row_h, oh * 46) + 10
    y0 = f.reserve(h + gap)
    pg = f.pg
    pos = {}
    y = y0
    for label, names in frames:
        fh = len(names) * row_h + 22
        pg.rect(L, y, name_w + 20, fh, C.GREY, 1.0, fillcolor="#f4f5f7", r=6)
        pg.text(L + 8, y + 3, label, 9.5, C.GREY, F.BOLD)
        for k, nm in enumerate(names):
            ny = y + 20 + k * row_h
            pg.rect(L + 10, ny, name_w, cell_h, C.INK, 0.9, fillcolor="#ffffff", r=3)
            pg.text(L + 16, ny + 4, nm, 10.5, C.INK, F.MONO)
            pos[nm] = (L + 10 + name_w, ny + cell_h / 2)
        y += fh + 8
    for oid, o in objects.items():
        ox = o["x"] if "x" in o else obj_x[o.get("col", 0)]
        oy = y0 + o.get("row", 0) * 46 + 4
        col = o.get("color", C.BLUE)
        slots = o.get("slots")
        tl = o.get("t", "")
        if slots:
            sw = 26
            bw = max(sw * len(slots) + 12, F.width(tl, F.SANS, 9) + 12)
            pg.rect(ox, oy, bw, 38, col, 1.2, fillcolor=C.LIGHT[col], r=6)
            pg.text(ox + 6, oy + 2, tl, 9, col, F.BOLD)
            for k, s in enumerate(slots):
                sx = ox + 6 + k * sw
                pg.rect(sx, oy + 15, sw - 2, 19, col, 0.8, fillcolor="#ffffff")
                pg.text(sx + (sw - 2) / 2, oy + 17, s, 8, C.GREY, F.MONO, align="center")
                pos[f"{oid}.{k}"] = (sx + (sw - 2) / 2, oy + 24.5)
            pos[oid] = (ox, oy + 19)
        else:
            v = o.get("v", "")
            bw = max(F.width(v, F.MONO, size) + 16, F.width(tl, F.SANS, 9) + 14, 44)
            pg.rect(ox, oy, bw, 38, col, 1.2, fillcolor=C.LIGHT[col], r=6)
            pg.text(ox + 6, oy + 2, tl, 9, col, F.BOLD)
            pg.text(ox + 8, oy + 17, v, size, C.INK, F.MONO)
            pos[oid] = (ox + bw / 2, oy + 2) if o.get("anchor") == "top" else (ox, oy + 19)
    for src, dst in links:
        x1, y1 = pos[src]
        x2, y2 = pos[dst]
        if "." in src:
            pg.rect(x1 - 2, y1 - 2, 4, 4, C.ORANGE, 0.8, fillcolor=C.ORANGE, r=2)
            if objects[dst].get("anchor") == "top":
                pg.arrow(x1, y1 + 2, x2, y2, C.ORANGE, 1.1, head=5)
            else:
                pg.arrow(x1 + 2, y1, x2 - 2, y2, C.ORANGE, 1.1, bend=0.08, head=5)
        else:
            pg.arrow(x1 + 2, y1, x2 - 2, y2, C.ORANGE, 1.2, bend=0.0, head=5)
    return y0


def seq(f, actors, msgs, gap=14, size=10.5, step=30):
    """Sequence diagram. msgs: (from, to, label) or (from, to, label, 'reply')."""
    n = len(actors)
    xs = [L + W * (i + 0.5) / n for i in range(n)]
    h = 36 + step * len(msgs) + 16
    y0 = f.reserve(h + gap)
    pg = f.pg
    for a, x in zip(actors, xs):
        wd = F.width(a, F.BOLD, size) + 18
        pg.rect(x - wd / 2, y0, wd, 26, C.INK, 1.1, fillcolor="#eef1f5", r=5)
        pg.text(x, y0 + 6, a, size, C.INK, F.BOLD, align="center")
        pg.line(x, y0 + 26, x, y0 + h - 4, C.GREY, 0.9, dash=(3, 3))
    for k, m in enumerate(msgs):
        a, b, lab = m[:3]
        reply = len(m) > 3 and m[3] == "reply"
        y = y0 + 44 + k * step
        xa, xb = xs[actors.index(a)], xs[actors.index(b)]
        col = C.GREEN if reply else C.BLUE
        pg.arrow(xa, y, xb, y, col, 1.2, head=5, dash=(4, 3) if reply else None)
        pg.text((xa + xb) / 2, y - 13, lab, 9.5, col, F.MONO, align="center")


def timeline(f, lanes, spans, tmax, unit="ms", gap=14, ticks=None, lane_h=24):
    """Concurrency picture. spans: (lane_index, t0, t1, label, colour)."""
    lw = 92
    h = len(lanes) * (lane_h + 6) + 24
    y0 = f.reserve(h + gap)
    pg = f.pg
    x0, x1 = L + lw, R - 6
    sx = (x1 - x0) / tmax
    for i, ln in enumerate(lanes):
        y = y0 + i * (lane_h + 6)
        pg.text(L, y + 5, ln, 10, C.INK, F.BOLD)
        pg.line(x0, y + lane_h / 2, x1, y + lane_h / 2, "#e3e6ea", 0.8)
    for lane, t0, t1, lab, col in spans:
        y = y0 + lane * (lane_h + 6)
        pg.rect(x0 + t0 * sx, y + 2, max(2, (t1 - t0) * sx), lane_h - 4, col, 0.9, fillcolor=C.LIGHT[col], r=3)
        if lab and F.width(lab, F.SANS, 8.5) < (t1 - t0) * sx - 4:
            pg.text(x0 + (t0 + t1) / 2 * sx, y + 6, lab, 8.5, col, align="center")
    ty = y0 + len(lanes) * (lane_h + 6) + 2
    pg.line(x0, ty, x1, ty, C.GREY, 0.9)
    for t in ticks or [0, tmax / 2, tmax]:
        pg.line(x0 + t * sx, ty - 3, x0 + t * sx, ty + 3, C.GREY, 0.9)
        pg.text(x0 + t * sx, ty + 4, f"{t:g} {unit}", 8.5, C.GREY, align="center")


def tree(f, nodes, edges, gap=14, size=10, h=None, mono=True, col=C.BLUE, row_h=46):
    """Boxes at given positions (relative x 0..1, row) joined by lines. nodes: {id: (label, x, row)}."""
    rows = max(r for _, _, r in nodes.values()) + 1
    h = h or rows * row_h
    y0 = f.reserve(h + gap)
    pg = f.pg
    font = F.MONO if mono else F.SANS
    centres = {}
    for nid, (lab, rx, row) in nodes.items():
        wd = F.width(lab if isinstance(lab, str) else lab[0], font, size) + 14
        cx, cy = L + rx * W, y0 + row * row_h + 14
        centres[nid] = (cx, cy, wd)
    for a, b in edges:
        xa, ya, _ = centres[a]
        xb, yb, _ = centres[b]
        pg.line(xa, ya + 11, xb, yb - 11, C.GREY, 1.0)
    for nid, (lab, rx, row) in nodes.items():
        cx, cy, wd = centres[nid]
        c = col if not isinstance(lab, tuple) else lab[1]
        _box(pg, cx - wd / 2, cy - 11, wd, 22, lab if isinstance(lab, str) else lab[0], c, size, font, r=5)
    return y0


# ----------------------------------------------------------------------------- the method pages
CARD_ROWS = ["Job", "Core objects", "Lifecycle", "Errors", "Traps", "Docs"]


def card(f, module, rows, color=C.TEAL, size=11.5, gap=14):
    """The library card: the same six questions for every library, in every language."""
    lab_w = 92
    body_w = W - lab_w - 20
    hs = [f.pg.rich_h(rows[k], body_w, size) + 8 for k in CARD_ROWS if k in rows]
    h = 30 + sum(hs) + 6
    y = f.reserve(h + gap)
    pg = f.pg
    pg.rect(L, y, W, h, color, 1.4, fillcolor="#ffffff", r=8)
    pg.rect(L, y, W, 26, color, 0, fillcolor=C.LIGHT[color], r=8)
    pg.text(L + 12, y + 5, "LIBRARY CARD", 10, color, F.BOLD)
    pg.text(L + 110, y + 4, module, 12.5, C.INK, F.MONOB)
    yy = y + 32
    for k in CARD_ROWS:
        if k not in rows:
            continue
        pg.text(L + 12, yy + 1, k, 10, color, F.BOLD)
        hh = pg.rich(L + lab_w + 10, yy, rows[k], body_w, size)
        yy += hh + 8
        pg.line(L + 10, yy - 4, R - 10, yy - 4, "#e6e9ed", 0.6)


def two_ways(f, a, b, verdict=None, run=True, same_output=True, size=8.4, gap=12, ns=None):
    """Two valid solutions side by side. a, b = (title, src). verdict: [(criterion, a_score, b_score)]
    scores 0..5, drawn as bars. Both are executed and must print the same thing."""
    ch = f.ch
    srcs = [textwrap.dedent(s).strip("\n") for _, s in (a, b)]
    outs = []
    if run:
        for s in srcs:
            o, _ = run_src(ch, s, dict(ns or {"__name__": "__main__"}))
            outs.append(o)
            ch.checks += 1
        if same_output and outs[0] != outs[1]:
            raise CheckFailed(f"ch{ch.num} two_ways outputs differ:\n{outs[0]}\n---\n{outs[1]}")
    colw = (W - 14) / 2
    longest = max(len(l) for s in srcs for l in s.split("\n"))
    while size > 7.4 and longest * F.width("M", F.MONO, size) + 14 > colw:
        size -= 0.2
    lh = F.line_h(F.MONO, size) * 1.04
    n = max(len(s.split("\n")) for s in srcs)
    box_h = n * lh + 14
    olines = [o.rstrip("\n").split("\n") if o.strip() else [] for o in outs]
    on = max((len(o) for o in olines), default=0)
    out_h = (on * lh + 12) if on else 0
    vh = (len(verdict) * 17 + 8) if verdict else 0
    y = f.reserve(18 + box_h + out_h + 2 + vh + gap)
    pg = f.pg
    cw = F.width("M", F.MONO, size)
    for k, ((title, _), s) in enumerate(zip((a, b), srcs)):
        x0 = L + k * (colw + 14)
        pg.text(x0 + 2, y, title, 10.5, (C.BLUE, C.PURPLE)[k], F.BOLD)
        pg.rect(x0, y + 16, colw, box_h, CODE_EDGE, 0.8, fillcolor=CODE_BG, r=5)
        lines = s.split("\n")
        if max(len(l) for l in lines) * cw + 14 > colw:
            raise CheckFailed(f"ch{ch.num} two_ways code too wide: {max(lines, key=len)!r}")
        sp = _spans(s)
        for i, line in enumerate(lines):
            _draw_line(pg, x0 + 7, y + 23 + i * lh, line, sp[i], cw, size)
        if out_h:
            oy = y + 16 + box_h + 2
            pg.rect(x0, oy, colw, out_h, OUT_BG, 0, fillcolor=OUT_BG, r=5)
            for i, ol in enumerate(olines[k]):
                while ol and len(ol) * cw > colw - 14:
                    ol = ol[:-2] + "…"
                pg.text(x0 + 7, oy + 6 + i * lh, ol, size, OUT_INK, F.MONO)
    box_h += out_h + 2 if out_h else 0
    if verdict:
        vy = y + 18 + box_h + 6
        half = max(F.width(c, F.BOLD, 9.5) for c, _, _ in verdict) / 2 + 10
        for i, (crit, sa, sb) in enumerate(verdict):
            yy = vy + i * 17
            pg.text(L + W / 2, yy, crit, 9.5, C.GREY, F.BOLD, align="center")
            bw = 9
            for k, sc in enumerate((sa, sb)):
                col = (C.BLUE, C.PURPLE)[k]
                for j in range(5):
                    if k == 0:
                        bx = L + W / 2 - half - (j + 1) * (bw + 2)
                    else:
                        bx = L + W / 2 + half + j * (bw + 2)
                    pg.rect(bx, yy + 1, bw, 9, col, 0.6, fillcolor=col if j < sc else "#ffffff")
    return outs[0] if outs else ""


PASSPORT_Q = ["How does code run?", "Memory model", "Typing", "Control flow", "Functions and scope",
              "Data structures", "Abstraction", "Errors", "Modules and build", "I/O", "Concurrency",
              "Stdlib and tooling"]


def passport(f, answers, color=C.TEAL, size=9.5, highlight=()):
    """The language passport: the same 12 questions for every language. answers: 12 markup strings.
    highlight: question indexes this chapter changed."""
    colw = (W - 10) / 2
    hs = [f.pg.rich_h(a, colw - 14, size) + 24 for a in answers]
    rows = [max(hs[i], hs[i + 1]) for i in range(0, 12, 2)]
    h = 30 + sum(rows) + 6 * len(rows)
    f.need(h + 10)
    y = f.reserve(h + 10)
    pg = f.pg
    pg.rect(L, y, W, 24, color, 0, fillcolor=color, r=6)
    pg.text(L + 12, y + 5, "LANGUAGE PASSPORT: Python", 11.5, "#ffffff", F.BOLD)
    pg.text(R - 12, y + 7, "same 12 questions for C, Java, Rust later", 8.5, "#ffffff", align="right")
    yy = y + 30
    for r, rh in enumerate(rows):
        for k in range(2):
            i = 2 * r + k
            x0 = L + k * (colw + 10)
            hot = i in highlight
            pg.rect(x0, yy, colw, rh, color, 1.4 if hot else 0.7,
                    fillcolor=C.LIGHT[color] if hot else "#ffffff", r=5)
            pg.text(x0 + 7, yy + 4, f"{i + 1}. {PASSPORT_Q[i]}", 9.5, color, F.BOLD)
            pg.rich(x0 + 7, yy + 19, answers[i], colw - 14, size)
        yy += rh + 6


def stamp(f, items, color=C.TEAL, size=10.5):
    """End-of-chapter passport stamp: only the passport questions this chapter answered.
    items: [(question_index, markup answer for Python)]."""
    body_w = W - 24
    hs = [f.pg.rich_h(a, body_w, size) + 18 for _, a in items]
    h = 28 + sum(hs) + 4
    y = f.reserve(h + 12)
    pg = f.pg
    pg.rect(L, y, W, h, color, 1.4, fillcolor="#ffffff", r=8, dash=(5, 3))
    pg.text(L + 12, y + 6, "PASSPORT STAMP", 10, color, F.BOLD)
    pg.text(R - 12, y + 7, "ask the same question of every new language (Appendix B)", 8.5, C.GREY, align="right")
    yy = y + 26
    for (qi, a), hh in zip(items, hs):
        pg.text(L + 12, yy, f"{qi + 1}. {PASSPORT_Q[qi]}", 9.5, color, F.BOLD)
        pg.rich(L + 12, yy + 14, a, body_w, size)
        yy += hh


def practice(f, chnum, color=C.GREEN):
    """'Now practise' box listing this chapter's exercises from the practice repo."""
    from practice.catalog import chapter_exercises
    exs = chapter_exercises(chnum)
    if not exs:
        return
    lines = [f"`{e['id']}`  {{y:{e['kind']}}}  {e['title']}" for e in exs]
    body = "\n".join(lines)
    hdr = f"Run `python -m practice check {exs[0]['id']}` (then the next id). Tests check what your code {{B:does}}, not how it looks, so any correct solution passes. After a pass, `python -m practice alt {exs[0]['id']}` shows other valid solutions and their trade-offs."
    h = f.pg.rich_h(hdr, W - 24, 11) + f.pg.rich_h(body, W - 24, 11, spacing=1.05) + 40
    y = f.reserve(h + 12)
    pg = f.pg
    pg.rect(L, y, W, h, color, 1.4, fillcolor=C.LIGHT[color], r=8)
    needs = sorted({n for e in exs for n in e.get("needs", [])})
    installs = f"needs: pip install {' '.join(needs)}" if needs else "no installs needed"
    pg.text(L + 12, y + 6, f"NOW PRACTISE  (practice/ folder, {installs})", 10.5, color, F.BOLD)
    hh = pg.rich(L + 12, y + 24, hdr, W - 24, 11)
    pg.rich(L + 12, y + 30 + hh, body, W - 24, 11, spacing=1.05)
