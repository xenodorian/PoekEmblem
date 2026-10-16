#!/usr/bin/env python3
"""Leg13: the three optional FE8 dungeons as clones of FireRed donor maps, hooked to a dungeon guide in Pallet Town.
  valni   Tower of Valni   = Pokemon Tower 1F-7F
  lagdou  Lagdou Ruins     = Mt. Moon 1F, B1F, B2F
  melkaen Melkaen Coast    = One Island Kindle Road (coast route)
Usage: leg13_dungeons.py DECOMP_DIR [valni] [lagdou] [melkaen]   (run after leg3_story.py; idempotent, rerun with the full list)
Donor layouts, tilesets, warps, trainers and item balls are reused as is. Donor trainers are re-partied (6 Pokemon or fewer),
donor NPCs on floors that lack trainers become trainers (free TRAINER_RS_* slots), each dungeon gets a boss slot, a completion
flag (FLAG_UNUSED_0x4A7..), a reward, and an entrance behind the Pallet Town dungeon guide (unlocks after FE8 chapter 8).
Donor trainers must not be used by story/chapters.json; if one is, it is replaced by a clone slot. No donor map file is touched."""
import json, os, re, struct, sys, textwrap
from pathlib import Path
from collections import deque

root = Path(sys.argv[1]); want = [a for a in sys.argv[2:]] or ['valni']
here = Path(__file__).resolve().parent
story = json.load(open(here.parent / 'story/chapters.json'))
src3 = (here / 'leg3_story.py').read_text()
exec(src3[src3.index('FAM = {'):src3.index('THEME = {')])          # FAM species families
def pick(theme, lvl, k):
    fam = FAM[theme][k % len(FAM[theme])]; best = fam[0][0]
    for sp, mn in fam:
        if lvl >= mn: best = sp
    return best
def const(n): return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', n).upper().replace('__', '_')
def fmt(t):
    lines = textwrap.wrap(t.replace('’', "'"), 34); s = ''
    for i, l in enumerate(lines):
        s += l.replace('"', '\\"')
        if i < len(lines) - 1: s += '\\n' if i % 2 == 0 else '\\p'
    return s + '$'

reserved = set()
for c in story['chapters']:
    for b in c['battles']:
        for k in ('a', 'b', 'partner'):
            if b.get(k): reserved.add(b[k])
chap_id = {c['label']: c['id'] for c in story['chapters']}
GATE = chap_id['8'] + 1        # VAR_STORY_CHAPTER counts finished chapters: >= GATE means FE8 chapter 8 is done

