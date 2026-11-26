**Corrida del CI en verde:** PEGAR_AQUI_LA_LIGA_A_LA_CORRIDA_VERDE_DE_GITHUB_ACTIONS

# Entregable 3 · Del tablero al producto

Tablero: https://proyecto-churn-kble5abrozjksmebbubndb.streamlit.app · Equipo 5

El pipeline de GitHub Actions ([`validacion-datos.yml`](../.github/workflows/validacion-datos.yml)) corre en cada *push* y *pull request* a `main`. Tiene un paso propio, **«Verificar contraste de la paleta (WCAG 2.2 AA)»**, que imprime la tabla de la sección 2 y falla si un par de colores no llega al mínimo. Las otras tres piezas del entregable también se verifican con pruebas: preguntas de las gráficas ([`tests/test_preguntas_graficas.py`](../tests/test_preguntas_graficas.py)), estado vacío ([`tests/test_estado_vacio.py`](../tests/test_estado_vacio.py)) y acceso por rol ([`tests/test_acceso.py`](../tests/test_acceso.py)).

## 1. Las gráficas, cada una con su pregunta

Cada gráfica muestra su pregunta debajo del título («**Pregunta:** ¿…?») y la repite en el botón ⓘ junto con qué enseña, cómo leerla y qué decisión apoya. La pregunta es un argumento obligatorio de `ayuda.titulo_grafica(..., pregunta=...)`: sin ella la app no corre. Además, `tests/test_preguntas_graficas.py` revisa tres cosas en el código: que toda llamada tenga una pregunta escrita como pregunta (¿…?), que no haya dos gráficas con la misma pregunta y que ningún `st.plotly_chart()` aparezca sin un título con pregunta antes.

