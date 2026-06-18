# Análisis Crítico de la Presentación (versión 26 láminas) — ELI556 T2

Auditoría realizada contrastando cada lámina contra el código fuente real (`src/fase0-7`), las bases de datos (`Base datos original/Cocoa`, `data/`) y los resultados de simulación (`output/Fase2_Resultados`). Fecha: 2026-06-10.

---

## ✅ ESTADO DE RESOLUCIÓN (actualización metodológica)

Varias incoherencias de esta auditoría **ya fueron resueltas** implementando la metodología que antes solo se describía:

| Issue | Estado | Cómo se resolvió |
|---|---|---|
| **A1** IAM/AM presentados pero no ejecutados | ✅ RESUELTO | IAM físico + factor espectral aplicados en `fase2` (irradiancia efectiva = POA·IAM·M). Anexo II ahora dice "APLICADO". |
| **A4** Cadencia "minutal" falsa | ✅ RESUELTO | Texto corregido a "5 min" y energía integrada con Δt = 5/60 h. |
| **A5** Albedo 0.20 vs 0.25 | ✅ RESUELTO | `albedo=0.20` declarado explícitamente en código y deck. |
| **A9** Recurso de Florida, no Atacama | ✅ RESUELTO (añadido) | Nueva `fase8` con TMY real de PVGIS (POA ≈ 2,810 kWh/m²·año); el track emulado se conserva para validar el modelo eléctrico. |
| **A10** Economía con escalado no declarado | ✅ RESUELTO | Economía recalculada con el recurso real: +3,294 MWh/+USD 148k (sin supuestos ocultos). |
| **A12** Meses con doble cobertura | ✅ RESUELTO | Ventana de 12 meses contiguos en `fase1` + dedup en `fase2`. |
| **A6** P_STC del PR | ✅ Declarado | Deck usa P_STC del SDM (50.1/238.0 W) y lo declara explícitamente. |
| **A2, A3, A7, A8, A11, A13–A15** | ✅ Ya corregidos | en la reestructura del deck (24+13 → 26+14, con anexo de herramientas). |

**Números vigentes (post-mejoras):** PR emulado m-Si 81.61 % / HIT 84.18 % (+2.57 pts); PR real m-Si 83.82 % / HIT 84.99 % (+1.17 pts). El detalle histórico de cada issue se conserva abajo como referencia.

---

## A. Incoherencias código ↔ presentación (críticas)

**A1. IAM y modificador espectral (AM) presentados como aplicados, pero NO se ejecutan.**
Las láminas 9, 20 (Anexo I, panel derecho) y 21 (Anexo II completo) describen pérdidas ópticas por ángulo de incidencia (Snell/Bouguer, vidrio 2 mm, n=1.526) y corrección de masa de aire de 4.º orden como parte del procedimiento. En el código, `fase2_recurso_solar.py` calcula POA con Perez y la pasa **directamente** como irradiancia efectiva a `calcparams_desoto` en `fase4`. No existe ninguna llamada a `pvlib.iam.*` ni a `spectral_factor_*`. → Resolución: mover IAM/AM a "marco teórico no aplicado / trabajo futuro".

**A2. Anexo V: "Derivada Analítica Completa en MPP" inexistente en el código.**
`fase3_extraccion_parametros.py` NO usa la condición dP/dV=0 ni la derivada dI/dV con coeficientes A y B. El ajuste real: `scipy.optimize.minimize` sobre la suma de errores cuadráticos de **3 ecuaciones** (Isc, Voc, MPP) con 5 incógnitas, regularizado con bounds físicos (Rs∈[0.001,2], Rsh∈[100,10⁴], a∈[0.5a₀,2a₀], IL±10%, Io∈[10⁻¹²,10⁻⁵]) e inicialización analítica (a₀ = Ns·1.2·kT/q; Io₀ = Isc·exp(−Voc/a₀)). Sistema subdeterminado: la unicidad la dan los bounds, no la derivada.

