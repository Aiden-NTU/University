"""Laser-cut poster walls: four engraved plywood boards that stand in a slot round the 1:1000 site.

The content lives in ``Poster/laser_wall.json``; adding a card needs no code. This script:

* fits every card onto the four walls: it grows the walls, then shrinks the text, only as far
  as needed to keep everything comfortably readable;
* turns all text into outlines, so the laser PC needs none of our fonts;
* draws four identical, unglued boards (a pinwheel round the rim slot, so any board fits any
  side), a sawtooth top edge that echoes the roof, a chamfered foot that drops into the slot,
  and a 1:1000 ruler on each wall that lines up with the site model behind it.

    python src/laser_wall.py

Outputs go to ``Poster/laser_wall/``. Layer colours follow the common laser convention
(red hairline = cut, blue hairline = score, black fill = engrave) and can be changed in the JSON.
"""
import json
import math
import re
import subprocess
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import qrcode
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from shapely.geometry import LineString, Point, Polygon, box as rect
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

import building as B
import config as C
import site_model as S
from project_facts import facts

CONTENT = C.ROOT / "Poster" / "laser_wall.json"
OUT = C.ROOT / "Poster" / "laser_wall"
FONTS = Path(__file__).with_name("fonts")

# Ply thickness and the rim slot live in config.py (WALL_PLY_MM, SITE_WALL_*), because the
# printed site model has to match them.
WALL_DEFAULTS = dict(
    kerf_mm=0.15,                # width the beam burns away; ask the technician
    height_mm=110.0,             # preferred height showing above the rim (to the sawtooth peaks)
    max_height_mm=140.0,         # the fitter may grow the walls up to this before shrinking text
    tooth_pitch_mm=14.0,         # sawtooth top edge; 0 for a straight top
    sheet_mm=[420.0, 297.0],     # material sheet / laser bed (A3 by default)
    min_text_scale=0.8,
    max_text_scale=1.3,
    layers=dict(cut="#FF0000", score="#0000FF", engrave="#000000"),
)
ROOF_TILT = math.radians(C.SAWTOOTH_TILT_DEG)
COLS_PER_PANEL = 4
GUTTER = 4.0
MARGIN = 4.0


# ---------------------------------------------------------------------------------------
# Fonts: HarfBuzz for shaping (kerning), fontTools for outlines
# ---------------------------------------------------------------------------------------
class Font:
    def __init__(self, file):
        self.name, path = file, str(FONTS / file)
        face = hb.Face(hb.Blob.from_file_path(path))
        self.hb, self.upem = hb.Font(face), face.upem
        self.tt = TTFont(path)
        self.glyphs, self.order = self.tt.getGlyphSet(), self.tt.getGlyphOrder()
        os2 = self.tt["OS/2"]
        self.cap = (getattr(os2, "sCapHeight", 0) or 0.7 * self.upem) / self.upem
        self._widths = {}

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        if any(i.codepoint == 0 for i in buf.glyph_infos):
            cmap = self.tt.getBestCmap()
            missing = sorted({ch for ch in text if not ch.isspace() and ord(ch) not in cmap})
            if missing:
                raise ValueError(f"the font {self.name} has no {' '.join(missing)} "
                                 f"(in \"{text}\"); swap it for a plain character")
        return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]

    def width(self, text, size):
        if text not in self._widths:
            self._widths[text] = sum(g[1] for g in self.shape(text)) / self.upem
        return self._widths[text] * size


@lru_cache(maxsize=1)
def fonts():
    return dict(title=Font("Comfortaa-Bold.otf"), bold=Font("Montserrat-Bold.otf"),
                body=Font("Montserrat-Medium.otf"), hand=Font("Caveat-SemiBold.ttf"))


def wrap(font, text, size, width):
    lines = []
    for para in str(text).split("\n"):
        line = ""
        words = []
        for word in para.split():
            while font.width(word, size) > width and len(word) > 2:
                cut = max(1, max(k for k in range(1, len(word)) if font.width(word[:k] + "-", size) <= width or k == 1))
                words.append(word[:cut] + "-")
                word = word[cut:]
            words.append(word)
        for word in words:
            trial = f"{line} {word}" if line else word
            if line and font.width(trial, size) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    return lines


def block_h(font, n, size, lead):
    return size * (font.cap + 0.3) + (n - 1) * lead * size if n else 0.0


# ---------------------------------------------------------------------------------------
# Canvas: every coordinate is flattened to absolute millimetres (no SVG transforms)
# ---------------------------------------------------------------------------------------
def _mul(m1, m2):
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2, a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


def _rotation(deg, cx, cy):
    r = math.radians(deg)
    co, si = math.cos(r), math.sin(r)
    return _mul((1, 0, 0, 1, cx, cy), _mul((co, si, -si, co, 0, 0), (1, 0, 0, 1, -cx, -cy)))


