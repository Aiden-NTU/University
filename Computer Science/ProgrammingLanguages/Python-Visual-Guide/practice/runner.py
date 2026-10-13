"""Run an exercise's tests against a solution file, through unittest, with a friendly report."""
import importlib.util
import os
import signal
import sys
import tempfile
import textwrap
import traceback
import unittest

from practice import testkit

TIME_LIMIT = 10  # seconds per test: catches accidental infinite loops


def load_module(path, name="solution"):
    spec = importlib.util.spec_from_file_location(f"{name}_{abs(hash(path))}", path)
    mod = importlib.util.module_from_spec(spec)
    with open(path) as f:
        mod.__source__ = f.read()
    d = os.path.dirname(path)
    sys.path.insert(0, d)
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(d)
    return mod


def load_source(src, name="alternative"):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(textwrap.dedent(src))
        p = f.name
    try:
        return load_module(p, name)
    finally:
        os.unlink(p)


class _Timeout(Exception):
    pass


def _alarm(*_):
    raise _Timeout(f"took longer than {TIME_LIMIT}s (infinite loop?)")


def collect(e, mod):
    ns = {k: getattr(testkit, k) for k in dir(testkit) if not k.startswith("_")}
    exec(compile(textwrap.dedent(e["tests"]), f"<tests {e['id']}>", "exec"), ns)
    tests = [(k, v) for k, v in ns.items() if k.startswith("test_") and callable(v)]

    def wrap(fn):
        def run():
            old_dir = os.getcwd()
            has_alarm = hasattr(signal, "SIGALRM")
            if has_alarm:
                signal.signal(signal.SIGALRM, _alarm)
                signal.alarm(TIME_LIMIT)
            try:
                with tempfile.TemporaryDirectory() as d:
                    os.chdir(d)
                    fn(mod)
            finally:
                os.chdir(old_dir)
                if has_alarm:
                    signal.alarm(0)
        run.__name__ = fn.__name__
        return run

    return [unittest.FunctionTestCase(wrap(fn), description=name[5:].replace("_", " ")) for name, fn in tests]


class Report(unittest.TestResult):
    def __init__(self, quiet=False):
        super().__init__()
        self.quiet = quiet
        self.lines = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.lines.append(("ok", test.shortDescription() or str(test), ""))

    def _bad(self, test, err):
        exc_type, exc, tb = err
        if isinstance(exc, AssertionError):
            msg = str(exc) or "assertion failed"
        else:
            frames = traceback.extract_tb(tb)
            mine = [fr for fr in frames if "solution" in os.path.basename(fr.filename) or fr.filename.startswith("/tmp")]
            where = f" (line {mine[-1].lineno} of your solution)" if mine else ""
            msg = f"{exc_type.__name__}: {exc}{where}"
        self.lines.append(("FAIL", test.shortDescription() or str(test), msg))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._bad(test, err)

    def addError(self, test, err):
        super().addError(test, err)
        self._bad(test, err)


def run(e, mod, quiet=False):
    suite = unittest.TestSuite(collect(e, mod))
    rep = Report(quiet)
    suite.run(rep)
    passed = rep.wasSuccessful() and rep.testsRun > 0
    if not quiet:
        for status, desc, msg in rep.lines:
            mark = "\033[32m  pass\033[0m" if status == "ok" else "\033[31m  FAIL\033[0m"
            print(f"{mark}  {desc}")
            if msg:
                for ln in msg.splitlines():
                    print(f"          {ln}")
        n_ok = sum(1 for s, _, _ in rep.lines if s == "ok")
        print(f"\n  {n_ok}/{rep.testsRun} tests passed" + ("  -- well done!" if passed else ""))
    return passed, rep
