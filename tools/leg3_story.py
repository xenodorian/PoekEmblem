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
HUBS = ['MAP_STORY_RENAIS_CASTLE', 'MAP_STORY_FRELIA_CASTLE', 'MAP_STORY_FORT_RIGWALD', 'MAP_STORY_JEHANNA_HALL',
        'MAP_STORY_GRADO_THRONE_ROOM', 'MAP_STORY_BLACK_TEMPLE']
HUBDIR = ['Story_RenaisCastle', 'Story_FreliaCastle', 'Story_FortRigwald', 'Story_JehannaHall', 'Story_GradoThroneRoom', 'Story_BlackTemple']
GATES = json.load(open(Path(__file__).resolve().parent.parent / 'story/gates.json'))   # tools/leg19_gates.py
def mapinfo(mid):
    # Leg19: the six hub rooms are all autotiled with the entry lane at (7,15); vanilla chapter maps use story/gates.json
    if mid in HUBS: return 7, 15
    return tuple(GATES[mid]['arrive'])

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
# ---- Leg19: walking world flow. Chapters run in FE8 order. Chapter maps (vanilla maps with their warps and connections removed)
# end at a gate the player must walk to; the gate leads to the camp (hub room). A hub room has three doors (mats at row 14):
# left = camp Pokemon Center, middle = on to the next chapter map, right = camp Pokemart. No menu teleports, no free heals.
def hub_for(i):
    if i <= 1: return 'MAP_STORY_RENAIS_CASTLE'
    if i <= 9: return 'MAP_STORY_FRELIA_CASTLE'
    if i <= 13: return 'MAP_STORY_FORT_RIGWALD'
    if i <= 17: return 'MAP_STORY_JEHANNA_HALL'
    if i <= 22: return 'MAP_STORY_GRADO_THRONE_ROOM'
    return 'MAP_STORY_BLACK_TEMPLE'
hidx = lambda m: HUBS.index(m)
STOCKS = {  # hub index -> [(display name, vanilla mart label)] in game order (Leg17 lists, exact vanilla stock by reference)
 0: [('VIRIDIAN CITY', 'ViridianCity_Mart_Items'), ('PEWTER CITY', 'PewterCity_Mart_Items')],
 1: [('CERULEAN CITY', 'CeruleanCity_Mart_Items'), ('VERMILION CITY', 'VermilionCity_Mart_Items')],
 2: [('LAVENDER TOWN', 'LavenderTown_Mart_Items'), ('CELADON 2F', 'CeladonCity_DepartmentStore_2F_Items')],
 3: [('FUCHSIA CITY', 'FuchsiaCity_Mart_Items'), ('CELADON 5F VITAMINS (HP UP, PROTEIN, IRON, CALCIUM, ZINC, CARBOS)', 'CeladonCity_DepartmentStore_5F_Vitamins'),
     ('CELADON 5F BATTLE ITEMS', 'CeladonCity_DepartmentStore_5F_XItems'), ('CELADON 2F TMS', 'CeladonCity_DepartmentStore_2F_TMs'),
     ('CELADON 4F STONES', 'CeladonCity_DepartmentStore_4F_Items')],
 4: [('SAFFRON CITY', 'SaffronCity_Mart_Items'), ('CINNABAR ISLAND', 'CinnabarIsland_Mart_Items')],
 5: [('INDIGO PLATEAU', 'IndigoPlateau_PokemonCenter_1F_Items'), ('SEVEN ISLAND', 'SevenIsland_Mart_Items')],
}
NCH = len(d['chapters'])
camp_txt = []
inc = ['@ Generated by tools/leg3_story.py from story/chapters.json. Do not edit by hand.', '']
arrive = ['EventScript_StoryArrive::', '\tgoto_if_eq VAR_0x8004, 2, Story_Camp']
def to_camp(n):   # warp to the camp hub of chapter n (n may equal NCH after the last chapter)
    return hub_for(min(n, NCH - 1))
