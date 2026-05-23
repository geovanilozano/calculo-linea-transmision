# Spec — App Educativa Interactiva: Diseño de Líneas de Transmisión 500 kV

**Fecha:** 2026-05-23
**Autor:** Geovani (capacitador) + Claude (asistencia)
**Estado:** Borrador para revisión del usuario

---

## 1. Contexto y problema

Geovani es capacitador y tiene en sus manos un trabajo académico ya completo de un estudiante: el diseño de una línea aérea de transmisión a **500 kV / 307 km / 300 MW** (corredor Santander de Quilichao – Manizales, Colombia). Necesita **capacitar a otros estudiantes** explicándoles paso a paso cómo se hizo el proyecto, qué se calcula en cada etapa, qué pasa si se cambia un parámetro, y por qué se toma cada decisión técnica.

Ya tiene una aplicación Flask previa (`Figuras_Calculo_Lineas`) que **genera 8 figuras** del proyecto pero:
- Es un **generador de imágenes**, no una herramienta didáctica.
- Solo cubre ~25% del alcance del proyecto (le faltan los cálculos eléctricos completos, las 4 hipótesis mecánicas, la cadena de aisladores, etc.).
- Usa parámetros de otro proyecto (230 kV / haz 2 / 17 discos), no los del estudiante (500 kV / haz 3 / 41 discos).

## 2. Objetivo

Construir una **aplicación web local interactiva** que sirva como **tour guiado del proyecto**, organizada en 11 módulos secuenciales que reproducen los 7 capítulos del informe del estudiante más 4 módulos de apertura/cierre. Cada módulo debe:

1. Mostrar **qué se calcula** y **para qué sirve** (en lenguaje accesible).
2. Mostrar la **fórmula** matemática (renderizada con MathJax).
3. Permitir **editar parámetros** y ver el efecto en tiempo real.
4. Mostrar una **visualización** (gráfica/diagrama).
5. Mostrar los **resultados** con validación automática (✅/❌).
6. Responder preguntas frecuentes del tipo "¿qué pasa si…?".

## 3. Usuarios y casos de uso

| Usuario | Caso de uso |
|---|---|
| **Geovani (capacitador)** | Proyectar la app en clase y guiar a los estudiantes módulo por módulo |
| **Estudiante en sesión** | Seguir el tour, ver los cambios al modificar parámetros |
| **Estudiante en casa** | Repasar a su ritmo, explorar variaciones |

## 4. Alcance funcional

### Incluido (MVP)

- **Dashboard principal** con sidebar de navegación de 11 módulos.
- **Modo Tour**: avance secuencial guiado (botón "Siguiente").
- **Modo Libre**: navegación a cualquier módulo desde el sidebar.
- **11 módulos** con layout estándar de 3 paneles (parámetros / visualización / explicación).
- **Recalculo en vivo** vía AJAX (sin recargar página).
- **5 figuras reutilizadas** del proyecto existente de Geovani.
- **6 figuras nuevas** creadas con matplotlib.
- **Renderizado matemático** con MathJax (CDN).
- **Validación automática** de resultados (cumple/no cumple normativa).
- **Datos por defecto**: parámetros reales del proyecto del estudiante (500 kV / 307 km / haz 3 / 41 discos).

### Excluido (fuera del MVP)

- Autenticación/multiusuario (la app es pública, sin login).
- Persistencia en base de datos (cada sesión es independiente).
- Generación de informe PDF.
- Soporte mobile (se asume pantalla ≥ 1280px, para proyección).
- Modo capacitador con notas privadas (postergado a versión 2).

### Incluido en el MVP (actualización post-revisión)

- **Despliegue público en Render** (free tier) con URL accesible.
- **Repositorio público en GitHub** con README profesional, licencia MIT y .gitignore.
- **Calidad de código profesional**: type hints, docstrings, estructura modular, código limpio.

## 5. Los 11 módulos