def _num(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


class Canvas:
    def __init__(self):
        self.layers = {"cut": [], "score": [], "engrave": []}
        self.m = (1, 0, 0, 1, 0, 0)

    @contextmanager
    def transform(self, m):
        old, self.m = self.m, _mul(self.m, m)
        try:
            yield
        finally:
            self.m = old

    def rotated(self, deg, cx, cy):
        return self.transform(_rotation(deg, cx, cy))

    def pt(self, x, y):
        a, b, c, d, e, f = self.m
        return a * x + c * y + e, b * x + d * y + f

    def line(self, pts, layer="score", closed=False):
        q = [self.pt(*p) for p in pts]
        self.layers[layer].append("M" + " L".join(f"{_num(x)},{_num(y)}" for x, y in q) + (" Z" if closed else ""))

    def circle(self, cx, cy, r, layer="score"):
        n = max(24, int(r * 12))
        self.line([(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)],
                  layer, closed=True)

    def rounded_rect(self, x, y, w, h, r, layer="score"):
        pts = []
        for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
            pts += [(cx + r * math.cos(math.radians(a0 + 15 * k)), cy + r * math.sin(math.radians(a0 + 15 * k)))
                    for k in range(7)]
        self.line(pts, layer, closed=True)

    def shape(self, geom, layer="engrave"):
        parts = []
        for p in getattr(geom, "geoms", [geom]):
            if p.is_empty or p.geom_type != "Polygon":
                continue
            p = orient(p, 1.0)
            for ring in (p.exterior, *p.interiors):
                q = [self.pt(x, y) for x, y in list(ring.coords)[:-1]]
                parts.append("M" + " L".join(f"{_num(x)},{_num(y)}" for x, y in q) + " Z")
        if parts:
            self.layers[layer].append(" ".join(parts))

    def text(self, font, text, size, x, y, anchor="start"):
        """Engrave one line of text with its baseline at y. Returns its width."""
        w = font.width(text, size)
        x0 = x - {"start": 0.0, "middle": w / 2, "end": w}[anchor]
        pen = SVGPathPen(font.glyphs, ntos=_num)
        k = size / font.upem
        for gid, adv, xo, yo in font.shape(text):
            font.glyphs[font.order[gid]].draw(TransformPen(pen, _mul(self.m, (k, 0, 0, -k, x0 + xo * k, y - yo * k))))
            x0 += adv * k
        d = pen.getCommands()
        if d:
            self.layers["engrave"].append(d)
        return w

    def lines(self, font, lines, size, x, y, lead, anchor="start"):
        for i, ln in enumerate(lines):
            self.text(font, ln, size, x, y + font.cap * size + i * lead * size, anchor)


# ---------------------------------------------------------------------------------------
# Icons: drawn on a 24 x 24 grid as strokes, engraved as filled outlines
# ---------------------------------------------------------------------------------------
def _arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def _ring(cx, cy, r):
    return _arc(cx, cy, r, 0, 360, 36)


def _leaf():
    a, b = (4.0, 20.0), (20.0, 4.0)
    side = []
    for sign in (1, -1):
        for k in range(13):
            t = k / 12 if sign == 1 else 1 - k / 12
            mx, my = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            off = sign * 5.5 * math.sin(math.pi * t)
            side.append((mx + off * 0.7071, my + off * 0.7071))
    return [side + [side[0]], [a, (15, 9)], [(2, 22), a]]


ICONS = {
    "sun": [_ring(12, 12, 4.5)] + [[(12 + 7 * math.cos(a), 12 + 7 * math.sin(a)), (12 + 10 * math.cos(a), 12 + 10 * math.sin(a))]
                                   for a in (k * math.pi / 4 for k in range(8))],
    "leaf": _leaf(),
    "bolt": [[(14, 2), (5, 14), (11.5, 14), (10, 22), (19, 10), (12.5, 10), (14, 2)]],
    "server": [[(4, y), (20, y), (20, y + 5.5), (4, y + 5.5), (4, y)] for y in (2.5, 9.25, 16)]
              + [[(7, y + 2.75), (7.4, y + 2.75)] for y in (2.5, 9.25, 16)],
    "bike": [_ring(6, 16, 4.5), _ring(18, 16, 4.5), [(6, 16), (10, 9), (16.5, 9), (18, 16)],
             [(10, 9), (12.5, 16), (6, 16)], [(12.5, 16), (16.5, 9)], [(8.5, 7), (11.5, 7)], [(16.5, 9), (15.5, 5.5), (18, 5.5)]],
    "pin": [_arc(12, 9, 6.5, 150, 390) + [(12, 22), _arc(12, 9, 6.5, 150, 150, 1)[0]], _ring(12, 9, 2.3)],
    "tree": [_ring(12, 9, 6.5), [(12, 15.5), (12, 22)], [(6, 22), (18, 22)]],
    "people": [_ring(8, 7, 3), _ring(16.5, 8, 2.5), _arc(8, 20, 6, 180, 360), _arc(16.5, 20, 5, 200, 340)],
    "house": [[(3, 11), (12, 3), (21, 11)], [(5.5, 9), (5.5, 21), (18.5, 21), (18.5, 9)], [(10, 21), (10, 15), (14, 15), (14, 21)]],
    "drop": [[(12, 2)] + _arc(12, 15, 6, -35, 215) + [(12, 2)]],
    "star": [[(12 + (10 if k % 2 == 0 else 4.2) * math.cos(math.radians(-90 + 36 * k)),
               12.5 + (10 if k % 2 == 0 else 4.2) * math.sin(math.radians(-90 + 36 * k))) for k in range(11)]],
    "sparkle": [[(12, 2), (13.8, 10.2), (22, 12), (13.8, 13.8), (12, 22), (10.2, 13.8), (2, 12), (10.2, 10.2), (12, 2)]],
    "cube": [[(12, 2), (21, 7), (21, 17), (12, 22), (3, 17), (3, 7), (12, 2)], [(3, 7), (12, 12), (21, 7)], [(12, 12), (12, 22)]],
    "globe": [_ring(12, 12, 9.5), [(12 + 4.3 * math.cos(math.radians(a)), 12 + 9.5 * math.sin(math.radians(a))) for a in range(0, 361, 10)],
              [(2.5, 12), (21.5, 12)], [(4.5, 7), (19.5, 7)], [(4.5, 17), (19.5, 17)]],
    "book": [[(2, 5), (12, 7), (22, 5), (22, 19), (12, 21), (2, 19), (2, 5)], [(12, 7), (12, 21)]],
    "cup": [[(4, 9), (5.5, 21), (15.5, 21), (17, 9), (4, 9)], _arc(17, 14, 3.2, -90, 90),
            [(8, 6), (8.8, 3)], [(12, 6), (12.8, 3)]],
    "wind": [[(2, 8), (14, 8)] + _arc(14, 5, 3, 90, -150), [(2, 14), (18, 14)] + _arc(18, 17, 3, -90, 150), [(4, 19.5), (10, 19.5)]],
    "thermo": [[(10, 15.5), (10, 4)] + _arc(12, 4, 2, 180, 360) + [(14, 15.5)], _ring(12, 18.5, 3.5), [(12, 8), (12, 16)]],
    "sawtooth": [[(2, 21), (22, 21)], [(2, 21), (2, 13), (8.5, 9), (8.5, 13), (15, 9), (15, 13), (21.5, 9), (21.5, 21)]],
    "cycle": [_arc(12, 12, 8, 200, 340), [(18.3, 3.6), (19.5, 7.3), (15.8, 8)], _arc(12, 12, 8, 20, 160), [(5.7, 20.4), (4.5, 16.7), (8.2, 16)]],
    "solar": [[(3, 17), (7, 7), (21, 7), (17, 17), (3, 17)], [(5, 12), (19, 12)], [(10, 17), (14, 7)], [(12, 17), (12, 22)]],
    "ruler": [[(2, 8), (22, 8), (22, 16), (2, 16), (2, 8)]] + [[(x, 8), (x, 11 if k % 2 else 12.5)] for k, x in enumerate((5, 8.5, 12, 15.5, 19))],
    "arrow": [[(3, 12), (20, 12)], [(14, 6), (20, 12), (14, 18)]],
}
DOODLES = ["sparkle", "leaf", "sun", "bike", "tree", "sawtooth", "star", "cube", "drop", "wind"]


@lru_cache(maxsize=None)
def icon_shape(name, size):
    if name not in ICONS:
        raise ValueError(f"unknown icon '{name}'; choose from {', '.join(sorted(ICONS))}")
    k = size / 24
    return unary_union([LineString([(x * k, y * k) for x, y in s]).buffer(0.8 * k, cap_style=1, join_style=1)
                        for s in ICONS[name]])


def draw_icon(cv, name, x, y, size):
    with cv.transform((1, 0, 0, 1, x, y)):
        cv.shape(icon_shape(name, round(size, 3)))


# ---------------------------------------------------------------------------------------
# Facts the cards can quote, e.g. "{gia_m2} m2" (see project_facts.py)
# ---------------------------------------------------------------------------------------
def fill(text):
    def sub(m):
        if m.group(1) not in facts():
            raise ValueError(f"unknown placeholder {{{m.group(1)}}}; available: {', '.join(sorted(facts()))}")
        return facts()[m.group(1)]
    return re.sub(r"\{(\w+)\}", sub, str(text))


# ---------------------------------------------------------------------------------------
# Cards. Each returns (height, draw) for a given width w and text scale s.
# draw(cv, x, y, tilt) engraves the card with its top-left corner at (x, y).
# ---------------------------------------------------------------------------------------
def _title(it, w, s):
    F = fonts()
    name, tag = fill(it.get("title", "")), fill(it.get("tagline", ""))
    size = min(float(it.get("size_mm", 15)) * s, 0.98 * w / F["title"].width(name, 1))
    tag_size = 5.2 * s
    tag_lines = wrap(F["hand"], tag, tag_size, w) if tag else []
    zig_y = size * F["title"].cap + 2.2 * s
    tag_y = zig_y + 2.0 * s + 2.4 * s
    h = tag_y + block_h(F["hand"], len(tag_lines), tag_size, 1.05)

    def draw(cv, x, y, tilt):
        cv.text(F["title"], name, size, x, y + size * F["title"].cap)
        tw, pitch, rise = F["title"].width(name, size), 4.5 * s, 2.0 * s
        pts, px = [(x, y + zig_y + rise)], x
        while px + pitch <= x + tw + 0.01:
            pts += [(px + pitch, y + zig_y), (px + pitch, y + zig_y + rise)]
            px += pitch
        cv.line(pts)
        cv.lines(F["hand"], tag_lines, tag_size, x, y + tag_y, 1.05)
    return h, draw


def _note(it, w, s):
    F = fonts()
    pad, inset = 2.6 * s, 1.2
    cw = w - 2 * inset
    iw = cw - 2 * pad
    icon = it.get("icon")
    isz = 7.0 * s if icon else 0.0
    t_size, b_size = 3.5 * s, 2.85 * s
    t_lines = wrap(F["bold"], fill(it.get("title", "")), t_size, iw - (isz + 1.8 * s if icon else 0)) if it.get("title") else []
    b_lines = wrap(F["body"], fill(it.get("text", "")), b_size, iw) if it.get("text") else []
    head = max(isz, block_h(F["bold"], len(t_lines), t_size, 1.18))
    body_y = pad + head + (2.0 * s if b_lines else 0)
    ch = body_y + block_h(F["body"], len(b_lines), b_size, 1.38) + pad
    h = ch + 2 * inset

    def draw(cv, x, y, tilt):
        x0, y0 = x + inset, y + inset
        with cv.rotated(0.9 * tilt, x0 + cw / 2, y0 + ch / 2):
            cv.rounded_rect(x0, y0, cw, ch, 2.2 * s)
            tw, th = 13 * s, 3.6 * s
            with cv.rotated(-5 * tilt, x0 + cw / 2, y0):
                cv.line([(x0 + cw / 2 - tw / 2, y0 - th / 2), (x0 + cw / 2 + tw / 2, y0 - th / 2),
                         (x0 + cw / 2 + tw / 2, y0 + th / 2), (x0 + cw / 2 - tw / 2, y0 + th / 2)], closed=True)
            tx = x0 + pad
            if icon:
                draw_icon(cv, icon, tx, y0 + pad, isz)
                tx += isz + 1.8 * s
            ty = y0 + pad + (head - block_h(F["bold"], len(t_lines), t_size, 1.18)) / 2
            cv.lines(F["bold"], t_lines, t_size, tx, ty, 1.18)
            cv.lines(F["body"], b_lines, b_size, x0 + pad, y0 + body_y, 1.38)
    return h, draw


def _stats(it, w, s):
    F = fonts()
    items = it.get("items", [])
    per_row = max(1, min(len(items), 4 if w > 100 else 2))
    g = 2.5 * s
    d = min((w - (per_row - 1) * g) / per_row, 32 * s)
    rows = math.ceil(len(items) / per_row)
    h = rows * d + (rows - 1) * g

    def draw(cv, x, y, tilt):
        for k, st in enumerate(items):
            r, c = divmod(k, per_row)
            n_row = min(per_row, len(items) - r * per_row)
            cx = x + (w - n_row * d - (n_row - 1) * g) / 2 + c * (d + g) + d / 2
            cy = y + r * (d + g) + d / 2
            cv.circle(cx, cy, d / 2 - 0.3)
            cv.circle(cx, cy, d / 2 - 1.3 * s)
            val, lab = fill(st.get("value", "")), fill(st.get("label", ""))
            vs = min(7.0 * s, 0.72 * d / max(F["title"].width(val, 1), 1e-6))
            ls = min(4.6 * s, 0.70 * d / max(F["hand"].width(lab, 1), 1e-6))
            if st.get("icon"):
                isz = 0.22 * d
                draw_icon(cv, st["icon"], cx - isz / 2, cy - 0.40 * d, isz)
            cv.text(F["title"], val, vs, cx, cy + vs * F["title"].cap * 0.5 + 0.02 * d, "middle")
            cv.text(F["hand"], lab, ls, cx, cy + 0.27 * d, "middle")
    return h, draw


def _steps(it, w, s):
    F = fonts()
    title, steps = fill(it.get("title", "")), [fill(t) for t in it.get("steps", [])]
    hs, ts, r = 5.0 * s, 2.75 * s, 2.7 * s
    tx = 2 * r + 2.2 * s
    t_lines = wrap(F["hand"], title, hs, w) if title else []
    blocks = [wrap(F["body"], t, ts, w - tx) for t in steps]
    heights = [max(2 * r, block_h(F["body"], len(b), ts, 1.32)) for b in blocks]
    top = block_h(F["hand"], len(t_lines), hs, 1.0) + (1.8 * s if t_lines else 0)
    gap = 2.0 * s
    h = top + sum(heights) + gap * (len(steps) - 1)

    def draw(cv, x, y, tilt):
        cv.lines(F["hand"], t_lines, hs, x, y, 1.0)
        yy = y + top
        for k, (b, bh) in enumerate(zip(blocks, heights)):
            cy = yy + r
            cv.circle(x + r, cy, r)
            cv.text(F["bold"], str(k + 1), 2.9 * s, x + r, cy + 2.9 * s * F["bold"].cap / 2, "middle")
            if k < len(blocks) - 1:
                cv.line([(x + r, cy + r), (x + r, yy + bh + gap)])
            cv.lines(F["body"], b, ts, x + tx, yy + max(0.0, r - block_h(F["body"], 1, ts, 1.32) / 2) if len(b) == 1 else yy,
                     1.32)
            yy += bh + gap
    return h, draw


def _quote(it, w, s):
    F = fonts()
    qs, ms = 5.6 * s, 11 * s
    indent = 6.5 * s
    lines = wrap(F["hand"], fill(it.get("text", "")), qs, w - indent)
    by = block_h(F["hand"], len(lines), qs, 1.02)
    who = fill(it.get("by", ""))
    h = by + (4.5 * s if who else 0)

    def draw(cv, x, y, tilt):
        cv.text(F["title"], "\u201c", ms, x, y + ms * 0.62)
        cv.lines(F["hand"], lines, qs, x + indent, y, 1.02)
        if who:
            cv.text(F["body"], f"- {who}", 2.6 * s, x + w, y + h - 0.6 * s, "end")
    return h, draw


def _text(it, w, s):
    F = fonts()
    t_size, b_size = 3.5 * s, 2.85 * s
    icon = it.get("icon")
    isz = 6.0 * s if icon else 0.0
    t_lines = wrap(F["bold"], fill(it.get("title", "")), t_size, w - (isz + 1.6 * s if icon else 0)) if it.get("title") else []
    b_lines = wrap(F["body"], fill(it.get("text", "")), b_size, w) if it.get("text") else []
    head = max(isz, block_h(F["bold"], len(t_lines), t_size, 1.18)) if (t_lines or icon) else 0.0
    by = head + (1.6 * s if head and b_lines else 0)
    h = by + block_h(F["body"], len(b_lines), b_size, 1.38)

    def draw(cv, x, y, tilt):
        tx = x
        if icon:
            draw_icon(cv, icon, x, y, isz)
            tx += isz + 1.6 * s
        cv.lines(F["bold"], t_lines, t_size, tx, y + (head - block_h(F["bold"], len(t_lines), t_size, 1.18)) / 2, 1.18)
        cv.lines(F["body"], b_lines, b_size, x, y + by, 1.38)
    return h, draw


def _team(it, w, s):
    F = fonts()
    names = [fill(n) for n in it.get("names", []) if str(n).strip()]
    hs, ns = 4.6 * s, 5.4 * s
    title = fill(it.get("title", "Made by"))
    lines = wrap(F["hand"], "  \u00b7  ".join(names), ns, w)
    h = block_h(F["hand"], 1, hs, 1) + 1.4 * s + block_h(F["hand"], len(lines), ns, 1.05)

    def draw(cv, x, y, tilt):
        cv.text(F["hand"], title, hs, x, y + hs * F["hand"].cap)
        tw = F["hand"].width(title, hs)
        cv.line([(x + tw + 2 * s, y + hs * F["hand"].cap * 0.6), (x + w, y + hs * F["hand"].cap * 0.6)])
        cv.lines(F["hand"], lines, ns, x, y + block_h(F["hand"], 1, hs, 1) + 1.4 * s, 1.05)
    return h, draw


def _plan(it, w, s):
    F = fonts()
    span_x = C.ANNEX_W + C.LENGTH
    side = w > 100
    pw = (w - 4 * s) / 2 if side else w
    k = pw / span_x
    ph = C.DEPTH * k
    ls = 3.9 * s
    label_h = block_h(F["hand"], 1, ls, 1) + 1.0 * s
    one = label_h + ph
    h = one if side else 2 * one + 3 * s

    def plan(cv, x, y, level):
        to = lambda px, py: (x + px * k, y + (C.DEPTH - py) * k)  # noqa: E731
        outline = B.FOOTPRINT_MAIN if level == "FF" else unary_union([B.FOOTPRINT_MAIN, B.FOOTPRINT_ANNEX])
        for g in getattr(outline, "geoms", [outline]):
            cv.line([to(*p) for p in g.exterior.coords], closed=True)
        for r in B.ROOMS:
            if r["level"] != level:
                continue
            p = r["poly"]
            for g in getattr(p, "geoms", [p]):
                cv.line([to(*q) for q in g.exterior.coords], closed=True)
            c = p.representative_point()
            bx0, by0, bx1, by1 = p.bounds
            rw, rh = (bx1 - bx0) * k, (by1 - by0) * k
            code = r["id"]
            size = min(2.3 * s, 0.8 * rw / F["bold"].width(code, 1))
            cx, cy = to(c.x, c.y)
            if size >= 1.5:
                cv.text(F["bold"], code, size, cx, cy + size * F["bold"].cap / 2, "middle")
            else:
                size = min(2.3 * s, 0.8 * rh / F["bold"].width(code, 1), 0.8 * rw / F["bold"].cap)
                if size >= 1.3:
                    with cv.rotated(-90, cx, cy):
                        cv.text(F["bold"], code, size, cx, cy + size * F["bold"].cap / 2, "middle")
        if level == "FF":
            vx0, vy0, vx1, vy1 = B.VOID.bounds
            cv.line([to(vx0, vy0), to(vx1, vy1)])
            cv.line([to(vx0, vy1), to(vx1, vy0)])

    def draw(cv, x, y, tilt):
        for i, (level, name) in enumerate((("GF", "Ground floor"), ("FF", "First floor"))):
            ox, oy = (x + i * (pw + 4 * s), y) if side else (x, y + i * (one + 3 * s))
            cv.text(F["hand"], name, ls, ox, oy + ls * F["hand"].cap)
            if i == 0:
                ax = ox + F["hand"].width(name, ls) + 3 * s
                cv.line([(ax, oy + ls * 0.75), (ax, oy)])
                cv.line([(ax - 1.0 * s, oy + 1.4 * s), (ax, oy), (ax + 1.0 * s, oy + 1.4 * s)])
                cv.text(F["bold"], "N", 2.2 * s, ax + 1.6 * s, oy + 2.2 * s * F["bold"].cap)
            plan(cv, ox, oy + label_h, level)
    return h, draw


def _rooms(it, w, s):
    F = fonts()
    skip = set(it.get("skip", ["G06", "F06"]))
    show_area = it.get("areas", True)
    net = json.loads((C.OUT_CAD / "building_metrics.json").read_text())["metrics"]["net_room_areas_m2"]
    side = w > 100
    cw = (w - 4 * s) / 2 if side else w
    hs, rs = 3.2 * s, 2.45 * s
    code_w = F["bold"].width("G00", rs) + 1.4 * s
    area_w = F["body"].width("000 m\u00b2", rs) + 1.0 * s if show_area else 0.0

    def column(level):
        rows = []
        for r in B.ROOMS:
            if r["level"] == level and r["id"] not in skip:
                rows.append((r["id"], wrap(F["body"], r["name"], rs, cw - code_w - area_w), f"{net.get(r['id'], 0):.0f} m\u00b2"))
        return rows
    cols = [("Ground floor", column("GF")), ("First floor", column("FF"))]
    lead = 1.32
    head = block_h(F["bold"], 1, hs, 1) + 1.4 * s

    def col_h(rows):
        return head + sum(block_h(F["body"], len(n), rs, lead) + 0.75 * s for _, n, _ in rows)
    hh = [col_h(r) for _, r in cols]
    h = max(hh) if side else sum(hh) + 3 * s

    def draw(cv, x, y, tilt):
        for i, (name, rows) in enumerate(cols):
            ox, oy = (x + i * (cw + 4 * s), y) if side else (x, y + (hh[0] + 3 * s if i else 0))
            cv.text(F["bold"], name.upper(), hs, ox, oy + hs * F["bold"].cap)
            yy = oy + head
            for code, name_lines, area in rows:
                base = yy + F["body"].cap * rs
                cv.text(F["bold"], code, rs, ox, base)
                cv.lines(F["body"], name_lines, rs, ox + code_w, yy, lead)
                if show_area:
                    cv.text(F["body"], area, rs, ox + cw, base, "end")
                yy += block_h(F["body"], len(name_lines), rs, lead) + 0.75 * s
    return h, draw


def _qr(it, w, s):
    F = fonts()
    url = fill(it.get("url", ""))
    if not url:
        raise ValueError("the qr card needs a url")
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    mat = qr.get_matrix()
    n = len(mat)
    quiet = 4
    size = min(w, float(it.get("size_mm", 44)))
    mod = size / (n + 2 * quiet)
    if mod < 0.9:
        raise ValueError(f"QR modules would be {mod:.2f} mm; give the qr card more width or size_mm (>= 0.9 mm needed)")
    cap = fill(it.get("caption", ""))
    cs, us = 5.0 * s, max(1.9, min(2.4 * s, 0.98 * w / F["body"].width(url, 1)))
    c_lines = wrap(F["hand"], cap, cs, w) if cap else []
    ch = block_h(F["hand"], len(c_lines), cs, 1.0)
    h = ch + size + block_h(F["body"], 1, us, 1)
    dark = unary_union([rect(c * mod, r * mod, (c + 1) * mod, (r + 1) * mod)
                        for r, row in enumerate(mat) for c, v in enumerate(row) if v])

    def draw(cv, x, y, tilt):
        cv.lines(F["hand"], c_lines, cs, x + w / 2, y, 1.0, "middle")
        qx, qy = x + (w - size) / 2, y + ch
        with cv.transform((1, 0, 0, 1, qx + quiet * mod, qy + quiet * mod)):
            cv.shape(dark)
        cv.text(F["body"], url, us, x + w / 2, y + ch + size + us * F["body"].cap, "middle")
    return h, draw, dark, mod * n


CARDS = dict(title=_title, note=_note, stats=_stats, steps=_steps, quote=_quote, text=_text, team=_team,
             plan=_plan, rooms=_rooms, qr=_qr)


def card(it, w, s):
    kind = it.get("type")
    if kind not in CARDS:
        raise ValueError(f"card type '{kind}' is not known; choose from {', '.join(CARDS)}")
    return CARDS[kind](it, w, s)[:2]


def is_wide(it):
    if "wide" in it:
        return bool(it["wide"])
    return it.get("type") in ("title", "plan", "rooms") or (it.get("type") == "stats" and len(it.get("items", [])) > 2)


# ---------------------------------------------------------------------------------------
# Wall geometry: four identical boards standing in the slot round the site model's rim
# ---------------------------------------------------------------------------------------
WALLS = ("south", "east", "north", "west")
# Seen from outside, each wall's left end butts the inner face of the previous wall and its
# right end runs into the next corner (a pinwheel), so all four boards are the same size.
# Ruler origin (the site corner at the reader's left) and direction, in half-widths.
RULER = dict(south=((-1, -1), (1, 0)), east=((1, -1), (0, 1)), north=((1, 1), (-1, 0)), west=((-1, 1), (0, -1)))


class Wall:
    def __init__(self, cfg, height):
        fr = S.wall_frame()
        self.cfg, self.frame = cfg, fr
        self.length = 2 * (fr["half"] - fr["lip"]) - fr["slot"] - C.SITE_WALL_END_CLEARANCE_MM
        self.offset = fr["lip"] + fr["slot"] + C.SITE_WALL_END_CLEARANCE_MM / 2
        self.visible = float(height)
        self.h = self.visible + fr["depth"]
        self.pitch = float(cfg["tooth_pitch_mm"])
        self.rise = self.pitch * math.tan(ROOF_TILT) if self.pitch > 0 else 0.0
        self.ruler_h = 14.0
        self.content_top = self.rise + MARGIN
        self.content_bottom = self.visible - self.ruler_h - 1.5
        self.col_w = (self.length - 2 * MARGIN - (COLS_PER_PANEL - 1) * GUTTER) / COLS_PER_PANEL

    def column_x(self, c):
        return MARGIN + c * (self.col_w + GUTTER)

    def outline(self):
        """Board outline as seen from outside: sawtooth top, chamfered foot that drops into the slot."""
        L, H, rise, ch = self.length, self.h, self.rise, 1.0
        top = [(0.0, rise)]
        if self.pitch > 0:
            teeth = max(1, round(L / self.pitch))
            p = L / teeth
            for k in range(teeth):
                top += [((k + 1) * p, 0.0), ((k + 1) * p, rise)] if k < teeth - 1 else [(L, 0.0)]
        else:
            top += [(L, rise)]
        return Polygon(top + [(L, H - ch), (L - ch, H), (ch, H), (0.0, H - ch)])


def draw_ruler(cv, wall, name):
    """1:1000 ruler along the visible foot, in metres from the site corner at the reader's left."""
    F = fonts()
    half = wall.frame["half"]
    (sx, sy), (dx, dy) = RULER[name]
    X = lambda e: e - wall.offset  # noqa: E731
    yb = wall.visible - 6.5
    lo = math.ceil((wall.offset + MARGIN) / 10) * 10
    hi = math.floor((wall.offset + wall.length - MARGIN) / 10) * 10
    cv.line([(X(lo), yb), (X(hi), yb)])
    for d in range(lo, hi + 1, 10):
        major = d % 50 == 0
        cv.line([(X(d), yb), (X(d), yb + (2.6 if major else 1.3))])
        if major:
            cv.text(F["body"], f"{d} m", 2.0, X(d), wall.visible - 1.4, "middle")
    cv.text(F["body"], f"1:{C.SITE_SCALE}", 2.0, wall.length - MARGIN, wall.visible - 1.4, "end")
    cx, cy = C.SITE_CENTRE_LOCAL
    fp = unary_union([B.FOOTPRINT_MAIN, B.FOOTPRINT_ANNEX])
    ds = [(x - cx - sx * half) * dx + (y - cy - sy * half) * dy for x, y in fp.exterior.coords]
    a, b = sorted((X(min(ds)), X(max(ds))))
    yk = yb - 2.6
    cv.line([(a, yb - 0.6), (a, yk), (b, yk), (b, yb - 0.6)])
    label = "The Heat Exchange is right behind here"
    ls = 3.4
    lw = F["hand"].width(label, ls)
    lx = min(max((a + b) / 2, lw / 2 + 2 * MARGIN), wall.length - lw / 2 - 2 * MARGIN)
    cv.text(F["hand"], label, ls, lx, yk - 1.2, "middle")


def draw_slot_label(cv, wall, name):
    """Small label on the strip that sits down in the rim slot, so it is hidden once in place."""
    F = fonts()
    size = min(2.4, 0.45 * wall.frame["depth"])
    k = WALLS.index(name) + 1
    text = f"{name.upper()} WALL  \u00b7  {k} of 4  \u00b7  this strip drops into the rim slot  \u00b7  engraved face outwards"
    cv.text(F["bold"], text, size, wall.length / 2, wall.visible + wall.frame["depth"] / 2 + size * F["bold"].cap / 2,
            "middle")


# ---------------------------------------------------------------------------------------
# Layout: masonry over 4 walls x 4 columns, then find the most comfortable fit
# ---------------------------------------------------------------------------------------
def card_wall(it):
    w = it.get("wall")
    if w is None:
        return None
    w = str(w).lower()
    if w not in WALLS:
        raise ValueError(f"card '{it.get('title') or it.get('type')}': wall must be one of {', '.join(WALLS)}")
    return WALLS.index(w)


def layout(items, wall, s):
    """Place every card, or return None if something does not fit.

    Cards are packed in their listed order, then wide cards first, then tallest first; the
    packing with the shortest tallest column wins. Cards without a "wall" go wherever there
    is room once the others are placed.
    """
    pinned = lambda i: ({"start": 0, "end": 1}.get(items[i].get("place"), 2), card_wall(items[i]) is None)  # noqa: E731
    w1 = wall.col_w
    heights = [card(it, 2 * w1 + GUTTER if is_wide(it) else w1, s)[0] for it in items]
    orders = [sorted(range(len(items)), key=pinned),
              sorted(range(len(items)), key=lambda i: (pinned(i), not is_wide(items[i]))),
              sorted(range(len(items)), key=lambda i: (pinned(i), -heights[i] * (2 if is_wide(items[i]) else 1)))]
    best = None
    for order in orders:
        res = _pack(items, wall, s, order)
        if res and (best is None or max(res[1]) < max(best[1]) - 1e-6):
            best = res
    return best


def _pack(items, wall, s, order):
    n = COLS_PER_PANEL
    fill_ = [0.0] * (n * len(WALLS))
    avail = wall.content_bottom - wall.content_top
    gap = 3.2 * s
    placed = []
    for i in order:
        it = items[i]
        span = 2 if is_wide(it) else 1
        place = it.get("place")
        w = card_wall(it)
        walls = range(len(WALLS)) if w is None else [w]
        if place == "start":
            starts = [k * n for k in walls]
        elif place == "end":
            starts = [k * n + n - span for k in walls]
        else:
            starts = [k * n + c for k in walls for c in range(n - span + 1)]
        c = min(starts, key=lambda c: (max(fill_[c:c + span]), c))
        cw = span * wall.col_w + (span - 1) * GUTTER
        h, draw = card(it, cw, s)
        y = max(fill_[c:c + span])
        y += gap if y > 0 else 0
        if y + h > avail + 1e-6:
            return None
        for k in range(c, c + span):
            fill_[k] = y + h
        placed.append((c, span, y, cw, h, draw))
    return placed, fill_


def fit(items, cfg):
    h0, hmax = float(cfg["height_mm"]), float(cfg["max_height_mm"])
    smin, smax = float(cfg["min_text_scale"]), float(cfg["max_text_scale"])

    def best(height, lo, hi):
        wall = Wall(cfg, height)
        if layout(items, wall, lo) is None:
            return None
        for _ in range(14):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if layout(items, wall, mid) is not None else (lo, mid)
        return lo
    height = h0
    while height <= hmax + 1e-6:
        s = best(height, 1.0, smax)
        if s:
            return Wall(cfg, height), s
        height += 5
    s = best(hmax, smin, 1.0)
    if s:
        return Wall(cfg, hmax), s
    raise ValueError(f"The cards do not fit even on {hmax:.0f} mm walls with text at {smin:.0%} size. "
                     "Shorten or remove a card, move one to a less busy wall, or raise wall.max_height_mm "
                     "in Poster/laser_wall.json.")


# ---------------------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------------------
def svg(cv, w, h, colours, preview=False):
    if preview:
        styles = dict(cut='fill="none" stroke="#6b4423" stroke-width="0.35"',
                      score='fill="none" stroke="#7a4b26" stroke-width="0.25"',
                      engrave='fill="#4a2c14" stroke="none"')
    else:
        styles = {k: (f'fill="none" stroke="{colours[k]}" stroke-width="0.025"' if k != "engrave"
                      else f'fill="{colours[k]}" stroke="none"') for k in ("cut", "score", "engrave")}
    body = []
    for k in ("engrave", "score", "cut"):
        if cv.layers[k]:
            body.append(f'<g id="{k}" {styles[k]}>' + "".join(f'<path d="{d}"/>' for d in cv.layers[k]) + "</g>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{_num(w)}mm" height="{_num(h)}mm" '
            f'viewBox="0 0 {_num(w)} {_num(h)}">' + "".join(body) + "</svg>\n")


def draw_panel(cv, wall, name, placed, extra, outline_offset=0.0):
    """Cut outline, ruler, slot label, cards and doodles of one wall. Returns the (unkerfed) outline."""
    k = WALLS.index(name)
    outline = wall.outline()
    cut = outline.buffer(outline_offset, join_style=2) if outline_offset else outline
    cv.line(list(cut.exterior.coords)[:-1], "cut", closed=True)
    draw_ruler(cv, wall, name)
    draw_slot_label(cv, wall, name)
    for j, (c, span, y, w, h, draw) in enumerate(placed):
        if c // COLS_PER_PANEL == k:
            draw(cv, wall.column_x(c % COLS_PER_PANEL), wall.content_top + y, 1 if j % 2 else -1)
    for c, y, size, icons in extra:
        if c // COLS_PER_PANEL != k:
            continue
        step = wall.col_w / len(icons)
        for j, icon in enumerate(icons):
            cx = wall.column_x(c % COLS_PER_PANEL) + step * (j + 0.5)
            cy = wall.content_top + y + size / 2
            with cv.rotated(((c * 37 + j * 53) % 30) - 15, cx, cy):
                draw_icon(cv, icon, cx - size / 2, cy - size / 2, size)
    return outline


def _path_points(d):
    pts, cur, cmd, nums = [], (0.0, 0.0), "M", []
    for tok in re.findall(r"[MLQCHVZ]|-?[\d.]+(?:e-?\d+)?", d):
        if tok.isalpha():
            cmd, nums = tok, []
            continue
        nums.append(float(tok))
        if cmd == "H":
            cur = (nums.pop(), cur[1])
        elif cmd == "V":
            cur = (cur[0], nums.pop())
        elif len(nums) == 2:
            cur = (nums[0], nums[1])
            nums = []
        else:
            continue
        pts.append(cur)
    return pts


def check_inside(cv, outline, name):
    """Every engraved or scored mark must stay at least 1 mm inside the panel's cut edge."""
    safe = outline.buffer(-1.0)
    for layer in ("engrave", "score"):
        for d in cv.layers[layer]:
            bad = [p for p in _path_points(d) if not safe.contains(Point(p))]
            if bad:
                x, y = bad[0]
                raise ValueError(f"{name}: an engraved mark at ({x:.0f}, {y:.0f}) mm runs off the panel edge; "
                                 "a word is probably too long for its card")


def doodles(wall, placed, fill_, s):
    """Little engraved doodles in leftover space at the foot of short columns."""
    avail = wall.content_bottom - wall.content_top
    out = []
    for c, used in enumerate(fill_):
        room = avail - used - 3 * s
        if room < 9:
            continue
        size = min(11.0, room * 0.55)
        n = max(1, min(3, int(wall.col_w // (size * 1.9))))
        names = [DOODLES[(c * 3 + k) % len(DOODLES)] for k in range(n)]
        out.append((c, used + 3 * s + (room - size) / 2, size, names))
    return out


def fit_coupon(kerf):
    """A short offcut of the wall's foot: test it in the printed rim slot before cutting the walls."""
    w, h, ch = 30.0, 16.0, 1.0
    return Polygon([(0, 0), (w, 0), (w, h - ch), (w - ch, h), (ch, h), (0, h - ch)]).buffer(kerf, join_style=2)


def build():
    data = json.loads(CONTENT.read_text())
    user = data.get("wall", {})
    for old in ("corner", "thickness_mm", "board_mm", "finger_mm"):
        if old in user:
            print(f"note: wall.{old} is no longer used (four slot-in walls; ply thickness is WALL_PLY_MM in src/config.py)")
    cfg = {**WALL_DEFAULTS, **user}
    cfg["layers"] = {**WALL_DEFAULTS["layers"], **cfg.get("layers", {})}
    items = [it for it in data.get("cards", []) if it.get("enabled", True)]
    for it in items:
        card_wall(it)
        if it.get("type") == "team" and not [n for n in it.get("names", []) if str(n).strip()]:
            print("note: the team card has no names yet, so it is left off the wall")
    items = [it for it in items if not (it.get("type") == "team" and not [n for n in it.get("names", []) if str(n).strip()])]
    wall, s = fit(items, cfg)
    placed, fill_ = layout(items, wall, s)
    extra = doodles(wall, placed, fill_, s)
    kerf = float(cfg["kerf_mm"]) / 2
    OUT.mkdir(parents=True, exist_ok=True)
    for old in [*OUT.glob("*.svg"), *OUT.glob("*.png")]:
        old.unlink()

    files = []
    for k, name in enumerate(WALLS):
        check = Canvas()
        check_inside(check, draw_panel(check, wall, name, placed, extra), f"{name} wall")
        cv = Canvas()
        with cv.transform((1, 0, 0, 1, 1, 1)):
            draw_panel(cv, wall, name, placed, extra, kerf)
        f = OUT / f"wall_{k + 1}_{name}.svg"
        f.write_text(svg(cv, wall.length + 2, wall.h + 2, cfg["layers"]))
        files.append(f)

    # Cut sheets: walls packed in rows, then a QR scan test and a slot fit coupon in the spare space.
    sw, sh = (float(v) for v in cfg["sheet_mm"])
    edge, gap = 5.0, 4.0
    if wall.length + 2 * edge > sw or wall.h + 2 * edge > sh:
        raise ValueError(f"a {wall.length:.0f} x {wall.h:.0f} mm wall does not fit on a {sw:.0f} x {sh:.0f} mm sheet; "
                         "set wall.sheet_mm in Poster/laser_wall.json to the laser bed size")
    sheets, x, y = [Canvas()], edge, edge
    for name in WALLS:
        if x + wall.length > sw - edge:
            x, y = edge, y + wall.h + gap
        if y + wall.h > sh - edge:
            sheets.append(Canvas())
            x, y = edge, edge
        with sheets[-1].transform((1, 0, 0, 1, x, y)):
            draw_panel(sheets[-1], wall, name, placed, extra, kerf)
        x += wall.length + gap
    qr_items = [it for it in items if it.get("type") == "qr"]
    qsize = _qr(qr_items[0], 60, 1.0)[3] if qr_items else 0.0
    tile = 4 + qsize + 4 if qr_items else 0.0
    tw, th = max(tile, 34.0) + 2, tile + 8 + 16 + 8
    spots = [(x, y, wall.h), (edge, y + wall.h + gap, sh - edge - (y + wall.h + gap))]
    tx, ty = next(((px, py) for px, py, room in spots if px + tw <= sw - edge and th <= room), (None, None))
    if tx is None:
        sheets.append(Canvas())
        tx, ty = edge, edge
    sheet, F = sheets[-1], fonts()
    if qr_items:
        _, _, dark, _ = _qr(qr_items[0], 60, 1.0)
        sheet.line([(tx, ty), (tx + tile, ty), (tx + tile, ty + tile), (tx, ty + tile)], "cut", closed=True)
        with sheet.transform((1, 0, 0, 1, tx + 4, ty + 4)):
            sheet.shape(dark)
        sheet.text(F["body"], "QR scan test: engrave + cut this first", 2.2, tx, ty + tile + 4)
    cy = ty + tile + 8
    with sheet.transform((1, 0, 0, 1, tx, cy)):
        sheet.line(list(fit_coupon(kerf).exterior.coords)[:-1], "cut", closed=True)
    sheet.text(F["body"], "Slot fit test: should slide into the rim slot", 2.2, tx, cy + 16 + 4)
    for i, sh_cv in enumerate(sheets):
        f = OUT / (f"cut_sheet_{sw:.0f}x{sh:.0f}.svg" if len(sheets) == 1 else f"cut_sheet_{i + 1}_{sw:.0f}x{sh:.0f}.svg")
        f.write_text(svg(sh_cv, sw, sh, cfg["layers"]))
        files.append(f)

    # Preview: the four outer faces in reading order (walk round the model anticlockwise).
    gx, gy, head = 8.0, 6.0, 7.0
    pv = Canvas()
    wood = []
    for k, name in enumerate(WALLS):
        r, c = divmod(k, 2)
        ox, oy = 6 + c * (wall.length + gx), 6 + head + r * (wall.h + gy + head)
        pv.text(F["bold"], f"{k + 1}. {name.capitalize()} wall", 4.0, ox, oy - 2.2)
        with pv.transform((1, 0, 0, 1, ox, oy)):
            outline = draw_panel(pv, wall, name, placed, extra)
        wood.append("M" + " L".join(f"{_num(ox + px)},{_num(oy + py)}" for px, py in list(outline.exterior.coords)[:-1]) + " Z")
        pv.line([(ox, oy + wall.visible), (ox + wall.length, oy + wall.visible)])
    pw, ph = 12 + 2 * wall.length + gx, 12 + 2 * (wall.h + head) + gy
    preview = svg(pv, pw, ph, cfg["layers"], preview=True).replace(
        f'viewBox="0 0 {_num(pw)} {_num(ph)}">',
        f'viewBox="0 0 {_num(pw)} {_num(ph)}"><rect width="100%" height="100%" fill="#ffffff"/>'
        + "".join(f'<path d="{d}" fill="#e3c08e"/>' for d in wood))
    f = OUT / "preview.svg"
    f.write_text(preview)
    files.append(f)
    try:
        subprocess.run(["rsvg-convert", "-d", "200", "-p", "200", "-o", str(OUT / "preview.png"), str(f)], check=True)
    except (OSError, subprocess.CalledProcessError):
        pass

    summary = dict(visible_height_mm=round(wall.visible, 1), board_mm=[round(wall.length, 1), round(wall.h, 1)],
                   ply_mm=C.WALL_PLY_MM, text_scale=round(s, 2), body_text_mm=round(2.85 * s, 2),
                   sheets=len(sheets), cards=len(items))
    print(f"4 walls, each {wall.length:.1f} x {wall.h:.0f} mm ({wall.visible:.0f} mm showing above the rim), "
          f"text at {s:.0%} ({2.85 * s:.1f} mm body text), {len(items)} cards on {len(sheets)} sheet(s)")
    return files, summary


if __name__ == "__main__":
    build()
