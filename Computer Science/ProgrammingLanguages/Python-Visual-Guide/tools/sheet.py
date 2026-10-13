"""Contact sheet of a chapter's preview pages, for a quick layout check: python3 tools/sheet.py 17-Quality"""
import glob
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sheet(slug, cols=5, scale=0.42):
    paths = sorted(glob.glob(os.path.join(HERE, "build", "preview", slug, "p-*.png")))
    pages = [Image.open(p) for p in paths]
    w, h = int(pages[0].width * scale), int(pages[0].height * scale)
    rows = (len(pages) + cols - 1) // cols
    out = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 8) + 8), "#888888")
    for i, im in enumerate(pages):
        x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 8)
        out.paste(im.convert("RGB").resize((w, h)), (x, y))
        ImageDraw.Draw(out).text((x + 4, y + 4), str(i + 1), fill="#d00000")
    dst = os.path.join(HERE, "build", f"sheet-{slug}.png")
    out.save(dst)
    print(dst)


if __name__ == "__main__":
    sheet(sys.argv[1])
