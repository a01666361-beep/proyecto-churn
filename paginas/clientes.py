"""
Pantalla 05 · Clientes prioritarios (modelo predictivo).
Pregunta: ¿qué clientes activos tienen más probabilidad de abandonar, a qué segmento pertenecen
y qué variables explican el riesgo?
RESPONSABLE: Sara Rivero
"""
import plotly.graph_objects as go
import streamlit as st

from src import modelo as M
from src.config import AZUL, AZUL_PALIDO, ROJO, VERDE
from src.contexto import contexto, obtener_datos
from src.tablas_datos import configuracion_columnas


@st.cache_resource(show_spinner="Entrenando el modelo…")
def preparar_modelo():
    """Entrena una sola vez el modelo y los segmentos con toda la base, y puntúa a todos los clientes."""
    df = obtener_datos()
    resultado = M.entrenar_modelo(df)
    segmentos = M.entrenar_segmentos(df)
    puntuado = M.puntuar(df, resultado["modelo"])
    puntuado["Segmento"] = segmentos["etiquetas"]
    return resultado, puntuado


@st.cache_data(show_spinner=False)
def silueta():
    return M.calidad_segmentos(obtener_datos())


c = contexto()
resultado, puntuado_total = preparar_modelo()
puntuado = puntuado_total.loc[c.df_filtrado.index]  # respeta los filtros de país, género y edad

st.markdown('<h2 class="seccion-titulo">Clientes prioritarios</h2>', unsafe_allow_html=True)
st.caption("Probabilidad de abandono de cada cliente según el modelo de regresión logística · "
           f"{len(puntuado):,} de {len(puntuado_total):,} clientes en el grupo seleccionado")

if puntuado.empty:
    st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

scoring, segmentos, modelo_tab = st.tabs(["Scoring de clientes", "Segmentos", "Modelo y variables"])

# ================================================================== Scoring
with scoring:
    st.markdown(f"**Niveles de riesgo:** Alto si la probabilidad es ≥ {M.UMBRAL_ALTO:.0%}, "
                f"Medio entre {M.UMBRAL_MEDIO:.0%} y {M.UMBRAL_ALTO:.0%}, Bajo si es menor a {M.UMBRAL_MEDIO:.0%}.")
    st.dataframe(M.resumen_niveles(puntuado), hide_index=True, use_container_width=True,
                 column_config={"Clientes": st.column_config.NumberColumn(format="localized"),
                                "Activos": st.column_config.NumberColumn(format="localized")})
    st.caption("El churn histórico sube de un nivel a otro: el modelo sí ordena a los clientes por riesgo.")

    col1, col2 = st.columns([1, 2])
    with col1:
        solo_activos = st.toggle("Solo clientes activos", value=True,
                                 help="Los que ya abandonaron no se pueden retener; se muestran solo para revisar el modelo.")
    with col2:
        niveles = st.multiselect("Nivel de riesgo", M.NIVELES, default=["Alto"], placeholder="Todos")

    tabla = M.tabla_scoring(puntuado, solo_activos=solo_activos, niveles=niveles)
    st.markdown(f"**{len(tabla):,} clientes**, ordenados de mayor a menor probabilidad de abandono.")
    st.dataframe(
        tabla, column_order=list(tabla.columns), hide_index=True,
        use_container_width=True, height=420,
        column_config={**configuracion_columnas(tabla),
                       "Probabilidad de churn (%)": st.column_config.ProgressColumn(
                           min_value=0, max_value=100, format="%.1f%%",
                           help="Origen: resultado estimado por el modelo, no es dato observado")})
    st.download_button("Descargar tabla (CSV)", tabla.to_csv(index=False).encode("utf-8-sig"),
                       file_name="clientes_priorizados.csv", mime="text/csv", disabled=tabla.empty)
    st.caption("Abre la ayuda de cada encabezado para ver si la cifra viene del CSV, de un cálculo o del modelo")
    st.caption("El scoring usa toda la base, incluidos los clientes con los que se entrenó el modelo. "
               "Sirve para ordenar la lista de contacto, no para medir qué tan bueno es el modelo (eso está en "
               "la pestaña Modelo y variables).")

