"""Load exercise specs (practice/specs/chNN.py) and turn them into folders you can work in."""
import importlib
import os
import pkgutil
import re
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")

KINDS = {
    "build": "build from a spec",
    "fix": "fix the bug",
    "fill": "fill the stub",
    "refactor": "refactor, tests stay green",
    "explore": "learn an unseen module",
    "time": "measure and explain",
    "project": "mini-project",
}


def _specs():
    from practice import specs
    mods = []
    for info in pkgutil.iter_modules(specs.__path__):
        if re.fullmatch(r"ch\d+", info.name):
            mods.append(importlib.import_module(f"practice.specs.{info.name}"))
    mods.sort(key=lambda m: int(m.__name__.rsplit("ch", 1)[1]))
    return mods


def _key(ex_id):
    return tuple(int(p) for p in ex_id.split("."))


def all_exercises():
    out = []
    for m in _specs():
        for e in getattr(m, "EXERCISES", []):
            e = dict(e)
            e["kind_label"] = KINDS[e["kind"]]
            e["chapter"] = int(e["id"].split(".")[0])
            out.append(e)
    out.sort(key=lambda e: _key(e["id"]))
    return out


def all_drills():
    out = []
    for m in _specs():
        ch = int(m.__name__.rsplit("ch", 1)[1])
        for i, d in enumerate(getattr(m, "DRILLS", [])):
            d = dict(d)
            d["chapter"] = ch
            d["id"] = f"{ch}.d{i + 1}"
            out.append(d)
    return out


def chapter_exercises(ch):
    return [dict(id=e["id"], kind=KINDS[e["kind"]], title=e["title"]) for e in all_exercises()
            if e["chapter"] == ch]


def missing(item):
    """The pip packages an exercise or drill needs (its 'needs' list) that aren't installed."""
    import importlib.util
    return [n for n in item.get("needs", []) if importlib.util.find_spec(n) is None]


def get(ex_id):
    for e in all_exercises():
        if e["id"] == ex_id:
            return e
    raise SystemExit(f"No exercise {ex_id!r}. Try: python -m practice list")


def slug(e):
    s = re.sub(r"[^a-z0-9]+", "_", e["title"].lower()).strip("_")
    return f"{e['id']}_{s}"[:60]


def folder(e):
    return os.path.join(WORK, f"ch{e['chapter']:02d}", slug(e))


def materialise(e):
    """Create (or refresh) the exercise folder. Never overwrites your solution.py."""
    d = folder(e)
    os.makedirs(d, exist_ok=True)
    needs = ""
    if e.get("needs"):
        needs = f"Needs: {', '.join(e['needs'])} (python3 -m pip install {' '.join(e['needs'])}, inside a venv)\n\n"
    with open(os.path.join(d, "task.md"), "w") as f:
        f.write(f"# {e['id']}  {e['title']}\n\n*{e['kind_label']}*\n\n{needs}{textwrap.dedent(e['task']).strip()}\n\n"
                f"Check with:  python -m practice check {e['id']}\n")
    sol = os.path.join(d, "solution.py")
    if not os.path.exists(sol):
        with open(sol, "w") as f:
            f.write(textwrap.dedent(e.get("stub", "")).strip() + "\n")
    for name, content in (e.get("files") or {}).items():
        p = os.path.join(d, name)
        if not os.path.exists(p):
            with open(p, "w") as f:
                f.write(textwrap.dedent(content).lstrip("\n"))
    return d
