"""Single source of truth for the site, the building and the print settings.

Coordinates: local metres, x = east, y = north (British National Grid axes),
z = metres above Ordnance Datum Newlyn (same as the LiDAR). The local origin is
the south-west corner of the main building block, so the Fusion 360 model, the
printed models and the web twin all share one reference point.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "Site" / "raw"
OUT_PRINT = ROOT / "Model" / "print"
OUT_CAD = ROOT / "Design" / "exports"
OUT_WEB = ROOT / "Web-Twin" / "data"

# --- Site data extent (BNG, EPSG:27700) -----------------------------------
DATA_BBOX = (454800.0, 335200.0, 455300.0, 335700.0)   # E0, N0, E1, N1 (500 m square)
PLOT_OSM_WAY = "29348021"                                # "Students' Car Park", NTU Clifton

# --- Building placement ----------------------------------------------------
ORIGIN_E = 454976.0          # BNG easting of building SW corner
ORIGIN_N = 335433.0          # BNG northing of building SW corner
FFL = 55.45                  # finished floor level (m AOD): car park mean 55.1 m + 350 mm plinth
# Grid north vs true north differs by ~0.65 deg here; ignored at this scale.

# --- Building geometry (metres) -------------------------------------------
BAY_X = 4.0                  # 6 bays east-west  -> 24.0 m (fits a 256 mm print bed at 1:100)
BAY_Y = 4.8                  # 3 bays north-south -> 14.4 m (shallow plan = daylight + cross-ventilation)
N_BAYS_X = 6
N_BAYS_Y = 3
FLOOR_TO_FLOOR = 3.6
SLAB = 0.30                  # CLT floor + acoustic layer
EXT_WALL = 0.36              # CLT 100 + wood-fibre insulation 220 + cladding 40
INT_WALL = 0.15
SOUTH_OVERHANG = 1.2         # slab-edge brise-soleil depth (see shading calc in building_metrics)
SAWTOOTH_TILT_DEG = 25.0     # south-facing PV slopes
ANNEX_W = 6.0                # single-storey cycle hub on the east end
ANNEX_D = 9.6

LENGTH = BAY_X * N_BAYS_X
DEPTH = BAY_Y * N_BAYS_Y

# --- Site redesign (local metres) -----------------------------------------
# Remaining car park (east triangle of the old car park) under solar canopies.
CARPORT_ROWS = [  # (x0, y0, x1, y1) canopy footprints in local coords
    (40.0, -14.0, 82.0, -8.5),
    (46.0, -2.0, 92.0, 3.5),
]
CARPORT_HEIGHT = 3.2

# --- Print settings ---------------------------------------------------------
SITE_SCALE = 1000            # 1:1000 site model
SITE_PRINT_SIZE_MM = 230.0   # square edge: clears the X1C/P1S wiper corner and P2S rear zone on a 256 mm bed
SITE_CENTRE_LOCAL = (10.0, -15.0)   # centre of printed site area, local coords
SITE_BASE_MM = 3.0           # solid base under lowest terrain point
SITE_VERTICAL_EXAGGERATION = 1.0
TREE_CANOPY_CAP_M = 18.0
ROAD_INLAY_MM = 0.6          # depth of separate-colour road/path layer

BUILDING_SCALE = 100         # 1:100 dollhouse model
PEG_D_MM = 1.8               # locating pegs (holes get +0.4 mm clearance)
PEG_H_MM = 2.0
HOLE_CLEARANCE_MM = 0.4

# --- Costs used by print_cost.py (assumptions - confirm with NTU print service) --
PLA_GBP_PER_KG = 20.0        # Bambu PLA Basic retail is roughly GBP 20-25/kg
PLA_DENSITY = 1.24           # g/cm3
RESIN_GBP_PER_L = 160.0      # Formlabs Standard resin ~GBP 150-180/L inc VAT
FDM_INFILL = 0.15
FDM_SHELL_MM = 0.8           # 2 perimeters / ~4 top-bottom layers
FDM_G_PER_HOUR = 18.0        # rough Bambu throughput on detailed parts
RESIN_SUPPORT_FACTOR = 1.35  # supports, raft and wastage

# --- Running-cost assumptions (state these in the Design Outline and cite a source) --------
ELEC_GBP_PER_KWH = 0.25      # verify: DESNZ "Prices of fuels purchased by non-domestic consumers"
GRID_KGCO2E_PER_KWH = 0.177  # verify: DESNZ/DEFRA GHG conversion factors (current year)
LIGHT_UF = 0.6               # utilisation factor (lumen method)
LIGHT_MF = 0.8               # maintenance factor
BASELINE_LM_PER_W = 60.0     # business-as-usual fluorescent fittings, no controls
SERVER_IT_KW_PER_RACK = 3.0  # placeholder until the energy model sizes the edge data centre

CATALOGUE = ROOT / "Costing" / "catalogue.csv"
OUT_COSTING = ROOT / "Costing"
