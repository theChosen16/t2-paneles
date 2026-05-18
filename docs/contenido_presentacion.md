# Contenido Textual: Presentación Tarea 2 — ELI556
# Evaluación de Tecnologías PV en el Desierto de Atacama
# Grupo: Alta Tensión | Fecha: 4 de junio de 2026

---

## SLIDE 1 — Portada

**Título principal:**
Evaluación de Tecnologías Fotovoltaicas en el Desierto de Atacama

**Subtítulo:**
Modelamiento Eléctrico mediante el Modelo de 5 Parámetros de De Soto

**Metadata:**
- Curso: ELI556 — Modelamiento y Análisis de Sistemas PV
- Grupo: Alta Tensión (AT)
- Fecha: 4 de junio de 2026
- Lámina: 1/15

---

## SLIDE 2 — Motivación y Contexto

**Título:** ¿Por qué el Desierto de Atacama?

**Párrafo introductorio:**
El Desierto de Atacama es una de las zonas de mayor radiación solar del planeta, con una irradiancia horizontal global anual superior a 2.900 kWh/m². Seleccionar la tecnología fotovoltaica correcta en este contexto puede significar diferencias de millones de dólares en proyectos de escala industrial.

**Puntos clave:**
- Irradiancia anual: ~2.900 kWh/m² (entre las más altas del mundo)
- Temperaturas extremas: máximas superiores a 35°C, amplias oscilaciones térmicas
- Alta altitud (≥2.400 m): menor masa de aire → mayor radiación UV/directa
- Condición crítica: las altas temperaturas de operación degradan la eficiencia de las celdas solares

**Pregunta de investigación:**
¿Cuál tecnología PV entrega el mayor rendimiento en las condiciones extremas del Atacama durante el año 2026?

---

## SLIDE 3 — Tecnologías de la Base de Datos y Selección

**Título:** ¿Por qué m-Si y HIT? Comparativa de la Base de Datos

**Introducción:**
La base de datos Cocoa (NREL) cuenta con 11 archivos de pruebas correspondientes a 5 familias tecnológicas de paneles fotovoltaicos. Para estudiar el rendimiento en el Desierto de Atacama, realizamos un análisis espectral y térmico de cada una para justificar nuestra selección:

**1. Silicio Cristalino (m-Si / x-Si) — [SELECCIONADO]**
- **Módulos:** Cocoa_mSi0166, Cocoa_mSi0188, Cocoa_mSi460A8, Cocoa_xSi12922
- **Eficiencia Típica:** 17% - 21%
- **Coeficiente de Temperatura ($P_{mp}$):** −0.40 %/°C (Deficiente)
- **Rol:** Estándar mayoritario a nivel mundial. Sirve como nuestra línea base de baja tolerancia térmica.

**2. Heterounión (HIT) — [SELECCIONADO]**
- **Módulos:** Cocoa_HIT05667
- **Eficiencia Típica:** 20% - 22%
- **Coeficiente de Temperatura ($P_{mp}$):** −0.26 %/°C (Excelente)
- **Rol:** Tecnología premium con el mejor coeficiente térmico. Ideal para evaluar el comportamiento desértico.

**3. Telururo de Cadmio (CdTe) — [DESCARTADO]**
- **Módulos:** Cocoa_CdTe75638
- **Eficiencia Típica:** 15% - 18%
- **Coeficiente de Temperatura ($P_{mp}$):** −0.28 %/°C (Excelente)
- **Razón:** Aunque es excelente ante el calor, el contraste de eficiencia frente a m-Si es menor y posee restricciones ambientales de toxicidad por Cadmio.

**4. Seleniuro de Cobre Indio Galio (CIGS) — [DESCARTADO]**
- **Módulos:** Cocoa_CIGS39017, Cocoa_CIGS8-001
- **Eficiencia Típica:** 14% - 16%
- **Coeficiente de Temperatura ($P_{mp}$):** −0.35 %/°C (Moderado)
- **Razón:** Su comportamiento térmico es intermedio y no proporciona el contraste extremo requerido metodológicamente.

**5. Silicio Amorfo (a-Si: Micro/Tandem/Triple) — [DESCARTADO]**
- **Módulos:** Cocoa_aSiMicro03036, Cocoa_aSiTandem72-46, Cocoa_aSiTriple28324
- **Eficiencia Típica:** 6% - 10%
- **Coeficiente de Temperatura ($P_{mp}$):** −0.20 %/°C (Excelente)
- **Razón:** Eficiencias extremadamente bajas y alta degradación inicial por luz (Efecto Staebler-Wronski), haciéndolos comercialmente inviables a gran escala.

**Conclusión y Justificación:**
La comparación directa de **m-Si** (eficiente, sensible al calor) contra **HIT** (premium, resistente al calor) proporciona el **contraste de Performance Ratio (PR) más rico e instructivo** para modelar pérdidas térmicas en el Desierto de Atacama.

