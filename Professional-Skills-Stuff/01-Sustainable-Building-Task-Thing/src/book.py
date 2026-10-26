"""Design Outline: the Markdown chapters in Book/ become a print-ready A4 PDF.

Contributors write in Book/chapters/*.md and Book/appendices/*.md. A build never rewrites their
words. It only:

* refreshes the generated tables and charts between  <!-- auto:NAME -->  and  <!-- /auto -->
  lines, writing a chapter file back only if one of those blocks changed;
* fills {{placeholders}}, Harvard citations such as [@un2015] and cross-references such as
  [[Solar power]] while making the PDF (the Markdown keeps them as written, so the numbers are
  always the current ones).

    python src/book.py              # build Book/<title>_Design_Outline.pdf
    python src/book.py --facts      # list every {{placeholder}} with its current value
    python src/book.py --blocks     # list the generated tables and charts

The contributor guide is docs/DESIGN_OUTLINE.md.
"""
import datetime
import html
import json
import re
from collections import defaultdict
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify

import book_blocks as BB
import config as C
from project_facts import facts

BOOK = C.ROOT / "Book"
META = BOOK / "book.json"
REFS = BOOK / "references.json"
THEME = BOOK / "theme" / "book.css"
PARTS = (("chapters", "chapter"), ("appendices", "appendix"))

FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
AUTO_RE = re.compile(r"(<!--\s*auto:([\w-]+)(.*?)-->[ \t]*\n)(.*?)(<!--\s*/auto\s*-->)", re.S)
OPEN_RE = re.compile(r"<!--\s*auto:")
CLOSE_RE = re.compile(r"<!--\s*/auto\s*-->")
ARG_RE = re.compile(r'([\w-]+)=(?:"([^"]*)"|(\S+))')
PLACE_RE = re.compile(r"(\\?)\{\{\s*(\w+)\s*\}\}")
CITE_RE = re.compile(r"\[((?:-?@[\w:.-]+[^;\]]*;?\s*)+)\]")
NARRATIVE_RE = re.compile(r"(?<![\w@\[/.:-])@([A-Za-z][\w:.-]*\w)")
HEAD_RE = re.compile(r"<h([123])([^>]*)>(.*?)</h\1>", re.S)


def rel(p):
    return Path(p).relative_to(C.ROOT).as_posix()


def split_front(text):
    m = FRONT_RE.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    return meta, text[m.end():]


class Chapter:
    def __init__(self, path, kind):
        self.path, self.kind = path, kind
        raw = path.read_bytes()
        self.crlf = b"\r\n" in raw
        self.text = raw.decode("utf-8-sig").replace("\r\n", "\n")
        self.meta, body = split_front(self.text)
        heads = re.findall(r"^# +(.+?)\s*#*\s*$", re.sub(r"```.*?```", "", body, flags=re.S), re.M)
        if len(heads) != 1:
            raise ValueError(f"{rel(path)}: each chapter file needs exactly one top-level '# Title' line "
                             f"(found {len(heads)}); use '##' for sections inside it")
        self.title = heads[0]

    def save(self, text):
        self.text = text
        self.path.write_bytes(text.replace("\n", "\r\n").encode() if self.crlf else text.encode())


class Context:
    def __init__(self):
        self.meta = json.loads(META.read_text())
        self.chapters = [Chapter(p, kind) for folder, kind in PARTS
                         for p in sorted((BOOK / folder).glob("*.md")) if not p.name.startswith("_")]
        if not any(ch.kind == "chapter" for ch in self.chapters):
            raise ValueError("no chapters found in Book/chapters/")
        self.facts = {**facts(), **BB.extra_facts()}
        self.refs = References(REFS)


