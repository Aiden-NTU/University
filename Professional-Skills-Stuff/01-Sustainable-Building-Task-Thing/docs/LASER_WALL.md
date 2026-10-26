# The laser-engraved poster walls

Instead of a paper poster, four plywood walls stand round the 1:1000 site model. Their outer faces carry the poster: title, headline numbers, how the heat exchange works, floor plans, the room list, the site, how we made it, and a QR code into the web twin. Everything is engraved into the wood.

The walls are not glued. Each one drops into a slot printed into the rim of the site model, so you can lift any wall out to show the model inside, and put it back.

![The four walls, in the order you meet them walking round the model](../Poster/laser_wall/preview.svg)

*The four outer faces. Walk round the model anticlockwise: south (the front), east, north, west. The line near each foot is the top of the rim; the strip below it sits down in the slot.*

| Wall | Theme | What's on it |
| --- | --- | --- |
| 1. South (front) | The project | Title, headline numbers, what it is, where it is, "peek inside", quote, QR code |
| 2. East | Energy | Where the heat comes from, server heat, solar and battery, lighting, fresh air, seasonal shade |
| 3. North | The building | Floor plans, room list, timber construction, sawtooth roof, glazing |
| 4. West | Site and people | Landscape, cycle hub, rainwater, teaching, UN SDGs, how we made the model, honest numbers, data credits, team |

Fun details are built in:

- **The top edge is the roof.** The sawtooth edge echoes the building's 25 degree north-light roof.
- **The foot of each wall is a ruler.** At 1:1000, 1 mm is 1 m, so the ticks measure the site directly behind that wall, counting from the corner at your left. A bracket marks where The Heat Exchange stands: "The Heat Exchange is right behind here".
- **The notes look like sticky notes.** Each one is slightly tilted and "taped" on.
- **Doodles fill spare space** so no wall looks half empty.

## How the walls fit the model

The outer 7.5 mm of the printed site model is a raised grey rim with a slot in it:

| | Size |
| --- | --- |
| Outer lip | 2 mm wide |
| Slot | 3.5 mm wide (3 mm ply + 0.5 mm play), 9 mm deep |
| Inner lip | 2 mm wide |
| Rim top | 14 mm above the bottom of the print, level all the way round |

The rim is part of the grey roads-and-paths print, so it needs no extra filament change. On the two-half print it runs through both halves, and the east and west walls straddle the join, which helps hold the halves in line.

The four walls are **identical boards**, 221 mm long. They sit in the slot like a pinwheel: seen from outside, each wall's right end runs into the next corner and its left end butts against the inside face of the previous wall. Because all four are the same size, any wall physically fits any side, but the content and rulers are written for one side each. The label engraved on the strip that hides in the slot (for example `SOUTH WALL · 1 of 4`) says which.

The bottom corners are chamfered by 1 mm so the boards find the slot easily.

## Is the QR code safe to engrave permanently?

Yes. The code only stores the address `https://aiden12343.github.io/heat-exchange-twin/`. Rebuilding and redeploying the web twin changes what is *at* that address, not the address itself, so the engraved code keeps working.

It breaks only if the GitHub repository is renamed or deleted, or GitHub Pages is switched off. Keep that repository as it is until after the assessment.

## Add your own card (no code)

Open [`Poster/laser_wall.json`](../Poster/laser_wall.json) and add a card to the `cards` list. Copy an existing card, change the words, and rebuild:

```bash
~/.venvs/heat-exchange/bin/python src/laser_wall.py
```

Then open `Poster/laser_wall/preview.svg` in a browser to see the result. The script fits all the cards automatically. All four walls are always the same height, so they stay interchangeable:

1. It keeps the preferred height above the rim (`height_mm`, 110 mm) and makes the text as large as fits, up to 130% size.
2. If the cards don't fit at normal text size, it makes the walls taller in 5 mm steps, up to `max_height_mm` (140 mm).
3. Only after that does it shrink the text, down to 80% (about 2.3 mm letters).
4. If it still doesn't fit, it stops and tells you to shorten something. It never produces an unreadable wall.

It prints what it chose, for example: `4 walls, each 221.0 x 129 mm (120 mm showing above the rim), text at 102% (2.9 mm body text)`.

### Card types

| `type` | What it looks like | Fields |
| --- | --- | --- |
| `note` | Tilted sticky note with an icon | `title`, `text`, `icon` |
| `text` | Plain paragraph, optional icon and heading | `title`, `text`, `icon` |
| `stats` | Round badges with a big number | `items`: list of `{ "value", "label" }` (optional `icon`) |
| `steps` | Numbered timeline | `title`, `steps`: list of sentences |
| `quote` | Big handwritten quote | `text`, optional `by` |
| `team` | Handwritten signatures | `title`, `names`: list of names |
| `plan` | Ground and first floor plans with room codes | none (drawn from the building model) |
| `rooms` | Room list with areas | optional `skip` (room codes), `areas` (true/false) |
| `title` | Heading with a sawtooth underline | `title`, `tagline`, optional `size_mm` (15 by default) |
| `qr` | QR code with a caption and the address | `url`, `caption`, `size_mm` (44 by default; at least 0.9 mm per square) |

Examples:

```json
{ "wall": "west", "type": "note", "icon": "drop", "title": "Rainwater", "text": "Rain from the roof flushes the WCs." }
```

```json
{ "wall": "east", "type": "stats", "items": [ { "value": "{pv_kwp} kWp", "label": "solar power" } ] }
```

The team card (on the west wall) is waiting for names. Fill in `"names": ["Your Name", ...]`; until then it is left off.

