#!/usr/bin/env python3
"""Report dialogue lines wider than the text box (about 36 glyphs). Usage: check_overflow.py DECOMP_DIR"""
import re, sys, pathlib
root = pathlib.Path(sys.argv[1]); bad = 0; tot = 0
for f in list(root.glob('data/**/*.inc')) + list(root.glob('data/**/*.s')):
    for i, l in enumerate(f.read_text(errors='ignore').splitlines(), 1):
        m = re.match(r'\s*\.string "(.*)"', l)
        if not m: continue
        t = re.sub(r'\{[^}]*\}', '', m.group(1))
        for seg in re.split(r'\\n|\\p|\\l|\$', t):
            tot += 1
            if len(seg) > 36:
                bad += 1; print('%s:%d %d %s' % (f.relative_to(root), i, len(seg), seg))
print('segments', tot, 'overflow', bad)
