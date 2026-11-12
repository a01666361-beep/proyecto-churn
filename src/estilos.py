"""
Estilos (CSS) del dashboard con la identidad visual de CartPulse Analytics.
RESPONSABLE: Coordinación (integrante 1)

- aplicar(): inyecta el CSS. Se llama una vez en app.py y aplica a todas las pantallas.
- encabezado(subtitulo): dibuja el logo (carrito + mouse) y el nombre de la marca.

Paleta: Noche #001219 · Petróleo #005F73 (dominante) · Turquesa #0A9396 · Menta #94D2BD
        Arena #E9D8A6 · Ámbar #EE9B00 · Naranja #CA6702 · Óxido #BB3E03
        Carmín #AE2012 (solo lo malo) · Vino #9B2226
"""
import streamlit as st

FUENTE = "'Outfit', 'Futura', 'Century Gothic', 'Trebuchet MS', sans-serif"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
  --cp-noche: #001219; --cp-petroleo: #005F73; --cp-turquesa: #0A9396; --cp-menta: #94D2BD;
  --cp-arena: #E9D8A6; --cp-ambar: #EE9B00; --cp-naranja: #CA6702; --cp-oxido: #BB3E03;
  --cp-carmin: #AE2012; --cp-vino: #9B2226; --cp-gris: #7A8C93;
  --cp-turquesa-texto: #087F82; --cp-ambar-texto: #A35A00;
  --cp-fondo: #F7F9F9; --cp-borde: #DCE5E6; --cp-panel: #0B2530; --cp-panel-borde: #1C3D48;
}
html, body, .stApp, .js-plotly-plot text {font-family: FUENTE !important;}
.stApp {color: var(--cp-noche);}

/* ---------- Barra superior y navegación ---------- */
header[data-testid="stHeader"] {border-bottom: 3px solid var(--cp-petroleo);}

/* ---------- Encabezado de marca ---------- */
.cp-encabezado {display: flex; align-items: center; gap: 14px; padding-bottom: 10px;
  border-bottom: 2px solid var(--cp-petroleo); margin-bottom: 0.4rem;}
