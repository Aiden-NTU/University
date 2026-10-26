# Adding reusable furniture and landscape items

Use [`src/placeables.json`](../src/placeables.json) to add ordinary furniture, screens and landscape props without editing Python. It is the one place where a teammate defines an item's shape, colour, print behaviour and (for room items) schedule item. A separate placement row then puts that same item wherever it is needed.

The file already contains disabled examples for a sofa, screen and swing. They do not change the current design until their placement has `"enabled": true`.

## The two ideas

An **asset** is the reusable item definition. Give it a memorable name and set its dimensions, colour and print/schedule behaviour once.

```json
"quiet-room-sofa": {
  "shape": "sofa",
  "catalogue_type": "sofa",
  "colour": "#C9CCCE",
  "printable": true,
  "parameters": {
    "width_m": 2.0,
    "depth_m": 0.9,
    "height_m": 0.8
  }
}
```

A **placement** is an instance of that asset. It says where the object goes, but does not repeat its size, colour or schedule information.

```json
{
  "id": "quiet-room-sofa-1",
  "asset": "quiet-room-sofa",
  "target": "room",
  "room": "G03",
  "x_m": 6.0,
  "y_m": 10.5,
  "facing": "N"
}
```

To use the same sofa in another room, add another placement row with a new `id`, room code and position, and keep `"asset": "quiet-room-sofa"`.

All coordinates are in metres. The building origin is its south-west corner; x goes east and y goes north. `N`, `S`, `E` and `W` control the facing of sofas and screens. Start with a position well inside the room boundary, rebuild, then fine-tune by viewing the web twin.

The build stops with a clear message if a room code does not exist, or if a printable item is not standing on its room's tray floor (for example, placed inside the lift shaft, the atrium void or a wall). Move it and rebuild; nothing is printed in mid-air.

## Ready-to-use shapes

| `shape` | Good for | Main parameters |
| --- | --- | --- |
| `sofa` | Sofas, armchair-like lounge pieces | `width_m`, `depth_m`, `height_m` |
| `screen` | Wall-mounted TV or information display | `width_m`, `height_m`, `sill_m`, `depth_m` |
| `swing` | Robust 1:1000 playground swing | `width_m`, `depth_m`, `height_m`, `member_m` |
| `box` | Cabinets, plinths, bins or other simple blocks | `width_m`, `depth_m`, `height_m` |

If a new shape is required—for example, a bike rack or a detailed play structure—it is added once to `src/placeables.py` by someone comfortable with the geometry code. It then becomes available to every future JSON asset and every exporter.

## Add a sofa to a room

1. In `assets`, copy the `lounge_sofa` definition and rename it if the new sofa has a different size or colour. If it is identical, reuse `lounge_sofa` without copying it.
2. In `placements`, copy `example-lounge-sofa`.
3. Give it a unique `id`, change `room`, `x_m`, `y_m` and `facing`, and remove `"enabled": false` (or set it to `true`).
4. Rebuild the outputs below.

Because the sofa has `catalogue_type: "sofa"`, it is added to `Costing/items.csv` automatically. Because it is `printable: true`, it is fused into that room's 1:100 furniture tray. It also appears in the web twin, coloured with its `colour` value.

For a decorative object that should not be costed, omit `catalogue_type`. It can still appear in the web twin and, when `printable` is true, in the tray; it simply has no row in the room-cost schedule.

## Add a TV or screen to a room

Repeat the sofa process but use the `wall_screen` asset. It uses the existing `display_screen` catalogue entry, so the schedule includes its purchase cost and electricity use.

Keep `"printable": false` for screens. A wall-mounted screen hangs above the floor, and the trays have no walls to hold it, so a printable screen would start in mid-air; the build refuses it. It still appears in the web twin and the schedule.

## Add a swing or other site prop

Use `"target": "site"` rather than `"target": "room"` and omit `room`.

```json
{
  "id": "rain-garden-swing",
  "asset": "playground_swing",
  "target": "site",
  "x_m": 18.0,
  "y_m": 28.0
}
```

Site coordinates use the same local origin as the building. The prop is automatically placed on the LiDAR terrain height (the lowest point under it, so it never hovers above a slope). It appears in the 1:1000 site model, the web twin and the Google Earth KMZ.

The physical 1:1000 site uses the existing four-colour Bambu workflow. Therefore site props print in the proposal's orange layer; give the asset the same orange `"colour": "#E8913A"` if the digital and physical versions should visually match. A different web colour is supported, but it will not create a fifth physical filament colour automatically.

The swing's members are intentionally much thicker than a real swing: at 1:1000, a 0.8 m member is only 0.8 mm wide, which is two lines of the printer's 0.4 mm nozzle. `member_m` cannot go below 0.8. The printed swing is the frame only; the seat and hangers would start in mid-air on the printer, so they appear in the web twin and Google Earth only.

## Rebuild after editing JSON

One command refreshes everything (print STLs, print cost, room schedule, web twin, Google Earth and, if Bambu Studio is installed, the printer-ready files):

```bash
~/.venvs/heat-exchange/bin/python src/build_all.py
```

`src/placeables.py` checks the JSON before generating anything. If it reports an error, it will name the affected asset or placement and explain the expected field.

## What updates where

| Addition | Cost schedule | 1:100 room tray | 1:1000 site model | Web twin | Google Earth |
| --- | --- | --- | --- | --- | --- |
| Printable room item, e.g. sofa | Yes | Yes | No | Yes | Building shell only; indoor furniture remains hidden |
| Non-printable room item, e.g. TV | Yes | No | No | Yes | Building shell only; indoor furniture remains hidden |
| Site prop, e.g. swing | No | No | Yes, proposal-orange layer | Yes | Yes |

Google Earth deliberately leaves indoor furniture out so the building remains easy to read at campus scale. Outdoor site props are included.
