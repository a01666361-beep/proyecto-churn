"""Dashboard Equipo 5: resumen general, tres pantallas (una por user persona) y recomendaciones.

00 Resumen general                         → paginas/resumen.py
01 Andrea López · gerente de retención     → paginas/andrea.py
02 Luis Ramírez · operaciones de datos/CRM → paginas/luis.py
03 Carlos Mendoza · estrategia y valor     → paginas/carlos.py
04 Recomendaciones finales                 → paginas/recomendaciones.py

Los filtros (país, género, edad y criterios de riesgo) están a la derecha y son
los mismos para todas las pantallas.
"""
import streamlit as st

from src import estilos
from src.contexto import preparar

st.set_page_config(page_title="Churn · Equipo 5", page_icon="📉", layout="wide",
                   initial_sidebar_state="collapsed")
estilos.aplicar()

pantalla = st.navigation([
    st.Page("paginas/resumen.py", title="00 · Resumen general", icon=":material/summarize:", default=True),
    st.Page("paginas/andrea.py", title="01 · Andrea · Priorizar campañas", icon=":material/campaign:"),
    st.Page("paginas/luis.py", title="02 · Luis · Alertas y calidad", icon=":material/notifications:"),
    st.Page("paginas/carlos.py", title="03 · Carlos · Valor y presupuesto", icon=":material/payments:"),
    st.Page("paginas/recomendaciones.py", title="04 · Recomendaciones", icon=":material/task_alt:"),
], position="top")

st.markdown('<h1 class="titulo">Abandono de clientes</h1>', unsafe_allow_html=True)
principal, lateral = st.columns([4, 1], gap="large")
with lateral:
    preparar()
with principal:
    pantalla.run()
