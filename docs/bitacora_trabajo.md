# Bitácora de Trabajo - Tarea 2: Evaluación de Tecnologías PV (ELI556)

**Objetivo del Proyecto:** Emular y evaluar el desempeño (*Performance Ratio*) de tecnologías fotovoltaicas instaladas virtualmente en el Desierto de Atacama durante el año 2026, utilizando el modelo de 5 parámetros de De Soto alimentado con datos experimentales de la base Cocoa (NREL).

---

## Fase 0: Preparación y Entorno (Completada)

### Decisiones Metodológicas - Fase 0

1. **Selección de Tecnologías:**
   La base de datos experimental *Cocoa* de NREL contiene 11 archivos CSV con 5 tecnologías diferentes. Para fundamentar científicamente por qué se seleccionaron únicamente **m-Si** y **HIT**, se realizó el siguiente análisis comparativo:

   | Tecnología | Eficiencia | Coef. Temp. | Comportamiento en Desierto (Atacama) | Decisión y Justificación Metodológica |
   | :--- | :---: | :---: | :--- | :--- |
   | **m-Si / x-Si** <br>(Monocristalino) | 17% - 21% | **Malo**<br>(~ −0.40%/°C) | Sufre grandes pérdidas de potencia a altas temperaturas debido a caídas severas de voltaje ($V_{oc}$). | **SELECCIONADO:** Representa la tecnología comercial mayoritaria a nivel mundial y es el estándar de referencia. |
   | **HIT** <br>(Heterounión c-Si/a-Si) | 20% - 22% | **Excelente**<br>(~ −0.26%/°C) | Mantiene un alto rendimiento bajo calor extremo gracias a su excelente coeficiente de temperatura. | **SELECCIONADO:** Representa la tecnología premium de alta tolerancia térmica, permitiendo el contraste óptimo de Performance Ratio (PR). |
   | **CdTe** <br>(Telururo de Cadmio) | 15% - 18% | **Excelente**<br>(~ −0.28%/°C) | Desempeño térmico sobresaliente, pero con menor eficiencia base y barreras ambientales por toxicidad del Cadmio. | **DESCARTADO:** Aunque es térmicamente excelente, HIT ofrece mayor contraste de eficiencia y es más seguro. |
   | **CIGS** <br>(Película Delgada) | 14% - 16% | **Bueno**<br>(~ −0.35%/°C) | Desempeño intermedio, pero muy susceptible a la degradación por humedad en encapsulados e inestabilidad espectral. | **DESCARTADO:** Su comportamiento térmico no ofrece un contraste extremo frente al silicio cristalino estándar. |
   | **a-Si** <br>(Silicio Amorfo) | 6% - 10% | **Excelente**<br>(~ −0.20%/°C) | Excelente tolerancia térmica, pero sufre degradación inicial drástica (Staebler-Wronski) y tiene bajísima eficiencia comercial. | **DESCARTADO:** Su baja densidad de potencia la hace comercialmente obsoleta para plantas solares de gran escala. |

   *Conclusión:* La comparación de **m-Si** (estándar, sensible al calor) contra **HIT** (premium, resistente al calor) proporciona el **contraste metodológico más rico e informativo** para evaluar las pérdidas por temperatura en el Desierto de Atacama.

2. **Extracción de Parámetros SRC (Standard Reference Conditions):**
   - *Problema:* Los IDs `mSi0166` y `HIT05667` son códigos de prueba del NREL y no figuran explícitamente en la base de datos de módulos de `pvlib` (CEC/Sandia).
   - *Solución:* En lugar de usar datasheets aproximados, se extraerán los valores de referencia ($I_{sc}, V_{oc}, I_{mp}, V_{mp}$) **directamente de los archivos CSV** buscando los instantes donde se cumplan las condiciones SRC ($G_{poa} \approx 1000 \text{ W/m}^2$, $T_c \approx 25^\circ\text{C}$). Esto garantiza coherencia total entre el modelo numérico y la data medida.

### Acciones Realizadas - Fase 0

- Configuración de entorno Python virtual (`venv`) con librerías científicas (`pvlib`, `pandas`, `numpy`, `scipy`, `matplotlib`).

---

## Fase 1: Caracterización del Recurso y Perfil Térmico (Completada)

### Decisiones Metodológicas - Fase 1

