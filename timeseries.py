import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .config import FORECAST_FILE


def forecast_monthly_crime(
    monthly_df: pd.DataFrame,
    horizon: int = 6,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12),
):
    """
    Forecast citywide monthly crime totals using SARIMA.

    Parameters
    ----------
    monthly_df : DataFrame
        Output from aggregate_features(), containing cell-level monthly counts.
    horizon : int
        Number of months to forecast ahead.
    order, seasonal_order : tuple
        SARIMA model parameters.

    Returns
    -------
    history_df : DataFrame
        Historical monthly totals.
    forecast_df : DataFrame
        Forecasted monthly totals.
    forecast_path : Path
        Path where forecast parquet was saved.
    """

    # ------------------------------------------------------------------
    # Aggregate to citywide monthly totals
    # ------------------------------------------------------------------

    history_df = (
        monthly_df
        .groupby("month", as_index=False)["crime_count"]
        .sum()
        .sort_values("month")
    )

    history_df["month"] = pd.to_datetime(history_df["month"])

    ts = history_df.set_index("month")["crime_count"]

    # ------------------------------------------------------------------
    # Fit SARIMA
    # ------------------------------------------------------------------

    model = SARIMAX(
        ts,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    res = model.fit(disp=False)

    # ------------------------------------------------------------------
    # Forecast
    # ------------------------------------------------------------------

    forecast_res = res.get_forecast(steps=horizon)
    forecast_df = forecast_res.summary_frame()

    forecast_df = (
        forecast_df
        .reset_index()
        .rename(columns={"index": "month", "mean": "forecast"})
        [["month", "forecast"]]
    )

    # ------------------------------------------------------------------
    # Save forecast
    # ------------------------------------------------------------------

    FORECAST_FILE.parent.mkdir(parents=True, exist_ok=True)
    forecast_df.to_parquet(FORECAST_FILE)

    return history_df, forecast_df, FORECAST_FILE