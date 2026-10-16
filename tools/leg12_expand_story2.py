#!/usr/bin/env python3
"""Leg12 part 2 (one time): doubles for the Lyon and Fomortiis chapters, Ephraim epilogue line."""
import json, sys
p = sys.argv[1]; d = json.load(open(p))
byt = {c['title']: c for c in d['chapters']}
if byt['River of Regrets']['battles'][0].get('b'): raise SystemExit('already done')
def setb(t, **kw): byt[t]['battles'][0].update(kw)
setb('River of Regrets', b='TRAINER_CHANNELER_PATRICIA', partner='TRAINER_LEADER_MISTY')
setb('Sacred Stone', b='TRAINER_CHANNELER_CARLY', partner='TRAINER_LEADER_SABRINA')
setb('Sacred Stone (Final)', b='TRAINER_CHANNELER_HOPE', partner='TRAINER_LEADER_LT_SURGE', boss=True)
ep = byt['Sacred Stone (Final)']['epilogue']
ep.insert(1, [None, "Ephraim: Renais is free, Eirika. I will help you rebuild it, stone by stone."])
json.dump(d, open(p, 'w'), indent=1)
