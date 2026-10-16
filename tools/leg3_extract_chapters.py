#!/usr/bin/env python3
"""Extract per-chapter facts for the Eirika route from the FE8 decomp.
Usage: leg3_extract_chapters.py DECOMP_DIR OUT_JSON
For each chapter event script: unit definition arrays it loads, recruits (CUSA), chests, seize/visit points."""
import re, sys, json
from pathlib import Path

d = Path(sys.argv[1])
udefs = (d/'src/events_udefs.c').read_text() + ''.join(f.read_text() for f in (d/'src/events').glob('*-eventudefs.h'))

# parse UnitDefinition arrays
arrays = {}
for m in re.finditer(r'struct UnitDefinition (\w+)\[\] = \{(.*?)\n\};', udefs, re.S):
    name, body = m.groups()
    units = []
    for u in re.finditer(r'\{\s*\.charIndex = (\w+),\s*\.classIndex = (\w+),(.*?)\n    \},', body, re.S):
        ch, cl, rest = u.groups()
        g = lambda k: (re.search(r'\.%s = (\w+)' % k, rest) or [None, None])[1]
        units.append(dict(char=ch.replace('CHARACTER_', ''), cls=cl.replace('CLASS_', ''),
                          faction=(g('allegiance') or '').replace('FACTION_ID_', ''),
                          level=int(g('level') or 0), x=int(g('xPosition') or 0), y=int(g('yPosition') or 0),
                          autolevel=('autolevel' in rest and 'TRUE' in (re.search(r'\.autolevel = (\w+)', rest) or [0, ''])[1])))
    arrays[name] = units

chapters = {}
for f in sorted((d/'src/events').glob('ch*-eventscript.h')) + [d/'src/events/prologue-eventscript.h']:
    key = f.name.replace('-eventscript.h', '')
    t = f.read_text()
    loads = sorted(set(re.findall(r'(UnitDef\w+)', t)))
    info = (d/'src/events'/f.name.replace('eventscript', 'eventinfo')).read_text()
    loads += [x for x in re.findall(r'(UnitDef\w+)', info)]
    loads = sorted(set(loads))
    recruits = re.findall(r'CUSA\(CHARACTER_(\w+)\)', t)
    chests = re.findall(r'Chest\((\w+),\s*(\d+),\s*(\d+)\)', (d/'src/events'/f.name.replace('eventscript', 'eventinfo')).read_text())
    seize = re.findall(r'Seize\((\d+),\s*(\d+)\)', info)
    villages = len(re.findall(r'Village\w*\(', info))
    units = []
    for l in loads:
        for u in arrays.get(l, []):
            units.append(dict(u, group=l))
    chapters[key] = dict(recruits=recruits, chests=[c[0] for c in chests], seize=seize, villages=villages, units=units)

Path(sys.argv[2]).write_text(json.dumps(chapters, indent=1))
print(len(chapters), 'chapters')