# ---------------------------------------------------------------------------------------
# Generated blocks: the only part of a chapter file the build ever rewrites
# ---------------------------------------------------------------------------------------
def refresh(ctx):
    changed = []
    for ch in ctx.chapters:
        opened, closed = len(OPEN_RE.findall(ch.text)), len(CLOSE_RE.findall(ch.text))
        if opened != closed:
            raise ValueError(f"{rel(ch.path)}: every '<!-- auto:NAME -->' line needs a '<!-- /auto -->' line after it")
        names = []

        def sub(m):
            name, args = m.group(2), {k: a or b for k, a, b in ARG_RE.findall(m.group(3))}
            if name not in BB.BLOCKS:
                raise ValueError(f"{rel(ch.path)}: there is no generated block called '{name}'. "
                                 f"Available: {', '.join(sorted(BB.BLOCKS))}")
            try:
                body = BB.BLOCKS[name](ctx=ctx, chapter=ch, **args).strip()
            except TypeError as e:
                raise ValueError(f"{rel(ch.path)}: block '{name}' does not take {sorted(args)}") from e
            new = f"{m.group(1)}{body}\n{m.group(5)}"
            if new != m.group(0):
                names.append(name)
            return new
        text = AUTO_RE.sub(sub, ch.text)
        if text != ch.text:
            ch.save(text)
            changed.append(f"{rel(ch.path)} ({', '.join(names)})")
    return changed


# ---------------------------------------------------------------------------------------
# Harvard references
# ---------------------------------------------------------------------------------------
class References:
    REQUIRED = ("key", "authors", "year", "title")

    def __init__(self, path):
        data = json.loads(path.read_text())
        self.items = {}
        for r in data:
            missing = [k for k in self.REQUIRED if not r.get(k)]
            if missing:
                raise ValueError(f"{rel(path)}: reference {r.get('key', r.get('title', '?'))!r} is missing {missing}")
            if r["key"] in self.items:
                raise ValueError(f"{rel(path)}: the key {r['key']!r} is used twice")
            self.items[r["key"]] = r
        self.cited = {}
        groups = defaultdict(list)
        for k, r in self.items.items():
            groups[(self.short(r), str(r["year"]))].append(k)
        self.year = {}
        for (_, y), keys in groups.items():
            keys.sort(key=lambda k: self.items[k]["title"].lower())
            for i, k in enumerate(keys):
                self.year[k] = y + ("abcdefghijklmnopqrstuvwxyz"[i] if len(keys) > 1 else "")

    @staticmethod
    def surname(name):
        return name.split(",")[0].strip()

    def short(self, r):
        a = [self.surname(n) for n in r["authors"]]
        return a[0] if len(a) == 1 else f"{a[0]} and {a[1]}" if len(a) == 2 else f"{a[0]} et al."

    def full(self, r):
        a = r["authors"]
        return a[0] if len(a) == 1 else ", ".join(a[:-1]) + " and " + a[-1]

    def _get(self, key, where):
        if key not in self.items:
            raise ValueError(f"{where}: no reference with the key @{key} in Book/references.json")
        self.cited.setdefault(key, None)
        return self.items[key]

    def process(self, text, where):
        def bracket(m):
            out = []
            for part in m.group(1).split(";"):
                pm = re.match(r"\s*(-?)@([\w:.-]*\w)\s*(?:,\s*(.*?))?\s*$", part)
                if not pm:
                    raise ValueError(f"{where}: cannot read the citation [{m.group(1)}]")
                r = self._get(pm.group(2), where)
                bits = [] if pm.group(1) else [self.short(r)]
                bits.append(self.year[pm.group(2)])
                if pm.group(3):
                    bits.append(pm.group(3))
                out.append(", ".join(bits))
            return "(" + "; ".join(out) + ")"

        def narrative(m):
            if m.group(1) not in self.items:
                return m.group(0)
            r = self._get(m.group(1), where)
            return f"{self.short(r)} ({self.year[m.group(1)]})"
        return NARRATIVE_RE.sub(narrative, CITE_RE.sub(bracket, text))

    def entry(self, k):
        r, e = self.items[k], html.escape
        s = f"{e(self.full(r))} ({e(self.year[k])}) "
        if r.get("type") == "article":
            s += f"‘{e(r['title'])}’, <em>{e(r.get('journal', ''))}</em>"
            if r.get("volume"):
                s += f", {e(str(r['volume']))}" + (f"({e(str(r['issue']))})" if r.get("issue") else "")
            if r.get("pages"):
                s += f", pp. {e(r['pages'])}"
            s += "."
        else:
            s += f"<em>{e(r['title'])}</em>"
            if r.get("version"):
                s += f" ({e(r['version'])})"
            if r.get("medium"):
                s += f" [{e(r['medium'])}]"
            s += "."
        if r.get("edition"):
            s += f" {e(r['edition'])}."
        if r.get("publisher"):
            s += f" {e(r['place'])}: {e(r['publisher'])}." if r.get("place") else f" {e(r['publisher'])}."
        if r.get("detail"):
            s += f" {e(r['detail'])}."
        if r.get("url"):
            s += f' Available at: <a href="{e(r["url"])}">{e(r["url"])}</a>'
            s += f" (Accessed: {e(r['accessed'])})." if r.get("accessed") else "."
        return s

    def section_html(self):
        keys = sorted(self.cited, key=lambda k: (self.full(self.items[k]).lower(), self.year[k]))
        return "".join(f'<p class="ref">{self.entry(k)}</p>' for k in keys)


