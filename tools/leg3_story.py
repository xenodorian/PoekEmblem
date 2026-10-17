#!/usr/bin/env python3
"""Generate the story chapter scripts and trainer parties in the decomp.
Usage: leg3_story.py CHAPTERS_JSON DECOMP_DIR"""
import json, os, re, sys, textwrap
from pathlib import Path

d = json.load(open(sys.argv[1])); root = Path(sys.argv[2])
opp = (root/'include/constants/opponents.h').read_text()
def need(t):
    if not re.search(r'#define %s\s' % t, opp): raise SystemExit('unknown trainer ' + t)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from level_curve import LV   # Leg19: monotonic curve, single source of truth (tools/level_curve.py)
FAM = {
 'brute':  [[('MANKEY',1),('PRIMEAPE',28)],[('MACHOP',1),('MACHOKE',28),('MACHAMP',45)],[('RATTATA',1),('RATICATE',20)],[('PINSIR',20)]],
 'knight': [[('GEODUDE',1),('GRAVELER',25),('GOLEM',40)],[('ONIX',1)],[('RHYHORN',1),('RHYDON',42)],[('SANDSHREW',1),('SANDSLASH',22)]],
 'rider':  [[('PONYTA',1),('RAPIDASH',40)],[('DODUO',1),('DODRIO',31)],[('GROWLITHE',1),('ARCANINE',36)],[('RHYHORN',1)]],
 'archer': [[('PIDGEY',1),('PIDGEOTTO',18),('PIDGEOT',36)],[('SPEAROW',1),('FEAROW',20)],[('FARFETCHD',1)],[('DODUO',1)]],
 'mage':   [[('ABRA',1),('KADABRA',16),('ALAKAZAM',36)],[('GASTLY',1),('HAUNTER',25),('GENGAR',38)],[('DROWZEE',1),('HYPNO',26)],[('KOFFING',1),('WEEZING',35)]],
 'dark':   [[('GASTLY',1),('HAUNTER',25),('GENGAR',38)],[('CUBONE',1),('MAROWAK',28)],[('KOFFING',1),('WEEZING',35)],[('ZUBAT',1),('GOLBAT',22)]],
 'wyvern': [[('DRATINI',1),('DRAGONAIR',30),('DRAGONITE',55)],[('AERODACTYL',1)],[('CHARMANDER',1),('CHARMELEON',16),('CHARIZARD',36)],[('PIDGEY',1),('PIDGEOT',36)]],
 'water':  [[('TENTACOOL',1),('TENTACRUEL',30)],[('KRABBY',1),('KINGLER',28)],[('POLIWAG',1),('POLIWHIRL',25),('POLIWRATH',40)],[('SHELLDER',1),('CLOYSTER',40)]],
 'plant':  [[('ODDISH',1),('GLOOM',21),('VILEPLUME',40)],[('BELLSPROUT',1),('WEEPINBELL',21),('VICTREEBEL',40)],[('EXEGGCUTE',1),('EXEGGUTOR',40)],[('TANGELA',1)]],
}
THEME = {'TRAINER_TEAM_ROCKET_GRUNT_27':'brute','TRAINER_TEAM_ROCKET_GRUNT_28':'brute','TRAINER_TEAM_ROCKET_GRUNT_29':'brute',
 'TRAINER_TEAM_ROCKET_GRUNT_30':'wyvern','TRAINER_TEAM_ROCKET_GRUNT_31':'brute','TRAINER_TEAM_ROCKET_GRUNT_32':'brute',
 'TRAINER_TEAM_ROCKET_GRUNT_33':'archer','TRAINER_TEAM_ROCKET_GRUNT_34':'knight','TRAINER_TEAM_ROCKET_GRUNT_36':'brute',
 'TRAINER_COOLTRAINER_ROLANDO':'knight','TRAINER_COOLTRAINER_COLBY':'rider','TRAINER_COOLTRAINER_WARREN':'rider','TRAINER_COOLTRAINER_SAMUEL':'knight',
 'TRAINER_PSYCHIC_TYRON':'dark','TRAINER_PSYCHIC_CAMERON':'dark','TRAINER_PSYCHIC_PRESTON':'mage','TRAINER_SCIENTIST_JERRY':'dark',
 'TRAINER_SCIENTIST_IVAN':'dark','TRAINER_SCIENTIST_PARKER':'mage','TRAINER_SCIENTIST_ED':'mage','TRAINER_SCIENTIST_GIDEON':'mage',
 'TRAINER_SCIENTIST_JOSHUA':'wyvern','TRAINER_SCIENTIST_JOSE':'mage','TRAINER_GENTLEMAN_THOMAS':'knight','TRAINER_GENTLEMAN_BROOKS':'knight',
 'TRAINER_GENTLEMAN_LAMAR':'rider','TRAINER_LASS_JOANA':'archer','TRAINER_BEAUTY_LORI':'water','TRAINER_ELITE_FOUR_BRUNO':'brute',
 'TRAINER_ELITE_FOUR_LANCE':'wyvern',
 'TRAINER_RIVAL_ROUTE22_LATE_SQUIRTLE':'mage','TRAINER_CHAMPION_FIRST_SQUIRTLE':'mage',
 'TRAINER_LEADER_BROCK':'rider','TRAINER_LEADER_BLAINE':'rider','TRAINER_LEADER_LT_SURGE':'knight','TRAINER_LEADER_MISTY':'water',
 'TRAINER_LEADER_ERIKA':'plant','TRAINER_LEADER_KOGA':'archer','TRAINER_LEADER_SABRINA':'mage','TRAINER_ELITE_FOUR_AGATHA':'dark'}
