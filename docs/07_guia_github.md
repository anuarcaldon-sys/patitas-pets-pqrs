# Guía de GitHub — PATITAS-PETS

**Responsable:** Anuar Ferney Caldón Quira, líder del proyecto

El enunciado exige que el líder cree una cuenta de GitHub **exclusivamente con las credenciales de la UdeA**, cargue el proyecto y vincule a sus compañeros en un repositorio compartido. Esta guía describe cómo hacerlo y cómo verificar que el repositorio cumple las reglas de la entrega. Complementa lo que se explique en clase.

---

## 1. Crear la cuenta del líder

1. Entre a [github.com](https://github.com) y elija **Sign up**.
2. Use **su correo institucional `@udea.edu.co`**. No use correos personales.
3. Elija un nombre de usuario fácil de identificar (por ejemplo, `nombreapellido-udea`) y una contraseña segura.
4. Verifique el correo con el código que envía GitHub.
5. Si GitHub le pide activar la verificación en dos pasos (2FA), hágalo con una aplicación autenticadora en el celular y guarde los códigos de recuperación.

Santiago y Sandra también necesitan una cuenta de GitHub para ser vinculados; se recomienda que usen igualmente su correo institucional.

## 2. Crear el repositorio

1. En GitHub, haga clic en **+** (esquina superior derecha) → **New repository**.
2. Diligencie:

| Campo | Valor recomendado |
|---|---|
| Repository name | `patitas-pets-pqrs` |
| Description | Gestor de PQRS de MEPEGA · Algoritmia y Programación 2026-2 · UdeA |
| Visibilidad | **Public**, para que el docente pueda revisarlo. Si lo crean **Private**, deben agregar al docente como colaborador. |
| Add a README file | **No marcar** (el proyecto ya trae su README.md) |
| Add .gitignore / Choose a license | **None** (el proyecto ya trae `.gitignore` y `LICENSE.md`) |

3. Clic en **Create repository**.

## 3. Cargar el proyecto

Descomprima el archivo del proyecto. Lo que se carga es **el contenido** de la carpeta `patitas/`, de forma que en la raíz del repositorio queden `README.md`, `LICENSE.md`, `src/`, `docs/`, `images/` y `data/`.

### Opción A — Desde el navegador (sin instalar nada)

1. En la página del repositorio vacío, haga clic en el enlace **uploading an existing file**.
2. Abra la carpeta `patitas/` en su computador, seleccione **todo su contenido** y arrástrelo a la página.
   - En Windows, active **Vista → Mostrar → Elementos ocultos** para ver y seleccionar `.gitignore` y `.gitattributes`.
   - GitHub no sube carpetas vacías; por eso `data/radicados/` y `data/exportaciones/` traen un archivo `.gitkeep`.
   - El navegador admite archivos de hasta 25 MB; el archivo más grande del proyecto pesa cerca de 1,2 MB.
3. En **Commit changes**, escriba un mensaje como `v2.0.0 - Versión completa de PATITAS-PETS` y confirme.

### Opción B — Con Git desde la terminal (recomendada)

Instale [Git](https://git-scm.com/downloads) y, una sola vez, configure su identidad:

```bash
git config --global user.name "Nombre Apellido"
git config --global user.email "usuario@udea.edu.co"
```

Luego, dentro de la carpeta `patitas/`:

```bash
git init
git add .
git commit -m "v2.0.0 - Versión completa de PATITAS-PETS"
git branch -M main
git remote add origin https://github.com/anuarcaldon-sys/patitas-pets-pqrs.git
git push -u origin main
```

En el primer `push`, Git abre el navegador para autorizar el acceso a su cuenta (en Windows lo hace el *Git Credential Manager* que se instala con Git).

## 4. Vincular a los compañeros

1. En el repositorio: **Settings → Collaborators** (sección *Access*) → **Add people**.
2. Escriba el nombre de usuario o el correo de cada integrante y envíe la invitación.
3. Cada integrante acepta la invitación desde su correo o desde [github.com/notifications](https://github.com/notifications).
4. Si el repositorio es privado, repita el proceso con el usuario del docente.

Verifique que todos los integrantes aparezcan en la lista de colaboradores antes de la fecha de entrega.

## 5. Trabajo en equipo

Cada integrante trabaja en su propia rama y el líder integra los cambios en `main`:

```bash
git clone https://github.com/anuarcaldon-sys/patitas-pets-pqrs.git   # una sola vez
cd patitas-pets-pqrs
git switch -c nombre/tarea          # crear una rama para la tarea
# ... editar archivos ...
git add .
git commit -m "Descripción corta del cambio"
git push -u origin nombre/tarea
```

Después, en GitHub, se abre un **Pull request** de la rama hacia `main`. El líder lo revisa (y el equipo lo comenta) antes de fusionarlo con **Merge pull request**. Para traer los cambios de los demás: `git switch main` y `git pull`.

**Reglas del equipo**

- Mensajes de *commit* claros y en español: qué se cambió y por qué.
- Nadie fusiona en `main` código que no haya explicado al equipo.
- Nunca se suben contraseñas reales. `data/Usuarios.txt` contiene credenciales ficticias entregadas por el docente con fines académicos; en un sistema real las claves no se guardan en texto plano.
- Antes de cada entrega se ejecutan `python src/validaciones.py` y una prueba completa del programa.

## 6. Versiones

Cada versión del [plan de versionado](04_plan_versionado.md) se marca con una etiqueta:

```bash
git tag -a v2.0.0 -m "Entrega del programa completo"
git push origin v2.0.0
```

Para las versiones principales (`v1.0.0` y `v2.0.0`) cree además un *Release*: pestaña **Releases → Draft a new release**, elija la etiqueta y copie el resumen de cambios del plan de versionado.

## 7. Lista de verificación antes de entregar

| Regla del enunciado | Dónde se cumple | ✔ |
|---|---|---|
| README.md con integrantes y descripción en Markdown | `README.md`, secciones 1 y 2 | ☐ |
| Nombre del proyecto e imagen representativa | `README.md` sección 3 e `images/logo_patitas_pets.png` | ☐ |
| Licencia del software | `LICENSE.md` y `README.md` sección 4 | ☐ |
| Reporte de visión, requisitos y plan de proyecto | `docs/01`, `docs/02`, `docs/03` | ☐ |
| Plan de versionado | `docs/04_plan_versionado.md` | ☐ |
| Todo el código en la carpeta **`src`** (su ausencia resta un punto) | `src/` | ☐ |
| Manual de usuario en la carpeta **`docs`** (su ausencia resta un punto) | `docs/06_manual_usuario.md` | ☐ |
| Imágenes y elementos gráficos en **`images`** | `images/` | ☐ |
| Archivos planos del programa en **`data`** | `data/Peticion.txt`, `Queja.txt`, `Reclamo.txt`, `Sugerencia.txt` | ☐ |
| Actas firmadas | `docs/actas/` | ☐ |
| Todos los integrantes vinculados como colaboradores | Settings → Collaborators | ☐ |
| El programa se ejecuta desde una copia recién descargada | `python src/main.py` | ☐ |
| Actas con fechas, documentos y firmas completos | `docs/actas/` | ☐ |

**Prueba final:** abra el enlace del repositorio en una ventana de incógnito para confirmar que se ve completo, descárguelo con **Code → Download ZIP** en otra carpeta y ejecute el programa desde esa copia.

## 8. Comandos de referencia

| Comando | Para qué sirve |
|---|---|
| `git status` | Ver qué archivos cambiaron |
| `git add .` | Preparar todos los cambios |
| `git commit -m "mensaje"` | Guardar los cambios preparados con un mensaje |
| `git push` | Subir los cambios a GitHub |
| `git pull` | Traer los cambios de los compañeros |
| `git switch -c rama` | Crear una rama y cambiarse a ella |
| `git log --oneline` | Ver el historial de *commits* |
| `git tag -a v1.0.0 -m "..."` | Marcar una versión |
