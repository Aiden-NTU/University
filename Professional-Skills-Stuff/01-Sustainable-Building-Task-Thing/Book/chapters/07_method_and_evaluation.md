---
authors:
---
# Method, evaluation and conclusion

## How the project was developed

Once the team had chosen the Clifton car park, the lead engineer needed a way to put a real site
into a 3D model. OpenStreetMap alone gives plan outlines but not terrain elevation [@osm]. After
testing options, we used **Terra Printer**, which builds 3D terrain from open map and elevation
sources for any place on Earth [@terraprinter]. From that export we flattened the car park,
copied trees and greenery from the surroundings into the cleared area, and blocked out a building
using forms taken from other campus buildings plus simple solids.

That gave a sketch of landscape and massing. For finer detail we moved the geometry into
**Python**: rooms and structure as coordinates, then reusable objects (sofas, chairs, screens,
solar panels) placed wherever needed. The printable files were produced through the **Bambu Studio**
console API (Linux community build), iterating until the parts were sliceable. We printed the
**site at 1:1000** and the **building at 1:100**. Combined print time is about **33 hours** and
about **1.1 kg** of PLA across four colours (about £21 of filament at £20/kg).

As a team we were stronger at programming than at interactive CAD. Driving the model from code
let us change dimensions once and regenerate prints, schedules and the web twin together. The
trade-off is clear: placing objects by coordinates is slower than dragging in a GUI, and a small
code error can corrupt an export—though the slicer usually warns before a bad print.

For the showcase poster we avoided a stack of paper boards. Each side of the 1:1000 site model
has a slot for a **laser-engraved plywood wall** carrying key facts and the QR code to the web
twin. That uses NTU workshop resources and folds the poster into the model itself. Overall, the
method moved from a rough idea to printable site and building models within a few days of focused
work.

Table: Contributions (edit names)

| Section | Lead | Role |
| --- | --- | --- |
| [[Introduction and site]] | *to be added* | *…* |
| [[Design concept]] | *to be added* | Design Lead |
| [[Sustainable technologies]] | *to be added* | *…* |
| [[Materials, research and the SDGs]] | *to be added* | Sustainability & Research Lead |
| [[Cost analysis]] | *to be added* | Cost & Resource Coordinator |
| Physical / web models | *to be added* | Engineering / Visual Communications |

## Benefits and drawbacks

**Benefits.** Students gain a learning hub with quiet and social options; the campus gains green
space aligned with its Green Flag landscape [@ntu_greenflag2026]; energy systems demonstrate PV
and heat reuse; and the project is explainable through physical models, a walkable web twin,
Google Earth and engraved walls.

**Drawbacks.** Capital cost is high; parking income is not fully replaced by PV value; the west
glazing needs careful summer shading; hempcrete and K-Briq detailing must be signed off by a
structural engineer; and server electricity dwarfs roof generation if counted against the building
alone.

**Limitations.** Heating demand and heat-pump size are not yet modelled; many plant prices are
provisional; fit-out rates are indicative; and performance in use is unproven. Those limits bound
any net-zero claim at the showcase.

## Conclusion

The Heat Exchange proposes a two-storey timber learning hub on the Clifton Campus car park,
with roof PV, waste-heat recovery, and a landscape that replaces hardstanding. It addresses SDG
bands 3–5, 6–9 and 13–17 through education, infrastructure and climate-focused choices [@un2015],
within a hypothetical budget of about £2.4 million. Next steps are a monthly energy model, supplier
quotes for plant, and confirmation of materials detailing with estates. The plywood walls and
models carry the quick story; this Design Outline is the referenced account required by the brief
[@ntu_brief].
