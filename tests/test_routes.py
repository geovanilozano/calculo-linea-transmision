"""Smoke tests: verifica que todas las rutas de los 11 módulos responden 200."""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Fixture que crea una app Flask configurada para testing."""
    import os
    os.environ["FLASK_ENV"] = "testing"
    app = create_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    """Fixture que retorna un test client de Flask."""
    return app.test_client()


def test_root_redirects_to_modulo_0(client):
    """La ruta / debe redirigir al módulo 0 (inicio)."""
    response = client.get("/")
    assert response.status_code in (301, 302)
    assert "/modulo/0" in response.headers.get("Location", "")


@pytest.mark.parametrize("modulo_id", range(11))
def test_modulo_renders(client, modulo_id):
    """Cada módulo (0-10) debe responder con 200 y contener su título."""
    response = client.get(f"/modulo/{modulo_id}")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data


def test_modulo_invalido_404(client):
    """Un módulo fuera de rango debe responder 404."""
    response = client.get("/modulo/99")
    assert response.status_code == 404


def test_static_css_disponible(client):
    """El CSS compilado debe estar accesible."""
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200
    assert b"--background" in response.data  # Token CSS personalizado
