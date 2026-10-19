#!/usr/bin/env python3
"""Leg20 check: the camp Pokemon Center PC. Continues a save that stands on a cleared chapter map, walks to the gate, the camp
center door and the PC, deposits party slot 2 into a box and withdraws it again. Real presses only. Test aid: party slot 2 is
filled with a copy of slot 1 first (the game will not deposit the last party Pokemon, and no ally has joined this early).
Usage: SAVE=<copy of a .sav> MGBA_DRV=<driver> verify_camp_pc.py ROM OUTDIR [TREE]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chapter_test as ct, walk_lib as wl
rom, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
TREE = sys.argv[3] if len(sys.argv) > 3 else '/workspace/L20/pf_eirika_work'
W = wl.World(TREE)
GATES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../story/gates.json')))
d = ct.Drv(rom)
def shot(n): d.cmd('shot %s/%s.png' % (out, n))
def tap(k=1, hold=4, wait=12): d.cmd('keys %x %d' % (k, hold)); d.cmd('run %d' % wait)
def count(): return int(d.cmd('r8 02024029', True)[0].split()[-1], 16)
def box0():
    p = int(d.cmd('r32 03005030', True)[0].split()[-1], 16)
    return int(d.cmd('r32 %x' % (p + 4), True)[0].split()[-1], 16)
def log(*a): print(*a, flush=True)
SEQ = os.environ.get('SEQ', '')
d.cmd('run 2300'); tap(8, 5, 300); tap(1, 4, 240); d.cmd('run 300')
m = W.mapdir(d, ct); log('continued on', m, wl.pos(d, ct))
gi = [g for g in GATES.values() if g['dir'] == m]
if gi:
    wl.walk_to(d, ct, W, tuple(gi[0]['gate']))
    for _ in range(24): tap(1, 4, 14)
log('camp', W.mapdir(d, ct), wl.pos(d, ct)); shot('pc_00_camp')
wl.walk_to(d, ct, W, (3, 14))
for _ in range(4): tap(1, 4, 14)
d.cmd('run 60'); log('center', W.mapdir(d, ct), wl.pos(d, ct)); shot('pc_01_center')
wl.walk_to(d, ct, W, (11, 2)); d.cmd('keys 40 6'); d.cmd('run 20')
log('at pc', wl.pos(d, ct))
for i in range(25): d.cmd('w32 %x %s' % (ct.PARTY + 100 + 4 * i, d.cmd('r32 %x' % (ct.PARTY + 4 * i), True)[0].split()[-1]))
d.cmd('w8 02024029 2'); log('party count (test aid)', count())
n = 2
for tok in SEQ.split():
    k, w = tok.split(':') if ':' in tok else (tok, '60')
    key = dict(A=1, B=2, U=0x40, D=0x80, L=0x20, R=0x10, S=8)[k]
    tap(key, 4, int(w)); shot('pc_%02d_%s' % (n, k)); n += 1
    if os.environ.get('LOGC'): log(n - 1, tok, 'party', count(), 'box1 slot1 pid %08x' % box0())
log('final party count', count(), 'box1 slot1 pid %08x' % box0(), 'map', W.mapdir(d, ct))
d.close()
