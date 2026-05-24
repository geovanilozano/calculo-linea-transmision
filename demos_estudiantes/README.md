# Proyectos de estudiantes

Esta carpeta contiene los proyectos base de cada estudiante (formato JSON).

## Cómo funciona

1. **Tú (Geovani)** preparas un JSON para cada estudiante con sus parámetros
   iniciales (longitud, potencia, conductor, etc.).
2. **El estudiante** abre la app, hace clic en **"Mi proyecto"** (esquina
   superior derecha) → **"Importar proyecto (.json)"** y selecciona su archivo.
3. La app carga los parámetros y los guarda en su navegador (cookie).
4. El estudiante trabaja en su proyecto. Sus cambios persisten en el navegador.
5. Cuando termina, hace clic en **"Exportar mi proyecto (.json)"** y te manda
   el archivo por correo / Drive.
6. **Tú** importas el archivo del estudiante para revisar lo que hizo.

## Estructura del archivo JSON

```json
{
  "version": 1,
  "tipo": "calculo_linea_transmision_proyecto",
  "estudiante": "Nombre Apellido",
  "fecha_exportacion": "2026-05-24T15:00:00Z",
  "proyecto": {
    "nombre": "Línea X - Y",
    "longitud_km": 200,
    "potencia_mw": 150,
    "tension_nominal_kv": 230,
    "altitud_msnm": 1500,
    "vano_diseno_m": 350,
    "factor_potencia": 1.0,
    "regulacion_max_pct": 19.0,
    "perdidas_max_pct": 4.7,
    "frecuencia_hz": 60
    /* ... resto de parámetros ... */
  },
  "conductor_id": "acsr_drake",
  "aislador_id": "ansi_52_3",
  "cable_guarda_id": "ehs_716"
}
```

### Campos mínimos

- `tipo`: debe ser **exactamente** `"calculo_linea_transmision_proyecto"`.
- `proyecto`: objeto con los parámetros del proyecto (todos los que aparecen
  en módulo 0).
- `conductor_id` / `aislador_id` / `cable_guarda_id`: IDs del catálogo
  (ver `static/data/*.json`). Si no aparecen, se usan los defaults.

## Generación rápida desde la app

La forma más fácil de generar un JSON nuevo:

1. Reinicia la app a demo (esquina superior derecha → "Reiniciar").
2. Ve a módulo 0 y cambia los parámetros del estudiante.
3. Cambia conductor en módulo 3 si aplica.
4. Click en "Mi proyecto" → "Exportar mi proyecto".
5. Renombra el archivo y guárdalo en esta carpeta.

## Aislamiento entre estudiantes

- La app usa cookies de Flask, no una base de datos. Cada navegador tiene su
  propio proyecto.
- Si dos estudiantes usan el mismo computador, deben usar perfiles de
  navegador distintos (o ventanas incógnito separadas).
- Los datos del estudiante NO se envían al servidor — viven en su cookie.
- Para revisar el trabajo de un estudiante, pídele que te mande su `.json`
  exportado e impórtalo en tu sesión.

## Ejemplo

`ejemplo_juan_perez.json` es un proyecto de prueba (230 kV / 145 km / 100 MW)
que puedes usar como plantilla para generar los reales.
