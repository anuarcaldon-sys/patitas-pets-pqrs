"""
config.py
---------
Parámetros generales de PATITAS-PETS (Gestor de PQRS de MEPEGA).

Aquí se concentran las rutas de los archivos, los catálogos de valores
permitidos y las reglas de negocio que el equipo definió. Si una regla
cambia (por ejemplo, el plazo de respuesta), se modifica solo en este
archivo y el resto del programa la toma automáticamente.
"""

from pathlib import Path

VERSION = "2.0.0"   # esquema MAYOR.MENOR.PARCHE (ver docs/04_plan_versionado.md)

# ---------------------------------------------------------------------------
# Rutas
# Se calculan a partir de la ubicación de este archivo (carpeta src/), así el
# programa funciona sin importar desde qué carpeta se ejecute.
# ---------------------------------------------------------------------------
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "data"
CARPETA_RADICADOS = CARPETA_DATOS / "radicados"
CARPETA_EXPORTACIONES = CARPETA_DATOS / "exportaciones"
ARCHIVO_USUARIOS = CARPETA_DATOS / "Usuarios.txt"

# Bitácora de cambios de estado: guarda cuándo y quién cambió cada PQRS.
# Es la fuente de la fecha de solución para el promedio de días de respuesta.
ARCHIVO_HISTORIAL = CARPETA_DATOS / "Historial.txt"
CAMPOS_HISTORIAL = [
    "tipo_solicitud",
    "id",
    "estado_anterior",
    "estado_nuevo",
    "fecha_cambio",
    "usuario",
    "observacion",
]

# ---------------------------------------------------------------------------
# Estructura de los archivos planos
# ---------------------------------------------------------------------------
SEPARADOR = "|"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"   # formato datetime usado en las bases de datos

# Columnas de cada registro, en el mismo orden de las bases de datos origen.
CAMPOS = [
    "id",
    "nombre_completo",
    "tipo_documento",
    "numero_documento",
    "tipo_telefono",
    "telefono_contacto",
    "correo_electronico",
    "direccion",
    "tipo_solicitud",
    "fecha_radicacion",
    "canal_recepcion",
    "asunto_titulo",
    "descripcion_detallada",
    "tipo_mascota",
    "campus_relacionado",
    "fecha_maxima_respuesta",
    "estado_peticion",
    "usuario_registro",
]

# Un archivo independiente por cada tipo de PQRS.
# La clave del diccionario es el valor que se guarda en la columna
# tipo_solicitud (sin tilde, igual que en las bases de datos entregadas).
TIPOS_SOLICITUD = {
    "Peticion": {
        "nombre": "Petición",
        "archivo": CARPETA_DATOS / "Peticion.txt",
        "prefijo": "PET",
    },
    "Queja": {
        "nombre": "Queja",
        "archivo": CARPETA_DATOS / "Queja.txt",
        "prefijo": "QUE",
    },
    "Reclamo": {
        "nombre": "Reclamo",
        "archivo": CARPETA_DATOS / "Reclamo.txt",
        "prefijo": "REC",
    },
    "Sugerencia": {
        "nombre": "Sugerencia",
        "archivo": CARPETA_DATOS / "Sugerencia.txt",
        "prefijo": "SUG",
    },
}

# ---------------------------------------------------------------------------
# Catálogos de valores permitidos (tomados del enunciado del proyecto)
# ---------------------------------------------------------------------------
TIPOS_DOCUMENTO = {
    "CC": "Cédula de ciudadanía",
    "TI": "Tarjeta de identidad",
    "CE": "Cédula de extranjería",
    "PP": "Pasaporte",
    "NIT": "NIT",
}

TIPOS_TELEFONO = ["Celular", "Fijo", "Corporativo", "Otro"]

CANALES_RECEPCION = [
    "Presencial",
    "Correo electrónico",
    "Página web",
    "Teléfono",
    "Redes sociales",
    "Otro",
]

TIPOS_MASCOTA = ["Perro", "Gato", "Otro"]

CAMPUS = [
    "Campus Medellín - Ciudad Universitaria",
    "Campus Medellín - Ciudadela Robledo",
    "Campus en el Área de la salud",
    "Campus Medellín - Sede de Posgrado",
    "Campus Medellín - Edificio San Ignacio",
    "Campus Medellín - Antigua Escuela de Derecho",
    "Campus Medellín - Edificio Antioquia",
    "Campus Medellín - Casas Patrimoniales",
    "Campus Medellín - Edificio de Extensión",
]

# Flujo obligatorio de estados: Registrada -> En proceso -> Solucionada
ESTADOS = ["Registrada", "En proceso", "Solucionada"]
ESTADO_INICIAL = "Registrada"
ESTADOS_ACTIVOS = ["Registrada", "En proceso"]      # PQRS aún sin solucionar

# Único cambio permitido desde cada estado (sin saltos ni retrocesos)
SIGUIENTE_ESTADO = {
    "Registrada": "En proceso",
    "En proceso": "Solucionada",
}

# ---------------------------------------------------------------------------
# Reglas de negocio definidas por el equipo
# ---------------------------------------------------------------------------
# El enunciado pide que cada equipo cambie el valor de 30 días.
# Elegimos 15 días calendario, en línea con el término general de 15 días
# que la Ley 1755 de 2015 fija para responder peticiones.
PLAZO_RESPUESTA_DIAS = 15

# Una PQRS activa está "próxima a vencer" si le quedan menos de estos días
DIAS_ALERTA_VENCIMIENTO = 5

FILAS_POR_PAGINA = 15       # filas por página en los listados de consola
MAX_OBSERVACION = 300       # longitud máxima de la observación de un cambio

MAX_INTENTOS_LOGIN = 3      # intentos fallidos permitidos antes de bloquear
SEGUNDOS_BLOQUEO = 30       # tiempo de bloqueo de la pantalla de ingreso

ANCHO_RADICADO = 120        # ancho fijo (en caracteres) del comprobante

# Si el PO exige texto ASCII puro en el radicado, cambiar a True:
# las tildes y la ñ se reemplazan (á -> a, ñ -> n).
RADICADO_SOLO_ASCII = False

# Muestra * al escribir la clave (solo en Windows). Si la consola del IDE
# no lo soporta, cambiar a False y la clave se leerá sin mostrar nada.
MOSTRAR_ASTERISCOS = True