BOSSES = {'TRAINER_TEAM_ROCKET_GRUNT_32','TRAINER_PSYCHIC_TYRON','TRAINER_GENTLEMAN_THOMAS','TRAINER_SCIENTIST_IVAN','TRAINER_COOLTRAINER_COLBY',
 'TRAINER_GENTLEMAN_BROOKS','TRAINER_ELITE_FOUR_BRUNO','TRAINER_SCIENTIST_PARKER','TRAINER_COOLTRAINER_WARREN','TRAINER_COOLTRAINER_SAMUEL',
 'TRAINER_TEAM_ROCKET_GRUNT_30','TRAINER_ELITE_FOUR_LANCE','TRAINER_GENTLEMAN_LAMAR','TRAINER_RIVAL_ROUTE22_LATE_SQUIRTLE','TRAINER_PSYCHIC_CAMERON',
 'TRAINER_SCIENTIST_GIDEON','TRAINER_CHAMPION_FIRST_SQUIRTLE','TRAINER_TEAM_ROCKET_GRUNT_27','TRAINER_COOLTRAINER_ROLANDO'}

def pick(theme, lvl, k):
    fam = FAM[theme][k % len(FAM[theme])]
    best = fam[0][0]
    for sp, mn in fam:
        if lvl >= mn: best = sp
    return best

# ---- Leg12: resolve battles (skirmish battle first, fresh trainers, one party per trainer per chapter via clones)
trall = (root/'src/data/trainers.h').read_text()
allids = re.findall(r'\[(TRAINER_\w+)\] =', trall)
reserved = set()
for c in d['chapters']:
    for b in c['battles']:
        for k in ('a', 'b', 'partner'):
            if b.get(k): reserved.add(b[k])
POOLP = {'brute': ['BLACK_BELT_', 'BIKER_', 'CUE_BALL_'], 'knight': ['HIKER_', 'ENGINEER_', 'BURGLAR_', 'TEAM_ROCKET_GRUNT'],
         'rider': ['JUGGLER_', 'GAMER_', 'TAMER_'], 'archer': ['BIRD_KEEPER_'], 'mage': ['PSYCHIC_', 'SCIENTIST_', 'POKEMANIAC_'],
         'dark': ['CHANNELER_', 'POKEMANIAC_', 'SUPER_NERD_'], 'water': ['SAILOR_', 'FISHERMAN_', 'SWIMMER_MALE_'],
         'wyvern': ['TAMER_', 'DRAGON_TAMER', 'COOLTRAINER_'], 'plant': ['CAMPER_', 'PICNICKER_', 'LASS_']}
