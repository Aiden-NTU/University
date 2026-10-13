"""Rebuild everything from open data: site download, print STLs, print cost, room schedule, web twin.

    python src/build_all.py            # full rebuild (downloads are cached in Site/raw)
    python src/build_all.py --skip-print
"""
import shutil
import sys
import time

import bambu
import config as C
import earth_export
import fetch_site
import print_cost
import print_export
import schedule
import web_export


def step(name, fn):
    t = time.time()
    print(f"== {name}")
    fn()
    print(f"   done in {time.time() - t:.1f} s")


if __name__ == "__main__":
    C.RAW.mkdir(parents=True, exist_ok=True)
    step("site data (OSM, EA LiDAR, aerial)", lambda: (fetch_site.fetch_osm(), fetch_site.fetch_lidar(), fetch_site.fetch_aerial()))
    if "--skip-print" not in sys.argv:
        step("print STLs", print_export.export_all)
        step("print cost estimate", print_cost.report)
    step("room schedule", schedule.write)
    step("web twin data", web_export.export_all)
    step("Google Earth KMZ", earth_export.export)
    if "--skip-print" not in sys.argv and shutil.which("flatpak"):
        step("Bambu Studio sliced print files", bambu.build_all)
