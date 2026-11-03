"""
Cálculo de los indicadores (KPI). Aquí NO va nada de Streamlit, solo pandas,
para que los números se puedan revisar fácilmente.
RESPONSABLE: Coordinación (integrante 1)
"""
import pandas as pd

from src.config import NOMBRES, RANGOS


def tasa_churn(df):
    """Proporción de clientes con Churned = 1."""
    if len(df) == 0:
        return 0.0
    return df["Churned"].mean()


def marcar_riesgo(df, regla):
    """True para los clientes que cumplen AMBOS criterios de la regla."""
    return (df["Cart_Abandonment_Rate"] > regla["carrito_min"]) & (
        df["Customer_Service_Calls"] >= regla["llamadas_min"]
    )


def resumen_riesgo(df, regla):
    """Datos del perfil de alto riesgo.

    - activos_en_perfil: clientes ACTIVOS (Churned = 0) que cumplen la regla
    - pct_activos: activos_en_perfil / total de activos
    - tasa_historica: churn de TODOS los clientes (activos y no) que cumplen la regla
    """
    en_perfil = marcar_riesgo(df, regla)
    activos = df["Churned"] == 0
    n_activos = int(activos.sum())
    activos_en_perfil = int((en_perfil & activos).sum())
    return {
        "activos_en_perfil": activos_en_perfil,
        "total_activos": n_activos,
        "pct_activos": activos_en_perfil / n_activos if n_activos else 0.0,
        "tasa_historica": float(df.loc[en_perfil, "Churned"].mean()) if en_perfil.any() else 0.0,
        "clientes_en_perfil": int(en_perfil.sum()),
    }


def rango(df, columna):
    """Agrupa una variable clave en sus rangos definidos en config.RANGOS."""
    cortes, etiquetas = RANGOS[columna]
    return pd.cut(df[columna], bins=cortes, labels=etiquetas)


def tasa_por_rango(df, columna):
    """Tasa de churn y número de clientes por rango de una variable clave."""
    tabla = (
        df.groupby(rango(df, columna), observed=False)["Churned"]
        .agg(tasa="mean", clientes="size")
        .reset_index()
        .rename(columns={columna: "rango"})
    )
    tabla["tasa"] = tabla["tasa"].fillna(0)
    return tabla


def mapa_carrito_llamadas(df):
    """Tasa de churn y conteo para cada combinación carrito × llamadas."""
    filas = rango(df, "Cart_Abandonment_Rate")
    columnas = rango(df, "Customer_Service_Calls")
    tasa = df.pivot_table(index=filas, columns=columnas, values="Churned",
                          aggfunc="mean", observed=False)
    conteo = df.pivot_table(index=filas, columns=columnas, values="Churned",
                            aggfunc="size", observed=False)
    return tasa, conteo.fillna(0).astype(int)


def riesgo_por_pais(df, regla):
    """% de activos en perfil de riesgo por país."""
    activos = df[df["Churned"] == 0].copy()
    activos["en_perfil"] = marcar_riesgo(activos, regla)
    tabla = activos.groupby("Country")["en_perfil"].mean().sort_values()
    return tabla


def correlaciones(df):
    """Correlación de cada variable numérica con Churned (ordenada)."""
    columnas = [c for c in NOMBRES if c in df.columns]
    if len(df) < 3:
        return pd.Series(dtype=float)
    corr = df[columnas + ["Churned"]].corr()["Churned"].drop("Churned")
    return corr.sort_values()


def matriz_correlacion(df, n=8):
    """Matriz de correlación entre las n variables más relacionadas con el churn."""
    corr = correlaciones(df)
    top = corr.abs().sort_values(ascending=False).head(n).index.tolist()
    return df[top + ["Churned"]].corr()
