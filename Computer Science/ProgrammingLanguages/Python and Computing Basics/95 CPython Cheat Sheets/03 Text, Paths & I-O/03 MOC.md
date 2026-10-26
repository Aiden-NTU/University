# 03 — Text, Paths & I-O

## Sheets

| Sheet | Covers |
|-------|--------|
| [[pathlib_sheet.py]] | Path objects vs `os.path`; pure vs concrete |
| [[io_sheet.py]] | Text/binary streams; buffering; flush |
| [[json_csv_sheet.py]] | json / csv contracts and failure modes |
| [[re_sheet.py]] | SRE engine; compile once; catastrophic backtracking |

## A vs B

| Goal | Prefer | Why |
|------|--------|-----|
| Path manipulation | `pathlib.Path` | Object API; `/` join; clearer than string glue |
| Bulk text decode | binary read + one decode | Avoid mixed text/binary confusion |
| Structured tabular | `csv` module | Correct quoting; don't `split(",")` |
| Repeated regex | `re.compile` | Avoid recompile per call |
