from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


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
