# Guion de la Defensa — ELI556 Tarea 2

Deck: `output/Presentacion_Final_ELI556_Atacama_POA_Tarea2_revisado.pptx` — **26 láminas presentadas + 14 anexos de respaldo** (40 en total; los anexos no se presentan, se usan en la ronda de preguntas). Cada lámina del PPTX lleva la misma nota en el panel de notas del expositor (vista Presentador de PowerPoint).

Presupuesto total: **~21.0 min**. Respecto a la versión previa se agregaron dos láminas (13 "Modificadores ópticos" y 22 "Recurso real de Atacama"); si vas justo de tiempo, las láminas marcadas ⚡ pueden contarse en una sola frase y las dos nuevas pueden resumirse en 20–25 s cada una.

| # | Lámina | Tiempo | Acumulado | Mensaje clave |
|---|---|---|---|---|
| 1 | Portada | 20 s | 0:20 | Somos consultores: ¿qué tecnología PV conviene en Atacama 2026? Respuesta con datos medidos. |
| 2 | Introducción | 60 s | 1:20 | Mejor recurso solar del mundo, pero celdas calientes: el calor degrada la potencia. |
| 3 | Justificación | 50 s | 2:10 | De 5 familias, los 2 extremos térmicos viables: m-Si (sensible) vs HIT (tolerante). |
| 4 | Marco teórico | 50 s | 3:00 | Perez + Sandia + De Soto + IAM/espectral, todos aplicados en el pipeline. |
| 5 | Pipeline | 60 s | 4:00 | Mapa del trabajo: 9 fases automatizadas de 1.2 GB crudos al PR. |
| 6 | Base de datos | 50 s | 4:50 | 11 módulos medidos cada 5 min (NREL). Usamos 11 columnas de 43. |
| 7 | Ingesta ⚡ | 45 s | 5:35 | Filas variables + sentinelas −9999 → lector streaming propio; ~96 % útil. |
| 8 | Embudo de datos ⚡ | 45 s | 6:20 | Trazabilidad: 420 mil curvas → ~64 mil registros simulados; cada filtro con número. |
| 9 | Emulación (concepto) | 60 s | 7:20 | +6 meses alinea solsticios entre hemisferios; sin esto, verano en julio. |
| 10 | Emulación (implementación) ⚡ | 45 s | 8:05 | Reescribe metadatos + fechas; ventana de 12 meses única (sin doble cobertura). |
| 11 | Verificación POA | 40 s | 8:45 | Las 11 curvas del piranómetro patrón se superponen → comparación justa. |
| 12 | Fase 2 (POA + Tc) ⚡ | 45 s | 9:30 | Perez (albedo 0.20) transpone; Sandia estima Tc con viento conservador 1 m/s. |
| 13 | **Modificadores ópticos (NUEVA)** ⚡ | 45 s | 10:15 | IAM físico (~3 % pérdida) + factor espectral (neutro): irradiancia efectiva al SDM. |
| 14 | Un día despejado | 40 s | 10:55 | La celda sigue al sol: >60 °C al mediodía. Cada grado sobre 25 °C cuesta potencia. |
| 15 | Fase 3 (flujo) ⚡ | 45 s | 11:40 | β medido; α de literatura (regresión negativa); ajuste con bounds físicos. |
| 16 | Parámetros extraídos | 60 s | 12:40 | I₀ de HIT 10× menor. Honestidad: Rs/Rsh quedan en su inicialización. |
| 17 | Fase 4 (simulación) ⚡ | 40 s | 13:20 | Cada registro 5-min: De Soto escala con G efectiva y Lambert W resuelve Pmp. |
| 18 | Validación | 55 s | 14:15 | R² 0.99 vs potencia medida — valida el circuito, no compara sitios. |
| 19 | Acoplamiento Rs–n | 60 s | 15:15 | Punto conflictual de la pauta: mal condicionado; mitigación bounds + init; nI = 1.20. |
| 20 | Pérdidas térmicas | 55 s | 16:10 | El gráfico clave: pendiente térmica de m-Si es el doble; castiga al mediodía. |
| 21 | Veredicto PR (validado) | 65 s | 17:15 | HIT 84.18 % vs 81.61 % → +2.57 pts (ya con pérdidas ópticas penalizadas). |
| 22 | **Recurso real Atacama (NUEVA)** | 55 s | 18:10 | PVGIS TMY: yields ~2,370 kWh/kWp; HIT +1.17 pts → +3,294 MWh, +USD 148k/año. |
| 23 | Cumplimiento Tarea 2 | 40 s | 18:50 | Cada requisito de la pauta: método, lámina de evidencia y resultado. |
| 24 | Limitaciones | 60 s | 19:50 | Resuelto: IAM/AM, albedo 0.20, doble cobertura, recurso real. Queda: validación in-situ, soiling, BOS. |
| 25 | Conclusiones | 60 s | 20:50 | HIT gana por física en ambos tracks. Futuro: in-situ, soiling, BOS, doble diodo. |
| 26 | Referencias | 10 s | 21:00 | Gracias — ronda de preguntas. |

