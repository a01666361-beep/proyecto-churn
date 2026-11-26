"""Estado vacío (entregable 3): si los filtros dejan 0 clientes, la pantalla avisa y st.stop() la detiene."""
import unittest
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest

from src.config import CARPETA_PROYECTO, REGLA_DEFAULT, RUTA_DATOS
from src.indicadores import tasa_churn
from src.limpieza import cargar_datos

# Pantallas que dependen de los filtros y el texto que dibujan solo si hay clientes
PANTALLAS = {
    "andrea.py": "Tasa de abandono",  # primer KPI: debe quedar después del st.stop()
    "luis.py": "Alertas del modelo",
    "carlos.py": "Abandono por cuartil de valor",
    "clientes.py": "Riesgo alto:",
    "segmentos.py": "Abandono por segmento",
    "resumen.py": "Qué está relacionado con el abandono",
    "recomendaciones.py": "Prioridades",
}


class EstadoVacio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = cargar_datos(RUTA_DATOS)

    def test_seleccion_sin_clientes_se_detiene(self):
        vacio = SimpleNamespace(df=self.df, df_filtrado=self.df.iloc[0:0], regla=dict(REGLA_DEFAULT),
                                tasa_global=tasa_churn(self.df))
        for pagina, contenido in PANTALLAS.items():
            with self.subTest(pagina=pagina):
                app = AppTest.from_file(str(CARPETA_PROYECTO / "paginas" / pagina))
                app.session_state["rol"] = "equipo"
                app.session_state["_contexto"] = vacio
                app.run(timeout=120)
                self.assertFalse(app.exception, [e.message for e in app.exception])
                avisos = " ".join(i.value for i in app.info)
                self.assertIn("Limpiar filtros", avisos)
                textos = " ".join(m.value for m in app.markdown)
                self.assertNotIn(contenido, textos)  # lo que sigue al st.stop() no se dibujó


if __name__ == "__main__":
    unittest.main()
