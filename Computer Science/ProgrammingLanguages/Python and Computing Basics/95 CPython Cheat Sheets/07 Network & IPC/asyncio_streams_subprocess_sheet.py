#!/usr/bin/env python3
"""
=============================================================================
SHEET: asyncio streams + subprocess          TARGET: CPython 3.14.x
CHAPTER CROSSWALK: 11.x / 14.x
=============================================================================

WHAT IT IS
  - asyncio high-level streams: open_connection / start_server give
    StreamReader / StreamWriter pairs.
  - asyncio.create_subprocess_exec: async child processes with PIPE
    communicate() — prefer argv lists (no shell).

INVARIANTS
  - StreamWriter.drain() awaits when the transport buffer is full.
  - writer.close(); await writer.wait_closed() for clean TCP shutdown.
  - create_subprocess_shell is shell-injection-prone — use _exec + list.
  - communicate() reads stdout/stderr until EOF then waits for exit.
  - Probes use localhost or subprocess of sys.executable — no internet.

DELEGATES TO (CPython)
  - Lib/asyncio/streams.py, subprocess.py, base_events.py
  - Same selector loop as asyncio_sheet

COMPLEXITY CARD
  - start_server: accept loop + per-connection tasks
  - communicate: O(output size) buffering — use streaming for huge data

WHEN A BEATS B
  - Many concurrent TCP clients → streams beat blocking sockets+threads
    for I/O-bound work on one thread.
  - One-shot child → asyncio.subprocess vs subprocess.run: use async when
    the parent is already async; else subprocess.run is simpler.
  - shell=True → almost never; pass argv to create_subprocess_exec.

EDGE CASES
  - Forgetting drain() under backpressure → memory growth / stall.
  - Incomplete ReadError on incomplete readline patterns.
  - Windows: ProactorEventLoop; some pipe behaviours differ.
  - Limit StreamReader buffer (limit=) for untrusted peers.

SOURCE MAP
  - Lib/asyncio/streams.py :: open_connection, start_server, StreamReader
  - Lib/asyncio/subprocess.py :: create_subprocess_exec, Process.communicate
=============================================================================
"""

from __future__ import annotations

import asyncio
import sys
from typing import Tuple

# --- API walkthrough ------------------------------------------------------
#
# reader, writer = await asyncio.open_connection(host, port, ssl=None)
# data = await reader.read(n) / readline() / readexactly(n)
# writer.write(b"..."); await writer.drain()
# writer.close(); await writer.wait_closed()
#
# server = await asyncio.start_server(client_connected_cb, host, port)
# async with server: await server.serve_forever()
#   # or server.sockets / start_serving / wait_closed
#
# proc = await asyncio.create_subprocess_exec(
#     *argv, stdout=PIPE, stderr=PIPE, stdin=PIPE)
# stdout, stderr = await proc.communicate(input=b"...")
# proc.returncode
#
# Also: connect_read_pipe / connect_write_pipe for FD bridging.


HOST = "127.0.0.1"


_ECHO = b"stream-hi"


async def _handle_echo(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    try:
        # Fixed-length framing avoids EOF races with full-close
        data = await reader.readexactly(len(_ECHO))
        writer.write(data)
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def _stream_echo_probe() -> None:
    server = await asyncio.start_server(_handle_echo, HOST, 0)
    sockets = server.sockets
    assert sockets
    port = sockets[0].getsockname()[1]
    async with server:
        await server.start_serving()
        reader, writer = await asyncio.open_connection(HOST, port)
        writer.write(_ECHO)
        await writer.drain()
        data = await asyncio.wait_for(reader.readexactly(len(_ECHO)), timeout=2.0)
        writer.close()
        await writer.wait_closed()
        assert data == _ECHO, data


async def _subprocess_probe() -> None:
    # Echo a small Python one-liner via the same interpreter — offline.
    code = "import sys; sys.stdout.write(sys.stdin.read().upper())"
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        code,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate(input=b"abc")
    assert proc.returncode == 0, (proc.returncode, err)
    assert out == b"ABC", out


async def _async_main() -> None:
    try:
        await _stream_echo_probe()
    except OSError as exc:
        print(f"stream echo soft-skip: {exc}")
    await _subprocess_probe()


def _probes() -> None:
    asyncio.run(_async_main())
    print("asyncio_streams_subprocess_sheet: OK")


if __name__ == "__main__":
    _probes()
