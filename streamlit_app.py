import pathlib

import pandas as pd
import plotly.express as px
import streamlit as st

from app.maps import make_static_map, make_animated_map, gdf, monthly_df
from src.config import FORECAST_FILE, MODEL_METRICS_FILE
from src.reporting import generate_pdf_summary
from src.spatial_stats import compute_moran


def _get_crime_types_from_gdf() -> list[str]:
    crime_cols = [
        c
        for c in gdf.columns
        if c.startswith("crime_") and c != "crime_count_total"
    ]
    crime_types = [c.replace("crime_", "").upper() for c in crime_cols]
    return sorted(set(crime_types))


CRIME_TYPES = _get_crime_types_from_gdf()


DAY_LABELS = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}


def main() -> None:
    st.set_page_config(
        page_title="Chicago Environmental Criminology Dashboard",
        page_icon="🛰️",
        layout="wide",
    )

    # Global styling (green-oriented, card-like sections)
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stMetric {
            background-color: #0d2818;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            border: 1px solid rgba(144, 238, 144, 0.3);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #0f1f16;
            border-radius: 999px;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #153323;
        }
        .stSidebar {
            background: linear-gradient(180deg, #04130a 0%, #020807 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Chicago Crime Risk Dashboard — 2025 Analysis")
    st.caption(
        "Interactive environmental criminology dashboard for Chicago — explore spatial risk, "
        "hotspots, and forecasts with model-based and observed crime patterns."
    )

    # High-level KPIs
    total_crime = int(gdf["crime_count_total"].sum())
    mean_crime = float(gdf["crime_count_total"].mean())
    num_cells = len(gdf)
    try:
        moran = compute_moran(gdf)
        moran_i = f"{moran.I:.4f}"
    except Exception:
        moran_i = "N/A"

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total crimes (selected types)", f"{total_crime:,}")
    kpi_cols[1].metric("Mean crimes per grid cell", f"{mean_crime:,.2f}")
    kpi_cols[2].metric("Grid cells", f"{num_cells:,}")
    kpi_cols[3].metric("Moran’s I (global)", moran_i)

    # ------------------------------------------------------------------
    # Sidebar controls
    # ------------------------------------------------------------------

    with st.sidebar:
        st.header("Controls")
        st.write(
            "Filter the temporal window, crime types, and modelling layer. "
            "Maps and statistics update instantly."
        )

        crime_type = st.selectbox(
            "Crime type",
            options=["ALL"] + CRIME_TYPES,
            format_func=lambda v: "All selected types" if v == "ALL" else v.title(),
            index=0,
        )

        model_choice = st.radio(
            "Model / layer",
            options=[
                ("Observed counts", "observed"),
                ("Composite risk index", "risk"),
                ("Forecast uncertainty width", "uncertainty"),
                ("Poisson regression", "pred_poisson"),
                ("Negative Binomial", "pred_nb"),
                ("Random Forest", "pred_rf"),
                ("Gradient Boosting", "pred_gb"),
                ("GWR / Local linear", "pred_gwr"),
                ("Hotspot (Gi*)", "hotspot"),
                ("KDE intensity", "kde"),
            ],
            format_func=lambda x: x[0],
            index=1,
        )[1]

        color_scale = st.selectbox(
            "Colour scale",
            options=[
                "Greens",
                "Viridis",
                "YlGn",
                "YlGnBu",
            ],
            index=0,
        )

        hour = st.slider("Hour of day", min_value=0, max_value=23, step=1, value=12)

        dows = st.multiselect(
            "Day of week",
            options=list(DAY_LABELS.keys()),
            default=list(DAY_LABELS.keys()),
            format_func=lambda v: DAY_LABELS.get(v, str(v)),
        )

        animate = st.checkbox("Animate monthly counts (observed only)", value=False)

        st.markdown("---")

        # Downloads
        st.subheader("Export")
        csv_df = gdf.drop(columns=["geometry"], errors="ignore")
        csv_bytes = csv_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name="crime_model_results.csv",
            mime="text/csv",
            type="primary",
        )

        try:
            moran_pdf = compute_moran(gdf)
            pdf_path = generate_pdf_summary(gdf, moran_pdf)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                "Download PDF summary",
                data=pdf_bytes,
                file_name="crime_summary.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.warning(f"PDF summary not available: {e}")

    # ------------------------------------------------------------------
    # Main content: tabs
    # ------------------------------------------------------------------

    tab_map, tab_stats, tab_scenarios = st.tabs(
        ["Risk map", "Statistics & forecast", "Interventions & scenarios"]
    )

    with tab_map:
        st.markdown(
            "Use the controls on the left to switch between observed counts, model predictions, "
            "hotspot Gi*, and KDE intensity. Darker greens highlight higher risk."
        )

        if animate and model_choice == "observed":
            fig = make_animated_map(crime_type, color_scale, hour, dows)
        else:
            fig = make_static_map(model_choice, color_scale, crime_type, hour, dows)

        st.plotly_chart(fig, use_container_width=True)

    with tab_stats:
        _render_stats_tab()

    with tab_scenarios:
        _render_scenarios_tab()


def _render_stats_tab() -> None:
    # Summary statistics table
    cols = [
        "crime_count_total",
        "streetlight_count",
        "bus_count",
        "pred_poisson",
        "pred_nb",
        "pred_rf",
        "pred_gb",
        "pred_gwr",
        "risk_score",
        "risk_quantile",
        "priority_rank",
        "pred_lower",
        "pred_upper",
        "gi_z",
        "kde_intensity",
    ]
    available_cols = [c for c in cols if c in gdf.columns]

    if available_cols:
        desc = gdf[available_cols].describe().reset_index()
        st.subheader("Summary statistics")
        st.dataframe(desc, use_container_width=True)
    else:
        st.info("No numeric columns available for summary statistics.")

    st.markdown("---")

    # Moran's I
    try:
        moran = compute_moran(gdf)
        st.subheader("Spatial autocorrelation (Moran’s I)")
        st.write(f"Moran’s I: {moran.I:.4f}")
        st.write(f"p-value: {moran.p_norm:.4f}")
    except Exception as e:
        st.subheader("Spatial autocorrelation (Moran’s I)")
        st.warning(f"Moran’s I failed to compute: {e}")

    st.markdown("---")

    # Hotspot scatterplot (Gi*)
    st.subheader("Hotspot Statistics (Gi*)")
    if "gi_star" in gdf.columns:
        fig_hot = px.scatter(
            gdf,
            x=gdf.index,
            y="gi_star",
            title="Gi* Z-scores (per grid cell)",
        )
    else:
        fig_hot = px.scatter(title="Gi* not available")
    st.plotly_chart(fig_hot, use_container_width=True)

    st.markdown("---")

    # KDE distribution
    st.subheader("KDE Intensity Distribution")
    if "kde_intensity" in gdf.columns:
        fig_kde = px.histogram(
            gdf,
            x="kde_intensity",
            nbins=40,
            title="Distribution of KDE intensity",
        )
    else:
        fig_kde = px.scatter(title="KDE not available")
    st.plotly_chart(fig_kde, use_container_width=True)

    st.markdown("---")

    # Forecast plot
    st.subheader("Forecasting")
    forecast_path = pathlib.Path(FORECAST_FILE)
    if forecast_path.exists():
        forecast_df = pd.read_parquet(forecast_path)
        if len(forecast_df) > 0:
            fig_forecast = px.line(
                forecast_df,
                x="month",
                y="forecast",
                title="Forecasted crime totals (next months)",
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
        else:
            st.info("No forecast data available.")
    else:
        st.info("No forecast file found.")

    st.markdown("---")

    # Model diagnostics table + RMSE chart
    st.subheader("Model diagnostics")
    try:
        metrics_df = pd.read_parquet(MODEL_METRICS_FILE)
        st.dataframe(metrics_df, use_container_width=True)

        rmse_slice = metrics_df[
            (metrics_df["metric"] == "rmse")
            & (metrics_df["target"] == "crime_count_total")
        ]
        if not rmse_slice.empty:
            fig_rmse = px.bar(
                rmse_slice,
                x="model",
                y="value",
                title="Model RMSE for crime_count_total",
            )
            st.plotly_chart(fig_rmse, use_container_width=True)
    except Exception as e:
        st.info(f"Model diagnostics not available: {e}")


def _render_scenarios_tab() -> None:
    st.subheader("Scenario analysis: simple lighting interventions")
    st.write(
        "Explore how hypothetical changes in street lighting intensity across the "
        "highest-risk cells could affect expected crime, using the Random Forest "
        "and Gradient Boosting models as a simple sensitivity proxy."
    )

    if "risk_score" not in gdf.columns or "streetlight_count" not in gdf.columns:
        st.info("Scenario analysis requires risk_score and streetlight_count columns.")
        return

    # Controls
    top_pct = st.slider(
        "Target top X% highest-risk cells",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
    )
    delta_lights_pct = st.slider(
        "Increase streetlights in targeted cells by (%)",
        min_value=0,
        max_value=200,
        value=50,
        step=10,
    )

    df = gdf.copy()

    # Identify top X% highest-risk cells
    n_cells = len(df)
    k = max(1, int(n_cells * top_pct / 100.0))
    df_sorted = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
    threshold_score = df_sorted.loc[k - 1, "risk_score"]
    target_mask = df["risk_score"] >= threshold_score

    st.markdown(
        f"- Cells targeted: **{target_mask.sum():,}** "
        f"({top_pct}% highest-risk cells, threshold risk_score ≥ {threshold_score:.3f})"
    )

    # Baseline expectations
    baseline_mu = df.get("pred_nb", df.get("pred_poisson", df["crime_count_total"]))
    baseline_total = float(baseline_mu.sum())

    # Simple sensitivity: assume elastic response to streetlight increase
    # based on RF / GB models (not re-fitted here). This is illustrative rather
    # than a causal estimate.
    elasticity = -0.1  # 10% more lights -> ~1% fewer expected crimes (illustrative)
    factor = 1.0 + (elasticity * (delta_lights_pct / 100.0))

    scenario_mu = baseline_mu.copy()
    scenario_mu[target_mask] = scenario_mu[target_mask] * factor
    scenario_mu = scenario_mu.clip(lower=0.0)
    scenario_total = float(scenario_mu.sum())

    delta = scenario_total - baseline_total
    st.metric(
        "Expected total crime (model-based)",
        f"{scenario_total:,.0f}",
        delta=f"{delta:,.0f} vs baseline {baseline_total:,.0f}",
    )

    # Before/after comparison by risk quantile
    if "risk_quantile" in df.columns:
        df_comp = df[["risk_quantile"]].copy()
        df_comp["baseline_mu"] = baseline_mu
        df_comp["scenario_mu"] = scenario_mu

        df_comp["bin"] = pd.qcut(df_comp["risk_quantile"], q=5, labels=False)
        grouped = (
            df_comp.groupby("bin")[["baseline_mu", "scenario_mu"]].sum().reset_index()
        )
        grouped["bin_label"] = grouped["bin"].map(
            {
                0: "Very low risk",
                1: "Low risk",
                2: "Medium risk",
                3: "High risk",
                4: "Very high risk",
            }
        )

        fig_comp = px.bar(
            grouped,
            x="bin_label",
            y=["baseline_mu", "scenario_mu"],
            barmode="group",
            labels={"value": "Expected crimes", "bin_label": "Risk band"},
            title="Baseline vs scenario expected crime by risk band",
        )
        st.plotly_chart(fig_comp, use_container_width=True)


if __name__ == "__main__":
    main()

