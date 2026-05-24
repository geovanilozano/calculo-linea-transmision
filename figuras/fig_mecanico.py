"""Figura del módulo mecánico: comparación de las 4 hipótesis (cargas y flechas)."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from calculos.mecanico import ResultadoMecanico
from figuras import configurar_estilo, figura_a_base64


def generar(r: ResultadoMecanico, dark_mode: bool = False) -> str:
    """Compara las 4 hipótesis en cargas (peso, viento, resultante) y flechas."""
    configurar_estilo(dark_mode)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))

    nombres = [h.nombre for h in r.hipotesis]
    pesos = [r.masa_kg_m * 9.8 for _ in r.hipotesis]  # mismo peso en todas
    vientos = [h.wv_n_m for h in r.hipotesis]
    flechas = [h.flecha_m for h in r.hipotesis]

    # Colores de cada hipótesis
    color_peso = "#94a3b8"
    color_viento = "#c97a3b"
    color_flecha = "#3b6dd9"
    color_gobernante = "#3ba163"
    color_max_flecha = "#dc2626"

    # ===== Gráfico 1: cargas (peso + viento) =====
    x = np.arange(len(nombres))
    width = 0.35

    bars1 = ax1.bar(x - width / 2, pesos, width, label="Peso propio (N/m)",
                    color=color_peso, edgecolor="none", zorder=3)
    bars2 = ax1.bar(x + width / 2, vientos, width, label="Carga viento (N/m)",
                    color=color_viento, edgecolor="none", zorder=3)

    for bar, val in zip(bars1, pesos):
        ax1.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=9)
    for bar, val in zip(bars2, vientos):
        ax1.text(bar.get_x() + bar.get_width() / 2, val + 0.5,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=9)

    ax1.set_xticks(x)
    ax1.set_xticklabels(
        [f"Hip {n}\n{h.descripcion}" for n, h in zip(nombres, r.hipotesis)],
        fontsize=8,
    )
    ax1.set_ylabel("Carga (N/m)", fontweight="600")
    ax1.set_title(f"Cargas por hipótesis — {r.nombre_elemento}")
    ax1.legend(loc="best", fontsize=9)
    ax1.grid(axis="y", alpha=0.3, zorder=0)
    ax1.set_axisbelow(True)

    # ===== Gráfico 2: flechas =====
    # La barra más alta (flecha máx) en rojo, la gobernante en verde
    flecha_max = max(flechas)
    colores_f = []
    for i, h in enumerate(r.hipotesis):
        if flechas[i] == flecha_max:
            colores_f.append(color_max_flecha)
        elif h.nombre == r.hipotesis_gobernante:
            colores_f.append(color_gobernante)
        else:
            colores_f.append(color_flecha)

    bars3 = ax2.bar(x, flechas, color=colores_f, width=0.55, edgecolor="none", zorder=3)

    for bar, val, h in zip(bars3, flechas, r.hipotesis):
        ax2.text(bar.get_x() + bar.get_width() / 2, val + flecha_max * 0.02,
                 f"{val:.2f} m", ha="center", va="bottom", fontweight="bold", fontsize=10)

    ax2.set_xticks(x)
    ax2.set_xticklabels(
        [f"Hip {n}\nFS={h.factor_seguridad}" for n, h in zip(nombres, r.hipotesis)],
        fontsize=8,
    )
    ax2.set_ylabel("Flecha (m)", fontweight="600")
    ax2.set_title(f"Flechas por hipótesis  ·  vano = {r.vano_m:.0f} m")
    ax2.set_ylim(0, flecha_max * 1.18)

    # Anotación de la gobernante
    ax2.text(0.5, 0.97, f"Gobernante: Hip {r.hipotesis_gobernante}  |  Flecha máx: {flecha_max:.2f} m",
             transform=ax2.transAxes, fontsize=9, ha="center", va="top",
             bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=color_gobernante, lw=1))

    ax2.grid(axis="y", alpha=0.3, zorder=0)
    ax2.set_axisbelow(True)

    return figura_a_base64(fig)
