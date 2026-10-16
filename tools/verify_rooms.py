#!/usr/bin/env python3
"""Verification only. Copies the ROM to /tmp, patches the bedroom stairs warp to land on a story map, walks up the
centre column and saves a screenshot per step. Usage: verify_rooms.py ROM OUTDIR"""
import sys, os, struct, shutil
sys.path.insert(0, os.path.dirname(__file__))
import chapter_test as c
rom, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
KEY = {'U': 0x40, 'D': 0x80, 'L': 0x20, 'R': 0x10, 'A': 1, 'B': 2}
MAPS = ['renais', 'frelia', 'jehanna', 'rigwald', 'grado', 'blacktemple']
for i, name in enumerate(MAPS):
    b = bytearray(open(rom, 'rb').read()); o = 0x4e6d78
    b[o+5] = 0; b[o+6] = i + 1; b[o+7] = 42
    p = '/tmp/vr_%s.gba' % name; open(p, 'wb').write(b)
    d = c.Drv(p); d.cmd('run 600')
    def seq(s):
        for tok in s.split():
            for _ in range(int(tok[1:] or 1)):
                d.cmd('keys %x 16' % KEY[tok[0]]); d.cmd('run 6')
        d.cmd('r8 02024029', True)
    seq('R4 U4 L2 U2'); d.cmd('run 120')
    d.cmd('shot %s/%s_00.png' % (out, name))
    for s in range(1, 15):
        seq('U1'); d.cmd('run 8'); d.cmd('shot %s/%s_%02d.png' % (out, name, s))
    seq('L5 U14'); d.cmd('run 20'); d.cmd('shot %s/%s_top_left.png' % (out, name))
    seq('R10 U14'); d.cmd('run 20'); d.cmd('shot %s/%s_top_right.png' % (out, name))
    d.close(); os.remove(p)
