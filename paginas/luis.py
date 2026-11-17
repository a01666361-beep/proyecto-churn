"""
Pantalla 02 · Luis Ramírez, coordinador de operaciones de datos y CRM.
Decisión: si hay alertas del modelo, si los datos son confiables y quiénes entran a la lista de campaña.
RESPONSABLE: (poner nombre)
"""
import streamlit as st

from src import ayuda
from src import modelo as M
from src.config import ALERTA_PP, META_RIESGO
from src.contexto import contexto
from src.indicadores import resumen_riesgo, tasa_churn
from src.puntuacion import modelo_y_puntuacion as modelo_y_puntajes
from src.vistas import DEFINICIONES, alertas_modelo, calidad_datos, simular_datos, tabla_clientes
from src.contrato_datos import resumen_validacion
from src.demo_validaciones import CASOS as CASOS_DEMO, crear_demostracion
from src.tablas_datos import configuracion_columnas

c = contexto()
df, df_general, regla, tasa_global = c.df_filtrado, c.df, c.regla, c.tasa_global

ayuda.titulo_pantalla("Centro de monitoreo y calidad", "luis",
                      "Alertas del modelo, calidad de los datos y lista de clientes para campañas · "
                      f"{len(df):,} de {len(df_general):,} clientes en el grupo seleccionado")

# Retroalimentación 12-nov: se quitó la pestaña "Datos"; la lista de clientes queda oculta en un desplegable.
monitoreo, definiciones = st.tabs(["Monitoreo", "Definiciones"])

