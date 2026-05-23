"""Configuración Flask para entornos dev y prod."""
import os
from pathlib import Path


class BaseConfig:
    """Configuración base compartida."""

    BASE_DIR = Path(__file__).resolve().parent
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    # Parámetros por defecto del proyecto de línea de transmisión
    PROYECTO_DEFAULTS = {
        "nombre": "Línea de Transmisión 500 kV",
        "corredor": "Santander de Quilichao – Manizales",
        "tension_nominal_kv": 500,
        "longitud_km": 307,
        "potencia_mw": 300,
        "factor_potencia": 1.0,
        "frecuencia_hz": 60,
        "altitud_msnm": 1000,
        "temperatura_max_conductor_c": 65,
        "temperatura_min_ambiente_c": 5,
        "velocidad_viento_max_kmh": 140,
        "regulacion_max_pct": 19.0,
        "perdidas_max_pct": 4.7,
        "haz_subconductores": 3,
        "haz_separacion_m": 0.40,
        "conductor_tipo": "ACSR Drake 795 kcmil",
        "n_discos_aislador": 41,
        "vano_diseno_m": 400,
    }


class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo local."""

    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    """Configuración para producción (Render)."""

    DEBUG = False
    TESTING = False

    # En producción SECRET_KEY DEBE venir de variable de entorno
    SECRET_KEY = os.environ["SECRET_KEY"] if "SECRET_KEY" in os.environ else BaseConfig.SECRET_KEY


class TestingConfig(BaseConfig):
    """Configuración para tests."""

    DEBUG = False
    TESTING = True


def get_config() -> type[BaseConfig]:
    """Retorna la clase de configuración según FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    mapping = {
        "production": ProductionConfig,
        "development": DevelopmentConfig,
        "testing": TestingConfig,
    }
    return mapping.get(env, DevelopmentConfig)
