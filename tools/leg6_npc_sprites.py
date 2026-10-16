#!/usr/bin/env python3
"""Build FireRed overworld sheets (144x32, 9 frames of 16x32) from FE8 class map sprites, one per character.
Usage: leg6_npc_sprites.py FE8_DECOMP_DIR OUT_DIR [--sheet]
Writes OUT_DIR/<name>.png (8-bit palette, index 0 transparent) and OUT_DIR/<name>.pal (JASC).
FE8 sheet (32x32 frames): 0-3 side (faces right), 4-7 down, 8-11 up. Frame order out: S, N, W, S1, S2, N1, N2, W1, W2.
Each direction is centred on the body of its standing frame and cut to 16 wide; sprites wider than 18 px are shrunk
to fit (nearest neighbour) so riders, wyverns and weapons are not sliced off."""
import sys
from PIL import Image, ImageOps
CHARS = {  # name: FE8 map sprite class
 'ephraim': 'Ephraim_Lord', 'moulder': 'Priest', 'lyon': 'Prince', 'valter': 'Wyvern_Knight', 'syrene': 'Falcon_Knight',
 'selena': 'Mercenary_F', 'binks': 'Sniper', 'seth': 'Paladin', 'marisa': 'Myrmidon_F', 'gilliam': 'Armor_Knight',
 'vanessa': 'Pegasus_Knight', 'colm': 'Thief', 'lute': 'Mage_F', 'garcia': 'Fighter', 'vigarde': 'General',
 'ismaire': 'Civilian_F1', 'hayden': 'Civilian_M1',
 'fe8_soldier': 'Soldier', 'fe8_peer': 'Peer', 'fe8_sage': 'Sage', 'fe8_shaman': 'Shaman', 'fe8_monk': 'Monk',
 'fe8_mercenary': 'Mercenary', 'fe8_cleric': 'Cleric', 'fe8_civilian_f': 'Civilian_F2', 'fe8_civilian_m': 'Civilian_M2',
 'fe8_knight': 'Armor_Knight', 'fe8_cavalier': 'Cavalier', 'fe8_druid': 'Druid',
}
def frames(path):
    sh = Image.open(path); assert sh.mode == 'P'
    return sh, [sh.crop((0, k*32, 32, k*32+32)) for k in range(12)]
def body_box(f):
    return f.point(lambda v: 255 if v else 0).getbbox()
def fit(f, ref_box, scale):
    if scale < 1:
        w = max(1, round(32*scale)); f = f.resize((w, w), Image.NEAREST)
        canvas = Image.new('P', (32, 32), 0); canvas.putpalette(f.getpalette())
        canvas.paste(f, ((32-w)//2, 32-w)); f = canvas
    return f
def build(path):
    sh, fr = frames(path)
    out = Image.new('P', (144, 32), 0); out.putpalette(sh.getpalette())
    def dirframes(base, mirror):
        fs = fr[base:base+4]
        boxes = [body_box(f) for f in fs if body_box(f)]
        w = max(b[2]-b[0] for b in boxes)
        scale = 1.0 if w <= 18 else 16.0/w if w <= 32 else 0.5
        scale = min(1.0, 16.0/w) if w > 18 else 1.0
        fs = [fit(f, None, scale) for f in fs]
        boxes = [body_box(f) for f in fs if body_box(f)]
        cx = (min(b[0] for b in boxes) + max(b[2] for b in boxes)) // 2
        x0 = max(0, min(16, cx-8))
        res = [f.crop((x0, 0, x0+16, 32)) for f in fs]
        return [ImageOps.mirror(r) for r in res] if mirror else res
    side = dirframes(0, True); down = dirframes(4, False); up = dirframes(8, False)
    seq = [down[0], up[0], side[0], down[1], down[3], up[1], up[3], side[1], side[3]]
    for i, f in enumerate(seq): out.paste(f, (i*16, 0))
    return out
def pal_text(img):
    p = img.getpalette()[:48]
    return 'JASC-PAL\r\n0100\r\n16\r\n' + ''.join('%d %d %d\r\n' % tuple(p[i*3:i*3+3]) for i in range(16))
if __name__ == '__main__':
    fe8, outd = sys.argv[1:3]
    import os; os.makedirs(outd, exist_ok=True)
    imgs = {}
    for n, c in CHARS.items():
        img = build(f'{fe8}/graphics/unit_icon/move/unit_icon_move_{c}_sheet.png')
        img.save(f'{outd}/{n}.png'); open(f'{outd}/{n}.pal', 'w').write(pal_text(img)); imgs[n] = img
    if '--sheet' in sys.argv:
        names = list(CHARS); sheet = Image.new('RGB', (144*2+8, 36*((len(names)+1)//2)), (60, 120, 60))
        for i, n in enumerate(names):
            im = imgs[n].convert('RGBA'); m = imgs[n].point(lambda v: 255 if v else 0)
            sheet.paste(imgs[n].convert('RGB'), ((i%2)*(144+8), (i//2)*36), m)
        sheet = sheet.resize((sheet.width*3, sheet.height*3), Image.NEAREST); sheet.save(f'{outd}/contact.png')
