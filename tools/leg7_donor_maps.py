#!/usr/bin/env python3
"""Owner rule: where FE8 backdrops look rough, use existing FireRed interiors. Switches Fort Rigwald and the Grado Throne Room
story maps to the Pokemon League interior layouts (Bruno's room, Champion's room; gTileset_PokemonLeague), moves their NPCs and
item to walkable cells, drops the backdrop signs, and hides the map name popup on all six story maps (it showed donor names such
as SILPH CO. 11F). Usage: leg7_donor_maps.py DECOMP_DIR   (run after leg4_story_tilesets.py and leg5_story_map_objects.py)"""
import sys, json
from pathlib import Path
root = Path(sys.argv[1])
SWITCH = {
 'Story_FortRigwald': ('PokemonLeague_BrunosRoom', (6, 10),
     {'Soldier': (4, 8), 'Scout': (9, 6), 'Recruit': (3, 4), 'Chest': (11, 4)}),
 'Story_BlackTemple': ('PokemonTower_6F', (11, 16),
     {'Cultist': (8, 6), 'Cultist2': (16, 8), 'Hermit': (4, 8), 'Chest': (3, 6)}),
 'Story_GradoThroneRoom': ('PokemonLeague_ChampionsRoom', (6, 18),
     {'Guard': (4, 6), 'Guard2': (8, 6), 'Advisor': (6, 9), 'Mage': (10, 11), 'Chest': (1, 12)}),
}
for m in ['Story_RenaisCastle', 'Story_FreliaCastle', 'Story_JehannaHall', 'Story_FortRigwald', 'Story_GradoThroneRoom', 'Story_BlackTemple']:
    p = root / 'data/maps' / m / 'map.json'; j = json.loads(p.read_text())
    j['show_map_name'] = False
    if m in SWITCH:
        donor, (ex, ey), pos = SWITCH[m]
        j['layout'] = json.loads((root / 'data/maps' / donor / 'map.json').read_text())['layout']
        for o in j['object_events']:
            nm = o['script'].split('_EventScript_')[1]
            o['x'], o['y'] = pos[nm]
        j['bg_events'] = []
        j['warp_events'] = [{'x': ex, 'y': ey, 'elevation': 0, 'dest_map': 'MAP_PALLET_TOWN', 'dest_warp_id': '0'}]
    p.write_text(json.dumps(j, indent=2) + '\n')
    print(m, j['layout'])
