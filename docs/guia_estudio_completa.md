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

## 3. El Pipeline de Trabajo (8 Fases)

El proyecto está completamente automatizado en Python. Cada fase es un script independiente que toma la salida de la fase anterior:

```
┌─────────────────────────────────────────────────────────────────┐
│ FLUJO DE TRABAJO                                                 │
│                                                                   │
│ Fase 0: Exploración de bases de datos pvlib (búsqueda de módulos)│
│    ↓                                                              │
│ Fase 1: Emulación geográfica (Florida → Atacama)                 │
│    ↓                                                              │
│ Fase 2: Recurso solar (transposición POA + temperatura de celda) │
│    ↓                                                              │
│ Fase 3: Extracción de 5 parámetros De Soto                      │
│    ↓                                                              │
│ Fase 4: Simulación anual y cálculo de Performance Ratio          │
│    ↓                                                              │
│ Fase 5: Gráficos adicionales (curvas I-V, día típico, etc.)     │
│    ↓                                                              │
│ Fase 6: Generación automática de la presentación PPTX            │
│    ↓                                                              │
│ Fase 7: Exportación de previsualizaciones de láminas             │
└─────────────────────────────────────────────────────────────────┘
```

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

> [!IMPORTANT]
> **Limitación clave:** Las *magnitudes físicas* de irradiancia, temperatura, humedad, etc., **NO se modifican**. Siguen siendo las de Florida. Esto significa que la POA anual simulada (~1,400 kWh/m²) es mucho menor que la real de Atacama (~2,500 kWh/m²). Sin embargo, el **Performance Ratio es un cociente normalizado**, así que la comparación relativa m-Si vs HIT **sigue siendo válida**.

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

Esto es lo que `pvlib.irradiance.get_total_irradiance(model='perez')` calcula.

#### B) Temperatura de Celda (Modelo SAPM de Sandia)

La temperatura de la celda NO es igual a la temperatura ambiente. La celda se calienta por la irradiancia absorbida. Se usa el modelo empírico de Sandia:

$$T_{celda} = T_{POA,back} + \Delta T \cdot \frac{G_{POA}}{1000}$$

donde $T_{POA,back}$ depende del tipo de encapsulado del módulo:
- **m-Si**: `open_rack_glass_polymer` (vidrio/polímero)
- **HIT**: `open_rack_glass_glass` (vidrio/vidrio)

Se asume velocidad de viento constante = 1 m/s (clima desértico suave).

**Outputs de esta fase:**
- Archivos CSV con datos limpios + columnas `poa_global` y `temp_cell`
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
     - m-Si: −0.0666 V/°C
     - HIT: −0.1075 V/°C
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
   - $I_L = (G/G_{ref}) \cdot [I_{L,ref} + \alpha \cdot (T_c - T_{ref})]$ (corriente proporcional a irradiancia)
   - $R_{sh} = R_{sh,ref} \cdot (G_{ref}/G)$ (resistencia shunt inversamente proporcional a irradiancia)
   - $R_s = R_{s,ref}$ (se asume constante)

2. **Resuelve el circuito** para encontrar el punto de máxima potencia ($P_{mp}$) usando la función de Lambert W (solución analítica de la ecuación del diodo).

3. **Calcula el Performance Ratio:**

$$PR = \frac{\sum P_{mp,simulada}(t)}{\sum \frac{G_{POA}(t)}{G_{ref}} \cdot P_{STC}}$$

Donde $P_{STC}$ se obtiene resolviendo el mismo modelo a exactamente 1000 W/m² y 25°C.

**Interpretación del PR:** Es la fracción de la energía *teórica ideal* que realmente se produce. Un PR de 85% significa que se pierde un 15% por efectos térmicos, resistivos y otros.

#### Validación

Se compara la potencia simulada vs la potencia medida por el trazador I-V del NREL en un scatter plot. El R² ≈ 0.99 confirma que el modelo eléctrico reproduce fielmente el comportamiento del módulo real.

> [!NOTE]
> Ambas series usan exactamente la misma meteorología. No es una comparación "Florida vs Atacama", sino una validación del modelo eléctrico: ¿el circuito de De Soto ajustado reproduce la potencia que midió el instrumento?

