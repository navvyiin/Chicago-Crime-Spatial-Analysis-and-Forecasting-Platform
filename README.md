# CrimeScope
### A Scalable Geospatial Machine Learning Platform for Urban Crime Intelligence, Spatial Risk Mapping, and Temporal Forecasting

> An end-to-end geospatial analytics framework that transforms more than two decades of urban crime records into interpretable spatial intelligence through statistical modelling, spatial statistics, machine learning, and interactive decision-support tools.

CrimeScope is an open-source spatial analytics platform designed for large-scale urban crime analysis. The system integrates geospatial data engineering, statistical modelling, spatial autocorrelation analysis, hotspot detection, temporal forecasting, and interactive visualisation into a reproducible computational workflow.

Unlike conventional crime prediction projects that focus on a single machine learning model, CrimeScope treats urban crime as a spatial process. The platform combines classical statistical inference with spatial statistical methods and modern machine learning to produce interpretable crime intelligence suitable for urban planning, public policy, and smart-city applications.

---

# Motivation

Urban crime exhibits strong spatial and temporal dependence.

Traditional predictive models often ignore these relationships by treating crime observations as independent events, leading to biased estimates and misleading predictions.

CrimeScope was developed to investigate crime through a spatial perspective by integrating

- Geospatial data engineering
- Spatial statistics
- Statistical modelling
- Machine learning
- Time-series forecasting
- Interactive geovisualisation

within a single modular architecture.

The project demonstrates how spatial intelligence can support evidence-based decision making in urban environments while remaining reproducible, extensible, and deployable.

---

# Key Features

## Geospatial Data Engineering

- Processes more than **8 million crime incidents (2001–2025)**
- Generates scalable hexagonal spatial grids
- Integrates multiple environmental datasets including

  - Streetlight locations
  - CTA Bus Stops
  - Administrative boundaries

- Automated CRS handling and spatial preprocessing

---

## Spatial Feature Engineering

- Hexagonal spatial aggregation
- Density estimation
- Environmental feature extraction
- Spatial neighbourhood construction
- Distance-based feature generation

---

## Statistical Modelling

Implements multiple complementary modelling approaches.

### Generalised Linear Models

- Poisson Regression
- Negative Binomial Regression

for interpretable baseline crime estimation.

### Machine Learning

- Random Forest Regression

captures nonlinear interactions between spatial variables.

### Spatial Regression

- Geographically Weighted Regression (GWR)

models spatially varying relationships across the city.

Automatic fallback methods ensure computational stability for large spatial grids.

---

## Spatial Statistics

The platform incorporates established spatial analytical methods including

- Moran's I
- Local Moran's I
- Getis–Ord Gi*
- Kernel Density Estimation (KDE)

to identify clustering, hotspots, and spatial dependence.

---

## Temporal Forecasting

Monthly crime trends are forecast using

- Exponential Smoothing (ETS)

allowing temporal analysis alongside spatial prediction.

---

## Interactive Decision Support

An interactive Streamlit dashboard provides

- Choropleth crime risk maps
- Hotspot visualisation
- KDE intensity surfaces
- Time filters
- Animated crime evolution
- Forecast dashboards
- PDF reporting
- CSV export

---

# System Architecture

```text
                Raw Spatial Data
                       │
                       ▼
               Data Validation
                       │
                       ▼
            Spatial Data Engineering
                       │
                       ▼
          Hexagonal Grid Construction
                       │
                       ▼
         Spatial Feature Engineering
                       │
      ┌───────────────────────────────────┐
      │                                   │
      ▼                                   ▼
Statistical Models                Spatial Statistics
(Poisson / NB / RF / GWR)    (Moran's I / Gi* / KDE)
      │                                   │
      └──────────────┬────────────────────┘
                     ▼
           Time-Series Forecasting
                     │
                     ▼
          Interactive Dashboard
                     │
                     ▼
          Reports & Spatial Outputs
```

---

# Repository Structure

