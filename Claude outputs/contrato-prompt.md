# Contrato del prompt — equipo 5

**Etapa del SDLC:** diseño · implementación

## Qué debe mostrar

Una sola pantalla en Streamlit (layout ancho): a la izquierda, el contenido principal (4/5 del ancho), y a la derecha, los filtros (1/5).

| Componente | Qué muestra | Estados | Qué decisión habilita |
|---|---|---|---|
| Encabezado | Título "Abandono de clientes" y conteo "X de 50,000 clientes en el grupo seleccionado" | Cambia con los filtros | Saber sobre qué grupo se está leyendo todo lo demás |
| Filtros (derecha) | País, género y edad (multiselección; vacío = todos) | Sin filtro / con filtro; botón **Limpiar filtros** regresa a lo inicial | Elegir el segmento que se quiere analizar |
| Criterios de riesgo (desplegable en filtros) | Slider de carrito abandonado > (50–95%, inicia en 71.25%) y slider de llamadas ≥ (1–12, inicia en 6) | Regla inicial / regla ajustada | Probar qué tan estricta debe ser la regla antes de lanzar una campaña |
| Tarjeta 1 · Clientes activos | Número de activos y % de la selección que sigue activo | Con o sin clientes en la selección; "Ver comparación y explicación" muestra la cifra general | Dimensionar la base que todavía se puede retener |
| Tarjeta 2 · Tasa de abandono | % con `Churned = 1` en la selección y diferencia en puntos contra la tasa general (28.9%) | ▲ rojo si está arriba del general, ▼ verde si está abajo, ↔ azul si es igual | Identificar si el segmento abandona más que el negocio |
| Tarjeta 3 · Activos con señales de riesgo | Activos que cumplen la regla, entre el total de activos | Verde si es menor a la meta (5%), rojo si no | A cuántos clientes activos dirigir la campaña de retención |
| Gráfica 1 | Tasa de abandono por rango de llamadas a servicio (barras horizontales) | Verde/rojo contra la línea punteada de la tasa general | Qué nivel de llamadas debe disparar una alerta |
| Gráfica 2 | Distribución del carrito abandonado: activos vs. abandonaron (cajas) | — | Confirmar que el carrito separa a los dos grupos |
| Gráfica 3 | Tasa de abandono por días sin comprar (barras) | Verde/rojo contra la tasa general | A partir de cuántos días contactar a un cliente |
| Gráfica 4 | Mapa de calor carrito × llamadas con la tasa de abandono por celda | Escala verde (0%) → rojo (100%); "Sin datos" en celdas vacías | De dónde sale la regla de riesgo |
| Desplegable "¿Qué parte del problema está en este grupo?" | Cuántos clientes, abandonos y activos en riesgo del negocio caen en el grupo filtrado | — | Priorizar segmentos por tamaño, no solo por tasa |
| Desplegable "Activos con señales de riesgo por país" | % de activos en riesgo por país contra la línea de 5% | ▼ verde cumple la meta, ▲ rojo no cumple | En qué país empezar la campaña |
| Botón **Todas las variables** | Correlación de cada variable con el abandono y relación entre ellas | Aviso si hay menos de 10 clientes | Revisar si hay otra variable que debería entrar a la regla |
| Botón **Definiciones** | Cómo se calcula cada KPI (numerador y denominador) | — | Leer los números sin confundir los denominadores |
| Botón **Datos** | Tabla filtrada y descarga en CSV | — | Llevarse la lista de clientes para ejecutar la campaña |

Estado vacío: si un filtro deja 0 clientes, las gráficas se reemplazan por "No hay clientes con esta combinación de filtros. Prueba otra selección."

## El diseño de lo que debe arrojar

**Orden en la pantalla, de arriba hacia abajo:**

1. Título y conteo de clientes de la selección.
2. Botones: Todas las variables · Definiciones · Datos.
3. Tarjetas KPI, en una sola fila y compactas: clientes activos → tasa de abandono → activos en riesgo.
4. "Entender el abandono": cuatro gráficas en dos columnas (llamadas | carrito; días sin comprar | mapa de calor).
5. Desplegables: participación del grupo y riesgo por país.
6. Al final, una nota de cautela: los datos muestran relaciones, no causas.

**Indicadores y unidades:**

| Indicador | Numerador | Denominador | Unidad | Formato |
|---|---|---|---|---|
| Clientes activos | Clientes con `Churned = 0` | — | clientes | 35,550 |
| Tasa de abandono | Clientes con `Churned = 1` | Todos los clientes de la selección | % | 1 decimal (28.9%) |
| Diferencia contra el general | Tasa de la selección − 28.9% | — | puntos porcentuales | 1 decimal |
| Activos con señales de riesgo | Activos con carrito > 71.25% **y** 6 o más llamadas | Total de activos de la selección | % y clientes | 6.8% · 2,401 |

**Rangos de las gráficas:**

- Llamadas: 0–2, 3–5, 6–8, 9–11, 12+.
- Carrito: ≤30%, 30–50%, 50–71.25%, >71.25%.
- Días sin comprar: 0–30, 31–60, 61–90, 91–180, 180+.

**Colores:** azul (`#1D4E89`) para información y referencias; verde (`#168451`) para lo favorable; rojo (`#C0392B`) para lo desfavorable. La tasa general (28.9%) aparece siempre como referencia y no como meta. Las cantidades exactas se ven al pasar el cursor.

**Datos:** `data/ecommerce_churn_final_comas.csv`, que se lee con `decimal=','`. Las columnas en logaritmo se regresan a su escala original con `exp(x) − 1`.

