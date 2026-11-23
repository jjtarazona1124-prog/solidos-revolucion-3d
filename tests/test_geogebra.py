import pytest

from solidos.ejemplos import EJEMPLOS, problema_desde_ejemplo
from solidos.geogebra import comandos_geogebra, html_applet


@pytest.mark.parametrize("nombre", list(EJEMPLOS))
def test_comandos_basicos(nombre):
    cmds = comandos_geogebra(problema_desde_ejemplo(nombre))
    texto = "\\n".join(cmds)
    assert cmds[0].startswith("a = ") and cmds[1].startswith("b = ")
    assert any(c.startswith("f(x) = ") for c in cmds)
    assert "Surface(" in texto and "Integral(" in texto
    assert "**" not in texto  # GeoGebra usa ^
    assert any(c.startswith("V = ") for c in cmds)


def test_funcion_se_convierte_a_sintaxis_geogebra():
    cmds = comandos_geogebra(problema_desde_ejemplo(list(EJEMPLOS)[2]))
    assert "f(x) = x^3 + x" in cmds


def test_eje_desplazado_en_arandelas():
    cmds = comandos_geogebra(problema_desde_ejemplo(list(EJEMPLOS)[1]))
    assert "c = -1" in cmds


def test_html_incluye_comandos_y_script():
    html = html_applet(["a = 1"])
    assert "deployggb.js" in html and "a = 1" in html
