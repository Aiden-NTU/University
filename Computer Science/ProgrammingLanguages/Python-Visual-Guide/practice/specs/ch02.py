EXERCISES = [
    dict(
        id="2.1", kind="explore", title="Count the node types in a program (ast)",
        task="""
        Write `node_counts(source)` returning a dict `{node type name: count}` for every node in the
        AST of `source` (a string of Python code), e.g. `{"Module": 1, "Assign": 1, "Name": 2, ...}`.
        Include context nodes like `Load`/`Store` exactly as `ast.walk` yields them.

        Explore `ast` in the REPL first: `ast.parse`, `ast.dump(..., indent=2)`, `ast.walk`.
        """,
        stub='''
        import ast

        def node_counts(source):
            ...
        ''',
        tests='''
        import ast

        def test_tiny(m):
            got = m.node_counts("x = 1")
            for k, v in {"Module": 1, "Assign": 1, "Name": 1, "Constant": 1, "Store": 1}.items():
                equal(got.get(k), v, f"count of {k} in 'x = 1'")

        def test_bigger(m):
            src = "def f(a):\\n    return [a * i for i in range(3)]\\nprint(f(2))"
            got = m.node_counts(src)
            equal(got["FunctionDef"], 1, "FunctionDef")
            equal(got["ListComp"], 1, "ListComp")
            equal(got["Call"], 3, "Calls: range, print, f")
            equal(sum(got.values()), sum(1 for _ in ast.walk(ast.parse(src))), "total nodes")

        def test_syntax_error_propagates(m):
            raises(SyntaxError, m.node_counts, "def (:")
        ''',
        alts={
            "Counter": ('''
                import ast
                from collections import Counter

                def node_counts(source):
                    return dict(Counter(type(n).__name__ for n in ast.walk(ast.parse(source))))
            ''', "ast.walk visits every node (breadth-first); Counter tallies the type names."),
            "NodeVisitor": ('''
                import ast

                class Counter(ast.NodeVisitor):
                    def __init__(self):
                        self.counts = {}
                    def generic_visit(self, node):
                        name = type(node).__name__
                        self.counts[name] = self.counts.get(name, 0) + 1
                        super().generic_visit(node)

                def node_counts(source):
                    c = Counter()
                    c.visit(ast.parse(source))
                    return c.counts
            ''', "NodeVisitor walks depth-first and lets you add visit_Name, visit_Call... methods later: "
                 "the shape linters use."),
        },
    ),
    dict(
        id="2.2", kind="build", title="A safe calculator (no eval)",
        task="""
        `eval()` on user input runs arbitrary code. Write `calc(expr, variables=None)` that evaluates
        arithmetic **by walking the AST yourself**:

        - numbers (int/float), names looked up in the `variables` dict
        - binary `+ - * / // % **` and unary `-` / `+`, with brackets
        - anything else (calls, attributes, strings, comparisons, unknown names...) → `ValueError`

        Parse with `ast.parse(expr, mode="eval")`. Don't call `eval` or `exec` (the tests check).
        """,
        stub='''
        import ast
        import operator

        def calc(expr, variables=None):
            ...
        ''',
        tests='''
        import random

        def rand_expr(rng, depth=0):
            if depth > 3 or rng.random() < 0.3:
                return rng.choice([str(rng.randint(0, 9)), "x", "y", f"{rng.randint(1, 9)}.5"])
            op = rng.choice(["+", "-", "*", "/", "//", "%"])
            if rng.random() < 0.15:
                return f"-({rand_expr(rng, depth + 1)})"
            return f"({rand_expr(rng, depth + 1)} {op} {rand_expr(rng, depth + 1)})"

        def test_matches_python(m):
            rng = random.Random(8)
            env = {"x": 3, "y": 7}
            done = 0
            while done < 300:
                e = rand_expr(rng)
                try:
                    want = eval(e, {}, dict(env))
                except ZeroDivisionError:
                    raises(ZeroDivisionError, m.calc, e, env)
                    continue
                equal(m.calc(e, env), want, e)
                done += 1

        def test_power_and_unary(m):
            equal(m.calc("2 ** 10"), 1024, "power")
            equal(m.calc("+-+3"), -3, "unary chain")

        def test_refuses_code(m):
            for bad in ["__import__('os')", "x.real", "'a' * 3", "1 < 2", "z + 1", "[1, 2]", "lambda: 1",
                        "(1).__class__"]:
                raises(ValueError, m.calc, bad, {"x": 1})

        def test_no_eval(m):
            check(not uses_name(m, "eval") and not uses_name(m, "exec"), "don't use eval/exec")
        ''',
        alts={
            "recursive walk with operator table": ('''
                import ast
                import operator

                BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                       ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
                       ast.Mod: operator.mod, ast.Pow: operator.pow}
                UN = {ast.USub: operator.neg, ast.UAdd: operator.pos}

                def calc(expr, variables=None):
                    env = variables or {}

                    def ev(n):
                        match n:
                            case ast.Expression(body=b):
                                return ev(b)
                            case ast.Constant(value=v) if type(v) in (int, float):
                                return v
                            case ast.Name(id=name) if name in env:
                                return env[name]
                            case ast.BinOp(left=a, op=op, right=b) if type(op) in BIN:
                                return BIN[type(op)](ev(a), ev(b))
                            case ast.UnaryOp(op=op, operand=a) if type(op) in UN:
                                return UN[type(op)](ev(a))
                        raise ValueError(f"not allowed: {ast.dump(n)[:40]}")

                    try:
                        tree = ast.parse(expr, mode="eval")
                    except SyntaxError as e:
                        raise ValueError(str(e)) from e
                    return ev(tree)
            ''', "An allow-list: only the node types we name can run; everything else is refused. "
                 "`type(v) in (int, float)` also rejects True/False, which are ints in disguise."),
        },
    ),
    dict(
        id="2.3", kind="explore", title="Which globals does a function use? (dis)",
        task="""
        Write `globals_used(func)` returning the **sorted, de-duplicated** list of global (or built-in)
        names the function's bytecode loads, e.g. `print`, `len`, a module name, a global constant.

        Use `dis.get_instructions(func)` and look at instructions whose `opname` is `LOAD_GLOBAL`;
        the name is in `.argval`. (Names used only inside nested functions don't count.)
        """,
        stub='''
        import dis

        def globals_used(func):
            ...
        ''',
        tests='''
        import math
        LIMIT = 10

        def f1(xs):
            return [math.sqrt(x) for x in xs if x < LIMIT]

        def f2(a, b):
            total = a + b
            return total

        def f3(s):
            print(len(s), len(s))
            return sorted(s)

        def test_examples(m):
            equal(m.globals_used(f1), ["LIMIT", "math"], "f1")
            equal(m.globals_used(f2), [], "f2 uses only locals")
            equal(m.globals_used(f3), ["len", "print", "sorted"], "f3")
        ''',
        alts={
            "set comprehension": ('''
                import dis

                def globals_used(func):
                    return sorted({i.argval for i in dis.get_instructions(func) if i.opname == "LOAD_GLOBAL"})
            ''', "Comprehensions are inlined into the function since 3.12, so their globals show up too."),
        },
    ),
    dict(
        id="2.4", kind="refactor", title="Make the script importable",
        task="""
        `solution.py` is a script: it prints a report as soon as it's loaded. Another program wants to
        import its `average` and `grade` functions **without** the report printing.

        Restructure it so importing it prints nothing, while `python3 solution.py` still prints the
        same report (put the script part in `main()` behind the `__name__` guard). Keep the functions'
        behaviour the same.
        """,
        stub='''
        def average(marks):
            return sum(marks) / len(marks)

        def grade(avg):
            return "A" if avg >= 70 else "B" if avg >= 60 else "C" if avg >= 50 else "F"

        marks = {"ana": [72, 81, 65], "ben": [55, 48, 61]}
        for name, ms in marks.items():
            avg = average(ms)
            print(f"{name}: {avg:.1f} {grade(avg)}")
        ''',
        stub_should_fail=True,
        tests='''
        import importlib.util, io, contextlib, subprocess, sys, os

        def load_quietly(m):
            with open("mod.py", "w") as fh:
                fh.write(m.__source__)
            buf = io.StringIO()
            spec = importlib.util.spec_from_file_location("mod_under_test", "mod.py")
            mod = importlib.util.module_from_spec(spec)
            with contextlib.redirect_stdout(buf):
                spec.loader.exec_module(mod)
            return mod, buf.getvalue()

        def test_import_is_silent(m):
            mod, out = load_quietly(m)
            equal(out, "", "printed on import")

        def test_functions(m):
            mod, _ = load_quietly(m)
            equal(mod.average([1, 2, 3]), 2, "average")
            equal([mod.grade(x) for x in (75, 65, 55, 10)], ["A", "B", "C", "F"], "grade")

        def test_still_a_script(m):
            with open("script.py", "w") as fh:
                fh.write(m.__source__)
            out = subprocess.run([sys.executable, "script.py"], capture_output=True, text=True).stdout
            equal(out, "ana: 72.7 A\\nben: 54.7 C\\n", "output of python3 solution.py")
        ''',
        alts={
            "main + guard": ('''
                def average(marks):
                    return sum(marks) / len(marks)

                def grade(avg):
                    return "A" if avg >= 70 else "B" if avg >= 60 else "C" if avg >= 50 else "F"

                def main():
                    marks = {"ana": [72, 81, 65], "ben": [55, 48, 61]}
                    for name, ms in marks.items():
                        avg = average(ms)
                        print(f"{name}: {avg:.1f} {grade(avg)}")

                if __name__ == "__main__":
                    main()
            ''', "Moving the data into main() also stops `marks`, `name` and `avg` leaking out as module "
                 "globals for importers to trip over."),
        },
    ),
    dict(
        id="2.5", kind="project", title="Mini-project: compile to your own stack machine",
        task="""
        Build a miniature CPython: a compiler from arithmetic to bytecode, and a VM that runs it.

        - `compile_expr(source)` takes an expression like `"a * (b + 1) - 2"` and returns a list of
          instructions (tuples): `("PUSH", number)`, `("LOAD", name)`, `("ADD",)`, `("SUB",)`,
          `("MUL",)`, `("DIV",)`, `("NEG",)`.
        - `run(code, env)` executes them on a stack and returns the final value (the only item left).

        Use `ast` to parse, and emit instructions in **post-order** (left operand, right operand,
        then the operation): exactly what CPython's compiler does. Unsupported syntax → `ValueError`.
        Then: add `("POW",)` and `**`, and print your bytecode next to `dis.dis` for the same expression.
        """,
        stub='''
        import ast

        def compile_expr(source):
            ...

        def run(code, env):
            ...
        ''',
        tests='''
        import random
        OPS = {"PUSH", "LOAD", "ADD", "SUB", "MUL", "DIV", "NEG"}

        def rand_expr(rng, d=0):
            if d > 3 or rng.random() < 0.3:
                return rng.choice(["a", "b", "c", str(rng.randint(1, 9))])
            if rng.random() < 0.1:
                return f"-{rand_expr(rng, d + 1)}"
            return f"({rand_expr(rng, d + 1)} {rng.choice('+-*/')} {rand_expr(rng, d + 1)})"

        def test_example(m):
            code = m.compile_expr("a * (b + 1)")
            equal([tuple(i) for i in code], [("LOAD", "a"), ("LOAD", "b"), ("PUSH", 1), ("ADD",), ("MUL",)],
                  "bytecode for a * (b + 1)")
            equal(m.run(code, {"a": 3, "b": 4}), 15, "run")

        def test_random(m):
            rng = random.Random(6)
            env = {"a": 3, "b": -2, "c": 0.5}
            n = 0
            while n < 300:
                e = rand_expr(rng)
                try:
                    want = eval(e, {}, dict(env))
                except ZeroDivisionError:
                    continue
                code = m.compile_expr(e)
                check(all(ins[0] in OPS for ins in code), f"unknown instruction in {code}")
                equal(m.run(code, env), want, e)
                n += 1

        def test_rejects(m):
            for bad in ["f(1)", "a.b", "'s'", "a < b"]:
                raises(ValueError, m.compile_expr, bad)
        ''',
        alts={
            "visitor + loop": ('''
                import ast

                BIN = {ast.Add: "ADD", ast.Sub: "SUB", ast.Mult: "MUL", ast.Div: "DIV"}

                def compile_expr(source):
                    code = []

                    def emit(n):
                        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
                            code.append(("PUSH", n.value))
                        elif isinstance(n, ast.Name):
                            code.append(("LOAD", n.id))
                        elif isinstance(n, ast.BinOp) and type(n.op) in BIN:
                            emit(n.left)
                            emit(n.right)
                            code.append((BIN[type(n.op)],))
                        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
                            emit(n.operand)
                            code.append(("NEG",))
                        else:
                            raise ValueError(f"unsupported: {type(n).__name__}")

                    emit(ast.parse(source, mode="eval").body)
                    return code

                def run(code, env):
                    stack = []
                    for op, *arg in code:
                        if op == "PUSH":
                            stack.append(arg[0])
                        elif op == "LOAD":
                            stack.append(env[arg[0]])
                        elif op == "NEG":
                            stack.append(-stack.pop())
                        else:
                            b, a = stack.pop(), stack.pop()
                            stack.append({"ADD": a + b, "SUB": a - b, "MUL": a * b}[op] if op != "DIV" else a / b)
                    (result,) = stack
                    return result
            ''', "Pop order matters: the right operand is on top. `(result,) = stack` asserts exactly one "
                 "value is left, catching compiler bugs. Note: the dict computes all three results; fine "
                 "for numbers, wasteful in general."),
        },
    ),
]

DRILLS = [
    dict(kind="recall", q="Which module shows a function's bytecode?", a=["dis"]),
    dict(kind="recall", q="Which module parses source into a tree?", a=["ast"]),
    dict(kind="recall", q="Where does import cache already-loaded modules? (module.attribute)",
         a=["sys.modules"]),
    dict(kind="recall", q="Folder where CPython stores compiled .pyc files?", a=["__pycache__"]),
    dict(kind="predict", code="def f():\n    return missing_name\nprint('defined')",
         why="Names are looked up when the line runs; f is never called."),
    dict(kind="predict", code="print(__name__)", why="Code run directly (or exec'd as main) has __name__ == '__main__'."),
    dict(kind="predict", code="import ast\nprint(type(ast.parse('1 + 2', mode='eval').body).__name__)"),
]
