"""
Estilos (CSS) para que el dashboard quepa en una sola pantalla.
RESPONSABLE: Coordinación (integrante 1)
"""
import streamlit as st

CSS = """
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 0.5rem; padding-left: 1.5rem; padding-right: 1.5rem; max-width: 100%;}
div[data-testid="stVerticalBlock"] {gap: 0.55rem;}
h1.titulo {font-size: 1.25rem; font-weight: 600; margin: 0; padding: 0.15rem 0 0 0;}
p.subtitulo {font-size: 0.78rem; opacity: 0.65; margin: 0;}

.kpi {height: 236px; border-radius: 12px; padding: 14px 16px; display: flex; flex-direction: column;
      justify-content: center; gap: 6px; border: 1px solid rgba(128,128,128,0.25);}
.kpi-azul {background: rgba(24,95,165,0.07); border-left: 5px solid #185FA5;}
.kpi-ambar {background: rgba(239,159,39,0.09); border-left: 5px solid #EF9F27;}
.kpi-label {font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.75;}
.kpi-valor {font-size: 2.9rem; font-weight: 700; line-height: 1;}
.kpi-chip {display: inline-block; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; width: fit-content;}
.chip-rojo {background: rgba(226,75,74,0.15); color: #A32D2D;}
.chip-verde {background: rgba(59,109,17,0.15); color: #3B6D11;}
.chip-gris {background: rgba(128,128,128,0.15);}
.kpi-sub {font-size: 0.8rem; opacity: 0.85;}
.kpi-barra {position: relative; height: 8px; border-radius: 4px; background: rgba(128,128,128,0.2); margin-top: 2px;}
.kpi-barra > div {height: 8px; border-radius: 4px;}
.kpi-meta {position: absolute; top: -4px; width: 2px; height: 16px; background: currentColor;}
.kpi-regla {font-size: 0.7rem; opacity: 0.6;}

.st-key-filtros {background: rgba(128,128,128,0.07); border-radius: 12px; padding: 0.7rem 0.7rem 0.4rem 0.7rem;}
.st-key-filtros label p, .st-key-filtros p, .st-key-filtros span, .st-key-filtros div[data-baseweb="select"] * {font-size: 0.75rem !important;}
.st-key-filtros div[data-testid="stVerticalBlock"] {gap: 0.35rem;}
.st-key-filtros button p {font-size: 0.75rem !important;}
.filtro-titulo {font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.6; margin: 0.2rem 0 0 0;}
</style>
"""


def aplicar():
    st.markdown(CSS, unsafe_allow_html=True)
