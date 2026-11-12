https://proyecto-churn-kble5abrozjksmebbubndb.streamlit.app

# Dashboard de abandono de clientes · Equipo 5

Dashboard en Streamlit con un **resumen general**, **tres pantallas (una por user persona)** y **recomendaciones finales**, para analizar el abandono (churn) de
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
| Poner KPI más pequeños | Las tarjetas se compactaron y quedaron en una sola fila arriba. La explicación del cálculo se abre con "Ver comparación y explicación" para no ocupar espacio | `src/seccion_kpis.py`, `src/estilos.py` y `paginas/andrea.py` (fila de KPI) |
| Retroalimentación posterior: quitar el total de clientes; con uno o dos indicadores basta | Se quitó la tarjeta de clientes. Quedan 2 KPI: tasa de abandono y activos en perfil de riesgo | `paginas/andrea.py`, `src/seccion_kpis.py` |
| Retroalimentación posterior: agregar un resumen general al inicio y recomendaciones finales | Pantalla 00 (situación, hallazgos y guía de uso) y pantalla 04 (acciones priorizadas con su dato de respaldo y cómo medirlas). Ambas se recalculan con los filtros | `paginas/resumen.py`, `paginas/recomendaciones.py`, `src/resumen.py` |

## Documentos del entregable

- `contrato-prompt.md`: contrato del prompt (qué muestra el tablero y la forma de la salida).
- `prompts/contrato-prompts.md`: registro de prompts del bloque 1, con su etapa del SDLC.

## Pantallas del dashboard

El menú de arriba cambia de pantalla. Los filtros de la derecha (país, género, edad y **Criterios de riesgo**) son los mismos para todas las pantallas y se conservan al cambiar.

| Pantalla | User persona | Pregunta que responde | Qué muestra |
|---|---|---|---|
| **00 · Resumen general** (`paginas/resumen.py`) | Todo el equipo | ¿Cuál es la situación del abandono y qué está relacionado con él? | Situación actual contra metas, 6 hallazgos (llamadas, carrito, días sin comprar, perfil de riesgo, segmento y valor) y guía de uso de las pantallas |
| **01 · Priorizar campañas** (`paginas/andrea.py`) | Andrea López, gerente de retención | ¿Dónde se concentra el abandono y a qué segmentos dirigir la campaña? | 2 KPI (abandono y riesgo), churn contra meta editable (25%), dona, mapa de calor carrito × llamadas, churn por edad / país / ciudad / antigüedad con exportación CSV |
| **02 · Alertas y calidad** (`paginas/luis.py`) | Luis Ramírez, operaciones de datos y CRM | ¿Hay alertas, los datos son confiables y quién entra a la lista? | Pestañas Monitoreo (alertas +2 pts y meta de 5%, calidad de datos), Datos (lista de activos en riesgo con búsqueda y descarga) y Definiciones |
| **03 · Valor y presupuesto** (`paginas/carlos.py`) | Carlos Mendoza, estrategia y valor del cliente | ¿Se van los clientes valiosos y dónde invertir? | Churn por cuartil de Lifetime_Value, segmentos de valor por país, escenario de reducción y datos que faltan para ROI |
| **05 · Clientes prioritarios** (`paginas/clientes.py`) | Andrea y Luis | ¿A qué clientes contactar primero y qué explica su riesgo? | Pestañas Scoring (toda la base ordenada por probabilidad, niveles Alto/Medio/Bajo, descarga CSV), Segmentos (3 clusters con perfil y nombre) y Modelo y variables (métricas, matriz de confusión y coeficientes) |
| **04 · Recomendaciones** (`paginas/recomendaciones.py`) | Todo el equipo | ¿Qué hacer primero y cómo medir si funcionó? | Tabla de prioridades y, por acción: qué hacer, por qué (dato), activos a quienes aplica, cómo medirlo y siguientes pasos |

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
├── app.py                  ← archivo de entrada: menú de 5 pantallas y filtros
├── paginas/
│   ├── resumen.py          ← pantalla 00 · resumen general
│   ├── andrea.py           ← pantalla 01 · priorizar campañas
│   ├── luis.py             ← pantalla 02 · alertas, calidad, datos y definiciones
│   ├── carlos.py           ← pantalla 03 · valor del cliente y presupuesto
│   ├── recomendaciones.py  ← pantalla 04 · recomendaciones finales
│   └── clientes.py         ← pantalla 05 · scoring, segmentos y modelo
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
    ├── contexto.py         ← datos y filtros compartidos por todas las pantallas
    ├── vistas.py           ← cálculos de las 3 pantallas (solo pandas)
    ├── resumen.py          ← cálculos del resumen y las recomendaciones (solo pandas)
    └── modelo.py           ← regresión logística, scoring y segmentos K-Means (scikit-learn)
