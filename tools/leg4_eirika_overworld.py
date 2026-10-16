#!/usr/bin/env python3
"""Build Eirika's overworld walking sheet (144x32, 9 frames of 16x32) and palette from the FE8 map-unit sheet.
Usage: leg4_eirika_overworld.py FE8_DECOMP_DIR OUT_PNG OUT_PAL
FE8 sheet unit_icon_move_Eirika_Lord_sheet.png is 32x32 frames: 0-3 side (faces right), 4-7 down, 8-11 up, 12-14 idle.
FireRed order: 0 face S, 1 face N, 2 face W, 3-4 walk S, 5-6 walk N, 7-8 walk W (east is a flip of west)."""
import sys
from PIL import Image, ImageOps
fe8, out_png, out_pal = sys.argv[1:4]
sh = Image.open(fe8 + '/graphics/unit_icon/move/unit_icon_move_Eirika_Lord_sheet.png')
assert sh.mode == 'P'
def fr(k): return sh.crop((0, k*32, 32, k*32+32))
def cut(f, x0):
    # 16 wide window from x0, content bottom row 31 kept
    return f.crop((x0, 0, x0+16, 32))
side = lambda k: ImageOps.mirror(cut(fr(k), 12))      # side frames face right, mirror for west
down = lambda k: cut(fr(4+k), 9)
up   = lambda k: cut(fr(8+k), 7)
frames = [down(0), up(0), side(0), down(1), down(3), up(1), up(3), side(1), side(3)]
out = Image.new('P', (144, 32), 0); out.putpalette(sh.getpalette())
for i, f in enumerate(frames): out.paste(f, (i*16, 0))
out.save(out_png)
pal = sh.getpalette()[:48]
open(out_pal, 'w').write('JASC-PAL\r\n0100\r\n16\r\n' + ''.join('%d %d %d\r\n' % tuple(pal[i*3:i*3+3]) for i in range(16)))
