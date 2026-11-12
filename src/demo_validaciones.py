"""Ejemplos de contrato de datos para una demostración didáctica segura.

Las modificaciones se hacen exclusivamente sobre tres registros COPIADOS EN MEMORIA.
No altera el CSV del repositorio, las métricas ni los filtros del dashboard.
La comprobación usa las mismas funciones productivas que la carga real.
"""

import pandas as pd

from src.contrato_datos import CAMPOS_ORIGEN, ErrorContrato, validar_origen, validar_procesado
from src.limpieza import agregar_variables, convertir_numeros, limpiar_texto

CASOS = {
    "texto": "Saldo con texto (debería ser numérico)",
    "vacio": "Saldo sin dato (celda vacía)",
    "duplicado": "Identificador de cliente duplicado",
    "rango": "Edad fuera de rango (150 años)",
}


def crear_demostracion(df: pd.DataFrame, caso: str) -> dict:
    """Ejecuta un error hipotético contra las validaciones reales, sin tocar ``df``.

    Devuelve datos para mostrar una etiqueta inequívoca de DEMOSTRACIÓN,
    el cambio realizado y el error real que emitió la función de validación.
    """
    if caso not in CASOS:
        raise ValueError(f"Escenario de demostración desconocido: {caso}")
    if len(df) < 2:
        raise ValueError("Se necesitan al menos dos filas para mostrar la demostración")

    muestra = df.loc[:, list(CAMPOS_ORIGEN)].head(3).copy(deep=True).reset_index(drop=True)
    if caso == "texto":
        fila, campo, nuevo = 0, "Credit_Balance", "MIL PESOS"
    elif caso == "vacio":
        fila, campo, nuevo = 0, "Credit_Balance", ""
    elif caso == "duplicado":
        fila, campo, nuevo = 1, "Customer_ID", str(muestra.loc[0, "Customer_ID"])
    else:
        fila, campo, nuevo = 0, "Age", 150

    original = muestra.loc[fila, campo]
    muestra[campo] = muestra[campo].astype(object)
    muestra.at[fila, campo] = nuevo

    error = None
    try:
        validar_origen(muestra)
        # Para la edad 150, la comprobación de límites opera DESPUÉS
        # de convertir tipos y generar las columnas derivadas.
        procesada = agregar_variables(limpiar_texto(convertir_numeros(muestra)))
        validar_procesado(procesada)
    except ErrorContrato as exc:
        error = str(exc)

    detalle = pd.DataFrame([{
        "Fila de muestra": fila + 1,
        "Columna": campo,
        "Valor original": str(original),
        "Valor simulado": repr(nuevo) if nuevo == "" else str(nuevo),
        "Resultado": "Rechazado" if error else "No rechazado",
    }])
    return {
        "escenario": CASOS[caso],
        "mensaje": error,
        "bloqueado": bool(error),
        "detalle": detalle,
    }
