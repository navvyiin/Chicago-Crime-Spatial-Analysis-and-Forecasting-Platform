import pandas as pd
import geopandas as gpd

from .config import (
    CRIME_CSV,
    STREETLIGHT_CSV,
    CTA_BUS_SHP,
    CITY_LIMITS_SHP,
    DEFAULT_CRS,
)

# ---------------------------------------------------------------------
# Chunked crime data loader (critical for large CSVs)
# ---------------------------------------------------------------------

def iter_crime_chunks(chunksize: int = 500_000):
    """
    Yield crime data in chunks as GeoDataFrames.

    Designed for very large CSVs (8+ million rows).
    Keeps memory usage bounded.
    """
    for chunk in pd.read_csv(
        CRIME_CSV,
        chunksize=chunksize,
        low_memory=False,
    ):
        # Standardise column names
        chunk.columns = (
            chunk.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )


        # Parse timestamps (Chicago crime format)
        chunk["date"] = pd.to_datetime(
            chunk["date"],
            format="%m/%d/%Y %I:%M:%S %p",
            errors="coerce",
        )

        # Drop unusable records early
        chunk = chunk.dropna(subset=["date", "latitude", "longitude"])

        # Temporal components
        chunk["month"] = chunk["date"].dt.to_period("M").astype(str)
        chunk["hour"] = chunk["date"].dt.hour
        chunk["dow"] = chunk["date"].dt.dayofweek

        # Convert to GeoDataFrame (WGS84 → projected)
        gdf = gpd.GeoDataFrame(
            chunk,
            geometry=gpd.points_from_xy(chunk["longitude"], chunk["latitude"]),
            crs="EPSG:4326",
        ).to_crs(epsg=DEFAULT_CRS)

        yield gdf


# ---------------------------------------------------------------------
# Optional small-data loader (do NOT use for full CSV)
# ---------------------------------------------------------------------

def load_crimes(primary_types=None):
    """
    Load crime data into memory.

    ⚠️ Only safe for small subsets or testing.
    For full historical data, use iter_crime_chunks().
    """
    df = pd.read_csv(CRIME_CSV, low_memory=False)
    df.columns = df.columns.str.lower()

    df["date"] = pd.to_datetime(
        df["date"],
        format="%m/%d/%Y %I:%M:%S %p",
        errors="coerce",
    )
    df = df.dropna(subset=["date", "latitude", "longitude"])

    if primary_types:
        df = df[df["primary_type"].isin(primary_types)]

    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["hour"] = df["date"].dt.hour
    df["dow"] = df["date"].dt.dayofweek

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    ).to_crs(epsg=DEFAULT_CRS)

    return gdf


# ---------------------------------------------------------------------
# Streetlights
# ---------------------------------------------------------------------

def load_streetlights():
    df = pd.read_csv(
        STREETLIGHT_CSV,
        parse_dates=["Creation Date"],
        low_memory=False,
    )
    df = df.dropna(subset=["Latitude", "Longitude"])

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
        crs="EPSG:4326",
    )

    return gdf.to_crs(epsg=DEFAULT_CRS)


# ---------------------------------------------------------------------
# Bus stops
# ---------------------------------------------------------------------

def load_bus_stops():
    gdf = gpd.read_file(CTA_BUS_SHP)

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)

    return gdf.to_crs(epsg=DEFAULT_CRS)


# ---------------------------------------------------------------------
# City boundary
# ---------------------------------------------------------------------

def load_boundary():
    gdf = gpd.read_file(CITY_LIMITS_SHP)
    return gdf.to_crs(epsg=DEFAULT_CRS)