EXERCISES = [
    dict(
        id="15.1", kind="build", title="Length-prefixed messages over TCP",
        task="""
        TCP is a byte stream, so messages need framing. Write:
        - `recv_exactly(sock, n)`: keep calling `recv` until exactly `n` bytes have arrived, and return them.
          If the peer closes first, raise `ConnectionError`.
        - `send_msg(sock, data)`: send a 4-byte big-endian length (`struct.pack("!I", len(data))`), then the data.
        - `recv_msg(sock)`: the matching receive. Return `None` if the peer closed cleanly **before** a new
          message started.
        """,
        stub='''
        import struct

        def recv_exactly(sock, n):
            return sock.recv(n)

        def send_msg(sock, data):
            sock.sendall(struct.pack("!I", len(data)) + data)

        def recv_msg(sock):
            (n,) = struct.unpack("!I", sock.recv(4))
            return sock.recv(n)
        ''',
        tests='''
        import random, socket, struct, threading, time

        def dribble(sock, data, rng):
            """Send in tiny pieces with pauses, like a slow network would."""
            i = 0
            while i < len(data):
                k = rng.randint(1, 7)
                sock.sendall(data[i:i + k])
                i += k
                time.sleep(0.0003)

        def test_round_trip(m):
            a, b = socket.socketpair()
            with a, b:
                for data in [b"", b"x", b"hello", bytes(range(256)) * 300]:
                    m.send_msg(a, data)
                    equal(m.recv_msg(b), data, f"message of {len(data)} bytes")

        def test_slow_network(m):
            rng = random.Random(18)
            msgs = [bytes(rng.randrange(256) for _ in range(rng.randint(0, 60))) for _ in range(30)]
            a, b = socket.socketpair()
            with a, b:
                stream = b"".join(struct.pack("!I", len(x)) + x for x in msgs)
                t = threading.Thread(target=dribble, args=(a, stream, rng))
                t.start()
                got = [m.recv_msg(b) for _ in msgs]
                t.join()
            equal(got, msgs, "messages sent in tiny pieces")

        def test_closing(m):
            a, b = socket.socketpair()
            m.send_msg(a, b"last")
            a.close()
            equal(m.recv_msg(b), b"last", "message before close")
            equal(m.recv_msg(b), None, "clean close between messages gives None")
            b.close()
            a, b = socket.socketpair()
            a.sendall(struct.pack("!I", 10) + b"abc")
            a.close()
            raises(ConnectionError, m.recv_msg, b)
            b.close()
        ''',
        alts={
            "loop with a bytearray": ('''
                import struct

                def recv_exactly(sock, n):
                    buf = bytearray()
                    while len(buf) < n:
                        chunk = sock.recv(n - len(buf))
                        if not chunk:
                            raise ConnectionError(f"peer closed after {len(buf)} of {n} bytes")
                        buf += chunk
                    return bytes(buf)

                def send_msg(sock, data):
                    sock.sendall(struct.pack("!I", len(data)) + data)

                def recv_msg(sock):
                    first = sock.recv(1)
                    if not first:
                        return None
                    (n,) = struct.unpack("!I", first + recv_exactly(sock, 3))
                    return recv_exactly(sock, n)
            ''', "recv(n) means 'up to n'. The loop asks only for what's still missing; reading the first byte "
                 "separately tells a clean close (nothing at all) from a broken message."),
            "MSG_WAITALL / recv_into": ('''
                import socket, struct

                def recv_exactly(sock, n):
                    buf = memoryview(bytearray(n))
                    got = 0
                    while got < n:
                        k = sock.recv_into(buf[got:], n - got)
                        if k == 0:
                            raise ConnectionError("peer closed mid-message")
                        got += k
                    return bytes(buf)

                def send_msg(sock, data):
                    sock.sendall(struct.pack("!I", len(data)) + data)

                def recv_msg(sock):
                    head = sock.recv(4, socket.MSG_WAITALL)
                    if not head:
                        return None
                    if len(head) < 4:
                        head += recv_exactly(sock, 4 - len(head))
                    return recv_exactly(sock, struct.unpack("!I", head)[0])
            ''', "recv_into fills a preallocated buffer without creating a bytes object per chunk, which matters "
                 "at high data rates. MSG_WAITALL asks the OS to wait for the full amount (POSIX only)."),
        },
    ),
    dict(
        id="15.2", kind="fix", title="Parse a raw HTTP request properly",
        task="""
        `parse_request(raw)` takes the raw bytes of one HTTP request and returns
        `(method, path, headers, body)`. `headers` is a dict with **lower-case** names (HTTP header names are
        case-insensitive), and `body` is exactly `Content-Length` bytes (`b""` if there is no such header).
        Lines end with `\\r\\n`, and the headers end at the first empty line. The stub splits on `\\n` (leaving
        `\\r` behind), keeps header case, and ignores Content-Length. Fix it. Raise `ValueError` for a
        malformed request line or a body shorter than Content-Length.
        """,
        stub='''
        def parse_request(raw):
            text = raw.decode()
            lines = text.split("\\n")
            method, path, version = lines[0].split(" ")
            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    k, v = line.split(":")
                    headers[k] = v
            body = text.split("\\n\\n")[-1].encode()
            return method, path, headers, body
        ''',
        tests='''
        def test_get(m):
            raw = b"GET /books?q=dune HTTP/1.1\\r\\nHost: lib.example.org\\r\\nAccept: */*\\r\\n\\r\\n"
            equal(m.parse_request(raw), ("GET", "/books?q=dune", {"host": "lib.example.org", "accept": "*/*"}, b""), "GET")

        def test_post(m):
            body = b'{"title": "Ubik: a novel"}'
            raw = (b"POST /books HTTP/1.1\\r\\nHOST: x\\r\\ncontent-TYPE: application/json\\r\\n"
                   b"Content-Length: " + str(len(body)).encode() + b"\\r\\nX-Note: a: b\\r\\n\\r\\n" + body + b"EXTRA")
            method, path, headers, got = m.parse_request(raw)
            equal((method, path), ("POST", "/books"), "request line")
            equal(headers, {"host": "x", "content-type": "application/json", "content-length": str(len(body)),
                            "x-note": "a: b"}, "headers: lower-case names, values stripped, ':' allowed in values")
            equal(got, body, "body is exactly Content-Length bytes")

        def test_binary_body(m):
            body = bytes(range(256)) + b"\\r\\n\\r\\n" + bytes(10)
            raw = b"PUT /f HTTP/1.1\\r\\nContent-Length: " + str(len(body)).encode() + b"\\r\\n\\r\\n" + body
            equal(m.parse_request(raw)[3], body, "binary body (may contain \\\\r\\\\n\\\\r\\\\n)")

        def test_bad(m):
            raises(ValueError, m.parse_request, b"GARBAGE\\r\\n\\r\\n")
            raises(ValueError, m.parse_request, b"POST /x HTTP/1.1\\r\\nContent-Length: 10\\r\\n\\r\\nshort")
        ''',
        alts={
            "split head from body as bytes": ('''
                def parse_request(raw):
                    head, sep, rest = raw.partition(b"\\r\\n\\r\\n")
                    if not sep:
                        raise ValueError("no blank line after the headers")
                    lines = head.decode("iso-8859-1").split("\\r\\n")
                    parts = lines[0].split(" ")
                    if len(parts) != 3 or not parts[2].startswith("HTTP/"):
                        raise ValueError(f"bad request line: {lines[0]!r}")
                    method, path, _ = parts
                    headers = {}
                    for line in lines[1:]:
                        name, colon, value = line.partition(":")
                        if not colon:
                            raise ValueError(f"bad header line: {line!r}")
                        headers[name.strip().lower()] = value.strip()
                    n = int(headers.get("content-length", 0))
                    if len(rest) < n:
                        raise ValueError(f"body is {len(rest)} bytes, expected {n}")
                    return method, path, headers, rest[:n]
            ''', "Split on the first blank line while still in bytes: the body may not be text. partition(':') "
                 "splits once, so values can contain colons. Headers are ISO-8859-1 by the HTTP spec."),
            "email.parser for the headers": ('''
                from email.parser import BytesHeaderParser

                def parse_request(raw):
                    head, sep, rest = raw.partition(b"\\r\\n\\r\\n")
                    line, _, header_block = head.partition(b"\\r\\n")
                    parts = line.decode("ascii", "replace").split()
                    if not sep or len(parts) != 3:
                        raise ValueError("malformed request")
                    msg = BytesHeaderParser().parsebytes(header_block + b"\\r\\n\\r\\n")
                    headers = {k.lower(): v.strip() for k, v in msg.items()}
                    n = int(headers.get("content-length", 0))
                    if len(rest) < n:
                        raise ValueError("truncated body")
                    return parts[0], parts[1], headers, rest[:n]
            ''', "HTTP headers use the same format as email headers (RFC 822), and http.server really does parse "
                 "them with the email package. Reuse beats re-invention, once you know it's there."),
        },
    ),
    dict(
        id="15.3", kind="explore", title="URL surgery with urllib.parse",
        task="""
        Use `urllib.parse` (Ch 7 method) to write:
        - `add_params(url, **params)`: return the URL with these query parameters added, or replacing
          parameters of the same name. Keep the other parameters (in order), the fragment and everything else;
          encode values properly (spaces, `&`, unicode).
        - `same_origin(a, b)`: True if two URLs have the same scheme, host (case-insensitive) and port, where a
          missing port means 80 for http and 443 for https.
        """,
        stub='''
        def add_params(url, **params):
            return url + "?" + "&".join(f"{k}={v}" for k, v in params.items())

        def same_origin(a, b):
            return a.split("/")[2] == b.split("/")[2]
        ''',
        tests='''
        from urllib.parse import parse_qsl, urlsplit

        def test_add_params(m):
            equal(m.add_params("https://x.org/s", q="dune"), "https://x.org/s?q=dune", "simple")
            u = m.add_params("https://x.org/s?page=2&q=old#top", q="science fiction & more", lang="en")
            p = urlsplit(u)
            equal((p.scheme, p.netloc, p.path, p.fragment), ("https", "x.org", "/s", "top"), "rest of the URL kept")
            equal(parse_qsl(p.query), [("page", "2"), ("q", "science fiction & more"), ("lang", "en")],
                  "replaced in place, new ones appended, values encoded")
            u = m.add_params("http://x.org/", name="Zoë")
            check("Zo%C3%AB" in u, f"unicode must be percent-encoded as UTF-8: {u}")
            equal(parse_qsl(urlsplit(m.add_params("http://x.org/?a=1&a=2", b=3)).query), [("a", "1"), ("a", "2"), ("b", "3")],
                  "repeated parameters not touched are kept")

        def test_same_origin(m):
            yes = [("https://x.org/a", "https://X.ORG:443/b?c"), ("http://x.org", "http://x.org:80/"),
                   ("http://a.b:8080/x", "http://a.b:8080/y")]
            no = [("https://x.org", "http://x.org"), ("https://x.org", "https://x.org:8443"),
                  ("https://x.org", "https://www.x.org"), ("http://a.b:8080", "http://a.b")]
            for a, b in yes:
                equal(m.same_origin(a, b), True, f"{a} vs {b}")
            for a, b in no:
                equal(m.same_origin(a, b), False, f"{a} vs {b}")
        ''',
        alts={
            "split, edit, unsplit": ('''
                from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

                DEFAULT_PORTS = {"http": 80, "https": 443}

                def add_params(url, **params):
                    parts = urlsplit(url)
                    placed, out = set(), []
                    for k, v in parse_qsl(parts.query, keep_blank_values=True):
                        if k in params:
                            if k not in placed:
                                out.append((k, str(params[k])))
                                placed.add(k)
                        else:
                            out.append((k, v))
                    out += [(k, str(v)) for k, v in params.items() if k not in placed]
                    return urlunsplit(parts._replace(query=urlencode(out)))

                def origin(url):
                    p = urlsplit(url)
                    return p.scheme, (p.hostname or "").lower(), p.port or DEFAULT_PORTS.get(p.scheme)

                def same_origin(a, b):
                    return origin(a) == origin(b)
            ''', "urlsplit returns a named tuple, so ._replace(query=...) changes one part and urlunsplit "
                 "rebuilds the rest unchanged. .hostname is already lower-cased; .port is None when absent."),
            "dict for the query": ('''
                from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

                def add_params(url, **params):
                    parts = urlsplit(url)
                    pairs = parse_qsl(parts.query, keep_blank_values=True)
                    seen, out = set(), []
                    for k, v in pairs:
                        if k in params:
                            if k in seen:
                                continue
                            seen.add(k)
                            v = params[k]
                        out.append((k, v))
                    out.extend((k, v) for k, v in params.items() if k not in seen)
                    return urlunsplit(parts._replace(query=urlencode(out)))

                def same_origin(a, b):
                    def key(u):
                        p = urlsplit(u)
                        return (p.scheme, p.hostname, p.port or {"http": 80, "https": 443}.get(p.scheme))
                    return key(a) == key(b)
            ''', "Same tools, tighter. Note the stub's two bugs: it ignored existing queries and fragments, and "
                 "it didn't encode, so a value containing & silently became two parameters."),
        },
    ),
    dict(
        id="15.4", kind="build", title="A JSON API client that handles failure",
        task="""
        Write `fetch_json(url, timeout=5)` with `urllib.request`. It returns the parsed JSON of a 2xx response.
        Every failure raises `ApiError` (define it) with attributes `status` and `message`:
        - an HTTP error status: `status` is the code; `message` is the body's `"error"` field if the body is
          JSON with one, otherwise the reason phrase;
        - a 2xx body that isn't valid JSON: `status` is the code and `message` mentions JSON;
        - a connection failure or timeout: `status` is `None`.
        """,
        stub='''
        import json, urllib.request

        def fetch_json(url, timeout=5):
            return json.loads(urllib.request.urlopen(url).read())
        ''',
        tests='''
        import json, socket, threading, time
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        class H(BaseHTTPRequestHandler):
            def reply(self, status, body, ctype="application/json"):
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                routes = {
                    "/ok": (200, b'{"a": [1, 2]}'),
                    "/missing": (404, b'{"error": "no such book"}'),
                    "/boom": (500, b"<html>oops</html>"),
                    "/notjson": (200, b"<html>hi</html>"),
                }
                if self.path == "/slow":
                    time.sleep(1.5)
                    try:
                        self.reply(200, b"{}")
                    except OSError:
                        pass                     # the client gave up first, as it should
                    return
                self.reply(*routes.get(self.path, (404, b"")))

            def log_message(self, *a):
                pass

        def serve():
            s = ThreadingHTTPServer(("127.0.0.1", 0), H)
            s.daemon_threads = True
            threading.Thread(target=s.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
            return s, f"http://127.0.0.1:{s.server_port}"

        def api_error(m, url, **kw):
            try:
                m.fetch_json(url, **kw)
            except m.ApiError as e:
                return e
            check(False, f"{url} should raise ApiError")

        def test_ok_and_errors(m):
            s, base = serve()
            try:
                equal(m.fetch_json(base + "/ok"), {"a": [1, 2]}, "200 with JSON")
                e = api_error(m, base + "/missing")
                equal((e.status, e.message), (404, "no such book"), "404 with a JSON error body")
                e = api_error(m, base + "/boom")
                equal((e.status, e.message), (500, "Internal Server Error"), "500 with an HTML body: reason phrase")
                e = api_error(m, base + "/notjson")
                check(e.status == 200 and "json" in e.message.lower(), "a 200 that isn't JSON")
                t0 = time.perf_counter()
                e = api_error(m, base + "/slow", timeout=0.3)
                check(e.status is None and time.perf_counter() - t0 < 1.2, "timeout gives status None, promptly")
            finally:
                s.shutdown()
                s.server_close()

        def test_refused(m):
            sock = socket.socket()
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            sock.close()
            e = api_error(m, f"http://127.0.0.1:{port}/", timeout=2)
            equal(e.status, None, "connection refused")
        ''',
        alts={
            "except in order: HTTPError, then URLError": ('''
                import json, socket, urllib.error, urllib.request

                class ApiError(Exception):
                    def __init__(self, status, message):
                        super().__init__(f"{status}: {message}")
                        self.status, self.message = status, message

                def fetch_json(url, timeout=5):
                    try:
                        with urllib.request.urlopen(url, timeout=timeout) as resp:
                            status, raw = resp.status, resp.read()
                    except urllib.error.HTTPError as e:                # a subclass of URLError: catch it first
                        try:
                            message = json.loads(e.read())["error"]
                        except (ValueError, KeyError, TypeError):
                            message = e.reason
                        raise ApiError(e.code, message) from None
                    except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError) as e:
                        raise ApiError(None, str(getattr(e, "reason", e))) from None
                    try:
                        return json.loads(raw)
                    except ValueError:
                        raise ApiError(status, "response was not valid JSON") from None
            ''', "HTTPError is-a URLError, so order matters. A timeout can surface as URLError(reason=timeout) or "
                 "a bare TimeoutError depending on where it hits; catching both is what real clients do."),
            "http.client, one level down": ('''
                import http.client, json
                from urllib.parse import urlsplit

                class ApiError(Exception):
                    def __init__(self, status, message):
                        super().__init__(message)
                        self.status, self.message = status, message

                def fetch_json(url, timeout=5):
                    u = urlsplit(url)
                    cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
                    conn = cls(u.hostname, u.port, timeout=timeout)
                    try:
                        conn.request("GET", (u.path or "/") + (f"?{u.query}" if u.query else ""))
                        resp = conn.getresponse()
                        raw = resp.read()
                    except OSError as e:                                # refused, reset, timed out
                        raise ApiError(None, str(e)) from None
                    finally:
                        conn.close()
                    try:
                        data = json.loads(raw)
                    except ValueError:
                        data = None
                    if not 200 <= resp.status < 300:
                        msg = data.get("error") if isinstance(data, dict) else None
                        raise ApiError(resp.status, msg or resp.reason)
                    if data is None and raw.strip() != b"null":
                        raise ApiError(resp.status, "body is not JSON")
                    return data
            ''', "http.client never raises for a status code: you check resp.status yourself. Every network "
                 "failure is an OSError subclass, so one except covers refused, reset and timeout."),
        },
    ),
    dict(
        id="15.5", kind="build", title="Serve a small JSON API",
        task="""
        Write `make_server(port=0)` returning a **not yet started** `http.server.ThreadingHTTPServer` on
        127.0.0.1 that serves a books API from its own in-memory store (two servers must not share books).
        Every response with a body is JSON with `Content-Type: application/json`.
        - `GET /books` gives 200 and a list of `{"id", "title"}`, sorted by id.
        - `GET /books/<id>` gives 200 and the book, or 404 `{"error": ...}`.
        - `POST /books` with body `{"title": "..."}` (a non-empty string) gives 201, the new book, and a
          `Location: /books/<id>` header. Ids start at 1. Bad JSON or a bad title gives 400 `{"error": ...}`.
        - `DELETE /books/<id>` gives 204 with no body, or 404.
        - Any other path gives 404.
        """,
        stub='''
        import json
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = json.dumps([]).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

        def make_server(port=0):
            return ThreadingHTTPServer(("127.0.0.1", port), Handler)
        ''',
        tests='''
        import http.client, json, threading

        class Client:
            def __init__(self, m):
                self.server = m.make_server(0)
                self.server.daemon_threads = True
                threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

            def __call__(self, method, path, body=None):
                conn = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=2)
                data = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
                headers = {"Content-Type": "application/json"} if data is not None else {}
                conn.request(method, path, body=data, headers=headers)
                r = conn.getresponse()
                raw = r.read()
                conn.close()
                parsed = json.loads(raw) if raw else None
                if raw:
                    check(r.getheader("Content-Type", "").startswith("application/json"), f"{method} {path}: JSON content type")
                return r.status, parsed, r

            def close(self):
                self.server.shutdown()
                self.server.server_close()

        def test_crud(m):
            c = Client(m)
            try:
                equal(c("GET", "/books")[:2], (200, []), "empty list")
                st, book, r = c("POST", "/books", {"title": "Dune"})
                equal((st, book), (201, {"id": 1, "title": "Dune"}), "create")
                equal(r.getheader("Location"), "/books/1", "Location header")
                c("POST", "/books", {"title": "Emma"})
                equal(c("GET", "/books")[:2], (200, [{"id": 1, "title": "Dune"}, {"id": 2, "title": "Emma"}]), "list")
                equal(c("GET", "/books/2")[:2], (200, {"id": 2, "title": "Emma"}), "get one")
                st, body, _ = c("GET", "/books/9")
                check(st == 404 and "error" in body, "missing book: 404 with an error")
                st, body, _ = c("DELETE", "/books/1")
                equal((st, body), (204, None), "delete: 204, no body")
                equal(c("DELETE", "/books/1")[0], 404, "delete again: 404")
                equal(c("GET", "/books")[:2], (200, [{"id": 2, "title": "Emma"}]), "after delete")
                equal(c("GET", "/nothing")[0], 404, "unknown path")
            finally:
                c.close()

        def test_bad_input(m):
            c = Client(m)
            try:
                for body in [b"{not json", {"name": "x"}, {"title": ""}, {"title": 5}, [1]]:
                    st, err, _ = c("POST", "/books", body)
                    check(st == 400 and isinstance(err, dict) and "error" in err, f"POST {body!r} should be 400")
                equal(c("GET", "/books")[:2], (200, []), "bad posts create nothing")
            finally:
                c.close()

        def test_separate_stores(m):
            a, b = Client(m), Client(m)
            try:
                a("POST", "/books", {"title": "Dune"})
                equal(b("GET", "/books")[:2], (200, []), "each server has its own books")
            finally:
                a.close(); b.close()
        ''',
        alts={
            "handler class made per server": ('''
                import json, re, threading
                from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

                def make_server(port=0):
                    books, lock = {}, threading.Lock()
                    next_id = [1]

                    class Handler(BaseHTTPRequestHandler):
                        def send_json(self, status, obj=None, **headers):
                            body = b"" if obj is None else json.dumps(obj).encode()
                            self.send_response(status)
                            if obj is not None:
                                self.send_header("Content-Type", "application/json")
                            self.send_header("Content-Length", str(len(body)))
                            for k, v in headers.items():
                                self.send_header(k, v)
                            self.end_headers()
                            self.wfile.write(body)

                        def book_id(self):
                            mt = re.fullmatch(r"/books/(\\d+)", self.path)
                            return int(mt[1]) if mt else None

                        def do_GET(self):
                            with lock:
                                if self.path == "/books":
                                    return self.send_json(200, [books[k] for k in sorted(books)])
                                if (i := self.book_id()) in books:
                                    return self.send_json(200, books[i])
                            self.send_json(404, {"error": "not found"})

                        def do_POST(self):
                            if self.path != "/books":
                                return self.send_json(404, {"error": "not found"})
                            try:
                                data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                                title = data["title"]
                                if not isinstance(title, str) or not title.strip():
                                    raise ValueError
                            except (ValueError, KeyError, TypeError):
                                return self.send_json(400, {"error": 'expected {"title": "non-empty string"}'})
                            with lock:
                                book = {"id": next_id[0], "title": title}
                                books[book["id"]] = book
                                next_id[0] += 1
                            self.send_json(201, book, Location=f"/books/{book['id']}")

                        def do_DELETE(self):
                            with lock:
                                found = books.pop(self.book_id(), None)
                            if found is None:
                                return self.send_json(404, {"error": "not found"})
                            self.send_json(204)

                        def log_message(self, *a):
                            pass

                    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
            ''', "Defining the handler class inside make_server gives each server its own closure over books "
                 "and a lock: ThreadingHTTPServer runs requests concurrently (Ch 16 explains why the lock matters)."),
            "store on the server object": ('''
                import json, threading
                from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

                class BookServer(ThreadingHTTPServer):
                    def __init__(self, addr, handler):
                        super().__init__(addr, handler)
                        self.books, self.next_id, self.lock = {}, 1, threading.Lock()

                class Handler(BaseHTTPRequestHandler):
                    def out(self, status, obj=None, location=None):
                        body = b"" if obj is None else json.dumps(obj).encode()
                        self.send_response(status)
                        if body:
                            self.send_header("Content-Type", "application/json")
                        if location:
                            self.send_header("Location", location)
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)

                    def target(self):
                        head, _, tail = self.path.rpartition("/")
                        return int(tail) if head == "/books" and tail.isdigit() else None

                    def do_GET(self):
                        s = self.server
                        with s.lock:
                            if self.path == "/books":
                                return self.out(200, sorted(s.books.values(), key=lambda b: b["id"]))
                            book = s.books.get(self.target())
                        self.out(200, book) if book else self.out(404, {"error": "no such book"})

                    def do_POST(self):
                        s = self.server
                        if self.path != "/books":
                            return self.out(404, {"error": "no such resource"})
                        try:
                            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                            ok = isinstance(data, dict) and isinstance(data.get("title"), str) and data["title"]
                        except ValueError:
                            ok = False
                        if not ok:
                            return self.out(400, {"error": "need a non-empty title"})
                        with s.lock:
                            book = {"id": s.next_id, "title": data["title"]}
                            s.books[s.next_id] = book
                            s.next_id += 1
                        self.out(201, book, location=f"/books/{book['id']}")

                    def do_DELETE(self):
                        s = self.server
                        with s.lock:
                            gone = s.books.pop(self.target(), None)
                        self.out(204) if gone else self.out(404, {"error": "no such book"})

                    def log_message(self, *a):
                        pass

                def make_server(port=0):
                    return BookServer(("127.0.0.1", port), Handler)
            ''', "Every handler can reach self.server, so a server subclass is a natural home for shared state. "
                 "Frameworks formalise this as the 'application' object."),
        },
    ),
    dict(
        id="15.6", kind="project", title="A line-based key-value server",
        task="""
        Mini-project. Write `make_server(port=0)` returning a **not yet started**
        `socketserver.ThreadingTCPServer` on 127.0.0.1 for a tiny Redis-like protocol. Each request is one
        UTF-8 line ending in `\\n`, and each gets one reply line:
        `SET key value...` gives `OK` (the value is the rest of the line, spaces allowed);
        `GET key` gives `VALUE <value>` or `NOT_FOUND`; `DEL key` gives `OK` or `NOT_FOUND`;
        `KEYS` gives `KEYS k1 k2 ...` sorted (just `KEYS` if empty); `QUIT` gives `BYE` and closes; anything
        else gives `ERR unknown command`. All clients share one store, so make it thread-safe. Clients may send
        several commands in one packet, or one command split across packets.
        """,
        stub='''
        import socketserver

        STORE = {}

        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                while data := self.request.recv(1024):
                    cmd, *args = data.decode().split()
                    if cmd == "SET":
                        STORE[args[0]] = args[1]
                        self.request.sendall(b"OK\\n")
                    elif cmd == "GET":
                        self.request.sendall(f"VALUE {STORE[args[0]]}\\n".encode())

        def make_server(port=0):
            return socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
        ''',
        tests='''
        import socket, threading, time

        class Conn:
            def __init__(self, port):
                self.s = socket.create_connection(("127.0.0.1", port), timeout=1.5)
                self.r = self.s.makefile("r", encoding="utf-8")

            def ask(self, *lines):
                self.s.sendall("".join(l + "\\n" for l in lines).encode())
                return [self.r.readline().rstrip("\\n") for _ in lines]

            def close(self):
                self.r.close(); self.s.close()

        def running(m):
            srv = m.make_server(0)
            srv.daemon_threads = True
            threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
            return srv, srv.server_address[1]

        def stop(srv):
            srv.shutdown(); srv.server_close()

        def test_commands(m):
            srv, port = running(m)
            c = Conn(port)
            try:
                equal(c.ask("GET a"), ["NOT_FOUND"], "missing key")
                equal(c.ask("SET a hello world"), ["OK"], "set")
                equal(c.ask("GET a"), ["VALUE hello world"], "value keeps its spaces")
                equal(c.ask("SET b 2", "SET a x", "KEYS", "DEL b", "DEL b", "KEYS", "FLY", "GET a"),
                      ["OK", "OK", "KEYS a b", "OK", "NOT_FOUND", "KEYS a", "ERR unknown command", "VALUE x"],
                      "several commands in one send")
                equal(c.ask("QUIT"), ["BYE"], "quit")
                check(c.r.readline() == "", "server closes the connection after BYE")
            finally:
                c.close(); stop(srv)

        def test_split_packets(m):
            srv, port = running(m)
            c = Conn(port)
            try:
                c.s.sendall(b"SE")
                time.sleep(0.05)
                c.s.sendall(b"T k v\\nGE")
                time.sleep(0.05)
                c.s.sendall(b"T k\\n")
                equal([c.r.readline().rstrip("\\n") for _ in range(2)], ["OK", "VALUE v"], "commands split across packets")
                equal(Conn(port).ask("KEYS"), ["KEYS k"], "a second client sees the same store")
            finally:
                c.close(); stop(srv)

        def test_concurrent(m):
            srv, port = running(m)
            errors = []
            def worker(i):
                try:
                    c = Conn(port)
                    for j in range(40):
                        if c.ask(f"SET k{i} {j}") != ["OK"]:
                            errors.append(i)
                    c.close()
                except Exception as e:
                    errors.append(e)
            try:
                ts = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
                for t in ts: t.start()
                for t in ts: t.join()
                equal(errors, [], "every SET answered OK")
                equal(Conn(port).ask("KEYS"), ["KEYS " + " ".join(sorted(f"k{i}" for i in range(8)))], "all keys present")
                equal(Conn(port).ask("GET k3"), ["VALUE 39"], "last write wins")
            finally:
                stop(srv)

        def test_fresh_store(m):
            a, pa = running(m)
            b, pb = running(m)
            try:
                Conn(pa).ask("SET only a")
                equal(Conn(pb).ask("KEYS"), ["KEYS"], "each server has its own store")
            finally:
                stop(a); stop(b)
        ''',
        alts={
            "StreamRequestHandler + a store on the server": ('''
                import socketserver, threading

                class KVServer(socketserver.ThreadingTCPServer):
                    allow_reuse_address = True
                    daemon_threads = True

                    def __init__(self, addr, handler):
                        super().__init__(addr, handler)
                        self.store, self.lock = {}, threading.Lock()

                class Handler(socketserver.StreamRequestHandler):
                    def reply(self, text):
                        self.wfile.write(text.encode() + b"\\n")

                    def handle(self):
                        store, lock = self.server.store, self.server.lock
                        for raw in self.rfile:                      # readline-based: framing for free
                            cmd, _, rest = raw.decode("utf-8").rstrip("\\r\\n").partition(" ")
                            with lock:
                                if cmd == "SET" and " " in rest:
                                    key, _, value = rest.partition(" ")
                                    store[key] = value
                                    out = "OK"
                                elif cmd == "GET" and rest:
                                    out = f"VALUE {store[rest]}" if rest in store else "NOT_FOUND"
                                elif cmd == "DEL" and rest:
                                    out = "OK" if store.pop(rest, None) is not None else "NOT_FOUND"
                                elif cmd == "KEYS" and not rest:
                                    out = " ".join(["KEYS", *sorted(store)])
                                elif cmd == "QUIT":
                                    self.reply("BYE")
                                    return
                                else:
                                    out = "ERR unknown command"
                            self.reply(out)

                def make_server(port=0):
                    return KVServer(("127.0.0.1", port), Handler)
            ''', "StreamRequestHandler gives you rfile/wfile, so 'for line in self.rfile' handles both pipelined "
                 "and split packets: the buffering does the framing. One lock around each command keeps it atomic."),
            "dispatch table": ('''
                import socketserver, threading

                def make_server(port=0):
                    store, lock = {}, threading.Lock()

                    def set_(rest):
                        key, sp, value = rest.partition(" ")
                        if not sp:
                            return "ERR unknown command"
                        store[key] = value
                        return "OK"

                    commands = {
                        "SET": set_,
                        "GET": lambda k: f"VALUE {store[k]}" if k in store else "NOT_FOUND",
                        "DEL": lambda k: "OK" if store.pop(k, None) is not None else "NOT_FOUND",
                        "KEYS": lambda _: " ".join(["KEYS", *sorted(store)]),
                    }

                    class Handler(socketserver.StreamRequestHandler):
                        def handle(self):
                            while line := self.rfile.readline():
                                cmd, _, rest = line.decode().rstrip("\\n").partition(" ")
                                if cmd == "QUIT":
                                    self.wfile.write(b"BYE\\n")
                                    break
                                with lock:
                                    fn = commands.get(cmd)
                                    out = fn(rest) if fn else "ERR unknown command"
                                self.wfile.write(out.encode() + b"\\n")

                    srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler, bind_and_activate=False)
                    srv.allow_reuse_address = True
                    srv.server_bind(); srv.server_activate()
                    return srv
            ''', "A dict from command name to function replaces the if/elif chain: adding a command is one "
                 "line. Real servers (Redis included) are organised exactly like this."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="from urllib.parse import urlsplit\nu = urlsplit('https://example.org:8443/a/b?x=1#top')\nprint(u.hostname, u.port, u.path, u.query)"),
    dict(kind="predict", code="from urllib.parse import urlencode\nprint(urlencode({'q': 'a b', 'n': 2}))", why="Spaces become + in query strings; values are str()'d."),
    dict(kind="predict", code="import socket\na, b = socket.socketpair()\na.sendall(b'ab'); a.sendall(b'cd')\nprint(b.recv(10))", why="TCP-style streams keep bytes, not message boundaries."),
    dict(kind="predict", code="import struct\nprint(struct.pack('!I', 5))"),
    dict(kind="predict", code="from http import HTTPStatus\nprint(HTTPStatus(404).phrase, HTTPStatus.CREATED.value)"),
    dict(kind="recall", q="Which class of HTTP status codes means the client made a mistake (e.g. 404)?", a=["4xx", "4", "400s"]),
    dict(kind="recall", q="What does sock.recv() return when the other side has closed the connection?", a=["b''", 'b""', "empty bytes", "empty"]),
    dict(kind="recall", q="Which ssl function gives a context that verifies certificates and hostnames?", a=["ssl.create_default_context", "create_default_context", "create_default_context()", "ssl.create_default_context()"]),
]
