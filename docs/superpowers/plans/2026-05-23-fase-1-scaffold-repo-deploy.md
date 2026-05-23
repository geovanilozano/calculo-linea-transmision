# Fase 1 — Scaffold + Repo + Deploy Inicial · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear el esqueleto funcional de la app educativa de líneas de transmisión: estructura de archivos, Flask con 11 rutas, base.html con layout sidebar + 3 paneles + dark mode, toolchain Tailwind, configs de deploy en Render, repo público en GitHub con MIT license, y primera versión desplegada en producción.

**Architecture:** Flask 3 + Jinja2 (server-rendered) + HTMX 2 + Alpine.js 3 + Tailwind CSS v3 (build con CLI standalone). Sin SPA, sin build de JS. Toda la interactividad cliente vía HTMX (server-driven) + Alpine.js (reactividad puntual: theme toggle, dropdowns). Deploy single-service en Render con gunicorn.

**Tech Stack:**
- Python 3.11 + Flask 3.0.3 + gunicorn 23.0.0
- HTMX 2.0 + Alpine.js 3.14 (via CDN)
- Tailwind CSS 3.4 (standalone CLI, build local) + @tailwindcss/forms + @tailwindcss/typography
- Lucide Icons (via CDN)
- KaTeX 0.16 (via CDN, para fases futuras)
- Inter Variable + Geist Mono (via Google Fonts)
- Render para deploy, GitHub público para repo

**Project root:** `C:/Users/geova/Desktop/Calculo Linea de Transmision/`

**Convención de commits importante:**
- Mensajes en imperativo en español o inglés (consistente)
- **NUNCA agregar `Co-Authored-By: Claude`** ni mención de IA
- Atómicos: un commit = un cambio coherente

---

## File Structure (qué se crea en esta fase)

```
calculo-linea-transmision/
├── .gitignore                           # CREATE (Task 10)
├── LICENSE                              # CREATE (Task 10) - MIT, Geovani Lozano 2026
├── README.md                            # CREATE (Task 10) - profesional con badges
├── Procfile                             # CREATE (Task 9) - gunicorn config
├── render.yaml                          # CREATE (Task 9) - Render IaC
├── requirements.txt                     # CREATE (Task 2) - Python deps pineadas
├── package.json                         # CREATE (Task 3) - solo para Tailwind build
├── tailwind.config.js                   # CREATE (Task 3) - tokens custom OKLCH
├── postcss.config.js                    # CREATE (Task 3)
├── config.py                            # CREATE (Task 4) - Flask config dev/prod
├── app.py                               # CREATE (Task 5) - Flask app + 11 rutas
├── calculos/
│   └── __init__.py                      # CREATE (Task 1) - placeholder
├── figuras/
│   └── __init__.py                      # CREATE (Task 1) - placeholder
├── static/
│   ├── css/
│   │   └── input.css                    # CREATE (Task 3) - Tailwind directives
│   ├── js/
│   │   └── app.js                       # CREATE (Task 6) - inicialización Alpine
│   └── data/
│       └── .gitkeep                     # CREATE (Task 1)
├── templates/
│   ├── base.html                        # CREATE (Task 6) - layout principal
│   ├── modulo_0_inicio.html             # CREATE (Task 7)
│   ├── modulo_1_tension.html            # CREATE (Task 7)
│   ├── modulo_2_configuracion.html      # CREATE (Task 7)
│   ├── modulo_3_conductor.html          # CREATE (Task 7)
│   ├── modulo_4_parametros.html         # CREATE (Task 7)
│   ├── modulo_5_linea_larga.html        # CREATE (Task 7)
│   ├── modulo_6_mecanico.html           # CREATE (Task 7)
│   ├── modulo_7_guarda.html             # CREATE (Task 7)
│   ├── modulo_8_aisladores.html         # CREATE (Task 7)
│   ├── modulo_9_torre.html              # CREATE (Task 7)
│   └── modulo_10_plantillado.html       # CREATE (Task 7)
├── tests/
│   ├── __init__.py                      # CREATE (Task 5)
│   └── test_routes.py                   # CREATE (Task 5) - smoke tests rutas
└── docs/
    ├── superpowers/
    │   ├── specs/                       # ALREADY EXISTS
    │   └── plans/                       # ALREADY EXISTS
    └── manual_capacitador.md            # CREATE (Task 10) - draft inicial
```

**Archivos generados automáticamente (en .gitignore):**
- `static/css/styles.css` (output de Tailwind build)
- `node_modules/`
- `.venv/`
- `__pycache__/`

---

## Task 1: Crear estructura de carpetas y __init__.py

**Files:**
- Create: `calculos/__init__.py`
- Create: `figuras/__init__.py`
- Create: `static/css/.gitkeep`, `static/js/.gitkeep`, `static/data/.gitkeep`
- Create: `templates/.gitkeep`
- Create: `tests/__init__.py`

- [ ] **Step 1: Crear todas las carpetas vacías**

```bash
cd "C:/Users/geova/Desktop/Calculo Linea de Transmision"
mkdir -p calculos figuras static/css static/js static/data templates tests
```

- [ ] **Step 2: Crear archivos __init__.py vacíos**

Create `calculos/__init__.py`:
```python
"""Módulos de cálculo del proyecto de línea de transmisión 500 kV."""
```

Create `figuras/__init__.py`:
```python
"""Generadores de figuras técnicas con matplotlib."""
```

Create `tests/__init__.py` (vacío):
```python
```

- [ ] **Step 3: Crear archivos .gitkeep en carpetas vacías**

```bash
touch static/css/.gitkeep
touch static/js/.gitkeep
touch static/data/.gitkeep
touch templates/.gitkeep
```

- [ ] **Step 4: Verificar estructura**

```bash
find . -type d -not -path '*/\.*' -not -path '*/node_modules*' -not -path '*/.venv*' | sort
```

Expected output (en orden):
```
.
./calculos
./docs
./docs/superpowers
./docs/superpowers/plans
./docs/superpowers/specs
./figuras
./static
./static/css
./static/data
./static/js
./templates
./tests
```

---

