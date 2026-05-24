"""Flask app principal: tour educativo de diseño de línea de transmisión 500 kV."""
from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, session, url_for

from calculos import (
    aisladores,
    conductor,
    geometria,
    linea_larga,
    mecanico,
    parametros,
    plantillado,
    tension,
    torre,
)
from config import get_config
from figuras import (
    fig_aisladores,
    fig_conductor,
    fig_geometria,
    fig_linea_larga,
    fig_mecanico,
    fig_parametros,
    fig_plantillado,
    fig_tension,
    fig_torre,
)


# Definición de los 11 módulos: (id, slug, nombre, descripción corta, sección, numeración)
# Estructura exacta del documento académico (7 secciones):
#   1. PARÁMETROS                     → módulo 0
#   2. CÁLCULOS ELÉCTRICOS            → módulos 1-5 (2.1-2.5)
#   3. MECÁNICA DEL CONDUCTOR         → módulo 6
#   4. MECÁNICA DEL CABLE DE GUARDA   → módulo 7
#   5. SELECCIÓN DE LOS AISLADORES    → módulo 8
#   6. DISEÑO DE LA TORRE             → módulo 9
#   7. PLANTILLADO                    → módulo 10
MODULOS: list[tuple[int, str, str, str, str, str]] = [
    # (id, slug, nombre, descripción, sección, numeración)
    (0, "inicio", "Parámetros del proyecto", "Datos eléctricos y mecánicos iniciales", "1. PARÁMETROS", "1"),

    (1, "tension", "Selección del nivel de tensión", "Hefner, Still, 1 kV/km vs escalones normalizados", "2. CÁLCULOS ELÉCTRICOS", "2.1"),
    (2, "configuracion", "Configuración de la línea", "GMD, GMR, radio del haz y geometría de fases", "2. CÁLCULOS ELÉCTRICOS", "2.2"),
    (3, "conductor", "Datos del conductor", "ACSR/AAAC/ACAR — R, ampacidad, corrección térmica", "2. CÁLCULOS ELÉCTRICOS", "2.3"),
    (4, "parametros", "Parámetros R, L, C + Corona", "Inductancia, capacitancia y efecto Corona", "2. CÁLCULOS ELÉCTRICOS", "2.4"),
    (5, "linea_larga", "Línea larga (modelo ABCD)", "Regulación, pérdidas y eficiencia (cuadripolo)", "2. CÁLCULOS ELÉCTRICOS", "2.5"),

    (6, "mecanico", "Mecánica del conductor", "4 hipótesis, vano crítico, ecuación de cambio de estado", "3. MECÁNICA DEL CONDUCTOR", "3"),

    (7, "guarda", "Mecánica del cable de guarda", "Acero EHS / Alumoweld / OPGW, 4 hipótesis", "4. MECÁNICA DEL CABLE DE GUARDA", "4"),

    (8, "aisladores", "Cálculo de los aisladores", "N discos por fuga y BIL, longitud, peso, FS", "5. SELECCIÓN DE LOS AISLADORES", "5"),

    (9, "torre", "Diseño de la torre", "Posicionamiento guarda, distancias RETIE, altura", "6. DISEÑO DE LA TORRE", "6"),

    (10, "plantillado", "Plantillado", "4 curvas patrón sobre perfil topográfico", "7. PLANTILLADO", "7"),

    (11, "resumen", "Resumen del diseño", "Memoria de cálculo consolidada de todos los módulos", "8. RESUMEN FINAL", "8"),
]


# Cargar catálogos desde JSON (al iniciar la app)
DATA_DIR = Path(__file__).parent / "static" / "data"


def _load_catalog(filename: str) -> dict:
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


CATALOGO_CONDUCTORES = _load_catalog("conductores.json")
CATALOGO_AISLADORES = _load_catalog("aisladores.json")
CATALOGO_CABLES_GUARDA = _load_catalog("cables_guarda.json")