FRESH_THEME = {}
def fresh(theme):
    for pre in POOLP[theme]:
        for t in allids:
            if t.startswith('TRAINER_' + pre) and t not in reserved:
                reserved.add(t); FRESH_THEME[t] = theme; return t
    raise SystemExit('fresh pool empty ' + theme)
RSPOOL = [t for t in allids if t.startswith('TRAINER_RS_') and t not in reserved]
CLONES = {}   # new id -> original id
seen_in = {}  # trainer -> chapter that first uses it
for c in d['chapters']:
    if not c.get('_resolved'):
        main = c['battles']
        if c.get('skirmish_theme'):
            th = c['skirmish_theme']; m0 = main[-1]
            sk = {'a': fresh(th)}
            if m0.get('b') and m0.get('partner'): sk['b'] = fresh(th); sk['partner'] = m0['partner']
            c['battles'] = [sk] + main
        for b in c['battles']:
            for k in ('a', 'b', 'partner'):
                t = b.get(k)
                if not t: continue
                if t in seen_in and seen_in[t] != c['id']:
                    nt = c.setdefault('_clone', {}).get(t)
                    if not nt:
                        nt = RSPOOL.pop(0); c['_clone'][t] = nt; CLONES[nt] = CLONES.get(t, t)
                    b[k] = nt; t = nt
                seen_in.setdefault(t, c['id'])
        c['_resolved'] = True
orig_THEME_get = None

plan = {}   # trainer -> (chapter, count, boss)
for c in d['chapters']:
    L = LV[c['id']]
    for b in c['battles']:
        for key, cnt in (('a', 3), ('b', 2), ('partner', 3)):
            t = b.get(key)
            if not t: continue
            need(t)
            if b.get('theme') and key == 'a': THEME[t] = b['theme']
            if t in CLONES: THEME[t] = THEME[CLONES[t]]
            if t in FRESH_THEME: THEME[t] = FRESH_THEME[t]
            if t not in THEME and c.get('skirmish_theme'): THEME[t] = c['skirmish_theme']
            if t not in THEME: raise SystemExit('no theme for ' + t)
            boss = key == 'a' and (t in BOSSES or b.get('boss'))
            plan[(t)] = (L + (2 if boss else 0), cnt if boss or key == 'partner' else 2, key)

# ---- write parties (always no-item default-move type)
pp = root/'src/data/trainer_parties.h'; tr = root/'src/data/trainers.h'
parties = pp.read_text(); trainers = tr.read_text()
for nt, ot in CLONES.items():
    ob = re.search(r'    \[%s\] = \{.*?\n    \},\n' % ot, trainers, re.S).group(0)
    nb = ob.replace('[%s]' % ot, '[%s]' % nt)
    nb = re.sub(r'\.party = (\w+)\((\w+)\),', lambda mm: '.party = %s(sParty_StoryClone_%s),' % (mm.group(1), nt[8:]), nb)
    trainers = re.sub(r'    \[%s\] = \{.*?\n    \},\n' % nt, lambda mm: nb, trainers, count=1, flags=re.S)
    sym = 'sParty_StoryClone_' + nt[8:]
    if sym not in parties:
        parties += '\nstatic const struct TrainerMonNoItemDefaultMoves %s[] = {\n    { .iv = 31, .lvl = 5, .species = SPECIES_RATTATA },\n};\n' % sym
for t, (lvl, cnt, key) in plan.items():
    m = re.search(r'\[%s\] = \{.*?\.party = (\w+)\((\w+)\),' % t, trainers, re.S)
    macro, sym = m.group(1), m.group(2)
    mons = [pick(THEME[t], lvl - (cnt - 1 - i), i) for i in range(cnt)]
    lv = [lvl - (cnt - 1 - i) for i in range(cnt)]
    body = ''.join('    {\n        .iv = 31,\n        .lvl = %d,\n        .species = SPECIES_%s,\n    },\n' % (l, s) for s, l in zip(mons, lv))
    pm = re.search(r'static const struct \w+ %s\[\] = \{.*?\n\};' % sym, parties, re.S)
    parties = parties.replace(pm.group(0), 'static const struct TrainerMonNoItemDefaultMoves %s[] = {\n%s};' % (sym, body))
    trainers = trainers.replace(m.group(0), m.group(0).replace(macro + '(', 'NO_ITEM_DEFAULT_MOVES('))
