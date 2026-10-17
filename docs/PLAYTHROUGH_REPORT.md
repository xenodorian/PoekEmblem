# Playthrough report (Leg19, walking world)

ROM: `builds/Pokemon FireRed Eirika Leg19-WorldFlow.gba` (release `release/PokemblemTheSacredStones.gba` is identical). Run from a fresh new game (no save, no save state) with `tools/full_playthrough.py` (headless mGBA, `tools/mgba_drv.c`, `tools/walk_lib.py`). Log: `docs/img/playthrough/w19_playthrough_log.txt`, per chapter results `w19_result.txt`. Screens: `docs/img/playthrough/w19_*.png`.

Result: all 24 chapters (index 0 to 23) passed, then the epilogue, the THE END card (`w19_THE_END_card.png`) and the closing message in the Black Temple camp were reached. Every one of the 40+ walks (to the gate, to the camp doors) reported ok=True; nothing was warped by memory writes.

## What the run does

- Chapter start: the map entry cutscene (A mashing through scenes and battles).
- Between chapters: the player walks (real D-pad input, path planned offline from the map data) from the arrival tile to the gate, taps A through the camp text, and walks to the middle door mat (7,14) of the camp. In hub to hub chapters it walks to the door directly.
- Services (chapters 1, 3, 10, 15, 22): walk to the Pokemon Center door, walk to the nurse, set lead HP to 1 and confirm it heals (hp 1 -> 1792 of 1792 each time), leave by the door mat, walk to the Pokemart door and clerk, open the stock list, and leave. Shots `w19_ch*_center_*`, `w19_ch*_mart_*`.
- Whiteout was checked separately with `tools/verify_whiteout.py` (`w19_whiteout_center.png`, `w19_whiteout_exit.png`): a faint returns to the camp center, healed, the chapter number stays, and the exit leads to the hub.

## Harness aids (test only, not part of the game)

- Player side HP and stats are topped up every few frames, the lead gets Ghost-capable moves, and Disable is cleared (as in earlier legs). There is no automatic level push or heal in the game, so the party stays far below the late chapter curve; for the last two chapters (index 22 and 23) the harness also sets the battle level of the player side to 60. Without it the party (Lv 20s) cannot win the Gengar and Marowak finale by button mashing.
- Recoveries: B backs out of menus, a stalled screen changes the move, and if a walk is blocked by an unseen NPC the planner marks that tile and routes around it.
- This is not a human playthrough: balance with real moves and item use is not judged.

## Changes seen in the run

- Entry by walking: the chapter maps have no warps or connections. Only the gate tile (beside a guide NPC) leaves the map.
- Camps have three doors (center, chapter, mart); wild tables follow `docs/LEVEL_CURVE.md`.

Known limits: chapter maps with little reachable land (Route 2, Route 22, Cerulean Cave, Victory Road) have short walks.
