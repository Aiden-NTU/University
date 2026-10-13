EXERCISES = [
    dict(
        id="8.1", kind="build", title="CSV that survives awkward names",
        task="""
        Write two functions using the `csv` module:

        - `write_scores(path, scores)`: `scores` is a dict name → int. Write a CSV with header
          `name,score`, rows sorted by score (highest first), ties by name.
        - `read_scores(path)`: the reverse, returning a dict name → **int**, skipping completely blank lines.

        Names can contain commas, quotes, accents and emoji. Use UTF-8.
        """,
        stub='''
        def write_scores(path, scores):
            with open(path, "w") as fh:
                fh.write("name,score\\n")
                for name, score in scores.items():
                    fh.write(f"{name},{score}\\n")

        def read_scores(path):
            out = {}
            for line in open(path).read().splitlines()[1:]:
                name, score = line.split(",")
                out[name] = int(score)
            return out
        ''',
        tests='''
        import random

        WEIRD = ["O'Brien, Pat", 'Ana "the reader"', "Zoë", "李", "🙂 smile", "plain"]

        def test_round_trip(m):
            with tmpdir():
                rng = random.Random(1)
                for _ in range(20):
                    scores = {n: rng.randint(0, 100) for n in rng.sample(WEIRD + rand_words(10, rng.randint(0, 99)), 8)}
                    m.write_scores("s.csv", scores)
                    equal(m.read_scores("s.csv"), scores, "round trip")

        def test_order_and_blank_lines(m):
            with tmpdir():
                m.write_scores("s.csv", {"b": 5, "a": 5, "c": 9})
                text = open("s.csv", encoding="utf-8").read().splitlines()
                equal([t.split(",")[0] for t in text], ["name", "c", "a", "b"], "header, then score desc, name asc")
                with open("s.csv", "a", encoding="utf-8") as fh:
                    fh.write("\\n\\n")
                equal(m.read_scores("s.csv"), {"a": 5, "b": 5, "c": 9}, "blank lines skipped")
        ''',
        alts={
            "DictWriter / DictReader": ('''
                import csv

                def write_scores(path, scores):
                    rows = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
                    with open(path, "w", newline="", encoding="utf-8") as fh:
                        w = csv.writer(fh)
                        w.writerow(["name", "score"])
                        w.writerows(rows)

                def read_scores(path):
                    with open(path, newline="", encoding="utf-8") as fh:
                        return {row["name"]: int(row["score"]) for row in csv.DictReader(fh)}
            ''', "DictReader skips blank lines itself. newline='' matters on Windows (otherwise you get blank "
                 "rows between records) and for fields containing newlines."),
        },
    ),
    dict(
        id="8.2", kind="fix", title="Counting characters, not bytes",
        task="""
        `text_stats(path)` should return `(lines, characters, words)` for a UTF-8 text file, where
        `characters` counts Unicode characters (not bytes) excluding newline characters, and `lines`
        is the number of lines. It gives wrong answers for anything non-English. Fix it.
        """,
        stub='''
        def text_stats(path):
            data = open(path, "rb").read()
            lines = data.count(b"\\n")
            chars = len(data) - lines
            words = len(data.split())
            return lines, chars, words
        ''',
        tests='''
        def write(name, text):
            with open(name, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)

        def test_unicode(m):
            with tmpdir():
                write("a.txt", "café au lait\\n€5 🙂\\n")
                equal(m.text_stats("a.txt"), (2, 16, 5), "two lines, 16 characters, 5 words")

        def test_no_final_newline(m):
            with tmpdir():
                write("b.txt", "one\\ntwo")
                equal(m.text_stats("b.txt"), (2, 6, 2), "last line without a newline still counts")
                write("c.txt", "")
                equal(m.text_stats("c.txt"), (0, 0, 0), "empty file")
        ''',
        alts={
            "decode, then count": ('''
                def text_stats(path):
                    with open(path, encoding="utf-8") as fh:
                        text = fh.read()
                    lines = text.splitlines()
                    return len(lines), sum(len(l) for l in lines), len(text.split())
            ''', "splitlines() handles a missing final newline (and \\r\\n). Counting b'\\n' doesn't."),
            "streaming": ('''
                def text_stats(path):
                    lines = chars = words = 0
                    with open(path, encoding="utf-8") as fh:
                        for line in fh:
                            line = line.rstrip("\\r\\n")
                            lines += 1
                            chars += len(line)
                            words += len(line.split())
                    return lines, chars, words
            ''', "Same answers in constant memory: fine for a 10 GB file."),
        },
    ),
    dict(
        id="8.3", kind="build", title="JSON that keeps its types",
        task="""
        Write `dumps(obj)` and `loads(text)` built on the `json` module that round-trip values
        containing `datetime.date`, `set`, `tuple` and `decimal.Decimal` (inside dicts and lists):
        `loads(dumps(x)) == x` and the types come back exactly.

        Idea: encode each special value as a tagged object such as `{"__type__": "date", "value": "2026-10-03"}`,
        using `default=` to encode and `object_hook=` to decode. (Tuples need extra care: `json` turns
        them into lists *before* calling `default`.)
        """,
        stub='''
        import json

        def dumps(obj):
            return json.dumps(obj)

        def loads(text):
            return json.loads(text)
        ''',
        tests='''
        import datetime
        from decimal import Decimal

        def same(a, b):
            if type(a) is not type(b):
                return False
            if isinstance(a, dict):
                return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
            if isinstance(a, (list, tuple)):
                return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
            return a == b

        def test_round_trip(m):
            x = {"due": datetime.date(2026, 10, 3), "tags": {"sf", "classic"}, "pos": (1, 2),
                 "fine": Decimal("1.10"), "nested": [{"when": datetime.date(2000, 1, 1)}, (3, (4, 5))], "n": None}
            back = m.loads(m.dumps(x))
            check(same(back, x), f"types lost: got {back!r}")

        def test_plain_json_unchanged(m):
            import json
            plain = {"a": [1, 2.5, "s", True, None], "b": {"c": []}}
            equal(json.loads(m.dumps(plain)), plain, "ordinary data is still ordinary JSON")
        ''',
        alts={
            "pre-walk + object_hook": ('''
                import datetime, json
                from decimal import Decimal

                def _tag(o):
                    if isinstance(o, dict):
                        return {k: _tag(v) for k, v in o.items()}
                    if isinstance(o, list):
                        return [_tag(v) for v in o]
                    if isinstance(o, tuple):
                        return {"__type__": "tuple", "value": [_tag(v) for v in o]}
                    if isinstance(o, set):
                        return {"__type__": "set", "value": [_tag(v) for v in sorted(o, key=repr)]}
                    if isinstance(o, datetime.date):
                        return {"__type__": "date", "value": o.isoformat()}
                    if isinstance(o, Decimal):
                        return {"__type__": "decimal", "value": str(o)}
                    return o

                def _untag(d):
                    kind = d.get("__type__")
                    if kind == "tuple":
                        return tuple(d["value"])
                    if kind == "set":
                        return set(d["value"])
                    if kind == "date":
                        return datetime.date.fromisoformat(d["value"])
                    if kind == "decimal":
                        return Decimal(d["value"])
                    return d

                def dumps(obj):
                    return json.dumps(_tag(obj))

                def loads(text):
                    return json.loads(text, object_hook=_untag)
            ''', "Walking the data first sidesteps the tuple problem. object_hook is called bottom-up, so "
                 "inner tagged values are already decoded when the outer one is built."),
        },
    ),
    dict(
        id="8.4", kind="build", title="Saving without ever corrupting the file",
        task="""
        Write `save_json(path, data)` that writes `data` as JSON to `path` **atomically**: if anything
        goes wrong (for example `data` can't be serialised), the old file must be left exactly as it
        was and no temporary files may be left behind. On success, `path` contains the new JSON.
        """,
        stub='''
        import json

        def save_json(path, data):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh)
        ''',
        tests='''
        import json, os

        def test_success(m):
            with tmpdir():
                m.save_json("d.json", {"a": 1})
                m.save_json("d.json", {"a": 2})
                equal(json.load(open("d.json")), {"a": 2}, "new content")
                equal(sorted(os.listdir(".")), ["d.json"], "no leftover files")

        def test_failure_keeps_old(m):
            with tmpdir():
                m.save_json("d.json", {"a": 1})
                try:
                    m.save_json("d.json", {"a": {1, 2}})
                except TypeError:
                    pass
                else:
                    raise AssertionError("a set isn't JSON: TypeError expected")
                equal(json.load(open("d.json")), {"a": 1}, "old file intact")
                equal(sorted(os.listdir(".")), ["d.json"], "temp file cleaned up")
        ''',
        alts={
            "mkstemp + os.replace": ('''
                import json, os, tempfile
                from pathlib import Path

                def save_json(path, data):
                    path = Path(path)
                    fd, tmp = tempfile.mkstemp(dir=path.parent or ".", suffix=".tmp")
                    try:
                        with os.fdopen(fd, "w", encoding="utf-8") as fh:
                            json.dump(data, fh)
                            fh.flush()
                            os.fsync(fh.fileno())
                        os.replace(tmp, path)
                    except BaseException:
                        os.unlink(tmp)
                        raise
            ''', "The temp file must be in the same directory: os.replace is only atomic within one filesystem."),
            "serialise first": ('''
                import json, os
                from pathlib import Path

                def save_json(path, data):
                    text = json.dumps(data)
                    tmp = Path(str(path) + ".tmp")
                    tmp.write_text(text, encoding="utf-8")
                    os.replace(tmp, path)
            ''', "Building the string before touching the disk avoids the serialisation failure case "
                 "entirely; a crash during write_text can still leave a stray .tmp, and there's no fsync."),
        },
    ),
    dict(
        id="8.5", kind="build", title="A binary file format with struct",
        task="""
        Write `pack(records)` → `bytes` and `unpack(blob)` → list for records `(id, year, title)`.
        The format (all little-endian):

        - header: the 4 bytes `b"LIB1"`, then the record count as an unsigned 32-bit int
        - each record: id as unsigned 32-bit, year as unsigned 16-bit, then the title's UTF-8 length
          as one unsigned byte, then the title bytes (titles are at most 255 bytes in UTF-8)

        `unpack` raises `ValueError` if the magic bytes are wrong or the data is truncated.
        """,
        stub='''
        import struct

        def pack(records):
            ...

        def unpack(blob):
            ...
        ''',
        tests='''
        import random, struct

        def test_exact_bytes(m):
            blob = m.pack([(1, 1965, "Dune")])
            equal(blob, b"LIB1" + struct.pack("<I", 1) + struct.pack("<IHB", 1, 1965, 4) + b"Dune", "exact layout")

        def test_round_trip_random(m):
            rng = random.Random(3)
            for _ in range(100):
                recs = [(rng.randint(0, 2**32 - 1), rng.randint(0, 65535), "".join(rng.choice("abcé🙂 ") for _ in range(rng.randint(0, 30))))
                        for _ in range(rng.randint(0, 10))]
                equal(m.unpack(m.pack(recs)), recs, "round trip")

        def test_bad_input(m):
            good = m.pack([(1, 2000, "x")])
            raises(ValueError, m.unpack, b"XXXX" + good[4:])
            raises(ValueError, m.unpack, good[:-1])
            raises(ValueError, m.unpack, good[:6])
        ''',
        alts={
            "struct with an offset": ('''
                import struct

                HEAD = struct.Struct("<4sI")
                REC = struct.Struct("<IHB")

                def pack(records):
                    out = [HEAD.pack(b"LIB1", len(records))]
                    for rid, year, title in records:
                        t = title.encode("utf-8")
                        out.append(REC.pack(rid, year, len(t)) + t)
                    return b"".join(out)

                def unpack(blob):
                    try:
                        magic, count = HEAD.unpack_from(blob, 0)
                        if magic != b"LIB1":
                            raise ValueError("not a LIB1 file")
                        pos, out = HEAD.size, []
                        for _ in range(count):
                            rid, year, n = REC.unpack_from(blob, pos)
                            pos += REC.size
                            if pos + n > len(blob):
                                raise ValueError("truncated title")
                            out.append((rid, year, blob[pos:pos + n].decode("utf-8")))
                            pos += n
                        return out
                    except struct.error as e:
                        raise ValueError(f"truncated data: {e}") from e
            ''', "Precompiled Struct objects and unpack_from(offset) avoid slicing copies. Translating "
                 "struct.error into ValueError keeps the low-level detail as __cause__."),
            "io.BytesIO stream": ('''
                import io, struct

                def pack(records):
                    buf = io.BytesIO()
                    buf.write(b"LIB1" + struct.pack("<I", len(records)))
                    for rid, year, title in records:
                        t = title.encode("utf-8")
                        buf.write(struct.pack("<IHB", rid, year, len(t)))
                        buf.write(t)
                    return buf.getvalue()

                def _read(f, n):
                    data = f.read(n)
                    if len(data) != n:
                        raise ValueError("truncated data")
                    return data

                def unpack(blob):
                    f = io.BytesIO(blob)
                    if _read(f, 4) != b"LIB1":
                        raise ValueError("not a LIB1 file")
                    (count,) = struct.unpack("<I", _read(f, 4))
                    out = []
                    for _ in range(count):
                        rid, year, n = struct.unpack("<IHB", _read(f, 7))
                        out.append((rid, year, _read(f, n).decode("utf-8")))
                    return out
            ''', "Reading from a file-like object means the same code works on a real open(path, 'rb')."),
        },
    ),
    dict(
        id="8.6", kind="project", title="Mini-project: summarise a folder of logs",
        task="""
        A folder holds request logs as **JSON Lines** files: `*.log` (plain text) and `*.log.gz`
        (gzip-compressed). Each line should be an object like
        `{"path": "/book/3", "status": 200, "ms": 12}`.

        Write `summarise(folder)` returning a dict:

        - `"requests"`: number of valid lines
        - `"errors"`: valid lines with `status >= 500`
        - `"top_paths"`: the 3 most requested paths as `[(path, count), ...]`, most first, ties by path
        - `"slowest"`: the largest `ms`, or `None` if there are no requests
        - `"bad_lines"`: lines that aren't valid JSON objects with those three keys (blank lines are ignored)

        Read files line by line (they can be big) and ignore files with other extensions.
        """,
        stub='''
        def summarise(folder):
            return {"requests": 0, "errors": 0, "top_paths": [], "slowest": None, "bad_lines": 0}
        ''',
        tests='''
        import gzip, json, os

        def line(p, s, ms):
            return json.dumps({"path": p, "status": s, "ms": ms}) + "\\n"

        def test_summary(m):
            with tmpdir():
                os.mkdir("logs")
                with open("logs/a.log", "w", encoding="utf-8") as fh:
                    fh.write(line("/book/1", 200, 5) + line("/book/2", 500, 40) + "not json\\n" + "\\n" + line("/book/1", 200, 7))
                with gzip.open("logs/b.log.gz", "wt", encoding="utf-8") as fh:
                    fh.write(line("/book/3", 503, 90) + line("/book/1", 404, 3) + '{"path": "/x"}\\n' + line("/book/2", 200, 1))
                with open("logs/notes.txt", "w") as fh:
                    fh.write(line("/ignored", 500, 999))
                got = m.summarise("logs")
                equal(got["requests"], 6, "requests")
                equal(got["errors"], 2, "errors")
                equal(got["top_paths"], [("/book/1", 3), ("/book/2", 2), ("/book/3", 1)], "top paths")
                equal(got["slowest"], 90, "slowest")
                equal(got["bad_lines"], 2, "bad lines")

        def test_empty(m):
            with tmpdir():
                os.mkdir("logs")
                equal(m.summarise("logs"), {"requests": 0, "errors": 0, "top_paths": [], "slowest": None, "bad_lines": 0}, "empty folder")
        ''',
        alts={
            "generators + Counter": ('''
                import gzip, json
                from collections import Counter
                from pathlib import Path

                def _lines(folder):
                    for p in sorted(Path(folder).iterdir()):
                        if p.name.endswith(".log.gz"):
                            opener = gzip.open
                        elif p.suffix == ".log":
                            opener = open
                        else:
                            continue
                        with opener(p, "rt", encoding="utf-8") as fh:
                            yield from fh

                def _records(folder, bad):
                    for raw in _lines(folder):
                        if not raw.strip():
                            continue
                        try:
                            rec = json.loads(raw)
                            yield rec["path"], int(rec["status"]), rec["ms"]
                        except (ValueError, KeyError, TypeError):
                            bad.append(raw)

                def summarise(folder):
                    bad, paths = [], Counter()
                    errors, slowest = 0, None
                    for path, status, ms in _records(folder, bad):
                        paths[path] += 1
                        errors += status >= 500
                        slowest = ms if slowest is None else max(slowest, ms)
                    top = sorted(paths.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
                    return {"requests": sum(paths.values()), "errors": errors, "top_paths": top,
                            "slowest": slowest, "bad_lines": len(bad)}
            ''', "A pipeline of generators: files → lines → records → totals, one line in memory at a time. "
                 "Counter.most_common(3) would break ties by first-seen order, so sort explicitly."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="print(len('é'), len('é'.encode('utf-8')), len('🙂'.encode('utf-8')))"),
    dict(kind="predict", code="import json\nprint(json.loads(json.dumps({1: (2, 3)})))"),
    dict(kind="predict", code="from pathlib import Path\np = Path('/data/reports/q3.tar.gz')\nprint(p.name, p.suffix, p.stem)"),
    dict(kind="predict", code="import csv, io\nprint(next(csv.reader(io.StringIO('a,\"b,c\",d'))))"),
    dict(kind="predict", code="print(b'abc'[0], list(b'hi'), bytes([72, 105]))"),
    dict(kind="recall", q="Which open() mode creates a file but fails if it already exists?", a=["x", "'x'", "\"x\""]),
    dict(kind="recall", q="Which os function atomically replaces one file with another?", a=["os.replace", "replace"]),
    dict(kind="recall", q="Which stdlib format module can run arbitrary code when loading untrusted data?", a=["pickle"]),
]