# ---------------------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------------------
def fill(text, values, where):
    def sub(m):
        if m.group(1):
            return "{{" + m.group(2) + "}}"
        if m.group(2) not in values:
            raise ValueError(f"{where}: unknown placeholder {{{{{m.group(2)}}}}}. "
                             f"Available: {', '.join(sorted(values))}")
        return values[m.group(2)]
    return PLACE_RE.sub(sub, text)


def _plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


class Renderer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.n_chapter = self.n_appendix = self.n_fig = self.n_tab = 0
        self.toc = []
        self.words = 0

    def chapter(self, idx, ch):
        where = rel(ch.path)
        numbered = ch.kind == "appendix" or ch.meta.get("numbered", "yes").lower() not in ("no", "false")
        _, body = split_front(ch.text)
        body = self.ctx.refs.process(fill(body, self.ctx.facts, where), where)
        prefix = f"s{idx}-"
        md = markdown.Markdown(extensions=["extra", "toc", "sane_lists", "smarty", "admonition"],
                               extension_configs={"toc": {"slugify": lambda v, sep: prefix + slugify(v, sep)}})
        out = md.convert(body)
        out = self._images(out, ch)
        out = self._tables(out)
        out = self._headings(out, ch, numbered)
        authors = ch.meta.get("authors", "").strip()
        if authors:
            names = [a.strip() for a in authors.split(",") if a.strip()]
            who = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
            out = re.sub(r"(</h1>)", rf'\1<p class="byline">Written by {html.escape(who)}</p>', out, count=1)
        if ch.kind == "chapter":
            text = re.sub(r"<(table|figure)\b.*?</\1>", " ", out, flags=re.S)
            self.words += len(re.findall(r"[A-Za-z0-9£%][\w'’£%.,-]*", _plain(text)))
        cls = f"chapter {ch.kind} {'numbered' if numbered else 'unnumbered'}"
        return f'<section class="{cls}" id="sec{idx}">{out}</section>'

    def _images(self, out, ch):
        def resolve(m):
            src = html.unescape(m.group(1))
            if re.match(r"^(https?|data|file):", src):
                return m.group(0)
            p = (ch.path.parent / src).resolve()
            if not p.exists():
                raise ValueError(f"{rel(ch.path)}: image not found: {src}")
            return f'src="{p.as_uri()}"'
        out = re.sub(r'src="([^"]+)"', resolve, out)

        def fig(m):
            img = m.group(1)
            alt = re.search(r'alt="([^"]*)"', img)
            self.n_fig += 1
            cap = alt.group(1) if alt else ""
            return (f'<figure id="fig-{self.n_fig}">{img}<figcaption><span class="label">Figure {self.n_fig}</span> '
                    f"{cap}</figcaption></figure>")
        return re.sub(r"<p>\s*(<img\b[^>]*>)\s*</p>", fig, out)

    def _tables(self, out):
        def cap(m):
            self.n_tab += 1
            return f'<table><caption><span class="label">Table {self.n_tab}</span> {m.group(1)}</caption>'
        out = re.sub(r"<p>Table:\s*(.*?)</p>\s*<table>", cap, out, flags=re.S)
        return re.sub(r"<p>Table:\s*(.*?)</p>", lambda m: f'<p class="error">Table caption without a table: {m.group(1)}</p>', out)

    def _headings(self, out, ch, numbered):
        state = {"h2": 0}
        if numbered and ch.kind == "appendix":
            self.n_appendix += 1
            label = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[self.n_appendix - 1]
        elif numbered:
            self.n_chapter += 1
            label = str(self.n_chapter)

        def sub(m):
            level, attrs, inner = int(m.group(1)), m.group(2), m.group(3)
            hid = re.search(r'id="([^"]+)"', attrs)
            hid = hid.group(1) if hid else ""
            num = ""
            if numbered and level == 1:
                num = f"Appendix {label}" if ch.kind == "appendix" else label
            elif numbered and level == 2:
                state["h2"] += 1
                num = f"{label}.{state['h2']}"
            if level <= 2 and hid:
                self.toc.append((level, hid, num, _plain(inner), ch.kind))
            span = f'<span class="num">{num}</span> ' if num else ""
            return f"<h{level}{attrs}>{span}{inner}</h{level}>"
        return HEAD_RE.sub(sub, out)

    def xrefs(self, out):
        """[[Heading title]] -> 'Section 4.2' (or 'Appendix A'), linked; resolved once every chapter is numbered."""
        def norm(s):
            return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'")).strip().lower()
        index = {}
        for level, hid, num, title, kind in self.toc:
            label = (num if num.startswith("Appendix") else f"Appendix {num}" if kind == "appendix"
                     else f"Section {num}") if num else f"‘{title}’"
            index.setdefault(norm(title), (hid, label))

        def sub(m):
            key = norm(_plain(m.group(1)))
            if key not in index:
                raise ValueError(f"cross-reference [[{_plain(m.group(1))}]] does not match any chapter or section "
                                 f"heading (check the spelling against the Contents page)")
            hid, label = index[key]
            return f'<a class="xref" href="#{hid}">{label}</a>'
        return re.sub(r"\[\[(.+?)\]\]", sub, out)

    def references(self):
        refs = self.ctx.refs.section_html()
        if not refs:
            return ""
        self.toc.append((1, "references", "", "References", "chapter"))
        return f'<section class="chapter references unnumbered"><h1 id="references">References</h1>{refs}</section>'

    def toc_html(self):
        items = []
        for level, hid, num, title, kind in self.toc:
            if level == 2 and kind == "appendix":
                continue
            items.append(f'<li class="l{level} {kind}"><a href="#{hid}"><span class="num">{html.escape(num)}</span>'
                         f'<span class="t">{html.escape(title)}</span></a></li>')
        return f'<nav class="toc"><h1 class="toc-title">Contents</h1><ul>{"".join(items)}</ul></nav>'


