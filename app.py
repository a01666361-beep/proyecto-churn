"""
Dashboard de abandono de clientes · Equipo 5
Archivo de entrada. Se ejecuta con:  python3 -m streamlit run app.py

RESPONSABLE: Arlen Martínez (coordinación)
Este archivo solo acomoda las piezas en la pantalla. Cada pieza vive en su
propio archivo dentro de src/ para que cada integrante trabaje sin pisar a los demás.

Pantalla (de lo general a lo particular, sin scroll):
  ┌───────────────────────────────────────────────┬─────────┐
  │ Título                       [botones extra]  │         │
  │ [KPI 1 abandono] [llamadas][carrito][días]    │ Filtros │
  │ [KPI 2 riesgo  ] [carrito × llamadas][país]   │         │
  └───────────────────────────────────────────────┴─────────┘
"""
import streamlit as st

from src import estilos, seccion_factores, seccion_kpis, seccion_riesgo, ventanas
from src.config import RUTA_DATOS
from src.filtros import mostrar_filtros
from src.indicadores import tasa_churn
from src.limpieza import cargar_datos

st.set_page_config(page_title="Churn · Equipo 5", page_icon="📉", layout="wide",
                   initial_sidebar_state="collapsed")
estilos.aplicar()


@st.cache_data
def obtener_datos():
    return cargar_datos(RUTA_DATOS)


df = obtener_datos()
tasa_global = tasa_churn(df)  # referencia fija: toda la base, sin filtros

principal, lateral = st.columns([5.2, 1], gap="medium")

with lateral:
    df_filtrado, regla = mostrar_filtros(df)

with principal:
    # Encabezado + botones a la información de apoyo
    titulo, b1, b2, b3 = st.columns([5, 1.25, 1.05, 0.8], vertical_alignment="center")
    titulo.markdown(
        '<h1 class="titulo">Abandono de clientes</h1>'
        f'<p class="subtitulo">E-commerce · {len(df_filtrado):,} de {len(df):,} clientes en la selección</p>',
        unsafe_allow_html=True,
    )
    if b1.button("Todas las variables", use_container_width=True):
        ventanas.ventana_variables(df_filtrado, tasa_global)
    if b2.button("Definiciones", use_container_width=True):
        ventanas.ventana_definiciones(tasa_global)
    if b3.button("Datos", use_container_width=True):
        ventanas.ventana_datos(df_filtrado)

    # Fila 1 · KPI 1 y sus variables relacionadas
    kpi, graficas = st.columns([1, 3.3], gap="small")
    with kpi:
        seccion_kpis.tarjeta_churn(df_filtrado, tasa_global)
    with graficas:
        seccion_factores.mostrar(df_filtrado, tasa_global)

    # Fila 2 · KPI 2 y sus variables relacionadas
    kpi, graficas = st.columns([1, 3.3], gap="small")
    with kpi:
        seccion_kpis.tarjeta_riesgo(df_filtrado, regla)
    with graficas:
        seccion_riesgo.mostrar(df_filtrado, regla)
