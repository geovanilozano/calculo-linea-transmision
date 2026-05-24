"""Cálculo mecánico completo del conductor y cable de guarda.

Cubre las secciones 3.1 a 3.6 del trabajo académico:
- 3.1 Datos mecánicos del conductor
- 3.2 Cálculo de las constantes (E, α, Wc, Wv, Wr, σ_máx, ac)
- 3.3 Ecuación de cambio de estado (cúbica en σ₂)
- 3.4 Comprobación de hipótesis (A vs B → gobernante)
- 3.5 Cálculo de flechas máximas en 4 hipótesis
- 3.6 Terreno llano y quebrado (corrección por desnivel)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict, field
from typing import Literal


K_PRESION_VIENTO = 0.613  # Pa·s²/m² (presión dinámica del aire)
G = 9.81  # m/s²


@dataclass(frozen=True)
class Hipotesis:
    """Una hipótesis climática del cálculo mecánico."""

    nombre: str
    descripcion: str
    velocidad_viento_kmh: float
    temperatura_c: float
    factor_seguridad: float
    delta_temp_c: float = 0.0  # variación de temperatura respecto al estado base


# Hipótesis estándar del proyecto colombiano
HIPOTESIS_ESTANDAR: list[Hipotesis] = [
    Hipotesis("A", "Viento máximo", 140.0, 15.0, 2.5, 5.0),
    Hipotesis("B", "Mínima temperatura", 35.0, 5.0, 2.5, 5.0),
    Hipotesis("C", "Operación diaria (EDS)", 20.0, 27.0, 5.0, 10.0),
    Hipotesis("D", "Máxima temperatura", 0.0, 65.0, 2.5, 5.0),
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
    flecha_terreno_quebrado_m: float
    cumple: bool


@dataclass(frozen=True)
class ResultadoMecanico:
    """Resultado completo del cálculo mecánico (secciones 3.1-3.6)."""

    # 3.1 Datos mecánicos
    nombre_elemento: str
    vano_m: float
    diametro_mm: float
    area_mm2: float
    carga_rotura_kgf: float
    masa_kg_m: float
    # 3.2 Constantes
    sigma_rotura_mpa: float
    peso_aparente_n_m: float  # 3.2.4 Wc
    modulo_elasticidad_kgf_mm2: float  # 3.2.1 E
    coef_dilatacion_invc: float  # 3.2.2 α
    vano_critico_ab_m: float  # 3.2.8 ac entre A y B
    # 3.4 Comprobación
    hipotesis_extrema: str  # A o B según vano > o < ac
    # 3.5 Flechas
    hipotesis: list[ResultadoHipotesis] = field(default_factory=list)
    hipotesis_gobernante: str = ""
    flecha_maxima_m: float = 0.0
    # 3.6 Terreno
    desnivel_m: float = 0.0
    angulo_psi_deg: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


def carga_viento_n_m(
    velocidad_kmh: float, diametro_mm: float, factor_sombra: float = 1.0
) -> float:
    """3.2.5 Presión del viento: Wv = K · (V/3.6)² · SF · Φ / 1000 [N/m]."""
    v_ms = velocidad_kmh / 3.6
    return K_PRESION_VIENTO * (v_ms ** 2) * factor_sombra * diametro_mm / 1000.0


def carga_resultante_n_m(peso_n_m: float, viento_n_m: float) -> float:
    """3.2.6 Factor de corrección: Wr = √(Wc² + Wv²)."""
    return math.sqrt(peso_n_m ** 2 + viento_n_m ** 2)


def vano_critico_m(
    sigma_max_mpa: float,
    area_mm2: float,
    coef_dilatacion: float,
    temp_a_c: float,
    temp_b_c: float,
    wr_a_n_m: float,
    wr_b_n_m: float,
) -> float:
    """3.2.8 Vano crítico entre hipótesis A y B:

    ac = √[ 24·A²·σ_máx²·α·(θA - θB) / (Wr_A² - Wr_B²) ]

    Devuelve 0 si las cargas son iguales (división por cero).
    """
    denom = wr_a_n_m ** 2 - wr_b_n_m ** 2
    if denom <= 0:
        return 0.0
    sigma_n_mm2 = sigma_max_mpa  # 1 MPa = 1 N/mm²
    delta_t = temp_a_c - temp_b_c
    if delta_t == 0:
        return 0.0
    numerador = 24.0 * (area_mm2 ** 2) * (sigma_n_mm2 ** 2) * abs(coef_dilatacion * delta_t)
    return math.sqrt(numerador / denom)


def resolver_cambio_estado(
    sigma_1_mpa: float,
    wr_1_n_m: float,
    temp_1_c: float,
    wr_2_n_m: float,
    temp_2_c: float,
    vano_m: float,
    area_mm2: float,
    modulo_e_kgf_mm2: float,
    coef_alpha: float,
) -> float:
    """3.3 Ecuación de cambio de estado (cúbica en σ₂).

    σ₂ - (Wr₂·a)²·E / (24·A²·σ₂²) = σ₁ - (Wr₁·a)²·E / (24·A²·σ₁²) - α·E·(θ₂-θ₁)

    Se resuelve por Newton-Raphson. Devuelve σ₂ en MPa.
    """
    # Conversión: usamos MPa = N/mm² consistentemente
    # E en MPa también
    e_mpa = modulo_e_kgf_mm2 * 9.81  # kgf/mm² → MPa (1 kgf = 9.81 N)
    a = vano_m * 1000.0  # mm
    a_area_24 = 24.0 * (area_mm2 ** 2)

    # Lado derecho (constante) convertimos Wr a N/mm
    wr_1_n_mm = wr_1_n_m / 1000.0
    wr_2_n_mm = wr_2_n_m / 1000.0

    rhs = (
        sigma_1_mpa
        - ((wr_1_n_mm * a) ** 2 * e_mpa) / (a_area_24 * (sigma_1_mpa ** 2))
        - coef_alpha * e_mpa * (temp_2_c - temp_1_c)
    )

    # f(σ) = σ - (Wr₂·a)²·E / (24·A²·σ²) - rhs = 0
    # Newton-Raphson
    k = ((wr_2_n_mm * a) ** 2 * e_mpa) / a_area_24

    sigma = sigma_1_mpa  # estimación inicial
    for _ in range(60):
        f = sigma - k / (sigma ** 2) - rhs
        fp = 1.0 + 2.0 * k / (sigma ** 3)
        if abs(fp) < 1e-12:
            break
        sigma_new = sigma - f / fp
        if sigma_new <= 0:
            sigma_new = sigma / 2.0
        if abs(sigma_new - sigma) < 1e-6:
            sigma = sigma_new
            break
        sigma = sigma_new

    return sigma


def encontrar_gobernante(
    hipotesis: list[Hipotesis],
    cargas_wr: dict[str, float],
    sigma_max_por_hip: dict[str, float],
    vano_m: float,
    area_mm2: float,
    modulo_e_kgf_mm2: float,
    coef_alpha: float,
) -> str:
    """Determina iterativamente la hipótesis GOBERNANTE del diseño mecánico.

    La gobernante es aquella tal que, al tomarla como estado base con σ = σ_máx,
    todas las demás hipótesis cumplen σⱼ ≤ σ_máx,j. Físicamente es la condición
    de carga/temperatura que primero alcanza su límite admisible al tensar el
    conductor; las demás quedan automáticamente por debajo.

    Algoritmo (converge en ≤ N pasos, N = nº hipótesis):
      1. Empezar con la hipótesis de mayor FS (la más restrictiva en σ_máx).
      2. Tomarla como base (σ = σ_máx) y calcular σⱼ en las demás vía cambio
         de estado.
      3. Si alguna σⱼ > σ_máx,j → esa hipótesis es más restrictiva: cambiar el
         candidato a ella y repetir.
      4. Cuando ninguna otra viola su σ_máx → el candidato actual es la
         gobernante.

    En diseño típico de 500 kV con FS_C=5 esto converge a la hipótesis C
    (operación diaria); pero la rutina es general y maneja cualquier
    combinación de vano, material y hipótesis (p.ej. un guarda en vano corto
    puede dar A como gobernante).
    """
    # Punto de partida: la hipótesis con mayor FS (σ_max más bajo = más restrictiva)
    candidato = max(hipotesis, key=lambda h: h.factor_seguridad).nombre

    for _ in range(len(hipotesis) + 1):
        hip_base = next(h for h in hipotesis if h.nombre == candidato)
        sigma_base = sigma_max_por_hip[candidato]
        wr_base = cargas_wr[candidato]
        temp_base = hip_base.temperatura_c

        peor_ratio = 1.0 + 1e-9  # margen numérico
        peor_hip = None
        for h in hipotesis:
            if h.nombre == candidato:
                continue
            sigma_j = resolver_cambio_estado(
                sigma_1_mpa=sigma_base,
                wr_1_n_m=wr_base,
                temp_1_c=temp_base,
                wr_2_n_m=cargas_wr[h.nombre],
                temp_2_c=h.temperatura_c,
                vano_m=vano_m,
                area_mm2=area_mm2,
                modulo_e_kgf_mm2=modulo_e_kgf_mm2,
                coef_alpha=coef_alpha,
            )
            ratio = sigma_j / sigma_max_por_hip[h.nombre]
            if ratio > peor_ratio:
                peor_ratio = ratio
                peor_hip = h.nombre

        if peor_hip is None:
            return candidato
        candidato = peor_hip

    return candidato


def flecha_parabolica_m(carga_resultante_n_m: float, vano_m: float, tension_n: float) -> float:
    """3.6.1 Flecha terreno llano: f = Wr·a² / (8·T)."""
    if tension_n <= 0:
        return 0.0
    return carga_resultante_n_m * (vano_m ** 2) / (8.0 * tension_n)


def flecha_terreno_quebrado_m(flecha_llano: float, vano_m: float, desnivel_m: float) -> float:
    """3.6.2 Corrección por terreno quebrado: f_incl = f_llano / cos²(ψ).

    Donde tan(ψ) = h/a (desnivel / vano).
    """
    if vano_m <= 0:
        return flecha_llano
    tan_psi = desnivel_m / vano_m
    cos_psi = 1.0 / math.sqrt(1.0 + tan_psi ** 2)
    return flecha_llano / (cos_psi ** 2)


def calcular(
    elemento: Literal["conductor", "guarda"],
    diametro_mm: float,
    area_mm2: float,
    masa_kg_m: float,
    carga_rotura_kgf: float,
    vano_m: float,
    modulo_elasticidad_kgf_mm2: float = 7500.0,
    coef_dilatacion_invc: float = 18.9e-6,
    hipotesis: list[Hipotesis] | None = None,
    factor_sombra: float = 1.0,
    desnivel_m: float = 0.0,
) -> ResultadoMecanico:
    """Cálculo mecánico completo según secciones 3.1-3.6.

    Procedimiento:
    1. Calcular constantes: Wc, Wv_i, Wr_i, σ_máx_i.
    2. Vano crítico A-B (informativo: cuál entre A y B tiene mayor carga
       combinada sólo determina cuál de las dos sería gobernante si
       tuvieran el mismo FS).
    3. Determinar la hipótesis GOBERNANTE iterativamente (ver
       `encontrar_gobernante`): es aquella tal que, al tomarla como base
       con σ = σ_máx, todas las demás cumplen σⱼ ≤ σ_máx,j. Para FS
       típicos (A=B=D=2.5, C=5) la gobernante resulta C; pero el algoritmo
       es general y maneja cualquier combinación.
    4. Tomar la gobernante como estado base (σ = σ_máx en ella).
    5. Para las demás hipótesis: resolver ecuación de cambio de estado.
    6. Calcular flecha en cada hipótesis (terreno llano + quebrado).
    """
    if hipotesis is None:
        hipotesis = HIPOTESIS_ESTANDAR

    # 3.2.4 Peso aparente
    peso_n_m = masa_kg_m * G

    # 3.2.3 Carga de rotura y σ_rotura
    carga_rotura_n = carga_rotura_kgf * G
    sigma_rotura_mpa = carga_rotura_n / area_mm2  # N/mm² = MPa

    nombre_elem = "Conductor de fase" if elemento == "conductor" else "Cable de guarda"

    # 3.2.5/3.2.6: cargas viento y resultantes por hipótesis
    cargas_wr: dict[str, float] = {}
    sigma_max_por_hip: dict[str, float] = {}
    for h in hipotesis:
        wv = carga_viento_n_m(h.velocidad_viento_kmh, diametro_mm, factor_sombra)
        wr = carga_resultante_n_m(peso_n_m, wv)
        cargas_wr[h.nombre] = wr
        # 3.2.7 σ_max admisible para esta hipótesis
        sigma_max_por_hip[h.nombre] = sigma_rotura_mpa / h.factor_seguridad

    # 3.2.8 Vano crítico entre A y B (informativo: qué hipótesis impone más
    # carga combinada entre A y B). NO se usa para elegir el estado base.
    hip_a = next((h for h in hipotesis if h.nombre == "A"), hipotesis[0])
    hip_b = next((h for h in hipotesis if h.nombre == "B"), hipotesis[1] if len(hipotesis) > 1 else hipotesis[0])
    ac = vano_critico_m(
        sigma_max_mpa=sigma_max_por_hip["A"],
        area_mm2=area_mm2,
        coef_dilatacion=coef_dilatacion_invc,
        temp_a_c=hip_a.temperatura_c,
        temp_b_c=hip_b.temperatura_c,
        wr_a_n_m=cargas_wr["A"],
        wr_b_n_m=cargas_wr["B"],
    )
    if ac > 0 and vano_m > ac:
        hip_extrema = "A"
    else:
        hip_extrema = "B"

    # 3.3-3.4 Hipótesis GOBERNANTE: la que primero alcanza su σ_máx al tensar.
    # Se determina iterativamente para que el cumplimiento sea consistente
    # en TODAS las hipótesis (no sólo en A o B).
    hip_gobernante_nombre = encontrar_gobernante(
        hipotesis=hipotesis,
        cargas_wr=cargas_wr,
        sigma_max_por_hip=sigma_max_por_hip,
        vano_m=vano_m,
        area_mm2=area_mm2,
        modulo_e_kgf_mm2=modulo_elasticidad_kgf_mm2,
        coef_alpha=coef_dilatacion_invc,
    )
    hip_base_obj = next(h for h in hipotesis if h.nombre == hip_gobernante_nombre)
    sigma_base_mpa = sigma_max_por_hip[hip_gobernante_nombre]
    wr_base = cargas_wr[hip_gobernante_nombre]
    temp_base = hip_base_obj.temperatura_c

    # Calcular σ en cada hipótesis usando cambio de estado desde la gobernante
    resultados: list[ResultadoHipotesis] = []
    flecha_max = 0.0
    flecha_max_nombre = ""

    for h in hipotesis:
        wv = carga_viento_n_m(h.velocidad_viento_kmh, diametro_mm, factor_sombra)
        wr = cargas_wr[h.nombre]
        sigma_max = sigma_max_por_hip[h.nombre]

        if h.nombre == hip_gobernante_nombre:
            # Estado base: σ ya conocido (σ_máx de la gobernante)
            sigma_calc = sigma_base_mpa
        else:
            # Resolver cambio de estado desde la gobernante
            sigma_calc = resolver_cambio_estado(
                sigma_1_mpa=sigma_base_mpa,
                wr_1_n_m=wr_base,
                temp_1_c=temp_base,
                wr_2_n_m=wr,
                temp_2_c=h.temperatura_c,
                vano_m=vano_m,
                area_mm2=area_mm2,
                modulo_e_kgf_mm2=modulo_elasticidad_kgf_mm2,
                coef_alpha=coef_dilatacion_invc,
            )

        tension_n = sigma_calc * area_mm2  # MPa × mm² = N
        flecha_llano = flecha_parabolica_m(wr, vano_m, tension_n)
        flecha_quebrado = flecha_terreno_quebrado_m(flecha_llano, vano_m, desnivel_m)

        if flecha_llano > flecha_max:
            flecha_max = flecha_llano
            flecha_max_nombre = h.nombre

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
                flecha_m=flecha_llano,
                flecha_terreno_quebrado_m=flecha_quebrado,
                cumple=sigma_calc <= sigma_max * 1.001,  # margen numérico
            )
        )

    gobernante = hip_gobernante_nombre

    # Ángulo de inclinación del terreno
    if vano_m > 0 and desnivel_m > 0:
        angulo_psi = math.degrees(math.atan(desnivel_m / vano_m))
    else:
        angulo_psi = 0.0

    return ResultadoMecanico(
        nombre_elemento=nombre_elem,
        vano_m=vano_m,
        diametro_mm=diametro_mm,
        area_mm2=area_mm2,
        carga_rotura_kgf=carga_rotura_kgf,
        masa_kg_m=masa_kg_m,
        sigma_rotura_mpa=sigma_rotura_mpa,
        peso_aparente_n_m=peso_n_m,
        modulo_elasticidad_kgf_mm2=modulo_elasticidad_kgf_mm2,
        coef_dilatacion_invc=coef_dilatacion_invc,
        vano_critico_ab_m=ac,
        hipotesis_extrema=hip_extrema,
        hipotesis=resultados,
        hipotesis_gobernante=gobernante,
        flecha_maxima_m=flecha_max,
        desnivel_m=desnivel_m,
        angulo_psi_deg=angulo_psi,
    )
