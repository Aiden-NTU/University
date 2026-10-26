"""Site context from open data: terrain, neighbouring buildings, trees, roads and the proposal.

Building heights are not guessed: each OpenStreetMap footprint is extruded to the LiDAR
surface height measured inside it (DSM), standing on the bare-ground terrain (DTM).
Trees come from the same data: canopy = DSM - DTM where there is no building.
"""
import xml.etree.ElementTree as ET
from functools import lru_cache

import numpy as np
import rasterio
import rasterio.features
from affine import Affine
from pyproj import Transformer
from scipy import ndimage
from shapely.geometry import LineString, Polygon, box as rect
from shapely.ops import unary_union

import building as B
import config as C
import placeables as P
from geom import EMPTY, box, heightfield_solid, prism, union

ROAD_WIDTH = {"motorway": 10, "trunk": 9, "primary": 8, "secondary": 7, "tertiary": 6.5,
              "unclassified": 5.5, "residential": 5.5, "living_street": 5, "service": 4,
              "pedestrian": 3, "track": 3, "cycleway": 2.5, "footway": 2, "path": 1.8, "steps": 2}


# ---------------------------------------------------------------------------------------
# Raw data in local coordinates
# ---------------------------------------------------------------------------------------
@lru_cache
def rasters():
    """DTM, DSM as arrays flipped so row 0 is the southern edge; plus cell-centre coords."""
    with rasterio.open(C.RAW / "dtm.tif") as r:
        dtm = r.read(1).astype(np.float64)
        bounds = r.bounds
    with rasterio.open(C.RAW / "dsm.tif") as r:
        dsm = r.read(1).astype(np.float64)
    for a in (dtm, dsm):
        bad = a < -100
        if bad.any():
            idx = ndimage.distance_transform_edt(bad, return_distances=False, return_indices=True)
            a[bad] = a[tuple(i[bad] for i in idx)]
    dtm, dsm = dtm[::-1].copy(), dsm[::-1].copy()
    ny, nx = dtm.shape
    xs = bounds.left + 0.5 + np.arange(nx) - C.ORIGIN_E
    ys = bounds.bottom + 0.5 + np.arange(ny) - C.ORIGIN_N
    return xs, ys, dtm, dsm


def raster_transform():
    xs, ys, _, _ = rasters()
    return Affine(1.0, 0, xs[0] - 0.5, 0, 1.0, ys[0] - 0.5)       # south-up array


def rasterize(shapes, shape):
    if not shapes:
        return np.zeros(shape, bool)
    return rasterio.features.rasterize([(s, 1) for s in shapes], out_shape=shape,
                                       transform=raster_transform(), dtype=np.uint8).astype(bool)


@lru_cache
def osm():
    root = ET.parse(C.RAW / "osm.xml").getroot()
    to_bng = Transformer.from_crs(4326, 27700, always_xy=True)
    ids, lon, lat = [], [], []
    for n in root.iter("node"):
        ids.append(n.get("id"))
        lon.append(float(n.get("lon")))
        lat.append(float(n.get("lat")))
    e, n = to_bng.transform(np.array(lon), np.array(lat))
    nodes = {i: (x - C.ORIGIN_E, y - C.ORIGIN_N) for i, x, y in zip(ids, e, n)}
    ways = []
    for w in root.iter("way"):
        tags = {t.get("k"): t.get("v") for t in w.findall("tag")}
        pts = [nodes[nd.get("ref")] for nd in w.findall("nd") if nd.get("ref") in nodes]
        if len(pts) >= 2:
            ways.append((w.get("id"), tags, pts))
    return ways


def plot_polygon():
    for wid, tags, pts in osm():
        if wid == C.PLOT_OSM_WAY:
            return Polygon(pts)
    raise KeyError("plot way not found in OSM extract")


@lru_cache
def context_buildings():
    """[(Polygon, base_z, top_z, name)] for every OSM building, heights from LiDAR."""
    xs, ys, dtm, dsm = rasters()
    out = []
    footprint = B.FOOTPRINT.buffer(2.0)
    for wid, tags, pts in osm():
        if "building" not in tags or len(pts) < 4:
            continue
        p = Polygon(pts)
        if not p.is_valid:
            p = p.buffer(0)
        if p.area < 8 or p.intersects(footprint):
            continue
        m = rasterize([p.buffer(-0.7) if p.buffer(-0.7).area > 4 else p], dtm.shape)
        if m.sum() < 3:
            continue
        ground = dtm[m].min()
        top = np.percentile(dsm[m], 60)
        if top - ground < 2.5:          # LiDAR older than the building, or a canopy: fall back
            levels = float(tags.get("building:levels", 1) or 1)
            top = ground + 3.2 * levels + 1.0
        out.append((p, ground - 0.8, top, tags.get("name", "")))
    return out


