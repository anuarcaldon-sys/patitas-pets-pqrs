# Guía de Power BI — Tablero de PATITAS-PETS

**Responsable:** Sandra Yulieth Salcedo Salazar (gestión de datos y Power BI) · **Herramienta:** Power BI Desktop (gratuito)

El tablero se construye con la base que exporta PATITAS-PETS, de modo que las cifras de Power BI coinciden con las del reporte de la opción 4 del programa.

---

## 1. Obtener la base consolidada

1. Ejecute `python src/main.py`, ingrese y elija **4. Estadísticas → 3. Exportar base consolidada para Power BI (CSV)**.
2. El archivo queda en `data/exportaciones/base_consolidada_pqrs.csv`: una fila por PQRS de los cuatro archivos y 19 columnas.

| Columna | Descripción |
|---|---|
| `radicado`, `tipo_solicitud`, `id` | Identificación de la PQRS (por ejemplo, `PET-003001`, Petición, 3001) |
| `tipo_documento`, `canal_recepcion`, `asunto_titulo`, `tipo_mascota`, `campus_relacionado` | Clasificación de la solicitud |
| `fecha_radicacion`, `fecha_maxima_respuesta` | Fechas de la PQRS |
| `estado_peticion` | Registrada, En proceso o Solucionada |
| `usuario_registro`, `nombre_registrador`, `rol_registrador` | Quién registró la PQRS |
| `fecha_solucion`, `dias_respuesta` | Fecha en que pasó a Solucionada (según `Historial.txt`) y días que tomó; vacías si no se conoce |
| `antiguedad_dias` | Días transcurridos desde la radicación hasta la exportación |
| `dias_para_vencer` | Días que faltan para la fecha máxima (solo PQRS activas; negativo = vencida) |
| `estado_plazo` | Solucionada, Vencida, Próxima a vencer o Al día |

Por protección de datos personales (Ley 1581 de 2012) la base no incluye nombres, documentos, teléfonos, correos, direcciones ni descripciones.

## 2. Cargar y preparar los datos

1. En Power BI Desktop: **Inicio → Obtener datos → Texto/CSV** y elija el archivo. Verifique que el origen sea **65001: Unicode (UTF-8)** y el delimitador **Coma**. Clic en **Transformar datos**.
2. En Power Query, cambie el nombre de la consulta a `PQRS` y asigne los tipos de columna:
   - `fecha_radicacion`, `fecha_maxima_respuesta`, `fecha_solucion` → **Fecha y hora**.
   - `id`, `dias_respuesta`, `antiguedad_dias`, `dias_para_vencer` → **Número entero**.
   - Si las fechas quedan con error por la configuración regional, use **Cambiar tipo → Usar configuración regional → Inglés (Estados Unidos)**.
3. Clic en **Cerrar y aplicar**.
4. *(Opcional)* Cargue también `data/Historial.txt` (delimitador `|`) para analizar los cambios de estado.

## 3. Medidas DAX

Cree cada medida con **Modelado → Nueva medida**:

```DAX
Total PQRS = COUNTROWS ( PQRS )

Promedio días de respuesta = ROUND ( AVERAGE ( PQRS[dias_respuesta] ), 0 )

PQRS con fecha de solución = COUNT ( PQRS[dias_respuesta] )

% del total = DIVIDE ( [Total PQRS], CALCULATE ( [Total PQRS], ALLSELECTED ( PQRS ) ) )

Solucionadas = CALCULATE ( [Total PQRS], PQRS[estado_peticion] = "Solucionada" )

Tasa de resolución = DIVIDE ( [Solucionadas], [Total PQRS] )

PQRS activas = CALCULATE ( [Total PQRS], PQRS[estado_peticion] IN { "Registrada", "En proceso" } )

Vencidas = CALCULATE ( [Total PQRS], PQRS[estado_plazo] = "Vencida" )

Próximas a vencer = CALCULATE ( [Total PQRS], PQRS[estado_plazo] = "Próxima a vencer" )

% vencidas sobre activas = DIVIDE ( [Vencidas], [PQRS activas] )

Antigüedad promedio activas =
    CALCULATE ( AVERAGE ( PQRS[antiguedad_dias] ), PQRS[estado_peticion] IN { "Registrada", "En proceso" } )
```

Dé formato de porcentaje a `% del total`, `Tasa de resolución` y `% vencidas sobre activas`.

> `Promedio días de respuesta` usa la misma definición que `reportes.py`: días entre la radicación y la solución registrada en PATITAS-PETS, redondeados al entero. Las PQRS históricas solucionadas no tienen fecha de solución y quedan por fuera; muéstrelo en el tablero junto a la medida `PQRS con fecha de solución`.

## 4. Diseño del tablero (3 páginas)

| Página | Visualizaciones | Estadística del enunciado |
|---|---|---|
| **1. Resumen y tiempos** | Tarjetas: *Promedio días de respuesta* (primera visualización), *PQRS con fecha de solución*, *Total PQRS*, *Tasa de resolución*, *PQRS activas*. Gráfico de columnas por `tipo_solicitud`. Gráfico de líneas de *Total PQRS* por mes de `fecha_radicacion`. | Obligatoria: promedio de días de respuesta |
| **2. Demanda del servicio** | Gráfico de anillo por `tipo_mascota`. Barras de *% del total* por `canal_recepcion`. Barras horizontales por `campus_relacionado`. | 1. Mascota · 2. Canal · 3. Campus |
| **3. Gestión y plazos** | Columnas apiladas de `estado_peticion` por `tipo_solicitud`. Anillo de `estado_plazo` filtrado a PQRS activas. Tarjetas de *Vencidas*, *Próximas a vencer* y *% vencidas sobre activas*. Tabla de las próximas a vencer (`radicado`, `fecha_maxima_respuesta`, `dias_para_vencer`). Barras de *Total PQRS* por `nombre_registrador`. | 4. Estado · 5. Vencimiento · 6. Carga operativa |

Agregue en todas las páginas segmentadores por `tipo_solicitud`, `campus_relacionado` y fecha de radicación, y use los colores del logo (verde `#1B7F3B` y naranja `#F59E0B`).

> **Perfil del solicitante.** La estadística 6 del enunciado pide clasificar por Estudiante, Docente, Administrativo o Ciudadano, pero ese dato no existe en las bases de MEPEGA. El tablero muestra la parte operativa (carga por registrador) y el perfil queda como pregunta abierta para el Product Owner.

## 5. Guardar y actualizar

- Guarde el archivo como `docs/powerbi/PATITAS-PETS_dashboard.pbix` y exporte una copia en PDF (**Archivo → Exportar → Exportar a PDF**) en la misma carpeta, para que el docente pueda verlo sin Power BI.
- Cada vez que exporte una base nueva desde PATITAS-PETS, use **Inicio → Actualizar** en Power BI.
