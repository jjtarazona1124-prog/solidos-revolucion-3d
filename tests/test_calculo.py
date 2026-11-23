import math

import pytest

from solidos.calculo import Problema, calcular, parse_funcion, riemann_punto_medio
from solidos.ejemplos import EJEMPLOS, problema_desde_ejemplo


@pytest.mark.parametrize("nombre", list(EJEMPLOS))
def test_ejemplos_coinciden_con_solucion_analitica(nombre):
    r = calcular(problema_desde_ejemplo(nombre), n_riemann=500)
    esperado = EJEMPLOS[nombre]["valor_analitico"]
    assert r.exacto == pytest.approx(esperado, rel=1e-9)
    assert r.cuadratura == pytest.approx(esperado, rel=1e-9)
    assert r.riemann == pytest.approx(esperado, rel=1e-4)


def test_valores_exactos_de_los_ejemplos():
    discos, arandelas, cascarones = (calcular(problema_desde_ejemplo(n)).exacto for n in EJEMPLOS)
    assert discos == pytest.approx(15 * math.pi / 2)
    assert arandelas == pytest.approx(104 * math.pi / 15)
    assert cascarones == pytest.approx(16 * math.pi / 15)


def test_cascaron_cilindro():
    # f(x)=2 en [0,1], eje x=0: V = 2π ∫ x·2 dx = 2π
    r = calcular(Problema("cascarones", parse_funcion("2"), a=0, b=1))
    assert r.exacto == pytest.approx(2 * math.pi)


def test_cascaron_eje_no_cruza_region():
    with pytest.raises(ValueError):
        Problema("cascarones", parse_funcion("x"), a=0, b=2, eje=1)


def test_cascarones_equivalen_a_arandelas_en_un_caso_simple():
    # Región bajo y=x² en [0,1] girada alrededor del eje Y:
    # cascarones: 2π ∫ x·x² dx = π/2
    r = calcular(Problema("cascarones", parse_funcion("x**2"), a=0, b=1))
    assert r.exacto == pytest.approx(math.pi / 2)


def test_disco_cilindro():
    # f(x)=2 en [0,3] -> cilindro radio 2, altura 3: V = 12π
    r = calcular(Problema("discos", parse_funcion("2"), a=0, b=3))
    assert r.exacto == pytest.approx(12 * math.pi)


def test_disco_con_eje_desplazado():
    # f(x)=3 girando alrededor de y=1 en [0,2] -> radio 2, altura 2: V = 8π
    r = calcular(Problema("discos", parse_funcion("3"), a=0, b=2, eje=1))
    assert r.exacto == pytest.approx(8 * math.pi)


def test_arandela_cilindro_hueco():
    # entre y=3 y y=1 en [0,2], eje y=0: π(9-1)·2 = 16π
    r = calcular(Problema("arandelas", parse_funcion("3"), parse_funcion("1"), 0, 2))
    assert r.exacto == pytest.approx(16 * math.pi)


def test_arandela_orienta_signo():
    # Intercambiar f y g no cambia el volumen
    p1 = Problema("arandelas", parse_funcion("2*x"), parse_funcion("x**2"), 0, 2, eje=-1)
    p2 = Problema("arandelas", parse_funcion("x**2"), parse_funcion("2*x"), 0, 2, eje=-1)
    assert calcular(p1).exacto == pytest.approx(calcular(p2).exacto)


def test_metodo_invalido():
    with pytest.raises(ValueError):
        Problema("esferas", parse_funcion("x"), a=0, b=1)


def test_limites_invalidos():
    with pytest.raises(ValueError):
        Problema("discos", parse_funcion("x"), a=2, b=1)


def test_riemann_converge():
    p = problema_desde_ejemplo(list(EJEMPLOS)[1])
    r = calcular(p)
    e10 = abs(riemann_punto_medio(r.integrando, p.a, p.b, 10) - r.exacto)
    e100 = abs(riemann_punto_medio(r.integrando, p.a, p.b, 100) - r.exacto)
    assert e100 < e10


@pytest.mark.parametrize("malo", ["", "__import__('os')", "x; y", "open('f')", "y+1", "[1]"])
def test_parse_rechaza_entradas_peligrosas_o_invalidas(malo):
    with pytest.raises(ValueError):
        parse_funcion(malo)


def test_parse_acepta_notaciones_comunes():
    assert parse_funcion("3x^2 + sin(x)")  # multiplicación implícita y ^
    assert parse_funcion("exp(-x/2)*sqrt(x)")
