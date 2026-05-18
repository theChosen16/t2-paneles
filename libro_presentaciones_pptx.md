# 📘 Libro de Estrategias y Aprendizajes: Presentaciones Dinámicas con Python-PPTX

Este documento consolida las mejores prácticas, arquitecturas y trucos técnicos descubiertos durante el desarrollo de presentaciones académicas de alto impacto (proyectos de Energía Fotovoltaica y Caracterización Electromagnética).

---

## 1. Arquitectura de Proyecto (Limpia y Escalable)

Para proyectos de larga duración, la estructura de carpetas debe ser jerárquica para evitar el caos de archivos temporales:

```text
proyecto_pptx/
├── src/                          ← Scripts lógicos (.py)
│   ├── fase0_setup.py            ← Comprobación de bases de datos pvlib
│   ├── fase1_filtro_emulacion.py ← Emulación geográfica Atacama 2026
│   ├── fase2_recurso_solar.py    ← Modelo POA (Perez) y Temperatura Celda
│   ├── fase3_extraccion_params.py← Ajuste 5-parámetros De Soto en SRC
│   ├── fase4_simulacion_final.py ← Simulación minutal y cálculo de PR
│   ├── fase5_gen_extra_plots.py  ← Gráficos de validación (curvas I-V/P-V, transientes)
│   └── fase6_gen_presentation.py ← Generación de la presentación PowerPoint final
├── assets/                       ← Recursos estáticos (Logos, iconos, fondos)
├── output/                       ← Resultados finales (CSV, PNG, PPTX)
│   ├── Extra_Resultados/         ← Curvas I-V/P-V y perfiles de días típicos
│   ├── Fase1_Resultados/         ← CSVs limpios y gráficos térmicos/POA
│   ├── Fase2_Resultados/         ← CSVs de simulación y gráficos de PR
│   └── Presentacion_Final_ELI556_Atacama.pptx ← PPTX final autogenerado
├── temp/                         ← Caché temporal de parámetros extraídos (.json)
└── docs/                         ← Documentación de física de celdas y bitácora
```

---

## 2. El Sistema de Diseño (Design System)

### 🎨 Paleta de Colores "Premium"

No uses colores básicos. Define una paleta HSL o RGB curada que dé una sensación de "Modo Oscuro" profesional:

* **DARK_BG**: `(0x1A, 0x1A, 0x2E)` - Fondo profundo.
* **PANEL_BG**: `(0x22, 0x22, 0x3A)` - Contraste suave para cajas.
* **ACCENT_GOLD**: `(0xE8, 0xA8, 0x38)` - Títulos y énfasis principal.
* **ACCENT_RED**: `(0xE0, 0x5A, 0x3A)` - Alertas y riesgos críticos.
* **ACCENT_BLUE**: `(0x00, 0x7A, 0xCC)` - Detalles técnicos y referencias.

### 📐 Regla de Oro de la Simetría

Para una presentación que "se sienta" bien, la simetría debe ser matemática:

* **Margen Externo**: 0.5 pulgadas en todos los bordes.
* **Layout de Doble Panel**:
  * Panel Izquierdo: `left=0.5, width=6.0`
  * Panel Derecho: `left=6.8, width=6.0` (Esto deja un gap central de 0.3).
* **Cómputo de Ancho Total**: `13.333"` (Widescreen 16:9). El contenido útil debe sumar ~12.3" para dejar márgenes simétricos.

---

## 3. Renderizado Matemático Avanzado

### Ecuaciones LaTeX de Alta Definición

Para que las ecuaciones no se vean pixeladas en proyectores 4K:

1. **DPI**: Usar siempre `300`.
2. **Transparencia**: `transparent=True` y `facecolor='none'` son vitales.
3. **Tamaño Dinámico**:
   * *Resultados clave*: `fontsize=36`, `height=0.9"`
   * *Desarrollos*: `fontsize=32`, `height=0.6"`
4. **Cierre de Memoria**: Siempre llamar a `plt.close(fig)` para evitar fugas de memoria en ejecuciones largas.

---

## 4. Gestión de Riesgos y "Margen sin Mitigación"

Al presentar datos técnicos (tablas de riesgo), evita términos binarios como "Pasa/Falla" o "Positivo/Negativo". Usa **Gradientes de Riesgo**:

* **CRÍTICO (Rojo + Bold)**: Acción inmediata requerida.
* **ALTO RIESGO (Rojo)**: Supera umbrales por margen amplio.
* **MODERADO (Dorado)**: Dependiente de condiciones externas.
* **BAJO (Gris)**: Dentro de límites seguros.

---

## 5. Automatización y Pipeline de Exportación

### Exportación Directa (PowerPoint COM)

Si trabajas en Windows, usa el motor COM de PowerPoint para exportar slides a PNG. Es el único que garantiza que las transparencias de las ecuaciones y las sombras de las cajas se vean exactamente como en el PPTX.

```python
powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
presentation = powerpoint.Presentations.Open(pptx_path)
slide.Export(path, "PNG", 1920, 1080)
```

---

## 6. Caso de Estudio: Tarea 2 PV (Atacama 2026)

Este proyecto sirvió como validación de las estrategias de automatización. Los hitos técnicos fueron:

### 🛠️ Desafíos y Soluciones

1. **Manejo de "Big Data" (>100MB por CSV)**:
   * *Problema*: Pandas agotaba la RAM al intentar parsear archivos con longitudes de línea variables (curvas I-V).
   * *Solución*: Uso de un **Lector Manual** línea por línea con el módulo `csv`, extrayendo solo los índices necesarios (GHI, DNI, DHI, Isc, Voc, etc.) antes de convertir a DataFrame.
2. **Emulación Geográfica (Cross-Hemisphere)**:
   * *Estrategia*: Implementación de un **desfase de 6 meses** para alinear el verano térmico con el astronómico, evitando que el modelo prediga irradiancia de verano con temperaturas de invierno.
3. **Identificación de Parámetros en "Ciego"**:
   * *Aprendizaje*: Ante la falta de datasheets oficiales para IDs internos de NREL, se desarrolló un algoritmo de **extracción experimental**. Se filtraron puntos con irradiancia cercana a 1000 W/m² y se normalizaron térmicamente para obtener los parámetros SRC.
4. **Optimización Robusta (Rs > 0)**:
   * Uso de `scipy.optimize.minimize` con límites (*bounds*) físicos estrictos para asegurar que la Resistencia Serie siempre sea positiva, evitando errores de convergencia en el modelo de De Soto.

### 📊 Automatización de la Narrativa

Se separó la **lógica de contenido** (`contenido_presentacion.md`) de la **lógica de diseño** (`src/fase6_gen_presentation.py`). Esto permitió iterar el texto de la presentación sin riesgo de romper el sistema de coordenadas de las slides.

---

## 7. Checklist de Finalización (Zero Waste)

* **Limpieza**: Eliminar carpetas de caché temporales (`temp/`, `ecuaciones_generadas/`).
* **Paths**: Asegurarse de que no existan rutas hardcodeadas fuera de la raíz del proyecto.
* **Symmetry Check**: Verificar que los títulos y footers estén alineados en la misma coordenada `X` en todas las slides.
* **Readability**: Comprobar que ninguna ecuación "tape" el texto o la línea del pie de página.

---

## Bitácora de Versiones

*Libro de Estrategias - Última actualización: Mayo 2026*
