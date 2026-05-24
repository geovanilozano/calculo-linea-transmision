"""Figura del módulo de parámetros eléctricos + Corona.

Gráfico comparativo: gradiente superficial vs gradiente crítico, con margen de seguridad.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from calculos.parametros import ResultadoParametros
from figuras import configurar_estilo, figura_a_base64


def generar(resultado: ResultadoParametros, dark_mode: bool = False) -> str:
    """Genera el gráfico de barras de gradientes superficial vs crítico."""
    configurar_estilo(dark_mode)

    fig, ax = plt.subplots(figsize=(9, 5))

    color_sup = "#3b6dd9"  # azul (gradiente del conductor)
    color_critico = "#3ba163"  # verde (umbral de seguridad)
    color_danger = "#dc2626"  # rojo si excede

    # Barras horizontales para comparar
    categorias = ["Gradiente\nsuperficial\n(E_sup)", "Gradiente\ncrítico\n(E_c)"]
    valores = [resultado.gradiente_superficial_kv_cm, resultado.gradiente_critico_kv_cm]
    colores = [
        color_danger if resultado.gradiente_superficial_kv_cm >= resultado.gradiente_critico_kv_cm else color_sup,
        color_critico,
    ]

    bars = ax.barh(categorias, valores, color=colores, height=0.5, edgecolor="none", zorder=3)

    # Etiquetas
    for bar, val in zip(bars, valores):
        ax.text(
            val + max(valores) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"  {val:.2f} kV/cm",
            va="center",
            ha="left",
            fontweight="bold",
            fontsize=11,
        )

    # Título con coeficiente de seguridad
    cs = resultado.coef_seguridad_corona
    cumple = "✓" if resultado.corona_cumple else "✗"
    estado_color = color_critico if resultado.corona_cumple else color_danger
    ax.set_title(
        f"Verificación de Corona (Peek)  ·  Cs = {cs:.2f}  {cumple}",
        pad=15,
        color=estado_color,
    )

    ax.set_xlabel("Gradiente eléctrico (kV/cm, valor pico)", fontweight="600")
    ax.set_xlim(0, max(valores) * 1.25)
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)
    ax.invert_yaxis()  # primera barra arriba

    # Anotación con condiciones
    info = (
        f"Altitud: {resultado.altitud_msnm:.0f} msnm  |  "
        f"Densidad relativa: δ = {resultado.densidad_relativa:.3f}  |  "
        f"T = {resultado.temperatura_c:.0f}°C"
    )
    fig.text(0.5, -0.02, info, ha="center", fontsize=9, color="#64748b", style="italic")

    return figura_a_base64(fig)
