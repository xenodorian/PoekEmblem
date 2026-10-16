# Leg 3 story plan: FE8 on FireRed maps (2026-10-16)

**Status: all decisions below approved (2026-10-16). Recruit points (2) and later partners (3) were left to my judgement. Future decisions are treated as approved.**

Format follows `xenodorian/Pokemon-War-and-Murder` `docs/STORY_PLAN.md`: a flow plus numbered DECISION entries. Every DECISION is approved (the owner delegated all decisions to the working agent). Facts marked "verified" come from the FE8 decomp (`docs/FE8_CHAPTERS.md`, `docs/LEG2_ALLIES.md`). Facts marked "inferred" are derived from those and not checked in an emulator.

## Scope
- Route: the Eirika route only (chapters Prologue to 8, then 9a to 21a, with 5x and 21x). Ephraim's route is not played. Ephraim appears only in cutscenes (DECISION 1).
- Chapter groups: Prologue, 1, 2, 3, 4, 5x, 5, 6, 7, 8 (10 chapters shared), then 9 to 21 plus 21x on the Eirika route (14 chapters), 24 in all.
- Side content (Tower of Valni 8 floors, Lagdou Ruins 10 floors, Melkaen Coast): kept as optional dungeons (DECISION 8).

## Flow of one chapter
1. A story scene on the map (dialogue with FE8 portraits, scripted).
2. One or more trainer battles on the chapter's FireRed map. Chapter 3 onward (first chapter with 9 deployment slots) uses double battles with an AI partner (see `docs/PARTNER_BATTLES.md`).
3. A boss battle if the chapter has a named boss (list below).
4. Recruit event if the chapter has one (`EventScript_RecruitX` in `data/scripts/ally_recruit.inc`).
5. Warp or walk to the next node.

## Verified chapter facts (Eirika route)
Start node is where the world map marker begins the chapter (verified from the world map scripts). Battle node is the next chapter's start node (inferred). Deployment slots are verified.

| Chapter | Title | Slots | Start node | Recruits (verified) | Named enemies at level above 1 (verified) |
| --- | --- | --- | --- | --- | --- |
| Prologue | The Fall of Renais | 2 | Border Mulan | none | O'Neill, Valter |
| 1 | Escape! | 2 | not listed | none | Breguet |
| 2 | The Protected | 5 | Castle Frelia | Ross, Garcia | Bone, Bazba |
| 3 | The Bandits of Borgo | 9 | Ide | Colm | Bazba |
| 4 | Ancient Horrors | 9 | Borgo Ridge | none | none (undead mobs) |
| 5x | Unbroken Heart | 4 | not listed | none | Zonta |
| 5 | The Empire's Reach | 9 | Zaha Woods | Joshua | Saar, bandit boss |
| 6 | Victims of War | 10 | Serafew | none | Novala |
| 7 | Waterside Renvall | 10 | Adlas Plains | none | Murray |
| 8 | It's a Trap! | 9 | Renvall | none | Tirado, Caellach, Selena |
| 9a | Distant Blade | 11 | Castle Frelia | Amelia | Binks |
| 10a | Revolt at Carcino | 12 | Port Kiris | Innes, Gerik, Tethys, Marisa | Pablo |
| 11a | Creeping Darkness | 11 | not listed | L'Arachel, Dozla | Wight |
| 12a | Village of Silence | 12 | not listed | none | Maelduin, Fado |
| 13a | Hamill Canyon | 12 | Caer Pelyn | Amelia (again), Cormag | Aias, Pablo, Caellach |
| 14a | Queen of White Dunes | 12 | Hamill Canyon | Rennac | Carlyle, Caellach |
| 15a | Scorched Sand | 12 | Jehanna Hall | none | Valter, Caellach |
| 16a | Ruled by Madness | 12 | Jehanna Hall | none | Orson |
| 17a | River of Regrets | 12 | Renais Castle | Syrene | Lyon |
| 18a | Two Faces of Evil | 12 | Narube River | none | Gorgon |
| 19a | Last Hope | 17 | Neleras Peak | none | Riev |
| 20a | Darkling Woods | 18 | Rausten Court | none | Riev, Morva |
| 21a | Sacred Stone | 12 | Grado Keep | none | Lyon (final form) |
| 21xa | Sacred Stone (x) | 2 | not listed | none | Fomortiis |