1. **Filtro de Emulación Geográfica:** Dado que los datos meteorológicos provienen de Florida (Hemisferio Norte) y se simulará en Atacama (Hemisferio Sur), se diseñó un filtro de emulación:
   - **Alineación Estacional (Desfase de 6 meses):** Se sumaron exactamente 6 meses a los *timestamps* originales para alinear el verano térmico con el astronómico.
   - **Proyección Temporal:** Se sobrescribió el año al **2026**.
   - **Traducción Espacial:** Los metadatos de los CSV fueron reescritos para reflejar San Pedro de Atacama (Lat: -22.91°, Long: -68.20°, Elevación: 2400 m, Tilt: 22.91°, Azimut: 0° Norte).

2. **Transposición de Irradiancia:** Se utilizó el **Modelo de Perez** para calcular la irradiancia en el plano del arreglo ($G_{poa}$).

3. **Modelo Térmico:** Se implementó el **Sandia Module Temperature Model (SAPM)** para estimar la temperatura de celda $T_c$ bajo condiciones desérticas.

### Resultados Clave - Fase 1

- Se generaron perfiles de irradiancia POA y temperatura de celda para todo el año 2026.
- Los datos filtrados y emulados se almacenaron en `data/Atacama_2026/` y los resultados térmicos en `output/Fase1_Resultados/`.

---

## Fase 2: Modelamiento Eléctrico y Simulación Final (Completada)

### Decisiones Metodológicas - Fase 2

1. **Extracción de Parámetros SRC:** Se implementó un algoritmo de optimización (`scipy.optimize.minimize`) para ajustar los 5 parámetros de De Soto a las condiciones medidas, asegurando la consistencia física ($R_s > 0$).

2. **Validación Experimental de Coeficientes:** Se extrajeron los coeficientes de temperatura ($\alpha_{Isc}$ y $\beta_{Voc}$) directamente de las nubes de puntos de los CSV emulados.

3. **Simulación Anual:** Se utilizó `pvlib.pvsystem.calcparams_desoto` para proyectar el desempeño minuto a minuto.

### Resultados de Desempeño - Fase 2 (Atacama 2026)

- **Tecnología m-Si (Silicio Monocristalino):**
  - PR Anual: **84.53%**
  - Observación: Mayor sensibilidad térmica.

- **Tecnología HIT (Heterounión):**
  - PR Anual: **86.92%**
  - Observación: Desempeño superior (+2.4% PR) debido a su menor coeficiente de temperatura.

---

## Fase 5: Preparación de la Presentación Académica (Completada)

### Acciones Realizadas - Fase 5

1. **Generación de Contenido Textual:** Se consolidó la narrativa técnica en `docs/contenido_presentacion.md`, estructurando 16 láminas que cubren desde la motivación hasta los trabajos futuros.

2. **Automatización PPTX (Design System):** Se implementó un script en Python (`src/fase6_gen_presentation.py`) para generar la presentación siguiendo un "Design System" de alta gama:
   - Modo Oscuro Profundo para reducir la fatiga visual.
   - Acentos en Oro Académico para resaltar resultados clave.
   - Layouts simétricos de doble panel para facilitar la lectura de comparativas técnicas.

3. **Validación de Resultados:** Se integraron los datos reales de Performance Ratio (84.53% vs 86.92%) directamente en las diapositivas finales.

### Estado Final del Proyecto - Fase 5

- **Archivos de salida:** `output/Presentacion_Final_ELI556_Atacama.pptx`
- **Trazabilidad:** Todo el proceso, desde el filtrado de datos crudos hasta la exportación de la presentación, está documentado y automatizado.
- **Veredicto:** El proyecto demuestra con rigor numérico que la tecnología **HIT** es la opción óptima para el despliegue fotovoltaico en el Desierto de Atacama en 2026.

---

## Fase 6 (revisión final): Reestructura del deck para la defensa de 20 minutos

### Decisiones - Reestructura

