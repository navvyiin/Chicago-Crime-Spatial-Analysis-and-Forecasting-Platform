import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
from src.config import MODEL_FILE, MONTHLY_FILE

# Load model output

gdf = gpd.read_parquet(MODEL_FILE).to_crs(4326)
gdf["id"] = gdf.index.astype(str)

# Ensure Gi* and KDE fields exist even if absent
# Fix Gi* naming
if "gi_zscore" in gdf.columns and "gi_z" not in gdf.columns:
    gdf["gi_z"] = gdf["gi_zscore"]
elif "gi_z" not in gdf.columns:
    gdf["gi_z"] = np.nan

if "kde_intensity" not in gdf.columns:
    gdf["kde_intensity"] = np.nan

# Interval width for uncertainty maps
if "pred_lower" in gdf.columns and "pred_upper" in gdf.columns:
    gdf["pred_interval_width"] = gdf["pred_upper"] - gdf["pred_lower"]

# Load monthly table

try:
    monthly_df = pd.read_parquet(MONTHLY_FILE)
except Exception:
    monthly_df = pd.DataFrame()
# Helper: observed crime type column

def get_observed_column(crime_type):
    if crime_type == "ALL":
        return "crime_count_total"
    return f"crime_{crime_type.lower()}"


# Build STATIC map (non-animated)

def make_static_map(model_choice, color_scale, crime_type, hour=None, dows=None):
    df = gdf.copy()

    # Select value column
    if model_choice == "observed":
        value_col = get_observed_column(crime_type)
    elif model_choice == "hotspot":
        value_col = "gi_star"
    elif model_choice == "kde":
        value_col = "kde_intensity"
    elif model_choice == "risk":
        value_col = "risk_score"
    elif model_choice == "uncertainty":
        value_col = "pred_interval_width"
    else:
        # pred_poisson / pred_nb / pred_rf / pred_gwr / pred_gb
        value_col = model_choice

    df["value"] = df[value_col]

    # Hover fields

    hover_fields = {
        "value": True,
        "crime_count_total": True,
        "streetlight_count": True,
        "bus_count": True,
        "pred_poisson": True,
        "pred_nb": True,
        "pred_rf": True,
        "pred_gb": True,
        "pred_gwr": True,
        "risk_score": True,
        "risk_quantile": True,
        "priority_rank": True,
        "gi_star": True,
        "kde_intensity": True,
    }

    # Plotly choropleth

    fig = px.choropleth_mapbox(
        df,
        geojson=df.set_index("id").geometry.__geo_interface__,
        locations="id",
        color="value",
        mapbox_style="carto-darkmatter",
        zoom=9,
        center={"lat": 41.8781, "lon": -87.6298},
        opacity=0.75,
        color_continuous_scale=color_scale,
        hover_data=hover_fields,
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig


# Build ANIMATED map (month-over-month)

def make_animated_map(crime_type, color_scale, hour, dows):
    if monthly_df.empty:
        # No animation available
        fig = px.scatter(
            title="No monthly data available to animate"
        )
        return fig

    df = monthly_df.copy()

    # Filter crime type

    if crime_type != "ALL":
        df = df[df["primary_type"] == crime_type]

    # Hour-of-day filter

    df = df[df["hour"] == hour]

    # Day-of-week filter

    if dows:
        df = df[df["dow"].isin(dows)]

    # Aggregate to cell+month

    df = (
        df.groupby(["cell_id", "month"], as_index=False)
        .agg({"crime_count": "sum"})
    )

    # Attach geometry

    df = df.merge(
        gdf[["cell_id", "id"]],
        on="cell_id",
        how="left",
    )

    # Animated map
    
    fig = px.choropleth_mapbox(
        df,
        geojson=gdf.set_index("id").geometry.__geo_interface__,
        locations="id",
        color="crime_count",
        animation_frame="month",
        mapbox_style="carto-darkmatter",
        zoom=9,
        center={"lat": 41.8781, "lon": -87.6298},
        opacity=0.75,
        color_continuous_scale=color_scale,
        hover_data={"crime_count": True, "month": True},
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig
