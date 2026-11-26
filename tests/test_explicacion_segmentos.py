"""Pruebas de la explicación por cliente y de la pantalla 06 · Segmentos (Víctor García, A01784206).
Ejecutar: python -m unittest discover -s tests -v"""
import unittest

import numpy as np
from streamlit.testing.v1 import AppTest

from src import modelo as M
from src.config import CARPETA_PROYECTO, RUTA_DATOS
from src.limpieza import cargar_datos


class ExplicacionCliente(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = cargar_datos(RUTA_DATOS)
        cls.modelo = M.entrenar_modelo(cls.df)["modelo"]
        cls.puntuado = M.puntuar(cls.df, cls.modelo)

    def test_aportes_reproducen_la_probabilidad_del_modelo(self):
        # La explicación debe cuadrar exacto con la probabilidad que muestra la tabla del scoring.
        for cliente in self.puntuado.sort_values("Probabilidad")["Customer_ID"].iloc[[0, 2500, -1]]:
            tabla, base = M.explicar_cliente(self.modelo, self.df, cliente, n=50)
            esperado = self.puntuado.loc[self.puntuado.Customer_ID == cliente, "Probabilidad"].iloc[0]
            self.assertAlmostEqual(base["probabilidad"], esperado, places=6)
            self.assertAlmostEqual(base["logit_promedio"] + base["suma_aportes"], base["logit"], places=6)
            # Con todas las variables, la suma de la tabla es la suma total de aportes.
            self.assertAlmostEqual(tabla["Aporte"].sum(), base["suma_aportes"], places=6)

    def test_ordena_por_peso_y_agrupa_categoricas(self):
        cliente = self.puntuado["Customer_ID"].iloc[0]
        tabla, _ = M.explicar_cliente(self.modelo, self.df, cliente, n=5)
        self.assertEqual(len(tabla), 5)
        pesos = tabla["Aporte"].abs().to_numpy()
        self.assertTrue(np.all(pesos[:-1] >= pesos[1:]))
        completa, _ = M.explicar_cliente(self.modelo, self.df, cliente, n=100)
        # País aparece una sola vez aunque el modelo tenga una columna por país.
        self.assertEqual((completa["Variable"] == "País").sum(), 1)
        self.assertEqual(len(completa), len(M.VARIABLES_NUMERICAS) + len(M.VARIABLES_CATEGORICAS))

    def test_cliente_inexistente(self):
        with self.assertRaises(KeyError):
            M.explicar_cliente(self.modelo, self.df, "NO_EXISTE")


class PantallasNuevas(unittest.TestCase):
    def app(self, pagina):
        app = AppTest.from_file(str(CARPETA_PROYECTO / "app.py"))
        # Entregable 3: la app pide rol. Las pruebas de regresión entran con el rol "equipo" (todas las pantallas).
        app.secrets["acceso"] = {"gerencia": "prueba-g", "operaciones": "prueba-o", "equipo": "prueba-e"}
        app.session_state["rol"] = "equipo"
        app.run(timeout=120)
        self.assertFalse(app.exception, [e.message for e in app.exception])
        app.switch_page(pagina).run(timeout=120)
        self.assertFalse(app.exception, [e.message for e in app.exception])
        return app

    def test_clientes_muestra_la_explicacion(self):
        a = self.app("paginas/clientes.py")
        self.assertIn("Explicación por cliente: las 5 variables que más pesan en su riesgo", " ".join(m.value for m in a.markdown))
        self.assertTrue(any(s.key == "explicar_cliente" for s in a.selectbox))

    def test_segmentos_se_dibuja_y_suma_la_base(self):
        a = self.app("paginas/segmentos.py")
        texto = " ".join(m.value for m in a.markdown)
        for nombre in M.NOMBRES_SEGMENTO:
            self.assertIn(nombre, texto)
        # Las tablas no muestran índice y respetan el orden de columnas declarado.
        self.assertGreaterEqual(len(a.dataframe), 1)
        a.selectbox(key="seg_elegido").set_value("Desconectados").run(timeout=120)
        self.assertFalse(a.exception)
        self.assertIn("Desconectados", " ".join(m.value for m in a.markdown))


if __name__ == "__main__":
    unittest.main()
