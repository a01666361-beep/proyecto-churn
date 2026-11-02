"""
Dashboard de abandono de clientes · Equipo 5
Archivo de entrada. Se ejecuta con:  streamlit run app.py

RESPONSABLE: Coordinación (Arlen Martínez 1)
Este archivo solo junta las secciones. Cada sección vive en su propio
archivo dentro de src/ para que cada integrante trabaje sin pisar a los demás.
"""
import streamlit as st

from src import seccion_factores, seccion_kpis, seccion_riesgo
from src.config import RUTA_DATOS
from src.filtros import mostrar_filtros
from src.indicadores import tasa_churn
from src.limpieza import cargar_datos

st.set_page_config(page_title="Churn · Equipo 5", page_icon="📉", layout="wide")


@st.cache_data
def obtener_datos():
    return cargar_datos(RUTA_DATOS)


df = obtener_datos()
tasa_global = tasa_churn(df)  # referencia fija: toda la base, sin filtros

st.title("Panorama de abandono de clientes")
st.caption(
    f"E-commerce Customer Churn · {len(df):,} clientes · "
    "Indicadores para priorizar acciones de retención"
)

df_filtrado, regla = mostrar_filtros(df)

seccion_kpis.mostrar(df_filtrado, tasa_global, regla)
st.divider()
seccion_factores.mostrar(df_filtrado, tasa_global)
st.divider()
seccion_riesgo.mostrar(df_filtrado, tasa_global, regla)

st.divider()
st.caption("Equipo 5 · Analítica de datos y herramientas de IA · Tec de Monterrey")
