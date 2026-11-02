# Dashboard de abandono de clientes · Equipo 5

Dashboard de una sola página en Streamlit para analizar el abandono (churn) de
50,000 clientes de una plataforma de e-commerce y priorizar acciones de retención.

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
├── app.py                  ← archivo de entrada (junta las secciones)
├── requirements.txt
├── data/
│   └── ecommerce_churn_final_comas.csv
├── notebooks/              ← Colab de las evidencias 1 y 2
└── src/
    ├── config.py           ← rutas, metas y regla de riesgo por defecto
    ├── limpieza.py         ← carga y limpieza (Evidencia 1)
    ├── indicadores.py      ← cálculo de los KPI (solo pandas)
    ├── filtros.py          ← barra lateral
    ├── seccion_kpis.py     ← 01 · Panorama general
    ├── seccion_factores.py ← 02 · Factores del abandono
    └── seccion_riesgo.py   ← 03 · Perfil de alto riesgo
```

## Indicadores

| KPI | Qué mide |
|---|---|
| Tasa de abandono | % de clientes con `Churned = 1` (referencia global: 28.9%) |
| Churn por llamadas a servicio | Tasa por rango de `Customer_Service_Calls` |
| Churn por carrito abandonado | Tasa por rango de `Cart_Abandonment_Rate` |
| Churn por días sin comprar | Tasa por rango de días desde la última compra |
| % de activos en perfil de riesgo | Activos con carrito abandonado > 71.25% **y** 6+ llamadas, entre el total de activos. Meta: < 10% |

## Reglas del equipo

1. La versión vigente es la rama `main` en GitHub.
2. Antes de trabajar: **pull**. Al terminar: **push** con un mensaje claro.
3. Cada quien edita solo su archivo (el responsable está al inicio de cada archivo).
4. Las rutas siempre son relativas (ver `src/config.py`).

## Equipo

Arlen Carolina Martínez González · José Gerardo Córdova Molina ·
Erick Eduardo Silva García · Irais Fernanda Granados Mendoza ·
Adán Ávila Esparza · Víctor Alejandro García Hernández ·
Sara Elizabeth Rivero Hernández
