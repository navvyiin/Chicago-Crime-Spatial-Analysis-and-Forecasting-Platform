from pathlib import Path

# Base paths

# Project root (…/project/)
BASE = Path(__file__).resolve().parents[1]

# Data roots
DATA_DIR = BASE / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"

# RAW DATA (pipeline-only, never required at runtime)
CRIME_CSV = DATA_RAW / "crimes.csv"
STREETLIGHT_CSV = DATA_RAW / "street_lights_all_out.csv"
CTA_BUS_SHP = DATA_RAW / "CTA_BusStops.shp"
CITY_LIMITS_SHP = DATA_RAW / "Chicago_City_Limits.shp"

# INTERMEDIATE PIPELINE OUTPUTS (not needed by Dash)
GRID_FILE = DATA_PROCESSED / "hex_grid.gpkg"
FEATURES_FILE = DATA_PROCESSED / "features.parquet"
FORECAST_FILE = DATA_PROCESSED / "forecast_monthly.parquet"
REPORTS_DIR = DATA_PROCESSED / "reports"

# RUNTIME ARTEFACTS (MUST exist for the app to start)
MODEL_FILE = DATA_PROCESSED / "model_results.parquet"
MONTHLY_FILE = DATA_PROCESSED / "monthly_cell_crime.parquet"

# Spatial configuration
# Projected CRS suitable for Chicago (UTM Zone 16N)
DEFAULT_CRS = 32616

# Utility flags
# True when running the Dash app (used only for sanity checks/logging)
IS_RUNTIME = (BASE / "run_app.py").exists()
