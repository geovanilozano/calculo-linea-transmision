"""Cálculo del número y dimensiones de la cadena de aisladores.

Dos criterios:
1. Línea de fuga (contaminación): N_f = k · V_L / L_fuga_unitario
2. Tensión disruptiva (BIL): N_BIL = 1.2 · BIL / (V_disco_lluvia · 0.9)

Se adopta el mayor de los dos.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict


# Aislador ANSI 52-3 (porcelana estándar 500 kV)
AISLADOR_ANSI_52_3 = {
    "tipo": "Disco porcelana ANSI 52-3",
    "diametro_mm": 254,
    "altura_unitaria_mm": 146,
    "tension_disruptiva_seco_kv": 80,
    "tension_disruptiva_lluvia_kv": 50,
    "linea_fuga_unitaria_mm": 305,
    "carga_rotura_kgf": 16800,
    "peso_kg": 5.6,
}

# Niveles de contaminación IEC 60815
COEF_CONTAMINACION_MM_KV = {
    "ligera": 16,
    "media": 20,
    "alta": 25,
    "muy_alta": 31,
    "severa": 44,
}


@dataclass(frozen=True)
class ResultadoAisladores:
    """Resultado del cálculo de la cadena de aisladores."""

    tension_linea_kv: float
    bil_kv: float
    nivel_contaminacion: str
    k_contaminacion_mm_kv: float
    linea_fuga_unitaria_mm: float
    tension_disruptiva_lluvia_kv: float
    altura_unitaria_mm: float
    peso_unitario_kg: float
    carga_rotura_unitaria_kgf: float

    # Resultados
    n_discos_por_fuga: int
    n_discos_por_bil: int
    n_discos_adoptado: int
    longitud_cadena_m: float
    peso_cadena_kg: float

    # Validación FS mecánico (cadena simple vs doble)
    carga_total_cadena_kgf: float
    fs_cadena_simple: float
    fs_cadena_doble: float
    cadena_doble_requerida: bool

    def to_dict(self) -> dict:
        return asdict(self)


def n_discos_por_fuga(tension_linea_kv: float, k_mm_kv: float, fuga_unitaria_mm: float) -> int:
    """Número de discos por criterio de línea de fuga (anticontaminación)."""
    n = (k_mm_kv * tension_linea_kv) / fuga_unitaria_mm
    return math.ceil(n)


def n_discos_por_bil(bil_kv: float, tension_disruptiva_lluvia_kv: float) -> int:
    """Número de discos por criterio BIL.

    N = 1.2 · BIL / (V_disco_lluvia · 0.9)
    """
    n = (1.2 * bil_kv) / (tension_disruptiva_lluvia_kv * 0.9)
    return math.ceil(n)


def calcular(
    tension_linea_kv: float,
    bil_kv: float = 1550.0,
    nivel_contaminacion: str = "alta",
    carga_total_kgf: float = 15360.0,
    aislador: dict | None = None,
    longitud_herrajes_m_por_extremo: float = 0.20,
    peso_herrajes_kg: float = 25.0,
) -> ResultadoAisladores:
    """Calcula el número de discos, longitud y verificación mecánica.

    Args:
        tension_linea_kv: Tensión nominal línea-línea (kV)
        bil_kv: BIL del sistema (kV) — 1550 estándar para 500 kV
        nivel_contaminacion: 'ligera', 'media', 'alta', 'muy_alta', 'severa'
        carga_total_kgf: Carga total que soporta la cadena (kgf)
        aislador: Datos del aislador unitario. None usa ANSI 52-3.
        longitud_herrajes_m_por_extremo: Herrajes por cada extremo de cadena (m)
        peso_herrajes_kg: Peso total de herrajes en la cadena (kg)

    Returns:
        ResultadoAisladores completo
    """
    if aislador is None:
        aislador = AISLADOR_ANSI_52_3

    if nivel_contaminacion not in COEF_CONTAMINACION_MM_KV:
        raise ValueError(
            f"Nivel '{nivel_contaminacion}' inválido. "
            f"Usa uno de: {list(COEF_CONTAMINACION_MM_KV.keys())}"
        )

    k = COEF_CONTAMINACION_MM_KV[nivel_contaminacion]

    n_fuga = n_discos_por_fuga(tension_linea_kv, k, aislador["linea_fuga_unitaria_mm"])
    n_bil = n_discos_por_bil(bil_kv, aislador["tension_disruptiva_lluvia_kv"])
    n = max(n_fuga, n_bil)

    # Longitud y peso de la cadena completa
    longitud_m = n * (aislador["altura_unitaria_mm"] / 1000.0) + 2 * longitud_herrajes_m_por_extremo
    peso_kg = n * aislador["peso_kg"] + peso_herrajes_kg

    # Factor de seguridad mecánico
    fs_simple = aislador["carga_rotura_kgf"] / carga_total_kgf
    fs_doble = (2 * aislador["carga_rotura_kgf"]) / carga_total_kgf
    requiere_doble = fs_simple < 2.0

    return ResultadoAisladores(
        tension_linea_kv=tension_linea_kv,
        bil_kv=bil_kv,
        nivel_contaminacion=nivel_contaminacion,
        k_contaminacion_mm_kv=k,
        linea_fuga_unitaria_mm=aislador["linea_fuga_unitaria_mm"],
        tension_disruptiva_lluvia_kv=aislador["tension_disruptiva_lluvia_kv"],
        altura_unitaria_mm=aislador["altura_unitaria_mm"],
        peso_unitario_kg=aislador["peso_kg"],
        carga_rotura_unitaria_kgf=aislador["carga_rotura_kgf"],
        n_discos_por_fuga=n_fuga,
        n_discos_por_bil=n_bil,
        n_discos_adoptado=n,
        longitud_cadena_m=longitud_m,
        peso_cadena_kg=peso_kg,
        carga_total_cadena_kgf=carga_total_kgf,
        fs_cadena_simple=fs_simple,
        fs_cadena_doble=fs_doble,
        cadena_doble_requerida=requiere_doble,
    )
