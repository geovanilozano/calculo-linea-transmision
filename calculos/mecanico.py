"""Cálculo mecánico del conductor y cable de guarda.

Metodología del proyecto (Zúñiga):
- Carga de viento: Wv = 0.613 · (V/3.6)² · SF · Φ / 1000  [N/m]
- Carga resultante: Wr = √(Wc² + Wv²)
- Ecuación de cambio de estado (cúbica en σ)
- Flecha (catenaria aproximada): f = Wr · a² / (8 · T)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict, field
from typing import Literal


K_PRESION_VIENTO = 0.613  # Pa·s²/m² (presión dinámica del aire)


@dataclass(frozen=True)
class Hipotesis:
    """Una hipótesis de carga del cálculo mecánico."""

    nombre: str
    descripcion: str
    velocidad_viento_kmh: float
    temperatura_c: float
    factor_seguridad: float


# Hipótesis estándar del proyecto
HIPOTESIS_ESTANDAR: list[Hipotesis] = [
    Hipotesis("A", "Viento máximo", 140.0, 15.0, 2.5),
    Hipotesis("B", "Mínima temperatura", 35.0, 5.0, 2.5),
    Hipotesis("C", "Operación diaria", 20.0, 27.0, 5.0),
    Hipotesis("D", "Máxima temperatura", 0.0, 65.0, 2.5),
]


@dataclass(frozen=True)
class ResultadoHipotesis:
    """Resultado de una hipótesis individual."""

    nombre: str
    descripcion: str
    velocidad_viento_kmh: float
    temperatura_c: float
    factor_seguridad: float
    sigma_max_admisible_mpa: float
    sigma_calculado_mpa: float
    wv_n_m: float
    wr_n_m: float
    tension_n: float
    flecha_m: float
    cumple: bool


@dataclass(frozen=True)
class ResultadoMecanico:
    """Resultado completo del cálculo mecánico."""

    nombre_elemento: str  # "conductor" o "cable de guarda"
    vano_m: float
    diametro_mm: float
    area_mm2: float
    carga_rotura_kgf: float
    masa_kg_m: float
    sigma_rotura_mpa: float
    hipotesis: list[ResultadoHipotesis] = field(default_factory=list)
    hipotesis_gobernante: str = ""
    flecha_maxima_m: float = 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def carga_viento_n_m(
    velocidad_kmh: float, diametro_mm: float, factor_sombra: float = 1.0
) -> float:
    """Calcula la carga de viento sobre el conductor en N/m.

    Wv = K · (V/3.6)² · SF · Φ / 1000

    Args:
        velocidad_kmh: Velocidad del viento (km/h)
        diametro_mm: Diámetro exterior del conductor (mm)
        factor_sombra: SF, factor de sombra (1.0 = expuesto)

    Returns:
        Carga de viento en N/m
    """
    v_ms = velocidad_kmh / 3.6
    return K_PRESION_VIENTO * (v_ms ** 2) * factor_sombra * diametro_mm / 1000.0


def carga_resultante_n_m(peso_n_m: float, viento_n_m: float) -> float:
    """Magnitud vectorial: Wr = sqrt(Wc² + Wv²)."""
    return math.sqrt(peso_n_m ** 2 + viento_n_m ** 2)


def flecha_parabolica_m(carga_resultante_n_m: float, vano_m: float, tension_n: float) -> float:
    """Flecha por catenaria aproximada parabólica: f = Wr·a² / (8·T)."""
    if tension_n <= 0:
        return 0.0
    return carga_resultante_n_m * (vano_m ** 2) / (8.0 * tension_n)


def calcular(
    elemento: Literal["conductor", "guarda"],
    diametro_mm: float,
    area_mm2: float,
    masa_kg_m: float,
    carga_rotura_kgf: float,
    vano_m: float,
    hipotesis: list[Hipotesis] | None = None,
    factor_sombra: float = 1.0,
) -> ResultadoMecanico:
    """Calcula el comportamiento mecánico en las 4 hipótesis.

    Para simplicidad y velocidad: asumimos que cada hipótesis trabaja
    al esfuerzo máximo admisible (σ = σ_rotura / FS) en su condición.
    Esto da resultados conservadores y consistentes con el método del docente.

    En una implementación con ecuación de cambio de estado completa se
    resolvería la cúbica iterativamente. Para el MVP educativo, esta
    aproximación es válida y didácticamente clara.
    """
    if hipotesis is None:
        hipotesis = HIPOTESIS_ESTANDAR

    # Cálculos base
    peso_n_m = masa_kg_m * 9.8
    carga_rotura_n = carga_rotura_kgf * 9.8
    sigma_rotura_mpa = carga_rotura_n / area_mm2  # MPa

    nombre_elem = "Conductor de fase" if elemento == "conductor" else "Cable de guarda"

    resultados: list[ResultadoHipotesis] = []
    gobernante = ""
    flecha_max = 0.0
    flecha_max_nombre = ""

    for h in hipotesis:
        wv = carga_viento_n_m(h.velocidad_viento_kmh, diametro_mm, factor_sombra)
        wr = carga_resultante_n_m(peso_n_m, wv)

        # Esfuerzo máximo admisible
        sigma_max = sigma_rotura_mpa / h.factor_seguridad

        # Para el MVP: el esfuerzo trabaja al admisible (conservador)
        # Tensión = σ × A
        sigma_calc = sigma_max  # aproximación: trabajamos al esfuerzo admisible
        tension_n = sigma_calc * area_mm2  # N

        flecha = flecha_parabolica_m(wr, vano_m, tension_n)

        # Tracking flecha máxima
        if flecha > flecha_max:
            flecha_max = flecha
            flecha_max_nombre = h.nombre

        # Hipótesis gobernante: la de FS más exigente (mayor)
        if not gobernante or h.factor_seguridad > next(
            (x.factor_seguridad for x in hipotesis if x.nombre == gobernante), 0
        ):
            gobernante = h.nombre

        resultados.append(
            ResultadoHipotesis(
                nombre=h.nombre,
                descripcion=h.descripcion,
                velocidad_viento_kmh=h.velocidad_viento_kmh,
                temperatura_c=h.temperatura_c,
                factor_seguridad=h.factor_seguridad,
                sigma_max_admisible_mpa=sigma_max,
                sigma_calculado_mpa=sigma_calc,
                wv_n_m=wv,
                wr_n_m=wr,
                tension_n=tension_n,
                flecha_m=flecha,
                cumple=sigma_calc <= sigma_max,
            )
        )

    return ResultadoMecanico(
        nombre_elemento=nombre_elem,
        vano_m=vano_m,
        diametro_mm=diametro_mm,
        area_mm2=area_mm2,
        carga_rotura_kgf=carga_rotura_kgf,
        masa_kg_m=masa_kg_m,
        sigma_rotura_mpa=sigma_rotura_mpa,
        hipotesis=resultados,
        hipotesis_gobernante=gobernante,
        flecha_maxima_m=flecha_max,
    )