---

## SLIDE 4 — Metodología General

**Título:** Pipeline de Simulación

**Descripción del flujo:**
La metodología sigue un pipeline de cuatro etapas, desde los datos experimentales brutos hasta el Performance Ratio final, garantizando coherencia física en cada paso.

**Etapas:**
1. **Datos de entrada:** Base de datos Cocoa (NREL) — mediciones experimentales minuto a minuto durante 2011–2012 (Florida, EE.UU.)
2. **Filtro de Emulación Geográfica:** Transformación de los datos para representar el Desierto de Atacama, año 2026
3. **Modelo Eléctrico:** Modelo de 5 Parámetros de De Soto (2006) con resolución numérica
4. **Resultado:** Performance Ratio (PR) anual y mensual por tecnología

---

## SLIDE 5 — Base de Datos Cocoa

**Título:** Base de Datos Experimental: Cocoa (NREL)

**Descripción:**
La base de datos Cocoa es un conjunto de mediciones experimentales de alto detalle, generadas por el National Renewable Energy Laboratory (NREL) en Cocoa, Florida, EE.UU. (Lat: 28.4°N, Lon: -80.7°W).

**Características:**
- Resolución temporal: ~15 minutos (mediciones de curvas I-V completas)
- Variables meteorológicas: GHI, DNI, DHI, Temperatura ambiente, Presión, Humedad
- Variables eléctricas: Isc, Voc, Imp, Vmp, Pmp, FF por cada registro
- Formato: CSV con metadatos geográficos en el encabezado

**Importante — Contexto Académico:**
Los datos son de Florida pero la simulación es para Atacama. Esto es un ejercicio académico válido: se usan los perfiles de irradiancia medidos para alimentar el modelo eléctrico, aplicando las correcciones geográficas necesarias.

---

## SLIDE 6 — Filtro de Emulación Geográfica

**Título:** Filtro de Emulación Geográfica: Florida → Atacama 2026

**Problema:**
Los datos de Cocoa corresponden al Hemisferio Norte (Florida, 2011-2012). Para simular correctamente Atacama (Hemisferio Sur, 2026) se deben resolver tres inconsistencias físicas.

**Las Tres Correcciones Aplicadas:**

**1. Alineación Estacional (Desfase +6 meses)**
- Problema: El verano en Florida (Julio) corresponde al invierno en Atacama (Julio).
- Solución: Se desplazan todos los timestamps +6 meses.
- Resultado: El verano de Florida (alta irradiancia) queda asignado al verano de Atacama (Enero 2026).

**2. Proyección Temporal al Año 2026**
- Todos los registros son remapeados al calendario del año 2026, manteniendo la correlación horaria.

**3. Traducción Espacial (Metadatos)**
- Latitud: −22.91° (Sur)
- Longitud: −68.20° (Oeste)
- Elevación: 2.400 m s.n.m.
- Tilt óptimo: 22.91° (igual a la latitud absoluta)
- Azimut: 0° (orientación Norte — óptima en el hemisferio Sur)

---

## SLIDE 7 — Recurso Solar en Atacama 2026

**Título:** Recurso Solar Emulado — Atacama 2026

**Modelo de Transposición:**
Se utilizó el Modelo de Perez para calcular la irradiancia en el Plano del Arreglo (G_poa), dada su superior precisión para la componente difusa del cielo.

**Fórmula:**
G_poa = G_b · Rb · Ktα_b + G_d · Ktα_d · (1+cosβ)/2 + G · ρ · Ktα_g · (1-cosβ)/2

**Parámetros adoptados:**
- Velocidad de viento: 1 m/s (constante, valor conservador para desierto)
- Reflectancia del suelo: ρ = 0.20 (terreno desértico árido)
- Inclinación β: 22.91°

**Resultado:**
- Recurso solar total anual (POA): ~16.355 kWh/m² (mSi) / ~17.068 kWh/m² (HIT)
- Temperatura de celda media (horas de sol): ~38°C, con máximos de hasta 70°C

---

## SLIDE 8 — Perfil Térmico: Modelo SAPM

**Título:** Temperatura de Celda — Modelo Sandia (SAPM)

**Ecuación del modelo:**
T_c = G_poa · exp(a + b·v_w) + T_a + (G_poa / G₀) · ΔT

**Parámetros según tecnología:**

| Parámetro | m-Si (glass/polymer) | HIT (glass/glass) |
|-----------|---------------------|-------------------|
| a         | −3.56               | −3.47             |
| b         | −0.075              | −0.059            |
| ΔT        | 3                   | 3                 |

**Conclusión térmica:**
En verano de Atacama, las temperaturas de celda alcanzan 65–70°C durante el mediodía solar. Esta es la condición más crítica para evaluar las diferencias entre tecnologías.

