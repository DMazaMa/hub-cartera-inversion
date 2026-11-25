import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html

from src.etl import DATA_DIR, indices, leer_tabla, normalize_columns
from src.etl import rentabilidad_mensual
from src.graphics import grafico_comparacion, grafico_composicion
from src.graphics import grafico_drawdown, grafico_evolucion, grafico_mensual
from src.graphics import grafico_historico, grafico_pesos, grafico_plusvalias

posiciones = pd.read_csv(DATA_DIR / "posiciones.csv")
evolucion = pd.read_csv(DATA_DIR / "evolucion.csv")
precios_indices = pd.read_csv(DATA_DIR / "indices.csv")
precios = pd.read_csv(DATA_DIR / "precios.csv")
precios["fecha"] = pd.to_datetime(precios["fecha"])
mensual = rentabilidad_mensual(evolucion)
operaciones = pd.read_csv(DATA_DIR / "operaciones_limpias.csv")
operaciones["fecha"] = pd.to_datetime(operaciones["fecha"])
activos = normalize_columns(leer_tabla(DATA_DIR / "activos.csv"))

nombres = {}
for i in range(len(activos)):
    nombres[activos.loc[i, "isin"]] = activos.loc[i, "nombre"]

valor_total = posiciones["valor"].sum()
invertido_total = posiciones["invertido"].sum()
plusvalia_total = valor_total - invertido_total
dividendos_total = posiciones["dividendos"].sum()

rentabilidad_total = evolucion["rentabilidad"].iloc[-1]
volatilidad = evolucion["rendimiento"].std() * (252**0.5) * 100
maximo_drawdown = evolucion["drawdown"].min()
anio_actual = evolucion["fecha"].iloc[-1][:4]
acumulado = 1
for r in evolucion[evolucion["fecha"] >= anio_actual + "-01-01"]["rendimiento"]:
    acumulado = acumulado * (1 + r)
rentabilidad_ytd = (acumulado - 1) * 100

secciones = [
    "Inicio",
    "Cartera",
    "Composición",
    "Rentabilidad",
    "Operaciones",
    "Ficha de activo",
]
ids_secciones = [
    "inicio",
    "cartera",
    "composicion",
    "rentabilidad",
    "operaciones",
    "ficha",
]


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
            "width": "140px",
            "padding": "12px",
            "margin": "6px",
            "backgroundColor": "white",
            "border-radius": "8px",
            "box-shadow": "0px 1px 4px lightgray",
        },
    )


estilo_celda = {
    "padding": "8px 12px",
    "border-bottom": "1px solid gainsboro",
    "text-align": "right",
    "white-space": "nowrap",
}
estilo_cabecera = {
    "padding": "8px 12px",
    "backgroundColor": "midnightblue",
    "color": "white",
    "text-align": "right",
    "white-space": "nowrap",
}


def tabla(cabeceras: list, filas: list) -> html.Div:
    primera_cabecera = estilo_cabecera.copy()
    primera_cabecera["text-align"] = "left"
    primera_celda = estilo_celda.copy()
    primera_celda["text-align"] = "left"

    cabecera = []
    for j in range(len(cabeceras)):
        if j == 0:
            cabecera.append(html.Th(children=[cabeceras[j]], style=primera_cabecera))
        else:
            cabecera.append(html.Th(children=[cabeceras[j]], style=estilo_cabecera))
    cuerpo = []
    for fila in filas:
        celdas = []
        for j in range(len(fila)):
            if j == 0:
                celdas.append(html.Td(children=[fila[j]], style=primera_celda))
            else:
                celdas.append(html.Td(children=[fila[j]], style=estilo_celda))
        cuerpo.append(html.Tr(children=celdas))
    return html.Div(
        children=[
            html.Table(
                children=[html.Thead(html.Tr(cabecera)), html.Tbody(cuerpo)],
                style={
                    "border-collapse": "collapse",
                    "width": "100%",
                    "backgroundColor": "white",
                    "font-size": "14px",
                },
            )
        ],
        style={"overflow-x": "auto", "margin": "10px"},
    )


