# Story flow (Leg19, walking world)

Progress follows the Fire Emblem: The Sacred Stones plot (Eirika route), in the order of `story/chapters.json`. No NPC conversation advances the story, and nothing teleports the player through a menu: every move to a new map is a walk to a visible door or a map edge gate.

## How the flow works

1. New game: after the naming speech the game starts in Renais Castle (chapter 0). Eirika is already in the party and the vanilla Oak gates are pre-set, so Pallet Town cannot soft lock.
2. Entering a chapter map plays the title card, the opening scene, the battles, recruits and the after scene (map entry cutscene hook in `src/overworld.c`). There is no level scaling and no free heal at the end. The reward is yen only.
3. Each chapter map is a vanilla FireRed map with its warps and connections removed. After the win the player walks across the map to the gate (a step trigger beside a guide NPC; `story/gates.json` lists the gate tile of every map). The gate fades to the camp.
4. A camp is a story room (hub) with a Pokemon Center door (left), a Pokemart door (right) and the chapter door (middle), shown as red mats at the bottom wall. The player walks to a mat to go through. The center has a nurse counter (heals the party) and a PC; the mart sells the vanilla FireRed lists. Jehanna Hall carries the big market chain (vitamins, battle items, TMs, stones).
5. The middle door starts the next chapter by the map entry cutscene. A hub to hub chapter (Grado to Black Temple) is also entered by the middle door.
6. Healing happens only at the camp center (or by items). A whiteout returns the player to the camp center (heal location `HEAL_LOCATION_STORY_CAMP`, vanilla whiteout path), the party is healed there and the chapter restarts at the same number.
7. After the final chapter the THE END card shows.

Hub assignment: chapters 0 to 1 Renais Castle, 2 to 9 Frelia Castle, 10 to 13 Fort Rigwald, 14 to 17 Jehanna Hall, 18 to 22 Grado Throne Room, 23 Black Temple. Wild levels per chapter map: `docs/LEVEL_CURVE.md`.

## Chapters

| # | FE8 chapter | Title | Chapter map | Camp before it | Trigger | Battles | Reward |
|---|---|---|---|---|---|---|---|
| 0 | 0 | The Fall of Renais | Renais Castle | none (new game) | New game (automatic) | single (boss Team Rocket Grunt 27) | 500 yen |
| 1 | 1 | Escape! | Route1 | Renais Castle | Walk through the camp middle door, then map entry cutscene | single (boss Coolrolando) | 750 yen |
| 2 | 2 | The Protected | Frelia Castle | Frelia Castle | Walk through the camp middle door, then map entry cutscene | single (boss Team Rocket Grunt 31) | 1000 yen |
| 3 | 3 | The Bandits of Borgo | Route3 | Frelia Castle | Walk through the camp middle door, then map entry cutscene | double (boss Team Rocket Grunt 32) | 1250 yen |
| 4 | 4 | Ancient Horrors | Viridian Forest | Frelia Castle | Walk through the camp middle door, then map entry cutscene | double (boss Psychic Tyron) | 1500 yen |
| 5 | 5x | Unbroken Heart | Renais Castle | Frelia Castle | Walk through the camp middle door, then map entry cutscene | single (boss Coolgeorge) | 1750 yen |
| 6 | 5 | The Empire's Reach | Pewter City | Frelia Castle | Walk through the camp middle door, then map entry cutscene | double (boss Gentleman Thomas) | 2000 yen, Joshua joins |
| 7 | 6 | Victims of War | Route2 | Frelia Castle | Walk through the camp middle door, then map entry cutscene | double (boss Scientist Ivan) | 2250 yen |
| 8 | 7 | Waterside Renvall | Vermilion City | Frelia Castle | Walk through the camp middle door, then map entry cutscene | double (boss Coolcolby) | 2500 yen |
| 9 | 8 | It's a Trap! | Fort Rigwald | Frelia Castle | Walk through the camp middle door, then map entry cutscene | double (boss Gentleman Brooks) | 2750 yen |
| 10 | 9 | Distant Blade | Cerulean City | Fort Rigwald | Walk through the camp middle door, then map entry cutscene | double (boss Elite Four Bruno) | 3000 yen, Tana joins |
| 11 | 10 | Revolt at Carcino | Saffron City | Fort Rigwald | Walk through the camp middle door, then map entry cutscene | double (boss Scientist Parker) | 3250 yen, Innes, Duessel joins |
| 12 | 11 | Creeping Darkness | Lavender Town | Fort Rigwald | Walk through the camp middle door, then map entry cutscene | double (boss Coolwarren) | 3500 yen, Larachel, Dozla joins |
| 13 | 12 | Village of Silence | Route9 | Fort Rigwald | Walk through the camp middle door, then map entry cutscene | double (boss Psychic Tyron) | 3750 yen, Myrrh joins |
| 14 | 13 | Hamill Canyon | Rock Tunnel 1F | Jehanna Hall | Walk through the camp middle door, then map entry cutscene | double (boss Coolsamuel) | 4000 yen, Cormag joins |
| 15 | 14 | Queen of White Dunes | Celadon City | Jehanna Hall | Walk through the camp middle door, then map entry cutscene | double (boss Team Rocket Grunt 30) | 4250 yen |
| 16 | 15 | Scorched Sand | Jehanna Hall | Jehanna Hall | Walk through the camp middle door, then map entry cutscene | double (boss Elite Four Lance) | 4500 yen |
| 17 | 16 | Ruled by Madness | Fuchsia City | Jehanna Hall | Walk through the camp middle door, then map entry cutscene | double (boss Gentleman Lamar) | 4750 yen |
| 18 | 17 | River of Regrets | Pallet Town | Grado Throne Room | Walk through the camp middle door, then map entry cutscene | double (boss Rival Route22 Late Squirtle) | 5000 yen |
| 19 | 18 | Two Faces of Evil | Route22 | Grado Throne Room | Walk through the camp middle door, then map entry cutscene | double (boss Psychic Cameron) | 5250 yen |
| 20 | 19 | Last Hope | Cerulean Cave 1F | Grado Throne Room | Walk through the camp middle door, then map entry cutscene | double (boss Scientist Gideon) | 5500 yen |
| 21 | 20 | Darkling Woods | Victory Road 1F | Grado Throne Room | Walk through the camp middle door, then map entry cutscene | double (boss Scientist Gideon) | 5750 yen |
| 22 | 21 | Sacred Stone | Grado Throne Room | Grado Throne Room | Walk through the camp middle door, then map entry cutscene | double (boss Champion First Squirtle) | 6000 yen |
| 23 | 21x | Sacred Stone (Final) | Black Temple | Black Temple | Walk through the camp middle door, then map entry cutscene | double (boss Psychic Cameron) | 6250 yen |

The Ephraim route and the optional dungeons (Tower of Valni, Lagdou Ruins, Melkaen Coast) are out of scope.

Regenerate: `SCRIPTS_ONLY=1 python3 tools/leg3_story.py story/chapters.json <tree>` then `python3 tools/story_flow_doc.py`.
