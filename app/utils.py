#Libreria para funciones auxiliares

import logging
import pandas as pd

log = logging.getLogger(__name__)

#Las columnas necesarias que están en CSV
REQUIRED_COLS = ["product_id", "title", "price", "store_id"]

def read_csv(path: str):
    try:
        df = pd.read_csv(path, dtype=str)
    except Exception:
        log.exception("Error reading CSV: %s", path)
        raise

    missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    #Eliminar filas del CSV donde falta información
    df = df.dropna(how='any')

    # Normalizar datos CSV
    df["product_id"] = df["product_id"].astype(int)
    df["title"] = df["title"].astype(str).str.strip()
    df["price"] = df["price"].astype(float)
    df["store_id"] = df["store_id"].astype(str).str.strip()
    return df


#Ver los casos donde un producto tiene varios store_id. Si tiene varios, creamos x filas.
def split_stores(df: pd.DataFrame):
    rows = []
    for _, r in df.iterrows():
        for sid in (str(r["store_id"]).split("|")):
            if sid:
                rows.append({
                    "product_id": int(r["product_id"]),
                    "title": str(r["title"]).strip(),
                    "price": float(r["price"]),
                    "store_id": int(sid),
                })
    return pd.DataFrame(rows, columns=["product_id", "title", "price", "store_id"])