| Pantalla | Pregunta que responde | Decisión que habilita | Dónde está |
|---|---|---|---|
| Actualización de datos y del modelo | ¿Los clientes nuevos se parecen a los que se usaron para entrenar el modelo, o conviene reentrenarlo? | Si los clientes nuevos se parecen a los del entrenamiento o si conviene reentrenar. | `paginas/actualizacion.py:149` |
| Andrea · Priorizar campañas | ¿El abandono de este grupo está arriba o abajo de la meta, y qué tan urgente es actuar? | Qué tan urgente es la campaña de retención para este grupo. | `paginas/andrea.py:52` |
| Andrea · Priorizar campañas | ¿Con qué combinación de carrito abandonado y llamadas a servicio se concentra el abandono? | De aquí sale la regla de riesgo que define a quién contactar. | `paginas/andrea.py:87` |
| Andrea · Priorizar campañas | ¿Qué segmento abandona más y tiene suficientes clientes para justificar una campaña? | A qué segmentos dirigir primero la campaña, considerando también su tamaño. | `paginas/andrea.py:104` |
| Andrea · Priorizar campañas | ¿A partir de cuántas llamadas o días sin comprar conviene activar una acción de retención? | Qué comportamiento usar como disparador de una acción de retención. | `paginas/andrea.py:137` |
| Carlos · Valor y presupuesto | ¿Se están yendo más los clientes de mayor valor que el resto? | Si hay que proteger primero a los clientes de mayor valor. | `paginas/carlos.py:63` |
| Carlos · Valor y presupuesto | ¿En qué países se concentran los clientes valiosos en riesgo? | En qué países conviene concentrar la inversión en retención. | `paginas/carlos.py:86` |
| Carlos · Valor y presupuesto | ¿Cuántos clientes se retendrían si el abandono bajara lo que supone el escenario? | Dimensionar el beneficio potencial antes de pedir presupuesto. | `paginas/carlos.py:107` |
| Clientes prioritarios | ¿Cuántos clientes activos están en riesgo alto y por qué nivel conviene empezar la campaña? | Cuántos clientes caben en la campaña y por qué nivel empezar. | `paginas/clientes.py:57` |
| Clientes prioritarios | ¿Por qué este cliente tiene riesgo alto y qué conviene decirle al contactarlo? | Qué mensaje o acción usar con ese cliente al contactarlo. | `paginas/clientes.py:95` |
| Clientes prioritarios | ¿Qué tan grande es cada segmento y qué comportamiento lo caracteriza? | Qué mensaje y canal usar con cada segmento. | `paginas/clientes.py:157` |
| Clientes prioritarios | ¿Qué segmento abandona más, y la diferencia es real o casualidad? | A qué segmento dirigir primero la retención. | `paginas/clientes.py:174` |
| Clientes prioritarios | ¿En qué comportamiento se diferencia cada segmento del cliente promedio? | Qué mensaje y qué acción usar con cada segmento. | `paginas/clientes.py:194` |
| Clientes prioritarios | ¿Cuántos abandonos detecta el modelo y a cuántos clientes contactaríamos de más? | Si el balance entre clientes detectados y contactos de más es aceptable. | `paginas/clientes.py:232` |
| Clientes prioritarios | ¿Qué comportamientos pesan más en el riesgo que calcula el modelo? | Qué comportamientos atacar con las acciones de retención. | `paginas/clientes.py:261` |
| Luis · Monitoreo y calidad | ¿El grupo seleccionado tiene más riesgo que el negocio como para adelantar la campaña? | Si conviene adelantar la campaña de retención para el grupo seleccionado. | `paginas/luis.py:57` |
| Comparativa y predicción | ¿Qué modelo predice mejor el abandono en clientes que no vio al entrenar? | Confirmar que el Gradient Boosting es el que conviene usar para puntuar a los clientes. | `paginas/modelos.py:65` |
| Comparativa y predicción | ¿Qué modelo separa mejor a los clientes que se van de los que se quedan? | Elegir el modelo que mejor separa a los clientes que se van de los que se quedan. | `paginas/modelos.py:99` |
| Comparativa y predicción | ¿Hay que enviarle la campaña de retención a este cliente en particular? | Decidir si a un cliente concreto se le envía la campaña de retención. | `paginas/modelos.py:131` |
| Recomendaciones | ¿Qué acción de retención conviene lanzar primero? | Qué acción lanzar primero. | `paginas/recomendaciones.py:30` |
| Resumen general | ¿Qué comportamientos están más relacionados con el abandono? | Qué señales usar para decidir a quién contactar. | `paginas/resumen.py:44` |
| Segmentos | ¿Qué segmento de clientes abandona más? | Qué segmento atender primero. | `paginas/segmentos.py:61` |
| Segmentos | ¿En qué segmento está el mayor volumen de clientes que conviene contactar? | Dónde está el volumen de clientes que conviene contactar. | `paginas/segmentos.py:80` |
| Andrea · ventana «Todas las variables» | ¿Qué variables suben o bajan junto con el abandono? | Qué variables vale la pena vigilar como señal de riesgo. | `src/ventanas.py:33` |
| Andrea · ventana «Todas las variables» | ¿A partir de qué valor de esta variable sube el abandono? | Desde qué valor de la variable conviene activar una acción. | `src/ventanas.py:54` |

**Gráficas eliminadas (no habilitaban ninguna decisión).** Eran 12. Respondían preguntas de método («¿cuántos clusters?», «¿los grupos son estables?»), no de negocio, y eliminarlas es el resultado correcto:
- En Clientes prioritarios → Segmentos se quitaron 10:
  - método del codo;
  - V de Cramér por número de clusters;
  - tres índices de validación (silueta, Calinski-Harabasz y Davies-Bouldin);
  - dos proyecciones 2D (variables y PCA);
  - estabilidad con otras semillas;
  - Kruskal-Wallis;
  - dendrograma.

  Esa validación sigue completa en `notebooks/Equipo5_KMeans_Clustering.ipynb`.
- En la ventana «Todas las variables» se quitó la matriz de correlación entre variables.
- En Comparativa y predicción se quitó la importancia de variables, que repetía la gráfica de Clientes prioritarios → Modelo y variables.

## 2. La paleta, con las razones de contraste calculadas

La paleta (CartPulse) se define una sola vez en [`src/config.py`](../src/config.py) y se usa en el tema de Streamlit ([`.streamlit/config.toml`](../.streamlit/config.toml)) y en el CSS ([`src/estilos.py`](../src/estilos.py)).

