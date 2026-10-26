"""Generated tables and charts for the Design Outline (see book.py).

A chapter asks for one with a pair of marker lines:

    <!-- auto:lighting -->
    <!-- /auto -->

and every build refreshes what sits between them. Each entry in BLOCKS is a function that
returns Markdown; add a function here to offer a new table or chart.
"""
import datetime
import io
import json
import math
from collections import defaultdict
from functools import lru_cache
from os.path import relpath

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import requests  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Polygon as MplPolygon  # noqa: E402

import building as B  # noqa: E402
import config as C  # noqa: E402
import schedule  # noqa: E402
from project_facts import facts  # noqa: E402

FIGS = C.ROOT / "Book" / "figures" / "auto"
PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"
PVGIS_CACHE = C.OUT_CAD / "pvgis.json"
PV_SYSTEM_LOSS_PCT = 14          # PVGIS default for cabling, inverter and soiling losses

INK, ACCENT, WOOD, GREY, TINT = "#1f2933", "#2a6f73", "#c8742c", "#9aa5b1", "#e6eeee"
CATEGORY = {
    "led_panel": "Lighting and controls", "pir_lux_sensor": "Lighting and controls",
    "iaq_sensor": "Lighting and controls",
    "server_rack": "IT, AV and data", "cooling_distribution_unit": "IT, AV and data",
    "display_large": "IT, AV and data", "display_screen": "IT, AV and data", "display_wall": "IT, AV and data",
    "laser_cutter": "Making and teaching", "printer_3d": "Making and teaching", "workbench": "Making and teaching",
    "lectern": "Making and teaching", "table_teach": "Making and teaching",
    "heat_pump": "Plant and energy", "battery": "Plant and energy", "mvhr": "Plant and energy",
    "thermal_store": "Plant and energy", "rainwater_pumpset": "Plant and energy",
    "wc_pan": "Sanitary and water", "basin_counter": "Sanitary and water", "shower_cubicle": "Sanitary and water",
    "water_refill": "Sanitary and water", "kitchen_counter": "Sanitary and water",
    "bike_rack_2tier": "Cycling", "ebike_charging": "Cycling", "lockers": "Cycling", "bench": "Cycling",
}


# ---------------------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def metrics():
    return json.loads((C.OUT_CAD / "building_metrics.json").read_text())


@lru_cache(maxsize=1)
def sched():
    return schedule.build()


def pvgis():
    """Annual and monthly PV yield for the roof array from the EU's PVGIS service (cached)."""
    met, f = metrics()["metrics"], facts()
    lon = float(f["lon"]) * (-1 if f["lon_dir"] == "W" else 1)
    params = dict(lat=float(f["lat"]), lon=lon, peakpower=met["pv_kwp"], loss=PV_SYSTEM_LOSS_PCT,
                  angle=met["pv_tilt_deg"], aspect=0)
    cached = json.loads(PVGIS_CACHE.read_text()) if PVGIS_CACHE.exists() else None
    if cached and cached["params"] == params:
        return cached
    try:
        r = requests.get(PVGIS_URL, params={**params, "outputformat": "json"}, timeout=60)
        r.raise_for_status()
        d = r.json()
    except requests.RequestException as e:
        if cached:
            print(f"note: PVGIS unreachable ({e}); using the cached yield for the previous PV layout")
            return cached
        raise RuntimeError("PVGIS is needed once to estimate the PV yield; connect to the internet and rebuild") from e
    out = dict(params=params, fetched=datetime.date.today().isoformat(),
               annual_kwh=round(d["outputs"]["totals"]["fixed"]["E_y"]),
               monthly_kwh=[round(m["E_m"]) for m in d["outputs"]["monthly"]["fixed"]],
               radiation_db=d["inputs"]["meteo_data"]["radiation_db"],
               years=f"{d['inputs']['meteo_data']['year_min']}-{d['inputs']['meteo_data']['year_max']}")
    PVGIS_CACHE.write_text(json.dumps(out, indent=1) + "\n")
    return out


