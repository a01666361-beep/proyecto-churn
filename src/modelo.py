"""
Modelo predictivo de churn (regresión logística), scoring de toda la base y segmentos (clusters).
Solo pandas y scikit-learn, sin Streamlit, para poder revisarlo y probarlo fácilmente.
RESPONSABLE: Sara Rivero

Decisiones documentadas (ver README, sección "Modelo predictivo"):
- Regresión logística con variables estandarizadas y class_weight="balanced": la base tiene 28.9% de
  churn y sin balancear el modelo detecta menos de la mitad de los clientes que se van.
- División 70/30 estratificada con random_state=0, igual que en las evidencias.
- Niveles de riesgo por probabilidad: Alto >= 0.70, Medio 0.40 a 0.70, Bajo < 0.40.
- Segmentos con K-Means (3 grupos, por el método del codo) sobre variables de comportamiento estandarizadas.
  Análisis completo en notebooks/Equipo5_KMeans_Clustering.ipynb.
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
NUM_SEGMENTOS = 3  # codo del WCSS; con 4, dos grupos tenían churn casi igual (18.2% y 18.4%)
# Nombres propuestos, del más activo al menos activo en la plataforma (se asignan por frecuencia de inicio
# de sesión, así no dependen del número que K-Means le da a cada grupo). El equipo puede cambiarlos aquí.
NOMBRES_SEGMENTO = ["Comprometidos", "Regulares", "Desconectados"]
DESCRIPCION_SEGMENTO = {
    "Comprometidos": "Entran seguido, pasan más tiempo, abren correos y usan la app. Abandonan poco el carrito y llaman poco a servicio.",
    "Regulares": "Actividad media en todas las variables: su comportamiento está en el promedio de la base.",
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


def explicar_cliente(modelo, df, cliente_id, n=5):
    """Explica la probabilidad de un cliente: cuánto aporta cada variable frente al cliente promedio.

    Agregado por Víctor García (A01784206). En una regresión logística el logit es la suma de
    coeficiente × valor estandarizado, así que el aporte de cada variable es exacto (no aproximado):
    aporte = coeficiente × (valor del cliente − valor promedio de la base), en la escala del logit.
    Las columnas one-hot de una misma variable (por ejemplo, Country) se suman en un solo renglón.
    La suma de todos los aportes más el logit del cliente promedio da el logit del cliente.

    Regresa (tabla, base): tabla con las n variables de mayor aporte absoluto y un dict con la
    probabilidad del cliente y la del cliente promedio.
    """
    prep = modelo.named_steps["preparacion"]
    reg = modelo.named_steps["regresion"]
    Z_base = prep.transform(_x(df))
    Z_base = Z_base.toarray() if hasattr(Z_base, "toarray") else np.asarray(Z_base)
    promedio = Z_base.mean(axis=0)

    fila = df[df["Customer_ID"] == cliente_id]
    if fila.empty:
        raise KeyError(f"No existe el cliente {cliente_id}")
    z = prep.transform(_x(fila.head(1)))
    z = (z.toarray() if hasattr(z, "toarray") else np.asarray(z))[0]

    coef = reg.coef_[0]
    aportes = coef * (z - promedio)
    nombres = prep.get_feature_names_out()
    variable = [n.split("__", 1)[1] if n.startswith("numericas__")
                else next(c for c in VARIABLES_CATEGORICAS if n.split("__", 1)[1].startswith(c + "_"))
                for n in nombres]
    tabla = (pd.DataFrame({"variable_modelo": variable, "Aporte": aportes})
             .groupby("variable_modelo", as_index=False)["Aporte"].sum())
    valores = fila.iloc[0]
    tabla["Variable"] = tabla["variable_modelo"].map(lambda v: NOMBRES.get(v, v))
    tabla["Valor del cliente"] = tabla["variable_modelo"].map(lambda v: valores[v])
    tabla["Efecto"] = np.where(tabla["Aporte"] > 0, "Sube el riesgo", "Baja el riesgo")

    logit_promedio = reg.intercept_[0] + coef @ promedio
    logit_cliente = logit_promedio + aportes.sum()
    base = {"probabilidad": 1 / (1 + np.exp(-logit_cliente)),
            "probabilidad_promedio": 1 / (1 + np.exp(-logit_promedio)),
            "logit": logit_cliente, "logit_promedio": logit_promedio,
            "suma_aportes": aportes.sum()}
    tabla = tabla.reindex(tabla["Aporte"].abs().sort_values(ascending=False).index).head(n)
    return tabla[["Variable", "Valor del cliente", "Aporte", "Efecto"]].reset_index(drop=True), base


def nivel_riesgo(prob):
    return np.select([prob >= UMBRAL_ALTO, prob >= UMBRAL_MEDIO], ["Alto", "Medio"], "Bajo")


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


# ------------------------------------------------------------------ Modelo campeón para el scoring
# Cambio del 24-nov: el scoring, los niveles de riesgo, las alertas de Luis y la explicación por cliente usan
# el Gradient Boosting (modelo campeón de src/modelo_gb.py, AUC 0.924 en test) en lugar de la regresión
# logística (AUC 0.770 en test). La regresión logística se conserva en este archivo como referencia
# interpretable (entrenar_modelo, coeficientes y explicar_cliente) y para las pruebas existentes.
NOMBRES_CAMPEON = {"City": "Ciudad", "Pages_Per_Session": "Páginas por sesión", "Age": "Edad"}


class ModeloCampeon:
    """Envuelve el Gradient Boosting para puntuar la base del dashboard.

    La base del dashboard guarda Lifetime_Value, Total_Purchases, Days_Since_Last_Purchase y Returns_Rate
    en log(1 + x) (ver contrato de datos), que es justo lo que el modelo espera en sus columnas log_*.
    """
    usa_base_completa = True

    def __init__(self, pipeline, train):
        from src import modelo_gb as G
        self.G = G
        self.pipeline = pipeline
        self.columnas = G.NUMERICAS + G.CATEGORICAS
        # Valor típico de cada variable (mediana o moda del train) para explicar a cada cliente
        self.tipico = {c: float(train[c].median()) for c in G.NUMERICAS}
        self.tipico.update({c: train[c].mode()[0] for c in G.CATEGORICAS})

    def caracteristicas(self, df):
        datos = {c: (df[c[4:]] if c.startswith("log_") else df[c]) for c in self.G.NUMERICAS}
        datos.update({c: df[c] for c in self.G.CATEGORICAS})
        return pd.DataFrame(datos, index=df.index)[self.columnas]

    def predict_proba(self, df):
        return self.pipeline.predict_proba(self.caracteristicas(df))


def entrenar_campeon():
    """Entrena el Gradient Boosting igual que el notebook y regresa sus métricas de test (salida del notebook)."""
    import json

    from src import modelo_gb as G
    train = G.leer(G.RUTA_TRAIN)
    campeon = ModeloCampeon(G.entrenar(train), train)
    resumen = json.loads((G.CARPETA / "resumen_campeon.json").read_text(encoding="utf-8"))
    matriz = resumen["matriz_test"]
    n_test = sum(matriz.values())
    metricas = dict(resumen["metricas_test"])
    metricas["Accuracy línea base"] = (matriz["VN"] + matriz["FP"]) / n_test
    return {"modelo": campeon, "metricas": metricas, "matriz": matriz,
            "n_train": len(train), "n_test": n_test, "corte": resumen["corte"]}


def puntuar(df, modelo):
    """Probabilidad de churn y nivel de riesgo para cada cliente de la base (cualquiera de los dos modelos)."""
    salida = df.copy()
    datos = df if getattr(modelo, "usa_base_completa", False) else _x(df)
    salida["Probabilidad"] = modelo.predict_proba(datos)[:, 1]
    salida["Nivel_Riesgo"] = nivel_riesgo(salida["Probabilidad"])
    return salida


def explicar_cliente_campeon(campeon, df, cliente_id, n=5):
    """Explica la probabilidad del Gradient Boosting para un cliente.

    Para cada variable del modelo se cambia el valor del cliente por el valor típico (mediana del train; la moda
    en Ciudad) y se mide cuánto cambia su probabilidad: aporte = probabilidad real − probabilidad con el valor típico,
    en puntos porcentuales. Positivo: esa variable le sube el riesgo. No es causalidad: describe cómo decide el modelo.
    """
    fila = df[df["Customer_ID"] == cliente_id]
    if fila.empty:
        raise KeyError(f"No existe el cliente {cliente_id}")
    x = campeon.caracteristicas(fila.head(1))
    prob = float(campeon.pipeline.predict_proba(x)[:, 1][0])
    variantes = []
    for col in campeon.columnas:
        v = x.copy()
        v[col] = campeon.tipico[col]
        variantes.append(v)
    probs = campeon.pipeline.predict_proba(pd.concat(variantes, ignore_index=True))[:, 1]
    filas = []
    for col, p in zip(campeon.columnas, probs):
        base = col[4:] if col.startswith("log_") else col
        valor = x.iloc[0][col]
        if col.startswith("log_"):
            valor = round(float(np.expm1(valor)), 1)
        elif col not in campeon.G.CATEGORICAS:
            valor = round(float(valor), 1)
        filas.append({"Variable": NOMBRES_CAMPEON.get(base, NOMBRES.get(base, base)), "Valor del cliente": valor,
                      "Aporte": (prob - p) * 100})
    tabla = pd.DataFrame(filas)
    tabla["Efecto"] = np.where(tabla["Aporte"] > 0, "Sube el riesgo", "Baja el riesgo")
    tabla = tabla.reindex(tabla["Aporte"].abs().sort_values(ascending=False).index).head(n)
    promedio = float(campeon.predict_proba(df)[:, 1].mean())
    return tabla.reset_index(drop=True), {"probabilidad": prob, "probabilidad_promedio": promedio}
