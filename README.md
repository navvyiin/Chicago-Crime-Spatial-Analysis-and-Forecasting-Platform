# Chicago Crime Spatial Analysis & Forecasting Platform

A geospatial machine learning pipeline for crime risk mapping, hotspot detection, and temporal forecasting across the City of Chicago. Built as a modular, end-to-end system covering spatial data engineering, statistical modelling, spatial statistics, time series forecasting, and an interactive dashboard.

---

## What It Does

- Builds a hexagonal spatial grid over Chicago and aggregates ~8 million crime incidents (2001-2025) with multi-source features: streetlight locations, CTA bus stops, and city boundaries
- Fits Poisson and Negative Binomial GLMs for baseline risk estimation, Random Forest for non-linear pattern capture, and Geographically Weighted Regression for spatially varying effects
- Computes global spatial autocorrelation (Moran's I), local hotspot detection (Getis-Ord Gi*), and KDE intensity surfaces
- Forecasts monthly crime activity using Exponential Smoothing (ETS)
- Delivers all outputs through an interactive Streamlit dashboard with choropleth risk maps, temporal filtering, animated crime maps, and PDF/CSV export

---

## Project Structure

```
env-crime-spatial-field/
├── app/
│   └── maps.py                   # Shared map rendering utilities
├── data/
│   ├── raw/                      # Input datasets
│   │   ├── Chicago_City_Limits.shp
│   │   ├── crimes.csv
│   │   ├── street_lights_all_out.csv
│   │   └── CTA_BusStops.*
│   └── processed/                # Pipeline outputs
│       ├── hex_grid.gpkg
│       ├── features.parquet
│       ├── model_results.parquet
│       ├── forecast_monthly.parquet
│       └── reports/
├── src/
│   ├── aggregate.py              # Spatial aggregation and feature engineering
│   ├── build_grid.py             # Hex grid generation
│   ├── config.py                 # Paths and global settings
│   ├── load_data.py              # Data ingestion
│   ├── model_poisson_nb.py       # Poisson and Negative Binomial GLMs
│   ├── model_rf_gwr.py           # Random Forest, GWR, and fallback methods
│   ├── spatial_stats.py          # Moran's I, Gi*, KDE
│   ├── timeseries.py             # ETS forecasting
│   └── reporting.py              # PDF report generation
├── run_pipeline.py               # Full pipeline execution
├── streamlit_app.py              # Dashboard entry point
└── requirements.txt
```

---

## Getting Started

**Requirements:** Python 3.8 or above

```bash
python -m venv crime_env
source crime_env/bin/activate     # Linux / Mac
crime_env\Scripts\activate        # Windows
pip install -r requirements.txt
```

---

## Data Requirements

Place the following files in `data/raw/`:

| File | Description |
|------|-------------|
| `Chicago_City_Limits.shp` | City boundary polygon |
| `crimes.csv` | Crime incidents with geocoordinates |
| `street_lights_all_out.csv` | Streetlight point dataset |
| `CTA_BusStops.*` | CTA bus stop shapefile |

All inputs must be in WGS84 (EPSG:4326) or will be reprojected automatically during ingestion.

---

## Running the Pipeline

```bash
python run_pipeline.py
```

This runs the full workflow: grid construction, feature engineering, statistical modelling, spatial autocorrelation analysis, hotspot detection, forecasting, and PDF report generation.

To adjust the hexagon resolution (default 100 metres):

```bash
python run_pipeline.py --hex 100
```

Or edit directly in `src/config.py`:

```python
HEX_DIAMETER = 100.0
```

---

## Launching the Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard includes choropleth maps for observed and predicted crime risk, Gi* hotspot layers, KDE intensity surfaces, hour-of-day and day-of-week filters, animated temporal maps, forecast charts, and scenario-based interventions on high-risk cells.

---

## Outputs

| File | Contents |
|------|----------|
| `model_results.parquet` | Features, crime counts, model predictions, Gi* scores, KDE values |
| `forecast_monthly.parquet` | Monthly crime forecasts |
| `hex_grid.gpkg` | Spatial grid geometry |
| `reports/crime_summary_*.pdf` | Automated PDF summaries |

---

## Technical Notes

- A KNN spatial weights matrix is used to avoid island effects and improve numerical stability
- GWR is automatically replaced by a Local Linear regression kernel for grids above approximately 6,000 cells
- KDE is computed on hex centroids rather than raw incidents for efficiency
- The forecasting module skips gracefully when historical depth is insufficient

---

## Extensibility

The modular architecture supports replacing ML models, adding environmental predictors, migrating data to PostGIS or cloud storage, extending the pipeline to other cities, and deploying as a production web service.

---

## Contributing

Contributions, issue reports, and feature suggestions are welcome.
