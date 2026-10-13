"""Chapter 8 - Files and formats: bytes vs text and UTF-8, open modes, pathlib, CSV, JSON, TOML,
pickle's danger, atomic writes, binary formats with struct, compression and archives."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, W, callout, code, flow, go, pipe, practice, repl, section, shell, stamp, sub, table,
                         title_block, tree, two_ways)

ORDER = 8
NUM = 8
TITLE = "Files and data formats"
SHORT = "Files and formats"
SLUG = "Files-and-formats"
ACCENT = C.ORANGE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def utf8_picture(f):
    chars = ["A", "é", "€", "🙂"]
    y = f.reserve(120)
    pg = f.pg
    x = L + 10
    for ch_ in chars:
        bs = ch_.encode("utf-8")
        bw = 32
        total = len(bs) * bw
        label = "emoji" if ch_ == "🙂" else ch_
        pg.rect(x, y, total, 34, C.BLUE, 1.2, fillcolor=C.LIGHT[C.BLUE], r=5)
        pg.text(x + total / 2, y + 7, label, 15 if label != "emoji" else 11, C.BLUE, F.BOLD, align="center")
        for k, b in enumerate(bs):
            bx = x + k * bw
            pg.rect(bx + 2, y + 44, bw - 4, 26, C.ORANGE, 1.0, fillcolor=C.LIGHT[C.ORANGE], r=3)
            pg.text(bx + bw / 2, y + 50, f"{b:02x}", 10.5, C.INK, F.MONO, align="center")
        pg.text(x + total / 2, y + 76, f"U+{ord(ch_):04X}", 9, C.GREY, F.MONO, align="center")
        pg.text(x + total / 2, y + 90, f"{len(bs)} byte{'s' if len(bs) > 1 else ''}", 9, C.GREY, align="center")
        x += total + 18
    pg.note(x + 4, y + 8, "1 character,\n1 to 4 bytes", C.PURPLE, 14, w=100)


def title_page(ch):
    title_block(ch, 8, TITLE, "a file is bytes; text is bytes plus an agreed encoding", ACCENT)
    f = ch.flow(top=190)
    f.p("Every file is a sequence of {B:bytes} (numbers 0–255). Text only exists once you agree how bytes map "
        "to characters: an {B:encoding}. Python keeps the two apart with two types: `bytes` for raw data, "
        "`str` for text, and you convert at the edges of your program:", 14, gap=10)
    pipe(f, [("bytes on disk or network", C.ORANGE), ("str in your program", C.BLUE),
             ("bytes on disk or network", C.ORANGE)], labels=[".decode('utf-8')", ".encode('utf-8')"], size=10.5)
    f.p("UTF-8, the encoding of the web and of nearly every modern file, uses 1 byte for ASCII characters "
        "and up to 4 for everything else:", 13.5, gap=8)
    utf8_picture(f)
    repl(f, """
        >>> s = "café €5"
        >>> len(s), len(s.encode("utf-8"))
        >>> s.encode("utf-8")
        >>> s.encode("utf-8").decode("latin-1")
        >>> b"caf\\xc3".decode("utf-8")
    """, raises_ok=True)
    callout(f, "rule", "Decode as early as possible, work in `str`, encode as late as possible, and {B:always} "
            "pass `encoding=\"utf-8\"` to `open()` for text. The default depends on the operating system "
            "(Windows has historically used cp1252), which is how \"works on my machine\" bugs start.")


def opening(ch):
    f = flow(ch)
    sec(f, "open(), modes and pathlib", room=430)
    table(f, ["mode", "means", "if the file exists", "if it doesn't"], [
        ["`\"r\"`", "read text (default)", "read from the start", "`FileNotFoundError`"],
        ["`\"w\"`", "write text", "{R:emptied first}", "created"],
        ["`\"a\"`", "append text", "write at the end", "created"],
        ["`\"x\"`", "exclusive create", "`FileExistsError`", "created"],
        ["add `b`", "bytes, not str (`\"rb\"`, `\"wb\"`)", "no encoding, no newline translation", ""],
        ["add `+`", "read and write (`\"r+\"`)", "rarely what you want", ""],
    ], widths=[0.8, 1.8, 2, 1.5])
    code(f, """
        from pathlib import Path

        data = Path("data")
        data.mkdir(exist_ok=True)
        notes = data / "notes.txt"                         # / joins paths on any OS

        notes.write_text("line one\\nline two\\n", encoding="utf-8")
        with notes.open("a", encoding="utf-8") as fh:
            fh.write("line three\\n")

        with notes.open(encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):               # one line at a time: any size of file
                print(n, line.rstrip("\\n"))

        print(notes.name, notes.stem, notes.suffix, notes.parent, notes.stat().st_size, "bytes")
        print(sorted(p.name for p in data.glob("*.txt")))
    """)
    table(f, ["pathlib", "instead of"], [
        ["`Path.home() / \"docs\" / \"a.txt\"`", "`os.path.join(os.path.expanduser(\"~\"), ...)`"],
        ["`p.exists()`, `p.is_file()`, `p.is_dir()`", "`os.path.exists(p)` ..."],
        ["`p.read_text()`, `p.write_bytes(b)`", "open / read / close by hand"],
        ["`p.glob(\"**/*.csv\")`, `p.iterdir()`", "`glob.glob`, `os.listdir`"],
        ["`p.with_suffix(\".bak\")`, `p.resolve()`", "string slicing on paths"],
    ], widths=[2.2, 2.4])
    callout(f, "trap", "`for line in fh` keeps the `\\n` on every line. Use `line.rstrip(\"\\n\")` (or "
            "`.strip()` if surrounding spaces don't matter). And `fh.read()` loads the whole file into memory: "
            "fine for kilobytes, not for a 4 GB log.")


def csv_section(ch):
    f = flow(ch)
    sec(f, "CSV: tables as text", room=430)
    f.p("CSV looks trivial until a field contains a comma, a quote or a newline. `line.split(\",\")` breaks on "
        "all three; the `csv` module handles the quoting rules:", 13.5, gap=8)
    code(f, """
        import csv
        from pathlib import Path

        rows = [{"title": "Dune", "author": "Herbert, Frank", "note": 'says "spice"'},
                {"title": "Emma", "author": "Austen, Jane", "note": "two\\nlines"}]

        with open("books.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["title", "author", "note"])
            w.writeheader()
            w.writerows(rows)

        print(Path("books.csv").read_text(encoding="utf-8"))

        with open("books.csv", newline="", encoding="utf-8") as fh:
            back = list(csv.DictReader(fh))
        print(back == rows, back[0]["author"])
    """, notes={8: "newline='' : let csv handle line ends"})
    two_ways(f, ("split by hand (broken)", """
        line = '"Herbert, Frank",Dune'
        print(line.split(","))
    """), ("csv.reader", """
        import csv
        print(next(csv.reader(['"Herbert, Frank",Dune'])))
    """), same_output=False)
    callout(f, "trap", "Everything from CSV comes back as a {B:string}: `\"1965\"`, not `1965`, and an empty "
            "field is `\"\"`, not `None`. Convert and validate each column yourself (or use pandas, which "
            "guesses types for you, sometimes wrongly).")


def json_section(ch):
    f = flow(ch)
    sec(f, "JSON: nested data as text", room=430)
    f.p("JSON stores nested lists and dicts, and it's what web APIs speak (Ch 15). It has fewer types than "
        "Python, so some things change on the round trip:", 13.5, gap=8)
    table(f, ["Python", "JSON", "comes back as"], [
        ["`dict` (str keys)", "object `{...}`", "`dict`"],
        ["`dict` with int keys `{1: \"a\"}`", "`{\"1\": \"a\"}`", "{R:str keys!}"],
        ["`list`, `tuple`", "array `[...]`", "`list` (tuples are lost)"],
        ["`str`, `int`, `float`", "string, number", "same"],
        ["`True`, `False`, `None`", "`true`, `false`, `null`", "same"],
        ["`set`, `datetime`, `Decimal`, your classes", "{R:not allowed}", "`TypeError` unless you convert"],
    ], widths=[2.2, 1.6, 1.6])
    code(f, """
        import json, datetime
        from dataclasses import dataclass, asdict

        @dataclass
        class Loan:
            title: str
            due: datetime.date

        def to_jsonable(obj):                             # called for anything json can't encode
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            raise TypeError(f"can't encode {type(obj).__name__}")

        data = {"member": "ana", "loans": [asdict(Loan("Dune", datetime.date(2026, 10, 3)))], 7: (1, 2)}
        text = json.dumps(data, default=to_jsonable, indent=2)
        print(text)
        print(json.loads(text)["7"])
    """, out_max=16)
    callout(f, "idea", "For logs and big datasets use {B:JSON Lines}: one JSON object per line. You can append "
            "without rewriting the file, and read it line by line: `[json.loads(l) for l in fh]`.")


def other_formats(ch):
    f = flow(ch)
    sec(f, "TOML, pickle, and choosing a format", room=420)
    code(f, """
        import tomllib                    # read-only TOML parser, in the stdlib since 3.11

        config = tomllib.loads('''
        [library]
        name = "Central"
        max_loans = 3
        open_days = ["Mon", "Wed", "Fri"]
        ''')
        print(config["library"]["max_loans"] + 1, config["library"]["open_days"][-1])
    """)
    f.p("`pickle` can save almost any Python object, but loading a pickle can run {B:arbitrary code}: the file "
        "itself says which functions to call while rebuilding objects. This harmless example runs `print`; "
        "a malicious one would run `os.system`:", 13.5, gap=8)
    code(f, """
        import pickle

        class Evil:
            def __reduce__(self):                   # "to rebuild me, call print(...)"
                return (print, ("this ran just by loading the file!",))

        payload = pickle.dumps(Evil())
        pickle.loads(payload)
    """)
    callout(f, "trap", "Never unpickle data from anyone you don't trust: not uploads, not downloads, not "
            "network messages. Use JSON for data exchange. Pickle is for your own caches, read only by your own "
            "program.")
    table(f, ["format", "good for", "watch out"], [
        ["CSV", "flat tables, spreadsheets", "everything is a string; quoting"],
        ["JSON / JSON Lines", "nested data, APIs, logs", "no dates, sets or int keys"],
        ["TOML", "config files written by humans", "stdlib can read but not write it"],
        ["SQLite (Ch 12)", "data you query and update", "a schema to design"],
        ["pickle", "caching your own objects", "{R:runs code when loaded}"],
        ["binary (`struct`)", "fixed file formats, protocols", "byte order, versioning"],
    ], widths=[1.4, 2, 2])


def robust(ch):
    f = flow(ch)
    sec(f, "Writing files safely", room=430)
    f.p("If the program crashes or the power fails half-way through `write_text`, the file is left truncated: "
        "the old data is gone and the new data is incomplete. The fix is to write a {B:temporary file} next to "
        "the target, then swap it in with `os.replace`, which is atomic (it either fully happens or not at all):",
        13.5, gap=8)
    pipe(f, ["write members.json.tmp", "flush + fsync", ("os.replace(tmp, target)", C.GREEN),
             "readers see old OR new, never half"], size=10)
    code(f, """
        import json, os, tempfile
        from pathlib import Path

        def write_atomic(path, text):
            path = Path(path)
            fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(text)
                    fh.flush()
                    os.fsync(fh.fileno())          # make sure the bytes reached the disk
                os.replace(tmp, path)              # atomic swap on the same filesystem
            except BaseException:
                os.unlink(tmp)
                raise

        write_atomic("members.json", json.dumps({"ana": 20}))
        print(Path("members.json").read_text(), [p.name for p in Path(".").glob("*.tmp")])
    """)
    sub(f, "Binary formats: struct", ACCENT)
    f.p("Many file formats start with a fixed binary header. `struct` packs numbers into exact bytes; the format "
        "string gives the byte order and the size of each field:", 13.5, gap=8)
    code(f, """
        import struct

        header = struct.pack("<4sHI", b"LIBR", 2, 1_000_000)   # little-endian: 4 bytes, uint16, uint32
        print(header, len(header))
        magic, version, count = struct.unpack("<4sHI", header)
        print(magic, version, count)
        print(struct.pack(">I", 1).hex(), struct.pack("<I", 1).hex())    # big vs little endian
    """)
    callout(f, "other", "Every language has the same pair: a text layer (encoding, newline handling) over a "
            "byte layer. Java has `Reader`/`InputStream`, C has `fopen(\"r\")`/`fopen(\"rb\")` (the distinction "
            "only matters on Windows), Rust has `String` vs `Vec<u8>` and refuses invalid UTF-8 in a `String`.")


def archives(ch):
    f = flow(ch)
    sec(f, "Compression, archives and copying", room=320)
    code(f, """
        import gzip, shutil, zipfile
        from pathlib import Path

        Path("log.txt").write_text("GET /book/3\\n" * 10_000, encoding="utf-8")
        with open("log.txt", "rb") as src, gzip.open("log.txt.gz", "wb") as dst:
            shutil.copyfileobj(src, dst)                     # streams in chunks: no full read
        print(Path("log.txt").stat().st_size, "->", Path("log.txt.gz").stat().st_size, "bytes")

        with zipfile.ZipFile("backup.zip", "w", zipfile.ZIP_DEFLATED) as z:
            z.write("log.txt")
            z.writestr("readme.txt", "made by Python")
        print(zipfile.ZipFile("backup.zip").namelist())

        shutil.make_archive("snapshot", "gztar", root_dir=".", base_dir="data")
        print(Path("snapshot.tar.gz").exists())
    """)
    table(f, ["module", "for"], [
        ["`shutil`", "copy, move, delete trees (`rmtree`), archives, disk usage"],
        ["`gzip`, `bz2`, `lzma`, `zlib`", "compress one stream; `compression.zstd` is new in 3.14"],
        ["`zipfile`, `tarfile`", "archives of many files (beware `../` paths when extracting untrusted ones)"],
        ["`tempfile`", "temporary files and directories that clean themselves up"],
    ], widths=[1.7, 4])


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 8)
    stamp(f, [
        (9, "Files are bytes; `str` is decoded text. `open(path, mode, encoding=\"utf-8\")` in a `with`; "
            "`pathlib` for paths; `csv`, `json`, `tomllib`, `struct`, `gzip`/`zipfile` for formats. Atomic "
            "writes via temp file + `os.replace`."),
        (11, "Stdlib covers the common formats; never unpickle untrusted data."),
    ])
    callout(f, "deep", "Vault notes: {b:5.12} Bytes and the text boundary · {b:11.2} Binary and text I/O · "
            "{b:11.3} File objects, modes, and offsets · {b:11.5} Paths and filesystem operations · {b:11.6} "
            "Buffers, flushing, and durability · {b:11.7} JSON · {b:11.8} CSV · {b:11.9} Pickle and object "
            "reconstruction · {b:11.15} pathlib · {b:11.16} Temporary resources · {b:11.17} Integrated "
            "serialisation pipeline.")


def build(ch):
    title_page(ch)
    opening(ch)
    csv_section(ch)
    json_section(ch)
    other_formats(ch)
    robust(ch)
    archives(ch)
    finish(ch)
