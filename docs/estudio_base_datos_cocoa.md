# Estudio de la Base de Datos "Cocoa"

Esta base de datos contiene mediciones experimentales de alta resolución de diversos módulos fotovoltaicos. Es el conjunto de datos que se utilizará para extraer los parámetros del modelo de De Soto y validar el comportamiento de las tecnologías.

---

## 1. Tecnologías Disponibles

La carpeta `Cocoa` contiene 11 archivos `.csv` correspondientes a distintas tecnologías y paneles específicos:

1. **CIGS (Cobre Indio Galio Seleniuro):** `Cocoa_CIGS39017.csv`, `Cocoa_CIGS8-001.csv`
2. **CdTe (Telururo de Cadmio):** `Cocoa_CdTe75638.csv`
3. **HIT (Heterounión):** `Cocoa_HIT05667.csv`
4. **a-Si (Silicio Amorfo):**
   - Micro: `Cocoa_aSiMicro03036.csv`
   - Tandem: `Cocoa_aSiTandem72-46.csv`
   - Triple unión: `Cocoa_aSiTriple28324.csv`
5. **m-Si / x-Si (Silicio Cristalino - Mono/Poli):** `Cocoa_mSi0166.csv`, `Cocoa_mSi0188.csv`, `Cocoa_mSi460A8.csv`, `Cocoa_xSi12922.csv`

> **Nota para la Tarea 2:** Debemos seleccionar al menos 2 de estas tecnologías para compararlas en el entorno del **Desierto de Atacama**, utilizando la base de datos Cocoa únicamente para extraer y validar su comportamiento eléctrico.

---

## 2. Estructura de los Archivos CSV

Cada archivo es extremadamente pesado (~110 MB) debido a la gran cantidad de puntos que describen la curva I-V completa en cada paso temporal. La estructura de las primeras 3 líneas es la siguiente:

### Línea 1 y 2: Metadatos del Sitio y Panel
Define la ubicación original de las mediciones y la configuración física del panel.
- **Ubicación:** Cocoa, Florida (Latitud: 28.39° N, Longitud: -80.46° W, Elevación: 12 m.s.n.m.)
- **Configuración:** Tilt (inclinación) de 28.5°, Azimuth de 180.0° (Sur).

### Línea 3: Cabeceras de Datos (Time-series)
Contiene las variables medidas. La frecuencia de muestreo es aproximadamente **cada 5 minutos** (con algunos saltos o datos faltantes).

#### Variables Meteorológicas y de Recurso Solar:
- `Global horizontal irradiance (W/m2)` (GHI)
- `Direct normal irradiance (W/m2)` (DNI)
- `Diffuse horizontal irradiance (W/m2)` (DHI)
- `POA irradiance CMP22 pyranometer (W/m2)` (Irradiancia en el Plano del Arreglo)
- `Dry bulb temperature (degC)` (Temperatura ambiente, $T_a$)
- `Relative humidity (%RH)`
- `Atmospheric pressure (mb)`
- `Precipitation (mm)`
- *(Nota: Al parecer no hay medición explícita de la velocidad del viento, lo que obligará a asumir un valor constante de $v_w \approx 1$ m/s como sugiere el plan, o investigar si se puede deducir de otra variable).*

#### Variables Eléctricas y de Temperatura del Panel:
- `PV module back surface temperature (degC)` (Temperatura posterior del módulo, sirve para estimar/validar $T_c$)
- Puntos singulares de la curva: `Isc (A)`, `Voc (V)`, `Imp (A)`, `Vmp (V)`, `Pmp (W)`, `FF (%FF)`
- Incertidumbres para cada variable.

#### Curva I-V Completa:
- `Number of I-V curve data pairs (n)`
- Seguido de cientos de columnas sin cabecera específica que contienen los pares de datos (Corriente, Voltaje) que forman la curva I-V trazada en ese instante de tiempo. Esto explica el gran tamaño de los archivos.

