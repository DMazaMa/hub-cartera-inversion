from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src.etl import DATA_DIR

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

ventana = 21
features = ["rendimiento", "vol_5", "vol_21", "vol_63"]


def crear_variables(serie: pd.DataFrame) -> pd.DataFrame:
    df = serie.copy().reset_index(drop=True)
    df["rendimiento"] = df["precio"].pct_change() * 100
    df["vol_5"] = df["rendimiento"].rolling(5).std() * (252**0.5)
    df["vol_21"] = df["rendimiento"].rolling(21).std() * (252**0.5)
    df["vol_63"] = df["rendimiento"].rolling(63).std() * (252**0.5)
    df["vol_futura"] = df["vol_21"].shift(-ventana)
    return df


def regression_report(y_true, y_hat, label: str) -> dict:
    mse = float(mean_squared_error(y_true, y_hat))
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_true, y_hat))
    r2 = float(r2_score(y_true, y_hat))
    print(f"[{label}] MSE={mse:.4f} | RMSE={rmse:.4f} | MAE={mae:.4f} | R²={r2:.4f}")
    return {"mse": mse, "rmse": rmse, "mae": mae, "r2": r2}


def entrenar_modelo(serie: pd.DataFrame, ticker: str) -> dict:
    df = crear_variables(serie).dropna().reset_index(drop=True)
    X = df[features]
    y = df["vol_futura"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, shuffle=False
    )

    reg = ElasticNet(random_state=123)
    reg.fit(X_train, y_train)
    pred_train = reg.predict(X_train)
    pred_test = reg.predict(X_test)

    regression_report(y_train, pred_train, ticker + " train")
    metricas = regression_report(y_test, pred_test, ticker + " test")
    metricas["mae_ingenuo"] = float(mean_absolute_error(y_test, X_test["vol_21"]))
    metricas["ticker"] = ticker
    metricas["inicio_test"] = df.loc[len(X_train), "fecha"]

    joblib.dump(reg, MODELS_DIR / (ticker + ".joblib"))
    return metricas


def entrenar_modelos(fichero: str = "precios.csv") -> pd.DataFrame:
    precios = pd.read_csv(DATA_DIR / fichero)
    filas = []
    for ticker in precios["ticker"].unique():
        filas.append(entrenar_modelo(precios[precios["ticker"] == ticker], ticker))
    metricas = pd.DataFrame(filas)
    metricas.to_csv(DATA_DIR / "metricas_modelos.csv", index=False)
    return metricas


def predecir_volatilidad(serie: pd.DataFrame, ticker: str) -> pd.DataFrame:
    reg = joblib.load(MODELS_DIR / (ticker + ".joblib"))
    df = crear_variables(serie).dropna(subset=features).reset_index(drop=True)
    df["prediccion"] = reg.predict(df[features])
    return df


if __name__ == "__main__":
    entrenar_modelos()
