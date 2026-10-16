#!/usr/bin/env python3
"""Contact sheet of a chapter run: trace_chapter.py ROM CH OUT.png [steps] [frames_per_step]"""
import sys; sys.path.insert(0, 'tools')
from chapter_test import *
from PIL import Image
rom, ch, outp = sys.argv[1], int(sys.argv[2]), sys.argv[3]
steps = int(sys.argv[4]) if len(sys.argv) > 4 else 24; per = int(sys.argv[5]) if len(sys.argv) > 5 else 25
d = Drv(rom); d.cmd('run 600'); d.cmd('w16p %x %x %d' % (SB1, V_CH, ch)); buff(d); d.cmd('w16p %x %x 1' % (SB1, V_PEND))
fs = []
for i in range(steps):
    for _ in range(per): d.cmd('keys 1 4'); d.cmd('run 12'); buff(d)
    fn = '/tmp/tr_%02d.png' % i; d.cmd('shot ' + fn); d.cmd('echo', True); fs.append(fn)
d.close()
im = Image.new('RGB', (240*6, 160*((steps+5)//6)))
for i, f in enumerate(fs): im.paste(Image.open(f).convert('RGB'), ((i % 6)*240, (i//6)*160))
im.save(outp)
