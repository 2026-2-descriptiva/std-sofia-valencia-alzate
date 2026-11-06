import csv
import gzip


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """
    with gzip.open("data/data.csv.gz", "rt", newline="") as archivo:
        filas = list(csv.reader(archivo, delimiter="\t"))

    maximos = {}
    minimos = {}
    for letra, valor, *_ in filas:
        valor = int(valor)
        maximos[letra] = max(maximos.get(letra, valor), valor)
        minimos[letra] = min(minimos.get(letra, valor), valor)

    return [(letra, maximos[letra], minimos[letra]) for letra in sorted(maximos)]
