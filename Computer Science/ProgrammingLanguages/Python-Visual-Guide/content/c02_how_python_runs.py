"""Chapter 2 - How Python runs: source -> tokens -> AST -> bytecode -> the CPython virtual machine;
compile time vs run time; .pyc caching; what import really does; ways to start a program."""
import ast
import dis

from generator import canvas as C
from content.kit import (L, W, callout, code, flow, go, pipe, practice, repl, section, seq, shell, stamp,
                         sub, table, title_block, trace, tree)
from generator.book import CheckFailed

ORDER = 2
NUM = 2
TITLE = "How Python runs your code"
SHORT = "How Python runs"
SLUG = "How-Python-runs"
ACCENT = C.PURPLE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def ast_tree(f, src, size=9.5):
    """Draw the AST of a one-line statement as a tree (leaves spread left to right)."""
    root = ast.parse(src).body[0]

    def label(n):
        if isinstance(n, ast.Name):
            return f"Name '{n.id}'"
        if isinstance(n, ast.Constant):
            return f"Constant {n.value!r}"
        if isinstance(n, ast.BinOp):
            return f"BinOp {type(n.op).__name__}"
        if isinstance(n, ast.Call):
            return "Call"
        return type(n).__name__

    def kids(n):
        out = []
        for name, val in ast.iter_fields(n):
            if name in ("ctx", "op", "type_comment"):
                continue
            if isinstance(val, ast.AST):
                out.append(val)
            elif isinstance(val, list):
                out += [v for v in val if isinstance(v, ast.AST)]
        return out

    nodes, edges = {}, []
    leaves = []

    def walk(n, depth):
        cs = kids(n)
        if not cs:
            leaves.append(n)
            xs = [len(leaves) - 1]
        else:
            xs = []
            for c in cs:
                walk(c, depth + 1)
                edges.append((id(n), id(c)))
                xs.append(nodes[id(c)][1])
        x = sum(xs) / len(xs)
        nodes[id(n)] = (label(n), x, depth)

    walk(root, 0)
    n_leaves = max(1, len(leaves) - 1)
    nodes = {k: (lab, 0.1 + 0.8 * x / n_leaves, d) for k, (lab, x, d) in nodes.items()}
    tree(f, nodes, edges, size=size)


def title_page(ch):
    title_block(ch, 2, TITLE, "from the text you type to things happening", ACCENT)
    f = ch.flow(top=190)
    f.p("When you run `python3 grades.py`, Python doesn't read your file line by line and act on it. It "
        "{B:translates the whole file first}, then runs the translation on a virtual machine. Knowing the "
        "stages explains a lot of everyday puzzles: why a syntax error stops everything before line 1 "
        "runs, why a misspelt name only fails when that line is reached, and what those `__pycache__` "
        "folders are.", 14, gap=10)
    pipe(f, [("source\n.py text", C.GREY), ("tokens", C.BLUE), ("AST\n(a tree)", C.GREEN),
             ("bytecode\n(.pyc)", C.ORANGE), ("CPython VM\neval loop", C.PURPLE)], h=46,
         under=["what you wrote", "words and symbols", "the grammar's meaning", "simple stack instructions",
                "runs them, one by one"])
    f.gap(4)
    table(f, ["stage", "done by", "you can look at it with"], [
        ["tokenise", "the tokenizer", "`python3 -m tokenize file.py`"],
        ["parse", "the parser", "`ast.parse(src)`, `python3 -m ast file.py`"],
        ["compile", "the compiler", "`compile(src, name, 'exec')`, `dis.dis(func)`"],
        ["execute", "the evaluation loop (ceval.c)", "`sys.settrace`, `pdb`, or just `print`"],
    ], widths=[1.1, 2.0, 3.0])
    callout(f, "idea", "{B:Compile time} is when the whole file is checked and translated. {B:Run time} is "
            "when each instruction actually executes. Most errors you meet happen at run time; syntax "
            "errors are the exception.")


