"""Visualización: región 2D y sólido de revolución 3D con Plotly.

El sólido puede mostrarse completo o parcialmente girado (parámetro ``angulo``),
junto con secciones transversales (disco, arandela o cascarón) que forman el volumen.
Las figuras reciben ``tema`` ("claro" u "oscuro") para adaptar fuentes, ejes, rejillas
y etiquetas a la interfaz.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from .calculo import Problema

COLOR_EXTERIOR = "#1E6FA8"
COLOR_INTERIOR = "#C08A3E"
COLOR_SECCION = "#C0402B"
COLOR_CORTE = "#2E7D6F"
COLOR_EJE = "#B4703F"

_FUENTE = "Bahnschrift, Segoe UI, sans-serif"

# Degradados según el radio al eje de giro (interior oscuro → exterior claro).
_COLORESCALA_F = [[0, "#0A3552"], [0.35, "#1A6699"], [0.7, "#3E97CE"], [1, "#8FD0EE"]]
_COLORESCALA_G = [[0, "#6B4718"], [0.5, "#C08A3E"], [1, "#EBCB96"]]

_TEMAS = {
    "claro": {
        "tinta": "#16222E",
        "suave": "#5D6C7B",
        "rejilla": "#E3E8ED",
        "borde": "#CBD4DC",
        "hover_fondo": "#16222E",
        "hover_texto": "#FFFFFF",
        "azul": COLOR_EXTERIOR,
    },
    "oscuro": {
        "tinta": "#E6EDF3",
        "suave": "#93A4B3",
        "rejilla": "#24323F",
        "borde": "#33475A",
        "hover_fondo": "#1B2A36",
        "hover_texto": "#E6EDF3",
        "azul": "#57A9E6",
    },
}


def _tema(nombre: str) -> dict:
    """Paleta de figuras del tema pedido (claro si el nombre no se reconoce)."""
    return _TEMAS.get(nombre, _TEMAS["claro"])


def _modebar(t: dict) -> dict:
    return dict(bgcolor="rgba(0,0,0,0)", color=t["suave"], activecolor=t["tinta"])


def _hoverlabel(t: dict) -> dict:
    return dict(
        font=dict(family=_FUENTE, color=t["hover_texto"]),
        bgcolor=t["hover_fondo"],
    )


def _eje_plano(t: dict, titulo: str, rango: list[float] | None = None) -> dict:
    """Eje cartesiano 2D con los colores del tema."""
    eje = dict(
        title=titulo,
        rangemode="normal",
        gridcolor=t["rejilla"],
        zerolinecolor=t["borde"],
        linecolor=t["borde"],
        ticks="outside",
        tickcolor=t["borde"],
        showline=True,
        tickfont=dict(size=11, color=t["suave"]),
        title_font=dict(color=t["tinta"]),
    )
    if rango is not None:
        eje["range"] = rango
    return eje


def _eje_escena(t: dict, titulo: str) -> dict:
    """Eje de la escena 3D con los colores del tema."""
    return dict(
        title=dict(text=titulo, font=dict(color=t["tinta"], size=12)),
        tickfont=dict(size=10, color=t["suave"]),
        gridcolor=t["rejilla"],
        zerolinecolor=t["borde"],
        linecolor=t["borde"],
        backgroundcolor="rgba(0,0,0,0)",
        showbackground=False,
    )


# --------------------------------------------------------------------------- #
# Región 2D
# --------------------------------------------------------------------------- #
def figura_2d(p: Problema, n: int = 400, tema: str = "claro") -> go.Figure:
    """Dibuja la región plana a rotar, sus guías a, b y el eje de giro."""
    t = _tema(tema)
    xs = np.linspace(p.a, p.b, n)
    fy = p.f_num()(xs)
    es_discos = p.metodo == "discos"
    gy = np.full_like(xs, p.eje) if es_discos else p.g_num()(xs)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=gy,
            mode="lines",
            name="eje de giro" if es_discos else "g(x)",
            line=(
                dict(color=COLOR_EJE, width=1.6, dash="dash")
                if es_discos
                else dict(color=COLOR_INTERIOR, width=2)
            ),
            hovertemplate=(
                "%{y:.4f}<extra>eje de giro</extra>"
                if es_discos
                else "%{y:.4f}<extra>g(x)</extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=fy,
            mode="lines",
            name="f(x)",
            line=dict(color=t["azul"], width=2.4),
            fill="tonexty",
            fillcolor="rgba(30, 111, 168, 0.10)",
            fillpattern=dict(
                shape="/",
                fgcolor="rgba(30, 111, 168, 0.38)",
                fillmode="overlay",
                fgopacity=0.6,
            ),
            hovertemplate="%{y:.4f}<extra>f(x)</extra>",
        )
    )
    if p.metodo == "cascarones":
        fig.add_vline(
            x=p.eje,
            line=dict(color=COLOR_EJE, dash="dash", width=1.4),
            annotation_text=f"eje x = {p.eje:g}",
            annotation_font=dict(size=11, color=t["suave"]),
        )
    elif p.metodo == "arandelas":
        fig.add_hline(
            y=p.eje,
            line=dict(color=COLOR_EJE, dash="dash", width=1.4),
            annotation_text=f"eje y = {p.eje:g}",
            annotation_font=dict(size=11, color=t["suave"]),
        )
    for valor, etiqueta in ((p.a, "a"), (p.b, "b")):
        fig.add_vline(
            x=valor,
            line=dict(color=t["borde"], dash="dot", width=1),
            annotation_text=etiqueta,
            annotation_position="bottom",
            annotation_font=dict(size=11, color=t["suave"]),
        )

    # Rangos con margen para que las curvas no toquen los bordes.
    if p.metodo == "cascarones":
        x_lo, x_hi = min(p.a, p.eje), max(p.b, p.eje)
    else:
        x_lo, x_hi = p.a, p.b
    ys = np.concatenate([fy[np.isfinite(fy)], gy[np.isfinite(gy)]])
    if p.metodo != "cascarones":
        ys = np.append(ys, p.eje)
    y_lo, y_hi = float(np.min(ys)), float(np.max(ys))
    margen_x = 0.04 * ((x_hi - x_lo) or 1.0)
    margen_y = 0.12 * ((y_hi - y_lo) or 1.0)

    fig.update_layout(
        title=dict(
            text="Región plana a rotar",
            x=0,
            xanchor="left",
            font=dict(size=13, color=t["tinta"], family=_FUENTE),
        ),
        font=dict(family=_FUENTE, size=12, color=t["tinta"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=_eje_plano(t, "x", [x_lo - margen_x, x_hi + margen_x]),
        yaxis=_eje_plano(t, "y", [y_lo - margen_y, y_hi + margen_y]),
        legend=dict(
            orientation="h",
            x=1,
            xanchor="right",
            y=1.06,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=t["tinta"]),
        ),
        hovermode="x unified",
        hoverlabel=_hoverlabel(t),
        modebar=_modebar(t),
        height=400,
        margin=dict(l=8, r=14, t=84, b=8),
    )
    return fig


# --------------------------------------------------------------------------- #
# Piezas 3D
# --------------------------------------------------------------------------- #
def _superficie_revolucion(
    p: Problema,
    xs,
    h,
    thetas,
    colorscale,
    nombre: str,
    opacidad: float = 0.9,
):
    """Superficie generada al girar y = h(x), con degradado según el radio al eje."""
    Xg, Tg = np.meshgrid(xs, thetas)
    H = np.tile(h, (len(thetas), 1))
    if p.metodo == "cascarones":
        radios = np.abs(Xg - p.eje)
        X3 = p.eje + (Xg - p.eje) * np.cos(Tg) if p.a >= p.eje else p.eje - radios * np.cos(Tg)
        Z3 = radios * np.sin(Tg)
        Y3 = H
    else:
        radios = np.abs(H - p.eje)
        X3 = Xg
        Y3 = p.eje + (H - p.eje) * np.cos(Tg)
        Z3 = (H - p.eje) * np.sin(Tg)
    finitos = radios[np.isfinite(radios)]
    tope = float(finitos.max()) if finitos.size else 1.0
    return go.Surface(
        x=X3,
        y=Y3,
        z=Z3,
        surfacecolor=radios,
        colorscale=colorscale,
        cmin=0.0,
        cmax=tope or 1.0,
        showscale=False,
        opacity=opacidad,
        name=nombre,
        showlegend=True,
        lighting=dict(
            ambient=0.55, diffuse=0.85, specular=0.25, roughness=0.7, fresnel=0.15
        ),
    )


def _anillo(
    p: Problema, t: float, rho_in: float, rho_out: float, thetas, color: str, nombre: str
):
    """Disco o arandela en el plano x = t (para discos/arandelas)."""
    rhos = np.linspace(rho_in, rho_out, 2)
    R, T = np.meshgrid(rhos, thetas)
    return go.Surface(
        x=np.full_like(R, t),
        y=p.eje + R * np.cos(T),
        z=R * np.sin(T),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=0.9,
        name=nombre,
        showlegend=False,
    )


def _cascaron(
    p: Problema, t: float, y0: float, y1: float, thetas, color: str, nombre: str
):
    """Cilindro hueco (cascarón) a distancia |t − c| del eje x = c."""
    rho = abs(t - p.eje)
    Y, T = np.meshgrid(np.linspace(y0, y1, 2), thetas)
    return go.Surface(
        x=p.eje + rho * np.cos(T),
        y=Y,
        z=rho * np.sin(T),
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=0.9,
        name=nombre,
        showlegend=False,
    )


def _seccion_en(p: Problema, t: float, thetas, color: str, nombre: str):
    fy = float(p.f_num()(np.array([t]))[0])
    gy = float(p.g_num()(np.array([t]))[0]) if p.metodo != "discos" else 0.0
    if p.metodo == "cascarones":
        return _cascaron(p, t, min(fy, gy), max(fy, gy), thetas, color, nombre)
    d_f = abs(fy - p.eje)
    d_g = abs(gy - p.eje) if p.metodo == "arandelas" else 0.0
    if p.metodo == "discos":
        return _anillo(p, t, 0.0, d_f, thetas, color, nombre)
    return _anillo(p, t, min(d_f, d_g), max(d_f, d_g), thetas, color, nombre)


def _contornos_corte(p: Problema, t: float, radios, thetas) -> list[go.Scatter3d]:
    """Contornos circulares (Scatter3d cerrado) de la sección resaltada."""
    ang = np.asarray(thetas, dtype=float)
    trazas = []
    for radio in radios:
        if radio <= 1e-12:
            continue
        trazas.append(
            go.Scatter3d(
                x=[t] * ang.size,
                y=p.eje + radio * np.cos(ang),
                z=radio * np.sin(ang),
                mode="lines",
                line=dict(color="#5FBFAE", width=5),
                hoverinfo="skip",
                showlegend=False,
                name="Contorno",
            )
        )
    return trazas


# --------------------------------------------------------------------------- #
# Figura principal
# --------------------------------------------------------------------------- #
def figura_3d(
    p: Problema,
    angulo: float = 360.0,
    resolucion: int = 60,
    n_secciones: int = 0,
    pos_corte: float | None = None,
    mostrar_solido: bool = True,
    tema: str = "claro",
) -> go.Figure:
    """Construye el sólido 3D.

    ``angulo``: grados girados (0–360) para ver cómo se forma el sólido.
    ``n_secciones``: número de discos/arandelas/cascarones equiespaciados a dibujar.
    ``pos_corte``: posición x de una sección resaltada (verde).
    ``tema``: "claro" u "oscuro" para fuentes, ejes y rejillas.
    """
    t = _tema(tema)
    angulo = float(np.clip(angulo, 1.0, 360.0))
    thetas = np.linspace(0, np.deg2rad(angulo), max(resolucion, 8))
    thetas_completos = np.linspace(0, 2 * np.pi, max(resolucion, 8))
    xs = np.linspace(p.a, p.b, max(resolucion, 8))

    fig = go.Figure()
    fy = p.f_num()(xs)
    gy = p.g_num()(xs)
    opacidad = 0.7 if n_secciones else 0.9

    if mostrar_solido:
        fig.add_trace(
            _superficie_revolucion(
                p, xs, fy, thetas, _COLORESCALA_F, "Superficie f(x)", opacidad
            )
        )
        if p.metodo == "arandelas" or (p.metodo == "cascarones" and np.any(gy != 0)):
            fig.add_trace(
                _superficie_revolucion(
                    p, xs, gy, thetas, _COLORESCALA_G, "Superficie g(x)", opacidad
                )
            )

    if n_secciones > 0:
        dx = (p.b - p.a) / n_secciones
        for i in range(n_secciones):
            t_i = p.a + dx * (i + 0.5)
            seccion = _seccion_en(p, t_i, thetas_completos, COLOR_SECCION, "Sección")
            seccion.opacity = 0.26
            fig.add_trace(seccion)

    if pos_corte is not None:
        corte = float(pos_corte)
        seccion = _seccion_en(p, corte, thetas_completos, COLOR_CORTE, "Sección resaltada")
        seccion.opacity = 0.75
        fig.add_trace(seccion)
        if p.metodo in ("discos", "arandelas"):
            f_corte = float(p.f_num()(np.array([corte]))[0])
            radios = [abs(f_corte - p.eje)]
            if p.metodo == "arandelas":
                radios.append(abs(float(p.g_num()(np.array([corte]))[0]) - p.eje))
            for contorno in _contornos_corte(p, corte, radios, thetas_completos):
                fig.add_trace(contorno)

    # Eje de rotación
    if p.metodo == "cascarones":
        yy = np.concatenate([fy, gy])
        fig.add_trace(
            go.Scatter3d(
                x=[p.eje] * 2,
                y=[float(yy.min()), float(yy.max())],
                z=[0, 0],
                mode="lines",
                line=dict(color=COLOR_EJE, width=5, dash="dash"),
                name="Eje de giro",
            )
        )
    else:
        fig.add_trace(
            go.Scatter3d(
                x=[p.a, p.b],
                y=[p.eje] * 2,
                z=[0, 0],
                mode="lines",
                line=dict(color=COLOR_EJE, width=5, dash="dash"),
                name="Eje de giro",
            )
        )

    fig.update_layout(
        scene=dict(
            aspectmode="data",
            bgcolor="rgba(0,0,0,0)",
            xaxis=_eje_escena(t, "x"),
            yaxis=_eje_escena(t, "y"),
            zaxis=_eje_escena(t, "z"),
            camera=dict(eye=dict(x=0.55, y=1.9, z=0.95)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family=_FUENTE, size=12, color=t["tinta"]),
        hoverlabel=_hoverlabel(t),
        modebar=_modebar(t),
        height=560,
        margin=dict(l=0, r=0, t=34, b=0),
        legend=dict(
            orientation="h",
            x=0,
            y=1.02,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=t["tinta"]),
        ),
    )
    return fig


# --------------------------------------------------------------------------- #
# Convergencia
# --------------------------------------------------------------------------- #
def figura_convergencia(ns, errores, tema: str = "claro") -> go.Figure:
    """Error absoluto de la regla del punto medio frente a n, en escala logarítmica."""
    t = _tema(tema)
    n_arr = np.asarray(ns, dtype=float)
    err = np.maximum(np.asarray(errores, dtype=float), 1e-18)
    fig = go.Figure(
        go.Scatter(
            x=n_arr,
            y=err,
            mode="lines+markers",
            name="Error absoluto",
            line=dict(color=t["azul"], width=2),
            marker=dict(size=6, color=t["azul"]),
            hovertemplate="n = %{x}<br>error = %{y:.2e}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(
            text="Error frente al número de tramos",
            x=0,
            xanchor="left",
            font=dict(size=13, color=t["tinta"], family=_FUENTE),
        ),
        font=dict(family=_FUENTE, size=12, color=t["tinta"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            _eje_plano(t, "n (tramos)"),
            type="log",
        ),
        yaxis=dict(
            _eje_plano(t, "Error absoluto (u³)"),
            type="log",
            exponentformat="power",
        ),
        hovermode="closest",
        hoverlabel=_hoverlabel(t),
        modebar=_modebar(t),
        showlegend=False,
        height=300,
        margin=dict(l=8, r=14, t=52, b=8),
    )
    return fig
