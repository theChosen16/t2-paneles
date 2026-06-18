# Estudio: Método De Soto et al. (2006) — Modelo de 5 Parámetros

> **Fuente:** W. De Soto, S.A. Klein, W.A. Beckman. *"Improvement and validation of a model for photovoltaic array performance."* Solar Energy 80 (2006) 78–88.

---

## 1. Introducción y Contexto

El modelo propone predecir la curva I-V de un dispositivo fotovoltaico bajo **cualquier condición de operación** usando únicamente datos de fabricante (datasheets). A diferencia del modelo de King (Sandia), no requiere parámetros experimentales extensivos.

### Circuito equivalente

Un diodo en paralelo con una resistencia shunt ($R_{sh}$) y una resistencia serie ($R_s$), más una fuente de corriente fotogenerada ($I_L$).

---

## 2. Ecuación Fundamental del Modelo (Single Diode Model)

$$I = I_L - I_0 \left[\exp\left(\frac{V + I R_s}{a}\right) - 1\right] - \frac{V + I R_s}{R_{sh}}$$

donde el **factor de idealidad modificado**:

$$a = \frac{N_s \cdot n_I \cdot k \cdot T_c}{q}$$

### Los 5 Parámetros

| Parámetro   | Descripción                               |
|-------------|-------------------------------------------|
| $I_L$       | Corriente fotogenerada (light current)    |
| $I_0$       | Corriente de saturación inversa del diodo |
| $a$ ($n_I$) | Factor de idealidad modificado            |
| $R_s$       | Resistencia serie                         |
| $R_{sh}$    | Resistencia shunt (paralelo)              |

---

## 3. Determinación de Parámetros de Referencia (SRC)

Se necesitan **5 ecuaciones** independientes, obtenidas de datos del fabricante en SRC ($G = 1000$ W/m², $T_c = 25°$C):

### Ecuación (3) — Cortocircuito ($I = I_{sc,ref}$, $V = 0$)

$$I_{sc,ref} = I_{L,ref} - I_{0,ref}\left[\exp\left(\frac{I_{sc,ref} R_{s,ref}}{a_{ref}}\right) - 1\right] - \frac{I_{sc,ref} R_{s,ref}}{R_{sh,ref}}$$

### Ecuación (4) — Circuito abierto ($I = 0$, $V = V_{oc,ref}$)

$$0 = I_{L,ref} - I_{0,ref}\left[\exp\left(\frac{V_{oc,ref}}{a_{ref}}\right) - 1\right] - \frac{V_{oc,ref}}{R_{sh,ref}}$$

### Ecuación (5) — Punto de máxima potencia ($I = I_{mp,ref}$, $V = V_{mp,ref}$)

$$I_{mp,ref} = I_{L,ref} - I_{0,ref}\left[\exp\left(\frac{V_{mp,ref} + I_{mp,ref} R_{s,ref}}{a_{ref}}\right) - 1\right] - \frac{V_{mp,ref} + I_{mp,ref} R_{s,ref}}{R_{sh,ref}}$$

### Ecuación (6a) — Derivada de potencia cero en MPP

$$\frac{d(IV)}{dV}\bigg|_{mp} = I_{mp} + V_{mp}\frac{dI}{dV}\bigg|_{mp} = 0$$

> ⚠️ **Erratum (2007):** La ecuación corregida tiene **signo positivo** en $V_{mp} \cdot dI/dV$.

### Ecuación (6b) — Derivada $dI/dV$ en MPP

$$\frac{dI}{dV}\bigg|_{mp} = \frac{-\frac{I_0}{a}\exp\left(\frac{V_{mp}+I_{mp}R_s}{a}\right) - \frac{1}{R_{sh}}}{1 + \frac{I_0 R_s}{a}\exp\left(\frac{V_{mp}+I_{mp}R_s}{a}\right) + \frac{R_s}{R_{sh}}}$$

