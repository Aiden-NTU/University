"""Chapter 16 - Concurrency: concurrency vs parallelism, threads, races and locks, queues, thread and process
pools, the GIL (and free-threaded builds), asyncio with TaskGroup and timeouts, an async chat server."""
import os
import subprocess
import sys
import tempfile
import textwrap

from generator import canvas as C
from content.kit import (callout, code, flow, pipe, practice, section, shell, stamp, sub, table, timeline,
                         title_block, trace, two_ways)

ORDER = 16
NUM = 16
TITLE = "Concurrency"
SHORT = "Concurrency"
SLUG = "Concurrency"
ACCENT = C.TEAL

PRIMES = '''
import os, sys, time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def count_primes(lo, hi):                       # pure CPU work: no waiting at all
    n = 0
    for k in range(max(lo, 2), hi):
        if all(k % d for d in range(2, int(k ** 0.5) + 1)):
            n += 1
    return n

CHUNKS = [(i * 150_000, (i + 1) * 150_000) for i in range(4)]

def timed(label, run):
    t0 = time.perf_counter()
    total = run()
    print(f"{label:<12} {total} primes  {time.perf_counter() - t0:5.2f} s")

if __name__ == "__main__":                      # required: worker processes import this file
    print("GIL enabled:", sys._is_gil_enabled(), "| cores:", os.cpu_count())
    timed("sequential", lambda: sum(count_primes(lo, hi) for lo, hi in CHUNKS))
    with ThreadPoolExecutor(4) as ex:
        timed("4 threads", lambda: sum(ex.map(count_primes, *zip(*CHUNKS))))
    with ProcessPoolExecutor(4) as ex:
        timed("4 processes", lambda: sum(ex.map(count_primes, *zip(*CHUNKS))))
'''


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


