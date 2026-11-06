# Dashboard de abandono de clientes · Equipo 5

Dashboard de una sola página en Streamlit para analizar el abandono (churn) de
50,000 clientes de una plataforma de e-commerce y priorizar acciones de retención.

## Navegación del dashboard

- Arriba: clientes activos, abandono y activos con señales de riesgo. Cada tarjeta conserva sus cantidades; **Ver comparación y explicación** abre la referencia general y el cálculo sin tapar los números.
- A la derecha: filtros de país, género y edad; **Criterios de riesgo** conserva los controles de carrito y llamadas. **Limpiar filtros** restaura la selección y la regla iniciales.
- Las gráficas se leen en dos columnas: llamadas, distribución del carrito, días sin comprar y combinaciones de carrito con llamadas. Los datos completos y sus cantidades siguen disponibles al pasar el cursor.
- Debajo: se pueden desplegar la participación del grupo dentro del negocio y el riesgo por país. Los botones **Todas las variables**, **Definiciones** y **Datos** mantienen sus consultas y la descarga CSV.
- Azul: información y referencias; verde/rojo: lectura favorable/desfavorable según la referencia indicada. La tasa general es una comparación, no una meta. La meta de riesgo es menos del 10%.

Comprobación de funcionamiento: `python -m unittest discover -s tests -v`.

## Cómo correr el proyecto

Requisitos: Python 3.9 o más reciente.

```bash
# 1. Clonar el repositorio
git clone https://github.com/USUARIO/proyecto-churn.git
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
├── app.py                  ← archivo de entrada (acomoda las piezas en la pantalla)
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
    └── ventanas.py         ← botones: todas las variables, definiciones y datos
```

## Indicadores

| KPI | Qué mide | Variables relacionadas en pantalla |
|---|---|---|
| **1 · Tasa de abandono** | % de clientes con `Churned = 1` (global: 28.9%) | Churn por llamadas a servicio, carrito abandonado y días sin comprar |
| **2 · Activos en perfil de riesgo** | Activos con carrito abandonado > 71.25% **y** 6+ llamadas, entre el total de activos. Meta: < 10% | Mapa de calor carrito × llamadas y % en riesgo por país |

## Reglas del equipo

1. La versión vigente es la rama `main` en GitHub.
2. Antes de trabajar: **pull**. Al terminar: **push** con un mensaje claro.
3. Cada quien edita solo su archivo (el responsable está al inicio de cada archivo).
4. Las rutas siempre son relativas (ver `src/config.py`).


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
