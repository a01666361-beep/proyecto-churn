"""Dashboard Equipo 5: resumen, explicación visual y detalles de la selección."""
import streamlit as st

from src import estilos, seccion_factores, seccion_grupo, seccion_kpis, seccion_riesgo, ventanas
from src.config import RUTA_DATOS
from src.filtros import mostrar_filtros
from src.graficas import separar_panel
from src.indicadores import tasa_churn
from src.limpieza import cargar_datos

st.set_page_config(page_title="Churn · Equipo 5", page_icon="📉", layout="wide",
                   initial_sidebar_state="collapsed")
estilos.aplicar()


@st.cache_data
def obtener_datos():
    return cargar_datos(RUTA_DATOS)


df = obtener_datos()
tasa_global = tasa_churn(df)

st.markdown('<h1 class="titulo">Abandono de clientes</h1>', unsafe_allow_html=True)
st.caption("E-commerce · Equipo 5 · Entender qué pasa con nuestros clientes")
principal, lateral = st.columns([4, 1], gap="large")
with lateral:
    df_filtrado, regla = mostrar_filtros(df)

with principal:
    st.caption(f"{len(df_filtrado):,} de {len(df):,} clientes en el grupo seleccionado")
    b1, b2, b3 = st.columns(3, gap="small")
    if b1.button("Todas las variables", use_container_width=True):
        ventanas.ventana_variables(df_filtrado, tasa_global)
    if b2.button("Definiciones", use_container_width=True):
        ventanas.ventana_definiciones(tasa_global)
    if b3.button("Datos", use_container_width=True):
        ventanas.ventana_datos(df_filtrado)

    k1, k2, k3 = st.columns(3, gap="medium")
    with k1:
        seccion_kpis.tarjeta_clientes(df_filtrado, df)
    with k2:
        seccion_kpis.tarjeta_churn(df_filtrado, tasa_global, df)
    with k3:
        seccion_kpis.tarjeta_riesgo(df_filtrado, regla, df)

    st.markdown('<h2 class="seccion-titulo">Entender el abandono</h2>', unsafe_allow_html=True)
    if df_filtrado.empty:
        st.info("No hay clientes con esta combinación de filtros. Prueba otra selección.")
    else:
        factores = seccion_factores.figura_factores(df_filtrado, tasa_global)
        riesgo = seccion_riesgo.figura_riesgo(df_filtrado, regla)
        izquierda, derecha = st.columns(2, gap="medium")
        with izquierda:
            with st.container(border=True, key="grafica_llamadas"):
                st.markdown("### ¿Qué rangos de llamadas tienen más abandono?")
                st.plotly_chart(separar_panel(factores, 1), key="llamadas", use_container_width=True,
                                config={"displayModeBar": False})
                st.caption(f"Verde: menor abandono que el negocio; rojo: mayor. Referencia: {tasa_global:.1%}, no es una meta.")
        with derecha:
            with st.container(border=True, key="grafica_carrito"):
                st.markdown("### ¿Cómo difiere el carrito entre los dos grupos?")
                st.plotly_chart(separar_panel(factores, 2), key="carrito", use_container_width=True,
                                config={"displayModeBar": False})
                st.caption("Verde: activos; rojo: abandonaron. Caja: 50% central; línea: mediana; bigotes: mínimo y máximo.")
        izquierda, derecha = st.columns(2, gap="medium")
        with izquierda:
            with st.container(border=True, key="grafica_dias"):
                st.markdown("### ¿Cómo cambia el abandono con los días sin comprar?")
                st.plotly_chart(separar_panel(factores, 3), key="dias", use_container_width=True,
                                config={"displayModeBar": False})
                st.caption("Verde: menor abandono que el negocio; rojo: mayor. Los rangos tienen distinta amplitud; no es una serie temporal.")
        with derecha:
            with st.container(border=True, key="grafica_mapa"):
                st.markdown("### ¿Qué combinaciones tienen más abandono?")
                st.plotly_chart(separar_panel(riesgo, 1), key="mapa", use_container_width=True,
                                config={"displayModeBar": False})
                st.caption("Verde: menor abandono; rojo: mayor (escala 0–100%, no es meta). Consulta la cantidad de clientes al pasar el cursor.")

    with st.expander("¿Qué parte del problema está en este grupo?"):
        seccion_grupo.mostrar(df_filtrado, df, regla, {
            "País": st.session_state.get("f_pais", []),
            "Género": st.session_state.get("f_genero", []),
            "Edad": st.session_state.get("f_edad", []),
        })
    with st.expander("Ver activos con señales de riesgo por país"):
        if df_filtrado.empty:
            st.info("No hay clientes con esta combinación de filtros.")
        elif not (df_filtrado.Churned == 0).any():
            st.info("No hay clientes activos en este grupo para comparar por país.")
        else:
            st.plotly_chart(separar_panel(riesgo, 2, alto=350), key="paises",
                            use_container_width=True, config={"displayModeBar": False})
            st.caption("Verde ▼ cumple la meta de menos de 10%; rojo ▲ no cumple. La línea marca el 10%.")
    st.caption("Los grupos pequeños requieren cautela. Los datos muestran relaciones; no explican por sí solos por qué un cliente se fue.")
