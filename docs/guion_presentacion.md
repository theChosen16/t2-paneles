# Guion de la Defensa — ELI556 Tarea 2 (20 minutos estrictos)

Deck: `output/Presentacion_Final_ELI556_Atacama_POA_Tarea2_revisado.pptx` — **24 láminas presentadas + 13 anexos de respaldo** (no se presentan; se usan en la ronda de preguntas). Cada lámina del PPTX lleva la misma nota en el panel de notas del expositor (vista Presentador de PowerPoint).

Presupuesto total: **19.4 min** (~35 s de colchón). Si vas atrasado, las láminas marcadas ⚡ pueden contarse en una sola frase.

| # | Lámina | Tiempo | Acumulado | Mensaje clave |
|---|---|---|---|---|
| 1 | Portada | 20 s | 0:20 | Somos consultores: ¿qué tecnología PV conviene en Atacama 2026? Respuesta con datos medidos. |
| 2 | Introducción | 60 s | 1:20 | Mejor recurso solar del mundo, pero celdas a 65–73 °C: el calor degrada la potencia. |
| 3 | Justificación | 50 s | 2:10 | De 5 familias, los 2 extremos térmicos viables: m-Si (sensible) vs HIT (tolerante). |
| 4 | Marco teórico | 50 s | 3:00 | Perez + Sandia + De Soto encadenados. IAM/AM revisados pero NO aplicados (honestidad). |
| 5 | Pipeline | 60 s | 4:00 | Mapa del trabajo: 5 fases automatizadas de 1.2 GB crudos al PR. |
| 6 | Base de datos | 50 s | 4:50 | 11 módulos medidos cada 5 min (NREL). Usamos 11 columnas de 43. |
| 7 | Ingesta ⚡ | 45 s | 5:35 | Filas variables + sentinelas −9999 → lector streaming propio; 97 % útil. |
| 8 | Embudo de datos ⚡ | 45 s | 6:20 | Trazabilidad: 420 mil curvas → 73 mil registros simulados; cada filtro con número y razón. |
| 9 | Emulación (concepto) | 60 s | 7:20 | +6 meses alinea solsticios entre hemisferios; sin esto, verano en julio. |
| 10 | Emulación (implementación) ⚡ | 45 s | 8:05 | Se reescriben metadatos y fechas; las magnitudes físicas NO se tocan (límite declarado). |
| 11 | Verificación POA | 40 s | 8:45 | Las 11 curvas del piranómetro patrón se superponen → comparación justa. |
| 12 | Fase 2 (POA + Tc) ⚡ | 45 s | 9:30 | Perez transpone al plano; Sandia estima Tc con viento conservador 1 m/s. |
| 13 | Un día despejado | 40 s | 10:10 | La celda sigue al sol: >60 °C al mediodía. Cada grado sobre 25 °C cuesta potencia. |
| 14 | Fase 3 (flujo) ⚡ | 45 s | 10:55 | β medido; α de literatura (regresión negativa); ajuste con bounds físicos. |
| 15 | Parámetros extraídos | 60 s | 11:55 | I₀ de HIT 10× menor. Honestidad: Rs/Rsh quedan en su inicialización. |
| 16 | Fase 4 (simulación) ⚡ | 40 s | 12:35 | Cada registro 5-min: De Soto escala el circuito y Lambert W resuelve Pmp. |
| 17 | Validación | 55 s | 13:30 | R² 0.99 vs potencia medida — valida el circuito, no compara sitios. |
| 18 | Acoplamiento Rs–n | 60 s | 14:30 | Punto conflictual de la pauta: mal condicionado; mitigación bounds + init; nI = 1.20. |
| 19 | Pérdidas térmicas | 55 s | 15:25 | El gráfico clave: pendiente térmica de m-Si es el doble; castiga al mediodía. |
| 20 | Veredicto + economía | 70 s | 16:35 | HIT 86.92 % vs 84.53 % → +2.39 pts ≈ 6,000 MWh y USD 270k/año en 100 MWp. |
| 21 | Cumplimiento Tarea 2 | 40 s | 17:15 | Cada requisito de la pauta: método, lámina de evidencia y resultado. |
| 22 | Limitaciones | 60 s | 18:15 | Magnitudes de Florida (comparación válida, absolutos conservadores); sin pérdidas ópticas/planta. |
| 23 | Conclusiones | 60 s | 19:15 | HIT gana por física. Futuro: IAM/AM, TMY Atacama, soiling, doble diodo. |
| 24 | Referencias | 10 s | 19:25 | Gracias — ronda de preguntas. |

## Anexos de respaldo (ronda de preguntas)

| Anexo | Lámina | Úsalo si preguntan por… |
|---|---|---|
| I | 25 | Ecuación de transposición de Perez / albedo |
| II | 26 | IAM y corrección espectral (marco NO aplicado) |
| III | 27 | Ecuación SAPM y coeficientes a, b, ΔT |
| IV | 28 | Ecuación del diodo / factor de idealidad |
| V | 29 | Cómo se ajustaron los 5 parámetros (minimize + bounds) |
| VI | 30 | Escalamiento De Soto a condiciones de operación |
| VII | 31 | Definición exacta del PR (IEC 61724-1) |
| VIII | 32 | Diccionario de columnas del CSV |
| IX | 33 | Anatomía del archivo y decisiones de ingesta |
| X | 34 | Contraste climático Florida vs Atacama |
| XI | 35 | Verificación del recurso (notas metodológicas) |
| XII | 36 | Distribución anual de temperatura de celda |
| XIII | 37 | Supuestos del cálculo económico |

## Respuestas preparadas (anticipación de preguntas)

1. **"¿Por qué Rs = 0.01 Ω en ambos módulos?"** — Con solo 3 condiciones (Isc, Voc, MPP) el residuo es casi insensible a Rs y Rsh: es la manifestación directa del mal condicionamiento Rs–n que pide discutir la pauta. Los bounds y la inicialización analítica garantizan valores físicamente plausibles, y la validación R² ≈ 0.99 confirma que el conjunto reproduce la potencia medida.
2. **"¿El PR no debería usar el recurso real de Atacama?"** — La emulación alinea estaciones y geometría; las magnitudes son de Florida. El PR es un cociente normalizado por el propio recurso, así que la comparación m-Si vs HIT es válida; los valores absolutos de energía son conservadores (Limitaciones, Lám. 22).
3. **"¿Por qué α_Isc de literatura?"** — La regresión experimental dio pendiente negativa (efecto espectral/estacional dominante sobre el térmico); +0.05 %/°C es el valor estándar y su impacto en el PR es de segundo orden porque la corriente la domina G.
4. **"¿Por qué no CdTe si su coeficiente es excelente?"** — Mayor contraste metodológico con HIT (premium c-Si) y barreras de toxicidad/cadena de suministro; el objetivo era cuantificar el castigo térmico del estándar comercial vs la alternativa premium.
