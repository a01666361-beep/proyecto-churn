"""
Pantalla · Asistente de retención (agente de IA).
Decisión: responder en lenguaje natural a quién contactar, por qué y qué acción tomar, con los datos del dashboard.
El agente (src/agente.py) usa Gemini con llamadas a funciones: Gemini decide qué consultar y Python calcula las cifras.
Agregado el 24-nov para cubrir el elemento "AI Agents" de la rúbrica.
"""
import requests
import streamlit as st

from src import agente as A
from src import ayuda
from src.contexto import contexto
from src.puntuacion import modelo_y_puntuacion

c = contexto()
resultado, puntuado_total = modelo_y_puntuacion()
puntuado = puntuado_total.loc[c.df_filtrado.index]  # el agente respeta los filtros del panel derecho

ayuda.titulo_pantalla("Asistente de retención (IA)", "asistente",
                      "Pregunta en español: el agente consulta los datos y el modelo del dashboard antes de responder · "
                      f"{len(puntuado):,} de {len(puntuado_total):,} clientes en el grupo seleccionado")

try:
    CLAVE = st.secrets.get("GEMINI_API_KEY", "")
except Exception:  # sin archivo de secretos
    CLAVE = ""

if not CLAVE:
    st.warning("Falta configurar la clave de Gemini. En Streamlit Cloud: **Manage app → Settings → Secrets** y "
               "escribe `GEMINI_API_KEY = \"tu_clave\"`. En tu compu: crea `.streamlit/secrets.toml` con la misma línea "
               "(ese archivo no se sube a GitHub).")
    st.stop()

if "chat_agente" not in st.session_state:
    st.session_state["chat_agente"] = []  # [{"rol", "texto", "herramientas"}]


def enviar(cuerpo):
    """Usa el primer modelo de Gemini que responda a tiempo y recuerda cuál funcionó.

    Si un modelo no existe para esta clave (404), está saturado (429/503) o tarda demasiado, se prueba el siguiente.
    """
    elegido = st.session_state.get("modelo_gemini")
    modelos = [elegido] + [m for m in A.MODELOS if m != elegido] if elegido else list(A.MODELOS)
    ultimo_error = None
    for modelo in modelos:
        try:
            datos = A.enviar_gemini(CLAVE, cuerpo, modelo)
            st.session_state["modelo_gemini"] = modelo
            return datos
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            ultimo_error = exc
        except RuntimeError as exc:
            ultimo_error = exc
            if not any(c in str(exc) for c in (" 400", " 404", " 429", " 500", " 503")) and "not found" not in str(exc).lower():
                raise
    raise ultimo_error


izquierda, derecha = st.columns([3, 1], gap="large")
with derecha:
    with st.container(border=True):
        st.markdown("**Cómo funciona**")
        st.caption("1. Escribes una pregunta.\n\n2. Gemini decide qué herramientas usar: resumen, lista de clientes, "
                   "explicación de un cliente, segmentos, churn por grupo o métricas del modelo.\n\n3. Python calcula "
                   "las cifras con los datos filtrados.\n\n4. Gemini redacta la respuesta solo con esas cifras.")
    if st.session_state.get("modelo_gemini"):
        st.caption(f"Modelo: {st.session_state['modelo_gemini']}")
    st.markdown("**Prueba con:**")
    sugerencias = ["¿Cómo estamos contra la meta de churn?",
                   "¿A qué 5 clientes debo contactar primero y por qué?",
                   "¿Qué segmento tiene más abandono y qué acción recomiendas?",
                   "¿En qué país hay más activos en riesgo alto?",
                   "¿Qué tan confiable es el modelo?"]
    elegida = None
    for s in sugerencias:
        if st.button(s, use_container_width=True):
            elegida = s
    if st.button("Borrar conversación", use_container_width=True):
        st.session_state["chat_agente"] = []
        st.rerun()

with izquierda:
    for mensaje in st.session_state["chat_agente"]:
        with st.chat_message("user" if mensaje["rol"] == "user" else "assistant"):
            st.markdown(mensaje["texto"])
            if mensaje.get("herramientas"):
                with st.expander("Datos que consultó el agente"):
                    for h in mensaje["herramientas"]:
                        argumentos = ", ".join(f"{k} = {v}" for k, v in h["argumentos"].items()) or "sin parámetros"
                        st.caption(f"`{h['herramienta']}` ({argumentos})")

    pregunta = st.chat_input("Escribe tu pregunta sobre clientes, segmentos o el modelo…") or elegida
    if pregunta:
        with st.chat_message("user"):
            st.markdown(pregunta)
        historial = [{"role": "user" if m["rol"] == "user" else "model", "parts": [{"text": m["texto"]}]}
                     for m in st.session_state["chat_agente"][-8:]]
        with st.chat_message("assistant"):
            with st.spinner("Consultando los datos…"):
                try:
                    texto, usadas = A.responder(pregunta, historial,
                                                A.Herramientas(puntuado, resultado, c.regla), enviar)
                except Exception as exc:
                    texto, usadas = (f"No pude conectarme con Gemini ({exc}). Revisa la clave en Secrets o intenta "
                                     "de nuevo en un momento."), []
            st.markdown(texto)
            if usadas:
                with st.expander("Datos que consultó el agente"):
                    for h in usadas:
                        argumentos = ", ".join(f"{k} = {v}" for k, v in h["argumentos"].items()) or "sin parámetros"
                        st.caption(f"`{h['herramienta']}` ({argumentos})")
        st.session_state["chat_agente"] += [{"rol": "user", "texto": pregunta},
                                            {"rol": "assistant", "texto": texto, "herramientas": usadas}]

st.caption("Las respuestas las redacta un modelo de lenguaje (Gemini) con cifras calculadas por el dashboard. "
           "Las probabilidades son predicciones del modelo, no datos observados, y las relaciones no son causas. "
           "Verifica las cifras importantes en la pantalla correspondiente antes de decidir.")
