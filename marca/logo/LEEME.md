# Kit del logo de NXplosion Labs

Todo el artwork del **logo final** (26-10-2026) está en esta carpeta. Los ficheros se pueden descargar desde la web:
`https://nxplosion-lab.github.io/marca/logo/<carpeta>/<fichero>`.

**Regla de marca:** el logo nunca lleva fondo ni caja. Siempre va solo, sobre lo que haya detrás.

## Cómo es el logo
- **Emblema NX** naranja delante. La X tiene forma de rayo y su punta sube por encima de la palabra.
- **«plosion»** a continuación.
- **LABS** debajo, alineado a la derecha y muy espaciado.
- Colores:

| Uso | Color |
|---|---|
| Naranja del emblema | `#FC5F15` |
| «plosion» y LABS sobre claro | `#12212C` (azul marino) |
| «plosion» y LABS sobre oscuro | `#FFFFFF` |

## Qué hay en cada carpeta

| Carpeta | Fichero | Para qué |
|---|---|---|
| `vector/` | `nxplosion-labs-sobre-claro.svg` | **Original vectorial.** Escala a cualquier tamaño: imprenta, Play, redes. Sobre fondo claro. |
| `vector/` | `nxplosion-labs-sobre-oscuro.svg` | Lo mismo, sobre fondo oscuro. |
| `vector/` | `emblema-nx.svg` | Solo el emblema NX: icono, avatar, favicon. |
| `plano/` | `nxplosion-labs-sobre-claro.png` / `-sobre-oscuro.png` | 1330 × 353, fondo transparente. |
| `plano/` | `emblema-nx.png`, `favicon-64.png` | El emblema solo (591 × 353) y el icono de la pestaña de la web. |
| `metalico/` | `nxplosion-labs-metalico.png` | Versión metálica: emblema de fuego, «plosion» y LABS de plata (741 × 205). |
| `metalico/` | `capa-emblema-fuego.png`, `capa-palabra-plata.png` | Las dos capas de la intro. Donde se tocan, la plata va por encima del fuego. |
| `metalico/` | `geometria.json` | Cajas del emblema, la palabra y LABS dentro de la versión metálica. |
| `metalico/` | `fuente-metalica-intro-anterior.webp`, `mascara-x-plateada-anterior.png` | De dónde sale el metal (el logo de la intro anterior) y la máscara de su X plateada. Hacen falta para regenerarlo. |
| `web/` | `forja-cabecera.jpg` | La imagen de la cabecera de la web: la forja de la intro con el logo metálico. |
| `web/` | `intro-platinum-hunter.mp4`, `intro-poster.jpg` | La intro de Platinum Hunter con el sello «Catedral» (5,55 s), sin lema. |
| `web/` | `nxplosion-labs-512.png` | El logo de la cabecera y el pie de la web. |
| `app/` | `nxplosion_logo_clear.webp`, `nxplosion_logo_light.webp` | Los de la app: tema oscuro y tema claro. |
| `app/` | `intro_nx_logo.webp`, `intro_nx_emblem.webp`, `intro_nx_word.webp` | La intro de la app: el logo entero y sus dos capas. |
| `app/` | `fragmentos-intro.txt` | Los 176 pedazos en los que estalla el logo en la intro (el `DATA` de `IntroShards.kt`). |
| `original/` | `logo-final-original.png` | La imagen que mandó Mr. J, tal cual. |

## Cómo se regenera
Hace falta Python con numpy, scipy, Pillow, shapely y potracer. Los scripts están en `scripts/` y leen los ficheros de esta carpeta. Lo que generan lo dejan donde se ejecutan.

1. `python scripts/extraer.py`: saca las versiones planas del original (`logo_final_claro.png`, `logo_final_oscuro.png`).
2. `python scripts/vectorizar.py`: traza los SVG a partir de la versión plana. El trazado coincide en un 99,1 % con el PNG.
3. `python scripts/logo3d_final.py`: hace la versión metálica y sus dos capas.
4. `python scripts/fragmentos.py 56 706 logo3d_final.png fragmentos.txt`: hace los pedazos de la intro, con el logo puesto en (56, 706) dentro de la imagen de 841 × 1870.

Comprobado el 26-10-2026: los pasos 1 y 3 dan exactamente los mismos ficheros que hay aquí.
