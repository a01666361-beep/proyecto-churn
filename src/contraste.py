"""
Contraste de la paleta según WCAG 2.2 AA (entregable 3).

El CI llama a `revisar()` desde tests/test_contraste.py: si un cambio de color
baja la legibilidad, la prueba falla y GitHub Actions marca la corrida en rojo.

Mínimos de WCAG 2.2 AA:
- 4.5:1 texto normal (criterio 1.4.3).
- 3:1 texto grande, es decir 24 px o más, o 18.66 px en negritas (criterio 1.4.3).
- 3:1 elementos no textuales: barras, líneas, bordes de estado, íconos (criterio 1.4.11).

Cada par dice dónde se usa en el dashboard, para que el número tenga sentido.
"""
import re

from src.config import (CARPETA_PROYECTO, AZUL_BOTON, AZUL_BOTON_HOVER, AZUL_DATOS, AZUL_SUAVE, AZUL_TEXTO, BLANCO, CIAN,
                        FONDO, GRIS_TEXTO, NARANJA, PALETA, TARJETA)

MINIMOS = {"texto": 4.5, "texto grande": 3.0, "no textual": 3.0}


def _canal(valor):
    valor = valor / 255
    return valor / 12.92 if valor <= 0.04045 else ((valor + 0.055) / 1.055) ** 2.4


def _rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(color):
    """Luminancia relativa de un color #RRGGBB (fórmula de WCAG)."""
    r, g, b = (_canal(c) for c in _rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razon(color_a, color_b):
    """Razón de contraste entre dos colores, de 1:1 a 21:1."""
    claro, oscuro = sorted((luminancia(color_a), luminancia(color_b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def mezclar(color, opacidad, fondo):
    """Color que se ve al poner `color` con esa opacidad sobre `fondo` (para los chips con rgba)."""
    frente, atras = _rgb(color), _rgb(fondo)
    return "#" + "".join(f"{round(f * opacidad + a * (1 - opacidad)):02X}" for f, a in zip(frente, atras))


# (color del frente, color de fondo, tipo, dónde se usa)
PARES = [
    # Texto normal: 4.5:1
    (BLANCO, FONDO, "texto", "Texto principal sobre el fondo"),
    (BLANCO, TARJETA, "texto", "Texto principal dentro de tarjetas y KPI"),
    (GRIS_TEXTO, FONDO, "texto", "Subtítulos, ayudas y notas sobre el fondo"),
    (GRIS_TEXTO, TARJETA, "texto", "Texto secundario dentro de tarjetas"),
    (AZUL_TEXTO, FONDO, "texto", "Ligas y pestaña activa"),
    (AZUL_TEXTO, TARJETA, "texto", "Texto azul pequeño dentro de tarjetas"),
    (NARANJA, FONDO, "texto", "Mensajes de alerta sobre el fondo"),
    (NARANJA, TARJETA, "texto", "Alertas dentro de tarjetas"),
    (CIAN, FONDO, "texto", "Título del panel de filtros"),
    (FONDO, CIAN, "texto", "Texto oscuro de un filtro activo (etiqueta cian)"),
    (BLANCO, AZUL_BOTON, "texto", "Texto de los botones principales"),
    (BLANCO, AZUL_BOTON_HOVER, "texto", "Botón principal al pasar el cursor"),
    # Texto grande: 3:1 (los valores de los KPI miden más de 24 px)
    (AZUL_DATOS, TARJETA, "texto grande", "Valor grande de los KPI y de st.metric"),
    (AZUL_DATOS, FONDO, "texto grande", "Números grandes sobre el fondo"),
    # Elementos no textuales: 3:1 (las gráficas tienen fondo transparente: se ven sobre FONDO o TARJETA)
    (AZUL_DATOS, FONDO, "no textual", "Barras principales de las gráficas"),
    (AZUL_DATOS, TARJETA, "no textual", "Barra de proporción del grupo en tarjetas"),
    (AZUL_SUAVE, FONDO, "no textual", "Barras «por debajo del promedio»"),
    (AZUL_SUAVE, TARJETA, "no textual", "Barras «por debajo del promedio» sobre tarjeta"),
    (NARANJA, FONDO, "no textual", "Barras y marcas de alerta"),
    (NARANJA, TARJETA, "no textual", "Borde de KPI en alerta"),
    (CIAN, FONDO, "no textual", "Barras favorables y controles activos"),
    (CIAN, TARJETA, "no textual", "Borde de KPI favorable"),
    (GRIS_TEXTO, FONDO, "no textual", "Series neutras de las gráficas"),
    (AZUL_BOTON, FONDO, "no textual", "Contorno del botón principal"),
] + [(color, FONDO, "no textual", f"Serie {i} de las gráficas con varias series")
     for i, color in enumerate(PALETA, 1)]


def _variables_css(css):
    return {n: v.upper() for n, v in re.findall(r"--(cp-[\w-]+):\s*(#[0-9A-Fa-f]{6})", css)}


def pares_chips(css=None):
    """Lee las reglas .chip-* del CSS y calcula su texto contra el fondo translúcido sobre una tarjeta."""
    if css is None:
        css = (CARPETA_PROYECTO / "src" / "estilos.py").read_text(encoding="utf-8")
    variables = _variables_css(css)
    patron = (r"\.(chip-[\w-]+)\s*\{background:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\);"
              r"\s*color:\s*var\(--(cp-[\w-]+)\);\}")
    pares = []
    for clase, r, g, b, alfa, variable in re.findall(patron, css):
        relleno = f"#{int(r):02X}{int(g):02X}{int(b):02X}"
        pares.append((variables[variable], mezclar(relleno, float(alfa), TARJETA), "texto",
                      f"Chip .{clase} dentro de una tarjeta"))
    return pares


def revisar(pares=None):
    """Regresa una fila por par con su razón y si cumple el mínimo de WCAG 2.2 AA."""
    if pares is None:
        pares = PARES + pares_chips()
    filas = []
    for frente, fondo, tipo, uso in pares:
        valor = razon(frente, fondo)
        filas.append({"frente": frente, "fondo": fondo, "tipo": tipo, "uso": uso,
                      "razon": round(valor, 2), "minimo": MINIMOS[tipo], "cumple": valor >= MINIMOS[tipo]})
    return filas


if __name__ == "__main__":  # python -m src.contraste  → tabla para docs/entregable-3.md
    print("| Uso | Frente | Fondo | Tipo | Razón | Mínimo | Cumple |")
    print("|---|---|---|---|---|---|---|")
    for f in revisar():
        print(f"| {f['uso']} | `{f['frente']}` | `{f['fondo']}` | {f['tipo']} | {f['razon']}:1 | "
              f"{f['minimo']}:1 | {'✅' if f['cumple'] else '❌'} |")
