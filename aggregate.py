import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.strtree import STRtree

from .load_data import (
    iter_crime_chunks,
    load_streetlights,
    load_bus_stops,
)
from .config import GRID_FILE, FEATURES_FILE, MONTHLY_FILE

DEFAULT_CRIME_TYPES = ["BURGLARY", "ROBBERY", "ASSAULT"]


# ---------------------------------------------------------------------
# Helper: build spatial index for grid
# ---------------------------------------------------------------------

def build_grid_index(grid):
    geoms = grid.geometry.values
    tree = STRtree(geoms)
    cell_ids = grid["cell_id"].values
    return tree, geoms, cell_ids


# ---------------------------------------------------------------------
# Helper: count point features per grid cell (small datasets only)
# ---------------------------------------------------------------------

def count_points(points_gdf, grid):
    tree, geoms, cell_ids = build_grid_index(grid)
    counts = pd.Series(0, index=grid["cell_id"], dtype=int)

    for geom in points_gdf.geometry:
        idxs = tree.query(geom)

        for idx in idxs:
            poly = geoms[idx]
            if poly.contains(geom):
                counts.loc[cell_ids[idx]] += 1
                break

    return counts


# ---------------------------------------------------------------------
# Main aggregation routine
# ---------------------------------------------------------------------

def aggregate_features(primary_types=None, chunksize: int = 500_000):

    if primary_types is None:
        primary_types = DEFAULT_CRIME_TYPES

    # ------------------------------------------------------------------
    # Load grid
    # ------------------------------------------------------------------

    grid = gpd.read_file(GRID_FILE)
    grid = gpd.GeoDataFrame(grid, geometry="geometry")
    grid.reset_index(drop=True, inplace=True)
    grid["cell_id"] = grid["cell_id"].astype(int)

    print("\n[AGGREGATE DEBUG] Loaded grid:")
    print("[AGGREGATE DEBUG] Rows:", len(grid))
    print("[AGGREGATE DEBUG] CRS:", grid.crs)

    # ------------------------------------------------------------------
    # Initialise counters
    # ------------------------------------------------------------------

    grid["crime_count_total"] = 0
    for ctype in primary_types:
        grid[f"crime_{ctype.lower()}"] = 0

    # ------------------------------------------------------------------
    # Environmental context (safe to sjoin — small)
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
    # Build spatial index ONCE
    # ------------------------------------------------------------------

    tree, geoms, cell_ids = build_grid_index(grid)

    # ------------------------------------------------------------------
    # Monthly aggregation accumulator
    # ------------------------------------------------------------------

    monthly_accumulator = {}

    print("\n[AGGREGATE] Processing crime data in chunks...")

    for i, crimes in enumerate(iter_crime_chunks(chunksize=chunksize), start=1):

        print(f"[AGGREGATE] Chunk {i} loaded ({len(crimes)} rows)")

        for row in crimes.itertuples(index=False):

            geom = row.geometry
            idxs = tree.query(geom)

            cell_id = None
            for idx in idxs:
                if geoms[idx].contains(geom):
                    cell_id = cell_ids[idx]
                    break


            if cell_id is None:
                continue

            # Total count
            grid.loc[grid["cell_id"] == cell_id, "crime_count_total"] += 1

            # Per-type count
            if row.primary_type in primary_types:
                col = f"crime_{row.primary_type.lower()}"
                grid.loc[grid["cell_id"] == cell_id, col] += 1

            # Monthly aggregation key
            key = (
                cell_id,
                row.month,
                row.hour,
                row.dow,
                row.primary_type,
            )

            monthly_accumulator[key] = monthly_accumulator.get(key, 0) + 1

    # ------------------------------------------------------------------
    # Finalise monthly table
    # ------------------------------------------------------------------

    if monthly_accumulator:
        monthly = (
            pd.Series(monthly_accumulator)
            .rename("crime_count")
            .reset_index()
            .rename(
                columns={
                    "level_0": "cell_id",
                    "level_1": "month",
                    "level_2": "hour",
                    "level_3": "dow",
                    "level_4": "primary_type",
                }
            )
        )
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