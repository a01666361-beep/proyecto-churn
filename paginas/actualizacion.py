"""
Pantalla · Actualización de datos y del modelo.
Decisión: si un archivo nuevo de clientes se puede usar, qué riesgo tiene cada cliente y si el modelo
sigue funcionando bien o hay que reentrenarlo.

Ciclo de actualización:
1. Llega un CSV nuevo con el mismo formato que la base del curso.
2. El contrato de datos (src/contrato_datos.py) lo valida antes de usarlo: si no cumple, se rechaza.
3. El Gradient Boosting (modelo campeón) puntúa a cada cliente.
4. Si el archivo trae Churned, se mide el desempeño del modelo (AUC y recall) contra la referencia de test.
5. Si el desempeño baja, se reentrena en el notebook, se sube a GitHub, GitHub Actions corre las pruebas
   y Streamlit Cloud publica la versión nueva sola.
Agregado el 24-nov para cubrir el elemento "Updating process" de la rúbrica.
"""
import io
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import recall_score, roc_auc_score

from src import ayuda
from src import modelo as M
from src.config import AZUL, NARANJA, RUTA_DATOS
from src.contexto import obtener_datos
from src.contrato_datos import ErrorContrato
from src.limpieza import cargar_datos
from src.puntuacion import modelo_y_puntuacion

TOLERANCIA_AUC = 0.03          # si el AUC baja más que esto contra la referencia, se recomienda reentrenar
TOLERANCIA_MEDIA = 0.10        # cambio relativo en el promedio de una variable que se marca para revisar
VARIABLES_VIGILADAS = ["Customer_Service_Calls", "Cart_Abandonment_Rate", "Age", "Discount_Usage_Rate",
                       "Email_Open_Rate", "Dias_Sin_Comprar"]

resultado, puntuado_total = modelo_y_puntuacion()
base = obtener_datos()
referencia = resultado["metricas"]

ayuda.titulo_pantalla("Actualización de datos y del modelo", "actualizacion",
                      "Cómo entra un archivo nuevo al dashboard, cómo se valida y cuándo hay que reentrenar el modelo")

# ------------------------------------------------------------------ Estado actual
st.markdown("#### Estado actual")
a, b, c, d = st.columns(4)
a.metric("Clientes en la base", f"{len(base):,}", help=f"Archivo: {RUTA_DATOS.name}")
b.metric("Modelo en uso", "Gradient Boosting", help="Modelo campeón de la comparativa de cinco modelos.")
c.metric("AUC de referencia (test)", f"{referencia['AUC']:.3f}",
         help="Desempeño en el 20% de clientes que el modelo no vio al entrenarse.")
entrenado = resultado.get("entrenado")
d.metric("Modelo cargado", entrenado.strftime("%d/%m/%Y %H:%M") if entrenado else "—",
         help="Fecha y hora (Ciudad de México) en que este servidor entrenó el modelo por última vez.")

# ------------------------------------------------------------------ Ciclo
st.markdown("#### Ciclo de actualización")
pasos = [
    ("1. Datos nuevos", "Llega un CSV de clientes con el mismo formato de la base."),
    ("2. Contrato de datos", "Se revisan columnas, tipos, vacíos y rangos. Si no cumple, se rechaza."),
    ("3. Puntuación", "El Gradient Boosting calcula la probabilidad de abandono de cada cliente."),
    ("4. Monitoreo", "Si el archivo trae Churned, se compara el AUC y el recall contra la referencia."),
    ("5. Reentrenar y publicar", "Notebook → GitHub → pruebas automáticas (GitHub Actions) → Streamlit Cloud."),
]
for columna, (titulo, texto) in zip(st.columns(len(pasos), gap="small"), pasos):
    with columna, st.container(border=True):
        st.markdown(f"**{titulo}**")
        st.caption(texto)

# ------------------------------------------------------------------ Probar con un archivo
st.markdown("#### Cargar un archivo nuevo")
izquierda, derecha = st.columns([3, 2], gap="large")
with izquierda:
    archivo = st.file_uploader("CSV de clientes (mismo formato que la base, coma decimal)", type="csv")
with derecha:
    st.caption("¿No tienes un archivo a la mano? Usa una muestra para ver el proceso completo.")
    if st.button("Usar una muestra de 1,000 clientes (demostración)", use_container_width=True):
        st.session_state["muestra_actualizacion"] = "buena"
    if st.button("Probar con un archivo con errores (demostración)", use_container_width=True,
                 help="Misma muestra, pero sin la columna Age y con un cliente sin dato de Churned."):
        st.session_state["muestra_actualizacion"] = "con errores"
    if st.button("Volver a entrenar el modelo y recargar la base", use_container_width=True,
                 help="Borra la caché y vuelve a leer el CSV y a entrenar el modelo (tarda unos segundos)."):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

contenido, origen = None, None
if archivo is not None:
    contenido, origen = archivo.getvalue(), f"archivo {archivo.name}"
elif st.session_state.get("muestra_actualizacion"):
    crudo = pd.read_csv(RUTA_DATOS, dtype=str, keep_default_na=False).sample(1000, random_state=7)
    if st.session_state["muestra_actualizacion"] == "con errores":
        crudo = crudo.drop(columns="Age")
        crudo.iloc[3, crudo.columns.get_loc("Churned")] = ""
        origen = "muestra de demostración con errores a propósito"
    else:
        origen = "muestra de demostración (1,000 clientes tomados de la base actual)"
    contenido = crudo.to_csv(index=False).encode("utf-8")

if contenido is None:
    st.info("Sube un archivo o usa la muestra para ver cómo se valida y se puntúa.")
    st.stop()

