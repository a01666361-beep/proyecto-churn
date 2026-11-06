"""Presenta por separado las gráficas existentes, sin recalcular sus datos."""
import plotly.graph_objects as go


def separar_panel(figura, panel, alto=290):
    sufijo = "" if panel == 1 else str(panel)
    eje_x, eje_y = f"x{sufijo}", f"y{sufijo}"
    resultado = go.Figure()
    for traza in figura.data:
        if (traza.xaxis or "x") == eje_x and (traza.yaxis or "y") == eje_y:
            datos = traza.to_plotly_json()
            datos.update(xaxis="x", yaxis="y")
            resultado.add_trace(datos)
    for nombre, referencia in [("xaxis", "y"), ("yaxis", "x")]:
        datos = figura.layout[f"{nombre}{sufijo}"].to_plotly_json()
        datos.update(domain=[0, 1], anchor=referencia, automargin=True,
                     tickfont=dict(size=12), title_font=dict(size=12))
        datos.pop("matches", None)
        resultado.update_layout(**{nombre: datos})
    for forma in figura.layout.shapes or []:
        datos = forma.to_plotly_json()
        if datos.get("xref", "x").split()[0] == eje_x and datos.get("yref", "y").split()[0] == eje_y:
            datos["xref"] = datos.get("xref", "x").replace(eje_x, "x", 1)
            datos["yref"] = datos.get("yref", "y").replace(eje_y, "y", 1)
            resultado.add_shape(datos)
    resultado.update_layout(height=alto, margin=dict(l=0, r=30, t=24, b=10),
                            showlegend=False, bargap=0.25,
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return resultado
