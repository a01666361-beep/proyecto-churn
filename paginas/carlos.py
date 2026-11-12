"""
Pantalla 03 · Carlos Mendoza, director de estrategia y valor del cliente.
Pregunta: ¿se están yendo los clientes valiosos y en qué segmentos conviene invertir?
RESPONSABLE: (poner nombre)
"""
import plotly.graph_objects as go
import streamlit as st

from src.config import AZUL, ROJO, VERDE
from src.contexto import contexto
from src.vistas import cuartiles_ltv, escenario, resumen_carlos, valor_por_pais

c = contexto()
df, df_general, regla, tasa_global = c.df_filtrado, c.df, c.regla, c.tasa_global
SIN_BARRA = {"displayModeBar": False}

st.markdown('<h2 class="seccion-titulo">Valor del cliente y decisiones estratégicas</h2>', unsafe_allow_html=True)
st.caption("Identificar dónde se concentra el valor en riesgo, sin atribuir ingresos o ROI que la base no mide · "
           f"{len(df):,} de {len(df_general):,} clientes en el grupo seleccionado")

if df.empty:
    st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

r = resumen_carlos(df, regla)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Clientes evaluados", f"{r['clientes']:,}")
m2.metric("Abandono observado", f"{r['tasa']:.1%}", f"{(r['tasa'] - tasa_global) * 100:+.1f} pts vs. global",
          delta_color="inverse")
m3.metric("Mediana de Lifetime_Value", f"{r['mediana_ltv']:.3f}", help="Escala del CSV (logaritmo), no es moneda.")
m4.metric("Pérdida en dinero / ROI", "No calculable", help="Faltan moneda del LTV, costos y resultados de campañas.")

cuartiles = cuartiles_ltv(df, df_general)
izquierda, derecha = st.columns([1, 1.1], gap="medium")
with izquierda:
    with st.container(border=True, key="grafica_ltv"):
        st.markdown("### ¿Se están yendo los clientes más valiosos?")
        barras = go.Figure(go.Bar(
            x=cuartiles["cuartil"].astype(str), y=cuartiles["tasa"] * 100,
            marker_color=[ROJO if t > tasa_global else VERDE for t in cuartiles["tasa"]],
            text=[f"{t:.1%}" for t in cuartiles["tasa"]], textposition="outside", cliponaxis=False,
            customdata=cuartiles[["clientes", "abandonaron"]].values,
            hovertemplate="%{x}<br>Churn: %{y:.1f}%<br>%{customdata[1]:,} de %{customdata[0]:,} clientes<extra></extra>"))
        barras.add_hline(y=tasa_global * 100, line_dash="dot", line_color=AZUL, line_width=1.5)
        barras.update_layout(height=330, margin=dict(l=0, r=10, t=20, b=10),
                             yaxis=dict(range=[0, max(55, cuartiles["tasa"].max() * 100 + 10)], ticksuffix="%",
                                        gridcolor="rgba(128,128,128,0.15)"),
                             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(barras, key="ltv", use_container_width=True, config=SIN_BARRA)
        st.caption(f"Cuartiles de Lifetime_Value calculados con la base completa (escala del CSV). "
                   f"Línea punteada: churn global ({tasa_global:.1%}).")

with derecha:
    with st.container(border=True, key="tabla_paises"):
        st.markdown("### Segmentos de valor por país")
        paises = valor_por_pais(df, regla)
        st.dataframe(paises, column_order=list(paises.columns), hide_index=True, use_container_width=True, height=330, column_config={
            "Churn": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
            "Mediana LTV": st.column_config.NumberColumn(format="%.3f"),
            "Clientes": st.column_config.NumberColumn(format="localized"),
            "Activos en riesgo": st.column_config.NumberColumn(format="localized"),
        })
        st.caption("Origen: País procede del CSV; Clientes, Churn, Mediana LTV y Activos en riesgo son cálculos con datos observados, la mediana LTV conserva la escala logarítmica y no es una moneda")
        st.caption("Ordenado por churn. Es descriptivo, no una recomendación automática de presupuesto.")
        st.download_button("Exportar análisis (CSV)", paises.to_csv(index=False).encode("utf-8"),
                           file_name="valor_por_pais.csv", mime="text/csv")

izquierda, derecha = st.columns(2, gap="medium")
with izquierda:
    with st.container(border=True):
        st.markdown("### Escenario de mejora del churn")
        puntos = st.slider("Reducción hipotética (puntos porcentuales)", 0.5, 5.0, 1.0, 0.5, key="c_puntos")
        alto_valor = cuartiles.iloc[-1]
        st.metric("SIMULACIÓN · Clientes que se retendrían", f"{escenario(r['clientes'], puntos):,}")
        st.metric("SIMULACIÓN · De valor alto (Q4)", f"{escenario(int(alto_valor['clientes']), puntos):,}")
        st.caption("Clientes × reducción supuesta. Es una simulación aritmética, no un pronóstico del efecto de una campaña.")
with derecha:
    with st.container(border=True):
        st.markdown("### Presupuesto y efectividad de campañas")
        st.markdown("""
| Dato necesario | Estado |
|---|---|
| Presupuesto de retención | Sin datos |
| Ingresos atribuibles | Sin datos |
| ROI de campañas | No calculable |
| Resultados antes / después | No disponibles |
""")
        st.caption("Para evaluar la inversión (y comparar retención contra adquisición) se necesitan costos, fechas, "
                   "clientes expuestos y resultados observados por campaña.")

st.caption("Próximas decisiones: 1) priorizar segmentos de alto valor con abandono elevado; "
           "2) agregar costo e ingreso por campaña; 3) definir metas financieras cuando se validen las unidades.")
