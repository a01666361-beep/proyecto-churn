"""
Pantalla 05 · Clientes prioritarios (modelo predictivo).
Decisión: a qué clientes activos contactar primero según su probabilidad de abandono, a qué segmento
pertenecen y qué variables explican el riesgo.
RESPONSABLE: Sara Rivero
Explicación por cliente (por qué está en riesgo): Víctor García (A01784206)
"""
import plotly.graph_objects as go
import streamlit as st

from src import analisis_clusters as A
from src import ayuda
from src import modelo as M
from src import modelo_gb as G
from src.config import AZUL, AZUL_PALIDO, AZUL_TEXTO, GRIS, ROJO, VERDE
from src.contexto import contexto, obtener_datos
from src.puntuacion import modelo_y_puntuacion as preparar_modelo  # caché compartida (Víctor)
from src.tablas_datos import configuracion_columnas
from src import acceso

acceso.exigir("paginas/clientes.py")  # entregable 3: segunda barrera por rol


@st.cache_resource(show_spinner="Calculando el perfil de los segmentos (solo la primera vez)…")
def analisis_clusters():
    """Perfil y prueba ji cuadrada de los segmentos con toda la base. Se calcula una sola vez.
    Las demás pruebas de validación (codo, índices, estabilidad, Kruskal-Wallis, jerárquico) están en el notebook."""
    df = obtener_datos()
    segmentos = preparar_modelo()[1]["Segmento"]
    return {
        "perfil_z": A.perfil_estandarizado(df, segmentos),
        "ji": A.ji_cuadrada(df, segmentos),
    }


COLOR_SEGMENTO = {"Comprometidos": VERDE, "Regulares": AZUL, "Desconectados": ROJO}


c = contexto()
resultado, puntuado_total = preparar_modelo()
puntuado = puntuado_total.loc[c.df_filtrado.index]  # respeta los filtros de país, género y edad

ayuda.titulo_pantalla("Clientes prioritarios", "clientes",
                      "Probabilidad de abandono de cada cliente según el Gradient Boosting (modelo campeón) · "
                      f"{len(puntuado):,} de {len(puntuado_total):,} clientes en el grupo seleccionado")

if puntuado.empty:
    st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

scoring, segmentos, modelo_tab = st.tabs(["Scoring de clientes", "Segmentos", "Modelo y variables"])

