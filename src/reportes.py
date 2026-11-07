"""
reportes.py
-----------
Cálculo de estadísticas de las PQRS y preparación de los archivos que se
exportan (reporte en texto y base consolidada para Power BI).

Estadística obligatoria:
    0. Promedio de días de respuesta (valor entero).

Estadísticas adicionales exigidas por el enunciado:
    1. Distribución por tipo de mascota.
    2. Proporción por canal de recepción.
    3. Distribución por campus.
    4. Efectividad y resolución por estado.
    5. Alerta de vencimiento y control de plazo.
    6. Perfil del solicitante y carga operativa (por rol y por usuario registrador).

Complementarias: cantidad por tipo de PQRS y por tipo de documento del solicitante.

¿Cómo se obtiene el perfil del solicitante (estadística 6)?
    Las bases de MEPEGA no tienen un campo de perfil, así que se DERIVA:
      - documento NIT                        -> Organización (NIT)
      - correo con dominio @udea.edu.co      -> Comunidad UdeA
      - cualquier otro caso                  -> Ciudadano externo
    Con los datos actuales no se puede distinguir entre estudiante, docente y
    administrativo; esa división queda pendiente de un campo nuevo aprobado por
    el Product Owner.

¿Cómo se calcula el promedio de días de respuesta?
    Días de respuesta de una PQRS = fecha en que pasó a Solucionada
                                    - fecha de radicación.
    La fecha de solución se toma de Historial.txt, que PATITAS-PETS llena cada
    vez que se registra un cambio de estado. Las PQRS de la base histórica
    que ya venían solucionadas no tienen fecha de solución, por eso no
    entran en el promedio; el reporte informa cuántas quedan por fuera.
"""

from collections import Counter
from datetime import datetime, timedelta

import config
import archivos
import autenticacion
from radicado import numero_radicado

ETIQUETA_SOLUCIONADA = "Solucionada"
ETIQUETA_VENCIDA = "Vencida"
ETIQUETA_PROXIMA = "Próxima a vencer"
ETIQUETA_AL_DIA = "Al día"


# ---------------------------------------------------------------------------
# Funciones de apoyo
# ---------------------------------------------------------------------------
def a_fecha(texto):
    """Convierte 'AAAA-MM-DD HH:MM:SS' a datetime."""
    return datetime.strptime(texto, config.FORMATO_FECHA)


def formato_numero(numero):
    """12000 -> '12.000' (separador de miles colombiano)."""
    return f"{numero:,}".replace(",", ".")


def porcentaje(parte, total):
    """Porcentaje con un decimal; 0 si el total es 0."""
    return round(parte * 100 / total, 1) if total else 0.0


def formato_porcentaje(valor):
    """33.5 -> '33,5 %'."""
    return f"{valor:.1f} %".replace(".", ",")


def es_activa(registro):
    return registro["estado_peticion"] in config.ESTADOS_ACTIVOS


def fechas_de_solucion():
    """Diccionario {(tipo, id): fecha en que la PQRS pasó a Solucionada}."""
    return {
        (m["tipo_solicitud"], m["id"]): a_fecha(m["fecha_cambio"])
        for m in archivos.leer_historial()
        if m["estado_nuevo"] == "Solucionada"
    }


def dias_de_respuesta(registro, soluciones):
    """Días entre radicación y solución, o None si no hay fecha de solución."""
    fecha_solucion = soluciones.get((registro["tipo_solicitud"], registro["id"]))
    if registro["estado_peticion"] != "Solucionada" or fecha_solucion is None:
        return None
    return (fecha_solucion - a_fecha(registro["fecha_radicacion"])).days


def perfil_solicitante(registro):
    """Perfil derivado del solicitante (ver la explicación al inicio del módulo)."""
    if registro["tipo_documento"] == "NIT":
        return config.PERFIL_ORGANIZACION
    dominio = registro["correo_electronico"].rsplit("@", 1)[-1].lower()
    if dominio == config.DOMINIO_INSTITUCIONAL:
        return config.PERFIL_COMUNIDAD_UDEA
    return config.PERFIL_EXTERNO


