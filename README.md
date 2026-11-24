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
| **Meta** | Bajar a menos de 4.5% de los activos en perfil de riesgo |
| **Referencia (no meta)** | Tasa general de abandono: 28.9% (14,450 de 50,000 clientes) |

## Observaciones de la exposición del 21 de octubre

| Observación | Qué cambió | Dónde quedó |
|---|---|---|
| Hacer una pantalla donde se vieran bien los colores | Se unificó la identidad visual CartPulse: fondo oscuro, azul para datos, naranja para alertas y cian para estados favorables | `.streamlit/config.toml`, `src/config.py` y `src/estilos.py` |
| Poner KPI más pequeños | Las tarjetas se compactaron y quedaron en una sola fila arriba. La explicación del cálculo se abre con "Ver comparación y explicación" para no ocupar espacio | `src/seccion_kpis.py`, `src/estilos.py` y `paginas/andrea.py` (fila de KPI) |
| Retroalimentación posterior: quitar el total de clientes; con uno o dos indicadores basta | Se quitó la tarjeta de clientes. Quedan 2 KPI: tasa de abandono y activos en perfil de riesgo | `paginas/andrea.py`, `src/seccion_kpis.py` |
| Retroalimentación posterior: agregar un resumen general al inicio y recomendaciones finales | Pantalla 00 (situación, hallazgos y guía de uso) y pantalla 04 (acciones priorizadas con su dato de respaldo y cómo medirlas). Ambas se recalculan con los filtros | `paginas/resumen.py`, `paginas/recomendaciones.py`, `src/resumen.py` |

## Documentos del entregable

- **Parte 1 — Investigación:** [`investigacion/claude.md`](investigacion/claude.md), resumen del ciclo de Anthropic y tres cambios propuestos.
- **Parte 2 — Validación:** [`contrato-datos.md`](contrato-datos.md), [`prompts/B2.md`](prompts/B2.md), pruebas en `tests/` y [workflow de GitHub Actions](.github/workflows/validacion-datos.yml).
- **Parte 3 — Propuestas individuales:** [carpeta `ideas/`](ideas/) con un Markdown por integrante.
- **Bloque anterior:** [`contrato-prompt.md`](contrato-prompt.md) y [`prompts/contrato-prompts.md`](prompts/contrato-prompts.md).

## Observaciones de la sesión del 12 de noviembre

| # | Observación | Qué cambió | Dónde quedó |
|---|---|---|---|
| 1 | Botón "?" de cómo usar el dashboard en todas las pantallas | Botón "?" junto al título de cada pantalla con: para qué sirve, pasos de uso, cómo leer los indicadores y cómo funcionan los filtros | `src/ayuda.py` (`titulo_pantalla`) y las 6 pantallas |
| 2 | No usar preguntas como títulos; usar KPI y su correlación | Los subtítulos ahora dicen el dato: por ejemplo "Abandono 28.9% vs. meta 25.0%", "Carrito y llamadas: 63.8% de abandono en el perfil de riesgo (r = 0.28 y 0.29)" y "Abandono por cuartil de valor: Q4 39.6% vs. negocio 28.9%". Las gráficas de factores muestran su r | `paginas/*.py`, `src/seccion_factores.py`, `src/seccion_riesgo.py`, `src/seccion_grupo.py` |
| 3 | Cada gráfica explica lo que enseña | Botón "ⓘ" junto al título de cada gráfica: qué enseña, cómo leerla y qué decisión apoya. Streamlit no detecta el doble clic sobre una gráfica (Plotly lo usa para regresar el zoom), por eso es un clic en "ⓘ" | `src/ayuda.py` (`titulo_grafica`) |
| 4 | Separar el dashboard | El menú se agrupa en cuatro bloques: Inicio, Análisis por usuario (Andrea, Luis y Carlos), Modelo predictivo y Plan de acción | `app.py` |
| 5 | Subir la información del grupo problema | "Peso de este grupo en el problema" pasó del final (desplegable) a justo debajo de los KPI | `paginas/andrea.py`, `src/seccion_grupo.py` |
| 6 | Menos alertas; dinámicas, basadas en el modelo y funcionales | Dos alertas calculadas con la probabilidad del modelo: % de activos con riesgo alto (≥ 70%) y probabilidad promedio de los activos, contra el negocio + 2 pts. Cambian con los filtros (con 18 a 29 años se encienden). Se validan en "Probar las alertas con datos modificados" (simulación sobre una copia: con 1 llamada más por cliente se encienden). La calidad de datos dejó de ser alerta | `paginas/luis.py`, `src/vistas.py` (`alertas_modelo`, `simular_datos`), `src/puntuacion.py` (caché compartida del modelo) |
| 7 | Quitar u ocultar el dataset | Se quitó la pestaña "Datos". La lista de clientes queda en un desplegable cerrado (con descarga) en Luis y en Clientes prioritarios | `paginas/luis.py`, `paginas/clientes.py` |

