# Project guide: The Heat Exchange

## What this repository is for

This repository is the digital source package for **The Heat Exchange**, a proposed two-storey, net-zero learning hub at NTU Clifton Campus. It is a Python-led parametric design project rather than a conventional web application.

One shared design model produces several presentation and fabrication outputs:

| Output | Purpose | Main location |
| --- | --- | --- |
| 1:1000 site and 1:100 building models | Physical demonstration model | `Model/print/`, then `Model/bambu/` |
| Costed room schedule | Fit-out quantities, costs and running-energy estimates | `Costing/items.csv` |
| Digital twin | Walkable browser presentation of the proposal | `Web-Twin/` |
| Google Earth model | Real-world location and campus context | `Design/exports/heat_exchange_google_earth.kmz` |
| Metrics and render assets | Poster and design-outline evidence | `Design/exports/`, `Design/renders/` |

The important principle is: **edit the design inputs, then regenerate the outputs**. Do not hand-edit a generated STL, JSON file, or the room-cost spreadsheet if the change originates in the design; the next rebuild would overwrite it.

## How the project fits together

`src/config.py` is the central place for site coordinates, building dimensions, print settings and headline assumptions. `src/building.py` turns those dimensions into the building geometry, room definitions, openings, furniture and calculated metrics. The other modules reuse that same model for their particular output.

```text
config.py ──► building.py ──► print_export.py ──► STL files ──► bambu.py ──► printer projects/jobs
     │             │
     │             ├────────► schedule.py ──────► Costing/items.csv
     │             │                                  │
     │             └────────► web_export.py ──────► Web-Twin/data/
     │                                                  │
site_model.py ◄── site data cache ──────────────────────┤
     │                                                  └── earth_export.py ─► Google Earth KMZ
     └── fetch_site.py ──► OpenStreetMap, LiDAR, aerial imagery
```

This reuse is deliberate. For example, a room's area and furniture definition feed both the printable furniture tray and the web twin's room panel. A change made in one source therefore remains consistent across the physical model, digital twin and cost schedule after a rebuild.

## Repository map

| Location | What is in it | Usually edit it? |
| --- | --- | --- |
| `src/config.py` | Shared design parameters and assumptions | Yes, for dimensions, coordinates, print settings and headline rates |
| `src/building.py` | Parametric building, room list, openings, furniture and metrics | Yes, for a substantial architectural or fit-out change |
| `src/site_model.py` | Site context derived from source data and proposal landscaping | Yes, for site/layout logic |
| `src/fetch_site.py` | Downloads and caches OSM, Environment Agency LiDAR and aerial imagery | Rarely; normally just run it through the main build |
| `src/print_export.py` | Converts site/building geometry to scaled STL parts | No, unless changing the fabrication pipeline |
| `src/schedule.py` | Converts rooms and catalogue items into the schedule and energy estimates | No, unless changing the calculation method |
| `src/web_export.py` | Writes the 3D twin assets and its data files | No, unless changing what the twin exports |
| `src/earth_export.py` | Builds the placed Google Earth KMZ | No, unless changing the Earth export |
| `src/bambu.py` | Creates/slices Bambu Studio projects and print-card folders | Only for printer or slicing-workflow changes |
| `src/placeables.json` | Teammate-editable reusable sofas, screens and site props | Yes; see the placeable-assets guide |
| `src/placeables.py` | Validates placeable definitions and creates their geometry | Only when adding a brand-new shape type |
| `Costing/catalogue.csv` | Item descriptions, costs, power, lifespan and evidence status | Yes; replace indicative values with sourced ones |
| `Web-Twin/` | Static Three.js viewer, styles and generated `data/` assets | Edit `app.js`, `style.css` or `index.html` for viewer changes; do not edit `data/` by hand |
| `Model/bambu/` | Ready-to-print Bambu jobs, unsliced projects and print instructions | Normally consume these files rather than edit them |
| `Design/` | Exports and poster-ready images | Treat exports as generated; renders are presentation assets |
| `Poster/` | QR code, its target URL, and the laser-wall content (`laser_wall.json`) and outputs | Yes, `laser_wall.json`; see the laser wall guide |
| `src/laser_wall.py` | Fits the poster cards onto the four engraved walls and writes the laser files | Only for new card types, icons or wall geometry |
| `src/fonts/` | Open-licence fonts used by the engraved walls, charts and Design Outline | No |
| `src/project_facts.py` | The `{placeholder}` numbers shared by the walls and the Design Outline | Only to add a new number |
| `Book/chapters/`, `Book/appendices/` | The Design Outline text, one Markdown file per section | Yes; see the Design Outline guide |
| `Book/book.json`, `Book/references.json` | Cover details (team, names, roles) and the Harvard reference list | Yes |
| `src/book.py`, `src/book_blocks.py` | Builds the PDF; generated tables, charts and the PVGIS yield | Only for new generated tables or charts |

