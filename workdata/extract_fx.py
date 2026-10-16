#!/usr/bin/env python3
"""Isolate a move animation's effect sprites from recorded engine frames.
usage: extract_fx.py <seq_prefix> <out_dir> [nframes]
Frame 0 is the base. For each frame the background layer may be dimmed (palette fade); we estimate that ratio
from the bright background pixels and only keep pixels that differ from the dimmed base. HUD boxes are excluded."""
import sys, os, numpy as np
from PIL import Image
prefix, out = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 420
os.makedirs(out, exist_ok=True)
base = np.array(Image.open(f'{prefix}_000.png').convert('RGB')).astype(float)[:112]
HUD = [(10, 14, 112, 48), (134, 72, 230, 112)]                # enemy and player HP boxes (x0,y0,x1,y1) in native px
excl = np.zeros(base.shape[:2], bool)
for x0, y0, x1, y1 in HUD: excl[y0:y1, x0:x1] = True
bright = (base.min(-1) > 200) & ~excl
rec = []
for i in range(n):
    f = np.array(Image.open(f'{prefix}_{i:03d}.png').convert('RGB')).astype(float)[:112]
    ratio = np.ones(3)
    d = np.abs(f - base).sum(-1)
    if (d[bright] > 40).mean() > 0.5:                          # most of the bright background changed: a uniform dim or tint
        ratio = np.median(f[bright] / np.maximum(base[bright], 1), axis=0)
    pred = np.clip(base * ratio, 0, 255)
    m = (np.abs(f - pred).sum(-1) > 45) & ~excl
    rec.append((m, f))
counts = [int(m.sum()) for m, f in rec]
np.save(f'{out}/_counts.npy', np.array(counts))
for i, (m, f) in enumerate(rec):
    a = np.dstack([f.astype(np.uint8), (m * 255).astype(np.uint8)])
    Image.fromarray(a, 'RGBA').save(f'{out}/fx_{i:03d}.png')
on = [i for i, c in enumerate(counts) if c > 12]
wins = []
for i in on:
    if wins and i - wins[-1][1] <= 20: wins[-1][1] = i
    else: wins.append([i, i])
print(os.path.basename(prefix), 'effect windows:', wins, '| peak px', max(counts))
