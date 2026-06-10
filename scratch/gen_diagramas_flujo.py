# -*- coding: utf-8 -*-
"""
Genera los diagramas de flujo de trabajo de los códigos (Fases 0-7) en estilo
dark-mode transparente, para la presentación rediseñada de la Tarea 2 ELI556.
Salida: output/Extra_Resultados/diagramas/*.png
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

# --- Paleta consistente con el deck ---
C_BG     = 'none'
C_PANEL  = '#1F2833'
C_PANEL2 = '#27313F'
C_GOLD   = '#F1C40F'
C_CYAN   = '#00D2FF'
C_ORANGE = '#FF5E3A'
C_WHITE  = '#FBFCFD'
C_GREY   = '#9AA5B1'
C_GREEN  = '#2ECC71'

OUT = 'output/Extra_Resultados/diagramas'
os.makedirs(OUT, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'


def box(ax, x, y, w, h, title, lines, edge=C_CYAN, title_color=C_GOLD,
        fc=C_PANEL, fs_title=11.5, fs_body=9.8, lw=1.6, title_bold=True):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
                       linewidth=lw, edgecolor=edge, facecolor=fc, zorder=2)
    ax.add_patch(p)
    cy = y + h - 0.055
    ax.text(x + w/2, cy, title, ha='center', va='top', fontsize=fs_title,
            color=title_color, fontweight='bold' if title_bold else 'normal', zorder=3)
    body = '\n'.join(lines)
    if body:
        ax.text(x + w/2, y + (h - 0.11)/2.05, body, ha='center', va='center',
                fontsize=fs_body, color=C_WHITE, zorder=3, linespacing=1.45)


def filebox(ax, x, y, w, h, label, sub='', edge=C_ORANGE, fs=9.5):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.010,rounding_size=0.012",
                       linewidth=1.4, edgecolor=edge, facecolor='#161B22',
                       linestyle=(0, (4, 2)), zorder=2)
    ax.add_patch(p)
    txt = label if not sub else label + '\n' + sub
    ax.text(x + w/2, y + h/2, txt, ha='center', va='center', fontsize=fs,
            color=edge, zorder=3, linespacing=1.4, family='monospace')


def arrow(ax, x1, y1, x2, y2, color=C_GOLD, lw=2.2, style='-|>', ms=16):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=ms,
                        linewidth=lw, color=color, zorder=4)
    ax.add_patch(a)


def new_fig(w=12.8, h=5.6):
    fig = plt.figure(figsize=(w, h), facecolor=C_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, transparent=True)
    plt.close(fig)
    print('OK ->', name)


# ============================================================
# 1) PIPELINE GENERAL (Fases 0-7, serpentina en 2 filas)
# ============================================================
fig, ax = new_fig(12.8, 6.2)

ROW1, ROW2 = 0.62, 0.10
BH = 0.30
BW = 0.205
xs = [0.015, 0.265, 0.515, 0.765]

fases_r1 = [
    ("FASE 0 · Exploración", ["fase0_setup.py", "Inspección bases CEC y", "Sandia de pvlib. Selección:", "mSi0166  /  HIT05667"], C_CYAN),
    ("FASE 1 · Emulación", ["fase1_filtro_emulacion.py", "Reescritura de metadatos,", "desfase +6 meses y", "proyección al año 2026"], C_CYAN),
    ("FASE 2 · Recurso Solar", ["fase2_recurso_solar.py", "Lectura streaming + limpieza.", "POA (Perez) y Tc (SAPM)", "minuto de medición a medición"], C_CYAN),
    ("FASE 3 · Parámetros", ["fase3_extraccion_parametros.py", "Filtro SRC, regresiones α/β y", "ajuste 5 parámetros De Soto", "(minimize + bounds físicos)"], C_CYAN),
]
fases_r2 = [
    ("FASE 7 · Export", ["fase7_export_slides.py", "Exporta láminas a PNG vía", "COM PowerPoint para QA", "visual del resultado"], C_GOLD),
    ("FASE 6 · Deck", ["fase6_gen_presentation.py", "Genera la presentación", "python-pptx, diseño dark", "premium (este documento)"], C_GOLD),
    ("FASE 5 · Gráficos", ["fase5_gen_extra_plots.py", "Curvas I-V/P-V en SRC,", "día típico, PR comparativo,", "degradación térmica"], C_GOLD),
    ("FASE 4 · Simulación", ["fase4_simulacion_final.py", "calcparams_desoto +", "singlediode (Lambert W).", "Energía anual y PR mensual"], C_GOLD),
]

for (t, l, e), x in zip(fases_r1, xs):
    box(ax, x, ROW1, BW, BH, t, l, edge=e)
for (t, l, e), x in zip(fases_r2, xs):
    box(ax, x, ROW2, BW, BH, t, l, edge=e)

# flechas fila 1
for i in range(3):
    arrow(ax, xs[i] + BW + 0.004, ROW1 + BH/2, xs[i+1] - 0.006, ROW1 + BH/2)
# bajada serpentina
arrow(ax, xs[3] + BW/2, ROW1 - 0.012, xs[3] + BW/2, ROW2 + BH + 0.012 + 0.055)
# fila 2 (derecha a izquierda)
for i in range(3, 0, -1):
    arrow(ax, xs[i] - 0.006, ROW2 + BH/2, xs[i-1] + BW + 0.004, ROW2 + BH/2)

# artefactos entre fases (etiquetas sobre las flechas)
art = [
    (xs[0]+BW+0.125, ROW1+BH+0.035, "Base datos original/\n11 CSV NREL (~1.2 GB)"),
    (xs[1]+BW+0.125, ROW1+BH+0.035, "data/Atacama_2026/\n2 CSV emulados"),
    (xs[2]+BW+0.125, ROW1+BH+0.035, "Datos_Fase2_{mod}.csv\n(limpio: POA + Tc)"),
    (xs[3]+BW/2-0.115, (ROW1+ROW2+BH)/2, "parametros_desoto\n.json (×2 módulos)"),
    (xs[2]+BW+0.125, ROW2-0.052, "Simulacion_{mod}\n_Atacama.csv"),
    (xs[1]+BW+0.125, ROW2-0.052, "Extra_Resultados/\n*.png"),
    (xs[0]+BW+0.125, ROW2-0.052, "output/*.pptx"),
]
for x, y, t in art:
    ax.text(x, y, t, ha='center', va='center', fontsize=8.6, color=C_GREY,
            family='monospace', linespacing=1.35)

save(fig, 'pipeline_general.png')

# ============================================================
# 2) ESTRUCTURA DEL CSV NREL (anatomía del archivo)
# ============================================================
fig, ax = new_fig(12.8, 6.4)

# Bloque archivo a la izquierda
box(ax, 0.013, 0.10, 0.30, 0.82, "Cocoa_mSi0166.csv  (~102 MB)",
    [], edge=C_CYAN, fs_title=11.5)
# líneas internas del archivo
rows = [
    ("Línea 1-2 · METADATOS", "módulo, ciudad, zona horaria,\nlat, lon, altitud, tilt, azimut", C_GOLD),
    ("Línea 3 · ENCABEZADO", "43 columnas fijas con nombre\ny unidad de cada variable", C_GOLD),
    ("Líneas 4+ · REGISTROS", "1 fila = 1 curva I-V completa\ncada 5 min (solo horas de sol)\n36,765 filas (ene/11-mar/12)", C_ORANGE),
    ("Cola variable de la fila", "n pares (I, V) crudos de la\ncurva trazada (n ≈ 180-380)\n→ longitud de fila VARIABLE", C_ORANGE),
]
yy = 0.745
for t, b, e in rows:
    box(ax, 0.030, yy - 0.125, 0.266, 0.158, t, b.split('\n'), edge=e,
        fc=C_PANEL2, fs_title=10.0, fs_body=8.9, lw=1.2)
    yy -= 0.170

# Grupos de columnas (centro)
grupos = [
    ("Eléctricas (usadas)", ["Isc, Pmp, Imp, Vmp, Voc", "+ FF e incertidumbres"], C_GREEN, 0.74),
    ("Meteorológicas (usadas)", ["GHI, DNI, DHI, T_bulbo seco,", "presión atmosférica"], C_GREEN, 0.525),
    ("Referencia POA (verificación)", ["Piranómetro CMP22 en el", "plano del arreglo + incert."], C_CYAN, 0.31),
    ("No usadas en la simulación", ["T_dorso módulo, humedad rel.,", "lluvia, soiling derate, QA", "residual, mantenimiento, n"], C_GREY, 0.065),
]
for t, b, e, y in grupos:
    box(ax, 0.40, y, 0.265, 0.185 if y > 0.05 else 0.20, t, b, edge=e,
        fs_title=10.8, fs_body=9.4)
    arrow(ax, 0.316, 0.40, 0.398, y + 0.09, color=C_GREY, lw=1.3, ms=11)

# Decisiones de ingesta (derecha)
box(ax, 0.735, 0.55, 0.252, 0.37, "Decisión de ingesta",
    ["Lector streaming (módulo csv)", "indexa SOLO 11 columnas clave", "por posición fija y descarta la", "cola I-V de longitud variable.",
     "Evita el fallo de pd.read_csv", "con filas irregulares y reduce", "la huella de memoria."],
    edge=C_GOLD, fs_title=11.5, fs_body=9.6)
box(ax, 0.735, 0.10, 0.252, 0.37, "Limpieza aplicada",
    ["Centinela -9999 → NaN", "dropna en GHI/DNI/DHI/T_air", "clip(≥0) en irradiancias",
     "Válidos: 35,669 / 36,765 (97.0%)", "HIT: 37,313 / 38,377 (97.2%)"],
    edge=C_ORANGE, fs_title=11.5, fs_body=9.6)
arrow(ax, 0.667, 0.63, 0.733, 0.70, color=C_GOLD, lw=1.8, ms=13)
arrow(ax, 0.667, 0.40, 0.733, 0.30, color=C_ORANGE, lw=1.8, ms=13)

save(fig, 'estructura_csv.png')

# ============================================================
# 3) FLUJO FASE 1 — Filtro de emulación geográfica
# ============================================================
fig, ax = new_fig(12.8, 4.6)
Y, H, W = 0.26, 0.48, 0.178

filebox(ax, 0.012, Y + 0.10, 0.135, 0.28, "Cocoa_*.csv", "(Florida)", edge=C_CYAN)
box(ax, 0.175, Y, W, H, "1 · Metadatos",
    ["Reescribe ubicación:", "lat -22.91°, lon -68.20°,", "alt 2400 m, TZ UTC-4,", "tilt 22.91°, azimut 0° (N)"], edge=C_CYAN)
box(ax, 0.385, Y, W, H, "2 · Desfase +6 meses",
    ["relativedelta(months=6)", "invierno⇄verano para", "alinear solsticios entre", "hemisferios"], edge=C_GOLD)
box(ax, 0.595, Y, W, H, "3 · Proyección 2026",
    ["Fuerza año = 2026.", "29-feb → 28-feb.", "Jul-sep 2026 quedan con", "doble cobertura (2 años)"], edge=C_GOLD)
filebox(ax, 0.815, Y + 0.10, 0.165, 0.28, "Atacama2026_*.csv", "(data/Atacama_2026)", edge=C_ORANGE)

arrow(ax, 0.149, Y + 0.24, 0.172, Y + 0.24)
arrow(ax, 0.175 + W + 0.003, Y + 0.24, 0.382, Y + 0.24)
arrow(ax, 0.385 + W + 0.003, Y + 0.24, 0.592, Y + 0.24)
arrow(ax, 0.595 + W + 0.003, Y + 0.24, 0.812, Y + 0.24)
ax.text(0.5, 0.055, "Procesamiento línea a línea en streaming: solo cambia el timestamp y la cabecera; las mediciones no se alteran.",
        ha='center', fontsize=10.5, color=C_GREY, style='italic')
save(fig, 'flujo_fase1.png')

# ============================================================
# 4) FLUJO FASE 2 — Recurso solar y perfil térmico
# ============================================================
fig, ax = new_fig(12.8, 4.9)
Y, H, W = 0.30, 0.50, 0.158

filebox(ax, 0.010, Y + 0.11, 0.125, 0.28, "Atacama2026\n_*.csv", edge=C_CYAN)
box(ax, 0.158, Y, W, H, "1 · Ingesta streaming",
    ["csv.reader fila a fila;", "extrae 11 columnas por", "índice; descarta cola I-V"], edge=C_CYAN)
box(ax, 0.345, Y, W, H, "2 · Limpieza",
    ["-9999→NaN, dropna,", "clip(≥0) irradiancias,", "viento fijo = 1 m/s"], edge=C_CYAN)
box(ax, 0.532, Y, W, H, "3 · POA (Perez)",
    ["get_solarposition +", "get_total_irradiance", "(albedo default 0.25)"], edge=C_GOLD)
box(ax, 0.719, Y, W, H, "4 · Tc (SAPM)",
    ["sapm_cell con coefs.", "open_rack glass_polymer", "(m-Si) / glass_glass (HIT)"], edge=C_ORANGE)
filebox(ax, 0.902, Y + 0.11, 0.088, 0.28, "Datos_\nFase2_*", edge=C_ORANGE)

xarr = [(0.137, 0.155), (0.158 + W + 0.003, 0.342), (0.345 + W + 0.003, 0.529),
        (0.532 + W + 0.003, 0.716), (0.719 + W + 0.003, 0.899)]
for x1, x2 in xarr:
    arrow(ax, x1, Y + 0.25, x2, Y + 0.25)
ax.text(0.5, 0.07, "Nota de honestidad metodológica: NO se aplican modificadores IAM ni corrección espectral AM — POA Perez se usa directo como irradiancia efectiva.",
        ha='center', fontsize=10.5, color=C_ORANGE, style='italic')
save(fig, 'flujo_fase2.png')

# ============================================================
# 5) FLUJO FASE 3 — Extracción de parámetros De Soto
# ============================================================
fig, ax = new_fig(12.8, 5.2)
Y, H, W = 0.30, 0.52, 0.205

filebox(ax, 0.010, Y + 0.12, 0.115, 0.28, "Datos_\nFase2_*.csv", edge=C_CYAN)
box(ax, 0.152, Y, W, H, "1 · Coeficientes térmicos",
    ["Ventana 800<G<1200 W/m².", "Isc·(1000/G) y Voc vs Tc →", "regresión lineal (polyfit).", "β_Voc OK; α_Isc sale <0 →", "fallback +0.05 %/°C"], edge=C_CYAN)
box(ax, 0.390, Y, W, H, "2 · Traslación a SRC",
    ["Ventana 900<G<1100 W/m².", "Isc, Voc, Imp, Vmp llevados a", "1000 W/m² y 25 °C con α/β.", "Promedios → Isc_ref, Voc_ref,", "Imp_ref, Vmp_ref"], edge=C_GOLD)
box(ax, 0.628, Y, W, H, "3 · Ajuste no lineal",
    ["scipy.optimize.minimize:", "min Σe² en {Isc, Voc, MPP}", "5 incógnitas + bounds físicos", "(Rs>0, n∈[1,2], Io, Rsh, IL)", "init analítica a₀, Io₀"], edge=C_ORANGE)
filebox(ax, 0.868, Y + 0.12, 0.122, 0.28, "parametros_\ndesoto.json", edge=C_ORANGE)

for x1, x2 in [(0.127, 0.149), (0.152 + W + 0.003, 0.387), (0.390 + W + 0.003, 0.625), (0.628 + W + 0.003, 0.865)]:
    arrow(ax, x1, Y + 0.26, x2, Y + 0.26)
ax.text(0.5, 0.075, "Salida (×2 módulos): IL_ref, Io_ref, a_ref, Rs_ref, Rsh_ref + α_Isc, β_Voc, Ns y puntos de referencia SRC.",
        ha='center', fontsize=10.5, color=C_GREY, style='italic')
save(fig, 'flujo_fase3.png')

# ============================================================
# 6) FLUJO FASE 4 — Simulación anual y PR
# ============================================================
fig, ax = new_fig(12.8, 5.2)
Y, H, W = 0.30, 0.52, 0.158

filebox(ax, 0.010, Y + 0.12, 0.105, 0.28, "JSON +\nDatos_Fase2", edge=C_CYAN)
box(ax, 0.140, Y, W, H, "1 · Escalamiento",
    ["calcparams_desoto:", "IL, Io, a, Rsh dinámicos", "según G y Tc de cada", "registro (Rs constante)"], edge=C_CYAN)
box(ax, 0.327, Y, W, H, "2 · Circuito SDM",
    ["singlediode (Lambert W)", "resuelve la ecuación", "trascendental → Pmp", "de cada registro 5-min"], edge=C_GOLD)
box(ax, 0.514, Y, W, H, "3 · Referencia STC",
    ["Mismo SDM evaluado a", "1000 W/m² y 25 °C →", "P_STC: 50.17 W (m-Si)", "236.72 W (HIT)"], edge=C_GOLD)
box(ax, 0.701, Y, W, H, "4 · Energía y PR",
    ["PR = ΣPmp / Σ(P_STC·G/1000)", "PR mensual (resample ME)", "y PR anual integral", "(IEC 61724-1)"], edge=C_ORANGE)
filebox(ax, 0.884, Y + 0.12, 0.106, 0.28, "Simulacion_*\n_Atacama.csv", edge=C_ORANGE)

for x1, x2 in [(0.117, 0.137), (0.140 + W + 0.003, 0.324), (0.327 + W + 0.003, 0.511),
               (0.514 + W + 0.003, 0.698), (0.701 + W + 0.003, 0.881)]:
    arrow(ax, x1, Y + 0.26, x2, Y + 0.26)
ax.text(0.5, 0.075, "Resultado anual 2026: PR m-Si 84.53 %  |  PR HIT 86.92 %  →  ventaja HIT +2.39 puntos porcentuales.",
        ha='center', fontsize=10.5, color=C_GOLD, style='italic')
save(fig, 'flujo_fase4.png')

# ============================================================
# 7) EMBUDO DE DATOS (conteos reales)
# ============================================================
fig, ax = new_fig(12.8, 6.6)

etapas = [
    ("Base original NREL Cocoa", "11 módulos · ~420,000 curvas I-V · ~1.2 GB", 1.00, C_CYAN),
    ("Selección de tecnologías (Fase 0)", "2 módulos: mSi0166 (36,765 filas) + HIT05667 (38,377 filas) = 75,142", 0.82, C_CYAN),
    ("Emulación Atacama 2026 (Fase 1)", "75,142 filas re-fechadas — sin pérdida de registros", 0.82, C_GOLD),
    ("Limpieza e ingesta (Fase 2)", "Válidas: m-Si 35,669 (97.0 %) + HIT 37,313 (97.2 %) = 72,982", 0.715, C_GOLD),
    ("Ventana térmica 800–1200 W/m² (Fase 3)", "m-Si 8,635 + HIT 9,004 → regresiones α_Isc / β_Voc", 0.58, C_ORANGE),
    ("Ventana SRC 900–1100 W/m² (Fase 3)", "m-Si 5,791 + HIT 6,027 → puntos de referencia STC", 0.46, C_ORANGE),
    ("Simulación anual completa (Fase 4)", "72,982 registros simulados con SDM → PR anual", 0.715, C_GREEN),
]
y = 0.965
maxw = 0.86
for i, (t, sub, frac, col) in enumerate(etapas):
    w = maxw * frac
    x = (1 - w) / 2
    p = FancyBboxPatch((x, y - 0.098), w, 0.098,
                       boxstyle="round,pad=0.008,rounding_size=0.014",
                       linewidth=1.6, edgecolor=col, facecolor=C_PANEL, zorder=2)
    ax.add_patch(p)
    ax.text(0.5, y - 0.028, t, ha='center', va='center', fontsize=11.3,
            color=col, fontweight='bold', zorder=3)
    ax.text(0.5, y - 0.068, sub, ha='center', va='center', fontsize=9.8,
            color=C_WHITE, zorder=3)
    if i < len(etapas) - 1:
        arrow(ax, 0.5, y - 0.106, 0.5, y - 0.132, color=C_GREY, lw=1.6, ms=12)
    y -= 0.138
save(fig, 'embudo_datos.png')

print('Diagramas generados en', OUT)
