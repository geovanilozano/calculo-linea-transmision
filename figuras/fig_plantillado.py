"""Figura del módulo de plantillado: 4 curvas patrón sobre perfil topográfico."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from calculos.plantillado import ResultadoPlantillado
from figuras import configurar_estilo, figura_a_base64


def generar(r: ResultadoPlantillado, dark_mode: bool = False) -> str:
    """Dibuja las 4 curvas patrón sobre un perfil topográfico de ejemplo."""
    configurar_estilo(dark_mode)

    fig, ax = plt.subplots(figsize=(11, 6))

    # Estilos de líneas para distinguir las 4 curvas
    estilos = ["-", "--", "-.", ":"]

    # Plotear las 4 curvas
    for curva, estilo in zip(r.curvas, estilos):
        # Para "Pie de apoyo" usamos valores negativos (referidos al pie de torre)
        ax.plot(
            curva.puntos_x_m,
            curva.puntos_y_m,
            color=curva.color,
            linestyle=estilo,
            linewidth=2,
            label=curva.nombre,
            zorder=3,
        )

    # Torres (postes verticales en los extremos)
    h_torre = r.altura_apoyo_conductor_m + 1
    torre_w = 4.0
    color_torre = "#475569"

    x_torre_izq = r.vano_diseno_m / 2 * -1
    x_torre_der = r.vano_diseno_m / 2
    h_apoyo = r.altura_apoyo_conductor_m

    # Pies de apoyo (parte inferior, "y = -H_apoyo" si curva caliente referencia a 0)
    ax.plot([x_torre_izq, x_torre_izq], [-h_apoyo, 2], color=color_torre, linewidth=4, alpha=0.8)
    ax.plot([x_torre_der, x_torre_der], [-h_apoyo, 2], color=color_torre, linewidth=4, alpha=0.8)
    ax.scatter([x_torre_izq, x_torre_der], [0, 0], s=60, color=color_torre, zorder=5)

    # Perfil topográfico de ejemplo (terreno irregular bajo las curvas)
    x_perfil = np.linspace(x_torre_izq * 1.1, x_torre_der * 1.1, 100)
    # Crear un perfil topográfico más realista (ondulado, en torno a -H_apoyo)
    perfil_y = (
        -h_apoyo
        + 2.5 * np.sin(x_perfil / 50.0) * np.cos(x_perfil / 30.0)
        + 1.5 * np.sin(x_perfil / 18.0)
    )
    ax.fill_between(x_perfil, perfil_y - 8, perfil_y, color="#8b7355", alpha=0.5, zorder=1)
    ax.plot(x_perfil, perfil_y, color="#5d4037", linewidth=1.5, alpha=0.9, zorder=2,
            label="Perfil del terreno")

    # Leyenda
    ax.legend(loc="lower right", framealpha=0.95, fontsize=9, ncol=2)

    # Configuración
    ax.set_xlabel("Distancia desde centro del vano (m)", fontweight="600")
    ax.set_ylabel("Altura (m)  — referida al conductor caliente", fontweight="600")
    ax.set_title(
        f"Plantilla — vano {r.vano_diseno_m:.0f} m  ·  "
        f"f_máx = {r.flecha_max_m:.2f} m  ·  f_mín = {r.flecha_min_m:.2f} m",
        pad=12,
    )
    ax.set_xlim(x_torre_izq * 1.15, x_torre_der * 1.15)
    ax.set_ylim(-h_apoyo - 5, r.flecha_max_m * 1.5)
    ax.grid(True, alpha=0.3, zorder=0)
    ax.set_axisbelow(True)

    # Línea horizontal de referencia (cota del conductor caliente en el centro)
    ax.axhline(0, color="#94a3b8", linestyle=":", linewidth=0.8, alpha=0.5)

    return figura_a_base64(fig)
