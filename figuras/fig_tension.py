"""Figura del módulo de selección de tensión.

Gráfico de barras comparando los 3 criterios (Hefner, Still, 1 kV/km)
contra los escalones normalizados de Colombia (115, 230, 500 kV).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from calculos.tension import ESCALONES_NORMALIZADOS_KV, ResultadoTension
from figuras import configurar_estilo, figura_a_base64


def generar(resultado: ResultadoTension, dark_mode: bool = False) -> str:
    """Genera el gráfico comparativo de los 3 criterios vs escalones normalizados.

    Args:
        resultado: ResultadoTension con los valores calculados
        dark_mode: Si True, usa paleta oscura

    Returns:
        String base64 del PNG generado
    """
    configurar_estilo(dark_mode)

    fig, ax = plt.subplots(figsize=(9, 5))

    # Datos
    criterios = ["Hefner", "Still", "1 kV / km"]
    valores = [resultado.hefner_kv, resultado.still_kv, resultado.regla_1kvkm_kv]

    # Color del proyecto (azul OKLCH primary aproximado en RGB)
    color_primary = "#3b6dd9"
    color_accent = "#c97a3b"
    color_success = "#3ba163"
    color_muted = "#94a3b8"

    # Colores condicionales: si supera el escalón seleccionado, lo destaca
    colores = []
    for v in valores:
        if v >= resultado.tension_recomendada_kv:
            colores.append(color_accent)
        else:
            colores.append(color_primary)

    # Barras
    bars = ax.bar(criterios, valores, color=colores, width=0.55, edgecolor="none", zorder=3)

    # Etiquetas en las barras
    for bar, val in zip(bars, valores):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + max(valores) * 0.02,
            f"{val:.0f} kV",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    # Líneas horizontales para los escalones normalizados
    for escalon in ESCALONES_NORMALIZADOS_KV:
        if escalon == resultado.tension_recomendada_kv:
            # El escalón seleccionado destacado
            ax.axhline(
                y=escalon,
                color=color_success,
                linestyle="-",
                linewidth=2.5,
                alpha=0.9,
                zorder=2,
                label=f"{escalon} kV (seleccionado)",
            )
            ax.text(
                len(criterios) - 0.3,
                escalon,
                f"  ► {escalon} kV  ",
                va="center",
                ha="left",
                fontweight="bold",
                color=color_success,
                fontsize=11,
            )
        else:
            ax.axhline(
                y=escalon,
                color=color_muted,
                linestyle="--",
                linewidth=1,
                alpha=0.5,
                zorder=1,
            )
            ax.text(
                len(criterios) - 0.3,
                escalon,
                f"  {escalon} kV",
                va="center",
                ha="left",
                color=color_muted,
                fontsize=9,
            )

    # Configuración del eje
    ax.set_ylabel("Tensión (kV)", fontweight="600")
    ax.set_title(
        f"Comparación de criterios P = {resultado.potencia_mw:.0f} MW, "
        f"L = {resultado.longitud_km:.0f} km",
        pad=15,
    )
    # Eje Y con headroom amplio para que la leyenda NO se monte sobre las barras/labels
    ax.set_ylim(0, max(max(valores), ESCALONES_NORMALIZADOS_KV[-1]) * 1.30)
    ax.grid(axis="y", zorder=0)
    ax.set_axisbelow(True)

    # Leyenda POR ENCIMA del gráfico (fuera del área de barras) para que no se muerda
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, fc=color_primary, label="Criterio < escalón"),
        plt.Rectangle((0, 0), 1, 1, fc=color_accent, label="Criterio ≥ escalón"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=2,
        framealpha=0.9,
        fontsize=9,
        frameon=False,
    )
    # Espacio inferior extra para acomodar la leyenda externa
    plt.subplots_adjust(bottom=0.18)

    return figura_a_base64(fig)