| # | Módulo | Contenido principal | Figura |
|---|---|---|---|
| 0 | **Inicio** | Objetivo del proyecto, parámetros generales, mapa del corredor | — (texto + mapa) |
| 1 | **Tensión nominal** | Hefner / Still / 1 kV-km vs escalones colombianos | NUEVA |
| 2 | **Configuración de la línea** | GMD, GMR_L, GMR_C, RMG corona | Reutiliza figura_1 |
| 3 | **Conductor seleccionado** | ACSR Drake: sección transversal, ampacidad, datos | NUEVA |
| 4 | **Parámetros R, L, C + Corona** | Cálculo R/L/C + Peek + gradiente vs altitud | NUEVA |
| 5 | **Línea larga (ABCD)** | Cuadripolo + regulación + pérdidas + eficiencia | NUEVA |
| 6 | **Mecánica del conductor** | 4 hipótesis + ecuación cambio estado + flechas | NUEVA |
| 7 | **Mecánica cable de guarda** | EHS 7/16″ + 4 hipótesis + comparación con conductor | NUEVA |
| 8 | **Aisladores** | Cadena 41 discos + fuga + BIL + fuerzas | Extiende figura_2 |
| 9 | **Torre** | Silueta + distancias RETIE + ángulo protección | Extiende figura_3 |
| 10 | **Plantillado** | Las 4 curvas patrón sobre perfil topográfico | Reutiliza figuras 4-8 |

## 6. Arquitectura técnica

### Stack (modernizado — stack 2026)

| Capa | Tecnología | Razón |
|---|---|---|
| Backend | Python 3.11 + Flask 3 | Maduro, reusa setup previo de Geovani |
| Templating | Jinja2 (server-rendered) | Estándar Flask, sin build step |
| Interactividad cliente | **HTMX 2** + **Alpine.js 3** | Server-driven, sin SPA, sin build, ultraligero |
| Estilos | **Tailwind CSS v3** (standalone CLI) | Moderno, dark mode nativo, shadcn-friendly |
| Componentes | **Shadcn-inspired** (Tailwind + Radix patterns vía Alpine) | Look profesional moderno |
| Renderizado matemático | **KaTeX** (más rápido que MathJax) | LaTeX bonito sin lag |
| Gráficas (técnicas) | Matplotlib (PNG base64 server-side) | Calidad imprenta para diagramas |
| Gráficas (interactivas) | **Chart.js 4** | Curvas en vivo, responsive, dark-aware |
| Iconos | **Lucide** (vía CDN) | Set moderno, consistente |
| Fuentes | **Inter Variable** + **Geist Mono** | Tipografía moderna |
| Animaciones | **Motion One** (Web Animations API wrapper) | Suave sin pesar nada |
| Dark mode | Tailwind `dark:` variant + system pref + manual toggle | Estándar de la industria |
| Servidor producción | gunicorn | Estándar Flask en producción |
| Sesión | Flask session (cookies firmadas) | Sin DB, suficiente para MVP |

### Estructura de carpetas

```
Calculo Linea de Transmision/
├── app.py                          # Flask app principal, rutas de 11 módulos
├── requirements.txt                # flask, matplotlib, numpy
├── calculos/                       # Lógica de cálculo por módulo
│   ├── __init__.py
│   ├── tension.py                  # Hefner, Still, 1 kV/km
│   ├── geometria.py                # GMD, GMR, RMG
│   ├── conductor.py                # Datos del conductor
│   ├── parametros.py               # R, L, C, X, B, Peek
│   ├── linea_larga.py              # ABCD, regulación, pérdidas
│   ├── mecanico_conductor.py       # Ecuación cambio estado, flechas
│   ├── mecanico_guarda.py          # Cable de guarda
│   ├── aisladores.py               # Discos, fuga, BIL, fuerzas
│   ├── torre.py                    # Distancias RETIE
│   └── plantillado.py              # Curvas patrón
├── figuras/                        # Generadores matplotlib
│   ├── __init__.py
│   ├── fig_tension.py              # NUEVA
│   ├── fig_geometria.py            # Adapta figura_1 existente
│   ├── fig_conductor.py            # NUEVA
│   ├── fig_parametros.py           # NUEVA (corona)
│   ├── fig_linea_larga.py          # NUEVA (fasores, perfil V)
│   ├── fig_mecanico.py             # NUEVA (4 hipótesis)
│   ├── fig_guarda.py               # NUEVA
│   ├── fig_aisladores.py           # Extiende figura_2 existente
│   ├── fig_torre.py                # Extiende figura_3 existente
│   └── fig_plantillado.py          # Reusa figuras 4-8 existentes
├── templates/
│   ├── base.html                   # Layout: sidebar + 3 paneles + footer
│   ├── modulo_0_inicio.html
│   ├── modulo_1_tension.html
│   ├── modulo_2_configuracion.html
│   ├── modulo_3_conductor.html
│   ├── modulo_4_parametros.html
│   ├── modulo_5_linea_larga.html
│   ├── modulo_6_mecanico.html
│   ├── modulo_7_guarda.html
│   ├── modulo_8_aisladores.html
│   ├── modulo_9_torre.html
│   └── modulo_10_plantillado.html
├── static/
│   ├── css/estilos.css             # Personalización Bootstrap
│   ├── js/app.js                   # AJAX recálculo en vivo
│   ├── img/                        # Logos, iconos
│   └── data/                       # Tablas estáticas
│       ├── conductores.json        # ACSR, AAAC, ACAR
│       ├── aisladores.json         # ANSI 52-3 y otros
│       └── normativa.json          # RETIE, IEC 60071
├── docs/superpowers/specs/         # Specs del proyecto
└── docs/                           # Documentación de uso
    └── manual_capacitador.md       # Cómo usar la app en clase
```

