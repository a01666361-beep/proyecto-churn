"""Gradient Boosting de la pantalla 07: reproduce el notebook y aplica bien los logaritmos.
Ejecutar: python -m unittest discover -s tests"""
import json
import unittest

import numpy as np
from sklearn.metrics import roc_auc_score

from src import modelo_gb as G


class ModeloGB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = G.leer(G.RUTA_TRAIN)
        cls.test = G.leer(G.RUTA_TEST)
        cls.modelo = G.entrenar(cls.train)
        cls.num = G.numericas(cls.train)

    def test_reglas_de_los_datos(self):
        self.assertEqual(list(self.train.columns), list(self.test.columns))
        self.assertEqual(int(self.train.isna().sum().sum()), 0)        # train limpio
        self.assertGreater(int(self.test.isna().sum().sum()), 0)        # test sin imputar (solo log)
        self.assertEqual((len(self.train), len(self.test)), (40_000, 10_000))
        for c in G.VARIABLES_LOG:
            self.assertIn(c, self.train)

    def test_usa_solo_las_11_variables_del_modelo_final(self):
        entradas = list(self.modelo.feature_names_in_)
        self.assertEqual(len(entradas), 11)
        self.assertEqual(set(entradas), set(G.NUMERICAS) | {"City"})
        self.assertEqual(len(G.CAMPOS) + len(G.CATEGORICAS), 11)  # el formulario pide las mismas

    def test_reproduce_las_metricas_del_notebook(self):
        resumen = json.loads((G.CARPETA / "resumen_campeon.json").read_text(encoding="utf-8"))
        prob = self.modelo.predict_proba(self.test[self.num + G.CATEGORICAS])[:, 1]
        auc = roc_auc_score(self.test[G.OBJETIVO], prob)
        self.assertAlmostEqual(auc, resumen["metricas_test"]["AUC"], places=3)
        tabla = G.comparativa().query("Partición == 'Validación'").set_index("Modelo")
        self.assertEqual(tabla["AUC"].idxmax(), G.CAMPEON)

    def test_prediccion_desde_escala_original(self):
        fila = self.test.iloc[0]
        datos = {c.replace("log_", ""): (None if np.isnan(fila[c]) else
                                         (float(np.expm1(fila[c])) if c in G.VARIABLES_LOG else float(fila[c])))
                 for c in self.num}
        datos.update({c: fila[c] for c in G.CATEGORICAS})
        r = G.predecir(self.modelo, datos, self.num)
        directo = self.modelo.predict_proba(self.test[self.num + G.CATEGORICAS].iloc[[0]])[:, 1][0]
        self.assertAlmostEqual(r["probabilidad"], directo, places=9)
        self.assertEqual(r["decision"], G.CAMPANA if directo > G.CORTE else G.SIN_ACCION)

    def test_logaritmo_y_dato_faltante(self):
        fila = G.preparar_cliente({"Total_Purchases": 9, "Age": None}, self.num)
        self.assertAlmostEqual(fila["log_Total_Purchases"].iloc[0], np.log(10))
        self.assertTrue(np.isnan(fila["Age"].iloc[0]))  # no se rellena con cero
        with self.assertRaises(ValueError):
            G.preparar_cliente({"Total_Purchases": -1}, self.num)


if __name__ == "__main__":
    unittest.main()
