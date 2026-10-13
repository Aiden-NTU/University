"""Chapter 14 - The OS and the command line: the process model (argv, env, streams, exit codes, signals),
sys and os, argparse, subprocess (and shell injection), signal handling, logging for CLIs."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, callout, code, flow, practice, section, seq, shell, stamp, sub, table,
                         title_block, two_ways)

ORDER = 14
NUM = 14
TITLE = "The OS and the command line"
SHORT = "OS and command line"
SLUG = "OS-and-CLI"
ACCENT = C.PURPLE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


# ----------------------------------------------------------------------------- pictures
def process_picture(f):
    """A program as the OS sees it: inputs on the left, outputs on the right."""
    y = f.reserve(214)
    pg = f.pg
    bx, by, bw, bh = L + 178, y + 40, 140, 126
    pg.rect(bx, by, bw, bh, ACCENT, 1.6, fillcolor=C.LIGHT[ACCENT], r=10)
    pg.text(bx + bw / 2, by + 40, "your process", 12, ACCENT, F.BOLD, align="center")
    pg.text(bx + bw / 2, by + 58, "python3 loans.py", 9, C.INK, F.MONO, align="center")
    pg.text(bx + bw / 2, by + 76, "has a pid and a cwd", 9, C.GREY, align="center")
    left = [("argv", "the words typed after the command"), ("environment", "NAME=value pairs, inherited"),
            ("stdin  (fd 0)", "piped or typed input")]
    right = [("stdout  (fd 1)", "results: the data"), ("stderr  (fd 2)", "logs, warnings, errors"),
             ("exit code", "0 = ok, anything else = failed")]
    for i, (name, what) in enumerate(left):
        ry = by + 18 + i * 40
        pg.text(bx - 22, ry - 8, name, 10.5, C.BLUE, F.BOLD, align="right")
        pg.text(bx - 22, ry + 6, what, 8.5, C.GREY, align="right")
        pg.arrow(bx - 18, ry + 2, bx - 2, ry + 2, C.BLUE, 1.3, head=5)
    for i, (name, what) in enumerate(right):
        ry = by + 18 + i * 40
        col = C.RED if "stderr" in name else C.GREEN
        pg.arrow(bx + bw + 2, ry + 2, bx + bw + 18, ry + 2, col, 1.3, head=5)
        pg.text(bx + bw + 22, ry - 8, name, 10.5, col, F.BOLD)
        pg.text(bx + bw + 22, ry + 6, what, 8.5, C.GREY)
    pg.text(bx + bw / 2, y + 2, "signals: Ctrl+C, kill, shutdown", 10, C.ORANGE, F.BOLD, align="center")
    pg.arrow(bx + bw / 2, y + 18, bx + bw / 2, by - 2, C.ORANGE, 1.3, head=5)
    pg.arrow(bx + bw / 2, by + bh + 2, bx + bw / 2, by + bh + 22, C.BROWN, 1.3, head=5, both=True)
    pg.text(bx + bw / 2, by + bh + 26, "files, sockets, other processes", 10, C.BROWN, F.BOLD, align="center")


def argv_picture(f):
    """How argparse turns argv tokens into Namespace fields."""
    toks = ["loans", "-v", "add", "Dune", "--days", "21"]
    fields = ["verbose=1", "cmd='add'", "title='Dune'", "days=21"]
    owner = {1: 0, 2: 1, 3: 2, 4: 3, 5: 3}
    y = f.reserve(118)
    pg = f.pg
    size = 10.5
    tw = [F.width(t, F.MONO, size) + 16 for t in toks]
    total = sum(tw) + 8 * (len(toks) - 1)
    x = L + (W - total) / 2
    tx = []
    for t, w_ in zip(toks, tw):
        col = C.GREY if t == "loans" else C.BLUE
        pg.rect(x, y + 14, w_, 24, col, 1.1, fillcolor=C.LIGHT[col], r=4)
        pg.text(x + w_ / 2, y + 19, t, size, C.INK, F.MONO, align="center")
        tx.append(x + w_ / 2)
        x += w_ + 8
    pg.text(L, y, "sys.argv[1:]  (argv[0] is the program name)", 9, C.GREY, F.BOLD)
    fw = [F.width(s, F.MONO, size) + 16 for s in fields]
    ftotal = sum(fw) + 16 * (len(fields) - 1)
    x = L + (W - ftotal) / 2
    fx = []
    for s, w_ in zip(fields, fw):
        pg.rect(x, y + 84, w_, 24, C.GREEN, 1.1, fillcolor=C.LIGHT[C.GREEN], r=4)
        pg.text(x + w_ / 2, y + 89, s, size, C.INK, F.MONO, align="center")
        fx.append(x + w_ / 2)
        x += w_ + 16
    for ti, fi in owner.items():
        pg.arrow(tx[ti], y + 40, fx[fi], y + 82, C.GREY, 1.0, head=4)
    pg.note(R, y + 50, "'21' → int(21)\nbecause type=int", C.PURPLE, 13, align="right")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 14, TITLE, "every program talks to the OS the same way", ACCENT)
    f = ch.flow(top=190)
    f.p("To the operating system, every program in every language is a {B:process} with the same few "
        "connections. Learn them once and you can drive any program from Python, and write Python tools "
        "that behave like real Unix commands:", 14, gap=10)
    process_picture(f)
    f.p("A shell pipeline like `grep ERROR app.log | sort | uniq -c > counts.txt` works only because every "
        "program in it follows these conventions: read stdin, write results to stdout, complain on stderr, "
        "report success with the exit code. This chapter makes your Python programs good citizens of "
        "that world.", 13.5, gap=8)


def sys_os_section(ch):
    f = flow(ch)
    sec(f, "sys and os: the process from the inside", room=420)
    f.p("`sys` is about the {B:interpreter} (its arguments, streams, version, exit); `os` is about the "
        "{B:operating system} (environment, files, process ids). Running a child Python is the easiest way "
        "to see argv and exit codes for real:", 13.5, gap=8)
    code(f, """
        import subprocess, sys

        child = "import sys; print(sys.argv[1:]); sys.exit(3)"
        r = subprocess.run([sys.executable, "-c", child, "a b", "c"], capture_output=True, text=True)
        print(r.returncode, r.stdout.strip())

        r = subprocess.run([sys.executable, "-c", "raise SystemExit('bad input')"],
                           capture_output=True, text=True)
        print(r.returncode, repr(r.stdout), r.stderr.strip())
    """, notes={4: "\"a b\" stays one argument", 7: "SystemExit(str): message to stderr, exit code 1"})
    table(f, ["exit code", "means", "who uses it"], [
        ["`0`", "success", "everything: `&&` in the shell, CI, cron, systemd"],
        ["`1`", "general failure", "`sys.exit(\"message\")`, an uncaught exception"],
        ["`2`", "you used it wrong (bad arguments)", "argparse, grep, most Unix tools"],
        ["`126` / `127`", "found but not executable / not found", "the shell"],
        ["`128 + n`", "killed by signal n (`130` = Ctrl+C, `137` = SIGKILL)", "the shell"],
    ], widths=[1.1, 3.0, 2.8], size=10.5)
    code(f, """
        import os, subprocess, sys
        from pathlib import Path

        print(sys.platform, sys.version_info[:2], os.path.basename(sys.executable))
        print(os.getcwd() == str(Path.cwd()), os.getpid() > 1, os.cpu_count() >= 1)
        print(os.sep, repr(os.pathsep), sys.stdout.isatty())
        print(os.getenv("LOANS_DB", "loans.db"))           # environment variable, with a default

        env = {**os.environ, "LOANS_DB": "test.db"}        # the child gets its own copy
        r = subprocess.run([sys.executable, "-c", "import os; print(os.environ['LOANS_DB'])"],
                           env=env, capture_output=True, text=True)
        print(r.stdout.strip(), "LOANS_DB" in os.environ)
    """, notes={6: "False: output is being captured", 12: "changes never flow back to the parent"})
    callout(f, "trap", "Environment variables are inherited by {B:every} child process, appear in crash reports, "
            "and can be read from `/proc` by the same user. They're the standard place for configuration and "
            "tolerable for secrets in containers, but never log `os.environ`, and don't pass secrets as "
            "command-line arguments: `ps` shows argv to every user on the machine.")


def argparse_section(ch):
    f = flow(ch)
    sec(f, "argparse: a real command-line interface", room=440)
    f.p("`argparse` turns the list of words in `sys.argv` into a tidy object, converts types, checks choices, "
        "and writes `--help` and error messages for you:", 13.5, gap=8)
    argv_picture(f)
    code(f, """
        import argparse

        def make_parser():
            p = argparse.ArgumentParser(prog="loans", description="Track library loans.")
            p.add_argument("-v", "--verbose", action="count", default=0, help="-vv for more")
            sub = p.add_subparsers(dest="cmd", required=True)
            add = sub.add_parser("add", help="lend a book")
            add.add_argument("title")
            add.add_argument("--days", type=int, default=14, help="default: %(default)s")
            ls = sub.add_parser("list", help="show loans")
            ls.add_argument("--overdue", action="store_true")
            ls.add_argument("--sort", choices=["title", "due"], default="due")
            return p

        print(make_parser().parse_args(["-v", "add", "Dune", "--days", "21"]))
        print(make_parser().parse_args(["list", "--overdue"]))
    """, notes={5: "-v, -vv, -vvv", 6: "subcommands, like git commit", 8: "positional: required",
                9: "option: has a default", 11: "a flag: True if present"})
    code(f, """
        print(make_parser().format_help())
    """, out_max=20)
    sub(f, "main(argv=None): the pattern that makes a CLI testable", ACCENT, room=220)
    code(f, """
        def main(argv=None):
            args = make_parser().parse_args(argv)        # None means: use sys.argv[1:]
            if args.cmd == "add":
                print(f"lent {args.title} for {args.days} days")
            return 0

        print(main(["add", "Emma"]))                    # a test calls main() with a list
        # in loans.py:   if __name__ == "__main__": sys.exit(main())
    """)
    shell(f, """
        $ python3 loans.py add Dune --days 21
        lent Dune for 21 days
        $ echo $?
        0
        $ python3 loans.py list --sort author
        usage: loans list [-h] [--overdue] [--sort {title,due}]
        loans list: error: argument --sort: invalid choice: 'author' (choose from 'title', 'due')
        $ echo $?
        2
    """, title="the same program from the shell (usage errors go to stderr, exit code 2)", size=8.4)


def subprocess_section(ch):
    f = flow(ch)
    sec(f, "subprocess: running other programs", room=440)
    f.p("`subprocess.run` starts a program, waits for it, and hands back its exit code and output. Under the "
        "hood the OS creates a child process wired to pipes:", 13.5, gap=8)
    seq(f, ["your Python", "OS kernel", "child process"], [
        ("your Python", "OS kernel", "fork + exec(argv, env)"),
        ("OS kernel", "child process", "start, fd 0/1/2 = pipes"),
        ("child process", "your Python", "bytes on stdout / stderr", "reply"),
        ("child process", "OS kernel", "exit(2)"),
        ("OS kernel", "your Python", "wait() → returncode 2", "reply"),
    ], step=28)
    code(f, """
        import subprocess, sys

        try:
            subprocess.run(["ls", "/no/such/dir"], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print("failed with", e.returncode, "|", e.stderr.strip())

        try:
            subprocess.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2)
        except subprocess.TimeoutExpired as e:
            print("gave up after", e.timeout, "s (the child is killed)")
    """, notes={4: "check=True: non-zero exit raises", 9: "always set a timeout for things that can hang"})
    sub(f, "Never build a shell command from data", ACCENT, room=260)
    f.p("With `shell=True` your string goes to `/bin/sh`, which treats `;`, `|`, `$( )` and spaces as "
        "syntax. If any part came from a user or a filename, they can run anything. Here the \"filename\" "
        "smuggles in a second command (a harmless `echo`, but it could be `rm -rf ~`):", 13.5, gap=8)
    two_ways(f, ("shell=True + f-string: injected", """
        import subprocess
        name = "notes.txt; echo HACKED"
        r = subprocess.run(f"echo {name}", shell=True,
                           capture_output=True, text=True)
        print(r.stdout)
    """), ("a list of arguments: safe", """
        import subprocess
        name = "notes.txt; echo HACKED"
        r = subprocess.run(["echo", name],
                           capture_output=True, text=True)
        print(r.stdout)
    """), same_output=False)
    callout(f, "rule", "Pass a {B:list}: each item reaches the program as exactly one argument and no shell ever "
            "parses it. If a value could start with `-`, put `\"--\"` before it so the program can't mistake "
            "it for an option. This is the same bug as SQL injection (Ch 12): data mixed into code.")


def signals_section(ch):
    f = flow(ch)
    sec(f, "Signals: being asked to stop", room=420)
    f.p("A signal is a tiny message from the OS: \"stop\", \"the terminal closed\", \"reload\". Ctrl+C sends "
        "`SIGINT`, which Python turns into `KeyboardInterrupt`. `kill`, `systemctl stop` and `docker stop` "
        "send `SIGTERM`, which by default kills Python on the spot: no `finally`, no flush. Handle it to "
        "shut down cleanly:", 13.5, gap=8)
    code(f, """
        import subprocess, sys, textwrap

        child = textwrap.dedent('''
            import signal, sys, time
            def stop(signum, frame):
                print("got", signal.Signals(signum).name, "- saving and exiting")
                sys.exit(0)                         # raises SystemExit: finally blocks run
            signal.signal(signal.SIGTERM, stop)
            print("ready", flush=True)
            time.sleep(30)
        ''')
        p = subprocess.Popen([sys.executable, "-c", child], stdout=subprocess.PIPE, text=True)
        print(p.stdout.readline().strip())
        p.terminate()                               # sends SIGTERM
        out, _ = p.communicate(timeout=5)
        print(out.strip(), "| exit code", p.returncode)
    """, notes={8: "install the handler", 12: "Popen: start without waiting"})
    table(f, ["signal", "sent by", "default", "Python"], [
        ["`SIGINT` (2)", "Ctrl+C", "stop", "raises `KeyboardInterrupt`"],
        ["`SIGTERM` (15)", "`kill`, systemd, Docker, Kubernetes", "stop at once", "handle it: clean up, exit"],
        ["`SIGKILL` (9)", "`kill -9`, the OOM killer", "stop at once", "{R:can't be caught}"],
        ["`SIGHUP` (1)", "terminal closed; daemons: \"reload config\"", "stop", "handle if you're a daemon"],
        ["`SIGPIPE` (13)", "reader of your pipe went away (`| head`)", "stop", "ignored: you get `BrokenPipeError`"],
    ], widths=[1.4, 2.6, 1.1, 2.3], size=10)
    callout(f, "honest", "Windows has no SIGTERM in this sense: `terminate()` there kills the process outright. "
            "Only Ctrl+C (`SIGINT`) and `SIGBREAK` are portable. Signal handlers run only in the main thread, "
            "between bytecodes, so keep them tiny: set a flag or raise.")


def citizen_section(ch):
    f = flow(ch)
    sec(f, "Logging, and the good-citizen checklist", room=420)
    f.p("A command-line tool's stdout is often piped into another program, so it must contain only results. "
        "Progress and diagnostics go to stderr through `logging`, with `-v` turning up the detail:", 13.5, gap=8)
    code(f, """
        import io, logging

        def setup_logging(verbose, stream):                    # pass sys.stderr in real life
            log = logging.getLogger("loans")
            log.setLevel([logging.WARNING, logging.INFO, logging.DEBUG][min(verbose, 2)])
            handler = logging.StreamHandler(stream)
            handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
            log.handlers[:] = [handler]
            log.propagate = False
            return log

        for v in (0, 2):
            buf = io.StringIO()
            log = setup_logging(v, buf)
            log.debug("opening loans.db"); log.info("3 loans found"); log.warning("1 overdue")
            print(f"-v x{v}:", buf.getvalue().splitlines())
    """, notes={5: "-v count picks the level"})
    table(f, ["a good command-line program...", "so that..."], [
        ["writes results to stdout, messages to stderr", "`prog > out.txt` and pipes get clean data"],
        ["exits 0 on success, non-zero on failure (2 for usage)", "`&&`, scripts, CI and cron can react"],
        ["reads stdin when given no file, or `-`", "it works in the middle of a pipeline"],
        ["has `--help` and clear error messages", "nobody has to read the source (argparse does it)"],
        ["takes config as flags > env vars > file > defaults", "the same build runs anywhere (practice 14.4)"],
        ["skips colour and progress bars if `not sys.stdout.isatty()`", "logs and pipes stay readable"],
        ["handles SIGTERM and Ctrl+C: cleans up, then exits", "containers and services stop it safely"],
    ], widths=[3.3, 3.0], size=10.5)


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 14)
    stamp(f, [
        (0, "To the OS, a Python program is a process: argv and environment in, stdin/stdout/stderr, an exit "
            "code out, signals from outside. `python3 file.py` runs the interpreter, which runs your file."),
        (9, "Text streams `sys.stdin`/`stdout`/`stderr`; results to stdout, messages to stderr."),
        (11, "`sys`, `os`, `argparse`, `subprocess` (list args, `check`, `timeout`), `signal`, `logging`, `shlex`."),
    ])
    callout(f, "other", "C: `int main(int argc, char **argv)`, the return value is the exit code. Java: "
            "`main(String[] args)`, `System.exit`, `ProcessBuilder`. Go: `os.Args`, `flag`, `os/exec`. "
            "Rust: `std::env::args`, `std::process::Command`, and the `clap` crate as its argparse. The "
            "process model underneath is identical.")
    callout(f, "deep", "Vault notes: {b:20.2} Programs as managed processes · {b:20.3} Exit status and "
            "supervision · {b:20.4} Configuration · {b:20.5} Filesystem and runtime conventions · {b:19.11} "
            "Command injection and subprocess boundaries · {b:19.15} Secrets · {b:12.12} Logging and "
            "diagnostics.")


def build(ch):
    title_page(ch)
    sys_os_section(ch)
    argparse_section(ch)
    subprocess_section(ch)
    signals_section(ch)
    citizen_section(ch)
    finish(ch)
