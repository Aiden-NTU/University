# Writing the Design Outline

The Design Outline is the detailed A4 document the brief asks for: drawings, design features
against the SDGs, research with Harvard citations, and the cost analysis. The engraved poster
walls are the quick read; this is the full story.

**`Book/chapters/` starts as a fill-in template** (sample academic prose, skeleton tables,
placeholder figures). Replace the samples with your research; delete “How to use this template”
before printing. Aim for about **15 dense pages** once filled, plus references.

It is built from plain-text Markdown files in `Book/`, one file per section, so each person can
write their own part without touching anyone else's. The build turns them into
`Book/The_Heat_Exchange_Design_Outline.pdf`, with a cover, contents page, numbered sections,
figures and tables, and a reference list.

```bash
~/.venvs/heat-exchange/bin/python src/book.py            # just the PDF (about 15 s)
~/.venvs/heat-exchange/bin/python src/build_all.py       # everything, the PDF last
```

**Your writing is never overwritten.** A rebuild only refreshes the generated tables and charts
(between `<!-- auto:... -->` and `<!-- /auto -->` lines) and fills in `{{numbers}}` while making
the PDF. Everything else in the files stays exactly as you wrote it.

## 1. The cover

Fill in `Book/book.json`: the team name, everyone's name, student number and role, and the lab
leader. Leave `date` empty to print the build date, or set it to the hand-in date. Set
`"double_sided": false` if it will be printed on one side only (the wider binding margin then
stays on the left of every page).

## 2. Writing a section

Sections live in `Book/chapters/` and appendices in `Book/appendices/`. They appear in filename
order, so `05_materials.md` comes before `06_form.md`. To add a section, copy
`Book/chapters/_template.md` to a new name such as `05b_water.md` (files starting with `_` are
ignored).

The top of each file looks like this:

```markdown
---
authors: Sam Smith, Alex Jones
---
# Materials and construction
```

- `authors:` puts "Written by ..." under the title and adds you to the contributions table.
- Each file has exactly one `#` title. Use `##` for numbered sub-sections and `###` below that.
- Add `numbered: no` under `authors:` for an unnumbered section (like the Summary).

Markdown in two minutes:

| You type | You get |
|---|---|
| `**bold**`, `*italic*` | **bold**, *italic* |
| A blank line | A new paragraph |
| `- item` or `1. item` | Bullet or numbered list |
| `![Caption](../images/photo.jpg)` on its own line | Numbered figure with a caption |
| `![Caption](../images/plan.png){: style="width:90mm"}` | The same, at a set width |
| `Table: Caption` on the line before a table | Numbered table with a caption |
| `!!! note "Title"` then indented text | A shaded call-out box (`note`, `tip`, `warning`) |

Put your own images in `Book/images/` (PNG, JPG or SVG). A table:

```markdown
Table: U-values of the main elements

| Element | U-value (W/m²K) |
| --- | ---: |
| External wall | 0.13 |
```

(`---:` right-aligns a column, which suits numbers.)

### Boxes marked "To write"

The starter text contains dashed orange boxes (`!!! contribute "..."`) saying what each role
should add. Replace the box with your writing. The build lists any that are left, so none get
printed by accident.

## 3. Numbers from the design

Never type a number that the model already knows. Write `{{gia_m2}}` and the PDF shows `720`;
if the design changes, the next build prints the new value. To see every placeholder and its
current value:

```bash
~/.venvs/heat-exchange/bin/python src/book.py --facts
```

They are the same placeholders the laser walls use (`src/project_facts.py`), plus a few
book-only ones (`src/book_blocks.py`, `extra_facts`). To print literal braces, write `\{{`.

## 4. Generated tables and charts

A pair of marker lines asks the build for a table or chart:

```markdown
<!-- auto:costs_by_room -->
<!-- /auto -->
```

Every build replaces whatever is between them, so **don't edit inside a block**: your changes
would be replaced on the next build. Write your discussion above or below it instead. Some blocks
take options on the first line, such as `<!-- auto:lumen_example room=F04 -->` or
`<!-- auto:rooms caption="Rooms on both floors" -->`. To freeze a block, so it stops updating,
delete its two marker lines and keep the table. To list the blocks:

```bash
~/.venvs/heat-exchange/bin/python src/book.py --blocks
```

New blocks are Python functions in `src/book_blocks.py` (add them to `BLOCKS` at the bottom).
Charts are saved to `Book/figures/auto/` and only rewritten when they change.

## 5. Harvard citations

Add each source once to `Book/references.json`, then cite it by its key:

| You write | The PDF shows |
|---|---|
| `[@desnz_ghg2026]` | (Department for Energy Security and Net Zero, 2026a) |
| `[@leti2020, p. 12]` | (LETI, 2020, p. 12) |
| `[@ea_dtm; @ea_dsm]` | (Environment Agency, 2022a; Environment Agency, 2022b) |
| `@churkina2020 argue that...` | Churkina et al. (2020) argue that... |
| `LETI [-@leti2020] set...` | LETI (2020) set... |

The reference list at the end contains only the sources that are cited, sorted alphabetically.
The 2026a and 2026b suffixes are added automatically when one author has two sources in a year.
A source in the file that is never cited is reported when you build.

An entry needs `key`, `authors` (a list of names written as `"Surname, I."`, or an organisation),
`year` (or `"no date"`) and `title`, plus whatever applies:

```json
{
  "key": "smith2024",
  "authors": ["Smith, J.", "Patel, R."],
  "year": 2024,
  "title": "Waste heat recovery from data centres",
  "type": "article",
  "journal": "Energy and Buildings",
  "volume": 301,
  "issue": 2,
  "pages": "113–125",
  "url": "https://doi.org/...",
  "accessed": "14 October 2026"
}
```

For anything that is not a journal article (`report`, `book`, `webpage`, `dataset`, `software`,
`standard`, `legislation`), the optional fields are `edition`, `place`, `publisher`, `version`,
`medium` (shown in square brackets, for example `"Dataset"`) and `detail` (any extra text).

## 6. Cross-references

Write `[[Solar power]]` (the exact heading text, upper or lower case) and the PDF shows
"Section 4.2" as a link. It keeps working when sections are added or reordered.

## 7. Printing

The PDF is A4 with a wider inner margin for binding, mirrored left and right for double-sided
printing. Print it double-sided at 100% (not "fit to page"), flipping on the long edge.

The look of the document (fonts, colours, spacing, cover) is in `Book/theme/book.css`. The
fonts are open-licence copies in `src/fonts/` (Source Serif 4, Source Sans 3, Montserrat,
Comfortaa), so the PDF looks the same on every computer.

## 8. When the build stops

The build stops with a plain message rather than making a PDF with a mistake in it:

| Message | Fix |
|---|---|
| `unknown placeholder {{...}}` | Check the spelling against `--facts` |
| `no reference with the key @...` | Add it to `Book/references.json`, or fix the key |
| `cross-reference [[...]] does not match` | Use the heading text exactly as it appears in Contents |
| `needs exactly one top-level '# Title'` | One `#` per file; use `##` inside |
| `every '<!-- auto:NAME -->' line needs a '<!-- /auto -->'` | A closing marker was deleted |
| `image not found` | Paths are relative to the chapter file: `../images/name.png` |

WeasyPrint needs the Pango text library, which Linux desktops already have. On Windows or macOS,
follow the [WeasyPrint install guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).
