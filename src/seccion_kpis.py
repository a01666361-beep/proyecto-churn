"""
Tarjetas de los 2 KPI principales.
RESPONSABLE: Integrante 4

KPI 1 · Tasa de abandono (relacionada con las 3 gráficas de factores).
KPI 2 · % de activos en perfil de riesgo (relacionada con el mapa de calor y el país).
"""
import streamlit as st

from src.config import AZUL, META_RIESGO, ROJO, VERDE
from src.indicadores import resumen_riesgo, tasa_churn


def _html(texto):
    """Quita la sangría: Streamlit trata las líneas con sangría como bloque de código."""
    return "".join(linea.strip() for linea in texto.splitlines())


def _chip(diferencia_pts, texto_base):
    if abs(diferencia_pts) < 0.05:
        mensaje = "Igual al general" if abs(diferencia_pts) < 1e-10 else "Diferencia menor a 0.05 pts"
        return f'<span class="kpi-chip chip-azul">↔ {mensaje}</span>'
    clase = "chip-rojo" if diferencia_pts > 0 else "chip-verde"
    flecha = "▲" if diferencia_pts > 0 else "▼"
    return f'<span class="kpi-chip {clase}">{flecha} {abs(diferencia_pts):.1f} pts {texto_base}</span>'

def tarjeta_churn(df, tasa_global, df_general):
    tasa = tasa_churn(df)
    abandonaron = int(df["Churned"].sum())
    chip = _chip((tasa - tasa_global) * 100, f"vs. global {tasa_global:.1%}")
    if df.empty:
        chip = '<span class="kpi-chip chip-gris">Sin clientes para comparar</span>'
    html = f"""
    <div class="kpi kpi-azul">
      <div class="kpi-label">Tasa de abandono</div>
      <div class="kpi-valor" style="color:{AZUL}">{f'{tasa:.1%}' if len(df) else '—'}</div>
      <div class="kpi-sub"><b>{abandonaron:,}</b> abandonaron de <b>{len(df):,}</b> clientes</div>
      {chip}
      <details class="kpi-detalle"><summary>Ver comparación y explicación</summary>
      <div class="kpi-referencia">General sin filtros: <b>{tasa_global:.1%}</b> · <b>{int(df_general['Churned'].sum()):,}</b> de <b>{len(df_general):,}</b> clientes</div>
      <div class="kpi-barra"><div style="width:{tasa * 100:.1f}%; background:{AZUL}"></div></div>
      <div class="kpi-info">
        <div><b>Qué mide:</b> el % de clientes de la selección que abandonaron.</div>
        <div><b>Cálculo:</b> clientes que abandonaron ÷ total de clientes.</div>
        <div><b>Cómo leerlo:</b> la etiqueta lo compara con la tasa global de {tasa_global:.1%}.</div>
      </div>
      </details>
    </div>
    """
    st.markdown(_html(html), unsafe_allow_html=True)


def tarjeta_riesgo(df, regla, df_general):
    r = resumen_riesgo(df, regla)
    # La referencia incluye toda la base con la MISMA regla de riesgo vigente.
    general = resumen_riesgo(df_general, regla)
    comparacion = _chip((r["pct_activos"] - general["pct_activos"]) * 100,
                        f"vs. general {general['pct_activos']:.1%}")
    if not r["total_activos"] or not general["total_activos"]:
        comparacion = '<span class="kpi-chip chip-gris">Sin activos para comparar</span>'
    pct = r["pct_activos"]
    sobre_meta = pct >= META_RIESGO
    color = ROJO if sobre_meta else VERDE
    estado = "rojo" if sobre_meta else "verde"
    chip_clase = "chip-rojo" if sobre_meta else "chip-verde"
    chip_texto = ("▲ Fuera de meta" if sobre_meta else "▼ Dentro de meta") + f" · menos de {META_RIESGO:.1%}"
    if not r["total_activos"]:
        color, estado, chip_clase = AZUL, "azul", "chip-gris"
        chip_texto = "Sin activos para evaluar la meta"
    escala = max(0.30, pct * 1.2)  # la barra llega hasta 30% o un poco más que el valor
    html = f"""
    <div class="kpi kpi-{estado}">
      <div class="kpi-label">Activos en perfil de riesgo</div>
      <div class="kpi-valor" style="color:{color}">{f'{pct:.1%}' if r['total_activos'] else '—'}</div>
      <div class="kpi-sub"><b>{r['activos_en_perfil']:,}</b> de <b>{r['total_activos']:,}</b> activos</div>
      <span class="kpi-chip {chip_clase}">{chip_texto}</span>
      <details class="kpi-detalle"><summary>Ver comparación y explicación</summary>
      <div class="kpi-referencia">General sin filtros: <b>{general['pct_activos']:.1%}</b> · <b>{general['activos_en_perfil']:,}</b> de <b>{general['total_activos']:,}</b> activos</div>
      {comparacion}
      <div class="kpi-barra">
        <div style="width:{pct / escala * 100:.1f}%; background:{color}"></div>
        <div class="kpi-meta" style="left:{META_RIESGO / escala * 100:.1f}%"></div>
      </div>
      <div class="kpi-info">
        <div><b>Qué mide:</b> el % de activos que se parecen a los clientes que sí se fueron.</div>
        <div><b>Cálculo:</b> activos con carrito &gt; {regla['carrito_min']:.2f}% y {regla['llamadas_min']}+ llamadas ÷ total de activos.</div>
        <div><b>Meta:</b> menos de {META_RIESGO:.1%}. Son los clientes a contactar primero.</div>
        <div><b>Churn histórico del perfil:</b> {r['tasa_historica']:.1%}.</div>
        <div><b>Referencia general:</b> toda la base con la misma regla de riesgo. Las flechas comparan segmentos, no cambios en el tiempo.</div>
      </div>
      </details>
    </div>
    """
    st.markdown(_html(html), unsafe_allow_html=True)