**A3. α_Isc experimental falla y se sustituye silenciosamente.**
La regresión lineal de Isc normalizada vs Tc arroja pendiente **negativa** en ambos módulos (m-Si: −0.00099 A/°C; HIT: −0.0039 A/°C), físicamente inválida. El código activa el fallback `alpha_isc = Isc_ref·0.0005` (+0.05 %/°C típico de literatura). La presentación dice que los coeficientes se "calcularon directamente de los datos" — solo es cierto para β_Voc (m-Si: −0.0666 V/°C ≈ −0.30 %/°C; HIT: −0.1075 V/°C ≈ −0.21 %/°C).

**A4. Cadencia "minuto a minuto" / "simulación minutal" — falso.**
El dataset NREL registra una curva I-V cada **5 minutos**, solo en horas de sol (p. ej. 08:15–18:10 en invierno). Láminas 6, 9, 11, 12, 14 hablan de datos/simulación "minutal".

**A5. Albedo declarado 0.20; el código usa 0.25.**
`get_total_irradiance` se llama sin argumento `albedo` → usa el default de pvlib (0.25). Láminas 9 y 20 afirman 0.20.

**A6. P_STC del glosario del PR no es el usado en el cálculo.**
Lámina 26 declara P_STC m-Si 46.68 W y HIT 217.52 W (Vmp_ref·Imp_ref promediados de datos). El denominador real del PR usa el P_STC **resuelto con el SDM ajustado**: m-Si 50.17 W, HIT 236.72 W (~+7–9 %). Esto deprime levemente el PR reportado y debe declararse.

**A7. "Se descartaron registros nocturnos (G<10 W/m²)" — inexacto.**
El filtro G>10 solo se usa para el histograma de Tc. La limpieza real: −9999→NaN, dropna en GHI/DNI/DHI/T_air, clip(≥0). La cifra "acelerando 95%" no tiene soporte. Conteos reales: m-Si 36,765→35,669 filas válidas (97.0 %); HIT 38,377→37,313 (97.2 %).

**A8. Ejes del scatter de validación engañosos.**
"Pmp Medida (Florida)" vs "Pmp Simulada (Atacama)" sugiere comparación entre sitios. Ambas series comparten exactamente la misma meteorología (desplazada): es una validación del modelo eléctrico bajo condiciones idénticas, no una comparación Florida-Atacama.

**A9. La magnitud del recurso sigue siendo de Florida (limitación central no declarada).**
POA anual simulada: m-Si 1,363 / HIT 1,422 kWh/m²·año — magnitudes de Cocoa, no de Atacama (POA real esperable ≳2,500). La lámina 2 promociona "GHI > 2,900 kWh/m²" creando expectativa falsa. La emulación alinea estaciones y geometría solar; NO escala irradiancia, ni DNI/clearness, ni humedad. Es la limitación más importante del estudio y no aparece en ninguna lámina.

**A10. Impacto financiero (+6,000 MWh, +USD 270k) solo cuadra con supuestos no declarados.**
Con el recurso simulado real (~1,400 kWh/m²): ΔE = 0.0239×1,400 ≈ 33 kWh/kWp → ~3,300 MWh por 100 MWp (~USD 150k a 45 USD/MWh). Los 6,000 MWh requieren escalar el recurso a ~2,500 kWh/m²·año POA de Atacama. Debe presentarse con los supuestos explícitos.

**A11. TODAS las referencias cruzadas a anexos están desfasadas en 1.**
Anexo I está en lámina 20 (citado como 19), Anexo III en 22 (citado 21), Anexo IV en 23 (citado 22), Anexo VI en 25 (citado 24), Anexo VII en 26 (citado 25).

**A12. Meses con doble cobertura no declarados.**
El dataset cubre 21-ene-2011 → 04-mar-2012 (13.5 meses). Tras +6 meses y forzar año 2026, julio–septiembre 2026 mezclan datos de dos años distintos (ene–mar 2011 y ene–mar 2012).

**A13. Infografía "4-STEP ENGINEERING SIMULATION PIPELINE" (lámina 5).**
En inglés, genérica, dice 4 pasos mientras el texto adyacente lista 5 etapas, y no refleja las fases reales 0–7 del repositorio.