Pruebas que verifican estos cambios: `test_retroalimentacion_12_noviembre` y `test_alertas_del_modelo_son_dinamicas` en `tests/test_dashboard.py`.

## Pantallas del dashboard

El menú de arriba está separado en cuatro bloques. Los filtros de la derecha (país, género, edad y **Criterios de riesgo**) son los mismos para todas las pantallas y se conservan al cambiar. Cada pantalla tiene un botón "?" con su guía de uso.

| Bloque | Pantalla | User persona | Decisión que habilita | Qué muestra |
|---|---|---|---|---|
| Inicio | **Resumen general** (`paginas/resumen.py`) | Todo el equipo | Entender la situación antes de entrar al detalle | Situación actual contra metas, 6 hallazgos y pantallas del dashboard |
| Análisis por usuario | **Andrea · Priorizar campañas** (`paginas/andrea.py`) | Andrea López, gerente de retención | A qué segmentos dirigir la campaña | 2 KPI, peso del grupo en el problema, abandono contra meta editable (25%), mapa de calor carrito × llamadas y abandono por segmento con exportación CSV |
| Análisis por usuario | **Luis · Monitoreo y calidad** (`paginas/luis.py`) | Luis Ramírez, operaciones de datos y CRM | Si hay alertas, si los datos son confiables y quién entra a la lista | Alertas del modelo con simulación para validarlas, calidad de datos, regla descriptiva de riesgo, lista de clientes oculta, contrato de datos y definiciones |
| Análisis por usuario | **Carlos · Valor y presupuesto** (`paginas/carlos.py`) | Carlos Mendoza, estrategia y valor del cliente | Si se van los clientes valiosos y dónde invertir | Churn por cuartil de Lifetime_Value, segmentos de valor por país, escenario de reducción y datos que faltan para ROI |
| Modelo predictivo | **Clientes prioritarios** (`paginas/clientes.py`) | Andrea y Luis | A qué clientes contactar primero | Scoring (niveles Alto/Medio/Bajo, lista oculta con descarga y explicación por cliente), Segmentos (3 clusters con validación estadística completa) y Modelo y variables |
| Modelo predictivo | **Segmentos** (`paginas/segmentos.py`) | Andrea y Carlos | Qué tipo de cliente se va más y a quién de cada segmento contactar primero | Churn por segmento contra la selección, activos por nivel de riesgo y lista de contacto por segmento (oculta, con descarga) |
| Modelo predictivo | **Comparativa y predicción** (`paginas/modelos.py`) | Andrea, Luis y Carlos | Con qué modelo puntuar y si a un cliente se le manda la campaña | Métricas de 5 modelos (árbol, bosque, red neuronal, logística y gradient boosting), curva ROC en test y formulario para predecir con el Gradient Boosting con las 11 variables del modelo final (regla > 30% → «No te vayas»; antes 50%, se bajó por indicación del profesor) |
| Plan de acción | **Recomendaciones** (`paginas/recomendaciones.py`) | Todo el equipo | Qué hacer primero y cómo medirlo | Tabla de prioridades y, por acción: qué hacer, por qué, activos a quienes aplica y cómo medirlo |

- **Limpiar filtros** restaura la selección y la regla oficial.
- Azul: datos y referencias; naranja: alertas o resultados desfavorables; cian: estados favorables y selecciones. La tasa general es una comparación, no una meta.

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
├── app.py                  ← archivo de entrada: menú de 6 pantallas y filtros
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
    ├── estilos.py          ← identidad visual y estilos CartPulse
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
| **2 · Activos en perfil de riesgo** | Activos con carrito abandonado > 71.25% **y** 6+ llamadas, entre el total de activos. Meta: < 4.5% | Mapa de calor carrito × llamadas y % en riesgo por país |

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
- `.streamlit/config.toml`: tema oscuro y paleta CartPulse Analytics.
- `requirements.txt`: librerías necesarias para ejecutar el dashboard, instaladas también en Streamlit Cloud.

### Paleta de colores vigente — CartPulse Analytics

| Uso | Color | Código |
|---|---|---|
| Fondo principal | Oscuro | `#1A1D24` |
| Tarjetas y contenedores | Azul grisáceo | `#293545` |
| Datos, botones y referencias | Azul | `#007BFF` |
| Alertas y resultados desfavorables | Naranja | `#FFA03A` |
| Estados favorables y filtros activos | Cian | `#3FD8E0` |
| Texto secundario | Gris claro | `#B0B7C3` |
| Texto principal | Blanco | `#FFFFFF` |
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