**Cómo se calcula:** [`src/contraste.py`](../src/contraste.py) aplica la fórmula de luminancia relativa de WCAG 2.2: razón = (L₁ + 0.05) / (L₂ + 0.05). Para los chips con fondo translúcido (`rgba`), primero mezcla el color con la tarjeta que tiene debajo.

**Mínimos de WCAG 2.2 AA:**
- 4.5:1 para texto normal (criterio 1.4.3).
- 3:1 para texto grande (24 px o más, o 18.66 px en negritas).
- 3:1 para elementos no textuales: barras, bordes de estado y controles (criterio 1.4.11).

**Qué revisa la prueba [`tests/test_contraste.py`](../tests/test_contraste.py):**
- Que cada par de colores llegue a su mínimo.
- Que el tema de Streamlit y las variables del CSS usen los mismos colores que `src/config.py`. Así, un color cambiado en un solo archivo no se escapa de la revisión.
- Que el color de bordes `#343B4A` (1.5:1) no se use para dibujar datos.

**Colores que se cambiaron porque no pasaban:**

| Uso | Antes | Razón antes | Ahora | Razón ahora |
|---|---|---|---|---|
| Texto blanco en botones principales | `#007BFF` | 3.98:1 ❌ | `#0066D6` | 5.42:1 ✅ |
| Barras «por debajo del promedio» sobre tarjeta | `#3A6EA5` | 2.34:1 ❌ | `#6699CC` | 4.14:1 ✅ |
| Chips naranjas (fondo 18 %) | `#FFA03A` sobre su mezcla | 4.40:1 ❌ | fondo al 12 % | 4.92:1 ✅ |
| Chip azul (texto `#4DA3FF`) | `#4DA3FF` sobre su mezcla | 3.92:1 ❌ | texto blanco | 10.12:1 ✅ |
| Chip gris (fondo 16 %) | `#B0B7C3` sobre su mezcla | 4.46:1 ❌ | fondo al 12 % | 4.83:1 ✅ |
| Riesgo bajo en «Activos de cada segmento» | `#343B4A` | 1.50:1 ❌ | `#B0B7C3` | 8.36:1 ✅ |

**El azul de datos `#007BFF` se conserva**, pero solo donde cumple:
- Como texto grande: valores de KPI de 2.4 rem, con 3.12:1 sobre la tarjeta.
- Como barras y marcas: 4.24:1 sobre el fondo.

El texto azul pequeño usa `#4DA3FF`, con 6.42:1 sobre el fondo.

**Tabla completa** (la imprime `python -m src.contraste` en cada corrida del CI):

| Uso | Frente | Fondo | Tipo | Razón | Mínimo | Cumple |
|---|---|---|---|---|---|---|
| Texto principal sobre el fondo | `#FFFFFF` | `#1A1D24` | texto | **16.87:1** | 4.5:1 | ✅ |
| Texto principal dentro de tarjetas y KPI | `#FFFFFF` | `#293545` | texto | **12.43:1** | 4.5:1 | ✅ |
| Subtítulos, ayudas y notas sobre el fondo | `#B0B7C3` | `#1A1D24` | texto | **8.36:1** | 4.5:1 | ✅ |
| Texto secundario dentro de tarjetas | `#B0B7C3` | `#293545` | texto | **6.16:1** | 4.5:1 | ✅ |
| Ligas y pestaña activa | `#4DA3FF` | `#1A1D24` | texto | **6.42:1** | 4.5:1 | ✅ |
| Texto azul pequeño dentro de tarjetas | `#4DA3FF` | `#293545` | texto | **4.73:1** | 4.5:1 | ✅ |
| Mensajes de alerta sobre el fondo | `#FFA03A` | `#1A1D24` | texto | **8.31:1** | 4.5:1 | ✅ |
| Alertas dentro de tarjetas | `#FFA03A` | `#293545` | texto | **6.12:1** | 4.5:1 | ✅ |
| Título del panel de filtros | `#3FD8E0` | `#1A1D24` | texto | **9.73:1** | 4.5:1 | ✅ |
| Texto oscuro de un filtro activo (etiqueta cian) | `#1A1D24` | `#3FD8E0` | texto | **9.73:1** | 4.5:1 | ✅ |
| Texto de los botones principales | `#FFFFFF` | `#0066D6` | texto | **5.42:1** | 4.5:1 | ✅ |
| Botón principal al pasar el cursor | `#FFFFFF` | `#0056B3` | texto | **7.04:1** | 4.5:1 | ✅ |
| Valor grande de los KPI y de st.metric | `#007BFF` | `#293545` | texto grande | **3.12:1** | 3.0:1 | ✅ |
| Números grandes sobre el fondo | `#007BFF` | `#1A1D24` | texto grande | **4.24:1** | 3.0:1 | ✅ |
| Barras principales de las gráficas | `#007BFF` | `#1A1D24` | no textual | **4.24:1** | 3.0:1 | ✅ |
| Barra de proporción del grupo en tarjetas | `#007BFF` | `#293545` | no textual | **3.12:1** | 3.0:1 | ✅ |
| Barras «por debajo del promedio» | `#6699CC` | `#1A1D24` | no textual | **5.62:1** | 3.0:1 | ✅ |
| Barras «por debajo del promedio» sobre tarjeta | `#6699CC` | `#293545` | no textual | **4.14:1** | 3.0:1 | ✅ |
| Barras y marcas de alerta | `#FFA03A` | `#1A1D24` | no textual | **8.31:1** | 3.0:1 | ✅ |
| Borde de KPI en alerta | `#FFA03A` | `#293545` | no textual | **6.12:1** | 3.0:1 | ✅ |
| Barras favorables y controles activos | `#3FD8E0` | `#1A1D24` | no textual | **9.73:1** | 3.0:1 | ✅ |
| Borde de KPI favorable | `#3FD8E0` | `#293545` | no textual | **7.17:1** | 3.0:1 | ✅ |
| Series neutras de las gráficas | `#B0B7C3` | `#1A1D24` | no textual | **8.36:1** | 3.0:1 | ✅ |
| Contorno del botón principal | `#0066D6` | `#1A1D24` | no textual | **3.11:1** | 3.0:1 | ✅ |
| Serie 1 de las gráficas con varias series | `#007BFF` | `#1A1D24` | no textual | **4.24:1** | 3.0:1 | ✅ |
| Serie 2 de las gráficas con varias series | `#FFA03A` | `#1A1D24` | no textual | **8.31:1** | 3.0:1 | ✅ |
| Serie 3 de las gráficas con varias series | `#3FD8E0` | `#1A1D24` | no textual | **9.73:1** | 3.0:1 | ✅ |
| Serie 4 de las gráficas con varias series | `#B0B7C3` | `#1A1D24` | no textual | **8.36:1** | 3.0:1 | ✅ |
| Serie 5 de las gráficas con varias series | `#6699CC` | `#1A1D24` | no textual | **5.62:1** | 3.0:1 | ✅ |
| Serie 6 de las gráficas con varias series | `#FFFFFF` | `#1A1D24` | no textual | **16.87:1** | 3.0:1 | ✅ |
| Chip .chip-rojo dentro de una tarjeta | `#FFA03A` | `#434244` | texto | **4.92:1** | 4.5:1 | ✅ |
| Chip .chip-verde dentro de una tarjeta | `#3FD8E0` | `#2D4F5E` | texto | **5.06:1** | 4.5:1 | ✅ |
| Chip .chip-azul dentro de una tarjeta | `#FFFFFF` | `#21436A` | texto | **10.12:1** | 4.5:1 | ✅ |
| Chip .chip-celeste dentro de una tarjeta | `#FFFFFF` | `#21436A` | texto | **10.12:1** | 4.5:1 | ✅ |
| Chip .chip-ambar dentro de una tarjeta | `#FFA03A` | `#434244` | texto | **4.92:1** | 4.5:1 | ✅ |
| Chip .chip-naranja dentro de una tarjeta | `#FFA03A` | `#434244` | texto | **4.92:1** | 4.5:1 | ✅ |
| Chip .chip-arena dentro de una tarjeta | `#FFA03A` | `#434244` | texto | **4.92:1** | 4.5:1 | ✅ |
| Chip .chip-gris dentro de una tarjeta | `#B0B7C3` | `#394554` | texto | **4.83:1** | 4.5:1 | ✅ |

