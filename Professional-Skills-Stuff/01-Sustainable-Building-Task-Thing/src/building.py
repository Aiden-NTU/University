"""Parametric model of "The Heat Exchange".

Local coordinates in metres: x east, y north, origin = south-west corner of the main block,
z = 0 at ground-floor finished floor level (config.FFL above Ordnance Datum).

The main block is 6 x 3 structural bays (4.0 m x 4.8 m) on two storeys with a north-light
sawtooth roof whose south slopes carry the PV. A single-storey cycle hub (the annex) sits on
the east end. Everything the printed models, the web twin and the room schedule need is
generated from the tables in this file, so changing a dimension here updates all outputs.
"""
import math

from shapely.geometry import MultiPolygon, Polygon, box as rect
from shapely.ops import unary_union

import config as C
import placeables as P
from geom import EMPTY, box, cylinder, prism, profile_x, union

L, D = C.LENGTH, C.DEPTH
H, S = C.FLOOR_TO_FLOOR, C.SLAB
T, t = C.EXT_WALL, C.INT_WALL
OH = C.SOUTH_OVERHANG
WALL_H = H - S                                  # wall height under the slab above
LEVEL_Z = {"GF": 0.0, "FF": H}
ROOF_Z = 2 * H                                  # top of roof structure line
TOOTH = C.BAY_Y
RISE = TOOTH * math.tan(math.radians(C.SAWTOOTH_TILT_DEG))
FINISH = 0.05                                   # floor-finish layer = printed furniture tray

AX0, AY0 = L, D - C.ANNEX_D                     # annex south-west corner
AX1, AY1 = L + C.ANNEX_W, D
ANNEX_H = 3.6

FOOTPRINT_MAIN = rect(0, 0, L, D)
FOOTPRINT_ANNEX = rect(AX0, AY0, AX1, AY1)
FOOTPRINT = unary_union([FOOTPRINT_MAIN, FOOTPRINT_ANNEX])
ENTRANCE_XY = (2.0, -1.0)

VOID = rect(0, 0, 6.0, 4.8)                     # double-height atrium over the entrance
LIFT = rect(6.0, 4.8, 8.0, 7.0)
STAIR_X0, STAIR_Y0, STAIR_Y1 = 0.87, 3.3, 4.8   # straight flight rising west -> east
RISER, GOING, N_RISERS = 0.18, 0.27, 20

# ---------------------------------------------------------------------------------------
# Openings in external walls: (level, face, start, end, sill, head) in metres.
# Faces: S/N run along x, W/E run along y. Sill/head are above that level's floor.
# ---------------------------------------------------------------------------------------
OPENINGS = [
    # South: full-height glazed atrium, deep-set study/teaching windows below the overhang
    ("GF", "S", 0.5, 3.6, 0.0, 3.0), ("GF", "S", 4.4, 7.6, 0.0, 3.0),
    ("GF", "S", 8.4, 11.6, 0.8, 3.0), ("GF", "S", 12.4, 15.6, 0.8, 3.0),
    ("GF", "S", 16.4, 19.6, 0.8, 3.0), ("GF", "S", 20.4, 23.6, 0.8, 3.0),
    ("FF", "S", 0.5, 3.6, 0.0, 3.0), ("FF", "S", 4.4, 7.6, 0.6, 3.0),
    ("FF", "S", 8.4, 11.6, 0.6, 3.0), ("FF", "S", 12.4, 15.6, 0.6, 3.0),
    ("FF", "S", 16.4, 19.6, 0.6, 3.0), ("FF", "S", 20.4, 23.6, 0.6, 3.0),
    # North: smaller openings to limit heat loss; none in the server room (security, no gains)
    ("GF", "N", 0.8, 3.2, 1.6, 2.6), ("GF", "N", 4.8, 7.2, 0.9, 2.4),
    ("GF", "N", 12.8, 15.2, 1.8, 2.8), ("GF", "N", 20.8, 23.2, 1.8, 2.6),
    ("FF", "N", 0.8, 3.2, 1.6, 2.6), ("FF", "N", 4.8, 7.2, 1.0, 2.6),
    ("FF", "N", 8.4, 9.6, 0.8, 2.6), ("FF", "N", 10.4, 11.6, 0.8, 2.6),
    ("FF", "N", 12.4, 13.6, 0.8, 2.6), ("FF", "N", 14.4, 15.6, 0.8, 2.6),
    ("FF", "N", 16.6, 19.4, 0.8, 2.6), ("FF", "N", 20.6, 23.4, 0.8, 2.6),
    # West: glazed corner facing the campus approach
    ("GF", "W", 0.6, 4.2, 0.0, 3.0), ("GF", "W", 5.4, 8.8, 0.0, 3.0), ("GF", "W", 10.4, 13.6, 1.6, 2.6),
    ("FF", "W", 0.6, 4.2, 0.0, 3.0), ("FF", "W", 5.4, 8.8, 0.6, 3.0), ("FF", "W", 10.4, 13.6, 1.6, 2.6),
    # East: makerspace window, corridor door into the cycle hub, first-floor offices above the annex
    ("GF", "E", 0.6, 4.2, 0.8, 3.0), ("GF", "E", 8.25, 9.45, 0.0, 2.4),
    ("FF", "E", 0.6, 3.6, 0.6, 3.0), ("FF", "E", 4.4, 7.4, 0.6, 3.0), ("FF", "E", 10.4, 13.6, 0.8, 2.6),
]
DOOR_OPENINGS = {("GF", "S", 0.5), ("GF", "E", 8.25)}       # openings with no glass (doors)

