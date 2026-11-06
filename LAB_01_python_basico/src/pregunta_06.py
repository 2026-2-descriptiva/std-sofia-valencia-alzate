import csv
import gzip


def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """
    with gzip.open("data/data.csv.gz", "rt", newline="") as archivo:
        filas = list(csv.reader(archivo, delimiter="\t"))

    minimos = {}
    maximos = {}
    for fila in filas:
        for par in fila[4].split(","):
            clave, valor = par.split(":")
            valor = int(valor)
            minimos[clave] = min(minimos.get(clave, valor), valor)
            maximos[clave] = max(maximos.get(clave, valor), valor)

    return [(clave, minimos[clave], maximos[clave]) for clave in sorted(minimos)]