**Paleta inclusiva (no depende solo del color).** Se usa azul contra naranja, una combinación que sigue siendo distinguible en los tipos más comunes de daltonismo (protanopía y deuteranopía), en lugar de rojo contra verde. Además, la información nunca depende solo del color: las barras llevan su porcentaje escrito, los chips de comparación llevan flecha (▲ / ▼) y texto, las líneas de referencia llevan etiqueta y los mapas de calor muestran su valor dentro de cada celda.

## 3. La jerarquía, justificada con la fuente

> **Pendiente del equipo:** citar la **investigación 1** (la de lectura) en cada punto. El criterio pide que la justificación venga de esa investigación y no de preferencias personales. Abajo está la jerarquía tal como está construida, con el espacio para la cita.

| Nivel | Qué se ve | Dónde | Justificación (investigación 1) |
|---|---|---|---|
| 1 | Título de la pantalla y conteo del grupo («7,534 de 50,000 clientes en el grupo seleccionado») | Arriba a la izquierda de cada pantalla | *[cita de la investigación 1]* |
| 2 | Dos KPI grandes (tasa de abandono y activos en perfil de riesgo) contra su meta | Primera fila, números a 2.4 rem en azul | *[cita]* |
| 3 | Peso del grupo seleccionado en el problema | Justo debajo de los KPI (retroalimentación del 12 de noviembre) | *[cita]* |
| 4 | Gráficas de detalle con su pregunta | Debajo, en pares | *[cita]* |
| 5 | Listas de clientes | Cerradas en un desplegable, solo para Operaciones | *[cita]* |
| — | Filtros | Columna derecha, separada del contenido | *[cita]* |

## 4. El estado vacío y dónde está el `st.stop()`

**Qué significa «nada seleccionado» en este tablero:** un filtro sin opciones elegidas significa **todos**; el cuadro lo dice con el texto «Todos». El caso vacío real es cuando la combinación de filtros deja **0 clientes**.

**Qué pasa en ese caso:** la pantalla muestra «No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.», y `st.stop()` corta la ejecución antes de calcular tasas o dibujar gráficas. Así no se divide entre cero ni se muestra una gráfica vacía.

| Pantalla | Dónde está el `st.stop()` |
|---|---|
| Resumen general | `paginas/resumen.py:25` |
| Andrea · Priorizar campañas | `paginas/andrea.py:38` |
| Luis · Monitoreo y calidad | `paginas/luis.py:31` (agregado en este entregable) |
| Carlos · Valor y presupuesto | `paginas/carlos.py:28` |
| Clientes prioritarios | `paginas/clientes.py:49` |
| Segmentos | `paginas/segmentos.py:36` |
| Recomendaciones | `paginas/recomendaciones.py:26` (cuando no queda ningún cliente activo) |

**Otros estados detenidos con `st.stop()`:**
- Datos fuera de contrato: `app.py:33` y `src/contexto.py:31`.
- Sin sesión o sin contraseñas configuradas: `src/acceso.py:116` y `:128`.
- Rol sin permiso para la pantalla: `src/acceso.py:143`.
- Actualización sin archivo: `paginas/actualizacion.py:105`.

Comparativa y predicción no usa los filtros, porque evalúa los modelos con el test completo.

**Cómo se verifica:** [`tests/test_estado_vacio.py`](../tests/test_estado_vacio.py) abre cada una de las 7 pantallas con una selección de 0 clientes y comprueba dos cosas: que aparece el aviso y que no se dibuja lo que va después del `st.stop()`.

## 5. Los dos controles y la decisión que habilita cada uno

El objetivo de negocio del README dice: *«A qué clientes activos dirigir la campaña de retención, y en qué país empezar»*. Cada control responde una mitad de esa frase.

