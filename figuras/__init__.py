"""Generadores de figuras técnicas con matplotlib.

Todas las figuras se generan en backend Agg (sin display) y se devuelven
como base64 PNG para incrustar en HTML.
"""
from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("Agg")  # Backend sin display, requerido para servidor


def figura_a_base64(fig) -> str:
    """Convierte una figura matplotlib a string base64 PNG.

    Cierra la figura al final para liberar memoria.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor="none")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("ascii")
    matplotlib.pyplot.close(fig)
    buf.close()
    return encoded


def configurar_estilo(dark_mode: bool = False) -> None:
    """Aplica el estilo visual coherente con el design system de la app."""
    import matplotlib.pyplot as plt

    if dark_mode:
        fg = "#f5f5f7"
        grid = "#2d3a52"
    else:
        fg = "#1a1a2e"
        grid = "#e5e7eb"

    plt.rcParams.update(
        {
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "axes.edgecolor": fg,
            "axes.labelcolor": fg,
            "axes.titlecolor": fg,
            "xtick.color": fg,
            "ytick.color": fg,
            "text.color": fg,
            "grid.color": grid,
            "grid.alpha": 0.4,
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Arial", "DejaVu Sans"],
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.autolayout": True,
        }
    )
