#!/usr/bin/env python3
"""Make Eirika versions of the Leaf bike, surf, fishing, item and VS Seeker bike overworld sheets.
Usage: leg5_eirika_vehicles.py PEOPLE_DIR   (dir holds eirika_normal.png; writes eirika_*.png with the same palette)
Base frames come from eirika_normal.png (9 frames 16x32: 0 S,1 N,2 W,3-4 walk S,5-6 walk N,7-8 walk W).
Extra props (wheels, rod, hand) are drawn with palette entries 15 (dark) and 4 (gray) and 13 (grey-green)."""
import sys
from PIL import Image, ImageDraw
d = sys.argv[1].rstrip('/') + '/'
base = Image.open(d + 'eirika_normal.png')
pal = base.getpalette()
def fr(k): return base.crop((k*16, 0, k*16+16, 32))
def newsheet(w): 
    im = Image.new('P', (w, 32), 0); im.putpalette(pal); return im
DARK, GRAY = 15, 4
def put(im, f, x, y):
    # paste with index 0 transparent
    m = Image.new('L', f.size); m.putdata([255 if v else 0 for v in f.get_flattened_data()] if hasattr(f,'get_flattened_data') else [255 if v else 0 for v in f.getdata()])
    im.paste(f, (x, y), m)
# item / field move: Eirika facing south for all frames, last frames show a raised hand (skin-like entry 6)
item = newsheet(144)
for i in range(9):
    f = fr(0).copy()
    if i >= 4:
        px = f.load()
        for yy in range(12 - min(i-4, 3), 17):
            px[13, yy] = 6   # raised arm on her right side
            px[14, yy] = 4
    item.paste(f, (i*16, 0)) if False else put(item, f, i*16, 0)
item.save(d + 'eirika_item.png')
# surf: seated frames S, N, W repeated to 14 frames of 16x32
surf = newsheet(224)
order = [0, 1, 2, 0, 0, 1, 1, 2, 2, 0, 1, 2, 0, 0]
for i, k in enumerate(order): put(surf, fr(k), i*16, 0)
surf.save(d + 'eirika_surf_run.png')
# bike: 9 frames 32x32
def bike_frame(k, step):
    im = Image.new('P', (32, 32), 0); im.putpalette(pal)
    dr = ImageDraw.Draw(im)
    side = k in (2, 7, 8)
    f = fr(k)
    if side:
        put(im, f, 8, -3)
        for cx in (9, 22):
            dr.ellipse((cx-4, 22, cx+4, 30), outline=DARK)
            dr.point((cx, 26), fill=GRAY)
        dr.line((9, 26, 17, 21), fill=DARK); dr.line((17, 21, 22, 26), fill=DARK); dr.line((18, 20, 21, 20), fill=GRAY)
    else:
        put(im, f, 8, -3)
        dr.line((15, 29, 15, 31), fill=DARK); dr.line((16, 29, 16, 31), fill=DARK)
        dr.line((11, 23, 20, 23), fill=GRAY)
    return im
bike = newsheet(288)
for k in range(9): bike.paste(bike_frame(k, 0), (k*32, 0))
bike.save(d + 'eirika_bike.png')
vs = newsheet(192)
for k in range(6): vs.paste(bike_frame([0,1,2,3,5,7][k], 0), (k*32, 0))
vs.save(d + 'eirika_vs_seeker_bike.png')
# fishing: 12 frames 32x32; dirs S(0-3) N(4-7) W(8-11); 4 stages: rod raised, rod forward, rod cast, line out
fish = newsheet(384)
for dirn, k in enumerate((0, 1, 2)):
    for st in range(4):
        im = Image.new('P', (32, 32), 0); im.putpalette(pal)
        put(im, fr(k), 8, 0)
        dr = ImageDraw.Draw(im)
        if k == 2:   # west: rod to the left
            hx, hy = 10, 16
            tips = [(3, 4), (1, 9), (0, 14), (0, 18)]
        elif k == 0:
            hx, hy = 22, 16
            tips = [(28, 4), (30, 9), (31, 13), (31, 17)]
        else:
            hx, hy = 22, 12
            tips = [(28, 2), (29, 4), (30, 7), (31, 10)]
        dr.line((hx, hy, *tips[st]), fill=DARK)
        if st == 3:
            dr.line((*tips[st], tips[st][0], min(31, tips[st][1]+10)), fill=GRAY)
        fish.paste(im, ((dirn*4+st)*32, 0))
fish.save(d + 'eirika_fish.png')
