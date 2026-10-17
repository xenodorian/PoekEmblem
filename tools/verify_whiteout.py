#!/usr/bin/env python3
"""Leg19: whiteout check. New game, start chapter 0, zero the player's HP in the first battle (test driver only), mash A.
Expected: the party wakes in the camp Pokemon Center (heal location HEAL_LOCATION_STORY_CAMP), the nurse heals, VAR_STORY_CHAPTER stays 0,
and walking out of the center leads to the hub room (Renais Castle). Usage: verify_whiteout.py ROM OUTDIR [TREE]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chapter_test as ct, walk_lib as wl
rom, out = sys.argv[1:3]; tree = sys.argv[3] if len(sys.argv) > 3 else '/workspace/L19/pf_eirika_work'
os.makedirs(out, exist_ok=True)
d = ct.Drv(rom); d.cmd('run 300'); W = wl.World(tree)
def shot(n): d.cmd('shot %s/%s.png' % (out, n))
def tap(k=1, hold=4, wait=12): d.cmd('keys %x %d' % (k, hold)); d.cmd('run %d' % wait)
for i in range(150): tap(8 if i < 6 else 1, 6, 18)
print('start map', W.mapdir(d, ct), 'chapter', d.var(ct.V_CH), flush=True)
hit = 0
for i in range(2500):
    tap(1, 4, 12)
    if W.mapdir(d, ct) != 'Story_RenaisCastle': break
    if i > 150:   # zero the lead and ally HP in battle (battler structs) and in the party
        d.cmd('w16 02023c0c 0'); d.cmd('w16 02023c0c 0')
        if i % 3 == 0:
            for b in range(2): d.cmd('w16 %x 0' % (ct.PARTY + 100 * b + 0x56))
    if i % 100 == 0: shot('wo_%03d' % (i // 100))
print('after loss: map', W.mapdir(d, ct), 'pos', wl.pos(d, ct), 'chapter', d.var(ct.V_CH), flush=True)
for i in range(40): tap(1, 4, 20)
shot('wo_center'); hp = d.cmd('r16 %x' % (ct.PARTY + 0x56), True)[0].split()[-1]; mx = d.cmd('r16 %x' % (ct.PARTY + 0x58), True)[0].split()[-1]
print('hp', int(hp, 16), 'max', int(mx, 16), 'map', W.mapdir(d, ct), 'pos', wl.pos(d, ct), flush=True)
ok = wl.walk_to(d, ct, W, (7, 8), on_stuck=lambda: tap(1, 4, 20))
for i in range(6): tap(1, 4, 20)
shot('wo_out'); print('after exit: map', W.mapdir(d, ct), 'pos', wl.pos(d, ct), 'chapter', d.var(ct.V_CH), flush=True)
d.close()
