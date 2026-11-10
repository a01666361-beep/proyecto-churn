"""
Variables relacionadas con el KPI 2 (perfil de riesgo):
- Mapa de calor: churn por carrito abandonado × llamadas (de dónde sale la regla).
- Barras: % de activos en perfil de riesgo por país, contra la meta.
RESPONSABLE: Integrante 6

QUÉ FALTA (TODO):
- Semana siguiente: opción de usar el modelo Gradient Boosting (probabilidad ≥ 0.44)
  en lugar de la regla.
"""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config import AZUL, AZUL_PALIDO, META_RIESGO, ROJO, VERDE
from src.indicadores import mapa_carrito_llamadas, riesgo_por_pais


def figura_riesgo(df, regla, alto=260):
    tasa, conteo = mapa_carrito_llamadas(df)
    pais = riesgo_por_pais(df, regla)

    fig = make_subplots(rows=1, cols=2, column_widths=[0.58, 0.42], horizontal_spacing=0.12,
                        subplot_titles=["¿Qué combinaciones concentran más abandono?", "Activos en riesgo por país"])

    z = tasa * 100
    texto = [[("Sin datos" if v != v else f"{v:.1f}%") for v in fila] for fila in z.values]
    fig.add_trace(
        go.Heatmap(
            z=z.values, x=[str(c) for c in z.columns],
            y=[str(i).replace("50–71%", "50–71.25%").replace(">71%", ">71.25%") for i in z.index],
            text=texto, texttemplate="%{text}", textfont_size=10,
            customdata=conteo.values,
            colorscale=[[0, VERDE], [0.5, AZUL_PALIDO], [1, ROJO]], zmin=0, zmax=100,
            showscale=False,
            hoverongaps=False,
            hovertemplate="Carrito %{y} · %{x} llamadas<br>Abandono: %{z:.1f}%<br>Clientes: %{customdata:,}<extra></extra>",
        ),
        row=1, col=1,
    )
    fig.update_xaxes(title_text="Llamadas a servicio", title_font_size=10, tickfont_size=10, row=1, col=1)
    fig.update_yaxes(title_text="Carrito (%)", title_font_size=10, tickfont_size=10, row=1, col=1)

    colores = [ROJO if v >= META_RIESGO else VERDE for v in pais.values]
    fig.add_trace(
        go.Bar(
            x=pais.values * 100, y=list(pais.index), orientation="h", marker_color=colores,
            text=[f"{v:.1%}" for v in pais.values], textposition="outside", textfont_size=10,
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.1f}% de activos<extra></extra>",
        ),
        row=1, col=2,
    )
    fig.add_vline(x=META_RIESGO * 100, line_dash="dot", line_color=AZUL, line_width=1.5, row=1, col=2)
    tope = max(15, (pais.max() * 100 if len(pais) else 0) + 4)
    fig.update_xaxes(range=[0, tope], ticksuffix="%", tickfont_size=10,
                     gridcolor="rgba(128,128,128,0.15)", row=1, col=2)
    fig.update_yaxes(tickfont_size=10, row=1, col=2)

    fig.update_annotations(font_size=12)
    fig.update_layout(height=alto, margin=dict(l=0, r=30, t=24, b=0), showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def mostrar(df, regla):
    if len(df) == 0:
        st.info("No hay clientes con esta combinación de filtros.")
        return
    st.plotly_chart(figura_riesgo(df, regla), config={"displayModeBar": False})
    st.caption("Mapa: verde = menor tasa de abandono, rojo = mayor tasa (escala 0–100%, no es meta). "
               f"País: verde ▼ cumple menos de {META_RIESGO:.0%}; rojo ▲ no cumple. Las celdas con pocos clientes requieren cautela; "
               "consulta su cantidad al pasar el cursor. Las asociaciones no demuestran causalidad.")
