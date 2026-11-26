# Investigación 3 · Legibilidad verificable y acceso por rol

Equipo 5 · Entregable 3

En el entregable 2 el tablero ya tenía buena calidad, pero dependía de que alguien revisara a ojo dos cosas: si los colores se leían y si cada persona veía lo que le correspondía. Esta investigación revisa cómo convertir esas dos revisiones en mecanismos que se comprueban solos, y cómo aplicamos cada idea en el repositorio.

## 1. Contraste: un número, no una opinión

WCAG 2.2 define el contraste como una razón entre la luminancia relativa de dos colores, (L₁ + 0.05) / (L₂ + 0.05), que va de 1:1 (mismo color) a 21:1 (negro sobre blanco). El nivel AA pide:

- **1.4.3 Contraste mínimo:** 4.5:1 para texto normal y 3:1 para texto grande (24 px, o 18.66 px en negritas).
- **1.4.11 Contraste no textual:** 3:1 para las partes de una gráfica que se necesitan para entenderla (barras, líneas, bordes de estado) y para los controles.
- **1.4.1 Uso del color:** el color no puede ser el único medio para transmitir información.

**Qué aprendimos al aplicarlo:**
1. El cálculo encontró fallas que a simple vista no se notaban:
   - el texto blanco sobre los botones azules daba 3.98:1;
   - el azul suave de las barras daba 2.34:1 sobre las tarjetas;
   - tres tipos de chip con fondo translúcido quedaban entre 3.92:1 y 4.46:1.
2. Un color translúcido (`rgba`) no tiene un contraste fijo, porque depende del fondo que tiene debajo. Para medirlo hay que mezclarlo primero con ese fondo.
3. Revisar solo la paleta no basta. También hay que revisar **dónde** se usa cada color: el gris de bordes (`#343B4A`, 1.5:1) estaba dibujando una serie de datos («riesgo bajo»).

**Cómo lo aplicamos:**
- [`src/contraste.py`](../src/contraste.py) calcula cada par de colores con su uso.
- [`tests/test_contraste.py`](../tests/test_contraste.py) falla si un par no llega al mínimo, si el tema o el CSS se desalinean de `src/config.py`, o si el gris de bordes se usa para datos.
- El workflow de GitHub Actions tiene un paso propio para esta revisión.

Así, la decisión no depende del criterio de nadie el día de la defensa: si un cambio baja la legibilidad, el CI queda en rojo.

## 2. Daltonismo: dos canales para cada dato

**Por qué azul contra naranja:** la deficiencia más común confunde el rojo con el verde (deuteranopía y protanopía), así que una paleta que separa «bueno» y «malo» con rojo y verde falla justo donde más importa. La pareja azul–naranja se distingue en esos casos.

**Pero el color solo no basta** (criterio 1.4.1). Por eso cada dato tiene un segundo canal:
- un porcentaje escrito en la barra;
- una flecha ▲ / ▼ en los chips;
- una etiqueta en las líneas de referencia;
- el valor dentro de cada celda de los mapas de calor.

## 3. Una gráfica, una pregunta

Si una gráfica no responde una pregunta, no habilita ninguna decisión: solo ocupa espacio y compite por la atención. Aplicamos dos cosas:

- **La pregunta es obligatoria en el código.** `titulo_grafica()` no funciona sin `pregunta=`, y [`tests/test_preguntas_graficas.py`](../tests/test_preguntas_graficas.py) rechaza preguntas repetidas o gráficas sin título.
- **Las gráficas sin decisión se quitaron.** Al escribir las preguntas, las de validación técnica del clustering solo tenían preguntas de método («¿cuántos clusters?»). Se quitaron del tablero y siguen en el notebook.

## 4. Estado vacío: detener antes de calcular

En Streamlit el script se ejecuta completo de arriba abajo en cada interacción. `st.stop()` corta esa ejecución en el punto donde se llama.

Si un filtro deja 0 clientes y la pantalla sigue, calcula tasas sobre nada: aparecen divisiones entre cero, gráficas vacías o mensajes de error. Lo correcto es declarar el caso, dar una salida («Limpiar filtros») y detener la pantalla.

[`tests/test_estado_vacio.py`](../tests/test_estado_vacio.py) lo comprueba en las 7 pantallas que usan filtros.

## 5. Autorización: un mecanismo, no un acuerdo en papel

Que el tablero «sea para Andrea» o «sea para Luis» no protege nada si cualquiera puede abrir cualquier pantalla. Revisamos tres opciones:

| Opción | Cómo funciona | Por qué sí o por qué no |
|---|---|---|
| Selector de rol sin contraseña | El usuario elige su rol | No autoriza nada: cualquiera elige el rol que quiera. Es el caso que la consigna descarta («un selector de rol que solo cambia el título») |
| **Contraseña por rol en `st.secrets`** | El rol se valida contra una contraseña guardada en la configuración del host | Funciona en Streamlit Cloud sin servicios externos y deja las contraseñas fuera del repositorio. **Es la que usamos** |
| `st.login()` con un proveedor OIDC | Cada persona entra con su cuenta (Google, Microsoft) y el rol se asigna en el proveedor | Identifica a la persona y deja registro. Es lo recomendable en producción, pero requiere registrar la app con el proveedor |

**Tres prácticas que tomamos:**
1. **Mínimo privilegio:** cada rol recibe solo lo que necesita su decisión. El corte lo hicimos por tipo de dato: los datos agregados son para Gerencia; los individuales y la escritura, para Operaciones.
2. **Ocultar no es proteger.** Además de quitar las pantallas del menú, `st.navigation()` solo registra las del rol, así que tampoco se pueden abrir por URL. Cada pantalla, además, vuelve a revisar el rol (`acceso.exigir`).
3. **Los secretos van en la configuración del host, nunca en el repositorio.** `.streamlit/secrets.toml` está en `.gitignore`.

La matriz completa, su justificación y la limitación del mecanismo están en [`docs/entregable-3.md`](../docs/entregable-3.md), sección 6.

## Fuentes

- W3C. *Web Content Accessibility Guidelines (WCAG) 2.2*. https://www.w3.org/TR/WCAG22/
- W3C WAI. *Understanding SC 1.4.3: Contrast (Minimum)*. https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- W3C WAI. *Understanding SC 1.4.11: Non-text Contrast*. https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
- W3C WAI. *Understanding SC 1.4.1: Use of Color*. https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
- Streamlit. *Secrets management*. https://docs.streamlit.io/develop/concepts/connections/secrets-management
- Streamlit. *User authentication and information* (`st.login`). https://docs.streamlit.io/develop/concepts/connections/authentication
- Streamlit. *st.navigation* y *st.stop*. https://docs.streamlit.io/develop/api-reference/navigation/st.navigation · https://docs.streamlit.io/develop/api-reference/execution-flow/st.stop
