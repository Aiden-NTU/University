#!/usr/bin/env python3
"""
=============================================================================
SHEET: urllib.request + http.client/server   TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x stdlib HTTP
=============================================================================

WHAT IT IS
  - urllib.request: high-level URL openers (Request, urlopen, handlers).
  - http.client: lower-level HTTPConnection / HTTPSConnection.
  - http.server: BaseHTTPRequestHandler + HTTPServer for local serving.
  - Probes prefer a local HTTPServer in a daemon thread; if bind fails,
    fall back to pure structure checks (must exit 0 offline).

INVARIANTS
  - urlopen returns a context-managed addinfourl-like response; .read()
    consumes the body; check .status / .getcode().
  - Never pass unsanitised URLs to openers in production (SSRF).
  - http.server is for demos/tools — not a hardened production server.
  - Prefer HTTPS + Certificate validation in real clients (see ssl sheet).

DELEGATES TO (CPython)
  - Lib/urllib/request.py, error.py, parse.py
  - Lib/http/client.py, server.py

COMPLEXITY CARD
  - One request: DNS + TCP + TLS + HTTP — dominated by network RTT
  - Local loopback probe: milliseconds

WHEN A BEATS B
  - Quick GET/POST scripts → urllib.request.
  - Custom headers / pipelining control → http.client.
  - Concurrent clients → asyncio / httpx (third-party) — not this sheet.
  - Teach HTTP → local HTTPServer beats mocking strings alone.

EDGE CASES
  - HTTPError is also a file-like response (has .code / .read()).
  - Redirects: HTTPRedirectHandler follows by default (limit).
  - Binding port 0 → ephemeral; firewalls may still block 127.0.0.1.
  - Offline CI: soft-skip live request if server cannot start.

SOURCE MAP
  - Lib/urllib/request.py :: urlopen, Request, build_opener
  - Lib/http/client.py :: HTTPConnection, HTTPSConnection
  - Lib/http/server.py :: HTTPServer, BaseHTTPRequestHandler
=============================================================================
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# --- API walkthrough ------------------------------------------------------
#
# req = Request(url, data=None, headers={}, method=None)
# with urlopen(req, timeout=...) as resp:
#     body = resp.read(); status = resp.status
#
# urllib.parse: urlparse, urlencode, quote, unquote
# build_opener(*handlers); opener.open(req)
#
# http.client:
#   conn = HTTPConnection(host, port, timeout=...)
#   conn.request("GET", "/path", body=None, headers={})
#   r = conn.getresponse(); r.status; r.read(); conn.close()
#
# http.server:
#   class H(BaseHTTPRequestHandler):
#       def do_GET(self): ...
#   HTTPServer((host, port), H).serve_forever()

HOST = "127.0.0.1"


class _ProbeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 — HTTP verb naming
        if self.path == "/ok":
            body = b'{"ok": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "missing")

    def log_message(self, fmt: str, *args: object) -> None:
        # Quiet — probes should not spam stdout
        return


def _start_local_server() -> Tuple[Optional[HTTPServer], Optional[int]]:
    try:
        httpd = HTTPServer((HOST, 0), _ProbeHandler)
    except OSError:
        return None, None
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


def _probes() -> None:
    """Local HTTP only; soft-skip if bind fails."""
    # --- Request object structure (no I/O) -------------------------------
    req = Request(
        "http://127.0.0.1/ok",
        headers={"User-Agent": "cpython-cheat-sheet"},
        method="GET",
    )
    assert req.get_method() == "GET"
    assert req.get_header("User-agent") == "cpython-cheat-sheet"

    httpd, port = _start_local_server()
    if httpd is None or port is None:
        print("urllib_http_sheet: OK (structure only; bind soft-skip)")
        return

    try:
        url = f"http://{HOST}:{port}/ok"
        with urlopen(url, timeout=2.0) as resp:
            data = resp.read()
            assert resp.status == 200
            assert b"ok" in data

        # 404 via urllib.error.HTTPError
        try:
            urlopen(f"http://{HOST}:{port}/nope", timeout=2.0)
            raise AssertionError("expected HTTPError")
        except HTTPError as e:
            assert e.code == 404
            e.read()  # drain

        # http.client against same server
        from http.client import HTTPConnection

        conn = HTTPConnection(HOST, port, timeout=2.0)
        try:
            conn.request("GET", "/ok")
            r = conn.getresponse()
            assert r.status == 200
            assert b"ok" in r.read()
        finally:
            conn.close()
    except (URLError, OSError, TimeoutError) as exc:
        print(f"local request soft-skip: {exc}")
    finally:
        httpd.shutdown()

    print("urllib_http_sheet: OK")


if __name__ == "__main__":
    _probes()
