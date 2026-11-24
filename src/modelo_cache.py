"""
Modelo y puntajes compartidos por las pantallas (se entrenan una sola vez por sesión del servidor).
RESPONSABLE: Sara Rivero

Lo usan la pantalla de Clientes prioritarios (scoring y segmentos) y la de Luis (alertas del modelo).
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from src import modelo as M
from src.contexto import obtener_datos


@st.cache_resource(show_spinner="Entrenando el modelo…")
def modelo_y_puntajes():
    """Entrena el modelo y los segmentos con toda la base y puntúa a todos los clientes."""
    df = obtener_datos()
    resultado = M.entrenar_campeon()  # Gradient Boosting (24-nov)
    resultado["entrenado"] = datetime.now(ZoneInfo("America/Mexico_City"))
    segmentos = M.entrenar_segmentos(df)
    puntuado = M.puntuar(df, resultado["modelo"])
    puntuado["Segmento"] = segmentos["etiquetas"]
    return resultado, puntuado
