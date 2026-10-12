# Especificación de requisitos — PATITAS-PETS

**Proyecto:** PATITAS-PETS · Gestor de PQRS de MEPEGA
**Versión del documento:** 2.0 — Entrega 2 (actualizado con la versión 2.0.0 del software)

---

## 1. Convenciones

- **RF-xx:** requisito funcional. **RNF-xx:** requisito no funcional.
- **Prioridad (MoSCoW):** *Debe* (obligatorio), *Debería* (importante), *Podría* (deseable).
- **Versión:** 1.0 corresponde a la Entrega 1 y 2.0 a la Entrega 2.
- **Estado:** ✅ implementado · 🔜 planeado.

## 2. Actores

| Actor | Descripción |
|---|---|
| Operador | Registra y consulta PQRS. |
| Supervisor | Consulta PQRS y hace seguimiento a los estados. |
| Administrador | Mismas funciones que el supervisor; responsable de los datos del sistema. |
| Sistema | Calcula consecutivos, fechas y genera radicados. |

> En la versión 1.0 los tres roles tienen las mismas opciones de menú. La diferenciación de permisos por rol está pendiente de confirmar con el PO (ver sección 8).

## 3. Requisitos funcionales

### 3.1 Autenticación y sesión

| ID | Requisito | Prioridad | Versión | Estado |
|---|---|---|---|---|
| RF-01 | El sistema debe exigir el ingreso (login) antes de mostrar el menú principal. | Debe | 1.0 | ✅ |
| RF-02 | El usuario debe poder ingresar con su **nombre de usuario o su correo institucional** y su clave, validados contra `data/Usuarios.txt`. | Debe | 1.0 | ✅ |
| RF-03 | Solo pueden ingresar usuarios con estado **Activo**. | Debe | 1.0 | ✅ |
| RF-04 | Tras **3 intentos fallidos** el sistema debe bloquear la pantalla de ingreso durante **30 segundos**, mostrando en pantalla la cuenta regresiva. | Debe | 1.0 | ✅ |
| RF-05 | La clave no debe mostrarse al escribirla (asteriscos en Windows; oculta en otros sistemas). | Debería | 1.0 | ✅ |
| RF-06 | El usuario debe poder **cancelar** el ingreso y salir del programa. | Debe | 1.0 | ✅ |
| RF-07 | Al ingresar, el sistema debe guardar la sesión (usuario, nombre, correo, rol, hora de ingreso) y mostrarla en el encabezado de cada pantalla. | Debe | 1.0 | ✅ |

### 3.2 Menú principal

| ID | Requisito | Prioridad | Versión | Estado |
|---|---|---|---|---|
| RF-08 | El menú debe ofrecer: 1. Registrar PQRS, 2. Consultar PQRS, 3. Registrar cambio en PQRS, 4. Estadísticas, 5. Salir. | Debe | 1.0 | ✅ |
| RF-09 | El menú debe rechazar opciones no válidas y volver a pedirlas. | Debe | 1.0 | ✅ |

### 3.3 Registro de PQRS

| ID | Requisito | Prioridad | Versión | Estado |
|---|---|---|---|---|
| RF-10 | El sistema debe capturar los datos del solicitante, la información de la PQRS y la información relacionada, validando cada campo según la tabla de la sección 5. | Debe | 1.0 | ✅ |
| RF-11 | Si un dato es inválido, el sistema debe explicar el motivo y volver a pedirlo sin perder lo ya digitado. | Debe | 1.0 | ✅ |
| RF-12 | Los campos de lista cerrada (tipo de documento, tipo de teléfono, tipo de solicitud, canal, mascota y campus) deben elegirse de un menú numerado. | Debería | 1.0 | ✅ |
| RF-13 | El operador debe poder escribir `cancelar` en cualquier campo para salir sin guardar. | Debería | 1.0 | ✅ |
| RF-14 | Antes de guardar, el sistema debe mostrar un resumen y pedir confirmación (S/N). | Debería | 1.0 | ✅ |
| RF-15 | El **ID de registro** debe ser un entero autoincremental **propio de cada archivo**: mayor ID existente en ese archivo + 1. Con las bases entregadas, el primer registro nuevo de cada tipo será el **3001**. | Debe | 1.0 | ✅ |
| RF-16 | La **fecha máxima de respuesta** debe calcularse como fecha de radicación + **15 días calendario** (valor definido por el equipo en `config.PLAZO_RESPUESTA_DIAS`). | Debe | 1.0 | ✅ |
| RF-17 | Toda PQRS nueva debe quedar en estado **Registrada**. | Debe | 1.0 | ✅ |
| RF-18 | El **usuario registrador** debe asignarse automáticamente desde la sesión y verificarse como activo y autorizado antes de guardar. | Debe | 1.0 | ✅ |