# Internal walls: (level, axis, const, start, end). axis "x" = wall on line x=const.
INT_WALLS = [
    ("GF", "x", 8.0, 0.0, 8.1), ("GF", "x", 20.0, 0.0, 8.1), ("GF", "y", 8.1, 8.0, 24.0),
    ("GF", "y", 9.6, 0.0, 24.0),
    *[("GF", "x", x, 9.6, 14.4) for x in (4.0, 8.0, 12.0, 16.0, 20.0)],
    ("FF", "x", 8.0, 0.0, 8.1), ("FF", "x", 20.0, 0.0, 8.1), ("FF", "y", 8.1, 8.0, 24.0),
    ("FF", "y", 9.6, 0.0, 24.0),
    *[("FF", "x", x, 9.6, 14.4) for x in (4.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0)],
    *[(lv, "x", 6.0, 4.8, 7.0) for lv in ("GF", "FF")],     # lift shaft
    *[(lv, "y", y, 6.0, 8.0) for lv in ("GF", "FF") for y in (4.8, 7.0)],
]
# Door cuts in internal walls: (level, axis, const, start, end); 2.2 m high.
INT_DOORS = [
    ("GF", "x", 8.0, 0.9, 2.7), ("GF", "y", 8.1, 9.0, 10.0), ("GF", "y", 8.1, 21.0, 22.0),
    ("GF", "y", 9.6, 2.6, 3.6), ("GF", "y", 9.6, 4.5, 5.5), ("GF", "y", 9.6, 8.7, 10.5),
    ("GF", "y", 9.6, 12.6, 14.4), ("GF", "y", 9.6, 17.0, 18.0), ("GF", "y", 9.6, 21.0, 22.0),
    ("FF", "x", 8.0, 1.0, 2.8), ("FF", "y", 8.1, 18.6, 19.6), ("FF", "y", 8.1, 21.0, 22.0),
    ("FF", "y", 9.6, 2.6, 3.6), ("FF", "y", 9.6, 4.5, 5.5),
    *[("FF", "y", 9.6, x0, x0 + 1.0) for x0 in (8.5, 10.5, 12.5, 14.5)],
    ("FF", "y", 9.6, 17.0, 18.0), ("FF", "y", 9.6, 21.0, 22.0),
    *[(lv, "x", 6.0, 5.4, 6.4) for lv in ("GF", "FF")],     # lift doors
]
BALUSTRADES = [("FF", "y", 4.8, 0.0, 6.0), ("FF", "x", 6.0, 0.0, STAIR_Y0)]

