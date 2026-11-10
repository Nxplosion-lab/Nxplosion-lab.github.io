#!/usr/bin/env python3
"""
Pruebas del vigilante, sin red. Se lanza sin argumentos desde cualquier sitio:
    python3 herramientas/probar_vigilante.py
Los casos salen de los repos reales tal como estaban el 03-11-2026.
"""
import datetime as dt, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import vigilante as v

ok, fallos = 0, []


def comprobar(nombre, cond):
    global ok
    if cond:
        ok += 1
    else:
        fallos.append(nombre)


AHORA = dt.datetime(2026, 11, 3, 6, 0, tzinfo=dt.timezone.utc)

# --- Versión contra CAMBIOS.md (encabezados reales) ---
comprobar("PH 2.5.35 apuntada", v.version_en_cambios("2.5.35", "## `PH 2.5.35 · b96 · (en casa)`\n"))
comprobar("RDR 4.59.0 apuntada", v.version_en_cambios("4.59.0", "## `RDR 4.59.0` — sin compilar\n"))
comprobar("MC 0.8.1 apuntada", v.version_en_cambios("0.8.1", "## MC 0.8.1 · b10 · 058f3c2\n"))
comprobar("AEB 4.51.0 NO apuntada (CAMBIOS llega a la 4.48.0)",
          not v.version_en_cambios("4.51.0", "## 4.48.0 — 28 de septiembre de 2026\n## 4.47.0 — 28 de septiembre de 2026\n"))
comprobar("4.5.1 no se confunde con 4.51.0", not v.version_en_cambios("4.5.1", "## 4.51.0\n"))
comprobar("solo cuentan los encabezados ##", not v.version_en_cambios("2.5.35", "texto que cita 2.5.35\n## PH 2.5.34\n"))

# --- De dónde sale la versión ---
comprobar("VERSION «PH 2.5.35» → 2.5.35", v.version_del_codigo("PH 2.5.35\n", []) == "2.5.35")
comprobar("APP_VERSION de Auditoría EB → 4.51.0", v.version_del_codigo(None, ['x = 1\nAPP_VERSION = "4.51.0"\n']) == "4.51.0")
comprobar("sin versión → None", v.version_del_codigo(None, ["nada"]) is None)

# --- targetSdk ---
comprobar("kts: targetSdk = 36", v.target_sdk("        targetSdk = 36\n") == 36)
comprobar("groovy: targetSdk 34", v.target_sdk("        targetSdk 34\n") == 34)
comprobar("antiguo: targetSdkVersion 33", v.target_sdk("targetSdkVersion 33") == 33)

# --- Workflows ---
RDR_ANTES = "name: Compilar el APK\n\non:\n  workflow_dispatch:\n  push:\n    branches: [main, master]\n\njobs:\n  apk:\n    steps:\n      - run: ./gradlew assembleDebug\n"
RDR_AHORA = "name: Compilar el APK\n\non:\n  workflow_dispatch:\n\njobs:\n  apk:\n    steps:\n      - run: ./gradlew assembleDebug\n"
PH_BUILD = "on:\n  workflow_dispatch:\n\njobs:\n  b:\n    steps:\n      - run: ./gradlew bundleRelease\n"
CON_TOPE = PH_BUILD.replace("  b:\n", "  b:\n    timeout-minutes: 45\n")
SERVIDOR = "on:\n  push:\n    branches: [main]\n    paths:\n      - \"server/**\"\njobs:\n  d:\n    steps:\n      - run: firebase deploy\n"
comprobar("RDR antes: compila con cada push", "compila con cada push" in v.revisar_workflow(RDR_ANTES, True))
comprobar("RDR ahora: ya no compila con push", "compila con cada push" not in v.revisar_workflow(RDR_AHORA, True))
comprobar("PH build: sin tope de tiempo", any("timeout" in a for a in v.revisar_workflow(PH_BUILD, True)))
comprobar("con timeout-minutes no avisa", v.revisar_workflow(CON_TOPE, True) == [])
comprobar("servidor en push no compila → sin aviso", v.revisar_workflow(SERVIDOR, True) == [])
REVISION = "on:\n  workflow_call:\njobs:\n  l:\n    steps:\n      - uses: gradle/actions/setup-gradle@v4\n        with:\n          gradle-version: 8.11.1\n      - run: gradle lintDebug --stacktrace\n"
SOLO_SETUP = "on:\n  workflow_dispatch:\njobs:\n  x:\n    steps:\n      - uses: gradle/actions/setup-gradle@v4\n        with:\n          gradle-version: 8.11.1\n"
comprobar("«gradle lintDebug» cuenta como compilar", any("timeout" in a for a in v.revisar_workflow(REVISION, True)))
comprobar("«gradle-version» y «gradle/actions» no cuentan", v.revisar_workflow(SOLO_SETUP, True) == [])
comprobar("repo público con push no avisa del push", "compila con cada push" not in v.revisar_workflow(RDR_ANTES, False))

