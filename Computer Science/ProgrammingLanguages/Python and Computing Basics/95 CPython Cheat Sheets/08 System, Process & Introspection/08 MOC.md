# 08 — System, Process & Introspection

## Sheets

| Sheet | Covers |
|-------|--------|
| [[os_sys_sheet.py]] | os, sys; argv; environ; platform facts |
| [[subprocess_argparse_logging.py]] | subprocess, argparse, logging |
| [[gc_dis_inspect_tracemalloc.py]] | gc, dis, inspect, tracemalloc |
| [[hashlib_sheet.py]] | hashlib digests; when to use secrets instead |

## A vs B

| Goal | Prefer | Why |
|------|--------|-----|
| Spawn child | `subprocess.run` | Safer than `os.system` |
| Measure allocations | `tracemalloc` | Python-level; not RSS alone |
| See bytecode | `dis.dis` | Understand optimisations |
| Password hashing | dedicated KDF (`hashlib.scrypt` / libs) | Not raw SHA for passwords |
