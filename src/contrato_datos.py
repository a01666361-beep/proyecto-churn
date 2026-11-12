"""Contrato verificable del CSV de clientes, independiente de Streamlit.

Los tipos, valores ausentes y reglas de negocio se definen aquí; las tablas
contractuales pueden documentarse sin depender de código de visualización.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


@dataclass(frozen=True)
class Campo:
    nombre: str
    tipo: str
    unidad: str
    origen: str
    ausencia: str


NULOS = frozenset({"", "NA", "N/A", "N/D", "NULL", "NONE", "NAN", "SIN DATO", "SIN DATOS", "NO DISPONIBLE", "NO APLICA", "-"})
AUSENCIA_DATO = "Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo"
AUSENCIA_ID = "Sin identificador no se puede rastrear al cliente; carga rechazada"
AUSENCIA_CHURN = "No se conoce si abandonó; no se supone 0; carga rechazada"
AUSENCIA_CALCULO = "No se puede calcular si falta el dato de origen; carga rechazada"


def _csv(nombre, tipo, unidad, ausencia=AUSENCIA_DATO):
    return Campo(nombre, tipo, unidad, "CSV original", ausencia)


ORIGINALES = (
    _csv("Customer_ID", "texto", "Identificador", AUSENCIA_ID),
    _csv("Age", "numérico", "años"),
    _csv("Gender", "texto", "categoría"),
    _csv("Country", "texto", "país"),
    _csv("City", "texto", "ciudad"),
    _csv("Membership_Years", "numérico", "log(1 + años)"),
    _csv("Login_Frequency", "numérico", "frecuencia, periodo no documentado"),
    _csv("Session_Duration_Avg", "numérico", "unidad no documentada"),
    _csv("Pages_Per_Session", "numérico", "páginas por sesión"),
    _csv("Cart_Abandonment_Rate", "numérico", "% (0–100)"),
    _csv("Wishlist_Items", "numérico", "log(1 + artículos)"),
    _csv("Total_Purchases", "numérico", "log(1 + compras)"),
    _csv("Average_Order_Value", "numérico", "log(1 + valor), moneda no documentada"),
    _csv("Days_Since_Last_Purchase", "numérico", "log(1 + días)"),
    _csv("Discount_Usage_Rate", "numérico", "% (0–100)"),
    _csv("Returns_Rate", "numérico", "log(1 + tasa), base no documentada"),
    _csv("Email_Open_Rate", "numérico", "% (0–100)"),
    _csv("Customer_Service_Calls", "numérico", "llamadas"),
    _csv("Product_Reviews_Written", "numérico", "log(1 + reseñas)"),
    _csv("Social_Media_Engagement_Score", "numérico", "puntos, escala no documentada"),
    _csv("Mobile_App_Usage", "numérico", "unidad no documentada"),
    _csv("Payment_Method_Diversity", "numérico", "número de métodos"),
    _csv("Lifetime_Value", "numérico", "log(1 + valor), moneda no documentada"),
    _csv("Credit_Balance", "numérico", "importe, moneda no documentada"),
    _csv("Signup_Quarter", "texto", "trimestre Q1–Q4"),
    _csv("Churned", "numérico", "indicador binario 0/1", AUSENCIA_CHURN),
)
DERIVADAS = (
    Campo("Dias_Sin_Comprar", "numérico", "días", "Calculada: expm1(Days_Since_Last_Purchase)", AUSENCIA_CALCULO),
    Campo("Grupo_Edad", "texto", "rango de edad", "Calculada: clasificación de Age", AUSENCIA_CALCULO),
)
CAMPOS = {c.nombre: c for c in (*ORIGINALES, *DERIVADAS)}
NUMERICAS = tuple(c.nombre for c in ORIGINALES if c.tipo == "numérico")
TEXTOS = tuple(c.nombre for c in ORIGINALES if c.tipo == "texto")
CAMPOS_ORIGEN = tuple(c.nombre for c in ORIGINALES)


class ErrorContrato(ValueError):
    """Un archivo o DataFrame infringe una regla obligatoria del contrato."""


def _es_nulo(serie):
    return serie.isna() | serie.astype("string").str.strip().str.upper().isin(NULOS).fillna(True)


def validar_origen(df):
    """Revisa el CSV **antes de convertir** valores o crear columnas derivadas.

    Retorna la cantidad de filas si cumple el contrato. Ante el primer conjunto
    de errores, falla explícitamente (no sustituye 'error' o vacío por cero).
    """
    errores = []
    faltantes = [c for c in CAMPOS_ORIGEN if c not in df]
    if faltantes:
        raise ErrorContrato("Columnas faltantes del CSV: " + ", ".join(faltantes))
    adicionales = [c for c in df.columns if c not in CAMPOS_ORIGEN]
    if adicionales:
        raise ErrorContrato("Columnas no documentadas en el contrato: " + ", ".join(adicionales))
    if df.empty:
        raise ErrorContrato("El archivo no contiene filas")

    for campo in ORIGINALES:
        nombre = campo.nombre
        serie = df[nombre]
        no_aplica = serie.astype("string").str.strip().str.upper().eq("NO APLICA").fillna(False)
        if no_aplica.any():
            errores.append(f"{nombre}: {int(no_aplica.sum())} valores 'No aplica' requieren revisión humana")
            continue
        ausentes = _es_nulo(serie)
        if ausentes.any():
            errores.append(f"{nombre}: {int(ausentes.sum())} valores sin dato")
            continue
        if campo.tipo == "numérico":
            convertida = pd.to_numeric(serie.astype(str).str.strip().str.replace(",", ".", regex=False), errors="coerce")
            invalidos = convertida.isna() | ~np.isfinite(convertida.to_numpy(dtype=float))
            if invalidos.any():
                ejemplo = str(serie[invalidos].iloc[0])[:35]
                errores.append(f"{nombre}: {int(invalidos.sum())} valores no numéricos, ej. {ejemplo!r}")
    if not _es_nulo(df["Customer_ID"]).any():
        duplicados = df["Customer_ID"].astype(str).str.strip().duplicated().sum()
        if duplicados:
            errores.append(f"Customer_ID: {int(duplicados)} identificadores duplicados")
    if errores:
        raise ErrorContrato(" | ".join(errores[:8]))
    return len(df)


def validar_procesado(df):
    """Verificación técnica de columnas y reglas al finalizar la limpieza.

    Se usa en la app y CI; el resultado también se presenta en una tabla de
    estado para que el usuario vea qué comprobó el sistema.
    """
    faltantes = [c for c in CAMPOS if c not in df]
    if faltantes:
        raise ErrorContrato("Faltan columnas del contrato: " + ", ".join(faltantes))
    errores = []
    for nombre, campo in CAMPOS.items():
        s = df[nombre]
        if campo.tipo == "numérico" and not is_numeric_dtype(s):
            errores.append(f"{nombre} tiene tipo {s.dtype}, debería ser numérico")
        if s.isna().any():
            errores.append(f"{nombre} contiene {int(s.isna().sum())} nulos")
        if campo.tipo == "numérico" and is_numeric_dtype(s) and not np.isfinite(s.to_numpy(dtype=float)).all():
            errores.append(f"{nombre} contiene valores infinitos")
    if df["Customer_ID"].astype(str).str.strip().duplicated().any():
        errores.append("Customer_ID contiene IDs duplicados")
    for nombre, minimo, maximo in [
        ("Age", 18, 80), ("Cart_Abandonment_Rate", 0, 100),
        ("Discount_Usage_Rate", 0, 100), ("Email_Open_Rate", 0, 100),
        ("Churned", 0, 1), ("Customer_Service_Calls", 0, None),
        ("Dias_Sin_Comprar", 0, None),
    ]:
        s = df[nombre]
        if not is_numeric_dtype(s):
            continue
        if minimo is not None and (s < minimo).any():
            errores.append(f"{nombre}: valores menores a {minimo}")
        if maximo is not None and (s > maximo).any():
            errores.append(f"{nombre}: valores mayores a {maximo}")
    if is_numeric_dtype(df["Churned"]) and not df["Churned"].isin([0, 1]).all():
        errores.append("Churned debe contener solamente 0 o 1")
    if not df["Grupo_Edad"].isin(["18–29", "30–44", "45–59", "60–80"]).all():
        errores.append("Grupo_Edad contiene grupos fuera del intervalo definido (18–80 años)")
    if errores:
        raise ErrorContrato(" | ".join(errores[:10]))
    return resumen_validacion(df)


def resumen_validacion(df):
    """DataFrame con resultado visible de tipo/unidad/procedencia por columna."""
    filas = []
    for campo in (*ORIGINALES, *DERIVADAS):
        if campo.nombre not in df:
            estado, dtype = "Falta", "—"
        else:
            s = df[campo.nombre]
            valido = (is_numeric_dtype(s) if campo.tipo == "numérico" else not is_numeric_dtype(s))
            valido = bool(valido and not s.isna().any())
            estado, dtype = ("Correcto" if valido else "Error"), str(s.dtype)
        filas.append({"Columna": campo.nombre, "Tipo esperado": campo.tipo,
                      "Tipo detectado": dtype, "Unidad": campo.unidad,
                      "Origen": campo.origen, "Resultado": estado})
    return pd.DataFrame(filas)
