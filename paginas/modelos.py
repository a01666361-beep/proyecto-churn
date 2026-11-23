"""
Pantalla 07 · Comparativa de modelos y predicción con Gradient Boosting.
Decisión: con qué modelo puntuar a los clientes y si a un cliente concreto se le manda la campaña "No te vayas".
RESPONSABLE: Arlen Martínez (A01666361)

Origen de cada cifra (no se mezclan):
- Métricas, curva ROC e importancia: calculadas en notebooks/Equipo5_Limpieza_y_Modelos_Churn.ipynb con el
  train 80% limpio + log y el test 20% con las mismas reglas y medianas del train + log (data/modelos/).
- Probabilidad de un cliente: predicción del Gradient Boosting, no es un dato observado.
Esta pantalla no usa los filtros de la derecha: los modelos se evalúan con el test completo.
"""
import plotly.graph_objects as go
import streamlit as st

from src import ayuda
from src import modelo_gb as G
from src.config import AZUL, AZUL_CLARO, CIAN, GRIS, NARANJA


@st.cache_resource(show_spinner="Entrenando el Gradient Boosting (solo la primera vez)…")
def modelo_campeon():
    train = G.leer(G.RUTA_TRAIN)
    return G.entrenar(train), G.numericas(train), G.opciones_y_rangos(train)


COLOR_MODELO = {"Gradient Boosting": AZUL, "Bosque aleatorio": CIAN, "Red neuronal": NARANJA,
                "Árbol de decisión": AZUL_CLARO, "Regresión logística": GRIS}
METRICAS = ["Accuracy", "Precisión", "Recall", "F1", "AUC", "KS"]

ayuda.titulo_pantalla("Comparativa de modelos", "modelos",
                      "Cinco modelos de clasificación con las 11 variables del modelo final, entrenados con el train "
                      "(80%, limpio y con logaritmos), elegidos con validación cruzada de 10 grupos y calificados con "
                      "el test (20%, con las mismas reglas de limpieza y medianas del train)")

resultados = G.comparativa()
test = resultados[resultados["Partición"] == "Test"].set_index("Modelo").loc[G.MODELOS]
validacion = resultados[resultados["Partición"] == "Validación"].set_index("Modelo").loc[G.MODELOS]
campeon = test.loc[G.CAMPEON]

comparar, curva, predecir = st.tabs(["Comparativa", "Curva ROC", "Predecir un cliente"])

# ================================================================== Comparativa
with comparar:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Modelo campeón", G.CAMPEON, help="Mayor AUC y KS en validación cruzada, igual que en SAS Model Studio.")
    k2.metric("AUC en test", f"{campeon['AUC']:.3f}",
              f"{campeon['AUC'] - test.drop(G.CAMPEON)['AUC'].max():+.3f} vs. el segundo", delta_color="normal")
    k3.metric("Accuracy en test", f"{campeon['Accuracy']:.1%}", help="Línea base (decir siempre «no se va»): 71.1%.")
    k4.metric("Recall en test", f"{campeon['Recall']:.1%}",
              help="De los clientes que sí se fueron, cuántos detectó el modelo con el corte de 0.5.")

    ayuda.titulo_grafica(
        "Métricas de los cinco modelos en el test",
        "Accuracy, precisión, recall, F1, AUC y KS de cada modelo con el corte de 0.5 (regla de la campaña).",
        "Mientras más alta la barra, mejor. El AUC no depende del corte; las demás sí.",
        "Confirmar que el Gradient Boosting es el que conviene usar para puntuar a los clientes.", nivel="####")
    fig = go.Figure()
    for metrica, color in zip(["Accuracy", "Precisión", "Recall", "F1", "AUC"], [AZUL, AZUL_CLARO, NARANJA, GRIS, CIAN]):
        fig.add_bar(name=metrica, x=test.index, y=test[metrica], marker_color=color,
                    hovertemplate="%{x} · " + metrica + ": %{y:.3f}<extra></extra>")
    fig.add_hline(y=0.711, line_dash="dot", line_color=GRIS, annotation_text="accuracy línea base",
                  annotation_position="top right")
    fig.update_layout(barmode="group", height=360, margin=dict(l=10, r=10, t=30, b=10),
                      yaxis=dict(range=[0, 1], title="Valor en test"), legend_orientation="h", legend_y=-0.15)
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Tabla de métricas")
    particion = st.radio("Partición", ["Test", "Validación"], horizontal=True,
                         help="Validación: promedio de la validación cruzada de 10 grupos dentro del train. El campeón se elige con ella; el test es el score final.")
    tabla = (test if particion == "Test" else validacion)[METRICAS + ["Error de clasificación"]].reset_index()
    st.dataframe(tabla, hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(format="%.3f")
                                for c in METRICAS + ["Error de clasificación"]})
    diferencia = (validacion["AUC"] - test["AUC"]).abs().max()
    st.caption(f"La diferencia de AUC entre validación y test es de {diferencia:.3f} o menos en todos los modelos: "
               "ninguno está sobreajustado. Cifras calculadas en el notebook de comparación.")

    with st.expander("Qué variables usa más el Gradient Boosting"):
        imp = G.importancia().head(10).iloc[::-1]
        fig = go.Figure(go.Bar(x=imp["Baja del AUC"], y=imp["Variable"], orientation="h", marker_color=AZUL,
                               hovertemplate="%{y}: el AUC baja %{x:.3f}<extra></extra>"))
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Cuánto baja el AUC si se revuelve la variable (test)")
        st.plotly_chart(fig, width="stretch")
        st.caption("Importancia por permutación. Las variables log_ están en escala log(x+1).")

