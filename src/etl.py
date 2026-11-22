from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

url_yahoo = "https://query1.finance.yahoo.com/"
headers = {"User-Agent": "Mozilla/5.0"}


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


def descargar_precios_cartera(tickers: list) -> pd.DataFrame:
    tablas = []
    for ticker in tickers:
        tablas.append(descargar_precios(ticker))
    precios = pd.concat(tablas, ignore_index=True)
    precios.to_csv(DATA_DIR / "precios.csv", index=False)
    return precios
