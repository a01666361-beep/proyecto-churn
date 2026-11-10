"""
Cálculos de las tres pantallas (Andrea, Luis y Carlos). Solo pandas, sin Streamlit,
para poder revisarlos y probarlos fácilmente.
RESPONSABLE: Coordinación (integrante 1)
"""
import numpy as np
import pandas as pd

from src.config import ALERTA_PP, META_RIESGO, MINIMO_SEGMENTO
from src.indicadores import marcar_riesgo, resumen_riesgo

# ---------------------------------------------------------------- Andrea
DIMENSIONES = {"Edad": "Grupo_Edad", "País": "Country", "Ciudad": "City", "Antigüedad": None}
ETIQUETAS_ANTIGUEDAD = ["Hasta 1 año", "1–3 años", "3–5 años", "Más de 5 años"]


def columna_segmento(df, dimension):
    """Serie con el segmento de cada cliente para la dimensión elegida."""
    if dimension == "Antigüedad":
        # Membership_Years viene en log(1 + x): se regresa a años con exp(x) − 1.
        anios = np.expm1(df["Membership_Years"])
        serie = pd.cut(anios, [-np.inf, 1, 3, 5, np.inf], labels=ETIQUETAS_ANTIGUEDAD).astype(str)
    else:
        serie = df[DIMENSIONES[dimension]].astype(str)
    return serie.rename("segmento")


def churn_por_segmento(df, dimension, minimo=MINIMO_SEGMENTO):
    """Clientes, abandonos y tasa de churn por segmento (solo grupos con `minimo` clientes o más)."""
    columnas = ["segmento", "clientes", "abandonaron", "tasa"]
    if df.empty:
        return pd.DataFrame(columns=columnas)
    tabla = (df.groupby(columna_segmento(df, dimension), observed=True)["Churned"]
               .agg(clientes="size", abandonaron="sum").reset_index())
    tabla["tasa"] = tabla["abandonaron"] / tabla["clientes"]
    tabla = tabla[tabla["clientes"] >= minimo]
    return tabla.sort_values("tasa", ascending=False).reset_index(drop=True)[columnas]


# ---------------------------------------------------------------- Luis
COLUMNAS_DERIVADAS = {"Dias_Sin_Comprar", "Grupo_Edad"}


def calidad_datos(df):
    """Revisión básica: nulos, IDs duplicados y valores fuera de rango."""
    originales = [c for c in df.columns if c not in COLUMNAS_DERIVADAS]
    base = df[originales]
    texto = base.select_dtypes(exclude="number")
    nulos = int(base.isna().sum().sum() + texto.isin(["", "nan", "None"]).sum().sum())
    duplicados = int(df["Customer_ID"].duplicated().sum())
    invalidos = int((
        ~df["Age"].between(0, 120)
        | ~df["Churned"].isin([0, 1])
        | ~df["Cart_Abandonment_Rate"].between(0, 100)
        | (df["Customer_Service_Calls"] < 0)
    ).sum())
    return {"registros": len(df), "variables": len(originales), "nulos": nulos,
            "duplicados": duplicados, "invalidos": invalidos}


def alertas(tasa_seleccion, tasa_global, riesgo, calidad):
    """Lista de alertas con su estado (encendida o no) y el motivo."""
    umbral = tasa_global + ALERTA_PP
    return [
        {"titulo": f"Churn supera la línea base +{ALERTA_PP * 100:.0f} pts",
         "encendida": bool(tasa_seleccion > umbral),
         "motivo": f"{tasa_seleccion:.1%} frente al umbral de {umbral:.1%}"},
        {"titulo": f"Activos en perfil de riesgo en {META_RIESGO:.0%} o más",
         "encendida": bool(riesgo["total_activos"] > 0 and riesgo["pct_activos"] >= META_RIESGO),
         "motivo": f"{riesgo['pct_activos']:.1%} de los activos ({riesgo['activos_en_perfil']:,} clientes)"},
        {"titulo": "Calidad de los datos",
         "encendida": bool(calidad["nulos"] or calidad["duplicados"] or calidad["invalidos"]),
         "motivo": (f"{calidad['nulos']:,} nulos · {calidad['duplicados']:,} IDs duplicados · "
                    f"{calidad['invalidos']:,} valores fuera de rango")},
    ]


COLUMNAS_LISTA = {
    "Customer_ID": "ID", "Country": "País", "City": "Ciudad", "Age": "Edad",
    "Cart_Abandonment_Rate": "Carrito abandonado (%)", "Customer_Service_Calls": "Llamadas",
    "Dias_Sin_Comprar": "Días sin comprar", "Login_Frequency": "Inicios de sesión",
    "Lifetime_Value": "LTV (escala CSV)",
}


def tabla_clientes(df, regla, solo_riesgo=True, buscar=""):
    """Clientes para la lista de campaña. Con `solo_riesgo`, solo activos que cumplen la regla."""
    datos = df
    if solo_riesgo:
        datos = datos[(datos["Churned"] == 0) & marcar_riesgo(datos, regla)]
    if buscar:
        texto = buscar.strip().lower()
        coincide = (datos["Customer_ID"].str.lower().str.contains(texto, regex=False)
                    | datos["Country"].str.lower().str.contains(texto, regex=False)
                    | datos["City"].str.lower().str.contains(texto, regex=False))
        datos = datos[coincide]
    tabla = datos[list(COLUMNAS_LISTA)].rename(columns=COLUMNAS_LISTA)
    tabla["Estado"] = np.where(datos["Churned"] == 1, "Abandonó", "Activo")
    return tabla.reset_index(drop=True)


