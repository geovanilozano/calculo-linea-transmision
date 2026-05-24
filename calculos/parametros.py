"""Cálculo de parámetros eléctricos distribuidos R, L, C, X, B y verificación de Corona.

Referencias:
- Inductancia: L = 2e-7 · ln(GMD / GMR_L) [H/m]
- Capacitancia: C = 2π·ε₀ / ln(GMD / GMR_C) [F/m]
- Fórmula de Peek para corona: Ec = 30·m·δ·(1 + 0.301/√(r·δ)) [kV/cm pico]
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict


EPSILON_0 = 8.854e-12  # F/m, permitividad del vacío
PRESION_ATMOSFERICA_NIVEL_MAR_CMHG = 76.0


@dataclass(frozen=True)
class ResultadoParametros:
    """Resultado del cálculo de parámetros eléctricos por unidad de longitud."""

    frecuencia_hz: float

    # Parámetros distribuidos por km
    r_fase_ohm_km: float
    l_fase_h_km: float
    xl_fase_ohm_km: float
    c_fase_f_km: float
    b_fase_s_km: float

    # Totales para la línea
    z_total_re: float
    z_total_im: float  # Ω
    y_total_im: float  # S

    # Corona
    altitud_msnm: float
    temperatura_c: float
    densidad_relativa: float
    gradiente_critico_kv_cm: float
    gradiente_superficial_kv_cm: float
    coef_seguridad_corona: float
    corona_cumple: bool

    def to_dict(self) -> dict:
        return asdict(self)


def inductancia_por_metro(gmd_m: float, gmr_l_m: float) -> float:
    """L = 2e-7 · ln(GMD / GMR_L)  [H/m por fase]."""
    if gmr_l_m <= 0 or gmd_m <= 0:
        raise ValueError("GMD y GMR deben ser positivos")
    return 2.0e-7 * math.log(gmd_m / gmr_l_m)


def capacitancia_por_metro(gmd_m: float, gmr_c_m: float) -> float:
    """C = 2π·ε₀ / ln(GMD / GMR_C)  [F/m por fase]."""
    if gmr_c_m <= 0 or gmd_m <= 0:
        raise ValueError("GMD y GMR deben ser positivos")
    return (2.0 * math.pi * EPSILON_0) / math.log(gmd_m / gmr_c_m)


def densidad_relativa_aire(altitud_msnm: float, temperatura_c: float) -> float:
    """Calcula la densidad relativa del aire.

    Presión barométrica (cmHg) en función de altitud: h = 76 · e^(-altitud/7463)
    δ = 3.921 · h / (273 + θ)

    Returns:
        Densidad relativa (1.0 a nivel del mar y 25°C)
    """
    presion_cmhg = PRESION_ATMOSFERICA_NIVEL_MAR_CMHG * math.exp(-altitud_msnm / 7463.0)
    return 3.921 * presion_cmhg / (273.0 + temperatura_c)


def gradiente_critico_peek(
    radio_subc_cm: float,
    densidad: float,
    factor_superficie: float = 0.85,
) -> float:
    """Gradiente crítico de inicio de Corona (Peek).

    Ec = 30 · m · δ · (1 + 0.301/√(r·δ))  [kV/cm pico]

    Args:
        radio_subc_cm: Radio del subconductor (cm)
        densidad: Densidad relativa del aire
        factor_superficie: m, factor de rugosidad superficial. 0.85 para trenzado comercial.

    Returns:
        Gradiente crítico en kV/cm (valor pico)
    """
    return 30.0 * factor_superficie * densidad * (
        1.0 + 0.301 / math.sqrt(radio_subc_cm * densidad)
    )


def gradiente_superficial_haz(
    tension_linea_kv: float,
    radio_subc_cm: float,
    n_subc: int,
    gmd_m: float,
    rmg_haz_corona_m: float,
) -> float:
    """Gradiente superficial máximo en el haz (valor pico).

    E_sup = V_fase_pico / (n · r · ln(GMD / RMG_haz))  [kV/cm]

    Args:
        tension_linea_kv: Tensión nominal línea-línea (kV)
        radio_subc_cm: Radio físico del subconductor (cm)
        n_subc: Número de subconductores
        gmd_m: GMD entre fases (m)
        rmg_haz_corona_m: RMG del haz para corona (m)

    Returns:
        Gradiente superficial pico en kV/cm
    """
    v_fase_pico = (tension_linea_kv * math.sqrt(2.0)) / math.sqrt(3.0)
    if rmg_haz_corona_m <= 0 or gmd_m <= 0:
        raise ValueError("GMD y RMG deben ser positivos")
    return v_fase_pico / (n_subc * radio_subc_cm * math.log(gmd_m / rmg_haz_corona_m))


def calcular(
    r_fase_ohm_km: float,
    gmd_m: float,
    gmr_l_m: float,
    gmr_c_m: float,
    rmg_corona_m: float,
    n_subc: int,
    radio_subc_mm: float,
    tension_linea_kv: float,
    longitud_km: float,
    altitud_msnm: float,
    temperatura_c: float = 25.0,
    factor_superficie: float = 0.85,
    frecuencia_hz: float = 60.0,
) -> ResultadoParametros:
    """Calcula todos los parámetros eléctricos y verifica efecto Corona.

    Args:
        r_fase_ohm_km: Resistencia AC por fase (Ω/km), del haz en paralelo
        gmd_m: Distancia Media Geométrica entre fases (m)
        gmr_l_m: GMR del haz para inductancia (m)
        gmr_c_m: GMR del haz para capacitancia (m)
        rmg_corona_m: RMG efectivo para análisis de corona (m)
        n_subc: Número de subconductores
        radio_subc_mm: Radio físico del subconductor (mm)
        tension_linea_kv: Tensión nominal línea-línea (kV)
        longitud_km: Longitud total de la línea (km)
        altitud_msnm: Altitud sobre el nivel del mar (m)
        temperatura_c: Temperatura ambiente para densidad de aire (°C)
        factor_superficie: m de Peek, factor de rugosidad
        frecuencia_hz: Frecuencia del sistema (Hz)

    Returns:
        ResultadoParametros completo
    """
    # Inductancia y capacitancia (por metro -> por km)
    l_por_metro = inductancia_por_metro(gmd_m, gmr_l_m)
    c_por_metro = capacitancia_por_metro(gmd_m, gmr_c_m)

    l_por_km = l_por_metro * 1000.0  # H/km
    c_por_km = c_por_metro * 1000.0  # F/km

    # Reactancia inductiva y susceptancia capacitiva
    omega = 2.0 * math.pi * frecuencia_hz
    xl_por_km = omega * l_por_km
    b_por_km = omega * c_por_km

    # Totales para la línea (impedancia y admitancia)
    z_re = r_fase_ohm_km * longitud_km
    z_im = xl_por_km * longitud_km
    y_im = b_por_km * longitud_km

    # Efecto Corona
    delta = densidad_relativa_aire(altitud_msnm, temperatura_c)
    radio_subc_cm = radio_subc_mm / 10.0
    ec = gradiente_critico_peek(radio_subc_cm, delta, factor_superficie)
    e_sup = gradiente_superficial_haz(
        tension_linea_kv, radio_subc_cm, n_subc, gmd_m, rmg_corona_m
    )
    cs = ec / e_sup if e_sup > 0 else float("inf")
    cumple_corona = cs > 1.0

    return ResultadoParametros(
        frecuencia_hz=frecuencia_hz,
        r_fase_ohm_km=r_fase_ohm_km,
        l_fase_h_km=l_por_km,
        xl_fase_ohm_km=xl_por_km,
        c_fase_f_km=c_por_km,
        b_fase_s_km=b_por_km,
        z_total_re=z_re,
        z_total_im=z_im,
        y_total_im=y_im,
        altitud_msnm=altitud_msnm,
        temperatura_c=temperatura_c,
        densidad_relativa=delta,
        gradiente_critico_kv_cm=ec,
        gradiente_superficial_kv_cm=e_sup,
        coef_seguridad_corona=cs,
        corona_cumple=cumple_corona,
    )
