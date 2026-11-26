"""Acceso por rol (entregable 3): dos roles entran y ven contenidos distintos."""
import unittest

from streamlit.testing.v1 import AppTest

from src import acceso
from src.config import CARPETA_PROYECTO

CLAVES = {"gerencia": "clave-gerencia", "operaciones": "clave-operaciones", "equipo": "clave-equipo"}


def nueva_app(secretos=True):
    app = AppTest.from_file(str(CARPETA_PROYECTO / "app.py"))
    if secretos:
        app.secrets["acceso"] = dict(CLAVES)
    return app


def texto(app):
    partes = [m.value for m in app.markdown] + [m.value for m in app.metric] + [e.value for e in app.error] + \
             [i.value for i in app.info] + [c.value for c in app.caption]
    return " ".join(str(p) for p in partes)


def entrar(rol, clave):
    app = nueva_app().run(timeout=120)
    app.selectbox(key="login_rol").set_value(rol)
    app.text_input(key="login_clave").input(clave)
    app.button[0].click().run(timeout=120)  # botón "Entrar" del formulario
    return app


class MatrizDeAcceso(unittest.TestCase):
    def test_los_dos_roles_de_negocio_ven_cosas_distintas(self):
        gerencia, operaciones = set(acceso.pantallas_de("gerencia")), set(acceso.pantallas_de("operaciones"))
        self.assertIn("paginas/andrea.py", gerencia - operaciones)
        self.assertIn("paginas/luis.py", operaciones - gerencia)
        self.assertIn("paginas/clientes.py", operaciones - gerencia)  # listas con ID: solo Operaciones
        self.assertNotIn("ver_clientes", acceso.ROLES["gerencia"]["permisos"])
        self.assertIn("ver_clientes", acceso.ROLES["operaciones"]["permisos"])

    def test_toda_pantalla_existe_y_tiene_algun_rol(self):
        for pantalla in acceso.PANTALLAS:
            with self.subTest(pantalla=pantalla):
                self.assertTrue((CARPETA_PROYECTO / pantalla).exists())
                self.assertTrue(any(pantalla in r["pantallas"] for r in acceso.ROLES.values()))

    def test_cada_pantalla_tiene_su_barrera(self):
        for pantalla in acceso.PANTALLAS:
            with self.subTest(pantalla=pantalla):
                codigo = (CARPETA_PROYECTO / pantalla).read_text(encoding="utf-8")
                self.assertIn(f'acceso.exigir("{pantalla}")', codigo)

    def test_no_hay_contrasenas_en_el_repositorio(self):
        ignorados = (CARPETA_PROYECTO / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".streamlit/secrets.toml", ignorados)
        codigo = (CARPETA_PROYECTO / "src" / "acceso.py").read_text(encoding="utf-8")
        self.assertIn('st.secrets["acceso"]', codigo)


class InicioDeSesion(unittest.TestCase):
    def test_sin_sesion_no_se_ve_ninguna_pantalla(self):
        app = nueva_app().run(timeout=120)
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertIn("Iniciar sesión", texto(app))
        self.assertNotIn("Situación actual", texto(app))  # contenido del resumen

    def test_sin_secrets_la_app_no_abre(self):
        app = nueva_app(secretos=False)
        app.secrets["acceso"] = {}  # vacío aunque la compu tenga un .streamlit/secrets.toml local
        app.run(timeout=120)
        self.assertFalse(app.exception)
        self.assertIn("El acceso no está configurado", texto(app))
        self.assertEqual(len(app.text_input), 0)

    def test_contrasena_incorrecta(self):
        app = entrar("gerencia", "no-es")
        self.assertFalse(app.exception)
        self.assertIn("Rol o contraseña incorrectos", texto(app))
        self.assertNotIn("rol", app.session_state)

    def test_la_contrasena_de_otro_rol_no_sirve(self):
        app = entrar("operaciones", CLAVES["gerencia"])
        self.assertIn("Rol o contraseña incorrectos", texto(app))

    def test_gerencia_entra_y_no_ve_lo_de_operaciones(self):
        app = entrar("gerencia", CLAVES["gerencia"])
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertEqual(app.session_state["rol"], "gerencia")
        self.assertIn("Situación actual", texto(app))
        self.assertIn("Gerencia de retención", texto(app))
        app.switch_page("paginas/segmentos.py").run(timeout=120)
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertIn("solo la ve el rol", texto(app))
        self.assertFalse([b for b in app.get("download_button")], "Gerencia no descarga listas de clientes")

    def test_operaciones_entra_y_ve_la_lista(self):
        app = entrar("operaciones", CLAVES["operaciones"])
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertEqual(app.session_state["rol"], "operaciones")
        app.switch_page("paginas/segmentos.py").run(timeout=120)
        self.assertFalse(app.exception, [e.message for e in app.exception])
        self.assertNotIn("solo la ve el rol", texto(app))
        self.assertTrue([b for b in app.get("download_button")])

    def test_pantalla_de_otro_rol_no_esta_registrada(self):
        """Con el rol de gerencia, la pantalla de Luis no existe en la navegación (tampoco por URL)."""
        app = nueva_app()
        app.session_state["rol"] = "gerencia"
        app.run(timeout=120)
        with self.assertRaises(ValueError):
            app.switch_page("paginas/luis.py")

    def test_la_barrera_de_pantalla_detiene_a_otro_rol(self):
        """Segunda barrera: si la pantalla de Luis se ejecutara con el rol de gerencia, no dibuja nada."""
        app = AppTest.from_file(str(CARPETA_PROYECTO / "paginas" / "luis.py"))
        app.session_state["rol"] = "gerencia"
        app.run(timeout=120)
        self.assertIn("Tu rol no tiene acceso", texto(app))
        self.assertNotIn("Alertas del modelo", texto(app))

    def test_cerrar_sesion(self):
        app = entrar("operaciones", CLAVES["operaciones"])
        next(b for b in app.button if b.label == "Cerrar sesión").click().run(timeout=120)
        self.assertNotIn("rol", app.session_state)
        self.assertIn("Iniciar sesión", texto(app))


if __name__ == "__main__":
    unittest.main()
