"""Data for the walkable web twin (Web-Twin/data).

building.glb   detailed building + carports, nodes named LEVEL__category__room for the viewer
terrain.bin    float32 heights (2 m grid, relative to FFL) + terrain.json describing the grid
context.json   neighbouring buildings (LiDAR heights) and trees
rooms.json     room schedule, metrics and assumptions (same numbers as Costing/items.csv)
aerial_*.jpg   existing and proposed site textures
"""
import json
import math

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from pyproj import Transformer
from shapely.geometry import Polygon

import building as B
import config as C
import schedule
import site_model as S
from geom import box, prism, profile_x, to_trimesh, union

Y_UP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=float)

PALETTE = {
    "extwall": ((0.78, 0.62, 0.45, 1), 0.0, 0.85),      # larch cladding
    "intwall": ((0.93, 0.89, 0.80, 1), 0.0, 0.9),       # exposed CLT
    "slab": ((0.86, 0.80, 0.69, 1), 0.0, 0.9),
    "plinth": ((0.55, 0.55, 0.53, 1), 0.0, 0.95),
    "glass": ((0.62, 0.80, 0.90, 0.28), 0.1, 0.05),
    "roof": ((0.47, 0.50, 0.53, 1), 0.4, 0.5),          # standing-seam metal
    "pv": ((0.10, 0.15, 0.28, 1), 0.6, 0.25),
    "green": ((0.38, 0.55, 0.25, 1), 0.0, 1.0),
    "stair": ((0.72, 0.55, 0.36, 1), 0.0, 0.8),
    "balustrade": ((0.70, 0.85, 0.92, 0.35), 0.1, 0.05),
    "furn": ((0.33, 0.47, 0.42, 1), 0.0, 0.8),
    "carport": ((0.35, 0.35, 0.36, 1), 0.5, 0.5),
}
FLOOR_COLOURS = {"G04": (0.62, 0.70, 0.75), "F04": (0.70, 0.66, 0.55), "G09": (0.55, 0.57, 0.60),
                 "G08": (0.55, 0.57, 0.60), "G11": (0.50, 0.52, 0.52), "G06": (0.80, 0.78, 0.72),
                 "F06": (0.80, 0.78, 0.72)}


def _mat(kind, colour=None):
    rgba, metal, rough = PALETTE.get(kind, PALETTE["furn"])
    if colour is not None:
        rgba = (*colour, 1)
    return trimesh.visual.material.PBRMaterial(
        name=kind, baseColorFactor=[int(c * 255) for c in rgba], metallicFactor=metal, roughnessFactor=rough,
        alphaMode="BLEND" if rgba[3] < 1 else "OPAQUE", doubleSided=rgba[3] < 1)


def _add(scene, name, manifold, kind, colour=None):
    if manifold is None or manifold.is_empty():
        return
    m = to_trimesh(manifold)
    m.apply_transform(Y_UP)
    m.visual = trimesh.visual.TextureVisuals(material=_mat(kind, colour))
    scene.add_geometry(m, node_name=name, geom_name=name)


def carport_geometry():
    """Solar carport canopies over the retained parking (z relative to FFL)."""
    xs, ys, dtm, _ = S.rasters()
    parts, pv = [], []
    for x0, y0, x1, y1 in C.CARPORT_ROWS:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        gz = dtm[np.searchsorted(ys, cy), np.searchsorted(xs, cx)] - C.FFL
        h = C.CARPORT_HEIGHT
        for x in np.arange(x0 + 1.0, x1, 6.0):
            parts.append(box(x - 0.1, cy - 0.1, gz - 0.2, x + 0.1, cy + 0.1, gz + h))
        rise = (y1 - y0) * math.tan(math.radians(10))
        pv.append(profile_x([(y0, gz + h - rise / 2), (y1, gz + h + rise / 2),
                             (y1, gz + h + rise / 2 + 0.08), (y0, gz + h - rise / 2 + 0.08)], x0, x1))
    return union(parts), union(pv)