def extra_facts():
    """Book-only placeholders on top of project_facts.facts()."""
    pv, tot = pvgis(), metrics()["totals"]
    rows, _ = sched()
    other = sum(r["kwh_per_year"] for r in rows if r["type"] not in ("led_panel", "server_rack"))
    server = sum(r["kwh_per_year"] for r in rows if r["type"] == "server_rack")
    unpriced = sorted({r["item"] for r in rows if r["capex_gbp"] is None})
    led_w = float(schedule.catalogue()["led_panel"]["power_w"])
    vol = float(facts()["volume_m3"].replace(",", ""))
    return dict(
        cube_side_m=f"{vol ** (1 / 3):.1f}", sa_v_cube=f"{6 / vol ** (1 / 3):.2f}",
        led_lumens=f"{schedule.LED_LUMENS:,.0f}", led_watts=f"{led_w:g}",
        led_lm_per_w=f"{schedule.LED_LUMENS / led_w:.0f}",
        server_vs_pv=f"{server / pv['annual_kwh']:.1f}",
        pv_value_gbp=f"{pv['annual_kwh'] * C.ELEC_GBP_PER_KWH:,.0f}",
        pv_yield_kwh=f"{pv['annual_kwh']:,}", pv_yield_mwh=f"{pv['annual_kwh'] / 1000:.1f}",
        pv_specific_yield=f"{pv['annual_kwh'] / pv['params']['peakpower']:.0f}",
        pv_loss_pct=str(PV_SYSTEM_LOSS_PCT), pvgis_db=pv["radiation_db"], pvgis_years=pv["years"].replace("-", "–"),
        pv_vs_lighting=f"{pv['annual_kwh'] / tot['lighting_design_kwh']:.0f}",
        pv_best_month_kwh=f"{max(pv['monthly_kwh']):,}", pv_worst_month_kwh=f"{min(pv['monthly_kwh']):,}",
        equipment_kwh=f"{other:,.0f}", unpriced_count=str(len(unpriced)), unpriced_items=", ".join(unpriced).lower(),
        server_it_kwh=f"{server:,.0f}",
        build_date=datetime.date.today().strftime("%-d %B %Y"),
    )


# ---------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------
def _gbp(v):
    return f"£{v:,.0f}"


def _cell(v):
    return str(v).replace("|", "\\|").replace("\n", " ")


def table(head, rows, align, caption=None):
    out = [f"Table: {caption}", ""] if caption else []
    out.append("| " + " | ".join(head) + " |")
    out.append("| " + " | ".join({"r": "---:", "c": ":---:"}.get(a, "---") for a in align) + " |")
    out += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def _style():
    for f in ("SourceSans3-Regular.otf", "SourceSans3-Semibold.otf", "SourceSans3-Bold.otf", "SourceSans3-It.otf"):
        font_manager.fontManager.addfont(str(C.ROOT / "src" / "fonts" / f))
    plt.rcParams.update({
        "font.family": "Source Sans 3", "font.size": 8.5, "axes.edgecolor": GREY, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 9, "axes.titleweight": "semibold", "svg.hashsalt": "heat-exchange",
        "axes.axisbelow": True, "grid.color": "#dde3e8", "grid.linewidth": 0.6,
    })


def figure(fig, name, chapter, caption, width=None, raster=False):
    """Save a chart as SVG, or JPEG for photo-like figures (only rewritten when it changes); return its Markdown."""
    FIGS.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    if raster:
        fig.savefig(buf, format="jpg", dpi=300, bbox_inches="tight", pil_kwargs={"quality": 85, "optimize": True})
    else:
        fig.savefig(buf, format="svg", bbox_inches="tight", metadata={"Date": None})
    plt.close(fig)
    path = FIGS / f"{name}.{'jpg' if raster else 'svg'}"
    if not path.exists() or path.read_bytes() != buf.getvalue():
        path.write_bytes(buf.getvalue())
    attr = f'{{: style="width:{width}"}}' if width else ""
    return f"![{caption}]({relpath(path, chapter.path.parent)}){attr}"