def _get_conductor(conductor_id: str | None = None) -> dict:
    """Retorna el dict del conductor seleccionado (o el default)."""
    if not conductor_id:
        conductor_id = CATALOGO_CONDUCTORES["default_id"]
    for c in CATALOGO_CONDUCTORES["conductores"]:
        if c["id"] == conductor_id:
            return c
    return CATALOGO_CONDUCTORES["conductores"][0]


def _get_aislador(aislador_id: str | None = None) -> dict:
    if not aislador_id:
        aislador_id = CATALOGO_AISLADORES["default_id"]
    for a in CATALOGO_AISLADORES["aisladores"]:
        if a["id"] == aislador_id:
            return a
    return CATALOGO_AISLADORES["aisladores"][0]


def _get_cable_guarda(cable_id: str | None = None) -> dict:
    if not cable_id:
        cable_id = CATALOGO_CABLES_GUARDA["default_id"]
    for c in CATALOGO_CABLES_GUARDA["cables"]:
        if c["id"] == cable_id:
            return c
    return CATALOGO_CABLES_GUARDA["cables"][0]


def _get_proyecto(app: Flask) -> dict:
    """Merge defaults del proyecto con valores guardados en sesión."""
    base = dict(app.config["PROYECTO_DEFAULTS"])
    # Sobrescribir con valores de sesión si existen
    overrides = session.get("proyecto", {})
    # Migración: reemplazar nombres antiguos por el actual
    nombres_obsoletos = {
        "Línea de Transmisión 500 kV",
        "Cálculo Línea de Transmisión",
    }
    if overrides.get("nombre") in nombres_obsoletos:
        overrides = dict(overrides)
        overrides["nombre"] = base["nombre"]
        session["proyecto"] = overrides
    base.update(overrides)
    return base


def _build_navegacion(modulo_id: int) -> dict:
    """Calcula contexto de navegación común para los módulos."""
    return {
        "modulo_id": modulo_id,
        "modulo_info": MODULOS[modulo_id],
        "anterior": modulo_id - 1 if modulo_id > 0 else None,
        "siguiente": modulo_id + 1 if modulo_id < len(MODULOS) - 1 else None,
        "progreso_pct": int((modulo_id + 1) / len(MODULOS) * 100),
    }


def _f(value, default):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _i(value, default):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# Mapping de nombres de campo del form → nombre de propiedad en proyecto session
# (algunos formularios usan nombres ligeramente distintos: tension_kv vs tension_nominal_kv)
_CAMPO_ALIAS = {
    "tension_kv": "tension_nominal_kv",
    "longitud_km": "longitud_km",
    "potencia_mw": "potencia_mw",
    "altitud_msnm": "altitud_msnm",
    "vano_m": "vano_diseno_m",
    "factor_potencia": "factor_potencia",
}


