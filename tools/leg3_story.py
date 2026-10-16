#!/usr/bin/env python3
"""Generate the story chapter scripts and trainer parties in the decomp.
Usage: leg3_story.py CHAPTERS_JSON DECOMP_DIR"""
import json, os, re, sys, textwrap
from pathlib import Path

d = json.load(open(sys.argv[1])); root = Path(sys.argv[2])
opp = (root/'include/constants/opponents.h').read_text()
def need(t):
    if not re.search(r'#define %s\s' % t, opp): raise SystemExit('unknown trainer ' + t)

LV = [5,6,8,10,12,13,14,16,18,20,22,24,26,28,30,32,34,38,42,46,50,55,60]
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

plan = {}   # trainer -> (chapter, count, boss)
for c in d['chapters']:
    L = LV[c['id']]
    for b in c['battles']:
        for key, cnt in (('a', 3), ('b', 2), ('partner', 3)):
            t = b.get(key)
            if not t: continue
            need(t)
            if t not in THEME: raise SystemExit('no theme for ' + t)
            boss = key == 'a' and t in BOSSES
            plan[(t)] = (L + (2 if boss else 0), cnt if boss or key == 'partner' else 2, key)

# ---- write parties (always no-item default-move type)
pp = root/'src/data/trainer_parties.h'; tr = root/'src/data/trainers.h'
parties = pp.read_text(); trainers = tr.read_text()
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
def mapinfo(mid):
    for f in (root/'data/maps').glob('*/map.json'):
        j = json.loads(f.read_text())
        if j.get('id') == mid:
            if j.get('warp_events'):
                w = j['warp_events'][0]; return w['x'], w['y']
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

hx, hy = mapinfo('MAP_PALLET_TOWN'); hy += 1
inc = ['@ Generated by tools/leg3_story.py from story/chapters.json. Do not edit by hand.', '']
guide = ['EventScript_StoryGuide::', '\tlock', '\tfaceplayer']
arrive = ['EventScript_StoryArrive::']
for c in d['chapters']:
    n = c['id']; x, y = mapinfo(c['map'])
    guide.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_Go_%d' % (n, n))
    arrive.append('\tgoto_if_eq VAR_STORY_CHAPTER, %d, Story_Arrive_%d' % (n, n))
    inc += ['Story_Go_%d::' % n,
            '\tmsgbox Story_Ch%d_Title, MSGBOX_DEFAULT' % n,
            '\tsetvar VAR_STORY_PENDING, 1',
            '\tfadescreen FADE_TO_BLACK',
            '\twarp %s, 255, %d, %d' % (c['map'], x, y),
            '\twaitstate', '\tend', '',
            'Story_Arrive_%d::' % n,
            '\tlockall',
            '\tshowmonpic %s, 1, 1' % c.get('speaker_before', 'SPECIES_EIRIKA'),
            '\tmsgbox Story_Ch%d_Before, MSGBOX_DEFAULT' % n,
            '\thidemonpic']
    inc += ['\tapplymovement OBJ_EVENT_ID_PLAYER, Story_WalkIn', '\twaitmovement 0']
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
    inc += ['\tshowmonpic %s, 1, 1' % sa, '\tmsgbox Story_Ch%d_After, MSGBOX_DEFAULT' % n, '\thidemonpic',
            '\tspecial HealPlayerParty', '\taddmoney %d' % (500 + 250*n), '\tmsgbox Story_Ch%d_Reward, MSGBOX_DEFAULT' % n,
            ] + sum([['\tshowmonpic %s, 1, 1' % sp, '\tmsgbox Story_Ch%d_Epi%d, MSGBOX_DEFAULT' % (n, k), '\thidemonpic'] for k, (sp, t) in enumerate(c.get('epilogue', []))], []) + (
            ['\tfadescreen FADE_TO_BLACK', '\tmsgbox Story_TheEnd, MSGBOX_DEFAULT'] if c.get('epilogue') else []) + [
            '\taddvar VAR_STORY_CHAPTER, 1',
            '\tfadescreen FADE_TO_BLACK',
            '\twarp MAP_PALLET_TOWN, 255, %d, %d' % (hx, hy),
            '\twaitstate', '\tend', '']
    inc += ['Story_Ch%d_Title:' % n, '\t.string "CHAPTER %d\\n%s$"' % (n, c['title'].upper().replace('"', '')), '',
            'Story_Ch%d_Before:' % n, '\t.string "%s"' % fmt(c['before']), '',
            'Story_Ch%d_Mid:' % n, '\t.string "%s"' % fmt([c['mid']['text'] if c.get('mid') else '...']), '',
            ] + sum([['Story_Ch%d_Recruit%s:' % (n, r), '\t.string "%s"' % fmt([t]), ''] for r, t in c.get('recruit_lines', {}).items()], []) + (
            ['Story_Ch%d_AllyTalk:' % n, '\t.string "%s"' % fmt([c['ally_talk']['text']]), ''] if c.get('ally_talk') else []) + [
            'Story_Ch%d_After:' % n, '\t.string "%s"' % fmt(c['after']), '',
            ] + sum([['Story_Ch%d_Epi%d:' % (n, k), '\t.string "%s"' % fmt([t]), ''] for k, (sp, t) in enumerate(c.get('epilogue', []))], []) + [
            'Story_Ch%d_Defeat:' % n, '\t.string "..."', '',
            'Story_Ch%d_Reward:' % n, '\t.string "Your party was fully healed.\\pThe court rewards you with\\n¥%d.$"' % (500 + 250*n), '']
guide += ['\tmsgbox Story_NoMoreChapters, MSGBOX_DEFAULT', '\trelease', '\tend', '',
       'Story_TheEnd:', '\t.string "THE SACRED STONES\\nTHE END\\pThank you for playing.$"', '',
       'Story_NoMoreChapters:', '\t.string "The war is over. Thank you for\\nplaying.$"', '']
arrive += ['\tend', '']
inc += ['Story_WalkIn:', '\twalk_up', '\twalk_up', '\twalk_up', '\twalk_up', '\tstep_end', '']
sw = guide + arrive
(root/'data/scripts/story_chapters.inc').write_text('\n'.join(inc + sw) + '\n')
print('chapters', len(d['chapters']), 'trainers', len(plan))
