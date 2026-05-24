"""Modelo de línea larga (parámetros distribuidos).

Para línea > 240 km se usa el modelo distribuido con funciones hiperbólicas:
- Zc = sqrt(z/y)
- γ = sqrt(z·y)
- A = D = cosh(γL)
- B = Zc · sinh(γL)
- C = sinh(γL) / Zc

Luego: V_G = A·V_R + B·I_R   ;   I_G = C·V_R + D·I_R
"""
from __future__ import annotations

import cmath
import math
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ResultadoLineaLarga:
    """Resultado completo del análisis de línea larga."""

    longitud_km: float
    tension_nominal_kv: float  # línea-línea
    potencia_mw: float
    factor_potencia: float

    # Parámetros característicos (complejos representados como dos floats)
    zc_re: float
    zc_im: float
    gamma_re: float  # nepers/km
    gamma_im: float  # rad/km

    # ABCD (todos complejos)
    a_re: float
    a_im: float
    b_re: float
    b_im: float  # Ω
    c_re: float
    c_im: float  # S
    d_re: float
    d_im: float

    # Magnitudes y resultados eléctricos
    ir_a: float  # corriente extremo receptor (magnitud)
    vr_fn_kv: float  # tensión extremo receptor fase-neutro
    vg_ll_kv: float  # tensión extremo generador línea-línea (mag)
    ig_a: float  # corriente extremo generador (mag)
    pg_mw: float  # potencia activa en el generador

    # Indicadores de desempeño
    regulacion_pct: float  # puede ser negativa (Ferranti)
    perdidas_pct: float
    eficiencia_pct: float

    # Validaciones
    reg_max_pct: float
    perdidas_max_pct: float
    regulacion_cumple: bool
    perdidas_cumple: bool

    def to_dict(self) -> dict:
        return asdict(self)


def calcular(
    r_fase_ohm_km: float,
    xl_fase_ohm_km: float,
    b_fase_s_km: float,
    longitud_km: float,
    tension_linea_kv: float,
    potencia_mw: float,
    factor_potencia: float = 1.0,
    reg_max_pct: float = 19.0,
    perdidas_max_pct: float = 4.7,
) -> ResultadoLineaLarga:
    """Aplica el modelo de línea larga con parámetros distribuidos.

    Args:
        r_fase_ohm_km: Resistencia AC por fase (Ω/km)
        xl_fase_ohm_km: Reactancia inductiva por fase (Ω/km)
        b_fase_s_km: Susceptancia capacitiva por fase (S/km)
        longitud_km: Longitud total de la línea (km)
        tension_linea_kv: Tensión nominal línea-línea (kV) — en el extremo receptor
        potencia_mw: Potencia activa entregada en el extremo receptor (MW)
        factor_potencia: cos(φ) en el extremo receptor (1.0 = carga resistiva)
        reg_max_pct: Regulación máxima admisible (%)
        perdidas_max_pct: Pérdidas activas máximas admisibles (%)

    Returns:
        ResultadoLineaLarga completo con validaciones
    """
    if longitud_km <= 0 or tension_linea_kv <= 0 or potencia_mw <= 0:
        raise ValueError("longitud, tensión y potencia deben ser positivos")
    if not (0 < factor_potencia <= 1.0):
        raise ValueError("factor_potencia debe estar entre 0 y 1")

    # Impedancia y admitancia distribuidas (complejas, por km)
    z = complex(r_fase_ohm_km, xl_fase_ohm_km)  # Ω/km
    y = complex(0.0, b_fase_s_km)  # S/km (G se asume 0 si no hay corona)

    # Impedancia característica y constante de propagación
    zc = cmath.sqrt(z / y)  # Ω
    gamma = cmath.sqrt(z * y)  # 1/km
    gamma_l = gamma * longitud_km

    # Parámetros ABCD
    cosh_gl = cmath.cosh(gamma_l)
    sinh_gl = cmath.sinh(gamma_l)
    a = cosh_gl
    d = cosh_gl
    b = zc * sinh_gl  # Ω
    c = sinh_gl / zc  # S

    # Corriente en el extremo receptor
    # I_R = P / (sqrt(3) · V_LL · cos(phi))  con phase angle = -arccos(fp)
    angulo_fp = -math.acos(factor_potencia)  # negativo = corriente atrasa
    ir_mag = (potencia_mw * 1e6) / (math.sqrt(3) * tension_linea_kv * 1e3 * factor_potencia)
    ir = cmath.rect(ir_mag, angulo_fp)

    # Tensión receptor fase-neutro (referencia 0°)
    vr_fn_kv = tension_linea_kv / math.sqrt(3)
    vr = complex(vr_fn_kv * 1e3, 0.0)  # V

    # Tensión y corriente en el generador
    vg = a * vr + b * ir  # V (fase-neutro complejo)
    ig = c * vr + d * ir  # A (complejo)

    vg_fn = abs(vg)  # módulo fase-neutro V
    vg_ll = vg_fn * math.sqrt(3) / 1000.0  # kV línea-línea
    ig_mag = abs(ig)  # A

    # Regulación: (V_G(L) - V_R(L)) / V_R(L) * 100
    regulacion = (vg_ll - tension_linea_kv) / tension_linea_kv * 100.0

    # Potencia generada y pérdidas
    # P_G = Re(sqrt(3) * V_G * I_G*)  con V_G y I_G en magnitudes complejas (línea)
    # Usamos por fase: P_G = 3 * Re(V_G_fn * conj(I_G))
    sg_compleja = 3.0 * vg * ig.conjugate()  # VA por fase * 3
    pg_w = sg_compleja.real
    pg_mw = pg_w / 1e6

    delta_p = pg_mw - potencia_mw
    perdidas_pct = (delta_p / potencia_mw) * 100.0
    eficiencia_pct = (potencia_mw / pg_mw) * 100.0 if pg_mw > 0 else 0.0

    # Validaciones (usamos valor absoluto de regulación)
    reg_cumple = abs(regulacion) <= reg_max_pct
    perd_cumple = perdidas_pct <= perdidas_max_pct

    return ResultadoLineaLarga(
        longitud_km=longitud_km,
        tension_nominal_kv=tension_linea_kv,
        potencia_mw=potencia_mw,
        factor_potencia=factor_potencia,
        zc_re=zc.real,
        zc_im=zc.imag,
        gamma_re=gamma.real,
        gamma_im=gamma.imag,
        a_re=a.real,
        a_im=a.imag,
        b_re=b.real,
        b_im=b.imag,
        c_re=c.real,
        c_im=c.imag,
        d_re=d.real,
        d_im=d.imag,
        ir_a=ir_mag,
        vr_fn_kv=vr_fn_kv,
        vg_ll_kv=vg_ll,
        ig_a=ig_mag,
        pg_mw=pg_mw,
        regulacion_pct=regulacion,
        perdidas_pct=perdidas_pct,
        eficiencia_pct=eficiencia_pct,
        reg_max_pct=reg_max_pct,
        perdidas_max_pct=perdidas_max_pct,
        regulacion_cumple=reg_cumple,
        perdidas_cumple=perd_cumple,
    )