### Patrón de cada módulo (interfaz)

```
┌────────────────────────────────────────────────────────────────────┐
│  Sidebar (11 módulos)  │  CONTENIDO DEL MÓDULO                    │
│                        │                                            │
│  0. Inicio             │  ┌───────────────┬──────────────────────┐│
│  1. Tensión           │  │ Panel 1:      │ Panel 3:             ││
│  2. Configuración     │  │ PARÁMETROS    │ EXPLICACIÓN          ││
│  3. Conductor         │  │ (inputs)      │ - ¿Qué se calcula?   ││
│  4. Eléctrico         │  │               │ - ¿Para qué sirve?   ││
│  5. Línea larga ←     │  │ [Recalcular]  │ - Fórmula (MathJax) ││
│  6. Mecánico          │  │               │ - ¿Qué pasa si...?  ││
│  7. Cable guarda      │  ├───────────────┤                      ││
│  8. Aisladores        │  │ Panel 2:      │ RESULTADOS           ││
│  9. Torre             │  │ VISUALIZACIÓN │ - Cs = 1,30 ✅       ││
│  10. Plantillado      │  │ (PNG)         │ - Reg = 5,53 % ✅    ││
│                        │  └───────────────┴──────────────────────┘│
│  [Modo Tour: ON ▶]    │  [← Anterior]              [Siguiente →]  │
└────────────────────────────────────────────────────────────────────┘
```

### Flujo de datos

1. Usuario carga la app → `GET /` → renderiza `modulo_0_inicio.html`.
2. Usuario navega a módulo N → `GET /modulo/<n>` → renderiza template del módulo.
3. Usuario cambia un parámetro → JS dispara `POST /api/modulo/<n>/calcular` con los nuevos valores.
4. Flask llama al módulo de cálculo correspondiente (`calculos/<modulo>.py`).
5. Flask llama al generador de figura (`figuras/fig_<modulo>.py`) y obtiene PNG en base64.
6. Flask devuelve JSON con resultados + figura base64.
7. JS actualiza el panel 2 (imagen) y panel 3 (resultados) sin recargar.

### Endpoints Flask

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Redirige a módulo 0 |
| GET | `/modulo/<int:n>` | Renderiza el módulo N (0-10) |
| POST | `/api/modulo/<int:n>/calcular` | Recalcula y devuelve JSON |
| GET | `/api/figura/<int:n>` | Sirve la figura del módulo N |
| GET | `/static/<path>` | Archivos estáticos |

## 7. Reutilización del trabajo previo de Geovani

| Asset existente | Uso en nueva app |
|---|---|
| `generar_figuras.py` (42 KB) | Se descompone en `figuras/fig_*.py` |
| `app.py` (26 KB) existente | Base para nuevo `app.py` (mucho más simple) |
| `templates/index.html` (55 KB) | Inspiración para estilos; nuevo HTML modular |
| 8 figuras PNG generadas | 5 se reutilizan (figura_1, 2, 3, y 4-8 para plantillado) |
| `.venv` | Se mantiene (solo añadir si falta alguna dependencia) |

## 8. Validaciones automáticas por módulo

Cada módulo muestra resultados con un check visual contra criterios:

