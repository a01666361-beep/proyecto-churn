"""Cada gráfica del dashboard declara por escrito la pregunta que responde (entregable 3).

Se revisa el código sin abrir la app:
- Toda llamada a ayuda.titulo_grafica() trae `pregunta=` escrita como pregunta (¿...?).
- Todo st.plotly_chart() de las pantallas tiene antes un titulo_grafica() que lo presenta.
  Si una gráfica no tiene pregunta, la prueba falla: o se le escribe una, o se quita.
"""
import ast
import unittest

from src.config import CARPETA_PROYECTO

# Archivos que dibujan gráficas en la app (las pantallas y la ventana "Todas las variables")
ARCHIVOS = sorted((CARPETA_PROYECTO / "paginas").glob("*.py")) + [CARPETA_PROYECTO / "src" / "ventanas.py"]


def _llamadas(arbol, nombre):
    return sorted((n for n in ast.walk(arbol) if isinstance(n, ast.Call)
                   and getattr(n.func, "attr", getattr(n.func, "id", None)) == nombre), key=lambda n: n.lineno)


def _texto(nodo):
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str):
        return nodo.value
    if isinstance(nodo, ast.JoinedStr):  # f-string: se revisa el texto fijo
        return "".join(p.value for p in nodo.values if isinstance(p, ast.Constant))
    return None


def preguntas():
    """(archivo, línea, pregunta) de todas las gráficas. También sirve para armar docs/entregable-3.md."""
    filas = []
    for archivo in ARCHIVOS:
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for llamada in _llamadas(arbol, "titulo_grafica"):
            pregunta = next((k.value for k in llamada.keywords if k.arg == "pregunta"), None)
            filas.append((archivo.relative_to(CARPETA_PROYECTO).as_posix(), llamada.lineno,
                          _texto(pregunta) if pregunta is not None else None))
    return filas


class PreguntasDeLasGraficas(unittest.TestCase):
    def test_cada_titulo_tiene_su_pregunta(self):
        filas = preguntas()
        self.assertGreater(len(filas), 10)
        for archivo, linea, pregunta in filas:
            with self.subTest(archivo=archivo, linea=linea):
                self.assertIsNotNone(pregunta, "titulo_grafica() sin pregunta=")
                self.assertTrue(pregunta.startswith("¿") and pregunta.endswith("?"), pregunta)
                self.assertGreater(len(pregunta), 15, "La pregunta debe decir qué se quiere saber")

    def test_preguntas_no_se_repiten(self):
        textos = [p for _, _, p in preguntas()]
        repetidas = {p for p in textos if textos.count(p) > 1}
        self.assertEqual(repetidas, set(), "Dos gráficas con la misma pregunta: sobra una")

    def test_cada_grafica_tiene_titulo_con_pregunta_antes(self):
        for archivo in ARCHIVOS:
            arbol = ast.parse(archivo.read_text(encoding="utf-8"))
            titulos = [n.lineno for n in _llamadas(arbol, "titulo_grafica")]
            for grafica in _llamadas(arbol, "plotly_chart"):
                with self.subTest(archivo=archivo.name, linea=grafica.lineno):
                    self.assertTrue(any(t < grafica.lineno for t in titulos),
                                    "st.plotly_chart() sin titulo_grafica(pregunta=...) antes")


if __name__ == "__main__":
    unittest.main()
