"""Helpers that every exercise's tests can use. Tests check behaviour, never the exact code."""
import ast
import contextlib
import inspect
import io
import os
import random
import tempfile


class Fail(AssertionError):
    pass


def check(cond, msg):
    if not cond:
        raise Fail(msg)


def equal(got, expected, what="result"):
    if got != expected:
        raise Fail(f"{what}: expected {expected!r}, got {got!r}")


def rand_lists(n=200, max_len=30, lo=-50, hi=50, seed=1):
    """Random lists including the awkward ones: empty, one item, duplicates, already sorted."""
    rng = random.Random(seed)
    out = [[], [1], [2, 1], [3, 3, 3], list(range(10)), list(range(10, 0, -1))]
    for _ in range(n):
        out.append([rng.randint(lo, hi) for _ in range(rng.randint(0, max_len))])
    return out


def rand_words(n=50, seed=2):
    rng = random.Random(seed)
    letters = "abcdefghijklmnopqrstuvwxyz"
    return ["".join(rng.choice(letters) for _ in range(rng.randint(1, 8))) for _ in range(n)]


def capture(fn, *args, **kw):
    """Run fn and return (result, printed_text)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = fn(*args, **kw)
    return res, buf.getvalue()


def raises(exc, fn, *args, **kw):
    try:
        fn(*args, **kw)
    except exc as e:
        return e
    except Exception as e:  # noqa: BLE001
        raise Fail(f"expected {exc.__name__}, but got {type(e).__name__}: {e}")
    raise Fail(f"expected {exc.__name__} to be raised, but nothing was raised")


def source_tree(module):
    src = getattr(module, "__source__", None) or inspect.getsource(module)
    return ast.parse(src)


def forbid(module, *node_names, msg=None):
    """Refactor exercises: fail if the solution uses e.g. 'For', 'While', 'ListComp'."""
    for node in ast.walk(source_tree(module)):
        if type(node).__name__ in node_names:
            raise Fail(msg or f"this exercise asks you not to use {type(node).__name__} (line {node.lineno})")


def uses_name(module, name):
    """True if the solution mentions a name or attribute (e.g. 'execute', 'compare_digest')."""
    for node in ast.walk(source_tree(module)):
        if isinstance(node, ast.Name) and node.id == name:
            return True
        if isinstance(node, ast.Attribute) and node.attr == name:
            return True
    return False


def imports(module):
    names = set()
    for node in ast.walk(source_tree(module)):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


@contextlib.contextmanager
def tmpdir():
    old = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        try:
            yield d
        finally:
            os.chdir(old)
