# 📖 Guía de Estudio Completa — Tarea 2 ELI556: Paneles Fotovoltaicos en Atacama

> **Objetivo de esta guía:** Que entiendas de principio a fin todo lo que se hizo en el proyecto, por qué se hizo, y qué deberías poder explicar en la defensa oral.

---

## 1. ¿Cuál es la Pregunta Central del Proyecto?

> **"Si tuviera que instalar una planta fotovoltaica de gran escala en el Desierto de Atacama en 2026, ¿qué tecnología de panel conviene más: silicio monocristalino convencional (m-Si) o heterounión HIT?"**

La respuesta se construye con **datos experimentales reales** (no simulaciones teóricas puras), usando un modelo físico validado académicamente (De Soto et al., 2006).

### ¿Por qué Atacama?
- El Desierto de Atacama tiene uno de los **mejores recursos solares del mundo** (GHI > 2,900 kWh/m²·año).
- Pero la alta irradiancia implica **temperaturas de celda extremas** (hasta 65–73 °C), lo cual degrada la potencia de los paneles.
- La pregunta real es: **¿cuánto "castiga" el calor a cada tecnología?**

### ¿Por qué m-Si vs HIT?
| Tecnología | Eficiencia | Coef. Temperatura | Papel en el estudio |
|---|---|---|---|
| **m-Si** (Monocristalino) | 17-21% | Malo (−0.40%/°C) | **Estándar comercial**, sensible al calor |
| **HIT** (Heterounión) | 20-22% | Excelente (−0.26%/°C) | **Premium**, tolerante al calor |

Se descartaron CdTe, CIGS y a-Si porque no ofrecen un contraste metodológico tan rico. El objetivo es comparar los **dos extremos viables** del mercado.

---

## 2. ¿De Dónde Vienen los Datos?

### Base de datos Cocoa (NREL)
- **Fuente:** National Renewable Energy Laboratory, sitio de prueba en Cocoa, **Florida**, EE.UU.
- **Contenido:** 11 archivos CSV con mediciones de 11 módulos fotovoltaicos reales de 5 tecnologías distintas.
- **Cadencia:** Una curva I-V completa cada **5 minutos**, solo en horas de sol.
- **Periodo:** 21 de enero de 2011 → 4 de marzo de 2012 (~13.5 meses).
- **Columnas relevantes usadas (de las 43+ disponibles):**

| Columna | Qué mide |
|---|---|
| `Isc` | Corriente de cortocircuito medida |
| `Voc` | Voltaje de circuito abierto medido |
| `Imp`, `Vmp` | Corriente y voltaje en punto de máxima potencia |
| `Pmp` | Potencia máxima medida (la "verdad" para validar) |
| `T_air` | Temperatura ambiente |
| `GHI`, `DNI`, `DHI` | Componentes de irradiancia solar |
| `Pressure` | Presión atmosférica |

### Módulos seleccionados
- **mSi0166**: Un módulo de silicio monocristalino con 36 celdas en serie (Ns=36)
- **HIT05667**: Un módulo de heterounión con 72 celdas en serie (Ns=72)

> [!NOTE]
> Estos son códigos de prueba del NREL, no modelos comerciales con datasheet público. Por eso los parámetros de referencia se extraen directamente de los datos medidos.

---

## 3. El Pipeline de Trabajo (9 Fases)

El proyecto está completamente automatizado en Python. Cada fase es un script independiente que toma la salida de la fase anterior:

```
┌─────────────────────────────────────────────────────────────────┐
│ FLUJO DE TRABAJO                                                 │
│                                                                   │
│ Fase 0: Exploración de bases de datos pvlib (búsqueda de módulos)│
│    ↓                                                              │
│ Fase 1: Emulación geográfica (Florida → Atacama, ventana 12 mes) │
│    ↓                                                              │
│ Fase 2: Recurso solar (POA Perez + IAM + espectral + Tc SAPM)    │
│    ↓                                                              │
│ Fase 3: Extracción de 5 parámetros De Soto                      │
│    ↓                                                              │
│ Fase 4: Simulación anual y cálculo de Performance Ratio          │
│    ↓                                                              │
│ Fase 5: Gráficos adicionales (curvas I-V, día típico, IAM, etc.) │
│    ↓                                                              │
│ Fase 6: Generación automática de la presentación PPTX            │
│    ↓                                                              │
│ Fase 7: Exportación de previsualizaciones de láminas             │
│    ↓                                                              │
│ Fase 8: Simulación con recurso REAL de Atacama (PVGIS TMY)       │
└─────────────────────────────────────────────────────────────────┘
```

> La Fase 8 es un track paralelo: reutiliza los parámetros De Soto de la Fase 3 pero los alimenta con el recurso meteorológico real de Atacama en lugar del emulado.

---

## 4. Fase por Fase — Explicación Detallada

### 4.1 Fase 0: Exploración Inicial
**Script:** [fase0_setup.py](../src/fase0_setup.py)

