"""Figura del módulo de aisladores: representación esquemática de la cadena."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from calculos.aisladores import ResultadoAisladores
from figuras import configurar_estilo, figura_a_base64


def generar(r: ResultadoAisladores, dark_mode: bool = False) -> str:
    """Visualización esquemática de la cadena de aisladores + comparación criterios."""
    configurar_estilo(dark_mode)

    fig = plt.figure(figsize=(11, 6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1.5])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # ===== Gráfico 1: cadena esquemática (vista lateral) =====
    n = r.n_discos_adoptado
    color_disco = "#cbd5e0"
    color_herraje = "#475569"
    color_metalico = "#1e293b"

    # Cruceta arriba
    ax1.plot([-0.5, 0.5], [n + 1, n + 1], color=color_metalico, linewidth=3, solid_capstyle="round")
    ax1.text(0, n + 1.3, "Cruceta de la torre", ha="center", fontsize=9, color=color_metalico)

    # Herraje superior
    ax1.plot([0, 0], [n + 1, n + 0.5], color=color_herraje, linewidth=2)

    # Discos (de arriba abajo)
    for i in range(n):
        y = n - 0.5 - i
        disco = plt.Circle((0, y), 0.35, color=color_disco, ec=color_metalico, linewidth=0.7)
        ax1.add_patch(disco)
        # Numero ocasional
        if (i + 1) % 5 == 0 or i == n - 1:
            ax1.text(0.55, y, f"{i + 1}", fontsize=7, va="center", color=color_metalico)

    # Herraje inferior y "conductor" — con más separación para que NO se monte sobre el último disco
    ax1.plot([0, 0], [-0.5, -2.0], color=color_herraje, linewidth=2)
    ax1.plot([-0.8, 0.8], [-2.3, -2.3], color=color_metalico, linewidth=4, solid_capstyle="round")
    ax1.text(0, -3.0, "Conductor", ha="center", fontsize=9, color=color_metalico, fontweight="600")

    ax1.set_xlim(-2, 2)
    ax1.set_ylim(-3.8, n + 2)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title(f"Cadena de {n} discos\n(altura ≈ {r.longitud_cadena_m:.2f} m, peso ≈ {r.peso_cadena_kg:.0f} kg)",
                  fontsize=11, pad=8)

    # ===== Gráfico 2: comparación criterios =====
    criterios = [f"Por fuga\n(k={r.k_contaminacion_mm_kv:.0f} mm/kV)",
                 f"Por BIL\n({r.bil_kv:.0f} kV)",
                 "Adoptado"]
    valores = [r.n_discos_por_fuga, r.n_discos_por_bil, r.n_discos_adoptado]
    color_fuga = "#3b6dd9"
    color_bil = "#c97a3b"
    color_adoptado = "#3ba163"
    colores = [color_fuga, color_bil, color_adoptado]

    bars = ax2.bar(criterios, valores, color=colores, width=0.55, edgecolor="none", zorder=3)

    for bar, val in zip(bars, valores):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, height + max(valores) * 0.02,
                 str(val), ha="center", va="bottom", fontweight="bold", fontsize=13)

    ax2.set_ylabel("Número de discos", fontweight="600")
    ax2.set_title(f"Criterios de selección  ·  Tensión: {r.tension_linea_kv:.0f} kV")
    ax2.set_ylim(0, max(valores) * 1.18)
    ax2.grid(axis="y", alpha=0.3, zorder=0)
    ax2.set_axisbelow(True)

    # FS info
    fs_text = f"FS cadena simple: {r.fs_cadena_simple:.2f}  |  FS cadena doble: {r.fs_cadena_doble:.2f}"
    if r.cadena_doble_requerida:
        fs_text += "  →  Adoptar cadena DOBLE"
    fig.text(0.5, -0.02, fs_text, ha="center", fontsize=9, color="#64748b", style="italic")

    return figura_a_base64(fig)
