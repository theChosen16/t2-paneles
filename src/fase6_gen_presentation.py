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
    
    # Aplicar estilo "No Style, Table Grid" para eliminar bordes blancos toscos por defecto
    tbl = table_shape._element.graphic.graphicData.tbl
    tblPr = tbl.tblPr
    style_id_element = tblPr.find(qn('a:tableStyleId'))
    if style_id_element is not None:
        style_id_element.text = '{5940675A-B579-460E-94D1-54222C63F5DA}'
    
    table.columns[0].width = Inches(2.0) # Tecnología
    table.columns[1].width = Inches(1.2) # Eficiencia
    table.columns[2].width = Inches(1.8) # Coef. Temp
    table.columns[3].width = Inches(4.3) # Comportamiento en Desierto
    table.columns[4].width = Inches(2.8) # Decisión / Rol
    
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
        cell.fill.fore_color.rgb = RGBColor(0x2C, 0x2C, 0x48) # Encabezado marino premium
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
            # Fila seleccionada vs descartada
            if is_selected:
                cell.fill.fore_color.rgb = RGBColor(0x28, 0x28, 0x4B) # Lighter Dark Navy
            else:
                cell.fill.fore_color.rgb = RGBColor(0x1F, 0x1F, 0x33) # Darker Dark Navy
            
            cell.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10.5 if c == 3 else 11.5)
                
                # Resaltar colores según selección
                if is_selected:
                    p.font.color.rgb = ACCENT_GOLD if c == 4 else TEXT_WHITE
                else:
                    p.font.color.rgb = RGBColor(0xBB, 0xBB, 0xBB) if c == 4 else TEXT_WHITE
                
                if c in [0, 4]: 
                    p.font.bold = True
                
                # Alineación adaptativa
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

    # --- SLIDE 5: Recurso Solar (Fórmulas POA y S) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Recurso Solar: Transposición y Absorción")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Fórmulas POA (Perez) y Absorción")
    
    eq_text = (
        "1. Irradiancia en Plano de Arreglo (POA):\n"
        "   G_poa = G_b · R_beam + G_d · [(1 + cos(β)) / 2] + G · ρ · [(1 - cos(β)) / 2]\n\n"
        "2. Irradiancia Absorbida por Celdas (S):\n"
        "   S / S_ref = (G_b / G_ref) · R_beam · K_τα,b + (G_d / G_ref) · K_τα,d · [(1 + cos(β)) / 2] + "
        "(G / G_ref) · ρ · K_τα,g · [(1 - cos(β)) / 2]\n\n"
        "Donde S_ref = G_ref = 1000 W/m² en condiciones de referencia (SRC)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), eq_text, size=13, color=ACCENT_GOLD)
    
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

    # --- SLIDE 6: Modificadores IAM y Air Mass ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Modificadores Ópticos: IAM y Masa de Aire")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Ángulo de Incidencia (IAM)")
    
    iam_text = (
        "Ecuación física basada en Ley de Snell y Bouguer:\n\n"
        "   K_τα(θ) = τ(θ) / τ(0)\n\n"
        "   τ(θ) = e^(-K·L / cos(θ_r)) · [ 1 - 0.5 · ( sin²(θ_r - θ)/sin²(θ_r + θ) + tan²(θ_r - θ)/tan²(θ_r + θ) ) ]\n\n"
        "   θ_r = arcsin( sin(θ) / n )\n\n"
        "Donde:\n"
        "• θ: Ángulo de incidencia solar.\n"
        "• n = 1.526 (Índice de refracción del vidrio templado).\n"
        "• K = 4 m⁻¹ (Absorción del vidrio).\n"
        "• L = 2 mm (Espesor típico del vidrio)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), iam_text, size=11, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Modificador por Masa de Aire (AM)")
    am_text = (
        "Corrige el desajuste del espectro solar según el espesor de la atmósfera atravesada:\n\n"
        "   M / M_ref = a₀ + a₁·AM + a₂·AM² + a₃·AM³ + a₄·AM⁴\n\n"
        "   AM = 1 / [ cos(θ_z) + 0.5057 · (96.08 - θ_z)⁻¹.⁶³⁴ ]\n\n"
        "Donde:\n"
        "• AM: Masa de aire absoluta.\n"
        "• θ_z: Ángulo cenital del sol.\n"
        "• a₀, a₁, a₂, a₃, a₄: Coeficientes empíricos espectrales.\n"
        "• M_ref: Transmitancia espectral a STC (AM 1.5g)."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), am_text, size=12)
    add_footer(slide, 6, TOTAL_SLIDES)

    # --- SLIDE 7: Perfil Diario (Imagen) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Dinámica Horaria: Irradiancia en Día Despejado")
    add_panel(slide, MARGIN, Inches(1.2), SLIDE_WIDTH - 2*MARGIN, Inches(5.8))
    add_image(slide, 'output/Extra_Resultados/perfil_dia_tipico.png', Inches(2.41), Inches(1.4), width=Inches(8.5))
    add_footer(slide, 7, TOTAL_SLIDES)

    # --- SLIDE 8: Modelamiento Térmico ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Temperatura de Celda (Sandia SAPM)")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación del Modelo Térmico")
    
    thermal_eq = (
        "La temperatura interna de la celda (T_c) depende del recurso solar y del viento:\n\n"
        "   T_c = G_poa · e^(a + b · v_w) + T_a + (G_poa / 1000) · ΔT\n\n"
        "Donde:\n"
        "• T_c / T_a: Temperatura de celda y ambiental (°C).\n"
        "• G_poa: Irradiancia en el plano del panel (W/m²).\n"
        "• v_w: Velocidad del viento (m/s).\n"
        "• a, b, ΔT: Parámetros empíricos del encapsulado."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), thermal_eq, size=14, color=ACCENT_GOLD)
    
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

    # --- SLIDE 10: Modelo de 5 Parámetros (SDM) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Modelo de 5 Parámetros: Diodo Simple (SDM)")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación del Circuito Equivalente")
    
    sdm_eq = (
        "El módulo se modela como un circuito equivalente de un diodo y pérdidas óhmicas:\n\n"
        "   I = I_L - I_₀ · [ exp((V + I·R_s) / a) - 1 ] - (V + I·R_s) / R_sh\n\n"
        "El factor de idealidad térmico (a) se define formalmente como:\n\n"
        "   a = (N_s · n_I · k · T_c) / q"
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), sdm_eq, size=14, color=ACCENT_GOLD)
    
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

    # --- SLIDE 11: Extracción en SRC ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Extracción de Parámetros de Referencia")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Sistema No-Lineal de 5 Ecuaciones")
    
    src_eq = (
        "Se extraen a_ref, I_L,ref, I_₀,ref, R_s,ref, R_sh,ref en STC:\n\n"
        "1. Cortocircuito (I_sc): V = 0, I = I_sc,ref\n"
        "2. Circuito Abierto (V_oc): I = 0, V = V_oc,ref\n"
        "3. Máxima Potencia (MPP): I = I_mp,ref, V = V_mp,ref\n"
        "4. Pendiente en MPP (dP/dV = 0):\n"
        "   dI/dV|_mpp = -I_mp,ref / V_mp,ref\n"
        "5. Coeficiente térmico de V_oc: β_Voc = ∂V_oc / ∂T_c"
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), src_eq, size=13, color=ACCENT_GOLD)
    
    add_panel(slide, MARGIN + COLUMN_WIDTH + GAP, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación de la Derivada Analítica en MPP")
    deriv_eq = (
        "Para acoplar R_s y el factor de idealidad, se implementa la derivada analítica obtenida del circuito:\n\n"
        "   dI/dV|_mpp = -(A + B) / (1 + R_s · A + R_s · B)\n\n"
        "Donde:\n"
        "   A = (I_₀ / a) · exp((V_mp + I_mp · R_s) / a)\n"
        "   B = 1 / R_sh\n\n"
        "La optimización se realiza mediante ajuste de mínimos cuadrados con bounds físicos (R_s > 0, n_I ∈ [1, 2])."
    )
    add_text(slide, MARGIN + COLUMN_WIDTH + GAP + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), deriv_eq, size=12)
    add_footer(slide, 11, TOTAL_SLIDES)

    # --- SLIDE 12: Ecuaciones de Escalado ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Escalamiento a Condiciones Reales")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Dependencias con (G, Tc) de De Soto")
    
    scale_eq = (
        "1. Factor de Idealidad:\n"
        "   a / a_ref = T_c / T_ref\n\n"
        "2. Corriente de Saturación Inversa (I_₀):\n"
        "   I_₀ / I_₀,ref = (T_c / T_ref)³ · exp[ E_g,ref / (k · T_ref) - E_g / (k · T_c) ]\n\n"
        "3. Energía de Bandgap (E_g):\n"
        "   E_g / E_g,ref = 1 - 0.0002677 · (T_c - T_ref)\n"
        "   Donde E_g,ref = 1.121 eV para Silicio a 25°C.\n\n"
        "4. Corriente Fotogenerada (I_L):\n"
        "   I_L = (S / S_ref) · (M / M_ref) · [ I_L,ref + α_Isc · (T_c - T_ref) ]\n\n"
        "5. Resistencia Shunt:\n"
        "   R_sh = R_sh,ref · (S_ref / S)"
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), scale_eq, size=12, color=ACCENT_GOLD)
    
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

    # --- SLIDE 15: Performance Ratio (Ecuación) ---
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_background(slide)
    add_title(slide, "Performance Ratio: Evaluación de Desempeño")
    add_panel(slide, MARGIN, Inches(1.2), COLUMN_WIDTH, Inches(5.5), title="Ecuación Matemática del PR")
    
    pr_eq = (
        "El Performance Ratio (PR) evalúa la eficiencia neta del sistema fotovoltaico:\n\n"
        "   PR = Σ P_mp,SDM(G, T_c) / Σ [ P_STC · (G_poa / 1000) ]\n\n"
        "Donde:\n"
        "• P_mp,SDM: Potencia MPP simulada hora a hora con De Soto (W).\n"
        "• P_STC: Potencia nominal a STC (m-Si: 46.68 W | HIT: 217.52 W).\n"
        "• G_poa: Irradiancia calculada en el plano del panel (W/m²).\n"
        "• 1000: Irradiancia de referencia a STC (W/m²)."
    )
    add_text(slide, MARGIN + Inches(0.2), Inches(1.8), COLUMN_WIDTH - Inches(0.4), Inches(4.5), pr_eq, size=14, color=ACCENT_GOLD)
    
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