**¿Qué hace?** Busca en las bases de datos de módulos de `pvlib` (CEC y Sandia) si existen los módulos `mSi0166` y `HIT05667`.

**Resultado:** No se encontraron. Esto justifica la decisión de extraer los parámetros SRC directamente de los datos medidos, en vez de usar un datasheet.

---

### 4.2 Fase 1: Emulación Geográfica (Florida → Atacama)
**Script:** [fase1_filtro_emulacion.py](../src/fase1_filtro_emulacion.py)

**Problema:** Los datos son de Florida (Lat 28.4°N), pero la tarea pide simular en Atacama (Lat 22.9°S). ¿Cómo pasar de un hemisferio a otro?

**Solución — "Emulación" en 3 pasos:**

1. **Desfase estacional (+6 meses):** En Florida, el verano es junio-agosto. En Atacama (hemisferio sur), el verano es diciembre-febrero. Se suman 6 meses a todas las fechas para alinear los solsticios.

2. **Proyección temporal (año → 2026):** Se cambia el año de todas las fechas a 2026.

3. **Traducción espacial (metadatos):** Se reescriben las 2 primeras líneas del CSV con:
   - Ubicación: San Pedro de Atacama
   - Latitud: −22.91°, Longitud: −68.20°
   - Elevación: 2400 m
   - Inclinación del panel (tilt): 22.91° (igual a la latitud, regla estándar)
   - Azimut: 0° (orientado al Norte, porque estamos en el hemisferio sur)

#### Resolución del problema de "meses con doble cobertura" (NUEVO)

**¿Por qué ocurría?** El dataset Cocoa abarca 21-ene-2011 → 04-mar-2012 (~13.5 meses), así que la temporada **21-ene → 04-mar aparece dos veces** (una en 2011 y otra en 2012). Al sumar +6 meses y forzar el año 2026, ambas copias caían sobre los mismos meses de destino (**jul–sep 2026**): esos meses recibían el doble de registros, **inflando la POA mensual y la energía anual** (~2×). El Performance Ratio, al ser un cociente, no se veía afectado, pero las magnitudes absolutas sí.

**Solución implementada:** `fase1` conserva únicamente la **primera ventana contigua de 12 meses** `[2011-01-21, 2012-01-21)`, de modo que cada mes calendario queda cubierto **una sola vez** (p. ej. enero = días 21-31 de 2011 + días 1-20 de 2012, sin solape; juntos forman un enero completo). Adicionalmente, `fase2` aplica una **red de seguridad** que elimina timestamps duplicados (575 en m-Si, 542 en HIT) generados por el recorte de fin de mes de `relativedelta(months=6)` (p. ej. 31-ago → 28-feb). Conteos resultantes:

| Etapa | m-Si | HIT |
|---|---|---|
| Filas crudas | 36,765 | 38,377 |
| Tras ventana de 12 meses | 32,961 | 34,169 |
| Válidas (dedup + limpieza) | 31,578 (95.8%) | 32,844 (96.1%) |

> [!IMPORTANT]
> **Doble track de recurso (la limitación de "magnitudes de Florida" ahora tiene contraparte):** La emulación **NO modifica** las magnitudes físicas de irradiancia/temperatura/humedad: siguen siendo las de Florida (POA emulada ≈ 1,217–1,265 kWh/m²·año). Esto se conserva porque permite **validar el modelo eléctrico** contra la potencia medida real (R² ≈ 0.99). Para obtener **energía y economía con magnitudes reales de Atacama**, se añadió la **Fase 8** (sección 4.8), que alimenta exactamente la misma metodología con el recurso TMY real de San Pedro de Atacama (POA ≈ 2,810 kWh/m²·año). Así, el PR comparativo m-Si vs HIT es válido en ambos tracks, y los valores absolutos provienen del recurso real.

---

### 4.3 Fase 2: Recurso Solar y Modelo Térmico
**Script:** [fase2_recurso_solar.py](../src/fase2_recurso_solar.py)

Esta fase hace dos cosas fundamentales:

#### A) Transposición de Irradiancia → POA (Plano del Arreglo)

Las estaciones meteorológicas miden irradiancia en tres componentes:
- **GHI** (Global Horizontal Irradiance): total que llega al suelo horizontal
- **DNI** (Direct Normal Irradiance): la componente directa del sol
- **DHI** (Diffuse Horizontal Irradiance): la que viene dispersa del cielo

Pero el panel no está horizontal — está inclinado. Se usa el **Modelo de Perez** para "transponer" estas componentes al plano inclinado del panel:

$$G_{POA} = G_{directa,panel} + G_{difusa,panel} + G_{reflejada,suelo}$$

Esto es lo que `pvlib.irradiance.get_total_irradiance(model='perez', albedo=0.20)` calcula. El **albedo se declara explícitamente en 0.20** (suelo desértico genérico), resolviendo la antigua discrepancia entre la presentación (0.20) y el código (que usaba el default 0.25 de pvlib).

