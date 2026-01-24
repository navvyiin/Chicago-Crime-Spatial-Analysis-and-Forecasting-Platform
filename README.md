# Chicago Crime Spatial Analysis & Forecasting Platform

A **research-grade, production-oriented spatial analytics system** for analysing, modelling, and forecasting urban crime patterns in Chicago across **multiple years of city-scale data**.

This project integrates **geospatial statistics, spatial econometrics, machine learning, and time-series forecasting** into a robust end-to-end pipeline that transforms raw crime events into **interpretable spatial risk surfaces, hotspot diagnostics, and forward-looking forecasts**, delivered through an interactive analytical dashboard.

---

## Project Motivation

Urban crime exhibits **strong spatial dependence, non-linear structure, and long-term temporal dynamics**.
Conventional descriptive analysis and naïve aggregation often fail to capture:

* global and local spatial autocorrelation
* non-linear environmental interactions
* temporal persistence and seasonal effects
* scale sensitivity introduced by arbitrary spatial units

This platform was designed to address these limitations by combining:

* spatial statistics (Moran’s I, Getis–Ord Gi*)
* count-based regression for over-dispersed events
* non-linear machine learning models
* scalable, multi-year temporal aggregation
* interactive spatial visualisation

The result is a **reproducible, extensible spatial intelligence framework** suitable for research, applied analytics, and technical evaluation.

---

## Core Capabilities

### Spatial Data Engineering

* Hexagonal grid aggregation (500 m resolution) to reduce edge effects
* CRS-safe spatial joins and projections
* Chunked processing of multi-million-row datasets
* Feature engineering across spatial, temporal, and contextual dimensions

### Spatial Statistics

* Global spatial autocorrelation (Moran’s I)
* Local hotspot detection (Getis–Ord Gi*)
* Kernel density–based intensity surfaces
* Diagnostic outputs for spatial dependence

### Modelling & Forecasting

* Poisson and Negative Binomial regression for count data
* Random Forest models for non-linear spatial effects
* Geographically Weighted Regression (with robust fallback for large grids)
* Monthly crime forecasting using historical spatial aggregates

### Interactive Analytics

* Interactive Dash-based spatial dashboard
* Layered risk maps and hotspot visualisation
* Model outputs rendered for exploratory analysis
* Exportable CSV summaries and PDF reports

---

## System Architecture

```
Chicago-Crime-Spatial-Analysis-Forecasting-Platform/
│
├── src/
│   ├── load_data.py           # Chunk-safe data ingestion
│   ├── build_grid.py          # Hex grid construction
│   ├── aggregate.py           # Scalable spatial aggregation
│   ├── spatial_stats.py       # Moran’s I, Gi*, KDE
│   ├── model_poisson_nb.py    # Count regression models
│   ├── model_rf_gwr.py        # RF, GWR, local-linear fallback
│   ├── timeseries.py          # Temporal forecasting
│   └── reporting.py           # PDF reporting
│
├── app/
│   ├── layout.py              # Dashboard layout
│   ├── callbacks.py           # Interactive logic
│   └── maps.py                # Spatial visualisation
│
├── run_pipeline.py            # End-to-end analytics pipeline
├── run_app.py                 # Interactive dashboard launcher
├── requirements.txt
└── README.md
```

*Raw and processed data are intentionally excluded from version control.*

---

## Methodological Overview

### Spatial Framework

Crime events are aggregated into a **hexagonal grid** to ensure uniform neighbourhood structure and minimise artefacts introduced by administrative boundaries.
Spatial weights are constructed using **K-nearest neighbours**, ensuring robustness for large grids.

### Statistical Analysis

* Moran’s I quantifies global spatial dependence
* Getis–Ord Gi* identifies statistically significant local hotspots
* KDE provides smooth intensity estimates at cell centroids

### Modelling Strategy

* Poisson and Negative Binomial models handle over-dispersed crime counts
* Random Forest captures non-linear spatial interactions
* GWR allows spatially varying relationships, with a local linear fallback for numerical stability

### Temporal Modelling

* Crimes are aggregated monthly at the grid-cell level
* Forecasting models estimate future crime intensity under historical dynamics

---

## Running the Platform

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

⚠️ Some spatial libraries may require system-level dependencies (e.g. GEOS, GDAL).

---

### 2. Run the Full Pipeline

```bash
python run_pipeline.py
```

This performs:

* grid construction
* chunked crime aggregation (multi-year)
* spatial statistics
* model training
* forecast generation
* output persistence

---

### 3. Launch the Interactive Dashboard

```bash
python run_app.py
```

Explore:

* crime density maps
* spatial hotspots
* model predictions
* forecasted risk surfaces

---

## Outputs

The pipeline generates:

* spatial risk maps
* hotspot layers
* model diagnostics
* monthly crime forecasts
* tabular summaries by spatial unit

All outputs are saved for **reproducibility and inspection**, but excluded from version control.

---

## Ethical & Responsible Use

Crime analytics is a high-impact and sensitive domain.

This project:

* operates exclusively on **aggregated spatial data**
* avoids individual-level prediction or profiling
* is intended for **research, planning, and exploratory analysis**
* is **not** designed for real-time policing or enforcement

Users are encouraged to:

* consider reporting bias and data limitations
* avoid stigmatization of communities
* treat outputs as decision support, not deterministic truth

---

## Limitations

* Forecast accuracy depends on historical stability and data quality
* Results are sensitive to spatial resolution and aggregation choices
* Spatial association should not be interpreted as causal

---

## Intended Audience

* Researchers in spatial statistics and urban analytics
* Data scientists working with geospatial or event data
* Policy analysts and urban planners
* Recruiters evaluating applied ML + GIS capability

---

## Future Work

* Spatial cross-validation and benchmarking
* Fairness and bias diagnostics
* Model comparison across spatial resolutions
* Pipeline orchestration and containerised deployment

---

## License

MIT License © 2026 navvyiin

---

## Final Note

This project is intentionally designed to demonstrate **how spatial intelligence systems are built in practice** — not just which models are used, but how large, sensitive, real-world spatial data are engineered, analysed, and communicated end-to-end.
