"""
interfaz.py
-----------
Funciones de apoyo para la consola: limpiar pantalla, mostrar el banner,
leer opciones numéricas, pedir confirmaciones, mostrar tablas por páginas
y leer la clave sin mostrarla.
"""

import os
import getpass

import config

BANNER = r"""
  ██████╗  █████╗ ████████╗██╗████████╗ █████╗ ███████╗      ██████╗ ███████╗████████╗███████╗
  ██╔══██╗██╔══██╗╚══██╔══╝██║╚══██╔══╝██╔══██╗██╔════╝      ██╔══██╗██╔════╝╚══██╔══╝██╔════╝
  ██████╔╝███████║   ██║   ██║   ██║   ███████║███████╗█████╗██████╔╝█████╗     ██║   ███████╗
  ██╔═══╝ ██╔══██║   ██║   ██║   ██║   ██╔══██║╚════██║╚════╝██╔═══╝ ██╔══╝     ██║   ╚════██║
  ██║     ██║  ██║   ██║   ██║   ██║   ██║  ██║███████║      ██║     ███████╗   ██║   ███████║
  ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝      ╚═╝     ╚══════╝   ╚═╝   ╚══════╝"""

LINEA = "  " + "=" * 92


def limpiar_pantalla():
    """Borra la consola (cls en Windows, clear en Linux/macOS)."""
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_encabezado(subtitulo="", sesion=None):
    """Limpia la pantalla y muestra el banner, la sesión activa y un subtítulo."""
    limpiar_pantalla()
    print(BANNER)
    print(f"       Gestor de PQRS - Movimiento Estudiantil de Perritos y Gaticos  v{config.VERSION}")
    print(LINEA)
    if sesion:
        print(f"  Sesión: {sesion['nombre']} ({sesion['usuario']}) - Rol: {sesion['rol']}")
        print(LINEA)
    if subtitulo:
        print(f"  {subtitulo}")
        print(LINEA)
    print()


def pedir_opcion(mensaje, minimo, maximo):
    """Pide un número entero entre minimo y maximo; insiste hasta que sea válido."""
    while True:
        texto = input(mensaje).strip()
        if texto.isdigit() and minimo <= int(texto) <= maximo:
            return int(texto)
        print(f"    [!] Opción no válida. Digite un número entre {minimo} y {maximo}.")


def pausar():
    """Detiene el programa hasta que el usuario presione Enter."""
    input("\n  Presione Enter para continuar...")


def confirmar(mensaje):
    """Pregunta S/N y devuelve True solo si el usuario responde S."""
    return input(f"{mensaje} (S/N): ").strip().upper() == "S"


def mostrar_tabla(encabezados, filas, anchos):
    """
    Imprime una tabla de texto por páginas de config.FILAS_POR_PAGINA filas.
    Los textos más largos que su columna se recortan con "~".
    Devuelve False si el usuario decidió salir antes de la última página.
    """
    separador = "  +" + "+".join("-" * (ancho + 2) for ancho in anchos) + "+"

    def formatear(valores):
        celdas = []
        for valor, ancho in zip(valores, anchos):
            texto = str(valor)
            if len(texto) > ancho:
                texto = texto[:ancho - 1] + "~"
            celdas.append(texto.ljust(ancho))
        return "  | " + " | ".join(celdas) + " |"

    total = len(filas)
    por_pagina = config.FILAS_POR_PAGINA
    for inicio in range(0, total, por_pagina):
        fin = min(inicio + por_pagina, total)
        print(separador)
        print(formatear(encabezados))
        print(separador)
        for fila in filas[inicio:fin]:
            print(formatear(fila))
        print(separador)
        print(f"  Registros {inicio + 1} a {fin} de {total}")
        if fin < total:
            respuesta = input("  Enter = siguiente página | S = terminar listado: ").strip().upper()
            if respuesta == "S":
                return False
    return True


def leer_clave(mensaje):
    """
    Lee la clave sin mostrarla en pantalla.
    En Windows muestra un * por cada carácter (como en la ilustración del
    enunciado). En otros sistemas, o si MOSTRAR_ASTERISCOS es False, usa
    getpass, que oculta la escritura por completo.
    """
    if not config.MOSTRAR_ASTERISCOS:
        return getpass.getpass(mensaje)
    try:
        import msvcrt  # módulo que solo existe en Windows
    except ImportError:
        return getpass.getpass(mensaje)

    print(mensaje, end="", flush=True)
    clave = ""
    while True:
        tecla = msvcrt.getwch()
        if tecla in ("\r", "\n"):            # Enter: termina la lectura
            print()
            return clave
        if tecla == "\x03":                  # Ctrl + C
            raise KeyboardInterrupt
        if tecla in ("\x00", "\xe0"):        # teclas especiales (flechas, F1...)
            msvcrt.getwch()                  # se descarta su segundo código
            continue
        if tecla == "\b":                    # Retroceso: borra el último *
            if clave:
                clave = clave[:-1]
                print("\b \b", end="", flush=True)
            continue
        clave += tecla
        print("*", end="", flush=True)