gate = ['EventScript_StoryGate::', '\tlockall']
hubdoor = ['EventScript_StoryHubDoor::', '\tlockall']
for c in d['chapters']:
    n = c['id']; x, y = mapinfo(c['map'])
    arrive.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_Arrive_%d' % (n, n))
    gate.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_ToCamp_%d' % (n, n))
    hubdoor.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_HubDoor_%d' % (n, n))
    hm = hub_for(n); hx, hy = mapinfo(hm)
    inc += ['Story_HubDoor_%d::' % n,
            '\tgoto_if_eq VAR_STORY_HOME, %d, Story_Go_%d' % (hidx(hm), n),
            '\tgoto Story_ToCamp_%d' % n, '',
            'Story_Go_%d::' % n,
            '\tmsgbox Story_Ch%d_Title, MSGBOX_DEFAULT' % n,
            '\tsetvar VAR_STORY_PENDING, 1',
            '\tfadescreen FADE_TO_BLACK',
            '\twarp %s, 255, %d, %d' % (c['map'], x, y),
            '\twaitstate', '\tend', '',
            'Story_ToCamp_%d::' % n,
            '\tsetvar VAR_STORY_PENDING, 2',
            '\tfadescreen FADE_TO_BLACK',
            '\twarp %s, 255, %d, %d' % (hm, hx, hy),
            '\twaitstate', '\tend', '',
            'Story_Arrive_%d::' % n,
            '\tlockall',
            '\tshowmonpic %s, 1, 1' % c.get('speaker_before', 'SPECIES_EIRIKA'),
            '\tmsgbox Story_Ch%d_Before, MSGBOX_DEFAULT' % n,
            '\thidemonpic'] + say(n, 'SB', c.get('scene_before', []))
    if c['map'] in HUBS: inc += ['\tapplymovement OBJ_EVENT_ID_PLAYER, Story_WalkIn', '\twaitmovement 0']
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
            '\taddmoney %d' % (500 + 250*n), '\tmsgbox Story_Ch%d_Reward, MSGBOX_DEFAULT' % n,
            ] + say(n, 'Epi', c.get('epilogue', [])) + (
            ['\tfadescreen FADE_TO_BLACK', '\tspecial ShowStoryTheEnd', '\twaitstate'] if c.get('epilogue') else []) + [
            '\taddvar VAR_STORY_CHAPTER, 1',
            '\tmsgbox Story_Ch%d_Hint, MSGBOX_DEFAULT' % n,
            '\treleaseall', '\tend', '']
    nx = d['chapters'][n + 1] if n + 1 < NCH else None
    camp_txt.append((n + 1, nx))
    nxt = ('CHAPTER %s, %s' % (nx.get('label', nx['id']), nx['title'])) if nx else ''
    if not nx: hint = 'The war is over. Thank you for playing.'
    elif c['map'] in HUBS and hub_for(n + 1) == c['map']:
        hint = 'CAMP. Left door: POKEMON CENTER. Right door: POKEMART. Middle door: on to %s.' % nxt
    elif c['map'] in HUBS:
        hint = 'The middle door leads on to %s.' % nxt
    else:
        hint = 'Walk to the gate, where a soldier stands, to return to camp.'
    inc += ['Story_Ch%d_Hint:' % n, '\t.string "%s"' % fmt([hint]), '']
    inc += ['Story_Ch%d_Title:' % n, '\t.string "CHAPTER %s\\n%s$"' % (c.get('label', n), c['title'].upper().replace('"', '')), '',
            'Story_Ch%d_Before:' % n, '\t.string "%s"' % fmt(c['before']), '',
            'Story_Ch%d_Mid:' % n, '\t.string "%s"' % fmt([c['mid']['text'] if c.get('mid') else '...']), '',
            ] + sum([['Story_Ch%d_Recruit%s:' % (n, r), '\t.string "%s"' % fmt([t]), ''] for r, t in c.get('recruit_lines', {}).items()], []) + (
            ['Story_Ch%d_AllyTalk:' % n, '\t.string "%s"' % fmt([c['ally_talk']['text']]), ''] if c.get('ally_talk') else []) + [
            'Story_Ch%d_After:' % n, '\t.string "%s"' % fmt(c['after']), '',
            ] + say_text(n, 'Epi', c.get('epilogue', [])) + say_text(n, 'SB', c.get('scene_before', [])) + say_text(n, 'SA', c.get('scene_after', [])) + [
            'Story_Ch%d_Defeat:' % n, '\t.string "..."', '',
            'Story_Ch%d_Reward:' % n, '\t.string "The court rewards you with\\n¥%d.$"' % (500 + 250*n), '']
# camp arrival (from a gate or from a hub door that leads to another hub)
camp = ['Story_Camp::', '\tlockall']
for k, nx in camp_txt:
    camp.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_Camp_%d' % (k, k))
