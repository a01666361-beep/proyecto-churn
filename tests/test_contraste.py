"""Contraste WCAG 2.2 AA de la paleta (entregable 3).

Corre en GitHub Actions con el resto de las pruebas. Si alguien cambia un color en
src/config.py, en .streamlit/config.toml o en el CSS de src/estilos.py y baja la
legibilidad, esta prueba falla y la corrida del CI queda en rojo.
"""
import re
import tomllib
import unittest

from src import config, contraste
from src.config import CARPETA_PROYECTO

TEXTO, GRANDE, NO_TEXTUAL = 4.5, 3.0, 3.0


def _tema():
    with open(CARPETA_PROYECTO / ".streamlit" / "config.toml", "rb") as archivo:
        return tomllib.load(archivo)["theme"]


def _variables_css():
    css = (CARPETA_PROYECTO / "src" / "estilos.py").read_text(encoding="utf-8")
    return {nombre: valor.upper() for nombre, valor in re.findall(r"--(cp-[\w-]+):\s*(#[0-9A-Fa-f]{6})", css)}


class FormulaWCAG(unittest.TestCase):
    def test_valores_de_referencia(self):
        self.assertAlmostEqual(contraste.razon("#FFFFFF", "#000000"), 21.0, places=2)
        self.assertAlmostEqual(contraste.razon("#777777", "#777777"), 1.0, places=2)
        # Ejemplo conocido: #767676 sobre blanco es el gris más claro que pasa 4.5:1
        self.assertGreaterEqual(contraste.razon("#767676", "#FFFFFF"), 4.5)
        self.assertLess(contraste.razon("#777777", "#FFFFFF"), 4.5)


class PaletaDelDashboard(unittest.TestCase):
    def test_todos_los_pares_cumplen_wcag_aa(self):
        fallas = [f"{f['uso']}: {f['frente']} sobre {f['fondo']} = {f['razon']}:1 (mínimo {f['minimo']}:1)"
                  for f in contraste.revisar() if not f["cumple"]]
        self.assertEqual(fallas, [], "\n".join(fallas))

    def test_tema_de_streamlit(self):
        tema = _tema()
        fondo, tarjeta = tema["backgroundColor"], tema["secondaryBackgroundColor"]
        self.assertGreaterEqual(contraste.razon(tema["textColor"], fondo), TEXTO)
        self.assertGreaterEqual(contraste.razon(tema["textColor"], tarjeta), TEXTO)
        self.assertGreaterEqual(contraste.razon(tema["linkColor"], fondo), TEXTO)
        self.assertGreaterEqual(contraste.razon("#FFFFFF", tema["primaryColor"]), TEXTO,
                                "texto blanco de los botones principales")
        for clave in ["primaryColor", "redColor", "orangeColor", "greenColor", "blueColor"]:
            with self.subTest(color=clave):
                self.assertGreaterEqual(contraste.razon(tema[clave], fondo), NO_TEXTUAL)
        for color in tema["chartCategoricalColors"]:
            with self.subTest(serie=color):
                self.assertGreaterEqual(contraste.razon(color, fondo), NO_TEXTUAL)

    def test_css_y_config_usan_los_mismos_colores(self):
        """Si el CSS o el tema se desalinean de src/config.py, la prueba de pares ya no los cubriría."""
        css, tema = _variables_css(), _tema()
        esperados = {"cp-fondo": config.FONDO, "cp-tarjeta": config.TARJETA, "cp-azul": config.AZUL_DATOS,
                     "cp-azul-texto": config.AZUL_TEXTO, "cp-naranja": config.NARANJA, "cp-cian": config.CIAN,
                     "cp-texto": config.BLANCO, "cp-texto-suave": config.GRIS_TEXTO,
                     "cp-boton": config.AZUL_BOTON, "cp-boton-hover": config.AZUL_BOTON_HOVER}
        for variable, color in esperados.items():
            with self.subTest(variable=variable):
                self.assertEqual(css.get(variable), color.upper())
        self.assertEqual(tema["backgroundColor"].upper(), config.FONDO.upper())
        self.assertEqual(tema["secondaryBackgroundColor"].upper(), config.TARJETA.upper())
        self.assertEqual(tema["primaryColor"].upper(), config.AZUL_BOTON.upper())

    def test_variables_css_sobre_fondos(self):
        css = _variables_css()
        for texto in ["cp-texto", "cp-texto-suave", "cp-azul-texto", "cp-naranja", "cp-cian"]:
            for fondo in ["cp-fondo", "cp-fondo-2", "cp-tarjeta"]:
                with self.subTest(texto=texto, fondo=fondo):
                    self.assertGreaterEqual(contraste.razon(css[texto], css[fondo]), TEXTO)


class ColoresDecorativos(unittest.TestCase):
    def test_linea_no_se_usa_para_datos(self):
        """LINEA (#343B4A, 1.5:1) es solo para bordes; una barra o serie con ese color no se distingue."""
        archivos = sorted((CARPETA_PROYECTO / "paginas").glob("*.py")) + [CARPETA_PROYECTO / "src" / "ventanas.py"]
        for archivo in archivos:
            with self.subTest(archivo=archivo.name):
                self.assertNotRegex(archivo.read_text(encoding="utf-8"), r"\bLINEA\b")


if __name__ == "__main__":
    unittest.main()
