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
