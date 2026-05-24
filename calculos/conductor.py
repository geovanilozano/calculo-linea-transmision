"""Cálculos asociados al conductor seleccionado.

Para el proyecto se usa ACSR Drake 795 kcmil. Este módulo expone:
- Resistencia AC equivalente por fase (haz en paralelo)
- Corrección de resistencia por temperatura
- Estimación simple de ampacidad por sobrecalentamiento (IEEE 738 simplificado)
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


# Coeficiente de temperatura del aluminio (ACSR)
ALPHA_AL = 0.00403  # 1/°C, típico para conductores aluminio
TEMPERATURA_REFERENCIA_C = 65.0  # temperatura a la cual está dada la R en tabla


@dataclass(frozen=True)
class ResultadoConductor:
    """Resultado del análisis del conductor seleccionado."""

    n_subc: int
    resistencia_subc_ohm_km: float
    resistencia_fase_ohm_km: float
    resistencia_total_fase_ohm: float  # para la línea completa
    ampacidad_subc_a: float
    ampacidad_fase_a: float
    longitud_km: float
    temperatura_op_c: float

    def to_dict(self) -> dict:
        return asdict(self)


def resistencia_corregida_por_temperatura(
    r_referencia: float, t_referencia_c: float, t_operacion_c: float
) -> float:
    """Ajusta resistencia AC a la temperatura de operación.

    R(T) = R_ref * (1 + α · (T - T_ref))
    """
    return r_referencia * (1.0 + ALPHA_AL * (t_operacion_c - t_referencia_c))


def calcular(
    resistencia_subc_ohm_km: float,
    ampacidad_subc_a: float,
    n_subc: int,
    longitud_km: float,
    temperatura_op_c: float = TEMPERATURA_REFERENCIA_C,
) -> ResultadoConductor:
    """Calcula los parámetros del conductor agrupado en haz.

    Args:
        resistencia_subc_ohm_km: Resistencia AC de un subconductor a T_referencia (Ω/km)
        ampacidad_subc_a: Ampacidad nominal de un subconductor (A)
        n_subc: Número de subconductores en el haz
        longitud_km: Longitud total de la línea (km)
        temperatura_op_c: Temperatura de operación (°C), por defecto = T_referencia

    Returns:
        ResultadoConductor con los parámetros calculados
    """
    if n_subc < 1:
        raise ValueError("n_subc debe ser >= 1")
    if longitud_km <= 0:
        raise ValueError("longitud_km debe ser > 0")

    # Resistencia ajustada por temperatura
    r_subc_op = resistencia_corregida_por_temperatura(
        resistencia_subc_ohm_km, TEMPERATURA_REFERENCIA_C, temperatura_op_c
    )

    # Resistencia equivalente del haz: n subconductores en paralelo
    r_fase = r_subc_op / n_subc

    # Resistencia total de la línea (por fase)
    r_total = r_fase * longitud_km

    # Ampacidad por fase: n veces la de un subconductor
    i_fase = ampacidad_subc_a * n_subc

    return ResultadoConductor(
        n_subc=n_subc,
        resistencia_subc_ohm_km=r_subc_op,
        resistencia_fase_ohm_km=r_fase,
        resistencia_total_fase_ohm=r_total,
        ampacidad_subc_a=ampacidad_subc_a,
        ampacidad_fase_a=i_fase,
        longitud_km=longitud_km,
        temperatura_op_c=temperatura_op_c,
    )
