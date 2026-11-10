"""
Datos y filtros compartidos por las tres pantallas.
RESPONSABLE: Coordinación (integrante 1)

app.py llama a `preparar()` en cada recarga, antes de mostrar la pantalla elegida.
Así los filtros del panel derecho se conservan al cambiar de pantalla.
Cada pantalla llama a `contexto()` para leer los datos ya filtrados.
"""
from types import SimpleNamespace

import streamlit as st

from src.config import RUTA_DATOS
from src.filtros import mostrar_filtros
from src.indicadores import tasa_churn
from src.limpieza import cargar_datos


@st.cache_data
def obtener_datos():
    return cargar_datos(RUTA_DATOS)


def preparar():
    """Dibuja los filtros y guarda la selección para la pantalla activa."""
    df = obtener_datos()
    df_filtrado, regla = mostrar_filtros(df)
    st.session_state["_contexto"] = SimpleNamespace(
        df=df, df_filtrado=df_filtrado, regla=regla, tasa_global=tasa_churn(df))


def contexto():
    if "_contexto" not in st.session_state:  # por si alguien abre la página sin app.py
        st.error("Abre el dashboard desde app.py (streamlit run app.py).")
        st.stop()
    return st.session_state["_contexto"]
