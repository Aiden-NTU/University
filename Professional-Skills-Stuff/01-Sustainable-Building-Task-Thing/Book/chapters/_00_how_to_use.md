# How to use this template (not printed)

This file starts with `_` so it is **excluded from the PDF**. Keep it as a checklist; delete when
finished.

## Brief checklist [@ntu_brief]

- [ ] Drawings / diagrams in the Design concept section
- [ ] Features explained vs SDG **targets**
- [ ] Background research with Harvard citations + reference list
- [ ] Cost analysis inside a hypothetical budget
- [ ] Materials, technologies, practicality, originality
- [ ] Honest benefits / drawbacks / limitations
- [ ] Names and roles in `Book/book.json`
- [ ] Cover image replaced (`Book/images/` + `book.json`)
- [ ] All `!!! note` instruction boxes deleted
- [ ] Target ~15 dense pages + references

## Edit / build

| What | Where |
| --- | --- |
| Section text | `Book/chapters/*.md` |
| Cover / team | `Book/book.json` |
| Sources | `Book/references.json` |
| Images | `Book/images/` |
| Rebuild PDF | `python src/book.py` |
| Citation syntax | `docs/DESIGN_OUTLINE.md` |

**Convention:** roman sample prose → rewrite; `[…]` in tables → your numbers; grey `!!! note`
boxes → delete when done.
