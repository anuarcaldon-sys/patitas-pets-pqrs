# Reporte de visión — PATITAS-PETS

**Proyecto:** PATITAS-PETS · Gestor de PQRS de MEPEGA
**Curso:** Algoritmia y Programación 2026-2 — Facultad de Ingeniería, Universidad de Antioquia
**Docente / Product Owner:** Victor Hugo Mercado Ramos
**Versión del documento:** 1.0 — Entrega 1 (30 de septiembre de 2026)

---

## 1. Propósito

Este documento describe qué es PATITAS-PETS, por qué se construye, a quién sirve y qué beneficios entrega. Es el punto de referencia común para el equipo y para el Product Owner (PO): cualquier requisito o decisión de diseño posterior debe poder justificarse a partir de esta visión.

## 2. Contexto

El Movimiento Estudiantil de Perritos y Gaticos (MEPEGA) apoya la atención veterinaria de perros y gatos en los campus de la Universidad de Antioquia. Recibe peticiones, quejas, reclamos y sugerencias (PQRS) por redes sociales, correo electrónico, papel, voz a voz y otros medios, y hoy las procesa **a papel y lápiz**, asignando a mano un número consecutivo a cada solicitud.

MEPEGA ya cuenta con cuatro bases de datos en archivos planos (3.000 registros por cada tipo de PQRS) y con un archivo de usuarios autorizados. El nuevo sistema debe leer esas bases y **continuar su numeración** sin repetir consecutivos.

## 3. Enunciado del problema

| Elemento | Descripción |
|---|---|
| **El problema de** | registrar y numerar manualmente las PQRS que llegan por múltiples canales |
| **afecta a** | los operadores de MEPEGA, a sus supervisores y a los ciudadanos, estudiantes y funcionarios que presentan solicitudes |
| **cuyo impacto es** | consecutivos repetidos o saltados, datos incompletos o mal escritos, pérdida de trazabilidad sobre quién registró cada caso y dificultad para saber qué solicitudes están por vencer |
| **una solución exitosa sería** | un programa de consola que exija autenticación, valide cada dato al momento de capturarlo, asigne automáticamente un consecutivo independiente por tipo de PQRS, guarde cada tipo en su propio archivo y entregue un radicado estandarizado al solicitante |

## 4. Posicionamiento del producto

| | |
|---|---|
| **Para** | MEPEGA y su equipo de operadores, supervisores y administradores |
| **quienes** | necesitan registrar, numerar y hacer seguimiento a las PQRS de atención veterinaria |
| **PATITAS-PETS** | es un gestor de PQRS de consola desarrollado en Python |
| **que** | controla el acceso, valida los datos, numera automáticamente, almacena en archivos planos independientes y emite radicados de 120 columnas |
| **a diferencia de** | el registro manual en papel |
| **nuestro producto** | garantiza consecutivos únicos, datos consistentes y trazabilidad del usuario que registra cada solicitud, sin requerir bases de datos ni software adicional |

## 5. Interesados y usuarios

| Interesado | Rol frente al sistema | Interés principal |
|---|---|---|
| Dirección de MEPEGA | Patrocinador | Mejor atención a las mascotas y control de los plazos de respuesta |
| Operador | Usuario directo | Registrar PQRS de forma rápida y sin errores |
| Supervisor | Usuario directo | Consultar el estado de las PQRS y hacer seguimiento a su equipo |
| Administrador | Usuario directo | Gestionar la información y los usuarios autorizados |
| Solicitante (estudiante, docente, administrativo o ciudadano) | Beneficiario indirecto | Recibir un número de radicado y una respuesta oportuna |
| Docente del curso | Product Owner | Validar que el producto cumpla los requisitos del proyecto |

## 6. Objetivos

**Objetivo general.** Desarrollar un programa de consola en Python, visualmente amigable, que permita a MEPEGA gestionar sus PQRS mediante archivos planos y exportar los resultados.

**Objetivos específicos.**

