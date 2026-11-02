"""
Barra lateral: filtros y regla de riesgo.
RESPONSABLE: Integrante 3

QUÉ FALTA (TODO):
- Agregar un botón "Limpiar filtros" (pista: st.button + st.session_state).
- Decidir si conviene un filtro por Signup_Quarter.
"""
import streamlit as st

from src.config import REGLA_DEFAULT


def mostrar_filtros(df):
    """Dibuja los filtros en la barra lateral y regresa (df_filtrado, regla)."""
    st.sidebar.header("Filtros")

    paises = st.sidebar.multiselect(
        "País", sorted(df["Country"].unique()), placeholder="Todos los países"
    )
    generos = st.sidebar.multiselect(
        "Género", sorted(df["Gender"].unique()), placeholder="Todos los géneros"
    )
    edades = st.sidebar.multiselect(
        "Grupo de edad", sorted(df["Grupo_Edad"].unique()), placeholder="Todas las edades"
    )

    df_filtrado = df.copy()
    if paises:
        df_filtrado = df_filtrado[df_filtrado["Country"].isin(paises)]
    if generos:
        df_filtrado = df_filtrado[df_filtrado["Gender"].isin(generos)]
    if edades:
        df_filtrado = df_filtrado[df_filtrado["Grupo_Edad"].isin(edades)]

    st.sidebar.divider()
    st.sidebar.header("Regla de alto riesgo")
    st.sidebar.caption("El cliente debe cumplir los dos criterios a la vez.")
    regla = {
        "carrito_min": st.sidebar.slider(
            "Carrito abandonado mayor a (%)", 50.0, 95.0,
            float(REGLA_DEFAULT["carrito_min"]), step=0.25,
        ),
        "llamadas_min": st.sidebar.slider(
            "Llamadas a servicio, al menos", 1, 12, int(REGLA_DEFAULT["llamadas_min"])
        ),
    }
    return df_filtrado, regla
