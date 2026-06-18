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
        fs_title=14.5, fs_body=12, lw=2.0, linespacing=1.65):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.012,rounding_size=0.018",
                 linewidth=lw, edgecolor=edge, facecolor=fc, zorder=2))
    ax.text(x+w/2, y+h-0.045, title, ha='center', va='top', fontsize=fs_title,
            color=C_GOLD, fontweight='bold', zorder=3)
    if lines:
        ax.text(x+w/2, y+(h-0.10)/2.0, '\n'.join(lines), ha='center', va='center',
                fontsize=fs_body, color=C_WHITE, zorder=3, linespacing=linespacing)


def filebox(ax, x, y, w, h, label, edge=C_ORANGE, fs=13.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0.010,rounding_size=0.012", linewidth=1.8,
                 edgecolor=edge, facecolor='#161B22', linestyle=(0, (4, 2)), zorder=2))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center', fontsize=fs,
            color=edge, zorder=3, linespacing=1.45, family='monospace')


def arrow(ax, x1, y1, x2, y2, color=C_GOLD, lw=2.4, ms=17):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                 mutation_scale=ms, linewidth=lw, color=color, zorder=4))


def new_fig(w=12.8, h=5.6):
    fig = plt.figure(figsize=(w, h), facecolor='none')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.015, 1.015); ax.set_ylim(-0.015, 1.015); ax.axis('off')
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, transparent=True)
    plt.close(fig)
    print('OK ->', name)


# ---------- 1) PIPELINE GENERAL ----------
fig, ax = new_fig(22.0, 6.4)
BW, BH = 0.168, 0.34
Y1, Y2 = 0.58, 0.08
xs = [0.02 + i * 0.198 for i in range(5)]

# Row 1: Files and Phases (Left to Right)
filebox(ax, xs[0], Y1, BW, BH, "Base datos original\n11 CSV NREL\n(~1.2 GB)", edge=C_ORANGE, fs=14.5)
box(ax, xs[1], Y1, BW, BH, "FASE 0 · Exploración", ["fase0_setup.py", "Inspección bases pvlib.", "Selección: mSi/HIT"], edge=C_ORANGE, fs_title=18.0, fs_body=14.0, lw=3.2)
box(ax, xs[2], Y1, BW, BH, "FASE 1 · Emulación", ["fase1_filtro_emulacion.py", "Metadatos + desfase 6m", "y proyección al 2026"], edge=C_ORANGE, fs_title=18.0, fs_body=14.0, lw=3.2)
filebox(ax, xs[3], Y1, BW, BH, "data/Atacama_2026\n2 CSV emulados", edge=C_ORANGE, fs=14.5)
box(ax, xs[4], Y1, BW, BH, "FASE 2 · Recurso Solar", ["fase2_recurso_solar.py", "POA Perez + IAM + espectral", "y Tc (SAPM)"], edge=C_CYAN, fs_title=18.0, fs_body=14.0, lw=2.0)

# Row 2: Files and Phases (Right to Left)
filebox(ax, xs[4], Y2, BW, BH, "Datos_Fase2_{mod}.csv\n(POA + Tc limpios)", edge=C_CYAN, fs=14.5)
box(ax, xs[3], Y2, BW, BH, "FASE 3 · Parámetros", ["fase3_extraccion_parametros.py", "Regresiones α/β y ajuste", "De Soto (minimize+bounds)"], edge=C_CYAN, fs_title=18.0, fs_body=14.0, lw=2.0)
filebox(ax, xs[2], Y2, BW, BH, "parametros_\ndesoto.json", edge=C_GOLD, fs=14.5)
box(ax, xs[1], Y2, BW, BH, "FASE 4 · Simulación", ["fase4_simulacion_final.py", "SDM vía Lambert W.", "Energía anual y PR"], edge=C_GOLD, fs_title=18.0, fs_body=14.0, lw=2.0)
filebox(ax, xs[0], Y2, BW, BH, "Simulacion_{mod}\n_Atacama.csv", edge=C_GOLD, fs=14.5)

# Connectors:
# Row 1 Rightward arrows:
for i in range(4):
    arrow(ax, xs[i]+BW+0.003, Y1+BH/2, xs[i+1]-0.004, Y1+BH/2, color=C_GOLD, lw=2.4, ms=16)

# Downward arrow from FASE 2 to File 2:
arrow(ax, xs[4]+BW/2, Y1-0.006, xs[4]+BW/2, Y2+BH+0.008, color=C_GOLD, lw=2.4, ms=16)