def dias_para_vencer(registro, ahora):
    """Días calendario que faltan para la fecha máxima (negativo si ya venció)."""
    return (a_fecha(registro["fecha_maxima_respuesta"]).date() - ahora.date()).days


def clasificar_plazo(registro, ahora):
    """Solucionada, Vencida, Próxima a vencer (menos de N días) o Al día."""
    if not es_activa(registro):
        return ETIQUETA_SOLUCIONADA
    restante = a_fecha(registro["fecha_maxima_respuesta"]) - ahora
    if restante < timedelta(0):
        return ETIQUETA_VENCIDA
    if restante < timedelta(days=config.DIAS_ALERTA_VENCIMIENTO):
        return ETIQUETA_PROXIMA
    return ETIQUETA_AL_DIA


def conteo(registros, obtener_valor, orden=None):
    """
    Cuenta cuántos registros hay por cada valor.
    Devuelve una lista de tuplas (valor, cantidad, porcentaje).
    orden: lista opcional con el orden en que se deben mostrar los valores.
    """
    contador = Counter(obtener_valor(r) for r in registros)
    total = len(registros)
    valores = orden if orden else [valor for valor, _ in contador.most_common()]
    return [(valor, contador[valor], porcentaje(contador[valor], total)) for valor in valores]


# ---------------------------------------------------------------------------
# Listados usados por las consultas
# ---------------------------------------------------------------------------
def registros_activos(registros):
    return [r for r in registros if es_activa(r)]


def mas_antiguas(registros, cantidad=10):
    """PQRS activas ordenadas de la más antigua a la más reciente."""
    activas = registros_activos(registros)
    activas.sort(key=lambda r: r["fecha_radicacion"])   # el formato ISO se ordena como texto
    return activas[:cantidad]


def por_clasificacion_de_plazo(registros, etiqueta, ahora):
    """PQRS activas con la etiqueta de plazo indicada, ordenadas por fecha máxima."""
    filtradas = [r for r in registros if clasificar_plazo(r, ahora) == etiqueta]
    filtradas.sort(key=lambda r: r["fecha_maxima_respuesta"])
    return filtradas


# ---------------------------------------------------------------------------
# Cálculo de todas las estadísticas
# ---------------------------------------------------------------------------
def calcular_estadisticas(registros, ahora=None):
    """Calcula todas las estadísticas y las devuelve en un diccionario."""
    ahora = ahora or datetime.now()
    total = len(registros)
    soluciones = fechas_de_solucion()
    activas = registros_activos(registros)
    roles = {u["usuario"]: u["rol"] for u in autenticacion.cargar_usuarios()}

    # 0. Estadística obligatoria: promedio de días de respuesta
    dias = [d for d in (dias_de_respuesta(r, soluciones) for r in registros) if d is not None]
    solucionadas = [r for r in registros if r["estado_peticion"] == "Solucionada"]
    plazos = [(a_fecha(r["fecha_maxima_respuesta"]) - a_fecha(r["fecha_radicacion"])).days
              for r in registros]
    antiguedades = [(ahora - a_fecha(r["fecha_radicacion"])).days for r in activas]

    return {
        "ahora": ahora,
        "total": total,
        "promedio_respuesta": round(sum(dias) / len(dias)) if dias else None,
        "muestras_respuesta": len(dias),
        "solucionadas_sin_fecha": len(solucionadas) - len(dias),
        "plazo_promedio": round(sum(plazos) / len(plazos)) if plazos else 0,
        "antiguedad_activas": round(sum(antiguedades) / len(antiguedades)) if antiguedades else 0,
        "por_tipo": conteo(registros,
                           lambda r: config.TIPOS_SOLICITUD[r["tipo_solicitud"]]["nombre"]),
        "por_tipo_documento": conteo(
            registros, lambda r: f"{r['tipo_documento']} - {config.TIPOS_DOCUMENTO.get(r['tipo_documento'], 'Otro')}",
            [f"{codigo} - {nombre}" for codigo, nombre in config.TIPOS_DOCUMENTO.items()]),
        "por_mascota": conteo(registros, lambda r: r["tipo_mascota"], config.TIPOS_MASCOTA),
        "por_canal": conteo(registros, lambda r: r["canal_recepcion"]),
        "por_campus": conteo(registros, lambda r: r["campus_relacionado"]),
        "por_estado": conteo(registros, lambda r: r["estado_peticion"], config.ESTADOS),
        "tasa_resolucion": porcentaje(len(solucionadas), total),
        "por_plazo_activas": conteo(activas, lambda r: clasificar_plazo(r, ahora),
                                    [ETIQUETA_VENCIDA, ETIQUETA_PROXIMA, ETIQUETA_AL_DIA]),
        "total_activas": len(activas),
        "por_perfil": conteo(registros, perfil_solicitante, config.PERFILES),
        "por_rol": conteo(registros, lambda r: roles.get(r["usuario_registro"], "Sin rol")),
        "por_usuario": conteo(registros, lambda r: r["usuario_registro"]),
    }


