"""Saca el logo final (el de Mr. J, 26-10-2026) del fondo blanco: dos tintas, naranja y azul noche,
con el antialias convertido en transparencia. Y la variante para fondo oscuro (azul → blanco)."""
from PIL import Image; import numpy as np
from pathlib import Path
K = Path(__file__).resolve().parent.parent   # raíz del kit: marca/logo
im = np.array(Image.open(K / 'original/logo-final-original.png').convert('RGB')).astype(float)[300:675, 95:1445]
W = np.array([254., 254., 254.])
COLS = {'naranja': np.array([252., 95., 21.]), 'azul': np.array([18., 33., 44.])}
best_a = None
for nm, C in COLS.items():
    d = W - C
    a = np.clip(((W - im) @ d) / (d @ d), 0, 1)
    res = np.linalg.norm(im - (a[..., None] * C + (1 - a[..., None]) * W), axis=-1)
    if best_a is None:
        best_a, best_res, best_c = a, res, np.where(np.ones_like(a, bool), 0, 0)
    else:
        take = res < best_res
        best_a = np.where(take, a, best_a); best_res = np.where(take, res, best_res); best_c = np.where(take, 1, best_c)
alpha = np.where(best_a < 0.03, 0, best_a)
def make(cols):
    out = np.zeros(alpha.shape + (4,), np.uint8)
    out[..., :3] = np.where(best_c[..., None] == 0, cols[0], cols[1])
    out[..., 3] = (alpha * 255).round().astype(np.uint8)
    im2 = Image.fromarray(out); return im2.crop(im2.getbbox())
claro = make([COLS['naranja'], COLS['azul']]); claro.save('logo_final_claro.png')
oscuro = make([COLS['naranja'], np.array([254., 254., 254.])]); oscuro.save('logo_final_oscuro.png')
np.save('tinta.npy', best_c[slice(None)]); print(claro.size, oscuro.size)
