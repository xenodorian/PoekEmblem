#!/usr/bin/env python3
"""Add the six story maps to the decomp as clones of existing interiors (no NPCs, warps kept).
Usage: leg3_custom_maps.py DECOMP_DIR. Idempotent. Maps are appended to the last map group so existing map numbers do not change."""
import json, re, sys
from pathlib import Path
root = Path(sys.argv[1])
MAPS = [  # (new name, source map)
 ('Story_RenaisCastle', 'SilphCo_11F'),
 ('Story_FreliaCastle', 'CeladonCity_Condominiums_1F'),
 ('Story_JehannaHall', 'PokemonLeague_LoreleisRoom'),
 ('Story_FortRigwald', 'RocketHideout_B1F'),
 ('Story_GradoThroneRoom', 'PokemonLeague_ChampionsRoom'),
 ('Story_BlackTemple', 'PokemonTower_6F'),
]
def const(n): return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', n).upper().replace('__', '_')
lay = json.loads((root/'data/layouts/layouts.json').read_text())
grp = json.loads((root/'data/maps/map_groups.json').read_text())
ev = (root/'data/event_scripts.s').read_text()
for new, src in MAPS:
    j = json.loads((root/('data/maps/%s/map.json' % src)).read_text())
    nid = 'MAP_' + const(new); lid = 'LAYOUT_' + const(new)
    sl = next(l for l in lay['layouts'] if l.get('id') == j['layout'])
    if not any(l.get('id') == lid for l in lay['layouts']):
        nl = dict(sl); nl['id'] = lid; nl['name'] = new + '_Layout'; lay['layouts'].append(nl)
    j.update(id=nid, name=new, layout=lid, show_map_name=True, object_events=[], coord_events=[], bg_events=[], connections=None)
    d = root/('data/maps/%s' % new); d.mkdir(exist_ok=True)
    (d/'map.json').write_text(json.dumps(j, indent=2) + '\n')
    (d/'scripts.inc').write_text('%s_MapScripts::\n\t.byte 0\n' % new)
    if new not in grp['gMapGroup_IndoorSevenIslandRoute']: grp['gMapGroup_IndoorSevenIslandRoute'].append(new)
    inc = '\t.include "data/maps/%s/scripts.inc"\n' % new
    if inc not in ev: ev = ev.replace('\t.include "data/maps/PalletTown/scripts.inc"\n', '\t.include "data/maps/PalletTown/scripts.inc"\n' + inc, 1)
(root/'data/layouts/layouts.json').write_text(json.dumps(lay, indent=2) + '\n')
(root/'data/maps/map_groups.json').write_text(json.dumps(grp, indent=2) + '\n')
(root/'data/event_scripts.s').write_text(ev)
print('maps added', len(MAPS))