# ---------------------------------------------------------------------------
# Reporte en texto (pantalla y archivo)
# ---------------------------------------------------------------------------
def barra(cantidad, maximo, ancho=30):
    """Barra de texto proporcional al valor más alto: ##########"""
    return "#" * round(cantidad * ancho / maximo) if maximo else ""


def bloque_distribucion(titulo, filas, ancho_etiqueta=44):
    """Sección del reporte con una fila por valor: etiqueta, cantidad, % y barra."""
    lineas = ["", f" {titulo}", " " + "-" * 98]
    maximo = max((cantidad for _, cantidad, _ in filas), default=0)
    for valor, cantidad, pct in filas:
        lineas.append(f"   {valor:<{ancho_etiqueta}} {formato_numero(cantidad):>7} "
                      f"{formato_porcentaje(pct):>8}  {barra(cantidad, maximo)}")
    return lineas


def texto_reporte(e, usuario=""):
    """Arma el reporte completo en texto a partir del diccionario de estadísticas."""
    lineas = [
        "=" * 100,
        " PATITAS-PETS - REPORTE DE ESTADÍSTICAS DE PQRS (MEPEGA)".ljust(100),
        f" Generado: {e['ahora'].strftime(config.FORMATO_FECHA)}"
        f"   Usuario: {usuario or 'N/A'}   Total de PQRS: {formato_numero(e['total'])}",
        "=" * 100,
        "",
        " 0. ESTADÍSTICA OBLIGATORIA - PROMEDIO DE DÍAS DE RESPUESTA",
        " " + "-" * 98,
    ]
    if e["promedio_respuesta"] is None:
        lineas.append("   Promedio de días de respuesta ..........: sin datos "
                      "(aún no hay soluciones en Historial.txt)")
    else:
        lineas.append(f"   Promedio de días de respuesta ..........: {e['promedio_respuesta']} días "
                      f"(muestra: {formato_numero(e['muestras_respuesta'])} PQRS con fecha de solución)")
    lineas += [
        f"   Solucionadas sin fecha de solución .....: {formato_numero(e['solucionadas_sin_fecha'])}"
        " (base histórica; no entran en el promedio)",
        f"   Referencia: plazo promedio otorgado ....: {e['plazo_promedio']} días",
        f"   Referencia: antigüedad promedio activas : {e['antiguedad_activas']} días",
    ]
    lineas += bloque_distribucion("CANTIDAD POR TIPO DE PQRS (complementaria)", e["por_tipo"])
    lineas += bloque_distribucion("CANTIDAD POR TIPO DE DOCUMENTO DEL SOLICITANTE (complementaria)",
                                  e["por_tipo_documento"])
    lineas += bloque_distribucion("1. DISTRIBUCIÓN POR TIPO DE MASCOTA", e["por_mascota"])
    lineas += bloque_distribucion("2. PROPORCIÓN POR CANAL DE RECEPCIÓN", e["por_canal"])
    lineas += bloque_distribucion("3. DISTRIBUCIÓN POR CAMPUS", e["por_campus"])
    lineas += bloque_distribucion("4. EFECTIVIDAD Y RESOLUCIÓN POR ESTADO", e["por_estado"])
    lineas.append(f"   Tasa de resolución: {formato_porcentaje(e['tasa_resolucion'])}"
                  f" de las PQRS están Solucionadas.")
    lineas += bloque_distribucion(
        f"5. ALERTA DE VENCIMIENTO (sobre {formato_numero(e['total_activas'])} PQRS activas; "
        f"próxima a vencer = menos de {config.DIAS_ALERTA_VENCIMIENTO} días)",
        e["por_plazo_activas"])
    lineas += bloque_distribucion("6a. PERFIL DEL SOLICITANTE (derivado: NIT, correo @udea.edu.co u otro)",
                                  e["por_perfil"])
    lineas += bloque_distribucion("6b. CARGA OPERATIVA POR ROL DEL REGISTRADOR", e["por_rol"])
    lineas += bloque_distribucion("6c. CARGA OPERATIVA POR USUARIO REGISTRADOR", e["por_usuario"])
    lineas += ["", "=" * 100]
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Base consolidada para Power BI
# ---------------------------------------------------------------------------
COLUMNAS_POWER_BI = [
    "radicado", "tipo_solicitud", "id", "tipo_documento", "perfil_solicitante", "fecha_radicacion",
    "canal_recepcion", "asunto_titulo", "tipo_mascota", "campus_relacionado",
    "fecha_maxima_respuesta", "estado_peticion", "usuario_registro",
    "nombre_registrador", "rol_registrador", "fecha_solucion", "dias_respuesta",
    "antiguedad_dias", "dias_para_vencer", "estado_plazo",
]


