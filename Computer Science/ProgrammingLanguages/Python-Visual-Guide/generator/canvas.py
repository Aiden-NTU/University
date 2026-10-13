"""Free-form page canvas: put text, maths, pictures and pen strokes anywhere."""
import io
import math
import re

from . import draw as D
from . import eq as EQ
from . import fonts as F
from .xopp import A4_H, A4_W, Image, Stroke, Text, XPage

# ---------------------------------------------------------------- palette
INK = "#1a1a1a"
BLUE = "#1f5fbf"
ORANGE = "#e07000"
GREEN = "#1e8a3c"
RED = "#c62828"
PURPLE = "#7b3fb5"
GREY = "#8a8a8a"
TEAL = "#00838f"
PINK = "#c2185b"
BROWN = "#8d5524"
YELLOW = "#ffe14d"
LIGHT = {
    BLUE: "#dbe7fa", ORANGE: "#fde6cc", GREEN: "#d7f0dc", RED: "#fadada",
    PURPLE: "#ece0f7", GREY: "#eeeeee", TEAL: "#d3eff1", PINK: "#f9d9e6",
    BROWN: "#efe1d3", INK: "#e6e6e6", YELLOW: "#fff6c2",
}
HL = {  # highlighter colours
    "y": "#ffec3d", "g": "#8ef08e", "b": "#8fc3ff", "p": "#e0b0ff", "o": "#ffc680", "r": "#ff9a9a",
}

CODES = {  # markup colour codes -> (hex, latex colour name)
    "k": (INK, "ink"), "b": (BLUE, "cblu"), "o": (ORANGE, "corg"), "g": (GREEN, "cgrn"),
    "r": (RED, "cred"), "p": (PURPLE, "cpur"), "y": (GREY, "cgry"), "t": (TEAL, "cteal"),
    "n": (PINK, "cpink"), "w": (BROWN, "cbrn"),
}
HEX2TEX = {v[0]: v[1] for v in CODES.values()}
CODE_INK = "#a3324a"  # inline `code` spans

MATH_SCALE = 1.15  # Computer Modern looks smaller than DejaVu at the same size
HAND_SCALE = 1.4  # Caveat looks smaller than DejaVu at the same size

UNDER, MAIN = 0, 1


def texcolor(c):
    return HEX2TEX.get(c, "ink") if c.startswith("#") else c