camp += ['\tgoto Story_Camp_%d' % NCH, '']
for k, nx in camp_txt:
    camp += ['Story_Camp_%d:' % k, '\tapplymovement OBJ_EVENT_ID_PLAYER, Story_WalkIn', '\twaitmovement 0',
             '\tmsgbox Story_CampText%d, MSGBOX_DEFAULT' % k, '\treleaseall', '\tend', '']
    if nx: msg = 'CAMP. Left door: POKEMON CENTER. Right door: POKEMART. Middle door: on to CHAPTER %s, %s.' % (nx.get('label', nx['id']), nx['title'])
    else: msg = 'The war is over. Thank you for playing.'
    camp += ['Story_CampText%d:' % k, '\t.string "%s"' % fmt([msg]), '']
# hub doors (each hub room has three door mat triggers; they set VAR_STORY_HOME to the hub index)
for h in range(len(HUBS)):
    inc += ['Story_HubMid_%d::' % h, '\tsetvar VAR_STORY_HOME, %d' % h, '\tgoto EventScript_StoryHubDoor', '',
            'Story_HubCenter_%d::' % h, '\tsetvar VAR_STORY_HOME, %d' % h, '\tlockall', '\tfadescreen FADE_TO_BLACK',
            '\twarp MAP_STORY_CAMP_CENTER, 255, 7, 7', '\twaitstate', '\tend', '',
            'Story_HubMart_%d::' % h, '\tsetvar VAR_STORY_HOME, %d' % h, '\tlockall', '\tfadescreen FADE_TO_BLACK',
            '\twarp MAP_STORY_CAMP_MART, 255, 4, 5', '\twaitstate', '\tend', '']
inc += ['Story_LeaveCenter::', '\tlockall'] + ['\tgoto_if_eq VAR_STORY_HOME, %d, Story_LeaveCenter_%d' % (h, h) for h in range(len(HUBS))] + ['\tend', '']
inc += ['Story_LeaveMart::', '\tlockall'] + ['\tgoto_if_eq VAR_STORY_HOME, %d, Story_LeaveMart_%d' % (h, h) for h in range(len(HUBS))] + ['\tend', '']
for h, m in enumerate(HUBS):
    inc += ['Story_LeaveCenter_%d:' % h, '\tfadescreen FADE_TO_BLACK', '\twarp %s, 255, 3, 13' % m, '\twaitstate', '\tend', '',
            'Story_LeaveMart_%d:' % h, '\tfadescreen FADE_TO_BLACK', '\twarp %s, 255, 11, 13' % m, '\twaitstate', '\tend', '']
# after a whiteout the player stands in the camp center; the exit leads to the hub of the current chapter
inc += ['Story_SetHome::'] + ['\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_SetHome_%d' % (i, i) for i in range(NCH)] + ['\tsetvar VAR_STORY_HOME, %d' % (len(HUBS) - 1), '\treturn', '']
for i in range(NCH): inc += ['Story_SetHome_%d:' % i, '\tsetvar VAR_STORY_HOME, %d' % hidx(hub_for(i)), '\treturn', '']
# camp mart: one clerk, yes/no chain over the hub's stock lists (exact vanilla lists by reference), Jehanna has the Celadon big market
inc += ['Story_MartMenu::', '\tlock', '\tfaceplayer'] + ['\tgoto_if_eq VAR_STORY_HOME, %d, Story_Mart_%d' % (h, h) for h in range(len(HUBS))] + ['\trelease', '\tend', '']
mart_txt = ['Story_Mart_Welcome:', '\t.string "Welcome to the camp store.$"', '', 'Story_Mart_Bye:', '\t.string "Come back any time.$"', '']
for h in range(len(HUBS)):
    inc += ['Story_Mart_%d::' % h, '\tmsgbox Story_Mart_Welcome, MSGBOX_DEFAULT']
    for j, (nm, lbl) in enumerate(STOCKS[h]):
        inc += ['\tmsgbox Story_Mart_Ask_%d_%d, MSGBOX_YESNO' % (h, j), '\tgoto_if_eq VAR_RESULT, NO, Story_Mart_Next_%d_%d' % (h, j),
                '\tmessage Text_MayIHelpYou', '\twaitmessage', '\tpokemart %s' % lbl, '\tmsgbox Text_PleaseComeAgain, MSGBOX_DEFAULT', '\trelease', '\tend',
                'Story_Mart_Next_%d_%d:' % (h, j)]
        mart_txt += ['Story_Mart_Ask_%d_%d:' % (h, j), '\t.string "%s"' % fmt(['Shall I show you the %s stock?' % nm.title().replace('Tms', 'TMs').replace('Hp Up', 'HP Up')]), '']
    inc += ['\tmsgbox Story_Mart_Bye, MSGBOX_DEFAULT', '\trelease', '\tend', '']