---

### 4.6 Fase 5: Gráficos Adicionales
**Script:** [fase5_gen_extra_plots.py](../src/fase5_gen_extra_plots.py)

Genera 4 gráficos clave:
1. **Curvas I-V y P-V en SRC** — Muestra la forma de la curva de cada tecnología
2. **Perfil de un día despejado** (28 enero 2026) — Irradiancia y temperatura de celda hora a hora
3. **PR mensual comparativo** — La diferencia m-Si vs HIT mes a mes
4. **Degradación térmica** — Scatter de potencia normalizada vs temperatura de celda (el gráfico que demuestra la pendiente más pronunciada de m-Si)

### 4.7 Fases 6 y 7: Presentación PPTX
**Scripts:** [fase6_gen_presentation.py](../src/fase6_gen_presentation.py) y [fase7_export_slides.py](../src/fase7_export_slides.py)

Generan la presentación PPTX automáticamente con un "Design System" visual (modo oscuro, acentos dorados, layouts de doble panel).

---

## 5. Resultados Principales

### 5.1 Performance Ratio Anual (Atacama 2026)

| Métrica | m-Si (mSi0166) | HIT (HIT05667) | Ventaja HIT |
|---|---|---|---|
| **PR Anual** | **84.53%** | **86.92%** | **+2.39 puntos** |
| PR mensual (rango) | 82.0% – 88.0% | 84.9% – 89.4% | — |
| Energía DC anual | 57.8 kWh/panel | 292.6 kWh/panel | — |
| Yield específico | 1,152 kWh/kWp | 1,236 kWh/kWp | +7.3% |

### 5.2 Interpretación Física

- La diferencia de +2.39% en PR se explica **casi completamente por el coeficiente de temperatura**.
- **m-Si** pierde ~0.40% de potencia por cada °C sobre 25°C.
- **HIT** pierde solo ~0.26% de potencia por cada °C sobre 25°C.
- En Atacama, con temperaturas de celda que superan 65°C frecuentemente, esta diferencia se acumula de forma significativa.
- El gráfico de "degradación térmica" muestra que la **pendiente de m-Si es casi el doble** que la de HIT.

### 5.3 Impacto Económico (con supuestos)

Para una planta de 100 MWp con recurso de Atacama real (~2,500 kWh/m² POA):
- ΔE ≈ 6,000 MWh/año
- ΔUSD ≈ 270,000/año (a 45 USD/MWh)

> [!CAUTION]
> Estos números económicos requieren escalar el recurso al valor real de Atacama. Con el recurso simulado (Florida, ~1,400 kWh/m²), los números serían ~3,300 MWh y ~150k USD.

### 5.4 Datos Duros Verificados

| Métrica | m-Si | HIT |
|---|---|---|
| Filas brutas del CSV | 36,765 | 38,377 |
| Filas válidas tras limpieza | 35,669 (97.0%) | 37,313 (97.2%) |
| β_Voc medido | −0.0666 V/°C (−0.30%/°C) | −0.1075 V/°C (−0.21%/°C) |
| α_Isc | fallback +0.05%/°C | fallback +0.05%/°C |
| Ns (celdas en serie) | 36 | 72 |
| Isc_ref / Voc_ref | 2.769 A / 22.55 V | 5.607 A / 51.51 V |
| P_STC (SDM ajustado) | 50.17 W | 236.72 W |
| POA anual | 1,363 kWh/m² | 1,422 kWh/m² |
| Tc máx | 70.2 °C | 73.4 °C |

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

1. **Recurso solar de Florida, no de Atacama:** Las magnitudes de irradiancia y temperatura son las medidas en Cocoa, FL. La emulación solo alinea estaciones y geometría. La comparación relativa m-Si vs HIT es válida, pero los valores absolutos de energía son conservadores.

2. **IAM y corrección espectral NO aplicados:** Las láminas del marco teórico los describen, pero el código no los implementa. Son "trabajo futuro".

