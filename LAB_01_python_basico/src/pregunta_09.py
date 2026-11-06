import csv
import gzip
from collections import Counter


def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """
    with gzip.open("data/data.csv.gz", "rt", newline="") as archivo:
        filas = list(csv.reader(archivo, delimiter="\t"))

    conteo = Counter()
    for fila in filas:
        for par in fila[4].split(","):
            clave, _ = par.split(":")
            conteo[clave] += 1

    return dict(sorted(conteo.items()))

