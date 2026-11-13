"""
Pantalla 02 · Luis Ramírez, coordinador de operaciones de datos y CRM.
Pregunta: ¿hay alguna alerta, los datos son confiables y quiénes entran a la lista de campaña?
RESPONSABLE: (poner nombre)
"""
import streamlit as st

from src.config import ALERTA_PP, META_RIESGO
from src.contexto import contexto
from src.indicadores import resumen_riesgo, tasa_churn
from src.vistas import DEFINICIONES, alertas, calidad_datos, tabla_clientes
from src.contrato_datos import resumen_validacion
from src.demo_validaciones import CASOS as CASOS_DEMO, crear_demostracion
from src.tablas_datos import configuracion_columnas

c = contexto()
df, df_general, regla, tasa_global = c.df_filtrado, c.df, c.regla, c.tasa_global

st.markdown('<h2 class="seccion-titulo">Centro de monitoreo y calidad</h2>', unsafe_allow_html=True)
st.caption("Alertas verificables, revisión de datos y listas de clientes para campañas · "
           f"{len(df):,} de {len(df_general):,} clientes en el grupo seleccionado")

monitoreo, datos, definiciones = st.tabs(["Monitoreo", "Datos", "Definiciones"])

# ------------------------------------------------------------------ Monitoreo
with monitoreo:
    tasa = tasa_churn(df)
    riesgo = resumen_riesgo(df, regla)
    calidad = calidad_datos(df_general)  # la calidad se revisa sobre la base completa
    llamadas_fraccionarias = int((df_general["Customer_Service_Calls"] % 1 != 0).sum())
    if llamadas_fraccionarias:
        st.warning(f"Hay {llamadas_fraccionarias:,} registros con llamadas fraccionarias en el CSV; se conservan sin redondear hasta aclarar su origen.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Churn de la selección", f"{tasa:.1%}" if len(df) else "—",
              f"{(tasa - tasa_global) * 100:+.1f} pts vs. línea base", delta_color="inverse")
    m2.metric("Activos en perfil de riesgo", f"{riesgo['pct_activos']:.1%}" if riesgo["total_activos"] else "—",
              f"{(riesgo['pct_activos'] - META_RIESGO) * 100:+.1f} pts vs. meta ({META_RIESGO:.1%})",
              delta_color="inverse")
    m3.metric("Valores nulos", f"{calidad['nulos']:,}", help=f"Base completa · {calidad['variables']} columnas")
    m4.metric("Fecha de última carga", "No informada", help="El CSV no incluye metadatos de carga.")

    izquierda, derecha = st.columns([1.2, 1], gap="medium")
    with izquierda:
        with st.container(border=True):
            st.markdown("### Estado de alertas")
            for alerta in alertas(tasa, tasa_global, riesgo, calidad):
                if alerta["encendida"]:
                    st.error(f"**{alerta['titulo']}** · {alerta['motivo']}", icon=":material/warning:")
                else:
                    st.success(f"**{alerta['titulo']}**: sin alerta · {alerta['motivo']}", icon=":material/check_circle:")
            st.caption("El estado se recalcula con los filtros y la regla activa.")
        with st.container(border=True):
            st.markdown("### Regla de riesgo vigente")
            st.markdown(f"Carrito abandonado **> {regla['carrito_min']:.2f}%** y **{regla['llamadas_min']} o más** "
                        "llamadas a servicio (ambos criterios a la vez).")
            st.caption(f"**{riesgo['activos_en_perfil']:,}** activos cumplen la regla · churn histórico del perfil: "
                       f"**{riesgo['tasa_historica']:.1%}** ({riesgo['clientes_en_perfil']:,} clientes). "
                       "Se ajusta en *Criterios de riesgo* (panel derecho); *Limpiar filtros* regresa a la regla oficial. "
                       "Es una regla descriptiva, no una probabilidad individual.")
    with derecha:
        with st.container(border=True):
            st.markdown("### Calidad y trazabilidad")
            st.markdown(f"""
| Revisión | Resultado |
|---|---|
| Registros | {calidad['registros']:,} |
| IDs duplicados | {calidad['duplicados']:,} |
| Valores fuera de rango | {calidad['invalidos']:,} |
| Variables revisadas | {calidad['variables']} |
""")
            st.caption("Revisa campos vacíos, IDs repetidos y rangos evidentes (edad, churn 0/1, carrito 0–100%, "
                       "llamadas ≥ 0). No certifica que las transformaciones o unidades sean correctas.")
        with st.container(border=True):
            st.markdown("### Umbrales de seguimiento")
            st.markdown(f"""
| Referencia | Valor |
|---|---|
| Churn global (línea base) | {tasa_global:.2%} |
| Umbral de alerta (+{ALERTA_PP * 100:.0f} pts) | {tasa_global + ALERTA_PP:.2%} |
| Meta de activos en riesgo | menos de {META_RIESGO:.1%} |
""")

    with st.expander("Contrato de datos · revisión de tipos y origen de las cifras"):
        comprobacion = resumen_validacion(df_general)
        correctas = int((comprobacion["Resultado"] == "Correcto").sum())
        if correctas == len(comprobacion):
            st.success(f"Verificación automática: {correctas}/{len(comprobacion)} columnas correctas")
        else:
            st.error(f"Hay errores de tipo o valores ausentes: {correctas}/{len(comprobacion)} correctas")
        st.dataframe(comprobacion, column_order=list(comprobacion.columns),
                     hide_index=True, use_container_width=True, height=280)
        st.caption("El CSV se valida antes de generar las pantallas; un dato que no cumple impide mostrar cifras incorrectas")

    # [M4C-P2 DEMO ERRORES]
    with st.expander("Demostración de errores · ejemplos seguros", expanded=False):
        st.info("MODO DEMOSTRACIÓN: se modifica una copia de 3 filas en memoria. Los datos reales y los KPI no cambian.")
        caso_demo = st.selectbox(
            "Selecciona un error de ejemplo",
            list(CASOS_DEMO),
            format_func=lambda k: CASOS_DEMO[k],
            key="m4c_parte2_caso_demo",
        )
        ejemplo = crear_demostracion(df_general, caso_demo)
        st.dataframe(ejemplo["detalle"], hide_index=True,
                     column_order=list(ejemplo["detalle"].columns),
                     use_container_width=True)
        if ejemplo["bloqueado"]:
            st.error("DEMO · Carga rechazada por el contrato de datos")
            st.code(ejemplo["mensaje"], language=None)
        else:
            st.warning("DEMO · El validador no rechazó el caso; revisar las reglas")
        st.caption("El mensaje proviene del validador real. Con ese fallo en el CSV original, "
                   "la aplicación detendría la carga antes de mostrar los datos.")

