#!/usr/bin/env python3
"""Render the FE8 attack animation frames used for the Leg 2 allies (and Eirika) from the FE8 decomp.

usage: render_ally_frames.py FE8_DECOMP_DIR OUT_DIR
Needs tools/banim_render.py next to this script. Output folders (one per character) hold f00_dN.png ..., _meta.txt and _hit.txt,
which tools/make_ally_attack_gfx.py turns into game assets. The frames are FE8 art and must not be committed.
"""
import importlib.util, os, sys, struct
import numpy as np
from PIL import Image
D, OUT = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('br', os.path.join(here, 'banim_render.py')); br = importlib.util.module_from_spec(spec); spec.loader.exec_module(br)

def charpal(name):
    d = open(f'{D}/graphics/banim/character_palette/banim_pal_{name}.agbpal', 'rb').read()[:32]
    return np.array([(((v := struct.unpack_from('<H', d, i)[0]) & 31) * 8, ((v >> 5) & 31) * 8, ((v >> 10) & 31) * 8) for i in range(0, 32, 2)], np.uint8)

# name: (battle animation stem, character palette set or None for the class palette)
JOBS = {'eirika': ('lorf_sw1', None), 'innes': ('snim_ar1', None), 'tana': ('pekf_sp1', None), 'larachel': ('trof_ro1', 'lar'), 'dozla': ('brsm_ax1', 'doz'),
        'joshua': ('myrm_sw1', 'jho'), 'duessel': ('grkm_ax1', 'dus'), 'cormag': ('wykm_sp1', 'com'), 'myrrh': ('mf_mi1', 'mul')}
for key, (stem, pn) in JOBS.items():
    oam, script = br.load(D, stem)
    sheets = {k: np.array(Image.open(f'{D}/graphics/banim/banim_{stem}_sheet_{k}.png').convert('P')) for k in range(32) if os.path.exists(f'{D}/graphics/banim/banim_{stem}_sheet_{k}.png')}
    pal = charpal(pn) if pn else br.palette(D, stem, 0)
    frames = [(d, sh, fn, 'l') for d, sh, fn, side in [e for e in script['attack_close'] if e[0] != 'event']]
    boxes = []
    for d, sh, fn, side in frames:
        for a0, a1, a2, dx, dy in oam[(fn, side)]:
            w, h = br.SZ[(a0 >> 14) & 3][(a1 >> 14) & 3]; boxes.append((dx, dy, dx + w, dy + h))
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes); x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    W, H = x1 - x0, y1 - y0
    out = os.path.join(OUT, key); os.makedirs(out, exist_ok=True)
    t = 0; hit = None
    for e in script['attack_close']:
        if e[0] == 'event':
            if hit is None and e[1] in ('hit_normal', 'call_spell_anim', 'wait_hp_deplete'): hit = t
        else: t += e[0]
    for i, (d, sh, fn, side) in enumerate(frames):
        br.render_frame(sh, oam[(fn, side)], sheets, pal, W, H, -x0, -y0).save(f'{out}/f{i:02d}_d{d}.png')
    open(f'{out}/_meta.txt', 'w').write(f'{W} {H} {-x0} {-y0}\n' + '\n'.join(f'{i} {f[0]} {f[1]} {f[2]} {f[3]}' for i, f in enumerate(frames)))
    open(f'{out}/_hit.txt', 'w').write(str(hit))
    print(key, stem, len(frames), 'frames', W, 'x', H, 'hit', hit)
