#!/usr/bin/env python3
"""
Vigilante de mantenimiento de las apps de NXplosion Labs.

Corre cada día en GitHub Actions dentro de este repo, que es público y por eso no gasta minutos.
Repasa todos los repos de la cuenta y deja el informe en un issue de un repo PRIVADO.

Por qué está aquí y no en cada repo: los repos privados comparten 2.000 min/mes y cada
ejecución se cobra como mínimo 1 min. Aquí sale gratis.

Lo que hace:
  - Limpia los paquetes de Actions viejos de todos los repos (deja el último de cada tipo).
  - Avisa de compilaciones que han fallado en la última semana.
  - Calcula los minutos gastados este mes en los repos privados y avisa al acercarse al tope.
  - Mira el espacio de paquetes (tope de 0,5 GB para toda la cuenta).
  - Cuenta las propuestas de Dependabot abiertas.
  - Comprueba que la versión del código (VERSION o APP_VERSION) esté apuntada en CAMBIOS.md.
  - En las apps de Play, comprueba el targetSdk contra el que exige Google.
  - Avisa de workflows que compilan con cada push en un repo privado o que no tienen tope de tiempo.
  - Avisa antes de que caduque el token.

IMPORTANTE: el registro de las ejecuciones de este repo es PÚBLICO. Por eso aquí no se imprime
nada de los repos privados (ni nombres, ni números, ni errores con su URL). Todo va al issue.

Secretos del repo (Settings → Secrets and variables → Actions):
  VIGILANTE_TOKEN   token de GitHub de grano fino (ver LEEME-VIGILANTE.md)
  REPO_INFORME      repo privado donde va el issue, como «Dueño/Repo»
Variable opcional:
  PLAY_TARGET_SDK   el targetSdk que exige Google Play (por defecto 36)
"""
import base64, datetime as dt, hashlib, json, math, os, re, sys, urllib.error, urllib.parse, urllib.request

API = "https://api.github.com"
TITULO_ISSUE = "Mantenimiento de las apps"
TOPE_MIN_MES = 2000          # minutos gratis al mes en los repos privados
TOPE_PAQUETES_MB = 500       # 0,5 GB de paquetes de Actions para toda la cuenta
DIAS_SEMANA = 7


class ErrorApi(Exception):
    """Error de la API sin la URL dentro, para que nunca acabe en el registro público."""


class GitHub:
    def __init__(self, token):
        self.token = token
        self.caduca = None   # fecha de caducidad del token, si GitHub la dice
        self.llamadas = 0

    def pedir(self, metodo, ruta, cuerpo=None, entero=False):
        url = ruta if ruta.startswith("http") else API + ruta
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        req = urllib.request.Request(url, data=datos, method=metodo, headers={
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "NXplosion-Labs-vigilante",
        })
        self.llamadas += 1
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                cad = r.headers.get("github-authentication-token-expiration")
                if cad:
                    self.caduca = cad
                txt = r.read().decode() or "null"
                return (json.loads(txt), r.headers) if entero else json.loads(txt)
        except urllib.error.HTTPError as e:
            raise ErrorApi(f"HTTP {e.code}") from None
        except Exception as e:
            raise ErrorApi(type(e).__name__) from None

    def get(self, ruta):
        return self.pedir("GET", ruta)

    def todas(self, ruta, clave=None, tope=1000):
        """Recorre las páginas de un listado. `clave` es el campo donde viene la lista, si no es la raíz."""
        sep = "&" if "?" in ruta else "?"
        url, filas = f"{ruta}{sep}per_page=100", []
        while url and len(filas) < tope:
            datos, cab = self.pedir("GET", url, entero=True)
            filas += datos[clave] if clave else datos
            m = re.search(r'<([^>]+)>;\s*rel="next"', cab.get("Link", "") or "")
            url = m.group(1) if m else None
        return filas

    def fichero(self, repo, ruta):
        """Texto de un fichero del repo, o None si no existe."""
        try:
            d = self.get(f"/repos/{repo}/contents/{urllib.parse.quote(ruta)}")
        except ErrorApi:
            return None
        if isinstance(d, dict) and d.get("encoding") == "base64":
            return base64.b64decode(d["content"]).decode("utf-8", "replace")
        return None


# ---------- Lógica pura (se prueba sin red en probar_vigilante.py) ----------

def tipo_de_paquete(nombre):
    """El nombre sin la versión delante ni el número detrás: misma regla que la limpieza de cada repo."""
    t = re.sub(r"^[A-Za-z]+(-Gratis)?-[0-9][^ ]* - ", "", nombre)
    t = re.sub(r"^(Platinum Hunter|PH Gratis) - ", "", t)
    return re.sub(r"-[0-9]+$", "", t)