#### A-bis) Modificadores Ópticos: IAM y Corrección Espectral (NUEVO)

Antes, la POA de Perez entraba **directa** al modelo eléctrico. Ahora se aplican los dos modificadores documentados en el marco teórico (De Soto 2006 §5-7; King 2004), produciendo la **irradiancia efectiva** que realmente fotogenera corriente:

1. **IAM (Incidence Angle Modifier)** — pérdidas por reflexión en ángulos de incidencia oblicuos:
   - Directa: modelo físico de Snell-Bouguer `pvlib.iam.physical(aoi, n=1.526, K=4, L=0.002)` (vidrio 2 mm).
   - Difusa: factores integrados de Marion para cielo y suelo (`pvlib.iam.marion_diffuse`).
2. **Factor espectral M** — desajuste entre el espectro real y AM1.5: `pvlib.spectrum.spectral_factor_firstsolar(pw, AM_abs)`, con agua precipitable derivada de humedad+temperatura (`gueymard94_pw`) y masa de aire absoluta.

$$G_{efectiva} = \big(G_{b}\,K_{\tau\alpha,b} + G_{d,cielo}\,K_{\tau\alpha,cielo} + G_{d,suelo}\,K_{\tau\alpha,suelo}\big)\cdot M$$

**Efecto en Atacama (track emulado):** pérdida óptica IAM ≈ **3.0%** (concentrada en amanecer/ocaso) y desajuste espectral ≈ **neutro** (cielo seco y limpio, agua precipitable baja). La POA efectiva anual es 1,180 (m-Si) / 1,229 (HIT) kWh/m² frente a la POA de banda ancha 1,217 / 1,265. La temperatura de celda sigue accionada por la POA de **banda ancha** (la absorción térmica es de banda ancha), mientras que `I_L` responde a la POA **efectiva**.

#### B) Temperatura de Celda (Modelo SAPM de Sandia)

La temperatura de la celda NO es igual a la temperatura ambiente. La celda se calienta por la irradiancia absorbida. Se usa el modelo empírico de Sandia:

$$T_{celda} = T_{POA,back} + \Delta T \cdot \frac{G_{POA}}{1000}$$

donde $T_{POA,back}$ depende del tipo de encapsulado del módulo:
- **m-Si**: `open_rack_glass_polymer` (vidrio/polímero)
- **HIT**: `open_rack_glass_glass` (vidrio/vidrio)

Se asume velocidad de viento constante = 1 m/s (clima desértico suave).

> **Cadencia / integración de energía (corregido):** La base NREL registra una curva I-V cada **5 minutos**. La energía se integra explícitamente como $\sum P\cdot\Delta t$ con $\Delta t = 5/60$ h; antes el código omitía el paso temporal, sobreestimando la energía ×12. Con el paso correcto, la POA anual emulada queda en ~1,217–1,265 kWh/m² (antes el print reportaba un valor sin integrar).

**Outputs de esta fase:**
- Archivos CSV con datos limpios + columnas `poa_global`, `poa_effective`, `iam_beam`, `spectral_factor` y `temp_cell`
- Gráficos de POA mensual y histogramas de temperatura

---

### 4.4 Fase 3: Extracción de los 5 Parámetros de De Soto
**Script:** [fase3_extraccion_parametros.py](../src/fase3_extraccion_parametros.py)

#### ¿Qué es el Modelo de De Soto (SDM)?

Es un modelo eléctrico que representa una celda fotovoltaica como un **circuito equivalente con un diodo** (Single Diode Model). La ecuación fundamental es:

$$I = I_L - I_0 \left[\exp\left(\frac{V + I R_s}{a}\right) - 1\right] - \frac{V + I R_s}{R_{sh}}$$

Los **5 parámetros** del circuito son:

| Parámetro | Símbolo | Significado Físico |
|---|---|---|
| Corriente fotogenerada | $I_L$ | La corriente que genera la luz al incidir en la celda |
| Corriente de saturación del diodo | $I_0$ | Cuánta corriente "se fuga" por el diodo (menor = mejor) |
| Factor de idealidad modificado | $a = N_s \cdot n_I \cdot kT/q$ | Qué tan ideal es el diodo |
| Resistencia serie | $R_s$ | Pérdidas en contactos y cables internos |
| Resistencia shunt | $R_{sh}$ | Fugas de corriente paralelas (mayor = mejor) |

#### ¿Cómo se extraen de los datos?

1. **Coeficientes de temperatura:**
   - Se filtran puntos con irradiancia alta (800-1200 W/m²) para aislar el efecto térmico
   - **β_Voc** (coeficiente de Voc vs temperatura): se obtiene por regresión lineal
     - m-Si: −0.0666 V/°C (−0.30%/°C)
     - HIT: −0.1115 V/°C (−0.22%/°C)
   - **α_Isc** (coeficiente de Isc vs temperatura): la regresión dio **pendiente negativa** (físicamente inválida — efecto espectral/estacional contamina). Se usó el fallback de literatura: +0.05%/°C

