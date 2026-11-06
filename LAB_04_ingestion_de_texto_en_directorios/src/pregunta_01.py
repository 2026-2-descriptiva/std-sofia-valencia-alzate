from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
SUBMISSION_DIR = Path("submission")
SENTIMIENTOS = ["negative", "neutral", "positive"]


def construir_dataset(division):
    filas = []
    for sentimiento in SENTIMIENTOS:
        carpeta = DATA_DIR / division / sentimiento
        for archivo in sorted(carpeta.glob("*.txt")):
            frase = archivo.read_text(encoding="utf-8").strip()
            filas.append({"phrase": frase, "target": sentimiento})
    return pd.DataFrame(filas, columns=["phrase", "target"])


def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """
    SUBMISSION_DIR.mkdir(exist_ok=True)
    for division in ["train", "test"]:
        dataset = construir_dataset(division)
        dataset.to_csv(SUBMISSION_DIR / f"{division}_dataset.csv", index=False)