MM = 1 / 25.4


# ---------------------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------------------
def key_facts(ctx, chapter, caption="Key figures, generated from the design model"):
    f, met = ctx.facts, metrics()["metrics"]
    rows = [
        ("Gross internal area", f"{f['gia_m2']} m²", "3D model"),
        ("Main block", f"{f['length_m']} × {f['depth_m']} m, {f['storeys']} storeys at {f['floor_to_floor_m']} m",
         "Structural grid"),
        ("Cycle hub (single storey)", f"{f['annex_w_m']} × {f['annex_d_m']} m", "Structural grid"),
        ("Rooms", f"{f['rooms']} (plus corridors)", "Room schedule"),
        ("Heated volume", f"{f['volume_m3']} m³", "3D model"),
        ("Envelope area", f"{f['envelope_m2']} m²", "3D model"),
        ("Surface area to volume ratio", f"{f['sa_v']} m⁻¹", "Envelope ÷ volume"),
        ("Window-to-wall ratio N / E / S / W", f"{f['wwr_n']}% / {f['wwr_e']}% / {f['wwr_s']}% / {f['wwr_w']}%",
         "3D model"),
        ("Roof PV", f"{f['pv_modules']} modules, {met['pv_kwp']:g} kWp at {f['pv_tilt']}°", "3D model"),
        ("PV yield", f"{f['pv_yield_kwh']} kWh/yr ({f['pv_specific_yield']} kWh/kWp)", "PVGIS [@pvgis]"),
        ("Lighting energy, design vs baseline", f"{f['lighting_design_kwh']} vs {f['lighting_baseline_kwh']} kWh/yr "
         f"(−{f['lighting_saving_pct']}%)", "Lumen method"),
        ("Fit-out, priced items", f"£{f['fitout_gbp']} (£{f['fitout_per_m2']}/m²)", "Costing schedule"),
    ]
    return table(("Quantity", "Value", "Source"), rows, "lll", caption)


def rooms(ctx, chapter, caption="Room schedule (net floor areas from the 3D model)"):
    _, rs = sched()
    rows = [(r["id"], r["name"], {"GF": "Ground", "FF": "First"}[r["level"]], f"{r['area_m2']:.1f}", r["use"])
            for r in rs]
    total = sum(r["area_m2"] for r in rs)
    rows.append(("", "**Total net area**", "", f"**{total:.0f}**", ""))
    return table(("Code", "Room", "Floor", "Area (m²)", "Use"), rows, "lllrl", caption)


def lighting(ctx, chapter, caption="Lighting design against a fluorescent, uncontrolled baseline"):
    _, rs = sched()
    rows, d_tot, b_tot = [], 0, 0
    for r in rs:
        L = r["lighting"]
        d_tot += L["design_kwh"]
        b_tot += L["baseline_kwh"]
        saving = 1 - L["design_kwh"] / L["baseline_kwh"] if L["baseline_kwh"] else 0
        rows.append((r["id"], r["name"], r["lux"], L["fittings"], f"{L['design_w_per_m2']:.1f}",
                     f"{L['design_kwh']:,}", f"{L['baseline_kwh']:,}", f"{saving:.0%}"))
    rows.append(("", "**Total**", "", f"**{sum(r['lighting']['fittings'] for r in rs)}**", "",
                 f"**{d_tot:,}**", f"**{b_tot:,}**", f"**{1 - d_tot / b_tot:.0%}**"))
    return table(("Code", "Room", "Lux", "Fittings", "W/m²", "Design kWh/yr", "Baseline kWh/yr", "Saving"),
                 rows, "llrrrrrr", caption)


def costs_by_room(ctx, chapter, caption="Fit-out cost and running cost by room (indicative prices)"):
    rows_all, rs = sched()
    rows = [(r["id"], r["name"], _gbp(r["fitout_capex_gbp"]), r["unpriced_items"] or "",
             _gbp(r["running_gbp_per_year"])) for r in rs]
    rows.append(("", "**Total**", f"**{_gbp(sum(r['fitout_capex_gbp'] for r in rs))}**",
                 f"**{sum(r['unpriced_items'] for r in rs)}**", f"**{_gbp(sum(r['running_gbp_per_year'] for r in rs))}**"))
    return table(("Code", "Room", "Fit-out", "Awaiting quote", "Running £/yr"), rows, "llrrr", caption)