def roads_polygon(window=None):
    plot = plot_polygon()
    lines, areas = [], []
    for wid, tags, pts in osm():
        hw = tags.get("highway")
        if hw in ROAD_WIDTH and tags.get("area") != "yes":
            g = LineString(pts).buffer(ROAD_WIDTH[hw] / 2, cap_style=2, join_style=2)
            if hw in ("service", "footway", "path") and g.centroid.within(plot):
                continue                 # old car-park aisles are replaced by the new landscape
            lines.append(g)
        elif tags.get("amenity") == "parking" and wid != C.PLOT_OSM_WAY and pts[0] == pts[-1]:
            areas.append(Polygon(pts).buffer(0))
    roads = unary_union(lines + areas + proposal_paving())
    return roads.intersection(window) if window is not None else roads


# ---------------------------------------------------------------------------------------
# The proposal's landscape (also painted onto the web twin's aerial texture)
# ---------------------------------------------------------------------------------------
def proposal_paving():
    plot = plot_polygon()
    parking = rect(36, -18, 96, 7).intersection(plot)
    forecourt = rect(-7, -7, 11, 0)
    approach = LineString([(35, -66), (20, -30), (8, -8)]).buffer(1.8, cap_style=2)
    west_path = LineString([(-6, -2), (-26, 6)]).buffer(1.2, cap_style=2)
    service = LineString([(24, 4.0), (40, 0), (55, -6)]).buffer(1.8, cap_style=2)
    return [parking, forecourt, approach.intersection(plot.buffer(10)), west_path, service]


def proposal_landscape():
    plot = plot_polygon()
    paving = unary_union(proposal_paving())
    rain_garden = rect(11, -7.5, 30, -3.0)
    pond = Polygon([(15, 40), (30, 36), (36, 46), (24, 54), (13, 50)]).buffer(-3).buffer(4.5, quad_segs=12)
    meadow = plot.difference(paving).difference(B.FOOTPRINT.buffer(0.5)).difference(rain_garden).difference(pond)
    return dict(plot=plot, paving=paving, rain_garden=rain_garden, pond=pond, meadow=meadow)


def carports():
    return [rect(x0, y0, x1, y1) for x0, y0, x1, y1 in C.CARPORT_ROWS]


# ---------------------------------------------------------------------------------------
# Solids for the printed site model
# ---------------------------------------------------------------------------------------
def window_box():
    cx, cy = C.SITE_CENTRE_LOCAL
    half = C.SITE_PRINT_SIZE_MM / 2 * C.SITE_SCALE / 1000
    return cx - half, cy - half, cx + half, cy + half


@lru_cache
def wall_frame():
    """Rim and wall slot round the printed site, in print mm (x, y from the model centre, z up from the bed).

    The rim is one level all round, just above the highest ground it replaces, so all four
    poster walls stand at the same height.
    """
    xs, ys, dtm, _, _ = _crop(*window_box())
    k = 1000 / C.SITE_SCALE                                   # print mm per model metre
    half = (xs[-1] - xs[0]) / 2 * k
    lip, slot = C.SITE_FRAME_LIP_MM, C.WALL_PLY_MM + C.SITE_WALL_SLOT_CLEARANCE_MM
    band = 2 * lip + slot
    n = int(np.ceil(band / k))
    edge = np.ones(dtm.shape, bool)
    edge[n:-n, n:-n] = False
    ground = (dtm[edge].max() - dtm.min()) * k + C.SITE_BASE_MM
    top = float(np.ceil(ground + 0.75))
    floor = top - C.SITE_WALL_SLOT_DEPTH_MM
    if floor < 1.5:
        raise ValueError(f"wall slot leaves only {floor:.1f} mm under it; make SITE_WALL_SLOT_DEPTH_MM shallower")
    return dict(half=half, lip=lip, slot=slot, band=band, top=top, floor=floor, depth=C.SITE_WALL_SLOT_DEPTH_MM)


def _crop(x0, y0, x1, y1):
    xs, ys, dtm, dsm = rasters()
    ix = np.where((xs >= x0) & (xs <= x1))[0]
    iy = np.where((ys >= y0) & (ys <= y1))[0]
    sl = (slice(iy[0], iy[-1] + 1), slice(ix[0], ix[-1] + 1))
    return xs[ix], ys[iy], dtm[sl], dsm[sl], sl


def canopy_top(dtm, dsm, sl):
    """Smoothed woodland canopy surface (z) and its mask, with buildings and the plot removed."""
    nd = dsm - dtm
    full_shape = rasters()[2].shape
    blocked = rasterize([p.buffer(1.5) for p, *_ in context_buildings()] + [B.FOOTPRINT.buffer(3), plot_polygon()],
                        full_shape)[sl]
    mask = (nd > 2.5) & ~blocked
    mask = ndimage.binary_opening(mask, iterations=1)
    mask = ndimage.binary_closing(mask, iterations=2) & ~blocked
    h = ndimage.gaussian_filter(np.clip(nd, 0, C.TREE_CANOPY_CAP_M) * mask, 1.2)
    w = ndimage.gaussian_filter(mask.astype(float), 1.2)
    h = np.where(w > 0.05, h / np.maximum(w, 0.05), 0)
    return np.where(mask, dtm + np.clip(h, 3.0, C.TREE_CANOPY_CAP_M), dtm - 1.5), mask


