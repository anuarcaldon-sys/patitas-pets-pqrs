"""
graficas.py
-----------
Gráficas estadísticas de las PQRS, generadas con matplotlib a partir de los
datos limpios y unificados (reportes.tabla_pqrs: un DataFrame con las cuatro
bases y las columnas calculadas).

Opción 4 > 4 del programa. Guarda siete imágenes PNG en
data/exportaciones/graficas/:

    1_tipo_y_estado.png        PQRS por tipo y estado
    2_canal.png                canales de recepción
    3_mascota.png              tipo de mascota
    4_campus.png               campus de la UdeA
    5_cumplimiento_plazo.png   cumplimiento del plazo de respuesta
    6_usuario_registrador.png  gestión por usuario registrador
    7_radicacion_mensual.png   PQRS radicadas por mes

Colores: una sola tinta (verde UdeA) cuando hay una sola serie; tres tonos
validados para daltonismo en los estados; y colores de estado (rojo, ámbar,
verde) con su nombre escrito en el cumplimiento del plazo.
"""

from datetime import datetime

try:
    import matplotlib
    matplotlib.use("Agg")                    # dibuja en archivos, sin abrir ventanas
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
except ImportError:
    raise SystemExit("\n[ERROR] Falta la librería matplotlib.\n"
                     "        Instálela con:  pip install -r requirements.txt\n")

import config
import reportes

CARPETA_GRAFICAS = config.CARPETA_EXPORTACIONES / "graficas"

# Paleta
VERDE_UDEA = "#00985A"
ESTADOS_COLOR = {"Registrada": "#2a78d6", "En proceso": "#eb6834", "Solucionada": "#1baf7a"}
PLAZO_COLOR = {
    reportes.ETIQUETA_VENCIDA: "#d03b3b",
    reportes.ETIQUETA_PROXIMA: "#fab219",
    reportes.ETIQUETA_AL_DIA: "#0ca30c",
    reportes.ETIQUETA_SOLUCIONADA: "#8c8b86",
}
TEXTO = "#1f1f1e"
TEXTO_SECUNDARIO = "#52514e"
REJILLA = "#e4e3df"
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def miles(numero):
    """12000 -> '12.000' (separador de miles colombiano)."""
    return f"{int(numero):,}".replace(",", ".")


def etiqueta_valor(valor, total):
    """Texto al final de la barra: '1.948 · 16,2 %'."""
    porcentaje = f"{valor / total * 100:.1f}".replace(".", ",")
    return f" {miles(valor)} · {porcentaje} %"


def estilo_base():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.edgecolor": REJILLA,
        "axes.labelcolor": TEXTO_SECUNDARIO,
        "xtick.color": TEXTO_SECUNDARIO,
        "ytick.color": TEXTO,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def nueva_figura(titulo, subtitulo, alto=4.5):
    figura, eje = plt.subplots(figsize=(8, alto), dpi=200)
    figura.subplots_adjust(top=0.80)
    figura.text(0.02, 0.95, titulo, fontsize=15, fontweight="bold", color=TEXTO, va="top")
    figura.text(0.02, 0.885, subtitulo, fontsize=10.5, color=TEXTO_SECUNDARIO, va="top")
    eje.grid(axis="x", color=REJILLA, linewidth=0.8)
    eje.set_axisbelow(True)
    eje.xaxis.set_major_formatter(FuncFormatter(lambda valor, _: miles(valor)))
    return figura, eje


def guardar(figura, nombre, fuente):
    figura.text(0.02, 0.015, fuente, fontsize=8, color=TEXTO_SECUNDARIO)
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_GRAFICAS / nombre
    figura.savefig(ruta, facecolor="white")
    plt.close(figura)
    return ruta


def barras_horizontales(serie, titulo, subtitulo, nombre, fuente, color=VERDE_UDEA, alto=4.5):
    """Barras horizontales ordenadas de mayor a menor, con el valor y el % al final."""
    serie = serie.sort_values()
    total = serie.sum()
    figura, eje = nueva_figura(titulo, subtitulo, alto)
    barras = eje.barh(serie.index, serie.values, color=color, height=0.62)
    for barra, valor in zip(barras, serie.values):
        eje.text(barra.get_width() + total * 0.004, barra.get_y() + barra.get_height() / 2,
                 etiqueta_valor(valor, total), va="center", fontsize=9.5, color=TEXTO)
    eje.set_xlim(0, serie.max() * 1.28)
    eje.tick_params(axis="y", length=0)
    figura.subplots_adjust(left=0.30, right=0.97, bottom=0.12)
    return guardar(figura, nombre, fuente)


