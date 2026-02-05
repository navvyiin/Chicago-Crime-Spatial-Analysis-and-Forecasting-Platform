from pathlib import Path
import argparse

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


# ---------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------

def run_pipeline(year: int = 2025, hex_diameter: float = 500.0):
    """
    End-to-end spatial analytics pipeline.

    This function is intentionally side-effectful:
    - builds spatial grid
    - aggregates multi-year crime data
    - fits statistical and ML models
    - computes spatial diagnostics
    - persists all outputs to disk

    Designed for:
    - local research execution
    - containerised batch execution
    """

    # ------------------------------------------------------------------
    # STEP 1: Load city boundary
    # ------------------------------------------------------------------

    print("=== STEP 1: Loading city boundary ===")
    boundary = load_boundary()

    # ------------------------------------------------------------------
    # STEP 2: Build hex grid
    # ------------------------------------------------------------------

    print("\n=== STEP 2: Building hex grid ===")
    grid = build_and_save_grid(boundary, hex_diameter=hex_diameter)
    print(f"Grid built with {len(grid)} cells.")

    # ------------------------------------------------------------------
    # STEP 3: Aggregate features
    # ------------------------------------------------------------------

    print("\n=== STEP 3: Aggregating crime + environmental features ===")
    features_gdf, monthly, crime_types = aggregate_features()

    # ------------------------------------------------------------------
    # STEP 4: Poisson & Negative Binomial regression
    # ------------------------------------------------------------------

    print("\n=== STEP 4: Fitting Poisson + Negative Binomial models ===")
    pois, nb, features_gdf, dispersion = fit_poisson_nb(features_gdf)
    print(f"Poisson dispersion ratio: {dispersion:.4f}")

    # ------------------------------------------------------------------
    # STEP 5: Random Forest
    # ------------------------------------------------------------------

    print("\n=== STEP 5: Fitting Random Forest model ===")
    rf, features_gdf = fit_rf(features_gdf)

    # ------------------------------------------------------------------
    # STEP 6: GWR or Local Linear fallback
    # ------------------------------------------------------------------

    print("\n=== STEP 6: Fitting GWR / Local Linear model ===")
    try:
        if len(features_gdf) > 6000:
            print("Grid too large for MGWR. Using local linear fallback.")
            features_gdf = fit_local_linear(features_gdf)
        else:
            gwr, features_gdf = fit_gwr(features_gdf)
    except Exception as exc:
        print("GWR failed; using local linear fallback.")
        print(f"Reason: {exc}")
        features_gdf = fit_local_linear(features_gdf)

    # ------------------------------------------------------------------
    # STEP 7: Spatial statistics
    # ------------------------------------------------------------------

    print("\n=== STEP 7: Spatial statistics ===")
    moran = compute_moran(features_gdf)
    print(f"Moran's I: {moran.I:.4f}, p-value: {moran.p_norm:.6f}")

    features_gdf = compute_getis_gi_star(features_gdf)
    features_gdf = compute_kde_intensity(
        features_gdf,
        bandwidth=750.0,  # aligned with 500 m grid resolution
    )

    # ------------------------------------------------------------------
    # STEP 8: Persist model outputs
    # ------------------------------------------------------------------

    print("\n=== STEP 8: Saving model outputs ===")
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    features_gdf.to_parquet(MODEL_FILE)
    print(f"Saved model results to: {MODEL_FILE}")

    # ------------------------------------------------------------------
    # STEP 9: Temporal forecasting
    # ------------------------------------------------------------------

    print("\n=== STEP 9: Forecasting monthly crime ===")
    history, forecast, forecast_path = forecast_monthly_crime(
        monthly,
        horizon=6,
    )
    print(f"Saved forecast to: {forecast_path}")

    MONTHLY_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(MONTHLY_FILE)
    print(f"Saved monthly table to: {MONTHLY_FILE}")

    # ------------------------------------------------------------------
    # STEP 10: PDF summary report
    # ------------------------------------------------------------------

    print("\n=== STEP 10: Generating PDF summary report ===")
    pdf_path = generate_pdf_summary(features_gdf, moran)
    print(f"Saved PDF summary to: {pdf_path}")

    print("\n=== PIPELINE COMPLETE ===")

    return {
        "features": features_gdf,
        "monthly": monthly,
        "crime_types": crime_types,
        "moran": moran,
        "forecast_path": forecast_path,
        "pdf_path": pdf_path,
    }


# ---------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Chicago Crime Spatial Analysis pipeline."
    )
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--hex-diameter", type=float, default=500.0)

    args = parser.parse_args()

    run_pipeline(
        year=args.year,
        hex_diameter=args.hex_diameter,
    )
