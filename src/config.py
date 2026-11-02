"""
Configuración general del dashboard.
RESPONSABLE: Coordinación (integrante 1)

Aquí van las constantes que usa toda la app. Si algo se repite en varios
archivos (rutas, metas, colores), va aquí para cambiarlo en un solo lugar.
"""
from pathlib import Path

# --- Rutas (siempre relativas a la carpeta del proyecto) ---
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DATOS = CARPETA_PROYECTO / "data" / "ecommerce_churn_final_comas.csv"

# --- Metas y referencias del equipo ---
META_RIESGO = 0.10  # meta propuesta: menos del 10% de los activos en perfil de riesgo

# --- Regla de riesgo por defecto (se puede ajustar en la barra lateral) ---
# Viene del árbol de decisión de la Evidencia 2: primera división en carrito
# abandonado > 71.25% y segunda en 6 o más llamadas a servicio.
REGLA_DEFAULT = {
    "carrito_min": 71.25,  # Cart_Abandonment_Rate mayor a este valor
    "llamadas_min": 6,     # Customer_Service_Calls mayor o igual a este valor
}

# --- Colores ---
COLOR_BARRA = "#185FA5"
COLOR_REFERENCIA = "#E24B4A"
