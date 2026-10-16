#!/usr/bin/env python3
"""Add NPCs, treasure objects, readable features and collision to the six story maps.
Usage: leg5_story_map_objects.py DECOMP_DIR     (run after leg4_story_tilesets.py; idempotent)
Collision: map.bin cells get collision bit (0x0C00) for blocked cells. Objects use elevation 3 like the map blocks.
Items use unused FLAG_HIDDEN_ITEM_UNUSED_* flags as the object hide flag."""
import sys, json, struct, re
from pathlib import Path
root = Path(sys.argv[1])
EDGE = lambda lo, hi: [(x, y) for y in range(8, 16) for x in range(0, 15) if x <= lo or x >= hi]
MAPS = {
 'Story_RenaisCastle': dict(
   block=EDGE(1, 13) + [(7, 9), (7, 10), (6, 9), (8, 9)],
   npcs=[('POLICEMAN', 4, 10, 'FACE_DOWN', 'Guard', 'RENAIS GUARD: Renais Castle is\\nsafe, Princess. The King awaits.'),
         ('POLICEMAN', 10, 10, 'FACE_DOWN', 'Guard2', 'RENAIS GUARD: Grado soldiers\\nare at our gates. Please be\\ncareful out there.'),
         ('OLD_MAN_1', 9, 12, 'WANDER_AROUND', 'Minister', 'MINISTER: Your father spoke of\\nyou often. Keep your resolve.'),
         ('WOMAN_1', 3, 13, 'WANDER_AROUND', 'Maid', 'MAID: Prince Ephraim trains\\nin the courtyard every dawn.')],
   items=[('ITEM_RARE_CANDY', 12, 9, 'FLAG_HIDDEN_ITEM_UNUSED_0x07', 'Chest')],
   signs=[(7, 7, 'The royal altar of Renais.\\pKing Fado once knelt here.'), (3, 7, 'A banner of Renais.\\nIt shows the white lion.')]),
 'Story_FreliaCastle': dict(
   block=EDGE(1, 13) + [(2, y) for y in range(8, 12)] + [(12, y) for y in range(8, 12)],
   npcs=[('MAN', 5, 9, 'FACE_DOWN', 'Knight', 'FRELIAN KNIGHT: Welcome to\\nCastle Frelia. Princess Ismaire\\nwill see you shortly.'),
         ('MAN', 9, 9, 'FACE_DOWN', 'Knight2', 'FRELIAN KNIGHT: Our knights\\nstand with Renais.'),
         ('LASS', 4, 13, 'WANDER_AROUND', 'Page', 'PAGE: The garden is lovely\\nthis time of year.'),
         ('GENTLEMAN', 10, 13, 'WANDER_AROUND', 'Noble', 'NOBLE: Prince Innes is a fine\\narcher, they say.')],
   items=[('ITEM_FULL_RESTORE', 3, 14, 'FLAG_HIDDEN_ITEM_UNUSED_0x10', 'Chest')],
   signs=[(6, 7, 'A castle window. Beyond it\\nlie the green fields of Frelia.'), (10, 7, 'A castle window. Beyond it\\nlie the green fields of Frelia.')]),
 'Story_JehannaHall': dict(
   block=EDGE(1, 13) + [(3, y) for y in range(8, 14)] + [(11, y) for y in range(8, 14)],
   npcs=[('CHANNELER', 7, 10, 'FACE_DOWN', 'Sage', 'SAGE: Jehanna Hall keeps the\\nsands of the desert at bay.'),
         ('BLACK_BELT', 5, 12, 'FACE_DOWN', 'Warrior', 'JEHANNA WARRIOR: I will not\\nbow to Grado.'),
         ('SCIENTIST', 9, 12, 'WANDER_AROUND', 'Scholar', 'SCHOLAR: These halls hold the\\nrecords of the old kings.')],
   items=[('ITEM_MAX_ELIXIR', 12, 14, 'FLAG_HIDDEN_ITEM_UNUSED_0x28', 'Chest')],
   signs=[(7, 7, 'A great dark doorway.\\nCold air drifts out.')]),
 'Story_FortRigwald': dict(
   block=[(x, y) for y in range(8, 16) for x in range(0, 15) if x <= 0 or x >= 8],
   npcs=[('ROCKET_M', 4, 10, 'FACE_DOWN', 'Soldier', 'GRADO SOLDIER: Halt! This is\\nFort Rigwald. State your business.'),
         ('HIKER', 2, 12, 'WANDER_AROUND', 'Scout', 'SCOUT: The cliffs make this fort\\nhard to take.'),
         ('CAMPER', 6, 13, 'FACE_DOWN', 'Recruit', 'RECRUIT: I only wanted to see\\nthe world. Now I hold a spear.')],
   items=[('ITEM_HYPER_POTION', 1, 9, 'FLAG_HIDDEN_ITEM_UNUSED_0x2B', 'Chest')],
   signs=[(5, 7, 'FORT RIGWALD\\nGrado border fortress.')]),
 'Story_GradoThroneRoom': dict(
   block=EDGE(1, 13) + [(6, 8), (7, 8), (8, 8)],
   npcs=[('ROCKET_M', 4, 10, 'FACE_DOWN', 'Guard', 'GRADO GUARD: The Emperor is\\nnot himself of late.'),
         ('ROCKET_M', 10, 10, 'FACE_DOWN', 'Guard2', 'GRADO GUARD: Do not step on\\nthe red carpet uninvited.'),
         ('GENTLEMAN', 7, 10, 'FACE_DOWN', 'Advisor', 'GRADO ADVISOR: Prince Lyon\\nhas changed since the Emperor fell\\nill. I fear for him.'),
         ('SCIENTIST', 12, 13, 'WANDER_AROUND', 'Mage', 'COURT MAGE: Strange magic\\nlingers in this room.')],
   items=[('ITEM_PP_UP', 2, 13, 'FLAG_HIDDEN_ITEM_UNUSED_0x2C', 'Chest')],
   signs=[(7, 7, 'The Grado throne. Its gold\\nfeels cold to the touch.')]),
 'Story_BlackTemple': dict(
   block=EDGE(2, 12),
   npcs=[('CHANNELER', 5, 10, 'FACE_DOWN', 'Cultist', 'CULTIST: The Demon King will\\nrise again.'),
         ('CHANNELER', 9, 12, 'WANDER_AROUND', 'Cultist2', 'CULTIST: You should not have\\ncome here.'),
         ('OLD_MAN_2', 4, 14, 'FACE_DOWN', 'Hermit', 'HERMIT: Four sacred stones sealed\\nthis place long ago.')],
   items=[('ITEM_ELIXIR', 11, 9, 'FLAG_HIDDEN_ITEM_UNUSED_0x2D', 'Chest')],
   signs=[(7, 7, 'An ancient altar. Dark\\nenergy pulses within.')]),
}
for mapdir, d in MAPS.items():
    # collision
    p = root / 'data/layouts' / mapdir / 'map.bin'
    w = 15
    raw = bytearray(p.read_bytes()); vals = list(struct.unpack('<%dH' % (len(raw)//2), raw))
    for i in range(len(vals)): vals[i] &= ~0x0C00      # clear, then rebuild: walls 0..7 blocked, floor open
    for i in range(len(vals)):
        y = i // w
        if y < 8: vals[i] |= 0x0400
    for (x, y) in d['block']: vals[y*w + x] |= 0x0400
    # keep the entry column clear
    for y in range(12, 16): vals[y*w + 7] &= ~0x0C00
    p.write_bytes(struct.pack('<%dH' % len(vals), *vals))
    mj_p = root / 'data/maps' / mapdir / 'map.json'; mj = json.loads(mj_p.read_text())
    objs = []; texts = []; scripts = []
    for g, x, y, mv, nm, txt in d['npcs']:
        lab = '%s_EventScript_%s' % (mapdir, nm)
        objs.append(dict(type='object', graphics_id='OBJ_EVENT_GFX_' + g, x=x, y=y, elevation=3, movement_type='MOVEMENT_TYPE_' + mv,
                         movement_range_x=1, movement_range_y=1, trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0', script=lab, flag='0'))
        scripts.append('%s::\n\tmsgbox %s_Text_%s, MSGBOX_NPC\n\tend\n' % (lab, mapdir, nm)); texts.append((nm, txt))
    for item, x, y, flag, nm in d['items']:
        lab = '%s_EventScript_%s' % (mapdir, nm)
        objs.append(dict(type='object', graphics_id='OBJ_EVENT_GFX_ITEM_BALL', x=x, y=y, elevation=3, movement_type='MOVEMENT_TYPE_LOOK_AROUND' if False else 'MOVEMENT_TYPE_FACE_DOWN',
                         movement_range_x=0, movement_range_y=0, trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0', script=lab, flag=flag))
        scripts.append('%s::\n\tfinditem %s\n\tend\n' % (lab, item))
    bgs = []
    for k, (x, y, txt) in enumerate(d['signs']):
        lab = '%s_EventScript_Sign%d' % (mapdir, k)
        bgs.append(dict(type='sign', x=x, y=y, elevation=3, player_facing_dir='BG_EVENT_PLAYER_FACING_ANY', script=lab))
        scripts.append('%s::\n\tmsgbox %s_Text_Sign%d, MSGBOX_SIGN\n\tend\n' % (lab, mapdir, k)); texts.append(('Sign%d' % k, txt))
    mj['object_events'] = objs; mj['bg_events'] = bgs; mj['coord_events'] = []
    mj_p.write_text(json.dumps(mj, indent=2) + '\n')
    sp = root / 'data/maps' / mapdir / 'scripts.inc'; s = sp.read_text()
    s = s.split('\n@ story objects')[0].rstrip('\n') + '\n\n@ story objects (tools/leg5_story_map_objects.py)\n'
    s += '\n'.join(scripts) + '\n'
    for nm, t in texts:
        s += '%s_Text_%s:\n\t.string "%s$"\n\n' % (mapdir, nm, t.replace('\\p', '\\p'))
    sp.write_text(s)
    print(mapdir, len(objs), 'objects', len(bgs), 'signs', len(d['block']), 'blocked extra')
