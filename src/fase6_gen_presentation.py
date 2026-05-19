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
    p = tf.paragraphs[0]
    p.text = text
    p.font.bold = True
    p.font.size = Pt(28)
    p.font.color.rgb = ACCENT_GOLD
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
        box = slide.shapes.add_textbox(left + Inches(0.1), top + Inches(0.1), width - Inches(0.2), Inches(0.4))
        p = box.text_frame.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = ACCENT_GOLD
    
    return rect

def add_text(slide, left, top, width, height, text, size=14, bold=False, color=TEXT_WHITE, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.alignment = align
    return box

def add_image(slide, img_path, left, top, width=None, height=None):
    if os.path.exists(img_path):
        return slide.shapes.add_picture(img_path, left, top, width=width, height=height)
    return None

def add_latex_equation(slide, formula_text, left, top, height, color='#E8A838', dpi=300):
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
    add_text(slide, MARGIN, Inches(3.2), SLIDE_WIDTH - 2*MARGIN, Inches(0.8), 
             "Modelamiento Eléctrico mediante el Modelo de 5 Parámetros de De Soto", size=20, align=PP_ALIGN.CENTER)
    
    names_text = ("Integrantes / Estudiantes:\n"
                  "Laury Gualdron  |  Sebastian Marin  |  Alejandro Hernández\n\n"
                  "Profesor Guía: Carlos Cardenas\n"
                  "ELI556 — Modelamiento y Análisis de Sistemas PV  |  Grupo Alta Tensión (AT)")
    add_text(slide, MARGIN, Inches(4.5), SLIDE_WIDTH - 2*MARGIN, Inches(1.8), names_text, size=15, color=TEXT_WHITE, align=PP_ALIGN.CENTER)
    add_footer(slide, 1, TOTAL_SLIDES)

    # --- SLIDE 2: Motivación ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "¿Por qué el Desierto de Atacama?")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Recurso Solar más Extremo")
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• Irradiancia GHI anual > 2900 kWh/m² (máxima mundial).\n"
             "• Cielos extremadamente limpios con baja atenuación.\n"
             "• Altitud elevada (>= 2400 m.s.n.m.): mayor radiación directa y UV.\n"
             "• Coordenadas del estudio: Latitud -22.91°, Longitud -68.20°.", size=17)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="El Desafío Térmico desértico")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4), 
             "• Las celdas solares operan a temperaturas > 65°C a mediodía.\n"
             "• La potencia y el voltaje decaen fuertemente con el calor.\n"
             "• La eficiencia térmica es el factor dominante en pérdidas.\n"
             "• Pregunta: ¿Qué tecnología resiste mejor este estrés extremo?", size=17)
    add_footer(slide, 2, TOTAL_SLIDES)

    # --- SLIDE 3: Comparativa de Tecnologías ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "¿Por qué m-Si y HIT? Comparativa de la Base de Datos")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.5), title="Familias Tecnológicas en Dataset Cocoa (NREL)")
    
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
    
    table.columns[0].width = Inches(2.0)
    table.columns[1].width = Inches(1.2)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(4.3)
    table.columns[4].width = Inches(2.8)
    
    headers = ["Tecnología", "Eficiencia", "Coef. Temp. (Pmp)", "Comportamiento en Desierto", "Decisión / Rol"]
    data = [
        ["m-Si / x-Si", "17% - 21%", "-0.40 %/°C (Malo)", "Grandes pérdidas por calor (baja tolerancia).", "SELECCIONADO (Línea Base)"],
        ["HIT", "20% - 22%", "-0.26 %/°C (Excelente)", "Mantiene alta producción bajo estrés térmico.", "SELECCIONADO (Premium)"],
        ["CdTe", "15% - 18%", "-0.28 %/°C (Excelente)", "Excelente desempeño, pero posee toxicidad por Cd.", "DESCARTADO (Menor contraste)"],
        ["CIGS", "14% - 16%", "-0.35 %/°C (Bueno)", "Pérdidas moderadas; susceptible a la humedad.", "DESCARTADO (Sin contraste extremo)"],
        ["a-Si (Película Fina)", "6% - 10%", "-0.20 %/°C (Excelente)", "Baja eficiencia base y fuerte degradación inicial.", "DESCARTADO (Inviable comercial)"]
    ]
    
    for c in range(cols):
        cell = table.cell(0, c)
        cell.text = headers[c]
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x2C, 0x2C, 0x48)
        cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(13)
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
                p.font.size = Pt(10.5 if c == 3 else 11.5)
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
    method = ("1. Ingesta de Datos: Dataset NREL Cocoa (mediciones experimentales reales).\n\n"
              "2. Filtro de Emulación Geográfica: Traslación temporal (desfase de 6 meses) y re-localización espacial.\n\n"
              "3. Modelamiento Térmico: Modelo Sandia SAPM para estimación dinámica de la Temperatura de Celda (Tc).\n\n"
              "4. Caracterización Eléctrica: Extracción de los 5 parámetros De Soto en SRC usando Scipy Optimize.\n\n"
              "5. Simulación de Desempeño: Traslado de parámetros a operación y cómputo de PR minutal anual.")
    add_text(slide, MARGIN + Inches(0.5), Inches(1.8), SLIDE_WIDTH - 2*MARGIN - Inches(1), Inches(4.5), method, size=18)
    add_footer(slide, 4, TOTAL_SLIDES)

    # --- SLIDE 5: Recurso Solar (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Recurso Solar: Transposición y Absorción")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Fórmulas POA (Perez) y Absorción")
    
    # 1. Irradiancia en Plano de Arreglo (POA)
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "1. Irradiancia en Plano de Arreglo (POA):", size=13, color=TEXT_WHITE)
    add_latex_equation(slide, 
                       r"G_{poa} = G_b \cdot R_{beam} + G_d \cdot \left(\frac{1 + \cos(\beta)}{2}\right) + G \cdot \rho \cdot \left(\frac{1 - \cos(\beta)}{2}\right)", 
                       MARGIN + Inches(0.3), Inches(2.1), Inches(0.38))
    
    # 2. Irradiancia Absorbida por Celdas (S) - Altura optimizada a 0.3 para evitar que desborde de la columna
    add_text(slide, MARGIN + Inches(0.2), Inches(2.8), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "2. Irradiancia Absorbida por Celdas (S):", size=13, color=TEXT_WHITE)
    add_latex_equation(slide, 
                       r"\frac{S}{S_{ref}} = \frac{G_b}{G_{ref}} \cdot R_{beam} \cdot K_{\tau\alpha,b} + \frac{G_d}{G_{ref}} \cdot K_{\tau\alpha,d} \cdot \left(\frac{1 + \cos(\beta)}{2}\right) + \frac{G}{G_{ref}} \cdot \rho \cdot K_{\tau\alpha,g} \cdot \left(\frac{1 - \cos(\beta)}{2}\right)", 
                       MARGIN + Inches(0.3), Inches(3.2), Inches(0.30))
    
    # Donde S_ref ...
    add_text(slide, MARGIN + Inches(0.2), Inches(4.1), COLUMN_WIDTH - Inches(0.4), Inches(2.0),
             "Donde S_ref = G_ref = 1000 W/m² en condiciones de referencia (SRC).", size=13, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Glosario de Términos")
    glossary = (
        "• G_b / G_d / G: Irradiancia directa, difusa y global horizontal (W/m²).\n"
        "• β (Tilt): Ángulo de inclinación del panel (22.91° optimizado).\n"
        "• ρ (Albedo): Reflectancia del suelo árido desértico (~0.20).\n"
        "• R_beam: Factor de transposición geométrica para radiación directa.\n"
        "• K_τα,b / K_τα,d / K_τα,g: Modificadores por ángulo de incidencia (IAM) para componente directa, difusa y del suelo."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), glossary, size=13)
    add_footer(slide, 5, TOTAL_SLIDES)

    # --- SLIDE 6: Modificadores IAM y Air Mass (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Modificadores Ópticos: IAM y Masa de Aire")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Ángulo de Incidencia (IAM)")
    
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "Ecuación física basada en Ley de Snell y Bouguer:", size=12)
    add_latex_equation(slide, r"K_{\tau\alpha}(\theta) = \frac{\tau(\theta)}{\tau(0)}", MARGIN + Inches(0.3), Inches(2.1), Inches(0.34))
    # Altura optimizada a 0.34 para evitar que desborde de la columna
    add_latex_equation(slide, r"\tau(\theta) = e^{-\frac{K \cdot L}{\cos(\theta_r)}} \cdot \left[ 1 - \frac{1}{2} \left( \frac{\sin^2(\theta_r - \theta)}{\sin^2(\theta_r + \theta)} + \frac{\tan^2(\theta_r - \theta)}{\tan^2(\theta_r + \theta)} \right) \right]", MARGIN + Inches(0.3), Inches(2.6), Inches(0.34))
    add_latex_equation(slide, r"\theta_r = \arcsin\left(\frac{\sin(\theta)}{n}\right)", MARGIN + Inches(0.3), Inches(3.25), Inches(0.3))
    
    iam_details = (
        "Donde:\n"
        "• θ: Ángulo de incidencia solar.\n"
        "• n = 1.526 (Índice de refracción del vidrio templado).\n"
        "• K = 4 m⁻¹ (Absorción del vidrio).\n"
        "• L = 2 mm (Espesor típico del vidrio)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(3.7), COLUMN_WIDTH - Inches(0.4), Inches(2.5), iam_details, size=11, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Masa de Aire (AM)")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "Corrige el desajuste del espectro solar según la atmósfera atravesada:", size=12)
    add_latex_equation(slide, r"\frac{M}{M_{ref}} = a_0 + a_1 \cdot AM + a_2 \cdot AM^2 + a_3 \cdot AM^3 + a_4 \cdot AM^4", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(2.2), Inches(0.34))
    add_latex_equation(slide, r"AM = \frac{1}{\cos(\theta_z) + 0.5057 \cdot (96.08 - \theta_z)^{-1.634}}", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(2.75), Inches(0.4))
    
    am_details = (
        "Donde:\n"
        "• AM: Masa de aire absoluta.\n"
        "• θ_z: Ángulo cenital del sol.\n"
        "• a₀, a₁, a₂, a₃, a₄: Coeficientes empíricos espectrales.\n"
        "• M_ref: Transmitancia espectral a STC (AM 1.5g)."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(3.4), COLUMN_WIDTH - Inches(0.4), Inches(3.0), am_details, size=12)
    add_footer(slide, 6, TOTAL_SLIDES)

    # --- SLIDE 7: Perfil Diario (Imagen) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Dinámica Horaria: Irradiancia en Día Despejado")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.8))
    add_image(slide, 'output/Extra_Resultados/perfil_dia_tipico.png', Inches(2.41), Inches(1.4), width=Inches(8.5))
    add_footer(slide, 7, TOTAL_SLIDES)

    # --- SLIDE 8: Modelamiento Térmico (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Temperatura de Celda (Sandia SAPM)")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación del Modelo Térmico")
    
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "La temperatura interna de la celda (Tc) depende del recurso solar y del viento:", size=13)
    add_latex_equation(slide, r"T_c = G_{poa} \cdot e^{a + b \cdot v_w} + T_a + \left(\frac{G_{poa}}{1000}\right) \cdot \Delta T", MARGIN + Inches(0.3), Inches(2.2), Inches(0.45))
    
    thermal_details = (
        "Donde:\n"
        "• T_c / T_a: Temperatura de celda y ambiental (°C).\n"
        "• G_poa: Irradiancia en el plano del panel (W/m²).\n"
        "• v_w: Velocidad del viento (m/s).\n"
        "• a, b, ΔT: Parámetros empíricos del encapsulado."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(2.9), COLUMN_WIDTH - Inches(0.4), Inches(3.0), thermal_details, size=13, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Coeficientes por Tecnología")
    thermal_coef = (
        "Los parámetros empíricos varían según la disipación del marco y capas protectoras:\n\n"
        "1. Silicio Monocristalino (m-Si) — glass/polymer:\n"
        "   • a = -3.56  |  b = -0.075\n"
        "   • ΔT = 3.0 °C\n"
        "   → Comportamiento: Disipación estándar, mayor calentamiento.\n\n"
        "2. Heterounión (HIT) — glass/glass:\n"
        "   • a = -3.47  |  b = -0.059\n"
        "   • ΔT = 3.0 °C\n"
        "   → Comportamiento: Estructura de doble vidrio, retiene ligeramente más calor, pero se compensa por su bajo coeficiente térmico."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), thermal_coef, size=14)
    add_footer(slide, 8, TOTAL_SLIDES)

    # --- SLIDE 9: Histograma Térmico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Resultados Térmicos: Distribución Anual Tc")
    add_panel(slide, MARGIN, Inches(1.2), Inches(7), Inches(5.5), title="Distribución de Temperatura de Celda")
    add_image(slide, 'output/Fase1_Resultados/temp_hist_HIT.png', MARGIN + Inches(0.2), Inches(1.8), width=Inches(5.8))
    
    add_panel(slide, Inches(7.5), Inches(1.2), Inches(5.4), Inches(5.5), title="Comportamiento en Atacama")
    add_text(slide, Inches(7.7), Inches(1.8), Inches(5), Inches(4), 
             "• Temperatura promedio diurna de celda: ~38°C a 45°C.\n"
             "• Picos térmicos extremos superan los 65°C a mediodía en verano.\n"
             "• Clima desértico seco reduce la convección natural del marco.\n"
             "• Las altas temperaturas aumentan la corriente de saturación inversa (Io), reduciendo severamente el Voc.", size=16)
    add_footer(slide, 9, TOTAL_SLIDES)

    # --- SLIDE 10: Modelo de 5 Parámetros (SDM) (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Modelo de 5 Parámetros: Diodo Simple (SDM)")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación del Circuito Equivalente")
    
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "El módulo se modela como un circuito equivalente de un diodo y pérdidas óhmicas:", size=13)
    # Altura optimizada a 0.34 para evitar que desborde de la columna
    add_latex_equation(slide, r"I = I_L - I_0 \cdot \left[ \exp\left(\frac{V + I \cdot R_s}{a}\right) - 1 \right] - \frac{V + I \cdot R_s}{R_{sh}}", MARGIN + Inches(0.3), Inches(2.2), Inches(0.34))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(2.9), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "El factor de idealidad térmico (a) se define formalmente como:", size=13)
    add_latex_equation(slide, r"a = \frac{N_s \cdot n_I \cdot k \cdot T_c}{q}", MARGIN + Inches(0.3), Inches(3.4), Inches(0.42))
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Glosario de Parámetros Físicos")
    sdm_glossary = (
        "• I / V: Corriente y voltaje de salida (A, V).\n"
        "• I_L: Corriente fotogenerada por irradiancia (A).\n"
        "• I_₀: Corriente de saturación inversa del diodo (A).\n"
        "• R_s: Resistencia serie de pérdidas (Ω).\n"
        "• R_sh: Resistencia paralelo o shunt de fugas (Ω).\n"
        "• N_s: Número de celdas en serie (m-Si: 36, HIT: 72).\n"
        "• n_I: Factor de idealidad del diodo.\n"
        "• k: Constante de Boltzmann (1.3806 × 10⁻²³ J/K).\n"
        "• q: Carga elemental del electrón (1.6022 × 10⁻¹⁹ C).\n"
        "• T_c: Temperatura de celda absoluta (K)."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), sdm_glossary, size=12)
    add_footer(slide, 10, TOTAL_SLIDES)

    # --- SLIDE 11: Extracción en SRC (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Extracción de Parámetros de Referencia")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Sistema No-Lineal de 5 Ecuaciones")
    
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(1.3),
             "Se extraen a_ref, I_L,ref, I_0,ref, R_s,ref, R_sh,ref en STC:\n\n"
             "1. Cortocircuito (I_sc): V = 0, I = I_sc,ref\n"
             "2. Circuito Abierto (V_oc): I = 0, V = V_oc,ref\n"
             "3. Máxima Potencia (MPP): I = I_mp,ref, V = V_mp,ref\n"
             "4. Pendiente en MPP (dP/dV = 0):", size=12)
    add_latex_equation(slide, r"\left.\frac{dI}{dV}\right|_{mp} = -\frac{I_{mp,ref}}{V_{mp,ref}}", MARGIN + Inches(0.3), Inches(3.1), Inches(0.4))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(3.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "5. Coeficiente térmico de V_oc:", size=12)
    add_latex_equation(slide, r"\beta_{Voc} = \frac{\partial V_{oc}}{\partial T_c}", MARGIN + Inches(0.3), Inches(4.1), Inches(0.36))
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación de la Derivada Analítica en MPP")
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "Para acoplar Rs y el factor de idealidad, se implementa la derivada analítica obtenida del circuito:", size=12)
    add_latex_equation(slide, r"\left.\frac{dI}{dV}\right|_{mp} = -\frac{A + B}{1 + R_s \cdot A + R_s \cdot B}", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(2.2), Inches(0.46))
    
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(2.85), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "Donde:", size=12)
    add_latex_equation(slide, r"A = \frac{I_0}{a} \cdot e^{\frac{V_{mp} + I_{mp} \cdot R_s}{a}}", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(3.15), Inches(0.42))
    add_latex_equation(slide, r"B = \frac{1}{R_{sh}}", MARGIN + COLUMN_WIDTH + GAP + Inches(0.3), Inches(3.75), Inches(0.3))
    
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(4.25), COLUMN_WIDTH - Inches(0.4), Inches(1.5),
             "La optimización se realiza mediante ajuste de mínimos cuadrados con bounds físicos (R_s > 0, n_I ∈ [1, 2]).", size=12, color=ACCENT_GOLD)
    add_footer(slide, 11, TOTAL_SLIDES)

    # --- SLIDE 12: Ecuaciones de Escalado (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Escalamiento a Condiciones Reales")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Dependencias con (G, Tc) de De Soto")
    
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "1. Factor de Idealidad:", size=12)
    add_latex_equation(slide, r"\frac{a}{a_{ref}} = \frac{T_c}{T_{ref}}", MARGIN + Inches(0.3), Inches(2.0), Inches(0.28))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(2.35), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "2. Corriente de Saturación Inversa (Io):", size=12)
    add_latex_equation(slide, r"\frac{I_0}{I_{0,ref}} = \left(\frac{T_c}{T_{ref}}\right)^3 \cdot \exp\left[ \frac{E_{g,ref}}{k \cdot T_{ref}} - \frac{E_g}{k \cdot T_c} \right]", MARGIN + Inches(0.3), Inches(2.65), Inches(0.35))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(3.1), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "3. Energía de Bandgap (Eg):", size=12)
    add_latex_equation(slide, r"\frac{E_g}{E_{g,ref}} = 1 - 0.0002677 \cdot (T_c - T_{ref})", MARGIN + Inches(0.3), Inches(3.4), Inches(0.28))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(3.75), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "4. Corriente Fotogenerada (IL):", size=12)
    add_latex_equation(slide, r"I_L = \left(\frac{S}{S_{ref}}\right) \cdot \left(\frac{M}{M_{ref}}\right) \cdot \left[ I_{L,ref} + \alpha_{Isc} \cdot (T_c - T_{ref}) \right]", MARGIN + Inches(0.3), Inches(4.05), Inches(0.32))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(4.45), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "5. Resistencia Shunt:", size=12)
    add_latex_equation(slide, r"R_{sh} = R_{sh,ref} \cdot \left(\frac{S_{ref}}{S}\right)", MARGIN + Inches(0.3), Inches(4.75), Inches(0.28))
    
    add_text(slide, MARGIN + Inches(0.2), Inches(5.15), COLUMN_WIDTH - Inches(0.4), Inches(0.3), "Donde Eg,ref = 1.121 eV para Silicio a 25°C.", size=12, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Suposiciones Físicas Justificadas")
    scale_just = (
        "• R_s Constante: Se asume R_s = R_s,ref.\n"
        "  Justificación: De Soto (2006) demuestra mediante validaciones contra NIST que la variación térmica de R_s es de segundo orden y su efecto en la curva I-V es despreciable.\n\n"
        "• R_sh dependiente de la Irradiancia Absorbida:\n"
        "  Sigue la relación inversamente proporcional con S para modelar cómo el aumento de portadores minoritarios abre caminos de fuga paralelos en la celda.\n\n"
        "• T_ref = 298.15 K (25°C)  |  S_ref = 1000 W/m²."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), scale_just, size=13)
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
             "• Coeficiente de determinación R² > 0.99 para ambas tecnologías.\n"
             "• RMSE < 5W en condiciones estándar.\n"
             "• Validación cruzada: El modelo de De Soto reproduce con alta fidelidad las pérdidas por temperatura en celdas de silicio.\n"
             "• Error máximo concentrado en la zona de codo a baja irradiancia.", size=16)
    add_footer(slide, 14, TOTAL_SLIDES)

    # --- SLIDE 15: Performance Ratio (Ecuación) (LaTeX) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Performance Ratio: Evaluación de Desempeño")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación Matemática del PR")
    
    add_text(slide, MARGIN + Inches(0.2), Inches(1.7), COLUMN_WIDTH - Inches(0.4), Inches(0.35),
             "El Performance Ratio (PR) evalúa la eficiencia neta del sistema fotovoltaico:", size=13)
    add_latex_equation(slide, r"PR = \frac{\sum P_{mp,SDM}(G, T_c)}{\sum \left[ P_{STC} \cdot \left(\frac{G_{poa}}{1000}\right) \right]}", MARGIN + Inches(0.3), Inches(2.2), Inches(0.48))
    
    pr_details = (
        "Donde:\n"
        "• P_mp,SDM: Potencia MPP simulada hora a hora con De Soto (W).\n"
        "• P_STC: Potencia nominal a STC (m-Si: 46.68 W | HIT: 217.52 W).\n"
        "• G_poa: Irradiancia calculada en el plano del panel (W/m²).\n"
        "• 1000: Irradiancia de referencia a STC (W/m²)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(2.9), COLUMN_WIDTH - Inches(0.4), Inches(3.0), pr_details, size=13, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Significado Físico del PR")
    pr_phys = (
        "• Indica la fracción de energía disponible que es realmente convertida en potencia útil de salida.\n\n"
        "• Un PR de 100% representaría un panel operando permanentemente a 25°C de temperatura de celda y sin ninguna pérdida reflectiva, de cableado o de suciedad.\n\n"
        "• Captura y penaliza de forma acumulativa:\n"
        "  1. Pérdidas Térmicas (elevada temperatura Tc).\n"
        "  2. Pérdidas Ópticas por Ángulo de Incidencia (IAM).\n"
        "  3. Pérdidas por Atenuación Espectral (Masa de Aire).\n"
        "  4. Pérdidas Óhmicas Internas (Resistencia Serie Rs)."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), pr_phys, size=14)
    add_footer(slide, 15, TOTAL_SLIDES)

    # --- SLIDE 16: PR Mensual ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Resultados: Performance Ratio Mensual")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.8))
    add_image(slide, 'output/Extra_Resultados/pr_mensual_comparativo.png', Inches(2.41), Inches(1.4), width=Inches(8.5))
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
             "• m-Si (Azul): Caída térmica severa. Su coeficiente térmico (-0.40 %/°C) penaliza fuertemente el voltaje en las horas pico de irradiancia desértica.", size=15)
    add_footer(slide, 17, TOTAL_SLIDES)

    # --- SLIDE 18: Resultados Anuales y Veredicto ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Resultados Anuales: m-Si vs. HIT en Atacama")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Veredicto Técnico")
    
    verdict = (
        "• Performance Ratio Anual m-Si: 84.53%\n"
        "• Performance Ratio Anual HIT: 86.92%\n\n"
        "• Ganancia Neta en PR: +2.39% a favor de HIT.\n\n"
        "El módulo HIT entrega un 2.39% más de energía útil por cada watt pico instalado, gracias a su menor caída térmica bajo el calor extremo del Desierto de Atacama en 2026."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), verdict, size=17, bold=True, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Impacto en Proyectos a Gran Escala")
    impact_text = (
        "Para una planta solar de gran escala de 100 MWp:\n\n"
        "• Cada +1% de Performance Ratio anual representa aproximadamente 2,500 MWh adicionales de generación de energía.\n\n"
        "• La ganancia de +2.39% de la tecnología HIT equivale a ~6,000 MWh/año adicionales de facturación neta.\n\n"
        "• Se justifica técnicamente la inversión en tecnología premium HIT para climas desérticos de alta irradiancia y alta temperatura."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), impact_text, size=15)
    add_footer(slide, 18, TOTAL_SLIDES)

    # --- SLIDE 19: Conclusiones y Trabajos Futuros ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Conclusiones y Proyecciones")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Conclusiones del Estudio")
    
    concl = (
        "1. La emulación geográfica (Cocoa → Atacama) fue coherente, permitiendo evaluar el Performance Ratio real.\n\n"
        "2. El modelo De Soto de 5 parámetros reprodujo con altísima precisión (R² > 0.99) el desempeño medido.\n\n"
        "3. La tecnología HIT supera en un 2.39% de PR anual al silicio monocristalino estándar.\n\n"
        "4. El coeficiente de temperatura es el factor dominante en el diseño solar desértico."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), concl, size=15, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Trabajos Futuros")
    futur = (
        "• Integración de Bifacialidad: Modelar la ganancia por albedo posterior del suelo desértico (ρ > 0.25).\n\n"
        "• Estudio de doble diodo: Capturar efectos de recombinación interna a baja irradiancia.\n\n"
        "• Pérdidas por acumulación de polvo (soiling) en el Desierto de Atacama.\n\n"
        "• Análisis de costo nivelado LCOE para evaluar el retorno de la inversión de paneles premium HIT."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), futur, size=14)
    add_footer(slide, 19, TOTAL_SLIDES)

    # --- SLIDE 20: Referencias ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Referencias y Agradecimientos")
    refs = ("• De Soto, W., Klein, S.A., Beckman, W.A. (2006). \"Improvement and validation of a model for photovoltaic array performance.\" Solar Energy 80 (2006) 78–88.\n\n"
            "• Sandia National Laboratories - Photovoltaic Array Performance Model (Sandia Report SAND2004-3535).\n\n"
            "• NREL Cocoa Dataset - Experimental Measurements for Model Validation.\n\n"
            "• pvlib-python Library documentation & community contributors.\n\n"
            "• Marion, B. et al. (2014). \"Cocoa, Florida Data Set for Validating PV Models.\" NREL Technical Report.\n\n"
            "Agradecimientos al Departamento de Electrotecnia de la UTFSM.")
    add_text(slide, MARGIN, Inches(2), SLIDE_WIDTH - 2*MARGIN, Inches(4), refs, size=16)
    add_footer(slide, 20, TOTAL_SLIDES)

    # --- Guardar ---
    output_path = "output/Presentacion_Final_ELI556_Atacama.pptx"
    prs.save(output_path)
    print(f"Presentación corregida guardada en: {output_path}")

if __name__ == "__main__":
    create_presentation()
