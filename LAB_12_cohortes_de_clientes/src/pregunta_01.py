from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """
    df = pd.read_csv("data/sales.csv.gz")
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    order_month = df["OrderDate"].dt.to_period("M")

    primera_compra = order_month.groupby(df["CustomerID"]).min()
    cohort_month = df["CustomerID"].map(primera_compra)
    period_index = (order_month - cohort_month).apply(lambda diferencia: diferencia.n)

    cohort_retention = (
        pd.DataFrame({"cohort_month": cohort_month, "period_index": period_index})
        .assign(CustomerID=df["CustomerID"])
        .groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .reset_index(name="active_customers")
    )

    tamanos_de_cohorte = cohort_retention.loc[
        cohort_retention["period_index"] == 0
    ].set_index("cohort_month")["active_customers"]
    cohort_retention["cohort_size"] = cohort_retention["cohort_month"].map(
        tamanos_de_cohorte
    )
    cohort_retention["retention_rate"] = (
        cohort_retention["active_customers"] / cohort_retention["cohort_size"]
    )
    cohort_retention["cohort_month"] = cohort_retention["cohort_month"].astype(str)
    cohort_retention = cohort_retention.sort_values(
        ["cohort_month", "period_index"]
    ).reset_index(drop=True)

    Path("submission").mkdir(exist_ok=True)
    cohort_retention.to_csv("submission/cohort_retention.csv", index=False)

    tabla_calor = cohort_retention.pivot(
        index="cohort_month", columns="period_index", values="retention_rate"
    )

    figura, eje = plt.subplots(figsize=(10, 6))
    imagen = eje.imshow(tabla_calor * 100, cmap="YlGnBu", aspect="auto")
    eje.set_xticks(range(len(tabla_calor.columns)))
    eje.set_xticklabels(tabla_calor.columns)
    eje.set_yticks(range(len(tabla_calor.index)))
    eje.set_yticklabels(tabla_calor.index)
    eje.set_xlabel("period_index")
    eje.set_ylabel("cohort_month")
    eje.set_title("Retención de clientes por cohorte (%)")
    figura.colorbar(imagen, ax=eje, label="retention_rate (%)")

    for fila, cohorte in enumerate(tabla_calor.index):
        for columna, periodo in enumerate(tabla_calor.columns):
            valor = tabla_calor.loc[cohorte, periodo]
            if pd.notna(valor):
                eje.text(
                    columna,
                    fila,
                    f"{valor * 100:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                )

    figura.tight_layout()
    figura.savefig("submission/cohort_retention_heatmap.png")
    plt.close(figura)

    return cohort_retention