## Task 2: Setup Python environment y requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Crear requirements.txt**

```txt
# Production dependencies
Flask==3.0.3
matplotlib==3.9.2
numpy==1.26.4
gunicorn==23.0.0
python-dotenv==1.0.1

# Development dependencies
pytest==8.3.3
pytest-flask==1.3.0
black==24.10.0
```

- [ ] **Step 2: Crear virtual environment**

```bash
cd "C:/Users/geova/Desktop/Calculo Linea de Transmision"
python -m venv .venv
```

- [ ] **Step 3: Activar venv e instalar dependencias**

PowerShell (Windows):
```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Expected: "Successfully installed Flask-3.0.3 ... gunicorn-23.0.0 ..."

- [ ] **Step 4: Verificar Flask instalado**

```bash
.venv/Scripts/python -c "import flask; print(flask.__version__)"
```

Expected output: `3.0.3`

---

## Task 3: Setup toolchain de Tailwind CSS

**Files:**
- Create: `package.json`
- Create: `tailwind.config.js`
- Create: `postcss.config.js`
- Create: `static/css/input.css`

- [ ] **Step 1: Crear package.json**

```json
{
  "name": "calculo-linea-transmision",
  "version": "1.0.0",
  "description": "App educativa interactiva: diseño de línea de transmisión 500 kV",
  "scripts": {
    "build:css": "tailwindcss -i ./static/css/input.css -o ./static/css/styles.css --minify",
    "watch:css": "tailwindcss -i ./static/css/input.css -o ./static/css/styles.css --watch"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.13",
    "@tailwindcss/forms": "^0.5.9",
    "@tailwindcss/typography": "^0.5.15",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.47"
  }
}
```

- [ ] **Step 2: Crear tailwind.config.js con tokens semánticos**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter Variable"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        // Mapean a CSS variables definidas en input.css
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        card: 'var(--card)',
        'card-foreground': 'var(--card-foreground)',
        muted: 'var(--muted)',
        'muted-foreground': 'var(--muted-foreground)',
        border: 'var(--border)',
        input: 'var(--input)',
        primary: 'var(--primary)',
        'primary-foreground': 'var(--primary-foreground)',
        accent: 'var(--accent)',
        'accent-foreground': 'var(--accent-foreground)',
        success: 'var(--success)',
        warning: 'var(--warning)',
        danger: 'var(--danger)',
      },
      borderRadius: {
        'lg': '0.5rem',
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

- [ ] **Step 3: Crear postcss.config.js**

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 4: Crear static/css/input.css con tokens OKLCH**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Light theme - tokens OKLCH */
    --background: oklch(99% 0 0);
    --foreground: oklch(15% 0.005 250);
    --card: oklch(100% 0 0);
    --card-foreground: oklch(15% 0.005 250);
    --muted: oklch(96% 0.005 250);
    --muted-foreground: oklch(45% 0.01 250);
    --border: oklch(91% 0.005 250);
    --input: oklch(91% 0.005 250);
    --primary: oklch(55% 0.18 250);
    --primary-foreground: oklch(99% 0 0);
    --accent: oklch(65% 0.15 50);
    --accent-foreground: oklch(99% 0 0);
    --success: oklch(65% 0.15 145);
    --warning: oklch(75% 0.15 80);
    --danger: oklch(60% 0.20 25);
  }

  .dark {
    --background: oklch(12% 0.01 250);
    --foreground: oklch(96% 0.005 250);
    --card: oklch(16% 0.01 250);
    --card-foreground: oklch(96% 0.005 250);
    --muted: oklch(20% 0.01 250);
    --muted-foreground: oklch(65% 0.01 250);
    --border: oklch(25% 0.01 250);
    --input: oklch(25% 0.01 250);
    --primary: oklch(70% 0.18 250);
    --primary-foreground: oklch(15% 0.005 250);
    --accent: oklch(72% 0.15 50);
    --accent-foreground: oklch(15% 0.005 250);
    --success: oklch(70% 0.15 145);
    --warning: oklch(78% 0.15 80);
    --danger: oklch(65% 0.20 25);
  }

  * {
    @apply border-border;
  }

  html {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body {
    @apply bg-background text-foreground font-sans antialiased;
    font-feature-settings: "rlig" 1, "calt" 1;
  }

  /* Smooth theme transitions */
  body, .card, button, input, select, textarea {
    transition: background-color 200ms ease, border-color 200ms ease, color 200ms ease;
  }

  /* Focus visible mejorado */
  :focus-visible {
    @apply outline-none ring-2 ring-primary ring-offset-2 ring-offset-background;
  }

  /* Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
}

@layer components {
  .card {
    @apply bg-card text-card-foreground border border-border rounded-xl shadow-sm;
  }

  .btn-primary {
    @apply inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg
           bg-primary text-primary-foreground font-medium
           hover:opacity-90 active:scale-95 transition-all
           disabled:opacity-50 disabled:pointer-events-none;
  }

  .btn-secondary {
    @apply inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg
           bg-muted text-foreground font-medium border border-border
           hover:bg-border active:scale-95 transition-all
           disabled:opacity-50 disabled:pointer-events-none;
  }

  .btn-ghost {
    @apply inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg
           text-foreground font-medium
           hover:bg-muted active:scale-95 transition-all;
  }

  .input {
    @apply w-full px-3 py-2 rounded-lg bg-card border border-input
           text-foreground placeholder:text-muted-foreground
           focus:border-primary focus:ring-1 focus:ring-primary
           disabled:opacity-50 disabled:cursor-not-allowed
           transition-colors;
  }

  .badge {
    @apply inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium;
  }

  .badge-success {
    @apply badge bg-success/15 text-success;
  }

  .badge-warning {
    @apply badge bg-warning/15 text-warning;
  }

  .badge-danger {
    @apply badge bg-danger/15 text-danger;
  }

  .sidebar-link {
    @apply flex items-center gap-3 px-3 py-2 rounded-lg text-sm
           text-muted-foreground font-medium
           hover:bg-muted hover:text-foreground
           transition-colors;
  }

  .sidebar-link-active {
    @apply sidebar-link bg-primary/10 text-primary
           hover:bg-primary/15 hover:text-primary;
  }
}
```

