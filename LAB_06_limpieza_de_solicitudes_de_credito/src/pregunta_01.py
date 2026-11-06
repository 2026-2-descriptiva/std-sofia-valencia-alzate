from pathlib import Path

import pandas as pd

COLUMNAS_DE_TEXTO = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "línea_credito",
]


def normalizar_texto(columna):
    return (
        columna.str.lower()
        .str.replace("-", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def normalizar_fecha(valor):
    primera, segunda, tercera = valor.split("/")
    if len(primera) == 4:
        anio, mes, dia = primera, segunda, tercera
    else:
        dia, mes, anio = primera, segunda, tercera
    return f"{int(anio):04d}-{int(mes):02d}-{int(dia):02d}"


def normalizar_monto(valor):
    texto = str(valor).replace("$", "").replace(" ", "").replace(",", "")
    if "." in texto:
        texto = texto.split(".")[0]
    return int(texto)


def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """
    df = pd.read_csv("data/solicitudes_de_credito.csv.gz", sep=";")
    df = df.drop(columns=["Unnamed: 0"])

    for columna in COLUMNAS_DE_TEXTO:
        df[columna] = normalizar_texto(df[columna])

    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].astype(str).apply(normalizar_fecha)
    df["monto_del_credito"] = df["monto_del_credito"].apply(normalizar_monto)
    df["comuna_ciudadano"] = df["comuna_ciudadano"].astype("Int64")

    columnas_obligatorias = [c for c in df.columns if c != "comuna_ciudadano"]
    df = df.dropna(subset=columnas_obligatorias).drop_duplicates()

    df = df[
        [
            "sexo",
            "tipo_de_emprendimiento",
            "idea_negocio",
            "barrio",
            "estrato",
            "comuna_ciudadano",
            "fecha_de_beneficio",
            "monto_del_credito",
            "línea_credito",
        ]
    ]

    Path("submission").mkdir(exist_ok=True)
    df.to_csv("submission/solicitudes_de_credito.csv", sep=";", index=False)
