"""
Agente de IA de retención (Gemini con llamadas a funciones). Sin Streamlit, para poder probarlo.
Agregado el 24-nov para cubrir el elemento "AI Agents" de la rúbrica.

Cómo funciona:
- El usuario hace una pregunta en español.
- Gemini decide qué herramientas llamar (funciones de este archivo que consultan los datos del dashboard,
  ya filtrados por país, género y edad) y con qué parámetros.
- El agente ejecuta esas funciones en Python y le regresa los resultados a Gemini, hasta 5 vueltas.
- Gemini redacta la respuesta solo con esos datos. Las cifras salen del CSV, de cálculos o del modelo,
  nunca de lo que el modelo de lenguaje "sepa".

La clave se lee de st.secrets["GEMINI_API_KEY"] en la página; nunca se guarda en el código ni en GitHub.
"""
import json

import numpy as np
import pandas as pd
import requests

from src import modelo as M
from src.config import META_CHURN, META_RIESGO
from src.indicadores import resumen_riesgo

URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
# Se prueban en orden; se usa el primero que responda a tiempo (Google retiró gemini-2.x en 2026).
MODELOS = ["gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-flash-latest"]
MAX_VUELTAS = 5

INSTRUCCIONES = f"""Eres el asistente de retención de CartPulse Analytics, un e-commerce. Ayudas al equipo
(Andrea, gerente de retención; Luis, operaciones de datos y CRM; Carlos, estrategia y valor) a decidir a qué
clientes contactar y qué acciones tomar para reducir el abandono (churn).

Reglas:
- Responde siempre en español, claro y breve (máximo unos 8 renglones o una lista corta).
- Usa SOLO los datos que regresan las herramientas. Nunca inventes cifras, clientes ni porcentajes.
  Si la pregunta no se puede responder con las herramientas, dilo.
- Las probabilidades son predicciones del modelo Gradient Boosting, no datos observados. Las relaciones
  entre variables no son causas.
- Lifetime_Value y Average_Order_Value no tienen moneda documentada: no hables de pesos ni dólares.
- La meta de churn es {META_CHURN:.0%} y la meta de activos en perfil de riesgo es menos de {META_RIESGO:.1%}.
- Los datos respetan los filtros que el usuario eligió en el panel derecho del dashboard.
- Cuando recomiendes una acción, di a cuántos clientes aplica y en qué dato te basas.
"""

HERRAMIENTAS = [
    {"name": "resumen_general",
     "description": "Panorama del grupo filtrado: clientes, churn, activos, activos por nivel de riesgo del modelo y "
                    "activos en el perfil de riesgo (carrito alto y muchas llamadas).",
     "parameters": {"type": "object", "properties": {}}},
    {"name": "clientes_prioritarios",
     "description": "Lista de clientes ACTIVOS ordenados de mayor a menor probabilidad de abandono, con sus variables clave.",
     "parameters": {"type": "object", "properties": {
         "n": {"type": "integer", "description": "Cuántos clientes regresar (1 a 20). Por defecto 10."},
         "nivel": {"type": "string", "enum": ["Alto", "Medio", "Bajo"], "description": "Nivel de riesgo (opcional)."},
         "segmento": {"type": "string", "enum": M.NOMBRES_SEGMENTO, "description": "Segmento K-Means (opcional)."},
         "pais": {"type": "string", "description": "País en inglés, por ejemplo USA, UK, Germany (opcional)."}}}},
    {"name": "explicar_cliente",
     "description": "Por qué el modelo le da esa probabilidad a un cliente: las 5 variables que más la mueven.",
     "parameters": {"type": "object", "properties": {
         "cliente_id": {"type": "string", "description": "Identificador, por ejemplo C00665."}},
         "required": ["cliente_id"]}},
    {"name": "perfil_segmentos",
     "description": "Los 3 segmentos de clientes (K-Means): tamaño, churn, activos en riesgo alto y comportamiento promedio.",
     "parameters": {"type": "object", "properties": {}}},
    {"name": "churn_por_grupo",
     "description": "Churn histórico y activos en riesgo alto por grupo de una variable.",
     "parameters": {"type": "object", "properties": {
         "variable": {"type": "string", "enum": ["País", "Género", "Edad", "Segmento", "Ciudad"]}},
         "required": ["variable"]}},
    {"name": "desempeno_modelo",
     "description": "Métricas del modelo campeón (Gradient Boosting) en el conjunto de prueba.",
     "parameters": {"type": "object", "properties": {}}},
]

