"""
consultas.py
------------
Opción 2 del menú: Consultar PQRS.

    1. Consultar una PQRS por número de radicado (se muestra como radicado).
    2. Buscar las PQRS de un solicitante por su número de documento.
    3. Estado general y listado de registros activos.
    4. PQRS activas más antiguas.
    5. PQRS próximas a vencer y vencidas.

Los listados se muestran en tablas por páginas; al final se puede escribir
el número de una fila para ver esa PQRS con el formato del radicado.
"""

import re
from datetime import datetime

import config
import interfaz
import archivos
import autenticacion
import radicado
import reportes
import validaciones

# Acepta PET-003001, pet-3001 o PET 3001
PATRON_RADICADO = re.compile(r"^([A-Za-z]{3})[- ]?0*([0-9]+)$")


def buscar_por_radicado(texto):
    """Devuelve (registro, "") si existe, o (None, mensaje) si no."""
    coincidencia = PATRON_RADICADO.match(texto.strip())
    if not coincidencia:
        return None, "Formato inválido. Ejemplo de número de radicado: PET-003001"
    prefijo = coincidencia.group(1).upper()
    numero = int(coincidencia.group(2))
    tipos_por_prefijo = {datos["prefijo"]: tipo for tipo, datos in config.TIPOS_SOLICITUD.items()}
    if prefijo not in tipos_por_prefijo:
        return None, "Prefijo desconocido. Use PET, QUE, REC o SUG."
    registro = archivos.buscar_por_id(tipos_por_prefijo[prefijo], numero)
    if registro is None:
        return None, f"No existe la PQRS {prefijo}-{numero:06d}."
    return registro, ""


def mostrar_radicado_de(registro, titulo="CONSULTA DE ESTADO DE PQRS"):
    """Muestra una PQRS con el formato del radicado, incluido su historial de estados."""
    usuario = autenticacion.buscar_usuario(autenticacion.cargar_usuarios(),
                                           registro["usuario_registro"])
    nombre = usuario["nombre_completo"] if usuario else ""
    texto = radicado.construir_radicado(registro, titulo=titulo, nombre_registrador=nombre,
                                        historial=archivos.historial_de(registro))
    print()
    print(texto)
    return texto


def ver_listado(registros, ahora):
    """Muestra una tabla paginada y permite abrir el radicado de una fila."""
    if not registros:
        print("\n  No hay PQRS que cumplan la condición.")
        return
    encabezados = ["#", "Radicado", "Radicación", "Vence", "Días", "Estado", "Mascota", "Asunto"]
    anchos = [5, 10, 10, 10, 5, 11, 7, 28]
    filas = [
        [posicion, radicado.numero_radicado(r), r["fecha_radicacion"][:10],
         r["fecha_maxima_respuesta"][:10],
         reportes.dias_para_vencer(r, ahora) if reportes.es_activa(r) else "-",
         r["estado_peticion"], r["tipo_mascota"], r["asunto_titulo"]]
        for posicion, r in enumerate(registros, start=1)
    ]
    print()
    interfaz.mostrar_tabla(encabezados, filas, anchos)
    print("  (Días = días que faltan para la fecha máxima; negativo = vencida)")
    eleccion = input("\n  Número de fila para ver su radicado (Enter para volver): ").strip()
    if eleccion.isdigit() and 1 <= int(eleccion) <= len(registros):
        mostrar_radicado_de(registros[int(eleccion) - 1])


# ---------------------------------------------------------------------------
# Opciones del submenú
# ---------------------------------------------------------------------------
def consultar_por_radicado():
    registro, mensaje = buscar_por_radicado(input("  Número de radicado (ej. PET-003001): "))
    if registro is None:
        print(f"  [!] {mensaje}")
        return
    mostrar_radicado_de(registro)


def buscar_por_documento():
    numero = input("  Número de documento del solicitante: ").strip()
    es_valido, mensaje = validaciones.validar_numero_documento(numero)
    if not es_valido:
        print(f"  [!] {mensaje}")
        return
    encontrados = [r for r in archivos.leer_todas() if r["numero_documento"] == numero]
    print(f"\n  Se encontraron {len(encontrados)} PQRS para el documento {numero}.")
    ver_listado(encontrados, datetime.now())