- [ ] **Step 5: Instalar dependencias Node**

```bash
cd "C:/Users/geova/Desktop/Calculo Linea de Transmision"
npm install
```

Expected: "added X packages" sin errores.

- [ ] **Step 6: Compilar CSS por primera vez**

```bash
npm run build:css
```

Expected: archivo `static/css/styles.css` creado, ~30-50 KB minified.

- [ ] **Step 7: Verificar build**

```bash
ls -la static/css/styles.css
```

Expected: archivo existe y tiene tamaño > 10 KB.

---

## Task 4: Crear config.py con configuración dev/prod

**Files:**
- Create: `config.py`

- [ ] **Step 1: Crear config.py**

```python
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
```

- [ ] **Step 2: Verificar import**

```bash
.venv/Scripts/python -c "from config import get_config; print(get_config().__name__)"
```

Expected output: `DevelopmentConfig`

---

## Task 5: Crear Flask app con 11 rutas + tests smoke

**Files:**
- Create: `app.py`
- Create: `tests/test_routes.py`

- [ ] **Step 1: Crear tests/test_routes.py PRIMERO (TDD)**

```python
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
```

- [ ] **Step 2: Correr tests para verificar que fallan**

```bash
.venv/Scripts/python -m pytest tests/test_routes.py -v
```

Expected: FAIL con `ImportError: cannot import name 'create_app' from 'app'` o similar.

- [ ] **Step 3: Crear app.py con factory + 11 rutas**

```python
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
        return render_template("404.html"), 404

    return app


# WSGI entrypoint para gunicorn
app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
```

- [ ] **Step 4: Correr tests de nuevo — ahora deberían fallar porque faltan templates**

```bash
.venv/Scripts/python -m pytest tests/test_routes.py -v
```

Expected: la mayoría FAIL con `jinja2.exceptions.TemplateNotFound: modulo_0_inicio.html`. Eso es esperado — los templates se crean en Task 7.

- [ ] **Step 5: Commit parcial (NO incluye Co-Authored-By)**

```bash
git add app.py config.py tests/ calculos/__init__.py figuras/__init__.py
git commit -m "feat: scaffold Flask app con factory pattern y 11 rutas"
```

Note: si git aún no está inicializado, este commit se hará en Task 11 después de `git init`. Marca este step como completado cuando hayas guardado los archivos.

---

## Task 6: Crear base.html con sidebar + 3 paneles + dark mode + HTMX + Alpine

**Files:**
- Create: `templates/base.html`
- Create: `templates/404.html`
- Create: `static/js/app.js`

- [ ] **Step 1: Crear static/js/app.js**

```javascript
/**
 * Inicialización Alpine.js + helpers globales para la app educativa.
 */

// Store global de Alpine para el theme
document.addEventListener('alpine:init', () => {
  Alpine.store('theme', {
    init() {
      // Detectar preferencia: localStorage > system preference > light
      const saved = localStorage.getItem('theme');
      if (saved) {
        this.current = saved;
      } else {
        this.current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      this.apply();

      // Escuchar cambios del sistema
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
          this.current = e.matches ? 'dark' : 'light';
          this.apply();
        }
      });
    },
    current: 'light',
    toggle() {
      this.current = this.current === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', this.current);
      this.apply();
    },
    apply() {
      if (this.current === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
  });
});

// Helper: View Transitions API para cambio entre módulos (con fallback)
document.addEventListener('htmx:beforeSwap', (e) => {
  if (document.startViewTransition && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    e.preventDefault();
    document.startViewTransition(() => {
      e.detail.target.innerHTML = e.detail.serverResponse;
    });
  }
});
```

- [ ] **Step 2: Crear templates/base.html**

