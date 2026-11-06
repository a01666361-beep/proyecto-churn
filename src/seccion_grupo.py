"""Explica cuánto representa el grupo seleccionado dentro de todo el negocio."""
from html import escape

import streamlit as st

from src.indicadores import resumen_riesgo


def _tarjeta(titulo, cantidad, total, detalle, descripcion):
    if total:
        porcentaje = cantidad / total * 100
        lectura = (f"En otras palabras: aproximadamente {porcentaje:.0f} de cada 100 {descripcion} "
                   "están en este grupo.")
        if cantidad == total:
            lectura = f"Estás viendo todos los {descripcion} del negocio."
        elif cantidad == 0:
            lectura = f"Ninguno de los {descripcion} del negocio está en este grupo."
        elif porcentaje < 0.5:
            lectura = f"Menos de 1 de cada 100 {descripcion} del negocio está en este grupo."
        proporcion = f"<b>{porcentaje:.1f}%</b> de los {descripcion} pertenece a este grupo."
        barra = f'''<div class="grupo-barra" role="img" aria-label="{porcentaje:.1f}% en este grupo">
          <div style="width:{porcentaje:.6f}%"></div></div>
          <div class="grupo-leyenda"><span>Este grupo</span><span>Resto del negocio</span></div>'''
    else:
        proporcion = f"No hay {descripcion} en todo el negocio con los criterios actuales."
        lectura = "No hay casos para hacer esta comparación."
        barra = ""
    return f'''<section class="grupo-tarjeta">
      <h4>{titulo}</h4><div class="grupo-cantidad">{cantidad:,}</div>
      <div class="grupo-texto">{detalle}<br>En todo el negocio: <b>{total:,}</b>.</div>
      <div class="grupo-texto">{proporcion}</div>{barra}
      <div class="grupo-lectura">{lectura}</div></section>'''


def mostrar(df, df_general, regla, filtros):
    grupos = [f"{nombre}: {', '.join(map(str, valores))}" for nombre, valores in filtros.items() if valores]
    seleccion = " · ".join(grupos) if grupos else "Todos los clientes"
    seleccion = escape(seleccion)
    riesgo_grupo = resumen_riesgo(df, regla)["activos_en_perfil"]
    riesgo_general = resumen_riesgo(df_general, regla)["activos_en_perfil"]
    tarjetas = _tarjeta(
        "Clientes que se fueron", int(df.Churned.sum()), int(df_general.Churned.sum()),
        "clientes se fueron de este grupo.", "clientes que se fueron",
    ) + _tarjeta(
        "Clientes activos con señales de riesgo", riesgo_grupo, riesgo_general,
        "activos de este grupo tienen señales de riesgo.", "activos con señales de riesgo",
    )
    html = f'''<div class="grupo-bloque">
      <h3>¿Qué parte del problema está en este grupo?</h3>
      <p class="grupo-contexto">{seleccion} · {len(df):,} clientes en este grupo</p>
      <div class="grupo-columnas">{tarjetas}</div>
      <p class="grupo-nota">Las barras muestran cuánto representa este grupo dentro del negocio.
      Los filtros no explican por qué se fueron los clientes.<br>
      Se usan los mismos criterios de riesgo para todos: carrito abandonado mayor a {regla['carrito_min']:.2f}%
      y {regla['llamadas_min']} o más llamadas.</p></div>'''
    st.markdown("".join(linea.strip() for linea in html.splitlines()), unsafe_allow_html=True)
