https://proyecto-churn-kble5abrozjksmebbubndb.streamlit.app

# Dashboard de abandono de clientes · Equipo 5

Dashboard en Streamlit con **tres pantallas, una por user persona**, para analizar el abandono (churn) de
50,000 clientes de una plataforma de e-commerce y priorizar acciones de retención.

## Objetivo de negocio

| | |
|---|---|
| **Decisión que habilita** | A qué clientes activos dirigir la campaña de retención, y en qué país empezar |
| **Indicador** | % de clientes activos en perfil de riesgo (carrito abandonado > 71.25% **y** 6 o más llamadas a servicio), entre el total de activos |
| **Línea base** | 6.75%: 2,401 de 35,550 activos (dataset completo, sin filtros) |
| **Meta** | Bajar a menos de 5% de los activos en perfil de riesgo |
| **Referencia (no meta)** | Tasa general de abandono: 28.9% (14,450 de 50,000 clientes) |

## Observaciones de la exposición del 21 de octubre

| Observación | Qué cambió | Dónde quedó |
|---|---|---|
| Hacer una pantalla donde se vieran bien los colores | La paleta cambió a azules: azul para información y referencias, verde para lo favorable y rojo para lo desfavorable. Se documentó la paleta en este README | `.streamlit/config.toml`, `src/config.py`, `src/estilos.py` y la sección "Paleta de colores" de este README |
| Poner KPI más pequeños | Las tarjetas se compactaron y quedaron en una sola fila arriba (clientes activos, abandono y riesgo). La explicación del cálculo se abre con "Ver comparación y explicación" para no ocupar espacio | `src/seccion_kpis.py`, `src/estilos.py` y `app.py` (fila de KPI) |

## Documentos del entregable

- `contrato-prompt.md`: contrato del prompt (qué muestra el tablero y la forma de la salida).
- `prompts/contrato-prompts.md`: registro de prompts del bloque 1, con su etapa del SDLC.

## Pantallas del dashboard

El menú de arriba cambia de pantalla. Los filtros de la derecha (país, género, edad y **Criterios de riesgo**) son los mismos para las tres y se conservan al cambiar.

| Pantalla | User persona | Pregunta que responde | Qué muestra |
|---|---|---|---|
| **01 · Priorizar campañas** (`paginas/andrea.py`) | Andrea López, gerente de retención | ¿Dónde se concentra el abandono y a qué segmentos dirigir la campaña? | KPI, churn contra meta editable (25%), dona, mapa de calor carrito × llamadas, churn por edad / país / ciudad / antigüedad con exportación CSV |
| **02 · Alertas y calidad** (`paginas/luis.py`) | Luis Ramírez, operaciones de datos y CRM | ¿Hay alertas, los datos son confiables y quién entra a la lista? | Pestañas Monitoreo (alertas +2 pts y meta de 5%, calidad de datos), Datos (lista de activos en riesgo con búsqueda y descarga) y Definiciones |
| **03 · Valor y presupuesto** (`paginas/carlos.py`) | Carlos Mendoza, estrategia y valor del cliente | ¿Se van los clientes valiosos y dónde invertir? | Churn por cuartil de Lifetime_Value, segmentos de valor por país, escenario de reducción y datos que faltan para ROI |

- **Limpiar filtros** restaura la selección y la regla oficial.
- Azul: información y referencias; verde/rojo: lectura favorable/desfavorable según la referencia indicada. La tasa general es una comparación, no una meta.

Comprobación de funcionamiento: `python -m unittest discover -s tests -v`.

## Cómo correr el proyecto

Requisitos: Python 3.9 o más reciente.

```bash
# 1. Clonar el repositorio
git clone https://github.com/a01666361-beep/proyecto-churn.git
cd proyecto-churn

# 2. Instalar las dependencias
pip install -r requirements.txt

# 3. Correr la app
streamlit run app.py
```

La app se abre en el navegador en `http://localhost:8501`.

## Estructura

```
proyecto-churn/
├── app.py                  ← archivo de entrada: menú de 3 pantallas y filtros
├── paginas/
│   ├── andrea.py           ← pantalla 01 · priorizar campañas
│   ├── luis.py             ← pantalla 02 · alertas, calidad, datos y definiciones
│   └── carlos.py           ← pantalla 03 · valor del cliente y presupuesto
├── requirements.txt
├── data/
│   └── ecommerce_churn_final_comas.csv
├── notebooks/              ← Colab de las evidencias 1 y 2
└── src/
    ├── config.py           ← rutas, metas, rangos, nombres y colores
    ├── estilos.py          ← CSS para que todo quepa en una pantalla
    ├── limpieza.py         ← carga y limpieza (Evidencia 1)
    ├── indicadores.py      ← cálculo de los KPI (solo pandas)
    ├── filtros.py          ← panel de filtros (derecha)
    ├── seccion_kpis.py     ← tarjetas de los 2 KPI
    ├── seccion_factores.py ← variables del KPI 1 (llamadas, carrito, días)
    ├── seccion_riesgo.py   ← variables del KPI 2 (carrito × llamadas, país)
    ├── ventanas.py         ← botones: todas las variables, definiciones y datos
    ├── contexto.py         ← datos y filtros compartidos por las 3 pantallas
    └── vistas.py           ← cálculos de las 3 pantallas (solo pandas)
```

## Indicadores

| KPI | Qué mide | Variables relacionadas en pantalla |
|---|---|---|
| **1 · Tasa de abandono** | % de clientes con `Churned = 1` (global: 28.9%) | Churn por llamadas a servicio, carrito abandonado y días sin comprar |
| **2 · Activos en perfil de riesgo** | Activos con carrito abandonado > 71.25% **y** 6+ llamadas, entre el total de activos. Meta: < 5% | Mapa de calor carrito × llamadas y % en riesgo por país |

## Reglas del equipo

1. La versión vigente es la rama `main` en GitHub.
2. Antes de trabajar: **pull**. Al terminar: **push** con un mensaje claro.
3. Cada quien edita solo su archivo (el responsable está al inicio de cada archivo). Cada pantalla de `paginas/` tiene su responsable.
4. Para cambios grandes, trabajar en una rama y abrir un pull request para que otra persona lo revise.
5. Las rutas siempre son relativas (ver `src/config.py`).


## Despliegue en Streamlit Cloud

1. Entrar a share.streamlit.io e iniciar sesión con GitHub.
2. Clic en "New app" y elegir el repositorio `proyecto-churn`, rama `main`.
3. En "Main file path" escribir `app.py` y dar Deploy.

### Archivos de configuración
- `.streamlit/config.toml`: paleta de colores del dashboard (azules).
- `requirements.txt`: librerías que Streamlit Cloud instala automáticamente. Las líneas con `#` son para la siguiente semana (modelo Gradient Boosting).

### Paleta de colores
| Nombre | Código |
|---|---|
| Azul marino | `#0B2545` |
| Azul profundo | `#13315C` |
| Azul real | `#1D4E89` |
| Azul vivo | `#2E86DE` |
| Azul cielo | `#7FB3E6` |
| Azul pálido | `#D6E6F7` |
| Azul hielo | `#EEF4FB` |

## Equipo

Arlen Carolina Martínez González · José Gerardo Córdova Molina ·
Erick Eduardo Silva García · Irais Fernanda Granados Mendoza ·
Adán Ávila Esparza · Víctor Alejandro García Hernández ·
Sara Elizabeth Rivero Hernández
