"""Estimate filament/resin use, cost and print time for every STL in Model/print.

FDM mass = density x (shell volume + infill x remaining volume), where the shell is the
outer skin (surface area x shell thickness, capped at the part volume).
SLA prints solid, plus a factor for supports, raft and wastage.
All prices are assumptions in config.py - check them against the NTU print service tariff.
"""
import json

import trimesh

import config as C

BEDS = {"Bambu Lab (X1/P1)": (256, 256, 256), "Formlabs Form 3": (145, 145, 185), "Formlabs Form 4": (200, 125, 210)}


def fdm(mesh):
    v = mesh.volume / 1000                                   # cm3
    shell = min(v, mesh.area / 100 * C.FDM_SHELL_MM / 10)
    grams = C.PLA_DENSITY * (shell + C.FDM_INFILL * (v - shell))
    return grams, grams / 1000 * C.PLA_GBP_PER_KG, grams / C.FDM_G_PER_HOUR


def sla(mesh):
    ml = mesh.volume / 1000 * C.RESIN_SUPPORT_FACTOR
    return ml, ml / 1000 * C.RESIN_GBP_PER_L


def fits(ext, bed):
    a, b = sorted(ext[:2])
    x, y = sorted(bed[:2])
    return a <= x and b <= y and ext[2] <= bed[2]


def report():
    rows = []
    for path in sorted(C.OUT_PRINT.rglob("*.stl")):
        if "single_colour" in path.name or path.parent.name == "site_halves":
            continue
        m = trimesh.load(path)
        ext = [round(e, 1) for e in m.extents]
        group = path.parent.name
        if group == "trays_sla":
            ml, gbp = sla(m)
            rows.append(dict(part=path.name, group=group, process="SLA resin", amount=f"{ml:.1f} ml",
                             gbp=gbp, hours=None, size_mm=ext,
                             fits=fits(ext, BEDS["Formlabs Form 3"]) or fits(ext, BEDS["Formlabs Form 4"])))
        else:
            g, gbp, hrs = fdm(m)
            rows.append(dict(part=path.name, group=group, process="FDM PLA", amount=f"{g:.0f} g",
                             gbp=gbp, hours=hrs, size_mm=ext, fits=fits(ext, BEDS["Bambu Lab (X1/P1)"])))
    totals = {}
    for r in rows:
        t = totals.setdefault(r["group"], dict(gbp=0.0, hours=0.0))
        t["gbp"] += r["gbp"]
        t["hours"] += r["hours"] or 0
    grand = sum(t["gbp"] for t in totals.values())

    lines = ["# Print cost estimate", "",
             f"Assumptions (edit in `src/config.py`): PLA GBP {C.PLA_GBP_PER_KG}/kg, {int(C.FDM_INFILL * 100)}% infill, "
             f"{C.FDM_SHELL_MM} mm shell, ~{C.FDM_G_PER_HOUR:.0f} g/h; resin GBP {C.RESIN_GBP_PER_L}/L "
             f"x{C.RESIN_SUPPORT_FACTOR} for supports and waste. Confirm real prices with the NTU print service.", "",
             "| Part | Process | Material | Est. cost | Est. time | Size (mm) | Fits bed |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        hrs = f"{r['hours']:.1f} h" if r["hours"] else "-"
        lines.append(f"| {r['part']} | {r['process']} | {r['amount']} | GBP {r['gbp']:.2f} | {hrs} | "
                     f"{' x '.join(str(e) for e in r['size_mm'])} | {'yes' if r['fits'] else 'NO'} |")
    lines += ["", "| Group | Cost | FDM hours |", "|---|---|---|"]
    for g, t in totals.items():
        lines.append(f"| {g} | GBP {t['gbp']:.2f} | {t['hours']:.1f} |")
    lines += ["", f"**Total material estimate: GBP {grand:.2f}** (budget GBP 40)", ""]
    (C.OUT_PRINT / "print_cost_estimate.md").write_text("\n".join(lines))
    (C.OUT_PRINT / "print_cost_estimate.json").write_text(json.dumps(dict(rows=rows, totals=totals, total_gbp=grand),
                                                                     indent=1, default=float))
    return rows, totals, grand


if __name__ == "__main__":
    rows, totals, grand = report()
    print((C.OUT_PRINT / "print_cost_estimate.md").read_text())