def base_consolidada(registros, ahora=None):
    """
    Une las cuatro bases en una sola tabla con columnas calculadas.
    Por protección de datos personales (Ley 1581 de 2012) NO se exportan
    nombre, número de documento, teléfono, correo, dirección ni descripción;
    del correo solo se exporta el perfil derivado.
    """
    ahora = ahora or datetime.now()
    soluciones = fechas_de_solucion()
    usuarios = {u["usuario"]: u for u in autenticacion.cargar_usuarios()}
    filas = []
    for r in registros:
        usuario = usuarios.get(r["usuario_registro"], {})
        fecha_solucion = soluciones.get((r["tipo_solicitud"], r["id"]))
        dias = dias_de_respuesta(r, soluciones)
        filas.append({
            "radicado": numero_radicado(r),
            "tipo_solicitud": config.TIPOS_SOLICITUD[r["tipo_solicitud"]]["nombre"],
            "id": r["id"],
            "tipo_documento": r["tipo_documento"],
            "perfil_solicitante": perfil_solicitante(r),
            "fecha_radicacion": r["fecha_radicacion"],
            "canal_recepcion": r["canal_recepcion"],
            "asunto_titulo": r["asunto_titulo"],
            "tipo_mascota": r["tipo_mascota"],
            "campus_relacionado": r["campus_relacionado"],
            "fecha_maxima_respuesta": r["fecha_maxima_respuesta"],
            "estado_peticion": r["estado_peticion"],
            "usuario_registro": r["usuario_registro"],
            "nombre_registrador": usuario.get("nombre_completo", ""),
            "rol_registrador": usuario.get("rol", ""),
            "fecha_solucion": fecha_solucion.strftime(config.FORMATO_FECHA) if fecha_solucion else "",
            "dias_respuesta": "" if dias is None else dias,
            "antiguedad_dias": (ahora - a_fecha(r["fecha_radicacion"])).days,
            "dias_para_vencer": dias_para_vencer(r, ahora) if es_activa(r) else "",
            "estado_plazo": clasificar_plazo(r, ahora),
        })
    return filas


def exportar_reporte_texto(texto):
    """Guarda el reporte en data/exportaciones/ con fecha y hora en el nombre."""
    nombre = f"reporte_estadisticas_{datetime.now():%Y%m%d_%H%M%S}.txt"
    return archivos.guardar_texto(config.CARPETA_EXPORTACIONES, nombre, texto)


def exportar_base_power_bi(registros):
    """Guarda la base consolidada en data/exportaciones/base_consolidada_pqrs.csv."""
    return archivos.exportar_csv("base_consolidada_pqrs.csv", COLUMNAS_POWER_BI,
                                 base_consolidada(registros))
