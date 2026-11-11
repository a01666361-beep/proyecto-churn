"""
Modelo predictivo de churn (regresión logística), scoring de toda la base y segmentos (clusters).
Solo pandas y scikit-learn, sin Streamlit, para poder revisarlo y probarlo fácilmente.
RESPONSABLE: Sara Rivero

Decisiones documentadas (ver README, sección "Modelo predictivo"):
- Regresión logística con variables estandarizadas y class_weight="balanced": la base tiene 28.9% de
  churn y sin balancear el modelo detecta menos de la mitad de los clientes que se van.
- División 70/30 estratificada con random_state=0, igual que en las evidencias.
- Niveles de riesgo por probabilidad: Alto >= 0.70, Medio 0.40 a 0.70, Bajo < 0.40.
- Segmentos con K-Means (4 grupos) sobre variables de comportamiento estandarizadas.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score, silhouette_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ------------------------------------------------------------------ Variables
VARIABLES_NUMERICAS = [
    "Age", "Membership_Years", "Login_Frequency", "Session_Duration_Avg", "Pages_Per_Session",
    "Cart_Abandonment_Rate", "Wishlist_Items", "Total_Purchases", "Average_Order_Value",
    "Days_Since_Last_Purchase", "Discount_Usage_Rate", "Returns_Rate", "Email_Open_Rate",
    "Customer_Service_Calls", "Product_Reviews_Written", "Social_Media_Engagement_Score",
    "Mobile_App_Usage", "Payment_Method_Diversity", "Lifetime_Value", "Credit_Balance",
]
# City se deja fuera: tiene demasiadas categorías para el tamaño de cada una.
VARIABLES_CATEGORICAS = ["Gender", "Country", "Signup_Quarter"]

NOMBRES = {
    "Age": "Edad", "Membership_Years": "Años de membresía", "Login_Frequency": "Frecuencia de inicio de sesión",
    "Session_Duration_Avg": "Duración de sesión", "Pages_Per_Session": "Páginas por sesión",
    "Cart_Abandonment_Rate": "Carrito abandonado (%)", "Wishlist_Items": "Artículos en lista de deseos",
    "Total_Purchases": "Compras totales", "Average_Order_Value": "Ticket promedio",
    "Days_Since_Last_Purchase": "Días sin comprar", "Discount_Usage_Rate": "Uso de descuentos (%)",
    "Returns_Rate": "Devoluciones (%)", "Email_Open_Rate": "Apertura de correos (%)",
    "Customer_Service_Calls": "Llamadas a servicio", "Product_Reviews_Written": "Reseñas escritas",
    "Social_Media_Engagement_Score": "Interacción en redes", "Mobile_App_Usage": "Uso de la app",
    "Payment_Method_Diversity": "Métodos de pago", "Lifetime_Value": "Lifetime_Value",
    "Credit_Balance": "Saldo a favor", "Gender": "Género", "Country": "País", "Signup_Quarter": "Trimestre de alta",
}

UMBRAL_ALTO, UMBRAL_MEDIO = 0.70, 0.40
NIVELES = ["Alto", "Medio", "Bajo"]

# Variables de comportamiento para los segmentos (sin datos demográficos)
VARIABLES_SEGMENTO = [
    "Login_Frequency", "Session_Duration_Avg", "Pages_Per_Session", "Cart_Abandonment_Rate",
    "Total_Purchases", "Average_Order_Value", "Dias_Sin_Comprar", "Customer_Service_Calls",
    "Discount_Usage_Rate", "Lifetime_Value", "Email_Open_Rate", "Mobile_App_Usage",
]
NUM_SEGMENTOS = 4
# Nombres propuestos, del más activo al menos activo en la plataforma (se asignan por frecuencia de inicio
# de sesión, así no dependen del número que K-Means le da a cada grupo). El equipo puede cambiarlos aquí.
NOMBRES_SEGMENTO = ["Comprometidos", "Regulares", "En enfriamiento", "Desconectados"]
DESCRIPCION_SEGMENTO = {
    "Comprometidos": "Entran seguido, pasan más tiempo, abren correos y usan la app. Abandonan poco el carrito y llaman poco a servicio.",
    "Regulares": "Actividad media en todas las variables. Su comportamiento está cerca del promedio de la base.",
    "En enfriamiento": "Su actividad ya bajó: menos sesiones, poca apertura de correos, más carrito abandonado y más llamadas a servicio.",
    "Desconectados": "Casi no entran ni abren correos, abandonan la mayoría de sus carritos y son los que más llaman a servicio.",
}


# ------------------------------------------------------------------ Modelo
def _x(df):
    return df[VARIABLES_NUMERICAS + VARIABLES_CATEGORICAS]


def entrenar_modelo(df, random_state=0):
    """Entrena la regresión logística y regresa el modelo con sus métricas en el conjunto de prueba."""
    X, y = _x(df), df["Churned"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=random_state, stratify=y)

    modelo = Pipeline([
        ("preparacion", ColumnTransformer([
            ("numericas", StandardScaler(), VARIABLES_NUMERICAS),
            ("categoricas", OneHotEncoder(handle_unknown="ignore"), VARIABLES_CATEGORICAS),
        ])),
        ("regresion", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])
    modelo.fit(X_train, y_train)

    prob = modelo.predict_proba(X_test)[:, 1]
    pred = (prob >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    metricas = {
        "Accuracy": accuracy_score(y_test, pred),
        "Precisión": precision_score(y_test, pred),
        "Recall": recall_score(y_test, pred),
        "F1": f1_score(y_test, pred),
        "AUC": roc_auc_score(y_test, prob),
        # Línea base: decir siempre "no abandona"
        "Accuracy línea base": 1 - y_test.mean(),
    }
    matriz = {"VN": int(tn), "FP": int(fp), "FN": int(fn), "VP": int(tp)}
    return {"modelo": modelo, "metricas": metricas, "matriz": matriz,
            "n_train": len(X_train), "n_test": len(X_test)}


def coeficientes(modelo):
    """Coeficientes de la regresión (variables estandarizadas), del que más sube el churn al que más lo baja."""
    nombres = modelo.named_steps["preparacion"].get_feature_names_out()
    coef = modelo.named_steps["regresion"].coef_[0]
    tabla = pd.DataFrame({"variable_modelo": nombres, "Coeficiente": coef})

    def legible(v):
        tipo, nombre = v.split("__", 1)
        if tipo == "numericas":
            return NOMBRES.get(nombre, nombre)
        base = next(c for c in VARIABLES_CATEGORICAS if nombre.startswith(c + "_"))
        return f"{NOMBRES[base]}: {nombre[len(base) + 1:]}"

    tabla["Variable"] = tabla["variable_modelo"].map(legible)
    tabla["Efecto"] = np.where(tabla["Coeficiente"] > 0, "Aumenta el riesgo", "Reduce el riesgo")
    tabla["Razón de momios"] = np.exp(tabla["Coeficiente"])
    return tabla.sort_values("Coeficiente", ascending=False, key=abs).reset_index(drop=True)[
        ["Variable", "Coeficiente", "Razón de momios", "Efecto"]]


def nivel_riesgo(prob):
    return np.select([prob >= UMBRAL_ALTO, prob >= UMBRAL_MEDIO], ["Alto", "Medio"], "Bajo")


def puntuar(df, modelo):
    """Probabilidad de churn y nivel de riesgo para cada cliente de la base."""
    salida = df.copy()
    salida["Probabilidad"] = modelo.predict_proba(_x(df))[:, 1]
    salida["Nivel_Riesgo"] = nivel_riesgo(salida["Probabilidad"])
    return salida


def tabla_scoring(df_puntuado, solo_activos=True, niveles=None):
    """Tabla de clientes ordenada por probabilidad (de mayor a menor), lista para mostrar y descargar."""
    t = df_puntuado
    if solo_activos:
        t = t[t["Churned"] == 0]
    if niveles:
        t = t[t["Nivel_Riesgo"].isin(niveles)]
    t = t.sort_values("Probabilidad", ascending=False)
    tabla = pd.DataFrame({
        "Prioridad": range(1, len(t) + 1),
        "Cliente": t["Customer_ID"].values,
        "Probabilidad de churn (%)": (t["Probabilidad"] * 100).round(1).values,
        "Nivel de riesgo": t["Nivel_Riesgo"].values,
        "Segmento": t["Segmento"].values if "Segmento" in t else "",
        "País": t["Country"].values,
        "Edad": t["Age"].values,
        "Carrito abandonado (%)": t["Cart_Abandonment_Rate"].round(1).values,
        "Llamadas a servicio": t["Customer_Service_Calls"].round(0).astype(int).values,
        "Días sin comprar": t["Dias_Sin_Comprar"].values,
        "Estado": np.where(t["Churned"].values == 1, "Abandonó", "Activo"),
    })
    return tabla


def resumen_niveles(df_puntuado):
    """Clientes, activos y churn histórico por nivel de riesgo."""
    filas = []
    for nivel in NIVELES:
        g = df_puntuado[df_puntuado["Nivel_Riesgo"] == nivel]
        filas.append({"Nivel de riesgo": nivel, "Clientes": len(g),
                      "Activos": int((g["Churned"] == 0).sum()),
                      "Churn histórico (%)": round(g["Churned"].mean() * 100, 1) if len(g) else 0.0,
                      "Probabilidad promedio (%)": round(g["Probabilidad"].mean() * 100, 1) if len(g) else 0.0})
    return pd.DataFrame(filas)


# ------------------------------------------------------------------ Segmentos
def entrenar_segmentos(df, k=NUM_SEGMENTOS, random_state=0):
    """K-Means sobre variables de comportamiento estandarizadas. Regresa las etiquetas con nombre."""
    escalador = StandardScaler()
    Z = escalador.fit_transform(df[VARIABLES_SEGMENTO])
    km = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(Z)
    # Nombrar por actividad: el grupo con más inicios de sesión es el primero de NOMBRES_SEGMENTO
    promedio = pd.DataFrame({"g": km.labels_, "login": df["Login_Frequency"].values}).groupby("g")["login"].mean()
    orden = promedio.sort_values(ascending=False).index.tolist()
    nombres = {grupo: NOMBRES_SEGMENTO[i] for i, grupo in enumerate(orden)}
    etiquetas = pd.Series(km.labels_, index=df.index).map(nombres)
    return {"etiquetas": etiquetas, "kmeans": km, "escalador": escalador, "nombres": nombres}


def calidad_segmentos(df, ks=range(3, 7), muestra=8000, random_state=0):
    """Silueta para distintos números de grupos (en una muestra, para que sea rápido)."""
    Z = StandardScaler().fit_transform(df[VARIABLES_SEGMENTO])
    idx = np.random.RandomState(random_state).choice(len(df), min(muestra, len(df)), replace=False)
    filas = []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(Z)
        filas.append({"Grupos (k)": k, "Silueta": round(silhouette_score(Z[idx], km.labels_[idx]), 3)})
    return pd.DataFrame(filas)


def perfil_segmentos(df_puntuado):
    """Perfil de cada segmento: tamaño, churn, riesgo y promedio de las variables clave."""
    g = df_puntuado.groupby("Segmento")
    perfil = pd.DataFrame({
        "Clientes": g.size(),
        "Activos": g["Churned"].apply(lambda s: int((s == 0).sum())),
        "Churn histórico (%)": (g["Churned"].mean() * 100).round(1),
        "Activos en riesgo alto": g.apply(lambda x: int(((x["Churned"] == 0) & (x["Nivel_Riesgo"] == "Alto")).sum()),
                                          include_groups=False),
        "Inicios de sesión": g["Login_Frequency"].mean().round(1),
        "Apertura de correos (%)": g["Email_Open_Rate"].mean().round(1),
        "Carrito abandonado (%)": g["Cart_Abandonment_Rate"].mean().round(1),
        "Llamadas a servicio": g["Customer_Service_Calls"].mean().round(1),
        "Días sin comprar": g["Dias_Sin_Comprar"].mean().round(0),
    })
    orden = [n for n in NOMBRES_SEGMENTO if n in perfil.index]
    perfil = perfil.loc[orden].reset_index()
    perfil["Descripción"] = perfil["Segmento"].map(DESCRIPCION_SEGMENTO)
    return perfil
