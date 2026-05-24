"""Diseño preliminar de la torre y distancias de seguridad RETIE para 500 kV."""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict


# Distancias mínimas RETIE para 500 kV (Art. 13)
RETIE_500KV = {
    "d_terreno_transitable_m": 9.0,  # áreas vehiculares
    "d_terreno_no_transitable_m": 7.5,
    "d_via_primer_orden_m": 10.5,
    "d_estructura_m": 3.5,
}

# Ajuste por altitud según RETIE
ALTITUD_REFERENCIA_M = 1000.0
INCREMENTO_PCT_POR_300M = 3.0


@dataclass(frozen=True)
class ResultadoTorre:
    """Resultado del diseño preliminar de la torre."""

    tension_linea_kv: float
    altitud_msnm: float

    # Distancias de seguridad RETIE
    d_terreno_m: float
    d_entre_fases_m: float
    d_a_estructura_m: float

    # Geometría adoptada
    separacion_fases_adoptada_m: float

    # Cable de guarda
    angulo_proteccion_grados: float
    cumple_blindaje: bool
    cable_guarda_dh_m: float  # separación horizontal guarda-fase exterior
    cable_guarda_dv_m: float  # separación vertical guarda-fase
    altura_remate_m: float
    d_entre_cables_guarda_m: float  # distancia entre los 2 cables de guarda
    n_cables_guarda: int

    # Altura
    flecha_max_m: float
    longitud_cadena_m: float
    h_apoyo_conductor_m: float
    h_total_torre_m: float

    # Configuración del haz y aisladores (para mostrar en diagrama)
    n_subconductores: int
    haz_separacion_m: float
    n_discos_aislador: int
    cadena_doble: bool

    # Número de estructuras
    longitud_linea_km: float
    vano_diseno_m: float
    n_estructuras: int

    def to_dict(self) -> dict:
        return asdict(self)


def distancia_terreno_con_altitud(d_base_m: float, altitud_msnm: float) -> float:
    """Aplica incremento por altitud según RETIE.

    Por cada 300 m sobre 1000 msnm, +3%
    """
    if altitud_msnm <= ALTITUD_REFERENCIA_M:
        return d_base_m
    incrementos = math.ceil((altitud_msnm - ALTITUD_REFERENCIA_M) / 300.0)
    factor = 1.0 + (INCREMENTO_PCT_POR_300M / 100.0) * incrementos
    return d_base_m * factor


def distancia_entre_fases_m(
    tension_linea_kv: float,
    longitud_cadena_m: float,
    flecha_max_m: float,
    coef_kc: float = 0.008,
) -> float:
    """Calcula la separación mínima entre fases adyacentes.

    D = k_c · V_LL + √(L_cadena + f_max)
    Fórmula práctica RETIE / CIGRÉ.
    """
    return coef_kc * tension_linea_kv + math.sqrt(longitud_cadena_m + flecha_max_m)


def calcular(
    tension_linea_kv: float,
    altitud_msnm: float,
    flecha_max_m: float,
    longitud_cadena_m: float,
    longitud_linea_km: float,
    vano_diseno_m: float,
    separacion_fases_adoptada_m: float = 9.0,
    h_seguridad_m: float = 1.0,
    cable_guarda_dh_m: float = 3.0,
    cable_guarda_dv_m: float = 5.5,
    altura_remate_m: float = 5.0,
    n_subconductores: int = 3,
    haz_separacion_m: float = 0.40,
    n_discos_aislador: int = 41,
    cadena_doble: bool = True,
    n_cables_guarda: int = 2,
) -> ResultadoTorre:
    """Calcula distancias RETIE, altura de torre y número de estructuras.

    Args:
        tension_linea_kv: Tensión nominal línea-línea (kV)
        altitud_msnm: Altitud (m)
        flecha_max_m: Flecha máxima del conductor (m) — usualmente Hipótesis D
        longitud_cadena_m: Longitud total de la cadena de aisladores (m)
        longitud_linea_km: Longitud total de la línea (km)
        vano_diseno_m: Vano de diseño (m)
        separacion_fases_adoptada_m: Distancia entre fases adoptada (m)
        h_seguridad_m: Margen de seguridad adicional (m)
        cable_guarda_dh_m: Separación horizontal cable de guarda vs fase exterior
        cable_guarda_dv_m: Separación vertical cable de guarda vs fase
        altura_remate_m: Altura del remate superior de la torre

    Returns:
        ResultadoTorre completo
    """
    # Distancias RETIE con corrección de altitud
    d_terreno_base = RETIE_500KV["d_terreno_transitable_m"]
    d_terreno = distancia_terreno_con_altitud(d_terreno_base, altitud_msnm)

    d_entre_fases_minima = distancia_entre_fases_m(
        tension_linea_kv, longitud_cadena_m, flecha_max_m
    )

    # Ángulo de protección
    angulo_proteccion = math.degrees(math.atan2(cable_guarda_dh_m, cable_guarda_dv_m))
    cumple_blindaje = angulo_proteccion <= 30.0

    # Altura del apoyo del conductor
    h_apoyo = d_terreno + flecha_max_m + longitud_cadena_m + h_seguridad_m

    # Altura total: apoyo + separación a cable de guarda + remate
    h_total = h_apoyo + cable_guarda_dv_m + altura_remate_m

    # Número de estructuras
    n_estructuras = math.ceil((longitud_linea_km * 1000.0) / vano_diseno_m)

    # Distancia entre los 2 cables de guarda = 2 * (x_fase_externa - dh)
    # Fase externa está a separacion_fases_adoptada (9 m) del centro.
    # Los cables de guarda están a separacion_fases - dh respecto al centro
    d_entre_cables_guarda = 2.0 * (separacion_fases_adoptada_m - cable_guarda_dh_m)
    if d_entre_cables_guarda < 0:
        d_entre_cables_guarda = abs(d_entre_cables_guarda)

    return ResultadoTorre(
        tension_linea_kv=tension_linea_kv,
        altitud_msnm=altitud_msnm,
        d_terreno_m=d_terreno,
        d_entre_fases_m=d_entre_fases_minima,
        d_a_estructura_m=RETIE_500KV["d_estructura_m"],
        separacion_fases_adoptada_m=separacion_fases_adoptada_m,
        angulo_proteccion_grados=angulo_proteccion,
        cumple_blindaje=cumple_blindaje,
        cable_guarda_dh_m=cable_guarda_dh_m,
        cable_guarda_dv_m=cable_guarda_dv_m,
        altura_remate_m=altura_remate_m,
        d_entre_cables_guarda_m=d_entre_cables_guarda,
        n_cables_guarda=n_cables_guarda,
        flecha_max_m=flecha_max_m,
        longitud_cadena_m=longitud_cadena_m,
        h_apoyo_conductor_m=h_apoyo,
        h_total_torre_m=h_total,
        n_subconductores=n_subconductores,
        haz_separacion_m=haz_separacion_m,
        n_discos_aislador=n_discos_aislador,
        cadena_doble=cadena_doble,
        longitud_linea_km=longitud_linea_km,
        vano_diseno_m=vano_diseno_m,
        n_estructuras=n_estructuras,
    )
