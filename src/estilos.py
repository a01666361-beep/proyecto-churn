"""
Estilos (CSS) para que el dashboard quepa en una sola pantalla.
RESPONSABLE: Coordinación (integrante 1)
"""
import streamlit as st

CSS = """
<style>
.block-container {padding-top: 4rem; padding-bottom: 2rem; padding-left: 2rem; padding-right: 2rem; max-width: 1500px;}
div[data-testid="stVerticalBlock"] {gap: 0.9rem;}
h1.titulo {font-size: 1.65rem; font-weight: 600; margin: 0; padding: 0;}
h2.seccion-titulo {font-size: 1.2rem; margin: 1rem 0 0; padding: 0;}
div[class*="st-key-grafica_"] h3 {font-size: 1rem; line-height: 1.5; min-height: 3rem; padding: 0;}
div[class*="st-key-grafica_"] {padding: 1rem;}
p.subtitulo {font-size: 0.78rem; opacity: 0.65; margin: 0;}

.kpi {min-height: 220px; border-radius: 12px; padding: 16px; display: flex; flex-direction: column;
      justify-content: flex-start; gap: 10px; border: 1px solid rgba(128,128,128,0.25);}
.kpi-azul {background: rgba(24,95,165,0.07); border-left: 5px solid #185FA5;}
.kpi-gris {background: rgba(128,128,128,0.07); border-left: 5px solid #888780;}
.kpi-ambar {background: rgba(46,134,222,0.09); border-left: 5px solid #2E86DE;}
.kpi-verde {background: rgba(22,132,81,0.08); border-left: 5px solid #168451;}
.kpi-rojo {background: rgba(192,57,43,0.08); border-left: 5px solid #C0392B;}
.kpi-label {font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.75; min-height: 2.3rem;}
.kpi-valor {font-size: 2rem; font-weight: 700; line-height: 1;}
.kpi-chip {display: inline-block; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; width: fit-content;}
.chip-rojo {background: rgba(226,75,74,0.15); color: #A32D2D;}
.chip-verde {background: rgba(59,109,17,0.15); color: #3B6D11;}
.chip-azul {background: rgba(46,134,222,0.12); color: #1D4E89;}
.chip-gris {background: rgba(128,128,128,0.15);}
.kpi-sub {font-size: 0.8rem; opacity: 0.85;}
.kpi-referencia {font-size: 0.78rem; line-height: 1.4; border-top: 1px solid rgba(128,128,128,0.25); padding-top: 6px; margin-top: 2px;}
.kpi-barra {position: relative; height: 8px; border-radius: 4px; background: rgba(128,128,128,0.2); margin-top: 2px;}
.kpi-barra > div {height: 8px; border-radius: 4px;}
.kpi-meta {position: absolute; top: -4px; width: 2px; height: 16px; background: currentColor;}
.kpi-regla {font-size: 0.7rem; opacity: 0.6;}
.grupo-bloque {margin: 8px 0;}
.grupo-bloque h3 {font-size: 1rem; margin: 0 0 4px; padding: 0;}
.grupo-contexto {font-size: 0.8rem; opacity: 0.8; margin: 0 0 10px;}
.grupo-columnas {display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;}
.grupo-tarjeta {background: rgba(46,134,222,0.05); border: 1px solid rgba(128,128,128,0.2);
  border-left: 4px solid #2E86DE; border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 8px; min-width: 0;}
.grupo-tarjeta h4 {font-size: 0.88rem; margin: 0; padding: 0;}
.grupo-cantidad {font-size: 1.6rem; font-weight: 700; line-height: 1.1;}
.grupo-texto, .grupo-lectura {font-size: 0.8rem; line-height: 1.5;}
.grupo-barra {height: 10px; border-radius: 4px; background: rgba(128,128,128,0.2); overflow: hidden;}
.grupo-barra > div {height: 100%; background: #2E86DE;}
.grupo-leyenda {display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px; font-size: 0.72rem; opacity: 0.8;}
.grupo-lectura {border-top: 1px solid rgba(128,128,128,0.2); padding-top: 8px;}
.grupo-nota {font-size: 0.72rem; line-height: 1.5; opacity: 0.8; margin: 8px 0 0;}
@media (max-width: 700px) {.grupo-columnas {grid-template-columns: 1fr;}}

.st-key-filtros {background: rgba(128,128,128,0.04); border: 1px solid rgba(128,128,128,0.2); border-radius: 12px; padding: 1rem;}
.st-key-filtros label p, .st-key-filtros p, .st-key-filtros span, .st-key-filtros div[data-baseweb="select"] * {font-size: 0.75rem !important;}
.st-key-filtros div[data-testid="stVerticalBlock"] {gap: 0.9rem;}
.st-key-filtros button p {font-size: 0.75rem !important;}
.filtro-titulo {font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.6; margin: 0.2rem 0 0 0;}
.kpi {position: relative;}
.kpi-info {display: flex; flex-direction: column; gap: 6px; font-size: 0.78rem; line-height: 1.5; margin-top: 10px;}
.kpi-detalle {margin-top: auto; font-size: 0.76rem; line-height: 1.5;}
.kpi-detalle summary {color: #1D4E89; cursor: pointer; padding-top: 4px;}
.kpi-detalle > .kpi-barra {margin-top: 12px;}
.kpi-detalle > .kpi-chip {margin-top: 8px;}
@media(max-width: 700px) {.block-container {padding: 3.5rem 1rem 1rem;} .kpi {min-height: 0;} .kpi-label {min-height: 0;}}
@media(max-width: 1000px) {
  div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-filtros) {flex-direction: column-reverse;}
  div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-filtros) > div[data-testid="stColumn"] {width: 100%; flex: 1 1 100%;}
}
@media(max-width: 700px) {
  div[data-testid="stHorizontalBlock"] {flex-wrap: wrap;}
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {width: 100%; flex: 1 1 100%;}
}
</style>
"""


def aplicar():
    st.markdown(CSS, unsafe_allow_html=True)