```html
<!DOCTYPE html>
<html lang="es" x-data x-init="$store.theme.init()" :class="$store.theme.current === 'dark' ? 'dark' : ''">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Tour interactivo del diseño de una línea aérea de transmisión 500 kV / 307 km / 300 MW">
  <title>{% block title %}{{ modulo_info[2] if modulo_info else 'Línea de Transmisión 500 kV' }} · Tour Educativo{% endblock %}</title>

  {# Fonts: Inter Variable + Geist Mono #}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@100..900&display=swap" rel="stylesheet">

  {# Tailwind CSS compilado #}
  <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">

  {# HTMX 2 #}
  <script src="https://unpkg.com/htmx.org@2.0.3" integrity="sha384-0895/pl2MU10Hqc6jd4RvrthNlDiE9U1tWmX7WRESftEDRosgxNsQG/Ze9YMRzHq" crossorigin="anonymous"></script>

  {# Alpine.js 3 (defer para evitar FOUC) #}
  <script src="{{ url_for('static', filename='js/app.js') }}" defer></script>
  <script src="https://unpkg.com/alpinejs@3.14.3/dist/cdn.min.js" defer></script>

  {# Lucide icons #}
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>

  {# Theme flicker prevention #}
  <script>
    (function() {
      const saved = localStorage.getItem('theme');
      const isDark = saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (isDark) document.documentElement.classList.add('dark');
    })();
  </script>

  {% block extra_head %}{% endblock %}
</head>
<body class="min-h-screen bg-background text-foreground">

  {# Layout principal: sidebar + content #}
  <div class="flex min-h-screen">

    {# ===== SIDEBAR ===== #}
    <aside class="w-72 shrink-0 border-r border-border bg-card flex flex-col">

      {# Logo / título #}
      <div class="px-6 py-5 border-b border-border">
        <a href="{{ url_for('modulo', modulo_id=0) }}" class="flex items-center gap-3 group">
          <div class="size-10 rounded-lg bg-primary/10 grid place-items-center group-hover:bg-primary/15 transition-colors">
            <i data-lucide="zap" class="size-5 text-primary"></i>
          </div>
          <div>
            <div class="font-semibold text-foreground text-sm">Línea 500 kV</div>
            <div class="text-xs text-muted-foreground">Tour Educativo</div>
          </div>
        </a>
      </div>

      {# Navegación de módulos #}
      <nav class="flex-1 px-3 py-4 overflow-y-auto">
        <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-3 mb-2">
          Módulos
        </div>
        {% for mod_id, mod_slug, mod_nombre, mod_desc in MODULOS %}
          <a href="{{ url_for('modulo', modulo_id=mod_id) }}"
             class="{% if mod_id == modulo_id %}sidebar-link-active{% else %}sidebar-link{% endif %}">
            <span class="size-6 rounded-md bg-muted text-muted-foreground text-xs font-mono grid place-items-center {% if mod_id == modulo_id %}bg-primary/20 text-primary{% endif %}">
              {{ mod_id }}
            </span>
            <span class="flex-1 truncate">{{ mod_nombre }}</span>
            {% if mod_id == modulo_id %}
              <i data-lucide="chevron-right" class="size-4 text-primary"></i>
            {% endif %}
          </a>
        {% endfor %}
      </nav>

      {# Progress bar #}
      <div class="px-6 py-4 border-t border-border">
        <div class="flex items-center justify-between text-xs text-muted-foreground mb-2">
          <span>Progreso del tour</span>
          <span class="font-mono">{{ modulo_id + 1 }}/{{ MODULOS|length }}</span>
        </div>
        <div class="h-2 bg-muted rounded-full overflow-hidden">
          <div class="h-full bg-primary rounded-full transition-all duration-500"
               style="width: {{ progreso_pct }}%"></div>
        </div>
      </div>

      {# Footer con theme toggle #}
      <div class="px-3 py-3 border-t border-border flex items-center justify-between">
        <span class="text-xs text-muted-foreground px-3">
          v1.0 · MIT
        </span>
        <button @click="$store.theme.toggle()"
                class="btn-ghost size-9 !p-0"
                :aria-label="$store.theme.current === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'">
          <i data-lucide="sun" class="size-4" x-show="$store.theme.current === 'dark'"></i>
          <i data-lucide="moon" class="size-4" x-show="$store.theme.current === 'light'"></i>
        </button>
      </div>
    </aside>

    {# ===== CONTENT ===== #}
    <main class="flex-1 flex flex-col min-w-0">

      {# Header del módulo #}
      <header class="px-8 py-6 border-b border-border bg-card/50 backdrop-blur-sm">
        <div class="flex items-start justify-between gap-6">
          <div>
            <div class="flex items-center gap-2 text-sm text-muted-foreground mb-1">
              <span>Módulo {{ modulo_id }}</span>
              <span>·</span>
              <span>{{ modulo_info[3] if modulo_info }}</span>
            </div>
            <h1 class="text-3xl font-bold tracking-tight text-foreground">
              {% block module_title %}{{ modulo_info[2] if modulo_info }}{% endblock %}
            </h1>
          </div>
        </div>
      </header>

      {# Contenido del módulo: 3 paneles #}
      <div class="flex-1 overflow-y-auto px-8 py-6">
        {% block module_content %}
          <div class="grid grid-cols-1 lg:grid-cols-[1fr_1.2fr_1fr] gap-6">
            {# Panel 1: Parámetros #}
            <div class="card p-6 animate-fade-in">
              <h2 class="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                Parámetros
              </h2>
              {% block panel_parametros %}
                <p class="text-muted-foreground text-sm">Parámetros editables aparecerán aquí.</p>
              {% endblock %}
            </div>

            {# Panel 2: Visualización #}
            <div class="card p-6 animate-fade-in">
              <h2 class="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                Visualización
              </h2>
              {% block panel_visualizacion %}
                <div class="aspect-video bg-muted rounded-lg grid place-items-center text-muted-foreground">
                  <i data-lucide="image" class="size-12 opacity-30"></i>
                </div>
              {% endblock %}
            </div>

            {# Panel 3: Explicación didáctica #}
            <div class="card p-6 animate-fade-in">
              <h2 class="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">
                Explicación
              </h2>
              {% block panel_explicacion %}
                <p class="text-muted-foreground text-sm">Explicación didáctica aparecerá aquí.</p>
              {% endblock %}
            </div>
          </div>
        {% endblock %}
      </div>

      {# Footer navegación #}
      <footer class="px-8 py-4 border-t border-border bg-card/50 backdrop-blur-sm">
        <div class="flex items-center justify-between gap-4">
          {% if anterior is not none %}
            <a href="{{ url_for('modulo', modulo_id=anterior) }}" class="btn-secondary">
              <i data-lucide="arrow-left" class="size-4"></i>
              <span>Anterior</span>
            </a>
          {% else %}
            <span></span>
          {% endif %}

          {% if siguiente is not none %}
            <a href="{{ url_for('modulo', modulo_id=siguiente) }}" class="btn-primary">
              <span>Siguiente</span>
              <i data-lucide="arrow-right" class="size-4"></i>
            </a>
          {% else %}
            <a href="{{ url_for('modulo', modulo_id=0) }}" class="btn-secondary">
              <i data-lucide="rotate-ccw" class="size-4"></i>
              <span>Reiniciar tour</span>
            </a>
          {% endif %}
        </div>
      </footer>
    </main>
  </div>

  {# Inicializar iconos Lucide después de que cargue todo #}
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      if (window.lucide) lucide.createIcons();
    });
    document.addEventListener('htmx:afterSwap', () => {
      if (window.lucide) lucide.createIcons();
    });
  </script>

  {% block extra_scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 3: Crear templates/404.html**

```html
{% extends "base.html" %}

{% block title %}404 - No encontrado{% endblock %}

{% block module_content %}
<div class="min-h-[60vh] grid place-items-center">
  <div class="text-center max-w-md">
    <div class="text-7xl font-bold text-primary mb-4">404</div>
    <h2 class="text-2xl font-semibold mb-2">Módulo no encontrado</h2>
    <p class="text-muted-foreground mb-6">
      El módulo solicitado no existe. Vuelve al inicio del tour para continuar.
    </p>
    <a href="{{ url_for('modulo', modulo_id=0) }}" class="btn-primary">
      <i data-lucide="home" class="size-4"></i>
      Ir al inicio
    </a>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Verificar que el HTML compila sin errores Jinja**