# ---------------------------------------------------------------- dungeon specs
SPECS = {
 'valni': dict(
   title='Tower of Valni', flag='FLAG_UNUSED_0x4A7', lv0=20, step=1, boss_lv=28, boss_theme='dark', boss_src='TRAINER_ELITE_FOUR_AGATHA',
   themes=['dark'], conv_src='TRAINER_CHANNELER_PATRICIA', conv_gfx='CHANNELER', min_tr=2,
   floors=[('PokemonTower_%dF' % i, 'Story_TowerOfValni_%dF' % i) for i in range(1, 8)],
   entry=0, exits={'MAP_LAVENDER_TOWN'}, boss_floor=6, boss_replace='MR_FUJI',
   reward=('ITEM_RARE_CANDY', 2, 3000),
   intro="Welcome to the Tower of Valni. The dead sleep here. Disturb them and answer to me.",
   defeat="The Tower rests. Take what lies at its top.",
   post="Valni will sleep soundly now. Go in peace.",
   won="The Tower of Valni is cleared. The old wardens leave you a reward.",
   guide="Tower of Valni (Lv 20 to 28)",
   lines=['The old dead do not like visitors.', 'Turn back, or join the Tower.', 'These stairs only go up.'],
   lines_d=['Rest, then.', 'The Tower forgives.', 'So the living are strong.'],
   lines_p=['Mind the upper floors.', 'The master waits at the top.', 'Few climb this far.']),
 'lagdou': dict(
   title='Lagdou Ruins', flag='FLAG_UNUSED_0x4A8', lv0=24, step=3, boss_lv=32, boss_theme='knight', boss_src='TRAINER_ELITE_FOUR_BRUNO',
   themes=['knight', 'mage', 'dark'], conv_src=None, conv_gfx=None, min_tr=0,
   floors=[('MtMoon_1F', 'Story_LagdouRuins_1F'), ('MtMoon_B1F', 'Story_LagdouRuins_B1F'), ('MtMoon_B2F', 'Story_LagdouRuins_B2F')],
   entry=0, exits={'MAP_ROUTE4'}, boss_floor=2, boss_replace='SCIENTIST',
   reward=('ITEM_PP_UP', 2, 4000),
   intro="You walked into the Lagdou Ruins. Nothing leaves these halls unchallenged.",
   defeat="The ruins accept you. Take the old hoard.",
   post="Lagdou keeps its dead. Go on.",
   won="The Lagdou Ruins are cleared. A sealed chest opens for you.",
   guide="Lagdou Ruins (Lv 24 to 32)",
   lines=['No one enters the ruins unarmed.', 'The stone remembers every thief.', 'Go no deeper.'],
   lines_d=['The stone yields.', 'Strong. Go on.', 'You pass.'],
   lines_p=['The deepest hall is ahead.', 'Watch the cracked floor.', 'The master is below.']),
 'melkaen': dict(
   title='Melkaen Coast', flag='FLAG_UNUSED_0x4A9', lv0=16, step=0, boss_lv=22, boss_theme='water', boss_src='TRAINER_LEADER_MISTY',
   themes=['brute', 'archer', 'knight'], conv_src=None, conv_gfx=None, min_tr=0,
   floors=[('Route25', 'Story_MelkaenCoast')],
   base_n=3, entry=0, exits={'MAP_ROUTE25_SEA_COTTAGE'}, boss_floor=0, boss_replace='LASS@42,5', entry_mode='edge',
   reward=('ITEM_NUGGET', 2, 2500),
   intro="This coast belongs to the Melkaen corsairs now. Pay the toll in battle.",
   defeat="The tide turns. The coast is yours.",
   post="Melkaen is quiet again. Safe road, traveler.",
   won="Melkaen Coast is cleared. The corsairs' chest is yours.",
   guide="Melkaen Coast (Lv 16 to 22)",
   lines=['Nobody walks this coast for free.', 'The tide brings fresh prey.', 'Hand over a fight.'],
   lines_d=['Hmph. Fair.', 'The sea favors you.', 'Wash out, then.'],
   lines_p=['The captain is down the shore.', 'Watch the cliffs.', 'The tide is rising.']),
}
order = [k for k in ('valni', 'lagdou', 'melkaen') if k in want]

# ---------------------------------------------------------------- trainers.h / parties
trainers = (root / 'src/data/trainers.h').read_text(); parties = (root / 'src/data/trainer_parties.h').read_text()
allids = re.findall(r'\[(TRAINER_\w+)\] =', trainers)
opp = (root / 'include/constants/opponents.h').read_text()
def trainer_body(t): return re.search(r'    \[%s\] = \{.*?\n    \},\n' % t, trainers, re.S).group(0)
def free_rs():
    out = []
    for t in allids:
        if t.startswith('TRAINER_RS_') and t != 'TRAINER_RS_NONE' and 'StoryClone' not in trainer_body(t) and re.search(r'#define %s\s' % t, opp):
            out.append(t)
    return out
RS = free_rs(); used_slots = {}
def clone_slot(key, src):
    global trainers
    if key in used_slots: return used_slots[key]
    if not RS: raise SystemExit('no free TRAINER_RS_ slot left for ' + key)
    nt = RS.pop(0); used_slots[key] = nt
    nb = trainer_body(src).replace('[%s]' % src, '[%s]' % nt)
    nb = re.sub(r'\.party = (\w+)\((\w+)\),', lambda m: '.party = %s(sParty_Dungeon_%s),' % (m.group(1), nt[8:]), nb)
    trainers = re.sub(r'    \[%s\] = \{.*?\n    \},\n' % nt, lambda m: nb, trainers, count=1, flags=re.S)
    return nt
