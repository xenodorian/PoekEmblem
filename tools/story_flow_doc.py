#!/usr/bin/env python3
"""Writes docs/STORY_FLOW.md from story/chapters.json (run after leg3_story.py so battles are resolved)."""
import json, re
d = json.load(open('story/chapters.json'))
def hub_for(i):
    if i <= 1: return 'Renais Castle'
    if i <= 9: return 'Frelia Castle'
    if i <= 13: return 'Fort Rigwald'
    if i <= 17: return 'Jehanna Hall'
    if i <= 22: return 'Grado Throne Room'
    return 'Black Temple'
nice = lambda m: m.replace('MAP_STORY_', '').replace('MAP_', '').replace('_', ' ').title()
L = ['# Story flow (Leg19, walking world)', '',
 'Progress follows the Fire Emblem: The Sacred Stones plot (Eirika route), in the order of `story/chapters.json`. No NPC conversation advances the story, and nothing teleports the player through a menu: every move to a new map is a walk to a visible door or a map edge gate.', '',
 '## How the flow works', '',
 '1. New game: after the naming speech the game starts in Renais Castle (chapter 0). Eirika is already in the party and the vanilla Oak gates are pre-set, so Pallet Town cannot soft lock.',
 '2. Entering a chapter map plays the title card, the opening scene, the battles, recruits and the after scene (map entry cutscene hook in `src/overworld.c`). There is no level scaling and no free heal at the end. The reward is yen only.',
 '3. Each chapter map is a vanilla FireRed map with its warps and connections removed. After the win the player walks across the map to the gate (a step trigger beside a guide NPC; `story/gates.json` lists the gate tile of every map). The gate fades to the camp.',
 '4. A camp is a story room (hub) with a Pokemon Center door (left), a Pokemart door (right) and the chapter door (middle), shown as red mats at the bottom wall. The player walks to a mat to go through. The center has a nurse counter (heals the party) and a PC; the mart sells the vanilla FireRed lists. Jehanna Hall carries the big market chain (vitamins, battle items, TMs, stones).',
 '5. The middle door starts the next chapter by the map entry cutscene. A hub to hub chapter (Grado to Black Temple) is also entered by the middle door.',
 '6. Healing happens only at the camp center (or by items). A whiteout returns the player to the camp center (heal location `HEAL_LOCATION_STORY_CAMP`, vanilla whiteout path), the party is healed there and the chapter restarts at the same number.',
 '7. After the final chapter the THE END card shows.', '',
 'Hub assignment: chapters 0 to 1 Renais Castle, 2 to 9 Frelia Castle, 10 to 13 Fort Rigwald, 14 to 17 Jehanna Hall, 18 to 22 Grado Throne Room, 23 Black Temple. Wild levels per chapter map: `docs/LEVEL_CURVE.md`.', '',
 '## Chapters', '',
 '| # | FE8 chapter | Title | Chapter map | Camp before it | Trigger | Battles | Reward |', '|---|---|---|---|---|---|---|---|']
for c in d['chapters']:
    n = c['id']; bs = c['battles']
    kind = ', '.join(('double' if b.get('b') else 'single') for b in bs)
    boss = bs[-1]['a'].replace('TRAINER_', '').replace('_', ' ').title()
    trig = 'New game (automatic)' if n == 0 else 'Walk through the camp middle door, then map entry cutscene'
    L.append('| %d | %s | %s | %s | %s | %s | %s (boss %s) | %d yen%s |' % (
        n, c.get('label', n), c['title'], nice(c['map']), hub_for(n) if n else 'none (new game)', trig, kind, boss, 500 + 250 * n,
        (', ' + ', '.join(r.title() for r in c['recruits']) + ' joins') if c.get('recruits') else ''))
L += ['', 'The Ephraim route and the optional dungeons (Tower of Valni, Lagdou Ruins, Melkaen Coast) are out of scope.', '',
 'Regenerate: `SCRIPTS_ONLY=1 python3 tools/leg3_story.py story/chapters.json <tree>` then `python3 tools/story_flow_doc.py`.']
open('docs/STORY_FLOW.md', 'w').write('\n'.join(L) + '\n')
