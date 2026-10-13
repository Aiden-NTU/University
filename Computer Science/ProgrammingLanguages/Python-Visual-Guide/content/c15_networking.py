"""Chapter 15 - Networking: layers, TCP sockets as byte streams and framing, HTTP anatomy, a JSON API with
http.server and urllib, URLs, TLS, email. Everything runs against servers started on localhost."""
from generator import canvas as C
from generator import fonts as F
from content.kit import (L, R, W, callout, code, flow, practice, section, seq, stamp, sub, table,
                         title_block)

ORDER = 15
NUM = 15
TITLE = "Networking"
SHORT = "Networking"
SLUG = "Networking"
ACCENT = C.BLUE


def sec(f, t, **kw):
    section(f, t, ACCENT, **kw)


# ----------------------------------------------------------------------------- pictures
def layers_picture(f):
    """The network stack, with the Python module that talks to each layer."""
    rows = [
        ("application", "HTTP, SMTP, your JSON", "urllib, http.client/server, smtplib", C.GREEN),
        ("security", "TLS: encryption + identity", "ssl", C.RED),
        ("transport", "TCP: reliable byte stream, ports", "socket (SOCK_STREAM)", ACCENT),
        ("network", "IP: addresses, packets, routing", "socket (AF_INET / AF_INET6)", C.PURPLE),
        ("link", "Ethernet, Wi-Fi", "the OS and the network card", C.GREY),
    ]
    h = 30
    y = f.reserve(len(rows) * (h + 4) + 24)
    pg = f.pg
    pg.text(L + 6, y, "layer", 9.5, C.GREY, F.BOLD)
    pg.text(L + 104, y, "what it gives the layer above", 9.5, C.GREY, F.BOLD)
    pg.text(L + 310, y, "Python", 9.5, C.GREY, F.BOLD)
    for i, (name, what, mod, col) in enumerate(rows):
        yy = y + 16 + i * (h + 4)
        pg.rect(L, yy, W, h, col, 1.1, fillcolor=C.LIGHT[col], r=5)
        pg.text(L + 8, yy + 8, name, 10.5, col, F.BOLD)
        pg.text(L + 104, yy + 8, what, 10, C.INK)
        pg.text(L + 310, yy + 8, mod, 8.6, C.INK, F.MONO)


def stream_picture(f):
    """Two sends become one stream of bytes; recv cuts it wherever it likes."""
    y = f.reserve(112)
    pg = f.pg
    data = "first message" + "second"
    cell = 15
    x0 = L + (W - len(data) * cell) / 2
    for i, ch in enumerate(data):
        col = ACCENT if i < 13 else C.PURPLE
        pg.rect(x0 + i * cell, y + 40, cell, 22, col, 0.8, fillcolor=C.LIGHT[col])
        pg.text(x0 + i * cell + cell / 2, y + 44, ch if ch != " " else "␣", 9.5, C.INK, F.MONO, align="center")
    pg.text(x0, y + 4, 'send(b"first message")', 9, ACCENT, F.MONO)
    pg.text(x0 + 13 * cell, y + 4, 'send(b"second")', 9, C.PURPLE, F.MONO)
    pg.line(x0, y + 20, x0 + 13 * cell - 2, y + 20, ACCENT, 1.2)
    pg.line(x0 + 13 * cell + 2, y + 20, x0 + len(data) * cell, y + 20, C.PURPLE, 1.2)
    for cut in (4, 16):
        cx = x0 + cut * cell
        pg.line(cx, y + 34, cx, y + 68, C.RED, 1.6, dash=(3, 2))
    pg.text(x0 + 2 * cell, y + 72, "recv → b'firs'", 9, C.RED, F.MONO, align="center")
    pg.text(x0 + 10 * cell, y + 72, "recv → b't messagesec'", 9, C.RED, F.MONO, align="center")
    pg.text(x0 + 17.5 * cell, y + 72, "recv → b'ond'", 9, C.RED, F.MONO, align="center")
    pg.note(L + W / 2, y + 88, "the boundaries you sent are gone: one possible way the receiver sees it",
            C.RED, 13, align="center")


