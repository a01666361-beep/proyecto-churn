"""
Carga y limpieza de datos (viene de la Evidencia 1).
RESPONSABLE: Integrante 2

QUÉ FALTA (TODO):
- Revisar que las funciones sean iguales a las del Colab Equipo5_EDA_final.ipynb.
- Si en el Colab hay más pasos de limpieza que queramos en la app, agregarlos aquí.
"""
import numpy as np
import pandas as pd

COLUMNAS_TEXTO = ["Customer_ID", "Gender", "Country", "City", "Signup_Quarter"]


def convertir_numeros(df):
    """Convierte las columnas con coma decimal ("27,4") a número (27.4)."""
    df = df.copy()
    for col in df.columns:
        if col not in COLUMNAS_TEXTO:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ".", regex=False))
    return df


def limpiar_texto(df):
    """Quita espacios y unifica mayúsculas en las columnas de texto."""
    df = df.copy()
    for col in COLUMNAS_TEXTO:
        df[col] = df[col].astype(str).str.strip()
    for col in ["Gender", "Country", "City"]:
        df[col] = df[col].str.title()
    # "Usa" / "Uk" deben quedar en mayúsculas
    df["Country"] = df["Country"].replace({"Usa": "USA", "Uk": "UK"})
    df["Signup_Quarter"] = df["Signup_Quarter"].str.upper()
    return df


def agregar_variables(df):
    """Crea las variables interpretables (la base guarda algunas en log(1 + x))."""
    df = df.copy()
    df["Dias_Sin_Comprar"] = np.expm1(df["Days_Since_Last_Purchase"]).round().astype(int)
    df["Grupo_Edad"] = pd.cut(
        df["Age"],
        bins=[17, 29, 44, 59, 80],
        labels=["18–29", "30–44", "45–59", "60–80"],
    ).astype(str)
    return df


def cargar_datos(ruta):
    """Lee el CSV y aplica toda la limpieza. Devuelve el DataFrame listo."""
    df = pd.read_csv(ruta, dtype=str)
    df = convertir_numeros(df)
    df = limpiar_texto(df)
    df = agregar_variables(df)
    return df
