"""Simulador de sólidos de revolución: cálculo, ejemplos y visualización 3D."""

from .calculo import Problema, Resultado, calcular, parse_funcion
from .ejemplos import EJEMPLOS

__all__ = ["Problema", "Resultado", "calcular", "parse_funcion", "EJEMPLOS"]
