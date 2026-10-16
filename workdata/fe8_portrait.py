#!/usr/bin/env python3
"""Assemble FE8 face portraits (80x72) from the decomp tileset PNG + palette + the game's face tilemap.
Usage: fe8_portrait.py <decomp_dir> <fe8_rom> <out_dir> [Name ...]   (no names = every portrait that has a tileset)"""
import re, struct, sys, os
import numpy as np
from PIL import Image

RAISED = {'Lute', 'Amelia', 'Ewan', 'Dozla', 'Myrrh'}   # ShouldFaceBeRaised() in src/face.c

def read_tsa(rom, off):
    b = rom[off:off + 0xB8]
    w, h = b[0] + 1, b[1] + 1
    return w, h, struct.unpack_from('<%dH' % (w * h), b, 2)

def palette(path):
    d = open(path, 'rb').read()
    out = []
    for i in range(0, 32, 2):
        v = struct.unpack_from('<H', d, i)[0]
        out.append(((v & 31) * 8, ((v >> 5) & 31) * 8, ((v >> 10) & 31) * 8))
    return np.array(out, np.uint8)

def render(name, gdir, rom, mouth_xy):
    sheet = np.array(Image.open(f'{gdir}/portrait_{name}_tileset.png').convert('P'))   # 32 rows x 256 cols, indices
    pal = palette(f'{gdir}/portrait_{name}_palette.agbpal')
    off = 0x5A08F0 if name in RAISED else 0x5A0838
    w, h, tm = read_tsa(rom, off)
    tm = [tm[(h - 1 - ty) * w + tx] for ty in range(h) for tx in range(w)]   # the ROM stores the TSA bottom-up
    idx = np.zeros((h * 8, w * 8), np.uint8)
    for ty in range(h):
        for tx in range(w):
            n = tm[ty * w + tx] & 0x3FF
            r, c = divmod(n, 32)
            idx[ty*8:ty*8+8, tx*8:tx*8+8] = sheet[r*8:r*8+8, c*8:c*8+8]
    rgba = np.dstack([pal[idx], np.where(idx == 0, 0, 255).astype(np.uint8)])
    return Image.fromarray(rgba, 'RGBA')

def main():
    gdecomp, rompath, out = sys.argv[1:4]; names = sys.argv[4:]
    gdir = f'{gdecomp}/graphics/portrait'
    rom = open(rompath, 'rb').read()
    os.makedirs(out, exist_ok=True)
    mouth = {}
    for m in re.finditer(r'\{portrait_(\w+?)_tileset,[^}]*?,\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*\w+\}', open(f'{gdecomp}/src/portrait_data.c').read()):
        mouth.setdefault(m.group(1), (int(m.group(2)), int(m.group(3))))   # (xMouth, yMouth)
    todo = names or sorted(n for n in mouth if os.path.exists(f'{gdir}/portrait_{n}_tileset.png'))
    done = 0
    for n in todo:
        if n not in mouth: print('skip (not in portrait_data.c):', n); continue
        render(n, gdir, rom, mouth[n]).save(f'{out}/{n}.png'); done += 1
    print('rendered', done, 'portraits to', out)
main()
