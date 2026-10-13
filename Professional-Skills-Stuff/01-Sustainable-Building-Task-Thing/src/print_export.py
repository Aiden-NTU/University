"""Write the printable STL files.

Model/print/site/        1:1000 site model, one STL per colour (load all together in Bambu Studio)
Model/print/building/    1:100 lift-off building: ground floor, first floor, roof (+PV), cycle hub
Model/print/trays_sla/   1:100 furniture trays for the Formlabs printer
Model/print/trays_fdm/   1:100 trays of chunky plant/sanitary items for the Bambu printer
"""
import re
import shutil

import building as B
import config as C
import site_model as S
from geom import scaled, union

BUILD_MM = 1000 / C.BUILDING_SCALE
SITE_MM = 1000 / C.SITE_SCALE


def _name(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _write(mesh, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)
    return path


def export_site():
    parts, base_z = S.site_print_solids()
    cx, cy = C.SITE_CENTRE_LOCAL
    out = C.OUT_PRINT / "site"
    files = []
    for key, label in (("terrain", "1_terrain_green"), ("roads", "2_roads_paths_grey"),
                       ("context", "3_existing_buildings_white"), ("trees", "4_trees_dark_green"),
                       ("proposal", "5_proposal_orange")):
        m = parts[key]
        if m.is_empty():
            continue
        t = scaled(m, SITE_MM, (-cx, -cy, -base_z))
        files.append(_write(t, out / f"site_1to{C.SITE_SCALE}_{label}.stl"))
    single = scaled(union(list(parts.values())), SITE_MM, (-cx, -cy, -base_z))
    files.append(_write(single, out / f"site_1to{C.SITE_SCALE}_single_colour.stl"))
    return files


def building_parts():
    """{file_stem: (Manifold, z_offset_group)} - parts in a group share a z offset (colour pairs)."""
    gf = union([B.slab("GF"), B.external_walls("GF")[0], B.internal_walls("GF"), B.stair(), B.pegs(B.WALL_H)])
    ff = union([B.slab("FF"), B.external_walls("FF")[0], B.internal_walls("FF"), B.balustrades("FF"),
                B.pegs(B.H + B.WALL_H)]) - B.pegs(B.WALL_H, holes=True)
    roof, pv = B.roof_print()
    roof = roof - B.pegs(B.H + B.WALL_H, holes=True)
    ax = B.annex()
    return {
        "1_ground_floor": (gf, "gf"),
        "2_first_floor": (ff, "ff"),
        "3_roof": (roof, "roof"),
        "3_roof_pv_strips_dark_blue": (pv, "pv"),
        "4_cycle_hub": (union([ax["floor"], ax["walls"]]), "annex"),
        "5_cycle_hub_roof": (ax["roof"], "annex_roof"),
        "5_cycle_hub_green_roof": (ax["green"], "green_roof"),
    }


def export_building():
    parts = building_parts()
    zmin = {}
    for m, grp in parts.values():
        zmin[grp] = min(zmin.get(grp, 1e9), m.bounding_box()[2])
    cx, cy = B.L / 2, B.D / 2
    out = C.OUT_PRINT / "building"
    return [_write(scaled(m, BUILD_MM, (-cx, -cy, -zmin[grp])),
                   out / f"building_1to{C.BUILDING_SCALE}_{stem}.stl")
            for stem, (m, grp) in parts.items()]


def export_trays():
    files = []
    for room in B.ROOMS:
        if not any(pr for _, _, pr in B.furniture(room["id"])):
            continue
        m = B.tray(room)
        bb = m.bounding_box()
        off = (-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2])
        sub = "trays_sla" if room["tray_process"] == "SLA" else "trays_fdm"
        files.append(_write(scaled(m, BUILD_MM, off),
                            C.OUT_PRINT / sub / f"{room['id']}_{_name(room['name'])}.stl"))
    return files


def export_all():
    if C.OUT_PRINT.exists():
        shutil.rmtree(C.OUT_PRINT)
    return export_site() + export_building() + export_trays()


if __name__ == "__main__":
    for f in export_all():
        print(f.relative_to(C.ROOT))