### Evidencia: el pipeline detectó un dato incorrecto

El 12 de noviembre de 2026 hicimos una prueba intencional en una rama separada: se escribió `ERROR_DEMO` en la columna numérica `Age` de un registro, GitHub Actions rechazó los datos y la ejecución terminó con error, como debía suceder. La prueba quedó en un *pull request* cerrado **sin integrar el CSV incorrecto en `main`**.

- [Prueba fallida real en GitHub Actions](https://github.com/a01666361-beep/proyecto-churn/actions/runs/43277557193).
- [Última ejecución aprobada en `main`](https://github.com/a01666361-beep/proyecto-churn/actions/runs/43787348010): **23 pruebas superadas**.
- La rama `main` todavía **no tiene protección obligatoria**: el pipeline informa el fallo, pero hace falta configurar el *status check* requerido para impedir un merge con pruebas fallidas.

Además, en **Luis > Monitoreo > Demostración de errores** se pueden revisar cuatro ejemplos seguros, realizados sobre copias en memoria, sin alterar el archivo original.
### Observación de calidad con el CSV actual

Al revisar los 50,000 registros, se identificaron **168 valores fraccionarios `5,6818`** en `Customer_Service_Calls`. El dato es numérico y no viola la regla actual del contrato, pero representa una anomalía semántica porque la variable se describe como conteo de llamadas. La pantalla **Luis > Monitoreo** muestra la observación. Hasta verificar el origen no se asume que sean faltantes ni se redondean.

## Comparativa de modelos y Gradient Boosting (pantalla 07)

| Elemento | Decisión |
|---|---|
| Notebook | `notebooks/Equipo5_Limpieza_y_Modelos_Churn.ipynb`: del crudo de 50,000 clientes a la limpieza variable por variable, logaritmos y comparación de árbol de decisión, bosque aleatorio, red neuronal, regresión logística y gradient boosting |
| Datos | `data/modelos/train_log.csv` (80%) y `data/modelos/test_log.csv` (20%), salidas del notebook. Primero se divide 80/20 (estratificado, `random_state=42`, la misma división que se usó en SAS) y después se limpia solo el train: cada error se demuestra con código (compras ×1.3, descuentos ×1.2, tickets inflados, valores imposibles y filas inventadas) y los faltantes se imputan según su significado (mediana del train, o mediana de su grupo de actividad en Email_Open_Rate y Session_Duration_Avg). Ambos con log(x+1) en 8 variables y coma decimal |
| Partición | Los modelos se entrenan con todo el 80% y se validan con validación cruzada de 10 grupos dentro del train (`KFold`, como en clase). En la tabla, «Validación» es el promedio de esos 10 grupos. El test solo se usa para el score final |
| Selección de variables | Comprobación en el notebook: con las 24 variables el AUC en validación cruzada es 0.9255 y con las 11 finales 0.9235 |
| Test | No se limpia ni se imputa, como indicó el profesor: conserva sus errores y vacíos, igual que llegarían clientes nuevos; solo se le aplica el logaritmo. Árbol, bosque y gradient boosting reciben los vacíos tal cual; la regresión logística y la red neuronal usan una copia rellenada con la mediana del train. `tests/test_modelo_gb.py` verifica que el test conserve sus vacíos |
| Variables | Las 11 del modelo final de SAS: log_Lifetime_Value, Cart_Abandonment_Rate, Customer_Service_Calls, Discount_Usage_Rate, log_Days_Since_Last_Purchase, Age, Email_Open_Rate, log_Total_Purchases, log_Returns_Rate, Pages_Per_Session y City. Las mismas en los cinco modelos y en train y test |
| Campeón | Gradient Boosting (`HistGradientBoostingClassifier`): mayor accuracy, AUC y KS en validación cruzada |
| Métricas del campeón (test, corte 0.5; con el corte actual de 0.3: Accuracy 90.6% · Recall 84.0% · Precisión 83.4% · F1 0.837) | AUC 0.924 · Accuracy 91.2% · Recall 76.9% · Precisión 91.3% · KS 0.773. En SAS (validación): Accuracy 91.7% · AUC 0.923 · KS 0.773. El bosque aleatorio queda casi empatado en AUC (0.924), pero abajo en accuracy, recall, F1 y KS |
| Predicción | `src/modelo_gb.py` vuelve a entrenar el mismo modelo con todo el train al abrir la pantalla (no depende de un `.pkl`) y reproduce exactamente el AUC del notebook. El usuario escribe los datos en escala normal y se aplica log(x+1) antes de predecir |
| Pruebas | `tests/test_modelo_gb.py`: el modelo del dashboard reproduce el AUC del notebook, la predicción desde escala original es igual a la del modelo y un dato faltante no se convierte en cero |
