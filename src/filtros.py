"""
Panel de filtros (columna derecha) y regla de riesgo.
RESPONSABLE: Integrante 3

QUÉ FALTA (TODO):
- Decidir si conviene un filtro por Signup_Quarter.
"""
import streamlit as st

from src.config import REGLA_DEFAULT

VALORES_INICIALES = {
    "f_pais": [],
    "f_genero": [],
    "f_edad": [],
    "r_carrito": float(REGLA_DEFAULT["carrito_min"]),
    "r_llamadas": int(REGLA_DEFAULT["llamadas_min"]),
}


def _limpiar():
    for clave, valor in VALORES_INICIALES.items():
        st.session_state[clave] = valor


def mostrar_filtros(df):
    """Dibuja los filtros y regresa (df_filtrado, regla)."""
    for clave, valor in VALORES_INICIALES.items():
        st.session_state.setdefault(clave, valor)

    with st.container(key="filtros"):
        st.markdown('<p class="filtro-titulo">Elige qué grupo quieres ver</p>', unsafe_allow_html=True)
        paises = st.multiselect("País", sorted(df["Country"].unique()), key="f_pais", placeholder="Todos")
        generos = st.multiselect("Género", sorted(df["Gender"].unique()), key="f_genero", placeholder="Todos")
        edades = st.multiselect("Edad", sorted(df["Grupo_Edad"].unique()), key="f_edad", placeholder="Todas")

        with st.expander("Criterios de riesgo"):
            carrito = st.slider("Carrito abandonado >", 50.0, 95.0, step=0.25, key="r_carrito", format="%.2f%%")
            llamadas = st.slider("Llamadas ≥", 1, 12, key="r_llamadas")

        st.button("Limpiar filtros", on_click=_limpiar, use_container_width=True)

    df_filtrado = df
    if paises:
        df_filtrado = df_filtrado[df_filtrado["Country"].isin(paises)]
    if generos:
        df_filtrado = df_filtrado[df_filtrado["Gender"].isin(generos)]
    if edades:
        df_filtrado = df_filtrado[df_filtrado["Grupo_Edad"].isin(edades)]

    regla = {"carrito_min": carrito, "llamadas_min": llamadas}
    return df_filtrado, regla
