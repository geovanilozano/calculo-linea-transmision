"""Configuración Flask para entornos dev y prod."""
import os
from pathlib import Path


class BaseConfig:
    """Configuración base compartida."""

    BASE_DIR = Path(__file__).resolve().parent
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    # Parámetros por defecto del proyecto de línea de transmisión.
    # NOTA: la tensión nominal (kV) se CALCULA en el módulo 1 a partir de P, L.
    # No es un parámetro de entrada — es un RESULTADO del análisis.
    PROYECTO_DEFAULTS = {
        # Identificación
        "nombre": "Cálculo de Línea de Transmisión",
        "corredor": "Santander de Quilichao – Manizales",

        # ===== PARÁMETROS ELÉCTRICOS DE ENTRADA =====
        "longitud_km": 300,
        "factor_potencia": 1.0,
        "potencia_mw": 300,
        "altitud_msnm": 1000,
        "temperatura_max_conductor_c": 75,
        "velocidad_viento_max_kmh": 140,
        "temperatura_min_ambiente_c": 5,
        "regulacion_max_pct": 19.0,
        "perdidas_max_pct": 4.7,
        "frecuencia_hz": 60,

        # Tensión nominal: se calcula en módulo 1 pero se guarda como referencia
        # para los demás módulos. Default 500 kV (caso típico Colombia).
        "tension_nominal_kv": 500,

        # ===== PARÁMETROS MECÁNICOS — 4 HIPÓTESIS CLIMÁTICAS =====
        # Hipótesis A: máxima velocidad del viento
        "hip_a_viento_kmh": 140,
        "hip_a_temperatura_c": 15,
        "hip_a_delta_temp_c": 5,
        "hip_a_fs": 2.5,
        # Hipótesis B: mínima temperatura
        "hip_b_viento_kmh": 35,
        "hip_b_temperatura_c": 5,
        "hip_b_delta_temp_c": 5,
        "hip_b_fs": 2.5,
        # Hipótesis C: operación diaria (EDS)
        "hip_c_viento_kmh": 20,
        "hip_c_temperatura_c": 27,
        "hip_c_delta_temp_c": 10,
        "hip_c_fs": 5.0,
        # Hipótesis D: máxima temperatura
        "hip_d_viento_kmh": 0,
        "hip_d_temperatura_c": 65,
        "hip_d_delta_temp_c": 5,
        "hip_d_fs": 2.5,

        # ===== PARÁMETROS GEOMÉTRICOS / CONSTRUCTIVOS =====
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