# ---------------------------------------------------------------------------------------
# Rooms. Rectangles run to wall centre-lines / external faces; the schedule uses net areas.
# lux = maintained illuminance target (BS EN 12464-1 style values), hours = annual use,
# daylight = fraction of use hours needing electric light, occupancy = PIR saving factor.
# ---------------------------------------------------------------------------------------
ROOMS = [
    dict(id="G01", level="GF", name="Entrance Atrium & Cafe", r=(0, 0, 8, 9.6), lux=200, hours=3000,
         daylight=0.45, occupancy=1.0,
         use="Double-height glazed entrance facing the campus, cafe and reception counter.",
         notes=["Atrium + opening rooflights drive stack ventilation in summer",
                "Full-height glazing on the south-west corner, shaded by the 1.2 m slab overhang"]),
    dict(id="G02", level="GF", name="WCs (incl. accessible)", r=(0, 9.6, 4, 14.4), lux=200, hours=3000,
         daylight=1.0, occupancy=0.6, use="Accessible WC plus two cubicles; stacked under the first-floor WCs.",
         notes=["Rainwater harvested from the roof flushes the WCs",
                "Stacked wet rooms = short drainage runs and cheaper plumbing"]),
    dict(id="G03", level="GF", name="Wellbeing & Prayer Room", r=(4, 9.6, 8, 14.4), lux=200, hours=1500,
         daylight=0.8, occupancy=0.6, use="Quiet, bookable room for prayer, reflection or a break.",
         notes=["Inclusive design: supports SDG 4/11 alongside the learning spaces"]),
    dict(id="G04", level="GF", name="Flexible Teaching Hall", r=(8, 0, 20, 8.1), lux=500, hours=2600,
         daylight=0.6, occupancy=0.9, use="48-seat flat-floor teaching space, reconfigurable for events.",
         notes=["South windows sit below the overhang: summer sun blocked, winter sun admitted",
                "CO2-controlled ventilation ramps up only when the room is full"]),
    dict(id="G05", level="GF", name="Makerspace", r=(20, 0, 24, 8.1), lux=500, hours=2000,
         daylight=0.6, occupancy=0.9, use="3D printing, electronics and prototyping benches.",
         notes=["Dual aspect (south + east) daylight", "Equipment on smart plugs, auto-off out of hours"]),
    dict(id="G06", level="GF", name="Ground Floor Corridor", r=(8, 8.1, 24, 9.6), lux=100, hours=3000,
         daylight=1.0, occupancy=0.5, use="1.5 m wide accessible corridor linking the atrium to the cycle hub.",
         notes=["Width meets Approved Document M guidance for wheelchair passing"]),
    dict(id="G07", level="GF", name="Furniture Store", r=(8, 9.6, 12, 14.4), lux=100, hours=150,
         daylight=1.0, occupancy=0.5, use="Store for stacking chairs and event kit next to the hall.", notes=[]),
    dict(id="G08", level="GF", name="Plant Room", r=(12, 9.6, 16, 14.4), lux=200, hours=200,
         daylight=1.0, occupancy=0.5,
         use="Water-source heat pump, thermal store, battery, MVHR and rainwater pumps.",
         notes=["Placed directly beside the server room so recovered heat travels metres, not tens of metres"]),
    dict(id="G09", level="GF", name="Edge Server Room", r=(16, 9.6, 20, 14.4), lux=500, hours=300,
         daylight=1.0, occupancy=0.5,
         use="Small edge data centre whose waste heat feeds the heat pump and heats the building.",
         notes=["North side: no solar gain to remove", "Hot-aisle heat captured by rear-door heat exchangers",
                "Surplus heat can be exported to neighbouring campus buildings"]),
    dict(id="G10", level="GF", name="Showers & Changing", r=(20, 9.6, 24, 14.4), lux=200, hours=3000,
         daylight=0.9, occupancy=0.6, use="Showers, lockers and changing for people who cycle in.",
         notes=["Next to the cycle hub: removes the main barrier to cycling (SDG 11/13)"]),
    dict(id="G11", level="GF", name="Cycle Hub", r=(AX0, AY0, AX1, AY1), lux=100, hours=4000,
         daylight=0.5, occupancy=0.6, use="Secure two-tier cycle parking and e-bike charging under a green roof.",
         notes=["Green roof: rainwater attenuation, insulation and habitat (Biodiversity Net Gain)"]),
    dict(id="F01", level="FF", name="Breakout & Co-working Lounge", r=(0, 0, 8, 9.6), lux=300, hours=3000,
         daylight=0.4, occupancy=0.9, use="Informal lounge and co-working around the atrium.",
         notes=["Sawtooth north-lights give glare-free daylight deep into the plan",
                "Reused/refurbished furniture: lower embodied carbon (SDG 12)"]),
    dict(id="F02", level="FF", name="WCs", r=(0, 9.6, 4, 14.4), lux=200, hours=3000,
         daylight=0.8, occupancy=0.6, use="First-floor WCs stacked above the ground-floor WCs.", notes=[]),
    dict(id="F03", level="FF", name="Kitchenette", r=(4, 9.6, 8, 14.4), lux=300, hours=3000,
         daylight=0.5, occupancy=0.7, use="Tea point with water refill station.",
         notes=["Refill station reduces single-use plastic (SDG 12)"]),
    dict(id="F04", level="FF", name="Quiet Study Library", r=(8, 0, 20, 8.1), lux=500, hours=3000,
         daylight=0.35, occupancy=0.9, use="28 silent study seats: window desks, shared tables, book stacks.",
         notes=["North-light sawtooth + south windows = high daylight, low glare",
                "Daylight-linked dimming cuts lighting use by more than half"]),
    dict(id="F05", level="FF", name="Staff Office", r=(20, 0, 24, 8.1), lux=500, hours=2400,
         daylight=0.4, occupancy=0.8, use="Office for the hub's staff and student support.", notes=[]),
    dict(id="F06", level="FF", name="First Floor Corridor", r=(8, 8.1, 24, 9.6), lux=100, hours=3000,
         daylight=0.6, occupancy=0.5, use="Corridor to the study pods, control room and meeting room.", notes=[]),
    *[dict(id=f"F{7 + i:02d}", level="FF", name=f"Group Study Pod {i + 1}", r=(8 + 2 * i, 9.6, 10 + 2 * i, 14.4),
           lux=500, hours=2600, daylight=0.45, occupancy=0.6,
           use="Bookable 4-person pod with a screen for group work.",
           notes=["Booking system releases the pod (and switches it off) if nobody checks in"]) for i in range(4)],
    dict(id="F11", level="FF", name="Smart Building Control Room", r=(16, 9.6, 20, 14.4), lux=500, hours=2400,
         daylight=0.45, occupancy=0.8,
         use="Building management system head-end with a live digital-twin dashboard students can see.",
         notes=["Sensors (occupancy, CO2, temperature, light) feed one open data platform over MQTT",
                "The building is a teaching tool: live energy data on screen (SDG 4/9)"]),
    dict(id="F12", level="FF", name="Meeting Room", r=(20, 9.6, 24, 14.4), lux=500, hours=1800,
         daylight=0.45, occupancy=0.6, use="6-person meeting room with video conferencing.", notes=[]),
]
# Rooms full of chunky blocks (plant, racks, showers) print fine and far cheaper on the FDM
# printer; rooms with chairs, tables and thin racks go to resin (SLA) for the detail.
FDM_TRAYS = {"G02", "F02", "G05", "G07", "G08", "G09", "G10"}

for _r in ROOMS:
    _r["poly"] = rect(*_r["r"])
    _r["tray_process"] = "FDM" if _r["id"] in FDM_TRAYS else "SLA"
    if _r["id"] in ("G01", "F01"):
        _r["poly"] = _r["poly"].difference(LIFT)
    if _r["id"] == "F01":
        _r["poly"] = _r["poly"].difference(VOID)


# ---------------------------------------------------------------------------------------
# Walls, slabs, roof
# ---------------------------------------------------------------------------------------
def _opening_box(face, a0, a1, z0, z1, depth_pad=0.1):
    if face == "S":
        return box(a0, -depth_pad, z0, a1, T + depth_pad, z1)
    if face == "N":
        return box(a0, D - T - depth_pad, z0, a1, D + depth_pad, z1)
    if face == "W":
        return box(-depth_pad, a0, z0, T + depth_pad, a1, z1)
    return box(L - T - depth_pad, a0, z0, L + depth_pad, a1, z1)


