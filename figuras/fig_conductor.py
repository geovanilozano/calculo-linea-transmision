"""Figura del conductor: sección transversal del ACSR con hilos de Al y núcleo de acero."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np

from figuras import configurar_estilo, figura_a_base64


def generar(
    diametro_exterior_mm: float = 28.14,
    n_hilos_aluminio: int = 26,
    n_hilos_acero: int = 7,
    dark_mode: bool = False,
) -> str:
    """Genera la sección transversal del conductor ACSR (26 Al / 7 acero típico Drake).

    Returns:
        String base64 del PNG generado
    """
    configurar_estilo(dark_mode)

    fig, ax = plt.subplots(figsize=(7, 7))

    # Colores
    color_acero = "#4a5568"  # gris acero
    color_aluminio = "#cbd5e0"  # gris claro aluminio
    color_borde = "#2d3748"

    # Radio total y de cada hilo
    R_total = diametro_exterior_mm / 2.0

    # Calcular el radio de cada hilo a partir del diámetro exterior
    # Para 26/7: 1 acero central + 6 acero capa 1 (radio = 2r_a) + 12 Al capa 2 + 14 Al capa 3 (exterior)
    # Si todos los hilos tienen igual diámetro d_hilo:
    # R_total = 4 * d_hilo (aproximadamente para 26/7)
    # → d_hilo ≈ R_total / 4
    d_hilo = R_total / 3.65  # aproximación visual estándar
    r_hilo = d_hilo / 2.0

    # Dibujar capa por capa (de afuera hacia adentro para que las exteriores tapen)
    # Capa 3 exterior: 14 hilos Al en R ~ R_total - r_hilo
    n_c3 = 14
    R_c3 = R_total - r_hilo
    for i in range(n_c3):
        theta = 2 * math.pi * i / n_c3 + math.pi / n_c3
        x = R_c3 * math.cos(theta)
        y = R_c3 * math.sin(theta)
        circle = plt.Circle((x, y), r_hilo, color=color_aluminio, ec=color_borde, linewidth=1)
        ax.add_patch(circle)

    # Capa 2: 12 hilos Al en R ~ R_total - 3*r_hilo
    n_c2 = 12
    R_c2 = R_total - 3 * r_hilo
    for i in range(n_c2):
        theta = 2 * math.pi * i / n_c2
        x = R_c2 * math.cos(theta)
        y = R_c2 * math.sin(theta)
        circle = plt.Circle((x, y), r_hilo, color=color_aluminio, ec=color_borde, linewidth=1)
        ax.add_patch(circle)

    # Capa 1: 6 hilos acero en R ~ 2*r_hilo
    n_c1 = 6
    R_c1 = 2 * r_hilo
    for i in range(n_c1):
        theta = 2 * math.pi * i / n_c1
        x = R_c1 * math.cos(theta)
        y = R_c1 * math.sin(theta)
        circle = plt.Circle((x, y), r_hilo, color=color_acero, ec=color_borde, linewidth=1)
        ax.add_patch(circle)

    # Centro: 1 hilo acero
    circle = plt.Circle((0, 0), r_hilo, color=color_acero, ec=color_borde, linewidth=1)
    ax.add_patch(circle)

    # Cota del diámetro
    ax.annotate(
        "",
        xy=(R_total, -R_total - 3),
        xytext=(-R_total, -R_total - 3),
        arrowprops=dict(arrowstyle="<->", color="#7c2d12", lw=1.5),
    )
    ax.text(
        0,
        -R_total - 4,
        f"D = {diametro_exterior_mm:.2f} mm",
        ha="center",
        va="top",
        fontsize=11,
        fontweight="600",
        color="#7c2d12",
    )

    # Leyenda
    legend_elements = [
        plt.Circle((0, 0), 1, color=color_acero, label=f"Acero ({n_hilos_acero} hilos)"),
        plt.Circle((0, 0), 1, color=color_aluminio, label=f"Aluminio ({n_hilos_aluminio} hilos)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", framealpha=0.95, fontsize=10)

    # Configuración del eje
    ax.set_xlim(-R_total - 5, R_total + 5)
    ax.set_ylim(-R_total - 8, R_total + 3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"Sección transversal ACSR ({n_hilos_aluminio}/{n_hilos_acero})\nVista aumentada",
        pad=10,
        fontsize=12,
    )

    return figura_a_base64(fig)