def generar_graficas(registros, ahora=None):
    """Genera las siete gráficas y devuelve la lista de rutas creadas."""
    estilo_base()
    ahora = ahora or datetime.now()
    df = reportes.tabla_pqrs(registros, ahora)
    total = len(df)
    fuente = (f"Fuente: PATITAS-PETS v{config.VERSION} · {miles(total)} PQRS limpias y unificadas "
              f"de Peticion, Queja, Reclamo y Sugerencia.txt · {ahora:%Y-%m-%d %H:%M}")
    rutas = []

    # 1. Tipo y estado (barras apiladas)
    tabla = df.groupby(["tipo_nombre", "estado_peticion"]).size().unstack(fill_value=0)
    tabla = tabla.reindex(index=[d["nombre"] for d in config.TIPOS_SOLICITUD.values()][::-1],
                          columns=config.ESTADOS, fill_value=0)
    figura, eje = nueva_figura("PQRS por tipo y estado",
                               f"{miles(total)} PQRS · cada barra suma el total de su tipo")
    izquierda = [0] * len(tabla)
    for estado in config.ESTADOS:
        valores = tabla[estado].values
        barras = eje.barh(tabla.index, valores, left=izquierda, color=ESTADOS_COLOR[estado],
                          height=0.62, label=estado, edgecolor="white", linewidth=1.5)
        for barra, valor in zip(barras, valores):
            if valor:
                eje.text(barra.get_x() + barra.get_width() / 2, barra.get_y() + barra.get_height() / 2,
                         miles(valor), ha="center", va="center", fontsize=9.5, color="white",
                         fontweight="bold")
        izquierda = [a + b for a, b in zip(izquierda, valores)]
    eje.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, 1.13), frameon=False, fontsize=10)
    eje.tick_params(axis="y", length=0)
    figura.subplots_adjust(left=0.16, right=0.97, bottom=0.12, top=0.76)
    rutas.append(guardar(figura, "1_tipo_y_estado.png", fuente))

    # 2. Canal de recepción
    rutas.append(barras_horizontales(
        df["canal_recepcion"].value_counts(), "Canales de recepción",
        "PQRS recibidas por cada canal", "2_canal.png", fuente))

    # 3. Tipo de mascota
    rutas.append(barras_horizontales(
        df["tipo_mascota"].value_counts(), "Tipo de mascota",
        "PQRS según la mascota relacionada", "3_mascota.png", fuente, alto=3.6))

    # 4. Campus (nombres cortos)
    campus = df["campus_relacionado"].str.replace("Campus Medellín - ", "", regex=False) \
                                     .str.replace("Campus en el ", "", regex=False).value_counts()
    rutas.append(barras_horizontales(
        campus, "PQRS por campus de la UdeA", "Sedes de Medellín y Área de la salud",
        "4_campus.png", fuente, alto=5))

    # 5. Cumplimiento del plazo
    orden = [reportes.ETIQUETA_SOLUCIONADA, reportes.ETIQUETA_VENCIDA,
             reportes.ETIQUETA_PROXIMA, reportes.ETIQUETA_AL_DIA]
    plazo = df["estado_plazo"].value_counts().reindex(orden, fill_value=0)
    figura, eje = nueva_figura("Cumplimiento del plazo de respuesta",
                               f"Estado del plazo al {ahora:%d/%m/%Y} · las activas vencen a los "
                               f"30 días (bases) o {config.PLAZO_RESPUESTA_DIAS} días (nuevas)")
    etiquetas = plazo.index[::-1]
    valores = plazo.values[::-1]
    barras = eje.barh(etiquetas, valores, color=[PLAZO_COLOR[e] for e in etiquetas], height=0.62)
    for barra, valor in zip(barras, valores):
        eje.text(barra.get_width() + total * 0.004, barra.get_y() + barra.get_height() / 2,
                 etiqueta_valor(valor, total), va="center", fontsize=9.5, color=TEXTO)
    eje.set_xlim(0, max(valores) * 1.28)
    eje.tick_params(axis="y", length=0)
    figura.subplots_adjust(left=0.30, right=0.97, bottom=0.12)
    rutas.append(guardar(figura, "5_cumplimiento_plazo.png", fuente))

    # 6. Usuario registrador
    rutas.append(barras_horizontales(
        df["usuario_registro"].value_counts(), "Gestión por usuario registrador",
        "PQRS registradas por cada usuario del sistema", "6_usuario_registrador.png",
        fuente, alto=5.2))

    # 7. Radicación mensual (columnas)
    por_mes = df.groupby(df["radicacion_dt"].dt.to_period("M")).size()
    figura, eje = nueva_figura("PQRS radicadas por mes", f"Año {ahora:%Y} · {miles(total)} PQRS")
    eje.grid(axis="x", visible=False)
    eje.grid(axis="y", color=REJILLA, linewidth=0.8)
    eje.yaxis.set_major_formatter(FuncFormatter(lambda valor, _: miles(valor)))
    posiciones = list(range(len(por_mes)))
    barras = eje.bar(posiciones, por_mes.values, color=VERDE_UDEA, width=0.62)
    eje.set_xticks(posiciones, [MESES[periodo.month - 1] for periodo in por_mes.index])
    for barra, valor in zip(barras, por_mes.values):
        eje.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), miles(valor),
                 ha="center", va="bottom", fontsize=9, color=TEXTO)
    eje.tick_params(axis="x", length=0)
    eje.set_ylim(0, por_mes.max() * 1.15)
    figura.subplots_adjust(left=0.09, right=0.98, bottom=0.12)
    rutas.append(guardar(figura, "7_radicacion_mensual.png", fuente))

    return rutas
