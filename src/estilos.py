"""
Estilos (CSS) del dashboard con la identidad visual de CartPulse Analytics.
RESPONSABLE: Coordinación (integrante 1)

- aplicar(): inyecta el CSS. Se llama una vez en app.py y aplica a todas las pantallas.
- encabezado(subtitulo): dibuja el logo (carrito + mouse) y el nombre de la marca.

Paleta complementaria de la UI de análisis CartPulse (7 colores):
  · Fondo principal #1A1D24 · Fondo de tarjetas #293545
  · Azul de datos #007BFF (números, barras, botones)
  · Naranja de advertencia #FFA03A (alertas, lo malo, tendencias)
  · Cian de énfasis #3FD8E0 (filtros activos, estados activos, lo favorable)
  · Gris de texto secundario #B0B7C3 · Blanco de texto #FFFFFF
  · Letra: títulos y números en Century Gothic (web: Jost), texto en Calibri (web: Carlito).
"""
import streamlit as st

TITULOS = "'Century Gothic', 'Jost', 'Futura', 'Trebuchet MS', sans-serif"
CUERPO = "'Calibri', 'Carlito', 'Segoe UI', 'Helvetica Neue', sans-serif"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Carlito:wght@400;700&display=swap');

:root {
  --cp-fondo: #1A1D24; --cp-fondo-2: #222733; --cp-tarjeta: #293545; --cp-pista: #1F2733;
  --cp-azul: #007BFF; --cp-azul-oscuro: #0062CC; --cp-azul-texto: #4DA3FF;
  --cp-naranja: #FFA03A; --cp-cian: #3FD8E0;
  --cp-texto: #FFFFFF; --cp-texto-suave: #B0B7C3; --cp-linea: #343B4A;
}

/* ---------- Letra ---------- */
html, body, .stApp, .stApp p, .stApp li, .stApp label, .stApp input, .js-plotly-plot text {font-family: CUERPO !important;}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .cp-marca, h1.titulo, h2.seccion-titulo,
.kpi-valor, .grupo-cantidad, div[data-testid="stMetricValue"], .js-plotly-plot .gtitle,
.stTabs [data-baseweb="tab"] p {font-family: TITULOS !important;}
.stApp {color: var(--cp-texto); background: var(--cp-fondo);}

/* ---------- Barra superior oscura con línea azul ---------- */
header[data-testid="stHeader"] {background: var(--cp-fondo); border-bottom: 2px solid var(--cp-azul);}
header[data-testid="stHeader"] * {color: var(--cp-texto-suave); fill: var(--cp-texto-suave);}

/* ---------- Encabezado de marca ---------- */
.cp-encabezado {display: flex; align-items: center; gap: 14px; padding-bottom: 10px;
  border-bottom: 1px solid var(--cp-linea); margin-bottom: 0.4rem;}
