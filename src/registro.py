"""
registro.py
-----------
Opción 1 del menú: Registrar PQRS.

Pide los datos campo por campo, valida cada uno con validaciones.py y no
avanza hasta que el dato sea correcto. Al final muestra un resumen, pide
confirmación, guarda el registro en el archivo de su tipo (archivos.py) y
genera el radicado de 120 columnas (radicado.py).

En cualquier campo se puede escribir "cancelar" para salir sin guardar.
"""

from datetime import datetime, timedelta

import config
import interfaz
import validaciones
import archivos
import radicado
import autenticacion

PALABRA_CANCELAR = "cancelar"


class RegistroCancelado(Exception):
    """Se lanza cuando el operador escribe 'cancelar' en cualquier campo."""


def leer(etiqueta):
    """Lee un texto, quita espacios repetidos y revisa si se pidió cancelar."""
    texto = " ".join(input(f"    {etiqueta}: ").split())
    if texto.lower() == PALABRA_CANCELAR:
        raise RegistroCancelado
    return texto


def pedir_texto(etiqueta, funcion_validacion):
    """Pide un dato hasta que la función de validación lo acepte."""
    while True:
        valor = leer(etiqueta)
        es_valido, mensaje = funcion_validacion(valor)
        if es_valido:
            return valor
        print(f"      [!] {mensaje}")


def elegir(etiqueta, opciones):
    """
    Muestra una lista numerada y devuelve el valor elegido.
    opciones es un diccionario {valor_que_se_guarda: texto_que_se_muestra}.
    """
    valores = list(opciones)
    print(f"    {etiqueta}:")
    for numero, valor in enumerate(valores, start=1):
        print(f"       {numero}. {opciones[valor]}")
    while True:
        texto = leer(f"Seleccione 1-{len(valores)}")
        if texto.isdigit() and 1 <= int(texto) <= len(valores):
            return valores[int(texto) - 1]
        print(f"      [!] Digite un número entre 1 y {len(valores)}.")


def pedir_fecha_radicacion():
    """Fecha de radicación: Enter toma la fecha y hora actual; no se aceptan fechas futuras."""
    print("    Fecha de radicación (AAAA-MM-DD HH:MM). Presione Enter para usar la fecha y hora actual.")
    while True:
        texto = leer("Fecha de radicación")
        if texto == "":
            return datetime.now().replace(microsecond=0)
        es_valido, mensaje = validaciones.validar_fecha_radicacion(texto)
        if es_valido:
            return validaciones.convertir_fecha(texto)
        print(f"      [!] {mensaje}")


def como_diccionario(lista):
    """Convierte una lista en {valor: valor} para usarla con elegir()."""
    return {valor: valor for valor in lista}


def capturar_datos():
    """Pide todos los campos de la PQRS y devuelve el registro (sin id)."""
    print("  --- DATOS DEL SOLICITANTE ---")
    nombre = pedir_texto("Nombre completo", validaciones.validar_nombre)
    tipo_documento = elegir("Tipo de documento",
                            {codigo: f"{texto} ({codigo})"
                             for codigo, texto in config.TIPOS_DOCUMENTO.items()})
    numero_documento = pedir_texto("Número de documento", validaciones.validar_numero_documento)
    tipo_telefono = elegir("Tipo de teléfono", como_diccionario(config.TIPOS_TELEFONO))
    telefono = pedir_texto("Teléfono de contacto (10 dígitos)", validaciones.validar_telefono)
    correo = pedir_texto("Correo electrónico", validaciones.validar_correo)
    direccion = pedir_texto("Dirección (opcional, Enter para omitir)",
                            validaciones.validar_direccion)

    print("\n  --- INFORMACIÓN DE LA PQRS ---")
    tipo_solicitud = elegir("Tipo de solicitud",
                            {clave: datos["nombre"]
                             for clave, datos in config.TIPOS_SOLICITUD.items()})
    fecha_radicacion = pedir_fecha_radicacion()
    canal = elegir("Canal de recepción", como_diccionario(config.CANALES_RECEPCION))
    asunto = pedir_texto("Asunto o título", validaciones.validar_asunto)
    descripcion = pedir_texto("Descripción detallada (mínimo 20 caracteres)",
                              validaciones.validar_descripcion)

    print("\n  --- INFORMACIÓN RELACIONADA ---")
    mascota = elegir("Tipo de mascota", como_diccionario(config.TIPOS_MASCOTA))
    campus = elegir("Campus relacionado", como_diccionario(config.CAMPUS))

    # Gestión de tiempos: fecha máxima = fecha de radicación + plazo del equipo
    fecha_maxima = fecha_radicacion + timedelta(days=config.PLAZO_RESPUESTA_DIAS)

    return {
        "id": "",
        "nombre_completo": nombre,
        "tipo_documento": tipo_documento,
        "numero_documento": numero_documento,
        "tipo_telefono": tipo_telefono,
        "telefono_contacto": telefono,
        "correo_electronico": correo,
        "direccion": direccion,
        "tipo_solicitud": tipo_solicitud,
        "fecha_radicacion": fecha_radicacion.strftime(config.FORMATO_FECHA),
        "canal_recepcion": canal,
        "asunto_titulo": asunto,
        "descripcion_detallada": descripcion,
        "tipo_mascota": mascota,
        "campus_relacionado": campus,
        "fecha_maxima_respuesta": fecha_maxima.strftime(config.FORMATO_FECHA),
        "estado_peticion": config.ESTADO_INICIAL,
        "usuario_registro": "",
    }


def mostrar_resumen(registro):
    """Muestra los datos capturados para que el operador los revise antes de guardar."""
    print("\n  --- RESUMEN ANTES DE GUARDAR ---")
    for campo in config.CAMPOS[1:]:
        valor = registro[campo] or "N/A"
        if len(valor) > 70:
            valor = valor[:67] + "..."
        print(f"    {campo:<24}: {valor}")


def registrar_pqrs(sesion):
    """Flujo completo de la opción 1 del menú principal."""
    interfaz.mostrar_encabezado("1. REGISTRAR PQRS", sesion)
    print("  Escriba 'cancelar' en cualquier campo para salir sin guardar.\n")

    try:
        registro = capturar_datos()
    except RegistroCancelado:
        print("\n  Registro cancelado. No se guardó ninguna información.")
        interfaz.pausar()
        return

    # Usuario registrador: se toma de la sesión y se verifica que siga activo
    registro["usuario_registro"] = sesion["usuario"]
    activos = autenticacion.usuarios_activos(autenticacion.cargar_usuarios())
    es_valido, mensaje = validaciones.validar_usuario_registrador(sesion["usuario"], activos)
    if not es_valido:
        print(f"\n  [!] {mensaje}")
        interfaz.pausar()
        return

    mostrar_resumen(registro)
    respuesta = input("\n  ¿Desea guardar esta PQRS? (S/N): ").strip().upper()
    if respuesta != "S":
        print("  La PQRS NO fue guardada.")
        interfaz.pausar()
        return

    archivos.guardar_registro(registro)
    texto = radicado.construir_radicado(registro, nombre_registrador=sesion["nombre"])
    ruta = archivos.guardar_radicado(texto, f"{radicado.numero_radicado(registro)}.txt")

    print("\n" + texto)
    print(f"\n  [OK] PQRS guardada en {config.TIPOS_SOLICITUD[registro['tipo_solicitud']]['archivo'].name}"
          f" con el radicado {radicado.numero_radicado(registro)}.")
    print(f"  [OK] Comprobante guardado en: {ruta}")
    interfaz.pausar()
