"""
archivos.py
-----------
Lectura y escritura de los archivos planos del programa (carpeta data/):

- Peticion.txt, Queja.txt, Reclamo.txt y Sugerencia.txt: una PQRS por línea.
- Historial.txt: bitácora de cambios de estado.
- data/radicados/ y data/exportaciones/: comprobantes y reportes generados.

Reglas que cumple este módulo:
- Cada tipo de PQRS se guarda solo en su propio archivo.
- Todos los archivos de PQRS tienen la misma estructura (config.CAMPOS) separada por |.
- Cada archivo lleva su propio consecutivo: el nuevo id es el mayor id que
  ya existe en ESE archivo + 1. Así los registros nuevos continúan la
  numeración de las bases de datos entregadas (3000 -> 3001) y nunca se
  repite un número.
"""

import csv

import config


def ruta_archivo(tipo):
    """Devuelve la ruta del archivo plano que corresponde al tipo de PQRS."""
    return config.TIPOS_SOLICITUD[tipo]["archivo"]


def crear_si_no_existe(ruta, campos):
    """Crea un archivo plano vacío (solo con el encabezado) si todavía no existe."""
    if ruta.exists():
        return False
    with open(ruta, "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(config.SEPARADOR.join(campos) + "\n")
    return True


def preparar_base_de_datos():
    """
    Revisa la estructura de almacenamiento al iniciar el programa:
    crea las carpetas y los archivos que falten (solo con el encabezado)
    y avisa si algún encabezado no coincide con la estructura esperada.
    Devuelve una lista de avisos para mostrar en pantalla.
    """
    if not config.ARCHIVO_USUARIOS.exists():
        raise FileNotFoundError(f"No se encontró {config.ARCHIVO_USUARIOS}")

    config.CARPETA_RADICADOS.mkdir(parents=True, exist_ok=True)
    config.CARPETA_EXPORTACIONES.mkdir(parents=True, exist_ok=True)
    encabezado_esperado = config.SEPARADOR.join(config.CAMPOS)
    avisos = []

    for tipo in config.TIPOS_SOLICITUD:
        ruta = ruta_archivo(tipo)
        if crear_si_no_existe(ruta, config.CAMPOS):
            avisos.append(f"Se creó {ruta.name} (vacío, solo encabezado).")
            continue
        with open(ruta, encoding="utf-8") as archivo:
            encabezado = archivo.readline().strip()
        if encabezado != encabezado_esperado:
            avisos.append(f"El encabezado de {ruta.name} no coincide con la estructura esperada.")

    crear_si_no_existe(config.ARCHIVO_HISTORIAL, config.CAMPOS_HISTORIAL)
    return avisos


def leer_archivo_plano(ruta):
    """Lee cualquier archivo plano con encabezado y devuelve una lista de diccionarios."""
    registros = []
    with open(ruta, encoding="utf-8") as archivo:
        encabezado = archivo.readline().strip().split(config.SEPARADOR)
        for numero_linea, linea in enumerate(archivo, start=2):
            linea = linea.rstrip("\r\n")
            if not linea.strip():
                continue                      # ignora líneas en blanco
            valores = linea.split(config.SEPARADOR)
            if len(valores) != len(encabezado):
                print(f"  [Aviso] {ruta.name}, línea {numero_linea}: "
                      f"tiene {len(valores)} campos y se esperaban {len(encabezado)}. Se omite.")
                continue
            registros.append(dict(zip(encabezado, valores)))
    return registros


def leer_registros(tipo):
    """Lee todas las PQRS de un tipo."""
    return leer_archivo_plano(ruta_archivo(tipo))


def leer_todas():
    """Lee los cuatro archivos y devuelve una sola lista con todas las PQRS."""
    todas = []
    for tipo in config.TIPOS_SOLICITUD:
        todas.extend(leer_registros(tipo))
    return todas


def siguiente_id(tipo):
    """Consecutivo propio de cada archivo: mayor id existente + 1 (1 si está vacío)."""
    ids = [int(r["id"]) for r in leer_registros(tipo) if r["id"].isdigit()]
    return max(ids, default=0) + 1


def agregar_linea(ruta, linea):
    """
    Agrega una línea al final de un archivo. Si el archivo no termina en
    salto de línea, primero agrega uno para no pegar la línea al último registro.
    """
    with open(ruta, "rb") as archivo_binario:
        archivo_binario.seek(0, 2)                        # ir al final
        falta_salto = False
        if archivo_binario.tell() > 0:
            archivo_binario.seek(-1, 2)
            falta_salto = archivo_binario.read(1) != b"\n"

    with open(ruta, "a", encoding="utf-8", newline="\n") as archivo:
        if falta_salto:
            archivo.write("\n")
        archivo.write(linea + "\n")


def guardar_registro(registro):
    """
    Agrega la PQRS al final del archivo de su tipo y devuelve el id asignado.
    El id se calcula justo antes de escribir para no repetir consecutivos.
    """
    tipo = registro["tipo_solicitud"]
    registro["id"] = str(siguiente_id(tipo))
    linea = config.SEPARADOR.join(registro[campo] for campo in config.CAMPOS)
    agregar_linea(ruta_archivo(tipo), linea)
    return int(registro["id"])


def actualizar_registro(registro):
    """
    Reemplaza en el archivo la línea de la PQRS con el mismo id.
    Las demás líneas se copian tal cual. Se escribe primero un archivo
    temporal y luego se reemplaza el original en un solo paso: si algo
    falla a mitad de camino, el archivo original queda intacto.
    """
    ruta = ruta_archivo(registro["tipo_solicitud"])
    with open(ruta, encoding="utf-8") as archivo:
        lineas = archivo.read().splitlines()

    nueva_linea = config.SEPARADOR.join(registro[campo] for campo in config.CAMPOS)
    encontrado = False
    for posicion in range(1, len(lineas)):          # la línea 0 es el encabezado
        if lineas[posicion].split(config.SEPARADOR)[0] == registro["id"]:
            lineas[posicion] = nueva_linea
            encontrado = True
            break
    if not encontrado:
        raise ValueError(f"No existe el id {registro['id']} en {ruta.name}")

    temporal = ruta.with_suffix(".tmp")
    with open(temporal, "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write("\n".join(lineas) + "\n")
    try:
        temporal.replace(ruta)
    except OSError:
        temporal.unlink(missing_ok=True)   # se descarta la copia; el original sigue intacto
        raise


def buscar_por_id(tipo, id_buscado):
    """Busca una PQRS por su id dentro del archivo de su tipo. None si no existe."""
    for registro in leer_registros(tipo):
        if registro["id"] == str(id_buscado):
            return registro
    return None


# ---------------------------------------------------------------------------
# Historial de cambios de estado
# ---------------------------------------------------------------------------
def registrar_historial(movimiento):
    """Agrega un cambio de estado a Historial.txt (diccionario con CAMPOS_HISTORIAL)."""
    crear_si_no_existe(config.ARCHIVO_HISTORIAL, config.CAMPOS_HISTORIAL)
    linea = config.SEPARADOR.join(movimiento[campo] for campo in config.CAMPOS_HISTORIAL)
    agregar_linea(config.ARCHIVO_HISTORIAL, linea)


def leer_historial():
    """Devuelve todos los cambios de estado registrados (lista vacía si no hay archivo)."""
    if not config.ARCHIVO_HISTORIAL.exists():
        return []
    return leer_archivo_plano(config.ARCHIVO_HISTORIAL)


def historial_de(registro):
    """Cambios de estado de una PQRS específica, en orden cronológico."""
    return [m for m in leer_historial()
            if m["tipo_solicitud"] == registro["tipo_solicitud"] and m["id"] == registro["id"]]


# ---------------------------------------------------------------------------
# Archivos generados: radicados y exportaciones
# ---------------------------------------------------------------------------
def guardar_texto(carpeta, nombre_archivo, texto):
    """Guarda un texto en la carpeta indicada y devuelve la ruta del archivo."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre_archivo
    with open(ruta, "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(texto + "\n")
    return ruta


def guardar_radicado(texto, nombre_archivo):
    """Guarda el comprobante en data/radicados/ y devuelve la ruta del archivo."""
    return guardar_texto(config.CARPETA_RADICADOS, nombre_archivo, texto)


def exportar_csv(nombre_archivo, columnas, filas):
    """
    Exporta una lista de diccionarios a CSV (separado por comas) en
    data/exportaciones/. Se usa UTF-8 con BOM para que Excel y Power BI
    reconozcan las tildes.
    """
    config.CARPETA_EXPORTACIONES.mkdir(parents=True, exist_ok=True)
    ruta = config.CARPETA_EXPORTACIONES / nombre_archivo
    with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta
