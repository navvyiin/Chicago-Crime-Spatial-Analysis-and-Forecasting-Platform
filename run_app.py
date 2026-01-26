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
        raise FileNotFoundError(
            f"Model file not found: {model_file}. "
            "Run run_pipeline.py first."
        )

    gdf = gpd.read_parquet(model_file)

    crime_cols = [
        c for c in gdf.columns
        if c.startswith("crime_") and c != "crime_count_total"
    ]

    crime_types = [c.replace("crime_", "").upper() for c in crime_cols]
    return sorted(crime_types)

# Initialise app

crime_types = extract_crime_types()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Chicago Crime Analysis 2025",
)

# Lazy-loaded layout
app.layout = lambda: build_layout(crime_types)

# Register callbacks
register_callbacks(app)

# Run server

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=8050,

    )
