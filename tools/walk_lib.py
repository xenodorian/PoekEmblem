#!/usr/bin/env python3
"""Leg19 harness helpers: read the player's map and position from the save block and walk to a tile with real D-pad input.
The path comes from tools/mapgrid.py (offline BFS over the decomp map data), the keys are real presses."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapgrid
K = {'U': 0x40, 'D': 0x80, 'L': 0x20, 'R': 0x10}
class World:
    def __init__(self, tree):
        self.tree = tree
        mg = json.load(open(os.path.join(tree, 'data/maps/map_groups.json')))
        self.groups = [mg[g] for g in mg['group_order']]
    def mapdir(self, d, ct):
        v = d.var(4); grp, num = v & 0xFF, v >> 8
        return self.groups[grp][num]
def pos(d, ct): return d.var(0), d.var(2)
def step(d, ct, key, hold=17):
    d.cmd('keys %x %d' % (K[key], hold)); d.cmd('run 3')
def walk_to(d, ct, W, goal, maxsteps=900, on_stuck=None, log=None):
    """Walk to goal (x, y) on the current map. Returns True when the player stands there or the map changed."""
    m0 = d.var(4); stuck = 0; steps = 0; blk = set()
    while steps < maxsteps:
        steps += 1
        if d.var(4) != m0: return True
        p = pos(d, ct)
        if p == tuple(goal): return True
        g = mapgrid.grid(W.tree, W.mapdir(d, ct))
        dist, par = mapgrid.bfs(g, p, blk)
        # goal may be a trigger tile that is not in the 'walkable' set (door mats): allow a final step onto it
        if tuple(goal) not in par:
            for k, (dx, dy) in {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}.items():
                n = (goal[0] - dx, goal[1] - dy)
                if n in par: par[tuple(goal)] = (n, k); dist[tuple(goal)] = dist[n] + 1; break
        if tuple(goal) not in par and blk:
            blk.clear(); stuck = 1; continue
        if tuple(goal) not in par:
            if log: log('no path from %s to %s' % (p, goal))
            return False
        k = mapgrid.path(par, tuple(goal))[0]
        step(d, ct, k)
        if pos(d, ct) == p and d.var(4) == m0:
            stuck += 1
            if stuck % 25 == 0:   # something unseen (an NPC) is in the way: plan around that tile
                dx, dy = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}[k]; blk.add((p[0] + dx, p[1] + dy))
                if log: log('blocked tile %s, replanning' % ((p[0] + dx, p[1] + dy),))
            if on_stuck: on_stuck()
            else:
                d.cmd('keys 1 4'); d.cmd('run 10')
            if stuck > 300: return False
        else: stuck = 0
    return False
