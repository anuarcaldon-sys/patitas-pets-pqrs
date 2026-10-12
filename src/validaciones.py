"""
validaciones.py
---------------
Funciones que revisan cada dato antes de guardar una PQRS.

Todas devuelven una tupla (es_valido, mensaje):
    (True, "")                    -> el dato cumple las reglas
    (False, "explicación")        -> el dato no cumple; el mensaje dice por qué

Las reglas salen del enunciado del proyecto (sección "Registrar PQRS").
Ejecutar este archivo directamente corre las pruebas con los ejemplos
válidos e inválidos del enunciado:  python src/validaciones.py
"""

import re
from datetime import datetime

import config

# Letras permitidas en español (incluye tildes, diéresis y ñ)
LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"

PATRON_NOMBRE = re.compile(rf"^[{LETRAS}' \-]+$")
PATRON_DOCUMENTO = re.compile(r"^[0-9]{3,15}$")
PATRON_TELEFONO = re.compile(r"^[0-9]{10}$")
PATRON_CORREO = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$"
)
PATRON_DIRECCION = re.compile(rf"^[{LETRAS}0-9#.,/° \-]+$")
PATRON_ASUNTO = re.compile(rf"^[{LETRAS}0-9 .,;:¿?¡!()\"'/\-]+$")

# Formatos de fecha que acepta el sistema al digitar la fecha de radicación
FORMATOS_FECHA_ACEPTADOS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]


# ---------------------------------------------------------------------------
# Datos del solicitante
# ---------------------------------------------------------------------------
def validar_nombre(nombre):
    """Nombre completo: 3-100 caracteres, solo letras, espacios, ' y -."""
    if not nombre.strip():
        return False, "El nombre completo es obligatorio."
    if not 3 <= len(nombre) <= 100:
        return False, "El nombre debe tener entre 3 y 100 caracteres."
    if any(caracter.isdigit() for caracter in nombre):
        return False, "El nombre no puede contener números."
    if not PATRON_NOMBRE.match(nombre):
        return False, ("Solo se permiten letras (con tildes y ñ), espacios, "
                       "apóstrofes (') y guiones (-).")
    if not any(caracter.isalpha() for caracter in nombre):
        return False, "El nombre debe contener letras."
    return True, ""


def validar_tipo_documento(tipo):
    """Tipo de documento: debe ser uno de los códigos del catálogo."""
    if tipo not in config.TIPOS_DOCUMENTO:
        return False, "Tipo de documento no permitido (CC, TI, CE, PP o NIT)."
    return True, ""


def validar_numero_documento(numero):
    """Número de documento: solo dígitos, entre 3 y 15."""
    if not numero:
        return False, "El número de documento es obligatorio."
    if not PATRON_DOCUMENTO.match(numero):
        return False, "Debe tener entre 3 y 15 dígitos, sin letras ni símbolos."
    return True, ""


def validar_telefono(telefono):
    """Teléfono de contacto: exactamente 10 dígitos."""
    if not telefono:
        return False, "El teléfono de contacto es obligatorio."
    if not PATRON_TELEFONO.match(telefono):
        return False, "Debe tener exactamente 10 dígitos, sin letras ni símbolos."
    return True, ""


def validar_correo(correo):
    """Correo: máximo 254 caracteres, un único @ y un dominio válido."""
    if not correo:
        return False, "El correo electrónico es obligatorio."
    if len(correo) > 254:
        return False, "El correo no puede superar 254 caracteres."
    if correo.count("@") != 1:
        return False, "El correo debe contener un único símbolo @."
    if ".." in correo or not PATRON_CORREO.match(correo):
        return False, "Formato inválido. Use la estructura usuario@dominio.com"
    return True, ""


def validar_direccion(direccion):
    """Dirección: OPCIONAL. Si se escribe, 5-200 caracteres (letras, números, # - . , /)."""
    if direccion == "":
        return True, ""          # campo opcional: vacío es válido
    if not 5 <= len(direccion) <= 200:
        return False, "La dirección debe tener entre 5 y 200 caracteres."
    if not PATRON_DIRECCION.match(direccion):
        return False, "Solo se permiten letras, números, espacios y los signos # - . , /"
    return True, ""


# ---------------------------------------------------------------------------
# Información de la PQRS
# ---------------------------------------------------------------------------
def validar_tipo_solicitud(tipo):
    """Tipo de solicitud: Peticion, Queja, Reclamo o Sugerencia."""
    if tipo not in config.TIPOS_SOLICITUD:
        return False, "Tipo de solicitud no permitido."
    return True, ""


def convertir_fecha(texto):
    """Convierte un texto a datetime probando los formatos aceptados. None si no se puede."""
    for formato in FORMATOS_FECHA_ACEPTADOS:
        try:
            return datetime.strptime(texto.strip(), formato)
        except ValueError:
            pass
    return None


def validar_fecha_radicacion(texto):
    """Fecha de radicación: formato datetime válido y no puede ser futura."""
    if not texto.strip():
        return False, "La fecha de radicación es obligatoria."
    fecha = convertir_fecha(texto)
    if fecha is None:
        return False, "Fecha inválida. Use AAAA-MM-DD HH:MM (ejemplo: 2026-09-28 14:30)."
    if fecha > datetime.now():
        return False, "La fecha de radicación no puede ser una fecha futura."
    return True, ""