# ------------------------------------------------------------------ Datos
with datos:
    a, b = st.columns([1, 2])
    solo_riesgo = a.toggle("Solo activos en perfil de riesgo", value=True, key="l_solo_riesgo")
    buscar = b.text_input("Buscar por ID, país o ciudad", key="l_buscar", placeholder="Ej. C00012, UK, Toronto")
    lista = tabla_clientes(df, regla, solo_riesgo, buscar)
    st.caption(f"{len(lista):,} clientes en la lista")
    st.dataframe(lista, column_order=list(lista.columns), hide_index=True,
                 height=420, use_container_width=True,
                 column_config=configuracion_columnas(lista))
    st.download_button("Descargar lista (CSV)", lista.to_csv(index=False).encode("utf-8"),
                       file_name="lista_campana_retencion.csv", mime="text/csv", disabled=lista.empty)
    st.caption("Origen por columna: abre la ayuda del encabezado, las cifras originales vienen del CSV y los días sin comprar son calculados con exp(x) − 1, el LTV está en escala logarítmica y no tiene moneda documentada")

# ------------------------------------------------------------------ Definiciones
with definiciones:
    st.caption("Nombre de campo, interpretación y unidad disponible. Las unidades no documentadas se indican "
               "como tales; no se les asigna una moneda.")
    st.dataframe(DEFINICIONES, column_order=list(DEFINICIONES.columns), hide_index=True, height=520, use_container_width=True)