def tokens_ast(ch):
    f = flow(ch)
    sec(f, "Stage 1 and 2: tokens, then a tree")
    f.p("The tokenizer chops text into tokens: names, operators, numbers, and indentation changes (Python's "
        "blocks are real tokens, `INDENT` and `DEDENT`).", 13.5, gap=8)
    code(f, """
        import io, tokenize
        src = "total = price * (1 + rate)"
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.string.strip():
                print(f"{tokenize.tok_name[tok.type]:<6} {tok.string!r}")
    """, out_max=10)
    f.p("The parser checks the tokens against Python's grammar and builds an {B:abstract syntax tree}. "
        "Brackets have gone: the tree's shape {B:is} the precedence. Multiplication sits above the "
        "addition, so the addition happens first:", 13.5, gap=8)
    ast_tree(f, "total = price * (1 + rate)")
    repl(f, """
        >>> import ast
        >>> print(ast.dump(ast.parse("x = a + b * 2").body[0].value))
    """, w=W)
    callout(f, "why", "This is where `SyntaxError` comes from: if the tokens can't form a tree, there's no "
            "program to run. That's why one missing bracket on line 200 stops line 1 from running.")


def bytecode(ch):
    f = flow(ch)
    sec(f, "Stage 3: bytecode, for a stack machine", room=440)
    f.p("The compiler turns the tree into {B:bytecode}: a list of tiny instructions for a virtual machine "
        "that works with a stack. Values are pushed on, operations pop their inputs and push the result. "
        "`dis` shows it:", 13.5, gap=8)
    code(f, """
        import dis

        def f(a, b):
            return a * (b + 1)

        for ins in dis.get_instructions(f):
            print(f"{ins.opname:<36} {ins.argrepr}")
    """, out_max=8)
    got = [i.opname for i in dis.get_instructions(lambda a, b: a * (b + 1))]
    want = ["RESUME", "LOAD_FAST_BORROW_LOAD_FAST_BORROW", "LOAD_SMALL_INT", "BINARY_OP", "BINARY_OP",
            "RETURN_VALUE"]
    if got != want:
        raise CheckFailed(f"ch2 bytecode changed in this Python version: {got}")
    f.p("Here's the stack as `f(3, 4)` runs (the long first name is two loads fused into one instruction, "
        "a 3.14 speed trick):", 13.5, gap=6)
    trace(f, ["instruction", "stack afterwards (top on the right)"], [
        ["LOAD_FAST..._LOAD_FAST (a, b)", "3  4"],
        ["LOAD_SMALL_INT 1", "3  4  1"],
        ["BINARY_OP +", "3  5"],
        ["BINARY_OP *", "15"],
        ["RETURN_VALUE", "(empty) → returns 15"],
    ], widths=[3, 3])
    callout(f, "other", "This is the same design as the Java Virtual Machine and .NET: compile to bytecode, "
            "run it on a VM. C and Rust compile straight to machine code instead, which is a big part of why "
            "they're faster for tight loops. PyPy is a different Python implementation that compiles hot "
            "bytecode to machine code while running (a JIT); CPython 3.13+ has an experimental JIT too.")


def two_times(ch):
    f = flow(ch)
    sec(f, "Compile time vs run time", room=420)
    f.p("Two programs, each with one mistake on its last line. Watch {B:when} each mistake is noticed:",
        13.5, gap=8)
    code(f, """
        src = 'print("line 1 runs?")\\nprint("oops"'
        try:
            compile(src, "a.py", "exec")
        except SyntaxError as e:
            print("SyntaxError before anything ran:", e.msg, "(line", e.lineno, ")")
    """)
    code(f, """
        src = 'print("line 1 runs?")\\nprint(undefined_name)'
        try:
            exec(compile(src, "b.py", "exec"))
        except NameError as e:
            print("NameError, after line 1 ran:", e)
    """)
    f.p("The first program never started. The second ran line 1 and only failed when it reached the bad "
        "name, because looking a name up is a run-time action. The same goes for functions: a typo inside "
        "a function body is only noticed when the function is {B:called}.", 13.5, gap=8)
    code(f, """
        def report():
            return totl * 2          # typo, but no error yet

        print("defined fine")
        try:
            report()
        except NameError as e:
            print("only now:", e)
    """, notes={2: "compiles: it's just a name"})
    callout(f, "trap", "So \"it ran without errors\" means only the paths you exercised are free of these "
            "mistakes. Tests (Ch 17) and a linter or type checker (which read the code without running it) "
            "catch the rest.")


