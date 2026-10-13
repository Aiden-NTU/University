"""Native Xournal++ graphs: axes, grids and curves drawn as pen strokes."""
import math

from . import canvas as C


def nice_ticks(a, b, step):
    k0 = math.ceil(a / step - 1e-9)
    k1 = math.floor(b / step + 1e-9)
    return [k * step for k in range(k0, k1 + 1)]


def fmt(v):
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:g}"


class Axes:
    def __init__(self, pg, x, y, w, h, xr, yr):
        self.pg = pg
        self.x0, self.y0, self.w, self.h = x, y, w, h
        self.xa, self.xb = xr
        self.ya, self.yb = yr

    def X(self, v):
        return self.x0 + (v - self.xa) / (self.xb - self.xa) * self.w

    def Y(self, v):
        return self.y0 + self.h - (v - self.ya) / (self.yb - self.ya) * self.h

    def P(self, x, y):
        return (self.X(x), self.Y(y))

    def inside(self, x, y, pad=0.0):
        return (self.xa - pad <= x <= self.xb + pad) and (self.ya - pad <= y <= self.yb + pad)

    # ------------------------------------------------------------------
    def grid(self, xs=1, ys=1, color="#d9dde3", width=0.5):
        for v in nice_ticks(self.xa, self.xb, xs):
            self.pg.line(self.X(v), self.y0, self.X(v), self.y0 + self.h, color, width, layer=C.UNDER)
        for v in nice_ticks(self.ya, self.yb, ys):
            self.pg.line(self.x0, self.Y(v), self.x0 + self.w, self.Y(v), color, width, layer=C.UNDER)

    def axes(self, xlabel="x", ylabel="y", xticks=1, yticks=1, color=C.INK, size=10,
             ticklabels=True, xfmt=fmt, yfmt=fmt, skip0=True, arrows=True, labels_math=True):
        pg = self.pg
        ox = self.X(0) if self.xa <= 0 <= self.xb else self.x0
        oy = self.Y(0) if self.ya <= 0 <= self.yb else self.y0 + self.h
        if arrows:
            pg.arrow(self.x0 - 4, oy, self.x0 + self.w + 8, oy, color, 1.2, head=6)
            pg.arrow(ox, self.y0 + self.h + 4, ox, self.y0 - 8, color, 1.2, head=6)
        else:
            pg.line(self.x0, oy, self.x0 + self.w, oy, color, 1.2)
            pg.line(ox, self.y0 + self.h, ox, self.y0, color, 1.2)
        if xlabel:
            if labels_math:
                pg.eq(self.x0 + self.w + 12, oy, xlabel, size + 3, color, valign="middle", solid=False)
            else:
                pg.text(self.x0 + self.w + 12, oy - 7, xlabel, size, color, solid=False)
        if ylabel:
            if labels_math:
                pg.eq(ox, self.y0 - 12, ylabel, size + 3, color, align="center", valign="baseline",
                      solid=False)
            else:
                pg.text(ox + 6, self.y0 - 18, ylabel, size, color, solid=False)
        if xticks:
            for v in nice_ticks(self.xa, self.xb, xticks):
                if skip0 and abs(v) < 1e-12:
                    continue
                X = self.X(v)
                pg.line(X, oy - 3, X, oy + 3, color, 1.0)
                if ticklabels:
                    pg.text(X, oy + 5, xfmt(v), size, C.GREY, align="center", solid=False)
        if yticks:
            for v in nice_ticks(self.ya, self.yb, yticks):
                if skip0 and abs(v) < 1e-12:
                    continue
                Y = self.Y(v)
                pg.line(ox - 3, Y, ox + 3, Y, color, 1.0)
                if ticklabels:
                    s = yfmt(v)
                    pg.text(ox - 6 - pg.twidth(s, size), Y - size * 0.62, s, size, C.GREY, solid=False)
        if skip0 and ticklabels and self.xa <= 0 <= self.xb and self.ya <= 0 <= self.yb:
            pg.text(ox - 4 - pg.twidth("0", size), oy + 3, "0", size, C.GREY, solid=False)

    def curve(self, f, a=None, b=None, color=C.BLUE, width=2.0, n=240, dash=None):
        """Plot y=f(x). Breaks the line where it leaves the window or f fails."""
        a = self.xa if a is None else a
        b = self.xb if b is None else b
        segs, cur = [], []
        for i in range(n + 1):
            x = a + (b - a) * i / n
            try:
                y = f(x)
                ok = y is not None and math.isfinite(y) and self.ya - 1e-9 <= y <= self.yb + 1e-9
            except (ValueError, ZeroDivisionError, OverflowError):
                ok = False
            if ok:
                cur.append(self.P(x, y))
            else:
                if len(cur) > 1:
                    segs.append(cur)
                cur = []
        if len(cur) > 1:
            segs.append(cur)
        for s in segs:
            self.pg.poly(s, color, width, dash=dash)
        return segs

    def param(self, fx, fy, t0, t1, color=C.BLUE, width=2.0, n=300, dash=None):
        pts = []
        for i in range(n + 1):
            t = t0 + (t1 - t0) * i / n
            pts.append(self.P(fx(t), fy(t)))
        self.pg.poly(pts, color, width, dash=dash)

    def polyline(self, pts, color=C.BLUE, width=2.0, dash=None, closed=False):
        self.pg.poly([self.P(*p) for p in pts], color, width, dash=dash, closed=closed)

    def dot(self, x, y, color=C.INK, r=3.0):
        self.pg.dot(self.X(x), self.Y(y), r, color)

    def hollow(self, x, y, color=C.INK, r=3.2):
        self.pg.circle(self.X(x), self.Y(y), r, color, 1.3, fillcolor="#ffffff")

    def label(self, x, y, s, size=12, color=C.INK, dx=6, dy=-18, math_=False):
        if math_:
            self.pg.eq(self.X(x) + dx, self.Y(y) + dy, s, size, color, solid=False)
        else:
            self.pg.rich(self.X(x) + dx, self.Y(y) + dy, s, w=240, size=size, color=color, solid=False)

    def fill_under(self, f, a, b, color=C.BLUE, alpha=255, n=120, base=0.0):
        pts = [self.P(a, base)]
        for i in range(n + 1):
            x = a + (b - a) * i / n
            pts.append(self.P(x, f(x)))
        pts.append(self.P(b, base))
        self.pg.fillpoly(pts, C.LIGHT.get(color, color), alpha)

    def fill_between(self, f, g, a, b, color=C.BLUE, alpha=255, n=120):
        top = [self.P(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)]
        bot = [self.P(a + (b - a) * i / n, g(a + (b - a) * i / n)) for i in range(n, -1, -1)]
        self.pg.fillpoly(top + bot, C.LIGHT.get(color, color), alpha)

    def vline(self, x, color=C.GREY, width=1.0, dash=(4, 3), y0=None, y1=None):
        self.pg.line(self.X(x), self.Y(self.ya if y0 is None else y0), self.X(x),
                     self.Y(self.yb if y1 is None else y1), color, width, dash=dash)

    def hline(self, y, color=C.GREY, width=1.0, dash=(4, 3), x0=None, x1=None):
        self.pg.line(self.X(self.xa if x0 is None else x0), self.Y(y),
                     self.X(self.xb if x1 is None else x1), self.Y(y), color, width, dash=dash)

    def arrow(self, x1, y1, x2, y2, color=C.RED, width=1.6, bend=0.0, head=7):
        self.pg.arrow(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2), color, width, bend, head)

    def seg(self, x1, y1, x2, y2, color=C.INK, width=1.6, dash=None):
        self.pg.line(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2), color, width, dash=dash)
