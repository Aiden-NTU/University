"""Minimal writer for Xournal++ .xopp files (gzipped XML, fileversion 4)."""
import base64
import gzip
from xml.sax.saxutils import escape, quoteattr

A4_W = 595.27559
A4_H = 841.88976


def _col(c):
    """Accept '#rrggbb' or '#rrggbbaa' and return '#rrggbbaa'."""
    c = c.lower()
    if len(c) == 7:
        c += "ff"
    return c


class Stroke:
    kind = "stroke"

    def __init__(self, pts, color="#000000", width=1.4, tool="pen", fill=None):
        self.pts = pts
        self.color = color
        self.width = width
        self.tool = tool
        self.fill = fill

    def bbox(self):
        xs = [p[0] for p in self.pts]
        ys = [p[1] for p in self.pts]
        w = self.width / 2
        return (min(xs) - w, min(ys) - w, max(xs) + w, max(ys) + w)

    def xml(self):
        attrs = f'tool="{self.tool}" color="{_col(self.color)}" width="{self.width:.2f}"'
        if self.fill is not None:
            attrs += f' fill="{int(self.fill)}"'
        if self.tool == "pen":
            attrs += ' capStyle="round"'
        coords = " ".join(f"{x:.2f} {y:.2f}" for x, y in self.pts)
        return f"<stroke {attrs}>{coords}</stroke>"


class Text:
    kind = "text"

    def __init__(self, x, y, text, size=13, font="DejaVu Sans", color="#1a1a1a", w=0, h=0):
        self.x, self.y, self.text = x, y, text
        self.size, self.font, self.color = size, font, color
        self.w, self.h = w, h

    def bbox(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def xml(self):
        return (
            f'<text font={quoteattr(self.font)} size="{self.size:.2f}" x="{self.x:.2f}" '
            f'y="{self.y:.2f}" color="{_col(self.color)}">{escape(self.text)}</text>'
        )


class Image:
    kind = "image"

    def __init__(self, x, y, w, h, png_bytes):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.png = png_bytes

    def bbox(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def xml(self):
        data = base64.b64encode(self.png).decode()
        return (
            f'<image left="{self.x:.2f}" top="{self.y:.2f}" right="{self.x + self.w:.2f}" '
            f'bottom="{self.y + self.h:.2f}">{data}</image>'
        )


class XPage:
    def __init__(self, w=A4_W, h=A4_H, bg="#ffffff", style="plain"):
        self.w, self.h = w, h
        self.bg, self.style = bg, style
        self.layers = [[]]

    def add(self, el, layer=0):
        while len(self.layers) <= layer:
            self.layers.append([])
        self.layers[layer].append(el)
        return el

    def xml(self):
        out = [
            f'<page width="{self.w:.5f}" height="{self.h:.5f}">',
            f'<background type="solid" color="{_col(self.bg)}" style="{self.style}"/>',
        ]
        for layer in self.layers:
            out.append("<layer>")
            out.extend(el.xml() for el in layer)
            out.append("</layer>")
        out.append("</page>")
        return "\n".join(out)


def save(pages, path, title="Maths Visual Guide"):
    body = "\n".join(p.xml() for p in pages)
    doc = (
        '<?xml version="1.0" standalone="no"?>\n'
        '<xournal creator="Xournal++ 1.3.6" fileversion="4">\n'
        f"<title>{escape(title)}</title>\n{body}\n</xournal>\n"
    )
    with open(path, "wb") as f:
        f.write(gzip.compress(doc.encode("utf-8"), compresslevel=6))
