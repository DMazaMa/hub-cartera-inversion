import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

colores_pie = [
    "midnightblue",
    "steelblue",
    "lightsteelblue",
    "darkorange",
    "gold",
    "mediumseagreen",
    "firebrick",
    "gray",
]


def grafico_evolucion(evolucion: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=evolucion["fecha"],
            y=evolucion["valor"],
            mode="lines",
            line=dict(color="steelblue", width=2),
            fill="tozeroy",
            name="Valor de la cartera",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=evolucion["fecha"],
            y=evolucion["aportado"],
            mode="lines",
            line=dict(color="darkorange", dash="dash"),
            name="Capital aportado",
        )
    )
    fig.update_layout(
        title="Valor de la cartera frente al capital aportado",
        yaxis_title="Euros",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def grafico_plusvalias(posiciones: pd.DataFrame) -> go.Figure:
    df = posiciones.sort_values("plusvalia_pct")
    colores = []
    for valor in df["plusvalia_pct"]:
        if valor >= 0:
            colores.append("mediumseagreen")
        else:
            colores.append("firebrick")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["plusvalia_pct"],
            y=df["nombre"],
            orientation="h",
            marker_color=colores,
            text=df["plusvalia_pct"].round(1).astype(str) + " %",
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Rentabilidad de cada posición",
        xaxis_title="Plusvalía (%)",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def grafico_pesos(posiciones: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=posiciones["nombre"],
            values=posiciones["valor"],
            textinfo="label+percent",
            textposition="inside",
            hole=0.5,
            sort=False,
            showlegend=False,
            marker=dict(colors=colores_pie),
        )
    )
    fig.update_layout(
        title="Peso de cada posición", margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig


def grafico_composicion(posiciones: pd.DataFrame, columnas: list) -> go.Figure:
    titulos = {"clase": "Clase de activo", "sector": "Sector", "region": "Región"}
    nombres_columnas = []
    for col in columnas:
        nombres_columnas.append(titulos[col])

    fig = make_subplots(
        rows=1,
        cols=len(columnas),
        specs=[[{"type": "domain"}] * len(columnas)],
        subplot_titles=nombres_columnas,
    )
    for col in columnas:
        reparto = posiciones.groupby(col, as_index=False)["valor"].sum()
        fig.add_trace(
            go.Pie(
                labels=reparto[col],
                values=reparto["valor"],
                textinfo="label+percent",
                insidetextorientation="radial",
                textposition="inside",
                sort=False,
                showlegend=False,
                hole=0.5,
                name=titulos[col],
                marker=dict(colors=colores_pie),
            ),
            row=1,
            col=columnas.index(col) + 1,
        )
    fig.update_traces(textfont_size=12)
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig


def grafico_comparacion(
    rentabilidades: pd.DataFrame, indice: pd.DataFrame, nombre: str
) -> go.Figure:
    inicio = rentabilidades["fecha"].min()
    serie = indice[indice["fecha"] >= inicio]
    base = serie["precio"].iloc[0]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=rentabilidades["fecha"],
            y=rentabilidades["rentabilidad"],
            mode="lines",
            line=dict(color="steelblue", width=2),
            name="Mi cartera",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=serie["fecha"],
            y=(serie["precio"] / base - 1) * 100,
            mode="lines",
            line=dict(color="darkorange"),
            name=nombre,
        )
    )
    fig.update_layout(
        title="Rentabilidad acumulada frente a " + nombre,
        yaxis_title="Rentabilidad (%)",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def grafico_mensual(mensual: pd.DataFrame) -> go.Figure:
    colores = []
    for valor in mensual["rentabilidad"]:
        if valor >= 0:
            colores.append("mediumseagreen")
        else:
            colores.append("firebrick")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=mensual["mes"], y=mensual["rentabilidad"], marker_color=colores)
    )
    fig.update_layout(
        title="Rentabilidad mensual",
        yaxis_title="Rentabilidad (%)",
        plot_bgcolor="white",
        bargap=0.1,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def grafico_drawdown(rentabilidades: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=rentabilidades["fecha"],
            y=rentabilidades["drawdown"],
            mode="lines",
            line=dict(color="firebrick"),
            fill="tozeroy",
            name="Drawdown",
        )
    )
    fig.update_layout(
        title="Caída desde máximos (drawdown)",
        yaxis_title="Caída (%)",
        plot_bgcolor="white",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def grafico_historico(
    serie: pd.DataFrame, ops: pd.DataFrame, precio_medio: float, nombre: str
) -> go.Figure:
    compras = ops[ops["tipo"] == "compra"]
    ventas = ops[ops["tipo"] == "venta"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=serie["fecha"],
            y=serie["precio"],
            mode="lines",
            line=dict(color="steelblue", width=2),
            name="Precio",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[serie["fecha"].iloc[0], serie["fecha"].iloc[-1]],
            y=[precio_medio, precio_medio],
            mode="lines",
            line=dict(color="darkorange", dash="dash"),
            name="Precio medio",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=compras["fecha"],
            y=compras["precio"],
            mode="markers",
            marker=dict(color="mediumseagreen", size=9, symbol="triangle-up"),
            name="Compras",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ventas["fecha"],
            y=ventas["precio"],
            mode="markers",
            marker=dict(color="firebrick", size=9, symbol="triangle-down"),
            name="Ventas",
        )
    )
    fig.update_layout(
        title="Histórico de precios de " + nombre,
        yaxis_title="Precio (€)",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def grafico_volatilidad(prediccion: pd.DataFrame, nombre: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=prediccion["fecha"],
            y=prediccion["vol_futura"],
            mode="lines",
            line=dict(color="steelblue", width=2),
            name="Volatilidad real del mes siguiente",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=prediccion["fecha"],
            y=prediccion["prediccion"],
            mode="lines",
            line=dict(color="darkorange", dash="dash"),
            name="Predicción del modelo",
        )
    )
    fig.update_layout(
        title="Volatilidad prevista de " + nombre + " (periodo de test)",
        yaxis_title="Volatilidad anual (%)",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.15),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def grafico_grupos(grupos: pd.DataFrame) -> go.Figure:
    colores = {
        "Riesgo bajo": "mediumseagreen",
        "Riesgo medio": "darkorange",
        "Riesgo alto": "firebrick",
    }
    fig = go.Figure()
    for perfil in colores.keys():
        df = grupos[grupos["perfil"] == perfil]
        fig.add_trace(
            go.Scatter(
                x=df["volatilidad"],
                y=df["rentabilidad"],
                mode="markers+text",
                text=df["nombre"],
                textposition="top center",
                marker=dict(color=colores[perfil], size=14),
                name=perfil,
            )
        )
    fig.update_layout(
        title="Grupos de riesgo de las posiciones (K-Means)",
        xaxis_title="Volatilidad anual (%)",
        yaxis_title="Rentabilidad anual media (%)",
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


def grafico_codo(codo: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=codo["k"],
            y=codo["distortion"],
            mode="lines+markers",
            line=dict(color="steelblue"),
            marker=dict(symbol="x", size=10),
        )
    )
    fig.update_layout(
        title="Método del codo: búsqueda de k",
        xaxis_title="k",
        xaxis=dict(dtick=1),
        yaxis_title="Inercia (distortion)",
        plot_bgcolor="white",
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig
