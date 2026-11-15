"""ETL de ejemplo para la clase de Docker.

Lee ventas crudas (CSV), limpia, agrega por día y sucursal y:
  1. escribe el resultado en Parquet (OUTPUT_DIR)
  2. si hay DB_URL, lo carga en Postgres (tabla ventas_diarias)

Toda la configuración llega por variables de entorno, así la misma imagen
sirve en tu laptop, en CI y en producción.
"""

import logging
import os
import platform
import sys
from pathlib import Path

import pandas as pd

INPUT_PATH = Path(os.getenv("INPUT_PATH", "data/raw/ventas.csv"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data/output"))
DB_URL = os.getenv("DB_URL")  # ej: postgresql+psycopg://etl:etl@db:5432/ventas
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("etl")


def extract(path: Path) -> pd.DataFrame:
    log.info("Leyendo %s", path)
    return pd.read_csv(path)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    filas_iniciales = len(df)
    df = (
        df.drop_duplicates()
        .assign(
            sucursal=lambda d: d["sucursal"].str.strip().str.title(),
            fecha=lambda d: pd.to_datetime(d["fecha"]).dt.date,
        )
        .dropna(subset=["cantidad"])
        .astype({"cantidad": "int64"})
    )
    df["importe"] = df["cantidad"] * df["precio_unitario"]
    log.info("Limpieza: %s -> %s filas", filas_iniciales, len(df))

    diario = (
        df.groupby(["fecha", "sucursal"], as_index=False)
        .agg(ordenes=("order_id", "nunique"), unidades=("cantidad", "sum"), importe=("importe", "sum"))
        .sort_values(["fecha", "sucursal"])
    )
    log.info("Agregado: %s filas (día x sucursal)", len(diario))
    return diario


def load_parquet(df: pd.DataFrame, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    destino = output_dir / "ventas_diarias.parquet"
    df.to_parquet(destino, index=False)
    log.info("Parquet escrito en %s", destino)
    return destino


def load_postgres(df: pd.DataFrame, db_url: str) -> None:
    from sqlalchemy import create_engine

    engine = create_engine(db_url)
    df.to_sql("ventas_diarias", engine, if_exists="replace", index=False)
    log.info("Cargadas %s filas en la tabla ventas_diarias", len(df))


def main() -> None:
    log.info("Python %s en %s (%s)", platform.python_version(), platform.system(), platform.node())
    df = transform(extract(INPUT_PATH))
    load_parquet(df, OUTPUT_DIR)
    if DB_URL:
        load_postgres(df, DB_URL)
    else:
        log.info("DB_URL no definida: no se carga en la base")
    log.info("ETL terminado OK")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("El ETL falló")
        sys.exit(1)
