from dash import Dash
import dash_bootstrap_components as dbc
import geopandas as gpd

from app.layout import build_layout
from app.callbacks import register_callbacks
from src.config import MODEL_FILE


def extract_crime_types(model_file=MODEL_FILE):
    """
    Load model results and infer available crime types
    from aggregated crime_* columns.
    """
    if not model_file.exists():
        raise RuntimeError(
            "Required model artefact not found:\n"
            f"  {model_file}\n\n"
            "This application expects precomputed model outputs.\n"
            "Run run_pipeline.py locally and commit the resulting\n"
            "data/processed/model_results.parquet file."
        )

    gdf = gpd.read_parquet(model_file)

    crime_cols = [
        c for c in gdf.columns
        if c.startswith("crime_") and c != "crime_count_total"
    ]

    if not crime_cols:
        raise RuntimeError(
            "Model file loaded successfully, but no crime_* columns were found.\n"
            "Check that the pipeline completed correctly."
        )

    crime_types = [c.replace("crime_", "").upper() for c in crime_cols]
    return sorted(crime_types)


# ---------------------------------------------------------------------
# Initialise app (import-safe for Gunicorn)
# ---------------------------------------------------------------------

crime_types = extract_crime_types()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Chicago Crime Analysis",
)

# Lazy-loaded layout
app.layout = lambda: build_layout(crime_types)

# Register callbacks
register_callbacks(app)

# ---------------------------------------------------------------------
# NOTE:
# No app.run() here.
# Gunicorn is responsible for serving the app in production.
# ---------------------------------------------------------------------