# Paso 2: contrato de datos
try:
    nuevo = cargar_datos(io.BytesIO(contenido))
except (ErrorContrato, ValueError) as exc:
    st.error(f"**Archivo rechazado por el contrato de datos** ({origen}). No se usa en el dashboard.")
    st.code(str(exc))
    st.stop()
st.success(f"**Contrato de datos correcto** · {origen} · {len(nuevo):,} clientes · "
           f"validado el {datetime.now(ZoneInfo('America/Mexico_City')):%d/%m/%Y %H:%M}")

# Paso 3: puntuación
puntuado = M.puntuar(nuevo, resultado["modelo"])
activos = puntuado[puntuado["Churned"] == 0]
k = st.columns(4)
k[0].metric("Clientes en el archivo", f"{len(puntuado):,}")
k[1].metric("Probabilidad promedio", f"{puntuado['Probabilidad'].mean():.1%}")
k[2].metric("Activos en riesgo alto", f"{(activos['Nivel_Riesgo'] == 'Alto').sum():,}",
            help=f"Activos con probabilidad ≥ {M.UMBRAL_ALTO:.0%}.")
k[3].metric("Recibirían campaña", f"{(activos['Probabilidad'] > resultado['corte']).sum():,}",
            help=f"Regla de decisión: probabilidad > {resultado['corte']:.0%} → campaña \"No te vayas\".")

# Paso 4: monitoreo del modelo y de los datos
st.markdown("#### Monitoreo del modelo")
if puntuado["Churned"].nunique() < 2:
    st.info("El archivo no trae clientes de las dos clases (se fue / se quedó): no se puede medir el AUC.")
else:
    auc = roc_auc_score(puntuado["Churned"], puntuado["Probabilidad"])
    recall = recall_score(puntuado["Churned"], (puntuado["Probabilidad"] > resultado["corte"]).astype(int))
    m1, m2, m3 = st.columns(3)
    m1.metric("AUC con el archivo nuevo", f"{auc:.3f}", f"{auc - referencia['AUC']:+.3f} vs. referencia")
    m2.metric("Recall con el archivo nuevo", f"{recall:.1%}", f"{(recall - referencia['Recall']) * 100:+.1f} pts vs. referencia")
    reentrenar = auc < referencia["AUC"] - TOLERANCIA_AUC
    m3.metric("Decisión", "Reentrenar" if reentrenar else "Mantener modelo",
              help=f"Se recomienda reentrenar si el AUC baja más de {TOLERANCIA_AUC} contra la referencia.")
    if reentrenar:
        st.warning("El desempeño bajó: reentrena el modelo en el notebook con los datos nuevos y súbelo a GitHub.")
    else:
        st.success("El modelo mantiene su desempeño con estos datos: no hace falta reentrenar.")
    if origen.startswith("muestra de demostración ("):
        st.caption("La muestra sale de la misma base con la que se entrenó el modelo, por eso el AUC puede salir "
                   "más alto que la referencia. Con datos realmente nuevos es la prueba que importa.")

ayuda.titulo_grafica(
    "Cambios en los datos frente a la base actual",
    "Promedio de las variables clave en el archivo nuevo contra la base actual.",
    f"Una variable se marca para revisar si su promedio cambia más de {TOLERANCIA_MEDIA:.0%}.",
    "Si los clientes nuevos se parecen a los del entrenamiento o si conviene reentrenar.", nivel="####")
filas = []
for col in VARIABLES_VIGILADAS:
    actual, nuevo_prom = base[col].mean(), nuevo[col].mean()
    cambio = (nuevo_prom - actual) / actual if actual else 0.0
    filas.append({"Variable": M.NOMBRES.get(col, "Días sin comprar" if col == "Dias_Sin_Comprar" else col),
                  "Base actual": round(actual, 2), "Archivo nuevo": round(nuevo_prom, 2),
                  "Cambio (%)": round(cambio * 100, 1),
                  "Estado": "Revisar" if abs(cambio) > TOLERANCIA_MEDIA else "Estable"})
deriva = pd.DataFrame(filas)
fig = go.Figure(go.Bar(x=deriva["Cambio (%)"], y=deriva["Variable"], orientation="h",
                       marker_color=[NARANJA if e == "Revisar" else AZUL for e in deriva["Estado"]],
                       text=[f"{v:+.1f}%" for v in deriva["Cambio (%)"]], textposition="outside",
                       hovertemplate="%{y}: %{x:+.1f}%<extra></extra>"))
fig.add_vline(x=0, line_color="#B0B7C3")
fig.update_layout(height=300, margin=dict(l=10, r=40, t=10, b=10), xaxis_title="Cambio del promedio (%)")
st.plotly_chart(fig, use_container_width=True)
st.dataframe(deriva, hide_index=True, use_container_width=True)

# Descarga
salida = puntuado[["Customer_ID", "Probabilidad", "Nivel_Riesgo", "Churned"]].sort_values("Probabilidad", ascending=False)
salida = salida.assign(Probabilidad=(salida["Probabilidad"] * 100).round(1)).rename(
    columns={"Probabilidad": "Probabilidad de churn (%)", "Nivel_Riesgo": "Nivel de riesgo"})
st.download_button("Descargar clientes puntuados (CSV)", salida.to_csv(index=False).encode("utf-8-sig"),
                   file_name="clientes_puntuados_actualizacion.csv", mime="text/csv")
st.caption("El archivo se valida y se puntúa en esta sesión; no reemplaza la base del dashboard. Para que la base "
           "cambie de forma permanente, se sube el CSV a la carpeta data/ en GitHub y Streamlit Cloud se actualiza solo. "
           "Origen de las probabilidades: resultado del modelo, no dato observado.")