# --- Limpieza de paquetes ---
def paq(n, nombre, horas):
    return {"id": n, "name": nombre, "size_in_bytes": 30_000_000,
            "created_at": (AHORA - dt.timedelta(hours=horas)).isoformat().replace("+00:00", "Z")}

P = [paq(1, "PH-2.5.35-b96-cd58c39 - Platinum Hunter COMPLETA", 5),
     paq(2, "PH-2.5.34-b95-aaaaaaa - Platinum Hunter COMPLETA", 30),
     paq(3, "PH-Gratis-2.5.35-b96-cd58c39 - PH GRATIS", 5),
     paq(4, "Capturas-22-idiomas", 60),
     paq(5, "RadarMovil-36", 100)]
b = {p["id"] for p in v.paquetes_a_borrar(P, AHORA)}
comprobar("mismo tipo: se borra el más viejo", 2 in b)
comprobar("se queda el último de PH COMPLETA", 1 not in b)
comprobar("PH GRATIS es otro tipo y se queda", 3 not in b)
comprobar("capturas de más de 2 días se borran", 4 in b)
comprobar("el único paquete de más de 3 días se borra", 5 in b)
comprobar("tipo sin versión ni número", v.tipo_de_paquete("RadarMovil-36") == "RadarMovil")

# --- Minutos: cada trabajo se redondea hacia arriba ---
T = [{"started_at": "2026-11-02T10:00:00Z", "completed_at": "2026-11-02T10:00:20Z"},   # 20 s → 1 min
     {"started_at": "2026-11-02T10:00:00Z", "completed_at": "2026-11-02T10:07:01Z"},   # 7 min 1 s → 8
     {"started_at": "2026-11-02T10:00:00Z", "completed_at": None}]                     # sin acabar → 0
comprobar("minutos: 1 + 8 = 9", v.minutos_facturados(T) == 9)

# --- Informe ---
res = {"filas": [{"repo": "App", "privado": True, "minutos": 1600, "mb": 120.0, "dependabot": 0, "version": "1.0.0", "sdk": 36}],
       "alertas": [], "avisos": [], "total_min": 1600, "total_mb": 120.0, "borrados_n": 2, "borrados_mb": 60.0}
cuerpo, alertas = v.componer(res, AHORA, "2026-11-20 10:00:00 UTC")
comprobar("1.600 de 2.000 min (80 %) da alerta", any("Minutos" in a for a in alertas))
comprobar("token que caduca en 17 días da alerta", any("caduca" in a for a in alertas))
comprobar("decimales con coma", "120,0 MB" in cuerpo)
res["total_min"] = 400
_, alertas2 = v.componer(res, AHORA, "2027-11-01 10:00:00 UTC")
comprobar("400 min y token lejano: sin alertas", alertas2 == [])
comprobar("la huella no depende del orden", v.huella(["a", "b"]) == v.huella(["b", "a"]))

