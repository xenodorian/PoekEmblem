#!/usr/bin/env python3
"""Offline render of all six story maps (four autotiled rooms from tools/leg9_indoor_maps.py plus the two FireRed League donor
layouts), with an audit of wall style and wall/floor width. Usage: render_story_maps.py DECOMP_DIR OUT.png
Env: POKEFIRERED, FE8_DECOMP as for indoor_tiling.py."""
import os, sys, struct
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indoor_tiling as it
from PIL import Image, ImageDraw

def load_ts(d):
    d = Path(d); raw = (d / 'tiles.4bpp').read_bytes() if (d / 'tiles.4bpp').exists() else None
    mb = (d / 'metatiles.bin').read_bytes()
    return dict(raw=raw, meta=[struct.unpack('<8H', mb[i*16:i*16+16]) for i in range(len(mb)//16)],
                pals=[it.read_pal(str(d / ('palettes/%02d.pal' % i))) if (d / ('palettes/%02d.pal' % i)).exists() else [(0, 0, 0)] * 16 for i in range(16)])

def tile_px(ts, i):
    b = ts['raw'][i*32:i*32+32]; px = []
    for v in b: px += [v & 15, v >> 4]
    return px

def render_donor(root, layout_dir, prim, sec):
    P = load_ts(root / 'data/tilesets/primary' / prim); S = load_ts(root / 'data/tilesets/secondary' / sec)
    W, H = {'PokemonLeague_BrunosRoom': (13, 13), 'PokemonLeague_ChampionsRoom': (13, 20)}[layout_dir]
    mp = struct.unpack('<%dH' % (W*H), (root / 'data/layouts' / layout_dir / 'map.bin').read_bytes())
    im = Image.new('RGB', (W*16, H*16))
    for y in range(H):
        for x in range(W):
            bid = mp[y*W+x] & 0x3ff
            ents = P['meta'][bid] if bid < 640 else S['meta'][bid-640]
            cell = Image.new('RGBA', (16, 16), (0, 0, 0, 255))
            for layer in (0, 1):
                for k in range(4):
                    e = ents[layer*4+k]; t, pal, hf, vf = e & 0x3ff, e >> 12, (e >> 10) & 1, (e >> 11) & 1
                    ts = P if t < 640 else S; px = tile_px(ts, t if t < 640 else t-640)
                    pl = (P if pal < 7 else S)['pals'][pal]
                    tile = Image.new('RGBA', (8, 8)); data = []
                    for yy in range(8):
                        for xx in range(8):
                            v = px[(7-yy if vf else yy)*8 + (7-xx if hf else xx)]
                            data.append((0, 0, 0, 0) if (v == 0 and layer == 1) else it.q5(pl[v]) + (255,))
                    tile.putdata(data); cell.alpha_composite(tile, ((k % 2)*8, (k//2)*8))
            im.paste(cell.convert('RGB'), (x*16, y*16))
    return im

if __name__ == '__main__':
    root = Path(sys.argv[1]); out = sys.argv[2]
    src = open(os.path.join(os.path.dirname(__file__), 'leg9_indoor_maps.py')).read().split('reg0 = None')[0].replace('root = Path(sys.argv[1])', 'root = None')
    ns = {'__name__': 'x', '__file__': os.path.abspath(__file__)}; sys.argv = ['x', str(root)]; exec(compile(src, 'leg9', 'exec'), ns)
    tiles = []
    for name, (seed, ts, lay, npcs, signs) in ns['ROOMS'].items():
        r = it.autotile(lay, seed=seed)       # autotile() runs validate(): single wall style, wall width == floor width
        walls = {c for row in lay for c in row if c in it.WALL_CH}
        print(name, 'ok: wall style', 'FE8 brick' if '#' in walls else 'FireRed cream', 'floor cols', sorted({x for row in lay for x, c in enumerate(row) if c in it.FLOORISH})[::12])
        tiles.append((name, it.render(r, 3)))
    for name, d in (('Story_FortRigwald (donor Bruno room)', 'PokemonLeague_BrunosRoom'), ('Story_GradoThroneRoom (donor Champion room)', 'PokemonLeague_ChampionsRoom')):
        tiles.append((name, render_donor(root, d, 'building', 'pokemon_league').resize((13*48, {'PokemonLeague_BrunosRoom': 13, 'PokemonLeague_ChampionsRoom': 20}[d]*48), Image.NEAREST)))
    pad = 20; Wt = sum(t.width for _, t in tiles) + pad*(len(tiles)+1); Ht = max(t.height for _, t in tiles) + 50
    sheet = Image.new('RGB', (Wt, Ht), (24, 24, 24)); d = ImageDraw.Draw(sheet); x = pad
    for n, t in tiles:
        sheet.paste(t, (x, 40)); d.text((x, 10), n.replace('Story_', ''), fill=(255, 255, 255)); x += t.width + pad
    sheet.save(out); print('wrote', out)
