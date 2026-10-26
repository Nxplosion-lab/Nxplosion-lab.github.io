"""Pedazos en los que estalla el logo nuevo (mismo formato que IntroShards.kt: cx,cy,x0,y0,x1,y1,puntos…; separados por «;»),
en coordenadas de la imagen de la intro (841 × 1870), con el logo puesto en (LOGO_X, LOGO_Y)."""
import json, sys, numpy as np
from PIL import Image
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, box as sbox
LOGO_X, LOGO_Y = int(sys.argv[1]), int(sys.argv[2])
SRC = sys.argv[3] if len(sys.argv) > 3 else 'logo3d_A.png'
im = np.array(Image.open(SRC).convert('RGBA')); H, W = im.shape[:2]
alpha = im[..., 3] > 60
rng = np.random.default_rng(16)
ys, xs = np.where(alpha)
pts = []
for i in rng.permutation(len(xs)):
    p = (xs[i], ys[i])
    if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 20 ** 2 for q in pts):
        pts.append(p)
    if len(pts) >= 300:
        break
pts = np.array(pts, float)
far = np.array([[-2000, -2000], [3000, -2000], [-2000, 3000], [3000, 3000]])
vor = Voronoi(np.vstack([pts, far]))
frame = sbox(0, 0, W, H)
out = []
for k in range(len(pts)):
    reg = vor.regions[vor.point_region[k]]
    if -1 in reg or not reg:
        continue
    poly = Polygon(vor.vertices[reg]).intersection(frame)
    if poly.is_empty or poly.area < 30:
        continue
    x0, y0, x1, y1 = poly.bounds
    m = alpha[int(y0):int(np.ceil(y1)), int(x0):int(np.ceil(x1))]
    if m.sum() < 25:
        continue
    c = poly.centroid
    ring = list(poly.exterior.coords)[:-1]
    vals = [c.x + LOGO_X, c.y + LOGO_Y, x0 + LOGO_X, y0 + LOGO_Y, x1 + LOGO_X, y1 + LOGO_Y]
    for (px, py) in ring:
        vals += [px + LOGO_X, py + LOGO_Y]
    out.append(','.join(str(int(round(v))) for v in vals))
open(sys.argv[4] if len(sys.argv) > 4 else 'fragmentos.txt', 'w').write(';'.join(out))
print(len(out), 'pedazos;', len(';'.join(out)), 'caracteres')
