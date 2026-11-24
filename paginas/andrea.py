"""
Pantalla 01 · Andrea López, gerente de retención.
Decisión: a qué segmentos dirigir la campaña de retención.
RESPONSABLE: (poner nombre)
"""
import plotly.graph_objects as go
import streamlit as st

from src import ayuda, seccion_grupo, seccion_kpis, ventanas
from src.config import AZUL, META_CHURN, MINIMO_SEGMENTO, ROJO, VERDE
from src.contexto import contexto
from src.graficas import separar_panel
from src.seccion_factores import figura_factores
from src.seccion_riesgo import figura_riesgo
from src.indicadores import resumen_riesgo
from src.vistas import DIMENSIONES, churn_por_segmento

c = contexto()
df, df_general, regla, tasa_global = c.df_filtrado, c.df, c.regla, c.tasa_global
SIN_BARRA = {"displayModeBar": False}

ayuda.titulo_pantalla("Panorama para priorizar campañas", "andrea",
                      "Concentración del abandono por segmento y por perfil de riesgo · "
                      f"{len(df):,} de {len(df_general):,} clientes en el grupo seleccionado")

# Dos KPI: tasa de abandono y activos en perfil de riesgo (se quitó la tarjeta de clientes por retroalimentación)
k1, k2 = st.columns(2, gap="medium")
with k1:
    seccion_kpis.tarjeta_churn(df, tasa_global, df_general)
with k2:
    seccion_kpis.tarjeta_riesgo(df, regla, df_general)

if df.empty:
    st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

# Retroalimentación 12-nov: el peso del grupo seleccionado en el problema sube junto a los KPI.
seccion_grupo.mostrar(df, df_general, regla, {
    "País": st.session_state.get("f_pais", []),
    "Género": st.session_state.get("f_genero", []),
    "Edad": st.session_state.get("f_edad", []),
})