def _categories():
    rows, _ = sched()
    cats = defaultdict(lambda: dict(capex=0.0, lines=0, unpriced=[]))
    for r in rows:
        c = cats[CATEGORY.get(r["type"], "Furniture and fittings")]
        c["lines"] += 1
        if r["capex_gbp"] is None:
            c["unpriced"].append(r["item"])
        else:
            c["capex"] += r["capex_gbp"]
    return dict(sorted(cats.items(), key=lambda kv: -kv[1]["capex"]))


def costs_by_category(ctx, chapter, caption="Fit-out cost by category"):
    cats = _categories()
    total = sum(c["capex"] for c in cats.values())
    rows = [(name, c["lines"], _gbp(c["capex"]), f"{c['capex'] / total:.0%}",
             ", ".join(sorted(set(c["unpriced"]))) or "") for name, c in cats.items()]
    rows.append(("**Total**", f"**{sum(c['lines'] for c in cats.values())}**", f"**{_gbp(total)}**", "**100%**", ""))
    return table(("Category", "Lines", "Priced cost", "Share", "Awaiting quote"), rows, "lrrrl", caption)


def cost_items(ctx, chapter, caption="Itemised fit-out schedule (from Costing/items.csv)"):
    rows, _ = sched()
    out = []
    for r in rows:
        status = "quote needed" if r["capex_gbp"] is None else "indicative" if "indicative" in r["cost_status"] else r["cost_status"]
        out.append((r["room_id"], r["item"], r["spec"], f"{r['qty']:g}",
                    _gbp(r["unit_cost_gbp"]) if r["unit_cost_gbp"] is not None else "",
                    _gbp(r["capex_gbp"]) if r["capex_gbp"] is not None else "", status))
    return table(("Room", "Item", "Specification", "Qty", "Unit", "Total", "Status"), out, "lllrrrl", caption)


def energy_balance(ctx, chapter, caption=None):
    f, pv, tot = ctx.facts, pvgis(), metrics()["totals"]
    rows_all, _ = sched()
    caption = caption or (f"Annual energy flows modelled so far, priced at {C.ELEC_GBP_PER_KWH * 100:.1f} p/kWh "
                          f"[@desnz_qep2026] with grid carbon at {C.GRID_KGCO2E_PER_KWH} kgCO₂e/kWh [@desnz_ghg2026]")
    server = sum(r["kwh_per_year"] for r in rows_all if r["type"] == "server_rack")
    other = sum(r["kwh_per_year"] for r in rows_all if r["type"] not in ("led_panel", "server_rack"))
    flows = [
        ("Roof PV generation", pv["annual_kwh"],
         f"{f['pv_kwp']} kWp, {f['pv_tilt']}° south, {f['pv_loss_pct']}% system losses [@pvgis]"),
        ("Lighting, as designed", tot["lighting_design_kwh"], "LED with daylight and occupancy control"),
        ("Lighting, baseline (for comparison)", tot["lighting_baseline_kwh"],
         f"Fluorescent at {f['baseline_lm_per_w']} lm/W, no controls"),
        ("Other equipment", other, "Catalogue power × hours × use factor"),
        ("Server IT load (all of it becomes heat)", server, f"{f['server_racks']} racks × {f['server_kw']} kW × 8,760 h"),
    ]
    rows = [(n, f"{k:,.0f}", _gbp(k * C.ELEC_GBP_PER_KWH), f"{k * C.GRID_KGCO2E_PER_KWH / 1000:,.1f}", b)
            for n, k, b in flows]
    rows.append(("Space heating, hot water and ventilation fans", "*to be modelled*", "", "", "Energy model: see [[Limitations and next steps]]"))
    return table(("Flow", "kWh/yr", "£/yr", "tCO₂e/yr", "Basis"), rows, "lrrrl", caption)


def lumen_example(ctx, chapter, room="G04", caption=None):
    """The lumen-method calculation for one room, step by step, using the same numbers as the schedule."""
    src = next((r for r in B.ROOMS if r["id"] == room), None)
    if src is None:
        raise ValueError(f"lumen_example: no room {room!r}; use a code from the room schedule")
    _, rs = sched()
    r = next(x for x in rs if x["id"] == room)
    cat = schedule.catalogue()["led_panel"]
    E, A, uf, mf, lm, w = r["lux"], r["area_m2"], C.LIGHT_UF, C.LIGHT_MF, schedule.LED_LUMENS, float(cat["power_w"])
    need = E * A / (uf * mf)
    L = r["lighting"]
    caption = caption or f"Lumen-method lighting calculation for the {r['name']} ({room})"
    steps = [
        ("Target illuminance, E", "Maintained illuminance in line with BS EN 12464-1 [@bsen12464]", f"{E} lux"),
        ("Floor area, A", "From the 3D model", f"{A:.1f} m²"),
        ("Lumens needed", f"E × A ÷ (UF × MF) = {E} × {A:.1f} ÷ ({uf} × {mf})", f"{need:,.0f} lm"),
        ("Number of panels, N", f"lumens needed ÷ {lm:,.0f} lm per panel = {need / lm:.2f}, rounded up", f"{L['fittings']}"),
        ("Installed power", f"{L['fittings']} × {w:.0f} W, which is {L['design_w_per_m2']} W per m² of floor",
         f"{L['design_w']:,} W"),
        ("Hours in use", "Timetable assumption for this room", f"{r['hours']:,} h/yr"),
        ("Controls", f"Daylight dimming {src['daylight']} × occupancy switching {src['occupancy']}",
         f"{src['daylight'] * src['occupancy']:.2f}"),
        ("Design energy", f"{L['design_w']:,} W × {r['hours']:,} h × {src['daylight'] * src['occupancy']:.2f} ÷ 1000",
         f"{L['design_kwh']:,} kWh/yr"),
        ("Baseline energy", f"{need:,.0f} lm ÷ {C.BASELINE_LM_PER_W:.0f} lm/W × {r['hours']:,} h ÷ 1000, no controls",
         f"{L['baseline_kwh']:,} kWh/yr"),
    ]
    return table(("Step", "Working", "Result"), steps, "llr", caption)


def print_jobs(ctx, chapter, caption="3D print jobs as sliced in Bambu Studio (X1 Carbon)"):
    import bambu
    report = json.loads((C.ROOT / "Model" / "bambu" / "slice_report.json").read_text())
    rows, secs, grams = [], 0.0, 0.0
    for name, plates in report.get("X1C", {}).items():
        if name in bambu.SITE_ALTERNATIVES:
            continue
        for p in plates:
            rows.append((p["plate"], f"{p['seconds'] / 3600:.1f}", f"{p['grams']:.0f}",
                         _gbp(p["grams"] / 1000 * C.PLA_GBP_PER_KG)))
            secs += p["seconds"]
            grams += p["grams"]
    rows.append(("**Total**", f"**{secs / 3600:.1f}**", f"**{grams:,.0f}**", f"**{_gbp(grams / 1000 * C.PLA_GBP_PER_KG)}**"))
    return table(("Print job", "Hours", "PLA (g)", f"Cost at £{C.PLA_GBP_PER_KG:.0f}/kg"), rows, "lrrr", caption)


def team(ctx, chapter, caption="Team and roles"):
    rows = [(a.get("name") or "*to be added*", a.get("student_id") or "", a.get("role", ""))
            for a in ctx.meta.get("authors", [])]
    return table(("Name", "Student number", "Role"), rows, "lll", caption)


