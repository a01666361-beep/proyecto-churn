"""
Variables relacionadas con el KPI 1 (tasa de abandono): 3 gráficas compactas
en una sola figura. La línea punteada es la tasa global.
RESPONSABLE: Integrante 5

QUÉ FALTA (TODO):
- Revisar los rangos de cada variable (están en src/config.py → RANGOS).
"""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config import AZUL, AZUL_CLARO, ROJO
from src.indicadores import tasa_por_rango

VARIABLES = [
    ("Customer_Service_Calls", "Llamadas a servicio"),
    ("Cart_Abandonment_Rate", "Carrito abandonado"),
    ("Dias_Sin_Comprar", "Días sin comprar"),
]


def figura_factores(df, tasa_global, alto=236):
    fig = make_subplots(rows=1, cols=3, subplot_titles=[t for _, t in VARIABLES],
                        horizontal_spacing=0.05, shared_yaxes=True)
    for i, (columna, _) in enumerate(VARIABLES, start=1):
        tabla = tasa_por_rango(df, columna)
        colores = [AZUL if t > tasa_global else AZUL_CLARO for t in tabla["tasa"]]
        fig.add_trace(
            go.Bar(
                x=tabla["rango"].astype(str), y=tabla["tasa"] * 100,
                marker_color=colores,
                text=[f"{t:.0%}" for t in tabla["tasa"]], textposition="outside",
                textfont_size=10, cliponaxis=False,
                customdata=tabla["clientes"],
                hovertemplate="%{x}<br>Churn: %{y:.1f}%<br>Clientes: %{customdata:,}<extra></extra>",
            ),
            row=1, col=i,
        )
        fig.add_hline(y=tasa_global * 100, line_dash="dot", line_color=ROJO, line_width=1.5, row=1, col=i)

    fig.update_yaxes(range=[0, 85], ticksuffix="%", tickfont_size=10, gridcolor="rgba(128,128,128,0.15)")
    fig.update_xaxes(tickfont_size=10)
    fig.update_annotations(font_size=12)
    fig.update_layout(height=alto, margin=dict(l=0, r=0, t=24, b=0), showlegend=False,
                      bargap=0.25, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def mostrar(df, tasa_global):
    if len(df) == 0:
        st.info("No hay clientes con esta combinación de filtros.")
        return
    st.plotly_chart(figura_factores(df, tasa_global), config={"displayModeBar": False})
