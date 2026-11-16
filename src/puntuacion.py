"""
Modelo y segmentos ya calculados, para las páginas que los necesitan.
RESPONSABLE: Víctor García (A01784206)

Entrena una sola vez la regresión logística y los segmentos de src/modelo.py con toda la base
y guarda el resultado en caché. Usa exactamente las mismas funciones que la pantalla 05, así que
la probabilidad, el nivel de riesgo y el segmento de cada cliente son los mismos en las dos pantallas.
"""
import streamlit as st

from src import modelo as M
from src.contexto import obtener_datos


@st.cache_resource(show_spinner="Entrenando el modelo y los segmentos…")
def modelo_y_puntuacion():
    df = obtener_datos()
    resultado = M.entrenar_modelo(df)
    segmentos = M.entrenar_segmentos(df)
    puntuado = M.puntuar(df, resultado["modelo"])
    puntuado["Segmento"] = segmentos["etiquetas"]
    return resultado, puntuado
