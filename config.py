from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

DATA_RAW = BASE / "data" / "raw"
DATA_PROCESSED = BASE / "data" / "processed"

CRIME_CSV = DATA_RAW / "crimes.csv"
STREETLIGHT_CSV = DATA_RAW / "street_lights_all_out.csv"
CTA_BUS_SHP = DATA_RAW / "CTA_BusStops.shp"
CITY_LIMITS_SHP = DATA_RAW / "Chicago_City_Limits.shp"

GRID_FILE = DATA_PROCESSED / "hex_grid.gpkg"
FEATURES_FILE = DATA_PROCESSED / "features.parquet"
MODEL_FILE = DATA_PROCESSED / "model_results.parquet"
MONTHLY_FILE = DATA_PROCESSED / "monthly_cell_crime.parquet"
REPORTS_DIR = DATA_PROCESSED / "reports"
FORECAST_FILE = DATA_PROCESSED / "forecast_monthly.parquet"

DEFAULT_CRS = 32616  # projected CRS for Chicago region