# Row 2 Leftward arrows:
for i in range(4, 0, -1):
    arrow(ax, xs[i]-0.004, Y2+BH/2, xs[i-1]+BW+0.003, Y2+BH/2, color=C_GOLD, lw=2.4, ms=16)

save(fig, 'pipeline_general.png')

# ---------- 2) ESTRUCTURA DEL CSV ----------
fig, ax = new_fig(18.2, 6.4)
box(ax, 0.012, 0.012, 0.315, 0.928, "Cocoa_mSi0166.csv  (~102 MB)", [],
    edge=C_CYAN, fs_title=20.0)
rows = [
    ("Líneas 1-2 · METADATOS", ["módulo, ciudad, TZ, lat, lon,", "altitud, tilt, azimut"], C_GOLD),
    ("Línea 3 · ENCABEZADO", ["43 columnas fijas con", "nombre y unidad"], C_GOLD),
    ("Líneas 4+ · REGISTROS", ["1 fila = 1 curva I-V cada 5 min", "(solo de día)", "Total registros: 36,765 filas"], C_ORANGE),
    ("Cola variable de fila", ["n pares (I,V) crudos (≈180–380)", "→ ancho de fila VARIABLE"], C_ORANGE),
]
yy = 0.755
for t, b, e in rows:
    box(ax, 0.028, yy-0.125, 0.283, 0.175, t, b, edge=e,
        fc=C_PANEL2, fs_title=14.5, fs_body=11.2, lw=1.6)
    yy -= 0.20
grupos = [
    ("Eléctricas (usadas)", ["Isc, Pmp, Imp, Vmp, Voc, FF", "e incertidumbres"], C_GREEN, 0.755),
    ("Meteorológicas (usadas)", ["GHI, DNI, DHI,", "T bulbo seco y presión"], C_GREEN, 0.525),
    ("POA CMP22 (verificación)", ["Piranómetro clase A en", "el plano del arreglo"], C_CYAN, 0.295),
    ("No usadas", ["T dorso, humedad, lluvia,", "soiling, QA, mantención"], C_GREY, 0.065),
]
for t, b, e, y in grupos:
    box(ax, 0.40, y, 0.27, 0.18, t, b, edge=e, fs_title=15.0, fs_body=12.0)
    arrow(ax, 0.33, 0.42, 0.397, y+0.09, color=C_GREY, lw=1.5, ms=12)
box(ax, 0.74, 0.525, 0.248, 0.41, "Decisión de ingesta",
    ["Lector streaming (csv) que indexa", "solo 11 columnas por posición fija", "y descarta la cola I-V al vuelo."],
    edge=C_GOLD, fs_title=17.0, fs_body=13.5)