```bash
.venv/Scripts/python -c "
from app import create_app
app = create_app()
with app.test_request_context():
    from flask import render_template
    try:
        html = render_template('404.html', modulo_id=99, modulo_info=None, anterior=None, siguiente=None, progreso_pct=0)
        print('Template renderiza OK, longitud:', len(html))
    except Exception as e:
        print('ERROR:', e)
"
```

Expected: `Template renderiza OK, longitud: <número grande>`

---

## Task 7: Crear los 11 templates de módulos (skeletons)

**Files:**
- Create: `templates/modulo_0_inicio.html` through `templates/modulo_10_plantillado.html`

- [ ] **Step 1: Crear template helper común para skeleton de módulo**

Cada uno de los 11 templates sigue el mismo patrón. Crearemos cada archivo individualmente con su contenido específico.

- [ ] **Step 2: Crear modulo_0_inicio.html**

```html
{% extends "base.html" %}

{% block panel_parametros %}
<div class="space-y-4">
  <div>
    <label class="block text-sm font-medium mb-1">Proyecto</label>
    <div class="text-foreground font-semibold">{{ PROYECTO.nombre }}</div>
  </div>
  <div>
    <label class="block text-sm font-medium mb-1">Corredor</label>
    <div class="text-sm text-muted-foreground">{{ PROYECTO.corredor }}</div>
  </div>
  <div class="grid grid-cols-2 gap-3 pt-2">
    <div class="bg-muted rounded-lg p-3">
      <div class="text-xs text-muted-foreground">Tensión</div>
      <div class="font-mono font-semibold">{{ PROYECTO.tension_nominal_kv }} kV</div>
    </div>
    <div class="bg-muted rounded-lg p-3">
      <div class="text-xs text-muted-foreground">Longitud</div>
      <div class="font-mono font-semibold">{{ PROYECTO.longitud_km }} km</div>
    </div>
    <div class="bg-muted rounded-lg p-3">
      <div class="text-xs text-muted-foreground">Potencia</div>
      <div class="font-mono font-semibold">{{ PROYECTO.potencia_mw }} MW</div>
    </div>
    <div class="bg-muted rounded-lg p-3">
      <div class="text-xs text-muted-foreground">Altitud</div>
      <div class="font-mono font-semibold">{{ PROYECTO.altitud_msnm }} m</div>
    </div>
  </div>
</div>
{% endblock %}

{% block panel_visualizacion %}
<div class="space-y-4">
  <div class="aspect-video bg-gradient-to-br from-primary/5 to-accent/5 rounded-lg grid place-items-center">
    <div class="text-center p-6">
      <i data-lucide="map" class="size-12 text-primary mx-auto mb-3"></i>
      <p class="font-semibold">Corredor de diseño</p>
      <p class="text-sm text-muted-foreground">{{ PROYECTO.corredor }}</p>
    </div>
  </div>
</div>
{% endblock %}

{% block panel_explicacion %}
<div class="prose prose-sm max-w-none dark:prose-invert">
  <h3>Bienvenido al tour</h3>
  <p>
    Este es un recorrido educativo paso a paso del diseño de una línea aérea de transmisión a 500 kV. Vas a recorrer los 11 módulos en orden, viendo en cada uno:
  </p>
  <ul>
    <li>Qué se calcula y para qué sirve</li>
    <li>La fórmula matemática</li>
    <li>Una visualización técnica</li>
    <li>Los resultados con validación automática</li>
  </ul>
  <p class="text-sm text-muted-foreground">
    Usa el botón "Siguiente" abajo o la barra lateral para navegar.
  </p>
</div>
{% endblock %}
```

- [ ] **Step 3: Crear modulo_1_tension.html (skeleton)**

```html
{% extends "base.html" %}

{% block panel_parametros %}
<div class="space-y-4">
  <div>
    <label class="block text-sm font-medium mb-1">Potencia (MW)</label>
    <input type="number" class="input" value="{{ PROYECTO.potencia_mw }}" readonly>
  </div>
  <div>
    <label class="block text-sm font-medium mb-1">Longitud (km)</label>
    <input type="number" class="input" value="{{ PROYECTO.longitud_km }}" readonly>
  </div>
  <button class="btn-primary w-full">
    <i data-lucide="calculator" class="size-4"></i>
    Calcular
  </button>
</div>
{% endblock %}

{% block panel_explicacion %}
<div class="prose prose-sm max-w-none dark:prose-invert">
  <h3>Selección del nivel de tensión</h3>
  <p>
    Tres criterios empíricos ayudan a justificar qué tensión usar para una línea de transmisión: <strong>Hefner</strong>, <strong>Still</strong> y la regla de <strong>1 kV/km</strong>.
  </p>
  <p class="text-sm text-muted-foreground">
    El cálculo detallado se implementará en la Fase 2 del proyecto.
  </p>
</div>
{% endblock %}
```

- [ ] **Step 4: Crear modulo_2_configuracion.html (skeleton)**

```html
{% extends "base.html" %}

{% block panel_parametros %}
<div class="space-y-4">
  <div>
    <label class="block text-sm font-medium mb-1">Distancia D₁₂ (m)</label>
    <input type="number" step="0.1" class="input" value="9.0">
  </div>
  <div>
    <label class="block text-sm font-medium mb-1">Distancia D₂₃ (m)</label>
    <input type="number" step="0.1" class="input" value="9.0">
  </div>
  <div>
    <label class="block text-sm font-medium mb-1">Distancia D₁₃ (m)</label>
    <input type="number" step="0.1" class="input" value="18.0">
  </div>
  <button class="btn-primary w-full">
    <i data-lucide="calculator" class="size-4"></i>
    Calcular GMD
  </button>
</div>
{% endblock %}

{% block panel_explicacion %}
<div class="prose prose-sm max-w-none dark:prose-invert">
  <h3>Configuración geométrica</h3>
  <p>Cálculo de la Distancia Media Geométrica (GMD) y el Radio Medio Geométrico (GMR) del haz triple.</p>
  <p class="text-sm text-muted-foreground">Implementación pendiente en Fase 2.</p>
</div>
{% endblock %}
```