## El prompt, literal

Usamos Claude (claude.ai) en tres prompts, y uno más que hizo una compañera para los KPI compactos. Los tres de Claude están copiados tal cual del historial, sin corregir.

**Prompt A · Claude, 2 de noviembre de 2026 (una sola pantalla). Es el prompt principal del rediseño.**

> ayudame a cambiar el dashboard con las siguientes correcciones:
> 1. el dashboard tiene que mostar la información de lo general a lo particular, según el profesor lo que tenemos uqe hacer es considerar 2 KPI´s (objetivo principal del monitoreo del dashboard) y en esa misma pantalla o al lado relacionar la información de las variables que se correlacionan con los indicadores ( es decir no tener la información de los perfiles de riesgo abajo porque no tiene ningún sentido si no lo relacionamos con la información principal de arriba de los KPI´s). 2. La información tiene que estar más compacta, lo ideal es no tener que scrollear hacia abajo sino que todo se vea en una misma pantalla, es la idea principal de un dashboard, tener la información en una sóla pantalla y con el resto de información menos relevante al alcance mediante otros botones a los que podemos acceder desde la pantalla principal. 3. No mencionar Insights ya que no es eficiente tener texto sin metricas clave a medio dashboard, tienen que ser inferibles mediante la información que arroja el tablero. Más organización de todos los segmentos, gráficas compactas, métricas llamativas y visibles, tener al alcance la información de el resto de variables en el dashboard y tener claro cómo se relacionan entre sí (no tener escritos insights sino que sean inferibles)
> Quítale los nombres a las pantallas justo
> que los filtros esten en la parte lateral derecha un poco más chicos

**Prompt B · Claude, entre el 3 y el 5 de noviembre de 2026 (lista de tareas: paleta y KPI)**

> faltan unas cosas: definir paleta de colores, ver lo del menu desplegable (que lo voy a hacer yo) cambiar KPIs de lugar y que otra cosa nos recomiendas para mejorar el dashbard? hare una lista de tareas que hacer en github para repartirnos entre mis compañeros

**Prompt C · Claude, entre el 3 y el 5 de noviembre de 2026 (explicación al pasar el cursor)**

> ahora si jeje listo. En fin, me puedes volver a pasar lo del menú desplegable? es decir a la hora de poner el cursos en un lado se despleha información no tanto que cambies de pestaña o pagina

**Prompt D · KPI compactos (lo hizo [nombre de la compañera] con [herramienta]). NO es literal: el texto original no se conservó y esta es una reconstrucción aproximada del equipo.**

> Haz las tarjetas de los KPI más pequeñas y ponlas en una sola fila arriba: clientes totales, tasa de abandono y activos en riesgo. Que sigan cambiando con los filtros.

## Qué devolvió

Claude rediseñó el dashboard en una sola pantalla: cada KPI con sus variables al lado, mapa de calor carrito × llamadas, colores en lugar de insights escritos, filtros compactos a la derecha y 3 botones (Todas las variables, Definiciones, Datos). También propuso una lista de tareas (paleta en `config.py`, KPI en una fila) y un recuadro con la explicación de cada KPI al pasar el cursor. Con el Prompt D, las tarjetas quedaron compactas en una fila arriba.

## Qué cambiamos de lo que devolvió

- **De 2 KPI a 3 tarjetas en una fila:** Claude puso cada KPI a la izquierda de su fila de gráficas. Nosotros juntamos las tarjetas en una sola fila arriba y agregamos la de clientes activos (observación del 21 de octubre: KPI más pequeños).
- **Explicación al pasar el cursor:** antes las tarjetas no explicaban nada. Con el Prompt C agregamos un recuadro que, al pasar el cursor, dice qué mide cada KPI, cómo se calcula y cuál es la meta. Como las tarjetas quedaron compactas con el Prompt D, acortamos los textos de Claude para que cupieran y corregimos un error (`NameError`) en la tarjeta de clientes, que hacía tronar el dashboard.
- **Paleta:** Claude usaba azul `#185FA5`, con la línea de referencia en rojo. La cambiamos a azul `#1D4E89` para información, y dejamos el verde y el rojo solo para lo favorable y lo desfavorable. La tasa general va en azul porque es referencia, no meta (observación del 21 de octubre: colores).
- **Gráficas:** a las 3 barras de Claude les agregamos la caja de carrito abandonado y las acomodamos en dos columnas, con el mapa de calor.
- **Meta:** Claude dejó la meta en 10%. La cambiamos a 5% porque la línea base (6.75%) ya estaba debajo de 10% y la meta no habría exigido nada.
- **Nota de cautela:** Claude quitó todos los textos. Nosotros agregamos al final una nota de que los datos muestran relaciones, no causas.

## Qué decidimos nosotros y no el modelo

- **La regla de riesgo** (carrito > 71.25% y 6 o más llamadas). Sale del árbol de decisión de nuestra Evidencia 2.
- **La meta de riesgo:** bajar de 6.75% (línea base) a menos de 5% de los activos en perfil de riesgo.
- **Que la tasa general (28.9%) sea una referencia y no una meta.** Por eso se pinta en azul y no en verde o rojo.
- **Los denominadores.** Lo histórico (tasa de abandono) se calcula sobre todos los clientes de la selección; lo accionable (a quién contactar) se calcula solo sobre activos.
- **Qué variables se muestran:** llamadas, carrito y días sin comprar, porque son las que separan a quienes abandonan en nuestros datos. Antigüedad, género y país no lo hacen.
- **Que el dashboard sirva para decidir a quién dirigir la campaña de retención.**
