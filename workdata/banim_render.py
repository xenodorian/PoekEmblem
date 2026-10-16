#!/usr/bin/env python3
"""Render FE8 battle animation frames from the decomp data (OAM piece lists + tile sheets + palette).
usage: banim_render.py <decomp_dir> <stem e.g. drkm_sp1> <mode e.g. attack_close> <out_dir> [palette_index]"""
import re, sys, os, struct
import numpy as np
from PIL import Image
SZ = {0:{0:(8,8),1:(16,16),2:(32,32),3:(64,64)},1:{0:(16,8),1:(32,8),2:(32,16),3:(64,32)},2:{0:(8,16),1:(8,32),2:(16,32),3:(32,64)}}

def load(dec, stem):
    s = open(f'{dec}/data/banim/banim_{stem}_motion.s').read()
    oam = {}; cur = None; script = {}; mode = None
    for line in s.split('\n'):
        m = re.match(r'banim_\w+_oam_frame_(\d+)_([lr]):', line)
        if m: cur = (int(m.group(1)), m.group(2)); oam[cur] = []; continue
        m = re.match(r'\s*banim_frame_oam\s+(0x[0-9A-Fa-f]+|\d+),\s*(0x[0-9A-Fa-f]+|\d+),\s*(0x[0-9A-Fa-f]+|\d+),\s*(-?\d+),\s*(-?\d+)', line)
        if m and cur is not None:
            oam[cur].append(tuple(int(m.group(i), 0) if i < 4 else int(m.group(i)) for i in (1, 2, 3, 4, 5))); continue
        m = re.match(rf'banim_{stem}_mode_(\w+):', line)
        if m: mode = m.group(1); script[mode] = []; cur = None; continue
        m = re.match(rf'\s*banim_code_frame\s+(\d+),\s*banim_{stem}_sheet_(\d+),\s*(\d+),\s*banim_{stem}_oam_frame_(\d+)_([lr])', line)
        if m and mode: script[mode].append((int(m.group(1)), int(m.group(2)), int(m.group(4)), m.group(5))); continue
        m = re.match(r'\s*banim_code_(sound_\w+|hit_normal|call_spell_anim|prepare_hp_deplete|wait_hp_deplete|start_opposite_turn|shake_\w+|end_\w+)', line)
        if m and mode: script[mode].append(('event', m.group(1)))
    return oam, script

def palette(dec, stem, idx):
    d = open(f'{dec}/graphics/banim/banim_{stem}.agbpal', 'rb').read()[idx*32:(idx+1)*32]
    return np.array([(((v := struct.unpack_from('<H', d, i)[0]) & 31) * 8, ((v >> 5) & 31) * 8, ((v >> 10) & 31) * 8) for i in range(0, 32, 2)], np.uint8)

def render_frame(sheet_idx, pieces, sheets, pal, W, H, ox, oy):
    canvas = np.zeros((H, W, 4), np.uint8)
    sheet = sheets[sheet_idx]
    for a0, a1, a2, dx, dy in reversed(pieces):          # OAM order: first entry is drawn on top
        w, h = SZ[(a0 >> 14) & 3][(a1 >> 14) & 3]
        n = a2 & 0x3FF; tx, ty = (n & 31) * 8, (n >> 5) * 8
        idxs = sheet[ty:ty+h, tx:tx+w]
        if idxs.shape != (h, w): continue
        if a1 & 0x1000: idxs = idxs[:, ::-1]
        if a1 & 0x2000: idxs = idxs[::-1, :]
        x0, y0 = ox + dx, oy + dy
        for yy in range(h):
            for xx in range(w):
                v = idxs[yy, xx]
                px, py = x0 + xx, y0 + yy
                if v and 0 <= px < W and 0 <= py < H:
                    canvas[py, px] = (*pal[v], 255)
    return Image.fromarray(canvas, 'RGBA')

if __name__ == '__main__':
    dec, stem, mode, out = sys.argv[1:5]; pi = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    os.makedirs(out, exist_ok=True)
    oam, script = load(dec, stem)
    sheets = {}
    for k in range(32):
        p = f'{dec}/graphics/banim/banim_{stem}_sheet_{k}.png'
        if os.path.exists(p): sheets[k] = np.array(Image.open(p).convert('P'))
    pal = palette(dec, stem, pi)
    frames = [e for e in script[mode] if e[0] != 'event']
    if os.environ.get('FORCE_SIDE'): frames = [(d, sh, fn, os.environ['FORCE_SIDE']) for d, sh, fn, side in frames]
    # canvas sized from the union bounding box of the frames used
    SZl = []
    for d, sh, fn, side in frames:
        for a0, a1, a2, dx, dy in oam[(fn, side)]:
            w, h = SZ[(a0 >> 14) & 3][(a1 >> 14) & 3]; SZl.append((dx, dy, dx + w, dy + h))
    x0 = min(a for a, b, c, d in SZl); y0 = min(b for a, b, c, d in SZl); x1 = max(c for a, b, c, d in SZl); y1 = max(d for a, b, c, d in SZl)
    W, H = x1 - x0, y1 - y0
    print(f'{stem} {mode}: {len(frames)} frames, union box {W}x{H}, origin offset ({-x0},{-y0}), total duration {sum(f[0] for f in frames)}')
    for i, (d, sh, fn, side) in enumerate(frames):
        im = render_frame(sh, oam[(fn, side)], sheets, pal, W, H, -x0, -y0)
        im.save(f'{out}/f{i:02d}_d{d}.png')
    open(f'{out}/_meta.txt', 'w').write(f'{W} {H} {-x0} {-y0}\n' + '\n'.join(f'{i} {f[0]} {f[1]} {f[2]} {f[3]}' for i, f in enumerate(frames)))
