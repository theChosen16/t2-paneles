# -*- coding: utf-8 -*-
"""Diagramas de flujo v2 — tipografía grande y sin solapamientos.
Salida: output/Extra_Resultados/diagramas/*.png"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

C_PANEL, C_PANEL2 = '#1F2833', '#27313F'
C_GOLD, C_CYAN, C_ORANGE = '#F1C40F', '#00D2FF', '#FF5E3A'
C_WHITE, C_GREY, C_GREEN = '#FBFCFD', '#9AA5B1', '#2ECC71'
OUT = 'output/Extra_Resultados/diagramas'
os.makedirs(OUT, exist_ok=True)
plt.rcParams['font.family'] = 'DejaVu Sans'


def box(ax, x, y, w, h, title, lines, edge=C_CYAN, fc=C_PANEL,
        fs_title=14.5, fs_body=12, lw=2.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.012,rounding_size=0.018",
                 linewidth=lw, edgecolor=edge, facecolor=fc, zorder=2))
    ax.text(x+w/2, y+h-0.045, title, ha='center', va='top', fontsize=fs_title,
            color=C_GOLD, fontweight='bold', zorder=3)
    if lines:
        ax.text(x+w/2, y+(h-0.13)/2.0, '\n'.join(lines), ha='center', va='center',
                fontsize=fs_body, color=C_WHITE, zorder=3, linespacing=1.4)


def filebox(ax, x, y, w, h, label, edge=C_ORANGE, fs=11.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.010,rounding_size=0.012", linewidth=1.8,
                 edgecolor=edge, facecolor='#161B22', linestyle=(0, (4, 2)), zorder=2))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=fs,
            color=edge, zorder=3, linespacing=1.35, family='monospace')


def arrow(ax, x1, y1, x2, y2, color=C_GOLD, lw=2.4, ms=17):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                 mutation_scale=ms, linewidth=lw, color=color, zorder=4))


def new_fig(w=12.8, h=5.6):
    fig = plt.figure(figsize=(w, h), facecolor='none')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, transparent=True)
    plt.close(fig)
    print('OK ->', name)


# ---------- 1) PIPELINE GENERAL ----------
fig, ax = new_fig(12.8, 6.4)
ROW1, ROW2, BH, BW = 0.615, 0.09, 0.315, 0.225
xs = [0.008, 0.262, 0.516, 0.770]
r1 = [
    ("FASE 0 · Exploración", ["fase0_setup.py", "Inspección bases pvlib.", "Selección: mSi0166 / HIT05667"]),
    ("FASE 1 · Emulación", ["fase1_filtro_emulacion.py", "Metadatos + desfase 6 meses", "y proyección al año 2026"]),
    ("FASE 2 · Recurso Solar", ["fase2_recurso_solar.py", "Streaming + limpieza.", "POA (Perez) y Tc (SAPM)"]),
    ("FASE 3 · Parámetros", ["fase3_extraccion_parametros.py", "Regresiones α/β y ajuste", "De Soto (minimize + bounds)"]),
]
r2 = [
    ("FASE 7 · Export", ["fase7_export_slides.py", "Exporta láminas a PNG", "para QA visual (COM)"]),
    ("FASE 6 · Deck", ["fase6_gen_presentation.py", "Genera esta presentación", "con python-pptx"]),
    ("FASE 5 · Gráficos", ["fase5_gen_extra_plots.py", "I-V/P-V en SRC, día típico,", "PR comparativo, térmica"]),
    ("FASE 4 · Simulación", ["fase4_simulacion_final.py", "SDM vía Lambert W.", "Energía anual y PR"]),
]
for (t, l), x in zip(r1, xs):
    box(ax, x, ROW1, BW, BH, t, l, edge=C_CYAN, fs_title=13.5, fs_body=11)
for (t, l), x in zip(r2, xs):
    box(ax, x, ROW2, BW, BH, t, l, edge=C_GOLD, fs_title=13.5, fs_body=11)
for i in range(3):
    arrow(ax, xs[i]+BW+0.004, ROW1+BH/2, xs[i+1]-0.006, ROW1+BH/2)
arrow(ax, xs[3]+BW/2, ROW1-0.012, xs[3]+BW/2, ROW2+BH+0.065)
for i in range(3, 0, -1):
    arrow(ax, xs[i]-0.006, ROW2+BH/2, xs[i-1]+BW+0.004, ROW2+BH/2)
art = [
    (xs[0]+BW+0.125, ROW1+BH+0.045, "Base datos original/\n11 CSV NREL (~1.2 GB)"),
    (xs[1]+BW+0.125, ROW1+BH+0.045, "data/Atacama_2026/\n2 CSV emulados"),
    (xs[2]+BW+0.125, ROW1+BH+0.045, "Datos_Fase2_{mod}.csv\n(POA + Tc limpios)"),
    (xs[3]+BW/2-0.125, (ROW1+ROW2+BH)/2, "parametros_\ndesoto.json"),
    (xs[2]+BW+0.125, ROW2-0.055, "Simulacion_{mod}\n_Atacama.csv"),
    (xs[1]+BW+0.125, ROW2-0.055, "Extra_Resultados/*.png"),
    (xs[0]+BW+0.125, ROW2-0.055, "output/*.pptx"),
]
for x, y, t in art:
    ax.text(x, y, t, ha='center', va='center', fontsize=10, color=C_GREY,
            family='monospace', linespacing=1.3)
save(fig, 'pipeline_general.png')

# ---------- 2) ESTRUCTURA DEL CSV ----------
fig, ax = new_fig(12.8, 6.4)
box(ax, 0.012, 0.06, 0.315, 0.88, "Cocoa_mSi0166.csv  (~102 MB)", [],
    edge=C_CYAN, fs_title=14)
rows = [
    ("Líneas 1-2 · METADATOS", "módulo, ciudad, TZ, lat,\nlon, altitud, tilt, azimut", C_GOLD),
    ("Línea 3 · ENCABEZADO", "43 columnas fijas, con\nnombre y unidad", C_GOLD),
    ("Líneas 4+ · REGISTROS", "1 fila = 1 curva I-V cada 5 min\n(solo de día) · 36,765 filas", C_ORANGE),
    ("Cola variable de fila", "n pares (I,V) crudos (≈180–380)\n→ ancho de fila VARIABLE", C_ORANGE),
]
yy = 0.755
for t, b, e in rows:
    box(ax, 0.028, yy-0.125, 0.283, 0.175, t, b.split('\n'), edge=e,
        fc=C_PANEL2, fs_title=12, fs_body=10.8, lw=1.6)
    yy -= 0.20
grupos = [
    ("Eléctricas (usadas)", ["Isc, Pmp, Imp, Vmp, Voc", "+ FF e incertidumbres"], C_GREEN, 0.755),
    ("Meteorológicas (usadas)", ["GHI, DNI, DHI, T bulbo", "seco, presión"], C_GREEN, 0.525),
    ("POA CMP22 (verificación)", ["Piranómetro clase A en", "el plano del arreglo"], C_CYAN, 0.295),
    ("No usadas", ["T dorso, humedad, lluvia,", "soiling, QA, mantenimiento"], C_GREY, 0.065),
]
for t, b, e, y in grupos:
    box(ax, 0.40, y, 0.27, 0.18, t, b, edge=e, fs_title=12.5, fs_body=11.5)
    arrow(ax, 0.33, 0.42, 0.397, y+0.09, color=C_GREY, lw=1.5, ms=12)
box(ax, 0.74, 0.525, 0.248, 0.41, "Decisión de ingesta",
    ["Lector streaming (csv):", "indexa SOLO 11 columnas", "por posición fija y descarta", "la cola I-V al vuelo."],
    edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.74, 0.065, 0.248, 0.41, "Limpieza aplicada",
    ["-9999 → NaN · dropna", "clip(≥0) en irradiancias", "Válidos: 97.0 % (m-Si)", "y 97.2 % (HIT)"],
    edge=C_ORANGE, fs_title=13.5, fs_body=11.8)
arrow(ax, 0.672, 0.62, 0.737, 0.70, color=C_GOLD, lw=2, ms=14)
arrow(ax, 0.672, 0.38, 0.737, 0.29, color=C_ORANGE, lw=2, ms=14)
save(fig, 'estructura_csv.png')

# ---------- 3) FASE 1 ----------
fig, ax = new_fig(12.8, 4.6)
Y, H, W = 0.24, 0.54, 0.178
filebox(ax, 0.010, Y+0.12, 0.135, 0.30, "Cocoa_*.csv\n(Florida)", edge=C_CYAN)
box(ax, 0.173, Y, W, H, "1 · Metadatos",
    ["Reescribe el sitio:", "lat −22.91°, lon −68.20°,", "2400 m, tilt 22.9°, az 0°"], edge=C_CYAN, fs_title=13.5, fs_body=11.8)
box(ax, 0.385, Y, W, H, "2 · Desfase +6 meses",
    ["relativedelta(months=6)", "invierno ⇄ verano:", "solsticios alineados"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.597, Y, W, H, "3 · Proyección 2026",
    ["Fuerza año = 2026", "29-feb → 28-feb", "jul–sep: 2 veranos"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
filebox(ax, 0.818, Y+0.12, 0.165, 0.30, "Atacama2026_*.csv", edge=C_ORANGE)
for x1, x2 in [(0.147, 0.170), (0.354, 0.382), (0.566, 0.594), (0.778, 0.815)]:
    arrow(ax, x1, Y+0.27, x2, Y+0.27)
ax.text(0.5, 0.055, "Streaming línea a línea: solo cambian timestamp y cabecera — las mediciones no se alteran.",
        ha='center', fontsize=13, color=C_GREY, style='italic')
save(fig, 'flujo_fase1.png')

# ---------- 4) FASE 2 ----------
fig, ax = new_fig(12.8, 4.9)
Y, H, W = 0.28, 0.55, 0.165
filebox(ax, 0.008, Y+0.12, 0.118, 0.30, "Atacama2026\n_*.csv", edge=C_CYAN)
box(ax, 0.155, Y, W, H, "1 · Ingesta",
    ["csv.reader fila a fila;", "11 columnas por índice;", "descarta cola I-V"], edge=C_CYAN, fs_title=13.5, fs_body=11.8)
box(ax, 0.348, Y, W, H, "2 · Limpieza",
    ["-9999 → NaN, dropna,", "clip(≥0) irradiancias,", "viento fijo = 1 m/s"], edge=C_CYAN, fs_title=13.5, fs_body=11.8)
box(ax, 0.541, Y, W, H, "3 · POA (Perez)",
    ["get_solarposition +", "get_total_irradiance", "(albedo default 0.25)"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.734, Y, W, H, "4 · Tc (SAPM)",
    ["sapm_cell, coeficientes", "open_rack: glass_polymer", "(m-Si) / glass_glass (HIT)"], edge=C_ORANGE, fs_title=13.5, fs_body=11.8)
filebox(ax, 0.922, Y+0.12, 0.07, 0.30, "Datos_\nFase2_*", edge=C_ORANGE)
for x1, x2 in [(0.128, 0.152), (0.323, 0.345), (0.516, 0.538), (0.709, 0.731), (0.902, 0.919)]:
    arrow(ax, x1, Y+0.27, x2, Y+0.27)
ax.text(0.5, 0.07, "Honestidad metodológica: SIN modificadores IAM ni corrección espectral AM — POA Perez entra directa al SDM.",
        ha='center', fontsize=13, color=C_ORANGE, style='italic')
save(fig, 'flujo_fase2.png')

# ---------- 5) FASE 3 ----------
fig, ax = new_fig(12.8, 5.2)
Y, H, W = 0.27, 0.57, 0.21
filebox(ax, 0.008, 0.40, 0.115, 0.30, "Datos_\nFase2_*.csv", edge=C_CYAN)
box(ax, 0.152, Y, W, H, "1 · Coef. térmicos",
    ["Ventana 800–1200 W/m².", "Regresión Isc·(1000/G) y", "Voc vs Tc. β ok; α sale <0", "→ resguardo +0.05 %/°C"], edge=C_CYAN, fs_title=13.5, fs_body=11.5)
box(ax, 0.392, Y, W, H, "2 · Traslación a SRC",
    ["Ventana 900–1100 W/m².", "Isc, Voc, Imp, Vmp llevados", "a 1000 W/m² y 25 °C.", "Promedios → puntos _ref"], edge=C_GOLD, fs_title=13.5, fs_body=11.5)
box(ax, 0.632, Y, W, H, "3 · Ajuste no lineal",
    ["minimize: min Σe² en", "{Isc, Voc, MPP} — 5 incóg.", "+ bounds físicos (Rs>0,", "n∈[1,2]) + init analítica"], edge=C_ORANGE, fs_title=13.5, fs_body=11.5)
filebox(ax, 0.872, 0.40, 0.118, 0.30, "parametros_\ndesoto.json", edge=C_ORANGE)
for x1, x2 in [(0.125, 0.149), (0.365, 0.389), (0.605, 0.629), (0.845, 0.869)]:
    arrow(ax, x1, 0.55, x2, 0.55)
ax.text(0.5, 0.07, "Salida ×2 módulos: IL_ref, Io_ref, a_ref, Rs_ref, Rsh_ref + α_Isc, β_Voc, Ns y referencia SRC.",
        ha='center', fontsize=13, color=C_GREY, style='italic')
save(fig, 'flujo_fase3.png')

# ---------- 6) FASE 4 ----------
fig, ax = new_fig(12.8, 5.2)
Y, H, W = 0.27, 0.57, 0.165
filebox(ax, 0.008, 0.40, 0.105, 0.30, "JSON +\nDatos_Fase2", edge=C_CYAN)
box(ax, 0.140, Y, W, H, "1 · Escalamiento",
    ["calcparams_desoto:", "IL, Io, a, Rsh según", "G y Tc del registro", "(Rs constante)"], edge=C_CYAN, fs_title=13.5, fs_body=11.8)
box(ax, 0.333, Y, W, H, "2 · Circuito SDM",
    ["singlediode resuelve", "la ec. trascendental", "(Lambert W) → Pmp", "por registro 5-min"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.526, Y, W, H, "3 · Referencia STC",
    ["Mismo SDM evaluado", "a 1000 W/m², 25 °C →", "P_STC 50.2 W (m-Si)", "236.7 W (HIT)"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.719, Y, W, H, "4 · Energía y PR",
    ["PR = ΣPmp / ΣP_ideal", "PR mensual + anual", "integral", "(IEC 61724-1)"], edge=C_ORANGE, fs_title=13.5, fs_body=11.8)
filebox(ax, 0.908, 0.40, 0.084, 0.30, "Simulacion\n_*.csv", edge=C_ORANGE)
for x1, x2 in [(0.115, 0.137), (0.308, 0.330), (0.501, 0.523), (0.694, 0.716), (0.887, 0.905)]:
    arrow(ax, x1, 0.55, x2, 0.55)
ax.text(0.5, 0.07, "Resultado 2026:  PR m-Si 84.53 %   |   PR HIT 86.92 %   →   ventaja HIT +2.39 puntos.",
        ha='center', fontsize=13.5, color=C_GOLD, style='italic')
save(fig, 'flujo_fase4.png')

# ---------- 7) EMBUDO ----------
fig, ax = new_fig(12.8, 6.6)
etapas = [
    ("Base original NREL Cocoa", "11 módulos · ~420,000 curvas I-V · ~1.2 GB", 1.00, C_CYAN),
    ("Selección de tecnologías (Fase 0)", "mSi0166 (36,765) + HIT05667 (38,377) = 75,142 filas", 0.84, C_CYAN),
    ("Emulación Atacama 2026 (Fase 1)", "75,142 filas re-fechadas — sin pérdida de registros", 0.84, C_GOLD),
    ("Limpieza e ingesta (Fase 2)", "m-Si 35,669 (97.0 %) + HIT 37,313 (97.2 %) = 72,982", 0.74, C_GOLD),
    ("Ventana térmica 800–1200 W/m² (Fase 3)", "8,635 + 9,004 → regresiones α_Isc / β_Voc", 0.62, C_ORANGE),
    ("Ventana SRC 900–1100 W/m² (Fase 3)", "5,791 + 6,027 → puntos de referencia STC", 0.52, C_ORANGE),
    ("Simulación anual completa (Fase 4)", "72,982 registros simulados con SDM → PR anual", 0.74, C_GREEN),
]
y = 0.965
for i, (t, sub, frac, col) in enumerate(etapas):
    w = 0.88*frac; x = (1-w)/2
    ax.add_patch(FancyBboxPatch((x, y-0.098), w, 0.098,
                 boxstyle="round,pad=0.008,rounding_size=0.014",
                 linewidth=2, edgecolor=col, facecolor=C_PANEL, zorder=2))
    ax.text(0.5, y-0.027, t, ha='center', va='center', fontsize=13,
            color=col, fontweight='bold', zorder=3)
    ax.text(0.5, y-0.069, sub, ha='center', va='center', fontsize=11.5,
            color=C_WHITE, zorder=3)
    if i < len(etapas)-1:
        arrow(ax, 0.5, y-0.106, 0.5, y-0.132, color=C_GREY, lw=1.8, ms=13)
    y -= 0.138
save(fig, 'embudo_datos.png')

print('Diagramas v2 generados en', OUT)
