import csv
import gzip
from collections import defaultdict


def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """
    with gzip.open("data/data.csv.gz", "rt", newline="") as archivo:
        filas = list(csv.reader(archivo, delimiter="\t"))

    letras_por_valor = defaultdict(set)
    for letra, valor, *_ in filas:
        letras_por_valor[int(valor)].add(letra)

    return [
        (valor, sorted(letras_por_valor[valor])) for valor in sorted(letras_por_valor)
    ]

