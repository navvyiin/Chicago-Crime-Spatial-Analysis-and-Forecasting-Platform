from src.load_data import load_boundary
from src.build_grid import build_and_save_grid
from src.aggregate import aggregate_features
from src.model_poisson_nb import fit_poisson_nb
from src.model_rf_gwr import fit_rf, fit_gb, fit_gwr, fit_local_linear
from src.spatial_stats import (
    compute_moran,
    compute_getis_gi_star,
    compute_kde_intensity,
)
from src.reporting import generate_pdf_summary
from src.timeseries import forecast_monthly_crime
from src.config import MODEL_FILE, MONTHLY_FILE, MODEL_METRICS_FILE

import geopandas as gpd
import numpy as np
import pandas as pd


def _normalise_safe(values):
    arr = np.asarray(values, dtype="float64")
    if np.all(~np.isfinite(arr)):
        return np.zeros_like(arr)
    arr = np.where(np.isfinite(arr), arr, 0.0)
    max_val = np.max(arr)
    if max_val <= 0:
        return np.zeros_like(arr)
    return arr / max_val


def _attach_risk_and_uncertainty(features_gdf):
    """
    Add composite risk score, quantiles, ranks, and simple
    approximate prediction intervals based on the main count model.
    """
    df = features_gdf.copy()

    # Core intensity components
    c_obs = _normalise_safe(df.get("crime_count_total", 0.0))
    c_pred_nb = df.get("pred_nb")
    c_pred_pois = df.get("pred_poisson")

    # Prefer NB if available, else fall back to Poisson, else zeros
    if c_pred_nb is not None:
        c_pred = _normalise_safe(c_pred_nb)
        mu = np.asarray(c_pred_nb, dtype="float64")
    elif c_pred_pois is not None:
        c_pred = _normalise_safe(c_pred_pois)
        mu = np.asarray(c_pred_pois, dtype="float64")
    else:
        c_pred = np.zeros(len(df), dtype="float64")
        mu = np.zeros(len(df), dtype="float64")

    # Hotspot & KDE components (Gi* and KDE intensity, clipped at 0)
    gi = df.get("gi_z", df.get("gi_star", 0.0))
    gi_pos = np.clip(np.asarray(gi, dtype="float64"), a_min=0.0, a_max=None)
    c_gi = _normalise_safe(gi_pos)

    kde = df.get("kde_intensity", 0.0)
    c_kde = _normalise_safe(kde)

    # Composite risk score (simple average of components)
    components = np.vstack([c_obs, c_pred, c_gi, c_kde])
    risk_score = np.nanmean(components, axis=0)

    df["risk_score"] = risk_score

    # Quantile (0–1) and priority rank (1 = highest risk)
    order = np.argsort(risk_score)
    ranks = np.empty_like(order, dtype="int64")
    ranks[order] = np.arange(1, len(risk_score) + 1)
    df["priority_rank"] = ranks
    df["risk_quantile"] = (ranks - 1) / max(len(ranks) - 1, 1)

    # Simple Poisson-style prediction intervals for main mean mu
    mu = np.clip(mu, a_min=0.0, a_max=None)
    sigma = np.sqrt(np.clip(mu, a_min=1e-6, a_max=None))
    z = 1.96
    lower = np.clip(mu - z * sigma, a_min=0.0, a_max=None)
    upper = mu + z * sigma

    df["pred_lower"] = lower
    df["pred_upper"] = upper

    return df


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
    # STEP 6: Gradient Boosting
    # ------------------------------------------------------------------

    print("=== STEP 6: Fitting Gradient Boosting ===")
    gb, features_gdf = fit_gb(features_gdf)
    print()

    # ------------------------------------------------------------------
    # STEP 7: GWR or Local Linear fallback
    # ------------------------------------------------------------------

    print("=== STEP 7: Fitting GWR ===")
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
    # STEP 8: Spatial statistics
    # ------------------------------------------------------------------

    print("=== STEP 8: Spatial statistics (Moran, Gi*, KDE) ===")
    moran = compute_moran(features_gdf)
    print(f"Moran's I: {moran.I:.4f}, p = {moran.p_norm:.6f}")

    features_gdf = compute_getis_gi_star(features_gdf)
    features_gdf = compute_kde_intensity(
        features_gdf,
        bandwidth=750.0,   # aligned with 500 m grid
    )
    print()

    # ------------------------------------------------------------------
    # STEP 9: Composite risk & uncertainty fields
    # ------------------------------------------------------------------

    print("=== STEP 9: Computing composite risk score and intervals ===")
    features_gdf = _attach_risk_and_uncertainty(features_gdf)
    print("Added columns: risk_score, risk_quantile, priority_rank, pred_lower, pred_upper.\n")

    # ------------------------------------------------------------------
    # STEP 10: Save model outputs
    # ------------------------------------------------------------------

    print("=== STEP 10: Saving model outputs ===")
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    features_gdf.to_parquet(MODEL_FILE)
    print(f"Saved model results to: {MODEL_FILE}\n")

    # ------------------------------------------------------------------
    # STEP 11: Forecasting
    # ------------------------------------------------------------------

    print("=== STEP 11: Forecasting monthly crime ===")
    history, forecast, forecast_path, ts_metrics = forecast_monthly_crime(
        monthly,
        horizon=6,
    )
    print(f"Saved monthly forecast to: {forecast_path}")

    MONTHLY_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(MONTHLY_FILE)
    print(f"Saved monthly table to: {MONTHLY_FILE}\n")

    # ------------------------------------------------------------------
    # STEP 12: Model metrics
    # ------------------------------------------------------------------

    print("=== STEP 12: Computing and saving model diagnostics ===")
    metrics: list[dict] = []

    # Poisson / NB diagnostics
    metrics.append(
        {
            "model": "poisson",
            "target": "crime_count_total",
            "metric": "dispersion_ratio",
            "value": float(disp),
        }
    )

    try:
        metrics.append(
            {
                "model": "poisson",
                "target": "crime_count_total",
                "metric": "aic",
                "value": float(pois.aic),
            }
        )
        metrics.append(
            {
                "model": "poisson",
                "target": "crime_count_total",
                "metric": "bic",
                "value": float(pois.bic),
            }
        )
    except Exception:
        pass

    if nb is not None:
        try:
            metrics.append(
                {
                    "model": "neg_bin",
                    "target": "crime_count_total",
                    "metric": "aic",
                    "value": float(nb.aic),
                }
            )
            metrics.append(
                {
                    "model": "neg_bin",
                    "target": "crime_count_total",
                    "metric": "bic",
                    "value": float(nb.bic),
                }
            )
        except Exception:
            pass

    # Helper for regression metrics
    def _add_regression_metrics(name: str, y_true, y_pred, target: str = "crime_count_total"):
        y_true = np.asarray(y_true, dtype="float64")
        y_pred = np.asarray(y_pred, dtype="float64")
        mask = np.isfinite(y_true) & np.isfinite(y_pred)
        if not np.any(mask):
            return
        y_true = y_true[mask]
        y_pred = y_pred[mask]
        mse = float(np.mean((y_true - y_pred) ** 2))
        rmse = float(np.sqrt(mse))
        if np.var(y_true) > 0:
            r2 = float(
                1.0
                - np.sum((y_true - y_pred) ** 2)
                / np.sum((y_true - np.mean(y_true)) ** 2)
            )
        else:
            r2 = float("nan")
        metrics.extend(
            [
                {"model": name, "target": target, "metric": "rmse", "value": rmse},
                {"model": name, "target": target, "metric": "r2", "value": r2},
            ]
        )

    # Random Forest metrics + feature importances
    try:
        candidate_cols = [
            "streetlight_count",
            "bus_count",
            "crime_burglary",
            "crime_robbery",
            "crime_assault",
        ]
        X_cols = [c for c in candidate_cols if c in features_gdf.columns]
        mask = features_gdf["crime_count_total"].notna()
        X = features_gdf.loc[mask, X_cols].fillna(0.0).values
        y = features_gdf.loc[mask, "crime_count_total"].values
        if len(y) > 0:
            y_pred_rf = rf.predict(X)
            _add_regression_metrics("random_forest", y, y_pred_rf)

            importances = getattr(rf, "feature_importances_", None)
            if importances is not None:
                for col, imp in zip(X_cols, importances):
                    metrics.append(
                        {
                            "model": "random_forest",
                            "target": "crime_count_total",
                            "metric": f"feature_importance_{col}",
                            "value": float(imp),
                        }
                    )
    except Exception:
        pass

    # Gradient Boosting metrics
    try:
        candidate_cols = [
            "streetlight_count",
            "bus_count",
            "crime_burglary",
            "crime_robbery",
            "crime_assault",
        ]
        X_cols = [c for c in candidate_cols if c in features_gdf.columns]
        mask = features_gdf["crime_count_total"].notna()
        X = features_gdf.loc[mask, X_cols].fillna(0.0).values
        y = features_gdf.loc[mask, "crime_count_total"].values
        if len(y) > 0:
            y_pred_gb = gb.predict(X)
            _add_regression_metrics("gradient_boosting", y, y_pred_gb)
    except Exception:
        pass

    # GWR / local linear metrics (based on pred_gwr column)
    if "pred_gwr" in features_gdf.columns:
        try:
            mask = features_gdf["crime_count_total"].notna()
            y = features_gdf.loc[mask, "crime_count_total"].values
            y_pred = features_gdf.loc[mask, "pred_gwr"].values
            _add_regression_metrics("gwr_or_local_linear", y, y_pred)
        except Exception:
            pass

    # Time-series diagnostics
    metrics.append(
        {
            "model": "sarima_citywide",
            "target": "monthly_total",
            "metric": "aic",
            "value": ts_metrics.get("aic"),
        }
    )
    metrics.append(
        {
            "model": "sarima_citywide",
            "target": "monthly_total",
            "metric": "bic",
            "value": ts_metrics.get("bic"),
        }
    )
    metrics.append(
        {
            "model": "sarima_citywide",
            "target": "monthly_total",
            "metric": "rmse_in_sample",
            "value": ts_metrics.get("rmse_in_sample"),
        }
    )

    # Persist metrics
    metrics_df = pd.DataFrame(metrics)
    MODEL_METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_parquet(MODEL_METRICS_FILE)
    print(f"Saved model diagnostics to: {MODEL_METRICS_FILE}\n")

    # ------------------------------------------------------------------
    # STEP 13: PDF summary
    # ------------------------------------------------------------------

    print("=== STEP 13: Generating PDF summary report ===")
    pdf_path = generate_pdf_summary(features_gdf, moran)
    print(f"Saved PDF summary to: {pdf_path}\n")

    print("=== PIPELINE COMPLETE ===")
    return features_gdf, monthly, crime_types, moran


if __name__ == "__main__":
    run_pipeline(year=2025, hex_diameter=500.0)