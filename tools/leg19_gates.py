#!/usr/bin/env python3
"""Leg19: choose the walk-back gate for every vanilla chapter map. Usage: leg19_gates.py PRISTINE_POKEFIRERED OUT_JSON
Output story/gates.json: per map id {dir, arrive, gate, elev, guide, dist}. arrive = vanilla first warp (or first object + 1 row)
unless chapters.json gives 'arrive'. gate = a plain ground cell reachable from arrive about 40 steps away (the player must walk
there after a chapter to return to camp). guide = free neighbour cell for the gate guard NPC (a visible signpost)."""
import sys, json, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapgrid
root = Path(sys.argv[1]); out = Path(sys.argv[2])
ch = json.load(open(Path(__file__).resolve().parent.parent / 'story/chapters.json'))['chapters']
dirs = {}
for f in (root / 'data/maps').glob('*/map.json'):
    dirs[json.loads(f.read_text())['id']] = f.parent.name
HUBS = {'MAP_STORY_RENAIS_CASTLE', 'MAP_STORY_FRELIA_CASTLE', 'MAP_STORY_FORT_RIGWALD', 'MAP_STORY_JEHANNA_HALL', 'MAP_STORY_GRADO_THRONE_ROOM', 'MAP_STORY_BLACK_TEMPLE'}
TARGET = 40
res = {}
for c in ch:
    m = c['map']
    if m in HUBS or m in res: continue
    g = mapgrid.grid(root, dirs[m]); mj = g['mj']
    if c.get('arrive'): ax, ay = c['arrive']
    elif mj.get('warp_events'): ax, ay = mj['warp_events'][0]['x'], mj['warp_events'][0]['y']
    else: o = mj['object_events'][0]; ax, ay = o['x'], o['y'] + 1
    dist, par = mapgrid.bfs(g, (ax, ay))
    def nbrs(cell): return [n for n in ((cell[0]+1, cell[1]), (cell[0]-1, cell[1]), (cell[0], cell[1]+1), (cell[0], cell[1]-1)) if n in dist]
    cands = []
    for mind, minn in ((12, 3), (8, 2), (4, 2), (2, 1)):
        for cell, dd in dist.items():
            x, y = cell
            if dd < mind or g['beh'][y][x] not in (0, 8, 0x21) or (g['enc'][y][x] != 0 and g['beh'][y][x] != 8): continue
            if len(nbrs(cell)) < minn or any((w['x'], w['y']) == cell for w in g['warps']): continue
            cands.append((-min(dd, TARGET), abs(dd - TARGET), cell))
        if cands: break
    cands.sort()
    best = cands[0][2]; nb = nbrs(best); guide = max(nb, key=lambda n: dist[n])
    res[m] = dict(dir=dirs[m], arrive=[ax, ay], gate=list(best), elev=g['elev'][best[1]][best[0]], guide=list(guide), dist=dist[best], reachable=len(dist))
    print(m, res[m])
json.dump(res, open(out, 'w'), indent=1); print('ok', len(res))