def estado_general():
    """Resumen de cantidades por tipo y estado, y listado de las PQRS activas."""
    ahora = datetime.now()
    todas = archivos.leer_todas()
    print("  ESTADO GENERAL DE LAS PQRS\n")
    encabezados = ["Tipo"] + config.ESTADOS + ["Total"]
    filas = []
    for tipo, datos in config.TIPOS_SOLICITUD.items():
        del_tipo = [r for r in todas if r["tipo_solicitud"] == tipo]
        cantidades = [sum(1 for r in del_tipo if r["estado_peticion"] == e) for e in config.ESTADOS]
        filas.append([datos["nombre"]] + [reportes.formato_numero(c) for c in cantidades]
                     + [reportes.formato_numero(len(del_tipo))])
    totales = [sum(1 for r in todas if r["estado_peticion"] == e) for e in config.ESTADOS]
    filas.append(["TOTAL"] + [reportes.formato_numero(c) for c in totales]
                 + [reportes.formato_numero(len(todas))])
    interfaz.mostrar_tabla(encabezados, filas, [12, 11, 11, 11, 8])

    activas = reportes.registros_activos(todas)
    print(f"\n  Registros activos (Registrada o En proceso): {reportes.formato_numero(len(activas))}")
    if not interfaz.confirmar("  ¿Desea listar los registros activos de un tipo de PQRS?"):
        return
    tipos = list(config.TIPOS_SOLICITUD)
    for numero, tipo in enumerate(tipos, start=1):
        print(f"    {numero}. {config.TIPOS_SOLICITUD[tipo]['nombre']}")
    tipo = tipos[interfaz.pedir_opcion(f"  Tipo de PQRS (1-{len(tipos)}): ", 1, len(tipos)) - 1]
    del_tipo = [r for r in activas if r["tipo_solicitud"] == tipo]
    del_tipo.sort(key=lambda r: r["fecha_maxima_respuesta"])     # primero las más urgentes
    ver_listado(del_tipo, ahora)


def mas_antiguas():
    ahora = datetime.now()
    antiguas = reportes.mas_antiguas(archivos.leer_todas(), cantidad=10)
    print("  LAS 10 PQRS ACTIVAS MÁS ANTIGUAS (por fecha de radicación)")
    if antiguas:
        primera = antiguas[0]
        print(f"  La más antigua es {radicado.numero_radicado(primera)}, radicada el "
              f"{primera['fecha_radicacion']} ({(ahora - reportes.a_fecha(primera['fecha_radicacion'])).days} días).")
    ver_listado(antiguas, ahora)


def proximas_a_vencer():
    ahora = datetime.now()
    todas = archivos.leer_todas()
    proximas = reportes.por_clasificacion_de_plazo(todas, reportes.ETIQUETA_PROXIMA, ahora)
    vencidas = reportes.por_clasificacion_de_plazo(todas, reportes.ETIQUETA_VENCIDA, ahora)
    print(f"  Próximas a vencer (menos de {config.DIAS_ALERTA_VENCIMIENTO} días): "
          f"{reportes.formato_numero(len(proximas))}")
    print(f"  Vencidas (superaron la fecha máxima sin solucionarse): "
          f"{reportes.formato_numero(len(vencidas))}\n")
    print("    1. Ver las próximas a vencer")
    print("    2. Ver las vencidas")
    print("    3. Volver")
    opcion = interfaz.pedir_opcion("  Seleccione una opción (1-3): ", 1, 3)
    if opcion == 1:
        ver_listado(proximas, ahora)
    elif opcion == 2:
        ver_listado(vencidas, ahora)


def menu_consultas(sesion):
    """Submenú de la opción 2. Se repite hasta elegir Volver."""
    opciones = {
        1: ("Consultar PQRS por número de radicado", consultar_por_radicado),
        2: ("Buscar PQRS por documento del solicitante", buscar_por_documento),
        3: ("Estado general y registros activos", estado_general),
        4: ("PQRS activas más antiguas", mas_antiguas),
        5: ("PQRS próximas a vencer y vencidas", proximas_a_vencer),
    }
    while True:
        interfaz.mostrar_encabezado("2. CONSULTAR PQRS", sesion)
        for numero, (texto, _) in opciones.items():
            print(f"      {numero}. {texto}")
        print("      6. Volver al menú principal\n")
        opcion = interfaz.pedir_opcion("  Seleccione una opción (1-6): ", 1, 6)
        if opcion == 6:
            return
        interfaz.mostrar_encabezado(f"2.{opcion} {opciones[opcion][0].upper()}", sesion)
        opciones[opcion][1]()
        interfaz.pausar()