# ================================================================== Scoring
with scoring:
    niveles_tabla = M.resumen_niveles(puntuado)
    alto = niveles_tabla.iloc[0]
    ayuda.titulo_grafica(
        f"Riesgo alto: {alto['Activos']:,} activos, {alto['Churn histórico (%)']:.1f}% de abandono histórico",
        "Cuántos clientes y activos hay en cada nivel de riesgo del modelo y cuánto abandonaron en realidad.",
        f"Alto si la probabilidad es ≥ {M.UMBRAL_ALTO:.0%}, Medio entre {M.UMBRAL_MEDIO:.0%} y {M.UMBRAL_ALTO:.0%}, "
        f"Bajo si es menor a {M.UMBRAL_MEDIO:.0%}. Si el churn histórico baja de Alto a Bajo, el modelo ordena bien.",
        "Cuántos clientes caben en la campaña y por qué nivel empezar.", nivel="####",
        pregunta="¿Cuántos clientes activos están en riesgo alto y por qué nivel conviene empezar la campaña?")
    st.dataframe(niveles_tabla, hide_index=True, use_container_width=True,
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
    st.download_button("Descargar lista (CSV)", tabla.to_csv(index=False).encode("utf-8-sig"),
                       file_name="clientes_priorizados.csv", mime="text/csv", disabled=tabla.empty)
    # Retroalimentación 12-nov: la tabla de clientes queda oculta; se abre o se descarga solo cuando se necesita.
    with st.expander("Ver la lista de clientes (oculta)"):
        st.dataframe(
            tabla, column_order=list(tabla.columns), hide_index=True,
            use_container_width=True, height=420,
            column_config={**configuracion_columnas(tabla),
                           "Probabilidad de churn (%)": st.column_config.ProgressColumn(
                               min_value=0, max_value=100, format="%.1f%%",
                               help="Origen: resultado estimado por el modelo, no es dato observado")})
    st.caption("Abre la ayuda de cada encabezado para ver si la cifra viene del CSV, de un cálculo o del modelo")
    st.caption("El scoring usa toda la base, incluidos los clientes con los que se entrenó el modelo. "
               "Sirve para ordenar la lista de contacto, no para medir qué tan bueno es el modelo (eso está en "
               "la pestaña Modelo y variables).")

    # -------------------------------------------- Explicación por cliente (Víctor García, A01784206)
    ayuda.titulo_grafica(
        "Explicación por cliente: las 5 variables que más pesan en su riesgo",
        "Para el cliente elegido, qué variables suben o bajan su probabilidad de abandono frente al cliente promedio.",
        "Naranja sube el riesgo, cian lo baja. El largo de la barra es cuánto cambia su probabilidad si esa variable tuviera el valor típico.",
        "Qué mensaje o acción usar con ese cliente al contactarlo.", nivel="####",
        pregunta="¿Por qué este cliente tiene riesgo alto y qué conviene decirle al contactarlo?")
    if tabla.empty:
        st.info("No hay clientes en la tabla con estos filtros.")
    else:
        opciones = tabla["Cliente"].tolist()
        elegido = st.selectbox(
            "Cliente", opciones, index=0, key="explicar_cliente",
            format_func=lambda cid: (f"{cid} · {tabla.loc[tabla['Cliente'] == cid, 'Probabilidad de churn (%)'].iloc[0]:.1f}% · "
                                     f"{tabla.loc[tabla['Cliente'] == cid, 'Nivel de riesgo'].iloc[0]}"),
            help="Clientes de la tabla de arriba, en el mismo orden (de mayor a menor probabilidad).")
        explicacion, base = M.explicar_cliente_campeon(resultado["modelo"], puntuado_total, elegido, n=5)
        fila = puntuado_total[puntuado_total["Customer_ID"] == elegido].iloc[0]

        izquierda, derecha = st.columns([1, 2], gap="large")
        with izquierda:
            with st.container(border=True):
                st.markdown(f"**Cliente {elegido}**")
                st.markdown(f'<div class="kpi-valor">{base["probabilidad"]:.1%}</div>', unsafe_allow_html=True)
                st.caption(f"Probabilidad de abandono según el modelo · nivel **{fila['Nivel_Riesgo']}** · "
                           f"segmento **{fila['Segmento']}**")
                st.caption(f"Cliente promedio de la base: {base['probabilidad_promedio']:.1%}")
            lectura = explicacion.iloc[0]
            st.markdown(f"Lo que más mueve su riesgo es **{lectura['Variable'].lower()}**, que "
                        f"{'lo sube' if lectura['Aporte'] > 0 else 'lo baja'} {abs(lectura['Aporte']):.1f} puntos frente al valor típico.")
        with derecha:
            orden = explicacion.iloc[::-1]
            fig = go.Figure(go.Bar(
                x=orden["Aporte"], y=orden["Variable"], orientation="h",
                marker_color=[ROJO if v > 0 else VERDE for v in orden["Aporte"]],
                customdata=orden["Valor del cliente"].astype(str),
                hovertemplate="%{y}<br>Valor del cliente: %{customdata}<br>Aporte: %{x:+.1f} pts<extra></extra>"))
            fig.add_vline(x=0, line_color=GRIS)
            fig.update_layout(height=280, margin=dict(l=10, r=20, t=30, b=10),
                              title=dict(text="Las 5 variables que más pesan en su probabilidad", font_size=14),
                              xaxis_title="Cambio en su probabilidad (puntos porcentuales)")
            st.plotly_chart(fig, width="stretch")
        st.caption("Naranja: sube su riesgo · cian: lo baja. Aporte = probabilidad del cliente − probabilidad si esa "
                   "variable tuviera el valor típico (mediana del entrenamiento), en puntos porcentuales. "
                   "Origen: resultado del modelo, no es dato observado. "
                   "Explica por qué el modelo le dio esa probabilidad; no prueba que esa sea la causa real de que se vaya. "
                   "Algunas variables vienen en escala log del CSV (ver contrato de datos).")

# ================================================================== Segmentos
with segmentos:
    perfil = M.perfil_segmentos(puntuado)
    st.markdown(f"Los clientes se agruparon en **{M.NUM_SEGMENTOS} segmentos** con K-Means según su comportamiento "
                "(actividad, compras, carrito, llamadas y correos). Los nombres describen qué tan activos son. "
                "Las gráficas de validación usan toda la base y no cambian con los filtros.")

    columnas = st.columns(len(perfil), gap="small")
    for columna, (_, fila) in zip(columnas, perfil.iterrows()):
        with columna, st.container(border=True):
            st.markdown(f"**{fila['Segmento']}**")
            st.markdown(f'<div class="kpi-valor">{fila["Churn histórico (%)"]:.1f}%</div>', unsafe_allow_html=True)
            st.caption(f"churn · {fila['Clientes']:,} clientes · {fila['Activos en riesgo alto']:,} activos en riesgo alto")
            st.caption(fila["Descripción"])

    ayuda.titulo_grafica(
        "Perfil promedio de cada segmento",
        "Tamaño, abandono, activos en riesgo alto y promedio de las variables clave de cada segmento.",
        "Compara cada columna entre segmentos: de ahí salen sus nombres (de más a menos activos).",
        "Qué mensaje y canal usar con cada segmento.", nivel="####",
        pregunta="¿Qué tan grande es cada segmento y qué comportamiento lo caracteriza?")
    st.dataframe(perfil.drop(columns="Descripción"), hide_index=True, use_container_width=True)

    analisis = analisis_clusters()

    # Entregable 3: se quitaron del tablero las gráficas de validación técnica del clustering (método del codo,
    # V de Cramér por k, índices de silueta/Calinski/Davies-Bouldin, proyecciones 2D, estabilidad con otras
    # semillas, Kruskal-Wallis y dendrograma). Responden preguntas de método, no habilitan una decisión de negocio.
    # Siguen completas en notebooks/Equipo5_KMeans_Clustering.ipynb.
    izquierda, derecha = st.columns(2, gap="medium")
    with izquierda, st.container(border=True):
        ji = analisis["ji"]
        ayuda.titulo_grafica(
            "Churn por segmento (prueba ji cuadrada)",
            "La tasa de abandono de cada segmento y si la diferencia es estadísticamente significativa.",
            "La línea punteada es el churn general. Cada barra tiene su porcentaje escrito. Si p < 0.05, "
            "el abandono depende del segmento.",
            "A qué segmento dirigir primero la retención.", nivel="####",
            pregunta="¿Qué segmento abandona más, y la diferencia es real o casualidad?")
        churn = ji["churn"]
        fig = go.Figure(go.Bar(x=churn.index, y=churn.values,
                               marker_color=[COLOR_SEGMENTO.get(n, AZUL) for n in churn.index],
                               text=[f"{c:.1f}%" for c in churn.values], textposition="outside",
                               hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
        fig.add_hline(y=c.tasa_global * 100, line_dash="dash", line_color=AZUL_TEXTO,
                      annotation_text=f"Churn general {c.tasa_global:.1%}", annotation_position="top left")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Churn (%)",
                          yaxis_range=[0, churn.max() * 1.25])
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Ji cuadrada = {ji['chi2']:,.1f}, gl = {ji['gl']}, p < 0.001, V de Cramér = {ji['v_cramer']:.3f}. "
                   "El churn depende del segmento (relación moderada).")
    with derecha, st.container(border=True):
        ayuda.titulo_grafica(
            "Perfil de cada segmento (desviaciones estándar vs. el promedio)",
            "En qué variables cada segmento está arriba o abajo del promedio de la base.",
            "Cada celda tiene su valor escrito: positivo = arriba del promedio, negativo = abajo, 0 = igual.",
            "Qué mensaje y qué acción usar con cada segmento.", nivel="####",
            pregunta="¿En qué comportamiento se diferencia cada segmento del cliente promedio?")
        pz = analisis["perfil_z"]
        fig = go.Figure(go.Heatmap(z=pz.values, x=pz.columns, y=pz.index, zmin=-1.5, zmax=1.5, colorscale="RdBu_r",
                                   text=pz.round(1).values, texttemplate="%{text}",
                                   colorbar=dict(title="DE"),
                                   hovertemplate="%{y} · %{x}: %{z:.2f} DE<extra></extra>"))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), yaxis_autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Los días sin comprar y el uso de descuentos casi no cambian entre segmentos.")

    st.caption("La elección de 3 segmentos se validó con el método del codo, índices de silueta, Calinski-Harabasz y "
               "Davies-Bouldin, estabilidad con otras semillas, Kruskal-Wallis y un cluster jerárquico. Esas pruebas "
               "están completas en notebooks/Equipo5_KMeans_Clustering.ipynb.")

