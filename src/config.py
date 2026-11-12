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
META_RIESGO = 0.05  # meta: menos del 5% de los activos en perfil de riesgo (línea base 6.75%)
META_CHURN = 0.25   # meta propuesta de churn para Andrea (editable en la pantalla 01)
ALERTA_PP = 0.02    # Luis: alerta si el churn de la selección supera la línea base en 2 puntos
MINIMO_SEGMENTO = 30  # no se muestran segmentos con menos clientes

# --- Regla de riesgo por defecto (se puede ajustar en los filtros) ---
# Viene del árbol de decisión de la Evidencia 2: primera división en carrito
# abandonado > 71.25% y segunda en 6 o más llamadas a servicio.
REGLA_DEFAULT = {
    "carrito_min": 71.25,  # Cart_Abandonment_Rate mayor a este valor
    "llamadas_min": 6,     # Customer_Service_Calls mayor o igual a este valor
}

# --- Rangos de las variables clave (para gráficas y mapa de calor) ---
RANGOS = {
    "Customer_Service_Calls": ([-1, 2, 5, 8, 11, 100], ["0–2", "3–5", "6–8", "9–11", "12+"]),
    "Cart_Abandonment_Rate": ([-1, 30, 50, 71.25, 101], ["≤30%", "30–50%", "50–71%", ">71%"]),
    "Dias_Sin_Comprar": ([-1, 30, 60, 90, 180, 10_000], ["0–30", "31–60", "61–90", "91–180", "180+"]),
}

# --- Nombres en español para mostrar ---
NOMBRES = {
    "Age": "Edad",
    "Membership_Years": "Años de membresía (log)",
    "Login_Frequency": "Frecuencia de inicio de sesión",
    "Session_Duration_Avg": "Duración promedio de sesión",
    "Pages_Per_Session": "Páginas por sesión",
    "Cart_Abandonment_Rate": "Carrito abandonado (%)",
    "Wishlist_Items": "Lista de deseos (log)",
    "Total_Purchases": "Total de compras (log)",
    "Average_Order_Value": "Valor promedio de pedido (log)",
    "Dias_Sin_Comprar": "Días sin comprar",
    "Discount_Usage_Rate": "Uso de descuentos (%)",
    "Returns_Rate": "Tasa de devoluciones (log)",
    "Email_Open_Rate": "Apertura de correos (%)",
    "Customer_Service_Calls": "Llamadas a servicio",
    "Product_Reviews_Written": "Reseñas escritas (log)",
    "Social_Media_Engagement_Score": "Interacción en redes",
    "Mobile_App_Usage": "Uso de la app móvil",
    "Payment_Method_Diversity": "Métodos de pago",
    "Lifetime_Value": "Valor de vida del cliente (log)",
    "Credit_Balance": "Saldo de crédito",
}

# --- Colores: identidad CartPulse Analytics (paleta petróleo–ámbar) ---
# Paleta oficial (de oscuro a cálido)
NOCHE = "#001219"       # texto principal, panel de filtros
PETROLEO = "#005F73"    # COLOR DOMINANTE: acciones, foco, encabezados, logo
TURQUESA = "#0A9396"    # favorable / retención
MENTA = "#94D2BD"       # series secundarias, acentos sobre fondo oscuro
ARENA = "#E9D8A6"       # neutro / punto medio
AMBAR = "#EE9B00"       # riesgo / atención
NARANJA = "#CA6702"     # alerta media
OXIDO = "#BB3E03"       # alerta alta
CARMIN = "#AE2012"      # lo malo (churn)
VINO = "#9B2226"        # lo muy malo / extremos

# Versiones oscuras SOLO para texto sobre fondo blanco
TURQUESA_TEXTO = "#087F82"
AMBAR_TEXTO = "#A35A00"

# Nombres que ya usa el dashboard (no cambiar los nombres, solo los valores)
AZUL = PETROLEO         # color principal
AZUL_CLARO = MENTA      # series secundarias
AZUL_VIVO = TURQUESA    # acentos
AZUL_PROFUNDO = NOCHE
AZUL_PALIDO = ARENA     # punto medio neutro de los mapas de calor
ROJO = CARMIN           # solo para cosas malas
VERDE = TURQUESA        # favorable: debajo de la meta o referencia indicada
GRIS = "#7A8C93"        # neutro
# compatibilidad con la versión anterior del kit
CIAN, VERDE_VIVO, LIMA, GRIS_UI = PETROLEO, TURQUESA, MENTA, NOCHE

# Orden de colores para gráficas con varias series
PALETA = [PETROLEO, AMBAR, TURQUESA, OXIDO, MENTA, NARANJA, VINO, NOCHE]
