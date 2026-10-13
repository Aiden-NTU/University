"""The back of the book, built from what the chapters registered while they were built:
a Word Finder (dictionary with thumb tabs), a Symbol Phrasebook (see it, say it, mean it), Formula
Pages grouped by Part, an Answer Key that doubles as a progress tracker, and the Slide Errata."""
import ast
import glob
import json
import os

from generator import canvas as C
from generator import fonts as F
from generator.book import BOTTOM, TOP
from content.errata import ERRATA
from content.kit import L, R, W, flow
from content.toc import CHAPTERS, PARTS

ORDER = 39
NUM = 39
TITLE = "The back of the book"
SHORT = "Back of the book"
SLUG = "Appendices"
ACCENT = C.INK
REQUIRES = []
INTRODUCES = []

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(HERE, "build", "registry")
PAPER = "#fffdf8"


def part_colour(chnum):
    for _, _, col, rg in PARTS:
        if chnum in rg:
            return col
    return C.BROWN


def part_of(chnum):
    for tag, name, col, rg in PARTS:
        if chnum in rg:
            return tag, name, col
    return "Start here", "The language of maths", C.BROWN


def load_registry():
    regs = []
    for p in sorted(glob.glob(os.path.join(REG, "*.json"))):
        d = json.load(open(p))
        if d["order"] < ORDER:
            regs.append(d)
    regs.sort(key=lambda d: d["order"])
    return regs


def fit(pg, latex, size, maxw, lo=8):
    while size > lo and pg.eq_size(latex, size)[0] > maxw:
        size -= 0.5
    return size


def loc(e):
    return f"{e['ch']}·p{e['page']}"


def band(f, text, col, sub=""):
    """A full-width coloured strip announcing a Part."""
    f.need(70)
    y_ = f.reserve(34)
    pg = f.pg
    pg.rect(L - 6, y_, W + 12, 26, col, 0.1, fillcolor=col, r=4)
    pg.text(L + 4, y_ + 4, text, 13, "#ffffff", F.BOLD)
    if sub:
        pg.text(L + 4, y_ + 6, sub, 10.5, "#ffffff", F.BOLD, w=W - 8, align="right")


def heading(f, title, blurb, col=C.INK):
    if f.y > f.top + 5:
        f.new_page()
    pg = f.pg
    pg.text(L, f.y, title, 26, col, F.BOLD)
    f.y += 40
    f.p(blurb, 12.5, C.GREY, gap=14)
    return pg.number


# ----------------------------------------------------------------------------- title
def title_page(ch):
    pg = ch.new_page(bg=PAPER)
    pg.text(L, 60, "Appendices", 16, C.GREY, F.BOLD)
    pg.text(L, 82, "The back of the book", 40, C.INK, F.BOLD)
    pg.note(L, 138, "look it up, say it, check it", C.BROWN, 22)
    ch._title = pg
    f = ch.flow(top=520)
    f.p("Everything here was collected automatically while the chapters were being built, so every page "
        "reference points to the place where the idea is {B:properly explained}, with pictures. References "
        "look like {w:24·p3}: Chapter 24, page 3 of that chapter's file.", 13.5, gap=10)
    f.p("Use the drawers above like a filing cabinet. In Xournal++ you can also tick, circle and scribble on "
        "every page here.", 13.5)


def cabinet(ch, starts):
    pg = ch._title
    x0, y0, dw, dh = L + 60, 190, 375, 56
    pg.rect(x0 - 14, y0 - 14, dw + 28, dh * len(starts) + 22, C.BROWN, 1.6, fillcolor="#f3e6d6", r=6)
    for k, (name, what, page, col) in enumerate(starts):
        yy = y0 + k * dh
        pg.rect(x0, yy, dw, dh - 8, col, 1.4, fillcolor=C.LIGHT[col], r=4)
        pg.rect(x0 + dw - 150, yy + 18, 36, 9, C.INK, 1.0, fillcolor="#ffffff", r=4)
        pg.text(x0 + 14, yy + 6, name, 14, col, F.BOLD)
        pg.text(x0 + 14, yy + 25, what, 9.5, C.INK)
        pg.text(x0 + dw - 90, yy + 10, f"page {page}", 13, col, F.BOLD, w=78, align="right")


