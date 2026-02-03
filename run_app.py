import os
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans

from utils.rfm_utils import (
    clean_df,
    build_rfm,
    scale_rfm,
    compute_k_options,
    auto_name_segments,
    churn_model_and_scores,
    compute_ltv_deterministic,
)

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Corporate RFM Suite — Extended",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- DATA LOADING -----------------
st.sidebar.title("Controls")
uploaded = st.sidebar.file_uploader("Upload transactions CSV", type=["csv"])
LOCAL_FALLBACK = "data.csv"


def read_csv_flexible(file_obj):
    if isinstance(file_obj, str):
        return pd.read_csv(file_obj, encoding="ISO-8859-1")
    file_obj.seek(0)
    return pd.read_csv(file_obj, encoding="ISO-8859-1")


if uploaded is not None:
    df_raw = read_csv_flexible(uploaded)
elif os.path.exists(LOCAL_FALLBACK):
    df_raw = read_csv_flexible(LOCAL_FALLBACK)
else:
    st.error("Upload a CSV or place data.csv next to app.py")
    st.stop()

df = clean_df(df_raw)

# ----------------- CORE RFM PIPELINE -----------------
rfm, ref_date = build_rfm(df)
scaled, scaler = scale_rfm(rfm)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=20)
rfm["Cluster"] = kmeans.fit_predict(scaled)

segment_map = auto_name_segments(rfm)
rfm["Segment"] = rfm["Cluster"].map(segment_map)

churn_model, rfm = churn_model_and_scores(scaled, rfm)
rfm = compute_ltv_deterministic(rfm, years_period=1, profit_margin=0.3, horizon_years=3)

# ----------------- NAVIGATION -----------------
PAGES = {
    "Executive Overview": "pages.executive",
    "Cluster Profiles": "pages.clusters",
    "LTV & Churn": "pages.ltv",
    "CLTV (Probabilistic)": "pages.cltv_probabilistic",
    "Explainability": "pages.explainability",
    "Embeddings": "pages.embeddings",
    "Uplift Modelling": "pages.uplift",
    "Realtime (example)": "pages.realtime",
    "AI Recommendations": "pages.ai_recommendations",
    "Export": "pages.export",
}

page = st.sidebar.radio("Navigate", list(PAGES.keys()))

# ----------------- LAZY PAGE LOAD -----------------
module_name = PAGES[page]
module = __import__(module_name, fromlist=["render"])

module.render(
    df=df,
    rfm=rfm,
    scaler=scaler,
    churn_model=churn_model,
    segment_map=segment_map,
    ref_date=ref_date,
)

# ----------------- FOOTER -----------------
st.markdown("---")
st.caption(f"Generated at {datetime.now():%Y-%m-%d %H:%M:%S}")
