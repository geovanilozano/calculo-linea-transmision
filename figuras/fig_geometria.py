"""Figura del módulo de configuración geométrica.

Diagrama mostrando la disposición de las 3 fases con su haz de subconductores.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np

from calculos.geometria import ResultadoGeometria
from figuras import configurar_estilo, figura_a_base64


def _posiciones_haz(centro_x: float, centro_y: float, n_subc: int, db_m: float) -> list[tuple[float, float]]:
    """Calcula posiciones de los subconductores dentro del haz centrado en (x, y)."""
    if n_subc == 1:
        return [(centro_x, centro_y)]

    # Radio del círculo envolvente
    if n_subc == 2:
        r = db_m / 2.0
    elif n_subc == 3:
        r = db_m / math.sqrt(3.0)
    elif n_subc == 4:
        r = db_m / math.sqrt(2.0)
    else:
        r = db_m / 2.0

    posiciones = []
    for i in range(n_subc):
        angulo = 2 * math.pi * i / n_subc - math.pi / 2  # empezar arriba
        px = centro_x + r * math.cos(angulo)
        py = centro_y + r * math.sin(angulo)
        posiciones.append((px, py))
    return posiciones


def generar(resultado: ResultadoGeometria, dark_mode: bool = False) -> str:
    """Genera el diagrama de configuración de fases con haz.

    Asume configuración horizontal: fases 1, 2, 3 alineadas en x con separaciones D12 y D23.
    Si las distancias forman un triángulo válido, se calcula la posición de fase 2 abajo.

    Returns:
        String base64 del PNG generado
    """
    configurar_estilo(dark_mode)

    fig, ax = plt.subplots(figsize=(9, 6))

    color_fase = "#3b6dd9"
    color_haz_border = "#94a3b8"
    color_label = "#1a1a2e" if not dark_mode else "#f5f5f7"
    color_dim = "#7c2d12"  # cobre/burnt orange

    # Resolver posiciones de las 3 fases (configuración horizontal con fase 2 abajo)
    # Coloca fase 1 en (0,0) y fase 3 en (D13, 0)
    # Calcula fase 2 con triangulación
    d12, d23, d13 = resultado.d12_m, resultado.d23_m, resultado.d13_m

    if resultado.triangulo_valido and d13 > 0:
        x1, y1 = 0.0, 0.0
        x3, y3 = d13, 0.0
        # Posición de fase 2: dado d12 y d23, ubicar el punto
        x2 = (d12 ** 2 - d23 ** 2 + d13 ** 2) / (2.0 * d13)
        y2_sq = d12 ** 2 - x2 ** 2
        # Caso colineal (típico horizontal): y2 = 0
        y2 = -math.sqrt(y2_sq) if y2_sq > 0.001 else 0.0
    else:
        # Fallback si distancias no válidas
        x1, y1 = 0.0, 0.0
        x2, y2 = d12, 0.0
        x3, y3 = d12 + d23, 0.0

    fases = [
        ("Fase R", x1, y1),
        ("Fase S", x2, y2),
        ("Fase T", x3, y3),
    ]

    # Dibujar haces de cada fase
    radio_subc_visual = 0.18  # tamaño visual del subconductor (no es el radio real)
    for nombre, fx, fy in fases:
        # Círculo envolvente del haz (línea punteada)
        if resultado.n_subconductores > 1:
            r_env = resultado.radio_circulo_envolvente_m
            theta = np.linspace(0, 2 * np.pi, 50)
            ax.plot(
                fx + r_env * np.cos(theta),
                fy + r_env * np.sin(theta),
                color=color_haz_border,
                linestyle=":",
                linewidth=1,
                alpha=0.5,
            )

        # Subconductores
        for px, py in _posiciones_haz(fx, fy, resultado.n_subconductores, resultado.db_m):
            circle = plt.Circle(
                (px, py),
                radio_subc_visual,
                color=color_fase,
                ec="white" if not dark_mode else "#1a2333",
                linewidth=1.5,
                zorder=3,
            )
            ax.add_patch(circle)

        # Etiqueta de la fase
        ax.annotate(
            nombre,
            xy=(fx, fy),
            xytext=(fx, fy + 1.0 if fy >= 0 else fy - 1.2),
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=12,
            color=color_fase,
        )

    # Líneas de cota (D12, D23, D13)
    cota_y_offset = max(abs(y2), 1.5) + 1.2

    def draw_cota(x1, y1, x2, y2, label, offset_dir="up"):
        """Dibuja una cota acotada con flechas y etiqueta."""
        # Calcular punto medio para etiqueta
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="<->", color=color_dim, lw=1.2),
        )
        ax.text(
            mx,
            my + (0.4 if offset_dir == "up" else -0.4),
            label,
            ha="center",
            va="center",
            color=color_dim,
            fontsize=10,
            fontweight="600",
            bbox=dict(boxstyle="round,pad=0.3", fc="white" if not dark_mode else "#1a2333", ec=color_dim, lw=1),
        )

    # Cotas entre fases con leve offset arriba/abajo
    draw_cota(x1, y1 + 0.6, x2, y2 + 0.6, f"D12 = {d12:.2f} m", "up")
    draw_cota(x2, y2 + 0.6, x3, y3 + 0.6, f"D23 = {d23:.2f} m", "up")
    draw_cota(x1, y1 - cota_y_offset, x3, y3 - cota_y_offset, f"D13 = {d13:.2f} m", "down")

    # Título y configuración
    ax.set_title(
        f"Configuración de fases — Haz de {resultado.n_subconductores} "
        f"subconductor{'es' if resultado.n_subconductores > 1 else ''} "
        f"(separación {resultado.db_m:.2f} m)"
        if resultado.n_subconductores > 1
        else f"Configuración de fases — Conductor simple",
        pad=15,
    )
    ax.set_xlabel("Posición horizontal (m)")
    ax.set_ylabel("Posición vertical (m)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    # Márgenes
    margen = 2.0
    ax.set_xlim(min(x1, x2, x3) - margen, max(x1, x2, x3) + margen)
    ax.set_ylim(min(y1, y2, y3) - cota_y_offset - 1, max(y1, y2, y3) + 2.5)

    return figura_a_base64(fig)