def validar_asunto(asunto):
    """Asunto: 5-150 caracteres; letras, números y puntuación básica."""
    if not asunto.strip():
        return False, "El asunto es obligatorio."
    if not 5 <= len(asunto) <= 150:
        return False, "El asunto debe tener entre 5 y 150 caracteres."
    if not PATRON_ASUNTO.match(asunto):
        return False, "Solo se permiten letras, números y signos de puntuación básicos."
    return True, ""


def validar_descripcion(descripcion):
    """Descripción: texto libre de 20 a 2000 caracteres, no solo espacios."""
    if not descripcion.strip():
        return False, "La descripción es obligatoria y no puede tener solo espacios."
    if len(descripcion) < 20:
        return False, "La descripción debe tener mínimo 20 caracteres."
    if len(descripcion) > 2000:
        return False, "La descripción no puede superar 2000 caracteres."
    if config.SEPARADOR in descripcion:
        # El | separa las columnas del archivo plano; si se guardara, dañaría el registro
        return False, f"El carácter '{config.SEPARADOR}' está reservado por el sistema."
    return True, ""


# ---------------------------------------------------------------------------
# Información relacionada, estado y usuario registrador
# ---------------------------------------------------------------------------
def validar_opcion(valor, permitidos, nombre_campo):
    """Valida cualquier campo de lista cerrada (mascota, campus, canal, estado...)."""
    if valor not in permitidos:
        return False, f"Valor no permitido para {nombre_campo}."
    return True, ""


def validar_cambio_estado(estado_actual, estado_nuevo):
    """Solo permite avanzar un paso: Registrada -> En proceso -> Solucionada."""
    if estado_nuevo not in config.ESTADOS:
        return False, "Estado no permitido."
    if estado_actual not in config.SIGUIENTE_ESTADO:
        return False, f"La PQRS está {estado_actual}; no admite más cambios de estado."
    permitido = config.SIGUIENTE_ESTADO[estado_actual]
    if estado_nuevo != permitido:
        return False, f"Cambio no permitido: desde {estado_actual} solo se puede pasar a {permitido}."
    return True, ""


def validar_observacion(observacion):
    """Observación del cambio: OPCIONAL, máximo 300 caracteres y sin el carácter |."""
    if len(observacion) > config.MAX_OBSERVACION:
        return False, f"La observación no puede superar {config.MAX_OBSERVACION} caracteres."
    if config.SEPARADOR in observacion:
        return False, f"El carácter '{config.SEPARADOR}' está reservado por el sistema."
    return True, ""


def validar_usuario_registrador(usuario, lista_usuarios_activos):
    """El registrador es obligatorio y debe ser un usuario activo y autorizado."""
    if not usuario:
        return False, "No se puede guardar la PQRS sin usuario registrador."
    if usuario not in [u["usuario"] for u in lista_usuarios_activos]:
        return False, "El usuario registrador no está activo o no está autorizado."
    return True, ""


# ---------------------------------------------------------------------------
# Pruebas rápidas con los ejemplos del enunciado
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pruebas = [
        (validar_nombre, "Juan David Pérez Gómez", True),
        (validar_nombre, "Juan123", False),
        (validar_numero_documento, "1037654321", True),
        (validar_numero_documento, "10376A321", False),
        (validar_telefono, "3001234567", True),
        (validar_telefono, "300123ABCD", False),
        (validar_correo, "usuario@correo.com", True),
        (validar_correo, "usuariocorreo.com", False),
        (validar_direccion, "Avenida Siempreviva 742", True),
        (validar_direccion, "", True),
        (validar_asunto, "Solicitud de información sobre servicio veterinario.", True),
        (validar_descripcion, "Solicito información sobre los servicios de consulta "
                              "para caninos disponibles en el campus Robledo.", True),
        (validar_descripcion, "                          ", False),
        (validar_fecha_radicacion, "2026-01-15 10:00", True),
        (validar_fecha_radicacion, "2999-01-01", False),
    ]
    # Pruebas del flujo de estados: (estado actual, estado nuevo, resultado esperado)
    pruebas_estado = [
        ("Registrada", "En proceso", True),
        ("En proceso", "Solucionada", True),
        ("Registrada", "Solucionada", False),   # no se permiten saltos
        ("En proceso", "Registrada", False),    # no se permiten retrocesos
        ("Solucionada", "En proceso", False),   # una PQRS solucionada queda cerrada
    ]
    errores = 0
    for funcion, dato, esperado in pruebas:
        resultado, mensaje = funcion(dato)
        estado = "OK " if resultado == esperado else "ERROR"
        errores += resultado != esperado
        print(f"[{estado}] {funcion.__name__}({dato[:40]!r}) -> {resultado} {mensaje}")
    for actual, nuevo, esperado in pruebas_estado:
        resultado, mensaje = validar_cambio_estado(actual, nuevo)
        estado = "OK " if resultado == esperado else "ERROR"
        errores += resultado != esperado
        print(f"[{estado}] validar_cambio_estado({actual!r} -> {nuevo!r}) -> {resultado} {mensaje}")
    total = len(pruebas) + len(pruebas_estado)
    print(f"\n{total - errores} de {total} pruebas correctas.")
