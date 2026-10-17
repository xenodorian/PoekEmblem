#!/usr/bin/env python3
"""Owner rule: where FE8 backdrops look rough, use existing FireRed interiors. Switches Fort Rigwald and the Grado Throne Room
story maps to the Pokemon League interior layouts (Bruno's room, Champion's room; gTileset_PokemonLeague), moves their NPCs and
item to walkable cells, drops the backdrop signs, and hides the map name popup on all six story maps (it showed donor names such
as SILPH CO. 11F). Usage: leg7_donor_maps.py DECOMP_DIR   (run after leg4_story_tilesets.py and leg5_story_map_objects.py)"""
import sys, json
from pathlib import Path
root = Path(sys.argv[1])
# Leg17: Black Temple is no longer switched to the Pokemon Tower donor here (tools/leg9_indoor_maps.py autotiles it and undid the switch anyway).
SWITCH = {
 'Story_FortRigwald': ('PokemonLeague_BrunosRoom', (6, 10),
     {'Soldier': (4, 8), 'Scout': (9, 6), 'Recruit': (3, 4), 'Chest': (11, 4)}),
 'Story_GradoThroneRoom': ('PokemonLeague_ChampionsRoom', (6, 18),
     {'Guard': (4, 6), 'Guard2': (8, 6), 'Advisor': (6, 9), 'Mage': (10, 11), 'Chest': (1, 12)}),
}
for m in ['Story_RenaisCastle', 'Story_FreliaCastle', 'Story_JehannaHall', 'Story_FortRigwald', 'Story_GradoThroneRoom', 'Story_BlackTemple']:
    p = root / 'data/maps' / m / 'map.json'; j = json.loads(p.read_text())
    j['show_map_name'] = False
    if m in SWITCH:
        donor, (ex, ey), pos = SWITCH[m]
        j['layout'] = json.loads((root / 'data/maps' / donor / 'map.json').read_text())['layout']
        lj_ = json.loads((root / 'data/layouts/layouts.json').read_text())['layouts']
        lay_ = [l for l in lj_ if l.get('id') == j['layout']][0]
        W_, H_ = lay_['width'], lay_['height']
        import struct
        raw_ = (root / lay_['blockdata_filepath']).read_bytes()
        col_ = [v & 0x0C00 for v in struct.unpack('<%dH' % (len(raw_) // 2), raw_)]
        def reach_(blocked):
            seen = {(ex, ey)}; st = [(ex, ey)]
            while st:
                cx, cy = st.pop()
                for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                    if 0 <= nx < W_ and 0 <= ny < H_ and (nx, ny) not in seen and not col_[ny*W_+nx] and (nx, ny) not in blocked:
                        seen.add((nx, ny)); st.append((nx, ny))
            return seen
        taken_ = set()
        for o in j['object_events']:
            nm = o['script'].split('_EventScript_')[1]
            if nm in pos:
                o['x'], o['y'] = pos[nm]; taken_.add(pos[nm])
        for o in j['object_events']:       # Leg17 service NPCs: auto place on a reachable cell, entry lane (column ex, 4 rows up) kept clear
            nm = o['script'].split('_EventScript_')[1]
            if nm in pos: continue
            free0 = reach_(taken_)
            ty_ = sum(v[1] for v in pos.values()) // len(pos); tx_ = sum(v[0] for v in pos.values()) // len(pos)
            cand = sorted(((abs(cx-tx_) + abs(cy-ty_), cx, cy) for (cx, cy) in free0
                           if (cx, cy) not in taken_ and not (cx == ex and ey-4 <= cy <= ey) and (cx, cy) != (ex, ey) and cy < ey-1))
            for _, cx, cy in cand:
                if len(reach_(taken_ | {(cx, cy)})) == len(free0) - 1:
                    o['x'], o['y'] = cx, cy; taken_.add((cx, cy)); break
            else:
                raise SystemExit('no cell for ' + nm)
        j['bg_events'] = []
        j['warp_events'] = [{'x': ex, 'y': ey, 'elevation': 0, 'dest_map': 'MAP_PALLET_TOWN', 'dest_warp_id': '0'}]
    p.write_text(json.dumps(j, indent=2) + '\n')
    print(m, j['layout'])
