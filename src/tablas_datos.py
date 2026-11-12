"""Columnas ordenadas, origen de cada valor y formatos en tablas Streamlit."""
import pandas as pd
import streamlit as st
from pandas.api.types import is_numeric_dtype
from src.contrato_datos import CAMPOS

# Etiquetas que las páginas dan a las variables del CSV o a sus resultados.
EQUIVALENCIAS = {
    "ID": "Customer_ID", "Cliente": "Customer_ID", "País": "Country",
    "Ciudad": "City", "Edad": "Age", "Carrito abandonado (%)": "Cart_Abandonment_Rate",
    "Llamadas": "Customer_Service_Calls", "Llamadas a servicio": "Customer_Service_Calls",
    "Días sin comprar": "Dias_Sin_Comprar", "Inicios de sesión": "Login_Frequency",
    "LTV (escala CSV)": "Lifetime_Value", "Mediana LTV": "Lifetime_Value",
    "Saldo de crédito": "Credit_Balance",
}
DEL_MODELO = {"Probabilidad de churn (%)", "Probabilidad promedio (%)", "Nivel de riesgo", "Segmento"}
SIMULADOS = {"Clientes que se retendrían", "De ellos, de valor alto (Q4)"}


def procedencia(columna):
    campo = CAMPOS.get(columna) or CAMPOS.get(EQUIVALENCIAS.get(columna))
    if campo:
        return f"{campo.origen}; unidad: {campo.unidad}"
    if columna in DEL_MODELO:
        return "Resultado del modelo predictivo o de agrupamiento; no es dato observado"
    if columna in SIMULADOS:
        return "Simulación hipotética, no es dato observado ni pronóstico validado"
    if columna in {"Estado", "Nivel de riesgo", "Prioridad", "Churn", "Churn histórico (%)",
                   "Clientes", "Activos", "Activos en riesgo", "Abandonaron", "abandonaron",
                   "clientes", "tasa", "Probabilidad", "Grupos (k)", "Silueta", "Cuartil"}:
        return "Calculado o clasificado a partir del CSV; no es un campo original"
    return "Origen por confirmar; consultar contrato-datos.md"


def configuracion_columnas(df):
    """Añade el origen al tooltip de TODAS las columnas del dataframe."""
    config = {}
    for nombre in df.columns:
        ayuda = "Origen: " + procedencia(nombre)
        if is_numeric_dtype(df[nombre]):
            formato = "%.3f" if nombre in {"LTV (escala CSV)", "Mediana LTV"} else None
            if nombre == "Carrito abandonado (%)":
                formato = "%.1f"
            parametros = {"help": ayuda}
            if formato:
                parametros["format"] = formato
            config[nombre] = st.column_config.NumberColumn(nombre, **parametros)
        else:
            config[nombre] = st.column_config.TextColumn(nombre, help=ayuda)
    return config
