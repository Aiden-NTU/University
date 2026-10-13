"""Render LaTeX maths to transparent PNGs, batched and cached.

Chapters are built twice when needed: the first pass records every formula that
is not yet cached (using estimated sizes), the formulas are rendered in one
LaTeX run, then the chapter is rebuilt with exact sizes.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "build", "cache", "eq")
os.makedirs(CACHE, exist_ok=True)

DPI = 600
BASE_PT = 12.0

PREAMBLE = r"""
\documentclass[12pt]{article}
\usepackage{amsmath,amssymb,xcolor,cancel,bm,mathtools}
\usepackage[active,tightpage]{preview}
\definecolor{ink}{HTML}{1A1A1A}
\definecolor{cblu}{HTML}{1F5FBF}
\definecolor{corg}{HTML}{E07000}
\definecolor{cgrn}{HTML}{1E8A3C}
\definecolor{cred}{HTML}{C62828}
\definecolor{cpur}{HTML}{7B3FB5}
\definecolor{cgry}{HTML}{8A8A8A}
\definecolor{cteal}{HTML}{00838F}
\definecolor{cpink}{HTML}{C2185B}
\definecolor{cbrn}{HTML}{8D5524}
\newcommand{\blu}[1]{{\color{cblu}#1}}
\newcommand{\org}[1]{{\color{corg}#1}}
\newcommand{\grn}[1]{{\color{cgrn}#1}}
\newcommand{\red}[1]{{\color{cred}#1}}
\newcommand{\pur}[1]{{\color{cpur}#1}}
\newcommand{\gry}[1]{{\color{cgry}#1}}
\newcommand{\tea}[1]{{\color{cteal}#1}}
\newcommand{\pnk}[1]{{\color{cpink}#1}}
\newcommand{\brn}[1]{{\color{cbrn}#1}}
\renewcommand{\CancelColor}{\color{cred}}
\newcommand{\dd}{\mathrm{d}}
\pagestyle{empty}
\begin{document}
"""

_index_path = os.path.join(CACHE, "index.json")
try:
    with open(_index_path) as f:
        _index = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _index = {}

_missing = {}


def _key(latex, color, display):
    return hashlib.sha1(f"{latex}\x00{color}\x00{display}".encode()).hexdigest()


def _body(latex, color, display):
    style = r"\displaystyle " if display else r"\textstyle "
    return r"\begin{preview}{\color{%s}$%s%s$}\end{preview}" % (color, style, latex)


def get(latex, color="ink", display=True):
    """Return dict(w, h, depth, png) in points at BASE_PT, or an estimate + None png."""
    k = _key(latex, color, display)
    meta = _index.get(k)
    if meta and os.path.exists(os.path.join(CACHE, k + ".png")):
        with open(os.path.join(CACHE, k + ".png"), "rb") as f:
            png = f.read()
        s = 72.0 / DPI
        return dict(w=meta["w"] * s, h=meta["h"] * s, depth=meta["d"] * s, png=png)
    _missing[k] = (latex, color, display)
    plain = re.sub(r"\\[a-zA-Z]+|[{}^_]", "", latex)
    tall = 2.2 if (r"\frac" in latex or r"\int" in latex or r"\sum" in latex) else 1.0
    return dict(w=max(6.0, 6.5 * len(plain)), h=12 * tall, depth=3 * tall, png=None)


def missing_count():
    return len(_missing)


def _run_batch(items, workdir):
    tex = PREAMBLE + "\n".join(_body(*it) for it in items) + "\n\\end{document}\n"
    with open(os.path.join(workdir, "b.tex"), "w") as f:
        f.write(tex)
    r = subprocess.run(
        ["latex", "-interaction=nonstopmode", "-halt-on-error", "b.tex"],
        cwd=workdir, capture_output=True, text=True, errors="replace",
    )
    if r.returncode != 0:
        return None, r.stdout[-3000:]
    r = subprocess.run(
        ["dvipng", "-D", str(DPI), "-T", "tight", "-bg", "Transparent", "--depth",
         "--height", "-z", "9", "-q", "-o", "p%d.png", "b.dvi"],
        cwd=workdir, capture_output=True, text=True, errors="replace",
    )
    metas = re.findall(r"depth=(-?\d+)\s+height=(-?\d+)", r.stdout)
    return metas, None


def flush():
    """Render everything recorded as missing. Raises with the bad formula on error."""
    global _missing
    if not _missing:
        return 0
    from PIL import Image as PILImage

    keys = list(_missing.keys())
    items = [_missing[k] for k in keys]

    def render(keys, items):
        with tempfile.TemporaryDirectory() as wd:
            metas, err = _run_batch(items, wd)
            if metas is None:
                if len(items) == 1:
                    raise RuntimeError(f"LaTeX failed for: {items[0][0]}\n{err}")
                mid = len(items) // 2
                render(keys[:mid], items[:mid])
                render(keys[mid:], items[mid:])
                return
            for i, k in enumerate(keys):
                src = os.path.join(wd, f"p{i + 1}.png")
                im = PILImage.open(src)
                w, h = im.size
                d = int(metas[i][0])
                shutil.move(src, os.path.join(CACHE, k + ".png"))
                _index[k] = dict(w=w, h=h, d=d)

    render(keys, items)
    n = len(keys)
    _missing = {}
    with open(_index_path, "w") as f:
        json.dump(_index, f)
    return n
