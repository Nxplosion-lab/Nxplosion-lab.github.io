#!/usr/bin/env python3
"""
Comprueba la intro de Platinum Hunter en la web (tercer móvil y portada al entrar) en los 22 idiomas.

  python3 herramientas/probar_intro_web.py

Sin argumentos y desde cualquier sitio. Cuenta las comprobaciones y dice cuáles fallan.
"""
import html
import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
import generar_web as gw  # noqa: E402

ok, fallos = 0, []


def check(cond, que):
    global ok
    if cond:
        ok += 1
    else:
        fallos.append(que)


# 1. La web generada está al día con la plantilla y los textos
fallos_txt, archivos = gw.generar()
check(not fallos_txt, "textos completos en los 22 idiomas")
for ruta, contenido in archivos.items():
    actual = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else None
    check(actual == contenido, f"{os.path.relpath(ruta, RAIZ)} al día")

# 2. Los ficheros de la intro
mp4 = os.path.join(RAIZ, "assets", "intro-ph.mp4")
poster = os.path.join(RAIZ, "assets", "intro-poster.jpg")
check(os.path.exists(mp4), "assets/intro-ph.mp4 existe")
check(os.path.exists(poster), "assets/intro-poster.jpg existe")
if os.path.exists(mp4):
    mb = os.path.getsize(mp4) / 1e6
    check(mb < 3, f"el vídeo pesa menos de 3 MB (pesa {mb:.2f} MB)")
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name",
                              "-of", "json", mp4], capture_output=True, text=True, timeout=30).stdout
        info = json.loads(out)
        dur = float(info["format"]["duration"])
        tipos = {s["codec_type"]: s["codec_name"] for s in info["streams"]}
        check(abs(dur - 5.55) < 0.05, f"el vídeo dura 5,55 s como la intro (dura {dur:.2f} s)")
        check(tipos.get("video") == "h264", f"vídeo en H.264 (es {tipos.get('video')})")
        check(tipos.get("audio") == "aac", f"sonido en AAC (es {tipos.get('audio')})")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # sin ffprobe no se mide; el resto de comprobaciones sigue

# 3. Cada portada: dos vídeos, lema y botones en su idioma, rutas bien, captura vieja fuera
for code, carpeta, *_ in gw.IDIOMAS:
    t = gw.textos(code)
    base = "" if carpeta == "" else "../"
    p = os.path.join(RAIZ, carpeta, "index.html") if carpeta else os.path.join(RAIZ, "index.html")
    h = open(p, encoding="utf-8").read()
    n = code
    check(h.count(f'src="{base}assets/intro-ph.mp4"') == 2, f"{n}: dos vídeos (tercer móvil y portada) con la ruta {base}assets/")
    check(h.count(f'poster="{base}assets/intro-poster.jpg"') == 2, f"{n}: los dos con su póster")
    check("assets/entrada.jpg" not in h, f"{n}: la captura fija del tercer móvil ya no está")
    esc = lambda k: html.escape(t[k], quote=True)
    check(h.count(f'<b class="l1">{esc("slogan_1")}</b><b class="l2">{esc("slogan_2")}</b>') == 2, f"{n}: el lema encima del vídeo es el de la página")
    check(f'<i></i>{esc("intro_sound")}</button>' in h, f"{n}: botón «{t['intro_sound']}»")
    check(f'<i></i>{esc("intro_enter_sound")}</button>' in h and f'>{esc("intro_enter_mute")}</button>' in h, f"{n}: botones de la portada")
    check(f'<button class="skip" type="button">{esc("intro_skip")}</button>' in h, f"{n}: botón «{t['intro_skip']}»")
    check(re.search(r'<div class="cine" id="cine" hidden ', h) is not None, f"{n}: la portada sale oculta sin JavaScript")
    check(h.index('id="cine"') < h.index("nx-intro"), f"{n}: el código de la portada va después de la portada")
    check(("nxRedirige=1" in h) == (carpeta == ""), f"{n}: solo la raíz marca que va a cambiar de idioma")
    check("prefers-reduced-motion: reduce" in h, f"{n}: respeta «reducir movimiento»")
    check("{{" not in h, f"{n}: no quedan campos sin sustituir")

# 4. Los tiempos del lema son los de Intro.kt (T_BOOM = 2,35 s; total 5,55 s; lema a +1,15 y +1,35 s)
h = open(os.path.join(RAIZ, "index.html"), encoding="utf-8").read()
check("T0=2.35,TOT=5.55" in h, "estallido a 2,35 s y final a 5,55 s, como en Intro.kt")
check("seg(t,T0+1.15,T0+1.7)" in h and "seg(t,T0+1.35,T0+1.9)" in h, "el lema entra a +1,15 s y +1,35 s del estallido, como en Intro.kt")

total = ok + len(fallos)
print(f"{ok} de {total} comprobaciones pasan")
for f in fallos:
    print("  FALLA:", f)
sys.exit(1 if fallos else 0)