def export_building(out):
    scene = trimesh.Scene()
    for lv in ("GF", "FF"):
        ext, glass = B.external_walls(lv)
        _add(scene, f"{lv}__extwall", ext, "extwall")
        _add(scene, f"{lv}__glass", glass, "glass")
        _add(scene, f"{lv}__intwall", B.internal_walls(lv), "intwall")
        _add(scene, f"{lv}__slab", B.slab(lv), "slab")
    _add(scene, "GF__plinth", box(-0.3, -0.3, -1.2, B.L + 0.3, B.D + 0.3, -B.S), "plinth")
    _add(scene, "GF__stair", B.stair(), "stair")
    _add(scene, "FF__balustrade", B.balustrades("FF"), "balustrade")
    roof, rglass, pv = B.roof_web()
    _add(scene, "RF__roof", roof, "roof")
    _add(scene, "RF__glass", rglass, "glass")
    _add(scene, "RF__pv", pv, "pv")
    ax = B.annex()
    _add(scene, "GF__annexwall", union([ax["walls"], ax["floor"]]), "extwall")
    _add(scene, "GF__annexglass", ax["glass"], "glass")
    _add(scene, "RF__annexroof", ax["roof"], "roof")
    _add(scene, "RF__green", ax["green"], "green")
    for room in B.ROOMS:
        z0 = B.LEVEL_Z[room["level"]]
        floor = prism(B.room_floor_poly(room), z0, z0 + B.FINISH)
        _add(scene, f"{room['level']}__floor__{room['id']}", floor, "floor",
             FLOOR_COLOURS.get(room["id"], (0.78, 0.72, 0.60)))
        furn = union([m for _, m, _ in B.room_items(room)])
        _add(scene, f"{room['level']}__furn__{room['id']}", furn, "furn")
    posts, cpv = carport_geometry()
    _add(scene, "SITE__carport", posts, "carport")
    _add(scene, "SITE__carportpv", cpv, "pv")
    (out / "building.glb").write_bytes(trimesh.exchange.gltf.export_glb(scene, include_normals=False))


def export_terrain(out, step=2):
    xs, ys, dtm, _ = S.rasters()
    h = (dtm[::step, ::step] - C.FFL).astype("<f4")
    (out / "terrain.bin").write_bytes(h.tobytes())
    e0, n0, e1, n1 = C.DATA_BBOX
    json.dump(dict(x0=float(xs[0]), y0=float(ys[0]), dx=step, nx=h.shape[1], ny=h.shape[0],
                   tex_x0=e0 - C.ORIGIN_E, tex_y0=n0 - C.ORIGIN_N, tex_w=e1 - e0, tex_h=n1 - n0),
              open(out / "terrain.json", "w"))


def export_context(out):
    bldg = []
    for p, zb, zt, name in S.context_buildings():
        p = p.simplify(0.3)
        if p.geom_type != "Polygon":
            continue
        bldg.append(dict(p=[[round(x, 1), round(y, 1)] for x, y in list(p.exterior.coords)[:-1]],
                         b=round(zb - C.FFL, 2), t=round(zt - C.FFL, 2), n=name))
    trees = [[x, y, round(z - C.FFL, 2), h, r] for x, y, z, h, r in S.tree_points()]
    json.dump(dict(buildings=bldg, trees=trees), open(out / "context.json", "w"), separators=(",", ":"))


def _noise_fill(size, base, spread, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (size[1], size[0], 1))
    img = np.clip(np.array(base)[None, None, :] + n * np.array(spread)[None, None, :], 0, 255)
    flowers = rng.random((size[1], size[0])) > 0.996
    img[flowers] = [235, 220, 120]
    return Image.fromarray(img.astype(np.uint8))


