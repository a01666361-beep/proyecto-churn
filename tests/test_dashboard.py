"""Regresión de datos y navegación del dashboard. Ejecutar: python -m unittest discover -s tests."""
import unittest

from streamlit.testing.v1 import AppTest

from src.config import CARPETA_PROYECTO, REGLA_DEFAULT, RUTA_DATOS
from src.graficas import separar_panel
from src.indicadores import resumen_riesgo
from src.limpieza import cargar_datos
from src.seccion_factores import figura_factores
from src.seccion_riesgo import figura_riesgo


class DashboardRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = cargar_datos(RUTA_DATOS)

    def app(self):
        app = AppTest.from_file(str(CARPETA_PROYECTO / "app.py")).run(timeout=90)
        self.assertFalse(app.exception, [e.message for e in app.exception])
        return app

    def contenido(self, app):
        return " ".join(m.value for m in app.markdown if "<style>" not in m.value)

    def test_paneles_conservan_datos_y_referencias(self):
        originales = [figura_factores(self.df, .289), figura_riesgo(self.df, REGLA_DEFAULT)]
        self.assertNotEqual(originales[0].data[1].x, originales[0].data[2].x)
        for original, numero in [(originales[0], 1), (originales[0], 2),
                                 (originales[0], 3), (originales[1], 1), (originales[1], 2)]:
            separado = separar_panel(original, numero)
            eje = "x" if numero == 1 else f"x{numero}"
            trazas = [t for t in original.data if (t.xaxis or "x") == eje]
            self.assertEqual(len(trazas), len(separado.data))
            for antes, despues in zip(trazas, separado.data):
                # Solo deben cambiar las referencias a los ejes del panel.
                datos = antes.to_plotly_json()
                datos.update(xaxis="x", yaxis="y")
                import plotly.graph_objects as go
                self.assertEqual(go.Figure(data=[datos]).to_json(), go.Figure(data=[despues]).to_json())
        self.assertEqual(len(separar_panel(originales[0], 1).layout.shapes), 1)
        self.assertEqual(len(separar_panel(originales[0], 3).layout.shapes), 1)
        self.assertEqual(len(separar_panel(originales[1], 2).layout.shapes), 1)

    def test_filtros_regla_y_limpieza(self):
        a = self.app()
        self.assertIn("35,550", self.contenido(a))
        self.assertIn("28.9%", self.contenido(a))
        self.assertIn("2,401", self.contenido(a))
        a.multiselect(key="f_pais").set_value(["UK"]).run(timeout=90)
        self.assertFalse(a.exception)
        texto = self.contenido(a)
        for valor in ["5,365", "2,169", "396", "15.0%", "16.5%", "▲ 0.6 pts"]:
            self.assertIn(valor, texto)
        genero = a.multiselect(key="f_genero").options[0]
        edad = a.multiselect(key="f_edad").options[0]
        a.multiselect(key="f_genero").set_value([genero])
        a.multiselect(key="f_edad").set_value([edad]).run(timeout=90)
        self.assertFalse(a.exception)
        esperado = self.df[(self.df.Country == "UK") & (self.df.Gender == genero) & (self.df.Grupo_Edad == edad)]
        self.assertIn(f"{len(esperado):,} clientes en este grupo", self.contenido(a))
        a.slider(key="r_carrito").set_value(80.0).run(timeout=90)
        self.assertFalse(a.exception)
        total = resumen_riesgo(self.df, {"carrito_min": 80., "llamadas_min": 6})["activos_en_perfil"]
        self.assertIn(f"{total:,}", self.contenido(a))
        next(b for b in a.button if b.label == "Limpiar filtros").click().run(timeout=90)
        self.assertFalse(a.exception)
        self.assertEqual(a.multiselect(key="f_pais").value, [])
        self.assertEqual(a.slider(key="r_carrito").value, 71.25)
        self.assertIn("35,550", self.contenido(a))

    def test_ventanas_y_descarga(self):
        for nombre, contenido in [("Todas las variables", "Variable"),
                                  ("Definiciones", "Tasa de abandono"), ("Datos", "Descargar CSV")]:
            with self.subTest(ventana=nombre):
                a = self.app()
                next(b for b in a.button if b.label == nombre).click().run(timeout=90)
                self.assertFalse(a.exception, [e.message for e in a.exception])
                self.assertTrue(a.get("dialog"))
                if nombre == "Datos":
                    self.assertEqual(len(a.dataframe[0].value), 50000)
                    self.assertTrue(a.get("download_button"))
                elif nombre == "Todas las variables":
                    self.assertTrue(a.selectbox)
                else:
                    self.assertIn(contenido, self.contenido(a))


if __name__ == "__main__":
    unittest.main()
