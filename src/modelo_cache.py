"""
Modelo y puntajes compartidos por las pantallas (se entrenan una sola vez por sesión del servidor).
RESPONSABLE: Sara Rivero

Lo usan la pantalla de Clientes prioritarios (scoring y segmentos) y la de Luis (alertas del modelo).
"""
import streamlit as st

from src import modelo as M
from src.contexto import obtener_datos


@st.cache_resource(show_spinner="Entrenando el modelo…")
def modelo_y_puntajes():
    """Entrena el modelo y los segmentos con toda la base y puntúa a todos los clientes."""
    df = obtener_datos()
    resultado = M.entrenar_modelo(df)
    segmentos = M.entrenar_segmentos(df)
    puntuado = M.puntuar(df, resultado["modelo"])
    puntuado["Segmento"] = segmentos["etiquetas"]
    return resultado, puntuado
