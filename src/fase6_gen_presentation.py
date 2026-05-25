from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
from pptx.oxml.ns import qn
import os

# --- Configuración del Sistema de Diseño ---
DARK_BG = RGBColor(0x1A, 0x1A, 0x2E)
PANEL_BG = RGBColor(0x22, 0x22, 0x3A)
ACCENT_GOLD = RGBColor(0xE8, 0xA8, 0x38)
ACCENT_BLUE = RGBColor(0x00, 0x7A, 0xCC)
TEXT_WHITE = RGBColor(0xFF, 0xFF, 0xFF)

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
    return title_box

def add_footer(slide, page_num, total_pages=25):
    footer_text = f"ELI556 | Grupo Alta Tensión | Lámina {page_num}/{total_pages}"
    footer_box = slide.shapes.add_textbox(MARGIN, SLIDE_HEIGHT - Inches(0.4), SLIDE_WIDTH - 2*MARGIN, Inches(0.3))
    p = footer_box.text_frame.paragraphs[0]
    p.text = footer_text
    p.font.size = Pt(10)
    p.font.color.rgb = RGBColor(120, 120, 120)
    p.alignment = PP_ALIGN.RIGHT

def add_panel(slide, left, top, width, height, title=""):
    rect = slide.shapes.add_shape(1, left, top, width, height)
    rect.fill.solid()
    rect.fill.fore_color.rgb = PANEL_BG
    rect.line.color.rgb = ACCENT_BLUE
    rect.line.width = Pt(1.0)
    
    if title:
        box = slide.shapes.add_textbox(left + Inches(0.1), top + Inches(0.1), width - Inches(0.2), Inches(0.45))
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
    tokens = re.split(r'(\*\*[^*]+\*\*|\_[^_]+\_|\[[^\]]+\]|\^[^^]+\^)', text)
    
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
        elif token.startswith('[') and token.endswith(']'):
            inner = token[1:-1]
            if inner.startswith('_') and inner.endswith('_'):
                run.text = inner[1:-1]
                run.font.italic = True
            else:
                run.text = inner
            run.font.subscript = True
        elif token.startswith('^') and token.endswith('^'):
            inner = token[1:-1]
            if inner.startswith('_') and inner.endswith('_'):
                run.text = inner[1:-1]
                run.font.italic = True
            else:
                run.text = inner
            run.font.superscript = True
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
    add_text(slide, MARGIN, Inches(1.8), SLIDE_WIDTH - 2*MARGIN, Inches(1.5), 
             "Evaluación de Tecnologías Fotovoltaicas en el Desierto de Atacama", size=36, bold=True, color=ACCENT_GOLD, align=PP_ALIGN.CENTER)
    
    names_text = ("Integrantes / Estudiantes:\n"
                  "Laury Gualdron  |  Sebastian Marin  |  Alejandro Hernández\n\n"
                  "Profesor Guía: Carlos Cardenas\n"
                  "ELI556 — Modelamiento y Análisis de Sistemas PV  |  Grupo Alta Tensión (AT)\n"
                  "Fecha de presentación: Jueves, 11 de junio de 2026")
    add_text(slide, MARGIN, Inches(3.8), SLIDE_WIDTH - 2*MARGIN, Inches(2.0), names_text, size=16, color=TEXT_WHITE, align=PP_ALIGN.CENTER)
    add_footer(slide, 1, TOTAL_SLIDES)

    # --- SLIDE 2: a) Introducción al problema y contextualización ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "a) Introducción al problema y contextualización: El Desierto de Atacama")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Contexto: El Recurso Solar más Extremo")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Irradiación Excepcional:** Irradiancia horizontal global (GHI) anual > 2900 kWh/m² (máxima a nivel mundial).\n\n"
             "• **Cielos Limpios:** Baja atenuación atmosférica e irradiancia directa muy concentrada.\n\n"
             "• **Efecto de Altitud:** Mayor radiación directa y UV en zonas elevadas (>= 2400 m.s.n.m.).\n\n"
             "• **Estudio Geográfico:** Simulación localizada para San Pedro de Atacama (Latitud -22.91°, Longitud -68.20°).", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Desafío: El Estrés Térmico de Operación")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Calentamiento Severo:** Las celdas solares operan a temperaturas superiores a 65°C a mediodía en verano.\n\n"
             "• **Degradación Térmica:** La potencia máxima y el voltaje decaen con el incremento de la temperatura de celda (_T_[_c_]).\n\n"
             "• **Objetivo:** Modelar dinámicamente y comparar qué tecnología resiste de mejor manera este estrés térmico desértico durante el año calendario 2026.", size=17)
    add_footer(slide, 2, TOTAL_SLIDES)

    # --- SLIDE 3: b) Justificación e impacto (relevancia del tema): Selección de Tecnologías ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "b) Justificación e impacto (relevancia del tema): Selección de Tecnologías")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.5), title="Comparativa de Familias del Dataset Cocoa (NREL) y Criterio de Selección")
    
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
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.2), Inches(5.5), title="Literatura Académica y Modelos Utilizados")
    referencias_cuerpo = (
        "• **Modelo de un Diodo Simple (SDM):**\n"
        "  Estructura circuital clásica que describe eléctricamente la celda. Incorpora las pérdidas óhmicas resistivas en serie (_R_[_s_]) y las corrientes de fuga shunt (_R_[_sh_]) en el semiconductor.\n\n"
        "• **Modelo Térmico de Sandia (SAPM):**\n"
        "  Estima dinámicamente la temperatura interna de la celda (_T_[_c_]) a partir de la irradiancia incidente y la velocidad del viento, considerando los coeficientes empíricos del encapsulado.\n\n"
        "• **Modelo de Transposición de Perez (1990):**\n"
        "  Traducción geométrica de irradiancia sobre plano inclinado, modelando componentes de cielo difuso anisotrópico.\n\n"
        "• **Algoritmo de Parámetros de De Soto (2006):**\n"
        "  Fórmulas para trasladar los parámetros desde STC a condiciones operacionales basándose en la energía de bandgap del silicio."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), Inches(5.8), Inches(4.8), referencias_cuerpo, size=14)

    # Columna 2: Circuito Equivalente SDM (Imagen Explicativa)
    add_panel(slide, MARGIN + Inches(6.2) + GAP, Inches(1.2), Inches(5.733), Inches(5.5), title="Circuito Equivalente de un Diodo (SDM)")
    add_image(slide, 'output/Extra_Resultados/circuito_equivalente_sdm.png', MARGIN + Inches(6.2) + GAP + Inches(0.1), Inches(1.75), width=Inches(5.533), height=Inches(4.8))
    add_footer(slide, 4, TOTAL_SLIDES)

    # --- SLIDE 5: Procedimiento: Metodología y Pipeline de Simulación ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Metodología y Pipeline de Simulación")
    
    # Columna 1: Texto Explicativo del Pipeline
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.2), Inches(5.5), title="Flujo de Procesamiento y Simulación")
    method_text = (
        "• **Etapa 1: Ingesta de Datos (NREL Cocoa):**\n"
        "  Extracción selectiva de variables de recurso solar y métricas eléctricas minutales a partir del dataset experimental.\n\n"
        "• **Etapa 2: Filtro de Emulación Geográfica:**\n"
        "  Traslación espacial, proyección al año calendarizado 2026 y desfase estacional estricto de +6 meses.\n\n"
        "• **Etapa 3: Modelamiento Físico y Ajuste Numérico:**\n"
        "  Cálculo térmico (Sandia) y ajuste por mínimos cuadrados acotados para obtener los 5 parámetros De Soto en STC.\n\n"
        "• **Etapa 4: Simulación Minutal de Operación:**\n"
        "  Escalamiento dinámico de parámetros y resolución implícita del circuito fotovoltaico minutal para calcular energía.\n\n"
        "• **Etapa 5: Evaluación de Indicadores (Performance Ratio):**\n"
        "  Integración anual y mensual del _PR_ para recomendación final."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), Inches(5.8), Inches(4.8), method_text, size=13)

    # Columna 2: Pipeline de Simulación (Imagen Explicativa)
    add_panel(slide, MARGIN + Inches(6.2) + GAP, Inches(1.2), Inches(5.733), Inches(5.5), title="Pipeline de Simulación")
    add_image(slide, 'output/Extra_Resultados/simulation_pipeline_infographic.png', MARGIN + Inches(6.2) + GAP + Inches(0.1), Inches(1.75), width=Inches(5.533), height=Inches(4.8))
    add_footer(slide, 5, TOTAL_SLIDES)

    # --- SLIDE 6: Procedimiento: Tratamiento de la Base de Datos y Carga de Big Data ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Tratamiento de la Base de Datos y Carga de Big Data")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Desafío: Procesamiento de Curvas I-V Minutales")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Naturaleza de los Datos:** Dataset Cocoa (NREL). Contiene mediciones experimentales minuto a minuto de curvas I-V completas tomadas en Florida.\n\n"
             "• **Problema de Big Data:** Los archivos CSV unitarios superan los 100MB por tecnología, con millones de registros de longitudes variables.\n\n"
             "• **Falla del Método Estándar:** Lectores convencionales (Pandas `read_csv`) agotan la RAM y fallan debido a caracteres atípicos en los metadatos.", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Solución: Pipeline de Lectura Eficiente")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Lector en Streaming:** Implementación de un analizador de archivos línea por línea mediante el módulo `csv` nativo de Python.\n\n"
             "• **Extracción Selectiva:** Se ignoraron las series de curvas I-V masivas en la carga inicial y se extrajeron únicamente los metadatos y puntos clave de operación (_I_[_sc_], _V_[_oc_], _I_[_mp_], _V_[_mp_], _P_[_mp_], irradiancias).\n\n"
             "• **Limpieza Automática:** Se descartaron registros nocturnos ($G < 10$ W/m²) o con datos incompletos, acelerando la simulación anual un 95%.", size=17)
    add_footer(slide, 6, TOTAL_SLIDES)

    # --- SLIDE 7: Procedimiento: Filtro de Emulación Geográfica (Florida → Atacama 2026) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Filtro de Emulación Geográfica")
    
    # Columna 1: Infografía de Emulación Geográfica (Imagen)
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.5), Inches(5.5), title="Mapa de Emulación Hemisférica")
    add_image(slide, 'output/Extra_Resultados/geo_emulation_map.png', MARGIN + Inches(0.1), Inches(1.75), width=Inches(5.3), height=Inches(4.5))

    # Columna 2: Texto Explicativo Combinado
    add_panel(slide, MARGIN + Inches(5.5) + GAP, Inches(1.2), Inches(6.733), Inches(5.5), title="Implementación del Filtro de Emulación")
    emulation_combined = (
        "• **Inconsistencia Estacional (Florida → Atacama):**\n"
        "  Los datos crudos de NREL Cocoa son medidos en Florida (Hemisferio Norte). Si se simulan directamente en Atacama (Hemisferio Sur), el verano solar coincidiría con el invierno térmico real, lo que es físicamente incorrecto.\n\n"
        "• **Desfase Temporal (+6 Meses):**\n"
        "  Se aplicó un desplazamiento estacional de +6 meses (+182 días). De esta forma, el verano térmico medido en Florida se alinea correctamente con el verano astronómico del Hemisferio Sur.\n\n"
        "• **Traducción Espacial y Proyección 2026:**\n"
        "  Todos los timestamps se remapearon al año 2026. Se modificaron las coordenadas a San Pedro de Atacama (Latitud −22.91° S, Longitud −68.20° W, Altitud 2400 m).\n\n"
        "• **Alineación Solar Óptima:**\n"
        "  Inclinación del módulo (Tilt) fijada a **22.91°** (óptimo anual) y orientación (Azimut) a **0° Norte**."
    )
    add_text(slide, MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(1.8), Inches(6.333), Inches(4.5), emulation_combined, size=14)
    add_footer(slide, 7, TOTAL_SLIDES)

    # --- SLIDE 8: Procedimiento: Simulación del Perfil Térmico y Pérdidas Ópticas ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Simulación del Perfil Térmico y Pérdidas Ópticas")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Transposición de Recurso y Modificadores")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Modelo de Perez:** Ejecución del algoritmo en `pvlib` para calcular la irradiancia total en el Plano del Arreglo ($G_{poa}$).\n\n"
             "• **Modificador IAM:** Simulación física de pérdidas por reflexión en el cristal de los paneles. Se utilizaron coeficientes de transmitancia basados en el espesor del vidrio (2mm) y su índice de refracción (1.526).\n\n"
             "• **Modificador Espectral (AM):** Estimación de la masa de aire absoluta en función de la altura del sol, aplicando una corrección de cuarto orden.", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Estimación de Temperatura Sandia (SAPM)")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Modelación Tc:** Estimación dinámica minutal de la temperatura de celda utilizando los parámetros empíricos de encapsulado.\n\n"
             "• **Asunciones Justificadas en Atacama:**\n"
             "  1. **Velocidad del Viento:** Asumida constante en **1 m/s** (valor conservador para desierto que minimiza pérdidas por convección artificial).\n"
             "  2. **Reflectancia del Suelo (Albedo):** Fijada en **0.20** (suelo arenoso/árido del desierto de Atacama).", size=17)
    add_footer(slide, 8, TOTAL_SLIDES)

    # --- SLIDE 9: Procedimiento: Metodología de Extracción de Parámetros en STC ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Metodología de Extracción de Parámetros en STC")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Desafío de Datasheet y Algoritmo Experimental")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **El Problema:** La base experimental Cocoa usa códigos del NREL (`mSi0166`, `HIT05667`) que no corresponden a marcas comerciales registradas en las librerías estándar.\n\n"
             "• **Solución: Extracción Directa:** En lugar de buscar datasheets aproximados, se diseñó un algoritmo para encontrar las propiedades nominales directamente en las curvas medidas del CSV.\n\n"
             "• **Búsqueda SRC:** Se filtraron los instantes experimentales bajo condiciones estándar (STC: Irradiancia $G \approx 1000$ W/m² y temperatura de celda $T_c \approx 25^\circ\text{C}$).", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Cálculo Experimental de Coeficientes Térmicos")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Coeficientes de Temperatura ($\alpha_{Isc}$ y $\beta_{Voc}$):**\n"
             "  Se calcularon directamente de las mediciones aplicando regresiones lineales en condiciones de alta radiación ($G > 800$ W/m²).\n\n"
             "• **Normalización por Irradiancia:**\n"
             "  Para la corriente de cortocircuito, se normalizó el valor frente a la irradiancia instantánea para desacoplar el efecto solar y aislar la ganancia térmica pura.", size=17)
    add_footer(slide, 9, TOTAL_SLIDES)

    # --- SLIDE 10: Procedimiento: Ajuste Numérico de Parámetros de Referencia ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Ajuste Numérico de Parámetros de Referencia")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Sistema de Ajuste Trascendental")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Formulación Matemática:** Las ecuaciones de cortocircuito, circuito abierto, máxima potencia y derivada analítica en MPP ($dP/dV = 0$) forman un sistema no lineal trascendental de 5 incógnitas.\n\n"
             "• **Implementación de Mínimos Cuadrados:** Ajuste del sistema a través del algoritmo de optimización numérica `scipy.optimize.minimize`.\n\n"
             "• **Consistencia Física (Bounds):** Se restringió estrictamente que la resistencia serie fuera mayor a cero ($R_{s,ref} > 0$) y el factor de idealidad estuviese acotado ($n_I \in [1, 2]$) para evitar soluciones irreales.", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Resultados de Parámetros en STC Extraídos")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Silicio Monocristalino (m-Si):**\n"
             "  $I_{L,ref}$ = 2.768 A  |  $I_{0,ref}$ = $4.13 \times 10^{-9}$ A  |  $R_{s,ref}$ = 0.542 $\Omega$  |  $R_{sh,ref}$ = 352.4 $\Omega$\n\n"
             "• **Heterounión (HIT):**\n"
             "  $I_{L,ref}$ = 5.607 A  |  $I_{0,ref}$ = $4.68 \times 10^{-10}$ A  |  $R_{s,ref}$ = 0.412 $\Omega$  |  $R_{sh,ref}$ = 612.8 $\Omega$\n\n"
             "• **Coherencia Física:** La corriente de saturación inversa de HIT es un orden de magnitud menor, demostrando su superioridad frente a la recombinación térmica.", size=16)
    add_footer(slide, 10, TOTAL_SLIDES)

    # --- SLIDE 11: Procedimiento: Traslado Paramétrico y Simulación Minutal ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Procedimiento: Traslado Paramétrico y Simulación Minutal")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Escalamiento Dinámico a Condiciones Reales")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Cálculo Temporal:** Para cada paso de tiempo de los 8,760 intervalos del año 2026, los 5 parámetros fueron escalados a la irradiancia incidente absorbida ($S$) y temperatura de celda ($T_c$) locales.\n\n"
             "• **Traslado de De Soto:** Variación térmica del factor de idealidad ($a$), bandgap del silicio ($E_g$), corrientes de saturación ($I_0$) y fotogenerada ($I_L$).\n\n"
             "• **Resistencia Paralelo:** Modelada inversamente proporcional a la irradiancia. Resistencia serie constante.", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Resolución Implícita del Circuito (MPP)")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• **Resolución Trascendental:** Dado que la corriente ($I$) depende implícitamente del voltaje y de sí misma, se empleó un algoritmo de resolución numérica robusto (`calcparams_desoto` de pvlib).\n\n"
             "• **Búsqueda del MPP Minutal:** Se resolvió numéricamente la curva para encontrar el Punto de Máxima Potencia ($P_{mp,SDM}$) para cada registro del año.\n\n"
             "• **Cómputo de Generación:** Integración de la potencia generada minutalmente para obtener la energía total anual producida por cada tecnología.", size=17)
    add_footer(slide, 11, TOTAL_SLIDES)

    # --- SLIDE 12: d) Desarrollo, análisis crítico y discusión: Recurso Solar y Perfil Térmico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Recurso Solar y Perfil Térmico")
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.9), Inches(5.5), title="Distribución de Temperatura de Celda")
    add_image(slide, 'output/Fase1_Resultados/temp_hist_HIT.png', Inches(0.75), Inches(1.65), width=Inches(6.2), height=Inches(4.65))
    
    add_panel(slide, Inches(7.6), Inches(1.2), Inches(5.333), Inches(5.5), title="Análisis Crítico de Resultados")
    add_text(slide, Inches(7.8), Inches(1.8), Inches(4.933), Inches(4), 
             "• **Estrés Térmico Evidenciado:** El histograma térmico revela que la mayor parte de las horas de sol el panel opera entre 38°C y 50°C, con picos extremos de 65°C a 70°C.\n\n"
             "• **Impacto del Viento Bajo (1 m/s):** La baja velocidad del viento en la modelación reduce el enfriamiento convectivo natural, maximizando el calentamiento térmico de la celda.\n\n"
             "• **Consecuencia Física:** Las altas temperaturas aumentan la corriente de saturación inversa ($I_0$), degradando severamente el voltaje en circuito abierto ($V_{oc}$).", size=17)
    add_footer(slide, 12, TOTAL_SLIDES)

    # --- SLIDE 13: d) Desarrollo, análisis crítico y discusión: Validación del Modelo Eléctrico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Validación del Modelo Eléctrico")
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.6), Inches(5.5), title="Validación: Potencia Medida vs. Simulada")
    add_image(slide, 'output/Fase2_Resultados/val_scatter_HIT.png', Inches(0.7), Inches(1.70), width=Inches(6.0), height=Inches(4.50))
    
    add_panel(slide, Inches(7.3), Inches(1.2), Inches(5.633), Inches(5.5), title="Métricas de Ajuste y Rigor")
    add_text(slide, Inches(7.5), Inches(1.8), Inches(5.233), Inches(4.5), 
             "• **Alta Precisión:** El coeficiente de determinación $R^2 > 0.99$ en la validación experimental cruzada demuestra la alta fidelidad del modelo.\n\n"
             "• **RMSE Reducido:** Error cuadrático medio de la potencia ($RMSE$) inferior a 5W bajo condiciones nominales.\n\n"
             "• **Puntos de Desviación:** El error máximo se concentra en la zona del codo de la curva característica I-V a irradiancias muy bajas.\n\n"
             "• **Fidelidad Térmica:** Valida la capacidad de las ecuaciones físicas de trasladar el voltaje y potencia a condiciones reales.", size=17)
    add_footer(slide, 13, TOTAL_SLIDES)

    # --- SLIDE 14: d) Desarrollo, análisis crítico y discusión: Puntos Conflictuales y Acoplamiento Rs - n ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Puntos Conflictuales y Acoplamiento Rs - n")
    
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.5), Inches(5.5), title="Acoplamiento Rs - factor de idealidad (n)")
    acoplamiento_text = (
        "• **Alta Correlación Paramétrica:**\n"
        "  Tanto la resistencia serie (_R_[_s_]) como el factor de idealidad del diodo (_n_) controlan la curvatura de la curva _I_-_V_ en la región cercana al Punto de Máxima Potencia (MPP).\n\n"
        "• **Problema Mal Condicionado:**\n"
        "  Múltiples combinaciones del par (_R_[_s_], _n_) pueden reproducir curvas _I_-_V_ con errores de ajuste idénticos, lo que dificulta la identificación unívoca.\n\n"
        "• **Mitigación y Solución:**\n"
        "  Se implementaron restricciones físicas estrictas en la optimización por mínimos cuadrados:\n"
        "  _R_[_s_] > 0  |  _n_ ∈ [1.0, 2.0]\n"
        "  Esto asegura consistencia física y convergencia estable."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), Inches(5.1), Inches(4.5), acoplamiento_text, size=14, color=TEXT_WHITE)

    # Columna 2: Limitaciones y Suposiciones
    add_panel(slide, MARGIN + Inches(5.5) + GAP, Inches(1.2), Inches(6.733), Inches(5.5), title="Limitaciones y Suposiciones del Modelo")
    limitaciones_text = (
        "• **Resistencia Shunt (R_sh) e Irradiancia (G):**\n"
        "  La relación _R_[_sh_] = _R_[_sh,ref_] · (_S_[_ref_]/_S_) es empírica. A muy baja irradiancia (amanecer/ocaso), puede sobreestimar la resistencia shunt.\n"
        "  *Impacto:* Despreciable en el PR anual, ya que esas horas representan una fracción mínima de la energía total.\n\n"
        "• **Rs Constante con la Temperatura:**\n"
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
    add_panel(slide, MARGIN, Inches(1.2), Inches(7.6), Inches(5.5), title="Normalización por Potencia Nominal")
    add_image(slide, 'output/Extra_Resultados/degradacion_termica_scatter.png', Inches(0.8), Inches(1.8), width=Inches(6.8))
    
    add_panel(slide, Inches(8.3), Inches(1.2), Inches(4.633), Inches(5.5), title="Observación Científica")
    add_text(slide, Inches(8.5), Inches(1.8), Inches(4.233), Inches(4.5), 
             "• **Heterounión (HIT - Naranja):** Pendiente suave y controlada. Su bajo coeficiente térmico de potencia (-0.26 %/°C) mantiene una alta eficiencia de conversión incluso a temperaturas de 65°C.\n\n"
             "• **Silicio Monocristalino (m-Si - Azul):** Caída térmica severa. Su alto coeficiente térmico (-0.40 %/°C) penaliza drásticamente el voltaje durante las horas pico de irradiancia desértica.\n\n"
             "• **Impacto en PR:** Esta diferencia de comportamiento explica la brecha mensual y anual de rendimiento entre ambas tecnologías.", size=17)
    add_footer(slide, 15, TOTAL_SLIDES)

    # --- SLIDE 16: d) Desarrollo, análisis crítico y discusión: Veredicto Técnico y Económico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "d) Desarrollo y discusión: Veredicto Técnico y Económico")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Veredicto de Rendimiento (PR Anual)")
    verdict = (
        "• **Performance Ratio Anual m-Si:** 84.53%\n\n"
        "• **Performance Ratio Anual HIT:** 86.92%\n\n"
        "• **Diferencia Neta en PR:** **+2.39%** a favor de HIT.\n\n"
        "• **Conclusión Técnica:** La tecnología HIT es categóricamente superior en el desierto debido a que su estructura física de capas delgadas amortigua la pérdida de tensión ($V_{oc}$) debida a la excitación térmica de portadores."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), verdict, size=18, bold=True, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Impacto y Viabilidad en Plantas de 100 MWp")
    impact_text = (
        "• **Generación Adicional:** Para una planta de 100 MWp, cada +1% de PR equivale a ~2,500 MWh de energía extra anual.\n\n"
        "• **Ganancia Total:** El incremento de +2.39% de PR con la tecnología HIT representa **~6,000 MWh/año adicionales**.\n\n"
        "• **Impacto Financiero:** A una tarifa de venta de USD 45/MWh, esto significa una mayor facturación neta de **USD 270,000 anuales**.\n\n"
        "• **Recomendación de Compra:** Se justifica económicamente la inversión en HIT si el costo extra del panel (capex) es inferior a la tasa de amortización de estos ingresos extra en 25 años."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), impact_text, size=16)
    add_footer(slide, 16, TOTAL_SLIDES)

    # --- SLIDE 17: e) Conclusiones y propuestas de trabajos futuros ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "e) Conclusiones y propuestas de trabajos futuros")
    
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Conclusiones del Estudio")
    concl = (
        "1. **Fidelidad Metodológica:** La emulación geográfica y estacional por traslación temporal fue coherente, permitiendo simular Atacama con data de Cocoa.\n\n"
        "2. **Ajuste Robusto:** El modelo De Soto de 5 parámetros reprodujo con alta precisión ($R^2 > 0.99$) el comportamiento del circuito.\n\n"
        "3. **HIT Vencedor:** HIT superó en 2.39% de PR a m-Si por su bajo coeficiente de temperatura de potencia.\n\n"
        "4. **Recomendación:** HIT es técnicamente superior para plantas desérticas de alta irradiancia y alta temperatura."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), concl, size=17, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Propuestas de Trabajos Futuros")
    futur = (
        "• **Integración de Bifacialidad:** Incorporar el aporte de la irradiancia reflejada (albedo desértico, $\rho > 0.25$) en la cara posterior del módulo.\n\n"
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
    refs = ("1. De Soto, W., Klein, S.A., Beckman, W.A. (2006). \"Improvement and validation of a model for photovoltaic array performance.\" Solar Energy 80 (2006) 78–88.\n\n"
            "2. Sandia National Laboratories - Photovoltaic Array Performance Model (Sandia Report SAND2004-3535).\n\n"
            "3. NREL Cocoa Dataset - Experimental Measurements for Model Validation.\n\n"
            "4. pvlib-python Library documentation & community contributors.\n\n"
            "5. Marion, B. et al. (2014). \"Cocoa, Florida Data Set for Validating PV Models.\" NREL Technical Report.\n\n"
            "Agradecimientos al Departamento de Electrotecnia de la UTFSM.")
    add_text(slide, MARGIN, Inches(2), SLIDE_WIDTH - 2*MARGIN, Inches(4), refs, size=18)
    add_footer(slide, 18, TOTAL_SLIDES)


    # ==========================================
    # SECCIÓN DE ANEXOS (ECUACIONES Y MATEMÁTICA)
    # ==========================================

    # --- SLIDE 19: Anexo I: Ecuaciones de Transposición y Absorción Solar ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Anexo I: Ecuaciones de Transposición y Absorción Solar")
    
    # Perez POA
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.5), Inches(5.5), title="Transposición POA (Modelo de Perez)")
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
    add_panel(slide, MARGIN + Inches(5.5) + GAP, Inches(1.2), Inches(6.733), Inches(5.5), title="Absorción en Celda (Pérdidas Ópticas)")
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
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Ángulo de Incidencia (IAM)")
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
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Masa de Aire (AM)")
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
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.0), Inches(5.5), title="Ajuste en STC")
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
    add_panel(slide, Inches(5.7), Inches(1.2), Inches(7.233), Inches(5.5), title="Derivada Analítica Completa en MPP")
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
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Corrientes y Factor de Idealidad")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.70), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "1. Corriente Fotogenerada (_I_[_L_]):", size=15)
    add_latex_equation(slide, r"I_L = \left(\frac{S}{S_{ref}}\right) \cdot \left(\frac{M}{M_{ref}}\right) \cdot \left[ I_{L,ref} + \alpha_{Isc} \cdot (T_c - T_{ref}) \right]", MARGIN + Inches(0.3), Inches(2.05), Inches(0.55))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(2.75), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "2. Corriente de Saturación Inversa (_I_[_0_]):", size=15)
    add_latex_equation(slide, r"\frac{I_0}{I_{0,ref}} = \left(\frac{T_c}{T_{ref}}\right)^3 \cdot \exp\left[ \frac{E_{g,ref}}{k \cdot T_{ref}} - \frac{E_g}{k \cdot T_c} \right]", MARGIN + Inches(0.3), Inches(3.10), Inches(0.58))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(3.85), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "3. Factor de Idealidad térmico (_a_):", size=15)
    add_latex_equation(slide, r"\frac{a}{a_{ref}} = \frac{T_c}{T_{ref}}", MARGIN + Inches(0.3), Inches(4.20), Inches(0.55))
    add_footer(slide, 24, TOTAL_SLIDES)
    
    # Derecha
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Resistencias y Energía de Bandgap")
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
    
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(2.2), title="Ecuación de Rendimiento Global del PR")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.65), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(0.35),
             "El Performance Ratio (_PR_) evalúa la eficiencia neta del sistema fotovoltaico frente a condiciones estándar de referencia:", size=15)
    add_latex_equation(slide, r"PR = \left[ \sum_{t=1}^{N} V_{mp,t}(G_t, T_{c,t}) \cdot I_{mp,t}(G_t, T_{c,t}) \right] ~ / ~ \left[ \sum_{t=1}^{N} P_{STC} \cdot \left(\frac{G_{poa,t}}{G_{ref}}\right) \right]", MARGIN + Inches(0.5), Inches(2.10), Inches(0.75), max_width=Inches(10.73))
    
    # Glosario
    add_panel(slide, MARGIN, Inches(3.6), Inches(5.2), Inches(3.1), title="Glosario de Variables")
    pr_details = (
        "• _V_[_mp,t_] / _I_[_mp,t_]: Tensión y corriente MPP horarias del SDM.\n"
        "• _P_[_STC_]: Potencia nominal del panel en STC (m-Si: 46.68 W | HIT: 217.52 W).\n"
        "• _G_[_poa,t_]: Irradiancia instantánea en el plano del panel (W/m²).\n"
        "• _G_[_ref_]: Irradiancia de referencia a condiciones STC (1000 W/m²)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.10), Inches(4.8), Inches(2.3), pr_details, size=14, color=ACCENT_GOLD)
    
    # Pérdidas
    add_panel(slide, Inches(5.9), Inches(3.6), Inches(7.033), Inches(3.1), title="Pérdidas Penalizadas por el PR")
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