| Control | Dónde | Decisión que habilita | Filtro activo visible | Conteo visible |
|---|---|---|---|---|
| **País** (`st.multiselect`, `key="f_pais"`) | Panel derecho, `src/filtros.py:33` | **En qué país empezar** la campaña: Andrea compara el abandono y los activos en riesgo de cada país antes de asignarla | Etiqueta cian en el filtro y la línea «País: UK · 7,534 clientes en este grupo» en *Peso de este grupo en el problema* (`src/seccion_grupo.py:50`) | Subtítulo de cada pantalla: «7,534 de 50,000 clientes en el grupo seleccionado» |
| **Criterios de riesgo: llamadas ≥** (`st.slider`, `key="r_llamadas"`, junto con carrito abandonado >) | Panel derecho → «Criterios de riesgo», `src/filtros.py:39` | **A qué clientes activos dirigir la campaña**: define quién entra al perfil de riesgo. Subir el umbral achica la lista a los casos más graves; bajarlo amplía la campaña | La nota «Se usan los mismos criterios de riesgo para todos: carrito abandonado mayor a 71.25% y 6 o más llamadas» se actualiza con el valor elegido | KPI «Activos en perfil de riesgo»: «2,401 de 35,550 activos» |

**Botón «Limpiar filtros»:** regresa los dos controles a su estado oficial (todos los países, carrito > 71.25 % y 6 o más llamadas).

**Prueba:** `test_filtros_regla_y_limpieza` en `tests/test_dashboard.py` cambia el país a UK y el umbral de carrito, y comprueba tres cosas: el conteo «7,534 de 50,000 clientes», el nuevo número de activos en riesgo y el regreso al estado inicial.

## 6. La matriz de acceso por rol y su limitación

### Mecanismo

1. Antes de mostrar cualquier pantalla, [`src/acceso.py`](../src/acceso.py) pide el **rol** y su **contraseña**.
2. La contraseña se compara con `hmac.compare_digest`, que tarda lo mismo acierte o no y así no revela cuántos caracteres coinciden, contra `st.secrets["acceso"][rol]`. Las contraseñas viven en los Secrets de Streamlit Cloud y **nunca en el repositorio**: `.streamlit/secrets.toml` está en `.gitignore` y solo se sube [`secrets.toml.example`](../.streamlit/secrets.toml.example) con valores de muestra.
3. Con el rol validado, `app.py` registra en `st.navigation()` **solo las pantallas de ese rol**. Las demás no aparecen en el menú y tampoco se pueden abrir escribiendo su URL.
4. **Segunda barrera:** cada pantalla empieza con `acceso.exigir("paginas/…")`, que detiene la ejecución si el rol no la tiene.
5. **Dentro de una pantalla compartida,** `acceso.puede("ver_clientes")` decide si se muestra la lista de clientes.

### Cómo decidimos qué ve cada persona

Para cada pantalla nos hicimos dos preguntas:
1. **¿Qué tipo de dato muestra?**
   - **Agregado:** tasas, conteos, métricas.
   - **Individual:** el ID de un cliente con su probabilidad, su comportamiento o la explicación de su riesgo.
   - **Escritura:** cargar datos o cambiar el modelo.
2. **¿Qué decisión de cuál persona necesita ese dato?**

La regla que salió: **cada persona ve lo que su decisión necesita y nada más**, es decir, mínimo privilegio. Los datos individuales y la escritura quedan solo con quien ejecuta la campaña y mantiene los datos.

| Persona (rol) | Su decisión | Qué tipo de dato necesita |
|---|---|---|
| **Andrea López**, gerente de retención (rol *Gerencia*) | A qué segmentos y países dirigir la campaña y qué tan urgente es | Agregados: tasas por segmento y país, perfil de riesgo, meta |
| **Carlos Mendoza**, estrategia y valor del cliente (rol *Gerencia*) | Si se van los clientes valiosos y dónde invertir | Agregados: abandono por cuartil de valor y por país, escenario |
| **Luis Ramírez**, operaciones de datos y CRM (rol *Operaciones*) | Si hay alertas, si los datos son confiables y quién entra a la lista de campaña | Individuales (lista con ID para el CRM) y escritura (actualizar datos y modelo) |
| **Equipo de desarrollo** (rol *Equipo*) | Mantener y probar el tablero | Todo; lo usan las pruebas automáticas |

Andrea y Carlos comparten rol porque los dos deciden con agregados y ninguno necesita datos individuales. Si en el futuro hiciera falta separarlos, basta con agregar un rol a la matriz.

### Matriz de acceso

