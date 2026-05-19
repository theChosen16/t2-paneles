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
COLUMN_WIDTH = (SLIDE_WIDTH - (3 * MARGIN)) / 2
GAP = Inches(0.3)

def apply_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG

def add_title(slide, text):
    title_box = slide.shapes.add_textbox(MARGIN, MARGIN, SLIDE_WIDTH - 2*MARGIN, Inches(0.8))
    tf = title_box.text_frame
    add_formatted_paragraph(tf, text, font_size=28, default_color=ACCENT_GOLD, is_first=True)
    p = tf.paragraphs[0]
    for run in p.runs:
        run.font.bold = True
    return title_box

def add_footer(slide, page_num, total_pages=20):
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
    TOTAL_SLIDES = 20

    # --- SLIDE 1: Portada ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_text(slide, MARGIN, Inches(1.8), SLIDE_WIDTH - 2*MARGIN, Inches(1.5), 
             "Evaluación de Tecnologías Fotovoltaicas en el Desierto de Atacama", size=36, bold=True, color=ACCENT_GOLD, align=PP_ALIGN.CENTER)
    
    names_text = ("Integrantes / Estudiantes:\n"
                  "Laury Gualdron  |  Sebastian Marin  |  Alejandro Hernández\n\n"
                  "Profesor Guía: Carlos Cardenas\n"
                  "ELI556 — Modelamiento y Análisis de Sistemas PV  |  Grupo Alta Tensión (AT)")
    add_text(slide, MARGIN, Inches(3.8), SLIDE_WIDTH - 2*MARGIN, Inches(1.8), names_text, size=16, color=TEXT_WHITE, align=PP_ALIGN.CENTER)
    add_footer(slide, 1, TOTAL_SLIDES)

    # --- SLIDE 2: Motivación ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "¿Por qué el Desierto de Atacama?")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Recurso Solar más Extremo")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• Irradiancia GHI anual > 2900 kWh/m² (máxima mundial).\n\n"
             "• Cielos extremadamente limpios con baja atenuación.\n\n"
             "• Altitud elevada (>= 2400 m.s.n.m.): mayor radiación directa y UV.\n\n"
             "• Coordenadas del estudio: Latitud -22.91°, Longitud -68.20°.", size=18)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Desafío Térmico desértico")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• Las celdas solares operan a temperaturas > 65°C a mediodía.\n\n"
             "• La potencia y el voltaje decaen fuertemente con el calor.\n\n"
             "• La eficiencia térmica es el factor dominante en pérdidas.\n\n"
             "• Pregunta: ¿Qué tecnología resiste mejor este estrés extremo?", size=18)
    add_footer(slide, 2, TOTAL_SLIDES)

    # --- SLIDE 3: Comparativa de Tecnologías ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "¿Por qué m-Si y HIT? Comparativa de la Base de Datos")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.5), title="Familias Tecnológicas en Dataset Cocoa (NREL) ^[5]^")
    
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
        ["m-Si / x-Si\n(Silicio Monocristalino / Cristalino)", "17% - 21%", "-0.40 %/°C (Malo)", "Grandes pérdidas por calor (baja tolerancia).", "SELECCIONADO (Línea Base)"],
        ["HIT\n(Heterounión con Capa Fina Intrínseca)", "20% - 22%", "-0.26 %/°C (Excelente)", "Mantiene alta producción bajo estrés térmico.", "SELECCIONADO (Premium)"],
        ["CdTe\n(Teluro de Cadmio)", "15% - 18%", "-0.28 %/°C (Excelente)", "Excelente desempeño, pero posee toxicidad por Cd.", "DESCARTADO (Menor contraste)"],
        ["CIGS\n(Seleniuro de Cobre, Indio y Galio)", "14% - 16%", "-0.35 %/°C (Bueno)", "Pérdidas moderadas; susceptible a la humedad.", "DESCARTADO (Sin contraste extremo)"],
        ["a-Si (Película Fina)\n(Silicio Amorfo)", "6% - 10%", "-0.20 %/°C (Excelente)", "Baja eficiencia base y fuerte degradación inicial.", "DESCARTADO (Inviable comercial)"]
    ]
    
    for c in range(cols):
        cell = table.cell(0, c)
        cell.text = headers[c]
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x2C, 0x2C, 0x48)
        cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(14)  # Aumentado de 13 a 14
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
                p.font.size = Pt(13 if c == 3 else 14)  # Aumentado para mejor legibilidad
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

    # --- SLIDE 4: Metodología ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Metodología: Pipeline de Simulación")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.5), title="Flujo de Procesamiento Automatizado")
    method = ("1. Ingesta de Datos: Dataset NREL Cocoa^[5]^ (mediciones experimentales reales).\n\n"
              "2. Filtro de Emulación Geográfica: Traslación temporal (desfase de 6 meses) y re-localización espacial.\n\n"
              "3. Modelamiento Térmico: Modelo Sandia SAPM^[2]^ para estimación dinámica de la Temperatura de Celda (_T_[_c_]).\n\n"
              "4. Caracterización Eléctrica: Extracción de los 5 parámetros De Soto^[1]^ en SRC usando Scipy Optimize.\n\n"
              "5. Simulación de Desempeño: Traslado de parámetros a operación y cómputo de _PR_ minutal anual usando pvlib-python^[4]^.")
    add_text(slide, MARGIN + Inches(0.5), Inches(1.8), SLIDE_WIDTH - 2*MARGIN - Inches(1), Inches(4.5), method, size=19) # Aumentado de 18 a 19
    add_footer(slide, 4, TOTAL_SLIDES)

    # --- SLIDE 5: Recurso Solar (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Recurso Solar: Transposición y Absorción")
    
    # Columna 1: Plano de Arreglo (POA) (Ancho calibrado a 5.5")
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.5), Inches(5.5), title="Transposición POA (Modelo de Perez)")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), Inches(5.1), Inches(0.35),
             "Calcula la irradiancia incidente total en el panel inclinado:", size=15)
    add_latex_equation(slide, 
                       r"G_{poa} = G_b \cdot R_{beam} + G_d \cdot \left(\frac{1 + \cos(\beta)}{2}\right) + G \cdot \rho \cdot \left(\frac{1 - \cos(\beta)}{2}\right)", 
                       MARGIN + Inches(0.2), Inches(2.20), Inches(0.38), max_width=Inches(5.1))
    poa_glossary = (
        "Donde:\n"
        "• _G_[_b_] / _G_[_d_] / _G_: Irradiancia directa, difusa y global (W/m²).\n"
        "• _β_ (Tilt): Ángulo de inclinación óptimo (22.91°).\n"
        "• _ρ_ (Albedo): Reflectancia del suelo desértico (~0.20).\n"
        "• _R_[_beam_]: Factor de transposición geométrica directa."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(3.20), Inches(5.1), Inches(3.0), poa_glossary, size=15, color=ACCENT_GOLD)
    
    # Columna 2: Absorción en la Celda (S) (Ancho calibrado a 6.2")
    add_panel(slide, MARGIN + Inches(5.5) + GAP, Inches(1.2), Inches(6.2), Inches(5.5), title="Absorción en Celda (Pérdidas Ópticas)")
    add_text(slide, MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(1.7), Inches(5.8), Inches(0.35),
             "Modela la radiación real que penetra y es absorbida por la celda:", size=15)
    eq_multiline = (
        r"$\frac{S}{S_{ref}} = \frac{G_b}{G_{ref}} \cdot R_{beam} \cdot K_{\tau\alpha,b}$" + "\n" +
        r"$\quad + \frac{G_d}{G_{ref}} \cdot K_{\tau\alpha,d} \cdot \left(\frac{1 + \cos(\beta)}{2}\right)$" + "\n" +
        r"$\quad + \frac{G}{G_{ref}} \cdot \rho \cdot K_{\tau\alpha,g} \cdot \left(\frac{1 - \cos(\beta)}{2}\right)$"
    )
    add_latex_equation(slide, eq_multiline, 
                       MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(2.05), Inches(1.40), max_width=Inches(5.8))
    abs_glossary = (
        "Donde:\n"
        "• _S_ / _S_[_ref_]: Irradiancia efectiva y de referencia (1000 W/m²).\n"
        "• _K_[_τα,b_] / _K_[_τα,d_] / _K_[_τα,g_]: Modificadores por IAM para directa, difusa y albedo.\n"
        "• Incorpora las pérdidas ópticas por ángulo de incidencia^[2]^."
    )
    add_text(slide, MARGIN + Inches(5.5) + GAP + Inches(0.2), Inches(3.65), Inches(5.8), Inches(2.6), abs_glossary, size=16)
    add_footer(slide, 5, TOTAL_SLIDES)

    # --- SLIDE 6: Modificadores IAM y Air Mass (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Modificadores Ópticos: IAM y Masa de Aire")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Ángulo de Incidencia (IAM) ^[2]^")
    
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "Ecuación física basada en Ley de Snell y Bouguer:", size=15)
    add_latex_equation(slide, r"K_{\tau\alpha}(\theta) = \frac{\tau(\theta)}{\tau(0)}", MARGIN + Inches(0.3), Inches(2.10), Inches(0.45))
    add_latex_equation(slide, r"\tau(\theta) = e^{-\frac{K \cdot L}{\cos(\theta_r)}} \cdot \left[ 1 - \frac{1}{2} \left( \frac{\sin^2(\theta_r - \theta)}{\sin^2(\theta_r + \theta)} + \frac{\tan^2(\theta_r - \theta)}{\tan^2(\theta_r + \theta)} \right) \right]", MARGIN + Inches(0.3), Inches(2.70), Inches(0.45))
    add_latex_equation(slide, r"\theta_r = \arcsin\left(\frac{\sin(\theta)}{n}\right)", MARGIN + Inches(0.3), Inches(3.45), Inches(0.40))
    
    iam_details = (
        "Donde:\n"
        "• _θ_: Ángulo de incidencia  |  _n_ = 1.526 (Índice refracción vidrio).\n"
        "• _K_ = 4 m⁻¹ (Absorción del vidrio)  |  _L_ = 2 mm (Espesor vidrio)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.30), COLUMN_WIDTH - Inches(0.4), Inches(2.0), iam_details, size=15, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Masa de Aire (AM) ^[2]^")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.65), COLUMN_WIDTH - Inches(0.4), Inches(0.55),
             "Corrige el desajuste del espectro solar según la atmósfera atravesada:", size=15)
    add_latex_equation(slide, r"\frac{M}{M_{ref}} = a_0 + a_1 \cdot AM + a_2 \cdot AM^2 + a_3 \cdot AM^3 + a_4 \cdot AM^4", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(2.35), Inches(0.40))
    add_latex_equation(slide, r"AM = \frac{1}{\cos(\theta_z) + 0.5057 \cdot (96.08 - \theta_z)^{-1.634}}", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(3.10), Inches(0.48))
    
    am_details = (
        "Donde:\n"
        "• _AM_: Masa de aire absoluta  |  _θ_[_z_]: Ángulo cenital del sol.\n"
        "• _a_[_0_], _a_[_1_], _a_[_2_], _a_[_3_], _a_[_4_]: Coeficientes empíricos espectrales.\n"
        "• _M_[_ref_]: Transmitancia espectral a STC (AM 1.5g)."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(4.10), COLUMN_WIDTH - Inches(0.4), Inches(2.5), am_details, size=15)
    add_footer(slide, 6, TOTAL_SLIDES)

    # --- SLIDE 7: Perfil Diario (Imagen) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Dinámica Horaria: Irradiancia en Día Despejado")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.8))
    add_image(slide, 'output/Extra_Resultados/perfil_dia_tipico.png', Inches(1.0), Inches(1.35), width=Inches(11.33), height=Inches(5.4))
    add_footer(slide, 7, TOTAL_SLIDES)

    # --- SLIDE 8: Modelamiento Térmico (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Temperatura de Celda (Sandia SAPM) ^[2]^")
    
    # Segmento Superior: Ecuación Principal (Ancho Completo)
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(2.2), title="Ecuación del Modelo Térmico")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.65), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(0.35),
             "La temperatura interna de la celda (_T_[_c_]) depende de la irradiancia incidente y de la velocidad del viento:", size=15)
    add_latex_equation(slide, r"T_c = G_{poa} \cdot e^{a + b \cdot v_w} + T_a + \left(\frac{G_{poa}}{1000}\right) \cdot \Delta T", MARGIN + Inches(1.8), Inches(2.15), Inches(0.55))
    
    # Segmento Inferior: Dos Paneles Asimétricos
    # Panel Izquierdo (Glosario)
    add_panel(slide, MARGIN, Inches(3.6), Inches(5.0), Inches(3.1), title="Glosario de Variables")
    thermal_details = (
        "• _T_[_c_] / _T_[_a_]: Temp. de celda y ambiental (°C).\n"
        "• _G_[_poa_]: Irradiancia en plano de panel (W/m²).\n"
        "• _v_[_w_]: Velocidad del viento local (m/s).\n"
        "• _a_, _b_, _ΔT_: Parámetros empíricos del encapsulado."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.10), Inches(4.6), Inches(2.3), thermal_details, size=15, color=ACCENT_GOLD)
    
    # Panel Derecho (Coeficientes)
    add_panel(slide, MARGIN + Inches(5.0) + GAP, Inches(3.6), Inches(6.7), Inches(3.1), title="Coeficientes Empíricos por Tecnología")
    thermal_coef = (
        "• **Silicio Monocristalino (m-Si) — glass/polymer:**\n"
        "  _a_ = -3.56  |  _b_ = -0.075  |  _ΔT_ = 3.0 °C\n"
        "  → Comportamiento: Disipación estándar, mayor calentamiento.\n\n"
        "• **Heterounión (HIT) — glass/glass:**\n"
        "  _a_ = -3.47  |  _b_ = -0.059  |  _ΔT_ = 3.0 °C\n"
        "  → Comportamiento: Retiene más calor, pero se compensa por su bajo coeficiente térmico."
    )
    add_text(slide, MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(4.10), Inches(6.3), Inches(2.3), thermal_coef, size=14)
    add_footer(slide, 8, TOTAL_SLIDES)

    # --- SLIDE 9: Histograma Térmico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Resultados Térmicos: Distribución Anual Tc")
    add_panel(slide, MARGIN, Inches(1.2), Inches(7), Inches(5.5), title="Distribución de Temperatura de Celda")
    add_image(slide, 'output/Fase1_Resultados/temp_hist_HIT.png', Inches(1.0), Inches(1.65), width=Inches(6.6), height=Inches(4.95))
    
    add_panel(slide, Inches(7.5), Inches(1.2), Inches(5.4), Inches(5.5), title="Comportamiento en Atacama")
    add_text(slide, Inches(7.7), Inches(1.8), Inches(5), Inches(4), 
             "• Temperatura promedio diurna de celda: ~38°C a 45°C.\n\n"
             "• Picos térmicos extremos superan los 65°C a mediodía en verano.\n\n"
             "• Clima desértico seco reduce la convección natural del marco.\n\n"
             "• Las altas temperaturas aumentan la corriente de saturación inversa (_I_[_0_]), reduciendo severamente el _V_[_oc_].", size=17) # Aumentado a 17
    add_footer(slide, 9, TOTAL_SLIDES)

    # --- SLIDE 10: Modelo de 5 Parámetros (SDM) (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Modelo de 5 Parámetros: Diodo Simple (SDM) ^[1]^")
    
    # Segmento Superior: Ecuación del Circuito Equivalente (Ancho Completo)
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(2.2), title="Ecuación del Circuito Equivalente")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.65), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(0.35),
             "El comportamiento eléctrico del módulo se modela mediante la ecuación trascendental del diodo:", size=15)
    add_latex_equation(slide, r"I = I_L - I_0 \cdot \left[ \exp\left(\frac{V + I \cdot R_s}{a}\right) - 1 \right] - \frac{V + I \cdot R_s}{R_{sh}}", MARGIN + Inches(1.2), Inches(2.15), Inches(0.42))
    
    # Segmento Inferior: Dos Paneles
    # Panel Izquierdo: Factor de Idealidad Térmico (a)
    add_panel(slide, MARGIN, Inches(3.6), Inches(5.4), Inches(3.1), title="Factor de Idealidad Térmico (a)")
    add_text(slide, MARGIN + Inches(0.2), Inches(4.0), Inches(5.0), Inches(0.35),
             "El factor de idealidad térmico se define formalmente como:", size=15)
    add_latex_equation(slide, r"a = \frac{N_s \cdot n_I \cdot k \cdot T_c}{q}", MARGIN + Inches(0.5), Inches(4.55), Inches(0.48))
    add_text(slide, MARGIN + Inches(0.2), Inches(5.25), Inches(5.0), Inches(1.0),
             "Donde _N_[_s_] es el número de celdas en serie (m-Si: 36, HIT: 72).", size=14, color=ACCENT_GOLD)
    
    # Panel Derecho: Glosario de Parámetros Físicos
    add_panel(slide, MARGIN + Inches(5.4) + GAP, Inches(3.6), Inches(6.3), Inches(3.1), title="Glosario de Parámetros Físicos")
    sdm_glossary = (
        "• _I_ / _V_: Corriente y voltaje de salida (A, V).\n"
        "• _I_[_L_] / _I_[_0_]: Corrientes fotogenerada y de saturación (A).\n"
        "• _R_[_s_] / _R_[_sh_]: Resistencia serie (pérdidas) y paralelo (fugas) (Ω).\n"
        "• _k_ / _q_ / _T_[_c_]: Constante de Boltzmann, carga elemental y Temp. (K)."
    )
    add_text(slide, MARGIN + Inches(5.4) + GAP + Inches(0.2), Inches(4.0), Inches(5.9), Inches(2.3), sdm_glossary, size=14)
    add_footer(slide, 10, TOTAL_SLIDES)

    # --- SLIDE 11: Extracción en SRC (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Extracción de Parámetros de Referencia")
    
    # Columna 1: Extracción STC (Más estrecha)
    add_panel(slide, MARGIN, Inches(1.2), Inches(5.0), Inches(5.5), title="Extracción en STC ^[1]^")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), Inches(4.6), Inches(1.5),
             "Se extraen _a_[_ref_], _I_[_L,ref_], _I_[_0,ref_], _R_[_s,ref_], _R_[_sh,ref_] en STC:\n\n"
             "1. Cortocircuito: _V_ = 0, _I_ = _I_[_sc,ref_]\n"
             "2. Circuito Abierto: _I_ = 0, _V_ = _V_[_oc,ref_]\n"
             "3. Máxima Potencia: _I_ = _I_[_mp,ref_], _V_ = _V_[_mp,ref_]\n"
             "4. Pendiente en MPP (d_P_/d_V_ = 0):", size=14)
    add_latex_equation(slide, r"\left.\frac{dI}{dV}\right|_{mp} = -\frac{I_{mp,ref}}{V_{mp,ref}}", MARGIN + Inches(0.2), Inches(3.55), Inches(0.42), max_width=Inches(4.6))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(4.15), Inches(4.6), Inches(0.35),
             "5. Coeficiente térmico de _V_[_oc_]:", size=14)
    add_latex_equation(slide, r"\beta_{Voc} = \frac{\partial V_{oc}}{\partial T_c}", MARGIN + Inches(0.2), Inches(4.55), Inches(0.40), max_width=Inches(4.6))
    
    # Columna 2: Derivada Analítica en MPP (Más ancha)
    add_panel(slide, MARGIN + Inches(5.0) + GAP, Inches(1.2), Inches(6.7), Inches(5.5), title="Derivada Analítica en MPP")
    add_text(slide, MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(1.7), Inches(6.3), Inches(0.6),
             "Para acoplar _R_[_s_] y el factor de idealidad, se implementa la derivada analítica obtenida del circuito:", size=14)
    add_latex_equation(slide, r"\left.\frac{dI}{dV}\right|_{mp} = -\frac{A + B}{1 + R_s \cdot A + R_s \cdot B}", MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(2.35), Inches(0.48))
    
    add_text(slide, MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(3.10), Inches(6.3), Inches(0.35),
             "Donde los coeficientes se definen como:", size=14)
    add_latex_equation(slide, r"A = \frac{I_0}{a} \cdot e^{\frac{V_{mp} + I_{mp} \cdot R_s}{a}}", MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(3.55), Inches(0.45))
    add_latex_equation(slide, r"B = \frac{1}{R_{sh}}", MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(4.15), Inches(0.35))
    
    add_text(slide, MARGIN + Inches(5.0) + GAP + Inches(0.2), Inches(4.85), Inches(6.3), Inches(1.0),
             "La optimización se realiza mediante ajuste de mínimos cuadrados con bounds físicos (_R_[_s_] > 0, _n_[_I_] ∈ [1, 2]).", size=14, color=ACCENT_GOLD)
    add_footer(slide, 11, TOTAL_SLIDES)

    # --- SLIDE 12: Ecuaciones de Escalado (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Escalamiento a Condiciones Reales")
    
    # Columna 1: Corrientes y Factor de Idealidad
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Corrientes y Factor de Idealidad ^[1]^")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "1. Corriente Fotogenerada (_I_[_L_]):", size=15)
    add_latex_equation(slide, r"I_L = \left(\frac{S}{S_{ref}}\right) \cdot \left(\frac{M}{M_{ref}}\right) \cdot \left[ I_{L,ref} + \alpha_{Isc} \cdot (T_c - T_{ref}) \right]", MARGIN + Inches(0.3), Inches(2.05), Inches(0.38))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(2.70), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "2. Corriente de Saturación Inversa (_I_[_0_]):", size=15)
    add_latex_equation(slide, r"\frac{I_0}{I_{0,ref}} = \left(\frac{T_c}{T_{ref}}\right)^3 \cdot \exp\left[ \frac{E_{g,ref}}{k \cdot T_{ref}} - \frac{E_g}{k \cdot T_c} \right]", MARGIN + Inches(0.3), Inches(3.05), Inches(0.42))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(3.80), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "3. Factor de Idealidad térmico (_a_):", size=15)
    add_latex_equation(slide, r"\frac{a}{a_{ref}} = \frac{T_c}{T_{ref}}", MARGIN + Inches(0.3), Inches(4.15), Inches(0.35))
    
    scale_notes = (
        "Donde:\n"
        "• _T_[_ref_] = 298.15 K (25°C)  |  _S_[_ref_] = 1000 W/m².\n"
        "• _M_[_ref_]: Transmitancia espectral a STC."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.80), COLUMN_WIDTH - Inches(0.4), Inches(2.0), scale_notes, size=15, color=ACCENT_GOLD)
    
    # Columna 2: Resistencias y Energía de Bandgap
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Resistencias y Energía de Bandgap ^[1]^")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "4. Resistencia Shunt (_R_[_sh_]):", size=15)
    add_latex_equation(slide, r"R_{sh} = R_{sh,ref} \cdot \left(\frac{S_{ref}}{S}\right)", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(2.05), Inches(0.35))
    
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(2.70), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "5. Energía de Bandgap del Silicio (_E_[_g_]):", size=15)
    add_latex_equation(slide, r"\frac{E_g}{E_{g,ref}} = 1 - 0.0002677 \cdot (T_c - T_{ref})", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(3.05), Inches(0.36))
    
    scale_just = (
        "Suposiciones Físicas Justificadas:\n"
        "• _R_[_s_] Constante: Se asume _R_[_s_] = _R_[_s,ref_].\n"
        "  La variación térmica de _R_[_s_] es de segundo orden y su efecto en la curva _I_-_V_ es despreciable.\n\n"
        "• _R_[_sh_] dependiente de la Irradiancia Absorbida:\n"
        "  Sigue la relación inversamente proporcional con _S_ para modelar fugas asociadas a portadores minoritarios.\n\n"
        "• _E_[_g,ref_] = 1.121 eV para Silicio a 25°C."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(3.80), COLUMN_WIDTH - Inches(0.4), Inches(3.0), scale_just, size=15)
    add_footer(slide, 12, TOTAL_SLIDES)

    # --- SLIDE 13: Validación curvas IV/PV ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Validación: Reconstrucción Curvas IV en SRC")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.8))
    add_image(slide, 'output/Extra_Resultados/curvas_iv_pv_src.png', Inches(1.66), Inches(1.4), width=Inches(10))
    add_footer(slide, 13, TOTAL_SLIDES)

    # --- SLIDE 14: Validación Scatter ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Validación: Potencia Medida vs. Simulada")
    add_panel(slide, MARGIN, Inches(1.2), Inches(6.5), Inches(5.5), title="Correlación de Potencia")
    add_image(slide, 'output/Fase2_Resultados/val_scatter_HIT.png', MARGIN + Inches(0.2), Inches(1.8), width=Inches(4.5))
    
    add_panel(slide, Inches(7), Inches(1.2), Inches(5.9), Inches(5.5), title="Métricas de Ajuste")
    add_text(slide, Inches(7.2), Inches(1.8), Inches(5.5), Inches(4), 
             "• Coeficiente de determinación R² > 0.99 para ambas tecnologías.\n\n"
             "• RMSE < 5W en condiciones estándar.\n\n"
             "• Validación cruzada: El modelo de De Soto reproduce con alta fidelidad las pérdidas por temperatura en celdas de silicio.\n\n"
             "• Error máximo concentrado en la zona de codo a baja irradiancia.", size=17) # Aumentado a 17
    add_footer(slide, 14, TOTAL_SLIDES)

    # --- SLIDE 15: Performance Ratio (Ecuación) (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Performance Ratio: Evaluación de Desempeño")
    
    # Segmento Superior: Ecuación Matemática del PR (Ancho Completo)
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(2.2), title="Ecuación Matemática del PR")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.65), SLIDE_WIDTH - 2*MARGIN - Inches(0.4), Inches(0.35),
             "El Performance Ratio (_PR_) evalúa la eficiencia neta del sistema fotovoltaico frente a condiciones de referencia STC:", size=15)
    add_latex_equation(slide, r"PR = \frac{\sum P_{mp,SDM}(G, T_c)}{\sum \left[ P_{STC} \cdot \left(\frac{G_{poa}}{1000}\right) \right]}", MARGIN + Inches(1.8), Inches(2.15), Inches(0.55))
    
    # Segmento Inferior: Dos Paneles
    # Panel Izquierdo: Glosario
    add_panel(slide, MARGIN, Inches(3.6), Inches(5.2), Inches(3.1), title="Glosario de Variables")
    pr_details = (
        "• _P_[_mp,SDM_]: Potencia MPP simulada hora a hora con De Soto^[1]^ (W).\n"
        "• _P_[_STC_]: Potencia nominal en STC (m-Si: 46.68 W | HIT: 217.52 W).\n"
        "• _G_[_poa_]: Irradiancia calculada en el plano del panel (W/m²).\n"
        "• 1000: Irradiancia de referencia a STC (W/m²)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(4.10), Inches(4.8), Inches(2.3), pr_details, size=14, color=ACCENT_GOLD)
    
    # Panel Derecho: Pérdidas Penalizadas
    add_panel(slide, MARGIN + Inches(5.2) + GAP, Inches(3.6), Inches(6.5), Inches(3.1), title="Pérdidas Penalizadas por el PR")
    pr_phys = (
        "• **Pérdidas Térmicas:** Caídas debidas a la elevada temperatura _T_[_c_].\n"
        "• **Pérdidas Ópticas:** Efectos reflectivos por ángulo de incidencia (IAM).\n"
        "• **Pérdidas Espectrales:** Desajustes causados por la Masa de Aire (AM).\n"
        "• **Pérdidas Óhmicas:** Pérdidas resistivas en la resistencia serie _R_[_s_]."
    )
    add_text(slide, MARGIN + Inches(5.2) + GAP + Inches(0.2), Inches(4.10), Inches(6.1), Inches(2.3), pr_phys, size=15)
    add_footer(slide, 15, TOTAL_SLIDES)

    # --- SLIDE 16: PR Mensual ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Resultados: Performance Ratio Mensual")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.8))
    add_image(slide, 'output/Extra_Resultados/pr_mensual_comparativo.png', Inches(1.0), Inches(1.35), width=Inches(11.33), height=Inches(5.4))
    add_footer(slide, 16, TOTAL_SLIDES)

    # --- SLIDE 17: Sensibilidad Térmica ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Análisis: Sensibilidad Térmica Realizada")
    add_panel(slide, MARGIN, Inches(1.2), Inches(8), Inches(5.5), title="Normalización por Potencia Nominal")
    add_image(slide, 'output/Extra_Resultados/degradacion_termica_scatter.png', MARGIN + Inches(0.2), Inches(1.8), width=Inches(6.8))
    
    add_panel(slide, Inches(8.3), Inches(1.2), Inches(4.6), Inches(5.5), title="Observación Científica")
    add_text(slide, Inches(8.5), Inches(1.8), Inches(4.2), Inches(4.5), 
             "• HIT (Naranja): Pendiente suave. Su bajo coeficiente térmico (-0.26 %/°C) mantiene una alta eficiencia de conversión incluso a 65°C de celda.\n\n"
             "• m-Si (Azul): Caída térmica severa. Su coeficiente térmico (-0.40 %/°C) penaliza fuertemente el voltaje en las horas pico de irradiancia desértica.", size=17) # Aumentado a 17
    add_footer(slide, 17, TOTAL_SLIDES)

    # --- SLIDE 18: Resultados Anuales y Veredicto ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Resultados Anuales: m-Si vs. HIT en Atacama")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Veredicto Técnico")
    
    verdict = (
        "• Performance Ratio Anual m-Si: 84.53%\n\n"
        "• Performance Ratio Anual HIT: 86.92%\n\n"
        "• Ganancia Neta en _PR_: +2.39% a favor de HIT.\n\n"
        "El módulo HIT entrega un 2.39% más de energía útil por cada watt pico instalado, gracias a su menor caída térmica bajo el calor extremo del Desierto de Atacama en 2026."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), verdict, size=18, bold=True, color=ACCENT_GOLD) # Aumentado a 18
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Impacto en Proyectos a Gran Escala")
    impact_text = (
        "Para una planta solar de gran escala de 100 MWp:\n\n"
        "• Cada +1% de Performance Ratio anual representa aproximadamente 2,500 MWh adicionales de generación de energía.\n\n"
        "• La ganancia de +2.39% de la tecnología HIT equivale a ~6,000 MWh/año adicionales de facturación neta.\n\n"
        "• Se justifica técnicamente la inversión en tecnología premium HIT para climas desérticos de alta irradiancia y alta temperatura."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), impact_text, size=17) # Aumentado a 17
    add_footer(slide, 18, TOTAL_SLIDES)

    # --- SLIDE 19: Conclusiones y Trabajos Futuros ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Conclusiones y Proyecciones")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Conclusiones del Estudio")
    
    concl = (
        "1. La emulación geográfica (Cocoa → Atacama) fue coherente, permitiendo evaluar el Performance Ratio real.\n\n"
        "2. El modelo De Soto de 5 parámetros reprodujo con altísima precisión (R² > 0.99) el desempeño medido.\n\n"
        "3. La tecnología HIT supera en un 2.39% de _PR_ anual al silicio monocristalino estándar.\n\n"
        "4. El coeficiente de temperatura es el factor dominante en el diseño solar desértico."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), concl, size=17, color=ACCENT_GOLD) # Aumentado a 17
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Trabajos Futuros")
    futur = (
        "• Integración de Bifacialidad: Modelar la ganancia por albedo posterior del suelo desértico (_ρ_ > 0.25).\n\n"
        "• Estudio de doble diodo: Capturar efectos de recombinación interna a baja irradiancia.\n\n"
        "• Pérdidas por acumulación de polvo (soiling) en el Desierto de Atacama.\n\n"
        "• Análisis de costo nivelado LCOE para evaluar el retorno de la inversión de paneles premium HIT."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), futur, size=16) # Aumentado a 16
    add_footer(slide, 19, TOTAL_SLIDES)

    # --- SLIDE 20: Referencias ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Referencias y Agradecimientos")
    refs = ("1. De Soto, W., Klein, S.A., Beckman, W.A. (2006). \"Improvement and validation of a model for photovoltaic array performance.\" Solar Energy 80 (2006) 78–88.\n\n"
            "2. Sandia National Laboratories - Photovoltaic Array Performance Model (Sandia Report SAND2004-3535).\n\n"
            "3. NREL Cocoa Dataset - Experimental Measurements for Model Validation.\n\n"
            "4. pvlib-python Library documentation & community contributors.\n\n"
            "5. Marion, B. et al. (2014). \"Cocoa, Florida Data Set for Validating PV Models.\" NREL Technical Report.\n\n"
            "Agradecimientos al Departamento de Electrotecnia de la UTFSM.")
    add_text(slide, MARGIN, Inches(2), SLIDE_WIDTH - 2*MARGIN, Inches(4), refs, size=18) # Aumentado a 18
    add_footer(slide, 20, TOTAL_SLIDES)

    # --- Guardar ---
    output_path = "output/Presentacion_Final_ELI556_Atacama.pptx"
    prs.save(output_path)
    print(f"Presentación corregida guardada en: {output_path}")

if __name__ == "__main__":
    create_presentation()