inc += mart_txt
# gate guard
inc += ['Story_GateGuide::', '\tmsgbox Story_GateGuideText, MSGBOX_NPC', '\tend', '',
        'Story_GateGuideText:', '\t.string "SOLDIER: This gate leads back\\nto camp. Walk through when you\\lare ready.$"', '']
inc += camp + ['Story_DepartNo:', '\tapplymovement OBJ_EVENT_ID_PLAYER, Story_StepBack', '\twaitmovement 0', '\treleaseall', '\tend', '',
               'Story_StepBack:', '\twalk_up', '\tstep_end', '']
gate += ['\tgoto Story_ToCamp_%d' % (NCH - 1), '']
hubdoor += ['\tmsgbox Story_NoMoreChapters, MSGBOX_DEFAULT', '\tgoto Story_DepartNo', '',
            'Story_NoMoreChapters:', '\t.string "The war is over. Thank you for\\nplaying.$"', '']
arrive += ['\tend', '']
inc += ['Story_WalkIn:', '\twalk_up', '\twalk_up', '\twalk_up', '\twalk_up', '\tstep_end', '']
sw = gate + hubdoor + arrive

# ---- map patches (idempotent). Hub rooms: three door triggers on the mats, no warps. Vanilla chapter maps: no warps, no map
# connections (the player cannot wander out of the story), one gate trigger plus a guard NPC next to it.
def trig(x, y, script):
    return {'type': 'trigger', 'x': x, 'y': y, 'elevation': 0, 'var': 'VAR_TEMP_F', 'var_value': '0', 'script': script}
OURS = ('Story_HubMid_', 'Story_HubCenter_', 'Story_HubMart_', 'EventScript_StoryGate', 'EventScript_StoryDepart')
for h, nm in enumerate(HUBDIR):
    f = root/('data/maps/%s/map.json' % nm); j = json.loads(f.read_text())
    j['warp_events'] = []
    j['coord_events'] = [e for e in j.get('coord_events', []) if not e.get('script', '').startswith(OURS)]
    j['coord_events'] += [trig(3, 14, 'Story_HubCenter_%d' % h), trig(7, 14, 'Story_HubMid_%d' % h), trig(11, 14, 'Story_HubMart_%d' % h)]
    f.write_text(json.dumps(j, indent=2) + '\n')
for mid, gi in GATES.items():
    f = root/('data/maps/%s/map.json' % gi['dir']); j = json.loads(f.read_text())
    j['warp_events'] = []; j['connections'] = None
    j['coord_events'] = [e for e in j.get('coord_events', []) if not e.get('script', '').startswith(OURS)]
    j['coord_events'].append(trig(gi['gate'][0], gi['gate'][1], 'EventScript_StoryGate'))
    j['object_events'] = [o for o in j['object_events'] if o.get('script') != 'Story_GateGuide']
    j['object_events'].append({'type': 'object', 'graphics_id': 'OBJ_EVENT_GFX_POLICEMAN', 'x': gi['guide'][0], 'y': gi['guide'][1], 'elevation': gi['elev'],
                               'movement_type': 'MOVEMENT_TYPE_FACE_DOWN', 'movement_range_x': 0, 'movement_range_y': 0, 'trainer_type': 'TRAINER_TYPE_NONE',
                               'trainer_sight_or_berry_tree_id': '0', 'script': 'Story_GateGuide', 'flag': '0'})
    f.write_text(json.dumps(j, indent=2) + '\n')
f = root/'data/maps/PalletTown/map.json'; j = json.loads(f.read_text())
j['object_events'] = [o for o in j['object_events'] if o.get('script') != 'EventScript_StoryGuide']
f.write_text(json.dumps(j, indent=2) + '\n')
(root/'data/scripts/story_chapters.inc').write_text('\n'.join(inc + sw) + '\n')
print('chapters', len(d['chapters']), 'trainers', len(plan), 'gates', len(GATES))
