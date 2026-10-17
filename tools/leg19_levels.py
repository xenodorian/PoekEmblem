#!/usr/bin/env python3
"""Leg19: wild encounter data per chapter map. Usage: leg19_levels.py DECOMP_DIR [PRISTINE_POKEFIRERED] [OUT_MD]
Vanilla FireRed routes (weighted land average, or water average when a route has no land) are staggered over the chapters
in order of level: for each chapter, in order, the nearest unused vanilla route within MAX_GAP levels of the chapter level.
Chapters without a route get a generated, level appropriate area built from the existing species themes.
The table is written into src/data/wild_encounters.json (FireRed entries only) for the chapter map and docs/LEVEL_CURVE.md.
Maps with no walkable encounter terrain (castle interiors, cities without grass) receive no table (listed as 'none')."""
import sys, json, os, copy
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from level_curve import LV, MAX_GAP
root = Path(sys.argv[1]); pris = Path(sys.argv[2] if len(sys.argv) > 2 else '/workspace/pokefirered')
outmd = Path(sys.argv[3]) if len(sys.argv) > 3 else None
ch = json.load(open(Path(__file__).resolve().parent.parent / 'story/chapters.json'))['chapters']
vj = json.load(open(pris / 'src/data/wild_encounters.json'))
van = {e['map']: e for e in vj['wild_encounter_groups'][0]['encounters'] if e['base_label'].endswith('_FireRed')}
RATES = {'land_mons': [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1], 'water_mons': [60, 30, 5, 4, 1]}
def avg(e, k):
    m = e[k]['mons']; r = RATES[k]
    return sum(r[i] * (x['min_level'] + x['max_level']) / 2 for i, x in enumerate(m)) / sum(r)
def route_avg(e):
    return avg(e, 'land_mons') if 'land_mons' in e else avg(e, 'water_mons')
ROUTES = ['MAP_ROUTE%d' % n for n in list(range(1, 19)) + [22, 23, 24, 25]] + ['MAP_ROUTE21_NORTH']
cand = {m: route_avg(van[m]) for m in ROUTES if m in van and ('land_mons' in van[m] or 'water_mons' in van[m])}
# vanilla route 19/20 are water only; the owner's list excludes them from the land stagger, keep them as a last resort pool
extra = {m: route_avg(van[m]) for m in ('MAP_ROUTE19', 'MAP_ROUTE20') if m in van}
# interiors with no encounter terrain
NOENC = {'MAP_STORY_RENAIS_CASTLE', 'MAP_STORY_FRELIA_CASTLE', 'MAP_STORY_FORT_RIGWALD', 'MAP_STORY_JEHANNA_HALL',
         'MAP_STORY_GRADO_THRONE_ROOM', 'MAP_STORY_BLACK_TEMPLE', 'MAP_PEWTER_CITY', 'MAP_LAVENDER_TOWN', 'MAP_CELADON_CITY', 'MAP_SAFFRON_CITY'}
WATERONLY = {'MAP_VERMILION_CITY', 'MAP_CERULEAN_CITY', 'MAP_PALLET_TOWN', 'MAP_FUCHSIA_CITY', 'MAP_ROUTE19'}
GEN = {  # generated areas by level band: (species, min_level offset, max_level offset), 12 land slots, 5 water slots
 0: [('RATTATA', -2, 0), ('SPEAROW', -2, 0), ('PIDGEY', -2, 0), ('NIDORAN_M', -1, 1), ('NIDORAN_F', -1, 1), ('EKANS', -1, 1), ('MANKEY', 0, 1), ('ODDISH', -1, 1), ('SANDSHREW', -1, 1), ('MEOWTH', -1, 1), ('JIGGLYPUFF', 0, 2), ('PIKACHU', 0, 2)],
 1: [('GEODUDE', -2, 0), ('ZUBAT', -2, 0), ('RHYHORN', -1, 1), ('PONYTA', -1, 1), ('GROWLITHE', -1, 1), ('MACHOP', -1, 1), ('DROWZEE', -1, 1), ('KRABBY', 0, 1), ('BELLSPROUT', -1, 1), ('ABRA', 0, 2), ('MAGNEMITE', 0, 2), ('ONIX', 0, 2)],
 2: [('PIDGEOTTO', -2, 0), ('ARBOK', -1, 0), ('GRAVELER', -1, 0), ('KADABRA', -1, 1), ('HAUNTER', -1, 1), ('GLOOM', -1, 1), ('WEEPINBELL', -1, 1), ('MAROWAK', -1, 1), ('GOLBAT', -1, 1), ('PRIMEAPE', 0, 1), ('ARCANINE', 0, 2), ('SCYTHER', 0, 2)],
 3: [('RAICHU', -2, 0), ('SANDSLASH', -2, 0), ('GOLEM', -1, 0), ('ALAKAZAM', -1, 1), ('GENGAR', -1, 1), ('VICTREEBEL', -1, 1), ('RHYDON', -1, 1), ('MACHOKE', -1, 1), ('DRAGONAIR', -1, 1), ('LAPRAS', 0, 1), ('SNORLAX', 0, 2), ('DRAGONITE', 0, 2)],
}
WATER = [('TENTACOOL', -2, 0), ('KRABBY', -2, 0), ('POLIWAG', -1, 1), ('SHELLDER', -1, 1), ('GOLDEEN', 0, 2)]
WATER_HI = [('TENTACRUEL', -2, 0), ('KINGLER', -2, 0), ('POLIWHIRL', -1, 1), ('CLOYSTER', -1, 1), ('SEAKING', 0, 2)]
def generate(L):
    band = 0 if L < 12 else 1 if L < 26 else 2 if L < 40 else 3
    mk = lambda lst: [dict(min_level=max(2, L + a), max_level=max(2, L + b), species='SPECIES_' + s) for s, a, b in lst]
    return {'land_mons': dict(encounter_rate=10, mons=mk(GEN[band])),
            'water_mons': dict(encounter_rate=2, mons=mk(WATER if L < 30 else WATER_HI))}
