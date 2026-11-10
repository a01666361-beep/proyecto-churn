# Registro de prompts — equipo 5 · Bloque 1

Asistentes usados: Claude (claude.ai). Ver la nota del prompt 6 sobre el último commit del dashboard.
Etapas tomadas de las nueve del SDLC con GenAI: planeación, diseño, diseño técnico, implementación, pruebas, revisión, documentación, incidentes, datos y analítica.

---

## Prompt 1 · Recalcular indicadores con la nueva base

**Fecha:** 26 de octubre de 2026
**Herramienta:** Claude (claude.ai)
**Etapa:** datos y analítica

### El prompt, literal

> Mira! La maestra nos dio esta retroalimentación, la nueva base de datos obliga un poquito a nuestro proyecto a cambiar  no se si mucho. pero mira: Christelle Navarrete Corella en lun 26 de oct de 2026 14:13
> Su propuesta vincula el análisis con una decisión de retención y muestra capacidad para revisar indicadores. Deben distinguir AUC, accuracy y recall, así como separar el abandono histórico del porcentaje de activos que cumplen una regla. Definan qué filtros afectan cada indicador y su denominador. El wireframe posterior mejora la selección de gráficos y las fórmulas; incorporen esas correcciones de forma consistente en la documentación del análisis.

Seguimiento, con el archivo `ecommerce_churn_final_comas.csv` adjunto:

> Esta es jiji

### Qué devolvió

Explicó la diferencia entre AUC, accuracy y recall, y separó el abandono histórico del % de activos en el perfil, con su numerador y su denominador. Con la base nueva recalculó todo (50,000 clientes, 28.9% de churn), avisó que ocho columnas venían en logaritmo y que los decimales usan coma, y propuso una regla nueva de alto riesgo: 7 o más llamadas y 5 o menos logins.

### Qué cambiamos de lo que devolvió

- No usamos su regla de riesgo. Nos quedamos con la regla de nuestro árbol de decisión de la Evidencia 2: carrito abandonado > 71.25% **y** 6 o más llamadas a servicio.
- Sí adoptamos la separación de denominadores: lo histórico se calcula sobre todos los clientes y lo accionable solo sobre activos. Así quedó en `src/indicadores.py`.
- Regresamos las columnas en logaritmo a su escala original en `src/limpieza.py` y leemos el archivo con `decimal=','`.

### Qué decidimos nosotros y no el modelo

- La regla de riesgo final y sus umbrales, que salen de nuestro propio modelo.
- Quitar la antigüedad como variable del perfil, porque en la base nueva no separa a quienes abandonan.
- Usar la tasa general (28.9%) como referencia y no como meta.

---

## Prompt 2 · Dashboard en una sola pantalla

**Fecha:** 2 de noviembre de 2026
**Herramienta:** Claude (claude.ai)
**Etapa:** diseño

### El prompt, literal

> ayudame a cambiar el dashboard con las siguientes correcciones:
> 1. el dashboard tiene que mostar la información de lo general a lo particular, según el profesor lo que tenemos uqe hacer es considerar 2 KPI´s (objetivo principal del monitoreo del dashboard) y en esa misma pantalla o al lado relacionar la información de las variables que se correlacionan con los indicadores ( es decir no tener la información de los perfiles de riesgo abajo porque no tiene ningún sentido si no lo relacionamos con la información principal de arriba de los KPI´s). 2. La información tiene que estar más compacta, lo ideal es no tener que scrollear hacia abajo sino que todo se vea en una misma pantalla, es la idea principal de un dashboard, tener la información en una sóla pantalla y con el resto de información menos relevante al alcance mediante otros botones a los que podemos acceder desde la pantalla principal. 3. No mencionar Insights ya que no es eficiente tener texto sin metricas clave a medio dashboard, tienen que ser inferibles mediante la información que arroja el tablero. Más organización de todos los segmentos, gráficas compactas, métricas llamativas y visibles, tener al alcance la información de el resto de variables en el dashboard y tener claro cómo se relacionan entre sí (no tener escritos insights sino que sean inferibles)
> Quítale los nombres a las pantallas justo
> que los filtros esten en la parte lateral derecha un poco más chicos

### Qué devolvió

