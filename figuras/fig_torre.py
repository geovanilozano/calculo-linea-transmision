"""Figura DETALLADA de la torre 500 kV con todas las cotas del documento académico.

Diagrama tipo plano técnico con layout en columnas:
- IZQUIERDA: panel de ángulo de protección + haz + cadena
- CENTRO: torre con todas las cotas
- DERECHA: cotas verticales (H_total, H_apoyo, d_terreno)
- ABAJO: panel RETIE
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, FancyBboxPatch, Circle

from calculos.torre import ResultadoTorre
from figuras import configurar_estilo, figura_a_base64


def _trazar_celosia(ax, x_izq, x_der, y_bot, y_top, color, alpha=0.4, lw=0.6):
    """Dibuja celosía X dentro del trapecio (más sutil para no robar protagonismo)."""
    n = 10
    for i in range(n):
        y0 = y_bot + (y_top - y_bot) * i / n
        y1 = y_bot + (y_top - y_bot) * (i + 1) / n
        t0 = (y0 - y_bot) / max(y_top - y_bot, 0.01)
        t1 = (y1 - y_bot) / max(y_top - y_bot, 0.01)
        x_l0 = x_izq[0] + (x_izq[1] - x_izq[0]) * t0
        x_l1 = x_izq[0] + (x_izq[1] - x_izq[0]) * t1
        x_r0 = x_der[0] + (x_der[1] - x_der[0]) * t0
        x_r1 = x_der[0] + (x_der[1] - x_der[0]) * t1
        ax.plot([x_l0, x_r1], [y0, y1], color=color, linewidth=lw, alpha=alpha)
        ax.plot([x_r0, x_l1], [y0, y1], color=color, linewidth=lw, alpha=alpha)


def generar(r: ResultadoTorre, dark_mode: bool = False) -> str:
    """Genera el diagrama técnico de la torre con todas las cotas."""
    configurar_estilo(dark_mode=False)  # diagrama técnico siempre en light

    fig = plt.figure(figsize=(14, 11))
    gs = fig.add_gridspec(2, 1, height_ratios=[4.5, 1.0], hspace=0.05)
    ax = fig.add_subplot(gs[0, 0])
    ax_retie = fig.add_subplot(gs[1, 0])

    # === Colores ===
    color_torre = "#3a5a7a"
    color_celosia = "#9bb5cf"
    color_cable_g = "#2d5f2d"
    color_punto_g = "#52a035"
    color_fase = "#c54c2f"
    color_cota = "#666"
    color_seg = "#c54c2f"
    color_aisl = "#7a8696"

    # === Dimensiones del cálculo ===
    H = r.h_total_torre_m
    H_apoyo = r.h_apoyo_conductor_m
    sep = r.separacion_fases_adoptada_m
    dh_g = r.cable_guarda_dh_m
    dv_g = r.cable_guarda_dv_m
    remate = r.altura_remate_m
    d_gg = r.d_entre_cables_guarda_m
    flecha = r.flecha_max_m
    L_cad = r.longitud_cadena_m

    y_guarda = H_apoyo + dv_g
    y_top = H

    # === Silueta torre ===
    ancho_base = max(sep * 1.4, 7.0)
    ancho_cintura = max(sep * 0.6, 3.5)
    ancho_top = max(sep * 0.30, 1.5)

    # Tronco
    tronco = np.array([
        [-ancho_base / 2, 0], [ancho_base / 2, 0],
        [ancho_cintura / 2, H_apoyo], [-ancho_cintura / 2, H_apoyo],
    ])
    ax.add_patch(Polygon(tronco, closed=True, facecolor=color_torre,
                          alpha=0.08, edgecolor=color_torre, linewidth=1.2, zorder=2))
    _trazar_celosia(ax, (-ancho_base / 2, -ancho_cintura / 2),
                    (ancho_base / 2, ancho_cintura / 2),
                    0, H_apoyo, color_celosia)

    # Cabeza
    cabeza = np.array([
        [-ancho_cintura / 2, H_apoyo], [ancho_cintura / 2, H_apoyo],
        [ancho_top / 2, y_top], [-ancho_top / 2, y_top],
    ])
    ax.add_patch(Polygon(cabeza, closed=True, facecolor=color_torre,
                          alpha=0.08, edgecolor=color_torre, linewidth=1.2, zorder=2))
    _trazar_celosia(ax, (-ancho_cintura / 2, -ancho_top / 2),
                    (ancho_cintura / 2, ancho_top / 2),
                    H_apoyo, y_top, color_celosia)

    # === Crucetas ===
    cruceta_fases_y = H_apoyo + 0.3
    ax.plot([-sep - 0.6, sep + 0.6], [cruceta_fases_y, cruceta_fases_y],
            color=color_torre, linewidth=2.5, zorder=3)

    cruceta_g_y = y_guarda + 0.3
    ax.plot([-d_gg / 2 - 0.5, d_gg / 2 + 0.5], [cruceta_g_y, cruceta_g_y],
            color=color_torre, linewidth=2.5, zorder=3)

    # === Cables de guarda (2 puntos verdes en la cruceta superior) ===
    x_gi = -d_gg / 2
    x_gd = d_gg / 2
    for x_g in [x_gi, x_gd]:
        ax.add_patch(Circle((x_g, y_guarda), 0.22, color=color_punto_g,
                             ec=color_cable_g, linewidth=1.5, zorder=4))

    # Etiquetas cables guarda (BIEN ARRIBA, fuera de cualquier cota)
    y_label_g = y_top + 1.8
    ax.text(x_gi, y_label_g, "Cable de guarda\nIZQUIERDO",
            ha="center", va="bottom", fontsize=8.5, color=color_cable_g, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color_cable_g, alpha=0.95, linewidth=1))
    ax.text(x_gd, y_label_g, "Cable de guarda\nDERECHO",
            ha="center", va="bottom", fontsize=8.5, color=color_cable_g, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color_cable_g, alpha=0.95, linewidth=1))
    # Líneas desde el cable hasta la etiqueta
    for x_g in [x_gi, x_gd]:
        ax.plot([x_g, x_g], [y_guarda + 0.3, y_label_g - 0.1],
                color=color_cable_g, linewidth=0.6, linestyle=":", alpha=0.6)

    # Cota entre cables de guarda (ENTRE las etiquetas y los puntos)
    y_cota_gg = y_label_g + 1.5
    ax.annotate("", xy=(x_gd, y_cota_gg), xytext=(x_gi, y_cota_gg),
                arrowprops=dict(arrowstyle="<->", color=color_cota, lw=1.0))
    ax.text(0, y_cota_gg + 0.4, f"{d_gg:.1f} m (entre cables de guarda)",
            ha="center", fontsize=8.5, color=color_cota, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor=color_cota, alpha=0.95))

    # === Ángulo de protección (líneas guarda → fase exterior) ===
    for x_g, x_fa in [(x_gi, -sep), (x_gd, sep)]:
        ax.plot([x_g, x_fa], [y_guarda, H_apoyo],
                color=color_punto_g, linewidth=1.0, linestyle="--", alpha=0.6, zorder=3)

    # Etiqueta del ángulo (solo a la IZQUIERDA, no duplicar)
    angulo = r.angulo_proteccion_grados
    x_angulo_label = x_gi - 4.5
    y_angulo_label = (y_guarda + H_apoyo) / 2
    ax.text(x_angulo_label, y_angulo_label,
            f"α = {angulo:.1f}°\n(≤ 30°)",
            ha="center", va="center", fontsize=9, color=color_punto_g, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor=color_punto_g, alpha=0.95, linewidth=1.2))
    # Flecha desde la etiqueta hasta el medio del ángulo
    ax.annotate("", xy=((x_gi + (-sep)) / 2, (y_guarda + H_apoyo) / 2),
                xytext=(x_angulo_label + 1.2, y_angulo_label),
                arrowprops=dict(arrowstyle="->", color=color_punto_g, lw=0.8, alpha=0.7))

    # === Cadenas de aisladores y fases ===
    fases_x = [-sep, 0, sep]
    fases_nombres = ["FASE A", "FASE B", "FASE C"]
    # Altura visual de la cadena (proporcional pero no realista)
    altura_cadena_vis = min(L_cad * 0.7, 3.5)
    # Posición del conductor (debajo de la cadena)
    y_conductor = H_apoyo  # el "apoyo" es el punto del conductor

    for x_f, nombre in zip(fases_x, fases_nombres):
        # Cadena de aisladores: rectángulo claro con bolitas
        y_top_cad = cruceta_fases_y - 0.15
        y_bot_cad = y_top_cad - altura_cadena_vis
        # 2 líneas verticales (cadena doble paralela)
        offsets = [-0.13, 0.13] if r.cadena_doble else [0]
        for dx in offsets:
            ax.plot([x_f + dx, x_f + dx], [y_top_cad, y_bot_cad],
                    color=color_aisl, linewidth=2.5, zorder=3, solid_capstyle="round")
            # Algunos discos visuales (5-6 puntos para indicar)
            n_marcas = 6
            for k in range(n_marcas):
                y_d = y_top_cad - (k + 0.5) * altura_cadena_vis / n_marcas
                ax.add_patch(Circle((x_f + dx, y_d), 0.16, color="#d4d8df",
                                     ec=color_aisl, linewidth=0.5, zorder=4))

        # Haz de subconductores AL FINAL de la cadena
        y_haz = y_bot_cad - 0.4
        _dibujar_haz_visible(ax, x_f, y_haz, r.n_subconductores, r.haz_separacion_m,
                              color_fase)

        # Etiqueta de fase BIEN ABAJO del haz (no se monta con cotas)
        ax.text(x_f, y_haz - 1.6, nombre,
                ha="center", fontsize=11, color=color_fase, fontweight="800")

    # Conductor más bajo = y_haz - flecha
    y_haz_general = cruceta_fases_y - 0.15 - altura_cadena_vis - 0.4
    y_conductor_bajo = y_haz_general - flecha

    # Línea horizontal del conductor más bajo (punteada, solo entre fases extremas)
    ax.plot([-sep - 0.5, sep + 0.5], [y_conductor_bajo, y_conductor_bajo],
            color=color_fase, linestyle=":", linewidth=1.5, alpha=0.6, zorder=2)

    # === Cotas entre fases (debajo de las etiquetas) ===
    y_cota_fases = y_haz_general - 4.0  # bien abajo de los nombres FASE A/B/C
    # Cotas individuales 9m + 9m
    for x0, x1 in [(-sep, 0), (0, sep)]:
        ax.annotate("", xy=(x1, y_cota_fases), xytext=(x0, y_cota_fases),
                    arrowprops=dict(arrowstyle="<->", color=color_cota, lw=1.0))
        ax.text((x0 + x1) / 2, y_cota_fases + 0.3, f"{sep:.1f} m",
                ha="center", fontsize=8.5, color=color_cota, fontweight="700",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor=color_cota, alpha=0.95))

    # Cota entre fases extremas (más abajo)
    y_cota_ext = y_cota_fases - 1.6
    ax.annotate("", xy=(sep, y_cota_ext), xytext=(-sep, y_cota_ext),
                arrowprops=dict(arrowstyle="<->", color=color_cota, lw=1.0))
    ax.text(0, y_cota_ext + 0.3, f"{2 * sep:.1f} m (entre fases extremas)",
            ha="center", fontsize=8.5, color=color_cota, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=color_cota, alpha=0.95))

    # === Cotas VERTICALES (todas a la DERECHA, bien separadas) ===
    # Columna 1: cotas parciales (remate, separación guarda-fases)
    x_col1 = max(sep + 3.5, ancho_base / 2 + 2.5)

    # Remate superior
    ax.annotate("", xy=(x_col1, y_top), xytext=(x_col1, y_guarda),
                arrowprops=dict(arrowstyle="<->", color=color_cota, lw=1.0))
    ax.text(x_col1 + 0.3, (y_top + y_guarda) / 2,
            f"{remate:.1f} m\n(remate\nsuperior)",
            ha="left", va="center", fontsize=8, color=color_cota, fontweight="600")

    # Separación guarda - fases
    ax.annotate("", xy=(x_col1, y_guarda), xytext=(x_col1, H_apoyo),
                arrowprops=dict(arrowstyle="<->", color=color_cota, lw=1.0))
    ax.text(x_col1 + 0.3, (y_guarda + H_apoyo) / 2,
            f"{dv_g:.1f} m\n(separación cable\nde guarda – fases)",
            ha="left", va="center", fontsize=8, color=color_cota, fontweight="600")

    # Columna 2: cotas totales
    x_col2 = x_col1 + 4.5

    # H_total
    ax.annotate("", xy=(x_col2, y_top), xytext=(x_col2, 0),
                arrowprops=dict(arrowstyle="<->", color="#000", lw=1.4))
    ax.text(x_col2 + 0.3, y_top - 1.5,
            f"H_total = {H:.2f} m",
            ha="left", va="top", fontsize=10, color="#000", fontweight="800",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#000", alpha=0.95))

    # H_apoyo (a la IZQUIERDA dentro de la torre, no se monta con la fase C)
    x_h_apoyo = sep + 1.5  # entre fase C y col1
    ax.annotate("", xy=(x_h_apoyo, H_apoyo), xytext=(x_h_apoyo, 0),
                arrowprops=dict(arrowstyle="<->", color=color_seg, lw=1.1))
    ax.text(x_h_apoyo + 0.2, H_apoyo / 2,
            f"H_apoyo\n{H_apoyo:.2f} m\n(altura del apoyo\ndel conductor)",
            ha="left", va="center", fontsize=8, color=color_seg, fontweight="600",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor=color_seg, alpha=0.92, linewidth=0.8))

    # d_terreno (en la columna 2 también, parte inferior)
    ax.annotate("", xy=(x_col2, y_conductor_bajo), xytext=(x_col2, 0),
                arrowprops=dict(arrowstyle="<->", color=color_seg, lw=1.3))
    ax.text(x_col2 + 0.3, y_conductor_bajo / 2,
            f"d_terreno = {r.d_terreno_m:.1f} m\n(RETIE {r.tension_linea_kv:.0f} kV)",
            ha="left", va="center", fontsize=9, color=color_seg, fontweight="700")

    # === Suelo ===
    ax.axhline(0, color="#000", linewidth=1.8, zorder=1)
    x_min_suelo = x_angulo_label - 2
    x_max_suelo = x_col2 + 5
    for x_h in np.linspace(x_min_suelo, x_max_suelo, 50):
        ax.plot([x_h, x_h - 0.4], [0, -0.6], color="#000", linewidth=0.5)

    # === Ejes ===
    ax.set_xlim(x_min_suelo, x_max_suelo)
    ax.set_ylim(y_cota_ext - 2, y_label_g + 4.5)
    ax.set_aspect("equal")
    ax.axis("off")

    titulo = "CONFIGURACIÓN HORIZONTAL PLANA – HAZ "
    titulo += {2: "DOBLE", 3: "TRIPLE", 4: "CUÁDRUPLE"}.get(r.n_subconductores, "SIMPLE")
    ax.set_title(titulo, fontsize=13, fontweight="800", pad=20, color="#1a1a1a")

    # === Panel RETIE inferior ===
    ax_retie.axis("off")
    ax_retie.set_xlim(0, 100)
    ax_retie.set_ylim(0, 10)

    ax_retie.text(50, 9, f"DISTANCIAS DE SEGURIDAD RETIE {r.tension_linea_kv:.0f} kV",
                  ha="center", fontsize=11, fontweight="800", color="#1a1a1a")

    distancias = [
        ("Al terreno", f"d_terreno = {r.d_terreno_m:.1f} m", color_seg),
        ("Entre fases", f"D = {r.separacion_fases_adoptada_m:.1f} m\n(mín. {r.d_entre_fases_m:.2f} m)", color_cota),
        ("Fase – Estructura", f"d_estructura = {r.d_a_estructura_m:.1f} m", color_cota),
        ("Altura del apoyo", f"H_apoyo = {r.h_apoyo_conductor_m:.2f} m", color_seg),
    ]
    x_pos = [10, 32, 54, 76]
    for x, (titulo_d, valor, color) in zip(x_pos, distancias):
        ax_retie.add_patch(FancyBboxPatch((x - 9, 1.5), 18, 6.3,
                                            boxstyle="round,pad=0.1",
                                            facecolor="white",
                                            edgecolor=color, linewidth=1.3))
        ax_retie.text(x, 6.3, titulo_d, ha="center", fontsize=9,
                      fontweight="700", color=color)
        ax_retie.text(x, 3.4, valor, ha="center", fontsize=8.5,
                      color="#1a1a1a", fontfamily="monospace")

    ax_retie.text(50, 0.4,
                  f"Distancias corregidas por altitud ({r.altitud_msnm:.0f} msnm) · Cumple RETIE {r.tension_linea_kv:.0f} kV",
                  ha="center", fontsize=8, color="#666", style="italic")

    plt.tight_layout()
    return figura_a_base64(fig)


def _dibujar_haz_visible(ax, x, y, n_subc, db_m, color):
    """Haz de subconductores visible y bien proporcionado."""
    radio_subc = 0.18
    escala = 3.5  # más visible que antes (era 2.0)
    if n_subc == 3:
        r = db_m * escala / (2.0 * np.sin(np.pi / 3))
        for k in range(3):
            angulo = -np.pi / 2 + k * 2 * np.pi / 3
            xc = x + r * np.cos(angulo)
            yc = y + r * np.sin(angulo)
            ax.add_patch(Circle((xc, yc), radio_subc, color=color, ec="white",
                                linewidth=1.0, zorder=5))
        # Etiqueta db
        ax.text(x + r + 0.4, y - 0.2, f"db = {db_m:.2f} m",
                fontsize=7, color="#444", style="italic", va="center")
    elif n_subc == 2:
        for k in range(2):
            xc = x + (db_m * escala / 2.0) * (-1 + 2 * k)
            ax.add_patch(Circle((xc, y), radio_subc, color=color, ec="white",
                                linewidth=1.0, zorder=5))
    elif n_subc == 4:
        d = db_m * escala / 2.0
        for dx, dy in [(-d, d), (d, d), (-d, -d), (d, -d)]:
            ax.add_patch(Circle((x + dx, y + dy), radio_subc, color=color, ec="white",
                                linewidth=1.0, zorder=5))
    else:
        ax.add_patch(Circle((x, y), radio_subc * 1.4, color=color, ec="white",
                            linewidth=1.0, zorder=5))
