#!/usr/bin/env python3
"""Leg18: after a real-input new game, print the vanilla gate vars and the party size. Usage: verify_newgame_state.py ROM"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chapter_test as ct
d = ct.Drv(sys.argv[1]); d.cmd('run 300')
for i in range(150): d.cmd('keys %x 6' % (8 if i < 6 else 1)); d.cmd('run 18')
print('VAR_MAP_SCENE_PALLET_TOWN_OAK (want 3):', d.var(0x1000 + 0x50 * 2))
print('VAR_MAP_SCENE_PALLET_TOWN_PROFESSOR_OAKS_LAB (want 7):', d.var(0x1000 + 0x55 * 2))
print('VAR_STORY_CHAPTER:', d.var(ct.V_CH))
print('party count:', d.cmd('r8 02024029', True)[0])
d.close()
