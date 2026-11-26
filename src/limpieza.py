"""
limpieza.py
-----------
Limpieza y estandarización de las PQRS que se leen de los archivos planos.

archivos.leer_registros() aplica limpiar_registro() a cada línea de
Peticion.txt, Queja.txt, Reclamo.txt y Sugerencia.txt antes de que la usen
las consultas, los cambios de estado, las estadísticas o las gráficas.

Reglas, en este orden:
    1. Espacios: quita los espacios del inicio y del final y deja uno solo
       entre palabras.
    2. Mayúsculas y minúsculas: el correo va en minúsculas y el tipo de
       documento en mayúsculas. Los campos de catálogo (tipo de solicitud,
       teléfono, canal, mascota, campus y estado) se comparan sin importar
       mayúsculas ni tildes y se reescriben con el valor oficial de config.py
       ("gato" -> "Gato", "pagina web" -> "Página web").
    3. Campos vacíos: la dirección vacía queda como "N/A"; si falta un campo
       obligatorio, el registro se omite y se informa.
    4. Fechas: deben tener el formato AAAA-MM-DD HH:MM:SS. Si llegan en otro
       formato conocido (por ejemplo 28/09/2026 17:44) se convierten; si no se
       pueden leer, el registro se omite y se informa.

Prueba rápida de las reglas:
    python src/limpieza.py
"""

import unicodedata
from datetime import datetime

import config

# Formatos de fecha alternos que se aceptan y se convierten al oficial
FORMATOS_ALTERNOS = [
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%Y/%m/%d %H:%M:%S",
]

CAMPOS_FECHA = ["fecha_radicacion", "fecha_maxima_respuesta"]
CAMPOS_OPCIONALES = ["direccion"]
VALOR_SIN_DIRECCION = "N/A"

# Nombres de las correcciones que se cuentan en el informe de limpieza
ESPACIOS = "Espacios sobrantes corregidos"
MAYUSCULAS = "Mayúsculas/minúsculas estandarizadas"
CATALOGOS = "Valores de catálogo estandarizados"
DIRECCION_VACIA = "Direcciones vacías completadas con N/A"
FECHAS = "Fechas convertidas al formato oficial"
OMITIDO_VACIO = "Registros omitidos por campo obligatorio vacío"
OMITIDO_FECHA = "Registros omitidos por fecha ilegible"
OMITIDO_CAMPOS = "Líneas omitidas por número de campos incorrecto"
TIPOS_DE_CORRECCION = [ESPACIOS, MAYUSCULAS, CATALOGOS, DIRECCION_VACIA, FECHAS,
                       OMITIDO_VACIO, OMITIDO_FECHA, OMITIDO_CAMPOS]


def clave_comparacion(texto):
    """Texto en minúsculas y sin tildes, para comparar valores de catálogo."""
    sin_tildes = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(letra for letra in sin_tildes if not unicodedata.combining(letra))
    return sin_tildes.lower()


def _catalogo(valores):
    """Diccionario {clave de comparación: valor oficial}."""
    return {clave_comparacion(valor): valor for valor in valores}


CATALOGOS_POR_CAMPO = {
    "tipo_solicitud": _catalogo(config.TIPOS_SOLICITUD),
    "tipo_telefono": _catalogo(config.TIPOS_TELEFONO),
    "canal_recepcion": _catalogo(config.CANALES_RECEPCION),
    "tipo_mascota": _catalogo(config.TIPOS_MASCOTA),
    "campus_relacionado": _catalogo(config.CAMPUS),
    "estado_peticion": _catalogo(config.ESTADOS),
}


def informe_vacio():
    """Contadores en cero para todas las correcciones."""
    return {tipo: 0 for tipo in TIPOS_DE_CORRECCION}


def normalizar_fecha(texto):
    """
    Devuelve una tupla (fecha_en_formato_oficial, fue_convertida).
    Si la fecha no se puede leer devuelve (None, False).
    """
    try:
        datetime.strptime(texto, config.FORMATO_FECHA)
        return texto, False
    except ValueError:
        pass
    for formato in FORMATOS_ALTERNOS:
        try:
            fecha = datetime.strptime(texto, formato)
            return fecha.strftime(config.FORMATO_FECHA), True
        except ValueError:
            continue
    return None, False