1. Restringir el acceso al sistema a usuarios activos y autorizados, con control de intentos fallidos y bloqueo temporal.
2. Registrar PQRS validando cada campo según las reglas definidas por MEPEGA.
3. Asignar un consecutivo único e independiente por tipo de PQRS que continúe la numeración de las bases de datos existentes.
4. Almacenar cada tipo de PQRS en su propio archivo plano con una estructura común.
5. Emitir un radicado en texto plano de 120 caracteres de ancho que certifique la información registrada.
6. Consultar el estado de las PQRS y generar estadísticas sobre la atención (versión 2.0).
7. Construir un tablero en Power BI que apoye la toma de decisiones (versión 2.0).

## 7. Beneficios esperados

| Beneficio | Cómo lo logra PATITAS-PETS |
|---|---|
| **Cero consecutivos repetidos** | El número se calcula desde el propio archivo justo antes de guardar (mayor ID existente + 1) |
| **Datos confiables** | Cada campo se valida al digitarlo; el sistema no avanza hasta que el dato es correcto |
| **Trazabilidad** | Cada PQRS queda vinculada automáticamente al usuario que inició sesión |
| **Control de plazos** | La fecha máxima de respuesta se calcula y se imprime en el radicado |
| **Comprobante estandarizado** | Radicado con formato fijo de 120 columnas, listo para imprimir o enviar |
| **Seguridad básica** | Ingreso obligatorio, máximo 3 intentos y bloqueo temporal visible en pantalla |
| **Bajo costo** | Funciona solo con Python y archivos de texto; no requiere licencias ni servidores |
| **Base para analítica** | Los archivos planos alimentan los reportes y el tablero de Power BI |

## 8. Alcance por versiones

| Versión | Entrega | Funcionalidades |
|---|---|---|
| **1.0** | Entrega 1 (30-sep-2026) | Login con usuario o correo, 3 intentos y bloqueo de 30 s; sesión activa; registro de PQRS con todas las validaciones; consecutivo por archivo que continúa desde 3001; almacenamiento en los 4 archivos planos; radicado de 120 columnas guardado en `data/radicados/`; consulta de una PQRS por tipo e ID |
| **2.0** | Entrega 2 (18-nov-2026) | Registro de cambios de estado (Registrada → En proceso → Solucionada); consultas de registros activos, más antiguos y próximos a vencer; `reportes.py` con el promedio de días de respuesta y cinco estadísticas adicionales; exportación de resultados a archivo plano; tablero en Power BI; manual de usuario y plan de versionado |

**Fuera del alcance:** interfaz web o gráfica, base de datos relacional, envío de notificaciones por correo, atención de la solicitud veterinaria en sí misma y administración de usuarios desde el programa.

## 9. Restricciones

- Lenguaje Python y ejecución en consola.
- Almacenamiento en archivos planos: `Peticion.txt`, `Queja.txt`, `Reclamo.txt` y `Sugerencia.txt`, independientes entre sí y con la misma estructura.
- Radicado en texto plano de exactamente 120 caracteres por línea, sin la descripción detallada.
- Código organizado en los módulos `validaciones.py`, `archivos.py` y `reportes.py`, entre otros.
- Repositorio en GitHub con las carpetas `src/`, `docs/`, `images/` y `data/`.

## 10. Supuestos y dependencias

- Los archivos entregados por MEPEGA usan UTF-8, el separador `|` y el formato de fecha `AAAA-MM-DD HH:MM:SS`.
- El archivo `Usuarios.txt` es la única fuente de usuarios autorizados.
- El equipo cuenta con computadores propios con Python 3.10 o superior.
- El PO está disponible para resolver dudas de requisitos durante el semestre.

## 11. Indicadores de éxito

- 100 % de los registros nuevos con consecutivo único dentro de su archivo.
- 0 registros guardados con campos obligatorios vacíos o inválidos.
- 100 % de los radicados con líneas de exactamente 120 caracteres.
- 100 % de las PQRS nuevas con usuario registrador asignado.
- Todos los integrantes pueden explicar cualquier parte del código en la sustentación.
