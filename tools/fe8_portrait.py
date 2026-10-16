#!/usr/bin/env python3
"""Assemble FE8 portraits (80x72, 16 colors, index 0 transparent) from the FE8 decomp graphics and the FE8 ROM tile maps.

usage: fe8_portrait.py FE8_DECOMP_DIR FE8_ROM OUT_DIR
Writes OUT_DIR/<Name>/full.png (80x72 indexed), back.png (64x64 crop used for pictures), normal.pal, shiny.pal (JASC).
FE8 art is not committed to the repo."""
import os, sys, struct, re, glob
import numpy as np
from PIL import Image
D, ROM, OUT = sys.argv[1:4]
rom = open(ROM, 'rb').read()
RAISED = {'Lute', 'Amelia', 'Ewan', 'Dozla', 'Myrrh'}
def tsa(off):
    d = rom[off:off + 0xB8]; w, h = d[0] + 1, d[1] + 1
    ents = struct.unpack_from('<%dH' % (w * h), d, 2)
    rows = [ents[i * w:(i + 1) * w] for i in range(h)][::-1]     # stored bottom-up
    return w, h, rows
def pal_of(path):
    d = open(path, 'rb').read()[:32]
    return [(((v := struct.unpack_from('<H', d, i)[0]) & 31) * 8, ((v >> 5) & 31) * 8, ((v >> 10) & 31) * 8) for i in range(0, 32, 2)]
def jasc(p): return 'JASC-PAL\n0100\n16\n' + '\n'.join('%d %d %d' % c for c in p) + '\n'
def shiny(p):
    return [(c[1], c[2], c[0]) if i else c for i, c in enumerate(p)]
names = sorted(set(re.match(r'portrait_(.*)_tileset\.png', os.path.basename(f)).group(1) for f in glob.glob(f'{D}/graphics/portrait/portrait_*_tileset.png')))
for n in names:
    ts = np.array(Image.open(f'{D}/graphics/portrait/portrait_{n}_tileset.png').convert('P'))
    w, h, rows = tsa(0x5A08F0 if n in RAISED else 0x5A0838)
    img = np.zeros((h * 8, w * 8), np.uint8)
    for y, r in enumerate(rows):
        for x, v in enumerate(r):
            t = v & 0x3FF; tx, ty = (t % 32) * 8, (t // 32) * 8
            tile = ts[ty:ty + 8, tx:tx + 8]
            if v & 0x400: tile = tile[:, ::-1]
            if v & 0x800: tile = tile[::-1, :]
            img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = tile
    pal = pal_of(f'{D}/graphics/portrait/portrait_{n}_palette.agbpal')
    od = os.path.join(OUT, n); os.makedirs(od, exist_ok=True)
    def save(arr, name, p):
        im = Image.fromarray(arr, 'P'); q = [v for c in p for v in c]; im.putpalette(q + [0] * (768 - len(q))); im.save(os.path.join(od, name), transparency=0)
    save(img, 'full.png', pal)
    crop = np.zeros((64, 64), np.uint8); crop[:] = img[0:64, 8:72]
    save(crop, 'back.png', pal)
    open(os.path.join(od, 'normal.pal'), 'w').write(jasc(pal)); open(os.path.join(od, 'shiny.pal'), 'w').write(jasc(shiny(pal)))
print(len(names), 'portraits')