3. **Meses con doble cobertura:** El dataset cubre 13.5 meses. Tras +6 meses y forzar 2026, julio–septiembre mezclan datos de dos años distintos.

4. **Sin pérdidas de planta (BOS):** No se modelan pérdidas por cableado, inversores, soiling, mismatch, etc. Solo se simula el módulo aislado.

5. **Albedo discrepancia:** La presentación dice 0.20, el código usa 0.25 (default de pvlib).

6. **Cadencia "minutal" → realmente son cada 5 minutos.**

---

## 8. Estructura de la Presentación (24 + 13)

La presentación tiene **24 láminas principales** (para 20 min de exposición) y **13 láminas de anexo** (solo para responder preguntas).

### Flujo narrativo:
1. **Láminas 1-3:** Contexto → ¿Por qué Atacama? ¿Por qué m-Si vs HIT?
2. **Láminas 4-5:** Marco teórico y pipeline de trabajo
3. **Láminas 6-8:** Base de datos, ingesta y embudo de datos
4. **Láminas 9-12:** Emulación geográfica y cálculo de POA + Tc
5. **Lámina 13:** Día despejado (puente divulgativo)
6. **Láminas 14-16:** Modelo eléctrico (De Soto) y simulación
7. **Láminas 17-19:** Validación, puntos conflictuales, degradación térmica
8. **Lámina 20:** Veredicto final + impacto económico
9. **Láminas 21-24:** Cumplimiento, limitaciones, conclusiones, referencias

### Presupuesto de tiempo:
- Total: ~19.4 min (35 s de colchón)
- Láminas marcadas ⚡ pueden explicarse en una sola frase si vas atrasado

---

## 9. Preguntas Anticipadas y Respuestas Preparadas

### P1: "¿Por qué Rs = 0.01 Ω en ambos módulos?"
**R:** Con solo 3 condiciones (Isc, Voc, MPP), el residuo es casi insensible a Rs y Rsh: es la manifestación directa del mal condicionamiento Rs–n. Los bounds y la inicialización analítica garantizan valores físicamente plausibles, y la validación R² ≈ 0.99 confirma que el conjunto reproduce la potencia medida.

### P2: "¿El PR no debería usar el recurso real de Atacama?"
**R:** La emulación alinea estaciones y geometría; las magnitudes son de Florida. El PR es un cociente normalizado por el propio recurso, así que la comparación m-Si vs HIT es válida; los valores absolutos de energía son conservadores.

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
│   ├── fase5_gen_extra_plots.py  # Gráficos adicionales
│   ├── fase6_gen_presentation.py # Generador PPTX
│   └── fase7_export_slides.py    # Exportador de previews
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
│   └── Atacama_2026/             # CSVs emulados
│
├── output/
│   ├── Fase1_Resultados/         # POA mensuales, histogramas Tc
│   ├── Fase2_Resultados/         # PR mensuales, scatters validación
│   ├── Extra_Resultados/         # Curvas I-V, día típico, degradación
│   └── Presentacion_Final_*.pptx # La presentación final
│
└── temp/                         # Archivos intermedios
    └── parametros_desoto.json    # Los 5 parámetros extraídos
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
| **IAM** | Incidence Angle Modifier — pérdida por ángulo (NO aplicada) |
| **AM** | Air Mass — masa de aire óptica |
| **Ns** | Número de celdas en serie |
| **nI** | Factor de idealidad del diodo |
| **Lambert W** | Función especial que resuelve analíticamente la ec. del diodo |

---

## 12. Conclusión del Trabajo

> **HIT gana por física:** Su menor coeficiente de temperatura le da una ventaja de +2.39 puntos de PR en condiciones desérticas. Esta ventaja se traduce en miles de MWh y cientos de miles de dólares anuales en una planta de escala.

**Trabajos futuros sugeridos:**
- Implementar IAM (pérdidas por ángulo de incidencia) y corrección espectral
- Usar datos meteorológicos reales de Atacama (TMY)
- Incluir soiling (ensuciamiento)
- Modelo de doble diodo para mayor precisión
- Pérdidas de Balance of System (inversores, cableado, etc.)
