#!/usr/bin/env python3
"""Make review contact sheets from preview PNGs.

    python3 sheet.py 02-Fractions 1 6    -> build/sheet.png with pages 1..6 (3 across)
"""
import glob
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
base, start, count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 3
files = sorted(glob.glob(os.path.join(HERE, "build", "preview", base, "p-*.png")))
files = files[start - 1:start - 1 + count]
ims = [Image.open(f) for f in files]
w, h = ims[0].size
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w + (cols - 1) * 10, rows * h + (rows - 1) * 10), "#777777")
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * (w + 10), (i // cols) * (h + 10)))
out = os.path.join(HERE, "build", f"sheet-{base}-{start}.png")
sheet.save(out)
print(out, len(ims), "pages")
