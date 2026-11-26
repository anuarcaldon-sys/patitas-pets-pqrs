"""
cambios.py
----------
Opción 3 del menú: Registrar cambio en PQRS.

Cambia el estado de una PQRS siguiendo el flujo obligatorio
    Registrada -> En proceso -> Solucionada
sin saltos ni retrocesos. Cada cambio:
    1. se valida con validaciones.validar_cambio_estado,
    2. actualiza la línea de la PQRS en su archivo plano,
    3. queda registrado en data/Historial.txt (fecha, usuario y observación),
    4. genera un comprobante en data/radicados/.
Al pasar a Solucionada, además muestra la fecha de respuesta, los días
transcurridos desde la radicación y si se respondió dentro del plazo.
"""

from datetime import datetime

import config
import interfaz
import archivos
import radicado
import validaciones
import consultas


def pedir_observacion():
    """Observación opcional del cambio; se repite hasta que sea válida."""
    while True:
        texto = " ".join(input("  Observación (opcional, Enter para omitir): ").split())
        es_valido, mensaje = validaciones.validar_observacion(texto)
        if es_valido:
            return texto
        print(f"    [!] {mensaje}")


def resumen_respuesta(registro, fecha_respuesta):
    """
    Días transcurridos entre la radicación y la respuesta, y cumplimiento del plazo.
    Devuelve una tupla (dias_transcurridos, plazo_en_dias, dentro_del_plazo).
    """
    radicacion = datetime.strptime(registro["fecha_radicacion"], config.FORMATO_FECHA)
    maxima = datetime.strptime(registro["fecha_maxima_respuesta"], config.FORMATO_FECHA)
    dias = (fecha_respuesta - radicacion).days
    plazo = (maxima - radicacion).days
    return dias, plazo, fecha_respuesta <= maxima


def registrar_cambio(sesion):
    """Flujo completo de la opción 3 del menú principal."""
    interfaz.mostrar_encabezado("3. REGISTRAR CAMBIO EN PQRS", sesion)
    registro, mensaje = consultas.buscar_por_radicado(
        input("  Número de radicado (ej. PET-003001): "))
    if registro is None:
        print(f"  [!] {mensaje}")
        interfaz.pausar()
        return

    numero = radicado.numero_radicado(registro)
    estado_actual = registro["estado_peticion"]
    print(f"\n  PQRS ............: {numero}")
    print(f"  Solicitante .....: {registro['nombre_completo']}")
    print(f"  Asunto ..........: {registro['asunto_titulo']}")
    print(f"  Fecha máxima ....: {registro['fecha_maxima_respuesta']}")
    print(f"  Estado actual ...: {estado_actual}")

    if estado_actual not in config.SIGUIENTE_ESTADO:
        print("\n  [!] Esta PQRS ya está Solucionada; no admite más cambios de estado.")
        interfaz.pausar()
        return

    estado_nuevo = config.SIGUIENTE_ESTADO[estado_actual]
    print(f"\n  Cambio permitido por el flujo: {estado_actual} -> {estado_nuevo}\n")
    observacion = pedir_observacion()
    if not interfaz.confirmar(f"\n  ¿Confirma el cambio a '{estado_nuevo}'?"):
        print("  No se realizó ningún cambio.")
        interfaz.pausar()
        return

    # Validación final antes de escribir (defensa ante cualquier error del flujo)
    es_valido, mensaje = validaciones.validar_cambio_estado(estado_actual, estado_nuevo)
    if not es_valido:
        print(f"  [!] {mensaje}")
        interfaz.pausar()
        return

    ahora = datetime.now().replace(microsecond=0)
    registro["estado_peticion"] = estado_nuevo
    archivos.actualizar_registro(registro)
    archivos.registrar_historial({
        "tipo_solicitud": registro["tipo_solicitud"],
        "id": registro["id"],
        "estado_anterior": estado_actual,
        "estado_nuevo": estado_nuevo,
        "fecha_cambio": ahora.strftime(config.FORMATO_FECHA),
        "usuario": sesion["usuario"],
        "observacion": observacion,
    })

    texto = consultas.mostrar_radicado_de(registro, titulo="COMPROBANTE DE CAMBIO DE ESTADO")
    nombre_archivo = f"{numero}_{estado_nuevo.replace(' ', '-')}.txt"
    ruta = archivos.guardar_radicado(texto, nombre_archivo)
    print(f"\n  [OK] {numero} pasó de '{estado_actual}' a '{estado_nuevo}'.")
    print(f"  [OK] Cambio registrado en {config.ARCHIVO_HISTORIAL.name} y comprobante en: {ruta}")

    if estado_nuevo == "Solucionada":
        dias, plazo, a_tiempo = resumen_respuesta(registro, ahora)
        print(f"\n  Fecha de respuesta ....: {ahora.strftime(config.FORMATO_FECHA)}")
        print(f"  Radicada el ...........: {registro['fecha_radicacion']}")
        print(f"  Días transcurridos ....: {dias} días (plazo otorgado: {plazo} días)")
        if a_tiempo:
            print("  [OK] Respondida dentro del plazo.")
        else:
            print(f"  [!] Respondida fuera del plazo: {dias - plazo} días de retraso.")
    interfaz.pausar()