# ----------------------------------------------------------------------------- word finder
class Columns:
    """Two newspaper columns that fill left then right, then turn the page."""

    def __init__(self, f, gap=15):
        self.f, self.col, self.cw = f, 0, (W - gap) / 2
        self.xs = [L, L + self.cw + gap]
        self.top = f.y
        self.y = f.y

    def place(self, h):
        if self.y + h > BOTTOM:
            if self.col == 0:
                self.col, self.y = 1, self.top
            else:
                self.f.new_page()
                self.col, self.top, self.y = 0, TOP, TOP
        x, y = self.xs[self.col], self.y
        self.y += h
        return self.f.pg, x, y


def word_finder(ch, regs):
    f = flow(ch)
    first = heading(f, "Word Finder", "Every maths word in the book, A to Z, with a one-line meaning and where it is "
                    "explained. Numbers like 36·p3 mean Chapter 36, page 3. The thumb tabs on the right edge work "
                    "like a dictionary's.")
    merged = {}
    for d in regs:
        for t in d["terms"]:
            k = t["word"].strip().lower()
            if k not in merged:
                merged[k] = dict(word=t["word"].strip(), meaning=t["meaning"], locs=[t])
            else:
                merged[k]["locs"].append(t)

    def key(w):
        s = w.lstrip("\"'(+−-∫δΣ√|")
        return (0 if s[:1].isalpha() else 1, s.lower())

    entries = sorted(merged.values(), key=lambda e: key(e["word"]))
    cols = Columns(f)
    cw = cols.cw
    letters_on = {}
    current = None
    for e in entries:
        s = e["word"].lstrip("\"'(+−-∫δΣ√|")
        letter = s[:1].upper() if s[:1].isalpha() else "#"
        locs = ", ".join(dict.fromkeys(loc(t) for t in e["locs"]))
        lw = F.width(locs, F.BOLD, 9) + 8
        wl = F.wrap(e["word"], F.BOLD, 10.5, cw - lw)
        ml = F.wrap(e["meaning"], F.SANS, 9, cw - 8)
        h = F.line_h(F.BOLD, 10.5) * len(wl) + F.line_h(F.SANS, 9) * len(ml) + 7
        if letter != current:
            pg, x, y = cols.place(34 + h)
            pg.circle(x + 13, y + 13, 13, C.BROWN, 1.4, fillcolor=C.LIGHT[C.BROWN])
            pg.text(x, y + 4, letter, 15, C.BROWN, F.BOLD, w=26, align="center")
            pg.line(x + 32, y + 13, x + cw, y + 13, C.BROWN, 0.8)
            y += 34
            current = letter
        else:
            pg, x, y = cols.place(h)
        letters_on.setdefault(pg.number, [])
        if letter not in letters_on[pg.number]:
            letters_on[pg.number].append(letter)
        col = part_colour(e["locs"][0]["ch"])
        pg.text(x, y, e["word"], 10.5, C.INK, F.BOLD, w=cw - lw)
        pg.text(x + cw - lw + 8, y + 1, locs, 9, col, F.BOLD, w=lw - 8, align="right")
        pg.text(x + 8, y + F.line_h(F.BOLD, 10.5) * len(wl), e["meaning"], 9, "#444444", w=cw - 8)
    f.y = BOTTOM
    alphabet = [chr(c) for c in range(65, 91)] + ["#"]
    for pnum, ls in letters_on.items():
        pg = ch.pages[pnum - 1]
        i0 = alphabet.index(ls[0])
        lab_ = ls[0] if len(ls) == 1 else f"{ls[0]}–{ls[-1]}"
        ty = 70 + i0 * 26
        pg.rect(568, ty, 27, 40, C.BROWN, 0.1, fillcolor=C.BROWN, r=4)
        pg.text(568, ty + 12, lab_, 9 if len(lab_) > 1 else 12, "#ffffff", F.BOLD, w=27, align="center",
                solid=False)
    return first, len(entries)