# ================================================================== Modelo
with modelo_tab:
    m = resultado["metricas"]
    st.markdown(f"**Gradient Boosting** (modelo campeón): 11 variables del modelo final de SAS, entrenado con "
                f"{resultado['n_train']:,} clientes (80%, limpio) y evaluado con {resultado['n_test']:,} que el modelo "
                "no vio (20%, sin limpiar ni imputar). Regla de decisión: probabilidad > 30% (antes 50%, cambio pedido por el profesor) → campaña \"No te vayas\". "
                "Las métricas no cambian con los filtros. La comparación contra los otros cuatro modelos está en "
                "**Comparativa y predicción**.")

    k = st.columns(5)
    k[0].metric("AUC", f"{m['AUC']:.3f}", help="Qué tan bien separa a quien se va de quien se queda (0.5 = azar, 1 = perfecto).")
    k[1].metric("Recall", f"{m['Recall']:.1%}", help="De los que sí abandonaron, cuántos detectó.")
    k[2].metric("Precisión", f"{m['Precisión']:.1%}", help="De los que marcó como abandono, cuántos sí abandonaron.")
    k[3].metric("F1", f"{m['F1']:.3f}")
    k[4].metric("Accuracy", f"{m['Accuracy']:.1%}", help="Clientes bien clasificados.")

    mt = resultado["matriz"]
    izquierda, derecha = st.columns([1, 1], gap="large")
    with izquierda:
        ayuda.titulo_grafica(
            f"Matriz de confusión: {mt['VP']:,} abandonos detectados y {mt['FN']:,} no detectados",
            "Cuántos clientes del conjunto de prueba clasificó bien y mal el modelo.",
            "Filas = lo que pasó; columnas = lo que predijo. Falsos negativos = clientes que se fueron sin ser "
            "detectados; falsos positivos = contactos a clientes que se iban a quedar.",
            "Si el balance entre clientes detectados y contactos de más es aceptable.", nivel="####",
            pregunta="¿Cuántos abandonos detecta el modelo y a cuántos clientes contactaríamos de más?")
        fig = go.Figure(go.Heatmap(
            z=[[mt["VN"], mt["FP"]], [mt["FN"], mt["VP"]]],
            x=["Predice: se queda", "Predice: abandona"], y=["Real: se queda", "Real: abandona"],
            text=[[f"{mt['VN']:,}<br>verdaderos negativos", f"{mt['FP']:,}<br>falsos positivos"],
                  [f"{mt['FN']:,}<br>falsos negativos", f"{mt['VP']:,}<br>verdaderos positivos"]],
            texttemplate="%{text}", colorscale=[[0, AZUL_PALIDO], [1, AZUL]], showscale=False))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), yaxis_autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    with derecha:
        st.markdown("#### Lectura de las métricas")
        st.markdown(
            f"- Detecta **{m['Recall']:.0%}** de los clientes que abandonan ({mt['VP']:,} de {mt['VP'] + mt['FN']:,}).\n"
            f"- Cuando marca a un cliente como abandono, acierta **{m['Precisión']:.0%}** de las veces: solo "
            f"{mt['FP']:,} falsas alarmas.\n"
            f"- Su accuracy ({m['Accuracy']:.1%}) supera a decir siempre \"no abandona\" ({m['Accuracy línea base']:.1%}).\n"
            f"- Se evalúa con **AUC ({m['AUC']:.3f})** y **recall**: en retención cuesta más perder a un cliente "
            "que contactar a uno que no se iba a ir.")

    imp = G.importancia().copy()
    imp["Variable"] = imp["Variable"].map(lambda v: M.NOMBRES_CAMPEON.get(v.replace("log_", ""),
                                                                         M.NOMBRES.get(v.replace("log_", ""), v)))
    imp = imp.sort_values("Baja del AUC", ascending=False)
    ayuda.titulo_grafica(
        f"Variable con más influencia: {imp.iloc[0]['Variable']}",
        "Cuánto baja el AUC del modelo si se revuelve cada variable (importancia por permutación en test).",
        "Barra más larga = el modelo depende más de esa variable. No indica si sube o baja el riesgo.",
        "Qué comportamientos atacar con las acciones de retención.", nivel="####",
        pregunta="¿Qué comportamientos pesan más en el riesgo que calcula el modelo?")
    fig = go.Figure(go.Bar(
        x=imp["Baja del AUC"][::-1], y=imp["Variable"][::-1], orientation="h", marker_color=AZUL,
        text=[f"{v:.3f}" for v in imp["Baja del AUC"][::-1]], textposition="outside",
        hovertemplate="%{y}: el AUC baja %{x:.3f}<extra></extra>"))
    fig.update_layout(height=420, margin=dict(l=10, r=40, t=10, b=10), xaxis_title="Baja del AUC al revolver la variable")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Importancia por permutación calculada en el notebook de modelos. Son relaciones, no causas. "
               "Para ver si una variable sube o baja el riesgo de un cliente en particular, usa la explicación por "
               "cliente en Scoring de clientes.")
