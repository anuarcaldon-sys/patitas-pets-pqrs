"""
radicado.py
-----------
Construye el comprobante (radicado) de una PQRS en texto plano con un
ancho fijo de 120 caracteres y marco ASCII (+, -, |).

Estructura de cada línea de contenido:
    "| " + texto (116 caracteres, relleno con espacios) + " |"  = 120

Por optimización de espacio NO se incluye la descripción detallada, y si
la dirección está vacía se muestra "N/A" (restricciones del enunciado).
La misma función sirve para imprimir el radicado al registrar, para
mostrar el estado de una PQRS al consultarla y para certificar un cambio
de estado (en esos dos casos se agrega la sección HISTORIAL DE ESTADOS).
"""

import textwrap
import unicodedata
from datetime import datetime

import config

ANCHO = config.ANCHO_RADICADO
INTERIOR = ANCHO - 4          # espacio útil entre "| " y " |"
ANCHO_ETIQUETA = 30           # columna de las etiquetas (con puntos guía)


def a_ascii(texto):
    """Quita tildes y ñ (á -> a, ñ -> n) cuando se exige ASCII puro."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def preparar(texto):
    """Aplica la conversión a ASCII solo si está activada en config."""
    return a_ascii(texto) if config.RADICADO_SOLO_ASCII else texto


def borde():
    return "+" + "-" * (ANCHO - 2) + "+"


def linea_texto(texto=""):
    return "| " + preparar(texto).ljust(INTERIOR) + " |"


def linea_centrada(texto):
    return "| " + preparar(texto).center(INTERIOR) + " |"


def titulo_seccion(texto):
    """Ejemplo: |----------------- DATOS DEL SOLICITANTE -----------------|"""
    return "|" + f" {preparar(texto)} ".center(ANCHO - 2, "-") + "|"


def lineas_campo(etiqueta, valor):
    """
    Escribe 'Etiqueta ......: valor'. Si el valor no cabe en una línea,
    lo parte en varias alineadas debajo del primer renglón.
    """
    prefijo = f"{etiqueta} ".ljust(ANCHO_ETIQUETA, ".") + ": "
    sangria = " " * len(prefijo)
    partes = textwrap.wrap(valor, width=INTERIOR - len(prefijo)) or [""]
    lineas = [linea_texto(prefijo + partes[0])]
    lineas += [linea_texto(sangria + parte) for parte in partes[1:]]
    return lineas


def numero_radicado(registro):
    """Formatea el id con el prefijo del tipo. Ejemplo: PET-003001."""
    prefijo = config.TIPOS_SOLICITUD[registro["tipo_solicitud"]]["prefijo"]
    return f"{prefijo}-{int(registro['id']):06d}"


def construir_radicado(registro, titulo="COMPROBANTE DE RADICACIÓN DE PQRS",
                       nombre_registrador="", historial=None):
    """
    Devuelve el texto completo del radicado (líneas de exactamente 120 caracteres).
    historial: lista opcional de cambios de estado de la PQRS (de Historial.txt).
    """
    tipo = config.TIPOS_SOLICITUD[registro["tipo_solicitud"]]["nombre"]
    direccion = registro["direccion"] if registro["direccion"].strip() else "N/A"
    registrador = registro["usuario_registro"]
    if nombre_registrador:
        registrador = f"{nombre_registrador} ({registro['usuario_registro']})"

    lineas = [
        borde(),
        linea_centrada("UNIVERSIDAD DE ANTIOQUIA - MEPEGA"),
        linea_centrada("Movimiento Estudiantil de Perritos y Gaticos"),
        linea_centrada("PATITAS-PETS - Sistema de Gestión de PQRS"),
        linea_texto(),
        linea_centrada(titulo),
        borde(),
        titulo_seccion("DATOS DEL RADICADO"),
    ]
    lineas += lineas_campo("Número de radicado", numero_radicado(registro))
    lineas += lineas_campo("ID de registro", registro["id"])
    lineas += lineas_campo("Fecha y hora de radicación", registro["fecha_radicacion"])
    lineas += lineas_campo("Estado", registro["estado_peticion"])
    lineas += lineas_campo("Fecha máxima de respuesta", registro["fecha_maxima_respuesta"])

    lineas.append(titulo_seccion("DATOS DEL SOLICITANTE"))
    lineas += lineas_campo("Nombre completo", registro["nombre_completo"])
    lineas += lineas_campo("Documento", f"{registro['tipo_documento']} {registro['numero_documento']}")
    lineas += lineas_campo("Teléfono de contacto",
                           f"{registro['telefono_contacto']} ({registro['tipo_telefono']})")
    lineas += lineas_campo("Correo electrónico", registro["correo_electronico"])
    lineas += lineas_campo("Dirección", direccion)

    lineas.append(titulo_seccion("CLASIFICACIÓN"))
    lineas += lineas_campo("Tipo de solicitud", tipo)
    lineas += lineas_campo("Canal de recepción", registro["canal_recepcion"])
    lineas += lineas_campo("Tipo de mascota", registro["tipo_mascota"])
    lineas += lineas_campo("Campus", registro["campus_relacionado"])

    lineas.append(titulo_seccion("RESUMEN"))
    lineas += lineas_campo("Asunto", registro["asunto_titulo"])

    if historial is not None:
        lineas.append(titulo_seccion("HISTORIAL DE ESTADOS"))
        if not historial:
            lineas += lineas_campo("Cambios registrados", "Ninguno en PATITAS-PETS")
        for movimiento in historial:
            detalle = (f"{movimiento['estado_anterior']} -> {movimiento['estado_nuevo']} "
                       f"(por {movimiento['usuario']})")
            if movimiento["observacion"]:
                detalle += f". Observación: {movimiento['observacion']}"
            lineas += lineas_campo(movimiento["fecha_cambio"], detalle)

    lineas.append(borde())
    lineas += lineas_campo("Registrado por", registrador)
    lineas += lineas_campo("Comprobante generado", datetime.now().strftime(config.FORMATO_FECHA))
    lineas.append(linea_texto())
    lineas.append(linea_centrada("Conserve este número de radicado para hacer seguimiento a su solicitud."))
    lineas.append(borde())

    # Control de calidad: ninguna línea puede quedar con un ancho distinto de 120
    for linea in lineas:
        if len(linea) != ANCHO:
            raise ValueError(f"Línea con ancho {len(linea)} en el radicado: {linea!r}")
    return "\n".join(lineas)
