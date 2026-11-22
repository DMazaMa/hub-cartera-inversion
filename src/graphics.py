import pandas as pd
import plotly.graph_objects as go


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