def contributions(ctx, chapter, caption="Who wrote which section"):
    rows = []
    for ch in ctx.chapters:
        if ch.title and ch.meta.get("authors"):
            rows.append((ch.title, ch.meta["authors"]))
    if not rows:
        return "*Add an `authors:` line to the top of each chapter file and this table fills itself in.*"
    return table(("Section", "Written by"), rows, "ll", caption)


# ---------------------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------------------
def chart_lighting(ctx, chapter, caption="Annual lighting energy by room: design against baseline"):
    _style()
    _, rs = sched()
    rs = [r for r in rs if r["lighting"]["baseline_kwh"] >= 50][::-1]
    fig, ax = plt.subplots(figsize=(160 * MM, (28 + 5.2 * len(rs)) * MM))
    y = range(len(rs))
    ax.barh([i + 0.2 for i in y], [r["lighting"]["baseline_kwh"] for r in rs], 0.4, color=GREY, label="Baseline: fluorescent, no controls")
    ax.barh([i - 0.2 for i in y], [r["lighting"]["design_kwh"] for r in rs], 0.4, color=ACCENT, label="Design: LED + daylight/occupancy control")
    ax.set_yticks(list(y), [f"{r['id']}  {r['name']}" for r in rs])
    ax.set_xlabel("kWh per year")
    ax.grid(axis="x")
    ax.legend(loc="lower right", frameon=False)
    return figure(fig, "lighting_by_room", chapter, caption)


def chart_costs(ctx, chapter, caption="Priced fit-out cost by category"):
    _style()
    cats = {k: v for k, v in _categories().items() if v["capex"] > 0}
    names = list(cats)[::-1]
    fig, ax = plt.subplots(figsize=(160 * MM, (22 + 8 * len(names)) * MM))
    vals = [cats[n]["capex"] for n in names]
    ax.barh(names, vals, color=[WOOD if i == len(names) - 1 else ACCENT for i in range(len(names))], height=0.6)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.01, i, _gbp(v), va="center", fontsize=8)
    ax.set_xlim(0, max(vals) * 1.15)
    ax.set_xlabel("£ (indicative prices, excluding plant awaiting quotes)")
    ax.grid(axis="x")
    return figure(fig, "costs_by_category", chapter, caption)


def chart_pv(ctx, chapter, caption=None):
    _style()
    pv = pvgis()
    caption = caption or (f"Monthly PV generation from the {pv['params']['peakpower']:g} kWp roof array "
                          f"(PVGIS, {pv['radiation_db']} {pv['years'].replace('-', '–')})")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    light = metrics()["totals"]["lighting_design_kwh"] / 12
    fig, ax = plt.subplots(figsize=(160 * MM, 62 * MM))
    ax.bar(months, pv["monthly_kwh"], color=ACCENT, width=0.65, label="PV generation")
    ax.axhline(light, color=WOOD, lw=1.4, label="Average monthly lighting use (design)")
    ax.set_ylabel("kWh per month")
    ax.grid(axis="y")
    ax.legend(loc="upper right", frameon=False)
    return figure(fig, "pv_monthly", chapter, caption)


def chart_shading(ctx, chapter, caption=None):
    _style()
    f, met = ctx.facts, metrics()["metrics"]
    lat, oh = float(f["lat"]), met["overhang_m"]
    caption = caption or (f"Noon sun height and the depth of south glazing shaded by the {oh:g} m overhang "
                          f"through the year (latitude {lat:.1f}° N)")
    days = list(range(1, 366))
    decl = [23.44 * math.sin(math.radians(360 * (284 + n) / 365)) for n in days]
    alt = [90 - lat + d for d in decl]
    depth = [oh * math.tan(math.radians(a)) for a in alt]
    fig, ax = plt.subplots(figsize=(160 * MM, 62 * MM))
    ax.plot(days, depth, color=ACCENT, lw=1.8, label="Shaded depth of glass below the overhang (m)")
    ax.set_ylabel("Shaded depth (m)")
    ax.set_xlim(1, 365)
    ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
                  ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.grid(axis="y")
    ax2 = ax.twinx()
    ax2.plot(days, alt, color=WOOD, lw=1.2, ls="--", label="Noon sun altitude (°)")
    ax2.set_ylabel("Sun altitude (°)")
    ax2.spines["right"].set_visible(True)
    for n in (172, 355):
        k = n - 1
        ax.annotate(f"{depth[k]:.2f} m", (n, depth[k]), textcoords="offset points", xytext=(0, 6), ha="center",
                    fontsize=8, color=ACCENT)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="lower center", frameon=False, fontsize=7.5)
    return figure(fig, "overhang_shading", chapter, caption)