# --- Trozo del error (registros con la forma real de Actions) ---
GRADLE = ("2026-11-09T13:22:27.1234567Z ##[group]Run ./gradlew assembleRelease\n"
          "2026-11-09T13:22:27.1234567Z Starting a Gradle Daemon\n"
          "2026-11-09T13:24:01.0000000Z \x1b[31mFAILURE: Build failed with an exception.\x1b[0m\n"
          "2026-11-09T13:24:01.0000000Z * What went wrong:\n"
          "2026-11-09T13:24:01.0000000Z Execution failed for task ':app:compileReleaseKotlin'.\n"
          "2026-11-09T13:24:01.0000000Z * Try:\n"
          "2026-11-09T13:24:01.0000000Z BUILD FAILED in 1m 34s\n"
          "2026-11-09T13:24:02.0000000Z ##[error]Process completed with exit code 1.\n"
          "2026-11-09T13:24:03.0000000Z Post job cleanup.\n")
KOTLIN = GRADLE.replace("Starting a Gradle Daemon\n", "Starting a Gradle Daemon\n2026-11-09T13:23:50.0000000Z e: file:///app/Receta.kt:12:5 Unresolved reference 'salsa'.\n")
tk = v.trozo_del_error(KOTLIN)
comprobar("Kotlin: trae la línea «e:» con fichero y línea", "e: file:///app/Receta.kt:12:5 Unresolved reference 'salsa'." in tk)
comprobar("Kotlin: sigue empezando por la causa", tk[0] == "* What went wrong:")
tg = v.trozo_del_error(GRADLE)
comprobar("Gradle: empieza por «What went wrong»", tg[:1] == ["* What went wrong:"])
comprobar("Gradle: trae la tarea que falla", "Execution failed for task ':app:compileReleaseKotlin'." in tg)
comprobar("sin horas ni colores", not any("2026-11-09T" in l or "\x1b" in l for l in tg))
comprobar("sin «* Try:»", "* Try:" not in tg)
LARGO = KOTLIN.replace("* Try:\n", "* Try:\n" + "".join(f"2026-11-09T13:24:01.0000000Z > consejo {i}\n" for i in range(40)))
comprobar("Kotlin: la línea «e:» no se pierde tras los consejos de Gradle",
          any(l.startswith("e: ") for l in v.trozo_del_error(LARGO)) and not any("consejo" in l for l in v.trozo_del_error(LARGO)))
OTRO = "\n".join([f"2026-11-09T10:00:{i:02d}Z línea {i}" for i in range(50)] +
                 ["2026-11-09T10:01:00Z ##[error]Falta el fichero recetas.json", "2026-11-09T10:01:01Z Post job cleanup."])
to = v.trozo_del_error(OTRO, max_lineas=10)
comprobar("sin Gradle: acaba en el ##[error]", to[-1] == "##[error]Falta el fichero recetas.json")
comprobar("sin Gradle: 10 líneas, no la limpieza de después", len(to) == 10 and "Post job cleanup." not in to)
comprobar("«```» no rompe el bloque", v.trozo_del_error("##[error]mal ```x```") == ["##[error]mal ´´´x´´´"])
comprobar("líneas larguísimas se cortan", len(v.trozo_del_error("x" * 500)[0]) == 161)
comprobar("registro vacío no rompe", v.trozo_del_error("") == [] and v.trozo_del_error(None) == [])


# --- Detalle del fallo, con un GitHub de mentira (sin red) ---
class GhFalso:
    def __init__(self, trabajos, registro=None, falla_registro=False):
        self.t, self.r, self.f = trabajos, registro, falla_registro
    def todas(self, ruta, clave=None, tope=1000):
        return self.t
    def registro(self, repo, id_trabajo):
        if self.f:
            raise v.ErrorApi("HTTP 410")
        return self.r

EJ = {"id": 7, "created_at": "2026-11-09T13:22:27Z"}
TR = [{"id": 1, "name": "apk", "conclusion": "failure",
       "steps": [{"name": "Checkout", "conclusion": "success"}, {"name": "Compilar", "conclusion": "failure"}]},
      {"id": 2, "name": "lint", "conclusion": "success", "steps": []}]