def http_picture(f):
    """Anatomy of an HTTP request and response."""
    req = [("POST /books HTTP/1.1", ACCENT, "request line: method, path, version"),
           ("Host: lib.example.org", C.PURPLE, "headers: Name: value"),
           ("Content-Type: application/json", C.PURPLE, ""),
           ("Content-Length: 17", C.PURPLE, ""),
           ("", C.GREY, "blank line (\\r\\n): headers end"),
           ('{"title": "Ubik"}', C.GREEN, "body: exactly Content-Length bytes")]
    resp = [("HTTP/1.1 201 Created", ACCENT, "status line: version, code, reason"),
            ("Content-Type: application/json", C.PURPLE, ""),
            ("Location: /books/3", C.PURPLE, ""),
            ("", C.GREY, ""),
            ('{"id": 3, "title": "Ubik"}', C.GREEN, "")]
    lh = 15
    h = 24 + len(req) * lh + 22 + len(resp) * lh + 10
    y = f.reserve(h)
    pg = f.pg
    bw = 250

    def block(yy, lines, title):
        pg.text(L, yy, title, 9.5, C.GREY, F.BOLD)
        pg.rect(L, yy + 14, bw, len(lines) * lh + 8, "#d5d9df", 0.8, fillcolor="#f6f7f9", r=4)
        for i, (s, col, note) in enumerate(lines):
            ly = yy + 18 + i * lh
            pg.text(L + 8, ly, s if s else "↵", 9, col, F.MONO)
            if note:
                pg.arrow(L + bw + 30, ly + 6, L + bw + 4, ly + 6, col, 0.9, head=4)
                pg.note(L + bw + 34, ly - 3, note, col, 13)
        return yy + 14 + len(lines) * lh + 8

    yy = block(y, req, "client sends")
    block(yy + 8, resp, "server answers")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    title_block(ch, 15, TITLE, "a network connection is just a file that someone else writes to", ACCENT)
    f = ch.flow(top=190)
    f.p("Networking is built in {B:layers}. Each one uses the layer below and hides its mess from the "
        "layer above: IP loses and reorders packets, TCP turns them into a reliable stream, HTTP gives the "
        "stream a request/response shape. Python has a module at each level:", 14, gap=10)
    layers_picture(f)
    f.p("Every example in this chapter really runs: it starts a server on your own machine "
        "(`127.0.0.1`, \"localhost\") in a background thread and talks to it. No internet needed, and the "
        "output shown is what happened.", 13.5, gap=8)
    callout(f, "idea", "An address is a pair: {B:(host, port)}. The host finds the machine; the port (0-65535) "
            "finds the program on it. Ports below 1024 are reserved for well-known services (80 HTTP, 443 "
            "HTTPS, 22 SSH, 25 SMTP) and need admin rights to listen on.")


def socket_section(ch):
    f = flow(ch)
    sec(f, "TCP sockets: a phone line for bytes", room=440)
    f.p("A server {B:listens} on a port; a client {B:connects}; then both sides have a socket they can "
        "`sendall` bytes into and `recv` bytes out of, until one side closes:", 13.5, gap=8)
    seq(f, ["client", "server (already listening)"], [
        ("client", "server (already listening)", "connect (TCP handshake)"),
        ("client", "server (already listening)", 'sendall(b"hello, server")'),
        ("server (already listening)", "client", 'sendall(b"HELLO, SERVER")', "reply"),
        ("client", "server (already listening)", "close → server's recv returns b''"),
    ], step=27)
    code(f, """
        import socket, threading

        def echo_server(listener):
            conn, addr = listener.accept()                  # wait for one client
            with conn:
                while data := conn.recv(1024):              # b"" means the client hung up
                    conn.sendall(data.upper())

        listener = socket.create_server(("127.0.0.1", 0))   # port 0: the OS picks a free one
        port = listener.getsockname()[1]
        threading.Thread(target=echo_server, args=(listener,), daemon=True).start()

        with socket.create_connection(("127.0.0.1", port), timeout=5) as c:
            c.sendall(b"hello, server")
            print(c.recv(1024))
            print(c.getsockname()[0], "->", c.getpeername()[0], 1023 < port < 65536)
        listener.close()
    """, notes={4: "accept blocks", 13: "always a timeout"})
    sub(f, "The big surprise: TCP has no messages", ACCENT, room=175)
    f.p("TCP promises the bytes arrive complete and in order, nothing more. Two `send`s can arrive as one "
        "`recv`, and one `send` can arrive as three:", 13.5, gap=6)
    stream_picture(f)
    code(f, """
        a, b = socket.socketpair()              # two connected sockets, handy for experiments
        a.sendall(b"first message")
        a.sendall(b"second")
        print(b.recv(1024))                     # both sends, glued together

        reader = b.makefile("rb")               # a file view of the socket
        a.sendall(b"first message\\n" + b"second\\n")
        print(reader.readline(), reader.readline())
    """, notes={7: "framing: newline ends a message"})
    callout(f, "rule", "Every protocol on TCP needs {B:framing}: a way to know where a message ends. The two "
            "classics are a delimiter (a newline, as SMTP, Redis and this chapter's practice 15.6 use) and a "
            "length prefix (send `struct.pack(\"!I\", len(data))` first, as HTTP's Content-Length and "
            "practice 15.1 do). `recv(n)` returns {B:up to} n bytes, so loop until you have them all.")


