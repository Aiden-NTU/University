#!/usr/bin/env python3
"""Build the Visual Maths Guide.

    python3 build.py              build every chapter
    python3 build.py 2 14         build only chapters 2 and 14
    python3 build.py --no-pdf     skip PDF export / previews
    python3 build.py --book-only  only re-join the chapters into the full book

Every run finishes by joining all chapters into one printable book:
output/Maths-Visual-Guide-Complete.xopp and output/PDF/Maths-Visual-Guide-Complete.pdf
"""
import glob
import gzip
import importlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from generator import eq as EQ  # noqa: E402
from generator.book import Chapter  # noqa: E402

OUT = os.path.join(HERE, "output")
PDF = os.path.join(OUT, "PDF")
PREV = os.path.join(HERE, "build", "preview")
REG = os.path.join(HERE, "build", "registry")
BOOK = "Maths-Visual-Guide-Complete"
for d in (OUT, PDF, PREV, REG):
    os.makedirs(d, exist_ok=True)


def modules():
    mods = []
    for path in sorted(glob.glob(os.path.join(HERE, "content", "c[0-9]*.py"))):
        name = os.path.splitext(os.path.basename(path))[0]
        mods.append(importlib.import_module(f"content.{name}"))
    mods.sort(key=lambda m: m.ORDER)
    return mods


def check_prereqs(mods):
    """Every concept a chapter REQUIRES must be INTRODUCED by an earlier chapter.

    Concepts introduced by a *later* chapter are always an error. Concepts nobody
    introduces are an error once every chapter exists (a warning before that)."""
    taught = {}
    for m in mods:
        for c in getattr(m, "INTRODUCES", []):
            taught.setdefault(c, m.ORDER)
    complete = len([m for m in mods if isinstance(m.ORDER, int) and m.ORDER <= 38]) >= 39
    errors, warnings = [], []
    for m in mods:
        for r in getattr(m, "REQUIRES", []):
            where = taught.get(r)
            if where is None:
                (errors if complete else warnings).append(
                    f"{m.__name__}: requires '{r}' which no chapter introduces")
            elif where >= m.ORDER:
                errors.append(f"{m.__name__}: requires '{r}' but it is only introduced in chapter {where}")
    for w in warnings:
        print("   (pending)", w)
    return errors


def build_one(m, pdf=True):
    t0 = time.time()
    for attempt in range(4):
        ch = Chapter(m.NUM, m.TITLE, m.SHORT, m.SLUG, getattr(m, "ACCENT", "#1f5fbf"))
        m.build(ch)
        if EQ.missing_count() == 0:
            break
        n = EQ.flush()
        print(f"   rendered {n} formulas")
    else:
        raise RuntimeError("formulas kept changing between passes")
    ch.finalize()
    base = f"{m.ORDER:02d}-{m.SLUG}"
    xo = os.path.join(OUT, base + ".xopp")
    ch.save(xo)
    probs = ch.overlaps()
    with open(os.path.join(REG, base + ".json"), "w") as f:
        json.dump(dict(num=m.NUM, order=m.ORDER, title=m.TITLE, short=m.SHORT,
                       terms=ch.terms, symbols=ch.symbols, formulas=ch.formulas,
                       pages=len(ch.pages)), f, indent=1)
    msg = f"{base}: {len(ch.pages)} pages, {ch.checks} answer checks, {len(probs)} layout warnings"
    if pdf:
        pdfp = os.path.join(PDF, base + ".pdf")
        r = subprocess.run(["xournalpp", f"--create-pdf={pdfp}", xo], capture_output=True, text=True)
        if "successfully" not in (r.stdout + r.stderr):
            raise RuntimeError(f"xournalpp could not export {xo}:\n{r.stderr[-2000:]}")
        pdir = os.path.join(PREV, base)
        os.makedirs(pdir, exist_ok=True)
        for old in glob.glob(os.path.join(pdir, "*.png")):
            os.remove(old)
        subprocess.run(["pdftoppm", "-r", "80", "-png", pdfp, os.path.join(pdir, "p")])
    print(f"{msg}  ({time.time() - t0:.1f}s)")
    for p in probs[:40]:
        print("   !", p)
    return ch


def build_book(mods, pdf=True):
    """Join every chapter (in book order) into one .xopp and one bookmarked PDF."""
    t0 = time.time()
    parts, missing = [], []
    for m in mods:
        base = f"{m.ORDER:02d}-{m.SLUG}"
        xo = os.path.join(OUT, base + ".xopp")
        if os.path.exists(xo):
            parts.append((m, base, xo))
        else:
            missing.append(base)
    if missing:
        print("   (book) not built yet, skipped:", ", ".join(missing))
    if not parts:
        return
    head, pages = None, []
    for m, base, xo in parts:
        x = gzip.open(xo).read().decode("utf-8")
        start, end = x.index("<page "), x.rindex("</xournal>")
        if head is None:
            head = x[:x.index("<title>")]
        pages.append(x[start:end])
    doc = head + "<title>Maths Visual Guide (complete)</title>\n" + "".join(pages) + "</xournal>\n"
    with gzip.open(os.path.join(OUT, BOOK + ".xopp"), "wb") as f:
        f.write(doc.encode("utf-8"))
    n_pages = doc.count("<page ")
    if pdf:
        pdfs = [(m, os.path.join(PDF, base + ".pdf")) for m, base, _ in parts]
        pdfs = [(m, p) for m, p in pdfs if os.path.exists(p)]
        out = os.path.join(PDF, BOOK + ".pdf")
        try:
            import pymupdf
        except ImportError:
            pymupdf = None
        if pymupdf:
            book, toc = pymupdf.open(), []
            for m, p in pdfs:
                toc.append([1, m.TITLE, book.page_count + 1])
                with pymupdf.open(p) as part:
                    book.insert_pdf(part)
            book.set_toc(toc)
            book.set_metadata({"title": "Maths Visual Guide (complete)"})
            book.save(out, garbage=3, deflate=True)
            book.close()
        else:
            subprocess.run(["pdfunite", *[p for _, p in pdfs], out], check=True)
    print(f"{BOOK}: {len(parts)} chapters, {n_pages} pages  ({time.time() - t0:.1f}s)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pdf = "--no-pdf" not in sys.argv
    mods = modules()
    if "--book-only" in sys.argv:
        build_book(mods, pdf)
        return
    errs = check_prereqs(mods)
    if errs:
        print("PREREQUISITE ERRORS:")
        for e in errs:
            print("  ", e)
        sys.exit(1)
    sel = [m for m in mods if not args or str(m.ORDER) in args or m.SLUG in args]
    total = 0
    for m in sel:
        ch = build_one(m, pdf)
        total += len(ch.pages)
    print(f"built {len(sel)} file(s), {total} pages")
    build_book(mods, pdf)


if __name__ == "__main__":
    main()
