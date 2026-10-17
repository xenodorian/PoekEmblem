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
L = ['# Story flow (Leg18)', '',
 'Progress follows the Fire Emblem: The Sacred Stones plot (Eirika route), in the order of `story/chapters.json` (prologue, chapters 1 to 21, with 5x and 21x). No NPC conversation advances the story.', '',
 '## How the flow works', '',
 '1. New game: after the naming speech the game warps straight to Renais Castle (chapter 0). Eirika is already in the party (she is the starter), and the vanilla starter, rival and Oak gates are pre-set in `NewGameInitData`, so Pallet Town can never soft lock.',
 '2. Entering a chapter map (by warp, `VAR_STORY_PENDING` = 1) automatically plays the title card, the opening scene, the walk in, the skirmish battle, the boss battle, recruits, the after scene, the full heal and the yen reward. This is the map entry cutscene hook in `src/overworld.c`.',
 '3. After a win the chapter number advances and the party is warped to the camp (hub) for the next chapter (`VAR_STORY_PENDING` = 2). The hub is a story map with a healer and two vendors (Leg17). A camp message tells the player what to do.',
 '4. To go on, walk out through the door at the bottom of the hub. The door tile is a step trigger (coord event `EventScript_StoryDepart`) that asks "Leave camp and begin CHAPTER X, Title?" Yes starts the next chapter, No steps the player back.',
 '5. A whiteout sends the party back to the camp of the current chapter (healed, no money trick), and the same door starts the chapter again. `SetWhiteoutRespawnWarpAndHealerNpc` in `src/heal_location.c`.',
 '6. After chapter 21x the THE END card shows, and the player is returned to the Black Temple camp, where the door says the war is over.', '',
 'Hub assignment (also the vendor stock progression): chapters 0 to 1 Renais Castle, 2 to 9 Frelia Castle, 10 to 13 Fort Rigwald, 14 to 17 Jehanna Hall, 18 to 22 Grado Throne Room, 21x Black Temple. The same table is in `hub_for()` (`tools/leg3_story.py`) and `sStoryHubs` (`src/heal_location.c`); keep both in sync.', '',
 '## Chapters', '',
 '| # | FE8 chapter | Title | Chapter map | Camp before it | Trigger | Battles | Reward |', '|---|---|---|---|---|---|---|---|']
for c in d['chapters']:
    n = c['id']; bs = c['battles']
    kind = ', '.join(('double' if b.get('b') else 'single') for b in bs)
    boss = bs[-1]['a'].replace('TRAINER_', '').replace('_', ' ').title()
    trig = 'New game (automatic)' if n == 0 else 'Camp door yes/no, then map entry cutscene'
    L.append('| %d | %s | %s | %s | %s | %s | %s (boss %s) | %d yen, full heal%s |' % (
        n, c.get('label', n), c['title'], nice(c['map']), hub_for(n) if n else 'none (new game)', trig, kind, boss, 500 + 250 * n,
        (', ' + ', '.join(r.title() for r in c['recruits']) + ' joins') if c.get('recruits') else ''))
L += ['', 'The Ephraim route and the optional dungeons (Tower of Valni, Lagdou Ruins, Melkaen Coast) are out of scope.', '',
 'Regenerate: `SCRIPTS_ONLY=1 python3 tools/leg3_story.py story/chapters.json <tree>` then `python3 tools/story_flow_doc.py`.']
open('docs/STORY_FLOW.md', 'w').write('\n'.join(L) + '\n')
