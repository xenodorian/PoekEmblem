#!/usr/bin/env python3
"""Leg18 full playthrough from a fresh new game (no save, no state). Usage: full_playthrough.py ROM OUTDIR
Real button presses only for navigation (START/A through title, Oak speech and naming, A through every scene,
DOWN to the hub door, A on the yes/no prompt). Battle aid (test driver only, same as chapter_test.py): party HP/stats
are topped up and the lead mon gets Ghost-capable moves; set NOBUFF=1 to play unaided. Prints one line per chapter."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('BUFFLEVEL', '0')   # keep the party level field honest (the story catch-up sets level and exp together)
import chapter_test as ct
rom, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
NOBUFF = os.environ.get('NOBUFF') == '1'
NCH = 24
d = ct.Drv(rom); d.cmd('run 300')
def shot(name): d.cmd('shot %s/%s.png' % (out, name))
def tap(k=1, hold=4, wait=12): d.cmd('keys %x %d' % (k, hold)); d.cmd('run %d' % wait)
# --- title and intro with real presses
t0 = time.time()
for i in range(150):
    tap(8 if i < 6 else 1, 6, 18)
    if i % 10 == 0: shot('intro_%03d' % (i // 10))
if os.environ.get('START_CH'):   # debugging jump only
    d.cmd('w16p %x %x %x' % (ct.SB1, ct.V_CH, int(os.environ['START_CH']))); d.cmd('w16p %x %x 1' % (ct.SB1, ct.V_PEND)); ct.buff(d)
ch = d.var(ct.V_CH); print('after intro: chapter var', ch, flush=True)
shot('new_game_start')
f = 0; log = []
while ch < NCH and f < 5000000:
    v = None
    start = f; first = True; shots = 0
    # play the chapter: mash A
    while f - start < 60000:
        tap(1, 4, 12); f += 16
        if (f // 16) % 9 == 0:   # B backs out of the party/summary screens, UP+LEFT puts the battle cursor back on FIGHT
            tap(2, 4, 12); tap(2, 4, 12); tap(0x40, 4, 8); tap(0x20, 4, 8)
        if not NOBUFF: ct.buff(d, 1)
        it = (f - start) // 16
        if it % 25 == 0 and shots < 12: shot('ch%02d_play_%02d' % (ch, shots)); shots += 1
        if it % 10 == 0:
            v = d.var(ct.V_CH)
            if v != ch: break
    if v == ch or v is None:
        shot('ch%02d_STUCK' % ch); log.append((ch, 'STUCK', f - start)); print('chapter idx %d STUCK' % ch, flush=True); break
    log.append((ch, 'PASS', f - start)); print('chapter idx %d PASS (%d frames, %.0fs) map %04x' % (ch, f - start, time.time() - t0, d.var(4)), flush=True)
    shot('ch%02d_win' % ch)
    ch = v
    # camp: A through the camp text, then walk down to the door and answer yes
    for k in range(22):
        tap(1, 4, 14); f += 18   # A through the camp text
        if k in (5, 12, 20): shot('ch%02d_camp_%02d' % (ch - 1, k))
    if ch >= NCH:
        shot('ending_camp'); break
    hub = d.var(4)
    # real input: walk to the door at the bottom (DOWN), A answers the prompt text and Yes
    for k in range(120):
        tap(1, 4, 6); d.cmd('keys 80 16'); d.cmd('run 2'); f += 32
        if k == 40: shot('ch%02d_door_prompt' % ch)
        if os.environ.get('WALKSHOTS') and k % 4 == 0: shot('ch%02d_walk_%03d' % (ch, k))
        if k % 5 == 0 and d.var(4) != hub: break
    for k in range(8): tap(1, 4, 30); f += 34   # title card and arrival
    shot('ch%02d_arrive' % ch); print('  departed: map %04x pos %s' % (d.var(4), (d.var(0), d.var(2))), flush=True)
print('final chapter var', d.var(ct.V_CH)); d.close()
open(os.path.join(out, 'result.txt'), 'w').write('\n'.join('%s %s %s' % x for x in log))