---

## 3. Utilidad para la Tarea 2

1. **Fase de Extracción (De Soto):** 
   - Idealmente, los 5 parámetros de De Soto se extraen de la hoja de datos (Datasheet) en SRC. Sin embargo, los valores medidos en la base de datos Cocoa (como `Isc`, `Voc`, `Vmp`, `Imp` a irradiancias cercanas a 1000 W/m² y temperaturas cercanas a 25 °C) pueden usarse para **validar** la extracción.
2. **Separación de Datos (¡CRÍTICO!):** 
   - Para evitar errores en la simulación, es fundamental distinguir qué información usar de los CSV de Cocoa y cuál reemplazar:
   - ✅ **Datos a UTILIZAR de Cocoa:** Los datos puramente eléctricos (Isc, Voc, Imp, Vmp, Pmp y pares de la curva I-V) junto con la temperatura y la irradiancia a la que fueron medidos. Esto se usa **exclusivamente** para extraer los 5 parámetros de De Soto y validar la curva del panel.
   - ❌ **Datos a DESCARTAR de Cocoa:** Las variables geográficas de la cabecera (Latitud 28.39° N, Longitud -80.46° W, Tilt 28.5°, Azimuth 180°).
   - 🌎 **Variables del Desierto de Atacama:** El análisis de rendimiento anual (PR), el cálculo de la posición solar, los ángulos de incidencia y la transposición de irradiancia al plano **deben realizarse asumiendo las coordenadas geográficas y meteorología del Desierto de Atacama**.
3. **Puntos Conflictuales ($R_s$, $R_{sh}$, $n_I$):**
   - Tener la curva I-V completa medida experimentalmente (los miles de puntos extra por fila) permitirá comparar la curva predicha por el modelo de 5 parámetros de De Soto contra la **curva real medida**, validando así los supuestos del acoplamiento entre resistencia serie y el factor de idealidad.

---

## 4. Análisis Técnico de Tecnologías PV (Contexto para Decisiones)

Para el clima del **Desierto de Atacama**, las variables críticas son la **altísima irradiancia** (que eleva la temperatura de la celda, $T_c$) y el **espectro solar** particular (alta radiación UV/directa). 

A continuación, se presenta una tabla comparativa de todas las tecnologías disponibles en la base de datos Cocoa, evaluando sus características clave y justificando la selección realizada para este estudio:

### Tabla Comparativa de Tecnologías en la Base de Datos Cocoa

| Tecnología | Archivos CSV en Cocoa | Eficiencia Típica | Coef. Temp. ($P_{mp}$) | Comportamiento en Desierto (Atacama) | Decisión y Justificación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **m-Si / x-Si** <br>(Silicio Cristalino) | `Cocoa_mSi0166.csv`<br>`Cocoa_mSi0188.csv`<br>`Cocoa_mSi460A8.csv`<br>`Cocoa_xSi12922.csv` | 17% - 21% | **Malo**<br>(~ −0.40 %/°C) | Elevada caída de voltaje y potencia debido a la baja tolerancia al calor extremo. Representa el estándar mundial. | **SELECCIONADO:** Representa la tecnología de referencia comercial mayoritaria y sirve como línea base de baja tolerancia térmica. |
| **HIT** <br>(Heterounión c-Si/a-Si) | `Cocoa_HIT05667.csv` | 20% - 22% | **Excelente**<br>(~ −0.26 %/°C) | Excepcional tolerancia al calor y alto Voc base. Mantiene alta generación bajo estrés térmico desértico. | **SELECCIONADO:** Representa la tecnología premium de alta eficiencia y la mejor tolerancia térmica disponible. |
| **CdTe** <br>(Telururo de Cadmio) | `Cocoa_CdTe75638.csv` | 15% - 18% | **Excelente**<br>(~ −0.28 %/°C) | Excelente desempeño térmico en desiertos, pero con menor eficiencia base y barreras ambientales (toxicidad del cadmio). | **DESCARTADO:** Aunque es térmicamente excelente, HIT ofrece mayor contraste de eficiencia y no posee restricciones de toxicidad. |
| **CIGS** <br>(Calco-pirita) | `Cocoa_CIGS39017.csv`<br>`Cocoa_CIGS8-001.csv` | 14% - 16% | **Bueno**<br>(~ −0.35 %/°C) | Desempeño térmico moderadamente bueno, pero propenso a fallas de aislamiento por humedad o inestabilidad espectral. | **DESCARTADO:** Su coeficiente térmico intermedio no ofrece el contraste metodológico extremo requerido en la comparativa. |
| **a-Si** <br>(Silicio Amorfo - Micro/Tandem/Triple) | `Cocoa_aSiMicro03036.csv`<br>`Cocoa_aSiTandem72-46.csv`<br>`Cocoa_aSiTriple28324.csv` | 6% - 10% | **Excelente**<br>(~ −0.20 %/°C) | Sufre fuerte degradación inicial por luz (Efecto Staebler-Wronski) y su bajísima eficiencia requiere áreas de instalación inviables. | **DESCARTADO:** Obsoleta a nivel comercial para proyectos de gran escala debido a su baja densidad de potencia. |

