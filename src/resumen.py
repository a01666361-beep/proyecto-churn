"""
Cálculos de las pantallas de resumen general y de recomendaciones finales.
Solo pandas, sin Streamlit, para poder revisarlos y probarlos fácilmente.
RESPONSABLE: Coordinación (integrante 1)

Todo se calcula con la selección de los filtros y la regla de riesgo vigente,
así que los textos de ambas pantallas cambian cuando se cambian los filtros.
"""
import pandas as pd

from src.config import META_CHURN, META_RIESGO
from src.indicadores import marcar_riesgo, resumen_riesgo, tasa_churn
from src.vistas import churn_por_segmento, cuartiles_ltv

DIAS_REACTIVAR = 60  # a partir de cuántos días sin comprar se propone una campaña de reactivación


def _comparar(df, condicion):
    """Churn de los clientes que cumplen la condición contra los que no, y activos que la cumplen."""
    dentro, fuera = df[condicion], df[~condicion]
    return {
        "tasa_dentro": tasa_churn(dentro),
        "tasa_fuera": tasa_churn(fuera),
        "clientes": len(dentro),
        "activos": int((dentro["Churned"] == 0).sum()),
    }


def situacion(df, regla):
    """Números de la situación general de la selección."""
    r = resumen_riesgo(df, regla)
    return {
        "clientes": len(df),
        "abandonaron": int(df["Churned"].sum()),
        "activos": r["total_activos"],
        "tasa": tasa_churn(df),
        "meta_churn": META_CHURN,
        "riesgo": r,
        "meta_riesgo": META_RIESGO,
    }


def factores(df, regla):
    """Churn dentro y fuera de cada condición de riesgo (llamadas, carrito y días sin comprar)."""
    return {
        "llamadas": _comparar(df, df["Customer_Service_Calls"] >= regla["llamadas_min"]),
        "carrito": _comparar(df, df["Cart_Abandonment_Rate"] > regla["carrito_min"]),
        "dias": _comparar(df, df["Dias_Sin_Comprar"] > DIAS_REACTIVAR),
        "perfil": _comparar(df, marcar_riesgo(df, regla)),
    }


def segmento_critico(df, dimensiones=("Edad", "País", "Antigüedad")):
    """El segmento con más churn entre las dimensiones dadas (solo segmentos con MINIMO_SEGMENTO clientes)."""
    mejor = None
    for dimension in dimensiones:
        tabla = churn_por_segmento(df, dimension)
        if tabla.empty:
            continue
        fila = tabla.iloc[0]
        if mejor is None or fila["tasa"] > mejor["tasa"]:
            mejor = {"dimension": dimension, "segmento": fila["segmento"], "tasa": float(fila["tasa"]),
                     "clientes": int(fila["clientes"]),
                     "activos": int(fila["clientes"] - fila["abandonaron"])}
    return mejor


def valor_alto(df, df_general):
    """Churn y activos del cuartil de mayor Lifetime_Value (Q4) contra el de los cuartiles intermedios."""
    cuartiles = cuartiles_ltv(df, df_general)
    q4 = cuartiles.iloc[-1]
    medios = cuartiles.iloc[1:3]
    clientes_medios = medios["clientes"].sum()
    return {
        "tasa_q4": float(q4["tasa"]),
        "activos_q4": int(q4["activos"]),
        "clientes_q4": int(q4["clientes"]),
        "tasa_medios": float(medios["abandonaron"].sum() / clientes_medios) if clientes_medios else 0.0,
    }