Rediseñó el dashboard en una sola pantalla: cada KPI con sus variables al lado, mapa de calor carrito × llamadas, colores en lugar de insights escritos y filtros compactos a la derecha. Agregó `src/estilos.py`, `src/ventanas.py` y 3 botones (Todas las variables, Definiciones y Datos).

### Qué cambiamos de lo que devolvió

- Claude dejó cada KPI a la izquierda de su fila de gráficas. Después los pasamos a una sola fila arriba (prompt 4).
- A las 3 gráficas de barras les agregamos la caja de carrito abandonado y las acomodamos en dos columnas.
- Claude quitó todos los textos. Nosotros agregamos al final una nota de que los datos muestran relaciones, no causas.

### Qué decidimos nosotros y no el modelo

- Las correcciones que pedimos salen de la retroalimentación del profesor: de lo general a lo particular, una sola pantalla y sin insights escritos.
- La regla de riesgo que aparece en el mapa de calor (carrito > 71.25% y 6 o más llamadas), de nuestra Evidencia 2.

---

## Prompt 3 · Lista de tareas: paleta y KPI

**Fecha:** entre el 3 y el 5 de noviembre de 2026 (el historial no guarda la fecha exacta)
**Herramienta:** Claude (claude.ai)
**Etapa:** planeación

### El prompt, literal

> faltan unas cosas: definir paleta de colores, ver lo del menu desplegable (que lo voy a hacer yo) cambiar KPIs de lugar y que otra cosa nos recomiendas para mejorar el dashbard? hare una lista de tareas que hacer en github para repartirnos entre mis compañeros

Seguimiento:

> mas cortito porfa y super claro pon lo del menu desplegable cin mi nombre

### Qué devolvió

Una lista de tareas para GitHub con su archivo y cuándo se considera terminada: juntar la paleta en `config.py` y `.streamlit/config.toml`, poner 3 tarjetas KPI en una fila arriba, página del modelo, publicar en Streamlit Cloud y limpiar `__pycache__`. Luego la resumió en 8 puntos.

### Qué cambiamos de lo que devolvió

- Claude propuso 3 tarjetas (clientes totales, abandono y riesgo). Cambiamos "clientes totales" por "clientes activos", que es la base que todavía se puede retener.
- La página del modelo y la tabla de clientes en riesgo las dejamos para los siguientes bloques.

### Qué decidimos nosotros y no el modelo

- Cómo repartir las tareas entre los integrantes del equipo.
- Qué tareas entraban en este bloque y cuáles no.

---

## Prompt 4 · KPI compactos en una sola fila

**Fecha:** 4 de noviembre de 2026
**Herramienta:** Claude (claude.ai), usado por Sara Rivero
**Etapa:** implementación

### El prompt, literal

El texto original no se conservó. Esto es una reconstrucción aproximada del equipo, **no es literal**:

> Haz las tarjetas de los KPI más pequeñas y ponlas en una sola fila arriba: clientes totales, tasa de abandono y activos en riesgo. Que sigan cambiando con los filtros.

### Qué devolvió

Cambió `app.py`, `src/seccion_kpis.py` y `src/estilos.py`: las tarjetas quedaron más chicas y en una fila arriba, y se agregó la de clientes. Quedó en los commits "KPIs en una fila arriba: clientes, abandono y riesgo" y "tarjetas kpi´s compactas".

### Qué cambiamos de lo que devolvió

- Al juntarlo con el prompt 5 se perdió la explicación de los KPI y quedó un error (`NameError`) en la tarjeta de clientes. Lo corregimos.
- Lo marcamos como reconstruido en lugar de presentarlo como literal.

### Qué decidimos nosotros y no el modelo

- El orden de las tarjetas: clientes activos → tasa de abandono → activos en riesgo.
- Que la meta de riesgo se muestre en la tarjeta 3 (observación del 21 de octubre: KPI más pequeños).

---

## Prompt 5 · Explicación de los KPI al pasar el cursor

**Fecha:** 4 de noviembre de 2026
**Herramienta:** Claude (claude.ai)
**Etapa:** implementación

### El prompt, literal

> ahora si jeje listo. En fin, me puedes volver a pasar lo del menú desplegable? es decir a la hora de poner el cursos en un lado se despleha información no tanto que cambies de pestaña o pagina

