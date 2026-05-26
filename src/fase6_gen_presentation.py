from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
from pptx.oxml.ns import qn
import os

# --- Configuración del Sistema de Diseño ---
DARK_BG = RGBColor(0x0B, 0x0C, 0x10)     # Fondo ultra profundo
PANEL_BG = RGBColor(0x1F, 0x28, 0x33)    # Gris oscuro con toque azulado
ACCENT_GOLD = RGBColor(0xF1, 0xC4, 0x0F)  # Oro solar vibrante
ACCENT_BLUE = RGBColor(0x00, 0xD2, 0xFF)  # Cyan eléctrico
ACCENT_ORANGE = RGBColor(0xFF, 0x5E, 0x3A)# Naranja solar
TEXT_WHITE = RGBColor(0xFB, 0xFC, 0xFD)   # Blanco roto para alta legibilidad

MARGIN = Inches(0.4)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)
GAP = Inches(0.3)
COLUMN_WIDTH = (SLIDE_WIDTH - 2 * MARGIN - GAP) / 2

def apply_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG

def add_title(slide, text):
    title_box = slide.shapes.add_textbox(MARGIN, MARGIN, SLIDE_WIDTH - 2*MARGIN, Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    add_formatted_paragraph(tf, text, font_size=24, default_color=ACCENT_GOLD, is_first=True)
    p = tf.paragraphs[0]
    for run in p.runs:
        run.font.bold = True
        
    # Añadir línea horizontal decorativa fina debajo del título
    line = slide.shapes.add_shape(1, MARGIN, MARGIN + Inches(0.72), SLIDE_WIDTH - 2*MARGIN, Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_ORANGE
    line.line.fill.background() # Sin bordes
    
    return title_box

def add_footer(slide, page_num, total_pages=25):
    footer_text = f"ELI556 | Grupo Alta Tensión | Lámina {page_num}/{total_pages}"
    footer_box = slide.shapes.add_textbox(MARGIN, SLIDE_HEIGHT - Inches(0.4), SLIDE_WIDTH - 2*MARGIN, Inches(0.3))
    p = footer_box.text_frame.paragraphs[0]
    p.text = footer_text
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(120, 120, 120)
    p.alignment = PP_ALIGN.RIGHT

def add_panel(slide, left, top, width, height, title="", accent_color=None):
    rect = slide.shapes.add_shape(1, left, top, width, height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = PANEL_BG
    border_color = accent_color if accent_color else ACCENT_BLUE
    rect.line.color.rgb = border_color
    rect.line.width = Pt(1.0)
    
    if accent_color:
        # Añadir barra de acento delgada a la izquierda del panel
        bar = slide.shapes.add_shape(1, left, top, Inches(0.08), height)
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_color
        bar.line.fill.background()
        
    if title:
        text_left = left + Inches(0.18) if accent_color else left + Inches(0.1)
        box = slide.shapes.add_textbox(text_left, top + Inches(0.1), width - Inches(0.3), Inches(0.45))
        tf = box.text_frame
        add_formatted_paragraph(tf, title, font_size=18, default_color=ACCENT_GOLD, is_first=True)
        p = tf.paragraphs[0]
        for run in p.runs:
            run.font.bold = True
            
    return rect

def add_formatted_paragraph(tf, text, font_size=14, default_color=TEXT_WHITE, is_first=False):
    if is_first:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.font.size = Pt(font_size)
    p.font.color.rgb = default_color
    
    import re
    tokens = re.split(r'(\*\*[^*]+\*\*|\_[^_]+\_|\[_[^_]+_\]|\^[^^]+\^)', text)
    
    for token in tokens:
        if not token:
            continue
        run = p.add_run()
        run.font.size = Pt(font_size)
        run.font.color.rgb = default_color
        
        if token.startswith('**') and token.endswith('**'):
            inner = token[2:-2]
            run.text = inner
            run.font.bold = True
        elif token.startswith('_') and token.endswith('_'):
            inner = token[1:-1]
            run.text = inner
            run.font.italic = True
        elif token.startswith('[_') and token.endswith('_]'):
            inner = token[2:-2]  # strip [_ and _]
            run.text = inner
            run.font.italic = True
            run.font.subscript = True
            run.font.size = Pt(max(8, font_size - 4))
        elif token.startswith('^') and token.endswith('^'):
            inner = token[1:-1]
            if inner.startswith('_') and inner.endswith('_'):
                run.text = inner[1:-1]
                run.font.italic = True
            else:
                run.text = inner
            run.font.superscript = True
            run.font.size = Pt(max(8, font_size - 4))
        else:
            run.text = token

def add_text(slide, left, top, width, height, text, size=14, bold=False, color=TEXT_WHITE, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        add_formatted_paragraph(tf, line, font_size=size, default_color=color, is_first=(i==0))
        tf.paragraphs[-1].alignment = align
        if bold:
            for run in tf.paragraphs[-1].runs:
                run.font.bold = True
                
    return box

def add_image(slide, img_path, left, top, width=None, height=None):
    if os.path.exists(img_path):
        return slide.shapes.add_picture(img_path, left, top, width=width, height=height)
    return None

def add_latex_equation(slide, formula_text, left, top, height, color='#E8A838', dpi=300, max_width=Inches(5.5)):
    import os
    import matplotlib.pyplot as plt
    from PIL import Image
    import hashlib
    
    # Carpeta temporal para las ecuaciones LaTeX
    temp_dir = 'output/temp_latex'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generar hash único para evitar re-renderizados innecesarios y acelerar la ejecución
    h = hashlib.md5(f"{formula_text}_{color}".encode('utf-8')).hexdigest()
    file_path = os.path.join(temp_dir, f"eq_{h}.png")
    
    if not os.path.exists(file_path):
        # Crear figura sin fondo con proporciones estiradas (20 pulgadas de ancho) para evitar cortes en fórmulas largas
        fig = plt.figure(figsize=(20, 1.8), facecolor='none')
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        
        # Envolver en dólares si no lo está
        math_text = formula_text if formula_text.startswith('$') else f"${formula_text}$"
        
        ax.text(0.5, 0.5, math_text, 
                fontsize=24, 
                color=color, 
                ha='center', 
                va='center',
                math_fontfamily='cm') # Computer Modern (LaTeX look)
                
        plt.savefig(file_path, dpi=dpi, bbox_inches='tight', pad_inches=0.05, transparent=True)
        plt.close(fig)
        
        # Recortar los bordes transparentes sobrantes usando Pillow
        img = Image.open(file_path)
        bbox = img.getbbox()
        if bbox:
            cropped = img.crop(bbox)
            cropped.save(file_path)
            
    # Determinar la relación de aspecto para no distorsionar la imagen en la diapositiva
    img = Image.open(file_path)
    aspect_ratio = img.width / img.height
    width = height * aspect_ratio
    
    # Restricción de ancho máximo de columna: si supera max_width, se auto-escala proporcionalmente
    if width > max_width:
        width = max_width
        height = width / aspect_ratio
    
    # Insertar la imagen en el slide
    slide.shapes.add_picture(file_path, left, top, width=width, height=height)


def create_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    TOTAL_SLIDES = 25

    # ==========================================
    # CUERPO PRINCIPAL DE LA PRESENTACIÓN
    # ==========================================

    # --- SLIDE 1: Portada (Formato obligatorio) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    
    # Banda de acento vertical izquierda para un diseño de portada muy profesional
    cover_band = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.2), SLIDE_HEIGHT)
    cover_band.fill.solid()
    cover_band.fill.fore_color.rgb = ACCENT_ORANGE
    cover_band.line.fill.background()
    
    add_text(slide, Inches(0.8), Inches(1.5), SLIDE_WIDTH - Inches(1.6), Inches(1.8), 
             "Evaluación de Tecnologías Fotovoltaicas en el Desierto de Atacama", size=38, bold=True, color=ACCENT_GOLD, align=PP_ALIGN.LEFT)
             
    # Delgada línea horizontal cyan de separación debajo del título
    sep_line = slide.shapes.add_shape(1, Inches(0.8), Inches(3.1), Inches(4.5), Inches(0.04))
    sep_line.fill.solid()
    sep_line.fill.fore_color.rgb = ACCENT_BLUE
    sep_line.line.fill.background()
    
    # Agrupar nombres e información en un panel premium
    names_panel = slide.shapes.add_shape(1, Inches(0.8), Inches(3.6), SLIDE_WIDTH - Inches(1.6), Inches(2.8))
    names_panel.fill.solid()
    names_panel.fill.fore_color.rgb = PANEL_BG
    names_panel.line.color.rgb = ACCENT_BLUE
    names_panel.line.width = Pt(1.5)
    
    names_text = ("Integrantes / Estudiantes:\n"
                  "Laury Gualdron  |  Sebastian Marin  |  Alejandro Hernández\n\n"
                  "Profesor Guía: Carlos Cardenas\n"
                  "ELI556 — Modelamiento y Análisis de Sistemas PV  |  Grupo Alta Tensión (AT)\n"
                  "Fecha de presentación: Jueves, 11 de junio de 2026")
    add_text(slide, Inches(1.1), Inches(3.8), SLIDE_WIDTH - Inches(2.2), Inches(2.4), names_text, size=16, color=TEXT_WHITE, align=PP_ALIGN.LEFT)
    add_footer(slide, 1, TOTAL_SLIDES)

    # --- SLIDE 2: a) Introducción al problema y contextualización ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "a) Introducción al problema y contextualización: El Desierto de Atacama")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Contexto: El Recurso Solar más Extremo", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Irradiación Excepcional:** Irradiancia horizontal global (GHI) anual > 2900 kWh/m² (máxima a nivel mundial).\n\n"
             "• **Cielos Limpios:** Baja atenuación atmosférica e irradiancia directa muy concentrada.\n\n"
             "• **Efecto de Altitud:** Mayor radiación directa y UV en zonas elevadas (>= 2400 m.s.n.m.).\n\n"
             "• **Estudio Geográfico:** Simulación localizada para San Pedro de Atacama (Latitud -22.91°, Longitud -68.20°).", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Desafío: El Estrés Térmico de Operación", accent_color=ACCENT_ORANGE)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Calentamiento Severo:** Las celdas solares operan a temperaturas superiores a 65°C a mediodía en verano.\n\n"
             "• **Degradación Térmica:** La potencia máxima y el voltaje decaen con el incremento de la temperatura de celda (_T_[_c_]).\n\n"
             "• **Objetivo:** Modelar dinámicamente y comparar qué tecnología resiste de mejor manera este estrés térmico desértico durante el año calendario 2026.", size=17)
    add_footer(slide, 2, TOTAL_SLIDES)

    # --- SLIDE 3: b) Justificación e impacto (relevancia del tema): Selección de Tecnologías ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "b) Justificación e impacto (relevancia del tema): Selección de Tecnologías")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.5), title="Comparativa de Familias del Dataset Cocoa (NREL) y Criterio de Selección", accent_color=ACCENT_GOLD)
    
    rows, cols = 6, 5
    left, top = MARGIN + Inches(0.2), Inches(1.8)
    width, height = SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(4.5)
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    tbl = table_shape._element.graphic.graphicData.tbl
    tblPr = tbl.tblPr
    style_id_element = tblPr.find(qn('a:tableStyleId'))
    if style_id_element is not None:
        style_id_element.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'
    
    table.columns[0].width = Inches(2.6)
    table.columns[1].width = Inches(1.2)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(3.7)
    table.columns[4].width = Inches(2.8)
    
    headers = ["Tecnología", "Eficiencia", "Coef. Temp. (Pmp)", "Comportamiento en Desierto", "Decisión / Rol"]
    data = [
        ["m-Si / x-Si\n(Silicio Monocristalino)", "17% - 21%", "-0.40 %/°C (Malo)", "Grandes pérdidas por calor (baja tolerancia).", "SELECCIONADO (Línea Base)"],
        ["HIT\n(Heterounión)", "20% - 22%", "-0.26 %/°C (Excelente)", "Mantiene alta producción bajo estrés térmico.", "SELECCIONADO (Premium)"],
        ["CdTe\n(Teluro de Cadmio)", "15% - 18%", "-0.28 %/°C (Excelente)", "Desempeño térmico sobresaliente; toxicidad por Cadmio.", "DESCARTADO (Menor contraste)"],
        ["CIGS\n(Película Delgada)", "14% - 16%", "-0.35 %/°C (Bueno)", "Pérdidas moderadas; susceptible a degradación por humedad.", "DESCARTADO (Sin contraste extremo)"],
        ["a-Si (Película Fina)\n(Silicio Amorfo)", "6% - 10%", "-0.20 %/°C (Excelente)", "Muy baja eficiencia base y alta degradación inicial.", "DESCARTADO (Inviable comercial)"]
    ]
    
    for c in range(cols):
        cell = table.cell(0, c)
        cell.text = headers[c]
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x2C, 0x2C, 0x48)
        cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(14)
            p.font.color.rgb = ACCENT_GOLD
            p.alignment = PP_ALIGN.CENTER
            
    for r in range(1, rows):
        row_data = data[r-1]
        is_selected = "SELECCIONADO" in row_data[4]
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = row_data[c]
            cell.fill.solid()
            if is_selected:
                cell.fill.fore_color.rgb = RGBColor(0x28, 0x28, 0x4B)
            else:
                cell.fill.fore_color.rgb = RGBColor(0x1F, 0x1F, 0x33)
            
            cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(13 if c == 3 else 14)
                if is_selected:
                    p.font.color.rgb = ACCENT_GOLD if c == 4 else TEXT_WHITE
                else:
                    p.font.color.rgb = RGBColor(0xBB, 0xBB, 0xBB) if c == 4 else TEXT_WHITE
                
                if c in [0, 4]: 
                    p.font.bold = True
                
                if c in [1, 2, 4]: 
                    p.alignment = PP_ALIGN.CENTER
                else: 
                    p.alignment = PP_ALIGN.LEFT
                    
    add_footer(slide, 3, TOTAL_SLIDES)

    # --- SLIDE 4: c) Marco referencial y revisión de literatura pertinente: Modelos Teóricos ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "c) Marco referencial y revisión de literatura pertinente: Modelos Teóricos")
    
    # Columna 1: Explicación de Modelos (Asimétrica y Detallada)
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.2), Inches(5.5), title="Literatura Académica y Modelos Utilizados", accent_color=ACCENT_BLUE)
    referencias_cuerpo = (
        "• **Modelo de un Diodo Simple (SDM) [De Soto et al., 2006]:**\n"
        "  Estructura circuital clásica que describe eléctricamente la celda. Incorpora las pérdidas óhmicas en serie (_R_[_s_]) y las corrientes de fuga shunt (_R_[_sh_]). *(Ecuación en Anexo IV, Lámina 22)*\n\n"
        "• **Modelo Térmico de Sandia (SAPM) [King et al., 2004]:**\n"
        "  Estima dinámicamente la temperatura interna de la celda (_T_[_c_]) a partir de la irradiancia incidente y el viento. *(Ecuación en Anexo III, Lámina 21)*\n\n"
        "• **Modelo de Transposición de Perez (1990) [Perez et al., 1990]:**\n"
        "  Traducción geométrica de irradiancia sobre plano inclinado, modelando el cielo difuso anisotrópico. *(Ecuación en Anexo I, Lámina 19)*\n\n"
        "• **Algoritmo de Parámetros de De Soto (2006) [De Soto et al., 2006]:**\n"
        "  Fórmulas para trasladar los parámetros desde STC a condiciones operacionales basándose en la energía de bandgap. *(Ecuaciones en Anexos V y VI, Láminas 23 y 24)*"
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), Inches(5.8), Inches(4.8), referencias_cuerpo, size=14)

    # Columna 2: Circuito Equivalente SDM (Imagen Explicativa)
    add_panel(slide, MARGIN + Inches(6.2) + GAP, Inches(1.2), Inches(5.733), Inches(5.5), title="Circuito Equivalente de un Diodo (SDM)", accent_color=ACCENT_GOLD)
    add_image(slide, 'output/Extra_Resultados/circuito_equivalente_sdm.png', MARGIN + Inches(6.2) + GAP + Inches(0.1), Inches(1.75), width=Inches(5.533), height=Inches(4.8))
    add_footer(slide, 4, TOTAL_SLIDES)

    # --- SLIDE 5: Procedimiento: Metodología y Pipeline de Simulación ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Metodología y Pipeline de Simulación")
    
    # Columna 1: Texto Explicativo del Pipeline
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.2), Inches(5.5), title="Flujo de Procesamiento y Simulación", accent_color=ACCENT_BLUE)
    method_text = (
        "• **Etapa 1: Ingesta de Datos (NREL Cocoa) [Marion et al., 2014]:**\n"
        "  Extracción selectiva de variables de recurso solar y métricas de curvas I-V completas a partir del dataset experimental.\n\n"
        "• **Etapa 2: Filtro de Emulación Geográfica:**\n"
        "  Traslación espacial, proyección a 2026 y desfase estacional de +6 meses para alinear el clima del Hemisferio Sur.\n\n"
        "• **Etapa 3: Modelamiento Físico y Ajuste Numérico:**\n"
        "  Cálculo térmico de Sandia [King et al., 2004] y ajuste de mínimos cuadrados para obtener los 5 parámetros de De Soto [De Soto et al., 2006] en STC.\n\n"
        "• **Etapa 4: Simulación Minutal de Operación:**\n"
        "  Escalamiento dinámico de parámetros (Modelo De Soto) y resolución implícita de I-V mediante pvlib [Holmgren et al., 2018].\n\n"
        "• **Etapa 5: Evaluación de Performance Ratio (PR):**\n"
        "  Integración anual y mensual del _PR_ utilizando el estándar IEC 61724-1. *(Fórmulas y glosario en Anexo VII, Lámina 25)*"
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), Inches(5.8), Inches(4.8), method_text, size=13)

    # Columna 2: Pipeline de Simulación (Imagen Explicativa)
    add_panel(slide, MARGIN + Inches(6.2) + GAP, Inches(1.2), Inches(5.733), Inches(5.5), title="Pipeline de Simulación", accent_color=ACCENT_GOLD)
    add_image(slide, 'output/Extra_Resultados/simulation_pipeline_infographic.png', MARGIN + Inches(6.2) + GAP + Inches(0.1), Inches(1.75), width=Inches(5.533), height=Inches(4.8))
    add_footer(slide, 5, TOTAL_SLIDES)

    # --- SLIDE 6: Procedimiento: Tratamiento de la Base de Datos y Carga de Big Data ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Tratamiento de la Base de Datos y Carga de Big Data")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Desafío: Procesamiento de Curvas I-V Minutales", accent_color=ACCENT_ORANGE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Naturaleza de los Datos:** Dataset experimental Cocoa (NREL) [Marion et al., 2014]. Contiene curvas I-V completas y mediciones meteorológicas minuto a minuto.\n\n"
             "• **Problema de Big Data:** Los archivos CSV unitarios superan los 100MB por tecnología, acumulando millones de registros de longitudes variables.\n\n"
             "• **Falla del Método Estándar:** Lectores convencionales (e.g., Pandas `read_csv`) agotan la memoria RAM y fallan debido a caracteres atípicos en la metadata.", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Solución: Pipeline de Lectura Eficiente", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Lector en Streaming:** Implementación de un analizador de archivos línea por línea mediante el módulo `csv` nativo de Python.\n\n"
             "• **Extracción Selectiva [Marion et al., 2014]:** Se ignoraron las series de curvas I-V completas en la carga inicial y se extrajeron únicamente los metadatos y puntos clave de operación (_I_[_sc_], _V_[_oc_], _I_[_mp_], _V_[_mp_], _P_[_mp_], irradiancias).\n\n"
             "• **Limpieza Automática:** Se descartaron registros nocturnos (_G_ < 10 W/m²) o incompletos, acelerando la simulación anual del recurso solar un 95%.", size=17)
    add_footer(slide, 6, TOTAL_SLIDES)

    # --- SLIDE 7: Procedimiento: Filtro de Emulación Geográfica (Florida → Atacama 2026) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Filtro de Emulación Geográfica")
    
    # Columna 1: Infografía de Emulación Geográfica (Imagen)
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.5), Inches(5.5), title="Mapa de Emulación Hemisférica", accent_color=ACCENT_GOLD)
    add_image(slide, 'output/Extra_Resultados/geo_emulation_map.png', MARGIN + Inches(0.1), Inches(1.75), width=Inches(5.3), height=Inches(4.5))

    # Columna 2: Texto Explicativo Combinado
    add_panel(slide, MARGIN + Inches(5.5) + GAP, Inches(1.2), Inches(6.733), Inches(5.5), title="Implementación del Filtro de Emulación", accent_color=ACCENT_BLUE)
    emulation_combined = (
        "• **Inconsistencia Estacional (Florida → Atacama):**\n"
        "  Los datos experimentales de NREL Cocoa [Marion et al., 2014] se midieron en el Hemisferio Norte. Simularlos directamente en el Hemisferio Sur crearía un desfase físico absurdo entre solsticios e inviernos térmicos.\n\n"
        "• **Desfase Temporal (+6 Meses):**\n"
        "  Se implementó un desplazamiento estacional exacto de +6 meses (+182 días). Así, el perfil de calor de Florida coincide coherentemente con el verano del Hemisferio Sur.\n\n"
        "• **Traducción Espacial a Atacama:**\n"
        "  Timestamp remapeado a 2026 con coordenadas de San Pedro de Atacama (Latitud −22.91° S, Longitud −68.20° W, Altitud 2400m) para calcular la inclinación óptima anual de **22.91° Norte** [Holmgren et al., 2018].\n\n"
        "• **Alineación de Coordenadas:**\n"
        "  Ajuste del ángulo cenital y azimutal en pvlib para simular una captación fotovoltaica impecable sin sombras locales."
    )
    add_text(slide, MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(1.8), Inches(6.333), Inches(4.5), emulation_combined, size=14)
    add_footer(slide, 7, TOTAL_SLIDES)

    # --- SLIDE 8: Procedimiento: Simulación del Perfil Térmico y Pérdidas Ópticas ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Simulación del Perfil Térmico y Pérdidas Ópticas")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Transposición de Recurso y Modificadores", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Modelo de Perez:** Ejecución del algoritmo [Perez et al., 1990] en pvlib para calcular la irradiancia total en el Plano del Arreglo (_G_[_poa_]). *(Ecuación en Anexo I, Lámina 19)*\n\n"
             "• **Modificador IAM:** Pérdidas por reflexión en el cristal basadas en la Ley de Snell y Bouguer [King et al., 2004] (espesor 2mm, índice refracción 1.526). *(Fórmulas en Anexo II, Lámina 20)*\n\n"
             "• **Modificador Espectral (AM):** Corrección empírica de masa de aire de cuarto orden [King et al., 2004] según la elevación del sol. *(Fórmula en Anexo II, Lámina 20)*", size=16)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Estimación de Temperatura Sandia (SAPM)", accent_color=ACCENT_ORANGE)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Modelación Tc:** Estimación dinámica de la temperatura de celda (_T_[_c_]) usando coeficientes empíricos de encapsulado del modelo de Sandia [King et al., 2004]. *(Fórmula en Anexo III, Lámina 21)*\n\n"
             "• **Asunciones Justificadas en Atacama:**\n"
             "  1. **Velocidad del Viento:** Fijada constante en **1 m/s** (valor conservador de diseño que minimiza pérdidas por convección artificial).\n"
             "  2. **Reflectancia del Suelo (Albedo):** Fijada en **0.20** (suelo arenoso/árido típico del desierto de Atacama).", size=16)
    add_footer(slide, 8, TOTAL_SLIDES)

    # --- SLIDE 9: Procedimiento: Metodología de Extracción de Parámetros en STC ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Metodología de Extracción de Parámetros en STC")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Desafío de Datasheet y Algoritmo Experimental", accent_color=ACCENT_ORANGE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **El Problema:** La base experimental Cocoa usa códigos internos del NREL (`mSi0166`, `HIT05667`) que no figuran directamente en datasheets comerciales estándar.\n\n"
             "• **Solución: Extracción en STC:** Se diseñó un algoritmo para caracterizar las propiedades nominales directamente desde la base de datos experimental minutal [De Soto et al., 2006].\n\n"
             "• **Condiciones de Referencia (SRC):** Se filtraron mediciones instantáneas bajo condiciones estándar (_G_ ≈ 1000 W/m² y temperatura de celda _T_[_c_] ≈ 25°C).", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Cálculo Experimental de Coeficientes Térmicos", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Coeficientes Térmicos** (_α_[_Isc_] y _β_[_Voc_]):\n"
             "  Calculados directamente de los datos usando regresiones lineales en periodos estables y de alta radiación (_G_ > 800 W/m²).\n\n"
             "• **Normalización y Consistencia [De Soto et al., 2006]:**\n"
             "  La corriente de cortocircuito se normalizó por irradiancia efectiva para aislar el coeficiente de ganancia térmica pura y asegurar consistencia paramétrica.", size=16)
    add_footer(slide, 9, TOTAL_SLIDES)

    # --- SLIDE 10: Procedimiento: Ajuste Numérico de Parámetros de Referencia ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Ajuste Numérico de Parámetros de Referencia")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Sistema de Ajuste Trascendental", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Formulación Matemática:** Ecuaciones del modelo SDM de 5 parámetros planteadas en STC para cortocircuito, circuito abierto y máxima potencia [De Soto et al., 2006]. *(Ecuación en Anexo IV, Lámina 22)*\n\n"
             "• **Optimización de Mínimos Cuadrados:** Resolución simultánea del sistema no lineal trascendental mediante scipy en Python para obtener los valores óptimos nominales.\n\n"
             "• **Consistencia Física (Bounds):** Restricciones explícitas de resistencia serie mayor a cero (_R_[_s,ref_] > 0) y factor de idealidad _n_[_I_] ∈ [1, 2] para garantizar sentido físico.", size=16)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Resultados de Parámetros en STC Extraídos", accent_color=ACCENT_GOLD)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **m-Si (Silicio Monocristalino) [De Soto et al., 2006]:**\n"
             "  _I_[_L,ref_] = 2.768 A  |  _I_[_0,ref_] = 4.13 × 10⁻⁹ A  |  _R_[_s,ref_] = 0.542 Ω  |  _R_[_sh,ref_] = 352.4 Ω\n\n"
             "• **HIT (Heterounión) [De Soto et al., 2006]:**\n"
             "  _I_[_L,ref_] = 5.607 A  |  _I_[_0,ref_] = 4.68 × 10⁻¹⁰ A  |  _R_[_s,ref_] = 0.412 Ω  |  _R_[_sh,ref_] = 612.8 Ω\n\n"
             "• **Coherencia Física:** La corriente de saturación inversa (_I_[_0_]) de HIT es un orden de magnitud inferior, demostrando su menor recombinación intrínseca por temperatura.", size=16)
    add_footer(slide, 10, TOTAL_SLIDES)

    # --- SLIDE 11: Procedimiento: Traslado Paramétrico y Simulación Minutal ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Traslado Paramétrico y Simulación Minutal")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Escalamiento Dinámico a Condiciones Reales", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Traslado de De Soto:** Para cada intervalo de la simulación anual 2026, los 5 parámetros se escalaron a la irradiancia efectiva (_S_) y temperatura de celda (_T_[_c_]) locales [De Soto et al., 2006]. *(Ecuaciones en Anexo VI, Lámina 24)*\n\n"
             "• **Dependencia del Bandgap:** Variación térmica no lineal del bandgap de silicio (_E_[_g_]) y factor de idealidad térmico (_a_).\n\n"
             "• **Resistencias Shunt y Serie:** Resistencia paralelo inversamente proporcional a la irradiancia. Resistencia serie asumida constante según validaciones NIST [De Soto et al., 2006].", size=16)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Resolución Implícita del Circuito (MPP)", accent_color=ACCENT_GOLD)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Resolución Numérica:** Empleo del algoritmo implícito `calcparams_desoto` de pvlib [Holmgren et al., 2018] para obtener los parámetros en cada minuto.\n\n"
             "• **Búsqueda del MPP:** Se resolvió la ecuación trascendental del diodo simple utilizando la función W de Lambert para ubicar el Punto de Máxima Potencia (_P_[_mp,SDM_]).\n\n"
             "• **Cómputo de Energía:** Integración temporal de la potencia útil minutal para consolidar la energía anual generada por cada panel.", size=16)
    add_footer(slide, 11, TOTAL_SLIDES)

    # --- SLIDE 12: d) Desarrollo, análisis crítico y discusión: Recurso Solar y Perfil Térmico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Recurso Solar y Perfil Térmico")
    
    # Columna Izquierda: Histograma
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.9), Inches(5.5), title="Distribución de Temperatura de Celda", accent_color=ACCENT_BLUE)
    add_image(slide, 'output/Fase1_Resultados/temp_hist_HIT.png', Inches(0.75), Inches(1.65), width=Inches(6.2), height=Inches(4.65))
    
    # Columna Derecha: Tarjeta Callout Superior
    add_panel(slide, Inches(7.6), Inches(1.2), Inches(5.333), Inches(1.6), title="Picos Térmicos Extremos de Celda", accent_color=ACCENT_ORANGE)
    add_text(slide, Inches(7.8), Inches(1.70), Inches(4.933), Inches(1.0), 
             "**65°C a 70°C** de temperatura operativa recurrente durante las horas del mediodía solar en Atacama.", size=16, color=ACCENT_ORANGE, bold=True)
             
    # Columna Derecha: Tarjeta de Análisis Inferior
    add_panel(slide, Inches(7.6), Inches(3.0), Inches(5.333), Inches(3.7), title="Análisis Crítico de Resultados", accent_color=ACCENT_GOLD)
    add_text(slide, Inches(7.8), Inches(3.50), Inches(4.933), Inches(3.0), 
             "• **Estrés Térmico Evidenciado:** La simulación térmica minutal revela temperaturas de celda operativas recurrentes muy por encima de STC.\n\n"
             "• **Enfriamiento Convectivo Limitado:** Al asumir velocidad de viento conservadora de 1 m/s en SAPM [King et al., 2004], se modela el escenario de mayor estrés físico.\n\n"
             "• **Consecuencia en Voltaje [De Soto et al., 2006]:** El calentamiento incrementa la corriente de saturación inversa (_I_[_0_]), deprimiendo la tensión de circuito abierto (_V_[_oc_]).", size=13)
    add_footer(slide, 12, TOTAL_SLIDES)

    # --- SLIDE 13: d) Desarrollo, análisis crítico y discusión: Validación del Modelo Eléctrico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Validación del Modelo Eléctrico")
    
    # Columna Izquierda: Scatter Plot
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.6), Inches(5.5), title="Validación: Potencia Medida vs. Simulada", accent_color=ACCENT_BLUE)
    add_image(slide, 'output/Fase2_Resultados/val_scatter_HIT.png', Inches(0.7), Inches(1.70), width=Inches(6.0), height=Inches(4.50))
    
    # Columna Derecha: Tarjeta Callout Superior
    add_panel(slide, Inches(7.3), Inches(1.2), Inches(5.633), Inches(1.6), title="Precisión del Modelo de 5 Parámetros", accent_color=ACCENT_BLUE)
    add_text(slide, Inches(7.5), Inches(1.70), Inches(5.233), Inches(1.0), 
             "**R² > 0.99**  |  **RMSE < 5W** de desviación minutal promedio bajo condiciones solares plenas.", size=16, color=ACCENT_BLUE, bold=True)
             
    # Columna Derecha: Tarjeta de Análisis Inferior
    add_panel(slide, Inches(7.3), Inches(3.0), Inches(5.633), Inches(3.7), title="Métricas de Ajuste y Rigor", accent_color=ACCENT_GOLD)
    add_text(slide, Inches(7.5), Inches(3.50), Inches(5.233), Inches(3.0), 
             "• **Fidelidad del Ajuste [De Soto et al., 2006]:** Coeficiente de determinación _R_² > 0.99 en validación cruzada frente a datos medidos, confirmando la precisión del modelo en todo el espectro.\n\n"
             "• **Desviación Minutal (RMSE):** Error cuadrático medio (_RMSE_) extremadamente bajo en periodos estables diurnos.\n\n"
             "• **Zonas de Discrepancia:** Leve dispersión en irradiancias bajas por la idealización empírica de la resistencia shunt.", size=13)
    add_footer(slide, 13, TOTAL_SLIDES)

    # --- SLIDE 14: d) Desarrollo, análisis crítico y discusión: Puntos Conflictuales y Acoplamiento Rs - n ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Puntos Conflictuales y Acoplamiento Rs - n")
    
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.5), Inches(5.5), title="Acoplamiento Rs - factor de idealidad (n)", accent_color=ACCENT_BLUE)
    acoplamiento_text = (
        "• **Alta Correlación Paramétrica [De Soto et al., 2006]:**\n"
        "  La resistencia serie (_R_[_s_]) y el factor de idealidad del diodo (_n_) influyen de manera similar en la redondez de la curva _I_-_V_ cerca del MPP.\n\n"
        "• **Problema Matemático Mal Condicionado:**\n"
        "  Múltiples combinaciones del par (_R_[_s_], _n_) pueden resultar en un ajuste idéntico de curvas con un error residual mínimo similar, perdiendo significado físico real.\n\n"
        "• **Mitigación y Solución [De Soto et al., 2006]:**\n"
        "  Se fijaron límites estrictos en el optimizador multivariable:\n"
        "  _R_[_s_] > 0  |  _n_ ∈ [1.0, 2.0]\n"
        "  Esto evita la convergencia a soluciones matemáticamente correctas pero físicamente imposibles."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), Inches(5.1), Inches(4.5), acoplamiento_text, size=14, color=TEXT_WHITE)
 
    # Columna 2: Limitaciones y Suposiciones
    add_panel(slide, MARGIN + Inches(5.5) + GAP, Inches(1.2), Inches(6.733), Inches(5.5), title="Limitaciones y Suposiciones del Modelo", accent_color=ACCENT_GOLD)
    limitaciones_text = (
        "• **Resistencia Shunt (_R_[_sh_]) e Irradiancia (_G_):**\n"
        "  La relación _R_[_sh_] = _R_[_sh,ref_] · (_S_[_ref_]/_S_) es empírica. A muy baja irradiancia (amanecer/ocaso), puede sobreestimar la resistencia shunt.\n"
        "  *Impacto:* Despreciable en el PR anual, ya que esas horas representan una fracción mínima de la energía total.\n\n"
        "• **_R_[_s_] Constante con la Temperatura:**\n"
        "  Ignora el cambio de la resistividad del semiconductor con _T_[_c_].\n"
        "  *Justificación:* De Soto (2006) validó que mantener _R_[_s_] constante produce errores de potencia < 2% frente a datos experimentales NIST.\n\n"
        "• **Bandgap lineal con la Temperatura:**\n"
        "  La relación del bandgap del Silicio con la temperatura se asume lineal, simplificando la ecuación real no lineal de Varshni.\n"
        "  *Impacto:* El error inducido es menor al 1% en el rango operacional (0°C a 70°C)."
    )
    add_text(slide, MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(1.8), Inches(6.333), Inches(4.5), limitaciones_text, size=14, color=TEXT_WHITE)
    add_footer(slide, 14, TOTAL_SLIDES)

    # --- SLIDE 15: d) Desarrollo, análisis crítico y discusión: Pérdidas Térmicas y Performance Ratio ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Pérdidas Térmicas y Performance Ratio")
    
    # Columna Izquierda: Gráfico de Degradación
    add_panel(slide, MARGIN, Inches(1.2), Inches(7.6), Inches(5.5), title="Normalización por Potencia Nominal", accent_color=ACCENT_BLUE)
    add_image(slide, 'output/Extra_Resultados/degradacion_termica_scatter.png', Inches(0.8), Inches(1.8), width=Inches(6.8))
    
    # Columna Derecha: Tarjeta Callout Superior
    add_panel(slide, Inches(8.3), Inches(1.2), Inches(4.633), Inches(1.6), title="Coeficientes de Temperatura (_P_[_mp_])", accent_color=ACCENT_ORANGE)
    add_text(slide, Inches(8.5), Inches(1.70), Inches(4.233), Inches(1.0), 
             "**m-Si:** −0.40 %/°C (Pérdidas severas)\n**HIT:** −0.26 %/°C (Alta tolerancia)", size=15, color=ACCENT_ORANGE, bold=True)
             
    # Columna Derecha: Tarjeta de Análisis Inferior
    add_panel(slide, Inches(8.3), Inches(3.0), Inches(4.633), Inches(3.7), title="Observación Científica", accent_color=ACCENT_GOLD)
    add_text(slide, Inches(8.5), Inches(3.50), Inches(4.233), Inches(3.0), 
             "• **Heterounión (HIT - Naranja) [De Soto et al., 2006]:** Coeficiente de temperatura muy bajo, preservando una alta eficiencia de conversión a 65°C.\n\n"
             "• **Silicio (m-Si - Azul) [De Soto et al., 2006]:** Descenso térmico pronunciado que penaliza la potencia generada durante el mediodía solar.\n\n"
             "• **Consecuencia en PR Anual:** Explica mecánicamente la diferencia del Performance Ratio entre tecnologías. *(Ecuación de PR en Anexo VII, Lámina 25)*", size=13)
    add_footer(slide, 15, TOTAL_SLIDES)

    # --- SLIDE 16: d) Desarrollo, análisis crítico y discusión: Veredicto Técnico y Económico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Veredicto Técnico y Económico")
    
    # Columna Izquierda: Callout de PR
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(1.8), title="Veredicto de Performance Ratio (PR Anual)", accent_color=ACCENT_GOLD)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.70), COLUMN_WIDTH - Inches(0.4), Inches(1.2), 
             "**HIT (Heterounión): 86.92%**  \n**m-Si (Monocristalino): 84.53%**  \n**Ganancia Neta: +2.39%** en PR anual.", size=16, color=ACCENT_GOLD, bold=True)
             
    # Columna Izquierda: Tarjeta de Análisis Técnico
    add_panel(slide, MARGIN, Inches(3.2), COLUMN_WIDTH, Inches(3.5), title="Conclusión Técnica de Diseño", accent_color=ACCENT_BLUE)
    verdict = (
        "• **Superioridad Física [De Soto et al., 2006]:**\n"
        "  HIT demuestra superioridad física indiscutible en Atacama. Su celda híbrida intrínsecamente resiste el calor amortiguando la caída de la tensión en circuito abierto (_V_[_oc_]).\n\n"
        "• **Estructura Híbrida:** Capas delgadas que atenúan recombinación de portadores debida a excitación térmica."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(3.70), COLUMN_WIDTH - Inches(0.4), Inches(2.8), verdict, size=14)
    
    # Columna Derecha: Callout de Impacto Financiero
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(1.8), title="Impacto Financiero (Planta de 100 MWp)", accent_color=ACCENT_ORANGE)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.70), COLUMN_WIDTH - Inches(0.4), Inches(1.2), 
             "**~6,000 MWh/año de generación adicional**  \n**+USD 270,000 anuales** de facturación neta.", size=16, color=ACCENT_ORANGE, bold=True)
             
    # Columna Derecha: Tarjeta de Análisis Económico
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(3.2), COLUMN_WIDTH, Inches(3.5), title="Análisis de Retorno de Inversión", accent_color=ACCENT_GOLD)
    impact_text = (
        "• **Equivalencia Energética:** Cada +1% de PR equivale a ~2,500 MWh de energía extra anual en una planta comercial de 100 MWp.\n\n"
        "• **Viabilidad en 25 Años:** Una mayor facturación neta de USD 270k anuales amortiza con holgura la inversión inicial (CAPEX) extra de paneles HIT frente a m-Si."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(3.70), COLUMN_WIDTH - Inches(0.4), Inches(2.8), impact_text, size=14)
    add_footer(slide, 16, TOTAL_SLIDES)

    # --- SLIDE 17: e) Conclusiones y propuestas de trabajos futuros ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "e) Conclusiones y propuestas de trabajos futuros")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Conclusiones del Estudio", accent_color=ACCENT_GOLD)
    concl = (
        "1. **Fidelidad Metodológica:** La emulación geográfica y estacional por traslación temporal fue coherente, permitiendo simular Atacama con data de Cocoa.\n\n"
        "2. **Ajuste Robusto:** El modelo De Soto de 5 parámetros reprodujo con alta precisión (_R_² > 0.99) el comportamiento del circuito.\n\n"
        "3. **HIT Vencedor:** HIT superó en 2.39% de PR a m-Si por su bajo coeficiente de temperatura de potencia.\n\n"
        "4. **Recomendación:** HIT es técnicamente superior para plantas desérticas de alta irradiancia y alta temperatura."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), concl, size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Propuestas de Trabajos Futuros", accent_color=ACCENT_BLUE)
    futur = (
        "• **Integración de Bifacialidad:** Incorporar el aporte de la irradiancia reflejada (albedo desértico, _ρ_ > 0.25) en la cara posterior del módulo.\n\n"
        "• **Pérdidas por Soiling:** Modelar la acumulación de polvo desértico en la superficie del cristal, factor de pérdida de rendimiento crítico en Atacama.\n\n"
        "• **Estudio Espectral Avanzado:** Evaluar el efecto de la masa de aire sobre la eficiencia cuántica de la celda de heterounión.\n\n"
        "• **Análisis de Doble Diodo:** Capturar los efectos de recombinación no ideal a baja irradiancia."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), futur, size=16)
    add_footer(slide, 17, TOTAL_SLIDES)

    # --- SLIDE 18: Referencias ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Referencias")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.5), title="Referencias Bibliográficas Estructuradas", accent_color=ACCENT_ORANGE)
    refs = ("1. De Soto, W., Klein, S.A., Beckman, W.A. (2006). \"Improvement and validation of a model for photovoltaic array performance.\" Solar Energy 80 (2006) 78–88.\n\n"
            "2. Sandia National Laboratories - Photovoltaic Array Performance Model (Sandia Report SAND2004-3535).\n\n"
            "3. NREL Cocoa Dataset - Experimental Measurements for Model Validation.\n\n"
            "4. pvlib-python Library documentation & community contributors.\n\n"
            "5. Marion, B. et al. (2014). \"Cocoa, Florida Data Set for Validating PV Models.\" NREL Technical Report.\n\n"
            "Agradecimientos al Departamento de Electrotecnia de la UTFSM.")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(4.5), refs, size=16)
    # ==========================================

    # --- SLIDE 19: Anexo I: Ecuaciones de Transposición y Absorción Solar ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo I: Ecuaciones de Transposición y Absorción Solar")
    
    # Perez POA
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.5), Inches(5.5), title="Transposición POA (Modelo de Perez)", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), Inches(5.1), Inches(0.35),
             "Calcula la irradiancia incidente total en el plano inclinado del panel:", size=15)
    add_latex_equation(slide, 
                       r"G_{poa} = G_b \cdot R_{beam} + G_d \cdot \left(\frac{1 + \cos(\beta)}{2}\right) + G \cdot \rho \cdot \left(\frac{1 - \cos(\beta)}{2}\right)", 
                       MARGIN + Inches(0.2), Inches(2.20), Inches(0.38), max_width=Inches(5.1))
    poa_glossary = (
        "Donde:\n"
        "• _G_[_b_] / _G_[_d_] / _G_: Irradiancia directa, difusa y global (W/m²).\n"
        "• _β_ (Tilt): Ángulo de inclinación del panel (22.91°).\n"
        "• _ρ_ (Albedo): Reflectancia del suelo desértico (~0.20).\n"
        "• _R_[_beam_]: Factor de transposición geométrica directa."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(3.20), Inches(5.1), Inches(3.0), poa_glossary, size=15, color=ACCENT_GOLD)
    
    # Absorción efectiva S
    add_panel(slide, MARGIN + Inches(5.5) + GAP, Inches(1.2), Inches(6.733), Inches(5.5), title="Absorción en Celda (Pérdidas Ópticas)", accent_color=ACCENT_GOLD)
    add_text(slide, MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(1.7), Inches(6.333), Inches(0.35),
             "Modela la radiación neta que penetra y es absorbida por la celda solar:", size=15)
    x_base = MARGIN + Inches(5.5) + GAP + Inches(0.2)
    add_latex_equation(slide, r"\frac{S}{S_{ref}} = \frac{G_b}{G_{ref}} \cdot R_{beam} \cdot K_{\tau\alpha,b}", x_base, Inches(2.05), Inches(0.42), max_width=Inches(6.333))
    add_latex_equation(slide, r"+ \frac{G_d}{G_{ref}} \cdot K_{\tau\alpha,d} \cdot \left(\frac{1 + \cos(\beta)}{2}\right)", x_base + Inches(0.95), Inches(2.50), Inches(0.42), max_width=Inches(5.383))
    add_latex_equation(slide, r"+ \frac{G}{G_{ref}} \cdot \rho \cdot K_{\tau\alpha,g} \cdot \left(\frac{1 - \cos(\beta)}{2}\right)", x_base + Inches(0.95), Inches(2.95), Inches(0.42), max_width=Inches(5.383))
    abs_glossary = (
        "Donde:\n"
        "• _S_ / _S_[_ref_]: Irradiancia efectiva y de referencia (1000 W/m²).\n"
        "• _K_[_τα,b_] / _K_[_τα,d_] / _K_[_τα,g_]: Modificadores por IAM para directa, difusa y albedo.\n"
        "• Modela las pérdidas ópticas reflectivas por ángulo de incidencia."
    )
    add_text(slide, MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(3.65), Inches(6.333), Inches(2.6), abs_glossary, size=16)
    add_footer(slide, 19, TOTAL_SLIDES)

    # --- SLIDE 20: Anexo II: Ecuaciones de Modificadores Ópticos (IAM y Masa de Aire) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo II: Ecuaciones de Modificadores Ópticos (IAM y Masa de Aire)")
    
    # IAM
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Ángulo de Incidencia (IAM)", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "Ecuación física basada en Ley de Snell y Bouguer:", size=15)
    add_latex_equation(slide, r"K_{\tau\alpha}(\theta) = \frac{\tau(\theta)}{\tau(0)}", MARGIN + Inches(0.3), Inches(2.10), Inches(0.45))
    add_latex_equation(slide, r"\tau(\theta) = e^{-\frac{K \cdot L}{\cos(\theta_r)}} \cdot \left[ 1 - \frac{1}{2} \left( \frac{\sin^2(\theta_r - \theta)}{\sin^2(\theta_r + \theta)} + \frac{\tan^2(\theta_r - \theta)}{\tan^2(\theta_r + \theta)} \right) \right]", MARGIN + Inches(0.3), Inches(2.70), Inches(0.45))
    add_latex_equation(slide, r"\theta_r = \arcsin\left(\frac{\sin(\theta)}{n}\right)", MARGIN + Inches(0.3), Inches(3.45), Inches(0.40))
    iam_details = (
        "Donde:\n"
        "• _θ_: Ángulo de incidencia  |  _n_ = 1.526 (Índice de refracción del vidrio).\n"
        "• _K_ = 4 m⁻¹ (Extinción del vidrio)  |  _L_ = 2 mm (Espesor del vidrio)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.30), COLUMN_WIDTH - Inches(0.4), Inches(2.0), iam_details, size=15, color=ACCENT_GOLD)
    
    # Air Mass
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Masa de Aire (AM)", accent_color=ACCENT_GOLD)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.65), COLUMN_WIDTH - Inches(0.4), Inches(0.55),
             "Corrige el desajuste del espectro según la atmósfera atravesada:", size=15)
    add_latex_equation(slide, r"\frac{M}{M_{ref}} = a_0 + a_1 \cdot AM + a_2 \cdot AM^2 + a_3 \cdot AM^3 + a_4 \cdot AM^4", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(2.35), Inches(0.40))
    add_latex_equation(slide, r"AM = \frac{1}{\cos(\theta_z) + 0.5057 \cdot (96.08 - \theta_z)^{-1.634}}", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(3.10), Inches(0.48))
    am_details = (
        "Donde:\n"
        "• _AM_: Masa de aire absoluta  |  _θ_[_z_]: Ángulo cenital del sol.\n"
        "• _a_[_0_] a _a_[_4_]: Coeficientes empíricos espectrales de la celda.\n"
        "• _M_[_ref_]: Transmitancia espectral a condiciones de referencia (AM 1.5g)."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(4.10), COLUMN_WIDTH - Inches(0.4), Inches(2.5), am_details, size=15)
    add_footer(slide, 20, TOTAL_SLIDES)

    # --- SLIDE 21: Anexo III: Ecuaciones del Perfil Térmico (Modelo Sandia SAPM) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo III: Ecuaciones del Perfil Térmico (Modelo Sandia SAPM)")
    
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(2.2), title="Ecuación de Sandia para Temperatura de Celda")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.65), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(0.35),
             "La temperatura de la celda fotovoltaica se modela a partir del equilibrio térmico dinámico:", size=15)
    add_latex_equation(slide, r"T_c = G_{poa} \cdot e^{a + b \cdot v_w} + T_a + \left(\frac{G_{poa}}{1000}\right) \cdot \Delta T", MARGIN + Inches(1.8), Inches(2.15), Inches(0.55))
    
    # Glosario
    add_panel(slide, MARGIN, Inches(3.6), Inches(5.0), Inches(3.1), title="Glosario de Variables")
    thermal_details = (
        "• _T_[_c_] / _T_[_a_]: Temp. de celda y ambiental (°C).\n"
        "• _G_[_poa_]: Irradiancia total en plano de panel (W/m²).\n"
        "• _v_[_w_]: Velocidad de viento circundante (m/s).\n"
        "• _a_, _b_, _ΔT_: Parámetros empíricos de encapsulado."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.10), Inches(4.6), Inches(2.3), thermal_details, size=15, color=ACCENT_GOLD)
    
    # Coeficientes
    add_panel(slide, MARGIN + Inches(5.0) + GAP, Inches(3.6), Inches(7.233), Inches(3.1), title="Coeficientes Empíricos Utilizados")
    thermal_coef = (
        "• **Silicio Monocristalino (m-Si) — glass/polymer (marco estándar):**\n"
        "  _a_ = -3.56  |  _b_ = -0.075  |  _ΔT_ = 3.0 °C\n\n"
        "• **Heterounión (HIT) — glass/glass (encapsulado térmico premium):**\n"
        "  _a_ = -3.47  |  _b_ = -0.059  |  _ΔT_ = 3.0 °C\n\n"
        "Estos coeficientes están validados empíricamente por el Sandia National Laboratories."
    )
    add_text(slide, MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(4.10), Inches(6.833), Inches(2.3), thermal_coef, size=14)
    add_footer(slide, 21, TOTAL_SLIDES)

    # --- SLIDE 22: Anexo IV: Ecuaciones del Modelo Eléctrico de un Diodo (SDM) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo IV: Ecuaciones del Modelo Eléctrico de un Diodo (SDM)")
    
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(2.2), title="Ecuación Trascendental del Circuito Equivalente")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.65), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(0.35),
             "Ecuación implícita de corriente del modelo de diodo simple con resistencias parásitas (Rs y Rsh):", size=15)
    add_latex_equation(slide, r"I = I_L - I_0 \cdot \left[ \exp\left(\frac{V + I \cdot R_s}{a}\right) - 1 \right] - \frac{V + I \cdot R_s}{R_{sh}}", MARGIN + Inches(1.2), Inches(2.15), Inches(0.42))
    
    # Factor de idealidad
    add_panel(slide, MARGIN, Inches(3.6), Inches(5.4), Inches(3.1), title="Factor de Idealidad Térmico (a)")
    add_text(slide, MARGIN + Inches(0.2), Inches(4.0), Inches(5.0), Inches(0.35),
             "El factor de idealidad térmico se define formalmente como:", size=15)
    add_latex_equation(slide, r"a = \frac{N_s \cdot n_I \cdot k \cdot T_c}{q}", MARGIN + Inches(0.5), Inches(4.55), Inches(0.48))
    add_text(slide, MARGIN + Inches(0.2), Inches(5.25), Inches(5.0), Inches(1.0),
             "Donde:\n"
             "• _N_[_s_]: Número de celdas en serie (m-Si: 36, HIT: 72).\n"
             "• _n_[_I_]: Factor de idealidad del diodo (idealmente entre 1 y 2).", size=14, color=ACCENT_GOLD)
    
    # Glosario
    add_panel(slide, Inches(6.1), Inches(3.6), Inches(6.833), Inches(3.1), title="Glosario de Parámetros Físicos")
    sdm_glossary = (
        "• _I_ / _V_: Corriente y voltaje de salida (A, V).\n"
        "• _I_[_L_]: Corriente fotogenerada por el efecto fotoeléctrico (A).\n"
        "• _I_[_0_]: Corriente de saturación inversa de la unión P-N (A).\n"
        "• _R_[_s_] / _R_[_sh_]: Resistencias parásitas en serie y paralelo (shunt) (Ω).\n"
        "• _k_ / _q_ / _T_[_c_]: Constante de Boltzmann, carga elemental y temperatura de celda (K)."
    )
    add_text(slide, Inches(6.3), Inches(4.0), Inches(6.433), Inches(2.3), sdm_glossary, size=14)
    add_footer(slide, 22, TOTAL_SLIDES)

    # --- SLIDE 23: Anexo V: Ecuaciones de Extracción en STC y Derivada Analítica ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo V: Ecuaciones de Extracción en STC y Derivada Analítica")
    
    # Ecuaciones en STC
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.0), Inches(5.5), title="Ajuste en STC", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.70), Inches(4.6), Inches(1.60),
             "Condiciones que determinan los 5 parámetros de referencia en STC (1000 W/m², 25°C):\n\n"
             "1. Cortocircuito: _V_ = 0, _I_ = _I_[_sc,ref_]\n"
             "2. Circuito Abierto: _I_ = 0, _V_ = _V_[_oc,ref_]\n"
             "3. Máxima Potencia: _I_ = _I_[_mp,ref_], _V_ = _V_[_mp,ref_]\n"
             "4. Derivada de Potencia en MPP (d_P_/d_V_ = 0):", size=15)
    add_latex_equation(slide, r"\left.\frac{dI}{dV}\right|_{mp} = -\frac{I_{mp,ref}}{V_{mp,ref}}", MARGIN + Inches(0.2), Inches(3.40), Inches(0.65), max_width=Inches(4.6))
    add_text(slide, MARGIN + Inches(0.2), Inches(4.25), Inches(4.6), Inches(0.35),
             "5. Coeficiente térmico experimental de _V_[_oc_]:", size=15)
    add_latex_equation(slide, r"\beta_{Voc} = \frac{\partial V_{oc}}{\partial T_c}", MARGIN + Inches(0.2), Inches(4.70), Inches(0.65), max_width=Inches(4.6))
    
    # Derivada analítica
    add_panel(slide, Inches(5.7), Inches(1.2), Inches(7.233), Inches(5.5), title="Derivada Analítica Completa en MPP", accent_color=ACCENT_GOLD)
    add_text(slide, Inches(5.9), Inches(1.70), Inches(6.833), Inches(0.6),
             "Para la optimización, se derivó analíticamente la ecuación implícita en la zona del MPP:", size=15)
    add_latex_equation(slide, r"\left.\frac{dI}{dV}\right|_{mp} = -\frac{A + B}{1 + R_s \cdot A + R_s \cdot B}", Inches(5.9), Inches(2.40), Inches(0.68), max_width=Inches(6.833))
    add_text(slide, Inches(5.9), Inches(3.25), Inches(6.833), Inches(0.35),
             "Donde los coeficientes internos del diodo se definen como:", size=15)
    add_latex_equation(slide, r"A = \frac{I_0}{a} \cdot e^{\frac{V_{mp} + I_{mp} \cdot R_s}{a}}", Inches(5.9), Inches(3.70), Inches(0.55), max_width=Inches(6.833))
    add_latex_equation(slide, r"B = \frac{1}{R_{sh}}", Inches(5.9), Inches(4.35), Inches(0.45), max_width=Inches(6.833))
    add_footer(slide, 23, TOTAL_SLIDES)

    # --- SLIDE 24: Anexo VI: Ecuaciones de Escalamiento a Condiciones de Operación ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo VI: Ecuaciones de Escalamiento a Condiciones de Operación")
    
    # Izquierda
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Corrientes y Factor de Idealidad", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.70), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "1. Corriente Fotogenerada (_I_[_L_]):", size=15)
    add_latex_equation(slide, r"I_L = \left(\frac{S}{S_{ref}}\right) \cdot \left(\frac{M}{M_{ref}}\right) \cdot \left[ I_{L,ref} + \alpha_{Isc} \cdot (T_c - T_{ref}) \right]", MARGIN + Inches(0.3), Inches(2.05), Inches(0.55))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(2.75), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "2. Corriente de Saturación Inversa (_I_[_0_]):", size=15)
    add_latex_equation(slide, r"\frac{I_0}{I_{0,ref}} = \left(\frac{T_c}{T_{ref}}\right)^3 \cdot \exp\left[ \frac{E_{g,ref}}{k \cdot T_{ref}} - \frac{E_g}{k \cdot T_c} \right]", MARGIN + Inches(0.3), Inches(3.10), Inches(0.58))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(3.85), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "3. Factor de Idealidad térmico (_a_):", size=15)
    add_latex_equation(slide, r"\frac{a}{a_{ref}} = \frac{T_c}{T_{ref}}", MARGIN + Inches(0.3), Inches(4.20), Inches(0.55))
    add_footer(slide, 24, TOTAL_SLIDES)
    
    # Derecha
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Resistencias y Energía de Bandgap", accent_color=ACCENT_GOLD)
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.70), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "4. Resistencia Shunt (_R_[_sh_]):", size=15)
    add_latex_equation(slide, r"R_{sh} = R_{sh,ref} \cdot \left(\frac{S_{ref}}{S}\right)", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(2.05), Inches(0.55))
    
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(2.75), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "5. Energía de Bandgap del Silicio (_E_[_g_]):", size=15)
    add_latex_equation(slide, r"\frac{E_g}{E_{g,ref}} = 1 - 0.0002677 \cdot (T_c - T_{ref})", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(3.10), Inches(0.55))
    
    scale_just = (
        "Suposiciones Físicas Justificadas:\n"
        "• _R_[_s_] Constante: Se asume _R_[_s_] = _R_[_s,ref_].\n"
        "• _R_[_sh_] Dependiente de G: Modelada inversamente proporcional a la irradiancia incidente efectiva _S_.\n"
        "• _E_[_g,ref_] = 1.121 eV para el Silicio a 25°C."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(3.85), COLUMN_WIDTH - Inches(0.4), Inches(2.70), scale_just, size=15)
    add_footer(slide, 24, TOTAL_SLIDES)

    # --- SLIDE 25: Anexo VII: Ecuaciones para el Cálculo del Performance Ratio ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo VII: Ecuaciones para el Cálculo del Performance Ratio")
    
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(2.2), title="Ecuación de Rendimiento Global del PR", accent_color=ACCENT_BLUE)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.65), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(0.35),
             "El Performance Ratio (_PR_) evalúa la eficiencia neta del sistema fotovoltaico frente a condiciones estándar de referencia:", size=15)
    add_latex_equation(slide, r"PR = \left[ \sum_{t=1}^{N} V_{mp,t}(G_t, T_{c,t}) \cdot I_{mp,t}(G_t, T_{c,t}) \right] ~ / ~ \left[ \sum_{t=1}^{N} P_{STC} \cdot \left(\frac{G_{poa,t}}{G_{ref}}\right) \right]", MARGIN + Inches(0.5), Inches(2.10), Inches(0.75), max_width=Inches(10.73))
    
    # Glosario
    add_panel(slide, MARGIN, Inches(3.6), Inches(5.2), Inches(3.1), title="Glosario de Variables", accent_color=ACCENT_GOLD)
    pr_details = (
        "• _V_[_mp,t_] / _I_[_mp,t_]: Tensión y corriente MPP horarias del SDM.\n"
        "• _P_[_STC_]: Potencia nominal del panel en STC (m-Si: 46.68 W | HIT: 217.52 W).\n"
        "• _G_[_poa,t_]: Irradiancia instantánea en el plano del panel (W/m²).\n"
        "• _G_[_ref_]: Irradiancia de referencia a condiciones STC (1000 W/m²)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.10), Inches(4.8), Inches(2.3), pr_details, size=14, color=ACCENT_GOLD)
    
    # Pérdidas
    add_panel(slide, Inches(5.9), Inches(3.6), Inches(7.033), Inches(3.1), title="Pérdidas Penalizadas por el PR", accent_color=ACCENT_BLUE)
    pr_phys = (
        "• **Pérdidas Térmicas:** Caídas debidas a la elevada temperatura _T_[_c_].\n"
        "• **Pérdidas Ópticas:** Pérdidas reflectivas por ángulo de incidencia (IAM).\n"
        "• **Pérdidas Espectrales:** Desajustes causados por la Masa de Aire (AM).\n"
        "• **Pérdidas Óhmicas:** Pérdidas resistivas en la resistencia serie _R_[_s_]."
    )
    add_text(slide, Inches(6.1), Inches(4.10), Inches(6.633), Inches(2.3), pr_phys, size=15)
    add_footer(slide, 25, TOTAL_SLIDES)

    # --- Guardar con manejo robusto de bloqueos de PowerPoint ---
    output_path = "output/Presentacion_Final_ELI556_Atacama.pptx"
    try:
        prs.save(output_path)
        print(f"Presentacion guardada exitosamente en: {output_path}")
    except PermissionError:
        alternative_path = "output/Presentacion_Final_ELI556_Atacama_v2.pptx"
        print(f"[ALERTA DE PERMISOS] '{output_path}' esta abierto y bloqueado.")
        print(f"Guardando copia alternativa en: {alternative_path}")
        prs.save(alternative_path)
        print(f"Presentacion alternativa guardada exitosamente en: {alternative_path}")

if __name__ == "__main__":
    create_presentation()