2. **Parámetros SRC (1000 W/m², 25°C):**
   - Se filtran puntos cercanos a las condiciones estándar (900-1100 W/m²)
   - Se normalizan a exactamente 1000 W/m² y 25°C usando los coeficientes de temperatura
   - Se obtiene el promedio de Isc_ref, Voc_ref, Imp_ref, Vmp_ref

3. **Resolución del sistema de 5 parámetros:**
   - Se plantean **3 ecuaciones** del circuito (cortocircuito, circuito abierto, punto de máxima potencia)
   - Se resuelve con `scipy.optimize.minimize` usando **5 incógnitas** (sistema subdeterminado)
   - La unicidad la dan los **bounds físicos**:
     - Rs ∈ [0.001, 2.0] Ω
     - Rsh ∈ [100, 10,000] Ω
     - a ∈ [0.5·a₀, 2·a₀]
     - IL ∈ ±10% de Isc
     - I₀ ∈ [10⁻¹², 10⁻⁵] A

**Resultado clave:**

| Parámetro | m-Si | HIT |
|---|---|---|
| IL_ref | ~2.77 A | ~5.61 A |
| I0_ref | Mayor | ~10× menor (mejor) |
| a_ref (nI=1.20) | Ns·1.2·kT/q | Ns·1.2·kT/q |
| Rs_ref | ~0.01 Ω (anclado al init) | ~0.01 Ω (anclado al init) |
| Rsh_ref | ~1000 Ω (anclado al init) | ~1000 Ω (anclado al init) |

> [!WARNING]
> **Punto conflictual importante:** Rs y Rsh quedaron esencialmente en sus valores de inicialización. Esto es evidencia directa del **mal condicionamiento Rs–n** que el paper original de De Soto ya advierte. Con solo 3 ecuaciones y 5 incógnitas, el optimizador no tiene suficiente información para distinguir entre Rs y nI. La validación R² ≈ 0.99 confirma que el conjunto reproduce bien la potencia, a pesar de esta ambigüedad.

---

### 4.5 Fase 4: Simulación Anual y Performance Ratio
**Script:** [fase4_simulacion_final.py](../src/fase4_simulacion_final.py)

#### ¿Qué hace exactamente?

Para **cada registro de 5 minutos** del año, toma las condiciones de operación (G_POA, T_celda) y:

1. **Escala los 5 parámetros** desde las condiciones SRC a las condiciones actuales usando las ecuaciones de De Soto:
   - $a = a_{ref} \cdot T_c / T_{ref}$ (factor de idealidad escala con temperatura)
   - $I_0 = I_{0,ref} \cdot (T_c/T_{ref})^3 \cdot \exp[...]$ (corriente de saturación crece con temperatura → más pérdidas)
   - $I_L = (G_{efectiva}/G_{ref}) \cdot [I_{L,ref} + \alpha \cdot (T_c - T_{ref})]$ (la corriente responde a la irradiancia **efectiva** = POA · IAM · M)
   - $R_{sh} = R_{sh,ref} \cdot (G_{ref}/G)$ (resistencia shunt inversamente proporcional a irradiancia)
   - $R_s = R_{s,ref}$ (se asume constante)

2. **Resuelve el circuito** para encontrar el punto de máxima potencia ($P_{mp}$) usando la función de Lambert W (solución analítica de la ecuación del diodo).

3. **Calcula el Performance Ratio:**

$$PR = \frac{\sum P_{mp,simulada}(t)}{\sum \frac{G_{POA}(t)}{G_{ref}} \cdot P_{STC}}$$

Donde $P_{STC}$ se obtiene resolviendo el mismo modelo a exactamente 1000 W/m² y 25°C.

> [!NOTE]
> **Numerador con irradiancia efectiva, denominador con POA de banda ancha:** la potencia simulada (numerador) ya incluye las pérdidas óptica (IAM) y espectral, mientras que la referencia ideal (denominador) usa la POA de banda ancha en el plano (criterio IEC 61724-1). Por eso, al aplicar IAM+espectral el PR **baja ~3 puntos** respecto a la versión previa: ahora penaliza correctamente esas pérdidas ópticas.

**Interpretación del PR:** Es la fracción de la energía *teórica ideal* que realmente se produce. Un PR de 85% significa que se pierde un 15% por efectos térmicos, resistivos y otros.

#### Validación

Se compara la potencia simulada vs la potencia medida por el trazador I-V del NREL en un scatter plot. El R² ≈ 0.99 confirma que el modelo eléctrico reproduce fielmente el comportamiento del módulo real.

> [!NOTE]
> Ambas series usan exactamente la misma meteorología. No es una comparación "Florida vs Atacama", sino una validación del modelo eléctrico: ¿el circuito de De Soto ajustado reproduce la potencia que midió el instrumento?

