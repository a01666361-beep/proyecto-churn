"""
Cálculo de los indicadores (KPI). Aquí NO va nada de Streamlit, solo pandas,
para que los números se puedan revisar fácilmente.
RESPONSABLE: Coordinación (integrante 1)
"""
import pandas as pd


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
        "tasa_historica": df.loc[en_perfil, "Churned"].mean() if en_perfil.any() else 0.0,
        "clientes_en_perfil": int(en_perfil.sum()),
    }


def tasa_por_rango(df, columna, cortes, etiquetas):
    """Tasa de churn y número de clientes por rango de una variable."""
    rangos = pd.cut(df[columna], bins=cortes, labels=etiquetas)
    tabla = (
        df.groupby(rangos, observed=False)["Churned"]
        .agg(tasa="mean", clientes="size")
        .reset_index()
        .rename(columns={columna: "rango"})
    )
    tabla["tasa"] = tabla["tasa"].fillna(0)
    return tabla
