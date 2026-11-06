import json
import re
from pathlib import Path

import pandas as pd

COLUMNAS_REQUERIDAS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]

PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalizar_encabezado(columna):
    return columna.strip().lower().replace(" ", "_")


def es_faltante(valor):
    return valor.strip() == "" or valor.strip() == "N/A"


def es_entero_positivo(valor):
    valor = valor.strip()
    return valor.isdigit() and int(valor) > 0


def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """
    df = pd.read_csv(
        "data/ventas.csv.gz", dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )
    df.columns = [normalizar_encabezado(columna) for columna in df.columns]

    columnas_presentes = set(df.columns)
    faltantes_requeridas = sorted(set(COLUMNAS_REQUERIDAS) - columnas_presentes)
    inesperadas = sorted(columnas_presentes - set(COLUMNAS_REQUERIDAS))

    tamanos_por_proveedor = df["supplier_id"].map(df.groupby("supplier_id").size())

    reporte = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "missing_required_columns": faltantes_requeridas,
        "unexpected_columns": inesperadas,
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_supplier_id_row_count": int((tamanos_por_proveedor > 1).sum()),
        "missing_value_count_by_column": {
            columna: int(df[columna].apply(es_faltante).sum()) for columna in df.columns
        },
        "invalid_email_count": int(
            df["contact_email"]
            .apply(lambda valor: not PATRON_EMAIL.match(valor.strip()))
            .sum()
        ),
        "invalid_unit_count": int(
            df["units"]
            .apply(lambda valor: not es_faltante(valor) and not es_entero_positivo(valor))
            .sum()
        ),
        "country_values": sorted(df["country"].unique().tolist()),
    }

    Path("submission").mkdir(exist_ok=True)
    Path("submission/data_quality_report.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return reporte
