from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

url_yahoo = "https://query1.finance.yahoo.com/"
headers = {"User-Agent": "Mozilla/5.0"}

indices = {"MSCI World": "IWDA.AS", "S&P 500": "VUSA.AS", "IBEX 35": "^IBEX"}


def leer_tabla(path: Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el fichero: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, engine="openpyxl")
    raise ValueError(f"Formato no soportado: {suffix}")


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out.columns = [
        str(c).strip().lower().replace(" ", "_").replace(".", "_") for c in out.columns
    ]
    return out.reset_index(drop=True)


def validar_operaciones(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = normalize_columns(frame)
    work["fecha"] = pd.to_datetime(work["fecha"], errors="coerce")
    for col in ["titulos", "precio", "comision"]:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    work["comision"] = work["comision"].fillna(0)
    work["tipo"] = work["tipo"].astype("string").str.lower()
    work = work.drop_duplicates()
    ok = (
        work["fecha"].notna()
        & work["isin"].notna()
        & work["tipo"].isin(["compra", "venta", "dividendo"])
        & work["titulos"].notna()
        & (work["titulos"] > 0)
        & work["precio"].notna()
        & (work["precio"] > 0)
        & (work["comision"] >= 0)
    )
    validos = work.loc[ok].copy()
    errores = work.loc[~ok].copy()
    validos["importe"] = validos["titulos"] * validos["precio"]
    validos = validos.sort_values("fecha").reset_index(drop=True)
    return validos, errores


def buscar_ticker(isin: str) -> str:
    response = requests.get(
        url_yahoo + "v1/finance/search?q={}".format(isin), headers=headers
    )
    resultados = response.json()["quotes"]
    if len(resultados) == 0:
        raise ValueError(f"No se ha encontrado el activo: {isin}")
    return resultados[0]["symbol"]


def descargar_precios(ticker: str, periodo: str = "5y") -> pd.DataFrame:
    response = requests.get(
        url_yahoo + "v8/finance/chart/{}?range={}&interval=1d".format(ticker, periodo),
        headers=headers,
    )
    if response.status_code != 200:
        raise ValueError(f"No se han podido descargar los precios de {ticker}")
    datos = response.json()["chart"]["result"][0]

    precios = pd.DataFrame()
    precios["fecha"] = pd.to_datetime(datos["timestamp"], unit="s").normalize()
    precios["ticker"] = ticker
    precios["precio"] = pd.to_numeric(
        datos["indicators"]["quote"][0]["close"], errors="coerce"
    )
    precios["divisa"] = datos["meta"]["currency"]
    precios = precios.dropna().drop_duplicates(subset=["fecha"])
    return precios.reset_index(drop=True)


def descargar_precios_cartera(
    tickers: list, fichero: str = "precios.csv"
) -> pd.DataFrame:
    tablas = []
    for ticker in tickers:
        tablas.append(descargar_precios(ticker))
    precios = pd.concat(tablas, ignore_index=True)
    precios.to_csv(DATA_DIR / fichero, index=False)
    return precios


def calcular_posiciones(
    validos: pd.DataFrame, activos: pd.DataFrame, precios: pd.DataFrame
) -> pd.DataFrame:
    filas = []
    for i in range(len(activos)):
        isin = activos.loc[i, "isin"]
        ticker = activos.loc[i, "ticker"]
        ops = validos[validos["isin"] == isin]
        compras = ops[ops["tipo"] == "compra"]
        ventas = ops[ops["tipo"] == "venta"]
        dividendos = ops[ops["tipo"] == "dividendo"]

        titulos_comprados = compras["titulos"].sum()
        if titulos_comprados == 0:
            continue
        coste = compras["importe"].sum() + compras["comision"].sum()
        precio_medio = coste / titulos_comprados
        titulos = titulos_comprados - ventas["titulos"].sum()
        realizada = (
            ventas["importe"].sum()
            - ventas["comision"].sum()
            - ventas["titulos"].sum() * precio_medio
        )

        serie = precios[precios["ticker"] == ticker]
        precio_actual = serie["precio"].iloc[-1]
        precio_anterior = serie["precio"].iloc[-2]

        filas.append(
            {
                "isin": isin,
                "ticker": ticker,
                "nombre": activos.loc[i, "nombre"],
                "activo": activos.loc[i, "activo"],
                "clase": activos.loc[i, "clase"],
                "sector": activos.loc[i, "sector"],
                "region": activos.loc[i, "region"],
                "titulos": titulos,
                "precio_medio": precio_medio,
                "precio_actual": precio_actual,
                "variacion_dia": (precio_actual / precio_anterior - 1) * 100,
                "invertido": titulos * precio_medio,
                "valor": titulos * precio_actual,
                "plusvalia_realizada": realizada,
                "dividendos": dividendos["importe"].sum(),
            }
        )

    posiciones = pd.DataFrame(filas)
    posiciones = posiciones[posiciones["titulos"] > 0].reset_index(drop=True)
    posiciones["plusvalia"] = posiciones["valor"] - posiciones["invertido"]
    posiciones["plusvalia_pct"] = (
        posiciones["plusvalia"] / posiciones["invertido"] * 100
    )
    posiciones["peso"] = posiciones["valor"] / posiciones["valor"].sum() * 100
    return posiciones.sort_values("valor", ascending=False).reset_index(drop=True)


def calcular_evolucion(
    validos: pd.DataFrame, activos: pd.DataFrame, precios: pd.DataFrame
) -> pd.DataFrame:
    tabla = precios.pivot(index="fecha", columns="ticker", values="precio").ffill()
    tabla = tabla[tabla.index >= validos["fecha"].min()]

    valor = []
    aportado = []
    for fecha in tabla.index:
        hasta = validos[validos["fecha"] <= fecha]
        total = 0
        for i in range(len(activos)):
            ops = hasta[hasta["isin"] == activos.loc[i, "isin"]]
            titulos = (
                ops[ops["tipo"] == "compra"]["titulos"].sum()
                - ops[ops["tipo"] == "venta"]["titulos"].sum()
            )
            if titulos > 0:
                total = total + titulos * tabla.loc[fecha, activos.loc[i, "ticker"]]
        compras = hasta[hasta["tipo"] == "compra"]
        ventas = hasta[hasta["tipo"] == "venta"]
        valor.append(total)
        aportado.append(
            compras["importe"].sum()
            + compras["comision"].sum()
            - ventas["importe"].sum()
            + ventas["comision"].sum()
        )

    evolucion = pd.DataFrame()
    evolucion["fecha"] = tabla.index
    evolucion["valor"] = valor
    evolucion["aportado"] = aportado
    return evolucion


def calcular_rentabilidades(evolucion: pd.DataFrame) -> pd.DataFrame:
    df = evolucion.copy()
    rendimientos = [0.0]
    for i in range(1, len(df)):
        flujo = df.loc[i, "aportado"] - df.loc[i - 1, "aportado"]
        anterior = df.loc[i - 1, "valor"]
        if anterior > 0:
            rendimientos.append((df.loc[i, "valor"] - flujo) / anterior - 1)
        else:
            rendimientos.append(0.0)

    acumulado = 1
    maximo = 1
    rentabilidad = []
    drawdown = []
    for r in rendimientos:
        acumulado = acumulado * (1 + r)
        if acumulado > maximo:
            maximo = acumulado
        rentabilidad.append((acumulado - 1) * 100)
        drawdown.append((acumulado / maximo - 1) * 100)

    df["rendimiento"] = rendimientos
    df["rentabilidad"] = rentabilidad
    df["drawdown"] = drawdown
    return df


def rentabilidad_mensual(rentabilidades: pd.DataFrame) -> pd.DataFrame:
    df = rentabilidades.copy()
    df["mes"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m")
    filas = []
    for mes in df["mes"].unique():
        datos = df[df["mes"] == mes]
        acumulado = 1
        for r in datos["rendimiento"]:
            acumulado = acumulado * (1 + r)
        filas.append({"mes": mes, "rentabilidad": (acumulado - 1) * 100})
    return pd.DataFrame(filas)


def actualizar_datos(fichero: str = "operaciones_ejemplo.csv") -> None:
    operaciones = leer_tabla(DATA_DIR / fichero)
    validos, errores = validar_operaciones(operaciones)
    activos = normalize_columns(leer_tabla(DATA_DIR / "activos.csv"))
    precios = descargar_precios_cartera(activos["ticker"].tolist())
    descargar_precios_cartera(list(indices.values()), "indices.csv")
    posiciones = calcular_posiciones(validos, activos, precios)
    evolucion = calcular_evolucion(validos, activos, precios)
    rentabilidades = calcular_rentabilidades(evolucion)

    validos.to_csv(DATA_DIR / "operaciones_limpias.csv", index=False)
    posiciones.to_csv(DATA_DIR / "posiciones.csv", index=False)
    rentabilidades.to_csv(DATA_DIR / "evolucion.csv", index=False)
    print("operaciones válidas:", len(validos), "| errores:", len(errores))
    print("posiciones:", len(posiciones), "| días de evolución:", len(evolucion))


if __name__ == "__main__":
    actualizar_datos()
