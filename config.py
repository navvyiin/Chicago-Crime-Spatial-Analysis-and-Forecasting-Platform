from pathlib import Path
import os

# ---------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------
# Assumes this file lives in: <project_root>/src/config.py
BASE = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------
# Data directories
# ---------------------------------------------------------------------

DATA_DIR = BASE / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"

# Allow override via environment variable (useful in containers / volumes)
DATA_PROCESSED = Path(
    os.environ.get("DATA_PROCESSED_DIR", DATA_PROCESSED)
)

# ---------------------------------------------------------------------
# RAW DATA (pipeline-only; never required at runtime)
# ---------------------------------------------------------------------

CRIME_CSV = DATA_RAW / "crimes.csv"
STREETLIGHT_CSV = DATA_RAW / "street_lights_all_out.csv"
CTA_BUS_SHP = DATA_RAW / "CTA_BusStops.shp"
CITY_LIMITS_SHP = DATA_RAW / "Chicago_City_Limits.shp"

# ---------------------------------------------------------------------
# INTERMEDIATE PIPELINE OUTPUTS
# (used during pipeline execution, not required by Dash)
# ---------------------------------------------------------------------

GRID_FILE = DATA_PROCESSED / "hex_grid.gpkg"
FEATURES_FILE = DATA_PROCESSED / "features.parquet"
FORECAST_FILE = DATA_PROCESSED / "forecast_monthly.parquet"
REPORTS_DIR = DATA_PROCESSED / "reports"

# ---------------------------------------------------------------------
# RUNTIME ARTEFACTS
# (MUST exist for the Dash app to start)
# ---------------------------------------------------------------------

MODEL_FILE = DATA_PROCESSED / "model_results.parquet"
MONTHLY_FILE = DATA_PROCESSED / "monthly_cell_crime.parquet"

# ---------------------------------------------------------------------
# Spatial configuration
# ---------------------------------------------------------------------

# Projected CRS suitable for Chicago (UTM Zone 16N)
DEFAULT_CRS = 32616

# ---------------------------------------------------------------------
# Runtime / execution context flags
# ---------------------------------------------------------------------

# True when running inside a container (Fly.io / Docker)
IS_CONTAINER = os.environ.get("FLY_APP_NAME") is not None

# True when running the Dash app (read-only mode expected)
IS_DASH_RUNTIME = (BASE / "run_app.py").exists() and not __name__ == "__main__"

# True when running the analytics pipeline
IS_PIPELINE_RUNTIME = (BASE / "run_pipeline.py").exists()

# ---------------------------------------------------------------------
# Sanity checks (fail fast, but only when appropriate)
# ---------------------------------------------------------------------

def assert_runtime_artifacts_exist():
    """
    Ensure required artefacts exist before starting the Dash app.
    """
    missing = []
    for path in [MODEL_FILE, MONTHLY_FILE]:
        if not path.exists():
            missing.append(path)

    if missing:
        msg = (
            "Required runtime artefacts are missing:\n"
            + "\n".join(f"  - {p}" for p in missing)
            + "\n\nThis application expects precomputed outputs.\n"
            "Run run_pipeline.py locally or as a batch job first."
        )
        raise RuntimeError(msg)
