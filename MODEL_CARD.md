# **Model Card: Chicago Crime Spatial Risk & Forecasting Suite**

## **Version**

**v2.0 — March 2026**

---

# **1. Model Overview**

This project provides a suite of statistical, machine learning, and spatial models designed to analyse crime patterns in the City of Chicago.
Models operate on a fine-grained 100-metre hexagonal grid and support detection of crime hotspots, generation of spatial risk surfaces, and forecasting of future incident counts.

The modelling suite includes:

| Category                    | Models                                                |
| --------------------------- | ----------------------------------------------------- |
| **Classical Count Models**  | Poisson Regression, Negative Binomial Regression     |
| **Machine Learning**        | Random Forest Regressor, Gradient Boosting Regressor |
| **Spatial Models**          | Geographically Weighted Regression (GWR)             |
| **Spatial Statistics**      | Getis-Ord Gi* Hotspot Analysis, Moran’s I            |
| **Density Estimation**      | Kernel Density Estimation (KDE)                      |
| **Time-Series Forecasting** | SARIMA (monthly crime forecasts)                     |

The goal is exploratory analysis, spatial understanding, and short-term forecasting—**not operational policing**.

---

# **2. Intended Use**

### **Primary Use Cases**

* Academic and policy research
* Urban analytics and neighbourhood planning
* Visualising spatial crime risk patterns
* Studying environmental correlates of crime (lights, transit stops)
* Understanding temporal rhythms (hour, day, month)
* Producing map-based dashboards for decision-support
* Communicating statistical summaries through reports

### **Not Intended For**

* Predictive policing or enforcement targeting
* Identifying individuals
* Real-time security operations
* Allocation of punitive resources

This system is built exclusively for **research**, **visualisation**, and **community-level analysis**.

---

# **3. Data Sources**

### **Input Datasets**

| Dataset               | Source                    | Notes                                     |
| --------------------- | ------------------------- | ----------------------------------------- |
| Crime Incidents       | Chicago Data Portal       | Filtered for valid dates, geocoded points |
| Streetlight Locations | Chicago Data Portal       | All active lights                         |
| CTA Bus Stops         | Chicago Transit Authority | Static GTFS-derived points                |
| City Boundary         | Chicago GIS Portal        | Used to trim the hex grid                 |

### **Preprocessing**

* All coordinates projected into a uniform CRS for spatial accuracy.
* Temporal features extracted: month, day of week, hour.
* Event-to-hex spatial joins performed using centroid-in-polygon tests.

---

# **4. Model Details**

## **4.1 Poisson Regression**

* **Type:** Generalised Linear Model (GLM)
* **Target:** Total crime count per cell
* **Strengths:** Interpretability, baseline comparison
* **Limitations:** Assumes equidispersion (variance ≈ mean)

---

## **4.2 Negative Binomial Regression**

* **Purpose:** Corrects Poisson overdispersion
* **Outputs:** Predicted crime counts and dispersion metrics
* **Limitations:** Captures only global relationships

---

## **4.3 Random Forest**

* **Type:** Ensemble tree model
* **Strengths:** Handles nonlinear patterns, complex interactions
* **Outputs:** `pred_rf`, feature importances
* **Limitations:** No inherent spatial awareness

---

## **4.4 Gradient Boosting**

* **Type:** Tree-based boosting ensemble
* **Strengths:** Captures nonlinearities and complex interactions with smoother function estimates than RF
* **Outputs:** `pred_gb`
* **Limitations:** Less interpretable than GLMs; still non-spatial

---

## **4.5 Geographically Weighted Regression (GWR)**

* **Type:** Localised regression with spatially varying coefficients
* **Outputs:** Local coefficients and predictions (`pred_gwr`)
* **Strengths:** Shows *where* features matter more
* **Limitations:** Sensitive to bandwidth choice; computationally heavier

---

## **4.6 Spatial Hotspot Model (Getis-Ord Gi*)**

* **Type:** Local spatial statistic
* **Outputs:**

  * `gi_star` — statistic
  * `gi_z` — z-scores
  * `gi_p` — p-values
* **Interpretation:**

  * High z = significant hotspot
  * Low z = coldspot
* **Limitations:** Requires well-connected spatial weights

---

## **4.7 Kernel Density Estimation (KDE)**

* Produces a smooth intensity surface of event density.
* Useful for heatmaps and hotspot visualisation.

---

## **4.8 Time-Series Forecasting**

* **Model:** SARIMA
* **Input:** Monthly aggregated counts
* **Horizons:** 6 months
* **Limitations:** Requires sufficient historical depth (≥ 2 months)
* **Use:** Macro-level trend indication, not operational prediction

---

# **5. Model Performance & Validation**

Validation is descriptive rather than predictive. Metrics include:

### **For GLM Models**

* Deviance
* AIC / BIC
* Dispersion ratio

### **For Tree-Based Models (RF / GB)**

* RMSE and R² on observed counts
* Feature importances for key predictors (e.g. streetlight_count, bus_count, crime subtypes)

### **For GWR / Local Linear**

* Local R² (where available)
* Approximate RMSE and R² based on `pred_gwr`

### **For Hotspot Detection**

* Moran’s I before/after hotspot classification
* Spatial clustering diagnostics

### **For Time-Series**

* AIC / BIC
* In-sample RMSE

---

# **6. Ethical Considerations**

### **Bias & Fairness**

Crime data reflect reporting behaviour, policing patterns, and systemic inequities.
Models built on such data **cannot be considered unbiased**.

### **No Person-Level Predictions**

The system does not and must not identify individuals.

### **Community Harm Prevention**

Spatial predictions risk being misinterpreted as justifications for aggressive policing.
This project must not be deployed operationally in law enforcement contexts.

### **Transparency**

Model coefficients, spatial surfaces, and summary statistics are all intentionally exposed to ensure interpretability.

---

# **7. Limitations**

* Historical crime datasets contain missing, delayed, or inconsistent records.
* Crime counts represent *reported* incidents, not true prevalence.
* Fine-grained spatial modelling (<100m grid) may introduce:

  * Islands (cells with no neighbours)
  * Sparse data issues
* Forecasting accuracy decreases rapidly with small temporal samples.
* KDE and Gi* are descriptive tools, **not predictors**.

---

# **8. Recommendations for Use**

* Use RF and GWR predictions for exploratory insight, not decision-making.
* Interpret coefficient maps alongside socio-economic context.
* Always complement hotspot maps with ground truth qualitative knowledge.
* When presenting results, emphasise uncertainty and limitations.

---

# **9. Maintenance**

### **Pipeline Regeneration**

The full pipeline can be recomputed via:

```
python run_pipeline.py
```

### **Dashboard Execution**

Start the interactive Dash app using:

```
python run_app.py
```

### **Versioning**

Model outputs are stored as timestamped Parquet files.
Forecasts and reports are archived under `data/processed/`.

---

# **10. Contact & Governance**

| Role           | Responsibility                         |
| -------------- | -------------------------------------- |
| Maintainer     | Pipeline integrity, modelling updates  |
| Data Custodian | Ensures compliance with data licensing |
| Reviewer       | Validates methodological changes       |

For questions or contributions, see the project's **CONTRIBUTING.md**.