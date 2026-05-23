"""Flask app principal: tour educativo de diseño de línea de transmisión 500 kV."""
from flask import Flask, redirect, render_template, url_for
from config import get_config


# Definición de los 11 módulos: (id, slug, nombre, descripción corta)
MODULOS = [
    (0, "inicio", "Inicio", "Objetivo del proyecto y parámetros generales"),
    (1, "tension", "Tensión nominal", "Hefner, Still, 1 kV/km vs escalones normalizados"),
    (2, "configuracion", "Configuración de la línea", "GMD, GMR, geometría de fases"),
    (3, "conductor", "Conductor seleccionado", "ACSR Drake: características y ampacidad"),
    (4, "parametros", "Parámetros R, L, C + Corona", "Cálculo eléctrico y efecto Corona"),
    (5, "linea_larga", "Línea larga (ABCD)", "Modelo distribuido, regulación, pérdidas"),
    (6, "mecanico", "Mecánica del conductor", "4 hipótesis, ecuación de cambio de estado"),
    (7, "guarda", "Mecánica del cable de guarda", "EHS 7/16″, 4 hipótesis, blindaje"),
    (8, "aisladores", "Aisladores", "41 discos, criterio fuga y BIL, fuerzas"),
    (9, "torre", "Torre", "Distancias RETIE 500 kV, ángulo de protección"),
    (10, "plantillado", "Plantillado", "4 curvas patrón sobre perfil topográfico"),
]


def create_app() -> Flask:
    """Factory pattern para crear la app Flask."""
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Inyectar MODULOS en todos los templates
    @app.context_processor
    def inject_globals():
        return {
            "MODULOS": MODULOS,
            "PROYECTO": app.config["PROYECTO_DEFAULTS"],
        }

    # Rutas
    @app.route("/")
    def index():
        """Redirige a módulo 0."""
        return redirect(url_for("modulo", modulo_id=0))

    @app.route("/modulo/<int:modulo_id>")
    def modulo(modulo_id: int):
        """Renderiza el módulo solicitado."""
        if modulo_id < 0 or modulo_id >= len(MODULOS):
            from flask import abort
            abort(404)

        modulo_info = MODULOS[modulo_id]
        template_name = f"modulo_{modulo_id}_{modulo_info[1]}.html"

        # Calcular módulos anterior y siguiente para navegación
        anterior = modulo_id - 1 if modulo_id > 0 else None
        siguiente = modulo_id + 1 if modulo_id < len(MODULOS) - 1 else None

        return render_template(
            template_name,
            modulo_id=modulo_id,
            modulo_info=modulo_info,
            anterior=anterior,
            siguiente=siguiente,
            progreso_pct=int((modulo_id + 1) / len(MODULOS) * 100),
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template(
            "404.html",
            modulo_id=0,
            modulo_info=None,
            anterior=None,
            siguiente=None,
            progreso_pct=0,
        ), 404

    return app


# WSGI entrypoint para gunicorn
app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