def http_section(ch):
    f = flow(ch)
    sec(f, "HTTP: text over TCP", room=440)
    f.p("HTTP is a framing convention on top of TCP: some lines of text, a blank line, then an optional "
        "body whose length is in a header. First, a small JSON API server using only the standard library:",
        13.5, gap=8)
    code(f, """
        import json, threading
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

        BOOKS = {1: {"id": 1, "title": "Dune"}, 2: {"id": 2, "title": "Emma"}}

        class Api(BaseHTTPRequestHandler):
            def send_json(self, status, obj):
                body = json.dumps(obj).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()                          # the blank line
                self.wfile.write(body)

            def do_GET(self):                               # one method per HTTP verb
                if self.path == "/books":
                    return self.send_json(200, list(BOOKS.values()))
                book_id = self.path.removeprefix("/books/")
                if book_id.isdigit() and int(book_id) in BOOKS:
                    return self.send_json(200, BOOKS[int(book_id)])
                self.send_json(404, {"error": f"no such book: {self.path}"})

            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                book = {"id": max(BOOKS) + 1, "title": data["title"]}
                BOOKS[book["id"]] = book
                self.send_json(201, book)

            def log_message(self, *args):                   # keep the server quiet
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Api)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
    """, notes={24: "read exactly the body", 32: "a thread per request"})
    f.p("This is what travels over the TCP connection. Each part has a job:", 13.5, gap=6)
    http_picture(f)
    f.need(190)
    f.p("Now speak HTTP to our server by hand over a raw socket (dropping the `Date` header, which changes "
        "every run):", 13.5, gap=6)
    code(f, """
        with socket.create_connection(("127.0.0.1", server.server_port), timeout=5) as c:
            c.sendall(b"GET /books/1 HTTP/1.0\\r\\nHost: localhost\\r\\n\\r\\n")
            reply = b""
            while chunk := c.recv(4096):                    # HTTP/1.0: server closes when done
                reply += chunk
        print("\\n".join(l for l in reply.decode().splitlines() if not l.startswith("Date")))
    """)


def client_section(ch):
    f = flow(ch)
    sec(f, "Calling a JSON API with urllib", room=440)
    f.p("`urllib.request` does the HTTP for you: building the request, reading the status and headers, "
        "following redirects. Errors with a status of 400 or more raise `HTTPError`, which still carries the "
        "response body:", 13.5, gap=8)
    code(f, """
        import json, urllib.error, urllib.request

        def get_json(url):
            with urllib.request.urlopen(url, timeout=5) as resp:
                return resp.status, json.load(resp)

        print(get_json(base + "/books/2"))

        req = urllib.request.Request(base + "/books", method="POST",
                                     data=json.dumps({"title": "Ubik"}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(resp.status, resp.headers["Content-Type"], json.load(resp))

        try:
            get_json(base + "/books/99")
        except urllib.error.HTTPError as e:
            print(e.code, e.reason, json.load(e))
        server.shutdown()                                   # stop the background server
    """, notes={4: "no timeout = may hang forever", 18: "the error body is JSON too"})
    table(f, ["status", "means", "common ones"], [
        ["`2xx`", "it worked", "`200 OK`, `201 Created` (+ `Location`), `204 No Content`"],
        ["`3xx`", "look elsewhere", "`301 Moved Permanently`, `304 Not Modified` (use your cache)"],
        ["`4xx`", "{B:you} got it wrong: don't retry as is", "`400`, `401` who are you?, `403` not allowed, "
         "`404`, `409` conflict, `429` slow down"],
        ["`5xx`", "{B:the server} broke: retry later", "`500`, `502 Bad Gateway`, `503 Unavailable`"],
    ], widths=[0.8, 2.4, 3.8], size=10.5)
    table(f, ["method", "does", "safe?", "repeatable (idempotent)?"], [
        ["`GET`", "read", "{G:yes}", "{G:yes}"],
        ["`POST`", "create / do something", "no", "{R:no}: twice makes two"],
        ["`PUT`", "replace at this URL", "no", "{G:yes}"],
        ["`DELETE`", "remove", "no", "{G:yes}"],
    ], widths=[1.0, 2.2, 0.9, 2.4], size=10.5)
    callout(f, "why", "Idempotency decides what is safe to {B:retry} after a timeout: you don't know whether "
            "the request arrived. Retrying a GET or PUT is harmless; retrying a POST might lend the book "
            "twice, which is why payment APIs make you send an idempotency key.")


