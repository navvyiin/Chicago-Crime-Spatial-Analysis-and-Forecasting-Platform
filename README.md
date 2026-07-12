# Chicago Crime Spatial Analysis & Forecasting Platform

A geospatial machine learning pipeline for crime risk mapping, hotspot detection, and short-term forecasting in Chicago, built as an independent project.

**Live app:** https://chicago-crime-spatial-analysis-and-forecasting-platform-usng.streamlit.app/

## What it does

Chicago's public crime dataset contains 8M+ recorded incidents (2001–2025). I filtered and spatially joined this down to 46,957 incidents relevant to the study period and aggregated them onto a 500-metre hexagonal grid, combining them with streetlight locations, CTA bus stops, and administrative boundary data.

From there, the pipeline:
- Tests spatial dependence with **Moran's I** (I = 0.5063, p < 0.0001 — moderate positive autocorrelation) and identifies local clusters with **Getis-Ord Gi\***
- Generates smoothed crime intensity surfaces via **kernel density estimation**
- Models baseline risk with **Poisson and Negative Binomial GLMs**, checking for overdispersion
- Captures non-linear spatial interactions with a **200+ tree Random Forest** regressor
- Fits a **Geographically Weighted Regression (GWR)** model, falling back to local linear modeling automatically on grids above 6,000 cells, where GWR becomes computationally impractical
- Forecasts monthly crime counts with **Exponential Smoothing (ETS)**, degrading gracefully when a given hex cell has too little history to forecast reliably

Results are served through an interactive Streamlit dashboard: observed vs. predicted choropleths, hour-of-day and day-of-week filtering, animated crime maps, and PDF/CSV export.

## Why hex grids, and why GWR at all

Point-level crime data is noisy and doesn't aggregate well for regression. A hexagonal grid gives uniform neighbor adjacency (unlike squares, which have ambiguous diagonal neighbors) and keeps spatial units at a consistent, interpretable scale. GWR was included specifically because global regression assumes the relationship between predictors and crime risk is constant across the city — it isn't; the drivers of risk in a dense downtown grid cell are not the same as in a low-density residential one. The automatic fallback to local linear modeling exists because GWR's computational cost scales roughly with the square of the number of spatial units, which becomes prohibitive above a few thousand cells on a single machine.

## Tech stack

Python, GeoPandas, Shapely, Scikit-learn, Statsmodels, Random Forest, Poisson/NB GLM, GWR, Streamlit, Plotly, ReportLab (PDF export).

## Known limitations

- Runs on a single machine — no distributed processing, so the grid resolution is capped by available memory.
- Crime data reflects reported incidents only, which is a known source of bias in any crime-risk model and isn't corrected for here.
- ETS forecasting is intentionally simple; it wasn't the focus of the project and a more capable time-series model (e.g., incorporating exogenous covariates) would likely outperform it.

## Setup

```bash
git clone https://github.com/navvyiin/chicago-crime-spatial-analysis-forecasting-platform.git
cd chicago-crime-spatial-analysis-forecasting-platform
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```
