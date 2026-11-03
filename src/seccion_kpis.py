"""
Tarjetas de los 2 KPI principales.
RESPONSABLE: Integrante 4

KPI 1 · Tasa de abandono (relacionada con las 3 gráficas de factores).
KPI 2 · % de activos en perfil de riesgo (relacionada con el mapa de calor y el país).
"""
import streamlit as st

from src.config import AMBAR, AZUL, META_RIESGO
from src.indicadores import resumen_riesgo, tasa_churn


def _html(texto):
    """Quita la sangría: Streamlit trata las líneas con sangría como bloque de código."""
    return "".join(linea.strip() for linea in texto.splitlines())


def _chip(diferencia_pts, texto_base):
    if abs(diferencia_pts) < 0.05:
        return f'<span class="kpi-chip chip-gris">{texto_base}</span>'
    clase = "chip-rojo" if diferencia_pts > 0 else "chip-verde"
    flecha = "▲" if diferencia_pts > 0 else "▼"
    return f'<span class="kpi-chip {clase}">{flecha} {abs(diferencia_pts):.1f} pts {texto_base}</span>'


def tarjeta_churn(df, tasa_global):
    tasa = tasa_churn(df)
    abandonaron = int(df["Churned"].sum())
    chip = _chip((tasa - tasa_global) * 100, f"vs. global {tasa_global:.1%}")
    html = f"""
    <div class="kpi kpi-azul">
      <div class="kpi-label">Tasa de abandono</div>
      <div class="kpi-valor" style="color:{AZUL}">{tasa:.1%}</div>
      {chip}
      <div class="kpi-sub"><b>{abandonaron:,}</b> abandonaron de <b>{len(df):,}</b> clientes</div>
      <div class="kpi-barra"><div style="width:{tasa * 100:.1f}%; background:{AZUL}"></div></div>
    </div>
    """
    st.markdown(_html(html), unsafe_allow_html=True)


def tarjeta_riesgo(df, regla):
    r = resumen_riesgo(df, regla)
    pct = r["pct_activos"]
    sobre_meta = pct > META_RIESGO
    chip_clase = "chip-rojo" if sobre_meta else "chip-verde"
    chip_texto = ("▲ Sobre la meta" if sobre_meta else "▼ Bajo la meta") + f" de {META_RIESGO:.0%}"
    escala = max(0.30, pct * 1.2)  # la barra llega hasta 30% o un poco más que el valor
    html = f"""
    <div class="kpi kpi-ambar">
      <div class="kpi-label">Activos en perfil de riesgo</div>
      <div class="kpi-valor" style="color:{AMBAR}">{pct:.1%}</div>
      <span class="kpi-chip {chip_clase}">{chip_texto}</span>
      <div class="kpi-sub"><b>{r['activos_en_perfil']:,}</b> de <b>{r['total_activos']:,}</b> activos ·
        churn del perfil <b>{r['tasa_historica']:.1%}</b></div>
      <div class="kpi-barra">
        <div style="width:{pct / escala * 100:.1f}%; background:{AMBAR}"></div>
        <div class="kpi-meta" style="left:{META_RIESGO / escala * 100:.1f}%"></div>
      </div>
      <div class="kpi-regla">Perfil: carrito &gt; {regla['carrito_min']:.2f}% y ≥ {regla['llamadas_min']} llamadas</div>
    </div>
    """
    st.markdown(_html(html), unsafe_allow_html=True)