def _glass_box(face, a0, a1, z0, z1, th=0.03):
    mid = {"S": T / 2, "N": D - T / 2, "W": T / 2, "E": L - T / 2}[face]
    if face in "SN":
        return box(a0, mid - th / 2, z0, a1, mid + th / 2, z1)
    return box(mid - th / 2, a0, z0, mid + th / 2, a1, z1)


def external_walls(level):
    z0 = LEVEL_Z[level]
    shell = box(0, 0, z0, L, D, z0 + WALL_H) - box(T, T, z0 - 1, L - T, D - T, z0 + WALL_H + 1)
    cuts, glass = [], []
    for lv, face, a0, a1, sill, head in OPENINGS:
        if lv != level:
            continue
        cuts.append(_opening_box(face, a0, a1, z0 + sill, z0 + head))
        if (lv, face, a0) not in DOOR_OPENINGS:
            glass.append(_glass_box(face, a0, a1, z0 + sill, z0 + head))
    return shell - union(cuts), union(glass)


def _wall_seg(axis, const, a0, a1, z0, z1, th):
    if axis == "x":
        return box(const - th / 2, a0, z0, const + th / 2, a1, z1)
    return box(a0, const - th / 2, z0, a1, const + th / 2, z1)


def internal_walls(level):
    z0 = LEVEL_Z[level]
    walls = union([_wall_seg(ax, c, a0, a1, z0, z0 + WALL_H, t)
                   for lv, ax, c, a0, a1 in INT_WALLS if lv == level])
    doors = union([_wall_seg(ax, c, a0, a1, z0 - 0.1, z0 + 2.2, t + 0.1)
                   for lv, ax, c, a0, a1 in INT_DOORS if lv == level])
    return walls - doors


def balustrades(level, height=1.1, th=0.12):
    z0 = LEVEL_Z[level]
    return union([_wall_seg(ax, c, a0, a1, z0, z0 + height, th)
                  for lv, ax, c, a0, a1 in BALUSTRADES if lv == level])


def stair():
    steps = []
    for i in range(N_RISERS):
        x0 = STAIR_X0 + i * GOING
        steps.append(box(x0, STAIR_Y0, 0, 6.0, STAIR_Y1, (i + 1) * RISER))
    return union(steps)


def slab(level):
    """Slab under a level (GF bears on the ground; FF has the atrium void + south overhang)."""
    if level == "GF":
        return box(0, 0, -S, L, D, 0)
    z0 = LEVEL_Z[level]
    # The slab keeps a wall-thick edge under the external walls so the first-floor piers at the
    # atrium corner bear on something (and the 1:100 first floor has no part printed in mid-air).
    return box(0, -OH, z0 - S, L, D, z0) - prism(VOID.intersection(rect(T, T, L, D)), z0 - S - 1, z0 + 1)


def _tooth_profile(k, z0=ROOF_Z):
    y0 = k * TOOTH
    return [(y0, z0), (y0 + TOOTH, z0), (y0 + TOOTH, z0 + RISE)]


def _slope_z(k, y, z0=ROOF_Z):
    return z0 + (y - k * TOOTH) * RISE / TOOTH


