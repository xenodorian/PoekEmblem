#!/usr/bin/env python3
"""Consistency audit of story/chapters.json. Usage: story_audit.py story/chapters.json"""
import json, sys
d = json.load(open(sys.argv[1])); got = set(); bad = 0
def chk(c, sp, where):
    global bad
    if sp and sp != 'SPECIES_EIRIKA' and sp[8:] not in {g.upper() for g in got}:
        bad += 1; print('ch', c['label'], where, 'speaker not yet recruited:', sp)
for c in d['chapters']:
    for r in c.get('recruits', []): got.add(r)
    for sp, t in c.get('scene_before', []) + c.get('scene_after', []) + c.get('epilogue', []):
        chk(c, sp, 'scene')
    if c.get('ally_talk'): chk(c, c['ally_talk']['speaker'], 'ally_talk')
    chk(c, c['mid']['speaker'], 'mid') if c.get('mid') else None
    for t in c['before'] + c['after'] + [c['mid']['text']] if c.get('mid') else c['before'] + c['after']:
        if '\u2014' in t or '\u2013' in t: bad += 1; print('dash in', c['label'])
    print(c['label'].rjust(3), c['title'][:26].ljust(26), 'battles', len(c['battles']), 'recruits', c.get('recruits', []), 'scene lines', len(c.get('scene_before', [])) + len(c.get('scene_after', [])), 'ally_talk', bool(c.get('ally_talk')))
print('problems', bad)