| Módulo | Validación |
|---|---|
| 1. Tensión | Resultado > 230 kV → justifica salto a 500 kV |
| 2. Configuración | Triángulo válido (desigualdad triangular) |
| 4. Corona | Cs = Ec/Esup > 1 |
| 5. Línea larga | Reg < 19 % AND Pérdidas < 4,7 % AND Eficiencia > 95 % |
| 6. Mecánico | σ_calculado ≤ σ_máx en las 4 hipótesis |
| 7. Cable guarda | Flecha guarda < Flecha conductor (blindaje OK) |
| 8. Aisladores | FS_cadena ≥ 2,0 |
| 9. Torre | Cumple distancias RETIE para 500 kV |
| 10. Plantillado | Curva pie de apoyo no intersecta perfil |

## 9. Roadmap de implementación

**Fase 1 — Scaffold + repo (1 sesión)**
- Crear estructura de carpetas
- `app.py` con las 11 rutas básicas (renderizan templates vacíos)
- `base.html` con layout sidebar + 3 paneles
- `requirements.txt` con dependencias (incluyendo gunicorn)
- `.gitignore`, `LICENSE` (MIT), `README.md` inicial
- Inicializar git, primer commit, conectar con GitHub (público)
- Verificar `python app.py` levanta el servidor local

**Fase 2 — Lógica de cálculo (3 sesiones)**
- Sesión A: módulos 1-4 (eléctricos: tensión, geometría, conductor, parámetros)
- Sesión B: módulos 5-7 (línea larga, mecánico conductor y guarda)
- Sesión C: módulos 8-10 (aisladores, torre, plantillado)

**Fase 3 — Figuras (2 sesiones)**
- Sesión A: figuras nuevas (1, 3, 4, 5, 6, 7)
- Sesión B: adaptación de figuras existentes (2, 8, 9, 10)

**Fase 4 — UI y didáctica (2 sesiones)**
- Sesión A: explicaciones didácticas + fórmulas MathJax
- Sesión B: validaciones, tour mode, pulido visual

**Fase 5 — Documentación (1 sesión)**
- Manual del capacitador
- README profesional con screenshots y demo link

**Fase 6 — Despliegue (1 sesión)**
- `render.yaml` + `Procfile` para Render
- Deploy primera vez a Render
- Verificar app funcionando en URL pública
- Configurar auto-deploy desde rama `main`
- Actualizar README con badge de deploy y URL en vivo

**Total estimado: 10 sesiones de chat**

## 8.5 Sistema de diseño (Design System)

Esta es la "última tecnología de diseño" — patrones modernos 2025-2026 aplicados a una app educativa.

### Filosofía

- **Claridad sobre adorno** — cada elemento visual debe ayudar a entender, no decorar.
- **Densidad de información alta** sin saturación — fuente y espaciado calibrados para proyección en aula.
- **Dark mode nativo** — no es agregado, es ciudadano de primera clase.
- **Animaciones con propósito** — guían la atención del estudiante.

### Paleta de colores (OKLCH-based, dark/light aware)

```css
/* Tokens semánticos — se redefinen automáticamente en dark mode */
:root {
  /* Base */
  --background: oklch(99% 0 0);            /* casi blanco */
  --foreground: oklch(15% 0 0);            /* casi negro */
  --card: oklch(100% 0 0);
  --muted: oklch(96% 0.005 250);
  --border: oklch(91% 0.005 250);

  /* Brand — azul eléctrico (industria energía) */
  --primary: oklch(55% 0.18 250);          /* azul vibrante */
  --primary-foreground: oklch(99% 0 0);

  /* Accent — cobre (conductor eléctrico) */
  --accent: oklch(65% 0.15 50);            /* cobre cálido */
  --accent-foreground: oklch(99% 0 0);

  /* Semánticos */
  --success: oklch(65% 0.15 145);          /* verde — cumple criterio */
  --warning: oklch(75% 0.15 80);           /* amarillo — alerta */
  --danger: oklch(60% 0.20 25);            /* rojo — no cumple */

  /* Curvas técnicas (igual en light/dark, alto contraste sobre fondo) */
  --curve-caliente: oklch(60% 0.18 25);    /* rojo conductor caliente */
  --curve-frio: oklch(50% 0.15 250);       /* azul conductor frío */
  --curve-terreno: oklch(55% 0.15 155);    /* verde distancia terreno */
  --curve-apoyo: oklch(50% 0.18 320);      /* morado pie apoyo */
}

[data-theme="dark"] {
  --background: oklch(12% 0.005 250);      /* azul muy oscuro */
  --foreground: oklch(96% 0 0);
  --card: oklch(16% 0.005 250);
  --muted: oklch(20% 0.005 250);
  --border: oklch(25% 0.005 250);

  --primary: oklch(70% 0.18 250);          /* azul más claro para contraste */
  --accent: oklch(72% 0.15 50);
}
```