box(ax, 0.74, 0.065, 0.248, 0.41, "Limpieza aplicada",
    ["Reemplazo de -9999 → NaN,", "dropna, clip(≥0) en irradiancias.", "Válidos: 95.8% (m-Si) y 96.1% (HIT)."],
    edge=C_ORANGE, fs_title=17.0, fs_body=13.5)
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
    ["Fuerza año = 2026", "29-feb → 28-feb", "ventana 12 meses única"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
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
box(ax, 0.541, Y, W, H, "3 · POA + óptica",
    ["Perez (albedo 0.20) +", "IAM físico + espectral", "→ irradiancia efectiva"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.734, Y, W, H, "4 · Tc (SAPM)",
    ["sapm_cell, coeficientes", "open_rack: glass_polymer", "(m-Si) / glass_glass (HIT)"], edge=C_ORANGE, fs_title=13.5, fs_body=11.8)
filebox(ax, 0.922, Y+0.12, 0.07, 0.30, "Datos_\nFase2_*", edge=C_ORANGE)
for x1, x2 in [(0.128, 0.152), (0.323, 0.345), (0.516, 0.538), (0.709, 0.731), (0.902, 0.919)]:
    arrow(ax, x1, Y+0.27, x2, Y+0.27)
ax.text(0.5, 0.07, "Irradiancia efectiva = POA Perez × IAM físico × factor espectral — entra al SDM (≈3 % de pérdida óptica).",
        ha='center', fontsize=13, color=C_GOLD, style='italic')
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
    ["calcparams_desoto:", "IL con G efectiva", "(IAM+espectral) y Tc", "(Rs constante)"], edge=C_CYAN, fs_title=13.5, fs_body=11.8)
box(ax, 0.333, Y, W, H, "2 · Circuito SDM",
    ["singlediode resuelve", "la ec. trascendental", "(Lambert W) → Pmp", "por registro 5-min"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.526, Y, W, H, "3 · Referencia STC",
    ["Mismo SDM evaluado", "a 1000 W/m², 25 °C →", "P_STC 50.1 W (m-Si)", "238.0 W (HIT)"], edge=C_GOLD, fs_title=13.5, fs_body=11.8)
box(ax, 0.719, Y, W, H, "4 · Energía y PR",
    ["PR = ΣPmp / ΣP_ideal", "PR mensual + anual", "integral", "(IEC 61724-1)"], edge=C_ORANGE, fs_title=13.5, fs_body=11.8)
filebox(ax, 0.908, 0.40, 0.084, 0.30, "Simulacion\n_*.csv", edge=C_ORANGE)
for x1, x2 in [(0.115, 0.137), (0.308, 0.330), (0.501, 0.523), (0.694, 0.716), (0.887, 0.905)]:
    arrow(ax, x1, 0.55, x2, 0.55)
ax.text(0.5, 0.07, "Resultado 2026:  PR m-Si 81.61 %   |   PR HIT 84.18 %   →   ventaja HIT +2.57 puntos.",
        ha='center', fontsize=13.5, color=C_GOLD, style='italic')
save(fig, 'flujo_fase4.png')

# ---------- 7) EMBUDO ----------
fig, ax = new_fig(12.8, 6.6)
etapas = [
    ("Base original NREL Cocoa", "11 módulos · ~420,000 curvas I-V · ~1.2 GB", 1.00, C_CYAN),
    ("Selección de tecnologías (Fase 0)", "mSi0166 (36,765) + HIT05667 (38,377) = 75,142 filas", 0.84, C_CYAN),
    ("Emulación + ventana 12 meses (Fase 1)", "m-Si 32,961 + HIT 34,169 = 67,130 (sin doble cobertura)", 0.78, C_GOLD),
    ("Limpieza e ingesta (Fase 2)", "m-Si 31,578 (95.8 %) + HIT 32,844 (96.1 %) = 64,422", 0.70, C_GOLD),
    ("Ventana térmica 800–1200 W/m² (Fase 3)", "7,749 + 8,079 → regresiones α_Isc / β_Voc", 0.60, C_ORANGE),
    ("Ventana SRC 900–1100 W/m² (Fase 3)", "5,149 + 5,389 → puntos de referencia STC", 0.50, C_ORANGE),
    ("Simulación anual completa (Fase 4)", "64,422 registros simulados con SDM → PR anual", 0.70, C_GREEN),
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

# ---------- 8) INGESTA Y LIMPIEZA ----------
fig, ax = new_fig(22.0, 5.6)
BW, BH, Y = 0.22, 0.74, 0.13
xs = [0.02 + i * 0.245 for i in range(4)]

box(ax, xs[0], Y, BW, BH, "1 · Dataset Crudo NREL",
    ["Archivo Cocoa: ~110 MB", "43 col fijas + cola I-V", "Longitud de fila variable", "Sentinelas con -9999"],
    edge=C_CYAN, fs_title=24.0, fs_body=20.0, linespacing=1.85)

box(ax, xs[1], Y, BW, BH, "2 · Ingesta por Streaming",
    ["Módulo csv nativo", "Lectura línea a línea", "Descarta cola I-V al vuelo", "Uso de memoria < 1 MB"],
    edge=C_GOLD, fs_title=24.0, fs_body=20.0, linespacing=1.85)

box(ax, xs[2], Y, BW, BH, "3 · Limpieza y QA",
    ["Reemplazo -9999 → NaN", "dropna() sobre variables", "clave (GHI, DNI, DHI, T)", "clip(≥0) en irradiancias"],
    edge=C_ORANGE, fs_title=24.0, fs_body=20.0, linespacing=1.85)

box(ax, xs[3], Y, BW, BH, "4 · Dataset Final",
    ["Tras ventana 12 meses:", "m-Si: 95.8% (31,578/32,961)", "HIT: 96.1% (32,844/34,169)", "Sin doble cobertura"],
    edge=C_GREEN, fs_title=24.0, fs_body=20.0, linespacing=1.85)

for i in range(3):
    arrow(ax, xs[i]+BW+0.002, Y+BH/2, xs[i+1]-0.004, Y+BH/2, color=C_GOLD, lw=2.4, ms=14)

save(fig, 'ingesta_limpieza.png')

print('Diagramas v2 generados en', OUT)