# ----------------------------------------------------------------------------- symbols
def phrasebook(ch, regs):
    f = flow(ch)
    first = heading(f, "Symbol Phrasebook", "See it, say it, mean it. The middle column is how you'd read the symbol out "
                    "loud; saying it is half of understanding it (Chapter 0).", C.BLUE)
    last_part = None
    n = 0
    for d in regs:
        for s in d["symbols"]:
            tag, name, col = part_of(s["ch"])
            if tag != last_part:
                band(f, f"{tag}: {name}", col)
                last_part = tag
            pg = f.pg
            size = fit(pg, s["latex"], 15, 125)
            w_, h_, _ = pg.eq_size(s["latex"], size)
            say_h = F.line_h(F.HAND, 14) * len(F.wrap(s["say"], F.HAND, 14, 175))
            mean_lines = F.wrap(s["meaning"], F.SANS, 9.5, 160)
            mean_h = F.line_h(F.SANS, 9.5) * len(mean_lines) + 14
            rh = max(h_, say_h, mean_h) + 10
            y_ = f.reserve(rh)
            pg = f.pg
            pg.eq(L, y_ + (rh - 10 - h_) / 2, s["latex"], size, col)
            pg.note(L + 140, y_, s["say"], C.INK, 14, w=175)
            pg.text(L + 330, y_, s["meaning"], 9.5, "#444444", w=160)
            pg.text(L + 330, y_ + mean_h - 13, loc(s), 8.5, col, F.BOLD)
            pg.line(L, y_ + rh - 4, R, y_ + rh - 4, "#e8e0d0", 0.6)
            n += 1
    return first, n


# ----------------------------------------------------------------------------- formulas
def formula_pages(ch, regs):
    f = flow(ch)
    first = heading(f, "Formula Pages", "Every boxed formula from the book in one place, Part by Part. The label says "
                    "what it's for; the reference says where it's explained and practised.", C.RED)
    last_part = None
    n = 0
    for d in regs:
        if not d["formulas"]:
            continue
        for fm in d["formulas"]:
            tag, name, col = part_of(fm["ch"])
            if tag != last_part:
                band(f, f"{tag}: {name}", col)
                last_part = tag
            pg = f.pg
            size = fit(pg, fm["latex"], 15, 330)
            w_, h_, _ = pg.eq_size(fm["latex"], size)
            lab_lines = F.wrap(fm["label"], F.BOLD, 10.5, 140)
            lab_h = F.line_h(F.BOLD, 10.5) * len(lab_lines) + 14
            rh = max(h_, lab_h) + 12
            y_ = f.reserve(rh)
            pg = f.pg
            pg.rect(L - 6, y_ + 2, 3, rh - 10, col, 0.1, fillcolor=col)
            pg.text(L + 4, y_ + 2, fm["label"], 10.5, col, F.BOLD, w=140)
            pg.text(L + 4, y_ + lab_h - 10, f"{CHAPTERS.get(fm['ch'], '')} · {loc(fm)}", 8, C.GREY, w=140)
            pg.eq(L + 160, y_ + (rh - 12 - h_) / 2 + 2, fm["latex"], size)
            pg.line(L + 4, y_ + rh - 4, R, y_ + rh - 4, "#eeeeee", 0.6)
            n += 1
    return first, n


