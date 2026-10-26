#!/usr/bin/env python3
"""
=============================================================================
SHEET: json / csv                       TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 03.x structured text / serialisation pitfalls
=============================================================================

WHAT IT IS
  - json: UTF-8-oriented encoder/decoder for JSON text ↔ Python objects
    (dict/list/str/int/float/bool/None by default).
  - csv: reader/writer for delimited tabular text with *correct quoting*
    (RFC 4180-ish dialects). DictReader maps header row → dict rows.
  - Both are stdlib; neither replaces a database or a binary protocol.

INVARIANTS
  - json.dumps → str; json.dump writes a text file object.
    json.loads ← str/bytes(utf-8); json.load reads a text file object.
  - JSON object keys become str; duplicate keys: last wins (decoder).
  - Default encoder rejects non-JSON types (set, bytes, datetime, …)
    unless default= callable or a custom JSONEncoder subclass (cls=).
  - csv quoting shields commas/newlines/quotes inside fields — split(",")
    does NOT.
  - csv dialect: delimiter, quotechar, escapechar, doublequote, etc.
  - DictReader requires a fieldnames source (header row or explicit).

DELEGATES TO (CPython)
  - Modules/_json.c + Lib/json/ — C scanner/encoder fast path
  - Lib/json/encoder.py / decoder.py / __init__.py
  - Lib/csv.py + Modules/_csv.c — reader/writer core
  - Lib/io.py — text stream expectations (newline='' for csv files)

COMPLEXITY CARD
  - json.dumps/loads:     O(n) in document size (plus Python object alloc)
  - csv row parse:        O(row length); whole file O(total bytes)
  - DictReader per row:   O(columns) dict build

WHEN A BEATS B
  - json vs pprint/repr: json for interchange; repr for debug only.
  - csv module vs line.split(","): ALWAYS csv for real CSV (quotes,
    embedded commas, newlines in fields).
  - DictReader vs reader: DictReader when columns have names; reader
    when positional tuples are enough / headers absent.
  - default= hook vs preprocess: default= for leaf non-JSON types;
    preprocess when you reshape the whole tree first.

EDGE CASES
  - float NaN/Inf: allowed by default in Python's json (non-standard);
    allow_nan=False to reject. Strict JSON consumers may break.
  - int vs float: JSON numbers without fraction may become int; large
    integers that overflow other languages are still fine in Python.
  - ensure_ascii=True (default historically) escapes non-ASCII; set
    False for readable Unicode in dumps.
  - csv: excel dialect quirks; sniffing with Sniffer is heuristic only.
  - Always open CSV files with newline='' (docs) so the csv module owns
    newline handling.
  - split(",") breaks on: "a,b",c  → wrong field count / quotes left in.

SOURCE MAP
  - Modules/_json.c                :: scan_once / encoder
  - Lib/json/encoder.py            :: JSONEncoder.default
  - Lib/json/decoder.py            :: JSONDecoder
  - Modules/_csv.c / Lib/csv.py    :: reader, writer, Dialect
=============================================================================
"""

from __future__ import annotations

# --- API walkthrough (dense comments, setts.py style) ---------------------

import csv
import io
import json
from datetime import date
from typing import Any

# --- json load / dump ----------------------------------------------------
# dumps/loads: in-memory str. dump/load: file-like .write/.read text.
# Separators, indent, sort_keys customise encoder output.

# --- default / cls hooks -------------------------------------------------
# def default(o): convert unknown → JSON-able, else raise TypeError
# class Enc(json.JSONEncoder):
#     def default(self, o): ...
# json.dumps(obj, default=fn)  or  json.dumps(obj, cls=Enc)
# object_hook on loads: dict → custom object after each JSON object parse.

# --- csv.reader / DictReader / dialect -----------------------------------
# csv.reader(f) → iterator of list[str]
# csv.DictReader(f) → iterator of dict[str, str|None]
# register dialects: csv.register_dialect("pipe", delimiter="|", ...)
# QUOTE_MINIMAL / ALL / NONNUMERIC / NONE — quoting strategies.

# --- Why split(",") lies -------------------------------------------------
# data = 'a,"b,c",d'
# data.split(",") → ['a', '"b', 'c"', 'd']   # WRONG
# csv.reader → ['a', 'b,c', 'd']             # RIGHT


# --- Runnable probes (quiet on import) ------------------------------------

def _probes() -> None:
    """Run with: python3 this_file.py"""
    # round-trip core types
    payload = {"ok": True, "n": 1, "x": 1.5, "s": "ü", "z": None, "a": [1, 2]}
    text = json.dumps(payload, ensure_ascii=False)
    assert json.loads(text) == payload

    # dump/load via StringIO (no network / no disk required)
    buf = io.StringIO()
    json.dump(payload, buf, ensure_ascii=False)
    buf.seek(0)
    assert json.load(buf) == payload

    # default= hook for date
    def _default(o: Any) -> str:
        if isinstance(o, date):
            return o.isoformat()
        raise TypeError(type(o))

    stamped = {"day": date(2026, 10, 23)}
    assert json.loads(json.dumps(stamped, default=_default)) == {
        "day": "2026-10-23"
    }

    # cls= JSONEncoder subclass
    class DateEncoder(json.JSONEncoder):
        def default(self, o: Any) -> Any:
            if isinstance(o, date):
                return o.isoformat()
            return super().default(o)

    assert "2026-10-23" in json.dumps(stamped, cls=DateEncoder)

    # object_hook
    def hook(d: dict[str, Any]) -> dict[str, Any]:
        if "n" in d:
            d["n"] = int(d["n"]) * 10
        return d

    assert json.loads('{"n": 2}', object_hook=hook)["n"] == 20

    # Non-JSON type without hook fails
    try:
        json.dumps({1, 2, 3})
        raise AssertionError("expected TypeError")
    except TypeError:
        pass

    # --- csv: quoting vs split -------------------------------------------
    raw_csv = 'name,note\nAda,"hello, world"\n'
    # split nightmare on the data line:
    bad = raw_csv.strip().split("\n")[1].split(",")
    assert bad == ["Ada", '"hello', ' world"']  # broken

    f = io.StringIO(raw_csv)
    rows = list(csv.reader(f))
    assert rows == [["name", "note"], ["Ada", "hello, world"]]

    f2 = io.StringIO(raw_csv)
    dicts = list(csv.DictReader(f2))
    assert dicts == [{"name": "Ada", "note": "hello, world"}]

    # dialect: pipe-separated
    pipe = io.StringIO("a|b|c\n1|2|3\n")
    r = csv.reader(pipe, delimiter="|")
    assert list(r)[1] == ["1", "2", "3"]

    # writer quoting
    out = io.StringIO()
    w = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    w.writerow(["a", "b,c", 'say "hi"'])
    assert out.getvalue().strip() == 'a,"b,c","say ""hi"""'

    # newline='' recommendation: simulate with StringIO (already clean)
    sample = io.StringIO("x,y\n1,2\n")
    assert list(csv.DictReader(sample)) == [{"x": "1", "y": "2"}]

    print("json_csv_sheet.py: all probes passed")


if __name__ == "__main__":
    _probes()