### Tipografía

| Uso | Familia | Peso |
|---|---|---|
| UI / Texto general | **Inter Variable** | 400 / 500 / 600 |
| Números técnicos, código, fórmulas | **Geist Mono** | 400 / 500 |
| Headings (h1-h3) | Inter Variable | 700 (con letter-spacing -0.02em) |

Tamaño base 16px. Escala tipográfica: 12 / 14 / 16 / 18 / 24 / 32 / 48 px.

### Espaciado y geometría

- Unidad base: **4 px** (Tailwind default).
- Border-radius: `rounded-lg` (8px) standard; `rounded-xl` (12px) para cards principales.
- Shadows: sutiles en light mode; **glow effects con `box-shadow` de color** en dark mode.
- Layout: max-width 1440px, padding 6 (24px), gap 6.

### Componentes base (estilo shadcn, sin React)

Todos construidos con HTML + Tailwind + Alpine.js para interactividad:

1. **Card** — contenedor base con border + shadow + radius
2. **Button** (variants: primary, secondary, ghost, destructive)
3. **Input** con label flotante y validation state
4. **Select / Combobox** con Alpine
5. **Tooltip** vía Alpine + Tailwind
6. **Tabs** server-driven con HTMX
7. **Dialog / Modal** con Alpine
8. **Badge** (status: ok, warning, error, info)
9. **Progress** (para el tour)
10. **Theme Toggle** (sun/moon icon con animación)
11. **Sidebar Navigation** con active state + progress
12. **Formula Block** (KaTeX rendered)
13. **Figure Viewer** (zoom, download, fullscreen)
14. **Result Card** (valor + unidad + estado + comparación vs criterio)

### Patrón visual de cada módulo

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar          │ Header del módulo                   [🌙 / ☀] │
│ ▸ 0. Inicio      │ ─────────────────────────────────────────────│
│ ▾ 1. Tensión ←   │ ┌─────────────────┐ ┌──────────────────────┐│
│   • Hefner       │ │ PARÁMETROS      │ │ ¿QUÉ SE CALCULA?    ││
│   • Still        │ │                 │ │ Texto didáctico...   ││
│   • 1 kV/km      │ │ Inputs          │ │                      ││
│ ▸ 2. Geometría   │ │ con tooltips    │ │ ¿PARA QUÉ SIRVE?    ││
│ ▸ 3. Conductor   │ │                 │ │ Impacto en el diseño ││
│ ▸ 4. R, L, C     │ │ [Recalcular]    │ │                      ││
│ ▸ 5. Línea larga │ ├─────────────────┤ │ FÓRMULA              ││
│ ▸ 6. Mecánico    │ │ VISUALIZACIÓN   │ │ $E_c = 30·m·δ...$    ││
│ ▸ 7. Guarda      │ │                 │ │                      ││
│ ▸ 8. Aisladores  │ │ [Figura/Gráfica]│ │ RESULTADO            ││
│ ▸ 9. Torre       │ │                 │ │ Cs = 1.30  ✅ Cumple ││
│ ▸ 10. Plantillado│ │ [⬇] [⛶] [↻]    │ │                      ││
│                  │ │                 │ │ ¿QUÉ PASA SI...?    ││
│ ━━━━━━━━━━━━━━  │ │                 │ │ • Subo altitud → ... ││
│ Progress: ▓▓▓░░░ │ │                 │ │ • Cambio conductor → ││
│   3/11 módulos   │ └─────────────────┘ └──────────────────────┘│
│                  │ [← Anterior]                  [Siguiente →] │
└─────────────────────────────────────────────────────────────────┘
```

### Microinteracciones

- **Hover en card**: subtle lift (translateY -2px, shadow más grande, 150ms ease-out).
- **Cambio de módulo**: View Transitions API con cross-fade (300ms).
- **Recálculo en vivo**: input → debounce 400ms → spinner sutil → resultado fade-in.
- **Validation feedback**: shake en input inválido, glow verde si pasa criterio.
- **Theme switch**: smooth color transition (200ms) en todas las superficies.

### Accesibilidad

- **WCAG AA mínimo** en todo el contraste de texto.
- Focus visible con outline de 2px en color `--primary`.
- Navegación completa por teclado.
- ARIA labels en componentes interactivos.
- Soporte para `prefers-reduced-motion`.

## 9.5 Despliegue en Render

### Por qué Render

- **Soporta Flask nativamente** (Python runtime detection automática).
- **Free tier** suficiente para uso educativo (limita: cold start de ~30s tras 15 min sin tráfico — aceptable para clase).
- **Deploy via git push** a rama `main` → auto-deploy.
- **HTTPS gratis** y URL pública estable (`<nombre>.onrender.com`).
- **No requiere autenticación** del usuario final (la app es educativa abierta).

### Archivos necesarios

```python
# Procfile (raíz del repo)
web: gunicorn app:app --workers 2 --timeout 120
```

```yaml
# render.yaml (opcional pero recomendado — Infrastructure as Code)
services:
  - type: web
    name: lineas-transmision-edu
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --workers 2 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.7
      - key: FLASK_ENV
        value: production