DEFINICIONES = pd.DataFrame([
    ["Customer_ID", "Identificador único del cliente", "Texto", "Sin unidad"],
    ["Age", "Edad del cliente", "Numérica", "Años"],
    ["Gender", "Género registrado", "Categoría", "—"],
    ["Country", "País del cliente", "Categoría", "—"],
    ["City", "Ciudad del cliente", "Categoría", "—"],
    ["Membership_Years", "Antigüedad de la membresía", "Numérica", "log(1 + años); años = exp(x) − 1"],
    ["Login_Frequency", "Inicios de sesión registrados", "Numérica", "Conteo"],
    ["Session_Duration_Avg", "Duración promedio de la sesión", "Numérica", "Unidad no documentada"],
    ["Pages_Per_Session", "Páginas promedio por sesión", "Numérica", "Páginas"],
    ["Cart_Abandonment_Rate", "Porcentaje de carritos abandonados", "Numérica", "%"],
    ["Wishlist_Items", "Productos en lista de deseos", "Numérica", "log(1 + x)"],
    ["Total_Purchases", "Total de compras", "Numérica", "log(1 + x)"],
    ["Average_Order_Value", "Valor promedio del pedido", "Numérica", "log(1 + x); sin moneda"],
    ["Days_Since_Last_Purchase", "Días desde la última compra", "Numérica", "log(1 + días); la app usa Dias_Sin_Comprar"],
    ["Discount_Usage_Rate", "Uso de descuentos", "Numérica", "%"],
    ["Returns_Rate", "Tasa de devoluciones", "Numérica", "log(1 + x)"],
    ["Email_Open_Rate", "Apertura de correos", "Numérica", "%"],
    ["Customer_Service_Calls", "Llamadas a servicio al cliente", "Numérica", "Conteo"],
    ["Product_Reviews_Written", "Reseñas escritas", "Numérica", "log(1 + x)"],
    ["Social_Media_Engagement_Score", "Interacción en redes sociales", "Numérica", "Puntaje"],
    ["Mobile_App_Usage", "Uso de la app móvil", "Numérica", "Unidad no documentada"],
    ["Payment_Method_Diversity", "Métodos de pago distintos", "Numérica", "Conteo"],
    ["Lifetime_Value", "Valor de vida del cliente (LTV)", "Numérica", "log(1 + x); sin moneda"],
    ["Credit_Balance", "Saldo de crédito", "Numérica", "Moneda no documentada"],
    ["Signup_Quarter", "Trimestre de registro", "Categoría", "Q1–Q4, sin año"],
    ["Churned", "Abandono del cliente", "Binaria", "0 = activo; 1 = abandonó"],
    ["Dias_Sin_Comprar (derivada)", "Días sin comprar en escala original", "Numérica", "Días"],
    ["Grupo_Edad (derivada)", "Rango de edad para filtros", "Categoría", "18–29, 30–44, 45–59, 60–80"],
], columns=["Variable", "Descripción", "Tipo", "Unidad"])


# ---------------------------------------------------------------- Carlos
ETIQUETAS_LTV = ["Q1 · valor bajo", "Q2", "Q3", "Q4 · valor alto"]


def cuartiles_ltv(df, df_general):
    """Churn por cuartil de Lifetime_Value. Los cortes salen de la base completa
    para que los cuartiles no cambien al filtrar."""
    _, cortes = pd.qcut(df_general["Lifetime_Value"], 4, retbins=True)
    cortes[0], cortes[-1] = -np.inf, np.inf
    cuartil = pd.cut(df["Lifetime_Value"], cortes, labels=ETIQUETAS_LTV).rename("cuartil")
    tabla = (df.groupby(cuartil, observed=False)
               .agg(clientes=("Churned", "size"), abandonaron=("Churned", "sum"),
                    mediana_ltv=("Lifetime_Value", "median"))
               .reset_index())
    tabla["activos"] = tabla["clientes"] - tabla["abandonaron"]
    tabla["tasa"] = (tabla["abandonaron"] / tabla["clientes"].replace(0, np.nan)).fillna(0)
    return tabla


def valor_por_pais(df, regla, minimo=MINIMO_SEGMENTO):
    """Tamaño, churn, mediana de LTV y activos en riesgo por país."""
    columnas = ["País", "Clientes", "Churn", "Mediana LTV", "Activos en riesgo"]
    if df.empty:
        return pd.DataFrame(columns=columnas)
    datos = df.assign(en_riesgo=(df["Churned"] == 0) & marcar_riesgo(df, regla))
    tabla = (datos.groupby("Country")
               .agg(Clientes=("Churned", "size"), Churn=("Churned", "mean"),
                    **{"Mediana LTV": ("Lifetime_Value", "median"),
                       "Activos en riesgo": ("en_riesgo", "sum")})
               .reset_index().rename(columns={"Country": "País"}))
    tabla = tabla[tabla["Clientes"] >= minimo]
    return tabla.sort_values("Churn", ascending=False).reset_index(drop=True)[columnas]


def escenario(clientes, puntos):
    """Clientes equivalentes a bajar el churn `puntos` puntos porcentuales.
    Es aritmética simple, no un pronóstico del efecto de una campaña."""
    return round(clientes * puntos / 100)


def resumen_carlos(df, regla):
    r = resumen_riesgo(df, regla)
    return {"clientes": len(df), "tasa": float(df["Churned"].mean()) if len(df) else 0.0,
            "mediana_ltv": float(df["Lifetime_Value"].median()) if len(df) else float("nan"),
            "activos_en_riesgo": r["activos_en_perfil"]}
