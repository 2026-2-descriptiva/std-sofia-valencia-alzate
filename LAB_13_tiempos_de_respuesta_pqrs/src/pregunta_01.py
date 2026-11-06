from pathlib import Path

import numpy as np
import pandas as pd

ORDEN_DIAS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
PLAZO_EN_DIAS_HABILES = 15


def leer_canal(archivo, nombre_canal):
    df = pd.read_csv(archivo).drop_duplicates()
    df["channel"] = nombre_canal
    return df


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """
    df = pd.concat(
        [
            leer_canal("data/historical_requests_web.csv.gz", "web"),
            leer_canal("data/historical_requests_letter.csv.gz", "letter"),
        ],
        ignore_index=True,
    )

    df["in_date"] = pd.to_datetime(df["in_date"])
    df["out_date"] = pd.to_datetime(df["out_date"])
    respondida = df["out_date"].notna()

    primer_dia_habil = (df["in_date"] + pd.Timedelta(days=1)).values.astype(
        "datetime64[D]"
    )
    ultimo_dia_habil = (df["out_date"] + pd.Timedelta(days=1)).values.astype(
        "datetime64[D]"
    )
    df["business_days"] = np.nan
    df.loc[respondida, "business_days"] = np.busday_count(
        primer_dia_habil[respondida.values], ultimo_dia_habil[respondida.values]
    )
    df["calendar_days"] = (df["out_date"] - df["in_date"]).dt.days
    df["on_time"] = respondida & (df["business_days"] <= PLAZO_EN_DIAS_HABILES)
    df["year"] = df["in_date"].dt.year

    channel_summary = (
        df.groupby("channel")
        .agg(requests=("channel", "size"), answered=("out_date", "count"))
        .reset_index()
    )
    channel_summary["pending"] = (
        channel_summary["requests"] - channel_summary["answered"]
    )
    mediana_por_canal = df.loc[respondida].groupby("channel")["business_days"].median()
    channel_summary["median_business_days"] = channel_summary["channel"].map(
        mediana_por_canal
    )
    channel_summary["on_time_rate"] = channel_summary["channel"].map(
        df.groupby("channel")["on_time"].mean()
    )
    channel_summary = channel_summary.sort_values("channel").reset_index(drop=True)

    yearly_summary = (
        df.groupby(["year", "channel"])
        .agg(
            requests=("channel", "size"),
            pending=("out_date", lambda serie: serie.isna().sum()),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )

    entry_day_summary = (
        df.groupby("day_name")
        .agg(
            requests=("day_name", "size"),
            median_calendar_days=(
                "calendar_days",
                lambda serie: serie[respondida.loc[serie.index]].median(),
            ),
            median_business_days=("business_days", "median"),
        )
        .reindex(ORDEN_DIAS)
        .reset_index()
    )

    Path("submission").mkdir(exist_ok=True)
    channel_summary.to_csv("submission/channel_summary.csv", index=False)
    yearly_summary.to_csv("submission/yearly_summary.csv", index=False)
    entry_day_summary.to_csv("submission/entry_day_summary.csv", index=False)

    return channel_summary, yearly_summary, entry_day_summary
