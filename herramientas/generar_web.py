#!/usr/bin/env python3
"""
Genera la web de NXplosion Labs en 22 idiomas a partir de dos plantillas y un archivo de textos por idioma.

  herramientas/web/inicio.html        plantilla de la portada
  herramientas/web/privacidad.html    plantilla de la política de privacidad
  herramientas/web/textos/<idioma>.json

El español va en la raíz (index.html y privacy.html, que es la dirección que usan la app y Google Play);
cada otro idioma en su carpeta (en/, fr/, ja/…). También crea sitemap.xml y robots.txt.

  python3 herramientas/generar_web.py           escribe la web
  python3 herramientas/generar_web.py --check   solo comprueba (textos completos y web al día); sale con error si no
"""
import html
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(RAIZ, "herramientas", "web")
URL = "https://nxplosion-lab.github.io/"

# código de textos, carpeta, región, bandera (archivo en assets/banderas o None), lang de HTML, hreflang
IDIOMAS = [
    ("es", "", "europe", "es", "es", "es"),
    ("en", "en", "europe", "en", "en", "en"),
    ("fr", "fr", "europe", "fr", "fr", "fr"),
    ("de", "de", "europe", "de", "de", "de"),
    ("it", "it", "europe", "it", "it", "it"),
    ("pt-PT", "pt-pt", "europe", "pt-PT", "pt-PT", "pt-PT"),
    ("nl", "nl", "europe", "nl", "nl", "nl"),
    ("pl", "pl", "europe", "pl", "pl", "pl"),
    ("ru", "ru", "europe", "ru", "ru", "ru"),
    ("uk", "uk", "europe", "uk", "uk", "uk"),
    ("tr", "tr", "europe", "tr", "tr", "tr"),
    ("es-419", "es-419", "americas", "es-419", "es-419", "es-419"),
    ("pt-BR", "pt-br", "americas", "pt-BR", "pt-BR", "pt-BR"),
    ("ja", "ja", "asia", "ja", "ja", "ja"),
    ("ko", "ko", "asia", "ko", "ko", "ko"),
    ("zh-Hans", "zh-hans", "asia", "zh-Hans", "zh-Hans", "zh-Hans"),
    ("zh-Hant", "zh-hant", "asia", None, "zh-Hant", "zh-Hant"),
    ("hi", "hi", "asia", "hi", "hi", "hi"),
    ("id", "id", "asia", "id", "id", "id"),
    ("th", "th", "asia", "th", "th", "th"),
    ("vi", "vi", "asia", "vi", "vi", "vi"),
    ("ar", "ar", "asia", "ar", "ar", "ar"),
]
RTL = {"ar"}
CAMPOS_HTML = {"hero_title", "privacy_html"}  # llevan etiquetas: no se escapan


def textos(code):
    with open(os.path.join(WEB, "textos", f"{code}.json"), encoding="utf-8") as f:
        return json.load(f)


def etiquetas(s):
    return re.findall(r"</?[a-z0-9]+", s)


def comprobar_textos(todos):
    """Mismas claves que el español y las mismas etiquetas HTML en lo que lleva HTML."""
    base = todos["es"]
    fallos = []
    for code, t in todos.items():
        faltan = set(base) - set(t)
        sobran = set(t) - set(base)
        vacios = [k for k, v in t.items() if not str(v).strip()]
        if faltan: fallos.append(f"{code}: faltan {sorted(faltan)}")
        if sobran: fallos.append(f"{code}: sobran {sorted(sobran)}")
        if vacios: fallos.append(f"{code}: vacíos {vacios}")
        for k in CAMPOS_HTML:
            if k in t and etiquetas(t[k]) != etiquetas(base[k]):
                fallos.append(f"{code}: las etiquetas de {k} no coinciden con el español")
    return fallos


def bandera(flag, base):
    if flag is None:
        return '<span class="zh">繁</span>'
    return f'<img src="{base}assets/banderas/{flag}.png" alt="" width="32" height="24">'


