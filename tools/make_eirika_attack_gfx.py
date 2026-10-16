#!/usr/bin/env python3
"""Build the in-battle Eirika attack animation assets for the decomp (needs the rendered frames, which are FE8 art and not in this repo).

usage: make_eirika_attack_gfx.py FRAME_DIR DECOMP_DIR
  FRAME_DIR: folder with f00_dN.png .. fNN_dN.png (88x48 RGBA, max 15 colors across all frames) and _meta.txt
  Writes graphics/battle_anims/eirika_attack/{a.png,b.png,attack.pal} and src/data/eirika_attack_frames.h in DECOMP_DIR.
Each frame becomes a 96x64 canvas (16 rows of headroom, frame at the bottom): sprite A is the left 64x64, sprite B the right 32x64.
"""
import sys, glob, os
import numpy as np
from PIL import Image

fd, dd = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(os.path.join(fd, 'f*.png')))
meta = open(os.path.join(fd, '_meta.txt')).read().split('\n')
dur = [int(l.split()[1]) for l in meta[1:] if l.strip()]
assert len(fs) == len(dur)
imgs = [np.array(Image.open(f).convert('RGBA')) for f in fs]
cols = sorted({tuple(c[:3]) for a in imgs for c in a.reshape(-1, 4) if c[3] > 0})
assert len(cols) <= 15
cmap = {c: i + 1 for i, c in enumerate(cols)}
pal = [(255, 0, 255)] + cols + [(0, 0, 0)] * (15 - len(cols))
N = len(imgs)
A = np.zeros((64 * N, 64), np.uint8); B = np.zeros((64 * N, 32), np.uint8)
for k, a in enumerate(imgs):
    canvas = np.zeros((64, 96), np.uint8)
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if a[y, x, 3] > 0:
                canvas[16 + y, x] = cmap[tuple(a[y, x, :3])]
    A[64 * k:64 * k + 64] = canvas[:, :64]; B[64 * k:64 * k + 64] = canvas[:, 64:]
out = os.path.join(dd, 'graphics/battle_anims/eirika_attack'); os.makedirs(out, exist_ok=True)
for arr, name in ((A, 'a.png'), (B, 'b.png')):
    im = Image.fromarray(arr, 'P'); p = [v for c in pal for v in c]
    im.putpalette(p + [0] * (768 - len(p))); im.save(os.path.join(out, name))
open(os.path.join(out, 'attack.pal'), 'w').write('JASC-PAL\n0100\n16\n' + '\n'.join('%d %d %d' % c for c in pal) + '\n')
L = ['// Generated: Eirika attack animation frame images and timing (1 unit = 1 game frame)\n',
     '#define EIRIKA_ATTACK_FRAME_COUNT %d\n' % N,
     'static const struct SpriteFrameImage sEirikaAttackImagesA[] = {\n' + ''.join('    { sEirikaAttackGfxA + 0x800 * %d, 0x800 },\n' % k for k in range(N)) + '};\n',
     'static const struct SpriteFrameImage sEirikaAttackImagesB[] = {\n' + ''.join('    { sEirikaAttackGfxB + 0x400 * %d, 0x400 },\n' % k for k in range(N)) + '};\n',
     'static const union AnimCmd sEirikaAttackAnim[] = {\n' + ''.join('    ANIMCMD_FRAME(%d, %d),\n' % (k, d) for k, d in enumerate(dur)) + '    ANIMCMD_FRAME(%d, EIRIKA_ATTACK_HOLD),\n    ANIMCMD_END\n};\n' % (N - 1)]
open(os.path.join(dd, 'src/data/eirika_attack_frames.h'), 'w').write(''.join(L))
print('frames', N, 'durations', dur, 'hit at', sum(dur[:9]))