.cp-encabezado svg {width: 52px; height: 52px; flex-shrink: 0;}
.cp-marca {font-size: 1.8rem; font-weight: 700; line-height: 1.1; margin: 0; color: #FFFFFF;}
.cp-marca span {color: var(--cp-azul-texto);}
.cp-sub {font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.14em; color: var(--cp-texto-suave); margin: 2px 0 0;}

/* ---------- Layout ---------- */
.block-container {padding-top: 4rem; padding-bottom: 2rem; padding-left: 2rem; padding-right: 2rem; max-width: 1500px;}
div[data-testid="stVerticalBlock"] {gap: 0.9rem;}
h1.titulo {font-size: 1.7rem; font-weight: 700; margin: 0; padding: 0; color: #FFFFFF;}
h2.seccion-titulo {font-size: 1.25rem; font-weight: 600; margin: 1rem 0 0; padding: 0 0 0 0.7rem; color: #FFFFFF;
  border-left: 4px solid var(--cp-azul);}
div[class*="st-key-grafica_"] {padding: 1rem; background: var(--cp-fondo); border: 1px solid var(--cp-linea); border-radius: 4px;}
div[class*="st-key-grafica_"] h3 {font-size: 1.05rem; font-weight: 500; line-height: 1.45; min-height: 3rem; padding: 0; color: var(--cp-texto);}
p.subtitulo {font-size: 0.82rem; color: var(--cp-texto-suave); margin: 0;}

/* ---------- Tarjetas KPI (azul marino, número azul brillante) ---------- */
.kpi {position: relative; min-height: 220px; border-radius: 4px; padding: 16px; display: flex; flex-direction: column;
      justify-content: flex-start; gap: 10px; border: 0; background: var(--cp-tarjeta);}
.kpi-azul     {border-top: 4px solid var(--cp-azul);}
.kpi-gris     {border-top: 4px solid var(--cp-texto-suave);}
.kpi-verde    {border-top: 4px solid var(--cp-cian);}
.kpi-menta    {border-top: 4px solid var(--cp-cian);}
.kpi-arena    {border-top: 4px solid var(--cp-naranja);}
.kpi-ambar    {border-top: 4px solid var(--cp-naranja);}
.kpi-naranja  {border-top: 4px solid var(--cp-naranja);}
.kpi-rojo     {border-top: 4px solid var(--cp-naranja);}
.kpi-label {font-size: 0.95rem; font-weight: 700; color: #FFFFFF; min-height: 2.3rem;}
.kpi-valor {font-size: 2.4rem; font-weight: 400; line-height: 1; color: var(--cp-azul);}
.kpi-chip {display: inline-block; font-size: 0.78rem; font-weight: 700; padding: 2px 10px; border-radius: 99px; width: fit-content;}
.chip-rojo    {background: rgba(255,160,58,0.18); color: var(--cp-naranja);}
.chip-verde   {background: rgba(63,216,224,0.16);  color: var(--cp-cian);}
.chip-azul    {background: rgba(0,123,255,0.20);  color: var(--cp-azul-texto);}
.chip-celeste {background: rgba(0,123,255,0.20);  color: var(--cp-azul-texto);}
.chip-ambar   {background: rgba(255,160,58,0.18);  color: var(--cp-naranja);}
.chip-naranja {background: rgba(255,160,58,0.18);  color: var(--cp-naranja);}
.chip-arena   {background: rgba(255,160,58,0.14);  color: var(--cp-naranja);}
.chip-gris    {background: rgba(176,183,195,0.16); color: var(--cp-texto-suave);}
.kpi-sub {font-size: 0.84rem; color: var(--cp-texto-suave);}
.kpi-referencia {font-size: 0.8rem; line-height: 1.4; color: var(--cp-texto-suave); border-top: 1px solid var(--cp-linea); padding-top: 6px; margin-top: 2px;}
.kpi-barra {position: relative; height: 8px; border-radius: 2px; background: var(--cp-pista); margin-top: 2px;}
.kpi-barra > div {height: 8px; border-radius: 2px;}
.kpi-meta {position: absolute; top: -4px; width: 2px; height: 16px; background: #FFFFFF;}
.kpi-regla {font-size: 0.72rem; color: var(--cp-texto-suave);}
.kpi-info {display: flex; flex-direction: column; gap: 6px; font-size: 0.8rem; line-height: 1.5; margin-top: 10px;}
.kpi-detalle {margin-top: auto; font-size: 0.78rem; line-height: 1.5;}
.kpi-detalle summary {color: var(--cp-azul-texto); font-weight: 700; cursor: pointer; padding-top: 4px;}
.kpi-detalle > .kpi-barra {margin-top: 12px;}
.kpi-detalle > .kpi-chip {margin-top: 8px;}

/* ---------- Bloques por grupo ---------- */
.grupo-bloque {margin: 8px 0;}
.grupo-bloque h3 {font-size: 1.05rem; font-weight: 600; margin: 0 0 4px; padding: 0; color: #FFFFFF;}
.grupo-contexto {font-size: 0.84rem; color: var(--cp-texto-suave); margin: 0 0 10px;}
.grupo-columnas {display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;}
.grupo-tarjeta {background: var(--cp-tarjeta); border: 0; border-top: 4px solid var(--cp-azul);
  border-radius: 4px; padding: 14px; display: flex; flex-direction: column; gap: 8px; min-width: 0;}
.grupo-tarjeta h4 {font-size: 0.92rem; font-weight: 600; margin: 0; padding: 0; color: #FFFFFF;}
.grupo-cantidad {font-size: 1.8rem; font-weight: 400; line-height: 1.1; color: var(--cp-azul);}
.grupo-texto, .grupo-lectura {font-size: 0.84rem; line-height: 1.5;}
.grupo-barra {height: 10px; border-radius: 2px; background: var(--cp-pista); overflow: hidden;}
.grupo-barra > div {height: 100%; background: var(--cp-azul);}
.grupo-leyenda {display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px; font-size: 0.74rem; color: var(--cp-texto-suave);}
.grupo-lectura {border-top: 1px solid var(--cp-linea); padding-top: 8px;}
.grupo-nota {font-size: 0.74rem; line-height: 1.5; color: var(--cp-texto-suave); margin: 8px 0 0;}

/* ---------- Componentes de Streamlit ---------- */
div[data-testid="stMetric"] {background: var(--cp-tarjeta); border: 0; border-radius: 4px; padding: 14px 16px; text-align: center;}
div[data-testid="stMetricLabel"] {justify-content: center;}
div[data-testid="stMetricLabel"] p {font-weight: 700; font-size: 0.95rem; color: #FFFFFF;}
div[data-testid="stMetricValue"] {color: var(--cp-azul); font-weight: 400;}
/* pestañas: activa en azul con línea debajo */
.stTabs [data-baseweb="tab"] p {font-weight: 500; color: var(--cp-texto);}
.stTabs [aria-selected="true"] p {color: var(--cp-azul-texto);}
.stTabs [data-baseweb="tab-highlight"] {background: var(--cp-azul-texto); height: 2px;}
.stTabs [data-baseweb="tab-border"] {background: var(--cp-linea);}
div[data-testid="stExpander"] details {border-color: var(--cp-linea); border-radius: 4px;}
div[data-testid="stExpander"] summary p {font-weight: 700;}
.stApp button[kind="primary"] {background: var(--cp-azul); border-color: var(--cp-azul); color: #FFFFFF;}
.stApp button[kind="primary"]:hover {background: var(--cp-azul-oscuro); border-color: var(--cp-azul-oscuro);}

/* ---------- Panel de filtros (grafito, cajas con línea abajo) ---------- */
.st-key-filtros {background: var(--cp-fondo); border: 1px solid var(--cp-linea); border-radius: 4px; padding: 1rem; color: var(--cp-texto);}
.st-key-filtros label p, .st-key-filtros p, .st-key-filtros span, .st-key-filtros div[data-baseweb="select"] * {font-size: 0.8rem !important;}
.st-key-filtros div[data-testid="stVerticalBlock"] {gap: 0.9rem;}
.st-key-filtros label p, .st-key-filtros [data-testid="stMarkdownContainer"] p {color: var(--cp-texto);}
.filtro-titulo {font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--cp-cian) !important; opacity: 1; margin: 0.2rem 0 0 0;}
/* cajas de selección: gris oscuro con línea clara abajo */
.st-key-filtros div[data-baseweb="select"] > div {background: var(--cp-tarjeta); border: 0; border-bottom: 1px solid var(--cp-texto-suave); border-radius: 2px;}
.st-key-filtros div[data-baseweb="select"] > div:focus-within {border-bottom-color: var(--cp-cian);}
.st-key-filtros div[data-baseweb="select"] div, .st-key-filtros div[data-baseweb="select"] input {color: var(--cp-texto);}
.st-key-filtros div[data-baseweb="select"] svg {fill: var(--cp-texto-suave);}
/* filtro activo = cian de énfasis */
.st-key-filtros span[data-baseweb="tag"] {background: var(--cp-cian) !important;}
.st-key-filtros span[data-baseweb="tag"] span, .st-key-filtros span[data-baseweb="tag"] svg {color: var(--cp-fondo) !important; fill: var(--cp-fondo) !important;}
/* expander "Criterios de riesgo" */
.st-key-filtros div[data-testid="stExpander"] details {background: var(--cp-fondo-2); border-color: var(--cp-linea);}
.st-key-filtros div[data-testid="stExpander"] summary, .st-key-filtros div[data-testid="stExpander"] summary * {color: var(--cp-texto); fill: var(--cp-texto);}
.st-key-filtros div[data-testid="stExpander"] summary:hover * {color: var(--cp-cian); fill: var(--cp-cian);}
/* sliders en cian (filtro activo) */
.st-key-filtros div[role="slider"] {background: var(--cp-cian) !important; border-color: var(--cp-cian) !important;}
.st-key-filtros [data-testid="stSliderThumbValue"] {color: var(--cp-texto) !important;}
.st-key-filtros [data-testid="stSliderTickBarMin"], .st-key-filtros [data-testid="stSliderTickBarMax"] {color: var(--cp-texto-suave) !important;}
/* botón Limpiar filtros */
.st-key-filtros button {background: var(--cp-fondo-2); border: 1px solid var(--cp-linea); color: var(--cp-texto);}
.st-key-filtros button p {font-size: 0.8rem !important; font-weight: 700; color: inherit !important;}
.st-key-filtros button:hover, .st-key-filtros button:focus:not(:active) {background: var(--cp-azul); border-color: var(--cp-azul); color: #FFFFFF;}

/* ---------- Responsivo ---------- */
@media (max-width: 700px) {.grupo-columnas {grid-template-columns: 1fr;}}
@media(max-width: 700px) {.block-container {padding: 3.5rem 1rem 1rem;} .kpi {min-height: 0;} .kpi-label {min-height: 0;}
  .cp-marca {font-size: 1.4rem;} .cp-encabezado svg {width: 42px; height: 42px;}}
@media(max-width: 1000px) {
  div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-filtros) {flex-direction: column-reverse;}
  div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-filtros) > div[data-testid="stColumn"] {width: 100%; flex: 1 1 100%;}
}
@media(max-width: 700px) {
  div[data-testid="stHorizontalBlock"] {flex-wrap: wrap;}
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {width: 100%; flex: 1 1 100%;}
}
</style>
""".replace("CUERPO", CUERPO).replace("TITULOS", TITULOS)

# Logo CartPulse: carrito azul de datos, mouse blanco con detalle cian y el pulso en naranja.
LOGO_SVG = """
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="CartPulse Analytics">
  <path d="M4 10 H12 L19 40 H52 L58 18 H14" fill="none" stroke="#007BFF" stroke-width="4.5"
        stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M19 40 L17.5 46 H51" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="23" cy="53" r="4.5" fill="#FFFFFF"/>
  <circle cx="47" cy="53" r="4.5" fill="#FFFFFF"/>
  <polyline points="20,30 22.5,30 24.5,24 27,35 29,30 32,30" fill="none" stroke="#FFA03A"
            stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="32" y="21.5" width="13" height="16.5" rx="6.5" fill="#FFFFFF"/>
  <line x1="38.5" y1="21.5" x2="38.5" y2="28" stroke="#1A1D24" stroke-width="1.3"/>
  <rect x="37.3" y="23.5" width="2.4" height="4" rx="1.2" fill="#3FD8E0"/>
</svg>
"""

# Plantilla de Plotly con la misma letra y colores (opcional).
# Uso:  fig.update_layout(**estilos.LAYOUT_PLOTLY)
LAYOUT_PLOTLY = dict(
    font=dict(family="Calibri, Carlito, sans-serif", color="#FFFFFF", size=13),
    title=dict(font=dict(family="Century Gothic, Jost, sans-serif", color="#FFFFFF", size=16)),
    colorway=["#007BFF", "#FFA03A", "#3FD8E0", "#B0B7C3", "#4DA3FF", "#FFFFFF"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor="#343B4A", griddash="dot", linecolor="#B0B7C3", zeroline=False, tickfont=dict(color="#B0B7C3")),
    yaxis=dict(gridcolor="#343B4A", griddash="dot", linecolor="#B0B7C3", zeroline=False, tickfont=dict(color="#B0B7C3")),
    hoverlabel=dict(bgcolor="#293545", bordercolor="#3FD8E0", font=dict(color="#FFFFFF")),
)


def aplicar():
    """Inyecta el CSS de la marca. Llamar una vez en app.py."""
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(subtitulo="Abandono de clientes"):
    """Logo + 'CartPulse Analytics' + subtítulo. Reemplaza al <h1 class="titulo">."""
    st.markdown(
        f'<div class="cp-encabezado">{" ".join(LOGO_SVG.split())}<div>'
        f'<p class="cp-marca">CartPulse <span>Analytics</span></p>'
        f'<p class="cp-sub">{subtitulo}</p></div></div>',
        unsafe_allow_html=True,
    )
