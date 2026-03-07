from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def _resolve_case_insensitive_dir(parent: Path, *candidates: str) -> Path:
    """
    Return the first existing directory among the given candidate names,
    falling back to the first candidate if none exist. This keeps things
    working across case-sensitive (Linux) and case-insensitive (Windows) FS.
    """
    for name in candidates:
        p = parent / name
        if p.exists():
            return p
    # Fallback: use the first candidate name
    return parent / candidates[0]


# Root data directory (handles "data" vs "Data")
DATA_ROOT = _resolve_case_insensitive_dir(BASE, "data", "Data")

# Raw vs processed subdirectories (handles "raw" vs "Raw")
DATA_RAW = _resolve_case_insensitive_dir(DATA_ROOT, "raw", "Raw")
DATA_PROCESSED = _resolve_case_insensitive_dir(DATA_ROOT, "processed", "Processed")

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
MODEL_METRICS_FILE = DATA_PROCESSED / "model_metrics.parquet"

DEFAULT_CRS = 32616  # projected CRS for Chicago region