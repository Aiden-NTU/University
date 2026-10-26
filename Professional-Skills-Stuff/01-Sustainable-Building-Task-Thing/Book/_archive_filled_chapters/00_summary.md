---
authors:
numbered: no
---
# Summary

The Heat Exchange is a two-storey timber learning hub for Nottingham Trent University's Clifton
Campus. It replaces most of the Students' Car Park with a {{gia_m2}} m² building, a meadow, a
pond and a rain garden, and keeps a smaller car park under solar canopies. Inside there is a
café and entrance atrium, a flexible teaching hall, a makerspace, a quiet library, four group
study pods and a cycle hub with showers: {{seats}} seats in all.

The name describes the main idea. Most buildings pay to cool their computers and then pay
again to heat their rooms. Here, a small edge server room is the boiler. Its waste heat,
about {{server_heat_mwh}} MWh a year, is collected in water and raised to a useful temperature by
a heat pump. A sawtooth roof carries {{pv_modules}} solar panels ({{pv_kwp}} kWp) on its south
slopes and lets soft north light into the first floor. LED lighting that responds to daylight
and occupancy uses {{lighting_saving_pct}}% less energy than a conventional fit-out.

The design addresses six of the United Nations Sustainable Development Goals [@un2015]: mainly
Goal 7 (clean energy), Goal 9 (innovation and infrastructure), Goal 12 (responsible consumption)
and Goal 13 (climate action), and also Goal 4 (quality education) and Goal 11 (sustainable
communities).

<!-- auto:key_facts -->
Table: Key figures, generated from the design model

| Quantity | Value | Source |
| --- | --- | --- |
| Gross internal area | 720 m² | 3D model |
| Main block | 24 × 14.4 m, 2 storeys at 3.6 m | Structural grid |
| Cycle hub (single storey) | 6 × 9.6 m | Structural grid |
| Rooms | 21 (plus corridors) | Room schedule |
| Heated volume | 2,875 m³ | 3D model |
| Envelope area | 1,244 m² | 3D model |
| Surface area to volume ratio | 0.43 m⁻¹ | Envelope ÷ volume |
| Window-to-wall ratio N / E / S / W | 20% / 27% / 49% / 45% | 3D model |
| Roof PV | 114 modules, 49 kWp at 25° | 3D model |
| PV yield | 46,924 kWh/yr (958 kWh/kWp) | PVGIS [@pvgis] |
| Lighting energy, design vs baseline | 4,021 vs 18,923 kWh/yr (−79%) | Lumen method |
| Fit-out, priced items | £88,270 (£123/m²) | Costing schedule |
<!-- /auto -->

## How to read this document

This Design Outline is the detailed companion to our poster display. The four engraved
plywood walls around the site model give the quick read, and this document explains how each
feature works, what it costs, where the numbers come from and which sources support them.

Every number in the tables and charts is calculated from the same 3D design model that produced
our printed models, web twin and poster. When the design changes, the document is rebuilt and
the figures update to match; [[How we made it]] explains how.

![Scan to walk around the building in the web twin (https://aiden12343.github.io/heat-exchange-twin/)](../../Poster/web_twin_qr.svg){: style="width:34mm"}

!!! note "A note on honesty"
    The building is designed to be net zero, but we have not yet proved it. The server room uses
    more electricity than the roof can generate, and the heating demand still needs a full
    energy model. [[The energy balance so far]] sets out what is known, and
    [[Limitations and next steps]] lists the work still to do.
