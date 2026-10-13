"""Google Earth Pro KMZ: the proposal as a georeferenced model world.

Open Design/exports/heat_exchange_google_earth.kmz in Google Earth Pro (File > Open). The proposed
landscape is a ground overlay, which Google Earth drapes over its 3D photo-mesh, so it replaces the
car park in place. White massing of the existing campus and simple trees are included (hidden) for
viewing with Layers > 3D Buildings unticked.
"""
import io
import zipfile
from xml.sax.saxutils import escape

import collada
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from pyproj import Geod, Transformer
from shapely.geometry import Point

import building as B
import config as C
import site_model as S
from web_export import Y_UP

OUT = C.OUT_CAD / "heat_exchange_google_earth.kmz"
CONTEXT_RADIUS = 220.0       # m around the building for massing and trees

KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
  <name>The Heat Exchange - NTU Clifton</name>
  <open>1</open>
  <Snippet maxLines="2">The proposal and its landscape, draped over the Students' Car Park.</Snippet>
  <description>The landscape overlay drapes over Google's 3D campus and replaces the car park. For a
    clean architectural-model look, untick Layers &gt; 3D Buildings and tick the massing and tree
    folders here instead.</description>
  <LookAt><longitude>{lon}</longitude><latitude>{lat}</latitude><altitude>0</altitude>
    <heading>20</heading><tilt>60</tilt><range>160</range><altitudeMode>relativeToGround</altitudeMode></LookAt>
  <Style id="massing">
    <LineStyle><color>ff9a9a9a</color><width>1</width></LineStyle>
    <PolyStyle><color>fff2f0eb</color></PolyStyle>
  </Style>
  <Placemark>
    <name>The Heat Exchange (proposed)</name>
    <Model>
      <altitudeMode>relativeToGround</altitudeMode>
      <Location><longitude>{lon}</longitude><latitude>{lat}</latitude><altitude>{alt}</altitude></Location>
      <Orientation><heading>{heading}</heading><tilt>0</tilt><roll>0</roll></Orientation>
      <Scale><x>1</x><y>1</y><z>1</z></Scale>
      <Link><href>models/heat_exchange.dae</href></Link>
    </Model>
  </Placemark>
  <GroundOverlay>
    <name>Proposed landscape (replaces the car park)</name>
    <drawOrder>10</drawOrder>
    <Icon><href>images/landscape.png</href></Icon>
    <gx:LatLonQuad><coordinates>{quad}</coordinates></gx:LatLonQuad>
  </GroundOverlay>
  <Folder>
    <name>Existing campus massing (with 3D Buildings off)</name>
    <visibility>0</visibility>
{buildings}
  </Folder>
  <Folder>
    <name>Trees (with 3D Buildings off)</name>
    <visibility>0</visibility>
{trees}
  </Folder>
