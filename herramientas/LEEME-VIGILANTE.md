# Vigilante de mantenimiento

Cada día, a las 06:23 en Madrid, repasa todos los repos de NXplosion Labs y reescribe el issue
**«Mantenimiento de las apps»** en un repo privado. Corre en este repo porque es público: aquí
GitHub Actions no gasta minutos.

## Qué hace y qué no

| Hace | No hace |
|---|---|
| Borra los paquetes de Actions viejos de todos los repos (deja el último de cada tipo) | No compila, no sube versiones, no toca el código |
| Avisa si un workflow sigue fallando | No cambia ajustes de los repos |
| Cuenta los minutos del mes en los repos privados y el espacio de paquetes | No publica nada de los repos privados en este repo |
| Mira que la versión del código esté en `CAMBIOS.md` | |
| Mira el `targetSdk` de las apps de Play contra lo que exige Google | |
| Avisa de compilaciones con cada push y sin `timeout-minutes` | |
| Avisa 30 días antes de que caduque su token | |

En el issue, 🔴 es lo que hay que mirar, 🟡 avisos y 🟢 todo en orden. Cuando sale una alerta 🔴
nueva, la ejecución termina en rojo a propósito: así GitHub te manda el aviso por correo y al móvil.

## Puesta en marcha 👤

1. **Token.** github.com → foto → Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token.
   - Nombre: `vigilante-apps`. Caducidad: 1 año (el vigilante avisa 30 días antes).
   - Resource owner: la cuenta de NXplosion Labs. Repository access: **All repositories**.
   - Permisos de repositorio: **Actions: Read and write** · **Contents: Read-only** ·
     **Issues: Read and write** · **Pull requests: Read-only** (Metadata sale solo).
2. **Secretos.** En este repo: Settings → Secrets and variables → Actions → New repository secret.
   - `VIGILANTE_TOKEN`: el token del paso 1.
   - `REPO_INFORME`: el repo privado donde va el issue, como `Nxplosion-lab/Platinum-Hunter`.
3. **Primera vuelta.** Actions → «Vigilante de mantenimiento de las apps» → Run workflow.
   El issue aparece en el repo de `REPO_INFORME`.

Opcional: la variable `PLAY_TARGET_SDK` (Settings → Variables) cuando Google suba el mínimo.
Mientras no exista, se usa 36.

## Si algo no va

| Qué pasa | Por qué |
|---|---|
| «Faltan los secretos…» | No están `VIGILANTE_TOKEN` o `REPO_INFORME`, o tienen otro nombre |
| «No pudo terminar (HTTP 401)» | El token ha caducado o se ha borrado |
| «No pudo terminar (HTTP 403/404)» | Al token le falta un permiso o no tiene acceso a todos los repos |
| La ejecución sale en rojo pero el issue está bien | Es a propósito: hay alertas 🔴 nuevas |
| Un repo sale como «no se pudo revisar del todo» | Ese repo no deja leer algo; el resto se revisa igual |

## Pruebas

`python3 herramientas/probar_vigilante.py`, sin red y desde cualquier sitio. Se pasan también
antes de cada vuelta del vigilante.