filas_cartera = []
for i in range(len(posiciones)):
    plusvalia = posiciones.loc[i, "plusvalia"]
    filas_cartera.append(
        [
            html.B(posiciones.loc[i, "nombre"]),
            formato(posiciones.loc[i, "titulos"], ""),
            formato(posiciones.loc[i, "precio_medio"]),
            formato(posiciones.loc[i, "precio_actual"]),
            formato(posiciones.loc[i, "valor"]),
            html.Span(formato(plusvalia), style={"color": color_signo(plusvalia)}),
            html.Span(
                formato(posiciones.loc[i, "plusvalia_pct"], " %"),
                style={"color": color_signo(plusvalia)},
            ),
            formato(posiciones.loc[i, "peso"], " %"),
        ]
    )

cabeceras_cartera = [
    "Activo",
    "Títulos",
    "Precio medio",
    "Precio actual",
    "Valor",
    "Plusvalía",
    "Plusvalía %",
    "Peso",
]

options_dropdown_activo = []
for isin in nombres.keys():
    options_dropdown_activo.append({"label": nombres[isin], "value": isin})

options_dropdown_ficha = []
for i in range(len(posiciones)):
    options_dropdown_ficha.append(
        {"label": posiciones.loc[i, "nombre"], "value": posiciones.loc[i, "isin"]}
    )

options_dropdown_tipo = []
for tipo in ["compra", "venta", "dividendo"]:
    options_dropdown_tipo.append({"label": tipo.capitalize(), "value": tipo})

options_checklist = [
    {"value": "clase", "label": "Clase de activo"},
    {"value": "sector", "label": "Sector"},
    {"value": "region", "label": "Región"},
]

