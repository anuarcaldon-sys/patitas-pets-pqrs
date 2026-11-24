"""
main.py
-------
Punto de entrada de PATITAS-PETS - Gestor de PQRS de MEPEGA.

Ejecución (desde la raíz del repositorio):
    python src/main.py

Flujo:
    1. Verifica la estructura de almacenamiento (carpeta data/).
    2. Pide el ingreso (login) obligatorio.
    3. Muestra el menú principal con la sesión activa.
"""

import sys

import config
import interfaz
import archivos
import autenticacion
import registro
import consultas
import cambios
import reportes


def mostrar_informe_limpieza():
    """Opción 4 > 5: muestra qué corrigió la limpieza al leer los cuatro archivos."""
    informe, total_lineas, validos = archivos.informe_limpieza()
    print("\n  LECTURA Y LIMPIEZA DE LOS ARCHIVOS DE PQRS")
    print("  " + "-" * 64)
    for tipo, cantidad in validos.items():
        print(f"  {config.TIPOS_SOLICITUD[tipo]['archivo'].name:<18} {cantidad:>7,} registros válidos".replace(",", "."))
    print(f"  {'Total unificado':<18} {sum(validos.values()):>7,} de {total_lineas:,} líneas leídas"
          .replace(",", "."))
    print("  " + "-" * 64)
    for tipo_correccion, cantidad in informe.items():
        print(f"  {tipo_correccion:<52} {cantidad:>6}")
    print("  " + "-" * 64)
    print("  Reglas: espacios, mayúsculas/minúsculas, catálogos sin tildes, campos vacíos y fechas.")


def menu_estadisticas(sesion):
    """Opción 4: estadísticas, exportaciones, gráficas y limpieza de datos."""
    while True:
        interfaz.mostrar_encabezado("4. ESTADÍSTICAS", sesion)
        print("      1. Ver estadísticas en pantalla")
        print("      2. Exportar reporte de estadísticas (TXT)")
        print("      3. Exportar base consolidada de PQRS (CSV)")
        print("      4. Generar gráficas estadísticas (PNG con matplotlib)")
        print("      5. Ver informe de lectura y limpieza de datos")
        print("      6. Volver al menú principal\n")
        opcion = interfaz.pedir_opcion("  Seleccione una opción (1-6): ", 1, 6)
        if opcion == 6:
            return

        print("\n  Calculando, por favor espere...")
        if opcion == 5:
            mostrar_informe_limpieza()
            interfaz.pausar()
            continue

        todas = archivos.leer_todas()
        if opcion == 3:
            ruta = reportes.exportar_base_consolidada(todas)
            print(f"  [OK] Base consolidada exportada ({len(todas)} filas): {ruta}")
        elif opcion == 4:
            import graficas          # se importa aquí: matplotlib solo se carga si se usa
            rutas = graficas.generar_graficas(todas)
            print(f"  [OK] {len(rutas)} gráficas guardadas en: {rutas[0].parent}")
            for ruta in rutas:
                print(f"       - {ruta.name}")
        else:
            texto = reportes.texto_reporte(reportes.calcular_estadisticas(todas), sesion["usuario"])
            if opcion == 1:
                print(texto)
            else:
                ruta = reportes.exportar_reporte_texto(texto)
                print(f"  [OK] Reporte exportado: {ruta}")
        interfaz.pausar()


def menu_principal(sesion):
    """Menú principal. Se repite hasta que el usuario elija Salir."""
    while True:
        interfaz.mostrar_encabezado(sesion=sesion)
        print("  Bienvenido a PATITAS-PETS - Gestión de PQRS\n")
        print("      1. Registrar PQRS")
        print("      2. Consultar PQRS")
        print("      3. Registrar Cambio en PQRS")
        print("      4. Estadísticas")
        print("      5. Salir\n")
        opcion = interfaz.pedir_opcion("  Seleccione una opción (1-5): ", 1, 5)

        try:
            if opcion == 1:
                registro.registrar_pqrs(sesion)
            elif opcion == 2:
                consultas.menu_consultas(sesion)
            elif opcion == 3:
                cambios.registrar_cambio(sesion)
            elif opcion == 4:
                menu_estadisticas(sesion)
            elif interfaz.confirmar("\n  ¿Desea cerrar la sesión y salir?"):
                print(f"\n  Sesión cerrada. Hasta pronto, {sesion['nombre']}.")
                return
        except PermissionError as error:
            # Ocurre si un archivo de data/ está abierto en otro programa (por ejemplo, Excel)
            print(f"\n  [!] No se pudo escribir en {error.filename}: el archivo está abierto "
                  "en otro programa. Ciérrelo e intente de nuevo.")
            interfaz.pausar()


def main():
    try:
        avisos = archivos.preparar_base_de_datos()
    except FileNotFoundError as error:
        print(f"[ERROR] {error}. Verifique la carpeta data/ del proyecto.")
        return
    for aviso in avisos:
        print(f"  [Aviso] {aviso}")

    sesion = autenticacion.iniciar_sesion()
    if sesion is None:
        print("\n  Ingreso cancelado. Hasta pronto.")
        return
    menu_principal(sesion)


if __name__ == "__main__":
    # Asegura que tildes, ñ y el banner se muestren bien en cualquier consola
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Programa finalizado por el usuario.")
