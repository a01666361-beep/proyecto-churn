"""
Ventanas emergentes con la información de apoyo (se abren con los botones de arriba).
RESPONSABLE: Integrante 7

- Todas las variables: correlación de cada variable con el churn, churn por
  quintil de la variable que elijas y cómo se relacionan entre sí.
- Definiciones: cómo se calcula cada KPI.
- Datos: tabla filtrada y descarga en CSV.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config import AZUL, AZUL_CLARO, NOMBRES, ROJO
from src.indicadores import correlaciones, matriz_correlacion


def _nombre(col):
    return NOMBRES.get(col, col)


@st.dialog("Todas las variables", width="large")
def ventana_variables(df, tasa_global):
    if len(df) < 10:
        st.info("Hay muy pocos clientes con estos filtros.")
        return

    izq, der = st.columns([1, 1.15])

    with izq:
        corr = correlaciones(df)
        fig = go.Figure(go.Bar(
            x=corr.values, y=[_nombre(c) for c in corr.index], orientation="h",
            marker_color=[ROJO if v > 0 else AZUL for v in corr.values],
            text=[f"{v:+.2f}" for v in corr.values], textposition="outside", textfont_size=10,
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.3f}<extra></extra>",
        ))
        fig.update_layout(title=dict(text="Correlación con el abandono", font_size=13), height=560,
                          margin=dict(l=0, r=30, t=30, b=0), xaxis=dict(range=[-0.4, 0.4], tickfont_size=10),
                          yaxis=dict(tickfont_size=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, config={"displayModeBar": False})

    with der:
        opciones = list(corr.index[::-1])
        variable = st.selectbox("Variable", opciones, format_func=_nombre)
        grupos = pd.qcut(df[variable].rank(method="first"), q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
        tabla = df.groupby(grupos, observed=False).agg(
            tasa=("Churned", "mean"), minimo=(variable, "min"), maximo=(variable, "max"))
        etiquetas = [f"{q}<br>{fila.minimo:,.1f}–{fila.maximo:,.1f}" for q, fila in tabla.iterrows()]
        fig = go.Figure(go.Bar(
            x=etiquetas, y=tabla["tasa"] * 100,
            marker_color=[AZUL if t > tasa_global else AZUL_CLARO for t in tabla["tasa"]],
            text=[f"{t:.0%}" for t in tabla["tasa"]], textposition="outside", textfont_size=10, cliponaxis=False,
        ))
        fig.add_hline(y=tasa_global * 100, line_dash="dot", line_color=ROJO, line_width=1.5)
        fig.update_layout(title=dict(text=f"Churn por quintil · {_nombre(variable)}", font_size=13), height=230,
                          margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(range=[0, 85], ticksuffix="%"),
                          xaxis=dict(tickfont_size=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, config={"displayModeBar": False})

        m = matriz_correlacion(df, n=8)
        nombres = [_nombre(c) if c != "Churned" else "Abandono" for c in m.columns]
        fig = go.Figure(go.Heatmap(
            z=m.values, x=nombres, y=nombres, zmin=-1, zmax=1,
            colorscale=[[0, AZUL], [0.5, "#F1EFE8"], [1, ROJO]],
            text=m.round(2).values, texttemplate="%{text}", textfont_size=9, showscale=False,
            hovertemplate="%{y} · %{x}: %{z:.2f}<extra></extra>",
        ))
        fig.update_layout(title=dict(text="Relación entre las variables más importantes", font_size=13),
                          height=300, margin=dict(l=0, r=0, t=30, b=0),
                          xaxis=dict(tickfont_size=9, tickangle=-35), yaxis=dict(tickfont_size=9, autorange="reversed"),
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, config={"displayModeBar": False})


@st.dialog("Definiciones de los KPI", width="large")
def ventana_definiciones(tasa_global):
    st.markdown(f"""
| KPI | Cálculo | Referencia |
|---|---|---|
| **Tasa de abandono** | Clientes con `Churned = 1` / total de clientes de la selección | Global: {tasa_global:.1%} |
| **Activos en perfil de riesgo** | Activos que cumplen la regla / total de activos de la selección | Meta: menos de 10% |
| **Churn del perfil** | Churn de todos los clientes (activos y no) que cumplen la regla | Se compara con la tasa global |

**Regla de riesgo:** carrito abandonado mayor al umbral **y** llamadas a servicio mayores o iguales al umbral
(por defecto 71.25% y 6, tomados del árbol de decisión de la Evidencia 2). Se ajusta en los filtros.

**Precaución:** las tasas son proporciones observadas, no probabilidades individuales, y las
asociaciones no demuestran causalidad.

**Datos:** `ecommerce_churn_final_comas.csv`, 50,000 clientes. Las variables marcadas con *(log)*
están guardadas en escala log(1 + x); los días sin comprar se muestran ya convertidos a días.
""")


@st.dialog("Datos", width="large")
def ventana_datos(df):
    st.caption(f"{len(df):,} clientes con los filtros actuales")
    st.dataframe(df, height=420, hide_index=True)
    st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"),
                       file_name="clientes_filtrados.csv", mime="text/csv")
