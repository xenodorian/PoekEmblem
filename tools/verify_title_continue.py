#!/usr/bin/env python3
"""Leg20 check: title screen, main menu, New Game intro, in-game SAVE, reset, CONTINUE, and a mid-chapter save.
Usage: SAVE=<new .sav path> MGBA_DRV=<driver with reset and SAVE support> verify_title_continue.py ROM OUTDIR [TREE]
Real presses only, except the battle aid inside the chapter 0 and 1 battles (HP/stat top-up, as in full_playthrough.py)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('BUFFLEVEL', '0')
import chapter_test as ct, walk_lib as wl
rom, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True)
TREE = sys.argv[3] if len(sys.argv) > 3 else '/workspace/L20/pf_eirika_work'
W = wl.World(TREE)
GATES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../story/gates.json')))
d = ct.Drv(rom)
def shot(n): d.cmd('shot %s/%s.png' % (out, n))
def tap(k=1, hold=4, wait=12): d.cmd('keys %x %d' % (k, hold)); d.cmd('run %d' % wait)
def state(): return dict(map=W.mapdir(d, ct), pos=wl.pos(d, ct), ch=d.var(ct.V_CH), pend=d.var(ct.V_PEND))
def log(*a): print(*a, flush=True)
def play_chapter(ch, maxf=60000):
    f = 0
    while f < maxf:
        tap(1, 4, 12); f += 16; ct.buff(d, 1)
        if (f // 16) % 9 == 0: tap(2, 4, 12); tap(2, 4, 12); tap(0x40, 4, 8); tap(0x20, 4, 8)
        if (f // 16) % 10 == 0 and d.var(ct.V_CH) != ch: break
    for _ in range(25): tap(1, 4, 14)
    return d.var(ct.V_CH)
def boot_to_menu(tag):
    d.cmd('run 2300'); shot('%s_title' % tag)
    tap(8, 5, 300); shot('%s_menu' % tag)
def save_game(tag, overwrite=False):
    tap(8, 4, 30); shot('%s_startmenu' % tag)
    for _ in range(4): tap(0x80, 4, 10)
    shot('%s_startmenu_save' % tag)
    tap(1, 4, 150); shot('%s_save_ask' % tag)
    tap(1, 4, 150); shot('%s_save_yes' % tag)
    if overwrite: d.cmd('run 150'); shot('%s_save_overwrite' % tag); tap(1, 4, 150)
    d.cmd('run 500'); shot('%s_saved' % tag)
    for _ in range(3): tap(2, 4, 30)
def continue_game(tag):
    tap(1, 4, 240); shot('%s_cont_0' % tag)
    for i in range(1, 6): d.cmd('run 120'); shot('%s_cont_%d' % (tag, i))
# 1. cold boot, no save
boot_to_menu('cold')
tap(1, 4, 200); shot('newgame_intro')
log('new game:', state())
for _ in range(3): tap(1, 4, 20)
shot('newgame_intro2')
ch = play_chapter(0); log('chapter 0 done:', state())
shot('ch0_done')
p0 = state()['pos']
for k in ('L', 'L', 'U'): wl.step(d, ct, k)
d.cmd('run 30'); s_before = state(); log('before save:', s_before); shot('before_save')
save_game('a')
d.cmd('reset'); boot_to_menu('reset1')
continue_game('c1'); s_after = state(); log('after continue:', s_after)
log('CONTINUE1', 'OK' if (s_after['map'], s_after['pos'], s_after['ch']) == (s_before['map'], s_before['pos'], s_before['ch']) else 'MISMATCH')
# 2. mid-chapter: go to chapter 1, finish its arrival scene and battles, save on the chapter map, reset, continue
gi = [g for g in GATES.values() if g['dir'] == s_after['map']]
if s_after['map'] == 'Story_RenaisCastle':
    wl.walk_to(d, ct, W, (7, 14))   # hub middle door
    for _ in range(10): tap(1, 4, 14)
d.cmd('run 200'); shot('ch1_arrive'); log('chapter 1 map:', state())
ch = play_chapter(1); log('chapter 1 done:', state()); shot('ch1_done')
for k in ('U', 'U'): wl.step(d, ct, k)
d.cmd('run 30'); m_before = state(); log('mid save:', m_before)
save_game('b', True)
d.cmd('reset'); boot_to_menu('reset2')
continue_game('c2'); m_after = state(); log('after continue 2:', m_after)
log('CONTINUE2', 'OK' if (m_after['map'], m_after['pos'], m_after['ch']) == (m_before['map'], m_before['pos'], m_before['ch']) else 'MISMATCH')
d.close()
