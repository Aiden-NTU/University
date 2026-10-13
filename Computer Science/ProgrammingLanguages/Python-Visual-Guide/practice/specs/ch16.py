EXERCISES = [
    dict(
        id="16.1", kind="fix", title="Make the bank thread-safe (and deadlock-free)",
        task="""
        The `Account` class and `transfer` function lose money when used from several threads, and two
        opposite transfers at the same time can freeze forever. Fix them:
        - `deposit` and `withdraw` must be atomic. `withdraw` raises `ValueError` if the balance is too small,
          and the balance must never go negative, even with many threads withdrawing at once.
        - `transfer(src, dst, amount)` must be atomic too: no other thread may see the money missing from both
          accounts. It must never deadlock, even when `transfer(a, b, …)` and `transfer(b, a, …)` run at the
          same moment.
        Keep the `time.sleep(0)` lines: they stand in for real work (logging, fraud checks) and make the bugs
        show up reliably.
        """,
        stub='''
        import threading, time

        class Account:
            def __init__(self, name, balance=0):
                self.name = name
                self.balance = balance
                self.lock = threading.Lock()

            def deposit(self, amount):
                new = self.balance + amount
                time.sleep(0)                      # e.g. writing an audit log
                self.balance = new

            def withdraw(self, amount):
                if self.balance < amount:
                    raise ValueError("insufficient funds")
                new = self.balance - amount
                time.sleep(0)
                self.balance = new

        def transfer(src, dst, amount):
            with src.lock:
                time.sleep(0)                      # e.g. fraud checks
                with dst.lock:
                    src.withdraw(amount)
                    dst.deposit(amount)
        ''',
        tests='''
        import random, threading, time

        def run_all(fns, timeout=2):
            ts = [threading.Thread(target=f, daemon=True) for f in fns]
            for t in ts: t.start()
            deadline = time.monotonic() + timeout
            for t in ts: t.join(max(0, deadline - time.monotonic()))
            check(not any(t.is_alive() for t in ts), "threads still running after 2 s: probably a deadlock")

        def test_deposits(m):
            acc = m.Account("a")
            run_all([lambda: [acc.deposit(1) for _ in range(500)] for _ in range(8)])
            equal(acc.balance, 4000, "8 threads x 500 deposits")

        def test_withdrawals(m):
            acc = m.Account("a", 100)
            ok, failed = [], []
            def grab():
                try:
                    acc.withdraw(10); ok.append(1)
                except ValueError:
                    failed.append(1)
            run_all([grab for _ in range(20)])
            equal((len(ok), len(failed), acc.balance), (10, 10, 0), "20 withdrawals of 10 from 100")

        def test_transfers(m):
            accs = [m.Account(n, 1000) for n in "abc"]
            rng = random.Random(19)
            plans = [[(rng.sample(accs, 2), rng.randint(1, 5)) for _ in range(200)] for _ in range(6)]
            def run(plan):
                for (src, dst), amt in plan:
                    try:
                        m.transfer(src, dst, amt)
                    except ValueError:
                        pass
            run_all([lambda p=p: run(p) for p in plans])
            equal(sum(a.balance for a in accs), 3000, "money is neither created nor destroyed")
            check(all(a.balance >= 0 for a in accs), "no negative balances")

        def test_opposite_transfers(m):
            a, b = m.Account("a", 10_000), m.Account("b", 10_000)
            run_all([lambda: [m.transfer(a, b, 1) for _ in range(300)],
                     lambda: [m.transfer(b, a, 1) for _ in range(300)]])
            equal((a.balance, b.balance), (10_000, 10_000), "a->b and b->a at the same time")
        ''',
        alts={
            "RLock per account, locks taken in a fixed order": ('''
                import threading, time

                class Account:
                    def __init__(self, name, balance=0):
                        self.name = name
                        self.balance = balance
                        self.lock = threading.RLock()          # re-entrant: transfer holds it, then withdraw takes it again

                    def deposit(self, amount):
                        with self.lock:
                            new = self.balance + amount
                            time.sleep(0)
                            self.balance = new

                    def withdraw(self, amount):
                        with self.lock:
                            if self.balance < amount:
                                raise ValueError("insufficient funds")
                            new = self.balance - amount
                            time.sleep(0)
                            self.balance = new

                def transfer(src, dst, amount):
                    first, second = sorted((src, dst), key=id)  # everyone locks in the same order
                    with first.lock:
                        time.sleep(0)
                        with second.lock:
                            src.withdraw(amount)
                            dst.deposit(amount)
            ''', "Deadlock needs a cycle of waiting. If every thread takes locks in one global order (here by id), "
                 "no cycle can form. RLock lets the same thread re-enter, so withdraw can reuse the held lock."),
            "one lock for the whole bank": ('''
                import threading, time

                BANK = threading.RLock()

                class Account:
                    def __init__(self, name, balance=0):
                        self.name = name
                        self.balance = balance

                    def deposit(self, amount):
                        with BANK:
                            new = self.balance + amount
                            time.sleep(0)
                            self.balance = new

                    def withdraw(self, amount):
                        with BANK:
                            if self.balance < amount:
                                raise ValueError("insufficient funds")
                            new = self.balance - amount
                            time.sleep(0)
                            self.balance = new

                def transfer(src, dst, amount):
                    with BANK:
                        time.sleep(0)
                        src.withdraw(amount)
                        dst.deposit(amount)
            ''', "One lock can't deadlock and is obviously correct, but only one account operation runs at a time. "
                 "Start coarse; split locks only when measurements say contention hurts."),
        },
    ),
    dict(
        id="16.2", kind="build", title="Run jobs concurrently, at most N at a time",
        task="""
        Write `run_limited(fn, items, limit)`. It calls `fn(item)` for every item using threads, with **at
        most** `limit` calls running at once, and returns the results **in input order**. If a call raises,
        put the exception object in its place instead of stopping, so one failure doesn't lose the other
        results.
        """,
        stub='''
        def run_limited(fn, items, limit):
            return [fn(x) for x in items]
        ''',
        tests='''
        import threading, time

        class Probe:
            def __init__(self, delay=0.05):
                self.delay, self.active, self.peak, self.lock = delay, 0, 0, threading.Lock()
            def __call__(self, x):
                with self.lock:
                    self.active += 1
                    self.peak = max(self.peak, self.active)
                time.sleep(self.delay)
                with self.lock:
                    self.active -= 1
                if x == "bad":
                    raise ValueError("bad item")
                return x * 2

        def test_order_and_limit(m):
            p = Probe()
            t0 = time.perf_counter()
            got = m.run_limited(p, list(range(12)), 4)
            took = time.perf_counter() - t0
            equal(got, [x * 2 for x in range(12)], "results in input order")
            equal(p.peak, 4, "exactly 4 at a time at the busiest moment")
            check(took < 0.4, f"12 jobs of 0.05 s, 4 at a time, should take about 0.15 s (took {took:.2f})")

        def test_errors(m):
            got = m.run_limited(Probe(0.01), [1, "bad", 3], 2)
            equal(got[0], 2, "first")
            check(isinstance(got[1], ValueError), "the exception takes the failed item's place")
            equal(got[2], 6, "the rest still run")

        def test_edges(m):
            equal(m.run_limited(Probe(0), [], 3), [], "no items")
            p = Probe(0.01)
            equal(m.run_limited(p, [5, 6], 10), [10, 12], "limit bigger than the work")
            equal(m.run_limited(Probe(0.01), [1, 2, 3], 1), [2, 4, 6], "limit 1 is sequential")
        ''',
        alts={
            "ThreadPoolExecutor": ('''
                from concurrent.futures import ThreadPoolExecutor

                def run_limited(fn, items, limit):
                    def safe(x):
                        try:
                            return fn(x)
                        except Exception as e:
                            return e
                    with ThreadPoolExecutor(max_workers=limit) as pool:
                        return list(pool.map(safe, items))
            ''', "The pool size is the limit, and map keeps input order. Wrapping fn turns exceptions into values; "
                 "otherwise map would re-raise the first one and you'd lose the rest."),
            "a Semaphore and plain threads": ('''
                import threading

                def run_limited(fn, items, limit):
                    gate = threading.Semaphore(limit)           # a counter: at most `limit` inside
                    results = [None] * len(items)

                    def work(i, x):
                        with gate:
                            try:
                                results[i] = fn(x)
                            except Exception as e:
                                results[i] = e

                    threads = [threading.Thread(target=work, args=(i, x)) for i, x in enumerate(items)]
                    for t in threads: t.start()
                    for t in threads: t.join()
                    return results
            ''', "A Semaphore is a lock that lets N holders in at once. One thread per item is wasteful for "
                 "thousands of items (a pool reuses threads), but it shows what the pool does inside."),
        },
    ),
    dict(
        id="16.3", kind="build", title="A concurrent crawler with a work queue",
        task="""
        Write `crawl(start, get_links, workers=4)` returning the set of pages reachable from `start`.
        `get_links(page)` is slow (it waits on the "network") and returns a list of linked pages. Use worker
        threads so up to `workers` pages are fetched at once. Fetch every page **exactly once**. If
        `get_links` raises, the page still counts as reachable but has no links. It must always finish.
        """,
        stub='''
        def crawl(start, get_links, workers=4):
            seen, todo = {start}, [start]
            while todo:
                page = todo.pop()
                for link in get_links(page):
                    if link not in seen:
                        seen.add(link)
                        todo.append(link)
            return seen
        ''',
        tests='''
        import random, threading, time
        from collections import Counter, deque

        def make_web(n, seed, delay=0.02, broken=()):
            rng = random.Random(seed)
            links = {p: rng.sample(range(n), 3) for p in range(n)}
            calls, lock = Counter(), threading.Lock()
            def get_links(page):
                with lock:
                    calls[page] += 1
                time.sleep(delay)
                if page in broken:
                    raise ConnectionError(f"{page} is down")
                return list(links[page])
            return links, get_links, calls

        def reachable(links, start, broken=()):
            seen, q = {start}, deque([start])
            while q:
                p = q.popleft()
                for x in ([] if p in broken else links[p]):
                    if x not in seen:
                        seen.add(x); q.append(x)
            return seen

        def test_correct_and_once(m):
            for seed in range(5):
                links, get, calls = make_web(30, seed, delay=0.001)
                equal(m.crawl(0, get, 4), reachable(links, 0), f"web {seed}: reachable pages")
                check(all(c == 1 for c in calls.values()), "every page fetched exactly once")

        def test_broken_pages(m):
            links, get, calls = make_web(30, 7, delay=0.001, broken={0})
            equal(m.crawl(0, get, 3), {0}, "a broken start page is still reachable, with no links")
            links, get, calls = make_web(30, 8, delay=0.001, broken={5, 9})
            equal(m.crawl(0, get, 3), reachable(links, 0, {5, 9}), "broken pages contribute no links")

        def test_concurrent(m):
            links, get, calls = make_web(60, 11, delay=0.02)
            want = reachable(links, 0)
            t0 = time.perf_counter()
            got = m.crawl(0, get, 6)
            took = time.perf_counter() - t0
            equal(got, want, "result")
            check(took < len(want) * 0.02 / 2, f"{len(want)} pages at 0.02 s each took {took:.2f} s: not concurrent enough")
        ''',
        alts={
            "Queue + task_done/join": ('''
                import queue, threading

                def crawl(start, get_links, workers=4):
                    seen, lock, todo = {start}, threading.Lock(), queue.Queue()
                    todo.put(start)

                    def worker():
                        while True:
                            page = todo.get()
                            try:
                                links = get_links(page)
                            except Exception:
                                links = []
                            with lock:
                                new = [l for l in links if l not in seen]
                                seen.update(new)
                            for l in new:
                                todo.put(l)
                            todo.task_done()                     # after queuing the children

                    for _ in range(workers):
                        threading.Thread(target=worker, daemon=True).start()
                    todo.join()                                  # returns when every put() has a task_done()
                    return seen
            ''', "Termination is the hard part: an empty queue doesn't mean done, since a worker may be about to add "
                 "links. join() waits until every item ever put has been marked done, and children are put first."),
            "level by level with a pool": ('''
                from concurrent.futures import ThreadPoolExecutor

                def crawl(start, get_links, workers=4):
                    def safe(page):
                        try:
                            return get_links(page)
                        except Exception:
                            return []
                    seen, frontier = {start}, [start]
                    with ThreadPoolExecutor(workers) as pool:
                        while frontier:
                            nxt = []
                            for links in pool.map(safe, frontier):
                                for l in links:
                                    if l not in seen:
                                        seen.add(l)
                                        nxt.append(l)
                            frontier = nxt
                    return seen
            ''', "BFS one level at a time: fetch the whole frontier concurrently, then build the next. Only the main "
                 "thread touches seen, so no lock. The cost: each level waits for its slowest page."),
        },
    ),
    dict(
        id="16.4", kind="build", title="asyncio: limited, with a timeout each",
        task="""
        Write `async def fetch_all(names, fetch, limit, timeout)`. `fetch(name)` is a coroutine. Run them
        concurrently, with at most `limit` running at once, each cancelled if it takes longer than `timeout`
        seconds. Return a dict mapping each name to its result, to the string `"timeout"`, or to the exception it
        raised.
        """,
        stub='''
        async def fetch_all(names, fetch, limit, timeout):
            return {n: await fetch(n) for n in names}
        ''',
        tests='''
        import asyncio, time

        DELAYS = {"a": 0.05, "b": 0.05, "c": 0.05, "d": 0.05, "slow": 1.0, "bad": 0.01, "e": 0.05, "f": 0.05}

        def make_fetch():
            state = {"active": 0, "peak": 0, "cancelled": 0}
            async def fetch(name):
                state["active"] += 1
                state["peak"] = max(state["peak"], state["active"])
                try:
                    await asyncio.sleep(DELAYS[name])
                    if name == "bad":
                        raise LookupError("no such page")
                    return name.upper()
                except asyncio.CancelledError:
                    state["cancelled"] += 1
                    raise
                finally:
                    state["active"] -= 1
            return fetch, state

        def test_results(m):
            fetch, state = make_fetch()
            t0 = time.perf_counter()
            got = asyncio.run(m.fetch_all(list(DELAYS), fetch, 3, 0.2))
            took = time.perf_counter() - t0
            equal({k: v for k, v in got.items() if k not in ("bad",)},
                  {"a": "A", "b": "B", "c": "C", "d": "D", "slow": "timeout", "e": "E", "f": "F"}, "results")
            check(isinstance(got["bad"], LookupError), "the exception is returned for 'bad'")
            check(state["peak"] <= 3, f"at most 3 at once (saw {state['peak']})")
            equal(state["cancelled"], 1, "the slow fetch was cancelled")
            check(took < 0.6, f"should take about 0.3 s, took {took:.2f}")

        def test_concurrency_used(m):
            fetch, state = make_fetch()
            names = ["a", "b", "c", "d", "e", "f"]
            t0 = time.perf_counter()
            asyncio.run(m.fetch_all(names, fetch, 6, 1))
            check(time.perf_counter() - t0 < 0.15, "6 fetches of 0.05 s with limit 6 should overlap")
            equal(state["peak"], 6, "all 6 ran at once")
        ''',
        alts={
            "Semaphore + asyncio.timeout + gather": ('''
                import asyncio

                async def fetch_all(names, fetch, limit, timeout):
                    gate = asyncio.Semaphore(limit)

                    async def one(name):
                        async with gate:                         # wait for a free slot first
                            try:
                                async with asyncio.timeout(timeout):
                                    return await fetch(name)
                            except TimeoutError:
                                return "timeout"
                            except Exception as e:
                                return e

                    results = await asyncio.gather(*(one(n) for n in names))
                    return dict(zip(names, results))
            ''', "The timeout starts after the slot is acquired, so queueing time doesn't count against a fetch. "
                 "asyncio.timeout cancels the inner await and turns it into TimeoutError at the block's edge."),
            "TaskGroup + wait_for": ('''
                import asyncio

                async def fetch_all(names, fetch, limit, timeout):
                    gate, out = asyncio.Semaphore(limit), {}

                    async def one(name):
                        async with gate:
                            try:
                                out[name] = await asyncio.wait_for(fetch(name), timeout)
                            except TimeoutError:
                                out[name] = "timeout"
                            except Exception as e:
                                out[name] = e

                    async with asyncio.TaskGroup() as tg:
                        for n in names:
                            tg.create_task(one(n))
                    return {n: out[n] for n in names}
            ''', "wait_for is the older spelling of the same idea. Because one() never raises, the TaskGroup never "
                 "cancels siblings; it's there to guarantee every task finished before we return."),
        },
    ),
    dict(
        id="16.5", kind="explore", title="Debounce with threading.Timer",
        task="""
        Use `threading.Timer` (Ch 7 method: `help(threading.Timer)`) to write a decorator factory
        `debounce(wait)`. The decorated function, when called, doesn't run straight away: it runs **once**,
        `wait` seconds after the **last** call in a burst, with that last call's arguments. Each new call
        restarts the countdown. The wrapper also has a `.cancel()` method that drops a pending call. It must work
        when called from several threads. (Search boxes and autosave use exactly this.)
        """,
        stub='''
        import functools

        def debounce(wait):
            def deco(fn):
                @functools.wraps(fn)
                def wrapper(*args, **kwargs):
                    return fn(*args, **kwargs)
                wrapper.cancel = lambda: None
                return wrapper
            return deco
        ''',
        tests='''
        import threading, time

        def recorder(m, wait=0.05):
            calls = []
            @m.debounce(wait)
            def save(text, *, who="me"):
                calls.append((text, who))
            return save, calls

        def test_burst(m):
            save, calls = recorder(m)
            for i in range(5):
                save(f"draft {i}", who="ana")
                time.sleep(0.01)
            equal(calls, [], "nothing runs during the burst")
            time.sleep(0.12)
            equal(calls, [("draft 4", "ana")], "one call, with the last arguments")

        def test_two_bursts(m):
            save, calls = recorder(m)
            save("a"); time.sleep(0.12)
            save("b"); save("c"); time.sleep(0.12)
            equal(calls, [("a", "me"), ("c", "me")], "two separate bursts")

        def test_cancel(m):
            save, calls = recorder(m)
            save("x")
            save.cancel()
            time.sleep(0.12)
            equal(calls, [], "cancel drops the pending call")
            save.cancel()

        def test_threads(m):
            save, calls = recorder(m, 0.08)
            ts = [threading.Thread(target=lambda i=i: save(i)) for i in range(20)]
            for t in ts: t.start()
            for t in ts: t.join()
            time.sleep(0.2)
            equal(len(calls), 1, "a burst from 20 threads runs once")
        ''',
        alts={
            "Timer, restarted under a lock": ('''
                import functools, threading

                def debounce(wait):
                    def deco(fn):
                        lock, state = threading.Lock(), {"timer": None}

                        @functools.wraps(fn)
                        def wrapper(*args, **kwargs):
                            with lock:
                                if state["timer"]:
                                    state["timer"].cancel()
                                t = threading.Timer(wait, fn, args, kwargs)
                                t.daemon = True
                                state["timer"] = t
                                t.start()

                        def cancel():
                            with lock:
                                if state["timer"]:
                                    state["timer"].cancel()
                                    state["timer"] = None

                        wrapper.cancel = cancel
                        return wrapper
                    return deco
            ''', "A Timer is a thread that sleeps, then calls fn unless cancel() came first. The lock makes 'cancel "
                 "the old timer, start a new one' a single step, so two threads can't both leave timers running."),
            "one worker thread and a Condition": ('''
                import functools, threading, time

                def debounce(wait):
                    def deco(fn):
                        cond = threading.Condition()
                        state = {"due": None, "args": None}

                        def worker():
                            while True:
                                with cond:
                                    while state["due"] is None:
                                        cond.wait()
                                    delay = state["due"] - time.monotonic()
                                    if delay > 0:
                                        cond.wait(delay)
                                        continue
                                    args, kwargs = state["args"]
                                    state["due"] = None
                                fn(*args, **kwargs)

                        threading.Thread(target=worker, daemon=True).start()

                        @functools.wraps(fn)
                        def wrapper(*args, **kwargs):
                            with cond:
                                state["due"], state["args"] = time.monotonic() + wait, (args, kwargs)
                                cond.notify()

                        def cancel():
                            with cond:
                                state["due"] = None
                                cond.notify()

                        wrapper.cancel = cancel
                        return wrapper
                    return deco
            ''', "One long-lived thread instead of a new Timer per call. A Condition lets it sleep until either the "
                 "deadline passes or a new call moves it. monotonic() (Ch 11) because deadlines must not jump."),
        },
    ),
    dict(
        id="16.6", kind="project", title="An asyncio chat server with nicknames",
        task="""
        Mini-project (builds on Ch 15's framing). Write `async def start_chat(port=0)` that returns a started
        `asyncio.Server` on 127.0.0.1. Lines are UTF-8 and end with `\\n`.
        - On connect the server sends `NAME?`. The client answers with a nickname. If it's empty or already
          taken, the server sends `NAME TAKEN` and then `NAME?` again.
        - Then the client gets `WELCOME <nick>`, and everyone else gets `* <nick> joined`.
        - Any other line `text` goes to everyone **else** as `<nick>: text`.
        - `/who` sends back `USERS <nicks sorted, space-separated>`, to the sender only.
        - `/quit`, or disconnecting, tells the others `* <nick> left`.
        """,
        stub='''
        import asyncio

        async def start_chat(port=0):
            async def handle(reader, writer):
                while line := await reader.readline():
                    writer.write(line)
            return await asyncio.start_server(handle, "127.0.0.1", port)
        ''',
        tests='''
        import asyncio

        class Client:
            @classmethod
            async def join(cls, port, nick, expect_ok=True):
                c = cls()
                c.r, c.w = await asyncio.open_connection("127.0.0.1", port)
                equal(await c.line(), "NAME?", "server asks for a name first")
                c.w.write(nick.encode() + b"\\n")
                if expect_ok:
                    equal(await c.line(), f"WELCOME {nick}", "welcome")
                return c

            async def line(self):
                raw = await asyncio.wait_for(self.r.readline(), 2)
                return raw.decode().rstrip("\\n")

            def say(self, text):
                self.w.write(text.encode() + b"\\n")

        def chat(m, scenario):
            async def main():
                server = await m.start_chat(0)
                port = server.sockets[0].getsockname()[1]
                try:
                    await scenario(port)
                finally:
                    server.close()
            asyncio.run(main())

        def test_conversation(m):
            async def scenario(port):
                ana = await Client.join(port, "ana")
                ben = await Client.join(port, "ben")
                equal(await ana.line(), "* ben joined", "others hear about a join")
                ana.say("hello ben")
                equal(await ben.line(), "ana: hello ben", "message to others, with nick")
                ben.say("/who")
                equal(await ben.line(), "USERS ana ben", "/who to the sender only")
                cy = await Client.join(port, "cy")
                equal([await ana.line(), await ben.line()], ["* cy joined"] * 2, "both hear cy")
                ben.say("/quit")
                equal([await ana.line(), await cy.line()], ["* ben left"] * 2, "/quit announces leaving")
                cy.w.close()
                equal(await ana.line(), "* cy left", "disconnecting announces leaving too")
                ana.say("anyone?")
                ana.say("/who")
                equal(await ana.line(), "USERS ana", "sender doesn't get its own message back")
                ana.w.close()
            chat(m, scenario)

        def test_names(m):
            async def scenario(port):
                ana = await Client.join(port, "ana")
                dup = await Client.join(port, "ana", expect_ok=False)
                equal([await dup.line(), await dup.line()], ["NAME TAKEN", "NAME?"], "a taken name is refused")
                dup.say("")
                equal([await dup.line(), await dup.line()], ["NAME TAKEN", "NAME?"], "an empty name is refused")
                dup.say("ana2")
                equal(await dup.line(), "WELCOME ana2", "then a free name works")
                equal(await ana.line(), "* ana2 joined", "and others hear it")
                ana.w.close(); dup.w.close()
            chat(m, scenario)
        ''',
        alts={
            "a dict of writers by nick": ('''
                import asyncio

                async def start_chat(port=0):
                    users = {}                                    # nick -> writer

                    async def send(writer, text):
                        writer.write(text.encode() + b"\\n")
                        await writer.drain()

                    async def broadcast(text, skip=None):
                        for nick, w in list(users.items()):
                            if nick != skip:
                                try:
                                    await send(w, text)
                                except ConnectionError:
                                    pass

                    async def ask_name(reader, writer):
                        while True:
                            await send(writer, "NAME?")
                            raw = await reader.readline()
                            if not raw:
                                return None
                            nick = raw.decode().strip()
                            if nick and nick not in users:
                                return nick
                            await send(writer, "NAME TAKEN")

                    async def handle(reader, writer):
                        nick = await ask_name(reader, writer)
                        if nick is None:
                            writer.close()
                            return
                        users[nick] = writer
                        await send(writer, f"WELCOME {nick}")
                        await broadcast(f"* {nick} joined", skip=nick)
                        try:
                            while raw := await reader.readline():
                                text = raw.decode().rstrip("\\n")
                                if text == "/quit":
                                    break
                                if text == "/who":
                                    await send(writer, " ".join(["USERS", *sorted(users)]))
                                else:
                                    await broadcast(f"{nick}: {text}", skip=nick)
                        except ConnectionError:
                            pass
                        finally:
                            del users[nick]
                            await broadcast(f"* {nick} left")
                            writer.close()

                    return await asyncio.start_server(handle, "127.0.0.1", port)
            ''', "No locks needed: asyncio only switches at await, and checking a name then claiming it happens with "
                 "no await in between. With threads, that check-then-act would be a race (Ch 16)."),
            "a Room class with a queue per client": ('''
                import asyncio

                class Room:
                    def __init__(self):
                        self.members = {}                         # nick -> asyncio.Queue of outgoing lines

                    def post(self, text, skip=None):
                        for nick, q in self.members.items():
                            if nick != skip:
                                q.put_nowait(text)

                async def start_chat(port=0):
                    room = Room()

                    async def pump(q, writer):                    # one sender per client: slow clients don't block others
                        while True:
                            writer.write((await q.get()).encode() + b"\\n")
                            await writer.drain()

                    async def handle(reader, writer):
                        q = asyncio.Queue()
                        sender = asyncio.create_task(pump(q, writer))
                        nick = None
                        try:
                            while nick is None:
                                q.put_nowait("NAME?")
                                raw = await reader.readline()
                                if not raw:
                                    return
                                name = raw.decode().strip()
                                if name and name not in room.members:
                                    nick = name
                                else:
                                    q.put_nowait("NAME TAKEN")
                            room.members[nick] = q
                            q.put_nowait(f"WELCOME {nick}")
                            room.post(f"* {nick} joined", skip=nick)
                            while raw := await reader.readline():
                                text = raw.decode().rstrip("\\n")
                                if text == "/quit":
                                    break
                                if text == "/who":
                                    q.put_nowait("USERS " + " ".join(sorted(room.members)))
                                else:
                                    room.post(f"{nick}: {text}", skip=nick)
                        finally:
                            if nick is not None:
                                del room.members[nick]
                                room.post(f"* {nick} left")
                            await asyncio.sleep(0.01)             # let the pump flush
                            sender.cancel()
                            writer.close()

                    return await asyncio.start_server(handle, "127.0.0.1", port)
            ''', "Broadcasting by awaiting each writer means one stuck client stalls everyone. Giving each client an "
                 "outgoing queue and its own pump task isolates them: the same backpressure idea as Ch 16's queues."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="import asyncio\nasync def f(x, d):\n    await asyncio.sleep(d)\n    return x\nasync def main():\n    print(await asyncio.gather(f('slow', 0.02), f('fast', 0.01)))\nasyncio.run(main())", why="gather returns results in argument order, not finishing order."),
    dict(kind="predict", code="import queue\nq = queue.Queue()\nfor x in 'abc':\n    q.put(x)\nprint(q.get(), q.qsize())"),
    dict(kind="predict", code="import queue\nq = queue.LifoQueue()\nfor x in 'abc':\n    q.put(x)\nprint(q.get())"),
    dict(kind="predict", code="import threading\nresult = []\nt = threading.Thread(target=result.append, args=(42,))\nt.start(); t.join()\nprint(result)"),
    dict(kind="predict", code="import asyncio\nasync def f():\n    return 1\nc = f()\nprint(type(c).__name__)\nc.close()", why="Calling an async function only creates a coroutine object; nothing runs until it's awaited."),
    dict(kind="recall", q="What CPython mechanism stops two threads running Python bytecode at the same time?", a=["GIL", "the GIL", "global interpreter lock"]),
    dict(kind="recall", q="Which executor should you use for CPU-bound pure-Python work: threads or processes?", a=["processes", "ProcessPoolExecutor", "process"]),
    dict(kind="recall", q="Which function runs a blocking call in a thread from async code?", a=["asyncio.to_thread", "to_thread"]),
]