def cover_html(ctx, words):
    m, e = ctx.meta, html.escape
    img = ""
    if m.get("cover_image"):
        p = (BOOK / m["cover_image"]).resolve()
        if not p.exists():
            raise ValueError(f"Book/book.json: cover_image not found: {m['cover_image']}")
        credit = f'<div class="cover-credit">{e(m["cover_credit"])}</div>' if m.get("cover_credit") else ""
        img = f'<div class="cover-image" style="background-image:url({p.as_uri()})"></div>{credit}'
    rows = "".join(
        f'<tr><td class="name{"" if a.get("name") else " todo"}">{e(a.get("name") or "Name to be added")}</td>'
        f'<td>{e(a.get("student_id", ""))}</td><td class="role">{e(a.get("role", ""))}</td></tr>'
        for a in m.get("authors", []))
    team = e(m.get("team_name") or "")
    date = m.get("date") or datetime.date.today().strftime("%-d %B %Y")
    meta_bits = [f"<span>{e(date)}</span>"]
    if m.get("version"):
        meta_bits.append(f"<span>Version {e(m['version'])}</span>")
    if m.get("lab_leader"):
        meta_bits.append(f"<span>Lab leader: {e(m['lab_leader'])}</span>")
    meta_bits.append(f"<span>{words:,} words (excluding tables, captions, references and appendices)</span>")
    zig = "".join(f"L{x + 9},0 L{x + 9},6 " for x in range(0, 180, 9))
    return f"""
<section class="cover">
  <div class="cover-band"><span>{e(m.get('institution', ''))}</span><span>{e(m.get('course', ''))}</span></div>
  <div class="cover-body">
    <div class="cover-module">{e(m.get('module', ''))}</div>
    <h1 class="cover-title">{e(m.get('title', ''))}</h1>
    <svg class="cover-zig" viewBox="0 0 180 7" preserveAspectRatio="none"><path d="M0,6 {zig}" fill="none" stroke="#c8742c" stroke-width="1.4"/></svg>
    <p class="cover-subtitle">{e(m.get('subtitle', ''))}</p>
  </div>
  {img}
  <div class="cover-foot">
    <div class="cover-doc">{e(m.get('document', ''))}</div>
    <div class="cover-team-name">{('Team ' + team) if team else '<span class="todo">Team name to be added</span>'}</div>
    <table class="cover-team"><thead><tr><th>Name</th><th>Student number</th><th>Role</th></tr></thead>
      <tbody>{rows}</tbody></table>
    <div class="cover-meta">{' · '.join(meta_bits)}</div>
  </div>
</section>"""


