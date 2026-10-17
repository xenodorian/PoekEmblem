#!/usr/bin/env python3
"""Fresh new game with real button presses. Usage: newgame_run.py ROM OUTDIR [frames]
Mashes START/A from the title screen through the Oak speech and name menus, logs screenshots, watches VAR_STORY_CHAPTER."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import chapter_test as ct
rom, out = sys.argv[1:3]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
os.makedirs(out, exist_ok=True)
d = ct.Drv(rom); d.cmd('run 300')
for i in range(n // 20):
    d.cmd('keys %x 6' % (8 if i < 10 else 1)); d.cmd('run 14')
    if i % 25 == 0: d.cmd('shot %s/ng_%03d.png' % (out, i // 25))
d.cmd('shot %s/ng_end.png' % out)
print('chapter var', d.var(ct.V_CH), 'pending', d.var(ct.V_PEND)); d.close()