### Ecuación (7) — Coeficiente de temperatura de $V_{oc}$

$$\beta_{V_{oc}} = \frac{\partial V}{\partial T}\bigg|_{I=0} \approx \frac{V_{oc,ref} - V_{oc,T_c}}{T_{ref} - T_c}$$

---

## 4. Dependencia con Condiciones de Operación

### 4.1 Factor de idealidad

$$\frac{a}{a_{ref}} = \frac{T_c}{T_{c,ref}}$$

### 4.2 Corriente de saturación inversa $I_0$

$$\frac{I_0}{I_{0,ref}} = \left(\frac{T_c}{T_{c,ref}}\right)^3 \exp\left[\frac{1}{k}\left(\frac{E_g|_{T_{ref}}}{T_{ref}} - \frac{E_g|_{T_c}}{T_c}\right)\right]$$

### 4.3 Bandgap del material $E_g$ (dependencia con temperatura)

$$\frac{E_g}{E_{g,T_{ref}}} = 1 - 0{,}0002677 \cdot (T - T_{ref})$$

Para silicio: $E_{g,T_{ref}} = 1{,}121$ eV. Para triple unión amorfo: $E_{g,T_{ref}} = 1{,}6$ eV.

### 4.4 Corriente fotogenerada $I_L$

$$I_L = \frac{S}{S_{ref}} \cdot \frac{M}{M_{ref}} \cdot [I_{L,ref} + \alpha_{I_{sc}}(T_c - T_{c,ref})]$$

### 4.5 Resistencia serie $R_s$

Se asume **constante** e igual a $R_{s,ref}$ (la variación tiene efecto pequeño en la curva I-V).

### 4.6 Resistencia shunt $R_{sh}$

Inversamente proporcional a la irradiancia absorbida:

$$\frac{R_{sh}}{R_{sh,ref}} = \frac{S_{ref}}{S}$$

---

## 5. Modificador por Ángulo de Incidencia $K_{\tau\alpha}(\theta)$

> [!NOTE]
> **Implementado en el pipeline (Fase 2).** Las secciones 5, 6 y 7 (IAM, masa de aire y irradiancia absorbida) **ya se ejecutan** en `fase2_recurso_solar.py`: el IAM directo con `pvlib.iam.physical` (n=1.526, K=4 m⁻¹, L=2 mm), la difusa con `pvlib.iam.marion_diffuse`, y el factor espectral con `pvlib.spectrum.spectral_factor_firstsolar` (agua precipitable + masa de aire). El resultado es la irradiancia efectiva $S$ que alimenta el modelo eléctrico (antes era trabajo futuro).

### Método basado en Snell y Bouguer (no requiere datos experimentales)

1. **Ley de Snell** — ángulo de refracción:
$$\theta_r = \arcsin(n \cdot \sin\theta)$$
donde $n = 1{,}526$ (vidrio).

2. **Transmitancia del vidrio:**
$$\tau(\theta) = e^{-KL/\cos\theta_r}\left[1 - \frac{1}{2}\left(\frac{\sin^2(\theta_r - \theta)}{\sin^2(\theta_r + \theta)} + \frac{\tan^2(\theta_r - \theta)}{\tan^2(\theta_r + \theta)}\right)\right]$$
con $K = 4$ m⁻¹, $L = 2$ mm.

3. **Modificador:**
$$K_{\tau\alpha}(\theta) = \frac{\tau(\theta)}{\tau(0)}$$

Se calculan modificadores separados para radiación directa, difusa y reflejada.

---

## 6. Modificador por Masa de Aire $M$

$$\frac{M}{M_{ref}} = \sum_{i=0}^{4} a_i \cdot (AM)^i$$

$$AM = \frac{1}{\cos(\theta_z) + 0{,}5057 \cdot (96{,}080 - \theta_z)^{-1{,}634}}$$

> Se encontró que usar un solo conjunto de coeficientes (policristalino) funciona bien para todos los tipos de celda.

