"""Aplicación Dash principal del hub de cartera de inversión."""

from dash import Dash, html

app = Dash(__name__, title="Hub de Cartera")
server = app.server  # necesario para gunicorn (Procfile / render.yaml)

app.layout = html.Div(
    children=[
        html.H1("Hub de Cartera de Inversión"),
        html.Div("Aplicación en construcción."),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
