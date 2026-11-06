import csv
import gzip
from collections import defaultdict


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
    with gzip.open("data/data.csv.gz", "rt", newline="") as archivo:
        filas = list(csv.reader(archivo, delimiter="\t"))

    sumas = defaultdict(int)
    for letra, _, _, _, metrics in filas:
        for par in metrics.split(","):
            _, valor = par.split(":")
            sumas[letra] += int(valor)

    return dict(sorted(sumas.items()))