if not os.environ.get('SCRIPTS_ONLY'):
    pp.write_text(parties); tr.write_text(trainers)

# ---- scripts
AUTOTILED = ('MAP_STORY_RENAIS_CASTLE', 'MAP_STORY_FRELIA_CASTLE', 'MAP_STORY_JEHANNA_HALL', 'MAP_STORY_BLACK_TEMPLE')
def mapinfo(mid):
    for f in (root/'data/maps').glob('*/map.json'):
        j = json.loads(f.read_text())
        if j.get('id') == mid:
            if j.get('warp_events'):
                w = j['warp_events'][0]
                # the four autotiled indoor maps (tools/leg9_indoor_maps.py) have their exit warp on the door mat (7,14).
                # Arrival and the walk-in start one row below it at (7,15); arriving on the warp tile itself is wrong.
                if w['x'] == 7 and w['y'] == 14 and mid in AUTOTILED: return 7, 15
                return w['x'], w['y']
            if j.get('object_events'):
                w = j['object_events'][0]; return w['x'], w['y'] + 1
            w = j['bg_events'][0]; return w['x'], w['y'] + 1
    raise SystemExit('map not found ' + mid)

def fmt(paras):
    out = []
    for p in paras:
        lines = textwrap.wrap(p.replace('’', "'"), 34)
        s = ''
        for i, l in enumerate(lines):
            s += l.replace('"', '\\"')
            if i < len(lines) - 1: s += '\\n' if i % 2 == 0 else '\\p'
        out.append(s)
    return '\\p'.join(out) + '$'

def say(n, tag, lines):
    out = []
    for k, (sp, t) in enumerate(lines):
        if sp: out.append('\tshowmonpic %s, 1, 1' % sp)
        out.append('\tmsgbox Story_Ch%d_%s%d, MSGBOX_DEFAULT' % (n, tag, k))
        if sp: out.append('\thidemonpic')
    return out
def say_text(n, tag, lines):
    out = []
    for k, (sp, t) in enumerate(lines):
        out += ['Story_Ch%d_%s%d:' % (n, tag, k), '\t.string "%s"' % fmt([t]), '']
    return out
# ---- Leg18: plot-ordered flow. Chapters run in FE8 order. After each chapter the player is warped to a story hub
# (healer and vendors) and departs through the hub door tile (coord event, yes/no) to start the next chapter.
def hub_for(i):
    if i <= 1: return 'MAP_STORY_RENAIS_CASTLE'
    if i <= 9: return 'MAP_STORY_FRELIA_CASTLE'
    if i <= 13: return 'MAP_STORY_FORT_RIGWALD'
    if i <= 17: return 'MAP_STORY_JEHANNA_HALL'
    if i <= 22: return 'MAP_STORY_GRADO_THRONE_ROOM'
    return 'MAP_STORY_BLACK_TEMPLE'
