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

¿Qué hace Pandas y qué hace NumPy aquí?
    - Las PQRS de los cuatro archivos se cargan en un DataFrame de Pandas
      (una tabla con una fila por PQRS y una columna por campo).
    - Cada estadística se obtiene de una columna (una Series) con value_counts().
    - NumPy calcula los promedios (np.mean, np.round) y clasifica cada PQRS en
      una sola operación sobre toda la columna (np.select, np.where).
    Las funciones que trabajan con UNA sola PQRS (es_activa, dias_para_vencer,
    clasificar_plazo...) siguen en Python puro porque las usa consultas.py.

Instalación de las librerías:  pip install -r requirements.txt
"""

from datetime import datetime, timedelta

try:
    import numpy as np
    import pandas as pd
except ImportError:                      # mensaje claro si faltan las librerías
    raise SystemExit("\n[ERROR] Faltan las librerías NumPy y Pandas.\n"
                     "        Instálelas con:  pip install -r requirements.txt\n")

import config
import archivos
import autenticacion

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


def conteo(serie, orden=None):
    """
    Cuenta cuántas PQRS hay por cada valor de una columna (Series de Pandas).
    Devuelve una lista de tuplas (valor, cantidad, porcentaje).
    orden: lista opcional con el orden en que se deben mostrar los valores;
    sin orden, se muestran de mayor a menor cantidad.
    """
    cantidades = serie.value_counts()                      # Series: valor -> cantidad
    if orden:
        cantidades = cantidades.reindex(orden, fill_value=0)
    total = len(serie)
    return [(valor, int(cantidad), porcentaje(int(cantidad), total))
            for valor, cantidad in cantidades.items()]


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
# Tabla de PQRS con Pandas
# ---------------------------------------------------------------------------
def tabla_pqrs(registros, ahora=None):
    """
    Convierte la lista de PQRS en un DataFrame y le agrega las columnas
    calculadas que usan las estadísticas y la base para Power BI.
    """
    ahora = pd.Timestamp(ahora or datetime.now())
    df = pd.DataFrame(registros, columns=config.CAMPOS)

    # Fechas de texto a datetime de Pandas (una sola operación por columna)
    df["radicacion_dt"] = pd.to_datetime(df["fecha_radicacion"], format=config.FORMATO_FECHA)
    df["maxima_dt"] = pd.to_datetime(df["fecha_maxima_respuesta"], format=config.FORMATO_FECHA)

    # Nombres legibles del tipo de PQRS y del tipo de documento
    df["tipo_nombre"] = df["tipo_solicitud"].map(
        {clave: datos["nombre"] for clave, datos in config.TIPOS_SOLICITUD.items()})
    df["documento_nombre"] = df["tipo_documento"] + " - " + \
        df["tipo_documento"].map(config.TIPOS_DOCUMENTO).fillna("Otro")

    # Perfil derivado (estadística 6) con np.select: la primera condición que se cumple gana
    dominio = df["correo_electronico"].str.rsplit("@", n=1).str[-1].str.lower()
    df["perfil_solicitante"] = np.select(
        [df["tipo_documento"] == "NIT", dominio == config.DOMINIO_INSTITUCIONAL],
        [config.PERFIL_ORGANIZACION, config.PERFIL_COMUNIDAD_UDEA],
        default=config.PERFIL_EXTERNO)

    # Nombre y rol del usuario registrador
    usuarios = pd.DataFrame(autenticacion.cargar_usuarios()).set_index("usuario")
    df["nombre_registrador"] = df["usuario_registro"].map(usuarios["nombre_completo"]).fillna("")
    df["rol_registrador"] = df["usuario_registro"].map(usuarios["rol"]).fillna("Sin rol")

    # Fecha de solución (de Historial.txt) y días de respuesta
    soluciones = fechas_de_solucion()
    claves = list(zip(df["tipo_solicitud"], df["id"]))     # tuplas (tipo, id)
    df["solucion_dt"] = pd.to_datetime(pd.Series([soluciones.get(c) for c in claves], index=df.index))
    df.loc[df["estado_peticion"] != "Solucionada", "solucion_dt"] = pd.NaT
    df["dias_respuesta"] = (df["solucion_dt"] - df["radicacion_dt"]).dt.days.astype("Int64")

    # Plazos
    df["activa"] = df["estado_peticion"].isin(config.ESTADOS_ACTIVOS)
    df["plazo_otorgado"] = (df["maxima_dt"] - df["radicacion_dt"]).dt.days
    df["antiguedad_dias"] = (ahora - df["radicacion_dt"]).dt.days
    dias_vencer = (df["maxima_dt"].dt.normalize() - ahora.normalize()).dt.days
    df["dias_para_vencer"] = dias_vencer.where(df["activa"]).astype("Int64")
    restante = df["maxima_dt"] - ahora
    df["estado_plazo"] = np.select(
        [~df["activa"], restante < pd.Timedelta(0),
         restante < pd.Timedelta(days=config.DIAS_ALERTA_VENCIMIENTO)],
        [ETIQUETA_SOLUCIONADA, ETIQUETA_VENCIDA, ETIQUETA_PROXIMA],
        default=ETIQUETA_AL_DIA)
    return df


def promedio_entero(serie):
    """Promedio redondeado a entero con NumPy; None si la Series está vacía."""
    valores = serie.dropna().to_numpy(dtype=float)
    return int(np.round(np.mean(valores))) if valores.size else None


# ---------------------------------------------------------------------------
# Cálculo de todas las estadísticas
# ---------------------------------------------------------------------------
def calcular_estadisticas(registros, ahora=None):
    """Calcula todas las estadísticas y las devuelve en un diccionario."""
    ahora = ahora or datetime.now()
    df = tabla_pqrs(registros, ahora)
    activas = df[df["activa"]]                              # filtro booleano del DataFrame
    solucionadas = int((df["estado_peticion"] == "Solucionada").sum())
    muestras = int(df["dias_respuesta"].notna().sum())

    return {
        "ahora": ahora,
        "total": len(df),
        # 0. Estadística obligatoria: promedio de días de respuesta
        "promedio_respuesta": promedio_entero(df["dias_respuesta"]),
        "muestras_respuesta": muestras,
        "solucionadas_sin_fecha": solucionadas - muestras,
        "plazo_promedio": promedio_entero(df["plazo_otorgado"]) or 0,
        "antiguedad_activas": promedio_entero(activas["antiguedad_dias"]) or 0,
        # Complementarias
        "por_tipo": conteo(df["tipo_nombre"],
                           [datos["nombre"] for datos in config.TIPOS_SOLICITUD.values()]),
        "por_tipo_documento": conteo(df["documento_nombre"],
                                     [f"{codigo} - {nombre}" for codigo, nombre in config.TIPOS_DOCUMENTO.items()]),
        # 1 a 3. Demanda del servicio
        "por_mascota": conteo(df["tipo_mascota"], config.TIPOS_MASCOTA),
        "por_canal": conteo(df["canal_recepcion"]),
        "por_campus": conteo(df["campus_relacionado"]),
        # 4. Efectividad y resolución
        "por_estado": conteo(df["estado_peticion"], config.ESTADOS),
        "tasa_resolucion": porcentaje(solucionadas, len(df)),
        # 5. Vencimiento
        "por_plazo_activas": conteo(activas["estado_plazo"],
                                    [ETIQUETA_VENCIDA, ETIQUETA_PROXIMA, ETIQUETA_AL_DIA]),
        "total_activas": len(activas),
        # 6. Perfil y carga operativa
        "por_perfil": conteo(df["perfil_solicitante"], config.PERFILES),
        "por_rol": conteo(df["rol_registrador"]),
        "por_usuario": conteo(df["usuario_registro"]),
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
    Une las cuatro bases en un solo DataFrame con columnas calculadas.
    Por protección de datos personales (Ley 1581 de 2012) NO se exportan
    nombre, número de documento, teléfono, correo, dirección ni descripción;
    del correo solo se exporta el perfil derivado.
    """
    df = tabla_pqrs(registros, ahora)
    prefijos = {clave: datos["prefijo"] for clave, datos in config.TIPOS_SOLICITUD.items()}
    df["radicado"] = df["tipo_solicitud"].map(prefijos) + "-" + df["id"].str.zfill(6)
    df["tipo_solicitud"] = df["tipo_nombre"]
    df["fecha_solucion"] = df["solucion_dt"].dt.strftime(config.FORMATO_FECHA).fillna("")
    return df[COLUMNAS_POWER_BI]


def exportar_reporte_texto(texto):
    """Guarda el reporte en data/exportaciones/ con fecha y hora en el nombre."""
    nombre = f"reporte_estadisticas_{datetime.now():%Y%m%d_%H%M%S}.txt"
    return archivos.guardar_texto(config.CARPETA_EXPORTACIONES, nombre, texto)


def exportar_base_power_bi(registros):
    """Guarda la base consolidada en data/exportaciones/base_consolidada_pqrs.csv."""
    config.CARPETA_EXPORTACIONES.mkdir(parents=True, exist_ok=True)
    ruta = config.CARPETA_EXPORTACIONES / "base_consolidada_pqrs.csv"
    # UTF-8 con BOM para que Excel y Power BI reconozcan las tildes
    base_consolidada(registros).to_csv(ruta, index=False, encoding="utf-8-sig", lineterminator="\n")
    return ruta
