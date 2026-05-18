# Estudio: Física de Celdas Solares (ELI556 — Parte 1)

> **Fuente:** ELI556_MODELADO_ELÉCTRICO_PV_1.pdf — PhD Carlos Cárdenas-Bravo, UTFSM, 2026-1

---

## 1. Contexto Histórico

| Año  | Hito                                         | Autor(es)                |
|------|----------------------------------------------|--------------------------|
| 1839 | Descubrimiento del efecto fotoeléctrico      | A. E. Becquerel          |
| 1873 | Fotoconductividad                            | W. Smith                 |
| 1876 | Fotoconductividad en Selenio                 | W.G. Smith y R. Evans    |
| 1883 | Primera celda solar (~1 % eficiencia)        | C. Fritts                |
| 1887 | Observación del efecto fotoeléctrico         | H. Hertz                 |
| 1905 | Explicación teórica del efecto fotoeléctrico | A. Einstein              |
| 1941 | Primer dispositivo fotovoltaico de silicio   | R.S. Ohl                 |
| 1954 | Celda solar de silicio con ~6 % eficiencia   | Pearson, Chapin y Fuller |

---

## 2. Efecto Fotoeléctrico

La **energía de un fotón** está dada por:

$$E = h\nu$$

donde:

- $h \approx 6{,}626 \times 10^{-34}$ J·s (constante de Planck)
- $\nu$ es la frecuencia de la onda electromagnética

### Función de trabajo $\varphi$

Un fotón puede expulsar un electrón con energía cinética máxima:

$$K_{\max} = h\nu - \varphi$$

donde $\varphi$ es la **energía mínima** requerida para remover un electrón del material. La radiación incidente debe tener frecuencia superior a la frecuencia umbral.

> **Relación frecuencia-longitud de onda:** $c = \lambda \times \nu$, con $c \approx 3 \times 10^8$ m/s.

---

## 3. Estructura de Bandas y Semiconductores

### Teoría de Bandas

- Los átomos de silicio comparten electrones en enlaces covalentes.
- A $T = 0$ K, los electrones están fijos; al aumentar $T$ se rompen enlaces → electrones libres + huecos.
- El **silicio** tiene 14 protones y 14 electrones, con **bandgap** $E_g = 1{,}12$ eV.

### Clasificación de Materiales

| Material      | $E_g$       | Ejemplo  |
|---------------|-------------|----------|
| Conductor     | $\approx 0$ | Cobre    |
| Semiconductor | $\sim 1$ eV | Silicio  |
| Aislante      | $> 3$ eV    | Diamante |

---

## 4. Densidad de Estados (DoS)

### Banda de conducción

$$g_c(E) = \frac{1}{2\pi^2}\left(\frac{2m_n^*}{\hbar^2}\right)^{3/2} \sqrt{E - E_c}$$

### Banda de valencia

$$g_v(E) = \frac{1}{2\pi^2}\left(\frac{2m_p^*}{\hbar^2}\right)^{3/2} \sqrt{E_v - E}$$

Para silicio a 300 K:

- $m_n^* \approx 6 \times 0{,}33 \times m_0$
- $m_p^* \approx 0{,}54 \times m_0$

---

## 5. Distribución de Fermi-Dirac

Probabilidad de que un estado de energía $E$ esté ocupado:

$$f(E; E_f, T) = \frac{1}{1 + e^{(E - E_f)/k_B T}}$$

**Casos especiales:**

- $E = E_F$ → $f = 0{,}5$
- $T \to 0$ K → función escalón
- $T > 0$ K, $E > E_f$ → probabilidad decreciente exponencialmente

---

## 6. Densidad de Electrones y Huecos

### Electrones (banda de conducción)

$$n_0 = N_c \exp\left(-\frac{E_c - E_f}{k_B T}\right)$$

donde $N_c = 2\left(\frac{2\pi m_n^* k_B T}{h^2}\right)^{3/2}$

### Huecos (banda de valencia)

$$p_0 = N_v \exp\left(\frac{E_v - E_f}{k_B T}\right)$$

donde $N_v = 2\left(\frac{2\pi m_p^* k_B T}{h^2}\right)^{3/2}$

### Nivel de Fermi intrínseco

$$E_{f,i} = \frac{E_c + E_v}{2} + \frac{k_B T}{2}\ln\left(\frac{N_v}{N_c}\right)$$

---

## 7. Ley de Acción de Masas

$$n_0 \times p_0 = n_i^2$$

Concentración intrínseca:

$$n_i = \sqrt{N_c N_v} \exp\left(-\frac{E_g}{2k_B T}\right)$$

> **Clave:** El producto $n_0 \cdot p_0$ es constante e independiente del dopaje.

---

## 8. Dopaje

### Tipo-N (donadores $N_D$)

- Portadores mayoritarios: electrones ($n_n$)
- Portadores minoritarios: huecos ($p_n$)
- $n_0 \approx N_D$

$$E_{f,n} = E_{f,i} + k_B T \ln\left(\frac{N_D}{n_i}\right)$$

### Tipo-P (aceptores $N_A$)

- Portadores mayoritarios: huecos ($p_p$)
- Portadores minoritarios: electrones ($n_p$)
- $p_0 \approx N_A$

$$E_{f,p} = E_{f,i} - k_B T \ln\left(\frac{N_A}{n_i}\right)$$

> El dopaje típico es de 0,00002 % a 0,2 %.

---

## Resumen — Cierre Épico

1. **Interacción Luz-Materia:** Los fotones superan $E_g$ del silicio (1,12 eV), promoviendo electrones a la banda de conducción.
2. **Estadística de Portadores:** La cantidad de carga depende de la DoS y la probabilidad Fermi-Dirac.
3. **Dopaje y Nivel de Fermi:** Las impurezas rompen el equilibrio intrínseco; $E_F$ se desplaza para reflejar la conductividad asimétrica.
