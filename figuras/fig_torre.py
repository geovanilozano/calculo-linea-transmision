"""Figura de la torre: silueta con distancias de seguridad acotadas."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, FancyArrowPatch

from calculos.torre import ResultadoTorre
from figuras import configurar_estilo, figura_a_base64


def generar(r: ResultadoTorre, dark_mode: bool = False) -> str:
    """Dibuja la silueta de la torre con cotas RETIE."""
    configurar_estilo(dark_mode)

    fig, ax = plt.subplots(figsize=(8, 9))

    color_torre = "#475569"
    color_celosia = "#94a3b8"
    color_cable = "#1e293b"
    color_cota = "#7c2d12"
    color_dist = "#dc2626"

    H = r.h_total_torre_m
    H_apoyo = r.h_apoyo_conductor_m
    ancho_base = 6.0
    ancho_top = 2.0

    # Silueta de la torre (trapezoidal)
    torre_pts = np.array([
        [-ancho_base / 2, 0],
        [ancho_base / 2, 0],
        [ancho_top / 2, H - 3],
        [ancho_top / 2, H],
        [-ancho_top / 2, H],
        [-ancho_top / 2, H - 3],
    ])
    torre = Polygon(torre_pts, closed=True, facecolor=color_torre, alpha=0.3,
                    edgecolor=color_torre, linewidth=2, zorder=2)
    ax.add_patch(torre)

    # Celosía simplificada (X horizontales y diagonales)
    for y_level in np.linspace(2, H - 5, 8):
        # Ancho de la torre a esta altura
        w = ancho_base / 2 - (ancho_base / 2 - ancho_top / 2) * (y_level / (H - 3))
        ax.plot([-w, w], [y_level, y_level], color=color_celosia, linewidth=0.8, alpha=0.6)
        ax.plot([-w, w], [y_level, y_level + 2], color=color_celosia, linewidth=0.5, alpha=0.4)
        ax.plot([w, -w], [y_level, y_level + 2], color=color_celosia, linewidth=0.5, alpha=0.4)

    # Cruceta y fases (vista frontal, 3 fases horizontales)
    sep = r.separacion_fases_adoptada_m
    y_cruceta = H_apoyo + 0.5
    ax.plot([-sep, sep], [y_cruceta, y_cruceta], color=color_cable, linewidth=2.5, zorder=3)

    # 3 fases (puntos)
    for i, x in enumerate([-sep, 0, sep]):
        ax.scatter([x], [H_apoyo], color="#3b6dd9", s=120, zorder=4, ec="white", lw=1.5)
        # Aisladores simplificados (línea vertical desde cruceta)
        for j in range(5):
            ax.scatter([x], [y_cruceta - 0.15 * (j + 1)], s=8, color="#cbd5e0", zorder=3)
        ax.annotate(f"F{i+1}", (x, H_apoyo), xytext=(8, -8), textcoords="offset points",
                    fontsize=8, color="#3b6dd9", fontweight="600")

    # Cables de guarda arriba
    ax.scatter([0], [H], color=color_cable, s=100, zorder=4, marker="o", ec="white", lw=1.5)
    ax.annotate("Cable de guarda", (0, H), xytext=(10, 5), textcoords="offset points",
                fontsize=8, color=color_cable)

    # Suelo
    ax.axhline(0, color="#1e293b", linewidth=2, zorder=1)
    for x_h in np.linspace(-12, 12, 25):
        ax.plot([x_h, x_h - 0.5], [0, -0.8], color="#1e293b", linewidth=0.6)
    ax.text(0, -1.5, "Suelo", ha="center", fontsize=8, color="#1e293b", style="italic")

    # ===== Cotas =====
    # H total
    ax.annotate("", xy=(-ancho_base / 2 - 2, H), xytext=(-ancho_base / 2 - 2, 0),
                arrowprops=dict(arrowstyle="<->", color=color_cota, lw=1.5))
    ax.text(-ancho_base / 2 - 2.5, H / 2, f"H_total\n{H:.1f} m",
            ha="right", va="center", color=color_cota, fontsize=10, fontweight="600")

    # H apoyo
    ax.annotate("", xy=(ancho_base / 2 + 1, H_apoyo), xytext=(ancho_base / 2 + 1, 0),
                arrowprops=dict(arrowstyle="<->", color=color_cota, lw=1.2))
    ax.text(ancho_base / 2 + 1.5, H_apoyo / 2, f"H_apoyo\n{H_apoyo:.1f} m",
            ha="left", va="center", color=color_cota, fontsize=9)

    # D terreno
    ax.annotate("", xy=(sep + 1, H_apoyo - r.flecha_max_m), xytext=(sep + 1, 0),
                arrowprops=dict(arrowstyle="<->", color=color_dist, lw=1.2))
    ax.text(sep + 1.5, (H_apoyo - r.flecha_max_m) / 2, f"D_terreno\n≥ {r.d_terreno_m:.1f} m",
            ha="left", va="center", color=color_dist, fontsize=9, fontweight="600")

    # Punto más bajo del conductor (línea horizontal punteada)
    ax.axhline(H_apoyo - r.flecha_max_m, xmin=0.35, xmax=0.8, color=color_dist,
               linestyle=":", linewidth=1.2, alpha=0.7)

    # Configuración del eje
    ax.set_xlim(-12, 12)
    ax.set_ylim(-2.5, H + 4)
    ax.set_aspect("equal")
    ax.axis("off")

    blindaje_text = f"Ángulo protección: {r.angulo_proteccion_grados:.1f}° "
    blindaje_text += "(≤ 30° OK)" if r.cumple_blindaje else "(> 30° revisar)"
    ax.set_title(
        f"Silueta de la torre — Diseño preliminar\n{blindaje_text}",
        fontsize=11,
    )

    return figura_a_base64(fig)