- [ ] **Step 5: Crear los 8 templates restantes con skeleton idéntico estructura**

Para `modulo_3_conductor.html`, `modulo_4_parametros.html`, `modulo_5_linea_larga.html`, `modulo_6_mecanico.html`, `modulo_7_guarda.html`, `modulo_8_aisladores.html`, `modulo_9_torre.html`, `modulo_10_plantillado.html`:

Cada uno debe contener exactamente:

```html
{% extends "base.html" %}

{% block panel_parametros %}
<div class="space-y-4">
  <p class="text-sm text-muted-foreground">
    Los parámetros editables de este módulo se implementarán en la Fase 2.
  </p>
  <button class="btn-primary w-full" disabled>
    <i data-lucide="calculator" class="size-4"></i>
    Calcular (próximamente)
  </button>
</div>
{% endblock %}

{% block panel_explicacion %}
<div class="prose prose-sm max-w-none dark:prose-invert">
  <h3>{{ modulo_info[2] }}</h3>
  <p>{{ modulo_info[3] }}</p>
  <p class="text-sm text-muted-foreground">
    El contenido completo de este módulo se implementará en la Fase 2 (Cálculos) y Fase 3 (Figuras).
  </p>
</div>
{% endblock %}
```

- [ ] **Step 6: Correr tests — ahora todos deberían pasar**

```bash
.venv/Scripts/python -m pytest tests/test_routes.py -v
```

Expected: **13 passed** (1 redirect + 11 módulos + 1 not found + 1 static css).

- [ ] **Step 7: Levantar el servidor y verificar visualmente en el navegador**

```bash
.venv/Scripts/python app.py
```

Abrir http://127.0.0.1:5000 en el navegador.

Verificar:
- ✅ Redirige a /modulo/0
- ✅ Sidebar muestra los 11 módulos
- ✅ El módulo 0 (Inicio) muestra los parámetros del proyecto (500 kV / 307 km / 300 MW)
- ✅ El botón theme toggle (luna/sol) cambia entre dark/light
- ✅ La preferencia de tema se persiste al recargar
- ✅ Navegación con Siguiente/Anterior funciona
- ✅ La barra de progreso avanza por módulo
- ✅ Probar URL inválida `/modulo/99` muestra 404 estilizado
- ✅ Los iconos Lucide se ven en todos lados

Detener con `Ctrl+C`.

---

## Task 8: Crear Procfile y render.yaml para deploy

**Files:**
- Create: `Procfile`
- Create: `render.yaml`

- [ ] **Step 1: Crear Procfile**

```
web: gunicorn app:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
```

- [ ] **Step 2: Crear render.yaml (Infrastructure as Code)**

```yaml
services:
  - type: web
    name: calculo-linea-transmision
    runtime: python
    plan: free
    region: oregon
    branch: main
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
      npm install
      npm run build:css
    startCommand: gunicorn app:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.7
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: NODE_VERSION
        value: 20.18.0
```

- [ ] **Step 3: Verificar configuración localmente con gunicorn**

```bash
.venv/Scripts/python -m gunicorn app:app --bind 127.0.0.1:8000 --workers 1
```

Abrir http://127.0.0.1:8000 — debe funcionar igual que con `python app.py`.

Detener con `Ctrl+C`.

---

## Task 9: Crear .gitignore + LICENSE + README profesional + manual capacitador inicial

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `README.md`
- Create: `docs/manual_capacitador.md`

- [ ] **Step 1: Crear .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# Flask
instance/
.flaskenv
.env

# Matplotlib cache
.matplotlib/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Tailwind output (se compila en build)
static/css/styles.css

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Render
.render/

# Local artifacts
*.log
*.tmp
```

- [ ] **Step 2: Crear LICENSE (MIT, Geovani Lozano 2026)**

```
MIT License

Copyright (c) 2026 Geovani Lozano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Crear README.md profesional**

```markdown
# ⚡ Cálculo Línea de Transmisión 500 kV

[![Deploy](https://img.shields.io/badge/deploy-render-46E3B7?logo=render&logoColor=white)](https://calculo-linea-transmision.onrender.com)
[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask 3](https://img.shields.io/badge/flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Tailwind CSS](https://img.shields.io/badge/tailwind-3.4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> Tour interactivo paso a paso del diseño de una línea aérea de transmisión a **500 kV / 307 km / 300 MW**, basado en normativa colombiana (RETIE, NTC 2050, CREG).

## 🌐 Demo en vivo

**[calculo-linea-transmision.onrender.com](https://calculo-linea-transmision.onrender.com)**

> ⚠️ El servidor está en plan gratuito de Render: el primer acceso tras inactividad puede tardar ~30 segundos en arrancar.

## ✨ Características

- 🎯 **11 módulos didácticos** navegables que reproducen el flujo completo del informe del estudiante
- ⚡ **Recálculo en vivo** al modificar parámetros (HTMX, sin recargar página)
- 📊 **Visualizaciones técnicas** con Matplotlib + Chart.js
- 🧮 **Fórmulas matemáticas** renderizadas con KaTeX
- ✅ **Validaciones automáticas** contra normativa colombiana
- 🌙 **Dark mode nativo** con detección de preferencia del sistema
- 🎨 **Diseño moderno** con sistema de tokens OKLCH (Tailwind v3)
- ♿ **Accesible** (WCAG AA, navegación por teclado, prefers-reduced-motion)

## 🏗 Estructura del proyecto

El proyecto reproduce el diseño completo de una línea de transmisión:

| Módulo | Contenido |
|--------|-----------|
| **0** | Inicio - parámetros generales del proyecto |
| **1** | Selección de tensión (Hefner / Still / 1 kV/km) |
| **2** | Configuración geométrica (GMD, GMR) |
| **3** | Conductor seleccionado (ACSR Drake) |
| **4** | Parámetros R, L, C + efecto Corona |
| **5** | Línea larga (parámetros ABCD, regulación, pérdidas) |
| **6** | Mecánica del conductor (4 hipótesis) |
| **7** | Mecánica del cable de guarda |
| **8** | Selección de aisladores |
| **9** | Diseño de torre |
| **10** | Plantillado (4 curvas patrón) |

## 🚀 Uso local

### Requisitos previos

- Python 3.11+
- Node.js 20+ (solo para build de Tailwind)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/geovanilozano/calculo-linea-transmision.git
cd calculo-linea-transmision

# Crear entorno virtual Python
python -m venv .venv

# Activar entorno (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# Activar entorno (macOS/Linux)
source .venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias Node y compilar CSS
npm install
npm run build:css
```

