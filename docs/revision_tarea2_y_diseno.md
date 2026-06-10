# Revisión Tarea 2 y Diseño - Presentación ELI556

## Entregables generados
- Gráfica POA: `C:\Users\alean\Desktop\Tareas\T2 paneles\outputs\poa_irradiance_cmp22.png`
- Presentación revisada: `C:\Users\alean\Desktop\Tareas\T2 paneles\output\Presentacion_Final_ELI556_Atacama_POA_Tarea2_revisado.pptx`
- CSV usados: 11 archivos desde `C:\Users\alean\Desktop\Tareas\T2 paneles\Base datos original\Cocoa`
- Registros válidos graficados: 421,664; omitidos por calidad: 0
- Rango total de medición: 2011-01-21 08:10 a 2012-03-04 18:10; rango común: 2011-01-21 a 2012-02-25

## Checklist contra Tarea 2.pdf
| Requisito | Estado | Evidencia buscada |
|---|---:|---|
| Portada completa: título, integrantes y curso | Cumple | integrantes, eli556, evaluación de tecnologías fotovoltaicas |
| Numeración de láminas | Cumple | lámina 1/26, lámina 26/26 |
| Introducción y contextualización del problema | Cumple | introducción, desierto de atacama, contextualización |
| Justificación e impacto | Cumple | justificación, impacto, selección de tecnologías |
| Marco referencial/literatura pertinente | Cumple | marco referencial, de soto, pvlib |
| Desarrollo, análisis crítico y discusión de resultados | Cumple | desarrollo y discusión, performance ratio, puntos conflictuales |
| Conclusiones y trabajos futuros | Cumple | conclusiones, trabajos futuros |
| Referencias | Cumple | referencias, de soto, marion |
| Base de datos Cocoa para Grupo AT | Cumple | cocoa, nrel |
| Ubicación Atacama y supuestos geométricos | Cumple | san pedro de atacama, azimut, inclinación |
| Caracterización del recurso solar y Gpoa/POA | Cumple | gpoa, poa, cmp22 |
| Perfil térmico con modelo Sandia/SAPM | Cumple | sandia, sapm, temperatura de celda |
| Modelo eléctrico SDM De Soto y cinco parámetros | Cumple | modelo de 5 parámetros, i0,ref, rs,ref |
| Discusión Rs - n y supuestos conflictuales | Cumple | acoplamiento rs, factor de idealidad, mal condicionado |
| Performance Ratio anual 2026 y recomendación | Cumple | 86.92%, 84.53%, recomendación técnica/conclusión técnica |

## Resumen de datos POA CMP22
| CSV | Filas válidas | Días | Inicio | Fin | POA max (W/m²) |
|---|---:|---:|---|---|---:|
| Cocoa_aSiMicro03036.csv | 39,037 | 339 | 2011-01-21 | 2012-03-04 | 1433.6 |
| Cocoa_aSiTandem72-46.csv | 39,186 | 341 | 2011-01-21 | 2012-03-04 | 1436.4 |
| Cocoa_aSiTriple28324.csv | 38,485 | 338 | 2011-01-21 | 2012-03-04 | 1437.8 |
| Cocoa_CdTe75638.csv | 39,080 | 340 | 2011-01-21 | 2012-03-04 | 1434.0 |
| Cocoa_CIGS39017.csv | 34,775 | 301 | 2011-01-21 | 2012-02-25 | 1439.1 |
| Cocoa_CIGS8-001.csv | 38,939 | 339 | 2011-01-21 | 2012-03-04 | 1439.5 |
| Cocoa_HIT05667.csv | 38,377 | 336 | 2011-01-21 | 2012-03-04 | 1438.2 |
| Cocoa_mSi0166.csv | 36,765 | 316 | 2011-01-21 | 2012-03-04 | 1387.4 |
| Cocoa_mSi0188.csv | 39,102 | 341 | 2011-01-21 | 2012-03-04 | 1443.5 |
| Cocoa_mSi460A8.csv | 38,929 | 340 | 2011-01-21 | 2012-03-04 | 1364.3 |
| Cocoa_xSi12922.csv | 38,989 | 340 | 2011-01-21 | 2012-03-04 | 1439.6 |

## Correcciones aplicadas
- Se agregó una nueva lámina después del tratamiento de datos con una gráfica única de POA CMP22 para los 11 CSV Cocoa.
- Se usaron curvas finas semitransparentes por archivo y una mediana dorada destacada para mantener legibilidad en proyección.
- Se normalizó la numeración de láminas a 26/26 y se agregó footer también a la slide de referencias, que en la vista previa original no mostraba numeración visible.
- Se ajustaron referencias internas a anexos cuando mencionaban números de lámina posteriores a la inserción.

## Revisión crítica de diseño/formato
- La presentación cumple estructura y contenido técnico, pero es visualmente monótona: la mayoría de las láminas repite fondo oscuro, dos paneles y bloques de texto largos.
- Hay alta densidad textual en slides 2, 6, 8, 9, 10, 11, 14 y 17; en defensa oral esto puede competir con el relato del expositor.
- El sistema cromático es consistente, aunque depende demasiado de amarillo/cian/naranja sobre fondo oscuro; conviene introducir ritmos visuales alternos sin abandonar la identidad.
- Algunas láminas de anexos son correctas como respaldo, pero no deberían presentarse linealmente dentro de los 20 minutos salvo que surjan preguntas.
- La nueva gráfica evita una leyenda extensa porque 11 curvas individuales harían ilegible la slide; los nombres quedan indicados en nota compacta y en este informe.

## Formas de hacer la presentación más dinámica
- Convertir 2-3 slides de procedimiento en una narrativa tipo “problema -> decisión -> evidencia”, usando una frase-tesis grande y un único objeto visual por lámina.
- Alternar layouts: una slide de mapa a pantalla completa, una comparación tipo scorecard m-Si vs HIT, y una slide de veredicto con número protagonista (+2.39% PR).
- Mover detalles matemáticos al anexo y dejar en cuerpo principal solo la interpretación física de cada ecuación.
- Añadir transiciones de capítulo muy simples antes de resultados y recomendación para separar metodología, evidencia y decisión.
- Ensayar con 17-19 slides principales y dejar anexos como backup; así se respeta mejor el límite de 20 minutos.

## Observaciones de cumplimiento
- No se detectan brechas mayores frente a la pauta: portada, estructura obligatoria, numeración, referencias, Cocoa/Atacama, De Soto, SAPM, PR y discusión técnica están presentes.
- Riesgo principal: duración. El deck revisado tiene 26 láminas totales; debe presentarse como 18-19 láminas principales más anexos de respaldo para no exceder 20 minutos.
