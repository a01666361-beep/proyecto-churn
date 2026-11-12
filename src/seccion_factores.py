"""Comparación por llamadas, distribución de carrito y patrón de inactividad."""
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from src.config import AZUL, RELLENO_CIAN, RELLENO_NARANJA, ROJO, VERDE
from src.indicadores import tasa_por_rango


def _color(tasa, global_):
    return AZUL if abs(tasa - global_) < 0.0005 else ROJO if tasa > global_ else VERDE


def figura_factores(df, tasa_global, alto=280):
    fig = make_subplots(rows=1, cols=3, horizontal_spacing=0.10,
                        subplot_titles=["¿Qué rangos de llamadas<br>tienen más abandono?",
                                        "¿Cómo difiere el carrito<br>entre grupos?",
                                        "¿Cómo cambia el abandono<br>con la inactividad?"])
    llamadas = tasa_por_rango(df, "Customer_Service_Calls")
    fig.add_trace(go.Bar(
        x=[t * 100 if n else None for t, n in zip(llamadas.tasa, llamadas.clientes)],
        y=llamadas["rango"].astype(str), orientation="h",
        marker_color=[_color(t, tasa_global) for t in llamadas.tasa],
        text=[f"{t:.1%}" if n else "Sin datos" for t, n in zip(llamadas.tasa, llamadas.clientes)],
        textposition="outside", textfont_size=11, cliponaxis=False,
        customdata=llamadas.clientes,
        hovertemplate="%{y} llamadas<br>Abandono: %{x:.1f}%<br>Clientes del rango: %{customdata:,}<extra></extra>",
    ), row=1, col=1)
    fig.add_vline(x=tasa_global * 100, line_dash="dot", line_color=AZUL, row=1, col=1)
    fig.update_xaxes(range=[0, 112], ticksuffix="%", title_text="Tasa de abandono", row=1, col=1)
    fig.update_yaxes(type="category", autorange="reversed", title_text="Llamadas", row=1, col=1)
    # Cuartiles explícitos; los bigotes muestran mínimo y máximo, sin inferir atípicos.
    for estado, nombre, color in [(0, "Activos", VERDE), (1, "Abandonaron", ROJO)]:
        valores = df.loc[df.Churned == estado, "Cart_Abandonment_Rate"].dropna()
        if valores.empty:
            continue
        q1, mediana, q3 = valores.quantile([0.25, 0.5, 0.75])
        fig.add_trace(go.Box(
            name=f"{nombre}<br>n={len(valores):,}",
            x=[f"{nombre}<br>n={len(valores):,}"],
            q1=[q1], median=[mediana], q3=[q3],
            lowerfence=[valores.min()], upperfence=[valores.max()],
            boxpoints=False, line_color=color,
            fillcolor=RELLENO_CIAN if estado == 0 else RELLENO_NARANJA,
            hoverinfo="all",
        ), row=1, col=2)
    fig.update_yaxes(range=[-3, 103], ticksuffix="%", title_text="Carrito abandonado (%)", row=1, col=2)
    fig.update_xaxes(type="category", title_text="Estado del cliente", row=1, col=2)
    dias = tasa_por_rango(df, "Dias_Sin_Comprar")
    fig.add_trace(go.Scatter(
        x=dias["rango"].astype(str),
        y=[t * 100 if n else None for t, n in zip(dias.tasa, dias.clientes)],
        mode="lines+markers+text", connectgaps=False, line=dict(color=AZUL, width=2),
        marker=dict(color=[_color(t, tasa_global) for t in dias.tasa], size=8),
        text=[f"{t:.1%}" if n else "" for t, n in zip(dias.tasa, dias.clientes)],
        textposition="top center", textfont_size=11, cliponaxis=False,
        customdata=dias.clientes,
        hovertemplate="%{x} días sin comprar<br>Abandono: %{y:.1f}%<br>Clientes del rango: %{customdata:,}<extra></extra>",
    ), row=1, col=3)
    fig.add_hline(y=tasa_global * 100, line_dash="dot", line_color=AZUL, row=1, col=3)
    fig.update_yaxes(range=[0, 112], ticksuffix="%", title_text="Tasa de abandono", row=1, col=3)
    fig.update_xaxes(type="category", title_text="Rangos de días sin comprar", row=1, col=3)
    fig.update_xaxes(tickfont_size=10, title_font_size=10, automargin=True)
    fig.update_yaxes(tickfont_size=10, title_font_size=10, automargin=True,
                     gridcolor="rgba(128,128,128,0.15)")
    fig.update_annotations(font_size=11)
    fig.update_layout(height=alto, margin=dict(l=0, r=15, t=42, b=5), showlegend=False,
                      bargap=0.25, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def mostrar(df, tasa_global):
    if df.empty:
        st.info("No hay clientes con esta combinación de filtros.")
        return
    st.plotly_chart(figura_factores(df, tasa_global), config={"displayModeBar": False})
    st.caption(
        f"Llamadas y días: verde ▼ menor que global; rojo ▲ mayor que global ({tasa_global:.1%}, no es meta). "
        "Carrito: verde = activos; rojo = abandonaron; caja = 50% central, línea = mediana, bigotes = mínimo–máximo. "
        "Días: rangos de distinta amplitud, no es una serie temporal. Consulta el número de clientes al pasar el cursor."
    )