</Document>
</kml>
"""

BUILDING = """    <Placemark><name>{name}</name><visibility>0</visibility><styleUrl>#massing</styleUrl><Polygon><extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates>
      </LinearRing></outerBoundaryIs></Polygon></Placemark>"""

TREE = """    <Placemark><visibility>0</visibility><Model><altitudeMode>relativeToGround</altitudeMode>
      <Location><longitude>{lon:.7f}</longitude><latitude>{lat:.7f}</latitude><altitude>0</altitude></Location>
      <Scale><x>{r}</x><y>{r}</y><z>{h}</z></Scale><Link><href>models/tree.dae</href></Link></Model></Placemark>"""


def collada_bytes(meshes):
    """One geometry per colour, every id unique (Google Earth segfaults on trimesh's shared source ids).

    Transparency uses RGB_ZERO (opacity = 1 - transparency): Google Earth reads it that way whatever
    the declared mode, so A_ONE with transparency 1.0 renders solid parts invisible.
    """
    groups = {}
    for m in meshes:
        groups.setdefault(tuple(m.visual.material.baseColorFactor), []).append(m)

    dae = collada.Collada()
    dae.assetInfo.upaxis = collada.asset.UP_AXIS.Z_UP
    dae.assetInfo.unitname, dae.assetInfo.unitmeter = "meter", 1.0
    nodes = []
    for i, (rgba, ms) in enumerate(groups.items()):
        m = trimesh.util.concatenate(ms)
        r, g, b, a = (c / 255 for c in rgba)
        effect = collada.material.Effect(f"effect{i}", [], "lambert", diffuse=(r, g, b, 1.0),
                                         transparent=(1.0, 1.0, 1.0, 1.0), transparency=1.0 - a,
                                         opaque_mode=collada.material.OPAQUE_MODE.RGB_ZERO, double_sided=True)
        mat = collada.material.Material(f"material{i}", f"material{i}", effect)
        verts = collada.source.FloatSource(f"verts{i}", m.vertices[m.faces].ravel(), ("X", "Y", "Z"))
        norms = collada.source.FloatSource(f"normals{i}", m.face_normals.ravel(), ("X", "Y", "Z"))
        geom = collada.geometry.Geometry(dae, f"geom{i}", f"geom{i}", [verts, norms])
        inputs = collada.source.InputList()
        inputs.addInput(0, "VERTEX", f"#verts{i}")
        inputs.addInput(1, "NORMAL", f"#normals{i}")
        n = len(m.faces) * 3
        idx = np.column_stack([np.arange(n), np.repeat(np.arange(len(m.faces)), 3)]).ravel()
        geom.primitives.append(geom.createTriangleSet(idx, inputs, f"matref{i}"))
        dae.effects.append(effect)
        dae.materials.append(mat)
        dae.geometries.append(geom)
        bind = collada.scene.MaterialNode(f"matref{i}", mat, inputs=[])
        nodes.append(collada.scene.Node(f"node{i}", children=[collada.scene.GeometryNode(geom, [bind])]))
    dae.scenes.append(collada.scene.Scene("scene", nodes))
    dae.scene = dae.scenes[0]
    buf = io.BytesIO()
    dae.write(buf)
    return buf.getvalue()


def _coloured(mesh, rgb):
    mesh.visual = trimesh.visual.TextureVisuals(
        material=trimesh.visual.material.PBRMaterial(baseColorFactor=[*rgb, 255]))
    return mesh


def tree_model():
    """Unit tree (crown radius 1, height 1), scaled per tree by its Placemark."""
    trunk = trimesh.creation.cylinder(radius=0.07, height=0.45, sections=8)
    trunk.apply_translation([0, 0, 0.225])
    crown = trimesh.creation.icosphere(subdivisions=1)
    crown.apply_scale([1.0, 1.0, 0.38])
    crown.apply_translation([0, 0, 0.6])
    return collada_bytes([_coloured(trunk, (104, 84, 62)), _coloured(crown, (78, 112, 60))])


def landscape_overlay():
    """The web twin's proposed site texture, cropped to the car park and transparent outside it."""
    img = Image.open(C.OUT_CAD / "site_plan_proposed_texture.jpg").convert("RGBA")
    W, H = img.size
    e0, n0, e1, n1 = C.DATA_BBOX
    sx, sy = W / (e1 - e0), H / (n1 - n0)
    plot = S.plot_polygon().buffer(1.5)
    x0, y0, x1, y1 = plot.bounds
    left, top = int((x0 + C.ORIGIN_E - e0) * sx) - 2, int((n1 - y1 - C.ORIGIN_N) * sy) - 2
    right, bottom = int((x1 + C.ORIGIN_E - e0) * sx) + 3, int((n1 - y0 - C.ORIGIN_N) * sy) + 3
    crop = img.crop((left, top, right, bottom))
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).polygon([((x + C.ORIGIN_E - e0) * sx - left, (n1 - y - C.ORIGIN_N) * sy - top)
                                  for x, y in plot.exterior.coords], fill=255)
    crop.putalpha(mask)
    buf = io.BytesIO()
    crop.save(buf, "PNG")
    corners_bng = [(e0 + left / sx, n1 - bottom / sy), (e0 + right / sx, n1 - bottom / sy),
                   (e0 + right / sx, n1 - top / sy), (e0 + left / sx, n1 - top / sy)]
    return buf.getvalue(), corners_bng


def export():
    scene = trimesh.load(C.OUT_WEB / "building.glb")
    meshes = []
    for m in scene.dump():
        if "__furn__" in m.metadata.get("name", ""):
            continue
        m.apply_transform(np.linalg.inv(Y_UP))
        meshes.append(m)
    dae = collada_bytes(meshes)

    to_ll = Transformer.from_crs(27700, 4326, always_xy=True)

    def ll(x, y):
        return to_ll.transform(x + C.ORIGIN_E, y + C.ORIGIN_N)

    lon, lat = ll(0, 0)
    lon_n, lat_n = ll(0, 100)
    heading = Geod(ellps="WGS84").inv(lon, lat, lon_n, lat_n)[0]     # grid north vs true north

    png, corners = landscape_overlay()
    quad = " ".join("{:.7f},{:.7f}".format(*to_ll.transform(e, n)) for e, n in corners)

    centre = B.FOOTPRINT.centroid
    plot = S.plot_polygon()
    buildings = []
    for poly, zb, zt, name in S.context_buildings():
        if poly.centroid.distance(centre) > CONTEXT_RADIUS:
            continue
        h = zt - zb - 0.8
        coords = " ".join("{:.7f},{:.7f},{:.1f}".format(*ll(x, y), h) for x, y in poly.exterior.coords)
        buildings.append(BUILDING.format(name=escape(name or "Existing building"), coords=coords))
    trees = []
    keep_out = B.FOOTPRINT.buffer(3.0)
    for x, y, _, h, r in S.tree_points():
        if centre.distance(Point(x, y)) > CONTEXT_RADIUS or keep_out.contains(Point(x, y)):
            continue
        tlon, tlat = ll(x, y)
        trees.append(TREE.format(lon=tlon, lat=tlat, r=r, h=h))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("doc.kml", KML.format(lon=f"{lon:.7f}", lat=f"{lat:.7f}", alt=0.3, heading=f"{heading:.3f}",
                                         quad=quad, buildings="\n".join(buildings), trees="\n".join(trees)))
        z.writestr("models/heat_exchange.dae", dae)
        z.writestr("models/tree.dae", tree_model())
        z.writestr("images/landscape.png", png)
    print(f"{len(buildings)} context buildings, {len(trees)} trees, plot overlay {plot.area:.0f} m2")
    return OUT


if __name__ == "__main__":
    print(export())
