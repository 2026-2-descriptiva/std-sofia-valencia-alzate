import csv
import gzip


def leer_registros():
    with gzip.open("data/data.csv.gz", "rt", newline="") as archivo:
        return list(csv.reader(archivo, delimiter="\t"))


def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo `data/data.csv.gz` y retorne el resultado como un número entero.

    Ejemplo del formato de la respuesta:

        214
    """
    registros = leer_registros()
    return sum(int(fila[1]) for fila in registros)