## Source data and coordinate system

The building is located on the NTU Clifton students' car park (OpenStreetMap way `29348021`). The project uses British National Grid coordinates (EPSG:27700): x increases east, y increases north, and z is metres above Ordnance Datum Newlyn.

The local origin is the building's south-west corner at BNG `(454976, 335433)`. The building's finished floor level is `55.45 m AOD`. Keeping every generator in this same local coordinate system is what lets the building sit correctly in the printed site, browser twin and Google Earth.

`fetch_site.py` downloads these inputs once and stores them in the ignored `Site/raw/` cache:

- OpenStreetMap features for buildings, roads, paths and the plot outline;
- Environment Agency 1 m DTM (bare ground) and DSM (ground plus objects) LiDAR rasters;
- Esri World Imagery tiles, resampled to the BNG grid.

The site model uses the DTM for terrain. It uses the difference between DSM and DTM to estimate surrounding building and tree heights; it does not use manually guessed context-building heights. Delete an individual cached file only when it genuinely needs downloading again.

## Design model in plain language

The main block is six 4.0 m bays by three 4.8 m bays. It has two storeys, a 3.6 m floor-to-floor height, a north-light sawtooth roof and a single-storey cycle-hub annex to the east. The south-facing roof slopes carry PV, while a south overhang shades the facade. The model includes an entrance atrium, teaching space, makerspace, library/study areas, support rooms, a server room and the cycle hub.

The proposal's sustainable-design story is encoded in the model and its assumptions:

- 49 kWp of south-facing roof PV is calculated from the PV module layout.
- An on-site edge-server room is represented in the room/fit-out model; its waste heat is intended as the heat-pump source.
- LED lighting uses a lumen-method calculation, with daylight and occupancy factors; a fluorescent no-control case provides a comparison baseline.
- The site proposal includes retained parking under solar carports, meadow, rain garden, pond and revised paths.
- The cycle-hub roof is exported as a separate green-roof print component.

Useful calculated outputs are written to `Design/exports/building_metrics.json`. They currently include 720 m² GIA, facade glazing ratios, 49.0 kWp PV capacity, shaded-depth estimates and lighting/fit-out totals.

## Rebuilding outputs

### First-time setup

Use Python 3 and keep the virtual environment outside the repository so it does not get mixed with project assets:

```bash
python3 -m venv ~/.venvs/heat-exchange
~/.venvs/heat-exchange/bin/pip install -r requirements.txt
```

The requirements provide the geometry, GIS, image, coordinate-conversion and export libraries. The initial full build needs internet access if `Site/raw/` is empty.

### Full build

```bash
~/.venvs/heat-exchange/bin/python src/build_all.py
```

This sequence:

1. obtains any missing site data;
2. recreates the STL print parts and the estimated print-cost report;
3. recreates `Costing/items.csv`;
4. writes all web-twin data assets;
5. writes the Google Earth KMZ; and
6. if Bambu Studio is installed through Flatpak, rebuilds sliced projects and reports;
7. refits and writes the laser-engraved poster wall; and
8. refreshes the generated tables and charts in the Design Outline and writes its PDF, leaving
   the written text untouched.

The site-data cache makes later builds much faster and avoids repeated downloads.

### Faster or targeted commands