---

## SLIDE 9 — Modelo Eléctrico: De Soto (2006)

**Título:** Modelo de 5 Parámetros — De Soto et al. (2006)

**Ecuación del Diodo Simple:**
I = I_L − I₀ · [exp((V + I·Rs)/a) − 1] − (V + I·Rs)/Rsh

**Los 5 Parámetros de Referencia (SRC: 1000 W/m², 25°C):**

| Parámetro | Descripción                              |
|-----------|------------------------------------------|
| I_L,ref   | Corriente fotogenerada                   |
| I₀,ref    | Corriente de saturación inversa del diodo|
| a_ref     | Factor de idealidad modificado (n·Ns·kT/q)|
| Rs,ref    | Resistencia serie                        |
| Rsh,ref   | Resistencia shunt                        |

**Obtención de parámetros:**
Los 5 parámetros se obtienen resolviendo el sistema de ecuaciones de 3 condiciones de operación conocidas (Isc, Voc, MPP) más la condición de máxima potencia (dP/dV=0), usando scipy.optimize.minimize con restricciones físicas.

---

## SLIDE 10 — Parámetros SRC Extraídos

**Título:** Parámetros Extraídos a Condiciones de Referencia

**Metodología de extracción:**
Los coeficientes de temperatura (α_Isc, β_Voc) se extrajeron directamente de la nube de datos experimentales mediante regresión lineal sobre puntos de alta irradiancia (G_poa > 800 W/m²), normalizando Isc por irradiancia para aislar el efecto térmico puro.

**Resultados por Tecnología:**

**m-Si (Silicio Monocristalino):**
- Isc_ref: 2.769 A | Voc_ref: 22.547 V
- Imp_ref: 2.500 A | Vmp_ref: 18.673 V
- Pmp_ref: 46.68 W | Ns: 36 celdas
- α_Isc: +0.00138 A/°C | β_Voc: −0.0666 V/°C
- I_L,ref: 2.768 A | I₀,ref: 4.13×10⁻⁹ A

**HIT (Heterounión):**
- Isc_ref: 5.607 A | Voc_ref: 51.514 V
- Imp_ref: 5.106 A | Vmp_ref: 42.600 V
- Pmp_ref: 217.52 W | Ns: 72 celdas
- α_Isc: +0.00280 A/°C | β_Voc: −0.1075 V/°C
- I_L,ref: 5.607 A | I₀,ref: 4.68×10⁻¹⁰ A

---

## SLIDE 11 — Traslado a Condiciones de Operación

**Título:** De SRC a Condiciones Reales de Atacama

**Ecuaciones de escalamiento (De Soto):**

Factor de idealidad:
a/a_ref = T_c / T_c,ref

Corriente de saturación:
I₀/I₀,ref = (T_c/T_c,ref)³ · exp[E_g/k · (1/T_ref − 1/T_c)]

Corriente fotogenerada:
I_L = (G/G_ref) · [I_L,ref + α_Isc · (T_c − T_c,ref)]

Resistencia shunt:
R_sh = R_sh,ref · (G_ref/G)

Resistencia serie:
R_s = R_s,ref = constante

**Justificación de Rs constante:**
De Soto (2006) demuestra que la variación de Rs con temperatura es de segundo orden y su efecto en la curva I-V es despreciable frente a los cambios de I₀ y a.

---

## SLIDE 12 — Puntos Conflictuales del Modelo

**Título:** Discusión: Limitaciones y Puntos Conflictuales

**1. Acoplamiento Rs − n_I (factor de idealidad)**
Ambos parámetros controlan la curvatura de la curva I-V en la región del MPP. Existe una alta correlación entre ellos: distintas combinaciones (Rs, n_I) pueden producir curvas I-V prácticamente idénticas. Esto hace que la identificación individual sea un problema mal condicionado.
→ Solución aplicada: Se fijaron bounds físicos en la optimización (Rs > 0, n ∈ [1, 2]).

**2. Rsh inversamente proporcional a G**
La relación Rsh = Rsh_ref · (G_ref/G) es una aproximación empírica. A irradiancia muy baja (amanecer/ocaso), Rsh puede sobreestimarse, afectando la corriente de fuga.
→ Impacto real: marginal en el cómputo de energía anual (horas de baja irradiancia tienen poca contribución).

**3. Bandgap lineal con temperatura**
La aproximación E_g = E_g,ref · (1 − 0.0002677·ΔT) es una simplificación. En realidad, la relación es no-lineal (Varshni).
→ Error típico: < 1% en el rango 0–70°C de operación.

**4. Rs constante con temperatura**
Implica ignorar el efecto de la resistividad del semiconductor con T.
→ Justificación: De Soto et al. validaron esta suposición contra datos NIST con error < 2%.

---

