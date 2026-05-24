"""Tests de regresión de cálculos contra el trabajo académico (500 kV / 307 km / 300 MW).

Verifica que los módulos `calculos/*` reproducen los valores del documento de
Naer (sección por sección). Tolerancia: ±0.5% para acumulación de redondeos.
"""
from __future__ import annotations

import math

import pytest

from calculos import (
    aisladores,
    geometria,
    linea_larga,
    mecanico,
    parametros,
    plantillado,
    tension,
    torre,
)


# Tolerancia genérica (0.5 % o 0.05 absoluto, lo que sea mayor)
def _close(actual: float, expected: float, rel: float = 0.005, abs_: float = 0.05) -> bool:
    return math.isclose(actual, expected, rel_tol=rel, abs_tol=abs_)


# ===== 2.1 SELECCIÓN DE TENSIÓN =====
def test_2_1_seleccion_tension():
    r = tension.calcular(potencia_mw=300, longitud_km=307)
    assert _close(r.hefner_kv, 960)
    # El doc reporta 312 kV con fórmula escrita errónea; el valor correcto es ~310.7
    assert _close(r.still_kv, 310.7, rel=0.01)
    assert _close(r.regla_1kvkm_kv, 307)
    assert r.tension_recomendada_kv == 500


# ===== 2.2 GEOMETRÍA =====
def test_2_2_geometria():
    r = geometria.calcular(
        d12_m=9, d23_m=9, d13_m=18,
        n_subc=3, db_m=0.40,
        r_conductor_mm=14.07, gmr_subconductor_mm=11.43,
    )
    assert _close(r.gmd_m, 11.339)
    assert _close(r.gmr_l_m, 0.1223)
    assert _close(r.gmr_c_m, 0.1311)
    assert _close(r.radio_circulo_envolvente_m, 0.2309)
    assert _close(r.rmg_corona_m, 0.1311)


# ===== 2.4 PARÁMETROS ELÉCTRICOS + CORONA =====
def test_2_4_parametros_y_corona():
    r = parametros.calcular(
        r_fase_ohm_km=0.0307, gmd_m=11.339, gmr_l_m=0.1223, gmr_c_m=0.1311,
        rmg_corona_m=0.1311, n_subc=3, radio_subc_mm=14.07,
        tension_linea_kv=500, longitud_km=307,
        altitud_msnm=1000, temperatura_c=25, factor_superficie=0.85,
        frecuencia_hz=60,
    )
    assert _close(r.r_fase_ohm_km, 0.0307)
    assert _close(r.l_fase_h_km * 1000, 0.9059)  # mH/km
    assert _close(r.xl_fase_ohm_km, 0.3415)
    assert _close(r.c_fase_f_km * 1e9, 12.47)  # nF/km
    assert _close(r.b_fase_s_km * 1e6, 4.702)  # µS/km
    assert _close(r.z_total_re, 9.425)
    assert _close(r.z_total_im, 104.84, rel=0.001)
    assert _close(r.y_total_im * 1e3, 1.4435)  # mS

    # Corona (doc: δ=0.87, Ec=28.22, Esup=21.69, Cs=1.30)
    assert _close(r.densidad_relativa, 0.87, rel=0.01)
    assert _close(r.gradiente_critico_kv_cm, 28.22, rel=0.01)
    assert _close(r.gradiente_superficial_kv_cm, 21.69)
    assert _close(r.coef_seguridad_corona, 1.30, rel=0.02)
    assert r.corona_cumple is True


# ===== 2.5 LÍNEA LARGA =====
def test_2_5_linea_larga():
    r = linea_larga.calcular(
        r_fase_ohm_km=0.0307, xl_fase_ohm_km=0.3415,
        b_fase_s_km=4.702e-6, longitud_km=307,
        tension_linea_kv=500, potencia_mw=300, factor_potencia=1.0,
    )
    assert _close(r.ir_a, 346.41)
    assert _close(r.vg_ll_kv, 472.37, rel=0.001)
    assert _close(r.ig_a, 519.0, rel=0.005)
    assert _close(r.pg_mw, 304.85, rel=0.002)
    assert _close(r.regulacion_pct, -5.53, rel=0.01)
    assert _close(r.perdidas_pct, 1.62, rel=0.02)
    assert _close(r.eficiencia_pct, 98.41)
    assert r.regulacion_cumple and r.perdidas_cumple


