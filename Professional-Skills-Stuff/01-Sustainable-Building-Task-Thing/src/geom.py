"""Small solid-modelling toolkit on top of manifold3d (robust booleans) and trimesh (export).

All geometry is built in real-world metres. Print exports scale it down at the very end,
so the same functions produce the 1:1000 site model, the 1:100 building and the web twin.
"""
import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold, Mesh, OpType
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient

EMPTY = Manifold()


def box(x0, y0, z0, x1, y1, z1) -> Manifold:
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    if min(x1 - x0, y1 - y0, z1 - z0) <= 1e-6:
        return EMPTY
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def _rings(poly: Polygon):
    poly = orient(poly, 1.0)
    rings = [list(poly.exterior.coords)[:-1]]
    rings += [list(r.coords)[:-1] for r in poly.interiors]
    return rings


def prism(shape, z0, z1) -> Manifold:
    """Extrude a shapely Polygon/MultiPolygon between two heights."""
    if shape is None or shape.is_empty or z1 - z0 <= 1e-6:
        return EMPTY
    polys = list(shape.geoms) if isinstance(shape, MultiPolygon) else [shape]
    parts = []
    for p in polys:
        if p.area < 1e-6:
            continue
        cs = CrossSection(_rings(p))
        parts.append(cs.extrude(z1 - z0).translate((0, 0, z0)))
    return union(parts)


def profile_x(points_yz, x0, x1) -> Manifold:
    """Extrude a polygon drawn in the (y, z) plane along x from x0 to x1."""
    cs = CrossSection([[(y, z) for y, z in points_yz]])
    m = cs.extrude(x1 - x0)                       # profile in XY, extruded along +Z
    # map (u, v, w) -> (x = w + x0, y = u, z = v)
    return m.transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]], dtype=float))


def cylinder(cx, cy, z0, r, h, segments=24) -> Manifold:
    return Manifold.cylinder(h, r, r, segments).translate((cx, cy, z0))


def union(parts) -> Manifold:
    parts = [p for p in parts if p is not None and not p.is_empty()]
    if not parts:
        return EMPTY
    if len(parts) == 1:
        return parts[0]
    return Manifold.batch_boolean(parts, OpType.Add)


def from_arrays(vertices, faces) -> Manifold:
    mesh = Mesh(vert_properties=np.asarray(vertices, dtype=np.float32),
                tri_verts=np.asarray(faces, dtype=np.uint32))
    m = Manifold(mesh)
    if m.status().name != "NoError":
        raise ValueError(f"mesh is not a closed manifold: {m.status()}")
    return m


def to_trimesh(m: Manifold) -> trimesh.Trimesh:
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=True)


def heightfield_solid(xs, ys, top, z_bottom) -> Manifold:
    """Closed solid between a regular-grid height surface and a flat base.

    xs: (nx,) increasing, ys: (ny,) increasing, top: (ny, nx) heights.
    """
    ny, nx = top.shape
    X, Y = np.meshgrid(xs, ys)
    top_v = np.column_stack([X.ravel(), Y.ravel(), top.ravel()])
    bot_v = np.column_stack([X.ravel(), Y.ravel(), np.full(X.size, z_bottom)])
    verts = np.vstack([top_v, bot_v])
    n = nx * ny

    idx = np.arange(n).reshape(ny, nx)
    a, b = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel()
    c, d = idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    top_f = np.vstack([np.column_stack([a, b, c]), np.column_stack([a, c, d])])
    bot_f = top_f[:, ::-1] + n

    ring = np.concatenate([idx[0, :], idx[1:, -1], idx[-1, -2::-1], idx[-2:0:-1, 0]])
    nxt = np.roll(ring, -1)
    side_f = np.vstack([np.column_stack([ring, ring + n, nxt + n]),
                        np.column_stack([ring, nxt + n, nxt])])
    faces = np.vstack([top_f, bot_f, side_f])

    tm = trimesh.Trimesh(verts, faces, process=False)
    trimesh.repair.fix_normals(tm)
    return from_arrays(tm.vertices, tm.faces)


def scaled(m: Manifold, factor, offset=(0.0, 0.0, 0.0)) -> trimesh.Trimesh:
    """Translate by offset (metres) then scale (e.g. 1000/scale for mm at 1:scale)."""
    t = to_trimesh(m.translate(offset))
    t.apply_scale(factor)
    return t