def pyc_import(ch):
    f = flow(ch)
    sec(f, "What import really does", room=470)
    f.p("`import grades` isn't a text include. It's a run-time statement that {B:executes} the module once and "
        "caches the result:", 13.5, gap=8)
    pipe(f, [("import m", C.PURPLE), ("in sys.modules?", C.ORANGE), ("search sys.path", C.BLUE),
             ("compile (or load .pyc)", C.GREEN), ("run the module's code", C.RED), ("bind name m", C.GREY)],
         h=40, under=["", "yes: reuse it, stop", "finds m.py", "cache in __pycache__", "top to bottom",
                      "in your namespace"])
    code(f, """
        import sys, pathlib, importlib

        pathlib.Path("noisy.py").write_text('print("noisy is running!")\\nX = 42\\n')
        sys.path.insert(0, ".")

        import noisy
        import noisy
        print(noisy.X, "noisy" in sys.modules)
        print(sorted(p.name for p in pathlib.Path("__pycache__").iterdir()))
        importlib.reload(noisy)
    """, notes={6: "runs the file", 7: "cached: prints nothing", 9: "the saved bytecode",
                10: "reload forces a re-run"})
    f.p("Because importing {B:runs} the file, any top-level code (prints, tests, a whole program) runs on "
        "import. The standard guard keeps script-only code from running when the file is imported:", 13.5,
        gap=8)
    code(f, """
        def main():
            print("doing the real work")

        if __name__ == "__main__":     # true only when run as a script
            main()
    """, run=False, numbers=False)
    table(f, ["how the file is used", "its `__name__` is", "so the guarded code..."], [
        ["`python3 grades.py`", "`\"__main__\"`", "runs"],
        ["`python3 -m grades`", "`\"__main__\"`", "runs"],
        ["`import grades` (from another file)", "`\"grades\"`", "doesn't run"],
    ], widths=[2.6, 1.6, 1.8])
    callout(f, "trap", "Never name your file after a stdlib module (`random.py`, `json.py`, `secrets.py`). "
            "The current folder comes first on `sys.path`, so `import random` anywhere in your program "
            "imports {R:your} file instead.")


def starting(ch):
    f = flow(ch)
    sec(f, "Ways to start Python, and which Python", room=420)
    shell(f, """
        $ python3 grades.py              # run a file
        $ python3 -m http.server 8000    # run a module found on sys.path (here: a stdlib web server)
        $ python3 -c 'print(2**100)'     # run a string
        $ python3 -i grades.py           # run, then drop into the REPL with its variables
        $ python3 -X importtime -c 'import json'   # how long each import took
    """)
    f.p("You may have several Pythons installed. Inside a program, `sys` tells you which one is running and "
        "where it looks for modules:", 13.5, gap=8)
    code(f, """
        import sys
        print(sys.version_info[:3], sys.implementation.name)
        print(sys.executable.rsplit("/", 2)[-2:])
        print([p for p in sys.path if p.endswith("site-packages")][:1])
    """)
    sub(f, "Virtual environments in one picture", ACCENT)
    f.p("A virtual environment (`python3 -m venv .venv`) is a folder with its own `python` link and its own "
        "`site-packages`, so each project's pip installs stay separate. Activating it just puts its `bin/` "
        "first on your `PATH`. Chapter 19 uses one.", 13.5, gap=8)
    pipe(f, [("system python3\n/usr/lib/python3.14", C.GREY), ("project A .venv\nits site-packages", C.BLUE),
             ("project B .venv\nits site-packages", C.GREEN)], h=46, labels=["", ""],
         under=["the stdlib, shared", "requests 2.32", "requests 2.28, numpy"])


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 2)
    stamp(f, [
        (0, "CPython compiles each module to bytecode (cached as `.pyc` in `__pycache__`), then a stack-based "
            "VM interprets it. Syntax errors at compile time; name, type and value errors at run time."),
        (8, "`import` runs a module once and caches it in `sys.modules`; it's found on `sys.path`. "
            "`if __name__ == \"__main__\"` separates script code from library code."),
    ])
    callout(f, "deep", "Vault notes: {b:15.2} From source bytes to an abstract syntax tree · {b:15.4} Code "
            "objects · {b:15.5} Disassembly and bytecode · {b:15.8} The evaluation loop · {b:10.2} Import is "
            "execution with caching · {b:10.5} `__name__` and entry execution · {b:10.14} Import security "
            "and shadowing.")


def build(ch):
    title_page(ch)
    tokens_ast(ch)
    bytecode(ch)
    two_times(ch)
    pyc_import(ch)
    starting(ch)
    finish(ch)
