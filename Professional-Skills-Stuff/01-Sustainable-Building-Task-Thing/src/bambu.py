"""Ready-to-print Bambu Lab projects, sliced on this machine with the Bambu Studio command line.

Needs Bambu Studio from Flathub (Linux):  flatpak install --user flathub com.bambulab.BambuStudio

    python src/bambu.py              # NTU's printers (PRINTERS)
    python src/bambu.py X1C P1S      # named printers, from ALL_PRINTERS

Writes Model/bambu/<printer>/<project>.gcode.3mf (sliced, printable straight from the printer's
SD card / USB stick) and Model/bambu/project/<project>.3mf (unsliced, open in Bambu Studio on any
Windows/macOS/Linux machine, change printer if needed, press Print). Real grams and hours from the
slicer go to Model/bambu/slice_report.md.
"""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import config as C

APP = "com.bambulab.BambuStudio"
OUT = C.ROOT / "Model" / "bambu"
PRINT = C.OUT_PRINT

PRINTERS = {      # NTU: X1C in the 3D Printing Studio, X1E (with AMS) in the RISE laboratory
    "X1C": dict(machine="Bambu Lab X1 Carbon 0.4 nozzle", tag="X1C", filament="Bambu PLA Basic @BBL X1C"),
    "X1E": dict(machine="Bambu Lab X1E 0.4 nozzle", tag="X1C", filament="Bambu PLA Basic @BBL X1C"),
}
OTHER_PRINTERS = {  # sliced only when named: python src/bambu.py P1S
    "P1S": dict(machine="Bambu Lab P1S 0.4 nozzle", tag="X1C", filament="Bambu PLA Basic @BBL P1S 0.4 nozzle"),
    "P2S": dict(machine="Bambu Lab P2S 0.4 nozzle", tag="P2S", filament="Bambu PLA Basic @BBL P2S"),
    "A1": dict(machine="Bambu Lab A1 0.4 nozzle", tag="A1", filament="Bambu PLA Basic @BBL A1"),
}
ALL_PRINTERS = {**PRINTERS, **OTHER_PRINTERS}
# Other ways to print the site, left out of the whole-model totals (the plan uses the two halves).
SITE_ALTERNATIVES = ("site_model_1to1000_4colour", "site_model_1to1000_single_colour")
# One microSD card per campus, files numbered in the order of Model/bambu/PRINT_PLAN.md so the
# printer's (alphabetical) file list reads as the timetable.
CARDS = {
    "sd_card_Clifton_RISE_X1E": ("X1E", [("01", "building_1to100_plate5_"),
                                         ("02", "site_model_1to1000_4colour_halves_plate2_"),
                                         ("03", "site_model_1to1000_4colour_halves_plate1_"),
                                         ("alt", "site_model_1to1000_single_colour")]),
    "sd_card_City_X1C": ("X1C", [("01", "building_1to100_plate4_"), ("02", "building_1to100_plate3_"),
                                 ("03", "building_1to100_plate1_"), ("04", "furniture_trays_1to100_plate3_"),
                                 ("05", "building_1to100_plate2_"), ("06", "furniture_trays_1to100_plate2_"),
                                 ("07", "furniture_trays_1to100_plate1_")]),
}
BED = "Textured PEI Plate"
COLOURS = {"green": "#5E9B3C", "white": "#F2F0EB", "dark_green": "#2E5A2A", "orange": "#E8913A",
           "grey": "#9A9A9A", "dark_blue": "#1D2F5A", "light_grey": "#C9CCCE"}


def profiles_dir():
    loc = subprocess.run(["flatpak", "info", "--show-location", APP], capture_output=True, text=True, check=True)
    return Path(loc.stdout.strip()) / "files/share/BambuStudio/profiles/BBL"


def resolve(kind, name, root=None):
    """Flatten a Bambu system preset (follow 'inherits' and 'include') into one full config."""
    root = root or profiles_dir()
    data = json.loads((root / kind / f"{name}.json").read_text())
    full = resolve(kind, data["inherits"], root) if data.get("inherits") else {}
    for inc in data.get("include", []):
        full.update({k: v for k, v in json.loads((root / kind / f"{inc}.json").read_text()).items()
                     if k not in ("name", "instantiation")})
    full.update({k: v for k, v in data.items() if k not in ("include",)})
    return full