1. **24 láminas presentadas + 13 anexos** (antes 28+8): fusiones basedatos+variables, estructura→ingesta (caption), emulación impl.+límite, POA medida+notas, veredicto+economía; las láminas desplazadas pasaron a Anexos IX–XIII. Guion total: **19.4 min**.
2. **Láminas nuevas:** "Un día despejado de verano" (28-ene-2026, puente divulgativo dato→física) y "Mapa de cumplimiento Tarea 2" (requisito → método → lámina de evidencia → resultado).
3. **Corrección de coherencia código↔deck:** la tabla de parámetros ahora muestra los valores reales de `temp/parametros_desoto.json` (Rs ≈ 0.01 Ω y Rsh ≈ 1000 Ω anclados a la inicialización, nI = 1.20 en ambas tecnologías) y se usa como evidencia del mal condicionamiento Rs–n.
4. **Gráficos regenerados:** scatter de validación sin ejes "Florida vs Atacama" (fase4), perfil de día típico con hora local correcta (bug tz-aware de matplotlib en fase5: dibujaba en UTC, +4 h) y día despejado 28-ene, y POA CMP22 en español con leyenda por familia (`scratch/gen_poa_cmp22.py`).
5. **Notas del expositor embebidas** en el PPTX con presupuesto de tiempo acumulado por lámina + `docs/guion_presentacion.md` con guion, mapa de anexos y respuestas preparadas.
6. **Guard anti-desbordes** en `fase6` (`_check_overflow`): estima la altura del texto y avisa con `[OVERFLOW]` al generar; deck actual con cero avisos y verificación visual de las 37 láminas exportadas.
7. **Bug corregido (A15):** `fase3` crea `temp/` antes de escribir el JSON.

---

## Fase 7 (mejoras metodológicas): IAM, espectral, recurso real, doble cobertura

### Decisiones - Mejoras metodológicas

1. **IAM y corrección espectral APLICADOS (antes "trabajo futuro"):** En `fase2` se calcula la **irradiancia efectiva** = POA · IAM · M. El IAM directo usa el modelo físico de Snell-Bouguer (`pvlib.iam.physical`, n=1.526, K=4 m⁻¹, L=2 mm), la difusa los factores de Marion, y el factor espectral el modelo First Solar (`pvlib.spectrum.spectral_factor_firstsolar`) con agua precipitable (de humedad+T) y masa de aire absoluta. `fase4` usa la POA efectiva para la fotogeneración `I_L` y mantiene la POA de banda ancha como referencia del PR (IEC 61724-1). Efecto: el PR baja ~3 puntos (pérdida óptica ahora penalizada); la validación se mantiene en R² ≈ 0.99 con sesgo casi nulo.

2. **Recurso REAL de Atacama (nueva `fase8_atacama_real.py`):** Track paralelo que descarga el **TMY horario de PVGIS** (Joint Research Centre, Comisión Europea, base satelital SARAH) para San Pedro de Atacama vía `pvlib.iotools.get_pvgis_tmy` (cacheado en `data/Atacama_TMY/`). Aplica la misma metodología (Perez + IAM + espectral + SAPM) con los parámetros De Soto de la `fase3`. GHI real ≈ 2,596 kWh/m²·año; POA ≈ 2,810; yields ~2,356 (m-Si) / 2,389 (HIT) kWh/kWp. Resuelve la limitación de "magnitudes de Florida" sin eliminar la validación eléctrica.

3. **Doble cobertura corregida:** `fase1` recorta a la primera ventana contigua de 12 meses `[2011-01-21, 2012-01-21)` (cada mes una sola vez); `fase2` deduplica timestamps residuales del recorte de fin de mes de `relativedelta`. Conteos: m-Si 36,765 → 32,961 → 31,578; HIT 38,377 → 34,169 → 32,844.

4. **Albedo declarado 0.20** explícitamente en `get_total_irradiance` (antes default 0.25, en contradicción con la presentación).

5. **Cadencia 5 min integrada correctamente:** la energía usa Δt = 5/60 h (antes el paso temporal se omitía, sobreestimando ×12).

### Resultados - Mejoras metodológicas

- **Track emulado (validado):** PR m-Si **81.61 %** · HIT **84.18 %** → **+2.57 pts**. Tc máx 70.2/73.3 °C.
- **Track real (PVGIS TMY):** PR m-Si **83.82 %** · HIT **84.99 %** → **+1.17 pts**. Tc máx 58.6/62.0 °C (aire de altura frío). Economía 100 MWp: Δyield 33 kWh/kWp → **+3,294 MWh/año** ≈ **+USD 148k/año**.
- **Veredicto:** HIT gana en ambos escenarios de recurso.

### Presentación

- Deck reestructurado a **26 láminas + 14 anexos** (40 en total; nuevas: "Modificadores ópticos APLICADOS", "Recurso REAL de Atacama" y un anexo inicial de "Librerías y Herramientas de Código"). Guion ~21.0 min. Diagramas de flujo y embudo regenerados con los nuevos conteos. Triple revisión visual de las láminas exportadas; corregidos dos artefactos de render `%%`→`%` en las láminas de limitaciones y Anexo II.
- Todos los documentos `.md` actualizados en consecuencia (`guia_estudio_completa`, `guion_presentacion`, `analisis_critico_presentacion`, `revision_tarea2_y_diseno`, `estudio_desoto_5parametros`).