---

### 4.6 Fase 5: Gráficos Adicionales
**Script:** [fase5_gen_extra_plots.py](../src/fase5_gen_extra_plots.py)

Genera 5 gráficos clave:
1. **Curvas I-V y P-V en SRC** — Muestra la forma de la curva de cada tecnología
2. **Perfil de un día despejado** (28 enero 2026) — Irradiancia y temperatura de celda hora a hora
3. **PR mensual comparativo** — La diferencia m-Si vs HIT mes a mes
4. **Degradación térmica** — Scatter de potencia normalizada vs temperatura de celda (el gráfico que demuestra la pendiente más pronunciada de m-Si)
5. **Modificadores ópticos (NUEVO)** — Respuesta angular del IAM $K_{\tau\alpha}(\theta)$ y factor espectral M vs masa de aire para distintos niveles de agua precipitable.

### 4.7 Fases 6 y 7: Presentación PPTX
**Scripts:** [fase6_gen_presentation.py](../src/fase6_gen_presentation.py) y [fase7_export_slides.py](../src/fase7_export_slides.py)

Generan la presentación PPTX automáticamente con un "Design System" visual (modo oscuro, acentos dorados, layouts de doble panel). La estructura actual es de **26 láminas principales + 13 anexos** (39 en total).

### 4.8 Fase 8: Simulación con Recurso REAL de Atacama (NUEVO)
**Script:** [fase8_atacama_real.py](../src/fase8_atacama_real.py)

**Motivación:** El track principal (Fases 1-4) valida el modelo eléctrico con datos medidos, pero conserva magnitudes de Florida. Esta fase **añade** (sin reemplazar nada) un segundo track alimentado con el recurso solar **real** de San Pedro de Atacama, para entregar energía y economía con valores absolutos representativos.

**Fuente de datos:** **PVGIS** (Photovoltaic Geographical Information System), del **Joint Research Centre de la Comisión Europea**, base satelital **SARAH**. Se descarga el **Año Meteorológico Típico (TMY)** horario para (lat −22.91°, lon −68.20°) con `pvlib.iotools.get_pvgis_tmy` (sin clave de API) y se cachea en `data/Atacama_TMY/`. **GHI anual ≈ 2,596 kWh/m²·año** (recurso desértico real).

**Metodología:** idéntica al track emulado — Perez (POA, albedo 0.20) → IAM + factor espectral → Tc Sandia (SAPM, con viento real del TMY) → De Soto con los **mismos 5 parámetros extraídos de las mediciones NREL** (Fase 3) → PR, energía y yield (paso horario).

**Hallazgo clave:** En Atacama real, el aire de altura es frío (T_aire máx 29 °C, media 15.5 °C) y el viento medio es 2.67 m/s, por lo que la **temperatura de celda solo llega a ~58–62 °C** (más baja que los 70–73 °C del track emulado con calor húmedo de Florida y viento fijo de 1 m/s). Como el castigo térmico es menor, la **ventaja de HIT se reduce a +1.17 pts de PR** (vs +2.57 en el escenario emulado), pero la **energía absoluta se duplica** (~2.3×) por la enorme irradiancia.

---

## 5. Resultados Principales

### 5.1 Performance Ratio Anual (dos tracks)

**Track emulado (validado, magnitudes de Florida) — con IAM + espectral + albedo 0.20:**

| Métrica | m-Si (mSi0166) | HIT (HIT05667) | Ventaja HIT |
|---|---|---|---|
| **PR Anual** | **81.61%** | **84.18%** | **+2.57 puntos** |
| PR mensual (rango) | 78.7% – 86.9% | 81.6% – 88.2% | — |
| Energía DC anual | 49.8 kWh/panel | 253.4 kWh/panel | — |
| Yield específico | 993 kWh/kWp | 1,065 kWh/kWp | +7.3% |

**Track real (recurso PVGIS TMY de San Pedro de Atacama):**

| Métrica | m-Si (mSi0166) | HIT (HIT05667) | Ventaja HIT |
|---|---|---|---|
| **PR Anual** | **83.82%** | **84.99%** | **+1.17 puntos** |
| Yield específico | 2,356 kWh/kWp | 2,389 kWh/kWp | +1.4% |
| Energía DC anual | 118 kWh/panel | 568 kWh/panel | — |
| Tc máx | 58.6 °C | 62.0 °C | — |

> El PR del track emulado **bajó** respecto a la versión previa (84.53/86.92%) porque ahora se penalizan las pérdidas óptica (~3%) y espectral recién aplicadas. HIT gana en **ambos** tracks.

### 5.2 Interpretación Física

