from src.load_data import load_boundary
from src.build_grid import build_and_save_grid
from src.aggregate import aggregate_features
from src.model_poisson_nb import fit_poisson_nb
from src.model_rf_gwr import fit_rf, fit_gwr, fit_local_linear
from src.spatial_stats import (
    compute_moran,
    compute_getis_gi_star,
    compute_kde_intensity,
)
from src.reporting import generate_pdf_summary
from src.timeseries import forecast_monthly_crime
from src.config import MODEL_FILE, MONTHLY_FILE

import geopandas as gpd


def run_pipeline(year: int = 2025, hex_diameter: float = 500.0):
    # ------------------------------------------------------------------
    # STEP 1: Load city boundary
    # ------------------------------------------------------------------

    print("=== STEP 1: Loading city boundary ===\n")
    boundary = load_boundary()

    # ------------------------------------------------------------------
    # STEP 2: Build hex grid (500 m)
    # ------------------------------------------------------------------

    print("=== STEP 2: Building hex grid ===\n")
    grid = build_and_save_grid(boundary, hex_diameter=hex_diameter)
    print(f"Grid built with {len(grid)} cells.\n")

    # ------------------------------------------------------------------
    # STEP 3: Aggregate features
    # ------------------------------------------------------------------

    print(f"=== STEP 3: Aggregating crime + environmental features ===\n")
    features_gdf, monthly, crime_types = aggregate_features()

    # ------------------------------------------------------------------
    # STEP 4: Poisson & Negative Binomial
    # ------------------------------------------------------------------

    print("=== STEP 4: Fitting Poisson + Negative Binomial ===")
    pois, nb, features_gdf, disp = fit_poisson_nb(features_gdf)
    print(f"Poisson dispersion ratio: {disp:.4f}\n")

    # ------------------------------------------------------------------
    # STEP 5: Random Forest
    # ------------------------------------------------------------------

    print("=== STEP 5: Fitting Random Forest ===")
    rf, features_gdf = fit_rf(features_gdf)
    print()

    # ------------------------------------------------------------------
    # STEP 6: GWR or Local Linear fallback
    # ------------------------------------------------------------------

    print("=== STEP 6: Fitting GWR ===")
    try:
        if len(features_gdf) > 6000:
            print("Grid too large for MGWR. Using Local Linear fallback.")
            features_gdf = fit_local_linear(features_gdf)
        else:
            gwr, features_gdf = fit_gwr(features_gdf)
    except Exception as e:
        print("GWR failed, using Local Linear fallback:", e)
        features_gdf = fit_local_linear(features_gdf)
    print()

    # ------------------------------------------------------------------
    # STEP 7: Spatial statistics
    # ------------------------------------------------------------------

    print("=== STEP 7: Spatial statistics (Moran, Gi*, KDE) ===")
    moran = compute_moran(features_gdf)
    print(f"Moran's I: {moran.I:.4f}, p = {moran.p_norm:.6f}")

    features_gdf = compute_getis_gi_star(features_gdf)
    features_gdf = compute_kde_intensity(
        features_gdf,
        bandwidth=750.0,   # aligned with 500 m grid
    )
    print()

    # ------------------------------------------------------------------
    # STEP 8: Save model outputs
    # ------------------------------------------------------------------

    print("=== STEP 8: Saving model outputs ===")
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    features_gdf.to_parquet(MODEL_FILE)
    print(f"Saved model results to: {MODEL_FILE}\n")

    # ------------------------------------------------------------------
    # STEP 9: Forecasting
    # ------------------------------------------------------------------

    print("=== STEP 9: Forecasting monthly crime ===")
    history, forecast, forecast_path = forecast_monthly_crime(
        monthly,
        horizon=6,
    )
    print(f"Saved monthly forecast to: {forecast_path}")

    MONTHLY_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(MONTHLY_FILE)
    print(f"Saved monthly table to: {MONTHLY_FILE}\n")

    # ------------------------------------------------------------------
    # STEP 10: PDF summary
    # ------------------------------------------------------------------

    print("=== STEP 10: Generating PDF summary report ===")
    pdf_path = generate_pdf_summary(features_gdf, moran)
    print(f"Saved PDF summary to: {pdf_path}\n")

    print("=== PIPELINE COMPLETE ===")
    return features_gdf, monthly, crime_types, moran


if __name__ == "__main__":
    run_pipeline(year=2025, hex_diameter=500.0)