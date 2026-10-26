"""Room-by-room schedule: quantities come from the 3D model, lighting from the lumen method.

Lumen method:  N = E x A / (lamp lumens x UF x MF)
Design energy: N x W x hours x daylight factor x occupancy factor
Baseline:      same lux from fluorescent fittings at 60 lm/W, no daylight or occupancy controls
"""
import csv
import math
from collections import Counter

import building as B
import config as C

LED_LUMENS = 4000.0          # per 600 x 600 panel (catalogue: led_panel)
ALWAYS_ON = {"server_rack"}
NO_IAQ = {"G06", "F06", "G07", "G08", "G09", "G11"}


def catalogue():
    with open(C.CATALOGUE, newline="") as f:
        return {r["type"]: r for r in csv.DictReader(f)}


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def lighting(room, area, cat):
    panel = cat["led_panel"]
    need_lm = room["lux"] * area / (C.LIGHT_UF * C.LIGHT_MF)
    n = max(1, math.ceil(need_lm / LED_LUMENS))
    w = n * _num(panel["power_w"])
    hours = room["hours"]
    design_kwh = w * hours * room["daylight"] * room["occupancy"] / 1000
    base_w = need_lm / C.BASELINE_LM_PER_W
    base_kwh = base_w * hours / 1000
    return dict(fittings=n, design_w=round(w), design_w_per_m2=round(w / area, 1),
                design_kwh=round(design_kwh), baseline_w=round(base_w), baseline_kwh=round(base_kwh))


def build():
    cat = catalogue()
    rows, rooms = [], []
    for room in B.ROOMS:
        area = B.room_floor(room).area
        # Placeables without catalogue_type are visual/physical props, not costed fit-out.
        counts = Counter(k for k, _, _ in B.furniture(room["id"]) if not k.startswith("__placeable__"))
        light = lighting(room, area, cat)
        counts["led_panel"] = light["fittings"]
        counts["pir_lux_sensor"] = max(1, math.ceil(area / 40))
        if room["id"] not in NO_IAQ:
            counts["iaq_sensor"] = max(1, math.ceil(area / 60))

        items, capex, kwh, unpriced = [], 0.0, 0.0, 0
        for kind, qty in sorted(counts.items()):
            c = cat.get(kind, {"item": kind, "spec": "", "unit_cost_gbp": "", "power_w": 0, "use_factor": 0,
                               "lifespan_yrs": "", "cost_status": "not in catalogue", "sustainability_note": ""})
            unit = _num(c["unit_cost_gbp"], None)
            if kind == "led_panel":
                item_kwh = light["design_kwh"]
            elif kind in ALWAYS_ON:
                item_kwh = qty * C.SERVER_IT_KW_PER_RACK * 8760
            else:
                item_kwh = qty * _num(c["power_w"]) * room["hours"] * _num(c["use_factor"]) / 1000
            life = _num(c["lifespan_yrs"], None)
            cost = unit * qty if unit is not None else None
            row = dict(room_id=room["id"], room=room["name"], level=room["level"], type=kind, item=c["item"],
                       spec=c["spec"], qty=qty, unit_cost_gbp=unit, capex_gbp=cost,
                       kwh_per_year=round(item_kwh), running_gbp_per_year=round(item_kwh * C.ELEC_GBP_PER_KWH),
                       lifespan_yrs=life,
                       replacement_gbp_per_year=round(cost / life) if cost and life else None,
                       sustainability_note=c["sustainability_note"], cost_status=c["cost_status"],
                       source=c.get("source", ""))
            rows.append(row)
            items.append({k: row[k] for k in ("item", "spec", "qty", "unit_cost_gbp", "capex_gbp", "kwh_per_year",
                                                "running_gbp_per_year", "sustainability_note", "cost_status")})
            if cost is None:
                unpriced += 1
            else:
                capex += cost
            kwh += item_kwh
        saving_kwh = light["baseline_kwh"] - light["design_kwh"]
        rooms.append(dict(
            id=room["id"], name=room["name"], level=room["level"], area_m2=round(area, 1), use=room["use"],
            notes=room["notes"], lux=room["lux"], hours=room["hours"], tray=room["tray_process"],
            polygon=[[round(x, 2), round(y, 2)] for x, y in B.room_floor_poly(room).exterior.coords],
            lighting=light,
            lighting_saving=dict(kwh=round(saving_kwh), gbp=round(saving_kwh * C.ELEC_GBP_PER_KWH),
                                 kgco2e=round(saving_kwh * C.GRID_KGCO2E_PER_KWH)),
            fitout_capex_gbp=round(capex), unpriced_items=unpriced,
            kwh_per_year=round(kwh), running_gbp_per_year=round(kwh * C.ELEC_GBP_PER_KWH),
            items=items))
    return rows, rooms


def write():
    rows, rooms = build()
    C.OUT_COSTING.mkdir(parents=True, exist_ok=True)
    with open(C.OUT_COSTING / "items.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows, rooms


if __name__ == "__main__":
    rows, rooms = write()
    for r in rooms:
        print(f"{r['id']} {r['name']:<32} {r['area_m2']:>6} m2  fit-out GBP {r['fitout_capex_gbp']:>7,}  "
              f"light {r['lighting']['design_kwh']:>5} vs {r['lighting']['baseline_kwh']:>5} kWh/yr")
    print("total fit-out (priced items): GBP", f"{sum(r['fitout_capex_gbp'] for r in rooms):,}")
