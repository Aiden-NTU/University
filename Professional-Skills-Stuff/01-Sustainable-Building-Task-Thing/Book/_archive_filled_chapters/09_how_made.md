---
authors:
---
# How we made it

## One model, many outputs

Instead of drawing the building separately for each output, we described it once, in code, and
generated everything else from that description. The design lives in a set of Python scripts
[@python]: one file holds the key dimensions (the grid, floor heights, wall build-up, overhang
depth, solar panel layout and so on), and others turn those numbers into geometry, schedules and
drawings.

Running a single build command regenerates every output:

Table: What the build produces from the design model

| Output | Used for |
| --- | --- |
| 1:1000 site model and 1:100 building model (STL, sliced for Bambu Lab printers) | Physical models at the poster event |
| Room schedule and itemised fit-out costs | [[Cost analysis]] and [[Itemised fit-out schedule]] |
| Building metrics: areas, volumes, glazing, PV, shading | Numbers throughout this document |
| Web digital twin | Interactive model, linked from the poster by QR code |
| Google Earth model | Seeing the building in its real context |
| Laser-cut poster walls | The display around the site model |
| This document's tables and charts | This Design Outline |

The advantage is consistency. When we changed the overhang depth or moved a room, every number
on the poster, in the models and in this document changed with it, so they can never disagree.

## Site data

The site model starts from real survey data. Ground levels come from the Environment Agency's 1 m
LiDAR terrain model [@ea_dtm], and the heights of trees and existing buildings from the
difference between its surface and terrain models [@ea_dsm]. Roads, paths and building outlines
come from OpenStreetMap [@osm], and the aerial photograph from Esri World Imagery
[@esri_imagery].

## 3D-printed models

The models were printed in PLA on the university's Bambu Lab printers, after slicing in Bambu
Studio [@bambu]. The 1:1000 site model prints in four colours: green terrain, grey roads and
paths, white existing buildings and dark green trees, with the proposed building in orange.
The 1:100 building comes apart floor by floor on locating pegs, and each room has a printed
furniture tray, so visitors can lift the roof off and look inside.

<!-- auto:print_jobs -->
Table: 3D print jobs as sliced in Bambu Studio (X1 Carbon)

| Print job | Hours | PLA (g) | Cost at £20/kg |
| --- | ---: | ---: | ---: |
| Site north half (4 colours) | 6.8 | 193 | £4 |
| Site south half (4 colours) | 5.6 | 172 | £3 |
| Ground floor + cycle hub - white | 4.5 | 205 | £4 |
| First floor - white | 4.0 | 178 | £4 |
| Roofs - grey | 3.8 | 195 | £4 |
| PV strips - dark blue | 0.9 | 22 | £0 |
| Green roof - green | 0.3 | 9 | £0 |
| Furniture trays 1 - light grey | 3.1 | 37 | £1 |
| Furniture trays 2 - light grey | 2.5 | 39 | £1 |
| Furniture trays 3 - light grey | 1.4 | 22 | £0 |
| **Total** | **32.9** | **1,072** | **£21** |
<!-- /auto -->

![Furniture trays at 1:100: each room's furniture printed on a thin floor plate](../../Design/renders/print_furniture_trays.png){: style="width:120mm"}

## The web digital twin

The digital twin is a 3D model of the building and site that runs in any web browser, built
with the three.js library [@threejs]. Visitors can orbit the site or walk through the rooms,
switch between the existing car park and the proposal, and move the sun through the day and
year to see the shading. Clicking a room shows its lighting design and fit-out list. The poster
links to it with a QR code.

![The web twin: the proposed site with the sun set to 1 pm in June](../../Design/renders/twin_site_overview.png)

## The poster walls

Around the site model stand four removable plywood walls, laser-engraved with a short version
of this document: what the building is, where its energy comes from, how it is built and how it
meets the SDGs. Each wall slots into a groove in the rim of the site model and can be lifted out
to see the model inside. Their text is filled in from the same design numbers as this document.

![The four engraved poster walls, laid out flat](../../Poster/laser_wall/preview.svg)

## Google Earth

The building and the proposed landscape were also exported as a Google Earth model, placed at
its real location on the campus, which is how the image on the cover was made.

## This document

This Design Outline is written in plain-text Markdown files, one per section, so each team
member can write their own part. A script assembles them into this PDF. It fills in the current
design numbers and the generated tables and charts, numbers the sections, figures and tables,
and builds the Harvard reference list from the sources cited in the text. The written text is
never overwritten by a rebuild; only the generated tables and charts are refreshed.