| Need | Command | What changes |
| --- | --- | --- |
| Refresh the schedule only | `python3 src/schedule.py` | `Costing/items.csv` |
| Refresh the browser-twin data and metrics | `python3 src/web_export.py` | `Web-Twin/data/`, `building_metrics.json`, schedule |
| Refresh the Earth model | `python3 src/earth_export.py` | KMZ in `Design/exports/` |
| Refresh raw print STLs and print estimate | `python3 src/print_export.py` then `python3 src/print_cost.py` | `Model/print/` |
| Skip all print work during a general rebuild | `python3 src/build_all.py --skip-print` | Schedule, web data and KMZ only |
| Re-slice Bambu jobs after STL changes | `python3 src/bambu.py` | `Model/bambu/` outputs |
| Fetch/re-fetch missing source data | `python3 src/fetch_site.py` | `Site/raw/` cache |
| Refit the poster wall after editing its cards | `python3 src/laser_wall.py` | `Poster/laser_wall/` |
| Rebuild the Design Outline after writing | `python3 src/book.py` | Generated blocks in `Book/`, the PDF |

Run targeted scripts from the repository root. They import neighbouring modules by name, so running them from another directory is not supported.

### Before committing regenerated work

Use a short consistency check instead of relying only on visual inspection:

```bash
python3 -m compileall -q src
git diff --check
git status --short
```

Then inspect the relevant deliverable: open the web twin, check the room schedule row(s) affected, or load the STL/KMZ. A geometry or print-settings change should also be checked in Bambu Studio before relying on a newly sliced job.

## Safe ways to make common changes

### Change a shared assumption or dimension

Edit `src/config.py`. It is the best place for bay sizes, floor heights, site placement, print scale, filament rates, electricity price, carbon factor and similar global parameters. Rebuild all outputs afterwards because this file is widely used.

### Change the room layout, openings or furniture

Edit the relevant tables and helpers in `src/building.py`:

- `ROOMS` supplies the room identity, use, target lux level, operating hours, lighting-control factors and tray-print process.
- `OPENINGS`, internal-wall and door definitions supply envelope/interior geometry.
- `furniture()` supplies the item types and 3D representations for each room.

This will affect rooms in the twin, the cost schedule, printable trays and potentially calculated areas and lighting loads. Run the full build, or at least refresh both print and web/schedule outputs.

### Update a supplier cost or product specification

Edit the appropriate row in `Costing/catalogue.csv`, including the `source` and `cost_status` fields. The schedule multiplies the room-level quantities by these values and records power, replacement and operating estimates. Rebuild with `python3 src/schedule.py` (or run the full build).

The currently marked **indicative** values are placeholders, not procurement-ready prices. They should be replaced with current suppliers' figures and an access date before being used as evidence in the design outline.

### Change the site landscape or carports

Edit `CARPORT_ROWS` in `src/config.py` for carport footprints, and the proposal helpers in `src/site_model.py` for paving, rain garden, pond and meadow logic. These changes flow into the printed site, web-twin proposed texture and Google Earth overlay.

### Change the web-twin interface

Edit `Web-Twin/index.html`, `Web-Twin/style.css` and `Web-Twin/app.js`. This is intentionally a simple static Three.js site: there is no Node package installation or bundler. The page imports Three.js from a CDN and fetches the files below `Web-Twin/data/`.

Avoid hard-coding a room metric or building property in `app.js` when it can come from the generated `rooms.json`; this keeps the panel aligned with the schedule.

### Add a reusable sofa, screen or landscape prop

Use [`src/placeables.json`](../src/placeables.json), rather than changing each exporter. An asset defines its shape, colour, dimensions and print/schedule behaviour once; placement rows then put it in one or more rooms or at site coordinates. The same enabled placement flows to the relevant schedule, printable model, web twin and Google Earth export. See the [placeable-assets guide](PLACEABLE_ASSETS.md) for copy-and-edit examples and its print-colour limits.

### Change a printer, slicing preset or print layout

Edit `src/bambu.py`, not the `.gcode.3mf` package directly. The script describes Bambu printer profiles, materials, plates, colour mapping and which jobs belong on each campus's SD card. It needs Bambu Studio installed via Flatpak:

```bash
flatpak install --user flathub com.bambulab.BambuStudio
python3 src/bambu.py
```

The existing print packages are already ready to use. See [the printing guide](../Model/bambu/README.md) and [the print plan](../Model/bambu/PRINT_PLAN.md) before changing the physical-model workflow.