### Análisis Detallado de Cada Tecnología:

Para el clima del **Desierto de Atacama**, las variables críticas son la **altísima irradiancia** (que eleva la temperatura de la celda, $T_c$) y el **espectro solar** particular (alta radiación UV/directa). A continuación, el contexto técnico de cada tecnología presente en Cocoa para fundamentar la selección:

### 4.1 Silicio Cristalino (m-Si / x-Si)
- **Tecnología:** Monocristalino (m-Si) y Policristalino (x-Si o p-Si). Es el estándar de la industria (>80 % del mercado).
- **Eficiencia:** Alta (17 % - 21 % comercial).
- **Coeficiente de Temperatura:** **Malo** ($\approx -0,40$ %/°C a $-0,45$ %/°C). 
- **Comportamiento en Atacama:** La altísima radiación calentará severamente los paneles. Debido a su pobre coeficiente térmico, sufrirán grandes caídas de voltaje ($V_{oc}$) y, por ende, pérdidas significativas de potencia (Pmp).

### 4.2 HIT (Heterounión con capa fina intrínseca)
- **Tecnología:** Combina una oblea de silicio cristalino (c-Si) rodeada por capas ultrafinas de silicio amorfo (a-Si). Desarrollada originalmente por Sanyo/Panasonic.
- **Eficiencia:** Muy alta (20 % - 22 % comercial). Los bajos defectos de recombinación generan un $V_{oc}$ excepcionalmente alto.
- **Coeficiente de Temperatura:** **Excelente** ($\approx -0,25$ %/°C a $-0,28$ %/°C).
- **Comportamiento en Atacama:** Es una tecnología *premium*. Su alta eficiencia base sumada a su excelente tolerancia al calor la hacen ideal para zonas desérticas. Perderá mucha menos potencia que el m-Si bajo estrés térmico.

### 4.3 CIGS (Cobre Indio Galio Seleniuro)
- **Tecnología:** Película fina (Thin-film).
- **Eficiencia:** Buena para capa fina (14 % - 16 % comercial).
- **Coeficiente de Temperatura:** **Bueno** ($\approx -0,35$ %/°C).
- **Comportamiento en Atacama:** Rinde mejor que el silicio tradicional a altas temperaturas y tiene buena absorción con luz difusa. Sin embargo, puede sufrir Degradación Inducida por Luz (LID) inicial y es muy susceptible a la humedad si el encapsulado falla (aunque en Atacama la humedad es bajísima).

