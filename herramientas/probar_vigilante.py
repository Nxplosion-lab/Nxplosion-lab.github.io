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

total = ok + len(fallos)
print(f"Pruebas del vigilante: {ok} de {total} pasan.")
for f in fallos:
    print(f"  FALLA: {f}")
sys.exit(1 if fallos else 0)
