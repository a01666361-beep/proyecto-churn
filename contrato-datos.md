# Contrato de datos — Equipo 5 · E-commerce Customer Churn

**Entregable 2 del módulo M4C · Build y Test**

Este documento describe las columnas que usa nuestro dashboard, de dónde sale cada una, en qué unidad está guardada y qué hacemos cuando una celda viene vacía, usamos el CSV `data/ecommerce_churn_final_comas.csv` como archivo principal y las reglas técnicas están en `src/contrato_datos.py`.

## Cómo interpretamos los valores faltantes

- Una celda vacía, `NA`, `N/A`, `N/D`, `null`, `None`, `nan`, `Sin dato`, `No disponible` o `-` indica que falta información, **no significa cero**.
- `0` sí es un número válido cuando el campo lo permite, por ejemplo cero llamadas o un cliente que no abandonó.
- `No aplica` significa que el valor no corresponde a ese caso, tampoco se convierte en cero, si aparece en una columna que necesita el dashboard debemos revisar el registro y decidir cómo tratarlo antes de cargarlo.
- En este entregable todas las columnas del CSV publicado se consideran **obligatorias** porque las pantallas o el modelo las usan, por eso un faltante impide cargar la base y muestra un error, esto evita presentar números que no podemos justificar.
- El separador decimal se maneja como coma y se convierte a tipo numérico, se mantienen los IDs como texto, y los valores almacenados en escala logarítmica **no se presentan como dinero**.

## Contrato columna por columna

| Columna | Tipo | Unidad / interpretación | Origen | Significado de una celda vacía |
|---|---|---|---|---|
| `Customer_ID` | texto | Identificador | CSV original | Sin identificador no se puede rastrear al cliente; carga rechazada |
| `Age` | numérico | años | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Gender` | texto | categoría | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Country` | texto | país | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `City` | texto | ciudad | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Membership_Years` | numérico | log(1 + años) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Login_Frequency` | numérico | frecuencia, periodo no documentado | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Session_Duration_Avg` | numérico | unidad no documentada | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Pages_Per_Session` | numérico | páginas por sesión | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Cart_Abandonment_Rate` | numérico | % (0–100) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Wishlist_Items` | numérico | log(1 + artículos) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Total_Purchases` | numérico | log(1 + compras) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Average_Order_Value` | numérico | log(1 + valor), moneda no documentada | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Days_Since_Last_Purchase` | numérico | log(1 + días) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Discount_Usage_Rate` | numérico | % (0–100) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Returns_Rate` | numérico | log(1 + tasa), base no documentada | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Email_Open_Rate` | numérico | % (0–100) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Customer_Service_Calls` | numérico | llamadas | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Product_Reviews_Written` | numérico | log(1 + reseñas) | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Social_Media_Engagement_Score` | numérico | puntos, escala no documentada | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Mobile_App_Usage` | numérico | unidad no documentada | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Payment_Method_Diversity` | numérico | número de métodos | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Lifetime_Value` | numérico | log(1 + valor), moneda no documentada | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Credit_Balance` | numérico | importe, moneda no documentada | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Signup_Quarter` | texto | trimestre Q1–Q4 | CSV original | Dato no informado: no equivale a cero; se rechaza la carga hasta revisarlo |
| `Churned` | numérico | indicador binario 0/1 | CSV original | No se conoce si abandonó; no se supone 0; carga rechazada |
| `Dias_Sin_Comprar` | numérico | días | Calculada: expm1(Days_Since_Last_Purchase) | No se puede calcular si falta el dato de origen; carga rechazada |
| `Grupo_Edad` | texto | rango de edad | Calculada: clasificación de Age | No se puede calcular si falta el dato de origen; carga rechazada |

## Columnas que se calculan al mostrar las tablas

Las siguientes cifras no son nuevas columnas del CSV, se generan a partir de los datos anteriores, deben etiquetarse como cálculos, predicciones o simulaciones para no mezclarlas.

| Columna visible | Tipo | Unidad | Origen | Si falta el dato base |
|---|---|---|---|---|
| `Estado` | categórico | Activo / Abandonó | Calculado desde `Churned` | No se calcula, se rechaza el CSV |
| `Clientes`, `Activos`, `Activos en riesgo` | entero | clientes | Recuento de registros y regla de riesgo | No se calcula hasta completar la base |
| `Churn` / `Churn histórico (%)` | numérico | proporción o %, según tabla | Tasa calculada con `Churned` | No se calcula hasta tener numerador y denominador válidos |
| `Mediana LTV` | numérico | escala log(1 + valor), sin moneda | Mediana calculada desde `Lifetime_Value` | No se calcula |
| `Probabilidad de churn (%)` | numérico | % (0–100) | Predicción del modelo logístico | No disponible si faltan variables del modelo |
| `Nivel de riesgo` | categórico | Alto, Medio, Bajo | Clasificación de la probabilidad del modelo | No se asigna si falta puntuación |
| `Segmento` | categórico | grupo de comportamiento | Asignado por K-Means | No se asigna si no puede puntuar / segmentar |
| `Prioridad` | entero | posición en lista | Calculada del orden de probabilidad estimada | No aplica si no existe la puntuación |
| `Clientes que se retendrían` y `De valor alto (Q4)` | entero | clientes hipotéticos | **Simulación:** clientes × reducción supuesta de churn | No se calcula y nunca se presenta como resultado observado |

## Reglas obligatorias y excepciones

**Reglas que bloquean automáticamente:** no puede faltar ninguna de las 26 columnas originales, ni contener un identificador vacío o duplicado, ninguna variable numérica puede quedar como texto, no se admiten infinitos ni nulos y `Churned` solo puede ser 0 o 1, se comprueban también la edad dentro de los grupos que usa la app (18–80 años), el carrito entre 0 y 100% y las llamadas y días sin comprar no negativos.

**Observación real detectada en el archivo:** 168 de los 50,000 registros tienen `Customer_Service_Calls = 5,6818` (fraccionario), aunque el nombre sugiere un conteo de llamadas. No hay evidencia para decidir si es una imputación de valores faltantes o una transformación deliberada. No se redondea ni se sustituye por cero: se conserva el dato del CSV y se muestra una advertencia en **Luis > Monitoreo**. La procedencia y el significado deben aclararse antes de usar esa variable para decisiones individuales.

**Cuestiones que requieren validación humana:** el CSV no documenta una moneda para `Credit_Balance`, `Average_Order_Value` o `Lifetime_Value`, tampoco especifica algunas unidades y periodicidades de actividad, por eso no las inventamos, si el equipo confirma esa información deberá actualizar este contrato y sus pruebas.

La prueba automática del contrato se ejecuta antes de dibujar gráficas, y el estado se puede revisar desde la pantalla de Luis, además GitHub Actions ejecutará estas verificaciones cuando se haga un cambio en `main` o se abra un pull request, para impedir la fusión de cambios fallidos es necesario activar una regla de protección de la rama.

**Base de definición:** `src/vistas.py` (tabla `DEFINICIONES`), `src/modelo.py`, `src/limpieza.py` y el README del proyecto, revisados el 12 de noviembre de 2026, las unidades que no están documentadas quedan expresamente marcadas como pendientes.