options_dropdown_indice = []
for nombre in indices.keys():
    options_dropdown_indice.append({"label": nombre, "value": nombre})

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
        html.Div(
            children=[
                html.H2(
                    children=["Posiciones de la cartera"],
                    style={"margin": "10px"},
                ),
                tabla(cabeceras_cartera, filas_cartera),
                dcc.Graph(
                    figure=grafico_plusvalias(posiciones),
                    id="figura_plusvalias",
                    style={"margin": "10px"},
                ),
            ],
            id="seccion_cartera",
        ),
        html.Div(
            children=[
                html.H2(
                    children=["Composición de la cartera"],
                    style={"margin": "10px"},
                ),
                dcc.Graph(
                    figure=grafico_pesos(posiciones),
                    id="figura_pesos",
                    style={"margin": "10px"},
                ),
                html.H3(
                    children=["¿Cómo está repartida mi cartera?"],
                    style={"margin": "20px 10px 10px 10px"},
                ),
                html.Div(
                    children=[
                        dcc.Checklist(
                            options=options_checklist,
                            value=["clase", "sector", "region"],
                            labelStyle={
                                "display": "inline-block",
                                "font-size": "16px",
                                "margin-right": "15px",
                            },
                            id="checklist_composicion",
                            style={"display": "inline-block"},
                        ),
                        html.Button(
                            children=["Mostrar"],
                            id="boton_composicion_mostrar",
                            n_clicks=0,
                            style={
                                "backgroundColor": "steelblue",
                                "color": "white",
                                "height": "35px",
                                "width": "100px",
                                "margin": "5px 0px",
                                "border": "none",
                                "border-radius": "5px",
                                "cursor": "pointer",
                            },
                        ),
                    ],
                    style={"margin": "10px"},
                ),
                dcc.Graph(
                    id="pie_charts",
                    style={"display": "none"},
                ),
            ],
            id="seccion_composicion",
        ),
        html.Div(
            children=[
                html.H2(
                    children=["Rentabilidad de la cartera"],
                    style={"margin": "10px"},
                ),
                html.Div(
                    children=[
                        tarjeta(
                            "Rentabilidad total",
                            formato(rentabilidad_total, " %"),
                            color_signo(rentabilidad_total),
                        ),
                        tarjeta(
                            "Rentabilidad " + anio_actual,
                            formato(rentabilidad_ytd, " %"),
                            color_signo(rentabilidad_ytd),
                        ),
                        tarjeta("Volatilidad anual", formato(volatilidad, " %")),
                        tarjeta(
                            "Máxima caída",
                            formato(maximo_drawdown, " %"),
                            "firebrick",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.P(
                            children=["Comparar con:"],
                            style={"display": "inline-block", "margin-right": "10px"},
                        ),
                        dcc.Dropdown(
                            options=options_dropdown_indice,
                            value="MSCI World",
                            clearable=False,
                            id="dropdown_indice",
                            style={
                                "display": "inline-block",
                                "width": "200px",
                                "vertical-align": "middle",
                            },
                        ),
                    ],
                    style={"margin": "10px"},
                ),
                dcc.Graph(id="figura_comparacion", style={"margin": "10px"}),
                dcc.Graph(
                    figure=grafico_mensual(mensual),
                    id="figura_mensual",
                    style={"margin": "10px"},
                ),
                dcc.Graph(
                    figure=grafico_drawdown(evolucion),
                    id="figura_drawdown",
                    style={"margin": "10px"},
                ),
            ],
            id="seccion_rentabilidad",
        ),
        html.Div(
            children=[
                html.H2(
                    children=["Registro de operaciones"],
                    style={"margin": "10px"},
                ),
                html.Div(
                    children=[
                        dcc.Dropdown(
                            options=options_dropdown_activo,
                            placeholder="Todos los activos",
                            id="dropdown_activo",
                            style={
                                "display": "inline-block",
                                "width": "250px",
                                "margin": "5px 10px 5px 0px",
                                "vertical-align": "middle",
                            },
                        ),
                        dcc.Dropdown(
                            options=options_dropdown_tipo,
                            placeholder="Todos los tipos",
                            id="dropdown_tipo",
                            style={
                                "display": "inline-block",
                                "width": "200px",
                                "margin": "5px 10px 5px 0px",
                                "vertical-align": "middle",
                            },
                        ),
                        dcc.DatePickerRange(
                            min_date_allowed=operaciones["fecha"].min(),
                            max_date_allowed=operaciones["fecha"].max(),
                            start_date_placeholder_text="Desde",
                            end_date_placeholder_text="Hasta",
                            display_format="DD/MM/YYYY",
                            id="fechas_operaciones",
                            style={
                                "display": "inline-block",
                                "width": "320px",
                                "vertical-align": "middle",
                            },
                        ),
                    ],
                    style={"margin": "10px"},
                ),
                html.P(id="resumen_operaciones", style={"margin": "10px"}),
                html.Div(id="tabla_operaciones"),
            ],
            id="seccion_operaciones",
        ),
        html.Div(
            children=[
                html.H2(
                    children=["Ficha de activo"],
                    style={"margin": "10px"},
                ),
                dcc.Dropdown(
                    options=options_dropdown_ficha,
                    value=posiciones.loc[0, "isin"],
                    clearable=False,
                    id="dropdown_ficha",
                    style={"width": "250px", "margin": "10px"},
                ),
                html.P(id="nombre_ficha", style={"margin": "10px", "color": "gray"}),
                html.Div(id="datos_ficha"),
                dcc.Graph(id="figura_historico", style={"margin": "10px"}),
            ],
            id="seccion_ficha",
        ),
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
    Output("seccion_ficha", "style"),
    Output("boton_inicio", "style"),
    Output("boton_cartera", "style"),
    Output("boton_composicion", "style"),
    Output("boton_rentabilidad", "style"),
    Output("boton_operaciones", "style"),
    Output("boton_ficha", "style"),
    Input("boton_inicio", "n_clicks"),
    Input("boton_cartera", "n_clicks"),
    Input("boton_composicion", "n_clicks"),
    Input("boton_rentabilidad", "n_clicks"),
    Input("boton_operaciones", "n_clicks"),
    Input("boton_ficha", "n_clicks"),
)
def mostrar_seccion(
    n_inicio, n_cartera, n_composicion, n_rentabilidad, n_operaciones, n_ficha
):
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