def urls_tls_section(ch):
    f = flow(ch)
    sec(f, "URLs, TLS, and email", room=420)
    code(f, """
        from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

        u = urlsplit("https://lib.example.org:8443/search?q=dune&page=2#results")
        print(u.scheme, u.hostname, u.port, u.path, u.query, u.fragment)
        print(parse_qs(u.query))
        print(urlencode({"q": "science fiction", "lang": "en"}), quote("a/b c&d", safe=""))
        print(urljoin("https://lib.example.org/books/", "../authors/7"))
    """, notes={6: "never glue URLs with +"})
    f.p("{B:TLS} (the S in HTTPS) encrypts the stream and proves the server's identity with a certificate. "
        "`urllib` uses it automatically for `https://`. The one rule is to leave verification on:", 13.5, gap=6)
    code(f, """
        import ssl

        ctx = ssl.create_default_context()          # trusted CAs, hostname checks, modern TLS
        print(ctx.verify_mode == ssl.CERT_REQUIRED, ctx.check_hostname, ctx.minimum_version)
    """)
    code(f, """
        with socket.create_connection(("example.org", 443), timeout=10) as raw:
            with ctx.wrap_socket(raw, server_hostname="example.org") as tls:
                print(tls.version(), tls.getpeercert()["subject"])
    """, run=False, title="wrapping a socket yourself (not run here: needs the internet)")
    callout(f, "trap", "`ssl._create_unverified_context()`, `verify=False` in requests, or `CERT_NONE` make "
            "the error go away by letting anyone in the middle read and change the traffic. Fix the "
            "certificate (or install the right CA) instead. And if your server fetches URLs that users supply, "
            "check where they point first: `http://169.254.169.254/` is how cloud credentials get stolen (SSRF).")
    sub(f, "Email: build with email, send with smtplib", ACCENT, room=220)
    code(f, """
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"], msg["To"] = "library@example.org", "ana@example.org"
        msg["Subject"] = "Your loan is due"
        msg.set_content("Dune is due back on 12 October.\\n")
        print(msg.as_string())
    """)
    code(f, """
        import smtplib

        with smtplib.SMTP("smtp.example.org", 587, timeout=10) as s:
            s.starttls(context=ssl.create_default_context())    # upgrade to TLS first
            s.login(user, password)                              # from the environment (Ch 14)
            s.send_message(msg)
    """, run=False, title="sending (not run here: needs a mail server)")
    table(f, ["need", "use"], [
        ["a quick GET/POST from a script", "`urllib.request` (stdlib)"],
        ["many requests to one host, low-level control", "`http.client` (keeps the connection open)"],
        ["a real application: sessions, retries, nicer API", "`requests` or `httpx` from pip (Ch 19)"],
        ["serve HTTP in production", "a framework (Flask, Django, FastAPI) behind a real server, not "
         "`http.server`"],
    ], widths=[3.0, 3.4], size=10.5)


def finish(ch):
    f = flow(ch)
    sec(f, "Practise, then stamp", room=300)
    practice(f, 15)
    stamp(f, [
        (9, "Network I/O is bytes over sockets: `socket` (TCP byte stream, needs framing), `ssl` for TLS, "
            "`urllib.request` / `http.client` for HTTP, `http.server` for tiny servers."),
        (11, "`socket`, `socketserver`, `ssl`, `urllib.request`, `urllib.parse`, `http.client`, `http.server`, "
             "`http.HTTPStatus`, `json`, `email`, `smtplib`."),
    ])
    callout(f, "other", "The socket API is the same everywhere because it's the OS's (BSD sockets, 1983): C "
            "`socket()/bind()/listen()/accept()`, Java `ServerSocket`, Go `net.Listen`, Rust "
            "`std::net::TcpListener`. HTTP clients differ in style, not substance: Java `HttpClient`, Go "
            "`net/http`, JS `fetch`.")
    callout(f, "deep", "Vault notes: {b:18.2} Networks and layered agreements · {b:18.3} Addresses, ports, and "
            "names · {b:18.4} TCP and the meaning of a byte stream · {b:18.5} TLS - authenticated protected "
            "transport · {b:18.7} HTTP messages · {b:18.8} Methods and method properties · {b:18.9} Status "
            "codes · {b:18.13} From a request to a Python callable · {b:18.26} Server-side request forgery.")


def build(ch):
    title_page(ch)
    socket_section(ch)
    http_section(ch)
    client_section(ch)
    urls_tls_section(ch)
    finish(ch)