def export_textures(out, web_px=2048):
    src = Image.open(C.RAW / "aerial_bng.jpg").convert("RGB")
    W, H = src.size
    e0, n0, e1, n1 = C.DATA_BBOX

    def px(poly):
        return [((x + C.ORIGIN_E - e0) / (e1 - e0) * W, (n1 - (y + C.ORIGIN_N)) / (n1 - n0) * H)
                for x, y in poly.exterior.coords]

    def mask(geom):
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        for g in getattr(geom, "geoms", [geom]):
            if g.geom_type == "Polygon" and not g.is_empty:
                d.polygon(px(g), fill=255)
        return m

    land = S.proposal_landscape()
    proposed = src.copy()
    layers = [
        (land["plot"].buffer(1.5), _noise_fill((W, H), (104, 134, 66), (10, 12, 8), 1)),
        (land["meadow"], _noise_fill((W, H), (112, 142, 70), (14, 16, 10), 2)),
        (land["paving"], _noise_fill((W, H), (190, 182, 162), (6, 6, 6), 3)),
        (S.proposal_paving()[0], _noise_fill((W, H), (112, 114, 112), (5, 5, 5), 4)),
        (land["rain_garden"], _noise_fill((W, H), (70, 104, 56), (14, 14, 10), 5)),
        (land["rain_garden"].buffer(-1.4), _noise_fill((W, H), (84, 116, 128), (6, 6, 6), 6)),
        (land["pond"], _noise_fill((W, H), (64, 104, 122), (5, 6, 6), 7)),
        (B.FOOTPRINT.buffer(1.0), _noise_fill((W, H), (176, 172, 164), (4, 4, 4), 8)),
    ]
    for geom, fill in layers:
        proposed.paste(fill, (0, 0), mask(geom))
    d = ImageDraw.Draw(proposed)
    park = S.proposal_paving()[0]
    for x in np.arange(36, 96, 2.5):
        for yy in ((-18.0, -13.0), (-7.0, -2.0), (2.0, 7.0)):
            seg = Polygon([(x, yy[0]), (x + 0.1, yy[0]), (x + 0.1, yy[1]), (x, yy[1])]).intersection(park)
            if not seg.is_empty and seg.geom_type == "Polygon":
                d.polygon(px(seg), fill=(225, 225, 220))
    C.OUT_CAD.mkdir(parents=True, exist_ok=True)
    proposed.save(C.OUT_CAD / "site_plan_proposed_texture.jpg", quality=90)
    src.resize((web_px, web_px), Image.LANCZOS).save(out / "aerial_existing.jpg", quality=82)
    proposed.resize((web_px, web_px), Image.LANCZOS).save(out / "aerial_proposed.jpg", quality=82)


def export_rooms(out):
    _, rooms = schedule.write()
    to_ll = Transformer.from_crs(27700, 4326, always_xy=True)
    lon, lat = to_ll.transform(C.ORIGIN_E, C.ORIGIN_N)
    met = B.metrics()
    light_d = sum(r["lighting"]["design_kwh"] for r in rooms)
    light_b = sum(r["lighting"]["baseline_kwh"] for r in rooms)
    data = dict(
        project="The Heat Exchange - NTU Clifton Campus",
        origin=dict(lat=lat, lon=lon, bng_e=C.ORIGIN_E, bng_n=C.ORIGIN_N, ffl_m_aod=C.FFL),
        assumptions=dict(elec_gbp_per_kwh=C.ELEC_GBP_PER_KWH, grid_kgco2e_per_kwh=C.GRID_KGCO2E_PER_KWH,
                         uf=C.LIGHT_UF, mf=C.LIGHT_MF, baseline_lm_per_w=C.BASELINE_LM_PER_W),
        metrics=met,
        totals=dict(fitout_capex_gbp=sum(r["fitout_capex_gbp"] for r in rooms),
                    lighting_design_kwh=light_d, lighting_baseline_kwh=light_b,
                    lighting_saving_gbp=round((light_b - light_d) * C.ELEC_GBP_PER_KWH),
                    lighting_saving_kgco2e=round((light_b - light_d) * C.GRID_KGCO2E_PER_KWH)),
        rooms=rooms,
        credits=["Imagery: Esri, Maxar, Earthstar Geographics", "LiDAR: Environment Agency, OGL v3",
                 "Map data: (c) OpenStreetMap contributors, ODbL"])
    json.dump(data, open(out / "rooms.json", "w"), indent=1)
    json.dump(dict(metrics=met, totals=data["totals"]), open(C.OUT_CAD / "building_metrics.json", "w"), indent=1)


def export_all():
    out = C.OUT_WEB
    out.mkdir(parents=True, exist_ok=True)
    export_building(out)
    export_terrain(out)
    export_context(out)
    export_textures(out)
    export_rooms(out)
    return sorted(out.iterdir())


if __name__ == "__main__":
    for f in export_all():
        print(f"{f.name:<24} {f.stat().st_size / 1024:8.0f} KB")
