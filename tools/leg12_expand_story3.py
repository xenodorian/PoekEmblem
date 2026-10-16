#!/usr/bin/env python3
"""Leg12 part 3 (one time): ally_talk lines for chapters that had none (labels 8 to 13)."""
import json, sys
p = sys.argv[1]; d = json.load(open(p))
A = {'8': ('SPECIES_JOSHUA', "Joshua: A trap, hm? I have been in worse card games. Stay sharp."),
     '9': ('SPECIES_JOSHUA', "Joshua: Frelia pays in real gold. I like this castle already."),
     '10': ('SPECIES_TANA', "Tana: Port Kiris is in an uproar. Innes will want a report, Princess."),
     '11': ('SPECIES_INNES', "Innes: Dead men in the streets. Grado has stooped very low."),
     '12': ('SPECIES_DOZLA', "Dozla: Quiet village. Dozla does not like quiet. Dozla likes loud."),
     '13': ('SPECIES_DUESSEL', "Duessel: Wyverns, Princess. I will hold the canyon mouth. Go on.")}
n = 0
for c in d['chapters']:
    if c['label'] in A and not c.get('ally_talk'):
        c['ally_talk'] = {'speaker': A[c['label']][0], 'text': A[c['label']][1]}; n += 1
json.dump(d, open(p, 'w'), indent=1); print('added', n)
