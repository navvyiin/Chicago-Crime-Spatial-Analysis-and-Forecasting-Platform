from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import pathlib

from .maps import (
    make_static_map,
    make_animated_map,
    gdf,
    monthly_df,
)
from src.reporting import generate_pdf_summary
from src.spatial_stats import compute_moran
from src.config import FORECAST_FILE


# Register callbacks

def register_callbacks(app):

    # TAB SWITCHING CALLBACK

    @app.callback(
        Output("tab-content", "children"),
        Input("tabs", "value"),
        Input("model-choice", "value"),
        Input("color-scale", "value"),
        Input("animate-toggle", "value"),
        Input("crime-type", "value"),
        Input("hour-slider", "value"),
        Input("dow-checklist", "value"),
    )
    def render_tab(tab, model_choice, color_scale, animate_value, crime_type, hour, dows):

        animate = "animate" in (animate_value or [])

        # TAB 1: MAP TAB

        if tab == "tab-map":
            if animate and model_choice == "observed":
                fig = make_animated_map(crime_type, color_scale, hour, dows)
            else:
                fig = make_static_map(model_choice, color_scale, crime_type, hour, dows)

            return html.Div(
                dcc.Graph(id="risk-map", figure=fig, style={"height": "82vh"}),
                style={"overflow": "hidden"}
            )

        # TAB 2: STATISTICS TAB

        elif tab == "tab-stats":

            # Summary table

            cols = [
                "crime_count_total",
                "streetlight_count",
                "bus_count",
                "pred_poisson",
                "pred_nb",
                "pred_rf",
                "pred_gwr",
                "gi_z",
                "kde_intensity",
            ]
            cols = [c for c in cols if c in gdf.columns]

            desc = gdf[cols].describe().reset_index()
            stats_table = dbc.Table.from_dataframe(
                desc, striped=True, bordered=True, hover=True
            )

            # Moran’s I

            try:
                moran = compute_moran(gdf)
                moran_block = html.Div(
                    [
                        html.H5("Spatial autocorrelation (Moran’s I)"),
                        html.P(f"Moran’s I: {moran.I:.4f}"),
                        html.P(f"p-value: {moran.p_norm:.4f}"),
                    ]
                )
            except Exception as e:
                moran_block = html.Div(
                    ["Moran’s I failed to compute.", html.Br(), str(e)]
                )

            # Hotspot Scatterplot (Gi*)

            if "gi_star" in gdf.columns:
                fig_hot = px.scatter(
                    gdf,
                    x=gdf.index,
                    y="gi_star",
                    title="Gi* Z-scores (per grid cell)",
                )
            else:
                fig_hot = px.scatter(title="Gi* not available")

            # KDE distribution

            if "kde_intensity" in gdf.columns:
                fig_kde = px.histogram(
                    gdf,
                    x="kde_intensity",
                    nbins=40,
                    title="Distribution of KDE intensity",
                )
            else:
                fig_kde = px.scatter(title="KDE not available")

            # Forecast plot

            forecast_block = html.Div(
                html.P("No forecast available."),
            )

            if pathlib.Path(FORECAST_FILE).exists():
                forecast_df = pd.read_parquet(FORECAST_FILE)

                if len(forecast_df) > 0:
                    fig_forecast = px.line(
                        forecast_df,
                        x="month",
                        y="forecast",
                        title="Forecasted crime totals (next months)",
                    )
                    forecast_block = dcc.Graph(figure=fig_forecast)

            # Assemble statistics tab

            return html.Div(
                [
                    html.H4("Summary statistics"),
                    stats_table,
                    html.Hr(),
                    moran_block,
                    html.Hr(),
                    html.H5("Hotspot Statistics (Gi*)"),
                    dcc.Graph(figure=fig_hot),
                    html.Hr(),
                    html.H5("KDE Intensity Distribution"),
                    dcc.Graph(figure=fig_kde),
                    html.Hr(),
                    html.H5("Forecasting"),
                    forecast_block,
                ],
                style={"padding": "1rem"},
            )

        return html.Div("Unknown tab")


    # EXPORT CSV

    @app.callback(
        Output("download-csv", "data"),
        Input("download-csv-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_csv(n_clicks):

        df = gdf.drop(columns=["geometry"], errors="ignore")
        return dcc.send_data_frame(
            df.to_csv,
            "crime_model_results.csv",
            index=False,
        )

        
    # EXPORT PDF

    @app.callback(
        Output("download-pdf", "data"),
        Input("download-pdf-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_pdf(n_clicks):

        moran = compute_moran(gdf)
        pdf_path = generate_pdf_summary(gdf, moran)

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        return dcc.send_bytes(
            pdf_bytes,
            filename="crime_summary.pdf"
        )