tasa = df["Churned"].mean() * 100
izquierda, derecha = st.columns([1, 1.25], gap="medium")
with izquierda:
    with st.container(border=True, key="grafica_meta"):
        meta_actual = st.session_state.get("a_meta", META_CHURN * 100)
        ayuda.titulo_grafica(
            f"Abandono {tasa:.1f}% vs. meta {meta_actual:.1f}%",
            "La tasa de abandono del grupo seleccionado comparada con la meta de churn, y la proporción de activos "
            "contra los que ya abandonaron.",
            "La barra es el abandono actual y la línea azul la meta. Barra naranja: estamos arriba de la meta; cian: abajo.",
            "Qué tan urgente es la campaña de retención para este grupo.")
        meta = st.number_input("Meta de churn (%)", min_value=0.0, max_value=100.0,
                               value=META_CHURN * 100, step=0.5, key="a_meta",
                               help="Meta propuesta por el equipo; Andrea la puede ajustar.")
        bala = go.Figure(go.Indicator(
            mode="number+gauge+delta", value=tasa,
            number={"suffix": "%", "valueformat": ".1f"},
            delta={"reference": meta, "valueformat": ".1f", "suffix": " pts vs. meta",
                   "increasing": {"color": ROJO}, "decreasing": {"color": VERDE}},
            gauge={"shape": "bullet", "axis": {"range": [0, max(50, tasa + 10)], "ticksuffix": "%"},
                   "bar": {"color": ROJO if tasa > meta else VERDE},
                   "threshold": {"line": {"color": AZUL, "width": 3}, "thickness": 0.9, "value": meta}},
        ))
        bala.update_layout(height=130, margin=dict(l=10, r=20, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(bala, key="bala", use_container_width=True, config=SIN_BARRA)
        dona = go.Figure(go.Pie(
            labels=["Activos", "Abandonaron"],
            values=[int((df["Churned"] == 0).sum()), int(df["Churned"].sum())],
            hole=0.62, sort=False, marker_colors=[AZUL, ROJO], textinfo="percent",
            hovertemplate="%{label}: %{value:,} clientes<extra></extra>"))
        dona.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), showlegend=True,
                           legend=dict(orientation="h", y=-0.05), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(dona, key="dona", use_container_width=True, config=SIN_BARRA)
        st.caption(f"Línea azul: meta ({meta:.1f}%). Barra naranja si el churn está arriba de la meta, cian si está abajo.")

with derecha:
    with st.container(border=True, key="grafica_mapa"):
        corr = df[["Cart_Abandonment_Rate", "Customer_Service_Calls"]].corrwith(df["Churned"])
        perfil = resumen_riesgo(df, regla)
        ayuda.titulo_grafica(
            f"Carrito y llamadas: {perfil['tasa_historica']:.1%} de abandono en el perfil de riesgo "
            f"(r = {corr['Cart_Abandonment_Rate']:.2f} y {corr['Customer_Service_Calls']:.2f})",
            "El abandono para cada combinación de carrito abandonado y llamadas a servicio, y los activos en riesgo "
            "por país.",
            "Cada celda es la tasa de abandono de esa combinación: naranja = alta, cian = baja. r es la correlación de "
            "cada variable con el abandono (de −1 a 1).",
            "De aquí sale la regla de riesgo que define a quién contactar.")
        mapa = separar_panel(figura_riesgo(df, regla), 1, alto=390)
        st.plotly_chart(mapa, key="mapa", use_container_width=True, config=SIN_BARRA)
        st.caption(f"De aquí sale la regla de riesgo: carrito > {regla['carrito_min']:.2f}% y "
                   f"{regla['llamadas_min']} o más llamadas. Pasa el cursor para ver cuántos clientes hay en cada celda.")

with st.container(border=True, key="grafica_segmentos"):
    dimension = st.session_state.get("a_dimension", list(DIMENSIONES)[0])
    tabla = churn_por_segmento(df, dimension)
    ayuda.titulo_grafica(
        (f"Abandono por {dimension.lower()}: {tabla.iloc[0]['segmento']} con {tabla.iloc[0]['tasa']:.1%} "
         f"(negocio {tasa_global:.1%})") if not tabla.empty else f"Abandono por {dimension.lower()}",
        "La tasa de abandono y el tamaño de cada segmento.",
        "Barras naranjas: el segmento abandona más que el negocio; cian: menos. La línea punteada es el churn global. "
        "La etiqueta muestra tasa · clientes.",
        "A qué segmentos dirigir primero la campaña, considerando también su tamaño.")
    st.radio("Comparar por", list(DIMENSIONES), horizontal=True, key="a_dimension")
    if tabla.empty:
        st.info(f"Ningún segmento tiene {MINIMO_SEGMENTO} clientes o más con estos filtros.")
    else:
        orden = tabla.sort_values("tasa")  # Plotly dibuja de abajo hacia arriba
        barras = go.Figure(go.Bar(
            x=orden["tasa"] * 100, y=orden["segmento"], orientation="h",
            marker_color=[ROJO if t > tasa_global else VERDE for t in orden["tasa"]],
            text=[f"{t:.1%} · {n:,}" for t, n in zip(orden["tasa"], orden["clientes"])],
            textposition="outside", cliponaxis=False, customdata=orden["clientes"],
            hovertemplate="%{y}: %{x:.1f}% de churn<br>%{customdata:,} clientes<extra></extra>"))
        barras.add_vline(x=tasa_global * 100, line_dash="dot", line_color=AZUL, line_width=1.5)
        barras.update_layout(height=max(260, 26 * len(orden)), margin=dict(l=0, r=60, t=10, b=10),
                             xaxis=dict(range=[0, max(60, orden["tasa"].max() * 100 + 12)], ticksuffix="%",
                                        gridcolor="rgba(128,128,128,0.15)"),
                             paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(barras, key="segmentos", use_container_width=True, config=SIN_BARRA)
        st.caption(f"Etiqueta: tasa de churn · clientes. Línea punteada: churn global ({tasa_global:.1%}), "
                   f"es referencia, no meta. Solo segmentos con {MINIMO_SEGMENTO} clientes o más.")
        exportar = tabla.assign(tasa=(tabla["tasa"] * 100).round(2), meta=meta,
                                churn_global=round(tasa_global * 100, 2))
        st.download_button("Exportar segmentos (CSV)", exportar.to_csv(index=False).encode("utf-8"),
                           file_name=f"segmentos_{dimension.lower()}.csv", mime="text/csv")

with st.expander("Comportamientos relacionados: llamadas y días sin comprar"):
    ayuda.titulo_grafica(
        "Llamadas y días sin comprar contra el abandono",
        "Cómo cambia el abandono según el número de llamadas a servicio y los días desde la última compra.",
        "Cada barra es la tasa de abandono del rango; la línea punteada es el churn del negocio. "
        "El título de cada gráfica trae su correlación r con el abandono.",
        "Qué comportamiento usar como disparador de una acción de retención.", nivel="####")
    factores = figura_factores(df, tasa_global)
    a, b = st.columns(2, gap="medium")
    with a:
        st.plotly_chart(separar_panel(factores, 1), key="llamadas", use_container_width=True, config=SIN_BARRA)
    with b:
        st.plotly_chart(separar_panel(factores, 3), key="dias", use_container_width=True, config=SIN_BARRA)
    st.caption("Cian: menor abandono que el negocio; naranja: mayor.")

if st.button("Todas las variables"):
    ventanas.ventana_variables(df, tasa_global)

st.caption("Límites: la base no tiene fechas ni resultados de campañas, así que todavía no se puede ver "
           "una tendencia ni medir un antes y después. Los datos muestran relaciones, no causas.")