```

```txt
# requirements.txt
Flask==3.0.3
matplotlib==3.9.2
numpy==1.26.4
gunicorn==23.0.0
python-dotenv==1.0.1
```

```jsonc
// package.json (solo para build de Tailwind)
{
  "name": "calculo-linea-transmision",
  "version": "1.0.0",
  "scripts": {
    "build:css": "tailwindcss -i ./static/css/input.css -o ./static/css/styles.css --minify",
    "watch:css": "tailwindcss -i ./static/css/input.css -o ./static/css/styles.css --watch"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.13",
    "@tailwindcss/forms": "^0.5.9",
    "@tailwindcss/typography": "^0.5.15"
  }
}
```

### Consideraciones técnicas para Matplotlib en Render

- Usar `matplotlib.use("Agg")` al inicio del módulo de figuras (sin display).
- Reusar figuras con cache en memoria para reducir CPU en cold start.
- Limit de timeout: gunicorn con `--timeout 120` para acomodar generación de figuras complejas.

### Workflow de deploy

1. Geovani hace `git push origin main`.
2. Render detecta el push, ejecuta `buildCommand` (instala pip + npm + tailwind build), luego `startCommand`.
3. App queda accesible en `https://calculo-linea-transmision.onrender.com`.
4. Build típico: 2-3 min. Cold start tras inactividad: 30-60s.

### Build command actualizado para Render

```bash
pip install -r requirements.txt && npm install && npm run build:css
```

Esto asegura que el CSS de Tailwind se compile en producción.

## 9.6 Repositorio público en GitHub

### Información confirmada del usuario

- **Usuario GitHub**: `geovanilozano`
- **Nombre del repo**: `calculo-linea-transmision`
- **URL repo**: `https://github.com/geovanilozano/calculo-linea-transmision`
- **URL deploy Render**: `https://calculo-linea-transmision.onrender.com`
- **Cuenta Render**: ya conectada a GitHub

### Estructura del repo (raíz)

```
calculo-linea-transmision/
├── .github/
│   └── workflows/
│       └── tests.yml               # CI: pytest en cada PR (opcional)
├── .gitignore                      # Python + Node + .venv + __pycache__
├── LICENSE                         # MIT (Geovani Lozano, 2026)
├── README.md                       # Profesional con badges, screenshots, demo
├── Procfile                        # Render
├── render.yaml                     # Render IaC
├── requirements.txt                # Python deps
├── package.json                    # Solo para Tailwind build
├── tailwind.config.js              # Config Tailwind con tokens custom
├── postcss.config.js               # PostCSS para Tailwind
├── app.py                          # Flask app principal
├── config.py                       # Configuración (dev/prod)
├── calculos/                       # Módulos de cálculo
├── figuras/                        # Generadores matplotlib
├── templates/                      # Jinja2
├── static/                         # CSS compilado, JS, data, fonts
├── tests/                          # pytest
└── docs/                           # Manual capacitador + specs
```

### README profesional (estructura)