def write_settings(printer, process, colours, work):
    p = ALL_PRINTERS[printer]
    machine = resolve("machine", p["machine"])
    root = profiles_dir()
    name = f"{process} @BBL {p['tag']}"
    if not (root / "process" / f"{name}.json").exists():
        layer = process.split()[0]
        name = sorted(f.stem for f in (root / "process").glob(f"{layer} * @BBL {p['tag']}.json"))[0]
    proc = resolve("process", name, root)
    files = []
    for kind, cfg in (("machine", machine), ("process", proc)):
        cfg.update({"from": "system", "inherits": "", "instantiation": "true"})
        files.append(work / f"{kind}.json")
        files[-1].write_text(json.dumps(cfg, indent=1))
    fil = []
    for i, col in enumerate(colours):
        f = resolve("filament", p["filament"])
        f.update({"from": "system", "inherits": "", "instantiation": "true", "filament_colour": [COLOURS[col]]})
        fil.append(work / f"filament_{i + 1}.json")
        fil[-1].write_text(json.dumps(f, indent=1))
    return files, fil


# ------------------------------------------------------------------ projects
def _stl(sub, name):
    return str(PRINT / sub / name)


def _tray_plates(max_area=0.5 * 256 * 256):
    """Greedy split of all furniture trays into plates by footprint area (the slicer arranges each plate)."""
    import trimesh
    trays = sorted((p for d in ("trays_sla", "trays_fdm") for p in (PRINT / d).glob("*.stl")),
                   key=lambda p: -float(trimesh.load(p).extents[:2].prod()))
    plates, area = [[]], 0.0
    for p in trays:
        a = float(trimesh.load(p).extents[:2].prod()) * 1.3
        if area + a > max_area:
            plates.append([])
            area = 0.0
        plates[-1].append(str(p))
        area += a
    return plates


def _site_half(side, parts, assemble, centre=(138, 128)):
    """Objects for one half of the site, its parts assembled and centred on the bed."""
    import numpy as np
    import trimesh
    paths = [(PRINT / "site_halves" / f.replace(f"1to{C.SITE_SCALE}_", f"1to{C.SITE_SCALE}_{side}_"), n)
             for f, n in parts]
    paths = [(p, n) for p, n in paths if p.exists()]
    bounds = np.array([trimesh.load(p).bounds for p, _ in paths])
    mid = (bounds[:, 0, :2].min(0) + bounds[:, 1, :2].max(0)) / 2
    return [dict(path=str(p), filament=n, assemble=assemble, pos=(centre[0] - mid[0], centre[1] - mid[1]))
            for p, n in paths]


def projects():
    s = C.SITE_SCALE
    site_parts = [(f"site_1to{s}_1_terrain_green.stl", 1), (f"site_1to{s}_2_roads_paths_grey.stl", 2),
                  (f"site_1to{s}_3_existing_buildings_white.stl", 2), (f"site_1to{s}_4_trees_dark_green.stl", 3),
                  (f"site_1to{s}_5_proposal_orange.stl", 4)]
    b = f"building_1to{C.BUILDING_SCALE}_"
    return {
        "site_model_1to1000_4colour": dict(
            process="0.20mm Standard", colours=["green", "light_grey", "dark_green", "orange"],
            overrides={"enable_prime_tower": "0"},
            plates=[dict(name="Site 1:1000 (needs AMS, 4 colours)", arrange=False, objects=[
                dict(path=_stl("site", f), filament=n, assemble=1, pos=(138, 118)) for f, n in site_parts])]),
        "site_model_1to1000_4colour_halves": dict(       # each half fits one staffed lab day
            process="0.28mm Extra Draft", colours=["green", "light_grey", "dark_green", "orange"],
            overrides={"enable_prime_tower": "0"},
            plates=[dict(name=f"Site {side} half (4 colours)", arrange=False,
                         objects=_site_half(side, site_parts, i + 1))
                    for i, side in enumerate(("north", "south"))]),
        "site_model_1to1000_single_colour": dict(
            process="0.20mm Standard", colours=["white"], overrides={},
            plates=[dict(name="Site 1:1000 (one colour, paint after)", arrange=False, objects=[
                dict(path=_stl("site", f"site_1to{s}_single_colour.stl"), filament=1, pos=(138, 118))])]),
        "building_1to100": dict(
            process="0.20mm Standard", colours=["white", "light_grey", "dark_blue", "green"],
            overrides={"enable_prime_tower": "0"},
            plates=[                                     # one colour per plate: no AMS needed
                dict(name="Ground floor + cycle hub - white", arrange=True, objects=[
                    dict(path=_stl("building", b + "1_ground_floor.stl"), filament=1),
                    dict(path=_stl("building", b + "4_cycle_hub.stl"), filament=1)]),
                dict(name="First floor - white", arrange=True, objects=[
                    dict(path=_stl("building", b + "2_first_floor.stl"), filament=1)]),
                dict(name="Roofs - grey", arrange=True, objects=[
                    dict(path=_stl("building", b + "3_roof.stl"), filament=2),
                    dict(path=_stl("building", b + "5_cycle_hub_roof.stl"), filament=2)]),
                dict(name="PV strips - dark blue", arrange=True, objects=[
                    dict(path=_stl("building", b + "3_roof_pv_strips_dark_blue.stl"), filament=3)]),
                dict(name="Green roof - green", arrange=True, objects=[
                    dict(path=_stl("building", b + "5_cycle_hub_green_roof.stl"), filament=4)]),
            ]),
        "furniture_trays_1to100": dict(
            process="0.12mm Fine", colours=["light_grey"], overrides={},
            plates=[dict(name=f"Furniture trays {i + 1} - light grey", arrange=True,
                         objects=[dict(path=p, filament=1) for p in group])
                    for i, group in enumerate(_tray_plates())]),
    }


