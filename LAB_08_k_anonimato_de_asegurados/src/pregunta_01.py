import json
from pathlib import Path

import pandas as pd

K = 5

ESQUEMAS = {
    "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
    "without_children": ["age_group", "sex", "bmi_group", "region"],
}


def grupo_edad(edad):
    if edad < 30:
        return "18-29"
    if edad < 40:
        return "30-39"
    if edad < 50:
        return "40-49"
    return "50-64"


def grupo_bmi(bmi):
    if bmi < 18.5:
        return "bajo peso"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "sobrepeso"
    return "obesidad"


def grupo_hijos(hijos):
    if hijos == 0:
        return "0"
    if hijos <= 2:
        return "1-2"
    return "3+"


def evaluar_esquema(df, cuasi_identificadores):
    tamanos_por_clase = df.groupby(cuasi_identificadores).size()
    tamanos_por_fila = df.set_index(cuasi_identificadores).index.map(tamanos_por_clase)

    publicado = tamanos_por_fila >= K
    df_publicado = df[publicado]
    tamanos_publicados = df_publicado.groupby(cuasi_identificadores).size()

    fumadores_distintos = df_publicado.groupby(cuasi_identificadores)["smoker"].nunique()
    clases_sin_diversidad = fumadores_distintos[fumadores_distintos == 1].index

    reporte = {
        "quasi_identifiers": cuasi_identificadores,
        "equivalence_classes": int(len(tamanos_por_clase)),
        "k_before_suppression": int(tamanos_por_clase.min()),
        "suppressed_records": int((~publicado).sum()),
        "published_records": int(publicado.sum()),
        "published_classes": int((tamanos_por_clase >= K).sum()),
        "classes_without_smoker_diversity": int(len(clases_sin_diversidad)),
        "records_without_smoker_diversity": int(
            tamanos_publicados.loc[clases_sin_diversidad].sum()
        ),
    }
    return reporte, df_publicado


def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """
    df = pd.read_csv("data/insurance.csv.gz")
    df["age_group"] = df["age"].apply(grupo_edad)
    df["bmi_group"] = df["bmi"].apply(grupo_bmi)
    df["children_group"] = df["children"].apply(grupo_hijos)

    cuasi_originales = ["age", "sex", "bmi", "children", "region"]
    tamanos_originales = df.groupby(cuasi_originales).size()
    tamanos_por_fila_original = df.set_index(cuasi_originales).index.map(
        tamanos_originales
    )

    esquemas_evaluados = {}
    publicados_por_esquema = {}
    for nombre, cuasi in ESQUEMAS.items():
        esquemas_evaluados[nombre], publicados_por_esquema[nombre] = evaluar_esquema(
            df, cuasi
        )

    esquema_elegido = min(
        esquemas_evaluados, key=lambda n: esquemas_evaluados[n]["suppressed_records"]
    )
    df_publicado = publicados_por_esquema[esquema_elegido]

    reporte = {
        "original_k": int(tamanos_originales.min()),
        "original_unique_records": int((tamanos_por_fila_original == 1).sum()),
        "schemes": esquemas_evaluados,
        "selected_scheme": esquema_elegido,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(df_publicado["charges"].mean()),
        "smoker_rate_original": float((df["smoker"] == "yes").mean()),
        "smoker_rate_published": float((df_publicado["smoker"] == "yes").mean()),
    }

    Path("submission").mkdir(exist_ok=True)
    Path("submission/privacy_report.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    columnas_publicadas = ESQUEMAS[esquema_elegido] + ["smoker", "charges"]
    df_publicado[columnas_publicadas].to_csv(
        "submission/insurance_published.csv", index=False
    )

    return reporte
