import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
import geopandas as gpd
import numpy as np

from .config import GRID_FILE


def _hexagon(cx: float, cy: float, radius: float) -> Polygon:
    """
    Build a regular hexagon centred at (cx, cy).

    Parameters
    ----------
    cx, cy : float
        Centre coordinates (in metres).
    radius : float
        Distance from centre to vertex (metres).
        Vertex-to-vertex width = 2 * radius.
    """
    angles = np.linspace(0, 2 * math.pi, 7)
    points = [
        (cx + radius * math.cos(a), cy + radius * math.sin(a))
        for a in angles
    ]
    return Polygon(points)


def build_hex_grid(
    boundary: gpd.GeoDataFrame,
    hex_diameter: float = 500.0
) -> gpd.GeoDataFrame:
    """
    Build a hexagonal grid covering the city boundary, then clip to boundary.

    Parameters
    ----------
    boundary : GeoDataFrame
        City polygon(s) in a projected CRS (metres).
    hex_diameter : float
        Vertex-to-vertex diameter of hexagon in metres.
        Default = 500 m.

    Returns
    -------
    GeoDataFrame with columns: geometry, cell_id
    """
    if boundary.crs is None:
        raise ValueError("Boundary GeoDataFrame must have a projected CRS (metres).")

    radius = hex_diameter / 2.0

    # Horizontal spacing between centres (pointy-top hexes)
    w = 3 * radius

    # Vertical spacing between rows
    h = math.sqrt(3) * radius

    minx, miny, maxx, maxy = boundary.total_bounds

    hexes = []
    y = miny
    row = 0

    while y <= maxy + h:
        x = minx + (0 if row % 2 == 0 else 1.5 * radius)
        while x <= maxx + w:
            hexes.append(_hexagon(x, y, radius))
            x += w
        y += h
        row += 1

    grid = gpd.GeoDataFrame({"geometry": hexes}, crs=boundary.crs)

    # Clip to city boundary
    boundary_union = unary_union(boundary.geometry)
    clip_gdf = gpd.GeoDataFrame(geometry=[boundary_union], crs=boundary.crs)
    grid = gpd.overlay(grid, clip_gdf, how="intersection")

    # Remove degenerate cells
    grid = grid[grid.geometry.is_valid & (grid.geometry.area > 0)].copy()

    grid.reset_index(drop=True, inplace=True)
    grid["cell_id"] = grid.index.astype(int)

    return grid


def build_and_save_grid(
    boundary: gpd.GeoDataFrame,
    hex_diameter: float = 500.0
) -> gpd.GeoDataFrame:
    """
    Build the hex grid and save it to disk.

    Returns
    -------
    GeoDataFrame
        Hex grid with cell_id.
    """
    grid = build_hex_grid(boundary, hex_diameter=hex_diameter)

    GRID_FILE.parent.mkdir(parents=True, exist_ok=True)
    grid.to_file(GRID_FILE, driver="GPKG")

    print(f"[GRID] Hex diameter (vertex-to-vertex): {hex_diameter:.1f} m")
    print(f"[GRID] Total cells: {len(grid)}")
    print(f"[GRID] CRS: {grid.crs}")
    print(f"[GRID] Saved to: {GRID_FILE}")

    return grid