### Correr la app

```bash
python app.py
```

Abrir http://127.0.0.1:5000 en el navegador.

### Modo desarrollo (con auto-rebuild de CSS)

En una terminal:
```bash
npm run watch:css
```

En otra terminal:
```bash
python app.py
```

## 📚 Para capacitadores

Si vas a usar esta app para dar clase, consulta el [manual del capacitador](docs/manual_capacitador.md).

## 🛠 Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 + Flask 3 |
| Templating | Jinja2 |
| Interactividad | HTMX 2 + Alpine.js 3 |
| Estilos | Tailwind CSS v3 (con tokens OKLCH) |
| Math rendering | KaTeX |
| Gráficas | Matplotlib + Chart.js |
| Fuentes | Inter Variable + Geist Mono |
| Iconos | Lucide |
| Server prod | gunicorn |
| Deploy | Render |

## 📐 Normativa de referencia

- **RETIE** (Reglamento Técnico de Instalaciones Eléctricas - Colombia)
- **NTC 2050** (Código Eléctrico Colombiano)
- **IEC 60071** (Coordinación de aislamiento)
- **IEEE Std 738** (Ampacidad)

## 🤝 Contribuir

Pull requests bienvenidos. Para cambios mayores, abre primero un issue para discutir lo que te gustaría cambiar.

## 📜 Licencia

[MIT](LICENSE) © 2026 Geovani Lozano

## 🙏 Créditos

Basado en el trabajo de tesis "Diseño de una Línea de Transmisión Aérea de Alta Tensión a 500 kV" (Unidades Tecnológicas de Santander, 2026), corredor Santander de Quilichao – Manizales.
```

- [ ] **Step 4: Crear docs/manual_capacitador.md (draft inicial)**

```markdown
# Manual del Capacitador

Esta guía es para instructores que quieran usar la app para enseñar diseño de líneas de transmisión a estudiantes.

## Antes de la clase