def plans(ctx, chapter, caption="Ground and first floor plans with room codes (generated from the 3D model)"):
    _style()
    fig, axes = plt.subplots(2, 1, figsize=(160 * MM, 150 * MM))
    span = C.LENGTH + C.ANNEX_W
    for ax, (level, title) in zip(axes, (("GF", "Ground floor"), ("FF", "First floor"))):
        outline = B.FOOTPRINT_MAIN if level == "FF" else B.FOOTPRINT_MAIN.union(B.FOOTPRINT_ANNEX)
        for g in getattr(outline, "geoms", [outline]):
            ax.add_patch(MplPolygon(list(g.exterior.coords), closed=True, fill=False, ec=INK, lw=2.2, zorder=3))
        lx0, ly0, lx1, ly1 = B.LIFT.bounds
        ax.text((lx0 + lx1) / 2, (ly0 + ly1) / 2, "lift", ha="center", va="center", fontsize=6.5, color=GREY)
        sx0, sx1 = (B.STAIR_X0, 6.0)
        if level == "GF":
            ax.add_patch(MplPolygon([(sx0, B.STAIR_Y0), (sx1, B.STAIR_Y0), (sx1, B.STAIR_Y1), (sx0, B.STAIR_Y1)],
                                    closed=True, fc="white", ec=GREY, lw=0.7, zorder=2))
            for k in range(1, 9):
                x = sx0 + (sx1 - sx0) * k / 9
                ax.plot([x, x], [B.STAIR_Y0, B.STAIR_Y1], color=GREY, lw=0.4, zorder=2)
            ax.text((sx0 + sx1) / 2, B.STAIR_Y0 - 0.45, "stair", ha="center", fontsize=6.5, color=GREY, zorder=2)
        for r in B.ROOMS:
            if r["level"] != level:
                continue
            for g in getattr(r["poly"], "geoms", [r["poly"]]):
                ax.add_patch(MplPolygon(list(g.exterior.coords), closed=True, fc=TINT if "Corridor" not in r["name"] else "white",
                                        ec=GREY, lw=0.7))
            p = r["poly"].representative_point()
            x0, y0, x1, y1 = r["poly"].bounds
            rot = 90 if (y1 - y0) > 1.6 * (x1 - x0) and (x1 - x0) < 3 else 0
            ax.text(p.x, p.y, r["id"], ha="center", va="center", fontsize=7, weight="semibold", color=INK, rotation=rot)
        if level == "FF":
            vx0, vy0, vx1, vy1 = B.VOID.bounds
            ax.plot([vx0, vx1], [vy0, vy1], color=GREY, lw=0.6)
            ax.plot([vx0, vx1], [vy1, vy0], color=GREY, lw=0.6)
            ax.text((vx0 + vx1) / 2, vy1 + 0.4, "void", ha="center", fontsize=6.5, color=GREY)
        ax.set_title(title, loc="left")
        ax.set_xlim(-1.5, span + 1.5)
        ax.set_ylim(-3.2, C.DEPTH + 1.2)
        ax.set_aspect("equal")
        ax.axis("off")
        for k, fc in ((0, INK), (5, "white")):
            ax.add_patch(MplPolygon([(k, -2.2), (k + 5, -2.2), (k + 5, -1.9), (k, -1.9)], closed=True, fc=fc, ec=INK, lw=0.6))
        for k in (0, 5, 10):
            ax.text(k, -2.9, f"{k} m", ha="center", fontsize=6.5)
        ax.annotate("N", xy=(span + 0.6, C.DEPTH - 0.2), xytext=(span + 0.6, C.DEPTH - 2.4), ha="center",
                    fontsize=8, weight="bold", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1))
    fig.tight_layout()
    return figure(fig, "floor_plans", chapter, caption)


