"""Chapter container: pages, a movable writing position, registries and checks."""
import sympy as sp

from . import canvas as C
from . import fonts as F
from .xopp import save as xsave

TOP = 52.0
BOTTOM = 792.0
LEFT = 50.0
WIDTH = 495.0


class CheckFailed(Exception):
    pass


class Flow:
    """A writing position that moves down the page and turns pages when full.

    It is only a convenience for running text; chapters place drawings freely."""

    def __init__(self, ch, x=LEFT, w=WIDTH, top=TOP, bottom=BOTTOM):
        self.ch, self.x, self.w, self.top, self.bottom = ch, x, w, min(top, TOP), bottom
        if not ch.pages:
            ch.new_page()
        self.y = top

    @property
    def pg(self):
        return self.ch.pages[-1]

    def new_page(self, **kw):
        self.ch.new_page(**kw)
        self.y = self.top
        return self.pg

    def need(self, h):
        if self.y + h > self.bottom:
            self.new_page()
            return True
        return False

    def room(self):
        return self.bottom - self.y

    def gap(self, n=10):
        self.y += n

    def reserve(self, h):
        """Make sure h points are free (turn the page if not); return the top y."""
        self.need(h)
        y0 = self.y
        self.y += h
        return y0

    def p(self, markup, size=13, color=C.INK, gap=9, x=None, w=None, align="left", spacing=1.0,
          font=F.SANS):
        x = self.x if x is None else x
        w = self.w if w is None else w
        h = self.pg.rich_h(markup, w, size, spacing)
        self.need(h)
        self.pg.rich(x, self.y, markup, w, size, color, font, align, spacing)
        self.y += h + gap
        return h

    def text(self, s, size=13, color=C.INK, font=F.SANS, gap=8, x=None, w=None, align="left"):
        x = self.x if x is None else x
        w = self.w if w is None else w
        lines = F.wrap(s, font, size, w)
        h = F.line_h(font, size) * len(lines)
        self.need(h)
        self.pg.text(x, self.y, s, size, color, font, w, align)
        self.y += h + gap
        return h

    def bullet(self, markup, size=13, color=C.INK, gap=6, indent=18, dot=None):
        x = self.x + indent
        w = self.w - indent
        h = self.pg.rich_h(markup, w, size)
        self.need(h)
        self.pg.dot(self.x + 7, self.y + size * 0.62, 2.4, dot or getattr(self.ch, "accent", C.INK))
        self.pg.rich(x, self.y, markup, w, size, color)
        self.y += h + gap
        return h

    def note(self, s, size=18, color=C.RED, gap=6, x=None, w=None, align="left"):
        return self.text(s, size, color, F.HAND, gap, x, w, align)

    def eq(self, latex, size=18, color=C.INK, align="center", gap=10, x=None):
        w, h, _ = self.pg.eq_size(latex, size, True, color)
        self.need(h)
        if align == "center":
            xx = (self.x + self.w / 2) if x is None else x
        else:
            xx = self.x if x is None else x
        self.pg.eq(xx, self.y, latex, size, color, align=align)
        self.y += h + gap
        return w, h

    def rule(self, color="#cfd4da", gap=12, width=0.8):
        self.need(gap * 2)
        self.y += gap
        self.pg.line(self.x, self.y, self.x + self.w, self.y, color, width)
        self.y += gap


REGISTRY = {"terms": [], "symbols": [], "formulas": [], "concepts": {}}


class Chapter:
    def __init__(self, num, title, short, slug, accent=C.BLUE):
        self.num, self.title, self.short, self.slug, self.accent = num, title, short, slug, accent
        self.pages = []
        self.checks = 0
        self.terms, self.symbols, self.formulas = [], [], []
        self.footer = True

    # ------------------------------------------------------------ pages
    def new_page(self, bg="#ffffff"):
        pg = C.Page(self, bg)
        pg.number = len(self.pages) + 1
        self.pages.append(pg)
        return pg

    @property
    def pg(self):
        return self.pages[-1]

    def flow(self, **kw):
        return Flow(self, **kw)

    # ------------------------------------------------------------ registries
    def term(self, word, meaning, page=None):
        self.terms.append(dict(word=word, meaning=meaning, ch=self.num, short=self.short,
                               page=page or len(self.pages)))

    def symbol(self, latex, say, meaning, page=None):
        self.symbols.append(dict(latex=latex, say=say, meaning=meaning, ch=self.num,
                                 short=self.short, page=page or len(self.pages)))

    def formula(self, latex, label, page=None):
        self.formulas.append(dict(latex=latex, label=label, ch=self.num, short=self.short,
                                  page=page or len(self.pages)))

    # ------------------------------------------------------------ answer checks
    def check(self, got, expected, what=""):
        """Assert two maths expressions are equal (sympy). Strings are parsed."""
        if isinstance(got, dict) or isinstance(expected, dict):
            if dict(got) != dict(expected):
                raise CheckFailed(f"ch{self.num} check failed [{what}]: {got} != {expected}")
            self.checks += 1
            return
        if isinstance(got, (list, tuple)) or isinstance(expected, (list, tuple)):
            if list(got) != list(expected):
                raise CheckFailed(f"ch{self.num} check failed [{what}]: {got} != {expected}")
            self.checks += 1
            return
        g = sp.sympify(got) if isinstance(got, str) else got
        e = sp.sympify(expected) if isinstance(expected, str) else expected
        if isinstance(g, sp.MatrixBase) or isinstance(e, sp.MatrixBase):
            ok = g.shape == e.shape and sp.simplify(g - e).is_zero_matrix
        else:
            ok = sp.simplify(g - e) == 0
        if not ok:
            try:
                ok = abs(float(sp.N(g - e))) < 1e-9
            except (TypeError, ValueError):
                ok = False
        if not ok:
            raise CheckFailed(f"ch{self.num} check failed [{what}]: {got} != {expected}")
        self.checks += 1

    def check_num(self, got, expected, tol=0.006, what=""):
        if abs(float(got) - float(expected)) > tol:
            raise CheckFailed(f"ch{self.num} numeric check failed [{what}]: {got} vs {expected}")
        self.checks += 1

    def check_true(self, cond, what=""):
        if not cond:
            raise CheckFailed(f"ch{self.num} check failed [{what}]")
        self.checks += 1

    # ------------------------------------------------------------ output
    def finalize(self):
        if not self.footer:
            return
        n = len(self.pages)
        for pg in self.pages:
            s = f"{self.num}  ·  {self.short}  ·  page {pg.number} of {n}" if self.num != "" else \
                f"{self.short}  ·  page {pg.number} of {n}"
            pg.text(pg.W / 2, 812, s, 8.5, "#9aa0a6", align="center", solid=False)

    def overlaps(self, tol=1.5):
        problems = []
        for pg in self.pages:
            bx = pg.boxes
            for i in range(len(bx)):
                (a0, b0, a1, b1), la = bx[i]
                if a0 < 8 or b0 < 8 or a1 > pg.W - 8 or b1 > pg.H - 8:
                    problems.append(f"p{pg.number}: off page: {la!r} {tuple(round(v) for v in bx[i][0])}")
                for j in range(i + 1, len(bx)):
                    (c0, d0, c1, d1), lb = bx[j]
                    if min(a1, c1) - max(a0, c0) > tol and min(b1, d1) - max(b0, d0) > tol:
                        problems.append(f"p{pg.number}: overlap {la!r} <-> {lb!r}")
        return problems

    def save(self, path):
        xsave([p.x for p in self.pages], path, title=f"{self.num} {self.title}")
