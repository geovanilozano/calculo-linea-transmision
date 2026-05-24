"""Cálculo de las 4 curvas patrón del plantillado.

1. Conductor en caliente (Hip D, máx flecha)
2. Distancia mínima al terreno (caliente + 9 m)
3. Pie de apoyo (caliente - H_apoyo)
4. Conductor en frío (Hip B, mín flecha)

Las 4 curvas siguen una parábola: y(x) = x²/(2C) donde C = T/wa.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class CurvaParabolica:
    """Una curva patrón (parábola) del plantillado."""

    nombre: str
    color: str
    parametro_c_m: float
    flecha_central_m: float
    puntos_x_m: list[float]
    puntos_y_m: list[float]


@dataclass(frozen=True)
class ResultadoPlantillado:
    """Resultado del cálculo de las 4 curvas patrón."""

    vano_diseno_m: float
    distancia_minima_terreno_m: float
    altura_apoyo_conductor_m: float

    flecha_max_m: float  # Hipótesis D, conductor caliente
    flecha_min_m: float  # Hipótesis B, conductor frío
    tension_caliente_n: float
    tension_frio_n: float

    curvas: list[CurvaParabolica]

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def generar_curva_parabolica(
    nombre: str,
    color: str,
    parametro_c_m: float,
    flecha_central_m: float,
    vano_m: float,
    desplazamiento_y_m: float = 0.0,
    n_puntos: int = 41,
) -> CurvaParabolica:
    """Genera una curva parabólica simétrica con el origen en el punto más bajo.

    Args:
        nombre: Nombre descriptivo de la curva
        color: Color asociado (CSS hex)
        parametro_c_m: Parámetro de la catenaria C = T/wa (m)
        flecha_central_m: Flecha en el centro del vano (m)
        vano_m: Vano horizontal (m)
        desplazamiento_y_m: Desplazamiento vertical adicional (m)
        n_puntos: Cantidad de puntos para discretizar

    Returns:
        CurvaParabolica con sus puntos x, y
    """
    x_min = -vano_m / 2.0
    x_max = vano_m / 2.0
    xs = [x_min + i * (vano_m / (n_puntos - 1)) for i in range(n_puntos)]
    ys = [(x ** 2) / (2.0 * parametro_c_m) + desplazamiento_y_m for x in xs]
    return CurvaParabolica(
        nombre=nombre,
        color=color,
        parametro_c_m=parametro_c_m,
        flecha_central_m=flecha_central_m,
        puntos_x_m=xs,
        puntos_y_m=ys,
    )


def calcular(
    vano_m: float,
    tension_caliente_n: float,
    tension_frio_n: float,
    masa_kg_m: float,
    distancia_min_terreno_m: float = 9.0,
    altura_apoyo_conductor_m: float = 29.33,
) -> ResultadoPlantillado:
    """Genera las 4 curvas patrón del plantillado.

    Args:
        vano_m: Vano de diseño (m)
        tension_caliente_n: Tensión del conductor en hipótesis D (N)
        tension_frio_n: Tensión del conductor en hipótesis B (N)
        masa_kg_m: Masa lineal del conductor (kg/m)
        distancia_min_terreno_m: Distancia mínima al terreno RETIE (m)
        altura_apoyo_conductor_m: Altura del punto de apoyo desde el terreno (m)

    Returns:
        ResultadoPlantillado con las 4 curvas
    """
    wa_n_m = masa_kg_m * 9.8  # peso por metro (N/m)

    # Parámetros de catenaria
    c_caliente = tension_caliente_n / wa_n_m
    c_frio = tension_frio_n / wa_n_m

    # Flechas centrales
    f_max = (wa_n_m * vano_m ** 2) / (8.0 * tension_caliente_n)
    f_min = (wa_n_m * vano_m ** 2) / (8.0 * tension_frio_n)

    # 1. Conductor en caliente (Hip D, máx flecha)
    curva_caliente = generar_curva_parabolica(
        "1. Conductor en caliente",
        "#dc2626",  # rojo
        c_caliente,
        f_max,
        vano_m,
        desplazamiento_y_m=0.0,
    )

    # 2. Distancia mínima al terreno (caliente + d_terreno)
    curva_terreno = generar_curva_parabolica(
        "2. Distancia mínima al terreno",
        "#059669",  # verde
        c_caliente,
        f_max,
        vano_m,
        desplazamiento_y_m=distancia_min_terreno_m,
    )

    # 3. Pie de apoyo (caliente - H_apoyo)
    curva_apoyo = generar_curva_parabolica(
        "3. Pie de apoyo",
        "#7c3aed",  # morado
        c_caliente,
        f_max,
        vano_m,
        desplazamiento_y_m=-altura_apoyo_conductor_m,
    )

    # 4. Conductor en frío (Hip B)
    curva_frio = generar_curva_parabolica(
        "4. Conductor en frío",
        "#2563eb",  # azul
        c_frio,
        f_min,
        vano_m,
        desplazamiento_y_m=0.0,
    )

    return ResultadoPlantillado(
        vano_diseno_m=vano_m,
        distancia_minima_terreno_m=distancia_min_terreno_m,
        altura_apoyo_conductor_m=altura_apoyo_conductor_m,
        flecha_max_m=f_max,
        flecha_min_m=f_min,
        tension_caliente_n=tension_caliente_n,
        tension_frio_n=tension_frio_n,
        curvas=[curva_caliente, curva_terreno, curva_apoyo, curva_frio],
    )
