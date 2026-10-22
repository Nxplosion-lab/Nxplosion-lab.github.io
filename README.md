# NXplosion Labs · web

Web pública de NXplosion Labs en 22 idiomas: el español en la raíz y cada idioma en su carpeta (en/, fr/, ja/…).
La raíz abre sola el idioma del navegador; el selector de arriba guarda el que elijas.

- Política de privacidad: https://nxplosion-lab.github.io/privacy.html (y /<idioma>/privacy.html)
- Contacto: duk3x.dev@gmail.com

## Cambiar textos

1. Edita `herramientas/web/textos/es.json` (y el mismo texto en los demás idiomas).
2. Las plantillas están en `herramientas/web/inicio.html` y `herramientas/web/privacidad.html`.
3. Ejecuta `python3 herramientas/generar_web.py` para rehacer todas las páginas, `sitemap.xml` y `robots.txt`.

GitHub comprueba en cada cambio que no falta ningún texto y que las páginas están al día.
