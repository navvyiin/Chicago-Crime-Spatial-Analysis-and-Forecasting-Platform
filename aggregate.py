import geopandas as gpd
import pandas as pd
from geopandas.tools import sjoin

from .load_data import (
    iter_crime_chunks,
    load_streetlights,
    load_bus_stops,
)
from .config import GRID_FILE, FEATURES_FILE, MONTHLY_FILE

DEFAULT_CRIME_TYPES = ["BURGLARY", "ROBBERY", "ASSAULT"]


# ---------------------------------------------------------------------
# Helper: count point features per grid cell
# ---------------------------------------------------------------------

def count_points(points_gdf, grid_gdf):
    """
    Spatial join: count how many point features fall inside each grid cell.
    """
    joined = sjoin(
        points_gdf,
        grid_gdf[["cell_id", "geometry"]],
        how="left",
        predicate="within",
    )
    return joined.groupby("cell_id").size()


# ---------------------------------------------------------------------
# Main aggregation routine
# ---------------------------------------------------------------------

def aggregate_features(primary_types=None, chunksize: int = 500_000):
    """
    Aggregate crime and environmental features onto a hex grid.

    Crime data are processed in chunks to support very large CSV files.
    """
    if primary_types is None:
        primary_types = DEFAULT_CRIME_TYPES

    # ------------------------------------------------------------------
    # Load grid
    # ------------------------------------------------------------------

    grid = gpd.read_file(GRID_FILE)
    grid = gpd.GeoDataFrame(grid, geometry="geometry")
    grid.reset_index(drop=True, inplace=True)
    grid["cell_id"] = grid["cell_id"].astype(int)

    print("\n[AGGREGATE DEBUG] Loaded grid from disk:")
    print("[AGGREGATE DEBUG] Columns:", grid.columns)
    print("[AGGREGATE DEBUG] Rows:", len(grid))
    print("[AGGREGATE DEBUG] CRS:", grid.crs)

    # ------------------------------------------------------------------
    # Initialise counters
    # ------------------------------------------------------------------

    grid["crime_count_total"] = 0
    for ctype in primary_types:
        grid[f"crime_{ctype.lower()}"] = 0

    # ------------------------------------------------------------------
    # Load environmental context (small datasets)
    # ------------------------------------------------------------------

    lights = load_streetlights()
    bus = load_bus_stops()

    grid["streetlight_count"] = (
        count_points(lights, grid)
        .reindex(grid["cell_id"])
        .fillna(0)
        .astype(int)
    )

    grid["bus_count"] = (
        count_points(bus, grid)
        .reindex(grid["cell_id"])
        .fillna(0)
        .astype(int)
    )

    # ------------------------------------------------------------------
    # Chunked crime aggregation
    # ------------------------------------------------------------------

    monthly_records = []

    print("\n[AGGREGATE] Processing crime data in chunks...")

    for i, crimes_chunk in enumerate(iter_crime_chunks(chunksize=chunksize), start=1):

        print(f"[AGGREGATE] Chunk {i} loaded ({len(crimes_chunk)} rows)")

        joined = sjoin(
            crimes_chunk,
            grid[["cell_id", "geometry"]],
            how="inner",
            predicate="within",
        )

        if joined.empty:
            continue

        # Total crime counts
        total_counts = joined.groupby("cell_id").size()
        grid.loc[total_counts.index, "crime_count_total"] += total_counts.values

        # Per-type counts
        for ctype in primary_types:
            subset = joined[joined["primary_type"] == ctype]
            if not subset.empty:
                c = subset.groupby("cell_id").size()
                grid.loc[c.index, f"crime_{ctype.lower()}"] += c.values

        # Monthly / temporal table
        monthly_chunk = (
            joined
            .groupby(
                ["cell_id", "month", "hour", "dow", "primary_type"],
                as_index=False
            )
            .size()
            .rename(columns={"size": "crime_count"})
        )

        monthly_records.append(monthly_chunk)

    # ------------------------------------------------------------------
    # Combine monthly data
    # ------------------------------------------------------------------

    if monthly_records:
        monthly = pd.concat(monthly_records, ignore_index=True)
    else:
        monthly = pd.DataFrame(
            columns=["cell_id", "month", "hour", "dow", "primary_type", "crime_count"]
        )

    # ------------------------------------------------------------------
    # Save outputs
    # ------------------------------------------------------------------

    FEATURES_FILE.parent.mkdir(parents=True, exist_ok=True)
    grid.to_parquet(FEATURES_FILE)

    MONTHLY_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(MONTHLY_FILE)

    print("\n[AGGREGATE] Aggregation complete.")
    print(f"[AGGREGATE] Saved features to: {FEATURES_FILE}")
    print(f"[AGGREGATE] Saved monthly table to: {MONTHLY_FILE}")

    return grid, monthly, primary_types