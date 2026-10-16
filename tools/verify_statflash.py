#!/usr/bin/env python3
"""Verification only: start chapter 0, mash A to the first battle, give Eirika Swords Dance (0x0E) in slot 1 and capture a frame sequence."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import chapter_test as c
rom, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
move = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x0e
d = c.Drv(rom); d.cmd('run 600')
KEY = {'U': 0x40, 'D': 0x80, 'L': 0x20, 'R': 0x10, 'A': 1, 'B': 2}
def seq(s):
    for tok in s.split():
        for _ in range(int(tok[1:] or 1)):
            d.cmd('keys %x 16' % KEY[tok[0]]); d.cmd('run 6')
    d.cmd('r8 02024029', True)
d.cmd('w16p %x %x 0' % (c.SB1, c.V_CH)); c.buff(d, 1)
seq('R4 U4 L2 U2'); d.cmd('run 90'); seq('D6 L5 L1 D1'); d.cmd('run 120'); seq('D3'); d.cmd('run 150'); seq('U1 R1'); seq('R1')
for n in range(int(sys.argv[4]) if len(sys.argv) > 4 else 130):
    d.cmd('keys 1 4'); d.cmd('run 12')
    if n % 4 == 0 and n < 40: c.buff(d, 1)
    if n >= 40:
        d.cmd('w32 02023bf0 %04x%04x' % (move, move)); d.cmd('w32 02023bf4 %04x%04x' % (move, move))
        d.cmd('w16 02023c0c 2bc')
for k in range(60):
    d.cmd('keys 1 4'); d.cmd('run 10'); d.cmd('shot %s/m_%02d.png' % (out, k))
    d.cmd('w32 02023bf0 %04x%04x' % (move, move)); d.cmd('w16 02023c0c 2bc')
d.cmd('shotseq %s/seq 120' % out); d.cmd('r8 02024029', True)
d.close()
