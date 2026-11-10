"""
Pantalla 04 · Recomendaciones finales.
Pregunta: ¿qué acciones conviene tomar primero, a cuántos clientes activos llegan y cómo se mide si funcionaron?
RESPONSABLE: (poner nombre)
"""
import streamlit as st

from src.contexto import contexto
from src.resumen import recomendaciones, tabla_recomendaciones

c = contexto()
df, df_general, regla = c.df_filtrado, c.df, c.regla

st.markdown('<h2 class="seccion-titulo">Recomendaciones finales</h2>', unsafe_allow_html=True)
st.caption("Acciones ordenadas por prioridad, cada una con el dato que la respalda · "
           f"{len(df):,} de {len(df_general):,} clientes en el grupo seleccionado")

lista = recomendaciones(df, df_general, regla)
if not lista:
    st.info("No hay clientes activos con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

# ------------------------------------------------------------------ Resumen de prioridades
with st.container(border=True):
    st.markdown("### Prioridades")
    st.dataframe(tabla_recomendaciones(lista), hide_index=True, use_container_width=True,
                 column_config={"Activos a contactar": st.column_config.NumberColumn(format="localized")})
    st.caption("Un mismo cliente puede estar en varios grupos, así que los activos de cada fila no se suman. "
               "La prioridad 1 combina las dos señales más fuertes (carrito y llamadas): por ahí conviene empezar.")

# ------------------------------------------------------------------ Detalle
for numero, rec in enumerate(lista, 1):
    with st.container(border=True):
        st.markdown(f"### {numero}. {rec['titulo']}")
        izquierda, derecha = st.columns([2, 1], gap="medium")
        with izquierda:
            st.markdown(f"**Qué hacer:** {rec['accion']}")
            st.markdown(f"**Por qué:** {rec['por_que']}")
            st.markdown(f"**Cómo medirlo:** {rec['medir']}")
        with derecha:
            st.metric("Activos a quienes aplica", f"{rec['a_quien']:,}")
            st.caption(f"Dónde verlo: {rec['pantalla']}")

# ------------------------------------------------------------------ Siguientes pasos
with st.container(border=True):
    st.markdown("### Siguientes pasos y límites")
    st.markdown("""
- **Medir con un grupo de control:** contactar a una parte del grupo y dejar otra sin contactar, para saber si la campaña redujo el abandono o si solo coincidió.
- **Registrar fechas y resultados de cada campaña:** hoy la base no tiene fechas, así que no se puede ver una tendencia ni un antes y después.
- **Agregar costos e ingresos:** sin ellos no se puede calcular el ROI ni decidir cuánto presupuesto asignar a cada acción.
- **Modelo predictivo:** la siguiente iteración agregará una probabilidad individual de abandono para ordenar mejor la lista de contacto.
""")
    st.caption("Las recomendaciones salen de relaciones observadas en los datos, no de causas comprobadas. "
               "Se recalculan con los filtros y la regla de riesgo del panel derecho.")