# ===== 3 CONDUCTOR CRÍTICO: validar valores del doc Tabla 8 y 9 =====
def test_3_mecanico_conductor_acsr_drake():
    """Reproduce los valores del documento (sección 3) para el conductor.

    Es la prueba más sensible: depende de que `encontrar_gobernante` elija
    C como base (no A como hacía la versión anterior).
    """
    r = mecanico.calcular(
        elemento="conductor", diametro_mm=28.14, area_mm2=468.5,
        masa_kg_m=1.628, carga_rotura_kgf=14288, vano_m=400,
        modulo_elasticidad_kgf_mm2=7838, coef_dilatacion_invc=18.9e-6,
    )
    assert _close(r.sigma_rotura_mpa, 298.87, rel=0.005)
    assert _close(r.vano_critico_ab_m, 145, rel=0.02)
    assert r.hipotesis_extrema == "A"  # vano 400 > ac 145
    assert r.hipotesis_gobernante == "C"  # FS=5 más restrictivo

    por_hip = {h.nombre: h for h in r.hipotesis}
    # Doc Tabla 8 (σ) + Tabla 9 (flechas)
    casos_doc = {
        "A": (105.78, 12.34),
        "B": (65.43, 10.46),
        "C": (59.77, 11.40),
        "D": (52.62, 12.94),
    }
    for nombre, (sigma_doc, flecha_doc) in casos_doc.items():
        h = por_hip[nombre]
        assert _close(h.sigma_calculado_mpa, sigma_doc, rel=0.005), \
            f"σ_{nombre}: got {h.sigma_calculado_mpa:.2f}, expected {sigma_doc}"
        assert _close(h.flecha_m, flecha_doc, rel=0.005), \
            f"f_{nombre}: got {h.flecha_m:.2f}, expected {flecha_doc}"
        assert h.cumple is True

    assert _close(r.flecha_maxima_m, 12.94)


def test_3_conductor_consistencia_cambio_estado():
    """Cumple consistencia interna: σ_C = σ_max,C (binding) y todos cumplen."""
    r = mecanico.calcular(
        elemento="conductor", diametro_mm=28.14, area_mm2=468.5,
        masa_kg_m=1.628, carga_rotura_kgf=14288, vano_m=400,
        modulo_elasticidad_kgf_mm2=7838, coef_dilatacion_invc=18.9e-6,
    )
    por_hip = {h.nombre: h for h in r.hipotesis}
    gob = por_hip[r.hipotesis_gobernante]
    # En la gobernante, σ = σ_max exactamente
    assert math.isclose(gob.sigma_calculado_mpa, gob.sigma_max_admisible_mpa, rel_tol=0.001)
    # Todas las demás cumplen
    for h in r.hipotesis:
        assert h.cumple, f"Hip {h.nombre} no cumple: σ={h.sigma_calculado_mpa} > σ_max={h.sigma_max_admisible_mpa}"


# ===== 4 CABLE DE GUARDA NO debe replicar el error del documento =====
def test_4_mecanico_guarda_consistencia():
    """El documento da σ_A=446.4 como gobernante para el guarda, pero eso
    viola σ_max,C=223. La app debe encontrar C como gobernante (resultado
    matemáticamente consistente).
    """
    r = mecanico.calcular(
        elemento="guarda", diametro_mm=11.1, area_mm2=72,
        masa_kg_m=0.583, carga_rotura_kgf=8200, vano_m=400,
        modulo_elasticidad_kgf_mm2=19367,  # ~190 000 N/mm² / 9.81
        coef_dilatacion_invc=11.5e-6,
    )
    assert r.hipotesis_gobernante == "C"
    por_hip = {h.nombre: h for h in r.hipotesis}
    gob = por_hip["C"]
    assert math.isclose(gob.sigma_calculado_mpa, gob.sigma_max_admisible_mpa, rel_tol=0.001)

    # Todas cumplen
    for h in r.hipotesis:
        assert h.cumple, f"Guarda Hip {h.nombre} no cumple"

    # σ_A ~ 356 MPa (cálculo correcto, NO el 446.4 del doc)
    assert 340 < por_hip["A"].sigma_calculado_mpa < 370
    # σ_D ~ 193 MPa (cálculo correcto, NO el 121.5 del doc)
    assert 180 < por_hip["D"].sigma_calculado_mpa < 210


