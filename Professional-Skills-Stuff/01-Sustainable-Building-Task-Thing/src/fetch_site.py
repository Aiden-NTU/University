"""Download the open data the site model is built from (skips anything already downloaded).

* OpenStreetMap extract (buildings, roads, paths, car parks)   - ODbL, (c) OpenStreetMap contributors
* Environment Agency LiDAR Composite 1 m DTM (bare ground) and DSM (ground + buildings + trees)
                                                                 - Open Government Licence v3
* Esri World Imagery aerial tiles, warped onto the British National Grid
                                                                 - Esri, Maxar, Earthstar Geographics
"""
import io

import numpy as np
import requests
from PIL import Image
from pyproj import Transformer

import config as C

UA = {"User-Agent": "ntu-student-sustainable-design/1.0 (educational project)"}
WCS = "https://environment.data.gov.uk/spatialdata/{name}/wcs"
LIDAR = {
    "dtm": ("lidar-composite-digital-terrain-model-dtm-1m",
            "13787b9a-26a4-4775-8523-806d13af58fc__Lidar_Composite_Elevation_DTM_1m"),
    "dsm": ("lidar-composite-digital-surface-model-first-return-dsm-1m",
            "df4e3ec3-315e-48aa-aaaf-b5ae74d7b2bb__Lidar_Composite_Elevation_FZ_DSM_1m"),
}


def fetch_osm():
    out = C.RAW / "osm.xml"
    if out.exists():
        return
    to_ll = Transformer.from_crs(27700, 4326, always_xy=True)
    e0, n0, e1, n1 = C.DATA_BBOX
    lons, lats = to_ll.transform([e0, e1, e0, e1], [n0, n0, n1, n1])
    pad = 0.001
    bbox = f"{min(lons) - pad},{min(lats) - pad},{max(lons) + pad},{max(lats) + pad}"
    r = requests.get(f"https://api.openstreetmap.org/api/0.6/map?bbox={bbox}", headers=UA, timeout=120)
    r.raise_for_status()
    out.write_bytes(r.content)


def fetch_lidar():
    e0, n0, e1, n1 = C.DATA_BBOX
    for key, (name, coverage) in LIDAR.items():
        out = C.RAW / f"{key}.tif"
        if out.exists():
            continue
        r = requests.get(WCS.format(name=name), headers=UA, timeout=120, params=[
            ("service", "WCS"), ("version", "2.0.1"), ("request", "GetCoverage"),
            ("CoverageId", coverage), ("format", "image/tiff"),
            ("subset", f"E({e0},{e1})"), ("subset", f"N({n0},{n1})")])
        r.raise_for_status()
        out.write_bytes(r.content)


def fetch_aerial(size=4096, zoom=19):
    """Mosaic Web-Mercator tiles, then resample them onto the BNG grid of the LiDAR."""
    out = C.RAW / "aerial_bng.jpg"
    if out.exists():
        return
    e0, n0, e1, n1 = C.DATA_BBOX
    to_merc = Transformer.from_crs(27700, 3857, always_xy=True)
    R = 20037508.342789244
    tile = 2 * R / 2 ** zoom
    xs, ys = to_merc.transform([e0, e1, e0, e1], [n0, n0, n1, n1])
    tx0, tx1 = int((min(xs) + R) // tile), int((max(xs) + R) // tile)
    ty0, ty1 = int((R - max(ys)) // tile), int((R - min(ys)) // tile)
    mosaic = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256, 3), np.uint8)
    s = requests.Session()
    s.headers.update(UA)
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            r = s.get("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/"
                      f"MapServer/tile/{zoom}/{ty}/{tx}", timeout=30)
            r.raise_for_status()
            mosaic[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = \
                np.array(Image.open(io.BytesIO(r.content)).convert("RGB"))
    e = e0 + (np.arange(size) + 0.5) * (e1 - e0) / size
    n = n1 - (np.arange(size) + 0.5) * (n1 - n0) / size
    E, N = np.meshgrid(e, n)
    mx, my = to_merc.transform(E, N)
    px = (((mx + R) / tile - tx0) * 256).astype(int).clip(0, mosaic.shape[1] - 1)
    py = (((R - my) / tile - ty0) * 256).astype(int).clip(0, mosaic.shape[0] - 1)
    Image.fromarray(mosaic[py, px]).save(out, quality=88)


if __name__ == "__main__":
    C.RAW.mkdir(parents=True, exist_ok=True)
    fetch_osm()
    fetch_lidar()
    fetch_aerial()
    print("site data ready in", C.RAW)
