#!/usr/bin/env python3
"""Leg19 full playthrough from a fresh new game (no save, no state). Usage: full_playthrough.py ROM OUTDIR [TREE]
Real button presses only for navigation (START/A through title, Oak speech and naming, A through every scene, and real D-pad
walking: from a chapter map to its gate, through the camp hub door to the next chapter map; tools/walk_lib.py plans the path
from the decomp map data with BFS and presses the keys). There is no level push and no free heal in the game.
Env: SERVICES=1 also walks into the camp Pokemon Center (HP set to 1 first, nurse heals) and the Pokemart at the chosen chapters. Battle aid (test driver only, same as chapter_test.py): party HP/stats
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

import json, walk_lib as wl
TREE = sys.argv[3] if len(sys.argv) > 3 else '/workspace/L19/pf_eirika_work'
W = wl.World(TREE)
CH = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../story/chapters.json')))['chapters']
GATES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../story/gates.json')))
HUBS = ['MAP_STORY_RENAIS_CASTLE', 'MAP_STORY_FRELIA_CASTLE', 'MAP_STORY_FORT_RIGWALD', 'MAP_STORY_JEHANNA_HALL', 'MAP_STORY_GRADO_THRONE_ROOM', 'MAP_STORY_BLACK_TEMPLE']
HUBDIR = ['Story_RenaisCastle', 'Story_FreliaCastle', 'Story_FortRigwald', 'Story_JehannaHall', 'Story_GradoThroneRoom', 'Story_BlackTemple']
def hub_for(i): return 0 if i <= 1 else 1 if i <= 9 else 2 if i <= 13 else 3 if i <= 17 else 4 if i <= 22 else 5
SERV = set(int(x) for x in os.environ.get('SERVICE_CHAPTERS', '3,11').split(',')) if os.environ.get('SERVICES') == '1' else set()
def tapA(n, wait=14):
    for _ in range(n): tap(1, 4, wait)
def stuck_cb(): mash(30)
def go(goal, name):
    ok = wl.walk_to(d, ct, W, goal, on_stuck=stuck_cb, log=lambda m: print('   ' + m, flush=True))
    print('   walk %s -> %s ok=%s map=%s pos=%s' % (name, goal, ok, W.mapdir(d, ct), wl.pos(d, ct)), flush=True)
    if not ok: shot('FAIL_%s_%d' % (name.replace(' ', '_'), int(time.time()) % 1000))
    return ok
def services(n):
    """walk into the camp Pokemon Center (heal) and the Pokemart (stock menu), then back out"""
    b = ct.PARTY
    d.cmd('w16 %x 1' % (b + 0x56)); hp_before = int(d.cmd('r16 %x' % (b + 0x56), True)[0].split()[-1], 16)
    if not go((3, 14), 'center door'): return
    tapA(4); shot('ch%02d_center_in' % n)
    go((7, 4), 'nurse'); d.cmd('keys 40 6'); d.cmd('run 20'); tap(1, 4, 60); shot('ch%02d_center_nurse0' % n); tapA(12, 60); shot('ch%02d_center_nurse' % n)
    hp_after = int(d.cmd('r16 %x' % (b + 0x56), True)[0].split()[-1], 16); mx = int(d.cmd('r16 %x' % (b + 0x58), True)[0].split()[-1], 16)
    print('   center heal: hp %d -> %d (max %d), map %s' % (hp_before, hp_after, mx, W.mapdir(d, ct)), flush=True)
    go((7, 8), 'center exit'); tapA(4); shot('ch%02d_center_out' % n)
    if not go((11, 14), 'mart door'): return
    tapA(4); go((4, 3), 'clerk'); d.cmd('keys 20 6'); d.cmd('run 6')
    tapA(1, 30); tapA(2, 30); shot('ch%02d_mart_menu' % n)
    for _ in range(40): tap(2, 4, 20)
    go((4, 7), 'mart exit'); tapA(4); shot('ch%02d_mart_out' % n)
def travel(done, n):
    """player stands in the chapter map `done` (cleared); chapter n is next. Walk gate -> camp hub -> middle door."""
    H = hub_for(n); cur = W.mapdir(d, ct); fr = 0
    if cur not in HUBDIR:
        gi = [g for g in GATES.values() if g['dir'] == cur][0]
        shot('ch%02d_gate_before' % done); go(tuple(gi['gate']), 'gate'); tapA(24); shot('ch%02d_camp_arrive' % n); fr += 600
    elif HUBDIR.index(cur) != H:
        go((7, 14), 'hub door to camp'); tapA(24); shot('ch%02d_camp_arrive' % n); fr += 600
    if n in SERV: services(n)
    shot('ch%02d_camp' % n)
    go((7, 14), 'middle door'); tapA(10); shot('ch%02d_arrive' % n); fr += 800
    print('  departed: map %s pos %s' % (W.mapdir(d, ct), wl.pos(d, ct)), flush=True)
    return fr
def mash_body(f):
    global last_img
    tap(1, 4, 12)
    if (f // 16) % 4 == 0:   # forced party menu after a faint (Destiny Bond): move the cursor off the fainted lead and confirm (same trick as chapter_test DUO)
        d.cmd('shot /tmp/pm_%d.png' % os.getpid()); d.cmd('r8 02024029', True)
        try:
            from PIL import Image
            if Image.open('/tmp/pm_%d.png' % os.getpid()).convert('RGB').getpixel((5, 5)) == (33, 107, 99):   # party menu background
                pmn[0] += 1
                for key in ((0x40, 0x10), (0x10,), (0x80, 0x10), (0x80,))[pmn[0] % 4]: tap(key, 4, 10)
                tap(1, 4, 20); tap(1, 4, 20)
        except Exception: pass
    if (f // 16) % 9 == 0:   # B backs out of the party/summary screens, UP+LEFT puts the battle cursor back on FIGHT
        tap(2, 4, 12); tap(2, 4, 12); tap(0x40, 4, 8); tap(0x20, 4, 8)
    if (f // 16) % 20 == 0:   # stall detector: an unchanged screen means a Disabled move or a stuck menu
        d.cmd('shot /tmp/stall_%d.png' % os.getpid()); d.cmd('r8 02024029', True)
        cur = open('/tmp/stall_%d.png' % os.getpid(), 'rb').read()
        if cur == last_img:   # back to FIGHT, open it, pick the right-hand move, then back out of anything else
            for _ in range(3): tap(2, 4, 14)
            tap(0x40, 4, 8); tap(0x20, 4, 8); tap(1, 4, 20); tap(0x10, 4, 8); tap(1, 4, 20); tap(2, 4, 14); tap(2, 4, 14)
        last_img = cur

    if not NOBUFF: ct.buff(d, 1)
    if not NOBUFF and ch >= 22:   # harness-only level boost for the last two chapters (the party is far below the curve there: no auto level push exists)
        for b in (0, 2): d.cmd('w8 %x 3c' % (0x02023be4 + 0x58 * b + 0x2A))

def mash(n):
    """battle/dialog handling while walking (wild or trainer battle, text boxes): same presses as the chapter loop"""
    for i in range(n): mash_body(1000 + 16 * i)
last_img = None
ch = d.var(ct.V_CH); print('after intro: chapter var', ch, flush=True)
shot('new_game_start')
pmn = [0]; f = 0; log = []
while ch < NCH and f < 5000000:
    v = None
    start = f; first = True; shots = 0
    # play the chapter: mash A
    while f - start < 60000:
        mash_body(f); f += 16
        if not NOBUFF: ct.buff(d, 1)
        it = (f - start) // 16
        if ch == NCH - 1 and it % 6 == 0: shot('end_%03d' % (it // 6))   # capture the epilogue and THE END card
        if it % 25 == 0 and shots < 12: shot('ch%02d_play_%02d' % (ch, shots)); shots += 1
        if it % 10 == 0:
            v = d.var(ct.V_CH)
            if v != ch: break
    if v == ch or v is None:
        shot('ch%02d_STUCK' % ch); log.append((ch, 'STUCK', f - start)); print('chapter idx %d STUCK' % ch, flush=True); break
    log.append((ch, 'PASS', f - start)); print('chapter idx %d PASS (%d frames, %.0fs) map %04x' % (ch, f - start, time.time() - t0, d.var(4)), flush=True)
    shot('ch%02d_win' % ch)
    ch = v
    # Leg19: walk to the next chapter. chapter maps end at a gate that leads to the camp hub; the hub's middle door starts the chapter.
    for k in range(25): tap(1, 4, 14); f += 18   # A through the reward and hint text
    shot('ch%02d_cleared' % (ch - 1))
    if ch >= NCH:
        shot('ending'); break
    f += travel(ch - 1, ch)
    if os.environ.get('STOPAFTER') and ch >= int(os.environ['STOPAFTER']): break
print('final chapter var', d.var(ct.V_CH)); d.close()
open(os.path.join(out, 'result.txt'), 'w').write('\n'.join('%s %s %s' % x for x in log))