- La ventaja de HIT en PR se explica **casi completamente por el coeficiente de temperatura**.
- **m-Si** pierde ~0.40% de potencia por cada °C sobre 25°C.
- **HIT** pierde solo ~0.26% de potencia por cada °C sobre 25°C.
- En el escenario emulado (calor húmedo de Florida + viento fijo 1 m/s) la celda supera 65°C frecuentemente (máx 70–73°C) y la brecha de PR es mayor (+2.57 pts).
- En el recurso **real** de Atacama, el aire de altura es frío y ventilado: la celda solo llega a ~58–62°C, el castigo térmico es menor y la brecha se reduce a +1.17 pts — pero la energía absoluta es ~2.3× mayor.
- El gráfico de "degradación térmica" muestra que la **pendiente de m-Si es casi el doble** que la de HIT.

### 5.3 Impacto Económico (recurso real, sin escalado arbitrario)

Para una planta de **100 MWp** con el recurso **real** de Atacama (PVGIS TMY, POA ≈ 2,810 kWh/m²·año):
- Δyield (HIT − m-Si) = **33 kWh/kWp·año**
- ΔE ≈ **3,294 MWh/año**
- ΔUSD ≈ **148,000/año** (a 45 USD/MWh)

> [!NOTE]
> A diferencia de la versión previa (que necesitaba "escalar" el recurso a un valor supuesto para llegar a +6,000 MWh/+USD 270k), estos números provienen **directamente** de la simulación con el recurso real medido por satélite, sin supuestos no declarados.

### 5.4 Datos Duros Verificados (track emulado)

| Métrica | m-Si | HIT |
|---|---|---|
| Filas brutas del CSV | 36,765 | 38,377 |
| Tras ventana de 12 meses | 32,961 | 34,169 |
| Filas válidas (dedup + limpieza) | 31,578 (95.8%) | 32,844 (96.1%) |
| β_Voc medido | −0.0666 V/°C (−0.30%/°C) | −0.1115 V/°C (−0.22%/°C) |
| α_Isc | fallback +0.05%/°C | fallback +0.05%/°C |
| Ns (celdas en serie) | 36 | 72 |
| Isc_ref / Voc_ref | 2.770 A / 22.53 V | 5.620 A / 51.65 V |
| P_STC (SDM ajustado) | 50.12 W | 237.96 W |
| Pérdida óptica IAM / espectral | ~3.0% / ~neutra | ~3.0% / ~neutra |
| POA banda ancha / efectiva | 1,217 / 1,180 kWh/m² | 1,265 / 1,229 kWh/m² |
| Tc máx / Tc>65°C | 70.2 °C / 58 reg | 73.3 °C / 430 reg |
| Validación | R² ≈ 0.991, RMSE 1.4 W | R² ≈ 0.991, RMSE 6.5 W |

---

## 6. Puntos Conflictuales (Lo que Pide Discutir la Tarea)

### 6.1 Acoplamiento Rs – nI (El más importante)

**¿Qué es?** La resistencia serie ($R_s$) y el factor de idealidad ($n_I$, contenido en $a$) afectan la curva I-V de manera similar cerca del punto de máxima potencia. Cuando intentas ajustar ambos simultáneamente, hay una "correlación fuerte" — múltiples combinaciones de (Rs, nI) producen curvas casi idénticas.

**Evidencia en este trabajo:** Rs quedó en ~0.01 Ω (su valor de inicialización) y nI = 1.20 (también su valor de inicialización), porque el optimizador no pudo separarlos con solo 3 ecuaciones.

**¿Por qué no es un problema fatal?** La validación R² ≈ 0.99 demuestra que el **conjunto** de parámetros reproduce correctamente la potencia medida, aunque individualmente Rs y nI no estén perfectamente identificados. Para el cálculo del PR (que solo necesita la potencia, no las variables internas del circuito), esto es suficiente.

**Mitigación:** Bounds físicos + inicialización analítica (a₀ = Ns·1.2·kT/q; Io₀ = Isc·exp(−Voc/a₀)).

### 6.2 Sensibilidad de Rsh a Baja Irradiancia

A baja irradiancia, Rsh cambia significativamente. La aproximación $R_{sh} \propto 1/G$ es una simplificación.

### 6.3 Rs Constante con Temperatura

Se asume que Rs no cambia con la temperatura, aunque en realidad hay un efecto menor.

### 6.4 α_Isc de Literatura (No Experimental)

La regresión experimental de Isc normalizada vs temperatura dio pendiente negativa (el efecto espectral/estacional dominó sobre el térmico). Se usó el valor de literatura (+0.05%/°C). El impacto en el PR es de segundo orden porque la corriente la domina la irradiancia.

---

## 7. Limitaciones del Trabajo (Honestidad Metodológica)

> [!IMPORTANT]
> Estas limitaciones son cruciales para la defensa. Demuestran madurez académica.

### 7.1 Resuelto en esta versión