Seguimiento:

> espera mi compañera actualizó el dashboard... en tal caso como le hafo ahorita que lo guarde

### Qué devolvió

CSS para `src/estilos.py` y un bloque `kpi-info` en cada tarjeta de `src/seccion_kpis.py`: al pasar el cursor aparece un recuadro con qué mide el KPI, cómo se calcula y la meta. Cuando Sara subió las tarjetas compactas, lo rehízo sobre esa versión y corrigió el `NameError`.

### Qué cambiamos de lo que devolvió

- Acortamos los textos para que cupieran en las tarjetas compactas.
- El recuadro tapaba el número de la tarjeta. Después lo cambiamos por el desplegable "Ver comparación y explicación" (prompt 6).

### Qué decidimos nosotros y no el modelo

- Qué dice cada explicación: qué mide, cómo se calcula y la meta.
- Que la explicación no debe obligar a cambiar de página.

---

## Prompt 6 · Desplegable "Ver comparación y explicación"

**Fecha:** 5 de noviembre de 2026
**Herramienta:** NO CONFIRMADO (commit de la cuenta `figura3academy`)
**Etapa:** implementación

### El prompt, literal

El texto original no se conservó. Esto es una reconstrucción aproximada del equipo, **no es literal**:

> Haz que la explicación de cada KPI no tape los números: ponla en un desplegable con la comparación contra el general, y conserva los filtros, las comparaciones y los botones de consulta.

### Qué devolvió

Cambió `src/seccion_kpis.py`, `src/estilos.py`, `src/config.py` y `.streamlit/config.toml`: puso la explicación y la comparación de cada KPI en un desplegable "Ver comparación y explicación" y dejó la paleta en azules. Quedó en el commit "Organiza dashboard y conserva filtros, comparaciones y consultas".

### Qué cambiamos de lo que devolvió

- Cambiamos la paleta a azul `#1D4E89` para información, y dejamos el verde y el rojo solo para lo favorable y lo desfavorable (observación del 21 de octubre: colores).
- Revisamos que el desplegable abriera con los filtros activos.

### Qué decidimos nosotros y no el modelo

- El significado de cada color: azul = referencia, verde = favorable, rojo = desfavorable.
- Que la tasa general (28.9%) se pinte en azul porque es referencia y no meta.

---

## Prompt 7 · Reunir prompts y armar el contrato del prompt

**Fecha:** 9 de noviembre de 2026
**Herramienta:** Claude (claude.ai)
**Etapa:** documentación

### El prompt, literal

> Hola! Oye nos piden este trabajo, reune todos los promtps para el dashboard de github (no de SAS) para completar el trabajo:

(con las instrucciones de la tarea adjuntas)

Seguimientos:

> esta es la liga. https://github.com/a01666361-beep/proyecto-churn.git. Las observaciones son que hicieramos una pantalla que vieramos los colores y que ademas piusieramos KPI mas pequeños creo que lo puse en un propmt. Pero esto era lo de antes ahorita te los paso

> si por facor y liego ime paso a paso que hacer para que lo pueda entregar

### Qué devolvió

Revisó el repositorio y redactó `contrato-prompt.md`, con pantallas, componentes, estados y la forma de la salida, y armó este registro. Señaló que la primera línea del README no era la URL de la app y que la meta de riesgo (< 10%) ya se cumplía con la línea base (6.75%). Después buscó en el historial los prompts literales del dashboard.

### Qué cambiamos de lo que devolvió

- No aceptamos la meta tal como estaba. Como ya se cumplía con la línea base, la bajamos a menos de 5%, en el README y en `src/config.py`.
- El primer borrador decía que los cambios de diseño se hicieron con Copilot. Lo corregimos con los prompts reales de Claude (prompts 2 a 5).
- Los prompts que no se conservaron los marcamos como reconstruidos, en lugar de presentarlos como literales.
- Revisamos que cada componente descrito en `contrato-prompt.md` coincida con lo que muestra el dashboard publicado.

### Qué decidimos nosotros y no el modelo

- Qué observaciones del 21 de octubre se atendieron y cómo.
- La meta de negocio final: menos de 5% (ver el README).
- Revisar que cada componente descrito en el contrato coincida con lo que hace el dashboard.