used = set(); plan = []
for c in ch:
    i = c['id']; L = LV[i]
    if c['map'] in NOENC:
        plan.append((i, c, L, None, None)); continue
    pool = {m: a for m, a in cand.items() if m not in used}
    best = min(pool, key=lambda m: (abs(pool[m] - L), pool[m])) if pool else None
    if best and abs(pool[best] - L) <= MAX_GAP:
        used.add(best); plan.append((i, c, L, best, pool[best]))
    else:
        plan.append((i, c, L, None, None))
# apply
tree_p = root / 'src/data/wild_encounters.json'; tj = json.loads(tree_p.read_text())
ents = tj['wild_encounter_groups'][0]['encounters']
# idempotent: undo an earlier run (story entries are replaced by the vanilla entry of that map, or dropped)
ents[:] = [van[e['map']] if (e['base_label'].startswith('sStoryChapter') and e['map'] in van) else e for e in ents
           if not (e['base_label'].startswith('sStoryChapter') and e['map'] not in van)]
byfr = {e['map']: k for k, e in enumerate(ents) if e['base_label'].endswith('_FireRed')}
rows = []; done = {}
for i, c, L, rt, ra in plan:
    m = c['map']; src = 'vanilla ' + rt if rt else ('generated' if m not in NOENC else '-')
    note = ''
    if m in NOENC:
        note = 'none (no grass, cave or water terrain)'
    elif m in done:
        note = 'SHARED MAP, keeps chapter %d table' % done[m]
    else:
        if rt:
            body = {k: copy.deepcopy(v) for k, v in van[rt].items() if k not in ('map', 'base_label')}
            if 'water_mons' not in body: body['water_mons'] = generate(L)['water_mons']
        else:
            body = generate(L)
        if m in WATERONLY: body = {k: v for k, v in body.items() if k != 'land_mons'}
        e = dict(map=m, base_label='sStoryChapter%d_FireRed' % i, **body)
        if m in byfr: ents[byfr[m]] = e
        else: ents.append(e); byfr[m] = len(ents) - 1
        done[m] = i; note = 'written'
    rows.append((i, c.get('label', i), c['title'], m, L, src, ra, note))
tree_p.write_text(json.dumps(tj, indent=2) + '\n')
used_routes = sorted(used)
unused = [m for m in cand if m not in used]
if outmd:
    t = ['# Level curve (Leg19)', '',
         'Chapter level table: `tools/level_curve.py` (`LV`). Regular trainers carry two Pokemon at LV-1 and LV (average LV-0.5). Boss trainers carry three Pokemon at LV, LV+1, LV+2 (average LV+1). Partner allies (Seth, Garcia) carry three Pokemon at LV-2, LV-1, LV.',
         'The party is never raised automatically. Levels come only from battles and items (Rare Candy, vitamins are in the shops).', '',
         'Wild tables (`tools/leg19_levels.py`): the vanilla FireRed routes were sorted by their weighted average level and staggered over the chapters in order. For each chapter, the nearest unused route within %.1f levels of the chapter level is copied onto that chapter\'s map (land, water, rock smash and fishing lists, vanilla encounter rates). Chapters with no route in range get a generated area from the existing species themes, level range LV-2 to LV+2.' % MAX_GAP, '',
         'The effect depends on the terrain: grass and cave floor give land encounters, water gives surf and fishing encounters. Castle interiors (Renais, Frelia, Fort Rigwald, Jehanna, Grado, Black Temple) and cities with neither grass nor water (Pewter, Lavender, Celadon, Saffron) have no encounter terrain, so they have no table and do not use up a route. Maps with water only (Vermilion, Cerulean, Pallet, Fuchsia, Route 19) get the water and fishing lists only (land lists are dropped).', '',
         '| Idx | FE8 | Title | Map | Chapter level | Source route | Route avg | Wild table |', '|---|---|---|---|---|---|---|---|']
    for i, lab, title, m, L, src, ra, note in rows:
        t.append('| %d | %s | %s | %s | %d | %s | %s | %s |' % (i, lab, title, m.replace('MAP_', ''), L, src, '%.1f' % ra if ra else '-', note))
    t += ['', 'Vanilla route averages used (weighted by encounter slot, land or water if no land):', '']
    t.append(', '.join('%s %.1f' % (m.replace('MAP_', '').title(), a) for m, a in sorted(cand.items(), key=lambda x: x[1])) + '.')
    t += ['', 'Routes assigned: ' + ', '.join(m.replace('MAP_', '').title() for m in used_routes) + '.',
          'Routes left unassigned (no free chapter within range): ' + (', '.join(m.replace('MAP_', '').title() for m in unused) or 'none') + '.', '']
    outmd.write_text('\n'.join(t) + '\n')
for r in rows: print(r)