def paquetes_a_borrar(paquetes, ahora):
    """De cada tipo se queda el más reciente, salvo que tenga más de 3 días (las capturas, 2)."""
    grupos = {}
    for p in paquetes:
        grupos.setdefault(tipo_de_paquete(p["name"]), []).append(p)
    borrar = []
    for tipo, lista in grupos.items():
        lista.sort(key=lambda p: p["created_at"], reverse=True)
        limite = 2 * 86400 if tipo.startswith("Capturas") else 3 * 86400
        for i, p in enumerate(lista):
            edad = (ahora - fecha(p["created_at"])).total_seconds()
            if i > 0 or edad > limite:
                borrar.append(p)
    return borrar


def fecha(txt):
    return dt.datetime.fromisoformat(txt.replace("Z", "+00:00"))


def minutos_facturados(trabajos):
    """GitHub cobra cada trabajo redondeado al minuto hacia arriba (Linux, multiplicador 1)."""
    total = 0
    for t in trabajos:
        if t.get("started_at") and t.get("completed_at"):
            seg = (fecha(t["completed_at"]) - fecha(t["started_at"])).total_seconds()
            if seg > 0:
                total += math.ceil(seg / 60)
    return total


def version_del_codigo(texto_version, textos_py):
    """«PH 2.5.35» del fichero VERSION, o el APP_VERSION de un *_app.py."""
    if texto_version and texto_version.strip():
        partes = texto_version.split()
        return partes[-1] if partes else None
    for t in textos_py:
        m = re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', t or "", re.M)
        if m:
            return m.group(1)
    return None


def version_en_cambios(version, cambios):
    """¿Aparece la versión en algún encabezado ## de CAMBIOS.md?"""
    if not version or not cambios:
        return False
    patron = re.compile(r"(?<![\d.])" + re.escape(version) + r"(?![\d.])")
    return any(patron.search(l) for l in cambios.splitlines() if l.startswith("## "))


def target_sdk(gradle):
    m = re.search(r"targetSdk(?:Version)?\s*=?\s*(\d+)", gradle or "")
    return int(m.group(1)) if m else None


def revisar_workflow(texto, privado):
    """Avisos de un workflow: compila con cada push (en privado) o compila sin tope de tiempo."""
    avisos = []
    # «./gradlew …» o «gradle …» (no «gradle-version:» ni «gradle/actions»)
    compila = re.search(r"(?:\./gradlew|\bgradle)\s+[A-Za-z:]|\bassemble[A-Z]|\bbundle[A-Z]", texto or "") is not None
    on = re.search(r"^on:\s*\n((?:[ \t]+.*\n|\s*\n)*)", (texto or "") + "\n", re.M)
    bloque_on = on.group(1) if on else ""
    con_push = re.search(r"^\s+push:", bloque_on, re.M) is not None or re.search(r"^on:\s*\[?.*\bpush\b", texto or "", re.M) is not None
    if privado and compila and con_push:
        avisos.append("compila con cada push")
    if compila and "timeout-minutes" not in (texto or ""):
        avisos.append("compila sin tope de tiempo (timeout-minutes)")
    return avisos


