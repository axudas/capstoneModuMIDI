# Renders the PNGs in ../img. Needs: pip install pyvista vtk, and a display (on a headless Linux box: xvfb-run python3 render_views.py .)
import sys, os, numpy as np
D = sys.argv[1]; sys.path.insert(0, D); os.chdir(D)
import spacebar_stack as S
import pyvista as pv
IMG = os.path.join(D, '..', 'img')
os.makedirs(IMG, exist_ok=True)

def poly(m):
    mesh = m.to_mesh(); v = np.asarray(mesh.vert_properties)[:, :3]; f = np.asarray(mesh.tri_verts)
    faces = np.hstack([np.full((len(f), 1), 3), f]).ravel()
    return pv.PolyData(v, faces).clean()

def render(items, fname, cam, title, size=(1800, 1100), zoom=1.0, parallel=False, labels=None):
    p = pv.Plotter(off_screen=True, window_size=size, lighting='three lights')
    p.set_background('#d9dde2', top='#ffffff')
    for m, c in items:
        pm = poly(m)
        if pm.n_points == 0:
            continue
        op = c[3] / 255
        p.add_mesh(pm, color=[x / 255 for x in c[:3]], opacity=op, smooth_shading=False,
                   specular=0.2, ambient=0.25, diffuse=0.75)
        p.add_mesh(pm.extract_feature_edges(35, boundary_edges=False, non_manifold_edges=False, manifold_edges=False),
                   color='#333333', line_width=1.0, opacity=min(1.0, op + 0.3))
    if labels:
        p.add_point_labels(np.array([q for q, t in labels], dtype=float), [t for q, t in labels], font_size=22,
                           text_color='#222222', shape_color='white', shape_opacity=0.8, point_size=1,
                           show_points=False, always_visible=True)
    p.camera_position = cam
    if parallel: p.enable_parallel_projection()
    p.reset_camera(); p.camera.zoom(zoom)
    p.add_text(title, position='upper_edge', font_size=12, color='#222222')
    p.screenshot(os.path.join(IMG, fname))
    p.close()

KEY_LAYERS = ('key', 'topper')
built = {k: S.build(k) for k in S.KEYS}
ISO = lambda c: [(c[0] + 190, c[1] - 150, c[2] + 150), c, (0, 0, 1)]

# the three keys side by side, assembled (key + topper + parts)
row = []
for i, k in enumerate(('white', 'black', 'grey')):
    row += [(m.translate(((i - 1) * 34.0, 0, 0)), c) for n, l, m, c in built[k] if l in KEY_LAYERS]
render(row, 'keys_overview.png', [(160, -170, 150), (0, 0, 22), (0, 0, 1)],
       'The three 3u keys, assembled with their toppers: white, black, grey (front of the keys toward the camera)', zoom=1.35)

# the three whole-stack breakdowns side by side (white, black, grey)
GAP = 95.0
allx, lbl = [], []
for i, k in enumerate(('white', 'black', 'grey')):
    dx = (i - 1) * GAP
    allx += [(m.translate((dx, 0, S.part_explode(n, l))), c) for n, l, m, c in built[k]]
    lbl.append(((dx, 0, S.Z_CAP_TOP + S.EXPLODE['key'] + S.KEY_EXPLODE['5_topper'] + S.TOPPER_H + 14), k.capitalize() + ' key'))
render(allx, 'exploded_all.png', [(170, -470, 260), (0, 0, 50), (0, 0, 1)],
       'White, black and grey keys exploded: PCB / foam / plate + switch + low-profile stab / key + LED, pogo, magnets / shim, magnets / topper',
       size=(2600, 1400), zoom=1.3, labels=lbl)
print('ok all')

for k in S.KEYS:
    parts = built[k]
    expl = [(m.translate((0, 0, S.part_explode(n, l))), c) for n, l, m, c in parts]
    render(expl, f'exploded_{k}.png', ISO((0, 0, 55)),
           f'{k.capitalize()} key: whole stack exploded (PCB, foam, plate + switch + low-profile stab, key + parts, topper)', zoom=1.1)
    kx = [(m.translate((0, 0, S.KEY_EXPLODE[n])), c) for n, l, m, c in parts if n in S.KEY_EXPLODE]
    render(kx, f'key_exploded_{k}.png', ISO((0, 0, 40)),
           f'{k.capitalize()} key broken apart: key / LED pixel, pogo, magnets / shim, magnets / topper', zoom=1.3)
    print('ok', k)

# assembled stack (white)
render([(m, c) for n, l, m, c in built['white']], 'assembled_iso.png', ISO((0, 5, 12)),
       'White key stack assembled (the PCB tab with the screw terminal sticks out at the back)', zoom=1.25)

# key tops with the topper lifted: LED pocket, pogo connector, magnets, lip
for k in ('white', 'black'):
    det = [(m.translate((26, 0, 0) if l == 'topper' else (0, 0, 0)), c) for n, l, m, c in built[k] if l in KEY_LAYERS]
    render(det, f'detail_{k}.png', [(40, -120, 150), (13, 0, 24), (0, 0, 1)],
           f'{k.capitalize()} key with the topper beside it: LED pixel, pogo connector, magnets', zoom=1.25)
    below = [(m.translate((26, 0, 0) if l == 'topper' else (0, 0, 0)), c) for n, l, m, c in built[k] if l in KEY_LAYERS]
    render(below, f'detail_below_{k}.png', [(40, -120, -110), (13, 0, 24), (0, 0, 1)],
           f'{k.capitalize()} key + topper from below: stem socket, stab posts, LED wire hole, pogo tails, topper lip, magnets', zoom=1.25)
print('done')