### 3.4 Almacenamiento

| ID | Requisito | Prioridad | Versión | Estado |
|---|---|---|---|---|
| RF-19 | Cada tipo de PQRS debe guardarse **solo** en su archivo: `Peticion.txt`, `Queja.txt`, `Reclamo.txt` o `Sugerencia.txt`. | Debe | 1.0 | ✅ |
| RF-20 | Los cuatro archivos deben tener la misma estructura de 18 campos separados por `\|` (sección 6). | Debe | 1.0 | ✅ |
| RF-21 | Al iniciar, el sistema debe verificar la estructura: crear carpetas o archivos faltantes con su encabezado y avisar si un encabezado no coincide. | Debería | 1.0 | ✅ |
| RF-22 | Al leer, las líneas en blanco o con un número de campos incorrecto deben omitirse con un aviso, sin detener el programa. | Debería | 1.0 | ✅ |

### 3.5 Radicado

| ID | Requisito | Prioridad | Versión | Estado |
|---|---|---|---|---|
| RF-23 | Al guardar una PQRS, el sistema debe generar un radicado en texto plano, con marco ASCII (`+`, `-`, `\|`) y **exactamente 120 caracteres por línea**. | Debe | 1.0 | ✅ |
| RF-24 | El radicado debe mostrar: encabezado institucional; número de radicado (prefijo + ID, p. ej. `PET-003001`), fecha y hora de radicación, estado y fecha máxima de respuesta; datos del solicitante; clasificación (tipo, canal, mascota y campus); asunto; usuario registrador. | Debe | 1.0 | ✅ |
| RF-25 | El radicado **no** debe incluir la descripción detallada, y si la dirección está vacía debe mostrar `N/A`. | Debe | 1.0 | ✅ |
| RF-26 | El radicado debe mostrarse en pantalla y guardarse en `data/radicados/<número de radicado>.txt`. | Debe | 1.0 | ✅ |

### 3.6 Consulta, cambios y estadísticas

| ID | Requisito | Prioridad | Versión | Estado |
|---|---|---|---|---|
| RF-27 | El sistema debe permitir consultar una PQRS y mostrarla con el formato del radicado. En la versión 2.0 la búsqueda se hace por número de radicado (p. ej. `PET-003001`) e incluye el historial de estados. | Debe | 1.0 / 2.0 | ✅ |
| RF-28 | El sistema debe permitir registrar cambios de estado respetando el flujo Registrada → En proceso → Solucionada, sin saltos ni retrocesos. | Debe | 2.0 | ✅ |
| RF-29 | El sistema debe listar los registros activos, las PQRS más antiguas y las que están próximas a vencer o vencidas, en tablas paginadas. | Debe | 2.0 | ✅ |
| RF-30 | `reportes.py` debe calcular el promedio de días de respuesta (en enteros) y las estadísticas por tipo de mascota, canal, campus, estado y vencimiento, más las complementarias por tipo de PQRS y por usuario registrador. | Debe | 2.0 | ✅ |
| RF-31 | El sistema debe exportar los resultados a un archivo plano: reporte de estadísticas (TXT) y base consolidada (CSV). | Debe | 2.0 | ✅ |
| RF-32 | El equipo debe construir un tablero en Power BI de mínimo 3 páginas con las estadísticas exigidas ([guía](08_guia_power_bi.md)). | Debe | 2.0 | 🔜 |
| RF-33 | Cada cambio de estado debe quedar en `data/Historial.txt` con fecha, usuario, estado anterior, estado nuevo y observación opcional. | Debe | 2.0 | ✅ |
| RF-34 | Cada cambio de estado debe generar un comprobante en `data/radicados/`. | Debería | 2.0 | ✅ |
| RF-35 | El sistema debe permitir buscar todas las PQRS de un solicitante por su número de documento. | Debería | 2.0 | ✅ |
| RF-36 | La base exportada para Power BI debe incluir columnas calculadas (días de respuesta, antigüedad, días para vencer, estado del plazo) y excluir los datos personales del solicitante. | Debe | 2.0 | ✅ |

## 4. Requisitos no funcionales

