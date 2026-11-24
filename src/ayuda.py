"""
Ayuda del dashboard (retroalimentación del 12 de noviembre):
- Botón "?" junto al título de cada pantalla con una guía corta de uso.
- Botón "ⓘ" junto al título de cada gráfica que explica qué enseña, cómo leerla y qué decisión apoya.
RESPONSABLE: Sara Rivero

Nota: Streamlit no detecta el doble clic sobre una gráfica (Plotly usa el doble clic para regresar el zoom),
así que la explicación se abre con un clic en el botón "ⓘ" que está junto al título de cada gráfica.
"""
import streamlit as st

FILTROS = ("Los filtros del panel derecho (país, género y edad) se aplican a todas las pantallas y se "
           "conservan al cambiar de una a otra. *Criterios de riesgo* cambia la regla de carrito y llamadas. "
           "*Limpiar filtros* regresa a toda la base y a la regla oficial.")

GUIAS = {
    "resumen": {
        "para": "Ver en un minuto cómo está el abandono y qué está relacionado con él, antes de entrar al detalle.",
        "pasos": ["Lee primero la tarjeta **Situación actual**: abandono contra la meta y activos en riesgo.",
                  "Revisa los seis **hallazgos**: cada porcentaje es la tasa de abandono de ese grupo.",
                  "Usa la tabla **Pantallas del dashboard** para saber a dónde ir según la decisión que necesitas."],
        "indicadores": "Las tasas son históricas (clientes que ya abandonaron) y cambian con los filtros.",
    },
    "andrea": {
        "para": "Decidir a qué segmentos dirigir la campaña de retención.",
        "pasos": ["Revisa los dos KPI de arriba: tasa de abandono y activos en perfil de riesgo.",
                  "Debajo está el **peso de tu grupo** en el problema: cuánto del abandono y del riesgo está en "
                  "la selección de filtros.",
                  "En el mapa de carrito × llamadas ubica las celdas rojas: ahí se concentra el abandono.",
                  "En **Abandono por segmento** cambia la comparación (edad, país, ciudad o antigüedad)."],
        "indicadores": "Rojo = más abandono que el promedio del negocio; verde = menos. La meta de churn se "
                       "puede ajustar en la gráfica de meta.",
    },
    "luis": {
        "para": "Saber si hay alertas, si los datos son confiables y obtener la lista de clientes para campaña.",
        "pasos": ["Revisa las **alertas del modelo**: se encienden si tu selección tiene más riesgo que el negocio.",
                  "Para comprobar que funcionan, abre **Probar las alertas con datos modificados** y mueve los "
                  "controles: la alerta debe encenderse o apagarse.",
                  "La calidad de datos y el contrato de datos están más abajo.",
                  "La lista de clientes está oculta: ábrela o descárgala solo cuando la necesites."],
        "indicadores": "Riesgo alto = probabilidad de abandono del modelo de 70% o más. El umbral de cada alerta es "
                       "el valor de todo el negocio más 2 puntos.",
    },
    "carlos": {
        "para": "Saber si se están yendo los clientes valiosos y dónde conviene invertir.",
        "pasos": ["Compara el abandono de cada cuartil de Lifetime_Value contra el promedio.",
                  "Revisa la tabla por país para ver dónde hay más activos en riesgo.",
                  "Usa el escenario para estimar cuántos clientes se retendrían con una mejora supuesta."],
        "indicadores": "Lifetime_Value viene en escala logarítmica en el CSV: no es dinero. El ROI no se puede "
                       "calcular sin costos ni resultados de campañas.",
    },
    "clientes": {
        "para": "Decidir a qué clientes contactar primero, según su probabilidad de abandono y su segmento.",
        "pasos": ["En **Scoring de clientes** revisa cuántos activos hay en cada nivel de riesgo y descarga la lista.",
                  "En **Segmentos** consulta los 3 grupos de comportamiento y su validación estadística.",
                  "En **Modelo y variables** revisa qué tan bueno es el modelo y qué variables pesan más."],
        "indicadores": "Riesgo Alto ≥ 70% de probabilidad del Gradient Boosting, Medio de 40% a 70%, Bajo menos de 40%. Las métricas del "
                       "modelo usan toda la base y no cambian con los filtros.",
    },
    "segmentos": {
        "para": "Saber qué tipo de cliente se va más y a quién de cada segmento contactar primero.",
        "pasos": ["Compara el churn de los 3 segmentos en las tarjetas y en la gráfica de abandono.",
                  "Revisa qué parte de los activos de cada segmento está en riesgo alto, medio o bajo.",
                  "Elige un segmento y un nivel de riesgo para obtener su lista de contacto (oculta, con descarga)."],
        "indicadores": "Churn histórico: calculado del CSV. Segmento y nivel de riesgo: resultado del modelo, no son "
                       "datos observados.",
    },
    "modelos": {
        "para": "Comparar los cinco modelos de clasificación y calcular la probabilidad de abandono de un cliente con el campeón.",
        "pasos": ["En **Comparativa** revisa las métricas de cada modelo en test (o en validación).",
                  "En **Curva ROC** compara qué tan bien separa cada modelo a los que se van de los que se quedan.",
                  "En **Predecir un cliente** escribe sus datos en escala normal y pulsa **Calcular probabilidad**."],
        "indicadores": "Las métricas salen del notebook de comparación (train 80% limpio + log, test 20% sin imputar) y "
                       "no cambian con los filtros. La probabilidad es una predicción del Gradient Boosting; "
                       "si es mayor a 50% se manda la campaña «No te vayas».",
    },
    "asistente": {
        "para": "Preguntar en español a quién contactar, por qué y qué hacer, sin buscar en cada pantalla.",
        "pasos": ["Escribe una pregunta o usa una de las sugeridas de la derecha.",
                  "El agente consulta los datos filtrados y el modelo antes de responder.",
                  "Abre **Datos que consultó el agente** para ver de dónde salió la respuesta.",
                  "Cambia los filtros del panel derecho para preguntar por un grupo específico."],
        "indicadores": "Las cifras las calcula el dashboard; Gemini solo redacta. Las probabilidades son predicciones "
                       "del Gradient Boosting, no datos observados.",
    },
    "actualizacion": {
        "para": "Revisar si un archivo nuevo de clientes se puede usar, puntuarlo con el modelo y decidir si hay que reentrenar.",
        "pasos": ["Revisa el **estado actual**: base, modelo en uso y su AUC de referencia.",
                  "Sube un CSV nuevo o usa la **muestra de demostración**.",
                  "Si el contrato de datos lo rechaza, el mensaje dice qué columna o regla falló.",
                  "En **Monitoreo del modelo** compara el AUC y el recall contra la referencia.",
                  "Descarga la lista de clientes puntuados para la campaña."],
        "indicadores": "Se recomienda reentrenar si el AUC baja más de 0.03 contra la referencia. Una variable se "
                       "marca para revisar si su promedio cambia más de 10% frente a la base actual.",
    },
    "recomendaciones": {
        "para": "Decidir qué acciones tomar primero y cómo medir si funcionaron.",
        "pasos": ["La tabla de prioridades ordena las acciones; la 1 es por donde conviene empezar.",
                  "Cada tarjeta dice qué hacer, el dato que lo respalda, a cuántos activos aplica y cómo medirlo."],
        "indicadores": "Un cliente puede estar en varios grupos: los activos de cada acción no se suman.",
    },
}


