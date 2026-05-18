# Plan Paso a Paso — Tarea 2: Evaluación de Tecnologías Fotovoltaicas

> **Curso:** ELI556 — Modelamiento y análisis de sistemas PV  
> **Grupo:** Alta Tensión (AT)  
> **Ubicación:** Desierto de Atacama (Caracterización eléctrica mediante DB Cocoa)  
> **Base de datos:** Cocoa  
> **Método SDM:** De Soto et al. (2006)  
> **Fecha presentación:** Jueves 4 de junio de 2026  
> **Duración:** 20 min exposición + 5-10 min preguntas

---

## Fase 0 — Configuración del Entorno

- [x] Crear entorno Python con las dependencias necesarias (`pvlib`, `numpy`, `scipy`, `matplotlib`, `pandas`)
- [x] Descargar la base de datos **Cocoa** desde el [enlace proporcionado](https://drive.google.com/drive/folders/1PbO-FAvIkmKmIeyZTRMkiCe2lS0WnbbV?usp=sharing)
- [x] Explorar y documentar la estructura de los datos meteorológicos (columnas, resolución temporal, unidades)
- [x] Seleccionar al menos **2 tecnologías fotovoltaicas** comerciales para comparar (e.g., m-Si vs. HIT)
- [x] Obtener los datasheets de los módulos seleccionados (Se extraerán de los CSV bajo condiciones SRC: $G \approx 1000$, $T \approx 25^\circ C$)

---

## Fase 1 — Caracterización del Recurso Solar y Perfil Térmico

### 1.1 Procesamiento de datos meteorológicos

- [x] Cargar datos meteorológicos de Cocoa usando `pvlib` o `pandas`
- [x] Verificar y limpiar datos (valores faltantes, outliers, gaps temporales)
- [x] Identificar componentes de irradiancia disponibles: GHI, DNI, DHI (o estimar la descomposición)
- [x] Desarrollo del Filtro de Emulación Geográfica (Atacama 2026)
- [x] Definir velocidad de viento asumida (justificar valor constante ~1 m/s)
- [x] Calcular la irradiancia en el Plano del Arreglo ($G_{poa}$) usando modelo de transposición (e.g., Perez)
- [x] Generar gráficos de $G_{poa}$ horario, diario, mensual para el año 2026
- [x] Calcular el recurso solar total anual ($\text{kWh/m}^2$/año)
- [x] Implementar el **Sandia Module Temperature Model** (ya está en pvlib)
- [x] Obtener parámetros empíricos $a$, $b$, $\Delta T$ para cada tipo de módulo
- [x] Generar perfiles de $T_c$ horario durante el año

---

## Fase 2 — Modelamiento Eléctrico (SDM — De Soto et al.)

### 2.1 Extracción de parámetros de referencia (SRC)

- [x] Implementar las ecuaciones del modelo de 5 parámetros de **De Soto (2006)**
- [x] Definir constantes físicas ($k, q, E_g$) y parámetros de entrada ($N_s, \alpha_{I_{sc}}, \beta_{V_{oc}}$)
- [x] Resolver el sistema de ecuaciones no lineales para encontrar los 5 parámetros de referencia ($I_{L,ref}, I_{o,ref}, a_{ref}, R_{s,ref}, R_{sh,ref}$)
- [x] Simular la curva I-V y P-V para condiciones de operación en Atacama
- [x] Validar: reconstruir la curva I-V en SRC y verificar que pase por los 3 puntos conocidos ($I_{sc}$, $V_{oc}$, MPP)

### 2.2 Traslado a condiciones de operación

- [x] Implementar las ecuaciones de dependencia con $(G, T_c)$ para $I_L, I_0, a, R_s, R_{sh}$
- [x] Calcular irradiancia absorbida $S$ y modificadores ópticos ($K_{\tau\alpha}$)
- [x] Verificar que el modelo reproduce curvas I-V razonables a diferentes $(G, T_c)$

### 2.3 Discusión de puntos conflictuales

- [x] Preparar análisis de sensibilidad: efecto de $R_s$ y $n_I$ en la curva I-V
- [x] Documentar el acoplamiento entre parámetros y la validez de las asunciones del modelo

---

## Fase 3 — Simulación Anual y Performance Ratio

### 3.1 Cálculo hora a hora

- [x] Resolver la ecuación I-V implícita para encontrar el MPP horario (8760 pasos)
- [x] Calcular la generación de energía horaria, diaria y mensual
- [x] Determinar la energía total anual producida ($\text{kWh}$/año) para cada tecnología

### 3.2 Cálculo del Performance Ratio

- [x] Calcular el **Performance Ratio (PR)** anual y mensual
- [x] Generar gráficos comparativos de PR entre tecnologías
- [x] Calcular Yield específico (kWh/kWp)

---

## Fase 4 — Análisis y Selección de Tecnología

- [x] Comparar el desempeño de m-Si vs. HIT en el contexto de Atacama
- [x] Discutir el impacto del coeficiente de temperatura en el PR
- [x] Preparar figuras y tablas para el informe/presentación final
- [x] Documentar conclusiones y recomendaciones técnicas

---

## Fase 5 — Preparación de la Presentación

### 5.1 Estructura obligatoria

- [x] **Portada:** Título, integrantes, nombre del curso (ELI556)
- [x] **Numeración de láminas**
- [x] **Introducción:** Contextualización del problema.
- [x] **Justificación e impacto:** Relevancia de evaluar tecnologías PV en desiertos
- [x] **Marco referencial:** Revisión del modelo SDM De Soto, física de celdas solares
- [x] **Desarrollo y resultados:** Gráficos de alta calidad
- [x] **Conclusiones:** Tecnología recomendada con justificación técnica
- [x] **Trabajos futuros:** Posibles mejoras (doble diodo, bifacialidad, degradación, etc.)
- [x] **Referencias:** Mínimo De Soto 2006, PVlib docs, datasheets de módulos

### 5.2 Producción

- [x] Diseñar slides (máximo 20 slides para 20 min)
- [x] Preparar guion para cada integrante
- [x] Ensayar presentación completa cronometrada

### 5.3 Penalizaciones a evitar

- [x] ⚠️ **No exceder 20 minutos** (penalización: -10 puntos)
- [x] ⚠️ **Portada completa** (penalización: -5 puntos si falta)
- [x] ⚠️ **Numeración de láminas** (penalización: -5 puntos si falta)
- [x] ⚠️ **Referencias** (penalización: -5 puntos si faltan)

---

## Resumen de Archivos de Estudio Creados

| Archivo                          | Contenido                                                     |
|----------------------------------|---------------------------------------------------------------|
| `estudio_fisica_celdas_PV.md`    | Efecto fotoeléctrico, bandas, DoS, Fermi-Dirac, dopaje        |
| `estudio_union_PN_modelacion.md` | Unión P-N, mecanismos de transporte, ecuación de celda solar  |
| `estudio_desoto_5parametros.md`  | Modelo De Soto completo: 5 parámetros, ecuaciones, validación |
| `plan_tarea2.md`                 | Este archivo — plan paso a paso                               |

---

## Suposiciones a Justificar en la Presentación

1. **Ubicación exacta en Atacama** (coordenadas, latitud, longitud)
2. **Inclinación y azimuth** del módulo
3. **Velocidad de viento** (constante o perfil horario)
4. **Reflectancia del suelo** ($\rho \approx 0{,}2$ para terreno genérico, podría ser mayor en desierto)
5. **Modelo de transposición** elegido (Perez, Isotropic, etc.)
6. **Tecnologías PV** seleccionadas y sus datasheets
7. **$R_s$ constante** con temperatura (justificación De Soto)
