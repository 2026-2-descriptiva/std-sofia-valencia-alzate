import re

import pandas as pd

PATRON_REGISTRO = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+,\d+)\s*%\s*(.*)$")


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """
    with open("data/clusters_report.txt", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    inicio_datos = (
        next(i for i, linea in enumerate(lineas) if linea.strip().startswith("---")) + 1
    )

    registros = []
    fragmentos_por_registro = []
    for linea in lineas[inicio_datos:]:
        if not linea.strip():
            continue

        coincidencia = PATRON_REGISTRO.match(linea)
        if coincidencia:
            cluster, cantidad, porcentaje, resto = coincidencia.groups()
            registros.append(
                [int(cluster), int(cantidad), float(porcentaje.replace(",", "."))]
            )
            fragmentos_por_registro.append([resto])
        else:
            fragmentos_por_registro[-1].append(linea)

    palabras_clave = []
    for fragmentos in fragmentos_por_registro:
        texto = re.sub(r"\s+", " ", " ".join(fragmentos)).strip().rstrip(".")
        palabras = [palabra.strip() for palabra in texto.split(",")]
        palabras_clave.append(", ".join(palabras))

    df = pd.DataFrame(
        registros,
        columns=[
            "cluster",
            "cantidad_de_palabras_clave",
            "porcentaje_de_palabras_clave",
        ],
    )
    df["principales_palabras_clave"] = palabras_clave
    return df
