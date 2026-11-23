"""Genera los comandos de GeoGebra que dibujan el mismo sólido que el simulador.

Los comandos se pueden:
  * pegar uno por uno en la barra de entrada de GeoGebra 3D (geogebra.org/3d), o
  * ejecutar automáticamente en el applet incrustado en la aplicación.

La geometría es la misma que usa ``visual.py``:
  * Discos / arandelas: giro alrededor de la recta horizontal y = c.
  * Cascarones: giro alrededor de la recta vertical x = c.
"""

from __future__ import annotations

import json

import sympy as sp

from .calculo import Problema


def _gg(expr: sp.Expr) -> str:
    """Convierte una expresión de SymPy a la sintaxis de GeoGebra."""
    return str(expr).replace("**", "^")


def _num(x: float) -> str:
    return f"{x:g}"


def comandos_geogebra(p: Problema) -> list[str]:
    """Lista de comandos de GeoGebra (en orden) para construir el sólido de ``p``."""
    cmds = [
        f"a = {_num(p.a)}",
        f"b = {_num(p.b)}",
        f"c = {_num(p.eje)}",
        f"f(x) = {_gg(p.f)}",
    ]
    con_g = p.metodo != "discos"
    if con_g:
        cmds.append(f"g(x) = {_gg(p.g)}")
    cmds += [
        "giro = Slider(0, 2pi, 0.05)",
        "SetValue(giro, 2pi)",
        f"t = Slider(a, b, 0.01)",
        "SetValue(t, (a + b) / 2)",
    ]

    if p.metodo == "discos":
        cmds += [
            "Solido = Surface(u, c + (f(u) - c) * cos(v), (f(u) - c) * sin(v), u, a, b, v, 0, giro)",
            "Disco = Surface(t, c + s * (f(t) - c) * cos(v), s * (f(t) - c) * sin(v), s, 0, 1, v, 0, 2pi)",
            "V = pi * Integral((f(x) - c)^2, a, b)",
        ]
    elif p.metodo == "arandelas":
        cmds += [
            "SolidoExterior = Surface(u, c + (f(u) - c) * cos(v), (f(u) - c) * sin(v), u, a, b, v, 0, giro)",
            "SolidoInterior = Surface(u, c + (g(u) - c) * cos(v), (g(u) - c) * sin(v), u, a, b, v, 0, giro)",
            "R = abs(f(t) - c)",
            "r = abs(g(t) - c)",
            "Arandela = Surface(t, c + (min(r, R) + s * abs(R - r)) * cos(v), (min(r, R) + s * abs(R - r)) * sin(v), s, 0, 1, v, 0, 2pi)",
            "V = abs(pi * Integral((f(x) - c)^2 - (g(x) - c)^2, a, b))",
        ]
    else:  # cascarones: giro alrededor de la recta vertical x = c
        if not con_g:
            raise ValueError("Cascarones requiere g(x).")
        cmds += [
            "Solido = Surface(c + (u - c) * cos(v), f(u), (u - c) * sin(v), u, a, b, v, 0, giro)",
            "Cascaron = Surface(c + (t - c) * cos(v), w, (t - c) * sin(v), w, g(t), f(t), v, 0, 2pi)",
            "V = 2 * pi * Integral((x - c) * (f(x) - g(x)), a, b)",
        ]
    return cmds


def html_applet(comandos: list[str], alto: int = 600) -> str:
    """HTML con el applet de GeoGebra 3D que ejecuta ``comandos`` al cargar.

    Requiere conexión a internet (carga ``deployggb.js`` desde geogebra.org).
    """
    cmds_json = json.dumps(comandos)
    return f"""
<div class="ggb-escala" style="position:relative;width:100%;height:{alto}px;">
  <div id="ggb-contenedor" style="width:100%;height:100%"></div>
</div>
<script src="https://www.geogebra.org/apps/deployggb.js"></script>
<script>
  var comandos = {cmds_json};
  var params = {{
    appName: "3d",
    width: 900, height: {alto},
    showToolBar: false, showAlgebraInput: false, showMenuBar: false,
    showAlgebraView: false,
    enableRightClick: true, enableShiftDragZoom: true,
    scaleContainerClass: "ggb-escala",
    appletOnLoad: function (api) {{
      comandos.forEach(function (c) {{ api.evalCommand(c); }});
      try {{ api.setPerspective("T"); }} catch (e) {{}}
    }}
  }};
  var applet = new GGBApplet(params, true);
  window.addEventListener("load", function () {{ applet.inject("ggb-contenedor"); }});
</script>
"""