def run_script(src):
    """Run a real script in a fresh interpreter and return what it printed."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "primes.py")
        with open(path, "w") as fh:
            fh.write(textwrap.dedent(src))
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=300, cwd=d)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout.rstrip("\n")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 16, TITLE, "doing several things at once, and the bugs that come with it", ACCENT)
    f = ch.flow(top=190)
    f.p("Most programs spend their time {B:waiting}: for the network, the disk, a database. "
        "{B:Concurrency} means making progress on several tasks by working on one while the others wait. "
        "{B:Parallelism} means literally computing on several CPU cores at the same instant. Three jobs, "
        "each 1 unit of work plus 3 units of waiting for a server:", 14, gap=10)
    W_, G_ = ACCENT, C.GREY
    f.p("**One at a time**: 12 units", 12, gap=2)
    timeline(f, ["main"], [
        (0, 0, 1, "A", W_), (0, 1, 4, "wait", G_), (0, 4, 5, "B", W_), (0, 5, 8, "wait", G_),
        (0, 8, 9, "C", W_), (0, 9, 12, "wait", G_)], 12, unit="", ticks=[0, 4, 8, 12], lane_h=18, gap=8)
    f.p("**Concurrent** (threads or asyncio, one core is enough): the waits overlap, 6 units", 12, gap=2)
    timeline(f, ["task A", "task B", "task C"], [
        (0, 0, 1, "A", W_), (0, 1, 4, "wait", G_), (1, 1, 2, "B", W_), (1, 2, 5, "wait", G_),
        (2, 2, 3, "C", W_), (2, 3, 6, "wait", G_)], 12, unit="", ticks=[0, 4, 8, 12], lane_h=18, gap=8)
    f.p("**Parallel** (processes, several cores): pure computing finishes 3× sooner", 12, gap=2)
    timeline(f, ["core 1", "core 2", "core 3"], [
        (0, 0, 4, "compute A", C.PURPLE), (1, 0, 4, "compute B", C.PURPLE), (2, 0, 4, "compute C", C.PURPLE)],
        12, unit="", ticks=[0, 4, 8, 12], lane_h=18, gap=8)
    table(f, ["your program mostly...", "use", "why"], [
        ["waits on I/O (network, disk, DB)", "threads, or `asyncio`", "waiting releases the CPU for others"],
        ["waits on thousands of connections", "`asyncio`", "a task costs KB; a thread costs MB"],
        ["computes (CPU-bound pure Python)", "processes (`ProcessPoolExecutor`)", "each process has its own GIL"],
        ["crunches arrays", "NumPy (Ch 18)", "its C loops already run outside the GIL"],
    ], widths=[2.4, 2.3, 2.6], size=10.5)


def threads_section(ch):
    f = flow(ch)
    sec(f, "Threads: several flows in one program", room=420)
    f.p("A thread is a separate flow of execution sharing the program's memory. `start()` launches it, "
        "`join()` waits for it to finish. Here five slow \"downloads\" (a 0.2 s sleep stands in for the "
        "network) run one by one, then all at once:", 13.5, gap=8)
    code(f, """
        import threading, time

        def download(name, results):
            time.sleep(0.2)                         # waiting: the thread gives up the CPU
            results[name] = f"{name}: 200 OK"

        names = ["dune", "emma", "ubik", "kim", "beloved"]

        results, t0 = {}, time.perf_counter()
        for n in names:
            download(n, results)
        print("one by one:", round(time.perf_counter() - t0, 1), "s")

        results, t0 = {}, time.perf_counter()
        threads = [threading.Thread(target=download, args=(n, results)) for n in names]
        for t in threads:
            t.start()
        for t in threads:
            t.join()                                # wait for every thread
        print("threaded:  ", round(time.perf_counter() - t0, 1), "s,", len(results), "results")
    """, notes={4: "I/O-bound: threads help", 19: "forget join() and you read results too early"})
    sub(f, "Shared memory means races", ACCENT, room=300)
    f.p("Threads can be paused {B:between any two steps}. `balance = balance + 1` is three steps: read, add, "
        "write. If two threads interleave them, one update is lost:", 13.5, gap=6)
    trace(f, ["step", "thread 1", "thread 2", "balance"], [
        ["1", "reads 5", "", "5"],
        ["2", "", "reads 5", "5"],
        ["3", "writes 5 + 1", "", "6"],
        ["4", "", "writes 5 + 1", "6  (should be 7)"],
    ], widths=[0.7, 2, 2, 2], size=10.5)
    code(f, """
        balance = 0
        lock = threading.Lock()

        def deposit(times, use_lock):
            global balance
            for _ in range(times):
                if use_lock:
                    with lock:                       # only one thread inside at a time
                        balance = balance + 1
                else:
                    current = balance
                    time.sleep(0)                    # any switch here loses updates
                    balance = current + 1

        for use_lock in (False, True):
            balance = 0
            ts = [threading.Thread(target=deposit, args=(1000, use_lock)) for _ in range(4)]
            for t in ts: t.start()
            for t in ts: t.join()
            print("with lock:" if use_lock else "no lock:  ", balance == 4000)
    """, notes={8: "the critical section", 12: "sleep(0) makes the race reliable to show"})
    callout(f, "trap", "A race may pass every test and fail once a week in production, because it depends on "
            "timing. The GIL does {B:not} save you: it stops two threads running bytecode at the same instant, "
            "but a thread can still be switched out between the read and the write. Protect every shared "
            "mutable value with a lock, or don't share it (next page).")


def queue_section(ch):
    f = flow(ch)
    sec(f, "Queues: share by passing messages", room=420)
    f.p("The safest shared data is none. Instead, threads hand work to each other through a "
        "`queue.Queue`, which does its own locking. Producers `put`, consumers `get`; a full or empty queue "
        "makes the caller wait:", 13.5, gap=8)
    pipe(f, ["producer\n(main thread)", "queue.Queue\n(maxsize=10)", "worker 1\nworker 2\nworker 3", "results"],
         color=ACCENT, labels=["put(job)", "get()", "put(result)"], h=56,
         under=["", "full? put() waits: backpressure", "", ""])
    code(f, """
        import queue, threading

        jobs, results = queue.Queue(maxsize=10), queue.Queue()

        def worker():
            while (n := jobs.get()) is not None:      # None = "no more work" (a sentinel)
                results.put((n, n * n))

        workers = [threading.Thread(target=worker) for _ in range(3)]
        for w in workers: w.start()
        for n in range(8):
            jobs.put(n)
        for _ in workers:
            jobs.put(None)                            # one sentinel per worker
        for w in workers: w.join()
        print(sorted(results.get() for _ in range(results.qsize())))
    """, notes={6: "get() blocks while empty", 14: "how workers know to stop"})
    callout(f, "rule", "Prefer queues to locks. A lock protects data that many threads touch; a queue moves "
            "each piece of data so only one thread owns it at a time. Go's motto is the same idea: \"don't "
            "communicate by sharing memory; share memory by communicating.\"")
    callout(f, "trap", "Deadlock: thread 1 holds lock A and waits for B while thread 2 holds B and waits for A. "
            "Both wait forever. Avoid it by always taking locks in the same global order (practice 16.1), by "
            "holding only one at a time, or by using `lock.acquire(timeout=...)` and backing off.")


def pools_section(ch):
    f = flow(ch)
    sec(f, "Pools, and the GIL", room=420)
    f.p("Starting and joining threads by hand gets tedious. `concurrent.futures` gives you a pool of "
        "workers and a {B:future} for each job: a placeholder for a result that will exist later.", 13.5, gap=8)
    code(f, """
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def check(url):
            time.sleep(0.1 if "slow" not in url else 0.3)
            if "bad" in url:
                raise ConnectionError(f"{url} refused")
            return url, 200

        urls = ["a.org", "slow.org", "bad.org", "b.org"]
        with ThreadPoolExecutor(max_workers=4) as pool:
            print(list(pool.map(check, ["a.org", "b.org"])))           # results in input order
            futures = {pool.submit(check, u): u for u in urls}
            for fut in as_completed(futures):                         # in finishing order
                try:
                    print("done:", fut.result())
                except ConnectionError as e:
                    print("failed:", e)
    """, notes={13: "submit returns a Future at once", 16: "result() re-raises the worker's error"})
    f.p("So far all the waiting was I/O. For pure computation, CPython's {B:GIL} (global interpreter lock) "
        "lets only one thread run Python bytecode at a time, so threads don't speed it up; separate "
        "processes do:", 13.5, gap=8)
    spans = [(k % 2, k, k + 1, "runs", ACCENT) for k in range(8)]
    spans += [(1 - k % 2, k, k + 1, "waits", C.GREY) for k in range(8)]
    spans += [(2, 0, 4, "runs", C.PURPLE), (3, 0, 4, "runs", C.PURPLE)]
    timeline(f, ["thread 1", "thread 2", "process 1", "process 2"], spans, 8, unit="", ticks=[0, 4, 8],
             lane_h=20)
    f.p("Two CPU-bound threads take turns holding the GIL, so together they're no faster than one. Two "
        "processes each have their own interpreter and GIL, and finish the same work in half the time. "
        "This script was run while building this page:", 13.5, gap=8)
    code(f, PRIMES, run=False, title="primes.py", size=8.6)
    shell(f, "$ python3 primes.py\n" + run_script(PRIMES), title="its real output on the machine that built this book")
    callout(f, "honest", "Processes cost more: each starts a fresh interpreter, and arguments and results are "
            "pickled between them, so only send small inputs and get back small outputs. Python 3.13+ also ships "
            "an optional {B:free-threaded} build (`python3.14t`, PEP 703/779) with no GIL, where threads do run "
            "CPU work in parallel. It's officially supported from 3.14 but not the default, and C extensions must "
            "opt in. Locks matter even more there.")


def asyncio_section(ch):
    f = flow(ch)
    sec(f, "asyncio: thousands of waits on one thread", room=440)
    f.p("`asyncio` runs many tasks on {B:one} thread. An `async def` function is a coroutine; at each "
        "`await` it pauses and the {B:event loop} runs another task that's ready. No thread switches you "
        "out by surprise: tasks switch only at `await`, so races are much rarer.", 13.5, gap=8)
    code(f, """
        import asyncio, time

        async def fetch(name, delay):
            await asyncio.sleep(delay)              # pause here; the loop runs other tasks
            return f"{name} done"

        async def main():
            t0 = time.perf_counter()
            results = await asyncio.gather(fetch("a", 0.2), fetch("b", 0.1), fetch("c", 0.15))
            print(results, round(time.perf_counter() - t0, 1), "s")

        asyncio.run(main())                         # start the event loop, run main, stop
    """, notes={9: "run all three concurrently; results in argument order"})
    sub(f, "Structured concurrency: TaskGroup and timeouts", ACCENT, room=220)
    code(f, """
        async def main():
            try:
                async with asyncio.timeout(0.12):            # a deadline for the whole block
                    async with asyncio.TaskGroup() as tg:     # every task finishes before we leave
                        fast = tg.create_task(fetch("fast", 0.05))
                        slow = tg.create_task(fetch("slow", 1.0))
            except TimeoutError:
                print("timed out:", fast.result(), "| slow cancelled:", slow.cancelled())

        asyncio.run(main())
    """, notes={4: "if one task fails, the rest are cancelled"})
    f.p("The one rule: never call blocking code inside a coroutine. `time.sleep`, `requests.get` or a "
        "slow loop freeze the whole loop, and every other task with it:", 13.5, gap=6)
    two_ways(f, ("time.sleep: blocks the loop", """
        import asyncio, time
        async def job():
            time.sleep(0.1)
        async def main():
            t0 = time.perf_counter()
            await asyncio.gather(job(), job(), job())
            print(round(time.perf_counter() - t0, 1))
        asyncio.run(main())
    """), ("await asyncio.sleep: yields", """
        import asyncio, time
        async def job():
            await asyncio.sleep(0.1)
        async def main():
            t0 = time.perf_counter()
            await asyncio.gather(job(), job(), job())
            print(round(time.perf_counter() - t0, 1))
        asyncio.run(main())
    """), same_output=False)
    callout(f, "rule", "Stuck with a blocking library in async code? `await asyncio.to_thread(blocking_fn, "
            "args)` runs it in a thread and awaits the result, so the loop keeps going.")


def chat_section(ch):
    f = flow(ch)
    sec(f, "An async chat server, end to end", room=440)
    f.p("This is where asyncio shines: a server holding many idle connections. Each client gets a "
        "coroutine; while it waits for that client's next line, the loop serves everyone else. Two clients "
        "connect and one talks:", 13.5, gap=8)
    code(f, """
        import asyncio

        clients = set()

        async def handle(reader, writer):                     # one coroutine per client
            clients.add(writer)
            try:
                while line := await reader.readline():        # b"" when the client leaves
                    for w in clients - {writer}:
                        w.write(line)
                        await w.drain()                       # wait if their buffer is full
            finally:
                clients.discard(writer)
                writer.close()

        async def main():
            server = await asyncio.start_server(handle, "127.0.0.1", 0)
            port = server.sockets[0].getsockname()[1]
            async with asyncio.timeout(5):
                r1, w1 = await asyncio.open_connection("127.0.0.1", port)
                r2, w2 = await asyncio.open_connection("127.0.0.1", port)
                await asyncio.sleep(0.05)                     # let the server register both
                w1.write(b"hi from ana\\n")
                print(await r2.readline())
                w1.close(); w2.close()
            server.close()

        asyncio.run(main())
    """, notes={8: "framing by newline (Ch 15)", 11: "backpressure"})
    table(f, ["", "threads", "asyncio", "processes"], [
        ["switches", "anywhere (preemptive)", "only at `await` (cooperative)", "separate programs"],
        ["shared memory", "yes: needs locks", "yes, safer: no surprise switches", "no: pickle messages"],
        ["cost each", "~MB of stack", "~KB", "a whole interpreter"],
        ["CPU-bound speed-up", "no (GIL), yes when free-threaded", "no", "{G:yes}"],
        ["works with blocking libraries", "{G:yes}", "only via `to_thread`", "{G:yes}"],
    ], widths=[1.8, 2.2, 2.4, 1.9], size=10)


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 16)
    stamp(f, [
        (10, "Threads share memory (protect it with `Lock`, or pass data through `queue.Queue`). The GIL stops "
             "CPU parallelism in threads on the default build; use processes for CPU work. `asyncio`: one thread, "
             "cooperative tasks that switch at `await`; `TaskGroup` and `asyncio.timeout` keep them structured."),
        (11, "`threading`, `queue`, `concurrent.futures`, `multiprocessing`, `asyncio`, `contextvars`."),
    ])
    callout(f, "other", "Java and C#: real parallel threads, `synchronized`/`lock`, executors and futures. "
            "JavaScript: one thread and an event loop, exactly asyncio's model (`async/await` came from C#). "
            "Go: goroutines (cheap threads) and channels (queues). Rust: threads with the compiler refusing to "
            "build data races, plus async with tokio.")
    callout(f, "deep", "Vault notes: {b:14.1} Concurrency is a lifetime relation · {b:14.2} Interleaving and race "
            "conditions · {b:14.4} Threads · {b:14.5} The CPython global interpreter lock · {b:14.6} Thread "
            "communication with queues · {b:14.7} Processes · {b:14.9} Asynchronous I/O · {b:14.10} Structured "
            "concurrency with task groups · {b:14.11} Cancellation and timeouts · {b:14.12} Backpressure · "
            "{b:14.13} Choosing a concurrency model · {b:15.16} The GIL and free-threaded internals.")


def build(ch):
    title_page(ch)
    threads_section(ch)
    queue_section(ch)
    pools_section(ch)
    asyncio_section(ch)
    chat_section(ch)
    finish(ch)
