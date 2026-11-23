"""Motor de cálculo: volumen exacto (SymPy) y aproximaciones numéricas (SciPy/NumPy).

Convenciones
------------
* Discos / Arandelas: la región se gira alrededor de la recta horizontal ``y = eje``
  (``eje = 0`` es el eje X).
* Cascarones: la región entre ``g(x)`` y ``f(x)`` se gira alrededor de la recta
  vertical ``x = eje`` (``eje = 0`` es el eje Y).

Fórmulas
--------
* Discos:     V = π ∫ (f(x) − c)² dx
* Arandelas:  V = π ∫ |(f(x) − c)² − (g(x) − c)²| dx
* Cascarones: V = 2π ∫ |x − c| · (f(x) − g(x)) dx
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import sympy as sp
from scipy import integrate
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

X = sp.Symbol("x", real=True)

METODOS = ("discos", "arandelas", "cascarones")

_TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)
_CARACTERES_PERMITIDOS = re.compile(r"^[0-9A-Za-z_+\-*/^().,\s]*$")


# --------------------------------------------------------------------------- #
# Lectura segura de funciones escritas por el usuario
# --------------------------------------------------------------------------- #
def parse_funcion(texto: str) -> sp.Expr:
    """Convierte un texto como ``"sqrt(x)*exp(-x/2)"`` en una expresión SymPy.

    Solo acepta caracteres matemáticos básicos (sin guiones bajos dobles, comillas,
    corchetes ni punto y coma) para evitar ejecución de código arbitrario.
    """
    texto = (texto or "").strip()
    if not texto:
        raise ValueError("La función no puede estar vacía.")
    if not _CARACTERES_PERMITIDOS.match(texto) or "__" in texto:
        raise ValueError("La función contiene caracteres no permitidos.")
    try:
        expr = parse_expr(
            texto,
            local_dict={"x": X, "pi": sp.pi, "e": sp.E},
            transformations=_TRANSFORMACIONES,
        )
    except Exception as exc:  # noqa: BLE001 - se re-lanza con mensaje claro
        raise ValueError(f"No se pudo interpretar la función: {exc}") from exc
    expr = sp.sympify(expr)
    libres = expr.free_symbols - {X}
    if libres:
        nombres = ", ".join(sorted(str(s) for s in libres))
        raise ValueError(f"Solo se permite la variable x (encontrado: {nombres}).")
    return expr


def _a_numero(valor) -> sp.Expr:
    return sp.nsimplify(valor, rational=True)


# --------------------------------------------------------------------------- #
# Modelo del problema
# --------------------------------------------------------------------------- #
@dataclass
class Problema:
    metodo: str
    f: sp.Expr
    g: sp.Expr = field(default_factory=lambda: sp.Integer(0))
    a: float = 0.0
    b: float = 1.0
    eje: float = 0.0

    def __post_init__(self) -> None:
        if self.metodo not in METODOS:
            raise ValueError(f"Método inválido: {self.metodo!r}. Usa uno de {METODOS}.")
        self.f = sp.sympify(self.f)
        self.g = sp.sympify(self.g)
        if not self.a < self.b:
            raise ValueError("Se requiere a < b.")
        if self.metodo == "cascarones" and self.a < self.eje < self.b:
            raise ValueError(
                "El eje de giro x = c no puede cruzar la región (a < c < b). "
                "Divide el problema en dos regiones."
            )

    # -- funciones numéricas -------------------------------------------------
    def f_num(self):
        return _lambdificar(self.f)

    def g_num(self):
        return _lambdificar(self.g)

    # -- integrando simbólico ------------------------------------------------
    def integrando(self) -> sp.Expr:
        c = _a_numero(self.eje)
        if self.metodo == "discos":
            return sp.pi * (self.f - c) ** 2
        if self.metodo == "arandelas":
            dif = (self.f - c) ** 2 - (self.g - c) ** 2
            return sp.pi * self._orientar(dif)
        # cascarones
        radio = (X - c) if self.a >= self.eje else (c - X)
        return 2 * sp.pi * radio * (self.f - self.g)

    def _orientar(self, dif: sp.Expr) -> sp.Expr:
        """Devuelve ``dif`` con el signo que lo hace positivo en [a, b]."""
        xs = np.linspace(self.a, self.b, 201)
        vals = _lambdificar(dif)(xs)
        if np.all(vals >= -1e-9):
            return dif
        if np.all(vals <= 1e-9):
            return -dif
        raise ValueError(
            "Las curvas f(x) y g(x) están a distancias que se cruzan respecto al eje "
            "dentro de [a, b]; separa el problema en subintervalos."
        )


def _lambdificar(expr: sp.Expr):
    fn = sp.lambdify(X, expr, modules=["numpy"])

    def evaluar(x):
        x_arr = np.asarray(x, dtype=float)
        with np.errstate(all="ignore"):
            y = fn(x_arr)
        return np.broadcast_to(np.asarray(y, dtype=float), x_arr.shape).copy()

    return evaluar


# --------------------------------------------------------------------------- #
# Resultado
# --------------------------------------------------------------------------- #
@dataclass
class Resultado:
    integrando: sp.Expr
    antiderivada: sp.Expr | None
    exacto_simbolico: sp.Expr | None
    exacto: float | None
    cuadratura: float
    riemann: float
    n_riemann: int

    @property
    def error_absoluto(self) -> float | None:
        if self.exacto is None:
            return None
        return abs(self.riemann - self.exacto)

    @property
    def error_relativo(self) -> float | None:
        if self.exacto is None or self.exacto == 0:
            return None
        return self.error_absoluto / abs(self.exacto)


def riemann_punto_medio(integrando: sp.Expr, a: float, b: float, n: int) -> float:
    """Aproximación por suma de Riemann con punto medio y ``n`` secciones."""
    if n < 1:
        raise ValueError("n debe ser ≥ 1.")
    dx = (b - a) / n
    medios = a + dx * (np.arange(n) + 0.5)
    return float(np.sum(_lambdificar(integrando)(medios)) * dx)


def calcular(p: Problema, n_riemann: int = 100) -> Resultado:
    """Calcula el volumen exacto (simbólico) y dos aproximaciones numéricas."""
    integrando = p.integrando()
    a, b = _a_numero(p.a), _a_numero(p.b)

    antiderivada = None
    exacto_simbolico = None
    exacto = None
    try:
        anti = sp.integrate(integrando, X)
        if not anti.has(sp.Integral):
            antiderivada = sp.simplify(anti)
            exacto_simbolico = sp.simplify(antiderivada.subs(X, b) - antiderivada.subs(X, a))
            exacto = float(sp.N(exacto_simbolico, 15))
    except Exception:  # noqa: BLE001 - si SymPy no puede, se usa solo lo numérico
        pass

    f_int = _lambdificar(integrando)
    cuadratura, _ = integrate.quad(lambda t: float(f_int(t)), p.a, p.b, limit=200)
    riemann = riemann_punto_medio(integrando, p.a, p.b, n_riemann)

    return Resultado(
        integrando=integrando,
        antiderivada=antiderivada,
        exacto_simbolico=exacto_simbolico,
        exacto=exacto,
        cuadratura=float(cuadratura),
        riemann=riemann,
        n_riemann=n_riemann,
    )
