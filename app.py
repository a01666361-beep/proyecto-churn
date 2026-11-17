"""Dashboard Equipo 5. El menú se separa en cuatro bloques (retroalimentación del 12 de noviembre):

Inicio                → Resumen general                    (paginas/resumen.py)
Análisis por usuario  → Andrea López · gerente de retención (paginas/andrea.py)
                        Luis Ramírez · operaciones y CRM    (paginas/luis.py)
                        Carlos Mendoza · estrategia y valor (paginas/carlos.py)
Modelo predictivo     → Clientes prioritarios               (paginas/clientes.py)
                        Segmentos de clientes (K-Means)     (paginas/segmentos.py)
Plan de acción        → Recomendaciones                     (paginas/recomendaciones.py)

Los filtros (país, género, edad y criterios de riesgo) están a la derecha y son
los mismos para todas las pantallas.
"""
import streamlit as st

from src import estilos
from src.contexto import preparar, obtener_datos
from src.contrato_datos import ErrorContrato

st.set_page_config(page_title="Churn · Equipo 5", page_icon="📉", layout="wide",
                   initial_sidebar_state="collapsed")
try:
    obtener_datos()  # antes de dibujar el dashboard
except (ErrorContrato, ValueError, FileNotFoundError) as exc:
    st.error("No se puede publicar el dashboard: datos fuera de contrato")
    st.code(str(exc))
    st.stop()
estilos.aplicar()

pantalla = st.navigation({
    "Inicio": [
        st.Page("paginas/resumen.py", title="Resumen general", icon=":material/summarize:", default=True),
    ],
    "Análisis por usuario": [
        st.Page("paginas/andrea.py", title="Andrea · Priorizar campañas", icon=":material/campaign:"),
        st.Page("paginas/luis.py", title="Luis · Monitoreo y calidad", icon=":material/notifications:"),
        st.Page("paginas/carlos.py", title="Carlos · Valor y presupuesto", icon=":material/payments:"),
    ],
    "Modelo predictivo": [
        st.Page("paginas/clientes.py", title="Clientes prioritarios", icon=":material/person_search:"),
        st.Page("paginas/segmentos.py", title="Segmentos", icon=":material/groups:"),
    ],
    "Plan de acción": [
        st.Page("paginas/recomendaciones.py", title="Recomendaciones", icon=":material/task_alt:"),
    ],
}, position="top")

estilos.encabezado("Abandono de clientes")
principal, lateral = st.columns([4, 1], gap="large")
with lateral:
    preparar()
with principal:
    pantalla.run()