1. Ten la app corriendo: localmente (`python app.py`) o usa el [demo en vivo](https://calculo-linea-transmision.onrender.com).
2. Asegúrate de proyectar a 1280×720 mínimo (la app está optimizada para esa resolución hacia arriba).
3. Recomendado: activar **dark mode** para proyección con luces apagadas.

## Estructura de una sesión típica (90 min)

| Tiempo | Actividad |
|--------|-----------|
| 0-5 min | Módulo 0: presentar objetivo y parámetros del proyecto |
| 5-15 min | Módulo 1: ¿por qué 500 kV? Comparar los 3 criterios |
| 15-25 min | Módulo 2: configuración geométrica y haz triple |
| 25-40 min | Módulos 3-5: cálculos eléctricos y línea larga |
| 40-60 min | Módulos 6-7: mecánica conductor y cable de guarda |
| 60-75 min | Módulos 8-9: aisladores y torre |
| 75-85 min | Módulo 10: plantillado |
| 85-90 min | Q&A |

## Notas pedagógicas por módulo

> Este manual se completará en la Fase 5 con notas específicas para cada módulo, preguntas frecuentes de los estudiantes y respuestas sugeridas.
```

---

## Task 10: Inicializar git + primer commit (sin atribución a IA)

**Files:**
- All previous files

- [ ] **Step 1: Verificar git instalado**

```bash
git --version
```

Expected: `git version 2.X.X`

- [ ] **Step 2: Inicializar repo git**

```bash
cd "C:/Users/geova/Desktop/Calculo Linea de Transmision"
git init -b main
```

- [ ] **Step 3: Configurar identidad LOCAL del repo (importante para que los commits salgan como Geovani)**

**IMPORTANTE: usar los valores de Geovani, no de Claude.**

```bash
git config user.name "Geovani Lozano"
git config user.email "TU_EMAIL_DE_GITHUB@example.com"
```

> Reemplaza `TU_EMAIL_DE_GITHUB@example.com` con el email asociado a tu cuenta de GitHub (geovanilozano).

- [ ] **Step 4: Verificar configuración**

```bash
git config user.name
git config user.email
```

Expected: `Geovani Lozano` y tu email.

- [ ] **Step 5: Stage de todos los archivos**

```bash
git add .
```

- [ ] **Step 6: Verificar qué se va a commitear (no deben aparecer .venv ni node_modules)**

```bash
git status
```

Verificar que NO aparecen:
- `.venv/`
- `node_modules/`
- `static/css/styles.css` (se compila en build)
- `__pycache__/`

Si alguno aparece, revisar `.gitignore`.

- [ ] **Step 7: Primer commit (SIN atribución a Claude)**

```bash
git commit -m "feat: scaffold inicial del proyecto

- Flask 3 app con factory pattern y 11 rutas de módulos
- Layout base con sidebar + 3 paneles + dark mode toggle
- Stack moderno: HTMX 2 + Alpine.js 3 + Tailwind CSS v3
- Sistema de tokens OKLCH con dark/light theme
- Templates skeleton para los 11 módulos
- Smoke tests con pytest cubriendo todas las rutas
- Configuración deploy en Render (Procfile + render.yaml)
- README profesional con badges y manual del capacitador inicial
- Licencia MIT"
```

**IMPORTANTE: NO incluir `Co-Authored-By: Claude` ni ninguna mención a IA en el commit.**

- [ ] **Step 8: Verificar el commit**

```bash
git log --oneline -1
git log -1 --format='%an <%ae>'
```

Expected: el commit debe aparecer como autor `Geovani Lozano <tu-email>`.

---

## Task 11: Crear repo en GitHub y conectar

**Files:** none (acción en GitHub web + local git config)

- [ ] **Step 1: Crear repo vacío en GitHub (acción manual del usuario)**

Geovani debe:
1. Ir a https://github.com/new
2. Repository name: `calculo-linea-transmision`
3. Description: `Tour interactivo educativo del diseño de una línea de transmisión 500 kV / 307 km / 300 MW`
4. Visibility: **Public**
5. **NO** marcar "Add a README", "Add .gitignore", ni "Choose a license" (ya están en local)
6. Click "Create repository"

- [ ] **Step 2: Conectar repo local con remoto**

```bash
cd "C:/Users/geova/Desktop/Calculo Linea de Transmision"
git remote add origin https://github.com/geovanilozano/calculo-linea-transmision.git
```

- [ ] **Step 3: Verificar remote**

```bash
git remote -v
```

Expected:
```
origin  https://github.com/geovanilozano/calculo-linea-transmision.git (fetch)
origin  https://github.com/geovanilozano/calculo-linea-transmision.git (push)
```

- [ ] **Step 4: Primer push a main**

```bash
git push -u origin main
```

> Si pide credenciales: usar usuario `geovanilozano` y un **Personal Access Token** de GitHub (no la contraseña). Crear token en https://github.com/settings/tokens (scope: `repo`).

- [ ] **Step 5: Verificar en GitHub**

Abrir https://github.com/geovanilozano/calculo-linea-transmision en el navegador.

Verificar:
- ✅ Todos los archivos están subidos
- ✅ El README se ve renderizado en la página principal
- ✅ Los badges aparecen
- ✅ El commit aparece como autoría de Geovani Lozano

---

## Task 12: Desplegar en Render

**Files:** none (acción en Render dashboard)

- [ ] **Step 1: Conectar Render con el repo (acción manual del usuario)**

Geovani debe:
1. Ir a https://dashboard.render.com/
2. Click "New +" → "Blueprint" (usa render.yaml)
3. Connect repository: `geovanilozano/calculo-linea-transmision`
4. Render detectará `render.yaml` automáticamente
5. Click "Apply"

- [ ] **Step 2: Esperar primer build**

Render comenzará a:
1. Clonar el repo
2. Ejecutar `pip install -r requirements.txt`
3. Ejecutar `npm install && npm run build:css`
4. Arrancar con `gunicorn app:app`

Build esperado: ~2-3 min la primera vez.

- [ ] **Step 3: Verificar deploy exitoso**

Render mostrará la URL pública: `https://calculo-linea-transmision.onrender.com`

Abrir en el navegador y verificar:
- ✅ La app carga (puede tardar 30-60s la primera vez por cold start)
- ✅ Redirige a /modulo/0
- ✅ Los 11 módulos son navegables
- ✅ El dark mode funciona
- ✅ Los iconos Lucide se ven
- ✅ Las fuentes Inter y Geist Mono se cargan

- [ ] **Step 4: Actualizar README.md con badge real de deploy**

Editar `README.md` y asegurar que el badge de deploy apunta a la URL real:

```markdown
[![Deploy](https://img.shields.io/badge/deploy-render-46E3B7?logo=render&logoColor=white)](https://calculo-linea-transmision.onrender.com)
```

- [ ] **Step 5: Commit y push final de Fase 1**

```bash
git add README.md
git commit -m "docs: actualizar URL de deploy en README"
git push
```

Render auto-desplegará el cambio.

---

## Validación final de Fase 1

Al terminar todas las tareas, verificar TODOS estos criterios:

- [ ] La app corre localmente con `python app.py` sin errores
- [ ] La app corre con `gunicorn app:app` sin errores
- [ ] `pytest tests/` pasa 13 tests
- [ ] Los 11 módulos son navegables vía sidebar
- [ ] El theme toggle funciona y persiste en localStorage
- [ ] La barra de progreso refleja correctamente la posición en el tour
- [ ] La página 404 está estilizada
- [ ] El repo público está en https://github.com/geovanilozano/calculo-linea-transmision
- [ ] El primer commit aparece con autoría `Geovani Lozano` (sin Claude)
- [ ] El deploy en Render funciona en https://calculo-linea-transmision.onrender.com
- [ ] Render auto-deploy desde `main` está activo (probar haciendo un commit pequeño)

---

## Self-Review checks

**1. Spec coverage:**
- ✅ Estructura de carpetas (spec §6) → Task 1
- ✅ Stack moderno HTMX+Tailwind (spec §6) → Tasks 3, 6
- ✅ Dark/light mode (spec §8.5) → Tasks 3, 6
- ✅ 11 rutas Flask (spec §6) → Task 5
- ✅ Layout 3 paneles (spec §8.5) → Task 6
- ✅ Despliegue Render (spec §9.5) → Tasks 8, 12
- ✅ Repo público + MIT (spec §9.6) → Tasks 9, 11
- ✅ Commits sin atribución IA (spec §10, memoria) → Task 10
- ✅ Calidad profesional con type hints/docstrings (spec §9.7) → Tasks 4, 5
- ⚠ Tests TDD: cubierto para rutas (Task 5). Tests de cálculo vendrán en Fase 2.

**2. Placeholder scan:** Ninguno detectado. Todo el código está completo y ejecutable.

**3. Type consistency:**
- `create_app()` definido en Task 5, usado en Task 5 (tests) consistentemente.
- `MODULOS` definido como lista de tuplas en Task 5, usado en Task 6 (template) con índices correctos `[0]`-`[3]`.
- `modulo_id`, `modulo_info`, `anterior`, `siguiente`, `progreso_pct` pasados al template en Task 5 y usados consistentemente en Task 6.

---

## Execution Handoff

Plan completo y guardado en `docs/superpowers/plans/2026-05-23-fase-1-scaffold-repo-deploy.md`.

**Dos opciones de ejecución:**

**1. Subagent-Driven (recomendado para este plan)** — dispatcheo un subagent por task, reviso entre tasks, iteración rápida. Permite paralelizar tasks independientes (ej. Task 1 + Task 9 simultáneos).

**2. Inline Execution** — ejecuto las tasks en esta sesión usando executing-plans, con checkpoints para tu revisión.

¿Cuál prefieres?
