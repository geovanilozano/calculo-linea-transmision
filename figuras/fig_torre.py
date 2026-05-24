"""Figura DETALLADA de la torre 500 kV con todas las cotas del documento académico.

Recrea el diagrama tipo plano técnico con:
- Cable de guarda izquierdo y derecho (con distancia entre ambos)
- 3 fases con sus cadenas de aisladores y haz triple
- Ángulo de protección α visualizado y calculado
- Todas las cotas: H_total, H_apoyo, d_terreno, distancias entre fases
- Panel inferior con distancias RETIE 500 kV
- Todos los valores se ACTUALIZAN automáticamente con los parámetros del cálculo.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, FancyBboxPatch, Rectangle, Circle, FancyArrowPatch

from calculos.torre import ResultadoTorre
from figuras import configurar_estilo, figura_a_base64


def _trazar_celosia(ax, x_izq, x_der, y_bot, y_top, color, alpha=0.5, lw=0.7):
    """Dibuja celosía en X dentro de un trapecio definido por los 4 puntos."""
    n = 8
    for i in range(n):
        y0 = y_bot + (y_top - y_bot) * i / n
        y1 = y_bot + (y_top - y_bot) * (i + 1) / n
        # Ancho a estas alturas
        t0 = (y0 - y_bot) / max(y_top - y_bot, 0.01)
        t1 = (y1 - y_bot) / max(y_top - y_bot, 0.01)
        x_l0 = x_izq[0] + (x_izq[1] - x_izq[0]) * t0
        x_l1 = x_izq[0] + (x_izq[1] - x_izq[0]) * t1
        x_r0 = x_der[0] + (x_der[1] - x_der[0]) * t0
        x_r1 = x_der[0] + (x_der[1] - x_der[0]) * t1
        # X
        ax.plot([x_l0, x_r1], [y0, y1], color=color, linewidth=lw, alpha=alpha)
        ax.plot([x_r0, x_l1], [y0, y1], color=color, linewidth=lw, alpha=alpha)
        # horizontal
        ax.plot([x_l1, x_r1], [y1, y1], color=color, linewidth=lw, alpha=alpha * 0.7)


def _dibujar_cadena_aisladores(ax, x, y_top, n_discos, doble=True):
    """Dibuja una cadena de aisladores como serie de discos."""
    color_disco = "#cbd5e0"
    color_metal = "#475569"
    # La cadena vertical desde y_top hacia abajo
    # Para no sobrecargar: si n_discos > 20, dibujamos representación visual proporcional
    # con menos discos pero mantenemos la altura real
    n_dibuja = min(n_discos, 20)
    disco_h = 0.15
    altura_total = n_dibuja * disco_h

    # Líneas paralelas si doble
    offsets = [-0.05, 0.05] if doble else [0]
    for dx in offsets:
        for i in range(n_dibuja):
            y_disco = y_top - 0.2 - (i + 0.5) * disco_h
            d = Circle((x + dx, y_disco), 0.07, color=color_disco,
                       ec=color_metal, linewidth=0.4, zorder=4)
            ax.add_patch(d)
        # Herraje arriba y abajo
        ax.plot([x + dx, x + dx], [y_top, y_top - 0.2],
                color=color_metal, linewidth=1.2, zorder=3)
        y_bot_cadena = y_top - 0.2 - n_dibuja * disco_h
        ax.plot([x + dx, x + dx], [y_bot_cadena, y_bot_cadena - 0.15],
                color=color_metal, linewidth=1.2, zorder=3)

    return y_top - 0.2 - n_dibuja * disco_h - 0.15  # y inferior de la cadena


def _dibujar_haz(ax, x, y, n_subc, db_m, escala=2.0):
    """Dibuja el haz de subconductores como n círculos formando un haz."""
    color = "#3b6dd9"
    radio_subc = 0.12
    # Para n=3 (triángulo equilátero invertido apuntando abajo)
    if n_subc == 3:
        r = db_m * escala / (2.0 * np.sin(np.pi / 3))  # radio del círculo circunscrito
        for k in range(3):
            angulo = -np.pi / 2 + k * 2 * np.pi / 3
            xc = x + r * np.cos(angulo)
            yc = y + r * np.sin(angulo)
            ax.add_patch(Circle((xc, yc), radio_subc, color=color, ec="white",
                                linewidth=0.8, zorder=5))
        return
    if n_subc == 2:
        for k in range(2):
            xc = x + (db_m * escala / 2.0) * (-1 + 2 * k)
            ax.add_patch(Circle((xc, y), radio_subc, color=color, ec="white",
                                linewidth=0.8, zorder=5))
        return
    if n_subc == 4:
        d = db_m * escala / 2.0
        for dx, dy in [(-d, d), (d, d), (-d, -d), (d, -d)]:
            ax.add_patch(Circle((x + dx, y + dy), radio_subc, color=color, ec="white",
                                linewidth=0.8, zorder=5))
        return
    # default: 1 subconductor
    ax.add_patch(Circle((x, y), radio_subc * 1.2, color=color, ec="white",
                        linewidth=0.8, zorder=5))


def generar(r: ResultadoTorre, dark_mode: bool = False) -> str:
    """Genera el diagrama técnico de la torre con todas las cotas."""
    configurar_estilo(dark_mode=False)  # forzar light para el diagrama técnico

    fig = plt.figure(figsize=(13, 11))
    # Layout: torre principal arriba (80%) + panel RETIE abajo (20%)
    gs = fig.add_gridspec(2, 1, height_ratios=[4.0, 1.0], hspace=0.1)
    ax = fig.add_subplot(gs[0, 0])
    ax_retie = fig.add_subplot(gs[1, 0])

    # === Colores estilo blueprint ===
    color_torre = "#3a5a7a"          # azul acero
    color_celosia = "#7a9bb8"
    color_cable_guarda = "#2d4f1f"    # verde oscuro
    color_punto_guarda = "#52a035"    # verde
    color_fase = "#c54c2f"            # naranja-rojo
    color_dist_cota = "#5a5a5a"       # gris cota
    color_dist_seg = "#c54c2f"        # rojo para distancias críticas

    # === Dimensiones ===
    H = r.h_total_torre_m
    H_apoyo = r.h_apoyo_conductor_m
    sep = r.separacion_fases_adoptada_m
    dh_guarda = r.cable_guarda_dh_m
    dv_guarda = r.cable_guarda_dv_m
    remate = r.altura_remate_m
    d_guarda_guarda = r.d_entre_cables_guarda_m
    flecha = r.flecha_max_m

    # Altura cable de guarda
    y_guarda = H_apoyo + dv_guarda
    # Altura del remate superior (top de torre)
    y_top_torre = H

    # === Silueta de la torre (trapezoidal, dos secciones: tronco y cabeza) ===
    ancho_base = max(sep * 2 * 0.7, 6.0)  # base proporcional
    ancho_cintura = max(sep * 0.55, 3.0)  # a la altura del apoyo del conductor
    ancho_top = max(sep * 0.30, 1.5)      # remate superior

    # Tronco principal (base hasta y_apoyo)
    torre_tronco_izq = (-ancho_base / 2, -ancho_cintura / 2)
    torre_tronco_der = (ancho_base / 2, ancho_cintura / 2)
    tronco_pts = np.array([
        [-ancho_base / 2, 0],
        [ancho_base / 2, 0],
        [ancho_cintura / 2, H_apoyo],
        [-ancho_cintura / 2, H_apoyo],
    ])
    ax.add_patch(Polygon(tronco_pts, closed=True, facecolor=color_torre,
                          alpha=0.12, edgecolor=color_torre, linewidth=1.5, zorder=2))
    _trazar_celosia(ax, torre_tronco_izq, torre_tronco_der, 0, H_apoyo, color_celosia)

    # Cabeza de la torre (apoyo hasta remate)
    cabeza_pts = np.array([
        [-ancho_cintura / 2, H_apoyo],
        [ancho_cintura / 2, H_apoyo],
        [ancho_top / 2, y_top_torre],
        [-ancho_top / 2, y_top_torre],
    ])
    ax.add_patch(Polygon(cabeza_pts, closed=True, facecolor=color_torre,
                          alpha=0.12, edgecolor=color_torre, linewidth=1.5, zorder=2))
    _trazar_celosia(ax,
                    (-ancho_cintura / 2, -ancho_top / 2),
                    (ancho_cintura / 2, ancho_top / 2),
                    H_apoyo, y_top_torre, color_celosia)

    # === Crucetas (horizontales) ===
    # Cruceta principal del conductor
    cruceta_y = H_apoyo + 0.5
    ax.plot([-sep - 0.5, sep + 0.5], [cruceta_y, cruceta_y],
            color=color_torre, linewidth=2.5, zorder=3)

    # Cruceta superior (cables de guarda)
    cruceta_guarda_y = y_guarda + 0.3
    ax.plot([-d_guarda_guarda / 2 - 0.5, d_guarda_guarda / 2 + 0.5],
            [cruceta_guarda_y, cruceta_guarda_y],
            color=color_torre, linewidth=2.5, zorder=3)

    # === Cables de guarda (2) ===
    x_guarda_izq = -d_guarda_guarda / 2
    x_guarda_der = d_guarda_guarda / 2
    for x_g in [x_guarda_izq, x_guarda_der]:
        ax.add_patch(Circle((x_g, y_guarda), 0.18, color=color_punto_guarda,
                             ec=color_cable_guarda, linewidth=1.5, zorder=4))

    # Etiquetas cables de guarda
    ax.text(x_guarda_izq, y_guarda + 1.2, "Cable de guarda\nIZQUIERDO",
            ha="center", fontsize=8, color=color_cable_guarda, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color_cable_guarda, alpha=0.9))
    ax.text(x_guarda_der, y_guarda + 1.2, "Cable de guarda\nDERECHO",
            ha="center", fontsize=8, color=color_cable_guarda, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color_cable_guarda, alpha=0.9))

    # Cota entre cables de guarda
    ax.annotate("", xy=(x_guarda_der, cruceta_guarda_y + 1.8),
                xytext=(x_guarda_izq, cruceta_guarda_y + 1.8),
                arrowprops=dict(arrowstyle="<->", color=color_dist_cota, lw=1.2))
    ax.text(0, cruceta_guarda_y + 2.0, f"{d_guarda_guarda:.1f} m",
            ha="center", fontsize=9, color=color_dist_cota, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=color_dist_cota, alpha=0.95))
    ax.text(0, cruceta_guarda_y + 1.3, "(entre cables\nde guarda)",
            ha="center", fontsize=7, color=color_dist_cota, style="italic")

    # === Ángulo de protección (líneas punteadas desde cables de guarda a fases externas) ===
    for x_g, x_fase in [(x_guarda_izq, -sep), (x_guarda_der, sep)]:
        ax.plot([x_g, x_fase], [y_guarda, H_apoyo],
                color=color_punto_guarda, linewidth=1.2, linestyle="--", alpha=0.7, zorder=3)

    # Etiqueta del ángulo
    angulo = r.angulo_proteccion_grados
    ax.text(x_guarda_izq - 1.5, y_guarda - 1.5,
            f"α = {angulo:.1f}°\n(≤ 30°)",
            ha="center", fontsize=8, color=color_punto_guarda, fontweight="600",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color_punto_guarda, alpha=0.9))
    ax.text(x_guarda_der + 1.5, y_guarda - 1.5,
            f"α = {angulo:.1f}°\n(≤ 30°)",
            ha="center", fontsize=8, color=color_punto_guarda, fontweight="600",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color_punto_guarda, alpha=0.9))

    # === 3 fases con cadenas de aisladores y haces ===
    fases_x = [-sep, 0, sep]
    fases_nombres = ["FASE A", "FASE B", "FASE C"]
    for i, (x_f, nombre) in enumerate(zip(fases_x, fases_nombres)):
        # Cadena de aisladores (cuelga de la cruceta)
        y_bot_cadena = _dibujar_cadena_aisladores(
            ax, x_f, cruceta_y, r.n_discos_aislador, doble=r.cadena_doble
        )
        # Haz de subconductores al final de la cadena
        _dibujar_haz(ax, x_f, y_bot_cadena - 0.15, r.n_subconductores, r.haz_separacion_m)
        # Etiqueta de fase
        ax.text(x_f, y_bot_cadena - 1.0, nombre,
                ha="center", fontsize=9, color=color_fase, fontweight="700")

    # === Cotas entre fases adyacentes (9 m + 9 m) ===
    y_cota_fases = H_apoyo - flecha - 1.5
    if y_cota_fases < 1.5:
        y_cota_fases = H_apoyo - 5
    for x0, x1 in [(-sep, 0), (0, sep)]:
        ax.annotate("", xy=(x1, y_cota_fases), xytext=(x0, y_cota_fases),
                    arrowprops=dict(arrowstyle="<->", color=color_dist_cota, lw=1.2))
        ax.text((x0 + x1) / 2, y_cota_fases + 0.3, f"{sep:.1f} m",
                ha="center", fontsize=9, color=color_dist_cota, fontweight="700",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor=color_dist_cota, alpha=0.95))

    # Cota entre fases extremas (18 m)
    y_cota_ext = y_cota_fases - 2.0
    ax.annotate("", xy=(sep, y_cota_ext), xytext=(-sep, y_cota_ext),
                arrowprops=dict(arrowstyle="<->", color=color_dist_cota, lw=1.2))
    ax.text(0, y_cota_ext + 0.3, f"{2 * sep:.1f} m (entre fases extremas)",
            ha="center", fontsize=9, color=color_dist_cota, fontweight="700",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=color_dist_cota, alpha=0.95))

    # === Cotas verticales a la derecha ===
    x_cota_der = max(sep + 4, ancho_base / 2 + 3)

    # Remate superior (entre cruceta guarda y top torre)
    ax.annotate("", xy=(x_cota_der, y_top_torre), xytext=(x_cota_der, cruceta_guarda_y),
                arrowprops=dict(arrowstyle="<->", color=color_dist_cota, lw=1.2))
    ax.text(x_cota_der + 0.3, (y_top_torre + cruceta_guarda_y) / 2,
            f"{remate:.1f} m\n(remate\nsuperior)",
            ha="left", va="center", fontsize=8, color=color_dist_cota)

    # Separación cable guarda - fases
    ax.annotate("", xy=(x_cota_der, y_guarda), xytext=(x_cota_der, H_apoyo),
                arrowprops=dict(arrowstyle="<->", color=color_dist_cota, lw=1.2))
    ax.text(x_cota_der + 0.3, (y_guarda + H_apoyo) / 2,
            f"{dv_guarda:.1f} m\n(separación cable\nde guarda – fases)",
            ha="left", va="center", fontsize=8, color=color_dist_cota)

    # H total
    x_cota_total = x_cota_der + 4
    ax.annotate("", xy=(x_cota_total, H), xytext=(x_cota_total, 0),
                arrowprops=dict(arrowstyle="<->", color="#000", lw=1.5))
    ax.text(x_cota_total + 0.3, H / 2,
            f"H_total = {H:.2f} m",
            ha="left", va="center", fontsize=10, color="#000", fontweight="700")

    # H_apoyo
    ax.annotate("", xy=(x_cota_total, H_apoyo), xytext=(x_cota_total, 0),
                arrowprops=dict(arrowstyle="<->", color=color_dist_seg, lw=1.2))
    ax.text(x_cota_total - 0.5, H_apoyo - 1.5,
            f"H_apoyo = {H_apoyo:.2f} m\n(altura del apoyo\ndel conductor)",
            ha="right", va="top", fontsize=8, color=color_dist_seg, fontweight="600",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=color_dist_seg, alpha=0.95))

    # d_terreno (distancia mínima al suelo desde el conductor más bajo)
    y_conductor_bajo = H_apoyo - flecha
    ax.annotate("", xy=(x_cota_total, y_conductor_bajo), xytext=(x_cota_total, 0),
                arrowprops=dict(arrowstyle="<->", color=color_dist_seg, lw=1.5))
    ax.text(x_cota_total + 0.3, y_conductor_bajo / 2,
            f"d_terreno = {r.d_terreno_m:.1f} m\n(RETIE {r.tension_linea_kv:.0f} kV)",
            ha="left", va="center", fontsize=9, color=color_dist_seg, fontweight="700")

    # Línea horizontal del conductor más bajo
    ax.plot([-sep - 1, sep + 1], [y_conductor_bajo, y_conductor_bajo],
            color=color_fase, linestyle=":", linewidth=1.5, alpha=0.7)

    # === Suelo ===
    suelo_y = 0
    ax.axhline(suelo_y, color="#000", linewidth=2, zorder=1)
    for x_h in np.linspace(-x_cota_total - 1, x_cota_total + 2, 35):
        ax.plot([x_h, x_h - 0.4], [suelo_y, suelo_y - 0.6], color="#000", linewidth=0.6)

    # === Configuración del eje principal ===
    ax.set_xlim(x_guarda_izq - 5, x_cota_total + 6)
    ax.set_ylim(-2, H + 3)
    ax.set_aspect("equal")
    ax.axis("off")

    titulo = "CONFIGURACIÓN HORIZONTAL PLANA – HAZ "
    titulo += {2: "DOBLE", 3: "TRIPLE", 4: "CUÁDRUPLE"}.get(r.n_subconductores, "SIMPLE")
    ax.set_title(titulo, fontsize=13, fontweight="700", pad=15, color="#1a1a1a")

    # === Panel inferior: distancias RETIE ===
    ax_retie.axis("off")
    ax_retie.set_xlim(0, 100)
    ax_retie.set_ylim(0, 10)

    # Título del panel
    ax_retie.text(50, 9, f"DISTANCIAS DE SEGURIDAD RETIE {r.tension_linea_kv:.0f} kV",
                  ha="center", fontsize=11, fontweight="700", color="#1a1a1a")

    # Distancias
    distancias = [
        ("Al terreno", f"d_terreno = {r.d_terreno_m:.1f} m", color_dist_seg),
        ("Entre fases", f"D = {r.separacion_fases_adoptada_m:.1f} m\n(mín. {r.d_entre_fases_m:.2f} m)", color_dist_cota),
        ("Fase – Estructura", f"d_estructura = {r.d_a_estructura_m:.1f} m", color_dist_cota),
        ("Altura del apoyo", f"H_apoyo = {r.h_apoyo_conductor_m:.2f} m", color_dist_seg),
    ]

    x_pos = [10, 32, 54, 76]
    for x, (titulo_d, valor, color) in zip(x_pos, distancias):
        # Caja con borde
        ax_retie.add_patch(FancyBboxPatch((x - 9, 1), 18, 7,
                                            boxstyle="round,pad=0.1",
                                            facecolor="white",
                                            edgecolor=color, linewidth=1.5))
        ax_retie.text(x, 6.3, titulo_d, ha="center", fontsize=9,
                      fontweight="600", color=color)
        ax_retie.text(x, 3.5, valor, ha="center", fontsize=8.5,
                      color="#1a1a1a", fontfamily="monospace")

    # Nota inferior
    ax_retie.text(50, 0.2,
                  f"Nota: distancias corregidas por altitud ({r.altitud_msnm:.0f} msnm). Cumple RETIE para {r.tension_linea_kv:.0f} kV.",
                  ha="center", fontsize=8, color="#666", style="italic")

    plt.tight_layout()
    return figura_a_base64(fig)
