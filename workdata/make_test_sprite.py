#!/usr/bin/env python3
"""Write a FE8 portrait into a FireRed species slot as an indexed back.png plus palette files.
usage: make_test_sprite.py <fe8_graphics_portrait_dir> <Name> <species_dir> [x0 [y0]]
   Crops a 64x64 window from the 80x72 portrait. x0 defaults to 8 (centered).
   y0 defaults to an automatic vertical crop: remove as many empty rows above the head as possible (max 8),
   then take whatever is left of the 8 rows to remove from the bottom."""
import sys, struct, numpy as np
from PIL import Image
gdir, name, sdir = sys.argv[1:4]
x0 = int(sys.argv[4]) if len(sys.argv) > 4 else 8
y0_arg = int(sys.argv[5]) if len(sys.argv) > 5 else None
d = open(f'{gdir}/portrait_{name}_palette.agbpal', 'rb').read()
pal = [(((v:=struct.unpack_from('<H', d, i)[0]) & 31) * 8, ((v >> 5) & 31) * 8, ((v >> 10) & 31) * 8) for i in range(0, 32, 2)]
sys.path.insert(0, '/tmp/claude-0/-home-user-PoekEmblem/27b9bd3f-f2d5-5a88-ab9b-85e258b1a44c/scratchpad')
# 80x72 index image straight from the assembler's logic
import importlib.util, re, os
spec = importlib.util.spec_from_file_location('p', '/tmp/claude-0/-home-user-PoekEmblem/27b9bd3f-f2d5-5a88-ab9b-85e258b1a44c/scratchpad/fe8_portrait.py')
src = open(spec.origin).read().replace('\nmain()\n', '\n')
ns = {}; exec(compile(src, 'p', 'exec'), ns)
rom = open('/home/user/PoekEmblem/Fire Emblem - The Sacred Stones (USA, Australia).gba', 'rb').read()
dec = '/home/user/fireemblemuniverse/fireemblem8u'
mouth = {}
for m in re.finditer(r'\{portrait_(\w+?)_tileset,[^}]*?,\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*\w+\}', open(f'{dec}/src/portrait_data.c').read()):
    mouth.setdefault(m.group(1), (int(m.group(2)), int(m.group(3))))
rgba = np.array(ns['render'](name, gdir, rom, mouth[name]))
# back to palette indices: transparent -> 0, else nearest palette entry
idx = np.zeros(rgba.shape[:2], np.uint8)
parr = np.array(pal, int)
for y in range(rgba.shape[0]):
    for x in range(rgba.shape[1]):
        if rgba[y, x, 3] == 0: continue
        idx[y, x] = int(np.abs(parr - rgba[y, x, :3].astype(int)).sum(1).argmin())
def save(arr, path):
    im = Image.fromarray(arr, 'P'); flat = [c for rgb in pal for c in rgb] + [0] * (768 - 48); im.putpalette(flat); im.save(path)
if y0_arg is None:
    nonempty = (idx != 0).any(1)
    top_empty = int(np.argmax(nonempty)) if nonempty.any() else 0
    y0 = min(top_empty, idx.shape[0] - 64, 8)          # empty rows above the head go first, max 8
else:
    y0 = y0_arg
print('top empty rows:', top_empty if y0_arg is None else 'n/a', '| cut from top:', y0, '| cut from bottom:', idx.shape[0] - 64 - y0)
crop = idx[y0:y0 + 64, x0:x0 + 64]
save(crop, f'{sdir}/back.png')
save(idx, f'{sdir}/../_portrait_{name}_80x72.png') if os.path.isdir(f'{sdir}/..') else None
jasc = 'JASC-PAL\n0100\n16\n' + ''.join('%d %d %d\n' % c for c in pal)
for f in ('normal.pal', 'shiny.pal'): open(f'{sdir}/{f}', 'w').write(jasc)
print('wrote', sdir, 'crop', (x0, y0, x0 + 64, y0 + 64), 'index image', idx.shape)