```markdown
# Diseño de Líneas de Transmisión 500 kV — App Educativa

[![Deploy en Render](https://img.shields.io/badge/deploy-render-46E3B7)](https://lineas-transmision-edu.onrender.com)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> Tour interactivo paso a paso del diseño de una línea aérea de transmisión 500 kV / 307 km / 300 MW, basado en normativa colombiana (RETIE, NTC 2050).

## 🌐 Demo en vivo
[lineas-transmision-edu.onrender.com](https://lineas-transmision-edu.onrender.com)

## 📸 Screenshots
[Imágenes de los módulos principales]

## ✨ Características
- 11 módulos didácticos navegables
- Recálculo en vivo al modificar parámetros
- Visualizaciones técnicas con Matplotlib
- Fórmulas matemáticas con MathJax
- Validaciones automáticas vs normativa

## 🚀 Uso local
[Instalación, dependencias, comandos]

## 📚 Para capacitadores
[Link a docs/manual_capacitador.md]

## 🛠 Stack
Python · Flask · Matplotlib · Bootstrap 5 · MathJax · Render

## 📜 Licencia
MIT
```

### Licencia: MIT

- Permite uso libre (académico y comercial) con atribución.
- Estándar en proyectos educativos open source.

### .gitignore (Python + Node + dev)

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
.pytest_cache/

# Flask
instance/
.flaskenv
.env

# Matplotlib cache
.matplotlib/

# Node (para Tailwind build)
node_modules/

