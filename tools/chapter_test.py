#!/usr/bin/env python3
"""Win-test story chapters headlessly. Usage: chapter_test.py ROM OUTDIR [chapter ...]
Boots a copy of ROM, buffs the party, sets VAR_STORY_CHAPTER and VAR_STORY_PENDING, mashes A
and reports whether VAR_STORY_CHAPTER advanced (win) or whiteout/hang happened."""
import subprocess, sys, os, shutil
DRV = os.environ.get('MGBA_DRV', '/workspace/mgba_drv')
FAST = os.environ.get('FAST') == '1'
PARTY = 0x02024284; SB1 = int(os.environ.get('SB1PTR', '0x03005028'), 16)
V_CH = 0x1000 + 0xF0*2; V_PEND = 0x1000 + 0xEF*2

class Drv:
    def __init__(s, rom):
        import threading, queue
        s.q = queue.Queue()
        s.p = subprocess.Popen([DRV, rom, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        def rd():
            for l in s.p.stdout:
                if l.startswith(('r16p', 'echo', 'r8', 'r32', 'r16 ')): s.q.put(l.strip())
        threading.Thread(target=rd, daemon=True).start()
    def cmd(s, c, reply=False):
        s.p.stdin.write(c + '\n')
        if reply:
            s.p.stdin.write('echo\n'); s.p.stdin.flush()
            out = []
            while True:
                l = s.q.get()
                if l.startswith('echo'): break
                out.append(l)
            return out
    def var(s, off):
        o = s.cmd('r16p %x %x' % (SB1, off), True)
        return int(o[0].split()[1], 16)
    def close(s):
        s.p.stdin.write('quit\n'); s.p.stdin.flush(); s.p.wait()

_rot = [0]
MOVES = [0xe8, 0xd3, 0xd2]   # Metal Claw, Steel Wing, Fury Cutter
def buff(d, n=1):
    for bt in (0, 2): d.cmd('w16 %x 0' % (0x02023e0c + 0x1C*bt + 4))   # clear Disable on the player side (gDisableStructs from the Leg18 map)
    d.cmd('w32 02023c08 3c3c3c3c'); d.cmd('w32 02023c30 0'); hp0 = int(d.cmd('r16 02023c0c', True)[0].split()[-1], 16)
    if hp0 > 0: d.cmd('w16 02023c0c 2bc')   # never revive a fainted lead inside the battle (that hangs the engine)
    _rot[0] += 1; m = MOVES[_rot[0] // 3 % 3:] + MOVES[:_rot[0] // 3 % 3]   # rotate slot 1 so a Disabled move cannot stall the run
    d.cmd('w32 02023bf0 %04x%04x' % (m[1], m[0])); d.cmd('w32 02023bf4 0000%04x' % m[2])  # Metal Claw, Steel Wing, Fury Cutter (hit Ghost types)
    if FAST:
        for b in (1, 3):
            a = 0x02023be4 + 0x58*b + 0x28
            d.cmd('r16 %x' % a) if False else None
            d.cmd('w16 %x 1' % a)
    for i in range(n):
        b = PARTY + 100*i
        if os.environ.get('BUFFLEVEL', '1') != '0': d.cmd('w8 %x 64' % (b+0x54))
        d.cmd('w16 %x 700' % (b+0x56)); d.cmd('w16 %x 700' % (b+0x58))
        for o in (0x5A, 0x5C, 0x5E, 0x60, 0x62): d.cmd('w16 %x 600' % (b+o))

def run(rom, out, ch, maxframes=40000):
    os.makedirs(out, exist_ok=True)
    d = Drv(rom); d.cmd('run 600')
    d.cmd('w16p %x %x %x' % (SB1, V_CH, ch)); buff(d)
    if os.environ.get('DUO') == '1':   # test driver only: a second party mon so Destiny Bond (ch22 Gengar) cannot wipe the party
        for i in range(25):
            o = d.cmd('r32 %x' % (PARTY + 4*i), True)[0].split()[-1]
            d.cmd('w32 %x %s' % (PARTY + 100 + 4*i, o))
        d.cmd('w8 02024029 2'); buff(d, 2)
    d.cmd('w16p %x %x 1' % (SB1, V_PEND))
    endn = [0]; res = 'HANG'; f = 0; last = None; stall = 0; shots = 0
    while f < maxframes:
        if os.environ.get('CYCLE') == '1' and (f // 16) % 9 == 8: d.cmd('keys 80 4'); d.cmd('run 8')   # cycle the move cursor so a Disabled move does not stall the run
        if os.environ.get('DUO') == '1' and (f // 16) % 2 == 0:   # party menu after a faint: move the cursor off the dead lead to slot 2 (test driver only)
            d.cmd('shot /tmp/pm_%d.png' % os.getpid()); d.cmd('r8 02024029', True)
            try:
                from PIL import Image
                if Image.open('/tmp/pm_%d.png' % os.getpid()).convert('RGB').getpixel((200, 100)) == (74, 173, 165):
                    d.cmd('keys 10 4'); d.cmd('run 10')
            except Exception: pass
        if os.environ.get('ENDCAP') == '1' and f > 9500:   # capture the fade/THE END screens: hold off on A while the screen is mostly black
            d.cmd('shot /tmp/bk_%d.png' % os.getpid()); d.cmd('r8 02024029', True)
            try:
                from PIL import Image
                im = Image.open('/tmp/bk_%d.png' % os.getpid()).convert('L'); px = list(im.tobytes())
                if sum(1 for q in px if q < 20) / len(px) > 0.6 and endn[0] < 60:
                    endn[0] += 1; d.cmd('run 20'); d.cmd('shot %s/ch%02d_end_%03d.png' % (out, ch, endn[0])); f += 20; continue
            except Exception: pass
        d.cmd('keys 1 4'); d.cmd('run 12'); f += 16
        buff(d, 2 if os.environ.get('DUO') == '1' else 1)  # keep HP topped
        if f % int(os.environ.get("SHOTEVERY","800")) == 0:
            d.cmd('shot %s/ch%02d_%03d.png' % (out, ch, shots)); shots += 1
        if f % 160 == 0:
            v = d.var(V_CH)
            if v != ch:
                res = 'PASS' if v == ch + 1 else 'ODD(%d)' % v
                for k in range(int(os.environ.get('CONT', '0')) // 16):   # keep going after the win to capture what follows (epilogue, THE END)
                    if os.environ.get('POSTSLOW') == '1':   # tap A every 40 frames, shot every 20, so short screens are captured
                        d.cmd('keys 1 4'); d.cmd('run 16'); d.cmd('shot %s/ch%02d_post_%03d.png' % (out, ch, 2*k)); d.cmd('run 20'); d.cmd('shot %s/ch%02d_post_%03d.png' % (out, ch, 2*k+1)); continue
                    d.cmd('keys 1 4'); d.cmd('run 12')
                    if k % 5 == 0: d.cmd('shot %s/ch%02d_post_%03d.png' % (out, ch, k))
                break
    d.cmd('shot %s/ch%02d_end.png' % (out, ch))
    d.close(); return res, f

if __name__ == '__main__':
    rom, out = sys.argv[1:3]
    chs = [int(x) for x in sys.argv[3:]] or range(23)
    for c in chs:
        r, f = run(rom, out, c); print('chapter %d: %s (%d frames)' % (c, r, f), flush=True)