class Page:
    def __init__(self, chapter=None, bg="#ffffff"):
        self.x = XPage(A4_W, A4_H, bg=bg)
        self.x.layers = [[], []]
        self.ch = chapter
        self.W, self.H = A4_W, A4_H
        self.boxes = []  # (bbox, label) for overlap checks
        self.number = None

    # ------------------------------------------------------------ low level
    def _stroke(self, pts, color=INK, width=1.4, tool="pen", fill=None, layer=MAIN):
        if len(pts) < 2:
            return None
        return self.x.add(Stroke(pts, color, width, tool, fill), layer)

    def _box(self, bb, label, solid=True):
        if solid:
            self.boxes.append((bb, label))

    # ------------------------------------------------------------ text
    def text(self, x, y, s, size=13, color=INK, font=F.SANS, w=None, align="left",
             solid=True):
        """Plain single-style text. Wraps to width w if given. Returns height."""
        lines = F.wrap(s, font, size, w) if w else s.split("\n")
        lh = F.line_h(font, size)
        widths = [F.width(l, font, size) for l in lines]
        tw = max(widths) if widths else 0
        h = lh * len(lines)
        if align == "left":
            self.x.add(Text(x, y, "\n".join(lines), size, font, color, tw, h), MAIN)
            self._box((x, y, x + tw, y + h), s[:30], solid)
        else:
            for i, (l, lw) in enumerate(zip(lines, widths)):
                if align == "center":
                    lx = x - lw / 2 if w is None else x + (w - lw) / 2
                else:
                    lx = x - lw if w is None else x + w - lw
                self.x.add(Text(lx, y + i * lh, l, size, font, color, lw, lh), MAIN)
                self._box((lx, y + i * lh, lx + lw, y + (i + 1) * lh), l[:30], solid)
        return h

    def note(self, x, y, s, color=RED, size=17, w=None, align="left", solid=True):
        """Handwritten-style annotation (Caveat font)."""
        return self.text(x, y, s, size, color, F.HAND, w, align, solid)

    def twidth(self, s, size=13, font=F.SANS):
        return max(F.width(l, font, size) for l in s.split("\n"))

    # ------------------------------------------------------------ rich text
    _tok = re.compile(r"(`[^`]+`|\$[^$]+\$|\*\*|__|\{[kbogrpytnwKBOGRPYTNWh]:|\})")

    def _parse(self, markup, color, font):
        """Yield atoms: ('t', text, font, color) / ('m', latex, color) / ('br',)."""
        bold = italic = False
        stack = [(color, False, False)]
        atoms = []
        for part in self._tok.split(markup):
            if not part:
                continue
            col, sb, hand = stack[-1]
            if part.startswith("`") and part.endswith("`") and len(part) > 2:
                body = part[1:-1]
                atoms.append(("t", body if len(body) > 22 else body.replace(" ", "\u00a0"), F.MONO, CODE_INK))
                continue
            if part == "**":
                bold = not bold
                continue
            if part == "__":
                italic = not italic
                continue
            if re.fullmatch(r"\{[kbogrpytnwKBOGRPYTNWh]:", part):
                code = part[1]
                if code == "h":
                    stack.append((col, sb, True))
                else:
                    stack.append((CODES[code.lower()][0], code.isupper(), hand))
                continue
            if part == "}" and len(stack) > 1:
                stack.pop()
                continue
            if part.startswith("$") and part.endswith("$") and len(part) > 1:
                atoms.append(("m", part[1:-1], col))
                continue
            b = bold or sb
            if hand:
                f = F.HAND
            elif font == F.SANS:
                f = F.BOLDITALIC if (b and italic) else F.BOLD if b else F.ITALIC if italic else F.SANS
            else:
                f = font
            for i, seg in enumerate(part.split("\n")):
                if i:
                    atoms.append(("br",))
                if seg:
                    atoms.append(("t", seg, f, col))
        return atoms

    def rich(self, x, y, markup, w=480, size=13, color=INK, font=F.SANS, align="left",
             spacing=1.0, dry=False, solid=True):
        """Paragraph with **bold**, __italic__, {b:colour} spans, {h:hand} and $maths$.

        Breaks lines only at spaces. Returns the height used."""
        atoms = self._parse(markup, color, font)
        # build unbreakable groups separated by spaces / breaks
        groups = []  # each group: list of pieces; piece = dict
        cur = []
        space_before = []
        pending_space = False

        def close():
            nonlocal cur
            if cur:
                groups.append((cur, pending_space_flag[0]))
                cur = []

        pending_space_flag = [False]
        for a in atoms:
            if a[0] == "br":
                close()
                groups.append(("BR", False))
                pending_space_flag[0] = False
                continue
            if a[0] == "m":
                m = EQ.get(a[1], texcolor(a[2]), display=False)
                sc = size / EQ.BASE_PT * MATH_SCALE
                cur.append(dict(k="m", latex=a[1], col=a[2], w=m["w"] * sc, h=m["h"] * sc,
                                d=m["depth"] * sc, png=m["png"]))
                continue
            _, s, f, col = a
            tokens = re.split(r"( +)", s)
            for tk in tokens:
                if tk == "":
                    continue
                if tk.startswith(" "):
                    close()
                    pending_space_flag[0] = True
                    continue
                if not cur:
                    pass
                sz = size * HAND_SCALE if f == F.HAND else size
                cur.append(dict(k="t", s=tk, f=f, col=col, sz=sz, w=F.width(tk, f, sz)))
                if len(cur) == 1:
                    pass
            # keep pending flag for next group
        close()

        # attach "space before" flags: a group has a space before it if a space token preceded it
        # (recomputed simply: every group except the first on a line gets a space unless glued)
        lines = [[]]
        lw = 0.0
        sw = F.width(" ", F.SANS, size)

        def gap_w(prev, g):
            a, b = prev[-1], g[0]
            if a["k"] == "t" and b["k"] == "t" and a["f"] == b["f"] and a["col"] == b["col"] and a["sz"] == b["sz"]:
                return F.width(" ", a["f"], a["sz"])
            return sw

        for g, _ in groups:
            if g == "BR":
                lines.append([])
                lw = 0.0
                continue
            gw = sum(p["w"] for p in g)
            add = gw + (gap_w(lines[-1][-1], g) if lines[-1] else 0)
            if lines[-1] and lw + add > w:
                lines.append([g])
                lw = gw
            else:
                lines[-1].append(g)
                lw += add

        total = 0.0
        text_lh = F.line_h(F.SANS, size) * spacing
        text_asc = F.baseline(F.SANS, size)
        for line in lines:
            asc = text_asc
            desc = text_lh - text_asc
            for g in line:
                for p in g:
                    if p["k"] == "m":
                        asc = max(asc, p["h"] - p["d"] + 1.5)
                        desc = max(desc, p["d"] + 2.5)
                    elif p["f"] == F.HAND:
                        asc = max(asc, F.baseline(F.HAND, p["sz"]) - 2)
            lh = max(text_lh, asc + desc)
            if not dry:
                width_line = (sum(sum(p["w"] for p in g) for g in line)
                              + sum(gap_w(a, b) for a, b in zip(line, line[1:])))
                if align == "center":
                    cx = x + (w - width_line) / 2
                elif align == "right":
                    cx = x + w - width_line
                else:
                    cx = x
                base = y + total + asc
                run = None  # [x, text, font, col]
                prev = None
                for gi, g in enumerate(line):
                    if gi:
                        first = g[0]
                        if (run and first["k"] == "t" and run[2] == first["f"]
                                and run[3] == first["col"] and run[4] == first["sz"]):
                            run[1] += " "
                            cx += F.width(" ", run[2], run[4])
                        else:
                            cx += sw
                    for p in g:
                        if p["k"] == "t":
                            if run and run[2] == p["f"] and run[3] == p["col"] and run[4] == p["sz"]:
                                run[1] += p["s"]
                            else:
                                self._flush_run(run, base, size)
                                run = [cx, p["s"], p["f"], p["col"], p["sz"]]
                        else:
                            self._flush_run(run, base, size)
                            run = None
                            if p["png"] is not None:
                                top = base - (p["h"] - p["d"])
                                self.x.add(Image(cx, top, p["w"], p["h"], p["png"]), MAIN)
                                self._box((cx, top, cx + p["w"], top + p["h"]), p["latex"][:30], solid)
                        cx += p["w"]
                self._flush_run(run, base, size)
            total += lh
        return total

    def _flush_run(self, run, base, size):
        if not run:
            return
        x, s, f, col, size = run
        s = s.rstrip(" ")
        if not s:
            return
        top = base - F.baseline(f, size)
        w = F.width(s, f, size)
        self.x.add(Text(x, top, s, size, f, col, w, F.line_h(f, size)), MAIN)
        self._box((x, top + 1, x + w, top + F.line_h(f, size) - 2), s[:30])

    def rich_h(self, markup, w=480, size=13, spacing=1.0):
        return self.rich(0, 0, markup, w, size, spacing=spacing, dry=True)

    def rich_w(self, markup, size=13):
        """Natural (unwrapped) width of a one-line rich string."""
        atoms = self._parse(markup, INK, F.SANS)
        tot = 0.0
        for a in atoms:
            if a[0] == "m":
                m = EQ.get(a[1], texcolor(a[2]), display=False)
                tot += m["w"] * size / EQ.BASE_PT * MATH_SCALE
            elif a[0] == "t":
                tot += F.width(a[1], a[2], size * (HAND_SCALE if a[2] == F.HAND else 1))
        return tot

    # ------------------------------------------------------------ maths
    def eq_size(self, latex, size=16, display=True, color=INK):
        m = EQ.get(latex, texcolor(color), display)
        sc = size / EQ.BASE_PT * MATH_SCALE
        return m["w"] * sc, m["h"] * sc, m["depth"] * sc

    def eq(self, x, y, latex, size=16, color=INK, align="left", display=True, solid=True,
           valign="top"):
        """Place a typeset formula. align: left|center|right relative to x.
        valign: top|middle|baseline relative to y. Returns (w, h)."""
        m = EQ.get(latex, texcolor(color), display)
        sc = size / EQ.BASE_PT * MATH_SCALE
        w, h, d = m["w"] * sc, m["h"] * sc, m["depth"] * sc
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        if valign == "middle":
            y -= h / 2
        elif valign == "baseline":
            y -= h - d
        if m["png"] is not None:
            self.x.add(Image(x, y, w, h, m["png"]), MAIN)
        self._box((x, y, x + w, y + h), latex[:30], solid)
        return w, h

    # ------------------------------------------------------------ images
    def image(self, x, y, png, w=None, h=None, px_w=None, px_h=None, solid=True):
        if px_w is None:
            from PIL import Image as PI
            im = PI.open(io.BytesIO(png))
            px_w, px_h = im.size
        if w is None and h is None:
            w = px_w * 72 / 150
        if h is None:
            h = w * px_h / px_w
        if w is None:
            w = h * px_w / px_h
        self.x.add(Image(x, y, w, h, png), MAIN)
        self._box((x, y, x + w, y + h), "image", solid)
        return w, h

    def mpl(self, fig, x, y, w, dpi=200, solid=True):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, transparent=True)
        import matplotlib.pyplot as plt
        plt.close(fig)
        return self.image(x, y, buf.getvalue(), w=w, solid=solid)

    # ------------------------------------------------------------ strokes
    def line(self, x1, y1, x2, y2, color=INK, width=1.4, dash=None, layer=MAIN):
        pts = [(x1, y1), (x2, y2)]
        if dash:
            for seg in D.dashes(pts, *dash):
                self._stroke(seg, color, width, layer=layer)
        else:
            self._stroke(pts, color, width, layer=layer)

    def poly(self, pts, color=INK, width=1.4, dash=None, fill=None, layer=MAIN, closed=False):
        pts = list(pts)
        if closed:
            pts = pts + [pts[0]]
        if dash:
            for seg in D.dashes(pts, *dash):
                self._stroke(seg, color, width, layer=layer)
        else:
            self._stroke(pts, color, width, fill=fill, layer=layer)

    def arrow(self, x1, y1, x2, y2, color=INK, width=1.4, bend=0.0, head=7.0, both=False,
              dash=None):
        pts = D.curve_between(x1, y1, x2, y2, bend)
        self.poly(pts, color, width, dash=dash)
        self._stroke(D.arrow_head(pts[-1], pts[-2], head), color, width)
        if both:
            self._stroke(D.arrow_head(pts[0], pts[1], head), color, width)

    def rect(self, x, y, w, h, color=INK, width=1.2, fill=None, fillcolor=None, r=0,
             dash=None, layer=MAIN):
        pts = D.rrect(x, y, w, h, r) if r else [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
        if fill is not None or fillcolor:
            fc = fillcolor or color
            self._stroke(pts, fc, 0.1 if fillcolor else width, fill=fill if fill is not None else 255,
                         layer=UNDER)
            if fillcolor and width:
                self.poly(pts, color, width, dash=dash, layer=layer)
        elif width:
            self.poly(pts, color, width, dash=dash, layer=layer)

    def fillpoly(self, pts, color, alpha=255, outline=None, width=1.2, layer=UNDER):
        pts = list(pts)
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        self._stroke(pts, color, 0.1, fill=alpha, layer=layer)
        if outline:
            self._stroke(pts, outline, width)

    def circle(self, cx, cy, r, color=INK, width=1.4, fill=None, fillcolor=None, dash=None):
        pts = D.ellipse(cx, cy, r, r)
        if fillcolor or fill is not None:
            self._stroke(pts, fillcolor or color, 0.1, fill=255 if fill is None else fill, layer=UNDER)
        if width:
            self.poly(pts, color, width, dash=dash)

    def ellipse(self, cx, cy, rx, ry, color=INK, width=1.4, fillcolor=None, dash=None):
        pts = D.ellipse(cx, cy, rx, ry)
        if fillcolor:
            self._stroke(pts, fillcolor, 0.1, fill=255, layer=UNDER)
        if width:
            self.poly(pts, color, width, dash=dash)

    def dot(self, x, y, r=2.6, color=INK):
        self._stroke(D.ellipse(x, y, r, r, 16), color, 0.5, fill=255)

    def ring(self, x, y, w, h, color=RED, width=1.6):
        """Hand-drawn looking loop around a box (x,y,w,h)."""
        cx, cy = x + w / 2, y + h / 2
        rx, ry = w / 2 + 6, h / 2 + 5
        pts = D.ellipse(cx, cy, rx, ry, 60, -0.3, 2 * math.pi + 0.15)
        self._stroke(pts, color, width)

    def highlight(self, x, y, w, h, color="y"):
        """Highlighter band covering the box (drawn under text)."""
        c = HL.get(color, color)
        inset = min(h / 2, w / 2 - 0.5)
        self._stroke([(x + inset, y + h / 2), (x + w - inset, y + h / 2)], c, h, tool="highlighter", layer=UNDER)

    def underline(self, x, y, w, color=ORANGE, width=1.8, wave=False):
        if wave:
            self._stroke(D.wavy(x, y, x + w), color, width * 0.8)
        else:
            self._stroke([(x, y), (x + w, y)], color, width)

    def cross(self, x, y, w, h, color=RED, width=1.8):
        self._stroke([(x, y + h), (x + w, y)], color, width)

    def strike(self, x, y, w, h, color=RED, width=1.8):
        self._stroke([(x, y), (x + w, y + h)], color, width)
        self._stroke([(x, y + h), (x + w, y)], color, width)

    def tick(self, x, y, s=12, color=GREEN, width=2.4):
        self._stroke([(x, y + s * 0.55), (x + s * 0.38, y + s), (x + s, y)], color, width)

    def xmark(self, x, y, s=12, color=RED, width=2.4):
        self._stroke([(x, y), (x + s, y + s)], color, width)
        self._stroke([(x, y + s), (x + s, y)], color, width)

    def brace(self, x1, y1, x2, y2, color=INK, width=1.3, depth=8):
        pts, tip = D.brace(x1, y1, x2, y2, depth)
        self._stroke(pts, color, width)
        return tip

    def arc(self, cx, cy, r, deg0, deg1, color=INK, width=1.4, arrow=False):
        pts = D.arc(cx, cy, r, deg0, deg1)
        self._stroke(pts, color, width)
        if arrow:
            self._stroke(D.arrow_head(pts[-1], pts[-2], 6), color, width)

    def sector(self, cx, cy, r, deg0, deg1, color, alpha=255, outline=None):
        pts = [(cx, cy)] + D.arc(cx, cy, r, deg0, deg1) + [(cx, cy)]
        self._stroke(pts, color, 0.1, fill=alpha, layer=UNDER)
        if outline:
            self._stroke(pts, outline, 1.2)

    def star(self, cx, cy, r, color=ORANGE, fill=True):
        pts = D.star(cx, cy, r)
        self._stroke(pts, color, 1.0, fill=255 if fill else None)

    # ------------------------------------------------------------ convenience
    def eqnote(self, x, y, latex, note, size=17, color=INK, note_color=RED, gap=26,
               note_w=200, note_size=16):
        """Formula with a hand-written note to its right joined by a small arrow.
        Returns (w_eq, height)."""
        w, h = self.eq(x, y, latex, size, color)
        nx = x + w + gap + 14
        nh = self.note(nx, y + h / 2 - 10, note, note_color, note_size, w=note_w)
        self.arrow(nx - 4, y + h / 2, x + w + 5, y + h / 2, note_color, 1.2, head=5)
        return w, max(h, nh)
