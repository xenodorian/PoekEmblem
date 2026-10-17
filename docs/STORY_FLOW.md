# Story flow (Leg18)

Progress follows the Fire Emblem: The Sacred Stones plot (Eirika route), in the order of `story/chapters.json` (prologue, chapters 1 to 21, with 5x and 21x). No NPC conversation advances the story.

## How the flow works

1. New game: after the naming speech the game warps straight to Renais Castle (chapter 0). Eirika is already in the party (she is the starter), and the vanilla starter, rival and Oak gates are pre-set in `NewGameInitData`, so Pallet Town can never soft lock.
2. Entering a chapter map (by warp, `VAR_STORY_PENDING` = 1) automatically plays the title card, the opening scene, the walk in, the skirmish battle, the boss battle, recruits, the after scene, the full heal and the yen reward. This is the map entry cutscene hook in `src/overworld.c`.
3. After a win the chapter number advances and the party is warped to the camp (hub) for the next chapter (`VAR_STORY_PENDING` = 2). The hub is a story map with a healer and two vendors (Leg17). A camp message tells the player what to do.
4. To go on, walk out through the door at the bottom of the hub. The door tile is a step trigger (coord event `EventScript_StoryDepart`) that asks "Leave camp and begin CHAPTER X, Title?" Yes starts the next chapter, No steps the player back.
5. A whiteout sends the party back to the camp of the current chapter (healed, no money trick), and the same door starts the chapter again. `SetWhiteoutRespawnWarpAndHealerNpc` in `src/heal_location.c`.
6. After chapter 21x the THE END card shows, and the player is returned to the Black Temple camp, where the door says the war is over.

Hub assignment (also the vendor stock progression): chapters 0 to 1 Renais Castle, 2 to 9 Frelia Castle, 10 to 13 Fort Rigwald, 14 to 17 Jehanna Hall, 18 to 22 Grado Throne Room, 21x Black Temple. The same table is in `hub_for()` (`tools/leg3_story.py`) and `sStoryHubs` (`src/heal_location.c`); keep both in sync.

## Chapters

| # | FE8 chapter | Title | Chapter map | Camp before it | Trigger | Battles | Reward |
|---|---|---|---|---|---|---|---|
| 0 | 0 | The Fall of Renais | Renais Castle | none (new game) | New game (automatic) | single (boss Team Rocket Grunt 27) | 500 yen, full heal |
| 1 | 1 | Escape! | Route1 | Renais Castle | Camp door yes/no, then map entry cutscene | single (boss Coolrolando) | 750 yen, full heal |
| 2 | 2 | The Protected | Frelia Castle | Frelia Castle | Camp door yes/no, then map entry cutscene | single (boss Team Rocket Grunt 31) | 1000 yen, full heal |
| 3 | 3 | The Bandits of Borgo | Route3 | Frelia Castle | Camp door yes/no, then map entry cutscene | double (boss Team Rocket Grunt 32) | 1250 yen, full heal |
| 4 | 4 | Ancient Horrors | Viridian Forest | Frelia Castle | Camp door yes/no, then map entry cutscene | double (boss Psychic Tyron) | 1500 yen, full heal |
| 5 | 5x | Unbroken Heart | Renais Castle | Frelia Castle | Camp door yes/no, then map entry cutscene | single (boss Coolgeorge) | 1750 yen, full heal |
| 6 | 5 | The Empire's Reach | Pewter City | Frelia Castle | Camp door yes/no, then map entry cutscene | double (boss Gentleman Thomas) | 2000 yen, full heal, Joshua joins |
| 7 | 6 | Victims of War | Route2 | Frelia Castle | Camp door yes/no, then map entry cutscene | double (boss Scientist Ivan) | 2250 yen, full heal |
| 8 | 7 | Waterside Renvall | Vermilion City | Frelia Castle | Camp door yes/no, then map entry cutscene | double (boss Coolcolby) | 2500 yen, full heal |
| 9 | 8 | It's a Trap! | Fort Rigwald | Frelia Castle | Camp door yes/no, then map entry cutscene | double (boss Gentleman Brooks) | 2750 yen, full heal |
| 10 | 9 | Distant Blade | Cerulean City | Fort Rigwald | Camp door yes/no, then map entry cutscene | double (boss Elite Four Bruno) | 3000 yen, full heal, Tana joins |
| 11 | 10 | Revolt at Carcino | Vermilion City | Fort Rigwald | Camp door yes/no, then map entry cutscene | double (boss Scientist Parker) | 3250 yen, full heal, Innes, Duessel joins |
| 12 | 11 | Creeping Darkness | Lavender Town | Fort Rigwald | Camp door yes/no, then map entry cutscene | double (boss Coolwarren) | 3500 yen, full heal, Larachel, Dozla joins |
| 13 | 12 | Village of Silence | Route9 | Fort Rigwald | Camp door yes/no, then map entry cutscene | double (boss Psychic Tyron) | 3750 yen, full heal, Myrrh joins |
| 14 | 13 | Hamill Canyon | Rock Tunnel 1F | Jehanna Hall | Camp door yes/no, then map entry cutscene | double (boss Coolsamuel) | 4000 yen, full heal, Cormag joins |
| 15 | 14 | Queen of White Dunes | Celadon City | Jehanna Hall | Camp door yes/no, then map entry cutscene | double (boss Team Rocket Grunt 30) | 4250 yen, full heal |
| 16 | 15 | Scorched Sand | Jehanna Hall | Jehanna Hall | Camp door yes/no, then map entry cutscene | double (boss Elite Four Lance) | 4500 yen, full heal |
| 17 | 16 | Ruled by Madness | Fuchsia City | Jehanna Hall | Camp door yes/no, then map entry cutscene | double (boss Gentleman Lamar) | 4750 yen, full heal |
| 18 | 17 | River of Regrets | Pallet Town | Grado Throne Room | Camp door yes/no, then map entry cutscene | double (boss Rival Route22 Late Squirtle) | 5000 yen, full heal |
| 19 | 18 | Two Faces of Evil | Route19 | Grado Throne Room | Camp door yes/no, then map entry cutscene | double (boss Psychic Cameron) | 5250 yen, full heal |
| 20 | 19 | Last Hope | Cerulean Cave 1F | Grado Throne Room | Camp door yes/no, then map entry cutscene | double (boss Scientist Gideon) | 5500 yen, full heal |
| 21 | 20 | Darkling Woods | Viridian Forest | Grado Throne Room | Camp door yes/no, then map entry cutscene | double (boss Scientist Gideon) | 5750 yen, full heal |
| 22 | 21 | Sacred Stone | Grado Throne Room | Grado Throne Room | Camp door yes/no, then map entry cutscene | double (boss Champion First Squirtle) | 6000 yen, full heal |
| 23 | 21x | Sacred Stone (Final) | Black Temple | Black Temple | Camp door yes/no, then map entry cutscene | double (boss Psychic Cameron) | 6250 yen, full heal |

The Ephraim route and the optional dungeons (Tower of Valni, Lagdou Ruins, Melkaen Coast) are out of scope.

Regenerate: `SCRIPTS_ONLY=1 python3 tools/leg3_story.py story/chapters.json <tree>` then `python3 tools/story_flow_doc.py`.