def coma(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def huella(alertas):
    return hashlib.sha1("\n".join(sorted(alertas)).encode()).hexdigest()[:12]


# ---------- Recogida ----------

def repasar(gh, dueno, ahora, sdk_play):
    try:
        perfil = gh.get(f"/users/{dueno}")
    except ErrorApi:
        perfil = {"type": "User"}
    if perfil.get("type") == "Organization":
        repos = gh.todas(f"/orgs/{dueno}/repos?type=all")
    else:
        repos = [r for r in gh.todas("/user/repos?affiliation=owner&visibility=all")
                 if r["owner"]["login"].lower() == dueno.lower()]
    repos = [r for r in repos if not r.get("archived")]

    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    hace_semana = ahora - dt.timedelta(days=DIAS_SEMANA)
    filas, alertas, avisos = [], [], []
    total_min = 0
    total_mb = 0.0
    borrados_n, borrados_mb = 0, 0.0

    for r in sorted(repos, key=lambda r: r["name"].lower()):
        nombre, privado = r["full_name"], r["private"]
        fila = {"repo": r["name"], "privado": privado}
        try:
            # Ejecuciones de este mes: fallos de la semana y minutos facturados
            desde = min(inicio_mes, hace_semana).strftime("%Y-%m-%d")
            ejec = gh.todas(f"/repos/{nombre}/actions/runs?created=%3E%3D{desde}", clave="workflow_runs", tope=400)
            fallos = [e for e in ejec if e.get("conclusion") in ("failure", "timed_out", "startup_failure")
                      and fecha(e["created_at"]) >= hace_semana]
            ultimos = {}
            for e in sorted(ejec, key=lambda e: e["created_at"]):
                ultimos[e["name"]] = e
            # Solo cuenta como fallo si la última ejecución de ese workflow sigue fallando
            fallos_vivos = sorted({e["name"] for e in fallos if ultimos[e["name"]].get("conclusion") in ("failure", "timed_out", "startup_failure")})
            fila["fallos"] = fallos_vivos
            for w in fallos_vivos:
                alertas.append(f"**{r['name']}**: «{w}» falla (última ejecución)")

            minutos = 0
            if privado:
                for e in ejec:
                    if fecha(e["created_at"]) >= inicio_mes and e.get("status") == "completed":
                        trabajos = gh.todas(f"/repos/{nombre}/actions/runs/{e['id']}/jobs", clave="jobs", tope=100)
                        minutos += minutos_facturados(trabajos)
            fila["minutos"] = minutos
            total_min += minutos

            # Paquetes: limpieza y espacio
            paquetes = [p for p in gh.todas(f"/repos/{nombre}/actions/artifacts", clave="artifacts") if not p.get("expired")]
            for p in paquetes_a_borrar(paquetes, ahora):
                try:
                    gh.pedir("DELETE", f"/repos/{nombre}/actions/artifacts/{p['id']}")
                    borrados_n += 1
                    borrados_mb += p["size_in_bytes"] / 1e6
                    paquetes.remove(p)
                except ErrorApi:
                    avisos.append(f"**{r['name']}**: no se pudo borrar un paquete viejo")
            mb = sum(p["size_in_bytes"] for p in paquetes) / 1e6
            fila["mb"] = mb
            total_mb += mb

            # Dependabot
            prs = gh.todas(f"/repos/{nombre}/pulls?state=open", tope=200)
            fila["dependabot"] = sum(1 for p in prs if p["user"]["login"].startswith("dependabot"))
            if fila["dependabot"]:
                avisos.append(f"**{r['name']}**: {fila['dependabot']} propuesta(s) de Dependabot sin revisar")

            # Versión contra CAMBIOS.md
            raiz = gh.get(f"/repos/{nombre}/contents/")
            nombres = {f["name"] for f in raiz} if isinstance(raiz, list) else set()
            txt_version = gh.fichero(nombre, "VERSION") if "VERSION" in nombres else None
            pys = [gh.fichero(nombre, n) for n in sorted(nombres) if n.endswith("_app.py")][:3]
            version = version_del_codigo(txt_version, pys)
            fila["version"] = version
            if version and "CAMBIOS.md" in nombres:
                if not version_en_cambios(version, gh.fichero(nombre, "CAMBIOS.md")):
                    avisos.append(f"**{r['name']}**: la versión {version} no está apuntada en CAMBIOS.md")

            # Apps de Play: targetSdk
            if "play" in nombres:
                gradle = gh.fichero(nombre, "app/build.gradle.kts") or gh.fichero(nombre, "app/build.gradle")
                sdk = target_sdk(gradle)
                fila["sdk"] = sdk
                if sdk is None:
                    avisos.append(f"**{r['name']}**: no encuentro el targetSdk")
                elif sdk < sdk_play:
                    alertas.append(f"**{r['name']}**: targetSdk {sdk}, Google Play exige {sdk_play}")

            # Workflows
            try:
                wfs = gh.get(f"/repos/{nombre}/contents/.github/workflows")
            except ErrorApi:
                wfs = []
            for w in wfs if isinstance(wfs, list) else []:
                if w["name"].endswith((".yml", ".yaml")):
                    for a in revisar_workflow(gh.fichero(nombre, w["path"]), privado):
                        avisos.append(f"**{r['name']}** · `{w['name']}`: {a}")
        except ErrorApi as e:
            avisos.append(f"**{r['name']}**: no se pudo revisar del todo ({e})")
        filas.append(fila)

    return {
        "filas": filas, "alertas": alertas, "avisos": avisos,
        "total_min": total_min, "total_mb": total_mb,
        "borrados_n": borrados_n, "borrados_mb": borrados_mb,
    }


def componer(res, ahora, caduca):
    alertas, avisos = list(res["alertas"]), list(res["avisos"])
    pct_min = 100 * res["total_min"] / TOPE_MIN_MES
    if pct_min >= 75:
        alertas.append(f"Minutos de Actions: {res['total_min']} de {TOPE_MIN_MES} este mes ({coma(pct_min, 0)} %)")
    pct_mb = 100 * res["total_mb"] / TOPE_PAQUETES_MB
    if pct_mb >= 75:
        alertas.append(f"Paquetes de Actions: {coma(res['total_mb'])} MB de {TOPE_PAQUETES_MB} MB ({coma(pct_mb, 0)} %)")
    if caduca:
        try:
            dias = (dt.datetime.strptime(caduca[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc) - ahora).days
            if dias <= 30:
                alertas.append(f"El token del vigilante caduca en {dias} días: hay que renovarlo")
        except ValueError:
            pass

    hoy = ahora.astimezone(dt.timezone(dt.timedelta(hours=1))).strftime("%d-%m-%Y")
    l = [f"Informe del vigilante · {hoy}", ""]
    if alertas:
        l += ["## 🔴 Hay que mirarlo", *[f"- {a}" for a in alertas], ""]
    else:
        l += ["## 🟢 Todo en orden", ""]
    if avisos:
        l += ["## 🟡 Avisos", *[f"- {a}" for a in avisos], ""]
    l += ["## Repos", "", "| Repo | Versión | Min. este mes | Paquetes | Dependabot | targetSdk |", "|---|---|---|---|---|---|"]
    for f in res["filas"]:
        priv = "" if f["privado"] else " (público)"
        l.append(f"| {f['repo']}{priv} | {f.get('version') or ''} | {f.get('minutos', '') if f['privado'] else '—'} | "
                 f"{coma(f.get('mb', 0))} MB | {f.get('dependabot', '')} | {f.get('sdk') or ''} |")
    l += ["", f"- Minutos de Actions este mes (repos privados, estimación por trabajos): **{res['total_min']} de {TOPE_MIN_MES}**",
          f"- Paquetes de Actions guardados: **{coma(res['total_mb'])} MB de {TOPE_PAQUETES_MB} MB**",
          f"- Limpieza de hoy: {res['borrados_n']} paquetes borrados ({coma(res['borrados_mb'])} MB)"]
    if caduca:
        l.append(f"- El token caduca el {caduca[:10]}")
    l += ["", "_Este issue lo reescribe cada día el vigilante del repo de la web. No se compila ni se sube nada desde aquí._"]
    return "\n".join(l), alertas


def publicar(gh, repo_informe, cuerpo, alertas):
    """Reescribe el issue fijo. Devuelve True si hay alertas nuevas respecto a ayer."""
    marca = f"<!-- alertas:{huella(alertas)} -->"
    abiertos = gh.todas(f"/repos/{repo_informe}/issues?state=open", tope=500)
    issue = next((i for i in abiertos if i["title"] == TITULO_ISSUE and "pull_request" not in i), None)
    if issue is None:
        gh.pedir("POST", f"/repos/{repo_informe}/issues", {"title": TITULO_ISSUE, "body": cuerpo + "\n" + marca})
        return bool(alertas)
    anterior = re.search(r"<!-- alertas:(\w+) -->", issue.get("body") or "")
    gh.pedir("PATCH", f"/repos/{repo_informe}/issues/{issue['number']}", {"body": cuerpo + "\n" + marca})
    nuevas = bool(alertas) and (anterior is None or anterior.group(1) != huella(alertas))
    if nuevas:
        gh.pedir("POST", f"/repos/{repo_informe}/issues/{issue['number']}/comments",
                 {"body": "🔴 Alertas nuevas:\n\n" + "\n".join(f"- {a}" for a in alertas)})
    return nuevas


def main():
    token, repo_informe = os.environ.get("VIGILANTE_TOKEN"), os.environ.get("REPO_INFORME")
    if not token or not repo_informe:
        print("Faltan los secretos VIGILANTE_TOKEN o REPO_INFORME (ver herramientas/LEEME-VIGILANTE.md).")
        return 2
    dueno = os.environ.get("GITHUB_REPOSITORY_OWNER") or repo_informe.split("/")[0]
    sdk_play = int(os.environ.get("PLAY_TARGET_SDK") or 36)
    ahora = dt.datetime.now(dt.timezone.utc)
    gh = GitHub(token)
    try:
        res = repasar(gh, dueno, ahora, sdk_play)
        cuerpo, alertas = componer(res, ahora, gh.caduca)
        nuevas = publicar(gh, repo_informe, cuerpo, alertas)
    except ErrorApi as e:
        # Sin detalles: el registro de este repo es público
        print(f"El vigilante no pudo terminar ({e}). Revisa el token y sus permisos.")
        return 1
    print(f"Informe escrito ({gh.llamadas} llamadas a la API).")
    if nuevas:
        # Hacer fallar la ejecución es lo que hace que GitHub mande el aviso por correo y al móvil
        print("Hay alertas nuevas: mira el issue «Mantenimiento de las apps».")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
