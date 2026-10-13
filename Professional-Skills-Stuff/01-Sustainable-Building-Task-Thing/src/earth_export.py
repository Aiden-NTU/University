"""Google Earth Pro KMZ: the web-twin building as a georeferenced COLLADA model.

Open Design/exports/heat_exchange_google_earth.kmz in Google Earth Pro (File > Open).
"""
import zipfile

import numpy as np
import trimesh
from pyproj import Geod, Transformer

import config as C
from web_export import Y_UP

OUT = C.OUT_CAD / "heat_exchange_google_earth.kmz"

KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>The Heat Exchange - NTU Clifton</name>
  <Placemark>
    <name>The Heat Exchange (proposed)</name>
    <LookAt><longitude>{lon}</longitude><latitude>{lat}</latitude><altitude>0</altitude>
      <heading>20</heading><tilt>60</tilt><range>140</range><altitudeMode>relativeToGround</altitudeMode></LookAt>
    <Model>
      <altitudeMode>relativeToGround</altitudeMode>
      <Location><longitude>{lon}</longitude><latitude>{lat}</latitude><altitude>{alt}</altitude></Location>
      <Orientation><heading>{heading}</heading><tilt>0</tilt><roll>0</roll></Orientation>
      <Scale><x>1</x><y>1</y><z>1</z></Scale>
      <Link><href>models/heat_exchange.dae</href></Link>
    </Model>
  </Placemark>
</Document>
</kml>
"""


def export():
    scene = trimesh.load(C.OUT_WEB / "building.glb")
    meshes = []
    for m in scene.dump():
        if "__furn__" in m.metadata.get("name", ""):
            continue
        m.apply_transform(np.linalg.inv(Y_UP))
        meshes.append(m)
    dae = trimesh.exchange.dae.export_collada(meshes).decode()
    dae = dae.replace("<up_axis>Y_UP</up_axis>", "<up_axis>Z_UP</up_axis>")
    if "<up_axis>" not in dae:
        dae = dae.replace("</asset>", "<up_axis>Z_UP</up_axis></asset>")

    to_ll = Transformer.from_crs(27700, 4326, always_xy=True)
    lon, lat = to_ll.transform(C.ORIGIN_E, C.ORIGIN_N)
    lon_n, lat_n = to_ll.transform(C.ORIGIN_E, C.ORIGIN_N + 100)
    heading = Geod(ellps="WGS84").inv(lon, lat, lon_n, lat_n)[0]     # grid north vs true north

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("doc.kml", KML.format(lon=f"{lon:.7f}", lat=f"{lat:.7f}", alt=0.3, heading=f"{heading:.3f}"))
        z.writestr("models/heat_exchange.dae", dae)
    return OUT


if __name__ == "__main__":
    print(export())