def site_plan(ctx, chapter, half="120", caption=None):
    """Existing and proposed aerial views of the plot, side by side, with scale bar and north arrow."""
    from PIL import Image
    import site_model as S
    _style()
    half = float(half)
    e0, n0, e1, n1 = C.DATA_BBOX
    land = S.proposal_landscape()
    cx, cy = land["plot"].centroid.x, land["plot"].centroid.y
    caption = caption or ("The Students' Car Park today (left) and as proposed (right). Aerial imagery: Esri, Maxar, "
                          "Earthstar Geographics [@esri_imagery]; proposal overlaid from the design model")
    ext = (e0 - C.ORIGIN_E, e1 - C.ORIGIN_E, n0 - C.ORIGIN_N, n1 - C.ORIGIN_N)
    fig, axes = plt.subplots(1, 2, figsize=(160 * MM, 82 * MM))
    for ax, (img, title) in zip(axes, ((C.RAW / "aerial_bng.jpg", "Existing"),
                                       (C.OUT_CAD / "site_plan_proposed_texture.jpg", "Proposed"))):
        im = Image.open(img).convert("RGB")
        W, H = im.size
        box = [int((cx - half - ext[0]) / (ext[1] - ext[0]) * W), int((ext[3] - (cy + half)) / (ext[3] - ext[2]) * H),
               int((cx + half - ext[0]) / (ext[1] - ext[0]) * W), int((ext[3] - (cy - half)) / (ext[3] - ext[2]) * H)]
        crop = im.crop(box).resize((1100, 1100), Image.LANCZOS)
        ax.imshow(crop, extent=(cx - half, cx + half, cy - half, cy + half))
        ax.set_xlim(cx - half, cx + half)
        ax.set_ylim(cy - half, cy + half)
        ax.set_title(title, loc="left")
        ax.axis("off")
        x0, y0 = cx - half + 10, cy - half + 10
        ax.add_patch(MplPolygon([(x0 - 4, y0 - 5), (x0 + 58, y0 - 5), (x0 + 58, y0 + 14), (x0 - 4, y0 + 14)],
                                closed=True, fc="white", alpha=0.8, lw=0))
        for k, fc in ((0, INK), (25, "white")):
            ax.add_patch(MplPolygon([(x0 + k, y0 + 7), (x0 + k + 25, y0 + 7), (x0 + k + 25, y0 + 10),
                                     (x0 + k, y0 + 10)], closed=True, fc=fc, ec=INK, lw=0.6))
        for k in (0, 25, 50):
            ax.text(x0 + k, y0 - 1.5, f"{k} m", ha="center", fontsize=6.5)
        ax.annotate("N", xy=(cx + half - 12, cy + half - 8), xytext=(cx + half - 12, cy + half - 34), ha="center",
                    fontsize=8, weight="bold", color="white", arrowprops=dict(arrowstyle="-|>", color="white", lw=1.2))
    b = B.FOOTPRINT.centroid
    axes[1].annotate("The Heat Exchange", xy=(b.x, b.y), xytext=(b.x - 70, b.y + 75), fontsize=7, weight="semibold",
                     color=INK, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5),
                     arrowprops=dict(arrowstyle="-", color="white", lw=0.9))
    fig.tight_layout(w_pad=1.0)
    return figure(fig, "site_plan", chapter, caption, raster=True)


BLOCKS = dict(
    key_facts=key_facts, rooms=rooms, lighting=lighting, costs_by_room=costs_by_room,
    costs_by_category=costs_by_category, cost_items=cost_items, energy_balance=energy_balance,
    lumen_example=lumen_example, site_plan=site_plan,
    print_jobs=print_jobs, team=team, contributions=contributions,
    chart_lighting=chart_lighting, chart_costs=chart_costs, chart_pv=chart_pv, chart_shading=chart_shading,
    plans=plans,
)