1. **IAM y corrección espectral APLICADOS:** ya se ejecutan en la Fase 2 (≈3% de pérdida óptica penalizada en el PR).
2. **Recurso real de Atacama incorporado:** la Fase 8 añade un track con PVGIS TMY (POA ≈ 2,810 kWh/m²·año) para energía/economía absolutas, sin perder la validación eléctrica con datos NREL.
3. **Doble cobertura corregida:** ventana de 12 meses contiguos → cada mes se cubre una sola vez.
4. **Albedo declarado 0.20** (antes el código usaba el default 0.25, en contradicción con la presentación).
5. **Cadencia 5 min integrada correctamente:** la energía usa $\Delta t = 5/60$ h (antes el paso temporal se omitía).

### 7.2 Limitaciones que permanecen

1. **Validación eléctrica con datos de Florida:** el R² ≈ 0.99 se valida contra mediciones de Cocoa; Atacama no dispone de un módulo PV de referencia medido, por lo que el track real usa TMY satelital (PVGIS), no mediciones in-situ.
2. **α_Isc de literatura:** la regresión experimental falló (espectro/estacionalidad) y se usó +0.05%/°C — impacto de segundo orden (la corriente la domina G).
3. **P_STC del SDM** (50.1 / 238.0 W) difiere ~7–9% del promedio empírico (46.7 / 218.4 W); criterio consistente entre tecnologías.
4. **Sin pérdidas de planta (BOS):** no se modelan cableado, inversores, soiling ni mismatch — el PR aquí es de módulo, no de planta.
5. **Modelo de un diodo:** no captura recombinación no ideal a baja irradiancia (un modelo de doble diodo sería más preciso).

---

## 8. Estructura de la Presentación (26 + 13)

La presentación tiene **26 láminas principales** y **13 láminas de anexo** (solo para responder preguntas), 39 en total. Respecto a la versión previa se agregaron dos láminas principales: **"Modificadores Ópticos APLICADOS"** (lámina 13, IAM + espectral) y **"Recurso REAL de Atacama (PVGIS TMY)"** (lámina 22, magnitudes absolutas).

### Flujo narrativo:
1. **Láminas 1-3:** Contexto → ¿Por qué Atacama? ¿Por qué m-Si vs HIT?
2. **Láminas 4-5:** Marco teórico y pipeline de trabajo
3. **Láminas 6-8:** Base de datos, ingesta y embudo de datos
4. **Láminas 9-12:** Emulación geográfica y cálculo de POA + Tc
5. **Lámina 13:** Modificadores ópticos IAM y espectral (NUEVA)
6. **Lámina 14:** Día despejado (puente divulgativo)
7. **Láminas 15-17:** Modelo eléctrico (De Soto) y simulación
8. **Láminas 18-20:** Validación, puntos conflictuales, degradación térmica
9. **Lámina 21:** Veredicto técnico (PR validado)
10. **Lámina 22:** Recurso real de Atacama + economía (NUEVA)
11. **Láminas 23-26:** Cumplimiento, limitaciones, conclusiones, referencias

### Presupuesto de tiempo:
- Total: ~21.0 min (las dos láminas nuevas añaden ~1.6 min; usar las marcadas ⚡ para comprimir si se excede el límite)
- Láminas marcadas ⚡ pueden explicarse en una sola frase si vas atrasado

---

## 9. Preguntas Anticipadas y Respuestas Preparadas

### P1: "¿Por qué Rs = 0.01 Ω en ambos módulos?"
**R:** Con solo 3 condiciones (Isc, Voc, MPP), el residuo es casi insensible a Rs y Rsh: es la manifestación directa del mal condicionamiento Rs–n. Los bounds y la inicialización analítica garantizan valores físicamente plausibles, y la validación R² ≈ 0.99 confirma que el conjunto reproduce la potencia medida.

### P2: "¿El PR no debería usar el recurso real de Atacama?"
**R:** Tenemos dos tracks. El **emulado** alinea estaciones y geometría con datos NREL medidos para **validar el modelo eléctrico** (R² ≈ 0.99); ahí las magnitudes son de Florida. El **track real** (Fase 8) usa el TMY de PVGIS para San Pedro de Atacama (POA ≈ 2,810 kWh/m²·año) y entrega energía y economía absolutas. HIT gana en ambos: +2.57 pts (emulado) y +1.17 pts (real). El menor margen en el real se debe a que el aire frío de altura modera la temperatura de celda (~58–62 °C).

### P2-bis: "¿Por qué la ventaja de HIT es menor con el recurso real?"
**R:** Porque San Pedro de Atacama está a 2,400 m: el aire es frío (máx 29 °C) y ventilado (2.67 m/s), así que la celda solo llega a ~58–62 °C, frente a los 70–73 °C del escenario emulado (calor húmedo de Florida + viento fijo 1 m/s). Menor temperatura → menor castigo térmico → menor brecha entre tecnologías. Aun así HIT gana, y la energía absoluta es ~2.3× mayor.

### P3: "¿Por qué α_Isc de literatura?"
**R:** La regresión experimental dio pendiente negativa (efecto espectral/estacional dominante). +0.05%/°C es el valor estándar y su impacto en el PR es de segundo orden porque la corriente la domina G.

