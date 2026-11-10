"""Regresión de datos y de las tres pantallas. Ejecutar: python -m unittest discover -s tests."""
import unittest

from streamlit.testing.v1 import AppTest

from src.config import CARPETA_PROYECTO, REGLA_DEFAULT, RUTA_DATOS
from src.graficas import separar_panel
from src.indicadores import resumen_riesgo
from src.limpieza import cargar_datos
from src.seccion_factores import figura_factores
from src.seccion_riesgo import figura_riesgo
from src import resumen, vistas


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
        a.switch_page("paginas/andrea.py").run(timeout=90)
        self.assertFalse(a.exception)
        for valor in ["35,550", "28.9%", "2,401"]:
            self.assertIn(valor, self.contenido(a))
        a.multiselect(key="f_pais").set_value(["UK"]).run(timeout=90)
        self.assertFalse(a.exception)
        self.assertIn("7,534 de 50,000 clientes", " ".join(c.value for c in a.caption))
        a.slider(key="r_carrito").set_value(80.0).run(timeout=90)
        self.assertFalse(a.exception)
        uk = self.df[self.df.Country == "UK"]
        total = resumen_riesgo(uk, {"carrito_min": 80., "llamadas_min": 6})["activos_en_perfil"]
        self.assertIn(f"{total:,}", self.contenido(a))
        next(b for b in a.button if b.label == "Limpiar filtros").click().run(timeout=90)
        self.assertFalse(a.exception)
        self.assertEqual(a.multiselect(key="f_pais").value, [])
        self.assertEqual(a.slider(key="r_carrito").value, 71.25)
        self.assertIn("35,550", self.contenido(a))

    def test_tres_pantallas_abren(self):
        a = self.app()
        self.assertIn("Situación actual", self.contenido(a))  # abre en el resumen general
        for pagina, texto in [("paginas/andrea.py", "Tasa de abandono"), ("paginas/luis.py", "No informada"),
                              ("paginas/carlos.py", "No calculable"),
                              ("paginas/recomendaciones.py", "Cómo medirlo")]:
            with self.subTest(pagina=pagina):
                a.switch_page(pagina).run(timeout=90)
                self.assertFalse(a.exception, [e.message for e in a.exception])
                valores = [m.value for m in a.metric] + [self.contenido(a)]
                self.assertTrue(any(texto in v for v in valores))

    def test_filtros_se_conservan_al_cambiar_de_pantalla(self):
        a = self.app()
        a.multiselect(key="f_pais").set_value(["UK"]).run(timeout=90)
        a.switch_page("paginas/carlos.py").run(timeout=90)
        self.assertFalse(a.exception)
        self.assertEqual(a.multiselect(key="f_pais").value, ["UK"])
        self.assertIn("7,534", " ".join(m.value for m in a.metric))

    def test_resumen_y_recomendaciones(self):
        f = resumen.factores(self.df, REGLA_DEFAULT)
        self.assertEqual(f["perfil"]["activos"], 2401)
        self.assertAlmostEqual(f["perfil"]["tasa_dentro"], resumen_riesgo(self.df, REGLA_DEFAULT)["tasa_historica"])
        self.assertEqual(resumen.segmento_critico(self.df)["segmento"], "18–29")
        lista = resumen.recomendaciones(self.df, self.df, REGLA_DEFAULT)
        self.assertEqual(lista[0]["a_quien"], 2401)
        self.assertEqual(resumen.recomendaciones(self.df.iloc[0:0], self.df, REGLA_DEFAULT), [])

    def test_kpi_sin_tarjeta_de_clientes(self):
        a = self.app()
        a.switch_page("paginas/andrea.py").run(timeout=90)
        self.assertNotIn("Clientes activos</div>", self.contenido(a))

    def test_calculos_de_las_pantallas(self):
        self.assertEqual(vistas.calidad_datos(self.df)["duplicados"], 0)
        edad = vistas.churn_por_segmento(self.df, "Edad")
        self.assertEqual(edad.iloc[0]["segmento"], "18–29")
        self.assertTrue((vistas.churn_por_segmento(self.df, "Ciudad")["clientes"] >= 30).all())
        self.assertEqual(len(vistas.tabla_clientes(self.df, REGLA_DEFAULT)), 2401)
        cuartiles = vistas.cuartiles_ltv(self.df, self.df)
        self.assertEqual(cuartiles["clientes"].sum(), 50000)
        self.assertAlmostEqual(cuartiles.iloc[-1]["tasa"], 4953 / 12496)
        self.assertEqual(vistas.escenario(50000, 1.0), 500)
        estados = [x["encendida"] for x in vistas.alertas(.289, .289, resumen_riesgo(self.df, REGLA_DEFAULT),
                                                           vistas.calidad_datos(self.df))]
        self.assertEqual(estados, [False, True, False])


if __name__ == "__main__":
    unittest.main()