# ----------------------------------------------------------------------------- answers
def practice_groups():
    out = {}
    for p in sorted(glob.glob(os.path.join(HERE, "content", "c[0-9]*.py"))):
        base = os.path.basename(p)
        if base.startswith("c39"):
            continue
        num = int(base[1:3])
        tree = ast.parse(open(p).read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "your_turn":
                for nd in ast.walk(node):
                    if isinstance(nd, ast.Assign) and getattr(nd.targets[0], "id", None) == "groups":
                        out[num] = ast.literal_eval(nd.value)
    return out


def answer_key(ch):
    f = flow(ch)
    first = heading(f, "Answer Key and Tracker", "The answers to every \"Your turn\" page, without the questions, so "
                    "you can check a whole chapter at a glance. Each small circle is one question: tick it in "
                    "Xournal++ when you get it right, and watch the book fill up.", C.GREEN)
    groups = practice_groups()
    total = 0
    for num in sorted(CHAPTERS):
        col = part_colour(num)
        f.need(80)
        y_ = f.reserve(30)
        pg = f.pg
        pg.circle(L + 12, y_ + 11, 12, col, 1.4, fillcolor=C.LIGHT[col])
        pg.text(L, y_ + 4, str(num), 10.5, col, F.BOLD, w=24, align="center")
        pg.text(L + 32, y_ + 2, CHAPTERS[num], 14, col, F.BOLD)
        if num not in groups:
            f.p("Worked answers, line by line, are on the last pages of this chapter itself.", 11, C.GREY,
                x=L + 32, w=W - 32, gap=12)
            continue
        for title, qs, ans in groups[num]:
            al = F.wrap(ans, F.SANS, 10, W - 50)
            h = 18 + F.line_h(F.SANS, 10) * len(al) + 8
            y_ = f.reserve(h)
            pg = f.pg
            for k in range(len(qs)):
                pg.circle(L + 38 + k * 13, y_ + 7, 4.5, col, 1.0)
            total += len(qs)
            pg.text(L + 44 + len(qs) * 13, y_, title, 10.5, C.INK, F.BOLD)
            pg.text(L + 32, y_ + 18, ans, 10, "#444444", w=W - 50)
        f.gap(8)
    return first, total


# ----------------------------------------------------------------------------- errata
def errata(ch):
    f = flow(ch)
    first = heading(f, "Slide Errata", "Small slips found on the lecture slides while writing this book. Each one is "
                    "explained where it comes up; here they are all together so you can correct your own copies. "
                    "Grey with a red wavy line: what the slide says. Green: what it should say.", C.RED)
    order = sorted(ERRATA, key=lambda e: (int(e[0][1:]), e[1]))
    for lec, where, wrong, right, chap in order:
        pg = f.pg
        maxw = W - 100
        s1 = fit(pg, wrong, 14, maxw)
        s2 = fit(pg, right, 14, maxw)
        w1, h1, _ = pg.eq_size(wrong, s1)
        w2, h2, _ = pg.eq_size(right, s2)
        h = 24 + h1 + 14 + h2 + 16
        y_ = f.reserve(h)
        pg = f.pg
        pg.rect(L, y_ + 2, 38, 18, C.RED, 0.1, fillcolor=C.RED, r=4)
        pg.text(L, y_ + 4, lec, 10, "#ffffff", F.BOLD, w=38, align="center")
        pg.text(L + 48, y_ + 3, where, 11, C.INK, F.BOLD, w=W - 170)
        pg.text(R - 120, y_ + 4, f"see Chapter {chap}", 10, part_colour(chap), F.BOLD, w=120, align="right")
        yy = y_ + 26
        pg.text(L + 48, yy + h1 / 2 - 7, "slide:", 9, C.GREY, F.BOLD)
        pg.eq(L + 90, yy, wrong, s1, C.GREY)
        pg.underline(L + 88, yy + h1 + 3, w1 + 4, C.RED, 1.4, wave=True)
        pg.xmark(L + 100 + w1, yy + h1 / 2 - 6, 10, C.RED, 2.0)
        yy += h1 + 14
        pg.text(L + 48, yy + h2 / 2 - 7, "fix:", 9, C.GREEN, F.BOLD)
        pg.eq(L + 90, yy, right, s2, C.GREEN)
        pg.line(L, y_ + h - 6, R, y_ + h - 6, "#eeeeee", 0.6)
    return first, len(order)


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    regs = load_registry()
    p1, nw = word_finder(ch, regs)
    p2, ns = phrasebook(ch, regs)
    p3, nf = formula_pages(ch, regs)
    p4, na = answer_key(ch)
    p5, ne = errata(ch)
    cabinet(ch, [("Word Finder", f"{nw} words, A to Z, with meanings", p1, C.BROWN),
                 ("Symbol Phrasebook", f"{ns} symbols: see it, say it, mean it", p2, C.BLUE),
                 ("Formula Pages", f"{nf} formulas, Part by Part", p3, C.RED),
                 ("Answer Key and Tracker", f"{na} practice questions to tick off", p4, C.GREEN),
                 ("Slide Errata", f"{ne} slips on the lecture slides, corrected", p5, C.PURPLE)])