### P4: "¿Por qué no CdTe si su coeficiente es excelente?"
**R:** Mayor contraste metodológico con HIT (premium c-Si) y barreras de toxicidad/cadena de suministro. El objetivo era cuantificar el castigo térmico del estándar comercial vs la alternativa premium.

---

## 10. Mapa de Archivos del Proyecto

```
T2 paneles/
├── src/                          # Scripts Python (el pipeline)
│   ├── fase0_setup.py            # Búsqueda de módulos en pvlib
│   ├── fase1_filtro_emulacion.py # Emulación Florida → Atacama
│   ├── fase2_recurso_solar.py    # POA (Perez) + Tc (SAPM)
│   ├── fase3_extraccion_parametros.py  # 5 parámetros De Soto
│   ├── fase4_simulacion_final.py # Simulación anual + PR
│   ├── fase5_gen_extra_plots.py  # Gráficos adicionales (incl. IAM/espectral)
│   ├── fase6_gen_presentation.py # Generador PPTX
│   ├── fase7_export_slides.py    # Exportador de previews
│   └── fase8_atacama_real.py     # Track con recurso REAL de Atacama (PVGIS TMY)
│
├── docs/                         # Documentación
│   ├── Tarea 2.pdf               # Enunciado original de la tarea
│   ├── 2006desoto.pdf            # Paper de De Soto et al.
│   ├── ELI556_MODELADO_*.pdf     # Material de clase
│   ├── bitacora_trabajo.md       # Log cronológico del trabajo
│   ├── estudio_desoto_5parametros.md  # Estudio del paper De Soto
│   ├── guion_presentacion.md     # Guión para la defensa oral
│   ├── analisis_critico_presentacion.md  # Auditoría código↔deck
│   ├── revision_tarea2_y_diseno.md  # Checklist de cumplimiento
│   └── guia_estudio_completa.md  # Esta guía de estudio
│
├── data/
│   ├── Cocoa/                    # CSVs originales de NREL
│   ├── Atacama_2026/             # CSVs emulados (Florida → Atacama)
│   └── Atacama_TMY/              # TMY real de PVGIS (San Pedro de Atacama)
│
├── output/
│   ├── Fase1_Resultados/         # POA mensuales, histogramas Tc
│   ├── Fase2_Resultados/         # PR mensuales, scatters validación
│   ├── Extra_Resultados/         # Curvas I-V, día típico, degradación
│   └── Presentacion_Final_*.pptx # La presentación final
│
└── temp/                         # Archivos intermedios
    ├── parametros_desoto.json    # Los 5 parámetros extraídos
    └── resultados_atacama_real.json  # Resultados del track real (Fase 8)
```

---

## 11. Glosario Rápido

| Término | Significado |
|---|---|
| **POA** | Plane of Array — irradiancia en el plano del panel |
| **GHI/DNI/DHI** | Global Horizontal / Direct Normal / Diffuse Horizontal Irradiance |
| **SRC / STC** | Standard Reference/Test Conditions (1000 W/m², 25°C, AM1.5) |
| **PR** | Performance Ratio — eficiencia real vs ideal |
| **SDM** | Single Diode Model — el modelo del circuito equivalente |
| **SAPM** | Sandia Array Performance Model — modelo térmico |
| **IAM** | Incidence Angle Modifier — pérdida por ángulo (APLICADA, modelo físico) |
| **AM** | Air Mass — masa de aire óptica (usada en el factor espectral, APLICADO) |
| **TMY** | Typical Meteorological Year — año meteorológico típico (PVGIS) |
| **PVGIS** | Photovoltaic Geographical Information System (JRC, Comisión Europea) |
| **Ns** | Número de celdas en serie |
| **nI** | Factor de idealidad del diodo |
| **Lambert W** | Función especial que resuelve analíticamente la ec. del diodo |

---

## 12. Conclusión del Trabajo

> **HIT gana por física:** Su menor coeficiente de temperatura le da ventaja en PR en condiciones desérticas. En el track **validado** (R² ≈ 0.99) la ventaja es **+2.57 puntos** (84.18% vs 81.61%); con el recurso **real** de Atacama (PVGIS TMY) es **+1.17 puntos** y se traduce en **+3,294 MWh y +USD 148k/año** en una planta de 100 MWp. HIT gana en ambos escenarios.

**Trabajos futuros sugeridos** (los previos IAM/espectral y recurso TMY ya están implementados):
- Validación in-situ contra un módulo PV medido en Atacama (no solo TMY satelital)
- Incluir soiling (ensuciamiento), factor crítico en el desierto
- Pérdidas de Balance of System (inversores, cableado, mismatch) → PR de planta
- Bifacialidad: aporte del albedo desértico en la cara posterior
- Modelo de doble diodo para mayor precisión a baja irradiancia