def set_party(t, theme, lvl, n, boss=False):
    global trainers, parties
    m = re.search(r'\[%s\] = \{.*?\.party = (\w+)\((\w+)\),' % t, trainers, re.S)
    macro, sym = m.group(1), m.group(2)
    n = min(n, 6)
    lv = [lvl - (n - 1 - i) for i in range(n)]
    mons = [pick(theme, l, i) for i, l in enumerate(lv)]
    body = ''.join('    {\n        .iv = 31,\n        .lvl = %d,\n        .species = SPECIES_%s,\n    },\n' % (l, s) for s, l in zip(mons, lv))
    arr = 'static const struct TrainerMonNoItemDefaultMoves %s[] = {\n%s};' % (sym, body)
    pm = re.search(r'static const struct \w+ %s\[\] = \{.*?\n\};' % sym, parties, re.S)
    if pm: parties = parties.replace(pm.group(0), arr)
    else: parties += '\n' + arr + '\n'
    trainers = trainers.replace(m.group(0), m.group(0).replace(macro + '(', 'NO_ITEM_DEFAULT_MOVES('))
    return len(mons)

# ---------------------------------------------------------------- map helpers
lay = {l.get('id'): l for l in json.loads((root / 'data/layouts/layouts.json').read_text())['layouts']}
def grid(layout_id):
    L = lay[layout_id]; b = (root / L['blockdata_filepath']).read_bytes()
    return L['width'], L['height'], struct.unpack('<%dH' % (len(b) // 2), b)
def passable(v): return (v >> 10 & 3) == 0 and (v >> 12) in (0, 3, 15)
def all_donor_scripts(mapname): return (root / 'data/maps' / mapname / 'scripts.inc').read_text()
def donor_trainer(mapname, label):
    s = all_donor_scripts(mapname) + '\n' + (root / 'data/scripts/trainers.inc').read_text()
    m = re.search(r'%s::\n(?:.*\n)*?\s*trainerbattle_\w+ (TRAINER_\w+),' % re.escape(label), s)
    return m.group(1) if m else None
def jload(p): return json.loads(Path(p).read_text())
grp = jload(root / 'data/maps/map_groups.json'); ev = (root / 'data/event_scripts.s').read_text()
mapid = lambda name: 'MAP_' + const(name)
PERSON_SKIP = ('FOSSIL', 'PUSHABLE_BOULDER', 'ROCK_SMASH_ROCK', 'MEWTWO', 'ITEM_BALL', 'BLUE', 'MR_FUJI')

report = []
def build(key):
    sp = SPECS[key]; names = {d: n for d, n in sp['floors']}
    didmap = {jload(root / 'data/maps' / d_ / 'map.json')['id']: mapid(n_) for d_, n_ in sp['floors']}
    inc = []; texts = []
    nboss_done = False; counters = {'T': 0}
    entry_xy = None
    ntr_total = 0; maxparty = 0
    for fi, (donor, new) in enumerate(sp['floors']):
        j = jload(root / 'data/maps' / donor / 'map.json')
        W, H, vals = grid(j['layout'])
        lvl = sp['lv0'] + fi * sp['step']
        newobjs = []; ntr = 0
        warps = []
        for w in j['warp_events']:
            if w['dest_map'] in sp.get('drop_warps', ()): continue
            w = dict(w)
            if w['dest_map'] in didmap: w['dest_map'] = didmap[w['dest_map']]
            else: w['dest_map'] = 'MAP_PALLET_TOWN'; w['dest_warp_id'] = '0'
            warps.append(w)
        for o in j['object_events']:
            o = dict(o); g = o['graphics_id'].replace('OBJ_EVENT_GFX_', '')
            if sp['boss_floor'] == fi and (g == sp['boss_replace'] or '%s@%d,%d' % (g, o['x'], o['y']) == sp['boss_replace']) and not nboss_done:
                nboss_done = True
                bt = clone_slot(key + '_boss', sp['boss_src']); set_party(bt, sp['boss_theme'], sp['boss_lv'], 5)
                lab = '%s_EventScript_Boss' % new
                o.update(graphics_id='OBJ_EVENT_GFX_' + ('CHANNELER' if key == 'valni' else {'lagdou': 'SCIENTIST', 'melkaen': 'SWIMMER_F_LAND'}[key]),
                         trainer_type='TRAINER_TYPE_NORMAL', trainer_sight_or_berry_tree_id='4', movement_type='MOVEMENT_TYPE_FACE_DOWN', script=lab, flag='0')
                inc += ['%s::' % lab,
                        '\ttrainerbattle_single %s, %s_Text_BossIntro, %s_Text_BossDefeat, %s_EventScript_BossWon' % (bt, new, new, new),
                        '\tmsgbox %s_Text_BossPost, MSGBOX_AUTOCLOSE' % new, '\tend', '',
                        '%s_EventScript_BossWon::' % new, '\tsetflag %s' % sp['flag'],
                        '\tmsgbox %s_Text_BossWon, MSGBOX_DEFAULT' % new,
                        '\tgiveitem %s, %d' % sp['reward'][:2], '\taddmoney %d' % sp['reward'][2], '\trelease', '\tend', '']
                texts += [('BossIntro', sp['intro']), ('BossDefeat', sp['defeat']), ('BossPost', sp['post']), ('BossWon', sp['won'])]
                newobjs.append(o); ntr += 1; continue
            if g == 'ITEM_BALL': newobjs.append(o); continue
            if o['trainer_type'] == 'TRAINER_TYPE_NORMAL':
                t = donor_trainer(donor, o['script'])
                if t is None: raise SystemExit('cannot read trainer for %s %s' % (donor, o['script']))
                o['flag'] = '0'
                if t in reserved:     # story trainer: swap to a private clone slot with its own script
                    nt = clone_slot('%s_%s_%d' % (key, new, len(newobjs)), t); lab = '%s_EventScript_T%d' % (new, counters['T']); counters['T'] += 1
                    n = set_party(nt, sp['themes'][ntr_total % len(sp['themes'])], lvl, min(4, sp.get('base_n', 2) + fi // 2))
                    ln = counters['T'] - 1
                    inc += ['%s::' % lab, '\ttrainerbattle_single %s, %s_Text_T%dIntro, %s_Text_T%dDefeat' % (nt, new, ln, new, ln),
                            '\tmsgbox %s_Text_T%dPost, MSGBOX_AUTOCLOSE' % (new, ln), '\tend', '']
                    texts += [('T%dIntro' % ln, sp['lines'][ln % 3]), ('T%dDefeat' % ln, sp['lines_d'][ln % 3]), ('T%dPost' % ln, sp['lines_p'][ln % 3])]
                    o['script'] = lab
                else:
                    set_party(t, sp['themes'][ntr_total % len(sp['themes'])], lvl, min(4, sp.get('base_n', 2) + fi // 2))
                ntr += 1; ntr_total += 1; newobjs.append(o); continue
            if g in PERSON_SKIP: continue
            # a plain donor NPC: convert while the floor still lacks trainers
            if ntr < sp['min_tr'] and sp['conv_src'] and g != 'WORKER_F':
                nt = clone_slot('%s_%s_%d' % (key, new, len(newobjs)), sp['conv_src']); lab = '%s_EventScript_T%d' % (new, counters['T']); ln = counters['T']; counters['T'] += 1
                set_party(nt, sp['themes'][ntr_total % len(sp['themes'])], lvl, min(4, sp.get('base_n', 2) + fi // 2))
                inc += ['%s::' % lab, '\ttrainerbattle_single %s, %s_Text_T%dIntro, %s_Text_T%dDefeat' % (nt, new, ln, new, ln),
                        '\tmsgbox %s_Text_T%dPost, MSGBOX_AUTOCLOSE' % (new, ln), '\tend', '']
                texts += [('T%dIntro' % ln, sp['lines'][ln % 3]), ('T%dDefeat' % ln, sp['lines_d'][ln % 3]), ('T%dPost' % ln, sp['lines_p'][ln % 3])]
                mv = o['movement_type'] if o['movement_type'].startswith('MOVEMENT_TYPE_FACE_') else 'MOVEMENT_TYPE_FACE_DOWN'
                o.update(graphics_id='OBJ_EVENT_GFX_' + sp['conv_gfx'], trainer_type='TRAINER_TYPE_NORMAL', trainer_sight_or_berry_tree_id='3',
                         movement_type=mv, script=lab, flag='0', movement_range_x=0, movement_range_y=0)
                o.pop('local_id', None)
                newobjs.append(o); ntr += 1; ntr_total += 1
        for o in newobjs: o.pop('local_id', None)
        j.update(id=mapid(new), name=new, show_map_name=False, object_events=newobjs, coord_events=[], bg_events=[],
                 warp_events=warps, connections=None)
        if 'floor_number' in j: j['floor_number'] = 0
        d = root / 'data/maps' / new; d.mkdir(exist_ok=True)
        (d / 'map.json').write_text(json.dumps(j, indent=2) + '\n')
        # arrival cell for the guide warp: next to the first exit warp of the entry floor
        if fi == sp['entry'] and sp.get('entry_mode') == 'edge':
            ok = [(x, y) for y in range(H) for x in range(W) if passable(vals[y * W + x]) and all(passable(vals[y * W + x + dx]) for dx in (0, 1) if x + dx < W)]
            mx = min(x for x, y in ok); entry_xy = min([c for c in ok if c[0] == mx], key=lambda c: abs(c[1] - H // 2))
        elif fi == sp['entry']:
            ex = [w for w in warps if w['dest_map'] == 'MAP_PALLET_TOWN'][0]
            cx, cy = ex['x'], ex['y']; wset = {(w['x'], w['y']) for w in warps}
            cand = [(cx, cy + 1), (cx, cy - 1), (cx - 1, cy), (cx + 1, cy)] if cy > H // 2 else [(cx, cy + 1), (cx - 1, cy), (cx + 1, cy), (cx, cy - 1)]
            cand = [(x, y) for (x, y) in cand if 0 <= x < W and 0 <= y < H and passable(vals[y * W + x]) and (x, y) not in wset]
            entry_xy = cand[0]
        maxparty = max(maxparty, min(4, sp.get('base_n', 2) + fi // 2))
        if new not in grp['gMapGroup_IndoorSevenIslandRoute']: grp['gMapGroup_IndoorSevenIslandRoute'].append(new)
        report.append((new, len(newobjs), ntr, len(warps)))
        # scripts file (donor floor scripts are global labels, reused as is)
        fl = ['%s_MapScripts::' % new, '\t.byte 0', '']
        (d / 'scripts.inc').write_text('\n'.join(fl) + '\n' + '@@FLOORSCRIPTS@@')
        sp.setdefault('_floorinc', {})[new] = (inc, texts); inc = []; texts = []
        incl = '\t.include "data/maps/%s/scripts.inc"\n' % new
        global ev
        if incl not in ev: ev = ev.replace('\t.include "data/maps/PalletTown/scripts.inc"\n', '\t.include "data/maps/PalletTown/scripts.inc"\n' + incl, 1)
    for new, (inc_, texts_) in sp['_floorinc'].items():
        p = root / 'data/maps' / new / 'scripts.inc'; s = p.read_text().replace('@@FLOORSCRIPTS@@', '')
        s += '\n'.join(inc_) + '\n'
        for nm, t in texts_: s += '%s_Text_%s:\n\t.string "%s"\n\n' % (new, nm, fmt(t))
        p.write_text(s)
    if not nboss_done: raise SystemExit('boss object not found for ' + key)
    sp['entry_map'] = mapid(sp['floors'][sp['entry']][1]); sp['entry_xy'] = entry_xy

# ---------------------------------------------------------------- reachability check (approximate, warps included)
def check(key):
    sp = SPECS[key]; maps = {}
    for donor, new in sp['floors']:
        j = jload(root / 'data/maps' / new / 'map.json'); W, H, vals = grid(j['layout']); maps[mapid(new)] = (j, W, H, vals)
    start = (sp['entry_map'],) + tuple(sp['entry_xy']); seen = {start}; q = deque([start])
    while q:
        m, x, y = q.popleft(); j, W, H, vals = maps[m]
        nxt = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = x + dx, y + dy
            if 0 <= a < W and 0 <= b < H and passable(vals[b * W + a]): nxt.append((m, a, b))
        for w in j['warp_events']:
            if abs(w['x'] - x) + abs(w['y'] - y) <= 1 and w['dest_map'] in maps:     # a warp tile is entered from a reachable neighbour
                dj = maps[w['dest_map']][0]; t = dj['warp_events'][int(w['dest_warp_id'])]; nxt.append((w['dest_map'], t['x'], t['y']))
                nxt.append((m, w['x'], w['y']))
        for n in nxt:
            if n not in seen: seen.add(n); q.append(n)
    bad = []
    for m, (j, W, H, vals) in maps.items():
        for o in j['object_events']:
            if not any((m, o['x'] + dx, o['y'] + dy) in seen for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))):
                bad.append((m, o['graphics_id'], o['x'], o['y']))
        # every floor must be entered from the chain
    return bad, {m for (m, _, _) in seen}

for k in order: build(k)
bad_all = []
for k in order:
    bad, floors = check(k)
    miss = {mapid(n) for _, n in SPECS[k]['floors']} - floors
    print(k, 'unreachable objects:', bad, 'unreached floors:', sorted(miss))
    bad_all += bad
    if miss: raise SystemExit('floor not reachable in ' + k)
if bad_all and not os.environ.get('ALLOW_UNREACHABLE'): raise SystemExit('unreachable objects (set ALLOW_UNREACHABLE=1 to override)')

# ---------------------------------------------------------------- guide in Pallet Town
g = ['@ Generated by tools/leg13_dungeons.py. Do not edit by hand.', '', 'EventScript_DungeonGuide::', '\tlock', '\tfaceplayer',
     '\tgoto_if_lt VAR_STORY_CHAPTER, %d, Dungeon_NotYet' % GATE, '\tmsgbox Dungeon_Greeting, MSGBOX_DEFAULT']
for k in order:
    sp = SPECS[k]
    g += ['\tmsgbox Dungeon_Ask_%s, MSGBOX_YESNO' % k, '\tgoto_if_eq VAR_RESULT, YES, Dungeon_Go_%s' % k]
g += ['\tmsgbox Dungeon_Bye, MSGBOX_DEFAULT', '\trelease', '\tend', '', 'Dungeon_NotYet:', '\tmsgbox Dungeon_NotYetText, MSGBOX_DEFAULT', '\trelease', '\tend', '']
for k in order:
    sp = SPECS[k]; x, y = sp['entry_xy']
    g += ['Dungeon_Go_%s:' % k, '\tgoto_if_set %s, Dungeon_Done_%s' % (sp['flag'], k), 'Dungeon_Enter_%s:' % k,
          '\tfadescreen FADE_TO_BLACK', '\twarp %s, 255, %d, %d' % (sp['entry_map'], x, y), '\twaitstate', '\tend', '',
          'Dungeon_Done_%s:' % k, '\tmsgbox Dungeon_DoneText_%s, MSGBOX_YESNO' % k,
          '\tgoto_if_eq VAR_RESULT, YES, Dungeon_Enter_%s' % k, '\tmsgbox Dungeon_Bye, MSGBOX_DEFAULT', '\trelease', '\tend', '']
g += ['Dungeon_Greeting:', '\t.string "%s"' % fmt('I keep the old roads of Magvel. Optional trials await the brave. Fight at your own pace.'), '',
      'Dungeon_Bye:', '\t.string "%s"' % fmt('Come back when you are ready.'), '',
      'Dungeon_NotYetText:', '\t.string "%s"' % fmt('The old roads open once you have crossed Chapter 8. Finish the story first.'), '']
for k in order:
    sp = SPECS[k]
    g += ['Dungeon_Ask_%s:' % k, '\t.string "%s"' % fmt('Enter the %s? Trainers there use at most 6 Pokemon.' % sp['guide']), '',
          'Dungeon_DoneText_%s:' % k, '\t.string "%s"' % fmt('You cleared the %s already. Enter again? Its trainers stay defeated.' % sp['title']), '']
(root / 'data/scripts/story_dungeons.inc').write_text('\n'.join(g) + '\n')
inc_line = '\t.include "data/scripts/story_dungeons.inc"\n'
if inc_line not in ev: ev = ev.replace('\t.include "data/scripts/story_chapters.inc"\n', '\t.include "data/scripts/story_chapters.inc"\n' + inc_line, 1)
# guide object
pj = root / 'data/maps/PalletTown/map.json'; P = jload(pj)
if not any(o.get('script') == 'EventScript_DungeonGuide' for o in P['object_events']):
    P['object_events'].append(dict(graphics_id='OBJ_EVENT_GFX_OLD_MAN_1', x=9, y=9, elevation=3, movement_type='MOVEMENT_TYPE_FACE_DOWN',
        movement_range_x=0, movement_range_y=0, trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0', script='EventScript_DungeonGuide', flag='0'))
    pj.write_text(json.dumps(P, indent=2) + '\n')
(root / 'data/event_scripts.s').write_text(ev)
(root / 'data/maps/map_groups.json').write_text(json.dumps(grp, indent=2) + '\n')
(root / 'src/data/trainers.h').write_text(trainers); (root / 'src/data/trainer_parties.h').write_text(parties)
for r in report: print('map %s objects %d trainers %d warps %d' % r)
print('slots used', used_slots, 'free left', len(RS))