def pv_layout():
    """PV modules on the south slopes: list of (x0, x1, k, y0, y1) in plan."""
    pw, ph, gap, edge = 1.134, 1.722, 0.02, 0.6
    cos = math.cos(math.radians(C.SAWTOOTH_TILT_DEG))
    run = ph * cos                                   # plan depth of one module up the slope
    n_x = int((L - 2 * edge + gap) // (pw + gap))
    n_up = int((TOOTH - 0.6 + gap * cos) // (run + gap * cos))
    x_start = (L - (n_x * pw + (n_x - 1) * gap)) / 2
    mods = []
    for k in range(C.N_BAYS_Y):
        for j in range(n_up):
            y0 = k * TOOTH + 0.3 + j * (run + gap * cos)
            for i in range(n_x):
                x0 = x_start + i * (pw + gap)
                mods.append((x0, x0 + pw, k, y0, y0 + run))
    return mods


PV_MODULE_WP = 430


def roof_print(th=0.08, fit=0.015, groove=0.03):
    """Single-colour solid sawtooth with a pocket on each south slope, plus flat PV strips that print
    lying down (dark blue, module grid engraved) and glue into the pockets - no colour changes."""
    base = box(0, -OH, ROOF_Z - S, L, D, ROOF_Z)
    teeth = union([profile_x(_tooth_profile(k), 0, L) for k in range(C.N_BAYS_Y)])
    cos = math.cos(math.radians(C.SAWTOOTH_TILT_DEG))
    pockets, strips = [], []
    mods = pv_layout()
    for k in range(C.N_BAYS_Y):
        ys = [m for m in mods if m[2] == k]
        y0, y1 = min(m[3] for m in ys), max(m[4] for m in ys)
        x0, x1 = min(m[0] for m in ys), max(m[1] for m in ys)
        pockets.append(profile_x([(y0, _slope_z(k, y0) - th), (y1, _slope_z(k, y1) - th),
                                  (y1, _slope_z(k, y1) + 0.01), (y0, _slope_z(k, y0) + 0.01)], x0, x1))
        run = (y1 - y0) / cos
        oy = k * (run + 1.0)
        strip = box(x0 + fit, oy + fit, 0, x1 - fit, oy + run - fit, th)
        lines = {m[0] for m in ys} - {x0}
        cuts = [box(x - groove, oy, th - 0.02, x, oy + run, th + 0.01) for x in lines]
        cuts += [box(x0, oy + (m[3] - y0) / cos - groove / 2, th - 0.02, x1, oy + (m[3] - y0) / cos + groove / 2, th + 0.01)
                 for m in ys if m[0] == ys[0][0] and m[3] > y0 + 1e-6]
        strips.append(strip - union(cuts))
    # recessed north-light glazing band on each vertical face (reads as rooflights)
    recess = union([box(0.4, (k + 1) * TOOTH - 0.15, ROOF_Z + 0.25, L - 0.4, (k + 1) * TOOTH + 0.01,
                        ROOF_Z + RISE - 0.35) for k in range(C.N_BAYS_Y)])
    return (base + teeth) - union(pockets) - recess, union(strips)


def roof_web():
    """Hollow sawtooth so the first floor gets its north light in the web twin."""
    th = 0.25
    parts, glass = [], []
    for k in range(C.N_BAYS_Y):
        y0, y1 = k * TOOTH, (k + 1) * TOOTH
        parts.append(profile_x([(y0, ROOF_Z - S), (y1 - 0.15, _slope_z(k, y1 - 0.15) - S + th * 0.2),
                                (y1 - 0.15, _slope_z(k, y1 - 0.15) + th * 0.2), (y0, ROOF_Z)], 0, L))
        parts.append(box(0, y1 - 0.3, ROOF_Z - S, L, y1, ROOF_Z))                         # valley beam
        glass.append(box(0.3, y1 - 0.18, ROOF_Z, L - 0.3, y1 - 0.15, _slope_z(k, y1 - 0.15)))
        for xa, xb in ((0, T), (L - T, L)):                                           # gable ends
            parts.append(profile_x([(y0, ROOF_Z - S), (y1, ROOF_Z - S), (y1, _slope_z(k, y1)),
                                    (y0, ROOF_Z)], xa, xb))
    parts.append(box(0, -OH, ROOF_Z - S, L, 0.0, ROOF_Z))                                 # overhang
    pv = []
    for x0, x1, k, ya, yb in pv_layout():
        pv.append(profile_x([(ya, _slope_z(k, ya) + 0.02), (yb, _slope_z(k, yb) + 0.02),
                             (yb, _slope_z(k, yb) + 0.07), (ya, _slope_z(k, ya) + 0.07)], x0, x1))
    return union(parts), union(glass), union(pv)


def annex():
    z_top = ANNEX_H - S
    shell = box(AX0, AY0, 0, AX1, AY1, z_top) - box(AX0 - 1, AY0 + T, -1, AX1 - T, AY1 - T, z_top + 1)
    cuts = [box(AX0 + 1.0, AY0 - 0.1, 0, AX1 - 1.0, AY0 + T + 0.1, 2.6),                # cycle entrance
            box(AX1 - T - 0.1, AY0 + 1.2, 0.9, AX1 + 0.1, AY1 - 1.2, 2.8),                # east louvres
            box(AX0 + 1.0, AY1 - T - 0.1, 2.0, AX1 - 1.0, AY1 + 0.1, 2.8)]                # high windows
    walls = shell - union(cuts)
    glass = union([box(AX1 - T / 2 - 0.015, AY0 + 1.2, 0.9, AX1 - T / 2 + 0.015, AY1 - 1.2, 2.8),
                   box(AX0 + 1.0, AY1 - T / 2 - 0.015, 2.0, AX1 - 1.0, AY1 - T / 2 + 0.015, 2.8)])
    floor = box(AX0, AY0, -S, AX1, AY1, 0)
    roof = box(AX0, AY0, z_top, AX1, AY1, ANNEX_H)
    green = box(AX0 + 0.2, AY0 + 0.2, ANNEX_H, AX1 - 0.2, AY1 - 0.2, ANNEX_H + 0.15)
    return dict(floor=floor, walls=walls, glass=glass, roof=roof, green=green)


def pegs(level_top_z, holes=False):
    """Locating pegs on wall tops (or matching holes in the slab above)."""
    r = C.PEG_D_MM / 2 * C.BUILDING_SCALE / 1000
    if holes:
        r += C.HOLE_CLEARANCE_MM / 2 * C.BUILDING_SCALE / 1000
    h = C.PEG_H_MM * C.BUILDING_SCALE / 1000
    pts = [(T / 2, T / 2), (L - T / 2, T / 2), (T / 2, D - T / 2), (L - T / 2, D - T / 2), (12.0, D - T / 2)]
    z0 = level_top_z - (0.5 if holes else 0)
    return union([cylinder(x, y, z0, r, h + (1.0 if holes else 0)) for x, y in pts])


# ---------------------------------------------------------------------------------------
# Furniture (box-based so it prints cleanly in resin at 1:100)
# ---------------------------------------------------------------------------------------
def _chair(x, y, facing, seat=0.45):
    h = seat / 2
    m = box(x - h, y - h, 0, x + h, y + h, 0.45)
    bt = 0.07
    back = {"N": (x - h, y - h, x + h, y - h + bt), "S": (x - h, y + h - bt, x + h, y + h),
            "E": (x - h, y - h, x - h + bt, y + h), "W": (x + h - bt, y - h, x + h, y + h)}[facing]
    return m + box(*back[:2], 0.45, *back[2:], 0.85)


def _table(x0, y0, x1, y1, h=0.74, top=0.05, leg=0.08):
    m = box(x0, y0, h - top, x1, y1, h)
    for lx, ly in ((x0 + 0.04, y0 + 0.04), (x1 - 0.04 - leg, y0 + 0.04),
                   (x0 + 0.04, y1 - 0.04 - leg), (x1 - 0.04 - leg, y1 - 0.04 - leg)):
        m += box(lx, ly, 0, lx + leg, ly + leg, h - top)
    return m


def _block(x0, y0, x1, y1, h, z0=0.0):
    return box(x0, y0, z0, x1, y1, z0 + h)


def _sofa(x0, y0, x1, y1, facing):
    m = box(x0, y0, 0, x1, y1, 0.42)
    bd, aw = 0.2, 0.2
    if facing in "NS":
        by = (y0, y0 + bd) if facing == "N" else (y1 - bd, y1)
        m += box(x0, by[0], 0.42, x1, by[1], 0.8)
        m += box(x0, y0, 0.42, x0 + aw, y1, 0.62) + box(x1 - aw, y0, 0.42, x1, y1, 0.62)
    else:
        bx = (x0, x0 + bd) if facing == "E" else (x1 - bd, x1)
        m += box(bx[0], y0, 0.42, bx[1], y1, 0.8)
        m += box(x0, y0, 0.42, x1, y0 + aw, 0.62) + box(x0, y1 - aw, 0.42, x1, y1, 0.62)
    return m


def _cluster(cx, cy, w, d, seats_x=True):
    """Table with a chair on each side of the long axis."""
    items = [("table_cafe", _table(cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2))]
    if seats_x:
        items += [("chair_stack", _chair(cx - w / 2 - 0.3, cy, "E")), ("chair_stack", _chair(cx + w / 2 + 0.3, cy, "W"))]
    items += [("chair_stack", _chair(cx, cy - d / 2 - 0.3, "N")), ("chair_stack", _chair(cx, cy + d / 2 + 0.3, "S"))]
    return items


def legacy_furniture(room_id):
    """Built-in furniture kept for the original design; new items live in placeables.json."""
    it = []
    add = lambda kind, m, printable=True: it.append((kind, m, printable))  # noqa: E731
    if room_id == "G01":
        for cx in (1.6, 3.7, 5.8):
            for k, m in _cluster(cx, 1.6, 0.8, 0.8):
                add(k, m)
        for cx in (1.7, 4.2):
            for k, m in _cluster(cx, 6.4, 0.8, 0.8):
                add(k, m)
        add("counter", _block(7.0, 7.3, 7.6, 9.3, 1.0))
        add("display_screen", _block(T + 0.02, 9.0, T + 0.07, 9.3, 0.5, 1.4), False)
    elif room_id == "G02":
        for y in (10.3, 11.6, 13.4):
            add("wc_pan", _block(0.45, y - 0.2, 1.15, y + 0.2, 0.42))
        add("basin_counter", _block(3.2, 10.0, 3.75, 13.8, 0.85))
    elif room_id == "G03":
        add("armchair", _sofa(4.6, 12.6, 5.45, 13.45, "S"))
        add("armchair", _sofa(6.4, 12.6, 7.25, 13.45, "S"))
        add("coffee_table", _block(5.6, 11.6, 6.3, 12.3, 0.4))
        add("prayer_mat_store", _block(7.3, 10.0, 7.85, 11.2, 0.9))
    elif room_id == "G04":
        for xr in (9.6, 11.4, 13.2, 15.0, 16.8, 18.6):
            for y0, y1 in ((0.9, 2.1), (2.1, 3.3), (4.8, 6.0), (6.0, 7.2)):
                add("table_teach", _table(xr, y0, xr + 0.6, y1))
                for yc in (y0 + 0.3, y1 - 0.3):
                    add("chair_stack", _chair(xr + 0.6 + 0.28, yc, "W"))
        add("lectern", _block(8.5, 1.6, 9.0, 2.2, 1.1))
        add("display_large", _block(8.08, 3.0, 8.13, 5.0, 1.2, 1.0), False)
    elif room_id == "G05":
        for y in (2.0, 5.0):
            add("workbench", _block(21.0, y - 0.45, 23.4, y + 0.45, 0.9))
            for x in (21.4, 22.2, 23.0):
                add("stool", _block(x - 0.17, y - 0.95, x + 0.17, y - 0.61, 0.7))
        add("printer_3d", _block(20.25, 6.6, 20.85, 7.2, 0.9))
        add("printer_3d", _block(20.25, 7.25, 20.85, 7.85, 0.9))
        add("laser_cutter", _block(22.6, 6.9, 23.6, 7.9, 1.0))
    elif room_id == "G07":
        add("shelving", _block(8.3, 13.6, 11.7, 14.0, 2.0))
        for x in (8.6, 9.3, 10.0, 10.7):
            add("chair_stack_trolley", _block(x, 11.0, x + 0.5, 11.5, 1.6), False)
    elif room_id == "G08":
        add("heat_pump", _block(12.3, 12.9, 13.5, 13.9, 1.6))
        add("thermal_store", cylinder(14.6, 13.4, 0, 0.45, 2.0))
        add("battery", _block(15.0, 10.0, 15.8, 11.2, 1.9))
        add("mvhr", _block(12.3, 10.0, 13.5, 10.8, 1.8))
        add("rainwater_pumpset", _block(13.9, 10.0, 14.5, 10.6, 0.8))
    elif room_id == "G09":
        for x in (16.6, 17.3, 18.0, 18.7):
            add("server_rack", _block(x, 11.4, x + 0.6, 12.6, 2.0))
        add("cooling_distribution_unit", _block(16.4, 13.4, 17.4, 14.0, 1.8))
    elif room_id == "G10":
        for x in (20.3, 21.4):
            add("shower_cubicle", _block(x, 13.0, x + 1.0, 14.0, 2.0))
        add("bench", _block(20.6, 11.0, 22.6, 11.4, 0.45))
        add("lockers", _block(23.1, 10.0, 23.6, 13.0, 1.8))
    elif room_id == "G11":
        for x0, x1 in ((AX0 + 0.2, AX0 + 2.0), (AX1 - 2.2, AX1 - 0.4)):
            for y in [AY0 + 0.9 + 0.8 * i for i in range(10)]:
                add("bike_rack_2tier", _block(x0, y - 0.03, x1, y + 0.03, 1.1) + _block(x0, y - 0.03, x0 + 0.06, y + 0.03, 2.4))
        add("ebike_charging", _block(AX0 + 2.6, AY1 - 0.9, AX1 - 2.8, AY1 - 0.5, 1.2))
    elif room_id == "F01":
        add("sofa", _sofa(0.8, 5.2, 2.8, 6.1, "N"))
        add("sofa", _sofa(0.8, 7.5, 2.8, 8.4, "S"))
        add("coffee_table", _block(1.3, 6.4, 2.3, 7.2, 0.4))
        add("armchair", _sofa(3.6, 5.3, 4.45, 6.15, "N"))
        add("armchair", _sofa(4.8, 5.3, 5.65, 6.15, "N"))
        add("coffee_table", _block(4.1, 6.6, 5.1, 7.3, 0.4))
        add("table_bench", _table(3.6, 8.2, 5.4, 9.0))
        for x in (3.95, 4.5, 5.05):
            add("chair_stack", _chair(x, 7.85, "N"))
        for k, m in _cluster(7.0, 1.8, 0.8, 1.6, seats_x=False):
            add(k, m)
    elif room_id in ("F02",):
        for y in (10.3, 11.6, 13.4):
            add("wc_pan", _block(0.45, y - 0.2, 1.15, y + 0.2, 0.42))
        add("basin_counter", _block(3.2, 10.0, 3.75, 13.8, 0.85))
    elif room_id == "F03":
        add("kitchen_counter", _block(4.3, 13.4, 7.7, 14.0, 0.9))
        add("water_refill", _block(4.3, 10.0, 4.8, 10.5, 1.4))
        for k, m in _cluster(6.0, 11.6, 0.8, 0.8):
            add(k, m)
    elif room_id == "F04":
        for i in range(10):
            x0 = 8.45 + i * 1.15
            add("desk_study", _table(x0, 0.5, x0 + 1.05, 1.15))
            add("chair_task", _chair(x0 + 0.525, 1.45, "S"))
        for cx in (10.4, 14.0, 17.6):
            add("table_study_large", _table(cx - 1.2, 3.2, cx + 1.2, 4.4))
            for dx in (-0.8, 0.0, 0.8):
                add("chair_task", _chair(cx + dx, 2.85, "N"))
                add("chair_task", _chair(cx + dx, 4.75, "S"))
        for i in range(8):
            x0 = 8.6 + i * 1.4
            add("bookcase", _block(x0, 7.55, x0 + 1.0, 7.95, 1.8))
    elif room_id == "F05":
        for y in (1.2, 3.6):
            for x0 in (20.4, 22.25):
                add("desk_office", _table(x0, y, x0 + 1.35, y + 0.7))
                add("chair_task", _chair(x0 + 0.675, y + 1.0, "S"))
        for k, m in _cluster(22.0, 6.6, 1.2, 0.8):
            add(k, m)
    elif room_id in ("F07", "F08", "F09", "F10"):
        x = 8 + 2 * (int(room_id[1:]) - 7) + 1.0
        add("table_pod", _table(x - 0.4, 11.4, x + 0.4, 13.0))
        for y in (11.8, 12.6):
            add("chair_stack", _chair(x - 0.65, y, "E", seat=0.42))
            add("chair_stack", _chair(x + 0.65, y, "W", seat=0.42))
        add("display_screen", _block(x - 0.6, D - T - 0.06, x + 0.6, D - T - 0.01, 0.7, 1.1), False)
    elif room_id == "F11":
        add("display_wall", _block(16.3, D - T - 0.06, 19.7, D - T - 0.01, 1.1, 1.0), False)
        for x0 in (16.5, 18.1):
            add("desk_office", _table(x0, 12.6, x0 + 1.4, 13.3))
            add("chair_task", _chair(x0 + 0.7, 12.25, "N"))
        for k, m in _cluster(18.0, 10.9, 1.2, 0.8):
            add(k, m)
    elif room_id == "F12":
        add("table_meeting", _table(21.5, 10.5, 22.5, 13.1))
        for y in (11.0, 11.8, 12.6):
            add("chair_task", _chair(21.15, y, "E"))
            add("chair_task", _chair(22.85, y, "W"))
        add("display_screen", _block(21.4, D - T - 0.06, 22.6, D - T - 0.01, 0.7, 1.1), False)
    return it


def furniture(room_id):
    """List of (catalogue_type, Manifold, printable) for a room, z = 0 at top of floor finish.

    In addition to the original built-in fit-out, this reads enabled room placements from
    ``placeables.json``. This single list drives the schedule, printable furniture tray and
    web-twin room model.
    """
    unknown = {p.room for p in P.registry()[1] if p.target == "room"} - {r["id"] for r in ROOMS}
    if unknown:
        raise ValueError(f"placeables.json uses unknown room code(s) {', '.join(sorted(unknown))}; "
                         f"choose from {', '.join(r['id'] for r in ROOMS)}")
    items = legacy_furniture(room_id)
    for placement, asset, solid in P.room_assets(room_id):
        # An asset without a catalogue type is still a valid visual/printable object. The
        # private marker tells schedule.py not to invent a misleading unpriced cost row.
        kind = asset.catalogue_type or f"__placeable__{placement.id}"
        items.append((kind, solid, asset.printable))
    return items


# ---------------------------------------------------------------------------------------
# Trays (floor finish + fused furniture) and room geometry
# ---------------------------------------------------------------------------------------
def _clear_floor(level):
    """Usable floor area of a level: inside the external walls, minus walls, stair, lift, void."""
    inner = rect(T, T, L - T, D - T)
    walls = [(c - t / 2, a0, c + t / 2, a1) if ax == "x" else (a0, c - t / 2, a1, c + t / 2)
             for lv, ax, c, a0, a1 in INT_WALLS if lv == level]
    blocked = unary_union([rect(*w) for w in walls] + [LIFT])
    if level == "GF":
        blocked = unary_union([blocked, rect(STAIR_X0, STAIR_Y0, 6.0, STAIR_Y1)])
    else:
        blocked = unary_union([blocked, VOID])
    return inner.difference(blocked)


def room_floor(room, clearance=0.0):
    """Whole usable floor of a room; a MultiPolygon where the void/lift split it (F01)."""
    if room["id"] == "G11":
        p = rect(AX0, AY0 + T, AX1 - T, AY1 - T)
    else:
        p = room["poly"].intersection(_clear_floor(room["level"]))
    if clearance:
        p = p.buffer(-clearance, join_style=2)
    parts = [g for g in getattr(p, "geoms", [p]) if g.geom_type == "Polygon" and g.area > 0.25]
    return parts[0] if len(parts) == 1 else MultiPolygon(parts)


def room_floor_poly(room, clearance=0.0):
    """Largest piece of the room floor, for places that need a single outline."""
    return max(getattr(f := room_floor(room, clearance), "geoms", [f]), key=lambda g: g.area)


def room_items(room):
    z0 = LEVEL_Z[room["level"]]
    return [(k, m.translate((0, 0, z0 + FINISH)), pr) for k, m, pr in furniture(room["id"])]


def tray(room, clearance_m=0.05):
    """Printable SLA insert: thin floor plate with that room's furniture fused on top."""
    z0 = LEVEL_Z[room["level"]]
    plate = prism(room_floor(room, clearance_m), z0, z0 + FINISH)
    base = plate.project()
    furn = []
    for kind, m, printable in room_items(room):
        if not printable:
            continue
        foot = m.project()
        if (foot - base).area() > 0.5 * foot.area() or m.bounding_box()[2] > z0 + FINISH + 1e-3:
            raise ValueError(f"{room['id']}: printable '{kind}' is off the tray floor and would print "
                             "in mid-air; move it inside the room or set printable to false")
        furn.append(m)
    return union([plate] + furn)


def massing():
    """Simplified solid for the 1:1000 site model (z relative to FFL)."""
    body = box(0, 0, -1.5, L, D, ROOF_Z) + union([profile_x(_tooth_profile(k), 0, L) for k in range(C.N_BAYS_Y)])
    return body + box(AX0, AY0, -1.5, AX1, AY1, ANNEX_H + 0.15)


def metrics():
    """Areas and ratios used in the design outline and the energy model."""
    gia = 2 * L * D - VOID.area + C.ANNEX_W * C.ANNEX_D
    net = {r["id"]: round(room_floor(r).area, 1) for r in ROOMS}
    glazing = {f: 0.0 for f in "NESW"}
    for lv, face, a0, a1, sill, head in OPENINGS:
        if (lv, face, a0) not in DOOR_OPENINGS:
            glazing[face] += (a1 - a0) * (head - sill)
    wall_h = 2 * H
    gross_wall = {"S": L * wall_h, "N": L * wall_h, "W": D * wall_h, "E": D * wall_h}
    volume = L * D * (2 * H) + C.N_BAYS_Y * 0.5 * TOOTH * RISE * L
    envelope = 2 * (L * D) + 2 * (L + D) * 2 * H
    alt_summer = 90 - 52.9135 + 23.44
    alt_winter = 90 - 52.9135 - 23.44
    mods = pv_layout()
    return {
        "gross_internal_area_m2": round(gia, 1),
        "net_room_areas_m2": net,
        "glazing_area_m2": {k: round(v, 1) for k, v in glazing.items()},
        "window_to_wall_ratio": {k: round(glazing[k] / gross_wall[k], 2) for k in glazing},
        "heated_volume_m3": round(volume, 0),
        "envelope_area_m2": round(envelope, 0),
        "surface_area_to_volume": round(envelope / volume, 3),
        "pv_modules": len(mods),
        "pv_kwp": round(len(mods) * PV_MODULE_WP / 1000, 1),
        "pv_tilt_deg": C.SAWTOOTH_TILT_DEG,
        "overhang_m": OH,
        "noon_sun_altitude_deg": {"21 June": round(alt_summer, 1), "21 December": round(alt_winter, 1)},
        "overhang_shadow_depth_m": {"21 June": round(OH * math.tan(math.radians(alt_summer)), 2),
                                     "21 December": round(OH * math.tan(math.radians(alt_winter)), 2)},
    }
