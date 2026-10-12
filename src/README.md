# src — Código fuente de PATITAS-PETS

Programa de consola en Python 3.10+ (solo biblioteca estándar). Se ejecuta desde la raíz del repositorio:

```bash
python src/main.py          # inicia el programa
python src/validaciones.py  # ejecuta las pruebas de las reglas de validación
```

| Archivo | Contenido |
|---|---|
| `main.py` | Punto de entrada, menú principal y menú de estadísticas |
| `config.py` | Rutas, catálogos y reglas de negocio (plazo, intentos, bloqueo, alertas) |
| `interfaz.py` | Banner, pantallas, tablas paginadas y lectura de la clave |
| `autenticacion.py` | Ingreso, intentos, bloqueo y sesión |
| `validaciones.py` | Reglas de validación de cada campo y del flujo de estados |
| `registro.py` | Opción 1: registrar PQRS |
| `consultas.py` | Opción 2: consultar PQRS |
| `cambios.py` | Opción 3: registrar cambio de estado |
| `reportes.py` | Opción 4: estadísticas y exportación para Power BI |
| `archivos.py` | Lectura y escritura de los archivos planos de `data/` |
| `radicado.py` | Comprobante de 120 columnas |

La explicación detallada de los algoritmos está en [docs/05_algoritmo.md](../docs/05_algoritmo.md).
