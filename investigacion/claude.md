# Investigación del ciclo de desarrollo con IA

**Equipo 5 — E-commerce Customer Churn**  
**Entregable 2 | Parte 1: Build y Test**

## Resumen del curso y relación con nuestro proyecto

### ¿En qué etapas ya usamos un asistente y en cuáles no?

El curso de Anthropic, *The AI-native SDLC playbook*, explica que desarrollar una aplicación no consiste solamente en escribir código, sino que incluye seis etapas: **Plan, Design, Build, Test, Deploy y Maintain**. La idea principal es utilizar la IA para apoyar distintas partes del trabajo, pero mantener las decisiones importantes en manos del equipo y comprobar que el resultado funciona. Al revisar nuestros prompts nos dimos cuenta de que hemos utilizado asistentes principalmente para planear, diseñar y construir el dashboard, y que apenas en este entregable empezamos a reforzar las pruebas.

En **Plan** utilizamos Claude para ordenar las tareas que teníamos pendientes, como definir la paleta, acomodar los indicadores y repartir cambios entre compañeros. En **Design** le pedimos reorganizar el dashboard para mostrar primero los indicadores principales y después las gráficas relacionadas, también trabajamos la separación en tres pantallas según lo que necesita Andrea, Luis y Carlos. Estas solicitudes aparecen en `prompts/contrato-prompts.md`, especialmente en los prompts 2, 3 y 8. No seguimos todas las sugerencias de forma automática: revisamos si ayudaban a tomar la decisión de retener clientes y ajustamos lo que no encajaba con la información disponible.

En **Build** sí tenemos varios ejemplos del uso de asistentes para programar. Pedimos ayuda para crear las tarjetas de indicadores, los filtros, las comparaciones y la navegación entre pantallas. Un caso importante fue el cambio de base de datos: Claude propuso una regla de riesgo distinta, pero el equipo mantuvo la que venía de nuestro árbol de decisión, carrito abandonado mayor a 71.25% y seis o más llamadas. También conservamos dos cálculos diferentes, la tasa de abandono sobre todos los clientes y el porcentaje de activos en riesgo solamente sobre los clientes activos. Esto quedó registrado en el primer prompt del historial, por lo que podemos distinguir lo que propuso el asistente de lo que decidimos nosotros.

La etapa **Test** es donde más avanzamos esta semana. Antes ya revisábamos que las pantallas abrieran, pero ahora agregamos un contrato de datos y pruebas para comprobar los tipos de columnas, los valores vacíos, los identificadores duplicados y los números fuera de rango. También dejamos cuatro ejemplos de errores en la pantalla de Luis, que se hacen sobre una copia de los datos para no modificar el archivo original. Con ayuda de ChatGPT preparamos las validaciones y las pruebas, como se describe en `prompts/B2.md`, y comprobamos el resultado con GitHub Actions. Introdujimos un error en `Age` de forma intencional y el sistema lo detectó; después, con los datos correctos, la última ejecución aprobó las 23 pruebas.

En **Deploy** ya publicamos el dashboard en Streamlit y usamos GitHub para integrar los cambios, pero todavía no tenemos una publicación automática controlada por un asistente ni una regla que obligue a aprobar las pruebas antes de fusionar con `main`. En **Maintain** revisamos algunos resultados y corregimos problemas conforme aparecen, aunque no existe un seguimiento automático que mida si las recomendaciones del dashboard realmente ayudan a reducir el abandono. Por eso consideramos que estas dos etapas todavía pueden mejorar. Tener la aplicación publicada no significa que ya tengamos resuelto todo el proceso de publicación y mantenimiento que explica el curso.

### ¿Qué práctica concreta podríamos adoptar esta semana?

La lección de **Test** propone darle al asistente una forma de revisar su propio trabajo, por ejemplo mediante un comando que ejecute las pruebas y muestre claramente si algo falló. También recomienda que, cuando se corrige un error, primero se reproduzca con una prueba que falle y después se cambie el código sin modificar la prueba solamente para obtener un resultado positivo. Nos parece útil porque en un dashboard es fácil cambiar una gráfica o una limpieza de datos y afectar otras pantallas sin darse cuenta.

