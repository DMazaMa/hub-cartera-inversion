import pandas as pd
from dash import Dash, Input, Output, ctx, dcc, html

from src.etl import DATA_DIR
from src.graphics import grafico_evolucion

posiciones = pd.read_csv(DATA_DIR / "posiciones.csv")
evolucion = pd.read_csv(DATA_DIR / "evolucion.csv")

valor_total = posiciones["valor"].sum()
invertido_total = posiciones["invertido"].sum()
plusvalia_total = valor_total - invertido_total
dividendos_total = posiciones["dividendos"].sum()

secciones = ["Inicio", "Cartera", "Composición", "Rentabilidad", "Operaciones"]
ids_secciones = ["inicio", "cartera", "composicion", "rentabilidad", "operaciones"]


def formato(numero: float, simbolo: str = " €") -> str:
    texto = f"{numero:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return texto + simbolo


def color_signo(numero: float) -> str:
    if numero >= 0:
        return "mediumseagreen"
    return "firebrick"


def tarjeta(titulo: str, valor: str, color: str = "black") -> html.Div:
    return html.Div(
        children=[
            html.P(
                children=[titulo],
                style={"margin": "0px", "color": "gray", "font-size": "14px"},
            ),
            html.H3(
                children=[valor],
                style={"margin": "5px 0px 0px 0px", "color": color},
            ),
        ],
        style={
            "display": "inline-block",
            "width": "200px",
            "padding": "15px",
            "margin": "10px",
            "backgroundColor": "white",
            "border-radius": "8px",
            "box-shadow": "0px 1px 4px lightgray",
        },
    )


cinta = []
for i in range(len(posiciones)):
    variacion = posiciones.loc[i, "variacion_dia"]
    if variacion >= 0:
        flecha = "▲"
    else:
        flecha = "▼"
    cinta.append(
        html.Span(
            children=[
                posiciones.loc[i, "nombre"] + " ",
                html.B(
                    children=[flecha + " " + formato(variacion, " %")],
                    style={"color": color_signo(variacion)},
                ),
            ],
            style={"margin-right": "40px", "white-space": "nowrap"},
        )
    )

estilo_boton = {
    "height": "40px",
    "padding": "0px 20px",
    "margin-right": "10px",
    "border": "1px solid steelblue",
    "border-radius": "20px",
    "font-size": "15px",
    "cursor": "pointer",
}

botones = []
for i in range(len(secciones)):
    botones.append(
        html.Button(
            children=[secciones[i]],
            id="boton_" + ids_secciones[i],
            n_clicks=0,
            style=estilo_boton,
        )
    )

app = Dash(__name__, title="Hub de Cartera")
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children=["Hub de Cartera de Inversión"],
                    id="titulo",
                    style={"margin": "0px", "font-size": "28px"},
                ),
                html.P(
                    children=["Seguimiento de mi cartera de MyInvestor"],
                    style={"margin": "5px 0px 0px 0px", "color": "lightsteelblue"},
                ),
            ],
            id="cabecera",
            style={
                "backgroundColor": "midnightblue",
                "color": "white",
                "padding": "20px",
            },
        ),
        html.Div(
            children=cinta,
            id="cinta",
            style={
                "backgroundColor": "white",
                "padding": "10px 20px",
                "overflow-x": "auto",
                "white-space": "nowrap",
                "border-bottom": "1px solid lightgray",
            },
        ),
        html.Div(
            children=botones,
            id="menu",
            style={
                "padding": "10px 20px",
                "overflow-x": "auto",
                "white-space": "nowrap",
            },
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        tarjeta("Valor de la cartera", formato(valor_total)),
                        tarjeta("Capital invertido", formato(invertido_total)),
                        tarjeta(
                            "Plusvalía latente",
                            formato(plusvalia_total),
                            color_signo(plusvalia_total),
                        ),
                        tarjeta(
                            "Rentabilidad",
                            formato(plusvalia_total / invertido_total * 100, " %"),
                            color_signo(plusvalia_total),
                        ),
                        tarjeta("Dividendos cobrados", formato(dividendos_total)),
                    ],
                    id="fila_tarjetas",
                ),
                dcc.Graph(
                    figure=grafico_evolucion(evolucion),
                    id="figura_evolucion",
                    style={"margin": "10px"},
                ),
            ],
            id="seccion_inicio",
        ),
        html.Div(children=[html.H2("Cartera")], id="seccion_cartera"),
        html.Div(children=[html.H2("Composición")], id="seccion_composicion"),
        html.Div(children=[html.H2("Rentabilidad")], id="seccion_rentabilidad"),
        html.Div(children=[html.H2("Operaciones")], id="seccion_operaciones"),
    ],
    style={
        "font-family": "Arial",
        "backgroundColor": "whitesmoke",
        "min-height": "100vh",
    },
)


@app.callback(
    Output("seccion_inicio", "style"),
    Output("seccion_cartera", "style"),
    Output("seccion_composicion", "style"),
    Output("seccion_rentabilidad", "style"),
    Output("seccion_operaciones", "style"),
    Output("boton_inicio", "style"),
    Output("boton_cartera", "style"),
    Output("boton_composicion", "style"),
    Output("boton_rentabilidad", "style"),
    Output("boton_operaciones", "style"),
    Input("boton_inicio", "n_clicks"),
    Input("boton_cartera", "n_clicks"),
    Input("boton_composicion", "n_clicks"),
    Input("boton_rentabilidad", "n_clicks"),
    Input("boton_operaciones", "n_clicks"),
)
def mostrar_seccion(n_inicio, n_cartera, n_composicion, n_rentabilidad, n_operaciones):
    pulsado = ctx.triggered_id
    if pulsado is None:
        pulsado = "boton_inicio"

    estilos_secciones = []
    estilos_botones = []
    for seccion in ids_secciones:
        estilo = estilo_boton.copy()
        if "boton_" + seccion == pulsado:
            estilos_secciones.append({"display": "block", "padding": "0px 10px"})
            estilo["backgroundColor"] = "steelblue"
            estilo["color"] = "white"
        else:
            estilos_secciones.append({"display": "none"})
            estilo["backgroundColor"] = "white"
            estilo["color"] = "steelblue"
        estilos_botones.append(estilo)
    return tuple(estilos_secciones + estilos_botones)


if __name__ == "__main__":
    app.run(debug=True)
