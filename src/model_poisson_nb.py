import statsmodels.api as sm
import numpy as np

def fit_poisson_nb(features_gdf, response_col="crime_count_total"):
    df = features_gdf.copy()

    # Defensive filtering
    df = df[df[response_col].notna()].copy()

    # Log-transform predictors to stabilise scale
    X = df[["streetlight_count", "bus_count"]].copy()
    X = X.apply(lambda s: np.log1p(s))

    X = sm.add_constant(X)
    y = df[response_col]

    # Poisson model
    pois = sm.GLM(
        y,
        X,
        family=sm.families.Poisson()
    ).fit()

    df["pred_poisson"] = pois.predict(X)

    # Overdispersion check
    ratio = pois.deviance / pois.df_resid if pois.df_resid > 0 else 1.0

    # Negative Binomial if needed
    if ratio > 1.5:
        nb = sm.GLM(
            y,
            X,
            family=sm.families.NegativeBinomial()
        ).fit()
        df["pred_nb"] = nb.predict(X)
    else:
        nb = None
        df["pred_nb"] = df["pred_poisson"]

    return pois, nb, df, ratio