.cp-encabezado svg {width: 52px; height: 52px; flex-shrink: 0;}
.cp-marca {font-size: 1.75rem; font-weight: 700; line-height: 1.1; margin: 0; color: var(--cp-noche); letter-spacing: -0.01em;}
.cp-marca span {color: var(--cp-petroleo);}
.cp-sub {font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.14em; color: #4F6670; margin: 2px 0 0;}

/* ---------- Layout (igual que antes) ---------- */
.block-container {padding-top: 4rem; padding-bottom: 2rem; padding-left: 2rem; padding-right: 2rem; max-width: 1500px;}
div[data-testid="stVerticalBlock"] {gap: 0.9rem;}
h1.titulo {font-size: 1.65rem; font-weight: 600; margin: 0; padding: 0; color: var(--cp-noche);}
h2.seccion-titulo {font-size: 1.2rem; font-weight: 600; margin: 1rem 0 0; padding: 0 0 0 0.6rem;
  border-left: 4px solid var(--cp-petroleo); text-transform: uppercase; letter-spacing: 0.03em;}
div[class*="st-key-grafica_"] h3 {font-size: 1rem; font-weight: 600; line-height: 1.5; min-height: 3rem; padding: 0; color: var(--cp-noche);}
div[class*="st-key-grafica_"] {padding: 1rem;}
p.subtitulo {font-size: 0.78rem; opacity: 0.65; margin: 0;}

/* ---------- Tarjetas KPI ---------- */
.kpi {position: relative; min-height: 220px; border-radius: 12px; padding: 16px; display: flex; flex-direction: column;
      justify-content: flex-start; gap: 10px; border: 1px solid var(--cp-borde); background: var(--cp-fondo);}
.kpi-azul     {background: rgba(0,95,115,0.06);   border-left: 5px solid var(--cp-petroleo);}
.kpi-gris     {background: rgba(122,140,147,0.08); border-left: 5px solid var(--cp-gris);}
.kpi-verde    {background: rgba(10,147,150,0.07);  border-left: 5px solid var(--cp-turquesa);}
.kpi-menta    {background: rgba(148,210,189,0.18); border-left: 5px solid var(--cp-menta);}
.kpi-arena    {background: rgba(233,216,166,0.30); border-left: 5px solid var(--cp-arena);}
.kpi-ambar    {background: rgba(238,155,0,0.09);   border-left: 5px solid var(--cp-ambar);}
.kpi-naranja  {background: rgba(202,103,2,0.08);   border-left: 5px solid var(--cp-naranja);}
.kpi-rojo     {background: rgba(174,32,18,0.06);   border-left: 5px solid var(--cp-carmin);}
.kpi-label {font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.75; min-height: 2.3rem;}
.kpi-valor {font-size: 2rem; font-weight: 700; line-height: 1;}
/* Los números vienen coloreados desde Python; los tonos claros se oscurecen
   aquí para que se lean sobre blanco. Las barras sí usan el color de marca. */
.kpi-valor[style*="#0A9396"] {color: var(--cp-turquesa-texto) !important;}
.kpi-valor[style*="#EE9B00"] {color: var(--cp-ambar-texto) !important;}
.kpi-chip {display: inline-block; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; width: fit-content;}
.chip-rojo    {background: rgba(174,32,18,0.10);  color: var(--cp-carmin);}
.chip-verde   {background: rgba(10,147,150,0.13); color: var(--cp-turquesa-texto);}
.chip-azul    {background: rgba(0,95,115,0.10);   color: var(--cp-petroleo);}
.chip-ambar   {background: rgba(238,155,0,0.18);  color: var(--cp-ambar-texto);}
.chip-naranja {background: rgba(202,103,2,0.13);  color: #8F4800;}
.chip-arena   {background: rgba(233,216,166,0.55); color: #5C4A12;}
.chip-gris    {background: rgba(122,140,147,0.16); color: #46575E;}
.kpi-sub {font-size: 0.8rem; opacity: 0.85;}
.kpi-referencia {font-size: 0.78rem; line-height: 1.4; border-top: 1px solid var(--cp-borde); padding-top: 6px; margin-top: 2px;}
.kpi-barra {position: relative; height: 8px; border-radius: 4px; background: var(--cp-borde); margin-top: 2px;}
.kpi-barra > div {height: 8px; border-radius: 4px;}
.kpi-meta {position: absolute; top: -4px; width: 2px; height: 16px; background: var(--cp-noche);}
.kpi-regla {font-size: 0.7rem; opacity: 0.6;}
.kpi-info {display: flex; flex-direction: column; gap: 6px; font-size: 0.78rem; line-height: 1.5; margin-top: 10px;}
.kpi-detalle {margin-top: auto; font-size: 0.76rem; line-height: 1.5;}
.kpi-detalle summary {color: var(--cp-petroleo); font-weight: 600; cursor: pointer; padding-top: 4px;}
.kpi-detalle > .kpi-barra {margin-top: 12px;}
.kpi-detalle > .kpi-chip {margin-top: 8px;}

/* ---------- Bloques por grupo ---------- */
.grupo-bloque {margin: 8px 0;}
.grupo-bloque h3 {font-size: 1rem; font-weight: 600; margin: 0 0 4px; padding: 0;}
.grupo-contexto {font-size: 0.8rem; opacity: 0.8; margin: 0 0 10px;}
.grupo-columnas {display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;}
.grupo-tarjeta {background: var(--cp-fondo); border: 1px solid var(--cp-borde);
  border-left: 4px solid var(--cp-petroleo); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 8px; min-width: 0;}
.grupo-tarjeta h4 {font-size: 0.88rem; font-weight: 600; margin: 0; padding: 0;}
.grupo-cantidad {font-size: 1.6rem; font-weight: 700; line-height: 1.1;}
.grupo-texto, .grupo-lectura {font-size: 0.8rem; line-height: 1.5;}
.grupo-barra {height: 10px; border-radius: 4px; background: var(--cp-borde); overflow: hidden;}
.grupo-barra > div {height: 100%; background: var(--cp-petroleo);}
.grupo-leyenda {display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px; font-size: 0.72rem; opacity: 0.8;}
.grupo-lectura {border-top: 1px solid var(--cp-borde); padding-top: 8px;}
.grupo-nota {font-size: 0.72rem; line-height: 1.5; opacity: 0.8; margin: 8px 0 0;}

/* ---------- Componentes de Streamlit ---------- */
div[data-testid="stMetric"] {background: var(--cp-fondo); border: 1px solid var(--cp-borde);
  border-left: 4px solid var(--cp-petroleo); border-radius: 10px; padding: 12px 14px;}
div[data-testid="stMetricLabel"] p {font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.75rem;}
div[data-testid="stMetricValue"] {color: var(--cp-noche); font-weight: 700;}
.stTabs [data-baseweb="tab"] p {font-weight: 600;}
div[data-testid="stExpander"] details {border-color: var(--cp-borde);}
div[data-testid="stExpander"] summary p {font-weight: 600;}

/* ---------- Panel de filtros oscuro (Noche) ---------- */
.st-key-filtros {background: var(--cp-noche); border: 1px solid var(--cp-noche); border-top: 4px solid var(--cp-petroleo);
  border-radius: 12px; padding: 1rem; color: #FFFFFF;}
.st-key-filtros label p, .st-key-filtros p, .st-key-filtros span, .st-key-filtros div[data-baseweb="select"] * {font-size: 0.75rem !important;}
.st-key-filtros div[data-testid="stVerticalBlock"] {gap: 0.9rem;}
.st-key-filtros label p, .st-key-filtros [data-testid="stMarkdownContainer"] p {color: #FFFFFF;}
.filtro-titulo {font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--cp-menta) !important; opacity: 1; margin: 0.2rem 0 0 0;}
/* cajas de selección */
.st-key-filtros div[data-baseweb="select"] > div {background: var(--cp-panel); border-color: var(--cp-panel-borde);}
.st-key-filtros div[data-baseweb="select"] div, .st-key-filtros div[data-baseweb="select"] input {color: #FFFFFF;}
.st-key-filtros div[data-baseweb="select"] svg {fill: var(--cp-menta);}
.st-key-filtros span[data-baseweb="tag"] {background: var(--cp-menta) !important;}
.st-key-filtros span[data-baseweb="tag"] span, .st-key-filtros span[data-baseweb="tag"] svg {color: var(--cp-noche) !important; fill: var(--cp-noche) !important;}
/* expander "Criterios de riesgo" */
.st-key-filtros div[data-testid="stExpander"] details {background: var(--cp-panel); border-color: var(--cp-panel-borde);}
.st-key-filtros div[data-testid="stExpander"] summary, .st-key-filtros div[data-testid="stExpander"] summary * {color: #FFFFFF; fill: #FFFFFF;}
.st-key-filtros div[data-testid="stExpander"] summary:hover * {color: var(--cp-menta); fill: var(--cp-menta);}
/* sliders: el petróleo no se ve sobre fondo oscuro, aquí se usa menta */
.st-key-filtros div[role="slider"] {background: var(--cp-menta) !important; border-color: var(--cp-menta) !important;}
.st-key-filtros [data-testid="stSliderThumbValue"] {color: var(--cp-menta) !important;}
.st-key-filtros [data-testid="stSliderTickBarMin"], .st-key-filtros [data-testid="stSliderTickBarMax"] {color: #8FA6AD !important;}
/* botón Limpiar filtros */
.st-key-filtros button {background: transparent; border: 1px solid var(--cp-menta); color: var(--cp-menta);}
.st-key-filtros button p {font-size: 0.75rem !important; font-weight: 600; color: inherit !important;}
.st-key-filtros button:hover, .st-key-filtros button:focus:not(:active) {background: var(--cp-menta); border-color: var(--cp-menta); color: var(--cp-noche);}

/* ---------- Responsivo (igual que antes) ---------- */
@media (max-width: 700px) {.grupo-columnas {grid-template-columns: 1fr;}}
@media(max-width: 700px) {.block-container {padding: 3.5rem 1rem 1rem;} .kpi {min-height: 0;} .kpi-label {min-height: 0;}
  .cp-marca {font-size: 1.35rem;} .cp-encabezado svg {width: 42px; height: 42px;}}
@media(max-width: 1000px) {
  div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-filtros) {flex-direction: column-reverse;}
  div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-filtros) > div[data-testid="stColumn"] {width: 100%; flex: 1 1 100%;}
}
@media(max-width: 700px) {
  div[data-testid="stHorizontalBlock"] {flex-wrap: wrap;}
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {width: 100%; flex: 1 1 100%;}
}
</style>
""".replace("FUENTE", FUENTE)

# Logo CartPulse: carrito de compras (petróleo) con un mouse dentro y un cable de pulso analítico (ámbar).
LOGO_SVG = """
<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="CartPulse Analytics">
  <path d="M4 10 H12 L19 40 H52 L58 18 H14" fill="none" stroke="#005F73" stroke-width="4.5"
        stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M19 40 L17.5 46 H51" fill="none" stroke="#001219" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="23" cy="53" r="4.5" fill="#001219"/>
  <circle cx="47" cy="53" r="4.5" fill="#001219"/>
  <polyline points="20,30 22.5,30 24.5,24 27,35 29,30 32,30" fill="none" stroke="#EE9B00"
            stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="32" y="21.5" width="13" height="16.5" rx="6.5" fill="#001219"/>
  <line x1="38.5" y1="21.5" x2="38.5" y2="28" stroke="#FFFFFF" stroke-width="1.3"/>
  <rect x="37.3" y="23.5" width="2.4" height="4" rx="1.2" fill="#94D2BD"/>
</svg>
"""


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