COLUMNA_GRUPO = {"País": "Country", "Género": "Gender", "Edad": "Grupo_Edad", "Segmento": "Segmento", "Ciudad": "City"}


def _limpio(valor):
    """Convierte números de numpy y pandas a tipos que se pueden mandar como JSON."""
    if isinstance(valor, dict):
        return {k: _limpio(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_limpio(v) for v in valor]
    if isinstance(valor, (np.integer,)):
        return int(valor)
    if isinstance(valor, (np.floating, float)):
        return None if np.isnan(valor) else round(float(valor), 4)
    return valor


class Herramientas:
    """Funciones que el agente puede llamar. Todas trabajan sobre los clientes ya filtrados."""

    def __init__(self, puntuado, resultado, regla):
        self.df = puntuado
        self.resultado = resultado
        self.regla = regla

    def resumen_general(self):
        activos = self.df[self.df["Churned"] == 0]
        riesgo = resumen_riesgo(self.df, self.regla) if len(self.df) else {}
        return {"clientes": len(self.df), "churn_historico": self.df["Churned"].mean() if len(self.df) else None,
                "meta_churn": META_CHURN, "activos": len(activos),
                "activos_por_nivel_de_riesgo": activos["Nivel_Riesgo"].value_counts().to_dict(),
                "activos_que_recibirian_campana": int((activos["Probabilidad"] > self.resultado["corte"]).sum()),
                "regla_de_campana": f"probabilidad > {self.resultado['corte']:.0%}",
                "activos_en_perfil_de_riesgo": riesgo.get("activos_en_perfil"),
                "pct_activos_en_perfil_de_riesgo": riesgo.get("pct_activos"),
                "meta_perfil_de_riesgo": META_RIESGO,
                "definicion_perfil": f"carrito abandonado > {self.regla['carrito_min']}% y "
                                     f"{self.regla['llamadas_min']} o más llamadas a servicio"}

    def clientes_prioritarios(self, n=10, nivel=None, segmento=None, pais=None):
        t = self.df[self.df["Churned"] == 0]
        if nivel:
            t = t[t["Nivel_Riesgo"] == nivel]
        if segmento:
            t = t[t["Segmento"] == segmento]
        if pais:
            t = t[t["Country"].str.lower() == str(pais).lower()]
        t = t.sort_values("Probabilidad", ascending=False).head(max(1, min(int(n or 10), 20)))
        return {"total_que_cumplen": int(len(t)), "clientes": [
            {"cliente": r.Customer_ID, "probabilidad": r.Probabilidad, "nivel": r.Nivel_Riesgo, "segmento": r.Segmento,
             "pais": r.Country, "edad": r.Age, "carrito_abandonado_pct": r.Cart_Abandonment_Rate,
             "llamadas_servicio": r.Customer_Service_Calls, "dias_sin_comprar": r.Dias_Sin_Comprar}
            for r in t.itertuples()]}

    def explicar_cliente(self, cliente_id):
        cliente_id = str(cliente_id).strip().upper()
        if cliente_id not in set(self.df["Customer_ID"]):
            return {"error": f"El cliente {cliente_id} no existe o no está en los filtros actuales."}
        tabla, base = M.explicar_cliente_campeon(self.resultado["modelo"], self.df, cliente_id, n=5)
        fila = self.df[self.df["Customer_ID"] == cliente_id].iloc[0]
        return {"cliente": cliente_id, "probabilidad": base["probabilidad"], "nivel": fila["Nivel_Riesgo"],
                "segmento": fila["Segmento"], "estado": "abandonó" if fila["Churned"] == 1 else "activo",
                "probabilidad_cliente_promedio": base["probabilidad_promedio"],
                "variables": tabla.rename(columns={"Aporte": "aporte_puntos_porcentuales"}).to_dict(orient="records"),
                "como_leer": "aporte = probabilidad del cliente menos la probabilidad si esa variable tuviera el valor típico"}

    def perfil_segmentos(self):
        if self.df.empty:
            return {"error": "No hay clientes con estos filtros."}
        return {"segmentos": M.perfil_segmentos(self.df).to_dict(orient="records")}

    def churn_por_grupo(self, variable):
        col = COLUMNA_GRUPO.get(variable)
        if col is None:
            return {"error": f"Variable no disponible: {variable}"}
        g = self.df.groupby(col)
        tabla = pd.DataFrame({
            "clientes": g.size(), "churn_historico": g["Churned"].mean(),
            "activos_riesgo_alto": g.apply(lambda x: int(((x["Churned"] == 0) & (x["Nivel_Riesgo"] == "Alto")).sum()),
                                           include_groups=False)})
        tabla = tabla[tabla["clientes"] >= 30].sort_values("churn_historico", ascending=False)
        return {"variable": variable, "churn_del_grupo_filtrado": self.df["Churned"].mean(),
                "grupos": tabla.reset_index().rename(columns={col: "grupo"}).to_dict(orient="records")}

    def desempeno_modelo(self):
        return {"modelo": "Gradient Boosting", "metricas_test": self.resultado["metricas"],
                "matriz_confusion_test": self.resultado["matriz"], "clientes_entrenamiento": self.resultado["n_train"],
                "clientes_prueba": self.resultado["n_test"],
                "nota": "Gano la comparativa contra bosque aleatorio, red neuronal, arbol y regresion logistica."}

    def ejecutar(self, nombre, argumentos):
        funcion = getattr(self, nombre, None)
        if nombre not in {h["name"] for h in HERRAMIENTAS} or funcion is None:
            return {"error": f"Herramienta desconocida: {nombre}"}
        try:
            return _limpio(funcion(**(argumentos or {})))
        except Exception as exc:  # el agente recibe el error y puede corregir
            return {"error": f"{type(exc).__name__}: {exc}"}


def enviar_gemini(clave, cuerpo, modelo, timeout=25):
    """Llama a la API de Gemini (REST). Regresa el JSON de respuesta o lanza un error legible."""
    if modelo.startswith("gemini-3"):  # razonamiento corto: respuestas en segundos, no en minutos
        cuerpo = {**cuerpo, "generationConfig": {**cuerpo.get("generationConfig", {}),
                                                 "thinkingConfig": {"thinkingLevel": "low"}}}
    r = requests.post(URL.format(modelo=modelo), json=cuerpo, timeout=timeout,
                      headers={"x-goog-api-key": clave, "Content-Type": "application/json"})
    if r.status_code != 200:
        try:
            mensaje = r.json().get("error", {}).get("message", r.text)
        except ValueError:
            mensaje = r.text
        raise RuntimeError(f"Gemini respondió {r.status_code}: {mensaje[:300]}")
    return r.json()


def responder(pregunta, historial, herramientas, enviar):
    """Corre el ciclo del agente.

    historial: lista de turnos previos en formato Gemini ({"role": "user"|"model", "parts": [...]}) solo con texto.
    enviar: función que recibe el cuerpo de la petición y regresa el JSON de Gemini (se inyecta para poder probar).
    Regresa (texto de respuesta, lista de herramientas usadas con sus argumentos).
    """
    contenidos = list(historial) + [{"role": "user", "parts": [{"text": pregunta}]}]
    usadas = []
    for _ in range(MAX_VUELTAS):
        cuerpo = {"systemInstruction": {"parts": [{"text": INSTRUCCIONES}]}, "contents": contenidos,
                  "tools": [{"functionDeclarations": HERRAMIENTAS}], "generationConfig": {"temperature": 0.2}}
        datos = enviar(cuerpo)
        candidatos = datos.get("candidates") or []
        if not candidatos or "content" not in candidatos[0]:
            return "No obtuve respuesta del modelo. Intenta reformular la pregunta.", usadas
        contenido = candidatos[0]["content"]
        partes = contenido.get("parts", [])
        llamadas = [p["functionCall"] for p in partes if "functionCall" in p]
        if not llamadas:
            texto = "".join(p.get("text", "") for p in partes if not p.get("thought")).strip()
            return texto or "No obtuve respuesta del modelo.", usadas
        contenidos.append(contenido)  # se conserva tal cual (incluye firmas de razonamiento si las hay)
        respuestas = []
        for llamada in llamadas:
            resultado = herramientas.ejecutar(llamada["name"], llamada.get("args"))
            usadas.append({"herramienta": llamada["name"], "argumentos": llamada.get("args") or {}})
            respuestas.append({"functionResponse": {"name": llamada["name"],
                                                    "response": {"resultado": json.loads(json.dumps(resultado, default=str))}}})
        contenidos.append({"role": "user", "parts": respuestas})
    return "Necesité demasiados pasos para responder. Intenta una pregunta más concreta.", usadas