| ID | Categoría | Requisito |
|---|---|---|
| RNF-01 | Usabilidad | Interfaz de consola con banner, encabezado de sesión, menús numerados y mensajes de error que explican cómo corregir el dato. |
| RNF-02 | Usabilidad | Un operador debe poder registrar una PQRS completa en menos de 3 minutos. |
| RNF-03 | Seguridad | Acceso solo para usuarios activos de `Usuarios.txt`; máximo 3 intentos; el mensaje de error no revela si falló el usuario o la clave. |
| RNF-04 | Seguridad | La sesión no guarda la clave del usuario. *Limitación conocida:* `Usuarios.txt` almacena claves en texto plano; se propone cifrarlas con `hashlib` en una versión futura, previa aprobación del PO. |
| RNF-05 | Integridad | Nunca se sobrescriben registros existentes: los nuevos se agregan al final del archivo. El ID se recalcula justo antes de escribir. |
| RNF-06 | Integridad | Los textos no pueden contener el carácter `\|`, reservado como separador de columnas. |
| RNF-07 | Fiabilidad | Un archivo de datos con líneas dañadas no detiene el programa; `Ctrl + C` cierra el programa de forma ordenada. |
| RNF-08 | Rendimiento | Registrar o consultar una PQRS debe tardar menos de 2 segundos con los 12.000 registros actuales. |
| RNF-09 | Compatibilidad | Python 3.10 o superior, sin librerías externas; Windows, Linux y macOS. Archivos en UTF-8 con saltos de línea LF. |
| RNF-10 | Portabilidad | Las rutas se calculan a partir de la ubicación del código, por lo que el programa funciona desde cualquier carpeta. |
| RNF-11 | Mantenibilidad | Código modular (sección 7) y reglas de negocio centralizadas en `config.py`; comentarios y nombres en español. |
| RNF-12 | Legal | Los datos personales de los solicitantes se tratan conforme a la Ley 1581 de 2012 (protección de datos personales): uso exclusivo para gestionar la PQRS. |

## 5. Reglas de validación por campo

| Campo | Obligatorio | Regla | Válido | Inválido |
|---|---|---|---|---|
| Nombre completo | Sí | 3 a 100 caracteres; letras con tildes y ñ, espacios, `'` y `-`; sin números | Juan David Pérez Gómez | Juan123 |
| Tipo de documento | Sí | CC, TI, CE, PP o NIT | CC | — |
| Número de documento | Sí | Solo dígitos, entre 3 y 15 | 1037654321 | 10376A321 |
| Tipo de teléfono | Sí | Celular, Fijo, Corporativo u Otro | Celular | — |
| Teléfono de contacto | Sí | Exactamente 10 dígitos | 3001234567 | 300123ABCD |
| Correo electrónico | Sí | Máximo 254 caracteres; un único `@`; dominio válido (`usuario@dominio.com`) | usuario@correo.com | usuariocorreo.com |
| Dirección | No | Si se digita: 5 a 200 caracteres; letras, números y `# - . , /` | Avenida Siempreviva 742 | Cra |
| Tipo de solicitud | Sí | Petición, Queja, Reclamo o Sugerencia | Queja | — |
| Fecha de radicación | Sí | `AAAA-MM-DD HH:MM` (Enter = fecha y hora actual); no puede ser futura | 2026-09-27 10:15 | 2999-01-01 |
| Canal de recepción | Sí | Presencial, Correo electrónico, Página web, Teléfono, Redes sociales u Otro | Página web | — |
| Asunto o título | Sí | 5 a 150 caracteres; letras, números y puntuación básica | Solicitud de información sobre servicio veterinario. | Hola |
| Descripción detallada | Sí | 20 a 2.000 caracteres; no solo espacios; sin `\|` | Solicito información sobre los servicios de consulta para caninos… | (solo espacios) |
| Tipo de mascota | Sí | Perro, Gato u Otro | Perro | — |
| Campus relacionado | Sí | Uno de los 9 campus del catálogo | Campus Medellín - Ciudadela Robledo | — |
| Fecha máxima de respuesta | Automático | Fecha de radicación + 15 días | 2026-10-12 10:15:00 | — |
| Estado | Automático | Inicia en Registrada | Registrada | — |
| Usuario registrador | Automático | Usuario de la sesión, activo en `Usuarios.txt` | admin_udea | (vacío) |

Las pruebas de estos ejemplos se ejecutan con `python src/validaciones.py`.

## 6. Modelo de datos

Cada línea de los archivos `Peticion.txt`, `Queja.txt`, `Reclamo.txt` y `Sugerencia.txt` es un registro con 18 campos separados por `|`. La primera línea es el encabezado.

