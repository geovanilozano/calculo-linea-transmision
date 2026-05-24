"""Cálculo de distancias geométricas de la línea: GMD, GMR_L, GMR_C, RMG corona.

Para una línea trifásica con haz de subconductores:
- GMD: Distancia Media Geométrica entre fases  = (D12·D23·D13)^(1/3)
- GMR_L: Radio Medio Geométrico para inductancia (incluye factor 0.7788)
- GMR_C: Radio Medio Geométrico para capacitancia (usa radio físico real)
- RMG corona: Radio efectivo del haz para análisis de efecto corona
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ResultadoGeometria:
    """Resultado del cálculo geométrico de la línea."""

    d12_m: float
    d23_m: float
    d13_m: float
    n_subconductores: int
    db_m: float
    r_conductor_mm: float
    gmr_subconductor_mm: float

    # Resultados
    gmd_m: float
    gmr_l_m: float
    gmr_c_m: float
    radio_circulo_envolvente_m: float
    rmg_corona_m: float
    triangulo_valido: bool
    advertencias: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def es_triangulo_valido(d12: float, d23: float, d13: float) -> bool:
    """Verifica si las 3 distancias forman un triángulo válido (desigualdad triangular).

    Se acepta el caso degenerado colineal (suma de los 2 menores = mayor),
    típico de configuración horizontal plana en líneas de transmisión.
    """
    lados = sorted([d12, d23, d13])
    return lados[0] + lados[1] >= lados[2] and all(l > 0 for l in lados)


def gmd(d12: float, d23: float, d13: float) -> float:
    """Distancia Media Geométrica entre fases.

    Args:
        d12, d23, d13: Distancias entre las 3 parejas de fases (m)

    Returns:
        GMD en metros
    """
    return (d12 * d23 * d13) ** (1.0 / 3.0)


def gmr_haz_inductancia(gmr_subconductor_m: float, n_subc: int, db_m: float) -> float:
    """GMR del haz para cálculo de inductancia.

    Para haz simétrico de n subconductores equidistantes a un radio R del centro:
    GMR_L = (n · GMR_sub · R^(n-1))^(1/n)

    Para el caso más común (haz triangular equilátero, n=3):
    GMR_L = (GMR_sub · db^2)^(1/3)

    Args:
        gmr_subconductor_m: GMR del subconductor individual (m), incluye factor 0.7788
        n_subc: Número de subconductores en el haz (1, 2, 3 o 4)
        db_m: Separación entre subconductores adyacentes del haz (m)

    Returns:
        GMR del haz para inductancia, en metros
    """
    if n_subc == 1:
        return gmr_subconductor_m
    elif n_subc == 2:
        return math.sqrt(gmr_subconductor_m * db_m)
    elif n_subc == 3:
        return (gmr_subconductor_m * db_m * db_m) ** (1.0 / 3.0)
    elif n_subc == 4:
        # Haz cuadrado: distancia diagonal = db * sqrt(2)
        return 1.0905 * (gmr_subconductor_m * (db_m ** 3)) ** (1.0 / 4.0)
    else:
        raise ValueError(f"Número de subconductores no soportado: {n_subc}")


def gmr_haz_capacitancia(r_conductor_m: float, n_subc: int, db_m: float) -> float:
    """GMR del haz para cálculo de capacitancia.

    Misma fórmula que inductancia pero usando radio físico (r), no GMR efectivo.

    Args:
        r_conductor_m: Radio físico del conductor (m)
        n_subc: Número de subconductores
        db_m: Separación entre subconductores adyacentes (m)

    Returns:
        GMR del haz para capacitancia, en metros
    """
    if n_subc == 1:
        return r_conductor_m
    elif n_subc == 2:
        return math.sqrt(r_conductor_m * db_m)
    elif n_subc == 3:
        return (r_conductor_m * db_m * db_m) ** (1.0 / 3.0)
    elif n_subc == 4:
        return 1.0905 * (r_conductor_m * (db_m ** 3)) ** (1.0 / 4.0)
    else:
        raise ValueError(f"Número de subconductores no soportado: {n_subc}")


def radio_circulo_envolvente(n_subc: int, db_m: float) -> float:
    """Radio del círculo circunscrito al haz.

    - n=1: r = 0 (no aplica)
    - n=2: r = db/2
    - n=3 (triángulo equilátero): r = db/sqrt(3)
    - n=4 (cuadrado): r = db/sqrt(2)
    """
    if n_subc == 1:
        return 0.0
    elif n_subc == 2:
        return db_m / 2.0
    elif n_subc == 3:
        return db_m / math.sqrt(3.0)
    elif n_subc == 4:
        return db_m / math.sqrt(2.0)
    else:
        raise ValueError(f"Número de subconductores no soportado: {n_subc}")


def calcular(
    d12_m: float,
    d23_m: float,
    d13_m: float,
    n_subc: int,
    db_m: float,
    r_conductor_mm: float,
    gmr_subconductor_mm: float,
) -> ResultadoGeometria:
    """Calcula todas las distancias geométricas de la línea.

    Args:
        d12_m, d23_m, d13_m: Distancias entre fases (m)
        n_subc: Número de subconductores en el haz
        db_m: Separación entre subconductores adyacentes (m)
        r_conductor_mm: Radio físico del subconductor (mm)
        gmr_subconductor_mm: GMR de tabla del subconductor (mm) — ya incluye 0.7788

    Returns:
        ResultadoGeometria con todos los cálculos
    """
    # Validaciones básicas
    advertencias = []
    valido = es_triangulo_valido(d12_m, d23_m, d13_m)
    if not valido:
        advertencias.append(
            "Las distancias D12, D23, D13 NO forman un triángulo válido "
            "(desigualdad triangular incumplida). Verifica los valores."
        )

    if n_subc < 1 or n_subc > 4:
        raise ValueError(f"n_subc debe ser 1, 2, 3 o 4 (recibido: {n_subc})")

    if n_subc > 1 and db_m <= 0:
        raise ValueError("db_m debe ser positivo cuando n_subc > 1")

    # Conversiones a metros
    r_m = r_conductor_mm / 1000.0
    gmr_sub_m = gmr_subconductor_mm / 1000.0

    # Cálculos principales (GMD se calcula siempre que las distancias sean positivas)
    _gmd = gmd(d12_m, d23_m, d13_m) if all(d > 0 for d in (d12_m, d23_m, d13_m)) else 0.0
    _gmr_l = gmr_haz_inductancia(gmr_sub_m, n_subc, db_m)
    _gmr_c = gmr_haz_capacitancia(r_m, n_subc, db_m)
    _r_env = radio_circulo_envolvente(n_subc, db_m)
    # RMG corona = GMR del haz para capacitancia (usa radio físico)
    _rmg_corona = _gmr_c

    return ResultadoGeometria(
        d12_m=d12_m,
        d23_m=d23_m,
        d13_m=d13_m,
        n_subconductores=n_subc,
        db_m=db_m,
        r_conductor_mm=r_conductor_mm,
        gmr_subconductor_mm=gmr_subconductor_mm,
        gmd_m=_gmd,
        gmr_l_m=_gmr_l,
        gmr_c_m=_gmr_c,
        radio_circulo_envolvente_m=_r_env,
        rmg_corona_m=_rmg_corona,
        triangulo_valido=valido,
        advertencias=advertencias,
    )