# ================================================================== Segmentos
with segmentos:
    perfil = M.perfil_segmentos(puntuado)
    st.markdown(f"Los clientes se agruparon en **{M.NUM_SEGMENTOS} segmentos** con K-Means según su comportamiento "
                "(actividad, compras, carrito, llamadas y correos). Los nombres describen qué tan activos son.")

    columnas = st.columns(len(perfil), gap="small")
    for columna, (_, fila) in zip(columnas, perfil.iterrows()):
        with columna, st.container(border=True):
            st.markdown(f"**{fila['Segmento']}**")
            st.markdown(f'<div class="kpi-valor">{fila["Churn histórico (%)"]:.1f}%</div>', unsafe_allow_html=True)
            st.caption(f"churn · {fila['Clientes']:,} clientes · {fila['Activos en riesgo alto']:,} activos en riesgo alto")
            st.caption(fila["Descripción"])

    st.markdown("**Perfil promedio de cada segmento**")
    st.dataframe(perfil.drop(columns="Descripción"), hide_index=True, use_container_width=True)

    with st.expander(f"¿Por qué {M.NUM_SEGMENTOS} segmentos?"):
        st.dataframe(silueta(), hide_index=True)
        st.caption("Con el método del codo, el WCSS deja de bajar de forma importante después de 3 grupos, y la "
                   "silueta (de −1 a 1, mayor es mejor) es más alta con 3 que con cualquier número mayor. Con 4 "
                   "grupos, dos quedaban con un churn casi igual (18.2% y 18.4%), así que no se justificaba separarlos. "
                   "Análisis completo en notebooks/Equipo5_KMeans_Clustering.ipynb.")

# ================================================================== Modelo
with modelo_tab:
    m = resultado["metricas"]
    st.markdown(f"Regresión logística con {len(M.VARIABLES_NUMERICAS)} variables numéricas estandarizadas y "
                f"{len(M.VARIABLES_CATEGORICAS)} categóricas. Entrenamiento con {resultado['n_train']:,} clientes y "
                f"evaluación con {resultado['n_test']:,} que el modelo no vio (70/30). "
                "El modelo usa toda la base: estas métricas no cambian con los filtros.")

    k = st.columns(5)
    k[0].metric("AUC", f"{m['AUC']:.3f}", help="Qué tan bien separa a quien se va de quien se queda (0.5 = azar, 1 = perfecto).")
    k[1].metric("Recall", f"{m['Recall']:.1%}", help="De los que sí abandonaron, cuántos detectó.")
    k[2].metric("Precisión", f"{m['Precisión']:.1%}", help="De los que marcó como abandono, cuántos sí abandonaron.")
    k[3].metric("F1", f"{m['F1']:.3f}")
    k[4].metric("Accuracy", f"{m['Accuracy']:.1%}", help="Clientes bien clasificados.")

    mt = resultado["matriz"]
    izquierda, derecha = st.columns([1, 1], gap="large")
    with izquierda:
        st.markdown("**Matriz de confusión (prueba)**")
        fig = go.Figure(go.Heatmap(
            z=[[mt["VN"], mt["FP"]], [mt["FN"], mt["VP"]]],
            x=["Predice: se queda", "Predice: abandona"], y=["Real: se queda", "Real: abandona"],
            text=[[f"{mt['VN']:,}<br>verdaderos negativos", f"{mt['FP']:,}<br>falsos positivos"],
                  [f"{mt['FN']:,}<br>falsos negativos", f"{mt['VP']:,}<br>verdaderos positivos"]],
            texttemplate="%{text}", colorscale=[[0, AZUL_PALIDO], [1, AZUL]], showscale=False))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), yaxis_autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    with derecha:
        st.markdown("**Cómo leer estas métricas**")
        st.markdown(
            f"- Detecta **{m['Recall']:.0%}** de los clientes que abandonan ({mt['VP']:,} de {mt['VP'] + mt['FN']:,}).\n"
            f"- Su accuracy ({m['Accuracy']:.1%}) es menor que decir siempre \"no abandona\" "
            f"({m['Accuracy línea base']:.1%}), porque el modelo se ajustó para no dejar escapar a quienes se van: "
            f"acepta {mt['FP']:,} falsas alarmas a cambio de detectar a más clientes en riesgo.\n"
            f"- Por eso se evalúa con **AUC ({m['AUC']:.3f})** y **recall**: en retención cuesta más perder "
            "a un cliente que contactar a uno que no se iba a ir.")

    st.markdown("**Variables que más influyen en el abandono**")
    coef = M.coeficientes(resultado["modelo"]).head(12)
    fig = go.Figure(go.Bar(
        x=coef["Coeficiente"][::-1], y=coef["Variable"][::-1], orientation="h",
        marker_color=[ROJO if v > 0 else VERDE for v in coef["Coeficiente"][::-1]],
        text=[f"×{r:.2f}" for r in coef["Razón de momios"][::-1]], textposition="outside",
        hovertemplate="%{y}: coeficiente %{x:.3f}<extra></extra>"))
    fig.update_layout(height=420, margin=dict(l=10, r=40, t=10, b=10),
                      xaxis_title="Coeficiente (variables estandarizadas)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Rojo: aumenta el riesgo · verde: lo reduce. La etiqueta (×) es la razón de momios: cuánto se "
               "multiplican los momios de abandono cuando la variable sube una desviación estándar. "
               "Son relaciones, no causas.")
