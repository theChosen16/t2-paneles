# Estudio: Unión P-N y Modelación Eléctrica (ELI556 — Parte 2)

> **Fuente:** ELI556_MODELADO_ELÉCTRICO_PV_2.pdf — PhD Carlos Cárdenas-Bravo, UTFSM, 2026-1

---

## 1. Recapitulación Clave

1. **Efecto Fotoeléctrico:** Fotones con $E > E_g$ (1,12 eV para Si) promueven electrones a la banda de conducción.
2. **Estadística de Portadores:** Depende de la Densidad de Estados (DoS) y Fermi-Dirac.
3. **Dopaje:** Desplaza el nivel de Fermi, rompiendo el equilibrio intrínseco.

---

## 2. Conceptos Clave del Semiconductor Dopado

### Equilibrio térmico

- Se cumple la ley de acción de masas: $p \cdot n = n_i^2$
- Portadores en movimiento térmico aleatorio sin flujo neto de corriente.

### Equilibrio térmico perturbado

- Se rompe la ley de acción de masas: $p \cdot n \neq n_i^2$
- Causas: radiación incidente, campos eléctricos, inyección de energía.
- Se activan dos mecanismos de transporte: **deriva (drift)** y **difusión (diffusion)**.

---

## 3. Mecanismos de Transporte de Carga

### Corriente de deriva (drift)

Ocurre bajo un campo eléctrico $\mathcal{E}$:

$$J_{\text{drift},p} = q \cdot p \cdot \mu_p \cdot \mathcal{E}$$

donde $\mu_p$ es la movilidad eléctrica de huecos.

### Corriente de difusión (diffusion)

Surge por gradiente de concentración de portadores:

$$J_{\text{diff},p} = q \cdot D_p \cdot \nabla p$$

donde $D_p$ es el coeficiente de difusión.

### Corriente total

$$J_{\text{total}} = J_{\text{drift}} + J_{\text{diff}}$$

---

## 4. Conservación de Portadores de Carga

$$q\frac{\partial p}{\partial t} = \nabla J_p + q G_p - q R_p$$

Tres componentes: generación ($G$), recombinación ($R$), y flujo de corriente.

### Difusión de portadores minoritarios

Para un material tipo-N, la concentración de huecos (minoritarios):

$$p_n(x) = p_{n,0} + (p_n(0) - p_{n,0}) \exp\left(-\frac{x}{L_p}\right)$$

donde $L_p$ es la longitud de difusión.

---

## 5. La Unión P-N

### Definiciones fundamentales

- **Unión p-n:** dos semiconductores (tipo-p y tipo-n) que comparten una superficie.
- Los portadores mayoritarios se recombinan generando la **región de agotamiento** (depletion region / space charge region).
- En dicha región existe un **potencial interno** $V_{bi}$ (built-in voltage).
- El ancho de la zona de agotamiento: $W_D = x_p + x_n$, donde $W_D \propto \sqrt{V_{bi}}$.

### Operación en oscuridad (sin iluminación)

La difusión domina; corriente en la juntura:

$$I = I_0 \left(\exp\left(\frac{V}{V_t}\right) - 1\right)$$

donde la **tensión térmica**:

$$V_t = \frac{k_B T}{q}$$

La **corriente de saturación** $I_0$:

$$I_0 = A \cdot q \left(\frac{D_p p_{n0}}{L_p} + \frac{D_n n_{p0}}{L_n}\right)$$

---

## 6. Operación en Iluminación (Celda Solar)

La celda solar es esencialmente una unión p-n expuesta a la luz.

### Componentes de la corriente fotovoltaica

Cuatro componentes:

$$I_{pv} = A\left[J_p(-x_n) + J_n(x_p) + q\int_{-x_n}^{x_p}(G_n - R_n)dx\right]$$

1. Generación de portadores minoritarios en zonas cuasineutras (2 términos)
2. Generación óptica de pares electrón-hueco
3. Recombinación en zona de agotamiento y cuasineutra

### Ecuación de la corriente fotovoltaica

$$I_{pv} = I_{ph} - I_{0,\text{cuasi}}\left(\exp\left(\frac{V_{pv}}{V_t}\right)-1\right) - I_{0,\text{depletion}}\left(\exp\left(\frac{V_{pv}}{2V_t}\right)-1\right)$$

> **Nota:** El segundo término exponencial (factor 2 en $V_t$) corresponde a la recombinación en la zona de agotamiento — base del **modelo de doble diodo**.

---

## 7. Límites de Conversión

### Límite de Shockley-Queisser

- Eficiencia máxima teórica: **~26 %–29 %** para materiales con bandgap entre 1,4 y 1,6 eV.

### Factores de pérdidas

| Factor             | Descripción                                          |
|--------------------|------------------------------------------------------|
| Falta de absorción | Fotones con $E < E_g$ no son absorbidos              |
| Termalización      | Fotones de alta energía disipan el exceso como calor |
| Recombinación      | Múltiples etapas de recombinación mejoran eficiencia |

### Límites superiores

- Con infinitas etapas de recombinación: **~86 %**
- **Límite de Landsberg** (máquina térmica ideal): **93,33 %**

---

## Resumen — Cierre Épico

1. **La Unión P-N:** La luz genera portadores; el campo eléctrico interno de la zona de agotamiento los separa para producir corriente útil.
2. **El Conflicto Fundamental:** Balance entre corriente extraída por iluminación y pérdidas por difusión al aumentar el voltaje.
3. **Límites de Conversión:** Desde el 30 % de Shockley-Queisser hasta el 93,3 % termodinámico — inmenso margen para innovar.