NCH = len(d['chapters'])
camp_txt = []
inc = ['@ Generated by tools/leg3_story.py from story/chapters.json. Do not edit by hand.', '']
guide = ['EventScript_StoryDepart::', '\tlockall']
arrive = ['EventScript_StoryArrive::', '\tgoto_if_eq VAR_0x8004, 2, Story_Camp']
for c in d['chapters']:
    n = c['id']; x, y = mapinfo(c['map'])
    guide.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_Depart_%d' % (n, n))
    arrive.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_Arrive_%d' % (n, n))
    inc += ['Story_Depart_%d::' % n,
            '\tmsgbox Story_Ch%d_DepartAsk, MSGBOX_YESNO' % n,
            '\tgoto_if_eq VAR_RESULT, NO, Story_DepartNo',
            'Story_Go_%d::' % n,
            '\tmsgbox Story_Ch%d_Title, MSGBOX_DEFAULT' % n,
            '\tsetvar VAR_STORY_PENDING, 1',
            '\tfadescreen FADE_TO_BLACK',
            '\twarp %s, 255, %d, %d' % (c['map'], x, y),
            '\twaitstate', '\tend', '',
            'Story_Arrive_%d::' % n,
            '\tlockall',
            '\tshowmonpic %s, 1, 1' % c.get('speaker_before', 'SPECIES_EIRIKA'),
            '\tmsgbox Story_Ch%d_Before, MSGBOX_DEFAULT' % n,
            '\thidemonpic'] + say(n, 'SB', c.get('scene_before', []))
    inc += ['\tapplymovement OBJ_EVENT_ID_PLAYER, Story_WalkIn', '\twaitmovement 0',
            '\tsetvar VAR_0x8004, %d' % (LV[n] + 2), '\tspecial StoryLevelCatchUp']   # Leg18: no grinding exists, so the party is raised to the chapter level
    for i, b in enumerate(c['battles']):
        if i == 1 and c.get('mid'):
            inc += ['\tshowmonpic %s, 1, 1' % c['mid']['speaker'], '\tmsgbox Story_Ch%d_Mid, MSGBOX_DEFAULT' % n, '\thidemonpic']
        if b.get('b') and b.get('partner'):
            inc += ['\tsetvar VAR_0x8004, %s' % b['a'], '\tsetvar VAR_0x8005, %s' % b['b'], '\tsetvar VAR_0x8006, %s' % b['partner'],
                    '\tspecial StartPartnerBattle', '\twaitstate']
        else:
            inc += ['\ttrainerbattle_no_intro %s, Story_Ch%d_Defeat' % (b['a'], n)]
    for r in c.get('recruits', []):
        rl = c.get('recruit_lines', {}).get(r)
        if rl:
            inc += ['\tshowmonpic SPECIES_%s, 1, 1' % r.upper(), '\tmsgbox Story_Ch%d_Recruit%s, MSGBOX_DEFAULT' % (n, r), '\thidemonpic']
        inc += ['\tcall EventScript_Recruit%s' % r]
    if c.get('ally_talk'):
        inc += ['\tshowmonpic %s, 1, 1' % c['ally_talk']['speaker'], '\tmsgbox Story_Ch%d_AllyTalk, MSGBOX_DEFAULT' % n, '\thidemonpic']
    if len(c['battles']) < 2 and c.get('mid'):
        inc += ['\tshowmonpic %s, 1, 1' % c['mid']['speaker'], '\tmsgbox Story_Ch%d_Mid, MSGBOX_DEFAULT' % n, '\thidemonpic']
    sa = c.get('speaker_after') or ('SPECIES_' + c['recruits'][0].upper() if c.get('recruits') else 'SPECIES_EIRIKA')
    inc += ['\tshowmonpic %s, 1, 1' % sa, '\tmsgbox Story_Ch%d_After, MSGBOX_DEFAULT' % n, '\thidemonpic'] + say(n, 'SA', c.get('scene_after', [])) + [
            '\tspecial HealPlayerParty', '\taddmoney %d' % (500 + 250*n), '\tmsgbox Story_Ch%d_Reward, MSGBOX_DEFAULT' % n,
            ] + say(n, 'Epi', c.get('epilogue', [])) + (
            ['\tfadescreen FADE_TO_BLACK', '\tspecial ShowStoryTheEnd', '\twaitstate'] if c.get('epilogue') else []) + [
            '\taddvar VAR_STORY_CHAPTER, 1',
            '\tsetvar VAR_STORY_PENDING, 2',
            '\tfadescreen FADE_TO_BLACK',
            '\twarp %s, 255, %d, %d' % ((hub_for(n + 1),) + mapinfo(hub_for(n + 1))),
            '\twaitstate', '\tend', '']
    nx = d['chapters'][n + 1] if n + 1 < NCH else None
    camp_txt.append((n + 1, nx))
    inc += ['Story_Ch%d_DepartAsk:' % n, '\t.string "%s"' % fmt(['Leave camp and begin CHAPTER %s, %s?' % (c.get('label', n), c['title'])]), '']
    inc += ['Story_Ch%d_Title:' % n, '\t.string "CHAPTER %s\\n%s$"' % (c.get('label', n), c['title'].upper().replace('"', '')), '',
            'Story_Ch%d_Before:' % n, '\t.string "%s"' % fmt(c['before']), '',
            'Story_Ch%d_Mid:' % n, '\t.string "%s"' % fmt([c['mid']['text'] if c.get('mid') else '...']), '',
            ] + sum([['Story_Ch%d_Recruit%s:' % (n, r), '\t.string "%s"' % fmt([t]), ''] for r, t in c.get('recruit_lines', {}).items()], []) + (
            ['Story_Ch%d_AllyTalk:' % n, '\t.string "%s"' % fmt([c['ally_talk']['text']]), ''] if c.get('ally_talk') else []) + [
            'Story_Ch%d_After:' % n, '\t.string "%s"' % fmt(c['after']), '',
            ] + say_text(n, 'Epi', c.get('epilogue', [])) + say_text(n, 'SB', c.get('scene_before', [])) + say_text(n, 'SA', c.get('scene_after', [])) + [
            'Story_Ch%d_Defeat:' % n, '\t.string "..."', '',
            'Story_Ch%d_Reward:' % n, '\t.string "Your party was fully healed.\\pThe court rewards you with\\n¥%d.$"' % (500 + 250*n), '']
