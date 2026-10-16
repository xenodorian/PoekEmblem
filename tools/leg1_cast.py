#!/usr/bin/env python3
"""Leg 1 master cast list: which FE8 character takes over which FireRed identity.

usage: leg1_cast.py DECOMP_DIR   -> prints the mapping and writes cast.json next to the script's cwd

Rules:
- Unique FireRed characters (leaders, Elite Four, Giovanni, rival, Red) are given by hand, matched on role and gender.
- Every other FE8 character takes over one FireRed trainer that appears in a map script, is not in the VS Seeker rematch table,
  and whose current trainer picture is a class that suits the FE8 character. Name and picture are replaced.
- The 8 Leg 2 allies are not trainers. They are Pokemon, so they get no trainer slot.
"""
import re, sys, json, collections, os
D = sys.argv[1]
src = open(os.path.join(D, 'src/data/trainers.h')).read()
rows = {}
for tid, b in re.findall(r'\[(TRAINER_\w+)\]\s*=\s*\{(.*?)\n    \},', src, re.S):
    pic = re.search(r'\.trainerPic = (\w+)', b); nm = re.search(r'\.trainerName = _\("([^"]*)"\)', b); cl = re.search(r'\.trainerClass = (\w+)', b)
    dbl = re.search(r'\.doubleBattle = (\w+)', b)
    if pic and nm and cl: rows[tid] = dict(pic=pic.group(1), name=nm.group(1), cls=cl.group(1), double=dbl.group(1) if dbl else 'FALSE')
used = set(re.findall(r'`(TRAINER_\w+)`', open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../docs/FRLG_CHARACTER_LIST.md')).read()))
rem = set(re.findall(r'TRAINER_\w+', open(os.path.join(D, 'src/vs_seeker.c')).read()))

unique = {  # FE8 name: (FireRed role, existing trainer pic constants that get the portrait)
    'Seth': ('Brock', ['TRAINER_PIC_LEADER_BROCK']),
    'Marisa': ('Misty', ['TRAINER_PIC_LEADER_MISTY']),
    'Gilliam': ('Lt. Surge', ['TRAINER_PIC_LEADER_LT_SURGE']),
    'Vanessa': ('Erika', ['TRAINER_PIC_LEADER_ERIKA']),
    'Colm': ('Koga', ['TRAINER_PIC_LEADER_KOGA']),
    'Lute': ('Sabrina', ['TRAINER_PIC_LEADER_SABRINA']),
    'Garcia': ('Blaine', ['TRAINER_PIC_LEADER_BLAINE']),
    'Vigarde': ('Giovanni', ['TRAINER_PIC_LEADER_GIOVANNI']),
    'Selena': ('Lorelei', ['TRAINER_PIC_ELITE_FOUR_LORELEI']),
    'Binks': ('Bruno', ['TRAINER_PIC_ELITE_FOUR_BRUNO']),
    'Syrene': ('Agatha', ['TRAINER_PIC_ELITE_FOUR_AGATHA']),
    'Valter': ('Lance', ['TRAINER_PIC_ELITE_FOUR_LANCE']),
    'Lyon': ('Rival', ['TRAINER_PIC_RIVAL_EARLY', 'TRAINER_PIC_RIVAL_LATE', 'TRAINER_PIC_CHAMPION_RIVAL']),
    'Ephraim': ('Red', ['TRAINER_PIC_RED']),
    'Moulder': ('Prof. Oak (NPC)', ['TRAINER_PIC_PROFESSOR_OAK']),
}
allies = ['Cormag', 'Dozla', 'Duessel', 'Innes', 'Joshua', "L'Arachel", 'Myrrh', 'Tana']
KNIGHT = ['TRAINER_PIC_COOLTRAINER_M', 'TRAINER_PIC_GENTLEMAN', 'TRAINER_PIC_BLACK_BELT']
BRUTE = ['TRAINER_PIC_ROCKET_GRUNT_M', 'TRAINER_PIC_BIKER', 'TRAINER_PIC_CUE_BALL', 'TRAINER_PIC_BURGLAR', 'TRAINER_PIC_HIKER', 'TRAINER_PIC_SAILOR']
MAGE = ['TRAINER_PIC_PSYCHIC_M', 'TRAINER_PIC_SCIENTIST', 'TRAINER_PIC_SUPER_NERD', 'TRAINER_PIC_POKEMANIAC']
pref = {}
for n in ['Aias', 'Breguet', 'Saar', 'Tirado', 'Franz', 'Forde', 'Kyle', 'Murray', 'Orson']: pref[n] = KNIGHT
for n in ['Bazba', 'Gheb', "O'Neill", 'Beran', 'Zonta', 'Gerik', 'Caellach', 'Carlyle', 'Glen', 'Hayden', 'Frelian', 'Ross', 'Rennac']: pref[n] = BRUTE
for n in ['Artur', 'Ewan', 'Saleh', 'Pablo', 'Fado', 'Klimt', 'Novala', 'Riev', 'Mansel', 'Morva', 'Fomortiis']: pref[n] = MAGE
pref['Natasha'] = ['TRAINER_PIC_LASS', 'TRAINER_PIC_PICNICKER']
pref['Neimi'] = ['TRAINER_PIC_PICNICKER', 'TRAINER_PIC_LASS']
pref['Knoll'] = ['TRAINER_PIC_PSYCHIC_M', 'TRAINER_PIC_SCIENTIST', 'TRAINER_PIC_SUPER_NERD']
pref['Amelia'] = ['TRAINER_PIC_LASS', 'TRAINER_PIC_PICNICKER']
pref['Dara'] = ['TRAINER_PIC_PSYCHIC_F', 'TRAINER_PIC_CHANNELER']
pref['Ismaire'] = ['TRAINER_PIC_COOLTRAINER_F', 'TRAINER_PIC_BEAUTY']
pref['Tethys'] = ['TRAINER_PIC_BEAUTY', 'TRAINER_PIC_COOLTRAINER_F']
pool = collections.defaultdict(list)
for tid, r in rows.items():
    if tid in used and tid not in rem and r['double'] == 'FALSE' and not tid.endswith(('_2', '_3', '_4', '_5')): pool[r['pic']].append(tid)
for k in pool: pool[k].sort()
prev = json.load(open('cast.json'))['cast'] if os.path.exists('cast.json') else {}
picked = {c['trainer'] for c in prev.values() if c.get('trainer')}
for k in pool: pool[k] = [t for t in pool[k] if t not in picked]
cast = {}
for n, (role, pics) in unique.items(): cast[n] = dict(role=role, pics=pics, trainer=None)
take = {}
for n in sorted(pref):
    if n in prev and prev[n].get('trainer'): take[n] = prev[n]['trainer']; continue
    for p in pref[n]:
        if pool[p]:
            # spread picks across the list so one map does not hold every character
            lst = pool[p]; tid = lst.pop(len(lst) // 2); take[n] = tid; break
    else: raise SystemExit('no trainer left for ' + n)
for n, tid in take.items(): cast[n] = dict(role='Trainer ' + rows[tid]['name'] + ' (' + rows[tid]['pic'].replace('TRAINER_PIC_', '') + ')', pics=[], trainer=tid, old_name=rows[tid]['name'])
json.dump(dict(cast=cast, allies=allies), open('cast.json', 'w'), indent=1)
print(len(cast), 'characters with an identity,', len(allies), 'allies (Pokemon)')
for n, c in cast.items(): print(n, '->', c['role'], c['trainer'] or '')
