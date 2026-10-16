#!/usr/bin/env python3
"""Real-flow playthrough capture. Usage: full_run.py ROM OUTDIR [first_chapter [last_chapter]]
Boots the ROM, walks from the bedroom to Pallet Town, talks to the guide (Brock) for each chapter, mashes A through the
story and battles (test party buffed, second party mon so Destiny Bond cannot wipe it, test driver only) and saves every
distinct screen to OUTDIR as sNN_FFFFF.png (NN chapter, FFFFF frame). Chapters are played in order."""
import sys, os, hashlib
sys.path.insert(0, os.path.dirname(__file__))
import chapter_test as c
rom, out = sys.argv[1:3]
c0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
c1 = int(sys.argv[4]) if len(sys.argv) > 4 else 22
os.makedirs(out, exist_ok=True)
d = c.Drv(rom); d.cmd('run 600')
KEY = {'U': 0x40, 'D': 0x80, 'L': 0x20, 'R': 0x10, 'A': 1, 'B': 2}
def seq(s):
    for tok in s.split():
        for _ in range(int(tok[1:] or 1)):
            d.cmd('keys %x 16' % KEY[tok[0]]); d.cmd('run 6')
    d.cmd('r8 02024029', True)
d.cmd('w16p %x %x %x' % (c.SB1, c.V_CH, c0))
NP = [1]
def duo():   # chapter 22 only: a second party mon so Gengar's Destiny Bond cannot wipe the party (test driver only)
    for i in range(25):
        o = d.cmd('r32 %x' % (c.PARTY + 4*i), True)[0].split()[-1]; d.cmd('w32 %x %s' % (c.PARTY + 100 + 4*i, o))
    d.cmd('w8 02024029 2'); NP[0] = 2
c.buff(d, 1)
seq('R4 U4 L2 U2'); d.cmd('run 90')          # bedroom stairs
seq('D6 L5 L1 D1'); d.cmd('run 120')         # 1F to the door mat
seq('D3'); d.cmd('run 150')                  # out to Pallet Town at (6,10)
seq('U1 R1')                                 # next to the guide
from PIL import Image
last = [None]; f = [0]; pm = [0]
def snap(ch):
    p = '/tmp/fr_%d.png' % os.getpid()
    d.cmd('shot ' + p); d.cmd('r8 02024029', True)
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != last[0]:
        last[0] = h; os.replace(p, '%s/s%02d_%06d.png' % (out, ch, f[0]))
def party_menu():
    try: return Image.open('/tmp/fr_%d.png' % os.getpid()).convert('RGB').getpixel((200, 100)) == (74, 173, 165)
    except Exception: return False
for ch in range(c0, c1 + 1):
    if ch >= 22 and NP[0] == 1: duo()
    c.buff(d, NP[0])
    seq('R1')                                # face the guide (blocked move turns)
    n = 0; res = 'HANG'
    while n < 5000:
        d.cmd('keys 1 4'); d.cmd('run 12'); f[0] += 16; n += 1
        snap(ch)
        if party_menu():
            pm[0] += 1
            if pm[0] % 4 == 3:   # optional 'switch POKEMON?' prompt: back out of the menu and answer No (Down, A)
                d.cmd('keys 2 4'); d.cmd('run 40'); d.cmd('keys 80 4'); d.cmd('run 10'); d.cmd('keys 1 4'); d.cmd('run 30')
            elif pm[0] % 4 == 2: d.cmd('keys 10 4'); d.cmd('run 10')
            else: d.cmd('keys 80 4'); d.cmd('run 10')   # forced switch (lead fainted): cursor to the second mon
        else: pm[0] = 0
        if n % 4 == 0: c.buff(d, NP[0])
        if n % 200 == 0: print(ch, n, f[0], d.var(c.V_CH), flush=True)
        if n % 10 == 0:
            v = d.var(c.V_CH)
            if v == ch + 1:
                res = 'PASS'; break
    print('chapter %d: %s (%d iterations)' % (ch, res, n), flush=True)
    if res != 'PASS': break
    # ride out the return to Pallet Town, then go to the guide again (arrival at (6,8))
    for _ in range(20): d.cmd('run 20'); snap(ch)
    seq('D1 R1')
d.close()
