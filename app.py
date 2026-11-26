"""Dashboard Equipo 5. El menú se separa en cuatro bloques (retroalimentación del 12 de noviembre):

Inicio                → Resumen general                    (paginas/resumen.py)
Análisis por usuario  → Andrea López · gerente de retención (paginas/andrea.py)
                        Luis Ramírez · operaciones y CRM    (paginas/luis.py)
                        Carlos Mendoza · estrategia y valor (paginas/carlos.py)
Modelo predictivo     → Clientes prioritarios               (paginas/clientes.py)
                        Segmentos de clientes (K-Means)     (paginas/segmentos.py)
                        Comparativa de modelos y predicción (paginas/modelos.py)
Plan de acción        → Recomendaciones                     (paginas/recomendaciones.py)
                        Asistente de retención (IA)         (paginas/asistente.py)
Datos                 → Actualización de datos y del modelo (paginas/actualizacion.py)

Los filtros (país, género, edad y criterios de riesgo) están a la derecha y son
los mismos para todas las pantallas.

Entregable 3: antes del menú se pide rol y contraseña (src/acceso.py). Cada rol ve
solo sus pantallas; la matriz de acceso está en src/acceso.py y en docs/entregable-3.md.
"""
import streamlit as st

from src import acceso, estilos
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
estilos.encabezado("Abandono de clientes")

# Entregable 3: acceso por rol. Sin sesión válida, iniciar_sesion() detiene la app con st.stop().
rol = acceso.iniciar_sesion()

MENU = {  # grupo del menú → [(archivo, ícono)]; el título sale de acceso.PANTALLAS
    "Inicio": [("paginas/resumen.py", ":material/summarize:")],
    "Análisis por usuario": [("paginas/andrea.py", ":material/campaign:"),
                             ("paginas/luis.py", ":material/notifications:"),
                             ("paginas/carlos.py", ":material/payments:")],
    "Modelo predictivo": [("paginas/clientes.py", ":material/person_search:"),
                          ("paginas/segmentos.py", ":material/groups:"),
                          ("paginas/modelos.py", ":material/model_training:")],
    "Plan de acción": [("paginas/recomendaciones.py", ":material/task_alt:"),
                       ("paginas/asistente.py", ":material/smart_toy:")],
    "Datos": [("paginas/actualizacion.py", ":material/sync:")],
}
permitidas = acceso.pantallas_de(rol)
menu = {}
for grupo, paginas in MENU.items():
    visibles = [st.Page(archivo, title=acceso.PANTALLAS[archivo], icon=icono, default=(archivo == permitidas[0]))
                for archivo, icono in paginas if archivo in permitidas]
    if visibles:
        menu[grupo] = visibles
# Solo se registran las pantallas del rol: las demás no están en el menú ni se abren por URL.
pantalla = st.navigation(menu, position="top")

principal, lateral = st.columns([4, 1], gap="large")
with lateral:
    acceso.barra_sesion()
    preparar()
with principal:
    pantalla.run()