## Anexos de respaldo (ronda de preguntas)

| Anexo | Lámina | Úsalo si preguntan por… |
|---|---|---|
| Herramientas | 27 | Librerías/herramientas de código usadas (pvlib, pandas, scipy, pptx, PVGIS…) |
| I | 28 | Ecuación de transposición de Perez / albedo 0.20 |
| II | 29 | IAM y corrección espectral (marco APLICADO en Fase 2) |
| III | 30 | Ecuación SAPM y coeficientes a, b, ΔT |
| IV | 31 | Ecuación del diodo / factor de idealidad |
| V | 32 | Cómo se ajustaron los 5 parámetros (minimize + bounds) |
| VI | 33 | Escalamiento De Soto a condiciones de operación |
| VII | 34 | Definición exacta del PR (IEC 61724-1) |
| VIII | 35 | Diccionario de columnas del CSV |
| IX | 36 | Anatomía del archivo y decisiones de ingesta |
| X | 37 | Contraste climático Florida vs Atacama |
| XI | 38 | Verificación del recurso (notas metodológicas) |
| XII | 39 | Distribución anual de temperatura de celda |
| XIII | 40 | Supuestos del cálculo económico (recurso real) |

## Respuestas preparadas (anticipación de preguntas)

1. **"¿Por qué Rs = 0.01 Ω en ambos módulos?"** — Con solo 3 condiciones (Isc, Voc, MPP) el residuo es casi insensible a Rs y Rsh: es la manifestación directa del mal condicionamiento Rs–n que pide discutir la pauta. Los bounds y la inicialización analítica garantizan valores físicamente plausibles, y la validación R² ≈ 0.99 confirma que el conjunto reproduce la potencia medida.
2. **"¿El PR no debería usar el recurso real de Atacama?"** — Tenemos dos tracks. El **emulado** valida el modelo eléctrico con datos NREL medidos (R² ≈ 0.99); ahí las magnitudes son de Florida. El **track real** (Fase 8) usa el TMY de PVGIS para San Pedro de Atacama (POA ≈ 2,810 kWh/m²·año) y entrega energía y economía absolutas. HIT gana en ambos: +2.57 pts (emulado) y +1.17 pts (real).
3. **"¿Por qué la ventaja de HIT cae a +1.17 pts con el recurso real?"** — Porque San Pedro de Atacama está a 2,400 m: aire frío (máx 29 °C) y ventilado (2.67 m/s), así que la celda solo llega a ~58–62 °C (vs 70–73 °C en el escenario emulado). Menor temperatura → menor castigo térmico → menor brecha. Aun así HIT gana y la energía absoluta es ~2.3× mayor.
4. **"¿Cómo aplicaron el IAM y la corrección espectral?"** — En la Fase 2, sobre la POA de Perez: IAM físico de Snell-Bouguer (`pvlib.iam.physical`, n=1.526, K=4, L=2 mm) para la directa y factores de Marion para la difusa; el factor espectral usa el modelo First Solar (`spectral_factor_firstsolar`) con agua precipitable y masa de aire. El resultado (POA·IAM·M) es la irradiancia efectiva que fotogenera I_L. Efecto en Atacama: ~3 % de pérdida óptica, espectral casi neutra.
5. **"¿Por qué α_Isc de literatura?"** — La regresión experimental dio pendiente negativa (efecto espectral/estacional dominante sobre el térmico); +0.05 %/°C es el valor estándar y su impacto en el PR es de segundo orden porque la corriente la domina G.
6. **"¿De dónde salen los datos meteorológicos reales de Atacama?"** — De **PVGIS** (Photovoltaic Geographical Information System), del Joint Research Centre de la Comisión Europea (base satelital SARAH), descargados con `pvlib.iotools.get_pvgis_tmy` como Año Meteorológico Típico horario para San Pedro de Atacama. GHI anual ≈ 2,596 kWh/m².
7. **"¿Por qué no CdTe si su coeficiente es excelente?"** — Mayor contraste metodológico con HIT (premium c-Si) y barreras de toxicidad/cadena de suministro; el objetivo era cuantificar el castigo térmico del estándar comercial vs la alternativa premium.
