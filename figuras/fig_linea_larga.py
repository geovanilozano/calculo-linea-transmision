"""Figura del módulo de línea larga: perfil de tensión a lo largo de la línea."""
from __future__ import annotations

import cmath
import math

import matplotlib.pyplot as plt
import numpy as np

from calculos.linea_larga import ResultadoLineaLarga
from figuras import configurar_estilo, figura_a_base64


def generar(r: ResultadoLineaLarga, dark_mode: bool = False) -> str:
    """Genera el perfil de magnitud de tensión a lo largo de la línea.

    Útil para visualizar el efecto Ferranti (cuando V crece hacia el receptor).
    """
    configurar_estilo(dark_mode)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    # ===== Gráfico 1: perfil de tensión =====
    color_v = "#3b6dd9"
    color_nominal = "#94a3b8"

    # Recrear gamma y Zc desde los componentes
    zc = complex(r.zc_re, r.zc_im)
    gamma = complex(r.gamma_re, r.gamma_im)

    # Calcular V(x) y I(x) para x desde 0 (receptor) hasta L (generador)
    n_puntos = 50
    distancias_km = np.linspace(0, r.longitud_km, n_puntos)
    vr_complejo = complex(r.vr_fn_kv * 1e3, 0.0)  # V

    # Corriente receptor con ángulo según factor de potencia
    angulo_fp = -math.acos(r.factor_potencia)
    ir_complejo = cmath.rect(r.ir_a, angulo_fp)

    tensiones_ll_kv = []
    for x_km in distancias_km:
        # V(x) = cosh(γ·x)·V_R + Zc·sinh(γ·x)·I_R
        gx = gamma * x_km
        v_x_fn = cmath.cosh(gx) * vr_complejo + zc * cmath.sinh(gx) * ir_complejo
        v_x_ll = abs(v_x_fn) * math.sqrt(3) / 1000.0  # kV línea-línea
        tensiones_ll_kv.append(v_x_ll)

    ax1.plot(distancias_km, tensiones_ll_kv, color=color_v, linewidth=2.5, zorder=3)
    ax1.fill_between(distancias_km, r.tension_nominal_kv, tensiones_ll_kv,
                     where=[v >= r.tension_nominal_kv for v in tensiones_ll_kv],
                     alpha=0.15, color="#dc2626")
    ax1.fill_between(distancias_km, r.tension_nominal_kv, tensiones_ll_kv,
                     where=[v < r.tension_nominal_kv for v in tensiones_ll_kv],
                     alpha=0.15, color="#059669")

    ax1.axhline(r.tension_nominal_kv, color=color_nominal, linestyle="--", linewidth=1, alpha=0.7,
                label=f"Nominal: {r.tension_nominal_kv:.0f} kV")

    # Marcar puntos clave
    ax1.scatter([0], [r.tension_nominal_kv], color=color_v, s=60, zorder=5, ec="white", lw=2)
    ax1.scatter([r.longitud_km], [r.vg_ll_kv], color="#7c3aed", s=60, zorder=5, ec="white", lw=2)

    # Decidir posición de etiquetas según si VG > VR (Ferranti) o VG < VR (normal)
    # Para que NUNCA queden tapadas por la curva o salgan del chart
    es_ferranti = r.vg_ll_kv > r.tension_nominal_kv
    y_offset_receptor = -22 if not es_ferranti else 18
    y_offset_generador = -22 if es_ferranti else 18

    ax1.annotate(f"Receptor\n{r.tension_nominal_kv:.0f} kV", xy=(0, r.tension_nominal_kv),
                 xytext=(12, y_offset_receptor), textcoords="offset points", fontsize=9,
                 color=color_v, fontweight="700", ha="left",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=color_v, alpha=0.85, linewidth=1))
    ax1.annotate(f"Generador\n{r.vg_ll_kv:.1f} kV", xy=(r.longitud_km, r.vg_ll_kv),
                 xytext=(-12, y_offset_generador), textcoords="offset points", fontsize=9,
                 color="#7c3aed", fontweight="700", ha="right",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#7c3aed", alpha=0.85, linewidth=1))

    ax1.set_xlabel("Distancia desde extremo receptor (km)", fontweight="600")
    ax1.set_ylabel("Tensión línea-línea (kV)", fontweight="600")
    ax1.set_title("Perfil de tensión a lo largo de la línea")
    ax1.grid(True, alpha=0.3)
    # Headroom arriba y abajo para que las etiquetas con cajita no se corten
    y_min = min(min(tensiones_ll_kv), r.tension_nominal_kv)
    y_max = max(max(tensiones_ll_kv), r.tension_nominal_kv)
    rango = max(y_max - y_min, 5)
    ax1.set_ylim(y_min - rango * 0.18, y_max + rango * 0.15)
    ax1.legend(loc="upper right", fontsize=9, framealpha=0.92)

    # ===== Gráfico 2: indicadores de desempeño =====
    indicadores = ["Regulación\n(|%|)", "Pérdidas\n(%)", "Eficiencia\n(%)"]
    valores = [abs(r.regulacion_pct), r.perdidas_pct, r.eficiencia_pct]
    limites = [r.reg_max_pct, r.perdidas_max_pct, 95.0]
    estado = [
        abs(r.regulacion_pct) <= r.reg_max_pct,
        r.perdidas_pct <= r.perdidas_max_pct,
        r.eficiencia_pct >= 95.0,
    ]

    colores_ind = ["#3ba163" if s else "#dc2626" for s in estado]

    bars2 = ax2.bar(indicadores, valores, color=colores_ind, width=0.55, edgecolor="none", zorder=3)

    # Etiquetas
    for bar, val in zip(bars2, valores):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, height + max(valores) * 0.03,
                 f"{val:.2f}", ha="center", va="bottom", fontweight="bold", fontsize=11)

    # Líneas de límite
    for i, lim in enumerate(limites):
        ax2.plot([i - 0.3, i + 0.3], [lim, lim], color="#64748b", linestyle="--", linewidth=1.5, zorder=2)
        ax2.text(i + 0.35, lim, f" lim {lim:.1f}", fontsize=8, color="#64748b", va="center")

    ax2.set_title("Indicadores de desempeño")
    ax2.set_ylabel("Porcentaje (%)", fontweight="600")
    ax2.set_ylim(0, max(max(valores), max(limites)) * 1.2)
    ax2.grid(axis="y", alpha=0.3, zorder=0)
    ax2.set_axisbelow(True)

    return figura_a_base64(fig)
