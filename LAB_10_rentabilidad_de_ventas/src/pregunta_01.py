from pathlib import Path

import pandas as pd

BANDAS_DE_DESCUENTO = ["0%", "1%-5%", "6%-10%", "más de 10%"]


def banda_de_descuento(descuento):
    if descuento == 0:
        return "0%"
    if descuento <= 0.05:
        return "1%-5%"
    if descuento <= 0.10:
        return "6%-10%"
    return "más de 10%"


def resumir(grupo):
    con_perdida = grupo["Profit"] < 0
    return {
        "lines": len(grupo),
        "sales": grupo["Sales"].sum(),
        "profit": grupo["Profit"].sum(),
        "profit_margin": grupo["Profit"].sum() / grupo["Sales"].sum(),
        "loss_line_rate": con_perdida.mean(),
        "lost_profit": -grupo.loc[con_perdida, "Profit"].sum(),
    }


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """
    df = pd.read_csv("data/superstore_orders.csv.gz", sep=";", decimal=",")
    con_perdida = df["Profit"] < 0

    resumen_general = resumir(df)
    profitability_summary = pd.DataFrame(
        [
            {
                "lines": resumen_general["lines"],
                "orders": df["Order ID"].nunique(),
                "sales": resumen_general["sales"],
                "profit": resumen_general["profit"],
                "profit_margin": resumen_general["profit_margin"],
                "loss_lines": int(con_perdida.sum()),
                "loss_line_rate": resumen_general["loss_line_rate"],
                "lost_profit": resumen_general["lost_profit"],
            }
        ]
    )

    df["discount_band"] = df["Discount"].apply(banda_de_descuento)
    discount_summary = pd.DataFrame(
        [
            {"discount_band": banda, **resumir(grupo)}
            for banda, grupo in (
                (banda, df[df["discount_band"] == banda]) for banda in BANDAS_DE_DESCUENTO
            )
        ]
    )

    filas_segmentos = []
    for (segmento, categoria), grupo in df.groupby(["Customer Segment", "Product Category"]):
        if len(grupo) < 100:
            continue
        resumen_grupo = resumir(grupo)
        filas_segmentos.append(
            {
                "Customer Segment": segmento,
                "Product Category": categoria,
                "lines": resumen_grupo["lines"],
                "sales": resumen_grupo["sales"],
                "profit": resumen_grupo["profit"],
                "profit_margin": resumen_grupo["profit_margin"],
                "lost_profit": resumen_grupo["lost_profit"],
            }
        )
    priority_segments = (
        pd.DataFrame(filas_segmentos)
        .sort_values("lost_profit", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )

    Path("submission").mkdir(exist_ok=True)
    profitability_summary.to_csv("submission/profitability_summary.csv", index=False)
    discount_summary.to_csv("submission/discount_summary.csv", index=False)
    priority_segments.to_csv("submission/priority_segments.csv", index=False)

    return profitability_summary, discount_summary, priority_segments