def page_css(meta):
    """Running header text, and a wider binding margin (mirrored on left pages if printed double-sided)."""
    running = f"{meta.get('title', '')} · {meta.get('document', '')}".replace("\\", "\\\\").replace('"', '\\"')
    binding, outer = 25, 17
    css = f'@page {{ margin-left: {binding}mm; margin-right: {outer}mm; @top-left {{ content: "{running}"; }} }}\n'
    if meta.get("double_sided", True):
        css += f"@page :left {{ margin-left: {outer}mm; margin-right: {binding}mm; }}\n"
    return css


def build():
    from weasyprint import CSS, HTML
    from weasyprint.text.fonts import FontConfiguration

    ctx = Context()
    changed = refresh(ctx)
    for c in changed:
        print(f"updated generated blocks in {c}")
    r = Renderer(ctx)
    body = [r.chapter(i, ch) for i, ch in enumerate(ctx.chapters) if ch.kind == "chapter"]
    refs = r.references()
    body += [refs] + [r.chapter(i, ch) for i, ch in enumerate(ctx.chapters) if ch.kind == "appendix"]
    body = r.xrefs("".join(body))
    m = ctx.meta
    names = [a["name"] for a in m.get("authors", []) if a.get("name")]
    doc = f"""<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8">
<title>{html.escape(m.get('title', ''))}: {html.escape(m.get('document', ''))}</title>
<meta name="author" content="{html.escape(', '.join(names) or m.get('team_name', ''))}">
<meta name="description" content="{html.escape(m.get('subtitle', ''))}">
<meta name="keywords" content="sustainable design, net zero, UN SDGs, NTU Clifton">
</head><body>{cover_html(ctx, r.words)}{r.toc_html()}{body}</body></html>"""

    uncited = sorted(set(ctx.refs.items) - set(ctx.refs.cited))
    if uncited:
        print(f"note: in Book/references.json but not cited anywhere (left out of the list): {', '.join(uncited)}")
    if not names:
        print("note: no author names yet; fill in Book/book.json")
    todo = [f"{ch.path.name} ({n})" for ch in ctx.chapters if (n := len(re.findall(r"^!!! contribute", ch.text, re.M)))]
    if todo:
        print(f"note: 'contribute' boxes still waiting to be written: {', '.join(todo)}")
    out = BOOK / (m.get("output") or f"{m.get('title', 'Book')} {m.get('document', '')}".strip().replace(" ", "_") + ".pdf")
    (BOOK / "build").mkdir(exist_ok=True)
    (BOOK / "build" / "book.html").write_text(doc)
    fonts = FontConfiguration()
    rendered = HTML(string=doc, base_url=str(BOOK)).render(
        stylesheets=[CSS(filename=str(THEME), font_config=fonts), CSS(string=page_css(m), font_config=fonts)],
        font_config=fonts)
    rendered.write_pdf(out)
    print(f"{rel(out)}: {len(rendered.pages)} pages, {r.words:,} words, {r.n_fig} figures, {r.n_tab} tables, "
          f"{len(ctx.refs.cited)} references")
    return out


def list_facts():
    values = {**facts(), **BB.extra_facts()}
    for k in sorted(values):
        print(f"{{{{{k}}}}}".ljust(28), values[k])


def list_blocks():
    import inspect
    for name, fn in sorted(BB.BLOCKS.items()):
        args = [f'{p.name}="{p.default}"' if p.default is not None else f"{p.name} (automatic)"
                for p in inspect.signature(fn).parameters.values() if p.name not in ("ctx", "chapter")]
        doc = (fn.__doc__ or "").strip().splitlines()
        print(f"<!-- auto:{name} -->".ljust(34), ", ".join(args))
        if doc:
            print(" " * 34, doc[0])


if __name__ == "__main__":
    import sys
    if "--facts" in sys.argv:
        raise SystemExit(list_facts())
    if "--blocks" in sys.argv:
        raise SystemExit(list_blocks())
    try:
        build()
    except ValueError as err:
        raise SystemExit(f"Design Outline not built: {err}") from None
