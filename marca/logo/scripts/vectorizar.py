"""Vectoriza el logo final (plano) a SVG: una forma por tinta, trazada con potrace sobre el original ampliado ×4."""
import sys, numpy as np, potrace
from pathlib import Path
from PIL import Image
from scipy import ndimage
K = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.')
S = 4
src = Image.open(K / 'plano/nxplosion-labs-sobre-claro.png').convert('RGBA')
W, H = src.size
big = np.array(src.resize((W * S, H * S), Image.LANCZOS)).astype(float)
r, g, b, a = (big[..., i] for i in range(4))
naranja = (a > 128) & (r > 150)
azul = (a > 128) & (r < 100)

def limpia(m):
    lab, n = ndimage.label(m); sz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    return np.isin(lab, 1 + np.nonzero(sz > 60 * S * S)[0])

def traza(m):
    bm = potrace.Bitmap(~m)   # potracer traza lo que vale False
    pl = bm.trace(turdsize=8 * S * S, alphamax=0.9, opticurve=True, opttolerance=0.25)
    f = lambda p: f'{p.x / S:.2f} {p.y / S:.2f}'
    d = []
    for c in pl:
        d.append('M' + f(c.start_point))
        for s in c.segments:
            d.append(('L' + f(s.c) + 'L' + f(s.end_point)) if s.is_corner else ('C' + f(s.c1) + ' ' + f(s.c2) + ' ' + f(s.end_point)))
        d.append('Z')
    return ''.join(d)

dn, da = traza(limpia(naranja)), traza(limpia(azul))
ys, xs = np.nonzero(limpia(naranja)); ew = (xs.max() + 1) / S
def svg(fill_word, title, w=W, h=H, solo_emblema=False):
    p = f'<path fill="#FC5F15" fill-rule="evenodd" d="{dn}"/>'
    if not solo_emblema: p += f'<path fill="{fill_word}" fill-rule="evenodd" d="{da}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{p}</svg>\n')
(OUT / 'nxplosion-labs-sobre-claro.svg').write_text(svg('#12212C', 'NXplosion Labs'))
(OUT / 'nxplosion-labs-sobre-oscuro.svg').write_text(svg('#FFFFFF', 'NXplosion Labs'))
(OUT / 'emblema-nx.svg').write_text(svg('', 'NXplosion Labs · emblema NX', w=round(ew + 1), solo_emblema=True))
print('ok', len(dn), len(da))