def _sync_form_to_session(req) -> None:
    """Guarda en sesión cualquier campo del formulario que coincida con un parámetro global.

    Esto permite sincronización bidireccional: cambiar potencia en módulo 1 también
    actualiza el valor que se ve en el módulo 5 y en el resumen del Inicio.
    """
    proy = session.get("proyecto", {})
    for form_key, session_key in _CAMPO_ALIAS.items():
        val = req.form.get(form_key)
        if val is not None and val.strip():
            try:
                proy[session_key] = float(val)
            except ValueError:
                pass
    session["proyecto"] = proy


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())

    @app.context_processor
    def inject_globals():
        return {
            "MODULOS": MODULOS,
            "PROYECTO": _get_proyecto(app),
            "CONDUCTOR": _get_conductor(session.get("conductor_id")),
            "AISLADOR": _get_aislador(session.get("aislador_id")),
            "CABLE_GUARDA": _get_cable_guarda(session.get("cable_guarda_id")),
            "CATALOGO_CONDUCTORES": CATALOGO_CONDUCTORES["conductores"],
            "CATALOGO_AISLADORES": CATALOGO_AISLADORES["aisladores"],
            "CATALOGO_CABLES_GUARDA": CATALOGO_CABLES_GUARDA["cables"],
        }

    # ===== Rutas de páginas =====

    @app.route("/")
    def index():
        return redirect(url_for("modulo", modulo_id=0))

    @app.route("/modulo/<int:modulo_id>")
    def modulo(modulo_id: int):
        if modulo_id < 0 or modulo_id >= len(MODULOS):
            abort(404)
        nav = _build_navegacion(modulo_id)
        template_name = f"modulo_{modulo_id}_{nav['modulo_info'][1]}.html"
        return render_template(template_name, **nav)

    # ===== Endpoint para actualizar parámetros globales del proyecto =====

    @app.post("/api/proyecto/actualizar")
    def api_proyecto_actualizar():
        """Guarda los parámetros principales en la sesión y devuelve el resumen actualizado.

        Recalcula automáticamente la tensión nominal cuando cambian P o L.
        El usuario NO edita tension_nominal_kv directamente — es un cálculo.
        """
        proyecto_session = session.get("proyecto", {})

        # Campos numéricos (eléctricos, geométricos y mecánicos)
        # NOTA: tension_nominal_kv NO se acepta del form — siempre se calcula.
        campos_floats = [
            # Eléctricos
            "longitud_km", "potencia_mw",
            "factor_potencia", "frecuencia_hz",
            "altitud_msnm",
            "temperatura_max_conductor_c", "temperatura_min_ambiente_c",
            "velocidad_viento_max_kmh",
            "regulacion_max_pct", "perdidas_max_pct",
            # Geométricos
            "vano_diseno_m", "haz_separacion_m",
            # Mecánicos — 4 hipótesis (16 campos)
            "hip_a_viento_kmh", "hip_a_temperatura_c", "hip_a_delta_temp_c", "hip_a_fs",
            "hip_b_viento_kmh", "hip_b_temperatura_c", "hip_b_delta_temp_c", "hip_b_fs",
            "hip_c_viento_kmh", "hip_c_temperatura_c", "hip_c_delta_temp_c", "hip_c_fs",
            "hip_d_viento_kmh", "hip_d_temperatura_c", "hip_d_delta_temp_c", "hip_d_fs",
        ]
        for campo in campos_floats:
            val = request.form.get(campo)
            if val is not None and val.strip():
                try:
                    proyecto_session[campo] = float(val)
                except ValueError:
                    pass

        # Campos enteros
        for campo in ("haz_subconductores", "n_discos_aislador"):
            val = request.form.get(campo)
            if val is not None and val.strip():
                try:
                    proyecto_session[campo] = int(float(val))
                except ValueError:
                    pass

        # Campos de texto (nombre, corredor)
        campos_texto = ["nombre", "corredor", "conductor_tipo"]
        for campo in campos_texto:
            val = request.form.get(campo)
            if val is not None and val.strip():
                proyecto_session[campo] = val.strip()[:200]

        # AUTO-CÁLCULO DE TENSIÓN NOMINAL
        # Si tenemos P y L, calculamos la tensión recomendada según RETIE
        # (Hefner + Still + 1kV/km → escalón normalizado >= máximo)
        p = proyecto_session.get("potencia_mw") or app.config["PROYECTO_DEFAULTS"]["potencia_mw"]
        l_ = proyecto_session.get("longitud_km") or app.config["PROYECTO_DEFAULTS"]["longitud_km"]
        try:
            r_tension = tension.calcular(float(p), float(l_))
            proyecto_session["tension_nominal_kv"] = float(r_tension.tension_recomendada_kv)
            proyecto_session["_tension_justificacion"] = r_tension.justificacion
            proyecto_session["_tension_hefner_kv"] = r_tension.hefner_kv
            proyecto_session["_tension_still_kv"] = r_tension.still_kv
            proyecto_session["_tension_1kvkm_kv"] = r_tension.regla_1kvkm_kv
        except (ValueError, TypeError):
            pass  # mantener el valor anterior si los inputs no son válidos

        session["proyecto"] = proyecto_session
        proy = _get_proyecto(app)
        return render_template("_partial_proyecto_resumen.html", PROYECTO=proy)

    # ===== Endpoints de cálculo (HTMX) =====

    @app.post("/api/modulo/1/calcular")
    def api_modulo_1_calcular():
        _sync_form_to_session(request)
        p = _f(request.form.get("potencia_mw"), 300)
        l_ = _f(request.form.get("longitud_km"), 307)
        try:
            r = tension.calcular(p, l_)
        except ValueError as e:
            return (f"<div class='text-danger'>{e}</div>", 400)
        # CRÍTICO: guardar la tensión recomendada en sesión para que
        # los módulos 2-10 usen el valor calculado, no el anterior.
        proy = session.get("proyecto", {})
        proy["tension_nominal_kv"] = float(r.tension_recomendada_kv)
        session["proyecto"] = proy
        return render_template(
            "_partial_modulo_1_resultado.html",
            r=r, figura_b64=fig_tension.generar(r),
        )

    @app.post("/api/modulo/2/calcular")
    def api_modulo_2_calcular():
        _sync_form_to_session(request)
        d12 = _f(request.form.get("d12_m"), 9.0)
        d23 = _f(request.form.get("d23_m"), 9.0)
        d13 = _f(request.form.get("d13_m"), 18.0)
        n = _i(request.form.get("n_subc"), 3)
        db = _f(request.form.get("db_m"), 0.40)
        # Usar el conductor seleccionado en sesión
        cond = _get_conductor(session.get("conductor_id"))
        try:
            r = geometria.calcular(
                d12_m=d12, d23_m=d23, d13_m=d13, n_subc=n, db_m=db,
                r_conductor_mm=cond["radio_fisico_mm"],
                gmr_subconductor_mm=cond["gmr_mm"],
            )
        except ValueError as e:
            return (f"<div class='text-danger'>{e}</div>", 400)
        return render_template(
            "_partial_modulo_2_resultado.html",
            r=r, figura_b64=fig_geometria.generar(r),
        )

    @app.post("/api/modulo/3/calcular")
    def api_modulo_3_calcular():
        _sync_form_to_session(request)
        # Guardar la selección del conductor en sesión
        conductor_id = request.form.get("conductor_id")
        if conductor_id:
            session["conductor_id"] = conductor_id
        cond = _get_conductor(conductor_id)

        n_subc = _i(request.form.get("n_subc"), 3)
        long_km = _f(request.form.get("longitud_km"), 307)
        t_op = _f(request.form.get("temperatura_op_c"), 65)

        r = conductor.calcular(
            resistencia_subc_ohm_km=cond["resistencia_ac_65c_ohm_km"],
            ampacidad_subc_a=cond["ampacidad_a"],
            n_subc=n_subc, longitud_km=long_km, temperatura_op_c=t_op,
        )
        return render_template(
            "_partial_modulo_3_resultado.html",
            r=r, cond=cond,
            figura_b64=fig_conductor.generar(
                diametro_exterior_mm=cond["diametro_exterior_mm"],
            ),
        )

    @app.post("/api/modulo/4/calcular")
    def api_modulo_4_calcular():
        _sync_form_to_session(request)
        cond = _get_conductor(session.get("conductor_id"))
        n_subc = _i(request.form.get("n_subc"), 3)
        db = _f(request.form.get("db_m"), 0.40)
        v_kv = _f(request.form.get("tension_kv"), 500)
        alt = _f(request.form.get("altitud_msnm"), 1000)
        long_km = _f(request.form.get("longitud_km"), 307)

        geo = geometria.calcular(
            d12_m=9.0, d23_m=9.0, d13_m=18.0, n_subc=n_subc, db_m=db,
            r_conductor_mm=cond["radio_fisico_mm"],
            gmr_subconductor_mm=cond["gmr_mm"],
        )
        r_fase = cond["resistencia_ac_65c_ohm_km"] / n_subc

        try:
            r = parametros.calcular(
                r_fase_ohm_km=r_fase,
                gmd_m=geo.gmd_m, gmr_l_m=geo.gmr_l_m, gmr_c_m=geo.gmr_c_m,
                rmg_corona_m=geo.rmg_corona_m,
                n_subc=n_subc,
                radio_subc_mm=cond["radio_fisico_mm"],
                tension_linea_kv=v_kv, longitud_km=long_km, altitud_msnm=alt,
            )
        except ValueError as e:
            return (f"<div class='text-danger'>{e}</div>", 400)

        return render_template(
            "_partial_modulo_4_resultado.html",
            r=r, cond=cond,
            figura_b64=fig_parametros.generar(r),
        )

    @app.post("/api/modulo/5/calcular")
    def api_modulo_5_calcular():
        _sync_form_to_session(request)
        cond = _get_conductor(session.get("conductor_id"))
        n_subc = 3
        geo = geometria.calcular(
            d12_m=9.0, d23_m=9.0, d13_m=18.0, n_subc=n_subc, db_m=0.40,
            r_conductor_mm=cond["radio_fisico_mm"],
            gmr_subconductor_mm=cond["gmr_mm"],
        )
        r_fase = cond["resistencia_ac_65c_ohm_km"] / n_subc
        param = parametros.calcular(
            r_fase_ohm_km=r_fase,
            gmd_m=geo.gmd_m, gmr_l_m=geo.gmr_l_m, gmr_c_m=geo.gmr_c_m,
            rmg_corona_m=geo.rmg_corona_m, n_subc=n_subc,
            radio_subc_mm=cond["radio_fisico_mm"],
            tension_linea_kv=500, longitud_km=307, altitud_msnm=1000,
        )

        p_mw = _f(request.form.get("potencia_mw"), 300)
        v_kv = _f(request.form.get("tension_kv"), 500)
        l_km = _f(request.form.get("longitud_km"), 307)
        fp = _f(request.form.get("factor_potencia"), 1.0)

        try:
            r = linea_larga.calcular(
                r_fase_ohm_km=param.r_fase_ohm_km,
                xl_fase_ohm_km=param.xl_fase_ohm_km,
                b_fase_s_km=param.b_fase_s_km,
                longitud_km=l_km, tension_linea_kv=v_kv,
                potencia_mw=p_mw, factor_potencia=fp,
            )
        except ValueError as e:
            return (f"<div class='text-danger'>{e}</div>", 400)

        return render_template(
            "_partial_modulo_5_resultado.html",
            r=r, cond=cond,
            figura_b64=fig_linea_larga.generar(r),
        )

    @app.post("/api/modulo/6/calcular")
    def api_modulo_6_calcular():
        _sync_form_to_session(request)
        cond = _get_conductor(session.get("conductor_id"))
        vano = _f(request.form.get("vano_m"), 400)
        desnivel = _f(request.form.get("desnivel_m"), 0.0)
        # Conversión del módulo de elasticidad N/mm² → kgf/mm² (÷9.81)
        e_n_mm2 = cond.get("modulo_elasticidad_n_mm2", 76900)
        e_kgf_mm2 = e_n_mm2 / 9.81
        alpha = cond.get("coef_dilatacion_invc", 18.9e-6)
        r = mecanico.calcular(
            elemento="conductor",
            diametro_mm=cond["diametro_exterior_mm"],
            area_mm2=cond["seccion_total_mm2"],
            masa_kg_m=cond["masa_kg_m"],
            carga_rotura_kgf=cond["carga_rotura_kgf"],
            vano_m=vano,
            modulo_elasticidad_kgf_mm2=e_kgf_mm2,
            coef_dilatacion_invc=alpha,
            desnivel_m=desnivel,
        )
        return render_template(
            "_partial_modulo_6_resultado.html",
            r=r, cond=cond,
            figura_b64=fig_mecanico.generar(r),
        )

    @app.post("/api/modulo/7/calcular")
    def api_modulo_7_calcular():
        _sync_form_to_session(request)
        # Guardar selección de cable de guarda en sesión
        cable_id = request.form.get("cable_guarda_id")
        if cable_id:
            session["cable_guarda_id"] = cable_id
        cable = _get_cable_guarda(cable_id)

        vano = _f(request.form.get("vano_m"), 400)
        # Cable de guarda (acero): E ≈ 20000 kgf/mm², α ≈ 11.5e-6 /°C
        e_kgf_mm2 = cable.get("modulo_elasticidad_n_mm2", 196000) / 9.81
        alpha = cable.get("coef_dilatacion_invc", 11.5e-6)
        r = mecanico.calcular(
            elemento="guarda",
            diametro_mm=cable["diametro_mm"],
            area_mm2=cable["seccion_mm2"],
            masa_kg_m=cable["masa_kg_m"],
            carga_rotura_kgf=cable["carga_rotura_kgf"],
            vano_m=vano,
            modulo_elasticidad_kgf_mm2=e_kgf_mm2,
            coef_dilatacion_invc=alpha,
        )
        return render_template(
            "_partial_modulo_7_resultado.html",
            r=r, cable=cable,
            figura_b64=fig_mecanico.generar(r),
        )

    @app.post("/api/modulo/8/calcular")
    def api_modulo_8_calcular():
        _sync_form_to_session(request)
        # Guardar selección de aislador en sesión
        aislador_id = request.form.get("aislador_id")
        if aislador_id:
            session["aislador_id"] = aislador_id
        aisl = _get_aislador(aislador_id)

        v_kv = _f(request.form.get("tension_kv"), 500)
        nivel = request.form.get("nivel_contaminacion", "alta")
        try:
            r = aisladores.calcular(
                tension_linea_kv=v_kv,
                nivel_contaminacion=nivel,
                aislador=aisl,
            )
        except ValueError as e:
            return (f"<div class='text-danger'>{e}</div>", 400)
        return render_template(
            "_partial_modulo_8_resultado.html",
            r=r, aisl=aisl,
            figura_b64=fig_aisladores.generar(r),
        )

    @app.post("/api/modulo/9/calcular")
    def api_modulo_9_calcular():
        _sync_form_to_session(request)
        v_kv = _f(request.form.get("tension_kv"), 500)
        alt = _f(request.form.get("altitud_msnm"), 1000)
        flecha = _f(request.form.get("flecha_max_m"), 12.94)
        cadena = _f(request.form.get("longitud_cadena_m"), 6.39)
        long_km = _f(request.form.get("longitud_km"), 307)
        vano = _f(request.form.get("vano_m"), 400)
        # Datos adicionales para diagrama detallado (tomados de sesión/proyecto)
        proy = _get_proyecto(app)
        n_subc = int(proy.get("haz_subconductores", 3))
        db = float(proy.get("haz_separacion_m", 0.40))
        n_discos = int(proy.get("n_discos_aislador", 41))
        r = torre.calcular(
            tension_linea_kv=v_kv, altitud_msnm=alt,
            flecha_max_m=flecha, longitud_cadena_m=cadena,
            longitud_linea_km=long_km, vano_diseno_m=vano,
            n_subconductores=n_subc,
            haz_separacion_m=db,
            n_discos_aislador=n_discos,
            cadena_doble=True,  # estándar en 500 kV
            n_cables_guarda=2,
        )
        return render_template(
            "_partial_modulo_9_resultado.html",
            r=r, figura_b64=fig_torre.generar(r),
        )

    @app.post("/api/modulo/10/calcular")
    def api_modulo_10_calcular():
        _sync_form_to_session(request)
        cond = _get_conductor(session.get("conductor_id"))
        vano = _f(request.form.get("vano_m"), 400)
        mec = mecanico.calcular(
            elemento="conductor",
            diametro_mm=cond["diametro_exterior_mm"],
            area_mm2=cond["seccion_total_mm2"],
            masa_kg_m=cond["masa_kg_m"],
            carga_rotura_kgf=cond["carga_rotura_kgf"],
            vano_m=vano,
        )
        hip_d = next((h for h in mec.hipotesis if h.nombre == "D"), mec.hipotesis[-1])
        hip_b = next((h for h in mec.hipotesis if h.nombre == "B"), mec.hipotesis[1])

        r = plantillado.calcular(
            vano_m=vano,
            tension_caliente_n=hip_d.tension_n,
            tension_frio_n=hip_b.tension_n,
            masa_kg_m=cond["masa_kg_m"],
        )
        return render_template(
            "_partial_modulo_10_resultado.html",
            r=r, cond=cond,
            figura_b64=fig_plantillado.generar(r),
        )

    @app.post("/api/modulo/11/calcular")
    def api_modulo_11_calcular():
        """Resumen: recalcula TODO con los parámetros actuales de sesión."""
        proy = _get_proyecto(app)
        cond = _get_conductor(session.get("conductor_id"))
        aisl = _get_aislador(session.get("aislador_id"))
        cable = _get_cable_guarda(session.get("cable_guarda_id"))

        resumen = {"proyecto": proy, "conductor": cond, "aislador": aisl, "cable_guarda": cable}

        # 2.1 Tensión nominal
        try:
            r_tension = tension.calcular(float(proy["potencia_mw"]), float(proy["longitud_km"]))
            resumen["tension"] = r_tension
        except Exception:
            resumen["tension"] = None

        # 2.2 Geometría (configuración estándar)
        try:
            r_geom = geometria.calcular(d12_m=9.0, d23_m=9.0, d13_m=18.0,
                                         n_subconductores=3, db_m=0.40,
                                         radio_conductor_mm=cond["radio_fisico_mm"],
                                         gmr_conductor_mm=cond["gmr_mm"])
            resumen["geometria"] = r_geom
        except Exception:
            resumen["geometria"] = None

        # 2.3 Conductor (datos ya están en cond)
        # 2.4 Parámetros R, L, C + Corona
        try:
            r_param = parametros.calcular(
                tension_linea_kv=float(proy["tension_nominal_kv"]),
                n_subconductores=3,
                db_m=0.40,
                altitud_msnm=float(proy["altitud_msnm"]),
                longitud_km=float(proy["longitud_km"]),
                radio_conductor_mm=cond["radio_fisico_mm"],
                gmr_conductor_mm=cond["gmr_mm"],
                resistencia_conductor_ohm_km=cond["resistencia_ac_65c_ohm_km"],
            )
            resumen["parametros"] = r_param
        except Exception:
            resumen["parametros"] = None

        # 2.5 Línea larga ABCD
        try:
            r_ll = linea_larga.calcular(
                tension_linea_kv=float(proy["tension_nominal_kv"]),
                potencia_mw=float(proy["potencia_mw"]),
                longitud_km=float(proy["longitud_km"]),
                factor_potencia=float(proy["factor_potencia"]),
                r_fase_ohm_km=cond["resistencia_ac_65c_ohm_km"],
                xl_fase_ohm_km=resumen["parametros"].xl_fase_ohm_km if resumen["parametros"] else 0.4,
                b_fase_s_km=resumen["parametros"].b_fase_s_km if resumen["parametros"] else 4e-6,
                reg_max_pct=float(proy["regulacion_max_pct"]),
                perdidas_max_pct=float(proy["perdidas_max_pct"]),
            )
            resumen["linea_larga"] = r_ll
        except Exception:
            resumen["linea_larga"] = None

        # 3 Mecánica del conductor
        try:
            e_kgf = cond.get("modulo_elasticidad_n_mm2", 76900) / 9.81
            alpha = cond.get("coef_dilatacion_invc", 18.9e-6)
            r_mec = mecanico.calcular(
                elemento="conductor",
                diametro_mm=cond["diametro_exterior_mm"],
                area_mm2=cond["seccion_total_mm2"],
                masa_kg_m=cond["masa_kg_m"],
                carga_rotura_kgf=cond["carga_rotura_kgf"],
                vano_m=float(proy["vano_diseno_m"]),
                modulo_elasticidad_kgf_mm2=e_kgf,
                coef_dilatacion_invc=alpha,
            )
            resumen["mecanico"] = r_mec
        except Exception:
            resumen["mecanico"] = None

        # 4 Cable de guarda
        try:
            e_kgf_g = cable.get("modulo_elasticidad_n_mm2", 196000) / 9.81
            alpha_g = cable.get("coef_dilatacion_invc", 11.5e-6)
            r_guarda = mecanico.calcular(
                elemento="guarda",
                diametro_mm=cable["diametro_mm"],
                area_mm2=cable["seccion_mm2"],
                masa_kg_m=cable["masa_kg_m"],
                carga_rotura_kgf=cable["carga_rotura_kgf"],
                vano_m=float(proy["vano_diseno_m"]),
                modulo_elasticidad_kgf_mm2=e_kgf_g,
                coef_dilatacion_invc=alpha_g,
            )
            resumen["guarda"] = r_guarda
        except Exception:
            resumen["guarda"] = None

        # 5 Aisladores
        try:
            r_aisl = aisladores.calcular(
                tension_linea_kv=float(proy["tension_nominal_kv"]),
                aislador=aisl,
                nivel_contaminacion="alta",
                n_subconductores=3,
                masa_conductor_kg_m=cond["masa_kg_m"],
                vano_gravitacional_m=float(proy["vano_diseno_m"]) * 1.1,
                tension_horizontal_conductor_n=resumen["mecanico"].hipotesis[0].tension_n if resumen["mecanico"] else 30000,
            )
            resumen["aisladores"] = r_aisl
        except Exception:
            resumen["aisladores"] = None

        # 6 Torre
        try:
            r_torre = torre.calcular(
                tension_linea_kv=float(proy["tension_nominal_kv"]),
                altitud_msnm=float(proy["altitud_msnm"]),
                flecha_max_m=resumen["mecanico"].flecha_maxima_m if resumen["mecanico"] else 12.0,
                longitud_cadena_m=resumen["aisladores"].longitud_cadena_m if resumen["aisladores"] else 6.0,
                longitud_linea_km=float(proy["longitud_km"]),
                vano_diseno_m=float(proy["vano_diseno_m"]),
                n_subconductores=int(proy.get("haz_subconductores", 3)),
                haz_separacion_m=float(proy.get("haz_separacion_m", 0.40)),
                n_discos_aislador=resumen["aisladores"].n_discos_adoptado if resumen["aisladores"] else 41,
                cadena_doble=resumen["aisladores"].cadena_doble_requerida if resumen["aisladores"] else True,
            )
            resumen["torre"] = r_torre
        except Exception:
            resumen["torre"] = None

        # 7 Plantillado
        try:
            hip_d = next((h for h in resumen["mecanico"].hipotesis if h.nombre == "D"), None) if resumen["mecanico"] else None
            hip_b = next((h for h in resumen["mecanico"].hipotesis if h.nombre == "B"), None) if resumen["mecanico"] else None
            if hip_d and hip_b:
                r_plant = plantillado.calcular(
                    vano_m=float(proy["vano_diseno_m"]),
                    tension_caliente_n=hip_d.tension_n,
                    tension_frio_n=hip_b.tension_n,
                    masa_kg_m=cond["masa_kg_m"],
                )
                resumen["plantillado"] = r_plant
            else:
                resumen["plantillado"] = None
        except Exception:
            resumen["plantillado"] = None

        return render_template("_partial_modulo_11_resumen.html", **resumen)

    @app.errorhandler(404)
    def not_found(_e):
        return render_template(
            "404.html",
            modulo_id=0, modulo_info=None,
            anterior=None, siguiente=None, progreso_pct=0,
        ), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