## Web twin: data contract and local preview

Serve `Web-Twin/` over HTTP rather than opening `index.html` directly; browser fetch requests for the data files commonly fail from a `file:` URL.

```bash
python3 -m http.server 8000 -d Web-Twin
```

Open <http://localhost:8000>. The viewer supports orbit and walk modes, existing/proposed site imagery, roof/first-floor visibility controls, location-based sun/shadow settings and room selection.

The generated assets have clear responsibilities:

| Asset | Contents | Used by |
| --- | --- | --- |
| `building.glb` | Detailed building, furniture and solar-carport geometry | Building display, walking/collision and room picking |
| `terrain.bin` + `terrain.json` | 2 m height grid and its placement metadata | Landscape mesh |
| `context.json` | Simplified neighbouring buildings and trees | Campus context |
| `aerial_existing.jpg` | Source aerial image | Existing-site mode |
| `aerial_proposed.jpg` | Aerial image painted with the proposed landscape | Proposed-site mode |
| `rooms.json` | Room schedule, metrics, assumptions, totals and credits | Room and project-information panels |

Adding `?debug` to the hosted URL exposes `window.twin`, which is useful for scripted checks during development.

## Printing and presentation outputs

There are two model scales:

- **1:1000 site:** terrain, roads/paths, existing buildings, trees and the proposal are exported as separate colour layers. A one-colour fallback is also generated. The intended four-colour site is split into north and south halves to keep each job within a staffed lab day.
- **1:100 building:** ground floor, first floor, main roof/PV strips, and cycle-hub components are separate lift-off parts. Furniture is generated as room-specific trays that drop into the model.

`Model/print/` contains the raw STLs. `Model/bambu/` contains Bambu Studio projects, printer-specific sliced jobs, bed thumbnails, reporting and campus SD-card folders. The latter is the folder to use for actual printing; it documents colour, printer and assembly decisions already made for the project.

For a quick browser inspection of the STL files:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/Model/preview.html>.

The poster QR code is generated separately so it can follow the final hosting location:

```bash
python3 src/make_qr.py https://<user>.github.io/<repository>/
```

This writes the SVG, PNG and recorded URL to `Poster/`. Prefer the SVG when placing it on the poster, and test the code from the expected viewing distance.

The poster can also be engraved into four removable plywood walls that stand in a slot round the rim of the site model; the same QR address is engraved into them. The slot is sized from `WALL_PLY_MM` in `src/config.py`, so measure the ply before printing the site. The [laser wall guide](LASER_WALL.md) covers adding cards, the laser files and assembly.

## Known boundaries of the model

This project is a coordinated design/presentation model, not a signed-off engineering design. In particular:

- LiDAR and OpenStreetMap provide a strong site-context model, but should still be checked against a current survey for construction decisions.
- The server heat, electricity tariff, grid-carbon factor, print pricing and catalogue costs are explicitly editable assumptions. They need current cited evidence.
- The room schedule estimates lighting and fit-out loads; it is not a full thermal or annual building-energy simulation.
- The Google Earth landscape overlay is draped onto Google's campus imagery/terrain. It cannot remove every existing 3D object at the plot edge.
- The browser twin is a presentation viewer. Its collision and sunlight behaviour is useful for explanation, not a substitute for compliance analysis.
- Any new fabrication geometry needs a slicer fit check, especially clearances, part orientation, nozzle compatibility and filament mapping.

## Suggested team workflow

1. Agree the design change and identify whether it belongs in configuration, building/site geometry, catalogue data or the viewer.
2. Make the source change in one focused commit; do not edit derivatives first.
3. Run the smallest rebuild that covers the affected deliverables. Use the full build for cross-cutting geometry changes.
4. Check the changed output in the medium in which it will be used: spreadsheet, browser, Google Earth or Bambu Studio.
5. Update evidence and presentation materials, including citations for any changed assumption.
6. Review `git diff` before committing. The raw source cache is intentionally ignored, while the curated deliverables in the repository can be shared and presented without a rebuild.

For a quick project introduction, setup command and presentation instructions, start with the [root README](../README.md). This guide is the reference for understanding and changing the pipeline behind it.
