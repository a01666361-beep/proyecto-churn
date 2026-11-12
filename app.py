"""Dashboard Equipo 5: tres pantallas, una por user persona.

01 Andrea López · gerente de retención     → paginas/andrea.py
02 Luis Ramírez · operaciones de datos/CRM → paginas/luis.py
03 Carlos Mendoza · estrategia y valor     → paginas/carlos.py

Los filtros (país, género, edad y criterios de riesgo) están a la derecha y son
los mismos para las tres pantallas.
"""
import streamlit as st

from src import estilos
from src.contexto import preparar

st.set_page_config(page_title="Churn · Equipo 5", page_icon="📉", layout="wide",
                   initial_sidebar_state="collapsed")
estilos.aplicar()

pantalla = st.navigation([
    st.Page("paginas/andrea.py", title="01 · Andrea · Priorizar campañas", icon=":material/campaign:", default=True),
    st.Page("paginas/luis.py", title="02 · Luis · Alertas y calidad", icon=":material/notifications:"),
    st.Page("paginas/carlos.py", title="03 · Carlos · Valor y presupuesto", icon=":material/payments:"),
], position="top")

estilos.encabezado("Abandono de clientes")
principal, lateral = st.columns([4, 1], gap="large")
with lateral:
    preparar()
with principal:
    pantalla.run()
