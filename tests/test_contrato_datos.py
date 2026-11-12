"""Pruebas del entregable 2: python -m unittest discover -s tests -v."""
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from src.contrato_datos import (CAMPOS, CAMPOS_ORIGEN, DERIVADAS, ErrorContrato,
                                NUMERICAS, ORIGINALES, validar_origen, validar_procesado)
from src.limpieza import cargar_datos
from src.config import RUTA_DATOS


def ejemplo_valido():
    registro = {}
    for campo in ORIGINALES:
        if campo.tipo == "texto":
            registro[campo.nombre] = {
                "Customer_ID": "C00001", "Gender": "Female", "Country": "UK",
                "City": "London", "Signup_Quarter": "Q1",
            }.get(campo.nombre, "Otro")
        else:
            registro[campo.nombre] = "1,5"
    registro.update(Age="30", Churned="0", Cart_Abandonment_Rate="71,25",
                    Customer_Service_Calls="6", Days_Since_Last_Purchase="3,43")
    return pd.DataFrame([registro])


class ContratoDatosTests(unittest.TestCase):
    def test_contrato_cubre_26_columnas_del_archivo_y_derivadas(self):
        self.assertEqual(len(ORIGINALES), 26)
        self.assertEqual(len(DERIVADAS), 2)
        self.assertEqual(len(CAMPOS), 28)

    def test_comas_decimales_se_convierten_y_dias_se_calculan(self):
        raw = ejemplo_valido()
        self.assertEqual(validar_origen(raw), 1)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "caso.csv"
            raw.to_csv(ruta, index=False)
            procesado = cargar_datos(ruta)
            self.assertAlmostEqual(procesado["Cart_Abandonment_Rate"].iloc[0], 71.25)
            self.assertEqual(procesado["Customer_Service_Calls"].iloc[0], 6)
            self.assertEqual(len(validar_procesado(procesado)), 28)
            self.assertEqual(procesado["Grupo_Edad"].iloc[0], "30–44")

    def test_valor_no_numerico_rompe_el_contrato(self):
        df = ejemplo_valido()
        df.loc[0, "Credit_Balance"] = "ERROR"
        with self.assertRaisesRegex(ErrorContrato, "Credit_Balance"):
            validar_origen(df)

    def test_celda_vacia_no_se_convierte_en_cero(self):
        df = ejemplo_valido()
        df.loc[0, "Age"] = "N/A"
        with self.assertRaisesRegex(ErrorContrato, "Age"):
            validar_origen(df)

    def test_falta_columna_y_doble_id_se_rechazan(self):
        df = ejemplo_valido()
        with self.assertRaisesRegex(ErrorContrato, "Churned"):
            validar_origen(df.drop(columns="Churned"))
        with self.assertRaisesRegex(ErrorContrato, "duplicados"):
            validar_origen(pd.concat([df, df], ignore_index=True))

    def test_no_aplica_no_se_confunde_con_cero(self):
        df = ejemplo_valido()
        df.loc[0, "Credit_Balance"] = "No aplica"
        with self.assertRaisesRegex(ErrorContrato, "revisión humana"):
            validar_origen(df)

    def test_credit_balance_orden_numerico(self):
        raw = ejemplo_valido()
        primero = raw.copy()
        primero["Customer_ID"] = "C00002"
        primero["Credit_Balance"] = "100,5"
        segundo = raw.copy()
        segundo["Customer_ID"] = "C00003"
        segundo["Credit_Balance"] = "20,5"
        muestra = pd.concat([raw, primero, segundo], ignore_index=True)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "orden.csv"
            muestra.to_csv(ruta, index=False)
            datos = cargar_datos(ruta)
        self.assertTrue(pd.api.types.is_numeric_dtype(datos["Credit_Balance"]))
        self.assertEqual(datos.sort_values("Credit_Balance")["Credit_Balance"].tolist(),
                         [1.5, 20.5, 100.5])

    def test_columna_nueva_requiere_contrato(self):
        df = ejemplo_valido()
        df["Columna_Sin_Contrato"] = "dato no documentado"
        with self.assertRaisesRegex(ErrorContrato, "no documentadas"):
            validar_origen(df)

    def test_columna_numero_como_texto_en_tablero_falla(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "caso.csv"
            ejemplo_valido().to_csv(ruta, index=False)
            df = cargar_datos(ruta)
            df["Credit_Balance"] = df["Credit_Balance"].astype(str)
            with self.assertRaisesRegex(ErrorContrato, "Credit_Balance"):
                validar_procesado(df)

    def test_numero_fuera_de_rango_se_rechaza(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "caso.csv"
            df = ejemplo_valido()
            df["Churned"] = "2"
            df.to_csv(ruta, index=False)
            with self.assertRaisesRegex(ErrorContrato, "Churned"):
                cargar_datos(ruta)

    @unittest.skipUnless(RUTA_DATOS.exists(), "El CSV completo solo se encuentra en el repositorio GitHub")
    def test_csv_oficial_rechaza_errores_y_preserva_dtypes(self):
        df = cargar_datos(RUTA_DATOS)
        self.assertEqual(len(df.columns), 28)
        self.assertTrue(all(pd.api.types.is_numeric_dtype(df[c]) for c in NUMERICAS))
        self.assertTrue((validar_procesado(df)["Resultado"] == "Correcto").all())
        # 168 registros traen decimales en una variable rotulada como conteo.
        # Se conservan sin redondear; la app advierte y pide aclarar su origen.
        self.assertEqual(int((df["Customer_Service_Calls"] % 1 != 0).sum()), 168)


if __name__ == "__main__":
    unittest.main()
