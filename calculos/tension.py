"""Cálculo del nivel de tensión por tres criterios empíricos.

Criterios:
- Hefner: V = 0.1 * sqrt(P * L)
- Still:  V = 5.5 * sqrt(L/1.609 + P/100)
- 1 kV / km: V = L

Donde P en kW y L en km. Retorna V en kV.

Escalones normalizados en Colombia (RETIE): 115 / 230 / 500 kV
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict


ESCALONES_NORMALIZADOS_KV: tuple[int, ...] = (115, 230, 500)


@dataclass(frozen=True)
class ResultadoTension:
    """Resultado del cálculo de tensión por los tres criterios."""

    potencia_mw: float
    longitud_km: float
    hefner_kv: float
    still_kv: float
    regla_1kvkm_kv: float
    tension_recomendada_kv: int
    justificacion: str

    def to_dict(self) -> dict:
        return asdict(self)


def hefner(potencia_mw: float, longitud_km: float) -> float:
    """Criterio de Hefner.

    Args:
        potencia_mw: Potencia activa a transmitir (MW)
        longitud_km: Longitud total de la línea (km)

    Returns:
        Tensión recomendada en kV (línea-línea)
    """
    potencia_kw = potencia_mw * 1000.0
    return 0.1 * math.sqrt(potencia_kw * longitud_km)


def still(potencia_mw: float, longitud_km: float) -> float:
    """Criterio de Still.

    Args:
        potencia_mw: Potencia activa a transmitir (MW)
        longitud_km: Longitud total de la línea (km)

    Returns:
        Tensión recomendada en kV (línea-línea)
    """
    potencia_kw = potencia_mw * 1000.0
    return 5.5 * math.sqrt(longitud_km / 1.609 + potencia_kw / 100.0)


def regla_1_kv_por_km(longitud_km: float) -> float:
    """Regla empírica simple: 1 kV por cada kilómetro de línea."""
    return float(longitud_km)


def seleccionar_escalon_normalizado(criterios_kv: list[float]) -> tuple[int, str]:
    """Selecciona el escalón normalizado adecuado.

    Regla: el escalón seleccionado debe ser >= al máximo de los tres criterios.

    Args:
        criterios_kv: Lista de los valores calculados por cada criterio (en kV)

    Returns:
        Tupla (escalón_seleccionado_kV, justificación_texto)
    """
    valor_minimo_necesario = max(criterios_kv)

    # Buscar el primer escalón normalizado que cumpla
    for escalon in ESCALONES_NORMALIZADOS_KV:
        if escalon >= valor_minimo_necesario:
            return escalon, (
                f"Los tres criterios arrojan valores hasta {valor_minimo_necesario:.0f} kV. "
                f"El escalón normalizado más bajo que cumple es {escalon} kV."
            )

    # Si supera 500 kV (caso raro), recomendar 500 + nota
    return ESCALONES_NORMALIZADOS_KV[-1], (
        f"Los criterios sugieren {valor_minimo_necesario:.0f} kV, "
        f"por encima del escalón más alto normalizado (500 kV) en Colombia. "
        f"Se adopta 500 kV con análisis técnico-económico adicional requerido."
    )


def calcular(potencia_mw: float, longitud_km: float) -> ResultadoTension:
    """Calcula los tres criterios y selecciona el escalón normalizado.

    Args:
        potencia_mw: Potencia activa a transmitir (MW)
        longitud_km: Longitud de la línea (km)

    Returns:
        ResultadoTension con todos los valores y la justificación.

    Raises:
        ValueError: Si potencia o longitud son <= 0
    """
    if potencia_mw <= 0:
        raise ValueError(f"La potencia debe ser positiva, recibido: {potencia_mw}")
    if longitud_km <= 0:
        raise ValueError(f"La longitud debe ser positiva, recibido: {longitud_km}")

    v_hefner = hefner(potencia_mw, longitud_km)
    v_still = still(potencia_mw, longitud_km)
    v_1kvkm = regla_1_kv_por_km(longitud_km)

    tension, justif = seleccionar_escalon_normalizado([v_hefner, v_still, v_1kvkm])

    return ResultadoTension(
        potencia_mw=potencia_mw,
        longitud_km=longitud_km,
        hefner_kv=v_hefner,
        still_kv=v_still,
        regla_1kvkm_kv=v_1kvkm,
        tension_recomendada_kv=tension,
        justificacion=justif,
    )
