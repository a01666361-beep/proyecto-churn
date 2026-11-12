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

# --- Colores: identidad CartPulse Analytics (paleta complementaria de la UI de análisis) ---
# Solo 7 colores. Naranja = alertas / lo malo. Cian = lo favorable y lo activo.
FONDO = "#1A1D24"       # fondo principal (app y panel de filtros)
TARJETA = "#293545"     # fondo de tarjetas y contenedores de datos
AZUL_DATOS = "#007BFF"  # COLOR PRINCIPAL: números, barras, botones
NARANJA = "#FFA03A"     # advertencia: alertas, churn alto, lo malo
CIAN = "#3FD8E0"        # énfasis: estados activos, filtros, lo favorable
GRIS_TEXTO = "#B0B7C3"  # texto secundario, ayudas e íconos
BLANCO = "#FFFFFF"      # texto principal

# Tonos de apoyo (derivados de la paleta, solo cuando hace falta)
AZUL_SUAVE = "#3A6EA5"  # barras "por debajo del promedio" junto a AZUL_DATOS
AZUL_TEXTO = "#4DA3FF"  # azul para texto pequeño sobre fondo oscuro
LINEA = "#343B4A"       # bordes y cuadrícula

# Nombres que ya usa el dashboard (no cambiar los nombres, solo los valores)
AZUL = AZUL_DATOS       # color principal
AZUL_CLARO = AZUL_SUAVE # serie secundaria
AZUL_VIVO = CIAN        # acentos
AZUL_PROFUNDO = TARJETA
AZUL_PALIDO = TARJETA   # punto medio neutro de los mapas de calor
ROJO = NARANJA          # lo malo (desfavorable) = naranja de advertencia
VERDE = CIAN            # lo favorable = cian de énfasis
GRIS = GRIS_TEXTO       # neutro

# Alias de versiones anteriores del kit (para no romper nada)
NOCHE = GRAFITO = FONDO
MARINO = CIELO = TARJETA
PETROLEO = MARINO_OSCURO = TARJETA
CERULEO = AZUL_FUERTE = AZUL_BARRA = AZUL_DATOS
CELESTE = AZUL_BRILLO = AZUL_TEXTO
TURQUESA = MENTA = CIAN
AMBAR = AMARILLO = NARANJA
ROJO_CLARO = CARMIN = OXIDO = VINO = NARANJA
ARENA = TARJETA
TEXTO, TEXTO_SUAVE = BLANCO, GRIS_TEXTO
TURQUESA_TEXTO, AMBAR_TEXTO, ROJO_TEXTO = CIAN, NARANJA, NARANJA
VERDE_VIVO, LIMA, GRIS_UI = CIAN, CIAN, FONDO

# Rellenos transparentes (cajas, áreas)
RELLENO_AZUL = "rgba(0,123,255,0.18)"
RELLENO_NARANJA = "rgba(255,160,58,0.18)"
RELLENO_CIAN = "rgba(63,216,224,0.18)"

# Orden de colores para gráficas con varias series
PALETA = [AZUL_DATOS, NARANJA, CIAN, GRIS_TEXTO, AZUL_SUAVE, BLANCO]
