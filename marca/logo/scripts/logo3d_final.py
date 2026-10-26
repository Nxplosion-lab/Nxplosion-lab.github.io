"""Versión metálica 3D del logo final para la intro y la cabecera de la web:
el emblema NX de fuego de siempre + «plosion» y LABS de plata, colocados como en el logo final."""
import json
from PIL import Image; import numpy as np
from scipy import ndimage
from pathlib import Path
K = Path(__file__).resolve().parent.parent   # raíz del kit: marca/logo
# --- geometría del logo final (plano)
F = np.array(Image.open(K / 'plano/nxplosion-labs-sobre-claro.png')); fa = F[..., 3] > 100
fh, fw = fa.shape; fy, fx = np.mgrid[0:fh, 0:fw]
f_or = fa & (F[..., 0] > 150); f_nv = fa & (F[..., 0] < 100)
f_labs = f_nv & (fy >= 290) & (fx >= 900); f_word = f_nv & ~f_labs
def bb(m): ys, xs = np.where(m); return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
E_f, W_f, L_f = bb(f_or), bb(f_word), bb(f_labs)
# --- piezas de la versión 3D de siempre (812 × 215)
T = np.array(Image.open(K / 'metalico/fuente-metalica-intro-anterior.webp').convert('RGBA'))
th, tw = T.shape[:2]; ty, tx = np.mgrid[0:th, 0:tw]
r, g, b, a = [T[..., i].astype(int) for i in range(4)]
silver = (a > 60) & (np.abs(r - b) < 45) & (r > 90)
sil_near = ndimage.binary_dilation(silver, iterations=3)
emb = (tx < 345) & (((tx < 241) & ~sil_near) | (tx < 236) | ((r > g + 25) & ~sil_near))   # el emblema: el fuego, sin restos de la N y la X de plata
X3 = np.array(Image.open(K / 'metalico/mascara-x-plateada-anterior.png')) > 0
X3 = ndimage.binary_dilation(X3 & ((tx < 409) | (ty < 42)), iterations=9)
word = (silver | (ndimage.binary_dilation(silver, iterations=2) & (a > 0))) & (tx >= 409) & (ty < 152) & ~X3          # «plosion» de plata (sin NX)
labs0 = silver & (ty >= 152)
lab_l, nl = ndimage.label(labs0)
sizes = ndimage.sum(labs0, lab_l, range(1, nl + 1))
objs = ndimage.find_objects(lab_l)
keep = [i + 1 for i, sl in enumerate(objs) if sizes[i] > 40 and sl[0].start >= 160 and sl[1].start >= 435]   # las cuatro letras de LABS
labs = ndimage.binary_dilation(np.isin(lab_l, keep), iterations=3) & (ty >= 148)
def layer(m):
    o = T.copy(); o[..., 3] = np.where(m, o[..., 3], 0); im = Image.fromarray(o); return im.crop(im.getbbox()), im.getbbox()
# el humo del emblema donde estaba la N de plata se desvanece suave (sin silueta de N); el fuego vivo se queda
lab_w, nw = ndimage.label(word); sz = ndimage.sum(word, lab_w, range(1, nw + 1))
word = np.isin(lab_w, [i + 1 for i, v in enumerate(sz) if v >= 30])            # fuera motas sueltas
bright = (r > 200) & (g > 70)
fade = np.clip((345 - tx) / (345 - 236), 0, 1) ** 1.5
Wi, W3 = layer(word); Li, L3 = layer(labs)
T = T.copy(); T[..., 3] = np.where((tx >= 236) & ~bright, (T[..., 3] * fade).astype(np.uint8), T[..., 3])   # solo para el emblema
Ei, E3 = layer(emb)
# --- escala: la del emblema (3D / plano)
s = ((E3[2] - E3[0]) / (E_f[2] - E_f[0]) + (E3[3] - E3[1]) / (E_f[3] - E_f[1])) / 2
def target(bf): return [round((bf[0] - E_f[0]) * s), round((bf[1] - E_f[1]) * s), round((bf[2] - E_f[0]) * s), round((bf[3] - E_f[1]) * s)]
Wt, Lt = target(W_f), target(L_f)
# misma proporción que el original (sin estirar): se ajusta por la altura y se alinea como en el logo final
kw = (Wt[3] - Wt[1]) / Wi.height; Wr = Wi.resize((round(Wi.width * kw), Wt[3] - Wt[1]), Image.LANCZOS)
Wt = [Wt[0], Wt[1], Wt[0] + Wr.width, Wt[3]]
kl = (Lt[2] - Lt[0]) / Li.width; Lr = Li.resize((Lt[2] - Lt[0], round(Li.height * kl)), Image.LANCZOS)   # LABS al ancho del logo final
Lt = [Wt[2] - Lr.width, Lt[1], Wt[2], Lt[3]]                     # LABS alineado a la derecha con la «n»
Wd = max(Ei.width, Wt[2], Lt[2]) + 6; Hd = max(Ei.height, Wt[3], Lt[3]) + 6
out = Image.new('RGBA', (Wd, Hd))
out.alpha_composite(Ei, (0, 0))          # primero el fuego; la plata va encima donde se cruzan
out.alpha_composite(Wr, (Wt[0], Wt[1])); out.alpha_composite(Lr, (Lt[0], Lt[1]))
out = out.crop(out.getbbox()); out.save('logo3d_final.png')
# capas para la intro: el emblema (cae) y la palabra (se forja); misma caja
ox, oy = Image.new('RGBA', (Wd, Hd)), None
base = Image.new('RGBA', (Wd, Hd)); base.alpha_composite(Ei, (0, 0)); 
wl = Image.new('RGBA', (Wd, Hd)); wl.alpha_composite(Wr, (Wt[0], Wt[1])); wl.alpha_composite(Lr, (Lt[0], Lt[1]))
full = Image.new('RGBA', (Wd, Hd)); full.alpha_composite(base); full.alpha_composite(wl)
box = full.getbbox()
base.crop(box).save('capa_emblema.png'); wl.crop(box).save('capa_palabra.png')
geo = dict(size=list(full.crop(box).size), emblema=[E3[0] - E3[0] - box[0], 0 - box[1], (E3[2] - E3[0]) - box[0], (E3[3] - E3[1]) - box[1]],
           palabra=[Wt[0] - box[0], Wt[1] - box[1], Wt[2] - box[0], Wt[3] - box[1]], labs=[Lt[0] - box[0], Lt[1] - box[1], Lt[2] - box[0], Lt[3] - box[1]])
json.dump(geo, open('geom_final.json', 'w')); print('escala', round(s, 3), geo)