def titulo_pantalla(titulo, clave, subtitulo):
    """Título de la pantalla con el botón "?" de ayuda a la derecha."""
    izquierda, derecha = st.columns([12, 1], vertical_alignment="center")
    with izquierda:
        st.markdown(f'<h2 class="seccion-titulo">{titulo}</h2>', unsafe_allow_html=True)
    guia = GUIAS[clave]
    with derecha:
        with st.popover("?", help="Cómo usar esta pantalla", use_container_width=True):
            st.markdown(f"**Cómo usar: {titulo}**")
            st.markdown(f"**Para qué sirve:** {guia['para']}")
            st.markdown("\n".join(f"{i}. {p}" for i, p in enumerate(guia["pasos"], 1)))
            st.markdown(f"**Cómo leer los indicadores:** {guia['indicadores']}")
            st.caption(FILTROS)
    st.caption(subtitulo)


def titulo_grafica(texto, que_muestra, como_leer, decision, nivel="###"):
    """Título de una gráfica con el botón "ⓘ" que explica lo que enseña."""
    izquierda, derecha = st.columns([6, 1], vertical_alignment="center")
    with izquierda:
        st.markdown(f"{nivel} {texto}" if nivel else texto)
    with derecha:
        with st.popover("ⓘ", help="Qué enseña esta gráfica", use_container_width=True):
            st.markdown(f"**Qué enseña:** {que_muestra}")
            st.markdown(f"**Cómo leerla:** {como_leer}")
            st.markdown(f"**Decisión que apoya:** {decision}")
