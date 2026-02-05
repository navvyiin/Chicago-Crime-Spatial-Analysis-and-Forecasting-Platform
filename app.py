from dash import Dash
import dash_bootstrap_components as dbc
from .layout import build_layout
from .callbacks import register_callbacks

crime_types = ["BURGLARY", "ROBBERY", "ASSAULT"]

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Chicago Environmental Criminology Dashboard"
app.layout = build_layout(crime_types)

register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)