import csv
import gzip
from collections import defaultdict


def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """
    with gzip.open("data/data.csv.gz", "rt", newline="") as archivo:
        filas = list(csv.reader(archivo, delimiter="\t"))

    sumas = defaultdict(int)
    for _, valor, _, codes, _ in filas:
        valor = int(valor)
        for codigo in codes.split(","):
            sumas[codigo] += valor

    return dict(sorted(sumas.items()))