```text
CrimeScope/

├── app/
│   └── maps.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── methodology.md
│   ├── architecture.md
│   ├── benchmark.md
│   ├── limitations.md
│   └── references.md
│
├── src/
│   ├── aggregate.py
│   ├── build_grid.py
│   ├── config.py
│   ├── load_data.py
│   ├── model_poisson_nb.py
│   ├── model_rf_gwr.py
│   ├── spatial_stats.py
│   ├── timeseries.py
│   └── reporting.py
│
├── assets/
│   ├── architecture.png
│   ├── workflow.gif
│   └── screenshots/
│
├── run_pipeline.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

---

# Methodology

CrimeScope follows a fully reproducible spatial analytics workflow.

1. Import raw spatial datasets.
2. Validate geometries and coordinate reference systems.
3. Construct a hexagonal spatial grid covering the study region.
4. Aggregate crime incidents into spatial units.
5. Engineer environmental and spatial features.
6. Fit statistical and machine learning models.
7. Quantify spatial dependence and hotspot intensity.
8. Forecast future crime trends.
9. Generate interactive visualisations and automated reports.

---

# Installation

## Requirements

- Python 3.10+
- GDAL-compatible environment
- Recommended: Conda or virtual environment

```bash
git clone https://github.com/navvyiin/CrimeScope.git

cd CrimeScope

python -m venv crime_env

source crime_env/bin/activate

pip install -r requirements.txt
```

---

# Running the Pipeline

Execute the complete analytical workflow.

```bash
python run_pipeline.py
```

Specify custom spatial resolutions.

```bash
python run_pipeline.py --hex 100
```

The pipeline performs

- spatial preprocessing
- feature engineering
- statistical modelling
- hotspot analysis
- temporal forecasting
- report generation

without additional user intervention.

---

# Launching the Dashboard

```bash
streamlit run streamlit_app.py
```

The dashboard supports interactive exploration of

- observed crime density
- predicted spatial risk
- hotspot significance
- KDE intensity
- temporal evolution
- monthly forecasts
- intervention scenarios

---

# Outputs

| Output | Description |
|----------|-------------|
| Hexagonal Grid | Spatial analysis units |
| Feature Matrix | Engineered spatial predictors |
| Model Predictions | Crime risk estimates |
| Moran's I | Global spatial autocorrelation |
| Getis–Ord Gi* | Local hotspot significance |
| KDE Surfaces | Spatial intensity estimation |
| Forecasts | Monthly crime projections |
| PDF Reports | Automated analytical summaries |

---

# Engineering Challenges

The primary challenge was not model development but computational scalability.

Spatial statistical techniques such as Geographically Weighted Regression become computationally expensive as the number of spatial units increases. CrimeScope therefore incorporates adaptive modelling strategies that automatically replace computationally intensive algorithms with efficient alternatives while preserving analytical consistency.

Another major challenge involved constructing a reproducible geospatial data engineering pipeline capable of integrating heterogeneous datasets with different coordinate systems, spatial resolutions, and attribute schemas into a unified analytical framework.

---

# Design Principles

CrimeScope was developed around several guiding principles.

- Modular software architecture
- Reproducible spatial workflows
- Statistical interpretability
- Computational scalability
- Interactive visual analytics
- Extensibility
- Research transparency

---

# Current Limitations

Current limitations include

- Single-machine execution
- Batch processing only
- No distributed spatial computation
- No streaming crime ingestion
- Limited forecasting models
- No deep learning spatial architectures

These limitations are intentional design trade-offs prioritising reproducibility and interpretability.

---

# Future Work

Future development will explore

- Graph Neural Networks for spatial dependency modelling
- Transformer-based temporal forecasting
- Distributed raster and vector computation using Dask
- PostGIS integration
- Cloud-native deployment
- Kubernetes orchestration
- Real-time streaming analytics
- Reinforcement learning for intervention planning
- Multi-city benchmarking
- Explainable spatial AI

---

# Applications

CrimeScope can support research and operational workflows in

- Urban Analytics
- Smart Cities
- Public Safety
- Spatial Epidemiology
- Environmental Risk Analysis
- Transportation Planning
- Emergency Management
- Geospatial Artificial Intelligence

---

# Citation

If you use CrimeScope in academic work, please cite

```text
Naval Kishore

CrimeScope: A Scalable Geospatial Machine Learning Platform for Urban Crime Intelligence, Spatial Risk Mapping, and Temporal Forecasting.

GitHub Repository, 2026.
```

---

# License

This project is released under the MIT License.

---

# Acknowledgements

CrimeScope builds upon the outstanding open-source geospatial and scientific Python ecosystem, including

- GeoPandas
- Shapely
- PySAL
- scikit-learn
- Statsmodels
- Streamlit
- Folium
- Pandas
- NumPy

whose contributions make modern computational geography and spatial data science possible.
