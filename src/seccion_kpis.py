"""
Sección 01 · Panorama general (4 tarjetas KPI).
RESPONSABLE: Integrante 4

QUÉ FALTA (TODO):
- Revisar que los textos de ayuda (help=) se entiendan para alguien sin estadística.
- Opcional: agregar una "lectura ejecutiva" de 1–2 frases debajo de las tarjetas.
"""
import streamlit as st

from src.config import META_RIESGO
from src.indicadores import resumen_riesgo, tasa_churn


def mostrar(df, tasa_global, regla):
    st.subheader("01 · Panorama general")

    tasa = tasa_churn(df)
    riesgo = resumen_riesgo(df, regla)
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Clientes analizados", f"{len(df):,}",
        help="Clientes que quedan con los filtros actuales.",
    )
    c2.metric(
        "Tasa de abandono", f"{tasa:.1%}",
        delta=f"{(tasa - tasa_global) * 100:+.1f} pts vs. global",
        delta_color="inverse",
        help=f"Porcentaje de clientes que abandonaron. Referencia global: {tasa_global:.1%}.",
    )
    c3.metric(
        "Clientes que abandonaron", f"{int(df['Churned'].sum()):,}",
        help="Clientes con Churned = 1.",
    )
    c4.metric(
        "Activos en perfil de riesgo", f"{riesgo['pct_activos']:.1%}",
        delta=f"{(riesgo['pct_activos'] - META_RIESGO) * 100:+.1f} pts vs. meta",
        delta_color="inverse",
        help=f"Activos que cumplen la regla de riesgo / total de activos. Meta: menos de {META_RIESGO:.0%}.",
    )
    st.caption(
        "La tasa de abandono es una proporción observada, no una predicción. "
        "Las asociaciones no demuestran causalidad."
    )