# ------------------------------------------------------------------ Monitoreo
with monitoreo:
    resultado, puntuado_total = modelo_y_puntajes()
    puntuado = puntuado_total.loc[df.index]  # predicción del modelo para la selección de filtros
    tasa = tasa_churn(df)
    riesgo = resumen_riesgo(df, regla)
    calidad = calidad_datos(df_general)  # la calidad se revisa sobre la base completa
    alertas = alertas_modelo(puntuado, puntuado_total)
    problemas = calidad["nulos"] + calidad["duplicados"] + calidad["invalidos"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Churn de la selección", f"{tasa:.1%}" if len(df) else "—",
              f"{(tasa - tasa_global) * 100:+.1f} pts vs. línea base", delta_color="inverse",
              help="Dato observado: clientes que ya abandonaron.")
    m2.metric("Activos con riesgo alto (modelo)", f"{alertas[0]['valor']:.1%}",
              f"{(alertas[0]['valor'] - (alertas[0]['umbral'] - ALERTA_PP)) * 100:+.1f} pts vs. negocio",
              delta_color="inverse", help="Predicción: activos con probabilidad de abandono de 70% o más.")
    m3.metric("Problemas de calidad", f"{problemas:,}", help="Nulos, IDs duplicados y valores fuera de rango "
                                                              "en la base completa.")

    with st.container(border=True):
        ayuda.titulo_grafica(
            "Alertas del modelo",
            "Si los clientes activos de la selección tienen más riesgo de abandono que los del negocio, según el modelo.",
            f"Rojo = alerta encendida: la selección supera el valor del negocio en más de {ALERTA_PP * 100:.0f} puntos. "
            "Verde = sin alerta. Cambian con los filtros.",
            "Si conviene adelantar la campaña de retención para el grupo seleccionado.")
        if not len(df):
            st.info("No hay clientes con esta combinación de filtros. Usa **Limpiar filtros**.")
        for alerta in alertas:
            if alerta["encendida"]:
                st.error(f"**{alerta['titulo']}** · {alerta['motivo']}", icon=":material/warning:")
            else:
                st.success(f"**{alerta['titulo']}**: sin alerta · {alerta['motivo']}", icon=":material/check_circle:")
        st.caption("Predicción del modelo de regresión logística (pantalla Clientes prioritarios), no dato observado.")

    with st.expander("Probar las alertas con datos modificados (simulación)"):
        st.info("SIMULACIÓN: se modifica una copia de los datos de la selección y se vuelve a puntuar con el modelo. "
                "Los datos reales no cambian.")
        a, b = st.columns(2)
        llamadas_extra = a.slider("Llamadas a servicio adicionales por cliente", 0, 5, 0, key="l_sim_llamadas")
        carrito_extra = b.slider("Puntos adicionales de carrito abandonado", 0, 30, 0, 5, key="l_sim_carrito")
        if len(df):
            simulado = M.puntuar(simular_datos(df, llamadas_extra, carrito_extra), resultado["modelo"])
            for antes, despues in zip(alertas, alertas_modelo(simulado, puntuado_total)):
                estado = "encendida" if despues["encendida"] else "apagada"
                texto = (f"**{despues['titulo']}**: {antes['valor']:.1%} → **{despues['valor']:.1%}** "
                         f"(umbral {despues['umbral']:.1%}) · alerta {estado}")
                (st.error if despues["encendida"] else st.success)(texto)
            st.caption("Ejemplo para validar: con 1 llamada adicional por cliente, las dos alertas se encienden.")

    izquierda, derecha = st.columns(2, gap="medium")
    with izquierda:
        with st.container(border=True):
            st.markdown("### Calidad y trazabilidad")
            st.markdown(f"""
| Revisión | Resultado |
|---|---|
| Registros | {calidad['registros']:,} |
| Valores nulos | {calidad['nulos']:,} |
| IDs duplicados | {calidad['duplicados']:,} |
| Valores fuera de rango | {calidad['invalidos']:,} |
""")
            llamadas_fraccionarias = int((df_general["Customer_Service_Calls"] % 1 != 0).sum())
            if llamadas_fraccionarias:
                st.caption(f"{llamadas_fraccionarias:,} registros tienen llamadas fraccionarias en el CSV; se "
                           "conservan sin redondear hasta aclarar su origen.")
            st.caption("Revisa campos vacíos, IDs repetidos y rangos evidentes (edad, churn 0/1, carrito 0–100%, "
                       "llamadas ≥ 0). No certifica que las transformaciones o unidades sean correctas.")
    with derecha:
        with st.container(border=True):
            st.markdown("### Regla descriptiva de riesgo")
            st.markdown(f"Carrito abandonado **> {regla['carrito_min']:.2f}%** y **{regla['llamadas_min']} o más** "
                        f"llamadas: **{riesgo['activos_en_perfil']:,}** activos ({riesgo['pct_activos']:.1%}; "
                        f"meta: menos de {META_RIESGO:.1%}).")
            st.caption(f"Churn histórico del perfil: {riesgo['tasa_historica']:.1%}. Se ajusta en *Criterios de "
                       "riesgo*. Es una regla descriptiva, no una probabilidad individual: las alertas de arriba usan "
                       "el modelo.")

    with st.expander("Lista de clientes para campaña (oculta)"):
        a, b = st.columns([1, 2])
        solo_riesgo = a.toggle("Solo activos en perfil de riesgo", value=True, key="l_solo_riesgo")
        buscar = b.text_input("Buscar por ID, país o ciudad", key="l_buscar", placeholder="Ej. C00012, UK, Toronto")
        lista = tabla_clientes(df, regla, solo_riesgo, buscar)
        st.caption(f"{len(lista):,} clientes en la lista")
        st.dataframe(lista, column_order=list(lista.columns), hide_index=True,
                     height=360, use_container_width=True,
                     column_config=configuracion_columnas(lista))
        st.download_button("Descargar lista (CSV)", lista.to_csv(index=False).encode("utf-8"),
                           file_name="lista_campana_retencion.csv", mime="text/csv", disabled=lista.empty)
        st.caption("Origen por columna: abre la ayuda del encabezado, las cifras originales vienen del CSV y los días "
                   "sin comprar son calculados con exp(x) − 1, el LTV está en escala logarítmica y no tiene moneda "
                   "documentada")

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

# ------------------------------------------------------------------ Definiciones
with definiciones:
    st.caption("Nombre de campo, interpretación y unidad disponible. Las unidades no documentadas se indican "
               "como tales; no se les asigna una moneda.")
    st.dataframe(DEFINICIONES, column_order=list(DEFINICIONES.columns), hide_index=True, height=520, use_container_width=True)