def test_4_blindaje_guarda_sobre_conductor():
    """La flecha del guarda debe ser menor que la del conductor (blindaje)."""
    rc = mecanico.calcular(
        elemento="conductor", diametro_mm=28.14, area_mm2=468.5,
        masa_kg_m=1.628, carga_rotura_kgf=14288, vano_m=400,
        modulo_elasticidad_kgf_mm2=7838, coef_dilatacion_invc=18.9e-6,
    )
    rg = mecanico.calcular(
        elemento="guarda", diametro_mm=11.1, area_mm2=72,
        masa_kg_m=0.583, carga_rotura_kgf=8200, vano_m=400,
        modulo_elasticidad_kgf_mm2=19367, coef_dilatacion_invc=11.5e-6,
    )
    # f_guarda_max < f_conductor_max → preserva zona de protección
    assert rg.flecha_maxima_m < rc.flecha_maxima_m


# ===== 5 AISLADORES =====
def test_5_aisladores():
    r = aisladores.calcular(
        tension_linea_kv=500, bil_kv=1550,
        nivel_contaminacion="alta",  # k=25
        carga_total_kgf=15360,
    )
    assert r.k_contaminacion_mm_kv == 25
    assert r.n_discos_por_fuga == 41
    # BIL: ceil(41.33) = 42 (mat. correcto, doc redondea a 41 con criterio laxo)
    assert r.n_discos_por_bil in (41, 42)
    assert r.n_discos_adoptado in (41, 42)
    assert _close(r.longitud_cadena_m, 6.39, abs_=0.2)
    assert _close(r.peso_cadena_kg, 254.6, abs_=10)
    assert _close(r.fs_cadena_simple, 1.09, rel=0.02)
    assert _close(r.fs_cadena_doble, 2.19, rel=0.02)


# ===== 6 TORRE =====
def test_6_torre():
    r = torre.calcular(
        tension_linea_kv=500, altitud_msnm=1000,
        flecha_max_m=12.94, longitud_cadena_m=6.39,
        longitud_linea_km=307, vano_diseno_m=400,
    )
    assert _close(r.d_terreno_m, 9.0)
    assert _close(r.d_entre_fases_m, 8.40, rel=0.01)
    assert _close(r.angulo_proteccion_grados, 28.6, rel=0.01)
    assert _close(r.h_apoyo_conductor_m, 29.33)
    assert _close(r.h_total_torre_m, 39.83)
    assert r.n_estructuras == 768
    assert r.cumple_blindaje is True


# ===== CONSISTENCIA: cadena completa que replica api_modulo_11_calcular =====
def test_consistencia_resumen_vs_modulos_individuales():
    """El resumen (módulo 11) debe producir EXACTAMENTE los mismos números
    que cada módulo individual cuando se ejecuta toda la cadena. Antes
    fallaba porque parametros.calcular() recibía kwargs equivocados y se
    silenciaba con `except Exception: None`, cayendo a defaults (xL=0.4,
    b=4e-6) y usando R sin dividir por n_subc."""
    # Defaults del proyecto (data/proyectos.json)
    v_kv, p_mw, l_km, alt, fp, vano = 500.0, 300.0, 307.0, 1000.0, 1.0, 400.0
    n_subc, db = 3, 0.40
    # Conductor ACSR Drake (static/data/conductores.json)
    r_subc, radio, gmr_mm, area, masa, rotura = 0.0921, 14.07, 11.43, 468.5, 1.628, 14288
    e_n_mm2, alpha = 76900, 18.9e-6

    # Cadena tal como debe ejecutarla el resumen
    r_geom = geometria.calcular(
        d12_m=9.0, d23_m=9.0, d13_m=18.0,
        n_subc=n_subc, db_m=db, r_conductor_mm=radio, gmr_subconductor_mm=gmr_mm,
    )
    r_fase = r_subc / n_subc
    r_param = parametros.calcular(
        r_fase_ohm_km=r_fase, gmd_m=r_geom.gmd_m, gmr_l_m=r_geom.gmr_l_m,
        gmr_c_m=r_geom.gmr_c_m, rmg_corona_m=r_geom.rmg_corona_m,
        n_subc=n_subc, radio_subc_mm=radio,
        tension_linea_kv=v_kv, longitud_km=l_km, altitud_msnm=alt,
    )
    r_ll = linea_larga.calcular(
        r_fase_ohm_km=r_param.r_fase_ohm_km, xl_fase_ohm_km=r_param.xl_fase_ohm_km,
        b_fase_s_km=r_param.b_fase_s_km, longitud_km=l_km, tension_linea_kv=v_kv,
        potencia_mw=p_mw, factor_potencia=fp,
    )
    # Resultados que el módulo 5 muestra y que el resumen DEBE replicar:
    assert _close(abs(r_ll.zc_re), 269.78, rel=0.005), \
        f"|Zc|: got {abs(r_ll.zc_re):.2f}, expected ~269.78 (módulo 5)"
    assert _close(r_ll.vg_ll_kv, 472.4, rel=0.005)
    assert _close(r_ll.regulacion_pct, -5.51, rel=0.02)
    assert _close(r_ll.perdidas_pct, 1.61, rel=0.02)
    assert _close(r_ll.eficiencia_pct, 98.42, rel=0.005)

    # Regresión específica: NO usar el bug viejo (r=0.0921, xL=0.4, b=4e-6)
    # que daba |Zc|316, Reg-2.9%, Perd4.4%, Efic95.8%
    assert not _close(abs(r_ll.zc_re), 320.3, rel=0.05), \
        "regresión: estás usando los defaults del bug (xL=0.4, b=4e-6)"
    assert r_ll.eficiencia_pct > 98.0, \
        f"regresión: η={r_ll.eficiencia_pct:.2f}% sugiere R sin dividir por n_subc"


