#!/usr/bin/env python3
"""Leg9: Renais Castle, Frelia Castle, Jehanna Hall and Black Temple story maps built with tools/indoor_tiling.py
(FE8 floor and walls, FireRed furniture lifted onto the FE8 floor). Fort Rigwald and the Grado Throne Room stay on the
FireRed League donor interiors (tools/leg7_donor_maps.py). No furniture is cropped from FE8 backdrops.
Usage: leg9_indoor_maps.py DECOMP_DIR   (run on a tree that already went through leg4, leg5 and leg7 scripts)
Env: POKEFIRERED, FE8_DECOMP as for indoor_tiling.py. Layouts are 15 x 16, door at column 7, same size as before."""
import os, sys, json, re, glob
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indoor_tiling as it

root = Path(sys.argv[1])
DOOR = ["      D        "]

ROOMS = {
 # throne hall: cream wall with windows, shelves, cabinets between FE8 wall ends, red carpet, potted plants
 'Story_RenaisCastle': (11, 'story_renais_castle', [
    "##===========##",
    "##=wwssfxxss=##",
    " ............. ",
    " .p.........p. ",
    " ....ccccc.... "[:15],
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ....ccccc.... ",
    " ............. "] + DOOR,
  {'Guard': (3, 10), 'Guard2': (11, 10), 'Minister': (9, 12), 'Maid': (3, 13), 'Chest': (12, 9)},
  {'Sign0': (5, 1), 'Sign1': (11, 1)}),
 # airy hall: cream centre, council table on a rug island, plants
 'Story_FreliaCastle': (23, 'story_frelia_castle', [
    "###=========###",
    "###=wwssxxf=###",
    " ............. ",
    " ............. ",
    " ...ccccccc... ",
    " ...caTTbcc... ",
    " ...caTTbcc... ",
    " ...ccccccc... ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. ",
    " .p........... ",
    " ............. ",
    " ............. "] + DOOR,
  {'Knight': (3, 9), 'Knight2': (11, 9), 'Page': (4, 13), 'Noble': (10, 13), 'Chest': (3, 14)},
  {'Sign0': (1, 1), 'Sign1': (13, 1)}),
 # stone hall with a dais rug and one window
 'Story_JehannaHall': (37, 'story_jehanna_hall', [
    "######====#####",
    "######=ww=#####"[:15],
    " ............. ",
    " ...ccccccc... ",
    " ...ccccccc... ",
    " ...ccccccc... ",
    " ..pccccccc... ",
    " ...ccccccc... ",
    " ...ccccccc... ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. "] + DOOR,
  {'Sage': (7, 10), 'Warrior': (3, 12), 'Scholar': (11, 12), 'Chest': (12, 14)},
  {'Sign0': (6, 1)}),
 # dark stone temple with an altar table
 'Story_BlackTemple': (51, 'story_black_temple', [
    "#####=====#####",
    "#####=xxf=#####",
    " ............. ",
    " ............. ",
    " ....ccccc.... ",
    " ....caTTb.... ",
    " ....caTTb.... ",
    " ....ccccc.... ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. ",
    " ............. "] + DOOR,
  {'Cultist': (3, 10), 'Cultist2': (11, 12), 'Hermit': (4, 14), 'Chest': (11, 9)},
  {'Sign0': (5, 1)}),
}
# fix rows: every row exactly 15 wide
for k, v in ROOMS.items():
    assert all(len(r) == 15 for r in v[2]), (k, [len(r) for r in v[2]])
    assert len(v[2]) == 16, k

reg0 = None
rules_p = root / 'tileset_rules.mk'
rules = rules_p.read_text()
for mapdir, (seed, tsdir, layout, npcs, signs) in ROOMS.items():
    res = it.autotile(layout, seed=seed)
    t = root / 'data/tilesets/secondary' / tsdir
    for f in glob.glob(str(t / 'tiles.4bpp*')) + glob.glob(str(t / 'palettes/*.gbapal')): os.remove(f)
    nt, nmeta = it.emit(res, str(t))
    # emit wrote tiles.png, palettes, metatiles.bin, metatile_attributes.bin, map.bin, border.bin, room.json into t
    ldir = root / 'data/layouts' / mapdir
    (ldir / 'map.bin').write_bytes((t / 'map.bin').read_bytes()); (ldir / 'border.bin').write_bytes((t / 'border.bin').read_bytes())
    for extra in ('map.bin', 'border.bin', 'room.json'): (t / extra).unlink()
    pat = re.compile(r'(secondary/%s/tiles\.4bpp: %%\.4bpp: %%\.png\n\t\$\(GFX\) \$< \$@ -num_tiles )\d+' % tsdir)
    assert pat.search(rules), tsdir
    rules = pat.sub(lambda m: m.group(1) + str(nt), rules)
    # object events and signs on valid cells; the walk in (7,14) up to (7,11) and the mat must stay clear
    ids, coll, lay = res['ids'], res['coll'], res['layout']
    mj = json.loads((root / 'data/maps' / mapdir / 'map.json').read_text())
    taken = set()
    for o in mj['object_events']:
        nm = o['script'].split('_EventScript_')[1]
        x, y = npcs[nm]
        assert lay[y][x] in '.c' and not coll[y][x] and (x, y) not in taken, (mapdir, nm, x, y)
        assert not (x == 7 and 11 <= y <= 15), (mapdir, nm)
        taken.add((x, y)); o['x'], o['y'] = x, y
    for o in mj['bg_events']:
        nm = o['script'].split('_EventScript_')[1]
        x, y = signs[nm]
        assert coll[y][x] and lay[y + 1][x] == '.' and y == 1, (mapdir, nm)
        o['x'], o['y'] = x, y
    assert len(mj['bg_events']) == len(signs)
    mj['warp_events'] = [{'x': 7, 'y': 14, 'elevation': 0, 'dest_map': 'MAP_PALLET_TOWN', 'dest_warp_id': '0'}]
    (root / 'data/maps' / mapdir / 'map.json').write_text(json.dumps(mj, indent=2) + '\n')
    print(mapdir, 'tiles', nt, 'metatiles', nmeta, it.count_sources(res))
rules_p.write_text(rules)
lj = root / 'data/layouts/layouts.json'; lj.write_text(lj.read_text())     # touch so make rebuilds the layout data
