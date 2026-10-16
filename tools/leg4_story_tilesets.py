#!/usr/bin/env python3
"""Turn FE8 story backdrops into six real FireRed map tilesets and layouts.
Usage: leg4_story_tilesets.py FE8_DECOMP_DIR DECOMP_DIR
Each map is the 240x160 FE8 backdrop (15x10 metatiles) plus extra floor rows made by repeating the bottom row.
Rows >= FLOOR_ROW are walkable. Secondary tileset: blank tile + up to 383 tiles, 6 palettes (slots 7-12, 15 colours each)."""
import sys, json, struct, re, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
fe8, root = Path(sys.argv[1]), Path(sys.argv[2])
EXTRA = 6; FLOOR_ROW = 8
sys.path.insert(0, str(Path(__file__).parent))
from leg6_props import PROPS
from PIL import ImageOps
import os; FLOOR_MODE = os.environ.get('FLOOR_MODE', 'repeat')
ROOMS = [  # map dir, tileset dir, C name, FE8 backdrop
 ('Story_RenaisCastle', 'story_renais_castle', 'StoryRenaisCastle', 'bg_Renais_Chamber', 'LAYOUT_STORY_RENAIS_CASTLE'),
 ('Story_FreliaCastle', 'story_frelia_castle', 'StoryFreliaCastle', 'bg_Castle_Interior', 'LAYOUT_STORY_FRELIA_CASTLE'),
 ('Story_JehannaHall', 'story_jehanna_hall', 'StoryJehannaHall', 'bg_White_Chamber', 'LAYOUT_STORY_JEHANNA_HALL'),
 ('Story_FortRigwald', 'story_fort_rigwald', 'StoryFortRigwald', 'bg_Fort', 'LAYOUT_STORY_FORT_RIGWALD'),
 ('Story_GradoThroneRoom', 'story_grado_throne_room', 'StoryGradoThroneRoom', 'bg_Throne_Normal', 'LAYOUT_STORY_GRADO_THRONE_ROOM'),
 ('Story_BlackTemple', 'story_black_temple', 'StoryBlackTemple', 'bg_Black_Temple_Inside', 'LAYOUT_STORY_BLACK_TEMPLE'),
]
NPAL = 6; MAXT = 383
rng = np.random.default_rng(1)

