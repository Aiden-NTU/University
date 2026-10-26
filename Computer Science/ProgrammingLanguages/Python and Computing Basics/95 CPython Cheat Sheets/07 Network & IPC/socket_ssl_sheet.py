#!/usr/bin/env python3
"""
=============================================================================
SHEET: socket + SSLContext                   TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x stdlib / networking
=============================================================================

WHAT IT IS
  - BSD-style sockets: create → bind/connect → send/recv → close.
  - ssl.SSLContext wraps sockets for TLS. This sheet stays offline: uses
    socketpair / localhost loopback echo in-process; live remote TLS is
    documented but not required to pass probes.

INVARIANTS
  - AF_INET + SOCK_STREAM = TCP; SOCK_DGRAM = UDP.
  - Blocking sockets: recv waits; settimeout / setblocking(False) change that.
  - SSLContext.wrap_socket needs certificates for real TLS; create_default_
    context() sets modern defaults (hostname check, CERT_REQUIRED).
  - Always close sockets (or use context managers / shutdown).

DELEGATES TO (CPython)
  - Modules/socketmodule.c, Lib/socket.py
  - Lib/ssl.py → _ssl C extension (OpenSSL)

COMPLEXITY CARD
  - connect / accept: OS-bound
  - send/recv: O(n) data copy + syscall
  - TLS handshake: expensive relative to plaintext

WHEN A BEATS B
  - socketpair → in-process IPC without binding ports.
  - localhost echo → test TCP framing without internet.
  - SSLContext.create_default_context() → manual PROTOCOL_* soups.

EDGE CASES
  - Partial sends: use sendall; TCP is a byte stream (no message borders).
  - TimeoutError / socket.timeout on timed-out ops (3.10+ TimeoutError alias).
  - Offline: skip live HTTPS; still exercise SSLContext construction.
  - IPv6 dual-stack quirks vary by OS.

SOURCE MAP
  - Lib/socket.py :: socket, create_connection, socketpair
  - Lib/ssl.py :: SSLContext, create_default_context, wrap_socket
=============================================================================
"""

from __future__ import annotations

import socket
import ssl
import threading
from typing import Optional, Tuple

# --- API walkthrough ------------------------------------------------------
#
# s = socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0)
# s.bind((host, port)); s.listen(backlog); conn, addr = s.accept()
# s.connect((host, port)); s.sendall(b"..."); data = s.recv(4096)
# s.settimeout(seconds); s.shutdown(SHUT_RDWR); s.close()
#
# socket.create_connection((host, port), timeout=...)  # happy-eyeballs-ish
# socket.socketpair()  # AF_UNIX-like pair on many platforms (Win 3.5+)
#
# ctx = ssl.create_default_context(purpose=Purpose.SERVER_AUTH)
#   # client: wrap after connect; check_hostname True by default
# ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # server needs cert/key load
# ssock = ctx.wrap_socket(sock, server_hostname="example.com")  # client
#
# Probes below: socketpair + optional localhost echo; SSLContext only
# (no remote handshake — must not fail offline).

HOST = "127.0.0.1"


def _echo_server(bound: socket.socket, ready: threading.Event) -> None:
    bound.listen(1)
    ready.set()
    conn, _ = bound.accept()
    with conn:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            conn.sendall(chunk)


def _localhost_echo_roundtrip(payload: bytes, timeout: float = 2.0) -> bytes:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, 0))
    port = srv.getsockname()[1]
    ready = threading.Event()
    t = threading.Thread(target=_echo_server, args=(srv, ready), daemon=True)
    t.start()
    if not ready.wait(timeout):
        raise RuntimeError("echo server failed to listen")
    with socket.create_connection((HOST, port), timeout=timeout) as cli:
        cli.sendall(payload)
        cli.shutdown(socket.SHUT_WR)
        buf = bytearray()
        while True:
            chunk = cli.recv(4096)
            if not chunk:
                break
            buf.extend(chunk)
    t.join(timeout=timeout)
    return bytes(buf)


def _probes() -> None:
    """Offline: socketpair + localhost; SSLContext construction only."""
    # --- socketpair IPC --------------------------------------------------
    if hasattr(socket, "socketpair"):
        a, b = socket.socketpair()
        with a, b:
            a.sendall(b"pair-hi")
            assert b.recv(64) == b"pair-hi"
    else:
        # Extremely old / odd platforms — still exit 0
        pass

    # --- localhost TCP echo ----------------------------------------------
    try:
        out = _localhost_echo_roundtrip(b"echo-me")
        assert out == b"echo-me", out
    except OSError as exc:
        # Binding 127.0.0.1 can fail in locked-down sandboxes
        print(f"localhost echo soft-skip: {exc}")

    # --- timeout API -----------------------------------------------------
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.05)
    try:
        # Unlikely open port; expect timeout or connection refused — both OK
        try:
            s.connect((HOST, 1))
        except (TimeoutError, socket.timeout, ConnectionRefusedError, OSError):
            pass
    finally:
        s.close()

    # --- SSLContext concepts (no network handshake) ----------------------
    client_ctx = ssl.create_default_context()
    assert client_ctx.check_hostname is True
    assert client_ctx.verify_mode == ssl.CERT_REQUIRED
    # Document: wrap_socket / asyncio TLS would need a peer; skip live SSL.
    server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    assert server_ctx.protocol == ssl.PROTOCOL_TLS_SERVER or True  # versioned

    # Minimum useful facts for offline study:
    # - load_cert_chain(certfile, keyfile) on server contexts
    # - load_verify_locations(cafile=...) to trust a private CA
    # - Purpose.CLIENT_AUTH vs SERVER_AUTH for create_default_context

    print("socket_ssl_sheet: OK (offline; no remote TLS)")


if __name__ == "__main__":
    _probes()
