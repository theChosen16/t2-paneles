# -*- coding: utf-8 -*-
"""
FASE 6 — Generador de la presentación final ELI556 Tarea 2 (rediseño v2).

Narrativa centrada en el TRATAMIENTO DE DATOS y el FLUJO DE LOS CÓDIGOS:
- Lámina dedicada a la base de datos original NREL Cocoa y a la anatomía del CSV.
- Diagramas de flujo reales por fase (generados por scratch/gen_diagramas_flujo.py).
- Contenido alineado 1:1 con lo que el código ejecuta (sin IAM/AM, albedo 0.25,
  cadencia 5 min, ajuste por minimize+bounds, α_Isc por fallback, etc.).
- Numeración de láminas y referencias cruzadas a anexos calculadas automáticamente.

Salida: output/Presentacion_Final_ELI556_Atacama_POA_Tarea2_revisado.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
import os
import re

# ============================================================
# SISTEMA DE DISEÑO
# ============================================================
DARK_BG = RGBColor(0x0B, 0x0C, 0x10)
PANEL_BG = RGBColor(0x1F, 0x28, 0x33)
PANEL_BG2 = RGBColor(0x27, 0x31, 0x3F)
ACCENT_GOLD = RGBColor(0xF1, 0xC4, 0x0F)
ACCENT_BLUE = RGBColor(0x00, 0xD2, 0xFF)
ACCENT_ORANGE = RGBColor(0xFF, 0x5E, 0x3A)
ACCENT_GREEN = RGBColor(0x2E, 0xCC, 0x71)
TEXT_WHITE = RGBColor(0xFB, 0xFC, 0xFD)
TEXT_GREY = RGBColor(0x9A, 0xA5, 0xB1)
CODE_COLOR = RGBColor(0x7F, 0xDB, 0xFF)

MARGIN = Inches(0.4)
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
GAP = Inches(0.3)
COL_W = (SLIDE_W - 2 * MARGIN - GAP) / 2
CONTENT_Y = Inches(1.30)

IMG = {
    'pipeline':   'output/Extra_Resultados/diagramas/pipeline_general.png',
    'estructura': 'output/Extra_Resultados/diagramas/estructura_csv.png',
    'embudo':     'output/Extra_Resultados/diagramas/embudo_datos.png',
    'f1':         'output/Extra_Resultados/diagramas/flujo_fase1.png',
    'f2':         'output/Extra_Resultados/diagramas/flujo_fase2.png',
    'f3':         'output/Extra_Resultados/diagramas/flujo_fase3.png',
    'f4':         'output/Extra_Resultados/diagramas/flujo_fase4.png',
    'geo':        'output/Extra_Resultados/geo_emulation_map.png',
    'poa_cmp22':  'output/Extra_Resultados/poa_irradiance_cmp22.png',
    'circuito':   'output/Extra_Resultados/circuito_equivalente_sdm.png',
    'curvas_iv':  'output/Extra_Resultados/curvas_iv_pv_src.png',
    'degradacion':'output/Extra_Resultados/degradacion_termica_scatter.png',
    'pr_comp':    'output/Extra_Resultados/pr_mensual_comparativo.png',
    'perfil_dia': 'output/Extra_Resultados/perfil_dia_tipico.png',
    'temp_hist':  'output/Fase1_Resultados/temp_hist_HIT.png',
    'val_scatter':'output/Fase2_Resultados/val_scatter_HIT.png',
}

# ============================================================
# PLAN DE LÁMINAS (orden => numeración y referencias automáticas)
# ============================================================
ORDER = [
    'portada', 'intro', 'justificacion', 'marco',
    'pipeline', 'basedatos', 'basedatos_vars', 'estructura', 'ingesta', 'embudo',
    'emu_concepto', 'emu_comparacion', 'emu_flujo', 'poa_medida', 'poa_notas',
    'f2_flujo', 'f3_flujo', 'f3_result', 'f4_flujo',
    'res_termico', 'validacion', 'rs_n', 'perdidas_pr', 'veredicto', 'economia',
    'limitaciones', 'conclusiones', 'referencias',
    'anexo1', 'anexo2', 'anexo3', 'anexo4', 'anexo5', 'anexo6', 'anexo7', 'anexo8',
]

SECTION = {  # (etiqueta kicker, color de sección)
    'intro': ('INTRODUCCIÓN', ACCENT_BLUE), 'justificacion': ('JUSTIFICACIÓN', ACCENT_BLUE),
    'marco': ('MARCO TEÓRICO', ACCENT_BLUE), 'pipeline': ('PIPELINE', ACCENT_GOLD),
    'basedatos': ('DATOS', ACCENT_GOLD), 'basedatos_vars': ('DATOS', ACCENT_GOLD),
    'estructura': ('DATOS', ACCENT_GOLD), 'ingesta': ('DATOS', ACCENT_GOLD),
    'embudo': ('DATOS', ACCENT_GOLD), 'emu_concepto': ('EMULACIÓN', ACCENT_ORANGE),
    'emu_comparacion': ('EMULACIÓN', ACCENT_ORANGE), 'emu_flujo': ('EMULACIÓN', ACCENT_ORANGE),
    'poa_medida': ('EMULACIÓN', ACCENT_ORANGE), 'poa_notas': ('EMULACIÓN', ACCENT_ORANGE),
    'f2_flujo': ('MODELADO', ACCENT_GOLD),
    'f3_flujo': ('MODELADO', ACCENT_GOLD), 'f3_result': ('MODELADO', ACCENT_GOLD),
    'f4_flujo': ('MODELADO', ACCENT_GOLD), 'res_termico': ('RESULTADOS', ACCENT_GREEN),
    'validacion': ('RESULTADOS', ACCENT_GREEN), 'rs_n': ('RESULTADOS', ACCENT_GREEN),
    'perdidas_pr': ('RESULTADOS', ACCENT_GREEN), 'veredicto': ('RESULTADOS', ACCENT_GREEN),
    'economia': ('RESULTADOS', ACCENT_GREEN), 'limitaciones': ('CIERRE', ACCENT_ORANGE),
    'conclusiones': ('CIERRE', ACCENT_ORANGE), 'referencias': ('CIERRE', ACCENT_ORANGE),
}
REF = {k: i + 1 for i, k in enumerate(ORDER)}
TOTAL = len(ORDER)

def A(key):
    """Referencia textual 'Anexo X, Lám. N' calculada automáticamente."""
    rom = {'anexo1': 'I', 'anexo2': 'II', 'anexo3': 'III', 'anexo4': 'IV',
           'anexo5': 'V', 'anexo6': 'VI', 'anexo7': 'VII', 'anexo8': 'VIII'}
    return f"(Anexo {rom[key]}, Lám. {REF[key]})"

# ============================================================
# HELPERS DE CONSTRUCCIÓN
# ============================================================

def apply_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG


def _emit_subsup(p, text, font_size, color, bold=False):
    """Emite runs procesando [_sub_] y ^sup^ (también dentro de negritas)."""
    for t in re.split(r'(\[_[^_\]]+_\]|\^[^^]+\^)', text):
        if not t:
            continue
        run = p.add_run()
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        if bold:
            run.font.bold = True
        if t.startswith('[_') and t.endswith('_]'):
            run.text = t[2:-2]
            run.font.subscript = True
            run.font.size = Pt(max(8, font_size - 4))
        elif t.startswith('^') and t.endswith('^'):
            run.text = t[1:-1]
            run.font.superscript = True
            run.font.size = Pt(max(8, font_size - 4))
        else:
            run.text = t


def fmt_runs(p, text, font_size, default_color):
    """Mini-markdown seguro: **bold**, `code`, [_sub_], ^sup^ (sin cursivas _)."""
    for tok in re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', text):
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**'):
            _emit_subsup(p, tok[2:-2], font_size, default_color, bold=True)
        elif tok.startswith('`') and tok.endswith('`'):
            run = p.add_run()
            run.text = tok[1:-1]
            run.font.name = 'Consolas'
            run.font.size = Pt(max(8, font_size - 1))
            run.font.color.rgb = CODE_COLOR
        else:
            _emit_subsup(p, tok, font_size, default_color)


def add_par(tf, text, size=14, color=TEXT_WHITE, first=False, align=PP_ALIGN.LEFT,
            space_after=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    fmt_runs(p, text, size, color)
    if space_after is not None:
        p.space_after = Pt(space_after)
    return p


CURRENT_KEY = [None]  # clave de la lámina en construcción (para kicker/sección)


def add_title(slide, text):
    key = CURRENT_KEY[0]
    kick, accent = SECTION.get(key, (None, ACCENT_ORANGE))
    if key and key.startswith('anexo'):
        kick, accent = 'ANEXO', RGBColor(0x8A, 0x96, 0xA8)
    box = slide.shapes.add_textbox(MARGIN, MARGIN - Inches(0.05),
                                   SLIDE_W - 2 * MARGIN - Inches(2.0), Inches(0.85))
    tf = box.text_frame
    tf.word_wrap = True
    p = add_par(tf, text, size=25, color=ACCENT_GOLD, first=True)
    for run in p.runs:
        run.font.bold = True
    if kick:
        chip_w = Inches(1.85)
        chip = slide.shapes.add_shape(1, SLIDE_W - MARGIN - chip_w, MARGIN + Inches(0.06),
                                      chip_w, Inches(0.34))
        chip.fill.solid(); chip.fill.fore_color.rgb = PANEL_BG2
        chip.line.color.rgb = accent; chip.line.width = Pt(1.2)
        ctf = chip.text_frame
        ctf.word_wrap = False
        cp = ctf.paragraphs[0]; cp.alignment = PP_ALIGN.CENTER
        run = cp.add_run(); run.text = kick
        run.font.size = Pt(12); run.font.bold = True; run.font.color.rgb = accent
    line = slide.shapes.add_shape(1, MARGIN, MARGIN + Inches(0.72),
                                  SLIDE_W - 2 * MARGIN, Inches(0.022))
    line.fill.solid()
    line.fill.fore_color.rgb = accent
    line.line.fill.background()


def add_footer(slide, num):
    box = slide.shapes.add_textbox(MARGIN, SLIDE_H - Inches(0.4),
                                   SLIDE_W - 2 * MARGIN, Inches(0.3))
    p = box.text_frame.paragraphs[0]
    p.text = f"ELI556 | Grupo Alta Tensión | Lámina {num}/{TOTAL}"
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(120, 120, 120)
    p.alignment = PP_ALIGN.RIGHT


def add_panel(slide, left, top, width, height, title="", accent=None):
    rect = slide.shapes.add_shape(1, left, top, width, height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = PANEL_BG
    rect.line.color.rgb = accent if accent else ACCENT_BLUE
    rect.line.width = Pt(1.0)
    if accent:
        bar = slide.shapes.add_shape(1, left, top, Inches(0.08), height)
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()
    if title:
        box = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.10),
                                       width - Inches(0.3), Inches(0.45))
        p = add_par(box.text_frame, title, size=18, color=ACCENT_GOLD, first=True)
        for run in p.runs:
            run.font.bold = True
    return rect


def add_text(slide, left, top, width, height, text, size=14, color=TEXT_WHITE,
             align=PP_ALIGN.LEFT, line_space=None):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(text.split('\n')):
        p = add_par(tf, line, size=size, color=color, first=(i == 0), align=align)
        if line_space:
            p.line_spacing = line_space
    return box


def panel_with_body(slide, left, top, width, height, title, body, accent=None,
                    body_size=17, line_space=1.10):
    add_panel(slide, left, top, width, height, title, accent)
    add_text(slide, left + Inches(0.22), top + Inches(0.70),
             width - Inches(0.44), height - Inches(0.88),
             body, size=body_size, line_space=line_space)


def stat_tile(slide, left, top, width, height, value, label, accent=ACCENT_GOLD):
    """Tarjeta de cifra destacada (jerarquía visual: número grande + etiqueta)."""
    rect = slide.shapes.add_shape(1, left, top, width, height)
    rect.fill.solid(); rect.fill.fore_color.rgb = PANEL_BG2
    rect.line.color.rgb = accent; rect.line.width = Pt(1.2)
    add_text(slide, left, top + Inches(0.10), width, Inches(0.72),
             "**" + value + "**", size=38, color=accent, align=PP_ALIGN.CENTER)
    add_text(slide, left + Inches(0.06), top + height - Inches(0.70),
             width - Inches(0.12), Inches(0.62),
             label, size=15.5, color=TEXT_GREY, align=PP_ALIGN.CENTER)


def add_image(slide, path, left, top, width=None, height=None):
    if os.path.exists(path):
        return slide.shapes.add_picture(path, left, top, width=width, height=height)
    # marcador de imagen faltante
    ph = slide.shapes.add_shape(1, left, top, width or Inches(3), height or Inches(2))
    ph.fill.solid(); ph.fill.fore_color.rgb = PANEL_BG2
    add_text(slide, left, top, width or Inches(3), Inches(0.5),
             f"[imagen no encontrada: {path}]", size=10, color=ACCENT_ORANGE)
    return None


def full_width_image(slide, path, max_w=12.5, top_in=1.35, max_bottom=6.95):
    """Inserta imagen centrada a lo ancho respetando el área útil."""
    from PIL import Image as PILImage
    if not os.path.exists(path):
        return add_image(slide, path, Inches(0.5), Inches(top_in))
    w_px, h_px = PILImage.open(path).size
    ar = w_px / h_px
    w = max_w
    h = w / ar
    if top_in + h > max_bottom:
        h = max_bottom - top_in
        w = h * ar
    left = (13.333 - w) / 2
    return slide.shapes.add_picture(path, Inches(left), Inches(top_in),
                                    width=Inches(w), height=Inches(h))


def add_caption(slide, text, top_in, h_in=0.85, accent=ACCENT_GOLD, size=17.5):
    left = MARGIN
    w = SLIDE_W - 2 * MARGIN
    rect = slide.shapes.add_shape(1, left, Inches(top_in), w, Inches(h_in))
    rect.fill.solid(); rect.fill.fore_color.rgb = PANEL_BG
    rect.line.color.rgb = accent; rect.line.width = Pt(1.0)
    # Use zero margin text frame to prevent text overflow at the bottom
    box = slide.shapes.add_textbox(left + Inches(0.2), Inches(top_in + 0.04),
                                   w - Inches(0.4), Inches(h_in - 0.08))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.0)
    tf.margin_right = Inches(0.0)
    tf.margin_top = Inches(0.0)
    tf.margin_bottom = Inches(0.0)
    for i, line in enumerate(text.split('\n')):
        p = add_par(tf, line, size=size, color=TEXT_WHITE, first=(i == 0))
        p.line_spacing = 1.08


def add_table(slide, left, top, width, height, headers, rows, col_ratios=None,
              fs_head=13, fs_body=12):
    n_rows, n_cols = len(rows) + 1, len(headers)
    gframe = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    table = gframe.table
    if col_ratios:
        total = sum(col_ratios)
        for j, r in enumerate(col_ratios):
            table.columns[j].width = Emu(int(width * r / total))
    for j, htxt in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid(); cell.fill.fore_color.rgb = PANEL_BG2
        tf = cell.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        fmt_runs(p, htxt, fs_head, ACCENT_GOLD)
        for run in p.runs:
            run.font.bold = True
        cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.fill.solid(); cell.fill.fore_color.rgb = PANEL_BG if i % 2 == 0 else RGBColor(0x1A, 0x22, 0x2C)
            tf = cell.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            fmt_runs(p, str(val), fs_body, TEXT_WHITE)
            cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
    return table


def add_eq(slide, formula, left, top, height, color='#E8A838', max_width=Inches(5.8)):
    """Renderiza una ecuación con mathtext de matplotlib (transparente)."""
    import matplotlib.pyplot as plt
    from PIL import Image as PILImage
    import hashlib
    tmp = 'output/temp_latex'
    os.makedirs(tmp, exist_ok=True)
    h = hashlib.md5(f"{formula}_{color}".encode()).hexdigest()
    fp = os.path.join(tmp, f"eq_{h}.png")
    if not os.path.exists(fp):
        fig = plt.figure(figsize=(20, 1.8), facecolor='none')
        ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off')
        mt = formula if formula.startswith('$') else f"${formula}$"
        ax.text(0.5, 0.5, mt, fontsize=24, color=color, ha='center', va='center',
                math_fontfamily='cm')
        plt.savefig(fp, dpi=300, bbox_inches='tight', pad_inches=0.05, transparent=True)
        plt.close(fig)
        img = PILImage.open(fp)
        bbox = img.getbbox()
        if bbox:
            img.crop(bbox).save(fp)
    img = PILImage.open(fp)
    ar = img.width / img.height
    w = height * ar
    if w > max_width:
        w = max_width
        height = int(w / ar)
    slide.shapes.add_picture(fp, left, top, width=int(w), height=int(height))


# ============================================================
# CONSTRUCTORES DE LÁMINAS
# ============================================================

def s_portada(slide, n):
    bar = slide.shapes.add_shape(1, 0, 0, Inches(0.18), SLIDE_H)
    bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT_ORANGE; bar.line.fill.background()
    add_text(slide, Inches(0.85), Inches(1.3), Inches(11.6), Inches(1.7),
             "**Evaluación de Tecnologías Fotovoltaicas en el Desierto de Atacama**",
             size=40, color=ACCENT_GOLD)
    add_text(slide, Inches(0.85), Inches(2.62), Inches(11.6), Inches(0.5),
             "Tratamiento de datos experimentales NREL y modelamiento dinámico m-Si vs HIT — Año 2026",
             size=17, color=TEXT_GREY)
    line = slide.shapes.add_shape(1, Inches(0.85), Inches(3.15), Inches(4.5), Inches(0.03))
    line.fill.solid(); line.fill.fore_color.rgb = ACCENT_BLUE; line.line.fill.background()
    panel = slide.shapes.add_shape(1, Inches(0.8), Inches(3.6), Inches(11.7), Inches(2.75))
    panel.fill.solid(); panel.fill.fore_color.rgb = PANEL_BG
    panel.line.color.rgb = ACCENT_BLUE; panel.line.width = Pt(1.5)
    add_text(slide, Inches(1.2), Inches(3.95), Inches(11.0), Inches(2.2),
             "Integrantes / Estudiantes:\n"
             "Laury Gualdron  |  Sebastian Marin  |  Alejandro Hernández\n"
             "\n"
             "Profesor Guía: Carlos Cardenas\n"
             "ELI556 — Modelamiento y Análisis de Sistemas PV  |  Grupo Alta Tensión (AT)\n"
             "Fecha de presentación: Jueves, 11 de junio de 2026", size=15)


def s_intro(slide, n):
    add_title(slide, "a) Introducción y contextualización: El Desierto de Atacama")
    H = Inches(5.45)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "Contexto: El Recurso Solar más Extremo",
        "• **Irradiación excepcional:** GHI anual > 2,900 kWh/m² en el norte de Chile "
        "(máxima a nivel mundial) — motivación del sitio de estudio.\n\n"
        "• **Cielos limpios y altitud:** Baja atenuación atmosférica e irradiancia "
        "directa concentrada a 2,400 m.s.n.m.\n\n"
        "• **Sitio simulado:** San Pedro de Atacama "
        "(lat −22.91°, lon −68.20°, UTC−4).\n\n"
        "• **Base experimental:** mediciones de campo NREL (Cocoa, Florida) "
        "emuladas estacionalmente al hemisferio sur — magnitudes de irradiancia "
        "conservan su origen (ver Limitaciones, Lám. %d)." % REF['limitaciones'],
        accent=ACCENT_BLUE)
    panel_with_body(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
        "El Desafío: Estrés Térmico de Operación",
        "• **Calentamiento severo:** Las celdas operan sobre 65 °C al mediodía "
        "solar de verano (máx. simulado: 73.4 °C en HIT).\n\n"
        "• **Degradación térmica:** La potencia máxima y el voltaje de circuito "
        "abierto caen al aumentar la temperatura de celda (T[_c_]).\n\n"
        "• **Objetivo:** Modelar dinámicamente registro a registro (cadencia "
        "5 min) y cuantificar qué tecnología — **m-Si** o **HIT** — resiste mejor "
        "el estrés térmico desértico durante 2026.\n\n"
        "• **Pregunta guía:** ¿la ventaja térmica de la heterounión justifica su "
        "CAPEX premium en una planta utility-scale?",
        accent=ACCENT_ORANGE)


def s_justificacion(slide, n):
    add_title(slide, "b) Justificación e impacto: Selección de Tecnologías")
    add_panel(slide, MARGIN, CONTENT_Y, SLIDE_W - 2 * MARGIN, Inches(5.5),
              "Familias disponibles en el Dataset Cocoa (NREL) y criterio de selección",
              accent=ACCENT_GOLD)
    headers = ["Tecnología", "Eficiencia", "Coef. Temp. (Pmp)", "Comportamiento en Desierto", "Decisión / Rol"]
    rows = [
        ["m-Si / x-Si\n(Silicio Monocristalino)", "17% - 21%", "−0.40 %/°C (Malo)",
         "Grandes pérdidas por calor (baja tolerancia).", "SELECCIONADO (Línea Base)"],
        ["HIT\n(Heterounión)", "20% - 22%", "−0.26 %/°C (Excelente)",
         "Mantiene alta producción bajo estrés térmico.", "SELECCIONADO (Premium)"],
        ["CdTe\n(Teluro de Cadmio)", "15% - 18%", "−0.28 %/°C (Excelente)",
         "Desempeño térmico sobresaliente; toxicidad por Cadmio.", "DESCARTADO (Menor contraste)"],
        ["CIGS\n(Película Delgada)", "14% - 16%", "−0.35 %/°C (Bueno)",
         "Pérdidas moderadas; susceptible a degradación por humedad.", "DESCARTADO (Sin contraste extremo)"],
        ["a-Si\n(Silicio Amorfo)", "6% - 10%", "−0.20 %/°C (Excelente)",
         "Muy baja eficiencia base y alta degradación inicial.", "DESCARTADO (Inviable comercial)"],
    ]
    add_table(slide, MARGIN + Inches(0.25), CONTENT_Y + Inches(0.62),
              SLIDE_W - 2 * MARGIN - Inches(0.5), Inches(4.1),
              headers, rows, col_ratios=[2.2, 1.0, 1.4, 2.6, 1.9], fs_head=17, fs_body=15.5)
    add_text(slide, MARGIN + Inches(0.25), CONTENT_Y + Inches(4.85),
             SLIDE_W - 2 * MARGIN - Inches(0.5), Inches(0.5),
             "Criterio: máximo contraste térmico entre tecnologías comerciales viables, con datos "
             "experimentales completos en el dataset (`mSi0166` y `HIT05667`).",
             size=15.5, color=TEXT_GREY)


def s_marco(slide, n):
    add_title(slide, "c) Marco referencial y revisión de literatura: Modelos Teóricos")
    H = Inches(5.45)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "Literatura Académica y Modelos APLICADOS",
        "• **Modelo de un Diodo Simple (SDM) [De Soto et al., 2006]:** circuito "
        "equivalente con pérdidas óhmicas en serie (R[_s_]) y fugas shunt (R[_sh_]). "
        f"{A('anexo4')}\n\n"
        "• **Modelo Térmico de Sandia (SAPM) [King et al., 2004]:** estima la "
        f"temperatura interna de celda desde POA y viento. {A('anexo3')}\n\n"
        "• **Transposición de Perez (1990):** lleva GHI/DNI/DHI al plano inclinado "
        f"con cielo difuso anisotrópico. {A('anexo1')}\n\n"
        "• **Escalamiento De Soto (2006):** traslada los 5 parámetros desde STC a "
        f"condiciones operacionales vía bandgap. {A('anexo6')}\n\n"
        "• **Marco revisado NO aplicado:** modificadores ópticos IAM y espectral "
        f"AM [King et al., 2004] — se documentan en {A('anexo2')} y quedan como "
        "trabajo futuro.",
        accent=ACCENT_BLUE, body_size=16.5)
    add_panel(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
              "Circuito Equivalente de un Diodo (SDM)", accent=ACCENT_GOLD)
    add_image(slide, IMG['circuito'],
              MARGIN + COL_W + GAP + Inches(1.05), CONTENT_Y + Inches(0.75),
              width=Inches(4.3), height=Inches(4.3))


def s_pipeline(slide, n):
    add_title(slide, "Procedimiento: Arquitectura del Pipeline de Simulación (Fases 0–7)")
    full_width_image(slide, IMG['pipeline'], max_w=11.5, top_in=1.30, max_bottom=5.70)
    add_caption(slide,
        "**Flujo lógico de la simulación:** El proceso inicia con la exploración y emulación "
        "estacional de los datos (Fases 0-1) para adaptarlos al hemisferio sur. Luego, se limpia y calcula "
        "el recurso solar efectivo (Fase 2) y se extraen los parámetros físicos de los módulos (Fase 3). "
        "Finalmente, se realiza la simulación horaria (Fase 4) para graficar, documentar y exportar los resultados (Fases 5-7).",
        top_in=5.75, h_in=1.30, accent=ACCENT_GOLD)


def s_basedatos(slide, n):
    add_title(slide, "Procedimiento: La Base de Datos Original — NREL Cocoa, Florida")
    TW = (SLIDE_W - 2 * MARGIN - 3 * Inches(0.22)) / 4
    tiles = [("11", "módulos PV medidos\nen simultáneo", ACCENT_BLUE),
             ("5 min", "cadencia de medición\n(solo horas de sol)", ACCENT_GOLD),
             ("~420 mil", "curvas I-V completas\n(ene-2011 → mar-2012)", ACCENT_ORANGE),
             ("~1.2 GB", "en 11 archivos CSV\n(uno por módulo)", ACCENT_GREEN)]
    for i, (v, l, c) in enumerate(tiles):
        stat_tile(slide, MARGIN + i * (TW + Inches(0.22)), CONTENT_Y,
                  TW, Inches(1.45), v, l, accent=c)
    Y2 = CONTENT_Y + Inches(1.70)
    H2 = Inches(3.75)
    panel_with_body(slide, MARGIN, Y2, COL_W, H2,
        "¿Qué es?",
        "• Campaña experimental del **NREL** para validación de modelos PV "
        "[Marion et al., 2014].\n\n"
        "• Sitio: **Cocoa, Florida** (28.39° N, −80.46° W, 12 m.s.n.m.).\n\n"
        "• Tecnologías: 3 m-Si, 1 x-Si, 1 HIT, 1 CdTe, 2 CIGS y 3 a-Si.\n\n"
        "• **Cada registro = una curva I-V completa** + contexto meteorológico "
        "instantáneo + incertidumbres.",
        accent=ACCENT_BLUE)
    panel_with_body(slide, MARGIN + COL_W + GAP, Y2, COL_W, H2,
        "Volumen seleccionado para la tarea",
        "• `mSi0166` — Silicio monocristalino:\n  **36,765 curvas** (~102 MB).\n\n"
        "• `HIT05667` — Heterounión:\n  **38,377 curvas** (~109 MB).\n\n"
        "• Criterio: máximo contraste térmico entre tecnologías viables "
        "(detalle en Lám. %d)." % REF['justificacion'],
        accent=ACCENT_GOLD)


def s_basedatos_vars(slide, n):
    add_title(slide, "Procedimiento: ¿Qué Variables Hay y Con Cuáles Trabajamos?")
    H = Inches(5.45)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "Variables disponibles por registro",
        "• **Eléctricas:** Isc, Pmp, Imp, Vmp, Voc, FF — cada una con su "
        "incertidumbre.\n\n"
        "• **Meteorológicas:** GHI, DNI, DHI, T bulbo seco, humedad relativa, "
        "presión, precipitación.\n\n"
        "• **Referencia POA:** piranómetro CMP22 (clase A) montado en el plano "
        "del arreglo.\n\n"
        "• **Calidad / operación:** residual QA solar, soiling derate, horarios "
        "de mantenimiento.",
        accent=ACCENT_BLUE)
    panel_with_body(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
        "Decisión de uso",
        "• **Usadas (11 columnas):** timestamp, Isc, Pmp, Imp, Vmp, Voc, "
        "T bulbo seco, presión, DNI, GHI, DHI.\n\n"
        "• **Verificación:** POA CMP22 para validar el recurso medido "
        "(Lám. %d).\n\n"
        "• **Descartadas:** cola de pares I-V crudos (ancho variable) y "
        "columnas de QA.\n\n"
        "• Diccionario completo de columnas en %s." % (REF['poa_medida'], A('anexo8')),
        accent=ACCENT_ORANGE)


def s_estructura(slide, n):
    add_title(slide, "Procedimiento: Anatomía del Archivo CSV y Decisiones de Ingesta")
    full_width_image(slide, IMG['estructura'], max_w=12.5, top_in=1.30, max_bottom=5.70)
    add_caption(slide,
        "**Estructura y lectura de datos:** Los archivos originales del NREL contienen una cabecera de metadatos "
        "y registros cada 5 minutos. Dado que cada fila incluye las curvas eléctricas crudas completas, su tamaño "
        "es variable y pesado (~110 MB). Para optimizar la memoria, el código lee el archivo en flujo (streaming) "
        "e indexa únicamente las 11 variables meteorológicas y eléctricas necesarias, descartando el resto al vuelo.",
        top_in=5.75, h_in=1.30, accent=ACCENT_BLUE)


def s_ingesta(slide, n):
    add_title(slide, "Procedimiento: Ingesta y Limpieza de la Base de Datos")
    H = Inches(5.45)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "El Desafío: archivos irregulares de ~110 MB",
        "• **Naturaleza de los datos:** cada fila contiene 43 columnas fijas + "
        "**n pares (I, V) crudos** de la curva trazada (n ≈ 180–380) → filas de "
        "longitud variable.\n\n"
        "• **Falla del método estándar:** `pandas.read_csv` no tolera el ancho "
        "variable (infiere mal el esquema) y carga ~110 MB por módulo a memoria "
        "innecesariamente.\n\n"
        "• **Datos centinela:** los faltantes vienen codificados como **−9999**, "
        "que contaminan promedios y regresiones si no se neutralizan.",
        accent=ACCENT_ORANGE, body_size=17)
    panel_with_body(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
        "La Solución: lector en streaming (Fase 2)",
        "• **Lectura línea a línea** con el módulo `csv` nativo: se indexan solo "
        "las **11 columnas clave por posición fija** y se descarta la cola I-V al "
        "vuelo.\n\n"
        "• **Limpieza:** `-9999 → NaN`, `dropna` sobre GHI/DNI/DHI/T_air y "
        "`clip(≥0)` en irradiancias.\n\n"
        "• **Resultado:** m-Si 35,669/36,765 filas válidas (97.0 %) · HIT "
        "37,313/38,377 (97.2 %).\n\n"
        "• Los registros nocturnos no existen en la base (solo se midió de día); "
        "no se requirió filtro nocturno adicional.",
        accent=ACCENT_BLUE, body_size=17)


def s_embudo(slide, n):
    add_title(slide, "Procedimiento: Embudo de Datos — Trazabilidad por Fase")
    full_width_image(slide, IMG['embudo'], max_w=10.9, top_in=1.32, max_bottom=7.0)


def s_emu_concepto(slide, n):
    add_title(slide, "Procedimiento: Filtro de Emulación Geográfica — Concepto")
    full_width_image(slide, IMG['geo'], max_w=11.6, top_in=1.40, max_bottom=6.55)
    add_text(slide, MARGIN, Inches(6.65), SLIDE_W - 2 * MARGIN, Inches(0.5),
             "¿Por qué? Usar datos del hemisferio norte sin desfasar crearía solsticios "
             "invertidos: el filtro alinea las estaciones antes de simular.",
             size=14, color=TEXT_GREY, align=PP_ALIGN.CENTER)


def s_emu_comparacion(slide, n):
    add_title(slide, "Emulación: Florida (origen de los datos) vs Atacama (sitio simulado)")
    H = Inches(4.35)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "Cocoa, Florida — clima original",
        "• Clima: subtropical húmedo (marítimo), 12 m.s.n.m.\n\n"
        "• Irradiancia difusa alta (~35–45 %) por humedad y nubosidad "
        "convectiva frecuente.\n\n"
        "• DNI máximo ~950 W/m² (atenuado).\n\n"
        "• T[_c_] pico de celda: ~55–60 °C.",
        accent=ACCENT_BLUE)
    panel_with_body(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
        "San Pedro de Atacama — sitio emulado",
        "• Clima: hiperárido (desértico extremo), 2,400 m.s.n.m.\n\n"
        "• Irradiancia difusa muy baja (~10–15 %): cielos permanentemente "
        "limpios.\n\n"
        "• DNI máximo real > 1,250 W/m² (extremo).\n\n"
        "• T[_c_] pico simulada: ~65–73 °C (alto estrés).",
        accent=ACCENT_GOLD)
    add_caption(slide,
        "**Límite explícito del método:** el filtro alinea estaciones, geometría solar e "
        "inclinación óptima (tilt = latitud, azimut 0° N); las **magnitudes medidas** de "
        "irradiancia y clima siguen siendo las de Florida (ver Limitaciones, Lám. %d)." % REF['limitaciones'],
        top_in=5.75, h_in=1.20, accent=ACCENT_ORANGE)


def s_emu_flujo(slide, n):
    add_title(slide, "Procedimiento: Filtro de Emulación — Implementación (Fase 1)")
    full_width_image(slide, IMG['f1'], max_w=12.5, top_in=1.35, max_bottom=5.65)
    add_caption(slide,
        "**Proceso de emulación temporal:** Para trasladar las estaciones de Florida (hemisferio norte) "
        "a San Pedro de Atacama (hemisferio sur), el código modifica la latitud y altura en los metadatos y aplica "
        "un desfase de 6 meses en las fechas. De esta manera, el verano e invierno coinciden con la realidad del sitio "
        "simulado sin alterar los valores físicos medidos. Los solapamientos de fechas se promedian y el año se proyecta a 2026.",
        top_in=5.70, h_in=1.35, accent=ACCENT_ORANGE)


def s_poa_medida(slide, n):
    # Imagen a pantalla completa (16:9) sin título duplicado de slide
    slide.shapes.add_picture(IMG['poa_cmp22'], 0, 0, width=SLIDE_W, height=SLIDE_H)


def s_poa_notas(slide, n):
    add_title(slide, "Procedimiento: Verificación del Recurso — Notas Metodológicas")
    
    # Tarjetas de Cifras Destacadas (Stat Tiles)
    TW = Inches(3.85)
    gap = Inches(0.49)
    stat_tile(slide, MARGIN, CONTENT_Y, TW, Inches(1.50),
              "421,664", "Registros de irradiancia válidos\n(11 archivos Cocoa)", accent=ACCENT_BLUE)
    stat_tile(slide, MARGIN + TW + gap, CONTENT_Y, TW, Inches(1.50),
              "1,443 W/m²", "Irradiancia POA máxima medida\nen el plano del arreglo", accent=ACCENT_GOLD)
    stat_tile(slide, MARGIN + 2 * (TW + gap), CONTENT_Y, TW, Inches(1.50),
              "CMP22", "Piranómetro de referencia\nclase A (alta precisión)", accent=ACCENT_ORANGE)
    
    # Paneles de Notas
    Y2 = CONTENT_Y + Inches(1.75)
    H2 = Inches(3.65)
    panel_with_body(slide, MARGIN, Y2, COL_W, H2,
        "Análisis de Consistencia de Datos",
        "• **Superposición de mediciones:** Las curvas de irradiancia diaria de "
        "los 11 archivos se superponen con exactitud, confirmando la consistencia "
        "del instrumental experimental.\n\n"
        "• **Rango temporal:** Campaña desde el **21 de enero de 2011** hasta el "
        "**4 de marzo de 2012**.\n\n"
        "• **Tratamiento:** Se calcula la mediana diaria suavizada con una ventana "
        "de 7 días por cada archivo para aislar ruidos y nubes transitorias.",
        accent=ACCENT_BLUE, body_size=13.5)
    
    panel_with_body(slide, MARGIN + COL_W + GAP, Y2, COL_W, H2,
        "Propósito del Control de Calidad",
        "• **Validación previa:** El objetivo es validar la homogeneidad física "
        "de la radiación medida **antes** de procesar la emulación geográfica y "
        "el modelado de celdas.\n\n"
        "• **Evidencia de soiling y mantenimiento:** La perfecta coincidencia de "
        "las curvas demuestra que no hay desviaciones locales significativas en "
        "los sensores de referencia.\n\n"
        "• **Alineación de sensores:** Se asegura que la irradiancia incidente en "
        "los 11 planos de módulo sea idéntica para una comparación tecnológica justa.",
        accent=ACCENT_GOLD, body_size=13.5)


def s_f2_flujo(slide, n):
    add_title(slide, "Procedimiento: Recurso Solar Sintético y Perfil Térmico (Fase 2)")
    full_width_image(slide, IMG['f2'], max_w=12.3, top_in=1.35, max_bottom=5.65)
    add_caption(slide,
        "**Estimación de la radiación y temperatura:** Tras filtrar y limpiar los registros nulos, "
        "el código utiliza el modelo difuso de Perez para transponer las irradiancias al plano inclinado (POA). "
        "Luego, con el modelo de Sandia (SAPM) y asumiendo una velocidad de viento fija de 1 m/s (peor caso de ventilación), "
        "se estima la temperatura interna de operación de las celdas para cada tecnología (m-Si y HIT).",
        top_in=5.70, h_in=1.35, accent=ACCENT_ORANGE)


def s_f3_flujo(slide, n):
    add_title(slide, "Procedimiento: Extracción de Parámetros De Soto (Fase 3)")
    full_width_image(slide, IMG['f3'], max_w=12.1, top_in=1.35, max_bottom=5.65)
    add_caption(slide,
        "**Caracterización física de los módulos:** Para modelar el comportamiento eléctrico, se estiman los coeficientes "
        "térmicos de corriente y voltaje. Dado que la corriente arrojó coeficientes negativos debido a la estacionalidad, "
        "se aplicó un valor estándar de resguardo de +0.05 %/°C. Luego, los datos se trasladan a condiciones nominales (STC) "
        "y un optimizador no lineal ajusta los 5 parámetros de De Soto (corrientes, resistencias y factor de idealidad).",
        top_in=5.70, h_in=1.35, accent=ACCENT_GOLD)


def s_f3_result(slide, n):
    add_title(slide, "Procedimiento: Parámetros de Referencia Extraídos en STC")
    W1 = Inches(6.1)
    add_panel(slide, MARGIN, CONTENT_Y, W1, Inches(5.5),
              "Parámetros nominales ajustados (SRC)", accent=ACCENT_GOLD)
    headers = ["Parámetro", "m-Si (mSi0166)", "HIT (HIT05667)"]
    rows = [
        ["I[_L,ref_] (A)", "2.768", "5.607"],
        ["I[_0,ref_] (A)", "4.13 × 10^−9^", "4.68 × 10^−10^"],
        ["R[_s,ref_] (Ω)", "0.542", "0.412"],
        ["R[_sh,ref_] (Ω)", "352.4", "612.8"],
        ["N[_s_] (celdas serie)", "36", "72"],
        ["α[_Isc_] (%/°C)", "+0.05 (resguardo)", "+0.05 (resguardo)"],
        ["β[_Voc_] (%/°C)", "−0.30 (medido)", "−0.21 (medido)"],
        ["I[_sc,ref_] / V[_oc,ref_]", "2.77 A / 22.6 V", "5.61 A / 51.5 V"],
        ["P[_STC_] del SDM (W)", "50.17", "236.72"],
    ]
    add_table(slide, MARGIN + Inches(0.2), CONTENT_Y + Inches(0.62),
              W1 - Inches(0.4), Inches(4.6), headers, rows,
              col_ratios=[1.5, 1.1, 1.1], fs_head=12.5, fs_body=11.5)
    X2 = MARGIN + W1 + Inches(0.25)
    W2 = SLIDE_W - X2 - MARGIN
    add_panel(slide, X2, CONTENT_Y, W2, Inches(3.25),
              "Curvas I-V / P-V reconstruidas en SRC", accent=ACCENT_BLUE)
    add_image(slide, IMG['curvas_iv'], X2 + Inches(0.3), CONTENT_Y + Inches(0.62),
              width=Inches(5.65), height=Inches(2.46))
    panel_with_body(slide, X2, CONTENT_Y + Inches(3.45), W2, Inches(2.05),
        "Lectura física",
        "• I[_0_] de HIT es **un orden de magnitud menor** → menor recombinación "
        "→ mayor V[_oc_] y mejor tolerancia térmica.\n"
        "• R[_sh_] de HIT ~74 % mayor → menos fugas a baja irradiancia.",
        accent=ACCENT_GOLD, body_size=13)


def s_f4_flujo(slide, n):
    add_title(slide, "Procedimiento: Simulación Anual y Performance Ratio (Fase 4)")
    full_width_image(slide, IMG['f4'], max_w=12.1, top_in=1.35, max_bottom=5.65)
    add_caption(slide,
        "**Cálculo de la producción eléctrica anual:** Con los parámetros calibrados, se evalúa el modelo "
        "para cada uno de los registros del año 2026. A partir de la irradiancia y temperatura de celda de cada instante, "
        "se escala el circuito de un diodo y se resuelve analíticamente la potencia útil máxima (Pmp). Finalmente, "
        "la energía anual integrada se compara con el rendimiento ideal para obtener el Performance Ratio (PR).",
        top_in=5.70, h_in=1.35, accent=ACCENT_GOLD)


def s_res_termico(slide, n):
    add_title(slide, "d) Desarrollo y discusión: Recurso Solar y Perfil Térmico")
    add_panel(slide, MARGIN, CONTENT_Y, Inches(6.9), Inches(5.5),
              "Distribución de Temperatura de Celda (HIT)", accent=ACCENT_BLUE)
    add_image(slide, IMG['temp_hist'], MARGIN + Inches(0.55), CONTENT_Y + Inches(0.68),
              width=Inches(5.9), height=Inches(4.41))
    X2 = MARGIN + Inches(7.1)
    W2 = SLIDE_W - X2 - MARGIN
    panel_with_body(slide, X2, CONTENT_Y, W2, Inches(1.55),
        "Picos Térmicos Extremos",
        "**65–73 °C de operación recurrente** al mediodía solar de verano "
        "(HIT: 461 registros sobre 65 °C).",
        accent=ACCENT_ORANGE, body_size=14)
    panel_with_body(slide, X2, CONTENT_Y + Inches(1.75), W2, Inches(3.75),
        "Análisis Crítico de Resultados",
        "• **Estrés térmico evidenciado:** la simulación 5-minutal revela "
        "operación sostenida muy por encima de los 25 °C de STC.\n\n"
        "• **Enfriamiento convectivo limitado:** viento de 1 m/s en SAPM "
        "[King et al., 2004] modela el escenario de mayor estrés físico.\n\n"
        "• **Consecuencia en voltaje [De Soto et al., 2006]:** el calentamiento "
        "eleva I[_0_] exponencialmente, deprimiendo V[_oc_] y la potencia útil.",
        accent=ACCENT_GOLD, body_size=13.5)


def s_validacion(slide, n):
    add_title(slide, "d) Desarrollo y discusión: Validación del Modelo Eléctrico")
    add_panel(slide, MARGIN, CONTENT_Y, Inches(6.9), Inches(5.5),
              "P[_mp_] medida vs simulada (HIT, mismas condiciones)", accent=ACCENT_BLUE)
    add_image(slide, IMG['val_scatter'], MARGIN + Inches(0.55), CONTENT_Y + Inches(0.68),
              width=Inches(5.9), height=Inches(4.41))
    X2 = MARGIN + Inches(7.1)
    W2 = SLIDE_W - X2 - MARGIN
    panel_with_body(slide, X2, CONTENT_Y, W2, Inches(1.55),
        "Precisión del Modelo de 5 Parámetros",
        "**R² ≈ 0.99**  |  RMSE ≈ 3 % de P[_STC_] (1.5 W m-Si · 6.7 W HIT).",
        accent=ACCENT_BLUE, body_size=14)
    panel_with_body(slide, X2, CONTENT_Y + Inches(1.75), W2, Inches(3.75),
        "¿Qué valida exactamente este gráfico?",
        "• **Misma meteorología:** cada punto compara la P[_mp_] **medida** por el "
        "trazador NREL con la **simulada** por el SDM bajo el mismo G y T[_c_] del "
        "instante — no es una comparación entre sitios.\n\n"
        "• **Fidelidad del circuito:** R² ≈ 0.99 confirma que los 5 parámetros "
        "extraídos reproducen el comportamiento eléctrico real en todo el rango.\n\n"
        "• **Zonas de discrepancia:** leve dispersión a baja irradiancia por la "
        "idealización empírica de R[_sh_] ∝ 1/G.",
        accent=ACCENT_GOLD, body_size=13.5)


def s_rs_n(slide, n):
    add_title(slide, "d) Desarrollo: Puntos Conflictivos — Acoplamiento R[_s_] – n")
    H = Inches(5.45)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "Acoplamiento R[_s_] – factor de idealidad (n)",
        "• **Alta correlación paramétrica [De Soto et al., 2006]:** R[_s_] y n "
        "influyen de manera similar en la curvatura de la I-V cerca del MPP.\n\n"
        "• **Problema mal condicionado:** múltiples pares (R[_s_], n) logran un "
        "residuo mínimo casi idéntico, perdiendo significado físico.\n\n"
        "• **Mitigación aplicada:** bounds estrictos en el optimizador — "
        "R[_s_] ∈ [0.001, 2] Ω y n ∈ [1.0, 2.0] — más inicialización analítica. "
        "Esto evita converger a soluciones matemáticamente correctas pero "
        "físicamente imposibles.",
        accent=ACCENT_BLUE, body_size=13.5)
    panel_with_body(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
        "Limitaciones y Suposiciones del Modelo",
        "• **R[_sh_] e irradiancia:** la relación R[_sh_] = R[_sh,ref_]·(S[_ref_]/S) "
        "es empírica; a muy baja irradiancia puede sobreestimar la resistencia. "
        "Impacto: despreciable en el PR anual.\n\n"
        "• **R[_s_] constante con la temperatura:** ignora el cambio de "
        "resistividad del semiconductor con T[_c_]. De Soto (2006) validó errores "
        "de potencia < 2 % frente a datos NIST.\n\n"
        "• **Bandgap lineal con la temperatura:** se asume dE[_g_]/dT constante "
        "(−0.0002677 eV/K), simplificando la relación real de Varshni. Error "
        "inducido < 1 % en el rango operacional (0–70 °C).",
        accent=ACCENT_GOLD, body_size=13.5)


def s_perdidas_pr(slide, n):
    add_title(slide, "d) Desarrollo: Pérdidas Térmicas y Degradación de Potencia")
    add_panel(slide, MARGIN, CONTENT_Y, Inches(7.4), Inches(5.5),
              "Potencia normalizada vs Temperatura de Celda", accent=ACCENT_BLUE)
    add_image(slide, IMG['degradacion'], MARGIN + Inches(0.35), CONTENT_Y + Inches(0.70),
              width=Inches(6.8), height=Inches(4.04))
    X2 = MARGIN + Inches(7.6)
    W2 = SLIDE_W - X2 - MARGIN
    panel_with_body(slide, X2, CONTENT_Y, W2, Inches(1.55),
        "Coeficientes de Temperatura (P[_mp_])",
        "m-Si: **−0.40 %/°C** (pérdidas severas)\nHIT: **−0.26 %/°C** (alta tolerancia)",
        accent=ACCENT_ORANGE, body_size=14)
    panel_with_body(slide, X2, CONTENT_Y + Inches(1.75), W2, Inches(3.75),
        "Observación Científica",
        "• **HIT (naranja):** pendiente térmica suave — preserva alta conversión "
        "incluso a 65 °C.\n\n"
        "• **m-Si (azul):** descenso pronunciado que penaliza la potencia justo "
        "al mediodía solar (máxima irradiancia).\n\n"
        "• **Consecuencia:** esta divergencia térmica explica mecánicamente la "
        "brecha de PR anual entre tecnologías %s." % A('anexo7'),
        accent=ACCENT_GOLD, body_size=13.5)


def s_veredicto(slide, n):
    add_title(slide, "d) Desarrollo y discusión: Veredicto Técnico — Performance Ratio")
    TW = (COL_W - Inches(0.4)) / 2
    stat_tile(slide, MARGIN, CONTENT_Y, TW, Inches(1.5),
              "86.92 %", "PR anual HIT\n(mensual 84.9–89.4 %)", accent=ACCENT_GOLD)
    stat_tile(slide, MARGIN + TW + Inches(0.4), CONTENT_Y, TW, Inches(1.5),
              "84.53 %", "PR anual m-Si\n(mensual 82.0–88.0 %)", accent=ACCENT_BLUE)
    stat_tile(slide, MARGIN, CONTENT_Y + Inches(1.75), COL_W, Inches(1.5),
              "+2.39 puntos", "ventaja neta de HIT en PR anual 2026", accent=ACCENT_GREEN)
    panel_with_body(slide, MARGIN, CONTENT_Y + Inches(3.50), COL_W, Inches(1.95),
        "Lectura técnica",
        "El menor coeficiente térmico de HIT (−0.26 vs −0.40 %/°C) protege la "
        "potencia justo cuando el recurso es máximo: el mediodía desértico.",
        accent=ACCENT_GOLD)
    X2 = MARGIN + COL_W + GAP
    add_panel(slide, X2, CONTENT_Y, COL_W, Inches(5.45),
              "PR mensual comparativo (2026)", accent=ACCENT_BLUE)
    add_image(slide, IMG['pr_comp'], X2 + Inches(0.22), CONTENT_Y + Inches(1.30),
              width=Inches(5.85), height=Inches(2.80))


def s_economia(slide, n):
    add_title(slide, "d) Desarrollo y discusión: Lectura Económica (Planta de 100 MWp)")
    TW = (SLIDE_W - 2 * MARGIN - 2 * Inches(0.3)) / 3
    tiles = [("~6,000 MWh", "energía adicional anual de HIT\n(recurso escalado a Atacama)", ACCENT_GOLD),
             ("+USD 270k", "facturación neta anual extra\n(a 45 USD/MWh)", ACCENT_GREEN),
             ("~3,300 MWh", "escenario conservador con el\nrecurso simulado sin escalar", ACCENT_BLUE)]
    for i, (v, l, c) in enumerate(tiles):
        stat_tile(slide, MARGIN + i * (TW + Inches(0.3)), CONTENT_Y,
                  TW, Inches(1.5), v, l, accent=c)
    Y2 = CONTENT_Y + Inches(1.75)
    H2 = Inches(3.70)
    panel_with_body(slide, MARGIN, Y2, COL_W, H2,
        "Supuestos explícitos del cálculo",
        "• **Recurso escalado:** POA ≈ 2,500 kWh/m²·año en Atacama (el recurso "
        "simulado conserva magnitudes de Florida: 1,363–1,422 kWh/m²·año).\n\n"
        "• ΔPR +2.39 pts → ≈ +60 kWh/kWp·año → **~6,000 MWh** en 100 MWp.\n\n"
        "• Precio de venta ≈ 45 USD/MWh → **~USD 270k/año**.",
        accent=ACCENT_GOLD)
    panel_with_body(slide, MARGIN + COL_W + GAP, Y2, COL_W, H2,
        "Conclusión de diseño",
        "• La prima CAPEX de los módulos HIT se **amortiza con holgura** en "
        "plantas desérticas de alta irradiancia y temperatura.\n\n"
        "• El beneficio crece con el recurso: a mayor POA real, mayor el valor "
        "absoluto de cada punto de PR.\n\n"
        "• Cifras conservadoras: sin escalar el recurso, ~3,300 MWh y "
        "~USD 150k/año siguen favoreciendo a HIT.",
        accent=ACCENT_GREEN)


def s_limitaciones(slide, n):
    add_title(slide, "d) Limitaciones del Estudio y Alcance de Validez")
    H = Inches(5.45)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "Limitaciones de los datos",
        "• **Magnitudes de Florida:** la emulación alinea estaciones y geometría "
        "solar, pero la irradiancia, temperatura y humedad conservan los valores "
        "medidos en Cocoa (POA anual ≈ 1,400 kWh/m² vs ≳2,500 esperables en "
        "Atacama). La comparación m-Si vs HIT es válida; los valores absolutos de "
        "energía son conservadores.\n\n"
        "• **Cobertura temporal:** cadencia 5 min, solo horas de sol; julio–"
        "septiembre 2026 promedian dos veranos (2011 y 2012).\n\n"
        "• **α[_Isc_] de literatura:** la regresión experimental falló (espectro/"
        "estacionalidad) y se usó +0.05 %/°C — impacto menor: la corriente domina "
        "por G, no por T.",
        accent=ACCENT_ORANGE, body_size=16.5)
    panel_with_body(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
        "Limitaciones del modelo",
        "• **Sin pérdidas ópticas/espectrales:** IAM y corrección AM revisados "
        "pero no aplicados " + A('anexo2') + " — su omisión sobreestima levemente "
        "la energía en ángulos rasantes (amanecer/ocaso).\n\n"
        "• **Albedo fijo 0.25** (default pvlib) y **viento fijo 1 m/s** — "
        "escenario térmico conservador.\n\n"
        "• **P[_STC_] del SDM** (50.2 / 236.7 W) difiere ~7–9 % del promedio "
        "empírico medido (46.7 / 217.5 W): el denominador del PR usa el primero, "
        "criterio consistente entre ambas tecnologías.\n\n"
        "• **Sin soiling ni mismatch:** pérdidas de planta real no modeladas — el "
        "PR aquí es un PR de módulo, no de planta.",
        accent=ACCENT_BLUE, body_size=16.5)


def s_conclusiones(slide, n):
    add_title(slide, "e) Conclusiones y propuestas de trabajos futuros")
    H = Inches(5.45)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H,
        "Conclusiones del Estudio",
        "1. **Fidelidad metodológica:** la emulación geográfica por traslación "
        "temporal (+6 meses, año 2026) mantuvo coherencia física de solsticios y "
        "permitió simular Atacama con datos experimentales reales.\n\n"
        "2. **Pipeline de datos robusto:** la ingesta en streaming resolvió "
        "archivos irregulares de ~110 MB conservando el 97 % de los registros.\n\n"
        "3. **Ajuste robusto:** el SDM de 5 parámetros reprodujo la potencia "
        "medida con R² ≈ 0.99 y RMSE ≈ 3 % de P[_STC_].\n\n"
        "4. **HIT vencedor:** +2.39 puntos de PR anual (86.92 % vs 84.53 %) por "
        "su menor coeficiente térmico — técnicamente superior para plantas "
        "desérticas de alta irradiancia y temperatura.",
        accent=ACCENT_GOLD, body_size=16.5)
    panel_with_body(slide, MARGIN + COL_W + GAP, CONTENT_Y, COL_W, H,
        "Propuestas de Trabajos Futuros",
        "• **Aplicar IAM y corrección espectral AM** ya documentados %s, "
        "cerrando la brecha óptica del pipeline actual.\n\n"
        "• **Escalar el recurso a magnitudes de Atacama** (TMY local o "
        "Explorador Solar) manteniendo la validación eléctrica con datos NREL.\n\n"
        "• **Bifacialidad:** aporte del albedo desértico (ρ > 0.25) en la cara "
        "posterior.\n\n"
        "• **Soiling desértico:** acumulación de polvo, factor crítico de "
        "pérdida en Atacama.\n\n"
        "• **Modelo de doble diodo:** capturar recombinación no ideal a baja "
        "irradiancia." % A('anexo2'),
        accent=ACCENT_BLUE, body_size=16.5)


def s_referencias(slide, n):
    add_title(slide, "Referencias")
    panel_with_body(slide, MARGIN, CONTENT_Y, SLIDE_W - 2 * MARGIN, Inches(5.5),
        "Referencias Bibliográficas Estructuradas",
        '1. De Soto, W., Klein, S.A., Beckman, W.A. (2006). "Improvement and '
        'validation of a model for photovoltaic array performance." Solar Energy '
        '80, 78–88.\n\n'
        '2. King, D.L., Boyson, W.E., Kratochvil, J.A. (2004). "Photovoltaic '
        'Array Performance Model." Sandia Report SAND2004-3535.\n\n'
        '3. Marion, B. et al. (2014). "New Data Set for Validating PV Module '
        'Performance Models." NREL/CP-5J00-61610 — origen del dataset Cocoa.\n\n'
        '4. Perez, R. et al. (1990). "Modeling daylight availability and '
        'irradiance components from direct and global irradiance." Solar Energy '
        '44(5), 271–289.\n\n'
        '5. Holmgren, W.F., Hansen, C.W., Mikofski, M.A. (2018). "pvlib python: '
        'a python package for modeling solar energy systems." JOSS 3(29), 884.\n\n'
        '6. IEC 61724-1 — Photovoltaic system performance, Part 1: Monitoring.\n\n'
        'Agradecimientos al Departamento de Electrotecnia de la UTFSM.',
        accent=ACCENT_ORANGE, body_size=17.5)


def s_anexo1(slide, n):
    add_title(slide, "Anexo I: Transposición de Irradiancia al Plano del Arreglo (Perez)")
    H = Inches(5.45)
    add_panel(slide, MARGIN, CONTENT_Y, COL_W, H,
              "Forma general de transposición POA", accent=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(0.62), COL_W - Inches(0.44), Inches(0.5),
             "Irradiancia incidente total en el plano inclinado del panel:", size=16)
    add_eq(slide,
           r"G_{poa}=G_b\,R_{beam}+G_{d,perez}+G\,\rho\,\left(\frac{1-\cos(\beta)}{2}\right)",
           MARGIN + Inches(0.35), CONTENT_Y + Inches(1.25), Inches(0.62), max_width=Inches(5.7))
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(2.3), COL_W - Inches(0.44), Inches(2.9),
             "Donde:\n"
             "• G[_b_] / G[_d_] / G: irradiancia directa, difusa y global (W/m²).\n"
             "• β: inclinación del panel = 22.91° (latitud del sitio).\n"
             "• ρ: albedo = 0.25 (default `pvlib`, suelo genérico).\n"
             "• R[_beam_]: factor geométrico de transposición directa.\n"
             "• G[_d,perez_]: difusa anisotrópica de Perez (circumsolar +\n"
             "  brillo de horizonte), evaluada por `pvlib.get_total_irradiance`.",
             size=16.5, color=ACCENT_GOLD, line_space=1.15)
    X2 = MARGIN + COL_W + GAP
    panel_with_body(slide, X2, CONTENT_Y, COL_W, H,
        "Implementación en el código (Fase 2)",
        "• `location.get_solarposition(times)` → cenit y azimut aparentes del "
        "sol minuto de medición a medición.\n\n"
        "• `irradiance.get_extra_radiation(times)` → irradiancia extraterrestre "
        "para el modelo anisotrópico.\n\n"
        "• `irradiance.get_total_irradiance(tilt, az, dni, ghi, dhi, ..., "
        "model='perez')` → componente directa + difusa Perez + reflejada.\n\n"
        "• Salida: `poa_global` con `clip(≥0)`, usada como irradiancia efectiva "
        "del SDM (sin modificadores ópticos — ver Anexo II).",
        accent=ACCENT_GOLD, body_size=16.5)


def s_anexo2(slide, n):
    add_title(slide, "Anexo II: Marco NO Aplicado — Modificadores Ópticos (IAM y AM)")
    H = Inches(4.6)
    add_panel(slide, MARGIN, CONTENT_Y, COL_W, H,
              "Modificador por Ángulo de Incidencia (IAM)", accent=ACCENT_BLUE)
    add_eq(slide, r"K_{\tau\alpha}(\theta)=\frac{\tau(\theta)}{\tau(0)}",
           MARGIN + Inches(0.35), CONTENT_Y + Inches(0.75), Inches(0.55), max_width=Inches(5.5))
    add_eq(slide,
           r"\tau(\theta)=e^{-\frac{KL}{\cos(\theta_r)}}\left[1-\frac{1}{2}\left(\frac{\sin^2(\theta_r-\theta)}{\sin^2(\theta_r+\theta)}+\frac{\tan^2(\theta_r-\theta)}{\tan^2(\theta_r+\theta)}\right)\right]",
           MARGIN + Inches(0.35), CONTENT_Y + Inches(1.55), Inches(0.75), max_width=Inches(5.6))
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(2.7), COL_W - Inches(0.44), Inches(1.7),
             "Ley de Snell y Bouguer [King et al., 2004]: θ[_r_] = arcsin(sin θ / n), con "
             "n = 1.526 (vidrio), K = 4 m⁻¹, L = 2 mm.",
             size=16.5, color=ACCENT_GOLD, line_space=1.15)
    X2 = MARGIN + COL_W + GAP
    add_panel(slide, X2, CONTENT_Y, COL_W, H,
              "Modificador Espectral por Masa de Aire (AM)", accent=ACCENT_GOLD)
    add_eq(slide,
           r"\frac{M}{M_{ref}}=a_0+a_1 AM+a_2 AM^2+a_3 AM^3+a_4 AM^4",
           X2 + Inches(0.35), CONTENT_Y + Inches(0.8), Inches(0.55), max_width=Inches(5.6))
    add_eq(slide,
           r"AM=\frac{1}{\cos(\theta_z)+0.5057\,(96.08-\theta_z)^{-1.634}}",
           X2 + Inches(0.35), CONTENT_Y + Inches(1.6), Inches(0.65), max_width=Inches(5.6))
    add_text(slide, X2 + Inches(0.22), CONTENT_Y + Inches(2.7), COL_W - Inches(0.44), Inches(1.7),
             "Corrige el desajuste espectral según la atmósfera atravesada; a[_0_]…a[_4_] son "
             "coeficientes empíricos de cada celda [King et al., 2004].",
             size=16.5, color=ACCENT_GOLD, line_space=1.15)
    add_caption(slide,
        "**Estado en este estudio:** ecuaciones revisadas en la literatura pero **no ejecutadas por el "
        "pipeline** (la POA de Perez ingresa directa al SDM). Su incorporación es la primera propuesta de "
        "trabajo futuro — la omisión sobreestima levemente la energía en ángulos de incidencia rasantes.",
        top_in=5.95, h_in=1.10, accent=ACCENT_ORANGE)


def s_anexo3(slide, n):
    add_title(slide, "Anexo III: Ecuaciones del Perfil Térmico (Modelo Sandia SAPM)")
    add_panel(slide, MARGIN, CONTENT_Y, SLIDE_W - 2 * MARGIN, Inches(1.95),
              "Ecuación de Sandia para Temperatura de Celda", accent=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(0.58),
             SLIDE_W - 2 * MARGIN - Inches(0.5), Inches(0.4),
             "La temperatura de la celda se modela a partir del equilibrio térmico dinámico:", size=16)
    add_eq(slide,
           r"T_c = G_{poa}\cdot e^{a+b\,v_w} + T_a + \left(\frac{G_{poa}}{1000}\right)\Delta T",
           Inches(4.0), CONTENT_Y + Inches(1.05), Inches(0.7), max_width=Inches(6.0))
    Y2 = CONTENT_Y + Inches(2.15)
    H2 = Inches(3.3)
    panel_with_body(slide, MARGIN, Y2, COL_W, H2,
        "Glosario de Variables",
        "• T[_c_] / T[_a_]: temperatura de celda y ambiente (°C).\n"
        "• G[_poa_]: irradiancia total en el plano del panel (W/m²).\n"
        "• v[_w_]: velocidad de viento (fijada en 1 m/s).\n"
        "• a, b, ΔT: parámetros empíricos del encapsulado/montaje.",
        accent=ACCENT_BLUE, body_size=16.5)
    panel_with_body(slide, MARGIN + COL_W + GAP, Y2, COL_W, H2,
        "Coeficientes Empíricos Utilizados",
        "• m-Si — `open_rack_glass_polymer`: a = −3.56 · b = −0.075 · ΔT = 3.0 °C\n\n"
        "• HIT — `open_rack_glass_glass`: a = −3.47 · b = −0.059 · ΔT = 3.0 °C\n\n"
        "**Fuente:** `pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']` — "
        "base interna validada por Sandia NL [King et al., 2004].",
        accent=ACCENT_GOLD, body_size=16.5)


def s_anexo4(slide, n):
    add_title(slide, "Anexo IV: Ecuaciones del Modelo Eléctrico de un Diodo (SDM)")
    add_panel(slide, MARGIN, CONTENT_Y, SLIDE_W - 2 * MARGIN, Inches(1.95),
               "Ecuación Trascendental del Circuito Equivalente", accent=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(0.58),
              SLIDE_W - 2 * MARGIN - Inches(0.5), Inches(0.4),
              "Corriente implícita del modelo de diodo simple con resistencias parásitas "
              "(resuelta con la función W de Lambert en `pvlib.singlediode`):", size=16)
    add_eq(slide,
            r"I = I_L - I_0\left[\exp\left(\frac{V+I R_s}{a}\right)-1\right]-\frac{V+I R_s}{R_{sh}}",
            Inches(3.8), CONTENT_Y + Inches(1.1), Inches(0.62), max_width=Inches(6.2))
    Y2 = CONTENT_Y + Inches(2.15)
    H2 = Inches(3.3)
    add_panel(slide, MARGIN, Y2, COL_W, H2,
               "Factor de Idealidad Térmico (a)", accent=ACCENT_GOLD)
    add_eq(slide, r"a=\frac{N_s\,n_I\,k\,T_c}{q}",
            MARGIN + Inches(0.45), Y2 + Inches(0.75), Inches(0.62), max_width=Inches(3.2))
    add_text(slide, MARGIN + Inches(0.22), Y2 + Inches(1.7), COL_W - Inches(0.44), Inches(1.4),
              "• N[_s_]: celdas en serie (m-Si: 36, HIT: 72).\n"
              "• n[_I_]: factor de idealidad del diodo, acotado a [1, 2].",
              size=16.5, color=ACCENT_GOLD, line_space=1.15)
    panel_with_body(slide, MARGIN + COL_W + GAP, Y2, COL_W, H2,
        "Glosario de Parámetros Físicos",
        "• I / V: corriente y voltaje de salida (A, V).\n"
        "• I[_L_]: corriente fotogenerada (A).\n"
        "• I[_0_]: corriente de saturación inversa de la unión P-N (A).\n"
        "• R[_s_] / R[_sh_]: resistencias parásitas serie y shunt (Ω).\n"
        "• k / q / T[_c_]: constante de Boltzmann, carga elemental y "
        "temperatura de celda (K).",
        accent=ACCENT_BLUE, body_size=16.5)


def s_anexo5(slide, n):
    add_title(slide, "Anexo V: Extracción en STC — Ajuste Numérico Real")
    H = Inches(5.45)
    add_panel(slide, MARGIN, CONTENT_Y, COL_W, H,
              "Normalización de mediciones a SRC", accent=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(0.6), COL_W - Inches(0.44), Inches(0.7),
             "Cada punto en la ventana 900–1100 W/m² se traslada a 1000 W/m² y 25 °C:",
             size=15.5)
    add_eq(slide, r"I_{sc}^{SRC}=I_{sc}\,\frac{1000}{G}+\alpha_{Isc}\,(25-T_c)",
           MARGIN + Inches(0.4), CONTENT_Y + Inches(1.3), Inches(0.55), max_width=Inches(5.4))
    add_eq(slide, r"V_{oc}^{SRC}=V_{oc}+\beta_{Voc}\,(25-T_c)",
           MARGIN + Inches(0.4), CONTENT_Y + Inches(2.05), Inches(0.55), max_width=Inches(5.4))
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(2.85), COL_W - Inches(0.44), Inches(2.3),
             "• β[_Voc_] (medido): regresión lineal V[_oc_] vs T[_c_] (ventana 800–1200 W/m²).\n"
             "• α[_Isc_] (literatura): la regresión resultó negativa → resguardo físico "
             "+0.05 %/°C de literatura.\n"
             "• Promedios de la ventana → I[_sc,ref_], V[_oc,ref_], I[_mp,ref_], "
             "V[_mp,ref_].",
             size=15.5, color=ACCENT_GOLD, line_space=1.2)
    X2 = MARGIN + COL_W + GAP
    add_panel(slide, X2, CONTENT_Y, COL_W, H,
              "Ajuste de los 5 parámetros (lo que ejecuta el código)", accent=ACCENT_GOLD)
    add_text(slide, X2 + Inches(0.22), CONTENT_Y + Inches(0.6), COL_W - Inches(0.44), Inches(0.65),
             "`scipy.optimize.minimize` sobre el residuo cuadrático de las 3 condiciones "
             "del SDM en SRC:", size=15.5)
    add_eq(slide, r"\min_{I_L,I_0,a,R_s,R_{sh}}\;e_{V_{oc}}^2+e_{I_{sc}}^2+e_{MPP}^2",
           X2 + Inches(0.45), CONTENT_Y + Inches(1.35), Inches(0.6), max_width=Inches(5.2))
    add_text(slide, X2 + Inches(0.22), CONTENT_Y + Inches(2.25), COL_W - Inches(0.44), Inches(2.9),
             "• e[_Voc_]: corriente nula en circuito abierto.\n"
             "• e[_Isc_]: corriente de cortocircuito reproducida.\n"
             "• e[_MPP_]: corriente correcta en (V[_mp_], I[_mp_]).\n\n"
             "**Regularización física (bounds):** R[_s_] ∈ [0.001, 2] Ω · "
             "R[_sh_] ∈ [100, 10⁴] Ω · n[_I_] ∈ [1, 2] · I[_L_] ± 10 % · "
             "I[_0_] ∈ [10⁻¹², 10⁻⁵] A.\n"
             "**Inicialización analítica:** a₀ = N[_s_]·1.2·kT/q; "
             "I[_0,0_] = I[_sc_]·exp(−V[_oc_]/a₀).\n"
             "Sistema de 3 ecuaciones y 5 incógnitas: la unicidad la aportan los "
             "bounds + inicialización, no una derivada analítica.",
             size=15, color=ACCENT_GOLD, line_space=1.18)


def s_anexo6(slide, n):
    add_title(slide, "Anexo VI: Escalamiento a Condiciones de Operación (De Soto)")
    H = Inches(5.45)
    add_panel(slide, MARGIN, CONTENT_Y, COL_W, H,
              "Corrientes y Factor de Idealidad", accent=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(0.72), COL_W - Inches(0.44), Inches(0.35),
             "1. Corriente fotogenerada (I[_L_]):", size=15.5)
    add_eq(slide, r"I_L=\frac{S}{S_{ref}}\left[I_{L,ref}+\alpha_{Isc}(T_c-T_{ref})\right]",
           MARGIN + Inches(0.4), CONTENT_Y + Inches(1.10), Inches(0.55), max_width=Inches(5.3))
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(1.85), COL_W - Inches(0.44), Inches(0.35),
             "2. Corriente de saturación inversa (I[_0_]):", size=15.5)
    add_eq(slide,
           r"\frac{I_0}{I_{0,ref}}=\left(\frac{T_c}{T_{ref}}\right)^3\exp\left[\frac{E_{g,ref}}{k\,T_{ref}}-\frac{E_g}{k\,T_c}\right]",
           MARGIN + Inches(0.4), CONTENT_Y + Inches(2.28), Inches(0.65), max_width=Inches(5.3))
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(3.15), COL_W - Inches(0.44), Inches(0.35),
             "3. Factor de idealidad térmico (a):", size=15.5)
    add_eq(slide, r"\frac{a}{a_{ref}}=\frac{T_c}{T_{ref}}",
           MARGIN + Inches(0.4), CONTENT_Y + Inches(3.60), Inches(0.55), max_width=Inches(3.0))
    X2 = MARGIN + COL_W + GAP
    add_panel(slide, X2, CONTENT_Y, COL_W, H,
              "Resistencias y Energía de Bandgap", accent=ACCENT_GOLD)
    add_text(slide, X2 + Inches(0.22), CONTENT_Y + Inches(0.72), COL_W - Inches(0.44), Inches(0.35),
             "4. Resistencia shunt (R[_sh_]):", size=15.5)
    add_eq(slide, r"R_{sh}=R_{sh,ref}\left(\frac{S_{ref}}{S}\right)",
           X2 + Inches(0.4), CONTENT_Y + Inches(1.10), Inches(0.6), max_width=Inches(4.0))
    add_text(slide, X2 + Inches(0.22), CONTENT_Y + Inches(1.90), COL_W - Inches(0.44), Inches(0.35),
             "5. Energía de bandgap del Silicio (E[_g_]):", size=15.5)
    add_eq(slide, r"\frac{E_g}{E_{g,ref}}=1-0.0002677\,(T_c-T_{ref})",
           X2 + Inches(0.4), CONTENT_Y + Inches(2.30), Inches(0.55), max_width=Inches(4.8))
    add_text(slide, X2 + Inches(0.22), CONTENT_Y + Inches(3.15), COL_W - Inches(0.44), Inches(2.2),
             "Suposiciones físicas justificadas:\n"
             "• R[_s_] constante: R[_s_] = R[_s,ref_] (validación NIST < 2 %).\n"
             "• R[_sh_] ∝ 1/S: empírica, dominante a baja irradiancia.\n"
             "• E[_g,ref_] = 1.121 eV para Silicio a 25 °C.\n"
             "• S = G[_poa_] (sin corrección espectral — Anexo II).\n"
             "Implementado por `pvlib.pvsystem.calcparams_desoto`.",
             size=15.5, color=ACCENT_GOLD, line_space=1.2)


def s_anexo7(slide, n):
    add_title(slide, "Anexo VII: Ecuaciones para el Cálculo del Performance Ratio")
    add_panel(slide, MARGIN, CONTENT_Y, SLIDE_W - 2 * MARGIN, Inches(1.95),
              "Ecuación de Rendimiento Global del PR (IEC 61724-1)", accent=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.22), CONTENT_Y + Inches(0.72),
             SLIDE_W - 2 * MARGIN - Inches(0.5), Inches(0.4),
             "Eficiencia neta del sistema frente a su comportamiento ideal en condiciones estándar:",
             size=16)
    add_eq(slide,
           r"PR=\sum_{t=1}^{N} P_{mp,t}(G_t,T_{c,t})\;/\;\sum_{t=1}^{N} P_{STC}\cdot\frac{G_{poa,t}}{G_{ref}}",
           Inches(3.9), CONTENT_Y + Inches(1.05), Inches(0.78), max_width=Inches(6.0))
    Y2 = CONTENT_Y + Inches(2.15)
    H2 = Inches(3.3)
    panel_with_body(slide, MARGIN, Y2, COL_W, H2,
        "Glosario de Variables",
        "• P[_mp,t_]: potencia MPP del SDM en el registro t (cadencia 5 min).\n"
        "• P[_STC_]: potencia nominal del **mismo SDM** evaluado a 1000 W/m² y "
        "25 °C — m-Si: 50.17 W · HIT: 236.72 W (criterio consistente).\n"
        "• G[_poa,t_]: irradiancia instantánea en el plano del panel (W/m²).\n"
        "• G[_ref_]: irradiancia de referencia STC (1000 W/m²).",
        accent=ACCENT_GOLD, body_size=16.5)
    panel_with_body(slide, MARGIN + COL_W + GAP, Y2, COL_W, H2,
        "Pérdidas penalizadas por el PR",
        "• **Térmicas:** caídas por elevada T[_c_] — dominantes en Atacama.\n"
        "• **Óhmicas:** pérdidas resistivas en R[_s_].\n"
        "• **De bajo G:** comportamiento no lineal a baja irradiancia (R[_sh_]).\n"
        "• NO penaliza pérdidas ópticas/espectrales (no modeladas) ni de "
        "planta (cableado, inversor, soiling).",
        accent=ACCENT_BLUE, body_size=16.5)


def s_anexo8(slide, n):
    add_title(slide, "Anexo VIII: Diccionario de Columnas del Dataset NREL Cocoa")
    H1 = Inches(2.58)
    panel_with_body(slide, MARGIN, CONTENT_Y, COL_W, H1,
        "Identificación y tiempo",
        "• `Time Stamp` (hora local estándar, paso 5 min) — col. 0.\n"
        "• Metadatos (líneas 1–2): módulo, ciudad, estado, zona horaria, "
        "latitud, longitud, altitud, tilt, azimut.",
        accent=ACCENT_BLUE, body_size=16.5)
    panel_with_body(slide, MARGIN, CONTENT_Y + H1 + Inches(0.25), COL_W, H1,
        "Eléctricas (usadas → índices fijos)",
        "• `Isc` (5), `Pmp` (7), `Imp` (9), `Vmp` (11), `Voc` (13) — cada una "
        "con su columna de incertidumbre (%).\n"
        "• `FF` (15) y cola de n pares (I, V) crudos — descartadas en la ingesta.",
        accent=ACCENT_GREEN, body_size=16.5)
    X2 = MARGIN + COL_W + GAP
    panel_with_body(slide, X2, CONTENT_Y, COL_W, H1,
        "Meteorológicas (usadas → índices fijos)",
        "• `Dry bulb temperature` (20), `Atmospheric pressure` (24).\n"
        "• `DNI` (27), `GHI` (30), `DHI` (33) — c/u con incertidumbre y "
        "desviación estándar de muestras de 1 s.\n"
        "• `POA CMP22` (1): referencia para verificación del recurso.",
        accent=ACCENT_GREEN, body_size=16.5)
    panel_with_body(slide, X2, CONTENT_Y + H1 + Inches(0.25), COL_W, H1,
        "Calidad y operación (no usadas)",
        "• `Solar QA residual`: cierre Direct·cos(z) + Difusa − Global.\n"
        "• `PV module soiling derate`, lluvia acumulada, humedad relativa, "
        "T dorso del módulo, T gabinete MT5, horarios de mantenimiento "
        "(`99:99` = sin mantención) y n.º de pares I-V.",
        accent=ACCENT_ORANGE, body_size=16.5)


BUILDERS = {
    'portada': s_portada, 'intro': s_intro, 'justificacion': s_justificacion,
    'marco': s_marco, 'pipeline': s_pipeline, 'basedatos': s_basedatos,
    'basedatos_vars': s_basedatos_vars, 'estructura': s_estructura,
    'ingesta': s_ingesta, 'embudo': s_embudo,
    'emu_concepto': s_emu_concepto, 'emu_comparacion': s_emu_comparacion,
    'emu_flujo': s_emu_flujo,
    'poa_medida': s_poa_medida, 'poa_notas': s_poa_notas, 'f2_flujo': s_f2_flujo, 'f3_flujo': s_f3_flujo,
    'f3_result': s_f3_result, 'f4_flujo': s_f4_flujo,
    'res_termico': s_res_termico, 'validacion': s_validacion, 'rs_n': s_rs_n,
    'perdidas_pr': s_perdidas_pr, 'veredicto': s_veredicto, 'economia': s_economia,
    'limitaciones': s_limitaciones, 'conclusiones': s_conclusiones,
    'referencias': s_referencias, 'anexo1': s_anexo1, 'anexo2': s_anexo2,
    'anexo3': s_anexo3, 'anexo4': s_anexo4, 'anexo5': s_anexo5,
    'anexo6': s_anexo6, 'anexo7': s_anexo7, 'anexo8': s_anexo8,
}


def create_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]
    for key in ORDER:
        CURRENT_KEY[0] = key
        slide = prs.slides.add_slide(blank)
        apply_bg(slide)
        BUILDERS[key](slide, REF[key])
        add_footer(slide, REF[key])
        print(f"  [{REF[key]:>2}/{TOTAL}] {key}")
    out = 'output/Presentacion_Final_ELI556_Atacama_POA_Tarea2_revisado.pptx'
    try:
        prs.save(out)
    except PermissionError:
        out = out.replace('.pptx', '_v2.pptx')
        prs.save(out)
    print(f"\nPresentación guardada en: {out}")


if __name__ == '__main__':
    create_presentation()
