"""
Pantalla 03 · Carlos Mendoza, director de estrategia y valor del cliente.
Decisión: si se están yendo los clientes valiosos y en qué segmentos conviene invertir.
RESPONSABLE: (poner nombre)
"""
import plotly.graph_objects as go
import streamlit as st

from src import ayuda

from src.config import AZUL, ROJO, VERDE
from src.contexto import contexto
from src.vistas import cuartiles_ltv, escenario, resumen_carlos, valor_por_pais
from src import acceso

acceso.exigir("paginas/carlos.py")  # entregable 3: segunda barrera por rol

c = contexto()
df, df_general, regla, tasa_global = c.df_filtrado, c.df, c.regla, c.tasa_global
SIN_BARRA = {"displayModeBar": False}

ayuda.titulo_pantalla("Valor del cliente y decisiones estratégicas", "carlos",
                      "Dónde se concentra el valor en riesgo, sin atribuir ingresos o ROI que la base no mide · "
                      f"{len(df):,} de {len(df_general):,} clientes en el grupo seleccionado")

if df.empty:
    st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

r = resumen_carlos(df, regla)
abandonaron = int(df["Churned"].sum())

with st.container(border=True, key="supuesto_dinero"):
    st.markdown("**SUPUESTO · Valor en dinero por cliente**")
    s1, s2 = st.columns(2)
    valor_cliente = s1.number_input(
        "Valor promedio de un cliente ($)", min_value=0.0, value=0.0, step=100.0, format="%.2f", key="c_valor",
        help="Lo escribe el usuario. El CSV no trae moneda para Lifetime_Value, así que este monto es un supuesto.")
    presupuesto = s2.number_input(
        "Presupuesto de la campaña de retención ($, opcional)", min_value=0.0, value=0.0, step=1000.0,
        format="%.2f", key="c_presupuesto", help="Solo se usa para estimar el ROI del escenario.")
    st.caption("Las cifras en dinero de esta pantalla son SUPUESTOS: clientes observados × el valor que escribas aquí. "
               "Con 0 se muestran como «No calculable».")


def dinero(clientes):
    return f"${clientes * valor_cliente:,.0f}" if valor_cliente > 0 else "No calculable"


m1, m2, m3, m4 = st.columns(4)
m1.metric("Clientes evaluados", f"{r['clientes']:,}")
m2.metric("Abandono observado", f"{r['tasa']:.1%}", f"{(r['tasa'] - tasa_global) * 100:+.1f} pts vs. global",
          delta_color="inverse")
m3.metric("Mediana de Lifetime_Value", f"{r['mediana_ltv']:.3f}", help="Escala del CSV (logaritmo), no es moneda.")
m4.metric("SUPUESTO · Pérdida en dinero", dinero(abandonaron),
          help=f"{abandonaron:,} clientes que abandonaron × valor por cliente escrito arriba. No sale del CSV.")

cuartiles = cuartiles_ltv(df, df_general)
izquierda, derecha = st.columns([1, 1.1], gap="medium")
with izquierda:
    with st.container(border=True, key="grafica_ltv"):
        q4 = cuartiles.iloc[-1]
        ayuda.titulo_grafica(
            f"Abandono por cuartil de valor: Q4 {q4['tasa']:.1%} vs. negocio {tasa_global:.1%}",
            "La tasa de abandono de cada cuartil de Lifetime_Value, de menor (Q1) a mayor valor (Q4).",
            "Barras naranjas: el cuartil abandona más que el negocio; cian: menos. La línea punteada es el churn global.",
            "Si hay que proteger primero a los clientes de mayor valor.",
            pregunta="¿Se están yendo más los clientes de mayor valor que el resto?")
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
        ayuda.titulo_grafica(
            "Segmentos de valor por país",
            "Por país: clientes, churn, mediana de Lifetime_Value y activos en perfil de riesgo.",
            "Ordenado por churn. La mediana LTV está en escala logarítmica, no es dinero.",
            "En qué países conviene concentrar la inversión en retención.",
            pregunta="¿En qué países se concentran los clientes valiosos en riesgo?")
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
        ayuda.titulo_grafica(
            "Escenario de mejora del churn",
            "SIMULACIÓN: cuántos clientes se retendrían si el churn bajara los puntos elegidos.",
            "Es aritmética (clientes × reducción supuesta), no un pronóstico del efecto de una campaña.",
            "Dimensionar el beneficio potencial antes de pedir presupuesto.",
            pregunta="¿Cuántos clientes se retendrían si el abandono bajara lo que supone el escenario?")
        puntos = st.slider("Reducción hipotética (puntos porcentuales)", 0.5, 5.0, 1.0, 0.5, key="c_puntos")
        alto_valor = cuartiles.iloc[-1]
        st.metric("SIMULACIÓN · Clientes que se retendrían", f"{escenario(r['clientes'], puntos):,}")
        st.metric("SIMULACIÓN · De valor alto (Q4)", f"{escenario(int(alto_valor['clientes']), puntos):,}")
        st.metric("SIMULACIÓN · Dinero que se conservaría", dinero(escenario(r['clientes'], puntos)))
        st.caption("Clientes × reducción supuesta. Es una simulación aritmética, no un pronóstico del efecto de una campaña.")
with derecha:
    with st.container(border=True):
        st.markdown("### Presupuesto y efectividad de campañas")
        retenidos = escenario(r["clientes"], puntos)
        beneficio = retenidos * valor_cliente
        if valor_cliente > 0 and presupuesto > 0:
            roi = f"{(beneficio - presupuesto) / presupuesto:+.0%} (supuesto)"
        else:
            roi = "No calculable"
        st.markdown(f"""
| Dato | Estado |
|---|---|
| Valor por cliente | {f"${valor_cliente:,.2f} (supuesto)" if valor_cliente > 0 else "Sin datos"} |
| Presupuesto de retención | {f"${presupuesto:,.2f} (supuesto)" if presupuesto > 0 else "Sin datos"} |
| Valor en riesgo (activos en perfil) | {dinero(r["activos_en_riesgo"])} |
| Ingresos conservados en el escenario | {dinero(retenidos)} |
| ROI del escenario | {roi} |
| Resultados antes / después | No disponibles |
""")
        st.caption("Para evaluar la inversión (y comparar retención contra adquisición) se necesitan costos, fechas, "
                   "clientes expuestos y resultados observados por campaña.")

st.caption("Próximas decisiones: 1) priorizar segmentos de alto valor con abandono elevado; "
           "2) agregar costo e ingreso por campaña; 3) definir metas financieras cuando se validen las unidades.")
