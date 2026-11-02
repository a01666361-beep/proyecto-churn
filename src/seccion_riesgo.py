"""
Sección 03 · Perfil de alto riesgo.
RESPONSABLE: Integrante 6

QUÉ FALTA (TODO):
- Semana siguiente: agregar la opción de usar el modelo Gradient Boosting
  (probabilidad >= 0.44) en lugar de la regla.
- Revisar el texto de "Cómo interpretar este KPI".
"""
import plotly.graph_objects as go
import streamlit as st

from src.config import META_RIESGO
from src.indicadores import resumen_riesgo


def grafica_bala(pct, meta):
    """Gráfica de bala: valor actual contra la meta."""
    fig = go.Figure(
        go.Indicator(
            mode="number+gauge",
            value=pct * 100,
            number={"suffix": "%", "valueformat": ".1f"},
            gauge={
                "shape": "bullet",
                "axis": {"range": [0, max(30, pct * 100 + 5)]},
                "bar": {"color": "#EF9F27"},
                "threshold": {"line": {"color": "black", "width": 3}, "value": meta * 100},
            },
        )
    )
    fig.update_layout(height=120, margin=dict(l=20, r=20, t=20, b=20))
    return fig


def mostrar(df, tasa_global, regla):
    st.subheader("03 · Perfil de alto riesgo")
    st.caption(
        f"Regla actual: carrito abandonado mayor a {regla['carrito_min']}% "
        f"y {regla['llamadas_min']} o más llamadas a servicio."
    )

    if len(df) == 0:
        st.info("No hay clientes con esta combinación de filtros.")
        return

    r = resumen_riesgo(df, regla)
    izq, der = st.columns([3, 2])

    with izq:
        a, b, c = st.columns(3)
        a.metric("Activos en el perfil", f"{r['activos_en_perfil']:,}")
        b.metric("% de activos en el perfil", f"{r['pct_activos']:.1%}")
        c.metric(
            "Churn histórico del perfil", f"{r['tasa_historica']:.1%}",
            delta=f"{(r['tasa_historica'] - tasa_global) * 100:+.1f} pts vs. global",
            delta_color="inverse",
        )
        st.plotly_chart(grafica_bala(r["pct_activos"], META_RIESGO))
        st.caption(f"La línea negra es la meta del equipo: menos de {META_RIESGO:.0%} de los activos.")

    with der:
        with st.container(border=True):
            st.markdown("**Cómo interpretar este KPI**")
            st.markdown(
                "- **Numerador:** clientes activos que cumplen los dos criterios.\n"
                "- **Denominador:** todos los clientes activos de la selección.\n"
                "- **Churn histórico:** se calcula con activos y no activos que cumplen la regla.\n"
                "- **Precaución:** no es la probabilidad de que un cliente se vaya "
                "ni demuestra que estos factores causen el abandono."
            )