@app.callback(
    Output("tabla_operaciones", "children"),
    Output("resumen_operaciones", "children"),
    Input("dropdown_activo", "value"),
    Input("dropdown_tipo", "value"),
    Input("fechas_operaciones", "start_date"),
    Input("fechas_operaciones", "end_date"),
)
def filtrar_operaciones(activo, tipo, inicio, fin):
    df = operaciones.copy()
    if activo:
        df = df[df["isin"] == activo]
    if tipo:
        df = df[df["tipo"] == tipo]
    if inicio:
        df = df[df["fecha"] >= inicio]
    if fin:
        df = df[df["fecha"] <= fin]
    df = df.sort_values("fecha", ascending=False).reset_index(drop=True)

    filas = []
    for i in range(len(df)):
        filas.append(
            [
                df.loc[i, "fecha"].strftime("%d/%m/%Y"),
                df.loc[i, "tipo"].capitalize(),
                nombres[df.loc[i, "isin"]],
                formato(df.loc[i, "titulos"], ""),
                formato(df.loc[i, "precio"]),
                formato(df.loc[i, "comision"]),
                formato(df.loc[i, "importe"]),
            ]
        )
    cabeceras = ["Fecha", "Tipo", "Activo", "Títulos", "Precio", "Comisión", "Importe"]
    resumen = (
        str(len(df)) + " operaciones | Importe total: " + formato(df["importe"].sum())
    )
    return tabla(cabeceras, filas), resumen


@app.callback(
    Output("pie_charts", "figure"),
    Output("pie_charts", "style"),
    Input("boton_composicion_mostrar", "n_clicks"),
    State("checklist_composicion", "value"),
)
def checklist_callback(n_clicks, checklist_value):
    if (checklist_value is None) or (checklist_value == []):
        return (go.Figure(data=[], layout={}), {"display": "none"})
    else:
        fig = grafico_composicion(posiciones, checklist_value)
        return (fig, {"display": "block", "margin": "10px"})


@app.callback(
    Output("figura_comparacion", "figure"),
    Input("dropdown_indice", "value"),
)
def comparar_indice(nombre):
    indice = precios_indices[precios_indices["ticker"] == indices[nombre]]
    return grafico_comparacion(evolucion, indice, nombre)


@app.callback(
    Output("figura_historico", "figure"),
    Output("figura_historico", "style"),
    Output("datos_ficha", "children"),
    Output("nombre_ficha", "children"),
    Input("dropdown_ficha", "value"),
)
def actualizar_ficha(isin):
    if isin:
        posicion = posiciones[posiciones["isin"] == isin].iloc[0]
        serie = precios[precios["ticker"] == posicion["ticker"]]
        ops = operaciones[operaciones["isin"] == isin]

        rentabilidad_anual = (
            serie["precio"].iloc[-1] / serie["precio"].iloc[-252] - 1
        ) * 100
        volatilidad_activo = serie["precio"].pct_change().std() * (252**0.5) * 100

        datos = [
            tarjeta("Precio actual", formato(posicion["precio_actual"])),
            tarjeta(
                "Variación del día",
                formato(posicion["variacion_dia"], " %"),
                color_signo(posicion["variacion_dia"]),
            ),
            tarjeta("Títulos", formato(posicion["titulos"], "")),
            tarjeta("Precio medio", formato(posicion["precio_medio"])),
            tarjeta("Valor", formato(posicion["valor"])),
            tarjeta(
                "Plusvalía",
                formato(posicion["plusvalia_pct"], " %"),
                color_signo(posicion["plusvalia_pct"]),
            ),
            tarjeta(
                "Rentabilidad 1 año",
                formato(rentabilidad_anual, " %"),
                color_signo(rentabilidad_anual),
            ),
            tarjeta("Volatilidad anual", formato(volatilidad_activo, " %")),
            tarjeta("Dividendos cobrados", formato(posicion["dividendos"])),
        ]
        nombre = (
            posicion["activo"]
            + " | "
            + posicion["clase"]
            + " | "
            + posicion["sector"]
            + " | "
            + posicion["region"]
            + " | ISIN "
            + isin
        )
        fig = grafico_historico(
            serie, ops, posicion["precio_medio"], posicion["nombre"]
        )
        return (fig, {"display": "block", "margin": "10px"}, datos, nombre)
    else:
        return (go.Figure(data=[], layout={}), {"display": "none"}, [], "")


if __name__ == "__main__":
    app.run(debug=True)
