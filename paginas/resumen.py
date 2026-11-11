"""
Pantalla 00 · Resumen general.
Pregunta: ¿cuál es la situación del abandono y qué está relacionado con él, antes de entrar al detalle?
RESPONSABLE: (poner nombre)
"""
import streamlit as st

from src.contexto import contexto
from src.resumen import DIAS_REACTIVAR, factores, segmento_critico, situacion, valor_alto

c = contexto()
df, df_general, regla = c.df_filtrado, c.df, c.regla

st.markdown('<h2 class="seccion-titulo">Resumen general</h2>', unsafe_allow_html=True)
st.caption(f"La situación del abandono en una sola vista · {len(df):,} de {len(df_general):,} clientes "
           "en el grupo seleccionado")

if df.empty:
    st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
    st.stop()

s = situacion(df, regla)
r = s["riesgo"]
estado_churn = "arriba" if s["tasa"] > s["meta_churn"] else "debajo"
estado_riesgo = "arriba" if r["pct_activos"] >= s["meta_riesgo"] else "debajo"

# ------------------------------------------------------------------ Situación
with st.container(border=True):
    st.markdown("### Situación actual")
    st.markdown(
        f"De **{s['clientes']:,} clientes**, **{s['abandonaron']:,} abandonaron la plataforma ({s['tasa']:.1%})**, "
        f"{estado_churn} de la meta de churn de {s['meta_churn']:.0%}. "
        f"De los {s['activos']:,} que siguen activos, **{r['activos_en_perfil']:,} ({r['pct_activos']:.1%}) "
        f"tienen el perfil de riesgo**, {estado_riesgo} de la meta de menos de {s['meta_riesgo']:.0%}. "
        "Esos son los clientes a contactar primero."
    )

# ------------------------------------------------------------------ Hallazgos
st.markdown("### Qué está relacionado con el abandono")
f = factores(df, regla)
seg = segmento_critico(df)
va = valor_alto(df, df_general)

hallazgos = [
    ("Llamadas a servicio", f["llamadas"]["tasa_dentro"],
     f"abandona con {regla['llamadas_min']} o más llamadas, contra {f['llamadas']['tasa_fuera']:.1%} con menos."),
    ("Carrito abandonado", f["carrito"]["tasa_dentro"],
     f"abandona con carrito > {regla['carrito_min']:.2f}%, contra {f['carrito']['tasa_fuera']:.1%} del resto."),
    ("Días sin comprar", f["dias"]["tasa_dentro"],
     f"abandona con más de {DIAS_REACTIVAR} días sin comprar, contra {f['dias']['tasa_fuera']:.1%} del resto."),
    ("Perfil de riesgo (carrito + llamadas)", f["perfil"]["tasa_dentro"],
     f"abandona cuando se cumplen las dos condiciones a la vez, contra {f['perfil']['tasa_fuera']:.1%} del resto."),
]
if seg:
    hallazgos.append((f"Segmento con más abandono ({seg['dimension'].lower()})", seg["tasa"],
                      f"abandona en el segmento {seg['segmento']} ({seg['clientes']:,} clientes), "
                      f"contra {s['tasa']:.1%} de la selección."))
hallazgos.append(("Clientes de mayor valor (Q4 de LTV)", va["tasa_q4"],
                  f"abandona en el cuartil de valor alto, contra {va['tasa_medios']:.1%} en los cuartiles intermedios."))

for inicio in range(0, len(hallazgos), 3):
    columnas = st.columns(3, gap="medium")
    for columna, (titulo, valor, texto) in zip(columnas, hallazgos[inicio:inicio + 3]):
        with columna, st.container(border=True):
            st.markdown(f"**{titulo}**")
            st.markdown(f'<div class="kpi-valor">{valor:.1%}</div>', unsafe_allow_html=True)
            st.caption(texto)

st.caption("Los porcentajes son tasas de churn históricas de cada grupo y cambian con los filtros. "
           "Muestran relaciones, no causas.")

# ------------------------------------------------------------------ Guía
with st.container(border=True):
    st.markdown("### Cómo usar este dashboard")
    st.markdown("""
| Pantalla | Para quién | Qué decisión habilita |
|---|---|---|
| **01 · Priorizar campañas** | Andrea López, gerente de retención | A qué segmentos dirigir la campaña de retención |
| **02 · Alertas y calidad** | Luis Ramírez, operaciones de datos y CRM | Si hay alertas, si los datos son confiables y quién entra a la lista de campaña |
| **03 · Valor y presupuesto** | Carlos Mendoza, estrategia y valor | Si se están yendo los clientes valiosos y dónde conviene invertir |
| **04 · Recomendaciones** | Todo el equipo | Qué acciones tomar primero y cómo medir si funcionaron |
| **05 · Clientes prioritarios** | Andrea y Luis | A qué clientes contactar primero según su probabilidad de abandono y su segmento |
""")
    st.caption("Los filtros de la derecha aplican a todas las pantallas y se conservan al cambiar de una a otra.")
