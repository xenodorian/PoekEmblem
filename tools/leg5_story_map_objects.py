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
   npcs=[('POLICEMAN', 5, 9, 'FACE_DOWN', 'Knight', 'FRELIAN KNIGHT: Welcome to\\nCastle Frelia. Princess Ismaire\\nwill see you shortly.'),
         ('POLICEMAN', 9, 9, 'FACE_DOWN', 'Knight2', 'FRELIAN KNIGHT: Our knights\\nstand with Renais.'),
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

# Leg17: healer and vendor NPCs. Vendor stock labels are the vanilla FireRed mart lists (global labels in the vanilla
# map scripts), so the inventories are exact copies by reference. Chronological order follows the FireRed route.
# kind: 'heal' | 'mart' (data = list of (prompt, label), several = chained yes/no menu)
SERVICES = {
 'Story_RenaisCastle': [('NURSE', 'Healer', 'heal', None, 'CLERIC: Rest a moment, Princess.\\nLet me tend to your party.'),
                        ('CLERK', 'VendorViridian', 'mart', [('', 'ViridianCity_Mart_Items')], 'VENDOR: The castle stores are\\nopen to you, Princess.'),
                        ('CLERK', 'VendorPewter', 'mart', [('', 'PewterCity_Mart_Items')], 'MERCHANT: Supplies for the road,\\nPrincess?')],
 'Story_FreliaCastle': [('NURSE', 'Healer', 'heal', None, 'FRELIAN CLERIC: You look weary.\\nLet me heal your party.'),
                        ('CLERK', 'VendorCerulean', 'mart', [('', 'CeruleanCity_Mart_Items')], 'FRELIAN QUARTERMASTER: Take what\\nyou need for the march.'),
                        ('CLERK', 'VendorVermilion', 'mart', [('', 'VermilionCity_Mart_Items')], 'TRADER: Goods from the ports.')],
 'Story_FortRigwald': [('NURSE', 'Healer', 'heal', None, 'FIELD CLERIC: Hold still. I will\\nmend your party.'),
                       ('CLERK', 'VendorLavender', 'mart', [('', 'LavenderTown_Mart_Items')], 'SUTLER: Rations and remedies.'),
                       ('CLERK', 'VendorCeladon2F', 'mart', [('', 'CeladonCity_DepartmentStore_2F_Items')], 'ARMORY CLERK: Fort stores,\\nfreshly stocked.')],
 'Story_JehannaHall': [('NURSE', 'Healer', 'heal', None, 'PRIEST: The desert sun is cruel.\\nLet me heal your party.'),
                       ('CLERK', 'VendorCeladonBig', 'mart',
                        [('Care to see the vitamins?', 'CeladonCity_DepartmentStore_5F_Vitamins'),
                         ('How about battle items?', 'CeladonCity_DepartmentStore_5F_XItems'),
                         ('Perhaps some TMs?', 'CeladonCity_DepartmentStore_2F_TMs'),
                         ('Or evolution stones?', 'CeladonCity_DepartmentStore_4F_Items')],
                        'GRAND MERCHANT: My stock is vast.\\nVitamins, battle items, TMs, stones.'),
                       ('CLERK', 'VendorFuchsia', 'mart', [('', 'FuchsiaCity_Mart_Items')], 'CARAVAN TRADER: Wares from\\nthe far east.')],
 'Story_GradoThroneRoom': [('NURSE', 'Healer', 'heal', None, 'COURT HEALER: Even in this hall,\\nI can mend your party.'),
                           ('CLERK', 'VendorSaffron', 'mart', [('', 'SaffronCity_Mart_Items')], 'IMPERIAL SUPPLIER: Fine goods\\nfor the discerning.'),
                           ('CLERK', 'VendorCinnabar', 'mart', [('', 'CinnabarIsland_Mart_Items')], 'ARMS DEALER: Only the best.')],
 'Story_BlackTemple': [('NURSE', 'Healer', 'heal', None, 'WANDERING PRIEST: Light still\\nburns here. Let me heal you.'),
                       ('CLERK', 'VendorIndigo', 'mart', [('', 'IndigoPlateau_PokemonCenter_1F_Items')], 'LAST MERCHANT: The final stock\\nbefore the end.'),
                       ('CLERK', 'VendorSeven', 'mart', [('', 'SevenIsland_Mart_Items')], 'RELIC DEALER: Rare goods,\\nfair prices.')],
}
sys.path.insert(0, str(Path(__file__).parent))
from leg6_props import block_cells
BG = {'Story_RenaisCastle': 'bg_Renais_Chamber', 'Story_FreliaCastle': 'bg_Castle_Interior', 'Story_JehannaHall': 'bg_White_Chamber',
      'Story_FortRigwald': 'bg_Fort', 'Story_GradoThroneRoom': 'bg_Throne_Normal', 'Story_BlackTemple': 'bg_Black_Temple_Inside'}
for mapdir, d in MAPS.items():
    d['block'] = list(d['block']) + [c for c in block_cells(BG[mapdir]) if 0 <= c[0] < 15 and c[1] < 16 and c[0] != 7]
    fixed = []
    taken = set(d['block']) | {(i[1], i[2]) for i in d['items']}
    for n in d['npcs']:      # move an NPC off a blocked cell to the nearest free walkable cell
        x, y = n[1], n[2]
        if (x, y) in taken:
            cand = sorted(((abs(cx-x)+abs(cy-y), cx, cy) for cx in range(1, 14) for cy in range(9, 16) if (cx, cy) not in taken and cx != 7))
            x, y = cand[0][1], cand[0][2]
        taken.add((x, y)); fixed.append((n[0], x, y) + tuple(n[3:]))
    d['npcs'] = fixed
    # Leg17 services: place on nearest free cell, keep every walkable cell reachable from the entry (7,15)
    def reachable(blocked):
        seen = {(7, 15)}; st = [(7, 15)]
        while st:
            cx, cy = st.pop()
            for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                if 0 <= nx < 15 and 8 <= ny < 16 and (nx, ny) not in seen and (nx, ny) not in blocked:
                    seen.add((nx, ny)); st.append((nx, ny))
        return seen
    d['services'] = []
    pref = [(2, 9), (12, 9), (3, 11), (11, 11)]
    for k, sv in enumerate(SERVICES[mapdir]):
        gfx, nm, kind, data, txt = sv
        objset = {(n[1], n[2]) for n in d['npcs']} | {(i[1], i[2]) for i in d['items']} | {(q[0], q[1]) for q in d['services']}
        free0 = reachable(set(d['block']) | objset)
        px, py = pref[k % len(pref)]
        cand = sorted(((abs(cx-px)+abs(cy-py), cx, cy) for (cx, cy) in free0 if cx != 7 and (cx, cy) not in objset and cy <= 14))
        for _, cx, cy in cand:
            blk = set(d['block']) | objset | {(cx, cy)}
            r = reachable(blk)
            if len(r) == len(free0) - 1 and all(((n[1], n[2]) in objset) for n in d['npcs']):
                d['services'].append((cx, cy, gfx, nm, kind, data, txt)); break
        else:
            raise SystemExit('no cell for service %s on %s' % (nm, mapdir))
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
    for cx, cy, gfx, nm, kind, data, txt in d['services']:
        lab = '%s_EventScript_%s' % (mapdir, nm)
        objs.append(dict(type='object', graphics_id='OBJ_EVENT_GFX_' + gfx, x=cx, y=cy, elevation=3, movement_type='MOVEMENT_TYPE_FACE_DOWN',
                         movement_range_x=0, movement_range_y=0, trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0', script=lab, flag='0'))
        if kind == 'heal':
            T = '%s_Text_%s' % (mapdir, nm)
            scripts.append('%s::\n\tlock\n\tfaceplayer\n\tmsgbox %s, MSGBOX_DEFAULT\n\tmsgbox %s_HealAsk, MSGBOX_YESNO\n'
                           '\tcompare VAR_RESULT, 0\n\tgoto_if_eq %s_Heal_No\n\tspecial HealPlayerParty\n\tplayfanfare MUS_HEAL\n\twaitfanfare\n'
                           '\tmsgbox %s_Healed, MSGBOX_DEFAULT\n\trelease\n\tend\n\n%s_Heal_No:\n\tmsgbox %s_HealNo, MSGBOX_DEFAULT\n\trelease\n\tend\n'
                           % (lab, T, T, lab, T, lab, T))
            texts += [(nm, txt), (nm + '_HealAsk', 'Shall I heal your party?'), (nm + '_Healed', 'Your party is fully healed.\\nGo with courage, Princess.'),
                      (nm + '_HealNo', 'Take care out there.')]
        else:
            T = '%s_Text_%s' % (mapdir, nm)
            body = '%s::\n\tlock\n\tfaceplayer\n\tmsgbox %s_Text_%s, MSGBOX_DEFAULT\n' % (lab, mapdir, nm)
            tl = [(nm, txt)]
            for j, (prompt, lbl) in enumerate(data):
                if prompt:
                    body += '\tmsgbox %s_Ask%d, MSGBOX_YESNO\n\tcompare VAR_RESULT, 0\n\tgoto_if_eq %s_Next%d\n' % (T, j, lab, j)
                    tl.append((nm + '_Ask%d' % j, prompt))
                body += '\tmessage Text_MayIHelpYou\n\twaitmessage\n\tpokemart %s\n\tmsgbox Text_PleaseComeAgain, MSGBOX_DEFAULT\n\trelease\n\tend\n' % lbl
                if prompt: body += '%s_Next%d:\n' % (lab, j)
            body += '\tmsgbox %s_Bye, MSGBOX_DEFAULT\n\trelease\n\tend\n' % T if len(data) > 1 else ''
            if len(data) > 1: tl.append((nm + '_Bye', 'Come back any time.'))
            scripts.append(body); texts += tl
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
