"""
Validación estadística de los clusters (las mismas pruebas del Colab notebooks/Equipo5_KMeans_Clustering.ipynb).
Solo pandas, NumPy, SciPy y scikit-learn, sin Streamlit.
RESPONSABLE: Sara Rivero

Todo se calcula con la base completa (no con los filtros), igual que el modelo de clusters.
"""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.cluster import hierarchy as sch
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score,
                             silhouette_score)
from sklearn.preprocessing import StandardScaler

from src.modelo import NOMBRES_SEGMENTO, NUM_SEGMENTOS, VARIABLES_SEGMENTO

MUESTRA = 8000  # para la silueta (con 50,000 tarda mucho)


def _escalar(df):
    return StandardScaler().fit_transform(df[VARIABLES_SEGMENTO])


def _kmeans(Z, k, semilla=0):
    return KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=semilla).fit(Z)


def _muestra(n, tam=MUESTRA, semilla=0):
    return np.random.RandomState(semilla).choice(n, min(tam, n), replace=False)


def indices_por_k(df, ks=range(1, 11)):
    """WCSS (método del codo), silueta, Calinski-Harabasz, Davies-Bouldin y V de Cramér con el churn por k."""
    Z = _escalar(df)
    idx = _muestra(len(Z))
    filas = []
    for k in ks:
        km = _kmeans(Z, k)
        fila = {"k": k, "WCSS": km.inertia_}
        if k >= 2:
            t = pd.crosstab(km.labels_, df["Churned"].values)
            chi2 = stats.chi2_contingency(t)[0]
            fila.update({
                "Silueta": silhouette_score(Z[idx], km.labels_[idx]),
                "Calinski-Harabasz": calinski_harabasz_score(Z, km.labels_),
                "Davies-Bouldin": davies_bouldin_score(Z, km.labels_),
                "V de Cramér": np.sqrt(chi2 / len(df)),
            })
        filas.append(fila)
    tabla = pd.DataFrame(filas)
    tabla["Reducción del WCSS (%)"] = -tabla["WCSS"].pct_change() * 100
    return tabla


def estabilidad(df, semillas=(1, 7, 21, 42, 99), k=NUM_SEGMENTOS):
    """ARI entre el modelo final (semilla 0) y el mismo modelo con otras semillas (1 = mismos grupos)."""
    Z = _escalar(df)
    base = _kmeans(Z, k).labels_
    return pd.DataFrame([{"Semilla": s, "ARI vs modelo final": adjusted_rand_score(base, _kmeans(Z, k, s).labels_)}
                         for s in semillas])


def perfil_estandarizado(df, segmentos):
    """Promedio de cada variable por segmento en desviaciones estándar (0 = promedio de la base)."""
    Z = pd.DataFrame(_escalar(df), columns=VARIABLES_SEGMENTO, index=df.index)
    perfil = Z.groupby(segmentos).mean()
    return perfil.loc[[n for n in NOMBRES_SEGMENTO if n in perfil.index]]


def proyeccion(df, segmentos, tam=3000):
    """Puntos de una muestra y centroides, en variables originales (carrito vs inicios de sesión) y en PCA 2D."""
    escalador = StandardScaler()
    Z = escalador.fit_transform(df[VARIABLES_SEGMENTO])
    km = _kmeans(Z, NUM_SEGMENTOS)
    centros_orig = pd.DataFrame(escalador.inverse_transform(km.cluster_centers_), columns=VARIABLES_SEGMENTO)
    # Nombre de cada centroide: el segmento al que pertenece la mayoría de sus clientes
    nombre_centro = pd.Series(segmentos.values).groupby(km.labels_).agg(lambda s: s.mode().iat[0])
    centros_orig["Segmento"] = nombre_centro.values

    pca = PCA(n_components=2, random_state=0)
    Z_pca = pca.fit_transform(Z)
    centros_pca = pd.DataFrame(pca.transform(km.cluster_centers_), columns=["PC1", "PC2"])
    centros_pca["Segmento"] = nombre_centro.values

    idx = _muestra(len(df), tam)
    puntos = pd.DataFrame({
        "Login_Frequency": df["Login_Frequency"].values[idx],
        "Cart_Abandonment_Rate": df["Cart_Abandonment_Rate"].values[idx],
        "PC1": Z_pca[idx, 0], "PC2": Z_pca[idx, 1],
        "Segmento": segmentos.values[idx],
    })
    return {"puntos": puntos, "centros": centros_orig, "centros_pca": centros_pca,
            "varianza_pca": float(pca.explained_variance_ratio_.sum())}


def kruskal(df, segmentos):
    """Kruskal-Wallis de cada variable entre segmentos, con tamaño del efecto (épsilon²)."""
    n = len(df)
    filas = []
    for var in VARIABLES_SEGMENTO:
        grupos = [df.loc[segmentos == s, var] for s in NOMBRES_SEGMENTO if (segmentos == s).any()]
        H, p = stats.kruskal(*grupos)
        filas.append({"Variable": var, "H": H, "p-value": p, "Épsilon²": H / (n - 1)})
    tabla = pd.DataFrame(filas).sort_values("Épsilon²", ascending=False)
    tabla["Efecto"] = pd.cut(tabla["Épsilon²"], [-1, 0.01, 0.08, 0.26, 1],
                             labels=["Despreciable", "Pequeño", "Moderado", "Grande"]).astype(str)
    return tabla.reset_index(drop=True)


def ji_cuadrada(df, segmentos):
    """Prueba de independencia entre el segmento y el churn."""
    tabla = pd.crosstab(segmentos, df["Churned"])
    tabla = tabla.loc[[n for n in NOMBRES_SEGMENTO if n in tabla.index]]
    chi2, p, gl, _ = stats.chi2_contingency(tabla)
    v = np.sqrt(chi2 / (len(df) * (min(tabla.shape) - 1)))
    churn = (tabla[1] / tabla.sum(axis=1) * 100)
    return {"chi2": chi2, "p": p, "gl": gl, "v_cramer": v, "churn": churn}


def jerarquico(df, segmentos, tam=2000):
    """Linkage de Ward en una muestra (para el dendrograma) y coincidencia con K-Means (ARI)."""
    Z = _escalar(df)
    idx = _muestra(len(df), MUESTRA)[:tam]
    enlace = sch.linkage(Z[idx], method="ward")
    y_cj = AgglomerativeClustering(n_clusters=NUM_SEGMENTOS, linkage="ward").fit_predict(Z[idx])
    ari = adjusted_rand_score(segmentos.values[idx], y_cj)
    # Altura de corte que deja NUM_SEGMENTOS grupos (entre la fusión k y la k-1, contando desde arriba)
    alturas = np.sort(enlace[:, 2])
    corte = (alturas[-NUM_SEGMENTOS] + alturas[-NUM_SEGMENTOS + 1]) / 2
    return {"enlace": enlace, "ari": ari, "corte": corte}
