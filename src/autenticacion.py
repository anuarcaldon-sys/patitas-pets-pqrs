"""
autenticacion.py
----------------
Módulo de control de acceso (Login) de PATITAS-PETS.

- Lee los usuarios autorizados desde data/Usuarios.txt.
- Permite ingresar con nombre de usuario o con correo institucional.
- Permite máximo 3 intentos fallidos; luego bloquea la pantalla por un
  tiempo definido en config.SEGUNDOS_BLOQUEO y lo muestra en pantalla.
- Al ingresar, crea la "sesión": un diccionario con los datos del usuario
  activo que se vincula automáticamente a cada PQRS registrada.
"""

import time
from datetime import datetime

import config
import interfaz


def cargar_usuarios():
    """Lee Usuarios.txt y devuelve una lista de diccionarios (uno por usuario)."""
    usuarios = []
    with open(config.ARCHIVO_USUARIOS, encoding="utf-8") as archivo:
        encabezado = archivo.readline().strip().split(config.SEPARADOR)
        for linea in archivo:
            linea = linea.strip()
            if linea:
                valores = linea.split(config.SEPARADOR)
                usuarios.append(dict(zip(encabezado, valores)))
    return usuarios


def usuarios_activos(usuarios):
    """Filtra la lista y deja solo los usuarios con estado Activo."""
    return [u for u in usuarios if u["estado"] == "Activo"]


def buscar_usuario(usuarios, identificador):
    """Busca por nombre de usuario o por correo (sin importar mayúsculas)."""
    identificador = identificador.strip().lower()
    for usuario in usuarios:
        if identificador in (usuario["usuario"].lower(),
                             usuario["correo_institucional"].lower()):
            return usuario
    return None


def validar_credenciales(usuarios, identificador, clave):
    """
    Revisa usuario/correo y clave.
    Devuelve (usuario, "") si son correctos o (None, mensaje) si fallan.
    El mensaje no dice cuál dato falló, para no dar pistas a un intruso.
    """
    usuario = buscar_usuario(usuarios, identificador)
    if usuario is None or usuario["contrasena"] != clave:
        return None, "Usuario o clave incorrectos."
    if usuario["estado"] != "Activo":
        return None, "El usuario está inactivo. Contacte al administrador."
    return usuario, ""


def crear_sesion(usuario):
    """Guarda los datos del usuario autenticado (sin la clave)."""
    return {
        "usuario": usuario["usuario"],
        "nombre": usuario["nombre_completo"],
        "correo": usuario["correo_institucional"],
        "rol": usuario["rol"],
        "inicio": datetime.now().strftime(config.FORMATO_FECHA),
    }


def bloquear_pantalla(segundos):
    """Bloquea el ingreso mostrando una cuenta regresiva en pantalla."""
    print()
    for restante in range(segundos, 0, -1):
        print(f"\r  Pantalla bloqueada por seguridad. "
              f"Podrá intentarlo de nuevo en {restante:2d} segundos. ",
              end="", flush=True)
        time.sleep(1)
    print("\r  Bloqueo finalizado. Puede intentarlo de nuevo." + " " * 30)
    time.sleep(1)


def iniciar_sesion():
    """
    Pantalla de ingreso. Es obligatoria antes del menú principal.
    Devuelve el diccionario de sesión, o None si el usuario cancela.
    """
    usuarios = cargar_usuarios()
    intentos_fallidos = 0

    while True:
        interfaz.mostrar_encabezado("Bienvenido a PATITAS-PETS - Gestión de PQRS")
        print("  Por favor ingrese sus credenciales\n")
        identificador = input("    1. Ingrese Usuario o correo : ").strip()
        clave = interfaz.leer_clave("    2. Ingrese Clave            : ")

        print("\n    [ 1 ] INGRESAR          [ 2 ] CANCELAR\n")
        if interfaz.pedir_opcion("  Seleccione una opción: ", 1, 2) == 2:
            return None

        usuario, mensaje = validar_credenciales(usuarios, identificador, clave)
        if usuario is not None:
            sesion = crear_sesion(usuario)
            print(f"\n  [OK] Bienvenido(a), {sesion['nombre']}.")
            time.sleep(1)
            return sesion

        intentos_fallidos += 1
        restantes = config.MAX_INTENTOS_LOGIN - intentos_fallidos
        if restantes > 0:
            print(f"\n  [!] {mensaje} Intentos restantes: {restantes}.")
            interfaz.pausar()
        else:
            print(f"\n  [!] {mensaje} Superó el máximo de "
                  f"{config.MAX_INTENTOS_LOGIN} intentos.")
            bloquear_pantalla(config.SEGUNDOS_BLOQUEO)
            intentos_fallidos = 0