Icons: `arrow`, `bike`, `bolt`, `book`, `cube`, `cup`, `cycle`, `drop`, `globe`, `house`, `leaf`, `people`, `pin`, `ruler`, `sawtooth`, `server`, `solar`, `sparkle`, `star`, `sun`, `thermo`, `tree`, `wind`.

If you type a character the fonts don't have (some emoji or unusual symbols), the build stops and names it, rather than engraving an empty box.

### Numbers that stay correct

Write a name in curly brackets and the script fills in the current value from the building model or the costing sheet, so the walls never disagree with the model. For example, `"{gia_m2} m²"` becomes `720 m²`.

| Placeholder | Meaning |
| --- | --- |
| `{gia_m2}`, `{rooms}`, `{length_m}`, `{depth_m}`, `{height_m}`, `{storeys}` | Size of the building |
| `{volume_m3}`, `{envelope_m2}` | Heated volume and envelope area |
| `{wwr_n}`, `{wwr_e}`, `{wwr_s}`, `{wwr_w}` | Glazing as a percentage of each facade |
| `{pv_kwp}`, `{pv_modules}`, `{pv_tilt}` | Solar roof |
| `{overhang_m}`, `{shade_june}`, `{shade_december}`, `{sun_june}`, `{sun_december}` | Noon sun height and the shadow of the south overhang |
| `{lighting_saving_pct}`, `{lighting_saving_kwh}`, `{lighting_saving_gbp}`, `{co2_saving_kg}` | LED and controls saving against a fluorescent baseline |
| `{lighting_design_kwh}`, `{lighting_baseline_kwh}` | Lighting energy a year, design and baseline |
| `{server_racks}`, `{server_kw}`, `{server_heat_mwh}` | Edge server room: racks, assumed load per rack, heat a year |
| `{led_panels}`, `{light_sensors}`, `{iaq_sensors}`, `{bike_spaces}` | Counts from `Costing/items.csv` |
| `{fitout_gbp}`, `{fitout_k}` | Fit-out cost (indicative prices) |
| `{print_hours}`, `{print_grams}`, `{print_gbp}` | Printing the whole model |
| `{lat}`, `{lon}`, `{lon_dir}`, `{ffl}` | Location and floor level |
| `{site_scale}`, `{building_scale}` | Model scales |

A misspelt name stops the build and lists the valid ones.

### Where a card goes

- `"wall": "south"`, `"east"`, `"north"` or `"west"` puts a card on that wall. A card without `wall` goes wherever there is room once the others are placed.
- Within its wall, cards fill the columns roughly in list order.
- `"place": "start"` pins a card to the top left of its wall (used for each wall's heading).
- `"place": "end"` pins it to the top right (used for the QR code).
- `"wide": true` or `false` makes a card two columns or one. Plans, rooms, titles and stats with more than two badges are wide by default.
- `"enabled": false` hides a card without deleting it.

If one wall gets much fuller than the others, every wall grows to match it. Moving a card to a quieter wall keeps them all shorter.

## Making it

Do these in order, because the printed slot and the plywood have to agree.

### 1. Measure the ply before printing the site model

Buy or borrow the sheet first and measure it with callipers in a few places. "3 mm" ply is often 2.8 to 3.2 mm. Set `WALL_PLY_MM` in `src/config.py` to the thickest reading and rebuild everything (`python src/build_all.py`). That re-cuts the slot in the site model and re-slices the print jobs. `SITE_WALL_SLOT_CLEARANCE_MM` (0.5 mm) is the play on top of that: lower it to 0.3 for a tighter, more upright fit, or raise it if the printed slot comes out tight.

### 2. Material and settings

- **Material:** 3 mm laser ply, which NTU's art and design workshops stock.
- **Files to bring:** `Poster/laser_wall/cut_sheet_1_420x297.svg` and `cut_sheet_2_420x297.svg`. Two walls fit on each A3 sheet, which fits even a small laser bed. The separate `wall_*.svg` files are there if the technician prefers one wall at a time. If the bed is bigger, set `sheet_mm` in the JSON and the walls are repacked. All text is already outlines, so no fonts are needed.
- **Colours:** red hairline = **cut**, blue hairline = **score** (the card borders and rulers), black fill = **engrave**. Show the technician this list; if their lab uses a different convention, change `layers` in the JSON. Ask for engrave, then score, then cut, so the walls don't move before they're finished.
- **Masking tape:** if the technician suggests it, masking tape over the face reduces smoke staining.

### 3. Test first: two small pieces in the spare corner of sheet 2

1. **QR scan test (about 2 minutes).** Engrave and cut only this square, then scan it with a few phones. If it won't scan, ask for a darker engrave (more power or less speed). Don't use an inverted or negative mode: the squares must be the dark, burnt part.
2. **Slot fit test.** A 30 x 16 mm offcut with the same chamfered foot as the walls. Push it into the printed rim slot.
   - It should slide down to the slot floor by hand and stand up without flopping over.
   - If it won't go in, sand the slot lightly or raise `SITE_WALL_SLOT_CLEARANCE_MM` for the next print.
   - It also checks the kerf: it should measure 30.0 x 16.0 mm. If it comes out smaller, raise `kerf_mm` (try 0.2); if bigger, lower it (try 0.1). Rebuild before cutting the real walls.

### 4. Putting it together

1. Stand the site model on the table.
2. Drop the walls in, engraved face outwards, in label order: south, east, north, west. Each wall's left end tucks behind the wall before it.
3. To show the inside, lift any one wall straight up. The others stay standing.

### Will the walls hide the model?

That's partly the point: lift a wall to reveal it. With all four in place, the walls stand 120 mm above the rim and the tallest thing on the site model (trees) is 27 mm. Someone standing at the table looks down at roughly 60 degrees, so each wall hides only about the first 70 mm behind it, and the middle of the model, including The Heat Exchange, stays in view from above.
