"""Command line for the practice repo. See practice/__init__.py for the commands."""
import argparse
import contextlib
import io
import os
import random
import sys
import textwrap
import traceback

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from practice import catalog, progress, runner  # noqa: E402

GREEN, RED, GREY, BOLD, END = "\033[32m", "\033[31m", "\033[90m", "\033[1m", "\033[0m"


def cmd_list(args):
    conn = progress.connect()
    done = progress.passed_ids(conn)
    ch = None
    for e in catalog.all_exercises():
        if args.chapter and e["chapter"] != args.chapter:
            continue
        if e["chapter"] != ch:
            ch = e["chapter"]
            print(f"\n{BOLD}Chapter {ch}{END}")
        mark = f"{GREEN}done{END}" if e["id"] in done else "    "
        print(f"  {mark}  {e['id']:<6} {GREY}{e['kind_label']:<26}{END} {e['title']}")


def cmd_next(args):
    conn = progress.connect()
    done = progress.passed_ids(conn)
    for e in catalog.all_exercises():
        if e["id"] not in done:
            args.id = e["id"]
            return cmd_start(args)
    print("Every exercise passed. Time for your own project!")


def cmd_start(args):
    e = catalog.get(args.id)
    d = catalog.materialise(e)
    print(open(os.path.join(d, "task.md")).read())
    print(f"{GREY}Your file: {os.path.join(d, 'solution.py')}{END}")


def cmd_check(args):
    e = catalog.get(args.id)
    d = catalog.materialise(e)
    path = os.path.join(d, "solution.py")
    print(f"{BOLD}{e['id']}  {e['title']}{END}  {GREY}({path}){END}\n")
    if catalog.missing(e):
        pkgs = " ".join(catalog.missing(e))
        print(f"{RED}This exercise needs {pkgs}.{END} Install it in a virtual environment (Ch 19):\n"
              f"    python3 -m venv .venv && source .venv/bin/activate && python3 -m pip install {pkgs}")
        return 1
    try:
        mod = runner.load_module(path)
    except Exception:  # noqa: BLE001
        print(f"{RED}Your solution.py doesn't run yet:{END}")
        print(textwrap.indent("".join(traceback.format_exc(limit=-1)), "    "))
        progress.record(progress.connect(), e["id"], False)
        return 1
    ok, _ = runner.run(e, mod)
    conn = progress.connect()
    progress.record(conn, e["id"], ok)
    if ok and e.get("alts"):
        print(f"{GREY}  See other valid solutions: python -m practice alt {e['id']}{END}")
    return 0 if ok else 1


def cmd_alt(args):
    e = catalog.get(args.id)
    conn = progress.connect()
    if e["id"] not in progress.passed_ids(conn) and not args.force:
        print("Pass the exercise first (or add --force). Seeing an answer too early skips the learning.")
        return 1
    for name, (src, note) in e.get("alts", {}).items():
        print(f"{BOLD}--- {name}{END}")
        print(textwrap.dedent(src).strip())
        print(f"{GREY}{textwrap.fill(note, 90)}{END}\n")


def _predict_answer(d):
    buf = io.StringIO()
    ns = {"__name__": "__main__"}
    try:
        with contextlib.redirect_stdout(buf):
            exec(textwrap.dedent(d["code"]), ns)
    except Exception as e:  # noqa: BLE001
        return buf.getvalue() + type(e).__name__
    return buf.getvalue()


def _norm(s):
    return [" ".join(line.split()) for line in s.strip().splitlines() if line.strip()]


