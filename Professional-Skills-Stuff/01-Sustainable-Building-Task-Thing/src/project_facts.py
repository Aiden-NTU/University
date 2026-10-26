"""Headline numbers that the poster walls and the Design Outline quote by name.

Everything comes from the model outputs (building metrics, costing schedule, slice report), so
the words on the walls and in the book can never disagree with the model.
"""
import csv
import json
from functools import lru_cache

from pyproj import Transformer

import building as B
import config as C


@lru_cache(maxsize=1)
def facts():
    m = json.loads((C.OUT_CAD / "building_metrics.json").read_text())
    met, tot = m["metrics"], m["totals"]
    lon, lat = Transformer.from_crs(27700, 4326, always_xy=True).transform(C.ORIGIN_E, C.ORIGIN_N)
    f = dict(
        gia_m2=f"{met['gross_internal_area_m2']:.0f}", pv_kwp=f"{met['pv_kwp']:.0f}", pv_modules=met["pv_modules"],
        pv_tilt=f"{met['pv_tilt_deg']:.0f}", rooms=sum("Corridor" not in r["name"] for r in B.ROOMS),
        length_m=f"{C.LENGTH:g}", depth_m=f"{C.DEPTH:g}", height_m=f"{B.ROOF_Z + B.RISE:.1f}", storeys=2,
        floor_to_floor_m=f"{C.FLOOR_TO_FLOOR:g}", bay_x_m=f"{C.BAY_X:g}", bay_y_m=f"{C.BAY_Y:g}",
        bays_x=C.N_BAYS_X, bays_y=C.N_BAYS_Y, annex_w_m=f"{C.ANNEX_W:g}", annex_d_m=f"{C.ANNEX_D:g}",
        ext_wall_mm=f"{C.EXT_WALL * 1000:.0f}",
        ffl=f"{C.FFL:.2f}", lat=f"{lat:.4f}", lon=f"{abs(lon):.4f}", lon_dir="W" if lon < 0 else "E",
        easting=f"{C.ORIGIN_E:.0f}", northing=f"{C.ORIGIN_N:.0f}",
        overhang_m=f"{met['overhang_m']:g}",
        shade_june=f"{met['overhang_shadow_depth_m']['21 June']:.1f}",
        shade_december=f"{met['overhang_shadow_depth_m']['21 December']:.1f}",
        fitout_gbp=f"{tot['fitout_capex_gbp']:,}", fitout_k=f"{tot['fitout_capex_gbp'] / 1000:.0f}",
        fitout_per_m2=f"{tot['fitout_capex_gbp'] / met['gross_internal_area_m2']:.0f}",
        lighting_saving_pct=f"{100 * (1 - tot['lighting_design_kwh'] / tot['lighting_baseline_kwh']):.0f}",
        lighting_saving_kwh=f"{tot['lighting_baseline_kwh'] - tot['lighting_design_kwh']:,}",
        co2_saving_kg=f"{tot['lighting_saving_kgco2e']:,}",
        lighting_design_kwh=f"{tot['lighting_design_kwh']:,}", lighting_baseline_kwh=f"{tot['lighting_baseline_kwh']:,}",
        lighting_saving_gbp=f"{tot['lighting_saving_gbp']:,}",
        lighting_kwh_per_m2=f"{tot['lighting_design_kwh'] / met['gross_internal_area_m2']:.1f}",
        volume_m3=f"{met['heated_volume_m3']:,.0f}", envelope_m2=f"{met['envelope_area_m2']:,.0f}",
        sa_v=f"{met['surface_area_to_volume']:.2f}",
        sun_june=f"{met['noon_sun_altitude_deg']['21 June']:.0f}",
        sun_december=f"{met['noon_sun_altitude_deg']['21 December']:.0f}",
        **{f"wwr_{k.lower()}": f"{100 * v:.0f}" for k, v in met["window_to_wall_ratio"].items()},
        **{f"glazing_{k.lower()}_m2": f"{v:.0f}" for k, v in met["glazing_area_m2"].items()},
        site_scale=C.SITE_SCALE, building_scale=C.BUILDING_SCALE,
        elec_p_per_kwh=f"{C.ELEC_GBP_PER_KWH * 100:.1f}", grid_kgco2e=f"{C.GRID_KGCO2E_PER_KWH:.3f}",
        light_uf=f"{C.LIGHT_UF:g}", light_mf=f"{C.LIGHT_MF:g}", baseline_lm_per_w=f"{C.BASELINE_LM_PER_W:.0f}",
    )
    qty, kwh = {}, {}
    with open(C.ROOT / "Costing" / "items.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            qty[row["type"]] = qty.get(row["type"], 0) + float(row["qty"] or 0)
            kwh[row["type"]] = kwh.get(row["type"], 0) + float(row["kwh_per_year"] or 0)
    f.update(server_racks=f"{qty.get('server_rack', 0):.0f}", server_kw=f"{C.SERVER_IT_KW_PER_RACK:g}",
             server_heat_mwh=f"{kwh.get('server_rack', 0) / 1000:.0f}", led_panels=f"{qty.get('led_panel', 0):.0f}",
             light_sensors=f"{qty.get('pir_lux_sensor', 0):.0f}", iaq_sensors=f"{qty.get('iaq_sensor', 0):.0f}",
             bike_spaces=f"{2 * qty.get('bike_rack_2tier', 0):.0f}",
             seats=f"{sum(qty.get(k, 0) for k in ('chair_stack', 'chair_task', 'stool', 'armchair')):.0f}")
    report = C.ROOT / "Model" / "bambu" / "slice_report.json"
    if report.exists():
        import bambu
        jobs = [p for name, plates in json.loads(report.read_text()).get("X1C", {}).items()
                if name not in bambu.SITE_ALTERNATIVES for p in plates]
        grams = sum(p["grams"] for p in jobs)
        f.update(print_hours=f"{sum(p['seconds'] for p in jobs) / 3600:.0f}", print_grams=f"{grams:,.0f}",
                 print_gbp=f"{grams / 1000 * C.PLA_GBP_PER_KG:.0f}", print_jobs=len(jobs))
    return {k: str(v) for k, v in f.items()}
