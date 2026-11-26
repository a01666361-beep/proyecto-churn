"""
Acceso por rol (entregable 3).

Mecanismo: cada rol tiene una contraseña guardada en los Secrets de Streamlit Cloud
(Manage app → Settings → Secrets), nunca en el repositorio:

    [acceso]
    gerencia = "..."
    operaciones = "..."
    equipo = "..."

Al entrar, la persona elige su rol y escribe la contraseña. Con el rol validado,
app.py registra en st.navigation() SOLO las pantallas que ese rol puede ver: las demás
no aparecen en el menú y tampoco se pueden abrir escribiendo su URL. Dentro de una
pantalla compartida, `puede()` decide si se muestra un elemento sensible (por ejemplo,
la lista de clientes con su ID).

Limitación: es una contraseña compartida por rol, no una cuenta por persona. No sabemos
quién de los que comparten la contraseña entró, no hay bloqueo por intentos fallidos
ni registro de accesos, y si la contraseña se filtra hay que cambiarla a mano en Secrets.
Para producción se usaría un proveedor de identidad (OIDC con st.login) con cuentas
individuales y los roles asignados en ese proveedor.
"""
import hmac

import streamlit as st

# Pantallas de la app (ruta del archivo → título en el menú)
PANTALLAS = {
    "paginas/resumen.py": "Resumen general",
    "paginas/andrea.py": "Andrea · Priorizar campañas",
    "paginas/luis.py": "Luis · Monitoreo y calidad",
    "paginas/carlos.py": "Carlos · Valor y presupuesto",
    "paginas/clientes.py": "Clientes prioritarios",
    "paginas/segmentos.py": "Segmentos",
    "paginas/modelos.py": "Comparativa y predicción",
    "paginas/recomendaciones.py": "Recomendaciones",
    "paginas/asistente.py": "Asistente de retención (IA)",
    "paginas/actualizacion.py": "Actualización de datos y del modelo",
}

# Matriz de acceso por rol. Principio: cada rol ve lo que necesita para su decisión y nada más.
# El corte se hace por tipo de dato, no por gusto: Gerencia decide con agregados (a qué segmento,
# en qué país, cuánto invertir, si el modelo es confiable); Operaciones trabaja con datos de clientes
# individuales (ID, probabilidad, explicación por cliente, listas y descargas) y es la única que
# puede cargar datos nuevos o cambiar el modelo. Justificación completa: docs/entregable-3.md.
ROLES = {
    "gerencia": {
        "nombre": "Gerencia de retención y estrategia (Andrea, Carlos)",
        # Sin el asistente de IA: sus herramientas regresan clientes con su ID (dato individual).
        "pantallas": ["paginas/resumen.py", "paginas/andrea.py", "paginas/carlos.py", "paginas/segmentos.py",
                      "paginas/modelos.py", "paginas/recomendaciones.py"],
        "permisos": set(),
    },
    "operaciones": {
        "nombre": "Operaciones de datos y CRM (Luis)",
        "pantallas": ["paginas/resumen.py", "paginas/luis.py", "paginas/clientes.py", "paginas/segmentos.py",
                      "paginas/modelos.py", "paginas/recomendaciones.py", "paginas/asistente.py",
                      "paginas/actualizacion.py"],
        "permisos": {"ver_clientes"},
    },
    "equipo": {
        "nombre": "Equipo de desarrollo (todas las pantallas)",
        "pantallas": list(PANTALLAS),
        "permisos": {"ver_clientes"},
    },
}

# Permisos dentro de una pantalla compartida
PERMISOS = {"ver_clientes": "Ver y descargar listas de clientes con su ID y probabilidad de abandono"}


def pantallas_de(rol):
    return list(ROLES[rol]["pantallas"])


def rol_actual():
    return st.session_state.get("rol")


def puede(permiso):
    rol = rol_actual()
    return rol in ROLES and permiso in ROLES[rol]["permisos"]


def _contrasenas():
    try:
        return dict(st.secrets["acceso"])
    except (KeyError, FileNotFoundError, AttributeError):
        return {}


def _validar(rol, clave, contrasenas):
    guardada = contrasenas.get(rol, "")
    # compare_digest compara en tiempo constante (no revela cuántos caracteres coinciden)
    return bool(guardada) and hmac.compare_digest(clave.encode(), str(guardada).encode())


def _cerrar_sesion():
    st.session_state.pop("rol", None)


def iniciar_sesion():
    """Pide rol y contraseña. Si no hay sesión válida, detiene la app con st.stop()."""
    rol = rol_actual()
    if rol in ROLES:
        return rol

    contrasenas = _contrasenas()
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        st.markdown('<h2 class="seccion-titulo">Iniciar sesión</h2>', unsafe_allow_html=True)
        if not contrasenas:
            st.error("El acceso no está configurado: faltan las contraseñas por rol en **Secrets** "
                     "(sección `[acceso]`). Ninguna pantalla se muestra sin ellas.")
            st.stop()
        st.caption("Cada rol ve solo las pantallas que necesita para su decisión.")
        with st.form("login"):
            elegido = st.selectbox("Rol", list(ROLES), format_func=lambda r: ROLES[r]["nombre"], key="login_rol")
            clave = st.text_input("Contraseña del rol", type="password", key="login_clave")
            entrar = st.form_submit_button("Entrar", type="primary")
        if entrar:
            if _validar(elegido, clave, contrasenas):
                st.session_state["rol"] = elegido
                st.session_state.pop("login_clave", None)
                st.rerun()
            st.error("Rol o contraseña incorrectos.")
    st.stop()


def barra_sesion():
    """Muestra con qué rol se entró y el botón para salir (panel derecho)."""
    rol = rol_actual()
    st.markdown(f'<p class="sesion-rol"><b>Rol:</b> {ROLES[rol]["nombre"]}</p>', unsafe_allow_html=True)
    st.button("Cerrar sesión", on_click=_cerrar_sesion, use_container_width=True, key="cerrar_sesion")


def exigir(pantalla):
    """Segunda barrera dentro de cada pantalla: si el rol no la tiene, no se dibuja nada."""
    rol = rol_actual()
    if rol not in ROLES or pantalla not in ROLES[rol]["pantallas"]:
        st.error("Tu rol no tiene acceso a esta pantalla.")
        st.stop()