# ================================================================== Curva ROC
with curva:
    ayuda.titulo_grafica(
        "Curva ROC de los cinco modelos · test",
        "Para cada corte posible: % de los que se van que detecta el modelo (eje y) contra % de los que se quedan "
        "que marca por error (eje x).",
        "Mientras más se acerque la curva a la esquina superior izquierda, mejor. La diagonal es un modelo al azar "
        "(AUC 0.5). El AUC es el área bajo cada curva.",
        "Elegir el modelo que mejor separa a los clientes que se van de los que se quedan.", nivel="####")
    puntos = G.roc()
    elegidos = st.multiselect("Modelos", G.MODELOS, default=G.MODELOS, placeholder="Elige al menos uno")
    fig = go.Figure()
    for nombre in [m for m in G.MODELOS if m in elegidos]:
        d = puntos[puntos["Modelo"] == nombre]
        fig.add_scatter(x=d["FPR"], y=d["TPR"], mode="lines", customdata=d["Corte"],
                        name=f"{nombre} (AUC {test.loc[nombre, 'AUC']:.3f})",
                        line=dict(color=COLOR_MODELO[nombre], width=3.5 if nombre == G.CAMPEON else 2),
                        hovertemplate=nombre + "<br>Corte %{customdata:.2f}<br>Falsos positivos %{x:.1%}"
                                               "<br>Verdaderos positivos %{y:.1%}<extra></extra>")
    fig.add_scatter(x=[0, 1], y=[0, 1], mode="lines", name="Al azar (AUC 0.5)",
                    line=dict(color=GRIS, dash="dash", width=1), hoverinfo="skip")
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(title="Tasa de falsos positivos (1 − especificidad)", range=[0, 1], tickformat=".0%"),
                      yaxis=dict(title="Tasa de verdaderos positivos (sensibilidad)", range=[0, 1.02], tickformat=".0%"),
                      legend=dict(x=0.98, y=0.02, xanchor="right", yanchor="bottom"))
    st.plotly_chart(fig, width="stretch")
    m = resultados.query("Modelo == @G.CAMPEON and Partición == 'Test'").iloc[0]
    st.caption(f"Con el corte de {G.CORTE} el Gradient Boosting detecta {m['Recall']:.1%} de los que se van "
               f"con {m['Precisión']:.1%} de precisión. Pasa el cursor por la curva para ver otros cortes.")