# ===== 7 PLANTILLADO =====
def test_7_plantillado_con_wr_explicito():
    """Con Wr explícito (recomendado), la flecha incluye el viento de la
    hipótesis fría B, igual que el doc Sec 7.4 (f_B = 10.46 m)."""
    r = plantillado.calcular(
        vano_m=400,
        tension_caliente_n=24652,  # Hip D
        tension_frio_n=30654,       # Hip B
        masa_kg_m=1.628,
        wr_caliente_n_m=15.95,     # Hip D: sin viento
        wr_frio_n_m=16.04,         # Hip B: con viento 35 km/h
        distancia_min_terreno_m=9.0,
        altura_apoyo_conductor_m=29.33,
    )
    assert _close(r.flecha_max_m, 12.94, rel=0.005)
    assert _close(r.flecha_min_m, 10.46, rel=0.005)  # doc Sec 7.4
    c_caliente = r.curvas[0].parametro_c_m
    c_frio = r.curvas[3].parametro_c_m
    assert _close(c_caliente, 1545, rel=0.01)
    assert _close(c_frio, 1911, rel=0.01)


def test_7_plantillado_consistencia_con_mecanico():
    """Plantillado y mecánico DEBEN producir la misma flecha cuando se
    pasan los Wr reales del mecánico."""
    mec = mecanico.calcular(
        elemento="conductor", diametro_mm=28.14, area_mm2=468.5,
        masa_kg_m=1.628, carga_rotura_kgf=14288, vano_m=400,
        modulo_elasticidad_kgf_mm2=7838, coef_dilatacion_invc=18.9e-6,
    )
    hip_d = next(h for h in mec.hipotesis if h.nombre == "D")
    hip_b = next(h for h in mec.hipotesis if h.nombre == "B")

    plant = plantillado.calcular(
        vano_m=400,
        tension_caliente_n=hip_d.tension_n,
        tension_frio_n=hip_b.tension_n,
        masa_kg_m=1.628,
        wr_caliente_n_m=hip_d.wr_n_m,
        wr_frio_n_m=hip_b.wr_n_m,
    )
    # Mismas flechas que mecánico (hasta tolerancia numérica)
    assert math.isclose(plant.flecha_max_m, hip_d.flecha_m, rel_tol=1e-4)
    assert math.isclose(plant.flecha_min_m, hip_b.flecha_m, rel_tol=1e-4)


def test_7_plantillado_fallback_sin_wr():
    """Sin Wr explícito, plantillado usa peso propio (m·g) como fallback."""
    r = plantillado.calcular(
        vano_m=400, tension_caliente_n=24652, tension_frio_n=30654,
        masa_kg_m=1.628,
    )
    # Sin Wr, usa m·g = 1.628·9.81 = 15.97 (ligeramente distinto al Wr con viento)
    assert _close(r.flecha_max_m, 12.94, rel=0.01)
    # Sin Wr para frío, la flecha es menor que la real (10.40 vs 10.46)
    assert r.flecha_min_m < 10.45