def pagina(plantilla, code, carpeta, flag, html_lang, todos, tipo):
    t = todos[code]
    base = "" if carpeta == "" else "../"
    nombre = "index.html" if tipo == "inicio" else "privacy.html"
    ruta = (carpeta + "/" if carpeta else "") + ("" if tipo == "inicio" else "privacy.html")
    alternates = "".join(
        f'<link rel="alternate" hreflang="{hl}" href="{URL}{(c + "/" if c else "") + ("" if tipo == "inicio" else "privacy.html")}">'
        for _, c, _, _, _, hl in IDIOMAS
    ) + f'<link rel="alternate" hreflang="x-default" href="{URL}{"" if tipo == "inicio" else "privacy.html"}">'

    # Selector: la pastilla y la hoja con los 22 idiomas agrupados por región
    picker = (
        f'<button class="lang" type="button" onclick="document.getElementById(\'langs\').showModal()" aria-haspopup="dialog">'
        f'{bandera(flag, base)}{html.escape(t["lang_name"])}<span class="cv">▼</span></button>'
    )
    grupos = ""
    for reg, clave in (("europe", "region_europe"), ("americas", "region_americas"), ("asia", "region_asia")):
        items = ""
        for c2, carp2, r2, f2, hl2, _ in IDIOMAS:
            if r2 != reg:
                continue
            destino = base + (carp2 + "/" if carp2 else "") + ("" if tipo == "inicio" else "privacy.html")
            if destino == "":
                destino = "./"
            on = " on" if c2 == code else ""
            items += (
                f'<a class="it{on}" href="{destino}" hreflang="{hl2}" lang="{hl2}" data-lang="{carp2 or "es"}">'
                f'{bandera(f2, base)}{html.escape(todos[c2]["lang_name"])}</a>'
            )
        grupos += f'<div class="rg">{html.escape(t[clave])}</div><div class="grid">{items}</div>'
    dialog = (
        f'<dialog class="langs" id="langs" onclick="if(event.target===this)this.close()">'
        f'<div class="sheet"><div class="grab"></div><h3>{html.escape(t["lang_title"])}</h3>{grupos}</div></dialog>'
    )
    # Recuerda el idioma elegido; en la raíz, abre la web en el idioma del navegador si no se ha elegido otro
    mapa = json.dumps({c: (carp or "es") for c, carp, *_ in IDIOMAS})
    script = (
        "<script>(function(){"
        "document.querySelectorAll('#langs a[data-lang]').forEach(function(a){a.addEventListener('click',function(){"
        "try{localStorage.setItem('nx-lang',a.dataset.lang)}catch(e){}})});"
    )
    if carpeta == "":
        script += (
            f"var M={mapa};var pag={json.dumps('' if tipo == 'inicio' else 'privacy.html')};"
            "function elegir(){var s=null;try{s=localStorage.getItem('nx-lang')}catch(e){}if(s)return s;"
            "var ls=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'']);"
            "for(var i=0;i<ls.length;i++){var l=(ls[i]||'').toLowerCase();if(!l)continue;"
            "if(l==='es-es'||l==='es')return 'es';if(l.indexOf('es-')===0)return 'es-419';"
            "if(l==='pt-br')return 'pt-br';if(l.indexOf('pt')===0)return 'pt-pt';"
            "if(l.indexOf('zh')===0)return(/hant|tw|hk|mo/.test(l)?'zh-hant':'zh-hans');"
            "var b=l.split('-')[0];if(b==='in')b='id';for(var k in M){if(k.toLowerCase()===b)return M[k]}}return 'es'}"
            "var d=elegir();if(d&&d!=='es'){window.nxRedirige=1;location.replace(d+'/'+pag)}"
        )
    script += "})();</script>"

    valores = {
        "html_lang": html_lang,
        "dir": "rtl" if code in RTL else "ltr",
        "base": base,
        "home": "./",
        "privacy": "privacy.html",
        "canonical": URL + ruta,
        "alternates": alternates,
        "picker": picker,
        "dialog": dialog,
        "script": script,
    }

    def sustituir(m):
        k = m.group(1)
        if k in valores:
            return valores[k]
        v = t[k]
        return v if k in CAMPOS_HTML else html.escape(v, quote=True)

    salida = re.sub(r"\{\{([a-z0-9_]+)\}\}", sustituir, plantilla)
    destino = os.path.join(RAIZ, carpeta, nombre) if carpeta else os.path.join(RAIZ, nombre)
    return destino, salida


def generar():
    todos = {c: textos(c) for c, *_ in IDIOMAS}
    fallos = comprobar_textos(todos)
    plantillas = {}
    for tipo, archivo in (("inicio", "inicio.html"), ("privacidad", "privacidad.html")):
        with open(os.path.join(WEB, archivo), encoding="utf-8") as f:
            plantillas[tipo] = f.read()
    archivos = {}
    if not fallos:
        for code, carpeta, _, flag, html_lang, _ in IDIOMAS:
            for tipo in ("inicio", "privacidad"):
                destino, salida = pagina(plantillas[tipo], code, carpeta, flag, html_lang, todos, tipo)
                archivos[destino] = salida
        # Dirección antigua de la versión en inglés
        archivos[os.path.join(RAIZ, "en.html")] = (
            '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>NXplosion Labs</title>'
            f'<link rel="canonical" href="{URL}en/"><meta http-equiv="refresh" content="0; url=en/"></head>'
            '<body><a href="en/">NXplosion Labs</a></body></html>\n'
        )
        urls = []
        for _, carpeta, *_ in IDIOMAS:
            pre = URL + (carpeta + "/" if carpeta else "")
            urls += [pre, pre + "privacy.html"]
        archivos[os.path.join(RAIZ, "sitemap.xml")] = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
        )
        archivos[os.path.join(RAIZ, "robots.txt")] = f"User-agent: *\nAllow: /\nSitemap: {URL}sitemap.xml\n"
    return fallos, archivos


def main():
    check = "--check" in sys.argv
    fallos, archivos = generar()
    if fallos:
        print("Textos incompletos:\n  " + "\n  ".join(fallos))
        sys.exit(1)
    desfasados = []
    for ruta, contenido in archivos.items():
        actual = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else None
        if actual != contenido:
            desfasados.append(os.path.relpath(ruta, RAIZ))
            if not check:
                os.makedirs(os.path.dirname(ruta), exist_ok=True)
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
    if check and desfasados:
        print("La web no está al día con los textos; ejecuta herramientas/generar_web.py:\n  " + "\n  ".join(desfasados))
        sys.exit(1)
    print(f"{len(IDIOMAS)} idiomas, {len(archivos)} archivos" + (f", {len(desfasados)} actualizados" if not check else ", todo al día"))


if __name__ == "__main__":
    main()