Notes. Tana, Duessel and Myrrh have no recruit event in the Eirika-route scripts that were parsed (Duessel's recruit event is in 10b, the Ephraim route). DECISION 2 below covers them. Chapter 5x is the Eirika-only Renais flashback chapter; it is kept as a short optional battle.

## Decisions

1. **Ephraim.** He appears as a cutscene character on the Red cast slot. The two routes' battles are not both built. The Ephraim-route chapters (9b to 21b) are summarized in dialogue only.
2. **Recruit points for the eight allies.** Innes in 10a, L'Arachel and Dozla in 11a, Cormag in 13a, Joshua in 5 (all verified). Tana joins in 9a with Amelia's scene, Duessel joins in 10a with Gerik's group, Myrrh joins in 12a (my choices, because the Eirika-route scripts do not show them).
3. **Partner battles.** Seth partners in 3 and 4, Garcia (the Blaine slot) from 5. From 9a onward the partner is whoever best fits the scene: Innes (10a), L'Arachel (11a), Cormag (13a). The partner is a trainer slot whose party stands in for that character.
4. **Enemy forces.** An FE8 map's 20 to 80 enemies becomes 3 to 6 trainer battles on the map, each with at most 6 Pokemon. The named boss is the last battle.
5. **Skirmishes** become wild encounter tables on the same maps.
6. **Enemy classes** map to FireRed trainer classes plus Pokemon families (table in `docs/STORY_PLAN.md` section below). About 70 FE8 classes collapse to roughly 25 trainer classes.
7. **Boss parties** are hand-written: level scales with the chapter (FE8 boss levels 4 to 20 become Pokemon levels 8 to 62).
8. **Dungeons.** Tower of Valni becomes the Pokemon Tower floors (8 floors), Lagdou Ruins becomes the Tanoby Ruins chambers plus Cinnabar Mansion (10 floors). Melkaen Coast becomes a One Island beach map. All optional, after Chapter 8.

## Node to FireRed map assignment (approved)

| FE8 node | FireRed map | Custom map needed |
| --- | --- | --- |
| Renais Castle | Pallet Town and the player's house | castle interior (Pallet lab reskin) |
| Border Mulan | Route 1 | no |
| Castle Frelia | Cerulean City | castle interior |
| Ide | Route 24 and Route 25 | no |
| Borgo Ridge | Mt. Moon exterior (Route 3) | no |
| Zaha Woods | Viridian Forest | no |
| Serafew | Pewter City | no |
| Adlas Plains | Route 2 | no |
| Renvall (two nodes) | Vermilion City, Route 11 | no |
| Port Kiris | Vermilion Harbor (S.S. Anne dock) | no |
| Teraz Plateau | Route 22 | no |
| Caer Pelyn | Lavender Town | no |
| Hamill Canyon | Rock Tunnel and Route 9 | no |
| Jehanna Hall (two nodes) | Celadon City, Celadon Department Store roof | desert hall interior |
| Fort Rigwald | Fuchsia City | fortress interior |
| Bethroen | Saffron City | no |
| Taizel | Cinnabar Island | no |
| Zaalbul Marsh | Safari Zone and Route 12 | no |
| Grado Keep | Silph Co. and Indigo Plateau | throne room |
| Narube River | Route 19 and Route 20 (sea) | no |
| Neleras Peak | Cerulean Cave | no |
| Rausten Court | Indigo Plateau | no |
| Darkling Woods | Route 2 forest and Diglett's Cave entrance | no |
| Black Temple | Pokemon Mansion (Cinnabar) | temple interior |
| Tower of Valni | Pokemon Tower | no |
| Lagdou Ruins | Tanoby Ruins | no |
| Melkaen Coast | One Island beach | no |

Custom maps (built last, with the War and Murder tile tools): castle interiors for Renais and Frelia, the Jehanna desert hall, the Rigwald fortress, the Grado throne room, the Black Temple. Six maps.

## Enemy class mapping (first pass)

| FE8 enemy class | FireRed trainer class | Pokemon families |
| --- | --- | --- |
| Brigand, Fighter, Warrior, Berserker | Bug Catcher to Black Belt (by level) | Mankey, Machop, Rattata, Pinsir |
| Soldier, Knight, General, Great Knight | Cooltrainer | Geodude, Onix, Golem, Rhydon |
| Cavalier, Paladin, Great Knight | Cooltrainer | Ponyta, Rapidash |
| Archer, Sniper | Bird Keeper | Pidgey, Spearow, Fearow |
| Mage, Shaman, Druid, Sage | Psychic | Abra, Gastly, Haunter |
| Wyvern Rider, Lord, Knight | Tamer | Dragonair, Aerodactyl, Charizard |
| Pirate, Mercenary, Hero | Sailor, Cue Ball | Tentacool, Machop |
| Monsters (Bonewalker, Mogall, Gorgon) | Channeler | Gastly line, Cubone line |
| Necromancer, Demon King | Boss slot (Lyon, Fomortiis) | Gengar, Mewtwo |

## Order of work
1. Approve this plan (the decisions above).
2. Build the story event layer on existing maps (no custom maps): chapter 3 to 8 first, since doubles start at 3.
3. Build boss parties and the class table in `src/data/trainers.h`.
4. Port the War and Murder tile tools and build the six custom maps.
5. Full playthrough test with the headless harness.

## Built so far (2026-10-16)
- `story/chapters.json` is the single source for all 23 chapters (0 to 22): title, node map, scene text, battles, recruits.
- `tools/leg3_story.py story/chapters.json <decomp>` writes `data/scripts/story_chapters.inc` and sets the trainer parties (themes by FE8 class, levels by chapter, bosses 2 levels higher).
- In game: talk to the guide (a Seth sprite) in Pallet Town. He shows the chapter title, warps the player to the chapter's node map (a Kanto map from the table), the scene plays on arrival (`VAR_STORY_PENDING`, hooked in `DoCB1_Overworld`), the battle runs (double battle with the AI partner from chapter 3), recruits happen, `VAR_STORY_CHAPTER` advances and the player returns to Pallet Town.
- Tested in mGBA: chapter 3 end to end (warp to Route 3, text, double battle with Seth, win, text, return).
- Smoke test: all 23 chapters were started from a test hook in mGBA. Each one warps to its node map, shows its scene and starts its battle without a crash or hang. A level 5 Eirika loses many of them, and the loss path (whiteout, back to the player's room, chapter can be retried) worked. Not yet tested: winning every chapter and the recruit calls inside chapters.
- Not done: walking between nodes on foot, custom maps, per-chapter FE8 portraits in dialogue, mid-chapter events.
