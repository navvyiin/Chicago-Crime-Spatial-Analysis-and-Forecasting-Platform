import numpy as np
import geopandas as gpd
from sklearn.neighbors import KernelDensity

import libpysal
import esda


def _make_knn_weights(gdf: gpd.GeoDataFrame, k: int = 8):
    """
    Build a KNN weights matrix. This avoids islands and scales better
    for large hex grids than Queen contiguity.
    """
    k = min(k, max(1, len(gdf) - 1))
    w = libpysal.weights.KNN.from_dataframe(gdf, k=k, silence_warnings=True)
    w.transform = "r"
    return w


def compute_moran(gdf: gpd.GeoDataFrame):
    """
    Compute global Moran's I on crime_count_total using KNN weights.
    """
    y = gdf["crime_count_total"].values.astype(float)
    w = _make_knn_weights(gdf, k=8)
    mi = esda.Moran(y, w)
    return mi


def compute_getis_gi_star(gdf: gpd.GeoDataFrame):
    """
    Compute local Getis-Ord Gi* using KNN weights and no permutations
    (fast, deterministic, suitable for large grids).

    Result is stored in column 'gi_star' (z-scores).
    """
    if "crime_count_total" not in gdf.columns:
        raise ValueError("crime_count_total not found in GeoDataFrame.")

    y = gdf["crime_count_total"].values.astype(float)
    w = _make_knn_weights(gdf, k=8)

    # permutations=0 → analytical, no Monte Carlo (fast)
    gi = esda.getisord.G_Local(y, w, transform="r", star=True, permutations=0)
    gdf["gi_star"] = gi.Zs
    return gdf


def compute_kde_intensity(gdf: gpd.GeoDataFrame, bandwidth: float = 200.0):
    """
    Compute KDE intensity at cell centroids using Gaussian kernel.

    Parameters
    ----------
    bandwidth : float
        Kernel bandwidth in CRS units (metres if CRS is projected).
    """
    centroids = gdf.geometry.centroid
    coords = np.column_stack([centroids.x.values, centroids.y.values])

    kde = KernelDensity(bandwidth=bandwidth, kernel="gaussian")
    kde.fit(coords)
    gdf["kde_intensity"] = np.exp(kde.score_samples(coords))
    return gdf