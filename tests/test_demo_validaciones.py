"""La demostración usa validadores reales y no altera los datos de clientes."""
import unittest

from src.config import RUTA_DATOS
from src.demo_validaciones import CASOS, crear_demostracion
from src.limpieza import cargar_datos


class DemoContratoDatosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = cargar_datos(RUTA_DATOS)

    def test_cada_ejemplo_se_rechaza(self):
        for caso in CASOS:
            with self.subTest(caso=caso):
                result = crear_demostracion(self.df, caso)
                self.assertTrue(result["bloqueado"], result)
                self.assertTrue(result["mensaje"])
                self.assertEqual(result["detalle"].loc[0, "Resultado"], "Rechazado")

    def test_caso_texto_identifica_valor(self):
        result = crear_demostracion(self.df, "texto")
        self.assertIn("Credit_Balance", result["mensaje"])
        self.assertIn("no numéricos", result["mensaje"])

    def test_edad_fuera_de_rango(self):
        result = crear_demostracion(self.df, "rango")
        self.assertIn("Age", result["mensaje"])
        self.assertIn("80", result["mensaje"])

    def test_datos_reales_permanecen_inalterados(self):
        original = self.df.loc[:2, ["Age", "Credit_Balance", "Customer_ID"]].copy(deep=True)
        for caso in CASOS:
            crear_demostracion(self.df, caso)
        self.assertTrue(self.df.loc[:2, original.columns].equals(original))


if __name__ == "__main__":
    unittest.main()