def site_print_solids():
    """Disjoint solids (metres, absolute z) for the multi-colour 1:1000 site model."""
    x0, y0, x1, y1 = window_box()
    xs, ys, dtm, dsm, sl = _crop(x0, y0, x1, y1)
    win = rect(xs[0], ys[0], xs[-1], ys[-1])
    base_z = dtm.min() - C.SITE_BASE_MM * C.SITE_SCALE / 1000
    terrain = heightfield_solid(xs, ys, dtm, base_z)

    ctx = []
    for p, zb, zt, _ in context_buildings():
        clipped = p.intersection(win.buffer(-0.5))
        if not clipped.is_empty and clipped.area > 6:
            ctx.append(prism(clipped, max(zb, base_z + 0.5), zt))
    ctx = union(ctx)

    proposal = B.massing().translate((0, 0, C.FFL))
    carport_h = C.CARPORT_HEIGHT
    xs_all, ys_all, dtm_all, _ = rasters()
    for cp in carports():
        if cp.intersects(win):
            cx, cy = cp.centroid.x, cp.centroid.y
            gz = dtm_all[np.searchsorted(ys_all, cy), np.searchsorted(xs_all, cx)]
            proposal += prism(cp.intersection(win), gz - 1.0, gz + carport_h)
    def ground_at(x, y):
        iy = np.searchsorted(ys_all, y).clip(0, len(ys_all) - 1)
        ix = np.searchsorted(xs_all, x).clip(0, len(xs_all) - 1)
        return float(dtm_all[iy, ix])
    # Site placeables share the proposal's orange print layer. This keeps the existing
    # four-filament Bambu workflow intact while still including the object in every export.
    for _, asset, solid in P.site_assets(ground_at, for_print=True):
        if asset.print_layer in (None, "proposal"):
            proposal += solid
    proposal = proposal ^ box(xs[0], ys[0], base_z, xs[-1], ys[-1], base_z + 500)

    top, _ = canopy_top(dtm, dsm, sl)
    trees = heightfield_solid(xs, ys, top, base_z + 0.2) - terrain - ctx - proposal

    inlay = C.ROAD_INLAY_MM * C.SITE_SCALE / 1000
    skin = terrain - terrain.translate((0, 0, -inlay))
    roads = prism(roads_polygon(win), base_z - 1, dtm.max() + 1) ^ skin
    roads = roads - ctx - proposal

    terrain = terrain - roads - ctx - proposal

    # Grey rim with the poster-wall slot; it replaces whatever was in the outermost band.
    fr, m = wall_frame(), C.SITE_SCALE / 1000
    rim_out = rect(xs[0], ys[0], xs[-1], ys[-1])
    slot = rim_out.buffer(-fr["lip"] * m, join_style=2).difference(rim_out.buffer(-(fr["lip"] + fr["slot"]) * m, join_style=2))
    band = prism(rim_out.difference(rim_out.buffer(-fr["band"] * m, join_style=2)), base_z - 1, base_z + 500)
    rim = (prism(rim_out.difference(rim_out.buffer(-fr["band"] * m, join_style=2)), base_z, base_z + fr["top"] * m)
           - prism(slot, base_z + fr["floor"] * m, base_z + fr["top"] * m + 1))
    terrain, ctx, trees, proposal = (p - band for p in (terrain, ctx, trees, proposal))
    roads = (roads - band) + rim
    return dict(terrain=terrain, roads=roads, context=ctx, trees=trees, proposal=proposal), base_z


# ---------------------------------------------------------------------------------------
# Data for the web twin
# ---------------------------------------------------------------------------------------
def tree_points(spacing=7):
    """Canopy peaks (x, y, ground_z, height, crown radius) for instanced web trees."""
    xs, ys, dtm, dsm = rasters()
    sl = (slice(None), slice(None))
    top, mask = canopy_top(dtm, dsm, sl)
    h = np.where(mask, top - dtm, 0)
    peaks = (h == ndimage.maximum_filter(h, size=spacing)) & (h > 3.5)
    out = []
    for iy, ix in zip(*np.nonzero(peaks)):
        hh = float(h[iy, ix])
        out.append([round(float(xs[ix]), 1), round(float(ys[iy]), 1), round(float(dtm[iy, ix]), 2),
                    round(hh, 1), round(float(np.clip(0.28 * hh + 1.2, 2.0, 6.5)), 1)])
    return out