---

## 7. Irradiancia Absorbida $S$

$$S = (\tau\alpha)_n \left[G_b R_{\text{beam}} K_{\tau\alpha,b} + G_d K_{\tau\alpha,d}\frac{1+\cos\beta}{2} + G \rho K_{\tau\alpha,g}\frac{1-\cos\beta}{2}\right]$$

Forma normalizada para cálculos:

$$\frac{S}{S_{ref}} = \frac{G_b}{G_{ref}} R_{\text{beam}} K_{\tau\alpha,b} + \frac{G_d}{G_{ref}} K_{\tau\alpha,d}\frac{1+\cos\beta}{2} + \frac{G}{G_{ref}} \rho K_{\tau\alpha,g}\frac{1-\cos\beta}{2}$$

donde:

- $\beta$ = inclinación del panel
- $\rho$ = reflectancia del suelo (~0,2)
- $R_{\text{beam}}$ = razón geométrica de radiación directa
- $G_{ref} = 1000$ W/m²

---

## 8. Validación

El modelo fue validado contra datos de **NIST** (Fanney et al., 2002) para 4 tipos de celdas:

| Tipo de celda             | $P_{mp,ref}$ [W] | $I_{sc,ref}$ [A] | $V_{oc,ref}$ [V] | $N_s$ | $E_g$ [eV] |
|---------------------------|------------------|------------------|------------------|-------|------------|
| Silicon thin film         | 103,96           | 5,11             | 29,61            | 40    | 1,12       |
| Single-crystalline        | 133,40           | 4,37             | 42,93            | 72    | 1,12       |
| Poly-crystalline          | 125,78           | 4,25             | 41,50            | 72    | 1,14       |
| Triple junction amorphous | 57,04 (×2)       | 4,44             | 23,16            | 22    | 1,60       |

### Resultados

- El modelo de 5 parámetros **concuerda bien** con datos experimentales NIST y con el modelo de King.
- La principal ventaja: **solo requiere datos del fabricante**, sin necesidad de experimentos adicionales.
- Las diferencias podrían reducirse si se proporcionaran curvas I-V a dos niveles de irradiancia.

---

## 9. Resumen del Flujo de Trabajo De Soto

```text
┌──────────────────────────────────────────────────────┐
│ DATOS FABRICANTE (SRC)                               │
│ Isc, Voc, Imp, Vmp, αIsc, βVoc, Ns, Eg              │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ RESOLVER SISTEMA NO-LINEAL (Eqs. 3-7)               │
│ → Obtener: aref, I0,ref, IL,ref, Rs,ref, Rsh,ref    │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ PARA CADA (G, Tc) de operación:                     │
│ 1. Calcular a, I0, IL (Eqs. 8-11)                   │
│ 2. Calcular Rsh (Eq. 12), Rs = Rs,ref               │
│ 3. Calcular S/Sref (Eq. 21), M/Mref (Eq. 17)       │
│ 4. Resolver Eq. (1) → curva I-V completa            │
│ 5. Encontrar MPP → Pmp                              │
└──────────────────────────────────────────────────────┘
```

---

## 10. Puntos Conflictuales para Discusión (Tarea 2)

> [!IMPORTANT]
> El enunciado pide discutir puntos conflictuales en la identificación de parámetros:

1. **Acoplamiento $R_s$ — $n_I$:** Ambos parámetros afectan la curvatura de la curva I-V cerca del MPP. Existe una correlación fuerte que dificulta su identificación independiente.
2. **Sensibilidad de $R_{sh}$:** A baja irradiancia, $R_{sh}$ cambia significativamente. La relación inversamente proporcional (Eq. 12) es una aproximación.
3. **$R_s$ constante:** Se asume que no cambia con la temperatura, aunque en realidad hay un efecto menor.
4. **Bandgap variable:** La dependencia lineal de $E_g$ con $T$ (Eq. 10) es una simplificación.