def limpiar_registro(registro, informe=None):
    """
    Limpia un registro (diccionario de 18 campos) y devuelve una tupla
    (registro_limpio, motivo_de_omision). Si el registro es válido, el
    motivo es None. Cada corrección suma 1 en el diccionario informe.
    """
    informe = informe if informe is not None else informe_vacio()
    limpio = {}

    # 1. Espacios
    for campo, valor in registro.items():
        texto = " ".join(str(valor).split())
        if texto != valor:
            informe[ESPACIOS] += 1
        limpio[campo] = texto

    # 2. Mayúsculas y minúsculas
    for campo, metodo in (("correo_electronico", str.lower), ("tipo_documento", str.upper)):
        nuevo = metodo(limpio[campo])
        if nuevo != limpio[campo]:
            informe[MAYUSCULAS] += 1
            limpio[campo] = nuevo
    for campo, catalogo in CATALOGOS_POR_CAMPO.items():
        oficial = catalogo.get(clave_comparacion(limpio[campo]))
        if oficial and oficial != limpio[campo]:
            informe[CATALOGOS] += 1
            limpio[campo] = oficial

    # 3. Campos vacíos
    if not limpio["direccion"]:
        limpio["direccion"] = VALOR_SIN_DIRECCION
        informe[DIRECCION_VACIA] += 1
    vacios = [c for c in config.CAMPOS if c not in CAMPOS_OPCIONALES and not limpio[c]]
    if vacios:
        informe[OMITIDO_VACIO] += 1
        return limpio, f"campo obligatorio vacío: {', '.join(vacios)}"

    # 4. Fechas
    for campo in CAMPOS_FECHA:
        fecha, convertida = normalizar_fecha(limpio[campo])
        if fecha is None:
            informe[OMITIDO_FECHA] += 1
            return limpio, f"fecha ilegible en {campo}: '{limpio[campo]}'"
        if convertida:
            informe[FECHAS] += 1
            limpio[campo] = fecha

    return limpio, None


# ---------------------------------------------------------------------------
# Prueba rápida:  python src/limpieza.py
# ---------------------------------------------------------------------------
def _probar():
    base = {campo: "x" for campo in config.CAMPOS}
    base.update({
        "id": "7", "nombre_completo": "  Ana   María  Ruiz ", "tipo_documento": "cc",
        "correo_electronico": "Ana.Ruiz@UdeA.edu.co", "direccion": "",
        "tipo_solicitud": "queja", "tipo_telefono": "celular", "canal_recepcion": "pagina web",
        "tipo_mascota": "GATO", "campus_relacionado": "campus medellin - ciudad universitaria",
        "estado_peticion": "en proceso", "fecha_radicacion": "28/09/2026 17:44",
        "fecha_maxima_respuesta": "2026-10-13 17:44:00",
    })
    informe = informe_vacio()
    limpio, motivo = limpiar_registro(base, informe)
    casos = [
        ("espacios", limpio["nombre_completo"] == "Ana María Ruiz"),
        ("correo en minúsculas", limpio["correo_electronico"] == "ana.ruiz@udea.edu.co"),
        ("documento en mayúsculas", limpio["tipo_documento"] == "CC"),
        ("catálogo sin tildes", limpio["canal_recepcion"] == "Página web"),
        ("catálogo de campus", limpio["campus_relacionado"] == config.CAMPUS[0]),
        ("estado", limpio["estado_peticion"] == "En proceso"),
        ("dirección vacía -> N/A", limpio["direccion"] == "N/A"),
        ("fecha convertida", limpio["fecha_radicacion"] == "2026-09-28 17:44:00"),
        ("registro válido", motivo is None),
    ]
    _, motivo_fecha = limpiar_registro({**base, "fecha_radicacion": "ayer"}, informe)
    casos.append(("fecha ilegible se omite", motivo_fecha is not None))
    _, motivo_vacio = limpiar_registro({**base, "asunto_titulo": "   "}, informe)
    casos.append(("obligatorio vacío se omite", motivo_vacio is not None))

    correctas = 0
    for nombre, resultado in casos:
        correctas += resultado
        print(f"  [{'OK' if resultado else 'FALLA'}] {nombre}")
    print(f"\n  {correctas} de {len(casos)} pruebas de limpieza correctas.")
    return correctas == len(casos)


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if _probar() else 1)