def assemble_list(project):
    plates = []
    for pl in project["plates"]:
        objs = []
        for o in pl["objects"]:
            d = {"path": o["path"], "count": 1, "filaments": [o["filament"]]}
            if o.get("assemble"):
                d["assemble_index"] = [o["assemble"]]
            if o.get("pos"):
                d.update(pos_x=[float(o["pos"][0])], pos_y=[float(o["pos"][1])], pos_z=[0.0])
            objs.append(d)
        plates.append({"plate_name": pl["name"], "need_arrange": pl["arrange"],
                       "plate_params": {"curr_bed_type": BED}, "objects": objs})
    return {"plates": plates}


# ------------------------------------------------------------------ thumbnails
# The Flathub CLI cannot open an OpenGL context (it requests "GL 3.5" = the GLFW version), so it
# writes no plate images. Render them here from the 3MF itself: same meshes, positions and colours.
def _meshes(z):
    """{(path, objectid): (vertices Nx3, triangles Mx3)} for every mesh object in the package."""
    import numpy as np
    out = {}
    for name in z.namelist():
        if not name.endswith(".model"):
            continue
        xml = z.read(name).decode()
        for oid, body in re.findall(r'<object id="(\d+)"[^>]*>(.*?)</object>', xml, re.S):
            if "<mesh>" not in body:
                continue
            v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', body), float)
            t = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), int)
            out[("/" + name, oid)] = (v, t)
    return out


def _plate_parts(z):
    """Per plate: list of (world vertices, triangles, rgb)."""
    import numpy as np
    meshes = _meshes(z)
    root = z.read("3D/3dmodel.model").decode()
    settings = z.read("Metadata/model_settings.config").decode()
    colours = json.loads(z.read("Metadata/project_settings.config")).get("filament_colour", ["#cccccc"])
    build = {oid: np.array([float(x) for x in tr.split()]).reshape(4, 3)
             for oid, tr in re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]+)"', root)}
    extr = {}
    for oid, body in re.findall(r'<object id="(\d+)">(.*?)</object>', settings, re.S):
        head = body.split("<part", 1)[0]
        default = int((re.findall(r'key="extruder" value="(\d+)"', head) or ["1"])[0])
        blocks = re.findall(r'(<part id="\d+".*?</part>)', body, re.S)
        extr[oid] = [int((re.findall(r'key="extruder" value="(\d+)"', b) or [default])[0]) for b in blocks] or [default]
    plates = {}
    for pid, body in re.findall(r'<plate>\s*<metadata key="plater_id" value="(\d+)"/>(.*?)</plate>', settings, re.S):
        plates[int(pid)] = re.findall(r'key="object_id" value="(\d+)"', body)
    out = {}
    for pid, oids in plates.items():
        parts = []
        for oid in oids:
            m = re.search(rf'<object id="{oid}"[^>]*>(.*?)</object>', root, re.S)
            comps = re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"[^>]*transform="([^"]+)"', m.group(1))
            B = build.get(oid, np.vstack([np.eye(3), np.zeros(3)]))
            for i, (path, cid, tr) in enumerate(comps):
                T = np.array([float(x) for x in tr.split()]).reshape(4, 3)
                v, t = meshes[(path, cid)]
                w = (v @ T[:3] + T[3]) @ B[:3] + B[3]
                e = extr.get(oid, [1])
                hexc = colours[min(len(colours), e[min(i, len(e) - 1)]) - 1].lstrip("#")[:6]
                parts.append((w, t, tuple(int(hexc[j:j + 2], 16) for j in (0, 2, 4))))
        out[pid] = parts
    return out


def render_plate(parts, size=512, ss=2):
    import numpy as np
    from PIL import Image, ImageDraw
    eye = np.array([0.55, -1.0, 0.95])
    f = -eye / np.linalg.norm(eye)
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    light = np.array([-0.3, -0.5, 1.0]); light /= np.linalg.norm(light)
    pitch = 256 * 1.2                                  # Bambu lays extra plates out on a grid
    lo = np.min([p[0][:, :2].min(0) for p in parts], axis=0) if parts else np.zeros(2)
    shift = np.append(np.floor((lo + 1) / pitch) * pitch, 0)
    parts = [(v - shift, t, c) for v, t, c in parts]
    bed = np.array([[0, 0, 0], [256, 0, 0], [256, 256, 0], [0, 256, 0.0]])
    allpts = np.vstack([bed] + [p[0] for p in parts])
    sx, sy = allpts @ r, allpts @ u
    scale = (size * ss * 0.92) / max(np.ptp(sx), np.ptp(sy))
    ox = size * ss / 2 - (sx.min() + sx.max()) / 2 * scale
    oy = size * ss / 2 + (sy.min() + sy.max()) / 2 * scale
    img = Image.new("RGB", (size * ss, size * ss), (38, 44, 48))
    d = ImageDraw.Draw(img)
    to2d = lambda P: np.stack([P @ r * scale + ox, oy - P @ u * scale], -1)  # noqa: E731
    d.polygon([tuple(p) for p in to2d(bed)], fill=(70, 74, 78), outline=(110, 114, 118))
    tris, cols, depth = [], [], []
    for v, t, rgb in parts:
        a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
        n = np.cross(b - a, c - a)
        nl = np.linalg.norm(n, axis=1) + 1e-12
        n /= nl[:, None]
        keep = (n @ f) < 0
        shade = 0.45 + 0.55 * np.clip(n[keep] @ light, 0, 1)
        P = to2d(np.stack([a[keep], b[keep], c[keep]], 1).reshape(-1, 3)).reshape(-1, 3, 2)
        tris.append(P)
        cols.append(np.clip(np.outer(shade, rgb), 0, 255).astype(int))
        depth.append(((a[keep] + b[keep] + c[keep]) / 3) @ f)
    if tris:
        P, Cc, D = np.concatenate(tris), np.concatenate(cols), np.concatenate(depth)
        for i in np.argsort(-D):
            d.polygon([tuple(p) for p in P[i]], fill=tuple(Cc[i]))
    return img.resize((size, size), Image.LANCZOS)


def add_thumbnails(path):
    """Write Metadata/plate_N.png (+ _small) into a Bambu 3MF; returns the images for checking."""
    with zipfile.ZipFile(path) as z:
        plates = _plate_parts(z)
        items = {n: z.read(n) for n in z.namelist()}
    imgs = {}
    for pid, parts in plates.items():
        img = render_plate(parts)
        imgs[pid] = img
        for name, im in ((f"Metadata/plate_{pid}.png", img), (f"Metadata/plate_{pid}_small.png", img.resize((128, 128)))):
            import io
            buf = io.BytesIO()
            im.save(buf, "PNG")
            items[name] = buf.getvalue()
    ct = items["[Content_Types].xml"].decode()
    if 'Extension="png"' not in ct:
        items["[Content_Types].xml"] = ct.replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>').encode()
    cfg = items["Metadata/model_settings.config"].decode()
    for pid in plates:
        tag = f'<metadata key="plater_id" value="{pid}"/>'
        if f"plate_{pid}.png" not in cfg:
            cfg = cfg.replace(tag, tag + f'\n    <metadata key="thumbnail_file" value="Metadata/plate_{pid}.png"/>', 1)
    items["Metadata/model_settings.config"] = cfg.encode()
    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in items.items():
            z.writestr(n, data)
    tmp.replace(path)
    return imgs


# ------------------------------------------------------------------ slicing
def run_cli(args, work):
    cmd = ["flatpak", "run", "--command=bambu-studio", APP, "--debug", "1", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=work)
    log = (r.stdout or "") + (r.stderr or "")
    (work / "cli.log").write_text(log)
    return r.returncode, log


def slice_info(path):
    """Per-plate print time (s) and filament grams from a sliced 3MF."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("Metadata/slice_info.config").decode()
    plates = []
    for block in re.findall(r"<plate>(.*?)</plate>", xml, re.S):
        meta = dict(re.findall(r'<metadata key="([^"]+)" value="([^"]*)"', block))
        fils = [(f.group(1), float(f.group(2)))
                for f in re.finditer(r'<filament id="(\d+)"[^>]*used_g="([\d.]+)"', block)]
        plates.append(dict(index=int(meta.get("index", 0)), seconds=float(meta.get("prediction", 0)),
                           grams=float(meta.get("weight", 0)), filaments=fils))
    return plates


def build(printer, name, project):
    work = OUT / "work" / printer / name
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    (settings, fils) = write_settings(printer, project["process"], project["colours"], work)
    if project["overrides"]:
        proc = json.loads(settings[1].read_text())
        proc.update(project["overrides"])
        settings[1].write_text(json.dumps(proc, indent=1))
    (work / "assemble.json").write_text(json.dumps(assemble_list(project), indent=1))
    base = ["--load-settings", ";".join(map(str, settings)), "--load-filaments", ";".join(map(str, fils)),
            "--load-assemble-list", str(work / "assemble.json"), "--outputdir", str(work)]
    dest = OUT / printer
    dest.mkdir(parents=True, exist_ok=True)
    info = []
    for i, plate in enumerate(project["plates"], 1):
        stem = f"{name}_plate{i}_{_slug(plate['name'])}" if len(project["plates"]) > 1 else name
        code, log = run_cli(base + ["--slice", str(i), "--export-3mf", f"{stem}.gcode.3mf"], work)
        sliced = work / f"{stem}.gcode.3mf"
        if code != 0 or not sliced.exists():
            raise RuntimeError(f"{printer}/{stem}: slicing failed (exit {code}), see {work / 'cli.log'}\n{log[-1500:]}")
        imgs = add_thumbnails(sliced)
        shutil.copy(sliced, dest / sliced.name)
        info += [dict(p, index=i, plate=plate["name"], file=sliced.name) for p in slice_info(sliced)]
        if printer == next(iter(PRINTERS)):
            (OUT / "plates").mkdir(parents=True, exist_ok=True)
            imgs[i].save(OUT / "plates" / f"{stem}.png")
    if printer == next(iter(PRINTERS)):
        run_cli(base + ["--export-3mf", f"{name}.3mf"], work)
        add_thumbnails(work / f"{name}.3mf")
        (OUT / "project").mkdir(parents=True, exist_ok=True)
        shutil.copy(work / f"{name}.3mf", OUT / "project" / f"{name}.3mf")
    return info


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]


def report(results):
    lines = ["# Sliced print report (Bambu Studio)", "",
             f"Real slicer estimates, PLA at GBP {C.PLA_GBP_PER_KG:.0f}/kg, {BED}. Times include filament changes.", ""]
    for printer, projs in results.items():
        lines += [f"## {printer} ({ALL_PRINTERS[printer]['machine']})", "",
                  "| File (one print job each) | What | Time | Filament | Cost |", "|---|---|---|---|---|"]
        tot_s = tot_g = 0.0
        for name, plates in projs.items():
            for p in plates:
                if name not in SITE_ALTERNATIVES:
                    tot_s += p["seconds"]
                    tot_g += p["grams"]
                lines.append(f"| `{p['file']}` | {p['plate']} | {p['seconds'] / 3600:.1f} h | {p['grams']:.0f} g | "
                             f"GBP {p['grams'] / 1000 * C.PLA_GBP_PER_KG:.2f} |")
        lines += ["", f"**Whole model (4-colour site in two halves + building + furniture): {tot_s / 3600:.1f} h of printing, "
                      f"{tot_g:.0f} g, about GBP {tot_g / 1000 * C.PLA_GBP_PER_KG:.2f}**", ""]
    (OUT / "slice_report.md").write_text("\n".join(lines))
    (OUT / "slice_report.json").write_text(json.dumps(results, indent=1))


def make_cards():
    for card, (printer, jobs) in CARDS.items():
        dest = OUT / card
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True)
        for num, prefix in jobs:
            (src,) = (OUT / printer).glob(f"{prefix}*.gcode.3mf")
            shutil.copy(src, dest / f"{num}_{src.name}")


def build_all(printers=None):
    results = {}
    for d in [*(printers or PRINTERS), "project", "plates", "work"]:
        shutil.rmtree(OUT / d, ignore_errors=True)
    for printer in printers or PRINTERS:
        results[printer] = {}
        for name, project in projects().items():
            print(f"slicing {printer} {name} ...", flush=True)
            results[printer][name] = build(printer, name, project)
    report(results)
    if all((OUT / printer).is_dir() for printer, _ in CARDS.values()):
        make_cards()
    shutil.rmtree(OUT / "work", ignore_errors=True)
    return results


if __name__ == "__main__":
    build_all(sys.argv[1:] or None)
