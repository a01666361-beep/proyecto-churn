"""
Sección 02 · Factores relacionados con el abandono (3 gráficas de barras).
RESPONSABLE: Integrante 5

QUÉ FALTA (TODO):
- Revisar los rangos (cortes) de cada gráfica con los resultados del EDA.
- Escribir debajo de cada gráfica una frase de interpretación (st.caption).
"""
import plotly.graph_objects as go
import streamlit as st

from src.config import COLOR_BARRA, COLOR_REFERENCIA
from src.indicadores import tasa_por_rango


def grafica_tasa(tabla, titulo, eje_x, tasa_global):
    """Barras de tasa de churn por rango, con línea de la tasa global."""
    fig = go.Figure(
        go.Bar(
            x=tabla["rango"].astype(str),
            y=tabla["tasa"] * 100,
            marker_color=COLOR_BARRA,
            text=[f"{t:.1%}" for t in tabla["tasa"]],
            textposition="outside",
            customdata=tabla["clientes"],
            hovertemplate="%{x}<br>Churn: %{y:.1f}%<br>Clientes: %{customdata:,}<extra></extra>",
        )
    )
    fig.add_hline(
        y=tasa_global * 100, line_dash="dash", line_color=COLOR_REFERENCIA,
        annotation_text=f"Global {tasa_global:.1%}", annotation_position="top left",
    )
    fig.update_layout(
        title=titulo, height=330, margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=eje_x, yaxis_title="% de churn",
        yaxis=dict(range=[0, 100]), showlegend=False,
    )
    return fig


def mostrar(df, tasa_global):
    st.subheader("02 · Factores relacionados con el abandono")
    st.caption("La línea roja es la tasa de abandono global. Las barras arriba de ella son grupos con más riesgo.")

    if len(df) == 0:
        st.info("No hay clientes con esta combinación de filtros.")
        return

    c1, c2, c3 = st.columns(3)

    with c1:
        tabla = tasa_por_rango(
            df, "Customer_Service_Calls",
            cortes=[-1, 2, 5, 8, 11, 100],
            etiquetas=["0–2", "3–5", "6–8", "9–11", "12+"],
        )
        st.plotly_chart(grafica_tasa(tabla, "¿Más llamadas a servicio, más abandono?", "Llamadas", tasa_global))

    with c2:
        tabla = tasa_por_rango(
            df, "Cart_Abandonment_Rate",
            cortes=[-1, 30, 50, 71.25, 101],
            etiquetas=["≤30%", "30–50%", "50–71%", ">71%"],
        )
        st.plotly_chart(grafica_tasa(tabla, "¿Carrito abandonado alto, más abandono?", "Tasa de carrito abandonado", tasa_global))

    with c3:
        tabla = tasa_por_rango(
            df, "Dias_Sin_Comprar",
            cortes=[-1, 30, 60, 90, 180, 10_000],
            etiquetas=["0–30", "31–60", "61–90", "91–180", "180+"],
        )
        st.plotly_chart(grafica_tasa(tabla, "¿Más días sin comprar, más abandono?", "Días desde la última compra", tasa_global))