def cmd_drill(args):
    conn = progress.connect()
    done_chapters = {int(i.split(".")[0]) for i in progress.passed_ids(conn)}
    drills = [d for d in catalog.all_drills()
              if (args.all or d["chapter"] in done_chapters or not done_chapters) and not catalog.missing(d)]
    due = progress.due_cards(conn, [d["id"] for d in drills])
    by_id = {d["id"]: d for d in drills}
    random.shuffle(due)
    due = due[:args.n]
    if not due:
        print("Nothing due today. Come back tomorrow (that's the point of spacing).")
        return
    score = 0
    for k, (did, box) in enumerate(due, 1):
        d = by_id[did]
        print(f"\n{BOLD}[{k}/{len(due)}]{END} {GREY}chapter {d['chapter']}, box {box}{END}")
        if d["kind"] == "predict":
            print("What does this print? (type the output; blank line to finish; an error -> its name)")
            print(textwrap.indent(textwrap.dedent(d["code"]).strip(), "    "))
            lines = []
            while True:
                try:
                    ln = input("  > ")
                except EOFError:
                    break
                if not ln:
                    break
                lines.append(ln)
            want = _predict_answer(d)
            ok = _norm("\n".join(lines)) == _norm(want)
        else:
            print(d["q"])
            try:
                got = input("  > ")
            except EOFError:
                got = ""
            answers = d["a"] if isinstance(d["a"], list) else [d["a"]]
            ok = " ".join(got.lower().split()) in [" ".join(a.lower().split()) for a in answers]
            want = answers[0]
        new = progress.answer(conn, did, ok)
        score += ok
        if ok:
            print(f"{GREEN}  right{END} -> box {new}")
        else:
            print(f"{RED}  not quite{END} -> back to box 1. Answer:")
            print(textwrap.indent(want.strip(), "    "))
        if d.get("why"):
            print(f"{GREY}  {d['why']}{END}")
    print(f"\n{score}/{len(due)} today.")


def cmd_verify(args):
    """Every reference solution must pass, and the starting stub must not (except explore/time)."""
    bad = skipped = 0
    for e in catalog.all_exercises():
        if args.chapter and e["chapter"] != args.chapter:
            continue
        if catalog.missing(e):
            skipped += 1
            print(f"{GREY}{e['id']}: skipped, needs {' '.join(catalog.missing(e))}{END}")
            continue
        alts = e.get("alts", {})
        if not alts:
            print(f"{RED}{e['id']}: no reference solutions{END}")
            bad += 1
        for name, (src, _) in alts.items():
            try:
                ok, rep = runner.run(e, runner.load_source(src), quiet=True)
            except Exception as ex:  # noqa: BLE001
                ok, rep = False, None
                print(f"{RED}{e['id']} [{name}] crashed: {ex!r}{END}")
            if not ok:
                bad += 1
                msgs = [m for s, _, m in (rep.lines if rep else []) if s != "ok"]
                print(f"{RED}{e['id']} [{name}] fails: {msgs[:2]}{END}")
        if e.get("stub_should_fail", True):
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    ok, _ = runner.run(e, runner.load_source(e.get("stub", "")), quiet=True)
            except Exception:  # noqa: BLE001
                ok = False
            if ok:
                bad += 1
                print(f"{RED}{e['id']}: the starting stub already passes{END}")
    n = len([e for e in catalog.all_exercises() if not args.chapter or e["chapter"] == args.chapter])
    drills = catalog.all_drills()
    for d in drills:
        if d["kind"] == "predict" and not catalog.missing(d):
            _predict_answer(d)
    note = f" ({skipped} skipped: missing packages)" if skipped else ""
    print(f"verified {n - skipped} exercises{note} and {len(drills)} drills: "
          f"{'all good' if not bad else f'{bad} problems'}")
    return 1 if bad else 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m practice", description="Practice for the Python Visual Guide")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("chapter", nargs="?", type=int)
    s.set_defaults(fn=cmd_list)
    sub.add_parser("next").set_defaults(fn=cmd_next)
    for name, fn in (("start", cmd_start), ("check", cmd_check)):
        s = sub.add_parser(name)
        s.add_argument("id")
        s.set_defaults(fn=fn)
    s = sub.add_parser("alt")
    s.add_argument("id")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_alt)
    s = sub.add_parser("drill")
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--all", action="store_true", help="include chapters you haven't reached")
    s.set_defaults(fn=cmd_drill)
    s = sub.add_parser("verify")
    s.add_argument("chapter", nargs="?", type=int)
    s.set_defaults(fn=cmd_verify)
    args = p.parse_args(argv)
    return args.fn(args) or 0


if __name__ == "__main__":
    sys.exit(main())
