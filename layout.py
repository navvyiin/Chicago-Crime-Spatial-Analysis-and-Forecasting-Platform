from dash import dcc, html
import dash_bootstrap_components as dbc

# Sidebar with controls

def build_sidebar(crime_types):
    return dbc.Card(
        [
            html.H4("Controls"),
            
            # Crime type selector

            html.Label("Crime type"),
            dcc.Dropdown(
                id="crime-type",
                options=[{"label": c.title(), "value": c} for c in crime_types]
                        + [{"label": "All selected types", "value": "ALL"}],
                value="ALL",
                clearable=False,
            ),
            html.Br(),

            # Model selector

            html.Label("Model"),
            dcc.RadioItems(
                id="model-choice",
                options=[
                    {"label": "Observed", "value": "observed"},
                    {"label": "Poisson", "value": "pred_poisson"},
                    {"label": "NegBin", "value": "pred_nb"},
                    {"label": "Random Forest", "value": "pred_rf"},
                    {"label": "GWR", "value": "pred_gwr"},
                    {"label": "Hotspot (Gi*)", "value": "hotspot"},
                    {"label": "KDE intensity", "value": "kde"},
                ],
                value="observed",
            ),
            html.Br(),

            # Colour scale

            html.Label("Colour scale"),
            dcc.Dropdown(
                id="color-scale",
                options=[
                    {"label": "Viridis", "value": "Viridis"},
                    {"label": "Plasma", "value": "Plasma"},
                    {"label": "Inferno", "value": "Inferno"},
                    {"label": "Blues", "value": "Blues"},
                    {"label": "Reds", "value": "Reds"},
                ],
                value="Viridis",
                clearable=False,
            ),
            html.Br(),

            # Hour slider

            html.Label("Hour of day"),
            dcc.Slider(
                id="hour-slider",
                min=0,
                max=23,
                step=1,
                value=12,
                marks={h: str(h) for h in range(0, 24, 3)},
            ),
            html.Br(),

            # Day-of-week selector

            html.Label("Day of week"),
            dcc.Checklist(
                id="dow-checklist",
                options=[
                    {"label": "Mon", "value": 0},
                    {"label": "Tue", "value": 1},
                    {"label": "Wed", "value": 2},
                    {"label": "Thu", "value": 3},
                    {"label": "Fri", "value": 4},
                    {"label": "Sat", "value": 5},
                    {"label": "Sun", "value": 6},
                ],
                value=[0, 1, 2, 3, 4, 5, 6],
                inline=True,
            ),
            html.Br(),

            # Animation toggle

            dcc.Checklist(
                id="animate-toggle",
                options=[{"label": "Animate monthly counts", "value": "animate"}],
                value=[],
            ),
            html.Br(),

            # Downloads

            dbc.Button("Download CSV", id="download-csv-btn", color="primary", className="mb-2"),
            dcc.Download(id="download-csv"),

            dbc.Button("Download PDF summary", id="download-pdf-btn", color="secondary"),
            dcc.Download(id="download-pdf"),
        ],
        body=True,
    )


# Tabs layout

def build_layout(crime_types):

    sidebar = build_sidebar(crime_types)

    tabs = dcc.Tabs(
        id="tabs",
        value="tab-map",
        children=[
            dcc.Tab(label="Risk Map", value="tab-map"),
            dcc.Tab(label="Statistics & Forecast", value="tab-stats"),
        ],
    )

    return dbc.Container(
        fluid=True,
        children=[
            # Title
            dbc.Row(
                dbc.Col(html.H2("Chicago Crime Risk Dashboard — 2025 Analysis"), width=12),
                className="my-2",
            ),

            dbc.Row(
                [
                    # Sidebar
                    dbc.Col(sidebar, width=3),

                    # Content
                    dbc.Col(
                        [
                            tabs,
                            html.Div(id="tab-content", className="mt-3"),
                        ],
                        width=9,
                    ),
                ],
                className="g-2",
            ),
        ],
    )


# Entry point for Dash app

def serve_layout():
    return build_layout(crime_types=["BURGLARY", "ROBBERY", "ASSAULT"])