### 4.4 CdTe (Telururo de Cadmio)
- **Tecnología:** Película fina, líder en utilility-scale (ej. First Solar).
- **Eficiencia:** Muy buena para capa fina (15 % - 18 % comercial).
- **Coeficiente de Temperatura:** **Excelente** ($\approx -0,25$ %/°C a $-0,30$ %/°C).
- **Comportamiento en Atacama:** Respuesta espectral óptima (se desplaza hacia longitudes de onda cortas al calentarse). Excelente tolerancia térmica, por lo que mantendrá un alto *Performance Ratio* (PR) bajo el sol del desierto. *Nota medioambiental:* Contiene Cadmio, material altamente tóxico, lo que genera retos de reciclaje al final de su vida útil.

### 4.5 a-Si (Silicio Amorfo - Micro, Tandem, Triple)
- **Tecnología:** Película fina. Las versiones Tandem y Triple apilan capas con distintos bandgaps (ej. a-Si y a-SiGe) para absorber un espectro solar mucho más amplio.
- **Eficiencia:** Baja (6 % - 10 % comercial). Requiere enormes áreas para la misma potencia.
- **Coeficiente de Temperatura:** **Excelente** ($\approx -0,20$ %/°C).
- **Degradación (Efecto Staebler-Wronski):** Sufre una degradación drástica inicial (15 % - 20 % de pérdida en los primeros meses) inducida por la luz antes de estabilizarse. Las uniones múltiples (Tandem/Triple) mitigan parcialmente este efecto.
- **Comportamiento en Atacama:** Toleran el calor maravillosamente, pero la combinación de baja eficiencia base y alta degradación inicial (LID) hace que comercialmente estén en desventaja frente a HIT o CdTe.

> **Estrategia sugerida para la Tarea:** Comparar una tecnología estándar afectada por el calor (**m-Si**) contra una optimizada para altas temperaturas (como **HIT** o **CdTe**). Esto garantizará un análisis rico en la evaluación del *Performance Ratio* bajo las implacables condiciones geográficas y climáticas del Desierto de Atacama.

---

## 5. Estrategia de Emulación Geográfica (Proyección Atacama 2026)

Dado que la información original (curvas I-V, clima) proviene de Cocoa, pero la consigna académica exige analizar el **Desierto de Atacama**, desarrollaremos un filtro geográfico. El objetivo es emular el comportamiento medido en Cocoa, pero trasladando matemáticamente las condiciones de incidencia solar al entorno de Atacama para el **año calendario 2026**:

1. **Inversión Hemisférica (Azimuth):** Los paneles en Cocoa (Hemisferio Norte, Latitud 28.39° N) fueron medidos mirando al Sur (Azimuth 180°). Para emular este mismo perfil de captación en Atacama (Hemisferio Sur, Latitud $\approx$ 23° S), la orientación del panel en la simulación **debe ser hacia el Norte (Azimuth 0°)**.
2. **Ajuste de Inclinación (Tilt):** El Tilt en Cocoa era de 28.5° (casi idéntico a su latitud). Para que el perfil de radiación incidente (POA) en Atacama sea óptimo y comparable, propondremos un Tilt equivalente a la latitud local ($\approx$ **23° a 24°**).
3. **Alineación Climática (Desfase Estacional de 6 meses):** Para evitar el error físico de simular irradiancia y clima frío de invierno (ej. Enero en Cocoa) bajo una geometría solar de verano (Enero en Atacama), el filtro aplicará un desplazamiento a la serie temporal. Por ejemplo, los datos medidos en **Julio en Cocoa** (pleno verano) serán reetiquetados para ser evaluados como **Enero en Atacama** (verano). Así, el clima concuerda con la posición del sol.
4. **Proyección Temporal (Remapeo a 2026):** Una vez alineadas las estaciones, el filtro sobreescribirá todos los *timestamps* originales (2011/2012) actualizándolos matemáticamente a las fechas y horas del año **2026**. El resultado es una base de datos donde el sol sigue exactamente la trayectoria astronómica de Atacama en 2026, pero respaldada por las curvas eléctricas reales medidas en terreno.
