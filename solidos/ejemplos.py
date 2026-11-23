"""Ejemplos contextualizados (uno por método) con su solución analítica."""

from __future__ import annotations

import math

from .calculo import Problema, parse_funcion

EJEMPLOS = {
    "Ejemplo 1 · Discos — Núcleo de fibra óptica cónica": {
        "programa": "Ingeniería de Sistemas",
        "metodo": "discos",
        "contexto": (
            "El radio del núcleo de un tramo de fibra óptica de perfil cónico es "
            "f(x) = √(x + 1), con x ∈ [0, 3] cm. Al girar la región alrededor del eje "
            "del cable (eje X) se obtiene el volumen del núcleo."
        ),
        "f": "sqrt(x+1)",
        "g": "0",
        "a": 0.0,
        "b": 3.0,
        "eje": 0.0,
        "solucion_latex": (
            r"V=\pi\int_0^3\left[\sqrt{x+1}\right]^2dx=\pi\int_0^3 (x+1)\,dx"
            r"=\pi\left[\tfrac{x^2}{2}+x\right]_0^3=\pi\left(\tfrac92+3\right)=\frac{15\pi}{2}"
        ),
        "valor_analitico": 15 * math.pi / 2,
    },
    "Ejemplo 2 · Arandelas — Pieza de blindaje hueca": {
        "programa": "Ingeniería Electrónica",
        "metodo": "arandelas",
        "contexto": (
            "Un componente de blindaje tiene una sección limitada por y = 2x (arriba) y "
            "y = x² (abajo), con x ∈ [0, 2] cm, y se gira alrededor del eje auxiliar "
            "y = −1. Los radios se miden desde ese eje: R(x) = 2x + 1 y r(x) = x² + 1."
        ),
        "f": "2*x",
        "g": "x**2",
        "a": 0.0,
        "b": 2.0,
        "eje": -1.0,
        "solucion_latex": (
            r"V=\pi\int_0^2\left[(2x+1)^2-(x^2+1)^2\right]dx"
            r"=\pi\int_0^2\left(-x^4+2x^2+4x\right)dx"
            r"=\pi\left[-\tfrac{x^5}{5}+\tfrac{2x^3}{3}+2x^2\right]_0^2=\frac{104\pi}{15}"
        ),
        "valor_analitico": 104 * math.pi / 15,
    },
    "Ejemplo 3 · Cascarones — Disipador de calor para servidor": {
        "programa": "Ingeniería de Sistemas",
        "metodo": "cascarones",
        "contexto": (
            "Un disipador de calor circular para servidor tiene una altura que crece con la "
            "distancia r al centro según h(r) = r³ + r, con r ∈ [0, 1] cm. Al girar la región "
            "bajo la curva alrededor del eje Y (eje central) se obtiene el volumen de aluminio. "
            "Por arandelas habría que despejar x de y = x³ + x; por cascarones la integral es directa."
        ),
        "f": "x**3 + x",
        "g": "0",
        "a": 0.0,
        "b": 1.0,
        "eje": 0.0,
        "solucion_latex": (
            r"V=2\pi\int_0^1 x\,(x^3+x)\,dx=2\pi\int_0^1 (x^4+x^2)\,dx"
            r"=2\pi\left[\tfrac{x^5}{5}+\tfrac{x^3}{3}\right]_0^1=2\pi\cdot\frac{8}{15}=\frac{16\pi}{15}"
        ),
        "valor_analitico": 16 * math.pi / 15,
    },
}


def problema_desde_ejemplo(nombre: str) -> Problema:
    e = EJEMPLOS[nombre]
    return Problema(
        metodo=e["metodo"],
        f=parse_funcion(e["f"]),
        g=parse_funcion(e["g"]),
        a=e["a"],
        b=e["b"],
        eje=e["eje"],
    )
