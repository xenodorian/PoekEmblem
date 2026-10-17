#!/usr/bin/env python3
"""Leg19 level curve: single source of truth for chapter levels (imported by leg3_story.py and leg19_levels.py).
LV[i] is the chapter level for chapter index i (0..23). Regular trainers are LV-1 and LV, bosses LV, LV+1, LV+2."""
LV = [5, 6, 8, 10, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 37, 40, 44, 48, 52, 56, 60]
assert all(a < b for a, b in zip(LV, LV[1:]))
MAX_GAP = 3.5   # a vanilla route is used for a chapter only if its average is within this many levels of the chapter level
