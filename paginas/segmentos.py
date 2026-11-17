"""
Pantalla 06 · Segmentos de clientes.
Decisión: qué tipo de cliente se va más, cuánto pesa cada segmento y a quién de cada segmento
conviene contactar primero.
RESPONSABLE: Víctor García (A01784206)

Usa los segmentos K-Means y el modelo de src/modelo.py (los mismos de la pantalla 05), así que
el segmento y la probabilidad de cada cliente coinciden en las dos pantallas.
Origen de cada cifra:
- Clientes, activos y churn histórico: calculados a partir del CSV.
- Segmento, probabilidad y nivel de riesgo: resultado del modelo, no son datos observados.
"""
import plotly.graph_objects as go
import streamlit as st

from src import ayuda
from src import modelo as M
from src.config import AZUL, GRIS, LINEA, NARANJA, ROJO, VERDE
from src.contexto import contexto
from src.puntuacion import modelo_y_puntuacion
from src.tablas_datos import configuracion_columnas

c = contexto()
_, puntuado_total = modelo_y_puntuacion()
puntuado = puntuado_total.loc[c.df_filtrado.index]  # respeta los filtros de la derecha

ayuda.titulo_pantalla("Segmentos de clientes", "segmentos",
                      f"Tres tipos de cliente según su comportamiento (K-Means) · {len(puntuado):,} de "
                      f"{len(puntuado_total):,} clientes en el grupo seleccionado")

if puntuado.empty:
    st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

perfil = M.perfil_segmentos(puntuado)
tasa_seleccion = puntuado["Churned"].mean()

# ------------------------------------------------------------------ Tarjetas por segmento
columnas = st.columns(len(perfil), gap="medium")
for columna, (_, fila) in zip(columnas, perfil.iterrows()):
    diferencia = fila["Churn histórico (%)"] - tasa_seleccion * 100
    color = ROJO if diferencia > 0 else VERDE
    with columna, st.container(border=True):
        st.markdown(f"**{fila['Segmento']}**")
        st.markdown(f'<div class="kpi-valor">{fila["Churn histórico (%)"]:.1f}%</div>', unsafe_allow_html=True)
        st.markdown(f'<span style="color:{color}; font-weight:700; font-size:0.85rem">'
                    f'{"▲" if diferencia > 0 else "▼"} {abs(diferencia):.1f} pts vs. la selección '
                    f'({tasa_seleccion:.1%})</span>', unsafe_allow_html=True)
        st.caption(f"churn histórico · {fila['Clientes']:,} clientes ({fila['Clientes'] / len(puntuado):.0%} de la selección)")
        st.caption(f"**{fila['Activos en riesgo alto']:,}** activos en riesgo alto según el modelo")
        st.caption(fila["Descripción"])
st.caption("Churn histórico: calculado a partir del CSV. Segmento y riesgo alto: resultado del modelo.")

# ------------------------------------------------------------------ Gráficas
izquierda, derecha = st.columns(2, gap="large")
with izquierda:
    mayor_seg = perfil.loc[perfil["Churn histórico (%)"].idxmax()]
    ayuda.titulo_grafica(
        f"Abandono por segmento: {mayor_seg['Segmento']} con {mayor_seg['Churn histórico (%)']:.1f}%",
        "La tasa de abandono histórica de cada segmento contra la de la selección.",
        "Naranja: el segmento abandona más que la selección (línea punteada); azul: menos.",
        "Qué segmento atender primero.", nivel="####")
    fig = go.Figure(go.Bar(
        x=perfil["Segmento"], y=perfil["Churn histórico (%)"],
        marker_color=[ROJO if v > tasa_seleccion * 100 else AZUL for v in perfil["Churn histórico (%)"]],
        text=[f"{v:.1f}%" for v in perfil["Churn histórico (%)"]], textposition="outside",
        hovertemplate="%{x}: %{y:.1f}% de churn<extra></extra>"))
    fig.add_hline(y=tasa_seleccion * 100, line_dash="dash", line_color=GRIS,
                  annotation_text=f"Selección {tasa_seleccion:.1%}", annotation_position="top left")
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10), yaxis_title="Churn histórico (%)",
                      )
    st.plotly_chart(fig, width="stretch")
    st.caption("Naranja: abandona más que el promedio de la selección. Calculado a partir del CSV.")

with derecha:
    ayuda.titulo_grafica(
        "Activos de cada segmento por nivel de riesgo",
        "Qué porcentaje de los clientes activos de cada segmento tiene riesgo alto, medio o bajo según el modelo.",
        "Cada barra suma 100%. La parte naranja son los activos con riesgo alto.",
        "Dónde está el volumen de clientes que conviene contactar.", nivel="####")
    activos = puntuado[puntuado["Churned"] == 0]
    mezcla = (activos.groupby(["Segmento", "Nivel_Riesgo"]).size().unstack(fill_value=0)
              .reindex(index=perfil["Segmento"], columns=M.NIVELES, fill_value=0))
    porcentaje = mezcla.div(mezcla.sum(axis=1).where(lambda s: s > 0, 1), axis=0) * 100
    colores = {"Alto": NARANJA, "Medio": AZUL, "Bajo": LINEA}
    fig = go.Figure()
    for nivel in M.NIVELES:
        fig.add_bar(name=f"Riesgo {nivel.lower()}", x=porcentaje.index, y=porcentaje[nivel],
                    marker_color=colores[nivel], customdata=mezcla[nivel],
                    hovertemplate="%{x} · riesgo " + nivel.lower() + ": %{y:.1f}% (%{customdata:,} activos)<extra></extra>")
    fig.update_layout(barmode="stack", height=340, margin=dict(l=10, r=10, t=40, b=10),
                      yaxis_title="% de los activos del segmento", legend_orientation="h", legend_y=-0.15)
    st.plotly_chart(fig, width="stretch")
    st.caption("Solo clientes activos. Nivel de riesgo: resultado del modelo, no es dato observado.")

# ------------------------------------------------------------------ A quién contactar
st.markdown("#### Clientes a contactar primero en cada segmento")
uno, dos = st.columns([1, 2])
with uno:
    mayor = int(perfil["Churn histórico (%)"].idxmax())  # empieza por el que más abandona
    elegido = st.selectbox("Segmento", perfil["Segmento"].tolist(), index=mayor, key="seg_elegido")
with dos:
    niveles = st.multiselect("Nivel de riesgo", M.NIVELES, default=["Alto"], placeholder="Todos", key="seg_niveles")

tabla = M.tabla_scoring(puntuado[puntuado["Segmento"] == elegido], solo_activos=True, niveles=niveles)
st.markdown(f"**{len(tabla):,} clientes activos** del segmento **{elegido}**, de mayor a menor probabilidad de abandono.")
# Retroalimentación 12-nov: la lista queda oculta; se abre o se descarga solo cuando se necesita.
with st.expander("Ver la lista de clientes del segmento (oculta)"):
    st.dataframe(
        tabla, column_order=list(tabla.columns), hide_index=True, width="stretch", height=360,
        column_config={**configuracion_columnas(tabla),
                       "Probabilidad de churn (%)": st.column_config.ProgressColumn(
                           min_value=0, max_value=100, format="%.1f%%",
                           help="Origen: resultado estimado por el modelo, no es dato observado")})
st.download_button("Descargar lista del segmento (CSV)", tabla.to_csv(index=False).encode("utf-8-sig"),
                   file_name=f"clientes_{elegido.lower()}.csv", mime="text/csv", disabled=tabla.empty)
st.caption("Para ver por qué un cliente tiene ese riesgo, búscalo en la pantalla Clientes prioritarios (Explicación por cliente).")
