#!/usr/bin/env python3
"""Leg17 verification: patches a COPY of the ROM so the bedroom warps land on Jehanna Hall, walks to the healer and a vendor,
checks the party heals (HP write-back) and that the mart menu opens. Usage: verify_services.py ROM OUTDIR  (env WARP_OFF)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import chapter_test as c
rom, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
KEY = {'U': 0x40, 'D': 0x80, 'L': 0x20, 'R': 0x10, 'A': 1, 'B': 2}
b = bytearray(open(rom, 'rb').read()); o = int(os.environ.get('WARP_OFF', '0x4e7768'), 16)
for k in (0, 8): b[o+k+5] = 0; b[o+k+6] = 3; b[o+k+7] = 42
p = '/tmp/vs.gba'; open(p, 'wb').write(b)
d = c.Drv(p); d.cmd('run 600')
def seq(s):
    for tok in s.split():
        for _ in range(int(tok[1:] or 1)):
            d.cmd('keys %x 16' % KEY[tok[0]]); d.cmd('run 6')
    d.cmd('r8 02024029', True)
seq('R4 U4 L2 U2'); d.cmd('run 120')
seq('U4'); d.cmd('run 30')          # arrival is (7,15); walk up to (7,11)
hp = c.PARTY + 0x56
d.cmd('w16 %x 1' % hp)             # current HP = 1
print('HP before', d.cmd('r16 %x' % hp, True))
d.cmd('shot %s/js_arrive.png' % out)
seq('L6'); seq('U1'); d.cmd('run 20')    # face the healer at (1,10) from (1,11)
d.cmd('keys 1 4'); d.cmd('run 60'); d.cmd('shot %s/js_heal_1.png' % out)
d.cmd('keys 1 4'); d.cmd('run 60'); d.cmd('shot %s/js_heal_2.png' % out)
d.cmd('keys 1 4'); d.cmd('run 200'); d.cmd('shot %s/js_heal_3.png' % out)
for i in range(4): d.cmd('keys 1 4'); d.cmd('run 100')
d.cmd('shot %s/js_heal_4.png' % out)
print('HP after', d.cmd('r16 %x' % hp, True))
seq('R1 U1'); d.cmd('run 20')   # Fuchsia vendor at (2,10) from (2,11)
for k in range(1, 4):
    d.cmd('keys 1 4'); d.cmd('run 70'); d.cmd('shot %s/js_mart_f%d.png' % (out, k))
d.cmd('keys 2 4'); d.cmd('run 60'); d.cmd('keys 2 4'); d.cmd('run 60'); d.cmd('keys 2 4'); d.cmd('run 60')
seq('D1 R11 U1'); d.cmd('run 20')   # Celadon big vendor at (13,10) from (13,11)
for k in range(1, 5):
    d.cmd('keys 1 4'); d.cmd('run 70'); d.cmd('shot %s/js_mart_b%d.png' % (out, k))
d.cmd('keys 1 4'); d.cmd('run 70'); d.cmd('shot %s/js_mart_b5.png' % out)
d.close()
