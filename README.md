# **Chicago Crime Spatial Analysis & Forecasting Platform (2025)**

*A geospatial machine learning pipeline for risk mapping, hotspot detection, and temporal crime forecasting.*

---

## **Overview**

This project delivers a complete end-to-end geospatial analytics workflow for the City of Chicago’s crime data.
It integrates spatial statistics, machine learning models, temporal forecasting, and interactive visualisation through a high-performance Streamlit dashboard.

The platform is designed with modularity, reproducibility, and scalability in mind.
It can be deployed as a research tool, an internal analytics product, or part of a smart-city decision support system.

---

## **Key Capabilities**

### **1. Spatial Data Engineering**

* Automatic construction of a **hexagonal spatial grid** (configurable resolution, default 100 metres).
* Ingestion and preprocessing of:

  * Reported crime incidents
  * Streetlight locations
  * Public transport infrastructure (CTA bus stops)
  * City administrative boundaries
* Spatial joins, feature engineering, temporal extraction, and aggregation.

### **2. Statistical Modelling**

* **Poisson and Negative Binomial regression** for baseline risk estimation.
* **Random Forest regression** for non-linear pattern capture and feature interaction modelling.
* **Geographically Weighted Regression (GWR)** or **Local Linear Modelling** depending on dataset scale.
* Automated overdispersion diagnostics and fallback strategies for stability.

### **3. Spatial Statistics**

* **Moran’s I** global autocorrelation.
* **Local Getis-Ord Gi*** hotspot detection using robust KNN-based weights.
* **Kernel Density Estimation (KDE)** for intensity surface generation.

### **4. Time Series Forecasting**

* Monthly crime activity forecasting using Exponential Smoothing (ETS).
* Graceful degradation logic when insufficient historical depth exists.

### **5. Interactive Visual Dashboard**

Built using **Streamlit + Plotly** with:

* Choropleth risk maps (observed, model predictions, and a composite risk index)
* Uncertainty visualisation via prediction interval width
* Hotspot and KDE visual layers
* Hour-of-day and day-of-week filtering
* Animated temporal crime maps
* Forecast charts with diagnostics
* Model comparison tables and metrics
* Scenario-based “what if” interventions on high-risk cells
* PDF and CSV export functionality

---

## **Project Structure**

```
env-crime-spatial-field/
│
├── app/                         
│   ├── maps.py                  # Map rendering utilities shared with Streamlit app
│   └── __init__.py
│
├── crime_env/                   # Virtual environment
│
├── data/ or Data/               # Case-insensitive handling on different OSes
│   ├── raw/                     # Raw inputs: shapefiles, CSVs
│   │   ├── Chicago_City_Limits.shp
│   │   ├── crimes.csv
│   │   ├── street_lights_all_out.csv
│   │   └── CTA_BusStops.*
│   ├── processed/               # Pipeline outputs
│   │   ├── hex_grid.gpkg
│   │   ├── features.parquet
│   │   ├── model_results.parquet
│   │   ├── forecast_monthly.parquet
│   │   ├── monthly_cell_crime.parquet
│   │   └── reports/
│   │       └── crime_summary_*.pdf
│
├── src/                         # Core analytics pipeline
│   ├── aggregate.py             # Spatial aggregation and feature construction
│   ├── build_grid.py            # Hex grid generation (100m default)
│   ├── config.py                # File paths and global settings
│   ├── load_data.py             # Data ingestion utilities
│   ├── model_poisson_nb.py      # GLM models (Poisson & Negative Binomial)
│   ├── model_rf_gwr.py          # Random Forest + Gradient Boosting + GWR + fallback methods
│   ├── spatial_stats.py         # Moran’s I, Gi*, KDE
│   ├── timeseries.py            # Monthly SARIMA forecasting + diagnostics
│   ├── reporting.py             # PDF report generation
│   └── __init__.py
│
├── run_pipeline.py              # Executes full analytical workflow
├── streamlit_app.py             # Launches Streamlit dashboard
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## **Installation**

### **1. Create and activate a virtual environment**

```bash
python -m venv crime_env
source crime_env/bin/activate       # Linux/Mac
crime_env\Scripts\activate          # Windows
```

### **2. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## **Data Requirements**

The `data/raw/` directory must contain:

| Dataset                     | Description                                |
| --------------------------- | ------------------------------------------ |
| `Chicago_City_Limits.shp`   | City boundary polygon                      |
| `crimes.csv`                | Crime incident dataset with geocoordinates |
| `street_lights_all_out.csv` | Streetlight point dataset                  |
| `CTA_BusStops.*`            | CTA bus stops shapefile                    |

All datasets must be in **WGS84 (EPSG:4326)** or will be reprojected during ingestion.

---

## **Running the Pipeline**

Execute the full modelling and spatial processing workflow:

```bash
python run_pipeline.py
```

This produces:

* Hex grid
* Feature matrices
* Statistical models
* Spatial autocorrelation diagnostics
* Hotspot intensity surfaces
* Forecast time-series
* Automated PDF summary reports

---

## **Launching the Dashboard**

After running the pipeline:

```bash
streamlit run streamlit_app.py
```

---

## **Outputs**

### **1. Spatial Model Results**

Stored in:

```
data/processed/model_results.parquet
```

Contains:

* Environmental features
* Crime counts
* Model predictions (Poisson, NB, RF, GWR/LLM)
* Gi* z-scores
* KDE intensities

### **2. Temporal Forecast**

```
data/processed/forecast_monthly.parquet
```

### **3. Hex Grid**

```
data/processed/hex_grid.gpkg
```

### **4. Automated PDF Summary**

Located under:

```
data/processed/reports/
```

---

## **Configuration**

Global parameters such as file paths, hexagon size, and output locations are controlled in:

```
src/config.py
```

Hexagon resolution (default 100 metres) can be adjusted by modifying:

```python
HEX_DIAMETER = 100.0
```

Or via pipeline:

```bash
python run_pipeline.py --hex 100
```

---

## **Technical Notes**

* The pipeline uses a **KNN spatial weights matrix** to avoid island effects and ensure numerical stability.
* GWR is automatically replaced by a **Local Linear regression kernel** for grids exceeding ~6,000 cells.
* KDE uses the centroids of hexagons instead of raw incidents for computational efficiency.
* The forecasting module automatically bypasses insufficient time-series depth.

---

## **Best Practices and Extensibility**

The project follows a modular architecture enabling:

* Replacement of machine learning models
* Integration of additional environmental predictors
* Migration to PostGIS or cloud data storage
* Deployment as a production-grade web service (Gunicorn/Nginx)
* Extension to other cities or administrative boundaries

---

## **Contact & Contributions**

This project is actively maintained.
Contributions, issue reports, and feature suggestions are welcome.