Ya empezamos a aplicar una parte de esta práctica: en `CLAUDE.md` dejamos escrito que se deben ejecutar las pruebas antes de dar por terminado un cambio, y en `.github/workflows/validacion-datos.yml` configuramos su ejecución al abrir solicitudes de cambio y al actualizar `main`. La prueba con `ERROR_DEMO` mostró que el control realmente puede detectar un archivo incorrecto. El siguiente paso sería escribir primero el caso que queremos comprobar cada vez que aparezca un problema nuevo, conservar esa prueba y exigir que pase antes de aprobar el cambio. Es importante aclarar que nuestras 23 pruebas revisan el código y los datos; todavía **no** tenemos las evaluaciones automáticas del comportamiento del asistente que el curso también propone.

### ¿Qué esperábamos encontrar y no estaba en el curso?

Al revisar la etapa de pruebas esperábamos encontrar un ejemplo más cercano a un dashboard que trabaja con un CSV, sobre todo cómo decidir qué hacer con valores vacíos, unidades desconocidas o números que parecen incorrectos. El curso explica muy bien cómo organizar las revisiones y cómo comprobar lo que genera un asistente, pero no indica qué significado debe tener cada dato de un negocio. Eso nos hizo notar que una prueba automática puede confirmar que una columna es numérica sin asegurar que el número tiene sentido.

En nuestra base, por ejemplo, hay valores fraccionarios en `Customer_Service_Calls`, aunque la variable se presenta como cantidad de llamadas. El programa puede leerlos, pero no tenemos información suficiente para afirmar por qué son fraccionarios. Por eso decidimos conservarlos y mostrar una advertencia en vez de redondearlos o inventar una explicación. El aprendizaje fue que **el asistente puede ayudar a programar una regla, pero el equipo debe decidir qué regla es correcta** y documentar los casos en los que todavía existen dudas.

## Tres cambios en nuestra forma de trabajar

| Qué cambiamos | Dónde lo ponemos | Por qué ahí |
|---|---|---|
| Revisar automáticamente el tipo de las columnas, los datos faltantes y los valores fuera de rango en cada cambio | **Dentro del pipeline**, en `.github/workflows/validacion-datos.yml` y las pruebas de `tests/` | Para detectar un CSV incorrecto antes de usarlo en las gráficas, sin depender de que alguien recuerde hacer la revisión manual |
| Anotar las reglas del negocio, las unidades que conocemos y lo que todavía necesita una decisión del equipo antes de pedir cambios a la IA | **Fuera del pipeline**, en `CLAUDE.md` y `contrato-datos.md`, con revisión del equipo | Porque una prueba puede revisar formatos, pero no decidir por nosotros qué significa un valor vacío o cuál debe ser la meta |
| Exigir la aprobación de las pruebas antes de integrar un cambio a `main` | **En GitHub**, mediante una regla de protección de la rama y la revisión del *pull request* | Para que una ejecución fallida no sea solo una advertencia, sino que impida integrar un cambio incorrecto, esta protección todavía debe configurarse |

## Fuentes y evidencia del equipo

- Anthropic, [*The AI-native SDLC playbook — Introducción*](https://academy.claude.com/courses/ai-native-sdlc-playbook/introduction).
- Anthropic, [*Give Claude a feedback loop*](https://academy.claude.com/courses/ai-native-sdlc-playbook/give-claude-a-feedback-loop).
- Anthropic, [*Continuous evals in CI*](https://academy.claude.com/courses/ai-native-sdlc-playbook/continuous-evals-in-ci).
- Prompts reales del proyecto: [`prompts/contrato-prompts.md`](../prompts/contrato-prompts.md) y [`prompts/B2.md`](../prompts/B2.md).
- Evidencia del fallo intencional: [GitHub Actions, 12 de noviembre](https://github.com/a01666361-beep/proyecto-churn/actions/runs/43277557193).
- Comprobación posterior con datos correctos: [Última ejecución de GitHub Actions, 23 pruebas aprobadas](https://github.com/a01666361-beep/proyecto-churn/actions/runs/43351872460).