d = v.detalle_del_fallo(GhFalso(TR, GRADLE), "X/Cookline", "Cookline", "Compilar Cookline", EJ)
comprobar("detalle: solo el trabajo que falla", [t["nombre"] for t in d["trabajos"]] == ["apk"])
comprobar("detalle: el paso que falla", d["trabajos"][0]["paso"] == "Compilar")
comprobar("detalle: con su fecha", d["fecha"] == "2026-11-09")
d2 = v.detalle_del_fallo(GhFalso(TR, falla_registro=True), "X/C", "C", "W", EJ)
comprobar("registro caducado: se dice y no rompe", "no se pudo leer el registro" in d2["trabajos"][0]["trozo"][0])
d3 = v.detalle_del_fallo(GhFalso([]), "X/C", "C", "W", EJ)
comprobar("sin trabajos fallidos: nota", d3["nota"] is not None and d3["trabajos"] == [])

# --- La redirección del registro se sigue SIN el token ---
import urllib.request as _ur, urllib.error as _ue, email.message as _em
vistas = []
class _Resp:
    def __init__(self, t): self.t = t
    def read(self): return self.t.encode()
    def __enter__(self): return self
    def __exit__(self, *a): return False
class _Abridor:
    def open(self, req, timeout=None):
        vistas.append(("api", req.get_header("Authorization")))
        h = _em.Message(); h["Location"] = "https://blob.example/registro?firma=1"
        raise _ue.HTTPError(req.full_url, 302, "Found", h, None)
_bo, _uo = _ur.build_opener, _ur.urlopen
_ur.build_opener = lambda *a: _Abridor()
def _abrir(req, timeout=None):
    vistas.append(("blob", req.get_header("Authorization")))
    return _Resp("hola")
_ur.urlopen = _abrir
try:
    texto = v.GitHub("TOKEN").registro("X/C", 1)
finally:
    _ur.build_opener, _ur.urlopen = _bo, _uo
comprobar("registro: sigue la redirección", texto == "hola")
comprobar("registro: la API lleva el token", vistas[0] == ("api", "Bearer TOKEN"))
comprobar("registro: el enlace temporal va sin token", vistas[1] == ("blob", None))

# --- Informe con fallos y propuestas ---
res3 = dict(res, total_min=241,
            detalles=[d, d3],
            propuestas=[{"repo": "Moodcell", "numero": 2, "titulo": "Actualizar librerías", "dias": 12},
                        {"repo": "Cookline", "numero": 4, "titulo": "Bump x", "dias": 3}])
c3, a3 = v.componer(res3, AHORA, "2027-11-01 10:00:00 UTC")
comprobar("informe: sección de fallos", "## Detalle de los fallos" in c3 and "falla en el paso «Compilar»" in c3)
comprobar("informe: el trozo va en un bloque plegado", "<details>" in c3 and "```text" in c3)
comprobar("informe: propuestas ordenadas por repo", c3.index("**Cookline** #4") < c3.index("**Moodcell** #2"))
comprobar("informe: antigüedad de la propuesta", "hace 12 días" in c3)
comprobar("informe: los detalles no crean alertas", a3 == [])
comprobar("informe: el pie sigue al final", c3.rstrip().endswith("No se compila ni se sube nada desde aquí._"))
comprobar("sin detalles ni propuestas: igual que antes", "## Detalle" not in cuerpo and "## Propuestas" not in cuerpo)
gordo = {"repo": "C", "workflow": "W", "fecha": "2026-11-09", "nota": None,
         "trabajos": [{"nombre": "apk", "paso": "x", "tiempo": False, "trozo": ["y" * 160] * 30}]}
c4, _ = v.componer(dict(res3, detalles=[gordo] * 40), AHORA, None)
comprobar("informe enorme: cabe en el issue", len(c4) <= v.TOPE_ISSUE)
comprobar("informe enorme: el resumen sigue entero", "## Repos" in c4 and "Minutos de Actions este mes" in c4)
comprobar("informe enorme: los bloques quedan cerrados", c4.count("```text") * 2 == c4.count("```"))

total = ok + len(fallos)
print(f"Pruebas del vigilante: {ok} de {total} pasan.")
for f in fallos:
    print(f"  FALLA: {f}")
sys.exit(1 if fallos else 0)
