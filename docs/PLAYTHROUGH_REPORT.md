# Playthrough report (Leg18)

ROM: `builds/Pokemon FireRed Eirika Leg18-PlayableFlow.gba` (release `release/PokemblemTheSacredStones.gba` is identical). Run from a fresh new game: no save, no save state. Tool: `tools/full_playthrough.py` (headless mGBA, `tools/mgba_drv.c`), log `docs/img/playthrough/playthrough_log.txt`.

## Method and limits

- Real button presses (START and A through the title, Oak speech and naming; A through every scene and the battle menus; DOWN to walk to the camp door; A on the door prompt text and Yes). Nothing is skipped by memory writes except the battle aid below.
- Battle aid (test driver only, as in `tools/chapter_test.py`): the player side HP and stats are topped up every few frames, the lead gets Ghost-capable moves, and Disable is cleared. A button mash only ever picks one move, so this keeps the run deterministic; it does not touch the story flow. An unaided mash with the weak first move lost chapter 2, which is a harness limit and not a flow fault.
- Harness recoveries (also test only): B backs out of party or summary screens, a stalled identical screen triggers a move change, and after a faint (Destiny Bond) the party menu cursor is moved to a living member.
- Not a manual human playthrough: balance with real moves and item use is not judged here. The party is raised to chapter level plus 2 at the start of each chapter (`special StoryLevelCatchUp`).

## Start of the game and the former soft lock

- Root cause of the old soft lock: Eirika is the starter and is created at new game, but the vanilla Oak gate (Oak stops the player at the Pallet Town grass and walks them to the lab) and the lab starter scene were still armed, and the lab ball says "EIRIKA already has her partner". The player could be led to the lab but never complete the choice.
- Fix: `NewGameInitData` pre-sets the vanilla vars and a new game starts in chapter 0 at Renais Castle, so the player never needs Pallet Town. Verified after a real-input new game (`docs/img/playthrough/newgame_state.txt`): `VAR_MAP_SCENE_PALLET_TOWN_OAK` = 3, `VAR_MAP_SCENE_PALLET_TOWN_PROFESSOR_OAKS_LAB` = 7, `VAR_STORY_CHAPTER` = 0, party size 1 (Eirika).
- The Pallet Town guide NPC is gone. Pallet Town is only visited as the chapter 17 map, entered by the chapter cutscene (`pt_ch18_arrive.png` is the title card there; the chapter label is 16 and the index 18).

Screens: new game start `pt_new_game_start.png`, `pt_intro_003.png`, `pt_intro_008.png`; chapter 0 opening battle `pt_ch00_play_00.png`.

## Healer and vendors

The camp screens (`pt_ch00_camp_05.png`, `pt_ch06_camp_12.png`, `pt_ch10_camp_12.png`, `pt_ch14_camp_12.png`, `pt_ch16_camp_12.png`) show the hub with the healer and vendors. The healer restoring HP from 1 and a vendor BUY/SELL menu were verified in Leg17 (`docs/img/verify_leg17_heal_mart.png`). The Leg18 run walks past them and talks to them with stray A presses, which never blocks the exit; the Celadon Grand Merchant menus were still not exercised live.

## Chapter by chapter

Each row: chapter index and FE8 label, map, result, frames needed. The trigger for chapter 0 is the new game; for every other chapter it is the camp door yes/no followed by the map entry cutscene (see `docs/STORY_FLOW.md`). Every chapter ended with the chapter variable advancing, the full heal, the yen reward and the warp to the next camp.

| Idx | FE8 | Title | Map | Result | Frames |
|---|---|---|---|---|---|
| 0 | 0 | The Fall of Renais | Story Renais Castle | PASS | 6560 |
| 1 | 1 | Escape! | Route1 | PASS | 7680 |
| 2 | 2 | The Protected | Story Frelia Castle | PASS | 6080 |
| 3 | 3 | The Bandits of Borgo | Route3 | PASS | 13120 |
| 4 | 4 | Ancient Horrors | Viridian Forest | PASS | 14560 |
| 5 | 5x | Unbroken Heart | Story Renais Castle | PASS | 8160 |
| 6 | 5 | The Empire's Reach | Pewter City | PASS | 15040 |
| 7 | 6 | Victims of War | Route2 | PASS | 16640 |
| 8 | 7 | Waterside Renvall | Vermilion City | PASS | 13760 |
| 9 | 8 | It's a Trap! | Story Fort Rigwald | PASS | 16800 |
| 10 | 9 | Distant Blade | Cerulean City | PASS | 13120 |
| 11 | 10 | Revolt at Carcino | Vermilion City | PASS | 16000 |
| 12 | 11 | Creeping Darkness | Lavender Town | PASS | 15680 |
| 13 | 12 | Village of Silence | Route9 | PASS | 14560 |
| 14 | 13 | Hamill Canyon | Rock Tunnel 1F | PASS | 17760 |
| 15 | 14 | Queen of White Dunes | Celadon City | PASS | 15680 |
| 16 | 15 | Scorched Sand | Story Jehanna Hall | PASS | 28000 |
| 17 | 16 | Ruled by Madness | Fuchsia City | PASS | 15200 |
| 18 | 17 | River of Regrets | Pallet Town | PASS | 16320 |
| 19 | 18 | Two Faces of Evil | Route19 | PASS | 21280 |
| 20 | 19 | Last Hope | Cerulean Cave 1F | PASS | 18880 |
| 21 | 20 | Darkling Woods | Viridian Forest | PASS | 32800 |
| 22 | 21 | Sacred Stone | Story Grado Throne Room | PASS | 19040 |
| 23 | 21x | Sacred Stone (Final) | Story Black Temple | PASS | 29920 |

Door prompt screens: `pt_ch01_door_prompt.png`, `pt_ch03_door_prompt.png`, `pt_ch09_door_prompt.png` (where present). Recruit chapters (5, 9 to 13 in FE8 numbers) passed with the recruit scripts running automatically.

## Ending

Chapter 21x (index 23, Black Temple) epilogue `pt_epilogue.png`, then the THE END card `pt_THE_END_card.png`, then the return to the Black Temple camp (`pt_after_end_camp.png`, `pt_ending_camp.png`), where the door says the war is over. The final chapter variable is 24.

## Whiteout

Whiteout returns the party to the camp of the current chapter (code path `Story_Retreat`). It was seen on screen only as the "Eirika whited out" battle text in an early unaided run; the camp arrival after a whiteout was not captured in a screenshot in the final run.

## Remaining issues

- Balance with real play (move choice, no items bought) is untested by a human. The catch-up keeps the party level near the enemies.
- Hub arrival after chapter on the donor maps (Fort Rigwald, Grado Throne Room) starts on the door tile and walks up four tiles, as before.
- The box lost its ARM toolchain during this leg; the final ROM is the one built before that, so no source change happened after the last full run.
- The old test hook `chapter_test.py N` jump mode is invalid on Leg18 builds (the new game init overwrites the chapter variable); use `full_playthrough.py` (START_CH is also unreliable).