# camp (arrival at a hub after a chapter)
camp = ['Story_Camp::', '\tlockall']
for k, nx in camp_txt:
    camp.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_Camp_%d' % (k, k))
camp += ['\tgoto Story_Camp_%d' % NCH, '']
for k, nx in camp_txt:
    camp += ['Story_Camp_%d:' % k, '\tapplymovement OBJ_EVENT_ID_PLAYER, Story_WalkIn', '\twaitmovement 0',
             '\tmsgbox Story_CampText%d, MSGBOX_DEFAULT' % k, '\treleaseall', '\tend', '']
    if nx: msg = 'CAMP. Use the healer and vendors, then leave through the door at the bottom to begin CHAPTER %s, %s.' % (nx.get('label', nx['id']), nx['title'])
    else: msg = 'The war is over. Thank you for playing.'
    camp += ['Story_CampText%d:' % k, '\t.string "%s"' % fmt([msg]), '']
inc += camp + ['Story_DepartNo:', '\tapplymovement OBJ_EVENT_ID_PLAYER, Story_StepBack', '\twaitmovement 0', '\treleaseall', '\tend', '',
               'Story_StepBack:', '\twalk_up', '\tstep_end', '']
guide += ['\tmsgbox Story_NoMoreChapters, MSGBOX_DEFAULT', '\tgoto Story_DepartNo', '',
       'Story_NoMoreChapters:', '\t.string "The war is over. Thank you for\\nplaying.$"', '']
arrive += ['\tend', '']
inc += ['Story_WalkIn:', '\twalk_up', '\twalk_up', '\twalk_up', '\twalk_up', '\tstep_end', '']
sw = guide + arrive

# ---- Leg18: map patches (idempotent): exit tile on each hub is a coord event that departs to the next chapter,
# the exit warp no longer leads to Pallet Town, and the Pallet Town guide NPC is removed.
for nm in ('RenaisCastle','FreliaCastle','FortRigwald','JehannaHall','GradoThroneRoom','BlackTemple'):
    f = root/('data/maps/Story_%s/map.json' % nm); j = json.loads(f.read_text())
    w = j['warp_events'][0]
    w['dest_map'] = j['id']; w['dest_warp_id'] = '0'
    j['coord_events'] = [e for e in j.get('coord_events', []) if e.get('script') != 'EventScript_StoryDepart']
    j['coord_events'].append({'type': 'trigger', 'x': w['x'], 'y': w['y'], 'elevation': 0, 'var': 'VAR_TEMP_F', 'var_value': '0', 'script': 'EventScript_StoryDepart'})
    f.write_text(json.dumps(j, indent=2) + '\n')
f = root/'data/maps/PalletTown/map.json'; j = json.loads(f.read_text())
j['object_events'] = [o for o in j['object_events'] if o.get('script') != 'EventScript_StoryGuide']
f.write_text(json.dumps(j, indent=2) + '\n')
(root/'data/scripts/story_chapters.inc').write_text('\n'.join(inc + sw) + '\n')
print('chapters', len(d['chapters']), 'trainers', len(plan))