| # | Campo | Tipo | Ejemplo |
|---|---|---|---|
| 1 | id | Entero consecutivo por archivo | 3001 |
| 2 | nombre_completo | Texto | Juan David Pérez Gómez |
| 3 | tipo_documento | Código | CC |
| 4 | numero_documento | Texto numérico | 1037654321 |
| 5 | tipo_telefono | Catálogo | Celular |
| 6 | telefono_contacto | Texto numérico | 3001234567 |
| 7 | correo_electronico | Texto | usuario@correo.com |
| 8 | direccion | Texto (puede estar vacío) | Carrera 55 #8-73 |
| 9 | tipo_solicitud | Peticion · Queja · Reclamo · Sugerencia (sin tilde, como en la base origen) | Peticion |
| 10 | fecha_radicacion | Fecha `AAAA-MM-DD HH:MM:SS` | 2026-09-27 10:15:00 |
| 11 | canal_recepcion | Catálogo | Correo electrónico |
| 12 | asunto_titulo | Texto | Solicitud de cita para esterilización |
| 13 | descripcion_detallada | Texto libre | Quisiera solicitar una cita… |
| 14 | tipo_mascota | Catálogo | Perro |
| 15 | campus_relacionado | Catálogo | Campus Medellín - Sede de Posgrado |
| 16 | fecha_maxima_respuesta | Fecha `AAAA-MM-DD HH:MM:SS` | 2026-10-12 10:15:00 |
| 17 | estado_peticion | Registrada · En proceso · Solucionada | Registrada |
| 18 | usuario_registro | Usuario de `Usuarios.txt` | admin_udea |

**Diagnóstico de las bases de datos origen (28-sep-2026):** cada archivo tiene 3.000 registros con IDs del 1 al 3.000, sin duplicados ni saltos; todas las líneas tienen 18 campos; las fechas van del 1 de enero al 28 de septiembre de 2026; la fecha máxima de los registros existentes es radicación + 30 días; entre 138 y 156 registros por archivo no tienen dirección; y los 12 usuarios de `Usuarios.txt` están activos.

## 7. Arquitectura y trazabilidad

| Módulo (`src/`) | Responsabilidad | Requisitos |
|---|---|---|
| `main.py` | Punto de entrada, menú principal y menú de estadísticas | RF-01, RF-08, RF-09, RF-31 |
| `config.py` | Rutas, catálogos y reglas de negocio | RF-16, RF-20, RNF-10, RNF-11 |
| `interfaz.py` | Banner, encabezados, lectura de opciones y de la clave | RF-05, RNF-01 |
| `autenticacion.py` | Usuarios, credenciales, intentos, bloqueo y sesión | RF-02 a RF-07, RNF-03, RNF-04 |
| `validaciones.py` | Reglas de cada campo (correo, teléfono, fechas, nombres…) | RF-10, RF-11, RF-18, RNF-06 |
| `registro.py` | Captura guiada, confirmación y guardado de la PQRS | RF-10 a RF-18 |
| `archivos.py` | Lectura/escritura de los 4 archivos y consecutivos | RF-15, RF-19 a RF-22, RNF-05 |
| `radicado.py` | Comprobante de 120 columnas | RF-23 a RF-26 |
| `consultas.py` | Consultas y listados | RF-27, RF-29, RF-35 |
| `cambios.py` | Cambio de estado, historial y comprobante | RF-28, RF-33, RF-34 |
| `reportes.py` | Estadísticas, reporte y base para Power BI | RF-30, RF-31, RF-36 |

## 8. Supuestos y preguntas para el Product Owner

Decisiones tomadas por el equipo que conviene validar en la entrevista con el PO:

1. **Base de cálculo de la fecha máxima.** El enunciado dice "fecha de registro + N días", pero la estructura de datos no tiene un campo `fecha_registro` y las bases entregadas calculan la fecha máxima desde `fecha_radicacion`. Mantuvimos esa base de cálculo para no alterar la estructura. ¿Es correcto?
2. **Plazo.** Elegimos 15 días calendario. ¿El PO prefiere días hábiles?
3. **Perfil del solicitante.** La estadística 6 pide clasificar por perfil (Estudiante, Docente, Administrativo, Ciudadano), pero ese campo no existe en la estructura ni en las bases. ¿Se agrega como campo 19 o se deriva de otro dato?
4. **Mascota "Otro".** El radicado del enunciado menciona "Perro o Gato", pero el catálogo y las bases incluyen "Otro". Lo conservamos.
5. **Texto ASCII del radicado.** El marco usa solo caracteres ASCII y el contenido conserva tildes y ñ (UTF-8). Si se exige ASCII puro, basta con activar `RADICADO_SOLO_ASCII = True` en `config.py`.
6. **Permisos por rol.** ¿Deben Operador, Supervisor y Administrador tener opciones distintas en el menú?
7. **Tiempo de bloqueo.** Definimos 30 segundos. ¿Debe aumentar si se repiten los bloqueos?
8. **Promedio de días de respuesta.** Las bases no tienen fecha de solución. PATITAS-PETS la registra en `Historial.txt` desde la versión 2.0, por lo que el promedio solo incluye las PQRS solucionadas en el sistema. ¿El PO puede entregar las fechas de solución de las PQRS históricas o acepta esta definición?