```

## Indicadores

| KPI | Qué mide | Variables relacionadas en pantalla |
|---|---|---|
| **1 · Tasa de abandono** | % de clientes con `Churned = 1` (global: 28.9%) | Churn por llamadas a servicio, carrito abandonado y días sin comprar |
| **2 · Activos en perfil de riesgo** | Activos con carrito abandonado > 71.25% **y** 6+ llamadas, entre el total de activos. Meta: < 5% | Mapa de calor carrito × llamadas y % en riesgo por país |

## Modelo predictivo

| Elemento | Decisión |
|---|---|
| Modelo | Regresión logística (`src/modelo.py`) con 20 variables numéricas estandarizadas y 3 categóricas (género, país, trimestre de alta). `City` se dejó fuera por tener demasiadas categorías |
| División | 70% entrenamiento / 30% prueba, estratificada, `random_state=0` |
| Balanceo | `class_weight="balanced"`: sin balancear, el recall era de 39%; con balanceo sube a 70% |
| Métricas (prueba) | AUC 0.771 · Recall 70.4% · Precisión 48.6% · F1 0.575 · Accuracy 69.9% (línea base 71.1%) |
| Niveles de riesgo | Alto ≥ 70% · Medio 40% a 70% · Bajo < 40%. Churn histórico por nivel: 65.5%, 32.2% y 11.6% |
| Segmentos | K-Means con 3 grupos (método del codo) sobre 12 variables de comportamiento: Comprometidos (18.3% churn), Regulares (22.3%) y Desconectados (44.4%). Validación estadística en `notebooks/Equipo5_KMeans_Clustering.ipynb` |

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

## Entregable 2 · Contrato de datos y validación automática

El significado de las columnas, las unidades y el manejo de valores faltantes están en [contrato-datos.md](contrato-datos.md). La app carga el CSV, revisa que cumpla el contrato antes de dibujar información, y muestra un resumen de la verificación en el panel de filtros y en la pestaña **Luis > Monitoreo > Contrato de datos**. Las tablas principales incluyen ayuda en sus encabezados sobre el origen de las cifras.

### Ejecutar las pruebas

```bash
python -m unittest discover -s tests -v
```

El workflow de GitHub Actions es [validacion-datos.yml](.github/workflows/validacion-datos.yml) y se ejecuta en *push* y *pull request* contra `main`.

### Evidencia obligatoria: corrida fallida por dato roto

**ESTADO: PENDIENTE DE EJECUTAR EN GITHUB.** No colocar una liga hasta que exista una corrida real.

1. Crear una rama temporal a partir de `main`, por ejemplo `demostracion-error-datos`, sin modificar la rama publicada.
2. En esa rama, modificar intencionalmente **una celda numérica** del CSV, por ejemplo poner `ERROR` en `Credit_Balance` de un registro, y subir el cambio a la rama temporal.
3. Abrir un *pull request* a `main`; GitHub Actions debe ejecutar `contrato-y-regresion` y fallar indicando que `Credit_Balance` no es numérica.
4. Copiar aquí el enlace **real** a la ejecución fallida: `PENDIENTE: pegar URL de Actions`.
5. Restaurar el CSV correcto antes de integrar cambios, correr las pruebas hasta que pasen y cerrar el PR de demostración si ya no se necesita.
6. Para que realmente se impida fusionar un cambio incorrecto, un administrador debe configurar una protección o *ruleset* de `main` y exigir el *status check* `contrato-y-regresion` (una corrida fallida sin esa protección no impide necesariamente fusionar).

> **Nota:** una prueba sintética en `tests/test_contrato_datos.py` también reproduce el problema, pero no sustituye el enlace a una ejecución fallida exigido por la rúbrica.

### Observación de calidad con el CSV actual

Al revisar los 50,000 registros, se identificaron **168 valores fraccionarios `5,6818`** en `Customer_Service_Calls`. El dato es numérico y no viola la regla actual del contrato, pero representa una anomalía semántica porque la variable se describe como conteo de llamadas. La pantalla **Luis > Monitoreo** muestra la observación. Hasta verificar el origen no se asume que sean faltantes ni se redondean.

La implementación local superó 11 pruebas del contrato con la base actual. Esto **no equivale** a una ejecución de GitHub Actions ni sustituye la captura de una corrida fallida real.

## Evidencia: el pipeline detecta datos incorrectos

Prueba realizada el 12 de noviembre de 2026.

- Error introducido: ERROR_DEMO en la columna Age.
- Resultado: GitHub Actions detectó el dato no numérico.
- Estado: FAILED (errors=3).
- Los datos correctos permanecen en la rama del entregable.

[Ejecución fallida de GitHub Actions](https://github.com/a01666361-beep/proyecto-churn/actions/runs/43277557193)

