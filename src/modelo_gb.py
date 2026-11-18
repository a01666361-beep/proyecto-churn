"""
Modelo campeón (Gradient Boosting) y comparativa de modelos de clasificación.
Solo pandas y scikit-learn, sin Streamlit, para poder probarlo fácilmente.
RESPONSABLE: Arlen Martínez (A01666361)

De dónde sale cada cosa (ver notebooks/Equipo5_Comparacion_Modelos.ipynb):
- Variables: las 11 del modelo final de SAS (10 numéricas + City); las demás columnas no se usan.
- Datos: train 80% limpio (versión A v2) y test 20% sin imputar, los dos con log(x+1) en 8 variables
  (data/modelos/train_log.csv y test_log.csv, coma decimal). Son los mismos archivos que se subieron a SAS.
- El modelo se entrena con el 70% del train (30% validación, 0% test), igual que en SAS Model Studio,
  con los mismos parámetros y la misma semilla que el notebook. Se entrena al abrir el dashboard (unos
  segundos) para no depender de la versión de scikit-learn con la que se hubiera guardado un .pkl.
- comparativa_modelos.csv, roc_modelos.csv e importancia_gb.csv son salidas del notebook: métricas de los
  cinco modelos (árbol, bosque, red neuronal, regresión logística y gradient boosting).
- Regla de decisión (Intelligent Decisioning): probabilidad de churn > 0.5 → campaña "No te vayas".
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import CARPETA_PROYECTO

CARPETA = CARPETA_PROYECTO / "data" / "modelos"
RUTA_TRAIN = CARPETA / "train_log.csv"
RUTA_TEST = CARPETA / "test_log.csv"

SEMILLA = 0
CORTE = 0.5
CAMPANA = "Enviar campaña \"No te vayas\""
SIN_ACCION = "No hacer nada"

OBJETIVO = "Churned"
# Las 11 variables del modelo final de SAS (después de quitar 8 y luego 5 por baja importancia).
NUMERICAS = ["log_Lifetime_Value", "Cart_Abandonment_Rate", "Customer_Service_Calls", "Discount_Usage_Rate",
             "log_Days_Since_Last_Purchase", "Age", "Email_Open_Rate", "log_Total_Purchases", "log_Returns_Rate",
             "Pages_Per_Session"]
CATEGORICAS = ["City"]
VARIABLES_LOG = [c for c in NUMERICAS if c.startswith("log_")]

# Orden de los modelos en tablas y gráficas (del campeón al de menor AUC en el notebook)
MODELOS = ["Gradient Boosting", "Bosque aleatorio", "Red neuronal", "Árbol de decisión", "Regresión logística"]
CAMPEON = "Gradient Boosting"

# Cómo se capturan las variables en la pantalla (escala original, sin log), en orden de importancia.
# (etiqueta, es entero). Las que tienen log en el modelo se transforman solas al predecir.
CAMPOS = {
    "Lifetime_Value": ("Valor de vida del cliente (sin moneda documentada)", False),
    "Customer_Service_Calls": ("Llamadas a servicio al cliente", True),
    "Age": ("Edad (años)", True),
    "Cart_Abandonment_Rate": ("Carrito abandonado (%)", False),
    "Discount_Usage_Rate": ("Uso de descuentos (%)", False),
    "Days_Since_Last_Purchase": ("Días desde la última compra", True),
    "Email_Open_Rate": ("Apertura de correos (%)", False),
    "Total_Purchases": ("Compras totales", True),
    "Returns_Rate": ("Tasa de devoluciones", False),
    "Pages_Per_Session": ("Páginas por sesión", False),
}
NOMBRES_CATEGORICAS = {"City": "Ciudad"}


def leer(ruta):
    return pd.read_csv(ruta, decimal=",")


def numericas(df=None):
    """Variables numéricas del modelo (las mismas para cualquier archivo: train o test)."""
    return list(NUMERICAS)


def entrenar(train=None):
    """Gradient Boosting igual al del notebook: mismo 70/30, mismos parámetros y misma semilla."""
    train = leer(RUTA_TRAIN) if train is None else train
    columnas = numericas(train) + CATEGORICAS
    X_ent, X_val, y_ent, y_val = train_test_split(train[columnas], train[OBJETIVO], test_size=0.30,
                                                  stratify=train[OBJETIVO], random_state=SEMILLA)
    modelo = Pipeline([
        ("prep", ColumnTransformer([
            ("num", "passthrough", numericas(train)),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAS)])),
        ("modelo", HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31,
                                                  early_stopping=True, random_state=SEMILLA)),
    ])
    modelo.fit(X_ent, y_ent)
    return modelo


def opciones_y_rangos(train):
    """Valores para el formulario, calculados con train y regresados a la escala original."""
    rangos = {}
    for col in numericas(train):
        original = col.replace("log_", "")
        valores = np.expm1(train[col]) if col in VARIABLES_LOG else train[col]
        rangos[original] = {"min": float(valores.min()), "max": float(valores.max()),
                            "mediana": float(valores.median())}
    opciones = {c: sorted(train[c].dropna().unique().tolist()) for c in CATEGORICAS}
    moda = {c: train[c].mode()[0] for c in CATEGORICAS}
    return rangos, opciones, moda


def preparar_cliente(datos, columnas_num):
    """Diccionario en escala original → fila con las columnas que espera el modelo (log(x+1) en 8 variables).

    Un dato que falta (None) se queda vacío: el Gradient Boosting sabe a qué rama mandarlo y no se rellena.
    """
    fila = {}
    for col in columnas_num + CATEGORICAS:
        valor = datos.get(col.replace("log_", ""))
        if col in VARIABLES_LOG and valor is not None:
            if valor < 0:
                raise ValueError(f"{col.replace('log_', '')} no puede ser negativo")
            valor = float(np.log1p(valor))
        fila[col] = np.nan if valor is None else valor
    return pd.DataFrame([fila])


def predecir(modelo, datos, columnas_num, corte=CORTE):
    """Probabilidad de churn del Gradient Boosting y decisión de la regla (> corte → campaña)."""
    fila = preparar_cliente(datos, columnas_num)
    prob = float(modelo.predict_proba(fila)[:, 1][0])
    return {"probabilidad": prob, "decision": CAMPANA if prob > corte else SIN_ACCION, "fila_modelo": fila}


def comparativa():
    """Métricas de los cinco modelos en validación y test (salida del notebook)."""
    return pd.read_csv(CARPETA / "comparativa_modelos.csv")


def roc():
    """Puntos de la curva ROC de cada modelo en test (salida del notebook)."""
    return pd.read_csv(CARPETA / "roc_modelos.csv")


def importancia():
    """Importancia por permutación del Gradient Boosting en validación (salida del notebook)."""
    return pd.read_csv(CARPETA / "importancia_gb.csv")