# ================================================================== Predecir
with predecir:
    modelo, columnas_num, (rangos, opciones, moda) = modelo_campeon()
    ayuda.titulo_grafica(
        "Probabilidad de abandono de un cliente con el Gradient Boosting",
        "Escribe los datos del cliente en su escala normal; el dashboard saca log(x+1) de las variables "
        "transformadas, igual que en train y test, y el modelo calcula la probabilidad.",
        f"Si la probabilidad es mayor a {G.CORTE:.0%}, la regla de decisión manda la campaña «No te vayas».",
        "Decidir si a un cliente concreto se le envía la campaña de retención.", nivel="####")
    st.caption("Los valores iniciales son la mediana de train (un cliente típico). Marca «Sin dato» si no lo conoces: "
               "el modelo manda el vacío a la rama con más clientes, sin rellenarlo.")

    with st.form("cliente"):
        st.markdown(f"**Las {len(G.CAMPOS) + len(G.CATEGORICAS)} variables del modelo final**, de la más a la menos importante:")
        datos = {}
        lista, _ = st.columns([3, 2])  # la lista ocupa solo parte del ancho para que se lea mejor
        with lista:
            for n, (campo, (etiqueta, entero)) in enumerate(G.CAMPOS.items(), 1):
                r = rangos[campo]
                log = "  ·  se le aplica log(x+1)" if f"log_{campo}" in G.VARIABLES_LOG else ""
                valor_col, dato_col = st.columns([4, 1], vertical_alignment="bottom")
                with valor_col:
                    if entero:
                        valor = st.number_input(f"{n}. {etiqueta}", min_value=0, value=int(round(r["mediana"])), step=1,
                                                help=f"En train va de {r['min']:,.0f} a {r['max']:,.0f}{log}.")
                    else:
                        valor = st.number_input(f"{n}. {etiqueta}", min_value=0.0, value=round(r["mediana"], 2),
                                                step=0.1, format="%.2f",
                                                help=f"En train va de {r['min']:,.2f} a {r['max']:,.2f}{log}.")
                with dato_col:
                    sin_dato = st.checkbox("Sin dato", key=f"sd_{campo}")
                datos[campo] = None if sin_dato else float(valor)
            for c in G.CATEGORICAS:
                n += 1
                datos[c] = st.selectbox(f"{n}. {G.NOMBRES_CATEGORICAS[c]}", opciones[c], index=opciones[c].index(moda[c]))
        enviado = st.form_submit_button("Calcular probabilidad", type="primary")

    if enviado:
        resultado = G.predecir(modelo, datos, columnas_num)
        prob = resultado["probabilidad"]
        campana = resultado["decision"] == G.CAMPANA
        a, b = st.columns([1, 2])
        a.metric("Probabilidad de churn (predicción)", f"{prob:.1%}")
        with b:
            (st.error if campana else st.success)(f"**Decisión:** {resultado['decision']}  \n"
                                                  f"Regla: probabilidad > {G.CORTE:.0%} → campaña.")
        fig = go.Figure(go.Bar(x=[prob], y=[""], orientation="h", marker_color=NARANJA if campana else CIAN,
                               hovertemplate="%{x:.1%}<extra></extra>"))
        fig.add_vline(x=G.CORTE, line_dash="dot", line_color=GRIS, annotation_text="corte 50%")
        fig.update_layout(height=110, margin=dict(l=10, r=10, t=20, b=10), showlegend=False,
                          xaxis=dict(range=[0, 1], tickformat=".0%"))
        st.plotly_chart(fig, width="stretch")
        fuera = [G.CAMPOS[c][0] for c, v in datos.items()
                 if c in rangos and v is not None and not rangos[c]["min"] <= v <= rangos[c]["max"]]
        if fuera:
            st.warning("Fuera del rango visto en train (la predicción es menos confiable): " + ", ".join(fuera))
        with st.expander("Ver lo que recibe el modelo (con logaritmos)"):
            fila = resultado["fila_modelo"].T.rename(columns={0: "Valor que recibe el modelo"})
            fila["Valor que recibe el modelo"] = fila["Valor que recibe el modelo"].astype(str)
            st.dataframe(fila, width="stretch")
