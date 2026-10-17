#!/usr/bin/env python3
"""Offline map grid reader for the pokefirered decomp tree (Leg19). Used by leg19_gates.py and the playthrough harness.
grid(root, 'Route1') -> dict(w, h, coll[y][x], elev[y][x], beh[y][x], terrain[y][x], enc[y][x], objs{(x,y)}, warps)"""
import json, re, struct
from pathlib import Path
_cache = {}
def _attrs(root, tsname):
    hs = (root / 'src/data/tilesets/headers.h').read_text()
    m = re.search(r'const struct Tileset %s =\s*\{.*?\.metatileAttributes = (\w+),' % tsname, hs, re.S)
    ms = (root / 'src/data/tilesets/metatiles.h').read_text()
    p = re.search(r'%s\[\] = INCBIN_U32\("([^"]+)"\)' % m.group(1), ms).group(1)
    raw = (root / p).read_bytes()
    return struct.unpack('<%dI' % (len(raw) // 4), raw)
def grid(root, mapname):
    root = Path(root); key = (str(root), mapname)
    if key in _cache: return _cache[key]
    mj = json.loads((root / 'data/maps' / mapname / 'map.json').read_text())
    lays = json.loads((root / 'data/layouts/layouts.json').read_text())['layouts']
    lay = [l for l in lays if l.get('id') == mj['layout']][0]
    w, h = lay['width'], lay['height']
    raw = (root / lay['blockdata_filepath']).read_bytes()
    vals = struct.unpack('<%dH' % (len(raw) // 2), raw)
    pa = _attrs(root, lay['primary_tileset']); sa = _attrs(root, lay['secondary_tileset'])
    coll = [[0] * w for _ in range(h)]; elev = [[0] * w for _ in range(h)]
    beh = [[0] * w for _ in range(h)]; ter = [[0] * w for _ in range(h)]; enc = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            v = vals[y * w + x]; mid = v & 0x3FF
            a = pa[mid] if mid < 640 else (sa[mid - 640] if mid - 640 < len(sa) else 0)
            coll[y][x] = (v >> 10) & 3; elev[y][x] = v >> 12
            beh[y][x] = a & 0x1FF; ter[y][x] = (a >> 9) & 0x1F; enc[y][x] = (a >> 24) & 7
    objs = {(o['x'], o['y']) for o in mj.get('object_events', [])}
    g = dict(w=w, h=h, coll=coll, elev=elev, beh=beh, terrain=ter, enc=enc, objs=objs, warps=mj.get('warp_events', []), mj=mj)
    _cache[key] = g; return g
OK_WALK = {0x00, 0x02, 0x03, 0x08, 0x21}   # normal ground, tall grass, long grass, cave floor, sand (anything else is not planned through)
def walkable(g, x, y):
    return 0 <= x < g['w'] and 0 <= y < g['h'] and g['coll'][y][x] == 0 and g['beh'][y][x] in OK_WALK and g['terrain'][y][x] == 0
def bfs(g, start, blocked=()):
    from collections import deque
    dist = {start: 0}; q = deque([start]); par = {start: None}
    while q:
        c = q.popleft()
        for dx, dy, k in ((0, -1, 'U'), (0, 1, 'D'), (-1, 0, 'L'), (1, 0, 'R')):
            n = (c[0] + dx, c[1] + dy)
            if n in dist or n in blocked or n in g['objs'] or not walkable(g, *n): continue
            dist[n] = dist[c] + 1; par[n] = (c, k); q.append(n)
    return dist, par
def path(par, goal):
    out = []; c = goal
    while par.get(c):
        c, k = par[c][0], par[c][1]; out.append(k)
    return out[::-1]