def recomendaciones(df, df_general, regla):
    """Lista de recomendaciones ordenadas por prioridad, cada una con su dato de respaldo.

    Cada recomendación trae: titulo, accion, por_que, a_quien (activos), medir y pantalla.
    Solo se incluyen las que tienen clientes activos a quién dirigirse.
    """
    if df.empty:
        return []
    f = factores(df, regla)
    lista = []

    p = f["perfil"]
    lista.append({
        "titulo": "Contactar primero a los activos en perfil de riesgo",
        "accion": ("Usar la lista de la pantalla 02 (pestaña Datos) para una campaña de retención directa: "
                   "llamada o correo personalizado y una oferta para recuperar el carrito."),
        "por_que": (f"Cumplen carrito > {regla['carrito_min']:.2f}% y {regla['llamadas_min']}+ llamadas. "
                    f"En este perfil abandonó el {p['tasa_dentro']:.1%} de los clientes, contra "
                    f"{p['tasa_fuera']:.1%} del resto."),
        "a_quien": p["activos"],
        "medir": f"% de activos en perfil de riesgo: bajar de la situación actual a menos de {META_RIESGO:.0%}.",
        "pantalla": "02 · Alertas y calidad",
    })

    ll = f["llamadas"]
    lista.append({
        "titulo": "Resolver el problema antes de que el cliente llame muchas veces",
        "accion": (f"Crear una alerta en servicio al cliente cuando un cliente llegue a {regla['llamadas_min']} llamadas, "
                   "para que lo atienda un supervisor y se resuelva su caso en ese contacto."),
        "por_que": (f"Con {regla['llamadas_min']} o más llamadas abandonó el {ll['tasa_dentro']:.1%}, contra "
                    f"{ll['tasa_fuera']:.1%} con menos llamadas."),
        "a_quien": ll["activos"],
        "medir": "Churn y número de llamadas de los clientes que entren a la alerta, contra los que no.",
        "pantalla": "01 · Priorizar campañas (mapa de calor)",
    })

    ca = f["carrito"]
    lista.append({
        "titulo": "Recuperar a quienes abandonan el carrito con frecuencia",
        "accion": ("Enviar recordatorios automáticos del carrito y revisar el proceso de pago "
                   "(costos de envío, pasos y métodos de pago) donde se pierde la compra."),
        "por_que": (f"Con carrito abandonado > {regla['carrito_min']:.2f}% abandonó el {ca['tasa_dentro']:.1%}, "
                    f"contra {ca['tasa_fuera']:.1%} del resto."),
        "a_quien": ca["activos"],
        "medir": "Tasa de carrito abandonado y churn de este grupo antes y después de la campaña.",
        "pantalla": "01 · Priorizar campañas (mapa de calor)",
    })

    di = f["dias"]
    lista.append({
        "titulo": f"Reactivar a los clientes con más de {DIAS_REACTIVAR} días sin comprar",
        "accion": "Campaña de reactivación con un beneficio por tiempo limitado antes de que el cliente se pierda.",
        "por_que": (f"Con más de {DIAS_REACTIVAR} días sin comprar abandonó el {di['tasa_dentro']:.1%}, contra "
                    f"{di['tasa_fuera']:.1%} de quienes compraron más recientemente."),
        "a_quien": di["activos"],
        "medir": f"% de clientes que vuelve a comprar después de la campaña y churn de quienes pasan de {DIAS_REACTIVAR} días.",
        "pantalla": "01 · Priorizar campañas (comportamientos relacionados)",
    })

    seg = segmento_critico(df)
    tasa = tasa_churn(df)
    if seg and seg["tasa"] > tasa:
        lista.append({
            "titulo": f"Diseñar una campaña específica para el segmento {seg['segmento']}",
            "accion": (f"Adaptar el mensaje y el canal al segmento con más abandono ({seg['dimension'].lower()}: "
                       f"{seg['segmento']}) en lugar de usar una sola campaña para todos."),
            "por_que": (f"Es el segmento con más churn: {seg['tasa']:.1%}, contra {tasa:.1%} de la selección "
                        f"({seg['clientes']:,} clientes)."),
            "a_quien": seg["activos"],
            "medir": f"Churn del segmento {seg['segmento']} contra el de la selección.",
            "pantalla": "01 · Priorizar campañas (segmentos)",
        })

    va = valor_alto(df, df_general)
    if va["tasa_q4"] > va["tasa_medios"]:
        lista.append({
            "titulo": "Proteger a los clientes de mayor valor",
            "accion": ("Dar atención preferente a los activos del cuartil más alto de Lifetime_Value (Q4): "
                       "ellos van primero cuando haya que decidir a quién contactar con presupuesto limitado."),
            "por_que": (f"El cuartil de valor alto abandona {va['tasa_q4']:.1%}, contra {va['tasa_medios']:.1%} "
                        "de los cuartiles intermedios (Q2 y Q3)."),
            "a_quien": va["activos_q4"],
            "medir": "Churn del cuartil Q4 de Lifetime_Value.",
            "pantalla": "03 · Valor y presupuesto",
        })

    return [r for r in lista if r["a_quien"] > 0]


def tabla_recomendaciones(lista):
    """Tabla resumen para la parte de arriba de la pantalla de recomendaciones."""
    return pd.DataFrame([{"Prioridad": i, "Acción": r["titulo"], "Activos a contactar": r["a_quien"],
                          "Dónde verlo": r["pantalla"]} for i, r in enumerate(lista, 1)])