# Build outputs
static/css/styles.css       # Generado por Tailwind (se compila en build)

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Render local
.render/
```

### Convención de commits

- **Atomicos y descriptivos**: un commit = una responsabilidad clara.
- **Mensaje en imperativo**: "Add modulo de tensión", "Fix cálculo GMR", "Update README".
- **Sin atribución a herramientas IA** (commits aparecen como autoría 100% del usuario).
- Tags para versiones: `v0.1.0`, `v1.0.0`, etc.

## 9.7 Estándares de calidad profesional

### Código Python

- **Type hints en todas las funciones públicas**:
  ```python
  def calcular_gmd(d12: float, d23: float, d13: float) -> float:
      """Calcula la Distancia Media Geométrica entre fases.

      Args:
          d12: Distancia entre fase 1 y 2 (m)
          d23: Distancia entre fase 2 y 3 (m)
          d13: Distancia entre fase 1 y 3 (m)

      Returns:
          GMD en metros (raíz cúbica del producto)
      """
      return (d12 * d23 * d13) ** (1/3)
  ```

- **Docstrings estilo Google** para funciones de cálculo.
- **Constantes en MAYÚSCULAS** con unidades en el nombre cuando aplique (`R_MAX_OMS = 25.0`).
- **Separación clara**: cálculos en `calculos/`, vistas en `app.py`, figuras en `figuras/`.
- **Tests para cálculos críticos** (al menos para Peek, ABCD, ecuación cambio estado).

### Frontend

- **Tailwind CSS v3** con tokens semánticos OKLCH (no inventar clases custom innecesarias).
- **HTMX 2** para interactividad server-driven (sin SPA, sin build de JS).
- **Alpine.js 3** para reactividad puntual (theme toggle, dropdowns, tooltips).
- **Accesibilidad WCAG AA mínimo**: labels en inputs, alt en imágenes, focus visible.
- **Dark mode nativo** con `dark:` variants + system preference + manual toggle.
- **Sin jQuery**: ES Modules modernos (fetch, async/await, Web Components donde aplique).
- **View Transitions API** para cambio entre módulos (con fallback).
- **prefers-reduced-motion** respetado en todas las animaciones.

### Documentación

- **README**: para usuarios finales (instalación + uso).
- **docs/manual_capacitador.md**: para Geovani y otros instructores (flujo de clase, qué decir en cada módulo).
- **Docstrings en código**: para desarrolladores.
- **Specs en docs/superpowers/specs/**: historial de decisiones de diseño.

## 10. Decisiones tomadas en auto mode (actualizado v2)

1. **Stack Python + Flask + HTMX + Alpine + Tailwind**. Modernizado tras feedback: necesita verse "fenomenal" con la "última tecnología de diseño". HTMX permite mantener Flask sin saltar a React.
2. **Tailwind CSS v3** (no Bootstrap 5 como en v1). Razón: mejor sistema de tokens, dark mode nativo, look más moderno 2026.
3. **KaTeX** (no MathJax como en v1). Razón: más rápido, mejor render en tipografía moderna.
4. **Chart.js 4** para gráficas interactivas (complementa Matplotlib que sigue para diagramas técnicos).
5. **OKLCH color system** con tokens semánticos. Razón: estándar moderno, soporta P3 wide gamut, mejor para dark mode.
6. **Inter Variable + Geist Mono** como fuentes. Razón: tipografía técnica moderna, excelente para datos.
7. **Datos por defecto: 500 kV / 307 km / haz 3 / 41 discos** (proyecto real del estudiante).
8. **11 módulos** (no 7 como los capítulos del profesor). Razón didáctica.
9. **Deploy en Render** + repo público en GitHub. URL final: `calculo-linea-transmision.onrender.com`.
10. **Layout fijo de 3 paneles** por módulo. Patrón único = curva de aprendizaje plana.
11. **Dark/light mode** como ciudadano de primera clase (no agregado).
12. **Sin autenticación**. App pública para estudiantes.

## 10.5 Estrategia de agentes para implementación

Para construir esto al nivel "lo mejor de lo mejor" usaremos agentes especializados en paralelo donde sea posible. La regla: **tareas independientes que tocan archivos distintos = paralelo; tareas dependientes = secuencial**.

### Agentes a usar

| Skill / Agent | Cuándo se invoca | Para qué |
|---|---|---|
| `superpowers:writing-plans` | Inmediato (después de aprobar spec) | Crear plan detallado de Fase 1 |
| `frontend-design` | Fase 4 (UI polish) | Diseño visual de cada módulo, refinamiento estético |
| `ui-design-system` | Fase 1-4 (continuo) | Asegurar consistencia del design system Tailwind + shadcn-style |
| `web-design-guidelines` | Fase 5 (revisión final) | Audit final de accesibilidad y UX |
| `Agent (general-purpose)` paralelo | Fase 2-3 (cálculos + figuras) | Trabajos independientes en paralelo (ej: módulo de tensión + módulo de geometría simultáneamente) |
| `superpowers:code-reviewer` | Final de cada fase | Review independiente vs spec |
| `superpowers:test-driven-development` | Fase 2 (cálculos críticos) | Tests primero para Peek, ABCD, ecuación cambio estado |

### Ejemplos de paralelización

**Fase 1 (Scaffold)** — secuencial (todo toca configuración base):
1. Crear estructura → 2. Setup git → 3. Setup Render → 4. Verificar build

**Fase 2 (Cálculos)** — paralelo posible:
- Agent A: módulos 1-3 (`tension.py`, `geometria.py`, `conductor.py`)
- Agent B: módulos 4-5 (`parametros.py`, `linea_larga.py`)
- Agent C: módulos 6-7 (`mecanico_conductor.py`, `mecanico_guarda.py`)
- Agent D: módulos 8-10 (`aisladores.py`, `torre.py`, `plantillado.py`)

**Fase 3 (Figuras)** — paralelo (cada figura es archivo distinto):
- 6 figuras nuevas pueden crearse simultáneamente

**Fase 4 (UI)** — invocar `frontend-design` para diseño visual de:
- Sidebar + navegación
- Layout de 3 paneles
- Componentes (cards, inputs, badges, etc.)
- Dark mode polish

## 11. Criterios de éxito

La app se considera exitosa cuando:

1. ✅ Geovani puede dar una capacitación de 60-90 min recorriendo los 11 módulos sin necesidad de salir de la app.
2. ✅ Un estudiante puede modificar parámetros y ver el efecto en regulación/pérdidas/flecha/corona en menos de 2 segundos.
3. ✅ Los 11 módulos cubren el 100% del alcance del informe del estudiante.
4. ✅ Las validaciones automáticas detectan correctamente si cumple/no cumple los criterios del proyecto.
5. ✅ La app levanta con `python app.py` sin errores en Windows 10/11.
6. ✅ El repo público en GitHub tiene README profesional, licencia MIT y .gitignore correcto.
7. ✅ La app está desplegada en Render con URL pública accesible (`*.onrender.com`).
8. ✅ Auto-deploy desde rama `main` funcionando (push → deploy automático).
9. ✅ Otros estudiantes pueden clonar el repo y correr la app local siguiendo solo el README.
10. ✅ Los commits aparecen como autoría única de Geovani (sin atribución a herramientas IA).

---

## 12. Próximos pasos

1. ✅ **Usuario aprobó el spec** (incluye stack moderno, deploy Render, repo público, MIT license).
2. ▶ **Próximo**: invocar skill `superpowers:writing-plans` para crear plan detallado de Fase 1 (Scaffold + Repo).
3. Tras aprobación del plan: ejecución de Fase 1 con agentes paralelos donde aplique.