| Pantalla | Tipo de dato | Gerencia (Andrea, Carlos) | Operaciones (Luis) | Equipo | Justificación |
|---|---|:---:|:---:|:---:|---|
| Resumen general | Agregado | ✅ | ✅ | ✅ | Todos necesitan la situación general antes de decidir. La tabla de pantallas solo lista las que cada rol puede abrir |
| Andrea · Priorizar campañas | Agregado | ✅ | — | ✅ | Es la decisión de Andrea: segmento, país y urgencia. Luis no decide la campaña, la ejecuta |
| Carlos · Valor y presupuesto | Agregado | ✅ | — | ✅ | Decisión de inversión de Carlos; Operaciones no asigna presupuesto |
| Luis · Monitoreo y calidad | Individual (lista de clientes con ID y descarga) | — | ✅ | ✅ | La lista para el CRM y la calidad de datos son responsabilidad de Luis. Gerencia no necesita el ID de cada cliente para decidir |
| Clientes prioritarios | Individual (probabilidad y explicación por cliente, lista descargable) | — | ✅ | ✅ | Cada fila es un cliente identificable. Andrea fija los criterios (segmento, país, nivel) en sus pantallas; Luis arma la lista con esos criterios |
| Segmentos: gráficas | Agregado | ✅ | ✅ | ✅ | Andrea y Carlos eligen el segmento a atacar |
| Segmentos: lista de clientes del segmento | Individual | — (ve un aviso) | ✅ | ✅ | La misma pantalla muestra contenidos distintos por rol. Es la **rebanada funcional** que se demuestra en vivo |
| Comparativa y predicción | Agregado (métricas) y valores que escribe el usuario | ✅ | ✅ | ✅ | No contiene datos de clientes de la base. Gerencia necesita saber si el modelo es confiable antes de invertir |
| Recomendaciones | Agregado | ✅ | ✅ | ✅ | Plan de acción compartido |
| Asistente de retención (IA) | Individual (sus herramientas regresan clientes con su ID) | — | ✅ | ✅ | Abrírselo a Gerencia sería una puerta trasera a los datos que la matriz le niega |
| Actualización de datos y del modelo | Escritura | — | ✅ | ✅ | Solo quien mantiene los datos puede cargar un archivo nuevo o reentrenar |

### Demostración en vivo

1. Entrar como **Gerencia**. El menú muestra Andrea y Carlos, pero no Luis, Clientes prioritarios, el Asistente ni Datos. En **Segmentos** aparece el aviso «La lista de clientes… solo la ve el rol Operaciones».
2. **Cerrar sesión** y entrar como **Operaciones**. El menú muestra Luis, Clientes prioritarios y Datos, pero no Andrea ni Carlos. En **Segmentos**, en el lugar del aviso, aparecen la lista y el botón de descarga.

Las pruebas de [`tests/test_acceso.py`](../tests/test_acceso.py) comprueban seis cosas:
- que sin sesión no se ve ninguna pantalla;
- que sin Secrets la app no abre;
- que una contraseña equivocada, o la de otro rol, no entra;
- que la pantalla de Luis no está registrada para Gerencia;
- que la barrera de pantalla detiene a otro rol;
- que la lista de Segmentos solo aparece para Operaciones.

### Limitación

- **No identifica a la persona.** Es una **contraseña compartida por rol**, no una cuenta individual: no sabemos cuál de las personas que comparten la contraseña de Gerencia entró.
- **No hay registro de accesos** ni bloqueo por intentos fallidos.
- **Si la contraseña se filtra,** cualquiera entra con ese rol hasta que alguien la cambie a mano en Secrets. Cambiarla obliga a avisar a todos los del rol.
- **El rol vive en `st.session_state`:** dura lo que dura la pestaña del navegador y se pierde al recargar.
- **El rol *Equipo* lo ve todo.** Existe para las pruebas y para mantener el tablero; su contraseña no debería compartirse fuera del equipo.
- **Para producción** se usaría `st.login()` con un proveedor de identidad (OIDC, por ejemplo Google o Microsoft), con cuentas individuales y el rol asignado en el proveedor. Ese mecanismo sí registra quién entró y permite quitarle el acceso a una sola persona.