## SLIDE 13 — Resultados: Performance Ratio

**Título:** Resultados Finales — Performance Ratio Atacama 2026

**Definición del PR:**
PR = Σ P_mp,SDM(G,T_c) / Σ [P_STC · (G_poa/1000)]

Donde P_STC es la potencia nominal del módulo a condiciones estándar (1000 W/m², 25°C).

**Resultados anuales:**

| Tecnología | PR Anual | ΔPR vs m-Si |
|------------|----------|-------------|
| m-Si       | 84.53%   | — (referencia) |
| HIT        | 86.92%   | +2.39%     |

**Interpretación:**
El módulo HIT entrega un 2.39% más de energía por watt instalado, manteniendo su eficiencia bajo el calor extremo del mediodía desértico. Esto se debe directamente a su menor coeficiente de temperatura de potencia.

**Nota de la variación mensual:**
El PR es más bajo en los meses de verano (Enero-Febrero) cuando las temperaturas de celda son máximas (~65°C). En invierno (Junio-Julio), el PR sube porque la irradiancia es alta pero las temperaturas son moderadas.

---

## SLIDE 14 — Análisis Comparativo y Recomendación

**Título:** Análisis Comparativo — ¿Cuál Tecnología para Atacama?

**Tabla comparativa:**

| Criterio                        | m-Si          | HIT           | Ventaja  |
|---------------------------------|---------------|---------------|----------|
| Performance Ratio Anual         | 84.53%        | 86.92%        | HIT      |
| Coef. de temperatura (P_mp)    | ~−0.40 %/°C   | ~−0.26 %/°C  | HIT      |
| Eficiencia SRC                  | ~17%          | ~22%          | HIT      |
| Costo relativo (por Wp)         | Bajo          | Alto (+20-30%)| m-Si     |
| Disponibilidad comercial        | Alta          | Moderada      | m-Si     |
| Madurez tecnológica             | Alta          | Alta          | Empate   |

**Recomendación técnica:**
Para proyectos en el Desierto de Atacama donde la temperatura de operación es críticamente alta, la tecnología HIT es técnicamente superior. Cada +1% de PR en un proyecto de 100 MWp representa aproximadamente 2.500 MWh adicionales de energía anual.

**Recomendación económica:**
La decisión final depende del LCOE (Costo Nivelado de Energía). El mayor costo del panel HIT debe amortizarse contra la ganancia en generación.

---

## SLIDE 15 — Conclusiones y Trabajos Futuros

**Título:** Conclusiones y Proyecciones

**Conclusiones:**
1. La emulación geográfica (Cocoa→Atacama) fue exitosa y físicamente coherente, permitiendo un estudio riguroso sin datos meteorológicos propios de Atacama.
2. El Modelo de De Soto (5 parámetros) reprodujo el comportamiento eléctrico de los módulos con alta fidelidad, validado por la concordancia entre parámetros extraídos y valores físicos esperados.
3. La tecnología HIT supera al m-Si en un 2.39% de Performance Ratio anual en el contexto de Atacama, representando una ventaja operacional significativa.
4. El coeficiente de temperatura es el factor diferenciador dominante en climas desérticos de alta irradiancia.

**Trabajos Futuros:**
- Modelo de doble diodo para capturar efectos de recombinación en la zona de deplexión
- Bifacialidad: incorporar la contribución del albedo del suelo desértico (ρ > 0.30)
- Degradación anual (LID/PID): modelar caída de eficiencia a lo largo de 25 años
- Análisis LCOE: integrar costos de instalación, O&M y financiamiento para decisión económica
- Sombreado y suciedad: corrección por acumulación de polvo en paneles (factor crítico en Atacama)

**Agradecimientos:**
Datos experimentales: Cocoa Dataset — National Renewable Energy Laboratory (NREL)

---

## SLIDE 16 — Referencias

**Título:** Referencias

1. De Soto, W., Klein, S.A., Beckman, W.A. (2006). "Improvement and validation of a model for photovoltaic array performance." *Solar Energy*, 80(1), 78–88.
2. King, D.L., Boyson, W.E., Kratochvil, J.A. (2004). "Photovoltaic Array Performance Model." Sandia Report SAND2004-3535.
3. Holmgren, W.F. et al. (2018). "pvlib python: a python package for modeling solar energy systems." *Journal of Open Source Software*, 3(29), 884.
4. Marion, B. et al. (2014). "Cocoa, Florida Data Set for Validating PV Models." NREL Technical Report TP-5200-61492.
5. Fanney, A.H. et al. (2002). "Short-term characterization of building integrated photovoltaic panels." *Journal of Solar Energy Engineering*, 124(1), 357–364.
6. Perez, R. et al. (1990). "Modeling daylight availability and irradiance components from direct and global irradiance." *Solar Energy*, 44(5), 271–289.
