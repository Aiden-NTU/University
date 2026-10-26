# 07 — Network & IPC

## Sheets

| Sheet | Covers |
|-------|--------|
| [[socket_ssl_sheet.py]] | BSD sockets; TLS wrap |
| [[urllib_http_sheet.py]] | urllib.request; http.client/server |
| [[asyncio_streams_subprocess_sheet.py]] | asyncio streams; subprocess pipes |
| [[sqlite3_sheet.py]] | sqlite3 as local IPC/store |

## A vs B

| Goal | Prefer | Why |
|------|--------|-----|
| Quick HTTP GET | `urllib.request` | Stdlib; no deps |
| Full control / HTTP server | `http.client` / `http.server` | Lower level |
| Concurrent clients | `asyncio` + SSL | Scale connections |
| Local structured store | `sqlite3` | ACID file DB |
