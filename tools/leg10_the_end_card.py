#!/usr/bin/env python3
"""Leg10: render the THE END title card (240x160, FE8 style: navy banded sky, gold serif lettering with dark outline,
ornament rules) and convert it to GBA BG data: 4bpp tiles (deduplicated, no flips), a 32x32 tilemap and a 16 colour palette.
Usage: leg10_the_end_card.py OUT_DIR   writes the_end_card.png, .4bpp, .bin (tilemap) and .gbapal into OUT_DIR
Nothing is cropped from FE8 and no FE8 art is used, only a design in the same look. Deterministic."""
import sys, os, struct
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
W, H = 240, 160
# palette (16): 0..5 navy bands (top dark to bottom lighter), 6 black outline, 7 gold dark, 8 gold, 9 gold light, 10 cream, 11 white, 12 rule blue, 13 star, 14 shadow, 15 mid navy
PAL = [(8,12,40),(12,18,56),(16,26,72),(22,36,92),(30,48,112),(40,62,132),
       (8,6,16),(150,98,24),(214,160,40),(252,224,120),(248,240,208),(255,255,255),(88,112,176),(200,216,248),(4,6,20),(20,30,80)]
img = Image.new('P', (W, H), 0)
pl = []
for c in PAL: pl += list(c)
img.putpalette(pl + [0]*(768-len(pl)))
d = ImageDraw.Draw(img)
# banded sky (8 px steps so tiles dedupe)
for y in range(H): d.line((0, y, W, y), fill=min(5, y * 6 // H))
# stars on fixed cells
for i, (x, y) in enumerate([(18,14),(52,30),(96,10),(150,22),(204,12),(226,40),(30,120),(70,140),(180,134),(214,110),(130,146),(10,70),(232,86)]):
    d.point((x, y), fill=13)
    if i % 3 == 0: d.point((x-1, y), fill=12); d.point((x+1, y), fill=12); d.point((x, y-1), fill=12); d.point((x, y+1), fill=12)
# border frame: double gold rule with corner diamonds
d.rectangle((4, 4, W-5, H-5), outline=7); d.rectangle((6, 6, W-7, H-7), outline=8)
for (x, y) in ((6,6),(W-7,6),(6,H-7),(W-7,H-7)):
    d.polygon([(x, y-4), (x+4, y), (x, y+4), (x-4, y)], fill=9, outline=7)
def font(path, size):
    return ImageFont.truetype(path, size)
SER = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
def mask(text, f):
    m = Image.new('1', (W, H), 0); ImageDraw.Draw(m).text((0, 0), text, font=f, fill=1)
    return m
def lettering(text, f, cy, fills):
    """gold lettering: 1px dark outline, 1px shadow, vertical 3 step gradient"""
    bb = f.getbbox(text); tw = bb[2] - bb[0]; th = bb[3] - bb[1]
    x0 = (W - tw) // 2 - bb[0]; y0 = cy - th // 2 - bb[1]
    m = Image.new('1', (W, H), 0); ImageDraw.Draw(m).text((x0, y0), text, font=f, fill=1)
    px = m.load()
    ys = [y for y in range(H) for x in range(W) if px[x, y]]
    top, bot = min(ys), max(ys)
    for y in range(H):
        for x in range(W):
            if px[x, y]:
                t = (y - top) / max(1, bot - top)
                d.point((x+1, y+1), fill=14)   # shadow, overdrawn below
    # outline
    for y in range(H):
        for x in range(W):
            if px[x, y]: continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    xx, yy = x+dx, y+dy
                    if 0 <= xx < W and 0 <= yy < H and px[xx, yy]: d.point((x, y), fill=6); break
                else: continue
                break
    for y in range(H):
        for x in range(W):
            if px[x, y]:
                t = (y - top) / max(1, bot - top)
                d.point((x, y), fill=fills[0] if t < 0.4 else fills[1] if t < 0.75 else fills[2])
    return top, bot
def rule(y, half):
    d.line((W//2 - half, y, W//2 + half, y), fill=8); d.line((W//2 - half, y+1, W//2 + half, y+1), fill=7)
    d.polygon([(W//2, y-3), (W//2+4, y+1), (W//2, y+5), (W//2-4, y+1)], fill=9, outline=6)
t1, b1 = lettering('THE SACRED STONES', font(SER, 13), 34, (10, 9, 8))
rule(50, 84)
t2, b2 = lettering('THE END', font(SER, 34), 82, (9, 8, 7))
rule(110, 84)
f3 = font('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 11)
lettering('Thank you for playing.', f3, 130, (11, 10, 10))
img.save(os.path.join(out, 'the_end_card.png'))
# tiles
px = img.load(); tiles = []; index = {}; tmap = [[0]*32 for _ in range(32)]
for ty in range(H // 8):
    for tx in range(W // 8):
        t = bytes(px[tx*8 + x, ty*8 + y] for y in range(8) for x in range(8))
        if t not in index: index[t] = len(tiles); tiles.append(t)
        tmap[ty][tx] = index[t]
assert len(tiles) <= 900, len(tiles)
raw = bytearray()
for t in tiles:
    for y in range(8):
        for x in range(0, 8, 2): raw.append(t[y*8+x] | (t[y*8+x+1] << 4))
open(os.path.join(out, 'the_end_card.4bpp'), 'wb').write(raw)
open(os.path.join(out, 'the_end_card.bin'), 'wb').write(b''.join(struct.pack('<H', v) for row in tmap for v in row))
open(os.path.join(out, 'the_end_card.gbapal'), 'wb').write(b''.join(struct.pack('<H', (r>>3) | ((g>>3)<<5) | ((b>>3)<<10)) for r, g, b in PAL))
print('tiles', len(tiles))