def q5(c): return (np.asarray(c) // 8) * 8 + np.asarray(c) // 32   # expand 5 bit to 8 bit like the GBA shows
def pal_from(pixels):
    im = Image.new('RGB', (len(pixels), 1)); im.putdata([tuple(p) for p in pixels])
    qi = im.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    p = np.array(qi.getpalette()[:45]).reshape(-1, 3)
    if len(p) < 15: p = np.vstack([p, np.zeros((15 - len(p), 3), int)])
    return (p // 8) * 8
def build(name, mapdir, tsdir, cname, bg, layout):
    img = Image.open(fe8 / 'graphics/bg' / (bg + '.png')).convert('RGB')
    assert img.size == (240, 160)
    # keep the top 112 px, stretch the bottom 48 px (floor) to 144 px so the floor gets deeper
    ext = Image.new('RGB', (240, 160 + 16*EXTRA)); ext.paste(img.crop((0, 0, 240, 112)), (0, 0))
    if FLOOR_MODE == 'repeat':   # keep the original floor, then repeat its 16 px row 8 so the floor stays clean and tile friendly
        ext.paste(img.crop((0, 112, 240, 144)), (0, 112))
        band = img.crop((0, 128, 240, 144))
        for k in range(7): ext.paste(band, (0, 144 + 16*k))
    else:
        ext.paste(img.crop((0, 112, 240, 160)).resize((240, 48 + 16*EXTRA), Image.Resampling.NEAREST), (0, 112))
    if os.environ.get('PROPS', '1') == '1':   # furniture crops from the same backdrop, pasted into the floor
        for (r, (dx, dy), mir) in PROPS.get(bg, []):
            c = img.crop(r)
            ext.paste(ImageOps.mirror(c) if mir else c, (dx, dy))
    a = np.asarray(ext).astype(int)
    H, W = a.shape[0] // 8, 30
    tiles = a.reshape(H, 8, W, 8, 3).transpose(0, 2, 1, 3, 4).reshape(H*W, 64, 3)
    uniq, inv = np.unique(tiles.reshape(len(tiles), -1), axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    ut = uniq.reshape(-1, 64, 3); cnt = np.bincount(inv)
    # initial grouping by mean colour (kmeans)
    feat = np.hstack([ut.mean(1), ut.std(1)])
    cen = feat[rng.choice(len(feat), NPAL, replace=False)]
    for _ in range(25):
        grp = ((feat[:, None] - cen[None])**2).sum(2).argmin(1)
        for k in range(NPAL):
            m = grp == k
            if m.any(): cen[k] = (feat[m] * cnt[m, None]).sum(0) / cnt[m].sum()
    for it in range(4):
        pals = []
        for k in range(NPAL):
            m = grp == k
            px = np.repeat(ut[m].reshape(-1, 3), np.repeat(cnt[m], 64), axis=0) if m.any() else np.zeros((1, 3))
            if len(px) > 20000: px = px[rng.choice(len(px), 20000, replace=False)]
            pals.append(pal_from(px))
        pals = np.array(pals)             # NPAL x 15 x 3
        # best palette and indices for each unique tile
        best = None
        errs = np.zeros((len(ut), NPAL)); idxs = np.zeros((len(ut), NPAL, 64), int)
        for k in range(NPAL):
            d = ((ut[:, :, None, :] - pals[k][None, None])**2).sum(3)
            idxs[:, k] = d.argmin(2); errs[:, k] = d.min(2).sum(1)
        grp = errs.argmin(1)
    ti = idxs[np.arange(len(ut)), grp] + 1       # 1..15, index 0 reserved
    recon = pals[grp[:, None], ti - 1]            # reconstructed colours
    # dedupe on (group, indices), then merge closest until <= MAXT
    keys = {}; remap = np.zeros(len(ut), int); items = []
    for i in range(len(ut)):
        key = (grp[i], ti[i].tobytes())
        if key not in keys: keys[key] = len(items); items.append(i)
        remap[i] = keys[key]
    use = np.zeros(len(items)); np.add.at(use, remap, cnt)
    print(name, 'tiles', len(ut), 'unique after palette', len(items))
    alive = list(range(len(items))); parent = list(range(len(items)))
    rec = np.array([recon[i] for i in items], dtype=float)   # n x 64 x 3
    g = np.array([grp[i] for i in items])
    while len(alive) > MAXT:
        al = np.array(alive); bestd = 1e18; bp = None
        for k in range(NPAL):
            s = al[g[al] == k]
            if len(s) < 2: continue
            r = rec[s].reshape(len(s), -1)
            d = ((r[:, None] - r[None])**2).sum(2) * (use[s][:, None] * use[s][None]) / (use[s][:, None] + use[s][None])
            np.fill_diagonal(d, 1e18); j = np.unravel_index(d.argmin(), d.shape)
            if d[j] < bestd: bestd = d[j]; bp = (s[j[0]], s[j[1]])
        a_, b_ = bp
        if use[a_] < use[b_]: a_, b_ = b_, a_
        parent[b_] = a_; use[a_] += use[b_]; alive.remove(b_)
    def root_of(x):
        while parent[x] != x: x = parent[x]
        return x
    final = {r: n + 1 for n, r in enumerate(alive)}   # local tile 0 is blank
    tile_local = np.array([final[root_of(remap[i])] for i in range(len(ut))])
    tile_pal = np.array([g[root_of(remap[i])] for i in range(len(ut))])
    ntiles = len(alive) + 1
    # tile sheet 128 wide
    rows = (ntiles + 15) // 16
    sheet = np.zeros((rows * 8, 128), np.uint8)
    for r_, n in final.items():
        d = ti[items[r_]].reshape(8, 8)
        sheet[(n // 16)*8:(n // 16)*8 + 8, (n % 16)*8:(n % 16)*8 + 8] = d
    sim = Image.fromarray(sheet, 'P')
    pl = []
    for k in range(16):
        col = [(0, 0, 0)] + [tuple(int(v) for v in c) for c in (pals[k] if k < NPAL else np.zeros((15, 3), int))]
        pl.append(col)
    sim.putpalette([v for c in pl[0] for v in c]); 
    tdir = root / 'data/tilesets/secondary' / tsdir; (tdir / 'palettes').mkdir(parents=True, exist_ok=True)
    sim.save(tdir / 'tiles.png')
    for k in range(16):    # absolute palette numbers 7..12 hold the six palettes
        idx = k - 7
        col = pl[idx] if 0 <= idx < NPAL else [(0, 0, 0)] * 16
        (tdir / 'palettes' / ('%02d.pal' % k)).write_text('JASC-PAL\r\n0100\r\n16\r\n' + ''.join('%d %d %d\r\n' % c for c in col))
    # metatiles
    tl = tile_local[inv].reshape(H, W); tp = tile_pal[inv].reshape(H, W)
    mt = {}; mlist = []; cells = np.zeros((H // 2, W // 2), int)
    blank = (0x280 + 0) | (7 << 12)
    for y in range(H // 2):
        for x in range(W // 2):
            ents = []
            for dy in (0, 1):
                for dx in (0, 1):
                    ents.append((0x280 + int(tl[2*y+dy, 2*x+dx])) | ((7 + int(tp[2*y+dy, 2*x+dx])) << 12))
            ents += [blank] * 4
            k = tuple(ents)
            if k not in mt: mt[k] = len(mlist); mlist.append(k)
            cells[y, x] = mt[k]
    assert len(mlist) <= 384, len(mlist)
    (tdir / 'metatiles.bin').write_bytes(b''.join(struct.pack('<8H', *m) for m in mlist))
    (tdir / 'metatile_attributes.bin').write_bytes(b'\0\0\0\0' * len(mlist))
    # layout
    mw, mh = W // 2, H // 2
    ldir = root / 'data/layouts' / mapdir; ldir.mkdir(parents=True, exist_ok=True)
    mp = []
    for y in range(mh):
        for x in range(mw):
            coll = 0 if (y >= FLOOR_ROW and 0 < x < mw - 1) else 1
            mp.append((0x280 + int(cells[y, x])) | (coll << 10) | (3 << 12))
    (ldir / 'map.bin').write_bytes(struct.pack('<%dH' % len(mp), *mp))
    b0 = 0x280 + int(cells[mh - 1, mw // 2])
    (ldir / 'border.bin').write_bytes(struct.pack('<4H', b0, b0, b0, b0))
    print(name, 'tiles', ntiles, 'metatiles', len(mlist), 'map', mw, mh)
    return mw, mh, ntiles

lay = json.loads((root / 'data/layouts/layouts.json').read_text())
gfx = (root / 'src/data/tilesets/graphics.h').read_text(); hd = (root / 'src/data/tilesets/headers.h').read_text()
mh_ = (root / 'src/data/tilesets/metatiles.h').read_text(); rules = (root / 'tileset_rules.mk').read_text()
for mapdir, tsdir, cname, bg, lid in ROOMS:
    mw, mh, nt = build(mapdir, mapdir, tsdir, cname, bg, lid)
    for l in lay['layouts']:
        if l.get('id') == lid:
            l.update(width=mw, height=mh, secondary_tileset='gTileset_' + cname,
                     border_filepath='data/layouts/%s/border.bin' % mapdir, blockdata_filepath='data/layouts/%s/map.bin' % mapdir)
    if 'gTilesetTiles_' + cname + '[]' not in gfx:
        gfx += '\nconst u32 gTilesetTiles_%s[] = INCBIN_U32("data/tilesets/secondary/%s/tiles.4bpp.lz");\n\nconst u16 gTilesetPalettes_%s[][16] =\n{\n%s};\n' % (
            cname, tsdir, cname, ''.join('\tINCBIN_U16("data/tilesets/secondary/%s/palettes/%02d.gbapal"),\n' % (tsdir, k) for k in range(16)))
        hd += '\nconst struct Tileset gTileset_%s =\n{\n    .isCompressed = TRUE,\n    .isSecondary = TRUE,\n    .tiles = gTilesetTiles_%s,\n    .palettes = gTilesetPalettes_%s,\n    .metatiles = gMetatiles_%s,\n    .metatileAttributes = gMetatileAttributes_%s,\n    .callback = NULL,\n};\n' % ((cname,) * 5)
        mh_ += '\nconst u16 gMetatiles_%s[] = INCBIN_U16("data/tilesets/secondary/%s/metatiles.bin");\nconst u32 gMetatileAttributes_%s[] = INCBIN_U32("data/tilesets/secondary/%s/metatile_attributes.bin");\n' % (cname, tsdir, cname, tsdir)
        rules += '\n$(TILESETGFXDIR)/secondary/%s/tiles.4bpp: %%.4bpp: %%.png\n\t$(GFX) $< $@ -num_tiles %d -Wnum_tiles\n' % (tsdir, nt)
    # map events: one exit warp at the bottom centre, nothing else
    mj = json.loads((root / 'data/maps' / mapdir / 'map.json').read_text())
    mj['object_events'] = []; mj['bg_events'] = []; mj['coord_events'] = []
    mj['warp_events'] = [{'x': mw // 2, 'y': mh - 1, 'elevation': 0, 'dest_map': 'MAP_PALLET_TOWN', 'dest_warp_id': '0'}]
    (root / 'data/maps' / mapdir / 'map.json').write_text(json.dumps(mj, indent=2) + '\n')
(root / 'data/layouts/layouts.json').write_text(json.dumps(lay, indent=2) + '\n')
(root / 'src/data/tilesets/graphics.h').write_text(gfx); (root / 'src/data/tilesets/headers.h').write_text(hd)
(root / 'src/data/tilesets/metatiles.h').write_text(mh_); (root / 'tileset_rules.mk').write_text(rules)