**A14. Ficha/descripcion de fase0 inexacta.**
`fase0_setup.py` no "descarga/valida la base Cocoa": busca coincidencias de nombres de módulos en las bases CEC/Sandia de pvlib.

**A15. Bug menor:** `fase3` escribe `temp/parametros_desoto.json` sin crear el directorio `temp/` (`os.makedirs` ausente) — falla en repos limpios.

## B. Errores visuales / de formato detectados

**B1.** Láminas 9 y 22: literales de código rotos por el mini-parser de markdown — `TEMPERATURE_MODEL_PARAMETERS` y `open_rack_glass_polymer` se renderizan con cursivas que se comen los guiones bajos.
**B2.** Lámina 15: marcas crudas visibles: `(_R_[_sh_])`, `(_G_)`, `_R_[_s_]`, `*Impacto:*`, `*Justificación:*`.
**B3.** Asteriscos literales `*(Ecuación en Anexo …)*` visibles en láminas 9, 11, 12, 16.
**B4.** Desequilibrio de densidad: paneles con 35–45 % de espacio vacío inferior (láminas 2, 6, 9–12, 15, 18).
**B5.** Lámina 8: leyenda de 11 series diminuta y nota al pie casi ilegible.

## C. Gaps de información (contenido faltante)

**C1.** No existe lámina que explique la base de datos original: estructura del CSV (2 líneas de metadatos, 43 columnas fijas + pares I-V de longitud variable), cadencia 5 min, periodo, solo horas de sol, columnas de incertidumbre, qué columnas se usan y cuáles se descartan.
**C2.** No hay diagramas de flujo reales de los códigos por fase (entrada → proceso → salida → archivo generado).
**C3.** No hay "embudo de datos" con conteos reales por etapa de filtrado (36,765 → 35,669 → 5,791 SRC, etc.).
**C4.** No se justifica la elección de los módulos específicos (mSi0166 entre 4 cristalinos; HIT05667 único heterounión).
**C5.** Columnas de QA disponibles y no usadas (Solar QA residual, soiling derate) sin mención.
**C6.** Faltan parámetros numéricos: a_ref, Ns, α_Isc y β_Voc extraídos; solo se muestran 4 de los 7 valores relevantes.
**C7.** Falta declarar P_STC real del PR y la energía DC anual por panel (m-Si 57.8 kWh; HIT 292.6 kWh; yield 1,152 vs 1,236 kWh/kWp).

## D. Datos duros verificados (para el nuevo deck)

| Métrica | m-Si (mSi0166) | HIT (HIT05667) |
|---|---|---|
| Filas brutas | 36,765 | 38,377 |
| Filas válidas tras limpieza | 35,669 (97.0 %) | 37,313 (97.2 %) |
| Ventana térmica 800–1200 W/m² | 8,635 | 9,004 |
| Ventana SRC 900–1100 W/m² | 5,791 | 6,027 |
| β_Voc (regresión) | −0.0666 V/°C (−0.30 %/°C) | −0.1075 V/°C (−0.21 %/°C) |
| α_Isc | fallback +0.05 %/°C (regresión negativa) | fallback +0.05 %/°C (regresión negativa) |
| Ns | 36 | 72 |
| Isc_ref / Voc_ref | 2.769 A / 22.55 V | 5.607 A / 51.51 V |
| P_STC (SDM, usado en PR) | 50.17 W | 236.72 W |
| POA anual simulada | 1,363 kWh/m² | 1,422 kWh/m² |
| Energía DC anual | 57.8 kWh | 292.6 kWh |
| Yield específico | 1,152 kWh/kWp | 1,236 kWh/kWp |
| PR anual | 84.53 % | 86.92 % |
| PR mensual (min–max) | 82.0–88.0 % | 84.9–89.4 % |
| Tc máx / horas Tc>65 °C | 70.2 °C / 63 reg. | 73.4 °C / 461 reg. |
